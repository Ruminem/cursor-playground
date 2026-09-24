# SPDX-License-Identifier: Apache-2.0
"""art/ 의 구성표 그림으로 preview.html 과 dist/<구성표>/*.cur 를 다시 만든다.

사용법: python build.py

preview.html 에는 기본 모양의 그림 데이터가 들어가고, 다른 모양은 data/<모양>/ 으로 따로 나간다
(index.json 과 구성표마다 한 파일 — split_data 참고).
dist/ 의 커서 파일은 시안 페이지 버튼이 GitHub Pages 에서 내려받는다 (기본 모양은 dist/<구성표>/,
나머지는 dist/<모양>/<구성표>/). art/ 나 shapes/ 를 고치면 이걸 다시 돌리고 결과까지 커밋해야 웹에 반영된다.
"""
import base64
import hashlib
import json
import os
import pickle
import subprocess
import sys
import time
import zlib
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import shape as shapelib
import smooth as smoothlib
from make_cur import canvas_size, is_animated, is_row, read_hotspot, read_rate, split_frames, txt_to_ani, txt_to_cur, txt_to_png

HERE = Path(__file__).parent
STENCILS = HERE / ".stencils.pkl"   # 매끈한 모양의 스텐실. 빌드가 먼저 구워 두고 워커들이 읽어 나눠 쓴다

# 구성표 목록은 schemes.json 한 곳에 둔다 (install.ps1, handler.ps1 도 같은 파일을 읽음)
SCHEMES = json.loads((HERE / "schemes.json").read_text(encoding="utf-8"))
# 커서 모양 목록. 첫 번째가 기본(테마 그림 그대로)이고, 나머지는 smooth.py 가 그려 테마 색을 입힌다
SHAPES = json.loads((HERE / "shapes.json").read_text(encoding="utf-8"))
# 구성표 → 재질. 빛을 어떻게 되받는지만 정하고 색은 그대로다 (smooth.MATERIALS)
MAT = {s["id"]: s.get("material") for s in SCHEMES}


def _sha(*blobs) -> str:
    h = hashlib.sha256()
    for b in blobs:
        h.update(b if isinstance(b, bytes) else b.encode())
    return h.hexdigest()[:16]


def version() -> str:
    """시안 페이지 제목 옆에 박는 표시. CHANGELOG 맨 위 버전 + 지금 커밋 7자.

    커밋이 같이 있어야 Pages 에 실린 것이 방금 민 것인지 눈으로 갈린다 — 버전만 적으면
    배포해도 글자가 그대로라 반영됐는지 알 수 없다"""
    ver = next((ln.split()[1] for ln in (HERE.parent / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()
                if ln.startswith("## ")), "?")
    try:
        sha = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], cwd=HERE,
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        sha = ""                      # git 없이 받은 사본. 버전만 적고 넘어간다
    return f"v{ver} · {sha}" if sha else f"v{ver}"


def _hashes() -> tuple[str, dict, str, str]:
    """(코드 해시, 구성표별 재료 해시, 전부 합친 해시, 시안 페이지 해시). 지난번과 같으면 그 산출물은 건너뛴다"""
    # 파이썬·zlib 버전도 코드로 친다. PNG 바이트가 버전마다 달라서, 다른 파이썬이 만든 캐시를
    # 받으면(러너의 3.14 패치가 올라간 날 등) 섞이지 않고 전부 다시 그려야 한다 — 릴리스가 캐시를 쓴다
    code = _sha(sys.version, zlib.ZLIB_RUNTIME_VERSION,
                *((HERE / n).read_bytes() for n in ("build.py", "make_cur.py", "shape.py", "smooth.py", "shapes.json")))
    art = {s["id"]: _sha(code, json.dumps(s, sort_keys=True),
                         *(f.read_bytes() for f in sorted((HERE / "art" / s["id"]).iterdir())))
           for s in SCHEMES}
    # 시안 페이지와 모양 데이터는 구성표 전부를 한 파일에 담아서 하나만 바뀌어도 다시 만든다
    every = _sha(*(art[s["id"]] for s in SCHEMES))
    # 버전 표시를 해시에 넣는다 — 커밋이 바뀌면 그림이 그대로여도 페이지를 다시 만들어야 한다
    return code, art, every, _sha(every, (HERE / "preview.tpl.html").read_bytes(), version())


# dist/ 안에 두면 CI 의 커서 파일 점검이 이걸 커서로 알고 열어 보다 실패한다
STAMP = HERE / ".build-stamp.json"
# 파일, 칸 이름, 브라우저가 이미지를 못 쓸 때의 기본 커서
ROLES = [
    ("arrow", "일반 선택", "default"),
    ("ibeam", "텍스트 선택", "text"),
    ("wait", "사용 중", "wait"),
    ("no", "사용할 수 없음", "not-allowed"),
    ("move", "이동", "move"),
    ("hand", "링크 선택", "pointer"),
]
# 나머지 11칸. 테마 화살표·모래시계에서 만든 것이라 시안에는 작은 그림으로만 보여 준다
EXTRA = [
    ("help", "도움말 선택", "help"),
    ("busy", "백그라운드 작업", "progress"),
    ("cross", "정밀 선택", "crosshair"),
    ("pen", "필기", "default"),
    ("ns", "세로 크기 조정", "ns-resize"),
    ("we", "가로 크기 조정", "ew-resize"),
    ("nwse", "대각선 크기 조정 1", "nwse-resize"),
    ("nesw", "대각선 크기 조정 2", "nesw-resize"),
    ("up", "대체 선택", "default"),
    ("pin", "위치 선택", "default"),
    ("person", "사용자 선택", "default"),
]


# 모양이 건드리지 않는 칸들. 테마 색으로만 그린 기호(크기 조정 4종 등)와, 테마마다
# 하트·손가락·별로 다른 링크 칸. 링크는 테마의 표정이라 모양을 바꿀 때도 그대로 둔다
KEEP = {"ns", "we", "nwse", "nesw", "up", "cross", "pen", "hand"}
# 구성표가 schemes.json 의 keep 으로 더 붙드는 칸 — 해양 생물의 "사용 중"은 모래시계가 아니라 생물 그림이다.
# 모양 폴더에 파일이 없으면 받는 쪽이 기본 모양으로 넘어가는 약속은 KEEP 만의 것이라, 여기 칸은
# 모양 폴더에도 기본 모양과 같은 바이트로 쓴다 (build_one)
KEEPS = {s["id"]: KEEP | set(s.get("keep", ())) for s in SCHEMES}
# 몸이 장마다 흔들리는 그림(헤엄) — 매끈한 모양의 번짐 테를 그 장 몸 밖에서만 뜬다 (smooth.samplers_of).
# 비율만으로 켜면 반짝이·폭죽 move 처럼 몸에서 튀는 것도 걸려서 표식을 단 구성표만
SWAYS = {s["id"] for s in SCHEMES if s.get("sway")}


def shape_of(shape_id: str) -> str | None:
    """기본 모양이면 None (테마 그림을 그대로 쓴다), 아니면 smooth.py 에 넘길 모양 이름"""
    return None if shape_id == SHAPES[0]["id"] else shape_id


def art_raw(sid: str, rid: str) -> str:
    """구성표가 그린 그림 txt"""
    return (HERE / "art" / sid / f"{rid}.txt").read_text(encoding="utf-8")


def smooth_parts(sid: str, rid: str, shape: str, cache: dict) -> tuple[list[dict], int, list | None]:
    """매끈한 모양으로 이 칸을 그릴 재료 — (색을 뜰 프레임, rate, 얹을 기호)"""
    frames, _, rate = shapelib.read_art(art_raw(sid, rid))
    if rid in smoothlib.ROLES:
        return frames, rate, None
    # 화살표에 기호를 얹어 만든 칸(도움말·백그라운드 작업·위치·사용자)은 새 화살표에 그 기호를 다시 붙인다
    if sid not in cache:
        cache[sid] = shapelib.read_art(art_raw(sid, "arrow"))[0]
    aframes = cache[sid]
    use = [aframes[i % len(aframes)] for i in range(len(frames))]   # 프레임 수는 이 칸을 따른다
    bx, by, bw, bh = smoothlib.base_box(shape, "arrow")
    glyphs = shapelib.place(shapelib.glyph_of(use, frames),
                            shapelib.bbox([p for f in use for p in f]),
                            (bx, by, bx + bw - 1, by + bh - 1))
    return use, rate, glyphs


def _drawer(ats: dict | None, sid: str, rid: str, shape: str, frames: list[dict], glyphs: list | None):
    """이 칸의 drawer. ats 를 받았으면 거기서 꺼내거나 만들어 둔다 — 커서와 시안 데이터가 같은 그림을 나눠 쓰게.
    안 받았어도 여기서 만든다 — smooth 쪽이 대신 만들면 구성표를 몰라 sway 표식이 빠진다"""
    if ats is None:
        return smoothlib.drawer(shape, rid, frames, glyphs, MAT.get(sid), sid in SWAYS)
    if rid not in ats:
        ats[rid] = smoothlib.drawer(shape, rid, frames, glyphs, MAT.get(sid), sid in SWAYS)
    return ats[rid]


def page_bits(sid: str, rid: str, shape: str | None, cache: dict,
              ats: dict | None = None) -> tuple[list[bytes], int, int, int, int, int]:
    """시안 페이지에 넣을 (프레임별 PNG, 핫스팟 x, y, rate(ms), 폭, 높이)"""
    if shape is None or rid in KEEPS[sid]:
        raw = art_raw(sid, rid)
        src = canvas_size(raw)
        pngs = [txt_to_png(f, None, src) for f in split_frames(raw)]
        hx, hy = read_hotspot(raw) or (0, 0)
        rows = [r for r in split_frames(raw)[0].splitlines() if is_row(r)]
        rate = read_rate(raw)
        w, h = max(len(r) for r in rows), len(rows)
    else:
        frames, rate, glyphs = smooth_parts(sid, rid, shape, cache)
        at = _drawer(ats, sid, rid, shape, frames, glyphs)
        pngs, (hx, hy), (w, h) = smoothlib.page(shape, rid, frames, glyphs, MAT.get(sid), at)
    return pngs, hx, hy, rate * 1000 // 60, w, h


def uri_of(png: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(png).decode()


def _scanlines(png: bytes) -> tuple[int, bytes]:
    """우리 PNG(8비트 RGBA, 필터 0, IDAT 하나 이상)를 풀어 (폭, 필터 바이트째 행들)"""
    w, pos, idat = int.from_bytes(png[16:20], "big"), 8, b""
    while pos < len(png):
        n = int.from_bytes(png[pos:pos + 4], "big")
        if png[pos + 4:pos + 8] == b"IDAT":
            idat += png[pos + 8:pos + 8 + n]
        pos += 12 + n
    return w, zlib.decompress(idat)


def strip(pngs: list[bytes], ink: bool = False) -> tuple[str, list[int] | int]:
    """프레임들을 세로로 이은 PNG 한 장 (주소, 잉크 상자).

    프레임마다 따로 넣으면 PNG 머리·base64 앞머리만 한 장에 115바이트라 기본 모양 데이터가 5.1MB 였고,
    이으면 zlib 가 앞 프레임과 같은 줄을 찾아 줄여서 1.4MB 가 된다(매끈한 모양 24.4→10.8MB, 2026-09-24).
    페이지는 그림 주소를 바꿔 끼우지 않고 자리(background-position)만 옮겨서, 사파리가 프레임마다 그림을
    다시 풀며 깜빡이던 것도 없어진다.
    프레임 뒤마다 판의 1/8 만큼 투명한 줄을 둔다 — 매끈한 모양을 부드럽게 줄여 그리면 이웃 프레임의 가장자리
    줄이 번져 들어온다 (프레임 2만 8천 장 중 1만 9천 장이 맨 윗줄이나 맨 아랫줄에 색이 있다).
    ink 면 모든 프레임의 불투명(알파 > 8) 영역을 합친 [x0, y0, x1, y1, 판] 도 잰다 — 목록 썸네일 자리 맞춤용"""
    raws, w = [], 0
    for png in pngs:
        w, raw = _scanlines(png)
        assert all(raw[i] == 0 for i in range(0, len(raw), w * 4 + 1)), "필터 없는 PNG 만 이을 수 있다"
        raws.append(raw)
    gap = bytes((w * 4 + 1) * (w // 8))
    body = gap.join(raws) + gap
    tall = len(body) // (w * 4 + 1)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return len(data).to_bytes(4, "big") + kind + data + zlib.crc32(kind + data).to_bytes(4, "big")

    ihdr = w.to_bytes(4, "big") + tall.to_bytes(4, "big") + bytes((8, 6, 0, 0, 0))
    uri = uri_of(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(body, 9)) + chunk(b"IEND", b""))
    if not ink:
        return uri, 0
    x0 = y0 = w
    x1 = y1 = -1
    for raw in raws:
        for y in range(w):
            row = raw[y * (w * 4 + 1) + 1:(y + 1) * (w * 4 + 1)]
            xs = [x for x in range(w) if row[x * 4 + 3] > 8]
            if xs:
                x0, x1, y0, y1 = min(x0, xs[0]), max(x1, xs[-1]), min(y0, y), max(y1, y)
    return uri, ([x0, y0, x1, y1, w] if x1 >= 0 else [0, 0, w - 1, w - 1, w])


def cursor_bytes(sid: str, rid: str, shape: str | None, cache: dict, ats: dict | None = None) -> tuple[bytes, str]:
    """dist 에 넣을 커서 파일 하나와 확장자"""
    if shape is None or rid in KEEPS[sid]:
        raw = art_raw(sid, rid)
        hot = read_hotspot(raw) or (0, 0)
        return (txt_to_ani(raw, hot), "ani") if is_animated(raw) else (txt_to_cur(raw, hot), "cur")
    frames, rate, glyphs = smooth_parts(sid, rid, shape, cache)
    at = _drawer(ats, sid, rid, shape, frames, glyphs)
    return smoothlib.cursor(shape, rid, frames, rate, glyphs, MAT.get(sid), at)


def favicon() -> str:
    """탭 아이콘. 직접 그린 분홍 화살표를 가운데 두고 꽉 채운 64px (저장소와 같은 Apache-2.0, 외부 아이콘 안 씀)"""
    text = (HERE / "art" / "pink" / "arrow.txt").read_text(encoding="utf-8")
    head = [l for l in text.splitlines() if not is_row(l)]
    rows = [l for l in text.splitlines() if is_row(l)]
    w, h = max(len(r) for r in rows), len(rows)
    side = max(w, h) + 2
    left, top = (side - w) // 2, (side - h) // 2
    square = [""] * top + ["." * left + r for r in rows]
    png = txt_to_png("\n".join(head + square), 64, side)
    return "data:image/png;base64," + base64.b64encode(png).decode()


def build() -> str:
    css, panels = [], []
    data: dict[str, dict[str, list]] = {}
    extra_data: dict[str, dict[str, list]] = {}
    groups: dict[str, list[str]] = {}
    for scheme in SCHEMES:
        sid, sname, sdesc = scheme["id"], scheme["name"], scheme["desc"]
        cards = []
        for rid, rlabel, fallback in ROLES:
            # 그림은 프레임을 이은 한 장(strip)으로 넘기고 페이지 스크립트가 카드에 깔고 자리를 옮긴다.
            # 카드에 미리 박아 두면 같은 그림이 페이지에 두 번 들어간다. CSS 커서 기본값은 첫 프레임
            entry = data_bit(sid, rid, None, {})
            hx, hy, w, h = entry[1], entry[2], entry[5], entry[6]
            uri = uri_of(page_bits(sid, rid, None, {})[0][0])
            css.append(
                f'[data-scheme="{sid}"] .c-{rid},[data-scheme="{sid}"].c-{rid},.card.s-{sid}.c-{rid}'
                f"{{cursor:url({uri}) {hx} {hy},{fallback}}}"
            )
            data.setdefault(sid, {})[rid] = entry
            cards.append(f"""
        <article class="card s-{sid} c-{rid}" tabindex="0">
          <div class="stage" style="--hx:{hx};--hy:{hy}">
            <div class="sprite"></div>
            <span class="hot" aria-hidden="true"></span>
          </div>
          <div class="meta">
            <h3>{rlabel}</h3>
            <p><code>art/{sid}/{rid}.txt</code></p>
            <p class="coords">{w}×{h} · hotspot <b>{hx},{hy}</b></p>
          </div>
        </article>""")
        extras = []
        for rid, rlabel, _ in EXTRA:
            extra_data.setdefault(sid, {})[rid] = data_bit(sid, rid, None, {})
            extras.append(f'<div class="extra s-{sid} e-{rid}"><span class="pic"><i></i></span>{rlabel}</div>')
        search = " ".join((sid, sname, scheme["name_en"], scheme["category"], scheme["category_en"])).lower()
        groups.setdefault(scheme["category"], []).append(f"""
      <div class="pick-wrap" data-scheme-item="{sid}" data-search="{search}">
        <button type="button" class="pick c-hand" data-pick="{sid}" aria-pressed="false">
          <span class="thumb"></span>
          <span class="pick-name">{sname}</span>
        </button>
        <button type="button" class="star c-hand" data-star="{sid}" aria-pressed="false" title="즐겨찾기" aria-label="{sname} 즐겨찾기">★</button>
      </div>""")
        panels.append(f"""
    <div class="panel" data-panel="{sid}" hidden>
      <div class="desc-row">
        <p class="desc"><b>cursor-playground {sname}</b> — {sdesc}</p>
        <button type="button" class="register c-hand" data-apply="{sid}" data-name="{sname}">이 구성표 적용</button>
      </div>
      <div class="grid">{"".join(cards)}</div>
      <div class="extras"><h4>나머지 11칸</h4><div class="extra-grid">{"".join(extras)}</div></div>
    </div>""")

    # 모양 탭. 단추에 붙는 그림은 첫 구성표의 화살표를 그 모양으로 그린 것
    tabs = []
    for i, shp in enumerate(SHAPES):
        pic = uri_of(page_bits(SCHEMES[0]["id"], "arrow", shape_of(shp["id"]), {})[0][0])
        tabs.append(f'<button type="button" class="shape c-hand{" smooth" if i else ""}" role="tab" data-shape="{shp["id"]}"'
                    f' aria-selected="{"true" if i == 0 else "false"}"><i style="background-image:url({pic})"></i>{shp["name"]}</button>')

    page = (
        (HERE / "preview.tpl.html").read_text(encoding="utf-8")
        .replace("<!--SHAPES-->", "".join(tabs))
        .replace("/*SHAPE_LIST*/", json.dumps([{k: s[k] for k in ("id", "name", "desc")} for s in SHAPES], ensure_ascii=False, separators=(",", ":")))
        .replace("/*CURSOR_CSS*/", "\n".join(css))
        .replace("/*CURSOR_DATA*/", json.dumps(data, separators=(",", ":")))
        .replace("/*EXTRA_DATA*/", json.dumps(extra_data, separators=(",", ":")))
        .replace("<!--FAVICON-->", favicon())
        .replace("<!--COUNT-->", str(len(SCHEMES)))
        .replace("<!--VERSION-->", version())
        .replace("<!--GROUPS-->", str(len(groups)))
        .replace("<!--PICKER-->", "".join(
            f'<div class="group"><h3 class="group-name">{cat}</h3><div class="picker">{"".join(items)}</div></div>'
            for cat, items in groups.items()))
        .replace("<!--PANELS-->", "".join(panels))
    )
    head, body = page.split("</style>", 1)
    # 파일로 바로 열어도 한글이 깨지지 않게 charset 을 박는다
    return (
        '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<!-- 자동 생성: python build.py 로 다시 만들 것. 고칠 때는 preview.tpl.html 을 고친다 -->\n"
        f"{head}</style>\n</head>\n<body>{body}</body>\n</html>\n"
    )


def data_bit(sid: str, rid: str, shape: str | None, cache: dict, ats: dict | None = None) -> list:
    """시안 데이터의 칸 하나. ROLES 칸은 [스트립, 핫스팟 x, y, 대체 커서, rate, 폭, 높이, 프레임 수, 잉크 상자],
    EXTRA 칸은 [스트립, rate, 프레임 수]. 잉크 상자는 화살표만 (나머지는 0)"""
    pngs, hx, hy, rate, w, h = page_bits(sid, rid, shape, cache, ats)
    uri, box = strip(pngs, rid == "arrow")
    fallback = next((f for r, _, f in ROLES if r == rid), None)
    return [uri, hx, hy, fallback, rate, w, h, len(pngs), box] if fallback is not None else [uri, rate, len(pngs)]


def splice(pieces: dict[str, tuple[dict, dict]], old: dict | None) -> dict:
    """구성표별 조각 {구성표: (칸들, 덧칸들)} 을 SCHEMES 차례로 이어 {"data": …, "extra": …} 로.
    old 를 주면 조각이 없는 구성표는 지난번 것을 그대로 옮긴다"""
    data: dict[str, dict[str, list]] = {}
    extra: dict[str, dict[str, list]] = {}
    for scheme in SCHEMES:
        sid = scheme["id"]
        data[sid], extra[sid] = pieces[sid] if sid in pieces else (old["data"][sid], old["extra"][sid])
    return {"data": data, "extra": extra}


def shape_data(shape_id: str, sids: list[str], old: dict | None) -> dict:
    """다른 모양의 페이지 데이터. 기본 모양이 preview.html 에 박혀 있는 것과 같은 구조.

    old 를 주면 sids 에 든 구성표만 새로 그리고 나머지는 지난번 것을 그대로 옮긴다."""
    shape, cache = shape_of(shape_id), {}
    pieces = {}
    for scheme in SCHEMES:
        sid = scheme["id"]
        if old is None or sid in sids:
            pieces[sid] = ({rid: data_bit(sid, rid, shape, cache) for rid, _, _ in ROLES},
                           {rid: data_bit(sid, rid, shape, cache) for rid, _, _ in EXTRA})
            cache.pop(sid, None)
    return splice(pieces, old)


def timed(fn, job) -> tuple:
    """일감 하나를 돌리고 (결과, 시작 시각, 끝 시각)을 돌려준다. 어디서 시간이 새는지 찍으려고"""
    t = time.time()
    got = fn(job)
    return got, t, time.time()


def _dur(s: float) -> str:
    return f"{int(s // 60)}분 {s % 60:.0f}초" if s >= 60 else f"{s:.0f}초"


def bake(key: tuple) -> tuple:
    """스텐실 하나를 굽는다 (워커에서). 값을 돌려보내 부모가 한 파일로 모은다"""
    return key, smoothlib.stencil(*key)


_stencils_loaded = False


def _load_stencils() -> None:
    """부모가 구워 둔 스텐실을 이 프로세스에 들인다. 프로세스마다 처음 한 번 (7ms).
    파일이 없으면 예전처럼 필요할 때 굽는다"""
    global _stencils_loaded
    if not _stencils_loaded and STENCILS.exists():
        smoothlib._cache.update(pickle.loads(STENCILS.read_bytes()))
        _stencils_loaded = True


def build_one(job: tuple[str, str, bool, bool]) -> tuple[int, tuple | None]:
    """(모양, 구성표) 하나. dist 커서 파일을 쓰고, 시안 데이터 조각을 만들어 돌려준다 (파일은 부모가 모아 쓴다).

    한 칸의 커서(32·64·128 판)와 시안 그림(20·40칸, 화살표는 60칸)은 20·40칸이 똑같은 그림이라
    drawer 하나로 나눠 그린다. data 를 모양마다 따로 일감으로 돌리던 때는 그게 워커 시간의 1/4이었다 (5600X, 2026-09-24)"""
    shape_id, sid, want_dist, want_data = job
    shape, cache = shape_of(shape_id), {}
    if shape is not None:
        _load_stencils()
    # 기본 모양은 dist/<구성표>/ 그대로 둔다 (이미 깔린 처리 스크립트가 그 주소를 쓴다)
    out = (HERE / "dist" if shape is None else HERE / "dist" / shape_id) / sid
    if want_dist:
        out.mkdir(parents=True, exist_ok=True)
    count, data, extra = 0, {}, {}
    for rid, _, _ in ROLES + EXTRA:
        ats: dict = {}                                  # 칸마다 새로 — 한 칸 그림만 들고 있게 (메모리)
        # 모양이 안 건드리는 칸은 기본 모양 파일과 바이트까지 같다. 두 번 쓰지 않고
        # 받는 쪽(handler.ps1, install.ps1)이 dist/<구성표>/ 것으로 넘어간다
        if want_dist and not (shape is not None and rid in KEEP):
            blob, ext = cursor_bytes(sid, rid, shape, cache, ats)
            (out / f"{rid}.{ext}").write_bytes(blob)
            count += 1
        if want_data:
            (data if any(r == rid for r, _, _ in ROLES) else extra)[rid] = data_bit(sid, rid, shape, cache, ats)
    return count, ((data, extra) if want_data else None)


def data_dir(shape_id: str) -> Path:
    return HERE / "data" / shape_id


def split_data(whole: dict) -> dict[str, dict]:
    """모양 하나의 데이터를 페이지가 받는 파일들로 {파일 이름: 내용}.

    index.json 은 구성표마다 칸의 핫스팟·크기·프레임 수만(그림 자리는 빈 글자, 몇십 KB),
    arrows.json 은 구성표 전부의 화살표 그림(목록 썸네일), <구성표>.json 은 그 구성표의 칸 그림 전부.
    모양을 고르면 index 와 지금 구성표 하나만 받고 바로 바꾸고, 썸네일 그림은 그 뒤에 받는다 —
    한 파일(24MB)을 통째로 받던 때는 다 받고 나서야 바뀌었고, index 에 화살표를 같이 넣었을 때도
    gzip 2.4MB 라 폰 회선에서 2–3초 기다렸다"""
    index: dict[str, dict] = {}
    arrows: dict[str, str] = {}
    files: dict[str, dict] = {"index.json": {"data": index}, "arrows.json": {"data": arrows}}
    for sid, roles in whole["data"].items():
        index[sid] = {rid: ["", *e[1:]] for rid, e in roles.items()}
        arrows[sid] = roles["arrow"][0]
        files[f"{sid}.json"] = {"data": {rid: e[0] for rid, e in roles.items()}, "extra": whole["extra"][sid]}
    return files


def read_data(shape_id: str) -> dict | None:
    """split_data 의 거꾸로. 지난번 파일들이 온전하지 않으면 None"""
    root = data_dir(shape_id)
    try:
        index = json.loads((root / "index.json").read_text(encoding="utf-8"))["data"]
        data, extra = {}, {}
        for sid, roles in index.items():
            one = json.loads((root / f"{sid}.json").read_text(encoding="utf-8"))
            data[sid] = {rid: [one["data"][rid], *e[1:]] for rid, e in roles.items()}
            extra[sid] = one["extra"]
        return {"data": data, "extra": extra}
    except (OSError, KeyError, ValueError):
        return None


def data_whole(shape_id: str) -> bool:
    """지난번 data/<모양>/ 을 조각 갈아 끼우기에 쓸 수 있나 — 없거나 구성표가 늘거나 줄었으면 못 쓴다"""
    old = read_data(shape_id)
    return old is not None and set(old["data"]) == {s["id"] for s in SCHEMES}


def write_data(shape_id: str, pieces: dict[str, tuple[dict, dict]]) -> None:
    """모양 하나의 시안 페이지 데이터 data/<모양>/. 지난번 파일이 있으면 조각이 온 구성표만 갈아 끼운다.
    코드가 바뀌면 모든 구성표의 조각이 오므로(해시에 코드가 섞여 있다) 통째로 다시 쓰인다"""
    root = data_dir(shape_id)
    root.mkdir(parents=True, exist_ok=True)
    old = read_data(shape_id) if len(pieces) < len(SCHEMES) else None
    for name, body in split_data(splice(pieces, old)).items():
        (root / name).write_text(json.dumps(body, separators=(",", ":")), encoding="utf-8", newline="\n")
    # 한 파일에 다 넣던 때의 data/<모양>.json. 남겨 두면 Pages 에 모양마다 24MB 씩 그대로 올라간다
    (HERE / "data" / f"{shape_id}.json").unlink(missing_ok=True)


def update_readme() -> None:
    """README 의 영어·한국어 구성표·모양 표를 schemes.json, shapes.json 으로 다시 채운다 (두 언어가 어긋나지 않게)"""
    path = HERE / "README.md"
    text = path.read_text(encoding="utf-8")
    for lang, name, desc, cat, head, shead in (
        ("en", "name_en", "desc_en", "category_en", "| Folder | Name | Style |", "| Id | Name | Look |"),
        ("ko", "name", "desc", "category", "| 폴더 | 이름 | 스타일 |", "| 아이디 | 이름 | 생김새 |"),
    ):
        rows, current = [], None
        for s in SCHEMES:
            if s[cat] != current:
                current = s[cat]
                rows += ["", f"**{current}**", "", head, "|---|---|---|"]
            rows.append(f"| `art/{s['id']}` | {s[name]} | {s[desc]} |")
        start, end = f"<!-- schemes:{lang} -->", f"<!-- /schemes:{lang} -->"
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        text = before + start + "\n".join(rows) + "\n\n" + end + after

        rows = ["", shead, "|---|---|---|"]
        for i, s in enumerate(SHAPES):
            where = "art/" if i == 0 else s["id"]
            rows.append(f"| `{where}` | {s[name]} | {s[desc]} |")
        start, end = f"<!-- shapes:{lang} -->", f"<!-- /shapes:{lang} -->"
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        text = before + start + "\n".join(rows) + "\n\n" + end + after
    # 윈도우 기본값으로 쓰면 CRLF 가 되어 저장소(LF)와 매번 달라진다
    path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    clash = {s["id"] for s in SHAPES} & {s["id"] for s in SCHEMES}
    if clash:  # dist/<모양>/ 과 dist/<구성표>/ 가 같은 자리를 쓰게 된다
        raise SystemExit(f"모양 이름이 구성표 이름과 겹침: {sorted(clash)}")
    t0 = time.time()
    # 지난번 빌드가 남긴 표식. 재료가 그대로인 산출물은 다시 그리지 않는다.
    # CI 는 늘 빈 체크아웃이라 표식이 없어 전부 다시 만든다. 손으로 그러려면 --all
    code, art, every, page_key = _hashes()
    was = {} if "--all" in sys.argv else json.loads(STAMP.read_text()) if STAMP.exists() else {}

    workers = getattr(os, "process_cpu_count", os.cpu_count)() or 1   # ProcessPoolExecutor 기본값과 같다
    with ProcessPoolExecutor(workers) as pool:
        # 재료가 바뀐 구성표. dist 는 여기에 "폴더가 없는 것"을 더하고, data 는 이 목록만 갈아 끼운다
        changed = [s["id"] for s in SCHEMES if was.get(s["id"]) != art[s["id"]]]
        jobs_of, skipped = [], 0
        # 일감 차례를 정할 어림 값 — 그림 프레임 수. 움직이는 구성표 몇이 일의 대부분이다
        frames = {(s["id"], rid): len(split_frames(art_raw(s["id"], rid))) for s in SCHEMES for rid, _, _ in ROLES + EXTRA}
        left: dict[str, int] = {}                       # 모양마다 남은 일감. 다 끝나면 한 줄 찍는다
        pieces: dict[str, dict] = {}                    # 시안 데이터를 새로 쓸 모양 → 구성표별 조각
        for shp in SHAPES:
            base = shp["id"] == SHAPES[0]["id"]
            root = HERE / "dist" if base else HERE / "dist" / shp["id"]
            stale = {s["id"] for s in SCHEMES
                     if s["id"] in changed or not (root / s["id"]).is_dir()}
            skipped += len(SCHEMES) - len(stale)
            fresh: set[str] = set()                     # 시안 데이터 조각을 새로 그릴 구성표
            if not base and (was.get("*") != every or not (data_dir(shp["id"]) / "index.json").exists()):
                fresh = set(changed) if changed and data_whole(shp["id"]) else {s["id"] for s in SCHEMES}
                pieces[shp["id"]] = {}
            # (모양 × 구성표) 하나가 일감 하나. 커서와 시안 데이터를 한 일감에서 같이 만든다.
            # 스텐실은 아래서 먼저 구워 나눠 쓰므로 잘게 쪼개도 다시 굽지 않는다.
            # 모양당 4묶음이던 때는 무거운 구성표(무지개 흐름·용암)가 한 묶음에 몰려 그 묶음이 2배 걸렸고,
            # 마지막 모양의 묶음만 남아 워커 8개가 20초 넘게 놀았다 (2026-09-24, 5600X 262초 중 22초)
            mine = [(shp["id"], s["id"], s["id"] in stale, s["id"] in fresh) for s in SCHEMES
                    if s["id"] in stale or s["id"] in fresh]
            if mine:
                left[shp["id"]] = len(mine)
                jobs_of += mine

        # 매끈한 모양의 스텐실(테마와 무관한 160벌)을 먼저 병렬로 구워 한 파일에 모은다. 워커마다 굽게 두면
        # 같은 것을 2.7배 다시 굽고, 그 값은 구성표 수와 무관해서 구성표를 줄여도 안 줄었다 (2026-09-20)
        # 스텐실은 테마와 무관해서 코드에만 기댄다 — 그림만 고쳤으면 다시 굽지 않는다
        if any(shape_of(j[0]) is not None for j in jobs_of) \
                and (was.get("*stencil") != code or not STENCILS.exists()):
            baked = dict(pool.map(bake, smoothlib.stencil_keys()))
            STENCILS.write_bytes(pickle.dumps(baked, protocol=pickle.HIGHEST_PROTOCOL))
            print(f"[{time.time() - t0:5.1f}초] 스텐실 {len(baked)}벌 구움")
        # 오래 걸리는 것부터 넣는다 — 긴 것이 맨 뒤에 오면 그 하나가 꼬리가 된다. 그릴 프레임 수 순.
        # 매끈한 모양은 프레임마다 세 크기로 새로 칠해서 기본 모양보다 프레임당 몇 배 무겁다.
        # 시안 데이터만 그리는 일감은 한 크기 몫 (차례만 정하는 어림이라 정확할 필요는 없다)
        def cost(job):
            shape_id, sid, want_dist, _ = job
            smooth = shape_of(shape_id) is not None
            n = sum(frames[sid, rid] for rid, _, _ in ROLES + EXTRA if not (smooth and rid in KEEPS[sid]))
            return n * (3 if smooth and want_dist else 1)
        jobs_of.sort(key=cost, reverse=True)
        t_sub = time.time()
        jobs = {pool.submit(timed, build_one, j): j for j in jobs_of}
        whole = sum(map(cost, jobs_of)) or 1            # 진행률은 이 어림 값의 합으로 센다

        out = HERE / "preview.html"                      # 그동안 이쪽에서는 페이지를 만든다
        if was.get("*page") != page_key or not out.exists():
            _load_stencils()                             # 모양 탭 아이콘도 매끈한 모양이다
            out.write_text(build(), encoding="utf-8", newline="\n")
            print(f"[{time.time() - t0:5.1f}초] {out.name} 만듦")
        total, made, spent, per_sid, got, step = 0, {}, {}, {}, 0, 1
        spans = []                                      # (시작, 끝) — 가동률과 꼬리를 잰다
        for n, done in enumerate(as_completed(jobs), 1):
            (count, piece), a, b = done.result()
            spans.append((a, b))
            total += count
            shape_id, sid, _, _ = job = jobs[done]
            if piece is not None:
                pieces[shape_id][sid] = piece
            per_sid[sid] = per_sid.get(sid, 0) + b - a
            spent[shape_id] = spent.get(shape_id, 0) + b - a
            got += cost(job)
            left[shape_id] -= 1
            made[shape_id] = made.get(shape_id, 0) + count
            # 모양 하나가 다 끝났을 때 한 줄 (시안 데이터도 그때 쓴다), 그 사이엔 어림 진행률이 10% 넘을 때마다 한 줄
            if not left[shape_id]:
                what = f"{shape_id} 커서 {made[shape_id]}개"
                if shape_id in pieces:
                    what += f" · data/{shape_id}/" + ("" if len(pieces[shape_id]) == len(SCHEMES)
                                                          else f" (구성표 {len(pieces[shape_id])}종만)")
                    write_data(shape_id, pieces.pop(shape_id))
                print(f"[{time.time() - t0:5.1f}초] {what} · 워커 시간 {_dur(spent[shape_id])}")
            if got * 10 >= whole * step and got < whole:
                step = got * 10 // whole + 1
                rest = sum(spent.values()) * (whole - got) / got / workers
                print(f"[{time.time() - t0:5.1f}초] 진행 {got * 100 // whole}% · 일감 {n}/{len(jobs)}"
                      f" · 커서 {total:,}개 · 남은 어림 {_dur(rest)}")
        if spans:
            # 가동률 = 워커들이 실제로 일한 시간 / (워커 수 × 걸린 시간). 꼬리 = 마지막 일감이 워커에 들어간
            # 뒤 처음 한 워커가 놀기 시작한 때부터 전부 끝날 때까지 — 차례 어림이 틀리면 여기가 길어진다
            last_in = max(a for a, _ in spans)
            end = max(b for _, b in spans)
            idle_from = min(b for _, b in spans if b >= last_in)
            busy = sum(b - a for a, b in spans)
            print(f"워커 {workers}개 · 일한 시간 합 {_dur(busy)} · 가동률 {busy * 100 / (workers * (end - t_sub)):.0f}%"
                  f" · 꼬리 {end - idle_from:.1f}초")
        if per_sid:
            top = sorted(per_sid.items(), key=lambda kv: -kv[1])[:5]
            print("무거운 구성표 (모양 전부 합친 워커 시간): " + " · ".join(f"{k} {_dur(v)}" for k, v in top))

    STAMP.write_text(json.dumps({**art, "*": every, "*page": page_key, "*stencil": code}), encoding="utf-8", newline="\n")
    update_readme()
    print(f"dist/ 커서 {total}개 만듦 (그대로 둔 구성표 {skipped}개) · 전부 {time.time() - t0:.1f}초")

# SPDX-License-Identifier: Apache-2.0
"""art/ 의 구성표 그림으로 preview.html 과 dist/<구성표>/*.cur 를 다시 만든다.

사용법: python build.py

모양마다 그림 데이터는 data/<모양>/ 으로 따로 나간다 (index.json 과 구성표마다 한 파일 — split_data 참고).
preview.html 에는 기본 모양의 칸 정보·목록 화살표와 처음 여는 구성표(START) 하나의 그림만 들어간다.
dist/ 의 커서 파일은 시안 페이지 버튼이 GitHub Pages 에서 내려받는다 (기본 모양은 dist/<구성표>/,
나머지는 dist/<모양>/<구성표>/). art/ 나 shapes/ 를 고치면 이걸 다시 돌리고 결과까지 커밋해야 웹에 반영된다.
"""
import ast
import base64
import hashlib
import json
import os
import pickle
import shutil
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
START = "rainbowflow"   # 시안 페이지가 처음 여는 구성표. 이것의 기본 모양 그림만 페이지에 박는다
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


def _tree(path: Path) -> ast.Module:
    """주석·docstring 을 걷어 낸 구문 나무. 해시를 여기서 떠서 주석만 고친 커밋은 커서를 다시 그리지 않는다
    (2026-09-30 주석 한 줄 고친 8ce80f86 이 CI 에서 75종을 전부 다시 그렸다)"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and body \
                and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                and isinstance(body[0].value.value, str):
            node.body = body[1:] or [ast.Pass()]
    return tree


def _dump(nodes) -> str:
    return "\n".join(ast.dump(n) for n in nodes)      # 줄 번호는 안 들어간다 — 위에 줄을 더해도 그대로


def _reach(tree: ast.Module, roots: set[str]) -> list:
    """roots 에서 이름으로 닿는 맨 윗단 정의(함수·대입·import)만, 소스 차례대로.
    워커가 부르는 것만 해시에 넣으려고 — 시안 페이지·README·main 을 고쳐도 커서는 다시 그리지 않는다"""
    named: dict[str, list] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names = [node.name]
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [n.id for t in targets for n in ast.walk(t) if isinstance(n, ast.Name)]
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [(a.asname or a.name).split(".")[0] for a in node.names]
        else:
            continue
        for name in names:
            named.setdefault(name, []).append(node)
    seen, todo = set(), list(roots)
    while todo:
        for node in named.get(todo.pop(), ()):
            if id(node) not in seen:
                seen.add(id(node))
                todo += [n.id for n in ast.walk(node) if isinstance(n, ast.Name)]
    return [n for n in tree.body if id(n) in seen]


def _only_shape(tree: ast.Module, shape: str) -> ast.Module:
    """smooth.py 의 SHAPES 표에서 이 모양 줄만 남긴 나무 — 둥근 모양 숫자를 고치면 둥근 모양만 다시 그린다.
    smooth 는 SHAPES 를 늘 SHAPES[모양] 으로만 읽는다 (stencil_keys 의 목록 돌기는 스텐실 해시가 따로 본다)"""
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SHAPES" for t in node.targets) \
                and isinstance(node.value, ast.Dict):
            keep = [(k, v) for k, v in zip(node.value.keys, node.value.values)
                    if isinstance(k, ast.Constant) and k.value == shape]
            node.value = ast.Dict(keys=[k for k, _ in keep], values=[v for _, v in keep])
    return tree


def _hashes() -> tuple[dict, dict, str]:
    """(일감별 재료 해시 {"<모양>/<구성표>": …}, 따로 쓰는 표식 {"*stencil", "*data/<모양>"}, 시안 페이지 해시).
    지난번과 같은 일감은 건너뛴다.

    일감마다 그 일감이 실제로 읽는 것만 넣는다 — 구성표의 그림·schemes.json 줄, make_cur·shape,
    build.py 중 워커가 부르는 부분, 매끈한 모양이면 smooth.py(SHAPES 는 제 모양 줄만).
    코드는 주석·docstring 을 걷어 낸 구문 나무로 잰다. 코드 한 줄이 구성표 전부를 다시 그리게 하던 때는
    CI 미스가 잡 20분이 넘었다 (2026-10-03 run #219, 워커 시간 82분)"""
    # 파이썬·zlib 버전도 코드로 친다. PNG 바이트가 버전마다 달라서, 다른 파이썬이 만든 캐시를
    # 받으면(러너의 3.14 패치가 올라간 날 등) 섞이지 않고 전부 다시 그려야 한다 — 릴리스가 캐시를 쓴다
    env = _sha(sys.version, zlib.ZLIB_RUNTIME_VERSION)
    base = _sha(env, *(_dump([_tree(HERE / n)]) for n in ("make_cur.py", "shape.py")),
                _dump(_reach(_tree(HERE / "build.py"), {"build_one", "bake"})))
    code = {shp["id"]: base if shape_of(shp["id"]) is None
            else _sha(base, shp["id"], _dump([_only_shape(_tree(HERE / "smooth.py"), shp["id"])]))
            for shp in SHAPES}
    art = {s["id"]: _sha(json.dumps(s, sort_keys=True),
                         *(f.read_bytes() for f in sorted((HERE / "art" / s["id"]).iterdir())))
           for s in SCHEMES}
    keys = {f"{shp['id']}/{sid}": _sha(code[shp["id"]], art[sid]) for shp in SHAPES for sid in drawn(shp["id"])}
    marks = {"*stencil": _sha(env, _dump([_tree(HERE / "smooth.py")]))}
    tree = _tree(HERE / "build.py")
    # 모양 데이터는 구성표 목록 차례까지 한 묶음이라 하나만 바뀌거나 빠져도 그 모양 data 를 다시 맞춘다.
    # data 파일을 나누고 쓰는 코드(부모가 돌린다)도 넣는다 — 빠졌을 때는 split_data 를 고쳐도 data 가 옛 꼴로 남았다
    writer = _dump(_reach(tree, {"write_data", "data_missing"}))
    for shp in SHAPES:
        marks[f"*data/{shp['id']}"] = _sha(writer, *(keys[f"{shp['id']}/{sid}"] for sid in drawn(shp["id"])))
    # 버전 표시를 해시에 넣는다 — 커밋이 바뀌면 그림이 그대로여도 페이지를 다시 만들어야 한다.
    # 페이지를 짜는 코드와 모양 탭 이름(shapes.json)도 — 빠졌을 때는 커밋 전에 build() 를 고쳐 돌려도 페이지가 그대로였다
    return keys, marks, _sha(*keys.values(), (HERE / "preview.tpl.html").read_bytes(), version(),
                             _dump(_reach(tree, {"build"})), (HERE / "shapes.json").read_bytes())


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
# 나머지 11칸. 테마 화살표·모래시계에서 만든 것이지만 시안에는 여섯 칸처럼 카드(핫스팟·크기)로 펼친다 —
# 작은 그림으로만 보이던 때는 핫스팟이 어디인지 안 보였다
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
# 기본 모양으로만 내는 구성표(해양 생물 · 애니). 매끈한 모양으로 다시 그리지 않아 dist/<모양>/·data/<모양>/ 에
# 없고, 시안 페이지는 어느 모양 탭에서든 이것의 기본 그림을 보이고 적용 주소에 모양을 안 붙인다.
# 그래서 지금은 SWAYS 로 그릴 일이 없다 — 표식을 떼면 다시 그려진다
CLASSIC_ONLY = {s["id"] for s in SCHEMES if s.get("classic_only")}


def drawn(shape_id: str) -> list[str]:
    """그 모양으로 그리는 구성표들. 테스트가 SCHEMES 를 갈아 끼우므로 부를 때마다 센다"""
    return [s["id"] for s in SCHEMES if shape_id == SHAPES[0]["id"] or s["id"] not in CLASSIC_ONLY]


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
    """탭 아이콘. 직접 그린 분홍 화살표를 가운데 두고 꽉 채운 64px (저장소와 같은 Apache-2.0, 외부 아이콘 안 씀).
    그림은 `favicon.txt` — 분홍 구성표를 지울 때(2026-10-04) 그 화살표 한 장만 옮겨 살렸다"""
    text = (HERE / "favicon.txt").read_text(encoding="utf-8")
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
    groups: dict[str, list[str]] = {}
    for scheme in SCHEMES:
        sid, sname, sdesc = scheme["id"], scheme["name"], scheme["desc"]
        cards = []
        for rid, rlabel, fallback in ROLES + EXTRA:
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
      <div class="grid">{"".join(cards[:len(ROLES)])}</div>
      <div class="extras"><h4>나머지 11칸</h4><div class="grid">{"".join(cards[len(ROLES):])}</div></div>
    </div>""")

    # 모양 탭. 단추에 붙는 그림은 첫 구성표의 화살표를 그 모양으로 그린 것
    tabs = []
    for i, shp in enumerate(SHAPES):
        pic = uri_of(page_bits(SCHEMES[0]["id"], "arrow", shape_of(shp["id"]), {})[0][0])
        tabs.append(f'<button type="button" class="shape c-hand{" smooth" if i else ""}" role="tab" data-shape="{shp["id"]}"'
                    f' aria-selected="{"true" if i == 0 else "false"}"><i style="background-image:url({pic})"></i>{shp["name"]}</button>')

    # 기본 모양 그림도 다른 모양처럼 data/<기본>/ 로 내보내고, 페이지에는 칸 정보·목록 화살표와 START 그림만 남긴다.
    # 전부 박던 때는 페이지가 gzip 1.3MB 라 폰 회선에서 그것을 다 받을 때까지 첫 화면이 안 떴다
    write_split(SHAPES[0]["id"], {"data": data})
    data = {sid: {rid: e if sid == START or rid == "arrow" else ["", *e[1:]] for rid, e in roles.items()}
            for sid, roles in data.items()}

    page = (
        (HERE / "preview.tpl.html").read_text(encoding="utf-8")
        .replace("/*START*/", json.dumps(START))
        .replace("/*CLASSIC_ONLY*/", json.dumps(sorted(CLASSIC_ONLY)))
        .replace("/*KEEP*/", json.dumps(sorted(KEEP)))
        .replace("<!--SHAPES-->", "".join(tabs))
        .replace("/*SHAPE_LIST*/", json.dumps([{k: s[k] for k in ("id", "name", "desc")} for s in SHAPES], ensure_ascii=False, separators=(",", ":")))
        .replace("/*CURSOR_CSS*/", "\n".join(css))
        .replace("/*CURSOR_DATA*/", json.dumps(data, separators=(",", ":")))
        .replace("<!--FAVICON-->", favicon())
        .replace("<!--VERSION-->", version())
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
    """시안 데이터의 칸 하나. [스트립, 핫스팟 x, y, 대체 커서, rate, 폭, 높이, 프레임 수, 잉크 상자].
    잉크 상자는 화살표만 (나머지는 0)"""
    pngs, hx, hy, rate, w, h = page_bits(sid, rid, shape, cache, ats)
    uri, box = strip(pngs, rid == "arrow")
    fallback = next(f for r, _, f in ROLES + EXTRA if r == rid)
    return [uri, hx, hy, fallback, rate, w, h, len(pngs), box]


def splice(pieces: dict[str, dict], old: dict | None, sids: list[str]) -> dict:
    """구성표별 조각 {구성표: 칸들} 을 sids 차례로 이어 {"data": …} 로.
    old 를 주면 조각이 없는 구성표는 지난번 것을 그대로 옮긴다"""
    return {"data": {sid: pieces[sid] if sid in pieces else old["data"][sid] for sid in sids}}


def shape_data(shape_id: str, sids: list[str], old: dict | None) -> dict:
    """다른 모양의 페이지 데이터. 기본 모양이 preview.html 에 박혀 있는 것과 같은 구조.

    old 를 주면 sids 에 든 구성표만 새로 그리고 나머지는 지난번 것을 그대로 옮긴다."""
    shape, cache = shape_of(shape_id), {}
    pieces = {}
    for sid in drawn(shape_id):
        if old is None or sid in sids:
            pieces[sid] = {rid: data_bit(sid, rid, shape, cache) for rid, _, _ in ROLES + EXTRA}
            cache.pop(sid, None)
    return splice(pieces, old, drawn(shape_id))


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
    count, data = 0, {}
    for rid, _, _ in ROLES + EXTRA:
        ats: dict = {}                                  # 칸마다 새로 — 한 칸 그림만 들고 있게 (메모리)
        # 모양이 안 건드리는 칸은 기본 모양 파일과 바이트까지 같다. 두 번 쓰지 않고
        # 받는 쪽(handler.ps1, install.ps1)이 dist/<구성표>/ 것으로 넘어간다
        if want_dist and not (shape is not None and rid in KEEP):
            blob, ext = cursor_bytes(sid, rid, shape, cache, ats)
            (out / f"{rid}.{ext}").write_bytes(blob)
            count += 1
        if want_data:
            data[rid] = data_bit(sid, rid, shape, cache, ats)
    return count, (data if want_data else None)


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
        files[f"{sid}.json"] = {"data": {rid: e[0] for rid, e in roles.items()}}
    return files


def read_data(shape_id: str) -> dict | None:
    """split_data 의 거꾸로. 지난번 파일들이 온전하지 않으면 None"""
    root = data_dir(shape_id)
    try:
        index = json.loads((root / "index.json").read_text(encoding="utf-8"))["data"]
        data = {}
        for sid, roles in index.items():
            one = json.loads((root / f"{sid}.json").read_text(encoding="utf-8"))
            data[sid] = {rid: [one["data"][rid], *e[1:]] for rid, e in roles.items()}
        return {"data": data}
    except (OSError, KeyError, ValueError):
        return None


def data_missing(shape_id: str) -> set[str] | None:
    """지난번 data/<모양>/ 에 없는 지금 구성표들 — 이것과 재료가 바뀐 구성표만 새로 그리면 된다.
    지난번 것을 못 읽으면 None (전부 그린다). 빠진 구성표는 splice 가 drawn 차례로 이어 붙이며 저절로 떨어진다.
    구성표 목록이 조금만 달라져도 None 이던 때는 한 종을 지워도 64종 × 매끈한 모양 10가지를 다시 그렸다"""
    old = read_data(shape_id)
    return None if old is None else set(drawn(shape_id)) - set(old["data"])


def write_split(shape_id: str, whole: dict) -> None:
    """split_data 를 data/<모양>/ 에 쓰고, 이번에 안 쓴 .json(지운 구성표의 것)은 지운다.
    남겨 두면 CI 캐시를 타고 Pages 에 계속 올라간다"""
    root = data_dir(shape_id)
    root.mkdir(parents=True, exist_ok=True)
    files = split_data(whole)
    for name, body in files.items():
        (root / name).write_text(json.dumps(body, separators=(",", ":")), encoding="utf-8", newline="\n")
    for f in root.glob("*.json"):
        if f.name not in files:
            f.unlink()


def write_data(shape_id: str, pieces: dict[str, dict]) -> None:
    """모양 하나의 시안 페이지 데이터 data/<모양>/. 지난번 파일이 있으면 조각이 온 구성표만 갈아 끼운다.
    코드가 바뀌면 모든 구성표의 조각이 오므로(해시에 코드가 섞여 있다) 통째로 다시 쓰인다"""
    sids = drawn(shape_id)
    old = read_data(shape_id) if len(pieces) < len(sids) else None
    write_split(shape_id, splice(pieces, old, sids))
    # 한 파일에 다 넣던 때의 data/<모양>.json. 남겨 두면 Pages 에 모양마다 24MB 씩 그대로 올라간다
    (HERE / "data" / f"{shape_id}.json").unlink(missing_ok=True)


def prune() -> list[str]:
    """지금 목록에 없는 구성표·모양의 dist·data 폴더를 지운다. 기본 모양으로만 내는 구성표의 모양 폴더도. 지운 경로를 돌려준다.
    handler.ps1 은 적용할 때 받아 두므로 이미 쓰는 사람의 커서는 안 깨진다"""
    sids, shps = {s["id"] for s in SCHEMES}, {s["id"] for s in SHAPES}
    dist, data = HERE / "dist", HERE / "data"
    gone = [d for d in dist.glob("*/") if d.name not in sids | shps] if dist.is_dir() else []
    gone += [d for shp in shps - {SHAPES[0]["id"]} if (dist / shp).is_dir()
             for d in (dist / shp).glob("*/") if d.name not in sids - CLASSIC_ONLY]
    gone += [d for d in data.glob("*/") if d.name not in shps] if data.is_dir() else []
    for d in gone:
        shutil.rmtree(d)
    return [str(d.relative_to(HERE)) for d in gone]


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
    # --plan 은 무엇을 다시 그릴지만 찍고 끝낸다 (아무것도 안 지우고 안 쓴다)
    keys, marks, page_key = _hashes()
    plan = "--plan" in sys.argv
    was = {} if "--all" in sys.argv else json.loads(STAMP.read_text()) if STAMP.exists() else {}
    for path in [] if plan else prune():
        print(f"[{time.time() - t0:5.1f}초] 목록에 없어 지움: {path}")

    workers = getattr(os, "process_cpu_count", os.cpu_count)() or 1   # ProcessPoolExecutor 기본값과 같다
    with ProcessPoolExecutor(workers) as pool:
        jobs_of, skipped = [], 0
        # 일감 차례를 정할 어림 값 — 그림 프레임 수. 움직이는 구성표 몇이 일의 대부분이다
        frames = {(s["id"], rid): len(split_frames(art_raw(s["id"], rid))) for s in SCHEMES for rid, _, _ in ROLES + EXTRA}
        left: dict[str, int] = {}                       # 모양마다 남은 일감. 다 끝나면 한 줄 찍는다
        pieces: dict[str, dict] = {}                    # 시안 데이터를 새로 쓸 모양 → 구성표별 조각
        for shp in SHAPES:
            base = shp["id"] == SHAPES[0]["id"]
            root = HERE / "dist" if base else HERE / "dist" / shp["id"]
            sids = drawn(shp["id"])
            # 재료가 바뀐 일감. dist 는 여기에 "폴더가 없는 것"을 더하고, data 는 이 목록만 갈아 끼운다
            changed = {sid for sid in sids if was.get(f"{shp['id']}/{sid}") != keys[f"{shp['id']}/{sid}"]}
            stale = {sid for sid in sids if sid in changed or not (root / sid).is_dir()}
            skipped += len(sids) - len(stale)
            fresh: set[str] = set()                     # 시안 데이터 조각을 새로 그릴 구성표
            mark = f"*data/{shp['id']}"
            if not base and (was.get(mark) != marks[mark] or not (data_dir(shp["id"]) / "index.json").exists()):
                missing = data_missing(shp["id"])
                fresh = set(sids) if missing is None else (changed | missing) & set(sids)
                if fresh:
                    pieces[shp["id"]] = {}
                elif plan:
                    print(f"{shp['id']}: 시안 데이터 다시 씀 (그리지 않고 지난 것을 옮김)")
                else:                                   # 구성표를 지웠거나 data 쓰는 코드만 바뀌었다 — 그릴 것 없이 다시 쓴다
                    write_data(shp["id"], {})
            # (모양 × 구성표) 하나가 일감 하나. 커서와 시안 데이터를 한 일감에서 같이 만든다.
            # 스텐실은 아래서 먼저 구워 나눠 쓰므로 잘게 쪼개도 다시 굽지 않는다.
            # 모양당 4묶음이던 때는 무거운 구성표(무지개 흐름·용암)가 한 묶음에 몰려 그 묶음이 2배 걸렸고,
            # 마지막 모양의 묶음만 남아 워커 8개가 20초 넘게 놀았다 (2026-09-24, 5600X 262초 중 22초)
            mine = [(shp["id"], sid, sid in stale, sid in fresh) for sid in sids if sid in stale or sid in fresh]
            if mine:
                left[shp["id"]] = len(mine)
                jobs_of += mine
                if plan:
                    print(f"{shp['id']}: 커서 {sum(j[2] for j in mine)}종 · 시안 데이터 {sum(j[3] for j in mine)}종"
                          f" (구성표 {len(sids)}종 중)" + ("" if len(mine) > 8 else " — " + " ".join(j[1] for j in mine)))
        if plan:
            print(f"다시 그릴 일감 {len(jobs_of)}개 · 그대로 둘 구성표 {skipped}개 (모양별 합)"
                  + (" · 스텐실 다시 구움" if was.get("*stencil") != marks["*stencil"] else "")
                  + (" · 페이지 다시 만듦" if was.get("*page") != page_key else ""))
            raise SystemExit

        # 매끈한 모양의 스텐실(테마와 무관한 160벌)을 먼저 병렬로 구워 한 파일에 모은다. 워커마다 굽게 두면
        # 같은 것을 2.7배 다시 굽고, 그 값은 구성표 수와 무관해서 구성표를 줄여도 안 줄었다 (2026-09-20)
        # 스텐실은 테마와 무관해서 코드에만 기댄다 — 그림만 고쳤으면 다시 굽지 않는다
        if any(shape_of(j[0]) is not None for j in jobs_of) \
                and (was.get("*stencil") != marks["*stencil"] or not STENCILS.exists()):
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
        if was.get("*page") != page_key or not out.exists() or not (data_dir(SHAPES[0]["id"]) / "index.json").exists():
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
                    what += f" · data/{shape_id}/" + ("" if len(pieces[shape_id]) == len(drawn(shape_id))
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

    STAMP.write_text(json.dumps({**keys, **marks, "*page": page_key}, indent=0), encoding="utf-8", newline="\n")
    update_readme()
    print(f"dist/ 커서 {total}개 만듦 (그대로 둔 구성표 {skipped}개) · 전부 {time.time() - t0:.1f}초")

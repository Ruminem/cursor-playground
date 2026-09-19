# SPDX-License-Identifier: Apache-2.0
"""art/ 의 구성표 그림으로 preview.html 과 dist/<구성표>/*.cur 를 다시 만든다.

사용법: python build.py

preview.html 에는 기본 모양의 그림 데이터가 들어가고, 다른 모양은 data/<모양>.json 으로 따로 나간다.
dist/ 의 커서 파일은 시안 페이지 버튼이 GitHub Pages 에서 내려받는다 (기본 모양은 dist/<구성표>/,
나머지는 dist/<모양>/<구성표>/). art/ 나 shapes/ 를 고치면 이걸 다시 돌리고 결과까지 커밋해야 웹에 반영된다.
"""
import base64
import hashlib
import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import shape as shapelib
import smooth as smoothlib
from make_cur import canvas_size, is_animated, is_row, read_hotspot, read_rate, split_frames, txt_to_ani, txt_to_cur, txt_to_png

HERE = Path(__file__).parent

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


def _hashes() -> tuple[dict, str, str]:
    """(구성표별 재료 해시, 전부 합친 해시, 시안 페이지 해시). 지난번과 같으면 그 산출물은 건너뛴다"""
    code = _sha(*((HERE / n).read_bytes() for n in ("build.py", "make_cur.py", "shape.py", "smooth.py", "shapes.json")))
    art = {s["id"]: _sha(code, json.dumps(s, sort_keys=True),
                         *(f.read_bytes() for f in sorted((HERE / "art" / s["id"]).iterdir())))
           for s in SCHEMES}
    # 시안 페이지와 모양 데이터는 구성표 전부를 한 파일에 담아서 하나만 바뀌어도 다시 만든다
    every = _sha(*(art[s["id"]] for s in SCHEMES))
    # 버전 표시를 해시에 넣는다 — 커밋이 바뀌면 그림이 그대로여도 페이지를 다시 만들어야 한다
    return art, every, _sha(every, (HERE / "preview.tpl.html").read_bytes(), version())


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


def page_bits(sid: str, rid: str, shape: str | None, cache: dict) -> tuple[list[str], int, int, int, int, int]:
    """시안 페이지에 넣을 (프레임별 그림 주소, 핫스팟 x, y, rate(ms), 폭, 높이)"""
    if shape is None or rid in KEEP:
        raw = art_raw(sid, rid)
        src = canvas_size(raw)
        pngs = [txt_to_png(f, None, src) for f in split_frames(raw)]
        hx, hy = read_hotspot(raw) or (0, 0)
        rows = [r for r in split_frames(raw)[0].splitlines() if is_row(r)]
        rate = read_rate(raw)
        w, h = max(len(r) for r in rows), len(rows)
    else:
        frames, rate, glyphs = smooth_parts(sid, rid, shape, cache)
        pngs, (hx, hy), (w, h) = smoothlib.page(shape, rid, frames, glyphs, MAT.get(sid))
    return (["data:image/png;base64," + base64.b64encode(p).decode() for p in pngs],
            hx, hy, rate * 1000 // 60, w, h)


def cursor_bytes(sid: str, rid: str, shape: str | None, cache: dict) -> tuple[bytes, str]:
    """dist 에 넣을 커서 파일 하나와 확장자"""
    if shape is None or rid in KEEP:
        raw = art_raw(sid, rid)
        hot = read_hotspot(raw) or (0, 0)
        return (txt_to_ani(raw, hot), "ani") if is_animated(raw) else (txt_to_cur(raw, hot), "cur")
    frames, rate, glyphs = smooth_parts(sid, rid, shape, cache)
    return smoothlib.cursor(shape, rid, frames, rate, glyphs, MAT.get(sid))


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
        cards, thumb = [], ""
        for rid, rlabel, fallback in ROLES:
            # 움직이는 커서는 프레임마다 그림을 넣어 두고 페이지 스크립트가 번갈아 끼운다. CSS 기본값은 첫 프레임
            uris, hx, hy, rate, w, h = page_bits(sid, rid, None, {})
            uri = uris[0]
            css.append(
                f'[data-scheme="{sid}"] .c-{rid},[data-scheme="{sid}"].c-{rid},.card.s-{sid}.c-{rid}'
                f"{{cursor:url({uri}) {hx} {hy},{fallback}}}"
            )
            data.setdefault(sid, {})[rid] = [uris, hx, hy, fallback, rate, w, h]
            if rid == "arrow":
                thumb = uri
            cards.append(f"""
        <article class="card s-{sid} c-{rid}" tabindex="0">
          <div class="stage" style="--hx:{hx};--hy:{hy}">
            <div class="sprite" style="background-image:url({uri})"></div>
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
            pics, _, _, rate, _, _ = page_bits(sid, rid, None, {})
            # 움직이거나 색조를 바꿀 때 페이지 스크립트가 프레임을 번갈아 끼울 수 있게 넘긴다
            extra_data.setdefault(sid, {})[rid] = [pics, rate]
            extras.append(f'<div class="extra s-{sid} e-{rid}"><span class="pic"><i style="background-image:url({pics[0]})"></i></span>{rlabel}</div>')
        search = " ".join((sid, sname, scheme["name_en"], scheme["category"], scheme["category_en"])).lower()
        groups.setdefault(scheme["category"], []).append(f"""
      <div class="pick-wrap" data-scheme-item="{sid}" data-search="{search}">
        <button type="button" class="pick c-hand" data-pick="{sid}" aria-pressed="false">
          <span class="thumb" style="background-image:url({thumb})"></span>
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
        pic = page_bits(SCHEMES[0]["id"], "arrow", shape_of(shp["id"]), {})[0][0]
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


def shape_data(shape_id: str, sids: list[str], old: dict | None) -> dict:
    """다른 모양의 페이지 데이터. 기본 모양이 preview.html 에 박혀 있는 것과 같은 구조.

    old 를 주면 sids 에 든 구성표만 새로 그리고 나머지는 지난번 것을 그대로 옮긴다."""
    shape, cache = shape_of(shape_id), {}
    data: dict[str, dict[str, list]] = {}
    extra: dict[str, dict[str, list]] = {}
    for scheme in SCHEMES:
        sid = scheme["id"]
        if old is not None and sid not in sids:
            data[sid], extra[sid] = old["data"][sid], old["extra"][sid]
            continue
        for rid, _, fallback in ROLES:
            uris, hx, hy, rate, w, h = page_bits(sid, rid, shape, cache)
            data.setdefault(sid, {})[rid] = [uris, hx, hy, fallback, rate, w, h]
        for rid, _, _ in EXTRA:
            pics, _, _, rate, _, _ = page_bits(sid, rid, shape, cache)
            extra.setdefault(sid, {})[rid] = [pics, rate]
        cache.pop(sid, None)
    return {"data": data, "extra": extra}


def build_dist(job: tuple[str, str, list[str]]) -> tuple[str, int]:
    """모양 하나의 dist 커서. 맡은 구성표만 만든다 (프로세스를 나눠 돌리기 위함)"""
    shape_id, label, sids = job
    shape, cache = shape_of(shape_id), {}
    # 기본 모양은 dist/<구성표>/ 그대로 둔다 (이미 깔린 처리 스크립트가 그 주소를 쓴다)
    root = HERE / "dist" if shape is None else HERE / "dist" / shape_id
    count = 0
    for sid in sids:
        out = root / sid
        out.mkdir(parents=True, exist_ok=True)
        for rid, _, _ in ROLES + EXTRA:
            # 모양이 안 건드리는 칸은 기본 모양 파일과 바이트까지 같다. 두 번 쓰지 않고
            # 받는 쪽(handler.ps1, install.ps1)이 dist/<구성표>/ 것으로 넘어간다
            if shape is not None and rid in KEEP:
                continue
            blob, ext = cursor_bytes(sid, rid, shape, cache)
            (out / f"{rid}.{ext}").write_bytes(blob)
            count += 1
        cache.pop(sid, None)
    return f"dist {label}", count


def build_data(job: tuple[str, list[str]]) -> tuple[str, int]:
    """모양 하나의 시안 페이지 데이터 data/<모양>.json"""
    shape_id, sids = job
    path = HERE / "data" / f"{shape_id}.json"
    path.parent.mkdir(exist_ok=True)
    # 한 파일에 구성표 121종이 다 들어 있다. 지난번 파일이 있으면 바뀐 자리만 갈아 끼운다.
    # 코드가 바뀌면 모든 구성표가 sids 에 들어오므로(해시에 코드가 섞여 있다) 통째로 다시 그려진다
    old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    if old is not None and set(old.get("data", ())) != {s["id"] for s in SCHEMES}:
        old = None                                   # 구성표가 늘거나 줄었으면 옮겨 쓸 수 없다
    path.write_text(json.dumps(shape_data(shape_id, sids, old), separators=(",", ":")), encoding="utf-8", newline="\n")
    return f"data/{shape_id}.json" + (f" (구성표 {len(sids)}종만)" if old is not None else ""), 0


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
    art, every, page_key = _hashes()
    was = {} if "--all" in sys.argv else json.loads(STAMP.read_text()) if STAMP.exists() else {}

    with ProcessPoolExecutor() as pool:
        # 재료가 바뀐 구성표. dist 는 여기에 "폴더가 없는 것"을 더하고, data 는 이 목록만 갈아 끼운다
        changed = [s["id"] for s in SCHEMES if was.get(s["id"]) != art[s["id"]]]
        jobs, skipped = [], 0
        for shp in SHAPES:
            base = shp["id"] == SHAPES[0]["id"]
            root = HERE / "dist" if base else HERE / "dist" / shp["id"]
            stale = [s["id"] for s in SCHEMES
                     if s["id"] in changed or not (root / s["id"]).is_dir()]
            skipped += len(SCHEMES) - len(stale)
            if stale:
                # 프로세스로 나눈다. 잘게 쪼개면 프로세스마다 매끈한 모양의 스텐실을 다시 그린다
                parts = min(4 if base else 2, len(stale))
                jobs += [pool.submit(build_dist, (shp["id"], f"{shp['id']} {i + 1}/{parts}", stale[i::parts]))
                         for i in range(parts)]
            if not base and (was.get("*") != every or not (HERE / "data" / f"{shp['id']}.json").exists()):
                jobs.append(pool.submit(build_data, (shp["id"], changed or [s["id"] for s in SCHEMES])))

        out = HERE / "preview.html"                      # 그동안 이쪽에서는 페이지를 만든다
        if was.get("*page") != page_key or not out.exists():
            out.write_text(build(), encoding="utf-8", newline="\n")
            print(f"[{time.time() - t0:5.1f}초] {out.name} 만듦")
        total = 0
        for done in as_completed(jobs):
            what, count = done.result()
            total += count
            print(f"[{time.time() - t0:5.1f}초] {what}" + (f" 커서 {count}개" if count else ""))

    STAMP.write_text(json.dumps({**art, "*": every, "*page": page_key}), encoding="utf-8", newline="\n")
    update_readme()
    print(f"dist/ 커서 {total}개 만듦 (그대로 둔 구성표 {skipped}개) · 전부 {time.time() - t0:.1f}초")

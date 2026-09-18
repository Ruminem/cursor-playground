# SPDX-License-Identifier: Apache-2.0
"""art/ 의 구성표 그림으로 preview.html 과 dist/<구성표>/*.cur 를 다시 만든다.

사용법: python build.py

preview.html 에는 기본 모양의 그림 데이터가 들어가고, 다른 모양은 data/<모양>.json 으로 따로 나간다.
dist/ 의 커서 파일은 시안 페이지 버튼이 GitHub Pages 에서 내려받는다 (기본 모양은 dist/<구성표>/,
나머지는 dist/<모양>/<구성표>/). art/ 나 shapes/ 를 고치면 이걸 다시 돌리고 결과까지 커밋해야 웹에 반영된다.
"""
import base64
import json
from pathlib import Path

import shape as shapelib
from make_cur import canvas_size, is_animated, is_row, read_hotspot, read_rate, split_frames, txt_to_ani, txt_to_cur, txt_to_png

HERE = Path(__file__).parent

# 구성표 목록은 schemes.json 한 곳에 둔다 (install.ps1, handler.ps1 도 같은 파일을 읽음)
SCHEMES = json.loads((HERE / "schemes.json").read_text(encoding="utf-8"))
# 커서 모양(실루엣) 목록. 첫 번째가 기본이고, 나머지는 shapes/<모양>/ 의 실루엣에 테마 색을 입힌다
SHAPES = json.loads((HERE / "shapes.json").read_text(encoding="utf-8"))
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


# 모양과 상관없는 칸들. 테마 색으로만 그린 기호라 실루엣을 갈아 끼울 것이 없다
GLYPH_ONLY = {"ns", "we", "nwse", "nesw", "up", "cross", "pen"}


def masks_of(shape_id: str) -> dict | None:
    """모양의 여섯 실루엣. 기본 모양이면 None (원래 그림을 그대로 쓴다)"""
    if shape_id == SHAPES[0]["id"]:
        return None
    return {rid: shapelib.read_mask((HERE / "shapes" / shape_id / f"{rid}.txt").read_text(encoding="utf-8")) for rid, _, _ in ROLES}


def art_text(sid: str, rid: str, masks: dict | None, cache: dict) -> str:
    """구성표 한 칸의 그림 txt. masks 가 있으면 그 실루엣에 테마 색을 옮겨 담는다"""
    raw = (HERE / "art" / sid / f"{rid}.txt").read_text(encoding="utf-8")
    if masks is None or rid in GLYPH_ONLY:
        return raw
    frames, _, rate = shapelib.read_art(raw)
    if rid in masks:
        mask, inner, mhot = masks[rid]
        return shapelib.to_text(shapelib.reshape(frames, mask, inner), mhot, rate)
    # 화살표에 기호를 얹어 만든 칸(도움말·백그라운드 작업·위치·사용자)은 새 화살표에 그 기호를 다시 붙인다
    mask, inner, mhot = masks["arrow"]
    if sid not in cache:
        araw = (HERE / "art" / sid / "arrow.txt").read_text(encoding="utf-8")
        aframes = shapelib.read_art(araw)[0]
        cache[sid] = (aframes, shapelib.reshape(aframes, mask, inner))
    aframes, new = cache[sid]
    glyphs = shapelib.place(shapelib.glyph_of(aframes, frames),
                            shapelib.bbox([p for f in aframes for p in f]), shapelib.bbox(mask))
    return shapelib.to_text([{**n, **g} for n, g in zip(new, glyphs)], mhot, rate)


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
            text = art_text(sid, rid, None, {})
            hx, hy = read_hotspot(text) or (0, 0)
            frames, src = split_frames(text), canvas_size(text)
            # 움직이는 커서는 프레임마다 그림을 넣어 두고 페이지 스크립트가 번갈아 끼운다. CSS 기본값은 첫 프레임
            uris = ["data:image/png;base64," + base64.b64encode(txt_to_png(f, None, src)).decode() for f in frames]
            uri = uris[0]
            rows = [r for r in frames[0].splitlines() if is_row(r)]
            w, h = max(len(r) for r in rows), len(rows)
            css.append(
                f'[data-scheme="{sid}"] .c-{rid},[data-scheme="{sid}"].c-{rid},.card.s-{sid}.c-{rid}'
                f"{{cursor:url({uri}) {hx} {hy},{fallback}}}"
            )
            data.setdefault(sid, {})[rid] = [uris, hx, hy, fallback, read_rate(text) * 1000 // 60, w, h]
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
            text = art_text(sid, rid, None, {})
            src = canvas_size(text)
            pics = ["data:image/png;base64," + base64.b64encode(txt_to_png(f, None, src)).decode() for f in split_frames(text)]
            # 움직이거나 색조를 바꿀 때 페이지 스크립트가 프레임을 번갈아 끼울 수 있게 넘긴다
            extra_data.setdefault(sid, {})[rid] = [pics, read_rate(text) * 1000 // 60]
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
        text = art_text(SCHEMES[0]["id"], "arrow", masks_of(shp["id"]), {})
        pic = "data:image/png;base64," + base64.b64encode(txt_to_png(split_frames(text)[0], None, canvas_size(text))).decode()
        tabs.append(f'<button type="button" class="shape c-hand" role="tab" data-shape="{shp["id"]}"'
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


def shape_data(shape_id: str) -> dict:
    """다른 모양의 페이지 데이터. 기본 모양이 preview.html 에 박혀 있는 것과 같은 구조"""
    masks, cache = masks_of(shape_id), {}
    data: dict[str, dict[str, list]] = {}
    extra: dict[str, dict[str, list]] = {}
    for scheme in SCHEMES:
        sid = scheme["id"]
        for rid, _, fallback in ROLES:
            text = art_text(sid, rid, masks, cache)
            hx, hy = read_hotspot(text) or (0, 0)
            frames, src = split_frames(text), canvas_size(text)
            uris = ["data:image/png;base64," + base64.b64encode(txt_to_png(f, None, src)).decode() for f in frames]
            rows = [r for r in frames[0].splitlines() if is_row(r)]
            data.setdefault(sid, {})[rid] = [uris, hx, hy, fallback, read_rate(text) * 1000 // 60,
                                             max(len(r) for r in rows), len(rows)]
        for rid, _, _ in EXTRA:
            text = art_text(sid, rid, masks, cache)
            src = canvas_size(text)
            pics = ["data:image/png;base64," + base64.b64encode(txt_to_png(f, None, src)).decode() for f in split_frames(text)]
            extra.setdefault(sid, {})[rid] = [pics, read_rate(text) * 1000 // 60]
        cache.pop(sid, None)
    return {"data": data, "extra": extra}


def build_dist() -> int:
    count = 0
    for shp in SHAPES:
        masks, cache = masks_of(shp["id"]), {}
        # 기본 모양은 dist/<구성표>/ 그대로 둔다 (이미 깔린 처리 스크립트가 그 주소를 쓴다)
        root = HERE / "dist" if masks is None else HERE / "dist" / shp["id"]
        for scheme in SCHEMES:
            sid = scheme["id"]
            out = root / sid
            out.mkdir(parents=True, exist_ok=True)
            for rid, _, _ in ROLES + EXTRA:
                text = art_text(sid, rid, masks, cache)
                hot = read_hotspot(text) or (0, 0)
                if is_animated(text):
                    (out / f"{rid}.ani").write_bytes(txt_to_ani(text, hot))
                else:
                    (out / f"{rid}.cur").write_bytes(txt_to_cur(text, hot))
                count += 1
            cache.pop(sid, None)
    return count


def update_readme() -> None:
    """README 의 영어·한국어 구성표·모양 표를 schemes.json, shapes.json 으로 다시 채운다 (두 언어가 어긋나지 않게)"""
    path = HERE / "README.md"
    text = path.read_text(encoding="utf-8")
    for lang, name, desc, cat, head, shead in (
        ("en", "name_en", "desc_en", "category_en", "| Folder | Name | Style |", "| Folder | Name | Look |"),
        ("ko", "name", "desc", "category", "| 폴더 | 이름 | 스타일 |", "| 폴더 | 이름 | 생김새 |"),
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
            where = "art/" if i == 0 else f"shapes/{s['id']}"
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
    out = HERE / "preview.html"
    out.write_text(build(), encoding="utf-8", newline="\n")
    print(f"{out} 만듦")
    for shp in SHAPES[1:]:
        path = HERE / "data" / f"{shp['id']}.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(shape_data(shp["id"]), separators=(",", ":")), encoding="utf-8", newline="\n")
        print(f"{path.name} 만듦")
    print(f"dist/ 커서 {build_dist()}개 만듦")
    update_readme()
    print("README 구성표 표 갱신함")

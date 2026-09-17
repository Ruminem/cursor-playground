# SPDX-License-Identifier: Apache-2.0
"""art/ 의 구성표 그림으로 preview.html 과 dist/<구성표>/*.cur 를 다시 만든다.

사용법: python build.py

preview.html 에는 그림 데이터가 들어가고, dist/ 의 커서 파일은 시안 페이지 버튼이 GitHub Pages 에서 내려받는다.
art/ 를 고치면 이걸 다시 돌리고 결과까지 커밋해야 웹에 반영된다.
"""
import base64
from pathlib import Path

from make_cur import png_to_cur, read_hotspot, txt_to_png

HERE = Path(__file__).parent

# install.ps1 의 $schemes 와 순서·이름을 맞춘다
SCHEMES = [
    ("pink", "분홍", "검은 외곽선에 분홍 채우기. 기본 크기의 또렷한 픽셀."),
    ("neon", "네온", "속이 빈 어두운 몸체에 청록·자홍 관, 바깥으로 반투명 번짐."),
    ("minimal", "미니멀", "절반 크기의 가는 검정 실루엣과 흰 테두리. 점 하나짜리 링크."),
    ("onebit", "1비트", "흑백 두 색에 디더링 음영과 딱딱한 그림자, 손가락 링크."),
    ("fantasy", "판타지", "은빛 칼, 나무 모래시계, 방패, 나침반, 마법 지팡이."),
]
# 파일, 칸 이름, 브라우저가 이미지를 못 쓸 때의 기본 커서
ROLES = [
    ("arrow", "일반 선택", "default"),
    ("ibeam", "텍스트 선택", "text"),
    ("wait", "사용 중", "wait"),
    ("no", "사용할 수 없음", "not-allowed"),
    ("move", "이동", "move"),
    ("hand", "링크 선택", "pointer"),
]


def build() -> str:
    css, picker, panels = [], [], []
    for sid, sname, sdesc in SCHEMES:
        cards, thumb = [], ""
        for rid, rlabel, fallback in ROLES:
            text = (HERE / "art" / sid / f"{rid}.txt").read_text(encoding="utf-8")
            hx, hy = read_hotspot(text) or (0, 0)
            uri = "data:image/png;base64," + base64.b64encode(txt_to_png(text)).decode()
            rows = [r for r in text.splitlines() if r.strip() and not r.startswith("hotspot")]
            w, h = max(len(r) for r in rows), len(rows)
            css.append(
                f'[data-scheme="{sid}"] .c-{rid},[data-scheme="{sid}"].c-{rid},.card.s-{sid}.c-{rid}'
                f"{{cursor:url({uri}) {hx} {hy},{fallback}}}"
            )
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
        picker.append(f"""
      <button type="button" class="pick c-hand" data-pick="{sid}" aria-pressed="false">
        <span class="thumb" style="background-image:url({thumb})"></span>
        <span class="pick-name">{sname}</span>
      </button>""")
        panels.append(f"""
    <div class="panel" data-panel="{sid}" hidden>
      <div class="desc-row">
        <p class="desc"><b>cursor-playground {sname}</b> — {sdesc}</p>
        <button type="button" class="register c-hand" data-apply="{sid}" data-name="{sname}">이 구성표 적용</button>
      </div>
      <div class="grid">{"".join(cards)}</div>
    </div>""")

    page = (
        (HERE / "preview.tpl.html").read_text(encoding="utf-8")
        .replace("/*CURSOR_CSS*/", "\n".join(css))
        .replace("<!--PICKER-->", "".join(picker))
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


def build_dist() -> int:
    count = 0
    for sid, _, _ in SCHEMES:
        out = HERE / "dist" / sid
        out.mkdir(parents=True, exist_ok=True)
        for rid, _, _ in ROLES:
            text = (HERE / "art" / sid / f"{rid}.txt").read_text(encoding="utf-8")
            (out / f"{rid}.cur").write_bytes(png_to_cur(txt_to_png(text), read_hotspot(text) or (0, 0)))
            count += 1
    return count


if __name__ == "__main__":
    out = HERE / "preview.html"
    out.write_text(build(), encoding="utf-8")
    print(f"{out} 만듦")
    print(f"dist/ 커서 {build_dist()}개 만듦")

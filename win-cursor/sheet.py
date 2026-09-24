# SPDX-License-Identifier: Apache-2.0
"""모양 × 구성표를 PNG 한 장에 늘어놓아 눈으로 견준다. 빌드(2분)를 돌리지 않고 몇 초 만에 본다.

행은 구성표, 열은 모양. 같은 그림을 밝은 바탕과 어두운 바탕에 두 번 놓는다 (어두운 쪽이 오른쪽에
붙는지 아래에 붙는지는 찍히는 안내를 본다) — 네온은 어두운 데서, 잉크는 밝은 데서만 보여서 한쪽만 보면 속는다.

사용법:
  python sheet.py round,bevel pink,ink,chrome      모양 둘 × 구성표 셋
  python sheet.py all pink                         모양 전부 (기본 모양 포함)
  python sheet.py glow electric --frames           열을 모양 대신 프레임으로 (움직임을 볼 때, 모양은 하나만)
  python sheet.py classic pink,ink --roles all     열을 칸 17개로 (구성표 한 벌을 통째로 볼 때)
  --role hand · --size 128 · -o 경로               칸 · 판 크기 · 나갈 자리 (기본은 임시 폴더)

매끈한 모양을 고치다 "그려서 보는" 임시 스크립트를 새로 짜고 싶어지면 이 파일에 옵션을 더한다.
2026-09-19 에 세어 보니 그런 스크립트를 세션마다 39번 다시 짜고 있었다.
"""
import argparse
import ast
import tempfile
import time
from pathlib import Path

import build
import shape as shapelib
import smooth as sm
from make_cur import canvas_size, pixels_to_png

PAD = 6                                              # 그림 둘레 여백. 번짐이 옆 칸에 붙어 보이지 않게
BGS = ((244, 244, 244, 255), (30, 30, 30, 255))      # 밝은 바탕, 어두운 바탕


def pick(arg: str, known: list[str], what: str) -> list[str]:
    ids = known if arg == "all" else arg.split(",")
    bad = [i for i in ids if i not in known]
    if bad:
        raise SystemExit(f"모르는 {what}: {', '.join(bad)} — 있는 것: {', '.join(known)}")
    return ids


def frames_of(shape: str, sid: str, role: str, size: int, cache: dict, mat: str | None = None,
              k: int = 1) -> list[dict]:
    """이 모양·구성표·칸의 프레임별 {좌표: RGBA}. build.py 가 커서를 만들 때와 같은 길을 지난다"""
    if build.shape_of(shape) is None or role in build.KEEP:     # 테마 그림 그대로 쓰는 자리
        raw = build.art_raw(sid, role)
        return sm.tween([sm.scale_up(f, size / canvas_size(raw)) for f in shapelib.read_art(raw)[0]], [1] * k)
    frames, _, glyphs = build.smooth_parts(sid, role, shape, cache)
    return sm.tween(sm.draw(shape, role, sm.samplers_of(frames, mat or build.MAT.get(sid)),
                            sm.cells_for(size), glyphs)[0], [1] * k)


def compose(rows: list[list[dict]], size: int) -> tuple[dict, int, int]:
    """행마다 그림 목록 → (한 장의 {좌표: RGBA}, 폭, 높이)"""
    tile, ncols, nrows = size + 2 * PAD, max(len(r) for r in rows), len(rows)
    # 어두운 바탕을 오른쪽에 붙일지 아래에 붙일지. PNG 가 정사각형으로만 나가므로 긴 변이 짧아지는 쪽을 고른다
    # (모양 11가지 × 구성표 5종을 옆으로 붙였더니 판의 77% 가 빈 자리였다)
    down = max(ncols, 2 * nrows) < max(2 * ncols, nrows)
    bw, bh = ncols * tile, nrows * tile
    w, h = (bw, 2 * bh) if down else (2 * bw, bh)
    out = {(x, y): BGS[(y >= bh) if down else (x >= bw)] for y in range(h) for x in range(w)}
    for ry, row in enumerate(rows):
        for cx, px in enumerate(row):
            for half in (0, 1):
                ox = cx * tile + PAD + (0 if down else half * bw)
                oy = ry * tile + PAD + (half * bh if down else 0)
                for (x, y), c in sm._fit(px, size).items():
                    out[(ox + x, oy + y)] = sm.over(out[(ox + x, oy + y)], c)
    return out, w, h


def main(argv: list[str] | None = None) -> Path:
    ap = argparse.ArgumentParser(description="모양 × 구성표를 한 장에 그린다")
    ap.add_argument("shapes", help="모양 id 를 쉼표로, 또는 all")
    ap.add_argument("schemes", help="구성표 id 를 쉼표로, 또는 all")
    ap.add_argument("--role", default="arrow")
    ap.add_argument("--size", type=int, default=sm.PAGE)
    ap.add_argument("--frames", action="store_true", help="열을 첫 모양의 프레임으로")
    ap.add_argument("--roles", metavar="칸들", help="열을 첫 모양의 칸으로 (쉼표로, 또는 all) — 구성표 한 벌을 통째로 볼 때")
    ap.add_argument("--mat", help="재질을 이 판에서만 이걸로 (metal·glass·glow·cloth·plastic)")
    ap.add_argument("--tween", type=int, default=1, metavar="배수",
                    help="프레임 사이를 섞어 이 배수로 늘려 본다 (--frames 와 같이 쓴다)")
    ap.add_argument("--range", metavar="처음:끝", help="프레임을 이 구간만 (60fps 판은 한 줄이 너무 길다)")
    ap.add_argument("--set", action="append", default=[], metavar="이름=값",
                    help="smooth.py 상수를 이 판에서만 바꾼다 (예: --set PATTERN=0 --set KEEP=40)")
    ap.add_argument("-o", "--out", type=Path, default=Path(tempfile.gettempdir()) / "cursor-sheet.png")
    a = ap.parse_args(argv)

    for one in a.set:                                # 값을 바꿔 두 장 뽑아 견주라고 둔 것
        name, _, val = one.partition("=")
        if not hasattr(sm, name):
            raise SystemExit(f"smooth.py 에 없는 상수: {name}")
        setattr(sm, name, ast.literal_eval(val))
    sm._cache.clear()                                # 스텐실 캐시가 옛 값으로 그린 것을 들고 있다
    sm._BLENDS.clear(); sm._SAME.clear()             # 색 캐시도 마찬가지

    t0 = time.time()
    shapes = pick(a.shapes, [s["id"] for s in build.SHAPES], "모양")
    schemes = pick(a.schemes, [s["id"] for s in build.SCHEMES], "구성표")
    if not (build.HERE / "art" / schemes[0] / f"{a.role}.txt").exists():
        raise SystemExit(f"모르는 칸: {a.role}")
    cache: dict = {}
    if a.frames:
        rows = [frames_of(shapes[0], sid, a.role, a.size, cache, a.mat, a.tween) for sid in schemes]
        if a.range:
            lo, _, hi = a.range.partition(":")
            rows = [r[int(lo or 0):int(hi or len(r))] for r in rows]
        cols = f"{shapes[0]} 의 프레임 (많은 쪽 {max(len(r) for r in rows)}장)"
    elif a.roles:
        roles = pick(a.roles, sorted(p.stem for p in (build.HERE / "art" / schemes[0]).glob("*.txt")), "칸")
        rows = [[frames_of(shapes[0], sid, r, a.size, cache, a.mat)[0] for r in roles] for sid in schemes]
        cols = f"{shapes[0]} 의 칸: {' · '.join(roles)}"
    else:
        rows = [[frames_of(shp, sid, a.role, a.size, cache, a.mat)[0] for shp in shapes] for sid in schemes]
        cols = " · ".join(shapes)

    px, w, h = compose(rows, a.size)
    # pixels_to_png 가 정사각형만 만든다. 긴 변에 맞추고 남는 자리는 투명으로 둔다 —
    # 거슬리면 make_cur 에 높이 인자를 더하면 되는데, 그 파일은 빌드 해시에 들어 있어 고치면 전부 다시 그린다
    a.out.write_bytes(pixels_to_png(px, max(w, h)))
    where = "아래" if h > len(rows) * (a.size + 2 * PAD) else "오른쪽"
    print(f"행(위→아래): {' · '.join(schemes)}\n열(왼→오른): {cols}\n밝은 바탕 다음, 같은 차례로 어두운 바탕이 {where}에")
    print(f"{a.out} · {w}x{h} · {time.time() - t0:.1f}초")
    return a.out


if __name__ == "__main__":
    main()

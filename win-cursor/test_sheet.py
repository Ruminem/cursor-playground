# SPDX-License-Identifier: Apache-2.0
"""sheet.py 가 그림을 제자리에 놓는지 본다. 시트가 어긋나면 눈으로 내린 판단이 통째로 틀린다.

사용법: python test_sheet.py — 몇 초 안에 끝난다.
"""
import struct
import tempfile
from pathlib import Path

import sheet

SIZE = 64
tile = SIZE + 2 * sheet.PAD
shapes, schemes = ["classic", "round"], ["pink", "ink"]

out = sheet.main([",".join(shapes), ",".join(schemes), "--size", str(SIZE),
                  "-o", str(Path(tempfile.gettempdir()) / "test-sheet.png")])
data = out.read_bytes()
assert data[:8] == b"\x89PNG\r\n\x1a\n", "PNG 가 아님"
side = struct.unpack(">II", data[16:24])
assert side == (2 * len(shapes) * tile,) * 2, f"판 크기가 다름: {side}"

# 자리마다 그림이 놓였는지는 PNG 를 풀지 않고 compose 가 낸 칸으로 본다
cache: dict = {}
rows = [[sheet.frames_of(shp, sid, "arrow", SIZE, cache)[0] for shp in shapes] for sid in schemes]
px, w, h = sheet.compose(rows, SIZE)
assert (w, h) == (2 * len(shapes) * tile, len(schemes) * tile)
for ry in range(len(schemes)):
    for cx in range(2 * len(shapes)):                # 밝은 쪽 열들, 이어서 어두운 쪽 열들
        bg = sheet.BGS[cx >= len(shapes)]
        drawn = sum(px[(x, y)] != bg for y in range(ry * tile, (ry + 1) * tile)
                    for x in range(cx * tile, (cx + 1) * tile))
        assert drawn > 50, f"행 {ry} 열 {cx} 에 그림이 없음 (바탕과 다른 칸 {drawn}개)"
    # 여백에는 아무것도 없어야 한다. 있으면 그림이 옆 칸으로 넘친 것
    assert all(px[(x, ry * tile)] in sheet.BGS for x in range(w)), f"행 {ry} 위 여백에 그림이 넘침"

# 같은 그림이 두 바탕에 놓였는지: 불투명한 칸은 바탕과 무관하게 같은 색이어야 한다
art = rows[0][1]
solid = [p for p, c in art.items() if c[3] == 255 and p[0] < SIZE and p[1] < SIZE]
assert solid, "불투명한 칸이 없음"
for x, y in solid[:200]:
    lx, ly = tile + sheet.PAD + x, sheet.PAD + y
    assert px[(lx, ly)] == px[(lx + len(shapes) * tile, ly)] == art[(x, y)], f"두 바탕의 그림이 다름 {(x, y)}"

# 옆으로 길어지면 어두운 바탕을 아래에 붙인다 (정사각형 PNG 의 빈 자리를 줄이려고)
wide, ww, wh = sheet.compose([rows[0] + rows[1]], SIZE)          # 한 행에 넷
assert (ww, wh) == (4 * tile, 2 * tile), f"넓은 판을 아래로 접지 않음: {(ww, wh)}"
assert wide[(0, 0)] == sheet.BGS[0] and wide[(0, tile)] == sheet.BGS[1], "아래쪽이 어두운 바탕이 아님"
assert sum(wide[(x, y)] != sheet.BGS[1] for y in range(tile, 2 * tile) for x in range(3 * tile, ww)) > 50, \
    "어두운 쪽 마지막 열에 그림이 없음"

try:
    sheet.main(["nope", "pink"])
except SystemExit as e:
    assert "nope" in str(e)
else:
    raise AssertionError("모르는 모양을 그냥 넘김")
print("sheet OK — 자리·두 바탕·판 크기·모르는 이름")

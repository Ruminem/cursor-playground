# SPDX-License-Identifier: Apache-2.0
"""shapes/ 의 실루엣에 테마 그림의 색을 옮겨, 같은 테마를 다른 모양으로 만든다.

art/<테마>/<칸>.txt 는 모양과 색을 함께 담는다. 여기서는 색만 빌려 와
shapes/<모양>/<칸>.txt 의 실루엣에 입힌다. 테마는 손대지 않고 모양만 바꾸기 위함이다.

모양 파일은 색이 없다. `#` 은 외곽선(실루엣 가장자리 한 겹), `-` 는 속에 그은 선,
`o` 는 속, `.` 는 빈칸. 외곽선과 속의 선에는 테마의 외곽선 색을, 속에는 테마 속의
같은 자리 색을 넣는다. 몸 바깥으로 번지는 빛(네온·야광)은 층마다 다시 둘러 준다.
"""
from collections import Counter

from make_cur import is_row, read_hotspot, read_palette, read_rate, split_frames

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = N4 + ((1, 1), (-1, -1), (1, -1), (-1, 1))
# 한 파일에 색이 많아질 수 있어 영숫자 뒤에 한글 음절까지 글자로 쓴다 (make_cur 는 글자 하나면 된다)
POOL = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "".join(chr(c) for c in range(0xAC00, 0xAC00 + 2000))
HALO = 3  # 몸 바깥으로 다시 둘러 줄 층 수


def read_art(text: str) -> tuple[list[dict], tuple[int, int], int]:
    """테마 그림 txt → (프레임별 {좌표: RGBA}, 핫스팟, rate)"""
    pal = read_palette(text)
    frames = []
    for f in split_frames(text):
        rows = [l for l in f.splitlines() if is_row(l)]
        frames.append({(x, y): pal[c] for y, r in enumerate(rows) for x, c in enumerate(r) if c != "." and pal[c][3] > 0})
    return frames, read_hotspot(text) or (0, 0), read_rate(text)


def read_mask(text: str) -> tuple[set, set, tuple[int, int]]:
    """모양 txt → (실루엣 전체, 속에 그은 선, 핫스팟)"""
    rows = [l for l in text.splitlines() if not l.startswith("hotspot")]
    mask = {(x, y) for y, r in enumerate(rows) for x, c in enumerate(r) if c != "."}
    inner = {(x, y) for y, r in enumerate(rows) for x, c in enumerate(r) if c == "-"}
    return mask, inner, read_hotspot(text) or (0, 0)


def to_text(frames: list[dict], hot: tuple[int, int], rate: int) -> str:
    """{좌표: RGBA} 프레임들 → art txt (make_cur 가 읽는 형식)"""
    allp = [p for f in frames for p in f]
    minx = min(x for x, _ in allp); miny = min(y for _, y in allp)
    maxx = max(x for x, _ in allp); maxy = max(y for _, y in allp)
    if maxx - minx >= 32 or maxy - miny >= 32:
        raise SystemExit(f"32칸을 넘음: {maxx - minx + 1}x{maxy - miny + 1}")
    colors = sorted({c for f in frames for c in f.values()})
    if len(colors) > len(POOL):
        raise SystemExit(f"색이 너무 많음: {len(colors)}")
    code = {c: POOL[i] for i, c in enumerate(colors)}
    lines = [f"hotspot {hot[0] - minx},{hot[1] - miny}"]
    if len(frames) > 1:
        lines.append(f"rate {rate}")
    lines += [f"color {code[c]} {bytes(c).hex()}" for c in colors]
    for f in frames:
        if len(frames) > 1:
            lines.append("frame")
        for y in range(miny, maxy + 1):
            lines.append("".join(code[f[(x, y)]] if (x, y) in f else "." for x in range(minx, maxx + 1)).rstrip(".") or ".")
    return "\n".join(lines) + "\n"


def bbox(points) -> tuple[int, int, int, int]:
    xs = [x for x, _ in points]; ys = [y for _, y in points]
    return min(xs), min(ys), max(xs), max(ys)


def border(mask: set) -> set:
    return {p for p in mask if any((p[0] + dx, p[1] + dy) not in mask for dx, dy in N4)}


def ring(mask) -> set:
    return {(x + dx, y + dy) for (x, y) in mask for dx, dy in N8} - set(mask)


def nearest(points: set, box: tuple[int, int, int, int]) -> dict:
    """box 안 모든 칸에서 가장 가까운 points 원소 (가장자리에서 안쪽으로 번져 나가며 찾는다)"""
    x0, y0, x1, y1 = box
    best = {p: p for p in points}
    frontier = list(points)
    while frontier:
        nxt = []
        for p in frontier:
            for dx, dy in N8:
                q = (p[0] + dx, p[1] + dy)
                if x0 - 1 <= q[0] <= x1 + 1 and y0 - 1 <= q[1] <= y1 + 1 and q not in best:
                    best[q] = best[p]
                    nxt.append(q)
        frontier = nxt
    return best


def reshape(frames: list[dict], mask: set, inner: set) -> list[dict]:
    """테마 프레임들의 색을 새 실루엣에 옮긴다"""
    edge = border(mask)
    nx0, ny0, nx1, ny1 = bbox(mask)
    halo = []
    grown = set(mask)
    for _ in range(HALO):
        r = ring(grown)
        halo.append(r)
        grown |= r
    out = []
    for frame in frames:
        solid = {p for p, c in frame.items() if c[3] >= 200} or set(frame)
        line = Counter(frame[p] for p in border(solid)).most_common(1)[0][0]
        fill = solid - border(solid) or solid
        sx0, sy0, sx1, sy1 = bbox(solid)
        near = nearest(fill, (sx0, sy0, sx1, sy1))
        px = {}
        for (x, y) in mask:
            if (x, y) in edge or (x, y) in inner:
                px[(x, y)] = line
                continue
            u = (x - nx0) / max(1, nx1 - nx0)
            v = (y - ny0) / max(1, ny1 - ny0)
            px[(x, y)] = frame[near[(round(sx0 + u * (sx1 - sx0)), round(sy0 + v * (sy1 - sy0)))]]
        # 몸 바깥 번짐: 원래 그림의 층별로 가장 흔한 색을 새 실루엣 둘레에 다시 두른다
        grown_src = set(solid)
        for layer in halo:
            r = ring(grown_src)
            grown_src |= r
            got = [frame[p] for p in r if p in frame]
            if got and len(got) * 2 >= len(r):  # 그 층이 반 넘게 차 있을 때만 번짐으로 본다
                col = Counter(got).most_common(1)[0][0]
                for p in layer:
                    px.setdefault(p, col)
        out.append(px)
    return out


def glyph_of(base: list[dict], over: list[dict]) -> list[dict]:
    """화살표에 기호를 얹어 만든 칸에서 기호만 떼어 낸다 (도움말·백그라운드 작업 등)"""
    return [{p: c for p, c in o.items() if b.get(p) != c} for b, o in zip(base, over)]


def place(glyphs: list[dict], old: tuple[int, int, int, int], new: tuple[int, int, int, int]) -> list[dict]:
    """기호를 원래 화살표에서와 같은 자리(비율)에 맞춰 새 화살표 옆으로 옮긴다"""
    marks = [p for g in glyphs for p in g]
    if not marks:
        return glyphs
    gx, gy = bbox(marks)[:2]
    ox0, oy0, ox1, oy1 = old
    nx0, ny0, nx1, ny1 = new
    dx = nx0 + round((gx - ox0) * (nx1 - nx0) / max(1, ox1 - ox0)) - gx
    dy = ny0 + round((gy - oy0) * (ny1 - ny0) / max(1, oy1 - oy0)) - gy
    return [{(x + dx, y + dy): c for (x, y), c in g.items()} for g in glyphs]

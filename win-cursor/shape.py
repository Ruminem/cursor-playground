# SPDX-License-Identifier: Apache-2.0
"""테마 그림 txt 를 픽셀로 읽고 다시 txt 로 쓰는 일, 그리고 화살표에 얹힌 기호를 떼어 옮기는 일.

art/<테마>/<칸>.txt 는 모양과 색을 함께 담는다. 모양을 바꿀 때는 smooth.py 가 그린 새 그림에
이 테마의 색을 입히고, 도움말·백그라운드 작업처럼 화살표에 기호를 얹어 만든 칸은 그 기호만
떼어 새 화살표 옆으로 옮긴다.
"""

from make_cur import is_row, read_hotspot, read_palette, read_rate, split_frames

# 한 파일에 색이 많아질 수 있어 영숫자 뒤에 한글 음절까지 글자로 쓴다 (make_cur 는 글자 하나면 된다)
POOL = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "".join(chr(c) for c in range(0xAC00, 0xD7A4))


def read_art(text: str) -> tuple[list[dict], tuple[int, int], int]:
    """테마 그림 txt → (프레임별 {좌표: RGBA}, 핫스팟, rate)"""
    pal = read_palette(text)
    frames = []
    for f in split_frames(text):
        rows = [l for l in f.splitlines() if is_row(l)]
        frames.append({(x, y): pal[c] for y, r in enumerate(rows) for x, c in enumerate(r) if c != "." and pal[c][3] > 0})
    return frames, read_hotspot(text) or (0, 0), read_rate(text)


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

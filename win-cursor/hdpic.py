# SPDX-License-Identifier: Apache-2.0
"""그림 결 — agy 가 그린 포즈 PNG(pic/<구성표>/)를 칸마다 깔고, 커서 기호는 hd.py 거리함수로 그려 끼운다.

칸 하나 = 포즈 원본(뒤) → 기호(hd 칸 그림을 줄여 기호 자리에) → 앞발 층(<포즈>_paw<n>.png, 앞).
무엇을 어디에 얼마나 크게, 개가 어떻게 움직이는지는 pic/<구성표>/cells.json 이 정한다:
  frames, rate         움직이는 칸 한 바퀴 장 수 · 장마다 1/60초 틱
  cells.<칸>.pose      포즈 이름(pic/<구성표>/<pose>.png)
  cells.<칸>.el        hd 칸 이름(그 칸 그림을 기호로 씀), null 이면 기호 없음 — 그러면 hot 이 핫스팟(point 의 앞발 끝)
  cells.<칸>.at        기호의 핫스팟을 둘 자리(256px). 커서 핫스팟도 여기다 — 기호와 핫스팟은 장마다 그대로고 개만 움직인다
  cells.<칸>.scale     hd 칸 그림 배율(1 이면 hd 화살표 그대로, 22칸 ≈ 176px)
  cells.<칸>.rot       기호를 핫스팟 축으로 돌리는 각(도, 시계 방향)
  cells.<칸>.move      개의 움직임: breathe(숨) · bob(통통) · sway(갸웃) · none
기호가 도는 칸(busy · wait)은 move 가 none 이어도 움직인다(hd 의 스피너가 frame 을 받는다).

hd.render · hd.frames · hd.animated · hdpet.hot 을 감싼다 — 그림 결이 아니면 원래 함수를 그대로 불러 바이트가 같다.
일감 해시에는 그림 결 구성표만 이 파일과 pic/<구성표>/ 가 든다(build._hashes). 윈도우 워커는 spawn 이라 build.py 가
모듈 머리에서 읽어야 워커에도 등록된다. 그림 결은 classic_only · 색조 막대 하나다(화살표 표식을 안 박는다).

  python hdpic.py <폴더> [구성표]     칸 17개 × (256 · 64 · 32) 시트를 sheet_<구성표>.png 로
"""
import json
import math
import struct
import zlib
from pathlib import Path

import hd
import hdpet
import hdmini  # noqa: F401 — 감싸는 차례를 정한다(hdpet → hdshape → hdmini → 여기)

HERE = Path(__file__).resolve().parent
N, U = hd.N, hd.U
PICS = {}
_render, _frames, _animated, _hot = hd.render, hd.frames, hd.animated, hdpet.hot
INK = (76 / 255, 22 / 255, 4 / 255)               # 시바 먹선(hug.png 의 가장 짙은 칸들, 2026-10-18 잼)


def read_png(path):
    """8비트 RGBA · 겹짜기 없는 PNG → 미리 곱한 0–1 판 넷. 필터 다섯 가지를 다 푼다(Pillow 가 행마다 고른다)"""
    raw = Path(path).read_bytes()
    pos, idat = 8, b""
    while pos < len(raw):
        n, kind = struct.unpack(">I4s", raw[pos:pos + 8])
        body = raw[pos + 8:pos + 8 + n]
        if kind == b"IHDR":
            w, h, depth, ctype, _, _, lace = struct.unpack(">IIBBBBB", body)
            assert (depth, ctype, lace) == (8, 6, 0), f"{path}: 8비트 RGBA 겹짜기 없음만 읽음"
        elif kind == b"IDAT":
            idat += body
        pos += 12 + n
    data, stride = zlib.decompress(idat), w * 4
    prev, rows = bytearray(stride), []
    for y in range(h):
        f, line = data[y * (stride + 1)], bytearray(data[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - 4] if i >= 4 else 0
            b, c = prev[i], (prev[i - 4] if i >= 4 else 0)
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(line)
        prev = line
    assert (w, h) == (N, N), f"{path}: {N}×{N} 만 받음"
    R, G, B, A = ([0.0] * (N * N) for _ in range(4))
    for y, line in enumerate(rows):
        for x in range(N):
            r, g, b, a = line[x * 4:x * 4 + 4]
            if a:
                i, k = y * N + x, a / 255 / 255
                R[i], G[i], B[i], A[i] = r * k, g * k, b * k, a / 255
    return R, G, B, A


class Pic:
    """그림 결 하나. 판은 처음 쓸 때 읽는다(워커마다 한 번)"""

    shadow = (0.0, 0.0, 0.0, 0.0)                 # 포즈 그림에 그림자가 없어 기호에도 안 깐다
    ink = INK

    def __init__(self, sid):
        self.dir = HERE / "pic" / sid
        cfg = json.loads((self.dir / "cells.json").read_text(encoding="utf-8"))
        self.NF, self.RATE, self.cells = cfg["frames"], cfg["rate"], cfg["cells"]
        self._img = {}

    def img(self, name):
        if name not in self._img:
            self._img[name] = read_png(self.dir / f"{name}.png")
        return self._img[name]

    def paws(self, pose):
        return sorted(p.stem for p in self.dir.glob(f"{pose}_paw*.png"))

    def body(self, x, y, e, nx, ny, warn, frame):
        """스티커 칠: 먹선 한 겹(0.5칸) · 오른쪽 아래 그늘 한 단 · 바탕은 흰색(금지는 빨강)"""
        if e > -0.5:
            return INK, 1.0
        if warn:
            return ((0.80, 0.26, 0.24) if nx * 0.6 + ny * 0.8 > 0.35 and e > -1.4 else (0.95, 0.38, 0.33)), 1.0
        if nx * 0.6 + ny * 0.8 > 0.35 and e > -1.4:
            return (0.84, 0.86, 0.93), 1.0
        return (1.0, 0.99, 0.97), 1.0

    def animated(self, name):
        c = self.cells[name]
        return c.get("move", "none") != "none" or c.get("el") in ("busy", "wait")


def register(sid):
    PICS[sid] = hd.STYLES[sid] = Pic(sid)


def _placed(c):
    """hd 칸 그림을 기호 자리에 놓는 cell 갈음 — 핫스팟 축으로 scale 배 · rot 도"""
    s, ang = c.get("scale", 1.0), math.radians(c.get("rot", 0.0))
    ax, ay = c["at"][0] / U, c["at"][1] / U
    co, si = math.cos(ang), math.sin(ang)
    orig = hd._cell

    def cell(name, frame=0.0, soft=0.0, tip_body=False):
        layers, (hx, hy) = orig(c["el"], frame)

        def src(x, y):
            dx, dy = (x - ax) / s, (y - ay) / s
            return hx + dx * co + dy * si, hy - dx * si + dy * co
        for L in layers:
            L["f"] = (lambda f: lambda x, y: s * f(*src(x, y)))(L["f"])        # 거리는 배율만큼 늘린다
            if "fade" in L:
                L["fade"] = (lambda f: lambda x, y: f(*src(x, y)))(L["fade"])   # 비율이라 그대로
        return layers, (ax, ay)
    return cell


def _motion(move, t, box):
    """개 판을 장 t(0–1)에 어떻게 옮기나 → 화면 자리 (x, y) 에 보일 원본 자리를 돌려주는 함수. 발 가운데가 축"""
    x0, y0, x1, y1 = box
    px, py = (x0 + x1) / 2, y1
    w = math.sin(math.tau * t)
    if move == "breathe":                         # 숨 — 세로로 2% 부풀고 가로로 1% 좁아짐
        sx, sy, ang, dy = 1 - 0.01 * w, 1 + 0.02 * w, 0.0, 0.0
    elif move == "bob":                           # 통통 — 3px 뜨고 내려앉을 때 살짝 눌림
        up = 0.5 - 0.5 * math.cos(math.tau * t)
        sx, sy, ang, dy = 1 + 0.015 * (1 - up), 1 - 0.015 * (1 - up), 0.0, -3.0 * up
    elif move == "sway":                          # 갸웃 — 발을 축으로 ±2°
        sx = sy = 1.0
        ang, dy = math.radians(2.0) * w, 0.0
    else:
        return None
    co, si = math.cos(ang), math.sin(ang)

    def src(x, y):
        dx, dy_ = x - px, y - py - dy
        rx, ry = dx * co + dy_ * si, -dx * si + dy_ * co
        return px + rx / sx, py + ry / sy
    return src


def _box(A):
    ys = [i // N for i in range(N * N) if A[i] > 0]
    xs = [i % N for i in range(N * N) if A[i] > 0]
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def _over(dst, img, src, box):
    """img 를 src 로 옮겨 dst 위에 덮는다(미리 곱한 값, 쌍선형). box 밖 여유 6px 안만 돈다 — 움직임이 3px 안팎이라"""
    R, G, B, A = img
    DR, DG, DB, DA = dst
    x0, y0, x1, y1 = box
    for y in range(max(0, y0 - 6), min(N, y1 + 6)):
        for x in range(max(0, x0 - 6), min(N, x1 + 6)):
            if src is None:
                i = y * N + x
                a = A[i]
                if a <= 0:
                    continue
                r, g, b = R[i], G[i], B[i]
            else:
                sx, sy = src(x + 0.5, y + 0.5)
                sx, sy = sx - 0.5, sy - 0.5
                ix, iy = math.floor(sx), math.floor(sy)
                fx, fy = sx - ix, sy - iy
                r = g = b = a = 0.0
                for jx, jy, wt in ((ix, iy, (1 - fx) * (1 - fy)), (ix + 1, iy, fx * (1 - fy)),
                                   (ix, iy + 1, (1 - fx) * fy), (ix + 1, iy + 1, fx * fy)):
                    if 0 <= jx < N and 0 <= jy < N and wt > 0:
                        j = jy * N + jx
                        if A[j] > 0:
                            r += R[j] * wt
                            g += G[j] * wt
                            b += B[j] * wt
                            a += A[j] * wt
                if a <= 0.001:
                    continue
            i = y * N + x
            k = 1 - a
            DR[i] = r + DR[i] * k
            DG[i] = g + DG[i] * k
            DB[i] = b + DB[i] * k
            DA[i] = a + DA[i] * k


def _pic_render(sid, name, frame):
    pic = PICS[sid]
    c = pic.cells[name]
    back = pic.img(c["pose"])
    box = _box(back[3])
    src = _motion(c.get("move", "none"), frame, box)
    out = tuple([0.0] * (N * N) for _ in range(4))
    _over(out, back, src, box)
    if c.get("el"):
        keep, hd.cell = hd.cell, _placed(c)
        try:
            el, hot = _render(sid, name, frame)
        finally:
            hd.cell = keep
        _over(out, el, None, (0, 0, N, N))
    else:
        hot = (round(c["hot"][0]), round(c["hot"][1]))
    for paw in pic.paws(c["pose"]):
        _over(out, pic.img(paw), src, box)
    return out, hot


def render(style, name, frame=0.0):
    if style in PICS:
        return _pic_render(style, name, frame)
    return _render(style, name, frame)


def frames(style, name):
    pic = PICS.get(style)
    if pic is None:
        return _frames(style, name)
    return (pic.NF, pic.RATE) if pic.animated(name) else (1, pic.RATE)


def animated(style, name):
    pic = PICS.get(style)
    return pic.animated(name) if pic else _animated(style, name)


def hot(style, name):
    pic = PICS.get(style)
    if pic is None:
        return _hot(style, name)
    c = pic.cells[name]
    x, y = c["at"] if c.get("el") else c["hot"]
    return x / U, y / U


hd.render, hd.frames, hd.animated, hdpet.hot = render, frames, animated, hot

for _d in sorted((HERE / "pic").iterdir()) if (HERE / "pic").is_dir() else []:
    if (_d / "cells.json").exists():
        register(_d.name)


def sheet(out, sid):
    """칸 17개를 여섯 줄로: 칸마다 256 판(첫 장) 밑에 64 · 32 실물(첫 장 · 사분 장). 바탕은 연회색, 핫스팟은 빨간 점"""
    tiles = []
    for name in hd.CELLS:
        n = frames(sid, name)[0]
        tile = []
        for k in sorted({0, n // 4}):
            img, (hx, hy) = render(sid, name, k / n)
            for s in ((N, 64, 32) if k == 0 else (32,)):
                small = img if s == N else hd.shrink(img, s)
                px = bytearray(hd.rgba_bytes(small, s))
                i = ((hy * s // N) * s + hx * s // N) * 4
                px[i:i + 4] = b"\xff\x00\x00\xff"
                tile.append((s, bytes(px)))
        tiles.append(tile)
    COLS, TW, TH = 6, N + 8, N + 64 + 16
    W, H = COLS * TW + 8, -(-len(tiles) // COLS) * TH + 8
    can = bytearray(b"\xdd\xdd\xdd" * (W * H))
    for t, tile in enumerate(tiles):
        bx, by = 8 + t % COLS * TW, 8 + t // COLS * TH
        spots = [(bx, by), (bx, by + N + 8), (bx + 72, by + N + 8), (bx + 112, by + N + 8)]
        for (x, y), (s, px) in zip(spots, tile):
            for j in range(s):
                for i in range(s):
                    r, g, b, a = px[(j * s + i) * 4:(j * s + i) * 4 + 4]
                    o = ((y + j) * W + x + i) * 3
                    can[o:o + 3] = bytes(round(v * a / 255 + 0xdd * (1 - a / 255)) for v in (r, g, b))
    Path(out).mkdir(parents=True, exist_ok=True)
    path = Path(out) / f"sheet_{sid}.png"
    path.write_bytes(hd.png(bytes(can), W, H, channels=3))
    return path


if __name__ == "__main__":
    import sys
    for s in sys.argv[2:] or list(PICS):
        print(sheet(sys.argv[1], s))

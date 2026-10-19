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
  cells.<칸>.grip      앞발 층이 화살표 테두리를 잡는 칸 — 모양 탭에서 그 모양 화살표의 배율 · 자리를 앞발에 맞춰 옮긴다(_fit)
  cells.<칸>.shapes    grip 칸의 모양별 포즈 {모양: {pose, scale, at}} — 그 모양을 잡고 그린 포즈가 있으면 _fit 대신 이 값(agy 안내 그림 자리).
                       "front": true 면 포즈를 기호 위에 통째로 얹는다 — 앱이 마젠타 위에 개를 그린 그대로라 앞 층이 필요 없다
  cells.<칸>.flip      포즈를 몸 상자 안에서 좌우로 뒤집음
  cells.<칸>.move      개의 움직임: breathe(숨) · bob(통통) · sway(갸웃) · none
  cells.<칸>.frames · rate   그 칸만 장 수 · 틱을 따로(도는 기호는 12fps 면 끊겨 보여 40장 × 2틱)
기호가 도는 칸(busy · wait)은 move 가 none 이어도 움직인다(hd 의 스피너가 frame 을 받는다).

hd.render · hd.frames · hd.animated · hdpet.hot 을 감싼다 — 그림 결이 아니면 원래 함수를 그대로 불러 바이트가 같다.
일감 해시에는 그림 결 구성표만 이 파일과 pic/<구성표>/ 가 든다(build._hashes). 윈도우 워커는 spawn 이라 build.py 가
모듈 머리에서 읽어야 워커에도 등록된다.
기호가 커서다(cursor) — 기호 몫 다섯째 판을 같이 겹쳐 hdpet.rgba_bytes 가 표식을 박고, 색조 막대가 둘(개 · 기호)이다.
"<결>@<모양>" 은 모양 탭 — 기호를 그리는 동안 hd 화살표 몸 · 끝을 hdshape.geom 의 것으로 갈아 끼운다(스티커는 흰 띠).
화살표가 든 칸(ARROWED)만 모양 폴더에 굽는다(hdmini.shaped_cells 를 감쌈).

  python hdpic.py <폴더> [구성표]     칸 17개 × (256 · 64 · 32) 시트를 sheet_<구성표>.png 로
"""
import json
import math
import struct
import zlib
from pathlib import Path

import hd
import hdpet
import hdmini  # 감싸는 차례를 정한다(hdpet → hdshape → hdmini → 여기)
import hdshape

HERE = Path(__file__).resolve().parent
N, U = hd.N, hd.U
PICS = {}
_render, _frames, _animated, _hot = hd.render, hd.frames, hd.animated, hdpet.hot
INK = (76 / 255, 22 / 255, 4 / 255)               # 시바 먹선(hug.png 의 가장 짙은 칸들, 2026-10-18 잼)
ARROWED = {"arrow", "help", "busy", "pin", "person"}   # hd._cell 이 화살표(A)를 까는 칸 — 모양 탭이 바꾸는 칸


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
    cursor = True

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

    def frames(self, name):
        c = self.cells[name]
        return (c.get("frames", self.NF), c.get("rate", self.RATE)) if self.animated(name) else (1, self.RATE)


def register(sid):
    PICS[sid] = hd.STYLES[sid] = Pic(sid)


def _shaped(el, frame, shape):
    """hd._cell 그대로, 모양이면 화살표 몸 · 끝(arrow · TIP 은 부를 때 찾는 이름이다)을 그 모양 것으로. 스티커는 흰 띠를 밑에"""
    if not shape:
        return hd._cell(el, frame)
    g = hdshape.geom(shape)
    keep = hd.arrow, hd.TIP
    hd.arrow, hd.TIP = (lambda: g["body"]), g["hot"]
    try:
        layers, hot = hd._cell(el, frame)
    finally:
        hd.arrow, hd.TIP = keep
    if g["band"]:
        layers = [dict(f=hd.grow(g["body"], g["band"]), paint=lambda x, y, e, nx, ny, f: (hdshape.BAND, 1.0), noglow=True)
                  ] + layers
    return layers, hot


def _placed(c, shape=None):
    """hd 칸 그림을 기호 자리에 놓는 cell 갈음 — 핫스팟 축으로 scale 배 · rot 도"""
    s, ang = c.get("scale", 1.0), math.radians(c.get("rot", 0.0))
    ax, ay = c["at"][0] / U, c["at"][1] / U
    co, si = math.cos(ang), math.sin(ang)

    def cell(name, frame=0.0, soft=0.0, tip_body=False):
        layers, (hx, hy) = _shaped(c["el"], frame, shape)

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


def _over(dst, img, src, box, cur=False):
    """img 를 src 로 옮겨 dst 위에 덮는다(미리 곱한 값, 쌍선형). box 밖 여유 6px 안만 돈다 — 움직임이 3px 안팎이라.
    dst 다섯째 판은 커서 몫 — cur 면 덮은 알파만큼 1, 아니면 0 으로 덮는다"""
    R, G, B, A = img
    DR, DG, DB, DA, DC = dst
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
            DC[i] = (a if cur else 0.0) + DC[i] * k


def _edge(shape, at, s):
    """기호 화살표 몸(스티커는 띠 바깥)의 거리함수를 256 판 px 로 — _placed 와 같은 놓기"""
    if shape:
        g = hdshape.geom(shape)
        body, (hx, hy) = hd.grow(g["body"], g["band"]), g["hot"]
    else:
        body, (hx, hy) = hd.arrow(), hd.TIP
    k = s * U
    return lambda x, y: k * body(hx + (x - at[0]) / k, hy + (y - at[1]) / k)


_FIT = {}


def _fit(sid, name, shape):
    """앞발이 화살표를 잡는 칸(cells.json "grip")의 모양 탭 — 앞발 층 무게중심마다 기본 화살표 테두리까지의 거리 · 방향을
    재고, 그 모양 화살표가 같은 거리 · 방향이 되는 배율 · 끝 자리를 찾는다. 돌리지 않고, 판 4px 안을 넘는 자리는 버린다.
    ponytail: 격자 찾기(배율 16 × 자리 25² 뒤 ±3px 다듬기)라 모양마다 몇 초 — 느리면 cells.json 에 값을 박는다"""
    c = PICS[sid].cells[name]
    if not (shape and c.get("grip")):
        return c
    if shape in c.get("shapes", {}):
        return dict(c, **c["shapes"][shape])
    key = (sid, name, shape)
    if key in _FIT:
        return _FIT[key]
    pic, s0, at0 = PICS[sid], c.get("scale", 1.0), c["at"]
    pts = []
    for paw in pic.paws(c["pose"]):
        A = pic.img(paw)[3]
        w = sum(A)
        pts.append((sum(a * (i % N) for i, a in enumerate(A)) / w, sum(a * (i // N) for i, a in enumerate(A)) / w))

    def look(f):
        out = []
        for x, y in pts:
            gx, gy = f(x + 1, y) - f(x - 1, y), f(x, y + 1) - f(x, y - 1)
            n = math.hypot(gx, gy) or 1.0
            out.append((f(x, y), gx / n, gy / n))
        return out
    want = look(_edge(None, at0, s0))

    def cost(s, at):
        e = 4.0 * (1 - s / s0) ** 2 * 100 + 0.002 * ((at[0] - at0[0]) ** 2 + (at[1] - at0[1]) ** 2)
        for (d, nx, ny), (d0, nx0, ny0) in zip(look(_edge(shape, at, s)), want):
            e += (d - d0) ** 2 + 100 * (1 - nx * nx0 - ny * ny0)
        return e

    def inside(s, at):
        f = _edge(shape, at, s)
        return all(f(x, y) > 0 for t in range(0, 249, 4) for x, y in ((4, 4 + t), (252, 4 + t), (4 + t, 4), (4 + t, 252)))
    cands = sorted((cost(s0 * (0.70 + 0.02 * i), (at0[0] + dx, at0[1] + dy)), s0 * (0.70 + 0.02 * i), (at0[0] + dx, at0[1] + dy))
                   for i in range(16) for dx in range(-48, 49, 4) for dy in range(-48, 49, 4))
    _, s, at = next(x for x in cands if inside(x[1], x[2]))
    _, s, at = min((cost(s, (at[0] + dx, at[1] + dy)), s, (at[0] + dx, at[1] + dy))
                   for dx in range(-3, 4) for dy in range(-3, 4) if inside(s, (at[0] + dx, at[1] + dy)))
    _FIT[key] = dict(c, scale=s, at=[at[0], at[1]])
    return _FIT[key]


def _pic_render(sid, shape, name, frame):
    pic = PICS[sid]
    c = _fit(sid, name, shape)
    back = pic.img(c["pose"])
    box = _box(back[3])
    src = _motion(c.get("move", "none"), frame, box)
    flip = c.get("flip")
    if flip:
        back = _flip(back, box)
    out = tuple([0.0] * (N * N) for _ in range(5))
    if not c.get("front"):
        _over(out, back, src, box)
    if c.get("el"):
        keep, hd.cell = hd.cell, _placed(c, shape)
        try:
            el, hot = _render(sid, name, frame)
        finally:
            hd.cell = keep
        _over(out, el, None, (0, 0, N, N), cur=True)
    else:
        hot = (round(c["hot"][0]), round(c["hot"][1]))
    if c.get("front"):
        _over(out, back, src, box)
    for paw in pic.paws(c["pose"]):
        _over(out, _flip(pic.img(paw), box) if flip else pic.img(paw), src, box)
    return out, hot


def _flip(img, box):
    """포즈를 몸 상자 안에서 좌우로 뒤집는다 — 개가 제자리에서 반대쪽을 본다(cells.json "flip")"""
    x0, _, x1, _ = box
    out = tuple(list(p) for p in img)
    for p, q in zip(img, out):
        for y in range(N):
            q[y * N + x0:y * N + x1] = p[y * N + x0:y * N + x1][::-1]
    return out


def _split(style):
    sid, _, shape = style.partition("@")
    return (sid, shape or None) if sid in PICS else (None, None)


def render(style, name, frame=0.0):
    sid, shape = _split(style)
    if sid:
        return _pic_render(sid, shape, name, frame)
    return _render(style, name, frame)


def frames(style, name):
    sid = _split(style)[0]
    return PICS[sid].frames(name) if sid else _frames(style, name)


def animated(style, name):
    sid = _split(style)[0]
    return PICS[sid].animated(name) if sid else _animated(style, name)


def hot(style, name):
    """칸 단위 핫스팟 — 기호 자리(at). 모양 화살표 끝을 그 자리에 놓으므로 모양이 달라도 같다(grip 칸만 _fit 이 옮긴다)"""
    sid, shape = _split(style)
    if sid is None:
        return _hot(style, name)
    c = _fit(sid, name, shape)
    x, y = c["at"] if c.get("el") else c["hot"]
    return x / U, y / U


_shaped_cells = hdmini.shaped_cells


def shaped_cells(style):
    sid, shape = _split(style)
    if sid is None:
        return _shaped_cells(style)
    return sorted(n for n, c in PICS[sid].cells.items() if c.get("el") in ARROWED) if shape else ["arrow"]


hd.render, hd.frames, hd.animated, hdpet.hot, hdmini.shaped_cells = render, frames, animated, hot, shaped_cells

for _d in sorted((HERE / "pic").iterdir()) if (HERE / "pic").is_dir() else []:
    if (_d / "cells.json").exists():
        register(_d.name)


def sheet(out, sid):
    """sid 는 "<결>" 또는 "<결>@<모양>"(모양 폴더에 굽는 칸만). 칸 17개를 여섯 줄로: 칸마다 256 판(첫 장) 밑에 64 · 32 실물(첫 장 · 사분 장). 바탕은 연회색, 핫스팟은 빨간 점"""
    tiles = []
    for name in hd.CELLS if "@" not in sid else shaped_cells(sid):
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
    path = Path(out) / f"sheet_{sid.replace('@', '_')}.png"
    path.write_bytes(hd.png(bytes(can), W, H, channels=3))
    return path


if __name__ == "__main__":
    import sys
    for s in sys.argv[2:] or list(PICS):
        print(sheet(sys.argv[1], s))

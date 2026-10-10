# SPDX-License-Identifier: Apache-2.0
"""고화질 구성표 3종 — 글래스 · 오로라 네온 · 크롬 메탈 — 생성기.

픽셀 그림(.txt)이 아니라 거리함수로 256칸 판에 바로 그린다. .txt 는 글자 하나가 색 하나라
그라데이션·하이라이트처럼 색이 수천 개인 그림을 못 담고, 기본 모양은 그 그림을 최근접으로 키워
32 위로는 계단이 그대로 커진다. 여기서는 256 원본을 그리고 크기마다 면적 평균으로 줄인다.

모양은 32칸 판의 한 칸(U = 8px)을 단위로 적는다 — 다른 구성표 그림과 같은 자리·크기 감각.
재질(Glass·Aurora·Chrome)은 거리 d 와 테두리 법선으로 칠한다: 테두리 쪽 밝기·안쪽 테·바깥 번짐.

    python gen/hd.py <출력 폴더> [재질…]        # 256 PNG 와 견줘 볼 시트

지금은 시안 단계라 art/ 에 쓰지 않는다. 고른 뒤 빌드 길과 같이 넣는다.
2026-10-10 보류 — 매끈한 모양 대응(classic_only 로 빌릴지, 모양마다 다시 그릴지)을 정하기 전. NEXT.md 참고.
시안 페이지: https://claude.ai/artifact/WToSbg2DiN2QL76z6SQ2or (gen/hd_preview.py 로 다시 뽑음)
"""
import math
import os
import struct
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor

N = 256           # 원본 판
U = N / 32        # 32칸 판의 한 칸 = 8px
TAU = 2 * math.pi
M = 3.5           # 모양 밖으로 칠할 수 있는 거리(그림자·번짐), 칸 단위
hypot, exp, sin, cos, atan2 = math.hypot, math.exp, math.sin, math.cos, math.atan2


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def smooth(a, b, v):
    t = clamp((v - a) / (b - a))
    return t * t * (3 - 2 * t)


def lerp(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, p[2] + (q[2] - p[2]) * t)


# ---- 거리함수: 안이 음수 ----

def poly(pts):
    E = []
    for i in range(len(pts)):
        ax, ay = pts[i]
        bx, by = pts[i - 1]
        ex, ey = bx - ax, by - ay
        E.append((ax, ay, ex, ey, ex * ex + ey * ey, by))

    def f(x, y):
        d, s = 1e18, 1.0
        for ax, ay, ex, ey, ee, by in E:
            wx, wy = x - ax, y - ay
            t = (wx * ex + wy * ey) / ee
            t = 0.0 if t < 0 else 1.0 if t > 1 else t
            qx, qy = wx - ex * t, wy - ey * t
            q = qx * qx + qy * qy
            if q < d:
                d = q
            c1, c2, c3 = y >= ay, y < by, ex * wy > ey * wx
            if (c1 and c2 and c3) or not (c1 or c2 or c3):
                s = -s
        return s * math.sqrt(d)
    return f


def circle(cx, cy, r):
    return lambda x, y: hypot(x - cx, y - cy) - r


def capsule(ax, ay, bx, by, r):
    ex, ey = bx - ax, by - ay
    ee = ex * ex + ey * ey or 1e-9

    def f(x, y):
        wx, wy = x - ax, y - ay
        t = clamp((wx * ex + wy * ey) / ee)
        return hypot(wx - ex * t, wy - ey * t) - r
    return f


def rbox(cx, cy, hx, hy, r):
    def f(x, y):
        qx, qy = abs(x - cx) - hx + r, abs(y - cy) - hy + r
        return hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0) - r
    return f


def ring(cx, cy, r, w):
    return lambda x, y: abs(hypot(x - cx, y - cy) - r) - w


def arc(cx, cy, r, w, a0, span):
    """a0 에서 시계 방향(화면 y 아래)으로 span 만큼 도는 굵기 2w 활, 끝은 둥글게."""
    e0 = (cx + r * cos(a0), cy + r * sin(a0))
    e1 = (cx + r * cos(a0 + span), cy + r * sin(a0 + span))

    def f(x, y):
        if (atan2(y - cy, x - cx) - a0) % TAU <= span:
            return abs(hypot(x - cx, y - cy) - r) - w
        return min(hypot(x - e0[0], y - e0[1]), hypot(x - e1[0], y - e1[1])) - w
    return f


def grow(f, r):
    return lambda x, y: f(x, y) - r


def union(*fs):
    return lambda x, y: min(g(x, y) for g in fs)


def smin(k, *fs):
    """이음매를 k 만큼 둥글려 붙인다(iq 의 다항 smooth min)."""
    def f(x, y):
        d = fs[0](x, y)
        for g in fs[1:]:
            e = g(x, y)
            h = clamp(0.5 + 0.5 * (e - d) / k)
            d = e * (1 - h) + d * h - k * h * (1 - h)
        return d
    return f


def cut(f, g):
    return lambda x, y: max(f(x, y), -g(x, y))


def turn(f, ang, cx, cy):
    """(cx, cy) 둘레로 ang(라디안, 화면 시계 방향) 돌린 모양."""
    c, s = cos(ang), sin(ang)
    return lambda x, y: f(cx + (x - cx) * c + (y - cy) * s, cy - (x - cx) * s + (y - cy) * c)


def at(f, dx, dy):
    return lambda x, y: f(x - dx, y - dy)


# ---- 칸 모양 ----

ARROW = [(1.6, 1.6), (14.8, 14.8), (9.8, 14.8), (12.6, 21.0), (10.0, 22.1), (7.2, 16.1), (1.6, 20.4)]
TIP = (1.6, 1.6)
C = 12.0          # 가운데 핫스팟 칸들(크기 조절·이동·십자·I빔·금지·바쁨)


def arrow():
    return grow(poly(ARROW), 0.5)


def darrow(hl, w=0.75, hw=3.0, hh=3.4):
    """가로로 누운 양쪽 화살표, 가운데가 (0, 0)."""
    return grow(smin(0.45, capsule(-hl + hh * 0.6, 0, hl - hh * 0.6, 0, w),
                     poly([(-hl, 0), (-hl + hh, -hw), (-hl + hh, hw)]),
                     poly([(hl, 0), (hl - hh, hw), (hl - hh, -hw)])), 0.35)


def spinner(cx, cy, r, w, a0):
    """바쁨 고리 — 흐린 길 위로 머리가 밝은 꼬리 활."""
    span = TAU * 0.62

    def fade(x, y):
        return 0.12 + 0.88 * clamp(((atan2(y - cy, x - cx) - a0) % TAU) / span)
    return [dict(f=ring(cx, cy, r, w), alpha=0.32, shadow=False),
            dict(f=arc(cx, cy, r, w, a0, span), fade=fade)]


def question(cx, cy, s=1.0):
    """물음표 획(잉크). (cx, cy) 는 고리 가운데."""
    r, w = 1.55 * s, 0.5 * s
    a0, span = math.pi, math.pi * 1.25
    ex, ey = cx + r * cos(a0 + span), cy + r * sin(a0 + span)
    return union(arc(cx, cy, r, w, a0, span), capsule(ex, ey, cx, cy + 2.3 * s, w),
                 circle(cx, cy + 4.0 * s, w * 1.15))


def hand():
    parts = [capsule(9.4, 2.4, 9.4, 11.5, 1.5),                    # 집게손가락
             rbox(12.3, 16.0, 4.7, 4.4, 2.3),                       # 손바닥
             capsule(12.0, 10.6, 12.0, 12.6, 1.4),                  # 접은 손가락 셋
             capsule(14.4, 11.3, 14.4, 13.0, 1.35),
             capsule(16.5, 12.4, 16.5, 13.8, 1.2),
             capsule(7.6, 15.6, 5.4, 12.3, 1.35)]                   # 엄지
    return smin(0.3, *parts)


def pencil():
    """끝이 (2.6, 21.4) 인 비스듬한 연필. 몸통·깎은 나무는 재질, 심은 잉크."""
    ang = -math.pi / 4                                             # 오른쪽 위로
    ux, uy = cos(ang), sin(ang)
    tx, ty = 2.6, 21.4

    def along(t, o):                                               # 끝에서 t, 옆으로 o
        return tx + ux * t - uy * o, ty + uy * t + ux * o
    w = 1.75
    body = rbox(0, 0, 7.8, w, 0.7)
    cx, cy = along(12.4, 0)
    body = turn(at(body, cx, cy), ang, cx, cy)
    cone = poly([along(0.2, 0), along(4.8, -w), along(4.8, w)])
    tip = poly([along(0.0, 0), along(1.5, -w * 0.36), along(1.5, w * 0.36)])
    return grow(smin(0.25, body, cone), 0.15), grow(tip, 0.12)


def pin(cx, cy, r=3.2):
    head = circle(cx, cy, r)
    tail = poly([(cx - r * 0.82, cy + r * 0.55), (cx + r * 0.82, cy + r * 0.55), (cx, cy + r * 2.3)])
    return cut(smin(0.6, head, tail), circle(cx, cy, r * 0.42))


def person(cx, cy):
    return union(circle(cx, cy - 2.6, 2.0),
                 cut(rbox(cx, cy + 2.6, 3.7, 2.7, 2.4), rbox(cx, cy + 5.6, 5, 0.3, 0)))


def cell(name, frame=0.0):
    """칸 → (레이어 목록, 핫스팟). 레이어: f 거리함수, ink 잉크색으로 칠함, alpha·fade 곱, shadow."""
    A = dict(f=arrow())
    spin = TAU * frame - math.pi / 2
    if name == "arrow":
        return [A], TIP
    if name == "busy":
        return [A, dict(f=circle(18.2, 18.2, 4.1), alpha=0.0, shadow=True)] + spinner(18.2, 18.2, 3.1, 0.75, spin), TIP
    if name == "wait":
        return spinner(C, C, 7.6, 1.55, spin), (C, C)
    if name == "help":
        return [A, dict(f=circle(18.4, 17.6, 4.6)), dict(f=question(18.4, 16.2, 1.0), ink=True)], TIP
    if name == "cross":
        g, e, w = 2.0, 9.5, 0.62
        return [dict(f=union(capsule(C - e, C, C - g, C, w), capsule(C + g, C, C + e, C, w),
                             capsule(C, C - e, C, C - g, w), capsule(C, C + g, C, C + e, w),
                             circle(C, C, 0.7)))], (C, C)
    if name == "ibeam":
        return [dict(f=smin(0.5, capsule(C, 3.6, C, 20.4, 0.75),
                            capsule(C - 3.0, 3.0, C + 3.0, 3.0, 0.75),
                            capsule(C - 3.0, 21.0, C + 3.0, 21.0, 0.75)))], (C, C)
    if name == "pen":
        body, tip = pencil()
        return [dict(f=body), dict(f=tip, ink=True, shadow=False)], (2.6, 21.4)
    if name == "no":
        return [dict(f=union(ring(C, C, 8.0, 1.45), turn(capsule(C - 7.6, C, C + 7.6, C, 1.45), math.pi / 4, C, C)),
                     warn=True)], (C, C)
    if name in ("we", "ns", "nwse", "nesw"):
        ang = {"we": 0, "ns": math.pi / 2, "nwse": math.pi / 4, "nesw": -math.pi / 4}[name]
        return [dict(f=turn(at(darrow(10.2 if name in ("we", "ns") else 9.6), C, C), ang, C, C))], (C, C)
    if name == "move":
        a = at(darrow(10.4, w=0.6, hw=2.7, hh=3.1), C, C)
        return [dict(f=smin(0.6, a, turn(a, math.pi / 2, C, C), circle(C, C, 1.6)))], (C, C)
    if name == "up":
        return [dict(f=grow(smin(0.45, capsule(C, 7, C, 21.6, 0.75),
                                 poly([(C, 2.0), (C - 4.4, 7.4), (C + 4.4, 7.4)])), 0.35))], (C, 2.0)
    if name == "hand":
        return [dict(f=hand())], (9.4, 0.9)
    if name == "pin":
        return [A, dict(f=pin(18.6, 13.4))], TIP
    if name == "person":
        return [A, dict(f=person(18.6, 16.4))], TIP
    raise KeyError(name)


CELLS = ["arrow", "help", "busy", "wait", "cross", "ibeam", "pen", "no", "ns", "we",
         "nwse", "nesw", "move", "up", "hand", "pin", "person"]


# ---- 재질 ----

WHITE = (1.0, 1.0, 1.0)
LX, LY = -0.6, -0.8           # 빛이 오는 쪽(왼쪽 위)


class Glass:
    shadow = (0.04, 0.07, 0.16, 0.30)
    ink = (0.10, 0.30, 0.62)
    glow = None

    def body(self, x, y, d, nx, ny, warn, frame):
        t = clamp((x + y) / 44)
        c = lerp((1.0, 0.86, 0.88), (0.96, 0.62, 0.68), t) if warn else lerp((0.90, 0.95, 1.0), (0.58, 0.76, 0.98), t)
        depth = -d
        rim = exp(-depth / 0.7)
        lit = clamp(nx * LX + ny * LY)
        dark = clamp(-(nx * LX + ny * LY))
        a = 0.46 + 0.40 * rim
        c = lerp(c, WHITE, rim * (0.25 + 0.75 * lit))
        c = lerp(c, (0.55, 0.20, 0.30) if warn else (0.22, 0.40, 0.68), rim * dark * 0.55)
        a += 0.25 * rim * dark
        glare = 0.30 * (1 - smooth(-0.6, 0.6, (y - 0.55 * x) - 4.2 - 6.0 * frame))  # 위쪽 비스듬한 반사
        c = lerp(c, WHITE, glare)
        a += 0.25 * glare
        edge = exp(-(depth / 0.36) ** 2)
        c = lerp(c, (0.36, 0.08, 0.14) if warn else (0.06, 0.13, 0.30), 0.92 * edge)
        return c, max(clamp(a), 0.97 * edge)


AURORA = [(0.15, 0.95, 0.85), (0.45, 1.0, 0.55), (0.30, 0.60, 1.0), (0.75, 0.40, 1.0), (1.0, 0.40, 0.80)]
EMBER = [(1.0, 0.30, 0.42), (1.0, 0.58, 0.30), (1.0, 0.30, 0.70)]


def ramp(pal, t):
    t = (t % 1.0) * len(pal)
    i = int(t)
    return lerp(pal[i % len(pal)], pal[(i + 1) % len(pal)], smooth(0, 1, t - i))


class Aurora:
    shadow = (0.02, 0.02, 0.08, 0.22)
    ink = (0.97, 0.99, 1.0)

    def hue(self, x, y, warn, frame):
        return ramp(EMBER if warn else AURORA, (x * 0.55 + y) / 30 + frame)

    def body(self, x, y, d, nx, ny, warn, frame):
        base = lerp((0.05, 0.06, 0.16), (0.13, 0.07, 0.26), clamp((x + y) / 44))
        h = self.hue(x, y, warn, frame)
        depth = -d
        c = lerp(base, h, 0.10)
        c = lerp(c, h, 0.92 * exp(-depth / 0.55))
        c = lerp(c, WHITE, 0.45 * exp(-((depth - 0.22) / 0.16) ** 2))
        c = lerp(c, WHITE, 0.12 * clamp(nx * LX + ny * LY) * exp(-depth / 1.5))
        return c, 0.97

    def glow(self, x, y, d, warn, frame):
        return self.hue(x, y, warn, frame), 0.62 * exp(-d / 0.75)


class Chrome:
    shadow = (0.02, 0.03, 0.06, 0.34)
    ink = (0.10, 0.11, 0.14)
    glow = None

    def body(self, x, y, d, nx, ny, warn, frame):
        v = x * 0.42 + y
        m = 0.58 + 0.27 * sin(v * 0.55 + 0.6) + 0.10 * sin(v * 1.7 + 1.3)
        c = lerp((0.28, 0.31, 0.36), (0.94, 0.96, 0.99), clamp(m))
        if warn:
            c = (c[0] * 1.0, c[1] * 0.72, c[2] * 0.72)
        depth = -d
        bev = 1 - smooth(0.0, 1.25, depth)
        lit = nx * LX + ny * LY
        c = lerp(c, WHITE, bev * lit * 0.85) if lit > 0 else lerp(c, (0.12, 0.13, 0.16), bev * -lit * 0.75)
        c = lerp(c, WHITE, 0.6 * exp(-((x + y - 16 - 40 * frame) / 1.4) ** 2))     # 지나가는 반사 띠
        c = lerp(c, (0.08, 0.09, 0.11), 0.9 * exp(-(depth / 0.2) ** 2))
        return c, 1.0


STYLES = {"glass": Glass(), "aurora": Aurora(), "chrome": Chrome()}


# ---- 그리기 ----

def field(f):
    """거리를 칠할 수 있는 자리만 잰다. 8칸 덩이 가운데에서 먼저 재 M 밖이면 덩이째 건너뛴다."""
    d = {}
    for by in range(0, N, 8):
        for bx in range(0, N, 8):
            if f((bx + 4) / U, (by + 4) / U) > M + 0.75:
                continue
            for py in range(by, by + 8):
                for px in range(bx, bx + 8):
                    d[px, py] = f((px + 0.5) / U, (py + 0.5) / U)
    return d


def render(style, name, frame=0.0):
    """→ 256×256 미리 곱한 RGBA float 목록 넷, 핫스팟(픽셀)."""
    st = STYLES[style]
    layers, hot = cell(name, frame)
    R, G, B, A = ([0.0] * (N * N) for _ in range(4))

    def over(i, r, g, b, a):
        k = 1 - a
        R[i] = r + R[i] * k
        G[i] = g + G[i] * k
        B[i] = b + B[i] * k
        A[i] = a + A[i] * k

    fields = [field(L["f"]) for L in layers]
    sr, sg, sb, sa = st.shadow
    ox, oy = round(0.55 * U), round(0.9 * U)
    for L, d in zip(layers, fields):                                # 그림자 먼저 다 깐다
        if not L.get("shadow", True):
            continue
        for (px, py) in d:
            e = d.get((px - ox, py - oy))
            if e is None or e > 1.8:
                continue
            a = sa * (1 - smooth(-0.8, 1.8, e))
            if a > 0.002:
                over(py * N + px, sr * a, sg * a, sb * a, a)
    for L, d in zip(layers, fields):
        mul = L.get("alpha", 1.0)
        if mul <= 0:
            continue
        fade = L.get("fade")
        warn = L.get("warn", False)
        glow = None if L.get("ink") else getattr(st, "glow", None)
        for (px, py), e in d.items():
            cov = clamp(0.5 - e * U)
            if cov <= 0 and (glow is None or e > M):
                continue
            x, y = (px + 0.5) / U, (py + 0.5) / U
            m = mul * (fade(x, y) if fade else 1.0)
            r = g = b = a = 0.0
            if cov > 0:
                if L.get("ink"):
                    (cr, cg, cb), ca = st.ink, 1.0
                else:
                    gx = d.get((px + 1, py), e) - d.get((px - 1, py), e)
                    gy = d.get((px, py + 1), e) - d.get((px, py - 1), e)
                    gl = hypot(gx, gy) or 1.0
                    (cr, cg, cb), ca = st.body(x, y, e, gx / gl, gy / gl, warn, frame)
                ca *= cov * m
                r, g, b, a = cr * ca, cg * ca, cb * ca, ca
            if glow is not None and cov < 1:
                (hr, hg, hb), ha = glow(x, y, max(e, 0.0), warn, frame)
                ha *= (1 - cov) * m
                r, g, b, a = r + hr * ha, g + hg * ha, b + hb * ha, a + ha
            if a > 0.001:
                over(py * N + px, r, g, b, a)
    return (R, G, B, A), (round(hot[0] * U), round(hot[1] * U))


def weights(src, dst):
    """한 축을 src → dst 로 줄이는 면적 가중치: 칸마다 [(원본 칸, 몫)]."""
    out = []
    k = src / dst
    for i in range(dst):
        a, b = i * k, (i + 1) * k
        row = []
        for j in range(int(a), min(src, math.ceil(b))):
            w = min(b, j + 1) - max(a, j)
            if w > 1e-9:
                row.append((j, w / k))
        out.append(row)
    return out


def shrink(img, size):
    """미리 곱한 RGBA 를 size 로 면적 평균. 가로 다음 세로."""
    W = weights(N, size)
    res = []
    for ch in img:
        tmp = [0.0] * (size * N)
        for y in range(N):
            row = ch[y * N:(y + 1) * N]
            for x, ws in enumerate(W):
                tmp[y * size + x] = sum(row[j] * w for j, w in ws)
        out = [0.0] * (size * size)
        for x in range(size):
            for y, ws in enumerate(W):
                out[y * size + x] = sum(tmp[j * size + x] * w for j, w in ws)
        res.append(out)
    return res


def rgba_bytes(img, size):
    R, G, B, A = img
    buf = bytearray(size * size * 4)
    for i in range(size * size):
        a = A[i]
        if a > 0.0005:
            buf[i * 4:i * 4 + 4] = bytes((min(255, round(R[i] / a * 255)), min(255, round(G[i] / a * 255)),
                                          min(255, round(B[i] / a * 255)), min(255, round(a * 255))))
    return bytes(buf)


def png(raw, w, h, channels=4):
    stride = w * channels
    rows = b"".join(b"\0" + raw[y * stride:(y + 1) * stride] for y in range(h))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6 if channels == 4 else 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")


def job(arg):
    style, name, out = arg
    img, hot = render(style, name)
    os.makedirs(os.path.join(out, style), exist_ok=True)
    with open(os.path.join(out, style, name + ".png"), "wb") as fh:
        fh.write(png(rgba_bytes(img, N), N, N))
    return style, name, shrink(img, 128), shrink(img, 32), hot


def sheet(out, style, got):
    """위 두 줄은 흰 바탕, 다음 두 줄은 검은 바탕에 128. 맨 아래 두 줄은 실제 32 를 2배로(흰·검은)."""
    big, small, cols = 136, 72, 9
    W = cols * big
    H = 4 * big + 2 * small
    pix = bytearray(W * H * 3)
    bgs = [(255, 255, 255), (32, 33, 36)]
    for y in range(H):
        bg = bgs[0] if y < 2 * big or (4 * big <= y < 4 * big + small) else bgs[1]
        pix[y * W * 3:(y + 1) * W * 3] = bytes(bg) * W

    def put(img, size, ox, oy, scale, bg):
        R, G, B, A = img
        for y in range(size):
            for x in range(size):
                i = y * size + x
                k = 1 - A[i]
                c = (round(min(1, R[i] + bg[0] / 255 * k) * 255), round(min(1, G[i] + bg[1] / 255 * k) * 255),
                     round(min(1, B[i] + bg[2] / 255 * k) * 255))
                for sy in range(scale):
                    o = ((oy + y * scale + sy) * W + ox + x * scale) * 3
                    pix[o:o + 3 * scale] = bytes(c) * scale
    for k, name in enumerate(CELLS):
        b128, b32, hot = got[name]
        col, row = k % cols, k // cols
        put(b128, 128, col * big + 4, row * big + 4, 1, bgs[0])
        put(b128, 128, col * big + 4, (2 + row) * big + 4, 1, bgs[1])
        sx = k * small + 4 if k * small + small <= W else None
        if sx is not None:
            put(b32, 32, sx, 4 * big + 4, 2, bgs[0])
            put(b32, 32, sx, 4 * big + small + 4, 2, bgs[1])
        hx, hy = col * big + 4 + hot[0] // 2, row * big + 4 + hot[1] // 2      # 핫스팟 표시(흰 바탕 줄만)
        for yy in range(hy - 1, hy + 2):
            o = (yy * W + hx - 1) * 3
            pix[o:o + 9] = bytes((255, 0, 200)) * 3
    with open(os.path.join(out, f"sheet_{style}.png"), "wb") as fh:
        fh.write(png(bytes(pix), W, H, 3))


def main():
    out = sys.argv[1]
    styles = sys.argv[2:] or list(STYLES)
    got = {s: {} for s in styles}
    with ProcessPoolExecutor() as ex:
        for style, name, b128, b32, hot in ex.map(job, [(s, c, out) for s in styles for c in CELLS]):
            got[style][name] = (b128, b32, hot)
            print(style, name, flush=True)
    for s in styles:
        sheet(out, s, got[s])
        print("시트", os.path.join(out, f"sheet_{s}.png"), flush=True)


if __name__ == "__main__":
    main()

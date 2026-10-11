# SPDX-License-Identifier: Apache-2.0
"""고화질 구성표 20종 생성기 — 글래스 · 오로라 네온 · 크롬 메탈(2026-10-10) 과
클레이 · 홀로그램 · 젤리 · 미드나잇 골드 · 선셋 · 갤럭시 · 잉크(2026-10-11 낮),
그리고 빛 번짐 없이 재질과 디자인 말씨로 가른 열 결(NEW, 2026-10-11 오후) — 백자 청화 · 청자 ·
대리석 · 테라초 · 현무암 · 월넛 · 가죽 · 종이접기 · 바우하우스 · 청사진. 앞 열이 다 네온에 번짐을
입혀 진부하다는 말에 뽑았다.

픽셀 그림(.txt)이 아니라 거리함수로 256칸 판에 바로 그린다. .txt 는 글자 하나가 색 하나라
그라데이션·하이라이트처럼 색이 수천 개인 그림을 못 담고, 기본 모양은 그 그림을 최근접으로 키워
32 위로는 계단이 그대로 커진다. 여기서는 256 원본을 그리고 크기마다 면적 평균으로 줄인다.

모양은 32칸 판의 한 칸(U = 8px)을 단위로 적는다 — 다른 구성표 그림과 같은 자리·크기 감각.
재질은 거리 d 와 테두리 법선으로 칠한다: 테두리 쪽 밝기·안쪽 테·바깥 번짐. 뒤 일곱은 dome() 으로
테두리 단면에서 법선을 세워 빛을 받고(L3·H3), soft 칸만큼 몸을 부풀리거나 tip_body 로 펜 심을
몸 색으로 칠할 수 있다. 움직임은 frame(0–1) 에 주기로 걸어 고리 이음매가 없다.

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


def cell(name, frame=0.0, soft=0.0, tip_body=False):
    """칸 → (레이어 목록, 핫스팟). 레이어: f 거리함수, ink 잉크색으로 칠함, alpha·fade 곱, shadow.
    soft 는 잉크가 아닌 레이어를 그만큼(칸) 부풀린다 — 클레이·젤리는 통통하게, 잉크·선셋은 흰 테를
    모양 밖에 두르려고(안 부풀리면 I빔·십자 같은 가는 획이 테만 남는다). tip_body 면 연필심도 재질로 칠한다
    (흰 테 결은 잉크 한 색 심이 어느 한 바탕에서 사라진다)."""
    layers, hot = _cell(name, frame)
    if tip_body:
        for L in layers:
            if L.get("tip"):
                L["ink"] = False
    if soft:
        for L in layers:
            if not L.get("ink"):
                L["f"] = grow(L["f"], soft)
    return layers, hot


def _cell(name, frame):
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
        return [dict(f=body), dict(f=tip, ink=True, tip=True, shadow=False)], (2.6, 21.4)
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


# ---- 2026-10-11 더한 일곱 결 ----
# 움직임은 frame(0..1)에 주기로만 기댄다 — 끝 장에서 첫 장으로 넘어갈 때 튀지 않게(글래스·크롬은 아직 튐, NEXT.md)

L3 = (-0.42, -0.56, 0.71)                         # 3D 빛: 왼쪽 위 앞
H3 = (-0.23, -0.31, 0.92)                         # 빛과 눈(0, 0, 1)의 반각 — 반짝임


def dome(nx, ny, depth, R):
    """테두리에서 R 칸 안쪽까지 둥글게 솟은 면의 3D 법선. 테두리에서는 옆을, R 안쪽은 앞을 본다."""
    s = clamp(1 - depth / R)
    return nx * s, ny * s, math.sqrt(1 - s * s)


def dot3(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def scale(c, k):
    return (clamp(c[0] * k), clamp(c[1] * k), clamp(c[2] * k))


def ramp_to(pal, t):
    """끝을 감지 않는 ramp — 처음에서 끝까지 한 번만 간다."""
    t = clamp(t) * (len(pal) - 1)
    i = min(int(t), len(pal) - 2)
    return lerp(pal[i], pal[i + 1], smooth(0, 1, t - i))


def hsh(ix, iy, s=0):
    n = (ix * 374761393 + iy * 668265263 + s * 1442695041) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0


def noise(x, y, s=0):
    """값 잡음 0..1."""
    ix, iy = math.floor(x), math.floor(y)
    fx, fy = x - ix, y - iy
    ux, uy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = hsh(ix, iy, s), hsh(ix + 1, iy, s)
    c, d = hsh(ix, iy + 1, s), hsh(ix + 1, iy + 1, s)
    return a + (b - a) * ux + (c - a) * uy + (a - b - c + d) * ux * uy


class Clay:
    """무광 파스텔 찰흙. 통통한 실루엣, 둥근 어깨에만 빛, 반짝임 거의 없음, 넓고 옅은 그림자."""
    soft = 0.55
    shadow = (0.34, 0.20, 0.44, 0.24)
    shadow_off, shadow_blur = (0.35, 1.15), 2.5
    ink = (0.36, 0.18, 0.40)
    glow = None
    PAL = [(1.0, 0.82, 0.70), (0.99, 0.72, 0.80), (0.80, 0.74, 0.99)]
    WARN = [(1.0, 0.68, 0.58), (0.97, 0.50, 0.55)]

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        base = ramp_to(self.WARN if warn else self.PAL, (x * 0.6 + y) / 34)
        n = dome(nx, ny, depth, 1.7)
        c = scale(base, 0.66 + 0.42 * dot3(n, L3))
        c = lerp(c, WHITE, 0.14 * max(0.0, dot3(n, H3)) ** 10)
        c = lerp(c, scale(base, 0.55), 0.45 * exp(-(depth / 0.22) ** 2))   # 흰 바탕에서 윤곽이 서게
        return c, 1.0


class Holo:
    """진주빛 홀로그램 포일. 비스듬한 무지개 띠가 흐르고, 기울어진 테일수록 색이 짙다."""
    shadow = (0.12, 0.08, 0.24, 0.26)
    ink = (0.32, 0.22, 0.58)
    glow = None
    PAL = [(1.0, 0.62, 0.80), (1.0, 0.85, 0.58), (0.72, 1.0, 0.70), (0.56, 0.90, 1.0), (0.72, 0.64, 1.0)]
    WARN = [(1.0, 0.55, 0.62), (1.0, 0.74, 0.52), (1.0, 0.52, 0.80)]

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        n = dome(nx, ny, depth, 1.4)
        tilt = 1 - n[2]
        t = (x + y) / 20 + 0.22 * sin((x - y) * 0.42) + 0.8 * tilt + frame
        h = ramp(self.WARN if warn else self.PAL, t)
        c = lerp((0.97, 0.96, 1.0), h, 0.55 + 0.4 * tilt)
        lit = dot3(n, L3)
        c = lerp(c, WHITE, 0.55 * max(0.0, dot3(n, H3)) ** 6)
        if lit < 0.6:
            c = lerp(c, (0.50, 0.42, 0.76), (0.6 - lit) * 0.45)
        c = lerp(c, (0.44, 0.34, 0.70) if not warn else (0.70, 0.25, 0.40), 0.85 * exp(-(depth / 0.26) ** 2))
        return c, 1.0


class Jelly:
    """딸기 젤리. 비치는 몸, 두꺼운 가운데일수록 진하고, 왼쪽 위 어깨에 젖은 반짝임."""
    soft = 0.45
    tip_body = True
    shadow = (0.55, 0.06, 0.26, 0.22)
    shadow_off, shadow_blur = (0.45, 1.0), 2.0
    ink = (1.0, 1.0, 1.0)
    glow = None

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        light, core, line = (((1.0, 0.62, 0.42), (0.86, 0.12, 0.10), (0.50, 0.04, 0.02)) if warn else
                             ((1.0, 0.58, 0.74), (0.93, 0.14, 0.42), (0.52, 0.02, 0.20)))
        k = smooth(0.0, 1.8, depth)
        c = lerp(light, core, k)
        a = 0.74 + 0.22 * k
        back = max(0.0, -(nx * LX + ny * LY)) * exp(-depth / 0.6)      # 아래 오른쪽 테로 빛이 새어 나옴
        c = lerp(c, (1.0, 0.88, 0.92), 0.6 * back)
        n = dome(nx, ny, depth, 1.6)
        spec = clamp(1.6 * max(0.0, dot3(n, H3)) ** 18 - 0.25)         # 젖은 반짝임 — 끝을 잘라 또렷하게
        c = lerp(c, WHITE, spec)
        c = lerp(c, line, 0.6 * exp(-(depth / 0.2) ** 2))
        return c, max(a, spec)


GOLD = [(0.40, 0.26, 0.06), (0.78, 0.56, 0.18), (1.0, 0.88, 0.56), (1.0, 0.97, 0.84)]


class Gold:
    """검은 옻칠에 금 테. 금빛이 테를 따라 훑고 지나가고, 옻칠 위에 흰 광택 하나."""
    shadow = (0.0, 0.0, 0.0, 0.34)
    ink = (0.92, 0.74, 0.36)
    glow = None
    RIM = 0.7

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        t = clamp((x + y) / 40)
        base = lerp((0.36, 0.05, 0.09), (0.16, 0.02, 0.04), t) if warn else lerp((0.12, 0.12, 0.16), (0.03, 0.03, 0.05), t)
        n = dome(nx, ny, depth - self.RIM, 1.5)
        c = lerp(base, (0.86, 0.88, 1.0), 0.7 * max(0.0, dot3(n, H3)) ** 30)
        w = smooth(self.RIM + 0.12, self.RIM - 0.06, depth)
        if w > 0:
            g = ramp_to(GOLD, 0.52 + 0.36 * (nx * LX + ny * LY) + 0.12 * (1 - depth / self.RIM))
            u = ((x + y) / 44 - frame) % 1.0
            g = lerp(g, (1.0, 0.98, 0.90), 0.85 * exp(-(min(u, 1 - u) * 44 / 1.3) ** 2))
            g = lerp(g, (0.30, 0.19, 0.04), 0.4 * exp(-(depth / 0.1) ** 2))
            c = lerp(c, g, w)
        return c, 1.0


class Sunset:
    """평면 그라데이션 + 흰 테. 노을색이 대각으로 깔리고 조금씩 오르내린다."""
    soft = 0.7
    tip_body = True
    LINE = 0.7
    shadow = (0.40, 0.16, 0.52, 0.30)
    shadow_off, shadow_blur = (0.4, 1.0), 2.2
    ink = (1.0, 1.0, 1.0)
    glow = None
    PAL = [(1.0, 0.80, 0.32), (1.0, 0.52, 0.36), (0.96, 0.30, 0.54), (0.58, 0.30, 0.88)]
    WARN = [(1.0, 0.56, 0.30), (0.95, 0.20, 0.30), (0.72, 0.10, 0.30)]

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        t = (x * 0.5 + y) / 30 + 0.10 * sin(TAU * frame)
        c = ramp_to(self.WARN if warn else self.PAL, t)
        c = lerp(c, WHITE, 0.10 * smooth(4.0, -2.0, y - x * 0.4))            # 위쪽이 아주 조금 밝게
        return lerp(c, WHITE, smooth(self.LINE + 0.07, self.LINE - 0.07, depth)), 1.0


class Galaxy:
    """밤하늘. 남보라 몸에 성운이 천천히 돌고 별이 깜빡인다. 라일락 테가 어두운 바탕에서도 윤곽을 잡는다."""
    shadow = (0.03, 0.02, 0.10, 0.30)
    ink = (1.0, 1.0, 1.0)
    NEB = [(0.95, 0.35, 0.85), (0.40, 0.52, 1.0), (0.30, 0.92, 0.95)]
    WARN = [(1.0, 0.35, 0.30), (1.0, 0.60, 0.25), (0.95, 0.25, 0.55)]
    STEP = 1.25                                    # 별 자리 칸

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        ox, oy = 1.8 * cos(TAU * frame), 1.8 * sin(TAU * frame)
        n1 = noise((x + ox) * 0.26, (y + oy) * 0.26, 1)
        n2 = noise(x * 0.55 + oy * 0.3, y * 0.55 - ox * 0.3, 2)
        neb = clamp((n1 * 0.7 + n2 * 0.3 - 0.36) * 1.9)
        hue = ramp(self.WARN if warn else self.NEB, n2 * 0.9 + x * 0.02)
        base = lerp((0.05, 0.04, 0.14), (0.11, 0.05, 0.22), clamp((x + y) / 44))
        c = lerp(base, hue, 0.6 * neb)
        gx, gy = math.floor(x / self.STEP), math.floor(y / self.STEP)
        if hsh(gx, gy, 7) > 0.7:
            sx = (gx + 0.2 + 0.6 * hsh(gx, gy, 8)) * self.STEP
            sy = (gy + 0.2 + 0.6 * hsh(gx, gy, 9)) * self.STEP
            tw = 0.5 + 0.5 * sin(TAU * (frame + hsh(gx, gy, 10)))
            big = hsh(gx, gy, 11) > 0.8
            ax, ay = abs(x - sx), abs(y - sy)
            b = exp(-((ax * ax + ay * ay) / (0.24 if big else 0.17) ** 2))
            if big:                                                      # 큰 별은 십자 반짝이
                b = max(b, 0.7 * tw * exp(-(min(ax, ay) / 0.07) ** 2) * exp(-max(ax, ay) / 0.45))
            c = lerp(c, WHITE, clamp(b * (0.35 + 0.65 * tw)))
        rim = (1.0, 0.66, 0.66) if warn else (0.84, 0.78, 1.0)
        return lerp(c, rim, 0.9 * exp(-(depth / 0.36) ** 2)), 1.0

    def glow(self, x, y, d, warn, frame):
        return ((1.0, 0.40, 0.45) if warn else (0.62, 0.50, 1.0)), 0.48 * exp(-d / 0.7)


class Ink:
    """검정 + 흰 테. 장식 없이 또렷한 매일 쓰는 결 — 어느 바탕이든 테나 몸 한쪽이 선다."""
    soft = 0.7
    tip_body = True
    LINE = 0.7
    shadow = (0.0, 0.0, 0.0, 0.32)
    shadow_off, shadow_blur = (0.3, 0.7), 1.9
    ink = (1.0, 1.0, 1.0)
    glow = None

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        t = clamp((x + y) / 40)
        core = lerp((0.88, 0.16, 0.20), (0.70, 0.06, 0.10), t) if warn else lerp((0.17, 0.17, 0.19), (0.04, 0.04, 0.05), t)
        return lerp(core, WHITE, smooth(self.LINE + 0.07, self.LINE - 0.07, depth)), 1.0


# ---- 2026-10-11 오후 더한 열 결 — 재료 결 ----
# 앞 열 결이 "죄다 네온에 글로우"라 진부하다는 말을 듣고 뺀 것: 빛 번짐(glow)·무지개 띠·네온 테.
# 실제 재료의 질감에 차분한 색, 윤곽은 진한 가는 선이나 상감선으로 세운다.

def fbm(x, y, s=0, n=4):
    """잡음 겹치기 0..1 언저리."""
    t, a, f = 0.0, 0.5, 1.0
    for i in range(n):
        t += a * noise(x * f, y * f, s + i)
        a, f = a * 0.5, f * 2.0
    return t


def cells(x, y, s=0):
    """지터 격자 보로노이 → (가장 가까운 점까지, 둘째까지, 그 칸 ix, iy, 점 x, 점 y)."""
    ix, iy = math.floor(x), math.floor(y)
    f1 = f2 = 9.0
    best = (ix, iy, x, y)
    for j in (-1, 0, 1):
        for i in (-1, 0, 1):
            cx, cy = ix + i, iy + j
            px, py = cx + hsh(cx, cy, s), cy + hsh(cx, cy, s + 1)
            q = (px - x) ** 2 + (py - y) ** 2
            if q < f1:
                f1, f2, best = q, f1, (cx, cy, px, py)
            elif q < f2:
                f2 = q
    return (math.sqrt(f1), math.sqrt(f2)) + best


def line_at(depth, at, w):
    """테에서 at 칸 안쪽에 그은 굵기 2w 선(0..1)."""
    return smooth(w + 0.06, w - 0.06, abs(depth - at))


class Porcelain:
    """백자 청화. 푸른 기 도는 젖빛 몸에 유약 광택, 테를 따라 코발트 붓 띠, 안쪽에 다섯 잎 잔꽃이 흩어졌다.
    붓선 한 줄을 테 안쪽에 긋던 판은 128 에서 테가 두 겹인 것으로만 읽혔다."""
    soft = 0.4
    shadow = (0.10, 0.14, 0.26, 0.24)
    shadow_off, shadow_blur = (0.35, 0.9), 2.0
    ink = (0.13, 0.22, 0.52)
    glow = None

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        c = lerp((0.985, 0.98, 0.965), (0.90, 0.92, 0.93), clamp((x + y) / 44))
        n = dome(nx, ny, depth, 1.5)
        c = scale(c, 0.87 + 0.15 * dot3(n, L3))
        blue = (0.66, 0.16, 0.16) if warn else lerp((0.20, 0.33, 0.68), (0.08, 0.15, 0.42), noise(x * 1.3, y * 1.3, 4))
        band = smooth(0.52 + 0.1 * noise(x * 0.9, y * 0.9, 3), 0.36, depth) * smooth(0.04, 0.12, depth)   # 붓 띠 — 안쪽 가장자리가 흔들린다
        f1, f2, ix, iy, px, py = cells(x * 0.3, y * 0.3, 5)
        if hsh(ix, iy, 6) > 0.45 and depth > 0.75:                      # 잔꽃 — 띠와 안 붙게 안쪽에만. 더 촘촘하면 128 에서 깨알로 읽힌다
            dx, dy = x * 0.3 - px, y * 0.3 - py
            th = math.atan2(dy, dx) + TAU * hsh(ix, iy, 7)
            R = 0.26 * (0.55 + 0.45 * abs(cos(2.5 * th)))
            band = max(band, smooth(R + 0.025, R - 0.025, f1) * smooth(0.035, 0.065, f1))   # 가운데 꽃술은 비운다
        c = lerp(c, blue, 0.9 * band)
        c = lerp(c, WHITE, 0.9 * max(0.0, dot3(n, H3)) ** 40)
        return lerp(c, (0.48, 0.10, 0.12) if warn else (0.12, 0.20, 0.44), 0.7 * exp(-(depth / 0.12) ** 2)), 1.0


class Celadon:
    """고려청자. 비색 유약이 두꺼운 가운데일수록 짙고 얇은 테는 밝게 비친다. 잔 빙렬, 왼쪽 위에 유약 광택.
    사용 불가 칸은 진사(구리 붉은 유약)."""
    soft = 0.35
    shadow = (0.08, 0.16, 0.14, 0.26)
    shadow_off, shadow_blur = (0.35, 0.9), 2.0
    ink = (0.18, 0.31, 0.27)
    glow = None

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        k = smooth(0.0, 1.8, depth)
        c = lerp((0.86, 0.60, 0.58), (0.62, 0.15, 0.20), k) if warn else lerp((0.76, 0.86, 0.80), (0.46, 0.65, 0.58), k)
        f1, f2 = cells(x * 0.95, y * 0.95, 51)[:2]
        c = lerp(c, scale(c, 0.62), 0.45 * exp(-((f2 - f1) / 0.07) ** 2))       # 빙렬
        n = dome(nx, ny, depth, 1.3)
        c = scale(c, 0.86 + 0.2 * dot3(n, L3))
        c = lerp(c, WHITE, 0.85 * max(0.0, dot3(n, H3)) ** 36)
        return lerp(c, (0.40, 0.08, 0.10) if warn else (0.20, 0.36, 0.31), 0.8 * exp(-(depth / 0.2) ** 2)), 1.0


BRASS = [(0.36, 0.25, 0.08), (0.68, 0.52, 0.24), (0.90, 0.78, 0.50), (0.98, 0.92, 0.74)]


class Marble:
    """카라라 대리석에 가는 놋쇠 테. 흰 돌에 회색 결이 흐르고 물갈이한 겉에 은은한 광택.
    사용 불가 칸은 붉은 대리석(로소)에 흰 결."""
    shadow = (0.10, 0.10, 0.12, 0.28)
    ink = (0.20, 0.20, 0.22)
    glow = None
    RIM = 0.42

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        u = fbm(x * 0.16 + 0.4 * y * 0.16, y * 0.16, 61, 4)             # 결은 잡음의 등치선 — 사인 줄무늬는 등고선으로 읽혔다
        w2 = fbm(x * 0.34, y * 0.34, 63, 3)
        vein = max(smooth(0.035, 0.008, abs(u - 0.5)) * (0.55 + 0.45 * noise(x * 0.3, y * 0.3, 66)),
                   0.25 * smooth(0.10, 0.0, abs(u - 0.5)),                 # 굵은 결 둘레의 옅은 번짐
                   0.5 * smooth(0.018, 0.004, abs(w2 - 0.47)))             # 가는 잔결
        haze = fbm(x * 0.5, y * 0.5, 67, 3)
        if warn:
            c = lerp(lerp((0.62, 0.17, 0.16), (0.48, 0.10, 0.11), haze), (0.96, 0.90, 0.88), 0.85 * vein)
        else:
            c = lerp(lerp((0.965, 0.96, 0.95), (0.86, 0.86, 0.86), 0.55 * haze), (0.50, 0.52, 0.56), 0.7 * vein)
        n = dome(nx, ny, depth - self.RIM, 1.2)
        c = scale(c, 0.9 + 0.12 * dot3(n, L3))
        c = lerp(c, WHITE, 0.55 * max(0.0, dot3(n, H3)) ** 40)
        w = smooth(self.RIM + 0.08, self.RIM - 0.05, depth)
        if w > 0:                                                        # 놋쇠 테 — 빛 쪽이 밝다
            g = ramp_to(BRASS, 0.5 + 0.38 * (nx * LX + ny * LY) + 0.1 * (1 - depth / self.RIM))
            g = lerp(g, (0.24, 0.16, 0.05), 0.55 * exp(-(depth / 0.1) ** 2))
            c = lerp(c, g, w)
        return c, 1.0


class Terrazzo:
    """테라초. 크림 시멘트에 테라코타·세이지·먹·황토·청회색 돌 조각이 박혔다. 무광, 가는 먹선 윤곽."""
    soft = 0.45
    shadow = (0.20, 0.15, 0.10, 0.24)
    shadow_off, shadow_blur = (0.35, 0.9), 2.0
    ink = (0.20, 0.20, 0.22)
    glow = None
    CHIPS = [(0.78, 0.42, 0.30), (0.55, 0.64, 0.53), (0.22, 0.22, 0.24), (0.86, 0.66, 0.32), (0.44, 0.54, 0.66)]
    WARN = [(0.78, 0.22, 0.20), (0.92, 0.55, 0.42), (0.30, 0.12, 0.12), (0.96, 0.82, 0.74)]

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        c = (0.96, 0.80, 0.76) if warn else (0.95, 0.92, 0.87)
        c = scale(c, 0.97 + 0.05 * noise(x * 6, y * 6, 71))
        f1, f2, ix, iy, px, py = cells(x * 0.78, y * 0.78, 72)
        if hsh(ix, iy, 74) > 0.38:                                       # 조각 — 돌린 세모·네모·오각
            k = 3 + int(hsh(ix, iy, 75) * 3)
            a0 = TAU * hsh(ix, iy, 76)
            dx, dy = x * 0.78 - px, y * 0.78 - py
            pd = max(dx * cos(a0 + i * TAU / k) + dy * sin(a0 + i * TAU / k) for i in range(k))
            r = 0.13 + 0.17 * hsh(ix, iy, 77)
            pal = self.WARN if warn else self.CHIPS
            c = lerp(c, pal[int(hsh(ix, iy, 78) * len(pal))], smooth(r + 0.025, r - 0.025, pd))
        n = dome(nx, ny, depth, 1.3)
        c = scale(c, 0.9 + 0.14 * dot3(n, L3))
        return lerp(c, (0.22, 0.21, 0.21), 0.8 * exp(-(depth / 0.2) ** 2)), 1.0


class Basalt:
    """제주 현무암. 잿빛 돌에 숨구멍이 송송, 무광. 모서리가 닳아 밝다. 사용 불가 칸은 붉은 송이."""
    soft = 0.45
    tip_body = True
    shadow = (0.0, 0.0, 0.0, 0.30)
    shadow_off, shadow_blur = (0.35, 0.9), 2.0
    ink = (0.93, 0.92, 0.89)
    glow = None

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        c = lerp((0.66, 0.32, 0.24), (0.50, 0.20, 0.15), clamp((x + y) / 44)) if warn else \
            lerp((0.56, 0.56, 0.56), (0.44, 0.44, 0.45), clamp((x + y) / 44))      # 어두운 바탕에 묻히지 않을 만큼 밝게
        c = scale(c, 0.9 + 0.2 * fbm(x * 1.6, y * 1.6, 81, 3))
        f1, f2, ix, iy, px, py = cells(x * 1.15, y * 1.15, 82)
        if hsh(ix, iy, 84) > 0.4:                                        # 숨구멍 — 안은 어둡고 아래 오른쪽 벽이 빛을 받는다
            r = 0.10 + 0.14 * hsh(ix, iy, 85)
            hole = smooth(r + 0.04, r - 0.03, f1)
            wall = clamp(((x * 1.15 - px) * -LX + (y * 1.15 - py) * -LY) / (r + 1e-6))
            c = lerp(c, lerp((0.10, 0.10, 0.11), scale(c, 1.2), 0.45 * wall), hole)
        n = dome(nx, ny, depth, 1.3)
        c = scale(c, 0.82 + 0.3 * dot3(n, L3))
        e = exp(-(depth / 0.32) ** 2)
        c = lerp(c, (0.86, 0.85, 0.82), e * (0.45 + 0.5 * clamp(nx * LX + ny * LY)))
        return c, 1.0


class Walnut:
    """호두나무 원목에 단풍나무 상감선 한 줄. 오일 마감이라 광택은 넓고 옅다. 사용 불가 칸은 붉은 블러드우드."""
    soft = 0.45
    tip_body = True
    shadow = (0.12, 0.07, 0.03, 0.30)
    shadow_off, shadow_blur = (0.35, 0.9), 2.0
    ink = (0.93, 0.85, 0.68)
    glow = None

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        g = (x * 0.94 - y * 0.34) * 1.5 + 2.4 * fbm(x * 0.10, y * 0.40, 91, 3)   # 결은 거의 세로, 결을 가로질러 나이테
        ring = (0.5 + 0.5 * sin(g * 1.9)) ** 3
        pore = smooth(0.62, 0.8, noise(x * 3.2, y * 0.7, 94))
        if warn:
            c = lerp((0.58, 0.14, 0.09), (0.38, 0.07, 0.05), clamp(ring + 0.4 * pore))
        else:
            c = lerp((0.40, 0.25, 0.15), (0.22, 0.13, 0.07), clamp(ring + 0.4 * pore))
        n = dome(nx, ny, depth, 1.4)
        c = scale(c, 0.85 + 0.3 * dot3(n, L3))
        c = lerp(c, (1.0, 0.94, 0.84), 0.22 * max(0.0, dot3(n, H3)) ** 8)
        c = lerp(c, (0.93, 0.84, 0.66), line_at(depth, 0.58, 0.08))        # 상감선
        return lerp(c, (0.14, 0.08, 0.04), 0.7 * exp(-(depth / 0.18) ** 2)), 1.0


class Leather:
    """새들 가죽. 황갈 몸에 잔 결, 끝은 짙게 태운 마감, 테 안쪽으로 크림색 실 바느질. 사용 불가 칸은 옥스블러드."""
    soft = 0.55
    tip_body = True
    shadow = (0.18, 0.08, 0.03, 0.30)
    shadow_off, shadow_blur = (0.35, 0.9), 2.0
    ink = (0.96, 0.90, 0.76)
    glow = None
    SD, STEP = 0.82, 0.78                       # 바늘땀 깊이·간격(칸)

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        t = clamp((x + y) / 44)
        c = lerp((0.50, 0.11, 0.12), (0.34, 0.06, 0.08), t) if warn else lerp((0.72, 0.44, 0.25), (0.56, 0.31, 0.16), t)
        c = scale(c, 0.9 + 0.12 * noise(x * 2.4, y * 2.4, 101) + 0.06 * noise(x * 6, y * 6, 102))
        n = dome(nx, ny, depth, 1.1)
        c = scale(c, 0.88 + 0.22 * dot3(n, L3))
        c = lerp(c, (1.0, 0.92, 0.80), 0.14 * max(0.0, dot3(n, H3)) ** 10)
        c = lerp(c, scale(c, 0.78), 0.5 * line_at(depth, self.SD, 0.2))     # 땀 자리가 눌려 조금 어둡다
        ph = ((x * -ny + y * nx) / self.STEP) % 1.0                         # 테를 따라가는 자리 — 곧은 변에서 길이와 같다
        dash = smooth(0.30, 0.22, abs(ph - 0.5))
        c = lerp(c, (0.97, 0.91, 0.78), line_at(depth, self.SD, 0.07) * dash)
        return lerp(c, (0.22, 0.10, 0.05), 0.85 * smooth(0.32, 0.0, depth)), 1.0


class Origami:
    """산호색 종이를 접은 결. 가장 가까운 테 쪽으로 면이 기울어 접힌 능선이 서고, 면마다 빛을 다르게 받는다.
    무광이라 면 사이 밝기 차를 줄이고 잔 섬유를 깔았다 — 겨자색에 대비를 세게 준 판은 금 조각으로 읽혔다.
    사용 불가 칸은 짙은 홍색 종이."""
    soft = 0.3
    shadow = (0.30, 0.12, 0.08, 0.24)
    shadow_off, shadow_blur = (0.4, 1.0), 2.0
    ink = (0.36, 0.14, 0.10)
    glow = None
    TILT = 0.85

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        base = (0.66, 0.13, 0.18) if warn else (0.94, 0.55, 0.45)
        m = math.sqrt(1 + self.TILT * self.TILT)
        lam = (nx * self.TILT * L3[0] + ny * self.TILT * L3[1] + L3[2]) / m       # 면마다 기울기가 같아 납작하게 칠해진다
        c = scale(base, 0.66 + 0.4 * lam)
        c = scale(c, 0.96 + 0.04 * noise(x * 5, y * 5, 111) + 0.03 * noise(x * 14, y * 3, 112))   # 종이 섬유
        return lerp(c, scale(base, 0.55), 0.6 * exp(-(depth / 0.12) ** 2)), 1.0


class Bauhaus:
    """바우하우스 포스터. 크림 몸에 굵은 먹선, 주홍 판 그림자가 블러 없이 비켜 찍힌다. 사용 불가 칸은 주홍 몸에 먹 그림자."""
    soft = 0.3
    shadow = (0.84, 0.25, 0.16, 1.0)
    shadow_hard = True
    shadow_off = (0.95, 0.95)
    ink = (0.08, 0.08, 0.09)
    glow = None
    LINE = 0.42

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        c = (0.86, 0.26, 0.17) if warn else (0.96, 0.93, 0.86)
        return lerp(c, (0.08, 0.08, 0.09), smooth(self.LINE + 0.05, self.LINE - 0.05, depth)), 1.0


class Cyanotype:
    """시아노타입 청사진. 프러시안 블루 몸에 테를 따라 흰 등고선이 겹겹이 들고, 등고선이 천천히 안으로 흐른다."""
    soft = 0.35
    tip_body = True
    shadow = (0.04, 0.10, 0.22, 0.28)
    shadow_off, shadow_blur = (0.35, 0.9), 2.0
    ink = (0.93, 0.96, 0.99)
    glow = None
    P = 0.56                                    # 등고선 간격(칸)

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        t = clamp((x + y) / 44)
        c = lerp((0.62, 0.20, 0.16), (0.46, 0.12, 0.10), t) if warn else lerp((0.14, 0.30, 0.55), (0.08, 0.20, 0.41), t)
        c = scale(c, 0.94 + 0.1 * fbm(x * 1.4, y * 1.4, 121, 3))
        q = (depth - self.P * frame) / self.P
        line = smooth(0.12, 0.05, abs(q - round(q)) * self.P) * smooth(0.25, 0.45, depth)
        c = lerp(c, (0.84, 0.91, 0.97), 0.6 * line)
        return lerp(c, (0.93, 0.96, 0.99), 0.92 * exp(-(depth / 0.17) ** 2)), 1.0


STYLES = {"glass": Glass(), "aurora": Aurora(), "chrome": Chrome(),
          "clay": Clay(), "holo": Holo(), "jelly": Jelly(), "gold": Gold(),
          "sunset": Sunset(), "galaxy": Galaxy(), "ink": Ink(),
          "porcelain": Porcelain(), "celadon": Celadon(), "marble": Marble(), "terrazzo": Terrazzo(),
          "basalt": Basalt(), "walnut": Walnut(), "leather": Leather(), "origami": Origami(),
          "bauhaus": Bauhaus(), "cyanotype": Cyanotype()}
NEW = ["porcelain", "celadon", "marble", "terrazzo", "basalt", "walnut", "leather", "origami", "bauhaus", "cyanotype"]


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
    layers, hot = cell(name, frame, getattr(st, "soft", 0.0), getattr(st, "tip_body", False))
    R, G, B, A = ([0.0] * (N * N) for _ in range(4))

    def over(i, r, g, b, a):
        k = 1 - a
        R[i] = r + R[i] * k
        G[i] = g + G[i] * k
        B[i] = b + B[i] * k
        A[i] = a + A[i] * k

    fields = [field(L["f"]) for L in layers]
    sr, sg, sb, sa = st.shadow
    sx, sy = getattr(st, "shadow_off", (0.55, 0.9))
    blur = getattr(st, "shadow_blur", 1.8)
    hard = getattr(st, "shadow_hard", False)                        # 번짐 없이 판으로 찍은 그림자(바우하우스)
    ox, oy = round(sx * U), round(sy * U)
    for L, d in zip(layers, fields):                                # 그림자 먼저 다 깐다
        if not L.get("shadow", True) or (hard and L.get("alpha", 1.0) <= 0):
            continue                                                # 안 보이는 몸의 판 그림자는 빈 원판만 남는다
        for (px, py) in d:
            e = d.get((px - ox, py - oy))
            if e is None or e > (0.2 if hard else blur):
                continue
            a = sa * (clamp(0.5 - e * U) if hard else 1 - smooth(-0.8, blur, e))
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

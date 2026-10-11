# SPDX-License-Identifier: Apache-2.0
"""고화질 구성표 틀 — 재질 7결(클레이 · 젤리 · 홀로그램 · 선셋 · 오로라 네온 · 갤럭시 · 바우하우스)은 여기,
이펙트 · 애니 20결은 hdfx/ 에 있고 이 틀의 render 고리(warp · extra · 층 paint/glow · LOOP · clip)에 얹는다.
스무 결을 시안으로 뽑아(2026-10-10–11) 사용자가 고른 일곱만 남겼다. 지운 열세 결(글래스 · 크롬 메탈 ·
미드나잇 골드 · 잉크 · 백자 청화 · 청자 · 대리석 · 테라초 · 현무암 · 월넛 · 가죽 · 종이접기 · 청사진)은
b6e4129 에 있다.

픽셀 그림(.txt)이 아니라 거리함수로 256칸 판에 바로 그린다. .txt 는 글자 하나가 색 하나라
그라데이션·하이라이트처럼 색이 수천 개인 그림을 못 담고, 기본 모양은 그 그림을 최근접으로 키워
32 위로는 계단이 그대로 커진다. 여기서는 256 원본을 그리고 크기마다 면적 평균으로 줄인다.

모양은 32칸 판의 한 칸(U = 8px)을 단위로 적는다 — 다른 구성표 그림과 같은 자리·크기 감각.
재질은 거리 d 와 테두리 법선으로 칠한다: 테두리 쪽 밝기·안쪽 테·바깥 번짐. 클레이·홀로그램·젤리는
dome() 으로 테두리 단면에서 법선을 세워 빛을 받고(L3·H3), soft 칸만큼 몸을 부풀리거나 tip_body 로 펜 심을
몸 색으로 칠할 수 있다. 움직임은 frame(0–1) 에 주기로 걸어 고리 이음매가 없다.

빌드가 부른다 — schemes.json 에 "hd": <재질> 을 단 구성표는 art/ 의 txt 없이 build.build_hd 가 칸마다 frames() 장을
그려 dist/<구성표>/<칸>.ani 로 바로 굽는다. 매끈한 모양으로는 안 그린다(classic_only, 다른 모양 탭은 이 그림을 빌림).
이 파일과 hdfx/ 는 빌드 해시에 들어가서 고치면 고화질 27종을 다시 그린다.

    python hd.py <출력 폴더> [재질…]        # 256 PNG 와 견줘 볼 시트 (빌드 없이)

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
    back = (TAU - span) / 2      # 꼬리 뒤(둥근 끝·빛 번짐)는 한 바퀴 넘기지 않고 음수 각으로 — 넘기면 머리만큼 짙어졌다

    def fade(x, y):
        t = clamp(((atan2(y - cy, x - cx) - a0 + back) % TAU - back) / span)
        return (0.12 + 0.88 * t) * min(1.0, t / 0.15)    # 꼬리 첫 15% 는 0 까지 — 12% 에서 끊으면 둥근 끝이 길 위에 턱으로 남았다
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
    # 검지가 손바닥보다 길면 주먹이 아니라 막대에 매달린 손으로 읽힌다(2026-10-11 사용자) — 끝(핫스팟)은
    # 그대로 두고 손을 3칸 올려 검지를 손바닥 높이의 절반쯤으로 줄였다. 그러면 손이 화살표보다 작아져서
    # 끝을 축으로 K 배 키워 전체 높이만 예전(끝에서 아래 끝까지 19칸 남짓)으로 돌린다
    K, ox, oy = 1.15, 9.4, 0.9
    parts = [capsule(9.4, 2.4, 9.4, 8.5, 1.5),                     # 집게손가락
             rbox(12.3, 13.0, 4.7, 4.4, 2.3),                       # 손바닥
             capsule(12.0, 7.6, 12.0, 9.6, 1.4),                    # 접은 손가락 셋
             capsule(14.4, 8.3, 14.4, 10.0, 1.35),
             capsule(16.5, 9.4, 16.5, 10.8, 1.2),
             capsule(7.6, 12.6, 5.4, 9.3, 1.35)]                    # 엄지
    f = smin(0.3, *parts)
    return lambda x, y: K * f(ox + (x - ox) / K, oy + (y - oy) / K)


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
FRAMES = 40       # 움직이는 칸 한 바퀴 장 수 (2026-10-11 사용자)
RATE = 2          # 장마다 1/60초 틱 — 40장 × 2 = 1.33초 한 바퀴
# 몸 색이 흐르는 재질 — 모든 칸이 움직인다. 나머지(클레이·젤리·바우하우스)는 돌기(바쁨·사용 중)만 움직인다
MOVES = {"holo", "sunset", "aurora", "galaxy"}


def animated(style, name):
    """이펙트 결(LOOP 를 단 것)은 17칸이 다 움직인다"""
    return name in ("busy", "wait") or style in MOVES or hasattr(STYLES.get(style), "LOOP")


def frames(style, name):
    """→ (장 수, 장마다 1/60초 틱). 일곱 결은 FRAMES × RATE, 이펙트 결은 제 LOOP(초)를 틱으로 바꿔
    그것을 나누는 2 이상 가장 작은 틱으로 48장 안에 담는다 — 한 바퀴 길이가 시안과 같게(1.6초 → 48장 × 2)"""
    if not animated(style, name):
        return 1, RATE
    loop = getattr(STYLES[style], "LOOP", None)
    if loop is None:
        return FRAMES, RATE
    ticks = round(loop * 60)
    rate = next(r for r in range(2, ticks + 1) if ticks % r == 0 and ticks // r <= 48)
    return ticks // rate, rate


# ---- 재질 ----

WHITE = (1.0, 1.0, 1.0)
LX, LY = -0.6, -0.8           # 빛이 오는 쪽(왼쪽 위)


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


# ---- 2026-10-11 더한 일곱 결 ----
# 움직임은 frame(0..1)에 주기로만 기댄다 — 끝 장에서 첫 장으로 넘어갈 때 튀지 않게

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


# ---- 2026-10-11 오후 — 빛 번짐 없는 결 ----
# 앞 결들이 "죄다 네온에 글로우"라 진부하다는 말에 재료·디자인 말씨로 열 결을 더 뽑았고 바우하우스만 남았다.

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


STYLES = {"clay": Clay(), "jelly": Jelly(), "holo": Holo(), "sunset": Sunset(),
          "aurora": Aurora(), "galaxy": Galaxy(), "bauhaus": Bauhaus()}            # 사용자가 고른 차례


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
    """→ 256×256 미리 곱한 RGBA float 목록 넷, 핫스팟(픽셀).

    이펙트 결(hdfx/)이 쓰는 갈고리 넷 — 없는 결은 예전 길 그대로라 바이트가 같다:
      warp(x, y, frame) → (sx, sy)      화면 자리 (x, y) 에 원래 (sx, sy) 의 모양이 보이게 민다 (글리치·일렁임)
      extra(name, frame, layers, hot)    레이어 목록을 고쳐 돌려준다. 레이어의 paint=함수(x, y, d, nx, ny, frame)
                                         → ((r, g, b), a) 는 body 대신, glow=함수(x, y, d, frame) 는 그 레이어 빛, noglow 는 빛 없음
      glow_n = True                      결의 glow 가 법선도 받는다: glow(x, y, d, warn, frame, nx, ny)
      clip = True                        겹쳐 칠한 값을 1 로 자른다 (빛을 더하는 결이 1 을 넘긴다)
    그리기 전에 st.cell_name 에 칸 이름을 넣어 둔다 (body 가 칸마다 달리 칠할 때)"""
    st = STYLES[style]
    st.cell_name = name
    layers, hot = cell(name, frame, getattr(st, "soft", 0.0), getattr(st, "tip_body", False))
    warp = getattr(st, "warp", None)
    if warp:
        for L in layers:
            L["f"] = (lambda f: lambda x, y: f(*warp(x, y, frame)))(L["f"])
    if hasattr(st, "extra"):
        layers = st.extra(name, frame, layers, hot)
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
    glow_n = getattr(st, "glow_n", False)
    clip = getattr(st, "clip", False)
    for L, d in zip(layers, fields):
        mul = L.get("alpha", 1.0)
        if mul <= 0:
            continue
        fade = L.get("fade")
        warn = L.get("warn", False)
        paint = L.get("paint")
        lglow = L.get("glow")
        if lglow is not None:
            glow = lambda x, y, e, w, fr, nx=0, ny=0, g=lglow: g(x, y, e, fr)      # noqa: E731
        elif L.get("ink") or L.get("noglow"):
            glow = None
        else:
            glow = getattr(st, "glow", None)
        for (px, py), e in d.items():
            cov = clamp(0.5 - e * U)
            if cov <= 0 and (glow is None or e > M):
                continue
            x, y = (px + 0.5) / U, (py + 0.5) / U
            m = mul * (fade(x, y) if fade else 1.0)
            r = g = b = a = 0.0
            nx = ny = 0.0
            if cov > 0 or glow_n:
                gx = d.get((px + 1, py), e) - d.get((px - 1, py), e)
                gy = d.get((px, py + 1), e) - d.get((px, py - 1), e)
                gl = hypot(gx, gy) or 1.0
                nx, ny = gx / gl, gy / gl
            if cov > 0:
                if L.get("ink"):
                    (cr, cg, cb), ca = st.ink, 1.0
                elif paint:
                    (cr, cg, cb), ca = paint(x, y, e, nx, ny, frame)
                else:
                    (cr, cg, cb), ca = st.body(x, y, e, nx, ny, warn, frame)
                ca *= cov * m
                r, g, b, a = cr * ca, cg * ca, cb * ca, ca
            if glow is not None and cov < 1:
                if glow_n and lglow is None:
                    (hr, hg, hb), ha = glow(x, y, max(e, 0.0), warn, frame, nx, ny)
                else:
                    (hr, hg, hb), ha = glow(x, y, max(e, 0.0), warn, frame)
                ha *= (1 - cov) * m
                r, g, b, a = r + hr * ha, g + hg * ha, b + hb * ha, a + ha
            if a > 0.001:
                if clip:
                    over(py * N + px, min(r, 1.0), min(g, 1.0), min(b, 1.0), min(a, 1.0))
                else:
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


def shrink(img, size, src=N):
    """미리 곱한 RGBA(src×src) 를 size 로 면적 평균. 가로 다음 세로."""
    W = weights(src, size)
    res = []
    for ch in img:
        tmp = [0.0] * (size * src)
        for y in range(src):
            row = ch[y * src:(y + 1) * src]
            for x, ws in enumerate(W):
                tmp[y * size + x] = sum(row[j] * w for j, w in ws)
        out = [0.0] * (size * size)
        for x in range(size):
            for y, ws in enumerate(W):
                out[y * size + x] = sum(tmp[j * size + x] * w for j, w in ws)
        res.append(out)
    return res


def sizes(img, want):
    """want 크기마다 줄인 판 {크기: 판}. 256 에서 바로 줄이는 대신 정수 배로 떨어지는 가장 작은 판에서 줄인다 —
    64 는 128 에서, 32 는 64 에서. 면적 평균이라 2배씩 두 번 줄인 것과 4배 한 번이 수식으로 같은 값이다"""
    got = {N: img}
    for s in sorted(want, reverse=True):
        src = min((k for k in got if k % s == 0), default=N)
        got[s] = shrink(got[src], s, src)
    return {s: got[s] for s in want}


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
    import hdfx  # noqa: F401 — spawn 워커도 이펙트 결을 받게
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
    import hd          # 이펙트 결(hdfx)은 모듈 hd 에 등록되므로 __main__ 이 아니라 그쪽으로 돈다
    import hdfx  # noqa: F401
    hd.main()

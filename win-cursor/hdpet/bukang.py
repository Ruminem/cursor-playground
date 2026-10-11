# SPDX-License-Identifier: Apache-2.0
"""부캉이(bukanganim) 고화질 — 치비(머리 큰 통통 상어) · 스티커 채색(굵은 먹선 + 셀 음영 2–3단).

픽셀 부캉이(지운 gen/bukang.py)가 귀여운 까닭(위가 넓적한 종 꼴 머리 · 얼굴 1/3 아래에 낮고 넓게 벌어진 까만 눈 ·
얼굴 폭만 한 U 웃음과 윗니 띠 · 회청색 등에 큰 흰 배)을 HD 로 옮겼다. 칸마다 하는 짓도 픽셀 판 그대로다(물음표 물방울 ·
물 위로 내민 앞모습 손 · 상어 연필 · 물 위를 도는 등지느러미). 사실적 옆모습 상어(시안 v1)는 32px 에서 무서워 접었고,
화살표는 머리 큰 옆모습 상어가 47° 로 서서 뾰족 내민 코끝으로 가리키는 판이다 — 화살표 몸에 얼굴을 넣은 판은 캐릭터가
묻히고, 위에서 본 판은 32px 에서 비행기로 읽혀 접었다(2026-10-11). 손 칸은 핫스팟에 흰 네모 표식을 찍던 것을
머리 위로 살짝 솟은 등지느러미 끝으로 바꿨다(사용자) — 나머지는 핫스팟이 뾰족한 끝이거나 누르는 커서가 아니다.
좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 장면은 NF 장으로 나뉘어 있다.
"""
import math

from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

from . import register

sin, cos, hypot, floor, atan2 = math.sin, math.cos, math.hypot, math.floor, math.atan2


def hx(s):
    return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))


# 픽셀 판 팔레트(지운 gen/bukang.py · 시안 v1) 그대로
OUT, DARK, MID, LIGHT = hx("1b2227"), hx("3d4a52"), hx("5b6b74"), hx("7e8f98")
BELLY, SHADE, GULLET, GUM = hx("eef2f3"), hx("c3ccd1"), hx("7a2430"), hx("e88a93")
ROOT, GRAPH = hx("c9a27a"), hx("2a2f33")
FISH, FISH_L, FISH_D = hx("f28c38"), hx("ffc36b"), hx("c0612a")
HOOD, MASK, GLASS = hx("2c343b"), hx("f2c230"), hx("9ed8ea")
SIGN, SIGN_D = hx("d64541"), hx("9e2b28")
WATER, FOAM, BUB, RIM = hx("7cc4d8"), hx("e8fcff"), hx("3f8fae"), hx("d2dde6")
WHITE = (1.0, 1.0, 1.0)
HOT = {"arrow": (4, 1), "busy": (4, 1), "cross": (13, 13), "hand": (14, 1), "help": (4, 1), "ibeam": (6, 13),
       "move": (7, 12), "nesw": (17, 12), "no": (12, 12), "ns": (16, 15), "nwse": (17, 16), "pen": (0, 29),
       "person": (4, 1), "pin": (4, 1), "up": (11, 1), "wait": (16, 14), "we": (17, 7)}


NF, LOOP = 12, 1.0
LINE = 1.0                         # 먹선 굵기(칸) — 32 로 줄여도 1px 이 남게
CHEEK = hx("f29aa6")               # 볼터치(GUM 보다 조금 밝게)
GREY = (MID, DARK, LIGHT)          # 바탕 · 그늘 · 빛
PALE = (BELLY, SHADE, WHITE)
REDF = (SIGN, SIGN_D, hx("ef7a72"))
SH = (1.45, 1.45)                  # 그늘 띠: 모양을 왼쪽 위로 민 것 밖(= 오른쪽 아래 가장자리)
HI = (1.25, 1.25)                  # 빛 띠: 왼쪽 위 가장자리


# ---- 거리함수 ----

def ell(cx, cy, rx, ry):
    def f(x, y):
        dx, dy = (x - cx) / rx, (y - cy) / ry
        g = hypot(dx, dy) or 1e-9
        gl = hypot(dx / (rx * g), dy / (ry * g)) or 1e-9
        return (g - 1) / gl
    return f


def taper(ax, ay, ra, bx, by, rb):
    """끝마다 반지름이 다른 캡슐(iq sdUnevenCapsule)"""
    ex, ey = bx - ax, by - ay
    h = ex * ex + ey * ey
    b = ra - rb
    cx_, cy_ = math.sqrt(max(h - b * b, 1e-9)), b

    def f(x, y):
        px, py = x - ax, y - ay
        qx = abs(px * ey - py * ex) / h
        qy = (px * ex + py * ey) / h
        k = cx_ * qy - cy_ * qx
        if k < 0:
            return math.sqrt(h * (qx * qx + qy * qy)) - ra
        if k > cx_:
            return math.sqrt(h * (qx * qx + qy * qy + 1 - 2 * qy)) - rb
        return cx_ * qx + cy_ * qy - ra
    return f


def oell(cx, cy, ra, rb, ang):
    """ang 방향으로 ra, 그 수직으로 rb 인 기운 타원"""
    return turn(ell(cx, cy, ra, rb), ang, cx, cy)


def clip_y(f, y0):
    return lambda x, y: max(f(x, y), y - y0)


def inter(f, g):
    return lambda x, y: max(f(x, y), g(x, y))


def cut(f, g):
    return lambda x, y: max(f(x, y), -g(x, y))


def rpoly(pts, r):
    return grow(poly(pts), r)


class Frame:
    """캐논 자세(왼쪽을 보고 선 상어 등) 좌표 ↔ art 좌표. ang 은 화면 시계 방향, flip 은 캐논 x 를 뒤집는다"""

    def __init__(self, ox=0.0, oy=0.0, ang=0.0, s=1.0, flip=False):
        self.ox, self.oy, self.c, self.sn, self.s, self.flip = ox, oy, cos(ang), sin(ang), s, flip

    def loc(self, x, y):
        dx, dy = (x - self.ox) / self.s, (y - self.oy) / self.s
        u, v = dx * self.c + dy * self.sn, -dx * self.sn + dy * self.c
        return (-u if self.flip else u), v

    def w(self, u, v):
        if self.flip:
            u = -u
        return self.ox + (u * self.c - v * self.sn) * self.s, self.oy + (u * self.sn + v * self.c) * self.s

    def place(self, lu, lv, wx, wy):
        """캐논 점 (lu, lv) 가 art 점 (wx, wy) 에 오게 옮긴다"""
        x, y = self.w(lu, lv)
        self.ox += wx - x
        self.oy += wy - y
        return self

    def f(self, g):
        s, loc = self.s, self.loc
        return lambda x, y: s * g(*loc(x, y))

    def col(self, g):
        loc = self.loc
        return lambda x, y: g(*loc(x, y))


# ---- 칠하기: 스티커 ----

def layer(f, paint, glow=True, shadow=True, alpha=1.0, fade=None):
    d = dict(f=f, paint=paint, noglow=not glow, shadow=shadow, alpha=alpha)
    if fade:
        d["fade"] = fade
    return d


def base(*fs):
    """스티커 바닥: 모든 조각의 합집합을 먹색으로 깔고 밝은 바깥 테 · 그림자를 맡는다"""
    u = fs[0] if len(fs) == 1 else union(*fs)
    return layer(u, lambda x, y, e, nx, ny, fr: (OUT, 1.0))


def mix3(a, b, t):
    return tuple(lerp(p, q, t) for p, q in zip(a, b))


def part(f, fam, line=LINE, hi=0.75, sh=1.0):
    """한 조각: 바탕색 + 오른쪽 아래 그늘 띠 + 왼쪽 위 빛 띠 + 먹선. fam 은 셋 또는 (x, y) → 셋"""
    def paint(x, y, e, nx, ny, fr):
        b, s_, h_ = fam(x, y) if callable(fam) else fam
        c = b
        t = smooth(-0.15, 0.15, f(x + SH[0], y + SH[1])) * sh if sh else 0.0
        if t:
            c = lerp(c, s_, t)
        if hi:
            u = smooth(-0.15, 0.15, f(x - HI[0], y - HI[1])) * (1 - t)
            if u:
                c = lerp(c, h_, u * hi)
        return lerp(c, OUT, smooth(line + 0.12, line - 0.12, -e)), 1.0
    return layer(f, paint, glow=False, shadow=False)


def ink(f, col=OUT, a=1.0):
    return layer(f, lambda x, y, e, nx, ny, fr: (col, a), glow=False, shadow=False)


def eye(cx, cy, rx, ry, blink=0.0, hl=1.0):
    """큰 동그란 눈 — 왼쪽 위 큰 반짝 + 오른쪽 아래 작은 반짝(art 좌표, 늘 화면 기준)"""
    if blink > 0.7:                                       # 감은 눈: 아래로 휜 웃는 선
        r = rx * 1.05
        return [ink(arc(cx, cy - 0.35 * r, r, 0.42, 0.45, math.pi - 0.9))]
    ry2 = ry * (1 - 0.75 * blink)
    r1, r2 = 0.42 * rx * hl, 0.2 * rx * hl
    a1x, a1y = cx - 0.32 * rx, cy - 0.36 * ry2
    a2x, a2y = cx + 0.38 * rx, cy + 0.36 * ry2

    def paint(x, y, e, nx, ny, fr):
        c = lerp(hx("2b3a48"), OUT, smooth(-0.6 * ry2, 0.1 * ry2, cy - y))      # 아래가 살짝 푸른 눈
        if blink < 0.4:
            c = lerp(c, WHITE, smooth(r1 + 0.12, r1 - 0.12, hypot(x - a1x, y - a1y)))
            c = lerp(c, WHITE, smooth(r2 + 0.1, r2 - 0.1, hypot(x - a2x, y - a2y)))
        return c, 1.0
    return [layer(ell(cx, cy, rx, ry2), paint, glow=False, shadow=False)]


def blush(cx, cy, rx, ry, a=0.6):
    return layer(ell(cx, cy, rx, ry), lambda x, y, e, nx, ny, fr: (CHEEK, a * smooth(-0.05, -0.45, e)),
                 glow=False, shadow=False)


def blink_of(fr, at=0.75):
    """한 바퀴에 한 번, 한 장만 감는다"""
    k = round(fr * NF) % NF
    return 1.0 if k == round(at * NF) % NF else 0.0


# ---- 옆모습 치비 상어 (캐논: 왼쪽을 봄, 머리 가운데 (0, 0)) ----

NOSE = (-7.6, 0.45)


def snout_tip(L):
    """snout=L 일 때 코끝(캐논) — 뾰족한 코의 맨 끝"""
    return (NOSE[0] - L, NOSE[1])


def chibi(F, ph=0.0, mouth=0.0, blink=0.0, wag=None, flap=None, extra_fins=True, face=True, snout=0.0):
    w = 0.24 * sin(ph) if wag is None else wag
    fl = 0.18 * sin(ph + 1.2) if flap is None else flap
    head = smin(1.6, ell(0, 0, 7.0, 6.0), circle(-4.2, 0.5, 3.3))
    if snout:                                          # 화살표용: 코를 뾰족이 내밀어 코끝이 맨 위·왼쪽 점이 되게
        tu, tv = snout_tip(snout)
        head = smin(0.8, head, taper(-4.6, 0.55, 2.6, tu + 0.35, tv, 0.35))
    body = taper(2.0, 0.3, 5.3, 10.0, -0.5, 2.3)
    tail = turn(smin(0.6, oell(13.1, -3.1, 3.4, 1.75, -0.95), oell(12.3, 1.9, 2.5, 1.4, 0.85)), w, 10.4, -0.5)
    parts = [head, body, tail]
    if extra_fins:
        parts.append(rpoly([(-0.4, -4.6), (4.8, -3.6), (4.0, -9.0)], 1.25))
    sil = smin(1.3, *parts)
    pec = turn(oell(2.6, 5.6, 2.9, 1.65, 1.0), fl, 1.0, 3.8)

    def fam(u, v):
        k = smooth(-0.15, 0.15, v - (1.2 + 0.1 * u)) * smooth(10.5, 9.5, u)
        return mix3(GREY, PALE, k)
    S, P = F.f(sil), F.f(pec)
    out = [base(S, P), part(S, F.col(fam)), part(P, GREY)]
    if not face:
        return out
    ex, ey = F.w(-2.7, -0.55)
    er = 2.4 * F.s
    out += eye(ex, ey, er * 0.93, er * 1.05, blink)
    bx, by = F.w(-1.3, 2.75)
    out.append(blush(bx, by, 1.6 * F.s, 0.95 * F.s))
    out += side_mouth(F, mouth)
    return out


def side_mouth(F, m):
    s = F.s
    if m <= 0.05:                                          # 다문 입: 작은 웃는 호
        cx, cy = F.w(-5.3, 1.65)
        r = 1.2 * s
        a0 = math.pi * 0.15 if not F.flip else math.pi * 0.15
        g = arc(cx, cy, r, 0.3, a0, math.pi * 0.7)
        return [ink(g)]
    dep = (0.7 + 1.5 * m)
    top = 1.9
    shape = F.f(lambda u, v: max(ell(-5.4, top, 1.85, dep)(u, v), top - v))
    tongue = F.f(ell(-5.2, top + dep, 1.2, 0.85))
    tooth = F.f(poly([(-6.5, top - 0.1), (-5.6, top - 0.1), (-6.05, top + 0.8)]))

    def paint(x, y, e, nx, ny, fr):
        c = GULLET
        c = lerp(c, CHEEK, smooth(0.15, -0.15, tongue(x, y)))
        c = lerp(c, WHITE, smooth(0.12, -0.12, tooth(x, y)))
        return lerp(c, OUT, smooth(0.5, 0.3, -e)), 1.0
    return [layer(grow(shape, 0.15), paint, glow=False, shadow=False)]


# ---- 위에서 본 치비 상어 (캐논: 코가 위, 코끝 (0, 0)) ----

def topview(F, ph=0.0, blink=0.0, smile=True, fw=1.0, snout=0.0):
    """코끝 (0, 0), 꼬리가 아래. 꼬리지느러미는 세로 날이라 위에서는 축을 따라 가는 잎꼴로 보인다.
    snout=L 이면 코를 뾰족이 내밀어 코끝이 (0, -L)"""
    sway = 0.2 * sin(ph)
    head = smin(1.6, ell(0, 6.6, 5.6, 6.6), ell(0, 3.0, 3.4, 3.2))
    if snout:
        head = smin(0.8, head, taper(0, 3.2, 2.7, 0, 0.35 - snout, 0.35))
    fins = [rpoly([(sx * 3.6, 8.0), (sx * (3.6 + 5.6 * fw), 14.4 - 1.5 * (1 - fw)), (sx * 4.4, 13.0)], 1.25) for sx in (-1, 1)]
    pel = [oell(-2.6, 17.4, 1.7, 0.9, 2.2), oell(2.6, 17.4, 1.7, 0.9, 0.94)]
    body = turn(taper(0, 11.0, 4.6, 0, 18.4, 1.9), sway * 0.4, 0, 11.0)
    tx, ty = 8.0 * sin(-sway * 0.4), 11.0 + 7.4 * cos(sway * 0.4)
    tail = turn(oell(tx, ty + 3.4, 3.8, 1.2, math.pi / 2), sway, tx, ty)
    sil = smin(1.2, head, body, tail)
    S = F.f(sil)
    FN = F.f(union(*fins, *pel))

    def fam(u, v):                                         # 머리 위가 밝은 얼굴
        k = smooth(4.6, 3.6, hypot(u / 1.2, v - 6.4))
        return mix3(GREY, (LIGHT, MID, hx("a5b4bc")), k)
    out = [base(S, FN), part(FN, GREY), part(S, F.col(fam))]
    for sx in (-1, 1):
        ex, ey = F.w(sx * 2.7, 6.4)
        er = 1.9 * F.s
        out += eye(ex, ey, er * 0.9, er * 1.05, blink)
        bx, by = F.w(sx * 3.4, 9.2)
        out.append(blush(bx, by, 1.25 * F.s, 0.75 * F.s))
    if smile:
        cx, cy = F.w(0, 8.4)
        out.append(ink(arc(cx, cy, 1.05 * F.s, 0.3, math.pi * 0.18, math.pi * 0.64)))
    return out


# ---- 화살표 ----

SNOUT = 2.2
B_TIP = (4.5, 1.45)             # 핫스팟 (4, 1) 칸 가운데 — 테가 판 위 끝 0.5칸 안에 들게


def arrow_shark(fr, s=1.0, mouth=0.0):
    """코끝 상어: 머리 큰 옆모습 상어가 47° 로 서서 뾰족 내민 코끝으로 가리킨다.
    코 길이 2.2 · 47° 면 코끝이 몸의 맨 위 · 맨 왼쪽 점이다 — 둥근 머리가 판 위로 넘지 않게"""
    ph = TAU * fr
    F = Frame(0, 0, math.radians(47), s).place(*snout_tip(SNOUT), *B_TIP)
    return chibi(F, ph, mouth, blink_of(fr), snout=SNOUT)


SMALL = 0.74


# ---- 소품 ----

def bubble(cx, cy, r, line=0.75):
    def paint(x, y, e, nx, ny, fr):
        c = lerp(FOAM, WHITE, smooth(0.32 * r, 0.12 * r, hypot(x - (cx - 0.4 * r), y - (cy - 0.4 * r))))
        return lerp(c, BUB, smooth(line + 0.1, line - 0.1, -e)), 0.95
    return layer(circle(cx, cy, r), paint, shadow=False)


def drop(x, y, r=0.7, col=None):
    def paint(px, py, e, nx, ny, fr):
        return lerp(col or FOAM, BUB, smooth(0.42, 0.2, -e)), 1.0
    return layer(circle(x, y, r), paint, glow=False, shadow=False)


def wave(x0, x1, y, fr, w=0.55, amp=0.35, freq=1.1):
    """물낯 한 줄(둥근 끝 물결)"""
    ph = -TAU * fr

    def f(x, yy):
        xc = min(max(x, x0), x1)
        return hypot(x - xc, yy - (y + amp * sin(freq * xc + ph))) - w

    def paint(px, py, e, nx, ny, frm):
        c = lerp(WATER, FOAM, 0.6 * smooth(0.1, -0.35, py - y))
        return lerp(c, BUB, smooth(0.32, 0.12, -e)), 1.0
    return layer(f, paint, glow=True, shadow=False)


def ripple(x0, x1, y, fr, a=0.5):
    def f(x, yy):
        xc = min(max(x, x0), x1)
        return hypot(x - xc, yy - y) - 0.4
    return layer(f, lambda px, py, e, nx, ny, frm: (WATER, 1.0), glow=False, shadow=False,
                 fade=lambda px, py: a * (0.35 + 0.65 * (0.5 + 0.5 * sin(TAU * (px / 4.0 + fr)))))


def splash(x0, y0, fr, n=4, spread=5.0, height=5.0):
    out = []
    for j in range(n):
        t = (fr + j / n) % 1
        side = -1 if j % 2 else 1
        x = x0 + side * spread * t * (0.6 + 0.4 * (j // 2))
        y = y0 - height * 4 * t * (1 - t)
        out.append(drop(x, y, 0.8 - 0.25 * t, FOAM if t < 0.5 else WATER))
    return out


FIN_PTS = [(-4.0, 0.4), (-2.4, -4.0), (0.9, -6.6), (1.9, -6.4), (1.1, -3.6), (3.9, 0.4)]
# 기다림(물 위를 도는) 지느러미: 끝이 뒷전보다 1.0 → 0.2 칸만 뒤로 넘게 조금 폄(사용자 "너무 구부려짐")
ORBIT_FIN = [(-4.0, 0.4), (-2.3, -4.0), (0.5, -6.6), (1.5, -6.5), (1.3, -3.6), (3.9, 0.4)]


def fin_shape(px, py, s=1.0, d=1.0, pts=FIN_PTS):
    """물 위 등지느러미, 밑동 가운데 (px, py). d=+1 왼쪽으로 헤엄(끝이 오른쪽으로 눕다), 사이 값은 납작"""
    sq = d if abs(d) > 0.25 else (0.25 if d >= 0 else -0.25)
    pts = [(px - sq * x * s, py + y * s) for x, y in pts]
    if sq < 0:
        pts.reverse()
    return rpoly(pts, 0.9 * s)


def fin_layers(px, py, s=1.0, d=1.0, wl=None, extra=None, pts=FIN_PTS):
    f = fin_shape(px, py, s, d, pts)
    if wl is not None:
        f = clip_y(f, wl)
    if extra is not None:
        f = inter(f, extra)
    return [base(f), part(f, GREY)]


def foam(cx, cy, hw, r=0.6, extra=None):
    f = capsule(cx - hw, cy, cx + hw, cy, r)
    if extra is not None:
        f = inter(f, extra)

    def paint(x, y, e, nx, ny, fr):
        return lerp(FOAM, BUB, 0.55 * smooth(0.3, 0.08, -e)), 1.0
    return layer(f, paint, glow=False, shadow=False)


def ellipse_ring(cx, cy, rx, ry, w):
    g = ell(cx, cy, rx, ry)
    return lambda x, y: abs(g(x, y)) - w


def question(cx, cy, s=1.0):
    r, w = 1.6 * s, 0.62 * s
    a0, span = math.pi, math.pi * 1.25
    ex, ey = cx + r * cos(a0 + span), cy + r * sin(a0 + span)
    return union(arc(cx, cy, r, w, a0, span), capsule(ex, ey, cx, cy + 2.2 * s, w), circle(cx, cy + 4.0 * s, w * 1.2))


# ---- 옮기기 ----

def shift(layers, dx, dy):
    """레이어 목록을 통째로 (dx, dy) 옮긴다 — 거리함수 · 칠 · fade 가 다 art 좌표를 받으므로 셋 다"""
    for L in layers:
        f = L["f"]
        L["f"] = lambda x, y, f=f: f(x - dx, y - dy)
        p = L.get("paint")
        if p:
            L["paint"] = lambda x, y, e, nx, ny, fr, p=p: p(x - dx, y - dy, e, nx, ny, fr)
        fd = L.get("fade")
        if fd:
            L["fade"] = lambda x, y, fd=fd: fd(x - dx, y - dy)
    return layers


# ---- 칸마다 장면 (art 좌표) ----

def sc_arrow(fr):
    return arrow_shark(fr)


def sc_help(fr):
    ph = TAU * fr
    out = arrow_shark(fr, SMALL)
    cx, cy = 24.0, 23.2 + 1.0 * sin(ph)
    out.append(bubble(cx, cy, 6.0))
    out.append(ink(question(cx, cy - 1.7, 1.08), hx("2e6f8c")))
    for j in range(2):
        t = (fr + j / 2) % 1
        out.append(bubble(29.0 - 1.6 * j, 15.0 - 6 * t, 1.0 + 0.3 * t, 0.45))
    return out


def orbit(fr, pond, s=1.0):
    cx, cy, rx, ry = pond
    th = TAU * fr + math.pi / 2
    px, py = cx + rx * cos(th), cy + ry * sin(th)
    d = -sin(th)
    out = [layer(ellipse_ring(cx, cy, rx, ry, 0.36 * max(s, 0.75)), lambda *a: (WATER, 1.0), glow=False, shadow=False,
                 alpha=0.45)]

    def trail(x, y):
        a = atan2((y - cy) / ry, (x - cx) / rx)
        dd = (th - a) % TAU
        return clamp(1 - dd / 1.8) if dd > 0.05 else 0.0
    out.append(layer(ellipse_ring(cx, cy, rx, ry, 0.6 * max(s, 0.75)), lambda *a: (WATER, 1.0), glow=False, shadow=False,
                     fade=trail))
    near = (1 + sin(th)) / 2
    fs = s * (0.85 + 0.3 * near)
    wl = py + 0.3 * s
    out += fin_layers(px, wl + 0.2 * s, fs, d, wl=wl, pts=ORBIT_FIN)
    out.append(foam(px, wl + 0.05, 3.2 * fs * max(abs(d), 0.45), 0.6 * max(s, 0.8)))
    return out


def sc_busy(fr):
    return arrow_shark(fr, SMALL) + orbit(fr, (22.9, 26.0, 6.5, 2.6), 0.62)


def sc_wait(fr):
    return orbit(fr, (16.0, 17.0, 12.0, 5.2), 1.15)


def sc_person(fr):
    ph = TAU * fr
    out = arrow_shark(fr, SMALL)
    cx, cy = 23.0, 20.6 + 0.4 * sin(ph)
    body = grow(clip_y(ell(cx, cy + 9.6, 6.2, 4.4), cy + 8.0), 0.8)   # 둥근 어깨 흉상, 아래 모서리도 둥글게 — 판 안
    head = circle(cx, cy, 4.6)
    out += [base(body, head), part(body, (HOOD, hx("1f262c"), hx("46525b"))), part(head, (HOOD, hx("1f262c"), hx("46525b")))]
    mask = rbox(cx, cy + 0.3, 3.4, 1.9, 1.3)
    out.append(part(mask, (MASK, hx("c99a1c"), hx("ffe07a")), line=0.55, hi=0.6))
    glass = rbox(cx, cy + 0.3, 2.35, 0.95, 0.75)

    def gpaint(x, y, e, nx, ny, frm):
        c = lerp(GLASS, WHITE, 0.8 * smooth(0.5, 0.2, abs((x - cx) + (y - cy) * 1.1 + 0.9)))
        return lerp(c, BUB, 0.6 * smooth(0.3, 0.1, -e)), 1.0
    out.append(layer(glass, gpaint, glow=False, shadow=False))
    sx = cx + 5.0
    tube = union(capsule(sx, cy - 6.0, sx, cy + 1.0, 0.75), capsule(sx - 1.2, cy - 6.0, sx, cy - 6.0, 0.75))
    out += [base(tube), part(tube, (MASK, hx("c99a1c"), hx("ffe07a")), line=0.5, hi=0)]
    for j in range(3):
        t = (fr + j / 3) % 1
        out.append(bubble(sx - 1.0 + 0.8 * sin(6 * t + j), cy - 8.5 - 7 * t, 0.8 + 0.4 * t, 0.4))
    return out


def sc_pin(fr):
    out = arrow_shark(fr, SMALL)
    dy = -2.2 * abs(sin(math.pi * fr))
    cx, cy = 24.0, 19.5 + dy
    f = smin(1.0, circle(cx, cy, 5.4), poly([(cx - 4.4, cy + 2.8), (cx + 4.4, cy + 2.8), (cx, cy + 10.2)]))
    out += [base(f), part(f, REDF)]
    fin = rpoly([(cx - 2.6, cy + 2.0), (cx - 0.9, cy - 1.8), (cx + 1.4, cy - 3.0), (cx + 0.6, cy - 0.6), (cx + 2.6, cy + 2.0)], 0.5)
    out.append(part(fin, PALE, line=0.0, sh=0.0, hi=0))
    sq = 1 - 0.25 * abs(sin(math.pi * fr)) ** 6                     # 닿을 때 그림자가 넓어진다
    out.insert(0, layer(ell(cx, 30.2, 3.0 * sq + 0.6, 0.7), lambda *a: (OUT, 0.18), glow=False, shadow=False))
    return out


def fish(fx, fy, ph):
    body = ell(fx, fy, 3.9, 3.4)
    wag = 0.25 * sin(2 * ph)
    tail = turn(rpoly([(fx + 2.8, fy), (fx + 6.2, fy - 3.0), (fx + 6.2, fy + 3.0)], 0.6), wag, fx + 3.0, fy)
    top = rpoly([(fx - 1.2, fy - 2.7), (fx + 1.3, fy - 4.3), (fx + 2.3, fy - 2.4)], 0.4)
    f = smin(0.5, body, tail, top)
    out = [base(f), part(f, (FISH, FISH_D, FISH_L))]
    out += eye(fx - 1.5, fy - 0.6, 1.05, 1.15)
    out.append(ink(arc(fx - 2.6, fy + 0.9, 0.7, 0.24, math.pi * 0.2, math.pi * 0.6)))
    return out


def sc_we(fr):
    ph = TAU * fr
    m = 0.5 + 0.5 * cos(2 * ph)
    F = Frame(0, 0, 0, 0.7).place(0, 0, 17.9 - 0.5 * sin(ph), 8.5)
    return fish(5.6 - 0.3 * sin(ph), 8.9, ph) + chibi(F, ph, m, blink_of(fr, 0.4))


def sc_ns(fr):
    ph = TAU * fr
    b = 1.0 * sin(ph)
    A = Frame(0, 0, -math.pi / 2, 0.7, flip=True).place(0, 0, 9.6, 8.9 - b)
    B = Frame(0, 0, math.pi / 2, 0.7, flip=True).place(0, 0, 22.6, 22.4 + b)
    return chibi(A, ph, 0.0, blink_of(fr, 0.3)) + chibi(B, ph + math.pi, 0.0, blink_of(fr, 0.8))


def sc_nesw(fr):
    ph = TAU * fr
    b = 1.0 * sin(ph)
    F = Frame(0, 0, -math.pi / 4, 0.92, flip=True).place(0, 0, 21.0 + 0.7 * b, 9.0 - 0.7 * b)
    out = chibi(F, ph, 0.6 + 0.4 * sin(ph), blink_of(fr, 0.6))
    wl = 26.0
    for L in out:
        L["f"] = clip_y(L["f"], wl + 0.4) if L is out[0] or L is out[1] else L["f"]
    return out + [wave(2.0, 17.0, wl, fr)] + splash(7.5, 24.5, fr, 4, 5, 4.5)


def sc_nwse(fr):
    ph = TAU * fr
    b = 0.8 * sin(ph)
    F = Frame(0, 0, math.pi / 4, 0.95, flip=True).place(0, 0, 18.6 + b, 17.6 + b)
    out = chibi(F, ph, 0.0, blink_of(fr, 0.2))
    for j in range(4):
        t = (fr + j / 4) % 1
        out.append(bubble(4.0 + 1.0 * sin(7 * t + j), 12.0 - 10 * t, 0.85 + 0.55 * t, 0.42))
    return out


def sc_up(fr):
    ph = TAU * fr
    F = Frame(0, 0, math.pi / 2, 0.98).place(*NOSE, 11.6, 1.45)
    out = chibi(F, ph, 0.55 + 0.35 * cos(ph), blink_of(fr, 0.55))
    wl = 26.5
    out[0]["f"] = clip_y(out[0]["f"], wl + 0.4)
    out[1]["f"] = clip_y(out[1]["f"], wl + 0.4)
    return out + [wave(2.0, 22.0, wl, fr)] + splash(11.5, 25.5, fr, 6, 7, 5)


def sc_pen(fr):
    ph = TAU * fr
    s = 0.93
    F = Frame(0, 0, -math.pi / 4, s)
    F.place(-13.6, 0.35, 0.55, 29.45)
    cone = F.f(rpoly([(-13.3, 0.35), (-6.2, -2.4), (-6.2, 3.1)], 0.3))
    lead = F.f(rpoly([(-13.3, 0.35), (-11.2, -0.45), (-11.2, 1.15)], 0.22))

    def cpaint(x, y, e, nx, ny, frm):
        c = lerp(ROOT, hx("e2c29b"), smooth(-0.2, 0.2, -(y - x) * 0.3 + 0.0) * 0.0)
        c = lerp(ROOT, hx("e9cfa9"), 0.6 * smooth(0.15, -0.15, cone(x + 1.0, y + 1.0)) * 0)
        c = lerp(c, GRAPH, smooth(0.12, -0.12, lead(x, y)))
        return lerp(c, OUT, smooth(LINE * 0.85 + 0.1, LINE * 0.85 - 0.1, -e)), 1.0
    sharkl = chibi(F, ph, 0.0, blink_of(fr, 0.5), wag=0.18 * sin(ph))
    x1 = 3.0 + 22 * (round(fr * NF) + 1) / NF

    def wy(x):
        return 29.6 - 0.5 * sin(x * 0.9)

    def wline(x, y):
        xc = min(max(x, 3.0), x1)
        return hypot(x - xc, y - wy(xc)) - 0.42
    return ([layer(wline, lambda *a: (lerp(WATER, BUB, 0.35), 1.0), shadow=False), base(cone), layer(cone, cpaint, glow=False, shadow=False)]
            + sharkl)


def sc_hand(fr):
    """원본 앞모습: 위가 둥근 종 머리, 낮고 넓게 벌어진 작은 눈, 흰 얼굴 가운데 작은 D 웃음 · 둥근 윗니 둘 · 분홍 혀"""
    ph = TAU * fr
    cx, top, bot = 15.0, 0.75, 24.6               # 그린 뒤 HAND_DY 만큼 내림. 등지느러미 끝이 핫스팟
    g = 0.5 + 0.5 * (0.5 + 0.5 * cos(ph))           # 크게 벌림 → 좁힘 → 다시

    def half(y):                                      # 둥근 지붕(초타원) — 원본처럼 위가 넓적하게 둥글다
        t = clamp((11.35 - y) / (11.35 - top))
        return 10.45 * (1 - t ** 2.3) ** (1 / 2.3)

    ys = [top + 10.6 * (i / 16) ** 2 for i in range(17)] + [bot - 1.2]
    right = [(cx + half(y), y) for y in ys]
    head = poly(right + [(cx + 10.45 - 0.9, bot), (cx - 10.45 + 0.9, bot)] + [(2 * cx - x, y) for x, y in reversed(right[1:])])
    head = smin(0.9, head, rbox(cx, bot - 2.0, 10.45, 2.0, 1.0))
    fins = union(capsule(cx - 9.6, 20.0, cx - 12.2, 22.6, 1.45), capsule(cx + 9.6, 20.0, cx + 12.2, 22.6, 1.45))
    # 등지느러미: 머리 지붕 뒤에서 살짝 솟아 뒤(오른쪽)로 누운 상어 지느러미. 끝이 핫스팟 칸(14, 1)에 든다
    dorsal = rpoly([(12.2, 3.4), (13.3, 0.7), (14.2, -0.6), (15.3, 0.0), (17.9, 3.4)], 0.55)

    def lip(x):                                       # 윗입술 선(회색 모자의 아래 끝): 가운데가 살짝 처진 넓은 M
        d = x - cx
        return 11.35 + 0.55 * math.exp(-d * d / 6.0) - 0.006 * d * d

    def fam(x, y):
        k = smooth(-0.12, 0.12, y - lip(x))
        side = smooth(7.8, 8.8, abs(x - cx)) * k             # 원본처럼 흰 얼굴 양옆에 그늘 기둥
        cap = mix3(GREY, PALE, k)
        return (lerp(cap[0], SHADE, side), cap[1], cap[2])
    out = [base(head, fins, dorsal), part(fins, GREY), part(dorsal, GREY), part(head, fam, hi=0.5)]
    # 입: 흰 얼굴 가운데 작게 벌린 D 웃음(입꼬리가 살짝 올라감) · 작은 윗니 둘 · 분홍 혀. 얼굴 폭만 하던 입은
    # 모자 테두리에 붙어 턱이 통째로 열리는 것처럼 보여서 줄였다. 다물어 이만 남는 장이 없게 늘 벌린 채 숨 쉬듯 오간다
    W, mt = 4.2, 13.0
    dep = 3.1 + 1.2 * g
    us = [i / 10 for i in range(-10, 11)]
    mouth = rpoly([(cx + W * u, mt - 0.6 * u * u) for u in us]
                  + [(cx + W * u, mt - 0.6 * u * u + dep * (1 - u * u) ** 0.6) for u in reversed(us[1:-1])], 0.4)
    tongue = ell(cx + 0.3, mt + dep + 0.1, 2.4, 1.6)

    def mpaint(x, y, e, nx, ny, frm):
        u = (x - cx) / W
        c = GULLET
        tooth = max(0.0, 1 - ((abs(x - cx) - 1.45) / 0.8) ** 2) ** 0.5     # 가운데 양옆으로 둥근 이 둘
        if y < mt - 0.6 * u * u + 0.45 + 1.05 * tooth:
            c = WHITE
        elif tongue(x, y) < 0:
            c = CHEEK
        return lerp(c, OUT, smooth(LINE * 0.8 + 0.12, LINE * 0.8 - 0.12, -e)), 1.0
    out.append(layer(mouth, mpaint, glow=False, shadow=False))
    bl = 1.0 if round(fr * NF) % NF == 7 else 0.0
    for s in (-1, 1):
        out += eye(cx + s * 5.0, 8.6, 1.75, 2.0, bl, hl=0.45)     # 32 에서도 까만 눈이 남게 반짝을 줄임
        out.append(blush(cx + s * 7.0, 14.2 + 0.4 * (g - 0.75) / 0.25, 1.1, 0.7, 0.55))
    wl = 25.9
    out.append(wave(2.2, 27.8, wl, fr, 0.62, 0.2, 1.3))
    out.append(ripple(3.2, 26.8, wl + 1.5, fr, 0.55))
    shift(out, 0.0, HAND_DY)
    return out


HAND_DY = 2.6


def sc_cross(fr):
    ph = TAU * fr
    C, R = 13.5, 9.6
    inner = circle(C, C, R - 0.7)
    wy = 17.5
    out = [layer(inter(lambda x, y: (wy - 0.2) - y, inner), lambda *a: (hx("bfe6f0"), 1.0), glow=False, shadow=False, alpha=0.75)]
    fx = C + 3.5 * sin(ph)
    d = cos(ph)
    out += fin_layers(fx, wy + 0.4, 0.85, d, wl=wy + 0.1, extra=inner)
    out.append(wave(C - R + 1.0, C + R - 1.0, wy, fr, 0.45, 0.2, 1.4))
    out[-1]["f"] = inter(out[-1]["f"], inner)
    E = 11.5                                                   # 선 끝 둥근 마개 + 테가 판 안에 들게(12.6 이면 잘림)
    lines = union(capsule(C, C - 3.6, C, C - E, 0.62), capsule(C, C + 3.6, C, C + E, 0.62),
                  capsule(C - 3.6, C, C - E, C, 0.62), capsule(C + 3.6, C, C + E, C, 0.62))
    rg = ring(C, C, R, 0.68)
    out += [base(lines, rg), ink(union(lines, rg))]
    dot = circle(C + 0.0, C + 0.0, 0.95)
    out.append(part(dot, REDF, line=0.35, hi=0))
    return out


def sc_ibeam(fr):
    """I빔: 위턱(작은 상어 얼굴) · 아래턱이 대를 사이에 두고 냠냠"""
    ph = TAU * fr
    c = 0.9 * smooth(0.2, 0.8, 0.5 + 0.5 * sin(ph))
    cx = 6.5
    up = rbox(cx, 3.4 + c, 5.15, 3.2, 2.4)
    dn = rbox(cx, 23.6 - c, 5.15, 2.4, 1.8)
    stem = capsule(cx, 6.0 + c, cx, 21.0 - c, 0.62)
    out = [base(stem), ink(stem)]
    out += [base(up), part(up, (MID, DARK, LIGHT))]
    tu = union(*[ell(cx + dx, 6.35 + c, 0.75, 0.9) for dx in (-2.3, 2.3)])
    out.append(part(inter(tu, grow(up, -0.5)), PALE, line=0.0, sh=0, hi=0))
    out += [base(dn), part(dn, PALE)]
    td = union(*[ell(cx + dx, 21.4 - c, 0.7, 0.85) for dx in (-1.6, 1.6)])
    out.append(part(inter(td, grow(dn, -0.5)), (WHITE, WHITE, WHITE), line=0.0, sh=0, hi=0))
    bl = 1.0 if round(fr * NF) % NF == 9 else 0.0
    for s in (-1, 1):
        out += eye(cx + s * 2.4, 2.6 + c, 0.95, 1.1, bl)
    out.append(blush(cx, 4.9 + c, 0.9, 0.5, 0.0))
    return shift(out, 0.0, 1.2)                         # 위턱 둥근 테가 판 위로 잘리지 않게(대 가운데는 핫스팟 줄 그대로 지남)


def sc_move(fr):
    ph = TAU * fr
    F = Frame(0, 0, 0, 1.05).place(0, 0, 9.1, 1.9)              # 원본처럼 x 7 줄에 서게 — 지느러미를 접어 판 안에
    return topview(F, ph, blink_of(fr, 0.5), fw=0.45)


def sc_no(fr):
    ph = TAU * fr
    cx, cy, ro, ri = 12.5, 12.5, 11.1, 8.1
    inner = circle(cx, cy, ri)
    wy = cy + 4.0
    lift = 0.5 + 0.5 * cos(ph)
    fx = cx - 1.5 + 1.5 * sin(ph)
    out = [layer(inter(lambda x, y: wy - y, inner), lambda *a: (hx("bfe6f0"), 1.0), glow=False, shadow=False, alpha=0.75)]
    out += fin_layers(fx, wy + 2.4 - 2.4 * lift, 1.0, 1.0, wl=wy + 0.1, extra=inner)
    w = wave(cx - ri, cx + ri, wy, fr, 0.45, 0.2, 1.4)
    w["f"] = inter(w["f"], inner)
    out.append(w)
    k = ri * 0.74
    sign = union(ring(cx, cy, (ro + ri) / 2, (ro - ri) / 2), capsule(cx - k, cy - k, cx + k, cy + k, 1.55))
    out += [base(sign), part(sign, REDF, hi=0.5)]
    return out


SCENE = {"arrow": sc_arrow, "busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "we": sc_we,
         "ns": sc_ns, "nesw": sc_nesw, "nwse": sc_nwse, "up": sc_up, "pen": sc_pen, "hand": sc_hand,
         "cross": sc_cross, "ibeam": sc_ibeam, "move": sc_move, "wait": sc_wait, "no": sc_no}


def scene(name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
    ax, ay = HOT[name]
    return SCENE[name](frame), (ax + 0.5, ay + 0.5)


class Bukang:
    cell = staticmethod(scene)
    M = 1.8
    NF, RATE = NF, round(LOOP * 60) // NF
    LOOP = LOOP                    # 17칸이 다 움직인다(hd.animated). 장 수는 LOOP 가 아니라 NF 로(hdpet.frames)
    shadow = (0.05, 0.09, 0.12, 0.18)
    shadow_off, shadow_blur = (0.35, 0.55), 1.0
    ink = OUT

    def body(self, x, y, d, nx, ny, warn, frame):
        return MID, 1.0

    def glow(self, x, y, d, warn, frame):
        return RIM, 0.95 * smooth(1.05, 0.6, d)          # 판 가장자리 2줄(0.5칸) 안에 들게 좁힘


register("bukang", Bukang())

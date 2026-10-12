# SPDX-License-Identifier: Apache-2.0
"""아기 스피노사우루스(spinoanim) 고화질 — 공룡 틀(dinokit)에 몸빛 · 돛 · 긴 주둥이와 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(지운 gen/dino.py)의 짓 그대로: 화살표 오른쪽 아래에서 긴 주둥이로 날개 끝을 킁킁 · 돛이 오르락(화살표),
물가에서 주둥이를 첨벙 넣어 물고기를 물고 나옴(기다림), 돛을 붉히고 고개를 홱 쳐듦 — 흥(금지).

돛은 등 뒤 한 점(SAIL_B)에서 펼친 부채다 — 빨간 막 + 주황 가시살(그 점 둘레 각도 줄무늬) + 살 끝마다 둥근 물결.
줄무늬를 칠하려면 art → 캐논 셈(F)이 있어야 하는데 Kind.back 은 P 만 받으므로, Kind.body 로 dino() 를 감싸 F 를
붙잡고 body 없는 안쪽 Kind 로 틀 몸을 그린다(dinokit Kind 설명의 길).
"""
from . import catkit, register
from .dinokit import (DF, TAIL_UP, Hide, Kind, DinoPet, Pose, dino, drop, no_sign, arrow_layers, ph_k, puff, zip_lines,
                      circle, ell, base, part, flat, layer, union, poly, turn, lerp, smooth, hx, sin, cos, pi, atan2, OUT,
                      HI, SIGN_D)

SAIL_O = hx("f39a4a")                                    # 가시살(주황) — 막은 deco(빨강)
FISH, FISH_D, FISH_L = hx("9cb6cc"), hx("6a879f"), hx("d4e4ef")
WATER, WATER_D, WATER_L = hx("8fd0ee"), hx("4f9cc8"), hx("dff3fb")

HIDE = Hide(hx("f7c4a0"), hx("dc9a70"), hx("fde8d6"), hx("e8604c"))

SNOUT = (4.4, 1.9, 5.4, 2.5)                             # 길고 낮은 주둥이(끝 u 9.8 — 티라노 8.0)
SAIL_B, SAIL_R = (-4.6, 5.6), 8.0                        # 부채 밑점 · 반지름(캐논). 안쪽은 머리 · 몸이 덮는다
SAIL_A0, SAIL_SPAN = -60.0, 135.0                        # 부채가 펼쳐진 각(도, 화면 기준 — 위가 -90) — -60 에서 위 · 왼쪽을 돌아 -195 까지


def _rad(a):
    return a * pi / 180.0


class Sail(Kind):
    """틀 몸을 그리는 안쪽 생김새 — 돛(back)과 긴 주둥이. F · lift · flush 는 바깥(SpinoKind.body · spino())이 장마다 넣는다"""
    snout = SNOUT
    F, lift, flush = None, 0.0, 0.0

    def back(self, P):
        F, lift, fl = self.F, self.lift, self.flush
        s = F.s if F else 1.0
        bx, by = SAIL_B
        R = SAIL_R + 0.7 * lift
        n = 6 if s >= 0.9 else 5 if s >= 0.65 else 3            # 작으면 살을 줄여 한 살이 판에서 1칸 넘게
        a0, a1 = _rad(SAIL_A0), _rad(SAIL_A0 - SAIL_SPAN)
        # 반평면 둘 — 바깥 법선이 부채 밖(오른쪽 아래 · 아래)을 향한다
        n1 = (cos(a0 + pi / 2), sin(a0 + pi / 2))
        n2 = (cos(a1 - pi / 2), sin(a1 - pi / 2))
        disc = circle(bx, by, R)

        def fan(x, y):
            dx, dy = x - bx, y - by
            return max(disc(x, y), n1[0] * dx + n1[1] * dy, n2[0] * dx + n2[1] * dy)
        rs = max(0.95, 0.75 / s)                                # 살 끝 물결 — 작아도 판에서 0.5칸 넘게
        tips = []
        for i in range(n):
            a = _rad(SAIL_A0 - SAIL_SPAN * (i + 0.5) / n)
            tips.append(circle(bx + cos(a) * (R - rs * 0.35), by + sin(a) * (R - rs * 0.35), rs))
        g = union(fan, inter_fan(tips, fan, bx, by, R + rs))
        memb = lerp(HIDE.deco, SIGN_D, 0.75 * fl)
        spine = lerp(SAIL_O, HIDE.deco, 0.8 * fl)
        step = SAIL_SPAN / n
        wid = 0.34 if n >= 5 else 0.42

        def col(x, y):
            if F is None:
                return memb
            u, v = F.loc(x, y)
            a = (SAIL_A0 - atan2(v - by, u - bx) * 180.0 / pi) % 360.0      # 부채 첫 가장자리에서 잰 각
            t = (a / step) % 1.0
            return spine if abs(t - 0.5) < wid / 2 else memb
        return [(g, col)]


def inter_fan(tips, fan, bx, by, R):
    """살 끝 물결은 부채 둘레 고리 안에서만(밑점 쪽으로 새지 않게)"""
    u = union(*tips)
    return lambda x, y: max(u(x, y), -(((x - bx) ** 2 + (y - by) ** 2) ** 0.5 - R * 0.55))


class SpinoKind(Sail):
    """바깥 생김새 — body 로 dino() 를 감싸 F 를 안쪽(Sail)에 넘긴다. snout 은 콕 칸 핫스팟(snout_tip)이 읽는다"""

    def __init__(self):
        self.inner = Sail()

    def body(self, F, K, **kw):
        self.inner.F = F
        return dino(F, self.inner, **kw)


K = SpinoKind()


def spino(F, lift=0.0, flush=0.0, **kw):
    """돛 들썩 · 붉힘을 이 장에만 — 공용 14칸은 늘 0 으로 그린다"""
    K.inner.lift, K.inner.flush = lift, flush
    try:
        return dino(F, K, **kw)
    finally:
        K.inner.lift, K.inner.flush = 0.0, 0.0


def fish(x, y, ang=0.0, L=2.0):
    """작은 물고기 — 몸 타원 + 꼬리 세모, (x, y) 가 몸 가운데, ang 은 머리 쪽 방향(라디안, 0 이 오른쪽)"""
    bodyf = ell(x, y, L, L * 0.5)
    tail = poly([(x - L * 0.75, y), (x - L * 1.6, y - L * 0.6), (x - L * 1.6, y + L * 0.6)])
    f = turn(union(bodyf, tail), ang, x, y)
    hx_, hy_ = x + cos(ang) * L * 0.5, y + sin(ang) * L * 0.5
    return [base(f), part(f, lambda px, py: lerp(FISH_L, FISH, smooth(y - L * 0.5, y + L * 0.1, py)), shade=FISH_D,
                          ink=hx("4a6278"), line=0.5),
            flat(circle(hx_, hy_ - L * 0.08, max(0.32, L * 0.13)), OUT)]


# ---- 화살표: 날개 끝을 긴 주둥이로 킁킁 ----

def sc_arrow(fr, g):
    """날개 끝 오른쪽 아래에 선 스피노가 왼쪽을 보고 긴 주둥이 끝으로 날개 끝을 킁킁 — 돛이 오르락내리락. 화살표가 맨 위"""
    ph, k = ph_k(fr)
    wx, wy = g["wing"]
    sniff = k % 6 in (2, 3)
    nod = 0.06 if sniff else 0.0
    ang = 0.26 + 0.04 * sin(ph)                         # 몸째 뒤로 젖혀 주둥이가 왼쪽 위(날개 끝)로 — 고개만 들면 머리가 돛을 덮음
    tu, tv = Pose(nod).hp(SNOUT[0] + SNOUT[2], SNOUT[1])         # 주둥이 끝(캐논)
    s = 0.62
    F0 = DF(0.0, 0.0, s, ang, fx=-1)
    tx, ty = F0.w(tu, tv)
    R = SAIL_R + 0.7 + 1.0                                        # 돛 끝(물결 포함)
    right = max(F0.w(SAIL_B[0] + R * cos(a), SAIL_B[1] + R * sin(a))[0]
                for a in (_rad(SAIL_A0 - SAIL_SPAN * i / 8) for i in range(9)))
    bottom = max(F0.w(u, 14.0)[1] for u in (-4.0, 3.3))           # 발바닥
    ox = min(wx + 0.6 - tx, 31.0 - right)                         # 주둥이 끝이 날개 끝 바로 오른쪽 아래 · 돛 끝이 판 안에
    oy = min(wy + 1.0 - ty, 30.6 - bottom)
    F = DF(ox, oy, s, ang, fx=-1)
    out = spino(F, lift=sin(ph), mood="happy" if sniff else "blink" if k == 8 else "open", nod=nod,
                arm=0.6, sway=0.8 * sin(ph), tail_pts=TAIL_UP)
    if sniff:                                            # 킁킁 줄 — 주둥이 끝 둘레(화살표 반대쪽)로
        tx, ty = F.w(tu, tv)
        out += zip_lines(tx, ty, 2, 0.9, 1.2, -pi * 0.3 + 0.15 * (k % 2), 0.9, 0.85)
    return out + arrow_layers(g)


# ---- 기다림: 물가에서 물고기 낚기 ----

DIP = (0, 0.3, 0.7, 1.0, 1.0, 0.6, 0.2, 0, 0, 0, 0, 0)
POND = (10.6, 12.6, 6.6, 3.0)                            # 발 앞 웅덩이(캐논 타원) — 고개를 다 숙이면 주둥이 끝(7.8, 11.1)이 잠김


def pond(F, ph, k):
    """땅 위 타원 웅덩이 — 물빛 + 밝은 물결 줄 둘, 첨벙한 뒤엔 주둥이 자리에 동심 물결. 공룡 위에 칠해 잠긴 주둥이를 가린다"""
    cu, cv, ru, rv = POND
    cx, cy = F.w(cu, cv)
    rx, ry = ru * F.s, rv * F.s
    w = ell(cx, cy, rx, ry)
    out = [base(w), part(w, lambda x, y: lerp(WATER_L, WATER, smooth(cy - ry, cy - ry * 0.2, y)), shade=WATER_D,
                         ink=hx("3d7fa8"), line=0.7)]
    for dx, dy, L in ((-0.25, -0.15, 0.22), (0.3, 0.35, 0.16)):
        x0 = cx + rx * dx + 0.8 * sin(ph)
        out.append(flat(lambda x, y, x0=x0, y0=cy + ry * dy, L=rx * L: max(abs(x - x0) - L, abs(y - y0) - 0.3), HI, 0.85))
    return out


def sc_wait(fr):
    """물가에 선 스피노가 발 앞 웅덩이에 긴 주둥이를 첨벙 넣었다가 물고기를 물고 나와 눈웃음. 물이 공룡 위라 잠긴 주둥이는 안 보임"""
    ph, k = ph_k(fr)
    d = DIP[k]
    s = 0.9
    F = DF(14.4, 16.8, s)
    nod = 1.0 * d
    mood = "squeeze" if d >= 1 else "happy" if 6 <= k <= 9 else "blink" if k == 11 else "open"
    out = spino(F, mood=mood, nod=nod, arm=0.4 + 0.6 * d, sway=0.6 * sin(ph), tail_pts=TAIL_UP)
    out += pond(F, ph, k)
    sx, sy = F.w(7.8, POND[1] - POND[3] + 0.6)            # 첨벙 자리(물낯)
    if k in (4, 5, 6):                                   # 동심 물결
        r = 1.0 + 1.1 * (k - 4)
        out.append(layer(lambda x, y, r=r: abs(ell(sx, sy + 0.4, r * 1.6, r * 0.55)(x, y)) - 0.28,
                         lambda *a: (HI, 1.0), alpha=1.0 - 0.25 * (k - 4)))
    if k in (3, 4, 5):                                   # 첨벙 — 물방울 셋이 튐
        h = (1.6, 3.0, 3.8)[k - 3]
        for dx, r in ((-2.0, 0.6), (0.3, 0.75), (2.4, 0.6)):
            out += drop(sx + dx * (0.7 + 0.35 * (k - 3)), sy - h - (0.7 if r > 0.7 else 0.0), r, r * 1.3)
    if 6 <= k <= 10:                                     # 물고기를 물고 — 파닥
        mx, my = F.w(*Pose(nod).hp(SNOUT[0] + SNOUT[2] - 1.4, SNOUT[1] + 1.6))
        out += fish(mx + 0.4, my + 0.6, ang=0.3 * (1 if k % 2 else -1) + 0.4, L=2.4)
    return out


# ---- 금지: 돛을 붉히고 고개를 홱 ----

TILT = (0.0, -0.04, -0.04, 0.4, 0.36, 0.38, 0.35, 0.38, 0.36, 0.38, 0.2, 0.04)     # 몸째 젖힘 — 3장째에 홱
FLUSH = (0.0, 0.0, 0.2, 0.55, 0.85, 1.0, 1.0, 1.0, 1.0, 0.9, 0.6, 0.25)            # 돛 붉힘(장마다 lerp)


def sc_no(fr):
    """금지 표지 빗금 위쪽(오른쪽 위 반)에서 돛을 장마다 빨갛게 붉히고 몸째 고개를 홱 쳐들어 눈 감고 흥 — 콧김 퐁. 표지가 위.
    고개만 들면 머리가 돛을 덮어 붉힘이 안 보여서 몸째 젖힌다"""
    ph, k = ph_k(fr)
    s = 0.58
    ang = TILT[k]
    F = DF(18.0, 9.4 + 1.6 * ang, s, ang, fx=-1)
    up = ang > 0.3
    out = spino(F, lift=0.8 * FLUSH[k], flush=FLUSH[k], mood="blink" if up else "sad" if k in (1, 2) else "open",
                nod=-0.08 if up else 0.04, arm=0.2, sway=0.5 * sin(ph), tail_pts=TAIL_UP)
    if k in (3, 4, 5):                                   # 콧김
        tx, ty = F.w(SNOUT[0] + SNOUT[2] - 0.6, SNOUT[1] - 1.4)
        out += puff(tx - 0.6 - 0.5 * (k - 3), ty - 0.9 - 0.6 * (k - 3), 0.8 + 0.15 * (k - 3), 0.9)
    return out + no_sign()


class Spino(DinoPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Spino(HIDE, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no})

register("spino", PET)
catkit.load()

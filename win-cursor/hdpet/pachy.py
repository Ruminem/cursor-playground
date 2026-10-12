# SPDX-License-Identifier: Apache-2.0
"""아기 파키케팔로사우루스(pachyanim) 고화질 — 공룡 틀(dinokit)에 몸빛 · 돔 머리 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(지운 gen/dino.py)의 짓 그대로: 화살표 날개 끝을 돔 머리로 콩콩 · 별(화살표), 고개 숙이고 뒷발로 땅 긁기 ·
콧김 퐁퐁 · 앞으로 쏠림(기다림), 금지 빗금을 돔 머리로 콩 · 별(금지).
표식은 머리 위 짙은 보라 돔(머리보다 2.8칸 솟고 양옆으로 살짝 넘침, 앞 위에 반짝 한 점) + 뒤통수 크림 혹 셋 + 짧은 주둥이.
혹은 판에서 반지름이 1.7칸 아래로 줄면 먹 덩어리라 작은 공룡(s < 0.7)에서는 빼고 돔만 남긴다 — 돔은 작아져도 솟은
윤곽과 색 띠로 읽힌다. 크기를 알아야 해서 Kind.body 로 틀 몸을 감싸 s 를 받아 둔다(dinokit Kind 설명).
"""
from . import catkit, dinokit, register
from .dinokit import (DF, TAIL_UP, Hide, Kind, Pose, DinoPet, dino, star, zip_lines, puff, no_sign, arrow_layers, ph_k,
                      ell, circle, capsule, inter, union, grow, flat, hx, sin, hypot, OUT, HI, DUST_D)

HIDE = Hide(hx("c9b2ee"), hx("9f86cc"), hx("eee4fc"), hx("ece2ff"))
DOME, DOME_D = hx("9a7ed2"), hx("7a5fb4")             # 돔(픽셀 판 DOME) · 돔 그늘
KNOB, KNOB_D = hx("fff3d6"), hx("e6d2a8")             # 뒤통수 혹(픽셀 판 CREAM_HORN) · 혹 그늘

HEAD = (0.0, -1.2, 6.6, 6.8)                          # 머리 — 틀(0, 0, 6.6, 5.6)보다 위로 2.4 솟은 둥근 돔 머리(턱 · 눈 자리는 그대로)
DOME_LINE = (-2.6, 0.15)                              # 돔 아래 끝 v = -2.6 + 0.15u(눈 위, 앞이 조금 낮음)
DOME_HIT = (2.6, -7.3)                                # 박을 때 닿는 돔 앞 위 점(캐논)
KNOBS = ((-6.0, -4.8), (-6.9, -2.2), (-6.4, 0.5))     # 뒤통수 혹 자리(픽셀 판 158 · 188 · 218°)


def _below(c, k):
    """v < c + k·u 인 쪽(돔 아래 끝 — 앞이 조금 낮다)의 거리"""
    n = hypot(1.0, k)
    return lambda u, v: (v - c - k * u) / n


class Paint:
    """over 조각의 칠 — 틀은 over 를 몸 그늘(밝은 보라)로 칠해서 돔이 거꾸로 그늘지고 반짝 점에 먹선이 둘린다.
    이 표시를 단 조각만 _part 가 제 그늘(shade) · 먹선 없는 납작 칠(flat)로 바꾼다"""

    def __init__(self, col, shade=None, flat_=False):
        self.col, self.shade, self.flat = col, shade, flat_


def _part(f, col=None, *a, **kw):
    if isinstance(col, Paint):
        return flat(f, col.col) if col.flat else catkit.part(f, col.col, shade=col.shade)
    return catkit.part(f, col, *a, **kw)


class _Pachy(Kind):
    snout = (3.0, 1.8, 3.8, 3.1)                      # 짧은 주둥이(틀 기본 3.6 · 4.4 보다 짧고 뭉툭)
    head = HEAD
    spots = ()                                        # 머리 뒤 무늬 자리를 혹이 쓴다
    s = 1.0

    def over(self, P):
        """돔 — 머리 윗부분을 먹선 안쪽만 납작한 짙은 보라로(배 · 턱처럼 아래 경계엔 먹선 없음) + 앞 위 반짝 한 점"""
        s = self.s
        dome = inter(grow(ell(*HEAD), -max(1.0, 1.0 / s)), _below(*DOME_LINE))
        hr = max(0.8, 0.7 / s)                        # 반짝 — 32 에서도 한 점 남게
        return [(P.hf(dome), Paint(DOME, flat_=True)),
                (P.hf(ell(1.9, -5.9, hr * 1.3, hr * 0.8)), Paint(HIDE.deco, flat_=True))]

    def behind(self, P):
        """뒤통수 혹 셋 — 머리 뒤에 깔아 윤곽이 울퉁불퉁. 판에서 반지름이 1칸 아래면 먹 덩어리라 작은 공룡은 뺀다"""
        if self.s < 0.7:
            return []
        r = max(1.5, 1.0 / self.s)
        return [(P.hf(circle(u, v, r)), Paint(KNOB, KNOB_D)) for u, v in KNOBS]


INNER = _Pachy()


class _Outer(_Pachy):
    def body(self, F, K, **kw):
        """틀 몸을 그대로 쓰되 크기(s)를 over 에 넘기고, 그리는 동안만 dinokit 의 part 를 _part 로 감싼다"""
        INNER.s = F.s
        old, dinokit.part = dinokit.part, _part
        try:
            return dino(F, INNER, **kw)
        finally:
            dinokit.part = old


K = _Outer()


def brows(F, nod, a=0.95):
    """박치기 준비 눈썹 — 눈 위에 앞쪽이 낮은 짧은 먹줄(잔뜩 벼름). 귀엽게 짧게"""
    s = F.s
    P = Pose(nod)
    er = max(1.15 * s, 0.95)
    out = []
    for u, v, k in ((0.2, -0.3, 0.86), (4.0, 0.0, 1.0)):
        ex, ey = F.w(*P.hp(u, v))
        r = er * k
        d = F.fx
        out.append(flat(capsule(ex - d * r * 0.95, ey - r * 1.75, ex + d * r * 0.75, ey - r * 1.15, max(0.26, 0.2 * r)), OUT, a))
    return out


def snort(x, y, r, a=0.95):
    """콧김 퐁 — 흰 동그라미 둘"""
    f = union(circle(x, y, r), circle(x + r * 0.9, y - r * 0.5, r * 0.75))
    return [flat(f, HI, a, line=0.35, ink=DUST_D)]


def place(F_s, fx, nod, tx, ty, pt=DOME_HIT):
    """돔의 닿는 점 pt(캐논)가 (tx, ty) 에 오는 DF 원점"""
    cx, cy = DF(0.0, 0.0, F_s, fx=fx).w(*Pose(nod).hp(*pt))
    return tx - cx, ty - cy


BONK_A = (0, 0, 1, 2, 3, 2, 0, 0, 1, 2, 3, 2)


def sc_arrow(fr, g):
    """날개 끝 오른쪽 아래에 선 파키가 왼쪽을 보고 고개를 숙여 돔으로 날개 끝을 아래에서 콩콩 — 박을 때 질끈 · 줄 · 별.
    박는 장(b 3)에서 돔 앞 위가 날개 끝 바로 밖에 닿게 원점을 정하고, 나머지 장은 땅에 선 채 오른쪽으로 물러나 고개를 든다.
    화살표가 맨 위"""
    ph, k = ph_k(fr)
    b = BONK_A[k]
    s = 0.58
    nod = 0.1 + 0.18 * b
    wx, wy = g["wing"]
    ox, oy = place(s, -1, 0.1 + 0.18 * 3, wx + 0.9, wy + 0.9)
    oy = min(oy, 30.3 - 14.0 * s)                          # 발바닥이 판 안에
    ox = min(ox + (3 - b) * 0.7, 30.0 - 11.3 * s)          # 꼬리 끝(TAIL_UP -9 + 끝 반지름)이 판 안에
    F = DF(ox, oy, s, fx=-1)
    out = dino(F, K, "squeeze" if b == 3 else "open", nod=nod, arm=0.4 + 0.3 * b, step=0.6 if b == 3 else 0.0,
               sway=0.5 * b - 0.6, tail_pts=TAIL_UP)
    if b == 3:
        hx_, hy_ = F.w(*Pose(nod).hp(*DOME_HIT))
        out += zip_lines(hx_, hy_, 3, 1.2, 1.5, -0.6, 0.8)
        out += star(hx_ + 3.6, hy_ - 2.6, 1.8, 0.6)
    return out + arrow_layers(g)


def sc_wait(fr):
    """박치기 준비 — 고개 숙이고 뒷발로 땅을 긁어 먼지 퐁, 콧김 퐁퐁, 끝에 앞으로 쏠림(뒤에 바람 줄)"""
    ph, k = ph_k(fr)
    lean = k in (9, 10)
    s = 1.12
    nod = 0.62 if lean else 0.34
    ox = 15.6 + (1.4 if lean else 0.0)
    oy = 13.4
    F = DF(ox, oy, s)
    step = (-1.6 if k % 4 < 2 else 0.6) if k < 9 else 0.0
    out = []
    if k % 4 == 3 and k < 9:                               # 긁은 뒷발 뒤로 먼지
        px, py = F.w(-6.4, 13.2)
        out += puff(px, py, 1.3, 0.9)
    out += dino(F, K, "squeeze" if lean else "open", nod=nod, step=step, arm=0.2, sway=0.8 * sin(ph))
    if not lean:
        out += brows(F, nod)
    if k % 4 in (1, 2) and k < 9:                          # 콧김
        sn = K.snout
        nx, ny = F.w(*Pose(nod).hp(sn[0] + sn[2] - 0.6, sn[1] - 0.4))
        out += snort(nx + 1.2 + 0.8 * (k % 4 - 1), ny - 0.6 - 0.6 * (k % 4 - 1), 0.85 + 0.25 * (k % 4 - 1))
    if lean:                                               # 쏠림 — 뒤로 바람 줄 셋
        for y in (9.0, 12.6, 16.2):
            out.append(flat(capsule(1.6, y, 4.4, y, 0.4), OUT, 0.85))
    return out


BONK_N = (0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1)


NO_TOP = (0.8, -8.0)                                        # 위로 박을 때 닿는 돔 꼭대기(캐논)
TAIL_CURL = [(-4.8, 9.4), (-7.2, 8.6), (-8.2, 6.0), (-7.4, 3.4)]   # 짧게 말아 올린 꼬리 — 끝이 고리 밖으로 안 나가게


def sc_no(fr):
    """금지 빗금 가운데 바로 밑에 선 파키가 깡충 뛰어 돔 꼭대기로 빗금 아랫변을 콩 — 닿을 때 질끈 · 줄 · 별.
    박는 장(b 3)에 돔이 빗금 아랫변(x = y 에서 아래로 1.35/cos45)에 닿게 원점을 정하고, 나머지 장은 그만큼 내려앉는다.
    발은 고리 아래 띠에 선다. 표지가 위"""
    ph, k = ph_k(fr)
    b = BONK_N[k]
    s = 0.56
    nod = 0.06 * b
    tx = 11.0                                               # 쉬는 장 발바닥(≈ 26.9)이 고리 아래 띠 뒤에 숨는 자리
    ty = tx + 1.35 * 2 ** 0.5 + 0.15                        # 빗금 아랫변
    ox, oy = place(s, 1, 0.06 * 3, tx, ty, NO_TOP)
    F = DF(ox, oy + (3 - b) * 0.5, s)
    out = dino(F, K, "squeeze" if b == 3 else "open", nod=nod, arm=0.4 + 0.5 * b, step=0.5 if b >= 2 else 0.0,
               sway=0.4 * sin(ph), tail_pts=TAIL_CURL)
    if b < 3:
        out += brows(F, nod)
    out += no_sign()
    if b == 3:
        out += zip_lines(tx, ty, 2, 1.1, 1.3, 2.4, 1.3, 0.8)
        out += star(tx - 4.0, ty - 0.6, 1.7, 0.55)
    return out


class Pachy(DinoPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Pachy(HIDE, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no}, hot={"wait": (13, 12)})

register("pachy", PET)
catkit.load()

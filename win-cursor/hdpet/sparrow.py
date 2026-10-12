# SPDX-License-Identifier: Apache-2.0
"""참새(sparrowanim) 고화질 — 새 틀(birdkit)에 깃빛 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(지운 gen/bird.py)의 짓 그대로: 화살표를 머리에 이고 통통(화살표), 땅에 흩어진 모이를 콕콕 — 고개를 숙일
때마다 낟알이 하나씩 사라짐(기다림), 흥 — 고개를 홱 돌리고 눈을 감음, 반 바퀴마다 반대쪽으로 홱 · 그때 꼬리를 탁(금지).
생김새는 갈색 모자 · 흰 볼에 까만 점 · 까만 턱 · 통통한 몸 · 짧은 꼬리. 볼 자리에 까만 점이 있어 분홍 볼은 안 단다.
"""
from . import catkit, register
from .birdkit import (Plume, Kind, BirdPet, bird, bface, beak_layers, stand, at_mid, carry_hop, ell, inter, circle,
                      capsule, oell, chain, hx, base, part, flat, ground, no_sign, ph_k, P_, Frame, sin, cos, pi,
                      radians, TAU)  # noqa: F401

S_CAP, S_BROWN, S_BROWN_D, S_BELLY, S_WHITE = hx("9a5632"), hx("b07c4c"), hx("6e4a30"), hx("e6dfd2"), hx("fbf6ec")
S_BLACK = hx("2f2a33")
PLUME = Plume(S_BROWN, S_BROWN_D, S_BELLY, S_BROWN, hx("5a4a40"), hx("3a2a30"), foot=hx("d0a088"))
SEED, SEED_D = hx("e8c27a"), hx("b08a48")
IN = 1.3          # 테에 닿는 무늬를 덩이 안으로 더 들이는 거리(캐논) — 틀이 0.9 만 들여 먹선이 얇아지는 것을 막음


class SparrowKind(Kind):
    """sw: 꼬리 각(라디안, + 면 끝이 아래로) · lu: 고개 돌린 만큼(캐논) — 볼 점 · 턱이 눈 · 부리와 같이 옆으로"""
    head = (6.8, 6.4)
    body = (7.6, 6.8, 5.2)
    eye = (3.0, 1.0)
    wing_l = 3.2
    foot_x = 2.6
    blush = False

    def __init__(self, sw=0.0, lu=0.0):
        self.sw, self.lu = sw, lu

    def marks(self, hv):
        hrx, hry = self.head
        lu = self.lu
        hd_ = ell(0.0, hv, hrx, hry)
        inner = ell(0.0, hv, hrx - IN, hry - IN)
        face = inter(inner, lambda x, y: (hv - 1.5 + 0.035 * (x - lu) ** 2) - y)       # 모자 선 밑 — 옆으로 갈수록 내려옴
        cap = inter(inner, lambda x, y: y - (hv - 1.5 + 0.035 * (x - lu) ** 2))
        out = [(face, S_WHITE), (cap, S_CAP)]
        for sg in (-1, 1):                                                              # 흰 볼의 까만 점 — 분홍 볼 자리
            out.append((inter(circle(sg * 4.7 + lu * 0.8, hv + 2.9, 1.0), grow_in(hd_)), S_BLACK))
        out.append((ell(lu, hv + 5.1, 1.3, 1.05), S_BLACK))                               # 까만 턱
        return out

    def wing_marks(self, w, rx, ry, a, L, sg):
        c, s = cos(a), sin(a)

        def along(x, y):
            return (x - rx) * c + (y - ry) * s
        return [(lambda x, y: 0.62 * L - along(x, y), S_BROWN_D)]      # 짙은 날개 끝 — 흰 띠까지 넣으면 32 에서 줄무늬 팔

    def tail(self):
        fl = self.body[0] + self.body[2]
        c, s = cos(self.sw), sin(self.sw)
        pts = [(u * c - v * s, fl + u * s + v * c) for u, v in ((2.0, -2.2), (4.6, 0.2), (6.1, 1.3))]
        return [(chain(pts, 1.9, 1.6), S_BROWN_D)]


def grow_in(f):
    return lambda x, y: f(x, y) + IN


K = SparrowKind()


def sc_arrow(fr, g):
    """크림 화살표를 정수리에 이고 통통 — 쪼그렸다가 날개를 들며 폴짝, 뛸 때 꼬리가 살짝 까딱. 화살표가 맨 위. 꼬리는 발바닥 위로 들어 둔다 — 발이 판 밑에 붙어 있어 처지면 잘림"""
    return carry_hop(SparrowKind(-0.38 + 0.07 * sin(TAU * fr)), fr, g)


SEEDS_AT = [(8.6, 27.4), (11.6, 28.5), (21.6, 27.4), (24.6, 28.5), (14.8, 29.4)]
PECK = [0, 0, 1, 2, 1, 0, 0, 0, 1, 2, 1, 0]


def sc_wait(fr):
    """땅에 흩어진 모이를 콕콕 — 고개를 숙일 때마다(몸째 왼쪽으로 기울며 꾹) 낟알이 하나씩 사라진다"""
    ph, k = ph_k(fr)
    p = PECK[k]
    eaten = (1 if k >= 4 else 0) + (1 if k >= 10 else 0)
    out = ground(16.0, 27.2, 6.0, 0.22)
    for i, (x, y) in enumerate(SEEDS_AT):
        if i < eaten:
            continue
        sd = oell(x, y, 1.05, 0.72, -0.35 if i % 2 else 0.3)
        out += [base(sd), part(sd, SEED, shade=SEED_D, ink=hx("7e5230"), line=0.5)]
    F = stand(SparrowKind(-0.12 * p), 16.0, 26.6, 0.78, radians(-7.0 * p))
    out += bird(F, SparrowKind(-0.12 * p), "happy" if p == 2 else "open", beak=0.8 if k in (5, 11) else 0.0, sq=0.8 * p)
    return out


def sulk_face(F, K_, look, hv=0.0):
    """흥 — 감은 눈이 바깥이 높고 안쪽이 낮은 짧은 빗금(픽셀 sulk). 부리는 공용"""
    s = F.s
    C = P_()
    er = max(1.0 * s, 0.9)
    ex, ey = K_.eye
    lu = 0.9 * look
    out = []
    for sg in (-1, 1):
        x, y = F.w(sg * ex + lu, ey + hv)
        g = capsule(x + sg * er * 0.85, y - er * 0.4, x - sg * er * 0.75, y + er * 0.35, max(0.3, 0.24 * er))
        out.append(flat(g, C.eye))
    return out + beak_layers(F, K_, 0.0, lu, hv)


def sc_no(fr):
    """흥 — 고개를 홱 돌리고 눈을 감는다. 반 바퀴마다 반대쪽으로 홱, 그때 꼬리를 탁 · 반대쪽에 휙 줄. 표지가 위"""
    ph, k = ph_k(fr)
    side = -1 if k < 6 else 1
    snap = k in (0, 6)
    look = side * (1.6 if snap else 2.6)
    Kn = SparrowKind(-side * (0.3 if snap else 0.1), 0.9 * look)
    F = at_mid(Kn, 14.5, 15.2, 0.7, radians(side * (3.0 if snap else 6.0)))
    out = bird(F, Kn, face_on=False)
    out += sulk_face(F, Kn, look)
    if snap:                                                       # 홱 — 돌린 반대쪽에 짧은 줄 셋
        x0 = 23.6 if side < 0 else 5.6
        for y in (9.6, 11.6, 13.6):
            out.append(flat(capsule(x0, y, x0 + 1.8, y, 0.32), catkit.C.out, 0.9))
    return out + no_sign()


class Sparrow(BirdPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Sparrow(PLUME, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no})

register("sparrow", PET)
catkit.load()

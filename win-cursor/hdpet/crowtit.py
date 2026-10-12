# SPDX-License-Identifier: Apache-2.0
"""뱁새(crowtitanim) 고화질 — 새 틀(birdkit)에 깃빛 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(지운 gen/bird.py)의 짓 그대로: 화살표를 머리에 이고 통통(화살표), 가지 끝에 앉아 가지째 살랑살랑 —
긴 꼬리가 반대로 흔들림(기다림), 도리도리 세차게 고개를 흔들고 긴 꼬리를 탁탁(금지).
생김새는 붉은 갈색 머리 · 연한 목 · 갈색 동그란 몸 · 아주 작은 부리 · 몸보다 긴 꼬리. 분홍 볼은 픽셀 화살표 칸처럼 단다.
꼬리는 픽셀보다 눕혔다 — 픽셀 그대로면 발보다 4칸 아래로 처져 화살표 칸 · 깡충 칸에서 판 밑으로 나간다.
"""
from . import catkit, register
from .birdkit import (Plume, Kind, BirdPet, bird, at_mid, stand, carry_hop, ell, inter, capsule, oell, chain, taper,
                      union, hx, base, part, flat, ph_k, no_sign, WOOD, WOOD_D, LEAF, LEAF_D, sin, cos, radians, TAU)

T_HEAD, T_BODY, T_BELLY, T_WING, T_TAIL = hx("c27a4e"), hx("c99a72"), hx("f1dcc0"), hx("9a6a46"), hx("8a6244")
PLUME = Plume(T_BODY, T_WING, T_BELLY, T_WING, hx("5a4a44"), hx("5a4a44"), foot=hx("8a7a70"))
IN = 1.3          # 테에 닿는 무늬를 덩이 안으로 더 들이는 거리(캐논) — 틀이 0.9 만 들여 먹선이 얇아지는 것을 막음


class CrowtitKind(Kind):
    """sw: 꼬리 각(라디안, + 면 끝이 아래로)"""
    head = (7.0, 6.6)
    body = (7.0, 6.6, 5.2)
    eye = (3.0, 1.1)
    beak_y = 2.7
    bw, bh = 1.0, 1.1
    wing_l = 2.8
    tl = 0.85         # 꼬리 길이 배 — 1 이면 글자 칸에서 판 오른쪽에 닿음. 0.85 로도 몸보다 긺

    def __init__(self, sw=0.0):
        self.sw = sw

    def marks(self, hv):
        hrx, hry = self.head
        inner = ell(0.0, hv, hrx - IN, hry - IN)
        return [(inner, T_HEAD), (inter(inner, ell(0.0, hv + 5.4, 3.6, 3.0)), T_BELLY)]     # 붉은 머리 · 연한 목

    def wing_marks(self, w, rx, ry, a, L, sg):
        c, s = cos(a), sin(a)
        return [(lambda x, y: 0.72 * L - ((x - rx) * c + (y - ry) * s), T_TAIL)]         # 날개 끝은 꼬리 색

    def tail(self):
        fl = self.body[0] + self.body[2]
        c, s = cos(self.sw), sin(self.sw)
        L = self.tl
        pts = [(u * c - v * s, fl + u * s + v * c) for u, v in ((2.4, -2.4), (6.4 * L, -0.2), (10.0 * L, 1.7 * L), (12.2 * L, 2.7 * L))]
        return [(chain(pts, 1.8, 1.55), T_TAIL)]          # 굵기를 끝까지 고르게 — 가늘게 빠지면 32 에서 쥐꼬리


K = CrowtitKind(-0.12)    # 공용 칸도 꼬리를 조금 든다 — 그대로면 위 칸에서 긴 꼬리가 판 밑으로 나감


def sc_arrow(fr, g):
    """크림 화살표를 정수리에 이고 통통 — 몸을 조금 부풀린 채, 긴 꼬리가 살짝 까딱. 화살표가 맨 위. 꼬리는 발바닥 위로 들어 둔다 — 발이 판 밑에 붙어 있어 처지면 잘림"""
    return carry_hop(CrowtitKind(-0.34 + 0.06 * sin(TAU * fr)), fr, g, puff=1.05)


PIV = (3.4, 27.6)


def sc_wait(fr):
    """가지 끝에 앉아 가지째 살랑살랑 흔들 — 긴 꼬리가 반대로 흔들리고 날개가 번갈아 살짝 들린다. 한 번 끔뻑"""
    ph, k = ph_k(fr)
    sw = 6.0 * sin(ph)
    a = radians(-14.0 + 0.5 * sw)
    c, s = cos(a), sin(a)

    def at(u, v):
        return PIV[0] + u * c - v * s, PIV[1] + u * s + v * c
    end = at(25.0, 0.0)
    br = taper(*PIV, 1.3, *end, 0.8)
    tw0, tw1 = at(19.0, -0.4), at(22.0, -3.4)                       # 잎 달린 잔가지
    twig = taper(*tw0, 0.55, *tw1, 0.4)
    leaf = union(oell(*at(22.6, -4.4), 1.9, 0.95, a - 0.9), oell(*at(25.6, -1.2), 1.8, 0.9, a + 0.4))
    wood = union(br, twig)
    out = [base(wood, leaf), part(wood, WOOD, shade=WOOD_D, ink=hx("5a3a20"), line=0.8),
           part(leaf, LEAF, shade=LEAF_D, ink=hx("3f7a32"), line=0.5)]
    px, py = at(12.0, -1.0)
    Kw = CrowtitKind(-0.25 * sin(ph))
    F = stand(Kw, px, py, 0.72, radians(sw * 0.6))
    out += bird(F, Kw, "blink" if k == 5 else "open", wl=(("fold", "out"), 0.4 * max(0.0, -sin(ph))),
                wr=(("fold", "out"), 0.4 * max(0.0, sin(ph))))
    return out


def sc_no(fr):
    """도리도리 세차게 고개를 흔들고 긴 꼬리를 탁탁 — 장마다 좌우, 눈 질끈, 흔드는 반대쪽에 휙 줄. 표지가 위"""
    ph, k = ph_k(fr)
    sd = 1 if k % 2 == 0 else -1
    Kn = CrowtitKind(0.3 * sd)
    F = at_mid(Kn, 13.8, 15.4, 0.66, radians(5.0 * sd))
    out = bird(F, Kn, "squeeze", look=1.6 * sd)
    x0 = 6.6 if sd > 0 else 21.0
    for y in (8.6, 10.8):
        out.append(flat(capsule(x0, y, x0 + 2.0, y, 0.32), catkit.C.out, 0.9))
    return out + no_sign()


class Crowtit(BirdPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Crowtit(PLUME, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no})

register("crowtit", PET)
catkit.load()

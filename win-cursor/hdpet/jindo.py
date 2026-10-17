# SPDX-License-Identifier: Apache-2.0
"""진돗개(jindoanim) 고화질 — 댕댕이 틀(dogkit)에 털빛 · 생김새 · 기다림 · 금지 두 칸만 얹는다.

시바와 가르는 것: 온몸 흰 백구(시바는 주황 + 흰 주둥이) · 더 크게 곧추선 세모 귀 · 등 위 흰 말린 꼬리.
픽셀 판(gen/dog.py)의 짓 그대로: 똑바로 앉아 경계 — 귀가 번갈아 쫑긋, 눈이 좌우를 살피다 '!'(기다림),
금지 표지 앞에서 귀를 뒤로 젖히고 몸을 낮춰 으르렁 — 이빨 대신 찡그린 눈 · 머리 위 화난 표시(금지).
"""
from . import catkit, register
from .dogkit import (Fur, Kind, DogPet, Frame, dog, no_sign, marks, ph_k, base, flat, part, arc, capsule, circle, union,
                     SIGN, SIGN_D, SIGN_L, RIM_GREY, sin, pi)

FUR = Fur(catkit.hx("f8f1e4"), catkit.hx("ddd2c0"), catkit.hx("fffdf8"), catkit.hx("fff4e8"), rim=RIM_GREY)   # 흰 백구(시안 D)


class JindoKind(Kind):
    ear, ear_s, tail, mouth = "prick", 1.15, "curl", "pant"
    snout = 1.1


K = JindoKind()


def bang(x, y, a=1.0):
    """'!' — 빨간 막대 + 점"""
    g = union(capsule(x, y - 2.6, x + 0.2, y + 0.4, 0.75), circle(x + 0.25, y + 2.2, 0.8))
    return [base(g), part(g, SIGN_L if a < 1 else SIGN, shade=SIGN_D, ink=SIGN_D, line=0.55, sh=0.0)]


def vein(x, y, k=1.0):
    """화난 표시 — 네 귀퉁이를 바깥으로 휜 활 넷(💢)"""
    r = 1.15 * k
    g = union(*[arc(x + dx * 1.75 * k, y + dy * 1.75 * k, r, 0.36 * k, a0, pi / 2)
                for dx, dy, a0 in ((-1, -1, 0.0), (1, -1, pi / 2), (1, 1, pi), (-1, 1, pi * 1.5))])
    return [flat(g, SIGN, line=0.0)]


def sc_wait(fr, K=K):
    """똑바로 앉아 경계 — 귀가 번갈아 쫑긋, 눈이 왼쪽 · 오른쪽을 살피다 마지막 네 장에 '!'"""
    ph, k = ph_k(fr)
    s = 0.86
    F = Frame(14.8, 12.8, s)
    look = (-1.0, -1.0, -1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)[k]
    alert = k >= 8
    fl = (-0.35, 0.0) if k % 4 < 2 else (0.0, -0.35)               # 귀 끝을 안으로 — 쫑긋
    out = dog(F, K, "open", mouth="none" if alert else None, look=look, flap=(-0.45, -0.45) if alert else fl,
              wag=0.4 * sin(ph), bob=-0.5 if alert else 0.0)
    if alert:
        out += bang(26.0, 4.4 - (0.6 if k == 8 else 0.0))
    return out


def sc_no(fr, K=K):
    """금지 표지 앞에서 으르렁 — 귀를 뒤로 젖히고 몸을 낮춰 찡그린 눈 · 앙다문 입, 머리 위 화난 표시가 두근.
    개가 표지 위다(시바와 같은 까닭)"""
    _, k = ph_k(fr)
    beat = 1.0 if k % 4 in (0, 1) else 0.82
    s = 0.7
    F = Frame(15.0, 13.0 + 0.4 * beat, s)
    out = no_sign()
    out += dog(F, K, "sulk", mouth="flat", flap=(0.55, 0.55), bob=0.8, wag=0.0, look=0.0)
    out += vein(*F.w(5.6, -7.2), beat)
    if k % 4 in (0, 1):
        out += marks([F.w(-8.6, 1.2) + F.w(-10.4, 0.6), F.w(8.6, 1.2) + F.w(10.4, 0.6)])
    return out


class Jindo(DogPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Jindo(FUR, K, {"wait": sc_wait, "no": sc_no})

register("jindo", PET)

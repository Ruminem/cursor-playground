# SPDX-License-Identifier: Apache-2.0
"""시바(shibaanim) 고화질 — 댕댕이 틀(dogkit)에 털빛 · 생김새 · 기다림 · 금지 두 칸만 얹는다.

픽셀 판(gen/dog.py)의 짓 그대로: 공을 물고 말린 꼬리를 프로펠러처럼 뱅글뱅글 · 눈웃음(기다림),
금지 표지 안에서 산책 거부 — 목줄이 왼쪽 위로 당겨도 앞발을 내밀어 버팀 · 흥(금지).
"""
from . import catkit, register
from .dogkit import (Fur, Kind, DogPet, Frame, dog, ball, no_sign, marks, ph_k, chain, base, flat, part, arc, ell, union,
                     H, LEASH, LEASH_D, MARK, TAU, sin)

FUR = Fur(catkit.hx("e0893a"), catkit.hx("b8692a"), catkit.hx("fff4e4"), catkit.hx("fff0dc"))


class ShibaKind(Kind):
    ear, tail, mouth = "prick", "curl", "pant"                  # 벌린 입 + 혀 — 고양이 · 여우는 입을 안 벌린다

    def marks(self):
        """우라지로 — 주둥이 둘레만. 볼까지 번지면 32 에서 흰 수염(여우)이고, 눈썹 점은 32 에서 안 남아 뺐다"""
        return [(union(ell(-2.4, 3.2, 2.2, 1.6), ell(2.4, 3.2, 2.2, 1.6)), H().light)]


K = ShibaKind()


def sc_wait(fr):
    """공을 물고 말린 꼬리를 프로펠러처럼 뱅글뱅글 — 둘레에 바람 고리, 눈웃음"""
    ph, k = ph_k(fr)
    s = 0.86
    F = Frame(14.6, 12.6, s)
    a = 2 * TAU * fr
    out = dog(F, K, "happy", mouth="none", spin=a, bob=0.4 * abs(sin(2 * ph)))
    cx, cy = F.w(4.2, 9.4)
    for i in range(2):                                           # 바람 고리
        out.append(flat(arc(cx, cy, 6.6 + 1.2 * i, 0.3, a + 2.2 * i, 1.1), MARK, 0.85 - 0.25 * i))
    bx, by = F.w(0.0, 4.6)
    return out + ball(bx, by, 2.3, ph)


def sc_no(fr):
    """금지 표지 앞에서 산책 거부 — 고리 밖 왼쪽 위로 목줄이 당기면 뒤로 버티며 고개를 돌림, 흥. 당길 때 움직임 줄.
    개가 표지 위다 — 표지를 위에 칠하니 빗금과 그 바깥 테가 개를 반쯤 지웠다"""
    ph, k = ph_k(fr)
    pull = 1.0 if k % 6 in (1, 2, 3) else 0.0
    s = 0.66
    F = Frame(16.4 + 0.5 * pull, 11.6, s)
    nx, ny = F.w(-1.0, 5.4)
    sag = 1.4 * (1 - pull)
    end = (2.8, 4.8)
    pts = [(nx + (end[0] - nx) * t, ny + (end[1] - ny) * t + sag * sin(3.1416 * t)) for t in (0.0, 0.33, 0.66, 1.0)]
    ls = chain(pts, 0.7)
    out = no_sign() + [base(ls), part(ls, LEASH, shade=LEASH_D, ink=LEASH_D, line=0.5, sh=0.0)]   # 줄은 턱 밑으로 들어간다
    out += dog(F, K, "sulk", mouth="flat", tilt=0.22 + 0.1 * pull, look=0.6, wag=0.0)
    if pull:
        out += marks([F.w(7.4, 1.0) + F.w(9.4, 1.6), F.w(7.6, 5.4) + F.w(9.6, 5.8)])
    return out


class Shiba(DogPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Shiba(FUR, K, {"wait": sc_wait, "no": sc_no}, hot={"wait": (14, 16)})

register("shiba", PET)
catkit.load()

# SPDX-License-Identifier: Apache-2.0
"""카나리아(canaryanim) 고화질 — 새 틀(birdkit)에 깃빛 · 생김새 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(지운 gen/bird.py)의 짓 그대로: 화살표를 머리에 이고 통통(화살표), 나뭇가지에 앉아 고개를 좌우로 흔들며 노래 —
부리를 벌릴 때마다 음표가 하나씩 솟아 흩어짐(기다림), 노래 안 해 — 날개로 부리를 꾹 가리고 고개를 돌림, 옆에 빗금 그은
음표(금지). 병아리 · 아기오리보다 진한 노랑에 머리가 작고 몸이 늘씬하며, 날개 끝 주황 줄 · 주황 꽁지가 표식이다.
"""
from . import catkit, register
from .birdkit import (Plume, Kind, BirdPet, bird, at_mid, stand, carry_hop, chain, inter, circle, hx, no_sign, ph_k, base, part,
                      layer, capsule, oell, union, WOOD, WOOD_D, LEAF, LEAF_D, OUT, sin, cos, pi, atan2, hypot)

Y_YEL, Y_YEL_L, Y_ORA, Y_OLIVE = hx("fcce1a"), hx("ffe466"), hx("f2a21a"), hx("c8a020")
PLUME = Plume(Y_YEL, Y_OLIVE, Y_YEL_L, Y_YEL, hx("f6c0a8"), hx("d89a84"), foot=hx("e8b0a0"))
NOTE = (hx("f07c9c"), hx("6aa8e0"), hx("8cc864"))


class CanaryKind(Kind):
    head = (6.1, 5.9)
    body = (8.1, 5.5, 5.6)         # 머리가 작고 몸이 세로로 긴 늘씬한 새
    eye = (2.8, 0.8)
    beak_y = 2.4
    bw, bh = 1.3, 1.5
    wing_l, wing_w = 3.6, 1.8

    def wing_marks(self, w, rx, ry, a, L, sg):
        """날개 끝 주황 줄 — 밑동에서 45–78% 자리, 그 너머 끝은 올리브"""
        c, s = cos(a), sin(a)

        def t(x, y):
            return ((x - rx) * c + (y - ry) * s) / L
        return [(lambda x, y: (abs(t(x, y) - 0.62) - 0.17) * L, Y_ORA), (lambda x, y: (0.79 - t(x, y)) * L, Y_OLIVE)]

    def tail(self):
        """몸 뒤 오른쪽 아래로 뻗은 꽁지 — 밑동은 주황, 끝은 올리브"""
        bv, brx, bry = self.body
        pts = [(1.2, bv + 1.6), (3.8, bv + bry - 0.4), (brx + 0.9, bv + bry + 0.8)]
        f = chain(pts, 1.7, 1.2)
        return [(f, Y_ORA), (inter(f, circle(pts[2][0] + 0.6, pts[2][1] + 0.6, 2.0)), Y_OLIVE)]


K = CanaryKind()


def sc_arrow(fr, g):
    """크림 화살표를 정수리에 이고 통통 — 쪼그렸다가 날개를 들며 폴짝. 화살표가 맨 위"""
    return carry_hop(K, fr, g)


def note(x, y, col, a=1.0, h=4.2):
    """♪ 음표 — 머리(기운 타원) 가운데 (x, y), 기둥이 위로 h, 꼭대기에서 오른쪽 아래로 깃발.
    먹선을 가늘게 둬야 32 에서 색이 남는다(0.55 면 까만 콩나물로 읽혔다)"""
    head = oell(x, y, 1.5, 1.1, -0.45)
    sx = x + 1.15
    stem = capsule(sx, y - 0.2, sx, y - h, 0.42)
    flag = capsule(sx, y - h, sx + 1.7, y - h + 1.8, 0.48)
    f = union(head, stem, flag)
    out = [base(f), part(f, col, shade=col, line=0.36, sh=0.0)]
    for L in out:
        L["alpha"] = a
    return out


PERCH_Y = 26.6


def perch():
    """가로 나뭇가지 하나 + 왼끝 잎 하나"""
    br = capsule(3.2, PERCH_Y + 0.9, 25.6, PERCH_Y + 0.9, 1.05)
    leaf = oell(4.6, PERCH_Y - 0.7, 1.6, 0.8, -0.6)
    return [base(br, leaf), part(br, WOOD, shade=WOOD_D, ink=hx("5a3a20"), line=0.8),
            part(leaf, LEAF, shade=LEAF_D, ink=hx("3f7a32"), line=0.5)]


def sc_wait(fr):
    """가지에 앉아 고개를 좌우로 흔들며 노래 — 부리를 벌린 두 장마다 음표가 하나씩 솟아 흔들리며 옅어진다"""
    ph, k = ph_k(fr)
    out = perch()
    sing = k % 4 < 2
    F = stand(K, 13.0, PERCH_Y + 0.2, 0.8)
    out += bird(F, K, "happy" if sing else "blink" if k == 7 else "open", beak=0.9 if sing else 0.0,
                look=0.7 * sin(ph), sq=-0.35 if sing else 0.15)
    for i in range(3):                                         # 음표 셋 — 부리 오른쪽에서 솟아 위로 흩어짐
        t = ((k + i * 4) % 12) / 12
        nx = 18.6 + i * 3.4 + 1.0 * sin(2 * pi * t + i)
        ny = 18.0 - 12.5 * t
        out += note(nx, ny, NOTE[i], min(1.0, (1 - t) * 3.0))
    return out


def sc_no(fr):
    """노래 안 해 — 오른 날개로 부리를 꾹 가리고 눈을 감은 채 고개를 홱 돌린다. 오른쪽 위에 빗금 그은 음표. 표지가 위"""
    ph, k = ph_k(fr)
    look = -0.9 if k < 6 else -0.45
    F = at_mid(K, 14.2, 15.2, 0.7)
    bv, brx, bry = K.body
    rx_, ry_ = brx * 0.72, bv - bry * 0.3                     # 오른 어깨(bird 의 날개 밑동과 같은 자리)
    tx, ty = 0.9 * look, K.beak_y + 0.2                       # 부리
    a = atan2(ty - ry_, tx - rx_)
    lm = (hypot(tx - rx_, ty - ry_) + 0.4) / K.wing_l
    out = bird(F, K, "blink", look=look, wl="fold", wr=("aim", a, lm, True))
    j = k % 2
    out += note(20.6, 9.4 + j * 0.4, NOTE[0])
    slash = capsule(18.4, 10.6 + j * 0.4, 24.4, 4.6 + j * 0.4, 0.45)
    out += [base(slash), layer(slash, lambda *_: (OUT, 1.0))]
    return out + no_sign()


class Canary(BirdPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Canary(PLUME, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no})

register("canary", PET)
catkit.load()

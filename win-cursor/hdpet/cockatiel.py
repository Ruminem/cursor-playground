# SPDX-License-Identifier: Apache-2.0
"""왕관앵무(cockatielanim) 고화질 — 새 틀(birdkit)에 깃빛 · 생김새 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(gen/bird.py)의 생김새 그대로: 회색 몸 · 밝은 회색 배 · 노란 얼굴에 주황 볼 · 머리 뒤로 솟은 노란 볏 깃 셋 ·
짙은 회색 날개 바깥 가운데에 흰 띠 · 갈고리 부리(코 없음) · 길고 짙은 회색 꼬리. 짓도 그대로: 볏을 뒤로 눕혀 화살표
날개를 비키고 통통(화살표), 횃대에 앉아 볏을 천천히 올렸다 내림 — 다 서면 눈이 동그래지고 볼이 빛나고 느낌표(기다림),
볏을 바짝 세우고 날개를 쫙 펴 쉭쉭 — 볼이 빨갛게 달아오름(금지).

볏 높이는 칸마다 달라서 생김새를 볏마다 따로 만든다(CockKind(crest)). 공용 14칸은 픽셀 판 기본처럼 반쯤 선 볏(0.5).
주황 볼이 틀의 분홍 볼 자리(눈 바로 밑 바깥)를 맡아 분홍 볼은 끈다 — 둘을 같이 두면 32 에서 한 덩이 주황 얼룩이 된다.
갈고리 부리는 사랑앵무와 같은 꼴이지만 사랑앵무 모듈을 읽으면 일감 해시가 엮이므로(build._pet_files) 여기 따로 둔다.
"""
from functools import lru_cache

from . import birdkit, catkit, register
from .birdkit import (Plume, Kind, BirdPet, bird, stand, at_mid, carry_hop, beak_layers, P_, OUT, MOUTH, WOOD, WOOD_D,
                      SIGN, ell, circle, capsule, inter, chain, rpoly, base, part, flat, soft, lerp, hx, no_sign, ph_k,
                      sin, cos, pi)

C_GREY, C_GREY_D, C_GREY_L, C_YEL, C_ORA = hx("9ea3ab"), hx("7a7f88"), hx("c2c6cc"), hx("ffe26e"), hx("f2863a")
WHITE = hx("fffaf2")
PLUME = Plume(C_GREY, C_GREY_D, C_GREY_L, C_GREY_D, hx("b8aca8"), hx("8a8080"), foot=hx("c8a0a0"))


def hook_beak(F, K_, o, lu, hv, up, cere=None):
    """앞에서 본 갈고리 부리 — 아래로 뾰족한 둥근 세모(윗부리). 벌리면 윗부리가 들리고 그 밑에 입속 · 작은 아랫부리.
    32 에서 1칸 아래로 안 줄게 판 단위로 바닥을 둔다"""
    if up:                                         # 고개를 젖힌 칸(hand)은 틀 부리 그대로 — 끝이 핫스팟이라
        return beak_layers(F, K_, o, lu, hv, True)
    C = P_()
    m = max(1.0, 0.8 / F.s)
    bx, by = lu, K_.beak_y + hv
    w, h = K_.bw * m, K_.bh * m
    ink = lerp(C.beak_d, OUT, 0.45)
    lift = o * 0.45 * m
    upper = rpoly([(bx - w, by - lift), (bx + w, by - lift), (bx, by + h - lift)], 0.35)
    out = []
    if o > 0.05:
        dn = o * 0.9 * m
        top = by + h * 0.4
        lower = rpoly([(bx - w * 0.62, top + dn), (bx + w * 0.62, top + dn), (bx, top + dn + h * 0.55)], 0.25)
        mouth = ell(bx, top + dn * 0.4, w * 0.55, h * 0.3 + dn * 0.55)
        out += [flat(F.f(mouth), MOUTH, line=0.32, ink=ink),
                part(F.f(lower), C.beak_d, shade=lerp(C.beak_d, OUT, 0.25), line=0.38, sh=0.0, ink=ink)]
    out.append(part(F.f(upper), C.beak, shade=C.beak_d, line=0.38, sh=0.0, ink=ink))
    if cere is not None:
        c = ell(bx, by - lift - 0.1 * m, w * 0.8, 0.62 * m)
        out.append(part(F.f(c), cere, shade=lerp(cere, OUT, 0.25), line=0.38, sh=0.0, ink=lerp(cere, OUT, 0.5)))
    return out


THIN = 2.4


def thin(f, k=THIN):
    """안쪽 거리만 k 배로 — 틀이 behind 갈래를 먹선 1칸(part 기본)으로 칠해서, 가는 볏 깃은 32 에서 노랑 없이 먹줄만 남았다.
    안쪽을 늘려 재면 먹선이 1/k 로 얇아지고, 바깥은 그대로라 밝은 테 · 그림자 폭은 안 바뀐다"""
    def g(x, y):
        v = f(x, y)
        return v * k if v < 0 else v
    return g


class CockKind(Kind):
    head = (6.5, 6.3)
    body = (7.8, 5.8, 5.4)
    beak_y = 2.2
    bw, bh = 1.4, 1.9
    blush = False                                  # 주황 볼이 볼 자리를 맡는다

    def __init__(self, crest=0.5, glow=0.0):
        self.crest, self.glow = crest, glow

    def behind(self, hv):
        """볏 깃 셋 — 머리 뒤 정수리에서 솟아 끝이 오른쪽으로 말린다. crest 0 이면 뒤로 눕고 1 이면 곧추선다(픽셀 판 셈)"""
        return [(thin(f), C_YEL) for f in self.feathers(hv)]

    def feathers(self, hv):
        th = 1.0 - 0.95 * self.crest
        bx, by = 0.4, hv - self.head[1] * 0.75
        fs = []
        for off, ln in ((0.0, 1.0), (-1.4, 0.8), (1.3, 0.65)):
            b0 = (bx + off, by)
            p1 = (b0[0] + 3.4 * ln * sin(th), b0[1] - 3.4 * ln * cos(th))
            p2 = (p1[0] + 2.8 * ln * sin(th + 0.7), p1[1] - 2.8 * ln * cos(th + 0.7))
            fs.append(chain([b0, p1, p2], 1.25, 0.65))
        return fs

    def marks(self, hv):
        """노란 얼굴 · 주황 볼(눈 바로 밑 바깥)"""
        hrx, hry = self.head
        head = ell(0.0, hv, hrx, hry)
        ex, ey = self.eye
        out = [(head, C_YEL)]
        for sg in (-1, 1):
            out.append((ell(sg * (ex + 0.7), hv + ey + 2.1, 1.75, 1.45), C_ORA))
        return out

    def tail(self):
        fv = self.feet_v
        return [(chain([(1.0, fv - 5.6), (3.2, fv - 2.4), (5.2, fv - 0.7)], 1.6, 0.75), C_GREY_D)]

    def wing_marks(self, w, rx, ry, a, L, sg):
        """날개 바깥 가운데 흰 띠 — 결 방향 가운데 토막의 바깥 가장자리만 가늘게. 바깥 반을 다 희게 하면 32 에서
        양옆에 흰 장갑 낀 손으로 읽혔다"""
        ca, sa = cos(a), sin(a)

        def band(x, y):
            t = (x - rx) * ca + (y - ry) * sa
            c = -(x - rx) * sa + (y - ry) * ca
            return max(L * 0.2 - t, t - L * 0.95, c * sg + 0.45, -c * sg - 1.35)
        return [(band, WHITE)]

    def beak(self, F, o, lu, hv, up):
        return hook_beak(F, self, o, lu, hv, up)


_PREV = [birdkit.bface]


def _face(F, K_, mood="open", beak=0.0, look=0.0, hv=0.0, up=False):
    """볏 깃 노랑을 납작하게 다시 칠하고 틀 얼굴을 얹는다. 틀은 behind 갈래를 part 로 칠해 그늘 띠(오른쪽 아래 1칸)가
    가는 깃을 통째로 회색으로 덮는다 — 얼굴을 그리는 자리가 머리 위 · 앞 날개 밑이라 여기서 머리 밖 깃만 먹선 안쪽으로
    덧칠한다. 끝이 먹선보다 가는 깃 끝은 그대로 그늘 회색이라 픽셀 판처럼 끝만 회색이 된다"""
    out = []
    if isinstance(K_, CockKind):
        head = F.f(ell(0.0, hv, *K_.head))
        for f in K_.feathers(hv):
            g = F.f(f)
            out.append(flat(lambda x, y, g=g: max(g(x, y) + 0.5 / THIN + 0.05, -head(x, y)), C_YEL))
    return out + _PREV[-1](F, K_, mood, beak, look, hv, up)


@lru_cache(maxsize=None)
def kind(crest, glow=0.0):
    """볏 높이마다 생김새 하나 — 같은 값은 돌려 쓴다"""
    return CockKind(round(crest, 3), glow)


K = kind(0.5)                       # 공용 14칸 — 반쯤 선 볏
K_FLAT = kind(0.0)                  # 화살표 — 볏을 뒤로 눕혀 화살표 날개를 비킨다(픽셀 판 CARRY_OPT)


def glow(F, K_, col, a):
    """볼이 달아오름 — 주황 볼 위에 번지는 둥근 빛"""
    ex, ey = K_.eye
    out = []
    for sg in (-1, 1):
        x, y = F.w(sg * (ex + 0.7), ey + 2.1)
        r = 2.1 * F.s
        out.append(soft(ell(x, y, r, r * 0.82), col, a))
    return out


def sc_arrow(fr, g):
    """크림 화살표를 정수리에 이고 통통 — 볏은 뒤로 눕힌 채. 화살표가 맨 위"""
    return carry_hop(K_FLAT, fr, g)


def perch(x0, x1, y):
    """나무 횃대 — 가로 막대 하나, 양끝 짙게"""
    f = capsule(x0, y, x1, y, 1.05)
    return [base(f), part(f, WOOD, shade=WOOD_D, line=0.8)]


def sc_wait(fr):
    """횃대에 앉아 볏을 천천히 올렸다 내렸다 — 다 서면 눈이 동그래지고 볼이 빛나고 느낌표"""
    ph, k = ph_k(fr)
    c = 0.5 - 0.5 * cos(ph)
    K_ = kind(c)
    py = 26.6
    out = perch(3.4, 28.6, py)
    F = stand(K_, 16.0, py - 0.2, 0.8)
    up = c > 0.9
    out += bird(F, K_, "blink" if k == 9 else "open", wl="fold", wr="fold")
    if up:
        out += glow(F, K_, C_ORA, 0.55)
        x, y = F.w(K_.head[0] + 2.4, -K_.head[1] - 0.6)
        bang = capsule(x, y - 2.2, x, y - 0.4, 0.42)
        dot = circle(x, y + 0.8, 0.46)
        out += [base(bang, dot), flat(bang, OUT), flat(dot, OUT)]
    return out


def sc_no(fr):
    """볏을 바짝 세우고 날개를 쫙 펴 쉭쉭 — 부리를 벌리고 볼이 빨갛게 달아오른다. 빗금 왼쪽 아래에 둔다 — 가운데 두면
    두 눈 · 볼이 빗금에 묻힌다(볏은 빗금 뒤로 지나가도 읽힌다). 표지가 위"""
    ph, k = ph_k(fr)
    big = k % 4 < 2
    K_ = kind(1.0 if big else 0.85)
    F = at_mid(K_, 11.4, 19.0, 0.6)
    out = bird(F, K_, "open", beak=0.9 if big else 0.0, wl="out", wr="out", puff=1.04 if big else 1.0)
    out += glow(F, K_, SIGN, 0.5 if big else 0.3)
    if big:                                                     # 쉭쉭 — 머리 양옆에 < > 꺾쇠
        for sg in (-1, 1):
            x, y = F.w(sg * (K_.head[0] + 2.2), 0.6)
            d = -sg * 1.0
            v = capsule(x, y - 1.0, x + d, y, 0.3), capsule(x + d, y, x, y + 1.0, 0.3)
            out += [flat(v[0], OUT), flat(v[1], OUT)]
    return out + no_sign()


class Cockatiel(BirdPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""

    def cell(self, name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
        _PREV.append(birdkit.bface)            # 이 결을 그리는 동안만 감싼다 — 다른 새는 틀 그대로
        birdkit.bface = _face
        try:
            return super().cell(name, frame, soft_, tip_body, shape)
        finally:
            birdkit.bface = _PREV.pop()


PET = Cockatiel(PLUME, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no})

register("cockatiel", PET)
catkit.load()

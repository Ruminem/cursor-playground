# SPDX-License-Identifier: Apache-2.0
"""문조(javasparrowanim) 고화질 — 새 틀(birdkit)에 깃빛 · 생김새 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(gen/bird.py)의 생김새 그대로: 회색 몸 · 분홍 배 · 까만 모자 아래 흰 얼굴(턱 밑에 까만 점) · 굵은 분홍 부리 ·
빨간 눈테 · 까만 꼬리 · 날개 끝이 짙은 회색. 짓도 그대로: 화살표를 이고 통통(화살표), 둥지에서 알을 품고 꾸벅꾸벅 졸다가
몸을 들어 알을 한 번 살핌(기다림), 굵은 부리를 딱딱 벌리며 부풀어 쑥 — 위협(금지).

까만 머리에 흰 볼만 얹은 첫 판은 까만 눈이 머리에 묻혀 32 에서 눈테만 남았고 그게 빨간 고글로 읽혔다 — 그래서 모자를
눈 높이에서 끊고 눈을 흰 얼굴 위에 앉혔다. 눈테는 틀(birdkit.bface)에 갈고리가 없어 이 결의 칸을 그리는 동안만 bface 를
감싸 얹는다(Java.cell). 픽셀 판에서 진한 빨강 눈테 막대가 1배에서 화난 눈썹으로 읽혔던 일이 있어 눈테는 모자 가장자리를
따르는 가는 반달로만 둔다.
"""
from . import birdkit, catkit, register
from .birdkit import (Plume, Kind, BirdPet, bird, stand, at_mid, carry_hop, chain, ell, inter, union, capsule, arc, base,
                      part, flat, hx, zip_lines, no_sign, ph_k, sin, pi, radians)

GREY, GREY_D, BELLY, BLACK = hx("8f9aab"), hx("6f7a8c"), hx("ecd9d3"), hx("2f2a33")
BEAK, BEAK_D, RING = hx("f2768c"), hx("c84a64"), hx("e8485a")
WHITE = hx("fffaf2")
LID = hx("f4a6b4")                     # 화난 눈썹 — 까만 모자 위라 밝게(픽셀 판 RING_SOFT)
PLUME = Plume(GREY, GREY_D, BELLY, GREY, BEAK, BEAK_D, foot=hx("f0a0a8"))
SHELL, SHELL_D = hx("fdf8ee"), hx("d8ccb4")
NEST, NEST_D, NEST_L = hx("a8743e"), hx("6e4a28"), hx("caa060")


class JavaKind(Kind):
    head = (6.8, 6.4)
    body = (7.6, 6.0, 5.2)
    beak_y = 2.7
    bw, bh = 2.0, 2.1                  # 굵은 부리

    def marks(self, hv):
        """까만 모자는 눈 높이까지, 그 아래 얼굴은 다 흰 볼 · 부리 밑 턱에 까만 점 하나.
        눈이 흰 볼 위에 앉아야 까만 콩 눈이 32 에서 보인다 — 까만 머리 안에 두면 눈테만 남아 빨간 띠로 읽힌다"""
        hrx, hry = self.head
        head = ell(0.0, hv, hrx, hry)
        white = inter(head, ell(0.0, hv + 4.6, hrx + 0.6, 5.0))
        chin = inter(head, ell(0.0, hv + 5.9, 1.2, 0.9))
        return [(head, BLACK), (white, WHITE), (chin, BLACK)]

    def tail(self):
        fv = self.feet_v
        return [(chain([(2.0, fv - 4.4), (5.0, fv - 2.4), (6.8, fv - 1.4)], 1.8, 1.3), BLACK)]

    def wing_marks(self, w, rx, ry, a, L, sg):
        """날개 끝 짙은 회색"""
        tx, ty = rx + birdkit.cos(a) * L, ry + sin(a) * L
        return [(birdkit.circle(tx, ty, L * 0.5), GREY_D)]


K = JavaKind()


def _eyes(F, K_, look, hv, up):
    """bface 와 같은 셈으로 눈 자리 · 반지름(art)"""
    s = F.s
    er = max(1.0 * s, 0.9)
    ex, ey = K_.eye
    if up:
        ex, ey, er = ex * 0.85, -2.2, max(1.15 * s, 1.1)
    lu = 0.9 * look
    return [(F.w(sg * ex + lu, ey + hv), er) for sg in (-1, 1)]


_PREV = [birdkit.bface]


def _face(F, K_, mood="open", beak=0.0, look=0.0, hv=0.0, up=False):
    """문조 얼굴 — 틀 얼굴에 눈마다 빨간 눈테(위 반)를 얹는다"""
    out = _PREV[-1](F, K_, mood, beak, look, hv, up)
    for (x, y), er in _eyes(F, K_, look, hv, up):              # 눈테는 모자 가장자리를 따라 위 반만
        w = max(0.24, 0.2 * er)
        out.append(flat(arc(x, y, er + 0.1 + w, w, pi * 0.95, pi * 1.1), RING))
    return out


def head_v(sq=0.0, puff=1.0):
    """bird() 가 눌림 · 부풂만큼 머리를 내리는 값(캐논)"""
    bry = K.body[2]
    return 1.5 * (bry - bry * (1 - 0.14 * sq) * puff)


def brows(F, hv, col, look=0.0):
    """화난 눈썹 — 안쪽이 내려온 짧은 막대 둘"""
    ex, ey = K.eye
    lu = 0.9 * look
    out = []
    for sg in (-1, 1):
        x0, y0 = F.w(sg * (ex - 1.3) + lu, ey + hv - 1.7)
        x1, y1 = F.w(sg * (ex + 1.1) + lu, ey + hv - 2.8)
        out.append(flat(capsule(x0, y0, x1, y1, max(0.42, 0.5 * F.s)), col))
    return out


def sc_arrow(fr, g):
    """크림 화살표를 정수리에 이고 통통 — 쪼그렸다가 날개를 들며 폴짝. 화살표가 맨 위"""
    return carry_hop(K, fr, g)


NOD = [0, 0, 0.4, 0.8, 1.2, 1.4, 1.4, 1.4, 1.0, 0, 0, 0]
MOOD = ["open", "open", "blink", "blink", "blink", "blink", "blink", "blink", "blink", "open", "happy", "open"]


def zee(x, y, h):
    """졸음 z 하나 — 윗줄 · 빗금 · 아랫줄"""
    r = max(0.32, h * 0.13)
    return union(capsule(x, y, x + h, y, r), capsule(x + h, y, x, y + h, r), capsule(x, y + h, x + h, y + h, r))


def nest(cx, top, w=12.5):
    """둥지 그릇 — 짚 색 반달 · 위 테는 밝게 · 짚 줄 몇 가닥"""
    bowl = inter(ell(cx, top, w, 6.6), lambda x, y: top - y)
    rim = capsule(cx - w + 1.4, top + 0.4, cx + w - 1.4, top + 0.4, 1.0)
    out = [base(bowl, rim), part(bowl, NEST, shade=NEST_D), part(rim, NEST_L, shade=NEST, line=0.7)]
    for i, (x, y, dx, dy) in enumerate(((cx - 8.0, top + 2.6, 2.6, 1.0), (cx - 3.4, top + 4.0, 3.0, -0.8),
                                        (cx + 2.2, top + 2.8, 2.8, 1.1), (cx + 6.6, top + 3.6, 2.4, -0.9),
                                        (cx - 1.0, top + 5.4, 2.2, 0.6))):
        out.append(flat(capsule(x, y, x + dx, y + dy, 0.3), NEST_D))
    return out


def sc_wait(fr):
    """둥지에서 알을 품고 꾸벅꾸벅 — 졸다가(z) 장 9 에 몸을 들어 알 둘을 한 번 살피고 다시 앉는다"""
    ph, k = ph_k(fr)
    nod = NOD[k]
    lift = 2.2 if k in (9, 10) else 0.0
    top = 21.4
    F = stand(K, 16.0, 27.2 - lift, 0.86, radians(4.0 * nod))
    out = bird(F, K, MOOD[k], sq=0.75 * nod, feet=False, look=0.5 if lift else 0.0)
    if lift:
        for cx in (13.2, 18.8):
            egg = ell(cx, top - 0.4, 2.0, 2.4)
            out += [base(egg), part(egg, SHELL, shade=SHELL_D)]
    out += nest(16.0, top)
    if 4 <= k <= 8:
        t = (k - 4) / 5
        for i, (h, d) in enumerate(((2.4, 0.0), (1.6, 0.5))):
            u = (t + d) % 1.0
            z = zee(22.6 + 3.2 * u, 7.0 - 4.6 * u - h * 0.5, h)
            out += [base(z), flat(z, birdkit.OUT)]
    return out


def sc_no(fr):
    """굵은 분홍 부리를 딱딱 벌렸다 다물며 부풀어 쑥 — 위협(짹!). 흰 눈썹이 안쪽으로 내려온다. 표지가 위"""
    ph, k = ph_k(fr)
    lunge = k % 4 in (1, 2)
    puff = 1.08 if lunge else 1.0
    F = at_mid(K, 10.8, 19.4 - (0.6 if lunge else 0.0), 0.62 if lunge else 0.58)  # 빗금 왼쪽 아래 — 가운데면 두 눈이 빗금에 묻힌다
    w = "out" if lunge else "fold"
    out = bird(F, K, "angry", beak=0.7 if lunge else 0.0, wl=w, wr=w, puff=puff)   # 더 벌리면 굵은 부리 속이 빨간 기둥
    out += brows(F, head_v(puff=puff), LID)
    if lunge:                                                   # 짹! 줄 — 빗금에 안 묻히는 왼쪽 위 · 왼쪽에만
        hx_, hy_ = F.w(-K.head[0] * 0.5, -K.head[1] * puff)
        out += zip_lines(hx_, hy_ + 0.4, 2, 1.2, 1.4, -pi / 2 - 0.45, 0.6)
        x, y = F.w(-K.head[0] * puff, 0.0)
        out += zip_lines(x, y, 2, 1.2, 1.0, pi + 0.35, 0.7)
    return out + no_sign()


class Java(BirdPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""

    def cell(self, name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
        _PREV.append(birdkit.bface)            # 이 결을 그리는 동안만 감싼다 — 다른 새는 틀 그대로
        birdkit.bface = _face
        try:
            return super().cell(name, frame, soft_, tip_body, shape)
        finally:
            birdkit.bface = _PREV.pop()


PET = Java(PLUME, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no})

register("javasparrow", PET)
catkit.load()

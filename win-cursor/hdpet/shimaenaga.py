# SPDX-License-Identifier: Apache-2.0
"""시마에나가(shimaenagaanim) 고화질 — 새 틀(birdkit)에 깃빛 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(지운 gen/bird.py)의 짓 그대로: 화살표를 머리에 이고 날개 없이 통통(화살표 — 픽셀 주석 "접은 까만 날개도
1배에선 짧은 팔다리로 읽힌다 — 날개 없이 찹쌀떡 그대로"), 눈송이 속에서 솜털을 부풀려 동그란 찹쌀떡이 되고 다 부풀면
눈을 감고 흐뭇(기다림), 솜털을 빵빵하게 부풀려 화남 — 부풀었다 숨을 고르며 조금 줄고 머리 옆에 💢(금지).
생김새는 머리와 몸이 거의 한 덩이인 새하얀 찹쌀떡 · 아주 작은 까만 부리 · 까만 날개(어깨 분홍) · 끝이 흰 긴 까만 꼬리.
"""
from . import catkit, register
from .birdkit import (Plume, Kind, BirdPet, bird, bface, at_mid, stand, ell, inter, circle, capsule, arc, chain, union, hx,
                      base, part, flat, layer, ground, no_sign, ph_k, HOP, carry_s, hang, puff, arrow_layers, OUT,
                      lerp, smooth, sin, cos, pi, TAU)

M_WHITE, M_CREAM, M_BLACK, M_PINK = hx("fffdf8"), hx("f4ede2"), hx("3a3236"), hx("e8b4bc")
TIP_WHITE = hx("fffaf2")
ICE, ICE_D = hx("e6f4fb"), hx("a8d4e8")
ANGRY, ANGRY_D = hx("e8484a"), hx("9e2b28")
PLUME = Plume(M_WHITE, hx("c9ced8"), M_CREAM, M_BLACK, M_BLACK, M_BLACK, foot=M_BLACK)


class ShimaKind(Kind):
    """sw: 꼬리 각(라디안, + 면 끝이 아래로). 머리와 몸 사이를 좁혀 한 덩이 찹쌀떡으로"""
    head = (7.2, 6.6)
    body = (6.6, 7.2, 5.4)
    eye = (2.8, 1.3)
    beak_y = 2.9
    bw, bh = 0.9, 1.0
    wing_l, wing_w = 2.6, 1.8

    def __init__(self, sw=0.0):
        self.sw = sw

    def wing_marks(self, w, rx, ry, a, L, sg):
        return [(circle(rx, ry, 0.8), M_PINK)]                                     # 어깨 분홍 — 크면 32 에서 까만 손의 젤리

    def tail(self):
        fl = self.body[0] + self.body[2]
        c, s = cos(self.sw), sin(self.sw)
        pts = [(u * c - v * s, fl + u * s + v * c) for u, v in ((2.0, -2.6), (5.6, -0.4), (9.2, 1.4))]
        t = chain(pts, 1.9, 1.5)
        return [(t, M_BLACK), (inter(t, circle(*pts[-1], 2.0)), TIP_WHITE)]        # 끝이 흰 까만 꼬리


K = ShimaKind()


def hv_of(K_, sq=0.0, pf=1.0):
    """bird() 가 머리를 내린 만큼 — 얼굴을 따로 그리는 칸이 쓴다"""
    bv, brx, bry = K_.body
    return ((bv + bry) - bry * (1 - 0.14 * sq) * pf - bv) * 1.5


def carry_bare(K_, fr, g, s=0.66, **kw):
    """birdkit.carry_hop 그대로이되 날개만 없다 — 화살표를 이고 통통"""
    ph, k = ph_k(fr)
    gap, sq, wu, mood, bk, dust = HOP[k]
    s = carry_s(K_, g, s)
    px, py = g["stem"][0], g["stem"][1] - 0.8
    F = hang(K_, px, py, s)
    fy = py + (K_.feet_v + K_.head[1]) * s
    out = ground(px, min(fy + 0.6, 30.0), 3.6 - 0.5 * gap, 0.2 - 0.03 * gap)
    out += bird(F, K_, mood, beak=0.8 if bk else 0.0, wl=None, wr=None, sq=sq - 0.25 * gap, lift=(0.4 * gap, 0.4 * gap), **kw)
    if dust:
        out += puff(px + 5.2, min(fy, 29.0), 0.9, 0.8)
    return out + arrow_layers(g)


def sc_arrow(fr, g):
    """크림 화살표를 정수리에 이고 날개 없이 통통 — 찹쌀떡이 눌렸다 늘어나고 꼬리가 살짝 까딱. 화살표가 맨 위. 꼬리는 발바닥 위로 들어 둔다 — 발이 판 밑에 붙어 있어 처지면 잘림"""
    return carry_bare(ShimaKind(-0.3 + 0.08 * sin(TAU * fr)), fr, g, puff=1.06)


FLAKES = [(4.6, 0.0), (27.4, 0.35), (7.6, 0.6), (26.0, 0.85), (13.4, 0.2), (21.6, 0.7)]   # (x, 장 어긋남)


def flake(cx, cy, a):
    """눈송이 — 여섯 갈래 연파랑 + 흰 가운데"""
    g = union(*[capsule(cx - 1.25 * cos(t), cy - 1.25 * sin(t), cx + 1.25 * cos(t), cy + 1.25 * sin(t), 0.34)
                for t in (pi / 2, pi / 2 + pi / 3, pi / 2 - pi / 3)])
    return [layer(g, lambda x, y, e, nx, ny, fr: (ICE_D, 1.0), alpha=a),
            layer(circle(cx, cy, 0.5), lambda x, y, e, nx, ny, fr: (TIP_WHITE, 1.0), alpha=a)]


def sc_wait(fr):
    """눈송이 속에서 솜털을 부풀려 동그란 찹쌀떡이 된다 — 다 부풀면 눈을 감고 흐뭇. 눈송이는 한 바퀴에 한 번 내려온다"""
    ph, k = ph_k(fr)
    pf = 0.5 - 0.5 * cos(ph)
    out = []
    for x, o in FLAKES:
        t = (fr + o) % 1.0
        a = min(1.0, t / 0.18, (1.0 - t) / 0.18)
        out += flake(x + 0.6 * sin(TAU * t * 2 + x), 2.4 + 20.0 * t, a)
    out += ground(15.5, 28.6, 6.4, 0.2)
    F = stand(K, 15.5, 28.0, 0.8)                                        # 발바닥을 28.0 에 — 부풀어도 발은 그대로
    out += bird(F, ShimaKind(0.05 * pf), "happy" if pf > 0.7 else "open", puff=1.0 + 0.16 * pf)
    return out


def anger(cx, cy, d=1.5):
    """💢 — 네 귀퉁이 활이 가운데로 볼록"""
    g = union(*[arc(cx + sx * d, cy + sy * d, d * 0.85, 0.42, a0 + 0.12 * pi, 0.26 * pi)
                for sx, sy, a0 in ((1, 1, pi), (-1, 1, 1.5 * pi), (-1, -1, 0.0), (1, -1, 0.5 * pi))])
    return [layer(g, lambda x, y, e, nx, ny, fr: (lerp(ANGRY, ANGRY_D, smooth(0.3, 0.1, -e)), 1.0))]


def angry_face(F, K_, hv):
    """눈은 공용 콩 눈, 그 위에 안쪽으로 내려온 눈썹(픽셀 angry)"""
    s = F.s
    er = max(1.0 * s, 0.9)
    ex, ey = K_.eye
    out = bface(F, K_, "open", 0.0, 0.0, hv)
    for sg in (-1, 1):
        x, y = F.w(sg * ex, ey + hv)
        out.append(flat(capsule(x + sg * er * 1.0, y - er * 1.95, x - sg * er * 0.7, y - er * 1.25, max(0.3, 0.26 * er)), OUT))
    return out


def sc_no(fr):
    """솜털을 빵빵하게 부풀려 화남 — 부풀었다 숨을 고르며 조금 줄었다, 머리 옆에 💢. 표지가 위"""
    ph, k = ph_k(fr)
    pf = 1.12 + 0.08 * sin(2 * ph)
    F = at_mid(K, 14.8, 15.6, 0.66)
    out = bird(F, K, face_on=False, puff=pf)
    out += angry_face(F, K, hv_of(K, 0.0, pf))
    out += no_sign()
    if k % 6 < 4:                                       # 💢 은 고리 밖 오른쪽 위 — 고리 안에 두면 표지에 가려 안 보인다
        out += anger(26.8, 3.8, 1.35)
    return out


class Shimaenaga(BirdPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Shimaenaga(PLUME, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no})

register("shimaenaga", PET)
catkit.load()

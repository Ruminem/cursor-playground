# SPDX-License-Identifier: Apache-2.0
"""병아리(chickanim) 고화질 — 새 틀(birdkit)에 깃빛 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(지운 gen/bird.py)의 짓 그대로: 화살표를 머리에 이고 뒤뚱(화살표), 알껍데기 바지를 입고 폴짝 · 삐약(기다림),
금지 표지 안에서 발을 동동 · 날개를 번갈아 들며 삐약 질끈(금지). 머리 위에 솜털 세 가닥.
"""
from . import catkit, register
from .birdkit import (Plume, Kind, BirdPet, bird, at_mid, stand, carry_waddle, chain, ell, inter, hx, ground, zip_lines,
                      no_sign, ph_k, sin, pi)

PLUME = Plume(hx("ffe476"), hx("f2c84a"), hx("fff2b4"), hx("f7d45c"), hx("f59a2a"), hx("d07a1a"))
SHELL, SHELL_D = hx("fdf8ee"), hx("d8ccb4")


class ChickKind(Kind):
    waddle = True

    def top(self, hv):
        """정수리 솜털 세 가닥 — 먹색 가는 줄"""
        t = -self.head[1] + hv + 0.6
        return [chain([(0.0, t), (-0.2, t - 1.6), (0.6, t - 2.7)], 0.6, 0.45),
                chain([(-0.8, t + 0.1), (-1.9, t - 1.3)], 0.55, 0.4),
                chain([(0.8, t + 0.1), (1.9, t - 1.2)], 0.55, 0.4)]


K = ChickKind()


def sc_arrow(fr, g):
    """크림 화살표를 정수리에 이고 뒤뚱뒤뚱 — 걸음마다 날개가 살짝 들리고 가끔 삐약. 화살표가 맨 위"""
    return carry_waddle(K, fr, g)


def shell(v0):
    """알껍데기 바지 — 몸 아래 반을 덮는 껍데기, 윗변은 들쭉날쭉(캐논, v0 이 윗변 높이)"""
    bv, brx, bry = K.body

    def zig(x, y):
        u = (x / 1.7) % 2.0
        return (v0 + 1.1 * abs(u - 1.0) - y) * 0.7
    return inter(ell(0.0, bv + 1.2, brx + 1.3, bry + 2.0), zig)


HOPW = [0, 0, 1, 2.5, 3.5, 3.5, 2.5, 1, 0, 0, 0, 0]


def sc_wait(fr):
    """알껍데기 바지를 입고 폴짝폴짝 — 뜰 때 날개를 들고 삐약, 내려앉을 때 꾹 눌림"""
    ph, k = ph_k(fr)
    h = HOPW[k]
    s = 0.8
    gy = 29.4
    out = ground(16.0, gy + 0.2, 6.0 - 0.6 * h, 0.24 - 0.03 * h)
    t = 0.6 if h else 0.0
    F = stand(K, 16.0, gy - 0.6 - h, s)
    cheep = 3 <= k <= 5
    out += bird(F, K, "happy" if h else "blink" if k == 10 else "open", beak=0.85 if cheep else 0.0,
                wl=(("fold", "up"), t), wr=(("fold", "up"), t), sq=0.6 if k in (0, 1, 8) else -0.3 if h > 2 else 0.0,
                feet=False, extra=[(shell(K.body[0] - 0.4), SHELL)])
    if cheep:
        hx_, hy_ = F.w(K.head[0] * 0.8, -K.head[1] * 0.5)
        out += zip_lines(hx_ + 1.2, hy_ - 0.6, 3, 1.2, 1.4, -pi / 4, 0.6)
    return out


def sc_no(fr):
    """금지 표지 안에서 발을 동동 구르고 날개를 번갈아 들며 삐약 — 눈 질끈. 표지가 위"""
    ph, k = ph_k(fr)
    sw = sin(ph * 2)
    F = at_mid(K, 14.5, 15.0, 0.7)
    out = bird(F, K, "squeeze", beak=0.85 if k % 4 < 2 else 0.0,
               wl=(("fold", "up"), 0.7 * max(0.0, sw)), wr=(("fold", "up"), 0.7 * max(0.0, -sw)),
               lift=(1.2 * max(0.0, sw), 1.2 * max(0.0, -sw)), sq=0.25 * abs(sw))
    if k % 4 < 2:
        out += zip_lines(23.4, 7.4, 3, 1.1, 0.8, -pi / 4, 0.6)
    return out + no_sign()


class Chick(BirdPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Chick(PLUME, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no})

register("chick", PET)
catkit.load()

# SPDX-License-Identifier: Apache-2.0
"""아기 티라노(trexanim) 고화질 — 공룡 틀(dinokit)에 몸빛 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(지운 gen/dino.py)의 짓 그대로: 화살표 날개를 잡으려다 짧은 팔이 안 닿아 버둥 · 땀(화살표),
짧은 팔을 엇갈려 버둥버둥 · 와앙 입 벌렸다 닫음(기다림), 짧은 팔로 X 를 만들려다 안 닿음 · 질끈 + 땀(금지).
"""
from . import catkit, register
from .dinokit import DF, TAIL_UP, Hide, Kind, DinoPet, dino, drop, no_sign, arrow_layers, ph_k, hx, sin

HIDE = Hide(hx("8fd17a"), hx("5fa35a"), hx("eef4c4"), hx("ffffff"))


K = Kind()                                               # 티라노가 틀의 기본 생김새다(표식 없음, 이도 없음 — taste.md 톱니 이빨)


def sc_arrow(fr, g):
    """날개 끝 오른쪽 아래에 선 티라노가 왼쪽을 보고 짧은 팔을 뻗어 버둥 — 안 닿아 질끈 · 땀. 화살표가 맨 위"""
    ph, k = ph_k(fr)
    s = 0.95
    wx, wy = g["wing"]
    ox = min(wx + 6.4, 29.1 - 9.4 * s)                    # 꼬리 끝(캐논 -9.4 + 반지름 1.5칸)이 판 안에
    oy = min(wy + 2.6, 30.4 - 14.0 * s)                   # 발바닥(캐논 14)이 판 안에
    reach = abs(sin(ph))
    out = dino(DF(ox, oy, s, fx=-1), K, "squeeze" if k % 6 in (2, 3) else "open", nod=-0.35 - 0.12 * reach,
               arm=1.6 + 1.2 * reach, arm_far=2.8 - 1.2 * reach, sway=0.8 * sin(ph), tail_pts=TAIL_UP)
    if k % 6 in (2, 3, 4):
        out += drop(ox + 2.6, oy - 3.8 - 0.4 * (k % 6 - 2), 0.75, 1.1)
    return out + arrow_layers(g)


def sc_wait(fr):
    """짧은 팔 버둥버둥 — 양팔이 엇갈려 위아래, 와앙 입 벌렸다 닫고 꼬리 살랑"""
    ph, k = ph_k(fr)
    up_ = 1.6 if k % 2 else -0.4
    roar = k in (4, 5, 6)
    out = dino(DF(17.4, 13.0, 1.2), K, "squeeze" if roar else "blink" if k == 10 else "open", nod=-0.18 if roar else 0.0,
               mouth=0.8 if roar else 0.0, arm=up_, arm_far=1.2 - up_, sway=1.0 * sin(ph))
    return out


def sc_no(fr):
    """금지 표지 안에서 짧은 팔로 X 를 만들려다 안 닿아 허우적 — 질끈 · 땀. 표지가 위"""
    ph, k = ph_k(fr)
    t = abs(sin(ph))
    s = 0.66
    out = dino(DF(17.6, 11.0, s), K, "squeeze", arm=0.6 + 1.6 * t, arm_far=2.2 - 1.6 * t,
               sway=0.6 * sin(ph), tail_pts=TAIL_UP)
    if k % 4 < 2:
        out += drop(20.6, 8.4, 0.75, 1.1)
    return out + no_sign()


class Trex(DinoPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Trex(HIDE, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no}, hot={"wait": (13, 12)})

register("trex", PET)
catkit.load()

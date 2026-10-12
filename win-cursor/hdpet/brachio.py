# SPDX-License-Identifier: Apache-2.0
"""아기 브라키오사우루스(brachioanim) 고화질 — 공룡 틀(dinokit)에 몸빛 · 생김새(긴 목 몸) · 화살표 · 기다림 · 금지 세 칸을 얹는다.

픽셀 판(gen/dino.py)의 짓 그대로: 화살표 오른쪽 아래에서 목을 늘였다 줄였다 하며 화살표 끝을 올려다봄(화살표),
목을 쭉 올려 늘어진 가지의 나뭇잎을 냠냠 — 잎이 한 장씩 줄고 내려옴(기다림), 쳐든 머리를 목째 시계추처럼 도리도리(금지).

긴 목은 선 치비 틀(머리 (0, 0) · 몸 (-1.2, 8))에 없어서 Kind.body 로 몸을 직접 그린다. 안쪽 캐논에서 머리를 몸 앞 위로
들고(HU, HV) 굵은 목 기둥으로 몸 앞 어깨에 잇고, 몸은 가로로 눕혀 네 발로 선다. 그걸 통째로 Z 배 줄여(축 PV) 발바닥이
틀과 같은 v ≈ 14 에 오게 해서 공용 칸의 자리를 그대로 쓴다. 고개 까딱(nod)은 머리 제 관절 둘레, 시계추(swing)는
목 밑동 둘레, 목 늘이기(neck)는 목 방향으로 — 셋을 따로 둔다. 손 칸만 공용 snout_tip 이 틀의 까딱 축을 써서
여기 관절과 안 맞으므로 같은 짓을 이 몸의 주둥이 끝 셈으로 다시 끼운다(shared).
"""
import copy

from . import catkit, register
from .dinokit import (DF, TAIL_UP, LINE_IN, LEAF, LEAF_D, STEM, OUT, Hide, Kind, Pose, DinoPet, dface, drop, no_sign,
                      zip_lines, arrow_layers, tail_of, ph_k, hx, sin, cos, pi, hypot, H, HAND_HOT)
from .dinokit import ell, oell, inter, chain, taper, base, part, flat, smin, union, capsule, grow, lerp

HIDE = Hide(hx("9fd0f0"), hx("6fa8d6"), hx("e4f3fc"), hx("c7e6f8"))

# 안쪽 캐논(오른쪽을 봄, 아래가 +v)
HU, HV = 1.8, -4.0                       # 머리 가운데 — 몸 앞 위로 쳐듦
HEAD = (0.0, 0.0, 6.0, 5.2)              # 머리(머리 제 좌표)
SNOUT = (3.2, 1.4, 3.8, 2.9)             # 짧고 둥근 주둥이
CREST = (1.0, -4.4, 2.4, 1.8)            # 이마 혹 — 브라키오 표식
JOINT = (0.2, 4.2)                       # 머리가 까딱이는 관절(머리 밑, 목 꼭대기)
NB = (0.2, 8.6)                          # 목 밑동(몸 앞 어깨 안)
BODY = (-3.8, 9.8, 6.8, 4.3)             # 가로로 누운 몸
VF = 15.4                                # 발바닥
TAIL = [(-9.2, 10.6), (-12.6, 11.2), (-15.2, 9.8), (-16.2, 7.8)]
TAIL_CURL = [(-9.0, 10.4), (-11.2, 10.0), (-12.2, 8.0), (-11.4, 6.0)]   # 판이 좁은 칸(틀이 TAIL_UP 을 주는 칸)
SPOTS = ((-7.0, 7.2, 1.0), (-4.0, 6.5, 0.85), (-9.0, 10.0, 0.8), (-1.4, 7.4, 0.7))
PV, Z = (0.4, 4.6), 0.86                 # 바깥(틀) 캐논 = PV + Z × (안쪽 - PV)

_nt = (HU + JOINT[0] - NB[0], HV + JOINT[1] - NB[1])
_nl = hypot(*_nt)
ND = (_nt[0] / _nl, _nt[1] / _nl)        # 목 방향(밑동 → 머리)


def sub(F, du, dv, k=1.0):
    """F 의 캐논 (du, dv) 를 원점으로, k 배 한 틀 — 새 틀의 (u, v) 가 F 의 (du, dv) + k (u, v)"""
    G = copy.copy(F)
    u = du * F.fx
    G.ox = F.ox + (u * F.c - dv * F.sn) * F.s
    G.oy = F.oy + (u * F.sn + dv * F.c) * F.s
    G.s = F.s * k
    return G


def inner(F):
    return sub(F, PV[0] * (1 - Z), PV[1] * (1 - Z), Z)


def rot(p, a, piv):
    if not a:
        return p
    c, s = cos(a), sin(a)
    du, dv = p[0] - piv[0], p[1] - piv[1]
    return piv[0] + du * c - dv * s, piv[1] + du * s + dv * c


def turned(g, a, piv):
    """거리함수 g 를 piv 둘레로 a(+ 가 시계 방향 = 앞으로 숙임) 돌림"""
    if not a:
        return g
    c, s = cos(a), sin(a)
    return lambda u, v: g(piv[0] + (u - piv[0]) * c + (v - piv[1]) * s, piv[1] - (u - piv[0]) * s + (v - piv[1]) * c)


def moved(g, du, dv):
    return lambda u, v: g(u - du, v - dv)


def head_place(neck=0.0):
    """목을 neck 만큼 늘인 머리 가운데 · 관절(안쪽 캐논, 돌리기 전)"""
    hc = (HU + ND[0] * neck, HV + ND[1] * neck)
    return hc, (hc[0] + JOINT[0], hc[1] + JOINT[1])


def pose_of(neck=0.0, nod=0.0, swing=0.0):
    """머리 놓기 — 관절 둘레 nod 다음 목 밑동 둘레 swing. (점 옮기기, 거리함수 옮기기, 머리 원점, 관절, 합친 각)"""
    hc, j = head_place(neck)

    def pt(p):
        return rot(rot(p, nod, j), swing, NB)

    def fn(g):
        return turned(turned(moved(g, *hc), nod, j), swing, NB)
    return pt, fn, pt(hc), pt(j), nod + swing


def snout_at(F, nod=0.0, neck=0.0, swing=0.0):
    """주둥이 끝(art) — 손 칸이 핫스팟을 여기에 맞춘다"""
    pt = pose_of(neck, nod, swing)[0]
    hc, _ = head_place(neck)
    return inner(F).w(*pt((hc[0] + SNOUT[0] + SNOUT[2], hc[1] + SNOUT[1])))


def body(F, K, mood="open", nod=0.0, mouth=0.0, arm=0.0, arm_far=None, step=0.0, sway=0.0, tail_pts=None, look=0.0,
         bob=0.0, face_on=True, neck=0.0, swing=0.0):
    """긴 목 브라키오 → 레이어. dino() 가 K.body 로 부른다(neck · swing 은 이 모듈 장면만 씀).
    arm 은 가까운 앞발을 든 정도(네 발이라 팔 대신)"""
    Fi = inner(F)
    s = Fi.s
    C = H()
    _, hf, ho, j, a = pose_of(neck, nod, swing)             # hf: 머리 제 좌표 거리함수 → 안쪽 캐논

    rt = max(2.4, 2.0 / s)                                  # 꼬리 · 다리 · 목은 판에서 1.6칸 넘게(틀과 같은 셈)
    rl = max(1.9, 1.7 / s)
    rn0, rn1 = max(3.0, 1.9 / s), max(2.6, 1.7 / s)
    fy = max(1.2, 1.2 / s)
    tp = tail_of(TAIL_CURL if tail_pts is TAIL_UP else (tail_pts or TAIL), sway)
    tl = chain(tp, rt, max(0.9, 1.5 / s))
    by = BODY[1] + bob * 0.4
    bd = ell(BODY[0], by, BODY[2] + bob * 0.3, BODY[3] - bob * 0.4)
    lift = 0.6 * max(0.0, arm)

    def leg(x, top, bot):
        return union(taper(x, top, rl * 1.05, x, bot - rl, rl), ell(x + 0.3, bot - fy, rl * 1.15, fy))
    far = [leg(1.8 - 0.5 * step, 10.6, VF - 0.5), leg(-6.2 + 0.5 * step, 11.0, VF - 0.5)]
    near = [leg(0.4 + 0.5 * step, 10.6, VF - lift), leg(-7.6 - 0.5 * step, 11.0, VF)]
    nt = j
    nk = taper(NB[0], NB[1], rn0, nt[0] + 0.2 * ND[0], nt[1] + 0.2 * ND[1], rn1)
    hd = hf(smin(1.0, smin(1.4, ell(*HEAD), ell(*SNOUT)), ell(*CREST)))
    allf = [tl, *far, *near, nk, bd, hd]
    out = [base(*[Fi.f(g) for g in allf])]
    out.append(part(Fi.f(tl), C.base))
    for g in far:
        out.append(part(Fi.f(g), C.far))
    out.append(part(Fi.f(nk), C.base))                    # 목은 몸 뒤에서 솟는다 — 어깨 테가 목 밑을 가름
    nkb = inter(grow(nk, -LINE_IN), lambda u, v: nk(u - 1.25 * rn1 * -ND[1], v - 1.25 * rn1 * ND[0]))
    out.append(flat(Fi.f(nkb), C.belly))                  # 목 앞 배 띠
    for g in near:
        out.append(part(Fi.f(g), C.base))
    out.append(part(Fi.f(bd), C.base))
    out.append(flat(Fi.f(inter(grow(bd, -LINE_IN), ell(BODY[0] + 1.6, by + 4.4, 5.6, 2.8))), C.belly))   # 배
    if s >= 0.5:                                           # 등 무늬 — 작으면 얼룩이라 뺀다
        sc = lerp(C.base, C.dark, 0.45)
        for u, v, r in SPOTS:
            out.append(flat(Fi.f(inter(ell(u, v + bob * 0.4, r, r), grow(bd, -1.2))), sc))
    out.append(part(Fi.f(hd), C.base))
    chin = hf(inter(smin(1.4, ell(*HEAD), ell(*SNOUT)), ell(4.4, 4.8, 5.4, 2.4)))
    out.append(flat(Fi.f(grow(chin, -LINE_IN)), C.belly))
    if face_on:
        Fh = sub(Fi, *ho)                                  # 머리 원점이 옮겨 간 자리에서 합친 각만큼 — 두 돌림의 합은 한 돌림
        out += dface(Fh, KL, Pose(a, piv=(0.0, 0.0)), mood, mouth, look)
    return out


KL = Kind()                                               # 얼굴용(머리 제 좌표) 주둥이
KL.snout, KL.head = SNOUT, HEAD


def _outer(u, v):
    return PV[0] + Z * (u - PV[0]), PV[1] + Z * (v - PV[1])


K = Kind()                                                # 틀에 보이는 생김새 — 머리 · 주둥이 자리는 바깥 캐논으로(연필 칸이 읽음)
K.quad = True
K.teeth = 0                                               # 이 없음(taste.md 톱니 이빨)
K.spots = ()
K.body = body
K.head = (*_outer(HU, HV), HEAD[2] * Z, HEAD[3] * Z)
K.snout = (*_outer(HU + SNOUT[0], HV + SNOUT[1]), SNOUT[2] * Z, SNOUT[3] * Z)


def sc_arrow(fr, g):
    """화살표 날개 오른쪽 아래에 선 브라키오가 왼쪽을 보고 목을 늘였다 줄였다 하며 화살표 끝을 올려다봄 · 고개 까딱. 화살표가 맨 위"""
    ph, k = ph_k(fr)
    sw = sin(ph)
    s = 0.72
    wx, wy = g["wing"]
    ox = min(wx + 3.4, 30.2 - 12.8 * s)                   # 말린 꼬리 끝(바깥 캐논 -12.8)이 판 안에
    oy = min(wy + 2.0, 30.4 - 14.0 * s)                   # 발바닥(바깥 캐논 14)이 판 안에
    out = body(DF(ox, oy, s, fx=-1), K, "blink" if k == 8 else "open", nod=-0.42 + 0.1 * sw, neck=1.0 + 1.0 * sw,
               swing=-0.14 + 0.06 * sw, sway=0.8 * sw, look=0.6, tail_pts=TAIL_UP)
    return out + arrow_layers(g)


def leaves(n, k):
    """오른쪽 위에서 늘어진 나뭇가지 — 잎 n 장(남은 것만)"""
    sw = 0.25 * sin(pi * k / 6)
    stem = chain([(31.6, 2.2), (26.0, 3.2), (19.6, 5.2 + sw)], 0.75, 0.55)
    out = [base(stem), part(stem, STEM, shade=hx("7a5838"), ink=hx("5a3e26"), line=0.5, sh=0.0)]
    spots = ((21.2, 8.8, 0.25), (24.8, 7.4, -0.2), (28.4, 5.8, 0.15))
    for x, y, t in spots[3 - n:]:
        lf = oell(x, y + sw, 1.6, 2.5, t)
        out += [base(lf), part(lf, LEAF, shade=LEAF_D, ink=hx("3f7a32"), line=0.5)]
    return out


REACH = (0.0, 0.3, 0.7, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.7, 0.3, 0.0)


def sc_wait(fr):
    """목을 쭉 올려 가지의 나뭇잎을 냠냠 — 올라가 잎을 한 장씩 먹고 내려온다. 먹을 때 눈웃음 · 입 오물"""
    ph, k = ph_k(fr)
    r = REACH[k]
    n = 3 if k < 6 else 2 if k < 8 else 1
    out = leaves(n, k)
    out += body(DF(15.2, 16.6, 0.88), K, "happy" if 5 <= k <= 8 else "blink" if k == 11 else "open", nod=-0.2 * r,
                neck=3.6 * r, swing=0.34 * r, mouth=0.6 if k in (5, 7) else 0.0, sway=0.8 * sin(ph))
    return out


def sc_no(fr):
    """금지 표지 안에서 쳐든 머리를 목째 시계추처럼 도리도리 — 질끈. 표지가 위"""
    ph, k = ph_k(fr)
    sw = sin(ph)
    out = body(DF(16.4, 13.2, 0.62), K, "squeeze", swing=0.32 * sw, nod=0.1 * sw, step=0.6 * sw, sway=-0.8 * sw,
               tail_pts=TAIL_UP)
    if k % 6 in (2, 3):
        out += drop(22.2, 7.0, 0.7, 1.0)
    return out + no_sign()


def sc_hand(K_, fr, hot=HAND_HOT, nod0=-1.0):
    """공용 손 칸과 같은 짓(고개를 젖혀 주둥이 끝으로 위를 콕콕, 그 끝이 핫스팟) — 주둥이 끝을 이 몸의 관절로 잰다"""
    ph, k = ph_k(fr)
    p = (0, 0, 1, 2, 0, 0, 1, 2, 0, 0, 0, 0)[k]
    nod = nod0 - 0.1 * p
    mood = "squeeze" if p == 2 else "blink" if k == 10 else "happy" if p == 1 else "open"
    s = 0.8
    nk = 2.6 - 0.4 * p                                     # 목을 늘여 젖힌 머리 밑으로 목이 보이게 — 콕 할 때 몸이 따라 내려감
    tx, ty = snout_at(DF(0.0, 0.0, s, fx=-1), nod, nk)
    hx_, hy_ = hot[0] + 0.5, hot[1] + 0.5 + 0.55
    F = DF(hx_ - tx, hy_ - ty, s, fx=-1)
    out = []
    if p == 2:
        out += zip_lines(hx_, hy_, 2, 1.4, 2.4, -pi / 2, 1.9)
    out += body(F, K_, mood, nod=nod, neck=nk, arm=1.8 if p else 0.8, sway=1.0 * sin(ph), tail_pts=TAIL_UP)
    return out


class Brachio(DinoPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Brachio(HIDE, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no}, shared={"hand": sc_hand})

register("brachio", PET)
catkit.load()

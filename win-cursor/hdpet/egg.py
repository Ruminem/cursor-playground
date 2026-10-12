# SPDX-License-Identifier: Apache-2.0
"""갓 깬 아기공룡(egganim) 고화질 — 공룡 틀(dinokit)에 몸빛 · 알껍데기 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

표식은 알껍데기 둘: 머리 위 모자(아래 테가 지그재그로 깨짐 · 민트 점)와 몸 아래를 감싼 껍데기(위 테가 지그재그).
몸 앞을 덮는 껍데기는 Kind 갈고리에 자리가 없어 Kind.body 로 몸을 감싼다 — body 안에서 body 없는 BARE 로 dino() 를
부르고 그 위에 껍데기 · 모자 · 앞 팔을 얹는다. 공용 14칸도 이 body 를 거쳐 저절로 알 속 아기가 된다.
픽셀 판(지운 gen/dino.py)의 짓 그대로: 날개 끝 옆 껍데기 속에서 올려다보며 모자가 들썩(화살표), 껍데기에 쏙 들어가
꾸벅꾸벅 흔들다가 모자가 퐁 뜨며 쑥 일어나 만세(기다림), 알 속으로 쏙 숨어 금 사이로 눈만 내놓고 알째 도리도리(금지).
"""
from math import atan2, hypot

from hd import union

from . import catkit, register
from .catkit import ell, oell, inter, taper, part
from .dinokit import (DF, TAIL_UP, Hide, Kind, Pose, DinoPet, dino, star, no_sign, arrow_layers, ph_k, hx, sin,
                      EGG_SHELL, EGG_SPOT)

HIDE = Hide(hx("a8e6cf"), hx("6fc4a8"), hx("e2f8ee"), EGG_SHELL, hx("eadcc0"))
SHELL_D = hx("eadcc0")                                    # 껍데기 그늘 띠 — 털빛 그늘(민트)을 쓰면 크림 위에 초록 띠가 진다

SHELL = (-0.4, 6.0, 7.6, 7.0)                             # 아래 껍데기 타원(캐논) — 위 테(TOP)가 타원 허리라 반쪽 알 컵이 된다.
                                                          # 테를 타원 위쪽에 두면 입구가 좁아 숨은 머리가 껍데기 밖으로 삐져 산 모양
TOP = 5.4                                                 # 아래 껍데기 위 테(골) — 이가 위로 솟는다
CAP = (0.4, -6.2, 6.2, 4.4, -0.15)                        # 모자 타원(뒤로 살짝 젖힘)
CAP_BOT = -4.4                                            # 모자 아래 테(골) — 이가 아래로 처진다
TUCK = [(-4.2, 9.4), (-5.2, 10.0), (-5.8, 9.4), (-6.0, 8.6)]   # 숨을 때 껍데기 속에 만 꼬리
CAP_SPOTS = ((2.4, -7.8, 1.05), (-2.2, -6.6, 0.85), (0.2, -9.4, 0.6))
SHELL_SPOTS = ((-4.4, 9.8, 1.05), (2.0, 11.0, 0.9), (-1.4, 7.4, 0.7))


class Bare(Kind):
    """껍데기 없는 알 속 아기 — 머리 뒤 무늬는 뺀다(모자 점과 겹쳐 얼룩)"""
    spots = ()


BARE = Bare()


def _tri(u, w):
    t = (u / w) % 2.0
    return t if t <= 1.0 else 2.0 - t


def teeth(s):
    """깨진 테의 이 반폭 · 높이(캐논). 판에서 1.5칸 · 1칸 아래로는 안 줄인다 — 32px 에서 지글거리지 않고 이 두셋으로 읽히게"""
    return max(1.5, 1.5 / s), max(1.0, 1.0 / s)


def below_zig(top, w, a):
    """지그재그 줄(골 top, 이 끝 top - a) 아래 — 기울기만큼 거리를 줄여 먹선 굵기를 맞춘다"""
    k = 1.0 / hypot(1.0, a / w)
    return lambda u, v: (top - a * _tri(u + 0.5 * w, w) - v) * k


def above_zig(bot, w, a):
    k = 1.0 / hypot(1.0, a / w)
    return lambda u, v: (v - bot - a * _tri(u, w)) * k


def spotted(pts, r_min):
    """[(art x, art y, r)…] 안이면 민트 점, 아니면 껍데기 크림"""
    pts = [(x, y, max(r, r_min) ** 2) for x, y, r in pts]

    def col(x, y):
        for cx, cy, rr in pts:
            if (x - cx) ** 2 + (y - cy) ** 2 < rr:
                return EGG_SPOT
        return EGG_SHELL
    return col


def hatchling(F, mood="open", nod=0.0, mouth=0.0, arm=0.0, arm_far=None, step=0.0, sway=0.0, tail_pts=None, look=0.0,
              bob=0.0, face_on=True, sink=0.0, lift=0.0, hide=False, arm_front=True):
    """알 속 아기 → 레이어. F 는 껍데기 자리, sink 는 아기가 껍데기 속으로 내려간 만큼(캐논), lift 는 모자가 뜬 만큼.
    hide 면 아기 층을 '껍데기 위 테 위 ∪ 껍데기 타원' 안으로 잘라 껍데기 밖 아래로 삐져나온 발 · 꼬리를 지운다"""
    s = F.s
    C = catkit.C
    Fb = DF(*F.w(0.0, sink), s, atan2(F.sn, F.c), F.fx) if sink else F
    out = dino(Fb, BARE, mood, nod=nod, mouth=mouth, arm=arm, arm_far=arm_far, step=step, sway=sway, tail_pts=tail_pts,
               look=look, bob=bob, face_on=face_on)
    w, a = teeth(s)
    shell = inter(ell(*SHELL[:4]), below_zig(TOP, w, a))
    P = Pose(nod)
    cap = P.hf(inter(oell(CAP[0], CAP[1] - lift, *CAP[2:]), above_zig(CAP_BOT - lift, w, a)))
    shf, capf = F.f(shell), Fb.f(cap)
    if hide:
        keep = F.f(union(ell(*SHELL[:4]), lambda u, v: v - TOP))
        for L in out:
            L["f"] = (lambda f0: lambda x, y: max(f0(x, y), keep(x, y)))(L["f"])
    out[0]["f"] = union(out[0]["f"], shf, capf)         # 바닥(먹 · 밝은 테 · 그림자)에 껍데기 둘을 더해 한 스티커로
    r_min = 0.75 if s < 0.6 else 0.6
    n = 2 if s < 0.6 else 3                              # 작으면 점 둘 — 셋이면 먹선 안에서 뭉친다
    sp = [(*F.w(u, v), r * s) for u, v, r in SHELL_SPOTS[:n]]
    cp = [(*Fb.w(*P.hp(u, v - lift)), r * s) for u, v, r in CAP_SPOTS[:n]]
    out.append(part(shf, spotted(sp, r_min), shade=SHELL_D))
    out.append(part(capf, spotted(cp, r_min), shade=SHELL_D))
    if arm_front:                                        # 앞 팔은 껍데기 테에 걸친다(틀과 같은 자리 · 굵기)
        ra = max(1.05, 1.7 / s)
        out.append(part(Fb.f(taper(2.2, 6.6, ra, 4.2, 7.6 - arm, ra * 0.9)), C.base))
    return out


def egg_body(F, K, **kw):
    """Kind.body — 공용 14칸이 부르는 dino() 가 이리로 온다"""
    return hatchling(F, **kw)


class EggKind(Kind):
    body = staticmethod(egg_body)
    spots = ()


K = EggKind()


def at_bottom(px, py, s, ang=0.0, fx=1):
    """껍데기 밑(캐논 (-1, 13))이 (px, py) 에 오고 그 둘레로 ang 만큼 기운 DF — 흔들흔들"""
    bx, by = DF(0.0, 0.0, s, ang, fx).w(-1.0, 13.0)
    return DF(px - bx, py - by, s, ang, fx)


def sc_arrow(fr, g):
    """날개 끝 오른쪽 아래 껍데기 속에서 화살표를 올려다봄 — 모자가 들썩 뜰 때 눈웃음 · 반짝, 짧은 팔을 화살표 쪽으로. 화살표가 맨 위"""
    ph, k = ph_k(fr)
    s = 0.72
    wx, wy = g["wing"]
    ox = min(wx + 6.0, 29.1 - 9.4 * s)                    # 꼬리 끝(캐논 -9.4 + 반지름)이 판 안에
    oy = min(wy + 1.6, 30.4 - 14.0 * s)                   # 발바닥(캐논 14)이 판 안에
    pop = k in (2, 3, 4, 5)
    mood = "happy" if k in (3, 4) else "blink" if k == 8 else "open"
    out = hatchling(DF(ox, oy, s, fx=-1), mood, nod=-0.3, arm=1.2 + 1.0 * abs(sin(ph)), arm_far=1.6,
                    sway=0.8 * sin(ph), tail_pts=TAIL_UP, look=0.5, lift=1.8 if pop else 0.0)
    if k in (3, 4):
        out += star(ox - 4.6, oy - 9.6 - 0.4 * (k - 3), 1.5, 0.5)
    return out + arrow_layers(g)


def sc_wait(fr):
    """껍데기에 쏙 들어가 꾸벅꾸벅 흔들흔들 → 모자가 퐁 뜨며 쑥 일어나 만세 · 반짝 → 다시 반쯤 쏙"""
    ph, k = ph_k(fr)
    s = 0.92
    pop = k in (6, 7, 8, 9)
    rock = 0.14 * sin(2 * ph) if k < 6 else 0.0
    sink = 3.6 if k < 6 else -2.0 if pop else 1.8        # 만세 때는 컵 위로 쑥(발은 컵 속)
    F = at_bottom(16.0, 29.8, s, rock)
    out = hatchling(F, "happy" if pop else "blink" if k < 6 else "open", nod=-0.12 if pop else 0.0, mouth=0.35 if pop else 0.0,
                    arm=2.6 if pop else 0.0, arm_far=2.6 if pop else 0.0, sway=0.8 * sin(ph) if pop else 0.0,
                    tail_pts=TAIL_UP if pop else TUCK, lift=3.0 if pop else 0.0, sink=sink, hide=True, arm_front=pop)
    if pop:
        j = (k - 6) % 2
        out += star(5.6, 7.0 - j, 1.8, 0.6) + star(26.6, 6.0 + j, 1.8, 0.6)
    return out


def sc_no(fr):
    """알 속으로 쏙 숨어 모자를 닫고 금 사이로 눈만 — 알째 도리도리, 질끈. 표지가 위"""
    ph, k = ph_k(fr)
    s = 0.7                                               # 0.62 · 쏙 4.4 면 모자와 테 사이 틈이 판에서 1.4칸 — 먹선만 남았다
    F = at_bottom(17.4, 22.2, s, 0.2 * sin(ph))           # 가운데보다 오른쪽 — 눈이 빗금 위(오른쪽 위 반)에 오게
    out = hatchling(F, "squeeze" if k % 6 in (2, 3) else "open", sink=2.6, hide=True, tail_pts=TUCK, arm=-1.0, arm_front=False)
    return out + no_sign()


class Egg(DinoPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Egg(HIDE, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no})

register("egg", PET)
catkit.load()

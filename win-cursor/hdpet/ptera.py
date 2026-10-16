# SPDX-License-Identifier: Apache-2.0
"""아기 프테라노돈(pteraanim) 고화질 — 공룡 틀(dinokit)에 몸빛 · 몸(Kind.body) · 화살표 · 기다림 · 금지 세 칸만 얹는다.

선 치비 공룡 틀이 안 맞아 몸을 통째로 갈아 끼운다: 동그란 큰 분홍 머리 · 뒤로 뻗은 보라 볏 · 노란 부리(이 없음) ·
작은 몸 · 보라 날개막 둘 · 뭉툭한 노란 발. 캐논은 티라노 틀과 같다(머리 가운데 (0, 0) · 발바닥 v 13.8 · 부리 끝 u ≈ 10.6)
— 공용 14칸이 같은 배율 · 자리로 부르므로. 픽셀 판(지운 gen/dino.py)은 몸 단위가 작아 1.3 배 키웠는데(KBOOST),
여기서는 머리 · 몸을 처음부터 그만큼 크게 잡았다.
공용 칸이 dino() 에 주는 인자는 이렇게 받는다: arm → 앞 날개를 드는 각도 · 펼친 정도, arm_far → 먼 날개,
step → 발, sway → 볏 끝 까딱, nod → 머리(부리 · 볏 · 얼굴째) 까딱, mouth → 아래 부리 벌림, bob → 몸 눌림.
tail_pts 는 꼬리가 없어 안 쓴다.

픽셀 판의 짓 그대로: 화살표 빗변에 내려앉아 날개를 폈다 접었다 · 볏 까딱(화살표), 제자리 날갯짓으로 몸이 오르내림(기다림),
두 날개를 몸 앞에 X 로 엇걸고 볏을 꼿꼿(금지).
"""
from . import catkit, register
from .dinokit import (DF, Hide, Kind, DinoPet, Pose, no_sign, arrow_layers, edge_pt, ph_k, hx, sin, cos, pi,
                      ell, taper, capsule, union, inter, grow, arc, lerp, clamp, smooth, base, part, flat, soft, shut,
                      H, BLUSH, HI, LINE_IN, drop, turn, circle, rpoly, sc_hand, sc_ibeam)

BEAK, BEAK_D = hx("f6d58a"), hx("d9a84a")
PURPLE_D = hx("8a62c4")

HIDE = Hide(hx("f6a8c8"), hx("d97ea6"), hx("fde0ea"), hx("b892e6"), PURPLE_D)

HEAD = (0.0, 0.0, 5.8, 5.0)
FOOT_V = 13.8

# 날개막 한 장(어깨 둘레 제 좌표: x 는 날개 끝 쪽, y 는 뒷전 쪽) — 접은 것과 편 것을 섞는다
OPEN = [(0.0, -1.0), (5.6, -2.4), (14.6, -1.0), (9.6, 0.8), (5.8, 2.8), (1.4, 5.4)]   # 길고 끝이 뾰족한 익룡 날개
SHUT = [(0.0, -1.0), (3.2, -1.6), (7.4, -0.6), (5.6, 1.2), (3.4, 2.6), (0.8, 3.8)]
SH_NEAR, SH_FAR = (-0.6, 5.8), (0.6, 5.2)


def wing_geo(S, a, spread, side=-1):
    """어깨 S 에서 뒤(side -1, -u) 또는 앞(side 1, +u)으로 뻗은 날개를 a(라디안, + 가 위)만큼 들어 올린 꼭짓점"""
    dx, dy = side * cos(a), -sin(a)
    nx, ny = (dy, -dx) if side < 0 else (-dy, dx)          # 뒷전은 늘 아래(날개를 수평으로 폈을 때)
    pts = []
    for (x0, y0), (x1, y1) in zip(SHUT, OPEN):
        x, y = x0 + (x1 - x0) * spread, y0 + (y1 - y0) * spread
        pts.append((S[0] + dx * x + nx * y, S[1] + dy * x + ny * y))
    return pts


def wing_f(pts, s):
    """날개막 — 꼭짓점 다각형을 둥글린다. 끝 · 뒷전이 판에서 먹선만 남지 않게 둥글림을 s 로 나눠 키운다"""
    return grow(rpoly(pts, 0.7), max(0.0, 0.8 / s - 0.9))   # rpoly 의 r 을 키우면 꼭짓점이 가운데로 뭉개져 밖으로 키운다


def beak_f(s, mouth=0.0):
    """노란 부리(위 · 아래). 판에서 밑동 반지름 1.5칸 · 끝 0.7칸 아래로 안 가게(먹선 안에 노랑이 남게)"""
    rb, rt = max(1.9, 1.5 / s), max(0.6, 0.7 / s)
    if mouth <= 0:
        return [taper(3.6, 0.6, rb, 10.0, 0.9, rt)]
    up = taper(3.6, 0.2, rb * 0.8, 10.0, 0.4, rt)
    lo = turn(taper(3.8, 1.5, rb * 0.62, 9.0, 1.7, rt * 0.9), 0.45 * mouth, 3.8, 1.5)
    return [lo, up]


def pface(F, P, mood="open", look=0.0):
    """3/4 옆얼굴 — 앞 눈 · 먼 눈(조금 작게), 눈 밑 분홍 볼. 코 · 입은 없다(부리가 그 몫).
    눈은 까만 콩 + 왼쪽 위 흰 반짝 하나(dface 와 같은 셈). angry 는 콩 눈 위에 부리 쪽으로 처진 눈썹"""
    s = F.s
    C = H()
    out = []
    er = max(1.15 * s, 0.95)
    eyes = ((-1.4, -0.3, 0.86), (2.4, 0.1, 1.0))
    for u, v, k in eyes:
        bx, by = F.w(*P.hp(u + 0.2, v + 2.5))
        rx = max(1.25 * s, 0.85) * k
        out.append(soft(ell(bx, by, rx, rx * 0.6), BLUSH, 0.85))
    sign = F.fx
    for i, (u, v, k) in enumerate(eyes):
        ex, ey = F.w(*P.hp(u + 0.35 * look, v))
        r = er * k
        if mood == "squeeze":
            d = (1 if i == 1 else -1) * sign
            w = max(0.3, 0.22 * r)
            g = union(capsule(ex - d * r * 0.8, ey - r * 0.75, ex + d * r * 0.55, ey, w),
                      capsule(ex + d * r * 0.55, ey, ex - d * r * 0.8, ey + r * 0.75, w))
            out.append(flat(g, C.eye))
        elif mood in ("blink", "happy"):
            out.append(shut(ex, ey, r * 1.05, mood))
        elif mood == "sad":
            out.append(flat(ell(ex, ey + r * 0.15, r * 0.8, r * 0.95), C.eye))
            out.append(flat(capsule(ex - r * 0.9, ey - r * 1.5 - sign * r * 0.3, ex + r * 0.9, ey - r * 1.5 + sign * r * 0.3,
                                    max(0.22, 0.16 * r)), C.eye, 0.9))
        else:
            out.append(flat(ell(ex, ey, r * 0.82, r), C.eye))
            hl = max(0.34 * r, 0.3)
            out.append(flat(circle(ex - 0.28 * r, ey - 0.36 * r, hl), HI))
            if mood == "angry":                           # 부리 쪽으로 처진 눈썹
                out.append(flat(capsule(ex - sign * r * 0.9, ey - r * 1.75, ex + sign * r * 0.9, ey - r * 1.15,
                                        max(0.26, 0.2 * r)), C.eye, 0.95))
    return out


def wing_of(arm):
    """공용 칸의 arm(팔 끝을 든 정도, 0 – 2.8) → (각도, 펼침). 0 이면 몸 옆에 접어 뒤로 늘어뜨린다"""
    return -0.55 + 0.42 * arm, clamp(0.12 + 0.24 * arm)


def ptera(F, mood="open", nod=0.0, mouth=0.0, near=(-0.55, 0.12), far=(-0.45, 0.12), step=0.0, crest=0.0, look=0.0,
          bob=0.0, face_on=True, cross=0.0, spread=False, crest_len=1.0):
    """프테라 → 레이어 목록. near · far 는 (각도, 펼침). cross 가 0 보다 크면 두 날개를 몸 앞에 X 로 엇건다(1 이 꽉).
    crest_len 은 볏 길이 비율 — 볏 끝이 32칸 판 밖으로 나가는 칸만 줄인다.
    spread 면 3/4 앞모습처럼 앞 날개는 앞(부리 쪽)으로, 먼 날개는 뒤로 양쪽에 편다 — 옆모습으로 뒤로만 뻗은 날개는
    위아래로 펄럭여도 볏 · 지느러미로 읽혀서(기다림)"""
    s = F.s
    C = H()
    P = Pose(nod)
    by = 7.8 + bob * 0.4
    body = ell(-1.0, by, 4.6 + bob * 0.3, 4.2 - bob * 0.4)
    head = P.hf(ell(*HEAD))
    cr0, cr1 = max(2.2, 1.7 / s), max(0.8, 1.0 / s)
    crest_f = P.hf(taper(-2.4, -2.4, cr0, -2.4 - 8.0 * crest_len, -2.4 - (2.4 + crest * 0.9) * crest_len, cr1))
    beak = [P.hf(g) for g in beak_f(s, mouth)]
    fy = max(1.3, 1.5 / s)
    fr_ = max(1.9, 1.6 / s)
    foot_far = ell(-2.8 - step * 0.6, FOOT_V - fy, fr_ * 0.92, fy)
    foot_near = ell(0.8 + step * 0.6, FOOT_V - fy, fr_, fy)
    wing_c, wing_far_c = C.deco, lerp(C.deco, PURPLE_D, 0.55)
    w_sh = lerp(C.deco, PURPLE_D, 0.5)
    if cross:
        rr, rt = max(2.0, 1.7 / s), max(0.9, 1.0 / s)
        c = cross
        # 눕힌 X(가로 26°쯤) — 45° 면 금지 표지 빗금과 겹쳐 묻힌다
        wf_far = taper(6.0, 4.0, rr, 6.0 - 14.6 * c, 4.0 + 7.0 * c + (1 - c) * 3.0, rt)
        wf_near = taper(-7.6, 4.0, rr, -7.6 + 15.0 * c, 4.0 + 7.0 * c + (1 - c) * 3.0, rt)
        back_ = [(foot_far, lerp(BEAK, BEAK_D, 0.5), BEAK_D)]
        # 둘 다 밝은 보라 — 먼 날개를 짙게 하면 32 에서 몸 앞의 먹 덩어리가 된다
        front_ = [(wf_far, lerp(C.deco, PURPLE_D, 0.22), PURPLE_D), (wf_near, wing_c, w_sh)]
    else:
        if spread:
            wf_far, wf_near = wing_f(wing_geo((-2.6, 5.4), *far), s), wing_f(wing_geo((1.4, 5.8), *near, side=1), s)
        else:
            wf_far, wf_near = wing_f(wing_geo(SH_FAR, *far), s), wing_f(wing_geo(SH_NEAR, *near), s)
        back_ = [(wf_far, wing_far_c, PURPLE_D), (foot_far, lerp(BEAK, BEAK_D, 0.5), BEAK_D)]
        front_ = [(wf_near, wing_c, w_sh)]
    mid_ = front_ if spread else []                          # 앞으로 편 날개는 머리 밑에 — 부리 · 얼굴을 안 덮게
    front_ = [] if spread else front_
    allf = [p[0] for p in back_ + mid_ + front_] + [crest_f, body, foot_near, head] + beak
    out = [base(*[F.f(g) for g in allf])]
    for g, col, sh in back_:
        out.append(part(F.f(g), col, shade=sh))
    out.append(part(F.f(crest_f), C.deco, shade=w_sh))      # 볏 — 짙은 보라면 32 에서 마녀 모자로 읽혀 날개와 같은 밝은 보라
    out.append(part(F.f(body), C.base))
    out.append(part(F.f(foot_near), BEAK, shade=BEAK_D))
    out.append(flat(F.f(inter(body, ell(1.0, by + 0.8, 3.0, 3.4))), C.belly))      # 배
    for g, col, sh in mid_:
        out.append(part(F.f(g), col, shade=sh))
    out.append(part(F.f(head), C.base))
    chin = P.hf(inter(ell(*HEAD), ell(2.6, 4.2, 4.6, 2.4)))
    out.append(flat(F.f(grow(chin, -LINE_IN)), C.belly))
    for g in beak:
        out.append(part(F.f(g), BEAK, shade=BEAK_D))
    if face_on:
        out += pface(F, P, mood, look)
    for g, col, sh in front_:
        out.append(part(F.f(g), col, shade=sh))
    return out


def body(F, K, mood="open", nod=0.0, mouth=0.0, arm=0.0, arm_far=None, step=0.0, sway=0.0, tail_pts=None, look=0.0,
         bob=0.0, face_on=True, crest_len=1.0):
    """Kind.body 갈고리 — 공용 칸의 dino() 인자를 프테라 짓으로 옮긴다(머리글 참고)"""
    arm_far = arm if arm_far is None else arm_far
    a, sp = wing_of(arm_far)
    return ptera(F, mood, nod, mouth, near=wing_of(arm), far=(a + 0.1, sp), step=step, crest=sway, look=look, bob=bob,
                 face_on=face_on, crest_len=crest_len)


def kind(crest_len=1.0):
    K = Kind()
    K.body = (lambda F, K, **kw: body(F, K, crest_len=crest_len, **kw)) if crest_len != 1.0 else body
    K.head = HEAD
    K.snout = (6.8, 0.9, 3.8, 1.6)                         # 부리 끝(콕 칸 핫스팟) — taper 끝 (10, 0.9) + 끝 반지름
    K.spots = ()
    return K


K = kind()
# 공용 칸은 티라노 자리 · 배율 그대로 부르는데 프테라 볏이 뒤로 길어(fx -1 이면 오른쪽) 판 오른쪽 밖으로 나가는 칸이 둘:
# 손(고개를 하늘로 젖혀 볏이 오른쪽 아래로 눕는다) · 글자(뼈 오른쪽 작은 몸). 그 둘만 볏을 줄여 같은 칸 함수를 부른다
SHARED = {"hand": lambda K_, fr: sc_hand(kind(0.7), fr), "ibeam": lambda K_, fr: sc_ibeam(kind(0.75), fr)}


def at_foot(px, py, s, fx):
    """발바닥(캐논 (-1, 13.8))이 (px, py) 에 오게 놓은 DF"""
    F0 = DF(0.0, 0.0, s, fx=fx)
    x0, y0 = F0.w(-1.0, FOOT_V)
    return DF(px - x0, py - y0, s, fx=fx)


EDGE_T, EDGE_OFF = 0.96, 0.5                             # 빗변(끝 0 … 날개 1)의 어디 · 바깥 테 밖으로 얼마 — 몸이 화살표에 안 가리게


def sc_arrow(fr, g):
    """화살표 빗변에 내려앉아 끝 쪽을 보고 날개를 폈다 접었다 — 볏이 까딱, 한 번 끔뻑. 화살표가 맨 위"""
    ph, k = ph_k(fr)
    s = 0.95
    px, py = edge_pt(g, EDGE_T, EDGE_OFF)
    top = at_foot(px, py, s, -1).w(-1.0, -6.4)[1]          # 볏 · 머리 위 끝
    py += max(0.0, 3.4 - top)                              # 스티커는 빗변이 높아 머리가 판 위로 나간다 — 발을 빗변 안쪽으로 내림
    F = at_foot(px, py, s, -1)
    op = 0.5 + 0.5 * cos(ph)                               # 1 활짝 … 0 접음
    out = ptera(F, "blink" if k == 6 else "open", nod=-0.08 * sin(ph), near=(0.15 + 0.9 * op, 0.25 + 0.75 * op),
                far=(0.3 + 0.9 * op, 0.25 + 0.75 * op), crest=0.8 * sin(ph), crest_len=0.8)   # 스티커 판에서 볏 끝이 판 위로 나가서
    return out + arrow_layers(g)


def sc_wait(fr):
    """제자리 날갯짓 — 두 날개가 위아래로 펄럭이고, 내려칠 때 몸이 떠오른다. 발은 대롱"""
    ph, k = ph_k(fr)
    w = cos(ph)                                            # 1 위로 … -1 아래로
    s = 0.86
    F = DF(15.2, 10.6 + 0.9 * w, s)
    out = ptera(F, "blink" if k == 9 else "happy" if k in (3, 4) else "open", nod=0.06 * w, spread=True,
                near=(0.1 + 0.75 * w, 0.8), far=(0.2 + 0.75 * w, 0.8), crest=-0.6 * w, bob=0.3 * (1 + w) / 2)
    return out


def sc_no(fr):
    """금지 표지 안에서 두 날개를 몸 앞에 X 로 엇걸고 볏을 꼿꼿 — 질끈 · 찡그림 번갈아, 까딱. 표지가 위"""
    ph, k = ph_k(fr)
    sq = k % 6 < 3
    s = 0.72
    F = DF(15.6, 7.8 + (0.4 if k % 4 < 2 else 0.0), s)
    out = ptera(F, "squeeze" if sq else "angry", nod=-0.1 if sq else 0.0, cross=1.0, crest=1.2)
    if sq and k % 6 == 1:
        out += drop(20.0, 6.0, 0.75, 1.1)
    return out + no_sign()


class Ptera(DinoPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Ptera(HIDE, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no}, shared=SHARED)

register("ptera", PET)
catkit.load()

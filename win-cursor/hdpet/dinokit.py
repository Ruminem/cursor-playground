# SPDX-License-Identifier: Apache-2.0
"""아기 공룡 · 애니 고화질 공용 틀 — 치비 공룡(머리가 몸만 한 옆모습 아기) · 스티커 채색은 냥이 틀(catkit) 그대로.

픽셀 판(지운 gen/dino.py)이 귀여운 까닭 — 둥근 큰 머리에 짧은 주둥이, 까만 콩 눈, 눈 밑 분홍 볼, 작은 몸 · 짧은 팔 ·
뭉툭한 발 · 굵은 꼬리 — 을 HD 로 옮겼다. 마리마다 다른 것은 몸빛(Hide)과 표식 하나(뿔 · 등판 · 곤봉 · 돛 · 볏 …,
Kind 의 갈고리)와 화살표 · 기다림 · 금지 세 칸이고, 나머지 14칸은 여기 하나다(작은 화살표 + 작은 공룡 + 소품 넷 ·
주둥이로 콕 · 열매 노려보기 · 뼈 I · 쿵쿵 · 기지개 넷 · 연필 · 올려다보며 깡충).
좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 공룡 제 좌표(캐논)는 머리 가운데 (0, 0), 아래가 +v,
오른쪽을 본다 — DF 의 fx = -1 이면 왼쪽을 본다. 장면은 NF 장으로 나뉜다(k = round(fr × NF) % NF).

catkit 은 고치지 않는다(냥이 열 마리 재료라 고치면 다 다시 굽는다). 몸빛은 catkit 전역 C 에 끼워 쓴다(use).
"""
import math

from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

from . import catkit
from .catkit import (hx, ell, oell, inter, clip_y, rpoly, chain, taper, Frame, layer, base, part, flat, soft,  # noqa: F401
                     sticker, cur, small_arrow, sparkle, ARROW, TIP, cream_of, shaped, _edge, HI_WHITE, HI, PINK,
                     NF, LOOP, Pet, shut, Coat, use)

sin, cos, hypot, floor, pi, atan2 = math.sin, math.cos, math.hypot, math.floor, math.pi, math.atan2

# 공룡 묶음 공통(픽셀 판 팔레트 그대로)
OUT, EYE, RIM = hx("3a2a30"), hx("2a1c22"), hx("f6e9d2")
BLUSH, MOUTH, TONGUE = hx("f4a0b0"), hx("d8607a"), hx("f7a3b5")
LEAF, LEAF_D, STEM = hx("8fd16a"), hx("5ea84a"), hx("a07850")
SWEAT, SWEAT_D = hx("9fd4f4"), hx("5a9cc8")
DUST, DUST_D = hx("e6d6bc"), hx("c4b090")
SPARK = hx("fff3a0")
CHEV, CHEV_D = hx("f59a5a"), hx("c8642a")
BONE, BONE_D = hx("f6ead0"), hx("d8c49c")
SKIN, SKIN_D, SHIRT, SHIRT_D = hx("f7d7bc"), hx("e8bfa0"), hx("4a7fb5"), hx("2e5a88")
BERRY, BERRY_D, BERRY_L = hx("e8484a"), hx("b02a30"), hx("f47a74")
SIGN, SIGN_D, SIGN_L = hx("d64541"), hx("9e2b28"), hx("ef7a72")
PEN_Y, PEN_YD, PEN_W, PEN_G, PEN_E = hx("f6c84a"), hx("d9a032"), hx("f3d6a8"), hx("3a3a44"), hx("f4a0b0")
EGG_SHELL, EGG_SPOT = hx("fff6e2"), hx("7fcab4")


class Hide(Coat):
    """몸빛 하나 — base(몸) · dark(먼 쪽 팔다리 · 무늬) · belly(배 · 턱) · deco · deco_d(표식). 그늘 띠는 몸과 dark 사이"""

    def __init__(self, base_, dark, belly, deco, deco_d=None):
        super().__init__(base_, lerp(base_, dark, 0.55), OUT, EYE, RIM, ((EYE,) * 3,) * 2, cheek=BLUSH)
        self.dark, self.belly, self.deco = dark, belly, deco
        self.deco_d = deco_d or lerp(deco, OUT, 0.25)
        self.far = lerp(base_, dark, 0.4)


def H():
    return catkit.C


class DF(Frame):
    """catkit.Frame + 좌우 뒤집기(fx = -1 이면 왼쪽을 봄) + 화면 축 e 를 따라 sa 배 · 그 직각으로 sb 배 늘이기(기지개).
    늘이기는 (ox, oy) 둘레로 — 거리는 s × min(sa, sb) 로 어림(먹선이 얇아지는 쪽으로만 틀림)"""

    def __init__(self, ox=0.0, oy=0.0, s=1.0, ang=0.0, fx=1, e=(1.0, 0.0), sa=1.0, sb=1.0):
        super().__init__(ox, oy, s, ang)
        self.fx, self.e, self.sa, self.sb = fx, e, sa, sb

    def _st(self, dx, dy, k):
        if self.sa == 1.0 and self.sb == 1.0:
            return dx, dy
        ex, ey = self.e
        a, b = dx * ex + dy * ey, -dx * ey + dy * ex
        a, b = a * self.sa ** k, b * self.sb ** k
        return a * ex - b * ey, a * ey + b * ex

    def loc(self, x, y):
        dx, dy = self._st(x - self.ox, y - self.oy, -1)
        dx, dy = dx / self.s, dy / self.s
        return (dx * self.c + dy * self.sn) * self.fx, -dx * self.sn + dy * self.c

    def w(self, u, v):
        u *= self.fx
        dx, dy = self._st((u * self.c - v * self.sn) * self.s, (u * self.sn + v * self.c) * self.s, 1)
        return self.ox + dx, self.oy + dy

    def f(self, g):
        k, loc = self.s * min(self.sa, self.sb), self.loc
        return lambda x, y: k * g(*loc(x, y))


# ---- 마리마다 다른 것: 표식 갈고리 ----

class Kind:
    """한 마리의 생김새 갈고리. 다 캐논(오른쪽을 봄) 좌표의 거리함수를 (f, 색) 짝 목록으로 돌려준다.
      behind(P)  머리 뒤 · 몸 앞(프릴 · 볏 뒤쪽) — 머리와 같이 까딱(P.hf 로 감싸서 줌)
      back(P)    몸 뒤(등판 · 돛) — 몸에 붙어 안 까딱
      over(P)    머리 위(뿔 · 돔 · 볏) — 머리와 같이 까딱
      tail_end(P) 꼬리 끝(곤봉 · 가시) — P.tail 끝점에 붙임
    quad 면 짧은 팔 대신 앞발 둘로 땅을 짚는다. snout 는 주둥이 타원(cx, cy, rx, ry) — 길면 스피노 · 짧으면 파키.
    body 를 주면 dino() 가 그 몸을 대신 그린다(프테라 · 알처럼 선 치비 틀이 안 맞는 마리) — body(F, K, **dino 인자) → 레이어.
    틀 몸을 감싸 쓰려면 body 안에서 body 가 없는 Kind 로 dino() 를 부른다"""
    quad = False
    body = None
    snout = (3.6, 1.6, 4.4, 3.3)
    head = (0.0, 0.0, 6.6, 5.6)
    teeth = 0
    spots = ((-2.6, -3.6, 0.95), (-4.6, -1.4, 0.8), (-0.4, -4.8, 0.7))   # 머리 뒤 무늬(u, v, r)

    def behind(self, P):
        return []

    def back(self, P):
        return []

    def over(self, P):
        return []

    def tail_end(self, P):
        return []


class Pose:
    """한 장의 자세 — nod(머리 까딱, 라디안, + 가 숙임) 둘레 piv. hf 는 머리 조각 거리함수를, hp 는 머리 점을 까딱인다"""

    def __init__(self, nod=0.0, piv=(0.4, 4.6), sway=0.0, step=0.0, tail=None):
        self.nod, self.piv, self.sway, self.step, self.tail = nod, piv, sway, step, tail

    def hf(self, g):
        return turn(g, self.nod, *self.piv) if self.nod else g

    def hp(self, u, v):
        if not self.nod:
            return u, v
        c, s = cos(self.nod), sin(self.nod)
        du, dv = u - self.piv[0], v - self.piv[1]
        return self.piv[0] + du * c - dv * s, self.piv[1] + du * s + dv * c


TAIL = [(-5.0, 9.6), (-8.6, 10.2), (-11.6, 8.8), (-13.0, 6.2)]            # 기본 꼬리(뒤로 뻗어 끝이 살짝 들림)
TAIL_UP = [(-4.8, 9.4), (-7.8, 9.0), (-9.4, 6.4), (-9.0, 3.4)]            # 말아 올린 꼬리 — 판이 좁은 칸


def tail_of(pts, sway):
    """꼬리 끝 둘을 sway 만큼 위아래로 — 뿌리는 그대로"""
    n = len(pts)
    return [(u, v + sway * (i / (n - 1)) ** 2) for i, (u, v) in enumerate(pts)]


def dino(F, K, mood="open", nod=0.0, mouth=0.0, arm=0.0, arm_far=None, step=0.0, sway=0.0, tail_pts=None,
         look=0.0, bob=0.0, face_on=True):
    """선 치비 공룡 → 레이어 목록. 캐논: 머리 (0, 0) · 몸 (-1.2, 8.0) · 발바닥 v ≈ 13.6 · 주둥이 끝 u ≈ 8.0.
    mood: open · blink · happy · squeeze(><) · sad. mouth 0–1 은 벌린 입. arm 은 팔 끝을 든 정도(캐논 칸, + 가 위).
    bob 0–1 은 몸이 살짝 눌림. look 은 눈동자를 앞(+) · 뒤(-)로"""
    if K.body:
        return K.body(F, K, mood=mood, nod=nod, mouth=mouth, arm=arm, arm_far=arm_far, step=step, sway=sway,
                      tail_pts=tail_pts, look=look, bob=bob, face_on=face_on)
    s = F.s
    C = H()
    arm_far = arm if arm_far is None else arm_far
    P = Pose(nod, sway=sway, step=step)
    tp = tail_of(tail_pts or TAIL, sway)
    P.tail = tp
    rt = max(2.5, 2.0 / s)                                     # 꼬리 · 팔 · 발은 판에서 1.6칸 넘게 — 먹선 안에 몸빛이 남게(냥이 틀과 같은 셈)
    hd_c = K.head
    head = P.hf(smin(1.4, ell(*hd_c), ell(*K.snout)))
    by = 8.0 + bob * 0.4
    body = ell(-1.2, by, 5.0 + bob * 0.3, 4.6 - bob * 0.4)
    thigh = ell(-1.0, by + 2.0, 2.9, 2.7)
    ra = max(1.05, 1.7 / s)                                    # 팔 반지름
    fy = max(1.4, 1.6 / s)                                     # 발 세로 반지름 — 발바닥(v 14)은 그대로
    pieces_back = []                                           # (f, col) — 먼 쪽 · 몸 뒤
    tl = chain(tp, rt, max(0.9, 1.5 / s))
    pieces_back.append((tl, C.base))
    pieces_back += K.tail_end(P)
    if K.quad:
        pieces_back.append((ell(3.0 - step * 0.5, 13.8 - fy, 1.9, fy), C.far))
    pieces_back.append((ell(-3.4 - step, 13.8 - fy, 2.1, fy), C.far))
    if not K.quad and s >= 0.75:                               # 먼 팔 — 작으면 먹 덩어리라 뺀다
        pieces_back.append((taper(3.2, 5.8, ra * 0.95, 4.8, 6.8 - arm_far, ra * 0.85), C.far))
    pieces_back += K.back(P)
    near = [(body, C.base), (thigh, C.base), (ell(1.0 + step, 14.0 - fy, 2.3, fy), C.base)]
    if K.quad:
        near.append((ell(4.4 + step * 0.5, 14.0 - fy, 2.0, fy), C.base))
    beh = K.behind(P)
    ov = K.over(P)
    arm_near = [] if K.quad else [(taper(2.2, 6.6, ra, 4.2, 7.6 - arm, ra * 0.9), C.base)]
    allf = [p[0] for p in pieces_back + near + beh + ov + arm_near] + [head]
    out = [base(*[F.f(g) for g in allf])]
    for g, col in pieces_back:
        out.append(part(F.f(g), col))
    for g, col in near:
        out.append(part(F.f(g), col))
    out.append(flat(F.f(inter(body, ell(1.2, by + 0.8, 3.0, 3.4))), C.belly))   # 배
    for g, col in beh:
        out.append(part(F.f(g), col))
    out.append(part(F.f(head), C.base))
    chin = P.hf(inter(smin(1.4, ell(*hd_c), ell(*K.snout)), ell(4.6, 5.0, 5.6, 2.6)))
    out.append(flat(F.f(grow(chin, -LINE_IN)), C.belly))
    dark = C.dark
    for u, v, r in (K.spots if s >= 0.55 else ()):          # 머리 뒤 무늬 — 납작한 동그라미, 작으면 얼룩이라 뺀다
        out.append(flat(F.f(P.hf(inter(circle(u, v, r), grow(ell(*hd_c), -1.2)))), lerp(C.base, dark, 0.4)))
    for g, col in ov:
        out.append(part(F.f(g), col))
    if face_on:
        out += dface(F, K, P, mood, mouth, look)
    for g, col in arm_near:
        out.append(part(F.f(g), col))
    return out


LINE_IN = 1.0                      # 턱 · 배 색이 먹선을 안 덮게 안으로 들이는 만큼(캐논)


def dface(F, K, P, mood="open", mouth=0.0, look=0.0):
    """3/4 옆얼굴: 앞 눈(4.0, 0.2) · 먼 눈(0.2, -0.2), 눈마다 바로 밑 분홍 볼, 주둥이 끝 콧구멍 하나, 주둥이 밑 작은 웃음.
    눈은 까만 콩 + 왼쪽 위 흰 반짝 하나 — 32 에서도 2px 남게 판 단위로 바닥을 둔다"""
    s = F.s
    C = H()
    out = []
    er = max(1.15 * s, 0.95)                                   # 눈 반지름(art)
    sn = K.snout
    eyes = ((0.2, -0.3, 0.86), (4.0, 0.0, 1.0))               # (u, v, 크기) — 먼 눈은 조금 작게
    for u, v, k in eyes:                                       # 볼 먼저(눈 아래 깔림)
        bx, by = F.w(*P.hp(u + 0.5, v + 2.4))
        rx = max(1.25 * s, 0.85) * k
        out.append(soft(ell(bx, by, rx, rx * 0.6), BLUSH, 0.85))
    sign = F.fx
    for i, (u, v, k) in enumerate(eyes):
        ex, ey = F.w(*P.hp(u + 0.35 * look, v))
        r = er * k
        if mood == "squeeze":                                   # >< — 앞 눈이 <, 먼 눈이 > (화면 기준으로 뒤집힘)
            d = (1 if i == 0 else -1) * sign
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
    if s >= 0.42:                                              # 콧구멍
        nx, ny = F.w(*P.hp(sn[0] + sn[2] - 1.5, sn[1] - 1.2))
        out.append(flat(ell(nx, ny, max(0.3 * s, 0.26), max(0.22 * s, 0.2)), C.out, 0.85))
    mx, my = F.w(*P.hp(sn[0] + 1.2, sn[1] + 1.6))
    if mouth > 0:                                              # 벌린 입: 분홍 D(혀)
        rw, rh = max(1.8 * s, 1.0), max((0.6 + 1.5 * mouth) * s, 0.7)
        g = turn(ell(mx, my + rh * 0.4, rw, rh), P.nod * F.fx, mx, my)
        out.append(flat(g, lambda x, y: lerp(MOUTH, TONGUE, smooth(my + rh * 0.2, my + rh * 1.1, y)), line=0.32, ink=C.out))
        for i in range(K.teeth):                               # 이(작은 흰 세모) — 위턱에서
            tx, ty = F.w(*P.hp(sn[0] + 2.6 - 1.8 * i, sn[1] + 1.3))
            out.append(flat(poly([(tx - 0.45, ty - 0.1), (tx + 0.45, ty - 0.1), (tx, ty + 0.75)]), HI))
    elif s >= 0.4:                                             # 다문 입: 작은 웃음
        r = max(1.0 * s, 0.75)
        a0 = pi * 0.12 + (P.nod if F.fx > 0 else -P.nod)
        out.append(flat(arc(mx, my - r * 0.6, r, max(0.17 * s, 0.17), a0 + (0 if F.fx > 0 else pi * 0.1), pi * 0.66), C.out, 0.95))
        for i in range(K.teeth):                               # 송곳니 — 입꼬리 앞에 하나씩
            tx, ty = F.w(*P.hp(sn[0] + 2.4 - 1.8 * i, sn[1] + 2.3))
            out.append(flat(poly([(tx - 0.4, ty - 0.2), (tx + 0.4, ty - 0.2), (tx, ty + 0.55)]), HI, line=0.0))
    return out


def snout_tip(F, K, nod=0.0):
    """주둥이 끝(art) — 콕 칸이 핫스팟을 여기에 맞춘다"""
    sn = K.snout
    return F.w(*Pose(nod).hp(sn[0] + sn[2], sn[1]))


def head_top(F, K, nod=0.0):
    hd_c = K.head
    return F.w(*Pose(nod).hp(hd_c[0], hd_c[1] - hd_c[3]))


# ---- 소품 ----

def chevron(cx, cy, dx, dy, L=2.4, a=1.0):
    """(dx, dy) 쪽을 가리키는 주황 화살촉 — 꼭짓점이 (cx, cy). 냥이 것(분홍)과 같은 꼴"""
    n = hypot(dx, dy)
    dx, dy = dx / n, dy / n
    px, py = -dy, dx
    f = union(*[capsule(cx, cy, cx - dx * L + s * px * L, cy - dy * L + s * py * L, 0.72) for s in (-1, 1)])
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(CHEV, CHEV_D, smooth(0.36, 0.2, -e)), 1.0), alpha=a)]


def drop(x, y, r=1.0, h=1.4):
    """땀방울 — 꼭지가 위"""
    f = smin(0.3, circle(x, y + 0.5, r), poly([(x, y - h), (x - r * 0.8, y + 0.4), (x + r * 0.8, y + 0.4)]))
    return [base(f), part(f, lambda px, py: lerp(HI, SWEAT, smooth(y - 0.6, y + 0.8, py)), shade=SWEAT_D, ink=SWEAT_D, line=0.45)]


def star(cx, cy, L=2.0, w=0.65):
    return sparkle(cx, cy, L, w)


def puff(cx, cy, r=1.4, a=1.0):
    """먼지 퐁 — 동그라미 셋"""
    f = union(circle(cx - r * 0.7, cy + r * 0.2, r * 0.75), circle(cx + r * 0.6, cy + r * 0.25, r * 0.7), circle(cx, cy - r * 0.35, r * 0.85))
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(DUST, DUST_D, smooth(0.32, 0.15, -e)), 1.0), alpha=a)]


def zip_lines(cx, cy, n=3, L=1.6, r0=2.2, a0=-pi / 2, spread=0.7, a=0.9):
    """콕 · 쿵 할 때 튀는 짧은 줄 n 개 — (cx, cy) 둘레 a0 쪽으로 부채꼴"""
    out = []
    for i in range(n):
        t = a0 + spread * (i - (n - 1) / 2)
        x0, y0 = cx + cos(t) * r0, cy + sin(t) * r0
        out.append(flat(capsule(x0, y0, x0 + cos(t) * L, y0 + sin(t) * L, 0.26), OUT, a))
    return out


def no_sign(C_=14.5, R=12.5):
    """빨간 금지 표지(고리 + 빗금) — 공룡 위에 칠한다"""
    g = union(ring(C_, C_, R - 1.25, 1.25), capsule(C_ - 7.7, C_ - 7.7, C_ + 7.7, C_ + 7.7, 1.35))
    return [base(g), part(g, lambda x, y: lerp(SIGN_L, SIGN, smooth(C_ - 10, C_ - 4, y + 0.5 * x - 0.5 * C_)), shade=SIGN_D,
                          ink=SIGN_D, line=0.8)]


# ---- 화살표 (핫스팟 (1, 1)) ----
# 기본은 냥이 빼꼼과 같은 크림 화살표(1.24 배, 끝 TIP). 모양 탭이면 catkit.shaped 윤곽. 공룡은 화살표 밑에, 화살표가 맨 위

def arrow_geo(shape=None):
    """화살표 자리 — body(몸) · outer(바깥 테) · band(흰 띠) · P0(끝) · u(빗변 방향) · L(빗변 길이) · wing(날개 끝) · hot"""
    if shape:
        g = dict(shaped(shape))
    else:
        sc = 1.24
        P = [(TIP[0] + sc * x, TIP[1] + sc * y) for x, y in ARROW]
        arw = rpoly(P, 0.55)
        ex, ey = P[6][0] - P[0][0], P[6][1] - P[0][1]
        el = hypot(ex, ey)
        g = dict(body=arw, outer=arw, band=0.0, P0=P[0], u=(ex / el, ey / el), L=el, hot=(1.5, 1.5))
    x0, y0 = g["P0"]
    g["wing"] = (x0 + g["u"][0] * g["L"], y0 + g["u"][1] * g["L"])
    return g


def arrow_layers(g):
    if g["band"]:                                       # 스티커: 먹선 · 흰 띠 · 크림 몸
        return cur([base(g["outer"]), part(g["outer"], HI_WHITE, sh=0.0), part(g["body"], cream_of, line=0.0, sh=0.0)])   # 그늘은 털빛(초록)이라 끈다
    return cur([base(g["body"]), part(g["body"], cream_of, sh=0.0)])


def edge_pt(g, t, off):
    """빗변 t(0 끝 · 1 날개) 자리에서 바깥 테 밖으로 off 만큼"""
    return _edge(g, t, off)


# ---- 공용 14칸 ----

def ph_k(fr):
    return TAU * fr, round(fr * NF) % NF


def mini(K, fr, look=0.0, nod=0.0, mood=None):
    """작은 화살표 밑에 선 작은 공룡 — 오른쪽(소품)을 보고 꼬리 살랑, 한 번 끔뻑. 화살표는 맨 위"""
    ph, k = ph_k(fr)
    m = mood or ("blink" if k == 7 else "open")
    F = DF(7.4, 17.4, 0.5)
    return dino(F, K, m, nod=nod, look=look, sway=0.9 * sin(ph), tail_pts=TAIL_UP, bob=0.3 * (1 - cos(2 * ph)) / 2)


def companion(K, fr, props, **kw):
    return props + mini(K, fr, **kw) + small_arrow()


def sc_busy(K, fr):
    """오른쪽에 그 공룡 색 알갱이 여덟이 원을 그리고 한 알씩 차례로 진해지며 돈다 — 공룡은 고개로 따라 봄"""
    ph, k = ph_k(fr)
    C = H()
    cx, cy, R = 23.4, 21.6, 5.6
    head = k * 8 / NF
    out = []
    for i in range(8):
        a = TAU * i / 8 - pi / 2
        lag = (head - i) % 8
        col, al = (C.out, 1.0) if lag < 1 else (C.dark, 1.0) if lag < 2 else (C.base, 1.0) if lag < 3.5 else (C.base, 0.4)
        f = circle(cx + R * cos(a), cy + R * sin(a), 1.45)
        out.append(layer(f, lambda x, y, e, nx, ny, fr_, c=col: (lerp(c, OUT, smooth(0.42, 0.26, -e)), 1.0), alpha=al))
    return companion(K, fr, out, nod=0.12 * sin(ph))


def bone_f(pts, r=1.2, knob=1.35):
    """뼈 한 토막: 줄기 + 양끝 마디 둘씩(끝 방향에 직각으로)"""
    out = [chain(pts, r)]
    for (ax, ay), (bx, by) in ((pts[0], pts[1]), (pts[-1], pts[-2])):
        dx, dy = ax - bx, ay - by
        n = hypot(dx, dy) or 1.0
        dx, dy = dx / n, dy / n
        for sg in (-1, 1):
            out.append(circle(ax + dx * 0.4 - dy * sg * knob * 0.8, ay + dy * 0.4 + dx * sg * knob * 0.8, knob))
    return union(*out)


QPATH = [(20.4, 20.4), (20.4, 17.6), (22.4, 15.6), (25.0, 13.6), (25.4, 10.2), (22.8, 7.8), (19.6, 8.4)]


def sc_help(K, fr):
    """화석 뼈 한 토막이 물음표로 휘어 살랑 — 점 자리엔 알 하나가 톡톡. 공룡은 고개 갸웃"""
    ph, k = ph_k(fr)
    sw = 0.5 * sin(ph)
    pts = [(x + sw * (21.0 - y) / 12.0, y) for x, y in QPATH]
    q = bone_f(pts, 1.15, 1.2)
    out = [base(q), part(q, BONE, shade=BONE_D, ink=hx("8a6e4a"), line=0.85)]
    hop = 0.6 * abs(sin(2 * ph))
    eg = ell(20.6, 26.2 - hop, 2.0, 2.4)
    out += [base(eg), part(eg, EGG_SHELL, shade=hx("eadcc0"))]
    for u, v, r in ((-0.6, -0.8, 0.5), (0.7, 0.4, 0.42), (-0.3, 1.1, 0.35)):
        out.append(flat(circle(20.6 + u, 26.2 - hop + v, r), EGG_SPOT))
    return companion(K, fr, out, nod=0.18 * sin(ph))


def sc_person(K, fr):
    """그 공룡 후드(등에 표식 색 가시)를 쓴 사람이 손을 흔들고, 작은 공룡이 올려다보며 꼬리 살랑"""
    ph, k = ph_k(fr)
    C = H()
    cx, cy = 23.0, 19.4
    wave = abs(sin(ph))
    hand = (cx + 6.2, cy - 2.4 - 2.2 * wave)
    torso = clip_y(ell(cx, cy + 9.4, 6.6, 5.6), 30.4)
    sleeve = capsule(cx + 3.6, cy + 5.4, hand[0], hand[1] + 0.6, 1.5)
    hd_ = ell(cx, cy, 4.6, 4.4)
    spikes = union(*[rpoly([(cx + u - 1.4, cy - 3.6 + 0.08 * u * u), (cx + u, cy - 7.0 + 0.1 * u * u), (cx + u + 1.4, cy - 3.6 + 0.08 * u * u)], 0.4)
                     for u in (-2.8, 0.0, 2.8)])
    hood = smin(0.6, ell(cx, cy - 0.8, 5.6, 5.4), ell(cx, cy + 3.8, 5.0, 1.8))
    face_ = ell(cx, cy + 0.9, 3.5, 3.2)
    hnd = circle(*hand, 1.55)
    out = [base(torso, sleeve, hood, spikes, hnd)]
    out += [part(torso, SHIRT, shade=SHIRT_D), part(spikes, C.deco, shade=C.deco_d), part(hood, C.base),
            flat(grow(face_, 0.0), SKIN, line=0.5, ink=C.out), part(sleeve, SHIRT, shade=SHIRT_D), part(hnd, SKIN, shade=SKIN_D)]
    for sg in (-1, 1):
        out.append(flat(ell(cx + sg * 1.4, cy + 0.9, 0.5, 0.68), EYE))
        out.append(soft(ell(cx + sg * 2.3, cy + 2.4, 0.85, 0.5), BLUSH, 0.85))
    out.append(flat(arc(cx, cy + 1.9, 0.8, 0.2, pi * 0.15, pi * 0.7), C.out))
    return companion(K, fr, out, nod=-0.3 - 0.08 * wave, mood="happy" if k % 6 in (2, 3) else "blink" if k == 9 else "open")


FOOT = [(0.0, 1.6, 1.15, 1.0), (-1.4, -0.6, 0.5, 1.15), (0.0, -1.1, 0.5, 1.2), (1.4, -0.6, 0.5, 1.15)]


def sc_pin(K, fr):
    """빨간 지도 핀 속에 흰 세 발가락 공룡 발자국 — 핀이 통통, 땅에 닿을 때 작은 공룡이 눈웃음"""
    ph, k = ph_k(fr)
    hop = abs(sin(pi * fr))
    cx, cy = 22.8, 14.2 - 2.6 * hop
    out = [layer(ell(23.0, 29.2, 3.4 - 0.8 * hop, 0.75), lambda *a: (OUT, 0.22))]
    f = smin(1.0, circle(cx, cy, 5.8), poly([(cx - 4.7, cy + 2.7), (cx + 4.7, cy + 2.7), (cx, cy + 11.6)]))
    out += [base(f), part(f, lambda x, y: lerp(SIGN_L, SIGN, smooth(cy - 5, cy - 1.5, y + 0.6 * (x - cx))), shade=SIGN_D, ink=SIGN_D)]
    toes = union(*[oell(cx + u * 1.05, cy + v * 1.05 + 0.2, a, b, (-0.5 if u < 0 else 0.5 if u > 0 else 0.0)) for u, v, a, b in FOOT])
    out.append(flat(toes, HI_WHITE))
    return companion(K, fr, out, nod=-0.08, mood="happy" if hop < 0.3 else "open")


HAND_HOT = (16, 1)


def sc_hand(K, fr, hot=HAND_HOT, nod0=-1.0):
    """고개를 하늘로 젖혀 주둥이 끝으로 위를 콕콕 — 그 끝이 핫스팟이고 장마다 그대로. 콕 할 때 더 젖히고 줄이 튄다"""
    ph, k = ph_k(fr)
    p = (0, 0, 1, 2, 0, 0, 1, 2, 0, 0, 0, 0)[k]
    nod = nod0 - 0.1 * p
    mood = "squeeze" if p == 2 else "blink" if k == 10 else "happy" if p == 1 else "open"
    s = 0.86
    F0 = DF(0.0, 0.0, s, fx=-1)
    tx, ty = snout_tip(F0, K, nod)
    hx_, hy_ = hot[0] + 0.5, hot[1] + 0.5 + 0.55                # 주둥이 끝 먹선 안쪽이 핫스팟 칸에 들게
    F = DF(hx_ - tx, hy_ - ty, s, fx=-1)
    out = []
    if p == 2:
        out += zip_lines(hx_, hy_, 2, 1.4, 2.4, -pi / 2, 1.9)
    out += dino(F, K, mood, nod=nod, arm=1.8 if p else 0.8, sway=1.0 * sin(ph), tail_pts=TAIL_UP)
    return out


def sc_cross(K, fr, C_=14.5):
    """조준선 네 갈래 가운데에 빨간 열매 하나 — 오른쪽 아래 공룡이 고개를 내밀어 노려보고 침을 꼴깍. 열매 가운데가 핫스팟"""
    ph, k = ph_k(fr)
    lick = k % 6 in (3, 4)
    F = DF(25.0, 21.2, 0.52, fx=-1)
    out = dino(F, K, "happy" if lick else "blink" if k == 8 else "open", nod=-0.12 + 0.08 * sin(ph), mouth=0.5 if lick else 0.0,
               sway=0.8 * sin(ph), tail_pts=TAIL_UP, look=1.0)
    lines = union(capsule(2.6, C_, 9.6, C_, 0.5), capsule(19.4, C_, 26.4, C_, 0.5),
                  capsule(C_, 2.6, C_, 9.6, 0.5), capsule(C_, 19.4, C_, 26.4, 0.5))
    out += [base(lines), flat(lines, OUT)]
    b = circle(C_, C_ + 0.3, 2.7)
    out += [base(b), part(b, lambda x, y: lerp(BERRY_L, BERRY, smooth(C_ - 2.0, C_ + 0.5, y + 0.4 * (x - C_))), shade=BERRY_D, ink=BERRY_D)]
    out.append(flat(circle(C_ - 0.9, C_ - 0.6, 0.6), HI))
    leaf = oell(C_ + 1.5, C_ - 2.6, 1.4, 0.7, -0.5)
    out += [base(leaf), part(leaf, LEAF, shade=LEAF_D, ink=hx("3f7a32"), line=0.5)]
    return out


def sc_ibeam(K, fr, X=7.5):
    """세로로 선 I 꼴 화석 뼈 오른쪽에서 고개를 갸웃갸웃 킁킁. 핫스팟은 줄기 가운데"""
    ph, k = ph_k(fr)
    tilt = (0, 0, 7, 10, 10, 7, 0, 0, -7, -10, -10, -7)[k]
    stem = rbox(X, 15.0, 1.5, 11.0, 0.5)
    bars = union(rbox(X, 4.0, 4.4, 1.3, 0.6), rbox(X, 26.0, 4.4, 1.3, 0.6))
    knobs = union(*[circle(X + sx * 4.4, y + sy * 1.0, 1.35) for sx in (-1, 1) for sy in (-1, 1) for y in (4.0, 26.0)])
    I = union(stem, bars, knobs)
    F = DF(22.4, 15.4, 0.6, fx=-1)
    out = dino(F, K, "blink" if k == 6 else "happy" if abs(tilt) == 10 else "open", nod=-0.05 + tilt * 0.022, sway=0.9 * sin(ph),
               tail_pts=TAIL_UP, look=0.6)
    out += [base(I), part(I, BONE, shade=BONE_D, ink=hx("8a6e4a"), line=0.85)]
    for y in (10.0, 20.0):
        out.append(flat(capsule(X - 0.7, y - 0.3, X + 0.4, y + 0.4, 0.18), BONE_D))
    if abs(tilt) == 10:                                  # 킁킁 줄
        out += zip_lines(15.4, 12.4, 2, 1.0, 0.8, pi * 1.1, 0.7, 0.8)
    return out


def sc_move(K, fr):
    """제자리에서 쿵쿵 걸음 — 네 방향 주황 화살촉이 바깥으로 두근. 몸 가운데(15, 15)가 핫스팟"""
    ph, k = ph_k(fr)
    o = 0.6 if k % 6 < 3 else 0.0
    out = []
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        out += chevron(15.5 + dx * (13.6 + o), 15.5 + dy * (13.6 + o), dx, dy, 2.2, 1.0 if o else 0.75)
    st = 1.2 if k % 6 < 3 else -1.2
    F = DF(17.4, 9.2 - (0.4 if k % 3 == 1 else 0.0), 0.62)
    out += dino(F, K, "happy" if k % 6 in (1, 4) else "open", step=st, arm=0.8 if k % 6 < 3 else 0.0, sway=0.8 * sin(2 * ph),
                tail_pts=TAIL_UP)
    if k % 6 in (0, 3):
        out += puff(10.8 if st > 0 else 20.4, 26.4, 1.1, 0.85)
    return out


AXES = {"ns": ((0.0, 1.0), (8.5, 15.5), 1, 13.0), "we": ((1.0, 0.0), (15.5, 7.5), 1, 13.0),
        "nwse": ((0.5 ** 0.5, 0.5 ** 0.5), (13.5, 13.5), -1, 11.0), "nesw": ((0.5 ** 0.5, -(0.5 ** 0.5)), (13.5, 13.5), 1, 11.0)}


def sc_stretch(K, fr, axis):
    """기지개 — 선 몸 그대로 축 방향으로 쭉 늘였다 줄였다(직각으로는 살짝 홀쭉), 늘 때 눈을 질끈. 축 양끝 화살촉이 두근.
    축 가운데가 핫스팟. ns 는 왼쪽 세로줄(8, 15), we 는 위 가로줄(15, 7) — 픽셀 판 핫스팟 자리"""
    ph, k = ph_k(fr)
    e, c, fx, R = AXES[axis]
    t = 0.5 + 0.5 * sin(ph)
    s = 0.5 if axis == "ns" else 0.52
    # 몸 가운데(캐논 (-0.8, 5.0))가 축 가운데에 오게
    if axis == "we":
        c_body = (15.5, 14.8)
    elif axis == "ns":
        c_body = c
    else:
        c_body = c
    F0 = DF(0.0, 0.0, s, fx=fx)
    bx, by = F0.w(-0.8, 5.0)
    F = DF(c_body[0] - bx, c_body[1] - by, s, fx=fx, e=e, sa=1.0 + 0.38 * t, sb=1.0 - 0.1 * t)
    F.ox, F.oy = F.ox, F.oy
    F = _stretch_about(F, c_body)
    out = []
    o = 0.6 if t > 0.6 else 0.0
    for sg in (-1, 1):
        out += chevron(c[0] + sg * e[0] * (R + o), c[1] + sg * e[1] * (R + o), sg * e[0], sg * e[1], 2.2, 1.0 if o else 0.75)
    out += dino(F, K, "squeeze" if t > 0.6 else "open", nod=-0.25 * t, arm=1.4 * t, sway=-0.6 * t, tail_pts=TAIL_UP)
    return out


class _About(DF):
    """늘이기 가운데를 몸 가운데(cx, cy)로 옮긴 DF"""

    def __init__(self, F, cx, cy):
        DF.__init__(self, F.ox, F.oy, F.s, 0.0, F.fx, F.e, F.sa, F.sb)
        self.c, self.sn = F.c, F.sn
        self.cx, self.cy = cx, cy

    def loc(self, x, y):
        dx, dy = self._st(x - self.cx, y - self.cy, -1)
        dx, dy = dx + self.cx - self.ox, dy + self.cy - self.oy
        dx, dy = dx / self.s, dy / self.s
        return (dx * self.c + dy * self.sn) * self.fx, -dx * self.sn + dy * self.c

    def w(self, u, v):
        u *= self.fx
        x = self.ox + (u * self.c - v * self.sn) * self.s - self.cx
        y = self.oy + (u * self.sn + v * self.c) * self.s - self.cy
        dx, dy = self._st(x, y, 1)
        return self.cx + dx, self.cy + dy


def _stretch_about(F, c):
    return _About(F, *c)


PEN_HOT = (1, 24)


def sc_pen(K, fr, hot=PEN_HOT):
    """연필 끝(지우개 쪽)을 입에 물고 쓰는 공룡 — 심이 왼쪽 아래 끝이자 핫스팟. 끄덕일 때 연필이 따라 까딱, 쓴 줄이 자란다"""
    ph, k = ph_k(fr)
    bob = ((0, 0), (0, 0), (0.5, 0), (0.5, 0.5), (0, 0.5), (0, 0), (0, 0), (0.5, 0), (0.5, 0.5), (0, 0.5), (0, 0), (0, 0))[k]
    s = 0.6
    nod = 0.22
    F = DF(22.2 + bob[0], 10.6 + bob[1], s, fx=-1)
    mx, my = F.w(*Pose(nod).hp(K.snout[0] + K.snout[2] - 0.8, K.snout[1] + 1.4))
    tip = (hot[0] + 0.55, hot[1] + 0.5)
    out = []
    n = min(k + 2, 12)
    for i in range(n):                                   # 쓴 줄 — 물결
        x0 = 3.6 + 1.7 * i
        out.append(flat(capsule(x0, 27.6 + 0.5 * sin(x0 * 0.9), x0 + 1.4, 27.6 + 0.5 * sin((x0 + 1.4) * 0.9), 0.32), OUT, 0.9))
    out += dino(F, K, "blink" if k == 4 else "happy" if k in (8, 9) else "open", nod=nod, arm=0.6, sway=0.8 * sin(ph),
                tail_pts=TAIL_UP, look=-0.4)
    L = hypot(mx - tip[0], my - tip[1])
    ux, uy = (mx - tip[0]) / L, (my - tip[1]) / L
    cone = taper(tip[0], tip[1], 0.3, tip[0] + ux * 3.6, tip[1] + uy * 3.6, 1.4)
    shaft = capsule(tip[0] + ux * 3.4, tip[1] + uy * 3.4, mx, my, 1.4)

    def pcol(x, y):
        t = (x - tip[0]) * ux + (y - tip[1]) * uy
        sd = -(x - tip[0]) * uy + (y - tip[1]) * ux
        if t < 1.6:
            return PEN_G
        if t < 3.7:
            return PEN_W
        if t > L - 2.0:
            return PEN_E
        return PEN_YD if sd > 0.45 else PEN_Y
    out += [base(cone, shaft), part(union(cone, shaft), pcol, shade=PEN_YD, ink=hx("6a4a2a"), line=0.6, sh=0.0)]
    return out


UP_HOT = (8, 1)


def sc_up(K, fr, hot=UP_HOT):
    """머리 위 굵은 주황 위쪽 화살표를 올려다보며 깡충 — 뜰 때 눈웃음. 화살표 끝(맨 위)이 핫스팟"""
    ph, k = ph_k(fr)
    hop = (0, 0, 1, 2, 3, 2, 1, 0, 0, 0, 0, 0)[k] * 0.55
    X = hot[0] + 0.5
    ty = hot[1] + 0.5 - 0.1
    up = rpoly([(X, ty), (X + 5.6, ty + 6.0), (X + 2.3, ty + 6.0), (X + 2.3, ty + 9.6), (X - 2.3, ty + 9.6), (X - 2.3, ty + 6.0),
                (X - 5.6, ty + 6.0)], 0.4)
    out = [layer(ell(X + 6.0, 29.4, 6.0 - hop, 0.8), lambda *a: (OUT, 0.18 if hop else 0.26))]
    F = DF(X + 4.4, 15.8 - hop, 0.64)
    out += dino(F, K, "happy" if hop >= 1.0 else "blink" if k == 9 else "open", nod=-0.5, arm=1.6 if hop else 0.4,
                step=0.6 if hop else 0.0, sway=0.8 * sin(ph), tail_pts=TAIL_UP, look=0.5)
    out += [base(up), part(up, lambda x, y: lerp(hx("ffc08a"), CHEV, smooth(ty, ty + 4, y)), shade=CHEV_D, ink=CHEV_D, line=0.8)]
    return out


SHARED = {"busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "hand": sc_hand, "cross": sc_cross,
          "ibeam": sc_ibeam, "move": sc_move, "pen": sc_pen, "up": sc_up,
          "ns": lambda K, fr: sc_stretch(K, fr, "ns"), "we": lambda K, fr: sc_stretch(K, fr, "we"),
          "nwse": lambda K, fr: sc_stretch(K, fr, "nwse"), "nesw": lambda K, fr: sc_stretch(K, fr, "nesw")}

HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1), "cross": (14, 14),
       "hand": HAND_HOT, "ibeam": (7, 14), "move": (15, 15), "nesw": (13, 13), "nwse": (13, 13), "no": (14, 14),
       "ns": (8, 15), "pen": PEN_HOT, "up": UP_HOT, "we": (15, 7), "wait": (15, 15)}


class DinoPet(Pet):
    """공룡 결 하나 — hide(몸빛) · kind(생김새) · own(arrow · wait · no 장면, fr[, g] → 레이어) · hot(칸 → art 칸).
    own 의 arrow 는 (fr, g) 를 받는다 — g 는 arrow_geo(모양) 라 모양 탭도 같은 함수가 그린다.
    shared 를 주면 공용 칸을 마리 것으로 바꿔 끼운다(이름 → (K, fr) → 레이어)"""
    M = 1.8

    def __init__(self, hide, kind, own, hot=None, shared=None):
        super().__init__(hide, {}, dict(HOT, **(hot or {})))
        self.kind, self.own = kind, own
        self.shared = dict(SHARED, **(shared or {}))

    def cell(self, name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
        use(self.coat)
        if name == "arrow":
            g = arrow_geo(shape)
            hot = g["hot"] if shape else (self.hot["arrow"][0] + 0.5, self.hot["arrow"][1] + 0.5)
            return self.own["arrow"](frame, g), hot
        ax, ay = self.hot[name]
        if name in self.own:
            return self.own[name](frame), (ax + 0.5, ay + 0.5)
        return self.shared[name](self.kind, frame), (ax + 0.5, ay + 0.5)

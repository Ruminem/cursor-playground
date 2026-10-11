# SPDX-License-Identifier: Apache-2.0
"""치즈냥(cheesecatanim) 고화질 — 치비(머리가 몸만 한 통통 냥) · 스티커 채색(고른 먹선 1칸 + 셀 그늘 한 단).

픽셀 치즈냥(gen/cheesecat.py)의 털빛(주황 바탕 · 이마 짙은 줄 셋 · 볼 옆 줄 · 크림 주둥이와 배 · 줄무늬 꼬리 · 흰 양말 발)과
칸마다 하는 짓을 HD 로 옮겼다. 핫스팟은 art 칸(art/cheesecatanim/*.txt 머리) 그대로다.

  arrow   크림 화살표 빗변 뒤에서 빼꼼(catkit.peek)
  busy    작은 화살표 치즈냥 + 생선 둘레를 도는 분홍 젤리 발자국 여덟, 생선이 파닥
  help    작은 화살표 치즈냥 + 줄무늬 꼬리를 말아 만든 물음표(점은 털실 공), 꼬리 끝이 살랑
  person  작은 화살표 치즈냥 + 고양이 귀 후드를 쓴 사람이 손을 흔든다
  pin     작은 화살표 치즈냥 + 동그라미 속 치즈냥 얼굴(귀가 핀 위로 솟음)이 든 빨간 핀이 통통, 땅에 닿으면 눈을 감는다
  wait    방석 위 식빵 자세로 꾸벅꾸벅 — 고개가 떨어지며 눈이 감기고 z 가 피어오르다 화들짝 깬다
  cross   앞모습 얼굴 — 긴 수염이 가로 조준선, 머리 위 장난감 줄 · 턱 밑 줄이 세로선. 코가 핫스팟, 짧은 수염 까딱
  ibeam   앉은 작은 치즈냥 뒤로 곧게 세운 줄무늬 꼬리가 I — 꼬리 끝이 갈고리로 까딱, 꼬리 가운데가 핫스팟
  pen     두 앞발로 연필을 쥐고 쓴다(혀 빼꼼) — 연필심(왼쪽 아래)이 핫스팟
  no      빨간 금지 표지 안에서 팔짱 끼고 고개를 홱 돌린 삐짐 — 반 바퀴마다 반대로 홱, 그때 꼬리를 탁
  ns      앞발을 위로 쭉 뻗고 몸을 세로로 늘인 기지개
  we · nwse · nesw   엎드려 앞발 · 뒷발을 축으로 쭉 늘인 기지개(catkit.stretch) — 늘 때 눈을 질끈(><)
  move    동그랗게 만 치즈냥이 데굴데굴 한 바퀴(눈은 ^^) — 네 방향 분홍 화살촉
  up      두 앞발을 활짝 든 만세 — 냥냥 입을 벌린다. 두 귀 사이 머리 꼭대기가 핫스팟이라 머리는 그대로
  hand    분홍 젤리 발바닥으로 꾹 — 누를 때 발바닥이 납작하게 퍼지고 눈을 질끈. 발바닥 꼭대기가 핫스팟

좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 장면은 NF 장으로 나뉘어 있다(k = round(fr × NF) % NF).
틀(먹선 · 치비 몸 · 빼꼼 · 기지개 · 모양 화살표)은 catkit 에 있고 여기는 털빛 · 소품 · 장면만 둔다.
catkit 에 없는 눈(><, 삐짐, 반쯤 감김)과 냥 입은 여기 face 가 catkit.face 의 눈 층만 갈아 끼워 그린다.
"""
import math

from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, cut, TAU  # noqa: F401

from . import catkit, register
from .catkit import *  # noqa: F401,F403

# 픽셀 판 팔레트(gen/cheesecat.py) 그대로 — 셀 그늘 FUR_SH 만 더함
OUT, EYE = hx("3a2a30"), hx("2a1c22")
FUR, FUR_SH, STRIPE, CREAMF = hx("e89a4a"), hx("d07f3a"), hx("c26f34"), hx("fff6e8")
NOSE, CHEEK, RIM = hx("e27d90"), hx("f7a3b5"), hx("fbecdc")
IRIS = (hx("8cc63f"), hx("4b8a2a"), hx("d2f08e"))          # 연두 눈 — 주황 털과 갈리게(원본은 눈이 2×2 먹색이라 색이 없음)
CUSH, CUSH_D, CUSH_L = hx("7fa3d4"), hx("587ab0"), hx("a9c4e8")   # 방석 (주황 몸과 갈리게 파랑)
YARN, YARN_D = hx("f07c9c"), hx("c4567a")                        # 털실 공
FISH, FISH_D, FISH_L = hx("9cb6cc"), hx("6a879f"), hx("d4e2ee")   # 생선
PENCIL, PENCIL_D, WOOD, LEAD = hx("f5c842"), hx("c8961c"), hx("efd2a8"), hx("3a3a3a")
ERASER, FERRULE = hx("f2a0a8"), hx("b8b8c0")
SHIRT, SHIRT_D, SKIN = hx("4a7fb5"), hx("2e5a88"), hx("f7d7bc")
SIGN, SIGN_D, SIGN_L = hx("d64541"), hx("9e2b28"), hx("ef7a72")
MOUTH = hx("8a2e3a")


class Tabby(Coat):
    """치즈 무늬 털빛 — 부위마다 (x, y) → 색. F(캐논 틀)가 없으면(기지개 몸 · 빼꼼 앞발) axis 로 줄무늬를 긋는다"""
    axis = None            # 기지개: (가운데 x, y, 축 ux, uy, 배 쪽 px, py, 몸 반지름) — sc 가 그리기 전에 꽂는다

    def fur(self, part, F=None, turn_=0.0):
        if part in ("paw", "hand", "front", "back"):
            return CREAMF                                   # 흰 양말
        if F is None:
            return self._axis_col(part) if self.axis and part in ("body", "tail") else FUR
        if part == "head":
            return _head_col(F, turn_)
        if part == "body":
            return _body_col(F)
        if part == "tail":
            return _tail_col(F)
        if part == "arm":
            return _arm_col(F)
        return FUR

    def _axis_col(self, part):
        cx, cy, ux, uy, px, py, r = self.axis

        def col(x, y):
            t = (x - cx) * ux + (y - cy) * uy
            q = (x - cx) * px + (y - cy) * py
            if part == "body" and q > r * 0.25:
                return CREAMF                               # 배
            return STRIPE if t % 2.8 < 1.0 else FUR
        return col


def _head_col(F, turn_):
    """이마 줄 셋 · 볼 옆 줄 둘 · 크림 주둥이(캐논 좌표로 재서 머리를 따라 돈다)"""
    def col(x, y):
        u, v = F.loc(x, y)
        mu = u - turn_
        if (mu / 3.6) ** 2 + ((v - 2.6) / 2.0) ** 2 <= 1:
            return CREAMF
        if v < -2.4 and any(abs(u - (turn_ * 0.6 + d * 1.7)) < 0.55 + 0.12 * (v + 2.4) for d in (-1, 0, 1)):
            return STRIPE
        if abs(mu) > 5.6 and any(abs(v - dd) < 0.5 for dd in (-0.2, 1.5)):
            return STRIPE
        return FUR
    return col


def _body_col(F):
    """크림 배 · 옆구리 굵은 줄"""
    def col(x, y):
        u, v = F.loc(x, y)
        if (u / 2.9) ** 2 + ((v - 8.2) / 3.4) ** 2 <= 1:
            return CREAMF
        if (v + 0.5 * u) % 2.8 < 1.0 and abs(u) > 3.4:
            return STRIPE
        return FUR
    return col


def _tail_col(F):
    """꼬리 고리 — 밑동(캐논 3.6, 10.4)에서 잰 거리로 띠를 둘러 꼬리를 가로지른다"""
    def col(x, y):
        u, v = F.loc(x, y)
        d = hypot(u - 3.6, v - 10.4)
        return STRIPE if d > 1.5 and d % 2.9 < 1.05 else FUR
    return col


def _arm_col(F):
    def col(x, y):
        u, v = F.loc(x, y)
        return STRIPE if (u + v) % 3.2 < 1.0 else FUR
    return col


COAT = Tabby(FUR, FUR_SH, OUT, EYE, RIM, (IRIS, IRIS), cheek=CHEEK, nose=NOSE)

# 픽셀 판 핫스팟(art/cheesecatanim/*.txt 머리) 그대로 — 적용한 사람의 손에 익은 자리
HOT = {"arrow": (1, 1), "busy": (1, 1), "cross": (15, 15), "hand": (8, 1), "help": (1, 1), "ibeam": (5, 8),
       "move": (15, 15), "nesw": (12, 12), "no": (14, 14), "ns": (6, 15), "nwse": (14, 12), "pen": (1, 25),
       "person": (1, 1), "pin": (1, 1), "up": (10, 2), "wait": (15, 14), "we": (15, 7)}


# ---- 얼굴: catkit.face 에 없는 눈(><, 삐짐, 반쯤 감김)과 냥 입 ----

_cat = catkit.cat                  # 기지개가 catkit.cat 을 잠깐 바꿔 끼우므로 원래 것을 붙잡아 둔다


def _eye_at(F, turn_, sg):
    ex, ey = F.w(turn_ + sg * 3.15, 0.25)
    return ex, ey, max(1.66 * F.s, 1.32)


def face(F, mood="open", look=(0.0, 0.0), turn_=0.0, mouth="w", tongue=0.0):
    """mood: open · blink · happy · wink(catkit 그대로) · sleep(= blink) · squeeze(><) · sulk(감은 눈 바깥을 치켜올림) ·
    half(윗눈꺼풀이 반쯤 덮은 졸린 눈) · wide(화들짝 — 동공이 작아짐 없이 그대로 연 눈). mouth="nyang" 은 벌린 입"""
    km = {"sleep": "blink", "squeeze": "open", "sulk": "open", "half": "open", "wide": "open"}.get(mood, mood)
    out = catkit.face(F, km, look, turn_, "" if mouth == "nyang" else mouth, tongue)
    ink = catkit.C.out
    if mood in ("squeeze", "sulk"):                 # 눈 층(볼 둘 다음 둘)을 갈아 끼움
        eyes = []
        for sg in (-1, 1):
            ex, ey, er = _eye_at(F, turn_, sg)
            w = max(0.3, 0.2 * er)
            if mood == "squeeze":                   # 왼눈 >, 오른눈 < — 꼭짓점이 코 쪽
                tx = ex - sg * er * 0.55
                bx = ex + sg * er * 0.75
                f = union(capsule(bx, ey - er * 0.7, tx, ey, w), capsule(tx, ey, bx, ey + er * 0.7, w))
            else:                                   # 흥 — 바깥 끝이 높은 감은 눈
                f = capsule(ex - sg * er * 0.8, ey + er * 0.35, ex + sg * er * 0.85, ey - er * 0.35, w)
            eyes.append(flat(f, catkit.C.eye))
        out[2:4] = eyes
    elif mood == "half":                            # 윗눈꺼풀: 눈 위쪽 반을 털색으로 덮고 아래 끝에 먹선
        for sg in (-1, 1):
            ex, ey, er = _eye_at(F, turn_, sg)
            lid = inter(ell(ex, ey, er * 1.12, er * 1.3), lambda x, y, ey=ey: y - (ey + er * 0.05))
            out.append(flat(lid, _head_col(F, turn_)))
            out.append(flat(inter(grow(ell(ex, ey, er * 1.02, er * 1.18), 0.0),
                                  lambda x, y, ey=ey: abs(y - (ey + er * 0.05)) - max(0.22, 0.17 * er)), catkit.C.eye))
    if mouth == "nyang":                            # 냥 — 코 아래 벌린 입 + 분홍 혀
        nx, ny = F.w(turn_, 2.05)
        s = F.s
        my = ny + max(1.55 * s, 1.15)
        rx, ry = max(1.15 * s, 0.85), max(1.0 * s, 0.75)
        m = ell(nx, my, rx, ry)
        tg = catkit.C.tongue
        out.append(flat(m, lambda x, y: lerp(MOUTH, tg, smooth(my + ry * 0.05, my + ry * 0.45, y)), line=max(0.3, 0.22 * s), ink=ink))
    return out


def cat(F, mood="open", look=(0.0, 0.0), turn_=0.0, mouth="w", tongue=0.0, face_on=True, arms=(), **kw):
    """catkit.cat 그대로 그리되 얼굴만 이 모듈 face 로(팔 층 아래에 끼움)"""
    out = _cat(F, mood, look, turn_, arms=arms, face_on=False, **kw)
    if face_on:
        n = sum(2 + (4 if j else 0) for _, _, j in arms)
        i = len(out) - n
        out[i:i] = face(F, mood, look, turn_, mouth, tongue)
    return out


def sticker_of(f, col, **kw):
    return [base(f), part(f, col, **kw)]


def stripe_along(pts, period=2.8, on=0.95, tip=0.5):
    """꺾은선 꼬리의 길이 방향 고리 무늬 — 처음부터 잰 길이로 띠를 두르고 끝은 짙게"""
    segs, acc = [], 0.0
    for p, q in zip(pts, pts[1:]):
        L = hypot(q[0] - p[0], q[1] - p[1]) or 1e-9
        segs.append((p, q, L, acc))
        acc += L
    total = acc

    def col(x, y):
        best = None
        for p, q, L, s0 in segs:
            t = clamp(((x - p[0]) * (q[0] - p[0]) + (y - p[1]) * (q[1] - p[1])) / (L * L))
            d = hypot(x - p[0] - (q[0] - p[0]) * t, y - p[1] - (q[1] - p[1]) * t)
            if best is None or d < best[0]:
                best = (d, s0 + L * t)
        s = best[1]
        if s > total - tip:
            return STRIPE
        return STRIPE if s > 1.0 and s % period > period - on else FUR
    return col


# ---- 소품 ----

def fish(cx, cy, L, h, ang):
    """옆모습 생선(머리가 오른쪽) — 등은 짙게 배는 옅게, 꼬리 세모 · 아가미 · 눈"""
    c, s = cos(ang), sin(ang)
    W = lambda u, v: (cx + u * c - v * s, cy + u * s + v * c)
    body = oell(cx, cy, L * 0.5, h * 0.5, ang)
    tl = rpoly([W(-L * 0.36, 0), W(-L * 0.8, -h * 0.62), W(-L * 0.8, h * 0.62)], 0.35)

    def bcol(x, y):
        v = -(x - cx) * s + (y - cy) * c
        return lerp(lerp(FISH_D, FISH, smooth(-h * 0.45, -h * 0.1, v)), FISH_L, smooth(0.0, h * 0.35, v))
    out = [base(body, tl), part(tl, FISH_D, shade=FISH_D), part(body, bcol, shade=FISH_D)]
    gx, gy = W(L * 0.14, 0)
    out.append(flat(turn(arc(gx, gy, h * 0.32, 0.18, -pi * 0.35, pi * 0.7), ang, gx, gy), FISH_D))
    ex, ey = W(L * 0.3, -h * 0.08)
    out.append(flat(circle(ex, ey, 0.62), EYE))
    out.append(flat(circle(ex - 0.2, ey - 0.2, 0.22), HI))
    return out


def yarn(cx, cy, r, k=0):
    """털실 공 — 분홍 동그라미에 비스듬한 실 줄 셋, 한 가닥이 삐져나온다"""
    ball = circle(cx, cy, r)
    loose = capsule(cx + r * 0.7, cy + r * 0.6, cx + r * 1.5, cy + r * 1.0, 0.28)
    sh = 0.25 * (k % 3)

    def col(x, y):
        t = ((x - cx) - (y - cy) + sh) % (r * 0.85)
        return YARN_D if t < 0.32 else YARN
    return [base(ball, loose), part(loose, YARN, shade=YARN_D, line=0.5, ink=YARN_D),
            part(ball, col, shade=YARN_D)]


def zz(x, y, L, a=1.0):
    """졸음 z 하나(방석 짙은 파랑)"""
    w = 0.32 + 0.06 * L
    f = union(capsule(x, y, x + L, y, w), capsule(x + L, y, x, y + L, w), capsule(x, y + L, x + L, y + L, w))
    return [layer(grow(f, 0.45), lambda *_: (RIM, 1.0), alpha=a), layer(f, lambda *_: (CUSH_D, 1.0), alpha=a)]


def sign_ring(C_, R, slash=True):
    """빨간 금지 표지(고리 + 왼쪽 위 → 오른쪽 아래 빗금). slash=False 는 고리만(냥 위에 다시 덮는 몫)"""
    sg = ring(C_, C_, R - 1.25, 1.25)
    if slash:
        sg = union(sg, capsule(C_ - R * 0.62, C_ - R * 0.62, C_ + R * 0.62, C_ + R * 0.62, 1.35))
    return [base(sg), part(sg, lambda x, y: lerp(SIGN_L, SIGN, smooth(C_ - 10, C_ - 4, y + 0.5 * x - 0.5 * C_)),
                          shade=SIGN_D, ink=SIGN_D, line=0.8)]


# ---- 칸마다 장면 (art 좌표, 화살표 칸은 catkit 빼꼼) ----

def sc_busy(fr):
    """작은 화살표 치즈냥 + 생선 둘레를 도는 분홍 젤리 발자국 여덟 — 생선은 파닥"""
    ph = TAU * fr
    out = buddy(fr)
    cx, cy = 22.4, 22.4
    k = round(fr * NF) % NF
    head = k * 8 / NF
    for i in range(8):
        a = TAU * i / 8 - pi / 2
        lag = (head - i) % 8
        out.append(paw_print(cx + 6.9 * cos(a), cy + 6.7 * sin(a), 1.0 if lag < 1.5 else 0.6 if lag < 3 else 0.28))
    out += fish(cx + 0.3, cy + 0.2, 8.6, 4.0, math.radians(-20 + 9 * sin(2 * ph)))
    return out


def sc_help(fr):
    """작은 화살표 치즈냥 + 줄무늬 꼬리를 말아 만든 물음표(밑동이 아래, 끝이 갈고리) · 점은 털실 공"""
    ph = TAU * fr
    out = buddy(fr)
    sw = 0.7 * sin(ph)
    pts = [(22.6, 23.4), (22.6, 20.8), (24.6, 18.8), (27.0, 16.9), (27.2, 13.7), (24.7, 12.0), (22.0, 12.8 + sw)]
    tl = chain(pts, 1.55, 1.3)
    out += [base(tl), part(tl, stripe_along(pts, 2.6, 0.9, 0.6))]
    out += yarn(22.6, 27.9, 2.1, round(fr * NF) % NF)
    return out


def sc_person(fr):
    """작은 화살표 치즈냥 + 고양이 귀 후드(주황 · 이마 줄)를 쓴 사람이 왼손을 흔든다"""
    ph = TAU * fr
    out = buddy(fr)
    cx, cy = 23.0, 23.0
    wave = 1.6 * sin(2 * ph)
    hand = (cx - 7.6 + 0.6 * wave, cy - 1.6 - abs(wave) * 0.5)
    body = clip_y(ell(cx, cy + 8.2, 6.8, 5.2), 30.4)
    arm = capsule(cx - 4.4, cy + 4.8, hand[0], hand[1] + 0.6, 1.25)
    hnd = circle(*hand, 1.35)
    hood = smin(0.6, ell(cx, cy - 0.6, 5.0, 4.6), ell(cx, cy + 1.4, 5.4, 3.4))
    ears = [rpoly([(cx + sg * 4.6, cy - 2.2), (cx + sg * 4.3, cy - 7.4), (cx + sg * 1.2, cy - 4.4)], 0.6) for sg in (-1, 1)]
    skin = ell(cx, cy + 0.4, 3.5, 3.2)
    out += [base(body, arm, hnd, hood, *ears), part(body, lambda x, y: SHIRT_D if abs(x - cx) < 0.45 else SHIRT, shade=SHIRT_D),
            part(arm, SHIRT, shade=SHIRT_D), part(hnd, SKIN, shade=hx("e8bfa0"))]
    for sg, E in zip((-1, 1), ears):
        out.append(part(E, FUR))
        out.append(flat(rpoly([(cx + sg * 3.9, cy - 3.0), (cx + sg * 3.85, cy - 6.0), (cx + sg * 2.1, cy - 4.4)], 0.3), PINK))

    def hcol(x, y):
        if y < cy - 3.2 and any(abs(x - (cx + d * 1.3)) < 0.42 for d in (-1, 0, 1)):
            return STRIPE
        return FUR
    out.append(part(hood, hcol))
    out.append(part(skin, SKIN, shade=hx("e8bfa0"), line=0.7))
    happy = round(fr * NF) % 6 < 2
    for sg in (-1, 1):
        if happy:
            out.append(flat(arc(cx + sg * 1.4, cy + 0.9, 0.75, 0.22, pi * 1.15, pi * 0.7), EYE))
        else:
            out.append(flat(ell(cx + sg * 1.4, cy + 0.2, 0.5, 0.7), EYE))
        out.append(soft(ell(cx + sg * 2.3, cy + 1.7, 0.8, 0.5), CHEEK, 0.85))
    out.append(flat(arc(cx, cy + 1.5, 0.8, 0.2, pi * 0.15, pi * 0.7), SHIRT_D))
    return out


def sc_pin(fr):
    """작은 화살표 치즈냥 + 빨간 지도 핀 — 동그라미 속에 치즈냥 얼굴, 귀는 핀 위로 솟는다. 땅에 닿을 때 눈을 감는다"""
    out = buddy(fr)
    hop = abs(sin(pi * fr))
    cx, cy = 22.6, 15.6 - 2.6 * hop
    out.insert(0, layer(ell(22.8, 29.2, 3.4 - 0.8 * hop, 0.75), lambda *a: (OUT, 0.2)))
    for sg in (-1, 1):                                    # 귀(핀 뒤)
        E = rpoly([(cx + sg * 4.4, cy - 2.6), (cx + sg * 4.2, cy - 8.6), (cx + sg * 0.9, cy - 5.0)], 0.6)
        out += [base(E), part(E, FUR)]
        out.append(flat(rpoly([(cx + sg * 3.8, cy - 4.0), (cx + sg * 3.75, cy - 7.0), (cx + sg * 2.0, cy - 5.1)], 0.3), PINK))
    f = smin(1.0, circle(cx, cy, 5.6), poly([(cx - 4.6, cy + 2.6), (cx + 4.6, cy + 2.6), (cx, cy + 11.4)]))
    out += [base(f), part(f, lambda x, y: lerp(SIGN_L, SIGN, smooth(cy - 5, cy - 1.5, y + 0.6 * (x - cx))), shade=SIGN_D, ink=SIGN_D)]
    out.append(flat(circle(cx, cy, 4.1), CREAMF, line=0.5, ink=SIGN_D))
    F = Frame(cx, cy - 0.35, 0.47)
    H = head_f(F)
    out += [part(H, _head_col(F, 0.0), line=0.6)]
    out += face(F, "blink" if hop < 0.2 else "open")
    return out


def sc_wait(fr):
    """방석 위 식빵 자세 — 고개가 스르르 떨어지며 눈이 반쯤 → 다 감기고 z 가 피어오르다(장 5–8) 화들짝(장 9) 깬다.
    꼬리 끝만 까딱. 머리는 식빵 몸 앞에 반쯤 묻는다 — 몸 위에 얹으면 눈사람으로 읽힌다(원본 주석)"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    drop = (0, 0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.0, 2.0, -0.4, 0, 0)[k]
    mood = ("open", "open", "half", "half", "sleep", "sleep", "sleep", "sleep", "sleep", "wide", "open", "blink")[k]
    cush = smin(0.8, ell(15.5, 25.2, 13.9, 3.4), ell(15.5, 26.4, 12.6, 2.8))
    tufts = union(ell(2.2, 26.4, 1.5, 0.95), ell(28.8, 26.4, 1.5, 0.95))
    out = [base(cush, tufts), part(tufts, CUSH_D, shade=CUSH_D),
           part(cush, lambda x, y: lerp(CUSH_L, CUSH, smooth(23.6, 25.6, y)), shade=CUSH_D)]
    loaf = smin(1.2, ell(15.5, 19.6, 10.8, 5.2), ell(15.5, 22.2, 11.6, 2.8))

    def lcol(x, y):
        return STRIPE if abs(x - 15.5) > 6.2 and (y + 0.2) % 2.6 < 0.95 else FUR
    tw = 0.7 * sin(2 * ph)
    tp = [(25.0, 22.6), (21.2, 24.0), (17.4, 24.2), (15.6 + 0.3 * tw, 23.4 + tw * 0.5)]
    tl = chain(tp, 1.55, 1.3)
    out += [base(loaf), part(loaf, lcol), base(tl), part(tl, stripe_along(tp, 2.6, 0.9, 0.5))]
    F = Frame(15.5, 13.4 + drop * 0.9, 0.86)
    out += cat(F, mood, body=False, paws=False, tail=False, mouth="w" if mood != "wide" else "")
    if 5 <= k <= 8:                                       # z 가 피어오른다
        j = k - 5
        out += zz(24.6 + 0.5 * j, 6.2 - 1.0 * j, 2.2 + 0.25 * j)
        if j >= 2:
            out += zz(27.6, 2.4 - 0.6 * (j - 2), 1.5, 0.8)
    if k == 9:                                            # 화들짝 — 머리 위 놀란 줄
        for a in (-0.55, 0.0, 0.55):
            bx, by = 15.5 + 8.6 * sin(a), 13.4 - 8.6 * cos(a) - 0.4
            dx, dy = sin(a), -cos(a)
            out += sticker_of(capsule(bx, by, bx + dx * 1.6, by + dy * 1.6, 0.42), OUT, sh=0.0, line=0.0)
    return out


def sc_cross(fr):
    """앞모습 얼굴 — 긴 수염 한 가닥씩이 가로 조준선, 머리 위로 늘어진 장난감 줄(끝에 털실 방울)과 턱 밑 줄이 세로선.
    코가 핫스팟. 짧은 수염이 까딱이고 한 번 감는다"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    C_ = 15.5
    s = 1.0
    F = Frame(C_, C_ - 2.05 * s, s)
    lines = union(capsule(2.4, C_, 8.6, C_, 0.42), capsule(22.4, C_, 28.6, C_, 0.42),
                  capsule(C_, 1.4, C_, 4.2, 0.42), capsule(C_, 23.4, C_, 28.6, 0.42))
    out = [base(lines), flat(lines, OUT)]
    out += [base(circle(C_, 5.2, 1.25)), part(circle(C_, 5.2, 1.25), lambda x, y: YARN_D if (x - y) % 1.2 < 0.38 else YARN,
                                             shade=YARN_D, line=0.5, ink=YARN_D)]
    out += cat(F, "blink" if k == 8 else "open", body=False, paws=False, tail=False)
    tw = 0.55 * sin(2 * ph)
    for sg in (-1, 1):                                    # 짧은 수염 — 긴 수염 아래로 비스듬히, 끝이 까딱
        x0 = C_ + sg * 7.2
        out.append(flat(capsule(x0, C_ + 1.4, x0 + sg * 3.2, C_ + 2.6 + tw, 0.24), OUT))
    return out


def sc_ibeam(fr):
    """곧게 세운 줄무늬 꼬리가 I 의 세로획 — 끝이 갈고리로 까딱. 그 앞에 앉은 작은 치즈냥이 아래 가로획 자리.
    꼬리 가운데가 핫스팟"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    hook = sin(ph)
    X = 5.5
    tp = [(X, 19.0), (X, 4.0), (X + 1.6 * hook, 1.9)]
    tl = chain(tp, 1.35, 1.2)
    out = [base(tl), part(tl, stripe_along(tp, 2.6, 0.9, 0.7))]
    F = Frame(X + 0.6, 21.0, 0.6)
    out += cat(F, "blink" if k == 6 else "open", tail=False)
    return out


def sc_pen(fr):
    """두 앞발로 연필을 꼭 쥐고 쓴다 — 연필심(왼쪽 아래)이 핫스팟, 연필은 심을 축으로 까딱. 쓰다가 혀를 빼꼼(집중)"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    tip = (1.55, 25.5)
    ang = -0.62 + 0.05 * sin(2 * ph)
    ux, uy = cos(ang), sin(ang)
    L = 17.0
    end = (tip[0] + ux * L, tip[1] + uy * L)
    out = []
    n = 1 + k                                             # 쓴 자국(연필 줄)이 길어진다
    pts = [(3.2 + 1.15 * i, 27.9 + 0.55 * sin(i * 1.7)) for i in range(n + 1)]
    for a, b in zip(pts, pts[1:]):
        out.append(flat(capsule(*a, *b, 0.34), LEAD, 0.75))
    F = Frame(20.2, 9.8, 0.72)
    hold = [F.loc(tip[0] + ux * 13.0, tip[1] + uy * 13.0), F.loc(tip[0] + ux * 15.6, tip[1] + uy * 15.6)]
    out += cat(F, "blink" if k == 4 else "open", look=(-0.8, 0.6), turn_=-0.9, sway=0.5 * sin(ph),
               tongue=0.7 if k % 6 in (2, 3, 4) else 0.0,
               arms=[((-3.6, 6.4), hold[0], False), ((-1.4, 6.8), hold[1], False)])     # 앞발이 몸에서 연필까지 닿게
    w = 1.55
    cone = (tip[0] + ux * 3.6, tip[1] + uy * 3.6)
    pen = smin(0.3, poly([tip, (cone[0] - uy * w, cone[1] + ux * w), (cone[0] + uy * w, cone[1] - ux * w)]),
               capsule(cone[0], cone[1], end[0], end[1], w))

    def pcol(x, y):
        t = (x - tip[0]) * ux + (y - tip[1]) * uy
        sd = -(x - tip[0]) * uy + (y - tip[1]) * ux
        if t < 1.5:
            return LEAD
        if t < 3.7:
            return WOOD
        if t > L - 0.4:
            return ERASER
        if t > L - 2.2:
            return FERRULE if (t - (L - 2.2)) % 0.9 > 0.25 else hx("8e8e98")
        return PENCIL_D if sd > 0.45 else PENCIL
    out += [base(pen), part(pen, pcol, shade=PENCIL_D, line=0.85)]
    for u, v in hold:                                    # 연필을 감싼 앞발(흰 양말)
        p = F.f(ell(u, v, 2.5, 2.3))
        out += [base(p), part(p, CREAMF)]
    return out


def sc_no(fr):
    """빨간 금지 표지 안에서 팔짱 끼고 고개를 홱 돌린 삐짐 — 반 바퀴마다 반대쪽으로 홱(장 0 · 6), 그때 꼬리를 탁 · 움직임 줄"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    C_ = 14.5
    side = -1 if k < 6 else 1
    snap = k in (0, 6)
    turn_ = side * (0.9 if snap else 1.5)
    tw = -side * (2.0 if snap else 1.0)
    F = Frame(C_ + 0.3, C_ - 2.9, 0.66)
    tp = [(3.6, 10.4), (7.8, 10.6), (9.9 + 0.3 * tw, 7.6), (9.4 + tw, 3.9), (8.2 + 1.4 * tw, 2.0)]
    out = cat(F, "sulk", turn_=turn_, mouth="", tail_pts=tp,
              arms=[((-4.4, 6.0), (3.4, 7.6), False), ((4.4, 6.0), (-3.4, 8.4), False)])
    if snap:                                              # 홱 — 돈 쪽 반대편에 움직임 줄
        x0 = C_ - side * 7.4
        for y in (8.6, 11.0, 13.4):
            out += sticker_of(capsule(x0, y, x0 - side * 1.6, y, 0.4), OUT, sh=0.0, line=0.0)
    R = 12.5                                              # 표지 → 냥 → 빗금(머리 자리만 비움): 빗금이 몸을 가로질러 금지로 읽히고 얼굴은 앞에 보인다
    sl = cut(capsule(C_ - R * 0.62, C_ - R * 0.62, C_ + R * 0.62, C_ + R * 0.62, 1.35), grow(head_f(F), 0.9))
    return sign_ring(C_, R) + out + [base(sl), part(sl, SIGN, shade=SIGN_D, ink=SIGN_D, line=0.8)]


def _stretch(fr, C_, ang, length, s, chev, head, hoff, **kw):
    """catkit 기지개 — 몸 줄무늬를 축에 맞추고(axis), 쭉 늘 때 눈을 질끈(><). 그리는 동안만 catkit.cat 을 바꿔 끼운다
    (한 프로세스가 한 칸씩 그린다는 catkit 의 전제 그대로)"""
    sq = sin(TAU * fr) > 0.2
    r = 3.3 * s / 0.6
    COAT.axis = (C_[0], C_[1], cos(ang), sin(ang), -head[0], -head[1], r)

    def c(F, mood="open", *a, **k):
        return cat(F, "squeeze" if sq else ("open" if mood == "happy" else mood), *a, **k)
    catkit.cat = c
    try:
        return stretch(fr, C_, ang, length, s, chev, head, hoff, **kw)
    finally:
        catkit.cat = _cat
        COAT.axis = None


def sc_we(fr):
    return _stretch(fr, (15.8, 10.0), 0.0, 13.0, 0.6, [(1.9, 10.0, -1, 0), (29.1, 10.0, 1, 0)], (0.0, -1.0), 2.6)


def sc_nwse(fr):
    return _stretch(fr, (14.8, 13.6), pi / 4, 13.0, 0.6, [(3.4, 2.2, -1, -1), (26.2, 25.0, 1, 1)], (0.45, -0.9), 1.8)


def sc_nesw(fr):
    return _stretch(fr, (13.2, 13.6), 3 * pi / 4, 13.0, 0.6, [(24.6, 2.2, 1, -1), (1.8, 25.0, -1, 1)], (-0.45, -0.9), 1.8)


def sc_ns(fr):
    """세로 기지개: 앞발 둘을 머리 위로 쭉, 몸이 세로로 늘었다 줄었다 · 뒷발은 아래로. 늘 때 눈을 질끈.
    머리는 똑바로 두고 앞발은 머리 뒤에서 솟는다(원본처럼 왼쪽 위로) — 머리를 감싸면 두건으로 읽힌다(원본 주석)"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    st = (1 + sin(ph)) / 2                               # 0 줄음 → 1 쭉
    X = 6.6
    top, bot = 13.6, 23.0 + 1.4 * st
    r = 2.9
    body = taper(X, top, r, X, bot, r * 0.92)
    reach = 1.3 * st
    arms = [(X - 1.4, 13.0, X - 4.0, 5.4 - reach), (X + 0.4, 13.0, X - 1.4, 4.6 - reach)]
    arm_fs = [capsule(a, b, c_, d, 1.7) for a, b, c_, d in arms]
    pawf = [ell(c_, d - 0.3, 2.05, 2.15) for _, _, c_, d in arms]       # 먹선 안에 크림이 남는 크기
    legs = [oell(X - 1.6, bot + 1.8, 1.25, 1.75, 0.2), oell(X + 1.6, bot + 1.8, 1.25, 1.75, -0.2)]
    tw = 0.8 * sin(2 * ph)
    tp = [(X + 1.6, bot - 0.6), (X + 4.6, bot - 0.4), (X + 5.8, bot - 3.6), (X + 5.2 + 0.6 * tw, bot - 6.6)]
    tl = chain(tp, 1.4, 1.25)
    COAT.axis = (X, top, 0.0, 1.0, 1.0, 0.0, r)          # 배는 오른쪽(꼬리 반대 아님 — 흰 배가 앞에 보이게)
    try:
        bcol = COAT.fur("body")
    finally:
        COAT.axis = None
    out = [base(tl, *legs, body, *arm_fs, *pawf), part(tl, stripe_along(tp, 2.6, 0.9, 0.5))]
    for f in legs:
        out.append(part(f, CREAMF))
    out.append(part(body, lambda x, y: CREAMF if abs(x - X - 0.5) < 0.6 and y > top + 2.0 else bcol(x, y)))
    for f in arm_fs:
        out.append(part(f, FUR))
    for f in pawf:
        out.append(part(f, CREAMF))
    F = Frame(X, 10.6, 0.56)
    out += cat(F, "squeeze" if st > 0.6 else ("blink" if k == 9 else "open"), body=False, paws=False, tail=False)
    o = 0.6 if st > 0.6 else 0.0
    out += chevron(X, 1.6 - o, 0, -1, 2.2, 1.0 if o else 0.75)
    out += chevron(X, 29.6 + o * 0.5, 0, 1, 2.2, 1.0 if o else 0.75)
    return out


def _face_rot(F, mood):
    """도는 틀(F.ang)에 붙은 얼굴 — 눈 · 코 · 볼을 캐논에서 그려 같이 돈다(catkit.face 는 화면에 똑바로 그린다)"""
    out = []
    for sg in (-1, 1):
        out.append(soft(F.f(ell(sg * 4.5, 2.7, 1.45, 0.9)), catkit.C.cheek, 0.85))
    for sg in (-1, 1):
        if mood == "happy":
            out.append(flat(F.f(arc(sg * 3.15, 0.25 + 1.66 * 0.55, 1.66 * 0.95, 0.42, pi * 1.2, pi * 0.6)), catkit.C.eye))
        else:
            out.append(flat(F.f(ell(sg * 3.15, 0.25, 1.4, 1.6)), catkit.C.eye))
    nose = F.f(rpoly([(-0.8, 1.7), (0.8, 1.7), (0.0, 2.55)], 0.25))
    out.append(flat(nose, catkit.C.nose))
    return out


def sc_move(fr):
    """배를 깔고 동그랗게 만 치즈냥(위에서 본)이 데굴데굴 한 바퀴(눈은 ^^) — 네 방향 분홍 화살촉이 두근댄다"""
    k = round(fr * NF) % NF
    o = 0.6 if k % 6 < 3 else 0.0
    out = []
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        out += chevron(15.5 + dx * (13.6 + o), 15.5 + dy * (13.6 + o), dx, dy, 2.2)
    a = TAU * k / NF
    F = Frame(15.5, 15.5, 1.0, a)
    ball = F.f(ell(0, -0.4, 8.2, 7.6))

    def bcol(x, y):
        u, v = F.loc(x, y)
        t = (math.atan2(v + 0.4, u) * 7 / pi) % 2
        return STRIPE if t < 0.55 and hypot(u, v + 0.4) > 4.0 else FUR
    tp = [(7.0, -1.4), (6.4, 4.0), (3.0, 7.0)]
    tl = F.f(chain(tp, 1.75, 1.45))
    H = Frame(*F.w(0.0, 2.2), 0.6, a)
    hd = H.f(head_f(Frame()))
    ears = [H.f(rpoly(ear_pts(sg), 0.95)) for sg in (-1, 1)]
    out += [base(ball, tl), part(ball, bcol), part(tl, lambda x, y: STRIPE if hypot(*F.loc(x, y)) % 2.6 < 0.9 else FUR)]
    out += [base(hd, *ears)]
    for sg, E in zip((-1, 1), ears):
        out.append(part(E, FUR))
        pts = ear_pts(sg)
        cx, cy = sum(p[0] for p in pts) / 3, sum(p[1] for p in pts) / 3 + 0.5
        out.append(flat(H.f(rpoly([(cx + (x - cx) * 0.5, cy + (y - cy) * 0.5) for x, y in pts], 0.5)), catkit.C.ear))
    out.append(part(hd, _head_col(H, 0.0)))
    out += _face_rot(H, "happy")
    return out


def sc_up(fr):
    """두 앞발을 옆으로 활짝 든 만세 \\(^ㅅ^)/ — 츄르 달라고 들썩이며 입을 냥냥 벌린다(장 0–1 · 4–5 · 8–9).
    머리는 그 자리에 두어 핫스팟(두 귀 사이 머리 꼭대기)이 장마다 같은 칸이다. 앞발만 오르내린다"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    s = 0.7
    F = Frame(10.5, 2.55 + 6.0 * s, s)
    lift = 1.3 * abs(sin(ph))
    nyang = k % 4 < 2
    out = [layer(ell(10.5, 18.2, 5.6, 0.8), lambda *a: (OUT, 0.18))]
    out += cat(F, "happy" if nyang else "open", look=(0.0, -0.4), mouth="nyang" if nyang else "w",
               sway=0.6 * sin(2 * ph), bob=0.3 * abs(sin(ph)),
               arms=[((-5.6, 6.6), (-11.2, -4.6 - lift), True), ((5.6, 6.6), (11.2, -4.6 - lift), True)])
    return out


def sc_hand(fr):
    """분홍 젤리 발바닥을 보이며 앞발로 꾹 — 누를 때(장 4–7) 발바닥이 옆 · 아래로 납작하게 퍼지고(위 끝은 그대로) 눈을 질끈.
    발바닥 꼭대기가 핫스팟"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    press = k in (4, 5, 6, 7)
    sq = 0.9 if press else 0.0
    rx, ry = 4.8 + sq, 4.6 - sq * 0.5
    pcx, pcy = 9.0, 1.45 + ry                             # 위 끝(1.45)은 그대로
    lean = 0.5 if press else 0.0
    F = Frame(19.6 - lean, 16.0, 0.74)
    sh = F.w(-4.2, 4.4)
    arm = taper(sh[0], sh[1], 2.2, pcx + 1.6, pcy + 1.6, 2.5)
    out = [base(arm), part(arm, lambda x, y: STRIPE if (x + y) % 3.0 < 0.95 else FUR)]
    tp = [(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.4 + 0.6 * sin(ph), 3.9), (8.2 + 0.9 * sin(ph), 2.0)]
    out += cat(F, "squeeze" if press else "open", look=(-0.7, -0.6), turn_=-0.6, tail_pts=tp, paws=True)
    pad = ell(pcx, pcy, rx, ry)
    out += [base(pad), part(pad, CREAMF)]
    bx, by = pcx, pcy + ry * 0.3                          # 큰 젤리(가로로 넓은 세모꼴) + 발가락 젤리 넷 부채꼴
    out.append(flat(rpoly([(bx - 2.2 - sq * 0.6, by - 0.4), (bx + 2.2 + sq * 0.6, by - 0.4), (bx + 1.2, by + 2.0),
                           (bx - 1.2, by + 2.0)], 0.7), PINK, line=0.3, ink=hx("d8728a")))
    for tx, ty in ((-3.1 - sq * 0.5, -1.5), (-1.15, -3.0), (1.15, -3.0), (3.1 + sq * 0.5, -1.5)):
        out.append(flat(ell(bx + tx, by + ty, 0.85, 1.0), PINK, line=0.25, ink=hx("d8728a")))
    if press:                                             # 꾹 — 발바닥 둘레 눌림 줄
        for a in (-2.6, -2.0, 2.6 - pi, 0.55, 0.0):
            ex, ey = pcx + (rx + 1.4) * cos(a), pcy + (ry + 1.4) * sin(a)
            if 1.0 < ex < 30.5 and 1.0 < ey < 30.5:
                out += sticker_of(capsule(ex, ey, ex + 1.3 * cos(a), ey + 1.3 * sin(a), 0.38), OUT, sh=0.0, line=0.0)
    return out


SCENE = {"busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "wait": sc_wait,
         "hand": sc_hand, "cross": sc_cross, "ibeam": sc_ibeam, "move": sc_move, "no": sc_no, "pen": sc_pen,
         "up": sc_up, "we": sc_we, "ns": sc_ns, "nwse": sc_nwse, "nesw": sc_nesw}


class CheeseCat(Pet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = CheeseCat(COAT, SCENE, HOT)


def scene(name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
    return PET.cell(name, frame, soft_, tip_body, shape)


register("cheesecat", PET)

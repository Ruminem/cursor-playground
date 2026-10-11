# SPDX-License-Identifier: Apache-2.0
"""고등어냥(mackerelcatanim) 고화질 — 흰냥이와 같은 치비 틀(catkit)에 회색 고등어 줄무늬 털빛.

픽셀 고등어냥(gen/mackerelcat.py)의 털빛(회색 바탕 · 짙은 회색 줄 · 이마 M · 볼 가로 줄 둘 · 흰 주둥이와 가슴 조금 ·
밝은 회색 발 · 고리 무늬 꼬리 · 초록 눈)과 칸마다 하는 짓을 HD 로 옮겼다. 신호색(화살촉 · 조준 눈금)은 눈 색 초록이다.

  arrow   크림 화살표 빗변 뒤에서 빼꼼(catkit peek)
  busy    작은 화살표 냥 + 물그릇 둘레를 도는 젖은 파란 발자국 여덟
  help    작은 화살표 냥이 제 고리 꼬리로 물음표를 그린다 — 점은 초록 공
  person  작은 화살표 냥 + 고등어냥을 품에 꼭 안은 사람. 늘어진 꼬리가 흔들린다
  pin     작은 화살표 냥 + 크림 발자국이 찍힌 빨간 지도 핀이 통통
  wait    앉아서 그루밍 — 든 앞발을 할짝(장 0–5) · 그 발로 볼에서 귀까지 쓱(6–10) · 눈 뜸(11). 꼬리가 발을 감싼다
  cross   앞모습 사냥 얼굴 — 세로 동공이 가늘었다 커진다. 수염이 가로 조준선, 귀 사이 · 턱 밑 초록 눈금. 코가 핫스팟
  hand    엎드린 냥이 앞발을 왼쪽 위로 쭉 내밀어 발톱으로 톡톡 — 발톱 끝이 핫스팟
  ibeam   I 꼴 스크래쳐(위아래 판 · 노끈 기둥)를 두 앞발로 번갈아 벅벅 — 기둥 가운데가 핫스팟
  move    납작 엎드려 네 발을 쭉 뻗은(위에서 본) 냥 — 등의 가로 줄이 고등어. 네 방향 초록 화살촉
  we · ns · nwse · nesw   기지개(롱캣) — 몸 줄무늬가 몸 축을 가로지른다. 양 끝 초록 화살촉이 두근
  no      빨간 금지 표지 안에서 등을 돌리고 앉아(쌩) 꼬리를 탁탁 — 장 7–9 에 어깨 너머로 힐끔(초록 눈 하나)
  pen     연필을 입에 물고 쓴다 — 연필심(왼쪽 아래)이 핫스팟, 연필 줄이 자란다
  up      서서 한 앞발을 머리 위로 쭉(저요!) — 발끝(맨 위)이 핫스팟, 눈은 위를 본다

좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 장면은 NF 장으로 나뉘어 있다(k = round(fr × NF) % NF).
틀(먹선 · 치비 몸 · 빼꼼 · 기지개 · 모양 화살표)은 catkit 에 있고 여기는 털빛 · 소품 · 장면만 둔다.
"""
from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

from . import catkit, register
from .catkit import *  # noqa: F401,F403
import math

atan2, fmod = math.atan2, math.fmod

# 픽셀 판 팔레트(gen/mackerelcat.py) 그대로 + 셀 그늘 · 초록 단
OUT, EYE = hx("34353d"), hx("1c1d22")
FUR, FUR_L, STRIPE, SHADE = hx("9a9ca4"), hx("b9bbc2"), hx("666871"), hx("80828b")
WHITE, NOSE, RIM = hx("f4f3ee"), hx("e27d90"), hx("e8eaf0")
GREEN, GREEN_D, GREEN_L = hx("6cc04a"), hx("3f8a2c"), hx("b6ec98")
WET, WET_D = hx("5aa8d8"), hx("3a7fb0")
BOWL, BOWL_D, BOWL_L, WATER, WATER_L = hx("e07a5a"), hx("b0553c"), hx("f0a084"), hx("7cc4e8"), hx("c8ecfa")
SISAL, SISAL_D, PLATE, PLATE_D, SCRATCH = hx("e0c08c"), hx("b8925a"), hx("8a6a52"), hx("6a4e3c"), hx("fff4dc")
PENCIL, PENCIL_D, WOOD, LEAD = hx("f5c842"), hx("c8961c"), hx("efd2a8"), hx("3a3a3a")
ERASER, FERRULE = hx("f2a0a8"), hx("b8b8c0")
SKIN, HAIR = hx("f7d7bc"), hx("6a4a3a")
SHIRT, SHIRT_D = hx("e8a33a"), hx("c07e22")                    # 사람 옷 (회색 냥이와 갈리게 주황)
SIGN, SIGN_D, SIGN_L = hx("d64541"), hx("9e2b28"), hx("ef7a72")


# ---- 털빛: 고등어 줄무늬 ----

M_PTS = [(-2.6, -2.2), (-1.55, -5.15), (0.0, -2.9), (1.55, -5.15), (2.6, -2.2)]   # 이마 M (캐논)


def _seg(px, py, pts):
    """꺾은선까지 거리"""
    best = 1e9
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        ex, ey = bx - ax, by - ay
        t = clamp(((px - ax) * ex + (py - ay) * ey) / (ex * ex + ey * ey or 1e-9))
        best = min(best, hypot(px - ax - ex * t, py - ay - ey * t))
    return best


def along(pts):
    """꺾은선 위 가장 가까운 자리까지의 길이(처음부터) — 꼬리 고리 무늬. → (함수, 전체 길이)"""
    segs, acc = [], 0.0
    for p, q in zip(pts, pts[1:]):
        L = hypot(q[0] - p[0], q[1] - p[1]) or 1e-9
        segs.append((p, q, L, acc))
        acc += L

    def at(a, b):
        best, s = 1e9, 0.0
        for p, q, L, s0 in segs:
            t = clamp(((a - p[0]) * (q[0] - p[0]) + (b - p[1]) * (q[1] - p[1])) / (L * L))
            d = hypot(a - p[0] - (q[0] - p[0]) * t, b - p[1] - (q[1] - p[1]) * t)
            if d < best:
                best, s = d, s0 + L * t
        return s
    return at, acc


def ringed(at, total, W, P=3.2, tip=True):
    """꼬리 길이 s → 줄(밑동 1칸은 털, 끝은 짙게)"""
    def col(s):
        if tip and s > total - W * 0.9:
            return STRIPE
        return STRIPE if s > 1.0 and fmod(s, P) > P - W else FUR
    return col


class Tabby(Coat):
    """고등어 털빛 — fur(부위, F, turn_) 가 (x, y) → 색을 준다. 줄 굵기는 32 로 줄여도 1px 남게 배율로 굵힌다.
    장면이 넘겨 주는 것(그리기 직전에 넣고, 꼬리는 한 번 쓰면 비움):
      tail  꼬리 꺾은선(캐논) — 길이 따라 고리. 없으면 말린 꼬리 가운데를 도는 각도로 고리(catkit 빼꼼 · 동반 냥)
      arms  팔 (어깨, 손) 목록(캐논) — 팔을 가로지르는 줄, cat 이 그리는 차례대로 하나씩 꺼낸다
      axis  기지개 몸 축(화면 단위 벡터) — F 없이 불리는 stretch 몸 줄이 축을 가로지른다
    back 이면 뒷모습(뒤통수 세로 줄 셋 · 등줄기)"""

    def __init__(self, *a, back=False, **kw):
        super().__init__(*a, **kw)
        self.back, self.tail, self.axis, self.arms = back, None, (1.0, 0.0), []

    def fur(self, part, F=None, turn_=0.0):
        if part in ("paw", "hand", "front", "back"):
            return FUR_L
        if part == "ear":
            return FUR
        if F is None:                                   # stretch: 화면 좌표
            if part == "body":
                ax, ay = self.axis
                return lambda x, y: STRIPE if fmod(x * ax + y * ay + 64.0, 3.0) < 1.25 else FUR
            if part == "tail":
                return lambda x, y: STRIPE if fmod(x * 0.7 - y * 0.7 + 64.0, 2.6) < 1.0 else FUR
            return FUR
        s = F.s
        W = max(1.35, 1.05 / s)                          # 줄 굵기(캐논) — 1px 아래로 안 가게
        loc = F.loc
        if part == "head":
            hw = max(0.6, 0.55 / s)
            back = self.back

            def head(x, y):
                u, v = loc(x, y)
                mu = u - turn_
                if back:
                    return STRIPE if v < 3.2 and min(abs(mu - d * 2.4) for d in (-1, 0, 1)) < hw else FUR
                if (mu / 2.7) ** 2 + ((v - 3.05) / 1.65) ** 2 <= 1:
                    return WHITE                        # 흰 주둥이
                if _seg(mu, v, M_PTS) < hw:
                    return STRIPE                       # 이마 M
                if abs(mu) > 5.15 and min(abs(v + 0.35), abs(v - 1.75)) < hw:
                    return STRIPE                       # 볼 가로 줄 둘
                return FUR
            return head
        if part == "body":
            back = self.back

            def body(x, y):
                u, v = loc(x, y)
                band = fmod(v - 5.0 + 64.0, 3.4) < W
                if back:
                    return STRIPE if abs(u) < 0.5 * W or band else FUR
                if (u / 2.4) ** 2 + ((v - 6.6) / 2.1) ** 2 <= 1:
                    return WHITE                        # 흰 가슴
                return STRIPE if abs(u) > 2.5 and band else FUR
            return body
        if part == "tail":
            pts, self.tail = self.tail, None
            if pts:
                at, total = along(pts)
                c = ringed(at, total, W)
                return lambda x, y: c(at(*loc(x, y)))
            return lambda x, y: (STRIPE if fmod(atan2(loc(x, y)[1] - 6.2, loc(x, y)[0] - 5.8) * 4.4 + 64.0, 3.2) > 3.2 - W
                                 else FUR)
        if part == "arm" and self.arms:
            (ax, ay), (bx, by) = self.arms.pop(0)
            L = hypot(bx - ax, by - ay) or 1e-9
            dx, dy = (bx - ax) / L, (by - ay) / L

            def arm(x, y):
                u, v = loc(x, y)
                t = (u - ax) * dx + (v - ay) * dy
                return STRIPE if 2.0 < t < L - 2.6 and fmod(t + 64.0, 3.4) < W else FUR
            return arm
        if part == "loaf":                               # 엎드린 몸 — 등을 가로지르는 세로 줄(고등어)
            return lambda x, y: (STRIPE if fmod(loc(x, y)[0] + 64.0, 3.4) < W and loc(x, y)[1] < 8.6 else FUR)
        if part == "top":                                # 위에서 본 등 — 가로 줄 + 등줄기
            def top(x, y):                               # 등줄기에서 옆구리로 비스듬히 내려가는 갈비 줄
                u, v = loc(x, y)
                if abs(u) < 0.45 * W:
                    return STRIPE
                return STRIPE if abs(u) > 1.6 and fmod(v - 0.45 * abs(u) + 64.0, 3.6) < W else FUR
            return top
        return FUR


IRIS = (GREEN, GREEN_D, GREEN_L)
COAT = Tabby(FUR, SHADE, OUT, EYE, RIM, (IRIS, IRIS), nose=NOSE)
BACK = Tabby(FUR, SHADE, OUT, EYE, RIM, (IRIS, IRIS), ear=SHADE, nose=NOSE, back=True)

# art 파일(art/mackerelcatanim/*.txt) 머리의 핫스팟 그대로 — 적용한 사람의 손에 익은 자리
HOT = {"arrow": (1, 1), "busy": (1, 1), "cross": (15, 15), "hand": (4, 4), "help": (1, 1), "ibeam": (7, 15),
       "move": (15, 15), "nesw": (15, 15), "no": (15, 15), "ns": (7, 15), "nwse": (15, 15), "pen": (1, 27),
       "person": (1, 1), "pin": (1, 1), "up": (14, 1), "wait": (10, 14), "we": (15, 7)}


def tabby(F, *a, tail_pts=None, sway=0.0, **kw):
    """catkit.cat 에 꼬리 꺾은선을 털빛에 먼저 넘겨 고리가 꼬리를 따라 돌게"""
    if kw.get("tail", True):
        tp = tail_pts or [(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.4 + sway, 3.9), (8.2 + 1.4 * sway, 2.0)]
        catkit.C.tail = tp
        kw["tail_pts"] = tp
    catkit.C.arms = [(sh_, hand) for sh_, hand, _ in kw.get("arms", ())]
    return cat(F, *a, sway=sway, **kw)


def kof(fr):
    return round(fr * NF) % NF


# ---- 소품 ----

def gchev(cx, cy, dx, dy, L=2.2, a=1.0):
    """(dx, dy) 쪽을 가리키는 초록 화살촉 — 꼭짓점이 (cx, cy). catkit chevron 의 초록 판"""
    n = hypot(dx, dy)
    dx, dy = dx / n, dy / n
    px, py = -dy, dx
    f = union(*[capsule(cx, cy, cx - dx * L + s * px * L, cy - dy * L + s * py * L, 0.72) for s in (-1, 1)])
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(GREEN, GREEN_D, smooth(0.36, 0.2, -e)), 1.0), alpha=a)]


def pal(fr, tail=True):
    """동반: 작은 화살표 + 작은 고등어냥(catkit buddy 와 같은 자리 · 박자, 꼬리를 뺄 수 있게)"""
    ph = TAU * fr
    F = Frame(13.6, 7.7, 0.58)
    return small_arrow() + tabby(F, "blink" if blink_of(fr, 0.25) else "open", look=(-0.4, 0.0), sway=0.5 * sin(ph),
                                 bob=0.4 * (1 - cos(ph)) / 2, tail=tail)


def stroke(pts, r, W=1.0, P=2.6):
    """화면 좌표 꺾은선 꼬리(고리 무늬) 스티커"""
    f = chain(pts, r, r * 0.9)
    at, total = along(pts)
    c = ringed(at, total, W, P)
    return [base(f), part(f, lambda x, y: c(at(x, y)))]


def bowl(cx, cy, rx, ry, k):
    """앞에서 본 테라코타 물그릇 — 위가 물낯(반짝 띠가 돈다)"""
    top = ell(cx, cy, rx, ry)
    body = smin(0.5, top, rbox(cx, cy + ry * 0.9, rx * 0.86, ry * 0.9, 0.2), ell(cx, cy + ry * 1.75, rx * 0.66, ry * 0.7))
    surf = ell(cx, cy + 0.05, rx - 1.1, ry - 0.7)
    sx = cx - rx * 0.55 + (k % 6) / 5 * rx * 1.1

    def bcol(x, y):
        c = lerp(BOWL_L, BOWL, smooth(cx - rx * 0.7, cx - rx * 0.2, x))
        return lerp(c, BOWL_D, smooth(cy + ry * 1.3, cy + ry * 2.1, y))

    def wcol(x, y):
        return lerp(WATER, WATER_L, smooth(0.9, 0.3, abs(x - sx)) * smooth(cy + 0.5, cy - 0.3, y))
    return [base(body), part(body, bcol, shade=BOWL_D, ink=BOWL_D, sh=0.6),
            flat(surf, wcol, line=0.35, ink=hx("3a7fb0"))]


def wet_print(x, y, a):
    f = union(ell(x, y + 0.6, 1.15, 0.95), circle(x - 1.35, y - 0.75, 0.55), circle(x, y - 1.35, 0.55),
              circle(x + 1.35, y - 0.75, 0.55))
    return layer(f, lambda px, py, e, nx, ny, fr: (lerp(WET, WET_D, smooth(0.3, 0.15, -e)), 1.0), alpha=a)


# ---- 칸마다 장면 (art 좌표, 화살표 칸은 catkit 빼꼼) ----

def sc_busy(fr):
    """작은 화살표 냥 + 물그릇 둘레를 도는 젖은 발자국 여덟(물그릇에 발을 담갔다)"""
    out = pal(fr)
    cx, cy = 22.5, 22.5
    k = kof(fr)
    head = k * 8 / NF
    for i in range(8):
        a = TAU * i / 8 - pi / 2
        lag = (head - i) % 8
        out.append(wet_print(cx + 6.9 * cos(a), cy + 6.6 * sin(a), 1.0 if lag < 1.5 else 0.6 if lag < 3 else 0.28))
    out += bowl(cx, cy - 0.8, 4.2, 1.5, k)
    return out


def sc_help(fr):
    """작은 화살표 냥이 엉덩이에서 뺀 고리 꼬리로 물음표 — 끝이 살랑, 점은 초록 공"""
    ph = TAU * fr
    sw = 0.6 * sin(ph)
    c, r = (23.4, 10.4), 3.5
    hook = [(c[0] + r * cos(math.radians(a)), c[1] + r * sin(math.radians(a))) for a in (165, 205, 240, 270, 300, 335, 15, 50)]
    pts = [(15.4, 13.6), (18.0, 13.7)] + hook + [(23.7, 15.2), (23.5, 17.6), (23.5 + sw, 19.8)]
    out = stroke(pts, 1.2, 1.0, 2.6)
    out += pal(fr, tail=False)
    b = circle(23.5, 23.6, 1.7)
    out += [base(b), part(b, lambda x, y: lerp(GREEN_L, GREEN, smooth(22.4, 24.2, y + 0.4 * (x - 23.5))), shade=GREEN_D,
                          ink=GREEN_D, line=0.8)]
    return out


def sc_pin(fr):
    """작은 화살표 냥 + 크림 발자국이 찍힌 빨간 지도 핀이 통통(닿을 때 그림자가 진하다)"""
    out = pal(fr)
    hop = abs(sin(pi * fr))
    cx, cy = 22.6, 15.4 - 2.6 * hop
    out.insert(0, layer(ell(22.8, 29.0, 3.4 - 0.8 * hop, 0.75), lambda *a: (GREEN_D, 0.35 - 0.15 * hop)))
    f = smin(1.0, circle(cx, cy, 5.6), poly([(cx - 4.6, cy + 2.6), (cx + 4.6, cy + 2.6), (cx, cy + 11.4)]))
    out += [base(f), part(f, lambda x, y: lerp(SIGN_L, SIGN, smooth(cy - 5, cy - 1.5, y + 0.6 * (x - cx))), shade=SIGN_D,
                          ink=SIGN_D)]
    pw = union(ell(cx, cy + 1.2, 1.9, 1.5), circle(cx - 2.15, cy - 0.85, 0.85), circle(cx - 0.75, cy - 2.25, 0.85),
               circle(cx + 0.75, cy - 2.25, 0.85), circle(cx + 2.15, cy - 0.85, 0.85))
    out.append(flat(pw, WHITE))
    return out


def sc_person(fr):
    """작은 화살표 냥 + 고등어냥을 품에 꼭 안은 사람 — 소매가 냥이 배를 감싸고 앞발이 소매 위로, 꼬리가 아래로 대롱"""
    ph = TAU * fr
    k = kof(fr)
    out = pal(fr)
    cx = 23.6
    body = clip_y(ell(cx, 28.4, 7.4, 9.6), 31.0)
    head = circle(cx, 11.4, 3.7)
    hair = smin(0.6, ell(cx, 9.4, 4.0, 2.3), ell(cx - 3.3, 11.0, 1.0, 1.9), ell(cx + 3.3, 11.0, 1.0, 1.9))
    out += [base(body, head, hair), part(body, SHIRT, shade=SHIRT_D), part(head, SKIN, shade=hx("e8bfa0")),
            part(hair, HAIR, shade=hx("4a3226"))]
    for sg in (-1, 1):
        out.append(flat(ell(cx + sg * 1.4, 11.7, 0.45, 0.62), EYE))
        out.append(soft(ell(cx + sg * 2.3, 13.0, 0.8, 0.5), hx("f7a3b5"), 0.8))
    out.append(flat(arc(cx, 12.9, 0.75, 0.2, pi * 0.15, pi * 0.7), SHIRT_D))
    # 품에 안긴 냥 — 머리는 사람 턱 밑, 몸은 두 팔이 U 자로 받친다
    F = Frame(cx, 19.4, 0.46)
    out += tabby(F, "blink" if k in (4, 5) else "open", paws=False, tail=False)
    sw = 1.0 * sin(ph)
    out += stroke([(cx + 2.4, 25.0), (cx + 3.4, 27.4), (cx + 2.8 + sw, 30.0)], 0.95, 0.8, 2.0)
    sl = arc(cx, 7.4, 16.4, 1.6, pi * 0.355, pi * 0.29)
    out += [base(sl), part(sl, SHIRT_D, shade=hx("9c6418"))]
    for sg in (-1, 1):                                  # 소매 위로 늘어진 앞발
        p = ell(cx + sg * 1.5, 22.6, 1.0, 0.8)
        out += [base(p), part(p, FUR_L)]
    return out


def sc_wait(fr):
    """앉아서 그루밍 — 장 0–5 든 앞발 할짝(혀 날름 · 눈 ^^), 6–10 그 발로 볼에서 귀까지 쓱, 11 눈 뜸.
    꼬리는 발을 감싸고 끝만 까딱"""
    ph = TAU * fr
    k = kof(fr)
    F = Frame(11.0, 11.2, 0.86)
    tw = 0.8 * sin(2 * ph)
    tp = [(4.4, 9.8), (4.0, 12.8), (0.0, 13.6), (-4.4, 13.0), (-6.8 + 0.4 * tw, 11.2 + tw)]
    lick = False
    if k < 6:
        lick = k % 2 == 1
        hand, turn_, mood, jelly = (-5.2, 4.6 + (0.0 if lick else 0.6)), -1.0, "happy", True
    elif k < 11:
        t = sin(pi * (k - 5) / 6)
        hand, turn_, mood, jelly = (-6.2 - 1.0 * t, 3.2 - 6.6 * t), -0.5, "happy", False
    else:
        hand, turn_, mood, jelly = (-2.8, 8.2), 0.0, "open", False
    out = tabby(F, mood, turn_=turn_, tail_pts=tp, arms=[((-3.8, 5.8), hand, jelly)])
    if lick:                                            # 혀 날름 — 입에서 든 앞발 쪽으로
        nx, ny = F.w(turn_, 2.05)
        hx_, hy_ = F.w(*hand)
        y0 = ny + 1.05
        tip = (hx_ + 1.6, hy_ - 0.2)
        f = smin(0.35, capsule(nx - 0.2, y0, tip[0], tip[1], 0.55), circle(tip[0], tip[1] + 0.1, 0.65))
        out.append(flat(f, PINK, line=0.22, ink=NOSE))
    return out


def slit_eye(cx, cy, rx, wid, look=(0.0, 0.0)):
    """사냥 눈 — 초록 홍채에 세로 동공(wid 는 동공 반폭 / 눈 반폭), 왼쪽 위 반짝"""
    ry = rx * 1.16
    px = cx + look[0] * rx * 0.2
    h1 = (cx - rx * 0.4, cy - ry * 0.42, rx * 0.3)

    def paint(x, y, e, nx, ny, fr):
        c = lerp(GREEN_L, GREEN, smooth(cy - ry * 0.9, cy - ry * 0.1, y))
        c = lerp(c, GREEN_D, 0.45 * smooth(cy + ry * 0.3, cy + ry * 1.0, y))
        c = lerp(c, EYE, smooth(0.12, -0.12, hypot((x - px) / (rx * wid), (y - cy) / (ry * 0.86)) - 1))
        c = lerp(c, HI, smooth(h1[2] + 0.1, h1[2] - 0.1, hypot(x - h1[0], y - h1[1])))
        return lerp(c, GREEN_D, smooth(0.26, 0.1, -e)), 1.0
    return layer(ell(cx, cy, rx, ry), paint)


def sc_cross(fr):
    """앞모습 사냥 얼굴 — 세로 동공이 가늘었다(장 0–3) 둥글게 커진다(4–9). 수염 한 줄씩이 가로 조준선,
    귀 사이 · 턱 밑 초록 눈금이 세로선. 귀 쫑긋(6–7), 코가 핫스팟"""
    ph = TAU * fr
    k = kof(fr)
    C_ = 15.5
    s = 1.04
    F = Frame(C_, C_ - 2.05 * s, s)
    lines = union(capsule(2.4, C_, 5.6, C_, 0.5), capsule(25.4, C_, 28.6, C_, 0.5))
    out = [base(lines), flat(lines, OUT)]
    tw = 0.5 * sin(2 * ph)
    for sg in (-1, 1):                                  # 수염 — 조준선으로 이어진다
        out.append(flat(capsule(C_ + sg * 7.2, C_, C_ + sg * 10.4, C_, 0.24), OUT))
        out.append(flat(capsule(C_ + sg * 7.4, C_ + 1.2, C_ + sg * 10.2, C_ + 1.9 + 0.4 * tw, 0.22), OUT))
    o = 0.8 if k % 6 < 3 else 0.0
    ticks = union(capsule(C_, 1.9, C_, 3.4 + o, 0.55), capsule(C_, 22.6 - o, C_, 28.8, 0.55))
    out += [base(ticks), flat(ticks, lambda x, y: lerp(GREEN_L, GREEN, 0.6), line=0.4, ink=GREEN_D)]
    out += tabby(F, "open", body=False, paws=False, tail=False, ear_tilt=(0.0, 0.9) if k in (6, 7) else (0.0, 0.0))
    wid = (0.2, 0.2, 0.22, 0.28, 0.45, 0.6, 0.66, 0.66, 0.6, 0.48, 0.32, 0.24)[k]
    er = max(1.66 * s, 1.32)
    for sg in (-1, 1):
        ex, ey = F.w(sg * 3.15, 0.25)
        out.append(slit_eye(ex, ey, er, wid))
    return out


def sc_hand(fr):
    """엎드린 냥이 앞발을 왼쪽 위로 쭉 내밀어 발톱 하나로 톡톡 — 발톱 끝이 핫스팟. 톡 칠 때(장 2–3 · 8–9) 눌림 줄"""
    ph = TAU * fr
    k = kof(fr)
    tap = k in (2, 3, 8, 9)
    s = 0.72
    F = Frame(15.4, 14.8, s)
    sw = sin(ph)
    tip = (4.55, 4.55)
    hand_art = (6.95 - (0.0 if tap else 0.35), 6.95 - (0.0 if tap else 0.35))
    hand = F.loc(*hand_art)
    loaf = F.f(ell(6.6, 6.4, 7.8, 4.3))
    paw2 = F.f(ell(1.4, 8.4, 2.2, 1.5))
    tp = [(11.4, 5.2), (13.0, 1.6), (11.8 + 1.4 * sw, -2.4)]
    catkit.C.tail = tp
    under = [(loaf, COAT.fur("loaf", F)), (paw2, FUR_L)]
    out = tabby(F, "blink" if k == 6 else "open", turn_=-0.4, look=(-0.9, -0.8), body=False, paws=False,
                tail_pts=tp, extra_under=under, arms=[((-6.6, 3.4), hand, False)])
    hx_, hy_ = hand_art                                 # 발톱 — 발끝에서 핫스팟까지 크림 갈고리
    cl = smin(0.3, capsule(hx_ - 1.2, hy_ - 1.2, tip[0] + 0.25, tip[1] + 0.25, 0.42), circle(tip[0] + 0.3, tip[1] + 0.3, 0.42))
    out += [base(cl), part(cl, WHITE, shade=hx("d8d6cc"), line=0.45)]
    if tap:
        for ax, ay, bx, by in ((2.9, 4.7, 1.7, 4.7), (4.7, 2.9, 4.7, 1.7), (3.15, 3.15, 2.4, 2.4)):
            out.append(flat(capsule(ax, ay, bx, by, 0.3), OUT))
    return out


def sc_ibeam(fr):
    """I 꼴 스크래쳐(위아래 판 · 노끈 기둥)를 오른쪽에 선 냥이 두 앞발로 번갈아 벅벅 — 한 발이 위에서 아래로 긁는 동안
    다른 발은 떼어 올린다. 긁힌 자리에 흰 자국 두 줄, 보풀이 튄다. 기둥 가운데가 핫스팟"""
    k = kof(fr)
    X = 7.5
    post = rbox(X, 15.5, 1.9, 11.0, 0.5)
    top = rbox(X, 3.3, 5.0, 1.35, 0.7)
    bot = rbox(X, 27.7, 5.0, 1.35, 0.7)

    def rope(x, y):
        return SISAL_D if fmod(y + 0.55 * x + 64.0, 1.7) < 0.5 else SISAL
    out = [base(post, top, bot), part(post, rope, shade=SISAL_D, ink=PLATE_D, line=0.8)]
    for b in (top, bot):
        out.append(part(b, lambda x, y: PLATE, shade=PLATE_D, ink=hx("4a3428"), line=0.8))
    s = 0.66
    F = Frame(19.8, 14.4, s)
    arms, marks = [], []
    for i, sh_ in enumerate(((-4.4, 5.4), (-3.0, 7.4))):
        t = (k / 6 + i / 2) % 1
        if t < 0.66:
            y = 11.6 + 10.0 * t / 0.66
            marks.append(y)
            hx_ = 10.3
        else:
            y = 21.6 - 10.0 * (t - 0.66) / 0.34
            hx_ = 11.6
        arms.append((sh_, F.loc(hx_, y), False))
    for y in marks:                                     # 긁힌 흰 자국 · 보풀
        for x in (X - 0.9, X + 0.9):
            out.append(flat(capsule(x, 11.2, x, y - 0.6, 0.28), SCRATCH, 0.95))
        if k % 2:
            for dx, dy in ((-3.0, -0.6), (-3.8, 0.9)):
                out.append(flat(circle(X + dx, y + dy, 0.5), SISAL_D))
    out += tabby(F, "blink" if k == 9 else "open", turn_=-0.8, look=(-1.0, 0.1), sway=0.5 * sin(TAU * fr), arms=arms)
    return out


def sc_move(fr):
    """납작 엎드려 네 발을 사방으로 쭉 뻗은(위에서 본) 냥 — 등의 가로 줄 · 등줄기가 고등어. 앞발이 헤엄치듯 까딱,
    네 방향 초록 화살촉이 바깥으로 두근"""
    ph = TAU * fr
    k = kof(fr)
    o = 0.6 if k % 6 < 3 else 0.0
    out = []
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        out += gchev(15.5 + dx * (13.6 + o), 15.5 + dy * (13.6 + o), dx, dy, 2.2)
    s = 0.6
    F = Frame(15.5, 8.6, s)
    sw = sin(ph)
    under = []
    tp = [(0.0, 18.8), (0.6 * sw, 23.0), (3.4 + sw, 26.0), (7.2, 25.6 + 1.2 * sw)]
    at, total = along(tp)
    tc = ringed(at, total, max(1.35, 1.05 / s))
    under.append((F.f(chain(tp, 2.2, 1.9)), lambda x, y: tc(at(*F.loc(x, y)))))
    for sg in (-1, 1):
        fl = [(sg * 4.0, 9.8), (sg * 8.0, 9.2 - 0.8 * sg * sw), (sg * 10.6, 9.6 + 1.0 * sg * sw)]
        hl = [(sg * 4.0, 16.6), (sg * 6.6, 19.2), (sg * 7.6, 20.8)]
        for L in (fl, hl):
            under.append((F.f(chain(L, 2.7, 2.4)), FUR))
            under.append((F.f(ell(L[-1][0], L[-1][1], 2.6, 2.3)), FUR_L))
    under.append((F.f(ell(0.0, 13.0, 6.2, 7.4)), COAT.fur("top", F)))
    out += tabby(F, "blink" if k == 8 else "open", body=False, paws=False, tail=False, extra_under=under)
    return out


def _stretch(fr, axis, *a, **kw):
    """catkit 기지개 + 같은 박자의 초록 화살촉(분홍 대신). axis 는 몸 줄이 가로지를 축"""
    COAT.axis = axis
    chev = kw.pop("chev")
    out = stretch(fr, *a, chev=None, **kw)
    o = 0.6 if sin(TAU * fr) > 0.3 else 0.0
    for (x, y, dx, dy) in chev:
        out += gchev(x + dx * o, y + dy * o, dx, dy, 2.2, 1.0 if o else 0.75)
    return out


def sc_we(fr):
    return _stretch(fr, (1.0, 0.0), (15.8, 10.2), 0.0, 13.0, 0.6, chev=[(1.9, 7.5, -1, 0), (29.1, 7.5, 1, 0)],
                    head=(0.0, -1.0), hoff=2.6)


def sc_ns(fr):
    return _stretch(fr, (0.0, 1.0), (8.0, 17.6), pi / 2, 11.0, 0.56, chev=[(7.5, 1.9, 0, -1), (7.5, 29.1, 0, 1)],
                    head=(0.0, -1.0), hoff=3.4, dangle=True)


def sc_nwse(fr):
    r = 0.7071
    return _stretch(fr, (r, r), (14.6, 14.6), pi / 4, 13.0, 0.6, chev=[(3.6, 3.6, -1, -1), (27.4, 27.4, 1, 1)],
                    head=(0.45, -0.9), hoff=1.8)


def sc_nesw(fr):
    r = 0.7071
    return _stretch(fr, (-r, r), (13.6, 14.2), 3 * pi / 4, 13.0, 0.6, chev=[(27.4, 3.6, 1, -1), (3.6, 27.4, -1, 1)],
                    head=(-0.45, -0.9), hoff=1.8)


def sc_no(fr):
    """빨간 금지 표지 안에서 등을 돌리고 앉은 냥(쌩) — 꼬리를 바닥에 탁탁, 장 7–9 에 어깨 너머로 힐끔(초록 눈 하나)"""
    ph = TAU * fr
    k = kof(fr)
    C_ = 15.5
    look = k in (7, 8, 9)
    lash = sin(2 * ph)
    F = Frame(C_, 12.6, 0.62)
    tp = [(3.6, 10.6), (7.8, 11.4), (10.6, 9.8 + 1.4 * lash), (11.2, 7.2 + 3.0 * lash)]
    use(BACK)
    try:
        out = tabby(F, face_on=False, tail_pts=tp, ear_tilt=(0.0, -0.8) if look else (0.0, 0.0))
    finally:
        use(COAT)
    if look:                                            # 어깨 너머 힐끔 — 머리 오른쪽 끝에 초록 눈 · 수염
        ex, ey = F.w(5.0, -0.2)
        out.append(eye(ex, ey, 1.25, *IRIS, look=(1.0, 0.0)) if k != 8 else shut(ex, ey, 1.25, "blink"))
        for j, dy in enumerate((0.6, 2.0)):
            x0, y0 = F.w(7.4, dy)
            out.append(flat(capsule(x0, y0, x0 + 2.4, y0 + (j - 0.5) * 0.8, 0.2), OUT))
    R = 12.5
    sg = union(ring(C_, C_, R - 1.25, 1.25), capsule(C_ - 7.7, C_ - 7.7, C_ + 7.7, C_ + 7.7, 1.35))
    out += [base(sg), part(sg, lambda x, y: lerp(SIGN_L, SIGN, smooth(C_ - 10, C_ - 4, y + 0.5 * x - 0.5 * C_)), shade=SIGN_D,
                           ink=SIGN_D, line=0.8)]
    return out


def sc_pen(fr):
    """연필을 입에 물고 쓰는 엎드린 냥 — 연필심(왼쪽 아래)이 핫스팟. 지나간 자리에 연필 줄이 물결치며 자라고 꼬리가 살랑"""
    ph = TAU * fr
    k = kof(fr)
    s = 0.7
    F = Frame(18.2, 11.2, s)
    sw = sin(ph)
    turn_ = -0.7
    out = []
    for i in range(k + 2):                              # 연필 줄
        x0 = 3.2 + 1.8 * i
        out.append(flat(capsule(x0, 29.9 + 0.5 * sin(x0 * 0.9), x0 + 1.6, 29.9 + 0.5 * sin((x0 + 1.6) * 0.9), 0.48), LEAD))
    tip = (1.0, 28.0)
    mx, my = F.w(turn_ - 0.4, 3.1)                      # 입 — 연필이 여기까지 물려 있다
    ang = atan2(my - tip[1], mx - tip[0])
    ux, uy = cos(ang), sin(ang)
    Lm = hypot(mx - tip[0], my - tip[1])
    L = Lm + 2.4
    w = 1.45
    pen_f = smin(0.3, rpoly([tip, (tip[0] + ux * 3.6 - uy * w, tip[1] + uy * 3.6 + ux * w),
                             (tip[0] + ux * 3.6 + uy * w, tip[1] + uy * 3.6 - ux * w)], 0.18),
                 capsule(tip[0] + ux * 3.4, tip[1] + uy * 3.4, tip[0] + ux * L, tip[1] + uy * L, w))

    def pcol(x, y):
        t = (x - tip[0]) * ux + (y - tip[1]) * uy
        o = (x - tip[0]) * -uy + (y - tip[1]) * ux
        if t < 1.4:
            return LEAD
        if t < 3.6:
            return WOOD
        if t < L - 3.0:
            return PENCIL_D if o > 0.35 else PENCIL
        if t < L - 1.6:
            return FERRULE
        return ERASER
    out += [base(pen_f), part(pen_f, pcol, shade=PENCIL_D, sh=0.0, line=0.8)]
    loaf = F.f(ell(6.8, 6.6, 7.8, 4.2))
    paws = F.f(union(ell(-2.2, 8.8, 2.2, 1.5), ell(2.8, 9.2, 2.2, 1.5)))
    tp = [(13.2, 4.6), (14.4, 0.6), (13.2 + 1.4 * sw, -3.2)]
    out += tabby(F, "blink" if k == 4 else "open", turn_=turn_, look=(-0.8, 0.8), body=False, paws=False, tail_pts=tp,
                 extra_under=[(loaf, COAT.fur("loaf", F)), (paws, FUR_L)])
    front = inter(pen_f, lambda x, y: (x - tip[0]) * ux + (y - tip[1]) * uy - Lm)   # 입 앞까지만 얼굴 위로
    out += [base(front), part(front, pcol, shade=PENCIL_D, sh=0.0, line=0.8)]
    return out


def sc_up(fr):
    """뒷발로 서서 한 앞발을 머리 위로 쭉(저요!) — 발끝(맨 위)이 핫스팟이라 그 발은 그대로, 눈은 위를 보고
    다른 앞발이 가슴 앞에서 까딱, 꼬리가 살랑"""
    ph = TAU * fr
    k = kof(fr)
    s = 0.76
    hand = (9.0, -11.6)
    F = Frame(14.5 - hand[0] * s, 3.35 - hand[1] * s, s)
    sw = sin(ph)
    tp = [(3.6, 10.4), (7.8, 10.8), (10.4, 9.0), (11.2 + 0.8 * sw, 6.4), (10.6 + 1.2 * sw, 4.6)]
    tuck = (-1.6, 7.6 - 0.8 * max(0.0, sw))
    return tabby(F, "blink" if k == 5 else "open", look=(0.35, -0.9), tail_pts=tp, ear_tilt=(0.0, -1.2),
                 turn_=-0.3, arms=[((-2.8, 5.0), tuck, False), ((7.0, 4.4), hand, True)])


SCENE = {"busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "wait": sc_wait,
         "hand": sc_hand, "cross": sc_cross, "ibeam": sc_ibeam, "move": sc_move, "no": sc_no, "pen": sc_pen,
         "up": sc_up, "we": sc_we, "ns": sc_ns, "nwse": sc_nwse, "nesw": sc_nesw}


class MackerelCat(Pet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = MackerelCat(COAT, SCENE, HOT)


def scene(name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
    return PET.cell(name, frame, soft_, tip_body, shape)


register("mackerelcat", PET)

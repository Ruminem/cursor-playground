# SPDX-License-Identifier: Apache-2.0
"""아기 공룡 · 애니 — 10종 × 17칸을 art/<마리>anim/<칸>.txt 로 쓴다.

  python gen/dino.py [마리...] [--cells 칸,칸]   (안 주면 10종 전부 · 17칸 전부, 마리마다 프로세스 하나)

arrow · wait · no 는 처음 그림 그대로고, 나머지 14칸은 `SCENES` 가 칸마다 장면을 따로 그린다
(작은 화살표 공룡 + 소품, 기지개 넷은 화면 축으로 늘이는 `SRig`). 화살표 · 핫스팟은 늘 맨 위에 칠한다.

티라노·프테라 말고 여덟은 티라노 치비 틀(머리 크기·몸 비율·눈)을 같이 쓰는 baby() 하나로 빚고
마리마다 큰 표식 하나만 얹는다. 냥이 애니(gen/cheesecat.py)와 같은 틀: 부위(타원 · 막대 · 세모)를 공룡 제 좌표 (u 앞쪽, w 아래)에 놓고
화면으로 돌려 찍는다(`Rig`, `draw`). cheesecat 의 draw 는 제 OUT 을 쓰므로 가져오지 않고 여기 따로 둔다.
Rig 에는 좌우 뒤집기(fx)를 더했다 — 같은 몸을 왼쪽을 보게도 그린다.
테두리는 짙은 자주 갈색, 반투명 테는 한 묶음이 한 벌로 보이게 열 다 크림 하나다.
"""
import math
import sys

import sea  # noqa: E402
import shape  # noqa: E402
from sea import (N, PEEK_CUR, PEEK_S, PEEK_WHITE, RATE, SIGN, SIGN_D, disc, finish, hx, ink,  # noqa: E402
                 inside, peek, phases, raster, solid)

ART = sea.WIN / "art"

OUT, EYE, HI = hx("3a2a30ff"), hx("2a1c22ff"), hx("ffffffff")
RIM = hx("f6e9d2c7")
ink(OUT, HI, RIM)
BLUSH, MOUTH, TOOTH = hx("f4a0b0ff"), hx("d8607aff"), hx("ffffffff")
LEAF, LEAF_D, STEM = hx("8fd16aff"), hx("5ea84aff"), hx("a07850ff")
SWEAT = hx("9fd4f4ff")
FISH, FISH_D = hx("9cb6ccff"), hx("6a879fff")
DUST = hx("e6d6bcff")
SPARK = hx("fff3a0ff")

# 마리마다 색: 몸 · 짙은(무늬) · 배 · 덧(뿔 · 판 · 돛 …)
C = {
    "trex": (hx("8fd17aff"), hx("5fa35aff"), hx("eef4c4ff"), hx("ffffffff")),
    "triceratops": (hx("f4a65aff"), hx("d9803cff"), hx("fde3b4ff"), hx("f7d36aff")),
    "stego": (hx("b8e08aff"), hx("86b860ff"), hx("eaf6cfff"), hx("4fb3a8ff")),
    "brachio": (hx("9fd0f0ff"), hx("6fa8d6ff"), hx("e4f3fcff"), hx("c7e6f8ff")),
    "ptera": (hx("f6a8c8ff"), hx("d97ea6ff"), hx("fde0eaff"), hx("b892e6ff")),
    "ankylo": (hx("dcc092ff"), hx("a8794eff"), hx("f3e4c4ff"), hx("f6ead0ff")),
    "pachy": (hx("c9b2eeff"), hx("9f86ccff"), hx("eee4fcff"), hx("ece2ffff")),
    "raptor": (hx("f6d65aff"), hx("c9902eff"), hx("fcefb8ff"), hx("f08a4aff")),
    "spino": (hx("f7c4a0ff"), hx("dc9a70ff"), hx("fde8d6ff"), hx("e8604cff")),
    "egg": (hx("a8e6cfff"), hx("6fc4a8ff"), hx("e2f8eeff"), hx("fff6e2ff")),
}
CREAM_HORN = hx("fff3d6ff")
TEAL_D = hx("2f8f86ff")
SAIL_O = hx("f39a4aff")
PURPLE_D = hx("8a62c4ff")
BEAK = hx("f6d58aff")
DOME = hx("9a7ed2ff")
EGG_SPOT = hx("7fcab4ff")


SHIFT = 0.0   # 그리는 판 전체를 옆으로 옮기는 칸 — run() 이 화살표 칸만 ARROW_FIT 값으로 켠다


# ── 그리개 (cheesecat 에서 복사 · 좌우 뒤집기 fx 를 더함) ───────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도, 시계 방향) · 배율 k · fx=-1 이면 좌우 뒤집기(왼쪽을 본다)"""

    def __init__(self, ox, oy, ang=0.0, k=1.0, fx=1):
        t = math.radians(ang)
        self.ox, self.oy, self.c, self.s, self.k, self.fx = ox + SHIFT, oy, math.cos(t), math.sin(t), k, fx

    @classmethod
    def at(cls, loc, scr, ang=0.0, k=1.0, fx=1):
        """제 좌표 loc 가 화면 scr 에 오게"""
        r = cls(0.0, 0.0, ang, k, fx)
        x, y = r.world(*loc)
        return cls(scr[0] - x, scr[1] - y, ang, k, fx)

    def world(self, a, b):
        a *= self.fx
        return self.ox + (a * self.c - b * self.s) * self.k, self.oy + (a * self.s + b * self.c) * self.k

    def local(self, x, y):
        dx, dy = (x - self.ox) / self.k, (y - self.oy) / self.k
        return (dx * self.c + dy * self.s) * self.fx, -dx * self.s + dy * self.c

    def cell(self, a, b):
        x, y = self.world(a, b)
        return math.floor(x), math.floor(y)


def ell(ca, cb, ra, rb, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)

    def hit(a, b):
        da, db = a - ca, b - cb
        u, v = da * c + db * s, -da * s + db * c
        return (u / ra) ** 2 + (v / rb) ** 2 <= 1
    return hit


def bar(p0, p1, r0, r1=None):
    r1 = r0 if r1 is None else r1
    ex, ey = p1[0] - p0[0], p1[1] - p0[1]
    ll = ex * ex + ey * ey or 1e-9

    def hit(a, b):
        t = max(0.0, min(1.0, ((a - p0[0]) * ex + (b - p0[1]) * ey) / ll))
        px, py = p0[0] + ex * t, p0[1] + ey * t
        return (a - px) ** 2 + (b - py) ** 2 <= (r0 + (r1 - r0) * t) ** 2
    return hit


def chain(pts, r0, r1=None):
    r1 = r0 if r1 is None else r1
    n = len(pts) - 1
    return any_of(*[bar(pts[i], pts[i + 1], r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n) for i in range(n)])


def tri(*pts):
    pl = list(pts)
    return lambda a, b: inside(pl, a, b)


def any_of(*hs):
    return lambda a, b: any(h(a, b) for h in hs)


def but(h, cut):
    return lambda a, b: h(a, b) and not cut(a, b)


def rp(p, piv, deg):
    """점 p 를 piv 둘레로 deg 만큼 돌린 자리(제 좌표)"""
    if not deg:
        return p
    t = math.radians(deg)
    da, db = p[0] - piv[0], p[1] - piv[1]
    return piv[0] + da * math.cos(t) - db * math.sin(t), piv[1] + da * math.sin(t) + db * math.cos(t)


def turn(parts, piv, deg):
    """부위들을 piv 둘레로 deg 만큼 돌린다 — 고개 까딱 · 갸웃"""
    if not deg:
        return parts
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)

    def back(f):
        def g(a, b):
            da, db = a - piv[0], b - piv[1]
            return f(piv[0] + da * c + db * s, piv[1] - da * s + db * c)
        return g
    return [(n, back(h), back(col) if callable(col) else col, ln) for n, h, col, ln in parts]


def draw(rig, parts):
    """parts: [(이름, 맞음, 색, 테두리)] — 앞의 것이 위. cheesecat.draw 와 같다(OUT 만 여기 것)"""
    order = {p[0]: i for i, p in enumerate(parts)}
    region, mask = {}, set()
    for y in range(-3, 35):
        for x in range(-3, 35):
            hits = {}
            for j in range(4):
                for i in range(4):
                    a, b = rig.local(x + (i + 0.5) / 4, y + (j + 0.5) / 4)
                    for name, hit, _, _ in parts:
                        if hit(a, b):
                            hits[name] = hits.get(name, 0) + 1
                            break
            if sum(hits.values()) >= 8:
                mask.add((x, y))
                region[x, y] = max(hits, key=lambda n: (hits[n], -order[n]))
    col = {p[0]: p[2] for p in parts}
    lined = {p[0] for p in parts if p[3]}
    out = {}
    for p in mask:
        c = col[region[p]]
        out[p] = c(*rig.local(p[0] + 0.5, p[1] + 0.5)) if callable(c) else c
        x, y = p
        nb = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        if any(q not in mask for q in nb):
            out[p] = OUT
        elif region[p] in lined and any(order[region[q]] > order[region[p]] for q in nb):
            out[p] = OUT
    return out, mask, region


def dot(f, p, c):
    f[p] = c


def eye(f, rig, u, w, mood="open"):
    """눈 하나: 크게(2×2, 흰 반짝) / 작게(rig.k < 0.62 면 1×2). mood: open · blink · happy · squeeze · sulk · angry"""
    ex, ey = rig.world(u, w)
    if rig.k < 0.62:
        x0, y0 = math.floor(ex), math.floor(ey - 0.5)
        if mood == "open" or mood == "angry":
            f[x0, y0] = EYE
            f[x0, y0 + 1] = EYE
        elif mood == "squeeze":
            f[x0, y0] = EYE
            f[x0 + 1, y0 + 1] = EYE
        else:
            f[x0, y0 + 1] = EYE
        return
    x0, y0 = round(ex - 1), round(ey - 1)
    if mood in ("open", "angry"):
        for dx in (0, 1):
            for dy in (0, 1):
                f[x0 + dx, y0 + dy] = EYE
        f[x0, y0] = HI
        if mood == "angry":   # 눈썹 — 앞쪽으로 내려 긋는다
            fx = rig.fx
            f[x0 + (0 if fx > 0 else 1), y0 - 2] = OUT
            f[x0 + (1 if fx > 0 else 0), y0 - 1] = OUT
    elif mood == "blink":
        f[x0, y0 + 1] = EYE
        f[x0 + 1, y0 + 1] = EYE
    elif mood == "happy":
        f[x0 - 1, y0 + 1] = EYE
        f[x0, y0] = EYE
        f[x0 + 1, y0] = EYE
        f[x0 + 2, y0 + 1] = EYE
    elif mood == "squeeze":   # > 또는 <
        fx = rig.fx
        xa, xb = (x0, x0 + 1) if fx > 0 else (x0 + 1, x0)
        f[xa, y0 - 1] = EYE
        f[xb, y0] = EYE
        f[xa, y0 + 1] = EYE
    elif mood == "sulk":
        f[x0, y0 + 1] = EYE
        f[x0 + 1, y0 + 1] = EYE
        f[x0 + (1 if rig.fx > 0 else 0), y0] = EYE


def blush(f, rig, u, w):
    x, y = rig.world(u, w)
    f[math.floor(x), math.floor(y)] = BLUSH
    if rig.k >= 0.62:
        f[math.floor(x) - rig.fx, math.floor(y)] = BLUSH


def seg(f, rig, p0, p1, col, only=None):
    """제 좌표 p0 → p1 한 칸 굵기 선. only 가 있으면 그 칸 집합 안에만"""
    a, b = rig.world(*p0), rig.world(*p1)
    n = max(1, math.ceil(math.hypot(b[0] - a[0], b[1] - a[1]) * 2))
    for i in range(n + 1):
        p = (math.floor(a[0] + (b[0] - a[0]) * i / n), math.floor(a[1] + (b[1] - a[1]) * i / n))
        if only is None or p in only:
            f[p] = col


def spots(pts, r, col, base):
    """몸 색 함수: 점 무늬 pts 안이면 col, 아니면 base(a, b) 또는 base"""
    def g(a, b):
        for (pa, pb) in pts:
            if (a - pa) ** 2 + (b - pb) ** 2 <= r * r:
                return col
        return base(a, b) if callable(base) else base
    return g


def legs4(sp, front=4.5, back=-4.5, top=4.0, bot=8.8, r=1.9, step=0.0, far_dx=1.6):
    """네 발 짐승의 짧은 다리 넷 — 앞 둘(가까운 것 · 먼 것) · 뒤 둘. 먼 다리는 짙게, 뒤에 그린다"""
    body, dark, _, _ = C[sp]
    near = ("legs", any_of(bar((front, top), (front + step, bot), r), bar((back, top), (back - step, bot), r)), body, True)
    far = ("legsfar", any_of(bar((front + far_dx, top), (front + far_dx - step, bot - 0.4), r * 0.9),
                             bar((back + far_dx, top), (back + far_dx + step, bot - 0.4), r * 0.9)), dark, False)
    return near, far


# ── 몸 10종: (부위들, 꾸밈(f, rig, mood)) 를 돌려준다. 오른쪽(+u)을 본다 ───────────
TAIL_UP = 0.0   # 꼬리를 치켜드는 각(도) — run() 이 화살표 칸만 ARROW_FIT 값으로 켠다


def trex(m=0.0, arm=0.0, arm_far=None, tail=0.0, nod=0.0, step=0.0, lean=0.0):
    """큰 머리 · 이빨 둘 · 아주 짧은 팔 · 굵은 꼬리. arm 은 팔 끝이 위로 든 정도(칸, + 가 위)"""
    B, D, L, T = C["trex"]
    piv = (1.0, -2.0)
    hd_spots = [(0.0, -10.4), (-2.2, -8.6), (-3.2, -6.2)]
    hcol = spots(hd_spots, 0.9, D, lambda a, b: L if b > -4.0 and a > 1.0 else B)
    head = [("head", any_of(ell(1.6, -7.0, 5.8, 5.2), ell(6.2, -5.6, 4.6, 3.2)), hcol, True)]
    if m > 0:
        head.insert(0, ("mouth", tri((3.6, -4.3), (11.4, -5.0), (11.4, -4.6 + 3.4 * m)), MOUTH, True))
    head = turn(head, piv, nod)
    arm_far = arm if arm_far is None else arm_far
    a_near = ("arm", chain([(2.8, 0.2), (5.0, 0.4 - arm)], 1.15), B, True)
    a_far = ("armfar", chain([(3.6, -0.4), (5.6, -0.2 - arm_far)], 1.0), D, False)
    bcol = spots([(-3.6, -0.6), (-1.0, -2.0), (-5.2, 2.2)], 0.8, D,
                 lambda a, b: L if a > 0.4 and b > -1.0 else B)
    body = ("body", ell(-1.2 - lean, 2.4, 5.6, 5.4), bcol, False)
    legn = ("leg", any_of(ell(-0.6, 5.0, 3.0, 3.0), ell(1.2 + step, 8.6, 3.0, 1.3)), B, True)
    legf = ("legfar", ell(-3.0 - step, 8.6, 2.6, 1.2), D, False)
    tl = ("tail", chain([(-5.2, 3.6), (-9.6, 4.0), (-13.4, 2.0 + tail)], 2.8, 0.9), B, False)
    if TAIL_UP:   # baby() 와 같은 꼬리 치켜들기 — 티렉스는 baby 를 안 거친다
        h = tl[1]
        tl = (tl[0], lambda a, b: h(*rp((a, b), (-5.2, 3.6), TAIL_UP)), tl[2], tl[3])
    parts = [a_near] + head + [legn, body, a_far, legf, tl]

    def deco(f, rig, mood="open"):
        e = rp((3.6, -8.0), piv, nod)
        eye(f, rig, *e, mood)
        blush(f, rig, *rp((4.4, -5.6), piv, nod))
        n = rp((10.0, -6.6), piv, nod)
        f[rig.cell(*n)] = OUT
        if m <= 0:   # 다문 입 + 송곳니 둘
            seg(f, rig, rp((5.2, -4.2), piv, nod), rp((10.6, -4.6), piv, nod), OUT)
            for u in (7.0, 9.6):
                f[rig.cell(*rp((u, -3.5), piv, nod))] = TOOTH
        else:
            for u in (6.0, 8.4, 10.4):
                f[rig.cell(*rp((u, -4.3 - 0.06 * (u - 4)), piv, nod))] = TOOTH
    return parts, deco


# ── 치비 틀 — 여덟 마리가 trex() 의 비율을 같이 쓴다 ─────────────────────────────
# 처음엔 종마다 실제 공룡 비율(낮고 긴 몸 · 긴 목 · 가는 몸)로 그렸더니 32칸 안에서 머리가 손톱만 하고
# 눈이 점 하나라 "티라노·프테라 말고는 안 귀엽다" 는 판정이었다. 머리 크기 · 몸 비율 · 눈을 티라노 것으로 맞추고
# 종마다 알아볼 표식 하나만 크게 남긴다(뿔+프릴 · 등판 · 곤봉 · 든 머리 · 돛 · 발톱+볏 · 돔 · 알 모자).
def shift(parts, du, dw):
    """부위들을 제 좌표에서 (du, dw) 만큼 옮긴다"""
    if not du and not dw:
        return parts

    def mv(f):
        return lambda a, b: f(a - du, b - dw)
    return [(n, mv(h), mv(col) if callable(col) else col, ln) for n, h, col, ln in parts]


def baby(sp, m=0.0, arm=0.0, arm_far=None, tail=0.0, nod=0.0, step=0.0, lean=0.0, quad=False, raise_=0.0,
         snout=(5.8, -5.4, 4.2, 3.2), hcol=None, bcol=None, head_extra=(), front=(), behind=(), back=(), tail_end=(),
         tail_pts=None, tail_r=(2.8, 0.9), teeth=0, smile=True, more=None):
    """티라노 틀 치비 몸 — 머리 ell(1.6,-7,5.8,5.2) · 몸 ell(-1.2,2.4,5.6,5.4) · 눈 (3.6,-8) 이 trex() 와 같다.
    quad 면 짧은 팔 대신 통통한 앞다리 둘로 땅을 짚는다(arm 은 가까운 앞발을 든 정도).
    raise_ 는 머리를 그만큼 위로 든다(브라키오). front 는 머리 앞 · behind 는 머리 뒤 몸 앞(둘 다 머리와 같이 까딱),
    back 은 몸 뒤(몸 속은 잘라 몸과의 경계에 테가 생기게), tail_end 는 꼬리 앞(곤봉 · 가시)"""
    B, D, L, A = C[sp]
    # 머리 덧(front · behind · head_extra · snout)은 전부 티라노 머리 자리 기준으로 받아 (hdu, hdw) 만큼 옮긴다.
    # 네 발이면 몸을 가로로 눕히고 머리를 앞 아래로 내려 몸 앞쪽에 겹친다 — 처음엔 티라노처럼 머리를 몸 위에 쌓았더니
    # 앞다리가 턱 밑 기둥이 되어 앉은 개처럼 읽혔다
    hdu, hdw = (2.8, 3.2 - raise_) if quad else (0.0, -raise_)
    hu, hw = 1.6, -7.0
    piv = (1.0 + hdu, -2.0 + hdw * 0.4 + (1.6 if quad else 0.0))
    sn = snout
    tip = sn[0] + sn[2]
    if hcol is None:
        jaw = sn[1] + 1.4

        def hcol(a, b):
            return L if b > jaw and a > 1.0 else B
    head = [("head", any_of(ell(hu, hw, 5.8, 5.2), ell(*sn), *head_extra), hcol, True)]
    mw = sn[1] + 1.3
    if m > 0:
        head.insert(0, ("mouth", tri((3.6, mw), (tip + 0.6, mw - 0.7), (tip + 0.6, mw - 0.3 + 3.2 * m)), MOUTH, True))
    head = turn(shift(list(front) + head + list(behind), hdu, hdw), piv, nod)
    arm_far = arm if arm_far is None else arm_far
    if quad:
        bc = (QB[0] - lean, QB[1], QB[2], QB[3])
        # 다리는 테를 안 둘러 배에 묻히게 한다 — 테를 두르면 다리 줄이 배 한가운데까지 올라와 길쭉한 탁자 다리로 읽혔다
        lim = [("arm", any_of(bar((3.0, 5.4), (3.2 + 0.5 * step, 8.2 - arm), 1.8), ell(3.6 + 0.5 * step, 8.7 - arm, 2.2, 1.2)), B, arm > 0.5)]
        lim_f = [("armfar", any_of(bar((5.0, 3.0), (5.0 - 0.5 * step, 8.0), 1.6), ell(5.6 - 0.5 * step, 8.6, 1.9, 1.0)), D, False)]
        legn = ("leg", any_of(ell(-5.4, 6.0, 2.6, 2.4), ell(-4.8 + step, 8.6, 2.6, 1.3)), B, False)
        legf = ("legfar", any_of(bar((-3.2, 5.0), (-3.0 - step, 8.2), 1.6), ell(-2.8 - step, 8.6, 1.9, 1.0)), D, False)
        tp0 = [(-7.4, 3.6), (-11.0, 3.8), (-14.4, 1.8 + tail)]
    else:
        bc = (-1.2 - lean, 2.4, 5.6, 5.4)
        lim = [("arm", chain([(2.8, 0.2), (5.0, 0.4 - arm)], 1.15), B, True)]
        lim_f = [("armfar", chain([(3.6, -0.4), (5.6, -0.2 - arm_far)], 1.0), D, False)]
        legn = ("leg", any_of(ell(-0.6, 5.0, 3.0, 3.0), ell(1.2 + step, 8.6, 3.0, 1.3)), B, True)
        legf = ("legfar", ell(-3.0 - step, 8.6, 2.6, 1.2), D, False)
        tp0 = [(-5.2, 3.6), (-9.6, 4.0), (-13.4, 2.0 + tail)]
    if bcol is None and quad:
        def bcol(a, b):
            return L if b > 6.0 and a > -6.0 else B
    elif bcol is None:
        def bcol(a, b):
            return L if a > 0.4 and b > -1.0 else B
    body = ("body", ell(*bc), bcol, False)
    core = ell(bc[0], bc[1], bc[2] - 0.9, bc[3] - 0.9)
    backs = [(n, but(h, core), col, ln) for n, h, col, ln in back]
    tl = ("tail", chain(tail_pts or tp0, *tail_r), B, False)
    if TAIL_UP:   # 꼬리째(끝 곤봉 · 가시 포함) 뿌리 둘레로 치켜든다 — 화살표 칸에서 꼬리 끝이 판 밖으로 안 나가게
        root = (tail_pts or tp0)[0]

        def up(h):
            return (lambda a, b: h(*rp((a, b), root, TAIL_UP))) if callable(h) else h
        tl = (tl[0], up(tl[1]), tl[2], tl[3])
        tail_end = [(n, up(h), up(col), ln) for n, h, col, ln in tail_end]
    parts = lim + head + [legn, body] + backs + lim_f + [legf] + list(tail_end) + [tl]

    def deco(f, rig, mood="open"):
        def R(p):
            return rp((p[0] + hdu, p[1] + hdw), piv, nod)
        eye(f, rig, *R((3.6, -8.0)), mood)
        blush(f, rig, *R((4.4, -5.6)))
        f[rig.cell(*R((tip - 0.9, sn[1] - 1.0)))] = OUT
        if m <= 0:
            seg(f, rig, R((5.6, mw)), R((tip - 0.5, mw - 0.3)), OUT)
            if smile:   # 입꼬리 — 뒤쪽 끝을 한 칸 올린다
                f[rig.cell(*R((5.0, mw - 0.9)))] = OUT
            for i in range(teeth):
                f[rig.cell(*R((tip - 1.6 - 2.4 * i, mw + 0.8)))] = TOOTH
        else:
            for i in range(teeth):
                f[rig.cell(*R((tip - 1.0 - 2.4 * i, mw - 0.3)))] = TOOTH
        if more:
            more(f, rig, R)
    return parts, deco


QB = (-2.2, 3.6, 6.8, 5.0)
ARMOR, ARMOR_D = hx("bc8c5aff"), hx("8a6040ff")   # 안킬로 갑옷 비늘 · 이음매   # 네 발 몸 타원 — baby(quad=True) 의 bc 와 같다


def on_back(phi):
    """네 발 몸 타원 위 각 phi(도, 90 이 꼭대기 · 180 이 엉덩이) 자리와 바깥 법선"""
    t = math.radians(phi)
    u, w = QB[0] + QB[2] * math.cos(t), QB[1] - QB[3] * math.sin(t)
    nx, ny = math.cos(t) / QB[2], -math.sin(t) / QB[3]
    ln = math.hypot(nx, ny)
    return (u, w), (nx / ln, ny / ln)


def blade(p, n, h, hw, sink=1.4):
    """바닥 p · 법선 n 으로 솟는 오각 판(끝이 둥글게 뾰족)"""
    e = (-n[1], n[0])

    def at(s, q):
        return (p[0] + e[0] * s + n[0] * q, p[1] + e[1] * s + n[1] * q)
    return tri(at(-hw, -sink), at(-hw * 1.15, h * 0.45), at(0, h), at(hw * 1.15, h * 0.45), at(hw, -sink))


def triceratops(m=0.0, tail=0.0, nod=0.0, step=0.0, arm=0.0, lean=0.0):
    """표식: 뿔 셋(이마 둘은 길게 앞으로 · 코 하나) + 머리 뒤 큰 프릴(주황 테 · 크림 혹 테두리). 부리는 짙은 주황, 네 발.
    처음엔 프릴을 노랑 한 색 동그라미로 했더니 금발 머리로 읽혀서 테와 혹을 둘렀다"""
    B, D, L, A = C["triceratops"]
    fc, fr = (-2.4, -8.2), 6.4
    dots = [(fc[0] + fr * 0.86 * math.cos(math.radians(a)), fc[1] - fr * 0.86 * math.sin(math.radians(a)))
            for a in (95, 135, 175)]

    def frill_col(a, b):
        if any((a - x) ** 2 + (b - y) ** 2 < 0.8 for x, y in dots):
            return CREAM_HORN
        r = math.hypot(a - fc[0], b - fc[1]) / fr
        return A if r > 0.8 else D

    def hcol(a, b):
        if a > 8.4 and b > -6.4:
            return D
        return L if b > -4.0 and a > 1.0 else B
    # 이마 뿔은 굵은 마디로 — 세모로 그리면 머리 밖으로 나온 끝만 남아 더듬이처럼 가늘었다
    front = [("horn", any_of(chain([(2.6, -11.4), (5.4, -14.6), (9.0, -16.4)], 1.8, 0.5),
                             tri((7.2, -7.8), (9.0, -10.8), (9.8, -7.2))), CREAM_HORN, True)]
    behind = [("hornfar", chain([(0.2, -11.8), (2.4, -15.6), (5.6, -18.0)], 1.7, 0.5), hx("e8d8b8ff"), True),
              ("frill", ell(fc[0], fc[1], fr, fr), frill_col, True)]
    return baby("triceratops", m=m, tail=tail, nod=nod, step=step, arm=arm, lean=lean, quad=True,
                hcol=hcol, front=front, behind=behind)


STEGO_PLATES = ((88, 6.8, 2.2), (116, 7.2, 2.3), (144, 6.0, 2.0), (168, 4.4, 1.6))


def stego_tip(i):
    p, n = on_back(STEGO_PLATES[i][0])
    h = STEGO_PLATES[i][1]
    return p[0] + n[0] * h, p[1] + n[1] * h


def stego(plate=(), tail=0.0, nod=0.0, step=0.0, arm=0.0, m=0.0):
    """표식: 등에 큰 오각 판 넷(목덜미에서 엉덩이로 작아짐) + 꼬리 끝 가시 둘. plate 는 반짝이는 판 번호들"""
    B, D, L, A = C["stego"]
    back = []
    for i, (phi, h, hw) in enumerate(STEGO_PLATES):
        p, n = on_back(phi)
        back.append((f"plate{i}", blade(p, n, h, hw), SPARK if i in plate else A, True))
    tp = [(-7.6, 3.8), (-11.0, 3.6), (-13.8, 1.8 + tail)]
    te = tp[-1]
    spikes = ("spikes", any_of(tri((te[0] + 1.4, te[1] + 0.2), (te[0] + 0.4, te[1] - 4.0), (te[0] - 0.2, te[1] + 0.4)),
                               tri((te[0] - 0.2, te[1] + 0.6), (te[0] - 3.0, te[1] - 2.6), (te[0] - 0.8, te[1] - 0.4))),
              CREAM_HORN, True)
    return baby("stego", m=m, tail=tail, nod=nod, step=step, arm=arm, quad=True, back=back, tail_end=[spikes],
                tail_pts=tp, tail_r=(2.6, 1.0))


def brachio(nod=0.0, tail=0.0, step=0.0, arm=0.0, m=0.0, up=0.0):
    """표식: 짧은 목 위로 머리를 쳐든 모양 + 이마 혹 + 등 점무늬, 네 발. up 은 목을 더 늘인 정도(칸)"""
    B, D, L, A = C["brachio"]
    r = 4.4 + up
    hdw = 3.2 - r                       # baby() 가 머리를 옮기는 만큼 — 목 밑동은 몸에 붙어 있게 거꾸로 뺀다
    neck = ("neck", bar((1.4 - 2.8, 0.2 - hdw), (1.0, -3.4), 2.8), B, False)
    crest = ell(2.4, -11.4, 2.4, 1.7)
    bcol = spots([(-5.4, 0.8), (-2.6, -0.4), (-6.8, 3.6), (-0.4, 1.2)], 0.95, D,
                 lambda a, b: L if a > 1.4 and b > 3.0 else B)
    tp = [(-7.6, 3.4), (-11.4, 2.8), (-15.0, 0.2 + tail)]
    return baby("brachio", m=m, tail=tail, nod=nod - 8, step=step, arm=arm, quad=True, raise_=r,
                snout=(5.6, -5.6, 3.8, 3.0), head_extra=(crest,), behind=[neck], bcol=bcol, tail_pts=tp,
                tail_r=(2.6, 0.8))


def ankylo(tail=0.0, club=0.0, nod=0.0, step=0.0, arm=0.0, m=0.0):
    """표식: 꼬리 곤봉(크게 · 짙은 갈색) + 등 갑옷(짙은 판에 크림 혹) · 크림 가시 줄, 네 발. club 은 곤봉을 든 높이"""
    B, D, L, A = C["ankylo"]

    def armor(a, b):   # 등은 짙은 갑옷 비늘(이음매 짙게) — 크림 점으로 했더니 아기 사슴 무늬로 읽혔다
        if b > 4.6:
            return L if a > -2 and b > 6.0 else B
        gu, gw = (a + 20 + 1.4 * ((b + 20) // 2.6 % 2)) % 2.8, (b + 20) % 2.6
        if gu < 0.7 or gw < 0.7:
            return ARMOR_D
        return ARMOR
    spikes = []
    for phi in (92, 118, 144, 168):
        p, n = on_back(phi)
        spikes.append(tri((p[0] - n[1] * 1.8, p[1] + n[0] * 1.8), (p[0] + n[0] * 4.2, p[1] + n[1] * 4.2),
                          (p[0] + n[1] * 1.8, p[1] - n[0] * 1.8)))
    for u in (-6.4, -2.4):   # 옆구리 가시
        spikes.append(tri((u - 1.1, 4.4), (u - 0.4, 8.0), (u + 1.1, 4.4)))
    back = [("spikes", any_of(*spikes), A, True)]
    behind = [("cheek", tri((-3.0, -4.2), (-6.4, -3.8), (-3.2, -6.4)), A, True)]
    tp = [(-7.6, 4.0), (-10.4, 4.0), (-12.2, 2.4 + tail - club * 0.6)]
    cu, cw = -13.6, 1.8 + tail - club

    def club_col(a, b):
        return ARMOR if (a - cu - 0.4) ** 2 + (b - cw + 0.6) ** 2 < 1.6 else D
    cl = ("club", any_of(ell(cu, cw, 3.0, 2.6), ell(cu - 1.6, cw + 0.4, 2.2, 2.0)), club_col, True)
    return baby("ankylo", m=m, tail=tail, nod=nod, step=step, arm=arm, quad=True, bcol=armor, back=back, behind=behind,
                tail_end=[cl], tail_pts=tp, tail_r=(2.4, 1.2), snout=(5.6, -5.2, 3.8, 3.2),
                hcol=lambda a, b: armor(a, b - 1.0) if b < -9.4 + 0.3 * (a - 1.6) else L if b > -4.0 and a > 1.0 else B)


def pachy(nod=0.0, tail=0.0, step=0.0, arm=0.0, lean=0.0, m=0.0):
    """표식: 짙은 보라 두꺼운 돔 머리 + 뒤통수 크림 혹 줄. 두 발(티라노와 같은 자세)"""
    B, D, L, A = C["pachy"]
    hu, hw = 1.6, -7.0

    def hcol(a, b):
        if b < hw - 1.4 + 0.30 * (a - hu):   # 돔 — 앞 위에 반짝 한 점
            return A if (a - 3.6) ** 2 + (b + 12.6) ** 2 < 1.0 else DOME
        return L if b > -4.0 and a > 1.0 else B
    knobs = []
    for ang in (158, 188, 218):
        t = math.radians(ang)
        knobs.append(ell(hu + 5.8 * math.cos(t), hw - 1.4 - 5.8 * math.sin(t) * 0.9, 1.5, 1.5))
    front = [("knob", any_of(*knobs), CREAM_HORN, True)]
    dome = ell(1.4, -9.4, 5.6, 5.2)
    return baby("pachy", m=m, arm=arm, tail=tail, nod=nod, step=step, lean=lean, hcol=hcol, head_extra=(dome,), front=front)


def raptor(nod=0.0, m=0.0, tail=0.0, step=0.0, arm=0.0, crest=0.0):
    """표식: 뒷발의 큰 낫 발톱(크림) + 뒤통수 깃털 볏 셋(주황) · 등 줄무늬, 두 발. 이빨 하나"""
    B, D, L, A = C["raptor"]

    def striped(a, b):
        if a > 0.4 and b > -1.0:
            return L
        return D if (a + 20) % 2.8 < 0.9 else B
    c = crest
    behind = [("crest", any_of(tri((-1.0, -11.6), (-6.0 - c, -15.0 - c), (-3.2, -9.6)),
                               tri((-3.0, -10.0), (-8.4 - c, -11.2 - c * 0.6), (-4.0, -7.4)),
                               tri((-3.8, -7.8), (-8.0 - c, -6.4 - c * 0.3), (-4.0, -5.4))), A, True)]
    s = step
    # 낫 발톱은 흰색으로 발 앞에 크게 — 크림으로 배 앞에 겹쳤더니 연노랑 배에 묻혀 안 보였다
    claw = ("claw", chain([(2.8 + s, 8.2), (4.4 + s, 6.0), (6.4 + s, 5.2), (7.4 + s, 6.4)], 1.3, 0.5), HI, True)
    return _with_front(baby("raptor", m=m, arm=arm, tail=tail, nod=nod, step=step, snout=(6.4, -5.8, 4.6, 2.8),
                            bcol=striped, behind=behind, teeth=1, smile=False), [claw])


def _with_front(pd, extra):
    """baby() 결과 맨 앞에 부위를 더한다(머리와 같이 안 까딱 — 발톱처럼 발에 붙은 것)"""
    parts, deco = pd
    return list(extra) + parts, deco


def spino(nod=0.0, m=0.0, tail=0.0, step=0.0, sail=0.0, flush=False, arm=0.0):
    """표식: 등의 큰 돛(빨강 + 주황 살) — 머리 뒤로 솟는다. 주둥이는 조금 길게, 이빨 둘, 두 발"""
    B, D, L, A = C["spino"]

    def sail_col(a, b):
        if flush:
            return A if (a + 20) % 2.2 > 0.8 else SIGN_D
        return SAIL_O if (a + 20) % 2.2 < 0.8 else A
    back = [("sail", ell(-5.2, -2.4 - sail * 0.5, 4.8, 8.0 + sail * 0.5, -0.32), sail_col, True)]
    return baby("spino", m=m, arm=arm, tail=tail, nod=nod, step=step, snout=(6.8, -5.4, 5.2, 2.6), back=back, teeth=2,
                smile=False)


def egg(lift=0.0, sink=0.0, shell=None, arm=0.0, nod=0.0, m=0.0, tail=0.0):
    """표식: 알껍데기 모자(톱니 금 · 민트 점)를 쓴 티라노 틀 아기. lift 는 모자가 뜬 높이,
    sink 는 아기가 아래로 숨은 정도(칸), shell 을 주면 그 높이(제 좌표 w)까지 아래 알껍데기가 둘러싼다"""
    B, D, L, S = C["egg"]
    cy = -11.2 - lift

    def zig_cap(a):
        return cy + 2.0 - 1.0 * abs(((a + 20) % 2.2) - 1.1)

    def cap_col(a, b):
        return EGG_SPOT if (a - 2.6) ** 2 + (b - cy + 0.6) ** 2 < 1.1 or (a + 1.6) ** 2 + (b - cy - 0.4) ** 2 < 0.8 else S
    front = [("cap", but(ell(1.0, cy + 0.8, 5.4, 3.8, -0.12), lambda a, b: b > zig_cap(a)), cap_col, True)]
    parts, deco = baby("egg", m=m, arm=arm, nod=nod, tail=tail, front=front)
    parts = shift(parts, 0.0, sink)
    if shell is not None:
        def zig(a):
            return shell + 1.1 * abs(((a + 20) % 2.4) - 1.2)
        spots_ = [(-4.0, 6.0), (2.6, 8.0), (-1.0, 9.6), (4.2, 4.6), (-5.4, 9.0)]

        def shell_col(a, b):
            for pa, pb in spots_:
                if (a - pa) ** 2 + (b - pb) ** 2 <= 1.1:
                    return EGG_SPOT
            return S
        hands = [p for p in parts if p[0] == "arm"]
        rest = [p for p in parts if p[0] != "arm"]
        parts = hands + [("shell", but(ell(-0.6, 5.0, 7.6, 6.8), lambda a, b: b < zig(a)), shell_col, True)] + rest

    def deco2(f, rig, mood="open"):
        r2 = Rig(*rig.world(0.0, sink), 0.0, rig.k, rig.fx)
        r2.c, r2.s = rig.c, rig.s
        g = {}
        deco(g, r2, mood)
        if shell is not None:   # 껍데기 앞으로 나온 꾸밈은 지운다
            g = {p: c for p, c in g.items() if not _in_shell(rig, p, shell)}
        f.update(g)
    return parts, deco2


def _in_shell(rig, p, shell):
    a, b = rig.local(p[0] + 0.5, p[1] + 0.5)
    return ((a + 0.6) / 7.6) ** 2 + ((b - 5.0) / 6.8) ** 2 <= 1 and b > shell + 1.1 * abs(((a + 20) % 2.4) - 1.2)


def ptera(wing=0.0, nod=0.0, legs=True, cross=False):
    """프테라노돈 — 동그란 큰 머리 · 뒤로 뾰족한 보라 볏 · 노란 부리 · 보라 날개막.
    wing: -1 위로 활짝 … 0 뒤로 펼침 … 1 아래로 접음. cross 면 날개 둘을 몸 앞에 X 로 엇갈린다"""
    B, D, L, A = C["ptera"]
    piv = (0.6, -2.4)
    head = turn([("beak", tri((3.6, -6.0), (10.0, -4.6), (3.8, -3.2)), BEAK, True),
                 ("head", ell(1.0, -5.0, 4.2, 3.7), lambda a, b: L if b > -3.2 and a > 0 else B, True),
                 ("crest", tri((-0.6, -7.6), (-8.4, -9.8), (-2.2, -4.6)), PURPLE_D, True)], piv, nod)
    CANON = [(1.0, -0.6), (-4.6, -2.8), (-12.0, -0.8), (-7.6, 1.2), (-5.2, 2.6), (-2.6, 4.2)]

    def wing_poly(dx, extra):
        th = 10 - 45 * wing + extra
        sh = (0.4 + dx, -0.6)
        return tri(*[rp((sh[0] + a, sh[1] + b), sh, th) for a, b in CANON])
    parts = list(head)
    if cross:
        parts.append(("wingx", any_of(bar((-6.0, -2.6), (6.4, 6.0), 2.0, 1.4), bar((6.4, -2.6), (-6.0, 6.0), 2.0, 1.4)),
                      A, True))
    else:
        parts.append(("wing", wing_poly(0.0, 0.0), A, True))
    parts.append(("body", ell(-0.4, 1.8, 3.8, 4.2), lambda a, b: L if a > 0.4 else B, False))
    if legs:
        parts.append(("legs", any_of(bar((-0.6, 5.0), (-0.6, 6.6), 0.8), ell(0.4, 7.0, 1.6, 0.8)), BEAK, True))
    if not cross:
        parts.append(("wingfar", wing_poly(1.8, 8.0), PURPLE_D, False))

    def deco(f, rig, mood="open"):
        eye(f, rig, *rp((2.2, -5.6), piv, nod), mood)
        blush(f, rig, *rp((2.8, -3.6), piv, nod))
    return parts, deco


BODY = {"trex": trex, "triceratops": triceratops, "stego": stego, "brachio": brachio, "ptera": ptera,
        "ankylo": ankylo, "pachy": pachy, "raptor": raptor, "spino": spino, "egg": egg}


def paint(f, sp, rig, mood="open", **kw):
    """몸 하나를 f 위에 덧그린다(앞에 오는 것). → 몸 칸 집합"""
    parts, deco = BODY[sp](**kw)
    o, mask, _ = draw(rig, parts)
    deco(o, rig, mood)
    f.update(o)
    return mask


def under(f, sp, rig, mood="open", **kw):
    """몸 하나를 f 뒤에 그린다(이미 있는 칸은 안 덮음)"""
    parts, deco = BODY[sp](**kw)
    o, mask, _ = draw(rig, parts)
    deco(o, rig, mood)
    for p, c in o.items():
        f.setdefault(p, c)
    return mask


# ── 소품 ─────────────────────────────────────────────────────────────────────
BARE = False   # 켜면 the_arrow 가 아무것도 안 그린다 — run() 이 매끈한 모양용 공룡 층(_peek.txt)을 뽑을 때


def the_arrow(f):
    """sea.peek 와 똑같은 1.6배 흰 화살표 — 끝 (1, 1). 화살표는 커서 — 쓸 때 sea.mark 가 파랑 맨 끝 비트로 공룡과 가른다"""
    if BARE:
        return
    solid(f, raster([(1 + x * PEEK_S, 1 + y * PEEK_S) for x, y in PEEK_CUR]), sea.Cur(PEEK_WHITE), sea.Cur(OUT))
    f[1, 1] = sea.Cur(OUT)


ARROW_MASK = raster([(1 + x * PEEK_S, 1 + y * PEEK_S) for x, y in PEEK_CUR])


def sign(f, R=13.5):
    ring = {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
    slash = set()
    for t in range(-90, 91):
        x, y = 15.5 + t / 100 * (R - 1.5) * 0.7071, 15.5 + t / 100 * (R - 1.5) * 0.7071
        slash |= disc(x, y, 1.3)
    solid(f, ring | slash, sea.Cur(SIGN), sea.Cur(SIGN_D))   # 금지 표지는 커서


def in_sign(f):
    return {p: c for p, c in f.items() if 1 <= p[1] <= 30 and 1 <= p[0] <= 30}


def drop(f, x, y, col=SWEAT):
    """땀방울 — 위가 뾰족한 3칸"""
    f[x, y] = col
    f[x, y + 1] = col
    f[x - 1, y + 1] = col
    f[x - 1, y + 2] = col
    f[x, y + 2] = col


def star(f, x, y, col=SPARK):
    for p in ((x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
        f[p] = col


def puff(f, x, y, r=1.2, col=DUST):
    for p in disc(x, y, r):
        f.setdefault(p, col)


def leaf_branch(f, x0, y0, n, k=0):
    """오른쪽 위에서 늘어진 나뭇가지 — 잎 n 장"""
    for i in range(6):
        f[x0 + i, y0 - (i // 3)] = STEM
    for i in range(n):
        lx, ly = x0 + 1 + i * 2, y0 + 1 + (i % 2)
        solid(f, disc(lx + 0.5, ly + 1.0, 1.3), LEAF, LEAF_D)


def grass(f, x, y, h=3, col=LEAF):
    for i in range(h):
        f[x, y - i] = col
    f[x - 1, y - h + 1] = col
    f[x + 1, y - h + 2] = col


def qmark(f, x, y, col=OUT):
    for p in sea.QMARK and [(i, j) for j, row in enumerate(sea.QMARK) for i, ch in enumerate(row) if ch == "#"]:
        f[x + p[0], y + p[1]] = col


def fish(f, x, y, flip=False, col=FISH):
    """작은 물고기 5×3"""
    s = -1 if flip else 1
    for dx, dy in ((0, 0), (1, 0), (2, 0), (1, -1), (1, 1), (0, -1), (0, 1), (-1, 0)):
        f[x + s * dx, y + dy] = col
    f[x - s * 2, y - 1] = FISH_D
    f[x - s * 2, y + 1] = FISH_D
    f[x + s * 2, y - 1] = OUT


# ── 칸: arrow ────────────────────────────────────────────────────────────────
def peek_with(sp, loc, k_, fur, mood_of=lambda k: "blink" if k == 7 else "open", ang=0.0, fx=1, below=None, **kwf):
    """sea.peek 틀(화살표 뒤 빼꼼) — loc 은 머리 가운데(제 좌표). kwf(k) → 몸 자세.
    below 를 주면 머리 가운데보다 그만큼 아래 칸은 버린다 — 날개 밑으로 다리가 비치면 지저분해서"""
    def head(x, y, k):
        rig = Rig.at(loc, (x, y), ang, k_, fx)
        g = {}
        paint(g, sp, rig, mood_of(k), **(kwf["pose"](k) if "pose" in kwf else {}))
        if below is not None:
            g = {p: c for p, c in g.items() if p[1] <= y + below}
        return g
    return [finish(peek(k, head, OUT, fur)) for k in range(N)]


def arrow_trex():
    """화살표 오른쪽 아래에 선 티라노가 화살표 날개를 잡으려고 짧은 팔을 버둥 — 안 닿아서 땀"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        the_arrow(f)
        reach = 1.2 * abs(math.sin(ph))
        rig = Rig(26.0, 19.6, 0.0, 0.8, -1)
        paint(f, "trex", rig, "squeeze" if k % 6 in (2, 3) else "open",
              arm=1.6 + reach, arm_far=0.6 + 1.6 - reach, nod=-8 - 4 * abs(math.sin(ph)), lean=0.0, tail=0.8 * math.sin(ph))
        if k % 6 in (2, 3, 4):
            drop(f, 30, 6 + (k % 6 - 2))
        fr.append(finish(f))
    return fr


def arrow_ptera():
    """화살표 빗변 가운데에 내려앉은 프테라 — 날개를 폈다 접었다, 볏이 까딱"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        the_arrow(f)
        wg = 0.5 + 0.5 * math.cos(ph)         # 1 접음 … 0 펼침
        rig = Rig.at((0.4, 7.4), (17.6, 16.0), 0.0, 0.84)
        paint(f, "ptera", rig, "blink" if k == 6 else "open", wing=-0.7 + 1.7 * wg, nod=-4 * math.sin(ph))
        fr.append(finish(f))
    return fr


def arrow_tricera():
    """화살표 오른쪽 아래에 선 트리케라가 고개를 숙여 코뿔로 날개 끝을 콕콕 — 밀 때 질끈, 꼬리 살랑"""
    fr = []
    poke = [0, 0, 0.5, 1, 1, 0.5, 0, 0, 0.5, 1, 1, 0.5]
    for k, ph in enumerate(phases()):
        f = {}
        the_arrow(f)
        p = poke[k]
        rig = Rig(25.6 - 1.0 * p, 20.0, 0.0, 0.74, -1)
        paint(f, "triceratops", rig, "squeeze" if p == 1 else "open", nod=4 + 8 * p, tail=0.8 * math.sin(ph))
        if p == 1:
            f[16, 13 - k % 2] = SPARK
            f[15, 15] = SPARK
        fr.append(finish(f))
    return fr


def arrow_stego():
    """화살표 오른쪽 아래 스테고가 날개 끝을 킁킁 — 등판이 앞에서 뒤로 차례로 반짝"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        the_arrow(f)
        sniff = k % 4 in (1, 2)
        rig = Rig(24.6, 20.4, 0.0, 0.74, -1)
        paint(f, "stego", rig, "happy" if sniff else "open", plate=(k // 3 % 4,), tail=0.9 * math.sin(ph),
              nod=-4 + (4 if sniff else 0))
        if sniff:
            f[17, 15 - k % 2] = OUT
            f[16, 14 - k % 2] = OUT
        fr.append(finish(f))
    return fr


def arrow_brachio():
    """화살표 오른쪽 아래 브라키오가 고개를 쳐들어 화살표 끝을 올려다본다 — 목을 늘였다 줄였다, 고개 까딱"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        the_arrow(f)
        sw = math.sin(ph)
        rig = Rig(24.4, 21.4, 0.0, 0.7, -1)
        paint(f, "brachio", rig, "blink" if k == 8 else "open", up=0.8 + 0.8 * sw, nod=-8 + 4 * sw, tail=0.6 * sw)
        fr.append(finish(f))
    return fr


def arrow_ankylo():
    """화살표 오른쪽 아래 안킬로가 화살표를 올려다보며 꼬리 곤봉을 통통 — 바닥 칠 때 먼지"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        the_arrow(f)
        h = abs(math.sin(ph))
        rig = Rig(23.6, 21.6, 0.0, 0.7, -1)
        paint(f, "ankylo", rig, "happy" if h < 0.3 else "open", club=-1.0 + 4.0 * h, tail=-1.6, nod=-6)
        if h < 0.3:
            x, _ = rig.cell(*rp((-12.8, 4.6), (-7.6, 4.0), TAIL_UP))   # 꼬리를 든 판에서도 곤봉 밑 바닥에
            _, y = rig.cell(-12.8, 4.6)
            puff(f, x - 1, y + 1, 0.9)
            puff(f, x + 2, y + 1, 0.8)
        fr.append(finish(f))
    return fr


def arrow_pachy():
    """화살표 오른쪽에 선 파키가 돔 머리로 빗변을 콩콩 — 박을 때 별이 튄다"""
    fr = []
    bonk = [0, 0, 1, 2, 3, 2, 0, 0, 1, 2, 3, 2]
    for k in range(N):
        f = {}
        the_arrow(f)
        b = bonk[k]
        rig = Rig(25.0 - 0.8 * b, 20.2, 0.0, 0.78, -1)
        paint(f, "pachy", rig, "squeeze" if b == 3 else "open", nod=6 * b, tail=0.5 * b)
        if b == 3:
            star(f, 15, 9)
            f[13, 7] = SPARK
            f[17, 6] = SPARK
        fr.append(finish(f))
    return fr


def arrow_raptor():
    """화살표 뒤에서 랩터가 빗변을 잡고 빼꼼 — 고개를 갸웃, 깃털 볏이 쫑긋"""
    return peek_with("raptor", (1.6, -7.0), 0.74, C["raptor"][0], below=3,
                     mood_of=lambda k: "blink" if k == 7 else "open",
                     pose=lambda k: dict(nod=8 * math.sin(2 * math.pi * k / N), crest=0.8 * (k % 4 == 0)))


def arrow_spino():
    """화살표 오른쪽 아래 스피노가 긴 주둥이로 날개 끝을 킁킁 — 등 돛이 오르락내리락"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        the_arrow(f)
        rig = Rig(24.8, 20.0, 0.0, 0.74, -1)
        sniff = k % 6 in (2, 3)
        paint(f, "spino", rig, "happy" if sniff else "open", sail=1.2 * math.sin(ph), nod=-2 + (5 if sniff else 0),
              tail=0.7 * math.sin(ph))
        if sniff:
            f[16, 13 - k % 2] = OUT
            f[15, 12 - k % 2] = OUT
        fr.append(finish(f))
    return fr


def arrow_egg():
    """화살표 뒤에서 알모자 아기가 빼꼼 — 모자가 들썩, 웃을 때 눈이 휨"""
    return peek_with("egg", (1.6, -7.0), 0.7, C["egg"][0],
                     mood_of=lambda k: "happy" if k in (3, 4) else "blink" if k == 8 else "open",
                     pose=lambda k: dict(lift=1.6 if k in (2, 3, 4, 5) else 0.0), below=3)


# ── 칸: wait ─────────────────────────────────────────────────────────────────
def wait_trex():
    """짧은 팔 버둥버둥 — 양팔이 엇갈려 위아래, 입을 '와앙' 벌렸다 닫고 꼬리가 살랑"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        up_ = 1.4 if k % 2 else -0.4
        roar = k in (4, 5, 6)
        rig = Rig(17.4, 17.4, 0.0, 0.98)
        paint(f, "trex", rig, "squeeze" if roar else "open", arm=up_, arm_far=1.4 - up_, m=0.7 if roar else 0.0,
              tail=0.9 * math.sin(ph), nod=-6 if roar else 0)
        if k % 2:
            for p in ((26, 18), (27, 17)):
                f.setdefault(p, OUT)
        fr.append(finish(f))
    return fr


def wait_ptera():
    """제자리 날갯짓 — 날개가 위아래로 펄럭이고 몸이 따라 오르내림"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        w = math.cos(ph)
        rig = Rig(17.4, 18.4 + 0.8 * w, 0.0, 1.08)
        paint(f, "ptera", rig, "blink" if k == 9 else "open", wing=w * 1.1, legs=True)
        fr.append(finish(f))
    return fr


def wait_tricera():
    """풀을 우물우물 — 입에 문 풀이 줄어들고 부리가 오물, 꼬리를 살랑"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        rig = Rig(17.0, 17.6, 0.0, 0.94)
        chew = k % 2
        paint(f, "triceratops", rig, "happy" if k in (8, 9) else "open", nod=2 if chew else 0, tail=1.0 * math.sin(ph),
              m=0.4 * chew)
        bx, by = rig.cell(*rp((9.8, -3.2), (1.0, -2.0), 2 if chew else 0))
        for i in range(3 - k // 4):
            f[bx + 1 + i, by + (i % 2)] = LEAF
        grass(f, 30, 28, 3)
        grass(f, 2, 28, 2)
        fr.append(finish(f))
    return fr


def wait_stego():
    """등판이 앞에서 뒤로 차례로 반짝 — 반짝이 별이 판 위로 톡, 꼬리 가시가 흔들"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        i = k // 3   # 0..3 판 번호
        rig = Rig(17.8, 17.8, 0.0, 0.94)
        paint(f, "stego", rig, "happy" if k >= 10 else "open", plate=(i,), tail=1.0 * math.sin(ph))
        x, y = rig.cell(*stego_tip(i))
        if k % 3 == 1:
            star(f, x, y - 1)
        else:
            f[x, y - 1] = SPARK
        fr.append(finish(f))
    return fr


def wait_brachio():
    """목을 쭉 올려 나뭇잎을 냠냠 — 올라갔다가 잎이 한 장씩 줄고 내려온다"""
    fr = []
    reach = [0, 0.3, 0.7, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.7, 0.3, 0]
    for k in range(N):
        f = {}
        r = reach[k]
        rig = Rig(15.6, 19.4, 0.0, 0.84)
        n = max(1, 3 - max(0, (k - 4) // 2)) if k >= 4 else 3
        leaf_branch(f, 20, 1, n)
        paint(f, "brachio", rig, "happy" if 5 <= k <= 8 else "open", up=2.4 * r, nod=-16 * r, m=1 if k in (5, 7) else 0)
        fr.append(finish(f))
    return fr


def wait_ankylo():
    """꼬리 곤봉을 통통 — 등 뒤로 들었다가 땅에 닿을 때 먼지가 퐁"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        h = abs(math.sin(ph))
        rig = Rig(18.2, 17.8, 0.0, 0.94)
        paint(f, "ankylo", rig, "happy" if h < 0.3 else "open", club=-1.4 + 5.0 * h, tail=-0.6)
        if h < 0.3:
            x, y = rig.cell(-12.8, 4.6)
            puff(f, x - 2, y + 1, 1.0)
            puff(f, x + 2, y + 1, 0.8)
        fr.append(finish(f))
    return fr


def wait_pachy():
    """박치기 준비 — 고개를 숙이고 뒷발로 땅을 긁으며 콧김 퐁퐁, 마지막에 앞으로 몸을 쏠림"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        lean = k in (9, 10)
        rig = Rig(16.8 + (1.2 if lean else 0.0), 17.6, 0.0, 0.94)
        paint(f, "pachy", rig, "angry", nod=10 if k < 9 else 18, step=(-1.4 if k % 4 < 2 else 0.6) if k < 9 else 0,
              tail=0.8 * math.sin(ph))
        if k % 4 in (1, 2) and k < 9:
            x, y = rig.cell(*rp((10.6, -6.4), (1.0, -2.0), 10))
            puff(f, x + k % 4, y + 1, 0.9, HI)
        if k % 4 == 3 and k < 9:
            x, y = rig.cell(-3.0, 9.4)
            puff(f, x - 2, y, 1.0)
        if lean:
            for y in (10, 13, 16):
                f.setdefault((2, y), OUT)
                f.setdefault((3, y), OUT)
        fr.append(finish(f))
    return fr


def wait_raptor():
    """고개를 갸웃 갸웃 — 왼쪽 오른쪽으로 기울이며 머리 위에 물음표"""
    fr = []
    tilt = [0, 8, 14, 14, 8, 0, -8, -14, -14, -8, 0, 0]
    for k in range(N):
        f = {}
        rig = Rig(17.8, 17.2, 0.0, 0.94)
        paint(f, "raptor", rig, "blink" if k == 10 else "open", nod=tilt[k], tail=0.8 * math.sin(2 * math.pi * k / N),
              crest=0.6 if abs(tilt[k]) == 14 else 0.0)
        if abs(tilt[k]) == 14:
            qmark(f, 25, 1)
        fr.append(finish(f))
    return fr


def wait_spino():
    """물가에서 물고기 낚기 — 주둥이를 물에 첨벙 넣었다가 물고기를 물고 나온다"""
    fr = []
    dip = [0, 0.3, 0.7, 1.0, 1.0, 0.6, 0.2, 0, 0, 0, 0, 0]
    for k in range(N):
        f = {}
        d = dip[k]
        rig = Rig(15.0, 16.6, 0.0, 0.9)
        g = {}
        paint(g, "spino", rig, "squeeze" if d >= 1 else "happy" if 6 <= k <= 9 else "open", nod=40 * d,
              tail=0.6 * math.sin(2 * math.pi * k / N))
        f.update({p: c for p, c in g.items() if p[1] < 26 or p[0] < 19 or d < 0.5})
        for x in range(19, 32):
            f[x, 26] = sea.WAKE[1]
            f[x, 27] = sea.WAKE[3] if (x + k) % 3 else sea.WAKE[2]
        if 6 <= k <= 10:
            hx_, hy_ = rig.cell(11.6, -4.0)
            fish(f, hx_ + 1, hy_ + 1, flip=False)
        if k in (3, 4):
            sea.splash(f, 26.0, 25.0, k, n=4, spread=4.0, height=4.0)
        fr.append(finish(f))
    return fr


def wait_egg():
    """알껍데기에 앉은 아기가 흔들흔들 — 모자가 퐁 뜨며 만세, 다시 쏙"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        rock = 8 * math.sin(2 * ph) if k < 6 else 0
        open_ = k in (6, 7, 8, 9)
        rig = Rig.at((0.0, 11.0), (16.4, 29.0), rock, 0.88)
        paint(f, "egg", rig, "happy" if open_ else "blink" if k < 6 else "open", lift=3.0 if open_ else 0.0,
              sink=3.6 if k < 6 else 0.0 if open_ else 1.8, shell=1.0, arm=3.6 if open_ else 0.0, m=0.5 if open_ else 0)
        if open_:
            star(f, 5, 6 - (k - 6) % 2)
            star(f, 26, 5 + (k - 6) % 2)
        fr.append(finish(f))
    return fr


# ── 칸: no ───────────────────────────────────────────────────────────────────
def no_trex():
    """짧은 팔로 X 를 만들려는데 팔이 안 닿아 허우적 — 질끈 감고 땀"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f)
        t = abs(math.sin(ph))
        rig = Rig(17.4, 17.4, 0.0, 0.66)
        paint(f, "trex", rig, "squeeze", arm=0.6 + 1.6 * t, arm_far=2.2 - 1.6 * t, tail=0.6 * math.sin(ph))
        if k % 4 < 2:
            drop(f, 23, 6)
        fr.append(finish(in_sign(f)))
    return fr


def no_ptera():
    """두 날개를 앞으로 X 자로 엇갈려 '안 돼' — 볏을 꼿꼿, 까딱"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f)
        rig = Rig(15.6, 18.0 + (0.6 if k % 4 < 2 else 0.0), 0.0, 0.72)
        paint(f, "ptera", rig, "squeeze" if k % 6 < 3 else "angry", cross=True, nod=-6 if k % 6 < 3 else 0)
        fr.append(finish(in_sign(f)))
    return fr


def no_tricera():
    """뿔을 들이밀며 고개를 도리도리 — 앞으로 콕 숙일 때 콧김"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f)
        rig = Rig(16.4 + 0.6 * math.sin(ph), 17.8, 0.0, 0.64)
        poke = k % 6 in (2, 3)
        paint(f, "triceratops", rig, "angry", nod=14 if poke else 6 * math.sin(2 * ph), step=0.6 * math.sin(2 * ph))
        if poke:
            x, y = rig.cell(11.4, -3.4)
            puff(f, x + 1, y, 0.8, HI)
        fr.append(finish(in_sign(f)))
    return fr


def no_stego():
    """홱 등 돌리고 꼬리 가시를 '안 돼 안 돼' 흔든다"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f)
        rig = Rig(14.6, 18.0, 0.0, 0.62, -1)
        paint(f, "stego", rig, "sulk", tail=3.0 * math.sin(2 * ph), nod=-6)
        fr.append(finish(in_sign(f)))
    return fr


def no_brachio():
    """쳐든 머리를 시계추처럼 도리도리 — 뾰로통"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f)
        sw = math.sin(ph)
        rig = Rig(16.6, 19.6, 0.0, 0.6)
        paint(f, "brachio", rig, "sulk", nod=-14 * sw, step=0.4 * sw)
        fr.append(finish(in_sign(f)))
    return fr


def no_ankylo():
    """홱 등 돌리고 꼬리 곤봉만 탁탁 — 뾰로통"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f)
        rig = Rig(14.6, 18.2, 0.0, 0.62, -1)
        paint(f, "ankylo", rig, "sulk", club=-0.6 + 3.0 * abs(math.sin(2 * ph)), tail=-0.8, nod=-6)
        fr.append(finish(in_sign(f)))
    return fr


def no_pachy():
    """금지 빗금을 돔 머리로 콩 — 박을 때 별이 튀고 눈이 질끈"""
    fr = []
    bonk = [0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1]
    for k in range(N):
        f = {}
        sign(f)
        b = bonk[k]
        rig = Rig(19.4 - 0.6 * b, 19.0, 0.0, 0.64, -1)
        paint(f, "pachy", rig, "squeeze" if b == 3 else "angry", nod=6 * b)
        if b == 3:
            star(f, 11, 11)
            f[9, 8] = SPARK
            f[13, 7] = SPARK
        fr.append(finish(in_sign(f)))
    return fr


def no_raptor():
    """볏을 바짝 세우고 '캬악' — 입을 벌리고 발톱 팔을 치켜든다"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f)
        hiss = k % 6 in (1, 2, 3)
        rig = Rig(17.0, 17.8, 0.0, 0.64)
        paint(f, "raptor", rig, "angry", m=0.8 if hiss else 0.0, crest=1.4 if hiss else 0.2, arm=1.8 if hiss else 0.0,
              nod=-6 if hiss else 0)
        fr.append(finish(in_sign(f)))
    return fr


def no_spino():
    """돛을 빨갛게 붉히고 고개를 홱 쳐든다(흥)"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f)
        fl = k % 4 < 2
        rig = Rig(15.0, 18.4, 0.0, 0.62, -1)
        paint(f, "spino", rig, "sulk", nod=-12 + 3 * math.sin(ph), sail=1.0 if fl else 0.0, flush=fl)
        fr.append(finish(in_sign(f)))
    return fr


def no_egg():
    """알껍데기 속으로 쏙 숨어 모자를 닫고 알째 도리도리 — 금 사이로 눈만"""
    fr = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f)
        rock = 12 * math.sin(ph)
        rig = Rig.at((0.0, 3.0), (15.5, 17.4), rock, 0.64)
        paint(f, "egg", rig, "squeeze" if k % 6 in (2, 3) else "sulk", sink=5.4, shell=-1.4)
        fr.append(finish(in_sign(f)))
    return fr


# ══ 나머지 14칸 — 열 마리가 장면 하나를 같이 쓰고 몸 · 표식(뿔 · 판 · 돛 · 곤봉 …)만 마리마다 다르다 ══════
# 짹짹이(gen/bird.py) · 댕댕이(gen/dog.py) 틀을 따른다: busy · help · person · pin 은 작은 화살표(끝 (1, 1)) 밑에
# 작은 공룡 + 오른쪽 소품, 크기 조절 넷은 그 축으로 몸을 쭉 늘이는 기지개, 나머지는 판 가운데(center_hot) 또는 끝 칸.
# 마리마다 받는 인자가 달라서(프테라는 날개 · 안킬로는 곤봉 …) 넉넉히 넘기고 그 몸이 받는 것만 골라 쓴다(body_kw)
import inspect  # noqa: E402

CHEV, CHEV_L = hx("f59a5aff"), hx("f59a5aa0")      # 화살촉 (짙은 것 · 옅은 것) — 짹짹이와 같은 색
BONE, BONE_D = hx("f6ead0ff"), hx("d8c49cff")      # 화석 뼈 (물음표 · I 빔)
SKIN, SHIRT, SHIRT_D = hx("f7d7bcff"), hx("4a7fb5ff"), hx("2e5a88ff")
BERRY, BERRY_D = hx("e8484aff"), hx("b02a30ff")
PEN_Y, PEN_YD, PEN_W, PEN_G, PEN_E = hx("f6c84aff"), hx("d9a032ff"), hx("f3d6a8ff"), hx("3a3a44ff"), hx("f4a0b0ff")
MINI_S = 0.8                                       # 작은 화살표 배율
KBOOST = {"ptera": 1.3}                          # 프테라는 몸 단위가 작아서 같은 배율이면 콩알만 하다
MINI_BOX = (1, 17, 15, 30)                         # 작은 공룡 자리(x0, y0, x1, y1) — 작은 화살표 밑


class SRig(Rig):
    """기지개 그리개 — 선 몸을 그대로 그린 뒤 화면 축 e(단위 벡터) 쪽으로 sa 배 늘이고 그 직각으로 sb 배.
    처음엔 몸을 축 방향으로 눕혀(돌려) 늘였더니 세로 · 대각에서 공룡이 뭉개진 덩어리로 읽혀서, 몸은 세우고 판만 늘인다"""

    def __init__(self, ox, oy, k, fx, e, sa, sb):
        super().__init__(ox, oy, 0.0, k, fx)
        self.e, self.sa, self.sb = e, sa, sb

    def world(self, a, b):
        x, y = super().world(a, b)
        qx, qy = x - 16.0, y - 16.0
        pa = qx * self.e[0] + qy * self.e[1]
        pb = -qx * self.e[1] + qy * self.e[0]
        pa, pb = pa * self.sa, pb * self.sb
        return 16.0 + pa * self.e[0] - pb * self.e[1], 16.0 + pa * self.e[1] + pb * self.e[0]

    def local(self, x, y):
        qx, qy = x - 16.0, y - 16.0
        pa = (qx * self.e[0] + qy * self.e[1]) / self.sa
        pb = (-qx * self.e[1] + qy * self.e[0]) / self.sb
        return super().local(16.0 + pa * self.e[0] - pb * self.e[1], 16.0 + pa * self.e[1] + pb * self.e[0])


def body_kw(sp, kw):
    """그 몸 함수가 받는 인자만 남긴다"""
    ps = inspect.signature(BODY[sp]).parameters
    return {k: v for k, v in kw.items() if k in ps}


def flair(k, ph, **over):
    """장마다 마리별 표식이 살짝 움직이는 기본 자세 — 꼬리 살랑 · 날개 접음 · 곤봉 통통 · 돛 오르락 · 볏 쫑긋 · 등판 반짝"""
    kw = dict(tail=0.8 * math.sin(ph), wing=0.9 + 0.1 * math.sin(ph), club=0.6 + 1.2 * abs(math.sin(ph)),
              sail=0.8 * math.sin(ph), crest=0.6 if k % 6 == 0 else 0.0, plate=(k // 3 % 4,))
    kw.update(over)
    return kw


def figure(sp, poses, k_, fx=1, ang=0.0):
    """poses: [{mood, kw, sa?, sb?, e?}] → 장마다 몸 그림(판 가운데 근처에 그린 것 — fit 이 옮긴다)"""
    out = []
    k_ *= KBOOST.get(sp, 1.0)
    for p in poses:
        if "sa" in p:
            rig = SRig(16.0, 16.0, k_, fx, p["e"], p["sa"], p.get("sb", 1.0))
        else:
            rig = Rig(16.0, 16.0, ang, k_, fx)
        g = {}
        paint(g, sp, rig, p.get("mood", "open"), **body_kw(sp, p.get("kw", {})))
        out.append(g)
    return out


def bbox(frames):
    ps = [p for f in frames for p, c in f.items() if c[3] == 255]
    return min(x for x, _ in ps), min(y for _, y in ps), max(x for x, _ in ps), max(y for _, y in ps)


def moved(f, dx, dy):
    return {(x + dx, y + dy): c for (x, y), c in f.items()}


def fit(sp, poses, box, fx=1, ang=0.0, kmax=0.62, kmin=0.4, ax="center", ay="bottom"):
    """몸을 box(x0, y0, x1, y1) 안에 들어가는 가장 큰 배율로 그려 옮긴다(장 전체를 같은 만큼 — 안 떨리게)"""
    bw, bh = box[2] - box[0] + 1, box[3] - box[1] + 1
    k_ = kmax
    while k_ > kmin:
        x0, y0, x1, y1 = bbox(figure(sp, poses[::3], k_, fx, ang))
        if x1 - x0 + 1 <= bw and y1 - y0 + 1 <= bh:
            break
        k_ -= 0.03
    frs = figure(sp, poses, k_, fx, ang)
    x0, y0, x1, y1 = bbox(frs)
    dx = box[0] - x0 if ax == "left" else box[2] - x1 if ax == "right" else round((box[0] + box[2] - x0 - x1) / 2)
    dy = box[1] - y0 if ay == "top" else box[3] - y1 if ay == "bottom" else round((box[1] + box[3] - y0 - y1) / 2)
    return [moved(f, dx, dy) for f in frs]


def chevron(f, cx, cy, dx, dy, col):
    """(dx, dy) 쪽을 가리키는 화살촉, 꼭짓점 (cx, cy) — bird.chevron 과 같다(대각은 두 칸 굵기 ㄱ 자)"""
    if dx and dy:
        for i in range(5):
            for w in (0, 1):
                f[cx - dx * i, cy - dy * w] = col
                f[cx - dx * w, cy - dy * i] = col
        return
    px, py = -dy, dx
    for i in range(4):
        for s in (-1, 1):
            for w in (0, 1):
                f[cx - dx * (i + w) + s * px * i, cy - dy * (i + w) + s * py * i] = col


# ── busy · help · person · pin: 작은 화살표 밑 작은 공룡 + 오른쪽 소품 ───────────────────
def mini_arrow():
    return raster([(1 + x * MINI_S, 1 + y * MINI_S) for x, y in PEEK_CUR])


def mini(sp, look=lambda k, ph: 0.0, mood_of=None):
    """작은 화살표 밑에 선 작은 공룡 12장 — 오른쪽(소품)을 보고 꼬리 살랑, 한 번 끔뻑. look 은 장마다 고개 각"""
    mood_of = mood_of or (lambda k: "blink" if k == 7 else "open")
    poses = [dict(mood=mood_of(k), kw=flair(k, ph, nod=look(k, ph))) for k, ph in enumerate(phases())]
    return fit(sp, poses, MINI_BOX, kmax=0.6, ax="left")


def companion(sp, scene, **mk):
    """작은 화살표 공룡 + scene(k, ph) 이 그리는 소품. 화살표는 맨 위에 — 무엇도 화살표를 덮지 않는다"""
    dinos = mini(sp, **mk)
    am = mini_arrow()
    frames = []
    for k, ph in enumerate(phases()):
        f = scene(k, ph)
        f.update(dinos[k])
        solid(f, am, sea.Cur(PEEK_WHITE), sea.Cur(OUT))   # 화살표는 커서
        f[1, 1] = sea.Cur(OUT)
        frames.append(finish({p: c for p, c in f.items() if 1 <= p[0] <= 31 and 1 <= p[1] <= 31}))
    return frames, (1, 1)


def busy(sp):
    """오른쪽에 그 공룡 색 알갱이 여덟 개가 원을 그리고 한 알씩 차례로 진해지며 돈다 — 공룡은 고개로 따라 봄"""
    B, D, L, A = C[sp]
    # 테를 두른 알갱이는 1배에서 속 빈 네모로 읽혀서 한 색 알갱이로 — 막 진해진 것은 짙은 테두리색, 꼬리는 제 몸 색
    trail = (OUT, D, B, D[:3] + (0x50,))
    cx, cy, R = 24.0, 22.5, 5.6

    def scene(k, ph):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            lag = (head - i) % 8
            col = trail[0] if lag < 1 else trail[1] if lag < 2 else trail[2] if lag < 3.5 else trail[3]
            for p in disc(cx + R * math.cos(a), cy + R * math.sin(a), 1.35):
                f[p] = sea.Cur(col)   # 도는 알갱이 고리는 커서(바쁨)
        return f
    return companion(sp, scene, look=lambda k, ph: 6 * math.sin(ph))


QPATH = [(20.0, 21.0), (20.0, 17.8), (22.2, 15.6), (25.0, 13.4), (25.2, 9.8), (22.4, 7.6), (19.2, 8.6)]


def help_(sp):
    """화석 뼈 한 토막이 물음표 꼴로 휘어 살랑 — 끝은 뼈 마디, 점 자리엔 알 하나. 공룡은 고개 갸웃"""
    def scene(k, ph):
        f = {}
        sw = 0.5 * math.sin(ph)
        pts = [(x + sw * (21.0 - y) / 12.0, y) for x, y in QPATH]
        knobs = any_of(ell(pts[-1][0] - 0.6, pts[-1][1] + 1.0, 1.4, 1.4), ell(pts[-1][0] - 0.6, pts[-1][1] - 1.0, 1.4, 1.4),
                       ell(pts[0][0] - 1.0, pts[0][1] + 0.6, 1.4, 1.4), ell(pts[0][0] + 1.0, pts[0][1] + 0.6, 1.4, 1.4))
        o, _, _ = draw(Rig(0, 0, 0, 1.0), [("bone", any_of(chain(pts, 1.2), knobs), BONE, False)])
        f.update({p: sea.Cur(c) for p, c in o.items()})   # 물음표 뼈와 점 자리 알은 한 기호 — 커서
        egg_m = {p for p in disc(20.5, 26.6, 2.0)} | {p for p in disc(20.5, 25.8, 1.6)}
        solid(f, egg_m, sea.Cur(C["egg"][3]), sea.Cur(OUT))
        f[20, 26] = sea.Cur(EGG_SPOT)
        return f
    return companion(sp, scene, look=lambda k, ph: 8 * math.sin(ph))


def person(sp):
    """그 공룡 후드(등에 표식 색 가시)를 쓴 사람이 손을 흔들고, 작은 공룡이 올려다보며 꼬리 살랑"""
    B, D, L, A = C[sp]

    def scene(k, ph):
        f = {}
        rig = Rig(23.0, 26.0, 0.0, 0.7)
        hand = (9.0, -8.0 - 2.0 * abs(math.sin(ph)))
        spikes = any_of(*[tri((u - 1.4, -12.0 + 0.1 * u * u), (u, -15.4 + 0.1 * u * u), (u + 1.4, -12.0 + 0.1 * u * u))
                          for u in (-3.0, 0.0, 3.0)])
        parts = [("hand", ell(*hand, 2.2, 2.2), SKIN, True), ("sleeve", bar((5.0, -0.5), hand, 1.8), SHIRT, False),
                 ("face", ell(0.0, -6.8, 4.2, 3.8), SKIN, True),
                 ("hood", any_of(ell(0.0, -8.4, 5.6, 5.2), spikes),
                  lambda a, b: (A if sp in ("stego", "spino", "raptor") else D) if b < -12.0 else B, False),
                 ("torso", ell(0, 3.0, 7.6, 6.4), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
        out, mask, _ = draw(rig, parts)
        for sg in (-1, 1):
            ex, ey = rig.cell(sg * 1.8, -7.0)
            out[ex, ey] = EYE
            out[ex, ey + 1] = EYE
            out[rig.cell(sg * 2.8, -5.2)] = BLUSH
        f.update({p: sea.Cur(c) for p, c in out.items() if p[1] <= 30})   # 사람(공룡 후드까지)은 커서
        return f
    return companion(sp, scene, look=lambda k, ph: -10 - 4 * abs(math.sin(ph)),
                     mood_of=lambda k: "happy" if k % 6 in (2, 3) else "blink" if k == 9 else "open")


FOOT = ["#..#..#", "#..#..#", ".#.#.#.", ".#####.", "..###..", "..###..", "...#..."]   # 세 발가락 공룡 발자국


def pin(sp):
    """빨간 지도 핀 속에 흰 세 발가락 공룡 발자국 — 핀이 통통 튀고, 땅에 닿을 때 작은 공룡이 눈웃음"""
    def scene(k, ph):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 23.0, 14.0 + dy
        for x in range(19, 28):
            f.setdefault((x, 29), hx("2a1c2260") if dy else hx("2a1c22a0"))
        pinm = disc(cx, cy, 6.2) | raster([(cx - 4.4, cy + 3.4), (cx + 4.4, cy + 3.4), (cx, cy + 12.4)])
        solid(f, pinm, sea.Cur(SIGN), sea.Cur(SIGN_D))   # 핀 몸통은 커서, 속 발자국 · 땅 그림자는 공룡 쪽
        for j, row in enumerate(FOOT):
            for i, ch in enumerate(row):
                if ch == "#":
                    f[math.floor(cx) - 3 + i, math.floor(cy) - 3 + j] = PEEK_WHITE
        return f
    return companion(sp, scene, look=lambda k, ph: -4.0,
                     mood_of=lambda k: "happy" if round(3 * math.sin(math.pi * k / N)) == 0 else "open")


# ── hand: 고개를 젖혀 주둥이 끝으로 위를 콕 ─────────────────────────────────────────
PECK = [0, 0, 1, 2, 0, 0, 1, 2, 0, 0, 0, 0]   # 2 가 콕(더 젖힘)
HAND_TIP = (16, 2)


def top_tip(f):
    """맨 윗줄 불투명 칸들의 가운데"""
    y = min(y for (x, y), c in f.items() if c[3] == 255)
    xs = sorted(x for (x, yy), c in f.items() if yy == y and c[3] == 255)
    return xs[len(xs) // 2], y


def hand(sp):
    """고개를 하늘로 젖혀 주둥이(트리케라는 뿔 · 프테라는 부리) 끝으로 위를 콕콕 — 그 끝이 맨 위 칸이자 핫스팟이고
    장마다 그대로다. 콕 할 때 더 젖히므로 몸이 따라 내려가고, 끝 양옆으로 튀는 줄"""
    frames = []
    for k, ph in enumerate(phases()):
        p = PECK[k]
        nod = {"ptera": -70, "brachio": -40}.get(sp, -55) - 6 * p
        mood = "squeeze" if p == 2 else "blink" if k == 10 else "happy" if p == 1 else "open"
        g = figure(sp, [dict(mood=mood, kw=flair(k, ph, nod=nod, wing=0.6, up=1.0))], 0.98)[0]
        tx, ty = top_tip(g)
        g = moved(g, HAND_TIP[0] - tx, HAND_TIP[1] - ty)
        f = {}
        if p == 2:
            x, y = HAND_TIP
            for q in ((x - 3, y + 1), (x - 4, y), (x + 3, y + 1), (x + 4, y), (x - 3, y + 3), (x + 3, y + 3)):
                f[q] = OUT
        f.update(g)
        frames.append(finish(f))
    return frames, HAND_TIP


# ── cross: 십자 가운데 빨간 열매를 노려보는 공룡 ─────────────────────────────────────
def cross(sp):
    """조준선 네 갈래 가운데에 빨간 열매 하나 — 오른쪽 아래 칸의 공룡이 고개를 내밀어 노려보고 침을 꼴깍.
    열매 가운데 (15, 15) 가 핫스팟"""
    poses = []
    for k, ph in enumerate(phases()):
        lick = k % 6 in (3, 4)
        poses.append(dict(mood="happy" if lick else "blink" if k == 8 else "open",
                          kw=flair(k, ph, nod=-6 + 4 * math.sin(ph), m=0.5 if lick else 0.0, wing=1.0)))
    dinos = fit(sp, poses, (18, 18, 31, 31), fx=-1, kmax=0.6, ax="right")
    frames = []
    for k, ph in enumerate(phases()):
        f = dict(dinos[k])
        for i in list(range(2, 11)) + list(range(21, 30)):   # 조준선 네 갈래는 커서, 가운데 열매는 소품
            f[i, 15] = sea.Cur(OUT)
            f[15, i] = sea.Cur(OUT)
        solid(f, disc(16.0, 16.0, 2.6), BERRY, BERRY_D)
        f[14, 14] = HI
        f[15, 15] = BERRY
        for p in ((16, 12), (17, 11), (18, 11)):
            f[p] = LEAF_D
        frames.append(finish({p: c for p, c in f.items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31}))
    return frames, (15, 15)


# ── ibeam: 세로로 선 화석 뼈(I) 옆에서 킁킁 갸웃 ─────────────────────────────────────
TILT = [0, 0, 7, 10, 10, 7, 0, 0, -7, -10, -10, -7]


def bone_i(f):
    """I 꼴 화석 뼈: 세로 줄기 + 위아래 가로대, 가로대 양끝은 뼈 마디처럼 둥글게"""
    m = {(x, y) for y in range(3, 29) for x in (14, 15, 16)}
    m |= {(x, y) for y in (3, 4, 5, 26, 27, 28) for x in range(11, 20)}
    for cx, cy in ((10.5, 3.5), (10.5, 5.5), (20.5, 3.5), (20.5, 5.5), (10.5, 26.5), (10.5, 28.5), (20.5, 26.5), (20.5, 28.5)):
        m |= disc(cx, cy, 1.4)
    solid(f, m, sea.Cur(BONE), sea.Cur(STEM))   # I 기둥은 커서
    f[15, 10] = f[15, 21] = sea.Cur(BONE_D)     # 금


def ibeam(sp):
    """세로로 선 I 꼴 화석 뼈 오른쪽에서 공룡이 고개를 갸웃갸웃하며 킁킁. 핫스팟은 줄기 가운데(15, 15)"""
    poses = [dict(mood="blink" if k == 6 else "happy" if abs(TILT[k]) == 10 else "open",
                  kw=flair(k, ph, nod=TILT[k], wing=1.0)) for k, ph in enumerate(phases())]
    dinos = fit(sp, poses, (18, 8, 31, 29), fx=-1, kmax=0.7, ax="left")
    frames = []
    for k in range(N):
        f = dict(dinos[k])
        g = {}
        bone_i(g)
        f.update(g)     # 뼈(커서 뜻)가 맨 위
        if abs(TILT[k]) == 10:
            f[19, 12] = OUT
            f[20, 11] = OUT
        frames.append(finish({p: c for p, c in f.items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31}))
    return frames, (15, 15)


# ── move · 기지개 ─────────────────────────────────────────────────────────────
def move(sp):
    """제자리에서 쿵쿵 걸음(프테라는 날갯짓) — 네 방향 화살촉이 바깥으로 두근. 몸 가운데가 핫스팟"""
    poses = []
    for k, ph in enumerate(phases()):
        st = 1.2 if k % 6 < 3 else -1.2
        poses.append(dict(mood="happy" if k % 6 in (1, 4) else "open",
                          kw=flair(k, ph, step=st, wing=math.cos(2 * ph), arm=0.6 if k % 6 < 3 else 0.0)))
    dinos = fit(sp, poses, (7, 7, 24, 24), kmax=0.66, ay="center")
    frames = []
    for k in range(N):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy, sea.Cur(CHEV if o else CHEV_L))   # 화살촉은 커서
        f.update(moved(dinos[k], 0, -1 if k % 3 == 1 else 0))
        frames.append(finish(f))
    return frames, None


# 축마다 (늘이는 화면 축 e, 좌우, 화살촉 방향, 고개) — 머리가 축의 위쪽 끝 쪽: ns 위 · we 오른쪽 · nwse 왼쪽 위 · nesw 오른쪽 위
R2 = 0.5 ** 0.5
AXES = {"ns": ((0.0, 1.0), 1, (0, -1), -14), "we": ((1.0, 0.0), 1, (-1, 0), 0),
        "nwse": ((R2, R2), -1, (-1, -1), -8), "nesw": ((R2, -R2), 1, (1, -1), -8)}


def stretch(sp, axis):
    """기지개 — 선 몸 그대로 축 방향으로 쭉 늘였다 줄였다(그 직각으로는 살짝 홀쭉), 늘 때 눈을 질끈.
    축 양끝 화살촉이 두근. 몸 가운데가 핫스팟"""
    e, fx, (dx, dy), look = AXES[axis]
    R = 13 if dx == 0 or dy == 0 else 11
    poses = []
    for k, ph in enumerate(phases()):
        s = 0.5 + 0.5 * math.sin(ph)
        poses.append(dict(mood="squeeze" if s > 0.6 else "open", e=e, sa=1.0 + 0.4 * s, sb=1.0 - 0.12 * s,
                          kw=flair(k, ph, tail=-0.4 * s, nod=look * s, wing=-0.4, up=1.0 * s)))
    lim = 7 if dx and dy else 5
    dinos = fit(sp, poses, (lim, lim, 31 - lim, 31 - lim), fx=fx, kmax=0.62, ay="center")
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if 0.5 + 0.5 * math.sin(ph) > 0.6 else 0
        for sg in (-1, 1):
            chevron(f, 15 + sg * dx * (R + o), 15 + sg * dy * (R + o), sg * dx, sg * dy,
                    sea.Cur(CHEV if o else CHEV_L))   # 화살촉은 커서
        f.update(dinos[k])
        frames.append(finish(f))
    return frames, None


# ── pen: 연필 끝을 입에 물고 사각사각 ───────────────────────────────────────────────
PTIP = (1, 29)


def pencil(f, tip, end):
    """tip(심) → end(지우개) 연필. 심 쪽은 가늘게 깎인 원뿔"""
    t0 = (tip[0] + 0.5, tip[1] + 0.5)
    L = math.hypot(end[0] - t0[0], end[1] - t0[1])
    ux, uy = (end[0] - t0[0]) / L, (end[1] - t0[1]) / L

    def col(a, b):
        t = (a - t0[0]) * ux + (b - t0[1]) * uy
        sd = -(a - t0[0]) * uy + (b - t0[1]) * ux
        if t < 2.0:
            return PEN_G
        if t < 4.2:
            return PEN_W
        if t > L - 2.0:
            return PEN_E
        return PEN_YD if sd > 0.5 else PEN_Y
    cone = bar(t0, (t0[0] + ux * 4.2, t0[1] + uy * 4.2), 0.3, 1.5)
    shaft = bar((t0[0] + ux * 4.0, t0[1] + uy * 4.0), end, 1.5)
    o, _, _ = draw(Rig(0, 0, 0, 1.0), [("pencil", any_of(cone, shaft), col, False)])
    f.update({p: sea.Cur(c) for p, c in o.items()})   # 연필은 커서
    f[tip] = sea.Cur(PEN_G)


def snout_tip(g):
    """왼쪽을 보는 몸의 주둥이 끝 — 위쪽 6할에서 가장 왼쪽 칸(같으면 아래)"""
    x0, y0, x1, y1 = bbox([g])
    cut = y0 + (y1 - y0) * 0.6
    return min(((x, y) for (x, y), c in g.items() if c[3] == 255 and y <= cut), key=lambda p: (p[0], -p[1]))


def pen(sp):
    """연필 끝(지우개)을 입에 물고 쓰는 공룡 — 심이 왼쪽 아래 끝이자 핫스팟. 공룡이 한 칸씩 끄덕이며 연필이 따라 까딱,
    심 오른쪽으로 쓴 줄이 자란다"""
    poses = [dict(mood="blink" if k == 4 else "happy" if k in (8, 9) else "open",
                  kw=flair(k, ph, nod=14, wing=1.0)) for k, ph in enumerate(phases())]
    g0 = figure(sp, poses, 0.62, fx=-1)
    bob = [(0, 0), (0, 0), (1, 0), (1, 1), (0, 1), (0, 0), (0, 0), (1, 0), (1, 1), (0, 1), (0, 0), (0, 0)]
    s = snout_tip(g0[0])
    x0, y0, x1, y1 = bbox(g0)
    want = (14, 13)                       # 연필 끝(입) 자리 — 몸이 판 안에 들게 당긴다
    dx = min(want[0] - s[0], 30 - x1)
    dy = max(want[1] - s[1], 2 - y0)
    dy = min(dy, 30 - y1)
    frames = []
    for k in range(N):
        bx, by = bob[k]
        g = moved(g0[k], dx + bx, dy + by)
        f = {}
        for i in range(min(k + 2, 12)):   # 쓴 줄 — 물결
            f[3 + i, 30 + (0 if i % 4 in (0, 3) else 1) - 1] = OUT
        mx, my = s[0] + dx + bx + 0.5, s[1] + dy + by + 1.6
        pencil(f, PTIP, (mx, my))
        f.update(g)
        f[PTIP] = sea.Cur(PEN_G)
        frames.append(finish({p: c for p, c in f.items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31}))
    return frames, PTIP


# ── up: 머리 위 화살표를 올려다보며 깡충 ──────────────────────────────────────────────
HOP = [0, 0, 1, 2, 3, 2, 1, 0, 0, 0, 0, 0]
CHEV_D = hx("c8642aff")
UPARROW = raster([(15.5, 0.6), (21.6, 7.0), (18.0, 7.0), (18.0, 10.4), (13.0, 10.4), (13.0, 7.0), (9.4, 7.0)])


def up(sp):
    """머리 위 굵은 위쪽 화살표를 올려다보며 깡충 — 뜰 때 눈웃음, 프테라는 날갯짓. 화살표 끝(맨 위 칸)이 핫스팟"""
    poses = [dict(mood="happy" if HOP[k] >= 2 else "blink" if k == 9 else "open",
                  kw=flair(k, ph, nod=-20, wing=-0.8 + 1.6 * (HOP[k] < 2), step=0.8 if HOP[k] else 0.0, up=1.4))
             for k, ph in enumerate(phases())]
    dinos = fit(sp, poses, (4, 14, 27, 29), kmax=0.72)
    ty = min(y for _, y in UPARROW)
    tip = sorted(x for x, y in UPARROW if y == ty)
    hot = (tip[len(tip) // 2], ty)
    frames = []
    for k in range(N):
        f = {}
        for x in range(9, 23):
            f[x, 30] = hx("2a1c2260") if HOP[k] else hx("2a1c22a0")
        f.update(moved(dinos[k], 0, -HOP[k]))
        solid(f, UPARROW, sea.Cur(CHEV), sea.Cur(CHEV_D))    # 화살표는 맨 위 · 커서
        f[hot] = sea.Cur(CHEV_D)
        frames.append(finish(f))
    return frames, hot


SCENES = {"busy": busy, "help": help_, "person": person, "pin": pin, "hand": hand, "cross": cross, "ibeam": ibeam,
          "move": move, "ns": lambda sp: stretch(sp, "ns"), "we": lambda sp: stretch(sp, "we"),
          "nwse": lambda sp: stretch(sp, "nwse"), "nesw": lambda sp: stretch(sp, "nesw"), "pen": pen, "up": up}


def center_hot(frames):
    """모든 장에서 불투명한 칸 중 판 가운데에 가장 가까운 것 (bird.center_hot 과 같다)"""
    common = set.intersection(*[{p for p, c in f.items() if c[3] == 255} for f in frames])
    return min(common, key=lambda p: (math.hypot(p[0] - 15.5, p[1] - 15.5), p))


def check14(rid, frames, hot):
    """bird.check 와 같은 검사 + 핫스팟 이웃이 아니라 핫스팟 칸 자체가 불투명인지. 경고 수를 돌려준다"""
    bad = 0
    if len(frames) != N:
        print(f"  ! {rid}: {len(frames)}장 (≠ {N})")
        bad += 1
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
            bad += 1
        if any(not (0 <= x <= 31 and 0 <= y <= 31) for x, y in f):
            print(f"  ! {rid} {i}장: 판 밖으로 나간 칸이 있음")
            bad += 1
        if hot == (1, 1) and any(c[3] == 255 and (p[0] < 1 or p[1] < 1) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 화살표 끝보다 왼쪽·위로 나온 칸이 있음")
            bad += 1
        if any(c[3] in (0xfe, 0xfd, 0xfc) for c in f.values()):
            print(f"  ! {rid} {i}장: 예약된 알파")
            bad += 1
    return bad


ROSTER = [
    ("trex", "티라노",
     "화살표 옆에 서서 짧은 팔로 날개를 잡으려다 안 닿아 버둥, 땀 삐질",
     "짧은 팔 버둥버둥, 와앙 입 벌렸다 닫음",
     "짧은 팔로 X 를 만들려다 팔이 안 닿음, 질끈 + 땀"),
    ("triceratops", "트리케라톱스",
     "화살표 오른쪽 아래에서 고개 숙여 코뿔로 날개 끝을 콕콕, 밀 때 질끈",
     "입에 문 풀을 우물우물, 꼬리 살랑",
     "뿔을 들이밀며 도리도리, 콕 숙일 때 콧김"),
    ("stego", "스테고사우루스",
     "화살표 오른쪽 아래에서 날개 끝을 킁킁, 등판이 차례로 반짝",
     "등판이 앞에서 뒤로 차례로 반짝, 별이 톡",
     "등 돌리고 꼬리 가시를 안 돼 안 돼 흔듦"),
    ("brachio", "브라키오사우루스",
     "화살표 오른쪽 아래에서 고개를 쳐들어 끝을 올려다봄",
     "목을 쭉 올려 나뭇잎 냠냠, 잎이 한 장씩 줄어듦",
     "쳐든 머리를 시계추처럼 도리도리"),
    ("ptera", "프테라노돈",
     "화살표 빗변 위에 내려앉아 날개를 폈다 접음",
     "제자리 날갯짓, 몸이 오르내림",
     "두 날개를 X 자로 엇갈려 안 돼"),
    ("ankylo", "안킬로사우루스",
     "화살표 오른쪽 아래에서 올려다보며 꼬리 곤봉 통통, 먼지 퐁",
     "꼬리 곤봉을 통통 내리치면 먼지가 퐁",
     "등 돌리고 꼬리 곤봉만 탁탁"),
    ("pachy", "파키케팔로사우루스",
     "화살표 오른쪽에서 돔 머리로 날개 끝을 콩콩, 별이 튐",
     "박치기 준비 — 고개 숙이고 땅 긁고 콧김, 앞으로 쏠림",
     "금지 빗금을 돔 머리로 콩, 별이 튐"),
    ("raptor", "랩터",
     "화살표 뒤에서 빗변을 잡고 고개 갸웃하며 빼꼼, 볏이 쫑긋",
     "고개를 갸웃 갸웃, 물음표",
     "볏을 세우고 입 벌려 캬악, 발톱 팔을 치켜듦"),
    ("spino", "스피노사우루스",
     "화살표 오른쪽 아래에서 긴 주둥이로 날개 끝 킁킁, 돛이 오르락",
     "물가에서 주둥이를 첨벙 넣어 물고기를 낚아 옴",
     "돛을 빨갛게 붉히고 고개를 홱 쳐듦(흥)"),
    ("egg", "아기공룡(알)",
     "알껍데기 모자 쓴 아기가 화살표 뒤에서 빼꼼, 모자가 들썩",
     "알껍데기에 앉아 흔들흔들하다가 모자가 퐁 뜨며 만세",
     "알 속으로 쏙 숨어 모자 닫고 알째 도리도리"),
]

SCENE = {
    "trex": (arrow_trex, wait_trex, no_trex),
    "triceratops": (arrow_tricera, wait_tricera, no_tricera),
    "stego": (arrow_stego, wait_stego, no_stego),
    "brachio": (arrow_brachio, wait_brachio, no_brachio),
    "ptera": (arrow_ptera, wait_ptera, no_ptera),
    "ankylo": (arrow_ankylo, wait_ankylo, no_ankylo),
    "pachy": (arrow_pachy, wait_pachy, no_pachy),
    "raptor": (arrow_raptor, wait_raptor, no_raptor),
    "spino": (arrow_spino, wait_spino, no_spino),
    "egg": (arrow_egg, wait_egg, no_egg),
}


def wait_hot(frames):
    """가운데(15.5, 15.5)에서 가장 가까운, 모든 장에서 불투명한 칸"""
    common = set.intersection(*[{p for p, c in f.items() if c[3] == 255} for f in frames])
    return min(common, key=lambda p: (p[0] + 0.5 - 16) ** 2 + (p[1] + 0.5 - 16) ** 2)


def check(sid, rid, frames, hot):
    bad = 0
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {sid}/{rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
            bad += 1
        if any(not (0 <= x <= 31 and 0 <= y <= 31) for x, y in f):
            print(f"  ! {sid}/{rid} {i}장: 판 밖으로 나간 칸이 있음")
            bad += 1
        if any(c[3] not in (255, 0xc7) and c not in sea.WAKE for c in f.values()):
            print(f"  ! {sid}/{rid} {i}장: 알파가 255 · c7 이 아닌 칸")
        if hot == (1, 1) and any(c[3] == 255 and (p[0] < 1 or p[1] < 1) for p, c in f.items()):
            print(f"  ! {sid}/{rid} {i}장: 화살표 끝보다 왼쪽·위로 나온 칸")
    return bad


# 화살표 칸에서 (왼쪽으로 옮길 칸, 꼬리를 치켜드는 각) — 화살표 오른쪽에 선 공룡의 꼬리 · 엉덩이가 판(0–31) 오른쪽 밖으로
# 3–4칸 잘려 나가서 들였다. 옮기기만 하면 6칸이 들어야 해 화살표를 덮고, 꼬리만 들면 엉덩이가 남는다
ARROW_FIT = {"trex": (-3, -60), "triceratops": (-2, -75), "stego": (-3, -40), "brachio": (-2, -40), "ankylo": (-3, -30),
             "pachy": (-1, -60), "spino": (-2, -40)}
# 옮긴 공룡 얼굴이 화살표 오른쪽 테를 장당 0–6칸 누른다. 화살표를 공룡 위에 다시 찍어 보니 공룡 눈이 가려져서 버렸다


# 매끈한 모양에서 공룡을 붙들 빗변 자리(끝 0 … 날개 1) — 선 공룡은 날개 끝, 프테라는 빗변에 앉은 자리
EDGE_T = {"ptera": 0.87}
PEEKERS = ("raptor", "egg")   # sea.peek 틀(화살표 뒤 빼꼼)이라 냥이와 같은 재료(write_peek)를 쓴다


def run(sid, only=None):
    """only 가 있으면 그 칸만 그린다(--cells). → (마리, 14칸 경고 수)"""
    global SHIFT, TAIL_UP, BARE
    d = ART / f"{sid}anim"
    d.mkdir(parents=True, exist_ok=True)
    for rid, fn in zip(("arrow", "wait", "no"), SCENE[sid]):
        if only and rid not in only:
            continue
        SHIFT, TAIL_UP = ARROW_FIT.get(sid, (0.0, 0.0)) if rid == "arrow" else (0.0, 0.0)
        sea.PEEKS.clear()
        frames = fn()
        if rid == "arrow" and sid not in PEEKERS:   # 화살표 없이 한 번 더 — 매끈한 모양은 새 화살표 위에 이 공룡을 얹는다
            BARE = True
            bare = [{p: c for p, c in f.items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31} for f in fn()]
            BARE = False
        SHIFT = TAIL_UP = 0.0
        frames = [{p: c for p, c in f.items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31} for f in frames]
        hot = (1, 1) if rid == "arrow" else (15, 15) if rid == "no" else wait_hot(frames)
        check(sid, rid, frames, hot)
        # 칸마다(커서가 없는 칸도) mark — 커서는 파랑 끝 비트 홀수, 공룡은 짝수(schemes.json "hue": "both")
        (d / f"{rid}.txt").write_text(shape.to_text(sea.mark(frames), hot, RATE), encoding="utf-8")
        if rid == "arrow" and sid in PEEKERS:
            sea.write_peek(d)
        elif rid == "arrow":   # 기본 그림처럼 공룡이 화살표 위 (over)
            sea.write_anchor(d, bare, PEEK_S, OUT, dict(anchor="edge", t=EDGE_T.get(sid, 1.0), over=True))
    bad = 0
    for rid, fn in SCENES.items():
        if only and rid not in only:
            continue
        frames, hot = fn(sid)
        frames = [{p: c for p, c in f.items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31} for f in frames]
        hot = hot or center_hot(frames)
        bad += check14(f"{sid}/{rid}", frames, hot)
        (d / f"{rid}.txt").write_text(shape.to_text(sea.mark(frames), hot, RATE), encoding="utf-8")
    return sid, bad


def main():
    args = sys.argv[1:]
    only = None
    if "--cells" in args:     # 몇 칸만 다시 그리기 — --cells hand,up
        i = args.index("--cells")
        only = set(args[i + 1].split(","))
        del args[i:i + 2]
    ids = args or [r[0] for r in ROSTER]
    from concurrent.futures import ProcessPoolExecutor
    from functools import partial
    bad = 0
    with ProcessPoolExecutor() as ex:
        for sid, b in ex.map(partial(run, only=only), ids):
            bad += b
            print("done", sid)
    print(f"경고 {bad}개")


if __name__ == "__main__":
    main()

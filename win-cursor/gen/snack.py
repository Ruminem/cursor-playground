# SPDX-License-Identifier: Apache-2.0
"""말랑 간식 · 애니 — 얼굴 달린 간식 10종의 17칸.

  python gen/snack.py [마리...] [--cells 칸,칸]   art/<마리>anim/<칸>.txt 를 쓴다 (안 주면 10종 전부)

냥이 · 애니 옆에 놓을 한 벌. 간식마다 생김새(실루엣 + 색)가 다르고 칸마다 그 간식이 하는 짓을 따로 그린다.
얼굴은 다 같은 틀(점 눈 · 볼터치 · 작은 입)이라 한 식구로 읽히고, 테두리(따뜻한 갈색)와 반투명 테(크림)도 하나로 맞춘다.
그리개(Rig · draw · ell · bar …)는 gen/cheesecat.py 에서 옮겨 왔다 — 그쪽 draw 는 제 OUT 을 쓰므로 가져다 쓰지 않는다.

  arrow   1.5배 흰 화살표(sea.peek 와 같은 꼴, 끝이 핫스팟 (1, 1))를 간식마다 제 식으로 갖고 논다
  wait    간식마다 제 대기 동작. 가운데 근처 불투명 칸이 핫스팟
  no      빨간 금지 표지 안에서 간식마다 제 식으로 거절한다. 핫스팟 (15, 15)
"""
import math
import sys

import sea  # noqa: E402
import shape  # noqa: E402
from sea import N, RATE, SIGN, SIGN_D, PEEK_CUR, PEEK_WHITE, disc, finish, hx, ink, inside, raster, solid  # noqa: E402

ART = sea.WIN / "art"

OUT, EYE, HI = hx("4a3028ff"), hx("3a2420ff"), hx("ffffffff")
RIM = hx("f6e9d2c7")
ink(OUT, HI, RIM)
BLUSH, MOUTH, TEAR = hx("f59aa6ff"), hx("c0484cff"), hx("8cc8f0ff")
STEAM = hx("c8d2dcff")      # 김 — 테를 안 두르고 맨 위에 찍는다

# 간식 색
CUSTARD, CUSTARD_L, CUSTARD_D = hx("f8d66aff"), hx("fce79cff"), hx("e6b444ff")
CARAMEL, CARAMEL_L = hx("8e4e22ff"), hx("b8702eff")
CHERRY, STEM = hx("e0384cff"), hx("5c8a3aff")
PLATE, PLATE_D = hx("eef2f8ff"), hx("bcc8d8ff")
MAC, MAC_L, MAC_D, CREAM = hx("f4a2c0ff"), hx("fac8daff"), hx("d97898ff"), hx("fff6e6ff")
GOLD, GOLD_L, GOLD_D, ANKO, BATTER = hx("e8a848ff"), hx("f6cc7aff"), hx("c27a2aff"), hx("7a3430ff"), hx("f6e4b4ff")
MOLD, MOLD_L = hx("4e4e58ff"), hx("74747fff")
ICING, ICING_L, DOUGH, DOUGH_D = hx("f57ba6ff"), hx("fbaac6ff"), hx("dda066ff"), hx("b87a44ff")
SPRINK = (hx("ffe066ff"), hx("6ec6f0ff"), hx("ffffffff"), hx("8cd67aff"))
MOCHI, MOCHI_D, MOCHI_P = hx("fdfaf6ff"), hx("e6dfd8ff"), hx("f2c8d0ff")
BERRY, LEAF = hx("e8485aff"), hx("6aa848ff")
WAFFLE, WAFFLE_D = hx("e6a654ff"), hx("b87830ff")
MINT, MINT_D, CHIP = hx("a2e4c8ff"), hx("72c4a4ff"), hx("5a3a2aff")
STRAW, STRAW_L = hx("f7a8bcff"), hx("fcd0dcff")
GUM, GUM_L, GUM_D = hx("e8364aff"), hx("ff8090ff"), hx("b01e34ff")
RICE, RICE_D, GRAIN = hx("fefdf8ff"), hx("e6e3dcff"), hx("eeebe2ff")
NORI, NORI_L = hx("27332dff"), hx("43544aff")
MANDU, MANDU_D, PLEAT = hx("f7eedcff"), hx("e4d6bcff"), hx("d4c09cff")
TAKO, TAKO_D, SAUCE, MAYO = hx("cc8640ff"), hx("9e5e2aff"), hx("5e2e1aff"), hx("fff2c8ff")
AONORI, KATSUO, KATSUO_D, WOOD = hx("6a9a3aff"), hx("f0b898ff"), hx("c88a6eff"), hx("e8c890ff")
PAN, PAN_L = hx("3e3e46ff"), hx("62626cff")


# ── 그리개 (gen/cheesecat.py 에서 옮김) ──────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도) · 배율 k. ang=0 이면 u 가 오른쪽, w 가 아래. ang 만큼 시계 방향으로 돈다"""

    def __init__(self, ox: float, oy: float, ang: float = 0.0, k: float = 1.0):
        t = math.radians(ang)
        self.ox, self.oy, self.c, self.s, self.k = ox, oy, math.cos(t), math.sin(t), k

    def world(self, a: float, b: float) -> tuple:
        return self.ox + (a * self.c - b * self.s) * self.k, self.oy + (a * self.s + b * self.c) * self.k

    def local(self, x: float, y: float) -> tuple:
        dx, dy = (x - self.ox) / self.k, (y - self.oy) / self.k
        return dx * self.c + dy * self.s, -dx * self.s + dy * self.c

    def cell(self, a: float, b: float) -> tuple:
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
    """p0 → p1 막대. 굵기(반지름)가 r0 → r1 로 변하고 두 끝이 둥글다"""
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


def rpoly(pts, r):
    """모서리가 둥근 다각형 — 꼭짓점 pts(안쪽으로 줄인 것) 둘레를 반지름 r 로 부풀린다"""
    return any_of(tri(*pts), *[bar(p, q, r) for p, q in zip(pts, pts[1:] + pts[:1])])


def xf(h, ang=0.0, piv=(0.0, 0.0), dx=0.0, dy=0.0, sx=1.0, sy=1.0):
    """부위 하나만 piv 둘레로 ang(라디안, 시계 방향) 돌리고 (sx, sy) 늘이고 (dx, dy) 옮긴다. h 는 맞음·색 함수, 색 상수면 그대로"""
    if not callable(h):
        return h
    c, s = math.cos(ang), math.sin(ang)

    def g(a, b):
        a, b = a - dx - piv[0], b - dy - piv[1]
        a, b = a * c + b * s, -a * s + b * c
        return h(a / sx + piv[0], b / sy + piv[1])
    return g


def fw(p, ang=0.0, piv=(0.0, 0.0), dx=0.0, dy=0.0, sx=1.0, sy=1.0):
    """xf 의 정방향 — 부위 제 좌표의 점이 옮긴 뒤 어디인지"""
    a, b = (p[0] - piv[0]) * sx, (p[1] - piv[1]) * sy
    c, s = math.cos(ang), math.sin(ang)
    return piv[0] + a * c - b * s + dx, piv[1] + a * s + b * c + dy


def part_xf(p, **kw):
    return (p[0], xf(p[1], **kw), xf(p[2], **kw), p[3])


def draw(rig: Rig, parts: list) -> tuple[dict, set, dict]:
    """parts: [(이름, 맞음(a, b), 색(a, b) 또는 색, 테두리)] — 앞의 것이 위에 그려진다 (cheesecat.draw 그대로)"""
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


# ── 얼굴: 점 눈 · 볼터치 · 작은 입 (간식 열 다 같은 틀) ───────────────────────────
def face(f: dict, rig: Rig, at, g=2, mood="open", mouth="smile", small=False, blush=True, keep=None):
    """at(제 좌표)이 얼굴 가운데. 눈은 축 cx 를 두고 좌우 대칭(오른눈 안쪽 칸이 cx+g). keep 을 주면 그 칸에만 찍는다"""
    x, y = rig.world(*at)
    cx, cy = round(x), math.floor(y)
    big = not small
    eye = {
        "open": [(0, -1), (1, -1), (0, 0), (1, 0)] if big else [(0, -1), (0, 0)],
        "blink": [(0, 0), (1, 0)] if big else [(0, 0)],
        "happy": [(0, 0), (1, -1), (2, 0)] if big else [(-1, 0), (0, -1), (1, 0)],
        "squeeze": [(1, -1), (0, 0), (1, 1)],
        "mad": [(0, -1), (1, -1), (0, 0), (1, 0), (0, -2), (1, -3)] if big else [(0, -1), (0, 0), (0, -2), (1, -3)],
        "cry": [(0, -1), (1, -1), (0, 0), (1, 0)] if big else [(0, -1), (0, 0)],
        "sleep": [(0, 0), (1, 0), (2, -1)] if big else [(0, 0), (1, -1)],
    }[mood]
    pix = {}
    b0 = cx + g
    for dx_, dy_ in eye:
        pix[b0 + dx_, cy + dy_] = EYE
        pix[2 * cx - 1 - (b0 + dx_), cy + dy_] = EYE
    if mood in ("open", "cry") and big:
        pix[b0, cy - 1] = HI
        pix[cx - g - 2, cy - 1] = HI
    if mood == "cry":
        w = 1 if big else 0
        for dy_ in (1, 2):
            pix[b0 + w, cy + dy_] = TEAR
            pix[cx - g - 1 - w, cy + dy_] = TEAR
    if blush:
        for xx in ((cx - g - 3, cx - g - 2) if big else (cx - g - 2,)):
            pix.setdefault((xx, cy + 1), BLUSH)
            pix.setdefault((2 * cx - 1 - xx, cy + 1), BLUSH)
    m = {
        "smile": [(-2, 1), (-1, 2), (0, 2), (1, 1)],
        "flat": [(-1, 2), (0, 2)],
        "frown": [(-2, 2), (-1, 1), (0, 1), (1, 2)],
        "wavy": [(-2, 2), (-1, 1), (0, 2), (1, 1)],
        "o": [(-1, 1), (0, 1), (-1, 2), (0, 2)],
        "yawn": [(-1, 1), (0, 1), (-1, 2), (0, 2), (-1, 3), (0, 3)],
        "dot": [(-1, 1), (0, 1)],
        "none": [],
    }[mouth]
    mc = MOUTH if mouth in ("o", "yawn", "dot") else EYE
    for dx_, dy_ in m:
        pix[cx + dx_, cy + dy_] = mc
    for p, c in pix.items():
        if keep is None or p in keep:
            f[p] = c


def steam(f: dict, x: int, y: int, k: int, h: int = 5, ph: int = 0) -> None:
    """모락모락 김 한 가닥 — 아래 (x, y) 에서 위로 h 칸, 장마다 물결이 위로 흐른다"""
    for i in range(h):
        if (i + k + ph) % 4 == 3:
            continue
        f[x + round(math.sin((i - k - ph) * 1.1)), y - i] = STEAM


def sparkle(f: dict, x: int, y: int, c=HI) -> None:
    for p in ((x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
        f[p] = c


def lines(f: dict, pts) -> None:
    for p in pts:
        f[p] = OUT


# ── 간식 열 종 (제 좌표: 너비 16 안팎, 가운데가 원점) ─────────────────────────────
def pudding(rig, sh=0.0, sq=0.0, mood="open", mouth="smile", plate=False, cherry_dy=0.0, cherry=True, small=False):
    """노란 몸 · 갈색 캐러멜 모자 · 체리. sh 는 꼭대기가 옆으로 쏠린 칸 수(출렁), sq 는 위가 눌린 정도"""
    top = -5.0 + sq

    def W(a, b):
        return a - sh * (5.4 - b) / 10.4

    body = rpoly([(-4.2, top + 1.0), (4.2, top + 1.0), (6.0, 4.4), (-6.0, 4.4)], 1.0)

    def col(a, b):
        u = W(a, b)
        if b < top + 2.6 + 0.7 * math.sin(u * 1.6 + 0.4):
            return CARAMEL_L if u < -1.8 and b < top + 1.2 else CARAMEL
        if u > 3.6:
            return CUSTARD_D
        if u < -3.4 and b < 2.0:
            return CUSTARD_L
        return CUSTARD
    cx_ = sh * (5.4 - (top - 1.0)) / 10.4
    parts = []
    if cherry:
        cy_ = top - 1.0 + cherry_dy
        parts += [("stem", bar((cx_ + 0.3, cy_ - 1.2), (cx_ + 1.8, cy_ - 3.6), 0.5), STEM, False),
                  ("cherry", ell(cx_, cy_, 1.8, 1.7), lambda a, b: HI if a < cx_ - 0.5 and b < cy_ - 0.6 else CHERRY, True)]
    parts.append(("body", lambda a, b: body(W(a, b), b), col, True))
    if plate:
        parts.append(("plate", ell(0, 5.2, 9.4, 1.8), lambda a, b: PLATE_D if b > 5.9 else PLATE, False))
    f, mask, reg = draw(rig, parts)
    face(f, rig, (sh * (5.4 - 1.2) / 10.4, 1.2), 1 if small else 2, mood, mouth, small)
    return f, mask, reg


def macaron(rig, ang=0.0, lift=0.0, squeeze=0.0, mood="open", mouth="smile", small=False):
    """분홍 꼬끄 두 장 사이 크림. ang 은 위 꼬끄가 오른쪽 경첩으로 벌어진 각(라디안), lift 는 위로 들린 칸 수"""
    piv = (6.6, -0.4)

    def shell(cb, upper):
        def col(a, b):
            edge = b > cb + 2.6 if upper else b < cb - 2.2
            if edge:   # 꼬끄 밑동의 오돌토돌한 피에
                return MAC_D if math.floor(a * 1.4) % 2 else MAC
            if upper and a < -3.4 and b < cb - 1.8:
                return MAC_L
            return MAC
        return (ell(0, cb, 7.6, 4.0), col) if upper else (ell(0, cb, 7.4, 3.2), col)
    th, tc = shell(-3.8, True)
    bh, bc = shell(3.4, False)
    tk = dict(ang=-ang, piv=piv, dy=-lift)
    cw = 6.4 + squeeze - lift * 0.5
    parts = [("top", xf(th, **tk), xf(tc, **tk), True),
             ("cream", ell(0, -0.2 - lift * 0.5, cw, 1.5 + lift * 0.5), CREAM, False),
             ("bot", bh, bc, False)]
    f, mask, reg = draw(rig, parts)
    fc = fw((0, -3.4), **tk)
    face(f, rig, fc, 1 if small else 2, mood, mouth, small)
    return f, mask, reg


def fish(rig, bite=False, done=1.0, mood="open", mouth="smile", tail_sw=0.0, chomp=False):
    """옆모습 붕어빵(왼쪽을 본다) — 금갈색, 비늘 무늬, 아가미 줄, 지느러미. bite 면 꼬리째 베어 먹혀 팥이 보인다"""
    def mix(c, t):
        return tuple(round(BATTER[i] + (c[i] - BATTER[i]) * t) for i in range(3)) + (255,)
    G, GL, GD = mix(GOLD, done), mix(GOLD_L, done), mix(GOLD_D, done)
    bites = [(8.0, -3.2, 2.8), (6.6, 0.6, 2.4), (7.8, 4.2, 2.8), (10.0, 0.0, 3.6)]

    def bitten(a, b):
        return bite and any((a - x) ** 2 + (b - y) ** 2 <= r * r for x, y, r in bites)
    body = any_of(ell(0, 0, 7.6, 5.0), ell(-3.6, 0.3, 4.4, 4.6))
    tail = lambda a, b: inside([(5.6, 0), (11.6, -5 + tail_sw), (10.4, tail_sw), (11.6, 5 + tail_sw)], a, b)
    dorsal = tri((-1.6, -4.0), (3.6, -6.6), (5.4, -3.2))
    belly = tri((0.4, 4.0), (3.8, 6.4), (4.6, 3.6))

    def skin(a, b):
        if bite and any(r * r <= (a - x) ** 2 + (b - y) ** 2 <= (r + 2.4) ** 2 for x, y, r in bites):
            return ANKO
        if abs(math.hypot(a + 7.0, b) - 4.4) < 0.45 and abs(b) < 3.4:
            return GD
        if a > -2.0:
            row = math.floor((b + 6) / 2.2)
            u = (a + 2 + (1.2 if row % 2 else 0)) % 2.4
            v = (b + 6) % 2.2
            if v > 1.4 and 0.4 < u < 2.0:
                return GD
        if b < -2.6 and a < 1:
            return GL
        return G

    def fin(a, b):
        return GD if (a * 0.8 + b) % 1.6 < 0.6 else G
    parts = [("body", lambda a, b: body(a, b) and not bitten(a, b), skin, True)]
    if not bite:
        parts.append(("tail", tail, fin, False))
    parts += [("dorsal", lambda a, b: dorsal(a, b) and not bitten(a, b), fin, False),
              ("belly", belly, fin, False)]
    f, mask, reg = draw(rig, parts)
    ex, ey = rig.world(-4.4, -1.2)
    x0, y0 = round(ex) - 1, math.floor(ey)
    if mood in ("open", "cry"):
        for p in ((x0, y0 - 1), (x0 + 1, y0 - 1), (x0, y0), (x0 + 1, y0)):
            f[p] = EYE
        f[x0, y0 - 1] = HI
        if mood == "cry":
            f[x0 + 1, y0 + 1] = TEAR
            f[x0 + 1, y0 + 2] = TEAR
    elif mood == "happy":
        for p in ((x0 - 1, y0), (x0, y0 - 1), (x0 + 1, y0 - 1), (x0 + 2, y0)):
            f[p] = EYE
    else:
        f[x0, y0] = EYE
        f[x0 + 1, y0] = EYE
    bx, by = rig.cell(-3.0, 1.6)
    f[bx, by] = BLUSH
    f[bx + 1, by] = BLUSH
    mx, my = rig.cell(-6.6, 1.2)
    if chomp or mouth == "o":
        f[mx, my] = MOUTH
        f[mx, my + 1] = MOUTH
    else:
        f[mx, my] = EYE
        f[mx + 1, my + 1] = EYE
    return f, mask, reg


SPR = [(-4.6, -3.2, 0), (-1.6, -5.6, 1), (2.6, -5.0, 2), (5.0, -2.4, 3), (-5.8, 0.0, 1), (3.0, -3.0, 0),
       (-3.0, -1.6, 3), (5.6, 0.6, 1), (0.4, -4.2, 3), (-2.8, -5.0, 2)]


def donut(rig, mood="open", mouth="smile", small=False, keep_face=True):
    """분홍 아이싱 · 스프링클 · 가운데 구멍. 얼굴은 구멍 아래 반죽 자리"""
    def ring(a, b):
        r2 = a * a + b * b
        return r2 <= 7.4 ** 2 and r2 > 2.4 ** 2

    def col(a, b):
        r = math.hypot(a, b)
        if b < 0.4 + 1.0 * math.sin(a * 1.3 + 0.3) and r < 6.9:
            for u, w, c in SPR:
                if abs(a - u) < 0.6 and abs(b - w) < 0.5:
                    return SPRINK[c]
            return ICING_L if (a < -3 and b < -3) or (r < 3.4 and b < 0) else ICING
        return DOUGH_D if r > 6.0 and b > 2.5 else DOUGH
    f, mask, reg = draw(rig, [("ring", ring, col, False)])
    if keep_face:
        face(f, rig, (0, 2.9), 2 if small else 3, mood, mouth, small)
    return f, mask, reg


def mochi(rig, sx=1.0, sy=1.0, mood="open", mouth="smile", berry=True, small=False):
    """하얀 찹쌀떡 — 아래가 넓게 퍼진 말랑 덩어리, 꼭대기에 딸기 끝이 빼꼼. (sx, sy) 로 바닥을 두고 늘었다 줄었다"""
    base = any_of(ell(0, 0.4, 7.4, 5.4), ell(0, 3.0, 8.4, 2.8))
    floor_ = 5.6
    k = dict(piv=(0, floor_), sx=sx, sy=sy)

    def col(a, b):
        if b > 3.8 or a > 5.4:
            return MOCHI_D
        if (math.floor(a * 1.5) * 7 + math.floor(b * 1.5) * 13) % 29 == 0:
            return MOCHI_P
        return MOCHI
    parts = []
    if berry:
        bt = fw((1.8, -5.0), **k)
        parts += [("leaf", any_of(ell(bt[0] - 1.0, bt[1] - 1.6, 1.4, 0.7, -0.5), ell(bt[0] + 1.0, bt[1] - 1.6, 1.4, 0.7, 0.5)),
                   LEAF, False),
                  ("berry", ell(bt[0], bt[1], 1.8, 1.6), lambda a, b: hx("ffe9a0ff") if (math.floor(a * 1.4) + math.floor(b * 1.4)) % 3 == 0 else BERRY, True)]
    parts.append(("mochi", xf(base, **k), xf(col, **k), False))
    f, mask, reg = draw(rig, parts)
    face(f, rig, fw((0, 1.0), **k), 1 if small else 2, mood, mouth, small)
    return f, mask, reg


def icecream(rig, mood="open", mouth="smile", drips=(0.0, 0.0, 0.0), sink=0.0, cone_front=False, small=False, tilt=0.0):
    """콘 위 민트(초코칩) · 딸기 두 스쿱. drips 는 민트가 녹아 흐른 길이 셋, sink 는 스쿱이 콘 안으로 숨은 칸 수"""
    sk = dict(dy=sink)
    s2 = ("s2", xf(ell(0, -8.4, 4.6, 3.8), **sk),
          xf(lambda a, b: STRAW_L if a < -1.6 and b < -9.6 else STRAW, **sk), True)
    dr = [bar((x, 0.6), (x, 0.6 + d), 0.9) for x, d in zip((-3.4, 0.6, 3.2), drips) if d > 0]
    mint_hit = any_of(ell(0, -2.6, 5.6, 4.0), *[ell(x, 0.4, 1.3, 1.1) for x in (-4.0, -1.6, 1.0, 3.6)], *dr)

    def mint_col(a, b):
        if ((round(a * 2) * 5 + round(b * 2) * 3) % 11 == 0) and b < -0.5 and abs(a) > 3.4:
            return CHIP
        return MINT_D if a > 3.4 or b > 0.4 else MINT
    s1 = ("s1", xf(mint_hit, **sk), xf(mint_col, **sk), True)
    cone_hit = rpoly([(-4.0, 0.6), (4.0, 0.6), (0, 11.0)], 0.8)

    def cone_col(a, b):
        if b < 1.6:
            return WAFFLE_D
        return WAFFLE_D if (a + b) % 2.6 < 0.6 or (a - b) % 2.6 < 0.6 else WAFFLE
    cone = ("cone", cone_hit, cone_col, True)
    parts = [cone, s1, s2] if cone_front else [s1, s2, cone]
    if tilt:
        parts = [part_xf(p, ang=tilt, piv=(0, 11.0)) for p in parts]
    f, mask, reg = draw(rig, parts)
    at = fw((0, -2.6 + sink), ang=tilt, piv=(0, 11.0))
    keep = {p for p in mask if reg[p] == "s1"} if cone_front else None
    face(f, rig, at, 1, mood, mouth, small, keep=keep)
    return f, mask, reg


def gummy(rig, mood="open", mouth="smile", arms=(0.8, 0.8), sq=0.0, legs=0.0, small=False, sit=False, tilt=0.0,
          ears=True):
    """빨간 젤리곰 앞모습 — 하리보처럼 통통한 머리·몸통 덩어리에 뭉툭한 혹 팔다리. 왼쪽 위 밝은 띠와 흰 반짝으로 투명감.
    팔다리는 몸통 높이(10)의 1/4 안쪽만 삐져나온다(팔 2.2 · 다리 1.3, 2026-10-09 "진짜 하리보처럼 짧게").
    arms: (왼, 오) 팔 혹이 가리키는 각(라디안, 0 아래 · 0.8 쉬는 꼴 · 2.4 만세 · 음수면 배 쪽으로 모음).
    legs: 두 발 덩이를 위아래로 엇갈리게(동동). sit 이면 발 덩이를 조금 벌려 앉은 꼴. tilt 는 발밑을 축으로 몸 전체 기울기"""
    def shade(c0, c1, r):
        def col(a, b):
            u, v = (a - c0) / r, (b - c1) / r
            if u < -0.5 and v < 0.1:
                return GUM_L
            if u > 0.6 and v > 0.1:
                return GUM_D
            return GUM
        return col
    k = dict(ang=tilt, piv=(0, 9.0), sx=1 + sq * 0.25, sy=1 - sq * 0.2)
    fx = 2.9 if sit else 2.5
    lg = [ell(-fx, 7.6 - legs, 2.3, 1.8), ell(fx, 7.6 + legs, 2.3, 1.8)]
    parts = [("muzzle", ell(0, -2.9, 2.2, 1.4), GUM_L, False),
             ("head", ell(0, -5.0, 5.2, 4.7), shade(0, -5.0, 5.2), True),
             ("ears", any_of(ell(-3.8, -9.2, 1.9, 1.9), ell(3.8, -9.2, 1.9, 1.9)) if ears else (lambda a, b: False), GUM,
              False)]
    for i, (side, th) in enumerate(zip((-1, 1), arms)):   # 어깨에서 1.4 만 뻗은 혹
        s = (4.0 * side, 0.8)
        h = (s[0] + side * 1.4 * math.sin(th), s[1] + 1.4 * math.cos(th))
        parts.append((f"arm{i}", bar(s, h, 1.5), GUM, True))
    parts += [("legs", any_of(*lg), GUM, True),
              ("body", ell(0, 3.0, 4.9, 5.0), lambda a, b: GUM_L if a * a / 5 + (b - 3.0) ** 2 / 7 < 1 else shade(0, 2.8, 4.5)(a, b), False)]
    parts = [part_xf(p, **k) for p in parts]
    f, mask, reg = draw(rig, parts)
    for u, w, part in ((-3.2, -7.6, "head"), (-2.4, -8.0, "head"), (-2.4, 1.6, "body")):   # 흰 반짝(젤리 광택)
        p = rig.cell(*fw((u, w), **k))
        if reg.get(p) == part and f[p] != OUT:
            f[p] = HI
    face(f, rig, fw((0, -5.0), **k), 1 if small else 2, mood, mouth, small)
    return f, mask, reg


def onigiri(rig, mood="open", mouth="smile", nori=(1.6, 9.0, 1.0), small=False, face_on=True):
    """흰 세모 주먹밥 + 김 띠. nori=(위, 아래, 감긴 비율) — 띠는 왼쪽부터 감긴다"""
    hit = rpoly([(0, -7.0), (6.8, 5.0), (-6.8, 5.0)], 2.0)
    n0, n1, fr = nori

    def col(a, b):
        if n0 <= b <= n1 and -4.2 <= a <= -4.2 + 8.4 * fr:
            return NORI_L if a < -3.2 or b < n0 + 0.8 else NORI
        if (math.floor(a * 1.6) * 5 + math.floor(b * 1.6) * 11) % 17 == 0:
            return GRAIN
        return RICE_D if a > 4.4 or b > 5.4 else RICE
    f, mask, reg = draw(rig, [("rice", hit, col, False)])
    if face_on:
        face(f, rig, (0, -1.4), 1 if small else 2, mood, mouth, small)
    return f, mask, reg


def mandu(rig, mood="open", mouth="smile", small=False, puff=0.0):
    """주름 잡힌 만두 — 반달 몸 위로 주름 볏이 솟는다. puff 는 볼이 부푼 정도"""
    body = any_of(ell(0, 1.6, 8.4 + puff, 4.8 + puff * 0.4), ell(0, -1.2, 6.4 + puff, 4.4))
    crest = any_of(*[ell(i * 2.3, -5.2 + 0.4 * abs(i), 1.3, 1.7) for i in range(-2, 3)])

    def col(a, b):
        if b < -2.2 and (a + 1.15) % 2.3 < 0.6:
            return PLEAT
        if b > 4.4 or a > 6.4:
            return MANDU_D
        return MANDU
    f, mask, reg = draw(rig, [("crest", crest, col, False), ("body", body, col, False)])
    face(f, rig, (0, 1.4), 1 if small else 2, mood, mouth, small)
    return f, mask, reg


def takoyaki(rig, k=0, mood="open", mouth="smile", pick=True, small=False, roll=0.0):
    """동그란 타코야키 — 소스 모자 · 마요 지그재그 · 파래 점 · 춤추는 가쓰오부시 · 꽂힌 이쑤시개. roll 은 공이 구른 각(라디안)"""
    rk = dict(ang=roll)

    def col(a, b):
        top = -1.2 + 0.8 * math.sin(a * 1.4)
        if b < top:
            zig = -3.0 + 1.4 * (abs(((a + 6) % 2.4) - 1.2) - 0.6)
            if abs(b - zig) < 0.45:
                return MAYO
            if (math.floor(a * 1.3) * 7 + math.floor(b * 1.3) * 3) % 13 == 0:
                return AONORI
            return SAUCE
        return TAKO_D if b > 3.6 or a > 4.8 else TAKO
    parts = []
    if pick:
        parts.append(("pick", xf(bar((2.4, -3.0), (6.4, -11.0), 0.6), **rk), WOOD, False))
    parts.append(("ball", ell(0, 0, 6.8, 6.4), xf(col, **rk), False))
    f, mask, reg = draw(rig, parts)
    for i, (u, w) in enumerate(((-3.0, -5.4), (1.2, -6.0))):   # 가쓰오부시 — 소스 위에 누운 얇은 조각이 장마다 들썩
        x, y = rig.cell(*fw((u, w), **rk))
        up = 1 if (k + i * 3) % 6 < 3 else 0
        for p, c in (((x, y - up), KATSUO), ((x + 1, y), KATSUO_D), ((x + 2, y - up), KATSUO)):
            f[p] = c
    face(f, rig, fw((0, 2.0), **rk), 1 if small else 2, mood, mouth, small)
    return f, mask, reg


# ── 화살표 ───────────────────────────────────────────────────────────────────
AS = 1.5   # 화살표 배율 — sea.peek 의 1.6 보다 조금 작게 해 간식을 키울 자리를 낸다 (간식이 작다는 말, 2026-10-09)
ARROW_M = raster([(1 + x * AS, 1 + y * AS) for x, y in PEEK_CUR])
LX, LY = 11.6 * AS, 11.0 * AS                       # 빗변: (1,1) → (1+LX, 1+LY)
NX, NY = LY / math.hypot(LX, LY), -LX / math.hypot(LX, LY)
WING = (1 + LX, 1 + LY)                              # 날개 끝


def arrow_layer(f: dict) -> None:
    solid(f, ARROW_M, sea.Cur(PEEK_WHITE), sea.Cur(OUT))   # 화살표는 커서 — 쓸 때 sea.mark 가 파랑 맨 끝 비트로 간식과 가른다
    f[1, 1] = sea.Cur(OUT)


def hyp(t, lift=0.0):
    return 1 + LX * t + NX * lift, 1 + LY * t + NY * lift


def above_hyp(p) -> bool:
    """칸이 빗변 위(오른쪽 위)에 있나"""
    x, y = p[0] + 0.5, p[1] + 0.5
    return (x - 1) * LY - (y - 1) * LX > 0


ARROW_SHADE = hx("d9c6aeff")   # 흰 간식이 화살표에 드리운 그림자 한 줄 — 화살표 바탕색은 그대로 두고 맞닿은 칸만


def apart(f: dict, shown: set, tint: dict) -> None:
    """흰 몸 간식(찹쌀떡·만두)이 흰 화살표와 한 덩어리로 읽히지 않게 가른다 (2026-10-09 사용자 말).
    ① 몸 칸이 화살표(흰 칸·테)와 맞닿으면 그 몸 칸을 테로 — 화살표 테 + 몸 테 두 줄이 된다
    ② 몸에 닿은 화살표 흰 칸은 그림자 한 줄로 ③ 몸 색은 tint 로 바꿔(연분홍·콩가루, 따뜻한 크림) 흰 화살표와 다른 색으로"""
    arrowish = {p for p, c in f.items() if p not in shown and c in (PEEK_WHITE, OUT)}
    nb4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
    for p in shown:
        if f[p] in tint:
            f[p] = tint[f[p]]
    for p in shown:
        if f[p] != OUT and any((p[0] + dx, p[1] + dy) in arrowish for dx, dy in nb4):
            f[p] = OUT
    for p in arrowish:
        if f[p] == PEEK_WHITE and any((p[0] + dx, p[1] + dy) in shown for dx, dy in nb4):
            f[p] = sea.Cur(ARROW_SHADE)   # 그림자가 진 화살표 칸도 화살표(커서)


def arrow_scene(k, ph, who):
    sw = math.sin(ph)
    f = {}
    if who == "pudding":
        # 화살표 뒤에 숨어 빗변 위로 빼꼼 출렁 — sea.peek 틀을 따르되 발끝 없이(푸딩은 발이 없다)
        lift = sea.peek_lift(k) + 1.0
        x, y = hyp(sea.PEEK_T, lift)
        g, _, _ = pudding(Rig(x + 0.6, y + 0.2, 0, 1.0), sh=1.3 * sw, sq=0.4 * math.sin(2 * ph),
                          mood="blink" if k == 7 else "happy" if k in (3, 4) else "open")
        f.update({p: c for p, c in g.items() if p[0] >= 1 and p[1] >= 1})
        arrow_layer(f)
        return f
    if who == "macaron":   # 날개 끝을 앙 — 위 꼬끄가 벌렸다 다물었다
        arrow_layer(f)
        op = [0.0, 0.15, 0.3, 0.42, 0.5, 0.42, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0][k]
        g, _, _ = macaron(Rig(WING[0] + 5.6, WING[1] - 0.6, 0, 0.88), ang=op,
                          mood="squeeze" if k in (7, 8) else "open", mouth="o" if op > 0.2 else "smile")
        f.update(g)
        return f
    if who == "bungeoppang":   # 빗변을 냠냠 갉아 먹으며 부스러기
        arrow_layer(f)
        nib = [0, 0.4, 0.8, 0.4, 0, 0, 0.4, 0.8, 0.4, 0, 0, 0][k]
        g, _, _ = fish(Rig(21.4 - nib, 12.2 + 0.4 * sw, -8, 0.84), tail_sw=1.6 * math.sin(2 * ph), chomp=nib > 0.5,
                       mood="happy" if k in (4, 5) else "open")
        f.update(g)
        if k in (2, 3, 7, 8):
            for p in ((12, 16 + (k % 5)), (14, 19 + (k % 5) // 2)):
                f.setdefault(p, GOLD_D)
        return f
    if who == "donut":   # 고리 던지기 — 날개 끝에 걸려 대롱대롱
        arrow_layer(f)
        a = 14 * math.sin(ph)
        rig = Rig(WING[0] - 0.4, WING[1] - 0.6, a, 0.78)
        rig.ox, rig.oy = rig.world(0, 2.0)[0] - 0 * 0, rig.world(0, 2.0)[1]
        g, _, _ = donut(rig, mood="happy" if abs(sw) > 0.8 else "open", small=True)
        f.update(g)
        return f
    if who == "mochi":   # 빗변 위에 철퍼덕 앉아 말랑 — 날개 끝으로 흘러내렸다 탱
        arrow_layer(f)
        sq = [0, 0.04, 0.08, 0.12, 0.16, 0.2, 0.22, -0.12, 0.06, -0.04, 0, 0][k]
        x, y = hyp(0.72, 5.4)
        g, _, _ = mochi(Rig(x, y, 0, 0.78), 1 + sq, 1 - sq,
                        mood="sleep" if 3 <= k <= 6 else "happy" if k == 7 else "open", berry=True)
        shown = {p for p in g if above_hyp((p[0], p[1] - 1)) or p not in ARROW_M}
        f.update({p: g[p] for p in shown})
        apart(f, shown, {MOCHI: hx("fde6ecff"), MOCHI_D: hx("ecd2a6ff"), MOCHI_P: hx("f4bcc8ff")})   # 연분홍 몸 · 콩가루 밑동
        return f
    if who == "icecream":   # 기운 콘에서 민트가 녹아 날개로 뚝뚝 — 날개에 민트 웅덩이
        arrow_layer(f)
        g, _, _ = icecream(Rig(24.0, 10.8, 0, 0.74), drips=(0.6 + 1.2 * ((k % 6) / 6), 0, 0), tilt=-0.38, small=True,
                           mood="open", mouth="wavy")
        drop_y = 17 + (k % 6)
        pud = [p for p in ARROW_M if p[1] >= 16 and p[0] >= 14 and (p[0] - 1) * LY - (p[1] - 1) * LX > -LX * 2.2]
        for p in pud:
            if f.get(p) == PEEK_WHITE and (p[0] + p[1] + k // 4) % 7 != 0:
                f[p] = MINT
        f.update(g)
        if k % 6 < 4:
            f[17, drop_y - 4] = MINT
            f[17, drop_y - 3] = MINT_D
        return f
    if who == "gummybear":   # 날개 끝에 걸터앉아 몸을 살랑 · 짧은 팔 혹을 까딱 흔들기
        arrow_layer(f)
        wave = math.sin(2 * ph)
        g, _, _ = gummy(Rig(WING[0] + 1.6, WING[1] - 6.6 - 0.4 * abs(sw), 0, 0.84), arms=(0.9, 2.1 + 0.5 * wave), sit=True,
                        legs=0.4 * sw, tilt=0.12 * sw, small=True, mood="happy" if k in (3, 4, 9, 10) else "open")
        f.update(g)
        return f
    if who == "onigiri":   # 빗변 미끄럼 — 쭉 미끄러졌다 폴짝 올라간다
        arrow_layer(f)
        t = [0.86, 0.82, 0.78, 0.74, 0.7, 0.67, 0.64, 0.64, 0.72, 0.8, 0.86, 0.86][k]   # 키운 몸이 판 위로 안 나가게 날개 쪽으로 옮김
        hop = [0, 0, 0, 0, 0, 0, 0, 0, 1.4, 1.6, 0.6, 0][k]
        x, y = hyp(t, 4.5 + hop)
        g, _, _ = onigiri(Rig(x, y, 0, 0.76), mood="happy" if k < 7 else "open", mouth="o" if k >= 7 else "smile", small=True)
        f.update(g)
        return f
    if who == "mandu":   # 날개 끝에 꼬치처럼 푹 — 반대편으로 끝이 삐죽, 김 모락
        arrow_layer(f)
        rig = Rig(WING[0] + 1.4, WING[1] + 1.4, 6 * sw, 0.72)
        g, _, _ = mandu(rig, mood="blink" if k == 5 else "open", mouth="o" if k in (8, 9) else "smile")
        f.update(g)
        t: dict = {}
        solid(t, raster([(25.0, 19.4), (31.6, 23.6), (24.6, 24.6)]), sea.Cur(PEEK_WHITE), sea.Cur(OUT))   # 삐죽 나온 화살표 끝도 커서
        for p, c in t.items():
            if p not in g or (g[p] == OUT and c == OUT):
                f[p] = c
        apart(f, {p for p in g if f.get(p) == g[p]},
              {MANDU: hx("f8e2bcff"), MANDU_D: hx("e8c896ff"), PLEAT: hx("cba070ff")})   # 따뜻한 크림 · 주름 그림자
        steam(f, 20, 12, k, 4)
        steam(f, 23, 11, k, 4, 2)
        return f
    if who == "takoyaki":   # 화살표 꼬리가 이쑤시개 — 끝에 꽂힌 타코야키, 가쓰오부시 너울
        arrow_layer(f)
        rig = Rig(13.6, 23.8, 6 * sw, 0.84)
        g, _, _ = takoyaki(rig, k, pick=False, mood="blink" if k == 9 else "open")
        f.update(g)
        return f
    raise KeyError(who)


# ── 대기 ─────────────────────────────────────────────────────────────────────
def wait_scene(k, ph, who):
    sw = math.sin(ph)
    f = {}
    if who == "pudding":   # 접시 위에서 출렁출렁, 체리가 통통
        g, _, _ = pudding(Rig(16, 17, 0, 1.15), sh=1.6 * sw, sq=0.5 * math.sin(2 * ph), plate=True,
                          cherry_dy=-0.8 * abs(math.sin(2 * ph)), mood="happy" if abs(sw) > 0.9 else "open")
        return g
    if who == "macaron":   # 위 꼬끄가 들리며 크림이 쭉 늘어났다 탁
        lift = [0, 0.6, 1.4, 2.2, 3.0, 3.6, 4.0, 4.2, 0, -0.5, 0, 0][k]
        g, _, _ = macaron(Rig(16, 18, 0, 1.08), lift=lift, squeeze=1.0 if k == 9 else 0,
                          mood="squeeze" if k in (8, 9) else "open", mouth="o" if 4 <= k <= 7 else "smile")
        if k == 8:
            lines(g, [(5, 13), (4, 12), (27, 13), (28, 12)])
        return g
    if who == "bungeoppang":   # 붕어빵 틀 안에서 노릇노릇 — 다 구워지면 반짝, 김 모락
        rig = Rig(17, 16, 0, 0.9)
        done = min(1.0, k / 8)
        g, mask, _ = fish(rig, done=done, mood="happy" if k >= 9 else "open" if k % 4 else "blink", tail_sw=0)
        mold = rpoly([(-9.6, -6.4), (13.4, -7.4), (13.4, 7.4), (-9.6, 6.4)], 1.4)
        hnd = bar((-11, 0), (-16.4, 0), 1.3)
        m, _, _ = draw(rig, [("handle", hnd, MOLD_L, True), ("mold", mold, lambda a, b: MOLD_L if b < -6.4 else MOLD, False)])
        m.update(g)
        for i in range(3):
            steam(m, 12 + 5 * i, 8, k, 3 + (k % 3), i)
        if k >= 9:
            sparkle(m, 24 + (k - 9), 10, hx("fff2a0ff"))
        return m
    if who == "donut":   # 데굴데굴 앞뒤로 굴렀다 돌아온다
        a = 40 * sw
        dx = 7.4 * 1.05 * math.radians(a) * 0.55
        g, _, _ = donut(Rig(16 + dx, 15, a, 1.05), mood="happy" if abs(sw) > 0.9 else "open",
                        mouth="o" if abs(sw) > 0.9 else "smile")
        for x in range(6, 27):
            if (x + k) % 4:
                g.setdefault((x, 24), hx("e2c8a8ff"))
        return g
    if who == "mochi":   # 스르르 늘어졌다가 탱!
        sx = [1, 1.06, 1.12, 1.18, 1.24, 1.3, 1.34, 1.36, 0.84, 1.1, 0.96, 1.0][k]
        sy = [1, 0.94, 0.88, 0.82, 0.76, 0.7, 0.66, 0.64, 1.22, 0.92, 1.04, 1.0][k]
        g, _, _ = mochi(Rig(16, 17, 0, 1.1), sx, sy, mood="sleep" if 3 <= k <= 7 else "open",
                        mouth="o" if k == 8 else "smile")
        if k == 8:
            lines(g, [(6, 8), (5, 7), (25, 8), (26, 7), (16, 2), (16, 1)])
        return g
    if who == "icecream":   # 녹아 뚝뚝 — 방울이 떨어져 바닥 웅덩이가 커진다
        dl = [(0.4 + 0.25 * k, 0.2 + 0.1 * ((k + 4) % 12), 0.6 + 0.2 * ((k + 7) % 12))][0]
        g, _, _ = icecream(Rig(16, 15.8, 0, 0.95), drips=dl, mood="open" if k % 6 else "blink", mouth="wavy")
        y = 15 + (k % 6) * 2
        if k % 6 < 5:
            g.setdefault((12, y), MINT)
            g.setdefault((12, y + 1), MINT_D)
        for x in range(9 - k // 3, 15 + k // 4):
            g.setdefault((x, 29), MINT)
        g[22, 7] = TEAR
        g[22, 8] = TEAR
        return g
    if who == "gummybear":   # 젤리 점프 — 착지하면 납작, 뛰면 길쭉
        up = [0, 0, -1, -2.2, -3.0, -3.4, -3.0, -2.2, -1, 0, 0, 0][k]
        sq = [0.4, 0.2, -0.3, -0.2, 0, 0, 0, -0.2, -0.3, 0.5, 0.3, 0.1][k]
        air = up < -1.5
        arms = (2.5, 2.5) if air else (1.3, 1.3) if sq > 0.3 else (0.8, 0.8)   # 뛰면 혹 팔 만세, 납작하면 옆으로 벌어짐
        g, _, _ = gummy(Rig(16, 17.4 + up, 0, 1.12), arms=arms, sq=sq, mood="happy" if air else "open",
                        mouth="o" if air else "smile")
        for x in range(11, 21):
            if not air or 13 <= x <= 18:
                g.setdefault((x, 29), hx("f0b0b8ff"))
        return g
    if who == "onigiri":   # 김 띠를 빙 둘러 감고 뿌듯
        fr = [0, 0.12, 0.25, 0.38, 0.5, 0.62, 0.75, 0.88, 1, 1, 1, 1][k]
        g, _, _ = onigiri(Rig(16, 16, 0, 1.1), nori=(1.8, 9.0, fr), mood="happy" if k >= 8 else "open",
                          mouth="o" if 2 <= k <= 7 else "smile")
        if k in (8, 9):
            sparkle(g, 27, 6, hx("fff2a0ff"))
        return g
    if who == "mandu":   # 김 모락모락 · 하품
        yawn = 4 <= k <= 7
        g, _, _ = mandu(Rig(16, 18, 4 * sw, 1.1), mood="sleep" if yawn else "open", mouth="yawn" if yawn else "smile")
        for i, x in enumerate((11, 16, 21)):
            steam(g, x, 8, k, 6, i * 2)
        return g
    if who == "takoyaki":   # 타코야키 판에서 반쯤 데굴 — 이쑤시개가 콕콕 뒤집는다
        roll = 0.9 * sw
        rig = Rig(16, 15, 0, 1.0)
        g, mask, reg = takoyaki(rig, k, pick=False, roll=roll, mood="squeeze" if abs(sw) > 0.95 else "open",
                                mouth="o" if abs(sw) > 0.95 else "smile")
        pan, _, _ = draw(rig, [("pan", lambda a, b: b > 2.4 and ell(0, 2.4, 10.2, 8.6)(a, b),
                                lambda a, b: PAN_L if b < 3.6 else PAN, False)])
        pan.update(g)
        jab = 1.6 * max(0, math.cos(ph))
        for i in range(9):
            pan[22 - round(jab) + i, 6 - i // 2] = WOOD
        return pan
    raise KeyError(who)


# ── 안 돼 ────────────────────────────────────────────────────────────────────
def sign(f: dict, R: float = 13.5) -> None:
    """빨간 금지 표지(고리 + 왼쪽 위 → 오른쪽 아래 빗금)"""
    ring = {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
    slash = set()
    for t in range(-90, 91):
        x, y = 15.5 + t / 100 * (R - 1.5) * 0.7071, 15.5 + t / 100 * (R - 1.5) * 0.7071
        slash |= disc(x, y, 1.3)
    solid(f, ring | slash, sea.Cur(SIGN), sea.Cur(SIGN_D))   # 금지 표지는 커서


def no_scene(k, ph, who):
    sw = math.sin(ph)
    shake = 1 if k % 4 < 2 else -1
    f = {}
    sign(f)
    if who == "pudding":   # 몸을 마구 흔들며 싫어 — 체리가 흔들
        g, _, _ = pudding(Rig(16, 17, 0, 0.82), sh=2.2 * shake, plate=True, mood="mad", mouth="frown",
                          cherry_dy=-0.6 * (k % 2))
    elif who == "macaron":   # 꼬끄를 꾹 다물어 크림이 삐져나옴
        g, _, _ = macaron(Rig(16, 16.5, 0, 0.88), lift=-0.6 - 0.3 * (k % 2), squeeze=1.2 + 0.6 * abs(sw),
                          mood="squeeze", mouth="flat")
    elif who == "bungeoppang":   # 꼬리를 한 입 베어 먹힘 — 팥이 보이고 엉엉
        g, _, _ = fish(Rig(15.0 + 0.4 * shake, 16, 0, 1.0), bite=True, mood="cry", mouth="o")
        y = 20 + (k % 6)
        g.setdefault((22, y), GOLD_D)
        g.setdefault((24, y + 2 - (k % 3)), GOLD)
    elif who == "donut":   # 금지 빗금에 꿰인 채 쭉 미끄러져 도망
        t = 4.0 * math.sin(ph)
        g, _, _ = donut(Rig(15.5 + t * 0.707, 15.5 + t * 0.707, 0, 0.66), mood="squeeze", mouth="wavy", small=True)
    elif who == "mochi":   # 화나서 빵빵하게 부풀었다 푸슉
        s = [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.34, 0.92, 0.96, 1.0, 1.0][k]
        g, _, _ = mochi(Rig(16, 17.6, 0, 0.72), s * 1.04, s, mood="mad", mouth="o" if k >= 8 else "flat")
        if k in (8, 9):
            for i, x in enumerate((12, 19)):
                steam(g, x, 9, k, 3, i)
    elif who == "icecream":   # 스쿱이 콘 속으로 쏙 숨고 눈만 빼꼼
        sink = [0, 1.5, 3, 4.5, 6, 7, 7, 7, 7, 5, 3, 1][k]
        g, _, _ = icecream(Rig(16 + 0.3 * shake * (sink > 6), 15, 0, 0.72), sink=sink, cone_front=True,
                           mood="squeeze" if sink < 5 else "open", mouth="wavy")
    elif who == "gummybear":   # 짧은 팔 혹을 배 앞에 모으고 몸을 도리도리 기울이며 발을 동동 (팔이 짧아 X 표 대신)
        g, _, _ = gummy(Rig(16, 16.8, 0, 0.9), arms=(-0.5, -0.5), legs=0.6 * shake, tilt=0.14 * shake, mood="mad", mouth="frown")
    elif who == "onigiri":   # 김 띠로 눈을 가리고 도리도리
        rig = Rig(16, 16.6, 10 * shake, 0.84)
        g, _, _ = onigiri(rig, nori=(-3.6, -0.6, 1.0), face_on=False)   # 띠를 올려 눈을 가림
        x, y = rig.world(0, -1.4)
        cx, cy = round(x), math.floor(y)
        for p in ((cx - 2, cy + 3), (cx - 1, cy + 2), (cx, cy + 2), (cx + 1, cy + 3)):   # 입은 삐죽
            g[p] = EYE
        g[cx - 5, cy + 2] = BLUSH
        g[cx + 4, cy + 2] = BLUSH
        x0 = 6 if shake > 0 else 25   # 도리도리 움직임 줄
        for yy in (12, 14):
            g[x0, yy] = OUT
    elif who == "mandu":   # 부글부글 — 주전자처럼 김을 뿜으며 들썩
        hop = -1 if k % 4 in (1, 2) else 0
        g, _, _ = mandu(Rig(16, 18 + hop, 6 * shake, 0.8), mood="mad", mouth="frown", puff=0.6)
        for i, x in enumerate((12, 19)):
            steam(g, x + (k % 2), 10 + hop, k * 2, 5, i)
    elif who == "takoyaki":   # 다가오는 이쑤시개를 데굴 피함
        d = 3.0 * sw
        g, _, _ = takoyaki(Rig(15 - d, 16.5, 0, 0.74), k, pick=False, roll=-d * 0.3, mood="squeeze", mouth="wavy")
        tip = 21 - round(max(0.0, -d) * 0.6)
        for i in range(9):
            g.setdefault((tip + i, 14 - i // 3), WOOD)
        if abs(sw) > 0.8:
            g[9 if d > 0 else 23, 9] = TEAR
            g[9 if d > 0 else 23, 10] = TEAR
    else:
        raise KeyError(who)
    f.update({p: c for p, c in g.items() if 1 <= p[1] <= 30 and 1 <= p[0] <= 30})
    return f


# ── 남은 14칸 (2026-10-10) ────────────────────────────────────────────────────
# 짹짹이 · 댕댕이처럼 열 종이 장면 하나를 같이 쓰고 몸 모양 · 색 · 토핑만 다르다. 간식은 팔다리가 없으니
# 뜻은 몸(쭉 늘어남 · 출렁 · 기울기)과 소품으로 낸다. 몸은 제 그리개(pudding … takoyaki)를 Aff 로 늘여 그린다.
class Aff:
    """Rig 와 같은 꼴(world · local · cell)의 아핀 그리개. 제 좌표 piv 가 화면 (ox, oy) 에 오고, 축 axis(도 — 0 세로 ·
    90 가로 · 45 는 오른쪽 위로 기운 대각) 방향으로 st 배 늘인다(가로질러는 q 배, 안 주면 1/√st 로 부피를 지킴).
    ang 은 그다음 시계 방향 기울기. 얼굴은 face() 가 world 로 한 점만 옮겨 찍으므로 늘여도 눈 · 입 크기는 그대로다"""

    def __init__(self, ox, oy, k=1.0, piv=(0.0, 0.0), st=1.0, axis=0.0, ang=0.0, q=None):
        t = math.radians(axis)
        ex, ey = math.sin(t), -math.cos(t)
        q = 1 / math.sqrt(st) if q is None else q
        s00, s01, s11 = q + (st - q) * ex * ex, (st - q) * ex * ey, q + (st - q) * ey * ey
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        m = (k * (c * s00 - s * s01), k * (c * s01 - s * s11), k * (s * s00 + c * s01), k * (s * s01 + c * s11))
        det = m[0] * m[3] - m[1] * m[2]
        self.m, self.inv = m, (m[3] / det, -m[1] / det, -m[2] / det, m[0] / det)
        self.ox, self.oy, self.piv, self.k = ox, oy, piv, k

    def world(self, a, b):
        u, v = a - self.piv[0], b - self.piv[1]
        m = self.m
        return self.ox + m[0] * u + m[1] * v, self.oy + m[2] * u + m[3] * v

    def local(self, x, y):
        dx, dy = x - self.ox, y - self.oy
        i = self.inv
        return self.piv[0] + i[0] * dx + i[1] * dy, self.piv[1] + i[2] * dx + i[3] * dy

    def cell(self, a, b):
        x, y = self.world(a, b)
        return math.floor(x), math.floor(y)


def body(who, rig, k=0, mood="open", mouth="smile", small=False, **kw):
    """간식 하나를 기본 자세로 — (칸 → 색, 몸 칸). 칸마다 장면이 열 종에 같이 쓰는 입구"""
    if who == "pudding":
        f, m, _ = pudding(rig, sh=kw.get("sh", 0.0), mood=mood, mouth=mouth, small=small, cherry=kw.get("top", True))
    elif who == "macaron":
        f, m, _ = macaron(rig, mood=mood, mouth=mouth, small=small)
    elif who == "bungeoppang":
        f, m, _ = fish(rig, mood={"blink": "sleep", "sleep": "sleep", "squeeze": "sleep"}.get(mood, mood), mouth=mouth,
                       tail_sw=kw.get("sw", 0.0))
    elif who == "donut":
        f, m, _ = donut(rig, mood=mood, mouth=mouth, small=small)
    elif who == "mochi":
        f, m, _ = mochi(rig, mood=mood, mouth=mouth, small=small, berry=kw.get("top", True))
    elif who == "icecream":
        f, m, _ = icecream(rig, mood=mood, mouth=mouth, small=small)
    elif who == "gummybear":
        f, m, _ = gummy(rig, mood=mood, mouth=mouth, small=small, arms=kw.get("arms", (0.8, 0.8)), ears=kw.get("top", True))
    elif who == "onigiri":
        f, m, _ = onigiri(rig, mood=mood, mouth=mouth, small=small)
    elif who == "mandu":
        f, m, _ = mandu(rig, mood=mood, mouth=mouth, small=small)
    elif who == "takoyaki":
        f, m, _ = takoyaki(rig, k, mood=mood, mouth=mouth, pick=False, small=small)
    else:
        raise KeyError(who)
    return f, m


# 얼굴 가운데(제 좌표) — cross 가 입을 십자 가운데에 맞출 때 쓴다. 붕어빵은 옆모습이라 입 자리
FACE_AT = {"pudding": (0.0, 1.2), "macaron": (0.0, -3.4), "bungeoppang": (-6.6, 1.2), "donut": (0.0, 2.9),
           "mochi": (0.0, 1.0), "icecream": (0.0, -2.6), "gummybear": (0.0, -5.0), "onigiri": (0.0, -1.4),
           "mandu": (0.0, 1.4), "takoyaki": (0.0, 2.0)}
# 간식마다 소품 색 (짙음 · 가운데 · 옅음) — 로딩 알갱이 · 소스 물음표에 쓴다
CRUMB = {"pudding": (CARAMEL, CUSTARD_D, CUSTARD_L), "macaron": (MAC_D, MAC, MAC_L),
         "bungeoppang": (ANKO, GOLD, GOLD_L), "donut": (hx("c84a7cff"), ICING, ICING_L),
         "mochi": (BERRY, hx("f08a98ff"), MOCHI_P), "icecream": (hx("3e9c7aff"), MINT_D, MINT),
         "gummybear": (GUM_D, GUM, GUM_L), "onigiri": (NORI, hx("6f8a7aff"), hx("a8b6aeff")),
         "mandu": (hx("a8885aff"), PLEAT, MANDU_D), "takoyaki": (SAUCE, TAKO_D, TAKO)}
HOT_SNACK = ("bungeoppang", "mandu", "takoyaki")   # 따끈한 것 — 몇 장면에서 김이 오른다
_BOX: dict = {}


def box(who, top=True):
    """제 좌표에서 몸이 차지하는 (왼, 위, 오른, 아래) — 배율 1 로 한 번 그려 잰다. top=False 는 토핑(체리 · 딸기)을 뺀 몸"""
    if (who, top) not in _BOX:
        f, _ = body(who, Aff(16, 16), top=top)
        xs, ys = [x for x, _ in f], [y for _, y in f]
        _BOX[who, top] = (min(xs) - 16, min(ys) - 16, max(xs) + 1 - 16, max(ys) + 1 - 16)
    return _BOX[who, top]


def place(who, x0, y0, x1, y1, anchor="c", kmax=1.2, **aff):
    """몸을 화면 상자 (x0, y0)–(x1, y1) 에 맞춰 넣는 Aff. anchor 'c' 는 가운데, 'b' 는 밑변 가운데를 상자 밑변에 붙임
    (늘이고 기울여도 그 점이 그 자리에 남는다)"""
    l, t, r, b = box(who)
    k = min((x1 - x0) / (r - l), (y1 - y0) / (b - t), kmax)
    if anchor == "b":
        return Aff((x0 + x1) / 2, y1, k, ((l + r) / 2, b), **aff)
    return Aff((x0 + x1) / 2, (y0 + y1) / 2, k, ((l + r) / 2, (t + b) / 2), **aff)


def clip(f: dict) -> dict:
    return {p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}


def shift(f: dict, dx: int, dy: int) -> dict:
    return {(x + dx, y + dy): c for (x, y), c in f.items()}


def phases():
    return [(k, 2 * math.pi * k / N) for k in range(N)]


# ── 작은 화살표 + 간식 + 소품 (busy · help · person · pin) ────────────────────────
MINI_S = 0.8                     # 작은 화살표 배율 — 짹짹이와 같음
MINI_BOX = (1, 15, 14, 30)       # 화살표 밑 간식 자리 — 화살표 밑동을 머리에 인다


def mini_arrow() -> set:
    return raster([(1 + x * MINI_S, 1 + y * MINI_S) for x, y in PEEK_CUR])


def mini(who, k, ph, mood=None, mouth="smile", tilt=0.0) -> dict:
    """작은 화살표 밑에 앉은 간식 — 밑동을 바닥에 두고 말랑 출렁(늘었다 줄었다), 한 번 끔뻑"""
    sq = 0.06 * math.sin(2 * ph)
    rig = place(who, *MINI_BOX, anchor="b", st=1 + sq, ang=tilt)
    f, _ = body(who, rig, k, mood or ("blink" if k == 7 else "open"), mouth, small=True)
    return f


def companion(who, scene, pose=lambda k, ph: {}) -> list[dict]:
    """작은 화살표 간식 + scene(k, ph) 이 그리는 소품(오른쪽). 화살표를 맨 나중에 — 무엇도 화살표를 못 덮는다"""
    am = mini_arrow()
    frames = []
    for k, ph in phases():
        f = scene(k, ph)
        f.update(mini(who, k, ph, **pose(k, ph)))
        solid(f, am, sea.Cur(PEEK_WHITE), sea.Cur(OUT))   # 화살표는 커서
        f[1, 1] = sea.Cur(OUT)
        frames.append(post_steam(clip(f)))
    return frames


def busy(who):
    """오른쪽 아래에 그 간식 색 알갱이 여덟이 원을 그리고, 한 알씩 차례로 진해지며 돈다(로딩 원)"""
    c0, c1, c2 = CRUMB[who]
    cols = tuple(sea.Cur(c) for c in (c0, c1, c2, c2[:3] + (0x68,)))   # 로딩 원은 커서
    cx, cy, R = 22.5, 22.0, 6.0

    def scene(k, ph):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = math.floor(cx + R * math.cos(a)), math.floor(cy + R * math.sin(a))
            lag = (head - i) % 8
            col = cols[0] if lag < 1 else cols[1] if lag < 2 else cols[2] if lag < 3.5 else cols[3]
            for p in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
                f[p] = col
        return f
    return companion(who, scene, lambda k, ph: {"mood": "blink" if k == 7 else "open", "mouth": "dot"}), (1, 1)


QMARK = [(19.4, 21.2), (19.4, 17.8), (21.6, 15.6), (24.2, 13.4), (24.4, 9.8), (21.6, 7.6), (18.4, 8.6)]


def help_(who):
    """그 간식 색 소스로 짠 물음표가 몸을 꿈틀 — 끝(점)은 소스 한 방울. 간식은 고개를 갸웃"""
    c0, c1, c2 = CRUMB[who]

    def scene(k, ph):
        pts = []
        n = len(QMARK)
        for i, (x, y) in enumerate(QMARK):
            a, b = QMARK[max(0, i - 1)], QMARK[min(n - 1, i + 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy)
            w = 0.5 * math.sin(2 * ph - i * 1.2) * (0.3 if i == 0 else 1.0)
            pts.append((x - dy / L * w, y + dx / L * w))
        o, _, _ = draw(Rig(0, 0, 0, 1.0), [("q", chain(pts, 1.7, 1.5), lambda a, b: c2 if a < 21 and b < 10.6 else c1,
                                            False)])
        f = {p: sea.Cur(c) for p, c in o.items()}   # 물음표(소스)와 점(방울)은 커서
        drop = round(0.6 * math.sin(2 * ph))   # 방울이 통 튄다
        solid(f, disc(19.9, 26.8 + drop * 0.5, 1.9), sea.Cur(c1), sea.Cur(OUT))
        f[19, 26 + (1 if drop > 0 else 0)] = sea.Cur(c2)
        return f
    tilt = [0, 4, 8, 10, 10, 8, 4, 0, 0, 0, 0, 0]
    return companion(who, scene, lambda k, ph: {"tilt": tilt[k], "mouth": "o" if 2 <= k <= 5 else "smile"}), (1, 1)


SKIN, HAIR, SHIRT, SHIRT_D = hx("f7d7bcff"), hx("5a3a28ff"), hx("4a7fb5ff"), hx("2e5a88ff")
HEART = ["##.##", "#####", ".###.", "..#.."]


def person(who):
    """사람이 손을 흔들고, 머리 위로 하트가 퐁 — 화살표 밑 간식이 좋아 반긴다 (사람은 짹짹이 person 과 같은 꼴)"""
    def scene(k, ph):
        f = {}
        rig = Rig(23.0, 26.0, 0.0, 0.7)
        wave = -2.0 * abs(math.sin(ph))
        hand_ = (9.0, -8.0 + wave)
        parts = [("hand", ell(*hand_, 2.2, 2.2), SKIN, True), ("sleeve", bar((5.0, -0.5), hand_, 1.8), SHIRT, False),
                 ("face", ell(0.0, -7.2, 4.6, 4.2), SKIN, True), ("hair", ell(0.0, -8.6, 5.4, 4.8), HAIR, False),
                 ("torso", ell(0, 3.0, 7.6, 6.4), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
        out, _, _ = draw(rig, parts)
        for sg in (-1, 1):
            ex, ey = rig.cell(sg * 2.0, -7.4)
            out[ex, ey] = EYE
            out[ex, ey + 1] = EYE
            out[rig.cell(sg * 3.0, -5.4)] = BLUSH
        f.update({p: sea.Cur(c) for p, c in out.items()})   # 사람은 커서, 머리 위 하트는 간식 쪽
        rise = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5][k]
        if rise < 5:
            for j, row in enumerate(HEART):
                for i, ch in enumerate(row):
                    if ch == "#":
                        f[19 + i, 9 - rise + j] = BERRY if rise < 4 else hx("e8485ab0")
        return f
    return companion(who, scene, lambda k, ph: {"mood": "happy" if k % 6 < 3 else "open"}), (1, 1)


def pin(who):
    """빨간 지도 핀 머리에 그 간식이 쏙 — 핀이 통통 튀고, 땅에 닿으면 눈웃음"""
    def scene(k, ph):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 15.0 + dy
        for x in range(19, 27):
            f.setdefault((x, 30), hx("2a1c2260") if dy else hx("2a1c22a0"))
        pinm = disc(cx, cy, 7.0) | raster([(cx - 5.0, cy + 3.8), (cx + 5.0, cy + 3.8), (cx, cy + 13.4)])
        solid(f, pinm, sea.Cur(SIGN), sea.Cur(SIGN_D))   # 핀 몸통은 커서, 속 간식 · 땅 그림자는 간식 쪽
        g, _ = body(who, place(who, cx - 5.0, cy - 5.0, cx + 5.0, cy + 5.0), k, "happy" if dy == 0 else "open",
                    small=True)
        f.update(g)
        return f
    return companion(who, scene), (1, 1)


# ── hand: 몸 꼭대기를 쭉 뽑아 콕 ──────────────────────────────────────────────────
class Taper:
    """밑은 base 그대로, 제 좌표 bm 줄 위는 화면 ty 까지 위로 쭉 늘이며 가늘게 — 말랑한 몸 꼭대기를 집어 뽑은 손가락.
    목(t 0.7–1)에서 몸 너비 → 손가락 너비 wf 로 좁아지고, 손가락은 곧게 서다 끝(t < tc)이 둥글게 닫힌다.
    처음 판은 끝으로 갈수록 뾰족한 원뿔이었는데 1배에서 양파 · 마늘로 읽혀(2026-10-10) 손가락 꼴로 바꿨다"""

    def __init__(self, base: Aff, bm: float, bt: float, ty: float, wf: float = 0.32, tc: float = 0.14):
        self.b, self.bm, self.bt, self.ty, self.wf, self.tc = base, bm, bt, ty, wf, tc
        self.ym = base.world(base.piv[0], bm)[1]

    def w(self, t):
        if t >= 0.7:
            u = (t - 0.7) / 0.3
            return self.wf + (1 - self.wf) * u * u * (3 - 2 * u)
        if t >= self.tc:
            return self.wf
        u = t / self.tc
        return self.wf * math.sqrt(max(0.0, 1 - (1 - u) ** 2))

    def world(self, a, b):
        if b >= self.bm:
            return self.b.world(a, b)
        t = max(0.0, (b - self.bt) / (self.bm - self.bt))
        return self.b.ox + (a - self.b.piv[0]) * self.b.k * self.w(t), self.ty + t * (self.ym - self.ty)

    def local(self, x, y):
        if y >= self.ym:
            return self.b.local(x, y)
        t = (y - self.ty) / (self.ym - self.ty)
        w = self.w(t) if t > 0 else 0.0
        if w <= 1e-3:
            return 1e6, 1e6
        return self.b.piv[0] + (x - self.b.ox) / (self.b.k * w), self.bt + t * (self.bm - self.bt)

    def cell(self, a, b):
        x, y = self.world(a, b)
        return math.floor(x), math.floor(y)


HAND_HOT = (15, 2)
POKE = [0.0, 0.3, 0.6, 1.0, 1.0, 0.4, 0.0, 0.3, 0.6, 1.0, 1.0, 0.4]   # 장마다 뽑힌 정도 — 1 이면 쭉 뻗어 콕


def hand(who):
    """말랑한 몸 꼭대기를 위로 쭉 뽑아 뾰족한 끝으로 콕콕 — 끝 칸이 핫스팟이고 장마다 그대로다.
    몸통이 내려앉을수록 끝이 길어진다(끝은 그 자리). 토핑(체리 · 딸기)은 끝에 걸려 뭉개지므로 뺀다"""
    l, t, r, b = box(who, top=False)
    fb = FACE_AT[who][1] if who != "bungeoppang" else -1.2
    frames = []
    for k, p in enumerate(POKE):
        k_ = min(20.0 / (b - t), 22.0 / (r - l), 1.1)
        base = Aff(15.5, 30.0 - 1.4 * (1 - p), k_, ((l + r) / 2, b), st=1.0 - 0.06 * (1 - p), q=1.0 + 0.06 * (1 - p))
        bm = fb - 2.2
        wf = max(0.45, 2.6 / ((r - l) / 2 * k_))   # 손가락 반너비 2.6 칸 이상 — 가늘면 1배에서 테만 남아 더듬이로 읽힌다
        tp = Taper(base, bm, t, HAND_HOT[1] + 0.2, wf, 0.25)
        if who == "onigiri":   # 세모 꼭짓점이 원래 뾰족 — 집어 뽑으면 바늘이 되므로 몸째 위로 늘이기만
            tp = Aff(15.5, 30.0 - 1.4 * (1 - p), min(26.0 / (b - t), 1.1) * 0.85, ((l + r) / 2, b), st=1.15 + 0.15 * p)
        f, mask = body(who, tp, k, "squeeze" if p >= 1 else "blink" if k == 6 else "open", "o" if p >= 1 else "smile",
                       small=k_ < 0.8, top=False)
        top = min(y for _, y in mask)
        xt = min((x for x, y in mask if y == top), key=lambda x: abs(x - 15.5))
        f = shift(f, HAND_HOT[0] - xt, HAND_HOT[1] - top)
        f[HAND_HOT] = OUT
        if p >= 1:   # 콕 — 끝 양옆으로 튀는 줄
            x, y = HAND_HOT
            for q in ((x - 3, y + 1), (x - 4, y), (x + 3, y + 1), (x + 4, y), (x - 3, y + 3), (x + 3, y + 3)):
                f.setdefault(q, OUT)
        frames.append(post_steam(clip(f)))
    return frames, HAND_HOT


# ── cross: 동그랗게 벌린 입이 십자 가운데 ──────────────────────────────────────────
def cross(who):
    """앞모습 간식, 동그랗게 벌린 입의 왼쪽 위 칸이 (15, 15). 가로 · 세로 조준선이 몸 가장자리까지 와 닿는다.
    몸은 입을 축으로 말랑 출렁(늘었다 줄었다)하고 한 번 끔뻑 — 입은 그 자리에 남는다"""
    fa = FACE_AT[who]
    l, t, r, b = box(who)
    k_ = min(19.0 / (b - t), 22.0 / (r - l), 1.1)
    frames = []
    for k, ph in phases():
        s = 1 + 0.07 * math.sin(2 * ph)
        if who == "bungeoppang":   # 옆모습 — 입 칸(mx, my)을 (15, 15) 에
            rig = Aff(15.5, 15.2, k_, fa, st=s)
        else:   # face() 는 입 'o' 를 (cx-1, cy+1) 부터 찍는다 — cx = 16 · cy = 14
            rig = Aff(16.0, 14.5, k_, fa, st=s)
        g, mask = body(who, rig, k, "blink" if k == 8 else "open", "o", small=k_ < 0.8)
        f = {}
        for i in range(1, 31):
            f[i, 15] = sea.Cur(OUT)   # 조준선은 커서
            f[15, i] = sea.Cur(OUT)
        f.update(g)
        f[15, 15] = MOUTH
        frames.append(post_steam(clip(f)))
    return frames, (15, 15)


# ── ibeam: 알파벳 쿠키 I 에 기대어 갸웃 ─────────────────────────────────────────
TILT = [0, 0, 6, 9, 9, 6, 0, 0, -3, -5, -5, -3]
BISC, BISC_D = hx("f2c27aff"), hx("c88a3eff")


def cookie_i(f: dict) -> None:
    """알파벳 쿠키 I: 세로 줄기 + 위아래 가로 머리, 군데군데 구멍 자국"""
    m = {(x, y) for y in range(2, 30) for x in (14, 15, 16)}
    m |= {(x, y) for y in (2, 3, 4, 27, 28, 29) for x in range(10, 21)}
    solid(f, m, lambda p: sea.Cur(BISC_D if p in ((12, 3), (18, 3), (15, 9), (15, 21), (12, 28), (18, 28)) else BISC),
          sea.Cur(OUT))   # 쿠키 I 는 I 기둥 — 커서


def ibeam(who):
    """알파벳 쿠키 I 오른쪽에 간식이 몸을 기대고 갸웃갸웃 — 쿠키를 맨 나중에 찍어 안 가려진다. 핫스팟은 줄기 가운데"""
    frames = []
    for k, ph in phases():
        rig = place(who, 17, 5, 31, 26, anchor="b", ang=-8 + TILT[k], st=1 + 0.04 * math.sin(2 * ph))
        g, _ = body(who, rig, k, "blink" if k == 6 else "happy" if k in (3, 4) else "open", small=rig.k < 0.8)
        f = dict(g)
        cookie_i(f)
        if who in HOT_SNACK:
            steam(f, 25, 6, k, 4)
        frames.append(post_steam(clip(f)))
    return frames, (15, 15)


# ── move · 늘이기 ─────────────────────────────────────────────────────────────
CHEV, CHEV_L = hx("f59a5aff"), hx("f59a5aa0")   # 화살촉 (짙은 것 · 옅은 것) — 짹짹이와 같은 색


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col) -> None:
    """(dx, dy) 쪽을 가리키는 화살촉 (bird.chevron 과 같음). 대각은 두 칸 굵기 ㄱ 자"""
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


def move(who):
    """한가운데서 말랑 출렁 — 가로로 퍼졌다 세로로 솟았다 번갈아, 네 방향 화살촉이 바깥으로 두근"""
    frames = []
    for k, ph in phases():
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy, sea.Cur(CHEV if o else CHEV_L))   # 화살촉은 커서
        s = 1 + 0.16 * math.cos(2 * ph)
        rig = place(who, 7, 7, 25, 25, st=s)
        g, _ = body(who, rig, k, "happy" if s > 1.1 else "squeeze" if s < 0.9 else "open", "o" if s > 1.1 else "smile")
        f.update(g)
        frames.append(post_steam(clip(f)))
    return frames, None


AXES = {"ns": 0.0, "we": 90.0, "nwse": -45.0, "nesw": 45.0}


def stretch(who, axis):
    """그 방향으로 몸을 쭉 늘였다 탱 줄었다 — 말랑하니 늘어난다. 얼굴은 늘지 않고 가운데, 늘 때 눈을 질끈.
    축 양끝 화살촉이 두근"""
    t = math.radians(axis)
    ex, ey = math.sin(t), -math.cos(t)
    dx, dy = round(ex), round(ey)
    R = 13 if dx == 0 or dy == 0 else 11
    frames = []
    for k, ph in phases():
        f = {}
        s = 0.5 + 0.5 * math.sin(ph)
        o = 1 if s > 0.6 else 0
        for sg in (-1, 1):
            chevron(f, 15 + sg * dx * (R + o), 15 + sg * dy * (R + o), sg * dx, sg * dy, sea.Cur(CHEV if o else CHEV_L))
        rig = place(who, 8, 8, 23, 23, st=1.05 + 0.6 * s, axis=axis)
        g, _ = body(who, rig, k, "squeeze" if s > 0.6 else "open", "o" if s > 0.6 else "smile")
        f.update(g)
        frames.append(post_steam(clip(f)))
    return frames, None


# ── pen: 초코펜으로 쓰기 ──────────────────────────────────────────────────────
TIP, PBACK = (1.5, 29.5), (20.0, 11.0)
PEN, PEN_D, CHOCO, CHOCO_L = hx("f6f0e8ff"), hx("d8ccbcff"), hx("5a3424ff"), hx("8a5a3eff")
PEN_END = hx("b8b0a8ff")   # 꽁무니 — 빨갛게 두면 1배에서 성냥개비로 읽혀(2026-10-10 첫 판) 회색으로
SCRIBBLE = [(3, 29), (4, 28), (5, 28), (6, 29), (7, 30), (8, 30), (9, 29), (10, 28), (11, 28), (12, 29), (13, 30),
            (14, 30)]


def pen(who):
    """초코펜을 몸으로 끌어안고 사각사각 — 펜이 펜촉을 축으로 까딱이고, 지나간 자리에 초코 글씨가 이어진다.
    펜촉(왼쪽 아래 끝)이 핫스팟. 펜은 간식 위에 찍어 끝이 안 가려진다"""
    L = math.hypot(PBACK[0] - TIP[0], PBACK[1] - TIP[1])
    frames = []
    for k, ph in phases():
        d = math.radians(4.0 * math.sin(2 * ph))
        rig = place(who, 15, 12, 31, 30, anchor="b", ang=-6 + 3 * math.sin(2 * ph))
        g, _ = body(who, rig, k, "blink" if k == 4 else "happy" if k in (8, 9) else "open", small=rig.k < 0.8)
        f = dict(g)
        for p in SCRIBBLE[:2 + k]:
            f[p] = sea.Cur(CHOCO)   # 펜이 쓴 글씨도 펜(커서) 색을 따른다
        ux, uy = (PBACK[0] - TIP[0]) / L, (PBACK[1] - TIP[1]) / L
        ux, uy = ux * math.cos(d) - uy * math.sin(d), ux * math.sin(d) + uy * math.cos(d)
        back = (TIP[0] + ux * L, TIP[1] + uy * L)

        def pcol(a, b):
            tt = (a - TIP[0]) * ux + (b - TIP[1]) * uy
            sd = -(a - TIP[0]) * uy + (b - TIP[1]) * ux
            if tt < 4.6:                # 짤주머니 꼭지 — 초코가 차 있다
                return CHOCO if tt < 2.6 else CHOCO_L
            if tt > L - 1.6:
                return PEN_END
            if 9.0 < tt < 13.0 and abs(sd) < 0.9:
                return CHOCO_L          # 투명 창으로 비치는 초코
            return PEN_D if sd > 0.6 else PEN
        neck = (TIP[0] + ux * 4.6, TIP[1] + uy * 4.6)
        pm, _, _ = draw(Rig(0, 0, 0, 1.0), [("pen", any_of(bar(TIP, neck, 0.5, 1.9), bar(neck, back, 1.9, 1.9)), pcol,
                                             False)])
        f.update({p: sea.Cur(c) for p, c in pm.items()})   # 초코펜은 테까지 커서
        f[math.floor(TIP[0]), math.floor(TIP[1])] = sea.Cur(CHOCO)
        frames.append(post_steam(clip(f)))
    return frames, (math.floor(TIP[0]), math.floor(TIP[1]))


# ── up: 위로 쭉 발돋움 ────────────────────────────────────────────────────────
def up(who):
    """몸을 위로 쭉 늘여 발돋움 — 꼭대기는 그 자리, 몸통이 늘었다 줄었다 하며 밑동이 통통 들썩. 양옆에 위로 솟는 줄.
    핫스팟은 꼭대기 가운데 칸이고 장마다 같다"""
    frames, hot = [], None
    for k, ph in phases():
        s = 1.25 + 0.2 * abs(math.sin(ph))
        rig = place(who, 7, 6, 25, 27, anchor="b", st=s)
        g, mask = body(who, rig, k, "happy" if k % 4 < 2 else "open", "o" if k % 4 < 2 else "smile", small=rig.k < 0.8)
        cols = [x for x, _ in mask]
        cx = round((min(cols) + max(cols)) / 2)
        top = min(y for x, y in mask if x == cx)
        if hot is None:
            hot = (cx, 3)
        f = shift(g, hot[0] - cx, hot[1] - top)
        for xx in range(9, 23):   # 바닥 그림자 — 몸이 길수록 옅게
            f.setdefault((xx, 30), hx("2a1c2250"))
        rise = k % 4   # 양옆에 작은 ^ 화살촉이 위로 솟으며 옅어진다
        for x0 in (4, 27):
            for dx_, dy_ in ((0, 0), (-1, 1), (1, 1), (-2, 2), (2, 2)):
                f.setdefault((x0 + dx_, 17 - 2 * rise + dy_), sea.Cur(CHEV if rise < 2 else CHEV_L))   # 화살촉은 커서
        frames.append(post_steam(clip(f)))
    return frames, hot


SCENES = {"busy": busy, "help": help_, "person": person, "pin": pin, "hand": hand, "cross": cross, "ibeam": ibeam,
          "move": move, "ns": lambda w: stretch(w, AXES["ns"]), "we": lambda w: stretch(w, AXES["we"]),
          "nwse": lambda w: stretch(w, AXES["nwse"]), "nesw": lambda w: stretch(w, AXES["nesw"]), "pen": pen, "up": up}


def center_hot(frames):
    """모든 장에서 불투명한 칸 중 판 가운데에 가장 가까운 것 (bird.center_hot 과 같음)"""
    common = set.intersection(*[{p for p, c in f.items() if c[3] == 255} for f in frames])
    return min(common, key=lambda p: (math.hypot(p[0] - 15.5, p[1] - 15.5), p))


# ── 쓰기 ─────────────────────────────────────────────────────────────────────
ROSTER = [
    ("pudding", "푸딩"), ("macaron", "마카롱"), ("bungeoppang", "붕어빵"), ("donut", "도넛"), ("mochi", "찹쌀떡"),
    ("icecream", "아이스크림"), ("gummybear", "젤리곰"), ("onigiri", "주먹밥"), ("mandu", "만두"), ("takoyaki", "타코야키"),
]
WAIT_HOT = {"pudding": (16, 18), "macaron": (16, 20), "bungeoppang": (16, 16), "donut": (16, 21), "mochi": (16, 20),
            "icecream": (16, 13), "gummybear": (16, 17), "onigiri": (16, 18), "mandu": (16, 19), "takoyaki": (16, 16)}


def check(rid: str, frames: list[dict], hot: tuple) -> int:
    """장 수 · 핫스팟이 장마다 불투명한 칸 위에 있는지(반투명 테면 걸림) · 판(0–31) 안인지 · 금지 알파(fe·fd·fc)가 없는지.
    경고 수를 돌려준다"""
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
            print(f"  ! {rid} {i}장: 예약된 알파(fe·fd·fc)")
            bad += 1
    return bad


def post_steam(f: dict) -> dict:
    """김은 테 없이 — finish 한 뒤 김 칸만 테를 걷는다(김 둘레에 둘린 테를 뺀다)"""
    sm = {p for p, c in f.items() if c == STEAM}
    if not sm:
        return finish(f)
    base = {p: c for p, c in f.items() if c != STEAM}
    g = finish(base)
    for p in sm:
        g[p] = STEAM
    return g


def main() -> None:
    """python3 snack.py [--cells 칸,칸] [마리...] — --cells 를 주면 그 칸만 다시 그린다 (bird.py 와 같음)"""
    args = sys.argv[1:]
    only = None
    if "--cells" in args:
        i = args.index("--cells")
        only = set(args[i + 1].split(","))
        del args[i:i + 2]
    ids = args or [r for r, _ in ROSTER]
    bad = 0
    for who in ids:
        d = ART / f"{who}anim"
        d.mkdir(parents=True, exist_ok=True)
        done = []
        for cell, fn, hot in (("arrow", arrow_scene, (1, 1)), ("wait", wait_scene, WAIT_HOT[who]),
                              ("no", no_scene, (15, 15))):
            if only and cell not in only:
                continue
            frames = [post_steam(fn(k, 2 * math.pi * k / N, who)) for k in range(N)]
            if cell == "arrow":
                for fr in frames:
                    fr[1, 1] = sea.Cur(OUT)
                frames = [{p: c for p, c in fr.items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31} for fr in frames]
            bad += check(f"{who}/{cell}", frames, hot)
            (d / f"{cell}.txt").write_text(shape.to_text(sea.mark(frames), hot, RATE), encoding="utf-8")
            done.append(cell)
        for cell, scene in SCENES.items():
            if only and cell not in only:
                continue
            frames, hot = scene(who)
            frames = [{p: c for p, c in fr.items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31} for fr in frames]
            hot = hot or center_hot(frames)
            bad += check(f"{who}/{cell}", frames, hot)
            (d / f"{cell}.txt").write_text(shape.to_text(sea.mark(frames), hot, RATE), encoding="utf-8")
            done.append(cell)
        print(f"{who}: {len(done)}칸")
    print(f"경고 {bad}개")


if __name__ == "__main__":
    main()

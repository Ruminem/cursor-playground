# SPDX-License-Identifier: Apache-2.0
"""짹짹이 · 애니 — 작은 새 열 마리의 17칸을 그린다. 손으로 돌린다.

  python gen/bird.py [마리...] [--cells 칸,칸]     art/<마리>anim/<칸>.txt 를 쓴다

새는 모두 앞모습 치비 — 큰 동그란 머리와 달걀 몸을 한 덩이로 칠하고(`skin` 이 마리마다 무늬를 정한다),
양옆 날개 · 뒤로 뻗은 꼬리 · 볏은 따로 놓는다. 눈 · 부리 · 발은 칸 단위로 찍는다(줄여도 점이 안 되게).

  arrow   1배 흰 윈도우 화살표를 정수리에 이고 그 밑에 앞모습 새가 선다(carry). 쪼그렸다 통통 뛰면 화살표가
          머리에서 한 줄 떴다 다시 얹힌다. 날지 않는 새(병아리 · 아기오리 · 펭귄)는 뒤뚱. 화살표 끝 (1, 1) 이 핫스팟.
          매끈한 모양용 재료(_peek.txt 새 층 · _arrow.txt · _peek.json 꼬리 밑점)도 같이 쓴다(write_carry) —
          smooth.peek_drawer 가 새 화살표 꼬리 밑에 새를 옮겨 단다. 매끈한 쪽 화살표도 장마다 같은 각도로 기운다(_peek.json 의 rot)
  wait    마리마다 제 버릇(알 품기 · 거울 수다 · 볏 까딱 · 모이 콕콕 · 가지 그네 · 솜털 빵빵 · 삐약 점프 ·
          둥둥 · 노래 · 뒤뚱)
  no      빨간 금지 표지 안에서 마리마다 제 식으로 싫다고 한다

나머지 14칸은 열 마리가 한 장면을 같이 쓰고 무늬 · 볏 · 꼬리만 제 것이다.
  busy · help · person · pin   작은 화살표를 인 작은 새(cheesecat 처럼 길동무) 옆에 소품 — 씨앗 여덟 알 로딩 원 ·
          물음표 꼴 분홍 지렁이(점은 흙 한 알) · 손 흔드는 사람(머리 위에 같은 새) · 새 얼굴 든 빨간 지도 핀.
          화살표를 맨 위에 칠해 무엇도 덮지 않는다. 핫스팟 (1, 1)
  hand    고개 젖혀 부리를 위로 콕콕. 몸만 움츠렸다 펴고 부리 끝(맨 윗칸)이 장마다 같은 핫스팟
  cross   앞모습 얼굴, 부리 맨 윗줄 왼칸이 (15, 15). 양옆 가는 선 · 머리 위 깃 한 가닥 · 턱 밑 줄이 조준선
  ibeam   I 꼴 나뭇가지를 옆으로 매달려 움켜쥐고 갸웃. 가지 가운데 (15, 15)
  move    날개 활짝 제자리 파닥 + 네 방향 화살촉. ns · we · nwse · nesw 는 고개를 세운 채 두 날개를 축 양쪽으로
          쭉 늘였다 줄이는 기지개 + 축 끝 화살촉. 모두 몸 가운데 (15, 15)
  pen     큰 깃펜을 왼 날개로 끼고 펜촉을 축으로 까딱. 펜촉 (1, 29)
  up      두 날개를 V 자로 번쩍 만세, 머리는 고정하고 몸만 들썩. 머리 윤곽 꼭대기 가운데(볏 아님)

그리개(Rig · draw · ell · bar · chain · tri · any_of · sign)는 cheesecat.py 에서 베껴 왔다 — 그쪽 draw 가
제 모듈의 OUT 을 쓰므로 불러오지 않는다.
"""
import math
import sys
from types import SimpleNamespace as NS

import sea  # noqa: E402
import shape  # noqa: E402
from sea import (N, PEEK_CUR, PEEK_WHITE, SIGN, SIGN_D, disc, finish, hx, ink, inside,  # noqa: E402
                 phases, raster, solid)


OUT, EYE, HI = hx("3a2a30ff"), hx("2a1c22ff"), hx("ffffffff")
RIM_WARM, RIM_GREY = hx("f6e9d2c7"), hx("d9dde3c7")       # 테 한 벌 — 따뜻한 새는 크림, 흰 · 회색 새는 연회색
WHITE = hx("fffaf2ff")
MOUTH = hx("8a2a3aff")
BLUSH = hx("f6a8b4ff")
ANGRY = hx("e8484aff")
WOOD, WOOD_D, LEAF, LEAF_D = hx("b07a48ff"), hx("7e5230ff"), hx("8cc864ff"), hx("5a9a44ff")
SEED, SEED_D = hx("e8c27aff"), hx("b08a48ff")
WATER = (hx("bfe6f5ff"), hx("7cc4d8ff"), hx("7cc4d8b0"), hx("7cc4d860"))
ICE, ICE_D = hx("e6f4fbff"), hx("a8d4e8ff")
NOTE = (hx("f07c9cff"), hx("6aa8e0ff"), hx("8cc864ff"))
SHELL, SHELL_D = hx("fdf8eeff"), hx("d8ccb4ff")
NEST, NEST_D, NEST_L = hx("a8743eff"), hx("6e4a28ff"), hx("caa060ff")
GLASS, GLASS_L, FRAME, FRAME_D = hx("bfe0f0ff"), hx("eef8ffff"), hx("c8ccd4ff"), hx("8a909aff")


# ── 그리개 (cheesecat.py 에서 베낌) ─────────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도) · 배율 k. ang=0 이면 u 가 오른쪽, w 가 아래"""

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


def draw(rig: Rig, parts: list) -> tuple[dict, set, dict]:
    """parts: [(이름, 맞음(a, b), 색(a, b) 또는 색, 테두리)] — 앞의 것이 위에 그려진다 (cheesecat.draw 와 같음)"""
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


def sign(f: dict, R: float = 13.5) -> None:
    """빨간 금지 표지(고리 + 왼쪽 위 → 오른쪽 아래 빗금) — cheesecat.sign 과 같음"""
    ring = {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
    slash = set()
    for t in range(-90, 91):
        x, y = 15.5 + t / 100 * (R - 1.5) * 0.7071, 15.5 + t / 100 * (R - 1.5) * 0.7071
        slash |= disc(x, y, 1.3)
    solid(f, ring | slash, SIGN, SIGN_D)


# ── 마리마다 무늬 ─────────────────────────────────────────────────────────────
def hcoord(a, b, G):
    """머리 제 좌표(반지름 단위). 고개를 돌린 만큼(ht) 무늬도 옆으로 간다"""
    return (a - G.hx - G.ht) / G.hr, (b - G.hy) / G.hr


def in_head(a, b, G):
    return (a - G.hx) ** 2 + (b - G.hy) ** 2 <= G.hr ** 2


def blob(u, v, cu, cv, ru, rv):
    return ((u - cu) / ru) ** 2 + ((v - cv) / rv) ** 2 <= 1


def belly(a, b, G, w=0.62, h=0.72, dy=0.22):
    return ((a - G.bx) / (G.ra * w)) ** 2 + ((b - G.by - G.rb * dy) / (G.rb * h)) ** 2 <= 1


def bands(al, period, width):
    """날개 길이 방향(al, -1–1) 줄무늬"""
    return (al * 5.0) % period < width


SPECS: dict = {}


def spec(sid, name, **kw):
    d = dict(hr=6.5, hy=-5.0, ra=6.6, rb=5.8, by=3.0, wl=4.6, ww=2.4, eye="big", eyex=0.42, eyey=-0.02,
             beak="small", beaky=0.3, crest=False, tail=None, rim=RIM_WARM, extra=None, toes=3)
    d.update(kw)
    SPECS[sid] = NS(id=sid, name=name, **d)
    return SPECS[sid]


# 1 문조 — 회색 몸 · 까만 머리 · 흰 볼 · 굵은 분홍 부리 · 빨간 눈테
J_GREY, J_GREY_D, J_BELLY, J_BLACK = hx("8f9aabff"), hx("6f7a8cff"), hx("ecd9d3ff"), hx("2f2a33ff")
J_BEAK, J_BEAK_D, J_RING = hx("f2768cff"), hx("c84a64ff"), hx("e8485aff")


def j_skin(a, b, G):
    if in_head(a, b, G):
        u, v = hcoord(a, b, G)
        if v > 0.02 and not (abs(u) < 0.22 and v > 0.62) and blob(abs(u), v, 0.5, 0.42, 0.52, 0.48):
            return WHITE
        return J_BLACK
    return J_BELLY if belly(a, b, G) else J_GREY


spec("javasparrow", "문조", skin=j_skin, wing=lambda al, ac, sg: J_GREY_D if al > 0.55 else J_GREY,
     beak="big", beak_col=(J_BEAK, J_BEAK_D), eye="ring", ring=J_RING, foot=hx("f0a0a8ff"), rim=RIM_GREY,
     hr=6.4, hy=-5.4, ra=6.3, rb=6.0, tail=dict(pts=[(1.5, -2.0), (4.0, 0.6), (5.2, 1.6)], r=(1.8, 1.5),
                                                  col=lambda s: J_BLACK))

# 2 사랑앵무 — 연두 몸 · 노란 얼굴 · 목 점 · 날개 물결 줄 · 파란 코
B_GREEN, B_GREEN_L, B_YEL, B_BAR, B_WING = hx("74c84cff"), hx("a6e070ff"), hx("ffe25aff"), hx("3a3a2eff"), hx("e6ec7aff")
B_TAIL, B_CERE, B_BEAK, B_SPOT = hx("3e6ec8ff"), hx("5a86e6ff"), hx("f0d8a0ff"), hx("6a5ad8ff")


def b_skin(a, b, G):
    if in_head(a, b, G):
        u, v = hcoord(a, b, G)
        if v < -0.55 and (b - G.hy) % 2.4 < 0.7:     # 정수리 물결 줄
            return B_BAR
        return B_YEL
    return B_GREEN_L if belly(a, b, G, 0.5, 0.6, 0.3) else B_GREEN


def b_extra(f, rig, G, P, small):
    """목 점 넷(가운데 둘 까망 · 양끝 보라)"""
    for i, du in enumerate((-0.62, -0.22, 0.22, 0.62)):
        x, y = rig.cell(G.hx + G.ht + du * G.hr, G.hy + G.hr * 0.8)
        if small and i in (0, 3):
            continue
        f[x, y] = B_SPOT if i in (0, 3) else B_BAR


spec("budgie", "사랑앵무", skin=b_skin, extra=b_extra,
     wing=lambda al, ac, sg: B_BAR if bands(al, 1.5, 0.5) and al > -0.6 else B_WING,
     beak="hook", beak_col=(B_BEAK, hx("c8a870ff")), cere=B_CERE, foot=hx("c89aa0ff"),
     hr=6.2, hy=-5.8, ra=6.0, rb=6.4, tail=dict(pts=[(1.0, -2.0), (3.6, 2.4), (6.0, 7.0)], r=(1.6, 0.8),
                                                  col=lambda s: B_TAIL))

# 3 왕관앵무 — 노란 얼굴 · 주황 볼 · 솟은 볏 · 회색 몸 · 날개 흰 띠
C_GREY, C_GREY_D, C_GREY_L, C_YEL, C_ORA = hx("9ea3abff"), hx("7a7f88ff"), hx("c2c6ccff"), hx("ffe26eff"), hx("f2863aff")


def c_skin(a, b, G):
    if in_head(a, b, G):
        u, v = hcoord(a, b, G)
        return C_ORA if blob(abs(u), v, 0.54, 0.34, 0.24, 0.24) else C_YEL
    return C_GREY_L if belly(a, b, G, 0.5, 0.6, 0.3) else C_GREY


spec("cockatiel", "왕관앵무", skin=c_skin,
     wing=lambda al, ac, sg: WHITE if -0.5 < al < 0.15 and ac * sg > 0.1 else C_GREY_D,
     beak="hook", beak_col=(hx("b8aca8ff"), hx("8a8080ff")), foot=hx("c8a0a0ff"), crest=True, rim=RIM_WARM,
     hr=6.2, hy=-5.6, ra=6.0, rb=6.4, tail=dict(pts=[(1.0, -2.0), (3.4, 2.6), (5.4, 7.6)], r=(1.6, 0.8),
                                                  col=lambda s: C_GREY_D))

# 4 참새 — 갈색 머리 · 흰 볼에 까만 점 · 까만 턱 · 통통
S_CAP, S_BROWN, S_BROWN_D, S_BELLY, S_WHITE = hx("9a5632ff"), hx("b07c4cff"), hx("6e4a30ff"), hx("e6dfd2ff"), hx("fbf6ecff")


def s_skin(a, b, G):
    if in_head(a, b, G):
        u, v = hcoord(a, b, G)
        if v < -0.22:
            return S_CAP
        if blob(abs(u), v, 0.58, 0.32, 0.17, 0.17):
            return J_BLACK
        if abs(u) < 0.26 and v > 0.55:
            return J_BLACK
        return S_WHITE
    if belly(a, b, G, 0.6, 0.7, 0.25):
        return S_BELLY
    return S_BROWN if (b * 2.0 + abs(a)) % 3 > 0.8 else S_BROWN_D


spec("sparrow", "참새", skin=s_skin,
     wing=lambda al, ac, sg: S_WHITE if abs(al + 0.25) < 0.12 else S_BROWN_D if bands(al + ac, 1.7, 0.6) else S_BROWN,
     beak="small", beak_col=(hx("5a4a40ff"), hx("3a2a30ff")), foot=hx("d0a088ff"),
     hr=6.4, hy=-4.8, ra=6.9, rb=6.0, tail=dict(pts=[(2.0, -2.0), (5.0, 1.0), (6.6, 2.4)], r=(1.8, 1.5),
                                                  col=lambda s: S_BROWN_D))

# 5 뱁새 — 갈색 동그란 몸 · 작은 부리 · 긴 꼬리
T_HEAD, T_BODY, T_BELLY, T_WING, T_TAIL = hx("c27a4eff"), hx("c99a72ff"), hx("f1dcc0ff"), hx("9a6a46ff"), hx("8a6244ff")


def t_skin(a, b, G):
    if in_head(a, b, G):
        u, v = hcoord(a, b, G)
        return T_BELLY if v > 0.5 and abs(u) < 0.5 else T_HEAD
    return T_BELLY if belly(a, b, G, 0.6, 0.72, 0.15) else T_BODY


spec("crowtit", "뱁새", skin=t_skin, wing=lambda al, ac, sg: T_TAIL if al > 0.5 else T_WING,
     beak="tiny", beak_col=(hx("5a4a44ff"), hx("5a4a44ff")), foot=hx("8a7a70ff"), eye="big",
     hr=6.8, hy=-3.9, ra=7.0, rb=6.2, by=2.6, wl=4.2,
     tail=dict(pts=[(2.5, -2.0), (6.5, 1.2), (10.5, 4.6), (13.0, 6.6)], r=(1.5, 1.0), col=lambda s: T_TAIL))

# 6 시마에나가 — 새하얀 찹쌀떡 · 까만 점 눈 · 긴 꼬리
M_WHITE, M_CREAM, M_BLACK, M_PINK = hx("fffdf8ff"), hx("f4ede2ff"), hx("3a3236ff"), hx("e8b4bcff")


def m_skin(a, b, G):
    if in_head(a, b, G):
        return M_WHITE
    return M_CREAM if belly(a, b, G, 0.55, 0.55, 0.45) else M_WHITE


spec("shimaenaga", "시마에나가", skin=m_skin,
     wing=lambda al, ac, sg: M_PINK if al < -0.45 else WHITE if ac * sg > 0.45 else M_BLACK,
     beak="tiny", beak_col=(M_BLACK, M_BLACK), foot=M_BLACK, eye="dot", rim=RIM_GREY,
     hr=7.0, hy=-3.0, ra=7.6, rb=6.0, by=2.6, wl=4.0, ww=2.2, eyex=0.4, eyey=0.05,
     tail=dict(pts=[(2.0, -2.0), (5.0, 1.8), (7.6, 5.6)], r=(2.0, 1.4),
               col=lambda s: M_BLACK if s < 0.8 else WHITE))

# 7 병아리 — 노란 솜털 · 주황 부리 · 발 · 머리 위 솜털 한 가닥
K_YEL, K_YEL_L, K_YEL_D, K_ORA = hx("ffe476ff"), hx("fff2b4ff"), hx("f2c84aff"), hx("f59a2aff")


def k_skin(a, b, G):
    if in_head(a, b, G):
        return K_YEL
    return K_YEL_L if belly(a, b, G, 0.55, 0.6, 0.3) else K_YEL


def k_extra(f, rig, G, P, small):
    """머리 위 솜털 두 가닥 · 볼터치"""
    x, y = rig.cell(G.hx + G.ht * 0.5, G.hy - G.hr)
    for p in ((x, y - 1), (x - 1, y - 2), (x + 1, y - 1), (x + 2, y - 2)) if not small else ((x, y - 1), (x + 1, y - 2)):
        f[p] = OUT
    if not small:
        blush(f, rig, G)


def blush(f, rig, G):
    for sg in (-1, 1):
        bx, by = rig.cell(G.hx + G.ht + sg * G.hr * 0.66, G.hy + G.hr * 0.32)
        f[bx, by] = BLUSH
        f[bx + (1 if sg < 0 else -1), by] = BLUSH


spec("chick", "병아리", skin=k_skin, extra=k_extra, wing=lambda al, ac, sg: K_YEL_D if al > 0.4 else K_YEL,
     beak="small", beak_col=(K_ORA, hx("d07a1aff")), foot=K_ORA,
     hr=7.4, hy=-3.2, ra=7.0, rb=6.0, by=3.0, wl=3.4, ww=2.2, beaky=0.28)

# 8 아기오리 — 노란 몸 · 넓적한 주황 부리 · 물갈퀴
D_YEL, D_YEL_D, D_YEL_L, D_BILL, D_BILL_D = hx("ffd23cff"), hx("e6b028ff"), hx("ffe88cff"), hx("f58a2aff"), hx("c8641aff")


def d_skin(a, b, G):
    if in_head(a, b, G):
        u, v = hcoord(a, b, G)
        return D_YEL_D if v < -0.7 else D_YEL
    return D_YEL_L if belly(a, b, G, 0.55, 0.6, 0.3) else D_YEL


spec("duckling", "아기오리", skin=d_skin, extra=lambda f, rig, G, P, small: None if small else blush(f, rig, G),
     wing=lambda al, ac, sg: D_YEL_D if al > 0.3 else D_YEL,
     beak="flat", beak_col=(D_BILL, D_BILL_D), foot=D_BILL, toes=4,
     hr=6.6, hy=-5.6, ra=6.6, rb=5.6, by=3.2, wl=3.8, beaky=0.38,
     tail=dict(pts=[(3.0, -3.0), (6.4, -5.0)], r=(1.5, 0.8), col=lambda s: D_YEL_D))

# 9 카나리아 — 진노랑 · 늘씬 · 날개 끝 주황 줄 · 노래
Y_YEL, Y_YEL_L, Y_ORA, Y_OLIVE = hx("fcce1aff"), hx("ffe466ff"), hx("f2a21aff"), hx("c8a020ff")


def y_skin(a, b, G):
    if in_head(a, b, G):
        return Y_YEL
    return Y_YEL_L if belly(a, b, G, 0.5, 0.62, 0.3) else Y_YEL


spec("canary", "카나리아", skin=y_skin,
     wing=lambda al, ac, sg: Y_OLIVE if al > 0.55 else Y_ORA if bands(al, 1.6, 0.55) else Y_YEL,
     beak="small", beak_col=(hx("f6c0a8ff"), hx("d89a84ff")), foot=hx("e8b0a0ff"), eye="big",
     hr=5.9, hy=-6.0, ra=5.7, rb=6.6, by=2.4, wl=4.8, ww=2.2,
     tail=dict(pts=[(1.0, -2.0), (3.6, 2.0), (5.6, 5.4)], r=(1.7, 1.3), col=lambda s: Y_OLIVE if s > 0.6 else Y_ORA))

# 10 아기펭귄 — 회색 솜털 · 까만 머리에 흰 얼굴 가면 · 지느러미
P_GREY, P_GREY_L, P_GREY_D, P_BLACK = hx("a9aeb7ff"), hx("dadde2ff"), hx("80868fff"), hx("2c2c34ff")


def p_skin(a, b, G):
    if in_head(a, b, G):
        u, v = hcoord(a, b, G)
        if abs(u) > 0.12 and blob(abs(u), v, 0.44, 0.2, 0.36, 0.52):   # 흰 고글 둘 — 가운데는 까만 줄로 갈라 둔다
            return WHITE
        return P_BLACK
    return P_GREY_L if belly(a, b, G, 0.55, 0.62, 0.3) else P_GREY


spec("penguin", "아기펭귄", skin=p_skin, wing=lambda al, ac, sg: P_GREY_D,
     beak="tiny", beak_col=(hx("6a6a76ff"), hx("6a6a76ff")), foot=hx("4a4a54ff"), rim=RIM_GREY, toes=4,
     hr=5.8, hy=-5.6, ra=7.8, rb=7.0, by=2.6, wl=5.2, ww=1.9, eyex=0.44, eyey=0.1, beaky=0.42)

ORDER = ["javasparrow", "budgie", "cockatiel", "sparrow", "crowtit", "shimaenaga", "chick", "duckling",
         "canary", "penguin"]


# ── 새 한 마리 ────────────────────────────────────────────────────────────────
# body · tailon 을 끄면 머리만(핀 · 조준점), tuft 는 머리 위 깃 두 가닥, props 는 날개 밑 · 몸 위에 끼울 부위(깃펜)
DEF = dict(sq=0.0, puff=1.0, hdx=0.0, hdy=0.0, ht=0.0, wl=("fold", 0), wr=("fold", 0), mood="open", beak_open=False,
           crest=0.5, tail=0.0, feet=True, ground=None, body=True, tailon=True, tuft=False, props=())

WPOSE = {   # 오른 날개(sg=+1) 기준 (중심 u 비율 · 중심 v 덧 · 길이배 · 굵기배 · 끝 방향) — 왼쪽은 거울
    "fold": lambda G, L: (G.ra * 0.80, G.by + 0.4, 1.0, 1.0, math.pi / 2 - 0.35),
    "out": lambda G, L: (G.ra + L * 0.55, G.by - 1.4, 1.0, 0.9, -0.3),
    "up": lambda G, L: (G.ra + L * 0.2, G.by - L * 0.85, 1.0, 0.9, -math.pi / 2 + 0.55),
    "cross": lambda G, L: (0.2, G.by - 0.8, 1.5, 0.72, math.pi / 2 + 0.72),
    "cover": lambda G, L: (G.hx + G.ht + 2.6, G.hy + G.hr * 0.62, 0.95, 0.7, math.pi + 0.2),
}


def wing_pose(B, G, sg, kind, t=0.0):
    """kind 꼴 날개. kind 가 (a, b) 둘이면 t 만큼 섞는다(날갯짓)"""
    def one(k):
        cx, cy, lm, wm, ang = WPOSE[k](G, B.wl)
        return [cx, cy, B.wl * lm, B.ww * wm, ang]
    if isinstance(kind, tuple):
        p0, p1 = one(kind[0]), one(kind[1])
        w = [p0[i] + (p1[i] - p0[i]) * t for i in range(5)]
    else:
        w = one(kind)
    cx, cy, L, W, ang = w
    if kind == "cover" or (isinstance(kind, tuple) and "cover" in kind):
        return (cx if sg > 0 else 2 * (G.hx + G.ht) - cx, cy, L, W, ang if sg > 0 else math.pi - ang)
    return (sg * cx, cy, L, W, ang if sg > 0 else math.pi - ang)


def wing_aim(B, G, sg, ang, lm=1.0, wm=0.85):
    """sg 쪽 어깨에서 ang(라디안, 0 = 오른쪽 · 아래가 +) 쪽으로 쭉 뻗은 날개 — 기지개 · 깃펜 쥐기"""
    rx, ry = sg * G.ra * 0.55, G.by - G.rb * 0.3
    L = B.wl * lm
    return (rx + math.cos(ang) * L * 0.8, ry + math.sin(ang) * L * 0.8, L, B.ww * wm, ang)


def tuft_hit(G):
    """머리 위로 솟은 깃 두 가닥(핀 위로 삐죽) — 긴 것은 왼쪽으로, 짧은 것은 오른쪽으로 휜다"""
    b0 = (G.hx + G.ht * 0.4, G.hy - G.hr * 0.6)
    return any_of(chain([b0, (b0[0] - 0.4, b0[1] - G.hr * 0.8), (b0[0] - 1.8, b0[1] - G.hr * 1.3)], 1.1, 0.6),
                  chain([(b0[0] + 0.8, b0[1]), (b0[0] + 1.4, b0[1] - G.hr * 0.7), (b0[0] + 2.6, b0[1] - G.hr * 1.0)],
                        1.0, 0.55))


def wing_hit(w):
    cx, cy, L, W, ang = w
    c, s = math.cos(ang), math.sin(ang)

    def uv(a, b):
        da, db = a - cx, b - cy
        al = (da * c + db * s) / L
        ac = (-da * s + db * c) / W
        return al, ac / (1 - 0.4 * max(0.0, al))

    def hit(a, b):
        al, ac = uv(a, b)
        return al * al + ac * ac <= 1
    return hit, uv


def bird(rig: Rig, B, P=None):
    """새 한 마리 → ({칸: 색}, 칸 집합, G). P 는 자세(DEF 참고)"""
    P = {**DEF, **(P or {})}
    ink(OUT, HI, B.rim)
    puff, sq = P["puff"], P["sq"]
    FL = B.by + B.rb                                  # 발 줄(몸 밑)은 그대로 두고 위로 부풀거나 줄어든다
    ra, rb = B.ra * puff * (1 + 0.08 * sq), B.rb * puff * (1 - 0.14 * sq)
    by = FL - rb
    G = NS(hx=P["hdx"], hy=B.hy + (by - B.by) - (B.hr * puff - B.hr) * 0.6 + P["hdy"], hr=B.hr * puff, ht=P["ht"],
           bx=0.0, by=by, ra=ra, rb=rb, FL=FL)
    parts, behind = [], []
    for sg, key in ((-1, "wl"), (1, "wr")):
        v = P[key]       # "꼴" 또는 ("꼴", 0) 또는 (("꼴", "꼴"), 섞음) 또는 ("aim", 방향, 길이배)
        if v is None:
            continue
        if v[0] == "aim":     # 쭉 뻗은 날개는 몸 뒤로 — 앞에 두면 머리 옆을 지나며 얼굴을 덮는다. 다섯째가 참이면 앞
            hit, uv = wing_hit(wing_aim(B, G, sg, *v[1:4]))
            front = len(v) > 4 and v[4]
            (parts if front else behind).append(
                (f"wing{sg}", hit, (lambda uv, sg: lambda a, b: B.wing(*uv(a, b), sg))(uv, sg), front))
            continue
        kind, t = (v, 0) if isinstance(v, str) else v
        w = wing_pose(B, G, sg, kind, t)
        hit, uv = wing_hit(w)
        parts.append((f"wing{sg}", hit, (lambda uv, sg: lambda a, b: B.wing(*uv(a, b), sg))(uv, sg), True))
    parts += list(P["props"])
    parts.append(("bird", any_of(ell(G.hx, G.hy, G.hr, G.hr), ell(0.0, by, ra, rb)) if P["body"] else
                  ell(G.hx, G.hy, G.hr, G.hr), lambda a, b: B.skin(a, b, G), False))
    parts += behind
    if P["tuft"]:
        top = B.skin(G.hx + G.ht, G.hy - G.hr * 0.85, G)
        parts.append(("tuft", tuft_hit(G), top, False))
    if B.crest:
        parts.append(("crest", crest_hit(G, P["crest"]), lambda a, b: C_YEL if b > G.hy - G.hr - 3.6 else C_GREY, False))
    if B.tail and P["tailon"]:
        sw = P["tail"]
        c, s = math.cos(sw), math.sin(sw)
        x0, y0 = 0.0, FL
        pts = [(x0 + u * c - v * s, y0 + u * s + v * c) for u, v in B.tail["pts"]]
        total = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:]))

        def tcol(a, b, pts=pts, total=total):
            d = math.hypot(a - pts[0][0], b - pts[0][1])
            return B.tail["col"](min(1.0, d / total))
        parts.append(("tail", chain(pts, *B.tail["r"]), tcol, False))
    out, mask, _ = draw(rig, parts)
    small = rig.k * B.hr < 5.0
    face(out, rig, B, G, P, small)
    if B.extra:
        B.extra(out, rig, G, P, small)
    if P["feet"]:
        feet(out, mask, rig, B, G, P["ground"], small)
    return out, mask, G


def crest_hit(G, raise_):
    """왕관앵무 볏 — 깃 셋. raise_ 0 이면 뒤로 눕고 1 이면 곧추선다"""
    th = 1.0 - 0.95 * raise_
    base = (G.hx + G.ht * 0.4 + 0.4, G.hy - G.hr * 0.75)
    hs = []
    for off, ln in ((0.0, 1.0), (-1.4, 0.8), (1.3, 0.65)):
        b0 = (base[0] + off, base[1])
        p1 = (b0[0] + 3.4 * ln * math.sin(th), b0[1] - 3.4 * ln * math.cos(th))
        p2 = (p1[0] + 2.8 * ln * math.sin(th + 0.7), p1[1] - 2.8 * ln * math.cos(th + 0.7))
        hs.append(chain([b0, p1, p2], 1.1, 0.6))
    return any_of(*hs)


BEAKS = {   # 칸 글자판: b 부리 · d 짙은 부리 · m 벌린 입 · c 코(납막) · o 테두리색
    ("tiny", False): ["dd"], ("tiny", True): ["d"],
    ("small", False): ["bb", "dd"], ("small", True): ["bb"],
    ("big", False): [".bb.", "bbbb", ".dd."], ("big", True): ["bb", "dd"],
    ("flat", False): [".bbbb.", "bbbbbb", ".dddd."], ("flat", True): ["bbbb"],
    ("hook", False): ["cc", "bb", "dd"], ("hook", True): ["bb"],
    ("none", False): [""], ("none", True): [""],      # 부리를 따로 그리는 칸(hand — 위로 쳐든 부리)
}
OPEN = {
    ("tiny", False): ["dd", "mm"], ("tiny", True): ["d", "m"],
    ("small", False): ["bb", "mm", "dd"], ("small", True): ["bb", "mm"],
    ("big", False): [".bb.", "bbbb", "mmmm", "dddd"], ("big", True): ["bb", "mm"],
    ("flat", False): [".bbbb.", "bmmmmb", "bmmmmb", ".dddd."], ("flat", True): ["bbbb", "mmmm"],
    ("hook", False): ["cc", "bb", "mm", "dd"], ("hook", True): ["bb", "mm"],
}


def face(f, rig, B, G, P, small):
    mood = P["mood"]
    cx, cy = rig.world(G.hx + G.ht, G.hy + G.hr * B.beaky)
    rows = (OPEN if P["beak_open"] else BEAKS)[B.beak, small]
    if B.beak == "hook" and not getattr(B, "cere", None):
        rows = [r.replace("c", "b") for r in rows]
    w = len(rows[0])
    x0, y0 = round(cx - w / 2), math.floor(cy - 0.5)
    pal = {"b": B.beak_col[0], "d": B.beak_col[1], "m": MOUTH, "c": getattr(B, "cere", None), "o": OUT}
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != ".":
                f[x0 + i, y0 + j] = pal[ch]
    for sg in (-1, 1):
        ex, ey = rig.world(G.hx + G.ht + sg * G.hr * B.eyex, G.hy + G.hr * B.eyey)
        if small:
            x, y = math.floor(ex), math.floor(ey - 0.5)
            if mood in ("open", "angry", "wide"):
                f[x, y] = EYE
                f[x, y + 1] = EYE
                if B.eye == "ring":
                    f[x + sg, y] = B.ring
                    f[x + sg, y + 1] = B.ring
            else:
                f[x, y + 1] = EYE
            continue
        x0, y0 = round(ex - 1), round(ey - 1)
        if B.eye == "ring":
            for p in ((x0 - 1 if sg < 0 else x0 + 2, y0), (x0, y0 - 1), (x0 + 1, y0 - 1)):   # 눈테는 까만 머리 쪽만
                f[p] = B.ring
        if mood in ("open", "angry", "wide"):
            if B.eye == "dot" and mood != "wide":
                xx = x0 + (1 if sg < 0 else 0)
                f[xx, y0] = EYE
                f[xx, y0 + 1] = EYE
            else:
                for dx in (0, 1):
                    for dy in (0, 1):
                        f[x0 + dx, y0 + dy] = EYE
                f[x0, y0] = HI
            if mood == "angry":   # 안쪽으로 내려온 눈썹
                for p in ((x0 + (0 if sg < 0 else 1), y0 - 2), (x0 + (1 if sg < 0 else 0), y0 - 1)):
                    f[p] = OUT if B.id not in ("javasparrow", "penguin") else WHITE
        elif mood == "blink":
            f[x0, y0 + 1] = EYE
            f[x0 + 1, y0 + 1] = EYE
        elif mood == "sleep":   # ︶
            f[x0, y0 + 1] = EYE
            f[x0 + 1, y0 + 1] = EYE
            f[x0 - 1 if sg < 0 else x0 + 2, y0] = EYE
        elif mood == "happy":   # ^
            f[x0 - 1 if sg < 0 else x0, y0 + 1] = EYE
            f[x0 if sg < 0 else x0 + 1, y0] = EYE
            f[x0 + 1 if sg < 0 else x0 + 2, y0 + 1] = EYE
        elif mood == "squeeze":   # > <
            xa, xb = (x0, x0 + 1) if sg < 0 else (x0 + 1, x0)
            f[xa, y0 - 1] = EYE
            f[xb, y0] = EYE
            f[xa, y0 + 1] = EYE
        elif mood == "sulk":
            f[x0, y0 + (1 if sg > 0 else 0)] = EYE
            f[x0 + 1, y0 + (0 if sg > 0 else 1)] = EYE


def feet(f, mask, rig, B, G, ground, small):
    """발 둘: 몸 밑 다리 한 칸 + 발가락. ground(x) 를 주면 그 줄까지 다리를 늘이고 발가락이 그 줄을 잡는다"""
    for sg in (-1, 1):
        wx, _ = rig.world(sg * G.ra * 0.34, G.FL)
        x = math.floor(wx)
        col = [y for (xx, y) in mask if xx == x]
        if not col:
            continue
        yb = max(col) + 1
        if ground:
            gy = ground(x)
            for y in range(yb, gy):
                f[x, y] = B.foot
            for dx in (-1, 0):
                f[x + dx, ground(x + dx)] = B.foot
            continue
        f[x, yb] = B.foot
        n = 2 if small else B.toes
        xs = range(x - 1, x - 1 + n) if sg < 0 else range(x + 2 - n, x + 2)
        for xx in xs:
            f[xx, yb + 1] = B.foot


def mark(f, x, y):
    """화남 표시(💢 꼴 네 갈래)"""
    for p in ((x, y), (x + 2, y), (x, y + 2), (x + 2, y + 2), (x + 1, y - 1), (x - 1, y + 1), (x + 3, y + 1),
              (x + 1, y + 3)):
        f[p] = ANGRY


# ── arrow: 머리에 이기 (carry) ────────────────────────────────────────────────
# 1배 흰 윈도우 화살표를 정수리에 곧게 이고 그 밑에 앞모습 새가 세로로 쌓인다. 화살표 끝 (1, 1) 은 커서라
# 움직일 수 없으니 새가 그 밑에서 뛴다 — 화살표를 따라가는 눈으로 보면 화살표가 머리에서 떴다 다시 얹힌다.
# 뛰는 장(틈 > 0)이 아니면 화살표 밑동이 늘 정수리에 닿는다(carry 안에서 재서 맞춘다)
CARRY_S, CARRY_TOP = 1.0, 16.0    # 화살표 배율 · 쉴 때 머리 꼭대기 줄(꼬리 아랫단 16–17줄이 정수리 뒤로 한 칸 숨는다)
CARRY: list = []                  # arrow() 가 장마다 남기는 새 층(화살표 빼고 테 두른 것) — write_carry 가 쓴다
CARRY_ROT: list = []              # 같은 장들의 화살표 기울기(도) — 매끈한 모양도 끝을 축으로 같이 기운다
RING_SOFT = hx("f4a6b4ff")        # 문조 눈테 — 진한 빨강 막대는 1배에서 화난 눈썹 · 빨간 덩어리로 읽혀 연분홍 한 칸으로
DUST = hx("c8ccd4ff")
# 뛰는 새: 장마다 (틈 · 쪼그림 sq · 날개 위로 t · 화살표 기울기(도, 음수만 — 양수면 x=0 으로 나간다) · 눈 · 부리 · 먼지)
HOP = [
    (0, 0.0, 0.2, 0, "open", False, False),     # 0 서 있음
    (0, 0.9, 0.15, 0, "open", False, False),    # 1 움찔
    (0, 1.8, 0.1, 0, "happy", False, False),    # 2 꾹 쪼그림
    (0, -0.8, 0.6, 0, "happy", True, True),     # 3 박참 — 아직 화살표를 이고 있다
    (2, 0.8, 0.8, -4, "happy", True, False),    # 4 화살표가 기울며 머리에서 막 떨어진다 — 공중에선 몸을 공처럼 웅크린다
    (3, 1.2, 0.6, -7, "open", False, False),    # 5 꼭대기 — 화살표와 머리 사이 빈 줄 하나(판 32줄이 꽉 차 더는 못 벌린다)
    (2, 0.8, 0.4, -4, "open", False, False),    # 6 다시 내려앉기 직전
    (0, 0.0, 0.5, 0, "open", False, False),     # 7 다시 받음
    (0, 1.4, 0.3, 0, "happy", False, True),     # 8 착지 꾹
    (0, 0.5, 0.2, 0, "open", False, False),     # 9
    (0, 0.0, 0.2, 0, "open", False, False),     # 10
    (0, 0.0, 0.2, 0, "blink", False, False),    # 11 끔뻑
]
# 마리마다: wing 날개 드는 한도 · waddle 날지 않고 뒤뚱(펭귄 · 병아리 · 아기오리) · puff · crest 볏 · blush 볼터치
CARRY_OPT = {
    "budgie": dict(wing=0.15),                    # 날개를 들면 줄무늬가 X 로 뭉개진다 — 접은 채
    "cockatiel": dict(crest=0.0),                 # 볏을 뒤로 눕혀 화살표 날개를 비킨다
    "crowtit": dict(blush=True, puff=1.05),
    "shimaenaga": dict(nowing=True, puff=1.06),   # 접은 까만 날개도 1배에선 짧은 팔다리로 읽힌다 — 날개 없이 찹쌀떡 그대로
    "chick": dict(waddle=True),
    "duckling": dict(waddle=True),
    "penguin": dict(waddle=True),
}


def arrow_mask(rot: float = 0.0) -> set:
    """끝 (1, 1) 을 축으로 rot 도 돌린 CARRY_S 배 화살표"""
    t = math.radians(rot)
    c, s = math.cos(t), math.sin(t)
    return raster([(1 + (x * c - y * s) * CARRY_S, 1 + (x * s + y * c) * CARRY_S) for x, y in PEEK_CUR])


def chibi(B):
    """머리에 이기용 몸과 배율 — 머리를 키우고 몸을 낮춰 화살표 밑 16줄(16–31)에 발까지 든다"""
    fl = B.by * 0.8 + B.rb * 0.70
    k = min(0.85, 14.0 / (1.55 * 1.08 * B.hr + fl))
    d = dict(vars(B))
    hr = max(B.hr * 1.08, 5.15 / k)             # 얼굴이 작은 그림(small)으로 안 떨어지게
    d.update(hr=hr, hy=-hr * 0.55, rb=B.rb * 0.70, by=B.by * 0.8, ra=B.ra * 1.08)
    return NS(**d), k


def carry_eyes(g, rig, B, G, mood):
    """문조 눈테를 눈 바깥 아래 연분홍 한 칸으로 줄이고, 까만 머리에 묻히는 ^ 눈은 밝은 색으로 다시 찍는다"""
    for sg in (-1, 1):
        ex, ey = rig.world(G.hx + G.ht + sg * G.hr * B.eyex, G.hy + G.hr * B.eyey)
        x0, y0 = round(ex - 1), round(ey - 1)
        side = x0 - 1 if sg < 0 else x0 + 2
        if B.eye == "ring":
            for p in ((side, y0), (x0, y0 - 1), (x0 + 1, y0 - 1)):
                if g.get(p) == B.ring:
                    g[p] = B.skin(*rig.local(p[0] + 0.5, p[1] + 0.5), G)
        skin = B.skin(*rig.local(ex, ey), G)
        if mood == "happy" and sum(skin[:3]) < 250:
            for p in ((x0 - 1 if sg < 0 else x0, y0 + 1), (x0 if sg < 0 else x0 + 1, y0), (x0 + 1 if sg < 0 else x0 + 2, y0 + 1)):
                g[p] = RING_SOFT if B.eye == "ring" else HI
        elif B.eye == "ring" and mood != "blink":
            g[side, y0 + 1] = RING_SOFT


def touches(bird_cells, am) -> bool:
    return any((x + dx, y + dy) in bird_cells for x, y in am for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1)))


def carry_seq(B, opt):
    """장마다 (틈, 자세 P, 기울기, 먼지)"""
    out = []
    if opt.get("waddle"):     # 날지 않는 새 — 좌우로 뒤뚱, 오른쪽으로 기울 때 화살표도 같이 기운다
        for k, ph in enumerate(phases()):
            s = math.sin(ph)
            P = dict(ang=7.0 * s, sq=0.7 * abs(math.cos(ph)), mood="blink" if k == 11 else "happy" if k in (3, 9) else "open",
                     wl=(("fold", "out"), 0.45 * max(0.0, -s)), wr=(("fold", "out"), 0.45 * max(0.0, s)),
                     beak_open=k in (3, 4), tail=0.15 * s)
            out.append((0, P, -4.0 * max(0.0, s), False))
        return out
    for k, (gap, sq, up, rot, mood, beak, dust) in enumerate(HOP):
        t = min(up, opt.get("wing", 1.0))
        wing = None if opt.get("nowing") else (("fold", "up"), t)
        out.append((gap, dict(sq=sq, mood=mood, wl=wing, wr=wing, beak_open=beak, feet=gap == 0,
                              tail=0.1 * math.sin(2 * math.pi * k / N)), rot, dust))
    return out


def arrow(B) -> list[dict]:
    """머리에 이기 — 화살표를 정수리에 이고 통통(날지 않는 새는 뒤뚱)"""
    opt = CARRY_OPT.get(B.id, {})
    C, k_ = chibi(B)
    seq = carry_seq(B, opt)
    seq = [(gap, {**P, "crest": opt.get("crest", 0.5), "puff": opt.get("puff", 1.0)}, rot, dust)
           for gap, P, rot, dust in seq]
    # 가로 자리는 한 번만 — 날개를 든 장까지 다 재서 제일 넓은 장의 왼끝이 x=1 안에 들게(장마다 옮기면 덜컥인다)
    lo = min(min(x for x, _ in bird(Rig(9.5, 16.0, P.get("ang", 0.0), k_), C, P)[0]) for _, P, _, _ in seq)
    ox = 9.5 + max(0, 1 - lo)
    top = max(q[0] for q in seq)
    frames = []
    CARRY.clear()
    CARRY_ROT.clear()
    for gap, P, rot, dust in seq:
        P = dict(P)
        ang = P.pop("ang", 0.0)
        am = arrow_mask(rot)
        for _ in range(4):
            _, _, G0 = bird(Rig(0, 0, 0, k_), C, P)
            oy = CARRY_TOP + gap - (G0.hy - G0.hr) * k_
            over = oy + G0.FL * k_ + (2 if P.get("feet", True) else 0) - 32   # 몸 밑단(+발)이 판 밑으로 나가면 올린다
            if over > 0:
                oy -= math.ceil(over)
            # 꼭대기 장은 머리와 화살표 사이에 빈 줄이 있어야 뛴 걸로 읽힌다 — 키 큰 새(볏 · 솜털)는 판 밑에
            # 걸려 못 내려가니 공처럼 더 웅크려 키를 줄인다
            if gap == top and touches(set(bird(Rig(ox, oy, ang, k_), C, P)[0]), am):
                P["sq"] += 0.4
                continue
            break
        for _ in range(4):
            g, mask, G = bird(Rig(ox, oy, ang, k_), C, P)
            if gap == 0 and not touches(set(g), am):   # 뛰는 장이 아니면 밑동이 정수리에 닿을 때까지 올린다
                oy -= 1
                continue
            break
        else:
            print(f"  ! {B.id}/arrow: 화살표 밑동을 정수리에 못 붙임")
        if gap and gap == top and touches(set(g), am):
            print(f"  ! {B.id}/arrow: 꼭대기 장인데 화살표와 머리 사이에 빈 줄이 없음")
        rig = Rig(ox, oy, ang, k_)
        carry_eyes(g, rig, C, G, P["mood"])
        if opt.get("blush"):
            blush(g, rig, G)
        f = {}
        solid(f, am, sea.Cur(PEEK_WHITE), sea.Cur(OUT))       # 화살표 먼저 — 꼬리 아랫단이 정수리 뒤로 숨는다. 화살표는 커서
        f.update(g)
        layer = dict(g)
        if dust:   # 박찰 때 · 내려앉을 때 발밑 먼지
            yb = max(y for _, y in mask) + 2
            xs = sorted(x for x, _ in g)
            for x, dy in ((xs[0] - 1, 1), (xs[0], 0), (xs[-1], 0), (xs[-1] + 1, 1)):
                f.setdefault((x, yb - dy), DUST)
                layer.setdefault((x, yb - dy), DUST)
        CARRY_ROT.append(rot)
        CARRY.append(finish({p: c for p, c in layer.items() if 1 <= p[0] <= 31 and 1 <= p[1] <= 31}))
        f[1, 1] = sea.Cur(OUT)
        frames.append(finish({p: c for p, c in f.items() if 1 <= p[0] <= 31 and 1 <= p[1] <= 31}))
    return frames


# ── wait: 마리마다 제 버릇 ─────────────────────────────────────────────────────
def zz(f, k, x, y, col=OUT):
    """졸음 z 둘이 피어오른다"""
    for i in range(2):
        t = (k / N + i * 0.5) % 1
        zx, zy = round(x + t * 3), round(y - t * 5)
        for p in ((zx, zy), (zx + 1, zy), (zx + 1, zy + 1), (zx, zy + 2), (zx + 1, zy + 2)) if i == 0 else \
                ((zx, zy), (zx, zy + 1)):
            f[p] = col


def nest(f, cx, top, w=12.0, front=True):
    """둥지 그릇: 짚 색 반달 + 짚 줄. front 면 테두리까지 그린다"""
    m = {(x, y) for y in range(top, top + 7) for x in range(round(cx - w), round(cx + w))
         if ((x + 0.5 - cx) / w) ** 2 + ((y + 0.5 - top) / 6.5) ** 2 <= 1}

    def col(p):
        if p[1] == top:
            return NEST_L
        return NEST_D if (p[0] + 2 * p[1]) % 5 == 0 or (p[0] - p[1]) % 7 == 0 else NEST
    solid(f, m, col, OUT)


def wait_javasparrow(B):
    """둥지에서 알을 품고 꾸벅꾸벅 — 졸다가 장 9 에 몸을 들어 알을 한 번 살피고 다시 앉는다"""
    frames = []
    nod = [0, 0, 0.4, 0.8, 1.2, 1.4, 1.4, 1.4, 1.0, 0, 0, 0]
    mood = ["open", "open", "blink", "blink", "sleep", "sleep", "sleep", "sleep", "sleep", "open", "happy", "open"]
    for k in range(N):
        f = {}
        lift = 2.0 if k in (9, 10) else 0.0
        rig = Rig(16.0, 15.5 - lift, 0.0, 0.92)
        g, _, _ = bird(rig, B, dict(hdy=nod[k], mood=mood[k], feet=False))
        f.update(g)
        if lift:   # 알 두 개가 보인다
            for cx in (13, 18):
                solid(f, disc(cx + 0.5, 22.0, 2.2), SHELL, OUT)
        f = {p: c for p, c in f.items() if p[1] < 23}
        nest(f, 16.0, 22, 12.5)
        if 4 <= k <= 8:
            zz(f, k - 4, 23, 6)
        frames.append(finish(f))
    return frames


def wait_budgie(B):
    """거울 앞에서 수다 — 거울 쪽으로 고개를 까딱이며 부리를 짹짹, 거울 속 초록 그림자, 말 점이 오간다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        mx, my = 25.5, 12.0
        solid(f, {(x, y) for x, y in disc(mx, my, 5.2) if abs(x + 0.5 - mx) <= 3.8}, GLASS, FRAME_D)
        for y in range(17, 26):
            f[25, y] = FRAME_D
        for x in range(22, 30):
            f[x, 26] = FRAME_D
        f[24, 9] = GLASS_L
        f[24, 10] = GLASS_L
        f[25, 8] = GLASS_L
        for p in disc(26.0, 13.0, 2.0):   # 거울 속 앵무
            f[p] = B_GREEN
        for p in disc(26.0, 10.6, 1.4):
            f[p] = B_YEL
        nodd = math.sin(2 * ph)
        rig = Rig(12.0, 15.0, 0.0, 0.88)
        talk = k % 3 != 2
        g, _, _ = bird(rig, B, dict(ht=0.5 + 0.4 * nodd, hdx=0.5 + 0.4 * nodd, hdy=0.5 * max(0.0, nodd),
                                    beak_open=talk and k % 2 == 0, mood="blink" if k == 6 else "open",
                                    tail=0.06 * math.sin(ph)))
        f.update(g)
        if talk:   # 말 점 ··
            for i in range(3):
                if (k + i) % 3 != 0:
                    f[18 + i * 2, 6 - (i % 2)] = NOTE[i % 3]
        frames.append(finish(f))
    return frames


def wait_cockatiel(B):
    """횃대에 앉아 볏을 천천히 올렸다 내렸다 — 다 올라가면 눈이 동그래지고 볼이 빛난다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        c = 0.5 - 0.5 * math.cos(ph)
        rig = Rig(16.0, 17.0, 0.0, 0.86)
        g, _, _ = bird(rig, B, dict(crest=c, mood="blink" if k == 9 else "open", tail=0.05 * math.sin(ph)))
        f.update(g)
        for x in range(4, 29):
            f.setdefault((x, 26), WOOD)
            f[x, 27] = WOOD_D
        f[4, 26] = f[28, 26] = WOOD_D
        if c > 0.9:
            for p in ((24, 4), (24, 5), (24, 7)):
                f[p] = OUT
        frames.append(finish(f))
    return frames


def wait_sparrow(B):
    """땅에 흩어진 모이를 콕콕 — 고개를 숙일 때마다 낟알이 하나씩 사라진다"""
    frames = []
    seeds = [(8, 27), (11, 28), (21, 27), (24, 28), (14, 29)]
    peck = [0, 0, 1, 2, 1, 0, 0, 0, 1, 2, 1, 0]
    for k in range(N):
        f = {}
        eaten = (1 if k >= 4 else 0) + (1 if k >= 10 else 0)
        for i, (x, y) in enumerate(seeds):
            if i >= eaten:
                f[x, y] = SEED
                f[x + 1, y] = SEED_D
        rig = Rig(16.0, 16.0, 0.0, 0.9)
        p = peck[k]
        g, _, _ = bird(rig, B, dict(hdy=1.6 * p, sq=0.4 * p, mood="happy" if p == 2 else "open",
                                    tail=-0.12 * p, beak_open=k in (5, 11)))
        f.update(g)
        frames.append(finish(f))
    return frames


def wait_crowtit(B):
    """가지 끝에 앉아 가지째 살랑살랑 흔들 — 긴 꼬리가 반대로 흔들린다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sw = 6.0 * math.sin(ph)
        piv = (2.0, 28.0)
        br = Rig(piv[0], piv[1], -14.0 + sw * 0.5, 1.0)
        o, _, _ = draw(br, [("leaf", any_of(ell(23.5, -2.0, 2.4, 1.2, -0.5), ell(25.0, 2.0, 2.2, 1.1, 0.5)), LEAF, True),
                            ("branch", bar((0.0, 0.0), (27.0, 0.0), 1.3, 0.8), WOOD, False)])
        ink(OUT, HI, B.rim)
        perch_x, perch_y = br.world(15.0, -1.0)
        rig = Rig(perch_x, perch_y - (B.by + B.rb + 2.0) * 0.84, sw * 0.6, 0.84)
        g, _, _ = bird(rig, B, dict(tail=-0.25 * math.sin(ph), mood="blink" if k == 5 else "open",
                                    wl=(("fold", "out"), max(0.0, -math.sin(ph)) * 0.4),
                                    wr=(("fold", "out"), max(0.0, math.sin(ph)) * 0.4)))
        f.update({p: c for p, c in o.items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31})
        f.update(g)
        frames.append(finish({p: c for p, c in f.items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31}))
    return frames


def wait_shimaenaga(B):
    """눈송이 속에서 솜털을 부풀려 동그란 찹쌀떡이 된다 — 다 부풀면 눈을 감고 흐뭇"""
    frames = []
    flakes = [(4, 3), (27, 6), (7, 15), (26, 18), (13, 2), (21, 1)]
    for k, ph in enumerate(phases()):
        f = {}
        pf = 0.5 - 0.5 * math.cos(ph)
        for i, (x, y) in enumerate(flakes):
            yy = (y + k + i * 3) % 30
            xx = x + (1 if (k + i) % 4 < 2 else 0)
            if 2 <= yy < 24:
                for p in ((xx, yy), (xx - 1, yy), (xx + 1, yy), (xx, yy - 1), (xx, yy + 1)):
                    f[p] = ICE_D if p != (xx, yy) else WHITE
        rig = Rig(15.0, 16.0, 0.0, 0.84)
        g, _, _ = bird(rig, B, dict(puff=1.0 + 0.16 * pf, mood="happy" if pf > 0.7 else "open",
                                    wl=("fold", 0), wr=("fold", 0), tail=0.05 * pf))
        f.update(g)
        frames.append(finish(f))
    return frames


def shell(f, cx, top, w=6.0):
    """깨진 알껍데기 아랫도리 — 위가 지그재그"""
    m = set()
    for y in range(top - 1, top + 6):
        for x in range(round(cx - w) - 1, round(cx + w) + 1):
            if ((x + 0.5 - cx) / w) ** 2 + ((y + 0.5 - top) / 6.0) ** 2 <= 1 and y >= top:
                m.add((x, y))
            elif y == top - 1 and abs(x + 0.5 - cx) < w - 1 and (x // 2) % 2 == 0:
                m.add((x, y))
    solid(f, m, lambda p: SHELL_D if p[1] >= top + 4 else SHELL, OUT)


def wait_chick(B):
    """알껍데기를 바지처럼 입고 삐약 점프 — 뛰어오르면 날개를 파닥이고, 바닥 그림자가 줄었다 는다"""
    frames = []
    hop = [0, 0, 1, 2.5, 3.5, 3.5, 2.5, 1, 0, 0, 0, 0]
    for k in range(N):
        f = {}
        h = hop[k]
        sh = 4 if h > 2 else 6
        for x in range(16 - sh, 16 + sh):
            f[x, 29] = hx("c8b48c90")
        rig = Rig(16.0, 16.0 - h, 0.0, 0.8)
        up = h > 2
        g, _, _ = bird(rig, B, dict(feet=False, sq=0.6 if k in (0, 1, 8) else 0.0,
                                    mood="happy" if up else "open", beak_open=k in (3, 4, 5),
                                    wl=(("fold", "up"), 0.6 if up else 0.0), wr=(("fold", "up"), 0.6 if up else 0.0)))
        f.update(g)
        shell(f, 16.0, round(22 - h), 6.8)
        if k in (3, 4, 5):
            for p in ((26, 6), (27, 5), (28, 4), (26, 9), (28, 9)):
                f[p] = OUT
        frames.append(finish(f))
    return frames


def wait_duckling(B):
    """물에 둥둥 — 위아래로 출렁이고 물결이 번진다. 물 밑은 안 보인다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        bob = math.sin(ph)
        rig = Rig(16.0, 16.4 + 0.7 * bob, 0.0, 0.88)
        g, _, _ = bird(rig, B, dict(feet=False, mood="blink" if k == 4 else "open", tail=0.12 * math.sin(2 * ph),
                                    ht=0.6 * math.sin(ph / 1), beak_open=k in (8, 9)))
        wl = 22
        f.update({p: c for p, c in g.items() if p[1] < wl})
        for x in range(1, 31):
            f[x, wl] = WATER[1]
            f[x, wl + 1] = WATER[2] if (x + k) % 4 else WATER[1]
            f[x, wl + 2] = WATER[3]
        for i in range(2):   # 번지는 물결
            r = 9 + ((k + i * 6) % N) * 0.6
            for sg in (-1, 1):
                x = round(16 + sg * r)
                if 0 <= x <= 31:
                    f[x, wl - 1] = WATER[0]
                    f[x - sg, wl - 1] = WATER[0]
        frames.append(finish(f))
    return frames


NOTE_GLYPH = [".##", ".#.", "##.", "##."]   # ♪


def note(f, x, y, col):
    for j, r in enumerate(NOTE_GLYPH):
        for i, ch in enumerate(r):
            if ch == "#":
                f[x + i, y + j] = col


def wait_canary(B):
    """고개를 좌우로 흔들며 노래 — 부리를 벌릴 때마다 음표가 하나씩 솟아 흩어진다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for i in range(3):
            t = ((k + i * 4) % N) / N
            nx, ny = 19 + i * 4 + round(2 * math.sin(2 * math.pi * t + i)), round(16 - 14 * t)
            note(f, nx, ny, NOTE[i])
        rig = Rig(14.0, 16.0, 0.0, 0.88)
        sing = k % 4 < 2
        g, _, _ = bird(rig, B, dict(ht=0.8 * math.sin(ph), hdy=-0.6 if sing else 0.0, beak_open=sing,
                                    mood="happy" if sing else "open", tail=0.06 * math.sin(ph)))
        f.update(g)
        for x in range(6, 23):
            f[x, 27] = WOOD
            f[x, 28] = WOOD_D
        frames.append(finish(f))
    return frames


def wait_penguin(B):
    """얼음판 위에서 뒤뚱뒤뚱 — 몸을 좌우로 기울이며 지느러미를 번갈아 들고 발을 바꿔 딛는다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for x in range(1, 31):
            f[x, 28] = ICE
            f[x, 29] = ICE_D
        tilt = 6.0 * math.sin(ph)
        rig = Rig(16.0 - 0.6 * math.sin(ph), 17.6, tilt, 0.86)
        s = math.sin(ph)
        g, _, _ = bird(rig, B, dict(wl=(("fold", "out"), max(0.0, s) * 0.7), wr=(("fold", "out"), max(0.0, -s) * 0.7),
                                    mood="blink" if k == 8 else "open"))
        f.update(g)
        frames.append(finish(f))
    return frames


# ── no: 빨간 금지 표지 안에서 싫다고 ────────────────────────────────────────────
def in_sign(rig_y=17.6, k_=0.7, ox=16.0):
    return Rig(ox, rig_y, 0.0, k_)


def no_frames(B, pose_of, extra=None, k_=0.7, oy=17.4, ang_of=None):
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f)
        P = pose_of(k, ph)
        rig = Rig(P.pop("ox", 16.0), oy + P.pop("dy", 0.0), ang_of(k, ph) if ang_of else 0.0, k_)
        g, _, _ = bird(rig, B, P)
        f.update({p: c for p, c in g.items() if 1 <= p[1] <= 30 and 1 <= p[0] <= 30})
        if extra:
            extra(f, k, ph)
        frames.append(finish(f))
    return frames


def no_javasparrow(B):
    """굵은 분홍 부리를 딱딱 벌렸다 다물며 몸을 앞으로 쑥 — 위협(짹!)"""
    def pose(k, ph):
        lunge = k % 4 in (1, 2)
        return dict(beak_open=lunge, puff=1.08 if lunge else 1.0, mood="angry", dy=-0.6 if lunge else 0.0,
                    wl=("out" if lunge else "fold"), wr=("out" if lunge else "fold"))

    def ex(f, k, ph):
        if k % 4 in (1, 2):
            for p in ((7, 9), (6, 8), (24, 9), (25, 8), (15, 5), (16, 5)):
                f[p] = OUT
    return no_frames(B, pose, ex)


def no_budgie(B):
    """두 날개를 가슴 앞에 X 로 엇걸고 고개를 도리도리"""
    def pose(k, ph):
        return dict(wl="cross", wr="cross", ht=1.2 * math.sin(2 * ph), mood="angry",
                    beak_open=k % 6 == 3)
    return no_frames(B, pose)


def no_cockatiel(B):
    """볏을 바짝 세우고 날개를 쫙 펴 쉭쉭 — 볼이 빨갛게 달아오른다"""
    def pose(k, ph):
        big = k % 4 < 2
        return dict(crest=1.0 if big else 0.85, wl=("out" if big else ("fold", "out")) if True else None,
                    wr="out" if big else "out", mood="angry", beak_open=big, dy=1.0)

    def ex(f, k, ph):
        if k % 4 < 2:
            for p in ((5, 13), (4, 14), (5, 15), (26, 13), (27, 14), (26, 15)):
                f[p] = OUT
    return no_frames(B, pose, ex, k_=0.64)


def no_sparrow(B):
    """흥 — 고개를 홱 돌리고 눈을 감는다. 반 바퀴마다 반대쪽으로 홱, 그때 꼬리를 탁"""
    def pose(k, ph):
        side = -1 if k < 6 else 1
        snap = k in (0, 6)
        return dict(ht=side * (1.4 if snap else 2.4), hdx=side * 0.8, mood="sulk", tail=-side * (0.3 if snap else 0.1))

    def ex(f, k, ph):
        if k in (0, 6):
            side = -1 if k < 6 else 1
            x0 = 7 if side > 0 else 24
            for y in (9, 11, 13):
                f[x0, y] = OUT
                f[x0 - side, y] = OUT
    return no_frames(B, pose, ex)


def no_crowtit(B):
    """도리도리 세차게 고개를 흔들고 긴 꼬리를 탁탁 친다"""
    def pose(k, ph):
        s = 1 if k % 2 == 0 else -1
        return dict(ht=1.6 * s, hdx=0.7 * s, mood="squeeze", tail=0.3 * s, ox=14.0)

    def ex(f, k, ph):
        s = 1 if k % 2 == 0 else -1
        for y in (8, 10):
            f[8 if s > 0 else 21, y] = OUT
    return no_frames(B, pose, ex, k_=0.66)


def no_shimaenaga(B):
    """솜털을 빵빵하게 부풀려 화남 — 부풀었다 숨을 고르며 조금 줄었다, 머리 옆에 💢"""
    def pose(k, ph):
        return dict(puff=1.12 + 0.08 * math.sin(2 * ph), mood="angry", ox=15.0)

    def ex(f, k, ph):
        if k % 6 < 4:
            mark(f, 21, 7)
    return no_frames(B, pose, ex, k_=0.68)


def no_chick(B):
    """발을 동동 구르며 삐약삐약 — 번갈아 발을 들고 날개를 파닥"""
    def pose(k, ph):
        s = k % 2
        return dict(feet=False, beak_open=k % 4 < 2, mood="squeeze", dy=-0.6 * s,
                    wl=(("fold", "up"), 0.7 * s), wr=(("fold", "up"), 0.7 * (1 - s)))

    def ex(f, k, ph):
        s = k % 2
        for i, sg in enumerate((-1, 1)):
            x = 13 if sg < 0 else 18
            y = 25 - (1 if (i == 0) == (s == 1) else 0)
            for dx in (-1, 0, 1):
                f[x + dx, y] = K_ORA
        if k % 4 < 2:
            for p in ((23, 8), (24, 7), (25, 6)):
                f[p] = OUT
    return no_frames(B, pose, ex, k_=0.7, oy=16.6)


def no_duckling(B):
    """꽥! — 넓적한 부리를 크게 벌려 소리치고 날개를 든다. 소리 줄이 퍼진다"""
    def pose(k, ph):
        q = k % 4 < 2
        return dict(beak_open=q, mood="squeeze" if q else "angry", sq=0.0 if q else 0.4,
                    wl=(("fold", "up"), 0.6 if q else 0.0), wr=(("fold", "up"), 0.6 if q else 0.0))

    def ex(f, k, ph):
        if k % 4 < 2:
            for p in ((7, 17), (6, 17), (7, 19), (6, 20), (24, 17), (25, 17), (24, 19), (25, 20)):
                f[p] = OUT
    return no_frames(B, pose, ex)


def no_canary(B):
    """노래 안 해 — 날개로 부리를 꾹 가리고 고개를 돌린다. 옆에 빗금 그은 음표"""
    def pose(k, ph):
        return dict(wr="cover", mood="sulk", ht=-0.8 if k < 6 else -0.4, ox=15.0)

    def ex(f, k, ph):
        note(f, 19, 5 + (k % 2), NOTE[0])
        for i in range(5):
            f[18 + i, 9 - i + (k % 2)] = OUT
    return no_frames(B, pose, ex)


def no_penguin(B):
    """지느러미를 위아래로 파닥파닥 휘저으며 발을 구른다 — 안 돼!"""
    def pose(k, ph):
        t = 0.5 + 0.5 * math.sin(2 * ph)
        return dict(wl=(("fold", "up"), t), wr=(("fold", "up"), 1 - t), mood="angry", beak_open=k % 3 == 0)

    def ex(f, k, ph):
        if k % 3 == 0:
            mark(f, 21, 6)
    return no_frames(B, pose, ex, k_=0.66)


# ── 작은 화살표 짹짹이 + 소품: busy · help · person · pin ────────────────────────
MINI_S, MINI_K = 0.8, 0.85      # 작은 화살표 배율 · 새 배율(머리에 이기 배율에 곱함)
SEEDS = (hx("7e5230ff"), hx("b08a48ff"), hx("e8c27aff"), hx("e8c27a68"))   # 로딩 씨앗 — 막 진해진 것부터
WORM, WORM_D, WORM_B = hx("f6a8b4ff"), hx("d97890ff"), hx("e88aa0ff")       # 지렁이 · 마디 · 띠
SOIL, SOIL_D = hx("9a6a40ff"), hx("6e4a28ff")
SKIN, HAIR, SHIRT, SHIRT_D = hx("f7d7bcff"), hx("5a3a28ff"), hx("4a7fb5ff"), hx("2e5a88ff")
QUILL, QUILL_D, NIB, NIB_L = hx("e6f2faff"), hx("9cc8e0ff"), hx("3a3a44ff"), hx("e8c27aff")
CHEV, CHEV_L = hx("f59a5aff"), hx("f59a5aa0")   # 화살촉 (짙은 것 · 옅은 것)


def mini_arrow() -> set:
    return raster([(1 + x * MINI_S, 1 + y * MINI_S) for x, y in PEEK_CUR])


def mini(B) -> list[dict]:
    """작은 화살표를 머리에 인 짹짹이 12장(테 두르기 전) — 제자리에서 꼬리 살랑 · 날개 꼼지락 · 한 번 끔뻑,
    날지 않는 새는 좌우로 뒤뚱. 장마다 정수리를 화살표 밑동에 붙인다"""
    opt = CARRY_OPT.get(B.id, {})
    C, k0 = chibi(B)
    k_ = k0 * MINI_K
    am = mini_arrow()
    poses = []
    for k, ph in enumerate(phases()):
        s = math.sin(ph)
        t = min(opt.get("wing", 1.0), 0.35 * max(0.0, math.sin(2 * ph)))
        wing = None if opt.get("nowing") else (("fold", "out"), t)
        poses.append((5.0 * s if opt.get("waddle") else 0.0,
                      dict(mood="blink" if k == 7 else "open", wl=wing, wr=wing, tail=0.15 * s,
                           crest=opt.get("crest", 0.5), puff=opt.get("puff", 1.0))))
    lo = min(min(x for x, _ in bird(Rig(7.5, 20.0, a, k_), C, P)[0]) for a, P in poses)
    ox = 7.5 + max(0, 1 - lo)
    out = []
    for a, P in poses:
        _, _, G0 = bird(Rig(0, 0, 0, k_), C, P)
        oy = 17.0 - (G0.hy - G0.hr) * k_
        for _ in range(8):
            g, _, G = bird(Rig(ox, oy, a, k_), C, P)
            if touches(set(g), am):
                break
            oy -= 1
        else:
            print(f"  ! {B.id}/mini: 화살표 밑동을 정수리에 못 붙임")
        if B.eye == "ring":   # 작은 얼굴의 빨간 눈테는 1배에서 핏자국 — 연분홍으로
            g = {p: RING_SOFT if c == B.ring else c for p, c in g.items()}
        if opt.get("blush"):
            blush(g, Rig(ox, oy, a, k_), G)
        out.append(g)
    return out


def companion(B, scene) -> list[dict]:
    """작은 화살표 짹짹이 + scene(k, ph) 이 그리는 소품. 화살표는 맨 위에 — 무엇도 화살표를 덮지 않는다"""
    birds = mini(B)
    am = mini_arrow()
    frames = []
    for k, ph in enumerate(phases()):
        f = scene(k, ph)
        f.update(birds[k])
        solid(f, am, sea.Cur(PEEK_WHITE), sea.Cur(OUT))   # 화살표는 커서
        f[1, 1] = sea.Cur(OUT)
        frames.append(finish({p: c for p, c in f.items() if 1 <= p[0] <= 31 and 1 <= p[1] <= 31}))
    return frames


def busy(B):
    """오른쪽 아래에 씨앗 여덟 알이 원을 그리고, 한 알씩 차례로 진해지며 돈다(로딩 원)"""
    cx, cy, R = 22.5, 22.0, 6.0

    def scene(k, ph):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = math.floor(cx + R * math.cos(a)), math.floor(cy + R * math.sin(a))
            lag = (head - i) % 8
            col = SEEDS[0] if lag < 1 else SEEDS[1] if lag < 2 else SEEDS[2] if lag < 3.5 else SEEDS[3]
            for p in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
                f[p] = col
        return f
    return companion(B, scene), (1, 1)


def along(pts):
    """꺾은선 위 가장 가까운 점까지의 길이(처음부터) — 지렁이 마디 무늬용 (cheesecat.along 과 같음)"""
    segs, acc = [], 0.0
    for p, q in zip(pts, pts[1:]):
        L = math.hypot(q[0] - p[0], q[1] - p[1]) or 1e-9
        segs.append((p, q, L, acc))
        acc += L

    def at(a, b):
        best = None
        for p, q, L, s0 in segs:
            t = max(0.0, min(1.0, ((a - p[0]) * (q[0] - p[0]) + (b - p[1]) * (q[1] - p[1])) / (L * L)))
            d = math.hypot(a - p[0] - (q[0] - p[0]) * t, b - p[1] - (q[1] - p[1]) * t)
            if best is None or d < best[0]:
                best = (d, s0 + L * t)
        return best[1]
    return at


QWORM = [(19.0, 21.0), (19.0, 17.8), (21.2, 15.6), (24.0, 13.4), (24.2, 9.8), (21.4, 7.8), (18.2, 8.8)]


def help_(B):
    """분홍 지렁이가 물음표 꼴로 몸을 말고 꿈틀 — 물결이 몸을 타고 지나간다. 점 자리에 흙 한 알"""
    def scene(k, ph):
        f = {}
        pts, n = [], len(QWORM)
        for i, (x, y) in enumerate(QWORM):
            a, b = QWORM[max(0, i - 1)], QWORM[min(n - 1, i + 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy)
            w = 0.6 * math.sin(2 * ph - i * 1.2) * (0.4 if i == 0 else 1.0)   # 밑동(흙 쪽)은 덜 움직인다
            pts.append((x - dy / L * w, y + dx / L * w))
        at = along(pts)

        def col(a, b):
            s = at(a, b)
            if 4.0 < s < 6.0:
                return WORM_B
            return WORM_D if s % 2.2 < 0.55 and s > 1.0 else WORM
        o, _, _ = draw(Rig(0, 0, 0, 1.0), [("worm", chain(pts, 1.6, 1.3), col, False)])
        f.update(o)
        solid(f, disc(19.4, 26.6, 1.9), SOIL, SOIL_D)
        f[19, 26] = hx("b88a58ff")
        return f
    return companion(B, scene), (1, 1)


def person(B):
    """사람이 손을 흔들고, 그 머리 위에 같은 새가 작게 앉아 날개를 같이 파닥인다"""
    def scene(k, ph):
        f = {}
        rig = Rig(23.0, 26.0, 0.0, 0.7)
        wave = -2.0 * abs(math.sin(ph))
        hand = (9.0, -8.0 + wave)     # 손은 반지름 2.2 — 그보다 작으면 1배에서 테만 남아 머리칼 테와 붙는다
        parts = [("hand", ell(*hand, 2.2, 2.2), SKIN, True), ("sleeve", bar((5.0, -0.5), hand, 1.8), SHIRT, False),
                 ("face", ell(0.0, -7.2, 4.6, 4.2), SKIN, True), ("hair", ell(0.0, -8.6, 5.4, 4.8), HAIR, False),
                 ("torso", ell(0, 3.0, 7.6, 6.4), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
        out, mask, _ = draw(rig, parts)
        for sg in (-1, 1):
            ex, ey = rig.cell(sg * 2.0, -7.4)
            out[ex, ey] = EYE
            out[ex, ey + 1] = EYE
            out[rig.cell(sg * 3.0, -5.4)] = BLUSH
        f.update({p: c for p, c in out.items() if p[1] <= 30})
        top = min(y for x, y in mask if x == 22)
        kb = 0.44
        up = abs(math.sin(ph)) > 0.5
        P = dict(mood="happy", wl=(("fold", "up"), 0.7 if up else 0.0), wr=(("fold", "up"), 0.7 if up else 0.0),
                 crest=0.8, tail=0.1 * math.sin(ph))
        oy = 12.0
        for _ in range(12):     # 발가락이 머리칼 맨 윗줄 바로 위에 오게
            g, _, _ = bird(Rig(22.5, oy, 0.0, kb), B, P)
            low = max(y for _, y in g)
            if low == top - 1:
                break
            oy += (top - 1 - low)
        f.update(g)
        return f
    return companion(B, scene), (1, 1)


def pin(B):
    """빨간 지도 핀 동그라미 속에 그 새 얼굴 — 볏 · 머리깃이 핀 위로 솟는다. 핀이 통통 튀고 땅에 닿으면 눈웃음"""
    def scene(k, ph):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 16.0 + dy
        for x in range(19, 27):
            f.setdefault((x, 30), hx("2a1c2260") if dy else hx("2a1c22a0"))
        pinm = disc(cx, cy, 6.2) | raster([(cx - 4.4, cy + 3.4), (cx + 4.4, cy + 3.4), (cx, cy + 12.4)])
        solid(f, pinm, SIGN, SIGN_D)
        kk = 4.3 / B.hr
        P = dict(body=False, tailon=False, wl=None, wr=None, feet=False, tuft=not B.crest, crest=1.0,
                 mood="happy" if dy == 0 else "open")
        _, _, G0 = bird(Rig(0, 0, 0, kk), B, P)
        hd, _, _ = bird(Rig(cx - G0.hx * kk, cy + 0.4 - G0.hy * kk, 0.0, kk), B, P)
        f.update(hd)
        return f
    return companion(B, scene), (1, 1)


# ── hand: 부리를 위로 콕콕 ───────────────────────────────────────────────────
UPBEAK = {"tiny": [".d.", "ddd"], "small": [".b.", "bbb", "ddd"], "big": ["..b..", ".bbb.", "bbbbb", ".ddd."],
          "flat": [".b.", "bbb", "bbb", "ddd"], "hook": [".b.", "bbb", "bbb", "ccc"]}
PECK = [0.4, 0.8, 1.0, -0.6, 0.0, 0.8, 1.0, -0.6, -0.3, 0.0, 0.0, 0.0]   # 장마다 sq — + 움츠림, - 쭉 펴 콕


def hand(B):
    """고개를 젖혀 부리를 위로 쳐들고 콕콕 — 부리 끝이 맨 위 칸이자 핫스팟이고 장마다 그대로다.
    움츠렸다(sq +) 쭉 펴며(sq -) 쪼는 것은 몸뿐이라 머리 꼭대기 줄을 고정하고 몸 밑단이 오르내린다"""
    k_, TOP, CX = 0.92, 6.0, 16.0
    B2 = NS(**{**vars(B), "beak": "none", "eyey": B.eyey - 0.5, "eyex": B.eyex + 0.06,
               "extra": (lambda f, rig, G, P, small: blush(f, rig, G)) if B.id == "chick" else B.extra})
    rows = UPBEAK[B.beak]
    pal = {"b": B.beak_col[0], "d": B.beak_col[1], "c": getattr(B, "cere", None) or B.beak_col[0]}
    frames, hot = [], None
    for k, sq in enumerate(PECK):
        hit = sq < 0
        w = (("fold", "out"), 0.5) if hit else ("fold", 0)
        P = dict(sq=sq, wl=w, wr=w, crest=0.0, mood="squeeze" if hit else "blink" if k == 10 else "open",
                 tail=-0.15 * sq)
        _, _, G0 = bird(Rig(0, 0, 0, k_), B2, P)
        rig = Rig(CX, TOP - (G0.hy - G0.hr) * k_, 0.0, k_)
        f, mask, G = bird(rig, B2, P)
        x = math.floor(CX + G.hx * k_)
        ytop = min(y for xx, y in mask if xx == x)
        y0 = ytop - len(rows) + 2     # 밑동 두 줄은 얼굴 속(두 눈 사이) — 머리 위에 얹으면 고깔모자로 읽힌다
        for j, r in enumerate(rows):
            for i, ch in enumerate(r):
                if ch != ".":
                    f[x - len(r) // 2 + i, y0 + j] = pal[ch]
        tip = (x, y0)
        hot = hot or tip
        if tip != hot:
            print(f"  ! {B.id}/hand {k}장: 부리 끝이 움직임 {tip} ≠ {hot}")
        if hit:   # 콕 — 부리 끝 양옆으로 튀는 줄
            for p in ((x - 3, y0 + 1), (x - 4, y0), (x + 3, y0 + 1), (x + 4, y0), (x - 3, y0 + 3), (x + 3, y0 + 3)):
                f[p] = OUT
        frames.append(finish(f))
    return frames, hot


# ── cross: 부리가 십자 가운데 ─────────────────────────────────────────────────
def cross(B):
    """앞모습 얼굴, 부리 맨 윗줄 왼쪽 칸이 (15, 15). 양옆 가는 선이 가로 조준선, 머리 위로 솟은 깃 한 가닥과
    턱 밑으로 늘어진 줄이 세로선. 눈을 깜빡이고 볏은 까딱"""
    k_ = 1.0
    P0 = dict(body=False, tailon=False, wl=None, wr=None, feet=False)
    _, _, G0 = bird(Rig(0, 0, 0, k_), B, P0)
    rig = Rig(16.0 - G0.hx * k_, 16.0 - (G0.hy + G0.hr * B.beaky) * k_, 0.0, k_)
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for i in list(range(1, 6)) + list(range(26, 31)):
            f[i, 15] = OUT
            f[15, i] = OUT
        hd, mask, _ = bird(rig, B, {**P0, "mood": "blink" if k == 8 else "open", "crest": 0.6 + 0.3 * math.sin(ph)})
        top = min(y for x, y in mask if x == 15)
        bot = max(y for x, y in mask if x == 15)
        for y in range(6, top):       # 머리 위 깃 한 가닥 — 맨 위 선에 이어진다
            f[15, y] = OUT
        for y in range(bot + 1, 26):  # 턱 밑 줄
            f[15, y] = OUT
        f.update(hd)
        frames.append(finish(f))
    return frames, (15, 15)


# ── ibeam: 세로 나뭇가지에 붙어 갸웃 ──────────────────────────────────────────
TILT = [0, 0, 7, 9, 9, 7, 0, 0, -7, -9, -9, -7]


def branch_i(f):
    """I 꼴 나뭇가지: 세로 줄기 + 위아래 끝의 짧은 가로 갈래, 위 오른끝 · 아래 왼끝에 잎 하나씩"""
    m = {(x, y) for y in range(2, 30) for x in (14, 15, 16)}
    m |= {(x, y) for y in (2, 3, 4, 27, 28, 29) for x in range(11, 21)}
    solid(f, disc(21.6, 2.2, 1.7), LEAF, LEAF_D)
    solid(f, disc(9.4, 29.0, 1.7), LEAF, LEAF_D)
    solid(f, m, WOOD, WOOD_D)
    f[15, 9] = f[15, 20] = WOOD_D     # 옹이


def ibeam(B):
    """세로로 선 나뭇가지(I) 오른쪽에 새가 붙어 발로 줄기를 움켜쥐고 고개를 갸웃갸웃. 핫스팟은 줄기 가운데"""
    k_ = 0.6
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        branch_i(f)
        a = TILT[k]
        P = dict(feet=False, ht=0.06 * a, mood="blink" if k == 6 else "open", tail=0.1 * math.sin(ph))
        rig = Rig(22.6, 15.4, a, k_)
        g, mask, G = bird(rig, B, P)
        f.update(g)
        yb = max(y for x, y in mask if x <= 21)
        for y in (yb - 1, yb - 3):     # 줄기를 움켜쥔 발 — 몸 왼쪽 밑에서 줄기 쪽으로
            x0 = min(x for x, yy in mask if yy == y)
            for x in range(16, x0):
                f[x, y] = B.foot
            f[16, y + 1] = B.foot
        frames.append(finish(f))
    return frames, (15, 15)


# ── move · 기지개 ─────────────────────────────────────────────────────────────
def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col) -> None:
    """(dx, dy) 쪽을 가리키는 화살촉. 꼭짓점이 (cx, cy) — 곧은 쪽은 cheesecat.chevron 과 같음.
    대각은 그 식으로 그리면 칸이 하나 걸러 찍혀 점선이 되므로 두 칸 굵기 ㄱ 자로 그린다"""
    col = sea.Cur(col)   # 화살촉은 커서 — 쓸 때 sea.mark 가 파랑 맨 끝 비트로 캐릭터와 가른다
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


def move(B):
    """앞모습으로 두 날개를 활짝 펴 제자리 파닥파닥 — 네 방향 화살촉이 바깥으로 두근. 몸 가운데가 핫스팟"""
    k_ = 0.66
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy, CHEV if o else CHEV_L)
        t = 0.5 + 0.5 * math.cos(2 * ph)
        P = dict(wl=(("out", "up"), t), wr=(("out", "up"), t), mood="happy" if t > 0.5 else "open",
                 beak_open=k % 6 == 0, sq=-0.3 * t, tail=0.1 * math.sin(ph))
        _, _, G0 = bird(Rig(0, 0, 0, k_), B, P)
        g, _, _ = bird(Rig(15.5, 16.0 - G0.by * k_, 0.0, k_), B, P)
        f.update(g)
        frames.append(finish(f))
    return frames, (15, 15)


AXES = {"ns": 0.0, "we": -90.0, "nwse": -45.0, "nesw": 45.0}


def stretch(B, ang):
    """날개 기지개 — 고개는 똑바로 세운 채 두 날개를 축 양쪽으로 쭉 뻗어 늘였다 줄였다, 늘 때 눈을 질끈.
    ns 는 오른 날개 위 · 왼 날개 아래, we 는 양옆, 대각은 그 대각. 축 양끝 화살촉이 두근. 몸 가운데가 핫스팟"""
    t = math.radians(ang)
    ex, ey = math.sin(t), -math.cos(t)          # 축의 한쪽 끝(위 · 왼쪽)
    dx, dy = round(ex), round(ey)
    R = 13 if dx == 0 or dy == 0 else 11
    head_dir = math.atan2(ey, ex)
    if ex < 0:      # 그 끝 쪽 날개가 그쪽으로
        aims = {-1: head_dir, 1: head_dir + math.pi}
    elif ex > 0:
        aims = {1: head_dir, -1: head_dir + math.pi}
    else:           # 세로 — 오른 날개 위, 왼 날개 아래. 머리 · 발을 비키게 살짝 바깥으로
        aims = {1: -math.pi / 2 + 0.18, -1: math.pi / 2 + 0.18}
    k_ = 0.62
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        s = 0.5 + 0.5 * math.sin(ph)            # 0 줄음 → 1 쭉
        o = 1 if s > 0.6 else 0
        for sg in (-1, 1):
            chevron(f, 15 + sg * dx * (R + o), 15 + sg * dy * (R + o), sg * dx, sg * dy, CHEV if o else CHEV_L)
        lm = 1.15 + 0.5 * s
        P = dict(wl=("aim", aims[-1], lm), wr=("aim", aims[1], lm), mood="squeeze" if s > 0.6 else "open",
                 sq=-0.25 * s, tail=0.08 * math.sin(ph))
        _, _, G0 = bird(Rig(0, 0, 0, k_), B, P)
        g, _, _ = bird(Rig(15.5, 15.8 - G0.by * k_, 0.0, k_), B, P)
        f.update(g)
        frames.append(finish(f))
    return frames, (15, 15)


# ── pen: 깃펜으로 쓰기 ────────────────────────────────────────────────────────
TIP, QBACK = (1.5, 29.5), (25.0, 5.0)   # 펜촉 · 깃 끝(화면)


def pen(B):
    """큰 깃펜을 왼 날개로 끼고 쓰는 새 — 깃펜과 새가 펜촉을 축으로 까딱인다. 펜촉(왼쪽 아래 끝)이 핫스팟"""
    base = Rig(22.6, 20.0, 0.0, 0.6)
    L = math.hypot(QBACK[0] - TIP[0], QBACK[1] - TIP[1])
    ux, uy = (QBACK[0] - TIP[0]) / L, (QBACK[1] - TIP[1]) / L
    lt, lb = base.local(*TIP), base.local(*QBACK)
    vc = base.local(TIP[0] + ux * L * 0.72, TIP[1] + uy * L * 0.72)   # 깃 가운데
    rot = math.atan2(lb[1] - lt[1], lb[0] - lt[0])
    grip = base.local(TIP[0] + ux * L * 0.4, TIP[1] + uy * L * 0.4)

    def qcol(a, b):
        x, y = base.world(a, b)
        tt = (x - TIP[0]) * ux + (y - TIP[1]) * uy
        sd = -(x - TIP[0]) * uy + (y - TIP[1]) * ux
        if tt < 1.8:
            return NIB
        if tt < 3.0:
            return NIB_L
        if abs(sd) < 0.5:
            return WHITE
        return QUILL_D if (tt + abs(sd) * 1.2) % 2.6 < 0.8 else QUILL
    quill = ("quill", any_of(bar(lt, lb, 0.5 / base.k), ell(vc[0], vc[1], L * 0.3 / base.k, 2.3 / base.k, rot)),
             qcol, True)
    frames = []
    for k, ph in enumerate(phases()):
        d = math.radians(3.0 * math.sin(2 * ph))
        ox, oy = base.ox - TIP[0], base.oy - TIP[1]
        rig = Rig(TIP[0] + ox * math.cos(d) - oy * math.sin(d), TIP[1] + ox * math.sin(d) + oy * math.cos(d),
                  math.degrees(d), base.k)
        P = dict(props=(quill,), wr=("fold", 0), mood="blink" if k == 4 else "open", tail=0.1 * math.sin(ph))
        _, _, G0 = bird(Rig(0, 0, 0, base.k), B, P)
        rx, ry = -G0.ra * 0.55, G0.by - G0.rb * 0.3
        reach = math.hypot(grip[0] - rx, grip[1] - ry)
        P["wl"] = ("aim", math.atan2(grip[1] - ry, grip[0] - rx), reach / 1.75 / B.wl, 0.95, True)
        f, _, _ = bird(rig, B, P)
        f[math.floor(TIP[0]), math.floor(TIP[1])] = NIB
        frames.append(finish(f))
    return frames, (math.floor(TIP[0]), math.floor(TIP[1]))


# ── up: 만세 ──────────────────────────────────────────────────────────────────
def up(B):
    """두 날개를 위로 번쩍 만세 — 머리는 그 자리에 두고 몸만 통통 들썩인다. 핫스팟은 머리 윤곽 꼭대기 가운데
    (볏 · 솜털은 그 위로 솟아도 핫스팟이 아니다), 장마다 같은 칸"""
    k_, TOP, CX = 0.7, 7.0, 16.0
    frames, hot = [], None
    for k, ph in enumerate(phases()):
        bob = abs(math.sin(ph))
        t = 0.8 + 0.2 * abs(math.sin(2 * ph))
        # 접은 날개 자세의 "up" 은 1배에서 귀 같은 꼭지라 날개를 위로 겨눠 쭉 뻗는다. 머리 뒤로 숨지 않게
        # 수직에서 45–55° 벌린 V 자
        sp = 0.95 - 0.15 * t
        P = dict(sq=0.9 * bob - 0.2, wl=("aim", -math.pi / 2 - sp, 1.55 * t), wr=("aim", -math.pi / 2 + sp, 1.55 * t),
                 crest=0.9,
                 mood="happy" if k % 4 < 2 else "open", beak_open=k % 4 < 2, tail=0.1 * math.sin(ph))
        _, _, G0 = bird(Rig(0, 0, 0, k_), B, P)
        rig = Rig(CX, TOP - (G0.hy - G0.hr) * k_, 0.0, k_)
        f, mask, G = bird(rig, B, P)
        x = math.floor(CX + G.hx * k_)
        y = min(yy for xx, yy in mask if xx == x and in_head(*rig.local(x + 0.5, yy + 0.5), G))
        hot = hot or (x, y)
        if (x, y) != hot:
            print(f"  ! {B.id}/up {k}장: 머리 꼭대기가 움직임 {(x, y)} ≠ {hot}")
        for xx in range(9, 24):   # 바닥 그림자
            f.setdefault((xx, 29), hx("2a1c2250"))
        frames.append(finish(f))
    return frames, hot


SCENES = {"busy": busy, "help": help_, "person": person, "pin": pin, "hand": hand, "cross": cross, "ibeam": ibeam,
          "move": move, "ns": lambda B: stretch(B, AXES["ns"]), "we": lambda B: stretch(B, AXES["we"]),
          "nwse": lambda B: stretch(B, AXES["nwse"]), "nesw": lambda B: stretch(B, AXES["nesw"]), "pen": pen, "up": up}


# ── 핫스팟 · 검사 · 쓰기 ──────────────────────────────────────────────────────
def center_hot(frames):
    """모든 장에서 불투명한 칸 중 판 가운데에 가장 가까운 것"""
    common = set.intersection(*[{p for p, c in f.items() if c[3] == 255} for f in frames])
    return min(common, key=lambda p: (math.hypot(p[0] - 15.5, p[1] - 15.5), p))


def check(rid, frames, hot):
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


def write_carry(d) -> None:
    """머리에 이기 화살표를 매끈한 모양으로 다시 그릴 재료 셋 (smooth.peek_drawer 의 anchor "base") — 냥이 빼꼼의
    sea.write_peek 와 같은 이름을 쓴다. base 는 꼬리 밑변 가운데 세로줄에서 화살표 맨 아래 칸 바로 밑(32칸 판 좌표)"""
    import json
    a: dict = {}
    am = arrow_mask(0)
    solid(a, am, sea.Cur(PEEK_WHITE), sea.Cur(OUT))
    (d / "_arrow.txt").write_text(shape.to_text(sea.mark([a]), (1, 1), sea.RATE), encoding="utf-8")
    (d / "_peek.txt").write_text(shape.to_text(sea.mark(CARRY), (1, 1), sea.RATE), encoding="utf-8")
    cx = 1 + (PEEK_CUR[3][0] + PEEK_CUR[4][0]) / 2 * CARRY_S
    by = max(y for x, y in am if abs(x + 0.5 - cx) <= 1) + 1
    meta = dict(anchor="base", base=[cx, by], height=max(y for _, y in PEEK_CUR) * CARRY_S,
                rot=[round(a, 2) + 0.0 for a in CARRY_ROT])
    (d / "_peek.json").write_text(json.dumps(meta, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    args = sys.argv[1:]
    only = None
    if "--cells" in args:     # 몇 칸만 다시 그리기 — --cells hand,up
        i = args.index("--cells")
        only = set(args[i + 1].split(","))
        del args[i:i + 2]
    ids = args or ORDER
    bad = 0
    for sid in ids:
        B = SPECS[sid]
        d = sea.WIN / "art" / f"{sid}anim"
        d.mkdir(parents=True, exist_ok=True)
        cells = {"arrow": (lambda: arrow(B), lambda fr: (1, 1)),
                 "wait": (lambda: globals()[f"wait_{sid}"](B), center_hot),
                 "no": (lambda: globals()[f"no_{sid}"](B), lambda fr: (15, 15))}
        for cell, scene in SCENES.items():
            made = {}

            def make(scene=scene, made=made):
                made["fr"], made["hot"] = scene(B)
                return made["fr"]
            cells[cell] = (make, lambda fr, made=made: made["hot"])
        for cell, (make, hot_of) in cells.items():
            if only and cell not in only:
                continue
            frames = [{p: c for p, c in fr.items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31} for fr in make()]
            hot = hot_of(frames)
            bad += check(f"{sid}/{cell}", frames, hot)
            # 칸마다(커서 없는 칸도) mark — 안 거친 칸의 홀수 파랑은 커서로 읽힌다
            (d / f"{cell}.txt").write_text(shape.to_text(sea.mark(frames), hot, sea.RATE), encoding="utf-8")
            if cell == "arrow":
                write_carry(d)
        print(f"{sid}: 끝")
    print(f"경고 {bad}개")


if __name__ == "__main__":
    main()

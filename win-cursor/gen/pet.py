# SPDX-License-Identifier: Apache-2.0
"""햄찌와 친구들 · 애니 — 작은 반려동물 열 마리의 17칸을 그린다.

  python gen/pet.py [마리...] [--cells 칸,칸]   art/<마리>anim/<칸>.txt 를 쓴다 (마리를 안 주면 열 마리 전부).
  푸딩햄스터만 말랑 간식의 푸딩과 이름이 겹쳐 puddinghamsteranim 이다(`sid`)

냥이 · 애니(gen/cheesecat.py)와 같은 틀이다 — 부위(타원 · 막대 · 세모)를 동물 제 좌표 (u 오른쪽, w 아래)에 놓고
화면으로 돌려 찍는다(`Rig`, `draw`). cheesecat 의 draw 는 그 파일의 OUT 을 써서 불러오지 않고 여기 옮겨 뒀다.
마리마다 털빛 · 무늬(PETS)만 다른 것이 아니라 wait · no 장면을 따로 짠다 — 한 틀에 색만 바꾸면 복제품으로 보인다.
  arrow  0.85배 흰 화살표 대 끝을 두 앞발로 쥐고 대롱대롱 — 마리마다 제 맛(손 흔들기 · 턱걸이 · 긴 몸 · 비막 …)
  wait   마리마다 제 버릇 12장
  no     빨간 금지 표지 안에서 마리마다 제 방식으로 싫다고 한다
"""
import math
import sys
from pathlib import Path

import sea  # noqa: E402,F401  (shape 경로를 sea 가 잡는다)
import shape as SH  # noqa: E402
from sea import N, PEEK_CUR, PEEK_WHITE, RATE, SIGN, SIGN_D, disc, finish, hx, ink, inside, phases, raster, solid  # noqa: E402

ART = Path(__file__).resolve().parent.parent / "art"

OUT, EYE, HI = hx("3a2a30ff"), hx("2a1c22ff"), hx("ffffffff")   # 테두리 · 눈 · 반짝 (냥이와 같은 색)
PINK, NOSE = hx("f4a0b0ff"), hx("e27d90ff")                      # 볼터치 · 귀 속 / 코
CREAMRIM, GREYRIM = hx("f6e9d2c7"), hx("d9dde3c7")               # 반투명 테 — 따뜻한 털 / 회색 · 흰 털
SEED, SEED_L = hx("3b3540ff"), hx("e8e2d6ff")                    # 해바라기씨 (까만 바탕 · 흰 줄)
WHEEL, WHEEL_D, WHEEL_L = hx("7fa3d4ff"), hx("587ab0ff"), hx("a9c4e8ff")   # 쳇바퀴 (털과 갈리게 파랑)
DUST, DUST_D = hx("ead6a8ff"), hx("c9a86aff")                    # 톱밥
SAND, SAND_D = hx("e6dcc2ff"), hx("c8b68cff")                    # 모래
TUBE, TUBE_D, TUBE_L = hx("7cc08aff"), hx("4f9a62ff"), hx("a8dcb2ff")   # 터널
BARK, BARK_D, WOOD = hx("a87a4cff"), hx("7a5532ff"), hx("e9cfa0ff")     # 나뭇가지
ANGER = hx("e0505aff")
FAINT = (hx("ffffffb0"), hx("3a2a3070"))                          # 바람 줄 · 움직임 줄


def P_(**kw):
    d = dict(head="ham", ear="round", cheek=1.0, stripe=None, low=False, cap=None, tri=False, mask=False,
             bigeye=False, teeth=False, tail=None, blush=True, paw=hx("f4b4b0ff"), ear_in=PINK, scale=1.0)
    d.update(kw)
    for key in ("fur", "dark", "belly", "paw", "ear_in"):
        if isinstance(d[key], str):
            d[key] = hx(d[key])
    return d


PETS = {
    "golden": P_(name="골든햄스터", fur="e8963cff", dark="c06a28ff", belly="fff6e8ff", low=True, rim=CREAMRIM),
    "pearl": P_(name="펄햄스터", fur="fbf8f4ff", dark="b4b8c4ff", belly="ffffffff", cap=True, rim=GREYRIM),
    "pudding": P_(name="푸딩햄스터", fur="f2c860ff", dark="d4a03cff", belly="fff0c8ff", cheek=1.18, scale=1.08,
                  rim=CREAMRIM),
    "sapphire": P_(name="블루사파이어", fur="8f9cb4ff", dark="56617cff", belly="f4f6faff", low=True, stripe=True,
                   rim=GREYRIM),
    "jungle": P_(name="정글리안", fur="9c8f84ff", dark="2e2a2cff", belly="f7f3eeff", low=True, stripe=True,
                 scale=0.86, rim=GREYRIM),
    "guinea": P_(name="기니피그", fur="dc8a3aff", dark="2e2a2cff", belly="fffaf2ff", head="guinea", ear="petal",
                 tri=True, blush=False, rim=CREAMRIM, paw="e8b8a8ff"),
    "chinchilla": P_(name="친칠라", fur="b6bcc8ff", dark="858c9aff", belly="f2f2f6ff", ear="big", ear_in="f2c4ccff",
                     tail="bushy", rim=GREYRIM, paw="d8dce4ff"),
    "ferret": P_(name="페럿", fur="8a6446ff", dark="4a3222ff", belly="fff6e8ff", head="ferret", ear="small",
                 mask=True, tail="ferret", rim=CREAMRIM, paw="4a3222ff", blush=False),
    "glider": P_(name="슈가글라이더", fur="a4a4aeff", dark="34303aff", belly="f6f2eaff", ear="tall", stripe=True,
                 bigeye=True, tail="glider", rim=GREYRIM, paw="f0c8c8ff"),
    "degu": P_(name="데구", fur="a37a4eff", dark="5e4028ff", belly="efdcb8ff", head="degu", ear="degu",
               ear_in="c99a7aff", teeth=True, tail="tuft", rim=CREAMRIM, paw="d8b49aff", blush=False),
}


# ── 그리개 (cheesecat.py 에서 옮김) ───────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도) · 배율 k. ang=0 이면 u 가 오른쪽, w 가 아래. ang 만큼 시계 방향으로 돈다"""

    def __init__(self, ox, oy, ang=0.0, k=1.0):
        t = math.radians(ang)
        self.ox, self.oy, self.c, self.s, self.k = ox, oy, math.cos(t), math.sin(t), k

    def world(self, a, b):
        return self.ox + (a * self.c - b * self.s) * self.k, self.oy + (a * self.s + b * self.c) * self.k

    def local(self, x, y):
        dx, dy = (x - self.ox) / self.k, (y - self.oy) / self.k
        return dx * self.c + dy * self.s, -dx * self.s + dy * self.c

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


def along(pts):
    """꺾은선 위 가장 가까운 점까지의 길이(처음부터) · 전체 길이"""
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
    return at, acc


def tri(*pts):
    pl = list(pts)
    return lambda a, b: inside(pl, a, b)


def any_of(*hs):
    return lambda a, b: any(h(a, b) for h in hs)


def draw(rig, parts):
    """parts: [(이름, 맞음(a, b), 색(a, b) 또는 색, 테두리)] — 앞의 것이 위. → ({칸: 색}, 칸 집합, {칸: 부위})"""
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


def dot(f, x, y, c):
    f[x, y] = c


# ── 몸 부위 (앞모습) ─────────────────────────────────────────────────────────
HC, HR = (0.0, -7.5), 7.0       # 머리 가운데 · 반지름 — peek_tail 의 엉덩이 자리와 맞춘 냥이 좌표 그대로
HAM_HC = (0.0, -5.4)            # 햄스터는 머리를 내려 몸과 한 덩이(동그란 떡) — 냥이 자리면 긴 기둥이 된다


def home(P):
    return HAM_HC if P["head"] == "ham" else HC


def head_parts(P, hc=None, r=HR, turn=0.0, cheek=None, back=False, name="head"):
    """앞모습 머리(back 이면 뒤통수). 햄스터는 목 없이 볼주머니가 아래로 불룩, 기니피그는 넓적, 페럿 · 데구는 주둥이가 길다"""
    u0, w0 = hc or home(P)
    cheek = P["cheek"] if cheek is None else cheek
    t = turn
    kind = P["head"]
    if kind == "ferret":
        head = any_of(ell(u0, w0 - 0.15 * r, 0.84 * r, 0.78 * r), ell(u0 + t * 0.5, w0 + 0.42 * r, 0.5 * r, 0.44 * r))
    elif kind == "guinea":
        head = any_of(ell(u0, w0, 1.04 * r, 0.82 * r), ell(u0 + t * 0.5, w0 + 0.36 * r, 0.62 * r, 0.46 * r))
    elif kind == "degu":
        head = any_of(ell(u0, w0 - 0.1 * r, 0.9 * r, 0.84 * r), ell(u0 + t * 0.5, w0 + 0.42 * r, 0.46 * r, 0.4 * r))
    else:
        cr = 0.4 * r * cheek ** 1.6       # 볼주머니 — 부풀면 머리 밖으로 불룩
        head = any_of(ell(u0, w0 - 0.1 * r, 0.9 * r, 0.86 * r),
                      ell(u0 - 0.5 * r - (cheek - 1) * r * 0.6 + t * 0.2, w0 + 0.32 * r, cr, cr * 0.9),
                      ell(u0 + 0.5 * r + (cheek - 1) * r * 0.6 + t * 0.2, w0 + 0.32 * r, cr, cr * 0.9))
    ear = P["ear"]
    ears, inner = [], []
    for sg in (-1, 1):
        if ear == "big":
            c, ra, rb, ri = (u0 + sg * 0.74 * r + t * 0.2, w0 - 0.98 * r), 0.5 * r, 0.56 * r, 0.62
            rot = sg * 0.35
        elif ear == "tall":
            c, ra, rb, ri, rot = (u0 + sg * 0.6 * r + t * 0.2, w0 - 0.92 * r), 0.24 * r, 0.42 * r, 0.5, sg * 0.4
        elif ear == "petal":
            c, ra, rb, ri, rot = (u0 + sg * 0.96 * r, w0 - 0.42 * r), 0.24 * r, 0.32 * r, 0.0, sg * -0.5
        elif ear == "small":
            c, ra, rb, ri, rot = (u0 + sg * 0.74 * r + t * 0.2, w0 - 0.6 * r), 0.26 * r, 0.24 * r, 0.5, 0.0
        elif ear == "degu":
            c, ra, rb, ri, rot = (u0 + sg * 0.64 * r + t * 0.2, w0 - 0.78 * r), 0.3 * r, 0.32 * r, 0.55, 0.0
        else:
            c, ra, rb, ri, rot = (u0 + sg * 0.66 * r + t * 0.2, w0 - 0.74 * r), 0.3 * r, 0.3 * r, 0.55, 0.0
        ears.append(ell(c[0], c[1], ra, rb, rot))
        if ri:
            inner.append(ell(c[0], c[1] + rb * 0.12, ra * ri, rb * ri, rot))
    inner_hit = any_of(*inner) if inner else (lambda a, b: False)

    def skin(a, b):
        mu = a - u0 - t
        if back:
            if P["stripe"] and abs(a - u0) < 0.13 * r:
                return P["dark"]
            if P["cap"] and b < w0 + 0.2 * r:
                return P["dark"]
            if P["tri"]:
                return P["fur"] if a < u0 else P["dark"]
            return P["fur"]
        if P["mask"]:
            if abs(b - (w0 - 0.06 * r)) < 0.2 * r and 0.12 * r < abs(mu) < 0.78 * r:
                return P["dark"]
            if b > w0 - 0.3 * r or abs(mu) < 0.14 * r:
                return P["belly"]
            return P["fur"]
        if (mu / (0.42 * r)) ** 2 + ((b - (w0 + 0.36 * r)) / (0.3 * r)) ** 2 <= 1:
            return P["belly"]
        if P["tri"]:
            if abs(mu) < 0.16 * r:
                return P["belly"]
            return P["fur"] if mu < 0 else P["dark"]
        if P["stripe"] and abs(mu) < 0.11 * r and b < w0 - 0.36 * r:
            return P["dark"]
        if P["cap"] and b < w0 - 0.3 * r - 0.25 * abs(mu):
            return P["dark"]
        if P["low"] and b > w0 + 0.12 * r and abs(mu) < 0.8 * r:
            return P["belly"]
        return P["fur"]

    def ear_col(a, b):
        if inner_hit(a, b) and not back:
            return P["ear_in"]
        if P["tri"]:
            return P["fur"] if a < u0 else P["dark"]
        if P["mask"]:
            return P["belly"]
        return P["dark"] if P["cap"] else P["fur"]
    # 햄스터는 목 없이 머리와 몸이 한 덩이 — 머리 밑 선을 그으면 공 두 개(눈사람)로 읽힌다
    return [(name, head, skin, kind != "ham"), (name + "_ear", any_of(*ears), ear_col, False)]


def body_part(P, c=(0.0, 3.0), ra=6.8, rb=6.0, back=False, name="body"):
    c0, c1 = c

    def col(a, b):
        if back:
            if P["stripe"] and abs(a - c0) < 0.9:
                return P["dark"]
            if P["cap"] and b < c1 + 1.0:
                return P["dark"]
            if P["tri"]:
                return P["dark"] if a > c0 + 1 else P["belly"] if a > c0 - 2 else P["fur"]
            return P["fur"]
        if ((a - c0) / (ra * 0.58)) ** 2 + ((b - c1 - rb * 0.08) / (rb * 0.8)) ** 2 <= 1:
            return P["belly"]
        if P["tri"]:
            return P["fur"] if a < c0 else P["dark"]
        if P["cap"]:
            return P["fur"]
        return P["fur"]
    return (name, ell(c0, c1, ra, rb), col, False)


def paws(P, pts, r=1.5, name="paw"):
    return [(f"{name}{i}", ell(a, b, r, r * 0.9), P["paw"], True) for i, (a, b) in enumerate(pts)]


def feet(P, y=8.8, dx=4.0, name="feet"):
    return (name, any_of(ell(-dx, y, 2.0, 1.2), ell(dx, y, 2.0, 1.2)), P["paw"], True)


def tail_part(P, pts, kind=None, name="tail", lined=False, scale=1.0):
    """꼬리 — bushy(친칠라 북슬) · ferret(굵고 짙음) · glider(북슬, 끝 까망) · tuft(데구 가는 꼬리에 끝 술)"""
    kind = kind or P["tail"]
    at, total = along(pts)
    if kind == "bushy":
        r0, r1 = 1.6 * scale, 2.2 * scale

        def col(a, b):
            return P["dark"] if at(a, b) > total * 0.55 and (a + b) % 2.2 < 0.9 else P["fur"]
    elif kind == "ferret":
        r0, r1 = 1.6 * scale, 1.1 * scale

        def col(a, b):
            return P["dark"]
    elif kind == "glider":
        r0, r1 = 1.2 * scale, 1.7 * scale

        def col(a, b):
            return P["dark"] if at(a, b) > total * 0.66 else P["fur"]
    else:   # tuft
        r0, r1 = 0.75 * scale, 0.75 * scale
        end = pts[-1]
        tuft = ell(end[0], end[1], 1.7 * scale, 1.7 * scale)
        return (name, any_of(chain(pts, r0, r1), tuft),
                lambda a, b: P["dark"] if at(a, b) > total - 2.2 * scale else P["fur"], lined)
    return (name, chain(pts, r0, r1), col, lined)


def face(f, rig, P, hc=None, r=HR, mood="open", turn=0.0, mouth="y", blush=None):
    """눈 · 코 · 입 · 볼터치. 작게(k·r < 4.6) 그리면 눈 1×2. bigeye(슈가글라이더)는 3×3 눈.
    mood: open · blink · sleep · happy · squeeze · sulk · x(죽은 척 ×). mouth: y(ㅅ) · o(벌림) · teeth · none"""
    u0, w0 = hc or home(P)
    small = rig.k * r < 4.6
    big = P["bigeye"] and not small
    for sg in (-1, 1):
        ex, ey = rig.world(u0 + turn + sg * r * (0.44 if big else 0.4), w0 - r * 0.06)
        if small:
            x0, y0 = math.floor(ex), math.floor(ey - 0.5)
            if mood == "open":
                dot(f, x0, y0, EYE)
                dot(f, x0, y0 + 1, EYE)
            else:
                dot(f, x0, y0 + 1, EYE)
            continue
        x0, y0 = round(ex - 1), round(ey - 1)
        if mood == "open":
            n = 3 if big else 2
            x0 -= 1 if big and sg < 0 else 0
            for dx in range(n):
                for dy in range(n):
                    dot(f, x0 + dx, y0 + dy - (1 if big else 0), EYE)
            dot(f, x0 + (0 if sg < 0 else n - 2), y0 - (1 if big else 0), HI)
        elif mood == "blink":
            dot(f, x0, y0 + 1, EYE)
            dot(f, x0 + 1, y0 + 1, EYE)
        elif mood == "sleep":
            dot(f, x0, y0 + 1, EYE)
            dot(f, x0 + 1, y0 + 1, EYE)
            dot(f, x0 - 1 if sg < 0 else x0 + 2, y0, EYE)
        elif mood == "happy":
            dot(f, x0 - 1 if sg < 0 else x0, y0 + 1, EYE)
            dot(f, x0 if sg < 0 else x0 + 1, y0, EYE)
            dot(f, x0 + 1 if sg < 0 else x0 + 2, y0 + 1, EYE)
        elif mood == "squeeze":
            xa, xb = (x0, x0 + 1) if sg < 0 else (x0 + 1, x0)
            dot(f, xa, y0 - 1, EYE)
            dot(f, xb, y0, EYE)
            dot(f, xa, y0 + 1, EYE)
        elif mood == "sulk":
            dot(f, x0, y0 + (1 if sg > 0 else 0), EYE)
            dot(f, x0 + 1, y0 + (0 if sg > 0 else 1), EYE)
        elif mood == "x":
            for p in ((x0 - 1, y0 - 1), (x0 + 1, y0 - 1), (x0, y0), (x0 - 1, y0 + 1), (x0 + 1, y0 + 1)):
                dot(f, *p, EYE)
    nx, ny = rig.world(u0 + turn, w0 + r * 0.2)
    nx, ny = math.floor(nx), math.floor(ny)
    dot(f, nx, ny, NOSE)
    if not small:
        if P["head"] == "guinea":
            dot(f, nx + 1, ny, NOSE)
        if mouth == "y":
            dot(f, nx, ny + 1, OUT)
            dot(f, nx - 1, ny + 2, OUT)
            dot(f, nx + 1, ny + 2, OUT)
        elif mouth == "o":
            for p in ((nx, ny + 1), (nx - 1, ny + 2), (nx, ny + 2), (nx + 1, ny + 2), (nx, ny + 3)):
                dot(f, *p, OUT)
            dot(f, nx, ny + 2, NOSE)
        elif mouth == "teeth" or (mouth == "y" and P["teeth"]):
            dot(f, nx - 1, ny + 1, OUT)
            dot(f, nx + 1, ny + 1, OUT)
            dot(f, nx, ny + 1, hx("fff4d8ff"))
            dot(f, nx, ny + 2, hx("fff4d8ff"))
        if P["teeth"] and mouth == "y":
            pass
    if blush if blush is not None else P["blush"]:
        for sg in (-1, 1):
            bx, by = rig.world(u0 + turn + sg * r * 0.66, w0 + r * 0.26)
            dot(f, math.floor(bx), math.floor(by), PINK)


def whiskers(f, rig, hc=HC, r=HR, turn=0.0, n=2, skip=(), w=1.0):
    u0, w0 = hc
    for sg in (-1, 1):
        if sg in skip:
            continue
        for j, dw in enumerate((0.1, 0.32)):
            x0, y0 = rig.world(u0 + turn + sg * r * w, w0 + r * dw)
            for i in range(n + 1):
                x = math.floor(x0 + sg * i)
                y = math.floor(y0 + (i * 0.4 * (j * 2 - 1) if j else 0))
                if (x, y) not in f:
                    f[x, y] = OUT


def sit_parts(P, hc=None, r=HR, turn=0.0, cheek=None, hand=None, extra=(), tail=None, back=False, body=None):
    """앉은 앞모습: 앞발(가슴 앞) · 머리 · 뒷발 · 몸 · 꼬리. extra 는 맨 앞"""
    hc = hc or home(P)
    hand = [(-2.4, 1.2), (2.4, 1.2)] if hand is None else hand
    parts = list(extra)
    if not back:
        parts += paws(P, hand)
    ham = P["head"] == "ham"
    parts += head_parts(P, hc, r, turn, cheek, back) + \
        [feet(P, 8.6 if ham else 8.8), body or (body_part(P, (0.0, 1.8), 8.6, 7.2, back=back) if ham else body_part(P, back=back))]
    if tail:
        parts.append(tail_part(P, tail))
    return parts


# ── 옆모습 ───────────────────────────────────────────────────────────────────
def side_parts(P, s=1, step=0.0, L=None, name="s", tail=None, ear_flat=0.0):
    """옆모습 — 몸 가운데 (0, 0), s=1 이면 오른쪽을 본다. 햄스터는 달걀 하나, 기니피그는 긴 감자(L 1.3).
    돌려주는 것: (부위들, 눈 자리, 코 자리, 볼 자리)"""
    L = L or (1.3 if P["tri"] else 1.0)
    hxc = s * 5.4 * L
    body = any_of(ell(0, 0.6, 7.4 * L, 5.2), ell(hxc, -0.4, 4.8, 4.5))
    snout_c = (hxc + s * 3.6, 0.8)
    snout = ell(snout_c[0], snout_c[1], 2.2, 1.9)

    def skin(a, b):
        sa = a * s
        if P["tri"]:
            if sa > 5.4 * L + 2.0:
                return P["belly"]
            if sa > 2.6 * L:
                return P["fur"]
            if sa > -2.4 * L:
                return P["belly"]
            return P["dark"]
        if P["mask"]:
            return P["belly"] if sa > 5.4 * L + 1 else P["fur"]
        if b > 2.2 and abs(a) < 7 * L or sa > 5.4 * L + 2.4 and b > 0.2:
            return P["belly"]
        if P["low"] and b > 0.9:
            return P["belly"]
        if P["stripe"] and -4.6 < b < -3.2 and -5.0 < sa < 5.0:
            return P["dark"]
        if P["cap"] and b < -1.6:
            return P["dark"]
        return P["fur"]
    ear = P["ear"]
    ec = (s * 4.2 * L, -4.6 + ear_flat)
    if ear == "big":
        e_hit, e_in = ell(ec[0] - s * 0.6, ec[1] - 2.0, 2.6, 3.6, s * 0.3), ell(ec[0] - s * 0.6, ec[1] - 1.6, 1.5, 2.4, s * 0.3)
    elif ear == "tall":
        e_hit, e_in = ell(ec[0], ec[1] - 1.2, 1.4, 2.6, s * 0.3), ell(ec[0], ec[1] - 1.0, 0.7, 1.6, s * 0.3)
    elif ear == "petal":
        e_hit, e_in = ell(s * 3.4 * L, -3.2, 1.8, 1.4, s * -0.4), (lambda a, b: False)
    elif ear == "small":
        e_hit, e_in = ell(ec[0], ec[1] + 0.8, 1.4, 1.3), ell(ec[0], ec[1] + 1.0, 0.7, 0.6)
    else:
        e_hit, e_in = ell(ec[0], ec[1], 1.8, 1.9), ell(ec[0], ec[1] + 0.2, 1.0, 1.1)

    def ear_col(a, b):
        if e_in(a, b):
            return P["ear_in"]
        return P["dark"] if (P["tri"] or P["cap"]) else P["fur"]
    ft = (f"{name}_feet", any_of(ell(s * (3.8 * L + step), 5.4, 1.8, 1.1), ell(-s * (4.0 * L + step), 5.4, 2.0, 1.1)),
          P["paw"], True)
    parts = [(name, any_of(body, snout), skin, True), (name + "_ear", e_hit, ear_col, False), ft]
    if tail:
        parts.append(tail_part(P, tail, name=name + "_tail"))
    eye = (hxc + s * 1.0, -1.4)
    nose = (snout_c[0] + s * 1.9, snout_c[1] - 0.3)
    cheek = (hxc + s * 0.8, 1.6)
    return parts, eye, nose, cheek


def side_face(f, rig, P, eye, nose, cheek, s=1, mood="open", whisk=True, mouth=True):
    small = rig.k < 0.55
    ex, ey = rig.cell(*eye)
    if mood == "open":
        if small:
            dot(f, ex, ey, EYE)
            dot(f, ex, ey + 1, EYE)
        else:
            for dx in (0, 1):
                for dy in (0, 1):
                    dot(f, ex + dx, ey + dy, EYE)
            dot(f, ex + (1 if s > 0 else 0), ey, HI)
            if P["bigeye"]:
                dot(f, ex + (-1 if s > 0 else 2), ey, EYE)
                dot(f, ex + (-1 if s > 0 else 2), ey + 1, EYE)
    elif mood == "squeeze":
        for p in ((ex, ey), (ex + s, ey + 1), (ex, ey + 2)) if s > 0 else ((ex + 1, ey), (ex, ey + 1), (ex + 1, ey + 2)):
            dot(f, *p, EYE)
    else:
        dot(f, ex, ey + 1, EYE)
        dot(f, ex + 1, ey + 1, EYE)
    if P["mask"]:
        for dx in (-2, -1, 2, 3) if s > 0 else (-2, -1, 2, 3):
            q = (ex + dx, ey + (0 if abs(dx) < 3 else 1))
            if f.get(q) not in (OUT, EYE, HI, None):
                f[q] = P["dark"]
    nx, ny = rig.cell(*nose)
    dot(f, nx, ny, NOSE)
    if mouth:
        dot(f, nx - s, ny + 1, OUT)
        if P["teeth"]:
            dot(f, nx - s, ny + 2, hx("fff4d8ff"))
    if P["blush"]:
        dot(f, *rig.cell(*cheek), PINK)
    if whisk:
        for j in (0, 1):
            for i in range(1, 3):
                q = (nx + s * i, ny + j * (i - 1) * (1 if j else 0) + j)
                if q not in f:
                    f[q] = OUT


def merge(*ds):
    f = {}
    for d in ds:
        f.update(d)
    return f


def clip(f):
    return {p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}


# ── arrow: 대롱대롱 ──────────────────────────────────────────────────────────
# 2026-10-09 사용자가 화살표와 노는 자세 시안(pose_pet.py F–J) 중 H 대롱대롱으로 정해 빼꼼을 갈아 끼웠다.
# 화살표 대 끝을 두 앞발로 쥐고 매달려 쥔 자리를 축으로 흔들린다. 동물은 화살표 칸을 한 칸도 안 덮는다 —
# 겹친 칸은 버리고 맞닿은 칸은 동물 테(apart)라 화살표 테 + 동물 테 두 줄로 갈리고, 끝 (1, 1) 은 늘 또렷하다.
A_S = 0.85        # 화살표 배율 — 대 끝 밑 자리(판 16–30줄)를 넓히려 조금 줄였다
A_K = 0.82        # 매달린 몸 배율(× 마리 scale) — 2026-10-09 0.72 에서 키웠다(사용자가 고른 B′). 판 왼쪽 · 아래에 닿아
                  # 더 키우면 A_BODY 를 같이 늘려야 한다(0.82 에서 3.6 아래면 골든햄스터가, 4 넘으면 족제비가 판 밖으로)
A_PTS = [(1 + x * A_S, 1 + y * A_S) for x, y in PEEK_CUR]
A_GRIP = ((A_PTS[3][0] + A_PTS[4][0]) / 2 + 0.3, (A_PTS[3][1] + A_PTS[4][1]) / 2 + 0.75)   # 대 끝 아랫단 가운데 바로 밑
A_HANDS = ((-4.2, -0.8), (3.6, -2.2))   # 두 앞발(제 좌표) — 대 끝을 양옆에서 꼭 쥔다(아랫단이 오른쪽으로 올라가 오른발이 높다)
A_SWEAT = hx("8fd0f0ff")


def apart(f, g, m):
    """동물(g)을 화살표(m) 밖에만 찍고, 화살표에 맞닿은 칸은 검은 테로"""
    for p, c in g.items():
        if p in m:
            continue
        x, y = p
        f[p] = OUT if any(q in m for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))) else c


A_HC = (0.0, 9.8)       # 쥔 자리에서 머리 가운데까지(제 좌표) — 정수리가 대 끝 바로 밑
A_BODY = (3.6, -3.6)    # 앞발은 대 끝에 둔 채 머리 · 몸 · 꼬리만 옮기는 칸(제 좌표, 팔이 늘어 잇는다) — 키운 몸이
                        # 판 왼쪽 · 아래로 안 나가게. 동물째 옮기면 앞발이 화살표 대 위로 올라가 대 끝이 지저분했다


def body_at(hc):
    return hc[0] + A_BODY[0], hc[1] + A_BODY[1]


def hang_parts(P, r, hc, cheek=None, hands=A_HANDS, hand_r=3.4, body=(4.4, 7.4, 4.4), feet=(8.2, 5.0),
               kick=0.0, extra=(), back=()):
    """앞발로 매달린 앞모습: extra → 앞발 → 팔 → 머리 → 뒷발 → 몸 → back(꼬리 · 비막). 앞의 것이 위.
    body = (머리 가운데에서 몸 가운데까지 아래로, 가로 · 세로 반지름), feet = (머리 가운데에서 아래로, 좌우 간격).
    몸은 머리 뒤에 거의 숨는다(동그란 떡) — 판 밑까지 14줄뿐이라 머리를 키우는 쪽을 골랐다.
    팔은 테 없이 앞발에서 정수리 양옆으로 — 테를 그으면 이마에 줄이 생긴다.
    hc · extra · back 은 A_BODY 만큼 옮겨 그리고 앞발(hands)은 그 자리에 둔다 — 얼굴은 body_at(hc) 에 그린다"""
    dx, dy = A_BODY
    def mv(h): return (lambda a, b: h(a - dx, b - dy)) if callable(h) else h
    extra = [(n, mv(h), mv(c), ln) for n, h, c, ln in extra]
    back = [(n, mv(h), mv(c), ln) for n, h, c, ln in back]
    u0, w0 = hc = body_at(hc)
    arm_col = (lambda a, b: P["dark"] if a > u0 else P["fur"]) if P["tri"] else P["fur"]
    parts = list(extra)
    parts += [(f"hand{i}", ell(a, b, hand_r, hand_r * 0.9), P["paw"], True) for i, (a, b) in enumerate(hands)]
    parts += [(f"arm{i}", bar((a, b + 0.8), (u0 + sg * 0.36 * r, w0 - 0.7 * r), 1.8), arm_col, False)
              for i, ((a, b), sg) in enumerate(zip(hands, (-1, 1)))]
    parts += head_parts(P, hc, r, cheek=cheek)
    if feet:
        fw, fd = feet
        parts.append(("feet", any_of(ell(u0 - fd, w0 + fw + kick, 2.2, 1.4), ell(u0 + fd, w0 + fw - kick, 2.2, 1.4)),
                      P["paw"], True))
    if body:
        parts.append(body_part(P, (u0, w0 + body[0]), body[1], body[2]))
    return parts + list(back)


def hang(P, K, swing, r=9.0, hc=A_HC, mood="open", mouth="y", **kw):
    rig = Rig(A_GRIP[0], A_GRIP[1], swing, K)
    g, _, _ = draw(rig, hang_parts(P, r, hc, **kw))
    face(g, rig, P, hc=body_at(hc), r=r, mood=mood, mouth=mouth)
    return g


def hang_golden(P, K, k, ph):       # 볼주머니 빵빵 · 뒷발 동동
    kick = 1.0 * math.sin(2 * ph)
    mood = "squeeze" if k % 6 in (2, 3) else "open"
    return hang(P, K, 6.0 * math.sin(ph), cheek=1.2 + 0.1 * math.sin(2 * ph), kick=kick, mood=mood,
                mouth="none" if mood == "squeeze" else "y")


def hang_jungle(P, K, k, ph):       # 제일 작아서 그네처럼 크게 흔들 — 끝에 닿을 때 신나서 눈웃음
    sw = 14.0 * math.sin(ph)
    return hang(P, K, sw, kick=0.6 * math.sin(ph), mood="happy" if abs(math.sin(ph)) > 0.85 else "open")


def hang_pearl(P, K, k, ph):        # 한 발로 매달려 다른 발로 손 흔들기(3–8장)
    u0, w0 = A_HC
    wave = 3 <= k <= 8
    hands = (A_HANDS[0], (u0 + 7.6, 1.6 + 1.8 * math.sin(2 * ph))) if wave else A_HANDS
    return hang(P, K, (-5.0 if wave else 0.0) + 3.0 * math.sin(ph), hands=hands, mood="happy" if wave else "open",
                kick=0.6 * math.sin(2 * ph))


def hang_pudding(P, K, k, ph):      # 통통한 몸이 푸딩처럼 출렁 — 옆으로 퍼졌다 오므라든다
    j = math.sin(2 * ph)
    return hang(P, K, 5.0 * math.sin(ph), r=8.6, body=(4.0, 7.8 + 1.0 * j, 4.4 - 0.4 * j), feet=(7.8, 5.0 + 0.8 * j),
                mood="blink" if k == 6 else "open")


def hang_sapphire(P, K, k, ph):     # 턱걸이 — 앞발을 당겨 얼굴이 대 끝까지 올라갔다 내려온다
    pull = max(0.0, math.sin(ph))
    hc = (A_HC[0], A_HC[1] - 2.0 * pull)
    return hang(P, K, 3.0 * math.sin(2 * ph), hc=hc, mood="squeeze" if pull > 0.5 else "open",
                mouth="none" if pull > 0.5 else "y")


def hang_chinchilla(P, K, k, ph):   # 큰 귀가 흔들리고 북슬 꼬리가 몸과 거꾸로 흔들
    u0, w0 = A_HC
    tw = 2.0 * math.sin(ph + math.pi)
    tail = tail_part(P, [(u0 + 4.6, 13.8), (u0 + 8.8, 15.2), (u0 + 12.2 + tw * 0.4, 12.2 + tw)], scale=1.2)
    return hang(P, K, 6.0 * math.sin(ph), cheek=1.0, kick=0.8 * math.sin(2 * ph), back=[tail],
                mood="blink" if k == 4 else "open")


def hang_degu(P, K, k, ph):         # 술 달린 긴 꼬리가 밑에서 휙휙 · 앞니
    u0, w0 = A_HC
    tw = 2.4 * math.sin(2 * ph)
    tail = tail_part(P, [(u0 + 3.6, 14.6), (u0 + 7.4, 16.6), (u0 + 11.4, 16.2), (u0 + 14.2 + tw * 0.3, 13.4 + tw)],
                     scale=1.2)
    return hang(P, K, 6.0 * math.sin(ph), kick=0.8 * math.sin(2 * ph), back=[tail], mouth="teeth")


def hang_guinea(P, K, k, ph):       # 감자 몸이 축 늘어져 짧은 다리로 허공을 버둥버둥 · 땀 한 방울
    u0, w0 = hc = (A_HC[0], 9.4)
    sw = 4.0 * math.sin(ph)
    g = hang(P, K, sw, hc=hc, body=(4.6, 9.8, 4.8), feet=(8.4, 5.2), kick=1.0 * math.sin(4 * ph),
             mood="squeeze" if k % 4 in (1, 2) else "open")
    x, y = Rig(A_GRIP[0], A_GRIP[1], sw, K).cell(u0 + 9.8, 2.6 + 0.6 * (k % 3))
    for p in ((x, y), (x, y + 1), (x - 1, y + 1)):
        g.setdefault(p, A_SWEAT)
    return g


FERRET_X = 1.0


def hang_ferret(P, K, k, ph):       # 긴 몸이 축 늘어져 밑에서 오른쪽으로 휘고, 꼬리 끝이 살랑
    sw = 5.0 * math.sin(ph)
    wv = 1.2 * math.sin(ph + 1.0)
    rig = Rig(A_GRIP[0], A_GRIP[1], sw, K)
    r, hc = 7.8, (A_HC[0], 9.0)
    u0 = hc[0]
    FX = FERRET_X                   # 오른쪽으로 뻗는 길이 배율 — 몸을 키운 판에서 판 오른쪽 밖으로 안 나가게 줄인다
    spine = [(u0, 12.0), (u0 + 1.2 * FX, 14.8), (u0 + 6.6 * FX, 16.2), (u0 + 14.0 * FX, 15.6 + 0.4 * wv), (u0 + 19.6 * FX, 12.8 + wv)]
    back = [("body", chain(spine, 3.4, 3.0), P["fur"], False),
            ("hind", any_of(ell(u0 + 9.6 * FX, 18.2 + 0.4 * wv, 1.8, 1.3), ell(u0 + 15.6 * FX, 17.8 - 0.4 * wv, 1.8, 1.3)),
             P["paw"], True),
            tail_part(P, [(u0 + 19.6 * FX, 12.8 + wv), (u0 + 22.4 * FX, 9.4 + wv), (u0 + 23.0 * FX + wv, 5.6)])]
    g, _, _ = draw(rig, hang_parts(P, r, hc, body=None, feet=None, back=back))
    face(g, rig, P, hc=body_at(hc), r=r, mood="blink" if k == 5 else "open")
    return g


def hang_glider(P, K, k, ph):       # 비막을 활짝 펴고 연처럼 대롱대롱 — 비막이 바람에 부푼다
    sw = 4.0 * math.sin(ph)
    sp = 10.8 + 0.8 * math.sin(2 * ph)      # 머리보다 넓게 — 좁으면 비막이 머리 뒤에 숨는다
    rig = Rig(A_GRIP[0], A_GRIP[1], sw, K)
    r, hc = 7.4, (2.4, 9.2)                 # 왼쪽 비막 자리를 벌려 머리를 대보다 오른쪽에
    u0, w0 = hc
    back = [("body", ell(u0, 14.0, 4.6, 4.6), lambda a, b: P["belly"] if abs(a - u0) < 2.0 else P["fur"], False)]
    ay = 16.0 + 0.5 * math.sin(2 * ph)
    for sg, (hx_, hy) in zip((-1, 1), A_HANDS):    # 비막은 손목(대를 쥔 앞발)에서 발목까지
        back.append((f"foot{sg}", ell(u0 + sg * sp, ay, 1.6, 1.4), P["paw"], True))
        back.append((f"wing{sg}", tri((hx_, hy + 1.0), (hx_ + sg * 1.6, hy + 1.6), (u0 + sg * sp * 0.92, 8.4),
                                       (u0 + sg * (sp + 0.4), ay), (u0 + sg * 2.6, 17.4), (u0, 4.0)),
                     lambda a, b, sg=sg: P["dark"] if (a - u0) * sg > 0.78 * sp else P["fur"], False))
    back.append(tail_part(P, [(u0 + 1.6, 16.8), (u0 + 5.0, 18.4), (u0 + 9.0 + 0.8 * math.sin(ph), 17.6)]))
    g, _, _ = draw(rig, hang_parts(P, r, hc, body=None, feet=None, back=back))
    face(g, rig, P, hc=body_at(hc), r=r, mood="open", mouth="y")
    return g


HANG = {"golden": hang_golden, "jungle": hang_jungle, "pearl": hang_pearl, "pudding": hang_pudding,
        "sapphire": hang_sapphire, "chinchilla": hang_chinchilla, "degu": hang_degu, "guinea": hang_guinea,
        "ferret": hang_ferret, "glider": hang_glider}


def arrow(pid):
    P = PETS[pid]
    K = A_K * P["scale"]
    m = raster(A_PTS)
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        solid(f, m, sea.Cur(PEEK_WHITE), sea.Cur(OUT))   # 화살표는 커서 — 쓸 때 sea.mark 가 파랑 맨 끝 비트로 동물과 가른다
        f[1, 1] = sea.Cur(OUT)
        apart(f, HANG[pid](P, K, k, ph), m)
        frames.append(finish(clip(f)))
    return frames, (1, 1)


# ── 금지 표지 ────────────────────────────────────────────────────────────────
SR = 14.8   # wait · no 칸 표지 반지름 — 판(1..30)을 꽉 채운다. 테 두께는 그대로라 안쪽이 지름 23 → 26 (2026-10-09 몸 키움)


def sign(f, R=13.5):
    ring = {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
    slash = set()
    for t in range(-90, 91):
        x = y = 15.5 + t / 100 * (R - 1.5) * 0.7071
        slash |= disc(x, y, 1.3)
    solid(f, ring | slash, sea.Cur(SIGN), sea.Cur(SIGN_D))   # 금지 표지는 커서


def inner(f, R=13.5):
    """표지 테 안쪽(테에 안 닿게)만 남긴다"""
    return {p: c for p, c in f.items() if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) < R - 1.9}


def seed_part(c, ra, rb, rot, name="seed"):
    ca, cb = c
    cr, sr = math.cos(rot), math.sin(rot)

    def col(a, b):
        u = (a - ca) * cr + (b - cb) * sr
        v = -(a - ca) * sr + (b - cb) * cr
        return SEED_L if abs(v) < rb * 0.3 or (abs(abs(v) - rb * 0.62) < 0.25 and abs(u) < ra * 0.6) else SEED
    return (name, ell(ca, cb, ra, rb, rot), col, True)


# ── 골든: 쳇바퀴 / 팔 X ──────────────────────────────────────────────────────
def wheel(f, cx, cy, R, k):
    ang0 = -k * (2 * math.pi / 8) / 4
    for i in range(8):     # 바큇살
        a = ang0 + 2 * math.pi * i / 8
        for t in range(2, int(R * 2) - 2):
            x, y = cx + math.cos(a) * t / 2, cy + math.sin(a) * t / 2
            f[math.floor(x), math.floor(y)] = WHEEL_D
    ring = {p for p in disc(cx, cy, R) if math.hypot(p[0] + 0.5 - cx, p[1] + 0.5 - cy) > R - 1.6}
    for p in ring:
        f[p] = WHEEL
    for i in range(16):    # 바퀴 가로대 무늬가 돈다
        a = ang0 + 2 * math.pi * i / 16
        f[math.floor(cx + math.cos(a) * (R - 0.8)), math.floor(cy + math.sin(a) * (R - 0.8))] = WHEEL_L
    for p in disc(cx, cy, 1.6):
        f[p] = WHEEL_D


def wait_golden():
    P = PETS["golden"]
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        # 바퀴가 판을 꽉 채우고(받침 다리는 둘 자리가 없어 뺐다) 햄찌가 바퀴 안 바닥을 달린다 — 화살표만 하게
        cx, cy, R = 15.5, 15.5, 14.5
        wheel(f, cx, cy, R, k)
        bob = 0.5 * abs(math.sin(2 * ph))
        rig = Rig(17.6, 20.8 - bob, 6.0, 1.12)
        step = 2.2 * math.sin(2 * ph)
        parts, eye, nose, cheek = side_parts(P, s=-1, step=step)
        g, _, _ = draw(rig, parts)
        side_face(g, rig, P, eye, nose, cheek, s=-1, mood="open")
        f.update(g)
        for i, y in enumerate((12, 14, 16)):   # 달리는 줄 — 엉덩이 뒤 위
            x0 = 25 + (k + i) % 2
            f[x0, y] = OUT
            f[x0 + 1, y] = OUT
        frames.append(finish(clip(f)))
    return frames, (15, 20)


def no_golden():
    """앞발 둘을 X 로 엇갈려 막고 고개를 도리도리"""
    P = PETS["golden"]
    frames = []
    rig = Rig(15.5, 16.8, 0.0, 0.98)
    for k, ph in enumerate(phases()):
        f = {}
        sign(f, SR)
        turn = 1.6 * math.sin(ph)
        X = [("armA", bar((-4.6, -1.2), (4.2, 5.6), 1.3), P["paw"], True),
             ("armB", bar((4.6, -1.2), (-4.2, 5.6), 1.3), P["paw"], True)]
        parts = X + sit_parts(P, turn=turn, hand=[])
        o, _, _ = draw(rig, parts)
        face(o, rig, P, mood="squeeze", turn=turn)
        f.update(inner(o, SR))
        frames.append(finish(f))
    return frames, (15, 15)


# ── 펄: 해바라기씨 오물오물 / 씨 사수 ─────────────────────────────────────────
def wait_pearl():
    P = PETS["pearl"]
    frames = []
    rig = Rig(16.0, 18.4, 0.0, 1.0)
    for k, ph in enumerate(phases()):
        chew = k % 2
        left = 1.0 - (k % 6) / 9.0          # 위 끝부터 갉아 씨가 줄었다가 반 바퀴마다 새 씨
        top = -4.2 + 4.2 * (1 - left)
        bot = 3.6
        sc = (0.0, (top + bot) / 2)
        seed = seed_part(sc, 1.9, (bot - top) / 2, 0.0)
        hand = [(-2.5, sc[1] + 0.4), (2.5, sc[1] + 0.4)]
        parts = paws(P, hand, r=1.5) + [seed] + sit_parts(P, cheek=1.0 + 0.08 * chew, hand=[])
        f, _, _ = draw(rig, parts)
        face(f, rig, P, mood="happy" if k in (4, 5, 10, 11) else "open", mouth="none")
        whiskers(f, rig, HAM_HC, n=1)
        if k % 3 == 2:   # 부스러기 — 발 앞 바닥
            f[11 + k % 4, 29] = SEED_L
            f[20 - k % 3, 30] = SEED
        frames.append(finish(clip(f)))
    return frames, (16, 22)


def no_pearl():
    """제 몸만 한 해바라기씨를 꼭 끌어안고 몸을 홱 돌려 사수 — 눈 질끈"""
    P = PETS["pearl"]
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f, SR)
        side_ = -1 if k < 6 else 1
        rig = Rig(15.5 + side_ * 0.6, 17.2, side_ * 8.0, 0.9)
        seed = seed_part((0.0, 2.4), 3.0, 5.6, 0.0)
        hand = [(-3.4, 1.2), (3.4, 1.2)]
        parts = paws(P, hand, r=1.6) + [seed] + sit_parts(P, hc=(0, -6.2), turn=side_ * 1.8, hand=[])
        o, _, _ = draw(rig, parts)
        face(o, rig, P, hc=(0, -6.2), mood="squeeze", turn=side_ * 1.8, mouth="none")
        f.update(inner(o, SR))
        if k in (0, 6):
            x0 = 5 if side_ > 0 else 26
            for y in (9, 11, 13):
                f[x0, y] = OUT
        frames.append(finish(f))
    return frames, (15, 15)


# ── 푸딩: 볼주머니 빵빵 / 볼 빵빵 삐짐 ───────────────────────────────────────
def wait_pudding():
    P = PETS["pudding"]
    frames = []
    rig = Rig(16.0, 18.8, 0.0, 0.98)
    cheeks = [1.1, 1.18, 1.18, 1.28, 1.28, 1.38, 1.38, 1.48, 1.48, 1.48, 1.3, 1.15]
    for k, ph in enumerate(phases()):
        stuffing = k < 8 and k % 2 == 0
        hand = [(-1.6, -2.6), (1.6, -2.6)] if stuffing else [(-2.6, 0.6), (2.6, 0.6)]
        extra = [seed_part((0.0, -3.4), 1.2, 0.8, 0.6)] if stuffing else []
        parts = paws(P, hand, r=1.4) + extra + sit_parts(P, cheek=cheeks[k], hand=[])
        f, _, _ = draw(rig, parts)
        face(f, rig, P, mood="happy" if k in (8, 9) else "open", mouth="none" if stuffing else "y")
        if k in (8, 9):   # 반짝 — 꽉 찼다 (볼 바깥 위)
            for sg in (-1, 1):
                sx, sy = rig.cell(sg * 11.4, -11.6)
                for p in ((sx, sy - 1), (sx - 1, sy), (sx, sy), (sx + 1, sy), (sx, sy + 1)):
                    f[p] = hx("fff2a0ff")
        frames.append(finish(clip(f)))
    return frames, (16, 22)


def no_pudding():
    """볼을 한껏 부풀리고 고개를 홱 — 머리 위로 화난 표시가 톡톡"""
    P = PETS["pudding"]
    frames = []
    rig = Rig(15.5, 17.0, 0.0, 0.92)
    for k, ph in enumerate(phases()):
        f = {}
        sign(f, SR)
        side_ = -1 if k < 6 else 1
        turn = side_ * 2.0
        puff = 1.5 + 0.08 * (k % 2)
        parts = sit_parts(P, turn=turn, cheek=puff, hand=[(-2.0, 1.6), (2.0, 1.6)])
        o, _, _ = draw(rig, parts)
        face(o, rig, P, mood="sulk", turn=turn, mouth="none")
        f.update(inner(o, SR))
        ax, ay = rig.cell(-side_ * 7.0, -7.4)   # 💢 가운데 → 무늬 왼쪽 위. 고개 반대쪽 관자놀이(귀와 안 겹치게)
        ax, ay = ax - 1, ay - 1
        if k % 6 < 4:   # 💢
            for p in ((ax, ay), (ax + 2, ay), (ax, ay + 2), (ax + 2, ay + 2), (ax + 1, ay - 1), (ax - 1, ay + 1),
                      (ax + 3, ay + 1), (ax + 1, ay + 3)):
                f[p] = ANGER
        frames.append(finish(f))
    return frames, (15, 15)


# ── 블루사파이어: 톱밥 굴 파기 / 굴로 쏙 ──────────────────────────────────────
def dust_pile(f, cx, cy, ra, rb, k):
    for p in disc(0, 0, 1):
        pass
    m = {(x, y) for y in range(int(cy - rb) - 1, 32) for x in range(int(cx - ra) - 1, int(cx + ra) + 2)
         if ((x + 0.5 - cx) / ra) ** 2 + ((y + 0.5 - cy) / rb) ** 2 <= 1 and y <= 30}

    def col(p):
        return DUST_D if (p[0] * 3 + p[1] * 5 + k // 4) % 7 == 0 else DUST
    solid(f, m, col, BARK_D)
    return m


def wait_sapphire():
    P = PETS["sapphire"]
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        wig = 0.7 * math.sin(2 * ph)
        rig = Rig(12.0 + wig, 16.6, 34.0, 1.16)    # 머리를 오른쪽 아래 톱밥에 박고
        step = 2.0 * math.sin(2 * ph)
        parts, eye, nose, cheek = side_parts(P, s=1, step=step)
        g, _, _ = draw(rig, parts)
        f.update(g)
        pile = {}
        dust_pile(pile, 22.0, 31.0, 11.0, 10.0, k)
        f.update(pile)
        for j in range(4):   # 뒤로 튀는 톱밥
            t = (k / N * 2 + j / 4) % 1
            x = 21 - 18 * t
            y = 17 - 14 * 4 * t * (1 - t)
            f[math.floor(x), math.floor(y)] = DUST_D if j % 2 else DUST
            f[math.floor(x) + 1, math.floor(y)] = DUST
        frames.append(finish(clip(f)))
    return frames, (13, 18)


def no_sapphire():
    """톱밥 굴로 머리부터 쏙 — 엉덩이와 뒷발만 남아 버둥대다가 꼬리 끝까지 쏙 들어간다"""
    P = PETS["sapphire"]
    frames = []
    depth = [0, 0, 0.6, 1.2, 1.8, 2.6, 3.4, 4.2, 4.2, 3.0, 1.6, 0.6]
    for k, ph in enumerate(phases()):
        f = {}
        sign(f, SR)
        rig = Rig(15.5, 13.6 + depth[k] * 1.2, 0.0, 1.12)   # 굴에 머리를 박은 뒷모습 — 동그란 엉덩이 · 등줄 · 버둥대는 뒷발
        kick = 1.4 * math.sin(3 * ph)
        legs = [("legL", any_of(bar((-3.6, 3.0), (-6.4, -1.0 + kick), 1.3), ell(-6.6, -1.6 + kick, 1.7, 1.2)), P["paw"], True),
                ("legR", any_of(bar((3.6, 3.0), (6.4, -1.0 - kick), 1.3), ell(6.6, -1.6 - kick, 1.7, 1.2)), P["paw"], True)]
        stub = ("stub", ell(0.0, -6.4, 1.0, 1.3), P["paw"], True)
        butt = ("butt", ell(0.0, 1.6, 7.0, 7.8),
                lambda a, b: P["dark"] if abs(a) < 0.9 else P["belly"] if b > 6.0 else P["fur"], False)
        g, _, _ = draw(rig, [stub] + legs + [butt])
        pile = {}
        m = dust_pile(pile, 15.5, 29.6, 11.0, 6.2, k)
        hole = {(x, y) for x in range(12, 20) for y in (24, 25) if (x, y) in m}
        f.update(inner({p: c for p, c in g.items() if p[1] < 25}, SR))
        f.update(inner(pile, SR))
        for p in hole:
            if (p[0], p[1]) not in g or p[1] >= 25:
                f[p] = BARK_D
        frames.append(finish(f))
    return frames, (15, 15)


# ── 정글리안: 세수 / 죽은 척 ─────────────────────────────────────────────────
def wait_jungle():
    P = PETS["jungle"]
    frames = []
    rig = Rig(16.0, 18.6, 0.0, 1.0)
    for k, ph in enumerate(phases()):
        wash = k < 9
        if wash:
            up = math.sin(2 * ph * 1.5)
            hand = [(-1.8, -6.0 + 1.6 * up), (1.8, -6.0 - 1.6 * up)]
        else:
            hand = [(-2.4, 1.0), (2.4, 1.0)]
        parts = paws(P, hand, r=1.5) + sit_parts(P, hand=[])
        f, _, _ = draw(rig, parts)
        face(f, rig, P, mood="squeeze" if wash else ("happy" if k == 9 else "open"), mouth="none" if wash else "y")
        if wash:   # 앞발이 눈을 덮는다 — 얼굴을 다 그린 뒤 발을 다시 얹는다
            g, _, _ = draw(rig, paws(P, hand, r=1.5))
            f.update(g)
        if k in (9, 10):   # 반짝 — 말끔해졌다 (머리 양옆 위)
            for sg, dw in ((-1, 0.0), (1, -1.0)):
                sx, sy = rig.cell(sg * 10.6, -11.4 + dw)
                for p in ((sx, sy - 1), (sx - 1, sy), (sx, sy), (sx + 1, sy), (sx, sy + 1)):
                    f[p] = hx("fff2a0ff")
        frames.append(finish(clip(f)))
    return frames, (16, 21)


def no_jungle():
    """배를 드러내고 벌러덩 — 위에서 본 대자 자세, 죽은 척(×× 눈)에 혀 빼꼼, 네 발 끝이 파르르. 혼이 솔솔"""
    P = PETS["jungle"]
    frames = []
    rig = Rig(15.5, 16.6, 0.0, 0.86)
    for k, ph in enumerate(phases()):
        f = {}
        sign(f, SR)
        tw = 0.7 * math.sin(3 * ph)
        legs = []
        for i, (sh, tip) in enumerate((((-4.0, -1.0), (-9.6, -2.6 + tw)), ((4.0, -1.0), (9.6, -2.6 - tw)),
                                      ((-4.0, 6.0), (-8.6, 10.0 - tw)), ((4.0, 6.0), (8.6, 10.0 + tw)))):
            legs.append((f"leg{i}", any_of(bar(sh, tip, 1.2), ell(tip[0], tip[1], 1.6, 1.6)), P["paw"], True))
        hc = (0.0, -6.8)
        body = ("body", ell(0, 3.4, 5.4, 6.4), lambda a, b: P["belly"] if abs(a) < 3.6 else P["fur"], True)
        o, _, _ = draw(rig, legs + [body] + head_parts(P, hc, 6.6))
        face(o, rig, P, hc, 6.6, mood="x", mouth="none", blush=False)
        nx, ny = rig.cell(0.0, hc[1] + 6.6 * 0.2)
        o[nx, ny + 1] = NOSE     # 혀 빼꼼
        o[nx + 1, ny + 1] = NOSE
        f.update(inner(o, SR))
        g = 3 - (k % 6) // 2     # 혼 — 배에서 작은 유령이 솔솔
        gx, gy = 22, 6 + g
        for p in ((gx, gy), (gx + 1, gy), (gx - 1, gy + 1), (gx, gy + 1), (gx + 1, gy + 1), (gx + 2, gy + 1),
                  (gx - 1, gy + 2), (gx + 1, gy + 2)):
            f[p] = hx("ffffffd8")
        f[gx, gy + 1] = EYE
        frames.append(finish(f))
    return frames, (15, 15)


# ── 기니피그: 팝콘 점프 / 뀨잉 ────────────────────────────────────────────────
def hay(f, y, k):
    for x in range(3, 29):
        f[x, y] = hx("d9c06aff") if (x + k // 3) % 3 else hx("b89a40ff")
        if x % 4 == (k // 2) % 4:
            f[x, y - 1] = hx("d9c06aff")


def wait_guinea():
    P = PETS["guinea"]
    frames = []
    #   장:  0 1 2 3   4    5    6    7  8 9 10 11
    jump = [0, 0, 0, 2.6, 4.6, 5.4, 4.6, 2.6, 0, 0, 0, 0]
    twist = [0, 0, 0, -10, -18, 0, 18, 10, 0, 0, 0, 0]
    for k, ph in enumerate(phases()):
        f = {}
        hay(f, 28, k)
        air = jump[k] > 0
        rig = Rig(14.0, 21.6 - jump[k] * 1.2, twist[k], 1.0)
        parts, eye, nose, cheek = side_parts(P, s=1, step=1.6 if air else 0.0)
        g, _, _ = draw(rig, parts)
        side_face(g, rig, P, eye, nose, cheek, s=1, mood="squeeze" if air else ("blink" if k == 10 else "open"))
        f.update(g)
        if jump[k] >= 4:   # 신나서 튀는 줄
            for p in ((2, 13), (3, 12), (1, 17), (2, 17), (28, 7), (27, 6), (29, 10), (28, 10)):
                f[p] = OUT
        if k in (8,):      # 착지 먼지
            for p in ((5, 27), (4, 26), (26, 27), (27, 26)):
                f[p] = FAINT[1]
        frames.append(finish(clip(f)))
    return frames, (16, 19)


def no_guinea():
    """앞모습으로 입을 크게 벌려 뀨잉! — 소리 줄이 퍼지고 몸이 들썩"""
    P = PETS["guinea"]
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f, SR)
        loud = k % 4 < 2
        rig = Rig(15.5, 17.0 - (0.6 if loud else 0), 0.0, 0.9)
        body = ("body", ell(0, 3.0, 8.2, 5.8),
                lambda a, b: P["belly"] if abs(a) < 2.4 else P["fur"] if a < 0 else P["dark"], False)
        parts = sit_parts(P, hand=[(-2.6, 2.0), (2.6, 2.0)], body=body)
        o, _, _ = draw(rig, parts)
        face(o, rig, P, mood="squeeze" if loud else "open", mouth="o" if loud else "y")
        f.update(inner(o, SR))
        if loud:   # 뀨 — 양옆 소리 줄
            for sg in (-1, 1):
                x0 = 15 + sg * 7
                for i, dy in enumerate((-2, 0, 2)):
                    f[x0 + sg * (1 + (i % 2)), 11 + dy] = OUT
                    f[x0 + sg * (2 + (i % 2)), 11 + dy + (dy // 2)] = OUT
        frames.append(finish(f))
    return frames, (15, 15)


# ── 친칠라: 모래 목욕 데굴 / 귀 막기 ──────────────────────────────────────────
def wait_chinchilla():
    P = PETS["chinchilla"]
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        bowl = {(x, y) for y in range(22, 31) for x in range(2, 30)
                if ((x + 0.5 - 16) / 14) ** 2 + ((y + 0.5 - 21) / 9.4) ** 2 <= 1}
        ang = 360.0 * k / N
        rig = Rig(16.0, 14.4, ang, 0.74)
        tail = [(5.6, 8.2), (9.4, 8.6), (12.0, 6.0)]
        parts = sit_parts(P, hand=[(-2.4, 1.0), (2.4, 1.0)], tail=tail)
        g, _, _ = draw(rig, parts)
        face(g, rig, P, mood="happy")
        f.update(g)
        for p in bowl:
            if p[1] >= 24 or p not in f:
                f[p] = SAND_D if (p[0] + p[1] * 2) % 5 == 0 else SAND
        solid(f, {p for p in bowl if p[1] >= 26}, WHEEL, WHEEL_D)
        for j in range(5):   # 모래 먼지
            t = (k / N + j / 5) % 1
            sx = 16 + (j - 2) * 4 * t * 1.6
            sy = 23 - 10 * t
            f.setdefault((math.floor(sx), math.floor(sy)), hx("e6dcc2b0") if t < 0.5 else hx("e6dcc260"))
        frames.append(finish(clip(f)))
    return frames, (16, 14)


def no_chinchilla():
    """뒷발로 우뚝 서서 앞발 둘을 앞으로 쭉 — 저리 가! 큰 귀가 뒤로 젖혔다 섰다, 고개를 도리도리"""
    P = PETS["chinchilla"]
    frames = []
    rig = Rig(15.5, 18.6, 0.0, 0.8)
    for k, ph in enumerate(phases()):
        f = {}
        sign(f, SR)
        turn = 1.4 * math.sin(ph)
        push = 0.8 * max(0.0, math.sin(2 * ph))
        hc = (0.0, -7.0)
        pads = []
        for sg in (-1, 1):   # 내민 앞발 — 손바닥이 보이게 크게
            c = (sg * 4.6, -0.4 - push)
            pads.append((f"pad{sg}", ell(c[0], c[1], 2.3 + push * 0.3, 2.5 + push * 0.3), P["ear_in"], True))
        tail = [(5.0, 8.4), (9.4, 8.0), (11.2, 3.0 + 0.6 * math.sin(2 * ph))]
        parts = pads + sit_parts(P, hc=hc, turn=turn, hand=[], tail=tail)
        o, _, _ = draw(rig, parts)
        for sg in (-1, 1):   # 손가락 줄
            cx, cy = rig.cell(sg * 4.6, -2.4 - push)
            for dx in (-1, 1):
                o[cx + dx, cy] = P["paw"]
        face(o, rig, P, hc, mood="sulk", turn=turn, mouth="none")
        whiskers(o, rig, hc, turn=turn, n=1)
        f.update(inner(o, SR))
        frames.append(finish(f))
    return frames, (15, 15)


# ── 페럿: 터널에서 쑥 / 쉭쉭 전투 춤 ─────────────────────────────────────────
def ferret_up(P, rise, look=0.0, k=0):
    """터널 구멍(가운데 (0, 0))에서 위로 솟은 페럿 — 긴 목/몸이 구멍 밑까지 이어진다"""
    hc = (look, -rise - 2.0)
    neck = ("neck", chain([(0, 4.0), (0, -rise * 0.5), (look * 0.6, -rise + 2.0)], 3.6, 3.4), P["fur"], False)
    paws_ = paws(P, [(-2.6, -rise + 5.0), (2.6, -rise + 5.0)], r=1.4) if rise > 6 else []
    return paws_ + head_parts(P, hc, 6.6, turn=look * 0.6) + [neck], hc


def wait_ferret():
    P = PETS["ferret"]
    frames = []
    #   장: 0 1 2 3   4   5   6   7   8   9   10 11
    rise = [0, 0, 2, 6, 10, 12, 12, 12, 12, 10, 5, 0]
    look = [0, 0, 0, 0, 0, -1.6, -1.6, 1.6, 1.6, 0, 0, 0]
    for k, ph in enumerate(phases()):
        f = {}
        ox, oy = 15.5, 20.4
        rig = Rig(ox, oy, 0.0, 0.95)
        # 터널: 세로 관(가운데) + 왼쪽으로 꺾인 가로 관 — 구멍을 낮춰 페럿이 솟을 자리를 넓혔다
        tube = {(x, y) for y in range(21, 31) for x in range(9, 23)} | {(x, y) for y in range(26, 31) for x in range(1, 11)}
        solid(f, tube, lambda p: TUBE_L if p[0] in (11, 12) or p[1] in (27, 28) and p[0] < 9 else TUBE, TUBE_D)
        hole = {(x, y) for x in range(7, 25) for y in range(17, 25)
                if ((x + 0.5 - 15.5) / 7.6) ** 2 + ((y + 0.5 - 21) / 2.6) ** 2 <= 1}
        solid(f, hole, hx("2a3a2eff"), TUBE_D)
        if rise[k] > 0:
            parts, hc = ferret_up(P, rise[k], look[k], k)
            g, _, _ = draw(rig, parts)
            face(g, rig, P, hc, 6.6, mood="open", turn=look[k] * 0.6)
            f.update({p: c for p, c in g.items() if p[1] < 21 or p in hole and p[1] < 22})
        else:   # 어둠 속 눈 둘이 반짝
            if k in (0, 1):
                f[13, 20] = HI
                f[18, 20] = HI
        frames.append(finish(clip(f)))
    return frames, (15, 26)


def no_ferret():
    """등을 활처럼 굽히고 입을 벌려 쉭쉭 — 옆으로 콩콩 뛰는 페럿 전투 춤, 꼬리가 부풀었다"""
    P = PETS["ferret"]
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f, SR)
        hop = abs(math.sin(ph * 2)) * 1.6
        dx = 1.2 * math.sin(ph)
        rig = Rig(14.4 + dx, 15.4 - hop * 1.2, 0.0, 0.72)
        arch = 3.4
        body = ("body", chain([(-8.0, 2.0), (-4.0, -arch), (2.0, -arch), (6.0, 0.0)], 3.4, 3.0), P["fur"], False)
        legs = ("legs", any_of(bar((-7.4, 3.0), (-8.0, 9.0), 1.2), bar((-4.6, 3.0), (-5.0, 9.0), 1.2),
                               bar((3.6, 1.0), (4.0, 9.0), 1.2), bar((6.0, 2.0), (7.0, 9.0), 1.2)), P["dark"], False)
        tail = ("tail", chain([(-9.0, 2.0), (-11.8, 0.0), (-12.2, -3.4)], 2.2, 2.6), P["dark"], False)
        hc = (8.4, -2.6)
        hd = head_parts(P, hc, 5.8)
        o, _, _ = draw(rig, hd + [body, legs, tail])
        face(o, rig, P, hc, 5.8, mood="squeeze", mouth="o")
        f.update(inner(o, SR))
        if k % 3 == 0:   # 쉭 — 머리 앞 줄
            bx, by = rig.cell(15.0, -3.6)
            for p in ((bx, by), (bx + 1, by - 1), (bx + 1, by + 2), (bx + 2, by + 2)):
                f[p] = OUT
        frames.append(finish(f))
    return frames, (15, 15)


# ── 슈가글라이더: 활공 / 비막 망토 ────────────────────────────────────────────
def glider_parts(P, spread=1.0, flap=0.0):
    """활짝 편 비막 — 손목에서 발목까지 뒷날이 안으로 오목하게 휜다. 바깥 테는 짙게"""
    wings = []
    for sg in (-1, 1):
        wx, wy = sg * (3 + 8.4 * spread), -2.6 - flap
        fx, fy = sg * (3 + 7.2 * spread), 7.6 + flap
        poly = [(sg * 2.4, -3.6), (wx, wy), (wx - sg * 1.2, wy + 2.4), (wx - sg * 2.4, wy + 5.0),
                (fx - sg * 0.6, fy - 2.4), (fx, fy), (sg * 2.4, 6.4)]
        edge = [(wx - sg * 1.6, wy + 0.6), (wx - sg * 3.0, wy + 4.4), (fx - sg * 1.8, fy - 2.0)]
        wings.append((f"hand{sg}", ell(wx, wy, 1.3, 1.3), P["paw"], True))
        wings.append((f"foot{sg}", ell(fx, fy, 1.3, 1.3), P["paw"], True))
        wings.append((f"wing{sg}", tri(*poly),
                      lambda a, b, sg=sg, edge=edge: P["dark"] if (a * sg) > 2.4 + 6.6 * spread - 0.3 * b else P["fur"],
                      False))
        _ = edge
    return wings


def wait_glider():
    P = PETS["glider"]
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        bob = math.sin(ph) * 1.0
        rig = Rig(16.0, 15.4 + bob, -6.0 * math.cos(ph), 0.8)
        flap = 0.8 * math.sin(2 * ph)
        tail = [(0.0, 7.0), (0.6, 11.4), (-0.6 + 0.6 * math.sin(ph), 14.6)]
        parts = [] + head_parts(P, (0, -6.0), 6.6) + glider_parts(P, 1.0, flap) + \
            [("body", ell(0, 2.4, 3.8, 5.2), lambda a, b: P["belly"] if abs(a) < 1.8 else P["fur"], False),
             tail_part(P, tail)]
        g, _, _ = draw(rig, parts)
        face(g, rig, P, (0, -6.0), 6.6, mood="open")
        f.update(g)
        for i, y in enumerate((5, 9, 23, 27)):   # 바람 줄이 뒤로 흐른다
            x0 = (28 - (k * 3 + i * 7) % 26)
            for dx in range(3):
                f.setdefault((x0 + dx, y), hx("7cc4d8b0"))
        frames.append(finish(clip(f)))
    return frames, (16, 17)


def no_glider():
    """비막을 담요처럼 둘둘 말고 웅크림 — 담요 끝을 앞발로 눈 밑까지 끌어올리고, 반 바퀴마다 쏙 숨었다가
    큰 눈만 빼꼼 내민다. 등줄 · 귀는 늘 보인다"""
    P = PETS["glider"]
    frames = []
    rig = Rig(15.5, 16.9, 0.0, 0.88)
    #  장:  0  1    2    3    4    5    6    7    8   9   10  11
    hide = [0, 0, 0.0, 0.0, 1.2, 2.6, 3.4, 3.4, 2.6, 1.2, 0.0, 0.0]
    for k, ph in enumerate(phases()):
        f = {}
        sign(f, SR)
        hc = (0.0, -5.0 + hide[k])
        top = -4.6               # 담요 윗단(앞발이 쥔 자리)
        blanket = ("blanket", any_of(ell(0, 3.2, 8.6, 7.8), ell(0, top + 1.0, 7.4, 2.0)),
                   lambda a, b: P["dark"] if b < top + 1.2 and abs(a) > 5.6 or abs(a - 0.6 * (b - 2)) < 0.5 else P["fur"],
                   True)
        hands = paws(P, [(-2.2, top + 0.6), (2.2, top + 0.6)], r=1.3)
        head = head_parts(P, hc, 6.8)
        o, _, _ = draw(rig, hands + [blanket] + head)
        # 얼굴은 담요 위로 나온 칸에만 — 눈은 담요 윗단보다 위일 때만
        face_f = {}
        face(face_f, rig, P, hc, 6.8, mood="open" if hide[k] < 2 else "blink", mouth="none", blush=False)
        cut = rig.world(0, top + 0.2)[1]
        for p, c in face_f.items():
            if p[1] < cut and p in o:
                o[p] = c
        f.update(inner(o, SR))
        frames.append(finish(f))
    return frames, (15, 15)


# ── 데구: 나무 갉기 / 등 돌려 꼬리 탁탁 ───────────────────────────────────────
def wait_degu():
    P = PETS["degu"]
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        gnaw = k % 2
        # 나무 토막 (오른쪽 아래) — 왼쪽 끝 · 갉은 자국은 코 자리(갉지 않는 장)에 맞춘다
        nx, ny = Rig(14.0, 21.2, 10.0, 1.0).cell(10.9, 0.5)
        L, T = nx + 1, ny - 6
        log = {(x, y) for x in range(L, 31) for y in range(T, 29)}
        bite = {(L, ny - 3), (L, ny - 2), (L + 1, ny - 2), (L, ny - 1), (L, ny)}
        solid(f, log - bite, lambda p: WOOD if p[0] == L + 1 or p[1] in (T + 1, T + 2) else BARK_D if p[0] % 3 == 0 else BARK,
              BARK_D)
        rig = Rig(14.0 + 0.4 * gnaw, 21.2, 10.0, 1.0)
        tw = 1.4 * math.sin(ph)
        tail = [(-7.0, 1.6), (-10.0, 2.2), (-11.6, -1.6 + tw), (-11.4, -5.0 + tw)]   # 판 안에 들게 위로 말아 올림
        parts, eye, nose, cheek = side_parts(P, s=1, step=0.0, tail=tail)
        g, _, _ = draw(rig, parts)
        side_face(g, rig, P, eye, nose, cheek, s=1, mood="squeeze" if gnaw else "open", whisk=False)
        f.update(g)
        for j in range(3):   # 나뭇조각이 튄다
            t = (k / N * 3 + j / 3) % 1
            x, y = L - 3 * t + j, T + 1 - 8 * 4 * t * (1 - t)
            f[math.floor(x), math.floor(y)] = WOOD
        frames.append(finish(clip(f)))
    return frames, (14, 22)


def no_degu():
    """등을 홱 돌려 앉아 술 달린 꼬리로 바닥을 탁탁 — 가끔 어깨너머로 흘깃"""
    P = PETS["degu"]
    frames = []
    rig = Rig(15.5, 17.4, 0.0, 0.86)
    for k, ph in enumerate(phases()):
        f = {}
        sign(f, SR)
        sw = math.cos(ph)
        tail = [(0.0, 8.0), (sw * 4.4, 10.4), (sw * 8.4, 9.6), (sw * 10.4, 6.0 - abs(sw))]   # 표지 안에 들게 짧게
        glance = k in (5, 6)
        hd = head_parts(P, HC, HR, turn=0.0, back=True)
        parts = [tail_part(P, tail, lined=True, scale=1.3)] + hd + [feet(P), body_part(P, back=True)]
        o, _, _ = draw(rig, parts)
        if glance:   # 어깨너머 흘깃 — 오른쪽 볼에 눈 하나
            ex, ey = rig.cell(HR * 0.62, HC[1] - 0.2)
            dot(o, ex, ey, EYE)
            dot(o, ex, ey + 1, EYE)
        f.update(inner(o, SR))
        if abs(sw) > 0.9:   # 탁 — 꼬리 끝 바닥 줄
            x = round(rig.world(sw * 10.4, 0)[0])
            y = rig.cell(0, 8.6)[1]
            for p in ((x - 1, y), (x + 1, y), (x, y + 1)):
                f.setdefault(p, OUT)
        frames.append(finish(f))
    return frames, (15, 15)


WAIT = {"golden": wait_golden, "pearl": wait_pearl, "pudding": wait_pudding, "sapphire": wait_sapphire,
        "jungle": wait_jungle, "guinea": wait_guinea, "chinchilla": wait_chinchilla, "ferret": wait_ferret,
        "glider": wait_glider, "degu": wait_degu}
NO = {"golden": no_golden, "pearl": no_pearl, "pudding": no_pudding, "sapphire": no_sapphire, "jungle": no_jungle,
      "guinea": no_guinea, "chinchilla": no_chinchilla, "ferret": no_ferret, "glider": no_glider, "degu": no_degu}


# ══ 나머지 14칸 ═════════════════════════════════════════════════════════════
# 짹짹이(bird.py) · 댕댕이(dog.py) 와 같은 틀이다 — 열 마리가 장면 하나를 같이 쓰고 털빛 · 무늬 · 귀 · 머리 꼴 · 꼬리만
# 마리마다 다르다(PETS 그대로). busy · help · person · pin 은 작은 화살표 + 그 밑에 앉은 작은 앞모습 + 오른쪽 소품,
# 크기 조절 4칸은 그 축으로 쭉 기지개. 화살표 · 핫스팟은 무엇도 덮지 않는다 — 화살표를 맨 나중에 칠한다(사용자 요구).
MINI_S = 0.8                                     # 작은 화살표 배율 (짹짹이 · 댕댕이와 같다)
MINI_BOX = (1.0, 17.0, 12.5, 30.6)              # 작은 앞모습이 들어갈 칸(왼 · 위 · 오른 · 아래) — 화살표 밑, 소품은 오른쪽
CHEV, CHEV_L = hx("f59a5aff"), hx("f59a5aa0")    # 화살촉 (짙은 것 · 옅은 것) — 짹짹이와 같은 주황
HAY, HAY_D = hx("d9c06aff"), hx("b89a40ff")      # 건초 (기니피그 wait 의 건초와 같은 색)
SKIN, HAIR, SHIRT, SHIRT_D = hx("f7d7bcff"), hx("5a3a28ff"), hx("4a7fb5ff"), hx("2e5a88ff")   # 사람
PENCIL, PENCIL_D, LEAD = hx("f5c842ff"), hx("c8961cff"), hx("3a3a3aff")
ERASER, FERRULE = hx("f2a0a8ff"), hx("b8b8c0ff")
BALL, BALL_RING, BALL_D = hx("cfe9f660"), hx("9fd2ecff"), hx("5a9cc4ff")    # 햄스터 볼 — 속은 반투명
SEED_FADE = (hx("8a8494ff"), hx("3b3540a0"), hx("3b354050"))                 # 로딩 씨앗 — 막 지나간 것부터


def tail_sit(P, w=0.0):
    """앉은 앞모습의 꼬리 자리(제 좌표, 엉덩이 오른쪽) — 꼬리 없는 햄찌 · 기니피그는 None. w 로 끝이 살랑"""
    t = P["tail"]
    if not t:
        return None
    if t == "tuft":
        return [(5.0, 8.0), (8.4, 8.8), (10.6 + w, 6.4), (10.6 + w, 3.6)]
    if t == "glider":
        return [(4.6, 7.8), (8.4, 9.2), (11.2 + w, 6.6)]
    if t == "ferret":
        return [(5.0, 7.6), (8.8, 8.6), (11.2 + w, 6.0)]
    return [(5.6, 8.2), (9.4, 8.6), (12.0 + w, 6.0)]


def pet_sit(P, rig, mood="open", hand=None, cheek=None, turn=0.0, wag=0.0, extra=(), mouth="y", body=None, cur=()):
    """앉은 앞모습 한 장 → (칸 사전, 칸 집합). cur 에 든 부위(extra 의 소품 이름)는 테까지 커서로 칠한다"""
    g, mask, reg = draw(rig, sit_parts(P, turn=turn, cheek=cheek, hand=hand, extra=extra, tail=tail_sit(P, wag),
                                       body=body))
    g.update({p: sea.Cur(g[p]) for p, n in reg.items() if n in cur})
    face(g, rig, P, mood=mood, turn=turn, mouth=mouth)
    return g, mask


def fit_rig(parts, box, kmax, ang=0.0, align="bottom"):
    """parts 를 box(왼 · 위 · 오른 · 아래, 화면) 안에 가장 크게(kmax 까지) 넣는 Rig — 아래(또는 가운데)에 붙인다"""
    _, m, _ = draw(Rig(16.0, 16.0, ang, 1.0), parts)
    x0, x1 = min(x for x, _ in m) - 16.0, max(x for x, _ in m) + 1 - 16.0
    y0, y1 = min(y for _, y in m) - 16.0, max(y for _, y in m) + 1 - 16.0
    L, T, R, B = box
    k = min(kmax, (R - L) / (x1 - x0), (B - T) / (y1 - y0))
    ox = (L + R) / 2 - (x0 + x1) / 2 * k
    oy = B - y1 * k if align == "bottom" else (T + B) / 2 - (y0 + y1) / 2 * k
    return Rig(ox, oy, ang, k)


def mini_arrow():
    return raster([(1 + x * MINI_S, 1 + y * MINI_S) for x, y in PEEK_CUR])


def companion(P, scene):
    """작은 화살표 + 그 밑에 앉은 작은 앞모습(볼 오물오물 · 꼬리 살랑 · 한 번 끔뻑) + scene(k, ph) 이 그리는 소품.
    화살표 둘레 한 칸을 비우고 화살표를 맨 나중에 찍어 동물도 소품도 화살표를 못 가린다. 핫스팟은 화살표 끝 (1, 1)"""
    am = mini_arrow()
    near = {(x + dx, y + dy) for x, y in am for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    rig = fit_rig(sit_parts(P, hand=None), MINI_BOX, 0.62)   # 몸만 재서 맞춘다 — 꼬리는 오른쪽으로 삐져도 된다
    ham = P["head"] == "ham"
    frames = []
    for k, ph in enumerate(phases()):
        f = scene(k, ph)
        g, _ = pet_sit(P, rig, mood="blink" if k == 7 else "open",
                       cheek=P["cheek"] * (1.0 + (0.08 if ham and k % 2 else 0.0)), wag=1.2 * math.sin(ph))
        f.update(g)
        f = {p: c for p, c in clip(f).items() if p not in near}
        solid(f, am, sea.Cur(PEEK_WHITE), sea.Cur(OUT))   # 화살표는 커서
        f[1, 1] = sea.Cur(OUT)
        frames.append(finish(f))
    return frames, (1, 1)


SEED_ROWS = [".s.", "sLs", "sLs", ".s."]   # 세운 해바라기씨 3×4 — 까만 바탕에 흰 줄


def seed_at(f, x0, y0, col=SEED, light=SEED_L):
    for j, row in enumerate(SEED_ROWS):
        for i, ch in enumerate(row):
            if ch != ".":
                f[x0 + i, y0 + j] = col if ch == "s" else light


def busy(P):
    """오른쪽 아래에 해바라기씨 여덟 알이 동그랗게 놓이고, 한 알씩 차례로 진해지며 돈다(로딩 원)"""
    cx, cy, R = 22.0, 21.5, 6.4

    def scene(k, ph):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = round(cx + R * math.cos(a) - 1.5), round(cy + R * math.sin(a) - 2.0)
            lag = (head - i) % 8
            if lag < 1:
                seed_at(f, x, y)
            elif lag < 2.5:
                seed_at(f, x, y, SEED_FADE[0], SEED_L)
            else:
                seed_at(f, x, y, SEED_FADE[1] if lag < 4.5 else SEED_FADE[2], hx("e8e2d680"))
        return {p: sea.Cur(c) for p, c in f.items()}   # 도는 씨앗 고리는 커서(로딩 원)
    return companion(P, scene)


QHAY = [(22.0, 22.0), (22.0, 18.6), (24.4, 16.2), (27.0, 13.4), (27.0, 9.4), (24.2, 6.6), (20.4, 6.8), (18.6, 9.4)]


def help_(P):
    """건초 한 가닥이 물음표 꼴로 휘어 끝이 살랑, 점 자리에 해바라기씨 한 알이 통통"""
    def scene(k, ph):
        f = {}
        pts = [(x, y) for x, y in QHAY]
        pts[-1] = (pts[-1][0], pts[-1][1] + 0.7 * math.sin(ph))
        pts[-2] = (pts[-2][0] + 0.3 * math.sin(ph), pts[-2][1])
        at, _ = along(pts)
        o, _, _ = draw(Rig(0, 0, 0, 1.0), [("hay", chain(pts, 1.25, 1.05),
                                            lambda a, b: HAY_D if at(a, b) % 3.2 < 0.8 else HAY, False)])
        f.update(o)
        seed_at(f, 21, 25 - (1 if k % 6 in (1, 2) else 0))
        return {p: sea.Cur(c) for p, c in f.items()}   # 물음표(건초)와 점(씨앗)은 커서
    return companion(P, scene)


def person(P):
    """사람이 한 손을 흔들고, 다른 손바닥에 해바라기씨를 올려 작은 친구 쪽으로 내민다"""
    def scene(k, ph):
        f = {}
        rig = Rig(23.4, 25.6, 0.0, 0.7)
        wave = -2.0 * abs(math.sin(ph))
        hand = (8.8, -8.4 + wave)
        palm = (-11.0, 0.4)
        parts = [("hand", ell(*hand, 2.2, 2.2), SKIN, True), ("sleeve", bar((5.0, -0.5), hand, 1.8), SHIRT, False),
                 ("palm", ell(*palm, 2.6, 1.7), SKIN, True), ("sleeve2", bar((-5.0, 0.0), palm, 1.8), SHIRT, False),
                 ("face", ell(0.0, -7.2, 4.6, 4.2), SKIN, True), ("hair", ell(0.0, -8.6, 5.4, 4.8), HAIR, False),
                 ("torso", ell(0, 3.0, 7.6, 6.4), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
        out, mask, _ = draw(rig, parts)
        for sg in (-1, 1):
            ex, ey = rig.cell(sg * 2.0, -7.4)
            out[ex, ey] = EYE
            out[ex, ey + 1] = EYE
            out[rig.cell(sg * 3.0, -5.4)] = PINK
        f.update({p: sea.Cur(c) for p, c in out.items() if p[1] <= 30})   # 사람은 커서, 손바닥 위 씨앗은 동물(소품)
        px, py = rig.cell(*palm)
        top = min(y for x, y in mask if x == px)
        seed_at(f, px - 1, top - 3)
        return f
    return companion(P, scene)


def pin(P):
    """빨간 지도 핀 동그라미 속에 그 마리 얼굴 — 귀가 핀 위로 솟는다. 핀이 통통 튀고 땅에 닿으면 눈웃음"""
    def scene(k, ph):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 16.0 + dy
        for x in range(19, 27):
            f.setdefault((x, 30), hx("2a1c2260") if dy else hx("2a1c22a0"))
        pinm = disc(cx, cy, 6.4) | raster([(cx - 4.6, cy + 3.4), (cx + 4.6, cy + 3.4), (cx, cy + 12.4)])
        solid(f, pinm, sea.Cur(SIGN), sea.Cur(SIGN_D))   # 핀 몸통은 커서, 속 얼굴 · 땅 줄은 동물
        r = 7.0
        kk = 4.5 / r
        rig = Rig(cx, cy + 0.6 - (0.0 if P["head"] == "ham" else 0.6), 0.0, kk)
        hd, _, _ = draw(rig, head_parts(P, (0.0, 0.0), r))
        face(hd, rig, P, hc=(0.0, 0.0), r=r, mood="happy" if dy == 0 else "open")
        f.update(hd)
        return f
    return companion(P, scene)


# ── hand · up: 뒷발로 선 앞모습 ───────────────────────────────────────────────
def stand_parts(P, bob=0.0, hands=((-2.2, 0.0), (2.2, 0.0)), arms=(), extra=(), head_dy=None):
    """뒷발로 선 앞모습 — 몸은 세로로 길쭉, 앞발은 가슴 앞. bob 만큼 몸이 내려가 웅크린다(머리는 head_dy 만큼).
    arms: [(어깨, 앞발)] 은 팔(털)로 이어 그린다 — 들어 올린 앞발"""
    ham = P["head"] == "ham"
    hdy = bob if head_dy is None else head_dy
    hc = (0.0, (-5.8 if ham else -7.2) + hdy)
    parts = list(extra) + paws(P, hands, r=1.5)
    for i, (sh, pw) in enumerate(arms):
        parts.append((f"pw{i}", ell(pw[0], pw[1], 1.8, 1.7), P["paw"], True))
        parts.append((f"arm{i}", bar(sh, pw, 1.5), P["dark"] if P["tri"] and sh[0] > 0 else P["fur"], False))
    parts += head_parts(P, hc, 6.8)
    parts.append(("feet", any_of(ell(-3.2, 10.4, 2.2, 1.2), ell(3.2, 10.4, 2.2, 1.2)), P["paw"], True))
    parts.append(body_part(P, (0.0, 3.2 + bob * 0.6), 6.4 if ham else 5.8, 7.4 - bob * 0.4))
    tl = tail_sit(P, 0.0)
    if tl:
        parts.append(tail_part(P, [(x, y + 1.6) for x, y in tl]))
    return parts, hc


H_ANG = -62.0     # hand: 옆모습 몸을 일으켜 세운 각 — 코가 오른쪽 위를 본다
H_HOT = (18, 2)   # 늘어난 주둥이 끝 맨 위 칸 — 장마다 몸째 옮겨 이 칸에 맞춘다
H_K = 1.0


def hand_parts(P, e):
    """옆모습으로 고개를 젖히고 주둥이를 화면 바로 위로 늘인 부위들 — e 0 줄음 → 1 쭉.
    늘면 가늘고 줄면 통통해서 말랑하게 보인다. 주둥이는 테두리 없이 머리에 붙여 한 덩이로 읽히게"""
    parts, eye, _, cheek = side_parts(P, s=1)
    L = 1.3 if P["tri"] else 1.0
    base = (5.4 * L + 3.0, 0.2)
    t = math.radians(90.0 + H_ANG)
    d = (math.cos(t), -math.sin(t))          # 제 좌표에서 화면 바로 위 쪽
    n = 1.8 + 6.2 * e
    mid = (base[0] + d[0] * n * 0.55, base[1] + d[1] * n * 0.55)
    tip = (base[0] + d[0] * n, base[1] + d[1] * n)
    r0 = 2.9 - 0.5 * e
    fur = P["dark"] if P["tri"] or P["cap"] or P["mask"] else P["fur"]

    def col(a, b):   # 등 쪽(화면 왼쪽)은 털빛, 턱 쪽(오른쪽)은 배 색 — 한 색이면 흰 막대로 읽힌다
        return fur if (a - base[0]) * d[1] - (b - base[1]) * d[0] > 0.35 else P["belly"]
    mz = ("mz", any_of(bar(base, mid, r0, r0 * 0.8), bar(mid, tip, r0 * 0.8, 1.7 - 0.3 * e)), col, False)
    return [mz] + parts, eye, tip, cheek


def hand(P):
    """고개를 젖혀 위를 보고 말랑한 주둥이를 위로 쭉 늘여 그 끝으로 콕콕 — 늘 때 가늘어지고 줄 때 통통.
    끝 맨 위 칸(분홍 코)이 핫스팟이고 장마다 몸째 옮겨 그 칸에 맞춘다.
    (머리 위로 한 앞발을 뻗은 판은 앞발이 귀 하나로 읽혀 접었다)"""
    frames = []
    for k, ph in enumerate(phases()):
        e = 0.5 + 0.5 * math.cos(2 * ph)              # 두 번 콕
        parts, eye, tip, cheek = hand_parts(P, e)
        rig = Rig(16.0, 16.0, H_ANG, H_K)
        g, mask, _ = draw(rig, parts)
        top = min(y for _, y in mask)
        tx = min((x for x, y in mask if y == top), key=lambda x: abs(x + 0.5 - rig.world(*tip)[0]))
        dx, dy = H_HOT[0] - tx, H_HOT[1] - top
        side_face(g, rig, P, eye, tip, cheek, s=1, mood="happy" if e > 0.7 else "open", whisk=False, mouth=False)
        f = {(x + dx, y + dy): c for (x, y), c in g.items()}
        x, y = H_HOT
        f[x, y] = NOSE                                 # 코끝 — 핫스팟
        for sg in (-1, 1):                             # 수염 — 주둥이 끝 양옆
            for i in (2, 3):
                f.setdefault((x + sg * i, y + 2 + (i - 2)), OUT)
        if e > 0.7:                                    # 콕 — 끝 위 양옆 튀는 줄
            for p in ((x - 3, y), (x - 4, y - 1), (x + 3, y), (x + 4, y - 1)):
                f.setdefault(p, OUT)
        lost = [p for p in f if not (1 <= p[0] <= 30 and 1 <= p[1] <= 30)]
        if lost:
            print(f"  ! hand {k}장: 판 밖으로 {len(lost)}칸 잘림")
        frames.append(finish(clip(f)))
    return frames, H_HOT


def up(P):
    """뒷발로 우뚝 서서 두 앞발을 가슴 앞에 모으고 싹싹 — 간식 달라고 조른다. 머리는 그 자리, 몸만 들썩여
    핫스팟(머리 꼭대기 가운데)이 장마다 같은 칸"""
    base_parts, hc0 = stand_parts(P)
    rig = fit_rig(base_parts, (5.0, 4.0, 27.0, 29.6), 0.82)
    frames = []
    for k, ph in enumerate(phases()):
        bob = 0.9 * abs(math.sin(ph))
        rub = 0.7 * math.sin(4 * ph)
        parts, hc = stand_parts(P, bob=bob, hands=[(-1.5, -0.4 + rub), (1.5, -0.4 - rub)], head_dy=0.0)
        f, _, _ = draw(rig, parts)
        face(f, rig, P, hc=hc, r=6.8, mood="happy" if k % 4 < 2 else "open", mouth="o" if k % 4 < 2 else "y")
        if k % 4 < 2:   # 싹싹 — 앞발 옆 움직임 줄
            for sg in (-1, 1):
                x0, y0 = rig.cell(sg * 4.6, -1.6)
                for p in ((x0, y0), (x0 + sg, y0 + 1)):
                    f.setdefault(p, OUT)
        for x in range(9, 24):   # 바닥 그림자
            f.setdefault((x, 30), hx("2a1c2250"))
        frames.append(finish(clip(f)))
    cx = math.floor(rig.world(0.0, 0.0)[0])
    hot = min((p for p, c in frames[0].items() if c[3] == 255 and p[0] == cx), key=lambda p: p[1])
    return frames, hot


# ── cross: 코가 십자 가운데 ───────────────────────────────────────────────────
def cross(P):
    """앞모습 얼굴, 코가 (15, 15). 코 줄 양옆으로 뻗은 수염이 가로 조준선, 머리 위 · 턱 밑 줄이 세로선.
    볼을 오물오물하고 한 번 끔뻑"""
    r = 7.6
    rig = Rig(15.5, 15.5 - 0.2 * r, 0.0, 1.0)      # 코(제 좌표 (0, 0.2r))가 (15, 15)
    ham = P["head"] == "ham"
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        cheek = P["cheek"] * (1.0 + (0.07 if ham and k % 2 else 0.0))
        hd, mask, _ = draw(rig, head_parts(P, (0.0, 0.0), r, cheek=cheek))
        face(hd, rig, P, hc=(0.0, 0.0), r=r, mood="blink" if k == 8 else "open", mouth="y")
        row = [x for x, y in mask if y == 15]
        lx, rx = min(row), max(row)
        top = min(y for x, y in mask if x == 15)
        bot = max(y for x, y in mask if x == 15)
        tw = k % 6 in (2, 3)                         # 수염 끝이 파르르
        for x in range(1, lx):                       # 곧은 가로 · 세로 줄은 조준선(커서), 비스듬한 한 가닥씩은 수염(동물)
            f[x, 15] = sea.Cur(OUT)
        for x in range(rx + 1, 31):
            f[x, 15] = sea.Cur(OUT)
        for sg, x0 in ((-1, lx - 1), (1, rx + 1)):   # 위아래로 한 가닥씩 더 — 수염으로 읽히게
            for i in range(4):
                f[x0 + sg * i, 13 - (i // 2 if tw else (i + 1) // 2)] = OUT
                f[x0 + sg * i, 17 + (i // 2 if tw else (i + 1) // 2)] = OUT
        for y in range(1, top):
            f[15, y] = sea.Cur(OUT)
        for y in range(bot + 1, 31):
            f[15, y] = sea.Cur(OUT)
        f.update(hd)
        frames.append(finish(f))
    return frames, (15, 15)


# ── ibeam: I 꼴 갉기 막대 ─────────────────────────────────────────────────────
def stick_i():
    m = {(x, y) for y in range(2, 30) for x in (14, 15, 16)}
    m |= {(x, y) for y in (2, 3, 4, 27, 28, 29) for x in range(11, 20)}
    f = {}
    solid(f, m, lambda p: BARK if p[1] in (3, 28) and p[0] not in (14, 15, 16) else WOOD, BARK_D)
    f[15, 10] = f[15, 21] = BARK      # 나뭇결
    return {p: sea.Cur(c) for p, c in f.items()}, m   # I 막대는 커서, 튀는 나뭇조각은 동물


def ibeam(P):
    """세로로 세운 I 꼴 갉기 막대를 두 앞발로 붙잡고 갉작갉작 — 갉을 때 몸을 막대 쪽으로 기울이고 나뭇조각이 튄다.
    막대를 맨 나중에 찍어 I 가 늘 끝까지 보인다. 핫스팟은 막대 가운데"""
    stick, sm = stick_i()
    K = 0.7
    feet = (23.2, 29.4)                                   # 기우는 축(발 밑)
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        gnaw = k % 4 in (1, 2)
        a = -9.0 if gnaw else -2.0
        t = math.radians(a)
        ham = P["head"] == "ham"
        fy = 9.6 if ham else 10.0                       # 발 밑(제 좌표)
        rig = Rig(feet[0] + fy * math.sin(t) * K, feet[1] - fy * math.cos(t) * K, a, K)
        hands = [rig.local(17.6, 14.6), rig.local(17.6, 18.0)]
        arms = [("arm0", bar((-3.0, -0.6), hands[0], 1.4), P["fur"], False),
                ("arm1", bar((-3.0, 2.0), hands[1], 1.4), P["fur"], False)]
        g, _ = pet_sit(P, rig, mood="squeeze" if gnaw else ("blink" if k == 7 else "open"), hand=hands, turn=-1.8,
                       extra=(), wag=1.0 * math.sin(ph), mouth="teeth" if gnaw else "y",
                       body=None)
        ga, _, _ = draw(rig, arms)
        for p, c in ga.items():
            g.setdefault(p, c)
        f.update({p: c for p, c in g.items() if p not in sm})
        f.update(stick)
        if gnaw:   # 나뭇조각
            for j, (dx, dy) in enumerate(((2, -3), (4, -5), (1, -6))):
                if (j + k) % 2 == 0:
                    f[17 + dx, 11 + dy] = WOOD
        frames.append(finish(clip(f)))
    return frames, (15, 15)


# ── move: 햄스터 볼 ───────────────────────────────────────────────────────────
def chevron(f, cx, cy, dx, dy, col):
    """(dx, dy) 쪽을 가리키는 화살촉, 꼭짓점이 (cx, cy) — bird.chevron 과 같음(대각은 두 칸 굵기 ㄱ 자)"""
    col = sea.Cur(col)   # 화살촉은 커서 — 쓸 때 sea.mark 가 파랑 맨 끝 비트로 동물과 가른다
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


def move(P):
    """투명한 햄스터 볼 속에서 옆모습으로 다다닥 달린다 — 볼의 숨구멍이 굴러가고, 네 방향 화살촉이 바깥으로 두근.
    몸 가운데가 핫스팟"""
    cx, cy, R = 15.5, 15.5, 8.8
    ball = disc(cx, cy, R)
    ring = {p for p in ball if math.hypot(p[0] + 0.5 - cx, p[1] + 0.5 - cy) > R - 1.3}
    parts0, *_ = side_parts(P, s=1)
    rig0 = fit_rig(parts0, (cx - 6.4, cy - 5.6, cx + 6.4, cy + 6.6), 0.62)
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        bob = 0.4 * abs(math.sin(2 * ph))
        rig = Rig(rig0.ox, rig0.oy - bob, 0.0, rig0.k)
        parts, eye, nose, cheek = side_parts(P, s=1, step=2.0 * math.sin(2 * ph))
        g, _, _ = draw(rig, parts)
        side_face(g, rig, P, eye, nose, cheek, s=1, mood="open", whisk=False)
        for p in ball - ring:
            f[p] = BALL
        f.update({p: c for p, c in g.items() if p not in ring})
        for p in ring:
            f[p] = BALL_RING
        a0 = -2 * math.pi * k / N / 2                       # 숨구멍 — 달리는 쪽(오른쪽)으로 굴러간다
        for i in range(6):
            a = a0 + 2 * math.pi * i / 6
            f[math.floor(cx + math.cos(a) * (R - 0.7)), math.floor(cy + math.sin(a) * (R - 0.7))] = BALL_D
        for p in ((10, 10), (11, 9), (12, 9)):              # 반짝
            if p not in g:
                f[p] = hx("ffffffd0")
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            o = 1 if k % 6 < 3 else 0
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy, CHEV if o else CHEV_L)
        frames.append(finish(clip(f)))
    return frames, center_hot(frames)


# ── 기지개: ns · we · nwse · nesw ─────────────────────────────────────────────
AXES = {"ns": 0.0, "we": -90.0, "nwse": -45.0, "nesw": 45.0}


def stretch(P, ang):
    """쭉 기지개 — 몸을 ang 축으로 눕혀(등이 보이게) 앞발은 머리 쪽 끝, 뒷발 · 꼬리는 반대 끝으로 뻗어
    늘었다 줄었다. 머리는 몸과 같이 돌리지 않고 똑바로 세워 머리 쪽 끝에 얹는다(돌린 얼굴은 칸 위에서 뭉갠다).
    늘 때 눈 질끈 · 하품. 축 양끝 화살촉이 두근. 몸 가운데가 핫스팟"""
    t = math.radians(ang)
    ex, ey = math.sin(t), -math.cos(t)          # 머리 쪽(화면)
    dx, dy = round(ex), round(ey)
    Rc = 14 if dx == 0 or dy == 0 else 11   # 화살촉이 발끝에 붙으면 몸 테두리로 읽혀 한 칸 띄운다
    K, KH, rh = 0.68, 0.6, 6.6   # 작게 그리면 막대로 읽혀서 몸을 굵게
    ham = P["head"] == "ham"
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        s = 0.5 + 0.5 * math.sin(ph)            # 0 줄음 → 1 쭉
        reach = 1.6 * s
        Lb = 5.0 + 1.2 * s
        rig = Rig(15.5 - ex * 1.0, 15.5 - ey * 1.0, ang, K)
        parts = []
        for sg in (-1, 1):                    # 앞발 — 머리 양옆으로 쭉
            tip = (sg * 3.4, -Lb - 3.8 - reach)
            parts.append((f"fp{sg}", ell(tip[0], tip[1], 1.7, 1.9), P["paw"], True))
            parts.append((f"fa{sg}", bar((sg * 3.0, -Lb + 2.4), tip, 1.6), P["fur"], False))
        for sg in (-1, 1):                    # 뒷발
            tip = (sg * 3.2, Lb + 2.6 + reach)
            parts.append((f"hp{sg}", ell(tip[0], tip[1], 1.4, 2.0), P["paw"], True))
            parts.append((f"ha{sg}", bar((sg * 3.0, Lb - 2.0), tip, 1.6), P["fur"], False))
        tl = None
        if P["tail"]:
            tl = tail_part(P, [(0.0, Lb - 1.0), (0.4, Lb + 2.8 + reach), (-0.6 + 0.8 * math.sin(2 * ph), Lb + 5.2 + reach)],
                           scale=0.9)
        parts.append(body_part(P, (0.0, 0.0), 6.0 if ham else 5.4, Lb, back=True))
        if tl:
            parts.append(tl)
        g, _, _ = draw(rig, parts)
        f.update(g)
        hx_, hy_ = rig.world(0.0, -Lb + 1.6)
        hc = home(P)
        hrig = Rig(hx_ - hc[0] * KH, hy_ - hc[1] * KH - (1.2 if ham else 0.6) * KH, 0.0, KH)
        hd, _, _ = draw(hrig, head_parts(P, hc, rh))
        f.update(hd)
        face(f, hrig, P, hc=hc, r=rh, mood="squeeze" if s > 0.6 else "open", mouth="o" if s > 0.6 else "y")
        o = 1 if s > 0.6 else 0
        for sg in (-1, 1):
            chevron(f, 15 + sg * dx * (Rc + o), 15 + sg * dy * (Rc + o), sg * dx, sg * dy, CHEV if o else CHEV_L)
        frames.append(finish(clip(f)))
    return frames, center_hot(frames)


# ── pen: 연필을 두 앞발로 쥐고 사각사각 ──────────────────────────────────────
PEN_TIP, PEN_BACK = (1.5, 29.5), (27.6, 14.6)   # 연필심 · 지우개 끝(화면)


def pen(P):
    """제 몸보다 긴 연필을 씨앗 쥐듯 두 앞발로 가슴 앞에 꼭 쥐고 쓰는 모습 — 연필과 동물이 연필심을 축으로 까딱.
    연필심(왼쪽 아래 끝)이 핫스팟"""
    base = Rig(21.0, 19.6, 0.0, 0.74)
    L = math.hypot(PEN_BACK[0] - PEN_TIP[0], PEN_BACK[1] - PEN_TIP[1])
    ux, uy = (PEN_BACK[0] - PEN_TIP[0]) / L, (PEN_BACK[1] - PEN_TIP[1]) / L
    cone = (PEN_TIP[0] + ux * 3.6, PEN_TIP[1] + uy * 3.6)
    lt, lc, lb = base.local(*PEN_TIP), base.local(*cone), base.local(*PEN_BACK)
    rr = 1.5 / base.k

    def pcol(a, b):
        x, y = base.world(a, b)
        tt = (x - PEN_TIP[0]) * ux + (y - PEN_TIP[1]) * uy
        sd = -(x - PEN_TIP[0]) * uy + (y - PEN_TIP[1]) * ux
        if tt < 1.4:
            return LEAD
        if tt < 3.8:
            return WOOD
        if tt > L - 1.8:
            return ERASER
        if tt > L - 3.4:
            return FERRULE
        return PENCIL_D if sd > 0.5 else PENCIL
    pencil = ("pencil", any_of(bar(lt, lc, 0.45 / base.k, rr), bar(lc, lb, rr)), pcol, True)
    grips = []
    for sg in (-1, 1):   # 앞발 — 연필 위, 가슴 양옆
        x = base.ox + sg * 2.6 * base.k
        y = PEN_TIP[1] + (x - PEN_TIP[0]) / ux * uy
        grips.append(base.local(x, y))
    frames = []
    for k, ph in enumerate(phases()):
        d = math.radians(3.0 * math.sin(2 * ph))
        ox, oy = base.ox - PEN_TIP[0], base.oy - PEN_TIP[1]
        rig = Rig(PEN_TIP[0] + ox * math.cos(d) - oy * math.sin(d), PEN_TIP[1] + ox * math.sin(d) + oy * math.cos(d),
                  math.degrees(d), base.k)
        extra = paws(P, grips, r=1.6) + [pencil]
        g, _ = pet_sit(P, rig, mood="blink" if k == 4 else "open", hand=[], extra=extra, wag=1.0 * math.sin(ph),
                       mouth="y", cur=("pencil",))   # 연필은 테까지 커서
        g[math.floor(PEN_TIP[0]), math.floor(PEN_TIP[1])] = sea.Cur(LEAD)
        frames.append(finish(clip(g)))
    return frames, (math.floor(PEN_TIP[0]), math.floor(PEN_TIP[1]))


SCENES = {"busy": busy, "help": help_, "person": person, "pin": pin, "hand": hand, "cross": cross, "ibeam": ibeam,
          "move": move, "ns": lambda P: stretch(P, AXES["ns"]), "we": lambda P: stretch(P, AXES["we"]),
          "nwse": lambda P: stretch(P, AXES["nwse"]), "nesw": lambda P: stretch(P, AXES["nesw"]), "pen": pen, "up": up}


def center_hot(frames):
    """모든 장에서 불투명한 칸 중 판 가운데에 가장 가까운 것 (bird.center_hot 과 같음)"""
    common = set.intersection(*[{p for p, c in f.items() if c[3] == 255} for f in frames])
    return min(common, key=lambda p: (math.hypot(p[0] - 15.5, p[1] - 15.5), p))


def check(rid, frames, hot):
    bad = 0
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
            bad += 1
        if any(not (0 <= x <= 31 and 0 <= y <= 31) for x, y in f):
            print(f"  ! {rid} {i}장: 판 밖으로 나간 칸이 있음")
            bad += 1
        if any(c[3] in (0xfe, 0xfd, 0xfc) for c in f.values()):
            print(f"  ! {rid} {i}장: 예약 알파(fe/fd/fc)")
            bad += 1
        if hot == (1, 1) and any(c[3] == 255 and (p[0] < 1 or p[1] < 1) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 발끝보다 왼쪽·위로 나온 칸이 있음")
            bad += 1
    return bad


def sid(pid: str) -> str:
    """구성표 이름 앞부분 — 푸딩햄스터는 말랑 간식 푸딩(puddinganim)과 겹쳐서 길게"""
    return "puddinghamster" if pid == "pudding" else pid


def main():
    # python3 pet.py [마리…] [--cells 칸,칸] — 칸을 주면 그 칸만 다시 그린다 (bird.py 와 같음)
    args = sys.argv[1:]
    only = None
    if "--cells" in args:
        i = args.index("--cells")
        only = set(args[i + 1].split(","))
        args = args[:i] + args[i + 2:]
    ids = args or list(PETS)
    bad = 0
    for pid in ids:
        P = PETS[pid]
        ink(OUT, HI, P["rim"])
        d = ART / f"{sid(pid)}anim"
        d.mkdir(parents=True, exist_ok=True)
        cells = {"arrow": lambda: arrow(pid), "wait": WAIT[pid], "no": NO[pid]}
        cells.update({c: (lambda fn=fn: fn(P)) for c, fn in SCENES.items()})
        for cell, fn in cells.items():
            if only is not None and cell not in only:
                continue
            frames, hot = fn()
            frames = sea.mark(frames)   # 칸마다(커서가 없는 칸도) — 안 거친 홀수 칸은 커서로 읽힌다
            assert len(frames) == N, (pid, cell, len(frames))
            bad += check(f"{pid}/{cell}", frames, hot)
            (d / f"{cell}.txt").write_text(SH.to_text(frames, hot, RATE), encoding="utf-8")
        print(f"{pid}: 끝")
    print(f"경고 {bad}개")

if __name__ == "__main__":
    main()

# SPDX-License-Identifier: Apache-2.0
"""너구리(raccoonanim) 구성표 그림 `art/raccoonanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/raccoon.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

숲속 친구들 · 애니 묶음의 한 마리(미국너구리 꼴). 칸마다 너구리가 그 칸 뜻에 맞는 짓을 따로 한다(`SCENE`).
치비 비율 — 회색 큰 머리 · 눈가의 까만 가면(바깥으로 처진 눈물방울 둘 — 가운데로 이으면 도둑 복면, 동그라미면
안경으로 읽혀서 콧등에서 떼고 끝을 처지게 했다) · 가면 위 흰 눈썹 · 흰 주둥이와 뺨 털 · 2×2 콩알 눈에 흰 반짝 ·
분홍 볼터치 · 흰 테 두른 둥근 귀 · 까만 작은 손. 실루엣의 주인공은 까만 고리 줄무늬 꼬리다.
너구리 짓은 앞발 쓰기다 — 열매(산딸기)를 물에 비비 씻고, 손바닥으로 만져 보고, 들어 올린다. 소품은 묶음 공통의
풀 · 나뭇잎 · 잔가지에 산딸기 · 물방울 · 물웅덩이를 더한다.

  arrow   왼쪽 위로 살금살금 걷는 너구리(옆으로 누운 몸에 똑바로 선 앞얼굴) — 왼쪽 귀 끝이 핫스팟.
          앞발 · 뒷발이 번갈아 딛고 줄무늬 꼬리가 살랑, 발치에 물방울 발자국이 남는다
  busy    작은 화살표 너구리 + 오른쪽 아래 큰 산딸기 둘레를 물방울 여덟이 차례로 빛나며 돈다
  cross   앞모습 얼굴. 가는 조준선 네 가닥, 코가 핫스팟. 두 앞발로 볼을 동글동글 비비며 세수한다
  hand    떠다니는 물방울을 손바닥 편 앞발로 톡 — 닿으면 물방울이 터져 튄다. 펼친 손 끝이 핫스팟.
          다른 앞발엔 산딸기
  help    작은 화살표 너구리 + 물방울로 찍은 물음표(점은 산딸기). 물방울이 차례로 반짝인다
  ibeam   위 나뭇가지에 두 앞발로 매달려 대롱대롱 — 가지가 I 의 위 가로획, 물웅덩이가 아래 가로획,
          매달린 몸과 늘어진 줄무늬 꼬리가 세로획. 핫스팟은 몸 가운데
  move    물웅덩이에 서서 두 앞발로 첨벙첨벙 — 물방울이 튀고 네 방향 풀잎 화살촉
  nesw · ns · nwse · we   그 축으로 몸을 쭉 늘여 기지개 켜는 옆모습 너구리 — 앞으로 뻗은 앞발과 곧게 편 줄무늬
          꼬리가 양 끝(머리는 몸보다 크게 그린 앞얼굴)이고 그 바깥에 풀잎 화살촉. 다 늘이면 눈을 감는다
  no      빨간 금지 표지 안에서 두 손바닥을 앞으로 내밀어(멈춰!) 눈을 질끈 감고 도리도리
  pen     산딸기 즙을 찍은 잔가지를 두 앞발로 쥐고 쓴다 — 즙 묻은 붉은 끝(왼쪽 아래)이 핫스팟. 끝을 축으로 까딱
  person  작은 화살표 너구리 + 사람 아이콘처럼 우뚝 선 앞모습 너구리가 한 팔을 들어 손을 흔든다
  pin     작은 화살표 너구리 + 크림 동그라미 속에 산딸기가 든 빨간 지도 핀이 물웅덩이에 통통 — 꽂힐 때 물결이 퍼진다
  up      발돋움하고 짧은 두 팔로 큰 산딸기를 머리 바로 위에 번쩍(만세) — 산딸기 꼭대기 잎이 핫스팟. 꼬리를 흔든다
  wait    물웅덩이 앞에 앉아 산딸기를 두 앞발로 물에 비비 씻다가 들어 올려 반짝 — 다시 씻는다. 핫스팟은
          장마다 불투명한 칸 중 가운데에 가장 가까운 칸(`steady`)

몸은 부위(타원 · 굵기가 변하는 막대 · 굵기가 변하는 사슬)를 너구리 제 좌표에 놓고 화면으로 돌려 찍는다(`Rig`, `draw`).
앞모습(`front`) · 옆모습(`side`) 두 벌이다. 옆모습도 머리만은 늘 똑바로 선 앞얼굴이다 — 옆얼굴은 32칸에서 가면이
까만 덩이, 흰 뺨이 뼈로 읽혀 해골이 됐다. 그리개는 gen/fox.py 와 같은 꼴이지만 다른 생성기를 import 하지 않으려고
여기 따로 둔다(그쪽을 고치면 이 그림이 조용히 바뀌지 않게). 숲 소품(풀 · 나뭇잎) 색과 꼴은 같은 묶음 생성기와 맞춘다.
빌드가 부르지 않고 손으로 돌린다 · 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import BUB, N, QMARK, SIGN, SIGN_D, WAKE, disc, finish, hx, ink, inside, phases, raster, solid, write

SID = "raccoonanim"

OUT, EYE, NOSE = hx("2c2830ff"), hx("141016ff"), hx("1c181eff")         # 테두리 · 눈 · 코
FUR, FUR_D, FUR_L = hx("b9b5bbff"), hx("8e8894ff"), hx("dcd8dbff")      # 몸 · 그늘 · 배
WHITE, WHITE_D = hx("f8f5f0ff"), hx("e2ddd6ff")                          # 눈썹 · 주둥이 · 뺨 털
MASK, RING, PAW = hx("38323eff"), hx("5a5462ff"), hx("4e4856ff")         # 가면 · 꼬리 고리 · 손발
EAR_IN, BLUSH, HI = hx("6e6876ff"), hx("f49a9aff"), hx("fffaf0ff")       # 귓속 · 볼터치 · 반짝
ink(OUT, HI, hx("f6e9d2c7"))
LEAF, LEAF_D, LEAF_L = hx("5aa04aff"), hx("3f7a35ff"), hx("86c46aff")   # 풀 · 나뭇잎
BARK, BARK_D = hx("8a6a4cff"), hx("5e4630ff")                           # 잔가지
BERRY, BERRY_D, BERRY_L = hx("e0405aff"), hx("9c2238ff"), hx("ff8a9cff")   # 산딸기
WATER, WATER_L = WAKE[1], WAKE[0]                                       # 물 · 물 반짝
CREAM = hx("fbf4eaff")


# ── 그리개: 너구리 제 좌표 (a, b) → 화면 ─────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도, a 축이 화면에서 가리키는 쪽, 90 이 아래) · 배율 k · 뒤집기 fl.
    b 축은 a 축을 시계 방향으로 90도 돌린 쪽(ang=0 이면 a 가 오른쪽, b 가 아래). fl 이면 b 축을 반대로"""

    def __init__(self, ox: float, oy: float, ang: float = 0.0, k: float = 1.0, fl: bool = False):
        t = math.radians(ang)
        self.ox, self.oy, self.c, self.s, self.k = ox, oy, math.cos(t), math.sin(t), k
        self.f = -1.0 if fl else 1.0

    def world(self, a: float, b: float) -> tuple:
        b *= self.f
        return self.ox + (a * self.c - b * self.s) * self.k, self.oy + (a * self.s + b * self.c) * self.k

    def local(self, x: float, y: float) -> tuple:
        dx, dy = (x - self.ox) / self.k, (y - self.oy) / self.k
        return dx * self.c + dy * self.s, (-dx * self.s + dy * self.c) * self.f

    def cell(self, a: float, b: float) -> tuple:
        x, y = self.world(a, b)
        return math.floor(x), math.floor(y)


def ell(ca, cb, ra, rb, rot=0.0):
    """타원 (rot 은 라디안)"""
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


def any_of(*hs):
    return lambda a, b: any(h(a, b) for h in hs)


def chain_dt(pts, rs):
    """굵기가 변하는 사슬(꼬리)의 (a, b) → (가운데 줄에서 떨어진 정도(1 이면 겉), 밑동에서 끝까지 0–1)"""
    segs = list(zip(pts, pts[1:], rs, rs[1:]))
    n = len(segs)

    def d(a, b):
        best, bt = 9.0, 0.0
        for i, ((x0, y0), (x1, y1), r0, r1) in enumerate(segs):
            ex, ey = x1 - x0, y1 - y0
            t = max(0.0, min(1.0, ((a - x0) * ex + (b - y0) * ey) / (ex * ex + ey * ey or 1e-9)))
            v = math.hypot(a - x0 - ex * t, b - y0 - ey * t) / (r0 + (r1 - r0) * t)
            if v < best:
                best, bt = v, (i + t) / n
        return best, bt
    return d


def wiggle(pts, amp: float, ph: float):
    """사슬을 밑동(첫 점) 쪽부터 휘게 한다 — 끝으로 갈수록 크게, 조금 늦게 따라온다(살랑)"""
    out = [pts[0]]
    n = len(pts) - 1
    tot = 0.0
    for i in range(1, len(pts)):
        tot += amp * (i / n) * math.sin(ph - 0.5 * i)
        x, y = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
        c, s = math.cos(tot), math.sin(tot)
        px, py = out[-1]
        out.append((px + x * c - y * s, py + x * s + y * c))
    return out


def tail_part(pts, rs, rings: int = 4, name="tail", lined=False):
    """너구리 꼬리: 회색 털과 까만 고리가 번갈아 들고 끝은 까맣다. 고리는 사슬을 따라 재므로 꼬리가 휘어도
    가로로 감긴다 — 고리가 실루엣의 첫째 표식이라(회색 꼬리만으로는 다람쥐 · 고양이) 줄이 칸에서 안 뭉개지게
    고리 수를 꼬리 길이에 맞춘다"""
    d = chain_dt(pts, rs)

    def col(a, b):
        v, t = d(a, b)
        if t > 0.86:
            return RING
        if int(t / 0.86 * (2 * rings - 1)) % 2:
            return RING
        return FUR_L if v > 0.78 else FUR
    return (name, lambda a, b: d(a, b)[0] <= 1.0, col, lined)


def draw(rig: Rig, parts: list) -> tuple[dict, set, dict]:
    """parts: [(이름, 맞음(a, b), 색(a, b) 또는 색, 테두리)] — 앞의 것이 위에 그려진다.
    칸을 4×4 로 찍어 반 넘게 덮이면 칠하고, 가장 많이 덮은 부위의 색을 준다. 바깥 테두리와,
    테두리=True 인 부위가 뒤 부위와 닿는 자리에 선을 긋는다. → ({칸: 색}, 칸 집합, {칸: 부위})"""
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


def dot(f: dict, rig: Rig, a: float, b: float, c: tuple) -> None:
    f[rig.cell(a, b)] = c


def eye(f: dict, rig: Rig, a: float, b: float, mood: str = "smile") -> None:
    """콩알 눈. 크면(k ≥ 0.75) 2×2 에 흰 반짝 한 칸, 작으면 반짝 한 칸 + 눈 한 칸(가면 위라 눈만 찍으면
    안 보인다). blink 는 가면보다 밝은 가로 한 줄(가면 위에 까만 줄은 묻힌다)"""
    x, y = rig.cell(a, b)
    big = rig.k >= 0.75
    if mood == "blink":
        f[x, y + 1] = WHITE_D
        if big:
            f[x + 1, y + 1] = WHITE_D
    elif big:
        for q in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
            f[q] = EYE
        f[x, y] = HI
    else:
        f[x, y] = HI
        f[x, y + 1] = EYE


def shut_pair(f: dict, rig: Rig, a: float, b: float, sg: int) -> None:
    """질끈 감은 눈 — 왼눈은 >, 오른눈은 <. 가면 위라 밝게 긋는다"""
    x, y = rig.cell(a, b)
    if sg < 0:
        f[x, y] = f[x + 1, y + 1] = f[x, y + 2] = WHITE_D
    else:
        f[x + 1, y] = f[x, y + 1] = f[x + 1, y + 2] = WHITE_D


# ── 소품: 숲(같은 묶음과 같은 색 · 꼴) · 산딸기 · 물 ─────────────────────────────────
LEAF_G = ["...##",
          ".#lL#",
          "#lLl#",
          "#Ll#.",
          ".##.."]
BERRY_G = [".gGg.",      # 산딸기(5×6): 꼭지 잎 · 알갱이 점
           "#gGg#",
           "#rRr#",
           "#RrR#",
           "#rRr#",
           ".###."]
DROP_G = ["..#..",       # 물방울(5×6): 위가 뾰족, 왼쪽 아래 반짝
          ".#w#.",
          "#wwW#",
          "#hwW#",
          "#wwW#",
          ".###."]
DROP_S = [".#.",         # 작은 물방울(3×4)
          "#w#",
          "#h#",
          ".#."]


def glyph_at(f: dict, rows: list, pal: dict, x0: int, y0: int, alpha: int = 255) -> None:
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != ".":
                r, g, b, _ = pal[ch]
                f[x0 + i, y0 + j] = (r, g, b, alpha)


def leaf_glyph(f: dict, x0: int, y0: int, alpha: int = 255) -> None:
    """칸 단위 작은 나뭇잎(5×5) — 오른쪽 위로 끝이 뾰족"""
    glyph_at(f, LEAF_G, {"#": LEAF_D, "l": LEAF, "L": LEAF_L}, x0, y0, alpha)


def berry_glyph(f: dict, x0: int, y0: int, alpha: int = 255) -> None:
    """칸 단위 산딸기(5×6)"""
    glyph_at(f, BERRY_G, {"#": BERRY_D, "r": BERRY, "R": BERRY_L, "g": LEAF, "G": LEAF_D}, x0, y0, alpha)


def drop_glyph(f: dict, x0: int, y0: int, alpha: int = 255, small: bool = False) -> None:
    """칸 단위 물방울 — 테는 sea 의 물방울 테(BUB)"""
    glyph_at(f, DROP_S if small else DROP_G, {"#": BUB, "w": WATER, "W": WATER_L, "h": HI}, x0, y0, alpha)


def berry_part(ca: float, cb: float, r: float = 1.6, name: str = "berry") -> tuple:
    """너구리가 쥔 산딸기(몸 좌표) — 알갱이가 엇갈려 점점이 밝고 꼭지는 잎"""
    def col(a, b):
        if b < cb - r * 0.55:
            return LEAF
        return BERRY_L if (math.floor((a - ca) * 1.4) + math.floor((b - cb) * 1.4)) % 2 == 0 else BERRY
    return (name, ell(ca, cb, r * 0.9, r), col, True)


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int) -> None:
    """(dx, dy) 쪽을 가리키는 풀잎 화살촉. 꼭짓점이 (cx, cy). 바깥 줄은 밝은 잎, 안 줄은 짙은 잎"""
    px, py = -dy, dx
    for i in range(4):
        for s in (-1, 1):
            for w in (0, 1):
                f[cx - dx * (i + w) + s * px * i, cy - dy * (i + w) + s * py * i] = LEAF if w == 0 else LEAF_D


def grass(f: dict, x0: int, x1: int, y: int, k: int = 0, front: bool = False) -> None:
    """풀 덤불: 밑줄 짙은 풀 위로 들쭉날쭉 풀잎이 바람에 까딱인다. front 면 이미 그린 것 위에 덮는다"""
    put = f.__setitem__ if front else f.setdefault
    for x in range(x0, x1 + 1):
        put((x, y), LEAF_D)
        h = (1, 2, 1, 3, 2, 1, 2)[(x * 3) % 7]
        lean = 1 if (x + k // 3) % 4 == 0 and h > 1 else 0
        for j in range(1, h):
            put((x + (lean if j == h - 1 else 0), y - j), LEAF if j < h - 1 else LEAF_L)


def puddle(f: dict, cx: float, cy: float, w: float, h: float, k: int = 0, ripple: float | None = None,
           front: bool = False) -> None:
    """납작한 물웅덩이: 물 테(BUB) · 옅은 물 · 퍼지는 물결 고리 하나. ripple 은 고리 크기(0–1, 기본은 박자대로).
    front 면 이미 그린 것(발) 위에 덮는다"""
    m = {(x, y) for y in range(math.floor(cy - h) - 1, math.ceil(cy + h) + 1)
         for x in range(math.floor(cx - w) - 1, math.ceil(cx + w) + 1)
         if ((x + 0.5 - cx) / w) ** 2 + ((y + 0.5 - cy) / h) ** 2 <= 1}
    rr = (k % 6) / 6 if ripple is None else ripple
    put = f.__setitem__ if front else f.setdefault
    for p in m:
        x, y = p
        d = math.hypot((x + 0.5 - cx) / w, (y + 0.5 - cy) / h)
        edge_ = any(q not in m for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
        if edge_:
            put(p, BUB)
        elif 0.2 < rr and abs(d - rr) < 0.16:
            put(p, WATER_L)
        else:
            put(p, WATER)


def splash(f: dict, x0: float, y0: float, k: int, n: int = 4, spread: float = 5.0, height: float = 5.0) -> None:
    """물 튀김: 작은 물방울 n 개가 x0 에서 좌우로 포물선을 그리며 떨어진다"""
    for j in range(n):
        t = (k / N + j / n) % 1
        sd = -1 if j % 2 else 1
        x = x0 + sd * spread * t * (0.6 + 0.4 * (j // 2))
        y = y0 - height * 4 * t * (1 - t)
        f[math.floor(x), math.floor(y)] = WATER_L if t < 0.5 else WATER
        f.setdefault((math.floor(x), math.floor(y) + 1), BUB)


# ── 앞모습 너구리: a 가로(+오른쪽), b 세로(+아래), 원점은 머리 가운데 ─────────────────────
def head_parts(turn: float = 0.0) -> list:
    """앞모습 머리: 회색 머리 · 양옆으로 뻗친 흰 뺨 털 · 흰 주둥이 · 흰 눈썹 · 바깥으로 처진 가면 둘 · 흰 테 귀.
    turn 은 고개를 돌린 만큼(칸)"""
    cheeks = any_of(bar((-4.0, 1.0), (-7.0, 2.6), 1.8, 0.5), bar((4.0, 1.0), (7.0, 2.6), 1.8, 0.5))
    muzzle = ell(turn, 2.4, 2.3, 1.7)
    brows = any_of(ell(-2.5 + turn, -3.0, 1.5, 0.65), ell(2.5 + turn, -3.0, 1.5, 0.65))
    masks = any_of(ell(-2.7 + turn, -0.9, 2.0, 1.3, -0.38), ell(2.7 + turn, -0.9, 2.0, 1.3, 0.38))

    def skin(a, b):
        if muzzle(a, b) or brows(a, b):
            return WHITE
        if masks(a, b):
            return MASK
        if cheeks(a, b) and abs(a) > 4.4:
            return WHITE
        return FUR
    head = any_of(ell(0, -0.6, 5.6, 4.5), cheeks, muzzle)
    ears = [ell(sg * 4.1, -4.4, 1.9, 2.0, sg * 0.4) for sg in (-1, 1)]
    inner = [ell(sg * 4.1, -4.1, 0.95, 1.1, sg * 0.4) for sg in (-1, 1)]

    def ear_col(a, b):
        return EAR_IN if any(h(a, b) for h in inner) else WHITE
    return [("head", head, skin, True), ("ears", any_of(*ears), ear_col, False)]


def face(f: dict, rig: Rig, mood: str = "smile", turn: float = 0.0, yawn: bool = False) -> None:
    """가면 속 눈 · 까만 코 · ω 입 · 볼터치"""
    for sg in (-1, 1):
        if mood == "shut":
            shut_pair(f, rig, sg * 2.6 + turn - 0.5, -1.8, sg)
        else:
            eye(f, rig, sg * 2.5 + turn - 0.5, -1.4, mood)
        dot(f, rig, sg * 4.6 + turn * 0.5, 1.6, BLUSH)
    dot(f, rig, turn, 1.4, NOSE)                      # 코
    if rig.k >= 0.75:
        dot(f, rig, turn - 1.0, 1.4, NOSE)
        if yawn:
            for q in ((-1.0, 3.0), (0.0, 3.0), (-1.0, 3.8), (0.0, 3.8)):
                dot(f, rig, turn + q[0], q[1], BERRY_D)
        else:
            dot(f, rig, turn - 1.2, 3.0, NOSE)        # ω 입
            dot(f, rig, turn + 0.6, 3.0, NOSE)


TAIL_F = [(3.4, 11.2), (6.8, 11.8), (9.4, 10.0), (10.6, 6.8), (10.8, 3.2)]     # 앉은 몸 오른쪽으로 세운 꼬리
TAIL_FR = [1.6, 2.6, 2.9, 2.9, 2.4]


def palm(pa: float, pb: float, up: float = -1.0) -> list:
    """손바닥을 편 까만 손 — 손바닥 덩이 + 위(up 쪽)로 손가락 셋"""
    hits = [ell(pa, pb, 1.7, 1.4)]
    for da in (-1.1, 0.0, 1.1):
        hits.append(bar((pa + da * 0.8, pb), (pa + da * 1.1, pb + up * (2.2 if da == 0 else 1.9)), 0.6))
    return hits


def front(rig: Rig, ph: float = 0.0, mood: str = "smile", paws=((-2.0, 9.2), (2.0, 9.2)), tail=None,
          tail_r=None, tail_amp: float = 0.10, elbows=(None, None), turn: float = 0.0, mid=(), feet: bool = True,
          behind: bool = False, palms=(False, False), tail_front: bool = False, tiptoe: float = 0.0,
          yawn: bool = False) -> tuple[dict, set]:
    """앞모습 앉은 너구리 한 장. paws 는 앞발 끝 둘, elbows 는 팔꿈치(팔을 머리 위로 들 때), palms 면 그 손을
    손바닥 편 꼴로(손가락이 팔꿈치 반대쪽으로), mid 는 앞발 뒤 · 몸 앞에 놓을 부위(산딸기 · 잔가지),
    behind 면 든 팔을 머리 뒤로 그린다(매달리기 · 만세), tiptoe 면 발을 그만큼 아래로 내려 발돋움한다"""
    tp = wiggle(tail or TAIL_F, tail_amp, ph)
    arms, pads = [], []
    for i, (sg, (pa, pb)) in enumerate(zip((-1, 1), paws)):
        sh = (sg * 2.4, 6.4)
        if elbows[i]:
            arms += [bar(sh, elbows[i], 1.9, 1.8), bar(elbows[i], (pa, pb), 1.8, 1.5)]
            ux, uy = pa - elbows[i][0], pb - elbows[i][1]
        else:
            arms.append(bar(sh, (pa, pb), 1.3, 1.0))
            ux, uy = pa - sh[0], pb - sh[1]
        if palms[i]:
            ln = math.hypot(ux, uy) or 1.0
            up = 1.0 if uy / ln > 0 else -1.0
            pads += palm(pa, pb, up)
        else:
            pads.append(ell(pa, pb, 1.2, 1.05))
    t = tail_part(tp, tail_r or TAIL_FR, lined=True)
    belly = ell(0, 9.8, 2.6, 2.8)

    def body(a, b):
        return FUR_L if belly(a, b) else FUR
    # 팔은 몸과 같은 털이라 안쪽 선을 안 긋는다 — 그으면 몸 위에 짙은 줄이 엉켜 벌레 다리로 읽힌다
    hand = [("paw", any_of(*pads), PAW, False), ("arm", any_of(*arms), FUR, False)]
    parts = [t] if tail_front else []
    if not behind:
        parts += hand
    parts += list(mid)
    parts += head_parts(turn) + (hand if behind else [])
    if feet:
        parts.append(("foot", any_of(ell(-2.9, 12.8 + tiptoe, 1.9, 1.1), ell(2.9, 12.8 + tiptoe, 1.9, 1.1),
                                     bar((-2.6, 10.6), (-2.9, 12.6 + tiptoe), 1.4),
                                     bar((2.6, 10.6), (2.9, 12.6 + tiptoe), 1.4)),
                      lambda a, b: PAW if b > 11.9 + tiptoe else FUR, False))
    parts.append(("body", any_of(ell(0, 9.4, 4.4, 3.9), ell(0, 6.2, 3.2, 2.0)), body, True))
    if not tail_front:
        parts.append(t)
    out, mask, _ = draw(rig, parts)
    face(out, rig, mood, turn, yawn)
    return out, mask


# ── 옆모습 너구리: 코끝이 원점, a 는 꼬리 쪽(+), b 는 배 쪽(+) ───────────────────────────
TAIL_SIDE = [(17.2, 0.4), (20.0, -0.8), (22.8, -1.8), (25.6, -2.2), (28.0, -1.6)]   # 뒤로 살짝 든 꼬리
TAIL_SIDER = [1.8, 2.8, 3.1, 3.1, 2.4]


def side(rig: Rig, ph: float = 0.0, mood: str = "smile", tail=None, tail_r=None, tail_amp: float = 0.12,
         legs=None, arm_behind: bool = False, yawn: bool = False, head_k: float = 1.0) -> tuple[dict, set, dict]:
    """옆으로 누운 몸에 앞모습 머리를 얹은 너구리 한 장 — 몸 · 다리 · 꼬리는 rig 를 따라 돌고, 머리는 늘 똑바로
    선 앞모습(`head_parts`)을 쓴다. 옆얼굴은 32칸에서 가면이 까만 덩이, 흰 뺨이 뼈로 읽혀 해골이 됐다 —
    가면 둘 · 흰 눈썹 · 볼터치는 앞얼굴이어야 읽힌다. 고개는 코 쪽으로 조금 돌린다.
    legs 를 주면 (앞발 끝, 뒷발 끝)을 그 자리에 둔다. arm_behind 는 예전 이름 그대로 둔다(앞발을 머리 쪽으로
    뻗을 때 — 앞모습 머리가 늘 위에 그려지므로 그리는 차례는 같다). head_k 는 몸보다 머리를 그만큼 키운다(치비). 몸 안쪽 선은 긋지 않는다 — 다리 · 허벅지마다
    그으면 회색 몸이 줄투성이가 돼 화살표로 눕혔을 때 까만 막대로 읽힌다. → (칸: 색, 칸 집합, 이름 있는 자리)"""
    tp = wiggle(tail or TAIL_SIDE, tail_amp, ph)
    sw = math.sin(ph)
    fore, hind = legs or ((8.4 + 1.0 * sw, 6.6), (16.6 - 1.0 * sw, 6.4))

    def body(a, b):
        return FUR_L if b > 2.6 else FUR
    parts = [("paw", ell(*fore, 1.2, 1.05), PAW, False), ("arm", bar((10.0, 2.6), fore, 1.4, 1.1), FUR, False),
             ("foot", any_of(bar((15.8, 3.0), hind, 1.4, 1.05), ell(*hind, 1.2, 1.05)),
              lambda a, b: PAW if math.hypot(a - hind[0], b - hind[1]) < 1.7 else FUR, False),
             ("body", any_of(ell(12.6, 1.2, 5.2, 3.8), ell(16.0, 2.0, 2.8, 2.8)), body, False),
             tail_part(tp, tail_r or TAIL_SIDER, rings=3, lined=True)]
    out, mask, _ = draw(rig, parts)
    turn = -1.0 * rig.c * rig.f if abs(rig.c) > 0.3 else 0.0
    hr = Rig(*rig.world(*SIDE_HEAD), 0.0, rig.k * head_k)
    ho, hm, _ = draw(hr, head_parts(turn))
    out.update(ho)
    face(out, hr, "blink" if yawn else mood, turn, yawn)
    return out, mask | hm, {"nose": hr.cell(turn, 1.4)}


SIDE_HEAD = (5.6, -1.0)    # 옆 몸 좌표에서 앞모습 머리 가운데


ARROW = Rig(1.5, 3.0, 45.0, 1.2)    # 화살표 너구리: 왼쪽 귀 끝이 (1, 1) 언저리 — 핫스팟은 `corner`
ARROW_S = Rig(2.1, 3.2, 45.0, 0.5)   # 작은 화살표 너구리 (busy · help · person · pin)


def arrow_rac(ph: float, small: bool = False) -> dict:
    k = round(N * ph / (2 * math.pi))
    return side(ARROW_S if small else ARROW, ph, "blink" if k == 7 else "smile", head_k=1.3 if small else 1.0)[0]


def crop(f: dict) -> dict:
    return {p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    """왼쪽 위로 살금살금 — 발이 번갈아 딛고 꼬리가 살랑, 발치에 물방울 발자국이 하나씩 남았다 사라진다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for j in range(3):                       # 지나온 자리(오른쪽 아래)의 물 발자국 — 오래된 것일수록 흐리다
            age = (k / N + j / 3) % 1
            x, y = 13 + 4 * j - round(2 * age), 23 + 3 * j - round(2 * age)
            al = round(255 * (1 - age))
            if al > 40:
                for q in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
                    f[q] = (*WATER[:3], al)
        f.update(arrow_rac(ph))
        frames.append(finish(crop(f)))
    return frames


WAIT = Rig(15.5, 11.0, 0.0, 0.84)


def wait() -> list[dict]:
    """물웅덩이에 앉아 산딸기를 비비 씻는다 — 0–5 · 10–11 두 앞발을 물낯에 담그고 번갈아 비빈다(물방울이 튄다),
    6–9 들어 올려 반짝 살펴본다. 웅덩이가 아랫몸을 가려 팔이 짧게 보인다. 꼬리가 살랑인다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        wash = k < 6 or k > 9
        if wash:
            rub = math.sin(2 * ph)
            pb = 12.2
            paws = ((-1.7 + 0.6 * rub, pb + 0.3 * rub), (1.7 + 0.6 * rub, pb - 0.3 * rub))
            bc = (0.6 * rub, pb - 0.4)
        else:
            pb = 8.4 - (0.4 if k in (7, 8) else 0.0)
            paws = ((-1.8, pb), (1.8, pb))
            bc = (0.0, pb - 0.5)
        o, _ = front(WAIT, ph, "blink" if k == 3 else "smile", paws=paws, mid=(berry_part(*bc, 1.7),),
                     tail_amp=0.16)
        f.update(o)
        puddle(f, 15.5, 24.6, 10.5, 3.0, k, None if wash else 0.0, front=True)
        if wash:
            splash(f, 15.5, 21.0, k, n=4, spread=6.0, height=4.0)
        else:
            x, y = WAIT.cell(bc[0] + 1.6, bc[1] - 1.8)
            if k in (7, 8):                           # 깨끗해진 산딸기에 반짝
                for q in ((x + 1, y - 1), (x + 2, y - 2), (x + 3, y - 1), (x + 2, y)):
                    f[q] = HI
            f[x - 3, y + 3 + (k - 6)] = WATER_L       # 산딸기에서 떨어지는 물
        frames.append(finish(crop(f)))
    return frames


def hand() -> list[dict]:
    """떠다니는 물방울을 손바닥 편 앞발로 톡 — 닿으면 터져 사방으로 튄다. 다른 앞발엔 산딸기.
    손가락 끝은 그대로(핫스팟) 두고 팔꿈치만 밀어 올린다"""
    frames = []
    rig = Rig(17.0, 16.4, 0.0, 0.88)
    tip = (-7.4, -8.6)                           # 손바닥 가운데
    for k, ph in enumerate(phases()):
        f = {}
        poke = k in (4, 5)
        # 든 팔은 머리 뒤로 — 앞으로 그리면 같은 털빛이라 뺨과 한 덩이가 된다
        o, _ = front(rig, ph, "blink" if poke else "smile", paws=(tip, (2.0, 9.0)),
                     elbows=((-7.0 if poke else -7.8, -1.6 if poke else -0.6), None), palms=(True, False),
                     mid=(berry_part(2.0, 8.0, 1.6),), tail_amp=0.14, behind=True)
        f.update(o)
        x, y = rig.cell(tip[0], tip[1] - 1.9)
        if k < 4:                                # 물방울이 위에서 손끝으로 내려온다
            drop_glyph(f, x + 2 - (3 - k), y - 6 + (3 - k) * 0 - (3 - k), 255)
        elif poke:                               # 톡 — 터진다
            for q in ((x - 3, y + 1), (x + 3, y + 1), (x - 2, y - 1), (x + 2, y - 1), (x + 4, y + 3), (x - 4, y + 3)):
                f.setdefault(q, WATER_L if k == 4 else WATER)
        elif k >= 9:                             # 새 물방울이 멀리서 둥실
            drop_glyph(f, x + 6 + (11 - k), y - 1 - (11 - k), 0xa0, small=True)
        frames.append(finish(crop(f)))
    return frames


def cross() -> list[dict]:
    """앞모습 얼굴 — 가는 조준선 네 가닥, 두 앞발로 볼을 동글동글 비비며 세수. 코가 핫스팟"""
    frames = []
    rig = Rig(15.5, 13.6, 0.0, 1.0)   # 코 칸이 (15, 15)
    for k, ph in enumerate(phases()):
        f = {}
        for x in list(range(1, 6)) + list(range(26, 31)):
            f[x, 15] = OUT
        for y in list(range(1, 4)) + list(range(22, 31)):
            f[15, y] = OUT
        parts = []    # 팔 없이 손만 — 팔까지 그리면 얼굴 밑으로 다리가 넷 달린 벌레가 된다
        for sg in (-1, 1):
            pa, pb = sg * 5.2 + 0.6 * math.cos(ph + sg), 2.8 + 0.6 * math.sin(ph + sg)
            parts.append(("paw" + str(sg), ell(pa, pb, 1.4, 1.2), PAW, True))
        out, _, _ = draw(rig, parts + head_parts())
        f.update(out)
        face(f, rig, "blink" if k in (2, 8) else "smile")
        frames.append(finish(f))
    return frames


def no() -> list[dict]:
    """빨간 금지 표지 안에서 두 손바닥을 앞으로 내밀어(멈춰!) 눈을 질끈 감고 도리도리"""
    frames = []
    rig = Rig(15.2, 11.4, 0.0, 0.8)
    for k, ph in enumerate(phases()):
        f = {}
        R = 13.5
        ring = {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
        slash = set()
        for t in range(-90, 91):
            x, y = 15.5 + t / 100 * (R - 1.5) * 0.7071, 15.5 + t / 100 * (R - 1.5) * 0.7071
            slash |= disc(x, y, 1.3)
        solid(f, ring | slash, SIGN, SIGN_D)
        turn = 1.2 * math.sin(2 * ph)
        push = 0.4 * math.sin(4 * ph)
        o, _ = front(rig, ph, "shut", turn=turn, paws=((-6.6, 4.8 - push), (6.6, 4.8 - push)),
                     elbows=((-5.2, 8.8), (5.2, 8.8)), palms=(True, True), tail_amp=0.05, tail=TAIL_F)
        f.update({p: c for p, c in o.items() if p[1] <= 30})
        frames.append(finish(f))
    return frames


def move() -> list[dict]:
    """물웅덩이에 서서 두 앞발로 첨벙첨벙 — 물방울이 튀고 네 방향 풀잎 화살촉이 바깥으로 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy)
        s = math.sin(2 * ph)
        rig = Rig(14.6, 11.6 - 0.6 * abs(s), 0.0, 0.56)
        paws = ((-4.6, 11.0 - 2.6 * max(s, 0)), (4.6, 11.0 - 2.6 * max(-s, 0)))
        oo, _ = front(rig, ph, "blink" if k == 4 else "smile", paws=paws, elbows=((-4.4, 7.4), (4.4, 7.4)),
                      tail_amp=0.2)
        f.update(oo)
        puddle(f, 15.0, 19.6, 6.4, 1.8, k, front=True)
        for sg in (-1, 1):
            if sg * s < -0.3:                    # 내리친 손 쪽에 물이 튄다
                for q in ((15 + sg * 6, 16), (15 + sg * 8, 17), (15 + sg * 7, 14)):
                    f[q] = WATER_L
        frames.append(finish(f))
    return frames


TAIL_LONG = [(16.4, -0.4), (19.6, -0.8), (22.8, -1.0), (26.0, -0.9), (29.0, -0.6)]
TAIL_LONGR = [1.6, 2.6, 2.8, 2.8, 2.2]


def stretch(ang: float, fl: bool = False) -> list[dict]:
    """ang 축으로 몸을 쭉 늘여 기지개 — 앞으로 뻗은 앞발과 곧게 편 꼬리가 양 끝, 다 늘이면 눈 감고 하품.
    그 바깥 풀잎 화살촉이 늘인 쪽으로 두근댄다. 몸 가운데가 판 가운데"""
    frames = []
    t = math.radians(ang)
    ex, ey = math.cos(t), math.sin(t)            # 코 → 꼬리 쪽 (화면)
    dx, dy = round(ex), round(ey)
    R = 14 if dx == 0 or dy == 0 else 11
    K = 0.62 if dx == 0 or dy == 0 else 0.56
    MID = 14.0                                   # 몸 가운데 (a)
    for k, ph in enumerate(phases()):
        f = {}
        e = 0.5 * (1 + math.sin(ph))             # 늘인 정도 0–1
        for sg in (-1, 1):
            o = 1 if e > 0.75 else 0
            chevron(f, 15 + sg * dx * (R + o), 15 + sg * dy * (R + o), sg * dx, sg * dy)
        rig = Rig(15.5 - MID * K * ex, 15.5 - MID * K * ey, ang, K, fl)
        fore = (2.6 - 1.6 * e, 5.4)                # 앞발은 턱 밑으로 — 머리 앞으로 내밀면 까만 뿔로 읽힌다
        hind = (20.0 + 2.6 * e, 5.0 - 0.4 * e)
        o_, _, _ = side(rig, ph, "smile", TAIL_LONG, TAIL_LONGR, 0.06 * (1 - e), legs=(fore, hind),
                        arm_behind=True, yawn=e > 0.85, head_k=1.25)
        f.update(o_)
        frames.append(finish(crop(f)))
    return frames


def we():
    return stretch(0.0)


def ns():
    return stretch(90.0)


def nwse():
    return stretch(45.0)


def nesw():
    return stretch(135.0, fl=True)


def up() -> list[dict]:
    """발돋움하고 두 앞발로 딴 큰 산딸기를 머리 바로 위로 번쩍(만세) — 산딸기 꼭대기 잎이 핫스팟.
    팔을 길게 뻗어 들면 가는 막대 끝에 열매가 달려 막대사탕, 머리 위 빈 고리는 손잡이로 읽혀서, 짧은 팔로
    머리 바로 위에서 양옆을 쥔다. 꼬리를 흔들고 발밑 풀이 까딱인다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        lift = 0.5 * (1 + math.sin(ph))          # 발돋움 — 산딸기는 그 자리, 몸이 들썩
        rig = Rig(15.5, 17.0 - 0.6 * lift, 0.0, 0.8)
        bc = (0.0, (8.2 - rig.oy) / rig.k)       # 산딸기 가운데는 화면 y≈8 에 그대로
        o, _ = front(rig, ph, "smile" if k != 5 else "blink", paws=((-3.4, bc[1] + 0.6), (3.4, bc[1] + 0.6)),
                     elbows=((-6.8, -1.4), (6.8, -1.4)), mid=(berry_part(*bc, 3.4),), behind=True,
                     tail_amp=0.3, tiptoe=0.8 * lift)
        f.update(o)
        grass(f, 6, 25, 30, k, front=True)
        frames.append(finish(crop(f)))
    return frames


def ibeam() -> list[dict]:
    """위 나뭇가지에 두 앞발로 매달려 대롱대롱 — 가지가 I 의 위 가로획, 물웅덩이가 아래 가로획.
    손을 축으로 몸이 흔들리고 늘어진 꼬리가 따라 흔들린다"""
    frames = []
    piv = (15.5, 3.0)
    for k, ph in enumerate(phases()):
        f = {}
        for x in range(8, 24):                       # 나뭇가지
            f[x, 2] = BARK_D
            f[x, 1] = BARK if x % 5 else BARK_D
        leaf_glyph(f, 21, -1)
        leaf_glyph(f, 6, 0)
        sw = 5.0 * math.sin(ph)
        t = math.radians(sw)
        ox, oy = 0.0, 10.2                           # 손 → 원점(머리 가운데) 화면 거리 (흔들기 전)
        rig = Rig(piv[0] + ox * math.cos(t) - oy * math.sin(t), piv[1] + ox * math.sin(t) + oy * math.cos(t),
                  sw, 0.72)
        hb = -10.2 / 0.72
        tail = [(1.6, 11.6), (2.8, 14.0), (3.2, 16.6), (2.6, 19.0)]
        o, _ = front(rig, ph, "smile" if k != 7 else "blink", paws=((-2.4, hb + 0.6), (2.4, hb + 0.6)),
                     elbows=((-3.4, -6.0), (3.4, -6.0)), behind=True, tail=tail, tail_r=[1.6, 2.4, 2.4, 1.8],
                     tail_amp=0.25, tiptoe=0.8)
        f.update({p: c for p, c in o.items() if p[1] <= 27})
        puddle(f, 15.5, 29.0, 8.5, 1.6, k, front=True)
        frames.append(finish(crop(f)))
    return frames


TIP_, BACK = (1.5, 29.5), (27.0, 13.4)   # 잔가지 끝 · 꽁무니(화면)


def pen() -> list[dict]:
    """산딸기 즙을 찍은 잔가지를 두 앞발로 쥐고 쓴다 — 붉은 끝이 핫스팟. 끝을 축으로 살짝 까딱인다"""
    frames = []
    base = Rig(20.6, 12.6, 0.0, 0.62)
    L = math.hypot(BACK[0] - TIP_[0], BACK[1] - TIP_[1])
    ux, uy = (BACK[0] - TIP_[0]) / L, (BACK[1] - TIP_[1]) / L
    lt, lb = base.local(*TIP_), base.local(*BACK)
    k_ = base.k

    def tcol(a, b):
        x, y = base.world(a, b)
        t = (x - TIP_[0]) * ux + (y - TIP_[1]) * uy
        s = -(x - TIP_[0]) * uy + (y - TIP_[1]) * ux
        if t < 2.0:
            return BERRY_D if t < 1.0 else BERRY
        if t < 3.4:
            return BERRY
        return BARK if s < 0.3 else BARK_D
    twig = ("twig", bar(lt, lb, 0.55 / k_, 1.15 / k_), tcol, True)
    paws = (base.local(TIP_[0] + ux * L * 0.62, TIP_[1] + uy * L * 0.62 - 0.4),
            base.local(TIP_[0] + ux * L * 0.80, TIP_[1] + uy * L * 0.80 - 0.4))
    for k, ph in enumerate(phases()):
        d = math.radians(3.0 * math.sin(2 * ph))
        ox, oy = base.ox - TIP_[0], base.oy - TIP_[1]
        rig = Rig(TIP_[0] + ox * math.cos(d) - oy * math.sin(d), TIP_[1] + ox * math.sin(d) + oy * math.cos(d),
                  math.degrees(d), base.k)
        f, _ = front(rig, ph, "blink" if k == 4 else "smile", paws=paws, mid=(twig,), tail_amp=0.12)
        bx, by = math.floor(BACK[0] + ux * 0.6 * math.cos(d)), math.floor(BACK[1] + uy * 0.6)
        leaf_glyph(f, bx - 1, by - 4)                 # 꽁무니에 남은 잎 하나
        f[math.floor(TIP_[0]), math.floor(TIP_[1])] = BERRY_D
        frames.append(finish(crop(f)))
    return frames


def busy() -> list[dict]:
    """작은 화살표 너구리 + 오른쪽 아래 큰 산딸기 — 둘레를 물방울 여덟이 차례로 빛나며 돈다"""
    frames = []
    cx, cy = 21.5, 21.0
    for k, ph in enumerate(phases()):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = math.floor(cx + 6.6 * math.cos(a) - 1.0), math.floor(cy + 6.6 * math.sin(a) - 1.5)
            lag = (head - i) % 8
            al = 255 if lag < 1 else 0xc0 if lag < 2 else 0x60
            drop_glyph(f, x, y, al, small=True)
        bob = 0.4 * math.sin(ph)
        b, _, _ = draw(Rig(cx, cy + bob, 0.0, 1.0), [berry_part(0.0, 0.0, 3.0)])
        f.update(b)
        f.update(arrow_rac(ph, small=True))
        frames.append(finish(crop(f)))
    return frames


def help_() -> list[dict]:
    """작은 화살표 너구리 + 물방울로 찍은 물음표(점은 산딸기) — 물방울이 차례로 하나씩 반짝인다"""
    frames = []
    cells = [(16.4 + 2.4 * i, 10.0 + 2.4 * j) for j, row in enumerate(QMARK[:-1]) for i, ch in enumerate(row)
             if ch == "#"]
    for k, ph in enumerate(phases()):
        f = {}
        m = set()
        lit = set()
        for i, (x, y) in enumerate(cells):
            d = (k * (len(cells) + 1) / N - i) % (len(cells) + 1)
            dd = disc(x, y, 1.6 + (0.3 if d < 1.5 else 0.0))
            m |= dd
            if d < 1.5:
                lit.add((math.floor(x - 0.6), math.floor(y - 0.6)))
        solid(f, m, WATER, BUB)
        for p in lit:
            f[p] = HI
        bob = 1 if (k * (len(cells) + 1) / N - len(cells)) % (len(cells) + 1) < 1.5 else 0
        berry_glyph(f, 19, 24 - bob)
        f.update(arrow_rac(ph, small=True))
        frames.append(finish(crop(f)))
    return frames


def person() -> list[dict]:
    """작은 화살표 너구리 + 사람 아이콘처럼 우뚝 선 앞모습 너구리가 손바닥을 펴고 손을 흔든다(안녕!)"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        w = math.sin(2 * ph)
        rig = Rig(22.0, 18.2, 0.0, 0.62)
        o, _ = front(rig, ph, "blink" if k == 6 else "smile", paws=((-10.6 - 1.2 * w, -4.2), (2.0, 9.2)),
                     elbows=((-8.6, 3.2), None), palms=(True, False), tail_amp=0.2, behind=True)
        f.update(o)
        f.update(arrow_rac(ph, small=True))
        frames.append(finish(crop(f)))
    return frames


def pin() -> list[dict]:
    """작은 화살표 너구리 + 크림 동그라미 속에 산딸기가 든 빨간 지도 핀이 물웅덩이에 통통 — 꽂힐 때 물결이 퍼진다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 21.5, 9.5 + dy
        rip = None if dy == 0 else 0.0
        puddle(f, 21.5, 27.0, 8.0, 2.4, k, ripple=((k + 2) % 6) / 6 if dy > -2 else 0.0)
        solid(f, disc(cx, cy, 5.4) | raster([(cx - 3.8, cy + 2.8), (cx + 3.8, cy + 2.8), (cx, cy + 15.0)]),
              SIGN, SIGN_D)
        for p in disc(cx, cy - 0.2, 3.4):
            f[p] = CREAM
        berry_glyph(f, math.floor(cx) - 2, math.floor(cy) - 3)
        _ = rip
        f.update(arrow_rac(ph, small=True))
        frames.append(finish(crop(f)))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def top_cell(fr):
    """장마다 불투명한 칸 중 맨 위 칸(같으면 왼쪽) — 몇 장에만 뜨는 물방울은 빼고 잡힌다"""
    common = set.intersection(*({p for p, c in f.items() if c[3] == 255} for f in fr))
    return min(common, key=lambda p: (p[1], p[0]))


def corner(fr):
    """장마다 불투명한 칸 중 왼쪽 위 끝(x + y 가 가장 작은 칸) — 화살표 너구리의 왼쪽 귀 끝. 머리는 장마다
    그 자리라 다리 · 꼬리가 움직여도 같은 칸이 잡힌다"""
    common = set.intersection(*({p for p, c in f.items() if c[3] == 255} for f in fr))
    return min(common, key=lambda p: (p[0] + p[1], p[1]))


def steady(fr):
    """장마다 불투명한 칸 중 판 가운데(15, 15)에 가장 가까운 칸 — 움직이는 너구리라도 찍는 점이 늘 보이게"""
    common = set.intersection(*({p for p, c in f.items() if c[3] == 255} for f in fr))
    return min(common, key=lambda p: (math.hypot(p[0] - 15, p[1] - 15), p))


def hand_hot(fr):
    """펼친 손의 가운데 손가락 끝 — 손바닥 위로 장마다 불투명한 맨 위 칸(물방울은 장마다 달라 빠진다)"""
    return top_cell(fr)


HOT = {"arrow": corner, "busy": corner, "help": corner, "person": corner, "pin": corner,
       "wait": steady, "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (15, 15),
       "pen": (math.floor(TIP_[0]), math.floor(TIP_[1])), "hand": hand_hot, "up": top_cell}


def check(rid: str, frames: list[dict], hot: tuple) -> None:
    """핫스팟이 장마다 불투명한 칸 위에 있는지"""
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
        if hot == (1, 1) and any(c[3] == 255 and (p[0] < 1 or p[1] < 1) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 코끝보다 왼쪽·위로 나온 칸이 있음")
        if any(c[3] == 255 and not (0 <= p[0] <= 31 and 0 <= p[1] <= 31) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 판(0–31) 밖으로 나간 칸이 있음")


def main() -> None:
    def job(r):
        def run():
            frames = SCENE[r]()
            hot = HOT[r](frames) if callable(HOT[r]) else HOT[r]
            check(r, frames, hot)
            print(f"  {r} 핫스팟 {hot}")
            return frames, hot
        return run
    write(SID, {r: job(r) for r in SCENE}, sys.argv[1:] or None)


if __name__ == "__main__":
    main()

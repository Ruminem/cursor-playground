# SPDX-License-Identifier: Apache-2.0
"""여우(foxanim) 구성표 그림 `art/foxanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/fox.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

숲속 친구들 · 애니 묶음(다람쥐 · 고슴도치 · 부엉이 · 토끼 · 여우)의 한 마리. 해양 애니의 물낯 · 물보라 자리를
풀 덤불 · 나뭇잎 · 도토리가 대신한다. 칸마다 여우가 그 칸 뜻에 맞는 짓을 따로 한다(`SCENE`).
치비 비율 — 붉은 기 도는 주황 큰 머리 · 흰 뺨 털과 주둥이 · 2×2 콩알 눈에 흰 반짝 · 분홍 볼터치 · 까만 코 ·
끝이 까만 큰 세모 귀 · 까만 양말 신은 다리 · 작은 몸. 실루엣의 주인공은 끝이 흰 복슬한 큰 꼬리다.
다람쥐(갈색 · 몸만 한 S 자로 되말린 꼬리 · 작은 귀)와는 뾰족한 주둥이 · 큰 세모 귀 · 곧게 뻗거나 몸을 감는
꼬리 · 흰 꼬리 끝 · 까만 다리로 가른다. 여우의 사냥 짓인 폴짝 뛰어들기(귀로 풀숲 속 소리를 듣고 높이 뛰어
머리부터 내리꽂는다)를 wait · arrow · up · 크기 조절 칸에 나눠 쓴다.

  arrow   왼쪽 위로 폴짝 뛰어드는 옆모습 여우 — 앞발을 모아 코 밑으로 뻗고 끝이 흰 꼬리가 뒤로 곧게 흐른다.
          코끝이 핫스팟. 꼬리 끝이 살랑, 뒷발이 차고 나간다
  busy    작은 화살표 여우 + 오른쪽 아래 꼬리를 감고 동그랗게 잠든 여우 둘레를 도토리 · 나뭇잎 여덟이 차례로 돈다
  cross   앞모습 얼굴. 가는 조준선 네 가닥, 코가 핫스팟. 큰 귀가 번갈아 기울어 듣는다
  hand    앞발 하나를 머리 위로 높이 들어 콕 — 든 까만 앞발 끝이 핫스팟. 꼬리를 세워 살랑인다
  help    작은 화살표 여우 + 주황 털 물음표(점은 나뭇잎). 글자 마디가 차례로 부푼다
  ibeam   위 덩굴의 포도송이에 두 앞발을 뻗어 발돋움하는 여우(여우와 신 포도) — 덩굴이 I 의 위 가로획,
          풀 덤불이 아래 가로획, 길게 늘인 몸이 세로획. 핫스팟은 몸 가운데
  move    풀 덤불 위에서 통통 뛰는 앞모습 작은 여우 + 네 방향 풀잎 화살촉
  nesw · ns · we · nwse   그 축으로 몸을 쭉 뻗고 폴짝 뛰어드는 옆모습 여우 — 모은 앞발과 곧게 편 꼬리가 양 끝이고
          그 바깥에 풀잎 화살촉. ns 는 머리부터 아래로 내리꽂는 사냥 자세다
  no      빨간 금지 표지 안에서 귀를 납작 젖히고 큰 꼬리로 발을 감싼 채 눈을 질끈 감고 도리도리
          (꼬리로 입가를 가리면 콧수염으로 읽혀서 발치로 내렸다)
  pen     붓을 끌어안은 여우 — 붓털이 여우 꼬리처럼 주황에 흰 끝이고 먹 묻은 끝(왼쪽 아래)이 핫스팟
  person  작은 화살표 여우 + 여우 얼굴에 셔츠 입은 사람 아이콘이 손을 흔든다(얼굴은 칸 글자판 `FACE_G`)
  pin     작은 화살표 여우 + 덤불에서 얼굴을 내민 여우 옆에 빨간 지도 핀이 통통 튀어 꽂힌다 — 핀이 뜨면
          고개를 들고 꽂힐 때 눈을 감는다
  up      풀숲에서 하늘로 곧게 뛰어오르는 옆모습 여우 — 위로 든 코끝이 핫스팟. 꼬리가 아래로 흐르고 풀잎이 튄다
  wait    풀 덤불 앞에 앉아 고개를 갸웃 귀 기울여 듣다가 웅크려 폴짝 — 머리부터 덤불에 꽂혀 엉덩이와 꼬리만
          살랑이다 다시 앉는다. 핫스팟은 장마다 불투명한 칸 중 가운데에 가장 가까운 칸(`steady`)

몸은 부위(타원 · 굵기가 변하는 막대 · 다각형 · 굵기가 변하는 사슬)를 여우 제 좌표에 놓고 화면으로 돌려 찍는다
(`Rig`, `draw`). 앞모습(`front`) · 옆모습(`side`) · 뒷모습(`rear`, 덤불에 꽂힌 엉덩이) · 잠든 모습(`curled`) 네 벌이다.
그리개는 gen/squirrel.py 와 같은 꼴이지만 다른 생성기를 import 하지 않으려고 여기 따로 둔다(그쪽을 고치면
이 그림이 조용히 바뀌지 않게). 숲 소품(풀 · 도토리 · 나뭇잎) 색과 꼴은 같은 묶음 생성기와 맞춘다.
빌드가 부르지 않고 손으로 돌린다 · 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, disc, finish, hx, ink, inside, phases, raster, solid, write

SID = "foxanim"

OUT, EYE, NOSE = hx("3a1a0cff"), hx("1e0f06ff"), hx("1e0f06ff")           # 테두리 · 눈 · 코
FUR, FUR_D, FUR_L = hx("e0703aff"), hx("b4522aff"), hx("f2945cff")       # 몸 · 그늘 · 밝은 털
WHITE, WHITE_D = hx("fbf4eaff"), hx("e8dccaff")                          # 뺨 · 가슴 · 꼬리 끝
SOCK, TIP = hx("4a2a1cff"), hx("2e1a10ff")                               # 까만 다리 · 귀 끝
EAR_IN, BLUSH, HI = hx("f6d2b8ff"), hx("f49a9aff"), hx("fffaf0ff")       # 귓속 · 볼터치 · 반짝
ink(OUT, HI, hx("f6e9d2c7"))
NUT, NUT_D, CAP, CAP_L = hx("a0662eff"), hx("7a4a1eff"), hx("6b4423ff"), hx("8a5c34ff")   # 도토리 · 깍정이
LEAF, LEAF_D, LEAF_L = hx("5aa04aff"), hx("3f7a35ff"), hx("86c46aff")   # 풀 · 나뭇잎
BARK, BARK_D = hx("8a6a4cff"), hx("5e4630ff")                           # 붓대 · 덩굴
GRAPE, GRAPE_D, GRAPE_L = hx("7a4a9eff"), hx("553270ff"), hx("a888c8ff")
FERRULE, INK_ = hx("c8a040ff"), hx("222226ff")                           # 붓 쇠테 · 먹
SHIRT, SHIRT_D = hx("4a8a9aff"), hx("33666fff")


# ── 그리개: 여우 제 좌표 (a, b) → 화면 ─────────────────────────────────────────
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


def poly(pts):
    pts = list(pts)
    return lambda a, b: inside(pts, a, b)


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


def tail_part(pts, rs, tip: float = 0.74, name="tail", lined=False):
    """여우 꼬리: 주황 · 겉 털끝은 밝게 · 끝 (1 - tip) 몫은 흰색. 흰 끝이 다람쥐 꼬리와 가르는 첫째 표식이다"""
    d = chain_dt(pts, rs)

    def col(a, b):
        v, t = d(a, b)
        if t > tip:
            return WHITE_D if v > 0.82 else WHITE
        return FUR_L if v > 0.8 else FUR
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
    """콩알 눈. 크면(k ≥ 0.75) 2×2 에 흰 반짝 한 칸, 작으면 세로 두 칸. blink 는 가로 한 줄"""
    x, y = rig.cell(a, b)
    big = rig.k >= 0.75
    if mood == "blink":
        f[x, y + 1] = EYE
        if big:
            f[x + 1, y + 1] = EYE
    elif big:
        for q in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
            f[q] = EYE
        f[x, y] = HI
    else:
        f[x, y] = EYE
        f[x, y + 1] = EYE


def shut_pair(f: dict, rig: Rig, a: float, b: float, sg: int) -> None:
    """질끈 감은 눈 — 왼눈은 >, 오른눈은 <"""
    x, y = rig.cell(a, b)
    if sg < 0:
        f[x, y] = f[x + 1, y + 1] = f[x, y + 2] = EYE
    else:
        f[x + 1, y] = f[x, y + 1] = f[x + 1, y + 2] = EYE


# ── 숲 소품 (같은 묶음과 같은 색 · 꼴) ─────────────────────────────────────────────
ACORN_G = ["..#..",
           ".#c#.",
           "#cCc#",
           "#nnN#",
           ".#n#.",
           "..#.."]
LEAF_G = ["...##",
          ".#lL#",
          "#lLl#",
          "#Ll#.",
          ".##.."]


def glyph_at(f: dict, rows: list, pal: dict, x0: int, y0: int, alpha: int = 255) -> None:
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != ".":
                r, g, b, _ = pal[ch]
                f[x0 + i, y0 + j] = (r, g, b, alpha)


def acorn_glyph(f: dict, x0: int, y0: int, alpha: int = 255) -> None:
    """칸 단위 작은 도토리(5×6)"""
    glyph_at(f, ACORN_G, {"#": OUT, "c": CAP, "C": CAP_L, "n": NUT, "N": NUT_D}, x0, y0, alpha)


def leaf_glyph(f: dict, x0: int, y0: int, alpha: int = 255) -> None:
    """칸 단위 작은 나뭇잎(5×5) — 오른쪽 위로 끝이 뾰족"""
    glyph_at(f, LEAF_G, {"#": LEAF_D, "l": LEAF, "L": LEAF_L}, x0, y0, alpha)


def leaf(f: dict, cx: float, cy: float, ang: float, ln: float = 2.4, col=LEAF) -> None:
    """작은 나뭇잎: 끝이 뾰족한 잎 몸 + 짙은 잎맥. ang 은 라디안(잎 끝이 가리키는 쪽)"""
    rig = Rig(cx, cy, math.degrees(ang), 1.0)
    out, _, _ = draw(rig, [("leaf", any_of(ell(0, 0, ln, ln * 0.5), bar((0, 0), (ln * 1.3, 0), ln * 0.35, 0.1)),
                            lambda a, b: col if b < 0 else LEAF_D, False)])
    for p, c in out.items():
        f.setdefault(p, c)


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


def bush(f: dict, cx: float, y: int, w: float, h: float, k: int = 0) -> None:
    """앞에 덮는 둥근 풀 덤불 — 들쭉날쭉 풀잎 윗머리. 이미 그린 것(여우) 위에 덮는다"""
    m = set()
    for x in range(math.floor(cx - w), math.ceil(cx + w) + 1):
        u = (x + 0.5 - cx) / w
        if abs(u) > 1:
            continue
        top = h * math.sqrt(1 - u * u) + (1.0 if (x * 3 + k // 3) % 4 == 0 else 0.0)
        for yy in range(math.floor(y - top), y + 1):
            m.add((x, yy))
    for p in m:
        x, yy = p
        f[p] = LEAF_D if (x, yy - 1) not in m else LEAF_L if (x * 5 + yy * 3) % 7 == 0 else LEAF


# ── 앞모습 여우: a 가로(+오른쪽), b 세로(+아래), 원점은 머리 가운데 ─────────────────────
def ear_poly(sg: int, tilt: float = 0.0, flat: float = 0.0, ln: float = 1.0):
    """큰 세모 귀. tilt 는 귀 기울임(도, + 면 바깥으로), flat 은 0–1 납작 젖힘, ln 은 길이 배.
    → (전체, 귓속, 끝) 맞음"""
    pv = (sg * 3.6, -3.4)
    t = math.radians(sg * (tilt + 62.0 * flat))
    c, s = math.cos(t), math.sin(t)

    def rot(p):
        dx, dy = p[0] - pv[0], p[1] - pv[1]
        return pv[0] + dx * c - dy * s, pv[1] + dx * s + dy * c
    tp = (sg * (3.6 + 1.6 * ln), -3.4 - 8.0 * ln)
    outer = [rot(p) for p in ((sg * 0.8, -3.6), tp, (sg * 6.4, -1.6))]
    tip = rot(tp)
    cx, cy = sum(p[0] for p in outer) / 3, sum(p[1] for p in outer) / 3
    inner = [(cx + (x - cx) * 0.5, cy + (y - cy) * 0.5 + 0.4) for x, y in outer]
    return poly(outer), poly(inner), lambda a, b: math.hypot(a - tip[0], b - tip[1]) < 2.6 * ln


def head_parts(turn: float = 0.0, tilt=(0.0, 0.0), flat: float = 0.0, ear_ln: float = 1.0) -> list:
    """앞모습 머리: 주황 머리 · 양옆으로 뻗친 흰 뺨 털 · 흰 주둥이 · 끝이 까만 큰 세모 귀.
    turn 은 고개를 돌린 만큼(칸), tilt 는 (왼귀, 오른귀) 기울임"""
    cheeks = any_of(ell(-3.6 + turn * 0.5, 1.4, 3.0, 2.4), ell(3.6 + turn * 0.5, 1.4, 3.0, 2.4),
                    bar((-4.2, 1.2), (-7.4, 2.6), 1.6, 0.4), bar((4.2, 1.2), (7.4, 2.6), 1.6, 0.4))
    muzzle = ell(turn, 2.5, 2.0, 1.6)

    def skin(a, b):
        if muzzle(a, b) or (cheeks(a, b) and b > 0.6 and abs(a - turn) > 1.2):
            return WHITE
        return FUR
    head = any_of(ell(0, -0.8, 5.4, 4.4), cheeks, muzzle)
    parts = [("head", head, skin, True)]
    hits = [ear_poly(sg, tl, flat, ear_ln) for sg, tl in zip((-1, 1), tilt)]

    def ear_col(a, b):
        for whole, inner, tip in hits:
            if whole(a, b):
                return TIP if tip(a, b) else EAR_IN if inner(a, b) else FUR
        return FUR
    parts.append(("ears", any_of(*(h[0] for h in hits)), ear_col, False))
    return parts


def face(f: dict, rig: Rig, mood: str = "smile", turn: float = 0.0) -> None:
    """눈 · 까만 코 · 입 · 볼터치"""
    for sg in (-1, 1):
        if mood == "shut":
            shut_pair(f, rig, sg * 2.5 + turn - 0.5, -1.6, sg)
        else:
            eye(f, rig, sg * 2.5 + turn - 0.5, -1.2, mood)
        dot(f, rig, sg * 4.0 + turn * 0.5, 1.4, BLUSH)
    dot(f, rig, turn, 2.0, NOSE)                      # 코
    if rig.k >= 0.75:
        dot(f, rig, turn - 1.0, 2.0, NOSE)
        dot(f, rig, turn - 0.6, 3.4, NOSE)            # ω 입
        dot(f, rig, turn + 0.6, 3.4, NOSE)


TAIL_WRAP = [(3.6, 9.6), (7.0, 11.4), (5.4, 14.0), (1.0, 14.6), (-3.4, 13.8), (-6.4, 12.2)]   # 앞발을 감는 꼬리
TAIL_WRAPR = [1.6, 2.8, 3.2, 3.0, 2.6, 1.6]
TAIL_UP = [(3.4, 10.4), (7.4, 10.6), (10.4, 7.8), (11.6, 3.8), (11.4, -0.6)]               # 옆으로 세운 꼬리
TAIL_UPR = [1.6, 2.8, 3.4, 3.2, 1.8]


def front(rig: Rig, ph: float = 0.0, mood: str = "smile", paws=((-1.6, 12.4), (1.6, 12.4)),
          tail=None, tail_r=None, tail_amp: float = 0.10, elbows=(None, None), turn: float = 0.0,
          tilt=(0.0, 0.0), flat: float = 0.0, mid=(), tail_front: bool = False, feet: bool = True,
          behind: bool = False) -> tuple[dict, set]:
    """앞모습 앉은 여우 한 장. paws 는 까만 앞다리 끝 둘, elbows 는 팔꿈치(다리를 머리 위로 들 때),
    mid 는 앞다리 뒤 · 몸 앞에 놓을 부위(붓), tail_front 면 꼬리를 몸 앞에 그린다(감아 덮기),
    behind 면 든 다리를 머리 뒤로 그린다(만세 — 앞으로 그리면 얼굴을 가린다)"""
    tp = wiggle(tail or TAIL_WRAP, tail_amp, ph)
    legs, raised, pads, rpads = [], [], [], []
    for i, (sg, (pa, pb)) in enumerate(zip((-1, 1), paws)):
        sh = (sg * 1.9, 6.6)
        if elbows[i]:   # 든 다리는 주황 털에 발만 까맣게 — 통째로 까마면 막대기로 읽힌다
            raised += [bar(sh, elbows[i], 1.4, 1.3), bar(elbows[i], (pa, pb), 1.3, 1.2)]
            rpads.append(ell(pa, pb, 1.4, 1.3))
        else:
            legs.append(bar(sh, (pa, pb), 1.25, 1.05))
            pads.append(ell(pa, pb, 1.2, 1.0))
    chest = ell(0, 7.2, 2.4, 3.2)

    def body(a, b):
        return WHITE if chest(a, b) else FUR
    t = tail_part(tp, tail_r or TAIL_WRAPR, lined=True)
    arm = [("rpaw", any_of(*rpads), SOCK, True), ("raised", any_of(*raised), FUR, True)] if raised else []
    parts = [t] if tail_front else []
    if pads:
        parts += [("paw", any_of(*pads), SOCK, True)]
    parts += list(mid)
    if legs:
        parts += [("leg", any_of(*legs), SOCK, True)]
    if not behind:
        parts += arm
    parts += head_parts(turn, tilt, flat) + (arm if behind else [])
    if feet:
        parts.append(("foot", any_of(ell(-3.2, 12.8, 2.0, 1.1), ell(3.2, 12.8, 2.0, 1.1)), SOCK, True))
    parts.append(("body", any_of(ell(0, 9.2, 4.2, 3.9), ell(0, 6.2, 3.2, 2.0)), body, True))
    if not tail_front:
        parts.append(t)
    out, mask, _ = draw(rig, parts)
    face(out, rig, mood, turn)
    return out, mask


# ── 옆모습 여우: 코끝이 원점, a 는 꼬리 쪽(+), b 는 배 쪽(+) ───────────────────────────
TAIL_SIDE = [(16.6, -0.6), (19.6, -1.8), (23.0, -2.6), (26.4, -2.4), (29.4, -1.4)]   # 뒤로 곧게 흐르는 꼬리
TAIL_SIDER = [1.6, 3.0, 3.8, 3.6, 2.0]


def side(rig: Rig, ph: float = 0.0, mood: str = "smile", tail=None, tail_r=None, tail_amp: float = 0.12,
         legs=None, reach: bool = False) -> tuple[dict, set, dict]:
    """옆모습 여우 한 장 — 폴짝 뛰는 자세가 기본이다(앞다리를 코 밑으로 모아 뻗고 뒷다리는 뒤로 찬다).
    legs 를 주면 (앞발 끝, 뒷발 끝) 을 그 자리에 둔다. → (칸: 색, 칸 집합, 이름 있는 자리)"""
    tp = wiggle(tail or TAIL_SIDE, tail_amp, ph)
    sw = math.sin(ph)
    fore, hind = legs or ((5.0 + 0.6 * sw, 5.6), (21.4 - 0.8 * sw, 4.6))

    def head(a, b):
        return WHITE if b > 1.0 - 0.2 * (a - 4.0) else FUR

    def body(a, b):
        return WHITE if b > 2.4 or (a < 11.4 and b > 0.4) else FUR
    ear_tip = (10.4, -9.6)    # 뒤로 조금 눕힌다 — 화살표로 눕혔을 때 귀 끝이 코끝보다 위로 안 나오게
    parts = [("nose", ell(0.5, 0.2, 0.8, 0.7), NOSE, False),
             ("paw", ell(*fore, 1.1, 1.0), SOCK, True),
             # 뻗어 든 앞다리(reach)는 주황 털 — 길게 까마면 막대기로 읽힌다
             ("arm", bar((10.8, 3.0), fore, 1.3 if reach else 1.2, 1.1 if reach else 1.0), FUR if reach else SOCK, True),
             ("snout", bar((0.8, 0.4), (3.8, 0.2), 1.0, 2.4), lambda a, b: WHITE if b > 0.6 else FUR, False),
             ("head", any_of(ell(6.6, -0.6, 4.6, 4.2), bar((7.4, 2.0), (11.0, 3.0), 1.6, 0.5)), head, True),
             ("ear", poly([(5.2, -3.4), ear_tip, (10.6, -2.6)]),
              lambda a, b: TIP if math.hypot(a - ear_tip[0], b - ear_tip[1]) < 2.6 else FUR, False),
             ("foot", bar((17.2, 3.0), hind, 1.1, 0.9), SOCK, True),
             ("thigh", ell(16.2, 1.0, 2.8, 2.8), FUR, True),
             ("body", any_of(ell(13.4, 1.0, 4.4, 3.2), ell(10.6, 1.2, 2.6, 3.2)), body, False),
             tail_part(tp, tail_r or TAIL_SIDER)]
    out, mask, _ = draw(rig, parts)
    eye(out, rig, 4.8, -1.8, mood)
    dot(out, rig, 7.0, 1.0, BLUSH)
    return out, mask, {"nose": rig.cell(0.1, 0.0)}


ARROW = Rig(1.4, 1.2, 45.0, 0.72)    # 화살표 여우: 코끝이 (1, 1)
ARROW_S = Rig(1.4, 1.2, 45.0, 0.5)   # 작은 화살표 여우 (busy · help · person · pin)


def arrow_fox(ph: float, small: bool = False) -> dict:
    k = round(N * ph / (2 * math.pi))
    return side(ARROW_S if small else ARROW, ph, "blink" if k == 7 else "smile")[0]


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    """왼쪽 위로 폴짝 뛰어든다 — 꼬리 끝이 살랑, 뒷발이 차고 나가며 발밑에 풀잎 하나가 튄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = arrow_fox(ph)
        t = k / N
        leaf_glyph(f, round(12.0 + 5.0 * t), round(21.0 - 3.0 * math.sin(math.pi * t)))
        frames.append(finish({p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}))
    return frames


def rear(rig: Rig, ph: float) -> dict:
    """덤불에 머리부터 꽂힌 여우의 뒷모습 — 엉덩이 · 위로 뻗은 까만 뒷다리 · 살랑이는 꼬리. 원점은 엉덩이"""
    tp = wiggle([(0.0, -1.6), (0.4, -5.0), (1.2, -8.4), (1.6, -11.6)], 0.5, ph)
    legs = any_of(bar((-2.4, -0.4), (-5.6, -4.6), 1.3, 1.1), bar((2.4, -0.4), (5.6, -4.6), 1.3, 1.1))
    paws = any_of(ell(-5.8, -4.8, 1.3, 1.2), ell(5.8, -4.8, 1.3, 1.2))
    parts = [tail_part(tp, [1.6, 2.6, 2.8, 1.6], 0.7, lined=True),
             ("paw", paws, SOCK, True), ("leg", legs, FUR, True),
             ("rump", any_of(ell(0.0, 1.6, 4.4, 3.6), ell(0.0, 5.0, 3.4, 3.0)), FUR, True)]
    return draw(rig, parts)[0]


WAIT = Rig(15.5, 13.0, 0.0, 0.84)


def wait() -> list[dict]:
    """풀 덤불 앞에 앉아 귀 기울여 듣다가 폴짝 — 0 앉음, 1–2 왼쪽으로 갸웃, 3–4 오른쪽으로 갸웃(귀를 기울인다),
    5 웅크림, 6–7 뛰어오름, 8–9 머리부터 덤불에 꽂혀 엉덩이 · 꼬리만 살랑, 10 덤불에서 쏙, 11 다시 앉음"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        if k in (8, 9):
            f.update(rear(Rig(15.5, 19.0 + (k - 8), 0.0, 0.84), ph * 2))
        else:
            dy, turn, tilt, paws, mood = 0.0, 0.0, (0.0, 0.0), ((-1.6, 12.4), (1.6, 12.4)), "smile"
            if k in (1, 2):
                turn, tilt = -1.0, (-16.0, 12.0)
            elif k in (3, 4):
                turn, tilt = 1.0, (12.0, -16.0)
            elif k == 5:
                dy, paws = 1.5, ((-1.8, 11.4), (1.8, 11.4))
            elif k in (6, 7):
                dy, paws, mood = (-4.0, -6.0)[k - 6], ((-2.6, 9.4), (2.6, 9.4)), "blink" if k == 7 else "smile"
            elif k == 10:
                dy, mood = 4.0, "blink"
            rig = Rig(WAIT.ox, WAIT.oy + dy, 0.0, WAIT.k)
            o, _ = front(rig, ph, mood, paws=paws, turn=turn, tilt=tilt, tail=TAIL_UP, tail_r=TAIL_UPR,
                         tail_amp=0.14, feet=k not in (6, 7))
            f.update(o)
        bush(f, 15.5, 30, 12.0, 4.0, k)
        if k in (8, 9):   # 덤불이 들썩
            for x in (8, 22):
                f[x, 24 - (k - 8)] = LEAF_L
        frames.append(finish({p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}))
    return frames


def hand() -> list[dict]:
    """앞발 하나를 머리 위로 높이 들어 콕 — 꼬리를 세워 살랑, 콕 할 때 발끝에 반짝. 든 앞발 끝이 핫스팟"""
    frames = []
    rig = Rig(16.0, 15.0, 0.0, 0.9)
    for k, ph in enumerate(phases()):
        f = {}
        poke = k in (0, 1, 6, 7)    # 발끝은 그대로 두고(핫스팟) 팔꿈치만 밀어 올려 콕
        o, _ = front(rig, ph, "blink" if k == 9 else "smile", paws=((-7.6, -13.6), (1.6, 12.4)),
                     elbows=((-6.4 if poke else -7.2, -3.0 if poke else -1.6), None), tail=TAIL_UP, tail_r=TAIL_UPR,
                     tail_amp=0.14, tilt=(10.0 if k % 6 < 3 else 0.0, 0.0))
        f.update(o)
        if poke:
            x, y = rig.cell(-7.6, -13.6)
            for q in ((x - 3, y + 2), (x + 3, y + 2), (x - 2, y), (x + 2, y)):   # 발끝보다 위로는 안 찍는다
                f.setdefault(q, HI if k % 2 == 0 else LEAF_L)
        frames.append(finish({p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}))
    return frames


def cross() -> list[dict]:
    """앞모습 얼굴 — 가는 조준선 네 가닥 · 큰 귀가 번갈아 기울어 듣는다. 코가 핫스팟"""
    frames = []
    rig = Rig(15.5, 13.0, 0.0, 1.0)   # 코 칸이 (15, 15)
    for k, ph in enumerate(phases()):
        f = {}
        for x in list(range(1, 7)) + list(range(25, 31)):
            f[x, 15] = OUT
        for y in list(range(1, 4)) + list(range(20, 31)):
            f[15, y] = OUT
        tl = 14.0 * math.sin(ph)
        out, _, _ = draw(rig, head_parts(tilt=(max(tl, 0.0), max(-tl, 0.0))))
        f.update(out)
        face(f, rig, "blink" if k == 8 else "smile")
        frames.append(finish(f))
    return frames


def no() -> list[dict]:
    """빨간 금지 표지 안에서 귀를 뒤로 젖히고 큰 꼬리로 몸을 감싼 채 눈을 질끈 감고 도리도리.
    꼬리를 입가까지 올리면 흰 꼬리 끝이 콧수염으로 읽혀서 앞발 위까지만 감는다"""
    frames = []
    rig = Rig(15.0, 11.6, 0.0, 0.8)
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
        o, _ = front(rig, ph, "shut", turn=turn, flat=0.3, tail_amp=0.05, tail_front=True)
        f.update({p: c for p, c in o.items() if p[1] <= 30})
        frames.append(finish(f))
    return frames


def chibi_move(rig: Rig, ph: float, mood: str) -> dict:
    o, _ = front(rig, ph, mood, tail=TAIL_UP, tail_r=TAIL_UPR, tail_amp=0.2)
    return o


def move() -> list[dict]:
    """풀 덤불 위에서 통통 — 네 방향 풀잎 화살촉이 바깥으로 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy)
        hop = abs(math.sin(ph))
        f.update(chibi_move(Rig(14.6, 14.2 - 1.4 * hop, 0.0, 0.56), ph, "blink" if k == 4 else "smile"))
        frames.append(finish(f))
    return frames


TAIL_LONG = [(16.6, -0.4), (19.8, -0.9), (23.2, -1.1), (26.6, -1.0), (29.6, -0.6)]
TAIL_LONGR = [1.6, 3.0, 3.6, 3.4, 2.0]


def stretch(ang: float, fl: bool = False) -> list[dict]:
    """ang 축으로 몸을 쭉 뻗고 폴짝 뛰어든다 — 모은 앞발과 곧게 편 꼬리가 양 끝, 그 바깥 풀잎 화살촉이 가는 쪽으로
    두근댄다. 몸 가운데가 판 가운데"""
    frames = []
    t = math.radians(ang)
    ex, ey = math.cos(t), math.sin(t)            # 코 → 꼬리 쪽 (화면)
    dx, dy = round(ex), round(ey)
    R = 13 if dx == 0 or dy == 0 else 10
    K = 0.6 if dx == 0 or dy == 0 else 0.5
    MID = 15.0                                   # 몸 가운데 (a)
    for k, ph in enumerate(phases()):
        f = {}
        d = 1.0 * math.sin(ph)                   # + 면 꼬리 쪽으로
        for sg in (-1, 1):
            o = 1 if sg * d > 0.3 else 0
            chevron(f, 15 + sg * dx * (R + o), 15 + sg * dy * (R + o), sg * dx, sg * dy)
        rig = Rig(15.5 - (MID - d) * K * ex, 15.5 - (MID - d) * K * ey, ang, K, fl)
        o_, _, _ = side(rig, ph, "blink" if k == 3 else "smile", TAIL_LONG, TAIL_LONGR, 0.08,
                        legs=((3.4, 6.2 - 0.6 * math.sin(ph)), (21.6, 5.8 + 0.6 * math.sin(ph))))
        f.update(o_)
        frames.append(finish(f))
    return frames


def we():
    return stretch(0.0)


def ns():
    return stretch(-90.0)


def nwse():
    return stretch(45.0)


def nesw():
    return stretch(135.0, fl=True)


def up() -> list[dict]:
    """풀숲에서 하늘로 곧게 뛰어오른다 — 코끝이 핫스팟. 꼬리가 아래로 흐르고 발밑 풀숲에서 풀잎이 튄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        rig = Rig(15.5, 1.2, 90.0, 0.78)   # 코가 위, 배가 왼쪽. 코끝(핫스팟)은 장마다 그 자리
        o, _, _ = side(rig, ph, "blink" if k == 5 else "smile", tail_amp=0.16,
                       legs=((2.4, 3.8), (21.6 + 0.8 * math.sin(ph), 4.4)), reach=True)
        f.update(o)
        grass(f, 4, 27, 30, k, front=True)
        t = k / N
        for j, sg in enumerate((-1, 1)):
            tt = (t + j * 0.5) % 1
            leaf_glyph(f, round(13.5 + sg * (5 + 6 * tt)), round(25 - 8 * math.sin(math.pi * tt)))
        frames.append(finish({p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}))
    return frames


TAIL_STAND = [(16.6, -0.8), (19.0, -3.2), (21.0, -6.2), (21.4, -9.4)]   # 서 있을 때 땅에 끌리듯 뒤로 내린 꼬리
TAIL_STANDR = [1.6, 3.0, 3.2, 1.8]


def ibeam() -> list[dict]:
    """위 덩굴의 포도송이에 두 앞발을 뻗어 발돋움 — 덩굴이 I 의 위 가로획, 풀 덤불이 아래 가로획. 포도가 흔들린다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sw = math.sin(ph)
        for x in range(8, 24):                       # 덩굴
            f[x, 2] = BARK_D
        for x0 in (8, 20):
            leaf_glyph(f, x0 - (0 if x0 > 15 else 1), 0)
        gx = 15.5 + 0.8 * sw
        for (u, v) in ((-1.2, 4.6), (1.2, 4.6), (0.0, 6.4), (-1.0, 8.0), (1.0, 8.0), (0.0, 9.6)):   # 포도송이
            solid(f, disc(gx + u, v, 1.3), GRAPE, GRAPE_D)
            f[math.floor(gx + u - 0.4), math.floor(v - 0.4)] = GRAPE_L
        f[15, 3] = BARK_D
        reach = 0.5 * (1 + sw)                      # 발돋움 — 뒷발 끝은 땅에 두고 몸만 늘인다
        rig = Rig(15.5, 11.4, 90.0, 0.7)            # 옆모습을 세운다: 코가 위, 배가 왼쪽
        o, _, _ = side(rig, ph, "smile" if k != 6 else "blink", tail=TAIL_STAND, tail_r=TAIL_STANDR, tail_amp=0.12,
                       legs=((-0.6 - reach, 3.4), (21.6, 1.8)), reach=True)
        f.update({p: c for p, c in o.items() if p[1] <= 28})
        grass(f, 8, 23, 29, k, front=True)
        frames.append(finish({p: c for p, c in f.items() if 0 <= p[1] <= 30}))
    return frames


TIP_, BACK = (1.5, 29.5), (27.6, 14.6)   # 붓 끝 · 붓대 꽁무니(화면)


def pen() -> list[dict]:
    """붓을 끌어안고 쓴다 — 붓털이 여우 꼬리처럼 주황에 흰 끝, 먹 묻은 끝이 핫스팟. 붓 끝을 축으로 살짝 까딱인다"""
    frames = []
    base = Rig(21.0, 13.4, 0.0, 0.62)
    L = math.hypot(BACK[0] - TIP_[0], BACK[1] - TIP_[1])
    ux, uy = (BACK[0] - TIP_[0]) / L, (BACK[1] - TIP_[1]) / L
    belly = (TIP_[0] + ux * 4.6, TIP_[1] + uy * 4.6)
    neck = (TIP_[0] + ux * 6.4, TIP_[1] + uy * 6.4)
    lt, lbel, lnk, lb = base.local(*TIP_), base.local(*belly), base.local(*neck), base.local(*BACK)
    k_ = base.k

    def bcol(a, b):
        x, y = base.world(a, b)
        t = (x - TIP_[0]) * ux + (y - TIP_[1]) * uy
        s = -(x - TIP_[0]) * uy + (y - TIP_[1]) * ux
        if t < 1.6:
            return INK_
        if t < 3.2:
            return WHITE
        if t < 6.0:
            return FUR_L if s < -0.4 else FUR
        if t < 7.4:
            return FERRULE
        if t > L - 1.4:
            return BARK_D
        return BARK if s < 0.5 else BARK_D
    brush = ("brush", any_of(bar(lt, lbel, 0.45 / k_, 1.9 / k_), bar(lbel, lnk, 1.9 / k_, 1.3 / k_),
                             bar(lnk, lb, 1.2 / k_)), bcol, True)
    paws = (base.local(TIP_[0] + ux * L * 0.6, TIP_[1] + uy * L * 0.6 - 0.4),
            base.local(TIP_[0] + ux * L * 0.78, TIP_[1] + uy * L * 0.78 - 0.4))
    for k, ph in enumerate(phases()):
        d = math.radians(3.0 * math.sin(2 * ph))
        ox, oy = base.ox - TIP_[0], base.oy - TIP_[1]
        rig = Rig(TIP_[0] + ox * math.cos(d) - oy * math.sin(d), TIP_[1] + ox * math.sin(d) + oy * math.cos(d),
                  math.degrees(d), base.k)
        f, _ = front(rig, ph, "blink" if k == 4 else "smile", paws=paws, mid=(brush,), tail=TAIL_UP,
                     tail_r=TAIL_UPR, tail_amp=0.12)
        f[math.floor(TIP_[0]), math.floor(TIP_[1])] = INK_
        frames.append(finish({p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}))
    return frames


def curled(rig: Rig, ph: float) -> dict:
    """꼬리를 감고 엎드려 잠든 여우 — 앞을 본 머리 · 감은 눈, 둥근 몸을 감은 꼬리의 흰 끝이 턱 밑에 온다.
    숨 쉬듯 몸이 살짝 부푼다. 원점은 머리 가운데"""
    br = 1.0 + 0.05 * math.sin(ph)
    tail = tail_part([(7.0, 1.6), (7.6, 5.0), (3.6, 7.2), (-1.6, 7.2), (-5.6, 5.4)], [2.0, 2.8, 3.0, 2.8, 1.8], 0.7,
                     lined=True)
    parts = [tail] + head_parts(ear_ln=0.8) + [("body", ell(3.0, 3.4, 6.6 * br, 4.2 * br), FUR, True)]
    out, _, _ = draw(rig, parts)
    face(out, rig, "blink")
    return out


def busy() -> list[dict]:
    """작은 화살표 여우 + 오른쪽 아래 꼬리를 감고 잠든 여우 — 둘레를 도토리 · 나뭇잎 여덟이 차례로 돈다"""
    frames = []
    cx, cy = 21.5, 21.0
    for k, ph in enumerate(phases()):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = math.floor(cx + 6.8 * math.cos(a) - 2.0), math.floor(cy + 6.8 * math.sin(a) - 2.5)
            lag = (head - i) % 8
            al = 255 if lag < 1 else 0xc0 if lag < 2 else 0x60
            (acorn_glyph if i % 2 == 0 else leaf_glyph)(f, x, y, al)
        f.update(curled(Rig(cx - 1.0, cy - 0.6, 0.0, 0.56), ph))
        f.update(arrow_fox(ph, small=True))
        frames.append(finish({p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}))
    return frames


def help_() -> list[dict]:
    """작은 화살표 여우 + 주황 털 물음표(점은 나뭇잎) — 글자 마디가 차례로 하나씩 부풀었다 돌아온다"""
    frames = []
    cells = [(17.6 + 2.2 * i, 11.6 + 2.2 * j) for j, row in enumerate(QMARK[:-1]) for i, ch in enumerate(row)
             if ch == "#"]
    for k, ph in enumerate(phases()):
        f = {}
        m = set()
        for i, (x, y) in enumerate(cells):
            d = (k * (len(cells) + 1) / N - i) % (len(cells) + 1)
            m |= disc(x, y, 1.5 + (0.5 if d < 1.5 else 0.0))
        solid(f, m, FUR, OUT)
        bob = 1 if (k * (len(cells) + 1) / N - len(cells)) % (len(cells) + 1) < 1.5 else 0
        leaf_glyph(f, 20, 25 - bob)
        f.update(arrow_fox(ph, small=True))
        frames.append(finish(f))
    return frames


# 칸 단위 작은 여우 얼굴(13×10) — 핀 · 사람 아이콘. 도형을 0.5 배로 줄여 찍으면 테두리가 속을 다 먹어
# 귀가 뿔 · 얼굴이 가면으로 읽혀서 작은 얼굴은 칸으로 그린다. E 는 눈, b 볼터치, n 코
FACE_G = [".#.........#.",
          "#k#.......#k#",
          "#fi#.....#if#",
          "#fii#####iif#",
          ".#fEfffffEf#.",
          ".#fEfffffEf#.",
          "#wwbfffffbww#",
          ".#wwwwnwwww#.",
          "..##wwwww##..",
          "....#####...."]


def face_glyph(f: dict, x0: int, y0: int, mood: str = "smile") -> None:
    pal = {"#": OUT, "k": TIP, "i": EAR_IN, "f": FUR, "w": WHITE, "E": EYE, "b": BLUSH, "n": NOSE}
    rows = FACE_G if mood != "blink" else FACE_G[:4] + [".#fffffffff#."] * 2 + FACE_G[6:]
    glyph_at(f, rows, pal, x0, y0)
    if mood == "blink":   # 감은 눈 — 가로 두 칸
        for x in (x0 + 2, x0 + 3, x0 + 9, x0 + 10):
            f[x, y0 + 5] = EYE


def hooded(f: dict, x0: int, y0: int, mood="smile", wave=0.0) -> None:
    """여우 모자(끝이 까만 세모 귀)를 쓴 사람 아이콘 — 칸 얼굴(`FACE_G`) 밑에 넓은 어깨. 오른팔을 흔든다.
    (x0, y0) 은 얼굴 글자판 왼쪽 위"""
    rig = Rig(x0 + 6.5, y0 + 13.0, 0.0, 0.6)
    hand_ = (11.0, -8.0 + wave)
    parts = [("hand", ell(*hand_, 1.8, 1.8), SOCK, True), ("sleeve", bar((6.0, -1.5), hand_, 1.7), SHIRT, False),
             ("torso", ell(0, 3.0, 9.0, 7.4), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
    out, _, _ = draw(rig, parts)
    f.update({p: c for p, c in out.items() if p[1] <= 30})
    face_glyph(f, x0, y0, mood)


def person() -> list[dict]:
    """작은 화살표 여우 + 여우 모자를 쓴 사람이 손을 흔든다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        hooded(f, 13, 12, "blink" if k == 6 else "smile", -2.0 * abs(math.sin(ph)))
        f.update(arrow_fox(ph, small=True))
        frames.append(finish(f))
    return frames


def pin() -> list[dict]:
    """작은 화살표 여우 + 덤불에서 얼굴을 내민 여우 옆에 빨간 지도 핀이 통통 튀어 꽂힌다 — 핀이 뜨면 여우가
    고개를 들어 보고, 꽂힐 때 눈을 감는다. 핀 동그라미 속에 얼굴을 넣으면 흰 수염 난 얼굴로 읽혀서 따로 둔다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 24.5, 11.0 + dy
        solid(f, disc(cx, cy, 5.0) | raster([(cx - 3.6, cy + 2.6), (cx + 3.6, cy + 2.6), (cx, cy + 14.5)]),
              SIGN, SIGN_D)
        for p in disc(cx, cy - 0.4, 1.8):   # 핀 머리의 흰 구멍
            f[p] = WHITE
        face_glyph(f, 9, 15 if dy < 0 else 16, "blink" if dy == 0 else "smile")
        bush(f, 15.0, 30, 9.5, 3.5, k)
        grass(f, 22, 29, 29, k, front=True)
        f.update(arrow_fox(ph, small=True))
        frames.append(finish({p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def top_cell(fr):
    """장마다 불투명한 칸 중 맨 위 칸(같으면 왼쪽) — 몇 장에만 뜨는 반짝이는 빼고 잡힌다"""
    common = set.intersection(*({p for p, c in f.items() if c[3] == 255} for f in fr))
    return min(common, key=lambda p: (p[1], p[0]))


def steady(fr):
    """장마다 불투명한 칸 중 판 가운데(15, 15)에 가장 가까운 칸 — 움직이는 여우라도 찍는 점이 늘 보이게"""
    common = set.intersection(*({p for p, c in f.items() if c[3] == 255} for f in fr))
    return min(common, key=lambda p: (math.hypot(p[0] - 15, p[1] - 15), p))


HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1),
       "wait": steady, "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (15, 15),
       "pen": (math.floor(TIP_[0]), math.floor(TIP_[1])), "hand": top_cell, "up": top_cell}


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

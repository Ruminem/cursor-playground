# SPDX-License-Identifier: Apache-2.0
"""다람쥐(squirrelanim) 구성표 그림 `art/squirrelanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/squirrel.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

숲속 친구들 · 애니 묶음(다람쥐 · 고슴도치 · 부엉이)의 하나. 해양 애니의 물낯 · 물보라 자리를 풀 덤불 · 나뭇잎 ·
도토리가 대신한다. 칸마다 다람쥐가 그 칸 뜻에 맞는 짓을 따로 한다(`SCENE`).
치비 비율 — 주황 갈색 큰 머리 · 크림 주둥이와 볼 · 2×2 콩알 눈에 흰 반짝 · 분홍 볼터치 · 끝 털 한 칸이 달린
뾰족한 작은 귀 · 작은 몸. 실루엣의 주인공은 몸만 한 S 자 꼬리다 — 굵게 부풀고 끝이 바깥으로 되말려서
여우 · 고양이 꼬리(가늘고 곧은)로 안 읽힌다. 꼬리 가운데에 짙은 등줄을 그어 S 가 겹쳐도 말린 꼴이 보인다.

  arrow   뒷발로 앉아 도토리를 안고 왼쪽 위로 고개를 쭉 빼 킁킁대는 옆모습 다람쥐, S 꼬리는 등 뒤로 솟았다 —
          코끝이 핫스팟. 앞발이 까딱(오물), 꼬리가 살랑, 발치로 나뭇잎 하나가 떨어진다
  busy    작은 화살표 다람쥐 + 오른쪽 아래 큰 도토리 둘레를 작은 도토리 여덟이 차례로 돈다
  cross   앞모습 얼굴(수염 없음 — 고양이로 읽혀서 뺐다). 네 방향에서 작은 도토리가 끝으로 과녁(코)을 콕콕 — 코가 핫스팟
  hand    앞발 하나를 머리 위로 높이 들어 콕 — 든 앞발 끝이 핫스팟. 다른 앞발은 도토리를 안고 꼬리를 살랑인다
  help    작은 화살표 다람쥐 + 도토리 색 물음표(점은 작은 도토리). 글자 마디가 차례로 부푼다
  ibeam   세로 나뭇가지(위아래 잎이 I 의 가로획) 오른쪽에 붙어 두 앞발로 가지를 쥔 작은 다람쥐. 가지가 몸을
          가로지르면 짙은 벌레 덩이가 돼서 옆에 붙였다. 핫스팟은 가지 가운데
  move    풀 덤불 위에서 통통 뛰는 앞모습 작은 다람쥐 + 네 방향 풀잎 화살촉
  nesw · ns · nwse · we   그 축으로 몸을 쭉 뻗고 날듯이 뛰는 옆모습 다람쥐 — 앞발과 곧게 편 굵은 꼬리가 양 끝이고 그
          바깥에 풀잎 화살촉(대각선은 꺾쇠). ns 는 다람쥐가 나무를 내려올 때처럼 머리를 아래로, 꼬리를 위로 세운다.
          작게 그리면 긴 주둥이 · 뾰족 귀만 남아 여우로 읽혀서 머리를 키우고 주둥이를 뭉툭하게 한다(`side(chibi=True)`)
  no      빨간 금지 표지 안에서 도토리를 꼭 끌어안고 눈을 질끈 감은 채 도리도리
  pen     연필을 끌어안은 다람쥐 — 연필 꽁무니가 지우개 대신 도토리 깍정이. 연필심(왼쪽 아래)이 핫스팟
  person  작은 화살표 다람쥐 + 다람쥐 모자(뾰족 귀)를 쓰고 등 뒤로 S 꼬리를 단 사람이 손을 흔든다
  pin     작은 화살표 다람쥐 + 크림 동그라미 속에 도토리가 든 빨간 지도 핀이 풀 위에서 통통 튄다(도토리 묻어 둔 자리)
  up      나무 기둥을 타고 오르는 옆모습 다람쥐 — 나무껍질 무늬가 아래로 흘러 오르는 것처럼 보인다. 코끝이 핫스팟
  wait    풀 덤불에 앉아 도토리를 볼에 쏙 넣고 오물오물(볼이 빵빵해진다) 다시 꺼낸다 — 꼬리가 살랑인다

몸은 부위(타원 · 굵기가 변하는 막대 · 굵기가 변하는 사슬)를 다람쥐 제 좌표에 놓고 화면으로 돌려 찍는다(`Rig`, `draw`).
앞모습(`front`) · 옆모습(`side`) · 앉은 옆모습(`perch`, 화살표) 세 벌이다. 그리개는 gen/otter.py 와 같은 꼴이지만 다른 생성기를 import 하지 않으려고
여기 따로 둔다(otter.py 를 고치면 이 그림이 조용히 바뀌지 않게).
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, disc, finish, hx, ink, phases, raster, solid, write

SID = "squirrelanim"

OUT, EYE, NOSE = hx("3a1f0eff"), hx("1e0f06ff"), hx("5a2a1cff")           # 테두리 · 눈 · 코
FUR, FUR_D, FUR_L = hx("cc7430ff"), hx("9c5222ff"), hx("e39a55ff")       # 몸 · 그늘(발) · 밝은 털
TAIL, TAIL_D, TAIL_L = hx("c06a2aff"), hx("8e4a1cff"), hx("e8a866ff")    # 꼬리 · 등줄 · 털끝
CREAM, CREAM_D, HI = hx("f7e3c0ff"), hx("e2c398ff"), hx("fffaf0ff")      # 배 · 볼 · 그늘 · 반짝
BLUSH, TOOTH = hx("f49a9aff"), hx("ffffffff")
ink(OUT, HI, hx("f6e9d2c7"))
NUT, NUT_D, CAP, CAP_L = hx("a0662eff"), hx("7a4a1eff"), hx("6b4423ff"), hx("8a5c34ff")   # 도토리 · 깍정이
LEAF, LEAF_D, LEAF_L = hx("5aa04aff"), hx("3f7a35ff"), hx("86c46aff")   # 풀 · 나뭇잎
BARK, BARK_D, BARK_L = hx("8a6a4cff"), hx("5e4630ff"), hx("a88866ff")   # 나무껍질 · 나뭇가지
PENCIL, PENCIL_D, WOOD, LEAD = hx("f5c842ff"), hx("c8961cff"), hx("efd2a8ff"), hx("3a3a3aff")
FERRULE = hx("b8b8c0ff")


# ── 그리개: 다람쥐 제 좌표 (a, b) → 화면 ─────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도, a 축이 화면에서 가리키는 쪽, 90 이 아래) · 배율 k · 뒤집기 fl.
    b 축은 a 축을 시계 방향으로 90도 돌린 쪽(ang=0 이면 a 가 오른쪽, b 가 아래). fl 이면 b 축을 반대로,
    kb 는 b 축만 그만큼 더 늘린다"""

    def __init__(self, ox: float, oy: float, ang: float = 0.0, k: float = 1.0, fl: bool = False, kb: float = 1.0):
        t = math.radians(ang)
        self.ox, self.oy, self.c, self.s, self.k = ox, oy, math.cos(t), math.sin(t), k
        self.f = (-1.0 if fl else 1.0) * kb     # kb 는 b 축만 더 늘리는 배(통통하게)

    def world(self, a: float, b: float) -> tuple:
        b *= self.f
        return self.ox + (a * self.c - b * self.s) * self.k, self.oy + (a * self.s + b * self.c) * self.k

    def local(self, x: float, y: float) -> tuple:
        dx, dy = (x - self.ox) / self.k, (y - self.oy) / self.k
        return dx * self.c + dy * self.s, (-dx * self.s + dy * self.c) / self.f

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


def chain_d(pts, rs):
    """굵기가 변하는 사슬(꼬리)의 (a, b) → 가운데 줄에서 떨어진 정도(1 이면 겉 테두리)"""
    segs = list(zip(pts, pts[1:], rs, rs[1:]))

    def d(a, b):
        best = 9.0
        for (x0, y0), (x1, y1), r0, r1 in segs:
            ex, ey = x1 - x0, y1 - y0
            t = max(0.0, min(1.0, ((a - x0) * ex + (b - y0) * ey) / (ex * ex + ey * ey or 1e-9)))
            best = min(best, math.hypot(a - x0 - ex * t, b - y0 - ey * t) / (r0 + (r1 - r0) * t))
        return best
    return d


def wiggle(pts, amp: float, ph: float):
    """사슬을 밑동(첫 점) 쪽부터 휘게 한다 — 끝으로 갈수록 크게, 조금 늦게 따라온다(살랑)"""
    out = [pts[0]]
    n = len(pts) - 1
    tot = 0.0
    for i in range(1, len(pts)):
        tot += amp * (i / n) * math.sin(ph - 0.5 * i)   # 앞 마디가 돈 만큼 같이 돌린 자리에서 이어 붙인다
        x, y = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
        c, s = math.cos(tot), math.sin(tot)
        px, py = out[-1]
        out.append((px + x * c - y * s, py + x * s + y * c))
    return out


def tail_part(pts, rs, name="tail", lined=False):
    """꼬리: 가운데 짙은 등줄 · 털끝은 밝게"""
    d = chain_d(pts, rs)

    def col(a, b):
        v = d(a, b)
        return TAIL_D if v < 0.34 else TAIL_L if v > 0.8 else TAIL
    return (name, lambda a, b: d(a, b) <= 1.0, col, lined)


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


def eye(f: dict, rig: Rig, a: float, b: float, mood: str = "smile", big: bool | None = None) -> None:
    """콩알 눈. 크면(k ≥ 0.75, 또는 big) 2×2 에 흰 반짝 한 칸, 작으면 한 칸. blink 는 가로 한 줄, shut 은 질끈(> <)"""
    x, y = rig.cell(a, b)
    big = rig.k >= 0.75 if big is None else big
    if mood == "blink":
        f[x, y + 1] = EYE
        if big:
            f[x + 1, y + 1] = EYE
    elif mood == "shut":
        f[x, y] = EYE
        f[x + 1, y + 1] = EYE
        f[x, y + 2] = EYE
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


# ── 도토리 ────────────────────────────────────────────────────────────────────
def acorn_parts(ca: float, cb: float, s: float = 1.0, rot: float = 0.0, name: str = "acorn") -> list:
    """(ca, cb) 가 알 가운데인 도토리 — 위가 깍정이, 아래 끝이 뾰족. rot 은 라디안(0 이면 꼭지가 위)"""
    c, sn = math.cos(rot), math.sin(rot)

    def to(u, v):   # 도토리 제 좌표(u 가로, v 아래) → (a, b)
        return ca + (u * c - v * sn) * s, cb + (u * sn + v * c) * s

    def back(a, b):
        da, db = (a - ca) / s, (b - cb) / s
        return da * c + db * sn, -da * sn + db * c
    nut = ell(0, 0.4, 1.8, 2.0)
    tip = bar((0, 1.2), (0, 2.9), 1.0, 0.25)
    cap = any_of(ell(0, -1.3, 2.25, 1.15), bar((0, -2.2), (0.5, -3.2), 0.45))

    def nut_col(a, b):
        u, v = back(a, b)
        return NUT_D if u > 0.7 else NUT

    def cap_col(a, b):
        u, v = back(a, b)
        return CAP_L if (round(u * 1.2) + round(v * 1.2)) % 2 == 0 and v > -2.0 else CAP
    return [(name + "_cap", lambda a, b: cap(*back(a, b)), cap_col, True),
            (name, lambda a, b: nut(*back(a, b)) or tip(*back(a, b)), nut_col, True)]


ACORN_G = ["..#..",
           ".#c#.",
           "#cCc#",
           "#nnN#",
           ".#n#.",
           "..#.."]


def acorn_glyph(f: dict, x0: int, y0: int, alpha: int = 255, rot: int = 0) -> None:
    """칸 단위 작은 도토리(5×6, 끝이 아래) — 고리 · 물음표 점 · 조준선. rot 은 시계 방향 90도 돌린 횟수"""
    pal = {"#": OUT, "c": CAP, "C": CAP_L, "n": NUT, "N": NUT_D}
    g = ACORN_G
    for _ in range(rot % 4):
        g = ["".join(g[len(g) - 1 - j][i] for j in range(len(g))) for i in range(len(g[0]))]
    for j, row in enumerate(g):
        for i, ch in enumerate(row):
            if ch != ".":
                r, gg, b, _ = pal[ch]
                f[x0 + i, y0 + j] = (r, gg, b, alpha)


LEAF_G = ["...lL",
          "..lLl",
          ".lDl.",
          "lDl..",
          "D...."]


def leaf(f: dict, x0: int, y0: int, rot: int = 0) -> None:
    """칸 단위 작은 나뭇잎(5×5, 꼭지가 왼쪽 아래 · 짙은 잎맥). rot 은 시계 방향 90도 돌린 횟수 — 테두리 없이
    색으로만 그린다(작은 잎에 테두리를 두르면 짙은 덩이가 된다)"""
    pal = {"l": LEAF, "L": LEAF_L, "D": LEAF_D}
    g = LEAF_G
    for _ in range(rot % 4):
        g = ["".join(g[len(g) - 1 - j][i] for j in range(len(g))) for i in range(len(g[0]))]
    for j, row in enumerate(g):
        for i, ch in enumerate(row):
            if ch != ".":
                f.setdefault((x0 + i, y0 + j), pal[ch])


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int) -> None:
    """(dx, dy) 쪽을 가리키는 풀잎 화살촉. 꼭짓점이 (cx, cy). 바깥 줄은 밝은 잎, 안 줄은 짙은 잎"""
    if dx and dy:                                # 대각선은 꺾쇠(ㄱ) 꼴 — 위 식으로는 두 칸 건너 점선이 된다
        for i in range(5):
            for w in (0, 1):
                c = LEAF if w == 0 else LEAF_D
                f[cx - dx * i, cy - dy * w] = c
                f[cx - dx * w, cy - dy * i] = c
        return
    px, py = -dy, dx
    for i in range(4):
        for s in (-1, 1):
            for w in (0, 1):
                f[cx - dx * (i + w) + s * px * i, cy - dy * (i + w) + s * py * i] = LEAF if w == 0 else LEAF_D


def grass(f: dict, x0: int, x1: int, y: int, k: int = 0) -> None:
    """풀 덤불: 밑줄 짙은 풀 위로 들쭉날쭉 풀잎이 바람에 까딱인다"""
    for x in range(x0, x1 + 1):
        f.setdefault((x, y), LEAF_D)
        h = (1, 2, 1, 3, 2, 1, 2)[(x * 3) % 7]
        lean = 1 if (x + k // 3) % 4 == 0 and h > 1 else 0
        for j in range(1, h):
            f.setdefault((x + (lean if j == h - 1 else 0), y - j), LEAF if j < h - 1 else LEAF_L)


# ── 앞모습 다람쥐: a 가로(+오른쪽), b 세로(+아래), 원점은 머리 가운데 ─────────────────────
TAIL_F = [(3.2, 11.6), (7.2, 11.2), (10.2, 7.6), (11.2, 2.6), (10.2, -2.4), (7.6, -6.4), (5.6, -9.2), (7.4, -11.8)]
TAIL_FR = [1.6, 2.6, 3.4, 3.8, 3.8, 3.4, 2.8, 2.0]


def head_parts(puff: float = 0.0, turn: float = 0.0, ears: bool = True) -> list:
    """앞모습 머리: 주황 동그라미 · 크림 주둥이와 볼(puff 만큼 빵빵) · 뾰족한 작은 귀. turn 은 고개를 돌린 만큼(칸)"""
    cheeks = any_of(ell(-3.3 + turn, 2.0, 2.6 + puff, 2.2 + 0.6 * puff), ell(3.3 + turn, 2.0, 2.6 + puff, 2.2 + 0.6 * puff))
    muzzle = ell(turn, 2.2, 2.4, 2.0)
    rings = any_of(ell(-2.4 + turn, -1.1, 1.9, 1.8), ell(2.4 + turn, -1.1, 1.9, 1.8))   # 눈테 — 고양이와 가르는 크림 테

    def skin(a, b):
        return CREAM if muzzle(a, b) or cheeks(a, b) or rings(a, b) else FUR
    head = any_of(ell(0, -0.4, 5.6, 5.0), ell(0, 1.4, 6.0, 3.6), cheeks)
    parts = [("head", head, skin, True)]
    if ears:
        # 귀는 뾰족하고 작게 — 둥글게 크면 곰 · 햄스터가 된다
        er = any_of(bar((-2.8, -3.8), (-3.5, -7.4), 1.3, 0.5), bar((2.8, -3.8), (3.5, -7.4), 1.3, 0.5))
        parts.append(("ears", er, lambda a, b: CREAM_D if abs(abs(a) - 3.1) < 0.5 and -6.0 < b < -4.4 else FUR, False))
    return parts


def face(f: dict, rig: Rig, mood: str = "smile", turn: float = 0.0, ears: bool = True) -> None:
    """눈 · 코 · 앞니 · 볼터치 · 귀 끝 털"""
    for sg in (-1, 1):
        if mood == "shut":
            shut_pair(f, rig, sg * 2.6 + turn - 0.5, -2.0, sg)
        else:
            eye(f, rig, sg * 2.6 + turn - 0.5, -1.6, mood)
        dot(f, rig, sg * 4.2 + turn, 1.4, BLUSH)
        if ears:
            dot(f, rig, sg * 3.6, -8.1, OUT)         # 귀 끝 털 한 칸
    dot(f, rig, turn, 0.6, NOSE)                      # 코
    dot(f, rig, turn - 1.0, 1.6, NOSE)                # 입 양 끝
    dot(f, rig, turn + 1.0, 1.6, NOSE)
    dot(f, rig, turn, 1.6, TOOTH)                     # 앞니


def front(rig: Rig, ph: float = 0.0, mood: str = "smile", puff: float = 0.0, paws=((-1.6, 5.6), (1.6, 5.6)),
          acorn=(0.0, 6.4), tail_amp: float = 0.10, elbows=(None, None), turn: float = 0.0, mid=(),
          tail=None, pr: float = 1.4, back=()) -> tuple[dict, set]:
    """앞모습 다람쥐 한 장. paws 는 앞발 끝 둘, acorn 은 가슴에 안은 도토리 가운데(None 이면 없음),
    elbows 는 팔꿈치(팔을 머리 위로 들 때), mid 는 앞발 뒤 · 몸 앞에 놓을 부위(연필 · 나뭇가지)"""
    tp = wiggle(tail or TAIL_F, tail_amp, ph)
    arms, pads = [], []
    for i, (sg, (pa, pb)) in enumerate(zip((-1, 1), paws)):
        sh = (sg * 3.2, 6.6)
        if elbows[i]:
            arms += [bar(sh, elbows[i], 1.4, 1.3), bar(elbows[i], (pa, pb), 1.3, 1.2)]
        else:
            arms.append(bar(sh, (pa, pb), 1.4, 1.2))
        pads.append(ell(pa, pb, pr if i == 0 else 1.4, (pr if i == 0 else 1.4) * 0.93))

    def body(a, b):
        return CREAM if (a / 2.8) ** 2 + ((b - 9.8) / 3.0) ** 2 <= 1 else FUR
    nut = acorn_parts(acorn[0], acorn[1], 0.85) if acorn else []
    parts = [("paw", any_of(*pads), FUR_D, True)] + nut + list(mid) + \
        [("arm", any_of(*arms), FUR, False)] + head_parts(puff, turn) + \
        [("foot", any_of(ell(-2.8, 12.9, 2.1, 1.1), ell(2.8, 12.9, 2.1, 1.1)), FUR_D, True),
         ("body", any_of(ell(0, 9.2, 4.6, 4.2), ell(0, 6.4, 3.6, 2.0)), body, True)] + list(back) + \
        [tail_part(tp, TAIL_FR)]
    out, mask, _ = draw(rig, parts)
    face(out, rig, mood, turn)
    return out, mask


# ── 옆모습 다람쥐: 코끝이 원점, a 는 꼬리 쪽(+), b 는 배 쪽(+) ───────────────────────────
TAIL_CURL = [(17.6, -1.4), (21.2, -3.6), (23.4, -7.6), (22.0, -11.6), (18.0, -12.8), (15.4, -10.6), (16.8, -8.0)]
TAIL_CURLR = [1.8, 2.8, 3.6, 3.8, 3.4, 2.6, 1.8]
TAIL_LONG = [(17.0, -0.8), (20.0, -1.8), (23.4, -2.4), (26.6, -2.2), (28.8, -1.4)]
TAIL_LONGR = [2.4, 3.8, 4.4, 4.2, 3.0]


def side(rig: Rig, ph: float = 0.0, mood: str = "smile", tail=None, tail_r=None, tail_amp: float = 0.12,
         run: float = 1.0, legs=None, chibi: bool = False) -> tuple[dict, set, dict]:
    """옆모습 다람쥐 한 장. ph 로 앞뒤 발이 번갈아 뻗고(run 배) 꼬리가 살랑인다.
    legs 를 주면 (앞발 끝, 뒷발 끝) 을 그 자리에 고정한다(나무 타기). 주둥이를 머리 앞으로 내밀어 둔다 —
    비스듬히 눕혔을 때 머리 옆이 코끝보다 판 가장자리로 튀어나오지 않게. chibi 면 머리를 키우고 주둥이를 뭉툭하게,
    눈을 2×2 로 — 작게 그리는 크기 조절 칸에서 긴 주둥이 · 뾰족 귀만 남아 여우로 읽혀서. → (칸: 색, 칸 집합, 이름 있는 자리)"""
    tp = wiggle(tail or TAIL_CURL, tail_amp, ph)
    sw = math.sin(ph) * run
    fore, hind = legs or ((7.4 + 1.4 * sw, 5.4 - 0.6 * abs(sw)), (21.0 - 1.4 * sw, 5.4))
    eye_ab = (4.6, -2.0)

    def head(a, b):
        return CREAM if b > 1.0 and a < 8.6 else FUR

    def body(a, b):
        return CREAM if b > 1.7 else FUR
    parts = [("nose", ell(0.8, 0.3, 0.9, 0.8), NOSE, False),
             ("paw", ell(*fore, 1.3, 1.2), FUR_D, True),
             ("arm", bar((10.4, 2.6), fore, 1.4, 1.2), FUR, True),
             ("head", any_of(ell(7.2, -0.2, 5.8, 5.4), ell(3.4, 1.0, 2.8, 2.6), ell(6.0, 2.2, 4.0, 3.0)) if chibi else
              any_of(ell(7.0, 0.0, 5.0, 4.6), ell(3.6, 0.8, 3.4, 2.7), ell(6.0, 1.8, 3.6, 2.8)), head, True),
             ("ear", bar((8.0, -3.6), (9.0, -6.6), 1.5, 0.6), FUR, False),
             ("foot", bar((18.4, 3.0), hind, 1.3, 1.1), FUR_D, True),
             ("thigh", ell(17.4, 1.2, 3.1, 3.0), FUR, True),
             ("body", any_of(ell(13.0, 1.0, 5.0, 3.9), ell(10.4, 0.8, 3.2, 3.6)), body, False),
             tail_part(tp, tail_r or TAIL_CURLR)]
    out, mask, _ = draw(rig, parts)
    eye(out, rig, *eye_ab, mood, True if chibi else None)
    dot(out, rig, 6.6, 1.6, BLUSH)
    dot(out, rig, 9.3, -7.4, OUT)      # 귀 끝 털
    return out, mask, {"nose": rig.cell(0.1, 0.1)}


# ── 화살표 다람쥐: 뒷발로 앉아 왼쪽 위로 고개를 쭉 빼고 킁킁 — 코끝이 원점(왼쪽 위 끝) ─────────────
# 칸 단위(k=1 이면 판 한 칸 = 1)로 바로 놓는다. 머리는 왼쪽 위, 몸은 오른쪽 아래, S 꼬리는 등 뒤(오른쪽)로 솟아
# 화살표 꼴 세모가 된다. 처음엔 옆모습 몸(`side`)을 45도 눕혀 뛰어드는 꼴이었는데 꼬리가 등 쪽(오른쪽 위)으로
# 말려 가로로 누운 덩이가 되고, 긴 주둥이 · 뾰족 귀만 남아 여우로 읽혔다
TAIL_P = [(15.0, 20.0), (18.8, 18.8), (21.2, 14.6), (21.8, 9.6), (20.8, 5.4), (17.8, 3.8), (15.6, 5.4), (16.4, 7.6)]
TAIL_PR = [1.8, 2.8, 3.4, 3.6, 3.4, 2.6, 2.0, 1.4]


def perch(rig: Rig, ph: float = 0.0, mood: str = "smile", sniff: float = 0.0) -> dict:
    """앉은 옆모습 다람쥐(코끝이 rig 원점). 가슴에 도토리를 안고, sniff 만큼 앞발이 까딱(오물), 꼬리가 살랑"""
    tp = wiggle(TAIL_P, 0.10, ph)
    d = 0.45 * sniff

    def head(a, b):
        return CREAM if b - a > 0.6 and a + b < 13.0 else FUR

    def body(a, b):
        return CREAM if ((a - 9.0) / 2.6) ** 2 + ((b - 12.6) / 4.6) ** 2 <= 1 else FUR
    q = math.pi / 4
    parts = [("nose", ell(0.9, 0.9, 0.9, 0.9), NOSE, False)] + \
        [("paw", any_of(ell(6.6 + d, 9.6 - d, 1.4, 1.2), ell(8.0 + d, 11.6 - d, 1.4, 1.2)), FUR_D, True)] + \
        acorn_parts(5.4 + d, 10.8 - d, 0.95, -0.5) + \
        [("head", any_of(ell(5.6, 5.2, 4.8, 4.4), ell(2.8, 2.8, 2.7, 2.0, q)), head, True),
         ("ear", bar((7.6, 2.0), (9.6, 0.4), 1.4, 0.5), lambda a, b: FUR, False),
         ("foot", bar((12.6, 21.4), (8.0, 22.6), 1.4, 1.1), FUR_D, True),
         ("haunch", ell(14.0, 18.2, 3.6, 3.4), FUR, True),
         ("body", ell(11.4, 13.8, 4.8, 6.2), body, True),
         tail_part(tp, TAIL_PR)]
    out, _, _ = draw(rig, parts)
    eye(out, rig, 4.2, 3.0, mood)
    dot(out, rig, 6.6, 6.4, BLUSH)
    dot(out, rig, 10.4, 0.2, OUT)                     # 귀 끝 털
    out[rig.cell(0.3, 0.3)] = NOSE                    # 코끝(핫스팟)은 늘 불투명
    return out


ARROW = Rig(1.0, 1.0, 0.0, 1.0)      # 화살표 다람쥐: 코끝이 (1, 1)
ARROW_S = Rig(1.0, 1.0, 0.0, 0.52)   # 작은 화살표 다람쥐 (busy · help · person · pin)


def arrow_squirrel(ph: float, small: bool = False) -> dict:
    k = round(N * ph / (2 * math.pi))
    return perch(ARROW_S if small else ARROW, ph, "blink" if k == 7 else "smile", max(0.0, math.sin(2 * ph)))


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    """왼쪽 위로 뛰어든다 — 앞뒤 발이 번갈아 뻗고 꼬리가 살랑, 배 밑으로 나뭇잎 하나가 빙글 떨어진다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = arrow_squirrel(ph)
        t = k / N
        leaf(f, round(2.0 + 2.0 * t + 1.2 * math.sin(2 * ph)), round(18.0 + 7.0 * t), k // 3)
        frames.append(finish(f))
    return frames


WAIT = Rig(12.0, 15.2, 0.0, 1.0)


def wait() -> list[dict]:
    """풀 덤불에 앉아 도토리를 볼에 넣고 오물오물 — 0–2 입에 대고, 3–4 쏙, 5–8 볼이 빵빵해져 오물거리고,
    9–11 다시 꺼낸다. 꼬리가 살랑인다. 가운데(배)가 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        if k <= 2:
            ac, puff, paws = (0.0, 5.2 - 0.4 * k), 0.0, ((-1.6, 4.6 - 0.4 * k), (1.6, 4.6 - 0.4 * k))
        elif k <= 4:
            ac, puff, paws = None, 0.6 * (k - 2), ((-1.4, 4.2), (1.4, 4.2))
        elif k <= 8:
            ac, puff, paws = None, 1.2 + (0.35 if k % 2 else 0.0), ((-1.4, 4.4), (1.4, 4.4))
        else:
            ac, puff, paws = (0.0, 4.4 + 0.4 * (k - 9)), 0.4, ((-1.6, 4.0 + 0.4 * (k - 9)), (1.6, 4.0 + 0.4 * (k - 9)))
        o, _ = front(WAIT, ph, "blink" if k == 6 else "smile", puff=puff, paws=paws, acorn=ac, tail_amp=0.14)
        grass(f, 4, 26, 29, k)
        f.update({p: c for p, c in o.items() if p[1] <= 28})
        frames.append(finish(f))
    return frames


def hand() -> list[dict]:
    """앞발 하나를 머리 위로 높이 들어 콕 — 다른 앞발은 도토리를 안고, 콕 할 때 발끝에 반짝. 든 앞발 끝이 핫스팟"""
    frames = []
    rig = Rig(16.6, 15.6, 0.0, 0.95)
    tip = (-6.8, -11.6)
    for k, ph in enumerate(phases()):
        f = {}
        o, _ = front(rig, ph, "blink" if k == 8 else "smile", paws=(tip, (1.0, 6.0)), acorn=(1.6, 6.4),
                     elbows=((-7.8, -3.4), None), tail_amp=0.12, pr=1.9)
        f.update(o)
        x, y = rig.cell(*tip)
        if k in (0, 1, 6, 7):   # 콕 — 발끝 양옆으로 반짝(발끝보다 위로는 안 나간다)
            for q in ((x - 3, y + 1), (x + 3, y + 1), (x - 3, y + 3), (x + 3, y + 3)):
                f.setdefault(q, HI if k % 2 == 0 else LEAF_L)
        for d in (-1, 1):       # 발가락 금
            f[x + d, y + 1] = OUT
        frames.append(finish(f))
    return frames


def cross() -> list[dict]:
    """앞모습 얼굴 — 가는 조준선 네 가닥, 끝마다 작은 도토리가 과녁 쪽을 콕콕. 코가 핫스팟.
    수염은 안 그린다 — 뾰족 귀 주황 얼굴에 수염까지 있으면 고양이로 읽힌다"""
    frames = []
    rig = Rig(15.5, 14.9, 0.0, 1.0)   # 코 칸이 (15, 15)
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0                   # 도토리가 과녁 쪽으로 콕
        for x in (7, 8, 22, 23, 24):
            f[x, 15] = OUT
        for y in (21, 22, 23, 24):
            f[15, y] = OUT
        out, _, _ = draw(rig, head_parts())
        f.update(out)
        face(f, rig, "blink" if k == 8 else "smile")
        acorn_glyph(f, 1 + o, 13, rot=3)            # 왼쪽 — 끝이 오른쪽(과녁)
        acorn_glyph(f, 25 - o, 13, rot=1)           # 오른쪽 — 끝이 왼쪽
        acorn_glyph(f, 13, 25 - o, rot=2)           # 아래 — 끝이 위
        acorn_glyph(f, 13, 1 + o, rot=0)            # 위 — 끝이 아래
        frames.append(finish(f))
    return frames


def no() -> list[dict]:
    """빨간 금지 표지 안에서 도토리를 꼭 끌어안고 눈을 질끈 감은 채 도리도리"""
    frames = []
    rig = Rig(14.6, 12.6, 0.0, 0.86)
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
        o, _ = front(rig, ph, "shut", paws=((-1.8, 6.0), (1.8, 6.0)), acorn=(0.0, 6.6), turn=turn, tail_amp=0.06)
        f.update({p: c for p, c in o.items() if p[1] <= 30})
        frames.append(finish(f))
    return frames


def chibi_move(rig: Rig, ph: float, mood: str) -> dict:
    o, _ = front(rig, ph, mood, acorn=None, paws=((-1.6, 6.4), (1.6, 6.4)), tail_amp=0.18)
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
        f.update(chibi_move(Rig(14.0, 13.6 - 1.4 * hop, 0.0, 0.62), ph, "blink" if k == 4 else "smile"))
        frames.append(finish(f))
    return frames


def stretch(ang: float, fl: bool = False) -> list[dict]:
    """ang 축으로 몸을 쭉 뻗고 날듯이 뛴다 — 앞발과 곧게 편 꼬리가 양 끝, 그 바깥 풀잎 화살촉이 가는 쪽으로
    두근댄다. 몸 가운데가 판 가운데"""
    frames = []
    t = math.radians(ang)
    ex, ey = math.cos(t), math.sin(t)            # 코 → 꼬리 쪽 (화면)
    dx, dy = round(ex), round(ey)
    R = 13 if dx == 0 or dy == 0 else 11
    K = 0.62 if dx == 0 or dy == 0 else 0.6
    MID = 15.2                                   # 앞발 끝 ~ 꼬리 끝의 가운데 (a)
    for k, ph in enumerate(phases()):
        f = {}
        d = 1.0 * math.sin(ph)                   # + 면 꼬리 쪽으로
        for sg in (-1, 1):
            o = 1 if sg * d > 0.3 else 0
            chevron(f, 15 + (1 if sg * dx > 0 else 0) + sg * dx * (R + o) - (1 if sg * dx > 0 else 0),
                    15 + sg * dy * (R + o), sg * dx, sg * dy)
        # 옆으로 1.35 배 통통하게 — 그대로 줄이면 막대기 · 족제비로 읽힌다
        rig = Rig(15.5 - (MID - d) * K * ex, 15.5 - (MID - d) * K * ey, ang, K, fl, kb=1.35)
        o_, _, _ = side(rig, ph, "blink" if k == 3 else "smile", TAIL_LONG, TAIL_LONGR, 0.10,
                        legs=((-0.4, 3.0 - 0.6 * math.sin(ph)), (24.0, 3.0 + 0.6 * math.sin(ph))), chibi=True)
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


UP_X = 15


def up() -> list[dict]:
    """나무 기둥을 타고 오른다 — 나무껍질 무늬가 아래로 흘러 오르는 것처럼 보이고, 앞뒤 발이 번갈아 기둥을 짚는다.
    코끝이 핫스팟"""
    frames = []
    rig = Rig(UP_X + 0.5, 1.2, 90.0, 0.8)     # 코가 위, 배가 왼쪽(기둥 쪽)
    for k, ph in enumerate(phases()):
        f = {}
        sw = math.sin(ph)
        o, _, _ = side(rig, ph, "blink" if k == 5 else "smile", TAIL_CURL, TAIL_CURLR, 0.12,
                       legs=((7.0 - 1.4 * sw, 5.2), (20.0 + 1.4 * sw, 5.0)))
        f.update({p: c for p, c in o.items() if p[1] <= 30})
        for y in range(7, 31):                 # 기둥 (다람쥐 뒤)
            for x in range(5, 12):
                if (x, y) in f:
                    continue
                if x in (5, 11):
                    f[x, y] = OUT
                elif (y + 2 * k // 2 * 0 + k * 2 + (x * 5) % 7) % 8 == 0:
                    f[x, y] = BARK_D
                else:
                    f[x, y] = BARK if x < 9 else BARK_L
        frames.append(finish(f))
    return frames


def ibeam() -> list[dict]:
    """세로 나뭇가지에 매달린 작은 다람쥐 — 위아래 잎이 I 의 가로획. 잎이 살랑이고 꼬리가 흔들린다"""
    frames = []
    X = 15
    for k, ph in enumerate(phases()):
        f = {}
        sw = math.sin(ph)
        for y in range(2, 30):
            f[X, y] = BARK_D
            f[X + 1, y] = BARK
        for sg, y in ((-1, 2), (1, 29)):   # 위 · 아래 잎(가로획)
            for i in range(1, 7):
                f[X - i, y] = LEAF if i < 6 else LEAF_L
                f[X + 1 + i, y] = LEAF if i < 6 else LEAF_L
            for i in range(1, 6, 2):
                f[X - i, y - sg] = LEAF_D
                f[X + 1 + i, y - sg] = LEAF_D
        if round(sw) != 0:
            f[X - 6, 2 - round(sw)] = LEAF_L
        # 다람쥐는 가지 오른쪽에 붙어 두 앞발로 가지를 쥔다 — 가지가 몸 앞을 지나면 몸이 둘로 갈려 벌레로 읽혔다
        rig = Rig(X + 5.6, 17.6, 0.0, 0.6)
        o, _ = front(rig, ph, "blink" if k == 8 else "smile", paws=((-7.4, 3.6), (-7.4, 6.4)), acorn=None,
                     elbows=((-4.6, 4.4), (-4.0, 7.4)), tail_amp=0.16)
        f.update({p: c for p, c in o.items() if 3 <= p[1] <= 28})
        frames.append(finish(f))
    return frames


TIP, BACK = (1.5, 29.5), (27.6, 14.6)   # 연필심 · 꽁무니(화면)


def pen() -> list[dict]:
    """연필을 꼭 끌어안고 쓴다 — 연필 꽁무니는 지우개 대신 도토리 깍정이. 연필심을 축으로 살짝 까딱인다"""
    frames = []
    base = Rig(21.0, 13.0, 0.0, 0.62)
    L = math.hypot(BACK[0] - TIP[0], BACK[1] - TIP[1])
    ux, uy = (BACK[0] - TIP[0]) / L, (BACK[1] - TIP[1]) / L
    cone = (TIP[0] + ux * 3.6, TIP[1] + uy * 3.6)
    lt, lc, lb = base.local(*TIP), base.local(*cone), base.local(*BACK)
    r = 1.6 / base.k

    def pcol(a, b):
        x, y = base.world(a, b)
        t = (x - TIP[0]) * ux + (y - TIP[1]) * uy
        s = -(x - TIP[0]) * uy + (y - TIP[1]) * ux
        if t < 1.4:
            return LEAD
        if t < 3.8:
            return WOOD
        if t > L - 2.4:
            return CAP_L if round(t + s) % 2 else CAP
        if t > L - 3.4:
            return FERRULE
        return PENCIL_D if s > 0.5 else PENCIL
    capend = bar(base.local(BACK[0] - ux * 2.0, BACK[1] - uy * 2.0), lb, 2.3 / base.k, 2.0 / base.k)
    pencil = ("pencil", any_of(bar(lt, lc, 0.45 / base.k, r), bar(lc, lb, r), capend), pcol, True)
    paws = (base.local(TIP[0] + ux * L * 0.62, TIP[1] + uy * L * 0.62 - 0.4),
            base.local(TIP[0] + ux * L * 0.78, TIP[1] + uy * L * 0.78 - 0.4))
    for k, ph in enumerate(phases()):
        d = math.radians(3.0 * math.sin(2 * ph))
        ox, oy = base.ox - TIP[0], base.oy - TIP[1]
        rig = Rig(TIP[0] + ox * math.cos(d) - oy * math.sin(d), TIP[1] + ox * math.sin(d) + oy * math.cos(d),
                  math.degrees(d), base.k)
        f, _ = front(rig, ph, "blink" if k == 4 else "smile", paws=paws, acorn=None, mid=(pencil,), tail_amp=0.12)
        f[math.floor(TIP[0]), math.floor(TIP[1])] = LEAD
        frames.append(finish({p: c for p, c in f.items() if p[0] <= 30 and p[1] >= 1}))
    return frames


def busy() -> list[dict]:
    """작은 화살표 다람쥐 + 오른쪽 아래 큰 도토리 — 둘레를 작은 도토리 여덟이 차례로 돈다(빙글빙글 작업 중)"""
    frames = []
    cx, cy = 21.5, 21.0
    for k, ph in enumerate(phases()):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = math.floor(cx + 6.6 * math.cos(a) - 2.0), math.floor(cy + 6.6 * math.sin(a) - 2.5)
            lag = (head - i) % 8
            acorn_glyph(f, x, y, 255 if lag < 1 else 0xc0 if lag < 2 else 0x60)
        f.update(draw(Rig(cx, cy, 0.0, 1.15), acorn_parts(0.0, 0.2))[0])
        f.update(arrow_squirrel(ph, small=True))
        frames.append(finish(f))
    return frames


def help_() -> list[dict]:
    """작은 화살표 다람쥐 + 도토리 색 물음표(점은 작은 도토리) — 글자 마디가 차례로 하나씩 부풀었다 돌아온다"""
    frames = []
    cells = [(17.6 + 2.2 * i, 11.6 + 2.2 * j) for j, row in enumerate(QMARK[:-1]) for i, ch in enumerate(row)
             if ch == "#"]
    for k, ph in enumerate(phases()):
        f = {}
        m = set()
        for i, (x, y) in enumerate(cells):
            d = (k * (len(cells) + 1) / N - i) % (len(cells) + 1)
            m |= disc(x, y, 1.2 + (0.5 if d < 1.5 else 0.0))
        solid(f, m, NUT, OUT)
        bob = 1 if (k * (len(cells) + 1) / N - len(cells)) % (len(cells) + 1) < 1.5 else 0
        acorn_glyph(f, 20, 24 - bob)
        f.update(arrow_squirrel(ph, small=True))
        frames.append(finish(f))
    return frames


def hooded(f: dict, rig: Rig, mood="smile", wave=0.0) -> None:
    """다람쥐 옷(뾰족 귀 후드 · 등 뒤 S 꼬리)을 입은 사람 아이콘 — 초록 옷 어깨. 왼팔을 흔든다"""
    shirt, shirt_d = LEAF, LEAF_D
    hand_ = (-8.4, -5.0 + wave)
    tail = [(4.0, 14.0), (8.6, 12.6), (11.0, 7.6), (10.8, 2.2), (8.6, -2.0), (10.2, -4.8)]
    parts = [("hand", ell(*hand_, 1.7, 1.7), FUR_D, True), ("sleeve", bar((-5.0, 4.5), hand_, 1.6), shirt, False)] + \
        head_parts() + [("hood", ell(0, -0.6, 7.4, 7.0), FUR, False),
                        ("torso", ell(0, 11.0, 7.6, 6.0), lambda a, b: shirt_d if abs(a) < 0.6 else shirt, True),
                        tail_part(wiggle(tail, 0.12, wave), [2.0, 3.0, 3.6, 3.6, 3.0, 2.0])]
    out, _, _ = draw(rig, parts)
    face(out, rig, mood)
    f.update({p: c for p, c in out.items() if p[1] <= 30})


def person() -> list[dict]:
    """작은 화살표 다람쥐 + 다람쥐 모자를 쓴 사람이 손을 흔든다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        hooded(f, Rig(20.0, 21.0, 0.0, 0.62), "blink" if k == 6 else "smile", -2.0 * abs(math.sin(ph)))
        f.update(arrow_squirrel(ph, small=True))
        frames.append(finish(f))
    return frames


def pin() -> list[dict]:
    """작은 화살표 다람쥐 + 빨간 지도 핀 동그라미 속에 도토리(다람쥐가 묻어 둔 자리) — 핀이 통통 튀고, 풀에 닿을 때
    도토리가 살짝 찌그러진다. 처음엔 다람쥐 얼굴을 넣었는데 핀 속 작은 얼굴은 귀 · 눈이 H 자로 뭉개졌다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 13.0 + dy
        grass(f, 18, 27, 28, 0)
        solid(f, disc(cx, cy, 6.6) | raster([(cx - 4.6, cy + 3.4), (cx + 4.6, cy + 3.4), (cx, cy + 12.6)]),
              SIGN, SIGN_D)
        solid(f, disc(cx, cy, 4.6), CREAM, SIGN_D)
        f.update(draw(Rig(cx, cy - 0.2, 0.0, 0.9 if dy else 0.82), acorn_parts(0.0, 0.0))[0])
        f.update(arrow_squirrel(ph, small=True))
        frames.append(finish(f))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def top_cell(fr):
    """맨 위 불투명 칸(같으면 왼쪽)"""
    return min((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1], p[0]))


HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1),
       "wait": (12, 24), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (15, 12),
       "pen": (math.floor(TIP[0]), math.floor(TIP[1])), "hand": top_cell, "up": top_cell}


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

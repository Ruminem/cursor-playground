# SPDX-License-Identifier: Apache-2.0
"""아기사슴(deeranim) 구성표 그림 `art/deeranim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/deer.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

숲속 친구들 · 애니 묶음의 한 마리(2기). 해양 애니의 물낯 · 물보라 자리를 풀 덤불 · 나뭇잎 · 버섯 · 잔가지가
대신한다. 칸마다 아기사슴이 그 칸 뜻에 맞는 짓을 따로 한다(`SCENE`).
치비 비율 — 황갈색 큰 머리 · 크림 주둥이와 턱 · 까만 코 · 2×2 콩알 눈에 흰 반짝 · 분홍 볼터치 · 옆으로 뻗은 큰 타원
귀(속은 분홍) · 작은 몸 · 등의 흰 점 두 줄 · 가늘고 긴 다리 끝 짙은 발굽 · 흰 속이 보이는 짧은 꼬리. 뿔은 없다(아기).
여우(주황 · 세모 귀 · 큰 꼬리) · 토끼(흰 털 · 위로 선 긴 귀)와는 흰 점 · 가는 다리와 발굽 · 옆으로 뻗은 타원 귀로
가른다. 그래서 몸이 보이는 칸은 옆모습을 주로 쓴다 — 앞모습은 흰 점이 안 보여 송아지 · 생쥐로 읽힌다.

  arrow   다리를 배 밑에 접고 엎드려 왼쪽 위로 고개를 쭉 내민 옆모습 아기사슴 — 왼쪽 위 끝(주둥이 · 이마)이
          핫스팟. 귀를 쫑긋 앞뒤로 돌리고 짧은 꼬리를 팔랑 들어 흰 속을 보인다
  busy    작은 화살표 사슴 + 오른쪽 아래 큰 광대버섯 둘레의 요정 고리 — 작은 버섯 여덟이 차례로 쑥 돋는다
  cross   앞모습 얼굴. 가는 조준선 네 가닥, 코가 핫스팟. 큰 귀를 한쪽씩 쫑긋 세웠다 내린다
  hand    앞모습으로 선 아기사슴이 한쪽 큰 귀를 하늘로 곧게 쫑긋 세워 가리킨다 — 귀 끝이 핫스팟. 톡 할 때
          귀 끝에 반짝이가 튀고 다른 귀가 파르르. (뒷다리로 서서 앞발굽을 드는 판은 다리가 얼굴을 가려 버렸다)
  help    작은 화살표 사슴 + 황갈색 털에 흰 점이 박힌 물음표(점은 버섯). 흰 점이 차례로 반짝인다
  ibeam   앞모습으로 다리를 모으고 꼿꼿이 선 아기사슴 — 옆으로 쫙 편 두 귀가 I 의 위 가로획, 발굽 밑
          풀줄이 아래 가로획, 긴 다리가 세로획. 귀를 파르르 턴다. 핫스팟은 몸 가운데. 앞모습은 앞다리 둘만
          테 없이 그린다 — 네 다리에 다 테를 두르면 다리 사이가 메워져 짙은 덩어리가 된다
  move    네 다리를 꼿꼿이 편 채 제자리에서 통통 튀는 옆모습 아기사슴(사슴의 껑충 뛰기) + 네 방향 풀잎 화살촉
  nesw · ns · nwse · we   그 축으로 앞다리는 앞으로, 뒷다리는 뒤로 쭉 뻗고 날듯이 뛰는 옆모습 — 앞발굽과
          뒷발굽이 양 끝이고 그 바깥에 풀잎 화살촉(사선은 ㄱ 자). 다리를 모았다 폈다 한다. 사선은 앞다리를
          배 밑에 접는다 — 넷을 다 뻗으면 돌린 몸에서 다리가 엉킨다
  no      빨간 금지 표지 안에서 네 다리를 쩍 벌려 버티고(안 갈래) 눈을 질끈 감은 채 고개를 도리도리 —
          귀를 뒤로 젖힌다. 핫스팟은 표지 가운데
  pen     잔가지를 입에 물고 땅에 글씨를 쓰는 아기사슴 — 잔가지 끝(왼쪽 아래)이 핫스팟. 고개를 까딱인다
  person  작은 화살표 사슴 + 사람 아이콘이 옆에 선 아기사슴 머리를 쓰다듬는다 — 사슴이 눈을 감고 꼬리가 팔랑
  pin     작은 화살표 사슴 + 풀밭에 발굽 자국이 하나씩 찍히며 빨간 지도 핀까지 이어진다. 핀이 통통 튀고 핀
          동그라미 속은 나뭇잎(발굽 자국을 넣으면 두 눈 달린 유령 얼굴로 읽혔다)
  up      네 발로 서서 목을 하늘로 쭉 뻗어 머리 위 잔가지의 나뭇잎을 뜯는다 — 위 끝이 핫스팟
  wait    풀밭에 서서 고개를 숙여 풀을 뜯다가 들어 오물오물 — 귀 한쪽씩 까딱, 꼬리 팔랑.
          핫스팟은 장마다 불투명한 칸 중 가운데에 가장 가까운 칸(`steady`)

몸은 부위(타원 · 굵기가 변하는 막대)를 사슴 제 좌표에 놓고 화면으로 돌려 찍는다(`Rig`, `draw`). 머리는 제 좌표를
따로 두고 목 끝에 돌려 붙인다(`head_xf`) — 풀 뜯기 · 하늘 보기처럼 머리만 숙이고 드는 칸이 많아서다.
옆모습(`side`) · 앞모습(`front`) 두 벌이다. 그리개는 gen/fox.py 와 같은 꼴이지만 다른 생성기를 import 하지 않으려고
여기 따로 둔다(그쪽을 고치면 이 그림이 조용히 바뀌지 않게). 숲 소품(풀 · 버섯 · 나뭇잎 · 잔가지) 색과 꼴은 같은 묶음과 맞춘다.
빌드가 부르지 않고 손으로 돌린다 · 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, disc, finish, hx, ink, inside, phases, raster, solid, write

SID = "deeranim"

OUT, EYE, NOSE = hx("3a2212ff"), hx("1e0f06ff"), hx("221410ff")           # 테두리 · 눈 · 코
FUR, FUR_D, FUR_L = hx("c07c44ff"), hx("94592eff"), hx("d89c64ff")       # 몸 · 먼 다리 · 밝은 털
CREAM, SPOT = hx("f6e8d0ff"), hx("fffbf2ff")                             # 주둥이 · 턱 · 배 · 꼬리 속 / 흰 점
HOOF = hx("2e1e16ff")
EAR_IN, BLUSH, HI = hx("f2c4b0ff"), hx("f49a9aff"), hx("fffaf0ff")       # 귓속 · 볼터치 · 반짝
ink(OUT, HI, hx("f6e9d2c7"))
NUT, NUT_D, CAP, CAP_L = hx("a0662eff"), hx("7a4a1eff"), hx("6b4423ff"), hx("8a5c34ff")   # 도토리 · 깍정이
LEAF, LEAF_D, LEAF_L = hx("5aa04aff"), hx("3f7a35ff"), hx("86c46aff")   # 풀 · 나뭇잎
BARK, BARK_D = hx("8a6a4cff"), hx("5e4630ff")                           # 잔가지
MUSH, MUSH_D, STEM = hx("d8573cff"), hx("a83a28ff"), hx("f2e4c8ff")      # 광대버섯 갓 · 갓 그늘 · 대
SKIN, HAIR, SHIRT, SHIRT_D = hx("f4c9a4ff"), hx("5a3a26ff"), hx("4a8a9aff"), hx("33666fff")
PRINT = hx("6b4a30ff")                                                  # 발굽 자국


# ── 그리개: 사슴 제 좌표 (a, b) → 화면 ─────────────────────────────────────────
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


class Xf:
    """자식 좌표(머리) → 부모 좌표(몸). 자식 원점이 부모의 (ox, oy), 자식 a 축이 부모에서 ang 도 돈 쪽"""

    def __init__(self, ox: float, oy: float, ang: float):
        t = math.radians(ang)
        self.ox, self.oy, self.c, self.s = ox, oy, math.cos(t), math.sin(t)

    def up(self, u: float, v: float) -> tuple:
        return self.ox + u * self.c - v * self.s, self.oy + u * self.s + v * self.c

    def down(self, a: float, b: float) -> tuple:
        da, db = a - self.ox, b - self.oy
        return da * self.c + db * self.s, -da * self.s + db * self.c

    def wrap(self, fn):
        """자식 좌표의 맞음 · 색 함수를 부모 좌표에서 부르게"""
        if not callable(fn):
            return fn
        return lambda a, b: fn(*self.down(a, b))


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


def eye_at(f: dict, p: tuple, big: bool, mood: str = "smile") -> None:
    """콩알 눈. p 는 왼쪽 위 칸. 크면 2×2 에 흰 반짝 한 칸, 작으면 세로 두 칸. blink 는 가로 한 줄"""
    x, y = p
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


def glyph_at(f: dict, rows: list, pal: dict, x0: int, y0: int, alpha: int = 255) -> None:
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != ".":
                r, g, b, _ = pal[ch]
                f[x0 + i, y0 + j] = (r, g, b, alpha)


def clip(f: dict) -> dict:
    return {p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}


# ── 숲 소품 (같은 묶음과 같은 색 · 꼴) ─────────────────────────────────────────────
LEAF_G = ["...##",
          ".#lL#",
          "#lLl#",
          "#Ll#.",
          ".##.."]
MUSH_G = [".###.",
          "#mSm#",
          "#####",
          ".#s#.",
          ".###."]
HOOF_G = [".#.#.",
          "##.##",
          "##.##",
          ".#.#."]


def leaf_glyph(f: dict, x0: int, y0: int, alpha: int = 255) -> None:
    """칸 단위 작은 나뭇잎(5×5) — 오른쪽 위로 끝이 뾰족"""
    glyph_at(f, LEAF_G, {"#": LEAF_D, "l": LEAF, "L": LEAF_L}, x0, y0, alpha)


def mush_glyph(f: dict, x0: int, y0: int, alpha: int = 255) -> None:
    """칸 단위 작은 광대버섯(5×5) — 빨간 갓에 흰 점 하나, 크림 대"""
    glyph_at(f, MUSH_G, {"#": OUT, "m": MUSH, "S": SPOT, "s": STEM}, x0, y0, alpha)


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int) -> None:
    """(dx, dy) 쪽을 가리키는 풀잎 화살촉. 꼭짓점이 (cx, cy). 바깥 줄은 밝은 잎, 안 줄은 짙은 잎"""
    if dx and dy:   # 사선은 ㄱ 자 두 팔 — 대각선으로 찍으면 칸이 바둑판으로 듬성듬성 빈다
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


def grass(f: dict, x0: int, x1: int, y: int, k: int = 0, front: bool = False) -> None:
    """풀 덤불: 밑줄 짙은 풀 위로 들쭉날쭉 풀잎이 바람에 까딱인다. front 면 이미 그린 것 위에 덮는다"""
    put = f.__setitem__ if front else f.setdefault
    for x in range(x0, x1 + 1):
        put((x, y), LEAF_D)
        h = (1, 2, 1, 3, 2, 1, 2)[(x * 3) % 7]
        lean = 1 if (x + k // 3) % 4 == 0 and h > 1 else 0
        for j in range(1, h):
            put((x + (lean if j == h - 1 else 0), y - j), LEAF if j < h - 1 else LEAF_L)


# ── 머리 (옆모습): 코끝이 원점, u 는 뒤통수 쪽(+), v 는 턱 쪽(+) ───────────────────────
JOINT = (8.0, 2.8)      # 목이 붙는 자리


def ear_hit(base, ln: float, w: float, ang: float):
    """base 에서 ang(도) 쪽으로 뻗은 타원 귀 → (전체, 귓속)"""
    t = math.radians(ang)
    cx, cy = base[0] + math.cos(t) * ln * 0.55, base[1] + math.sin(t) * ln * 0.55
    return (ell(cx, cy, ln * 0.6, w, t), ell(cx + math.cos(t) * 0.4, cy + math.sin(t) * 0.4, ln * 0.4, w * 0.55, t))


def head_side(ear: float = 0.0, chew: float = 0.0, flat: float = 0.0) -> list:
    """옆모습 머리 부위들(머리 제 좌표). ear 는 귀를 쫑긋 세운 만큼(도, + 면 앞으로 세움), flat 은 0–1 뒤로 붙임,
    chew 는 턱을 오물거린 만큼(칸)"""
    def snout_col(u, v):
        return CREAM if v > 0.5 - 0.15 * u else FUR

    def head_col(u, v):
        return CREAM if v > 1.6 and u < 7.0 else FUR
    near_a = -22.0 - ear + 26.0 * flat     # 귀 방향: 뒤(+u)에서 위로 든 각
    far_a = -52.0 - ear * 0.8 + 40.0 * flat
    ne, ni = ear_hit((8.4, -2.2), 6.0, 2.2, near_a)
    fe, fi = ear_hit((7.4, -3.6), 5.4, 2.0, far_a)
    return [("nose", ell(0.5, 0.4, 0.8, 0.7), NOSE, False),
            ("snout", bar((0.9, 0.6 + chew * 0.3), (3.8, 0.4), 1.1, 2.3), snout_col, False),
            ("head", ell(6.0, -0.8, 4.8, 4.4), head_col, True),
            ("ear", ne, lambda u, v: EAR_IN if ni(u, v) else FUR, True),
            ("ear2", fe, lambda u, v: EAR_IN if fi(u, v) else FUR_D, True)]


# ── 옆모습 사슴: 몸 가운데가 원점, a 는 꼬리 쪽(+), b 는 배 쪽(+) ───────────────────────
SHOULDER, HIP = (-2.6, 1.4), (3.0, 1.2)
NECK0 = (-2.6, -0.8)
STAND = (((-3.2, 8.6), 0.6), ((-1.6, 8.6), 0.6), ((2.8, 8.6), -0.8), ((4.4, 8.6), -0.8))   # 앞(가까운 · 먼) · 뒤(가까운 · 먼)
SPOTS = [(-1.8, -1.6), (0.0, -2.0), (1.8, -1.8), (3.4, -1.3), (-0.9, -0.1), (0.9, -0.4), (2.6, 0.0)]


def leg_parts(name: str, top, foot, bend: float, col, thick: float = 1.0, lined: bool = True) -> list:
    """다리 하나: 윗다리(굵다) → 무릎 → 가는 아랫다리 → 짙은 발굽. bend 는 무릎을 옆으로 민 만큼(다리 길이 몫)"""
    ex, ey = foot[0] - top[0], foot[1] - top[1]
    ln = math.hypot(ex, ey) or 1e-9
    ux, uy = ex / ln, ey / ln
    knee = (top[0] + ex * 0.45 - uy * bend * ln * 0.25, top[1] + ey * 0.45 + ux * bend * ln * 0.25)
    kx, ky = foot[0] - knee[0], foot[1] - knee[1]
    kl = math.hypot(kx, ky) or 1e-9
    hb = (foot[0] - kx / kl * 1.2, foot[1] - ky / kl * 1.2)
    return [(name + "_hoof", bar(hb, foot, 0.95 * thick, 0.9 * thick), HOOF, True),
            (name, any_of(bar(top, knee, 1.8 * thick, 1.05 * thick), bar(knee, hb, 1.0 * thick, 0.9 * thick)),
             col, lined)]


def head_xf(neck, tilt: float) -> Xf:
    """머리 제 좌표 → 몸 좌표. 머리의 JOINT 가 목 끝 neck 에 오게 원점을 옮긴다. tilt 가 + 면 코를 내린다
    (머리 u 축(뒤통수 쪽)을 거꾸로 돌려야 코가 내려간다)"""
    jx, jy = Xf(0.0, 0.0, -tilt).up(*JOINT)
    return Xf(neck[0] - jx, neck[1] - jy, -tilt)


def aim(ang: float, k: float, neck, tilt: float, at=(1.3, 1.3)) -> Rig:
    """코끝이 화면 at 에 오는 Rig"""
    r = Rig(0.0, 0.0, ang, k)
    x, y = r.world(*head_xf(neck, tilt).up(0.2, 0.4))
    return Rig(at[0] - x, at[1] - y, ang, k)


def side(rig: Rig, ph: float = 0.0, mood: str = "smile", neck=(-4.6, -3.6), tilt: float = 0.0,
         legs=STAND, ear: float = 0.0, flat: float = 0.0, tail: float = 0.0, chew: float = 0.0,
         lying: bool = False, mouth=(), spots: bool = True, thin: float = 1.0) -> tuple[dict, set, dict]:
    """옆모습 아기사슴 한 장 — 왼쪽을 본다(rig 으로 돌린다). neck 은 목 끝(머리가 붙는 자리), tilt 는 머리를
    돌린 각(도, + 면 코를 내림). legs 는 (발굽 자리, 무릎 굽힘) 넷: 앞 가까운 · 앞 먼 · 뒤 가까운 · 뒤 먼.
    tail 은 0–1 꼬리를 든 만큼(들면 흰 속), lying 이면 엎드린 몸(배를 땅에 붙인다), mouth 는 입에 문 부위,
    thin 은 다리 굵기 배수(작게 그릴 때 줄인다 — 네 다리가 한 덩어리 짙은 테로 메워지지 않게).
    → (칸: 색, 칸 집합, 이름 있는 자리)"""
    hx_ = head_xf(neck, tilt)
    head = [(n, hx_.wrap(h), hx_.wrap(c), ln) for n, h, c, ln in head_side(ear, chew, flat)]

    t = tail
    tail_end = (5.2 + 1.0 * (1 - t), -0.6 - 2.4 * t)
    tail_hit = bar((4.4, -0.8), tail_end, 1.1, 1.0)

    def tail_col(a, b):
        return CREAM if t > 0.4 and (a - 4.4) * (tail_end[1] + 0.8) - (b + 0.8) * (tail_end[0] - 4.4) > 0 else FUR

    def body_col(a, b):
        return CREAM if b > 2.0 else FUR
    near, far = [], []
    for i, ((foot, bend), top) in enumerate(zip(legs, (SHOULDER, SHOULDER, HIP, HIP))):
        top = (top[0] + (0.6 if i in (1, 3) else 0.0), top[1])
        if i in (0, 2):
            near += leg_parts(f"leg{i}", top, foot, bend, FUR, thin)
        else:
            far += leg_parts(f"leg{i}", top, foot, bend, FUR_D, thin)
    torso = ell(0.0, 0.0, 4.8, 2.9) if not lying else ell(0.0, 0.4, 5.2, 2.8)
    parts = list(mouth) + near + head[:3] + [head[3]] + [
        ("neck", bar(NECK0, neck, 2.3, 2.0), lambda a, b: FUR, False),
        ("thigh", ell(3.0, 0.6, 2.3, 2.5), FUR, True),
        ("body", torso, body_col, True),
        ("tail", tail_hit, tail_col, True),
        head[4]] + far
    out, mask, region = draw(rig, parts)
    big = rig.k >= 0.75
    ex, ey = hx_.up(4.2, -1.6)
    eye_at(out, rig.cell(ex, ey), big, mood)
    out[rig.cell(*hx_.up(6.2, 1.0))] = BLUSH
    if spots:
        for a, b in SPOTS:
            p = rig.cell(a, b)
            if region.get(p) == "body" and out.get(p) != OUT:
                out[p] = SPOT
    tx, ty = rig.world(*hx_.up(-0.4, 0.4))   # 코끝 바로 앞 — 거기에 가장 가까운 불투명 칸이 코끝 칸
    nose = min(mask, key=lambda p: (math.hypot(p[0] + 0.5 - tx, p[1] + 0.5 - ty), p))
    return out, mask, {"nose": nose, "head": hx_}


ARROW_NECK, ARROW_TILT = (-6.6, -4.4), -36.0   # 화살표 자세: 엎드려 목을 왼쪽 위로 쭉 뺀다
FOLDED = (((-0.8, 3.6), 4.0), ((0.2, 3.6), 4.0), ((1.4, 3.8), -4.3), ((2.4, 3.8), -4.3))   # 다리를 접고 엎드림
ARROW_ANG = 0.0                                 # 몸을 오른쪽 아래로 눕혀 코 → 꼬리가 화살 대
ARROW = aim(ARROW_ANG, 1.12, ARROW_NECK, ARROW_TILT)
ARROW_S = aim(ARROW_ANG, 0.72, ARROW_NECK, ARROW_TILT)   # 작은 화살표 사슴 (busy · help · person · pin)


def arrow_deer(ph: float, small: bool = False) -> dict:
    """화살표 사슴 — 왼쪽 위 끝 칸(주둥이)이 화면 (1, 1) 에 오게 몸을 민다. 코끝 칸을 맞추면 고개를 든 정수리가
    판 위로 잘려서 끝을 잰다"""
    k = round(N * ph / (2 * math.pi))
    rig0 = ARROW_S if small else ARROW
    sw = math.sin(ph)
    o, _, at = side(rig0, ph, "blink" if k == 7 else "smile", neck=ARROW_NECK, tilt=ARROW_TILT, legs=FOLDED,
                    ear=-10.0 + 24.0 * max(0.0, sw), tail=max(0.0, math.sin(2 * ph)), lying=True)
    nx, ny = min((p for p, c in o.items() if c[3] == 255), key=lambda p: (p[0] + p[1], p[1]))   # 왼쪽 위 끝(주둥이)
    return {(x - nx + 1, y - ny + 1): c for (x, y), c in o.items()}


# ── 앞모습 사슴: a 가로(+오른쪽), b 세로(+아래), 원점은 머리 가운데 ─────────────────────
def head_front(ears=(0.0, 0.0)) -> list:
    """앞모습 머리: 황갈색 머리 · 짙은 콧등 · 크림 주둥이 · 까만 코 · 비스듬히 위로 뻗은 큰 타원 귀
    (ears 는 (왼, 오른) 쫑긋 각, + 면 위로). 귀를 수평으로 뻗으면 그렘린 얼굴로 읽혀서 32도 든다"""
    parts = []
    muzzle = ell(0.0, 2.5, 2.1, 1.9)

    def skin(a, b):   # 이마에서 코로 내려오는 짙은 콧등 · 크림 주둥이
        if abs(a) < 0.9 and -2.6 < b < 1.4:
            return FUR_D
        return CREAM if muzzle(a, b) else FUR
    parts.append(("fnose", ell(0.0, 3.0, 1.3, 0.8), NOSE, False))
    parts.append(("fhead", any_of(ell(0.0, -0.6, 4.2, 3.8), muzzle), skin, True))
    hits = []
    for sg, e in zip((-1, 1), ears):
        ang = 180.0 + 32.0 + e if sg < 0 else -32.0 - e
        hits.append(ear_hit((sg * 2.8, -2.4), 6.4, 2.3, ang))
    parts.append(("fear", any_of(*(h[0] for h in hits)),
                  lambda a, b: EAR_IN if any(h[1](a, b) for h in hits) else FUR, True))
    return parts


def face_front(f: dict, rig: Rig, mood: str = "smile") -> None:
    big = rig.k >= 0.75
    for sg in (-1, 1):
        x, y = rig.cell(sg * 2.3 - (1.0 if big else 0.4), -1.0)
        if mood == "shut":
            f[x, y + 1] = f[x + 1, y + 1] = EYE
        else:
            eye_at(f, (x, y), big, mood)
        f[rig.cell(sg * 3.2, 1.4)] = BLUSH


def front(rig: Rig, ph: float = 0.0, mood: str = "smile", ears=(0.0, 0.0), legs: float = 0.0) -> tuple[dict, set]:
    """앞모습으로 다리를 모으고 선 아기사슴 한 장. legs 는 다리를 늘인 만큼(칸)"""
    feet = 16.0 + legs
    near = []
    for sg in (-1, 1):
        near += leg_parts(f"fl{sg}", (sg * 1.9, 8.6), (sg * 2.3, feet), 0.0, FUR, 0.85, lined=False)
    far = []   # 뒷다리는 그리지 않는다 — 넷에 다리마다 테를 두르면 다리 사이가 메워져 짙은 덩어리가 된다
    chest = ell(0.0, 6.4, 1.6, 2.2)
    parts = head_front(ears) + near + [
        ("fbody", ell(0.0, 7.4, 3.9, 3.3), lambda a, b: CREAM if chest(a, b) else FUR, True)] + far
    out, mask, region = draw(rig, parts)
    face_front(out, rig, mood)
    for a, b in ((-2.4, 7.0), (2.4, 7.0), (-2.0, 9.0), (2.0, 9.0)):
        p = rig.cell(a, b)
        if region.get(p) == "fbody" and out.get(p) != OUT:
            out[p] = SPOT
    return out, mask


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    """다리를 접고 엎드려 왼쪽 위로 고개를 쭉 내민다 — 귀가 쫑긋 앞뒤로, 짧은 꼬리를 팔랑 들어 흰 속"""
    return [finish(clip(arrow_deer(ph))) for ph in phases()]


def wait() -> list[dict]:
    """풀밭에 서서 고개를 숙여 풀을 뜯다가(0–4) 들어 오물오물(5–11) — 귀 한쪽씩 까딱, 꼬리 팔랑"""
    frames = []
    rig = Rig(17.0, 21.4, 0.0, 0.84)
    for k, ph in enumerate(phases()):
        f = {}
        if k < 5:
            down = math.sin(math.pi * min(1.0, k / 2.0) / 2)   # 0 → 1 로 숙인다
        else:
            down = max(0.0, 1.0 - (k - 4) / 2.0)
        neck = (-4.6 - 2.4 * down, -3.6 + 8.6 * down)
        tilt = 70.0 * down
        o, _, _ = side(rig, ph, "blink" if k == 9 else "smile", neck=neck, tilt=tilt,
                       ear=(20.0 if k in (7, 8) else 0.0), chew=(1.0 if k in (6, 8, 10) else 0.0),
                       tail=1.0 if k in (2, 3) else 0.0)
        f.update(o)
        grass(f, 2, 29, 30, k, front=True)
        frames.append(finish(clip(f)))
    return frames


def cross() -> list[dict]:
    """앞모습 얼굴 — 가는 조준선 네 가닥 · 큰 귀를 한쪽씩 쫑긋. 코가 핫스팟"""
    frames = []
    rig = Rig(15.5, 13.6, 0.0, 1.0)
    for k, ph in enumerate(phases()):
        f = {}
        for x in list(range(1, 4)) + list(range(28, 31)):
            f[x, 15] = OUT
        for y in list(range(1, 7)) + list(range(20, 31)):
            f[15, y] = OUT
        e = 24.0 * math.sin(ph)
        out, _, _ = draw(rig, head_front((max(e, 0.0), max(-e, 0.0))))
        f.update(out)
        face_front(f, rig, "blink" if k == 8 else "smile")
        frames.append(finish(f))
    return frames


def hand() -> list[dict]:
    """앞모습으로 선 아기사슴이 오른쪽 귀를 하늘로 곧게 쫑긋 세워 가리킨다 — 귀 끝이 핫스팟. 톡 할 때 귀 끝에
    반짝이 튀고 다른 귀가 파르르"""
    frames = []
    rig = Rig(15.0, 13.0, 0.0, 0.8)
    for k, ph in enumerate(phases()):
        poke = k in (0, 1, 6, 7)
        o, _ = front(rig, ph, "blink" if k in (1, 7) else "smile", ears=(14.0 if poke else 0.0, 72.0), legs=-0.4)
        f = dict(o)
        if poke:
            x, y = top_cell([o])
            for q in ((x - 3, y + 2), (x + 3, y + 2), (x - 2, y), (x + 2, y)):
                f.setdefault(q, HI if k % 2 == 0 else LEAF_L)
        frames.append(finish(clip(f)))
    return frames


def no() -> list[dict]:
    """빨간 금지 표지 안에서 네 다리를 쩍 벌려 버티고(안 갈래) 눈을 질끈 감은 채 고개를 도리도리 — 귀를 뒤로 젖힌다"""
    frames = []
    rig = Rig(16.6, 14.6, 0.0, 0.66)
    brace = (((-7.0, 7.6), 0.3), ((-5.8, 7.8), 0.3), ((6.6, 7.6), -0.4), ((5.6, 7.8), -0.4))
    for k, ph in enumerate(phases()):
        f = {}
        R = 13.5
        ring = {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
        slash = set()
        for t in range(-90, 91):
            x, y = 15.5 + t / 100 * (R - 1.5) * 0.7071, 15.5 + t / 100 * (R - 1.5) * 0.7071
            slash |= disc(x, y, 1.3)
        shake = math.sin(2 * ph)
        o, _, _ = side(rig, ph, "blink", neck=(-4.0 + 0.6 * shake, -3.4), tilt=12.0 + 14.0 * shake,
                       legs=brace, flat=0.8)
        solid(f, ring | slash, SIGN, SIGN_D)
        f.update({p: c for p, c in o.items() if p not in f or (p[0] - p[1]) ** 2 > 4})   # 사슴이 사선 앞, 고리 위
        frames.append(finish(f))
    return frames


def move() -> list[dict]:
    """네 다리를 꼿꼿이 편 채 제자리에서 통통(사슴의 껑충 뛰기) — 네 방향 풀잎 화살촉이 바깥으로 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy)
        hop = abs(math.sin(ph))
        sp = 0.6 * hop
        legs = (((-4.8 - sp, 9.6), 0.2), ((-2.6 - sp, 9.6), 0.2), ((3.0 + sp, 9.6), -0.2), ((5.4 + sp, 9.6), -0.2))
        o_, _, _ = side(Rig(16.6, 16.0 - 2.0 * hop, 0.0, 0.64), ph, "blink" if k == 4 else "smile",
                        legs=legs, ear=-20.0 * hop, tail=hop, thin=0.7)
        f.update(o_)
        frames.append(finish(f))
    return frames


def stretch(ang: float, fl: bool = False) -> list[dict]:
    """ang 축으로 뛴다 — 앞다리는 앞으로, 뒷다리는 뒤로 쭉 뻗어 앞발굽 · 뒷발굽이 양 끝이고 그 바깥에 풀잎 화살촉.
    ang 은 사슴 a 축(코 → 꼬리)이 화면에서 가리키는 쪽. 다리를 모았다 폈다 한다"""
    frames = []
    t = math.radians(ang)
    ex, ey = math.cos(t), math.sin(t)
    dx, dy = round(ex), round(ey)
    R = 13 if dx == 0 or dy == 0 else 10
    K = 0.7 if dx == 0 or dy == 0 else 0.64
    for k, ph in enumerate(phases()):
        f = {}
        d = math.sin(ph)                       # + 면 쭉 폄
        for sg in (-1, 1):
            o = 1 if d > 0.3 else 0
            chevron(f, 15 + sg * dx * (R + o), 15 + sg * dy * (R + o), sg * dx, sg * dy)
        reach = 1.0 + 0.8 * d
        legs = (((-9.0 - 1.4 * reach, 4.4), -0.2), ((-8.0 - 1.4 * reach, 5.6), -0.2),
                ((9.6 + 1.4 * reach, 3.6), 0.3), ((8.6 + 1.4 * reach, 4.8), 0.3))
        if dx and dy:   # 사선은 앞다리를 배 밑에 접는다 — 넷을 다 뻗으면 돌린 몸에서 다리가 사방으로 뻗쳐 엉킨다
            legs = (((-3.0, 4.2), 3.6), ((-2.0, 4.4), 3.6)) + legs[2:]
        rig = Rig(15.5, 15.5, ang, K, fl)
        o_, _, _ = side(rig, ph, "blink" if k == 3 else "smile", neck=(-6.4, -3.6), tilt=-10.0,
                        legs=legs, ear=-25.0, tail=1.0, thin=0.75)
        f.update(o_)
        frames.append(finish(f))
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
    """네 발로 서서 목을 하늘로 쭉 뻗어 머리 위 나뭇잎을 뜯는다 — 위로 든 코끝이 핫스팟"""
    frames = []
    rig = Rig(16.0, 19.0, 0.0, 0.84)
    for k, ph in enumerate(phases()):
        f = {}
        for x in range(20, 31):                       # 오른쪽에서 뻗어 든 잔가지
            f[x, 7 + (x - 20) // 4] = BARK_D
        sway = 1 if k % 6 < 3 else 0
        leaf_glyph(f, 19 + sway, 7)
        leaf_glyph(f, 24, 9 - sway)
        o, _, _ = side(rig, ph, "blink" if k == 5 else "smile", neck=(-4.8, -7.4), tilt=-80.0,
                       chew=1.0 if k % 3 == 1 else 0.0, ear=10.0, tail=1.0 if k in (8, 9) else 0.0)
        f.update(o)
        grass(f, 2, 29, 30, k, front=True)
        frames.append(finish(clip(f)))
    return frames


def ibeam() -> list[dict]:
    """앞모습으로 다리를 모으고 꼿꼿이 선 아기사슴 — 옆으로 쫙 편 귀가 I 의 위 가로획, 발굽 밑 풀줄이 아래 가로획"""
    frames = []
    rig = Rig(15.5, 6.4, 0.0, 0.78)
    for k, ph in enumerate(phases()):
        f = {}
        e = 8.0 if k in (3, 9) else -8.0 if k in (4, 10) else 0.0     # 귀를 파르르
        o, _ = front(rig, ph, "blink" if k == 6 else "smile", ears=(e, e), legs=9.2)   # 긴 다리가 I 의 기둥
        f.update(o)
        for x in range(8, 24):
            f[x, 29] = LEAF_D
            f.setdefault((x, 28), LEAF if x % 3 else LEAF_L)
        frames.append(finish(clip(f)))
    return frames


TIP_ = (1, 29)   # 잔가지 끝(화면)


def pen() -> list[dict]:
    """잔가지를 입에 물고 땅에 글씨를 쓴다 — 잔가지 끝이 핫스팟. 고개를 까딱인다"""
    frames = []
    base = Rig(21.6, 14.6, 0.0, 0.8)
    for k, ph in enumerate(phases()):
        f = {}
        nod = 5.0 * math.sin(2 * ph)
        neck, tilt = (-5.6, 0.4), 46.0 + nod
        hx_ = head_xf(neck, tilt)                    # 입 자리를 먼저 구해 거기서 잔가지 끝까지 긋는다
        mx, my = base.world(*hx_.up(2.6, 1.6))
        far = (mx + (mx - TIP_[0] - 0.5) * 0.18, my + (my - TIP_[1] - 0.5) * 0.18)
        twig = ("twig", bar(base.local(TIP_[0] + 0.5, TIP_[1] + 0.5), base.local(*far), 0.6, 0.8), BARK, True)
        o, _, _ = side(base, ph, "blink" if k == 4 else "smile", neck=neck, tilt=tilt,
                       mouth=(twig,), tail=1.0 if k in (2, 3) else 0.0)
        f.update(o)
        f[TIP_] = BARK_D
        for x in range(3, 9):                       # 땅에 쓴 글씨 자국
            if (x + k) % 3:
                f.setdefault((x, 30), PRINT)
        frames.append(finish(clip(f)))
    return frames


def busy() -> list[dict]:
    """작은 화살표 사슴 + 오른쪽 아래 큰 광대버섯 둘레의 요정 고리 — 작은 버섯 여덟이 차례로 쑥 돋는다"""
    frames = []
    cx, cy = 21.5, 21.0
    for k, ph in enumerate(phases()):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            lag = (head - i) % 8
            up_ = 1 if lag < 1 else 0
            al = 255 if lag < 1 else 0xc0 if lag < 2 else 0x60
            x, y = math.floor(cx + 6.8 * math.cos(a) - 2.0), math.floor(cy + 6.8 * math.sin(a) - 2.5) - up_
            mush_glyph(f, x, y, al)
        cap = {p for p in disc(cx, cy + 0.6, 4.4) if p[1] + 0.5 <= cy + 0.6}       # 둥근 갓(반달)
        stem = raster([(cx - 1.5, cy), (cx + 1.5, cy), (cx + 1.8, cy + 4.0), (cx - 1.8, cy + 4.0)])
        solid(f, stem, STEM)
        solid(f, cap, MUSH)
        for p in ((21, 17), (19, 19), (23, 19)):
            f[p] = SPOT
        f.update(arrow_deer(ph, small=True))
        frames.append(finish(clip(f)))
    return frames


def help_() -> list[dict]:
    """작은 화살표 사슴 + 황갈색 털에 흰 점이 박힌 물음표(점은 버섯) — 흰 점이 차례로 반짝인다"""
    frames = []
    cells = [(17.6 + 2.2 * i, 11.6 + 2.2 * j) for j, row in enumerate(QMARK[:-1]) for i, ch in enumerate(row)
             if ch == "#"]
    for k, ph in enumerate(phases()):
        f = {}
        m = set()
        for x, y in cells:
            m |= disc(x, y, 2.0)
        solid(f, m, FUR, OUT)
        for i, (x, y) in enumerate(cells[::2]):
            lit = (k * len(cells[::2]) / N - i) % len(cells[::2]) < 1.2
            f[math.floor(x), math.floor(y)] = HI if lit else SPOT
            if lit:
                f[math.floor(x) - 1, math.floor(y)] = SPOT
        mush_glyph(f, 20, 25 - (1 if k % 6 < 2 else 0))
        f.update(arrow_deer(ph, small=True))
        frames.append(finish(clip(f)))
    return frames


def person() -> list[dict]:
    """작은 화살표 사슴 + 사람 아이콘이 옆에 선 아기사슴 머리를 쓰다듬는다 — 사슴이 눈을 감고 꼬리를 팔랑"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        rig = Rig(24.0, 17.0, 0.0, 0.56)
        pat = abs(math.sin(ph))
        hand_ = (-7.4, 0.6 + 1.6 * pat)
        parts = [("hand", ell(*hand_, 1.8, 1.6), SKIN, True), ("sleeve", bar((-5.0, 9.0), hand_, 1.7), SHIRT, False),
                 ("hair", ell(0.0, -2.4, 5.2, 3.4), HAIR, True),
                 ("face", ell(0.0, 0.4, 4.8, 4.6), SKIN, True),
                 ("torso", ell(0.0, 13.0, 8.0, 6.6), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
        o, _, _ = draw(rig, parts)
        for sg in (-1, 1):
            x, y = rig.cell(sg * 2.0, 0.6)
            o[x, y] = o[x, y + 1] = EYE
            o[rig.cell(sg * 3.2, 2.6)] = BLUSH
        fawn, _, _ = side(Rig(13.6, 22.6 + 0.6 * pat, 0.0, 0.5), ph, "blink" if pat > 0.5 else "smile",
                          neck=(-4.0, -4.4), tilt=-8.0, flat=0.5 * pat, tail=1.0 if k % 6 in (2, 3) else 0.0)
        f.update(fawn)
        f.update({p: c for p, c in o.items() if p[1] <= 30})
        grass(f, 3, 29, 30, k, front=True)
        f.update(arrow_deer(ph, small=True))
        frames.append(finish(clip(f)))
    return frames


def pin() -> list[dict]:
    """작은 화살표 사슴 + 풀밭에 발굽 자국이 하나씩 찍히며 빨간 지도 핀까지 이어진다. 핀이 통통 튄다 —
    핀 동그라미 속에는 나뭇잎"""
    frames = []
    trail = [(3, 25), (8, 22), (12, 25), (17, 22)]
    for k in range(N):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 24.5, 14.0 + dy
        grass(f, 2, 29, 30, k, front=True)
        for x, y in trail[:1 + k // 3]:
            glyph_at(f, HOOF_G, {"#": PRINT}, x, y)
        solid(f, disc(cx, cy, 4.6) | raster([(cx - 3.2, cy + 2.4), (cx + 3.2, cy + 2.4), (cx, cy + 12.5)]),
              SIGN, SIGN_D)
        solid(f, disc(cx, cy, 2.6), SPOT, SPOT)
        leaf_glyph(f, math.floor(cx) - 2, math.floor(cy) - 2)   # 발굽 자국을 넣으면 두 눈 달린 유령 얼굴로 읽혀서 잎
        f.update(arrow_deer(2 * math.pi * k / N, small=True))
        frames.append(finish(clip(f)))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def top_cell(fr):
    """장마다 불투명한 칸 중 맨 위 칸(같으면 왼쪽) — 몇 장에만 뜨는 반짝이는 빼고 잡힌다"""
    common = set.intersection(*({p for p, c in f.items() if c[3] == 255} for f in fr))
    return min(common, key=lambda p: (p[1], p[0]))


def ul_cell(fr):
    """장마다 불투명한 칸 중 가장 왼쪽 위(x + y 가 작은) 칸 — 든 발굽 끝"""
    common = set.intersection(*({p for p, c in f.items() if c[3] == 255} for f in fr))
    return min(common, key=lambda p: (p[0] + p[1], p[1]))


def steady(fr):
    """장마다 불투명한 칸 중 판 가운데(15, 15)에 가장 가까운 칸 — 움직이는 사슴이라도 찍는 점이 늘 보이게"""
    common = set.intersection(*({p for p, c in f.items() if c[3] == 255} for f in fr))
    return min(common, key=lambda p: (math.hypot(p[0] - 15, p[1] - 15), p))


HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1),
       "wait": steady, "we": steady, "ns": steady, "nwse": steady, "nesw": steady,
       "no": (15, 15), "cross": (15, 15), "move": steady, "ibeam": steady,
       "pen": TIP_, "hand": top_cell, "up": top_cell}


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

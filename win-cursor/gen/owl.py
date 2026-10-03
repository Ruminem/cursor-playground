# SPDX-License-Identifier: Apache-2.0
"""부엉이(owlanim) 구성표 그림 `art/owlanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/owl.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

'숲속 친구들 · 애니' 묶음(다람쥐 · 고슴도치 · 부엉이)의 한 마리. 해달처럼 칸마다 부엉이가 하는 짓을 따로 그린다(`SCENE`).
치비 비율 — 갈색 달걀 몸 · 머리 위 귀깃 두 뾰족(끝이 갈라진 깃털 — 통짜 세모면 고양이 귀 · 악마 뿔로 읽힌다) ·
크림 얼굴판에 큰 둥근 눈(노란 홍채 + 까만 눈동자 + 흰 반짝) · 작은 주황 부리 · 분홍 볼터치 · 배에 V 무늬.
눈이 얼굴의 주인공이라 몸을 줄여도 눈은 칸 단위 글자판(`EYES`)으로 크게 찍는다 — 같이 줄이면 32칸에서 점이 된다.
해양의 물낯 · 물보라 자리는 숲 소품(나뭇가지 · 나뭇잎 · 도토리)이 대신하고, 금지 칸은 sea.py 의 빨간 표지(SIGN)를 쓴다.

  arrow   나뭇가지 없이 앉은 부엉이가 한쪽 날개를 왼쪽 위로 쭉 뻗는다 — 날개 깃 끝이 핫스팟. 눈은 그 끝을 본다
  busy    작은 화살표 부엉이 + 오른쪽 아래 도토리 둘레를 도는 나뭇잎 여덟 고리
  cross   앞모습 얼굴. 위아래 · 양옆 잔가지가 조준선이고, 두 눈이 가운데(부리 위)를 몰아 본다
  hand    한쪽 날개를 위로 들어 깃 끝으로 콕 — 닿는 순간 눈을 질끈(^^) 감고 끝에 반짝. 깃 끝이 핫스팟
  help    작은 화살표 부엉이가 고개를 빙글 갸웃 + 나뭇잎 물음표(점은 도토리)
  ibeam   위아래 나뭇가지 사이에 길쭉하게 꼿꼿이 선 부엉이 — 가지가 I 의 가로획, 몸이 세로획
  move    날갯짓하며 둥실 뜬 작은 부엉이 + 네 방향 나뭇잎 화살촉
  ns      놀라서 몸을 길쭉하게 늘였다 둥글게 줄였다 하는 부엉이(부엉이의 경계 자세) — 위아래 화살촉
  we      두 날개를 양옆으로 쫙 폈다 접었다 — 날개 끝 너머 양옆 화살촉
  nwse · nesw   날개 하나는 대각 위로, 하나는 대각 아래로 뻗어 그 축으로 늘였다 줄였다 — 양 끝 화살촉
  no      빨간 금지 표지 안에서 두 날개를 가슴 앞에 X 로 엇갈린 부엉이(안 돼!) — 날개가 도리도리 떤다
  pen     깃털 펜을 끌어안은 작은 부엉이 — 펜촉(왼쪽 아래)이 핫스팟. 펜촉을 축으로 살짝 까딱인다
  person  작은 화살표 부엉이 + 사람 아이콘 꼴의 아기 부엉이(동그란 머리 · 넓은 어깨)가 날개를 흔든다
  pin     작은 화살표 부엉이 + 동그라미 속에 부엉이 얼굴이 든 빨간 지도 핀이 통통 튄다
  up      두 날개를 머리 위로 모아 끝을 맞대고 위로 날아오르는 부엉이 — 맞댄 날개 끝이 핫스팟, 발밑으로 바람 줄
  wait    나뭇가지에 앉아 눈을 천천히 끔뻑 — 가운데(얼굴)가 핫스팟. 귀깃이 까딱이고 나뭇잎 하나가 떨어진다

몸은 부위(타원 · 굵기가 변하는 막대 · 다각형)를 부엉이 제 좌표에 놓고 화면으로 돌려 찍는다(`Rig`, `draw` — 해달과 같은 틀).
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, SIGN, SIGN_D, disc, finish, hx, ink, inside, phases, solid, write

SID = "owlanim"

OUT, PUPIL = hx("2f1b10ff"), hx("1a0e08ff")                         # 테두리 · 눈동자
FEATHER, FEATHER_D, FEATHER_L = hx("8a5a36ff"), hx("63401fff"), hx("a8774cff")   # 깃털 · 날개 · 밝은 깃
BELLY, BELLY_V = hx("e6c99cff"), hx("a2714aff")                     # 배 · 배의 V 무늬
FACE, FACE_D, HI = hx("f6e8cdff"), hx("d9b98cff"), hx("fffaf0ff")    # 얼굴판 · 얼굴판 테 · 반짝
IRIS, IRIS_R = hx("f8bf1eff"), hx("c46a12ff")                       # 노란 홍채 · 눈 테(검정 테면 안경으로 읽힌다)
BEAK, BEAK_D, FOOT = hx("f08a24ff"), hx("b85e14ff"), hx("e9a53aff")  # 부리 · 부리 그늘 · 발
BLUSH = hx("f49a9aff")
ink(OUT, HI, hx("f6e9d2c7"))                       # 숲속 친구들 공용 크림 테 (다람쥐·토끼·여우와 같게)
BRANCH, BRANCH_D = hx("7a5230ff"), hx("553820ff")                    # 나뭇가지
LEAF, LEAF_D, LEAF_L = hx("5aa04aff"), hx("3f7a35ff"), hx("86c46aff")   # 나뭇잎 · 풀
ACORN, CAP, ACORN_L = hx("a0662eff"), hx("6b4423ff"), hx("c58a4eff")    # 도토리 · 모자 · 반짝
QUILL, QUILL_D, NIB = hx("f3ead8ff"), hx("c9b597ff"), hx("3a3a3aff")    # 깃털 펜
WIND = (hx("8fa6bcd0"), hx("8fa6bc80"))                                  # 바람 줄(반투명 — 밝은 바탕 · 어두운 바탕 둘 다 보이게)
SHADOW = (hx("3f7a3570"), hx("3f7a35b0"))                                # 핀 그림자(풀빛, 높을수록 옅게)
LEAF_DIM = hx("5aa04a70")                                                # 고리에서 꺼진 잎


# ── 그리개: 부엉이 제 좌표 (a, b) → 화면 (해달과 같은 틀) ───────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도) · 배율 k. a 가 오른쪽, b 가 아래(ang=0)"""

    def __init__(self, ox: float, oy: float, ang: float = 0.0, k: float = 1.0):
        t = math.radians(ang)
        self.ox, self.oy, self.c, self.s, self.k = ox, oy, math.cos(t), math.sin(t), k
        self.ang = ang

    def world(self, a: float, b: float) -> tuple:
        return self.ox + (a * self.c - b * self.s) * self.k, self.oy + (a * self.s + b * self.c) * self.k

    def local(self, x: float, y: float) -> tuple:
        dx, dy = (x - self.ox) / self.k, (y - self.oy) / self.k
        return dx * self.c + dy * self.s, -dx * self.s + dy * self.c

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
    return lambda a, b: inside(pts, a, b)


def any_of(*hs):
    return lambda a, b: any(h(a, b) for h in hs)


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


def glyph(f: dict, rows: list, x0: int, y0: int, pal: dict, only=None) -> None:
    """글자판 rows 를 (x0, y0) 에 찍는다 — pal 에 없는 글자('.')는 안 칠한다. only 를 주면 그 칸들 위에만"""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            p = (x0 + i, y0 + j)
            if ch in pal and (only is None or p in only):
                f[p] = pal[ch]


PAL = {"#": OUT, "r": IRIS_R, "y": IRIS, "p": PUPIL, "h": HI, "f": FEATHER, "c": FACE, "o": BEAK, "d": BEAK_D, "b": BLUSH,
       "a": ACORN, "k": CAP, "l": ACORN_L, "g": LEAF, "G": LEAF_D, "L": LEAF_L, "F": FOOT}

# 눈 글자판 — 큰 것(6×6, 몸 k ≥ 0.8)과 작은 것(4×4). 눈동자 2×2 는 gaze 로 한 칸 옮긴다(`eye`)
EYES = {
    "big": {"open": [".yyyy.", "yyyyyy", "yyyyyy", "yyyyyy", "yyyyyy", ".yyyy."],
            "half": [".####.", "#ffff#", "######", "yyyyyy", "yyyyyy", ".yyyy."],
            "shut": ["......", "......", "#....#", ".####.", "......", "......"],
            "happy": ["......", ".####.", "#....#", "......", "......", "......"],
            "wide": [".rrrr.", "ryyyyr", "ryyyyr", "ryyyyr", "ryyyyr", ".rrrr."]},
    "small": {"open": [".yy.", "yyyy", "yyyy", ".yy."],
              "half": [".##.", "####", "y..y", ".yy."],
              "shut": ["....", "#..#", ".##.", "...."],
              "happy": [".##.", "#..#", "....", "...."],
              "wide": [".yy.", "yyyy", "yyyy", ".yy."]},
}


def eye(f: dict, cx: float, cy: float, size: str, mood: str, gaze=(0, 0), sg: int = -1) -> None:
    """가운데 (cx, cy)(칸 경계)에 눈 하나. open/half 면 눈동자 2×2(왼쪽 위 흰 반짝)를 gaze 만큼 옮겨 찍는다"""
    rows = EYES[size][mood]
    w = len(rows[0])
    x0, y0 = round(cx - w / 2), round(cy - w / 2)
    glyph(f, rows, x0, y0, PAL)
    if mood in ("open", "half"):
        n = 3 if size == "big" else 2                     # 눈동자 한 변
        if size == "big":   # 6칸 눈에 3칸 눈동자는 가운데가 없다 — 가만히 볼 땐 안쪽 아래(살짝 몰린 눈)
            px = x0 + {-1: 1, 0: 2 if sg < 0 else 1, 1: 2}[gaze[0]]
            py = y0 + {-1: 1, 0: 2, 1: 2}[gaze[1]]
        else:
            px, py = x0 + 1 + gaze[0], y0 + 1 + gaze[1]
        top = y0 + (3 if size == "big" else 2) if mood == "half" else py
        for dx in range(n):
            for dy in range(n):
                if py + dy >= top:
                    f[px + dx, py + dy] = PUPIL
        if mood == "open":
            f[px, py] = HI
    if mood == "wide":   # 놀란 눈 — 작은 눈동자 한 칸
        f[x0 + w // 2 - 1 + (gaze[0] > 0), y0 + w // 2 - 1 + (gaze[1] > 0)] = PUPIL


# ── 부엉이 앞모습: a 가로(+오른쪽), b 세로(+아래), 원점은 몸 가운데 ─────────────────────────────
EYE_B = -4.6                     # 눈 줄 높이
SHOULDER = (5.6, 0.6)            # 날개 밑동(오른쪽, 왼쪽은 a 를 뒤집는다)


def tufts(sx: float = 1.0, sy: float = 1.0):
    """귀깃 둘 — 끝이 두 갈래인 깃털 다발. 통짜 세모면 고양이 귀 · 악마 뿔로 읽힌다. sx 는 바깥으로 벌린 정도,
    sy 는 세운 정도(작으면 뒤로 눕힌다)"""
    hs = []
    for sg in (-1, 1):
        pts = [(sg * 2.4, -10.4), (sg * 5.4 * sx, -10.4 - 4.4 * sy), (sg * 6.4 * sx, -10.4 - 2.5 * sy),
               (sg * 8.0 * sx, -10.4 - 3.8 * sy), (sg * 8.8, -5.6)]
        hs.append(poly(pts))
    return any_of(*hs)


def wing_part(sg: int, tip, width: float = 0.34, kx: float = 1.0, ky: float = 1.0, k: float = 1.0):
    """펼친 날개 하나 — 어깨에서 깃 끝으로 가늘어지고, 뒷날(몸에서 먼 쪽)은 첫째 날개깃 셋이 톱니로 갈라진다.
    통짜 막대면 막대기 · 지팡이로 읽힌다. 밑동은 밝은 깃(덮깃), 바깥은 짙은 날개깃, 앞날에 밝은 줄.
    폭은 길이에 비례하되 화면에서 밑동이 5칸은 되게 — 작은 부엉이의 짧은 날개는 비율대로면 실 한 가닥이다"""
    sh = (sg * SHOULDER[0] * kx, SHOULDER[1] * ky)
    ex, ey = tip[0] - sh[0], tip[1] - sh[1]
    L = math.hypot(ex, ey) or 1.0
    ux, uy = ex / L, ey / L
    nx, ny = sg * uy, -sg * ux        # 앞날 쪽 — 옆으로 편 날개면 위. 뒷날(톱니)은 -n
    W = max(width, 5.0 / (1.05 * L * k))
    uv = [(-0.06, 0.0), (0.0, W * 0.55), (0.5, W * 0.42), (0.85, W * 0.2), (1.0, 0.0),
          (0.9, -W * 0.22), (0.8, -W * 0.12), (0.74, -W * 0.38), (0.63, -W * 0.22), (0.55, -W * 0.5),
          (0.44, -W * 0.32), (0.34, -W * 0.55), (0.0, -W * 0.5)]
    pts = [(sh[0] + (u * ux + v * nx) * L, sh[1] + (u * uy + v * ny) * L) for u, v in uv]
    hit = poly(pts)

    def col(a, b):
        u = ((a - sh[0]) * ux + (b - sh[1]) * uy) / L
        v = ((a - sh[0]) * nx + (b - sh[1]) * ny) / L
        if u < 0.36:
            return FEATHER
        return FEATHER_L if v > W * 0.42 * (1.0 - u) * 1.4 - 0.02 else FEATHER_D
    return (f"wing{sg}", hit, col, True)


NECK = (0.0, 1.5)                # 머리를 키우고 돌리는 축


def owl(rig: Rig, wings=(None, None), mood="open", gaze=(0, 0), tilt=0.0, squash=(1.0, 1.0), feet=True,
        front=(), back=(), blush=True, eyes=None, tsx=1.0, tsy=1.0) -> tuple[dict, set]:
    """앞모습 부엉이 한 장. wings 는 (왼쪽, 오른쪽) 날개: None 이면 몸 옆에 접고, (a, b) 면 그 깃 끝으로 몸 뒤에서 편다,
    ("front" 또는 "back", (a, b), 폭) 이면 몸 앞 · 뒤로(앞이면 엇갈린 X · 끌어안기). gaze 가 "in" 이면 두 눈이 가운데로 몰린다.
    mood 는 눈(open · half · shut · happy · wide), gaze 는 눈동자를 옮길 칸,
    tilt 는 고개를 갸웃한 각도(도, 목을 축으로 머리만 돈다), squash 는 (가로, 세로) 늘림(놀라서 길쭉해진 몸),
    front · back 은 몸 앞 · 뒤에 놓을 부위, eyes 는 눈 크기(big · small, 안 주면 k 로 고른다), tsx 는 귀깃 벌림.
    눈은 칸 단위로 크기가 정해져 있어서 작은 부엉이는 머리를 키운다(hr) — 머리가 몸보다 큰 치비가 되고,
    얼굴판 둘레에 갈색 깃이 남는다(안 키우면 얼굴판이 머리를 다 덮어 병아리 · 햄스터로 읽힌다)"""
    kx, ky = squash
    t = math.radians(tilt)
    ct, st = math.cos(t), math.sin(t)
    size = eyes or ("big" if rig.k * min(kx, 1.0) >= 0.8 else "small")
    off = 3.5 if size == "big" else 2.5                       # 눈 가운데 사이 반(칸) — 두 눈 사이에 얼굴 한 줄
    hr = max(1.0, (off + 3.0) / (rig.k * kx) / 8.6)            # 머리 키움
    k = rig.k * hr                                             # 머리 제 좌표 한 단위가 화면 몇 칸인지(가로)
    fr = (off + (1.3 if size == "big" else 1.0)) / k           # 얼굴판 동그라미 반지름(머리 단위)
    eo = off / k

    def to_head(a, b):   # 몸 좌표 → 머리 제 좌표(늘림 · 갸웃 · 키움을 거꾸로)
        a, b = a / kx, b / ky
        da, db = a - NECK[0], b - NECK[1]
        da, db = da * ct + db * st, -da * st + db * ct
        return NECK[0] + da / hr, NECK[1] + db / hr

    def from_head(a, b):
        da, db = (a - NECK[0]) * hr, (b - NECK[1]) * hr
        da, db = da * ct - db * st, da * st + db * ct
        return (NECK[0] + da) * kx, (NECK[1] + db) * ky

    def head_xf(h):
        return lambda a, b: h(*to_head(a, b))

    def body_xf(h):
        return lambda a, b: h(a / kx, b / ky)

    def face_col(a, b):
        a, b = to_head(a, b)
        depth = max(fr - math.hypot(a - sg * eo, b - EYE_B) for sg in (-1, 1))
        return FACE if depth > 1.0 / k else FACE_D
    face_hit = any_of(ell(-eo, EYE_B, fr, fr), ell(eo, EYE_B, fr, fr), ell(0, EYE_B + fr * 0.55, fr * 0.6, fr * 0.6))
    # 이마의 갈색 V — 얼굴판이 하트 꼴이 되고, 눈 사이 깃이 부엉이 눈썹이 된다
    brow = poly([(-1.6 / k, EYE_B - fr - 1.0), (1.6 / k, EYE_B - fr - 1.0), (0.0, EYE_B - 1.2 / k)])
    belly = ell(0, 5.2, 4.4, 5.0)

    def body_col(a, b):
        return BELLY if belly(a / kx, b / ky) else FEATHER
    ws = [None if w is None else (w[1], w[0] == "front", w[2] if len(w) > 2 else 0.34) if isinstance(w[0], str)
          else (w, False, 0.34) for w in wings]
    parts = list(front)
    for sg, w in zip((-1, 1), ws):
        if w is not None and w[1]:
            parts.append(wing_part(sg, w[0], w[2], kx, ky, rig.k))
    parts += [("brow", head_xf(brow), FEATHER, False),
              ("face", head_xf(face_hit), face_col, False)]
    parts += [("feet", any_of(ell(-2.6, 11.0 * ky, 1.7, 1.1), ell(2.6, 11.0 * ky, 1.7, 1.1)), FOOT, True)] if feet else []
    for sg, w in zip((-1, 1), ws):
        if w is None:
            parts.append((f"fold{sg}", body_xf(ell(sg * 6.6, 3.4, 2.5, 5.4, -sg * 0.18)), FEATHER_D, True))
    parts += [("body", any_of(head_xf(ell(0, -4.0, 8.6, 7.2)), body_xf(ell(0, 4.6, 7.0, 6.6))), body_col, True),
              ("tufts", head_xf(tufts(tsx, tsy)), FEATHER_D, False)]
    for sg, w in zip((-1, 1), ws):
        if w is not None and not w[1]:
            parts.append(wing_part(sg, w[0], w[2], kx, ky, rig.k))
    parts += list(back)
    out, mask, region = draw(rig, parts)

    # 얼굴: 눈 · 부리 · 볼터치는 칸 단위 글자판 — 머리를 돌린 만큼 자리만 돌린다
    def at(a, b):   # 머리 좌표 → 화면(실수)
        return rig.world(*from_head(a, b))
    for sg in (-1, 1):
        cx, cy = at(sg * eo, EYE_B)
        eye(out, cx, cy, size, mood, (-sg, 0) if gaze == "in" else gaze, sg)
        if blush:
            bx, by = at(sg * (eo + (2.6 if size == "big" else 1.9) / k), EYE_B + (2.6 if size == "big" else 1.8) / k)
            for d in ((0, 0), (-sg, 0)) if size == "big" else ((0, 0),):
                p = (math.floor(bx) + d[0], math.floor(by) + d[1])
                if region.get(p) == "face" and out[p] != OUT:
                    out[p] = BLUSH
    bx, by = at(0.0, EYE_B + (3.0 if size == "big" else 2.0) / k)
    x0, y0 = math.floor(bx) - 1, math.floor(by)
    for p, c in (((x0, y0), BEAK), ((x0 + 1, y0), BEAK), ((x0 + 2, y0), BEAK_D), ((x0 + 1, y0 + 1), BEAK_D)):
        out[p] = c
    # 배의 V 무늬
    vs = ((-1.9, 3.4), (1.9, 3.4), (0.0, 5.6), (-1.9, 7.8), (1.9, 7.8)) if rig.k >= 0.8 else ((-1.7, 3.8), (1.7, 3.8), (0.0, 6.4))
    for a, b in vs:
        x, y = rig.cell(a * kx, b * ky)
        cells = ((x - 1, y), (x, y + 1), (x + 1, y)) if rig.k >= 0.8 else ((x, y),)
        for p in cells:
            if region.get(p) == "body" and out.get(p) == BELLY:
                out[p] = BELLY_V
    return out, mask


# ── 숲 소품 ──────────────────────────────────────────────────────────────────
LEAF_G = {"r": ["..GG", ".GgG", "GgG.", "GG.."], "l": ["GG..", "GgG.", ".GgG", "..GG"]}
ACORN_G = ["..#..", ".#k#.", "#kkk#", "#lak#", "#aaa#", ".#a#.", "..#.."]


def branch(f: dict, x0: int, x1: int, y: int, leaves=(), k: int = 0) -> None:
    """가로 나뭇가지(4줄: 테 · 밝은 · 짙은 · 테). leaves 는 (x, 위쪽?) 잎 자리 — k 로 살랑인다"""
    m = {(x, y + j) for x in range(x0, x1 + 1) for j in range(4)}
    solid(f, m, lambda p: BRANCH if p[1] == y + 1 else BRANCH_D)
    for i, (x, upside) in enumerate(leaves):
        sway = 1 if (k + 3 * i) % N < N // 2 else 0
        rows = LEAF_G["r" if (i + sway) % 2 else "l"]
        glyph(f, rows, x, y - 3 if upside else y + 3, PAL)


def acorn(f: dict, x0: int, y0: int) -> None:
    glyph(f, ACORN_G, x0, y0, PAL)


# ── 장면 ─────────────────────────────────────────────────────────────────────
def blink_mood(k: int, at: int = 7) -> str:
    """한 바퀴에 한 번 끔뻑 — at 장에 감고 앞뒤 장은 반쯤"""
    return "shut" if k == at else "half" if k in (at - 1, at + 1) else "open"


ARROW_TIP = (0.7, 0.7)                       # 화살표 날개 깃 끝(화면) — (1, 1) 칸을 반 넘게 덮게 칸 밖으로 민다
ARROW = (19.5, 19.0, 0.82)                   # 화살표 부엉이 몸 가운데 · 배율
ARROW_S = (9.5, 12.4, 0.5)                   # 작은 화살표 부엉이 (busy · help · person · pin)


def arrow_owl(ph: float, small: bool = False, tilt: float = 0.0, mood=None) -> dict:
    """왼날개를 왼쪽 위로 쭉 뻗은 부엉이. 몸이 살짝 들썩여도 깃 끝은 제자리, 눈은 깃 끝을 본다"""
    ox, oy, kk = ARROW_S if small else ARROW
    k = round(N * ph / (2 * math.pi)) % N
    rig = Rig(ox, oy + (0.0 if small else 0.5 * math.sin(ph)), 0.0, kk)
    out, _ = owl(rig, wings=(rig.local(*ARROW_TIP), None), mood=mood or blink_mood(k, 9),
                 gaze=(0, 0) if tilt else (-1, -1), tilt=tilt, tsx=1.0 + 0.05 * math.sin(2 * ph),
                 eyes="small" if small else None)
    # 작은 부엉이는 날개 최소 폭 때문에 깃 끝 둘레가 (1, 1) 바깥 줄까지 번진다 — 깃 끝이 맨 끝이게 잘라 낸다
    return {p: c for p, c in out.items() if p[0] >= 1 and p[1] >= 1} if small else out


def arrow() -> list[dict]:
    """왼날개를 왼쪽 위로 쭉 — 깃 끝이 핫스팟. 몸이 살짝 들썩이고 귀깃이 까딱인다"""
    return [finish(arrow_owl(ph)) for ph in phases()]


def falling_leaf(f: dict, k: int, x0: float, y0: float, y1: float) -> None:
    """나뭇잎 하나가 좌우로 흔들리며 떨어진다(한 바퀴에 한 번)"""
    t = k / N
    x, y = x0 + 2.0 * math.sin(2 * math.pi * t * 1.5), y0 + (y1 - y0) * t
    glyph(f, LEAF_G["r" if math.cos(2 * math.pi * t * 1.5) > 0 else "l"][1:3], math.floor(x), math.floor(y),
          {"g": LEAF, "G": LEAF_D})


def wait() -> list[dict]:
    """나뭇가지에 앉아 눈을 천천히 끔뻑 — 반쯤 감았다 꼭 감았다 다시 뜬다. 귀깃이 까딱이고 잎 하나가 떨어진다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        mood = "open" if k < 3 else "half" if k in (3, 4, 10, 11) else "shut"
        falling_leaf(f, k, 25.0, 2.0, 18.0)
        o, _ = owl(Rig(15.5, 14.6, 0.0, 0.9), mood=mood, tsx=1.0 + 0.05 * math.sin(ph))
        f.update(o)
        branch(f, 2, 29, 24, leaves=((3, True), (24, False)), k=k)
        frames.append(finish(f))
    return frames


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col) -> None:
    """(dx, dy) 쪽을 가리키는 나뭇잎 화살촉(해달의 물결 화살촉과 같은 꼴). 꼭짓점이 (cx, cy), 바깥 줄이 짙다"""
    px, py = -dy, dx
    for i in range(4):
        for s in (-1, 1):
            for w in (0, 1):
                f[cx - dx * (i + w) + s * px * i, cy - dy * (i + w) + s * py * i] = LEAF_D if w == 0 else col


def diag_chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col) -> None:
    """대각 화살촉 — 꼭짓점 (cx, cy) 에서 두 팔이 가로 · 세로로 뻗는다"""
    for i in range(4):
        for w in (0, 1):
            c = LEAF_D if w == 0 else col
            f[cx - dx * i, cy - dy * w] = c
            f[cx - dx * w, cy - dy * i] = c


def move() -> list[dict]:
    """날갯짓하며 둥실 뜬 작은 부엉이 — 날개가 위아래로 퍼덕이고 몸이 오르내린다. 네 방향 나뭇잎 화살촉"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o) + (1 if dx > 0 else 0) * 0, 15 + dy * (13 + o), dx, dy, LEAF if o else LEAF_L)
        flap = math.sin(2 * ph)
        rig = Rig(15.5, 15.6 - 0.8 * math.sin(2 * ph - 1.0), 0.0, 0.6)
        tips = ((-17.0, -4.0 + 10.0 * flap), (17.0, -4.0 + 10.0 * flap))
        o_, _ = owl(rig, wings=(("back", tips[0], 0.42), ("back", tips[1], 0.42)), mood=blink_mood(k, 4),
                    feet=True)
        f.update(o_)
        frames.append(finish(f))
    return frames


def ns() -> list[dict]:
    """놀란 부엉이 — 몸을 길쭉하게 늘여(귀깃을 곧추세우고 눈을 휘둥그레) 섰다가 동그랗게 줄어든다. 위아래 화살촉"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        s = 0.5 + 0.5 * math.sin(ph)                 # 1 이면 길쭉
        tall = s > 0.6
        for sg in (-1, 1):
            chevron(f, 15, 15 + sg * (13 + (1 if tall else 0)), 0, sg, LEAF_L if tall else LEAF)
        o_, _ = owl(Rig(15.5, 16.0, 0.0, 0.62), squash=(1.08 - 0.3 * s, 0.9 + 0.32 * s), mood="wide" if tall else "open",
                    tsx=1.0 - 0.25 * s)
        f.update(o_)
        frames.append(finish(f))
    return frames


def we() -> list[dict]:
    """두 날개를 양옆으로 쫙 폈다 조금 접었다 — 날개 끝 너머 양옆 화살촉"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        s = 0.5 + 0.5 * math.sin(ph)
        for sg in (-1, 1):
            chevron(f, 15 + (1 if sg > 0 else 0) + sg * (13 + (1 if s > 0.6 else 0)), 15, sg, 0, LEAF_L if s > 0.6 else LEAF)
        rig = Rig(15.5, 17.0, 0.0, 0.6)
        L = 14.5 + 3.0 * s    # 날개는 몸통 높이로 — 어깨 높이면 큰 머리에 가려 끝만 보인다
        o_, _ = owl(rig, wings=(("back", (-L, 3.0), 0.4), ("back", (L, 3.0), 0.4)), mood=blink_mood(k, 3))
        f.update(o_)
        frames.append(finish(f))
    return frames


def diag(flip: bool) -> list[dict]:
    """날개 하나는 대각 위로, 하나는 대각 아래로 뻗어 그 축으로 늘였다 줄였다 — 양 끝 대각 화살촉.
    flip 이면 오른쪽 위 · 왼쪽 아래(nesw)"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        s = 0.5 + 0.5 * math.sin(ph)
        o = 1 if s > 0.6 else 0
        c = LEAF_L if o else LEAF
        if flip:
            diag_chevron(f, 28 + o, 2 - o, 1, -1, c)
            diag_chevron(f, 2 - o, 28 + o, -1, 1, c)
        else:
            diag_chevron(f, 2 - o, 2 - o, -1, -1, c)
            diag_chevron(f, 28 + o, 28 + o, 1, 1, c)
        L = 12.5 + 2.5 * s
        up, down = (-L, -L), (L * 0.95, L * 0.8)
        if flip:
            up, down = (L, -L), (-L * 0.95, L * 0.8)
        wings = (("back", up, 0.4), ("back", down, 0.4)) if not flip else (("back", down, 0.4), ("back", up, 0.4))
        o_, _ = owl(Rig(15.5, 16.2, 0.0, 0.6), wings=wings, mood=blink_mood(k, 5), gaze=(-1, -1) if not flip else (1, -1))
        f.update(o_)
        frames.append(finish(f))
    return frames


def nwse():
    return diag(False)


def nesw():
    return diag(True)


def sign(f: dict) -> None:
    """빨간 금지 표지(고리 + 빗금) — 부엉이 뒤에 깐다"""
    R = 13.5
    ring = {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
    slash = set()
    for t in range(-90, 91):
        x = y = 15.5 + t / 100 * (R - 1.5) * 0.7071
        slash |= disc(x, y, 1.3)
    solid(f, ring | slash, SIGN, SIGN_D)


def no() -> list[dict]:
    """금지 표지 안에서 두 날개를 가슴 앞에 X 로 엇갈린다(안 돼!) — 눈을 질끈 감고 고개를 도리도리"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f)
        j = 0.6 * math.sin(4 * ph)                   # 날개 떨림
        tilt = 9.0 * math.sin(2 * ph)
        wings = (("front", (7.4 + j, 9.6), 0.3), ("front", (-7.4 - j, 9.6), 0.3))
        o_, _ = owl(Rig(15.5, 16.6, 0.0, 0.66), wings=wings, mood="shut" if k % 6 < 4 else "open", tilt=tilt,
                    feet=True)
        f.update({p: c for p, c in o_.items() if 1 <= p[1] <= 30})
        frames.append(finish(f))
    return frames


def cross() -> list[dict]:
    """앞모습 부엉이 — 두 눈 사이가 조준점. 양옆 · 위 잔가지가 조준선이고, 두 눈이 가운데로 몰렸다 풀린다"""
    frames = []
    k_ = 0.8
    rig = Rig(15.5, 15.0 - EYE_B * k_, 0.0, k_)        # 눈 줄이 y=15, 두 눈 사이 줄이 x=15
    for k, ph in enumerate(phases()):
        f = {}
        for x in list(range(1, 7)) + list(range(25, 31)):
            f[x, 15] = BRANCH_D
        for y in range(1, 6):
            f[15, y] = BRANCH_D
        sw = k % 6 < 3
        glyph(f, LEAF_G["r" if sw else "l"][1:3], 1, 13, {"g": LEAF, "G": LEAF_D})
        glyph(f, LEAF_G["l" if sw else "r"][1:3], 27, 13, {"g": LEAF, "G": LEAF_D})
        o_, _ = owl(rig, mood="shut" if k == 8 else "open", gaze="in" if k % 12 < 7 else (0, 0))
        f.update({p: c for p, c in o_.items() if p[1] <= 30})
        frames.append(finish(f))
    return frames


BUSY_C = (22.5, 22.5)


def busy() -> list[dict]:
    """작은 화살표 부엉이 + 오른쪽 아래 도토리 — 둘레를 나뭇잎 여덟이 차례로 밝아지며 돈다"""
    frames = []
    cx, cy = BUSY_C
    for k, ph in enumerate(phases()):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = math.floor(cx + 6.6 * math.cos(a) - 0.5), math.floor(cy + 6.6 * math.sin(a) - 0.5)
            lag = (head - i) % 8
            col = LEAF_L if lag < 1 else LEAF if lag < 2 else LEAF_D if lag < 3 else LEAF_DIM
            for q in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
                f[q] = col
            f[(x, y) if math.cos(a) * math.sin(a) >= 0 else (x + 1, y)] = LEAF_D if lag < 3 else LEAF_DIM   # 잎자루 쪽
        acorn(f, math.floor(cx) - 2, math.floor(cy) - 3)
        f.update(arrow_owl(ph, small=True))
        frames.append(finish(f))
    return frames


QMARK_L = [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..o.."]


def help_() -> list[dict]:
    """작은 화살표 부엉이가 고개를 빙글 갸웃 + 나뭇잎 물음표(점은 도토리) — 잎이 글자 차례로 하나씩 부푼다"""
    frames = []
    cells = [(18.2 + 2.2 * i, 9.6 + 2.2 * j) for j, row in enumerate(QMARK_L) for i, ch in enumerate(row) if ch == "#"]
    for k, ph in enumerate(phases()):
        f = {}
        m = set()
        for i, (x, y) in enumerate(cells):
            d = (k * len(cells) / N - i) % len(cells)
            m |= disc(x, y, 1.2 + (0.5 if d < 1.5 else 0.0))
        solid(f, m, LEAF, LEAF_D)
        acorn(f, 21, 22)
        f.update(arrow_owl(ph, small=True, tilt=28.0 * math.sin(ph), mood="open"))
        frames.append(finish(f))
    return frames


def person() -> list[dict]:
    """작은 화살표 부엉이 + 사람 아이콘 꼴의 아기 부엉이(동그란 머리 · 넓은 어깨)가 날개를 흔든다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        wave = abs(math.sin(ph))
        rig = Rig(22.5, 25.4, 0.0, 0.52)
        o_, _ = owl(rig, wings=(None, (12.0, -8.0 - 6.0 * wave)), mood=blink_mood(k, 6), feet=False,
                    squash=(1.12, 1.0))
        f.update({p: c for p, c in o_.items() if p[1] <= 30})
        f.update(arrow_owl(ph, small=True))
        frames.append(finish(f))
    return frames


def pin() -> list[dict]:
    """작은 화살표 부엉이 + 빨간 지도 핀 동그라미 속 부엉이 얼굴(귀깃 둘이 핀 위로) — 핀이 통통 튀고, 땅에 닿으면 눈을 감는다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 15.0 + dy
        for x in range(19, 27):
            f.setdefault((x, 29), SHADOW[0] if dy else SHADOW[1])
        rig = Rig(cx, cy, 0.0, 1.0)
        ears = ("ears", any_of(poly([(-5.6, -1.0), (-4.6, -8.2), (-3.6, -6.6), (-2.6, -7.6), (-1.4, -3.0)]),
                               poly([(5.6, -1.0), (4.6, -8.2), (3.6, -6.6), (2.6, -7.6), (1.4, -3.0)])), FEATHER_D, False)
        pinp = ("pin", any_of(ell(0, 0, 6.4, 6.4), poly([(-4.6, 3.4), (4.6, 3.4), (0, 12.6)])),
                lambda a, b: SIGN, False)
        face_ = ("face", any_of(ell(-2.5, 0.2, 3.6, 3.6), ell(2.5, 0.2, 3.6, 3.6)), lambda a, b: FACE, True)
        o_, _, _ = draw(rig, [face_, pinp, ears])
        for p, c in list(o_.items()):
            if c == OUT and any(o_.get(q) == SIGN for q in ((p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1))) \
                    and not any(o_.get(q) in (FACE, FEATHER_D) for q in ((p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1))):
                o_[p] = SIGN_D
        mood = "shut" if dy == 0 else "open"
        for sg in (-1, 1):
            eye(o_, cx + sg * 2.5, cy + 0.2, "small", mood, (0, 0), sg)
        o_[math.floor(cx) - 1, math.floor(cy) + 2] = BEAK
        o_[math.floor(cx), math.floor(cy) + 2] = BEAK
        o_[math.floor(cx) + 1, math.floor(cy) + 2] = BEAK_D
        o_[math.floor(cx), math.floor(cy) + 3] = BEAK_D
        f.update(o_)
        f.update(arrow_owl(ph, small=True))
        frames.append(finish(f))
    return frames


def hand() -> list[dict]:
    """한쪽 날개를 위로 들어 깃 끝으로 콕 — 몸이 끝 쪽으로 쑥 다가갔다 물러난다(끝은 제자리). 닿는 순간 눈을 ^^ 감고
    깃 끝에 반짝. 깃 끝이 핫스팟"""
    frames = []
    tipw = (8.3, 0.7)
    for k, ph in enumerate(phases()):
        f = {}
        poke = max(0.0, math.sin(ph))                 # 1 이면 콕
        rig = Rig(18.5 - 0.8 * poke, 19.6 - 1.2 * poke, -6.0 * poke, 0.78)
        o_, _ = owl(rig, wings=(("back", rig.local(*tipw), 0.36), None), mood="happy" if poke > 0.8 else "open",
                    gaze=(-1, -1))
        f.update(o_)
        if poke > 0.8:
            for d in ((-2, 0), (-3, 0), (2, 0), (3, 0), (1, -1)):
                f.setdefault((8 + d[0], 1 + d[1] + (1 if abs(d[0]) == 3 else 0)), IRIS)
        frames.append(finish(f))
    return frames


def ibeam() -> list[dict]:
    """위아래 나뭇가지 사이에 길쭉하게 꼿꼿이 선 부엉이 — 가지가 I 의 가로획, 몸이 세로획. 잎이 살랑, 눈 끔뻑"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        branch(f, 8, 23, 1, leaves=(), k=k)
        branch(f, 8, 23, 26, leaves=(), k=k)
        sw = k % 6 < 3
        glyph(f, LEAF_G["r" if sw else "l"][1:3], 21, 5, {"g": LEAF, "G": LEAF_D})
        glyph(f, LEAF_G["l" if sw else "r"][1:3], 7, 30 - 1, {"g": LEAF, "G": LEAF_D})
        o_, _ = owl(Rig(15.5, 16.4, 0.0, 0.66), squash=(0.78, 1.13), mood=blink_mood(k, 8), tsx=0.85,
                    eyes="small")
        f.update(o_)
        frames.append(finish(f))
    return frames


TIP = (1.5, 29.5)          # 펜촉(화면)
PEN_ANG = -40.0            # 깃털 펜이 누운 각도(도, 펜촉 → 깃 끝)


def quill(rig: Rig, L: float) -> list:
    """깃털 펜 부위 — rig 원점이 펜촉, a 축이 깃 끝 쪽. 펜촉 · 깃대 · 한쪽이 넓은 깃 날개(깃가지 빗금)"""
    def vane(a, b):
        return QUILL_D if (round(a * 0.9 - b * 0.9) % 3 == 0) or abs(b) < 0.5 else QUILL
    return [("nib", bar((0, 0), (3.2, 0), 0.35, 0.9), NIB, True),
            ("vane", any_of(ell(L * 0.62, -0.6, L * 0.4, 2.6), ell(L * 0.75, 0.4, L * 0.25, 2.0)), vane, False),
            ("shaft", bar((2.6, 0), (L, 0), 0.6), QUILL_D, False)]


def pen() -> list[dict]:
    """깃털 펜을 끌어안은 작은 부엉이 — 펜촉을 축으로 살짝 까딱이며 쓴다. 펜촉이 핫스팟"""
    frames = []
    L = 26.0
    for k, ph in enumerate(phases()):
        d = 3.0 * math.sin(2 * ph)
        prig = Rig(TIP[0], TIP[1], PEN_ANG + d, 1.0)
        f, _, _ = draw(prig, quill(prig, L))
        # 부엉이는 펜 몸통(펜촉에서 0.62 L)에 앉아 두 날개로 감싼다
        hx_, hy_ = prig.world(L * 0.5, 0.0)
        orig = Rig(hx_ + 2.5, hy_ - 4.0, 0.0, 0.52)
        o_, _ = owl(orig, wings=(("front", orig.local(*prig.world(L * 0.38, 1.0)), 0.3),
                                 ("front", orig.local(*prig.world(L * 0.52, 1.6)), 0.3)),
                    mood=blink_mood(k, 4), gaze=(-1, 1))
        f.update(o_)
        f[math.floor(TIP[0]), math.floor(TIP[1])] = NIB
        frames.append(finish(f))
    return frames


def up() -> list[dict]:
    """귀깃을 뒤로 눕히고 위로 솟구친다 — 머리가 화살촉 끝, 아래로 내리친 두 날개가 화살촉 날개. 날개가 퍼덕여도 머리는
    제자리라 정수리 가운데가 핫스팟. 몸 둘레로 바람 줄이 흘러내린다.
    처음엔 두 날개를 머리 위로 모아 끝을 맞댔는데 갈색 고깔(마법사 모자 · 크리스마스트리)로 읽혔다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        t = k / N
        for j, x in enumerate((6, 12, 19, 25)):          # 바람 줄
            y = 14 + ((t * 16 + j * 5) % 16)
            for d in range(3):
                if math.floor(y) + d <= 30:
                    f[x, math.floor(y) + d] = WIND[0] if d < 2 else WIND[1]
        flap = 0.5 + 0.5 * math.sin(2 * ph)              # 1 이면 아래로 내리침
        rig = Rig(15.5, 13.5, 0.0, 0.7)
        tips = ((-13.5 - 1.5 * flap, 2.0 + 9.0 * flap), (13.5 + 1.5 * flap, 2.0 + 9.0 * flap))
        o_, _ = owl(rig, wings=(("back", tips[0], 0.4), ("back", tips[1], 0.4)), mood=blink_mood(k, 6), gaze=(0, -1),
                    tsx=1.15, tsy=0.25)
        f.update(o_)
        frames.append(finish({p: c for p, c in f.items() if p[1] <= 30}))
    return frames


def top_cell(fr: list[dict]) -> tuple:
    """맨 위 불투명 칸(같으면 가운데에 가까운 것)"""
    return min((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1], abs(p[0] - 15.5)))


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}
HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1),
       "wait": (15, 15), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (15, 15),
       "pen": (math.floor(TIP[0]), math.floor(TIP[1])), "hand": (8, 1), "up": top_cell}


def check(rid: str, frames: list[dict], hot: tuple) -> None:
    """핫스팟이 장마다 불투명한 칸 위에 있는지"""
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
        if hot == (1, 1) and any(c[3] == 255 and (p[0] < 1 or p[1] < 1) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 깃 끝보다 왼쪽·위로 나온 칸이 있음")


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

# SPDX-License-Identifier: Apache-2.0
"""고슴도치(hedgehoganim) 구성표 그림 `art/hedgehoganim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/hedgehog.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

숲속 친구들(다람쥐 · 고슴도치 · 부엉이) 묶음의 한 마리. 칸마다 고슴도치가 하는 짓을 따로 그린다(`SCENE`).
치비 비율 — 짙은 갈색 가시 덩어리(끝이 밝은 톱니 테) · 크림 얼굴과 배 · 뾰족한 주둥이 끝 까만 코 · 콩알 눈 ·
분홍 볼터치 · 작은 발. 해양 애니의 물낯 · 물보라 자리는 숲 소품(풀 덤불 · 나뭇잎 · 도토리 · 사과)이 대신한다.

  arrow   왼쪽 위로 코를 내민 옆모습 — 까만 코끝이 핫스팟. 발을 종종거리고 코 위로 킁킁 김이 오른다
  busy    작은 화살표 고슴도치 + 오른쪽 아래 데굴데굴 도는 가시 공 둘레를 도토리 여덟 개가 차례로 빛낸다
  cross   조준선 한가운데에 코끝을 대고 킁킁 — 몸은 오른쪽 아래 사분면. 코끝이 핫스팟
  hand    뒷발로 앉아 코끝을 왼쪽 위로 내밀어 콕 — 등 가시에 사과가 꽂혀 있다. 코끝이 핫스팟
  help    작은 화살표 고슴도치 + 나뭇잎으로 찍은 물음표
  ibeam   세로 나뭇가지(위아래 잎이 I 의 가로획)에 옆으로 매달려 앞발로 쥐고 오르내린다. 핫스팟은 가지
  move    공처럼 몸을 만 고슴도치가 제자리에서 데굴데굴 구른다 — 네 방향 풀잎 화살촉
  nesw · ns · nwse · we   몸을 그 축으로 쭉 늘인 옆모습 — 뾰족한 주둥이와 가시 엉덩이가 양 끝이고, 숨 쉬듯
          늘었다 줄었다 하며 양 끝 풀잎 화살촉이 두근댄다
  no      빨간 금지 표지 안에서 공처럼 몸을 말고 가시를 세웠다 가라앉힌다 — 말린 틈으로 코끝과 눈이 빼꼼
  pen     뒷발로 서서 뽑은 가시 하나를 깃펜처럼 쥔 고슴도치 — 가시 끝(왼쪽 아래)이 핫스팟
  person  작은 화살표 고슴도치 + 고슴도치를 품에 안은 사람 아이콘 — 안긴 고슴도치가 킁킁
  pin     작은 화살표 고슴도치 + 빨간 지도 핀 머리에 올라탄 고슴도치가 핀과 같이 통통 튄다
  up      풀 줄기를 타고 오르는 옆모습 — 하늘로 든 코끝이 핫스팟, 줄기 잎이 아래로 흘러간다
  wait    풀숲 도토리 앞에서 코를 들썩이며 킁킁 — 가운데(몸)가 핫스팟

몸은 부위(타원 · 굵기가 변하는 막대 · 톱니 가시 덩어리)를 고슴도치 제 좌표에 놓고 화면으로 돌려 찍는다(`Rig`, `draw`).
옆모습(`side`) · 공처럼 만 모습(`ball`) 두 벌이다. 앞모습은 갈색 가시가 단발머리로 읽혀 사람 얼굴이 돼서 버렸다. 가시 덩어리(`burr`)만으로는 밤송이 · 성게로 읽히니
어느 칸이든 얼굴(코 · 눈)이 보이게 한다 — 만 공에도 크림 얼굴 조각과 코끝을 남긴다.
빌드가 부르지 않고 손으로 돌린다 · 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, disc, finish, hx, ink, phases, raster, solid, write

SID = "hedgehoganim"

OUT, EYE, HI = hx("2a1a10ff"), hx("1a0e08ff"), hx("fffaf0ff")                  # 테두리 · 눈코 · 반짝
SPINE, SPINE_D, SPINE_M, SPINE_L = hx("5c3b22ff"), hx("3e2716ff"), hx("7c5434ff"), hx("dcc08eff")   # 가시 · 끝
CREAM, CREAM_D, BLUSH = hx("f4e2c4ff"), hx("dcc39aff"), hx("f49a9aff")         # 얼굴 · 배 그늘 · 볼터치
FEET, EAR = hx("d4927aff"), hx("c98a72ff")                                     # 발 · 귀
ink(OUT, HI, hx("f6e9d2c7"))                       # 숲속 친구들 공용 크림 테 (다람쥐·토끼·여우와 같게)
GRASS, GRASS_D, GRASS_L = hx("5aa04aff"), hx("3f7a35ff"), hx("86c46aff")      # 풀 · 나뭇잎
ACORN, ACORN_L, CAP, CAP_D = hx("a0662eff"), hx("c88a4eff"), hx("6b4423ff"), hx("4a2e16ff")   # 도토리
APPLE, APPLE_D, APPLE_L = hx("d9443aff"), hx("a52f28ff"), hx("f08a7aff")
TWIG, TWIG_D = hx("8a6a44ff"), hx("5e4628ff")
SHIRT, SHIRT_D = hx("4a7fb5ff"), hx("2e5a88ff")
PUFF = hx("ffffffa0")                                                         # 킁킁 김


# ── 그리개: 고슴도치 제 좌표 (a, b) → 화면 ────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도, a 축이 화면에서 가리키는 쪽, 90 이 아래) · 배율 k.
    b 축은 a 축을 시계 방향으로 90도 돌린 쪽(ang=0 이면 a 가 오른쪽, b 가 아래)"""

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


def burr(ca, cb, ra, rb, n, amp, gate=None, skew=0.0, turn=0.0):
    """톱니 가시 덩어리 → (맞음, 색). 타원 (ca, cb, ra, rb) 둘레에 가시 n 개(한 바퀴 기준)가 amp 배 길이로 솟는다.
    gate(θ) 가 거짓인 쪽(배 · 얼굴 쪽)은 가시 없이 매끈하다. skew 는 가시가 뒤로 눕는 정도, turn 은 가시 줄을
    돌린 각(구르는 공). 색은 가시 끝이 밝고(`SPINE_L`), 속은 가시 줄을 따라 짙고 옅은 결이 진다"""
    def geo(a, b):
        da, db = (a - ca) / ra, (b - cb) / rb
        rho, th = math.hypot(da, db), math.atan2(db, da)
        t = (th + turn) * n / (2 * math.pi) + skew * rho
        tri = 1 - abs(2 * (t % 1) - 1)
        lim = 1 + amp * tri if (gate is None or gate(th)) else 1.0
        return rho, lim, t

    def hit(a, b):
        rho, lim, _ = geo(a, b)
        return rho <= lim

    def col(a, b):
        rho, lim, t = geo(a, b)
        if rho > 1.0 - 0.06 and lim > 1.0 + amp * 0.35:
            return SPINE_L
        f = (t + 0.5) % 1
        if rho > 0.35 and abs(f - 0.5) < 0.16:
            return SPINE_M
        return SPINE
    return hit, col


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


def eye(f: dict, rig: Rig, a: float, b: float, big: bool = True, shut: bool = False) -> None:
    """콩알 눈 — 화면 칸 2×2(big) 의 왼쪽 위가 흰 반짝, 아니면 한 칸. shut 이면 감은 눈 가로 두 칸"""
    x, y = rig.cell(a, b)
    if shut:
        f[x, y + (1 if big else 0)] = EYE
        f[x + 1, y + (1 if big else 0)] = EYE
        return
    if big:
        f[x, y], f[x + 1, y], f[x, y + 1], f[x + 1, y + 1] = HI, EYE, EYE, EYE
    else:
        f[x, y] = EYE


def clip(f: dict) -> dict:
    return {p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}


# ── 옆모습: a 는 코끝 0 → 엉덩이, b 는 + 가 배(발) 쪽 ───────────────────────────
def side(rig: Rig, step: float = 0.0, sniff: float = 0.0, shut: bool = False, stretch: float = 1.0,
         extra=(), big_eye: bool = True, turn: float = 0.0) -> tuple[dict, set]:
    """옆모습 고슴도치 한 장. 코끝이 원점 근처. step 은 앞뒤 발이 엇갈린 정도(-1–1), sniff 는 코를 든 정도(0–1),
    stretch 는 머리 뒤 몸(가시 · 배 · 뒷발)을 a 축으로 늘인 배율, extra 는 몸 앞에 놓을 부위, turn 은 가시 결을
    살짝 흔드는 각. 가시는 이마부터 엉덩이까지 등 쪽에만 솟고 배 · 얼굴 쪽은 매끈하다"""
    S = stretch

    def ax(a):   # 머리(a≈8) 뒤를 늘인다
        return 8.0 + (a - 8.0) * S
    nose_b = 0.2 - 0.9 * sniff
    n = max(9, min(13, round(15 * rig.k)))   # 작게 그려도 가시가 두 칸 넘게 솟게(앞모습과 같은 까닭)
    hit_sp, col_sp = burr(ax(15.5), -1.2, 7.4 * S, 6.6, round(n * (0.6 + 0.4 * S)), max(0.32, 2.2 / (7.4 * rig.k)),
                          gate=lambda th: -2.6 < th < 0.9, skew=0.35, turn=turn)
    feet = any_of(ell(9.4 + 0.9 * step, 6.0, 1.4, 1.0), ell(ax(18.5) - 0.9 * step, 6.0, 1.5, 1.0))

    def head(a, b):
        return CREAM_D if b > 3.0 else CREAM
    parts = [("nose", ell(0.9, nose_b, 1.1, 1.0), EYE, False)] + list(extra) + [
        ("feet", feet, FEET, True),
        ("snout", bar((1.6, nose_b + 0.2), (5.5, 1.4), 0.9, 3.0), CREAM, False),
        ("head", ell(8.6, 0.6, 5.4, 4.8), head, True),
        ("ear", ell(11.4, -3.7, 1.4, 1.4), EAR, True),
        ("belly", ell(ax(15.0), 3.8, 6.0 * S, 2.2), CREAM_D, False),
        ("spines", hit_sp, col_sp, False)]
    out, mask, _ = draw(rig, parts)
    eye(out, rig, 6.6, -1.0, big_eye, shut)
    dot(out, rig, 9.0, 1.9, BLUSH)
    if big_eye:
        dot(out, rig, 9.9, 1.5, BLUSH)
    return out, mask


ARROW = Rig(1.4, 1.3, 47.0, 0.98)     # 화살표 고슴도치: 코끝이 (1, 1)
ARROW_S = Rig(1.4, 1.3, 47.0, 0.64)   # 작은 화살표 고슴도치 (busy · help · person · pin)


def arrow_hog(k: int, small: bool = False) -> dict:
    ph = 2 * math.pi * k / N
    return side(ARROW_S if small else ARROW, step=math.sin(2 * ph), shut=(k == 7), big_eye=True,
                turn=0.05 * math.sin(ph))[0]


# ── 공처럼 만 모습: 원점이 공 가운데 ─────────────────────────────────────────────
def ball(rig: Rig, R: float = 8.0, puff: float = 1.0, peek: bool = True, shut: bool = False) -> tuple[dict, set]:
    """몸을 공처럼 만 고슴도치 — 가시가 둘레를 다 덮고 왼쪽 아래 말린 틈으로 크림 얼굴 조각 · 까만 코끝 · 눈이
    빼꼼 보인다(얼굴이 안 보이면 밤송이 · 성게다). 구르는 것은 rig 의 각으로 돌린다. puff 는 가시가 선 정도"""
    hit_sp, col_sp = burr(0.0, 0.0, R, R, 16, 0.3 * puff, gate=lambda th: not (1.7 < th < 3.0), skew=0.2)
    fa = math.radians(135)                       # 얼굴 조각 쪽(왼쪽 아래)
    fc = (math.cos(fa) * R * 0.62, math.sin(fa) * R * 0.62)
    nose = (math.cos(fa) * R * 1.0, math.sin(fa) * R * 1.0)
    parts = [("nose", ell(*nose, 1.0, 1.0), EYE, False),
             ("feet", any_of(ell(R * 0.15, R * 0.92, 1.3, 1.0), ell(-R * 0.98, -R * 0.05, 1.0, 1.3)), FEET, True),
             ("face", ell(*fc, R * 0.52, R * 0.36, fa + math.pi / 2 - 0.25), CREAM, True),
             ("spines", hit_sp, col_sp, False)]
    out, mask, _ = draw(rig, parts)
    if peek:
        eye(out, rig, fc[0] + 0.6, fc[1] - 1.6, big=rig.k * R > 6.5, shut=shut)
        dot(out, rig, fc[0] + 1.6, fc[1] + 1.1, BLUSH)
    return out, mask


# ── 숲 소품 ──────────────────────────────────────────────────────────────────
ACORN_ART = ["..s.", ".cc.", "cCCc", "aaaa", "aAaa", ".aa."]
APPLE_ART = ["..sl", ".rr.", "rLrr", "rrrr", "rrrd", ".rd."]
LEAF_ART = ["..g", ".lg", "lgg", "g.."]
SPRITE = {"s": CAP_D, "c": CAP, "C": CAP_D, "a": ACORN, "A": ACORN_L, "r": APPLE, "L": APPLE_L, "d": APPLE_D,
          "l": GRASS_L, "g": GRASS}


def sprite(f: dict, rows: list, x0: int, y0: int, outline: bool = True) -> None:
    """작은 글자판 그림. outline 이면 둘레에 테두리 한 칸"""
    cells = {(x0 + i, y0 + j): SPRITE[ch] for j, row in enumerate(rows) for i, ch in enumerate(row) if ch != "."}
    if outline:
        for (x, y) in list(cells):
            for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if q not in cells:
                    f[q] = OUT
    f.update(cells)


def tuft(f: dict, x0: int, x1: int, y: int, k: int = 0) -> None:
    """풀 덤불: y 줄을 밑동으로 높이가 들쭉날쭉한 풀잎. k 로 잎끝이 살랑인다"""
    for x in range(x0, x1 + 1):
        h = (2, 3, 1, 4, 2, 3, 1)[(x * 3) % 7]
        for j in range(h):
            f[x, y - j] = GRASS_D if j == 0 else GRASS if j < h - 1 else GRASS_L
        if h >= 3 and (x + k) % 4 == 0:   # 바람에 잎끝이 옆으로
            f.pop((x, y - h + 1), None)
            f[x + 1, y - h + 1] = GRASS_L


ACORN_SMALL = [".s.", "ccc", "aaa", ".a."]


def acorn(f: dict, x0: int, y0: int, alpha: int = 255) -> None:
    """3×4 도토리(모자 · 꼭지). alpha 가 255 면 반짝 한 칸, 낮으면 반투명으로 흐리게(도는 고리의 꼬리)"""
    for j, row in enumerate(ACORN_SMALL):
        for i, ch in enumerate(row):
            if ch != ".":
                c = SPRITE[ch]
                f[x0 + i, y0 + j] = c[:3] + (alpha,)
    if alpha == 255:
        f[x0, y0 + 2] = ACORN_L


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col) -> None:
    """(dx, dy) 쪽을 가리키는 풀잎 화살촉. 꼭짓점이 (cx, cy)"""
    px, py = -dy, dx
    for i in range(4):
        for s in (-1, 1):
            for w in (0, 1):
                f[cx - dx * (i + w) + s * px * i, cy - dy * (i + w) + s * py * i] = col


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    """왼쪽 위로 코를 내밀고 종종 — 앞뒤 발이 엇갈리고, 코 위로 킁킁 김이 두 번 오른다"""
    frames = []
    for k in range(N):
        f = arrow_hog(k)
        if k % 6 in (1, 2, 3):   # 킁킁 김: 코 오른쪽 위로 작은 점 둘
            t = (k % 6) - 1
            for d in (0, 1):
                f.setdefault(ARROW.cell(3.0 + d * 1.6, -3.6 - t * 1.2 - d), PUFF)
        frames.append(finish(clip(f)))
    return frames


def wait() -> list[dict]:
    """풀숲에 떨어진 도토리 앞에서 코를 들썩들썩 킁킁 — 코를 들 때 김이 오르고 가시 결이 숨 따라 살짝 흔들린다"""
    frames = []
    rig = Rig(5.0, 16.0, 0.0, 0.92)
    for k, ph in enumerate(phases()):
        sniff = abs(math.sin(2 * ph))          # 한 바퀴에 두 번 들썩
        f = {}
        tuft(f, 1, 30, 24, k)
        sprite(f, ACORN_ART, 1, 18)
        o, _ = side(rig, step=0.0, sniff=sniff, shut=(k == 9), turn=0.04 * math.sin(ph))
        f.update(o)
        if sniff > 0.7:
            for d in range(2):
                f.setdefault(rig.cell(2.0 + 1.4 * d, -3.0 - 1.4 * d - 1.5 * (k % 3 == 1)), PUFF)
        frames.append(finish(clip(f)))
    return frames


def sign(f: dict, R: float = 13.5, ring: bool = True, slash: bool = True) -> None:
    """빨간 금지 표지(sea 의 SIGN 색). 고리와 빗금을 따로 그릴 수 있다 — 빗금을 몸 앞에 긋는다"""
    cells = set()
    if ring:
        cells |= {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
    if slash:
        for t in range(-90, 91):
            x, y = 15.5 + t / 100 * (R - 1.5) * 0.7071, 15.5 + t / 100 * (R - 1.5) * 0.7071
            cells |= disc(x, y, 1.3)
    solid(f, cells, SIGN, SIGN_D)


def no() -> list[dict]:
    """금지 표지 안에서 공처럼 몸을 말았다 — 가시가 쭈뼛 섰다가 가라앉고, 말린 틈으로 코끝과 눈이 빼꼼"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f, slash=False)
        puff = 0.7 + 0.6 * max(0.0, math.sin(ph))
        o, _ = ball(Rig(15.5, 15.5, 0.0, 1.0), R=7.2 + 0.4 * max(0.0, math.sin(ph)), puff=puff,
                    shut=(k in (4, 5)))
        f.update(o)
        sign(f, ring=False)   # 빗금은 몸 앞 — 몸 뒤에 숨으면 그냥 고리라 금지로 안 읽힌다
        frames.append(finish(f))
    return frames


def move() -> list[dict]:
    """공처럼 만 고슴도치가 데굴데굴(한 바퀴에 1초) — 네 방향 풀잎 화살촉이 바깥으로 두근댄다"""
    frames = []
    for k in range(N):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy, GRASS)
        ob, _ = ball(Rig(15.5, 15.5, 360.0 * k / N, 1.0), R=7.0)
        f.update(ob)
        frames.append(finish(f))
    return frames


def stretch(ang: float) -> list[dict]:
    """몸을 ang 축으로 쭉 늘인 옆모습 — 주둥이 끝과 가시 엉덩이가 양 끝 화살 노릇. 숨 쉬듯 늘었다 줄고
    양 끝 풀잎 화살촉이 두근댄다. 몸 가운데가 판 가운데"""
    frames = []
    t = math.radians(ang)
    ux, uy = math.cos(t), math.sin(t)
    dx, dy = round(ux), round(uy)
    diag = dx != 0 and dy != 0
    R = 10 if diag else 13
    k_ = 0.76 if diag else 0.66
    for k, ph in enumerate(phases()):
        f = {}
        st = 1.2 + 0.1 * math.sin(ph)
        o = 1 if math.sin(ph) > 0.3 else 0
        for sg in (-1, 1):
            chevron(f, 15 + (1 if sg * dx > 0 else 0) + sg * dx * (R + o) - (1 if sg * dx > 0 else 0),
                    15 + sg * dy * (R + o), sg * dx, sg * dy, GRASS if o else GRASS_D)
        mid = 8.0 + (13.0 - 8.0) * st         # 몸 가운데(a)
        rig = Rig(15.5 - ux * mid * k_, 15.5 - uy * mid * k_, ang, k_)
        b, _ = side(rig, step=math.sin(2 * ph), stretch=st, shut=(k == 3), big_eye=True)
        f.update(b)
        frames.append(finish(clip(f)))
    return frames


def we():
    return stretch(0.0)


def ns():
    return stretch(-90.0)


def nwse():
    return stretch(45.0)


def nesw():
    return stretch(-45.0)


CROSS = Rig(15.42, 15.24, 40.0, 0.75)   # 코끝 칸이 (15, 15), 몸은 오른쪽 아래 사분면


def cross() -> list[dict]:
    """조준선 한가운데에 코끝을 대고 킁킁 — 몸은 오른쪽 아래 사분면에 엎드리고 가는 조준선 넷이 코끝을 가리킨다.
    처음엔 앞모습 얼굴을 한가운데 두었는데 갈색 단발머리 아이로 읽혀서 옆모습으로 바꿨다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        tw = 1 if k % 6 < 3 else 0
        for i in list(range(1, 12)) + list(range(20, 31)):
            c = SPINE_L if i in (1 + tw, 30 - tw) else SPINE_D
            f[i, 15] = c
            f[15, i] = c
        o, _ = side(CROSS, sniff=0.3 * abs(math.sin(2 * ph)), shut=(k == 8))
        f.update(o)
        frames.append(finish(clip(f)))
    return frames


def busy() -> list[dict]:
    """작은 화살표 고슴도치 + 오른쪽 아래 데굴데굴 도는 가시 공 — 둘레 도토리 여덟이 차례로 크게 빛난다"""
    frames = []
    cx, cy = 22.0, 22.0
    for k in range(N):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = math.floor(cx + 7.2 * math.cos(a)), math.floor(cy + 7.2 * math.sin(a))
            lag = (head - i) % 8
            acorn(f, x - 1, y - 2, 255 if lag < 1 else 200 if lag < 2 else 140 if lag < 3 else 90)
        ob, _ = ball(Rig(cx, cy, 360.0 * k / N, 0.62), R=6.0)
        f.update(ob)
        f.update(arrow_hog(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def help_() -> list[dict]:
    """작은 화살표 고슴도치 + 나뭇잎으로 찍은 물음표 — 잎이 글자 차례로 하나씩 부풀었다 돌아온다"""
    frames = []
    cells = [(17.6 + 2.2 * i, 11.6 + 2.2 * j) for j, row in enumerate(QMARK) for i, ch in enumerate(row) if ch == "#"]
    for k in range(N):
        f = {}
        m, big = set(), set()
        for i, (x, y) in enumerate(cells):
            d = (k * len(cells) / N - i) % len(cells)
            (big if d < 1.5 else m).update(disc(x, y, 1.2 + (0.5 if d < 1.5 else 0.0)))
        solid(f, m, GRASS, GRASS_D)
        solid(f, big - m, GRASS_L, GRASS_D)
        f.update(arrow_hog(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def person() -> list[dict]:
    """작은 화살표 고슴도치 + 고슴도치를 품에 안은 사람 아이콘 — 안긴 고슴도치가 코를 킁킁, 사람은 눈을 깜빡.
    처음엔 가시 후드를 쓴 사람을 그렸는데 갈색 단발머리로 읽혔다. 머리 위에 태우면 모자로 읽힌다"""
    frames = []
    prig = Rig(23.0, 14.0, 0.0, 1.0)
    skin = hx("f2c9a0ff")
    for k, ph in enumerate(phases()):
        f = {}
        parts = [("head", ell(0.0, 0.0, 3.8, 3.8), skin, True),
                 ("torso", ell(0.0, 13.0, 7.4, 7.0), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
        o, _, _ = draw(prig, parts)
        for sg in (-1, 1):
            eye(o, prig, sg * 1.6 - 0.5, -0.4, big=False, shut=(k == 6))
            dot(o, prig, sg * 2.2, 1.4, BLUSH)
        f.update(o)
        sniff = abs(math.sin(2 * ph))
        hog, _ = side(Rig(14.2, 22.2, 0.0, 0.44), sniff=0.6 * sniff, big_eye=True, shut=(k == 10))
        f.update(hog)
        for x, y in ((17, 26), (25, 26)):     # 감싸 안은 두 손
            for q in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
                f[q] = skin
        f.update(arrow_hog(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def pin() -> list[dict]:
    """작은 화살표 고슴도치 + 빨간 지도 핀 머리에 올라탄 고슴도치 — 핀이 통통 튀면 같이 튀고, 땅에 닿을 때
    눈을 꼭 감는다. 처음엔 핀 동그라미 창 속에 얼굴을 넣었는데 앞모습은 사람 머리로, 옆얼굴은 창에 잘려
    초록 두건 쓴 아이로 읽혀서 몸 전체를 핀 위에 올렸다"""
    frames = []
    for k in range(N):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 19.5 + dy
        for x in range(19, 27):   # 그림자 — 높을수록 옅게
            f.setdefault((x, 30), hx("3f7a3570") if dy else hx("3f7a35b0"))
        solid(f, disc(cx, cy, 5.2) | raster([(cx - 3.8, cy + 2.6), (cx + 3.8, cy + 2.6), (cx, cy + 10.4)]),
              SIGN, SIGN_D)
        solid(f, disc(cx, cy + 0.5, 2.2), HI, SIGN_D)
        hog, _ = side(Rig(cx - 6.6, cy - 4.4 - 7.0 * 0.5, 0.0, 0.5), shut=(dy == 0))
        f.update(hog)
        f.update(arrow_hog(k, small=True))
        frames.append(finish(clip(f)))
    return frames


HAND = Rig(3.72, 3.5, 62.0, 1.0)   # 뒷발로 앉아 코끝을 왼쪽 위로 쭉 — 코끝 칸이 (3, 3)


def hand() -> list[dict]:
    """뒷발로 앉아 코끝을 왼쪽 위로 쭉 내밀어 콕 — 등 가시에 빨간 사과가 꽂혀 있다. 한 바퀴에 두 번 몸째 코를 한 칸
    내밀고 그때 코끝 둘레가 반짝. 핫스팟은 쉴 때의 코끝(콕 찌를 때도 코가 덮는다).
    처음엔 앞모습으로 앞발을 번쩍 든 고슴도치를 그렸는데 든 팔이 토끼 귀로, 사과가 리본으로 읽혀서 옆모습으로 바꿨다"""
    frames = []
    apple = ("apple", ell(13.6, -8.6, 2.6, 2.4), lambda a, b: APPLE_L if a < 12.8 and b < -9.4 else APPLE, True)
    stem = ("stem", any_of(bar((13.4, -10.8), (13.0, -12.2), 0.45), ell(14.6, -12.0, 1.3, 0.6, -0.3)),
            lambda a, b: GRASS if a > 13.8 else CAP, False)
    for k, ph in enumerate(phases()):
        poke = max(0.0, math.sin(2 * ph))
        rig = Rig(HAND.ox - 1.1 * poke, HAND.oy - 1.1 * poke, 62.0, 1.0)
        o, _ = side(rig, step=0.0, sniff=0.0, shut=(k == 9), extra=(stem, apple))
        f = dict(o)
        if poke > 0.9:
            x, y = rig.cell(0.0, 0.2)
            for q in ((x - 2, y + 2), (x + 2, y - 2), (x - 2, y - 1)):
                f.setdefault(q, HI)
        frames.append(finish(clip(f)))
    return frames


IX = 7   # I 기둥(가지) 왼쪽 칸


def ibeam() -> list[dict]:
    """세로 나뭇가지(위아래 잎이 I 의 가로획)에 옆으로 매달린 고슴도치 — 앞발로 가지를 꼭 쥐고 코를 들썩이며
    한 칸씩 오르내린다. 핫스팟은 가지 가운데(몸이 덮는 칸).
    처음엔 가지를 끌어안은 앞모습이었는데 사람 머리로 읽혔고, 가지 옆을 구르는 공은 b · P 글자로 읽혀서 바꿨다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sw = 1 if k % 6 < 3 else 0
        for y in range(2, 30):
            f[IX, y] = TWIG
            f[IX + 1, y] = TWIG_D
        for x in range(IX - 3, IX + 5):   # 위 · 아래 잎 — I 의 가로획
            end = x in (IX - 3, IX + 4)
            f[x, 1 + (sw if end else 0)] = GRASS_L if x < IX else GRASS
            f[x, 2] = GRASS_D if x not in (IX, IX + 1) else TWIG
            f[x, 29] = GRASS_D if x not in (IX, IX + 1) else TWIG
            f[x, 30 - (sw if end else 0)] = GRASS
        rig = Rig(IX - 3.9, 15.0 - 1.0 * math.sin(ph), 0.0, 0.6)
        grip = ("grip", ell(9.6, 2.8, 1.5, 1.5), FEET, True)    # 가지를 쥔 앞발
        o, _ = side(rig, step=0.6 * math.sin(2 * ph), sniff=0.5 * abs(math.sin(2 * ph)), shut=(k == 8),
                    extra=(grip,))
        f.update(o)
        frames.append(finish(clip(f)))
    return frames


TIP, BACK = (1.5, 29.5), (17.2, 12.6)   # 깃펜 끝 · 꽁무니(화면)
PEN = Rig(15.9, 7.9, 70.0, 0.72)        # 뒷발로 선 옆모습 — 코가 위, 배가 왼쪽(깃펜 쪽)


def pen() -> list[dict]:
    """뽑은 가시 하나를 깃펜처럼 앞발로 쥐고 뒷발로 서서 쓴다 — 끝이 짙고 마디마디 갈색 · 크림 띠가 진 가시.
    가시 끝(왼쪽 아래)이 핫스팟. 고슴도치와 깃펜이 펜 끝을 축으로 살짝 까딱인다"""
    frames = []
    base = PEN
    L = math.hypot(BACK[0] - TIP[0], BACK[1] - TIP[1])
    ux, uy = (BACK[0] - TIP[0]) / L, (BACK[1] - TIP[1]) / L
    lt, lb = base.local(*TIP), base.local(*BACK)
    mid = base.local(TIP[0] + ux * L * 0.3, TIP[1] + uy * L * 0.3)

    def qcol(a, b):
        x, y = base.world(a, b)
        t = (x - TIP[0]) * ux + (y - TIP[1]) * uy
        if t < 2.2:
            return EYE
        return SPINE_L if int(t / 3.0) % 2 else SPINE
    quill = ("quill", any_of(bar(lt, mid, 0.3 / base.k, 1.25 / base.k), bar(mid, lb, 1.25 / base.k, 0.8 / base.k)),
             qcol, True)
    pa, pb = base.local(TIP[0] + ux * L * 0.86, TIP[1] + uy * L * 0.86)
    paw = ("paw", ell(pa, pb, 1.5, 1.5), FEET, True)
    for k, ph in enumerate(phases()):
        d = math.radians(3.0 * math.sin(2 * ph))
        ox, oy = base.ox - TIP[0], base.oy - TIP[1]
        rig = Rig(TIP[0] + ox * math.cos(d) - oy * math.sin(d), TIP[1] + ox * math.sin(d) + oy * math.cos(d),
                  70.0 + math.degrees(d), base.k)
        f, _ = side(rig, shut=(k == 4), extra=(paw, quill))
        f[math.floor(TIP[0]), math.floor(TIP[1])] = EYE
        frames.append(finish(clip(f)))
    return frames


UP = Rig(18.6, 1.3, 90.0, 0.84)   # 코끝이 위, 배(풀 줄기 쪽)가 왼쪽
SX = 12                            # 풀 줄기 왼쪽 칸


def up() -> list[dict]:
    """풀 줄기를 타고 오른다 — 코를 하늘로 들고 앞뒤 발이 번갈아 줄기를 잡는다. 줄기 잎이 아래로 흘러가
    올라가는 것처럼 보인다. 코끝이 핫스팟"""
    frames = []
    sx = SX
    for k, ph in enumerate(phases()):
        f = {}
        for y in range(1, 31):
            f[sx, y] = GRASS
            f[sx + 1, y] = GRASS_D
        for j in range(3):   # 줄기 잎 — 한 바퀴에 판 1/3 씩 아래로
            y = 4 + (j * 10 + k * 10 // N) % 30
            sprite(f, ["..g", ".lg", "lg."] if j % 2 else ["g..", "gl.", ".gl"],
                   sx + 2 if j % 2 else sx - 3, y, outline=False)
        o, _ = side(UP, step=math.sin(2 * ph), shut=(k == 7))
        f.update(o)
        frames.append(finish(clip(f)))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1),
       "wait": (15, 15), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (IX, 15),
       "pen": (math.floor(TIP[0]), math.floor(TIP[1])), "hand": lambda fr: min((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[0] + p[1], p[1])),
       "up": lambda fr: min((p for p, c in fr[0].items() if c[3] == 255 and p[0] > SX + 1), key=lambda p: (p[1], p[0]))}


def check(rid: str, frames: list[dict], hot: tuple) -> None:
    """핫스팟이 장마다 불투명한 칸 위에 있는지"""
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
        if hot == (1, 1) and any(c[3] == 255 and (p[0] < 1 or p[1] < 1) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 코끝보다 왼쪽·위로 나온 칸이 있음")


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

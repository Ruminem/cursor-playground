# SPDX-License-Identifier: Apache-2.0
"""턱시도냥(tuxedocatanim) 구성표 그림 `art/tuxedocatanim/*.txt` 를 만든다.
빌드가 부르지 않고 손으로 돌린다 · 빌드 코드 해시와 CI 캐시 키에 안 들어간다.

  python3 gen/tuxedocat.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

해달처럼 칸마다 턱시도냥이 하는 짓을 따로 그린다(`SCENE`). '냥이 · 애니' 셋(치즈냥 · 턱시도냥 · 까망이) 중
턱시도냥은 **길쭉하고 날씬한 신사**다 — 짙은 회흑 몸(순검정이면 어두운 바탕에서 테만 남는다) · 흰 셔츠 가슴 ·
흰 주둥이와 콧등 줄 · 흰 양말 네 발 · 초록 눈 · 빨간 나비넥타이(실루엣의 표식) · 길고 곧게 선 꼬리.
새침한 성격이라 코를 치켜들고 눈을 내리깐다. 소품도 신사의 것(회중시계 · 깃펜 · 지팡이 · 찻잔)이다.

  arrow   큰 흰 화살표 뒤에 숨은 턱시도냥이 빗변 위로 빼꼼 — 흰 양말 발끝 둘이 빗변을 잡고 장 2–5 에 쏙 더
          올라온다. 화살표 끝이 핫스팟(`sea.peek`, 냥이 10종 공용 틀)
  busy    작은 화살표 턱시도냥 + 오른쪽 아래 찻잔(김이 오른다) 둘레를 도는 분홍 젤리 발자국 여덟
  cross   가는 조준선 가운데 빨간 레이저 점(핫스팟) — 오른쪽 아래에서 동공이 커진 턱시도냥이 엉덩이를 씰룩이며 노린다
  hand    옆으로 앉아 흰 양말 앞발 하나를 왼쪽 위로 쭉 들어 콕 누른다 — 분홍 젤리가 보이는 발끝이 핫스팟
  help    작은 화살표 턱시도냥 + 분홍 젤리 발자국으로 찍은 물음표(차례로 꾹꾹)
  ibeam   위 판 · 밧줄 기둥 · 아래 받침이 I 인 스크래처 — 옆에 선 턱시도냥이 앞발을 번갈아 머리 위에서
          아래로 박박 내리긁고 밧줄에 발톱 자국이 남는다(두 발이 같이 움직이면 박수로 읽힌다). 핫스팟은 기둥 가운데
  move    앞모습으로 앉아 앞발을 번갈아 들며 사뿐사뿐 제자리 걸음 — 네 방향 빨간 화살촉
  ns      제자리에서 수직 점프 — 웅크렸다 쭉 늘어나 뜨고 다시 내려앉는다. 위아래 화살촉
  nwse · nesw  옆모습으로 그 대각선을 따라 다다닥 달린다 — 한쪽 끝으로 갔다가 돌아서 반대쪽으로, 가는 쪽 화살촉이 깜빡
          (기지개로 늘었다 줄었다 하던 판은 몸통이 늘어나는 것으로 읽혀 바꿨다)
  no      빨간 금지 표지 안에서 코를 치켜들고 눈을 감은 채 앞발 하나를 내밀어 '사양하겠소'
  pen     깃펜을 쥐고 글씨를 쓰는 신사 — 펜촉(왼쪽 아래)이 핫스팟
  person  작은 화살표 턱시도냥 + 나비넥타이를 맨 신사 고양이 흉상(사람 아이콘 꼴)
  pin     작은 화살표 턱시도냥 + 흰 동그라미 속에 빨간 나비넥타이가 든 지도 핀이 통통 튄다
  up      뒷발로 서서 신사 지팡이를 머리 위로 곧게 치켜든다 — 지팡이 끝(맨 위)이 핫스팟
  wait    앉아서 회중시계를 들여다본다 — 시곗바늘이 돌고 꼬리 끝이 똑딱똑딱. 가운데가 핫스팟
  we      꼬리를 곧게 세우고 새침하게 옆으로 걷는다 — 왼쪽으로 가다가 돌아서 오른쪽으로. 양 끝 화살촉

몸은 부위(타원 · 굵기가 변하는 막대 · 세모)를 고양이 제 좌표 (u 오른쪽, w 아래)에 놓고 화면으로 돌려 찍는다
(`Rig`, `draw` — 해달 생성기와 같은 방식이지만 다른 생성기에 기대지 않게 여기 따로 둔다). 앞모습(`front`)과
옆모습(`side`) 두 벌이고, 머리는 제 좌표(`Sub`)로 따로 돌려 코를 치켜들 수 있다. 눈 · 코 · 입은 화면 칸에 직접 찍는다.
화살표 끝을 귀 끝으로 잡으면 몸을 기울일 때 반대쪽 귀가 더 올라가고, 동그란 머리는 코끝이 모서리가 못 된다 —
그래서 몸이 아니라 껴안은 흰 화살표의 끝을 쓴다.
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, disc, finish, hx, ink, inside, peek, phases, raster, solid, write

SID = "tuxedocatanim"

OUT = hx("0c0c10ff")                                                # 테두리
FUR, FUR_L, FUR_D = hx("2a2a33ff"), hx("3e3e4cff"), hx("1c1c23ff")  # 털 · 앞에 놓인 다리 · 뒤에 놓인 다리
WHITE, WHITE_D = hx("f7f7f2ff"), hx("cfd1dbff")                     # 셔츠 · 양말 · 주둥이 / 그늘
GREEN, GREEN_D, PUPIL, HI = hx("9ee05aff"), hx("4f9a2cff"), hx("121218ff"), hx("ffffffff")
LID = hx("a2a2b4ff")                                                # 감은 눈 (검은 털 위에 짙은 선은 안 보인다)
NOSE, PINK, BLUSH = hx("f29aaeff"), hx("e8899cff"), hx("ee7f98ff")  # 코 · 귀 속 · 볼터치
BEAN, BEAN_D = hx("f6a8b8ff"), hx("d9758eff")                       # 발바닥 젤리
BOW, BOW_D = hx("dc3340ff"), hx("98202cff")                         # 나비넥타이
ink(OUT, HI, hx("e6e8f0c7"))
GOLD, GOLD_D, DIAL = hx("e8bf4aff"), hx("a8822aff"), hx("fbf3dcff")  # 회중시계 · 지팡이 손잡이
CUP, CUP_D, TEA = hx("f2f4fbff"), hx("a9b4cfff"), hx("b0703cff")    # 찻잔
STEAM = hx("b8bcccc0")
QUILL, QUILL_D, NIB = hx("f4f1e6ff"), hx("bdb8a8ff"), hx("3a3a46ff")  # 깃펜
ROPE, ROPE_D, PLANK, PLANK_D = hx("dcc08cff"), hx("b0915aff"), hx("8a5a3aff"), hx("643e26ff")  # 스크래처
CANE = hx("2e2a30ff")
LASER, GLOW = hx("ff2a2aff"), hx("ff4a4a70")


# ── 그리개: 고양이 제 좌표 (a, b) → 화면 ─────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도, a 축이 화면에서 가리키는 쪽, 90 이 아래) · 배율 k · 세로 배율 sy(점프의 눌림).
    flip 이면 좌우를 뒤집는다(오른쪽을 보는 옆모습)"""

    def __init__(self, ox: float, oy: float, ang: float = 0.0, k: float = 1.0, flip: bool = False, sy: float = 1.0):
        t = math.radians(ang)
        self.ox, self.oy, self.c, self.s, self.k, self.f, self.sy = ox, oy, math.cos(t), math.sin(t), k, flip, sy

    def world(self, a: float, b: float) -> tuple:
        a = -a if self.f else a
        return self.ox + (a * self.c - b * self.s) * self.k, self.oy + (a * self.s + b * self.c) * self.k * self.sy

    def local(self, x: float, y: float) -> tuple:
        dx, dy = (x - self.ox) / self.k, (y - self.oy) / (self.k * self.sy)
        a, b = dx * self.c + dy * self.s, -dx * self.s + dy * self.c
        return (-a if self.f else a), b

    def cell(self, a: float, b: float) -> tuple:
        x, y = self.world(a, b)
        return math.floor(x), math.floor(y)


class Sub:
    """머리처럼 따로 도는 부위의 제 좌표 — 가운데 c, 크기 r(반지름 단위), ang(도, + 면 시계 방향: 왼쪽을 보는
    머리의 코가 위로 들린다)"""

    def __init__(self, c, r: float, ang: float = 0.0):
        t = math.radians(ang)
        self.cx, self.cy, self.r, self.c, self.s = c[0], c[1], r, math.cos(t), math.sin(t)

    def to(self, x: float, y: float) -> tuple:
        return self.cx + (x * self.c - y * self.s) * self.r, self.cy + (x * self.s + y * self.c) * self.r

    def back(self, a: float, b: float) -> tuple:
        dx, dy = (a - self.cx) / self.r, (b - self.cy) / self.r
        return dx * self.c + dy * self.s, -dx * self.s + dy * self.c

    def hit(self, h):
        return lambda a, b: h(*self.back(a, b))

    def col(self, c):
        return (lambda a, b: c(*self.back(a, b))) if callable(c) else c


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


def shrink(pts, k):
    cx, cy = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    return [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in pts]


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


def mirror(f: dict) -> dict:
    """좌우 뒤집기 — 칸 15 는 15 로 간다"""
    return {(30 - x, y): c for (x, y), c in f.items()}


def moved(f: dict, dx: int, dy: int) -> dict:
    return {(x + dx, y + dy): c for (x, y), c in f.items()}


# ── 부위 ─────────────────────────────────────────────────────────────────────
def limb(name, p0, p1, r0, r1=None, sock=0.34, fur=FUR, lined=True):
    """다리 · 팔. 끝 sock 몫이 흰 양말이고 끝에 조금 굵은 발이 붙는다"""
    r1 = r0 if r1 is None else r1
    ex, ey = p1[0] - p0[0], p1[1] - p0[1]
    ll = ex * ex + ey * ey or 1e-9

    def col(a, b):
        t = ((a - p0[0]) * ex + (b - p0[1]) * ey) / ll
        return WHITE if t > 1 - sock else fur
    return (name, any_of(bar(p0, p1, r0, r1), ell(p1[0], p1[1], r1 * 1.18, r1 * 1.18)), col, lined)


def tail(pts, r0=1.15, r1=0.8, name="tail", lined=False):
    """곧게 선 꼬리 — 꺾인 줄 pts 를 따라 굵기가 r0 → r1"""
    n = len(pts) - 1
    hs = [bar(pts[i], pts[i + 1], r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n) for i in range(n)]
    return (name, any_of(*hs), FUR, lined)


EAR = {"up": [(-1.0, -0.22), (-0.84, -1.46), (-0.18, -0.86)],     # 쫑긋
       "flick": [(-1.02, -0.3), (-1.22, -1.28), (-0.26, -0.86)],  # 바깥으로 까딱
       "flat": [(-1.02, -0.12), (-1.5, -0.52), (-0.5, -0.82)]}   # 옆으로 젖힘


def head_front(sub: Sub, ears=("up", "up")) -> list:
    """앞모습 머리(제 좌표, 반지름 1): 검은 머리 · 흰 주둥이와 콧등 줄 · 세모 귀(속은 분홍)"""
    eps = [EAR[ears[0]], [(-x, y) for x, y in EAR[ears[1]]]]
    inner = [shrink(p, 0.45) for p in eps]
    muzzle = ell(0, 0.5, 0.52, 0.38)
    blaze = bar((0, -0.34), (0, 0.2), 0.12)

    def skin(x, y):
        return WHITE if muzzle(x, y) or blaze(x, y) else FUR

    def ear(x, y):
        return PINK if any(inside(p, x, y) for p in inner) else FUR
    # 위는 둥근 이마, 아래는 옆으로 퍼진 볼 — 동그라미 하나면 칸 위에서 네모로 읽힌다
    head = any_of(ell(0, -0.05, 1.02, 0.88), ell(0, 0.3, 1.12, 0.6))
    return [("head", sub.hit(head), sub.col(skin), True),
            ("ears", sub.hit(lambda x, y: any(inside(p, x, y) for p in eps)), sub.col(ear), False)]


def eye(f: dict, rig: Rig, a: float, b: float, mood: str) -> None:
    """눈 한 짝 — 2×2 칸. 초록 눈에 왼쪽 위 흰 반짝(검은 얼굴에 짙은 점 눈은 안 보인다)"""
    x, y = rig.cell(a, b)
    x, y = x - 1 + (1 if rig.world(a, b)[0] % 1 >= 0.5 else 0), y - 1 + (1 if rig.world(a, b)[1] % 1 >= 0.5 else 0)
    if mood == "open":
        cells = {(0, 0): HI, (1, 0): GREEN, (0, 1): GREEN, (1, 1): GREEN_D}
    elif mood == "wide":     # 사냥 눈 — 동공이 커진다
        cells = {(0, 0): HI, (1, 0): PUPIL, (0, 1): PUPIL, (1, 1): PUPIL}
    elif mood == "blink":
        cells = {(0, 1): LID, (1, 1): LID}
    elif mood == "smug":     # 새침하게 내리깐 눈 — 위 눈꺼풀이 반쯤 덮는다
        cells = {(0, 0): LID, (1, 0): LID, (0, 1): GREEN, (1, 1): GREEN_D}
    else:                    # closed: 흥 하고 감은 눈 — 아래로 둥근 선
        cells = {(0, 0): LID, (1, 1): LID}
    for (dx, dy), c in cells.items():
        f[x + dx, y + dy] = c


def face_front(f: dict, rig: Rig, sub: Sub, mood="open", mouth=True) -> None:
    for sg in (-1, 1):
        eye(f, rig, *sub.to(sg * 0.46, -0.04), mood if not (mood == "closed" and sg > 0) else "closed")
        dot(f, rig, *sub.to(sg * 0.76, 0.34), BLUSH)
    dot(f, rig, *sub.to(0, 0.3), NOSE)
    if mouth:
        n = rig.cell(*sub.to(0, 0.3))
        f[n[0] - 1, n[1] + 1] = OUT
        f[n[0] + 1, n[1] + 1] = OUT


def bow_front(c, r, name="bow", h=0.32) -> tuple:
    """앞에서 본 나비넥타이 — 가운데 매듭 + 두 날개. r 은 머리 반지름(머리에 맞춰 크기를 정한다), h 는 날개 끝 높이"""
    x, y = c
    w, h = r * 0.62, r * h
    knot = ell(x, y, r * 0.16, r * 0.19)
    wings = any_of(poly([(x, y), (x - w, y - h), (x - w, y + h)]), poly([(x, y), (x + w, y - h), (x + w, y + h)]))
    # 테를 두르면 작게 그린 판에서 날개가 다 테가 된다 — 빨강은 검은 털 위에서 테 없이도 읽힌다
    return (name, any_of(knot, wings), lambda a, b: BOW_D if knot(a, b) else BOW, False)


HC, HR = (0.0, -8.0), 6.0       # 앞모습 머리 가운데 · 반지름 (몸 원점은 가슴 아래)


def front(rig: Rig, mood="open", ears=("up", "up"), body="sit", arms=None, tail_pts=None, extra=(), mid=(),
          head_ang=0.0, lift=(0.0, 0.0), beans=(), st=1.0, hc=HC) -> tuple[dict, set]:
    """앞모습 턱시도냥 한 장. body 는 sit(앉음) · stand(뒷발로 섬) · air(뛰어올라 다리를 늘어뜨림) · bust(흉상).
    arms 는 [(어깨, 앞발 끝) 또는 None] 둘 — None 이면 앉은 앞다리. lift 는 앉은 앞발을 든 높이,
    beans 는 젤리를 보일 앞발 번호, st 는 몸통 세로 늘임, extra 는 맨 앞 · mid 는 팔 뒤 · 머리 앞에 놓을 부위"""
    sub = Sub(hc, HR, head_ang)
    parts = list(extra) + [bow_front((hc[0], hc[1] + HR * 0.98), HR)]
    arms = arms or (None, None)
    paws = []
    for i, sg in enumerate((-1, 1)):
        if arms[i]:
            sh, tip = arms[i]
            parts.append(limb(f"arm{i}", sh, tip, 1.3, 1.25, sock=0.3, fur=FUR_L))
            paws.append(tip)
        elif body == "sit":
            parts.append(limb(f"arm{i}", (sg * 1.6, 2.4), (sg * 1.6, 8.5 - lift[i]), 1.2, 1.25, fur=FUR_L))
            paws.append((sg * 1.6, 8.5 - lift[i]))
        elif body in ("stand", "air"):   # 가슴에 모은 앞발
            parts.append(limb(f"arm{i}", (sg * 2.6, -0.4), (sg * 1.3, 3.6), 1.15, 1.15, sock=0.4, fur=FUR_L))
            paws.append(None)
    parts += list(mid) + head_front(sub, ears)
    shirt = ell(0, 0.4 * st, 2.2, 3.6 * st)

    def tcol(a, b):
        return WHITE if shirt(a, b) else FUR
    if body == "sit":
        parts += [("feet", any_of(ell(-4.6, 8.8, 1.8, 1.0), ell(4.6, 8.8, 1.8, 1.0)), WHITE, True),
                  ("haunch", any_of(ell(-3.3, 6.2, 2.5, 3.0), ell(3.3, 6.2, 2.5, 3.0)), FUR, True),
                  ("torso", any_of(ell(0, 3.0, 4.0, 5.8), ell(0, -0.8, 3.4, 2.6)), tcol, False)]
    elif body in ("stand", "air"):
        foot = 10.4 * st if body == "stand" else 11.4 * st
        parts += [limb("leg0", (-2.0, 5.0 * st), (-2.2 - (0.6 if body == "air" else 0), foot), 1.45, 1.25),
                  limb("leg1", (2.0, 5.0 * st), (2.2 + (0.6 if body == "air" else 0), foot), 1.45, 1.25),
                  ("torso", any_of(ell(0, 1.8 * st, 3.7, 5.4 * st), ell(0, -0.8, 3.2, 2.4)), tcol, False)]
    elif body == "bust":
        parts += [("torso", any_of(ell(0, 4.6, 6.6, 5.2), ell(0, -0.6, 3.4, 2.6)), tcol, False)]
    if tail_pts:
        parts.append(tail(tail_pts))
    out, mask, _ = draw(rig, parts)
    face_front(out, rig, sub, mood)
    for i in beans:
        if paws[i]:
            dot(out, rig, *paws[i], BEAN)
    return out, mask


# ── 옆모습: 왼쪽을 본다. a 오른쪽(꼬리 쪽), b 아래 ───────────────────────────────────
def head_side(sub: Sub) -> list:
    """옆모습 머리(제 좌표, 반지름 1) — 둥근 머리 · 조금 나온 흰 주둥이 · 귀 둘(앞 귀는 조금 앞에)"""
    muzzle = ell(-0.8, 0.3, 0.4, 0.32)
    chin = ell(-0.48, 0.6, 0.5, 0.28)
    near = [(0.02, -0.7), (0.4, -1.46), (0.82, -0.5)]
    far = [(-0.7, -0.52), (-0.58, -1.4), (-0.1, -0.82)]
    inner = shrink(near, 0.45)

    def skin(x, y):
        return WHITE if muzzle(x, y) or chin(x, y) else FUR

    def ear(x, y):
        return PINK if inside(inner, x, y) else FUR
    head = any_of(ell(0, 0, 1.0, 0.88), ell(-0.22, 0.28, 0.92, 0.6), muzzle)
    return [("head", sub.hit(head), sub.col(skin), True),
            ("ear", sub.hit(poly(near)), sub.col(ear), False),
            ("ear2", sub.hit(poly(far)), FUR_D, False)]


def face_side(f: dict, rig: Rig, sub: Sub, mood="open") -> None:
    eye(f, rig, *sub.to(-0.44, -0.08), mood)
    dot(f, rig, *sub.to(-1.14, 0.16), NOSE)
    dot(f, rig, *sub.to(-0.12, 0.34), BLUSH)


def bow_side(c, r, name="bow") -> tuple:
    """옆에서 본 나비넥타이 — 매듭과 앞으로 나온 날개 하나, 뒤 날개는 조금만"""
    x, y = c
    knot = ell(x, y, r * 0.16, r * 0.2)
    wings = any_of(poly([(x, y), (x - r * 0.62, y - r * 0.4), (x - r * 0.62, y + r * 0.4)]),
                   poly([(x, y), (x + r * 0.36, y - r * 0.3), (x + r * 0.36, y + r * 0.3)]))
    # 테를 두르면 작은 날개가 다 테가 되어 빨강이 안 남는다 — 검은 털 위 빨강은 테 없이도 읽힌다
    return (name, any_of(knot, wings), lambda a, b: BOW_D if knot(a, b) else BOW, False)


def side(rig: Rig, pose="walk", ph=0.0, mood="open", head_ang=0.0, tail_pts=None, paw=None, s=0.0,
         ears=True, tr=(1.15, 0.8), sh=(-2.2, 0.0)) -> tuple[dict, set]:
    """옆모습 턱시도냥 한 장(왼쪽을 본다). pose 는 walk(걷기, ph 는 걸음 위상) · sit(앉음) · stretch(기지개, s 는
    늘인 정도 0–1). paw 는 sit 에서 든 앞발 끝(a, b) — 주면 앞 앞발을 그리로 든다"""
    parts = []
    if pose == "walk":
        bob = 0.35 * abs(math.sin(ph))
        hc, hr = (-7.4, -5.0 + bob), 5.0
        legs = []
        for name, hip, ph_, fur in (("legF", (-4.4, 1.2), ph, FUR_L), ("legH", (5.0, 1.2), ph + math.pi, FUR_L),
                                    ("legF2", (-3.0, 1.2), ph + math.pi, FUR_D), ("legH2", (6.4, 1.2), ph, FUR_D)):
            sw = math.sin(ph_)
            up = max(0.0, math.cos(ph_)) * 1.4
            legs.append(limb(name, (hip[0], hip[1] + bob), (hip[0] - 1.6 * sw, 7.6 - up), 1.25, 1.15, fur=fur,
                             lined=fur is FUR_L))
        torso = any_of(ell(0.6, 0.2 + bob, 7.0, 3.2), ell(-4.6, -1.0 + bob, 2.8, 3.0))
        bib = ell(-6.2, 0.6 + bob, 2.4, 2.8)
        tp = tail_pts or [(7.2, -1.0 + bob), (8.4, -4.0), (8.6, -14.0)]
        bow = bow_side((hc[0] + 1.4, hc[1] + hr * 0.95), hr)
        parts = [legs[0], legs[1], bow] + head_side(Sub(hc, hr, head_ang)) + \
            [("torso", torso, lambda a, b: WHITE if bib(a, b) else FUR, False), legs[2], legs[3], tail(tp, *tr)]
    elif pose == "sit":
        hc, hr = (-2.4, -9.0), 5.0
        bib = ell(-3.0, -0.4, 2.3, 4.0)
        torso = any_of(ell(-0.6, 0.6, 3.4, 6.0, 0.22), ell(2.8, 5.2, 4.2, 4.0))
        arm = limb("arm", sh, paw, 1.3, 1.45, sock=0.3, fur=FUR_L) if paw else \
            limb("arm", (-2.0, 1.6), (-2.6, 8.6), 1.2, 1.2, fur=FUR_L)
        tp = tail_pts or [(6.0, 7.6), (8.4, 6.8), (9.2, -6.0)]
        parts = [arm, bow_side((hc[0] - 0.4, hc[1] + hr * 0.98), hr)] + head_side(Sub(hc, hr, head_ang)) + \
            [("foot", ell(0.4, 8.9, 2.4, 0.95), WHITE, True),
             limb("arm2", (-0.8, 1.6), (-0.9, 8.6), 1.2, 1.2, fur=FUR_D, lined=False),
             ("torso", torso, lambda a, b: WHITE if bib(a, b) else FUR, False), tail(tp, *tr)]
    elif pose == "stretch":
        # 앞발은 땅에 쭉, 가슴은 낮게, 엉덩이는 높이, 꼬리는 곧게
        hc, hr = (-8.2 - 1.2 * s, 1.0), 4.8
        torso = any_of(ell(0.4, -0.6, 7.4 + 0.6 * s, 2.9, -0.32), ell(-4.6, 1.6, 2.6, 2.4))
        bib = ell(-5.6, 2.6, 1.6, 1.8)
        legs = [limb("legF", (-5.2, 2.4), (-13.0 - 2.6 * s, 6.4), 1.15, 1.1, fur=FUR_L),
                limb("legH", (5.6, -1.0), (6.6, 7.0), 1.35, 1.15, fur=FUR_L),
                limb("legF2", (-4.2, 2.6), (-11.6 - 2.4 * s, 6.6), 1.1, 1.05, fur=FUR_D, lined=False),
                limb("legH2", (6.8, -1.2), (8.0, 6.8), 1.3, 1.1, fur=FUR_D, lined=False)]
        tp = tail_pts or [(7.6, -3.2), (8.6, -6.0), (9.4, -14.0 - 1.0 * s)]
        parts = [legs[0], legs[1], bow_side((hc[0] + 1.8, hc[1] + hr * 0.9), hr)] + \
            head_side(Sub(hc, hr, head_ang)) + \
            [("torso", torso, lambda a, b: WHITE if bib(a, b) else FUR, False), legs[2], legs[3], tail(tp, *tr)]
    elif pose == "run":
        # 내달리기 — e=1 이면 앞다리는 앞으로 · 뒷다리는 뒤로 쭉, e=-1 이면 네 다리를 배 밑에 모은다.
        # 몸통 길이는 그대로 두고 다리와 높이만 바꾼다(몸이 늘어나 보이면 달리기가 아니라 기지개다)
        e = math.cos(ph)
        bob = -0.7 * e
        hc, hr = (-8.0, -3.6 + bob), 5.0
        t = (1 + e) / 2

        def lerp(p, q):
            return (q[0] + (p[0] - q[0]) * t, q[1] + (p[1] - q[1]) * t)
        legs = [limb("legF", (-4.6, 1.0 + bob), lerp((-11.6, 3.2), (-1.8, 6.4)), 1.25, 1.15, fur=FUR_L),
                limb("legH", (5.0, 1.0 + bob), lerp((12.0, 3.6), (0.8, 6.2)), 1.35, 1.15, fur=FUR_L),
                limb("legF2", (-3.4, 1.2 + bob), lerp((-10.2, 4.6), (-0.6, 6.6)), 1.15, 1.05, fur=FUR_D, lined=False),
                limb("legH2", (6.2, 1.0 + bob), lerp((10.6, 5.0), (2.2, 6.6)), 1.25, 1.05, fur=FUR_D, lined=False)]
        torso = any_of(ell(0.4, 0.2 + bob, 6.6, 3.0, 0.06 * e), ell(-4.4, -0.8 + bob, 2.8, 2.9))
        bib = ell(-6.0, 0.8 + bob, 2.2, 2.6)
        tp = tail_pts or [(6.8, -0.6 + bob), (10.0, -2.4 + bob), (13.4, -3.4 + 0.9 * math.sin(ph))]
        parts = [legs[0], legs[1], bow_side((hc[0] + 1.4, hc[1] + hr * 0.95), hr)] + \
            head_side(Sub(hc, hr, head_ang)) + \
            [("torso", torso, lambda a, b: WHITE if bib(a, b) else FUR, False), legs[2], legs[3], tail(tp, *tr)]
    if not ears:
        parts = [p for p in parts if p[0] not in ("ear", "ear2")]
    out, mask, _ = draw(rig, parts)
    face_side(out, rig, Sub(hc, hr, head_ang), mood)
    if paw:
        dot(out, rig, *paw, BEAN)
    return out, mask


# ── 화살표 턱시도냥: 흰 화살표 커서를 껴안는다 ─────────────────────────────────────────


# 윈도우 기본 화살표 꼴 — 끝이 (0, 0), 1 이 한 칸
CURSOR = [(0, 0), (0, 15.4), (4.0, 11.8), (6.6, 17.6), (9.2, 16.6), (6.8, 11.0), (11.6, 11.0)]
HUG = {False: (1.25, Rig(20.2, 23.4, 0.0, 0.7)), True: (0.86, Rig(13.6, 16.6, 0.0, 0.47))}


def arrow_cat(k: int, small: bool = False) -> dict:
    """화살표 턱시도냥 한 장 — 흰 화살표 커서 오른쪽에 앉아 두 앞발로 화살표 기둥을 꼭 껴안고 볼을 기댄다.
    화살표 끝이 (1, 1) 이라 찍는 점이 곧 화살표 끝이다. 화살표는 그대로 두고 고개 갸웃 · 꼬리 살랑 · 눈 깜빡만.
    옆모습에 긴 꼬리를 곧게 세운 판(V 자 막대)과 앞발을 번쩍 든 판(가는 막대)은 화살표로 안 읽혀 바꿨다"""
    s, rig = HUG[small]
    ph = 2 * math.pi * k / N
    f = {}
    solid(f, raster([(1 + x * s, 1 + y * s) for x, y in CURSOR]), WHITE, OUT)
    f[1, 1] = OUT
    # 두 앞발이 화살표 꼬리 기둥을 감싼다 — 몸 앞으로 지나가게 팔을 몸보다 먼저 놓는다
    sx, sy = 1 + 7.6 * s, 1 + 14.4 * s
    grip = rig.local(sx, sy)
    arms = (((-2.6, -0.8), (grip[0] + 0.6, grip[1] - 1.4)), ((2.4, -0.4), (grip[0] + 1.6, grip[1] + 1.4)))
    sw = math.sin(ph)
    tp = [(3.6, 8.6), (6.8, 7.4), (8.4 + 0.6 * sw, 3.0), (7.4 + 1.2 * sw, 0.0)]
    mood = "blink" if k == 7 else ("closed" if k in (3, 4, 5) else "open")
    g, _ = front(rig, mood=mood, arms=arms, tail_pts=tp, head_ang=-12.0 + 4.0 * sw, beans=(0, 1))
    f.update({p: c for p, c in g.items() if p[0] >= 1 and p[1] >= 1})
    return f


# ── 소품 ─────────────────────────────────────────────────────────────────────
PAW = ["b.b", ".b.", "BBB"]


def paw_print(f: dict, x0: int, y0: int, col: tuple, col2: tuple) -> None:
    """발자국 젤리 — 위 발가락 둘(+가운데 하나) · 아래 큰 젤리"""
    for j, row in enumerate(PAW):
        for i, ch in enumerate(row):
            if ch == "b":
                f[x0 + i, y0 + j] = col
            elif ch == "B":
                f[x0 + i, y0 + j] = col2


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col=BOW) -> None:
    """(dx, dy) 쪽을 가리키는 꽉 찬 화살촉. 꼭짓점이 (cx, cy)"""
    px, py = -dy, dx
    for i in range(3):
        for s in range(-i, i + 1):
            f[cx - dx * i + px * s, cy - dy * i + py * s] = col


def diag_chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col=BOW) -> None:
    """대각선 (dx, dy) 쪽 화살촉 — 꼭짓점 (cx, cy) 에서 두 변이 거꾸로 뻗는 세모"""
    for i in range(4):
        for j in range(4 - i):
            f[cx - dx * i, cy - dy * j] = col


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    def head(x, y, k):
        return front(Rig(x - HC[0] * PEEK_K, y - HC[1] * PEEK_K, 0.0, PEEK_K), mood="blink" if k == 7 else "open")[0]
    return [finish(peek(k, head, OUT, WHITE)) for k in range(N)]


PEEK_K = 0.86     # 빼꼼 턱시도냥 배율 — 머리 반지름이 6 이라 다른 냥이(7 × 0.74)와 머리 크기를 맞춘다


def watch(f: dict, cx: float, cy: float, r: float, k: int) -> None:
    """회중시계 — 금 테 · 흰 판 · 꼭지. 바늘이 한 바퀴에 N 칸 돈다"""
    solid(f, disc(cx, cy, r), DIAL, GOLD_D)
    for p in disc(cx, cy, r) - disc(cx, cy, r - 1.0):
        if p in f and f[p] == DIAL:
            f[p] = GOLD
    top = (math.floor(cx), math.floor(cy - r) - 1)
    f[top] = GOLD
    f[top[0], top[1] - 1] = GOLD_D
    t = 2 * math.pi * k / N - math.pi / 2
    for d in (0.6, 1.3, 2.0):
        if d < r - 1.0:
            f[math.floor(cx + d * math.cos(t)), math.floor(cy + d * math.sin(t))] = PUPIL
    f[math.floor(cx), math.floor(cy)] = BOW_D


def wait() -> list[dict]:
    """앉아서 두 앞발로 든 회중시계를 들여다본다 — 바늘이 돌고 꼬리 끝이 똑딱똑딱, 가끔 눈을 깜빡"""
    frames = []
    rig = Rig(15.5, 19.6, 0.0, 0.86)
    for k, ph in enumerate(phases()):
        tick = 1.4 if k % 2 else -1.4
        tp = [(3.6, 8.6), (6.6, 7.6), (7.6, -4.0), (7.6 + tick, -9.0)]
        wc = (0.0, 2.6)
        arms = (((-2.6, -0.6), (-1.9, 2.4)), ((2.6, -0.6), (1.9, 2.4)))
        f, _ = front(rig, mood="blink" if k == 6 else "smug", arms=arms, tail_pts=tp, head_ang=0.0)
        x, y = rig.world(*wc)
        watch(f, x, y + 0.2, 3.2, k)
        frames.append(finish(f))
    return frames


def teacup(f: dict, cx: int, cy: int, k: int) -> None:
    """김이 오르는 찻잔 — 접시 · 잔 · 손잡이"""
    m = raster([(cx - 3.5, cy - 2), (cx + 3.5, cy - 2), (cx + 2.6, cy + 2.4), (cx - 2.6, cy + 2.4)])
    solid(f, m, lambda p: TEA if p[1] == cy - 1 else CUP, OUT)
    solid(f, {(cx + 4, cy - 1), (cx + 5, cy - 1), (cx + 5, cy), (cx + 5, cy + 1), (cx + 4, cy + 1)}, CUP, OUT)
    for x in range(cx - 5, cx + 6):
        f[x, cy + 3] = CUP_D if abs(x - cx) < 5 else OUT
    for j in range(2):
        t = (k / N + j / 2) % 1
        y = cy - 3 - round(4 * t)
        x = cx - 1 + 2 * j + round(math.sin(2 * math.pi * t + j))
        f.setdefault((x, y), STEAM)


def busy() -> list[dict]:
    """작은 화살표 턱시도냥 + 찻잔 둘레를 젤리 발자국 여덟이 차례로 꾹꾹 돈다"""
    frames = []
    cx, cy = 21.5, 21.5
    for k, ph in enumerate(phases()):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = math.floor(cx + 7.0 * math.cos(a) - 1.0), math.floor(cy + 7.0 * math.sin(a) - 1.0)
            lag = (head - i) % 8
            if lag < 1:
                paw_print(f, x, y, BEAN, BEAN_D)
            elif lag < 3:
                paw_print(f, x, y, hx("f6a8b8d0"), hx("d9758ed0"))
            else:
                paw_print(f, x, y, hx("f6a8b888"), hx("d9758e88"))
        teacup(f, 21, 22, k)
        f.update(arrow_cat(k, small=True))
        frames.append(finish(f))
    return frames


def help_() -> list[dict]:
    """작은 화살표 턱시도냥 + 젤리 발자국으로 찍은 물음표 — 하나씩 차례로 꾹 눌린다(진해진다)"""
    frames = []
    cells = [(16 + 2 * i, 12 + 2 * j) for j, row in enumerate(QMARK) for i, ch in enumerate(row) if ch == "#"]
    for k, ph in enumerate(phases()):
        f = {}
        m = set()
        for i, (x, y) in enumerate(cells):
            d = (k * len(cells) / N - i) % len(cells)
            m |= disc(x + 1, y + 1, 1.25 + (0.45 if d < 1.5 else 0.0))
        solid(f, m, BEAN, BEAN_D)
        f.update(arrow_cat(k, small=True))
        frames.append(finish(f))
    return frames


def bust(f: dict, rig: Rig, mood="open", ears=("up", "up")) -> None:
    o, _ = front(rig, mood=mood, ears=ears, body="bust")
    f.update({p: c for p, c in o.items() if p[1] <= 30})


def person() -> list[dict]:
    """작은 화살표 턱시도냥 + 나비넥타이를 맨 신사 고양이 흉상 — 깜빡, 귀 까딱"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        bust(f, Rig(22.0, 24.5, 0.0, 0.62), "blink" if k == 6 else "open", ("up", "flick" if k in (9, 10) else "up"))
        f.update(arrow_cat(k, small=True))
        frames.append(finish(f))
    return frames


def pin() -> list[dict]:
    """작은 화살표 턱시도냥 + 빨간 지도 핀, 핀 머리 흰 동그라미 속에 나비넥타이 — 통통 튄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 13.0 + dy
        for x in range(19, 27):
            f.setdefault((x, 27), hx("00000040") if dy else hx("00000070"))
        solid(f, disc(cx, cy, 6.4) | raster([(cx - 4.6, cy + 3.4), (cx + 4.6, cy + 3.4), (cx, cy + 12.6)]), SIGN,
              SIGN_D)
        solid(f, disc(cx, cy, 4.4), WHITE, SIGN_D)
        # 날개 끝을 높게 — 납작하면 흰 동그라미 속 가로줄이라 진입 금지 표지로 읽힌다
        o, _, _ = draw(Rig(cx, cy, 0.0, 1.0), [bow_front((0, 0), 5.0, h=0.62)])
        f.update(o)
        f.update(arrow_cat(k, small=True))
        frames.append(finish(f))
    return frames


def cross() -> list[dict]:
    """가는 조준선 + 가운데 빨간 레이저 점(핫스팟). 오른쪽 아래에서 동공이 커진 턱시도냥이 엉덩이를 씰룩인다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for t in list(range(1, 11)) + list(range(20, 31)):
            f[t, 15] = OUT
            f[15, t] = OUT
        g = 2 if k % 4 < 2 else 1
        for p in disc(15.5, 15.5, 1.2 + g):
            f[p] = GLOW
        f[15, 15] = LASER
        wig = round(math.sin(2 * ph))
        rig = Rig(24.5 + wig, 31.6, 0.0, 0.62)
        o, _ = front(rig, mood="wide", ears=("up", "up"), body="sit", lift=(1.4, 1.4))
        f.update({p: c for p, c in o.items() if p[1] <= 30 and p[0] <= 30})
        frames.append(finish(f))
    return frames


HAND_PAW = (-12.4, -11.6)
HAND_SH = (-3.4, -1.0)
HAND = Rig(21.0, 18.6, 0.0, 0.86)


def hand() -> list[dict]:
    """옆으로 앉아 앞발 하나를 앞으로 높이 들어 콕 — 발끝은 그대로 두고 몸이 숨 쉬듯 들썩, 눈 깜빡, 꼬리 살랑"""
    frames = []
    for k, ph in enumerate(phases()):
        sw = math.sin(ph)
        tp = [(6.0, 7.6), (8.4, 6.8), (9.6 + 0.6 * sw, -2.0), (10.0 + 1.4 * sw, -8.0)]
        f, _ = side(HAND, "sit", mood="blink" if k == 5 else "open", head_ang=-6.0, tail_pts=tp, paw=HAND_PAW,
                    sh=HAND_SH)
        if k % 6 in (0, 1):   # 콕 — 발끝 둘레 반짝
            x, y = HAND.cell(*HAND_PAW)
            for d in ((-2, -1), (-2, 1), (0, -3)):
                f.setdefault((x + d[0], y + d[1]), hx("ffffffa8"))
        frames.append(finish(f))
    return frames


def ibeam() -> list[dict]:
    """스크래처 — 위 판 · 밧줄 기둥 · 아래 받침이 I. 오른쪽에 매달린 턱시도냥이 앞발로 박박 긁는다"""
    frames = []
    X = 7
    for k, ph in enumerate(phases()):
        f = {}
        for y in range(3, 29):
            for x in (X - 1, X, X + 1):
                f[x, y] = ROPE_D if (y + (x - X)) % 3 == 0 else ROPE
            f[X - 2, y] = OUT
            f[X + 2, y] = OUT
        for x in range(X - 5, X + 6):
            f[x, 1], f[x, 2] = PLANK, PLANK_D
            f[x, 29], f[x, 30] = PLANK, PLANK_D
        rig = Rig(15.6, 15.0, 0.0, 0.64)
        arms, marks = [], []
        for i, sh in enumerate(((-2.6, -1.2), (2.4, -0.8))):
            # 한 앞발이 기둥 높이 박혀 아래로 죽 긁어내리는 동안 다른 앞발은 떼어 위로 올린다 — 번갈아.
            # 두 발이 같은 높이에서 마주 오가면 박수로 읽힌다
            t = (k / 6 + i / 2) % 1
            if t < 0.66:
                s = t / 0.66
                tip = (-11.2, -15.0 + 12.0 * s)
                marks.append((tip, s))
            else:
                s = (t - 0.66) / 0.34
                tip = (-8.4, -3.0 - 12.0 * s)
            arms.append((sh, tip))
        tp = [(2.0, 9.0), (6.0, 11.0), (9.0 + 0.8 * math.sin(2 * ph), 16.0)]
        o, _ = front(rig, mood="smug" if k % 6 < 4 else "closed", body="stand", arms=tuple(arms), tail_pts=tp,
                     head_ang=-8.0, beans=(0, 1))
        # 긁는 발이 지나온 자리에 밧줄이 일어난 흰 자국 세 줄
        for (a, b), s in marks:
            x0, y0 = rig.cell(-11.2, -15.0)
            x1, y1 = rig.cell(a, b)
            for y in range(y0, y1):
                for dx in (-1, 1):
                    if (X + dx, y) in f:
                        f[X + dx, y] = hx("fff4dcff")
        f.update(o)
        frames.append(finish(f))
    return frames


def move() -> list[dict]:
    """앞모습으로 앉아 앞발을 번갈아 들며 사뿐사뿐 제자리 걸음 — 네 방향 빨간 화살촉이 바깥으로 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (14 + o), 15 + dy * (14 + o), dx, dy)
        s = math.sin(ph)
        lift = (2.2 * max(0.0, s), 2.2 * max(0.0, -s))
        rig = Rig(15.5, 18.8 - 0.4 * abs(s), 0.0, 0.6)
        tp = [(3.6, 8.6), (6.6, 7.6), (7.4 + 0.8 * s, -4.0)]
        g, _ = front(rig, mood="blink" if k == 9 else "open", lift=lift, tail_pts=tp)
        f.update(g)
        frames.append(finish(f))
    return frames


def no() -> list[dict]:
    """금지 표지 안에서 코를 치켜들고 눈을 감은 채 앞발 하나를 내밀어 '사양하겠소' — 고개를 홱 들었다 내린다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        R = 13.5
        ring = {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
        slash = set()
        for t in range(-90, 91):
            x, y = 15.5 + t / 100 * (R - 1.5) * 0.7071, 15.5 + t / 100 * (R - 1.5) * 0.7071
            slash |= disc(x, y, 1.3)
        solid(f, ring | slash, SIGN, SIGN_D)
        up = k in range(3, 10)
        rig = Rig(15.5, 20.6, 0.0, 0.66)
        arms = (((-2.6, -0.4), (-8.6, -3.6 if up else -2.6)), None)
        g, _ = front(rig, mood="closed" if up else "smug", arms=arms, head_ang=-14.0 if up else -4.0, beans=(0,),
                     ears=("up", "flat" if up else "up"), tail_pts=[(3.6, 8.6), (6.6, 7.6), (7.0, -5.0)])
        f.update({p: c for p, c in g.items() if 1 <= p[1] <= 30})
        frames.append(finish(f))
    return frames


TIP = (1.5, 29.5)


def pen() -> list[dict]:
    """깃펜을 쥐고 글씨를 쓰는 신사 — 깃털이 펜촉을 축으로 까딱이고 펜촉 뒤로 잉크 물결이 남는다. 펜촉이 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        d = math.radians(4.0 * math.sin(2 * ph))
        L = 26.0
        ang = math.radians(-50.0) + d
        ux, uy = math.cos(ang), math.sin(ang)
        tx, ty = TIP

        def P(t, o=0.0):
            return tx + ux * t - uy * o, ty + uy * t + ux * o
        vane = raster([P(6.0, 0), P(10.0, -2.4), P(20.0, -2.8), P(L, -0.6), P(L, 0.4), P(20.0, 2.0), P(10.0, 1.6)])
        solid(f, vane, lambda p: QUILL_D if ((p[0] - tx) * -uy + (p[1] - ty) * ux) > 0.6 else QUILL, OUT)
        # 깃대가 펜촉부터 깃털 끝까지 한 줄로 지나가야 깃털로 읽힌다 — 없으면 흰 날 + 자루라 칼이 된다
        for t in range(0, int(2 * L) - 2):
            x, y = P(t * 0.5)
            f[math.floor(x), math.floor(y)] = NIB if t < 7 else QUILL_D
        for t in (12.0, 17.0, 22.0):     # 깃털 가장자리의 갈라진 홈
            x, y = P(t, -2.6 if t < 20 else -2.0)
            f.pop((math.floor(x), math.floor(y)), None)
        for x in range(3, 3 + (k % 6) * 2):   # 잉크 물결
            f.setdefault((x, 29 - (1 if (x // 2) % 2 else 0)), hx("2a2a3aa0"))
        rig = Rig(21.0, 19.8, 0.0, 0.62)
        g, _ = front(rig, mood="blink" if k == 4 else "smug", arms=(((-2.6, -0.4), (-6.4, 2.6)), None),
                     tail_pts=[(3.6, 8.6), (6.6, 7.6), (7.2, -6.0)])
        for p, c in g.items():
            f[p] = c
        # 쥔 앞발이 깃대 위에 오게 한 번 더
        x, y = rig.world(-6.4, 2.6)
        f[math.floor(x), math.floor(y)] = WHITE
        f[math.floor(TIP[0]), math.floor(TIP[1])] = NIB
        frames.append(finish(f))
    return frames


CANE_TOP = (-5.8, -24.5)


def up() -> list[dict]:
    """뒷발로 서서 신사 지팡이를 머리 위로 곧게 치켜든다 — 지팡이 끝(맨 위)이 핫스팟. 꼬리 살랑, 깜빡"""
    frames = []
    rig = Rig(16.6, 21.0, 0.0, 0.74)
    for k, ph in enumerate(phases()):
        sw = math.sin(ph)
        grip = (-5.6, -9.0)
        cane = ("cane", any_of(bar(CANE_TOP, (-5.6, -6.0), 0.75), bar((-5.6, -6.0), (-3.4, -4.6), 0.75)),
                lambda a, b: GOLD if b < CANE_TOP[1] + 1.6 else CANE, True)
        arms = (((-2.6, -0.6), grip), ((2.6, -0.6), (4.4, 3.4)))
        tp = [(2.0, 8.0), (5.6, 8.0), (7.4 + 0.6 * sw, -2.0), (7.6 + 1.2 * sw, -7.0)]
        f, _ = front(rig, mood="blink" if k == 7 else "open", body="stand", arms=arms, tail_pts=tp,
                     extra=(), mid=(cane,), head_ang=-6.0)
        frames.append(finish(f))
    return frames


def walk_frames(rig_at) -> list[dict]:
    frames = []
    for k, ph in enumerate(phases()):
        frames.append(rig_at(k, ph))
    return frames


def we() -> list[dict]:
    """꼬리를 곧게 세우고 새침하게 걷는다 — 앞 반은 왼쪽으로, 뒤 반은 돌아서 오른쪽으로. 가는 쪽 화살촉이 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        half = k < N // 2
        j = k % (N // 2)
        x = 1.5 - 3.0 * j / (N // 2 - 1)        # 오른쪽 → 왼쪽으로 3칸
        rig = Rig(17.0 + x, 17.4, 0.0, 0.7)
        g, _ = side(rig, "walk", ph=2 * math.pi * j / (N // 2) * 2, mood="smug", head_ang=8.0)
        if not half:
            g = mirror(g)
        f.update(g)
        go = -1 if half else 1
        for sg in (-1, 1):
            o = 1 if sg == go and j % 3 < 2 else 0
            chevron(f, 15 + sg * (14 + o), 15, sg, 0)
        frames.append(finish(f))
    return frames


def ns() -> list[dict]:
    """제자리 수직 점프 — 웅크렸다(눌림) 쭉 늘어나 떠오르고 다시 내려앉는다. 위아래 화살촉"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        t = k / N
        h = max(0.0, math.sin(math.pi * (t - 0.17) / 0.66)) if 0.17 <= t <= 0.83 else 0.0
        squash = k in (0, 11)
        rig = Rig(15.5, 19.6 - 6.0 * h, 0.0, 0.58, sy=0.88 if squash else (1.0 + 0.1 * h))
        tp = [(2.0, 8.0), (4.6, 9.0), (5.4, 14.0)] if h > 0 else [(3.6, 8.6), (6.6, 7.6), (7.0, -4.0)]
        g, _ = front(rig, mood="open" if h > 0 else "blink", body="air" if h > 0 else "sit", tail_pts=tp,
                     ears=("up", "up"))
        f.update(g)
        for sg in (-1, 1):
            o = 1 if (sg < 0) == (h > 0.3) else 0
            chevron(f, 15, 15 + sg * (14 + o), 0, sg)
        frames.append(finish(f))
    return frames


def run_diag(flip: bool) -> list[dict]:
    """대각선으로 내달린다 — 앞 반은 왼쪽 위로(flip 이면 오른쪽 위로), 뒤 반은 돌아서 오른쪽 아래로.
    한 걸음에 다리를 쭉 폈다 배 밑에 모았다 하고 몸이 들썩인다. 가는 쪽 화살촉이 두근댄다.
    기지개로 몸을 늘였다 줄였다 하던 판은 몸통이 늘어나는 것으로 읽혀 달리기로 바꿨다"""
    frames = []
    h = N // 2
    for k in range(N):
        f = {}
        half = k < h
        j = k % h
        d = 1.6 - 3.2 * j / (h - 1)                # 대각선을 따라 앞으로 3칸쯤
        if half:
            rig = Rig(16.4 + d * 0.7071, 16.0 + d * 0.7071, 22.0, 0.7)
        else:
            rig = Rig(14.6 - d * 0.7071, 15.0 - d * 0.7071, 22.0, 0.7, flip=True)
        g, _ = side(rig, "run", ph=2 * math.pi * j / h, mood="open", head_ang=4.0)
        f.update(g)
        for sg in (-1, 1):
            o = 1 if (sg < 0) == half and j % 3 < 2 else 0
            if sg < 0:
                diag_chevron(f, 2 - o, 2 - o, -1, -1)
            else:
                diag_chevron(f, 28 + o, 28 + o, 1, 1)
        if flip:
            f = mirror(f)
        frames.append(finish(f))
    return frames


def nwse():
    return run_diag(False)


def nesw():
    return run_diag(True)


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def paw_tip(fr):
    """hand — 든 앞발의 끝(팔 방향으로 발 둥치 끝)"""
    ax, ay = HAND_PAW[0] - HAND_SH[0], HAND_PAW[1] - HAND_SH[1]
    d = math.hypot(ax, ay)
    return HAND.cell(HAND_PAW[0] + 0.6 * ax / d, HAND_PAW[1] + 0.6 * ay / d)


def top_cell(fr):
    """맨 위 불투명 칸(같으면 왼쪽)"""
    return min((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1], p[0]))


HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1),
       "wait": (15, 15), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (7, 15),
       "pen": (math.floor(TIP[0]), math.floor(TIP[1])), "hand": paw_tip, "up": top_cell}


def check(rid: str, frames: list[dict], hot: tuple) -> None:
    """핫스팟이 장마다 불투명한 칸 위에 있는지"""
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
        if hot == (1, 1) and any(c[3] == 255 and (p[0] < 1 or p[1] < 1) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 꼬리 끝보다 왼쪽·위로 나온 칸이 있음")
        if any(c[3] == 255 and not (0 <= p[0] <= 31 and 0 <= p[1] <= 31) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 판 밖 칸")


def main() -> None:

    def job(r):
        def run():
            frames = [{p: c for p, c in f.items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31} for f in SCENE[r]()]
            hot = HOT[r](frames) if callable(HOT[r]) else HOT[r]
            check(r, frames, hot)
            print(f"  {r} 핫스팟 {hot}")
            return frames, hot
        return run
    write(SID, {r: job(r) for r in SCENE}, sys.argv[1:] or None)


if __name__ == "__main__":
    main()

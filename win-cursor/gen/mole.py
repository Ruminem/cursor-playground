# SPDX-License-Identifier: Apache-2.0
"""두더지(moleanim) 구성표 그림 `art/moleanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/mole.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

숲속 친구들 · 애니 묶음(다람쥐 · 고슴도치 · 부엉이 · 토끼 · 여우 · 아기곰 · 아기사슴 · 너구리 · 두더지 · 개구리)의
한 마리. 칸마다 두더지가 그 칸 뜻에 맞는 짓을 따로 한다(`SCENE`).
치비 비율 — 짙은 회갈색 벨벳 털(왼쪽 위에 윤기) · 큰 동그란 머리와 몸이 목 없이 한 덩이 · 옅은 주둥이 둘레 ·
분홍 뾰족 코 · 작은 콩알 눈에 흰 반짝 · 분홍 볼터치 · 크고 넓은 분홍 앞발(크림 발톱 셋) · 짧은 분홍 꼬리.
쥐로 읽히지 않게 하는 표지는 둘이다 — 몸통만 한 삽 같은 앞발과 흙더미. 귀는 그리지 않는다(동그란 귀가
붙으면 바로 쥐다). 소품은 흙더미 · 흙 부스러기 · 지렁이 · 잔가지와 묶음 공통의 풀 덤불 · 풀잎 화살촉이다.

  arrow   왼쪽 위로 흙을 헤치고 나아가는 옆모습 — 분홍 코끝이 핫스팟. 큰 앞발이 평영처럼 흙을 긁어 뒤로 넘기고
          꼬리 뒤로 흙 부스러기가 튄다
  busy    작은 화살표 두더지 + 오른쪽 아래 흙더미에서 두더지가 쏙 솟았다 숨는다. 둘레를 흙덩이 여덟이 차례로 빛나며 돈다
  cross   앞모습 얼굴 — 코가 분홍 별코(촉수가 번갈아 꼼지락). 가는 뿌리 네 가닥이 조준선, 별코 가운데가 핫스팟
  hand    흙더미에서 솟아 큰 앞발 하나를 하이파이브하듯 펴 든다 — 발톱이 손가락처럼 벌어지고 가운데 발톱 끝이 핫스팟.
          톡톡 칠 때 발톱 위에 반짝
  help    작은 화살표 두더지 + 땅굴 둔덕으로 그린 물음표 — 파 나가는 앞머리가 글자를 따라 돌고, 점은 코만 내민 작은 흙더미
  ibeam   지렁이 국수 — 풀 띠(I 의 위 가로획)에서 흙 띠(아래 가로획)까지 늘어진 지렁이를 두 앞발로 위아래 쥐고 후루룩
          (입 벌리고 눈 감기). 앞발은 몸 · 지렁이 위에 따로 그린다(`grip`). 핫스팟은 지렁이 가운데
  move    흙더미에서 쏙 솟아 두리번거렸다 쏙 숨는다(두더지 잡기) — 네 방향 풀잎 화살촉. 첫 장은 솟은 모습. 핫스팟은 흙더미
  nesw · ns · nwse · we   그 축으로 몸을 쭉 뻗고 땅속을 헤엄치듯 파 나가는 옆모습 — 코끝과 꼬리가 양 끝이고 그 바깥에
          풀잎 화살촉, 앞발이 흙을 긁을 때마다 부스러기가 뒤로 튄다. ns 는 머리를 아래로 파 내려간다
  no      빨간 금지 표지 안 흙더미(빗금 왼쪽 아래) — 솟은 채 표지를 보고 눈을 질끈 감고 도리도리, 흙더미 속으로 쏙
          숨었다 다시 빼꼼. 핫스팟은 빗금 가운데
  pen     잔가지를 크레용처럼 두 앞발로 가슴 앞에 쥐고 흙바닥에 끼적인다 — 가지 끝(왼쪽 아래)이 핫스팟. 가지 중간 잎이
          살랑, 흙 위에 줄이 그어진다. 가지는 갈색 칸으로 바로 칠한다(테두리만 남은 가는 막대는 창으로 읽혔다)
  person  작은 화살표 두더지 + 불 켜진 안전모(광부 모자)를 쓴 사람이 손을 흔든다 — 모자 등이 깜빡
  pin     작은 화살표 두더지 + 흙더미 꼭대기에 꽂힌 빨간 지도 핀 — 밑에서 두더지가 밀어 올려 흙더미가 불룩, 핀이 들썩인다
  up      흙더미에서 하늘로 코를 쭉 내밀고 솟는 옆모습 — 위로 든 코끝이 핫스팟. 앞발로 흙을 헤치고 부스러기가 위로 튄다
  wait    흙더미에 반쯤 묻혀 두 앞발로 번갈아 흙을 퍼 올려 뒤로 넘긴다(굴 파는 중) — 핫스팟은 흙더미 가운데

몸은 부위(타원 · 굵기가 변하는 막대)를 두더지 제 좌표에 놓고 화면으로 돌려 찍는다(`Rig`, `draw` — 해달과 같은 틀).
앞모습(`front`)과 옆모습(`side`) 두 벌이다. 흙더미(`hill`)는 두더지 앞에 그리는 부위라 몸이 그 속으로 숨는다 —
흙더미 밑(땅속)으로 내려간 몸은 `front(ground=)` 가 잘라 낸다.
그리개는 gen/rabbit.py 와 같은 꼴이지만 다른 생성기를 import 하지 않으려고 여기 따로 둔다(다른 생성기를 고치면
이 그림이 조용히 바뀌지 않게). 숲 소품(풀 · 흙) 색과 꼴은 같은 묶음 생성기와 맞춘다.
빌드가 부르지 않고 손으로 돌린다 · 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, disc, finish, hx, ink, phases, raster, solid, write

SID = "moleanim"
OUT, EYE, HI = hx("2e2220ff"), hx("140d0cff"), hx("fffaf0ff")                  # 테두리 · 눈 · 반짝
FUR, FUR_L, FUR_D = hx("6f625fff"), hx("8e817cff"), hx("564a47ff")            # 벨벳 털 · 윤기 · 그늘
FACE = hx("b8a69cff")                                                         # 주둥이 둘레 옅은 털
PINK, PINK_D, NOSE = hx("f4a7b5ff"), hx("d9849aff"), hx("ec7590ff")           # 앞발 · 먼 앞발 · 코
CLAW, BLUSH, MOUTH = hx("fff3e2ff"), hx("f7a0a8ff"), hx("3a2826ff")           # 발톱 · 볼 · 입
ink(OUT, HI, hx("f6e9d2c7"))
GRASS, GRASS_D, GRASS_L = hx("5aa04aff"), hx("3f7a35ff"), hx("86c46aff")      # 풀 · 풀잎 (묶음 공통)
SOIL, SOIL_D, SOIL_L = hx("8a6a44ff"), hx("5e4628ff"), hx("ab8858ff")         # 흙
CRUMB, CRUMB_D = hx("8a6a44e0"), hx("5e4628e0")                               # 튀는 부스러기 — 반투명이라 테를 안 두른다
TWIG, TWIG_D = hx("9a6a3cff"), hx("5c3a1eff")                                 # 잔가지
WORM, WORM_D = hx("e8909aff"), hx("c06a78ff")                                 # 지렁이
SKIN, SHIRT, SHIRT_D = hx("f4e2c4ff"), hx("4a7fb5ff"), hx("2e5a88ff")          # 사람
HAT, HAT_D, LAMP, LAMP_OFF = hx("f5c542ff"), hx("c9962aff"), hx("fffbe0ff"), hx("b8b0a0ff")   # 안전모 · 등


# ── 그리개: 두더지 제 좌표 (a, b) → 화면 ─────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도, a 축이 화면에서 가리키는 쪽, 90 이 아래) · 배율 k · 뒤집기 fl.
    b 축은 a 축을 시계 방향으로 90도 돌린 쪽(ang=0 이면 a 가 오른쪽, b 가 아래). fl 이면 b 축을 반대로"""

    def __init__(self, ox: float, oy: float, ang: float = 0.0, k: float = 1.0, fl: bool = False):
        t = math.radians(ang)
        self.ox, self.oy, self.c, self.s = ox, oy, math.cos(t), math.sin(t)
        self.k = k
        self.kx, self.ky = k, k * (-1 if fl else 1)

    def world(self, a: float, b: float) -> tuple:
        a, b = a * self.kx, b * self.ky
        return self.ox + a * self.c - b * self.s, self.oy + a * self.s + b * self.c

    def local(self, x: float, y: float) -> tuple:
        dx, dy = x - self.ox, y - self.oy
        return (dx * self.c + dy * self.s) / self.kx, (-dx * self.s + dy * self.c) / self.ky

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


def above(h, ground):
    """ground 보다 위(b 가 작은 쪽)만 남긴 맞음 — 흙더미 밑 땅속으로 내려간 몸을 자른다"""
    if ground is None:
        return h
    return lambda a, b: b < ground and h(a, b)


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


def velvet(cu: float, cw: float, r: float):
    """벨벳 털 색 — 왼쪽 위 (cu, cw) 둘레 r 안은 윤기, 아래쪽은 그늘"""
    def col(a, b):
        if (a - cu) ** 2 + (b - cw) ** 2 < r * r:
            return FUR_L
        return FUR
    return col


def hill(cu: float, base: float, hw: float, ht: float, name: str = "hill"):
    """흙더미 부위 — (cu, base) 를 밑동 가운데로 반폭 hw · 높이 ht 인 둥근 언덕. 꼭대기 쪽은 밝고 흙덩이 점이 박힌다"""
    shape = lambda a, b: b <= base and ((a - cu) / hw) ** 2 + ((b - base) / ht) ** 2 <= 1   # noqa: E731

    def col(a, b):
        t = (base - b) / ht
        if (math.floor(a * 0.9) * 5 + math.floor(b * 0.9) * 3) % 7 == 0 and t < 0.8:
            return SOIL_D
        return SOIL_L if t > 0.62 else SOIL
    return (name, shape, col, True)


def claws(paw_c, deg: float, r: float, n: int = 3, spread: float = 30.0, ln: float = 1.3, mid: float = 0.0,
          w: float = 0.8):
    """앞발 가장자리에서 deg(0 이 위 -b, + 가 +a 쪽) 쪽으로 뻗은 발톱 n 개. mid 는 가운데 발톱을 더 늘인 길이.
    → (맞음, 발톱 심 선분들). 발톱은 굵기가 두 칸 남짓이라 그리면 테두리만 남는다 — 심 선분을 `nails` 로 크림색 칠한다"""
    hs, segs = [], []
    for i in range(n):
        d = math.radians(deg + spread * (i - (n - 1) / 2))
        ux, uy = math.sin(d), -math.cos(d)
        p0 = (paw_c[0] + ux * r * 0.6, paw_c[1] + uy * r * 0.6)
        L = r * 0.4 + ln + (mid if i == (n - 1) // 2 and n % 2 else 0.0)
        p1 = (p0[0] + ux * L, p0[1] + uy * L)
        hs.append(bar(p0, p1, w, w * 0.75))
        segs.append(((paw_c[0] + ux * r * 0.75, paw_c[1] + uy * r * 0.75), p1))
    return any_of(*hs), segs


def nails(out: dict, mask: set, rig: Rig, segs, keep=lambda a, b: True) -> None:
    """발톱 심을 크림색으로 — 선분의 밑동부터 끝 한 칸 앞까지, 몸 칸 위에만"""
    for p0, p1 in segs:
        n = 12
        for i in range(n):
            t = i / n * 0.86
            a, b = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
            q = rig.cell(a, b)
            x, y = q
            inner = all(n in mask for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
            if inner and out.get(q) != OUT and keep(a, b):
                out[q] = CLAW


# ── 앞모습: u 가로(+오른쪽), w 세로(+아래), 원점은 얼굴 가운데(코 바로 위) ────────────────
def front(rig: Rig, mood: str = "smile", paws=((-5.6, 4.6, -60), (5.6, 4.6, 60)), ground=None, hills=(),
          extra=(), mid=(), star: int = -1, nose: int = 0, mouth: bool = False, big_eye: bool = True,
          five: int = -1) -> tuple[dict, set]:
    """앞모습 두더지 한 장. paws 는 앞발마다 (u, w, 발톱이 가리키는 각 — 0 이 위, + 가 오른쪽). ground 를 주면 그 w 아래
    (땅속)는 안 그린다. hills 는 두더지 앞에 그리는 흙더미 부위들, extra 는 맨 앞 부위, mid 는 앞발 뒤 · 머리 앞 부위(쥔 가지). star 가 0 이상이면 코를 별코로
    (값은 꼼지락 위상), nose 는 뾰족 코가 씰룩인 칸(0 · 1), mouth 면 입을 벌렸다(후루룩).
    five 가 0 이상인 앞발은 발톱 다섯을 손가락처럼 부채꼴로 편다(하이파이브)"""
    pads, cl, segs, arms = [], [], [], []
    for i, (pu, pw, deg) in enumerate(paws or ()):
        if i == five:   # 가리키는 앞발: 가운데 발톱 하나를 검지처럼 길게, 양옆은 짧은 마디
            pads.append(ell(pu, pw, 2.8, 2.6))
            h, sg_ = claws((pu, pw), deg, 2.6, n=1, ln=3.6, w=1.55)
            h2, _ = claws((pu, pw), deg, 2.6, n=4, spread=34.0, ln=0.5, w=1.0)
            pads.append(h2)
            arms.append(bar((math.copysign(4.0, pu), 3.0), (pu, pw), 1.8, 1.6))
        else:
            pads.append(ell(pu, pw, 2.5, 2.1, math.radians(deg)))
            h, sg_ = claws((pu, pw), deg, 2.3, spread=42.0, ln=1.6, w=0.75)
        cl.append(h)
        segs += sg_
    head = any_of(ell(0.0, -0.2, 5.7, 5.1), ell(0.0, 5.4, 6.2, 4.8))
    sheen = velvet(-2.4, -3.0, 2.0)

    def headc(a, b):
        if b > 0.0 and (a / 2.9) ** 2 + ((b - 1.6) / 2.2) ** 2 <= 1:
            return FACE
        if b > 6.8:
            return FUR_D
        return sheen(a, b)
    parts = list(extra)
    if pads:
        parts += [("claw", above(any_of(*cl), ground), CLAW, False), ("paw", above(any_of(*pads), ground), PINK, True)]
    parts += list(mid) + list(hills)
    if arms:
        parts += [("arm", above(any_of(*arms), ground), FUR, False)]
    parts += [("head", above(head, ground), headc, False)]
    out, mask, _ = draw(rig, parts)
    nails(out, mask, rig, segs, lambda a, b: ground is None or b < ground)

    def put(a, b, c):   # 몸 위에만 찍는다 — 흙더미에 묻힌 자리엔 안 찍는다
        p = rig.cell(a, b)
        if p in mask and (ground is None or b < ground):
            out[p] = c
    for sg in (-1, 1):
        ex = sg * 2.5 - (0.6 if big_eye else 0.2)
        if mood == "smile":
            if (ground is None or -1.0 < ground):
                eye(out, rig, ex, -1.2, big_eye)
        elif mood in ("blink", "squint"):
            if ground is None or -1.0 < ground:
                eye(out, rig, ex, -1.2, big_eye, shut=True)
        put(sg * 3.9, 1.4, BLUSH)
    x, y = rig.cell(-0.3, 0.6)
    if ground is None or 0.6 < ground:
        if star >= 0:   # 분홍 별코 — 가운데 둘레로 촉수가 번갈아 꼼지락
            out[x, y] = NOSE
            for i, (dx, dy) in enumerate(((0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1))):
                out[x + dx, y + dy] = PINK
                if (i + star) % 2 == 0:
                    out[x + 2 * dx, y + 2 * dy] = PINK if dx == 0 or dy == 0 else NOSE
        else:   # 뾰족한 분홍 코 — 위는 옅고 아래 끝이 짙다
            y -= nose
            out[x, y], out[x + 1, y] = PINK, PINK
            out[x, y + 1], out[x + 1, y + 1] = NOSE, NOSE
            if mouth:
                out[x, y + 3], out[x + 1, y + 3] = MOUTH, MOUTH
                out[x, y + 4], out[x + 1, y + 4] = BLUSH, BLUSH
    return out, mask


# ── 옆모습: a 는 코끝 0 → 꼬리, b 는 + 가 배(발) 쪽 ─────────────────────────────
def side(rig: Rig, stroke: float = 0.0, shut: bool = False, nose: int = 0, simple: bool = False, extra=(),
         big_eye: bool = True, ground=None, reach: float = 5.0) -> tuple[dict, set]:
    """옆모습 두더지 한 장. 코끝이 원점 근처. stroke 는 앞발 젓기 위상(라디안) — 앞발이 앞으로 뻗었다가 배 밑으로
    흙을 긁어 넘긴다. reach 는 앞발 밑동의 a(작을수록 코 쪽으로 뻗는다 — 화살표는 코끝보다 왼쪽으로 안 나가게 어깨에 둔다).
    먼 앞발은 반 박자 늦게 짙은 분홍으로 몸 뒤에 둔다. nose 는 코끝이 씰룩인 칸.
    simple 이면 작게 그릴 때라 먼 앞발 · 뒷발을 빼고 머리 · 앞발만 선을 긋는다. ground 를 주면 a 가 그보다 큰 몸(땅속)은 안 그린다"""
    def paw_at(t):
        c = math.cos(t)
        return (reach + 3.0 * (1 - c) / 2, 6.4 + 0.8 * math.sin(t))
    np_ = paw_at(stroke)
    fp = paw_at(stroke + math.pi)
    fp = (fp[0] + 2.0, fp[1] - 0.6)
    deg = 235 - 45 * (1 - math.cos(stroke)) / 2      # 발톱은 앞쪽 아래(-a, +b)를 보다가 긁어 넘길 때 아래로
    sheen = velvet(8.6, -2.0, 2.2)

    def bodyc(a, b):
        if b < -2.4 and a > 10.0:
            return FUR_L
        return FUR_D if b > 5.0 else FUR

    def headc(a, b):
        if a < 6.0 and b > 0.0:
            return FACE
        return sheen(a, b)
    cut = (lambda h: h) if ground is None else (lambda h: (lambda a, b: a < ground and h(a, b)))
    near_cl, segs = claws(np_, deg, 3.0, n=3, spread=30.0, ln=1.6)
    far_cl, _ = claws(fp, deg, 2.2)
    parts = list(extra) + [
        ("tip", cut(bar((0.3, 0.6), (2.6, 0.8), 0.75, 1.2)), PINK, False),
        ("claw", cut(near_cl), PINK, False),
        ("paw", cut(ell(np_[0], np_[1], 2.5, 3.2, math.radians(deg))), PINK, True),
        ("snout", cut(bar((2.2, 0.8), (6.0, 1.1), 1.15, 2.7)), FACE, False),
        ("head", cut(ell(8.4, 1.0, 4.9, 4.7)), headc, False),
        ("hind", cut(ell(18.0, 6.4, 1.9, 1.2)), PINK, True),
        ("tail", cut(bar((19.8, 1.2), (22.0, 0.2), 0.75, 0.55)), PINK, True),
        ("body", cut(ell(13.6, 1.8, 6.6, 5.4)), bodyc, False),
        ("far_claw", cut(far_cl), PINK_D, False),
        ("far_paw", cut(ell(fp[0], fp[1], 1.7, 2.4, math.radians(deg))), PINK_D, False)]
    if simple:
        parts = [(n, h, c, ln and n in ("head", "paw")) for n, h, c, ln in parts
                 if n not in ("far_paw", "far_claw", "hind")]
    out, mask, _ = draw(rig, parts)
    if not simple:
        nails(out, mask, rig, segs, lambda a, b: ground is None or a < ground)
    eye(out, rig, 6.4, -0.8, big_eye, shut)
    dot(out, rig, 8.6, 2.4, BLUSH)
    dot(out, rig, 1.0 - 0.5 * nose, 0.9, NOSE)
    return out, mask


ARROW = Rig(1.75, 0.95, 38.0, 1.05)      # 화살표 두더지: 코끝이 (1, 1)
ARROW_S = Rig(1.7, 1.1, 38.0, 0.6)     # 작은 화살표 두더지 (busy · help · person · pin)


def arrow_mole(k: int, small: bool = False) -> dict:
    ph = 2 * math.pi * k / N
    return side(ARROW_S if small else ARROW, stroke=ph, nose=1 if k % 4 == 1 else 0, shut=(k == 9),
                simple=small, big_eye=not small, reach=8.0)[0]


# ── 숲 소품 ──────────────────────────────────────────────────────────────────
def tuft(f: dict, x0: int, x1: int, y: int, k: int = 0) -> None:
    """풀 덤불: y 줄을 밑동으로 높이가 들쭉날쭉한 풀잎. k 로 잎끝이 살랑인다 (토끼 · 고슴도치와 같은 꼴)"""
    for x in range(x0, x1 + 1):
        h = (2, 3, 1, 4, 2, 3, 1)[(x * 3) % 7]
        for j in range(h):
            f[x, y - j] = GRASS_D if j == 0 else GRASS if j < h - 1 else GRASS_L
        if h >= 3 and (x + k) % 4 == 0:
            f.pop((x, y - h + 1), None)
            f[x + 1, y - h + 1] = GRASS_L


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col) -> None:
    """(dx, dy) 쪽을 가리키는 풀잎 화살촉. 꼭짓점이 (cx, cy)"""
    px, py = -dy, dx
    for i in range(4):
        for s in (-1, 1):
            for w in (0, 1):
                f[cx - dx * (i + w) + s * px * i, cy - dy * (i + w) + s * py * i] = col


def sign(f: dict, R: float = 13.5, ring: bool = True, slash: bool = True) -> None:
    """빨간 금지 표지(sea 의 SIGN 색). 고리와 빗금을 따로 — 빗금을 몸 앞에 긋는다"""
    cells = set()
    if ring:
        cells |= {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
    if slash:
        for t in range(-90, 91):
            x, y = 15.5 + t / 100 * (R - 1.5) * 0.7071, 15.5 + t / 100 * (R - 1.5) * 0.7071
            cells |= disc(x, y, 1.3)
    solid(f, cells, SIGN, SIGN_D)


def clod(f: dict, x0: int, y0: int, alpha: int = 255) -> None:
    """2×2 흙덩이 — 왼쪽 위가 밝다. alpha 가 낮으면 흐리게(도는 고리의 꼬리)"""
    for (dx, dy), c in (((0, 0), SOIL_L), ((1, 0), SOIL), ((0, 1), SOIL), ((1, 1), SOIL_D)):
        f[x0 + dx, y0 + dy] = c[:3] + (alpha,)


def fling(f: dict, rig: Rig, a0: float, b0: float, da: float, db: float, k: int, n: int = 3, h: float = 3.0) -> None:
    """흙 부스러기 n 개가 (a0, b0) 에서 (da, db) 쪽으로 포물선을 그리며 튄다 — 두더지 제 좌표에서 h 만큼 -b 로 솟는다"""
    for j in range(n):
        t = (k / N * 2 + j / n) % 1
        a = a0 + da * t * (0.7 + 0.3 * j / n)
        b = b0 + db * t - h * 4 * t * (1 - t)
        f.setdefault(rig.cell(a, b), CRUMB if j % 2 else CRUMB_D)


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    """왼쪽 위로 흙을 헤치고 나아간다 — 큰 앞발이 평영처럼 코 옆으로 뻗었다가 흙을 긁어 넘기고, 꼬리 뒤로
    부스러기가 튄다. 코끝은 제자리(핫스팟)이고 씰룩인다"""
    frames = []
    for k in range(N):
        f = arrow_mole(k)
        fling(f, ARROW, 18.0, 4.0, 9.0, 1.0, k, 3, 2.4)
        frames.append(finish(clip(f)))
    return frames


WAIT = Rig(15.5, 10.4, 0.0, 0.92)


def wait() -> list[dict]:
    """흙더미에 반쯤 묻혀 두 앞발로 번갈아 흙을 퍼 올려 어깨 너머로 넘긴다 — 굴 파는 중. 퍼 올린 쪽으로 흙이 튀고
    가끔 눈을 끔뻑. 핫스팟은 흙더미 가운데"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        tuft(f, 1, 30, 30, k)
        s = math.sin(ph)
        lp = (-6.0, 3.4 - 2.6 * max(0.0, s), -40 - 30 * max(0.0, s))
        rp = (6.0, 3.4 - 2.6 * max(0.0, -s), 40 + 30 * max(0.0, -s))
        o, _ = front(WAIT, "blink" if k == 10 else "smile", paws=(lp, rp), ground=8.6,
                     hills=[hill(0.0, 21.5 / 0.92 - 10.4 / 0.92 + 0.3, 11.0, 8.8)], nose=k % 3 == 1)
        f.update(o)
        sg = -1 if s > 0 else 1   # 퍼 올린 발 쪽으로 튄다
        fling(f, WAIT, sg * 7.0, 0.0, sg * 6.0, 3.0, k, 3, 4.0)
        frames.append(finish(clip(f)))
    return frames


def cross() -> list[dict]:
    """앞모습 얼굴 — 코가 분홍 별코라 촉수가 번갈아 꼼지락. 가는 뿌리 네 가닥이 조준선, 별코 가운데가 핫스팟"""
    frames = []
    rig = Rig(15.8, 14.4, 0.0, 0.92)   # 별코 가운데 칸이 (15, 15)
    for k, ph in enumerate(phases()):
        f = {}
        for i in range(1, 31):
            if i < 6 or i > 25:
                f[i, 15] = TWIG_D
                f[15, i] = TWIG_D
        for sg in (-1, 1):   # 뿌리 끝 잔뿌리
            f[15 + sg * 12 + (1 if sg > 0 else 0) - sg, 14 + (k // 3) % 2] = TWIG_D
        o, _ = front(rig, "blink" if k == 8 else "smile", paws=((-5.4, 6.4, -50), (5.4, 6.4, 50)), star=k % 2)
        f.update(o)
        frames.append(finish(clip(f)))
    return frames


HAND = Rig(17.2, 15.6, 0.0, 0.86)
HAND_PAW = (-7.6, -6.6)   # 머리 옆 바깥으로 든 앞발 — 머리 위에 들면 귀로 읽힌다


def hand() -> list[dict]:
    """흙더미에서 솟아 큰 앞발 하나를 하이파이브하듯 펴 든다 — 발톱 다섯이 손가락처럼 벌어지고 가운데 발톱 끝이
    핫스팟. 톡톡 칠 때 발톱 위에 반짝, 다른 앞발은 흙더미를 짚었다"""
    frames = []
    for k, ph in enumerate(phases()):
        poke = max(0.0, math.sin(2 * ph))
        paw = (HAND_PAW[0], HAND_PAW[1] - 0.9 * poke, -8)
        f = {}
        o, _ = front(HAND, "blink" if k == 9 else "smile", paws=(paw, (5.4, 7.0, 40)), ground=10.0,
                     hills=[hill(0.0, 15.6, 9.6, 7.0)], five=0, nose=k % 4 == 2)
        f.update(o)
        if poke > 0.9:
            x, y = HAND.cell(paw[0] - 0.4, paw[1] - 6.6)
            for q in ((x - 2, y), (x + 2, y), (x - 2, y - 2), (x + 2, y - 2)):
                f.setdefault(q, HI)
        frames.append(finish(clip(f)))
    return frames


def popper(f: dict, rig: Rig, rise: float, k: int, mood: str = "smile", hw: float = 7.0, ht: float = 4.6,
           paws=True) -> None:
    """흙더미 하나와 거기서 rise(0 숨음 – 1 다 솟음)만큼 솟은 두더지. rig 원점이 흙더미 밑동 가운데"""
    lift = 9.6 * rise                    # 얼굴 가운데가 밑동 위로 올라온 거리
    face = Rig(rig.ox, rig.oy - lift * rig.k, 0.0, rig.k)
    base = lift
    pw = ((-5.2, 4.4, -40), (5.2, 4.4, 40)) if paws else None
    o, _ = front(face, mood, paws=pw, ground=base - 1.0, hills=[hill(0.0, base, hw, ht)], nose=k % 3 == 1)
    f.update(o)


def busy() -> list[dict]:
    """작은 화살표 두더지 + 오른쪽 아래 흙더미에서 두더지가 쏙 솟았다 숨는다 — 둘레를 흙덩이 여덟이 차례로 빛나며 돈다"""
    frames = []
    cx, cy = 22.0, 22.0
    for k in range(N):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = math.floor(cx + 7.6 * math.cos(a)), math.floor(cy + 7.6 * math.sin(a))
            lag = (head - i) % 8
            clod(f, x - 1, y - 1, 255 if lag < 1 else 220 if lag < 2 else 170 if lag < 3 else 120)
        rise = 0.5 + 0.5 * math.sin(2 * math.pi * k / N)
        popper(f, Rig(cx, cy + 3.6, 0.0, 0.52), rise, k, "smile" if rise > 0.3 else "blink", 9.0, 6.0, paws=False)
        f.update(arrow_mole(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def help_() -> list[dict]:
    """작은 화살표 두더지 + 땅굴 둔덕으로 그린 물음표 — 흙이 불룩 솟은 앞머리가 글자를 따라 돌고, 점은 코만 내민
    작은 흙더미"""
    frames = []
    cells = [(17.6 + 2.2 * i, 11.0 + 2.2 * j) for j, row in enumerate(QMARK[:-1]) for i, ch in enumerate(row)
             if ch == "#"]
    order = [0, 1, 2, 3, 4, 5, 6, 7, 8]   # QMARK 위에서부터 — 고리 → 꼬리
    for k in range(N):
        f = {}
        m, big = set(), set()
        n = len(cells)
        lead = k * n / N
        for i in order[:n]:
            x, y = cells[i]
            d = (lead - i) % n
            (big if d < 1.0 else m).update(disc(x, y, 1.25 + (0.55 if d < 1.0 else 0.0)))
        solid(f, m, SOIL, OUT)
        solid(f, big - m, SOIL_L, OUT)
        for p in m:   # 흙덩이 점
            if (p[0] * 5 + p[1] * 3) % 7 == 0 and f[p] == SOIL:
                f[p] = SOIL_D
        hx_, hy = 22, 27
        o, _, _ = draw(Rig(hx_, hy + 1, 0.0, 1.0), [hill(0.0, 0.0, 3.2, 2.6)])
        f.update(o)
        f[hx_ - 1, hy - 2] = PINK if k % 4 < 2 else NOSE    # 흙더미 꼭대기에 코끝만 빼꼼
        f[hx_, hy - 2] = PINK if k % 4 < 2 else NOSE
        f.update(arrow_mole(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def person() -> list[dict]:
    """작은 화살표 두더지 + 불 켜진 안전모(광부 모자)를 쓴 사람이 손을 흔든다 — 모자 등이 깜빡"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        rig = Rig(22.5, 20.4, 0.0, 0.56)
        wave = -2.4 * abs(math.sin(ph))
        hand_ = (8.6, 3.0 + wave)
        parts = [("hand", ell(*hand_, 1.8, 1.8), SKIN, True), ("sleeve", bar((5.4, 9.0), hand_, 1.7), SHIRT, False),
                 ("brim", bar((-6.4, -2.2), (6.4, -2.2), 0.9), HAT_D, True),
                 ("hat", lambda a, b: b < -2.0 and (a / 5.6) ** 2 + ((b + 2.0) / 5.4) ** 2 <= 1,
                  lambda a, b: hx("fbe08aff") if a < -2.0 and b < -4.0 else HAT, True),
                 ("face", ell(0.0, 1.4, 5.0, 4.4), SKIN, True),
                 ("torso", ell(0.0, 12.0, 7.6, 6.2), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
        o, _, _ = draw(rig, parts)
        for sg in (-1, 1):
            eye(o, rig, sg * 2.4 - 0.8, 1.0, big=False, shut=(k == 6))
        lx, ly = rig.cell(-0.9, -4.6)   # 모자 등
        on = k % 4 < 2
        o[lx, ly], o[lx + 1, ly] = (LAMP, LAMP) if on else (LAMP_OFF, LAMP_OFF)
        if on:
            for q in ((lx - 1, ly - 2), (lx + 2, ly - 2), (lx + 3, ly - 1), (lx - 2, ly - 1)):
                o.setdefault(q, hx("fffbe0b0"))
        f.update({p: c for p, c in o.items() if p[1] <= 30})
        f.update(arrow_mole(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def pin() -> list[dict]:
    """작은 화살표 두더지 + 흙더미 꼭대기에 꽂힌 빨간 지도 핀 — 밑에서 두더지가 밀어 올려 흙더미가 불룩 솟고
    핀이 들썩인다. 다 솟으면 흙더미 옆구리로 코가 빼꼼"""
    frames = []
    for k in range(N):
        f = {}
        push = max(0.0, math.sin(2 * math.pi * k / N))
        ht = 4.0 + 2.6 * push
        base = 29.6
        o, _, _ = draw(Rig(22.0, base, 0.0, 1.0), [hill(0.0, 0.0, 7.4, ht)])
        f.update(o)
        cx, cy = 22.5, base - ht - 8.4
        solid(f, disc(cx, cy, 5.6) | raster([(cx - 3.8, cy + 3.2), (cx + 3.8, cy + 3.2), (cx, cy + 9.4)]),
              SIGN, SIGN_D)
        solid(f, disc(cx, cy, 2.6), hx("fff4f0ff"), SIGN_D)
        if push > 0.8:   # 흙더미 옆구리로 코 빼꼼 + 튄 흙
            f[16, 28], f[17, 28] = PINK, NOSE
            f.setdefault((14, 24), CRUMB)
            f.setdefault((29, 25), CRUMB_D)
        f.update(arrow_mole(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def grip(rig: Rig, pts, deg: float, ln: float = 1.4) -> dict:
    """쥔 앞발들 — 몸 · 쥔 것 위에 따로 그린다. pts 는 앞발 가운데(제 좌표), deg 는 발톱이 감아쥐는 쪽"""
    cl, segs, pads = [], [], []
    for gu, gw in pts:
        pads.append(ell(gu, gw, 2.9, 2.3))
        h, sg_ = claws((gu, gw), deg, 2.6, spread=38.0, ln=ln, w=0.8)
        cl.append(h)
        segs += sg_
    po, pm, _ = draw(rig, [("claw", any_of(*cl), CLAW, False), ("paw", any_of(*pads), PINK, True)])
    nails(po, pm, rig, segs)
    return po


IX = 9   # I 기둥(지렁이) 왼쪽 칸


def ibeam() -> list[dict]:
    """지렁이 국수 — 풀 띠(I 의 위 가로획)에서 흙 띠(아래 가로획)까지 늘어진 지렁이를 두 앞발로 쥐고 후루룩.
    후루룩 할 때 지렁이 마디가 한 칸 내려가고 두더지가 눈을 감는다. 핫스팟은 지렁이 가운데"""
    frames = []
    for k, ph in enumerate(phases()):
        slurp = k % 6 in (2, 3, 4)
        sh = 1 if slurp else 0
        rig = Rig(IX + 6.4, 13.6, 0.0, 0.74)
        f, _ = front(rig, "blink" if slurp else "smile", paws=None, mouth=slurp, nose=0, big_eye=True)
        for y in range(4, 28):   # 지렁이 — 2칸 굵기, 마디 고리가 흘러내린다
            ring = (y - sh) % 4 == 0
            f[IX, y] = WORM_D if ring else WORM
            f[IX + 1, y] = WORM_D
        for x in range(IX - 3, IX + 5):   # 위 풀 띠 — 가로획
            end = x in (IX - 3, IX + 4)
            f[x, 2 + (1 if end and k % 6 < 3 else 0)] = GRASS_L if x < IX + 1 else GRASS
            f[x, 3] = GRASS_D
        for x in range(IX - 4, IX + 6):   # 아래 흙 띠 — 가로획
            f[x, 28] = SOIL
            f[x, 29] = SOIL_D
        f[IX - 2, 27], f[IX + 3, 27] = SOIL, SOIL
        # 두 앞발로 지렁이를 위아래로 쥔다 — 몸 · 지렁이 위에
        f.update(grip(rig, [rig.local(IX + 2.0, 13.0), rig.local(IX + 2.0, 17.4)], -90.0, ln=0.5))
        frames.append(finish(clip(f)))
    return frames


TIP, BACK = (1.5, 29.5), (19.6, 15.0)   # 잔가지 끝 · 윗끝(화면) — 윗끝은 두더지 가슴 앞


def pen() -> list[dict]:
    """잔가지를 크레용처럼 두 앞발로 꼭 쥐고 흙바닥에 끼적인다 — 가지 끝이 핫스팟. 두더지와 가지가 끝을 축으로
    살짝 까딱이고, 가지 중간에 돋은 잎이 살랑, 가지 끝 오른쪽 흙 위에 끼적인 줄이 자란다.
    가지는 갈색 칸으로 바로 칠하고(테두리만 남는 가는 막대가 창으로 읽혔다) 앞발은 가지 위에 따로 그린다"""
    frames = []
    base = Rig(21.0, 11.4, 0.0, 0.76)
    for k, ph in enumerate(phases()):
        d = math.radians(3.0 * math.sin(2 * ph))
        cs, sn = math.cos(d), math.sin(d)

        def rot(x, y):   # 가지 끝을 축으로 d 만큼
            return TIP[0] + (x - TIP[0]) * cs - (y - TIP[1]) * sn, TIP[1] + (x - TIP[0]) * sn + (y - TIP[1]) * cs
        rig = Rig(*rot(base.ox, base.oy), math.degrees(d), base.k)
        f = {}
        for i in range(min(k, 9) + 1):   # 끼적인 줄 — 물결
            f[3 + i, 30 - (1 if i % 4 in (1, 2) else 0)] = SOIL_D
        o, _ = front(rig, "blink" if k == 4 else "smile", paws=None, nose=k % 4 == 1)
        f.update(o)
        bx, by = rot(*BACK)
        cells = set()
        for i in range(41):   # 끝은 가늘고 위로 갈수록 굵다
            t = i / 40
            cells |= disc(TIP[0] + (bx - TIP[0]) * t, TIP[1] + (by - TIP[1]) * t, 0.7 + 0.9 * t)
        lx, ly = rot(TIP[0] + (BACK[0] - TIP[0]) * 0.45, TIP[1] + (BACK[1] - TIP[1]) * 0.45)
        sway = 0.5 * math.sin(2 * ph)
        leaf = disc(lx + 2.2 + sway, ly + 0.6, 1.5) | disc(lx + 3.6 + sway, ly - 0.2, 1.1)
        solid(f, leaf - cells, GRASS, GRASS_D)
        solid(f, cells, TWIG, TWIG_D)
        # 앞발 둘이 가지 윗동을 위아래로 겹쳐 쥔다 — 몸 · 가지 위에 따로 그린다
        pts = [rig.local(*rot(TIP[0] + (BACK[0] - TIP[0]) * t, TIP[1] + (BACK[1] - TIP[1]) * t)) for t in (0.8, 0.97)]
        f.update(grip(rig, pts, -100.0))
        f[math.floor(TIP[0]), math.floor(TIP[1])] = TWIG_D
        frames.append(finish(clip(f)))
    return frames


def up() -> list[dict]:
    """흙더미에서 하늘로 코를 쭉 내밀고 솟는 옆모습 — 위로 든 코끝이 핫스팟(제자리). 앞발로 흙을 헤치고 부스러기가
    양옆 위로 튄다"""
    frames = []
    rig = Rig(15.5, 1.3, 90.0, 0.98)
    for k, ph in enumerate(phases()):
        f = {}
        o, _ = side(rig, stroke=ph, nose=0, shut=(k == 7), ground=19.5, reach=8.4)
        f.update(o)
        h, _, _ = draw(Rig(15.5, 30.8, 0.0, 1.0), [hill(0.0, 0.0, 12.0, 11.0)])
        f.update(h)
        fling(f, Rig(15.5, 20.0, 0.0, 1.0), -3.0, 0.0, -9.0, 1.0, k, 3, 3.0)
        fling(f, Rig(15.5, 20.0, 0.0, 1.0), 3.0, 0.0, 9.0, 1.0, k + 3, 3, 3.0)
        frames.append(finish(clip(f)))
    return frames


MOVE = Rig(15.5, 19.6, 0.0, 0.62)   # 흙더미 밑동 가운데


def move() -> list[dict]:
    """흙더미에서 쏙 솟아 두리번거렸다 쏙 숨는다(두더지 잡기) — 네 방향 풀잎 화살촉이 바깥으로 두근댄다.
    핫스팟은 흙더미"""
    frames = []
    rises = [1.0, 1.0, 1.0, 1.0, 0.8, 0.35, 0.0, 0.0, 0.35, 0.8, 1.0, 1.0]   # 첫 장은 솟은 모습
    for k, ph in enumerate(phases()):
        f = {}
        o_ = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o_), 15 + dy * (13 + o_), dx, dy, GRASS)
        look = (0, -1, -1, 1, 1, 0)[k % 6] if rises[k] == 1.0 else 0
        popper(f, Rig(MOVE.ox + 0.6 * look, MOVE.oy, 0.0, MOVE.k), rises[k], k,
               "blink" if k == 2 else "smile", 9.6, 7.6)
        frames.append(finish(clip(f)))
    return frames


def dig(ang: float, fl: bool = False) -> list[dict]:
    """그 축으로 몸을 쭉 뻗고 땅속을 헤엄치듯 파 나간다 — 코끝과 꼬리가 양 끝 화살 노릇, 앞발이 흙을 긁을 때마다
    부스러기가 뒤로 튀고 양 끝 풀잎 화살촉이 두근댄다. 몸 가운데가 판 가운데"""
    frames = []
    t = math.radians(ang)
    ux, uy = math.cos(t), math.sin(t)
    dx, dy = round(ux), round(uy)
    diag = dx != 0 and dy != 0
    R = 10 if diag else 13
    k_ = 0.72 if diag else 0.8
    mid = 11.0
    rig = Rig(15.5 - ux * mid * k_, 15.5 - uy * mid * k_, ang, k_, fl=fl)
    for k, ph in enumerate(phases()):
        f = {}
        s = math.sin(ph)
        o = 1 if s > 0.3 else 0
        for sg in (-1, 1):
            chevron(f, 15 + sg * dx * (R + o), 15 + sg * dy * (R + o), sg * dx, sg * dy, GRASS if o else GRASS_D)
        b, _ = side(rig, stroke=ph, nose=1 if k % 3 == 1 else 0, shut=(k == 3))
        f.update(b)
        fling(f, rig, 19.0, 3.4, 3.0, 0.6, k, 2, 1.6)
        frames.append(finish(clip(f)))
    return frames


def we():
    return dig(180.0, fl=True)


def ns():
    return dig(90.0)


def nwse():
    return dig(225.0, fl=True)


def nesw():
    return dig(135.0, fl=True)


def no() -> list[dict]:
    """빨간 금지 표지 안 흙더미 — 솟았다가 표지를 보고 눈을 질끈 감고 도리도리, 흙더미 속으로 쏙 숨었다 다시 빼꼼"""
    frames = []
    rises = [1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.0, 0.0, 0.0, 0.15, 0.15, 0.6]   # 첫 장은 솟은 모습
    for k in range(N):
        f = {}
        sign(f, slash=False)
        shake = (0, -1, 1, -1, 1)[k] if k <= 4 else 0
        mood = "squint" if 1 <= k <= 4 else "smile"
        popper(f, Rig(12.4 + 0.7 * shake, 25.6, 0.0, 0.84), rises[k], k, mood, 9.0, 4.6)   # 빗금 왼쪽 아래 — 얼굴이 빗금에 안 가린다
        if k in (5, 6):   # 숨을 때 튄 흙
            for q in ((10, 15 + k - 5), (21, 14 + k - 5)):
                f.setdefault(q, CRUMB)
        sign(f)   # 고리도 다시 — 표지 밖으로 나간 흙더미 · 몸을 고리가 덮는다
        frames.append(finish(clip(f)))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def top_cell(fr, xmax: int = 31):
    """맨 위 불투명 칸(같으면 왼쪽) — xmax 보다 왼쪽에서만"""
    return min((p for p, c in fr[0].items() if c[3] == 255 and p[0] < xmax), key=lambda p: (p[1], p[0]))


HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1),
       "wait": (15, 15), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (IX, 15),
       "pen": (math.floor(TIP[0]), math.floor(TIP[1])),
       "hand": lambda fr: top_cell(fr, 14), "up": lambda fr: top_cell(fr)}


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

# SPDX-License-Identifier: Apache-2.0
"""토끼(rabbitanim) 구성표 그림 `art/rabbitanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/rabbit.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

숲속 친구들 · 애니 묶음(다람쥐 · 고슴도치 · 부엉이 · 토끼 · 여우)의 한 마리. 칸마다 토끼가 하는 짓을 따로 그린다(`SCENE`).
치비 비율 — 흰 털(짙은 갈색 테라 어두운 바탕에서도 읽힌다) · 큰 동그란 머리 · 안쪽이 분홍인 굵은 긴 귀 둘 ·
2×2 콩알 눈에 흰 반짝 · 오물거리는 분홍 코 · 분홍 볼터치 · 동그란 솜꼬리 · 긴 뒷발. 소품은 당근과 묶음 공통의
풀 덤불 · 나뭇잎 · 도토리다. 귀는 실루엣의 주인공이지만 머리 위 V 자 둘만 남으면 브이 손 · 가위로 읽히니
거의 나란히 세우고 굵게 그려 얼굴과 한 덩이로 보이게 한다.

  arrow   왼쪽 위로 깡총 뛰는 옆모습 — 분홍 코끝이 핫스팟. 뛸 때 뒷발을 차고 귀를 접었다가 내려앉으면 귀를 쫑긋
  busy    작은 화살표 토끼 + 오른쪽 아래 당근 둘레를 도토리 · 나뭇잎 여덟이 차례로 빛나며 돈다
  cross   앞모습 얼굴. 수염이 가로 조준선, 턱 밑 · 두 귀 사이 가는 줄이 세로 조준선. 오물거리는 코가 핫스팟
  hand    뒷발로 서서 앞발 하나를 높이 들어 콕 — 다른 앞발은 당근을 안았다. 든 앞발 끝이 핫스팟
  help    작은 화살표 토끼 + 나뭇잎으로 찍은 물음표(점은 작은 당근)
  ibeam   땅에 박힌 긴 당근을 끌어안고 쑥쑥 당기는 토끼 — 잎이 I 의 위 가로획, 흙 둔덕이 아래 가로획. 핫스팟은 당근
  move    풀 덤불 위에서 제자리 깡총(빈키) — 뛰어오르면 귀가 양옆으로 펄럭인다. 네 방향 풀잎 화살촉
  ns      뒷발 끝으로 쭉 서서 귀 끝까지 몸을 늘였다 웅크렸다 — 위아래 풀잎 화살촉
  we · nwse · nesw   그 축으로 몸을 쭉 뻗고 멀리뛰기 하는 옆모습 — 앞발과 차 낸 뒷발이 양 끝, 몸을 폈다 모았다 한다
  no      빨간 금지 표지 안에서 두 앞발로 제 귀를 끌어내려 눈을 가린다(안 볼래) — 가끔 귀 한쪽을 들고 빼꼼
  pen     연필처럼 깎은 당근을 끌어안고 쓴다 — 연필심(왼쪽 아래)이 핫스팟. 당근 꼭지 잎이 살랑인다
  person  작은 화살표 토끼 + 토끼 귀 후드를 쓴 사람이 손을 흔든다
  pin     작은 화살표 토끼 + 동그라미 속에 토끼 얼굴이 든 빨간 지도 핀(귀가 동그라미 위로 솟는다)이 통통 튄다
  up      뒷발로 꼿꼿이 서서 귀를 세우고 둘레를 살핀다 — 높은 귀 끝이 핫스팟. 다른 귀가 이리저리 돌아간다
  wait    풀숲에 앉아 두 앞발로 당근을 쥐고 오물오물 갉아 먹는다 — 볼이 들썩이고 부스러기가 떨어진다

몸은 부위(타원 · 굵기가 변하는 막대)를 토끼 제 좌표에 놓고 화면으로 돌려 찍는다(`Rig`, `draw` — 해달과 같은 틀).
앞모습(`front`)과 옆모습(`side`) 두 벌이다. 그리개는 gen/otter.py 와 같은 꼴이지만 다른 생성기를 import 하지 않으려고
여기 따로 둔다(다른 생성기를 고치면 이 그림이 조용히 바뀌지 않게). `Rig` 은 가로 · 세로 배율을 따로 받아 몸을
늘였다 줄인다(ns).
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, disc, finish, hx, ink, phases, raster, solid, write

SID = "rabbitanim"

OUT, EYE, HI = hx("3b2a26ff"), hx("1e1412ff"), hx("fffaf0ff")                  # 테두리 · 눈 · 반짝
FUR, FUR_S, FUR_D = hx("fbf8f3ff"), hx("ebe4daff"), hx("d3c8baff")            # 흰 털 · 옅은 그늘 · 짙은 그늘(먼 귀)
PINK, NOSE, BLUSH, MOUTH = hx("f5a9b8ff"), hx("e8728aff"), hx("f49a9aff"), hx("8a6660ff")   # 귀 속 · 코 · 볼 · 입
ink(OUT, HI, hx("f6e9d2c7"))
CARROT, CARROT_D, CARROT_L = hx("f28a2eff"), hx("c9621cff"), hx("f8b066ff")   # 당근
GRASS, GRASS_D, GRASS_L = hx("5aa04aff"), hx("3f7a35ff"), hx("86c46aff")      # 풀 · 나뭇잎 (묶음 공통)
ACORN, ACORN_L, CAP, CAP_D = hx("a0662eff"), hx("c88a4eff"), hx("6b4423ff"), hx("4a2e16ff")   # 도토리
SOIL, SOIL_D = hx("8a6a44ff"), hx("5e4628ff")                                  # 흙
SKIN, SHIRT, SHIRT_D = hx("f4e2c4ff"), hx("4a7fb5ff"), hx("2e5a88ff")          # 사람
WOOD, LEAD = hx("efd2a8ff"), hx("3a3a3aff")                                    # 깎은 당근 연필
PUFF = hx("ffffffa0")                                                         # 흙먼지 · 김


# ── 그리개: 토끼 제 좌표 (a, b) → 화면 ─────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도, a 축이 화면에서 가리키는 쪽, 90 이 아래) · 배율 k(a 축 kx, b 축 ky 를 따로 줄 수
    있다) · 뒤집기 fl. b 축은 a 축을 시계 방향으로 90도 돌린 쪽(ang=0 이면 a 가 오른쪽, b 가 아래). fl 이면 b 축을 반대로"""

    def __init__(self, ox: float, oy: float, ang: float = 0.0, k: float = 1.0, fl: bool = False,
                 kx: float = None, ky: float = None):
        t = math.radians(ang)
        self.ox, self.oy, self.c, self.s = ox, oy, math.cos(t), math.sin(t)
        self.k = k
        self.kx, self.ky = kx or k, (ky or k) * (-1 if fl else 1)

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


# ── 귀: 밑동에서 두 마디로 뻗는 굵은 막대 + 안쪽 분홍 ─────────────────────────────
def ear(base, ang1: float, ang2: float, l1: float, l2: float, r: float = 1.9, inner: bool = True):
    """base 에서 ang1(라디안, 0 이 위(-b), + 가 +a 쪽으로 눕는다)으로 l1, 거기서 ang2 로 l2 뻗는 귀.
    → (겉 맞음, 속 맞음 또는 None, 끝 (a, b)). 끝은 살짝 가늘고 둥글다 — 뾰족하면 여우 · 고양이 귀다"""
    v1 = (math.sin(ang1), -math.cos(ang1))
    v2 = (math.sin(ang2), -math.cos(ang2))
    mid = (base[0] + v1[0] * l1, base[1] + v1[1] * l1)
    tip = (mid[0] + v2[0] * l2, mid[1] + v2[1] * l2)
    outer = any_of(bar(base, mid, r, r), bar(mid, tip, r, r * 0.8))
    if not inner:
        return outer, None, tip
    ri = r * 0.45
    b0 = (base[0] + v1[0] * 1.2, base[1] + v1[1] * 1.2)
    t0 = (tip[0] - v2[0] * 1.0, tip[1] - v2[1] * 1.0)
    return outer, any_of(bar(b0, mid, ri), bar(mid, t0, ri, ri * 0.7)), tip


# ── 앞모습: u 가로(+오른쪽), w 세로(+아래), 원점은 얼굴 가운데 ────────────────────
def front(rig: Rig, mood: str = "smile", ears=((6, 0), (6, 0)), paws=((-1.9, 6.2), (1.9, 6.2)), extra=(),
          mid=(), body: bool = True, feet: bool = True, nose: int = 0, chew: int = 0, cover=None,
          lens=(5.0, 4.6)) -> tuple[dict, set]:
    """앞모습 토끼 한 장. ears 는 귀마다 (바깥으로 기운 각 · 그 위 마디가 더 꺾인 각, 도), paws 는 앞발 끝들
    (어깨에서 막대로 잇는다, None 이면 안 그린다), extra 는 맨 앞 부위, mid 는 앞발 뒤 · 몸 앞 부위(안은 당근),
    nose 는 코가 오물거린 칸(0 · 1), chew 는 볼이 들썩인 정도(0 · 1), mood: smile · blink · sleep · hide.
    cover 가 (u, w) 둘이면 귀를 앞으로 끌어내려 그 자리(눈)를 가린다(no). lens 는 귀 두 마디 길이"""
    ear_parts, ear_in = [], []
    for sg, (tilt, bend) in zip((-1, 1), ears):
        base = (sg * 2.3, -3.6)
        if cover:
            cu, cw = cover[0 if sg < 0 else 1]
            if cu is None:   # 놓은 귀는 그대로 서 있다
                o, i, _ = ear(base, sg * math.radians(tilt), sg * math.radians(tilt + bend), *lens)
                ear_parts.append(o)
                ear_in.append(i)
            else:            # 밑동만 조금 서고 나머지는 얼굴 앞으로 접혀 내려온다
                o, _, _ = ear(base, sg * math.radians(tilt), sg * math.radians(tilt), 2.4, 0.1, inner=False)
                ear_parts.append(any_of(o, bar((sg * 2.6, -6.2), (cu, cw), 2.0, 1.8)))
            continue
        o, i, _ = ear(base, sg * math.radians(tilt), sg * math.radians(tilt + bend), *lens)
        ear_parts.append(o)
        ear_in.append(i)
    pads, arms = [], []
    for au, aw in (paws or ()):
        sh = (math.copysign(3.6, au), 5.0)
        arms.append(bar(sh, (au, aw), 1.3, 1.2))
        pads.append(ell(au, aw, 1.4, 1.4))
    puff = 0.5 * chew

    def face(a, b):
        return FUR_S if b > 3.6 else FUR

    def bodyc(a, b):
        return FUR_S if b > 9.6 or abs(a) > 3.6 else FUR
    head = any_of(ell(0.0, -0.2, 5.6, 4.9), ell(0.0, 1.8, 6.2 + puff, 3.2 + puff * 0.4))
    parts = list(extra)
    if cover:   # 끌어내린 귀는 얼굴 앞, 그 귀를 쥔 앞발은 귀 앞
        parts += [("paw", any_of(*pads), FUR, True)] if pads else []
        parts += [("flap", any_of(*[e for e in ear_parts]), FUR, True)]
        parts += [("head", head, face, True)]
        if ear_in:
            parts += [("ear_in", any_of(*ear_in), PINK, False)]
        parts += list(mid) + ([("arm", any_of(*arms), FUR, False)] if arms else [])
    else:
        parts += [("paw", any_of(*pads), FUR, True)] if pads else []
        parts += list(mid)
        parts += [("arm", any_of(*arms), FUR, False)] if arms else []
        parts += [("head", head, face, True), ("ear_in", any_of(*ear_in), PINK, False),
                  ("ear", any_of(*ear_parts), FUR, False)]
    if feet:
        parts += [("feet", any_of(ell(-2.8, 11.0, 2.2, 1.2), ell(2.8, 11.0, 2.2, 1.2)), FUR, True)]
    if body:
        parts += [("body", ell(0.0, 7.8, 4.8, 3.8), bodyc, False)]
    out, mask, _ = draw(rig, parts)
    for sg in (-1, 1):
        if mood == "smile":
            eye(out, rig, sg * 2.7 - 0.5, -0.6)
        elif mood in ("blink", "sleep"):
            eye(out, rig, sg * 2.7 - 0.5, -0.6, shut=True)
        dot(out, rig, sg * (3.9 + puff), 2.0, BLUSH)
    if mood != "hide" or True:
        x, y = rig.cell(-0.3, 1.2)
        y -= nose
        out[x, y] = NOSE
        out[x + 1, y] = NOSE
        mx, my = rig.cell(0.0, 2.5)
        out[mx, my] = MOUTH
    return out, mask


# ── 옆모습: a 는 코끝 0 → 꼬리, b 는 + 가 배(발) 쪽 ─────────────────────────────
def side(rig: Rig, hop: float = 0.0, ear_up: float = 1.0, nose: int = 0, shut: bool = False, stretch: float = 1.0,
         extra=(), big_eye: bool = True, simple: bool = False) -> tuple[dict, set]:
    """옆모습 토끼 한 장. 코끝이 원점 근처. hop 은 뛴 정도(0 웅크림 – 1 앞발 · 뒷발을 쭉 뻗음), ear_up 은 귀를
    세운 정도(1 쫑긋 – 0 등에 납작), nose 는 코가 오물거린 칸, stretch 는 머리 뒤 몸을 a 축으로 늘인 배율,
    extra 는 맨 앞 부위. 먼 귀 · 먼 뒷발은 짙은 그늘로 몸 뒤에 둔다. simple 이면 작게 그릴 때라 뒷발 · 솜꼬리 선과
    먼 앞발을 뺀다 — 0.6 배에서 선이 다 남으면 몸이 까만 줄 덩어리다"""
    S = stretch

    def ax(a):   # 머리 뒤를 늘인다
        return 8.0 + (a - 8.0) * S
    # 귀는 25°(살짝 선) – 85°(등에 납작), 밑동은 머리 뒤 꼭대기. 화살표로 눕히면 25° 가 화면에서 오른쪽 조금 위라
    # 판 위로 안 나간다 — 머리 꼭대기에 세우면 판 위에 잘려 납작한 막대가 된다
    ea = math.radians(25 + 60 * (1 - ear_up))
    droop = math.radians(12 * (1 - ear_up))
    near_o, near_i, _ = ear((9.0, -2.6), ea, ea + droop, 4.4, 4.4, 1.7)
    far_o, _, _ = ear((10.4, -2.2), ea + 0.18, ea + 0.18 + droop, 4.2, 4.2, 1.6, inner=False)
    reach = hop
    fpaw0 = (ax(9.6), 3.6)
    fpaw1 = (ax(9.6) - 1.0 - 2.8 * reach, 6.0 - 0.6 * reach)
    hind0 = (ax(16.0), 5.0)
    hind1 = (ax(16.0) + 3.0 + 3.4 * reach, 6.4 - 1.4 * reach)
    tail_c = (ax(20.2) + 0.6 * reach, 0.4 - 0.6 * reach)
    hc = (ax(15.6), 2.8, 3.4 + 0.4 * reach, 3.0)

    def headc(a, b):
        return FUR_S if b > 4.0 else FUR

    def bodyc(a, b):
        return FUR_S if b > 3.4 else FUR

    def haunchc(a, b):   # 넓적다리는 선 대신 앞쪽 테만 옅은 그늘 — 선을 그으면 몸속이 줄투성이다
        r = ((a - hc[0]) / hc[2]) ** 2 + ((b - hc[1]) / hc[3]) ** 2
        return FUR_S if r > 0.55 and a < hc[0] else FUR
    # 주둥이는 머리보다 앞으로 내민 뭉툭한 콘 — 동그란 머리만이면 비스듬히 눕혔을 때 머리 옆이 코끝보다 판 가장자리로 나간다
    parts = list(extra) + [
        ("snout", bar((0.8, 0.7), (4.4, 1.0), 0.9, 2.5), FUR, False),
        ("head", ell(6.6, 0.9, 4.6, 4.3), headc, True),
        ("ear_in", near_i, PINK, False),
        ("ear", near_o, FUR, True),
        ("tail", ell(*tail_c, 2.1, 2.0), FUR, True),
        ("hind", bar(hind0, hind1, 1.8, 1.5), FUR, True),
        ("fpaw", bar(fpaw0, fpaw1, 1.5, 1.4), FUR, False),
        ("haunch", ell(*hc), haunchc, False),
        ("body", ell(ax(12.6), 1.6, 6.4 * S + 0.6 * reach, 4.4 - 0.5 * reach), bodyc, False),
        ("far_paw", bar((ax(10.6), 3.6), (fpaw1[0] + 1.2, fpaw1[1] - 0.2), 1.1), FUR_D, False),
        ("far_ear", far_o, FUR_D, False)]
    if simple:
        parts = [(n, h, c, ln and n == "head") for n, h, c, ln in parts if n != "far_paw"]
    out, mask, _ = draw(rig, parts)
    eye(out, rig, 4.9, -0.2, big_eye, shut)
    dot(out, rig, 6.8, 2.4, BLUSH)
    dot(out, rig, 0.6, 0.4 - 0.9 * nose, NOSE)
    return out, mask


ARROW = Rig(1.4, 1.3, 47.0, 0.85)      # 화살표 토끼: 코끝이 (1, 1)
ARROW_S = Rig(1.4, 1.3, 47.0, 0.62)    # 작은 화살표 토끼 (busy · help · person · pin)


def arrow_bun(k: int, small: bool = False) -> dict:
    ph = 2 * math.pi * k / N
    hop = (0.5 - 0.5 * math.cos(ph)) * (0.6 if small else 1.0)
    return side(ARROW_S if small else ARROW, hop=hop, ear_up=1.0 - 0.5 * hop, nose=1 if k % 4 == 1 else 0,
                shut=(k == 9), simple=small)[0]


# ── 숲 소품 ──────────────────────────────────────────────────────────────────
def carrot_parts(p_tip, p_top, r: float, leaf_k: float = 0.0, name: str = "carrot", lead: float = 0.0) -> list:
    """p_tip(뾰족한 끝) → p_top(꼭지) 당근 + 꼭지에서 부채꼴로 나는 잎 셋. r 은 꼭지 쪽 반지름, leaf_k 는 잎이
    살랑인 각(라디안). lead 가 0 보다 크면 끝을 연필처럼 깎았다(그 길이만큼 나무색 · 끝 한 마디는 심)"""
    ex, ey = p_top[0] - p_tip[0], p_top[1] - p_tip[1]
    L = math.hypot(ex, ey)
    ux, uy = ex / L, ey / L

    def col(a, b):
        t = (a - p_tip[0]) * ux + (b - p_tip[1]) * uy
        s = -(a - p_tip[0]) * uy + (b - p_tip[1]) * ux
        if lead:
            if t < lead * 0.4:
                return LEAD
            if t < lead:
                return WOOD
        if (t % 2.6) < 0.55 and t > 1.5:   # 가로 주름
            return CARROT_D
        return CARROT_L if s < -r * 0.35 else CARROT
    body = bar(p_tip, p_top, 0.35 if not lead else 0.3, r)
    if lead:
        body = any_of(bar(p_tip, (p_tip[0] + ux * lead, p_tip[1] + uy * lead), 0.3, r * 0.92),
                      bar((p_tip[0] + ux * lead, p_tip[1] + uy * lead), p_top, r * 0.92, r))
    leaves = []
    base = math.atan2(uy, ux)
    for d in (-0.55, 0.0, 0.55):
        t = base + d + leaf_k * (1 if d >= 0 else -1)
        q = (p_top[0] + math.cos(t) * r * 3.0, p_top[1] + math.sin(t) * r * 3.0)
        leaves.append(bar(p_top, q, r * 0.5, r * 0.3))

    def leaf_col(a, b):
        return GRASS_L if ((a - p_top[0]) * -uy + (b - p_top[1]) * ux) < 0 else GRASS
    return [(name, body, col, True), (name + "_leaf", any_of(*leaves), leaf_col, False)]


def tuft(f: dict, x0: int, x1: int, y: int, k: int = 0) -> None:
    """풀 덤불: y 줄을 밑동으로 높이가 들쭉날쭉한 풀잎. k 로 잎끝이 살랑인다 (고슴도치와 같은 꼴)"""
    for x in range(x0, x1 + 1):
        h = (2, 3, 1, 4, 2, 3, 1)[(x * 3) % 7]
        for j in range(h):
            f[x, y - j] = GRASS_D if j == 0 else GRASS if j < h - 1 else GRASS_L
        if h >= 3 and (x + k) % 4 == 0:
            f.pop((x, y - h + 1), None)
            f[x + 1, y - h + 1] = GRASS_L


ACORN_SMALL = [".s.", "ccc", "aaa", ".a."]
LEAF_SMALL = ["..g", ".lg", "lg.", "g.."]


def acorn(f: dict, x0: int, y0: int, alpha: int = 255) -> None:
    """3×4 도토리. alpha 가 낮으면 반투명으로 흐리게(도는 고리의 꼬리)"""
    pal = {"s": CAP_D, "c": CAP, "a": ACORN}
    for j, row in enumerate(ACORN_SMALL):
        for i, ch in enumerate(row):
            if ch != ".":
                f[x0 + i, y0 + j] = pal[ch][:3] + (alpha,)
    if alpha == 255:
        f[x0, y0 + 2] = ACORN_L


def leaflet(f: dict, x0: int, y0: int, alpha: int = 255) -> None:
    """3×4 나뭇잎"""
    pal = {"g": GRASS, "l": GRASS_L}
    for j, row in enumerate(LEAF_SMALL):
        for i, ch in enumerate(row):
            if ch != ".":
                f[x0 + i, y0 + j] = pal[ch][:3] + (alpha,)


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


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    """왼쪽 위로 깡총 — 뛸 때 앞발 · 뒷발을 쭉 뻗고 귀를 등에 접었다가, 내려앉으면 귀를 쫑긋 세운다.
    코끝은 제자리(핫스팟)이고 코가 오물거린다. 뒷발을 찰 때 흙먼지가 인다"""
    frames = []
    for k in range(N):
        f = arrow_bun(k)
        if k in (1, 2, 3):
            t = k - 1
            for d in (0, 1):
                f.setdefault(ARROW.cell(24.0 + t * 1.5 + d, 7.5 + d * 1.2 - t * 0.3), PUFF)
        frames.append(finish(clip(f)))
    return frames


def wait() -> list[dict]:
    """풀숲에 앉아 두 앞발로 당근을 쥐고 오물오물 — 볼이 들썩이고 코가 씰룩, 부스러기가 떨어진다.
    가끔 한쪽 귀가 톡 꺾였다 선다"""
    frames = []
    rig = Rig(15.5, 13.6, 0.0, 0.84)
    for k, ph in enumerate(phases()):
        f = {}
        tuft(f, 1, 30, 30, k)
        chew = k % 2
        bite = 0.6 * (k % 4 in (1, 2))
        carrot = carrot_parts((0.6, 3.6 + bite), (6.2, 10.4), 1.5, 0.15 * math.sin(2 * ph))
        flop = 55 if k in (6, 7, 8) else 0
        o, _ = front(rig, "blink" if k == 10 else "smile", ears=((5, 0), (5, flop)),
                     paws=((-1.2, 5.6 + bite), (2.6, 6.8 + bite)), mid=carrot, nose=k % 3 == 1, chew=chew)
        f.update(o)
        if k % 4 in (2, 3):   # 부스러기
            t = k % 4 - 2
            f.setdefault(rig.cell(-2.4 - t, 8.0 + 3.0 * t), CARROT)
        frames.append(finish(clip(f)))
    return frames


def cross() -> list[dict]:
    """앞모습 얼굴 — 양 볼에서 뻗은 수염이 가로 조준선, 턱 밑과 두 귀 사이 가는 줄이 세로선. 코가 핫스팟"""
    frames = []
    rig = Rig(15.5, 14.6, 0.0, 0.92)   # 코 칸이 (15, 15)
    for k, ph in enumerate(phases()):
        f = {}
        tw = 1 if k % 6 < 3 else 0
        for i in range(1, 31):
            if i < 9 or i > 22:
                f[i, 15] = MOUTH
            if i > 24 and i <= 30:
                f[15, i] = MOUTH
            if i < 4:
                f[15, i] = MOUTH
        for sg in (-1, 1):   # 수염 끝이 까딱 — 부채꼴로 그리면 가운데를 가리키는 화살촉으로 읽힌다
            f[15 + sg * 13 + (1 if sg > 0 else 0), 15 - tw] = MOUTH
        o, _ = front(rig, "blink" if k == 8 else "smile", ears=((9, 0), (9, 0)), paws=None, body=False,
                     feet=False, nose=0, lens=(4.6, 4.0))
        f.update(o)
        x, y = 15, 15
        f[x, y], f[x + 1, y] = NOSE, NOSE
        if k % 4 == 1:   # 오물
            f[x, y - 1], f[x + 1, y - 1] = NOSE, NOSE
        frames.append(finish(clip(f)))
    return frames


HAND = Rig(18.0, 16.8, 0.0, 0.86)
HAND_PAW = (-9.4, -7.6)   # 머리 옆 바깥으로 든다 — 머리 위에 들면 세 번째 귀로 읽힌다


def hand() -> list[dict]:
    """뒷발로 서서 앞발 하나를 높이 들어 콕 — 귀는 반대쪽으로 기울이고, 다른 앞발로 당근을 안았다.
    콕 찌를 때 발끝 옆에 반짝"""
    frames = []
    carrot = carrot_parts((1.6, 8.6), (5.6, 2.0), 1.3)
    for k, ph in enumerate(phases()):
        poke = max(0.0, math.sin(2 * ph))
        paw = (HAND_PAW[0], HAND_PAW[1] - 0.9 * poke)
        o, _ = front(HAND, "blink" if k == 9 else "smile", ears=((-14, 0), (24, 10 if k % 6 < 3 else 0)),
                     paws=(paw, (3.2, 6.4)), mid=carrot, nose=k % 4 == 2)
        f = dict(o)
        if poke > 0.9:
            x, y = HAND.cell(paw[0], paw[1] - 1.6)
            for q in ((x - 2, y), (x + 2, y), (x - 2, y - 2), (x + 2, y - 2)):
                f.setdefault(q, HI)
        frames.append(finish(clip(f)))
    return frames


def busy() -> list[dict]:
    """작은 화살표 토끼 + 오른쪽 아래 당근 — 둘레를 도토리 · 나뭇잎 여덟이 차례로 빛나며 돈다"""
    frames = []
    cx, cy = 22.0, 22.0
    for k in range(N):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = math.floor(cx + 7.0 * math.cos(a)), math.floor(cy + 7.0 * math.sin(a))
            lag = (head - i) % 8
            al = 255 if lag < 1 else 200 if lag < 2 else 140 if lag < 3 else 90
            (acorn if i % 2 == 0 else leaflet)(f, x - 1, y - 2, al)
        o, _, _ = draw(Rig(cx, cy, 0.0, 1.0), carrot_parts((-2.6, 2.8), (1.6, -1.6), 1.5, 0.2 * math.sin(2 * math.pi * k / N)))
        f.update(o)
        f.update(arrow_bun(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def help_() -> list[dict]:
    """작은 화살표 토끼 + 나뭇잎으로 찍은 물음표(점은 작은 당근) — 잎이 글자 차례로 하나씩 부풀었다 돌아온다"""
    frames = []
    cells = [(17.6 + 2.2 * i, 11.6 + 2.2 * j) for j, row in enumerate(QMARK[:-1]) for i, ch in enumerate(row)
             if ch == "#"]
    for k in range(N):
        f = {}
        m, big = set(), set()
        n = len(cells) + 1
        for i, (x, y) in enumerate(cells):
            d = (k * n / N - i) % n
            (big if d < 1.5 else m).update(disc(x, y, 1.2 + (0.5 if d < 1.5 else 0.0)))
        solid(f, m, GRASS, GRASS_D)
        solid(f, big - m, GRASS_L, GRASS_D)
        bob = 1 if (k * n / N - len(cells)) % n < 1.5 else 0
        o, _, _ = draw(Rig(22.5, 25.6 - bob, 0.0, 1.0), carrot_parts((-0.2, 2.6), (0.0, -1.2), 1.3))
        f.update(o)
        f.update(arrow_bun(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def person() -> list[dict]:
    """작은 화살표 토끼 + 토끼 귀 후드를 쓴 사람이 손을 흔든다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        rig = Rig(22.5, 20.6, 0.0, 0.56)
        wave = -2.4 * abs(math.sin(ph))
        hand_ = (8.6, 3.0 + wave)
        eo = []
        for sg in (-1, 1):
            o, i, _ = ear((sg * 2.6, -5.6), sg * math.radians(8), sg * math.radians(8 + (20 if sg > 0 and k % 6 < 3 else 0)),
                          4.6, 3.8, 1.9)
            eo.append((o, i))
        parts = [("hand", ell(*hand_, 1.8, 1.8), SKIN, True), ("sleeve", bar((5.4, 9.0), hand_, 1.7), SHIRT, False),
                 ("face", ell(0.0, 0.8, 5.0, 4.4), SKIN, True),
                 ("hood", ell(0.0, -0.2, 7.2, 6.8), FUR, True),
                 ("ear_in", any_of(*[i for _, i in eo]), PINK, False),
                 ("ear", any_of(*[o for o, _ in eo]), FUR, False),
                 ("torso", ell(0.0, 12.0, 7.6, 6.2), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
        o, _, _ = draw(rig, parts)
        for sg in (-1, 1):
            eye(o, rig, sg * 2.4 - 0.8, -0.2, big=False, shut=(k == 6))
            dot(o, rig, sg * 3.4, 2.4, BLUSH)
        dot(o, rig, 0.0, 2.0, NOSE)
        f.update({p: c for p, c in o.items() if p[1] <= 30})
        f.update(arrow_bun(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def pin() -> list[dict]:
    """작은 화살표 토끼 + 빨간 지도 핀 — 동그라미 속 토끼 얼굴, 귀 둘이 동그라미 위로 솟는다. 땅에 닿으면 눈을 감는다"""
    frames = []
    for k in range(N):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 15.0 + dy
        for x in range(19, 27):   # 그림자 — 높을수록 옅게
            f.setdefault((x, 29), hx("3f7a3570") if dy else hx("3f7a35b0"))
        for sg in (-1, 1):        # 핀 위로 솟은 귀
            m = raster([(cx + sg * 2.4 - 1.6, cy - 4.0), (cx + sg * 2.4 + 1.6, cy - 4.0),
                        (cx + sg * 2.9 + 1.4, cy - 10.4), (cx + sg * 2.9 - 1.4, cy - 10.4)])
            m |= disc(cx + sg * 2.9, cy - 10.0, 1.5)
            solid(f, m, FUR)
            for y in range(math.floor(cy - 9.6), math.floor(cy - 5.0)):
                f[math.floor(cx + sg * 2.6), y] = PINK
        solid(f, disc(cx, cy, 6.6) | raster([(cx - 4.6, cy + 3.6), (cx + 4.6, cy + 3.6), (cx, cy + 12.6)]),
              SIGN, SIGN_D)
        solid(f, disc(cx, cy + 0.4, 4.3), FUR, OUT)
        x0, y0 = int(cx), int(cy)
        if dy == 0:
            f[x0 - 3, y0 + 1], f[x0 - 2, y0 + 1], f[x0 + 1, y0 + 1], f[x0 + 2, y0 + 1] = EYE, EYE, EYE, EYE
        else:
            f[x0 - 2, y0], f[x0 - 2, y0 + 1], f[x0 + 1, y0], f[x0 + 1, y0 + 1] = EYE, EYE, EYE, EYE
        f[x0 - 1, y0 + 2], f[x0, y0 + 2] = NOSE, NOSE
        f[x0 - 3, y0 + 2], f[x0 + 2, y0 + 2] = BLUSH, BLUSH
        f.update(arrow_bun(k, small=True))
        frames.append(finish(clip(f)))
    return frames


IX = 9   # I 기둥(당근) 왼쪽 칸


def ibeam() -> list[dict]:
    """땅에 박힌 긴 당근을 끌어안고 당긴다 — 당근 잎이 I 의 위 가로획, 흙 둔덕이 아래 가로획.
    당길 때 당근이 한 칸 쑥 올라오고 토끼가 뒤로 젖힌다. 핫스팟은 당근 가운데"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        pull = 1 if k % 6 in (2, 3, 4) else 0
        top = 4 - pull
        for y in range(top, 29):   # 당근 기둥 — 위가 굵고(2칸) 아래로 가늘다
            t = (y - top) / (28 - top)
            ridge = (y - top) % 4 == 2
            f[IX, y] = CARROT_D if ridge else CARROT_L
            if t < 0.85:
                f[IX + 1, y] = CARROT_D if ridge or t > 0.6 else CARROT
        for x in range(IX - 3, IX + 5):   # 위 잎 — 가로획
            end = x in (IX - 3, IX + 4)
            f[x, top - 2 + (1 if end and k % 6 < 3 else 0)] = GRASS_L if x < IX + 1 else GRASS
            f[x, top - 1] = GRASS_D if x not in (IX, IX + 1) else GRASS
        for x in range(IX - 4, IX + 6):   # 흙 둔덕 — 아래 가로획
            f[x, 29] = SOIL
            f[x, 30] = SOIL_D
        f[IX - 2, 28], f[IX + 3, 28] = SOIL, SOIL
        if pull:
            f.setdefault((IX - 5, 27), PUFF)
            f.setdefault((IX + 6, 27), PUFF)
        o, _ = front(Rig(IX + 5.8 + 0.6 * pull, 15.4, 0.0, 0.6), "blink" if pull else "smile",
                     ears=((4 + 8 * pull, 0), (4 + 8 * pull, 0)), paws=((-7.6, 1.0 - pull), (-7.4, 5.0 - pull)),
                     nose=k % 3 == 1)
        f.update(o)
        frames.append(finish(clip(f)))
    return frames


TIP, BACK = (1.5, 29.5), (25.0, 10.5)   # 당근 연필심 · 꼭지(화면)


def pen() -> list[dict]:
    """연필처럼 깎은 당근을 끌어안고 쓴다 — 끝은 나무색 · 짙은 심. 토끼와 당근이 심을 축으로 살짝 까딱이고
    꼭지 잎이 살랑인다. 연필심이 핫스팟"""
    frames = []
    base = Rig(21.4, 17.6, 0.0, 0.6)
    L = math.hypot(BACK[0] - TIP[0], BACK[1] - TIP[1])
    ux, uy = (BACK[0] - TIP[0]) / L, (BACK[1] - TIP[1]) / L
    paws = (base.local(TIP[0] + ux * L * 0.62, TIP[1] + uy * L * 0.62),
            base.local(TIP[0] + ux * L * 0.78, TIP[1] + uy * L * 0.78))
    for k, ph in enumerate(phases()):
        d = math.radians(3.0 * math.sin(2 * ph))
        ox, oy = base.ox - TIP[0], base.oy - TIP[1]
        rig = Rig(TIP[0] + ox * math.cos(d) - oy * math.sin(d), TIP[1] + ox * math.sin(d) + oy * math.cos(d),
                  math.degrees(d), base.k)
        carrot = carrot_parts(base.local(*TIP), base.local(*BACK), 1.6 / base.k, 0.2 * math.sin(2 * ph),
                              lead=5.0 / base.k)
        f, _ = front(rig, "blink" if k == 4 else "smile", ears=((4, 0), (8, 30 if k % 6 < 3 else 20)),
                     paws=paws, mid=carrot, nose=k % 4 == 1)
        f[math.floor(TIP[0]), math.floor(TIP[1])] = LEAD
        frames.append(finish(clip(f)))
    return frames


UP = Rig(15.5, 17.0, 0.0, 0.8)


def up() -> list[dict]:
    """뒷발로 꼿꼿이 서서 둘레를 살핀다 — 앞발은 가슴에 모으고, 높이 선 왼귀 끝이 핫스팟. 오른귀가
    소리 나는 쪽으로 이리저리 돌아가고 코가 씰룩인다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        tuft(f, 1, 30, 30, k)
        swiv = 14 + 14 * math.sin(ph)
        o, _ = front(UP, "blink" if k == 7 else "smile", ears=((2, 0), (swiv, 8 * math.sin(ph))),
                     paws=((-1.4, 4.4), (1.4, 4.4)), nose=k % 3 == 1, lens=(6.0, 5.4))
        f.update(o)
        frames.append(finish(clip(f)))
    return frames


def move() -> list[dict]:
    """풀 덤불 위에서 제자리 깡총(빈키) — 뛰어오르면 귀가 양옆으로 펄럭이고 발밑 그림자가 작아진다.
    네 방향 풀잎 화살촉이 바깥으로 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o_ = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o_), 15 + dy * (13 + o_), dx, dy, GRASS)
        h = abs(math.sin(ph))
        for x in range(12, 20):
            if abs(x - 15.5) < 4 - 2 * h:
                f.setdefault((x, 23), hx("3f7a3590"))
        flare = 8 + 30 * h
        o, _ = front(Rig(15.5, 14.6 - 2.4 * h, 0.0, 0.58), "smile" if h < 0.7 else "blink",
                     ears=((flare, 10 * h), (flare, 10 * h)), paws=((-2.2, 5.6 - 1.4 * h), (2.2, 5.6 - 1.4 * h)),
                     nose=k % 3 == 1)
        f.update(o)
        frames.append(finish(clip(f)))
    return frames


def ns() -> list[dict]:
    """뒷발 끝으로 쭉 서서 귀 끝까지 몸을 늘였다가 동그랗게 웅크린다 — 위아래 풀잎 화살촉이 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        s = math.sin(ph)
        o = 1 if s > 0.3 else 0
        for sg in (-1, 1):
            chevron(f, 15, 15 + sg * (13 + o), 0, sg, GRASS if o else GRASS_D)
        ky = 0.62 * (1.0 + 0.12 * s)
        kx = 0.74 * (1.0 - 0.06 * s)
        rig = Rig(15.5, 15.5 + 2.4 * ky / 0.62 - 1.0, 0.0, kx=kx, ky=ky)
        b, _ = front(rig, "blink" if s < -0.8 else "smile", ears=((3, 0), (3, 0)),
                     paws=((-1.6, 4.6 - 1.2 * max(0.0, s)), (1.6, 4.6 - 1.2 * max(0.0, s))), nose=k % 3 == 1,
                     lens=(5.0 + 0.6 * s, 4.6 + 0.6 * s))
        f.update(b)
        frames.append(finish(clip(f)))
    return frames


def leap(ang: float, fl: bool = False) -> list[dict]:
    """그 축으로 몸을 쭉 뻗고 멀리뛰기 — 앞발과 차 낸 뒷발이 양 끝 화살 노릇, 몸을 폈다 모았다 하며
    양 끝 풀잎 화살촉이 두근댄다. 몸 가운데가 판 가운데"""
    frames = []
    t = math.radians(ang)
    ux, uy = math.cos(t), math.sin(t)
    dx, dy = round(ux), round(uy)
    diag = dx != 0 and dy != 0
    R = 10 if diag else 13
    k_ = 0.7 if diag else 0.74
    for k, ph in enumerate(phases()):
        f = {}
        s = math.sin(ph)
        hop = 0.7 + 0.3 * s
        o = 1 if s > 0.3 else 0
        for sg in (-1, 1):
            chevron(f, 15 + (1 if sg * dx > 0 else 0) + sg * dx * (R + o) - (1 if sg * dx > 0 else 0),
                    15 + sg * dy * (R + o), sg * dx, sg * dy, GRASS if o else GRASS_D)
        st = 1.1 + 0.08 * s
        mid = 8.0 + (13.0 - 8.0) * st          # 몸 가운데(a)
        rig = Rig(15.5 - ux * mid * k_, 15.5 - uy * mid * k_, ang, k_, fl=fl)
        b, _ = side(rig, hop=hop, ear_up=0.15, stretch=st, nose=k % 3 == 1, shut=(k == 3))
        f.update(b)
        frames.append(finish(clip(f)))
    return frames


def we():
    return leap(180.0, fl=True)


def nwse():
    return leap(45.0)


def nesw():
    return leap(135.0, fl=True)


def no() -> list[dict]:
    """빨간 금지 표지 안에서 두 앞발로 제 귀를 끌어내려 눈을 가린다(안 볼래) — 귀가 파르르 떨고,
    가끔 오른귀를 놓고 한쪽 눈으로 빼꼼 본다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f, slash=False)
        peek = k in (5, 6, 7)
        tr = 0.25 * math.sin(3 * ph)
        cover = ((-2.4 + tr, 0.4), (None, None) if peek else (2.4 - tr, 0.4))
        paws = ((-2.6 + tr, 1.4), (3.4, 5.6) if peek else (2.6 - tr, 1.4))
        o, _ = front(Rig(15.5, 15.4, 0.0, 0.68), "smile" if peek else "hide", ears=((6, 0), (6, 0)),
                     paws=paws, cover=cover)
        f.update(o)
        sign(f, ring=False)
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
       "hand": lambda fr: top_cell(fr, 13), "up": lambda fr: top_cell(fr, 16)}


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

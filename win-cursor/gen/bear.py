# SPDX-License-Identifier: Apache-2.0
"""아기곰(bearanim) 구성표 그림 `art/bearanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/bear.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

숲속 친구들 · 애니 묶음의 한 마리(2기). 칸마다 아기곰이 그 칸 뜻에 맞는 짓을 따로 한다(`SCENE`).
치비 비율 — 갈색 털 · 크고 동그란 머리 · 머리 위 동그란 귀 둘(속이 옅은 갈색) · 크림 주둥이에 까만 코 ·
2×2 콩알 눈에 흰 반짝 · 분홍 볼터치 · 통통한 몸 · 옅은 배 · 발바닥이 보이는 뭉툭한 발. 소품은 꿀단지 · 꿀방울 ·
벌집과 묶음 공통의 풀 덤불 · 나뭇가지다. 귀가 동그랗고 주둥이가 크림이어야 곰이다 — 귀가 뾰족하면 여우 ·
고양이, 주둥이까지 갈색이면 강아지로 읽힌다. 꿀단지는 털과 갈리게 붉은 흙빛이고 노란 꿀이 넘친다.

  arrow   네 발로 뒤뚱뒤뚱 왼쪽 위로 기어오르는 옆모습 — 까만 코끝이 핫스팟. 꿀 냄새를 쫓아 코를 킁킁, 걸음마다
          엉덩이가 씰룩인다
  busy    작은 화살표 곰 + 오른쪽 아래 꿀단지 둘레를 꿀방울 여덟이 차례로 빛나며 돈다
  cross   앞모습 얼굴. 가는 잔가지 조준선 넷, 위 선을 타고 꿀방울이 내려와 코에 닿으면 혀를 날름. 코가 핫스팟
  hand    꿀 묻은 앞발 하나를 머리 옆 위로 들어 콕 — 발바닥 젤리가 보이고 발끝에 맺힌 꿀방울이 뚝 떨어진다.
          든 앞발 끝이 핫스팟
  help    작은 화살표 곰 + 꿀방울로 찍은 물음표(점은 작은 꿀단지). 글자 마디가 차례로 부푼다
  ibeam   위 벌집에서 아래 꿀단지로 흘러내리는 꿀 줄기 — 벌집이 I 의 위 가로획, 꿀단지가 아래 가로획, 꿀 줄기가
          세로획. 옆에 앉은 곰이 앞발로 줄기를 받아 날름 핥는다. 핫스팟은 꿀 줄기 가운데
  move    두 팔을 양옆으로 벌리고 좌우로 기우뚱 뒤뚱 걷는 앞모습 곰 + 네 방향 풀잎 화살촉
  ns      위 나뭇가지에 두 앞발로 매달려 대롱대롱 기지개 — 몸을 쭉 늘였다 웅크렸다, 위아래 풀잎 화살촉
  we · nwse · nesw   그 축으로 배를 깔고 엎드려 앞발은 앞으로, 뒷발은 뒤로 쭉 뻗는 기지개 — 양 끝 화살촉
  no      빨간 금지 표지 안에서 꿀단지를 등 뒤로 감추고 눈을 질끈 감은 채 도리도리(안 줘!) — 단지가 옆으로 빼꼼
          (빈 단지를 머리 위로 거꾸로 들면 모자로 읽혀서 버렸다)
  pen     끝이 홈 파인 꿀 막대(허니 디퍼)를 끌어안고 쓴다 — 꿀이 맺힌 막대 끝(왼쪽 아래)이 핫스팟
  person  작은 화살표 곰 + 아기곰을 목말 태운 사람이 손을 흔든다 — 곰은 사람 머리에 턱을 괴고 앞발을 얹었다
  pin     작은 화살표 곰 + 동그라미 속에 꿀방울이 든 빨간 지도 핀이 꿀단지 옆에서 통통 튄다(꿀 있는 자리)
  up      뒷발 끝으로 서서 두 앞발을 머리 위로 V 자로 쭉 뻗고(만세) 하품하는 기지개 — 왼 앞발 끝이 핫스팟.
          앞발을 머리 위에 모으면 팔이 머리 뒤로 숨어 모자로 읽힌다
  wait    꿀단지를 다리 사이에 끼고 앉아 앞발을 쏙 넣었다 꺼내 날름날름 핥는다 — 꿀이 뚝뚝, 가운데(몸)가 핫스팟

몸은 부위(타원 · 굵기가 변하는 막대)를 곰 제 좌표에 놓고 화면으로 돌려 찍는다(`Rig`, `draw` — 해달 · 토끼와 같은 틀).
앞모습(`front`)과 옆모습(`side`) 두 벌이다. 그리개는 gen/rabbit.py 와 같은 꼴이지만 다른 생성기를 import 하지 않으려고
여기 따로 둔다(다른 생성기를 고치면 이 그림이 조용히 바뀌지 않게). 숲 소품(풀 · 나뭇가지) 색과 꼴은 같은 묶음과 맞춘다.
빌드가 부르지 않고 손으로 돌린다 · 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, disc, finish, hx, ink, phases, raster, solid, write

SID = "bearanim"
OUT, EYE, HI = hx("3b2a26ff"), hx("1e1412ff"), hx("fffaf0ff")                  # 테두리 · 눈 · 반짝
FUR, FUR_S, FUR_D = hx("a8743fff"), hx("8e5f31ff"), hx("744b25ff")            # 갈색 털 · 그늘 · 먼 다리
BELLY, MUZ, EAR_IN = hx("c99a62ff"), hx("f1dcb4ff"), hx("d9aa74ff")          # 옅은 배 · 크림 주둥이 · 귀 속
NOSE, BLUSH, MOUTH, TONGUE = hx("231612ff"), hx("ef8f8fff"), hx("5a3a2cff"), hx("f07c8cff")
PAD = hx("6a3f2cff")                                                          # 발바닥 젤리
ink(OUT, HI, hx("f6e9d2c7"))
HONEY, HONEY_D, HONEY_L = hx("f5b02aff"), hx("c9800fff"), hx("ffdc6eff")      # 꿀
POT, POT_D, POT_L, LABEL = hx("c4573aff"), hx("8e3622ff"), hx("de7d58ff"), hx("f6e4c0ff")   # 붉은 흙 꿀단지
GRASS, GRASS_D, GRASS_L = hx("5aa04aff"), hx("3f7a35ff"), hx("86c46aff")      # 풀 · 나뭇잎 (묶음 공통)
TWIG, TWIG_D = hx("7a5634ff"), hx("54391fff")                                 # 나뭇가지
COMB, COMB_D = hx("f7c64aff"), hx("b9861cff")                                 # 벌집
SKIN, SHIRT, SHIRT_D = hx("f4e2c4ff"), hx("4a7fb5ff"), hx("2e5a88ff")          # 사람
WOOD, WOOD_D = hx("ead0a0ff"), hx("b48a52ff")                                 # 꿀 막대
PUFF = hx("ffffffa0")                                                         # 흙먼지 · 김


# ── 그리개: 곰 제 좌표 (a, b) → 화면 ──────────────────────────────────────────
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
        if big:
            f[x + 1, y + 1] = EYE
        return
    if big:
        f[x, y], f[x + 1, y], f[x, y + 1], f[x + 1, y + 1] = HI, EYE, EYE, EYE
    else:
        f[x, y] = EYE


def clip(f: dict) -> dict:
    return {p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}


# ── 꿀단지: 제 좌표 원점이 단지 가운데, r 은 몸통 반지름 ─────────────────────────
def pot_parts(c, r: float, name: str = "pot", flip: bool = False, honey: bool = True, drip: float = 0.0) -> list:
    """붉은 흙 꿀단지 — 통통한 몸통 · 위에 좁은 목과 두툼한 테 · 테에서 넘친 꿀 한 줄기(drip 은 흘러내린 길이 0–1).
    flip 이면 거꾸로 든 빈 단지(입이 아래). 몸통 가운데에 크림 띠"""
    cx, cy = c
    sg = -1 if flip else 1
    body = ell(cx, cy, r * 1.15, r)
    rim = bar((cx - r * 0.8, cy - sg * r * 0.95), (cx + r * 0.8, cy - sg * r * 0.95), r * 0.32)

    def bodyc(a, b):
        if abs(b - cy - sg * r * 0.15) < r * 0.2:
            return LABEL
        return POT_L if a < cx - r * 0.45 else POT
    parts = []
    if honey and not flip:
        # 테를 납작하게 덮어 넘친 꿀 + 테에서 몸통으로 흘러내린 줄기 둘 — 위로 볼록 솟으면 불꽃(촛불)으로 읽힌다
        parts.append((name + "_honey", any_of(bar((cx - r * 0.85, cy - r * 1.05), (cx + r * 0.85, cy - r * 1.05),
                                                  r * 0.34),
                                              bar((cx + r * 0.45, cy - r * 0.9),
                                                  (cx + r * 0.45, cy - r * (0.75 - 0.75 * drip)), r * 0.26, r * 0.32),
                                              bar((cx - r * 0.5, cy - r * 0.9), (cx - r * 0.5, cy - r * 0.55), r * 0.26)),
                      lambda a, b: HONEY_L if b < cy - r * 1.15 else HONEY, True))
    parts += [(name + "_rim", rim, POT_D, True), (name, body, bodyc, False)]
    return parts


DROP = [".l.", "lhh", "hhd", ".d."]


def drop(f: dict, x0: int, y0: int, alpha: int = 255) -> None:
    """3×4 꿀방울. alpha 가 낮으면 반투명으로 흐리게(도는 고리의 꼬리)"""
    pal = {"l": HONEY_L, "h": HONEY, "d": HONEY_D}
    for j, row in enumerate(DROP):
        for i, ch in enumerate(row):
            if ch != ".":
                f[x0 + i, y0 + j] = pal[ch][:3] + (alpha,)


# ── 앞모습: u 가로(+오른쪽), w 세로(+아래), 원점은 얼굴 가운데 ────────────────────
def front(rig: Rig, mood: str = "smile", paws=((-2.0, 6.4), (2.0, 6.4)), extra=(), mid=(), body: bool = True,
          feet: bool = True, soles: bool = True, tongue: int = 0, yawn: float = 0.0, pads=(), legs=None, behind=(), arm: float = 1.8,
          arm_back: bool = False) -> tuple[dict, set]:
    """앞모습 곰 한 장. paws 는 앞발 끝들(어깨에서 막대로 잇는다, None 이면 안 그린다), extra 는 맨 앞 부위,
    mid 는 앞발 뒤 · 몸 앞 부위(꿀단지), mood: smile · blink · happy(^^) · sad. tongue 은 혀를 내민 칸 수,
    yawn 은 입을 벌린 정도(0–1), behind 는 몸 뒤 부위(등 뒤에 감춘 단지). pads 는 발바닥 젤리를 보일 앞발 번호. soles 면 앉아서 앞으로 내민 뒷발 바닥을
    보인다(서 있으면 끈다). legs 는 뒷발 자리 둘(None 이면 앉은 자리). arm_back 이면 팔을 머리·귀 뒤로 보낸다
    (만세 팔이 귀를 덮으면 팔과 귀가 한 덩이 뾰족귀로 읽혀 박쥐가 된다)"""
    pad_parts, arms = [], []
    for au, aw in (paws or ()):
        sh = (math.copysign(3.8, au), 4.8)
        arms.append(bar(sh, (au, aw), arm, arm * 0.95))
        pad_parts.append(ell(au, aw, arm + 0.2, arm + 0.2))

    def headc(a, b):
        return FUR_S if b > 3.8 else FUR

    def bodyc(a, b):
        if ((a / 2.7) ** 2 + ((b - 8.4) / 2.8) ** 2) <= 1:
            return BELLY
        return FUR_S if abs(a) > 3.6 else FUR
    head = ell(0.0, 0.0, 6.3, 5.3)
    ears = any_of(ell(-4.8, -4.5, 2.5, 2.5), ell(4.8, -4.5, 2.5, 2.5))
    ear_in = any_of(ell(-4.9, -4.7, 1.2, 1.2), ell(4.9, -4.7, 1.2, 1.2))
    muzzle = ell(0.0, 2.1, 2.7, 2.0)
    lg = legs or ((-2.9, 11.2), (2.9, 11.2))
    sole_l = [ell(u, w + 0.2, 0.9, 0.8) for u, w in lg]
    parts = list(extra)
    if pad_parts:
        parts += [("paw", any_of(*pad_parts), FUR, True)]
    parts += list(mid)
    if arms and not arm_back:
        parts += [("arm", any_of(*arms), FUR, False)]
    parts += [("muzzle", muzzle, MUZ, False), ("head", head, headc, True), ("ear_in", ear_in, EAR_IN, False),
              ("ear", ears, FUR, True if arm_back else False)]
    if arms and arm_back:
        parts += [("arm", any_of(*arms), FUR_S, True)]
    if feet:
        if soles:
            parts += [("sole", any_of(*sole_l), MUZ, False)]
        parts += [("feet", any_of(*[ell(u, w, 2.1, 1.6) for u, w in lg]), FUR, True)]
    if body:
        parts += [("body", ell(0.0, 8.0, 4.6, 4.0), bodyc, False)]
    parts += list(behind)
    out, mask, _ = draw(rig, parts)
    for i in pads:   # 발바닥 젤리 — 가운데 큰 것 하나
        au, aw = paws[i]
        dot(out, rig, au, aw + 0.6, PAD)
    for sg in (-1, 1):
        if mood == "smile":
            eye(out, rig, sg * 3.0 - 1.0, -1.6)
        elif mood == "blink":
            eye(out, rig, sg * 3.0 - 1.0, -1.6, shut=True)
        elif mood == "happy":   # ^^ — 가운데가 솟은 감은 눈
            x, y = rig.cell(sg * 3.0 - 1.0, -1.6)
            out[x, y + 1], out[x + 1, y], out[x + 2, y + 1] = EYE, EYE, EYE
        elif mood == "squeeze":   # 질끈 감은 눈 > < — 바깥 끝이 위아래로 벌어진다
            x, y = rig.cell(sg * 3.0 - 1.0, -1.6)
            ox = x if sg < 0 else x + 1
            ix = x + 1 if sg < 0 else x
            out[ix, y + 1], out[ox, y], out[ox, y + 2] = EYE, EYE, EYE
        elif mood == "sad":     # 처진 눈 — 바깥이 내려간 두 칸
            x, y = rig.cell(sg * 3.0 - 1.0, -1.6)
            out[x, y + (1 if sg < 0 else 0)], out[x + 1, y + (0 if sg < 0 else 1)] = EYE, EYE
        dot(out, rig, sg * 4.1, 1.9, BLUSH)
    x, y = rig.cell(-0.4, 1.3)
    out[x, y], out[x + 1, y] = NOSE, NOSE
    if yawn > 0:
        h = max(1, round(2.2 * yawn / rig.ky * 0.85))
        for j in range(h):
            out[x, y + 2 + j], out[x + 1, y + 2 + j] = MOUTH, MOUTH
        out[x, y + 1 + h], out[x + 1, y + 1 + h] = TONGUE, TONGUE
    else:
        mx, my = rig.cell(0.0, 2.6)
        if mood in ("sad", "squeeze"):
            out[mx - 1, my + 1], out[mx, my], out[mx + 1, my + 1] = MOUTH, MOUTH, MOUTH
        else:
            out[mx, my] = MOUTH
        for j in range(tongue):
            out[mx, my + 1 + j] = TONGUE
    return out, mask


# ── 옆모습: a 는 코끝 0 → 꼬리, b 는 + 가 배(발) 쪽 ─────────────────────────────
def side(rig: Rig, step: float = 0.0, reach: float = 0.0, stretch: float = 1.0, shut: bool = False, sniff: int = 0,
         tongue: float = 0.0, extra=(), big_eye: bool = True, simple: bool = False, rise: float = 0.0) -> tuple[dict, set]:
    """옆모습 곰 한 장. 코끝이 원점 근처. step 은 걸음 위상(라디안 사인 값, -1–1: 가까운 앞발 · 먼 뒷발이 앞으로),
    reach 는 기지개(0 서 있음 – 1 앞발을 코 앞으로 · 뒷발을 뒤로 쭉 뻗고 배를 깖), stretch 는 머리 뒤 몸을 a 축으로
    늘인 배율, sniff 는 코가 씰룩인 칸, tongue 은 코 앞으로 내민 혀 길이(a 단위). rise 는 앞을 든 정도(머리를 든다).
    simple 이면 작게 그릴 때라 먼 다리를 뺀다 — 0.6 배에서 다리 넷이 다 남으면 거미로 읽힌다"""
    S = stretch

    def ax(a):
        return 8.4 + (a - 8.4) * S
    down = 2.0 * reach          # 기지개 땐 배를 깔아 몸이 다리 쪽으로 내려온다
    lift = 1.6 * rise
    by = 2.8 + down * 0.6
    sh_f = (ax(11.4), 5.2 + down * 0.3)
    sh_h = (ax(17.6), 5.2 + down * 0.3)
    st = 1.2 * step
    if reach > 0:   # 앞발은 코 밑 앞으로, 뒷발은 꼬리 뒤로
        ff = (sh_f[0] - 2.6 - 4.0 * reach, sh_f[1] + 2.4 - 1.0 * reach)
        hf = (sh_h[0] + 2.4 + 3.4 * reach, sh_h[1] + 2.4 - 1.2 * reach)
        ffar = (ff[0] + 1.4, ff[1] - 0.8)
        hfar = (hf[0] - 1.4, hf[1] - 0.8)
    else:           # 짧고 굵은 다리 — 가늘고 길면 강아지 · 아기사슴이다
        ff = (sh_f[0] - st, 8.8)
        hf = (sh_h[0] + st, 8.8)
        ffar = (sh_f[0] + 1.4 + st, 8.4)
        hfar = (sh_h[0] + 1.4 - st, 8.4)

    def headc(a, b):
        return FUR_S if b > hb + 3.6 else FUR

    def bodyc(a, b):
        return BELLY if b > by + 2.8 else FUR
    hb = 0.3 - lift + down * 0.5
    parts = list(extra) + [
        ("muzzle", bar((0.9, hb + 1.1), (4.6, hb + 1.3), 1.5, 2.6), MUZ, False),
        ("head", ell(7.6, hb + 0.2, 5.6, 5.2), headc, True),
        ("ear_in", ell(9.2, hb - 4.6, 1.1, 1.1), EAR_IN, False),
        ("ear", ell(9.4, hb - 4.7, 2.5, 2.5), FUR, True),
        ("fpaw", bar(sh_f, ff, 2.3, 2.1), FUR, True),
        ("hpaw", bar(sh_h, hf, 2.5, 2.2), FUR, True),
        ("tail", ell(ax(21.6), by - 1.6, 1.5, 1.4), FUR, False),
        ("body", ell(ax(14.8), by, 7.0 * S, 4.8 - 0.8 * reach), bodyc, False),
        ("far_f", bar((sh_f[0] + 1.4, sh_f[1]), ffar, 1.9), FUR_D, True),
        ("far_h", bar((sh_h[0] + 1.4, sh_h[1]), hfar, 2.0), FUR_D, True)]
    if simple:
        parts = [(n, h, c, ln and n in ("head", "ear")) for n, h, c, ln in parts if not n.startswith("far")]
    out, mask, _ = draw(rig, parts)
    eye(out, rig, 5.2, hb - 1.3, big_eye, shut)
    dot(out, rig, 7.8, hb + 2.2, BLUSH)
    x, y = rig.cell(0.5, hb + 0.8 - 0.9 * sniff)
    out[x, y] = NOSE
    if tongue > 0:
        n = max(1, round(tongue))
        for i in range(n):
            out[rig.cell(-0.4 - i / rig.k, hb + 2.2)] = TONGUE
    return out, mask


ARROW = Rig(1.87, 0.61, 47.0, 0.8)     # 화살표 곰: 코끝이 (1, 1)
ARROW_S = Rig(1.78, 0.83, 47.0, 0.6)    # 작은 화살표 곰 (busy · help · person · pin)


def arrow_bear(k: int, small: bool = False) -> dict:
    ph = 2 * math.pi * k / N
    return side(ARROW_S if small else ARROW, step=math.sin(ph), sniff=1 if k % 4 == 1 else 0,
                shut=(k == 9), simple=small)[0]


# ── 숲 소품 ──────────────────────────────────────────────────────────────────
def tuft(f: dict, x0: int, x1: int, y: int, k: int = 0) -> None:
    """풀 덤불: y 줄을 밑동으로 높이가 들쭉날쭉한 풀잎. k 로 잎끝이 살랑인다 (묶음과 같은 꼴)"""
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


def twig(f: dict, x0: int, x1: int, y: int, knots=()) -> None:
    """가로 나뭇가지 두 줄(위 밝게 · 아래 짙게), knots 자리에 작은 잎"""
    for x in range(x0, x1 + 1):
        f[x, y] = TWIG
        f[x, y + 1] = TWIG_D
    for x in knots:
        f[x, y - 1], f[x + 1, y - 2] = GRASS, GRASS_L


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    """네 발로 뒤뚱뒤뚱 왼쪽 위로 기어오른다 — 코끝은 제자리(핫스팟)이고 씰룩, 다리가 번갈아 앞으로 나간다.
    뒷발을 디딜 때 흙먼지가 인다"""
    frames = []
    for k in range(N):
        f = arrow_bear(k)
        if k in (2, 3, 8, 9):
            t = k % 2
            f.setdefault(ARROW.cell(19.0 + t * 1.5, 10.0 + t), PUFF)
        frames.append(finish(clip(f)))
    return frames


def wait() -> list[dict]:
    """풀숲에 앉아 옆에 둔 꿀단지에 앞발을 쏙 넣었다 꺼내 날름날름 — 꺼낸 앞발에서 꿀이 뚝뚝 떨어지고,
    핥을 때는 눈이 ^^ 가 된다. 가운데(얼굴)가 핫스팟"""
    frames = []
    rig = Rig(12.6, 14.6, 0.0, 1.12)
    for k, ph in enumerate(phases()):
        f = {}
        tuft(f, 1, 30, 30, k)
        # 0–3 단지에 넣음 · 4–5 꺼내 올림 · 6–10 날름 · 11 내림
        if k < 4:
            paw, mood, tg = (8.6, 5.4 + 0.5 * (k % 2)), "smile", 0
        elif k < 6:
            paw, mood, tg = ((6.0, 4.6), (3.4, 3.6))[k - 4], "smile", 0
        elif k < 11:
            paw, mood, tg = (1.9, 3.4 + 0.3 * (k % 2)), "happy", 1 + (k % 2)
        else:
            paw, mood, tg = (5.2, 5.6), "blink", 0
        pot = pot_parts((9.2, 9.0), 3.5, drip=0.45 + 0.35 * math.sin(ph))
        o, _ = front(rig, mood, paws=((-3.8, 7.6), paw), extra=pot if k < 4 else (),
                     mid=pot if k >= 4 else (), tongue=tg)
        f.update(o)
        if 4 <= k < 11:   # 앞발에 묻은 꿀 · 떨어지는 방울
            x, y = rig.cell(paw[0], paw[1] + 1.4)
            f[x, y] = HONEY
            f[x + 1, y] = HONEY_L
            if k % 3 == 1:
                f.setdefault((x, y + 2), HONEY)
            elif k % 3 == 2:
                f.setdefault((x, y + 4), HONEY)
        frames.append(finish(clip(f)))
    return frames


def cross() -> list[dict]:
    """앞모습 얼굴 — 가는 잔가지 조준선 넷. 위 선을 타고 꿀방울이 내려와 코에 닿으면 혀를 날름. 코가 핫스팟"""
    frames = []
    rig = Rig(15.9, 14.3, 0.0, 1.2)   # 코 칸이 (15, 15)
    for k, ph in enumerate(phases()):
        f = {}
        for i in range(1, 31):
            if i < 9 or i > 22:
                f[i, 15] = TWIG
            if i > 23:
                f[15, i] = TWIG
            if i < 4:
                f[15, i] = HONEY_D
        lick = k >= 9
        o, _ = front(rig, "happy" if lick else "smile", paws=None, body=False, feet=False, tongue=2 if lick else 0)
        f.update(o)
        dy = 1 + k * 1.2   # 꿀방울이 위 선을 타고 내려온다
        if not lick:
            y = math.floor(dy)
            if y < 7:
                f[15, y], f[15, y + 1] = HONEY_L, HONEY
            f[14, 4], f[16, 4] = HONEY_D, HONEY_D
        f[15, 15], f[16, 15] = NOSE, NOSE
        frames.append(finish(clip(f)))
    return frames


HAND = Rig(18.0, 16.0, 0.0, 0.84)
HAND_PAW = (-9.0, -7.2)   # 머리 옆 바깥 위로 든다 — 머리 위에 들면 세 번째 귀로 읽힌다


def hand() -> list[dict]:
    """꿀 묻은 앞발 하나를 머리 옆 위로 들어 콕 — 발바닥 젤리가 보이고, 발끝에 맺힌 꿀방울이 뚝 떨어진다"""
    frames = []
    for k, ph in enumerate(phases()):
        poke = max(0.0, math.sin(2 * ph))
        paw = (HAND_PAW[0], HAND_PAW[1] - 0.9 * poke)
        o, _ = front(HAND, "blink" if k == 9 else "smile", paws=(paw, (3.4, 7.0)), pads=(0,))
        f = dict(o)
        x, y = HAND.cell(paw[0] + 0.9, paw[1] + 1.4)
        f[x + 1, y] = HONEY   # 앞발에 묻은 꿀
        t = k % 6
        if t >= 2:   # 꿀방울이 맺혔다가 떨어진다
            f.setdefault((x + 1, y + 1 + (t - 2) * 2), HONEY if t < 4 else HONEY_L)
        frames.append(finish(clip(f)))
    return frames


def busy() -> list[dict]:
    """작은 화살표 곰 + 오른쪽 아래 꿀단지 — 둘레를 꿀방울 여덟이 차례로 빛나며 돈다"""
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
            drop(f, x - 1, y - 2, al)
        o, _, _ = draw(Rig(cx, cy + 0.8, 0.0, 1.0), pot_parts((0.0, 0.0), 3.4, drip=0.5 + 0.4 * math.sin(2 * math.pi * k / N)))
        f.update(o)
        f.update(arrow_bear(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def help_() -> list[dict]:
    """작은 화살표 곰 + 꿀방울로 찍은 물음표(점은 작은 꿀단지) — 방울이 글자 차례로 하나씩 부풀었다 돌아온다"""
    frames = []
    cells = [(17.6 + 2.2 * i, 10.6 + 2.2 * j) for j, row in enumerate(QMARK[:-1]) for i, ch in enumerate(row)
             if ch == "#"]
    for k in range(N):
        f = {}
        m, big = set(), set()
        n = len(cells) + 1
        for i, (x, y) in enumerate(cells):
            d = (k * n / N - i) % n
            (big if d < 1.5 else m).update(disc(x, y, 1.2 + (0.5 if d < 1.5 else 0.0)))
        solid(f, m, HONEY, HONEY_D)
        solid(f, big - m, HONEY_L, HONEY_D)
        bob = 1 if (k * n / N - len(cells)) % n < 1.5 else 0
        o, _, _ = draw(Rig(22.5, 26.0 - bob, 0.0, 1.0), pot_parts((0.0, 0.0), 2.0, drip=0.6))
        f.update(o)
        f.update(arrow_bear(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def person() -> list[dict]:
    """작은 화살표 곰 + 아기곰을 목말 태운 사람이 손을 흔든다 — 곰은 사람 머리 위에 턱을 괴고 앞발을 얹었다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        rig = Rig(21.6, 20.8, 0.0, 0.62)
        wave = -2.4 * abs(math.sin(ph))
        hand_ = (9.0, 1.4 + wave)
        bh = -7.2   # 곰 머리 가운데 — 사람 머리 꼭대기에 턱을 괸다
        parts = [("hand", ell(*hand_, 1.8, 1.8), SKIN, True), ("sleeve", bar((5.6, 8.0), hand_, 1.7), SHIRT, False),
                 ("bpaw", any_of(ell(-4.3, -1.8, 1.8, 1.6), ell(4.3, -1.8, 1.8, 1.6)), FUR, True),
                 ("bmuz", ell(0.0, bh + 2.0, 2.3, 1.6), MUZ, False),
                 ("bhead", ell(0.0, bh, 5.4, 4.4), FUR, True),
                 ("bear_in", any_of(ell(-4.2, bh - 3.6, 1.0, 1.0), ell(4.2, bh - 3.6, 1.0, 1.0)), EAR_IN, False),
                 ("bear", any_of(ell(-4.2, bh - 3.6, 2.2, 2.2), ell(4.2, bh - 3.6, 2.2, 2.2)), FUR, False),
                 ("face", ell(0.0, 0.6, 4.4, 4.2), SKIN, True),
                 ("torso", ell(0.0, 11.0, 7.6, 5.6), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
        o, _, _ = draw(rig, parts)
        for sg in (-1, 1):
            eye(o, rig, sg * 2.0 - 0.8, 1.0, big=False, shut=(k == 6))
            eye(o, rig, sg * 2.4 - 0.8, bh - 1.0, big=False, shut=(k == 3))
        x, y = rig.cell(-0.4, bh + 1.4)
        o[x, y], o[x + 1, y] = NOSE, NOSE
        f.update({p: c for p, c in o.items() if p[1] <= 30})
        f.update(arrow_bear(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def pin() -> list[dict]:
    """작은 화살표 곰 + 빨간 지도 핀(크림 동그라미 속 꿀방울)이 꿀단지 옆에서 통통 튄다 — 땅에 닿으면 방울이 반짝"""
    frames = []
    for k in range(N):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 20.5, 13.5 + dy
        for x in range(17, 25):   # 그림자 — 높을수록 옅게
            f.setdefault((x, 29), hx("3f7a3570") if dy else hx("3f7a35b0"))
        o, _, _ = draw(Rig(27.0, 26.2, 0.0, 1.0), pot_parts((0.0, 0.0), 2.7, drip=0.7))
        f.update(o)
        solid(f, disc(cx, cy, 6.4) | raster([(cx - 4.4, cy + 3.6), (cx + 4.4, cy + 3.6), (cx, cy + 12.4)]),
              SIGN, SIGN_D)
        m = disc(cx, cy + 0.2, 4.2)
        solid(f, m, LABEL, OUT)
        dm = disc(cx, cy + 1.0, 1.9) | raster([(cx - 1.3, cy), (cx + 1.3, cy), (cx, cy - 3.2)])
        solid(f, dm, HONEY, HONEY_D)
        x0, y0 = math.floor(cx), math.floor(cy)
        f[x0 - 1, y0] = HI if dy == 0 else HONEY_L
        f.update(arrow_bear(k, small=True))
        frames.append(finish(clip(f)))
    return frames


IX = 9   # I 기둥(꿀 줄기) 왼쪽 칸


def ibeam() -> list[dict]:
    """위 벌집에서 아래 꿀단지로 흘러내리는 꿀 줄기 — 벌집이 I 의 위 가로획, 꿀단지가 아래 가로획, 줄기가 세로획.
    옆에 앉은 곰이 앞발로 줄기를 받아 날름 핥는다. 핫스팟은 줄기 가운데"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for y in range(5, 26):   # 꿀 줄기 2칸 — 덩이가 아래로 흘러내린다
            lump = (y - k * 2) % 6 == 0
            f[IX, y] = HONEY_L if not lump else HONEY
            f[IX + 1, y] = HONEY_D if lump else HONEY
        for j in range(3):       # 벌집 — 육각 칸 무늬
            for x in range(IX - 4, IX + 6):
                f[x, 2 + j] = COMB_D if (x + (j % 2) * 2) % 4 == 0 or j == 2 else COMB
        o, _, _ = draw(Rig(IX + 0.5, 27.4, 0.0, 1.0), pot_parts((0.0, 0.0), 2.9, honey=False))
        f.update(o)
        # 0–2 앞발을 줄기 밑에 대고 받음 · 3–5 받은 꿀을 입으로 · 6–11 날름 (옆모습은 작게 그리면 강아지로 읽혀서 앞모습)
        t = k % 12
        if t < 3:
            paw, mood, tg = (-8.2, 2.6), "smile", 0
        elif t < 6:
            paw, mood, tg = (-5.0 + 1.6 * (t - 3), 3.0), "smile", 0
        else:
            paw, mood, tg = (-1.4, 3.6), "happy", 1 + t % 2
        rig = Rig(IX + 10.0, 17.6, 0.0, 0.82)
        o, _ = front(rig, mood, paws=(paw, (3.6, 7.2)), tongue=tg)
        f.update(o)
        x, y = rig.cell(paw[0], paw[1] - 1.0)
        if t >= 3:
            f[x, y] = HONEY
        tuft(f, IX + 3, 30, 30, k)
        frames.append(finish(clip(f)))
    return frames


TIP, BACK = (1.5, 29.5), (25.0, 10.5)   # 꿀 막대 끝 · 손잡이 끝(화면)


def dipper_parts(p_tip, p_top, r: float, drip: float = 0.0) -> list:
    """p_tip(꿀이 맺힌 끝) → p_top 꿀 막대. 끝 쪽 길이 3r 남짓은 홈 파인 머리(꿀 · 짙은 홈), 나머지는 나무 손잡이"""
    ex, ey = p_top[0] - p_tip[0], p_top[1] - p_tip[1]
    L = math.hypot(ex, ey)
    ux, uy = ex / L, ey / L
    hl = r * 3.4

    def headc(a, b):
        t = (a - p_tip[0]) * ux + (b - p_tip[1]) * uy
        return HONEY_D if (t % 1.6) < 0.55 and t > 0.8 else HONEY

    def handlec(a, b):
        s = -(a - p_tip[0]) * uy + (b - p_tip[1]) * ux
        return WOOD if s < 0 else WOOD_D
    mid = (p_tip[0] + ux * hl, p_tip[1] + uy * hl)
    return [("dhead", bar(p_tip, mid, r * 0.55, r * 1.05), headc, True),
            ("dhandle", bar(mid, p_top, r * 0.62, r * 0.7), handlec, False)]


def pen() -> list[dict]:
    """끝이 홈 파인 꿀 막대를 끌어안고 쓴다 — 곰과 막대가 끝을 축으로 살짝 까딱이고 끝에 꿀이 맺혔다 번진다.
    막대 끝이 핫스팟"""
    frames = []
    base = Rig(20.6, 19.0, 0.0, 0.6)
    L = math.hypot(BACK[0] - TIP[0], BACK[1] - TIP[1])
    ux, uy = (BACK[0] - TIP[0]) / L, (BACK[1] - TIP[1]) / L
    paws = (base.local(TIP[0] + ux * L * 0.6, TIP[1] + uy * L * 0.6),
            base.local(TIP[0] + ux * L * 0.76, TIP[1] + uy * L * 0.76))
    for k, ph in enumerate(phases()):
        d = math.radians(3.0 * math.sin(2 * ph))
        ox, oy = base.ox - TIP[0], base.oy - TIP[1]
        rig = Rig(TIP[0] + ox * math.cos(d) - oy * math.sin(d), TIP[1] + ox * math.sin(d) + oy * math.cos(d),
                  math.degrees(d), base.k)
        dip = dipper_parts(base.local(*TIP), base.local(*BACK), 1.7 / base.k)
        f, _ = front(rig, "blink" if k == 4 else "smile", paws=paws, mid=dip, tongue=1 if k % 6 in (1, 2) else 0)
        f[math.floor(TIP[0]), math.floor(TIP[1])] = HONEY_D
        if k % 4 == 3:   # 끝에서 꿀이 번진다
            f.setdefault((math.floor(TIP[0]) + 2, math.floor(TIP[1])), HONEY)
        frames.append(finish(clip(f)))
    return frames


def up() -> list[dict]:
    """뒷발 끝으로 서서 두 앞발을 머리 위로 V 자로 쭉 뻗고(만세) 하품하는 기지개 — 왼 앞발 끝이 핫스팟(제자리).
    앞발을 머리 위에 모으면 팔이 머리 뒤로 숨어 모자로 읽혀서 벌렸다. 팔은 머리 뒤로 보내 동그란 귀가 앞에 보이게 한다.
    몸이 늘었다 줄었다 하며 하품할 때 입이 쩍 벌어지고 눈을 감는다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        tuft(f, 1, 30, 30, k)
        s = 0.5 - 0.5 * math.cos(ph)      # 0 → 1(가장 늘임) → 0
        ky = 0.9 * (1.0 + 0.08 * s)
        kx = 0.86 * (1.0 - 0.05 * s)
        tip_w = -11.0
        rig = Rig(15.5, 2.6 - tip_w * ky, 0.0, kx=kx, ky=ky)
        o, _ = front(rig, "blink" if s > 0.5 else "smile", paws=((-8.4, tip_w + 2.4), (8.4, tip_w + 2.4)), pads=(0, 1), arm=2.1,
                     arm_back=True, soles=False, yawn=max(0.0, (s - 0.4) / 0.6), legs=((-2.6, 12.0), (2.6, 12.0)))
        f.update(o)
        frames.append(finish(clip(f)))
    return frames


def move() -> list[dict]:
    """두 팔을 양옆으로 벌리고 좌우로 기우뚱 뒤뚱 — 무게를 실은 쪽 발이 땅에 붙고 반대 발이 든다.
    네 방향 풀잎 화살촉이 바깥으로 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o_ = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o_), 15 + dy * (13 + o_), dx, dy, GRASS)
        s = math.sin(ph)
        rig = Rig(15.5 - 0.8 * s, 12.6, -9.0 * s, 0.72)
        lift = 0.8 * abs(s)
        legs = ((-2.8, 11.0 - (lift if s > 0 else 0.0)), (2.8, 11.0 - (lift if s < 0 else 0.0)))
        o, _ = front(rig, "smile" if k != 8 else "blink", paws=((-8.4, 4.0 - 1.0 * s), (8.4, 4.0 + 1.0 * s)),
                     soles=False, legs=legs)
        f.update(o)
        frames.append(finish(clip(f)))
    return frames


def ns() -> list[dict]:
    """위 나뭇가지에 두 앞발로 매달려 대롱대롱 기지개 — 몸을 쭉 늘였다 동그랗게 웅크렸다, 다리가 대롱인다.
    위아래 풀잎 화살촉이 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        s = math.sin(ph)
        o = 1 if s > 0.3 else 0
        for sg in (-1, 1):
            chevron(f, 15, 15 + sg * (13 + o), 0, sg, GRASS if o else GRASS_D)
        twig(f, 6, 25, 6, knots=(8, 22))
        ky = 0.66 * (1.0 + 0.12 * s)
        kx = 0.7 * (1.0 - 0.05 * s)
        grip = -10.4
        rig = Rig(15.5, 6.6 - grip * ky, 0.0, kx=kx, ky=ky)
        sw = 0.6 * math.sin(2 * ph)
        b, _ = front(rig, "happy" if s > 0.6 else "smile", paws=((-2.8, grip), (2.8, grip)), soles=False,
                     legs=((-2.6 + sw, 11.8), (2.6 + sw, 11.8)))
        f.update(b)
        twig(f, 6, 25, 6, knots=())   # 가지가 앞발 위로 지나가게 — 앞발이 쥔 것처럼 보인다
        for sg in (-1, 1):
            x, y = rig.cell(sg * 2.8, grip)
            f[x, y + 1] = OUT
        frames.append(finish(clip(f)))
    return frames


def sprawl(ang: float, fl: bool = False) -> list[dict]:
    """그 축으로 배를 깔고 엎드려 기지개 — 앞발은 코 앞으로, 뒷발은 꼬리 뒤로 쭉 뻗어 화살 노릇을 하고,
    몸을 폈다 모았다 하며 양 끝 풀잎 화살촉이 두근댄다. 몸 가운데가 판 가운데"""
    frames = []
    t = math.radians(ang)
    ux, uy = math.cos(t), math.sin(t)
    dx, dy = round(ux), round(uy)
    diag = dx != 0 and dy != 0
    R = 10 if diag else 13
    k_ = 0.66 if diag else 0.74
    for k, ph in enumerate(phases()):
        f = {}
        s = math.sin(ph)
        o = 1 if s > 0.3 else 0
        for sg in (-1, 1):
            chevron(f, 15 + sg * dx * (R + o), 15 + sg * dy * (R + o), sg * dx, sg * dy, GRASS if o else GRASS_D)
        reach = 0.75 + 0.25 * s
        st = 1.0 + 0.06 * s
        mid = 8.4 + (14.8 - 8.4) * st          # 몸 가운데(a) — 배 쪽(b=3.6)으로 내려 몸 속이 판 가운데에 오게
        wx, wy = Rig(0.0, 0.0, ang, k_, fl=fl).world(mid, 3.6)
        rig = Rig(15.5 - wx, 15.5 - wy, ang, k_, fl=fl)
        b, _ = side(rig, reach=reach, stretch=st, shut=(s > 0.6), sniff=k % 3 == 1)
        f.update(b)
        frames.append(finish(clip(f)))
    return frames


def we():
    return sprawl(180.0, fl=True)


def nwse():
    return sprawl(45.0)


def nesw():
    return sprawl(135.0, fl=True)


def no() -> list[dict]:
    """빨간 금지 표지 안에서 꿀단지를 등 뒤로 감추고 고개를 도리도리(안 줘!) — 눈을 질끈 감고 입을 삐죽,
    단지는 몸 옆으로 빼꼼 보인다. 빗금은 몸 앞에 긋는다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f, slash=False)
        sh = math.sin(2 * ph)
        pot = pot_parts((7.6, 4.6), 3.2, drip=0.5)
        rig = Rig(14.2 + 0.6 * sh, 12.8, 7.0 * sh, 0.74)
        o, _ = front(rig, "squeeze", paws=((-4.6, 8.0), (4.4, 5.4)), extra=(), soles=True, behind=pot)
        f.update(o)
        sign(f, ring=False)
        frames.append(finish(clip(f)))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def top_cell(fr, xmax: int = 31):
    """맨 위 불투명 칸(같으면 왼쪽) — xmax 보다 왼쪽에서만, 장 전부에서 불투명한 칸 가운데"""
    common = set.intersection(*[{p for p, c in f.items() if c[3] == 255} for f in fr])
    return min((p for p in common if p[0] < xmax), key=lambda p: (p[1], p[0]))


HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1),
       "wait": (15, 15), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (IX, 15),
       "pen": (math.floor(TIP[0]), math.floor(TIP[1])),
       "hand": lambda fr: top_cell(fr, 13), "up": lambda fr: top_cell(fr)}


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

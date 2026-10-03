# SPDX-License-Identifier: Apache-2.0
"""개구리(froganim) 구성표 그림 `art/froganim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/frog.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

숲속 친구들 · 애니 묶음의 한 마리. 칸마다 개구리가 그 칸 뜻에 맞는 짓을 따로 한다(`SCENE`).
치비 비율 — 연두 큰 머리 · 머리 위로 툭 튀어나온 눈 둘(2×2 콩알 눈에 흰 반짝) · 얼굴을 가로지르는 넓은 웃는 입 ·
분홍 볼터치 · 크림 턱과 배 · 넓게 벌린 물갈퀴 발. 실루엣의 주인공은 머리 위 눈 둘과 옆으로 넓은 머리, 그리고
쭉 뻗는 분홍 혀다 — 혀는 가리키는 칸(arrow · hand)의 손가락 노릇을 하고 끝 덩이가 핫스팟이라 끝 칸을 불투명하게 둔다.
소품은 연잎 · 파리 · 물방울과 묶음 공통의 나뭇잎 · 잔가지다. 연잎은 개구리(노란 연두)와 갈리게 푸른 초록이다.

  arrow   왼쪽 위로 혀를 쭉 뻗은 옆모습 개구리 — 혀 끝 덩이가 핫스팟. 혀 끝은 제자리에 붙어 있고 몸이 당겼다
          늦췄다 하며 턱 밑이 벌떡인다
  busy    작은 화살표 개구리 + 오른쪽 아래 연잎 둘레를 파리 한 마리가 흐린 자취를 끌며 빙빙 돈다
  cross   물 위로 머리만 내놓은 개구리가 조준선 한가운데 파리를 올려다본다 — 파리가 핫스팟
  hand    연잎에 앉아 고개를 들고 혀를 곧게 위로 뻗어 물방울을 콕 — 터지면 반짝. 혀 끝이 핫스팟
  help    작은 화살표 개구리 + 물방울로 찍은 물음표(점은 파리). 글자 마디가 차례로 부푼다
  ibeam   물속에서 연잎 줄기를 붙잡고 헤엄치는 개구리 — 물 위 연잎이 I 의 위 가로획, 바닥 진흙이 아래 가로획,
          줄기가 세로획. 뒷다리를 차면 물방울이 오른다. 핫스팟은 줄기 가운데
  move    둥근 연잎 위에서 위에서 본 개구리가 팔다리를 네 대각으로 쫙 폈다 모았다 — 네 방향 풀잎 화살촉
  ns      앞모습으로 높이 뛰어올라 두 팔을 V 로 들고 긴 뒷다리를 축 늘어뜨렸다가 쪼그려 앉는다 — 위아래 화살촉
  we · nwse · nesw   위에서 본 개구리가 그 축으로 멀리뛰기 — 앞으로 모은 앞발과 V 로 찬 물갈퀴 뒷발이 양 끝.
          옆모습으로 뻗으면 납작하고 길어 악어로 읽혀서 위에서 본 모습이다
  no      빨간 금지 표지 안에서 눈을 질끈 감고 턱 밑 울음주머니를 풍선처럼 부풀린 채 도리도리(개굴!)
  pen     갈대 펜을 끌어안은 개구리 — 비스듬히 깎은 펜촉 끝(왼쪽 아래)이 핫스팟. 펜촉을 축으로 살짝 까딱인다
  person  작은 화살표 개구리 + 눈 둘이 달린 개구리 모자를 쓴 사람이 손을 흔든다
  pin     작은 화살표 개구리 + 빨간 지도 핀이 물 위 연잎에 통통 꽂히고 꽂힐 때마다 물결이 퍼진다
  up      위에서 본 개구리가 물 위를 위로 헤엄쳐 간다(평영) — 코끝이 핫스팟, 뒤로 V 자 물결
  wait    연잎에 앉아 날아다니는 파리를 보다가 혀로 휙 낚아채 꿀꺽 — 삼킬 때 눈을 감는다. 가운데(몸)가 핫스팟

몸은 부위(타원 · 굵기가 변하는 막대)를 개구리 제 좌표에 놓고 화면으로 돌려 찍는다(`Rig`, `draw` — 토끼와 같은 틀).
앞모습(`front`) · 옆모습(`side`) · 위에서 본 모습(`top`) 세 벌이다. 그리개는 gen/rabbit.py 와 같은 꼴이지만 다른
생성기를 import 하지 않으려고 여기 따로 둔다(그쪽을 고치면 이 그림이 조용히 바뀌지 않게). 혀는 개구리보다 먼저
화면 좌표로 따로 그린다(`tongue`) — 부위로 그리면 두 칸 굵기라 전부 테두리 칸이 돼 까만 줄이 된다.
빌드가 부르지 않고 손으로 돌린다 · 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, WAKE, BUB, disc, finish, hx, ink, phases, raster, solid, write

SID = "froganim"

OUT, EYE, HI = hx("1f3a1cff"), hx("15200fff"), hx("fffaf0ff")                  # 테두리 · 눈 · 반짝
SKIN, SKIN_S, SKIN_D = hx("92d050ff"), hx("76b63eff"), hx("5a9431ff")          # 몸 · 그늘 · 먼 다리
BELLY, BELLY_S = hx("f6f0c8ff"), hx("e4dba4ff")                                # 턱 · 배
TONGUE, TONGUE_D = hx("f57d9eff"), hx("c84f72ff")                              # 혀
BLUSH, MOUTH = hx("f49a9aff"), hx("2c4a20ff")                                  # 볼터치 · 입
ink(OUT, HI, hx("f6e9d2c7"))
PAD, PAD_D, PAD_L = hx("3f9a6cff"), hx("27694aff"), hx("62b88aff")             # 연잎 (개구리보다 푸르다)
LOTUS = hx("f6a8c4ff")                                                         # 연꽃 봉오리
FLY, WING = hx("34343eff"), hx("e6f2ffb4")                                     # 파리
GRASS, GRASS_D, GRASS_L = hx("5aa04aff"), hx("3f7a35ff"), hx("86c46aff")       # 풀 · 나뭇잎 (묶음 공통)
MUD, MUD_D = hx("7a6244ff"), hx("54422cff")                                    # 진흙 바닥
REED, REED_D, NIB = hx("d8c27aff"), hx("a08a48ff"), hx("2a2a36ff")             # 갈대 펜 · 먹
SKINP, SHIRT, SHIRT_D = hx("f4e2c4ff"), hx("e8a23cff"), hx("b87a22ff")         # 사람 (노란 비옷)
WATER = hx("7cc4d860")                                                         # 물속 (아주 옅게)


# ── 그리개: 개구리 제 좌표 (a, b) → 화면 ────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도, a 축이 화면에서 가리키는 쪽, 90 이 아래) · 배율 k(a 축 kx, b 축 ky 를 따로 줄 수
    있다) · 뒤집기 fl. b 축은 a 축을 시계 방향으로 90도 돌린 쪽(ang=0 이면 a 가 오른쪽, b 가 아래). fl 이면 b 축을 반대로"""

    def __init__(self, ox: float, oy: float, ang: float = 0.0, k: float = 1.0, fl: bool = False,
                 kx: float = None, ky: float = None):
        t = math.radians(ang)
        self.ox, self.oy, self.c, self.s = ox, oy, math.cos(t), math.sin(t)
        self.ang, self.fl, self.k = ang, fl, k
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


def anchor(ang: float, k: float, a: float, b: float, x: float, y: float, fl: bool = False) -> Rig:
    """제 좌표 (a, b) 가 화면 (x, y) 에 오는 Rig"""
    r = Rig(0.0, 0.0, ang, k, fl)
    wx, wy = r.world(a, b)
    return Rig(x - wx, y - wy, ang, k, fl)


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
    hs = [h for h in hs if h]
    return lambda a, b: any(h(a, b) for h in hs)


def lerp(p, q, t):
    return p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t


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


def tongue(f: dict, p0, p1, w: float = 0.75, tip: float = 1.5) -> None:
    """화면 p0(입) → p1(끝) 분홍 혀. 끝은 둥근 덩이(반지름 tip). 가장자리는 짙은 분홍 — 까만 테를 두르면
    두 칸 굵기 혀가 통째로 테두리가 된다"""
    n = max(1, math.ceil(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) * 3))
    m = set()
    for i in range(n + 1):
        x, y = p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n
        m |= disc(x, y, w)
    m |= disc(p1[0], p1[1], tip)
    solid(f, m, TONGUE, TONGUE_D)


def mouth_line(f: dict, rig: Rig, pts) -> None:
    for a, b in pts:
        f[rig.cell(a, b)] = MOUTH


# ── 앞모습: u 가로(+오른쪽), w 세로(+아래), 원점은 얼굴 가운데 ────────────────────
def front(rig: Rig, mood: str = "smile", paws=((-3.2, 6.8), (3.2, 6.8)), legs: float = None, extra=(), mid=(),
          body: bool = True, look=(0.0, 0.0), pouch: float = 0.0, gape: bool = False, small: bool = False,
          tilt: float = 0.0) -> tuple[dict, set]:
    """앞모습 개구리 한 장. paws 는 앞발 끝들(어깨에서 막대로 잇는다, None 이면 안 그린다), legs 가 None 이면 뒷다리를
    접어 몸 옆에 앉고, 숫자면 그만큼(0–1) 아래로 축 늘어뜨린다(뛰어오른 꼴). extra 는 맨 앞 부위, mid 는 앞발 뒤 ·
    몸 앞 부위. look 은 눈동자를 옮길 칸(가로 · 세로, 눈마다 (좌, 우) 쌍도 된다), pouch 는 턱 밑 울음주머니를
    부풀린 정도(0–1), gape 면 입 가운데가 벌어져 혀가 나온다. mood: smile · blink · shut · chew.
    tilt 는 눈 둘이 기운 정도(도리도리, 칸)"""
    pads, arms = [], []
    for au, aw in (paws or ()):
        sh = (math.copysign(3.8, au), 4.4)
        arms.append(bar(sh, (au, aw), 1.2, 1.1))
        pads.append(ell(au, aw, 1.4, 1.2))
    bumps = [ell(sg * 3.5, -3.7 + sg * tilt, 2.5, 2.4) for sg in (-1, 1)]
    head = any_of(ell(0.0, 0.2, 6.6, 4.3), *bumps)

    def headc(a, b):
        return BELLY if b > 2.3 and abs(a) < 5.0 else SKIN

    def bodyc(a, b):
        return BELLY if abs(a) < 3.0 and b > 4.6 else SKIN
    parts = list(extra)
    if pouch > 0:
        parts += [("pouch", ell(0.0, 3.2 + 1.6 * pouch, 2.4 + 2.2 * pouch, 1.2 + 1.8 * pouch),
                   lambda a, b: HI if (a < -0.6 and b < 3.0 + 1.2 * pouch) else BELLY, True)]
    parts += [("paw", any_of(*pads), SKIN, True)] if pads else []
    parts += list(mid)
    parts += [("arm", any_of(*arms), SKIN, False)] if arms else []
    parts += [("head", head, headc, True)]
    if legs is None:
        feet = [bar((sg * 4.2, 10.6), (sg * 8.0, 10.3), 1.0, 1.4) for sg in (-1, 1)]
        thighs = [ell(sg * 4.8, 7.8, 2.4, 2.4) for sg in (-1, 1)]
    else:
        s = legs
        feet, thighs = [], []
        for sg in (-1, 1):
            hip = (sg * 2.6, 8.0)
            knee = (sg * (4.6 - 0.8 * s), 10.2 + 2.6 * s)
            ank = (sg * (3.4 - 0.4 * s), 12.0 + 5.0 * s)
            toe = (sg * (4.6 + 0.6 * s), 13.2 + 6.6 * s)
            thighs.append(any_of(bar(hip, knee, 2.2, 1.6), bar(knee, ank, 1.5, 1.2)))
            feet.append(bar(ank, toe, 1.1, 2.0))
    if body:
        parts += [("foot", any_of(*feet), SKIN, True), ("thigh", any_of(*thighs), SKIN_S, True),
                  ("body", ell(0.0, 6.6, 4.8, 3.9), bodyc, False)]
    out, mask, _ = draw(rig, parts)
    looks = look if isinstance(look[0], (tuple, list)) else (look, look)
    for sg, (lx, ly) in zip((-1, 1), looks):
        a, b = sg * 3.5 - 0.6 + lx, -4.1 + ly + sg * tilt
        eye(out, rig, a, b, big=not small, shut=mood in ("blink", "shut"))
        if mood == "shut" and not small:   # 질끈 — 감은 눈 위로 한 칸 더
            x, y = rig.cell(a, b)
            out[x + (1 if sg < 0 else 0), y] = EYE
    for sg in (-1, 1):
        dot(out, rig, sg * 5.0, 1.0, BLUSH)
    # 넓게 웃는 입: 가운데가 처지고 양 끝이 올라간다
    pts = [(u / 2, 1.0 + 0.8 * (1 - (u / 2 / 3.8) ** 2)) for u in range(-8, 9)]
    if mood == "chew":
        pts = [(u / 2, 1.5) for u in range(-6, 7)]
    mouth_line(out, rig, pts)
    if gape:
        x, y = rig.cell(0.0, 1.8)
        out[x, y], out[x - 1, y], out[x, y + 1], out[x - 1, y + 1] = TONGUE, TONGUE, MOUTH, MOUTH
    return out, mask


# ── 옆모습: a 는 코끝 d → 엉덩이, b 는 + 가 배(발) 쪽 ──────────────────────────────
def side(rig: Rig, d: float = 0.0, mood: str = "smile", pouch: float = 0.0, simple: bool = False,
         reach: float = 0.0, extra=()) -> tuple[dict, set]:
    """앉은 옆모습 개구리 한 장. 코끝이 a=d. reach 는 앞발을 앞으로 뻗은 정도(0–1), pouch 는 턱 밑이 벌떡인 정도.
    먼 눈 · 먼 다리는 짙은 그늘로 몸 뒤에 둔다. simple 이면 작게 그릴 때라 먼 다리 · 넓적다리 선을 뺀다.
    뛰는 옆모습은 납작하고 길어 악어로 읽혀서 두지 않는다(크기 조절 칸은 위에서 본 모습)"""
    D = d
    sh = (D + 5.8, 2.8)
    hand = lerp((D + 4.8, 6.0), (D - 1.6, 3.8), reach)

    def headc(a, b):
        return BELLY if b > 1.7 + 0.12 * (a - D) and a < D + 7.6 else SKIN

    def bodyc(a, b):
        return BELLY if b > 3.0 + 0.3 * (a - D - 8.0) and a < D + 12.0 else SKIN
    # 넓적다리가 몸 옆에 동그랗게 접히고 물갈퀴 발이 앞으로 놓인다
    legs = [("foot", bar((D + 11.6, 6.3), (D + 5.8, 6.7), 0.8, 1.3), SKIN, True),
            ("thigh", ell(D + 11.0, 4.0, 3.0, 2.2, -0.25), SKIN_S, not simple)]
    far = [("far_leg", bar((D + 12.6, 6.0), (D + 8.0, 6.2), 0.8, 1.1), SKIN_D, False)]
    bod = ell(D + 9.4, 2.2, 5.0, 3.4, 0.42)
    parts = list(extra)
    if pouch > 0:
        parts += [("pouch", ell(D + 3.2, 2.9 + 0.5 * pouch, 1.8 + 1.1 * pouch, 0.9 + 0.9 * pouch), BELLY, True)]
    parts += [
        ("hand", ell(hand[0], hand[1], 1.4, 1.0), SKIN, True),
        ("arm", bar(sh, hand, 1.1, 1.0), SKIN, False),
        ("head", any_of(ell(D + 4.2, 0.5, 4.5, 3.1), ell(D + 1.4, 0.9, 1.6, 1.8), ell(D + 4.9, -2.3, 2.5, 2.4)),
         headc, False)] + legs + [
        ("body", bod, bodyc, False),
        ("far_eye", ell(D + 6.9, -2.5, 2.0, 2.0), SKIN_D, False)]
    if not simple:
        parts += [("far_arm", bar((D + 6.8, 2.6), (hand[0] + 1.6, hand[1] - 0.2), 1.0), SKIN_D, False)] + far
    out, mask, _ = draw(rig, parts)
    eye(out, rig, D + 4.4, -2.9, big=not simple, shut=mood in ("blink", "shut"))
    dot(out, rig, D + 6.6, 0.5, BLUSH)
    # 웃는 입: 코끝 밑에서 눈 밑까지 거의 곧게, 끝만 살짝 올라간다
    mouth_line(out, rig, [(D + 0.9 + i * 0.5, 1.4 + 0.04 * i) for i in range(10)] + [(D + 5.9, 1.0)])
    return out, mask


def mouth_at(rig: Rig, d: float = 0.0) -> tuple:
    """옆모습 입 앞 끝(혀가 나오는 자리)의 화면 좌표"""
    return rig.world(d + 0.9, 1.3)


# ── 위에서 본 모습: u 가로, w 세로(+ 가 꽁무니), 원점은 몸 가운데 ────────────────────
def top(rig: Rig, kick: float = 0.0, arms: float = 0.0, spread: float = None, mood: str = "smile",
        reach: float = 0.0) -> tuple[dict, set]:
    """위에서 본 개구리. kick 은 뒷다리를 뒤로 쭉 찬 정도(0 접음 – 1 폄), arms 는 앞발을 뒤로 저은 정도,
    reach 는 앞발을 머리 앞으로 모아 뻗은 정도(뛰어드는 꼴). spread 를 주면 팔다리를 네 대각으로 별처럼 편다(0 모음 – 1 쫙)"""
    parts = []
    limbs, hands, feet, thighs = [], [], [], []
    for sg in (-1, 1):
        if spread is None:
            hd = lerp((sg * 5.8, -5.2), (sg * 5.6, 1.6), arms)
            el = lerp((sg * 5.4, -1.6), (sg * 6.4, -0.6), arms)
            hd = lerp(hd, (sg * 2.6, -9.4), reach)
            el = lerp(el, (sg * 4.8, -4.6), reach)
            knee = lerp((sg * 7.4, 4.4), (sg * 5.6, 9.6), kick)     # 찬 다리는 V 자로 벌어진다 — 모으면 막대 둘이다
            ank = lerp((sg * 4.4, 8.4), (sg * 6.0, 13.8), kick)
            toe = lerp((sg * 6.6, 10.2), (sg * 8.0, 16.8), kick)
        else:
            s = spread
            hd = (sg * (5.0 + 2.4 * s), -5.0 - 1.8 * s)
            el = (sg * (5.0 + 0.8 * s), -1.6 - 0.6 * s)
            knee = (sg * (6.8 + 0.8 * s), 4.6 + 0.6 * s)
            ank = (sg * (5.0 + 2.4 * s), 8.0 + 1.8 * s)
            toe = (sg * (6.8 + 3.0 * s), 9.8 + 2.6 * s)
        limbs.append(any_of(bar((sg * 3.0, -0.6), el, 1.1, 1.0), bar(el, hd, 1.0, 0.9)))
        hands.append(ell(hd[0], hd[1], 1.3, 1.3))
        thighs.append(any_of(bar((sg * 2.6, 5.0), knee, 1.8, 1.3), bar(knee, ank, 1.2, 1.0)))
        feet.append(bar(ank, toe, 0.9, 1.6))
    head = any_of(ell(0.0, -3.6, 4.6, 3.4), ell(-3.0, -4.2, 2.1, 2.1), ell(3.0, -4.2, 2.1, 2.1))

    def backc(a, b):   # 등에 짙은 점 둘 — 위에서 본 개구리 등 무늬
        if (a + 1.4) ** 2 + (b - 1.0) ** 2 < 1.0 or (a - 1.6) ** 2 + (b - 3.2) ** 2 < 1.0:
            return SKIN_S
        return SKIN
    parts += [("hand", any_of(*hands), SKIN, True), ("arm", any_of(*limbs), SKIN, False),
              ("head", head, SKIN, True),
              ("foot", any_of(*feet), SKIN, True), ("thigh", any_of(*thighs), SKIN_S, True),
              ("body", ell(0.0, 1.8, 4.2, 4.9), backc, False)]
    out, mask, _ = draw(rig, parts)
    for sg in (-1, 1):
        eye(out, rig, sg * 3.0 - 0.6, -4.8, shut=mood == "blink")
    return out, mask


# ── 화살표 개구리: 혀 끝이 (1, 1) ─────────────────────────────────────────────────
def arrow_frog(k: int, small: bool = False) -> dict:
    """왼쪽 위로 혀를 쭉 뻗은 옆모습 개구리. 혀 끝 덩이는 (1, 1) 에 붙어 있고 몸이 당겼다 늦췄다 한다"""
    ph = 2 * math.pi * k / N
    pull = 0.5 - 0.5 * math.cos(ph)
    kk = 0.8 if small else 1.1
    dist = (4.2 if small else 5.6) + (0.8 if small else 1.4) * pull     # 혀 끝 → 입 (칸, 대각선을 따라)
    tip = (2.0, 2.0) if small else (2.2, 2.2)
    m = (tip[0] + dist * 0.7071, tip[1] + dist * 0.7071)
    rig = anchor(28.0, kk, 0.9, 1.3, *m)
    f = {}
    tongue(f, m, tip, 0.7 if small else 0.75, 1.2 if small else 1.5)
    o, _ = side(rig, mood="blink" if k == 9 else "smile", pouch=0.0 if small else 0.6 * pull,
                simple=small, reach=0.0)
    f.update(o)
    return f


# ── 소품 ─────────────────────────────────────────────────────────────────────
def lily(f: dict, cx: float, cy: float, rx: float, ry: float, notch: float = 30.0, flower: bool = False) -> None:
    """연잎: 타원에서 notch(도, 0 이 오른쪽, 90 이 아래) 쪽으로 쐐기 하나를 뺐다. 납작하면(ry < 3) 위쪽 반을 밝게,
    둥글면 가운데에서 잎맥이 뻗는다"""
    t = math.radians(notch)
    m = set()
    for p in disc(cx, cy, max(rx, ry) + 1):
        dx, dy = (p[0] + 0.5 - cx) / rx, (p[1] + 0.5 - cy) / ry
        if dx * dx + dy * dy > 1:
            continue
        r = math.hypot(dx, dy)
        if r > 0.2:
            da = (math.atan2(dy, dx) - t + math.pi) % (2 * math.pi) - math.pi
            if abs(da) < 0.28:
                continue
        m.add(p)

    def col(p):
        dx, dy = (p[0] + 0.5 - cx) / rx, (p[1] + 0.5 - cy) / ry
        if ry < 3:
            return PAD_L if dy < 0 else PAD
        ang = math.atan2(dy, dx)
        if math.hypot(dx, dy) > 0.25 and min(abs((ang - t - math.pi / 3 * j + math.pi) % (2 * math.pi) - math.pi)
                                              for j in range(1, 6)) < 0.12:
            return PAD_D
        return PAD_L if dx + dy < -0.5 else PAD
    solid(f, m, col, PAD_D)
    if flower:
        x, y = math.floor(cx), math.floor(cy)
        f[x, y], f[x + 1, y], f[x, y - 1] = LOTUS, LOTUS, HI


def ripple(f: dict, cx: float, cy: float, r: float, col=WAKE[2]) -> None:
    """물결 고리: 납작한 타원 테 (가로 r, 세로 r × 0.35)"""
    ry = max(0.8, r * 0.35)
    for i in range(int(r * 8)):
        a = 2 * math.pi * i / int(r * 8)
        f.setdefault((math.floor(cx + r * math.cos(a)), math.floor(cy + ry * math.sin(a))), col)


def fly(f: dict, x: int, y: int, k: int, alpha: int = 255) -> None:
    """파리: 짙은 몸 두 칸 + 파닥이는 반투명 날개"""
    f[x, y] = FLY[:3] + (alpha,)
    f[x + 1, y] = FLY[:3] + (alpha,)
    if alpha == 255:
        if k % 2:
            f.setdefault((x - 1, y - 1), WING)
            f.setdefault((x + 2, y - 1), WING)
        else:
            f.setdefault((x, y - 1), WING)
            f.setdefault((x + 1, y - 1), WING)


def drop(f: dict, cx: float, cy: float, r: float) -> None:
    """물방울: 파란 테 · 옅은 속 · 왼쪽 위 흰 반짝"""
    solid(f, disc(cx, cy, r), WAKE[0], BUB)
    if r >= 1.6:
        f[math.floor(cx - r * 0.4), math.floor(cy - r * 0.4)] = HI


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


def pond(f: dict, y: int, k: int, x0: int = 1, x1: int = 30) -> None:
    """물낯 한 줄(y)과 그 아래 옅은 물결"""
    for x in range(x0, x1 + 1):
        f.setdefault((x, y), WAKE[1])
        f.setdefault((x, y + 1), WAKE[3] if (x + k) % 3 else WAKE[2])


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    """왼쪽 위로 혀를 쭉 뻗은 옆모습 — 혀 끝 덩이(핫스팟)는 제자리, 몸이 당겼다 늦췄다 하며 턱 밑이 벌떡인다"""
    return [finish(clip(arrow_frog(k))) for k in range(N)]


FLY_PATH = [(24, 6), (20, 4), (15, 3), (10, 4), (6, 6), (4, 9), (4, 9), (5, 10), (5, 10), (28, 3), (27, 5), (26, 6)]


def wait() -> list[dict]:
    """연잎에 앉아 날아다니는 파리를 눈으로 좇다가 혀로 휙 낚아채 꿀꺽 — 삼킬 때 눈을 감고 볼을 오물거린다.
    새 파리가 오른쪽에서 다시 날아든다"""
    frames = []
    rig = Rig(15.5, 13.6, 0.0, 0.8)
    for k, ph in enumerate(phases()):
        f = {}
        pond(f, 27, k)
        lily(f, 15.5, 25.6, 12.6, 2.4, notch=-20.0)
        fx, fy = FLY_PATH[k]
        look = (max(-1.0, min(1.0, (fx - 15.5) / 8)), max(-0.6, min(0.6, (fy - 9) / 6)))
        mood = "smile"
        catch = k in (6, 7)
        if k in (8, 9):
            mood = "shut" if k == 8 else "chew"
        o, _ = front(rig, mood, paws=((-3.0, 7.2), (3.0, 7.2)), look=look, gape=catch,
                     pouch=0.5 if k == 9 else 0.0)
        f.update(o)
        if catch:   # 혀를 파리까지 쭉 — 다음 장은 반쯤 거둬들인다
            m = rig.world(0.0, 1.9)
            end = (fx + 1.0, fy + 0.5) if k == 6 else lerp(m, (fx + 1.0, fy + 0.5), 0.5)
            tongue(f, m, end, 0.7, 1.3)
            fly(f, math.floor(end[0]) - 1, math.floor(end[1]), k)
        elif k not in (8,):
            fly(f, fx, fy, k)
        frames.append(finish(clip(f)))
    return frames


def cross() -> list[dict]:
    """물 위로 눈만 내놓은 개구리가 조준선 한가운데의 파리를 두 눈 몰아 노려본다 — 파리가 핫스팟.
    물낯에 물결이 일고 파리 날개가 파닥인다"""
    frames = []
    rig = Rig(15.5, 25.4, 0.0, 1.0)
    for k, ph in enumerate(phases()):
        f = {}
        for i in range(1, 31):
            if i <= 11 or 20 <= i <= 30:
                f[i, 15] = OUT
            if i <= 11:
                f[15, i] = OUT
        o, _ = front(rig, "blink" if k == 9 else "smile", paws=None, body=False,
                     look=((0.8, -0.4), (-1.0, -0.4)))
        f.update({p: c for p, c in o.items() if p[1] < 27})
        pond(f, 27, k)
        r = 7.5 + (k % 6) * 0.9
        ripple(f, 15.5, 27.8, r, WAKE[2] if k % 6 < 3 else WAKE[3])
        fly(f, 15, 15, k)
        f[14, 15] = FLY
        frames.append(finish(clip(f)))
    return frames


HAND = anchor(-62.0, 0.86, 0.0, 0.0, 13.0, 18.6, fl=True)   # 고개를 쳐든 옆모습. 코끝이 위
HAND_TIP = (6.5, 2.2)


def hand() -> list[dict]:
    """연잎에 앉아 고개를 들고 혀를 곧게 위로 뻗어 물방울을 콕 — 터지면 반짝이 흩어진다. 혀 끝이 핫스팟.
    혀 끝은 제자리이고 몸이 웅크렸다 펴며 혀가 늘었다 줄었다 한다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        pond(f, 23, k, 3, 28)
        lily(f, 15.5, 21.4, 10.0, 1.8, notch=200.0)
        bob = 0.8 * max(0.0, math.sin(ph))
        rig = Rig(HAND.ox, HAND.oy + bob, HAND.ang, HAND.k, True)
        d = 0.0
        m = mouth_at(rig, d)
        tongue(f, m, (HAND_TIP[0], HAND_TIP[1] + 0.8), 0.75, 1.5)
        o, _ = side(rig, d=d, mood="blink" if k in (4, 5) else "smile", reach=0.1)
        f.update(o)
        if k < 4:   # 물방울이 혀 끝에 다가와 닿는다
            drop(f, HAND_TIP[0] + 4.6 - 1.0 * k, 2.6, 1.8)
        elif k in (4, 5):
            x, y = math.floor(HAND_TIP[0]), math.floor(HAND_TIP[1])
            for dx, dy in ((-2, 0), (3, 0), (0, -1) if False else (3, 3), (-2, 3)):
                f.setdefault((x + dx + (k - 4) * (1 if dx > 0 else -1), y + dy), HI if k == 4 else WAKE[1])
        frames.append(finish(clip(f)))
    return frames


def busy() -> list[dict]:
    """작은 화살표 개구리 + 오른쪽 아래 연잎(가운데 연꽃 봉오리) — 둘레를 파리 한 마리가 흐린 자취를 끌며 돈다"""
    frames = []
    cx, cy = 22.0, 22.5
    for k in range(N):
        f = {}
        lily(f, cx, cy, 6.6, 4.6, notch=-60.0, flower=True)
        for j in range(5, 0, -1):   # 자취 — 오래된 것일수록 옅다
            a = 2 * math.pi * (k - j * 0.7) / N
            x, y = math.floor(cx + 7.6 * math.cos(a)), math.floor(cy + 6.4 * math.sin(a))
            f[x, y] = FLY[:3] + (200 - 34 * j,)
        a = 2 * math.pi * k / N
        fly(f, math.floor(cx + 7.6 * math.cos(a)), math.floor(cy + 6.4 * math.sin(a)), k)
        f.update(arrow_frog(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def help_() -> list[dict]:
    """작은 화살표 개구리 + 물방울로 찍은 물음표(점은 파리) — 방울이 글자 차례로 하나씩 부풀었다 돌아온다"""
    frames = []
    cells = [(17.6 + 2.2 * i, 10.6 + 2.2 * j) for j, row in enumerate(QMARK[:-1]) for i, ch in enumerate(row)
             if ch == "#"]
    for k in range(N):
        f = {}
        m, big = set(), set()
        n = len(cells) + 1
        for i, (x, y) in enumerate(cells):
            d = (k * n / N - i) % n
            (big if d < 1.5 else m).update(disc(x, y, 1.45 + (0.4 if d < 1.5 else 0.0)))
        solid(f, m, WAKE[1], BUB)
        solid(f, big - m, WAKE[0], BUB)
        bob = 1 if (k * n / N - len(cells)) % n < 1.5 else 0
        fly(f, 21, 26 - bob, k)
        f.update(arrow_frog(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def person() -> list[dict]:
    """작은 화살표 개구리 + 눈 둘이 달린 개구리 모자를 쓰고 노란 비옷을 입은 사람이 손을 흔든다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        rig = Rig(22.5, 20.8, 0.0, 0.56)
        wave = -2.4 * abs(math.sin(ph))
        hand_ = (8.6, 3.0 + wave)
        bumps = [ell(sg * 3.6, -6.2, 2.6, 2.5) for sg in (-1, 1)]
        parts = [("hand", ell(*hand_, 1.8, 1.8), SKINP, True), ("sleeve", bar((5.4, 9.0), hand_, 1.7), SHIRT, False),
                 ("face", ell(0.0, 0.8, 5.0, 4.4), SKINP, True),
                 ("hood", any_of(ell(0.0, -0.4, 7.2, 6.6), *bumps), SKIN, True),
                 ("torso", ell(0.0, 12.0, 7.6, 6.2), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
        o, _, _ = draw(rig, parts)
        for sg in (-1, 1):
            eye(o, rig, sg * 3.6 - 0.8, -6.6, big=True, shut=(k == 6))   # 모자의 개구리 눈
            eye(o, rig, sg * 2.2 - 0.6, 0.4, big=False, shut=(k == 6))   # 사람 눈
            dot(o, rig, sg * 3.4, 2.4, BLUSH)
        dot(o, rig, 0.0, 2.8, MOUTH)
        f.update({p: c for p, c in o.items() if p[1] <= 30})
        f.update(arrow_frog(k, small=True))
        frames.append(finish(clip(f)))
    return frames


def pin() -> list[dict]:
    """작은 화살표 개구리 + 빨간 지도 핀이 물 위 연잎에 통통 꽂힌다 — 꽂힐 때마다 물결이 퍼진다"""
    frames = []
    for k in range(N):
        f = {}
        pond(f, 29, k, 13, 30)
        lily(f, 22.5, 27.0, 7.6, 2.2, notch=200.0)
        dy = -round(4 * math.sin(math.pi * k / N))
        if k < 4:   # 꽂힌 뒤 물결이 번진다
            ripple(f, 22.5, 28.4, 8.2 + 1.2 * k, WAKE[2] if k < 2 else WAKE[3])
        cx, cy = 22.5, 15.0 + dy
        solid(f, disc(cx, cy, 6.0) | raster([(cx - 4.2, cy + 3.4), (cx + 4.2, cy + 3.4), (cx, cy + 11.6)]),
              SIGN, SIGN_D)
        solid(f, disc(cx, cy, 2.6), BELLY, OUT)
        f[math.floor(cx - 1), math.floor(cy - 1)] = HI
        f.update(arrow_frog(k, small=True))
        frames.append(finish(clip(f)))
    return frames


STEM = 12   # I 기둥(연잎 줄기) 칸


def ibeam() -> list[dict]:
    """물속에서 연잎 줄기를 붙잡고 헤엄치는 개구리 — 물 위 연잎이 I 의 위 가로획, 바닥 진흙이 아래 가로획,
    줄기가 세로획. 뒷다리를 쭉 차면 몸이 한 칸 오르고 입에서 물방울이 오른다. 핫스팟은 줄기 가운데"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for y in range(5, 28):
            f[STEM, y] = PAD_D if y % 5 == 0 else PAD
        lily(f, STEM + 0.5, 3.8, 7.0, 1.8, notch=180.0)
        for x in range(STEM - 5, STEM + 7):   # 진흙 바닥
            f[x, 28] = MUD
            f[x, 29] = MUD_D
        f[STEM - 2, 27], f[STEM + 2, 27] = MUD, MUD
        kick = 0.5 + 0.5 * math.sin(ph)
        rise = 1.0 * kick
        rig = Rig(STEM + 5.4, 12.6 - rise, 90.0, 0.5)    # 머리가 위, 다리가 아래 — 위에서 본 모습을 세운다
        o, _ = top(Rig(rig.ox, rig.oy, 0.0, 0.52), kick=kick, arms=0.0 if kick > 0.5 else 0.6)
        f.update(o)
        f[STEM + 1, round(12.6 - rise - 2)] = SKIN   # 줄기를 쥔 앞발
        f[STEM + 1, round(12.6 - rise - 3)] = OUT
        for j in range(2):   # 오르는 물방울
            t = (k / N + j / 2) % 1
            x, y = STEM + 6 + (j % 2), 9 - 4 * t
            f.setdefault((math.floor(x), math.floor(y)), WAKE[1] if t < 0.6 else WAKE[2])
        frames.append(finish(clip(f)))
    return frames


TIP, BACK = (1.5, 29.5), (25.0, 9.5)   # 갈대 펜촉 · 꽁무니(화면)


def reed_pen(base: Rig) -> list:
    """제 좌표로 그린 갈대 펜 — 마디가 있는 갈대 대롱, 끝은 비스듬히 깎은 펜촉(먹 묻은 끝)"""
    p0, p1 = base.local(*TIP), base.local(*BACK)
    ex, ey = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(ex, ey)
    ux, uy = ex / L, ey / L
    r = 1.5 / base.k
    cut = 5.0 / base.k

    def col(a, b):
        t = (a - p0[0]) * ux + (b - p0[1]) * uy
        s = -(a - p0[0]) * uy + (b - p0[1]) * ux
        if t < cut * 0.35:
            return NIB
        if (t % (6.0 / base.k)) < 0.7 / base.k and t > cut:
            return REED_D
        return REED if s > -r * 0.3 else hx("ecdca0ff")
    body = any_of(bar(p0, (p0[0] + ux * cut, p0[1] + uy * cut), 0.3, r * 0.9),
                  bar((p0[0] + ux * cut, p0[1] + uy * cut), p1, r * 0.9, r))
    return [("pen", body, col, True)]


def pen() -> list[dict]:
    """갈대 펜을 끌어안은 개구리 — 비스듬히 깎은 펜촉 끝이 핫스팟. 개구리와 펜이 펜촉을 축으로 살짝 까딱인다"""
    frames = []
    base = Rig(21.2, 15.6, 0.0, 0.6)
    L = math.hypot(BACK[0] - TIP[0], BACK[1] - TIP[1])
    ux, uy = (BACK[0] - TIP[0]) / L, (BACK[1] - TIP[1]) / L
    paws = (base.local(TIP[0] + ux * L * 0.6, TIP[1] + uy * L * 0.6),
            base.local(TIP[0] + ux * L * 0.76, TIP[1] + uy * L * 0.76))
    for k, ph in enumerate(phases()):
        d = math.radians(3.0 * math.sin(2 * ph))
        ox, oy = base.ox - TIP[0], base.oy - TIP[1]
        rig = Rig(TIP[0] + ox * math.cos(d) - oy * math.sin(d), TIP[1] + ox * math.sin(d) + oy * math.cos(d),
                  math.degrees(d), base.k)
        f, _ = front(rig, "blink" if k == 4 else "smile", paws=paws, mid=reed_pen(base),
                     look=(-0.6, 0.4))
        f[math.floor(TIP[0]), math.floor(TIP[1])] = NIB
        frames.append(finish(clip(f)))
    return frames


def up() -> list[dict]:
    """위에서 본 개구리가 물 위를 위로 헤엄쳐 간다(평영) — 앞발을 저어 젖히고 뒷다리를 쭉 찬다. 코끝이 핫스팟,
    뒤로 V 자 물결이 흘러간다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for j in range(3):   # V 자 물결 — 아래로 흘러간다
            t = (k / N + j / 3) % 1
            y = 17 + 13 * t
            w = 3 + 9 * t
            col = WAKE[2] if t < 0.5 else WAKE[3]
            for sg in (-1, 1):
                f.setdefault((math.floor(15.5 + sg * w), math.floor(y)), col)
                f.setdefault((math.floor(15.5 + sg * (w - 1)), math.floor(y) - 1), col)
        kick = 0.5 + 0.5 * math.sin(ph)
        o, _ = top(Rig(15.5, 11.4, 0.0, 0.88), kick=kick, arms=1.0 - kick, mood="blink" if k == 7 else "smile")
        f.update(o)
        frames.append(finish(clip(f)))
    return frames


def move() -> list[dict]:
    """둥근 연잎 위에서 위에서 본 개구리가 팔다리를 네 대각으로 쫙 폈다 모았다 — 네 방향 풀잎 화살촉이
    바깥으로 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o_ = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o_), 15 + dy * (13 + o_), dx, dy, GRASS)
        lily(f, 15.5, 15.5, 9.6, 9.6, notch=60.0)
        s = 0.5 + 0.5 * math.sin(ph)
        o, _ = top(Rig(15.5, 15.8, 0.0, 0.62), spread=s, mood="blink" if k == 3 else "smile")
        f.update(o)
        frames.append(finish(clip(f)))
    return frames


def ns() -> list[dict]:
    """앞모습으로 높이 뛰어올라 두 팔을 들고 긴 뒷다리를 축 늘어뜨렸다가 쪼그려 앉는다 — 위아래 풀잎 화살촉"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        s = 0.5 + 0.5 * math.sin(ph)
        o = 1 if s > 0.65 else 0
        for sg in (-1, 1):
            chevron(f, 15, 15 + sg * (14 + o), 0, sg, GRASS if o else GRASS_D)
        rig = Rig(15.5, 9.6 + 2.4 * (1 - s), 0.0, 0.86)
        paws = ((-5.4 - 2.2 * s, 6.6 - 10.8 * s), (5.4 + 2.2 * s, 6.6 - 10.8 * s))
        b, _ = front(rig, "smile" if s > 0.3 else "blink", paws=paws, legs=s)
        f.update(b)
        frames.append(finish(clip(f)))
    return frames


def leap(head: float) -> list[dict]:
    """위에서 본 개구리가 그 축으로 몸을 쭉 뻗고 뛴다 — 앞으로 모은 앞발과 뒤로 쭉 찬 물갈퀴 뒷발이 양 끝 화살
    노릇. 뒷다리를 찼다 당겼다 하며 양 끝 풀잎 화살촉이 두근댄다. head 는 머리가 향한 쪽(도). 몸 가운데가 판 가운데.
    옆모습으로 뻗으면 납작하고 길어 악어로 읽혀서 위에서 본 모습으로 그린다"""
    frames = []
    t = math.radians(head)
    ux, uy = math.cos(t), math.sin(t)
    dx, dy = round(ux), round(uy)
    diag = dx != 0 and dy != 0
    R = 10 if diag else 13
    k_ = 0.68 if diag else 0.78
    for k, ph in enumerate(phases()):
        f = {}
        s = math.sin(ph)
        o = 1 if s > 0.3 else 0
        for sg in (-1, 1):
            chevron(f, 15 + sg * dx * (R + o), 15 + sg * dy * (R + o), sg * dx, sg * dy, GRASS if o else GRASS_D)
        rig = anchor(head + 90.0, k_, 0.0, 4.6, 15.5, 15.5)
        b, _ = top(rig, kick=0.7 + 0.3 * s, arms=0.0, reach=0.8, mood="blink" if k == 3 else "smile")
        f.update(b)
        frames.append(finish(clip(f)))
    return frames


def we():
    return leap(180.0)


def nwse():
    return leap(225.0)


def nesw():
    return leap(315.0)


def no() -> list[dict]:
    """빨간 금지 표지 안에서 눈을 질끈 감고 턱 밑 울음주머니를 풍선처럼 부풀린 채 도리도리(개굴!)"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sign(f, slash=False)
        pouch = 0.5 + 0.5 * math.sin(2 * ph)
        sway = 0.9 * math.sin(ph)
        o, _ = front(Rig(15.5 + sway, 13.0, 0.0, 0.8), "shut", paws=((-3.4, 7.2), (3.4, 7.2)), pouch=pouch,
                     tilt=0.5 * math.sin(ph))
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
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (STEM, 15),
       "pen": (math.floor(TIP[0]), math.floor(TIP[1])),
       "hand": lambda fr: top_cell(fr, 13), "up": lambda fr: top_cell(fr, 31)}


def check(rid: str, frames: list[dict], hot: tuple) -> None:
    """핫스팟이 장마다 불투명한 칸 위에 있는지"""
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
        if hot == (1, 1) and any(c[3] == 255 and (p[0] < 1 or p[1] < 1) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 혀 끝보다 왼쪽·위로 나온 칸이 있음")


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

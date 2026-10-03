# SPDX-License-Identifier: Apache-2.0
"""먼치킨(munchkincatanim) 구성표 그림 `art/munchkincatanim/*.txt` 를 만든다.
빌드가 부르지 않고 손으로 돌린다 · 빌드 코드 해시와 CI 캐시 키에 안 들어간다.

  python3 gen/munchkincat.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

해달처럼 칸마다 먼치킨이 하는 짓을 따로 그린다(`SCENE`). '냥이 · 애니' 묶음과 머리 비율(반지름 7 · 세모 귀 ·
ㅅ 입 · 볼터치 · 1칸 수염)을 맞추되, 먼치킨은 **아주 짧은 다리**와 **뒷발로 서는 미어캣 자세**로 실루엣을 가른다.
털은 연크림 바탕에 옅은 주황 줄(치즈냥보다 연하고 밝다) · 흰 배와 주둥이 · 분홍 코. 소품의 주인공은 금빛 방울이고,
화살촉 같은 신호색도 방울의 금색이다. 다리가 짧아 몸통 밑으로 발만 빼꼼 보이게 그린다 — 다리를 길게 그리면 치즈냥이 된다.

  arrow   미어캣처럼 뒷발로 선 먼치킨이 짧은 앞발 하나를 귀 옆으로 번쩍 들어 금빛 화살촉 막대를 왼쪽 위로 쳐든다 —
          화살촉 끝이 핫스팟(귀 끝을 찍던 때는 찍는 점이 안 보였다). 다른 앞발은 가슴에 방울을 안고 딸랑, 눈 깜빡,
          바닥에 깐 꼬리 끝이 까딱. 곁들이 칸(busy · help · person · pin)의 작은 냥은 볼 옆에 든 발과 손으로 찍은
          화살촉, 앉은 빵 몸 — 판을 덜 써서 옆 장면에 안 닿게
  busy    작은 화살표 먼치킨 + 오른쪽 아래 동그라미를 따라 데굴데굴 구르는 금빛 방울(지나간 자리에 반짝이가 남는다)
  cross   가는 조준선 가운데 리본에 매달린 방울(핫스팟) — 아래에서 먼치킨이 짧은 앞발 둘을 뻗어 허우적대지만 안 닿는다
  hand    까치발로 서서 짧은 앞발 하나를 왼쪽 위로 쭉 내밀어 톡톡 — 젤리가 보이는 발끝이 핫스팟, 짧은 뒷발이 바들바들
  help    작은 화살표 먼치킨 + 분홍 리본으로 그린 물음표, 점은 딸랑이는 방울
  ibeam   미어캣 서기 — 꼿꼿이 선 가는 몸이 I, 발밑 그림자가 아래 가로획. 고개를 좌우로 두리번. 핫스팟은 배 가운데
  move    옆모습으로 짧은 다리를 뱅글뱅글 돌려 종종종 제자리 달리기 — 뒤에 먼지가 퐁퐁, 네 방향 금빛 화살촉
  we      옆모습으로 방울을 코앞에 굴리며 종종 드리블 — 반 바퀴마다 돌아선다. 양 끝 화살촉
  ns      앉았다가 쭉 일어서 미어캣 — 위아래로 늘었다 줄었다 하며 두리번. 위아래 화살촉
  nwse · nesw  그 대각선 비탈을 짧은 다리로 종종 오르다가 미끄덩 — 몸이 비탈을 따라 눕고 얼굴은 똑바로
  no      빨간 금지 표지 안에서 방울을 두 앞발로 꼭 끌어안고 도리도리(안 줘)
  pen     파란 크레용을 두 앞발로 쥐고 삐뚤빼뚤 낙서 — 크레용 끝(왼쪽 아래)이 핫스팟, 지나간 자리에 파란 줄
  person  작은 화살표 먼치킨 + 방울 낚싯대를 흔들어 주는 사람
  pin     작은 화살표 먼치킨 + 흰 동그라미 속에 금빛 방울이 든 빨간 지도 핀이 통통 튄다
  up      미어캣 서기로 머리 위에 방울을 얹고 짧은 앞발을 양옆으로 벌려 비틀비틀 균형 — 방울 꼭지(맨 위)가 핫스팟
  wait    사람처럼 등을 기대고 짧은 뒷발을 앞으로 쭉 뻗은 소파 자세로 앉아 배 위 방울을 앞발로 톡톡. 가운데가 핫스팟

몸은 부위(타원 · 굵기가 변하는 막대 · 세모)를 고양이 제 좌표 (u 오른쪽, w 아래)에 놓고 화면으로 돌려 찍는다
(`Rig`, `draw` — 치즈냥 생성기와 같은 방식이지만 다른 생성기에 기대지 않게 여기 따로 둔다). 앞모습(`stand_parts`)과
왼쪽을 보는 옆모습(`side_parts`, `Rig(mirror=True)` 면 오른쪽을 본다) 두 벌이다. 비탈 칸은 몸만 비탈 각도로 돌리고
머리는 똑바로 세운 다른 `Rig` 로 그린다 — 기운 얼굴은 칸 위에서 뭉개진다(치즈냥 · 삼색냥과 같은 교훈).
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, disc, finish, hx, ink, inside, phases, raster, solid, write  # noqa: F401

SID = "munchkincatanim"

OUT, EYE = hx("3a2a30ff"), hx("2a1c22ff")                    # 테두리 · 눈 (치즈냥과 같다 — 한 묶음)
FUR, STRIPE, CREAM = hx("f6dcb0ff"), hx("e9a868ff"), hx("fffaf0ff")
PINK, NOSE, HI = hx("f4a0b0ff"), hx("e27d90ff"), hx("ffffffff")
ink(OUT, HI, hx("fbecdcc7"))
BELL, BELL_D, BELL_L, BELL_S = hx("f2c230ff"), hx("c08a1aff"), hx("fff2a8ff"), hx("6e4a10ff")   # 방울 · 그늘 · 빛 · 틈
RIB, RIB_D = hx("ec6f8eff"), hx("b84462ff")                                                   # 리본
GOLD = (hx("e8b020ff"), hx("e8b020b0"), hx("e8b02060"))      # 화살촉 · 반짝이 (짙은 것부터)
CRAY, CRAY_D, PAPER = hx("4a8fd8ff"), hx("2c64a8ff"), hx("f4efe2ff")
SKIN, HAIR, SHIRT, SHIRT_D = hx("f7d7bcff"), hx("6b4a34ff"), hx("7cb87aff"), hx("4f8a4eff")
ROD = hx("8a6a48ff")
SLOPE, SLOPE_D = hx("b9c8a0ff"), hx("8ea076ff")                                               # 비탈 (풀빛)
DUST = (hx("d8ccb8c0"), hx("d8ccb870"))


# ── 그리개: 고양이 제 좌표 (u, w) → 화면 ─────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도) · 배율 k. ang=0 이면 u 가 오른쪽, w 가 아래. ang 만큼 시계 방향으로 돈다.
    mirror 면 u 를 뒤집고 나서 돌린다(옆모습이 오른쪽을 본다)"""

    def __init__(self, ox: float, oy: float, ang: float = 0.0, k: float = 1.0, mirror: bool = False):
        t = math.radians(ang)
        self.ox, self.oy, self.c, self.s, self.k = ox, oy, math.cos(t), math.sin(t), k
        self.m = -1.0 if mirror else 1.0

    def world(self, a: float, b: float) -> tuple:
        a *= self.m
        return self.ox + (a * self.c - b * self.s) * self.k, self.oy + (a * self.s + b * self.c) * self.k

    def local(self, x: float, y: float) -> tuple:
        dx, dy = (x - self.ox) / self.k, (y - self.oy) / self.k
        return (dx * self.c + dy * self.s) * self.m, -dx * self.s + dy * self.c

    def cell(self, a: float, b: float) -> tuple:
        x, y = self.world(a, b)
        return math.floor(x), math.floor(y)


def ell(ca, cb, ra, rb):
    return lambda a, b: ((a - ca) / ra) ** 2 + ((b - cb) / rb) ** 2 <= 1


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


def chain(pts, r0, r1=None):
    r1 = r0 if r1 is None else r1
    n = len(pts) - 1
    return any_of(*[bar(pts[i], pts[i + 1], r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n) for i in range(n)])


def along(pts):
    """꺾은선 위 가장 가까운 점까지의 길이(처음부터) — 꼬리 고리 무늬용"""
    segs, acc = [], 0.0
    for p, q in zip(pts, pts[1:]):
        L = math.hypot(q[0] - p[0], q[1] - p[1]) or 1e-9
        segs.append((p, q, L, acc))
        acc += L

    def at(a, b):
        best = None
        for p, q, L, s0 in segs:
            t = max(0.0, min(1.0, ((a - p[0]) * (q[0] - p[0]) + (b - p[1]) * (q[1] - p[1])) / (L * L)))
            d = math.hypot(a - p[0] - (q[0] - p[0]) * t, b - p[1] - (q[1] - p[1]) * t)
            if best is None or d < best[0]:
                best = (d, s0 + L * t)
        return best[1]
    return at


def tri(*pts):
    pl = list(pts)
    return lambda a, b: inside(pl, a, b)


def any_of(*hs):
    return lambda a, b: any(h(a, b) for h in hs)


def draw(rig: Rig, parts: list) -> tuple[dict, set, dict]:
    """parts: [(이름, 맞음(a, b), 색(a, b) 또는 색, 테두리)] — 앞의 것이 위에 그려진다.
    칸을 4×4 로 찍어 반 넘게 덮이면 칠하고 가장 많이 덮은 부위의 색을 준다. 바깥 테두리와,
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


def dot(f: dict, x: int, y: int, c: tuple) -> None:
    f[x, y] = c


# ── 앞모습 ──────────────────────────────────────────────────────────────────
HC, HR = (0.0, -7.5), 7.0       # 머리 가운데 · 반지름


def head_parts(hc=HC, r=HR, turn=0.0, ear_turn=0.0, name="head") -> list:
    """앞모습 머리: 둥근 볼 · 세모 귀(속 분홍) · 이마에 옅은 주황 줄 셋 · 흰 주둥이. turn 은 얼굴이 옆으로 돈 정도(u)"""
    u0, w0 = hc
    head = any_of(ell(u0, w0 - 0.4, r * 1.0, r * 0.84), ell(u0, w0 + 1.0, r * 1.1, r * 0.64))
    ears, inner = [], []
    for sg in (-1, 1):
        base0, tip, base1 = (u0 + sg * r * 1.0, w0 - r * 0.2), (u0 + sg * r * 0.84 + ear_turn, w0 - r * 1.3), \
            (u0 + sg * r * 0.2, w0 - r * 0.74)
        ears.append(tri(base0, tip, base1))
        cx, cy = (base0[0] + tip[0] + base1[0]) / 3, (base0[1] + tip[1] + base1[1]) / 3 + r * 0.06
        inner.append(tri(*[(cx + (p[0] - cx) * 0.48, cy + (p[1] - cy) * 0.48) for p in (base0, tip, base1)]))
    inner_hit = any_of(*inner)

    def skin(a, b):
        mu = a - u0 - turn
        if (mu / (r * 0.44)) ** 2 + ((b - (w0 + r * 0.34)) / (r * 0.3)) ** 2 <= 1:
            return CREAM
        if b < w0 - r * 0.44 and any(abs(a - (u0 + turn * 0.6 + d * r * 0.25)) < r * 0.075 for d in (-1, 0, 1)):
            return STRIPE
        if abs(mu) > r * 0.86 and abs(b - (w0 + r * 0.1)) < r * 0.08:
            return STRIPE
        return FUR

    def ear_col(a, b):
        return PINK if inner_hit(a, b) else FUR
    return [(name, head, skin, True), (name + "_ear", any_of(*ears), ear_col, False)]


def face(f: dict, rig: Rig, hc=HC, r=HR, mood="open", turn=0.0) -> None:
    """얼굴: 2×2 눈(흰 반짝 1칸, 보는 쪽에) · 분홍 코 · ㅅ 입 · 볼터치. 작게(k·r < 5) 그리면 눈 1×2 · 코 1칸.
    mood: open · blink · happy(^) · squeeze(><) · sulk(감은 눈 치켜올림)"""
    u0, w0 = hc
    small = rig.k * r < 5.0
    for sg in (-1, 1):
        ex, ey = rig.world(u0 + turn + sg * r * 0.42, w0 - r * 0.06)
        if small:
            x0, y0 = math.floor(ex), math.floor(ey - 0.5)
            dot(f, x0, y0 + 1, EYE)
            if mood == "open":
                dot(f, x0, y0, EYE)
            continue
        x0, y0 = round(ex - 1), round(ey - 1)
        if mood == "open":
            for dx in (0, 1):
                for dy in (0, 1):
                    dot(f, x0 + dx, y0 + dy, EYE)
            dot(f, x0 + (1 if turn > 0.5 else 0), y0, HI)
        elif mood == "blink":
            dot(f, x0, y0 + 1, EYE)
            dot(f, x0 + 1, y0 + 1, EYE)
        elif mood == "happy":
            dot(f, x0 - 1 if sg < 0 else x0, y0 + 1, EYE)
            dot(f, x0 if sg < 0 else x0 + 1, y0, EYE)
            dot(f, x0 + 1 if sg < 0 else x0 + 2, y0 + 1, EYE)
        elif mood == "squeeze":
            xa, xb = (x0, x0 + 1) if sg < 0 else (x0 + 1, x0)
            dot(f, xa, y0 - 1, EYE)
            dot(f, xb, y0, EYE)
            dot(f, xa, y0 + 1, EYE)
        elif mood == "sulk":
            dot(f, x0, y0 + (1 if sg > 0 else 0), EYE)
            dot(f, x0 + 1, y0 + (0 if sg > 0 else 1), EYE)
    nx, ny = rig.world(u0 + turn, w0 + r * 0.16)
    if small:
        dot(f, math.floor(nx), math.floor(ny), NOSE)
    else:
        nl, ny = round(nx) - 1, math.floor(ny)
        dot(f, nl, ny, NOSE)
        dot(f, nl + 1, ny, NOSE)
        for p in ((nl - 1, ny + 2), (nl, ny + 1), (nl + 1, ny + 1), (nl + 2, ny + 2)):   # ㅅ 입
            dot(f, *p, OUT)
    for sg in (-1, 1):   # 볼터치
        bx, by = rig.world(u0 + turn + sg * r * 0.66, w0 + r * 0.22)
        dot(f, math.floor(bx), math.floor(by), PINK)
        if not small:
            dot(f, math.floor(bx) + (1 if sg < 0 else -1), math.floor(by), PINK)


def whiskers(f: dict, rig: Rig, hc=HC, r=HR, turn=0.0, n=2, skip=()) -> None:
    """볼 바깥으로 뻗은 1칸 수염 둘씩 — 머리 테두리 밖 칸에만 찍는다(얼굴 안에 그으면 콧수염이 된다)"""
    u0, w0 = hc
    for sg in (-1, 1):
        if sg in skip:
            continue
        for j, dw in enumerate((0.05, 0.3)):
            x0, y0 = rig.world(u0 + turn * 0.4 + sg * r * 1.1, w0 + r * dw)
            for i in range(n + 1):
                x = math.floor(x0 + sg * i)
                y = math.floor(y0 + (i * 0.4 * (j * 2 - 1) if j else 0))
                if (x, y) not in f:
                    f[x, y] = OUT


def tail_part(pts, r0=1.6, r1=1.3, name="tail", lined=False):
    """꼬리 — 옅은 주황 고리 무늬, 끝은 짙게"""
    at = along(pts)
    total = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:]))

    def col(a, b):
        s = at(a, b)
        if s > total - 0.5:
            return STRIPE
        return STRIPE if (s % 2.8) > 1.9 and s > 1.0 else FUR
    return (name, chain(pts, r0, r1), col, lined)


def arm_part(pts, r=1.9, pr=1.8, name="arm", lined=False, paw=(CREAM, True)):
    """앞발 하나 → [발, 팔]. 발은 흰 양말. 팔에 테를 두르면 짧고 가는 팔이 통째로 테가 되어 가슴에 검은 띠가 생긴다 —
    그래서 기본은 발에만 테를 두른다"""
    return [(name + "_paw", ell(*pts[-1], pr, pr * 1.05), paw[0], paw[1]), (name, chain(pts, r, r * 0.92), FUR, lined)]


def torso(c=(0.0, 3.0), ra=5.4, rb=6.0, name="body"):
    """선 몸통 — 흰 배, 옆구리에 옅은 주황 줄"""
    c0, c1 = c

    def col(a, b):
        if ((a - c0) / (ra * 0.52)) ** 2 + ((b - c1 + rb * 0.05) / (rb * 0.8)) ** 2 <= 1:
            return CREAM
        if abs(a - c0) > ra * 0.6 and (b - c1 + 0.3) % 2.6 < 0.95:
            return STRIPE
        return FUR
    return (name, ell(c0, c1, ra, rb), col, False)


def stand_parts(hc=HC, r=HR, turn=0.0, ear_turn=0.0, arms=None, tail_pts=None, body=(0.0, 3.0, 5.4, 6.0),
                foot_w=9.4, tip=0.0, extra=(), front=(), pr=2.0) -> list:
    """뒷발로 선 먼치킨(미어캣 자세): 머리 · 몸통 · 앞발 둘(arms 를 주면 그 자리로, 기본은 가슴 앞에 모은 발) ·
    아주 짧은 뒷발 둘 · 바닥에 깐 꼬리. tip 은 까치발(뒷발 뒤꿈치를 든 정도). extra 는 맨 앞, front 는 앞발 뒤 · 머리 앞"""
    bc0, bc1, bra, brb = body
    paw = (CREAM, True)
    if arms is None:   # 미어캣처럼 가슴 앞에 늘어뜨린 앞발. 흰 배 위에 흰 발 + 테를 두르면 사다리 같은 검은 줄이 된다 —
        # 털빛 발을 테 없이 얹어 흰 배 위 주황 두 줄로 보이게 한다
        arms = [[(-3.0, bc1 - brb * 0.55), (-1.9, bc1 + brb * 0.05)], [(3.0, bc1 - brb * 0.55), (1.9, bc1 + brb * 0.05)]]
        paw = (FUR, False)
    ap = []
    for i, pts in enumerate(arms):
        ap += arm_part(pts, name=f"arm{i}", pr=pr if paw[1] else min(pr, 1.6), paw=paw)
    fy = bc1 + brb * 0.95
    feet = ("feet", any_of(ell(-2.6, fy - tip * 0.5, 1.9, 1.2 + tip * 0.3), ell(2.6, fy - tip * 0.5, 1.9, 1.2 + tip * 0.3)),
            CREAM, True)
    tp = tail_pts or [(bra * 0.6, fy - 0.6), (bra + 2.0, fy + 0.2), (bra + 4.4, fy - 0.6)]
    return list(extra) + ap + list(front) + head_parts(hc, r, turn, ear_turn) + \
        [feet, torso((bc0, bc1), bra, brb), tail_part(tp)]


def stand(rig: Rig, mood="open", turn=0.0, whisk=True, **kw) -> dict:
    hc, r = kw.get("hc", HC), kw.get("r", HR)
    out, _, _ = draw(rig, stand_parts(turn=turn, **kw))
    face(out, rig, hc, r, mood, turn)
    if whisk and rig.k * r >= 5.0:
        whiskers(out, rig, hc, r, turn)
    return out


# ── 옆모습 (왼쪽을 본다 — a 오른쪽이 꼬리 쪽, b 아래) ─────────────────────────────────
def head_side(hc, r, name="head") -> list:
    """옆모습 머리 — 둥근 머리 · 앞으로 나온 흰 주둥이 · 귀 둘(뒤 귀는 조금만) · 이마 줄"""
    u0, w0 = hc
    muzzle = ell(u0 - r * 0.78, w0 + r * 0.3, r * 0.42, r * 0.32)
    chin = ell(u0 - r * 0.46, w0 + r * 0.6, r * 0.48, r * 0.26)
    near = [(u0 - r * 0.02, w0 - r * 0.7), (u0 + r * 0.36, w0 - r * 1.42), (u0 + r * 0.8, w0 - r * 0.46)]
    far = [(u0 - r * 0.72, w0 - r * 0.5), (u0 - r * 0.6, w0 - r * 1.36), (u0 - r * 0.12, w0 - r * 0.8)]
    cx, cy = sum(p[0] for p in near) / 3, sum(p[1] for p in near) / 3 + r * 0.06
    inner = [(cx + (p[0] - cx) * 0.45, cy + (p[1] - cy) * 0.45) for p in near]

    def skin(a, b):
        if muzzle(a, b) or chin(a, b):
            return CREAM
        if b < w0 - r * 0.3 and any(abs(a - (u0 + d * r * 0.26)) < r * 0.08 for d in (0, 1, 2)):
            return STRIPE
        return FUR
    head = any_of(ell(u0, w0, r, r * 0.9), ell(u0 - r * 0.2, w0 + r * 0.28, r * 0.92, r * 0.6), muzzle)
    return [(name, head, skin, True), (name + "_ear", tri(*near), lambda a, b: PINK if inside(inner, a, b) else FUR, False),
            (name + "_ear2", tri(*far), STRIPE, False)]


def face_side(f: dict, rig: Rig, hc, r, mood="open") -> None:
    u0, w0 = hc
    ex, ey = rig.world(u0 - r * 0.42, w0 - r * 0.08)
    x0, y0 = round(ex - 1), round(ey - 1)
    if mood == "open":
        for dx in (0, 1):
            for dy in (0, 1):
                dot(f, x0 + dx, y0 + dy, EYE)
        dot(f, x0 + (1 if rig.m > 0 else 0), y0, HI)
    else:   # happy — ^
        dot(f, x0, y0 + 1, EYE)
        dot(f, x0 + 1, y0, EYE)
        dot(f, x0 + 2, y0 + 1, EYE)
    nx, ny = rig.world(u0 - r * 1.14, w0 + r * 0.14)
    dot(f, math.floor(nx), math.floor(ny), NOSE)
    bx, by = rig.world(u0 - r * 0.12, w0 + r * 0.36)
    dot(f, math.floor(bx), math.floor(by), PINK)


def side_parts(ph: float, run: float = 1.0, hc=(-7.6, -3.4), hr=5.0, tail_pts=None, extra=(), head=True) -> tuple:
    """옆모습 먼치킨: 긴 몸통 · 큰 머리 · 몸통 밑으로 빼꼼 나온 아주 짧은 다리 넷 · 위로 세운 꼬리.
    ph 는 걸음 위상(다리가 둥글게 돈다), run 은 다리 놀림 크기. → (부위들, 머리 가운데, 반지름)"""
    bob = 0.4 * abs(math.sin(ph)) * run
    legs = []
    for name, hx_, off, near in (("legF", -4.6, 0.0, True), ("legH", 4.8, math.pi, True),
                                 ("legF2", -3.2, math.pi, False), ("legH2", 6.2, 0.0, False)):
        q = ph + off
        fx = hx_ - 1.5 * math.sin(q) * run
        fy = 6.0 - 0.9 * max(0.0, math.cos(q)) * run
        legs.append((name, bar((hx_, 2.4 + bob), (fx, fy), 1.7, 1.6), CREAM if near else STRIPE, near))
    body = ell(0.8, 0.8 + bob, 7.8, 3.5)

    def col(a, b):
        if b > 2.2 + bob and a < 5.0:
            return CREAM
        if b < 0.4 + bob and (a + 0.4) % 2.8 < 1.0 and a > -4.0:
            return STRIPE
        return FUR
    tp = tail_pts or [(8.0, -0.4 + bob), (10.2, -2.8), (10.4 + 0.8 * math.sin(ph), -7.4)]
    hcb = (hc[0], hc[1] + bob)
    hp = head_side(hcb, hr) if head else []
    parts = list(extra) + [legs[0], legs[1]] + hp + [("body", body, col, False), legs[2], legs[3], tail_part(tp, 1.4, 1.1)]
    return parts, hcb, hr


def side(rig: Rig, ph: float, mood="open", **kw) -> dict:
    parts, hc, hr = side_parts(ph, **kw)
    out, _, _ = draw(rig, parts)
    face_side(out, rig, hc, hr, mood)
    return out


# ── 소품 ─────────────────────────────────────────────────────────────────────
def bell(f: dict, cx: float, cy: float, r: float, roll: float = 0.0) -> None:
    """금빛 방울: 왼쪽 위 빛 · 오른쪽 아래 그늘 · 가운데 아래 가로 틈(roll 만큼 돈다) · 꼭대기 고리"""
    m = disc(cx, cy, r)
    ca, sa = math.cos(roll), math.sin(roll)

    def col(p):
        dx, dy = p[0] + 0.5 - cx, p[1] + 0.5 - cy
        u, v = dx * ca + dy * sa, -dx * sa + dy * ca
        if r >= 2.4 and abs(v - r * 0.38) < 0.55 and abs(u) < r * 0.75:
            return BELL_S
        if dx + dy < -r * 0.7:
            return BELL_L
        if dx + dy > r * 0.6:
            return BELL_D
        return BELL
    solid(f, m, col, OUT)
    lx, ly = math.floor(cx + sa * r), math.floor(cy - ca * r)   # 고리 — 틈의 반대쪽
    if r >= 2.4:
        f.setdefault((lx, ly - 1), OUT)
    if r >= 3:
        f[math.floor(cx - r * 0.4), math.floor(cy - r * 0.4)] = HI


def bell_part(ca: float, cb: float, r: float, name="bell"):
    """draw 에 넣는 방울 부위(Rig 좌표) — 왼쪽 위 반짝, 아래 반은 짙게, 아래쪽 가로 틈"""
    def col(a, b):
        if (a - ca + 0.38 * r) ** 2 + (b - cb + 0.38 * r) ** 2 < (0.3 * r) ** 2:
            return BELL_L
        if abs(b - cb - 0.5 * r) < 0.17 * r and abs(a - ca) < 0.62 * r:
            return BELL_S
        return BELL_D if b > cb + 0.25 * r else BELL
    return (name, ell(ca, cb, r, r), col, True)


def jingle(f: dict, cx: float, cy: float, r: float, k: int) -> None:
    """딸랑 — 방울 양옆에 짧은 소리 줄이 번갈아 뜬다"""
    if k % 4 >= 2:
        return
    for sg in (-1, 1):
        x = math.floor(cx + sg * (r + 1.6))
        y = math.floor(cy - r * 0.4)
        for p in ((x, y), (x + sg, y - 1)):
            f.setdefault(p, GOLD[0])


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col=GOLD[0]) -> None:
    """(dx, dy) 쪽을 가리키는 꽉 찬 화살촉. 꼭짓점이 (cx, cy)"""
    px, py = -dy, dx
    for i in range(3):
        for s in range(-i, i + 1):
            f[cx - dx * i + px * s, cy - dy * i + py * s] = col


def diag_chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col=GOLD[0]) -> None:
    """대각선 (dx, dy) 쪽 화살촉 — 꼭짓점 (cx, cy) 에서 두 변이 거꾸로 뻗는 세모"""
    for i in range(4):
        for j in range(4 - i):
            f[cx - dx * i, cy - dy * j] = col


def anchor(frames: list[dict], tip: tuple) -> tuple[list[dict], tuple]:
    """tip 칸(막대 끝)을 (1, 1) 로 옮긴다 → (장들, (1, 1)). 그보다 왼쪽 · 위로 나온 불투명 칸은 check 가 잡는다"""
    dx, dy = 1 - tip[0], 1 - tip[1]
    return [{(x + dx, y + dy): c for (x, y), c in f.items()} for f in frames], (1, 1)


# ── 화살표 먼치킨 ────────────────────────────────────────────────────────────
LOOK = [0, 0, -1.6, -2.0, -2.0, -1.6, 0, 0, 1.6, 2.0, 2.0, 1.6]   # 두리번 — 얼굴이 돈 정도(u)
WAND_TIP, WAND_GRIP = (-18.0, -20.8), (-11.4, -13.8)   # 화살촉 막대 끝 · 쥔 발 (고양이 좌표)
SMALL_GRIP = (-7.8, -11.6)   # 작은 것의 든 발 — 볼 옆에 붙여 판을 덜 쓴다(높이 들수록 고양이가 아래로 밀린다)
# 작은 것의 화살촉 — 칸을 손으로 찍는다. 배율 0.54 로 세모를 그리면 3칸이 다 테가 되어 금빛이 안 남는다
# (s 짙은 금빛 테 · g 금빛 · l 빛). 왼쪽 위 꼭짓점이 핫스팟
SMALL_HEAD = ["sssss", "slgg.", "sgg..", "sg...", "s...."]


def arrow_cat(k: int, ph: float, scale: float) -> tuple[dict, tuple]:
    """미어캣처럼 선 먼치킨이 짧은 앞발 하나를 귀 옆으로 번쩍 들어 금빛 화살촉 막대를 왼쪽 위로 쳐든다 — 화살촉 끝
    한 칸이 핫스팟. 귀 끝을 찍던 때는 무엇이 찍는 점인지 안 보였다. 화살촉은 45° 로 둔다 — 비탈을 세우면 화살촉 날개
    한쪽이 끝보다 왼쪽으로 나온다. 든 팔은 머리 뒤로 지나가게 해서 발만 머리 옆에 보인다(머리 앞으로 그으면 볼과 귀가
    팔 털빛에 묻힌다). 다른 앞발은 가슴에 금빛 방울을 꼭 안고, 방울이 딸랑 · 눈 깜빡 · 꼬리 살랑만 움직인다 — 막대와
    든 발은 장마다 그 자리라 핫스팟 칸이 안 움직인다. → (장, 끝 칸)"""
    rig = Rig(16.0, 18.0, 0.0, scale)
    small = scale < 0.7
    tw = 0.8 * math.sin(2 * ph)
    fy = 3.0 + 6.0 * 0.95
    tail = [(3.2, fy - 0.6), (7.4, fy + 0.2), (9.8, fy - 0.8 - max(0.0, tw))]
    if small:   # 귀 옆에 든 발 하나 + 손으로 찍은 화살촉. 팔은 머리 뒤라 안 보이므로 안 그린다
        paw = ("paw", ell(*SMALL_GRIP, 2.8, 2.8), CREAM, True)
        # 화살촉을 든 만큼 판을 더 쓰므로 몸을 짧게(앉은 빵 자세), 꼬리는 왼쪽(화살촉 밑 빈자리)으로 세운다 — 미어캣 키
        # 그대로거나 꼬리를 오른쪽 바닥에 깔면 옆 장면(낚싯대 끝 방울 · 방울 길)에 닿는다
        body = (0.0, 1.8, 5.0, 4.6)
        fy = body[1] + body[3] * 0.95
        tail = [(-3.0, fy - 0.6), (-5.6, fy - 0.6), (-6.6 - 0.5 * tw, fy - 3.6)]
        out, _, _ = draw(rig, [paw] + stand_parts(turn=-0.8, tail_pts=tail, arms=[], body=body))
        face(out, rig, mood="blink" if k == 6 else "open", turn=-0.8)
        for sg in (-1, 1):   # 귀 속 분홍 한 칸 — 이 배율에선 귀 세모가 다 테가 되어 검은 뿔로 읽힌다
            q = rig.cell(sg * 4.6, -12.0)
            if out.get(q) == OUT:
                out[q] = PINK
        px, py = rig.cell(*SMALL_GRIP)
        tip = (px - 4, py - 4)
        for j, row in enumerate(SMALL_HEAD):
            for i, ch in enumerate(row):
                if ch != ".":
                    out[tip[0] + i, tip[1] + j] = {"s": BELL_S, "g": BELL, "l": BELL_L}[ch]
        return out, tip
    tx, ty = WAND_TIP
    ux, uy = WAND_GRIP[0] - tx, WAND_GRIP[1] - ty
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    hl, hw = 7.0, 3.9                                  # 화살촉 길이 · 날개 반폭
    bx_, by_ = tx + ux * hl, ty + uy * hl
    head_ = ("arrowhead", tri((tx, ty), (bx_ - uy * hw, by_ + ux * hw), (bx_ + uy * hw, by_ - ux * hw)),
             lambda a, b: BELL_L if (a - tx) * ux + (b - ty) * uy < hl * 0.45 else BELL, True)
    shaft = ("shaft", bar((bx_ - ux * 0.6, by_ - uy * 0.6), WAND_GRIP, 1.25), ROD, True)
    paw = ("paw", ell(*WAND_GRIP, 2.2, 2.3), CREAM, True)
    arm = ("raise", chain([(-3.8, -0.8), (-7.6, -5.6), WAND_GRIP], 1.9, 1.8), FUR, False)
    sw = math.sin(2 * ph)
    parts = stand_parts(turn=-0.8, tail_pts=tail, arms=[[(3.6, -0.4), (1.6 + 0.3 * sw, 2.2)]],
                        extra=[paw, head_, shaft], pr=2.0, front=[bell_part(-0.2, 3.4, 3.4)])
    i = next(j for j, p in enumerate(parts) if p[0] == "head_ear") + 1
    parts.insert(i, arm)   # 든 팔은 머리 뒤
    out, _, region = draw(rig, parts)
    for p, r in region.items():   # 화살촉 테는 짙은 금빛 — 검은 테면 금빛 속이 + 자로 남아 반짝이로 읽힌다
        if r == "arrowhead" and out[p] == OUT:
            out[p] = BELL_S
    face(out, rig, mood="blink" if k == 6 else "open", turn=-0.8)
    whiskers(out, rig, turn=-0.8, skip=(-1,))
    x0, y0 = rig.world(-0.2, 3.4)
    jingle(out, x0, y0, 3.4 * scale, k)
    return out, rig.cell(tx + ux * 0.3, ty + uy * 0.3)


SMALL = 0.54   # 곁들이 칸 고양이 배율 — 화살촉을 든 만큼 판을 더 써서 귀 끝을 찍던 때(0.6)보다 줄였다


def arrow_frames(small=False) -> tuple[list[dict], tuple]:
    got = [arrow_cat(k, ph, SMALL if small else 0.86) for k, ph in enumerate(phases())]
    f0 = got[0][0]
    # 막대 끝 칸 — 끝 좌표에서 가장 가까운 불투명 칸(가늘게 깎은 끝은 반 넘게 덮이지 않아 빌 수 있다)
    tx, ty = got[0][1]
    tip = min((p for p, c in f0.items() if c[3] == 255), key=lambda p: (p[0] + p[1], abs(p[0] - tx) + abs(p[1] - ty)))
    return anchor([f for f, _ in got], tip)


def arrow():
    frames, hot = arrow_frames()
    return [finish(f) for f in frames], hot


def companion(scene):
    """작은 화살표 먼치킨 + scene(k, ph) 이 그리는 소품 — busy · help · person · pin"""
    cats, hot = arrow_frames(small=True)
    frames = []
    for k, ph in enumerate(phases()):
        f = scene(k, ph)
        f.update(cats[k])
        frames.append(finish(f))
    return frames, hot


# ── 장면 ─────────────────────────────────────────────────────────────────────
def busy():
    """동그라미 길을 따라 구르는 방울 — 지나간 자리에 반짝이가 옅어지며 남는다"""
    cx, cy, R = 21.5, 21.5, 6.2

    def scene(k, ph):
        f = {}
        for j in range(1, 5):   # 반짝이 꼬리
            a = ph - j * 0.5 - math.pi / 2
            x, y = math.floor(cx + R * math.cos(a)), math.floor(cy + R * math.sin(a))
            f[x, y] = GOLD[0] if j == 1 else GOLD[1] if j < 4 else GOLD[2]
        a = ph - math.pi / 2
        bell(f, cx + R * math.cos(a), cy + R * math.sin(a), 3.2, roll=ph * 2)
        return f
    return companion(scene)


def help_():
    """분홍 리본으로 그린 물음표 — 점 자리 방울이 좌우로 딸랑"""
    def scene(k, ph):
        f = {}
        pts = [(16.8, 11.4), (17.4, 8.8), (20.4, 7.6), (23.4, 8.8), (24.0, 11.8), (21.4, 14.4), (20.4, 16.6), (20.4, 19.4)]
        o, _, _ = draw(Rig(0, 0, 0, 1.0), [("rib", chain(pts, 1.25), lambda a, b: RIB_D if b > 16 else RIB, False)])
        f.update(o)
        sw = 0.9 * math.sin(ph)
        bell(f, 20.9 + sw, 25.0, 2.8, roll=-sw * 0.3)
        jingle(f, 20.9 + sw, 25.0, 2.8, k)
        return f
    return companion(scene)


def person():
    """사람이 방울 낚싯대를 흔들어 준다 — 막대 끝 줄에 매달린 방울이 대롱대롱"""
    def scene(k, ph):
        f = {}
        rig = Rig(24.0, 25.0, 0.0, 0.62)
        sw = math.sin(ph)
        hand = (-7.4, -6.4 + 1.2 * sw)
        parts = [("hand", ell(*hand, 1.8, 1.8), SKIN, True), ("sleeve", bar((-4.6, -0.2), hand, 1.7), SHIRT, False),
                 ("hair", any_of(ell(0.0, -10.2, 5.4, 3.6), ell(0, -8.8, 5.6, 2.8)), HAIR, True),
                 ("face", ell(0.0, -7.6, 4.8, 4.8), SKIN, True),
                 ("torso", ell(0, 3.0, 7.6, 6.4), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
        out, _, _ = draw(rig, parts)
        for sg in (-1, 1):
            ex, ey = rig.cell(sg * 2.0, -7.2)
            out[ex, ey] = EYE
            out[ex, ey + 1] = EYE
            out[rig.cell(sg * 3.0, -5.0)] = PINK
        hx_, hy_ = rig.world(*hand)
        tip = (hx_ - 6.0, hy_ - 4.0 - sw)
        rod = {}
        from sea import line
        line(rod, (hx_ - 0.5, hy_), tip, ROD)
        bx, by = tip[0] - 1.0 * sw, tip[1] + 5.4
        line(rod, tip, (bx, by - 2.6), OUT)
        f.update(rod)
        f.update({p: c for p, c in out.items() if p[1] <= 30})
        bell(f, bx, by, 2.6, roll=-0.4 * sw)
        jingle(f, bx, by, 2.6, k)
        return f
    return companion(scene)


def pin():
    """빨간 지도 핀 속 흰 동그라미에 금빛 방울 — 핀이 통통 튄다"""
    def scene(k, ph):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 15.0 + dy
        for x in range(19, 27):
            f.setdefault((x, 28), GOLD[2] if dy else GOLD[1])
        pinm = disc(cx, cy, 6.2) | raster([(cx - 4.4, cy + 3.4), (cx + 4.4, cy + 3.4), (cx, cy + 12.4)])
        solid(f, pinm, SIGN, SIGN_D)
        solid(f, disc(cx, cy, 3.9), CREAM, SIGN_D)
        bell(f, cx, cy + 0.3, 2.6, roll=0.25 * math.sin(2 * ph))
        return f
    return companion(scene)


def cross():
    """가는 조준선 가운데 리본에 매달린 방울(핫스팟) — 아래에서 먼치킨이 짧은 앞발 둘을 번갈아 뻗어 허우적대지만
    짧아서 안 닿는다. 리본이 위 세로선, 고양이가 아래 세로선 자리다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for x in list(range(1, 7)) + list(range(25, 31)):
            f[x, 15] = OUT
        sw = round(0.6 * math.sin(ph))
        for y in range(1, 11):
            f[15, y] = RIB
        rig = Rig(15.5, 27.4, 0.0, 0.6)
        hc = (0.0, 0.0)
        arms = []
        for i, sg in enumerate((-1, 1)):
            lift = 1.6 * max(0.0, math.sin(ph + i * math.pi))
            arms += arm_part([(sg * 7.6, 5.0), (sg * 9.4, -2.0), (sg * 8.6 + sg * 0.8 * math.cos(2 * ph), -6.6 - lift)],
                             r=2.0, pr=2.2, name=f"arm{i}")
        parts = arms + head_parts(hc, 7.0) + [("chest", ell(0, 6.4, 6.4, 4.0), lambda a, b: CREAM if abs(a) < 2.6 else FUR,
                                                False)]
        out, _, _ = draw(rig, parts)
        face(out, rig, hc, 7.0, "squeeze" if k % 6 in (2, 3) else "open")
        f.update({p: c for p, c in out.items() if p[1] <= 30})
        bell(f, 15.5 + sw * 0.5, 14.5, 3.6, roll=0.15 * sw)
        frames.append(finish(f))
    return frames, (15, 15)


def hand():
    """까치발로 서서 짧은 앞발 하나를 왼쪽 위로 쭉 내밀어 톡톡 — 누를 때 발바닥 젤리가 벌어지고 몸이 앞으로 기운다.
    발은 그 자리에 두고 몸만 바들바들 떨게 해서 핫스팟(발끝)이 장마다 같은 칸이다"""
    frames = []
    rig = Rig(18.6, 18.0, 0.0, 0.84)
    pc, pr = (-10.6, -10.8), 2.6
    hot = None
    for k, ph in enumerate(phases()):
        press = k % 6 in (2, 3)
        jit = 0.35 * (1 if k % 2 else -1)
        hc = (HC[0] - 0.6 + jit, HC[1] + (0.3 if press else 0.0))
        pad = ("pad", ell(pc[0], pc[1], pr, pr), CREAM, True)
        arm = ("reach", chain([(-3.6, -0.4), (-7.4, -6.0), pc], 1.9, 2.2), FUR, False)
        parts = [pad] + head_parts(hc) + [arm] + \
            stand_parts(hc=hc, arms=[[(3.4, -0.2), (1.8, 1.8)]], tip=1.6, body=(jit * 0.5, 3.0, 5.4, 6.0))[2:]
        out, mask, region = draw(rig, parts)
        x0, y0 = rig.cell(pc[0] + 0.3, pc[1] + 0.3)
        for p in ((x0 - 1, y0), (x0, y0), (x0 + 1, y0), (x0, y0 + 1)) + \
                (((x0 - 1, y0 - 2), (x0 + 1, y0 - 2), (x0 + 2, y0 - 1), (x0 - 2, y0 - 1)) if press else
                 ((x0 - 1, y0 - 2), (x0 + 1, y0 - 2), (x0 + 2, y0 - 1))):
            if region.get(p) == "pad" and out[p] != OUT:
                out[p] = PINK
        face(out, rig, hc, mood="squeeze" if press else "open", turn=-0.6)
        whiskers(out, rig, hc, turn=-0.6, skip=(-1,))
        if press:   # 톡 — 발끝 둘레 눌림 줄
            tx, ty = rig.cell(pc[0] - pr, pc[1] - pr)
            for p in ((tx - 1, ty + 3), (tx - 2, ty + 4), (tx + 3, ty - 1), (tx + 4, ty - 2)):
                if 0 <= p[0] <= 31 and 0 <= p[1] <= 31:
                    out.setdefault(p, OUT)
        for sg in (-1, 1):   # 바들바들 — 발 양옆 떨림 줄
            fx, fy = rig.cell(sg * 5.6, 9.0)
            if k % 2:
                out.setdefault((fx, fy), OUT)
                out.setdefault((fx + sg, fy - 1), OUT)
        if hot is None:
            hot = min((p for p in mask if region[p] == "pad"), key=lambda p: (p[0] + p[1], p[1]))
        frames.append(finish(out))
    return frames, hot


def ibeam():
    """미어캣 서기 — 꼿꼿이 선 가는 몸이 I 의 세로획, 발밑 그림자가 아래 가로획. 고개를 좌우로 두리번"""
    frames = []
    rig = Rig(16.0, 18.4, 0.0, 0.72)
    for k, ph in enumerate(phases()):
        f = {}
        for x in range(10, 22):
            f[x, 27] = GOLD[2] if x in (10, 21) else GOLD[1]
        turn = LOOK[k] * 1.1
        f.update(stand(rig, "blink" if k == 7 else "open", turn, False, ear_turn=turn * 0.25, body=(0.0, 3.4, 4.4, 6.4),
                       tail_pts=[(3.0, 9.2), (5.4, 11.2), (8.4, 11.0)]))
        frames.append(finish(f))
    return frames, (15, 17)


def move():
    """옆모습 종종종 제자리 달리기 — 짧은 다리가 뱅글뱅글 돌고 꽁무니에 먼지가 퐁퐁. 네 방향 금빛 화살촉"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy, GOLD[0] if o else GOLD[1])
        q = 2 * ph   # 한 바퀴에 두 걸음
        for j in range(3):   # 먼지 — 뒤로 밀려나며 옅어진다
            t = ((k + j * 4) % N) / N
            f[math.floor(22.0 + 5.0 * t), math.floor(21.0 - 2.0 * math.sin(math.pi * t))] = DUST[0] if t < 0.5 else DUST[1]
        f.update(side(Rig(16.0, 15.4, 0.0, 0.8), q))
        frames.append(finish(f))
    return frames, (15, 15)


def we():
    """방울을 코앞에 굴리며 옆으로 종종 드리블 — 반 바퀴는 왼쪽, 반 바퀴는 돌아서 오른쪽. 양 끝 화살촉"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        left = k < 6
        o = 1 if k % 3 == 0 else 0
        chevron(f, 15 - 14 - o + 1, 15, -1, 0, GOLD[0] if left else GOLD[1])
        chevron(f, 15 + 14 + o, 15, 1, 0, GOLD[1] if left else GOLD[0])
        rig = Rig(16.6 if left else 14.4, 15.0, 0.0, 0.72, mirror=not left)
        f.update(side(rig, 2 * ph))
        bx, _ = rig.world(-14.2 - 0.6 * math.sin(2 * ph), 0)
        bell(f, bx, 18.4, 2.6, roll=(-1 if left else 1) * ph * 2)
        frames.append(finish(f))
    return frames, (15, 15)


def ns():
    """앉았다가 쭉 일어서 미어캣 — 일어선 동안 두리번. 위아래 화살촉이 늘 때 바깥으로"""
    frames = []
    #   장:   0  1    2    3    4  5  6  7  8    9    10  11
    S = [0, 0.3, 0.7, 1, 1, 1, 1, 1, 1, 0.7, 0.3, 0]
    look = [0, 0, 0, -1.6, -2.0, -1.6, 0, 1.6, 2.0, 1.6, 0, 0]
    for k, ph in enumerate(phases()):
        f = {}
        s = S[k]
        o = 1 if s > 0.6 else 0
        chevron(f, 15, 2 - o, 0, -1, GOLD[0] if o else GOLD[1])
        chevron(f, 15, 28 + o, 0, 1, GOLD[0] if o else GOLD[1])
        rig = Rig(16.0, 16.6, 0.0, 0.78)
        hc = (0.0, -6.4 - 2.6 * s)
        bc1, brb = 3.4 - 1.0 * s, 4.6 + 1.6 * s
        # 앉은 장은 앞발을 두 뒷발 사이 바닥에 짚는다 — 팔을 길게 내리면 가는 팔이 테만 남아 세로 검은 줄이 된다
        arms = None if s > 0.5 else [[(-2.2, bc1 + 1.0), (-1.5, bc1 + brb * 0.78)], [(2.2, bc1 + 1.0), (1.5, bc1 + brb * 0.78)]]
        fy = bc1 + brb * 0.95
        f.update(stand(rig, "open", look[k], hc=hc, body=(0.0, bc1, 5.6 - 0.6 * s, brb), arms=arms, pr=2.3,
                       tail_pts=[(3.0, fy - 0.6), (6.4, fy + 0.2), (9.0, fy - 1.0)]))
        frames.append(finish(f))
    return frames, (15, 15)


def slope(ang: float, mirror: bool):
    """비탈 오르기 — 몸은 비탈 각도로 눕히고 다리는 종종, 머리는 똑바로 세운 Rig 로 몸 앞에 붙인다.
    장 8–10 에 미끄덩 비탈을 따라 한 칸 내려갔다가 다시 오른다"""
    frames = []
    t = math.radians(ang)
    up_x, up_y = (math.cos(t) * (1 if mirror else -1), math.sin(t) * (1 if not mirror else -1))
    # 비탈 위쪽(머리 쪽) 화면 방향
    hx_, hy_ = Rig(0, 0, ang, 1.0, mirror).world(-1.0, 0.0)
    dx, dy = (1 if hx_ > 0 else -1), (1 if hy_ > 0 else -1)
    slip = [0, 0, 0, 0, 0, 0, 0, 0, 1.4, 2.4, 1.2, 0]
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0
        diag_chevron(f, 15 + dx * (13 + o) + (1 if dx > 0 else 0) - (1 if dx > 0 else 0), 15 + dy * (13 + o), dx, dy)
        diag_chevron(f, 15 - dx * (13 + o), 15 - dy * (13 + o), -dx, -dy)
        sl = slip[k]
        cx, cy = 15.6 - hx_ * sl, 15.6 - hy_ * sl
        rig = Rig(cx, cy, ang, 0.74, mirror)
        # 비탈 — 몸 밑으로 언덕 한 자락(판처럼 얇은 줄이면 썰매 · 스노보드로 읽힌다). 비탈은 미끄러져도 제자리다
        g = Rig(15.6, 15.6, ang, 0.74, mirror)
        for y in range(3, 29):
            for x in range(3, 29):
                a, b = g.local(x + 0.5, y + 0.5)
                if b >= 6.0:
                    f[x, y] = SLOPE if b < 7.4 else SLOPE_D if b < 8.8 else hx("b9c8a090") if b < 12 else hx("b9c8a048")
        run = 0.4 if sl else 1.0
        parts, hc, hr = side_parts(2 * ph, run, head=False)
        body, _, _ = draw(rig, parts)
        f.update(body)
        hxw, hyw = rig.world(hc[0] + 0.6, hc[1] + 0.8)
        hrig = Rig(hxw, hyw, 0.0, 0.74, mirror)
        hd, _, _ = draw(hrig, head_side((0.0, 0.0), hr))
        f.update(hd)
        face_side(f, hrig, (0.0, 0.0), hr, "happy" if sl else "open")
        if sl > 2:   # 미끄덩 — 땀방울
            sx, sy = hrig.cell(hr * 0.9, -hr * 0.9)
            f[sx, sy] = hx("9fd0f0ff")
            f[sx, sy + 1] = hx("9fd0f0ff")
        frames.append(finish(f))
    return frames, (15, 15)


def nwse():
    return slope(45.0, False)


def nesw():
    return slope(-45.0, True)


def sign(f: dict, R: float = 13.5) -> None:
    """빨간 금지 표지(고리 + 왼쪽 위 → 오른쪽 아래 빗금)"""
    ring = {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
    slash = set()
    for t in range(-90, 91):
        x, y = 15.5 + t / 100 * (R - 1.5) * 0.7071, 15.5 + t / 100 * (R - 1.5) * 0.7071
        slash |= disc(x, y, 1.3)
    solid(f, ring | slash, SIGN, SIGN_D)


def no():
    """금지 표지 안에서 방울을 두 앞발로 꼭 끌어안고 도리도리(안 줘) — 얼굴이 좌우로 홱홱, 그때 움직임 줄"""
    frames = []
    rig = Rig(16.0, 17.0, 0.0, 0.76)
    turns = [-2.2, -2.2, -1.2, 1.2, 2.2, 2.2, 2.2, 2.2, 1.2, -1.2, -2.2, -2.2]
    for k, ph in enumerate(phases()):
        f = {}
        sign(f)
        turn = turns[k]
        hc = (0.0, -7.2)
        # 방울을 몸과 같은 판(부위)으로 그려 앞발이 그 위를 덮게 한다 — 따로 찍어 덮으면 팔 테가 몸통에 검게 남는다
        arms = [[(-4.6, -0.4), (-4.0, 3.4)], [(4.6, -0.4), (4.0, 2.6)]]
        out = stand(rig, "sulk", turn, hc=hc, arms=arms, ear_turn=turn * 0.3, body=(0.0, 3.2, 5.6, 6.0),
                    front=[bell_part(0.0, 3.4, 4.6)], pr=1.7)
        f.update({p: c for p, c in out.items() if 1 <= p[1] <= 30})
        if k in (2, 3, 8, 9):   # 홱 — 움직임 줄
            sg = 1 if k in (2, 3) else -1
            x0 = 7 if sg > 0 else 24
            for y in (7, 9):
                f[x0, y] = OUT
                f[x0 - sg, y] = OUT
        frames.append(finish(f))
    return frames, (15, 15)


TIP = (1.5, 29.5)   # 크레용 끝(화면)


def pen():
    """두 짧은 앞발로 파란 크레용을 꼭 쥐고 삐뚤빼뚤 낙서 — 크레용 끝이 핫스팟, 오른쪽으로 파란 지그재그가 자란다.
    크레용은 굵고 짧다(종이 띠 · 짙은 줄 둘) — 연필 · 붓 · 깃펜은 다른 냥이가 썼다"""
    frames = []
    BACK = (17.0, 16.0)
    L = math.hypot(BACK[0] - TIP[0], BACK[1] - TIP[1])
    ux, uy = (BACK[0] - TIP[0]) / L, (BACK[1] - TIP[1]) / L
    base = Rig(22.0, 15.6, 0.0, 0.6)
    cone = (TIP[0] + ux * 3.4, TIP[1] + uy * 3.4)
    lt, lc, lb = base.local(*TIP), base.local(*cone), base.local(*BACK)
    rr = 2.0 / base.k

    def ccol(a, b):
        x, y = base.world(a, b)
        tt = (x - TIP[0]) * ux + (y - TIP[1]) * uy
        if tt < 3.6:
            return CRAY_D if tt < 1.2 else CRAY
        if 6.0 < tt < L - 3.0:
            return CRAY_D if abs(tt - 8.0) < 0.6 or abs(tt - (L - 5.0)) < 0.6 else PAPER
        return CRAY
    crayon = ("crayon", any_of(bar(lt, lc, 0.5 / base.k, rr), bar(lc, lb, rr)), ccol, True)
    g1 = base.local(TIP[0] + ux * L * 0.62, TIP[1] + uy * L * 0.62)
    g2 = base.local(TIP[0] + ux * L * 0.86, TIP[1] + uy * L * 0.86)
    zig = [(3, 30), (5, 28), (7, 30), (9, 28), (11, 30), (13, 28), (15, 30), (17, 28)]
    for k, ph in enumerate(phases()):
        f = {}
        n = 1 + k * (len(zig) - 1) // (N - 1)
        from sea import line
        for a, b in zip(zig[:n], zig[1:n + 1]):
            line(f, (a[0] + 0.5, a[1] + 0.5), (b[0] + 0.5, b[1] + 0.5), CRAY)
        d = math.radians(3.0 * math.sin(2 * ph))
        ox, oy = base.ox - TIP[0], base.oy - TIP[1]
        rig = Rig(TIP[0] + ox * math.cos(d) - oy * math.sin(d), TIP[1] + ox * math.sin(d) + oy * math.cos(d),
                  math.degrees(d), base.k)
        paws = arm_part([(-3.8, -0.4), (g1[0] + 0.6, g1[1] - 0.6)], r=1.7, pr=2.0, name="armL") + \
            arm_part([(3.8, -0.4), (g2[0] + 0.6, g2[1] - 0.6)], r=1.7, pr=2.0, name="armR")
        pp = [p for p in paws if p[0].endswith("_paw")]
        ab = [p for p in paws if not p[0].endswith("_paw")]
        parts = pp + [crayon] + ab + stand_parts(arms=[], tail_pts=[(3.2, 8.4), (7.4, 9.0), (9.6 + 0.8 * math.sin(ph), 7.6)])
        out, _, _ = draw(rig, parts)
        face(out, rig, mood="happy" if k % 6 in (3, 4) else "open", turn=-0.8)
        whiskers(out, rig, turn=-0.8, skip=(-1,))
        f.update(out)
        f[math.floor(TIP[0]), math.floor(TIP[1])] = CRAY_D
        frames.append(finish(f))
    return frames, (math.floor(TIP[0]), math.floor(TIP[1]))


def up():
    """미어캣 서기로 머리 위에 방울을 얹고 짧은 앞발을 양옆으로 벌려 균형 — 몸이 좌우로 비틀대도 머리와 방울은
    그 자리라서 핫스팟(방울 꼭지)이 장마다 같은 칸이다"""
    frames = []
    rig = Rig(16.0, 19.6, 0.0, 0.7)
    for k, ph in enumerate(phases()):
        f = {}
        sw = math.sin(ph)
        arms = [[(-4.2, -1.0), (-7.4, -3.0 - 1.6 * sw)], [(4.2, -1.0), (7.4, -3.0 + 1.6 * sw)]]
        out = stand(rig, "open" if k % 6 else "blink", 0.0, arms=arms, body=(0.5 * sw, 3.0, 5.4, 6.0),
                    tail_pts=[(3.2, 8.4), (6.6 + 0.6 * sw, 9.2), (9.2, 7.6 - 0.6 * sw)])
        f.update(out)
        bx, by = rig.world(0.0, -18.0)
        bell(f, bx, by, 3.8)   # 굴리면 꼭지 칸이 옮겨 다녀 핫스팟이 비므로 안 굴린다
        if abs(sw) > 0.8:   # 비틀 — 방울 옆 흔들림 줄
            sg = 1 if sw > 0 else -1
            for y in (int(by) - 1, int(by) + 1):
                f.setdefault((math.floor(bx + sg * 6), y), OUT)
        frames.append(finish(f))
    hot = min((p for p, c in frames[0].items() if c[3] == 255 and p[0] in (15, 16)), key=lambda p: p[1])
    return frames, hot


def wait():
    """소파 자세 — 사람처럼 등을 기대고 짧은 뒷발(분홍 젤리가 보이게)을 앞으로 쭉 뻗고 앉아 배 위 방울을 두 앞발로
    번갈아 톡톡. 방울이 통통 튀고 딸랑, 눈은 즐거워 ^^ 와 뜬 눈을 오간다"""
    frames = []
    rig = Rig(16.0, 16.6, 0.0, 0.82)
    for k, ph in enumerate(phases()):
        f = {}
        tapL, tapR = max(0.0, math.sin(2 * ph)), max(0.0, -math.sin(2 * ph))
        hop = 0.9 * abs(math.sin(2 * ph))
        hc = (0.0, -7.0)
        legs = []
        for sg in (-1, 1):
            legs += [(f"leg{sg}_pad", ell(sg * 7.0, 10.0, 2.2, 2.0), CREAM, True),
                     (f"leg{sg}", bar((sg * 3.6, 7.0), (sg * 6.6, 9.6), 2.2), FUR, False)]
        arms = [[(-4.4, -0.6), (-2.6 + 0.4 * tapL, 2.2 - 1.6 * tapL)], [(4.4, -0.6), (2.6 - 0.4 * tapR, 2.2 - 1.6 * tapR)]]
        parts = stand_parts(hc=hc, arms=arms, body=(0.0, 3.6, 6.4, 5.6),
                            tail_pts=[(-5.6, 7.8), (-9.4, 8.6), (-11.0, 6.8 + 0.6 * math.sin(ph))])
        parts = [p for p in parts if p[0] != "feet"]
        parts = parts[:4] + legs + parts[4:]
        out, _, _ = draw(rig, parts)
        for sg in (-1, 1):   # 발바닥 젤리
            px, py = rig.cell(sg * 7.0, 10.2)
            for p in ((px, py), (px - 1, py), (px - 1, py - 2) if sg < 0 else (px, py - 2), (px + 1 if sg < 0 else px - 2, py - 2)):
                if out.get(p) == CREAM:
                    out[p] = PINK
        face(out, rig, hc, mood="happy" if k % 6 in (1, 2) else "open")
        whiskers(out, rig, hc)
        f.update(out)
        bx, by = rig.world(0.0, 3.0 - hop * 1.6)
        bell(f, bx, by, 2.6, roll=0.3 * math.sin(2 * ph))
        jingle(f, bx, by, 2.6, k)
        frames.append(finish(f))
    return frames, (16, 16)


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def check(rid: str, frames: list[dict], hot: tuple) -> None:
    """핫스팟이 장마다 불투명한 칸 위에 있는지 · 판(0–31) 안인지"""
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
        if any(not (0 <= x <= 31 and 0 <= y <= 31) for x, y in f):
            print(f"  ! {rid} {i}장: 판 밖으로 나간 칸이 있음")
        if rid in ("arrow", "busy", "help", "person", "pin") and \
                any(c[3] == 255 and (p[0] < 1 or p[1] < hot[1]) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 귀 끝보다 위로(또는 판 왼쪽 밖으로) 나온 칸이 있음")


def main() -> None:
    def job(r):
        def run():
            frames, hot = SCENE[r]()
            check(r, frames, hot)
            print(f"  {r} 핫스팟 {hot}")
            return frames, hot
        return run
    write(SID, {r: job(r) for r in SCENE}, sys.argv[1:] or None)


if __name__ == "__main__":
    main()

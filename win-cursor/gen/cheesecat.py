# SPDX-License-Identifier: Apache-2.0
"""치즈냥(cheesecatanim) 구성표 그림 `art/cheesecatanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/cheesecat.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

해달처럼 칸마다 치즈냥이 하는 짓을 따로 그린다(`SCENE`). 둥글고 통통한 뚱냥 — 옆으로 퍼진 큰 머리 · 세모 귀(속은 분홍) ·
이마에 짙은 주황 줄 셋 · 흰 주둥이와 배 · 분홍 코와 ㅅ 입 · 1칸 수염 · 짧고 굵은 줄무늬 꼬리 · 흰 양말 발.
색은 같은 저장소 `cat-follower/art/*.txt` 의 치즈 고양이(주황 e89a4a · 짙은 주황 c26f34 · 흰 fff6e8 · 분홍 f4a0b0)를 따른다.
해양 애니의 물낯 자리는 집 소품(방석 · 털실 공 · 생선 · 발바닥 젤리)이 대신한다.

  arrow   통통하게 앉은 치즈냥이 몸을 왼쪽 위로 기울여 앞발 하나를 머리 위로 쭉 뻗는다 — 그 발끝이 핫스팟.
          꼬리가 살랑이고 아래 앞발이 꾹꾹이를 한다
  busy    작은 화살표 치즈냥 + 오른쪽 아래 생선 둘레를 도는 분홍 젤리 발자국 여덟 개
  cross   앞모습 얼굴. 긴 수염 한 가닥씩이 가로 조준선, 머리 위로 늘어진 장난감 줄과 턱 밑 줄이 세로선. 코가 핫스팟
  hand    분홍 젤리 발바닥을 보이며 앞발로 꾹 누른다 — 누를 때 눈을 질끈(><) 감는다. 발바닥 꼭대기가 핫스팟
  help    작은 화살표 치즈냥 + 줄무늬 꼬리를 말아 만든 물음표(점은 털실 공)
  ibeam   등을 보이고 앉아 꼬리를 곧게 세운 치즈냥 — 꼬리가 I, 꼬리 끝이 까딱인다. 핫스팟은 꼬리 가운데
  move    배를 깔고 동그랗게 만 치즈냥이 데굴데굴 한 바퀴 — 네 방향 분홍 화살촉
  nesw · ns · nwse · we   앞발은 위로, 뒷발은 아래로 쭉 늘인 기지개(눈은 질끈) — 그 축으로 늘었다 줄었다 하고
          양 끝 화살촉이 두근댄다. we 는 옆으로 누워 하는 기지개다
  no      빨간 금지 표지 안에서 팔짱 끼고 고개를 홱 돌린 치즈냥(삐짐) — 왼쪽 오른쪽으로 홱홱
  pen     앞발로 연필을 꼭 쥐고 쓰는 치즈냥 — 연필심(왼쪽 아래)이 핫스팟
  person  작은 화살표 치즈냥 + 고양이 귀 후드를 쓴 사람이 손을 흔든다
  pin     작은 화살표 치즈냥 + 동그라미 속에 치즈냥 얼굴(귀가 핀 위로 솟음)이 든 빨간 지도 핀이 통통 튄다
  up      두 앞발을 머리 위로 모아 만세 — 츄르 달라고 뒷발로 서서 들썩인다. 모은 발끝(맨 위)이 핫스팟
  wait    방석 위 식빵 자세(앞발을 숨김)로 꾸벅꾸벅 존다 — 고개가 떨어지며 눈이 감기다가 화들짝 뜬다. 가운데가 핫스팟

몸은 부위(타원 · 굵기가 변하는 막대 · 세모)를 고양이 제 좌표 (u 오른쪽, w 아래)에 놓고 화면으로 돌려 찍는다
(`Rig`, `draw` — 해달 생성기와 같은 방식이지만 다른 생성기에 기대지 않게 여기 따로 둔다).
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, disc, finish, hx, ink, inside, phases, solid, write

SID = "cheesecatanim"

OUT, EYE = hx("3a2a30ff"), hx("2a1c22ff")                    # 테두리 · 눈 (cat-follower 의 # 색)
FUR, STRIPE, CREAM = hx("e89a4aff"), hx("c26f34ff"), hx("fff6e8ff")
PINK, NOSE, HI = hx("f4a0b0ff"), hx("e27d90ff"), hx("ffffffff")   # 볼터치 · 젤리 · 귀 속 / 코 / 반짝
ink(OUT, HI, hx("fbecdcc7"))
CUSH, CUSH_D, CUSH_L = hx("7fa3d4ff"), hx("587ab0ff"), hx("a9c4e8ff")   # 방석 (주황 몸과 갈리게 파랑)
YARN, YARN_D = hx("f07c9cff"), hx("c4567aff")                          # 털실 공
FISH, FISH_D = hx("9cb6ccff"), hx("6a879fff")                          # 생선
PENCIL, PENCIL_D, WOOD, LEAD = hx("f5c842ff"), hx("c8961cff"), hx("efd2a8ff"), hx("3a3a3aff")
ERASER, FERRULE = hx("f2a0a8ff"), hx("b8b8c0ff")
SHIRT, SHIRT_D = hx("4a7fb5ff"), hx("2e5a88ff")
GLOW = (hx("f4a0b0ff"), hx("f4a0b0b0"), hx("f4a0b060"))                 # 젤리 발자국 · 화살촉 (짙은 것부터)


# ── 그리개: 고양이 제 좌표 (u, w) → 화면 ─────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도) · 배율 k. ang=0 이면 u 가 오른쪽, w 가 아래. ang 만큼 시계 방향으로 돈다"""

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


def chain(pts, r0, r1=None):
    """꺾은선 막대 — 굵기가 처음 r0 에서 끝 r1 로 고르게 변한다"""
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


# ── 몸 부위 ──────────────────────────────────────────────────────────────────
HC, HR = (0.0, -7.5), 7.0       # 머리 가운데 · 반지름(앉은 치즈냥 기준)


def head_parts(hc=HC, r=HR, turn=0.0, name="head") -> list:
    """앞모습 머리: 옆으로 퍼진 볼 · 세모 귀(속 분홍) · 이마 줄 셋 · 흰 주둥이. turn 은 얼굴이 옆으로 돈 정도(u)"""
    u0, w0 = hc
    head = any_of(ell(u0, w0 - 0.4, r * 1.0, r * 0.84), ell(u0, w0 + 1.0, r * 1.14, r * 0.64))
    ears, inner = [], []
    for sg in (-1, 1):
        base0, tip, base1 = (u0 + sg * r * 1.0, w0 - r * 0.2), (u0 + sg * r * 0.86 + turn * 0.3, w0 - r * 1.3), \
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
        if abs(mu) > r * 0.86 and any(abs(b - (w0 + r * dd)) < r * 0.07 for dd in (-0.05, 0.22)):
            return STRIPE
        return FUR

    def ear_col(a, b):
        return PINK if inner_hit(a, b) else FUR
    return [(name, head, skin, True), (name + "_ear", any_of(*ears), ear_col, False)]


def body_part(c=(0.0, 3.2), ra=7.2, rb=6.4, belly=True, name="body"):
    """통통한 몸 — 흰 배, 옆구리에 짙은 주황 줄"""
    c0, c1 = c

    def col(a, b):
        if belly and ((a - c0) / (ra * 0.5)) ** 2 + ((b - c1 + rb * 0.1) / (rb * 0.78)) ** 2 <= 1:
            return CREAM
        if abs(a - c0) > ra * 0.62 and (b - c1 + 0.3) % 2.6 < 0.95:
            return STRIPE
        return FUR
    return (name, ell(c0, c1, ra, rb), col, False)


def tail_part(pts, r0=1.9, r1=1.5, name="tail", lined=False):
    """짧고 굵은 꼬리 — 짙은 고리 무늬, 끝은 짙게"""
    at = along(pts)
    total = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:]))

    def col(a, b):
        s = at(a, b)
        if s > total - 0.4:
            return STRIPE
        return STRIPE if (s % 2.8) > 1.9 and s > 1.0 else FUR
    return (name, chain(pts, r0, r1), col, lined)


def arm_part(pts, r=1.7, pr=2.0, name="arm", sock=True, lined=True):
    """앞발 하나 → [발, 팔] 두 부위. 발은 흰 양말"""
    paw = (name + "_paw", ell(*pts[-1], pr, pr * 1.05), CREAM if sock else FUR, True)
    return [paw, (name, chain(pts, r, r * 0.92), FUR, lined)]


def dot(f: dict, x: int, y: int, c: tuple) -> None:
    f[x, y] = c


def face(f: dict, rig: Rig, hc=HC, r=HR, mood="open", turn=0.0, whisk=0) -> None:
    """얼굴: 2×2 눈(흰 반짝 1칸) · 분홍 코 · ㅅ 입 · 볼터치 · 1칸 수염 둘씩. 작게(k < 0.75) 그리면 눈 1×2 · 코 1칸.
    mood: open · blink(감은 한 줄) · sleep(︶) · happy(^) · squeeze(><) · sulk(흥 — 감은 눈을 치켜올림).
    whisk 는 수염 끝이 까딱인 칸 수"""
    u0, w0 = hc
    small = rig.k * r < 5.0
    for sg in (-1, 1):
        ex, ey = rig.world(u0 + turn + sg * r * 0.42, w0 - r * 0.06)
        if small:
            x0, y0 = math.floor(ex), math.floor(ey - 0.5)
            if mood in ("open",):
                dot(f, x0, y0, EYE)
                dot(f, x0, y0 + 1, EYE)
            else:
                dot(f, x0, y0 + 1, EYE)
            continue
        x0, y0 = round(ex - 1), round(ey - 1)
        if mood == "open":
            for dx in (0, 1):
                for dy in (0, 1):
                    dot(f, x0 + dx, y0 + dy, EYE)
            dot(f, x0, y0, HI)
        elif mood == "blink":
            dot(f, x0, y0 + 1, EYE)
            dot(f, x0 + 1, y0 + 1, EYE)
        elif mood == "sleep":     # ︶ — 바깥 끝이 살짝 들린다
            dot(f, x0, y0 + 1, EYE)
            dot(f, x0 + 1, y0 + 1, EYE)
            dot(f, x0 - 1 if sg < 0 else x0 + 2, y0, EYE)
        elif mood == "happy":     # ^
            dot(f, x0 - 1 if sg < 0 else x0, y0 + 1, EYE)
            dot(f, x0 if sg < 0 else x0 + 1, y0, EYE)
            dot(f, x0 + 1 if sg < 0 else x0 + 2, y0 + 1, EYE)
        elif mood == "squeeze":   # > <
            xa, xb = (x0, x0 + 1) if sg < 0 else (x0 + 1, x0)
            dot(f, xa, y0 - 1, EYE)
            dot(f, xb, y0, EYE)
            dot(f, xa, y0 + 1, EYE)
        elif mood == "sulk":      # 감은 눈을 바깥으로 치켜올림
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


def whiskers(f: dict, rig: Rig, hc=HC, r=HR, turn=0.0, n=3, tw=0, skip=()) -> None:
    """볼 바깥으로 뻗은 1칸 수염 둘씩 — 머리 테두리 밖 칸에만 찍는다(얼굴 안에 그으면 콧수염이 된다)"""
    u0, w0 = hc
    for sg in (-1, 1):
        if sg in skip:
            continue
        for j, dw in enumerate((0.05, 0.3)):
            x0, y0 = rig.world(u0 + turn + sg * r * 1.1, w0 + r * dw)
            for i in range(n + 1):
                x = math.floor(x0 + sg * i)
                y = math.floor(y0 + (i * 0.4 * (j * 2 - 1) if j else 0) + (tw if i == n else 0))
                if (x, y) not in f:
                    f[x, y] = OUT


def sit_parts(tail_pts, paws=None, extra=(), front=(), hc=HC, r=HR, turn=0.0, body=None, feet=True) -> list:
    """앉은 통통한 치즈냥: 머리 · 몸 · 앞발 둘(paws 를 주면 그 자리로) · 뒷발 둘 · 꼬리.
    extra 는 맨 앞, front 는 앞발 뒤 · 머리 앞에 놓을 부위"""
    paws = paws if paws is not None else [[(-2.4, 1.0), (-2.4, 8.4)], [(2.4, 1.0), (2.4, 8.4)]]
    arms = []
    for i, pts in enumerate(paws):
        arms += arm_part(pts, name=f"arm{i}", pr=1.9)
    hind = ("feet", any_of(ell(-5.0, 8.9, 2.2, 1.4), ell(5.0, 8.9, 2.2, 1.4)), CREAM, True) if feet else None
    haunch = ("haunch", any_of(ell(-5.0, 6.2, 2.9, 2.8), ell(5.0, 6.2, 2.9, 2.8)), FUR, True)
    return list(extra) + arms + list(front) + head_parts(hc, r, turn) + \
        ([hind] if hind else []) + [haunch, body or body_part(), tail_part(tail_pts)]


def anchor(frames: list[dict], target=(1, 1)) -> list[dict]:
    """맨 왼쪽 위 불투명 칸(x+y 가 가장 작은 것, 같으면 위)을 target 으로 옮긴다 — 화살표 꼴 칸의 발끝"""
    tip = min((p for p, c in frames[0].items() if c[3] == 255), key=lambda p: (p[0] + p[1], p[1]))
    dx, dy = target[0] - tip[0], target[1] - tip[1]
    return [{(x + dx, y + dy): c for (x, y), c in f.items()} for f in frames]


# ── 화살표 치즈냥 ────────────────────────────────────────────────────────────
def arrow_cat(ph: float, k: float = 0.8, blink=False) -> dict:
    """똑바로 앉은 통통한 치즈냥이 왼 앞발을 머리 뒤로 해서 왼쪽 위로 쭉 뻗는다 — 발끝이 왼쪽 위 끝.
    처음엔 고양이째 45도 기울였는데 기운 얼굴이 칸 위에서 뭉개졌다. 얼굴은 똑바로 두고 팔만 뻗는다.
    오른 앞발은 배 앞에서 꾹꾹, 꼬리는 살랑"""
    rig = Rig(16.0, 16.0, 0.0, k)
    sw = math.sin(ph)
    knead = 0.7 * max(0.0, math.sin(2 * ph))
    reach = [(-4.2, -2.0), (-8.4, -9.6), (-10.6, -17.6)]
    down = [(2.6, 1.0), (2.6, 8.2 - knead)]
    tail = [(5.6, 8.2), (9.6, 7.2 + 0.6 * sw), (11.0 + 0.8 * sw, 3.6 + 0.8 * sw)]
    reach_parts = arm_part(reach, name="reach", pr=2.2, lined=False)
    parts = [reach_parts[0]] + arm_part(down, name="down", pr=1.9) + head_parts() + [reach_parts[1]] + \
        [("feet", any_of(ell(-5.0, 8.9, 2.2, 1.4), ell(5.0, 8.9, 2.2, 1.4)), CREAM, True),
         ("haunch", any_of(ell(-5.0, 6.2, 2.9, 2.8), ell(5.0, 6.2, 2.9, 2.8)), FUR, True),
         body_part(), tail_part(tail)]
    out, mask, _ = draw(rig, parts)
    face(out, rig, mood="blink" if blink else "open")
    if k >= 0.7:
        whiskers(out, rig, n=2, skip=(-1,))
    return out


def arrow_frames(small=False) -> list[dict]:
    fr = []
    for k, ph in enumerate(phases()):
        fr.append(arrow_cat(ph, 0.5 if small else 0.8, blink=k in (7,)))
    return anchor(fr)


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    return [finish(f) for f in arrow_frames()]


def companion(scene) -> list[dict]:
    """작은 화살표 치즈냥 + scene(k, ph) 이 그리는 소품 — busy · help · person · pin"""
    cats = arrow_frames(small=True)
    frames = []
    for k, ph in enumerate(phases()):
        f = scene(k, ph)
        f.update(cats[k])
        frames.append(finish(f))
    return frames


def paw_print(f: dict, cx: int, cy: int, col) -> None:
    """젤리 발자국: 2×2 큰 젤리 + 위에 발가락 젤리 셋"""
    for p in ((cx, cy), (cx + 1, cy), (cx, cy + 1), (cx + 1, cy + 1), (cx - 1, cy - 1), (cx + 2, cy - 1)):
        f[p] = col
    f[cx, cy - 2] = col
    f[cx + 1, cy - 2] = col


def fish_parts(c=(0.0, 0.0), L=6.0, h=2.4, flip=False):
    """옆모습 생선 — 몸 타원 + 꼬리 세모. flip 이면 머리가 오른쪽"""
    s = -1 if flip else 1
    body = ell(c[0], c[1], L * 0.5, h * 0.5)
    tail = tri((c[0] + s * L * 0.38, c[1]), (c[0] + s * L * 0.78, c[1] - h * 0.62), (c[0] + s * L * 0.78, c[1] + h * 0.62))

    def col(a, b):
        return FISH_D if b > c[1] + h * 0.12 else FISH
    return [("fish", body, col, True), ("fishtail", tail, FISH_D, False)]


def busy() -> list[dict]:
    cx, cy = 22.0, 22.0

    def scene(k, ph):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = round(cx + 6.8 * math.cos(a) - 0.5), round(cy + 6.8 * math.sin(a) - 0.5)
            lag = (head - i) % 8
            paw_print(f, x, y + 1, NOSE if lag < 1.5 else PINK if lag < 3 else GLOW[2])
        rig = Rig(cx, cy, -20.0 + 8 * math.sin(2 * ph), 1.0)
        o, _, _ = draw(rig, fish_parts(L=8.4, h=3.8, flip=True))
        f.update(o)
        f[rig.cell(2.0, -0.6)] = EYE
        return f
    return companion(scene)


def help_() -> list[dict]:
    """물음표 꼴로 만 줄무늬 꼬리 + 점 자리 털실 공 — 꼬리 끝이 살랑인다"""
    def scene(k, ph):
        f = {}
        sw = 0.8 * math.sin(ph)
        pts = [(17.6, 21.0), (17.6, 18.2), (20.0, 16.0), (23.2, 13.8), (23.4, 10.2), (20.4, 8.4), (17.0, 9.2 + sw)]
        o, _, _ = draw(Rig(0, 0, 0, 1.0), [tail_part(pts, 1.7, 1.4)])
        f.update(o)
        yarn(f, 17.6, 26.2, 2.3, k)
        return f
    return companion(scene)


def yarn(f: dict, cx: float, cy: float, r: float, k: int = 0) -> None:
    """털실 공: 분홍 동그라미에 비스듬한 실 줄, 한 가닥이 삐져나온다"""
    m = disc(cx, cy, r)

    def col(p):
        return YARN_D if (p[0] - p[1] + k // 3) % 3 == 0 else YARN
    solid(f, m, col, OUT)


def person() -> list[dict]:
    """고양이 귀 후드(주황, 귀 속 분홍)를 쓴 사람이 손을 흔든다"""
    def scene(k, ph):
        f = {}
        rig = Rig(22.5, 25.0, 0.0, 0.62)
        wave = -2.0 * abs(math.sin(ph))
        hand = (8.0, -6.0 + wave)
        hood_c, hood_r = (0.0, -8.4), 6.6
        hood = head_parts(hood_c, hood_r + 1.4, name="hood")
        hood = [("hood", hood[0][1], FUR, True), hood[1]]
        faceskin = ("skin", ell(0.0, -7.6, 5.0, 4.6), hx("f7d7bcff"), True)
        parts = [("hand", ell(*hand, 1.7, 1.7), hx("f7d7bcff"), True), ("sleeve", bar((5.0, -0.5), hand, 1.6), SHIRT, False),
                 faceskin] + hood + [("torso", ell(0, 3.0, 7.6, 6.4), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
        out, _, _ = draw(rig, parts)
        for sg in (-1, 1):
            ex, ey = rig.cell(sg * 2.0, -8.0)
            out[ex, ey] = EYE
            out[ex, ey + 1] = EYE
            out[rig.cell(sg * 3.0, -5.8)] = PINK
        f.update({p: c for p, c in out.items() if p[1] <= 30})
        return f
    return companion(scene)


def pin() -> list[dict]:
    """빨간 지도 핀 동그라미 속에 치즈냥 얼굴 — 귀가 핀 위로 솟는다. 땅에 닿을 때 눈을 감는다"""
    def scene(k, ph):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 14.0 + dy
        for x in range(19, 27):
            f.setdefault((x, 28), GLOW[2] if dy else GLOW[1])
        rig = Rig(cx, cy + 0.6 + 7.5 * 0.56, 0.0, 0.56)
        ears = draw(rig, head_parts())[0]
        pinm = disc(cx, cy, 6.2)
        from sea import raster
        pinm |= raster([(cx - 4.4, cy + 3.4), (cx + 4.4, cy + 3.4), (cx, cy + 12.4)])
        solid(f, pinm, SIGN, SIGN_D)
        rig2 = Rig(cx, cy + 0.4 + 7.5 * 0.5, 0.0, 0.5)
        hd, _, _ = draw(rig2, head_parts())
        f.update({p: c for p, c in ears.items() if p not in pinm})
        f.update(hd)
        face(f, rig2, mood="sleep" if dy == 0 else "open")
        return f
    return companion(scene)


def wait() -> list[dict]:
    """방석 위 식빵 자세 — 고개가 스르르 떨어지며 눈이 감기다가 화들짝 들고 뜬다. 꼬리 끝만 까딱.
    머리를 식빵 몸 앞에 반쯤 묻는다 — 몸 위에 얹으면 눈사람(공 두 개)으로 읽힌다"""
    frames = []
    #  장:  0 1 2 3 4 5 6 7 8 9 10 11
    drop = [0, 0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.0, 2.0, 0, 0, 0]
    mood = ["open", "open", "blink", "blink", "sleep", "sleep", "sleep", "sleep", "sleep", "open", "open", "blink"]
    rig = Rig(16.0, 17.0, 0.0, 0.92)
    for k, ph in enumerate(phases()):
        hc = (0.0, -4.6 + drop[k])
        cush = ("cushion", ell(0, 8.6, 13.6, 3.6), lambda a, b: CUSH_L if b < 7.0 else CUSH_D if b > 10.0 else CUSH, True)
        tuft = ("tuft", any_of(ell(-13.2, 9.2, 1.6, 1.0), ell(13.2, 9.2, 1.6, 1.0)), CUSH_D, False)
        loaf = ("body", any_of(ell(0, 2.6, 9.8, 5.6), ell(0, 5.2, 10.4, 3.6)),
                lambda a, b: STRIPE if abs(a) > 5.6 and (b + 0.2) % 2.6 < 0.95 else FUR, False)
        tw = 0.6 * math.sin(2 * ph)
        tail = tail_part([(9.0, 6.0), (5.0, 7.6), (1.0, 7.8 + tw * 0.3)], 1.8, 1.5, lined=True)
        parts = [tail] + head_parts(hc, 6.8) + [loaf, cush, tuft]
        f, _, _ = draw(rig, parts)
        face(f, rig, hc, 6.8, mood[k])
        whiskers(f, rig, hc, 6.8, n=2)
        if k in (5, 6, 7, 8):   # 작은 z 가 피어오른다
            zx, zy = 25 + (k - 5) // 2, 6 - (k - 5) // 2
            for p in ((zx, zy), (zx + 1, zy), (zx + 1, zy + 1), (zx, zy + 2), (zx + 1, zy + 2)):
                f[p] = CUSH_D
        if k == 9:   # 화들짝 — 머리 위 놀란 줄
            for p in ((9, 6), (10, 5), (16, 3), (16, 4), (22, 5), (23, 6)):
                f[p] = OUT
        frames.append(finish(f))
    return frames


def bean_paw(f: dict, rig: Rig, pc, pr: float, sq: float = 0.0) -> None:
    """발바닥 젤리: 아래 가운데 큰 젤리(가로 넓은 세모꼴) + 위로 부채꼴 발가락 젤리 넷 — pc 는 발바닥 가운데"""
    bx, by = rig.world(pc[0], pc[1] + pr * 0.28)
    bx, by = round(bx), round(by)
    w = 2 + round(sq)
    for dy in range(3):
        for dx in range(-w + (1 if dy == 0 else 0), w - (1 if dy == 0 else 0) + (0 if dy < 2 else -1)):
            f[bx + dx, by + dy] = PINK
    for tx, ty in ((-4 - round(sq), -2), (-2, -4), (1, -4), (3 + round(sq), -2)):
        f[bx + tx, by + ty] = PINK
        f[bx + tx, by + ty + 1] = PINK


def hand() -> list[dict]:
    """분홍 젤리가 보이게 앞발을 내밀어 꾹 — 누를 때(장 4–7) 발바닥이 납작하게 퍼지고 눈을 질끈(><) 감는다.
    발바닥 꼭대기가 핫스팟이고 누를 때도 그 칸은 그대로다(아래로만 퍼진다)"""
    frames = []
    rig = Rig(19.0, 21.0, 0.0, 0.74)
    pc0, pr = (-9.6, -16.0), 5.0
    for k, ph in enumerate(phases()):
        press = k in (4, 5, 6, 7)
        sq = 0.9 if press else 0.0
        pc = (pc0[0], pc0[1] - sq * 0.5)   # 위 끝은 그대로 두고 옆 · 아래로 퍼진다
        pad = ("pad", ell(pc[0], pc[1], pr + sq, pr - sq * 0.5), CREAM, True)
        arm = ("arm", chain([(-3.6, -2.0), (-7.4, -9.0), pc], 2.6, 3.0), FUR, False)
        lean = 0.5 if press else 0.0
        hc = (HC[0] - lean, HC[1])
        tail = [(5.6, 8.2), (10.0, 6.6 + 0.8 * math.sin(ph)), (11.0, 2.0 + 0.8 * math.sin(ph))]
        parts = [pad] + head_parts(hc, turn=-0.6) + [arm] + \
            sit_parts(tail, paws=[[(2.4, 1.0), (2.4, 8.4)]], hc=hc)[2:]
        f, _, _ = draw(rig, parts)
        bean_paw(f, rig, pc, pr, sq)
        face(f, rig, hc, mood="squeeze" if press else "open", turn=-0.6)
        whiskers(f, rig, hc, turn=-0.6, n=2, skip=(-1,))
        if press:   # 꾹 — 발바닥 둘레 눌림 줄
            x0, y0 = rig.cell(*pc)
            for p in ((x0 - 6, y0 - 3), (x0 - 7, y0 - 1), (x0 - 6, y0 + 4), (x0 + 6, y0 - 3), (x0 + 7, y0 - 1)):
                if 0 <= p[0] <= 31 and 0 <= p[1] <= 31:
                    f.setdefault(p, OUT)
        frames.append(finish(f))
    return frames


def cross() -> list[dict]:
    """앞모습 얼굴 — 가장 긴 수염 한 가닥씩이 가로 조준선(코 줄), 머리 위로 늘어진 장난감 줄과 턱 밑 줄이 세로선.
    짧은 수염이 까딱이고 눈을 깜빡인다. 코 왼쪽 칸이 핫스팟"""
    frames = []
    r = 7.0
    rig = Rig(16.0, 15.5 - (HC[1] + r * 0.16), 0.0, 1.0)   # 코 줄이 y=15, 코 두 칸이 x=15·16
    for k, ph in enumerate(phases()):
        f = {}
        for x in list(range(1, 6)) + list(range(26, 31)):   # 긴 수염 = 가로선
            f[x, 15] = OUT
        for y in list(range(1, 6)) + list(range(26, 31)):   # 장난감 줄 = 세로선
            f[15, y] = OUT
        hd, _, _ = draw(rig, head_parts(r=r))
        f.update(hd)
        face(f, rig, r=r, mood="blink" if k == 8 else "open")
        tw = round(0.6 * math.sin(2 * ph))
        for sg in (-1, 1):   # 짧은 수염 — 긴 수염 아래로 비스듬히
            x0 = 7 if sg < 0 else 24
            for i in range(3):
                f.setdefault((x0 + sg * i, 17 + (i + 1) // 2 + (tw if i == 2 else 0)), OUT)
        frames.append(finish(f))
    return frames


def ibeam() -> list[dict]:
    """꼬리를 머리 뒤로 곧게 세우고 앉은 작은 치즈냥 — 머리 위로 솟은 줄무늬 꼬리가 I 의 세로획,
    꼬리 끝이 갈고리로 까딱인다. 고양이가 아래 가로획 자리다. 핫스팟은 꼬리 가운데"""
    frames = []
    rig = Rig(16.0, 22.4, 0.0, 0.66)
    for k, ph in enumerate(phases()):
        hook = math.sin(ph)
        top = [(15.5, 17.0), (15.5, 4.6), (15.5 + 1.8 * hook, 2.8)]
        tail = draw(Rig(0, 0, 0, 1.0), [tail_part(top, 1.25, 1.15)])[0]
        cat_f, _, _ = draw(rig, sit_parts([(5.6, 8.2), (8.0, 7.6), (9.0, 5.6)], feet=True)[:-1])
        face(cat_f, rig, mood="blink" if k == 6 else "open")
        f = dict(tail)
        f.update(cat_f)
        frames.append(finish(f))
    return frames


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col) -> None:
    """(dx, dy) 쪽을 가리키는 화살촉. 꼭짓점이 (cx, cy)"""
    px, py = -dy, dx
    for i in range(4):
        for s in (-1, 1):
            for w in (0, 1):
                f[cx - dx * (i + w) + s * px * i, cy - dy * (i + w) + s * py * i] = col


def move() -> list[dict]:
    """배를 깔고 동그랗게 만 치즈냥(위에서 본)이 데굴데굴 한 바퀴 — 네 방향 분홍 화살촉이 바깥으로 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy, GLOW[0])
        rig = Rig(15.5, 15.5, 360.0 * k / N, 1.0)
        hc, r = (0.0, 2.6), 4.6
        tail = tail_part([(6.4, -1.0), (5.6, 4.2), (2.4, 7.0)], 1.7, 1.4, lined=True)
        ball = ("ball", ell(0, -0.6, 7.6, 7.0),
                lambda a, b: STRIPE if (math.atan2(b + 0.6, a) * 7 / math.pi) % 2 < 0.55 and math.hypot(a, b + 0.6) > 3.4
                else FUR, False)
        out, _, _ = draw(rig, [tail] + head_parts(hc, r) + [ball])
        face(out, rig, hc, r, mood="happy")
        f.update(out)
        frames.append(finish(f))
    return frames


def stretch(ang: float, belly: int = -1) -> list[dict]:
    """쭉 기지개 — 몸은 ang 축으로 눕히고 앞발은 머리 쪽 끝, 뒷발은 반대 끝으로 쭉 뻗어 늘었다 줄었다.
    양 끝 화살촉이 늘 때 바깥으로 두근대고, 늘 때 눈을 질끈 감는다. 몸 가운데가 판 가운데.
    머리는 몸과 같이 돌리지 않고 늘 똑바로 세워 몸 앞(머리 쪽 끝)에 붙인다 — 돌린 얼굴은 칸 위에서 뭉개지고,
    처음엔 앞모습 고양이를 통째로 세워 팔을 머리 옆으로 올렸더니 머리 위 흰 발이 귀 · 두건으로, 몸은 알약으로 읽혔다.
    앞발은 턱 밑(배 쪽, belly 가 그 u 부호)으로 나와 머리보다 멀리 뻗는다"""
    frames = []
    t = math.radians(ang)
    ex, ey = math.sin(t), -math.cos(t)           # 머리 쪽 (화면)
    dx, dy = round(ex), round(ey)
    R = 13 if dx == 0 or dy == 0 else 10
    k_ = 0.8
    for k, ph in enumerate(phases()):
        f = {}
        s = 0.5 + 0.5 * math.sin(ph)              # 0 줄음 → 1 쭉
        for sg in (-1, 1):
            o = 1 if s > 0.6 else 0
            chevron(f, 15 + (1 if sg * dx > 0 else 0) + sg * dx * (R + o) - (1 if sg * dx > 0 else 0),
                    15 + sg * dy * (R + o), sg * dx, sg * dy, GLOW[0] if o else GLOW[1])
        rig = Rig(16.0 + ex * 0.4, 16.0 + ey * 0.4, ang, k_)
        reach = 1.4 * s
        b = belly
        legs = []
        for i, (sh, tip) in enumerate((((b * 3.6, -2.0), (b * 6.0, -13.6 - reach)), ((b * 1.6, -1.6), (b * 3.8, -13.0 - reach)),
                                       ((b * 2.0, 5.6), (b * 2.4, 11.4 + reach)), ((-b * 0.2, 5.8), (-b * 0.2, 10.8 + reach)))):
            legs += arm_part([sh, tip], r=1.9, pr=2.0, name=f"leg{i}")
        body = ("body", ell(0.0, 2.0, 4.0, 5.8 + reach * 0.4),
                lambda a, bb: CREAM if a * b > 1.6 else STRIPE if a * b < -0.6 and (bb + 0.4) % 2.6 < 0.95 else FUR, False)
        tail = tail_part([(-b * 1.6, 6.6), (-b * 5.0, 8.4), (-b * 6.0, 11.4 - reach * 0.4)], 1.6, 1.3)
        out, _, _ = draw(rig, legs + [body, tail])
        f.update(out)
        hx_, hy_ = rig.world(-b * 0.6, -5.4)
        hr = 6.4
        hrig = Rig(hx_, hy_ - (HC[1] + 0.4) * k_, 0.0, k_)     # 머리 가운데가 (hx_, hy_ + 0.4k) 쯤
        hd, _, _ = draw(hrig, head_parts(r=hr))
        f.update(hd)
        face(f, hrig, r=hr, mood="squeeze" if s > 0.6 else "open")
        frames.append(finish(f))
    return frames


def ns():
    return stretch(0.0)


def we():
    return stretch(-90.0)


def nwse():
    return stretch(-45.0)


def nesw():
    return stretch(45.0, 1)


def sign(f: dict, R: float = 13.5) -> None:
    """빨간 금지 표지(고리 + 왼쪽 위 → 오른쪽 아래 빗금)"""
    ring = {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
    slash = set()
    for t in range(-90, 91):
        x, y = 15.5 + t / 100 * (R - 1.5) * 0.7071, 15.5 + t / 100 * (R - 1.5) * 0.7071
        slash |= disc(x, y, 1.3)
    solid(f, ring | slash, SIGN, SIGN_D)


def no() -> list[dict]:
    """빨간 금지 표지 안에서 팔짱을 끼고 고개를 홱 돌린 치즈냥(삐짐) — 반 바퀴마다 반대쪽으로 홱, 그때 꼬리를 탁"""
    frames = []
    rig = Rig(16.0, 17.6, 0.0, 0.72)
    for k, ph in enumerate(phases()):
        f = {}
        sign(f)
        side_ = -1 if k < 6 else 1
        snap = k in (0, 6)
        turn = side_ * (1.4 if snap else 2.2)
        hc = (HC[0], HC[1] - 0.6)
        arms = arm_part([(-4.6, 0.6), (3.6, 2.6)], r=1.8, pr=1.8, name="armL") + \
            arm_part([(4.6, 0.6), (-3.6, 3.4)], r=1.8, pr=1.8, name="armR")
        tw = -side_ * (2.0 if snap else 1.0)
        tail = [(5.6, 8.2), (9.6, 7.4), (11.0 + tw * 0.4, 4.0 + tw)]
        parts = arms + sit_parts(tail, paws=[], hc=hc, turn=turn)
        o, _, _ = draw(rig, parts)
        face(o, rig, hc, mood="sulk", turn=turn)
        whiskers(o, rig, hc, turn=turn, n=2, skip=(side_ * -1,))
        f.update({p: c for p, c in o.items() if 1 <= p[1] <= 30})
        if snap:   # 홱 — 돈 쪽 반대편에 움직임 줄
            x0 = 6 if side_ > 0 else 25
            for y in (8, 10, 12):
                f[x0, y] = OUT
                f[x0 + side_ * -1, y] = OUT
        frames.append(finish(f))
    return frames


TIP, BACK = (1.5, 29.5), (25.0, 12.0)   # 연필심 · 지우개 끝(화면)


def pen() -> list[dict]:
    """두 앞발로 연필을 꼭 쥐고 쓰는 치즈냥 — 연필과 고양이가 연필심을 축으로 까딱인다. 연필심이 핫스팟.
    쓰다가 혀를 빼꼼 내민다(집중)"""
    frames = []
    base = Rig(20.6, 15.8, 0.0, 0.62)
    L = math.hypot(BACK[0] - TIP[0], BACK[1] - TIP[1])
    ux, uy = (BACK[0] - TIP[0]) / L, (BACK[1] - TIP[1]) / L
    cone = (TIP[0] + ux * 3.6, TIP[1] + uy * 3.6)
    lt, lc, lb = base.local(*TIP), base.local(*cone), base.local(*BACK)
    rr = 1.6 / base.k

    def pcol(a, b):
        x, y = base.world(a, b)
        tt = (x - TIP[0]) * ux + (y - TIP[1]) * uy
        sd = -(x - TIP[0]) * uy + (y - TIP[1]) * ux
        if tt < 1.4:
            return LEAD
        if tt < 3.8:
            return WOOD
        if tt > L - 1.8:
            return ERASER
        if tt > L - 3.4:
            return FERRULE
        return PENCIL_D if sd > 0.5 else PENCIL
    pencil = ("pencil", any_of(bar(lt, lc, 0.45 / base.k, rr), bar(lc, lb, rr)), pcol, True)
    g1 = base.local(TIP[0] + ux * L * 0.6, TIP[1] + uy * L * 0.6)
    g2 = base.local(TIP[0] + ux * L * 0.78, TIP[1] + uy * L * 0.78)
    for k, ph in enumerate(phases()):
        d = math.radians(3.0 * math.sin(2 * ph))
        ox, oy = base.ox - TIP[0], base.oy - TIP[1]
        rig = Rig(TIP[0] + ox * math.cos(d) - oy * math.sin(d), TIP[1] + ox * math.sin(d) + oy * math.cos(d),
                  math.degrees(d), base.k)
        paws = arm_part([(-4.0, 0.0), (g1[0] + 0.6, g1[1] - 0.6)], r=1.7, pr=2.0, name="armL") + \
            arm_part([(4.0, 0.0), (g2[0] + 0.6, g2[1] - 0.6)], r=1.7, pr=2.0, name="armR")
        pp = [p for p in paws if p[0].endswith("_paw")]
        ab = [p for p in paws if not p[0].endswith("_paw")]
        tail = [(5.6, 8.2), (10.0, 6.8), (11.0 + 0.8 * math.sin(ph), 2.4)]
        parts = pp + [pencil] + ab + sit_parts(tail, paws=[], hc=HC)
        f, _, _ = draw(rig, parts)
        face(f, rig, mood="blink" if k == 4 else "open")
        whiskers(f, rig, n=2, skip=(-1,))
        if k % 6 in (2, 3, 4):   # 혀 빼꼼
            nx, ny = rig.world(0.0, HC[1] + HR * 0.16)
            f[round(nx), math.floor(ny) + 2] = NOSE
        f[math.floor(TIP[0]), math.floor(TIP[1])] = LEAD
        frames.append(finish(f))
    return frames


def up() -> list[dict]:
    """두 앞발을 옆으로 활짝 든 만세 \\(^ㅅ^)/ — 츄르 달라고 뒷발로 서서 들썩이고 입을 냥냥 벌린다.
    머리는 그 자리에 두고 몸만 들썩여서 핫스팟(머리 꼭대기 가운데, 두 귀 사이)이 장마다 같은 칸이다.
    처음엔 두 발을 머리 위에서 모았는데 머리를 감싼 팔이 두건 · 투구로, 머리 옆으로 곧게 세운 팔은 긴 귀로 읽혔다"""
    frames = []
    for k, ph in enumerate(phases()):
        bob = 0.8 * abs(math.sin(ph))
        rig = Rig(16.0, 18.0, 0.0, 0.72)
        hc = (0.0, -7.0)
        arms = []
        for i, sg in enumerate((-1, 1)):
            arms += arm_part([(sg * 5.4, -1.4 - bob), (sg * 9.6, -6.4), (sg * 11.6, -12.4)], r=1.9, pr=2.2,
                             name=f"arm{i}", lined=True)
        legs = [("feet", any_of(ell(-3.6, 12.4, 2.4, 1.4), ell(3.6, 12.4, 2.4, 1.4)), CREAM, True),
                ("legs", any_of(bar((-3.4, 6.0), (-3.6, 11.6), 2.2), bar((3.4, 6.0), (3.6, 11.6), 2.2)), FUR, False)]
        body = body_part((0.0, 3.0 - bob * 0.5), 6.6, 6.6 + bob * 0.4)
        tail = tail_part([(4.0, 9.0), (8.0, 9.6), (9.6 + 0.8 * math.sin(2 * ph), 6.2)], 1.7, 1.4)
        parts = arms + head_parts(hc) + legs + [body, tail]
        f, _, _ = draw(rig, parts)
        face(f, rig, hc, mood="happy" if k % 4 < 2 else "open")
        whiskers(f, rig, hc, n=2)
        if k % 4 < 2:   # 냥 — 입을 벌린다
            nx, ny = rig.world(0.0, hc[1] + HR * 0.16)
            for p in ((round(nx) - 1, math.floor(ny) + 2), (round(nx), math.floor(ny) + 2)):
                f[p] = NOSE
        for x in range(8, 25):   # 바닥 그림자
            f.setdefault((x, 28), GLOW[2])
        frames.append(finish(f))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def head_top(fr):
    """두 귀 사이 머리 꼭대기 — 판 가운데 줄(x=15)에서 맨 위 불투명 칸"""
    return min((p for p, c in fr[0].items() if c[3] == 255 and p[0] == 15), key=lambda p: p[1])


def top_cell(fr):
    return min((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1], p[0]))


HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1),
       "wait": (16, 16), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (15, 9),
       "pen": (math.floor(TIP[0]), math.floor(TIP[1])), "hand": top_cell, "up": head_top}


def check(rid: str, frames: list[dict], hot: tuple) -> None:
    """핫스팟이 장마다 불투명한 칸 위에 있는지 · 판(0–31) 안인지"""
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
        if any(not (0 <= x <= 31 and 0 <= y <= 31) for x, y in f):
            print(f"  ! {rid} {i}장: 판 밖으로 나간 칸이 있음")
        if hot == (1, 1) and any(c[3] == 255 and (p[0] < 1 or p[1] < 1) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 발끝보다 왼쪽·위로 나온 칸이 있음")


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

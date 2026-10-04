# SPDX-License-Identifier: Apache-2.0
"""삼색냥(calicocatanim) 구성표 그림 `art/calicocatanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/calicocat.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

해양 애니처럼 칸마다 삼색냥이 그 칸 뜻에 맞는 짓을 따로 그린다(`SCENE`). '냥이 · 애니' 묶음(치즈냥 · 턱시도냥 ·
까망이 · 고등어냥 · 삼색냥) 중 삼색냥은 **흰 바탕**에 큰 얼룩 둘 — 왼쪽 귀와 이마는 주황, 오른쪽 귀와 이마는 까망,
몸통 왼쪽 위에 주황 한 덩이 · 오른쪽 엉덩이에 까만 한 덩이, 꼬리는 까망. 얼룩이 잘게 흩어지면 32px 에서
더러워 보여서 큰 덩어리만 둔다(`patches`). 머리 · 귀 · 눈 비율과 작은 화살표 동반 꼴 · 분홍 발자국 고리는 치즈냥을 따른다.
소품의 주인공은 골판지 상자와 꾹꾹이 담요다.

  arrow   큰 흰 화살표 뒤에 숨은 삼색냥이 빗변 위로 빼꼼 — 주황 발끝 둘이 빗변을 잡고 장 2–5 에 쏙 더 올라온다.
          화살표 끝이 핫스팟(`sea.peek`, 냥이 10종 공용 틀)
  busy    작은 화살표 삼색냥 + 오른쪽 아래 작은 골판지 상자 둘레를 도는 분홍 발자국 여덟
  cross   앞모습 얼굴 — 양 볼 수염이 가로 조준선, 머리 위로 늘어진 낚싯대 장난감 줄과 턱 밑 줄이 세로선. 코가 핫스팟
  hand    배를 깔고 엎드린 식빵 삼색냥이 앞발 하나를 위로 쭉 내밀어 톡톡 — 누를 때 젤리가 벌어진다. 발끝이 핫스팟
  help    작은 화살표 삼색냥 + 까만 꼬리(끝은 주황)를 말아 만든 물음표, 점은 분홍 발자국
  ibeam   스크래처 기둥(삼줄)이 I — 뒷발로 서서 기둥을 끌어안고 앞발로 번갈아 박박 긁는다. 핫스팟은 기둥 가운데
  move    골판지 상자에 쏙 들어간 삼색냥이 상자째 좌우로 들썩 — 네 방향 분홍 화살촉
  ns · nwse · nesw · we   앞발은 머리 위로, 뒷발은 뒤로 쭉 뻗은 기지개 — 그 축으로 몸이 늘었다 줄었다 하고 양 끝
          화살촉이 두근댄다. 얼굴은 기울이면 뭉개져서 몸만 축으로 돌리고 얼굴은 늘 똑바로 둔다
  no      빨간 금지 표지 안에서 상자에 든 삼색냥이 날개를 닫아 버린다 — 닫힌 날개 틈으로 귀만, 다시 빼꼼
  pen     붓을 두 앞발로 쥐고 먹 글씨를 쓴다 — 붓끝(왼쪽 아래)이 핫스팟, 지나간 자리에 먹이 남는다
  person  작은 화살표 삼색냥 + 삼색 고양이 귀 후드(왼 귀 주황 · 오른 귀 까망)를 쓴 사람이 손을 흔든다
  pin     작은 화살표 삼색냥 + 동그라미 속에 삼색냥 얼굴(귀가 핀 위로 솟음)이 든 빨간 지도 핀이 통통 튄다
  up      상자에서 쏙 일어서 앞발 하나를 머리 위로 번쩍(저요!) — 든 발끝(맨 위)이 핫스팟. 상자 날개가 들썩
  wait    보라 담요 위에서 꾹꾹이 — 두 앞발을 번갈아 눌러 담요가 움푹 꺼지고, 눈은 ^^ 로 골골. 가운데가 핫스팟

몸은 부위(타원 · 굵기가 변하는 막대 · 세모)를 고양이 제 좌표 (u 오른쪽, w 아래)에 놓고 화면으로 돌려 찍는다
(`Rig`, `draw` — 치즈냥 생성기와 같은 방식이지만 다른 생성기에 기대지 않게 여기 따로 둔다).
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, disc, finish, hx, ink, inside, peek, phases, raster, solid, write  # noqa: F401

SID = "calicocatanim"

OUT, EYE = hx("3a2a30ff"), hx("2a1c22ff")                     # 테두리 · 눈
WHITE, WHITE_D = hx("fff6e8ff"), hx("eadccaff")                # 바탕 털 · 그늘
ORNG, ORNG_D = hx("ec8f3cff"), hx("c46a26ff")                  # 주황 얼룩
BLK, BLK_L = hx("4d424bff"), hx("6c5f69ff")                    # 까만 얼룩 (테두리와 갈리게 조금 밝게) · 결
PINK, NOSE, HI = hx("f4a0b0ff"), hx("e27d90ff"), hx("ffffffff")
ink(OUT, HI, hx("fbecdcc7"))
BOX, BOX_D, BOX_L, BOX_IN = hx("d2a466ff"), hx("a5793fff"), hx("e8c690ff"), hx("6e4c2cff")   # 골판지 상자
BLANK, BLANK_D, BLANK_L = hx("b9a3dcff"), hx("8d74b8ff"), hx("d8cbefff")                       # 꾹꾹이 담요
SISAL, SISAL_D, POST = hx("dcc08aff"), hx("b0915aff"), hx("8fa7c8ff")                          # 스크래처
BRUSH, BRUSH_D, INKC = hx("c9a46aff"), hx("8f6c38ff"), hx("2b2630ff")                          # 붓 · 먹
SHIRT, SHIRT_D, SKIN = hx("6aa36aff"), hx("487a4aff"), hx("f7d7bcff")
GLOW = (hx("f4a0b0ff"), hx("f4a0b0b0"), hx("f4a0b060"))   # 발자국 · 화살촉 (짙은 것부터) — 냥이 묶음 공통


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
    """꺾은선 위 가장 가까운 점까지의 길이(처음부터) — 꼬리 끝 색용"""
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
    return at, acc


def tri(*pts):
    pl = list(pts)
    return lambda a, b: inside(pl, a, b)


def box_hit(a0, b0, a1, b1):
    return lambda a, b: a0 <= a <= a1 and b0 <= b <= b1


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
HC, HR = (0.0, -7.5), 7.0       # 머리 가운데 · 반지름(앉은 삼색냥 기준)


def patches(base, *blobs):
    """흰 바탕 위 큰 얼룩: blobs = (맞음(a, b), 색) 들 — 앞의 것이 이긴다"""
    def col(a, b):
        for hit, c in blobs:
            if hit(a, b):
                return c
        return base
    return col


def head_parts(hc=HC, r=HR, turn=0.0, name="head", mirror=False) -> list:
    """앞모습 머리: 옆으로 퍼진 볼 · 세모 귀(속 분홍). 왼쪽 귀 · 이마는 주황, 오른쪽 귀 · 이마는 까망(mirror 면 반대).
    얼룩은 눈 위에서 끊는다 — 까만 얼룩에 눈이 묻히면 한쪽 눈이 없어 보인다"""
    u0, w0 = hc
    head = any_of(ell(u0, w0 - 0.4, r * 1.0, r * 0.84), ell(u0, w0 + 1.0, r * 1.14, r * 0.64))
    ears, inner = {}, []
    for sg in (-1, 1):
        base0, tip, base1 = (u0 + sg * r * 1.0, w0 - r * 0.2), (u0 + sg * r * 0.86 + turn * 0.3, w0 - r * 1.3), \
            (u0 + sg * r * 0.2, w0 - r * 0.74)
        ears[sg] = tri(base0, tip, base1)
        cx, cy = (base0[0] + tip[0] + base1[0]) / 3, (base0[1] + tip[1] + base1[1]) / 3 + r * 0.06
        inner.append(tri(*[(cx + (p[0] - cx) * 0.48, cy + (p[1] - cy) * 0.48) for p in (base0, tip, base1)]))
    inner_hit = any_of(*inner)
    lo, hi = (BLK, ORNG) if mirror else (ORNG, BLK)
    left = ell(u0 - r * 0.62 + turn * 0.4, w0 - r * 0.78, r * 0.62, r * 0.5, -0.35)
    right = ell(u0 + r * 0.66 + turn * 0.4, w0 - r * 0.8, r * 0.56, r * 0.46, 0.35)
    skin = patches(WHITE, (left, lo), (right, hi))

    def ear_col(a, b):
        if inner_hit(a, b):
            return PINK
        return lo if a < u0 else hi
    return [(name, head, skin, True), (name + "_ear", any_of(*ears.values()), ear_col, False)]


def body_part(c=(0.0, 3.2), ra=7.2, rb=6.4, name="body"):
    """통통한 몸 — 흰 바탕, 왼쪽 위 주황 얼룩 · 오른쪽 아래 까만 얼룩"""
    c0, c1 = c
    col = patches(WHITE, (ell(c0 - ra * 0.62, c1 - rb * 0.5, ra * 0.55, rb * 0.5, -0.4), ORNG),
                  (ell(c0 + ra * 0.78, c1 + rb * 0.35, ra * 0.42, rb * 0.5), BLK))
    return (name, ell(c0, c1, ra, rb), col, False)


def tail_part(pts, r0=1.8, r1=1.4, name="tail", lined=False):
    """까만 꼬리 — 끝만 주황"""
    at, total = along(pts)

    def col(a, b):
        return ORNG if at(a, b) > total - 1.4 else BLK
    return (name, chain(pts, r0, r1), col, lined)


def arm_part(pts, r=1.7, pr=2.0, name="arm", fur=WHITE, lined=True):
    """앞발 하나 → [발, 팔] 두 부위. 발은 흰 양말"""
    paw = (name + "_paw", ell(*pts[-1], pr, pr * 1.05), WHITE, True)
    return [paw, (name, chain(pts, r, r * 0.92), fur, lined)]


def dot(f: dict, x: int, y: int, c: tuple) -> None:
    f[x, y] = c


def face(f: dict, rig: Rig, hc=HC, r=HR, mood="open", turn=0.0) -> None:
    """얼굴: 2×2 눈(흰 반짝 1칸) · 분홍 코 · ㅅ 입 · 볼터치. 작게(k·r < 5) 그리면 눈 1×2 · 코 1칸.
    mood: open · blink(감은 한 줄) · happy(^ — 골골) · peek(눈만 동그랗게, 입 없음)"""
    u0, w0 = hc
    small = rig.k * r < 5.0
    for sg in (-1, 1):
        ex, ey = rig.world(u0 + turn + sg * r * 0.42, w0 - r * 0.06)
        if small:
            x0, y0 = math.floor(ex), math.floor(ey - 0.5)
            if mood in ("open", "peek"):
                dot(f, x0, y0, EYE)
            dot(f, x0, y0 + 1, EYE)
            continue
        x0, y0 = round(ex - 1), round(ey - 1)
        if mood in ("open", "peek"):
            for dx in (0, 1):
                for dy in (0, 1):
                    dot(f, x0 + dx, y0 + dy, EYE)
            dot(f, x0, y0, HI)
        elif mood == "blink":
            dot(f, x0, y0 + 1, EYE)
            dot(f, x0 + 1, y0 + 1, EYE)
        elif mood == "happy":     # ^
            dot(f, x0 - 1 if sg < 0 else x0, y0 + 1, EYE)
            dot(f, x0 if sg < 0 else x0 + 1, y0, EYE)
            dot(f, x0 + 1 if sg < 0 else x0 + 2, y0 + 1, EYE)
    if mood == "peek":
        return
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
    """볼 바깥으로 뻗은 1칸 수염 둘씩 — 머리 테두리 밖 빈 칸에만 찍는다(얼굴 안에 그으면 콧수염이 된다)"""
    u0, w0 = hc
    for sg in (-1, 1):
        if sg in skip:
            continue
        for j, dw in enumerate((0.05, 0.3)):
            x0, y0 = rig.world(u0 + turn + sg * r * 1.1, w0 + r * dw)
            for i in range(n + 1):
                x = math.floor(x0 + sg * i)
                y = math.floor(y0 + (i * 0.4 if j else 0))
                if (x, y) not in f:
                    f[x, y] = OUT


def head_only(rig, hc=HC, r=HR, mood="open", turn=0.0, whisk=True, mirror=False) -> dict:
    f, _, _ = draw(rig, head_parts(hc, r, turn, mirror=mirror))
    face(f, rig, hc, r, mood, turn)
    if whisk:
        whiskers(f, rig, hc, r, turn)
    return f


def anchor(frames: list[dict], target=(1, 1)) -> list[dict]:
    """맨 왼쪽 위 불투명 칸(x+y 가 가장 작은 것, 같으면 위)을 target 으로 옮긴다 — 화살표 꼴 칸의 발끝"""
    tip = min((p for p, c in frames[0].items() if c[3] == 255), key=lambda p: (p[0] + p[1], p[1]))
    dx, dy = target[0] - tip[0], target[1] - tip[1]
    return [{(x + dx, y + dy): c for (x, y), c in f.items()} for f in frames]


# ── 소품 ─────────────────────────────────────────────────────────────────────
def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col, n: int = 4) -> None:
    """(dx, dy) 쪽을 가리키는 화살촉. 꼭짓점이 (cx, cy)"""
    px, py = -dy, dx
    for i in range(n):
        for s in (-1, 1):
            for w in (0, 1):
                f[cx - dx * (i + w) + s * px * i, cy - dy * (i + w) + s * py * i] = col


def paw_print(f: dict, cx: int, cy: int, col) -> None:
    """젤리 발자국: 2×2 큰 젤리 + 위에 발가락 젤리 넷"""
    for p in ((cx, cy), (cx + 1, cy), (cx, cy + 1), (cx + 1, cy + 1), (cx - 1, cy - 1), (cx + 2, cy - 1),
              (cx, cy - 2), (cx + 1, cy - 2)):
        f[p] = col


def box_parts(a0=-7.0, a1=7.0, b0=0.0, b1=9.0, flap=1.0, inside_=True, name="box"):
    """앞에서 본 열린 골판지 상자 — 앞판 · 양옆으로 벌어진 날개 · 안쪽 그늘(inside_).
    flap 은 날개가 벌어진 정도(1 = 활짝, 0 = 닫혀 위를 덮음). 앞판 가운데 테이프 한 줄"""
    mid = (a0 + a1) / 2
    w = (a1 - a0) / 2

    def front_col(a, b):
        if abs(a - mid) < 0.9 and b < b0 + 3.0:
            return BOX_L
        return BOX_D if b > b1 - 1.6 else BOX
    parts = [(name, box_hit(a0, b0, a1, b1), front_col, True)]
    fl = []
    al = math.radians(155.0 * flap)     # 0 = 안쪽으로 누워 입구를 덮음 · 90 = 곧게 섬 · 155 = 바깥으로 활짝(더 세우면 든 팔로 읽힌다)
    for sg in (-1, 1):
        edge = a0 if sg < 0 else a1
        d = (-sg * math.cos(al), -math.sin(al))
        n = (-d[1] * 1.5, d[0] * 1.5)
        L = w * 1.02 if flap < 0.5 else w * 0.8
        h = (edge, b0 - 0.4)
        e = (h[0] + d[0] * L, h[1] + d[1] * L)
        fl.append(tri((h[0] + n[0], h[1] + n[1]), (e[0] + n[0], e[1] + n[1]), (e[0] - n[0], e[1] - n[1]),
                      (h[0] - n[0], h[1] - n[1])))
    parts.append((name + "_flap", any_of(*fl), BOX_L, True))
    if inside_:
        parts.append((name + "_in", box_hit(a0 + 0.6, b0 - 1.8, a1 - 0.6, b0 + 0.4), BOX_IN, False))
    return parts


def sign(f: dict, cx=15.5, cy=15.5, R=13.5) -> set:
    """빨간 금지 표지(둥근 테 + 왼쪽 위 → 오른쪽 아래 빗금) — 칠한 칸 집합을 돌려준다"""
    ring = {p for p in disc(cx, cy, R) if math.hypot(p[0] + 0.5 - cx, p[1] + 0.5 - cy) > R - 2.4}
    slash = set()
    for t in range(-90, 91):
        x, y = cx + t / 100 * (R - 1.5) * 0.7071, cy + t / 100 * (R - 1.5) * 0.7071
        slash |= disc(x, y, 1.3)
    solid(f, ring | slash, SIGN, SIGN_D)
    return ring | slash


# ── 화살표 삼색냥 ────────────────────────────────────────────────────────────
def arrow_cat(ph: float, k: float = 0.8, blink=False) -> dict:
    """똑바로 앉은 삼색냥이 왼 앞발을 머리 뒤로 해서 왼쪽 위로 쭉 뻗는다 — 발끝이 왼쪽 위 끝.
    뻗은 팔은 주황 얼룩 쪽이라 주황, 발만 흰 양말. 오른 앞발은 배 앞에서 꾹꾹, 꼬리는 살랑"""
    rig = Rig(16.0, 16.0, 0.0, k)
    sw = math.sin(ph)
    knead = 0.7 * max(0.0, math.sin(2 * ph))
    reach = [(-4.2, -2.0), (-8.4, -9.6), (-10.6, -17.6)]
    down = [(2.6, 1.0), (2.6, 8.2 - knead)]
    tail = [(5.6, 8.2), (9.6, 7.2 + 0.6 * sw), (11.0 + 0.8 * sw, 3.6 + 0.8 * sw)]
    reach_parts = arm_part(reach, r=2.0, name="reach", pr=2.3, fur=ORNG, lined=False)
    parts = [reach_parts[0]] + arm_part(down, name="down", pr=1.9) + head_parts() + [reach_parts[1]] + \
        [("feet", any_of(ell(-5.0, 8.9, 2.2, 1.4), ell(5.0, 8.9, 2.2, 1.4)), WHITE, True),
         ("haunch", any_of(ell(-5.0, 6.2, 2.9, 2.8), ell(5.0, 6.2, 2.9, 2.8)),
          lambda a, b: BLK if a > 0 else WHITE, True),
         body_part(), tail_part(tail)]
    out, mask, _ = draw(rig, parts)
    face(out, rig, mood="blink" if blink else "open")
    if k >= 0.7:
        whiskers(out, rig, n=2, skip=(-1,))
    return out


def arrow_frames(small=False) -> list[dict]:
    return anchor([arrow_cat(ph, 0.5 if small else 0.8, blink=k == 7) for k, ph in enumerate(phases())])


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    def head(x, y, k):
        rig = Rig(x - HC[0] * PEEK_K, y - HC[1] * PEEK_K, 0.0, PEEK_K)
        g, _, _ = draw(rig, head_parts() + [   # 꼬리 · 앞발은 화살표 뒤라 안 그린다
            ("feet", any_of(ell(-5.0, 8.9, 2.2, 1.4), ell(5.0, 8.9, 2.2, 1.4)), WHITE, True),
            ("haunch", any_of(ell(-5.0, 6.2, 2.9, 2.8), ell(5.0, 6.2, 2.9, 2.8)), lambda a, b: BLK if a > 0 else WHITE, True),
            body_part()])
        face(g, rig, mood="blink" if k == 7 else "open")
        whiskers(g, rig, n=2, skip=(-1,))
        return g
    return [finish(peek(k, head, OUT, ORNG)) for k in range(N)]


PEEK_K = 0.74     # 빼꼼 삼색냥 배율


def companion(scene) -> list[dict]:
    """작은 화살표 삼색냥 + scene(k, ph) 이 그리는 소품 — busy · help · person · pin"""
    cats = arrow_frames(small=True)
    frames = []
    for k, ph in enumerate(phases()):
        f = scene(k, ph)
        f.update(cats[k])
        frames.append(finish(f))
    return frames


def busy() -> list[dict]:
    """작은 골판지 상자 둘레를 분홍 발자국 여덟이 차례로 돈다 — 상자 날개가 까딱"""
    cx, cy = 22.0, 22.0

    def scene(k, ph):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = round(cx + 7.0 * math.cos(a) - 0.5), round(cy + 7.0 * math.sin(a) - 0.5)
            lag = (head - i) % 8
            paw_print(f, x, y + 1, GLOW[0] if lag < 1.5 else GLOW[1] if lag < 3 else GLOW[2])
        o, _, _ = draw(Rig(cx, cy + 0.6, 0.0, 0.62), box_parts(-4.4, 4.4, -1.6, 4.4, 0.75 + 0.15 * math.sin(2 * ph)))
        f.update(o)
        return f
    return companion(scene)


def help_() -> list[dict]:
    """물음표 꼴로 만 까만 꼬리(끝 주황) + 점 자리 분홍 발자국 — 꼬리 끝이 살랑인다"""
    def scene(k, ph):
        f = {}
        sw = 0.8 * math.sin(ph)
        pts = [(17.6, 21.0), (17.6, 18.2), (20.0, 16.0), (23.2, 13.8), (23.4, 10.2), (20.4, 8.4), (17.0, 9.2 + sw)]
        o, _, _ = draw(Rig(0, 0, 0, 1.0), [tail_part(pts, 1.7, 1.4)])
        f.update(o)
        paw_print(f, 17, 26, GLOW[0])
        return f
    return companion(scene)


def person() -> list[dict]:
    """삼색 고양이 귀 후드(흰 바탕, 왼 귀 주황 · 오른 귀 까망)를 쓴 사람이 손을 흔든다"""
    def scene(k, ph):
        f = {}
        rig = Rig(22.5, 25.0, 0.0, 0.62)
        hand = (8.0, -6.0 - 2.0 * abs(math.sin(ph)))
        hood = head_parts((0.0, -8.4), 8.0, name="hood")
        faceskin = ("skin", ell(0.0, -7.6, 5.0, 4.6), SKIN, True)
        parts = [("hand", ell(*hand, 1.7, 1.7), SKIN, True), ("sleeve", bar((5.0, -0.5), hand, 1.6), SHIRT, False),
                 faceskin] + hood + \
            [("torso", ell(0, 3.0, 7.6, 6.4), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
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
    """빨간 지도 핀 동그라미 속에 삼색냥 얼굴 — 귀가 핀 위로 솟는다. 땅에 닿을 때 눈을 감는다"""
    def scene(k, ph):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 14.0 + dy
        for x in range(19, 27):
            f.setdefault((x, 28), GLOW[2] if dy else GLOW[1])
        rig = Rig(cx, cy + 0.6 + 7.5 * 0.56, 0.0, 0.56)
        ears = draw(rig, head_parts())[0]
        pinm = disc(cx, cy, 6.2) | raster([(cx - 4.4, cy + 3.4), (cx + 4.4, cy + 3.4), (cx, cy + 12.4)])
        solid(f, pinm, SIGN, SIGN_D)
        rig2 = Rig(cx, cy + 0.4 + 7.5 * 0.5, 0.0, 0.5)
        hd, _, _ = draw(rig2, head_parts())
        f.update({p: c for p, c in ears.items() if p not in pinm})
        f.update(hd)
        face(f, rig2, mood="blink" if dy == 0 else "open")
        return f
    return companion(scene)


def wait() -> list[dict]:
    """보라 담요 위 꾹꾹이 — 두 앞발을 번갈아 꾹 눌러 그 자리 담요가 꺼지고(짙은 보라 주름), 든 발은 젤리가 보인다.
    눈은 ^^ 로 골골, 꼬리 끝이 까딱"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(16.0, 15.0, 0.0, 0.9)
        pl, pr_ = max(0.0, math.sin(ph)), max(0.0, -math.sin(ph))   # 왼발 · 오른발 누른 정도
        hc = (0.0, -6.8 + 0.3 * (pl + pr_))
        paws = []
        for sg, pd in ((-1, pl), (1, pr_)):
            lift = 1.0 - pd
            paws += arm_part([(sg * 3.0, 0.6), (sg * 3.4, 8.4 - 3.6 * lift)], r=1.7, pr=2.0 + 0.4 * pd,
                             name=f"p{sg}", fur=ORNG if sg < 0 else WHITE, lined=False)
        tw = 0.8 * math.sin(2 * ph)
        tail = tail_part([(6.6, 7.2), (10.4, 6.0), (12.0 + tw * 0.4, 2.6 + tw)], 1.7, 1.4, lined=True)
        dent = [sg for sg, pd in ((-1, pl), (1, pr_)) if pd > 0.5]

        def blanket(a, b, dent=dent):
            for sg in dent:
                if abs(a - sg * 3.4) < 2.6 and b < 9.4:
                    return BLANK_D
            if b < 8.6:
                return BLANK_L
            return BLANK if (a + 30) % 4.0 < 2.6 else BLANK_D
        blank_hit = lambda a, b: ell(0, 10.6, 14.4, 3.4)(a, b) and not any(   # noqa: E731
            ell(sg * 3.4, 7.4, 2.2, 1.4)(a, b) for sg in dent)
        parts = paws + head_parts(hc, 6.8) + \
            [("haunch", any_of(ell(-5.4, 6.0, 3.0, 2.8), ell(5.4, 6.0, 3.0, 2.8)),
              lambda a, b: BLK if a > 0 else WHITE, True),
             body_part((0.0, 3.0), 7.4, 6.0), tail, ("blanket", blank_hit, blanket, True)]
        f, _, _ = draw(rig, parts)
        face(f, rig, hc, 6.8, "happy")
        whiskers(f, rig, hc, 6.8)
        for sg, pd in ((-1, pl), (1, pr_)):   # 든 발은 젤리가 아래로 보인다 · 누른 발 옆에 꾹 줄
            px, py = rig.world(sg * 3.4, 8.4 - 3.6 * (1.0 - pd))
            if pd < 0.3:
                dot(f, math.floor(px), math.floor(py) + 1, PINK)
                dot(f, math.floor(px) - 1, math.floor(py), PINK)
            if pd > 0.8:
                for q in ((math.floor(px) - 3, math.floor(py) + 1), (math.floor(px) + 3, math.floor(py) + 1)):
                    f.setdefault(q, BLANK_D)
        frames.append(finish(f))
    return frames


def hand() -> list[dict]:
    """배를 깔고 엎드린 식빵 삼색냥이 오른 앞발을 위로 쭉 내밀어 톡톡 — 누를 때(장 3–5, 9–11) 젤리가 벌어지고
    발 둘레에 톡 줄이 선다. 발끝은 그대로 두고 팔꿈치가 굽었다 펴진다. 발바닥 꼭대기가 핫스팟"""
    frames = []
    top = -19.2                       # 발바닥 꼭대기 (w) — 핫스팟이라 장마다 그대로
    for k, ph in enumerate(phases()):
        tap = k % 6 in (3, 4, 5)
        rig = Rig(18.0, 21.0, 0.0, 0.78)
        ra, rb = (3.9, 3.0) if tap else (3.3, 3.4)
        pc = (-6.4, top + rb)
        elbow = (-7.0 + (0.0 if tap else 0.6), -8.0 + (0.8 if tap else 0.0))
        pad = ("pad", ell(pc[0], pc[1], ra, rb), WHITE, True)
        arm = ("arm", chain([(-3.0, -0.4), elbow, (pc[0], pc[1] + 1.6)], 2.8, 2.6), WHITE, False)
        tail = tail_part([(9.6, 6.2), (12.6, 4.2 + 0.8 * math.sin(ph)), (12.8, 0.4 + math.sin(ph))], 1.7, 1.4)
        loaf = ("body", any_of(ell(0.6, 3.4, 10.6, 5.2), ell(0.6, 5.6, 11.2, 3.4)),
                patches(WHITE, (ell(-4.6, 1.4, 4.6, 3.2, -0.2), ORNG), (ell(7.4, 4.6, 3.8, 3.6), BLK)), False)
        paw2 = ("paw2", ell(3.6, 8.2, 2.6, 1.5), WHITE, True)
        parts = [pad] + head_parts((1.0, -4.8), 6.8, turn=0.4) + [arm, paw2, loaf, tail]
        f, _, _ = draw(rig, parts)
        bx, by = rig.cell(pc[0], pc[1] + 0.6)
        # 젤리: 큰 젤리 2×2 + 발가락 젤리 셋 (톡 할 때 벌어진다)
        for p in ((bx - 1, by), (bx, by), (bx - 1, by + 1), (bx, by + 1)):
            f[p] = PINK
        sp = 1 if tap else 0
        for tx, ty in ((-2 - sp, -1), (-1, -2 - sp), (0, -2 - sp), (1 + sp, -1)):
            f[bx + tx, by + ty] = PINK
        face(f, rig, (1.0, -4.8), 6.8, "happy" if tap else "open", turn=0.4)
        whiskers(f, rig, (1.0, -4.8), 6.8, turn=0.4, skip=(-1,))
        if tap:   # 톡 — 발 양옆 짧은 줄
            for p in ((bx - 6, by - 1), (bx - 6, by - 3), (bx + 5, by - 1), (bx + 5, by - 3)):
                f.setdefault(p, OUT)
        frames.append(finish(f))
    return frames
    return frames


def cross() -> list[dict]:
    """앞모습 얼굴 — 볼 수염이 가로 조준선, 머리 위로 늘어진 낚싯대 장난감 줄과 턱 밑 줄이 세로선. 코가 핫스팟.
    줄 끝 깃털 장난감이 위에서 까딱이고 눈이 가끔 깜빡"""
    frames = []
    rig = Rig(15.5, 16.4, 0.0, 1.0)
    hc = (0.0, -0.4)
    for k, ph in enumerate(phases()):
        f = {}
        tw = round(0.6 * math.sin(2 * ph))
        for x in range(1, 31):
            if x < 7 or x > 24:
                f[x, 15] = OUT
        for sg in (-1, 1):
            f[15 + sg * 10, 14 - tw] = OUT
            f[15 + sg * 10, 16 + tw] = OUT
        for y in list(range(1, 4)) + list(range(25, 31)):
            f[15, y] = OUT
        f.update(head_only(rig, hc, 7.4, "blink" if k == 8 else "open", whisk=False))
        frames.append(finish(f))
    return frames


def ibeam() -> list[dict]:
    """스크래처 기둥이 I — 위 뚜껑 · 아래 받침이 I 의 가로획이다. 오른쪽에서 뒷발로 서서 기둥을 끌어안고 두 앞발을
    번갈아 박박 긁는다(긁는 발 자리에 짙은 긁힘 줄). 핫스팟은 기둥 가운데"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for y in range(4, 28):    # 기둥: 4칸 폭 삼줄
            for x in range(13, 17):
                f[x, y] = OUT if x in (13, 16) else (SISAL_D if (y + (x == 15)) % 2 else SISAL)
        for x in range(10, 20):   # 뚜껑 · 받침
            for y in (2, 3):
                f[x, y] = OUT if y == 2 or x in (10, 19) else POST
            for y in (28, 29):
                f[x, y] = OUT if y == 29 or x in (10, 19) else POST
        f[10, 3] = f[19, 3] = OUT
        sc = math.sin(2 * ph)
        rig = Rig(21.0, 17.0, 0.0, 0.62)
        hc = (1.0, -10.0)
        # 턱시도냥과 같은 박자 — 한 앞발이 기둥 높이 박혀 아래로 죽 긁어내리는 동안 다른 앞발은 떼어 위로 올린다.
        # 두 발이 사인으로 마주 오가면 펌프질로 읽힌다
        paws, marks = [], []
        for i in range(2):
            t = (k / 6 + i / 2) % 1
            if t < 0.66:
                tip = (-9.2, -8.0 + 11.0 * t / 0.66)
                marks.append(tip)
            else:
                tip = (-7.6, 3.0 - 11.0 * (t - 0.66) / 0.34)
            paws += arm_part([(-2.0, -1.0 + i * 3.0), tip], r=1.8, pr=2.0, name=f"a{i}")
        parts = paws + head_parts(hc, 6.6, turn=-0.8) + \
            [("body", ell(1.0, 4.0, 5.6, 8.0),
              patches(WHITE, (ell(-2.0, 0.6, 3.6, 3.4), ORNG), (ell(3.6, 8.6, 3.4, 3.8), BLK)), False),
             ("feet", ell(0.0, 12.6, 4.4, 1.6), WHITE, True),
             tail_part([(5.0, 10.0), (9.0, 9.0), (10.0, 4.0 + 1.0 * sc)], 1.7, 1.4)]
        o, _, _ = draw(rig, parts)
        f.update(o)
        face(f, rig, hc, 6.6, "happy" if k % 6 < 3 else "open", turn=-0.8)
        for a, b in marks:   # 긁는 발이 지나온 자리에 삼줄이 일어난 흰 자국
            _, y0 = rig.cell(a, -8.0)
            _, y1 = rig.cell(a, b)
            for y in range(y0, y1):
                if f.get((14, y)) not in (None, OUT) and (14, y) not in o:
                    f[14, y] = hx("fff4dcff")
        frames.append(finish(f))
    return frames


def box_cat(rig: Rig, flap=1.0, mood="open", peek=1.0, paws=True, scale_box=(-7.0, 7.0, 0.0, 9.0)) -> dict:
    """상자에 쏙 들어간 삼색냥(앞모습) — 머리만 상자 위로, 두 앞발은 상자 턱에. peek 은 머리가 올라온 정도(0–1)"""
    a0, a1, b0, b1 = scale_box
    hc = (0.0, b0 + 3.6 - 8.0 * peek)
    front = box_parts(a0, a1, b0, b1, flap, inside_=False)
    head = head_parts(hc, 6.4)
    pw = [("paws", any_of(ell(-3.2, b0 + 0.2, 1.9, 1.3), ell(3.2, b0 + 0.2, 1.9, 1.3)), WHITE, True)] if paws else []
    inner = ("box_in", box_hit(a0 + 0.6, b0 - 1.8, a1 - 0.6, b0 + 0.6), BOX_IN, False)
    parts = pw + [front[0]] + ([front[1]] if flap < 0.5 else []) + head + ([front[1]] if flap >= 0.5 else []) + [inner]
    f, _, region = draw(rig, parts)
    # 머리 중 상자 앞판에 가린 칸은 draw 가 이미 앞판 색으로 칠했다. 얼굴은 보이는 칸에만
    g = {}
    face(g, rig, hc, 6.4, mood)
    for p, c in g.items():
        if region.get(p) == "head":
            f[p] = c
    return f


def move() -> list[dict]:
    """상자에 쏙 들어간 삼색냥이 상자째 좌우로 들썩들썩 — 네 방향 분홍 화살촉이 바깥으로 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy, GLOW[0], 3)
        hop = -abs(math.sin(2 * ph)) * 1.0
        tilt = 6.0 * math.sin(2 * ph)
        rig = Rig(15.5, 17.0 + hop, tilt, 0.78)
        f.update(box_cat(rig, 0.9, "blink" if k == 4 else "open", scale_box=(-7.4, 7.4, 0.0, 8.6)))
        frames.append(finish(f))
    return frames


def no() -> list[dict]:
    """빨간 금지 표지 안에서 상자에 든 삼색냥이 날개를 닫아 버린다 — 장 0–2 빼꼼 · 3–4 닫는 중 · 5–9 닫힘(귀 끝만)
    · 10–11 다시 빼꼼"""
    frames = []
    #        0    1    2    3    4    5    6    7    8    9    10   11
    flaps = [1.0, 1.0, 1.0, 0.6, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.8]
    peeks = [0.8, 0.8, 0.8, 0.5, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.6]
    for k in range(N):
        f = {}
        rig = Rig(15.5, 16.4, 0.0, 0.74)
        o = box_cat(rig, flaps[k], "peek" if peeks[k] < 0.7 else "open", peeks[k], paws=peeks[k] > 0.5)
        f.update(o)
        sign(f)
        frames.append(finish(f))
    return frames


def pen() -> list[dict]:
    """붓을 두 앞발로 쥐고 먹 글씨를 쓴다 — 붓은 붓끝(왼쪽 아래)을 축으로 까딱이고, 붓끝 오른쪽으로 먹 줄이 차츰
    길어진다. 붓끝이 핫스팟"""
    frames = []
    TIP = (4, 27)
    for k, ph in enumerate(phases()):
        d = 4.0 * math.sin(2 * ph)
        br = Rig(TIP[0] + 0.5, TIP[1] + 0.5, -48.0 + d, 1.0)     # 붓대가 오른쪽 위로
        brush = [("hair", any_of(tri((0, 0), (3.4, -1.4), (3.4, 1.4)), bar((3.4, 0), (4.4, 0), 1.4)), INKC, True),
                 ("ferrule", bar((4.8, 0), (5.8, 0), 1.3), BRUSH_D, True),
                 ("stick", bar((5.8, 0), (20.0, 0), 1.0), lambda a, b: BRUSH_D if b > 0.3 else BRUSH, False)]
        o, _, _ = draw(br, brush)
        rig = Rig(21.6, 19.6, 0.0, 0.7)
        hc = (0.0, -10.4)
        p1, p2 = rig.local(*br.world(11.0, 0.0)), rig.local(*br.world(14.6, 0.0))
        back = head_parts(hc, 6.8, turn=-0.8) + \
            [("arm1", bar((-3.4, 1.0), p1, 1.8), WHITE, True), ("arm2", bar((-2.6, -2.4), p2, 1.8), ORNG, True),
             ("body", ell(0.6, 2.8, 6.4, 7.0),
              patches(WHITE, (ell(-2.2, -1.6, 3.6, 3.0), ORNG), (ell(5.0, 6.4, 3.6, 3.4), BLK)), False),
             tail_part([(5.4, 8.4), (10.0, 7.4), (11.4 + 0.6 * math.sin(ph), 3.0)], 1.6, 1.3)]
        f, _, _ = draw(rig, back)
        face(f, rig, hc, 6.8, "blink" if k == 6 else "open", turn=-0.8)
        whiskers(f, rig, hc, 6.8, turn=-0.8, skip=(-1,))
        f.update(o)
        paws, _, _ = draw(rig, [("pa", ell(*p1, 2.2, 2.0), WHITE, True), ("pb", ell(*p2, 2.2, 2.0), WHITE, True)])
        f.update(paws)
        for i in range(2 + k):   # 먹 줄: 붓끝 오른쪽으로 물결치며 길어진다
            f.setdefault((TIP[0] + 2 + i, 29 - (1 if (i // 2) % 2 else 0)), INKC)
        f[TIP] = INKC
        frames.append(finish({p: v for p, v in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}))
    return frames


def up() -> list[dict]:
    """상자에서 쏙 일어서 왼 앞발(주황)을 머리 위로 번쩍 — "저요!". 다른 앞발은 상자 턱에, 상자 날개가 들썩이고
    꼬리가 상자 뒤로 살랑, 눈이 가끔 깜빡. 든 발끝(맨 위)이 핫스팟이라 그 발은 안 움직인다.
    처음엔 두 앞발을 머리 위로 모았는데 두 팔이 귀 사이로 솟은 기둥(양초)으로 읽혔다"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(15.5, 21.0, 0.0, 0.74)
        flap = 0.8 + 0.2 * math.sin(2 * ph)
        a0, a1, b0, b1 = -8.0, 8.0, 1.0, 11.0
        front = box_parts(a0, a1, b0, b1, flap, inside_=False)
        hc = (0.0, -6.8)
        arms = [("paw", ell(-8.8, -19.4, 2.6, 2.4), WHITE, True),
                ("arm", bar((-4.6, -1.0), (-8.6, -17.6), 2.2, 2.0), ORNG, True)]
        rest = ("rest", ell(3.6, b0 + 0.1, 2.2, 1.4), WHITE, True)    # 다른 앞발은 상자 턱에
        tail = tail_part([(6.0, 2.0), (10.6, -1.0 + math.sin(ph)), (11.6 + 0.5 * math.sin(ph), -5.0)], 1.7, 1.4)
        parts = [rest, front[0], arms[0]] + head_parts(hc, 6.6) + [arms[1], front[1]] + \
            [("body", ell(0.0, 1.6, 5.8, 6.6), patches(WHITE, (ell(-3.6, -0.6, 3.0, 2.8), ORNG)), False), tail,
             ("box_in", box_hit(a0 + 0.6, b0 - 1.8, a1 - 0.6, b0 + 0.6), BOX_IN, False)]
        f, _, _ = draw(rig, parts)
        face(f, rig, hc, 6.6, "blink" if k == 9 else "open")
        frames.append(finish(f))
    return frames


def arrows2(f: dict, dx: int, dy: int, ph: float) -> None:
    """크기 조절 칸 양 끝의 분홍 화살촉 — 늘어날 때 한 칸 바깥으로 두근"""
    R = 14 if dx == 0 or dy == 0 else 11
    o = 1 if math.sin(ph) > 0.3 else 0
    for sg in (-1, 1):
        chevron(f, 15 + sg * dx * (R + o), 15 + sg * dy * (R + o), sg * dx, sg * dy, GLOW[0] if o else GLOW[1], 3)


def long_loaf(ang: float) -> list[dict]:
    """길쭉한 식빵 — 배를 깔고 엎드린 삼색냥 몸통이 ang 축(도, 0 이면 머리가 왼쪽)으로 길게 늘었다 줄었다 한다.
    머리는 한쪽 끝에 늘 똑바로(기울이면 칸 위에서 뭉개진다), 앞발 · 뒷발은 몸통 아래쪽으로 뭉툭하게, 까만 꼬리는
    끝에서 위로 말려 살랑. 처음엔 앞발을 머리 너머로 뻗은 기지개였는데 머리 위로 솟은 두 앞발이 토끼 귀로,
    가는 몸통 양 끝에 머리 · 발이 달린 것은 뼈다귀로 읽혀서 몸통을 머리만큼 두툼하게 했다"""
    frames = []
    t = math.radians(ang)
    dx, dy = round(math.cos(t)), round(math.sin(t))
    sd = 1 if math.cos(t) >= 0 else -1          # 몸통의 아래쪽(발 쪽)이 화면 아래로 가게
    for k, ph in enumerate(phases()):
        f = {}
        arrows2(f, dx, dy, ph)
        s = 1.6 * math.sin(ph)
        rig = Rig(15.5, 15.5, ang, 0.74)
        e = 7.4 + s                                       # 몸통 끝
        body = ("body", bar((-4.0, 0.0), (e, 0.0), 4.6, 4.4),
                patches(WHITE, (ell(0.6, -sd * 2.6, 3.4, 2.4), ORNG), (ell(e - 1.4, sd * 1.6, 2.8, 3.0), BLK)), False)
        paws = []
        for i, u in enumerate((-2.0, 0.8, e - 2.6, e - 0.2)):
            paws.append((f"paw{i}", ell(u, sd * 4.4, 1.6, 1.3), WHITE, True))
        tw = 0.8 * math.sin(2 * ph)
        tail = tail_part([(e + 1.0, -sd * 0.6), (e + 3.6, -sd * 1.6), (e + 4.4 + tw, -sd * 4.4)], 1.4, 1.2)
        o, _, _ = draw(rig, paws + [body, tail])
        f.update(o)
        hr = Rig(*rig.world(-5.4, 0.0), 0.0, 0.74)
        f.update(head_only(hr, (0.0, 0.0), 6.6, "happy" if k % 6 < 2 else "open", whisk=False))
        frames.append(finish({p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}))
    return frames


def ns() -> list[dict]:
    """막대에 두 앞발로 매달린 삼색냥 — 몸이 축 늘어졌다 줄었다 하고 뒷발 · 꼬리가 대롱대롱. 위아래 화살촉.
    앞발은 머리 바깥으로 올려 막대를 쥔다(머리 위 한가운데로 솟으면 토끼 귀가 된다)"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        arrows2(f, 0, 1, ph)
        s = 1.6 * math.sin(ph)
        rig = Rig(15.5, 11.4, 0.0, 0.74)
        for x in range(8, 24):    # 막대
            f[x, 4] = OUT
            f[x, 5] = BRUSH_D if x in (8, 23) else BRUSH
            f[x, 6] = OUT
        f[8, 5] = f[23, 5] = OUT
        e = 12.0 + s
        arms = []
        for sg in (-1, 1):
            arms += arm_part([(sg * 5.0, 3.6), (sg * 8.6, -2.0), (sg * 8.4, -8.4)], r=1.6, pr=1.8, name=f"a{sg}",
                             fur=ORNG if sg < 0 else WHITE)
        legs = []
        sw = 0.6 * math.sin(2 * ph)
        for sg in (-1, 1):
            legs += arm_part([(sg * 2.4, e - 1.0), (sg * 2.6 + sw, e + 2.6)], r=1.5, pr=1.7, name=f"l{sg}")
        tail = tail_part([(1.0, e), (3.6 + sw, e + 2.6), (5.4 + 2 * sw, e + 0.6)], 1.3, 1.1)
        body = ("body", bar((0.0, 3.0), (0.0, e - 0.6), 4.8, 4.4),
                patches(WHITE, (ell(-2.4, 5.2, 3.0, 3.0), ORNG), (ell(2.4, e - 2.4, 2.8, 3.2), BLK)), False)
        o, _, _ = draw(rig, arms + legs + [body, tail])
        f.update(o)
        f.update(head_only(rig, (0.0, 0.0), 6.6, "happy" if k % 6 < 2 else "open", whisk=False))
        frames.append(finish({p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}))
    return frames


def we():
    return long_loaf(0.0)


def nwse():
    return long_loaf(45.0)


def nesw():
    return long_loaf(135.0)


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def top_cell(fr):
    return min((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1], p[0]))


HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1),
       "wait": (16, 16), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (15, 15), "pen": (4, 27),
       "hand": top_cell, "up": top_cell}


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

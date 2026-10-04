# SPDX-License-Identifier: Apache-2.0
"""고등어냥(mackerelcatanim) 구성표 그림 `art/mackerelcatanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/mackerelcat.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

해달처럼 칸마다 고등어냥이 하는 짓을 따로 그린다(`SCENE`). 같은 묶음(치즈냥 · 턱시도냥 · 까망이 · 삼색냥)과
머리 비율(반지름 7 · 세모 귀 · ㅅ 입 · 볼터치 · 1칸 수염)을 맞추되, 고등어냥은 날씬한 몸 · 조금 더 높이 선 귀 ·
길고 가는 고리 무늬 꼬리로 실루엣을 가른다. 회색 바탕(9a9ca4)에 짙은 회색 줄 — 이마의 M 무늬, 볼에 가로 줄 둘,
몸 · 꼬리에 굵은 가로 줄(32칸에서 잘면 회색 덩어리라 2–3개로 굵게) · 흰 주둥이와 가슴은 조금 · 초록 눈 · 회색 발.
화살촉 같은 신호색은 눈 색(초록)이다.

  arrow   큰 흰 화살표 뒤에 숨은 고등어냥이 빗변 위로 빼꼼 — 회색 발끝 둘이 빗변을 잡고 장 2–5 에 쏙 더
          올라온다 · 10 에 깜빡. 화살표 끝이 핫스팟(`sea.peek`, 냥이 10종 공용 틀)
  busy    작은 화살표 고등어냥 + 오른쪽 아래 물그릇 둘레를 도는 젖은 발자국 여덟 개(물그릇에 발을 담갔다)
  cross   앞모습 얼굴 — 사냥 눈(동공이 커졌다 줄었다). 긴 수염이 가로 조준선, 귀 사이 · 턱 밑 초록 눈금이 세로선.
          코가 핫스팟
  hand    엎드린 고등어냥이 앞발 하나를 왼쪽 위로 내밀어 발톱 하나로 톡톡 — 발톱 끝이 핫스팟
  help    작은 화살표 고등어냥이 제 꼬리로 물음표를 그린다 — 엉덩이에서 나온 꼬리가 고리를 돌아 내려온다(점은 초록 공)
  ibeam   I 꼴 스크래쳐(위아래 판 · 노끈 기둥)를 두 앞발로 벅벅 긁는다 — 기둥이 I, 핫스팟은 기둥 가운데
  move    납작 엎드려 네 발을 사방으로 쭉 뻗은(위에서 본) 고등어냥 — 등의 가로 줄이 고등어 같다. 네 방향 초록 화살촉
  nesw · ns · nwse · we   롱캣 — 머리를 한쪽 끝에 두고 몸이 그 축으로 쭉 늘었다 줄었다. 반대 끝은 뒷발과 꼬리.
          양 끝 초록 화살촉이 두근댄다. 얼굴은 늘 똑바로 둔다(기운 얼굴은 칸 위에서 뭉개진다)
  no      빨간 금지 표지 안에서 등을 돌리고 앉은 고등어냥(쌩) — 꼬리를 탁탁 치다가 어깨 너머로 힐끔 본다
  pen     연필을 입에 물고 쓰는 고등어냥 — 연필심(왼쪽 아래)이 핫스팟, 지나간 자리에 연필 줄이 남는다
  person  작은 화살표 고등어냥 + 고등어냥을 품에 꼭 안은 사람. 소매가 냥이 배를 감싸고 아래로 삐져나온 꼬리가 흔들린다
  pin     작은 화살표 고등어냥 + 흰 발자국이 찍힌 빨간 지도 핀이 통통 튄다
  up      뒷발로 꼿꼿이 서서 한 앞발을 머리 위로 쭉 뻗는다(저요!) — 발끝(맨 위)이 핫스팟. 눈은 위를 본다
  wait    앉아서 그루밍 — 앞발을 핥다가(혀 날름) 그 발로 얼굴을 쓱 닦는다. 꼬리는 발을 감싸고 끝만 까딱. 가운데가 핫스팟

몸은 부위(타원 · 굵기가 변하는 막대 · 세모)를 고양이 제 좌표 (u 오른쪽, w 아래)에 놓고 화면으로 돌려 찍는다
(`Rig`, `draw` — 치즈냥 생성기와 같은 방식이지만 다른 생성기에 기대지 않게 여기 따로 둔다).
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, SIGN, SIGN_D, disc, finish, hx, ink, inside, peek, peek_tail, phases, raster, solid, write

SID = "mackerelcatanim"

OUT, EYE = hx("34353dff"), hx("1c1d22ff")                       # 테두리 · 눈동자
FUR, FUR_L, STRIPE = hx("9a9ca4ff"), hx("b9bbc2ff"), hx("666871ff")   # 회색 · 밝은 회색(발) · 짙은 줄
CREAM, PINK, NOSE, HI = hx("f4f3eeff"), hx("f4a0b0ff"), hx("e27d90ff"), hx("ffffffff")
GREEN = hx("6cc04aff")                                          # 눈
ink(OUT, HI, hx("e8eaf0c7"))
GLOW = (hx("6cc04aff"), hx("6cc04ab0"), hx("6cc04a60"))         # 화살촉 · 조준 눈금 (짙은 것부터)
WET = (hx("5aa8d8ff"), hx("5aa8d8b0"), hx("5aa8d860"))          # 젖은 발자국
BOWL, BOWL_D, WATER, WATER_L = hx("e07a5aff"), hx("b0553cff"), hx("7cc4e8ff"), hx("c8ecfaff")
SISAL, SISAL_D, PLATE, PLATE_D = hx("e0c08cff"), hx("b8925aff"), hx("8a6a52ff"), hx("6a4e3cff")
PENCIL, PENCIL_D, WOOD, LEAD = hx("f5c842ff"), hx("c8961cff"), hx("efd2a8ff"), hx("3a3a3aff")
ERASER, FERRULE = hx("f2a0a8ff"), hx("b8b8c0ff")
SKIN, HAIR = hx("f7d7bcff"), hx("6a4a3aff")
SHIRT, SHIRT_D = hx("e8a33aff"), hx("c07e22ff")                 # 사람 옷 (회색 냥이와 갈리게 주황)
BALL = hx("6cc04aff")


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
    return at, acc


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
HC, HR = (0.0, -7.5), 7.0       # 머리 가운데 · 반지름 (묶음 공통)


def head_parts(hc=HC, r=HR, turn=0.0, name="head", back=False) -> list:
    """앞모습 머리: 퍼진 볼 · 높이 선 세모 귀(속 분홍) · 흰 주둥이 · 볼에 가로 줄 둘. M 무늬는 `face` 가 칸으로 찍는다.
    back 이면 뒤통수 — 귀 속이 안 보이고 정수리에서 목덜미로 짙은 줄 셋이 내려온다"""
    u0, w0 = hc
    head = any_of(ell(u0, w0 - 0.4, r * 0.98, r * 0.86), ell(u0, w0 + 1.0, r * 1.08, r * 0.62))
    ears, inner = [], []
    for sg in (-1, 1):
        base0, tip, base1 = (u0 + sg * r * 0.98, w0 - r * 0.24), (u0 + sg * r * 0.8 + turn * 0.3, w0 - r * 1.42), \
            (u0 + sg * r * 0.16, w0 - r * 0.78)
        ears.append(tri(base0, tip, base1))
        cx, cy = (base0[0] + tip[0] + base1[0]) / 3, (base0[1] + tip[1] + base1[1]) / 3 + r * 0.06
        inner.append(tri(*[(cx + (p[0] - cx) * 0.46, cy + (p[1] - cy) * 0.46) for p in (base0, tip, base1)]))
    inner_hit = any_of(*inner)

    def skin(a, b):
        mu = a - u0 - turn
        if back:
            if b < w0 + r * 0.5 and any(abs(mu - d * r * 0.34) < r * 0.1 for d in (-1, 0, 1)):
                return STRIPE
            return FUR
        if (mu / (r * 0.4)) ** 2 + ((b - (w0 + r * 0.38)) / (r * 0.27)) ** 2 <= 1:
            return CREAM
        if abs(mu) > r * 0.74 and any(abs(b - (w0 + r * dd)) < r * 0.08 for dd in (0.0, 0.26)):
            return STRIPE
        return FUR

    def ear_col(a, b):
        return FUR if back else PINK if inner_hit(a, b) else FUR
    return [(name, head, skin, True), (name + "_ear", any_of(*ears), ear_col, False)]


def body_part(c=(0.0, 3.0), ra=5.8, rb=6.2, chest=True, name="body", rot=0.0, stripes="across"):
    """날씬한 몸 — 가슴에 흰 털 조금, 옆구리에 굵은 짙은 줄. rot 으로 기울인 몸은 줄도 같이 돈다"""
    c0, c1 = c
    cs, sn = math.cos(rot), math.sin(rot)

    def col(a, b):
        da, db = a - c0, b - c1
        u, v = da * cs + db * sn, -da * sn + db * cs
        if chest and (da / (ra * 0.42)) ** 2 + ((db + rb * 0.62) / (rb * 0.24)) ** 2 <= 1:
            return CREAM
        if stripes == "across":      # 앞모습: 옆구리 가로 줄
            if abs(da) > ra * 0.5 and (db + 0.8) % 4.0 < 1.5:
                return STRIPE
        elif stripes == "along":     # 기울인 몸: 몸 축을 가로지르는 줄
            if (u + 0.6) % 4.2 < 1.6 and abs(v) < rb * 0.9:
                return STRIPE
        return FUR
    return (name, ell(c0, c1, ra, rb, rot), col, False)


def tail_part(pts, r0=1.9, r1=1.5, name="tail", lined=False):
    """길고 가는 꼬리 — 굵은 짙은 고리, 끝은 짙게"""
    at, total = along(pts)

    def col(a, b):
        s = at(a, b)
        if s > total - 0.9:
            return STRIPE
        return STRIPE if (s % 3.6) > 2.2 and s > 1.2 else FUR
    return (name, chain(pts, r0, r1), col, lined)


def leg_part(pts, r=2.0, pr=2.1, name="arm", lined=True):
    """다리 하나 → [발, 다리]. 발은 밝은 회색(고등어냥은 흰 양말이 없다), 다리에 줄 하나"""
    at, total = along(pts)
    paw = (name + "_paw", ell(*pts[-1], pr, pr * 1.0), FUR_L, True)

    def col(a, b):
        s = at(a, b)
        return STRIPE if total > 9.0 and abs(s - total * 0.55) < 0.7 else FUR
    return [paw, (name, chain(pts, r, r * 0.92), col, lined)]


def dot(f: dict, x: int, y: int, c: tuple) -> None:
    f[x, y] = c


M_MARK = ["#...#", "##.##", "#.#.#"]


def face(f: dict, rig: Rig, hc=HC, r=HR, mood="open", turn=0.0, look=(0, 0), mark=True) -> None:
    """얼굴: 2×2 초록 눈(흰 반짝 · 짙은 동공) · 분홍 코 · ㅅ 입 · 볼터치 · 이마 M 무늬. 작게(k·r < 5) 그리면 눈 1×2 · 코 1칸.
    mood: open · blink · sleep(︶) · happy(^) · lick(^ 에 입 벌림). look 은 동공을 옮길 칸 (dx, dy)"""
    u0, w0 = hc
    small = rig.k * r < 4.5
    for sg in (-1, 1):
        ex, ey = rig.world(u0 + turn + sg * r * 0.42, w0 - r * 0.06)
        if small:
            x0, y0 = math.floor(ex), math.floor(ey - 0.5)
            if mood == "open":
                dot(f, x0, y0, GREEN)
                dot(f, x0, y0 + 1, EYE)
            else:
                dot(f, x0, y0 + 1, EYE)
            continue
        x0, y0 = round(ex - 1), round(ey - 1)
        if mood == "open":
            for dx in (0, 1):
                for dy in (0, 1):
                    dot(f, x0 + dx, y0 + dy, GREEN)
            px = x0 + (1 if look[0] >= 0 else 0)
            py = y0 + (1 if look[1] >= 0 else 0)
            dot(f, px, py, EYE)
            dot(f, x0 + (0 if px > x0 else 1), y0 + (0 if py > y0 else 1), HI)
        elif mood == "blink":
            dot(f, x0, y0 + 1, EYE)
            dot(f, x0 + 1, y0 + 1, EYE)
        elif mood == "sleep":
            dot(f, x0, y0 + 1, EYE)
            dot(f, x0 + 1, y0 + 1, EYE)
            dot(f, x0 - 1 if sg < 0 else x0 + 2, y0, EYE)
        elif mood in ("happy", "lick"):
            dot(f, x0 - 1 if sg < 0 else x0, y0 + 1, EYE)
            dot(f, x0 if sg < 0 else x0 + 1, y0, EYE)
            dot(f, x0 + 1 if sg < 0 else x0 + 2, y0 + 1, EYE)
    if mark and not small:   # 이마 M — 머리 위쪽 털 칸에만
        mx, my = rig.world(u0 + turn, w0 - r * 0.66)
        x0, y0 = round(mx) - 3, round(my) - 1
        for j, row in enumerate(M_MARK):
            for i, ch in enumerate(row):
                if ch == "#" and f.get((x0 + i, y0 + j)) == FUR:
                    f[x0 + i, y0 + j] = STRIPE
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
        bx, by = rig.world(u0 + turn + sg * r * 0.64, w0 + r * 0.24)
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
            x0, y0 = rig.world(u0 + turn + sg * r * 1.12, w0 + r * dw)
            for i in range(n + 1):
                x = math.floor(x0 + sg * i)
                y = math.floor(y0 + (i * 0.4 * (j * 2 - 1) if j else 0) + (tw if i == n else 0))
                if (x, y) not in f:
                    f[x, y] = OUT


def anchor(frames: list[dict], target=(1, 1)) -> tuple[list[dict], tuple]:
    """맨 왼쪽 위 불투명 칸(x+y 가 가장 작은 것, 같으면 위)을 target 으로 옮긴다 — 화살표 꼴 칸의 발끝"""
    tip = min((p for p, c in frames[0].items() if c[3] == 255), key=lambda p: (p[0] + p[1], p[1]))
    dx, dy = target[0] - tip[0], target[1] - tip[1]
    return [{(x + dx, y + dy): c for (x, y), c in f.items()} for f in frames], (dx, dy)


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col, n: int = 3) -> None:
    """(dx, dy) 쪽을 가리키는 화살촉. 꼭짓점이 (cx, cy)"""
    if dx and dy:   # 대각선은 꺾쇠(┘ 꼴) — 비스듬한 V 는 칸 위에서 점선이 된다
        for i in range(n + 1):
            for w in (0, 1):
                f.setdefault((cx - dx * i, cy - dy * w), col)
                f.setdefault((cx - dx * w, cy - dy * i), col)
        return
    px, py = -dy, dx
    for i in range(n):
        for s in (-1, 1):
            for w in (0, 1):
                f.setdefault((cx - dx * (i + w) + s * px * i, cy - dy * (i + w) + s * py * i), col)


# ── 화살표 고등어냥 ──────────────────────────────────────────────────────────
TAIL0 = (5.0, 7.4)       # 하이파이브 고등어냥 꼬리 밑동 (help 가 여기서 물음표 꼬리를 뺀다)
HI5 = (-11.0, -15.4)     # 번쩍 든 앞발 가운데 — 귀 끝(w -17.4)보다 발 위끝이 높아야 발이 맨 왼쪽 위다
NYANG = (4, 5, 6)        # "냥!" 하는 장 — 발끝으로 몸을 쭉 펴고 ^^ 눈에 입을 벌린다


def squircle(cu, cw, r, p=2.8):
    """모서리가 조금 찬 동그라미 — 든 앞발. 원이면 왼쪽 위 모서리 칸이 비어 발끝(핫스팟)이 한 칸으로 안 선다"""
    return lambda a, b: abs((a - cu) / r) ** p + abs((b - cw) / r) ** p <= 1


def beans(f: dict, region: dict, name: str) -> None:
    """든 앞발 바닥에 분홍 젤리 — 위에 발가락 셋, 아래에 큰 젤리. 발 속(테두리 뺀 칸)이 좁으면 큰 젤리 한 칸만"""
    cells = [p for p, r in region.items() if r == name and f.get(p) != OUT]
    if not cells:
        return
    rows = {}
    for x, y in cells:
        rows.setdefault(y, []).append(x)
    full = sorted(y for y, xs in rows.items() if len(xs) >= 5)
    if len(full) >= 4:   # 발가락 셋은 넉넉한 첫 줄, 큰 젤리는 끝 두 줄
        cx = (min(rows[full[0]]) + max(rows[full[0]])) // 2
        pads = [(cx + d, full[0]) for d in (-2, 0, 2)] + [(cx + d, y) for y in full[-2:] for d in (-1, 0, 1)]
    else:
        ys = sorted(rows)
        y = ys[len(ys) // 2]
        pads = [((min(rows[y]) + max(rows[y])) // 2, y)]
    for p in pads:
        if p in cells:
            f[p] = PINK


def arrow_cat(ph: float, k: float = 0.8, mood="open", lift=0.0, tail=True) -> tuple[dict, Rig]:
    """하이파이브 고등어냥 — 큰 머리 · 동그란 몸으로 앞을 보고 앉아 왼 앞발을 머리 옆으로 번쩍 든다(손바닥 젤리가 보인다).
    발은 핫스팟이라 그 자리에 두고, "냥!" 하는 장(lift)에 발끝으로 몸을 쭉 편다. 다른 앞발은 가슴 앞, 짧고 통통한
    꼬리가 오른쪽에서 살랑"""
    rig = Rig(16.0, 16.0, 0.0, k)
    sw = math.sin(ph)
    up = -lift
    hc = (HC[0], HC[1] + up)
    small = k < 0.7      # 작게 그리면 팔 · 발을 굵혀야 테두리에 먹히지 않고 회색 속이 남는다
    paw = ("hi5_paw", squircle(*HI5, 4.6 if small else 3.8, 5.0), FUR_L, True)
    arm = leg_part([(-5.0, -0.6 + up), (-10.2, -5.0 + up * 0.5), (HI5[0], HI5[1] + 2.0)], name="hi5",
                   r=3.0 if small else 2.3, lined=False)[1]
    feet = ("feet", any_of(ell(-3.8, 9.0, 2.2, 1.5), ell(4.0, 9.0, 2.2, 1.5)), FUR_L, True)
    haunch = ("haunch", any_of(ell(-4.0, 6.6 + up * 0.5, 2.5, 2.5), ell(4.2, 6.6 + up * 0.5, 2.5, 2.5)), FUR, True)
    body = body_part((0.2, 3.6 + up * 0.7), 5.0, 5.2 + lift * 0.3)
    parts = [paw] + head_parts(hc) + [arm, feet, haunch, body]
    if tail:
        parts.append(tail_part([TAIL0, (9.4, 5.6), (10.2 + 0.9 * sw, 1.2 - 0.4 * sw)], 2.0, 1.8))
    out, mask, region = draw(rig, parts)
    # 발끝: 그림 전체의 맨 왼쪽 · 맨 위가 만나는 칸을 채워 핫스팟을 한 칸으로 세운다
    xs = min(x for x, _ in mask)
    ys = min(y for _, y in mask)
    own = [p for p, r in region.items() if r == "hi5_paw"]
    assert min(x for x, _ in own) == xs and min(y for _, y in own) == ys, "든 앞발이 맨 왼쪽 위가 아님"
    x, y = xs, ys
    while (x, ys) not in mask:     # 위 변을 발 끝까지 잇는다
        out[x, ys] = OUT
        x += 1
    while (xs, y) not in mask:     # 왼 변도
        out[xs, y] = OUT
        y += 1
    beans(out, region, "hi5_paw")
    face(out, rig, hc, mood="happy" if mood == "nyang" else mood, look=(-1, -1))
    if mood == "nyang" and k >= 0.7:   # 입을 벌려 "냥!" — ㅅ 입 자리에 분홍 입
        nx, ny = rig.world(hc[0], hc[1] + HR * 0.16)
        nl, ny = round(nx) - 1, math.floor(ny)
        out[nl, ny + 2] = PINK
        out[nl + 1, ny + 2] = PINK
    if k >= 0.7:
        whiskers(out, rig, hc, n=2, skip=(-1,))
    return out, rig


def arrow_frames(small=False, tail=True):
    fr = []
    for k, ph in enumerate(phases()):
        mood = "nyang" if k in NYANG else "blink" if k == 10 else "open"
        fr.append(arrow_cat(ph, 0.5 if small else 0.9, mood, 1.25 if k in NYANG else 0.0, tail)[0])
    return anchor(fr)


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    def head(x, y, k):
        rig = Rig(x - HC[0] * PEEK_K, y - HC[1] * PEEK_K, 0.0, PEEK_K)
        g, _, _ = draw(rig, head_parts() + [            # 꼬리는 오른쪽으로 길게 U 자
            ("feet", any_of(ell(-3.8, 9.0, 2.2, 1.5), ell(4.0, 9.0, 2.2, 1.5)), FUR_L, True),
            ("haunch", any_of(ell(-4.0, 6.6, 2.5, 2.5), ell(4.2, 6.6, 2.5, 2.5)), FUR, True),
            body_part((0.2, 3.6), 5.0, 5.2), tail_part(peek_tail(k))])
        face(g, rig, mood="blink" if k == 10 else "open", look=(-1, -1))
        whiskers(g, rig, n=2, skip=(-1,))
        return g
    return [finish(peek(k, head, OUT, FUR)) for k in range(N)]


PEEK_K = 0.74     # 빼꼼 고등어냥 배율


def companion(scene, tail=True) -> list[dict]:
    """작은 화살표 고등어냥 + scene(k, ph) 이 그리는 소품 — busy · help · person · pin"""
    cats, _ = arrow_frames(small=True, tail=tail)
    frames = []
    for k, ph in enumerate(phases()):
        f = scene(k, ph)
        f.update(cats[k])
        frames.append(finish(f))
    return frames


def paw_print(f: dict, cx: int, cy: int, col) -> None:
    """발자국: 2×2 큰 젤리 + 위에 발가락 넷 (묶음 공통 꼴)"""
    for p in ((cx, cy), (cx + 1, cy), (cx, cy + 1), (cx + 1, cy + 1), (cx - 1, cy - 1), (cx + 2, cy - 1),
              (cx, cy - 2), (cx + 1, cy - 2)):
        f[p] = col


def busy() -> list[dict]:
    """물그릇에 발을 담갔다 나온 젖은 발자국 여덟 개가 그릇 둘레를 돈다. 그릇 물이 찰랑인다"""
    cx, cy = 22.0, 22.0

    def scene(k, ph):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = round(cx + 6.8 * math.cos(a) - 0.5), round(cy + 6.8 * math.sin(a) - 0.5)
            lag = (head - i) % 8
            paw_print(f, x, y + 1, WET[0] if lag < 1.5 else WET[1] if lag < 3 else WET[2])
        bowl = {(x, y) for x in range(18, 26) for y in range(21, 25)
                if not ((x in (18, 25)) and y == 24)}
        solid(f, bowl, lambda p: BOWL_D if p[1] == 23 else BOWL)
        for x in range(19, 25):
            f[x, 21] = WATER
        f[19 + (k // 2) % 6, 21] = WATER_L
        return f
    return companion(scene)


def help_() -> list[dict]:
    """작은 화살표 고등어냥의 꼬리가 엉덩이에서 나와 물음표 고리를 돌아 내려온다 — 꼬리 끝이 살랑, 점은 초록 공"""
    _, (sx, sy) = arrow_frames(small=True)
    rig0 = Rig(16.0, 16.0, 0.0, 0.5)
    bx, by = rig0.world(*TAIL0)
    bx, by = bx + sx, by + sy

    def scene(k, ph):
        f = {}
        sw = 0.6 * math.sin(ph)
        pts = [(bx, by), (bx + 0.6, by - 4.0), (bx + 3.4, by - 6.6), (bx + 7.4, by - 6.8), (bx + 10.2, by - 4.4),
               (bx + 10.0, by - 0.8), (bx + 7.6, by + 1.6), (bx + 6.4, by + 4.4), (bx + 6.4 + sw, by + 7.4)]
        o, _, _ = draw(Rig(0, 0, 0, 1.0), [tail_part(pts, 1.25, 1.1)])
        f.update(o)
        solid(f, disc(bx + 6.6, by + 12.0, 1.7), BALL)
        return f
    return companion(scene, tail=False)


def person() -> list[dict]:
    """사람이 고등어냥을 품에 꼭 안았다 — 사람 머리 · 어깨 아래 냥이 얼굴, 두 팔(소매)이 냥이 배를 감싸고
    냥이 앞발이 소매 위로 늘어진다. 아래로 삐져나온 꼬리가 흔들린다"""
    def scene(k, ph):
        f = {}
        rig = Rig(23.0, 21.6, 0.0, 0.72)
        sw = 1.6 * math.sin(ph)
        chc, cr = (0.0, 1.6), 6.4
        cpaws = ("cpaws", any_of(ell(-3.2, 7.0, 1.9, 1.6), ell(3.2, 7.0, 1.9, 1.6)), FUR_L, True)
        sleeves = ("sleeves", any_of(bar((-9.0, 0.6), (-1.6, 9.8), 2.2), bar((9.0, 0.6), (1.6, 9.8), 2.2)), SHIRT_D, True)
        cbody = ("cbody", ell(0.0, 9.0, 5.4, 3.4), lambda a, b: STRIPE if (a + 0.6) % 4.0 < 1.5 else FUR, True)
        ctail = tail_part([(4.2, 10.4), (6.4, 12.4), (5.6 + sw, 14.6)], 1.5, 1.3, name="ctail")
        hair = ("hair", any_of(ell(0.0, -12.4, 5.6, 3.6), ell(-4.6, -10.0, 1.6, 2.6), ell(4.6, -10.0, 1.6, 2.6)),
                HAIR, True)
        skin = ("skin", ell(0.0, -9.6, 5.0, 4.8), SKIN, True)
        torso = ("torso", ell(0.0, 6.0, 9.6, 8.0), SHIRT, False)
        out, _, _ = draw(rig, [cpaws, sleeves] + head_parts(chc, cr, name="chead") + [cbody, ctail, hair, skin, torso])
        for sg in (-1, 1):
            ex, ey = rig.cell(sg * 2.0, -9.2)
            out[ex, ey] = EYE
            out[ex, ey + 1] = EYE
            out[rig.cell(sg * 3.4, -7.2)] = PINK
        face(out, rig, chc, cr, mood="blink" if k in (4, 5) else "open")
        f.update({p: c for p, c in out.items() if p[1] <= 30 and p[0] <= 30})
        return f
    return companion(scene)


PAW = [".#.#.", "#...#", "..#..", ".###.", "#####", ".###."]   # 핀 속 발자국


def pin() -> list[dict]:
    """빨간 지도 핀 동그라미 속에 흰 발자국 — 통통 튀고 땅에 닿을 때 그림자가 진해진다"""
    def scene(k, ph):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 14.0 + dy
        for x in range(19, 27):
            f.setdefault((x, 28), GLOW[2] if dy else GLOW[1])
        pinm = disc(cx, cy, 6.2) | raster([(cx - 4.4, cy + 3.4), (cx + 4.4, cy + 3.4), (cx, cy + 12.4)])
        solid(f, pinm, SIGN, SIGN_D)
        x0, y0 = math.floor(cx) - 2, math.floor(cy) - 3
        for j, row in enumerate(PAW):
            for i, ch in enumerate(row):
                if ch == "#":
                    f[x0 + i, y0 + j] = CREAM
        return f
    return companion(scene)


def wait() -> list[dict]:
    """앉아서 그루밍 — 장 0–5 는 입 앞에 든 앞발을 날름날름 핥고(눈은 ^^), 장 6–10 은 그 발로 볼에서 귀까지 쓱 닦고,
    11 에 눈을 뜬다. 꼬리는 발을 감싸고 끝만 까딱"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(16.0, 18.0, 0.0, 0.86)
        if k < 6:
            lick = k % 2 == 1
            paw = (-8.4, -3.0 + (0.0 if lick else 0.7))
            hc, turn, mood = (-0.4, -6.6), -1.4, "lick" if lick else "happy"
        elif k < 11:
            t = math.sin(math.pi * (k - 5) / 6)
            paw = (-8.4 + 2.6 * t, -3.0 - 7.0 * t)
            hc, turn, mood = (-0.4, -7.0), -0.6, "happy"
        else:
            paw = (-2.6, 0.4)
            hc, turn, mood = (0.0, -7.5), 0.0, "open"
        paw_parts = leg_part([(-3.4, 1.4), (-6.8, 0.8), paw], name="lick", pr=2.3)
        stand = leg_part([(2.4, 1.0), (2.4, 8.4)], name="stand", pr=1.9)
        tw = 0.8 * math.sin(2 * ph)
        tail = tail_part([(5.0, 8.8), (1.0, 10.0), (-4.0, 9.8), (-7.0 + tw * 0.4, 8.0 + tw)], 1.4, 1.2, lined=True)
        hind = ("feet", any_of(ell(-4.4, 8.9, 2.0, 1.4), ell(4.4, 8.9, 2.0, 1.4)), FUR_L, True)
        haunch = ("haunch", any_of(ell(-4.6, 6.2, 2.6, 2.8), ell(4.6, 6.2, 2.6, 2.8)), FUR, True)
        parts = paw_parts + [tail] + stand + head_parts(hc, turn=turn) + [hind, haunch, body_part()]
        f, _, region = draw(rig, parts)
        keep = {p: f[p] for p, r in region.items() if r in ("lick_paw", "lick")}
        face(f, rig, hc, mood="happy" if mood == "lick" else mood, turn=turn)
        f.update(keep)   # 든 앞발이 볼터치 · 눈보다 앞이다
        if mood == "lick":   # 혀 날름 — ㅅ 입 왼발에서 든 앞발 쪽으로
            nx, ny = rig.world(hc[0] + turn, hc[1] + HR * 0.16)
            nl, ny = round(nx) - 1, math.floor(ny)
            for p in ((nl - 2, ny + 2), (nl - 3, ny + 2), (nl - 4, ny + 2), (nl - 3, ny + 3)):
                f[p] = PINK
        whiskers(f, rig, hc, turn=turn, n=2, skip=(-1,) if k < 11 else ())
        frames.append(finish(f))
    return frames


def cross() -> list[dict]:
    """앞모습 사냥 얼굴 — 초록 눈의 동공이 가늘었다(장 0–3) 둥글게 커진다. 긴 수염 한 줄씩이 가로 조준선,
    귀 사이와 턱 밑 초록 눈금이 세로선. 귀가 쫑긋, 코(15, 15)가 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(16.0, 21.9, 0.0, 1.0)
        tw = 0.6 if k in (6, 7) else 0.0
        f, _, _ = draw(rig, head_parts(turn=tw))
        face(f, rig, mood="open", mark=True)
        wide = 4 <= k <= 9
        for sg in (-1, 1):   # 3×3 초록 눈에 세로 동공
            ex, ey = rig.world(sg * HR * 0.42, HC[1] - HR * 0.06)
            x0, y0 = round(ex) - (2 if sg < 0 else 1), round(ey) - 2
            for dx in range(3):
                for dy in range(3):
                    f[x0 + dx, y0 + dy] = GREEN
            for dy in range(3):
                f[x0 + 1, y0 + dy] = EYE
                if wide and dy > 0:
                    f[x0 + (0 if sg > 0 else 2), y0 + dy] = EYE
            f[x0 + (2 if sg > 0 else 0), y0] = HI
        for x in range(1, 31):   # 가로 조준선 — 얼굴 밖 칸만
            if (x, 15) not in f:
                f[x, 15] = OUT
        for sg in (-1, 1):   # 아래로 비스듬한 짧은 수염
            for i in range(3):
                x = (6 - i * 2 if sg < 0 else 25 + i * 2)
                f.setdefault((x, 17 + (i + 1) // 2), OUT)
                f.setdefault((x + (-1 if sg < 0 else 1), 17 + (i + 1) // 2), OUT)
        o = 1 if k % 6 < 3 else 0
        for y in range(1 + o, 4):          # 귀 사이 세로 눈금
            f.setdefault((15, y), GLOW[0])
        for y in range(25, 31 - o):        # 턱 밑 세로 눈금
            f.setdefault((15, y), GLOW[0])
        frames.append(finish(f))
    return frames


HAND_TIP = (4, 4)


def hand() -> list[dict]:
    """엎드린 고등어냥이 앞발을 왼쪽 위로 쭉 내밀어 발톱 하나로 톡톡 — 발톱 끝이 핫스팟(`HAND_TIP`).
    톡 칠 때(장 2–3 · 8–9) 발톱 둘레에 눌림 줄이 튀고, 뒤에서 꼬리가 살랑인다"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(19.0, 21.0, 0.0, 0.74)
        tap = k in (2, 3, 8, 9)
        pc = (-11.6, -12.6)
        arm = leg_part([(-3.8, 1.0), (-7.6, -6.0), pc], name="arm", pr=2.8, r=2.5)
        sw = math.sin(ph)
        loaf = ("loaf", any_of(ell(4.6, 3.6, 8.6, 4.6), ell(1.0, 6.2, 9.0, 2.6)),
                lambda a, b: STRIPE if a > 1.0 and (a + 0.2) % 4.2 < 1.6 and b < 6.0 else FUR, False)
        paw2 = ("paw2", ell(2.6, 7.6, 2.2, 1.4), FUR_L, True)
        tail = tail_part([(12.4, 5.4), (15.0, 2.2), (14.0 + 1.4 * sw, -3.0)])
        parts = arm + head_parts(turn=-0.8) + [paw2, loaf, tail]
        f, _, _ = draw(rig, parts)
        face(f, rig, mood="open", turn=-0.8, look=(-1, -1))
        # 발톱: 발끝에서 왼쪽 위로 흰 두 칸
        tx, ty = rig.cell(pc[0] - 1.5, pc[1] - 1.5)
        claw = [(tx, ty), (tx - 1, ty - 1)]
        for p in claw:
            f[p] = CREAM
        f.setdefault((tx - 1, ty), OUT)
        f.setdefault((tx, ty - 1), OUT)
        if tap:
            for p in ((tx - 4, ty - 1), (tx - 4, ty), (tx - 1, ty - 4), (tx, ty - 4), (tx - 3, ty - 3)):
                f.setdefault(p, OUT)
        dx, dy = HAND_TIP[0] - (tx - 1), HAND_TIP[1] - (ty - 1)
        frames.append(finish({(x + dx, y + dy): c for (x, y), c in f.items()}))
    return frames


def ibeam() -> list[dict]:
    """I 꼴 스크래쳐(위아래 판 · 노끈 감은 기둥)를 오른쪽에서 뒷발로 선 고등어냥이 두 앞발로 번갈아 벅벅 긁는다.
    긁을 때 노끈 보풀이 튄다. 기둥 가운데(15, 15)가 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        post = {(x, y) for x in range(14, 18) for y in range(4, 27)}
        solid(f, post, lambda p: SISAL_D if (p[0] + p[1] + k // 3) % 3 == 0 else SISAL)
        top = {(x, y) for x in range(9, 23) for y in range(1, 5)}
        base = {(x, y) for x in range(9, 23) for y in range(26, 30)}
        solid(f, top, lambda p: PLATE_D if p[1] == 3 else PLATE)
        solid(f, base, lambda p: PLATE_D if p[1] == 28 else PLATE)
        rig = Rig(24.4, 18.6, 0.0, 0.6)
        s = math.sin(ph)
        # 턱시도냥과 같은 박자 — 한 앞발이 기둥 높이 박혀 아래로 죽 긁어내리는 동안 다른 앞발은 떼어 위로 올린다.
        # 두 발이 사인으로 마주 오가면 펌프질로 읽힌다
        arms, marks = [], []
        for i, sh in enumerate(((-2.6, -0.6), (-2.6, 1.6))):
            t = (k / 6 + i / 2) % 1
            if t < 0.66:
                tip = (-12.6, -12.0 + 12.0 * t / 0.66)
                marks.append(tip)
            else:
                tip = (-10.6, 0.0 - 12.0 * (t - 0.66) / 0.34)
            arms += leg_part([sh, (-7.0, (sh[1] + tip[1]) / 2 - 1.0), tip], name=f"a{i + 1}", pr=2.0, r=1.7)
        body = body_part((0.6, 4.0), 4.8, 7.0, rot=0.0)
        hind = ("hind", any_of(ell(-1.6, 11.6, 2.4, 1.4), ell(3.0, 11.6, 2.4, 1.4)), FUR_L, True)
        tail = tail_part([(4.0, 9.0), (8.0, 8.0 + s), (9.0, 3.0 + s)], 1.6, 1.3)
        cat, _, _ = draw(rig, arms + head_parts(turn=-1.0) + [hind, body, tail])
        face(cat, rig, mood="open", turn=-1.0, look=(-1, 0))
        # 긁는 발이 지나온 자리에 노끈이 일어난 흰 자국 두 줄, 발끝 왼쪽으로 보풀이 튄다
        for a, b in marks:
            _, y0 = rig.cell(a, -12.0)
            _, y1 = rig.cell(a, b)
            for y in range(y0, y1):
                for x in (15, 17):
                    if (x, y) in post:
                        f[x, y] = hx("fff4dcff")
            if k % 2:
                for p in ((12, y1 - 1), (11, y1 + 1)):
                    f.setdefault(p, SISAL_D)
        f.update({p: c for p, c in cat.items() if p[0] <= 30})
        frames.append(finish(f))
    return frames


def move() -> list[dict]:
    """납작 엎드려 네 발을 쭉 뻗은(위에서 본) 고등어냥 — 앞발은 좌우로, 꼬리는 아래로. 등의 굵은 가로 줄이 고등어 같다.
    앞발이 헤엄치듯 까딱이고 네 방향 초록 화살촉이 바깥으로 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy, GLOW[0])
        rig = Rig(15.5, 16.4, 0.0, 0.72)
        sw = math.sin(ph)
        hc = (0.0, -7.6)
        back = ("body", ell(0.0, 2.2, 4.2, 6.6), lambda a, b: STRIPE if (b + 0.2) % 3.8 < 1.5 and abs(a) < 3.4 else FUR, False)
        legs = []
        for sg in (-1, 1):
            legs += leg_part([(sg * 2.6, -1.2), (sg * 7.0, -1.2 - 0.8 * sg * sw), (sg * 11.6, -1.2 + 0.9 * sg * sw)],
                             name=f"f{sg}", pr=1.9, r=1.6)
            legs += leg_part([(sg * 2.4, 6.6), (sg * 5.8, 9.4)], name=f"h{sg}", pr=1.7, r=1.5)
        tail = tail_part([(0.0, 8.0), (0.8 * sw, 12.4), (-0.8 * sw, 15.4)], 1.4, 1.1)
        cat, _, _ = draw(rig, head_parts(hc) + legs + [back, tail])
        face(cat, rig, hc, mood="blink" if k == 8 else "open")
        f.update(cat)
        frames.append(finish(f))
    return frames


def longcat(ang: float, L0: float, D: float, r: float = 5.0) -> list[dict]:
    """롱캣 — ang 축(도, 0 이 오른쪽, 머리 → 꼬리)을 따라 몸이 L0 ± 1.4 로 늘었다 줄었다. 머리는 늘 똑바로(얼굴이
    안 기운다), 반대 끝은 뒷발 둘과 옆으로 말린 꼬리. 늘이지 않은 그림을 축 따라 판 가운데로 옮기고,
    양 끝 화살촉 꼭짓점은 판 가운데에서 축 따라 D 칸"""
    t = math.radians(ang)
    ex, ey = math.cos(t), math.sin(t)
    dx, dy = round(ex), round(ey)

    def cat(L, ph, k, shift):
        rig = Rig(15.5 + ex * shift, 15.5 + ey * shift, ang, 1.0)
        sw = math.sin(ph + 1.0)
        body = ("body", ell(0.0, 0.0, L / 2 + 1.2, 3.2),
                lambda a, b: STRIPE if (a + 0.6) % 4.0 < 1.5 and abs(b) < 2.8 else FUR, False)
        paws = ("paws", any_of(ell(-L / 2 + 1.0, -3.0, 1.7, 1.5), ell(-L / 2 + 1.0, 3.0, 1.7, 1.5),
                               ell(L / 2 - 0.2, -3.0, 1.7, 1.5), ell(L / 2 - 0.2, 3.0, 1.7, 1.5)), FUR_L, True)
        side = 1 if ey >= 0 and ex >= 0 else -1          # 꼬리는 화면 아래 · 오른쪽으로 말린다
        tail = tail_part([(L / 2 + 0.6, 0.6 * side), (L / 2 + 2.8, 2.8 * side), (L / 2 + 2.2 + sw, 5.8 * side)], 1.4, 1.1)
        bo, _, _ = draw(rig, [paws, body, tail])
        hxw, hyw = rig.world(-L / 2 - r * 0.55, 0.0)
        hrig = Rig(hxw, hyw, 0.0, 1.0)
        ho, _, _ = draw(hrig, head_parts((0.0, 0.0), r))
        face(ho, hrig, (0.0, 0.0), r, mood="sleep" if k in (3, 4, 5) else "open")
        bo.update(ho)
        return bo

    rest = cat(L0, 0.0, 0, 0.0)
    proj = [(x + 0.5 - 15.5) * ex + (y + 0.5 - 15.5) * ey for x, y in rest]
    shift = -(min(proj) + max(proj)) / 2
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        st = 1.4 * math.sin(ph)
        o = 1 if st > 0.4 else 0
        for sg in (-1, 1):
            chevron(f, round(15.5 + sg * ex * (D + o) - 0.5), round(15.5 + sg * ey * (D + o) - 0.5),
                    sg * dx, sg * dy, GLOW[0] if o else GLOW[1])
        f.update(cat(L0 + st, ph, k, shift))
        frames.append({p: c for p, c in finish(f).items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31})
    return frames


def ns() -> list[dict]:
    return longcat(90.0, 9.0, 13.5, r=4.8)


def we() -> list[dict]:
    return longcat(0.0, 10.5, 13.5, r=5.0)


def nwse() -> list[dict]:
    return longcat(45.0, 12.0, 18.4, r=5.0)


def nesw() -> list[dict]:
    return longcat(135.0, 12.0, 18.4, r=5.0)


def no() -> list[dict]:
    """빨간 금지 표지 안에서 등을 돌리고 앉은 고등어냥(쌩) — 꼬리를 바닥에 탁탁 치다가, 장 7–9 에 어깨 너머로 힐끔
    (초록 눈 하나가 머리 오른쪽 끝에 보인다)"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        ring = {(x, y) for x in range(32) for y in range(32)
                if 11.4 <= math.hypot(x + 0.5 - 16, y + 0.5 - 16) <= 14.6}
        slash = {(x, y) for x in range(32) for y in range(32)
                 if math.hypot(x + 0.5 - 16, y + 0.5 - 16) < 11.6 and abs((x - y)) <= 1}
        solid(f, ring | slash, SIGN, SIGN_D)
        rig = Rig(16.0, 18.4, 0.0, 0.7)
        look = k in (7, 8, 9)
        lash = math.sin(2 * ph)
        tail = tail_part([(4.6, 8.4), (9.0, 9.2), (12.0, 6.6 + 3.0 * lash)], 1.5, 1.2)
        back = ("body", ell(0.0, 3.2, 6.0, 6.4),
                lambda a, b: STRIPE if abs(a) < 0.7 or (b - 0.4) % 4.0 < 1.5 else FUR, False)
        haunch = ("haunch", any_of(ell(-4.8, 7.0, 2.6, 2.6), ell(4.8, 7.0, 2.6, 2.6)), FUR, True)
        cat, _, _ = draw(rig, head_parts(turn=1.2 if look else 0.0, back=True) + [tail, haunch, back])
        if look:   # 어깨 너머 힐끔 — 머리 오른쪽 끝에 초록 눈 · 수염
            x, y = rig.cell(5.2, -8.0)
            cat[x, y] = GREEN
            cat[x, y + 1] = EYE
            cat[x - 1, y] = HI if k == 8 else GREEN
            cat[x - 1, y + 1] = EYE
            for i in range(1, 4):
                cat.setdefault((rig.cell(7.6, -5.6)[0] + i, rig.cell(7.6, -5.6)[1]), OUT)
        f.update(cat)
        frames.append(finish(f))
    return frames


def pencil_parts(Lp: float = 21.0, w: float = 1.8):
    """끝(0, 0)에서 +u 로 뻗은 연필 — 심 · 나무 깎은 데 · 노란 몸(아래쪽 그늘) · 쇠테 · 지우개"""
    shape = any_of(tri((0.0, 0.0), (5.0, -w), (5.0, w)), bar((5.0, 0.0), (Lp, 0.0), w))

    def col(a, b):
        if a < 1.7:
            return LEAD
        if a < 5.0:
            return WOOD
        if a < Lp - 3.4:
            return PENCIL_D if b > 0.4 else PENCIL
        if a < Lp - 1.8:
            return FERRULE
        return ERASER
    return ("pencil", shape, col, True)


def pen() -> list[dict]:
    """엎드린 고등어냥이 연필을 입에 물고 쓴다 — 연필심(왼쪽 아래)이 핫스팟. 지나간 자리에 연필 줄이 자라고 꼬리가 살랑"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        n = k + 1   # 연필 줄 — 심에서 오른쪽으로 물결치며 자란다
        for i in range(n):
            x = 5 + i
            f[x, 29 + (1 if (i // 2) % 2 else 0)] = LEAD
        prig = Rig(1.6, 30.4, -45.0, 1.0)
        po, _, _ = draw(prig, [pencil_parts()])
        rig = Rig(15.6, 15.6, 0.0, 0.74)
        sw = math.sin(ph)
        body = body_part((8.6, 3.0), 8.6, 4.4, chest=False, stripes="along")
        paws = ("paws", any_of(ell(-3.4, 6.0, 2.2, 1.5), ell(2.6, 6.4, 2.2, 1.5)), FUR_L, True)
        tail = tail_part([(16.2, 2.4), (18.4, -1.6), (17.0 + 1.4 * sw, -5.6)], 1.5, 1.2)
        cat, _, _ = draw(rig, head_parts(turn=-0.6) + [paws, body, tail])
        face(cat, rig, mood="open", turn=-0.6, look=(-1, 1))
        whiskers(cat, rig, turn=-0.6, n=2, skip=(-1,))
        f.update({p: c for p, c in cat.items() if p[0] <= 30})
        mx, my = rig.world(-0.6, HC[1] + HR * 0.45)   # 입 — 연필이 여기까지 물려 있다
        for p, c in po.items():
            u, _ = prig.local(p[0] + 0.5, p[1] + 0.5)
            if u < 18.5 or p not in cat:
                f[p] = c
        frames.append(finish(f))
    return frames


def pen_tip(fr):
    return max((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1] - p[0], -p[0]))


def up() -> list[dict]:
    """뒷발로 꼿꼿이 서서 한 앞발을 머리 위로 쭉 뻗은 고등어냥(저요!) — 발끝(맨 위)이 핫스팟이라 그 발은 안 움직이고,
    눈은 위를 보고, 다른 앞발이 가슴 앞에서 까딱, 꼬리가 살랑"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(15.0, 19.6, 0.0, 0.74)
        sw = math.sin(ph)
        raise_ = leg_part([(3.8, -0.6), (7.6, -8.4), (6.4, -19.8)], name="up", pr=2.0, lined=False)
        tuck = leg_part([(-2.8, 0.4), (-3.4, 3.4 - 0.8 * max(0.0, sw))], name="tuck", pr=1.8)
        body = body_part((0.0, 3.8), 5.2, 7.0)
        feet = ("feet", any_of(ell(-3.0, 11.2, 2.4, 1.4), ell(3.0, 11.2, 2.4, 1.4)), FUR_L, True)
        tail = tail_part([(-3.6, 9.0), (-8.0, 8.4), (-9.6 + sw, 4.0), (-8.4 + 1.2 * sw, 0.6)], 1.4, 1.1)
        parts = [raise_[0]] + tuck + head_parts() + [raise_[1], feet, body, tail]
        f, _, _ = draw(rig, parts)
        face(f, rig, mood="blink" if k == 5 else "open", look=(1, -1))
        whiskers(f, rig, n=2, skip=(1,))
        frames.append(finish(f))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def top_cell(fr):
    return min((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1], p[0]))


HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1),
       "wait": (16, 16), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (15, 15),
       "hand": HAND_TIP, "up": top_cell, "pen": pen_tip}


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

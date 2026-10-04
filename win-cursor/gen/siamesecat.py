# SPDX-License-Identifier: Apache-2.0
"""샴냥(siamesecatanim) 구성표 그림 `art/siamesecatanim/*.txt` 를 만든다.
빌드가 부르지 않고 손으로 돌린다 · 빌드 코드 해시와 CI 캐시 키에 안 들어간다.

  python3 gen/siamesecat.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

해양 애니처럼 칸마다 샴냥이 그 칸 뜻에 맞는 짓을 따로 그린다(`SCENE`). '냥이 · 애니' 묶음 중 샴냥은 **포인트 무늬**다 —
크림 몸에 얼굴 가운데 짙은 갈색 마스크, 귀 · 발 · 꼬리가 짙은 갈색이고 눈은 파랗다(실루엣 안의 표지). 머리 · 귀 · 눈 비율과
작은 화살표 동반 꼴은 치즈냥 · 삼색냥을 따른다. 수다쟁이라 소품의 주인공은 말풍선과 음표(♪)이고, 신호색(화살촉 ·
음표 · 말풍선 점)은 눈 색인 파랑이다. 꼬리는 끝을 갈고리로 만 물음표 꼴로 자주 세운다.

  arrow   큰 흰 화살표 뒤에 숨은 샴냥이 빗변 위로 빼꼼하며 조잘댄다(입이 열렸다 닫혔다) — 짙은 발끝 둘이 빗변을 잡고
          장 2–5 에 쏙 더 올라온다. 화살표 끝이 핫스팟(`sea.peek`, 냥이 10종 공용 틀)
  busy    작은 화살표 샴냥 + 오른쪽 아래 말풍선 속 '…' 세 점이 차례로 통통 튄다(입력 중)
  cross   가는 조준선 가운데 앉은 파란 나비(몸통이 핫스팟)를 아래에서 고개를 내민 샴냥이 사시 눈으로 노려본다.
          나비가 날갯짓
  hand    마네키네코처럼 앉아 짙은 앞발 하나를 들고 까딱까딱 손짓(이리 와) — 다른 앞발엔 금화, 목엔 방울.
          든 발 꼭대기가 핫스팟(발끝을 굽혀도 꼭대기는 그대로)
  help    작은 화살표 샴냥 + 말풍선 속 파란 물음표 — 말풍선이 통 하고 튀어 오른다
  ibeam   크게 선 글자 커서 I 오른쪽에서 샴냥이 앞발을 I 에 얹고 조잘대면, I 왼쪽에 글자 점이 하나씩 찍힌다.
          I 는 깜빡이듯 짙었다 옅어진다. 핫스팟은 I 가운데
  move    앉은 샴냥이 위 · 오른쪽 · 아래 · 왼쪽으로 한 칸씩 콩콩 옮겨 앉는다 — 가는 쪽 화살촉이 켜지고 뒤에 바람 줄
  ns      앉아서 목을 쭉 빼고 "야~옹" — 목이 늘어나며 입이 열리고, 줄어들며 닫힌다. 위아래 화살촉
  we · nwse · nesw   배를 깔고 앞발은 앞으로, 뒷발은 뒤로 쭉 뻗은 '슈퍼맨' 기지개 — 그 축으로 다리가 늘었다 줄었다.
          얼굴은 기울이면 칸 위에서 뭉개져서 몸만 축으로 돌리고 얼굴은 늘 똑바로 둔다
  no      빨간 금지 표지 안에서 입을 크게 벌리고 "냐아앙!" 항의하다가(눈은 ><) 입을 꾹 다물고 흥 — 옆에 느낌표
  pen     짙은 꼬리 끝을 붓 삼아 글씨를 쓴다 — 꼬리 끝(왼쪽 아래)이 핫스팟, 지나간 자리에 먹 줄이 남는다
  person  작은 화살표 샴냥 + 어깨에 샴냥을 얹은 사람(샴은 어깨 위를 좋아한다) — 어깨냥 꼬리가 사람 가슴께로 살랑
  pin     작은 화살표 샴냥 + 흰 동그라미 속에 파란 음표가 든 빨간 지도 핀이 통통 튄다
  up      앞모습으로 앉아 꼬리를 머리 옆으로 곧게 세운다(반가워) — 꼬리 끝은 물음표 갈고리, 그 꼭대기가 핫스팟.
          갈고리 끝만 까딱인다
  wait    앉아서 고개를 좌우로 까딱이며 노래 — 입이 열렸다 닫히고 음표가 머리 위로 둥실 떠올랐다 사라진다. 가운데가 핫스팟

몸은 부위(타원 · 굵기가 변하는 막대 · 세모)를 고양이 제 좌표 (u 오른쪽, w 아래)에 놓고 화면으로 돌려 찍는다
(`Rig`, `draw` — 치즈냥 생성기와 같은 방식이지만 다른 생성기에 기대지 않게 여기 따로 둔다). 마스크는 머리 색 함수가
칠하므로(`head_parts`) 작게 그려도 같이 줄어든다. 눈 · 코 · 입은 화면 칸에 직접 찍는다(`face`).
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, disc, finish, hx, ink, inside, peek, peek_tail, phases, raster, solid, write  # noqa: F401

SID = "siamesecatanim"

OUT = hx("3a2a30ff")                                           # 테두리
CREAM, CREAM_D = hx("fff3e0ff"), hx("eedabdff")                # 몸 · 그늘
PT, PT_L, PT_D = hx("7a5642ff"), hx("a8866aff"), hx("4a3226ff")  # 포인트(짙은 갈색) · 번진 테 · 코
BLUE, BLUE_D = hx("5aa0ecff"), hx("2f6cc0ff")                  # 눈
PINK, HI = hx("f4a0b0ff"), hx("ffffffff")
ink(OUT, HI, hx("fbecdcc7"))
PAPER = hx("fffdf8ff")                                         # 말풍선 속
GOLD, GOLD_D = hx("f2c94cff"), hx("c9962aff")                  # 금화 · 방울
INKC = hx("2b2630ff")                                          # 먹
SKIN, SHIRT, SHIRT_D, HAIR = hx("f7d7bcff"), hx("c98aa8ff"), hx("a46886ff"), hx("5a4038ff")
WING, WING_D = hx("9ccaf6ff"), hx("5aa0ecff")                  # 나비
GLOW = (hx("5aa0ecff"), hx("5aa0ecb0"), hx("5aa0ec60"))       # 화살촉 · 음표 (짙은 것부터) — 눈 색


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
HC, HR = (0.0, -7.5), 7.0       # 머리 가운데 · 반지름(앉은 샴냥 기준)


def head_parts(hc=HC, r=HR, turn=0.0, name="head") -> list:
    """앞모습 머리: 옆으로 퍼진 볼 · 조금 큰 세모 귀(짙은 갈색, 속은 번진 갈색) · 얼굴 가운데 짙은 마스크.
    마스크는 눈 · 코 · 주둥이를 덮는 타원이고 가장자리는 한 칸 옅게 번진다 — 경계가 칼 같으면 가면으로 읽힌다"""
    u0, w0 = hc
    head = any_of(ell(u0, w0 - 0.4, r * 1.0, r * 0.84), ell(u0, w0 + 1.0, r * 1.12, r * 0.64))
    ears, inner = [], []
    for sg in (-1, 1):
        base0, tip, base1 = (u0 + sg * r * 1.02, w0 - r * 0.16), (u0 + sg * r * 0.9 + turn * 0.3, w0 - r * 1.4), \
            (u0 + sg * r * 0.16, w0 - r * 0.74)
        ears.append(tri(base0, tip, base1))
        cx, cy = (base0[0] + tip[0] + base1[0]) / 3, (base0[1] + tip[1] + base1[1]) / 3 + r * 0.06
        inner.append(tri(*[(cx + (p[0] - cx) * 0.45, cy + (p[1] - cy) * 0.45) for p in (base0, tip, base1)]))
    inner_hit = any_of(*inner)
    mc, mra, mrb = (u0 + turn * 0.6, w0 + r * 0.2), r * 0.64, r * 0.56

    def skin(a, b):
        d = ((a - mc[0]) / mra) ** 2 + ((b - mc[1]) / mrb) ** 2
        return PT if d <= 0.62 else PT_L if d <= 1.0 else CREAM

    def ear_col(a, b):
        return PT_L if inner_hit(a, b) else PT
    return [(name, head, skin, True), (name + "_ear", any_of(*ears), ear_col, False)]


def body_part(c=(0.0, 3.2), ra=7.0, rb=6.4, name="body"):
    """크림 몸 — 오른쪽 아래만 한 톤 그늘"""
    c0, c1 = c

    def col(a, b):
        return CREAM_D if (a - c0) / ra * 0.6 + (b - c1) / rb > 0.62 else CREAM
    return (name, ell(c0, c1, ra, rb), col, False)


def tail_part(pts, r0=1.6, r1=1.3, name="tail", lined=False):
    """짙은 꼬리 — 밑동만 번진 갈색, 끝으로 갈수록 짙다"""
    at, total = along(pts)

    def col(a, b):
        t = at(a, b)
        return PT_L if t < total * 0.22 else PT
    return (name, chain(pts, r0, r1), col, lined)


def arm_part(pts, r=1.6, pr=1.9, name="arm", fur=PT_L, lined=True):
    """앞발 하나 → [발, 팔] 두 부위. 발은 짙은 갈색, 팔은 번진 갈색(포인트는 발끝으로 갈수록 짙다)"""
    paw = (name + "_paw", ell(*pts[-1], pr, pr * 1.05), PT, True)
    return [paw, (name, chain(pts, r, r * 0.92), fur, lined)]


def dot(f: dict, x: int, y: int, c: tuple) -> None:
    f[x, y] = c


def face(f: dict, rig: Rig, hc=HC, r=HR, mood="open", turn=0.0) -> None:
    """얼굴: 2×2 파란 눈(흰 반짝 1칸, 오른쪽 아래가 짙은 파랑) · 짙은 코 · ㅅ 입 · 볼터치(마스크 바깥 크림 위).
    작게(k·r < 5) 그리면 눈 1×2 · 코 1칸.
    mood: open · blink(감은 한 줄) · happy(^) · talk(입을 동그랗게 벌림) · yowl(눈 >< · 입을 크게) ·
    cross(사시 — 위 안쪽을 본다) · up(위를 본다)"""
    u0, w0 = hc
    small = rig.k * r < 5.0
    for sg in (-1, 1):
        ex, ey = rig.world(u0 + turn + sg * r * 0.42, w0 - r * 0.06)
        if small:
            x0, y0 = math.floor(ex), math.floor(ey - 0.5)
            if mood in ("blink", "happy", "yowl"):
                dot(f, x0, y0 + 1, OUT)
            else:
                dot(f, x0, y0, BLUE)
                dot(f, x0, y0 + 1, BLUE_D)
            continue
        x0, y0 = round(ex - 1), round(ey - 1)
        if mood in ("open", "talk"):
            dot(f, x0, y0, HI)
            dot(f, x0 + 1, y0, BLUE)
            dot(f, x0, y0 + 1, BLUE)
            dot(f, x0 + 1, y0 + 1, BLUE_D)
        elif mood in ("cross", "up"):     # 동공(짙은 파랑)이 위로 — cross 는 안쪽 위
            inner = 1 if sg < 0 else 0
            for dx in (0, 1):
                for dy in (0, 1):
                    dot(f, x0 + dx, y0 + dy, BLUE)
            dot(f, x0 + (inner if mood == "cross" else (0 if sg < 0 else 1)), y0, BLUE_D)
            dot(f, x0 + (1 - inner if mood == "cross" else (1 if sg < 0 else 0)), y0 + 1, HI)
        elif mood == "blink":
            dot(f, x0, y0 + 1, OUT)
            dot(f, x0 + 1, y0 + 1, OUT)
        elif mood == "happy":     # ^
            dot(f, x0 - 1 if sg < 0 else x0, y0 + 1, OUT)
            dot(f, x0 if sg < 0 else x0 + 1, y0, OUT)
            dot(f, x0 + 1 if sg < 0 else x0 + 2, y0 + 1, OUT)
        elif mood == "yowl":      # > <
            a = x0 if sg < 0 else x0 + 1
            b = x0 + 1 if sg < 0 else x0
            dot(f, a, y0 - 1 if False else y0, OUT)
            dot(f, b, y0 + 1, OUT)
            dot(f, a, y0 + 2, OUT)
    nx, ny = rig.world(u0 + turn, w0 + r * 0.16)
    if small:
        dot(f, math.floor(nx), math.floor(ny), PT_D)
    else:
        nl, ny = round(nx) - 1, math.floor(ny)
        dot(f, nl, ny, PT_D)
        dot(f, nl + 1, ny, PT_D)
        if mood == "talk":        # 동그랗게 벌린 입
            for p in ((nl, ny + 1), (nl + 1, ny + 1), (nl - 1, ny + 2), (nl + 2, ny + 2), (nl, ny + 3), (nl + 1, ny + 3)):
                dot(f, *p, OUT)
            dot(f, nl, ny + 2, PINK)
            dot(f, nl + 1, ny + 2, PINK)
        elif mood == "yowl":      # 크게 벌린 입 (분홍 혀)
            for p in ((nl - 1, ny + 1), (nl + 2, ny + 1), (nl - 1, ny + 2), (nl + 2, ny + 2), (nl, ny + 4),
                      (nl + 1, ny + 4), (nl - 1, ny + 3), (nl + 2, ny + 3)):
                dot(f, *p, OUT)
            for p in ((nl, ny + 1), (nl + 1, ny + 1), (nl, ny + 2), (nl + 1, ny + 2)):
                dot(f, *p, PT_D)
            dot(f, nl, ny + 3, PINK)
            dot(f, nl + 1, ny + 3, PINK)
        else:
            for p in ((nl - 1, ny + 2), (nl, ny + 1), (nl + 1, ny + 1), (nl + 2, ny + 2)):   # ㅅ 입
                dot(f, *p, OUT)
    if small:
        return
    for sg in (-1, 1):   # 볼터치 — 마스크 바깥 크림 위
        bx, by = rig.world(u0 + turn + sg * r * 0.8, w0 + r * 0.3)
        dot(f, math.floor(bx), math.floor(by), PINK)


def whiskers(f: dict, rig: Rig, hc=HC, r=HR, turn=0.0, n=2, skip=()) -> None:
    """볼 바깥으로 뻗은 1칸 수염 둘씩 — 머리 테두리 밖 빈 칸에만 찍는다(얼굴 안에 그으면 콧수염이 된다)"""
    u0, w0 = hc
    for sg in (-1, 1):
        if sg in skip:
            continue
        for j, dw in enumerate((0.05, 0.3)):
            x0, y0 = rig.world(u0 + turn + sg * r * 1.08, w0 + r * dw)
            for i in range(n + 1):
                x = math.floor(x0 + sg * i)
                y = math.floor(y0 + (i * 0.4 if j else 0))
                if (x, y) not in f:
                    f[x, y] = OUT


def head_only(rig, hc=HC, r=HR, mood="open", turn=0.0, whisk=True) -> dict:
    f, _, _ = draw(rig, head_parts(hc, r, turn))
    face(f, rig, hc, r, mood, turn)
    if whisk:
        whiskers(f, rig, hc, r, turn)
    return f


def anchor(frames: list[dict]) -> list[dict]:
    """불투명 칸의 왼쪽 끝 · 위 끝을 1 에 맞춘다(테 한 칸은 0 에) — 둥근 발은 x+y 최소 칸보다 한 칸 왼쪽으로 삐져서
    그 칸을 (1, 1) 에 박으면 판 밖으로 나갔다. 핫스팟은 `tip` 이 고른다"""
    op = [p for f in frames for p, c in f.items() if c[3] == 255]
    dx, dy = 1 - min(x for x, _ in op), 1 - min(y for _, y in op)
    return [{(x + dx, y + dy): c for (x, y), c in f.items()} for f in frames]


def tip(fr) -> tuple:
    """맨 왼쪽 위 불투명 칸(x+y 가 가장 작은 것, 같으면 위) — 화살표 꼴 칸의 발끝"""
    return min((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[0] + p[1], p[1]))


def board(f: dict) -> dict:
    """판(테 한 칸을 남긴 1–30) 밖을 자른다"""
    return {p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}


# ── 소품 ─────────────────────────────────────────────────────────────────────
NOTE = [".##",          # ♪ — 깃발 · 기둥 · 2×2 머리
        ".#.",
        "##.",
        "##."]


def note(f: dict, x0: int, y0: int, col) -> None:
    for j, row in enumerate(NOTE):
        for i, ch in enumerate(row):
            if ch == "#":
                f[x0 + i, y0 + j] = col


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col, n: int = 4) -> None:
    """(dx, dy) 쪽을 가리키는 화살촉. 꼭짓점이 (cx, cy)"""
    px, py = -dy, dx
    for i in range(n):
        for s in (-1, 1):
            for w in (0, 1):
                f[cx - dx * (i + w) + s * px * i, cy - dy * (i + w) + s * py * i] = col


def speech(f: dict, x0: int, y0: int, x1: int, y1: int, R: float = 3.0, tip=2.6) -> None:
    """말풍선: 모서리를 둥글린(반지름 R) 흰 판(x0..x1, y0..y1) + 왼쪽 위 모서리에서 화살표 샴냥 쪽으로 삐져나온
    세모 꼬리(길이 tip). 꼬리 쪽은 늘 왼쪽 위다 — 동반 칸의 샴냥이 거기 앉는다"""
    m = set()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cx = min(max(x + 0.5, x0 + R), x1 + 1 - R)
            cy = min(max(y + 0.5, y0 + R), y1 + 1 - R)
            if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= R:
                m.add((x, y))
    m |= raster([(x0 + R + 1.6, y0 + 0.6), (x0 - tip, y0 - tip), (x0 + 0.6, y0 + R + 1.6), (x0 + R, y0 + R)])
    solid(f, m, PAPER, OUT)


def sign(f: dict, cx=15.5, cy=15.5, R=13.5) -> set:
    """빨간 금지 표지(둥근 테 + 왼쪽 위 → 오른쪽 아래 빗금) — 칠한 칸 집합을 돌려준다"""
    ring = {p for p in disc(cx, cy, R) if math.hypot(p[0] + 0.5 - cx, p[1] + 0.5 - cy) > R - 2.4}
    slash = set()
    for t in range(-90, 91):
        x, y = cx + t / 100 * (R - 1.5) * 0.7071, cy + t / 100 * (R - 1.5) * 0.7071
        slash |= disc(x, y, 1.3)
    solid(f, ring | slash, SIGN, SIGN_D)
    return ring | slash


def sit_parts(tail, hc=HC, r=HR, turn=0.0, front=(), mid=(), paws=(-1, 1), body=None) -> list:
    """앉은 샴냥 한 벌: front(머리 앞에 오는 것) · 머리 · mid(머리 뒤, 몸 앞) · 앞발(paws 쪽만) · 뒷발 · 엉덩이 · 몸 · 꼬리.
    앞다리는 따로 안 그리고 짙은 앞발만 몸 아래에 둔다 — 다리 막대를 테두리째 그으면 배에 세로줄이 서서 글자로 읽혔다"""
    fp = [("fpaws", any_of(*[ell(sg * 2.3, 8.7, 1.9, 1.3) for sg in paws]), PT, True)] if paws else []
    return list(front) + head_parts(hc, r, turn) + list(mid) + fp + \
        [("feet", any_of(ell(-5.8, 9.0, 1.9, 1.2), ell(5.8, 9.0, 1.9, 1.2)), PT, True),
         ("haunch", any_of(ell(-4.8, 6.2, 2.8, 2.8), ell(4.8, 6.2, 2.8, 2.8)), CREAM, True),
         body or body_part()] + ([tail] if tail else [])


# ── 화살표 샴냥 ──────────────────────────────────────────────────────────────
def arrow_cat(ph: float, k: float = 0.8, k_i: int = 0) -> dict:
    """앉은 샴냥이 왼 앞발을 왼쪽 위로 쭉 뻗어 가리킨다 — 발끝이 왼쪽 위 끝. 다른 앞발은 배 앞에 얌전히,
    물음표 꼬리(끝이 갈고리)가 살랑, 입은 조잘조잘(장마다 열렸다 닫혔다)"""
    rig = Rig(16.0, 16.0, 0.0, k)
    sw = math.sin(ph)
    reach = [(-4.0, -2.0), (-8.6, -8.8), (-14.2, -14.4)]
    tail = [(5.4, 8.0), (9.4, 6.8), (10.8, 2.2 + 0.4 * sw), (10.6 + 0.6 * sw, -1.6), (8.6 + 0.9 * sw, -2.6)]
    reach_parts = arm_part(reach, r=1.9, name="reach", pr=2.2, lined=False)
    parts = sit_parts(tail_part(tail), front=[reach_parts[0]], mid=[reach_parts[1]], paws=(1,))
    out, _, _ = draw(rig, parts)
    mood = "blink" if k_i == 7 else "talk" if k_i % 4 in (1, 2) else "open"
    face(out, rig, mood=mood)
    if k >= 0.7:
        whiskers(out, rig, n=2, skip=(-1,))
    return out


def arrow_frames(small=False) -> list[dict]:
    return anchor([arrow_cat(ph, 0.5 if small else 0.8, k) for k, ph in enumerate(phases())])


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    def head(x, y, k):
        rig = Rig(x - HC[0] * PEEK_K, y - HC[1] * PEEK_K, 0.0, PEEK_K)
        g, _, _ = draw(rig, sit_parts(tail_part(peek_tail(k))))   # 꼬리는 오른쪽으로 길게 U 자
        face(g, rig, mood="blink" if k == 7 else "talk" if k % 4 in (1, 2) else "open")
        whiskers(g, rig, n=2, skip=(-1,))
        return g
    return [finish(peek(k, head, OUT, PT)) for k in range(N)]


PEEK_K = 0.74     # 빼꼼 샴냥 배율


def companion(scene) -> list[dict]:
    """작은 화살표 샴냥 + scene(k, ph) 이 그리는 소품 — busy · help · person · pin"""
    cats = arrow_frames(small=True)
    frames = []
    for k, ph in enumerate(phases()):
        f = scene(k, ph)
        f.update(cats[k])
        frames.append(finish(f))
    return frames


def busy() -> list[dict]:
    """말풍선 속 '…' 세 점이 차례로 켜지며 한 칸 튀어 오른다 — 입력 중"""
    def scene(k, ph):
        f = {}
        speech(f, 15, 17, 30, 27)
        on = (k // 3) % 4         # 0·1·2 차례로, 3 은 쉼
        for i in range(3):
            x, y = 18 + i * 4, 22
            lit = i == on
            col = GLOW[0] if lit else PT_L
            for dx in (0, 1):
                for dy in (0, 1):
                    f[x + dx, y + dy - (1 if lit else 0)] = col
        return f
    return companion(scene)


def help_() -> list[dict]:
    """말풍선 속 굵은 파란 물음표 — 말풍선이 통 하고 한 칸 튀었다 내려앉는다"""
    def scene(k, ph):
        f = {}
        dy = -1 if k % 6 in (1, 2) else 0
        speech(f, 15, 14 + dy, 29, 29 + dy, R=4.0)
        y = 16 + dy               # 5×7 물음표를 가로 두 배 · 위 다섯 줄은 세로 두 배로 — 10×12
        for j, row in enumerate(QMARK):
            h = 2 if j < 5 else 1
            if j == 6:
                h = 2
            for i, ch in enumerate(row):
                if ch == "#":
                    for sx in (0, 1):
                        for sy in range(h):
                            f[17 + i * 2 + sx, y + sy] = BLUE_D
            y += h
        return f
    return companion(scene)


def person() -> list[dict]:
    """어깨에 샴냥을 얹은 사람 — 샴냥은 사람 어깨 뒤에 길게 엎드려 머리를 왼쪽 어깨에 얹고, 꼬리가 오른쪽 어깨 아래로
    늘어져 살랑. 사람은 가끔 눈을 감고 웃는다"""
    def scene(k, ph):
        f = {}
        sw = math.sin(ph)
        rig = Rig(0.0, 0.0, 0.0, 1.0)
        hd = (25.0, 20.6)
        parts = [("skin", ell(hd[0], hd[1] + 0.4, 3.2, 3.2), SKIN, True),
                 ("hair", any_of(ell(hd[0], hd[1] - 1.6, 3.8, 2.6), ell(hd[0] + 3.0, hd[1] + 0.4, 1.3, 2.8)),
                  HAIR, True),
                 ("cbody", any_of(ell(23.6, 24.8, 6.6, 2.2)), CREAM, True),
                 tail_part([(29.2, 25.2), (30.0, 27.4 + 0.4 * sw), (29.4 + 0.8 * sw, 30.4)], 1.0, 0.9),
                 ("torso", ell(24.8, 31.0, 6.8, 5.2), lambda a, b: SHIRT_D if abs(a - 24.8) < 0.5 else SHIRT, False)]
        out, _, _ = draw(rig, parts)
        for sg in (-1, 1):
            ex, ey = math.floor(hd[0] + sg * 1.4 + 0.5) - (1 if sg < 0 else 0), math.floor(hd[1]) + 1
            out[ex, ey] = OUT
            if k % 6 != 4:
                out[ex, ey - 1] = OUT
        f.update(board(out))
        cr = Rig(18.4, 22.4, 0.0, 0.52)
        o, _, _ = draw(cr, head_parts((0.0, 0.0), 6.4) + [("cpaw", ell(1.8, 5.6, 2.4, 1.6), PT, True)])
        face(o, cr, (0.0, 0.0), 6.4, "blink" if k % 6 == 2 else "open")
        f.update(board(o))
        return f
    return companion(scene)


def pin() -> list[dict]:
    """흰 동그라미 속에 파란 음표가 든 빨간 지도 핀이 통통 — 땅에 닿을 때 바닥 그림자가 짙어진다"""
    def scene(k, ph):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 15.0 + dy
        for x in range(19, 27):
            f.setdefault((x, 29), GLOW[2] if dy else GLOW[1])
        pinm = disc(cx, cy, 6.2) | raster([(cx - 4.4, cy + 3.4), (cx + 4.4, cy + 3.4), (cx, cy + 12.4)])
        solid(f, pinm, SIGN, SIGN_D)
        solid(f, disc(cx, cy, 3.9), PAPER, SIGN_D)
        note(f, 21, 13 + dy, BLUE_D)
        return f
    return companion(scene)


def wait() -> list[dict]:
    """앉아서 노래 — 고개가 좌우로 까딱(얼굴이 한 칸씩 옆으로), 입이 열렸다 닫히고, 음표가 머리 위로 떠오르며 옅어진다.
    물음표 꼬리 끝이 박자를 탄다"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(15.5, 17.4, 0.0, 0.84)
        tilt = math.sin(ph)
        turn = 1.0 * tilt
        hc = (0.6 * tilt, -7.2)
        tail = [(5.2, 8.0), (9.2, 6.6), (10.4, 2.0), (10.0 + 0.8 * tilt, -1.6), (8.0 + 1.2 * tilt, -2.4)]
        f, _, _ = draw(rig, sit_parts(tail_part(tail), hc, 6.8, turn))
        face(f, rig, hc, 6.8, "talk" if k % 4 in (0, 1) else "happy", turn)
        whiskers(f, rig, hc, 6.8, turn)
        for i in range(2):        # 음표 둘이 엇갈려 떠오른다
            t = ((k + i * 6) % N) / N
            x = round(4 + i * 20 + 2 * math.sin(2 * math.pi * t + i))
            y = round(12 - 10 * t)
            note(f, x, y, GLOW[0] if t < 0.4 else GLOW[1] if t < 0.75 else GLOW[2])
        frames.append(finish(board(f)))
    return frames


def hand() -> list[dict]:
    """마네키네코 — 앉아서 왼 앞발을 들고 까딱까딱 손짓. 펼친 장(0–2, 6–8)은 분홍 젤리가 보이고, 굽힌 장은 발이
    아래로 짧아져 발등(짙은 갈색)만 보인다 — 꼭대기는 그대로라 핫스팟이 안 비운다. 오른 앞발은 금화를 안고,
    목에 빨간 띠 · 금방울"""
    frames = []
    top = -19.0
    for k, ph in enumerate(phases()):
        bend = k % 6 >= 3
        rig = Rig(17.4, 16.6, 0.0, 0.8)
        rb = 1.7 if bend else 2.5
        pc = (-11.6, top + rb)
        arm = ("arm", chain([(-4.4, -0.6), (-10.4, -6.4), (pc[0], pc[1] + 0.8)], 1.9, 1.8), PT_L, False)
        paw = ("paw", ell(pc[0], pc[1], 2.4, rb), PT, True)
        coin = ("coin", ell(3.0, 3.6, 2.8, 3.6), lambda a, b: GOLD_D if abs(a - 3.0) < 0.6 and abs(b - 3.6) < 2.0
                else GOLD, True)
        hold = ("hold", ell(1.6, 1.0, 2.0, 1.6), PT, True)
        bell = ("bell", ell(0.0, 0.0, 1.4, 1.4), GOLD, True)
        collar = ("collar", box_hit(-4.6, -1.4, 4.6, -0.4), SIGN, False)
        tail = tail_part([(5.4, 8.0), (9.4, 6.8), (10.8, 2.6), (10.4, -1.2), (8.6 + 0.6 * math.sin(ph), -2.0)])
        parts = sit_parts(tail, front=[paw, hold, coin, bell], mid=[arm, collar], paws=())
        f, _, _ = draw(rig, parts)
        bx, by = rig.cell(pc[0], pc[1])
        if not bend:              # 펼친 발: 큰 젤리 + 발가락 젤리
            for p in ((bx, by), (bx + 1, by), (bx - 1, by - 1), (bx + 2, by - 1)):
                f[p] = PINK
        face(f, rig, mood="happy" if bend else "open")
        whiskers(f, rig, skip=(-1,))
        if bend:                  # 까딱 — 발 옆 짧은 줄
            for p in ((bx - 4, by - 1), (bx - 4, by + 1)):
                f.setdefault(p, OUT)
        frames.append(finish(board(f)))
    return frames


def cross() -> list[dict]:
    """조준선 가운데 파란 나비 — 몸통이 핫스팟. 아래에서 고개를 내민 샴냥이 사시 눈으로 노려본다(눈동자가 안쪽 위).
    나비는 날개를 폈다 접었다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for x in range(1, 31):
            if x < 9 or x > 22:
                f[x, 15] = OUT
        for y in range(1, 9):
            f[15, y] = OUT
        rig = Rig(15.5, 27.4, 0.0, 1.0)
        hc = (0.0, 0.0)
        head = head_only(rig, hc, 7.0, "blink" if k == 9 else "cross", whisk=False)
        f.update(board(head))
        whiskers(f, rig, hc, 7.0)
        f = board(f)
        # 나비: 몸통 (15, 14..16) · 날개
        open_ = k % 4 < 2
        wing = set()
        if open_:
            for dx, dy in ((1, -2), (2, -2), (3, -2), (1, -1), (2, -1), (3, -1), (1, 0), (2, 0), (1, 1), (2, 1),
                           (3, 1), (2, 2)):
                wing |= {(15 + dx, 15 + dy), (15 - dx, 15 + dy)}
        else:
            for dx, dy in ((1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (2, -2), (2, -1)):
                wing |= {(15 + dx, 15 + dy), (15 - dx, 15 + dy)}
        solid(f, wing, WING, BLUE_D)
        for y in (14, 15, 16):
            f[15, y] = INKC
        f[14, 12] = f[16, 12] = INKC   # 더듬이
        frames.append(finish(f))
    return frames


def ibeam() -> list[dict]:
    """글자 커서 I(짙은 갈색, 깜빡이듯 짙었다 옅었다) 오른쪽에서 샴냥이 앞발을 I 에 얹고 조잘댄다 — 입을 열 때마다
    I 왼쪽에 글자 점(파랑)이 하나씩 늘어난다. 핫스팟은 I 가운데"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        stem = PT if k % 6 < 4 else PT_L
        m = set()
        for y in range(4, 28):
            for x in (14, 15, 16):
                m.add((x, y))
        for y in (2, 3, 4):
            for x in range(11, 20):
                m.add((x, y))
        for y in (27, 28, 29):
            for x in range(11, 20):
                m.add((x, y))
        solid(f, m, stem, OUT)
        n = 1 + k // 3            # 글자 점 수 (1–4)
        for i in range(n):          # 새 글자는 늘 커서 바로 왼쪽, 앞 글자들이 왼쪽으로 밀린다
            x = 11 - (n - 1 - i) * 3
            for dx in (0, 1):
                for dy in (0, 1):
                    f[x + dx, 14 + dy] = GLOW[0] if i == n - 1 else GLOW[1]
        rig = Rig(24.2, 17.4, 0.0, 0.56)
        hc = (0.0, -7.6)
        reach = arm_part([(-3.0, -1.4), (-9.6, -2.4)], name="reach", pr=2.0)
        tail = tail_part([(5.4, 8.0), (9.4, 6.8), (10.4, 2.2), (9.6, -1.4), (8.0, -2.0)])
        o, _, _ = draw(rig, sit_parts(tail, hc, turn=-1.0, front=reach[:1], mid=reach[1:], paws=(1,)))
        face(o, rig, hc, HR, "talk" if k % 3 == 1 else "open", turn=-1.0)
        f.update(o)
        frames.append(finish(board(f)))
    return frames


def move() -> list[dict]:
    """앉은 샴냥이 위 · 오른쪽 · 아래 · 왼쪽으로 한 칸씩 콩 옮겨 앉는다 — 가는 쪽 화살촉이 켜지고 반대쪽에 바람 줄"""
    frames = []
    dirs = ((0, -1), (1, 0), (0, 1), (-1, 0))
    for k, ph in enumerate(phases()):
        f = {}
        d = dirs[k // 3]
        st = k % 3                # 0 제자리 · 1 뛰는 중 · 2 옮겨 앉음
        off = (0, 1, 2)[st] * 0.9
        for dd in dirs:
            lit = dd == d
            chevron(f, 15 + dd[0] * 14, 15 + dd[1] * 14, dd[0], dd[1], GLOW[0] if lit else GLOW[2], 3)
        hop = -1.2 if st == 1 else 0.0
        rig = Rig(15.5 + d[0] * off, 17.2 + d[1] * off + hop, 0.0, 0.66)
        tail = tail_part([(5.2, 8.0), (9.0, 6.6), (10.2, 2.0), (9.6, -1.6), (7.8, -2.2)])
        o, _, _ = draw(rig, sit_parts(tail, turn=d[0] * 0.8))
        face(o, rig, mood="blink" if k == 7 else "open", turn=d[0] * 0.8)
        f.update(o)
        if st >= 1:               # 바람 줄 (가는 쪽 반대)
            cx, cy = rig.cell(-d[0] * 9.0, -d[1] * 12.0 - 1.0)
            px, py = -d[1], d[0]
            for j in (-2, 0, 2):
                for i in range(2):
                    f.setdefault((cx + px * j - d[0] * i, cy + py * j - d[1] * i), GLOW[1])
        frames.append(finish(board(f)))
    return frames


def no() -> list[dict]:
    """빨간 금지 표지 안에서 "냐아앙!" — 장 0–6 입을 크게 벌리고 눈은 >< 로 항의(머리가 들썩), 7–11 입을 꾹 다물고
    흥(눈 감음). 머리 오른쪽 위에 느낌표"""
    frames = []
    for k in range(N):
        f = {}
        yowl = k < 7
        rig = Rig(15.5, 16.0 + (-0.6 if yowl and k % 2 else 0.0), 0.0, 0.7)
        hc = (0.0, -1.0)
        fp = ("fpaws", any_of(ell(-2.4, 13.2, 1.9, 1.3), ell(2.4, 13.2, 1.9, 1.3)), PT, True)
        parts = head_parts(hc, 7.4) + [fp, body_part((0.0, 9.6), 6.6, 5.0)]
        o, _, _ = draw(rig, parts)
        face(o, rig, hc, 7.4, "yowl" if yowl else "blink")
        whiskers(o, rig, hc, 7.4)
        f.update(o)
        if yowl or k % 2:         # 느낌표
            for y in range(7, 11):
                f[22, y] = SIGN_D
                f[23, y] = SIGN_D
            f[22, 12] = f[23, 12] = SIGN_D
        sign(f)
        frames.append(finish(board(f)))
    return frames


def pen() -> list[dict]:
    """짙은 꼬리 끝을 붓 삼아 쓴다 — 꼬리 끝(왼쪽 아래)은 그대로, 꼬리 중간이 물결치고, 끝 오른쪽으로 먹 줄이 길어진다.
    샴냥은 오른쪽에 앉아 고개를 돌려 꼬리 끝을 내려다본다"""
    frames = []
    TIP = (4, 27)
    for k, ph in enumerate(phases()):
        f = {}
        for i in range(2 + 2 * k):   # 먹 줄: 꼬리 끝 오른쪽으로 꼬불꼬불 글씨
            f[TIP[0] + 1 + i, 28 + (0, 1, 1, 0)[i % 4]] = INKC
        rig = Rig(22.4, 15.6, 0.0, 0.7)
        hc = (-0.6, -8.0)
        w = 1.2 * math.sin(ph)
        # 꼬리는 화면 좌표로 잡아 끝을 TIP 에 박는다
        pts_s = [(25.6, 22.4), (21.0, 24.0 + 0.3 * w), (15.0, 21.6 + w), (9.6, 21.4 - w), (5.8, 23.8),
                 (TIP[0] + 0.5, TIP[1] + 0.5)]
        pts = [rig.local(*p) for p in pts_s]
        tail = tail_part(pts, 2.2, 1.0)
        o, _, _ = draw(rig, [tail] + sit_parts(None, hc, HR, -1.2))
        face(o, rig, hc, HR, "blink" if k == 6 else "open", -1.2)
        whiskers(o, rig, hc, HR, -1.2, skip=(-1,))
        f.update(o)
        f[TIP] = INKC
        frames.append(finish(board(f)))
    return frames


def up() -> list[dict]:
    """앞모습으로 앉아 꼬리를 머리 오른쪽으로 곧게 세운다 — 꼬리 끝은 왼쪽으로 만 물음표 갈고리이고 그 꼭대기가 핫스팟.
    갈고리 끝만 까딱, 눈은 반가워 ^^ 와 뜬 눈을 오간다"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(14.4, 21.2, 0.0, 0.74)
        sw = math.sin(ph)
        apex = (8.6, -26.0)
        tail = tail_part([(5.4, 7.6), (9.4, 5.0), (10.6, -4.0), (10.4, -14.0), (10.0, -22.0), apex,
                          (6.2 + 0.4 * sw, -24.6), (5.2 + 1.0 * sw, -22.0 + 0.4 * sw)], 1.7, 1.5, lined=True)
        f, _, _ = draw(rig, [tail] + sit_parts(None))
        face(f, rig, mood="happy" if k % 6 < 3 else "open")
        whiskers(f, rig, skip=(1,))
        frames.append(finish(board(f)))
    return frames


def arrows2(f: dict, dx: int, dy: int, ph: float) -> None:
    """크기 조절 칸 양 끝의 파란 화살촉 — 늘어날 때 한 칸 바깥으로 두근"""
    R = 14 if dx == 0 or dy == 0 else 11
    o = 1 if math.sin(ph) > 0.3 else 0
    for sg in (-1, 1):
        chevron(f, 15 + sg * dx * (R + o), 15 + sg * dy * (R + o), sg * dx, sg * dy, GLOW[0] if o else GLOW[1], 3)


def ns() -> list[dict]:
    """앉아서 목을 쭉 빼고 야~옹 — 목이 늘어나 머리가 위 화살촉 쪽으로 오르며 입이 열리고, 줄어들며 닫힌다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        arrows2(f, 0, 1, ph)
        s = max(0.0, math.sin(ph))
        rig = Rig(15.5, 16.0, 0.0, 0.7)
        hc = (0.0, -5.4 - 4.6 * s)
        neck = ("neck", bar((0.0, -1.0), (0.0, hc[1] + 4.0), 3.4, 3.0), CREAM, False)
        tail = tail_part([(5.2, 8.0), (9.0, 6.6), (10.2, 2.0), (9.6, -1.6), (7.8, -2.2)])
        parts = sit_parts(tail, hc, 6.6)
        i = parts.index(next(p for p in parts if p[0] == "feet"))
        o, _, _ = draw(rig, parts[:i] + [neck] + parts[i:])
        face(o, rig, hc, 6.6, "talk" if s > 0.5 else "open" if s > 0.1 else "blink")
        f.update(o)
        frames.append(finish(board(f)))
    return frames


def superman(ang: float) -> list[dict]:
    """배를 깔고 앞발은 앞으로, 뒷발은 뒤로 쭉 뻗은 기지개 — 몸통은 ang 축(도, 0 이면 머리가 왼쪽), 다리가 그 축으로
    늘었다 줄었다 한다. 머리는 앞쪽 끝에 늘 똑바로(기울이면 칸 위에서 뭉개진다), 꼬리는 뒷발 사이로 곧게"""
    frames = []
    t = math.radians(ang)
    dx, dy = round(math.cos(t)), round(math.sin(t))
    sd = 1 if math.cos(t) >= 0 else -1           # 배(발) 쪽이 화면 아래로
    for k, ph in enumerate(phases()):
        f = {}
        arrows2(f, dx, dy, ph)
        s = 1.6 * math.sin(ph)
        rig = Rig(15.5, 15.5, ang, 0.74)
        body = ("body", bar((-3.4, 0.0), (5.0, 0.0), 4.0, 3.6),
                lambda a, b: CREAM_D if b * sd > 1.6 else CREAM, False)
        legs = arm_part([(-3.4, sd * 3.0), (-15.6 - s, sd * 4.2)], r=1.8, pr=2.0, name="fl") + \
            arm_part([(4.6, sd * 2.4), (12.8 + s, sd * 3.0)], r=1.9, pr=2.0, name="bl")
        tail = tail_part([(5.6, -sd * 1.4), (10.0 + 0.5 * s, -sd * 2.6), (13.0 + 0.5 * s, -sd * 4.4)], 1.6, 1.4)
        o, _, _ = draw(rig, legs + [body, tail])
        f.update(o)
        hr = Rig(*rig.world(-5.6, -sd * 0.4), 0.0, 0.74)
        f.update(head_only(hr, (0.0, 0.0), 6.4, "happy" if k % 6 < 2 else "open", whisk=False))
        frames.append(finish(board(f)))
    return frames


def we():
    return superman(0.0)


def nwse():
    return superman(45.0)


def nesw():
    return superman(135.0)


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def top_cell(fr):
    return min((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1], p[0]))


HOT = {"arrow": tip, "busy": tip, "help": tip, "person": tip, "pin": tip,
       "wait": (15, 17), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
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
        if rid in ("arrow", "busy", "help", "person", "pin") and \
                any(c[3] == 255 and (p[0] < 1 or p[1] < 1) for p, c in f.items()):
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

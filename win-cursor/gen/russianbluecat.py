# SPDX-License-Identifier: Apache-2.0
"""러시안블루(russianbluecatanim) 구성표 그림 `art/russianbluecatanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/russianbluecat.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

해달처럼 칸마다 러시안블루가 하는 짓을 따로 그린다(`SCENE`). 같은 묶음(치즈냥 · 턱시도냥 · 까망이 · 고등어냥 · 삼색냥)과
머리 비율(반지름 7 · 세모 귀 · 볼터치 · 1칸 수염)을 맞추되, 러시안블루는 **무늬 없이 매끈한 푸른 은회색**이다 —
고등어냥(회색 줄무늬)과 갈리게 줄을 하나도 안 긋고 색을 푸르게 잡았다. 머리 · 몸의 왼쪽 위에 은빛 털끝(`SHEEN`),
오른쪽 아래에 살짝 짙은 그늘을 줘서 결이 반짝이는 벨벳처럼 보이게 한다. 에메랄드 초록 눈 · 연보라 코 ·
입꼬리가 올라간 ω 입(러시안블루 미소). 성격이 새침해서 대개 얌전히 앉아 있고, 소품의 주인공은 분홍 깃털 낚싯대다
(깃털 · 막대 · 줄). 화살촉 같은 신호색은 눈 색(에메랄드)이다.

  arrow   큰 흰 화살표 뒤에 숨은 러시안블루가 빗변 위로 새침하게 빼꼼 — 은회색 발끝 둘이 빗변을 잡고 장 2–5 에 쏙
          더 올라온다. 화살표 끝이 핫스팟(`sea.peek`, 냥이 10종 공용 틀)
  busy    작은 화살표 러시안블루 + 오른쪽 아래 낚싯대 끝에서 줄에 매달린 깃털이 빙글빙글 돈다(지나간 자리에 잔상)
  cross   가는 조준선 가운데 늘어진 깃털(깃대 가운데가 핫스팟) — 양옆에서 회색 앞발 둘이 젤리를 보이며 다가와 짝! 덮친다
  hand    앉은 러시안블루가 깃털 낚싯대를 쥐고 왼쪽 위로 내민다 — 막대 끝이 핫스팟, 끝에 매달린 깃털이 대롱대롱
  help    작은 화살표 러시안블루 + 에메랄드 물음표, 점 자리에는 깃털 하나가 살랑살랑 내려앉는다
  ibeam   위아래 가름대를 단 곧게 선 깃털이 I — 오른쪽에서 고개를 내민 러시안블루가 앞발로 깃을 톡톡. 핫스팟은 깃대 가운데
  move    가운데 얌전히 앉아 두리번두리번 — 위 · 오른쪽 · 아래 · 왼쪽을 차례로 보고 그쪽 에메랄드 화살촉이 켜진다
  nesw · ns · nwse · we   깃털을 덮치러 그 축으로 몸을 날린다 — 두 앞발을 모아 앞으로, 뒷발과 긴 꼬리는 뒤로 쭉.
          몸이 그 축으로 늘었다 줄었다 하고 양 끝 화살촉이 두근댄다. 얼굴은 늘 똑바로 둔다(기운 얼굴은 칸 위에서 뭉개진다)
  no      빨간 금지 표지 안에서 눈을 꼭 감고 두 앞발을 가슴 앞에 엇갈려 X(안 돼) — 팔을 콕콕 내밀고, 장 6–8 에 눈을 떠 힐끔
  pen     엎드려 은빛 펜촉 만년필을 두 앞발로 쥐고 쓴다 — 펜촉(왼쪽 아래)이 핫스팟, 지나간 자리에 초록 잉크 줄이 자란다
  person  작은 화살표 러시안블루 + 깃털 낚싯대를 흔드는 집사(사람 흉상) — 줄 끝 깃털이 흔들린다
  pin     작은 화살표 러시안블루 + 동그라미 속에 흰 깃털이 든 빨간 지도 핀이 통통 튄다
  up      뒷발로 서서 잡은 깃털을 두 앞발로 머리 위에 번쩍(잡았다!) — 깃털 끝(맨 위)이 핫스팟, 눈은 ^^
  wait    얌전히 앉아 위에서 흔들리는 깃털에 홀렸다 — 고개 · 눈이 깃털을 따라 좌우로, 장 9–10 에 앞발로 냥! 가운데가 핫스팟

몸은 부위(타원 · 굵기가 변하는 막대 · 세모)를 고양이 제 좌표 (u 오른쪽, w 아래)에 놓고 화면으로 돌려 찍는다
(`Rig`, `draw` — 고등어냥 생성기와 같은 방식이지만 다른 생성기에 기대지 않게 여기 따로 둔다).
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, disc, finish, hx, ink, inside, peek, phases, raster, solid, write

SID = "russianbluecatanim"

OUT, EYE = hx("2c3244ff"), hx("142019ff")                        # 테두리 · 눈동자
FUR, FUR_D, SHEEN = hx("8fa0b8ff"), hx("7788a2ff"), hx("bccadcff")   # 푸른 은회색 · 그늘 · 은빛 털끝
MUZ, PAW = hx("a2b2c6ff"), hx("aebcd0ff")                       # 주둥이 · 발 (조금 밝게)
PINK, NOSE, HI = hx("eea2b8ff"), hx("b07a98ff"), hx("ffffffff")  # 볼 · 귀 속 · 젤리 / 연보라 코 / 반짝
GREEN = hx("2fc278ff")                                          # 에메랄드 눈
ink(OUT, HI, hx("e6e8f0c7"))
GLOW = (hx("2fc278ff"), hx("2fc278b0"), hx("2fc27860"))         # 화살촉 · 물음표 (짙은 것부터)
FEA, FEA_L, FEA_D, QUILL = hx("f0628cff"), hx("ffaec4ff"), hx("c8406aff"), hx("fff4f2ff")   # 깃털
STICK, STICK_D, STRING = hx("d0a468ff"), hx("9a7038ff"), hx("5c6274ff")
INK_G = hx("1f9a5cff")                                          # 초록 잉크
PEN, PEN_D, NIB, BAND = hx("2d6a58ff"), hx("1d4a3cff"), hx("d4d8e2ff"), hx("e0b44cff")
SKIN, HAIR = hx("f7d7bcff"), hx("5a3e30ff")
SHIRT, SHIRT_D = hx("e3b341ff"), hx("b88a22ff")                 # 집사 옷 (푸른 냥이와 갈리게 겨자색)


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


SCREEN = Rig(0.0, 0.0)


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


def tri(*pts):
    pl = list(pts)
    return lambda a, b: inside(pl, a, b)


def any_of(*hs):
    return lambda a, b: any(h(a, b) for h in hs)


def draw(rig: Rig, parts: list) -> tuple[dict, set, dict]:
    """parts: [(이름, 맞음(a, b), 색(a, b) 또는 색, 테두리[, 테두리 색])] — 앞의 것이 위에 그려진다.
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
                    for name, hit, *_ in parts:
                        if hit(a, b):
                            hits[name] = hits.get(name, 0) + 1
                            break
            if sum(hits.values()) >= 8:
                mask.add((x, y))
                region[x, y] = max(hits, key=lambda n: (hits[n], -order[n]))
    col = {p[0]: p[2] for p in parts}
    lined = {p[0] for p in parts if p[3]}
    edge = {p[0]: p[4] for p in parts if len(p) > 4}   # 깃털처럼 테두리를 짙은 제 색으로 긋는 부위
    out = {}
    for p in mask:
        c = col[region[p]]
        out[p] = c(*rig.local(p[0] + 0.5, p[1] + 0.5)) if callable(c) else c
        x, y = p
        nb = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        if any(q not in mask for q in nb) or \
                region[p] in lined and any(order[region[q]] > order[region[p]] for q in nb):
            out[p] = edge.get(region[p], OUT)
    return out, mask, region


# ── 몸 부위 ──────────────────────────────────────────────────────────────────
HC, HR = (0.0, -7.5), 7.0       # 머리 가운데 · 반지름 (묶음 공통)


def velvet(ca, cb, ra, rb, base=FUR):
    """매끈한 벨벳 털 — 왼쪽 위 테두리 안쪽에 은빛 털끝, 오른쪽 아래에 살짝 짙은 그늘. 줄무늬는 없다"""
    def col(a, b):
        d = (a - ca) / ra + (b - cb) / rb
        if d < -1.0:
            return SHEEN
        if d > 1.12:
            return FUR_D
        return base
    return col


def head_parts(hc=HC, r=HR, turn=0.0, name="head") -> list:
    """앞모습 머리: 살짝 갸름한 볼 · 넓게 선 큰 세모 귀(속 분홍) · 조금 밝은 주둥이. 눈 · 코 · 입은 `face` 가 칸으로 찍는다"""
    u0, w0 = hc
    head = any_of(ell(u0, w0 - 0.4, r * 0.98, r * 0.86), ell(u0, w0 + 1.0, r * 1.04, r * 0.6))
    ears, inner = [], []
    for sg in (-1, 1):
        base0, tip, base1 = (u0 + sg * r * 1.0, w0 - r * 0.22), (u0 + sg * r * 0.84 + turn * 0.3, w0 - r * 1.4), \
            (u0 + sg * r * 0.12, w0 - r * 0.76)
        ears.append(tri(base0, tip, base1))
        cx, cy = (base0[0] + tip[0] + base1[0]) / 3, (base0[1] + tip[1] + base1[1]) / 3 + r * 0.06
        inner.append(tri(*[(cx + (p[0] - cx) * 0.46, cy + (p[1] - cy) * 0.46) for p in (base0, tip, base1)]))
    inner_hit = any_of(*inner)
    fur = velvet(u0, w0, r, r)

    def skin(a, b):
        mu = a - u0 - turn
        if (mu / (r * 0.4)) ** 2 + ((b - (w0 + r * 0.38)) / (r * 0.27)) ** 2 <= 1:
            return MUZ
        return fur(a, b)

    def ear_col(a, b):
        return PINK if inner_hit(a, b) else SHEEN if a < u0 else FUR
    return [(name, head, skin, True), (name + "_ear", any_of(*ears), ear_col, False)]


def body_part(c=(0.0, 3.0), ra=5.8, rb=6.2, name="body", rot=0.0):
    c0, c1 = c
    return (name, ell(c0, c1, ra, rb, rot), velvet(c0, c1, ra, rb), False)


def tail_part(pts, r0=1.8, r1=1.3, name="tail", lined=False):
    """길게 가늘어지는 매끈한 꼬리 — 무늬 없이 한 빛깔"""
    return (name, chain(pts, r0, r1), FUR, lined)


def leg_part(pts, r=1.9, pr=2.0, name="arm", lined=False):
    """다리 하나 → [발, 다리]. 발은 조금 밝은 푸른 회색(흰 양말이 없다)이고 테두리를 두른다. 다리는 기본으로
    테두리를 안 긋는다 — 다리마다 선을 그으면 매끈한 몸에 짙은 줄이 생겨 고등어냥 줄무늬로 읽혔다"""
    paw = (name + "_paw", ell(*pts[-1], pr, pr), PAW, True)
    return [paw, (name, chain(pts, r, r * 0.92), FUR, lined)]


def feather_part(p0, p1, w=3.0, ph=0.0, name="feather", lined=True, bend=0.0):
    """깃털: p0 깃대 밑동 → p1 끝. 밑동 15% 는 흰 깃대만, 나머지는 통통한 분홍 깃(엇갈린 결이 ph 로 흐른다).
    테두리는 짙은 분홍 — 짙은 남색 테를 두르면 작은 깃털이 테만 남아 막대 · 고리로 읽혔다"""
    x0, y0 = p0
    ex, ey = p1[0] - x0, p1[1] - y0
    L = math.hypot(ex, ey) or 1e-9
    ux, uy = ex / L, ey / L

    def ts(a, b):   # bend: 깃대가 끝으로 갈수록 옆으로 휜다(포물선) — 곧은 작은 깃털은 보석 · 등불로 읽혔다
        da, db = a - x0, b - y0
        t = (da * ux + db * uy) / L
        return t, -da * uy + db * ux - bend * L * t * t

    def hit(a, b):
        t, s = ts(a, b)
        if t < 0 or t > 1:
            return False
        if t < 0.15:
            return abs(s) <= 0.6
        tt = (t - 0.15) / 0.85
        return abs(s) <= max(0.6, w * math.sin(math.pi * min(1.0, 0.1 + tt * 0.9)) ** 0.45)

    def col(a, b):
        t, s = ts(a, b)
        if w < 3.0:   # 작은 깃털은 깃대를 흰 줄로 안 긋고 두 쪽 빛깔로만 가른다 — 흰 깃대 + 분홍 테가 고리 · 보석으로 읽혔다
            return QUILL if t < 0.15 else FEA_L if s < -0.2 else FEA
        if abs(s) < 0.55 and t < 0.8:
            return QUILL
        return FEA_L if int((t * L - abs(s) * 0.8 + ph) / 1.6) % 2 else FEA
    return (name, hit, col, lined, FEA_D)


def plume(p0, p1, ph=0.0, sg=1) -> tuple:
    """줄 끝에 매단 작은 깃털: 가늘고 길게, 끝이 sg 쪽으로 휜다. 곧고 통통한 깃털은 칸 위에서 분홍 보석 · 등불로,
    셋을 부채꼴로 펼친 다발은 위를 가리키는 화살로 읽혔다"""
    return feather_part(p0, p1, w=1.9, ph=ph, bend=0.28 * sg)


def dot(f: dict, x: int, y: int, c: tuple) -> None:
    f[x, y] = c


def face(f: dict, rig: Rig, hc=HC, r=HR, mood="open", turn=0.0, look=(0, 0)) -> None:
    """얼굴: 2×2 에메랄드 눈(흰 반짝 · 짙은 동공) · 연보라 코 · 입꼬리가 올라간 ω 입 · 볼터치.
    작게(k·r < 4.5) 그리면 눈 1×2 · 코 1칸. mood: open · blink · happy(^) · shut(꼭 감은 —)"""
    u0, w0 = hc
    small = rig.k * r < 4.5
    for sg in (-1, 1):
        ex, ey = rig.world(u0 + turn + sg * r * 0.42, w0 - r * 0.06)
        if small:
            x0, y0 = math.floor(ex), math.floor(ey - 0.5)
            if mood == "open":
                dot(f, x0, y0, GREEN)
            dot(f, x0, y0 + 1, EYE)
            continue
        x0, y0 = round(ex - 1), round(ey - 1)
        if mood == "open":
            for dx in (0, 1):
                for dy in (0, 1):
                    dot(f, x0 + dx, y0 + dy, GREEN)
            px = x0 + (1 if look[0] > 0 or (look[0] == 0 and sg < 0) else 0)
            py = y0 + (1 if look[1] >= 0 else 0)
            dot(f, px, py, EYE)
            dot(f, x0 + (0 if px > x0 else 1), y0 + (0 if py > y0 else 1), HI)
        elif mood in ("blink", "shut"):
            dot(f, x0, y0 + 1, EYE)
            dot(f, x0 + 1, y0 + 1, EYE)
        elif mood == "happy":
            dot(f, x0 - 1 if sg < 0 else x0, y0 + 1, EYE)
            dot(f, x0 if sg < 0 else x0 + 1, y0, EYE)
            dot(f, x0 + 1 if sg < 0 else x0 + 2, y0 + 1, EYE)
    nx, ny = rig.world(u0 + turn, w0 + r * 0.16)
    if small:
        dot(f, math.floor(nx), math.floor(ny), NOSE)
    else:
        nl, ny = round(nx) - 1, math.floor(ny)
        dot(f, nl, ny, NOSE)
        dot(f, nl + 1, ny, NOSE)
        # ω 입 — 가운데가 코 밑으로 내려오고 양 끝이 올라간다(러시안블루 미소)
        for p in ((nl - 2, ny + 1), (nl - 1, ny + 2), (nl, ny + 1), (nl + 1, ny + 1), (nl + 2, ny + 2), (nl + 3, ny + 1)):
            dot(f, *p, OUT)
    for sg in (-1, 1):   # 볼터치
        bx, by = rig.world(u0 + turn + sg * r * 0.66, w0 + r * 0.26)
        dot(f, math.floor(bx), math.floor(by), PINK)
        if not small:
            dot(f, math.floor(bx) + (1 if sg < 0 else -1), math.floor(by), PINK)


def whiskers(f: dict, rig: Rig, hc=HC, r=HR, turn=0.0, n=3, skip=()) -> None:
    """볼 바깥으로 뻗은 1칸 수염 둘씩 — 머리 테두리 밖 칸에만 찍는다(얼굴 안에 그으면 콧수염이 된다)"""
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


def anchor(frames: list[dict], target=(1, 1)) -> tuple[list[dict], tuple]:
    """맨 왼쪽 위 불투명 칸(x+y 가 가장 작은 것, 같으면 위)을 target 으로 옮긴다 — 화살표 꼴 칸의 끝"""
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


def seat(sw: float = 0.0, arms=None, hc=HC, turn=0.0) -> list:
    """얌전히 앉은 몸(머리 빼고): 앞발 둘(arms 를 주면 그것으로) · 뒷발 · 엉덩이 · 몸 · 오른쪽으로 감아 올린 긴 꼬리"""
    if arms is None:
        arms = leg_part([(-2.4, 1.0), (-2.4, 8.4)], name="fl", pr=1.9) + \
            leg_part([(2.4, 1.0), (2.4, 8.4)], name="fr", pr=1.9)
    feet = ("feet", any_of(ell(-4.6, 8.9, 2.0, 1.4), ell(4.6, 8.9, 2.0, 1.4)), PAW, True)
    haunch = ("haunch", any_of(ell(-4.6, 6.2, 2.6, 2.8), ell(4.6, 6.2, 2.6, 2.8)), velvet(0.0, 6.0, 7.0, 3.0), False)
    tail = tail_part([(5.0, 8.6), (9.6, 8.0), (11.4 + 0.4 * sw, 3.6), (10.0 + 1.6 * sw, -0.8)], 1.7, 1.2)
    return arms + head_parts(hc, turn=turn) + [feet, haunch, body_part(), tail]


# ── 화살표 러시안블루 ────────────────────────────────────────────────────────
def arrow_cat(ph: float, k: float = 0.8, blink=False) -> dict:
    """새침하게 앉아 낚아챈 깃털을 왼 앞발로 왼쪽 위로 치켜든다 — 깃털 끝이 맨 왼쪽 위.
    깃 결이 흐르고 꼬리가 살랑, 오른 앞발은 얌전히 바닥에"""
    rig = Rig(17.0, 17.0, 0.0, k)
    sw = math.sin(ph)
    paw = (-9.2, -10.2)
    raise_ = leg_part([(-3.6, 0.4), (-8.0, -3.6), paw], name="raise", pr=2.1, lined=False)
    fea = feather_part((paw[0] + 0.6, paw[1] + 0.6), (-17.4, -18.4), w=3.2, ph=-ph * 1.5)
    stand = leg_part([(2.4, 1.0), (2.4, 8.4)], name="fr", pr=1.9)
    parts = [raise_[0], fea] + seat(sw, arms=[raise_[1]] + stand)
    out, _, _ = draw(rig, parts)
    face(out, rig, mood="blink" if blink else "open", look=(-1, -1))
    if k >= 0.7:
        whiskers(out, rig, n=2, skip=(-1,))
    return out


def arrow_frames(small=False):
    fr = [arrow_cat(ph, 0.5 if small else 0.8, blink=k == 7) for k, ph in enumerate(phases())]
    return anchor(fr)


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    def head(x, y, k):
        rig = Rig(x - HC[0] * PEEK_K, y - HC[1] * PEEK_K, 0.0, PEEK_K)
        g, _, _ = draw(rig, seat()[:-1])               # 꼬리는 화살표 뒤라 안 그린다
        face(g, rig, mood="blink" if k == 7 else "open")
        whiskers(g, rig, n=2, skip=(-1,))
        return g
    return [finish(peek(k, head, OUT, FUR)) for k in range(N)]


PEEK_K = 0.74     # 빼꼼 러시안블루 배율


def companion(scene) -> list[dict]:
    """작은 화살표 러시안블루 + scene(k, ph) 이 그리는 소품 — busy · help · person · pin"""
    cats, _ = arrow_frames(small=True)
    frames = []
    for k, ph in enumerate(phases()):
        f = {p: c for p, c in scene(k, ph).items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}
        f.update(cats[k])
        frames.append(finish(f))
    return frames


def busy() -> list[dict]:
    """오른쪽 아래 낚싯대(막대 끝이 가운데)에서 줄에 매달린 깃털이 빙글빙글 돈다 — 지나간 두 자리에 옅은 분홍 잔상"""
    cx, cy = 21.5, 21.5

    def scene(k, ph):
        f = {}
        R = 5.4
        a = 2 * math.pi * k / N - math.pi / 2
        for j, alpha in ((2, "50"), (1, "a0")):   # 잔상
            aj = a - j * 2 * math.pi / N
            p = (round(cx + R * math.cos(aj) - 0.5), round(cy + R * math.sin(aj) - 0.5))
            for q in (p, (p[0] + 1, p[1]), (p[0], p[1] + 1)):
                f[q] = hx("f0628c" + alpha)
        fx, fy = cx + R * math.cos(a), cy + R * math.sin(a)
        n = 8
        for i in range(1, n):   # 줄 — 막대 끝에서 깃털까지
            f[math.floor(cx + (fx - cx) * i / n), math.floor(cy + (fy - cy) * i / n)] = STRING
        ta = a + math.pi / 2   # 깃털은 도는 쪽 뒤로 끌린다
        p0 = (fx + 1.2 * math.cos(a), fy + 1.2 * math.sin(a))
        p1 = (p0[0] - 4.6 * math.cos(ta) * 0.8 + 1.5 * math.cos(a), p0[1] - 4.6 * math.sin(ta) * 0.8 + 1.5 * math.sin(a))
        stick = ("stick", bar((cx, cy), (29.5, 30.0), 0.9), lambda a_, b_: STICK_D if b_ > 27.0 else STICK, True)
        o, _, _ = draw(SCREEN, [feather_part(p0, p1, w=2.6, ph=k), stick])
        f.update(o)
        return f
    return companion(scene)


def help_() -> list[dict]:
    """에메랄드 물음표(2배) — 점 자리에는 깃털 하나가 좌우로 흔들리며 살랑 내려앉는다"""
    def scene(k, ph):
        f = {}
        m = set()
        for j, row in enumerate(QMARK[:5]):
            for i, ch in enumerate(row):
                if ch == "#":
                    for dx in (0, 1):
                        for dy in (0, 1):
                            m.add((17 + 2 * i + dx, 8 + 2 * j + dy))
        grown = m | {(x + dx, y + dy) for x, y in m for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
        solid(f, grown, GREEN)
        sw = math.sin(ph)
        bx, by = 22.5 + 2.2 * sw, 24.0 + 1.2 * abs(math.cos(ph))
        tilt = 0.6 * sw
        p0 = (bx - 4.0 * math.cos(tilt), by - 4.0 * math.sin(tilt) * 0.4 + 1.6)
        p1 = (bx + 4.0 * math.cos(tilt), by + 4.0 * math.sin(tilt) * 0.4 - 1.6)
        o, _, _ = draw(SCREEN, [feather_part(p0, p1, w=2.8, ph=k)])
        f.update(o)
        return f
    return companion(scene)


def person() -> list[dict]:
    """집사(사람 흉상)가 한 손에 깃털 낚싯대를 들고 흔든다 — 막대가 까딱이고 줄 끝 깃털이 흔들린다"""
    def scene(k, ph):
        f = {}
        rig = Rig(20.6, 21.0, 0.0, 0.66)
        sw = math.sin(ph)
        hand_ = (8.4, -1.6)
        tip = (16.0 + 1.2 * sw, -16.0)
        stick = ("stick", bar(hand_, tip, 0.8), STICK, True)
        fist = ("fist", ell(*hand_, 2.0, 2.0), SKIN, True)
        sleeve = ("sleeve", bar((6.4, 4.4), hand_, 2.6), SHIRT_D, True)
        hair = ("hair", any_of(ell(0.0, -12.4, 5.6, 3.6), ell(-4.6, -10.0, 1.6, 2.6), ell(4.6, -10.0, 1.6, 2.6)),
                HAIR, True)
        skin = ("skin", ell(0.0, -9.6, 5.0, 4.8), SKIN, True)
        torso = ("torso", ell(0.0, 6.0, 9.6, 8.0), SHIRT, False)
        out, _, _ = draw(rig, [fist, stick, sleeve, hair, skin, torso])
        for sg in (-1, 1):
            ex, ey = rig.cell(sg * 2.0, -9.2)
            out[ex, ey] = EYE
            out[ex, ey + 1] = EYE if k not in (4, 5) else SKIN
            out[rig.cell(sg * 3.4, -7.2)] = PINK
        mx, my = rig.cell(0.0, -6.6)   # 웃는 입
        out[mx - 1, my] = OUT
        out[mx, my + 1] = OUT
        out[mx + 1, my] = OUT
        # 줄과 깃털 — 막대 끝에서 늘어져 흔들린다
        tx, ty = rig.world(*tip)
        ang = 0.5 * math.sin(ph - 0.8)
        fx, fy = tx + 6.0 * math.sin(ang), ty + 6.0 * math.cos(ang)
        for i in range(1, 7):
            out.setdefault((math.floor(tx + (fx - tx) * i / 7), math.floor(ty + (fy - ty) * i / 7)), STRING)
        o, _, _ = draw(SCREEN, [plume((fx, fy), (fx + 4.4 * math.sin(ang), fy + 6.6 * math.cos(ang)), sg=-1)])
        out.update(o)
        f.update({p: c for p, c in out.items() if p[1] <= 30 and p[0] <= 30})
        return f
    return companion(scene)


def pin() -> list[dict]:
    """빨간 지도 핀 동그라미 속에 흰 깃털 — 통통 튀고 땅에 닿을 때 그림자가 진해진다"""
    def scene(k, ph):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 14.0 + dy
        for x in range(19, 27):
            f.setdefault((x, 28), GLOW[2] if dy else GLOW[1])
        pinm = disc(cx, cy, 6.2) | raster([(cx - 4.4, cy + 3.4), (cx + 4.4, cy + 3.4), (cx, cy + 12.4)])
        solid(f, pinm, SIGN, SIGN_D)
        p0, p1 = (cx - 2.6, cy + 2.6), (cx + 2.8, cy - 2.8)
        quill = feather_part(p0, p1, w=1.7, lined=False)
        _, m, _ = draw(SCREEN, [quill])
        for p in m:
            if p in pinm:
                f[p] = QUILL
        for i in range(-2, 3):   # 깃대 — 분홍 줄 하나로 흰 깃을 가른다
            f[math.floor(cx + i), math.floor(cy - i)] = FEA
        return f
    return companion(scene)


def wait() -> list[dict]:
    """얌전히 앉아 위에서 흔들리는 깃털에 홀렸다 — 고개 · 눈동자가 깃털을 따라 좌우로 가고,
    장 9–10 에 오른 앞발을 들어 냥! 하고 친다. 꼬리 끝이 까딱. 코(16, 16)가 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(16.0, 22.4, 0.0, 0.72)
        sw = math.sin(ph)
        turn = 0.9 * sw
        swat = k in (9, 10)
        arms = leg_part([(-2.4, 1.0), (-2.4, 8.4)], name="fl", pr=1.9)
        if swat:
            arms = leg_part([(2.6, 0.4), (6.4, -6.0), (5.4 + 3.0 * sw, -13.0)], name="fr", pr=2.0, lined=False) + arms
        else:
            arms += leg_part([(2.4, 1.0), (2.4, 8.4)], name="fr", pr=1.9)
        parts = seat(0.4 * math.sin(2 * ph), arms=arms, turn=turn)
        f, _, region = draw(rig, parts)
        keep = {p: f[p] for p, r in region.items() if r.startswith("fr")} if swat else {}
        face(f, rig, mood="open", turn=turn, look=(1 if sw > 0.3 else -1 if sw < -0.3 else 0, -1))
        f.update(keep)
        whiskers(f, rig, turn=turn, n=2)
        # 깃털 진자 — 판 위 가운데에서 줄이 내려온다
        ang = 0.85 * sw
        ax, ay = 16.0, -1.0
        fx, fy = ax + 4.4 * math.sin(ang), ay + 4.4 * math.cos(ang)
        for i in range(1, 9):
            f.setdefault((math.floor(ax + (fx - ax) * i / 9), math.floor(ay + (fy - ay) * i / 9)), STRING)
        o, _, _ = draw(SCREEN, [plume((fx, fy), (fx + 4.0 * math.sin(ang * 1.6), fy + 6.2 * math.cos(ang * 1.6)),
                                        ph=k, sg=1 if ang >= 0 else -1)])
        for p, c in o.items():
            f.setdefault(p, c)
        frames.append({p: c for p, c in finish(f).items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31})
    return frames


def cross() -> list[dict]:
    """가는 조준선 가운데 위에서 늘어진 깃털(깃대 (15, 15)가 핫스팟). 양옆에서 회색 앞발 둘이 분홍 젤리를 보이며
    가로선을 따라 다가오다가 장 6–7 에 짝! 덮친다 — 덮칠 때 깃털이 파르르, 둘레에 반짝 눈금"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        close = {0: 0.0, 1: 0.1, 2: 0.25, 3: 0.4, 4: 0.6, 5: 0.85, 6: 1.0, 7: 1.0, 8: 0.7, 9: 0.4, 10: 0.2, 11: 0.05}[k]
        for y in range(1, 31):   # 세로 조준선 (깃털 위는 낚싯줄)
            f[15, y] = STRING if y < 9 else OUT
        jig = 0.6 if k in (6, 7) else 0.0
        fo, _, _ = draw(SCREEN, [feather_part((15.5, 21.5), (15.5 + (jig if k == 6 else -jig), 8.6), w=3.2, ph=k)])
        f.update(fo)
        parts = []
        for sg in (-1, 1):   # 앞발 바닥(젤리 쪽)을 깃털로 — 발가락 셋이 울퉁불퉁 튀어나와야 발로 읽힌다(매끈한 타원은 플러그였다)
            px = 15.5 + sg * (11.0 - 6.4 * close)
            toes = [ell(px - sg * 2.2, 15.5 + d, 1.2, 1.2) for d in (-2.2, 0.0, 2.2)]
            parts += [(f"p{sg}", any_of(ell(px + sg * 0.4, 15.5, 2.4, 3.2), *toes), PAW, False),
                      (f"a{sg}", bar((15.5 + sg * 18.0, 15.5), (px + sg * 1.4, 15.5), 3.0, 2.2),
                       velvet(15.5, 13.0, 9.0, 3.0), False)]
        po, _, region = draw(SCREEN, parts)
        for sg in (-1, 1):   # 젤리 — 발가락 셋 + 가운데 큰 젤리
            px = 15.5 + sg * (11.0 - 6.4 * close)
            for p in [(math.floor(px - sg * 2.2), 13 + 2 * i) for i in range(3)] + \
                    [(math.floor(px + sg * 0.6), y) for y in (15, 16)] + [(math.floor(px + sg * 0.6) + sg, 15)]:
                if po.get(p) == PAW:
                    po[p] = PINK
        f.update({p: c for p, c in po.items() if 0 <= p[0] <= 31})
        for x in range(1, 31):   # 가로 조준선 — 앞발이 없는 자리
            f.setdefault((x, 15), OUT)
        if k in (6, 7):
            for p in ((11, 10), (20, 10), (11, 20), (20, 20), (10, 9), (21, 9), (10, 21), (21, 21)):
                f.setdefault(p, GLOW[0] if k == 6 else GLOW[1])
        frames.append({p: c for p, c in finish(f).items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31})
    return frames


def hand() -> list[dict]:
    """앉은 러시안블루가 깃털 낚싯대를 쥐고 왼쪽 위로 내민다 — 막대 끝이 핫스팟(장마다 같은 칸).
    끝에서 늘어진 줄에 매달린 깃털이 대롱대롱 흔들리고, 눈이 깃털을 본다"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(21.6, 20.0, 0.0, 0.76)
        sw = math.sin(ph)
        tip = rig.local(4.0, 4.0)
        paw = (-8.4, -3.4)
        hold = leg_part([(-3.4, 0.6), (-6.4, -0.6), paw], name="hold", pr=2.1)
        stick = ("stick", bar(tip, (paw[0] + 2.4, paw[1] + 2.4), 1.0 / 0.76), STICK, True)
        stand = leg_part([(2.4, 1.0), (2.4, 8.4)], name="fr", pr=1.9)
        parts = [hold[0], stick, hold[1]] + seat(0.6 * sw, arms=stand, turn=-1.0)
        f, _, _ = draw(rig, parts)
        face(f, rig, mood="blink" if k == 9 else "open", turn=-1.0, look=(-1, -1))
        whiskers(f, rig, turn=-1.0, n=2, skip=(-1,))
        ang = 0.3 * math.sin(ph)
        ax, ay = 5.0, 5.5
        fx, fy = ax + 8.0 * math.sin(ang), ay + 8.0 * math.cos(ang)
        for i in range(1, 8):
            f.setdefault((math.floor(ax + (fx - ax) * i / 8), math.floor(ay + (fy - ay) * i / 8)), STRING)
        o, _, _ = draw(SCREEN, [plume((fx, fy), (fx + 5.0 * math.sin(ang * 1.4), fy + 8.0 * math.cos(ang * 1.4)),
                                        ph=k)])
        for p, c in o.items():
            f.setdefault(p, c)
        frames.append({p: c for p, c in finish(f).items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31})
    return frames


HAND_TIP = (4, 4)


def ibeam() -> list[dict]:
    """곧게 선 깃털(깃대 x=15)과 위아래 가름대가 I. 오른쪽에서 고개를 내민 러시안블루가 앞발로 깃을 톡톡 —
    칠 때마다 깃 결이 흐른다. 깃대 가운데(15, 15)가 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for x in range(11, 21):   # 가름대
            for y in (2, 29):
                f[x, y] = OUT
        fo, _, _ = draw(SCREEN, [feather_part((15.5, 29.0), (15.5, 2.5), w=3.0, ph=k * 1.5)])
        f.update(fo)
        rig = Rig(25.4, 19.0, 0.0, 0.6)
        tap = k % 4 in (1, 2)
        pa = (-11.6 + (1.2 if tap else -0.4), -3.0 + (1.0 if k % 8 < 4 else -2.0))
        arm = leg_part([(-3.0, -0.4), (-7.0, -2.0), pa], name="tap", pr=2.4, r=2.3, lined=True)
        cat, _, _ = draw(rig, arm + head_parts(turn=-1.2) + [body_part((0.6, 4.0), 5.0, 7.0)])
        face(cat, rig, mood="open", turn=-1.2, look=(-1, 0))
        f.update({p: c for p, c in cat.items() if p[0] <= 30 and p[1] <= 30})
        if tap:
            for p in ((12, 8 + k % 3), (12, 20 - k % 3)):
                f.setdefault(p, FEA_L)
        frames.append(finish(f))
    return frames


def move() -> list[dict]:
    """가운데 얌전히 앉아 두리번두리번 — 장 0–2 위, 3–5 오른쪽, 6–8 아래, 9–11 왼쪽을 본다(고개 · 눈동자).
    보는 쪽 화살촉이 짙게 켜지고 나머지는 옅다"""
    dirs = ((0, -1), (1, 0), (0, 1), (-1, 0))
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        cur = dirs[k // 3]
        for d in dirs:
            o = 1 if d == cur and k % 3 == 1 else 0
            chevron(f, 15 + d[0] * (13 + o), 15 + d[1] * (13 + o), d[0], d[1], GLOW[0] if d == cur else GLOW[2])
        rig = Rig(15.5, 20.2, 0.0, 0.66)
        turn = 1.1 * cur[0]
        hc = (0.0, -7.5 + 0.5 * cur[1])
        cat, _, _ = draw(rig, seat(0.5 * math.sin(ph), hc=hc, turn=turn))
        face(cat, rig, hc, mood="open", turn=turn, look=cur)
        whiskers(cat, rig, hc, turn=turn, n=1)
        f.update(cat)
        frames.append({p: c for p, c in finish(f).items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31})
    return frames


def pounce(ang: float, L0: float, D: float, r: float = 4.8) -> list[dict]:
    """깃털을 덮치러 몸을 날린 러시안블루 — ang 축(도, 0 이 오른쪽, 앞 → 뒤)을 따라 몸이 L0 ± 1.4 로 늘었다 줄었다.
    앞 끝에 똑바로 선 머리와 그 앞으로 모아 뻗은 두 앞발, 뒤 끝에 쭉 뻗은 뒷발 둘과 긴 꼬리.
    늘이지 않은 그림을 축 따라 판 가운데로 옮기고, 양 끝 화살촉 꼭짓점은 판 가운데에서 축 따라 D 칸"""
    t = math.radians(ang)
    ex, ey = math.cos(t), math.sin(t)
    dx, dy = round(ex), round(ey)

    def cat(L, ph, k, shift):
        rig = Rig(15.5 + ex * shift, 15.5 + ey * shift, ang, 1.0)
        sw = math.sin(ph + 1.0)
        body = ("body", ell(0.0, 0.0, L / 2 + 1.0, 3.0), velvet(0.0, 0.0, L / 2 + 1.0, 3.0), False)
        front, pv = -L / 2 - r * 1.5, r * 1.1   # 머리 바로 위에 모으면 왕관 · 모자로 읽혀서 머리 양옆 바깥으로 뻗는다
        paws = ("paws", any_of(ell(front, -pv, 1.6, 1.5), ell(front, pv, 1.6, 1.5)), PAW, True)
        arms = ("arms", any_of(bar((-L / 2 + 1.0, -1.6), (front, -pv), 1.3), bar((-L / 2 + 1.0, 1.6), (front, pv), 1.3)),
                FUR, True)
        hind = ("hind", any_of(bar((L / 2 - 0.6, -1.8), (L / 2 + 3.6, -2.4), 1.3),
                               bar((L / 2 - 0.6, 1.8), (L / 2 + 3.6, 2.4), 1.3)), FUR, False)
        hpaw = ("hpaw", any_of(ell(L / 2 + 3.8, -2.5, 1.4, 1.2), ell(L / 2 + 3.8, 2.5, 1.4, 1.2)), PAW, True)
        tail = tail_part([(L / 2 + 0.8, 0.0), (L / 2 + 4.0, 0.6 * sw), (L / 2 + 7.0, 1.4 * sw)], 1.3, 1.0)
        bo, _, _ = draw(rig, [paws, arms, hpaw, hind, body, tail])
        hxw, hyw = rig.world(-L / 2 - r * 0.45, 0.0)
        hrig = Rig(hxw, hyw, 0.0, 1.0)
        ho, _, _ = draw(hrig, head_parts((0.0, 0.0), r))
        face(ho, hrig, (0.0, 0.0), r, mood="shut" if k in (5, 6) else "open",
             look=(1 if ex < -0.3 else -1 if ex > 0.3 else 0, 1 if ey < -0.3 else -1))
        for p in [p for p, c in bo.items() if p in ho and c in (PAW,)]:
            ho.pop(p)   # 머리 앞으로 뻗은 앞발이 머리에 덮이지 않게
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
    return pounce(90.0, 6.0, 13.5, r=4.6)


def we() -> list[dict]:
    return pounce(0.0, 6.0, 13.5, r=4.6)


def nwse() -> list[dict]:
    return pounce(45.0, 8.0, 18.4, r=4.6)


def nesw() -> list[dict]:
    return pounce(135.0, 8.0, 18.4, r=4.6)


def no() -> list[dict]:
    """빨간 금지 표지 안에서 앉은 러시안블루가 눈을 꼭 감고 두 앞발을 가슴 앞에 엇갈려 X(안 돼) — 장 6–8 에 눈을 떠 힐끔.
    두 발로 눈을 가리는 판은 발과 얼굴 테가 엉켜 얼굴이 짙은 네모가 됐다. 꼬리 끝이 까딱"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        ring = {(x, y) for x in range(32) for y in range(32)
                if 11.4 <= math.hypot(x + 0.5 - 16, y + 0.5 - 16) <= 14.6}
        slash = {(x, y) for x in range(32) for y in range(32)
                 if math.hypot(x + 0.5 - 16, y + 0.5 - 16) < 11.6 and abs((x - y)) <= 1}
        solid(f, ring | slash, SIGN, SIGN_D)
        rig = Rig(16.0, 19.2, 0.0, 0.74)
        peek = k in (6, 7, 8)
        lift = 0.6 * math.sin(2 * ph)   # 엑스 팔을 콕콕 내민다
        # 두 앞발을 가슴 앞에서 엇갈려 X(안 돼) — 발끝이 몸 바깥으로 삐져나와야 X 로 읽힌다. 팔은 테 없이 은빛 털끝
        # 빛깔로만 가른다 — 비스듬한 팔에 테를 그으면 칸 위에서 계단 선이 엉켜 가슴이 그물이 됐다
        cross_arms = []
        for nm, sg in (("xl", -1), ("xr", 1)):
            pts = [(sg * 4.6, 7.0), (-sg * 7.4, -2.6 - lift)]
            cross_arms += [(nm + "_paw", ell(*pts[-1], 1.8, 1.8), SHEEN, False), (nm, chain(pts, 1.0, 1.1), SHEEN, False)]
        cat, _, region = draw(rig, cross_arms + seat(0.5 * math.sin(2 * ph), arms=[]))
        for p, nm in region.items():   # 가슴은 그늘 빛으로 — 은빛 X 가 또렷하게
            if nm in ("body", "haunch") and cat[p] != OUT:
                cat[p] = FUR_D
        face(cat, rig, mood="open" if peek else "shut", look=(-1, 0))
        whiskers(cat, rig, n=1)
        f.update(cat)
        frames.append(finish(f))
    return frames


def pen_parts(Lp: float = 19.0, w: float = 1.7):
    """끝(0, 0)에서 +u 로 뻗은 만년필 — 은빛 펜촉(가운데 틈) · 짙은 초록 몸 · 금빛 띠 · 둥근 꼭지"""
    shape = any_of(tri((0.0, 0.0), (4.6, -w), (4.6, w)), bar((4.6, 0.0), (Lp, 0.0), w))

    def col(a, b):
        if a < 4.6:
            return OUT if abs(b) < 0.35 and a > 1.2 else NIB
        if Lp - 6.0 < a < Lp - 5.0:
            return BAND
        return PEN_D if b > 0.5 else PEN
    return ("pen", shape, col, True)


def pen() -> list[dict]:
    """엎드린 러시안블루가 만년필을 두 앞발로 쥐고 쓴다 — 펜촉(왼쪽 아래)이 핫스팟.
    지나간 자리에 초록 잉크 줄이 물결치며 자라고 꼬리가 살랑"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for i in range(k + 2):   # 잉크 줄
            f[5 + i, 29 + (1 if (i // 2) % 2 else 0)] = INK_G
        rig = Rig(19.0, 14.0, 0.0, 0.72)
        sw = math.sin(ph)
        prig_pts = [rig.local(1.6 + 0.707 * d, 30.4 - 0.707 * d) for d in (0.0, 4.6, 19.0)]
        tip, nibend, end = prig_pts
        L = math.hypot(end[0] - tip[0], end[1] - tip[1])

        def pen_hit(a, b, tip=tip, end=end):
            return pen_parts(L, 1.7 / 0.72)[1](*to_pen(a, b, tip, end))

        def pen_col(a, b, tip=tip, end=end):
            return pen_parts(L, 1.7 / 0.72)[2](*to_pen(a, b, tip, end))
        g1 = (tip[0] + (end[0] - tip[0]) * 0.42, tip[1] + (end[1] - tip[1]) * 0.42)
        g2 = (tip[0] + (end[0] - tip[0]) * 0.64, tip[1] + (end[1] - tip[1]) * 0.64)
        arms = leg_part([(-3.0, 3.0), (-6.0, 6.0), g1], name="a1", pr=2.1, r=1.7) + \
            leg_part([(2.0, 4.0), (-1.0, 6.4), g2], name="a2", pr=2.1, r=1.7)
        loaf = ("loaf", any_of(ell(4.6, 4.0, 8.4, 4.8), ell(1.0, 6.6, 8.6, 2.6)), velvet(4.6, 4.0, 8.4, 4.8), False)
        tail = tail_part([(12.0, 5.4), (15.0, 2.0), (14.0 + 1.4 * sw, -3.0)], 1.5, 1.1)
        parts = [arms[0], arms[2], ("pen", pen_hit, pen_col, True), arms[1], arms[3]] + \
            head_parts(turn=-0.8) + [loaf, tail]
        cat, _, _ = draw(rig, parts)
        face(cat, rig, mood="open", turn=-0.8, look=(-1, 1))
        whiskers(cat, rig, turn=-0.8, n=2, skip=(-1,))
        f.update({p: c for p, c in cat.items() if p[0] <= 30 and p[1] <= 31})
        frames.append(finish(f))
    return frames


def to_pen(a, b, tip, end):
    """고양이 제 좌표 → 만년필 제 좌표(끝이 원점, 몸이 +u)"""
    ex, ey = end[0] - tip[0], end[1] - tip[1]
    L = math.hypot(ex, ey)
    ux, uy = ex / L, ey / L
    da, db = a - tip[0], b - tip[1]
    return da * ux + db * uy, -da * uy + db * ux


def pen_tip(fr):
    return max((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1] - p[0], -p[0]))


def up() -> list[dict]:
    """뒷발로 서서 잡은 깃털을 두 앞발로 머리 위에 번쩍 — 깃털 끝(맨 위)이 핫스팟이라 깃털과 앞발은 안 움직이고,
    깃 결이 흐르고, 눈은 ^^, 꼬리가 살랑"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(15.5, 21.0, 0.0, 0.7)
        sw = math.sin(ph)
        arms = []
        for sg in (-1, 1):
            arms += leg_part([(sg * 4.4, -0.4), (sg * 8.6, -9.0), (sg * 2.2, -17.4)], name=f"u{sg}", pr=2.0, r=1.7, lined=True)
        fea = feather_part((0.0, -15.4), (0.0, -28.0), w=3.4, ph=-ph * 1.5)
        body = body_part((0.0, 3.8), 5.2, 7.0)
        feet = ("feet", any_of(ell(-3.0, 11.2, 2.4, 1.4), ell(3.0, 11.2, 2.4, 1.4)), PAW, True)
        tail = tail_part([(3.6, 9.0), (8.0, 8.4), (9.6 + sw, 4.0), (8.4 + 1.2 * sw, 0.6)], 1.5, 1.1)
        parts = [arms[0], arms[2], fea] + head_parts() + [arms[1], arms[3], feet, body, tail]
        f, _, _ = draw(rig, parts)
        face(f, rig, mood="happy" if k % 6 < 4 else "open", look=(0, -1))
        whiskers(f, rig, n=2)
        frames.append(finish(f))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def top_cell(fr):
    return min((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1], p[0]))


def hand_tip(fr):
    return min((p for p, c in fr[0].items() if c == STICK or c == OUT and p[0] + p[1] < 12),
               key=lambda p: (p[0] + p[1], p[1]))


HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1),
       "wait": (16, 16), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (15, 15),
       "hand": hand_tip, "up": top_cell, "pen": pen_tip}


def check(rid: str, frames: list[dict], hot: tuple) -> None:
    """핫스팟이 장마다 불투명한 칸 위에 있는지 · 판(0–31) 안인지"""
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
        if any(not (0 <= x <= 31 and 0 <= y <= 31) for x, y in f):
            print(f"  ! {rid} {i}장: 판 밖으로 나간 칸이 있음")
        if hot == (1, 1) and any(c[3] == 255 and (p[0] < 1 or p[1] < 1) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 끝보다 왼쪽·위로 나온 칸이 있음")


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

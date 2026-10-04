# SPDX-License-Identifier: Apache-2.0
"""오드아이 흰냥(whitecatanim) 구성표 그림 `art/whitecatanim/*.txt` 를 만든다.
빌드가 부르지 않고 손으로 돌린다 · 빌드 코드 해시와 CI 캐시 키에 안 들어간다.

  python3 gen/whitecat.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

해양 애니처럼 칸마다 흰냥이 그 칸 뜻에 맞는 짓을 따로 그린다(`SCENE`). '냥이 · 애니' 묶음 중 흰냥은
**새하얀 털에 짝짝이 눈** — 보는 쪽 왼눈은 파랑, 오른눈은 금색이다(눈이 실루엣의 표식이라 감는 장도 한쪽씩 감는다).
흰 몸이 흰 바탕에서 사라지지 않게 그늘(연한 푸른 회색, `fur` 가 부위마다 오른쪽 아래를 칠한다)과 차가운 연회색 테를 두른다.
분홍 귀 속 · 코 · 젤리. 소품의 주인공은 파란 우유 접시 · 우유 · 햇살(노란 반짝이)이다.
머리 · 귀 · 몸 비율과 작은 화살표 동반 꼴 · 분홍 발자국 고리는 삼색냥을 따른다.

  arrow   큰 흰 화살표 뒤에 숨은 흰냥이 빗변 위로 빼꼼 — 흰 발끝 둘이 빗변을 잡고 장 2–5 에 쏙 더 올라오며 가끔 금눈만
          찡긋. 화살표 끝이 핫스팟(`sea.peek`, 냥이 10종 공용 틀)
  busy    작은 화살표 흰냥 + 오른쪽 아래 우유 접시(물결이 돈다) 둘레를 도는 분홍 발자국 여덟
  cross   앞모습 얼굴(짝짝이 눈) — 양 볼 수염이 가로 조준선, 위 줄과 턱 밑 줄이 세로선. 턱 밑 줄을 따라 우유 방울이
          또르르 떨어진다. 분홍 코가 핫스팟
  hand    앉아서 앞발 하나를 왼쪽 위로 높이 들어 젤리를 보이며 하이파이브 — 짝 할 때 젤리가 벌어지고 볕 반짝이가 튄다.
          발바닥 꼭대기가 핫스팟
  help    작은 화살표 흰냥 + 엎지른 우유 줄기로 그린 물음표, 점은 똑 떨어져 퍼지는 우유 방울
  ibeam   옆으로 누운 우유갑(위 가로획)에서 쏟아지는 우유 줄기(세로획)가 아래 접시(아래 가로획)로 — I.
          오른쪽에 앉은 흰냥이 혀를 내밀어 줄기를 할짝. 핫스팟은 줄기 가운데
  move    앉은 흰냥 둘레를 볕 조각(노란 반짝)이 빙글 돌고 흰냥이 고개를 돌려 눈으로 쫓는다 — 네 방향 분홍 화살촉
  nesw · ns · nwse · we   배를 깔고 엎드려 앞발은 앞으로 · 뒷발은 뒤로 쭉 뻗는 기지개 — 몸이 그 축을 따라 놓여
          늘었다 줄었다, 발은 늘 몸 아래. 세로는 같은 자세를 세워 벽 짚고 위로 뻗는 꼴. 양 끝 화살촉.
          얼굴은 늘 똑바로 둔다(기운 얼굴은 칸 위에서 뭉개진다)
  no      빨간 금지 표지 안에서 우유 접시를 앞발로 쓱 밀어내며 눈을 감고 고개를 도리도리 — 밀린 접시에서 우유가 출렁
  pen     파란 분필을 두 앞발로 쥐고 바닥에 쓴다 — 분필 끝(왼쪽 아래)이 핫스팟, 파랑 · 금색(눈 색) 분필 줄이 길어진다
  person  작은 화살표 흰냥 + 머리 위에 흰냥이 식빵 자세로 올라앉은 사람(꼬리가 사람 이마 옆으로 살랑)
  pin     작은 화살표 흰냥 + 흰 동그라미 속에 금방울이 든 빨간 지도 핀이 통통 튄다 — 방울이 딸랑 기운다
  up      뒷발로 서서 우유병을 두 앞발로 머리 위에 번쩍 — 병뚜껑(맨 위)이 핫스팟이라 병은 그대로, 몸이 신나서 들썩
  wait    우유 접시에 고개를 숙여 할짝할짝 — 분홍 혀가 들락날락, 우유에 물결, 꼬리 끝 까딱. 가운데가 핫스팟

몸은 부위(타원 · 굵기가 변하는 막대 · 세모)를 고양이 제 좌표 (u 오른쪽, w 아래)에 놓고 화면으로 돌려 찍는다
(`Rig`, `draw` — 삼색냥 생성기와 같은 방식이지만 다른 생성기에 기대지 않게 여기 따로 둔다).
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, SIGN, SIGN_D, disc, finish, hx, ink, inside, peek, peek_tail, phases, raster, solid, write  # noqa: F401

SID = "whitecatanim"

OUT, EYE = hx("3c4052ff"), hx("252836ff")                     # 테두리(차가운 짙은 남회색) · 동공
WHITE, SHADE, SHADE_D = hx("fcfdffff"), hx("dde3eeff"), hx("c3cbdbff")   # 털 · 그늘(연한 푸른 회색) · 짙은 그늘
BLUE, BLUE_D = hx("4a9bf0ff"), hx("2a68c4ff")                 # 파란 눈
GOLD, GOLD_D = hx("f0bb2aff"), hx("bf8410ff")                 # 금색 눈 · 방울
PINK, NOSE, HI = hx("f4a0b0ff"), hx("e27d90ff"), hx("ffffffff")
ink(OUT, HI, hx("e6e8f0c7"))
MILK, MILK_D = hx("ffffffff"), hx("dbe8f5ff")                  # 우유 · 우유 그늘
DISH, DISH_D, DISH_L = hx("6f9fd8ff"), hx("4b77b4ff"), hx("a8c8eeff")   # 우유 접시
SUN, SUN_L = hx("ffd24aff"), hx("fff0a8ff")                    # 볕 반짝이
CHALK, CHALK_L, CHALK_D = hx("8ec4f4ff"), hx("c8e2faff"), hx("5d97d2ff")   # 분필
SHIRT, SHIRT_D, SKIN, HAIR = hx("e88f7aff"), hx("c46d5aff"), hx("f7d7bcff"), hx("5a4034ff")
GLOW = (hx("f4a0b0ff"), hx("f4a0b0b0"), hx("f4a0b060"))   # 발자국 · 화살촉 (짙은 것부터) — 냥이 묶음 공통


# ── 그리개: 고양이 제 좌표 (u, w) → 화면 ─────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도) · 배율 k. ang=0 이면 u 가 오른쪽, w 가 아래. ang 만큼 시계 방향으로 돈다.
    flip=True 면 w 를 뒤집는다(거울) — 기운 축에서도 발(+w)이 화면 아래쪽에 오게"""

    def __init__(self, ox: float, oy: float, ang: float = 0.0, k: float = 1.0, flip: bool = False):
        t = math.radians(ang)
        self.ox, self.oy, self.c, self.s, self.k = ox, oy, math.cos(t), math.sin(t), k
        self.fl = -1.0 if flip else 1.0

    def world(self, a: float, b: float) -> tuple:
        b *= self.fl
        return self.ox + (a * self.c - b * self.s) * self.k, self.oy + (a * self.s + b * self.c) * self.k

    def local(self, x: float, y: float) -> tuple:
        dx, dy = (x - self.ox) / self.k, (y - self.oy) / self.k
        return dx * self.c + dy * self.s, (-dx * self.s + dy * self.c) * self.fl

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
HC, HR = (0.0, -7.5), 7.0       # 머리 가운데 · 반지름(앉은 흰냥 기준)


def fur(cu, cw, r, k=0.42):
    """흰 털 — 부위의 오른쪽 아래(빛 반대쪽)만 연한 푸른 회색 그늘. 흰 바탕에서 몸의 둥근 꼴이 이걸로 보인다"""
    return lambda a, b: SHADE if (a - cu) * 0.5 + (b - cw) > r * k else WHITE


def head_parts(hc=HC, r=HR, turn=0.0, name="head") -> list:
    """앞모습 머리: 옆으로 퍼진 볼 · 세모 귀(속 분홍). 턱과 오른쪽 볼 아래만 그늘"""
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
    shade = fur(u0, w0, r, 0.66)

    def ear_col(a, b):
        return PINK if inner_hit(a, b) else WHITE
    return [(name, head, shade, True), (name + "_ear", any_of(*ears), ear_col, False)]


def body_part(c=(0.0, 3.2), ra=7.2, rb=6.4, name="body"):
    return (name, ell(c[0], c[1], ra, rb), fur(c[0], c[1], max(ra, rb)), False)


def tail_part(pts, r0=1.8, r1=1.4, name="tail", lined=True):
    """흰 꼬리 — 아래쪽 반만 그늘"""
    def col(a, b):
        return SHADE if b > lerp_w(pts, a) else WHITE
    return (name, chain(pts, r0, r1), col, lined)


def lerp_w(pts, a):
    """꺾은선에서 a 에 가장 가까운 꼭짓점의 w — 꼬리 그늘을 가르는 대충의 등선"""
    return min(pts, key=lambda p: abs(p[0] - a))[1]


def arm_part(pts, r=1.7, pr=2.0, name="arm", lined=True):
    """앞발 하나 → [발, 팔] 두 부위. 흰 바탕에서 팔이 몸에 묻히지 않게 팔에도 테두리를 긋는다"""
    paw = (name + "_paw", ell(*pts[-1], pr, pr * 1.05), WHITE, True)
    return [paw, (name, chain(pts, r, r * 0.92), fur(*pts[-1], r * 2, 0.2), lined)]


def dot(f: dict, x: int, y: int, c: tuple) -> None:
    f[x, y] = c


def face(f: dict, rig: Rig, hc=HC, r=HR, mood="open", turn=0.0) -> None:
    """얼굴: 짝짝이 눈(보는 쪽 왼눈 파랑 · 오른눈 금색, 2×2 에 흰 반짝 1칸 · 짙은 동공 1칸) · 분홍 코 · ㅅ 입 · 볼터치.
    작게(k·r < 5) 그리면 눈 1×2(위 홍채 · 아래 짙은 홍채) · 코 1칸.
    mood: open · blink(감은 한 줄) · happy(^ — 골골) · wink(금눈만 ^) · lap(감은 눈 · 입 아래로 혀)"""
    u0, w0 = hc
    small = rig.k * r < 5.0
    for sg in (-1, 1):
        iris, deep = (BLUE, BLUE_D) if sg < 0 else (GOLD, GOLD_D)
        ex, ey = rig.world(u0 + turn + sg * r * 0.42, w0 - r * 0.06)
        shut = mood in ("blink", "lap") or mood == "happy" or (mood == "wink" and sg > 0)
        if small:
            x0, y0 = math.floor(ex), math.floor(ey - 0.5)
            if not shut:
                dot(f, x0, y0, iris)
            dot(f, x0, y0 + 1, deep if not shut else EYE)
            continue
        x0, y0 = round(ex - 1), round(ey - 1)
        if not shut:
            dot(f, x0, y0, HI)
            dot(f, x0 + 1, y0, iris)
            dot(f, x0, y0 + 1, iris)
            dot(f, x0 + 1, y0 + 1, EYE)
        elif mood in ("blink", "lap"):
            dot(f, x0, y0 + 1, EYE)
            dot(f, x0 + 1, y0 + 1, EYE)
        else:     # ^
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
        for p in ((nl - 1, ny + 2), (nl, ny + 1), (nl + 1, ny + 1), (nl + 2, ny + 2)):   # ㅅ 입
            dot(f, *p, OUT)
        if mood == "lap":    # 혀 날름
            for p in ((nl, ny + 2), (nl + 1, ny + 2), (nl, ny + 3), (nl + 1, ny + 3)):
                dot(f, *p, PINK)
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


def head_only(rig, hc=HC, r=HR, mood="open", turn=0.0, whisk=True) -> dict:
    f, _, _ = draw(rig, head_parts(hc, r, turn))
    face(f, rig, hc, r, mood, turn)
    if whisk:
        whiskers(f, rig, hc, r, turn)
    return f


def clip(f: dict) -> dict:
    """판(테 한 칸을 남긴 1–30) 밖을 자른다"""
    return {p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}


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


def sparkle(f: dict, x: int, y: int, big: bool = True) -> None:
    """볕 반짝이 — 노란 + (big 이면 팔이 2칸, 가운데는 연노랑)"""
    f[x, y] = SUN_L if big else SUN
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        f[x + dx, y + dy] = SUN
        if big:
            f.setdefault((x + 2 * dx, y + 2 * dy), hx("ffd24a90"))


def dish_parts(cu=0.0, cw=0.0, rx=4.6, ry=1.6, ripple=None, name="dish"):
    """앞에서 본 우유 접시 — 위는 우유 면(타원), 아래는 파란 접시 몸. ripple 은 우유 면의 물결 고리 반지름(0–1)"""
    def milk(a, b):
        if ripple is not None:
            d = math.hypot((a - cu) / (rx * 0.82), (b - cw) / (ry * 0.7))
            if abs(d - ripple) < 0.16:
                return MILK_D
        return MILK if b - cw < ry * 0.3 else MILK_D

    def body(a, b):
        if b > cw + ry * 1.5:
            return DISH_D
        return DISH_L if a < cu - rx * 0.55 else DISH
    return [(name + "_milk", ell(cu, cw, rx * 0.82, ry * 0.7), milk, True),
            (name, any_of(ell(cu, cw, rx, ry), box_hit(cu - rx * 0.86, cw, cu + rx * 0.86, cw + ry * 1.3),
                          ell(cu, cw + ry * 1.3, rx * 0.72, ry * 0.75)), body, False)]


def sign(f: dict, cx=15.5, cy=15.5, R=13.5) -> set:
    """빨간 금지 표지(둥근 테 + 왼쪽 위 → 오른쪽 아래 빗금) — 칠한 칸 집합을 돌려준다"""
    ring = {p for p in disc(cx, cy, R) if math.hypot(p[0] + 0.5 - cx, p[1] + 0.5 - cy) > R - 2.4}
    slash = set()
    for t in range(-90, 91):
        x, y = cx + t / 100 * (R - 1.5) * 0.7071, cy + t / 100 * (R - 1.5) * 0.7071
        slash |= disc(x, y, 1.3)
    solid(f, ring | slash, SIGN, SIGN_D)
    return ring | slash


# ── 화살표 흰냥 ──────────────────────────────────────────────────────────────
ARROW = [(0.0, 0.0), (0.0, 19.6), (4.4, 15.2), (7.8, 22.6), (10.8, 21.2), (7.4, 14.0), (13.8, 14.0)]   # 끝 (0, 0)


def arrow_cat(ph: float, sc: float = 1.0, ck: float = 0.62, mood="open") -> dict:
    """클래식 흰 화살표(짙은 테) 옆에 흰냥이 붙어 앉아 두 앞발을 화살표 빗변에 걸치고 기댄다 — 화살표 끝이 (1, 1).
    화살표는 통째로 보이게 두고 앞발만 그 위에 겹친다. 꼬리가 살랑, 고개가 화살표 쪽으로 갸웃, 가끔 금눈 찡긋.
    sc 는 화살표 · 자리 배율, ck 는 고양이 배율(작은 판은 고양이를 화살표보다 덜 줄여 얼굴을 살린다).
    처음엔 앞발 하나를 왼쪽 위로 쭉 뻗어 발끝을 핫스팟으로 삼았는데 '팔인지 꼬리인지 들고 있는 거' 로 읽혔다.
    화살표 꼬리 막대를 껴안게도 해 봤는데 팔이 막대를 가로질러 선이 엉키고 막대가 가려 세모로만 보였다"""
    f = {}
    solid(f, raster([(1 + sc * x, 1 + sc * y) for x, y in ARROW]), WHITE, OUT)
    f[1, 1] = OUT
    hug = ck >= 0.55            # 작은 판은 앞발이 한두 칸이라 덩이로 읽혀 팔 없이 화살표 옆에 붙어 앉는다
    rig = Rig(1 + sc * 19.6 + (0.0 if hug else 1.4), 1 + sc * 14.6, 0.0, ck)
    sw = math.sin(ph)
    tilt = -0.5 + 0.5 * math.sin(2 * ph)                  # 화살표 쪽(-u)으로 갸웃
    hc = (-2.0, -7.6)
    paws = [rig.local(1 + sc * x, 1 + sc * y) for x, y in ((11.0, 11.4), (13.2, 13.6))]   # 빗변 위 두 점
    arms = [("paw0", ell(*paws[0], 2.2, 2.0), WHITE, True), ("paw1", ell(*paws[1], 2.2, 2.0), WHITE, True),
            ("arm0", bar((-3.4, -0.6), paws[0], 2.0, 1.9), fur(-4, 0, 3, 0.2), True),
            ("arm1", bar((-2.6, 2.2), paws[1], 2.0, 1.9), fur(-4, 2, 3, 0.2), True)] if hug else []
    parts = arms[:2] + head_parts(hc, 6.6, turn=tilt) + arms[2:] + \
        [("feet", any_of(ell(-2.6, 8.9, 2.2, 1.4), ell(4.4, 8.9, 2.2, 1.4)), WHITE, True),
         ("haunch", ell(4.8, 6.2, 2.9, 2.8), SHADE, True),
         body_part((0.6, 3.4), 6.4, 6.0),
         tail_part([(5.4, 8.2), (9.4, 7.2 + 0.6 * sw), (10.6 + 0.8 * sw, 3.6 + 0.8 * sw)])]
    out, _, _ = draw(rig, parts)
    f.update(out)
    face(f, rig, hc, 6.6, mood=mood, turn=tilt)
    if hug:
        whiskers(f, rig, hc, 6.6, turn=tilt, skip=(-1,))
    return f


def arrow_frames(small=False) -> list[dict]:
    return [arrow_cat(ph, 0.6 if small else 1.0, 0.44 if small else 0.62, "wink" if k in (7, 8) else "open")
            for k, ph in enumerate(phases())]


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    def head(x, y, k):
        rig = Rig(x - HC[0] * PEEK_K, y - HC[1] * PEEK_K, 0.0, PEEK_K)
        g, _, _ = draw(rig, head_parts() + [           # 꼬리는 오른쪽으로 길게 U 자
            ("feet", any_of(ell(-4.4, 8.9, 2.2, 1.4), ell(4.4, 8.9, 2.2, 1.4)), WHITE, True),
            ("haunch", ell(4.8, 6.2, 2.9, 2.8), SHADE, True), body_part(), tail_part(peek_tail(k))])
        face(g, rig, mood="wink" if k in (7, 8) else "open")
        whiskers(g, rig, skip=(-1,))
        return g
    return [finish(peek(k, head, OUT, WHITE)) for k in range(N)]


PEEK_K = 0.74     # 빼꼼 흰냥 배율


def companion(scene) -> list[dict]:
    """작은 화살표 흰냥 + scene(k, ph) 이 그리는 소품 — busy · help · person · pin"""
    cats = arrow_frames(small=True)
    frames = []
    for k, ph in enumerate(phases()):
        f = scene(k, ph)
        f.update(cats[k])
        frames.append(finish(f))
    return frames


def busy() -> list[dict]:
    """우유 접시 둘레를 분홍 발자국 여덟이 차례로 돈다 — 우유 면에 물결 고리가 퍼진다"""
    cx, cy = 22.0, 22.0

    def scene(k, ph):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = round(cx + 7.0 * math.cos(a) - 0.5), round(cy + 7.0 * math.sin(a) - 0.5)
            lag = (head - i) % 8
            paw_print(f, x, y + 1, GLOW[0] if lag < 1.5 else GLOW[1] if lag < 3 else GLOW[2])
        o, _, _ = draw(Rig(cx, cy, 0.0, 1.0), dish_parts(0.0, -1.0, 4.6, 1.8, ripple=(k % 4) / 4 + 0.2))
        f.update(o)
        return f
    return companion(scene)


def help_() -> list[dict]:
    """엎지른 우유 줄기로 그린 물음표 — 점 자리에 우유 방울이 똑 떨어져 납작하게 퍼졌다가 다시 맺힌다"""
    pts = [(17.6, 20.6), (17.6, 18.2), (20.0, 16.0), (23.2, 13.8), (23.4, 10.2), (20.4, 8.4), (17.0, 9.4)]

    def scene(k, ph):
        f = {}
        o, _, _ = draw(Rig(0, 0, 0, 1.0), [("milk", chain(pts, 1.7, 1.5),
                                             lambda a, b: MILK_D if a > 21.8 or b > 19.0 else MILK, True)])
        f.update(o)
        t = k % 6
        if t < 4:      # 맺힌 방울이 떨어진다
            y = 25.0 + t * 0.6
            o, _, _ = draw(Rig(0, 0, 0, 1.0), [("drop", any_of(ell(18.1, y + 0.6, 1.9, 1.9),
                                                                   tri((18.1, y - 2.2), (16.5, y), (19.7, y))),
                                                 MILK, True)])
        else:          # 퍼진 웅덩이
            o, _, _ = draw(Rig(0, 0, 0, 1.0), [("pool", ell(18.1, 27.6, 3.4 if t == 4 else 2.6, 1.2), MILK, True)])
        f.update(o)
        return f
    return companion(scene)


def person() -> list[dict]:
    """사람 머리 위에 흰냥이 식빵 자세로 올라앉았다 — 흰냥 꼬리가 사람 이마 옆으로 늘어져 살랑, 사람은 방긋"""
    def scene(k, ph):
        f = {}
        rig = Rig(22.5, 25.4, 0.0, 0.62)
        parts = [("skin", ell(0.0, -5.4, 4.8, 4.6), SKIN, True),
                 ("hair", any_of(ell(0.0, -9.0, 5.4, 3.0), ell(-4.6, -6.4, 1.3, 2.4), ell(4.6, -6.4, 1.3, 2.4)),
                  HAIR, True),
                 ("neck", box_hit(-1.6, -2.0, 1.6, 0.6), SKIN, True),
                 ("torso", ell(0, 4.4, 8.4, 6.4), lambda a, b: SHIRT_D if a > 4.0 else SHIRT, False)]
        out, _, _ = draw(rig, parts)
        for sg in (-1, 1):
            ex, ey = rig.cell(sg * 1.8, -5.6)
            out[ex, ey] = EYE
            out[rig.cell(sg * 3.0, -3.6)] = PINK
        mx, my = rig.cell(0.0, -2.8)
        out[mx, my] = SHIRT_D
        f.update({p: c for p, c in out.items() if p[1] <= 30})
        # 머리 위 식빵 흰냥
        cat = Rig(22.5, 25.4 - 0.62 * 12.0, 0.0, 0.7)
        sw = 0.8 * math.sin(ph)
        hc = (-2.6, -3.4)
        cparts = head_parts(hc, 4.8) + \
            [("loaf", any_of(ell(1.4, -1.4, 5.8, 2.6), ell(1.4, -0.2, 6.2, 1.4)), fur(1.4, -1.4, 5.8, 0.3), False),
             tail_part([(6.4, -0.6), (7.8, 1.6), (7.8 + sw * 0.4, 5.2 + sw)], 1.2, 1.0)]
        o, _, _ = draw(cat, cparts)
        f.update(o)
        face(f, cat, hc, 4.8, "happy" if k % 6 < 2 else "open")
        return f
    return companion(scene)


def pin() -> list[dict]:
    """빨간 지도 핀 흰 동그라미 속 금방울 — 핀이 통통 튀고, 방울은 딸랑 좌우로 기운다. 땅에 닿을 때 그림자가 짙다"""
    def scene(k, ph):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 15.0 + dy
        for x in range(19, 27):
            f.setdefault((x, 28), GLOW[2] if dy else GLOW[1])
        pinm = disc(cx, cy, 6.2) | raster([(cx - 4.4, cy + 3.4), (cx + 4.4, cy + 3.4), (cx, cy + 12.4)])
        solid(f, pinm, SIGN, SIGN_D)
        solid(f, disc(cx, cy, 4.3), WHITE, SIGN_D)
        tilt = 18.0 * math.sin(2 * ph)
        b = Rig(cx, cy + 0.2, tilt, 1.0)
        bell = [("loop", any_of(bar((-0.7, -2.8), (0.7, -2.8), 0.5)), GOLD_D, False),
                ("bell", ell(0.0, 0.0, 2.6, 2.5), lambda a, bb: GOLD_D if bb > 0.9 or a > 1.4 else GOLD, False)]
        o, _, _ = draw(b, bell)
        f.update(o)
        for p in (b.cell(-0.7, 1.0), b.cell(0.3, 1.0)):    # 방울 틈
            f[p] = OUT
        f[b.cell(-1.0, -1.0)] = HI
        return f
    return companion(scene)


def wait() -> list[dict]:
    """우유 접시에 고개를 숙이고 할짝할짝 — 혀를 내밀 때(장 1–2, 7–8) 고개가 살짝 내려가고 우유에 물결 고리가
    퍼진다. 둥근 등이 머리 뒤로 솟고, 두 앞발은 접시 양옆, 꼬리 끝이 까딱"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(16.0, 15.6, 0.0, 0.9)
        lap = k % 6 in (1, 2)
        hc = (0.0, 0.6 + (0.7 if lap else 0.0))
        tw = 0.8 * math.sin(2 * ph)
        paws = [("paws", any_of(ell(-8.2, 8.0, 2.3, 1.6), ell(8.2, 8.0, 2.3, 1.6)), WHITE, True)]
        dish = dish_parts(0.0, 8.0, 7.6, 1.8, ripple=((k % 6) / 6 + 0.15) if k % 6 >= 1 else None)
        parts = dish[:1] + head_parts(hc, 6.6) + paws + dish[1:] + \
            [("back", ell(0.0, -3.4, 8.6, 4.6), fur(0.0, -3.4, 8.6, 0.3), False),
             tail_part([(6.4, -6.0), (10.6, -8.4), (11.8 + tw * 0.4, -12.0 + tw)], 1.7, 1.4)]
        f, _, _ = draw(rig, parts)
        face(f, rig, hc, 6.6, "lap" if lap else ("blink" if k == 9 else "open"))
        frames.append(finish(clip(f)))
    return frames


def hand() -> list[dict]:
    """앉아서 앞발 하나를 왼쪽 위로 높이 들어 젤리를 보이며 하이파이브 — 짝 할 때(장 3–5, 9–11) 젤리가 벌어지고
    발 둘레에 볕 반짝이가 튄다. 발끝은 그대로 두고 팔꿈치가 굽었다 펴진다. 발바닥 꼭대기가 핫스팟"""
    frames = []
    top = -21.6                       # 발바닥 꼭대기 (w) — 핫스팟이라 장마다 그대로
    for k, ph in enumerate(phases()):
        tap = k % 6 in (3, 4, 5)
        rig = Rig(19.0, 21.4, 0.0, 0.8)
        ra, rb = (3.8, 3.1) if tap else (3.3, 3.4)
        pc = (-7.4, top + rb)
        elbow = (-8.6 + (0.0 if tap else 0.6), -8.6 + (0.8 if tap else 0.0))
        pad = ("pad", ell(pc[0], pc[1], ra, rb), WHITE, True)
        arm = ("arm", chain([(-3.6, -1.0), elbow, (pc[0], pc[1] + 1.6)], 2.4, 2.2), fur(-6, -6, 4, 0.2), True)
        hc = (0.8, -5.8)
        sw = math.sin(ph)
        parts = [pad] + head_parts(hc, 6.8, turn=-0.4) + [arm] + \
            [("down", ell(3.2, 8.4, 2.2, 1.6), WHITE, True),
             ("feet", any_of(ell(-4.4, 9.0, 2.3, 1.4), ell(6.0, 9.0, 2.3, 1.4)), WHITE, True),
             ("haunch", ell(5.6, 6.0, 3.0, 2.9), SHADE, True),
             body_part((0.6, 3.6), 6.8, 6.2),
             tail_part([(6.0, 8.6), (10.0, 7.6 + 0.6 * sw), (11.2 + 0.8 * sw, 3.6 + 0.6 * sw)])]
        f, _, _ = draw(rig, parts)
        bx, by = rig.cell(pc[0], pc[1] + 0.6)
        for p in ((bx - 1, by), (bx, by), (bx - 1, by + 1), (bx, by + 1)):    # 큰 젤리
            f[p] = PINK
        sp = 1 if tap else 0
        for tx, ty in ((-2 - sp, -1), (-1, -2 - sp), (0, -2 - sp), (1 + sp, -1)):   # 발가락 젤리
            f[bx + tx, by + ty] = PINK
        face(f, rig, hc, 6.8, "happy" if tap else "open", turn=-0.4)
        whiskers(f, rig, hc, 6.8, turn=-0.4, skip=(-1,))
        if tap:   # 짝! — 발 양옆 볕 반짝이
            sparkle(f, bx - 6, by - 1, k % 6 == 4)
            sparkle(f, bx + 6, by - 1, k % 6 == 4)
        frames.append(finish(clip(f)))
    return frames


def cross() -> list[dict]:
    """앞모습 얼굴(짝짝이 눈) — 볼 수염이 가로 조준선, 머리 위 줄과 턱 밑 줄이 세로선. 턱에 묻은 우유가 방울져
    줄을 따라 또르르 떨어진다. 코가 핫스팟, 가끔 한쪽 눈 찡긋"""
    frames = []
    rig = Rig(15.5, 14.4, 0.0, 1.0)
    hc = (0.0, -0.4)
    for k, ph in enumerate(phases()):
        f = {}
        tw = round(0.6 * math.sin(2 * ph))
        for x in range(1, 31):
            if x < 6 or x > 25:
                f[x, 15] = OUT
        for sg in (-1, 1):
            f[15 + sg * 10, 14 - tw] = OUT
            f[15 + sg * 10, 16 + tw] = OUT
        for y in list(range(1, 3)) + list(range(24, 31)):
            f[15, y] = OUT
        f.update(head_only(rig, hc, 7.4, "wink" if k in (8, 9) else "open", whisk=False))
        y = 23 + (k % 6) * 1.3        # 우유 방울
        o, _, _ = draw(Rig(0, 0, 0, 1.0), [("drop", any_of(ell(15.5, y + 0.7, 1.3, 1.3),
                                                              tri((15.5, y - 1.4), (14.4, y + 0.5), (16.6, y + 0.5))),
                                            MILK, True)])
        f.update(o)
        frames.append(finish(clip(f)))
    return frames


def ibeam() -> list[dict]:
    """옆으로 누운 우유갑(위 가로획)에서 쏟아지는 우유 줄기(세로획)가 아래 접시(아래 가로획)로 떨어지는 I.
    줄기 속 그늘 줄이 아래로 흐르고 접시에서 방울이 튄다. 오른쪽에 앉은 흰냥이 혀를 내밀어 줄기를 할짝.
    핫스팟은 줄기 가운데"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for x in range(9, 22):       # 우유갑: 흰 몸 · 파란 띠
            for y in range(2, 6):
                edge_ = y in (2, 5) or x in (9, 21)
                f[x, y] = OUT if edge_ else (DISH if y == 3 else WHITE)
        for y in range(6, 27):       # 줄기: 4칸 폭
            for x in range(13, 17):
                if x in (13, 16):
                    f[x, y] = OUT
                else:
                    f[x, y] = MILK_D if (y - k + (x == 15) * 2) % 4 == 0 else MILK
        for x in range(9, 22):       # 접시
            f[x, 27] = OUT if x in (9, 21) else MILK
            f[x, 28] = OUT if x in (9, 21) else (DISH_L if x < 12 else DISH)
            if 10 <= x <= 20:
                f[x, 29] = OUT if x in (10, 20) else DISH_D
            if 11 <= x <= 19:
                f[x, 30] = OUT
        for i, sg in enumerate((-1, 1)):   # 튀는 방울
            t = ((k + 3 * i) % 6) / 6
            f[round(14.5 + sg * (2.5 + 3 * t)), round(26 - 5 * t * (1 - t) * 4)] = MILK
        ext = (0.0, 0.6, 1.0, 1.0, 0.8, 0.0)[k % 6]   # 혀가 나온 정도 — 쭉 뻗었다 도로 감는다
        lap = ext > 0
        rig = Rig(23.4, 19.4, 0.0, 0.62)
        hc = (0.0, -7.6)
        sw = math.sin(ph)
        parts = head_parts(hc, 6.6, turn=-1.2) + \
            [("paw", ell(-3.2, 8.6, 2.2, 1.5), WHITE, True),
             body_part((0.6, 3.4), 6.0, 6.6),
             tail_part([(5.0, 8.4), (9.0, 7.6), (10.0 + 0.6 * sw, 3.0 + 0.6 * sw)], 1.7, 1.4)]
        o, _, _ = draw(rig, parts)
        f.update(o)
        face(f, rig, hc, 6.6, "blink" if lap else "open", turn=-1.2)
        if lap:      # 혀가 줄기까지 날름 — 끝이 아래로 말린 국자꼴, 밑줄은 짙은 분홍이라 두께가 보인다
            # (mx, my) 는 코 칸. 이 크기면 얼굴이 작아 입이 따로 없으니 혀는 코 바로 아랫줄(입 자리)에서 나온다 —
            # 두 줄 아래는 턱 테두리라 혀가 턱 밑에서 나오는 것처럼 읽혔다. 밑줄은 머리 밖에서만 칠해 턱 테두리를 남긴다
            mx, my = rig.cell(-1.2, hc[1] + 6.6 * 0.16)
            tip = mx - max(3, round((mx - 17) * ext))
            for x in range(tip, mx):
                f[x, my + 1] = PINK
            for x in range(tip + 1, mx - 1):
                f[x, my + 2] = NOSE
            f[tip, my + 2] = PINK     # 아래로 말린 끝
            for x in range(tip, mx - 1):   # 혀 바로 위 볼터치는 테두리로 — 붙으면 혀가 볼에서 나오는 것처럼 보인다
                if f.get((x, my)) == PINK:
                    f[x, my] = OUT
            if k % 6 == 4:            # 감아 들일 때 말린 끝 안쪽에 우유 한 모금
                f[tip + 1, my + 2] = MILK_D
        frames.append(finish(clip(f)))
    return frames


def move() -> list[dict]:
    """앉은 흰냥 둘레를 볕 조각이 빙글 — 흰냥이 고개를 돌려 눈으로 쫓는다. 네 방향 분홍 화살촉이 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy, GLOW[0], 3)
        a = ph - math.pi / 2
        sx, sy = 15.5 + 9.6 * math.cos(a), 15.5 + 9.6 * math.sin(a)
        rig = Rig(15.5, 17.6, 0.0, 0.68)
        hc = (0.0, -5.4)
        turn = 1.4 * math.cos(a)
        sw = math.sin(2 * ph)
        parts = head_parts(hc, 6.6, turn=turn) + \
            [("paws", any_of(ell(-2.4, 8.4, 2.0, 1.4), ell(2.4, 8.4, 2.0, 1.4)), WHITE, True),
             ("haunch", any_of(ell(-5.2, 6.4, 2.8, 2.6), ell(5.2, 6.4, 2.8, 2.6)),
              lambda u, w: SHADE if u > 0 else WHITE, True),
             body_part((0.0, 3.6), 6.4, 5.8),
             tail_part([(5.0, 8.4), (9.0, 7.4), (10.0 + 0.6 * sw, 3.4 + 0.6 * sw)], 1.6, 1.3)]
        out, _, _ = draw(rig, parts)
        f.update(out)
        face(f, rig, hc, 6.6, "open", turn=turn)
        whiskers(f, rig, hc, 6.6, turn=turn)
        sparkle(f, math.floor(sx), math.floor(sy), k % 2 == 0)
        frames.append(finish(clip(f)))
    return frames


def no() -> list[dict]:
    """빨간 금지 표지 안에서 우유 접시를 앞발로 쓱 밀어내며 고개를 도리도리 — 눈은 질끈, 밀린 접시에서 우유가
    출렁 튄다. 앞발은 장 0–5 동안 내밀고 6–11 동안 거둔다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        push = 2.0 * math.sin(math.pi * k / N)
        rig = Rig(17.6, 16.6, 0.0, 0.66)
        turn = 1.2 if (k // 2) % 2 else -0.2
        hc = (1.0, -5.6)
        dc = -9.6 - push
        arm = arm_part([(-2.6, 1.4), (dc + 4.0, 5.4)], r=1.6, pr=1.8, name="arm")
        dish = dish_parts(dc, 7.0, 5.8, 2.4, ripple=0.6 if push > 1.0 else None)
        parts = arm + head_parts(hc, 6.6, turn=turn) + dish + \
            [("feet", ell(3.4, 9.6, 2.2, 1.4), WHITE, True),
             body_part((1.4, 4.0), 6.2, 6.0),
             tail_part([(6.4, 8.6), (9.6, 6.8), (10.0, 3.4)], 1.5, 1.3)]
        out, _, _ = draw(rig, parts)
        f.update(out)
        face(f, rig, hc, 6.6, "blink", turn=turn)
        if push > 1.2:   # 출렁 튄 우유
            x, y = rig.cell(dc - 1.0, 3.6)
            f[x, y] = MILK
            f[x - 2, y + 1] = MILK
        sign(f)
        frames.append(finish(clip(f)))
    return frames


def pen() -> list[dict]:
    """파란 분필을 두 앞발로 쥐고 바닥에 쓴다 — 분필은 끝(왼쪽 아래)을 축으로 까딱이고, 끝 오른쪽으로 파랑 · 금색
    분필 줄이 차츰 길어진다. 분필 끝이 핫스팟"""
    frames = []
    TIP = (4, 27)
    for k, ph in enumerate(phases()):
        d = 4.0 * math.sin(2 * ph)
        ck = Rig(TIP[0] + 0.5, TIP[1] + 0.5, -48.0 + d, 1.0)     # 분필이 오른쪽 위로
        def chalk_col(a, b):     # 닳은 끝 · 굵은 몸 · 두 줄 띠
            if a < 2.4 or 5.2 < a < 6.2 or 9.4 < a < 10.4:
                return CHALK_D
            return CHALK_L if b < -0.5 else CHALK
        chalk = [("chalk", any_of(tri((0.0, 0.0), (2.6, -1.9), (2.6, 1.9)), bar((2.4, 0), (12.6, 0), 1.9)),
                  chalk_col, False)]
        o, _, _ = draw(ck, chalk)
        rig = Rig(20.6, 19.6, 0.0, 0.7)
        hc = (0.0, -10.4)
        p1, p2 = rig.local(*ck.world(7.6, 0.0)), rig.local(*ck.world(11.4, 0.0))
        back = head_parts(hc, 6.8, turn=-0.8) + \
            [("arm1", bar((-3.4, 1.0), p1, 1.8), fur(-4, 4, 3, 0.2), True), ("arm2", bar((-2.6, -2.4), p2, 1.8), WHITE, True),
             body_part((0.6, 2.8), 6.4, 7.0),
             tail_part([(5.4, 8.4), (10.0, 7.4), (11.4 + 0.6 * math.sin(ph), 3.0)], 1.6, 1.3)]
        f, _, _ = draw(rig, back)
        face(f, rig, hc, 6.8, "wink" if k == 6 else "open", turn=-0.8)
        whiskers(f, rig, hc, 6.8, turn=-0.8, skip=(-1,))
        f.update(o)
        paws, _, _ = draw(rig, [("pa", ell(*p1, 2.2, 2.0), WHITE, True), ("pb", ell(*p2, 2.2, 2.0), WHITE, True)])
        f.update(paws)
        for i in range(2 + k):   # 분필 줄: 끝 오른쪽으로 물결치며 길어진다
            f.setdefault((TIP[0] + 2 + i, 29 - (1 if (i // 2) % 2 else 0)), CHALK_D if (i // 3) % 2 == 0 else GOLD)
        f[TIP] = CHALK_D
        frames.append(finish(clip(f)))
    return frames


def up() -> list[dict]:
    """뒷발로 서서 우유병을 두 앞발로 머리 위에 번쩍 — 병뚜껑(맨 위)이 핫스팟이라 병은 장마다 그대로고, 몸만 신나서
    들썩이며 팔이 늘었다 줄었다. 꼬리가 살랑, 눈은 웃다가 가끔 뜬다"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(15.5, 21.4, 0.0, 0.74)
        bob = 0.8 * abs(math.sin(ph))
        hc = (0.0, -6.0 + bob)

        def bottle(a, b):        # 파란 뚜껑 · 빈 유리 목(연파랑) · 우유가 찬 몸(오른쪽 그늘)
            if b < -24.4:
                return BLUE if a < 1.0 else BLUE_D
            if b < -20.6:
                return DISH_L
            return MILK_D if a > 2.0 else MILK
        btl = [("cap", box_hit(-2.2, -26.4, 2.2, -24.2), bottle, True),
               ("bottle", any_of(box_hit(-1.7, -25.0, 1.7, -20.0), ell(0.0, -19.6, 4.2, 2.2),
                                 box_hit(-4.2, -19.6, 4.2, -14.4), ell(0.0, -14.4, 4.2, 1.0)), bottle, False)]
        # 두 앞발이 병 밑 모서리를 받쳐 든다(트로피처럼) — 팔은 귀 바깥으로
        paws = [("paws", any_of(ell(-4.6, -14.0, 2.2, 1.9), ell(4.6, -14.0, 2.2, 1.9)), WHITE, True)]
        arms = [("arms", any_of(bar((-4.6, 0.4 + bob), (-6.4, -8.0), 1.8), bar((-6.4, -8.0), (-4.8, -13.0), 1.7),
                                bar((4.6, 0.4 + bob), (6.4, -8.0), 1.8), bar((6.4, -8.0), (4.8, -13.0), 1.7)),
                 fur(0, -8, 4, 0.2), True)]
        sw = math.sin(ph)
        parts = paws + btl + head_parts(hc, 6.4) + arms + \
            [("feet", any_of(ell(-3.4, 10.2, 2.3, 1.4), ell(3.4, 10.2, 2.3, 1.4)), WHITE, True),
             body_part((0.0, 3.4 + bob * 0.5), 5.6, 6.8),
             tail_part([(4.6, 8.0), (9.0, 7.0 + sw), (10.0 + 0.6 * sw, 2.6 + sw)], 1.6, 1.3)]
        f, _, _ = draw(rig, parts)
        face(f, rig, hc, 6.4, "open" if k in (4, 5, 10, 11) else "happy")
        frames.append(finish(clip(f)))
    return frames


def arrows2(f: dict, dx: int, dy: int, ph: float) -> None:
    """크기 조절 칸 양 끝의 분홍 화살촉 — 늘어날 때 한 칸 바깥으로 두근"""
    R = 14 if dx == 0 or dy == 0 else 11
    o = 1 if math.sin(ph) > 0.3 else 0
    for sg in (-1, 1):
        chevron(f, 15 + sg * dx * (R + o), 15 + sg * dy * (R + o), sg * dx, sg * dy, GLOW[0] if o else GLOW[1], 3)


def stretch(ang: float, flip: bool = False) -> list[dict]:
    """배를 깔고 엎드려 앞발을 앞으로 쭉 뻗는 기지개 — 옆에서 본 몸이 ang 축(도, 0 이면 머리가 왼쪽)을 따라 놓인다.
    앞발 하나는 머리 쪽 끝으로, 뒷발 하나는 반대 끝으로 바닥을 따라 쭉 뻗고, 꼬리는 위로 살랑. 늘 때(장 0–5)
    앞발 · 엉덩이 · 뒷발이 더 나간다. 발은 늘 몸 아래(+w) — 기운 축에서 +w 가 화면 위로 가면 flip 으로 거울.
    세로(90)는 같은 자세를 세운 것이라 벽을 짚고 서서 앞발을 위로 뻗는 꼴이 된다. 머리는 앞발 위에 늘 똑바로
    (기운 얼굴은 칸 위에서 뭉개진다). 다리는 안쪽 테 없이 몸과 한 실루엣으로 — 32칸에서 다리마다 테를 두르면
    검은 막대가 얽혀 읽히지 않았다.
    처음엔 볕 웅덩이에 벌러덩 누워 버둥대는 꼴이었는데 '팔다리가 왜 위에 있냐'는 말을 들었다. 세로를 앞모습으로
    세워 두 앞발을 머리 위로 들면 팔이 토끼 귀로 읽혔다"""
    frames = []
    t = math.radians(ang)
    dx, dy = round(math.cos(t)), round(math.sin(t))
    G = 5.6                                               # 바닥선 (w)
    for k, ph in enumerate(phases()):
        f = {}
        rig = Rig(15.5, 15.5, ang, 0.7, flip)
        s = math.sin(ph)
        e = 8.0 + 1.4 * s                                 # 엉덩이 (u)
        tip = -14.6 - 1.0 * s                             # 앞발 끝 (u)
        arrows2(f, dx, dy, ph)

        def belly(a, b):         # 위는 흰 등, 바닥 쪽 배는 그늘
            line = 1.2 + (0.4 - 1.2) * (a + 2.6) / (e + 2.6)
            return SHADE if b - line > 1.4 else WHITE
        tw = 0.8 * math.sin(2 * ph)
        # 다리는 굵게(반지름 2.1–2.3) — 더 가늘면 32칸에서 테만 남아 검은 막대로 읽힌다
        back = e + 6.0 + 0.6 * s                          # 뒷발 끝 (u)
        # 세로(벽 짚고 선 기지개)는 꼬리를 등 쪽으로 말아 올린다 — 엉덩이 뒤로 뻗으면 발 하나로 읽힌다
        curl = [(e + 2.2, -1.8), (e + 1.8, -5.4), (e - 1.8 + tw, -6.6)] if dx == 0 else None
        parts = [("fore_p", ell(tip + 1.4, G - 1.0, 2.6, 1.9), WHITE, False),
                 ("fore", bar((-2.0, 2.4), (tip + 2.4, G - 1.4), 2.3, 2.1), fur(-6, 3, 4, 0.3), False),
                 ("hind_p", ell(back - 1.4, G - 1.0, 2.6, 1.9), WHITE, False),
                 ("hind", any_of(ell(e - 0.6, 1.6, 3.0, 3.2), bar((e, 2.6), (back - 2.4, G - 1.4), 2.3, 2.1)),
                  fur(e, 1.6, 3.2, 0.3), False),
                 ("body", bar((-2.6, 1.2), (e, 0.4), 4.0, 3.8), belly, False),
                 tail_part(curl or [(e + 2.6, -1.6), (e + 4.6, -4.0), (e + 3.8 + tw, -7.2)], 1.6, 1.3)]
        o, _, _ = draw(rig, parts)
        f.update(o)
        hr = Rig(*rig.world(-4.6 - 0.3 * s, -2.6), 0.0, 0.7)
        f.update(head_only(hr, (0.0, 0.0), 6.2, "blink" if k in (5, 11) else "open", whisk=False))
        frames.append(finish(clip(f)))
    return frames


def ns():
    return stretch(90.0)


def we():
    return stretch(0.0)


def nwse():
    return stretch(45.0)


def nesw():
    return stretch(135.0, flip=True)


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

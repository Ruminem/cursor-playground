# SPDX-License-Identifier: Apache-2.0
"""까망이(blackcatanim) 구성표 그림 `art/blackcatanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/blackcat.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

해양 애니처럼 칸마다 까망이가 그 칸 뜻에 맞는 짓을 따로 그린다(`SCENE`). '냥이 · 애니' 셋(치즈냥 · 턱시도냥 · 까망이)
중 까망이는 **작은 아기 고양이**다 — 머리가 몸보다 크고 귀가 크며, 노란 눈이 실루엣 안에서 제일 밝다.
몸은 짙은 회흑(순검정이면 어두운 바탕에서 테만 남는다)에 왼쪽 위 털 결만 살짝 밝다. 분홍 코 · 귀 속 · 발바닥 젤리,
소품의 주인공은 분홍 털실 공이다. 눈이 커서 부엉이로 읽히지 않게 세모 귀 · 수염 · 고양이 꼬리를 늘 살린다.

  arrow   오른쪽 아래 앉은 까망이가 발치 털실 공에서 뽑은 실을 한 앞발로 쥐어 왼쪽 위로 당긴다 — 실 끝이 핫스팟.
          당길 때마다 실이 출렁, 꼬리가 살랑
  busy    작은 화살표 까망이 + 오른쪽 아래 털실 공 둘레를 차례로 도는 발자국(젤리) 여덟
  cross   앞모습 얼굴 — 양 볼 수염이 가로 조준선, 위에서 늘어진 털실과 턱 밑 털실이 세로선. 사냥 눈(동공이 커졌다
          작아졌다). 분홍 코가 핫스팟
  hand    종이 상자에 쏙 들어앉아 앞발 하나를 쑥 내밀어 톡 — 분홍 젤리가 보이는 발끝이 핫스팟
  help    작은 화살표 까망이 + 털실 한 가닥으로 그린 물음표, 점은 작은 털실 공이 통통
  ibeam   위아래 매듭으로 묶어 늘어뜨린 털실 한 가닥이 I — 옆에 앉은 까망이가 앞발로 실을 톡톡 친다. 실은 S 자로
          흔들려도 가운데(핫스팟)는 제자리
  move    털실 공을 쫓아 제자리에서 폴짝폴짝 — 네 방향 분홍 화살촉
  we      두 앞발을 양옆으로 쭉 뻗어 털실을 팽팽히 당긴다 — 실이 앞발에서 양 끝 화살촉까지
  ns      위에서 내려온 털실에 한 앞발로 매달려 대롱대롱 — 뒷발 · 꼬리가 아래 화살촉 쪽으로 늘어졌다 줄었다
  nwse · nesw   한 앞발은 위 대각선, 다른 앞발은 아래 대각선으로 뻗어 그 축의 털실을 당긴다
          (몸은 바로 서고 팔만 축을 탄다 — 몸째 돌리면 얼굴이 기울어 글자로 읽혔다)
  no      빨간 금지 표지 안에서 등을 아치로 세우고 털과 꼬리를 빵빵하게 부풀려 하악 — 귀는 납작
  pen     분홍 구슬 꼭지 뜨개바늘(뜨개코가 걸린)을 두 앞발로 쥐고 실로 글씨를 쓴다 — 바늘 끝(왼쪽 아래)이 핫스팟,
          실이 물결 글씨로 길어진다
  person  작은 화살표 까망이 + 까만 고양이 귀 후드를 쓴 사람이 손을 흔든다
  pin     작은 화살표 까망이 + 빨간 지도 핀 동그라미 속 분홍 발자국이 통통 튄다
  up      뒷발로 서서 한 앞발은 위로 쭉, 다른 앞발로 냥냥펀치 — 위로 뻗은 발끝이 핫스팟
  wait    앉아서 분홍 털실 공을 두 앞발로 이리저리 굴리며 논다 — 눈이 공을 따라간다. 가운데가 핫스팟

몸은 부위(타원 · 막대 · 세모)를 고양이 제 좌표에 놓고 화면으로 돌려 찍는다(`Rig`, `draw`).
몸은 늘 앞모습(`kit`) 한 벌이고, 눈 · 코 · 수염은 화면 칸에 직접 찍는다(`face`).
화살표는 처음에 귀 끝 · 덮치는 옆모습으로 해 봤는데, 귀 끝은 몸을 기울이면 반대쪽 귀가 더 높이 솟고, 45도로
눕힌 검은 옆모습은 32칸에서 도마뱀 · 강아지로 읽혀서 털실 끝으로 했다(치즈냥 · 고등어냥 · 삼색냥은 앞발 끝이다).
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, disc, finish, hx, ink, inside, phases, solid, write

SID = "blackcatanim"

OUT = hx("0b0b12ff")                                              # 테두리
FUR, FUR_L, FUR_D = hx("2a2a35ff"), hx("4a4a5eff"), hx("1d1d27ff")  # 털 · 털 결 하이라이트 · 그늘
EYE, PUPIL, HI = hx("ffd23cff"), hx("15151cff"), hx("ffffffff")    # 노란 눈 · 동공 · 반짝
LID = hx("9a9ab4ff")                                              # 감은 눈 · 입 (검은 털 위에 짙은 선은 안 보인다)
PINK, PINK_D = hx("f7a3baff"), hx("d76f8eff")                     # 코 · 귀 속 · 젤리
BLUSH = hx("e8789aff")
WHISK = hx("b8b8ccd8")                                            # 수염 (반투명 — 테를 안 두른다)
YARN, YARN_D, YARN_L, YARN_O = hx("f27aa8ff"), hx("c84c80ff"), hx("ffc2daff"), hx("7a2148ff")   # 털실
MAW, FANG = hx("b02848ff"), hx("ffffffff")                        # 하악 벌린 입 · 송곳니
ink(OUT, HI)
BOX, BOX_D, BOX_L = hx("c99a5eff"), hx("9c6f3cff"), hx("e2bd85ff")   # 종이 상자
NEEDLE, NEEDLE_D, KNOB = hx("cfd3dcff"), hx("8a90a0ff"), hx("f27aa8ff")
SHIRT, SHIRT_D, SKIN = hx("4a7fb5ff"), hx("2e5a88ff"), hx("f2c9a0ff")
PAD = (hx("f7a3baff"), hx("f7a3bab0"), hx("f7a3ba68"))             # 발자국 고리 (앞장 → 꼬리)


# ── 그리개: 고양이 제 좌표 (a, b) → 화면 ─────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도, a 축이 화면에서 가리키는 쪽, 90 이 아래) · 배율 k.
    b 축은 a 축을 시계 방향으로 90도 돌린 쪽(ang=0 이면 a 가 오른쪽, b 가 아래)"""

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


def path(pts, r0, r1=None, fluff=0.0, n=0):
    """꺾은선을 따라가는 굵기 r0 → r1 의 줄(꼬리 · 등). fluff 면 n 번 삐죽삐죽 부푼 털"""
    r1 = r0 if r1 is None else r1
    segs, tot = [], 0.0
    for p, q in zip(pts, pts[1:]):
        d = math.hypot(q[0] - p[0], q[1] - p[1])
        segs.append((p, q, tot, d))
        tot += d

    def hit(a, b):
        for p, q, s0, d in segs:
            ex, ey = q[0] - p[0], q[1] - p[1]
            t = max(0.0, min(1.0, ((a - p[0]) * ex + (b - p[1]) * ey) / (d * d or 1e-9)))
            u = (s0 + t * d) / tot
            r = r0 + (r1 - r0) * u + (fluff * abs(math.sin(u * math.pi * n)) if fluff else 0.0)
            if (a - p[0] - ex * t) ** 2 + (b - p[1] - ey * t) ** 2 <= r * r:
                return True
        return False
    return hit


def poly(pts):
    return lambda a, b: inside(pts, a, b)


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


def sheen(out: dict) -> dict:
    """털 결: 왼쪽 위 테두리 바로 안쪽 털 칸을 살짝 밝힌다 — 검은 고양이가 납작한 검은 덩이로 안 보이게"""
    f = dict(out)
    for (x, y), c in out.items():
        if c == FUR and (out.get((x - 1, y)) == OUT or out.get((x, y - 1)) == OUT) \
                and out.get((x - 1, y - 1)) in (OUT, None) and out.get((x + 1, y)) != OUT:
            f[x, y] = FUR_L
    return f


def stack(*layers) -> dict:
    """앞 → 뒤 차례의 조각들을 겹친다(앞 조각이 칸을 갖는다)"""
    f = {}
    for lay in layers:
        for p, c in lay.items():
            f.setdefault(p, c)
    return f


def clip(f: dict) -> dict:
    return {p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}


# ── 얼굴: 화면 칸에 직접 찍는다 ─────────────────────────────────────────────────
def eye_rows(size: str, mood: str, look: int = 0) -> list:
    """눈 하나 칸판 — Y 노랑 · P 동공 · W 반짝 · L 감은 눈 줄. look 은 동공을 옆으로(-1 · 0 · 1)"""
    if size == "big":
        if mood in ("blink", "happy"):
            return ["....", ".LL.", "L..L", "...."]
        if mood == "wide":           # 놀라 동공이 바늘처럼
            c = 2 if look > 0 else 1
            rows = [list(".YY."), list("YYYY"), list("YYYY"), list(".YY.")]
            rows[1][c] = rows[2][c] = "P"
            return ["".join(r) for r in rows]
        if mood == "hunt":           # 사냥: 동공이 꽉 찬다
            return [".PP.", "PWPP", "PPPP", ".YY."]
        c = 1 + look
        rows = [list(".YY."), list("YYYY"), list("YYYY"), list(".YY.")]
        for j in (1, 2):
            for i in (c, c + 1):
                if 0 <= i < 4:
                    rows[j][i] = "P"
        if 0 <= c < 4:
            rows[1][c] = "W"
        return ["".join(r) for r in rows]
    if size == "mid":   # 노란 마름모 속 동공 — 2칸 너비 막대 눈은 괄호 · 고글로 읽혔다
        if mood == "happy":
            return [".L.", "L.L", "..."]
        if mood == "blink":
            return ["...", "LLL", "..."]
        if mood == "wide":
            return ["YYY", "YPY", ".Y."]
        return [".Y.", "YPW", ".Y."]
    if mood in ("blink", "happy"):
        return ["..", "LL"]
    return ["YY", "YP"]


EYE_COL = {"Y": EYE, "P": PUPIL, "W": HI, "L": LID}


def put(f: dict, rows: list, x0: int, y0: int, cmap=EYE_COL) -> None:
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in cmap:
                f[x0 + i, y0 + j] = cmap[ch]


def at(rig: Rig, a: float, b: float, w: int, h: int) -> tuple:
    """제 좌표 (a, b) 를 가운데로 하는 w × h 칸판의 왼쪽 위 칸"""
    x, y = rig.world(a, b)
    return math.floor(x - w / 2 + 0.5), math.floor(y - h / 2 + 0.5)


def face(f: dict, rig: Rig, hc=(0.0, -5.5), s: float = 1.0, mood: str = "open", look: int = 0,
         whiskers: bool = True) -> None:
    """앞모습 얼굴: 큰 노란 눈 둘 · 분홍 코 · ㅅ 입 · 볼터치 · 양 볼 수염(반투명)"""
    u0, w0 = hc
    sc = s * rig.k
    size = "big" if sc >= 0.8 else "mid" if sc >= 0.5 else "small"
    rows = eye_rows(size, mood, look)
    w, h = len(rows[0]), len(rows)
    nx, ny = rig.cell(u0, w0 + 1.7 * s)
    level = abs(rig.s) < 1e-6
    ex = 3.2 if size == "big" else 3.9      # 가운데 크기 눈이 3.2 면 두 눈 사이가 한 칸뿐이라 고글로 읽힌다
    x0, y0 = at(rig, u0 - ex * s, w0 - 0.6 * s, w, h)
    put(f, rows, x0, y0)
    flip = rows if size != "small" else [row[::-1] for row in rows]    # 반짝은 두 눈 모두 같은 쪽
    if level:   # 오른눈은 코 칸을 축으로 왼눈을 뒤집어 찍는다 — 따로 반올림하면 한쪽이 한 칸 붙는다
        put(f, flip, 2 * nx - (x0 + w - 1), y0)
    else:       # 기운 얼굴은 축이 없으니 제 자리에 따로
        put(f, flip, *at(rig, u0 + ex * s, w0 - 0.6 * s, w, h))
    if mood == "hiss":
        put(f, ["WMW", ".M."] if size == "big" else ["WW"], nx - (1 if size == "big" else 0), ny,
            {"W": FANG, "M": MAW})
        f[nx, ny - 1] = PINK
    else:
        f[nx, ny] = PINK
        if size == "big":
            f[nx - 1, ny + 1] = LID
            f[nx + 1, ny + 1] = LID
    if size != "small" and level:
        bx, by = rig.cell(u0 - 4.6 * s, w0 + 1.9 * s)
        for x in ([bx, bx + 1] if size == "big" else [bx]):
            f[x, by] = BLUSH
            f[2 * nx - x, by] = BLUSH
    elif size != "small":
        for sg in (-1, 1):
            f[rig.cell(u0 + sg * 4.6 * s, w0 + 1.9 * s)] = BLUSH
    if whiskers and size != "small" and level:
        L = 3 if size == "big" else 2
        sx, sy = rig.cell(u0 - 7.2 * s, w0 + 1.5 * s)
        for dv in (0, 1):
            for i in range(L):
                y = sy + dv + ((-1 if dv == 0 else 1) if i == L - 1 else 0)
                f.setdefault((sx - i, y), WHISK)
                f.setdefault((2 * nx - sx + i, y), WHISK)
    elif whiskers and size != "small":      # 기운 얼굴: 수염을 얼굴 가로축을 따라
        for sg in (-1, 1):
            for dv, slope in ((0.0, -0.5), (1.3, 0.5)):
                for i in range(3):
                    f.setdefault(rig.cell(u0 + sg * (7.0 + 1.1 * i) * s, w0 + (1.4 + dv + slope * i) * s), WHISK)


# ── 앞모습 까망이: a 가로(+오른쪽), b 세로(+아래), 원점은 몸 가운데 위 ─────────────────
HC = (0.0, -5.5)


def head_parts(hc=HC, s: float = 1.0, ears: str = "up") -> list:
    """앞모습 머리: 볼이 퍼진 둥근 머리 + 큰 세모 귀(속은 분홍). ears 가 flat 이면 옆으로 납작 — 하악할 때"""
    u0, w0 = hc

    def P(du, dw, sg=1):
        return (u0 + sg * du * s, w0 + dw * s)
    if ears == "flat":
        ear, inn = [(-5.4, -2.0), (-1.8, -4.4), (-9.6, -6.2)], [(-5.0, -3.2), (-3.2, -4.2), (-7.6, -5.6)]
    else:
        ear, inn = [(-6.6, -1.2), (-1.6, -4.6), (-6.2, -9.2)], [(-5.6, -2.8), (-3.0, -4.4), (-5.6, -7.4)]
    ears_ = any_of(*(poly([P(a, b, sg) for a, b in ear]) for sg in (1, -1)))
    inner = any_of(*(poly([P(a, b, sg) for a, b in inn]) for sg in (1, -1)))
    # 위는 둥근 이마, 아래는 옆으로 퍼진 볼 — 동그라미 하나면 부엉이 · 공으로 읽힌다
    head = any_of(ell(u0, w0 - 0.4 * s, 6.3 * s, 5.0 * s), ell(u0, w0 + 1.3 * s, 7.0 * s, 3.5 * s))
    return [("head", head, FUR, True), ("earin", inner, PINK, False), ("ears", ears_, FUR, False)]


def kit(rig: Rig, mood="open", look=0, ears="up", hc=HC, s=1.0, body=(0.0, 3.0, 4.6, 4.4), sit=True,
        arms=(), legs=(), tail=(), extra=(), mid=(), beans=(), whiskers=True, back=()) -> dict:
    """앞모습 까망이 한 장. sit 이면 앉은 앞발 둘과 엉덩이. arms 는 든 팔 [(어깨, 팔꿈치 또는 None, 발끝)],
    legs 는 뻗은 뒷다리 [(엉덩이, 발끝)], tail 은 꼬리 꺾은선, extra 는 맨 앞 부위, mid 는 든 팔 앞 · 머리 뒤,
    back 은 몸 뒤. beans 는 젤리를 보일 발끝들"""
    pads = [ell(p[0], p[1], 1.9, 1.8) for _, _, p in arms]
    limbs = []
    for sh, el, p in arms:
        limbs += [bar(sh, el, 1.5), bar(el, p, 1.4)] if el else [bar(sh, p, 1.5, 1.4)]
    parts = list(extra)
    if pads:
        parts.append(("pad", any_of(*pads), FUR, True))
    parts += list(mid) + head_parts(hc, s, ears)
    if limbs:
        parts.append(("arm", any_of(*limbs), FUR, True))
    if sit:
        parts.append(("paw", any_of(ell(-1.9, 7.2, 1.6, 1.3), ell(1.9, 7.2, 1.6, 1.3)), FUR, True))
    if legs:
        parts += [("foot", any_of(*(ell(p[0], p[1], 1.6, 1.4) for _, p in legs)), FUR, True),
                  ("leg", any_of(*(bar(h, p, 1.7, 1.4) for h, p in legs)), FUR, False)]
    bx, by, rx, ry = body
    parts.append(("body", ell(bx, by, rx, ry), FUR, False))
    if sit:
        parts.append(("haunch", any_of(ell(-3.7, 5.4, 2.4, 2.4), ell(3.7, 5.4, 2.4, 2.4)), FUR, False))
    if tail:
        parts.append(("tail", path(tail, 1.3, 1.0), FUR, False))
    parts += list(back)
    out, _, _ = draw(rig, parts)
    out = sheen(out)
    face(out, rig, hc, s, mood, look, whiskers)
    for p in beans:
        toes(out, rig, p)
    return out


def toes(f: dict, rig: Rig, p) -> None:
    """발바닥 젤리: 큰 젤리 하나 + 발가락 젤리 셋"""
    x, y = rig.cell(*p)
    put(f, ["B.B", ".B.", "BBB"] if rig.k >= 0.7 else ["B.B", ".B."], x - 1, y - 1, {"B": PINK})


# ── 털실 공 ───────────────────────────────────────────────────────────────────
def yarn(f: dict, cx: float, cy: float, r: float, rot: float = 0.0, tail=None) -> None:
    """털실 공: 감긴 실 줄무늬가 rot 만큼 굴러가 있다. tail 은 풀린 실 끝 꺾은선(공 앞에 깔린다)"""
    cells = disc(cx, cy, r)
    c, s = math.cos(rot), math.sin(rot)

    def col(p):
        u, v = p[0] + 0.5 - cx, p[1] + 0.5 - cy
        u, v = u * c + v * s, -u * s + v * c
        band = (u + 0.28 * v * v / max(r, 1)) * 1.25
        if math.hypot(p[0] + 0.5 - cx + r * 0.38, p[1] + 0.5 - cy + r * 0.42) < r * 0.3:
            return YARN_L
        return YARN_D if band % 2 < 0.62 else YARN
    solid(f, cells, col, YARN_O)
    if tail:
        for a, b in zip(tail, tail[1:]):
            n = max(1, math.ceil(math.hypot(b[0] - a[0], b[1] - a[1]) * 2))
            for i in range(n + 1):
                f.setdefault((math.floor(a[0] + (b[0] - a[0]) * i / n), math.floor(a[1] + (b[1] - a[1]) * i / n)),
                             YARN)


def thread(f: dict, pts, col=YARN, w: int = 1, force=False, twist=False) -> None:
    """털실 한 가닥 꺾은선 (w=2 면 오른쪽에 짙은 줄을 하나 더). twist 면 세 칸마다 밝은 칸 — 꼰 실 결.
    밋밋한 두 칸 굵기 분홍 직선은 광선검 · 막대로 읽혔다"""
    seen = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, math.ceil(math.hypot(b[0] - a[0], b[1] - a[1]) * 2))
        for i in range(n + 1):
            p = (math.floor(a[0] + (b[0] - a[0]) * i / n), math.floor(a[1] + (b[1] - a[1]) * i / n))
            if seen and seen[-1] == p:
                continue
            seen.append(p)
            c = YARN_L if twist and len(seen) % 3 == 0 else col
            if force:
                f[p] = c
            else:
                f.setdefault(p, c)
            if w == 2:
                f.setdefault((p[0] + 1, p[1]), YARN_D)


def blink(k: int, at_: int = 9) -> str:
    return "blink" if k == at_ else "open"


# ── 장면 ─────────────────────────────────────────────────────────────────────
_ARROW = {}
ARROW_PAW = (-8.8, -8.0)     # 실을 쥔 앞발(제 좌표) — 머리 왼쪽 볼 옆


def arrow_frames(small: bool = False) -> tuple[list[dict], tuple]:
    """털실 끝 화살표 12장(테 두르기 전)과 핫스팟 (1, 1). 오른쪽 아래에 앉은 까망이가 발치 털실 공에서 뽑은 실을
    한 앞발로 쥐어 왼쪽 위로 팽팽히 당기고, 그 실 끝이 핫스팟이다. 실은 끝을 둔 채 가운데만 출렁인다.
    small 은 도움말 · 작업 중 · 사용자 · 핀 칸의 작은 동반(같은 그림을 끝 기준으로 줄인 것)"""
    if small not in _ARROW:
        sc, k0 = (0.56, 0.5) if small else (1.0, 0.82)
        rig = Rig(1 + 19.0 * sc, 1 + 17.4 * sc, 0.0, k0)
        frames = []
        for k, ph in enumerate(phases()):
            tug = 0.5 + 0.5 * math.sin(ph)
            paw = (ARROW_PAW[0] - 0.5 * tug, ARROW_PAW[1] - 0.5 * tug)
            px, py = rig.world(*paw)
            line, n = [], 24
            for i in range(n + 1):
                t = i / n
                # 실 가운데가 아래로 처지고(왼쪽 아래로 휜 활꼴) 당길 때마다 출렁인다 — 끝은 그대로
                w = sc * math.sin(math.pi * t) * (1.6 - 0.9 * tug + 0.5 * math.sin(2 * ph))
                line.append((1.5 + (px - 1.5) * t - w * 0.7, 1.5 + (py - 1.5) * t + w * 0.7))
            front, strand = {}, {}
            bx, by = rig.world(-5.8, 8.6)
            yarn(front, bx, by, 2.9 * sc, -0.4 * ph)
            thread(strand, line, YARN, w=1 if small else 2, twist=not small)
            thread(strand, [(bx - 0.4 * sc, by - 2.4 * sc), (bx - 2.2 * sc, by - 6.0 * sc), (px - 0.6, py + 1.2)], YARN)
            strand[1, 1] = YARN
            sw = math.sin(ph + 1)
            o = kit(rig, blink(k, 8), look=-1, arms=[((-2.6, 0.4), None, paw)], beans=[] if small else [paw],
                    tail=[(3.8, 6.4), (7.2, 7.0), (9.6, 4.4), (9.2 + 1.2 * sw, 0.6)])
            frames.append(clip(stack(front, o, strand)))
        _ARROW[small] = frames, (1, 1)
    return _ARROW[small]


def arrow_cat(ph: float, k: int, small: bool = False) -> dict:
    return dict(arrow_frames(small)[0][k])


def arrow() -> list[dict]:
    """털실 끝 화살표 — 실 끝이 핫스팟, 앞발이 실을 당겼다 놓고 실이 출렁, 꼬리가 살랑"""
    return [finish(f) for f in arrow_frames()[0]]


def wait() -> list[dict]:
    """앉아서 털실 공을 두 앞발 사이로 이리저리 굴린다 — 공이 구른 만큼 줄무늬가 돌고, 눈이 공을 따라간다"""
    frames = []
    rig = Rig(15.5, 15.6, 0.0, 0.92)
    for k, ph in enumerate(phases()):
        d = 4.2 * math.sin(ph)                       # 공 가로 위치 (몸 가운데에서)
        bx, by = 15.5 + d, 26.4
        f = {}
        yarn(f, bx, by, 3.3, -d / 3.3, [(bx + 3.0, by + 2.4), (bx + 6.0, by + 3.4), (bx + 8.5, by + 3.0)])
        # 공 쪽 앞발이 공 위에 얹힌다
        sg = 1 if d > 0 else -1
        lift = abs(math.sin(ph))
        arms = [((sg * 2.4, 2.4), None, ((d * 0.92 + sg * 0.6) / 0.92, 8.6 - 1.4 * lift))]
        tail = [(3.8, 6.4), (7.2, 7.0), (9.6, 4.4), (9.2 + 1.2 * math.sin(ph + 1), 0.6)]
        o = kit(rig, blink(k, 6), look=1 if d > 1.5 else -1 if d < -1.5 else 0, arms=arms, tail=tail)
        frames.append(finish(clip(stack(o, f))))
    return frames


def busy() -> list[dict]:
    """작은 화살표 까망이 + 오른쪽 아래 털실 공 둘레를 발자국 여덟이 차례로 돈다"""
    frames = []
    cx, cy = 22.5, 22.5
    for k, ph in enumerate(phases()):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = math.floor(cx + 6.6 * math.cos(a) - 0.5), math.floor(cy + 6.6 * math.sin(a) - 0.5)
            lag = (head - i) % 8
            col = PAD[0] if lag < 1 else PAD[1] if lag < 2 else PAD[2]
            for q in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
                f[q] = col
        yarn(f, cx, cy, 3.4, -2 * math.pi * k / N)
        frames.append(finish(stack(arrow_cat(ph, k, True), f)))
    return frames


def help_() -> list[dict]:
    """작은 화살표 까망이 + 털실 한 가닥 물음표 — 점 자리 작은 털실 공이 통통 튄다"""
    frames = []
    hook = [(18.0, 13.2), (19.2, 11.0), (22.0, 10.0), (25.0, 10.8), (26.2, 13.2), (25.4, 15.6), (22.6, 17.4),
            (22.0, 19.4), (22.0, 21.4)]
    for k, ph in enumerate(phases()):
        f = {}
        m = set()
        for a, b in zip(hook, hook[1:]):
            for i in range(9):
                m |= disc(a[0] + (b[0] - a[0]) * i / 8, a[1] + (b[1] - a[1]) * i / 8, 1.05)
        solid(f, m, YARN, YARN_O)
        hop = abs(math.sin(ph)) * 2.4
        yarn(f, 22.3, 26.0 - hop, 2.2, ph)
        frames.append(finish(stack(arrow_cat(ph, k, True), f)))
    return frames


def person() -> list[dict]:
    """작은 화살표 까망이 + 까만 고양이 귀 후드를 쓴 사람이 손을 흔든다"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(22.5, 24.2, 0.0, 0.66)
        hand = (8.4, -6.0 - 2.0 * abs(math.sin(ph)))
        parts = [("hand", ell(*hand, 1.7, 1.7), SKIN, True), ("sleeve", bar((5.0, -0.5), hand, 1.6), SHIRT, False),
                 ("face", ell(0, -7.2, 5.4, 4.6), SKIN, False)] + \
            [(n, h, c, l) for n, h, c, l in head_parts((0.0, -8.0), 1.05) if n != "head"] + \
            [("hood", ell(0, -8.0, 7.6, 7.0), FUR, False),
             ("torso", ell(0, 3.0, 7.6, 6.4), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
        out, _, _ = draw(rig, parts)
        # 얼굴 테를 두르면 살색이 T 자만 남아 글자로 읽혀서, 테 없이 눈 · 볼 · 입만 점으로
        for sg in (-1, 1):
            ex, ey = rig.cell(sg * 2.3, -8.2)
            out[ex, ey] = PUPIL
            out[ex, ey + 1] = PUPIL if k != 6 else SKIN
            out[rig.cell(sg * 3.8, -5.8)] = BLUSH
        out[rig.cell(0, -5.2)] = PINK_D
        f = {p: c for p, c in out.items() if p[1] <= 30}
        frames.append(finish(stack(arrow_cat(ph, k, True), f)))
    return frames


def paw_print(f: dict, cx: int, cy: int, col) -> None:
    put(f, [".B.B.", "B...B", "..B..", ".BBB.", ".BBB."], cx - 2, cy - 2, {"B": col})


def pin() -> list[dict]:
    """작은 화살표 까망이 + 빨간 지도 핀 — 동그라미 속 분홍 발자국. 핀이 통통 튄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 13.0 + dy
        for x in range(19, 27):
            f.setdefault((x, 28), hx("00000040") if dy else hx("00000068"))
        tri = [(cx - 4.6, cy + 3.4), (cx + 4.6, cy + 3.4), (cx, cy + 12.6)]
        cells = disc(cx, cy, 6.4) | {(x, y) for y in range(int(cy), int(cy) + 14) for x in range(14, 32)
                                     if inside(tri, x + 0.5, y + 0.5)}
        solid(f, cells, SIGN, SIGN_D)
        solid(f, disc(cx, cy, 4.2), hx("fff4f6ff"), SIGN_D)
        paw_print(f, 22, math.floor(cy), PINK_D)
        frames.append(finish(stack(arrow_cat(ph, k, True), f)))
    return frames


def cross() -> list[dict]:
    """앞모습 얼굴 — 수염이 가로 조준선, 위아래 털실이 세로선. 사냥 눈. 분홍 코가 핫스팟"""
    frames = []
    rig = Rig(15.5, 19.9, 0.0, 1.0)      # 코 칸이 (15, 15)
    for k, ph in enumerate(phases()):
        f = {}
        tw = round(0.6 * math.sin(2 * ph))
        for x in list(range(1, 8)) + list(range(24, 31)):
            f[x, 15] = LID
        for sg in (-1, 1):
            f[15 + sg * 10, 14 - tw] = LID
            f[15 + sg * 10, 16 + tw] = LID
        sway = round(0.8 * math.sin(ph))
        thread(f, [(15.5, 1.0), (15.5, 4.6)], YARN, force=True)
        thread(f, [(15.5, 25.6), (15.5 + sway, 30.6)], YARN, force=True)
        out, _, _ = draw(rig, head_parts((0.0, -5.5)))
        out = sheen(out)
        mood = "hunt" if k % 6 < 3 else "open"
        face(out, rig, (0.0, -5.5), 1.0, mood, whiskers=False)
        frames.append(finish(stack(out, f)))
    return frames


HAND = Rig(17.4, 20.0, 0.0, 0.86)
HAND_PAW = (-7.6, -15.4)


def hand() -> list[dict]:
    """종이 상자에 들어앉아 앞발 하나를 쑥 내밀어 톡 — 젤리 보이는 발끝이 핫스팟. 톡 할 때 반짝"""
    frames = []
    for k, ph in enumerate(phases()):
        tap = k in (2, 3, 8, 9)
        box = {}
        bx0, bx1, by0, by1 = 6, 28, 23, 30
        for y in range(by0, by1 + 1):
            for x in range(bx0, bx1 + 1):
                edge = x in (bx0, bx1) or y in (by0, by1)
                box[x, y] = OUT if edge else BOX_L if y == by0 + 1 else BOX_D if x in (17, 18) and y < by0 + 3 else BOX
        o = kit(HAND, blink(k, 6) if not tap else "happy", look=-1, sit=False, body=(0.0, 3.0, 4.6, 4.4),
                arms=[((-2.6, 0.6), (-6.6, -6.0), HAND_PAW)], beans=[HAND_PAW], whiskers=True)
        o = {p: c for p, c in o.items() if p[1] < by0}
        f = stack(box, o)
        if tap:
            px, py = HAND.cell(*HAND_PAW)
            for dx, dy in ((-3, -2), (3, -2), (-4, 1)):
                f.setdefault((px + dx, py + dy), YARN_L)
        frames.append(finish(clip(f)))
    return frames


def ibeam() -> list[dict]:
    """매듭으로 묶어 늘어뜨린 털실 한 가닥이 I — 옆에 매달린 까망이가 실을 톡톡. 실 가운데가 핫스팟"""
    frames = []
    X = 9
    for k, ph in enumerate(phases()):
        f = {}
        bend = 0.9 * math.sin(ph)
        for y in range(1, 31):
            t = (y - 1) / 29
            x = X + round(bend * math.sin(2 * math.pi * t))     # S 자로 흔들려 가운데(핫스팟 줄)는 제자리
            f[x, y] = YARN
            f[x + 1, y] = YARN_D
        for x in range(X - 3, X + 5):    # 위아래 매듭(가로획)
            f[x, 1] = YARN_O if x in (X - 3, X + 4) else YARN
            f[x, 30] = YARN_O if x in (X - 3, X + 4) else YARN
        tapk = math.sin(2 * ph)
        rig = Rig(18.0, 18.4, 0.0, 0.62)
        paw = (-10.6 + 0.9 * tapk, -2.4)       # 실에 닿았다 떨어졌다
        o = kit(rig, blink(k, 8), look=-1, arms=[((-2.6, 0.6), None, paw)],
                tail=[(3.8, 6.4), (7.2, 7.0), (9.6, 4.4), (9.2 + 1.2 * math.sin(ph), 0.4)])
        frames.append(finish(clip(stack(o, f))))
    return frames


def move() -> list[dict]:
    """털실 공을 쫓아 제자리에서 폴짝폴짝 — 네 방향 분홍 화살촉이 바깥으로 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o_ = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o_), 15 + dy * (13 + o_), dx, dy, YARN)
        hop = abs(math.sin(ph))
        rig = Rig(15.5, 16.6 - 2.4 * hop, 0.0, 0.6)
        o = kit(rig, "happy" if hop > 0.8 else "open",
                tail=[(3.8, 6.4), (7.2, 7.0), (9.6, 4.4), (9.2 + 1.2 * math.sin(ph), 0.6)])
        frames.append(finish(stack(o, f)))
    return frames


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col) -> None:
    """(dx, dy) 쪽을 가리키는 화살촉. 꼭짓점이 (cx, cy). 대각선은 ㄱ 자 두 팔(가로 · 세로)로 —
    가로 · 세로 식을 그대로 쓰면 한 칸씩 건너뛴 점선이 된다"""
    if dx and dy:
        for i in range(5):
            for w in (0, 1):
                f[cx - dx * i, cy - dy * w] = col
                f[cx - dx * w, cy - dy * i] = col
        return
    px, py = -dy, dx
    for i in range(4):
        for s in (-1, 1):
            for w in (0, 1):
                f[cx - dx * (i + w) + s * px * i, cy - dy * (i + w) + s * py * i] = col


def tug(dx: int, dy: int) -> list[dict]:
    """털실 한 가닥을 (dx, dy) 축으로 팽팽히 당기는 까망이 — 앞발이 그 축을 따라 쭉 뻗었다 오므렸다 하고,
    실은 앞발에서 양 끝 화살촉까지 이어진다. 몸을 축대로 돌리면 얼굴이 기울어 눈 · 코가 글자처럼 읽혀서
    몸은 늘 바로 서고 팔만 축을 탄다. ns 는 위 실에 두 앞발로 매달려 뒷발 · 꼬리가 아래로 늘어진다"""
    frames = []
    diag = dx != 0 and dy != 0
    R = 10 if diag else 13
    for k, ph in enumerate(phases()):
        e = 0.5 + 0.5 * math.sin(ph)                 # 얼마나 뻗었나
        f = {}
        o_ = 1 if e > 0.6 else 0
        for sg in (-1, 1):
            chevron(f, 15 + sg * dx * (R + o_), 15 + sg * dy * (R + o_), sg * dx, sg * dy, YARN if o_ else YARN_D)
        sw = math.sin(ph + 1)
        if dx == 0:      # ns: 위 실에 한 앞발로 매달려 대롱대롱 — 실이 앞발 위 한 줄(x 15), 몸은 그 오른쪽에 늘어진다.
            # 두 앞발을 머리 위로 모았더니 귀와 한 덩이가 되어 모자로 읽혔다
            rig = Rig(20.8, 20.0, 0.0, 0.7)
            paws = [(-7.6, -16.0 - 1.2 * e)]
            arms = [((-2.6, 0.2), (-7.4, -6.0), paws[0]), ((2.6, 0.4), None, (4.0, 5.4))]
            legs = [((-2.0, 6.2), (-2.4, 10.4 + 1.6 * e)), ((2.0, 6.2), (2.6, 10.0 + 1.6 * e))]
            tail = [(0.8, 7.4), (0.0, 10.6), (-2.6 + 0.6 * sw, 12.0 + 0.8 * e)]
        else:
            rig = Rig(15.5, 15.2, 0.0, 0.64)
            if diag:    # 위로 뻗은 발은 볼 옆 높이에서, 아래로 뻗은 발은 허리 옆에서 축을 따라
                ex = (10.4 + 1.6 * e) * 0.7071
                paws = [(-ex - 0.6, -ex - 4.4), (ex + 0.6, ex + 0.6)] if dx * dy > 0 else \
                    [(-ex - 0.6, ex + 0.6), (ex + 0.6, -ex - 4.4)]
            else:
                paws = [(-10.0 - 1.8 * e, -1.0), (10.0 + 1.8 * e, -1.0)]
            arms = [((-2.6, 0.4), None, paws[0]), ((2.6, 0.4), None, paws[1])]
            legs = [((-2.0, 6.0), (-2.6, 10.6)), ((2.0, 6.0), (2.6, 10.6))]
            tail = [(3.0, 7.0), (6.4, 8.4), (8.6, 6.0), (8.8 + 1.0 * sw, 2.4)]
        o = kit(rig, "happy" if e > 0.75 else blink(k, 3), look=-1 if dx == 0 else 0, sit=False,
                body=(0.0, 3.2, 4.4, 5.0), arms=arms, legs=legs, tail=tail, beans=paws if rig.k >= 0.7 else [])
        line = {}
        for sg in (-1, 1):
            tip = (15 + sg * dx * (R + o_) + 0.5 - sg * dx * 1.5, 15 + sg * dy * (R + o_) + 0.5 - sg * dy * 1.5)
            # 이 끝 쪽 앞발: 축 방향으로 더 나간 발
            if dx == 0:      # ns 는 앞발에서 위로만 — 아래쪽은 실 대신 꼬리 · 뒷발이 늘어진다
                if sg > 0:
                    continue
                p = paws[0]
            else:
                p = max(paws, key=lambda q: sg * (dx * q[0] + dy * q[1]))
            px, py = rig.world(*p)
            thread(line, [(px, py), tip], YARN, w=1, twist=True)
        frames.append(finish(clip(stack(o, line, f))))
    return frames


def we():
    return tug(1, 0)


def ns():
    return tug(0, 1)


def nwse():
    return tug(1, 1)


def nesw():
    return tug(1, -1)


def no() -> list[dict]:
    """빨간 금지 표지 안에서 등을 아치로 세우고 털 · 꼬리를 빵빵하게 부풀려 하악 — 귀는 납작"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        R = 13.5
        ring = {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
        slash = set()
        for t in range(-90, 91):
            x, y = 15.5 + t / 100 * (R - 1.5) * 0.7071, 15.5 + t / 100 * (R - 1.5) * 0.7071
            slash |= disc(x, y, 1.3)
        solid(f, ring | slash, SIGN, SIGN_D)
        puff = 0.5 + 0.5 * math.sin(ph)
        rig = Rig(15.5, 17.0, 0.0, 0.78)
        fl = 0.5 + 0.7 * puff
        back = [(-5.0, 1.0), (-3.0, -3.4), (0.0, -5.0), (3.0, -3.4), (5.0, 1.0)]
        sw = math.sin(ph + 0.6)
        tail = [(6.0, 0.0), (9.0, -2.0), (10.0 + 0.6 * sw, -7.0), (9.0 + 1.0 * sw, -11.0)]
        parts = head_parts((-6.4, -4.2), 0.72, "flat") + [
            ("legs", any_of(bar((-4.0, 1.0), (-4.8, 8.6), 1.3), bar((4.4, 1.0), (5.2, 8.6), 1.3)), FUR, True),
            ("back", path(back, 2.8, 2.8, fl, 5), FUR, False),
            ("tail", path(tail, 1.8, 1.6, fl * 1.1, 4), FUR, False),
            ("far", any_of(bar((-2.6, 1.0), (-2.6, 8.6), 1.2), bar((3.0, 1.0), (3.6, 8.6), 1.2)), FUR_D, False)]
        out, _, _ = draw(rig, parts)
        out = sheen(out)
        face(out, rig, (-6.4, -4.2), 0.72, "hiss" if k % 6 < 4 else "wide", whiskers=True)
        frames.append(finish(clip(stack(out, f))))
    return frames


TIP = (3.5, 28.5)    # 뜨개바늘 끝(화면)
BACK = (14.5, 14.0)  # 분홍 구슬 꼭지 — 얼굴 앞을 가리지 않게 볼 왼쪽에서 끝난다


def pen() -> list[dict]:
    """뜨개바늘을 펜처럼 쥐고 실로 글씨를 쓴다 — 바늘 끝이 핫스팟, 바늘 끝에서 풀린 실이 물결 글씨로 남는다.
    바늘을 세 칸 굵기로 그렸더니 칼 · 방망이로 읽혀서, 한 칸 심 + 한 칸 그늘의 가는 막대에 분홍 구슬 꼭지,
    바늘에 걸린 뜨개코 몇 땀으로 뜨개바늘임을 알린다"""
    frames = []
    L = math.hypot(BACK[0] - TIP[0], BACK[1] - TIP[1])
    ux, uy = (BACK[0] - TIP[0]) / L, (BACK[1] - TIP[1]) / L
    rig = Rig(21.0, 18.2, 0.0, 0.66)
    for k, ph in enumerate(phases()):
        wob = 0.4 * math.sin(2 * ph)                 # 쓰는 손이 까딱 — 끝은 그대로
        f = {}
        n = 4 + k                                   # 써 나간 물결 길이
        pts = [(TIP[0] + 0.5 + 1.0 * i, TIP[1] + 0.2 - 1.3 * abs(math.sin(i * 0.9))) for i in range(n + 1)]
        thread(f, pts, YARN, twist=True)
        needle = {}
        for i in range(int(L * 2) + 1):
            t = i / 2
            x, y = TIP[0] + 0.5 + ux * t + wob * t / L, TIP[1] + 0.5 + uy * t
            p = (math.floor(x), math.floor(y))
            needle.setdefault(p, NEEDLE)
            if t > 1.5:
                needle.setdefault((p[0] + 1, p[1]), NEEDLE_D)
        bx, by = BACK[0] + 0.5 + wob, BACK[1] + 0.5
        solid(needle, disc(bx, by, 1.6), KNOB, YARN_O)
        loops = {}
        for t in (0.38, 0.5, 0.62):                # 바늘에 걸린 뜨개코
            cx, cy = TIP[0] + 0.5 + ux * L * t + wob * t, TIP[1] + 0.5 + uy * L * t
            for d in ((-1, 0), (0, -1), (1, 1)):
                loops[math.floor(cx) + d[0], math.floor(cy) + d[1]] = YARN
        grip = rig.local(TIP[0] + ux * L * 0.78 + wob, TIP[1] + uy * L * 0.78)
        grip2 = rig.local(TIP[0] + ux * L * 0.9 + wob, TIP[1] + uy * L * 0.9)
        o = kit(rig, blink(k, 4), look=-1, arms=[((-2.4, 0.6), None, grip), ((2.4, 0.6), None, grip2)],
                tail=[(3.8, 6.4), (7.2, 7.0), (9.6, 4.4), (9.2 + 1.2 * math.sin(ph), 0.6)])
        # 앞발이 맨 앞, 바늘 · 뜨개코는 몸 앞, 쓴 실은 맨 뒤
        paws = {p: c for p, c in o.items() if _near_paw(rig, p, grip, grip2)}
        out = stack(paws, loops, needle, o, f)
        out[math.floor(TIP[0]), math.floor(TIP[1])] = NEEDLE_D
        frames.append(finish(clip(out)))
    return frames


def _near_paw(rig, p, g1, g2) -> bool:
    a, b = rig.local(p[0] + 0.5, p[1] + 0.5)
    return any(math.hypot(a - g[0], b - g[1]) < 2.2 for g in (g1, g2))


UP = Rig(14.4, 19.0, 0.0, 0.8)
UP_PAW = (-4.6, -15.6)


def up() -> list[dict]:
    """뒷발로 서서 한 앞발은 위로 쭉, 다른 앞발로 냥냥펀치 — 위로 뻗은 발끝이 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        jab = max(0.0, math.sin(2 * ph))
        p2 = (5.4 + 2.6 * jab, -9.0 - 4.0 * jab)
        arms = [((-2.6, 0.4), (-6.0, -6.8), UP_PAW), ((2.6, 0.4), None, p2)]
        legs = [((-2.2, 6.0), (-2.8, 11.0)), ((2.2, 6.0), (2.8, 11.0))]
        o = kit(UP, "happy" if jab > 0.6 else blink(k, 7), sit=False, body=(0.0, 3.2, 4.4, 5.0), arms=arms,
                beans=[UP_PAW],
                legs=legs, tail=[(3.0, 7.0), (6.4, 8.4), (8.6, 6.0), (8.8 + 1.0 * math.sin(ph), 2.4)])
        f = dict(o)
        if jab > 0.6:
            px, py = UP.cell(*p2)
            for d in ((2, -2), (3, 0), (1, -3)):
                f.setdefault((px + d[0], py + d[1]), YARN_L)
        frames.append(finish(clip(f)))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def _top(fr):   # 맨 위 불투명 칸(같으면 왼쪽)
    return min((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1], p[0]))


def _tip(fr):
    return arrow_frames()[1]


def _tip_s(fr):
    return arrow_frames(True)[1]


HOT = {"arrow": _tip, "busy": _tip_s, "help": _tip_s, "person": _tip_s, "pin": _tip_s,
       "wait": (15, 15), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (9, 15),
       "pen": (math.floor(TIP[0]), math.floor(TIP[1])), "hand": _top, "up": _top}


def check(rid: str, frames: list[dict], hot: tuple) -> None:
    """핫스팟이 장마다 불투명한 칸 위에 있는지"""
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
        if rid in ("arrow", "busy", "help", "person", "pin") and \
                any(c[3] == 255 and (p[0] < hot[0] or p[1] < hot[1]) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 실 끝보다 왼쪽·위로 나온 칸이 있음")


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

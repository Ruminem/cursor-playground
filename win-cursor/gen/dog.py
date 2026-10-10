# SPDX-License-Identifier: Apache-2.0
"""댕댕이 · 애니 — 견종 10마리 × 16칸(arrow 는 dog_front.py). 손으로 돌린다.

  python gen/dog.py [견종...] [--cells 칸,칸]   art/<견종>anim/<칸>.txt 를 쓴다 (안 주면 10마리 · 16칸 전부)

치즈냥(gen/cheesecat.py)과 같은 틀 — 몸 부위(타원 · 막대 · 세모)를 개 제 좌표 (u 오른쪽, w 아래)에 놓고
화면으로 돌려 찍는다(`Rig`, `draw`). cheesecat 의 draw 가 제 전역 OUT 을 쓰므로 들여오지 않고 여기 옮겨 둔다.
견종마다 털빛 · 귀(쫑긋 · 늘어짐 · 곱슬 뭉치 · 긴 털) · 꼬리(말림 · 깃털 · 방울 …) · 얼굴 무늬를 데이터(`DOGS`)로 두고
앉은 몸은 같이 쓰되, wait · no 는 견종마다 제 짓을 따로 그린다(`WAIT`, `NO`).
  arrow  dog_front.py 가 그린다 — 앞모습으로 앉아 화살표 대 끝을 입꼬리에 물고 꼬리 붕붕
  wait   견종마다 기다리는 버릇 12장
  no     빨간 금지 표지 안에서 견종마다 제 방식으로 싫다고 함
나머지 14칸은 견종 데이터만 갈아 끼우고 장면은 같이 쓴다(`SCENE`, 핫스팟 `HOT`).
  busy · help · person · pin   작은 화살표 밑에 앉은 작은 댕댕이 도장(`mini_dog`) + 오른쪽 절반 소품 —
         발자국 원과 뼈다귀 · 물음표 리드줄과 테니스공 · 리드줄 쥐고 손 흔드는 사람 · 제 얼굴 든 지도 핀. 핫스팟 (1, 1)
  hand   손! — 앞발 젤리를 내밀어 꾹. 핫스팟은 젤리 맨 위 칸(누르면 옆 · 아래로만 퍼진다)
  cross  앞모습 얼굴, 코가 십자 가운데 — 수염이 가로선, 리드줄이 세로선
  ibeam  세운 뼈다귀가 I, 오른쪽에 앉아 어깨를 기대고 고개를 갸웃. 핫스팟은 뼈다귀 가운데
  move   공처럼 만 몸으로 제 꼬리를 쫓아 빙글빙글 + 네 방향 화살촉
  ns · we · nwse · nesw   그 축으로 쭉 기지개, 머리는 늘 똑바로 + 양 끝 화살촉
  pen    연필을 가로 물고 연필심(왼쪽 아래, 핫스팟)을 축으로 까딱
  up     뒷발로 서서 앞발 싹싹. 머리는 그 자리라 핫스팟(머리 꼭대기)이 장마다 같은 칸
치즈냥(cheesecat.py)에서 안 된 것 — 돌린 얼굴은 칸 위에서 뭉개지고, 머리 위로 든 팔은 귀 · 두건으로 읽혔다 — 을 따라
머리는 어느 칸에서도 안 돌리고 팔은 가슴 앞에 둔다.
"""
import math
import sys

import sea  # noqa: E402
import shape  # noqa: E402
from sea import N, PEEK_CUR, PEEK_WHITE, RATE, SIGN, SIGN_D, disc, finish, hx, ink, inside, phases, raster, solid  # noqa: E402

ART = sea.WIN / "art"

OUT, EYE, NOSE, HI = hx("3a2a30ff"), hx("2a1c22ff"), hx("1e1418ff"), hx("ffffffff")
TONGUE, TONGUE_D, MOUTH = hx("f27a8aff"), hx("d65a70ff"), hx("7a2c3aff")
CHEEK = hx("f4a0b0ff")
RIM_WARM, RIM_GREY = hx("f6e9d2c7"), hx("d9dde3c7")
BALL, BALL_D, BALL_W = hx("d4e04aff"), hx("a8b830ff"), hx("fffbe8ff")   # 테니스공 — 빨강은 벌린 입으로 읽혔다
LEASH, LEASH_D = hx("4a7fb5ff"), hx("2e5a88ff")
RIBBON, RIBBON_D = hx("ff7aa8ff"), hx("d24f80ff")
BLUE = hx("5aaee8ff")
MARK, MARK_L = hx("8a7f88ff"), hx("b8b0b8ff")       # 움직임 줄 · 소리 물결
BONE, BONE_D = hx("fbf1dcff"), hx("e2cfa6ff")
PAD, CLIP = hx("f07c92ff"), hx("c4ccd6ff")          # 발바닥 젤리 · 리드줄 고리
GLOW = (hx("f27a8aff"), hx("f4a0b0ff"), hx("f4a0b060"))   # 발자국 · 화살촉 · 그림자 (짙은 것부터)
SKIN, HAIR, SHIRT, SHIRT_D = hx("f7d7bcff"), hx("6b4630ff"), hx("5aa26aff"), hx("3f7d4dff")
PENCIL, PENCIL_D, WOOD, LEAD = hx("f5c842ff"), hx("c8961cff"), hx("efd2a8ff"), hx("3a3a3aff")
ERASER, FERRULE = hx("f2a0a8ff"), hx("b8b8c0ff")

# ── 견종 표 ──────────────────────────────────────────────────────────────────
# fur 털 · dark 짙은 털(귀 · 무늬 · 그늘) · light 밝은 털(주둥이 · 가슴 · 양말) · inner 귀 속
DOGS = [
    dict(id="shiba", name="시바", fur="e0893a", dark="b8692a", light="fff4e4", inner="fff0dc", ear="prick", ear_s=1.0,
         tail="curl", marks=("urajiro", "brow"), sock=True, rim=RIM_WARM, mouth="smile"),
    dict(id="corgi", name="웰시코기", fur="ea9a40", dark="c47628", light="fff6ea", inner="f6c8b8", ear="prick", ear_s=1.45,
         tail="stub", marks=("blaze",), sock=True, rim=RIM_WARM, mouth="tongue", short=True),
    dict(id="pomeranian", name="포메", fur="f4b462", dark="d99540", light="fff0d6", inner="fbd8b8", ear="small", ear_s=0.75,
         tail="pom", marks=(), coat="fluff", ruff=True, sock=False, rim=RIM_WARM, mouth="tongue", muzzle=1),
    dict(id="bichon", name="비숑", fur="fffdf8", dark="dedad2", light="fffdf8", inner="fffdf8", ear="none",
         tail="fluff", marks=(), coat="fluff", big=True, sock=False, rim=RIM_GREY, mouth="smile", muzzle=1),
    dict(id="retriever", name="골든리트리버", fur="e8b45a", dark="c68e36", light="f8dfa8", inner="c68e36", ear="drop",
         ear_len=1.0, tail="feather", marks=(), sock=False, rim=RIM_WARM, mouth="tongue"),
    dict(id="dachshund", name="닥스훈트", fur="b0602e", dark="7c3e1a", light="d99a62", inner="7c3e1a", ear="drop",
         ear_len=1.3, tail="thin", marks=(), sock=False, rim=RIM_WARM, mouth="smile", snout=1.25, short=True),
    dict(id="husky", name="허스키", fur="7e8896", dark="5a6270", light="f6f7fa", inner="e8c8cc", ear="prick", ear_s=1.05,
         tail="plume", marks=("mask",), sock=True, rim=RIM_GREY, mouth="smile", eye=BLUE),
    dict(id="poodle", name="푸들", fur="c98552", dark="9c5e32", light="e2a878", inner="9c5e32", ear="poof",
         tail="pompom", marks=(), coat="curly", topknot=True, sock=False, rim=RIM_WARM, mouth="smile"),
    dict(id="maltese", name="말티즈", fur="fffcf7", dark="e0dad2", light="fffcf7", inner="fffcf7", ear="hair",
         tail="fluff", marks=(), ribbon=True, sock=False, rim=RIM_GREY, mouth="smile", muzzle=1),
    dict(id="jindo", name="진돗개", fur="faf3e4", dark="ddd0b8", light="fffaf0", inner="ead8b8", ear="prick", ear_s=1.15,
         tail="curl", marks=(), sock=False, rim=RIM_GREY, mouth="smile", snout=1.2, gape=True),
]
D: dict = {}      # 지금 그리는 견종 (use 가 정한다)


def use(d: dict) -> None:
    D.clear()
    D.update(d)
    for key in ("fur", "dark", "light", "inner"):
        D[key.upper()] = hx(d[key] + "ff")
    D["EYE"] = d.get("eye", EYE)
    ink(OUT, HI, d["rim"])


# ── 그리개 (cheesecat.py 에서 옮김 — 각도를 들고 다니게만 고침) ──────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도) · 배율 k. ang=0 이면 u 가 오른쪽, w 가 아래. ang 만큼 시계 방향으로 돈다"""

    def __init__(self, ox: float, oy: float, ang: float = 0.0, k: float = 1.0):
        t = math.radians(ang)
        self.ox, self.oy, self.ang, self.c, self.s, self.k = ox, oy, ang, math.cos(t), math.sin(t), k

    def world(self, a: float, b: float) -> tuple:
        return self.ox + (a * self.c - b * self.s) * self.k, self.oy + (a * self.s + b * self.c) * self.k

    def local(self, x: float, y: float) -> tuple:
        dx, dy = (x - self.ox) / self.k, (y - self.oy) / self.k
        return dx * self.c + dy * self.s, -dx * self.s + dy * self.c

    def cell(self, a: float, b: float) -> tuple:
        x, y = self.world(a, b)
        return math.floor(x), math.floor(y)

    def turned(self, pivot, tilt: float) -> "Rig":
        """제 좌표 pivot 을 축으로 tilt 도 더 돈 그리개 — 갸웃한 머리"""
        wx, wy = self.world(*pivot)
        t = math.radians(self.ang + tilt)
        c, s = math.cos(t), math.sin(t)
        pa, pb = pivot
        return Rig(wx - (pa * c - pb * s) * self.k, wy - (pa * s + pb * c) * self.k, self.ang + tilt, self.k)


def ell(ca, cb, ra, rb, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)

    def hit(a, b):
        da, db = a - ca, b - cb
        u, v = da * c + db * s, -da * s + db * c
        return (u / ra) ** 2 + (v / rb) ** 2 <= 1
    return hit


def fluff(ca, cb, ra, rb, n=9, amp=0.1, ph=0.0):
    """가장자리가 물결진 타원 — 솜털"""
    def hit(a, b):
        da, db = (a - ca) / ra, (b - cb) / rb
        return math.hypot(da, db) <= 1 + amp * math.cos(n * math.atan2(db, da) + ph)
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


def draw(rig: Rig, parts: list) -> dict:
    """parts: [(이름, 맞음(a, b), 색(a, b) 또는 색, 테두리)] — 앞의 것이 위에 그려진다.
    칸을 4×4 로 찍어 반 넘게 덮이면 칠하고, 가장 많이 덮은 부위의 색을 준다. 바깥 테두리와,
    테두리=True 인 부위가 뒤 부위와 닿는 자리에 선을 긋는다"""
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
    return out


def dot(f: dict, x: int, y: int, c: tuple) -> None:
    f[x, y] = c


# ── 털 무늬 ──────────────────────────────────────────────────────────────────
def coat(base, a, b):
    """곱슬(푸들)은 짙은 동글 점, 솜털은 그대로"""
    if D.get("coat") == "curly" and math.sin(a * 2.1) + math.sin(b * 2.1 + a * 0.7) > 1.25:
        return D["DARK"]
    return base


# ── 머리 ─────────────────────────────────────────────────────────────────────
HC, HR = (0.0, -7.5), 7.0


def head_parts(hc=HC, r=HR, turn=0.0, ears=(0.0, 0.0), swing=0.0, name="head", squash=0.0, rear=False) -> list:
    """앞모습 머리 → 부위 목록(앞 귀 · 머리 · 리본 · 뒤 귀 · 갈기). ears = 좌우 귀를 뒤로 젖힌 정도(0 쫑긋 – 1 납작),
    swing 은 늘어진 귀가 흔들린 정도(u), squash 는 솜머리 통통(+ 납작 · − 길쭉)"""
    u0, w0 = hc
    F, Dk, L = D["FUR"], D["DARK"], D["LIGHT"]
    marks = D["marks"]
    sn = D.get("snout", 1.0)
    ra, rb = r * (1 + squash * 0.5), r * (1 - squash * 0.5)
    if D.get("big"):
        head = fluff(u0, w0 - 0.6, ra * 1.34, rb * 1.22, n=12, amp=0.09)
    elif D.get("coat") in ("fluff", "curly"):
        head = any_of(fluff(u0, w0 - 0.4, ra * 1.0, rb * 0.88, n=10, amp=0.06), ell(u0, w0 + 1.0, ra * 1.08, rb * 0.66))
    else:
        head = any_of(ell(u0, w0 - 0.4, ra * 0.98, rb * 0.86), ell(u0, w0 + 1.0, ra * 1.08, rb * 0.66))

    def skin(a, b):
        if rear:   # 뒤통수 — 무늬 없이 털빛만
            return coat(F, a, b)
        mu = a - u0 - turn
        muz = (mu / (r * 0.5)) ** 2 + ((b - (w0 + r * 0.44 * sn)) / (r * 0.34 * sn)) ** 2 <= 1
        if "mask" in marks:
            if muz or (abs(mu) < r * 0.12 and b > w0 - r * 0.72):
                return L
            if b < w0 - r * 0.16 or (abs(mu) > r * 0.74 and b < w0 + r * 0.28):
                return F
            return L
        if muz:
            return L
        if "urajiro" in marks and b > w0 + r * 0.14 and abs(mu) < r * 0.92:
            return L
        if "blaze" in marks and abs(mu) < r * 0.15 and b < w0 + r * 0.1:
            return L
        if D["fur"] == D["light"] and (b > w0 + r * 0.62 or abs(mu) > r * 1.0):   # 흰 개 — 아래 · 옆 그늘
            return Dk
        return coat(F, a, b)

    front, back = [], []
    kind = D["ear"]
    for i, sg in enumerate((-1, 1)):
        fl = ears[i]
        if kind in ("prick", "small"):
            s = D.get("ear_s", 1.0)
            wide = 1.0 if kind == "prick" else 0.7
            base0 = (u0 + sg * r * 0.98, w0 - r * 0.15)
            base1 = (u0 + sg * r * (0.98 - 0.8 * wide * min(s, 1.2)), w0 - r * 0.72)
            tip = (u0 + sg * r * (0.8 + 0.75 * fl) + turn * 0.3, w0 - r * (0.3 + 1.0 * s) * (1 - fl * 0.55) - r * 0.1)
            ear = tri(base0, tip, base1)
            cx, cy = (base0[0] + tip[0] + base1[0]) / 3, (base0[1] + tip[1] + base1[1]) / 3 + r * 0.06
            inner = tri(*[(cx + (p[0] - cx) * 0.5, cy + (p[1] - cy) * 0.5) for p in (base0, tip, base1)])
            back.append((f"{name}_ear{i}", ear, (lambda h: lambda a, b: D["INNER"] if h(a, b) else F)(inner), False))
        elif kind == "drop":
            ln = D.get("ear_len", 1.0)
            back_ear = ell(u0 + sg * r * 0.98 + swing, w0 + r * 0.1 * ln, r * 0.34, r * 0.62 * ln, sg * (0.3 - fl * 0.5))
            front.append((f"{name}_ear{i}", back_ear, Dk, True))
        elif kind == "poof":
            front.append((f"{name}_ear{i}", fluff(u0 + sg * r * 1.0 + swing, w0 + r * 0.35, r * 0.42, r * 0.62, n=7, amp=0.12),
                          lambda a, b: coat(D["FUR"], a, b), True))
        elif kind == "hair":
            front.append((f"{name}_ear{i}", fluff(u0 + sg * r * 1.06 + swing, w0 + r * 0.55, r * 0.3, r * 0.95, n=6, amp=0.08,
                                                  ph=1.0),
                          lambda a, b, sg=sg: Dk if (a - u0) * sg > r * 1.05 else F, True))
    parts = front + [(name, head, skin, True)]
    if D.get("ribbon"):
        bx, by = u0 + turn * 0.3 + swing * 0.5 + r * 0.3, w0 - r * 0.86
        wob = swing * 0.12
        wings = any_of(tri((bx, by), (bx - r * 0.8, by - r * (0.5 + wob)), (bx - r * 0.75, by + r * 0.42)),
                       tri((bx, by), (bx + r * 0.8, by - r * (0.5 - wob)), (bx + r * 0.75, by + r * 0.42)),
                       ell(bx, by, r * 0.22, r * 0.22))
        parts = [("ribbon", wings, lambda a, b: RIBBON_D if abs(a - bx) < r * 0.2 else RIBBON, True)] + parts
    if D.get("topknot"):
        back.append(("topknot", fluff(u0 + turn * 0.2, w0 - r * 0.88, r * 0.62, r * 0.42, n=7, amp=0.14),
                     lambda a, b: coat(D["FUR"], a, b), False))
    if D.get("ruff"):
        back.append(("ruff", fluff(u0, w0 + r * 0.3, r * 1.32, r * 1.08, n=13, amp=0.07), F, False))
    return parts + back


def eyes(f: dict, rig: Rig, hc=HC, r=HR, mood="open", turn=0.0, look=0) -> None:
    """2×2 눈(흰 반짝 1칸). mood: open · blink · sleep(︶) · happy(^) · squeeze(><) · sulk(흥) · angry(눈썹 ↘↙)
    · sad(눈썹 ↗↖, 촉촉). look 은 눈동자를 옆으로 민 칸 수"""
    u0, w0 = hc
    for sg in (-1, 1):
        ex, ey = rig.world(u0 + turn + sg * r * 0.44, w0 - r * 0.12)
        x0, y0 = round(ex - 1) + look, round(ey - 1)
        if mood in ("open", "angry", "sad"):
            for dx in (0, 1):
                for dy in (0, 1):
                    dot(f, x0 + dx, y0 + dy, EYE)
            if D["EYE"] != EYE:
                dot(f, x0 + 1, y0, D["EYE"])
                dot(f, x0, y0 + 1, D["EYE"])
            dot(f, x0 if look <= 0 else x0 + 1, y0, HI)
            if mood == "angry":
                dot(f, x0 - (1 if sg < 0 else -1) + (0 if sg < 0 else 1), y0 - 2, OUT)
                dot(f, x0 + (1 if sg < 0 else 0), y0 - 1, OUT)
            if mood == "sad":
                dot(f, x0 + (1 if sg < 0 else 0), y0 - 2, OUT)
                dot(f, x0 + (0 if sg < 0 else 1) - sg, y0 - 1, OUT)
                dot(f, x0 + (1 if sg < 0 else 0), y0 + 2, BLUE)
        elif mood == "blink":
            dot(f, x0, y0 + 1, EYE)
            dot(f, x0 + 1, y0 + 1, EYE)
        elif mood == "sleep":
            dot(f, x0, y0 + 1, EYE)
            dot(f, x0 + 1, y0 + 1, EYE)
            dot(f, x0 - 1 if sg < 0 else x0 + 2, y0, EYE)
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
        if "brow" in D["marks"] or "mask" in D["marks"]:   # 시바 · 허스키 눈썹 점
            if mood not in ("angry", "sad"):
                bx, by = rig.world(u0 + turn + sg * r * 0.36, w0 - r * 0.46)
                dot(f, math.floor(bx), math.floor(by), D["LIGHT"])
                dot(f, math.floor(bx) + 1, math.floor(by), D["LIGHT"])


def mouth(f: dict, rig: Rig, hc=HC, r=HR, kind="smile", turn=0.0, k=0) -> None:
    """까만 코 + 입. kind: smile(ω) · tongue(혀 빼꼼) · pant(헥헥 — k 로 혀가 들썩) · open(왈) · O(아우우) ·
    teeth(으르렁) · flat(일자) · none"""
    u0, w0 = hc
    sn = D.get("snout", 1.0)
    nx, ny = rig.world(u0 + turn, w0 + r * 0.36 * sn)   # 눈과 한 줄 띄운다 — 붙이면 선글라스로 읽혔다
    nl, ny = round(nx) - 1, math.floor(ny)
    for x in (nl, nl + 1):
        dot(f, x, ny, NOSE)
    for x in range(nl - 1, nl + 3):   # 위가 넓은 개 코 — 고양이와 가르는 첫 표시
        dot(f, x, ny - 1, NOSE)
    dot(f, nl, ny - 1, HI if r * rig.k >= 5.6 else NOSE)
    if kind in ("smile", "tongue", "pant"):
        for p in ((nl - 1, ny + 1), (nl, ny + 2), (nl + 1, ny + 2), (nl + 2, ny + 1)):
            dot(f, *p, OUT)
        if kind == "tongue":
            dot(f, nl, ny + 3, TONGUE)
            dot(f, nl + 1, ny + 3, TONGUE)
        if kind == "pant":
            dot(f, nl, ny + 3, TONGUE)
            dot(f, nl + 1, ny + 3, TONGUE)
            if k % 2 == 0:
                dot(f, nl, ny + 4, TONGUE)
                dot(f, nl + 1, ny + 4, TONGUE_D)
                dot(f, nl - 1, ny + 3, OUT)
                dot(f, nl + 2, ny + 3, OUT)
                dot(f, nl - 1, ny + 4, OUT)
                dot(f, nl + 2, ny + 4, OUT)
                dot(f, nl, ny + 5, OUT)
                dot(f, nl + 1, ny + 5, OUT)
    elif kind == "open":
        for x in range(nl - 1, nl + 3):
            dot(f, x, ny + 1, OUT)
            dot(f, x, ny + 2, MOUTH)
            dot(f, x, ny + 4, OUT)
        dot(f, nl - 1, ny + 2, OUT)
        dot(f, nl + 2, ny + 2, OUT)
        dot(f, nl - 1, ny + 3, OUT)
        dot(f, nl + 2, ny + 3, OUT)
        dot(f, nl, ny + 3, TONGUE)
        dot(f, nl + 1, ny + 3, TONGUE)
    elif kind == "O":
        for x in (nl, nl + 1):
            dot(f, x, ny + 1, OUT)
            dot(f, x, ny + 2, MOUTH)
            dot(f, x, ny + 3, MOUTH)
            dot(f, x, ny + 4, OUT)
        for y in (ny + 2, ny + 3):
            dot(f, nl - 1, y, OUT)
            dot(f, nl + 2, y, OUT)
    elif kind == "teeth":
        for x in range(nl - 2, nl + 4):
            dot(f, x, ny + 1, OUT)
            dot(f, x, ny + 3, OUT)
        for x in range(nl - 1, nl + 3):
            dot(f, x, ny + 2, HI)
        dot(f, nl - 2, ny + 2, OUT)
        dot(f, nl + 3, ny + 2, OUT)
    elif kind == "flat":
        dot(f, nl, ny + 1, OUT)
        dot(f, nl + 1, ny + 1, OUT)
        dot(f, nl - 1, ny + 2, OUT)
        dot(f, nl + 2, ny + 2, OUT)
    if kind not in ("none",):   # 볼터치
        for sg in (-1, 1):
            bx, by = rig.world(u0 + turn + sg * r * 0.74, w0 + r * 0.3)
            if (math.floor(bx), math.floor(by)) in f and f[math.floor(bx), math.floor(by)] != OUT:
                dot(f, math.floor(bx), math.floor(by), CHEEK)


# ── 몸 ──────────────────────────────────────────────────────────────────────
def tail_part(kind: str, k: int = 0, wag: float = 1.0, name="tail"):
    """앉은 개 오른쪽으로 보이는 꼬리. k 로 살랑"""
    F, Dk, L = D["FUR"], D["DARK"], D["LIGHT"]
    sw = wag * math.sin(2 * math.pi * k / N)
    if kind == "curl":   # 등 위로 말린 꼬리
        pts = [(5.0, 4.6), (8.6, 2.0 + sw * 0.3), (9.4 + sw * 0.4, -1.8), (7.0 + sw * 0.6, -3.0), (5.8 + sw * 0.5, -0.8)]
        return (name, chain(pts, 1.9, 1.4), lambda a, b: L if b > 1.2 else F, False)
    if kind == "plume":
        pts = [(5.0, 4.6), (9.2, 2.0 + sw * 0.3), (10.0 + sw * 0.4, -2.6), (7.4 + sw * 0.6, -4.0), (6.2 + sw * 0.5, -1.6)]
        return (name, chain(pts, 2.2, 1.6), lambda a, b: L if (a > 9.0 or b < -3.0) else F, False)
    if kind == "pom":
        return (name, fluff(7.4 + sw * 0.4, -0.6, 4.4, 3.6, n=9, amp=0.12, ph=k), F, False)
    if kind == "fluff":
        return (name, fluff(6.8 + sw * 0.4, 0.6, 3.4, 3.0, n=8, amp=0.12, ph=k), lambda a, b: D["DARK"] if b > 2.2 else F,
                False)
    if kind == "feather":
        pts = [(5.6, 8.2), (9.6, 7.6), (12.4, 5.4 + sw * 1.4)]
        return (name, chain(pts, 1.7, 1.2), lambda a, b: L if b > 7.0 or a > 11.6 else F, False)
    if kind == "thin":
        pts = [(5.6, 8.2), (9.8, 7.6), (12.6, 5.2 + sw * 1.4)]
        return (name, chain(pts, 1.2, 0.7), F, False)
    if kind == "pompom":
        end = (9.6 + sw * 0.6, -1.6)
        return (name, any_of(fluff(*end, 2.4, 2.2, n=7, amp=0.12), chain([(5.0, 5.0), (8.4, 2.4), end], 0.9)),
                lambda a, b: coat(D["FUR"], a, b), False)
    return None   # stub — 앞에서 안 보인다


def arm_part(pts, r=1.7, pr=1.9, name="arm", lined=None):
    """앞다리 하나 → [발, 다리]. 양말 견종은 발이 밝다. 흰 개만 다리에 테를 긋는다 — 털빛 개는 가슴 색이 다리를 가른다"""
    lined = False if lined is None else lined
    white = D["fur"] == D["light"]
    paw = (name + "_paw", ell(*pts[-1], pr, pr * 0.9), D["LIGHT"] if D.get("sock") else D["FUR"], True)
    # 흰 개도 다리에 테를 긋지 않는다 — 그으면 몸이 창살로, 그늘색으로 칠하면 회색 바지로 읽혔다. 발만 테로 가른다
    return [paw, (name, chain(pts, r, r * 0.92), lambda a, b: coat(D["FUR"], a, b), False if white else lined)]


def body_part(c=(0.0, 3.2), ra=6.6, rb=6.4, name="body"):
    c0, c1 = c
    F, L = D["FUR"], D["LIGHT"]
    hit = fluff(c0, c1, ra, rb, n=11, amp=0.06) if D.get("coat") in ("fluff", "curly") else ell(c0, c1, ra, rb)

    def col(a, b):
        if ((a - c0) / (ra * 0.48)) ** 2 + ((b - c1 + rb * 0.25) / (rb * 0.72)) ** 2 <= 1:
            return L
        if D["fur"] == D["light"] and abs(a - c0) > ra * 0.7:
            return D["DARK"]
        return coat(F, a, b)
    return (name, hit, col, False)


def sit(rig: Rig, k=0, *, hc=HC, r=HR, turn=0.0, tilt=0.0, mood="open", mo=None, tail=None, wag=1.0, paws=None,
        front=(), ears=(0.0, 0.0), swing=0.0, look=0, squash=0.0, body=None, behind=(), face=True) -> dict:
    """앉은 앞모습 댕댕이 한 장. 몸 · 머리(tilt 만큼 갸웃) · 앞(front) 세 겹으로 찍는다.
    paws 를 주면 앞다리 자리를 바꾼다, behind 는 몸 뒤 부위, front 는 얼굴 위에 덮는 부위"""
    short = D.get("short")
    leg = 7.4 if short else 8.4
    paws = paws if paws is not None else [[(-2.4, 1.0), (-2.6, leg)], [(2.4, 1.0), (2.6, leg)]]
    arms = []
    for i, pts in enumerate(paws):
        arms += arm_part(pts, name=f"arm{i}")
    fy = 8.4 if short else 8.9
    hind = ("feet", any_of(ell(-5.0, fy, 2.2, 1.3), ell(5.0, fy, 2.2, 1.3)), D["LIGHT"] if D.get("sock") else D["FUR"], True)
    haunch = ("haunch", any_of(ell(-4.8, 6.0, 2.8, 2.7), ell(4.8, 6.0, 2.8, 2.7)), lambda a, b: coat(D["FUR"], a, b), True)
    tp = tail_part(tail or D["tail"], k, wag)
    bp = body or body_part((0.0, 3.0 if short else 3.2), 6.6, 5.8 if short else 6.4)
    f = draw(rig, arms + [hind, haunch, bp] + ([tp] if tp else []) + list(behind))
    hrig = rig if not tilt else rig.turned((hc[0], hc[1] + r * 0.8), tilt)
    f.update(draw(hrig, head_parts(hc, r, turn, ears, swing, squash=squash)))
    if face:
        eyes(f, hrig, hc, r, mood, turn, look)
        mouth(f, hrig, hc, r, mo or D["mouth"], turn, k)
    if front:
        f.update(draw(rig, list(front)))
    return f


# ── 화살표 ─────────────────────────────────────────────────────────────────
STEM =(0.40, 0.92)            # 대 축 방향(PEEK_CUR 좌표) — 대를 늘일 때 끝 두 점을 이쪽으로 민다


def arrow_poly(s: float, ext: float = 0.0) -> list:
    """s 배 화살표. ext 만큼 대를 늘인다(물고 오기 — 짧은 대는 입에 안 닿는다)"""
    pts = [(x + STEM[0] * ext, y + STEM[1] * ext) if i in (3, 4) else (x, y) for i, (x, y) in enumerate(PEEK_CUR)]
    return [(1 + x * s, 1 + y * s) for x, y in pts]


def put_arrow(f: dict, s: float, fill=PEEK_WHITE, ext: float = 0.0) -> set:
    m = raster(arrow_poly(s, ext))
    solid(f, m, sea.Cur(fill), sea.Cur(OUT))   # 화살표는 커서 — 쓸 때 sea.mark 가 파랑 맨 끝 비트로 캐릭터와 가른다
    f[1, 1] = sea.Cur(OUT)
    return m


def clip(f: dict) -> dict:
    """판(1–30) 밖을 자른다 — 테 한 칸 자리를 남기고, 화살표 끝보다 왼쪽 · 위는 비운다"""
    return {p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}


def tail_side(kind: str, ang: float, root: tuple):
    """옆모습 꼬리 — 뿌리에서 ang(도, 0 이 위 · + 가 뒤쪽) 로 뻗는다. 점은 (앞쪽으로 휜 양, 길이) 로 적는다"""
    F, L = D["FUR"], D["LIGHT"]
    t = math.radians(ang)
    d, n = (math.sin(t), -math.cos(t)), (-math.cos(t), -math.sin(t))    # 뻗는 쪽 · 앞(머리)쪽

    def at(a, b):
        return root[0] + d[0] * b + n[0] * a, root[1] + d[1] * b + n[1] * a

    def far(u, w):   # 뿌리에서 얼마나 나갔나(길이 축)
        return (u - root[0]) * d[0] + (w - root[1]) * d[1]
    if kind == "curl":
        return chain([at(*p) for p in ((0, 0), (-0.2, 3.0), (1.2, 5.2), (3.2, 5.0))], 2.1, 1.7), \
            lambda u, w: L if far(u, w) > 4.6 else F     # 고리를 열면 손잡이로 읽혀 굵은 갈고리
    if kind == "plume":
        return chain([at(*p) for p in ((0, 0), (-0.2, 3.4), (0.8, 6.6), (2.8, 7.6))], 2.2, 1.8), \
            lambda u, w: L if far(u, w) > 5.6 else F
    if kind == "stub":
        return fluff(*at(0, 1.2), 1.8, 1.8, n=5, amp=0.15), lambda u, w: L
    if kind == "pom":
        return fluff(*at(0.6, 3.6), 3.4, 3.4, n=9, amp=0.12), lambda u, w: F
    if kind == "fluff":
        return fluff(*at(0.4, 2.8), 2.6, 2.6, n=8, amp=0.12), lambda u, w: D["DARK"] if far(u, w) < 1.2 else F
    if kind == "feather":
        return chain([at(*p) for p in ((0, 0), (-0.8, 3.6), (-1.0, 7.0))], 1.7, 1.1), \
            lambda u, w: L if far(u, w) > 4.6 else F
    if kind == "thin":
        return chain([at(*p) for p in ((0, 0), (-0.6, 3.6), (0.2, 7.0))], 1.0, 0.6), lambda u, w: F
    if kind == "pompom":
        return any_of(chain([at(0, 0), at(0, 4.6)], 0.8), fluff(*at(0, 6.0), 2.2, 2.2, n=7, amp=0.12)), \
            lambda u, w: coat(F, u, w)
    return chain([at(0, 0), at(0, 5.0)], 1.4, 1.0), lambda u, w: F


# ── 금지 표지 ─────────────────────────────────────────────────────────────────
def sign(f: dict, R: float = 13.5) -> None:
    ring = {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
    slash = set()
    for t in range(-90, 91):
        x, y = 15.5 + t / 100 * (R - 1.5) * 0.7071, 15.5 + t / 100 * (R - 1.5) * 0.7071
        slash |= disc(x, y, 1.3)
    solid(f, ring | slash, SIGN, SIGN_D)


def in_sign(o: dict) -> dict:
    f = {}
    sign(f)
    f.update({p: c for p, c in o.items() if 1 <= p[1] <= 30 and 1 <= p[0] <= 30})
    return f


def marks(f: dict, pts, col=MARK) -> None:
    for p in pts:
        if 0 <= p[0] <= 31 and 0 <= p[1] <= 31:
            f.setdefault(p, col)


def glyph(f: dict, rows, x0, y0, col) -> None:
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "#":
                f[x0 + i, y0 + j] = col


BANG = ["#", "#", "#", ".", "#"]
NOTE = [".##", ".#.", ".#.", "##.", "##."]
QM = [".##.", "#..#", "...#", "..#.", "....", "..#."]
ZZ = ["###", "..#", ".#.", "###"]


# ── 옆모습 닥스훈트 ───────────────────────────────────────────────────────────
def dachs_side(rig: Rig, k=0, yawn=0.0, mood="open", snout_up=0.0, tail_up=0.0, flip=False) -> dict:
    """엎드린 옆모습 닥스 — 왼쪽이 머리. yawn 0–1 은 아래턱이 벌어진 정도, snout_up 은 고개를 쳐든 각(도)"""
    F, Dk, L = D["FUR"], D["DARK"], D["LIGHT"]
    hc = (-9.0, -3.4)
    t = math.radians(-snout_up)
    c, s = math.cos(t), math.sin(t)

    def rot(p):   # 머리 가운데를 축으로 고개를 든다
        dx, dy = p[0] - hc[0], p[1] - hc[1]
        return hc[0] + dx * c - dy * s, hc[1] + dx * s + dy * c
    jaw_a = math.radians(-snout_up + 28 * yawn)
    jc, js = math.cos(jaw_a), math.sin(jaw_a)
    jaw_root = rot((-11.4, -1.6))
    jaw_tip = (jaw_root[0] - 4.0 * jc, jaw_root[1] + 4.0 * js)
    snout_tip = rot((-15.6, -3.0))
    sw = math.sin(2 * math.pi * k / N)
    parts = [("ear", ell(*rot((-7.6, -1.4)), 1.9, 3.6, 0.25), Dk, True),
             ("eye_bg", ell(0, 0, 0.01, 0.01), F, False),
             ("snout", bar(rot((-11.0, -3.0)), snout_tip, 2.6, 1.7), F, True),
             ("jaw", bar(jaw_root, jaw_tip, 1.3, 0.9), L, True),
             ("mouthin", tri(jaw_root, snout_tip, jaw_tip) if yawn > 0.2 else ell(0, 0, 0.01, 0.01), MOUTH, False),
             ("head", ell(*hc, 4.6, 4.0), F, True),
             ("fleg", any_of(bar((-6.0, 3.0), (-9.4, 4.2), 1.4), bar((-4.2, 3.2), (-7.4, 4.6), 1.4)), F, True),
             ("body", any_of(bar((-5.0, 0.6), (8.4, 0.8), 3.6)), lambda a, b: L if b > 2.6 else F, False),
             ("hleg", bar((7.6, 3.0), (4.4, 4.4), 1.5), F, True),
             ("tail", chain([(11.6, 0.0), (14.0, -1.4 - tail_up + sw * 0.6 * (1 + tail_up)), (15.0, -3.6 - tail_up * 1.4)],
                            1.0, 0.6), F, False)]
    f = draw(rig, parts)
    ex, ey = rig.world(*rot((-10.0, -4.6)))
    x0, y0 = round(ex - 1), round(ey - 1)
    if mood == "open":
        for p in ((x0, y0), (x0 + 1, y0), (x0, y0 + 1), (x0 + 1, y0 + 1)):
            f[p] = EYE
        f[x0, y0] = HI
    elif mood == "squeeze":
        for p in ((x0, y0 - 1), (x0 + 1, y0), (x0, y0 + 1)):
            f[p] = EYE
    else:
        f[x0, y0 + 1] = EYE
        f[x0 + 1, y0 + 1] = EYE
        if mood == "sulk":
            f[x0 + 2, y0] = EYE
    nx, ny = rig.world(snout_tip[0] + 0.4, snout_tip[1] - 0.4)
    f[math.floor(nx), math.floor(ny)] = NOSE
    f[math.floor(nx) + 1, math.floor(ny)] = NOSE
    if yawn > 0.4:   # 혀
        tx, ty = rig.world(jaw_root[0] - 2.2 * jc, jaw_root[1] + 2.2 * js - 0.6)
        f[math.floor(tx), math.floor(ty)] = TONGUE
        f[math.floor(tx) + 1, math.floor(ty)] = TONGUE
    return f


# ── wait ─────────────────────────────────────────────────────────────────────
def w_shiba():
    """공을 물고 꼬리 프로펠러 — 말린 꼬리가 뒤에서 뱅글뱅글, 바람 줄이 돈다"""
    frames = []
    rig = Rig(15.0, 17.4, 0.0, 0.8)
    for k, ph in enumerate(phases()):
        a = 2 * math.pi * k / 6
        tip = (7.0 + 3.6 * math.cos(a), 0.6 + 3.6 * math.sin(a))
        prop = ("tail", chain([(4.8, 3.6), (7.0, 0.6), tip], 1.9, 1.4), lambda u, v: D["LIGHT"] if v > 2.4 else D["FUR"],
                False)
        by = -1.8 + 0.3 * math.sin(2 * ph)
        ball = ("ball", ell(0.0, by, 3.5, 3.2),
                lambda u, v: BALL_W if abs(math.hypot(u + 3.4, v - by) - 3.2) < 0.6 else BALL, True)
        hop = 0.4 * abs(math.sin(2 * ph))
        f = sit(Rig(15.0, 17.4 - hop, 0.0, 0.8), k, mood="happy", mo="none", tail="none", behind=[prop], front=[ball])
        for i in range(3):   # 바람 고리
            b = a + 2.0 + i * 0.5
            x, y = rig.world(7.0 + 5.6 * math.cos(b), 0.6 + 5.6 * math.sin(b))
            marks(f, [(math.floor(x), math.floor(y))], MARK_L)
        frames.append(finish(f))
    return frames


def corgi_butt(rig: Rig, k, sway: float, look: int = -1, mood="open", mo="tongue", hop=0.0) -> dict:
    """뒷모습 코기 — 하트 식빵 엉덩이(가운데 흰 솜털) · 짧은 다리 · 어깨 너머로 돌아보는 얼굴"""
    F, Dk, L = D["FUR"], D["DARK"], D["LIGHT"]
    hips = Rig(*rig.world(0.0, 6.0), rig.ang + sway, rig.k)
    legs = [("feet", any_of(ell(-4.0, 7.8, 2.2, 1.3), ell(4.0, 7.8, 2.2, 1.3)), L, True),
            ("legs", any_of(bar((-4.0, 4.0), (-4.0, 7.2), 1.9), bar((4.0, 4.0), (4.0, 7.2), 1.9)), F, True)]
    f = draw(rig, legs)
    pants = ("pants", any_of(ell(-1.5, 0.0, 2.0, 2.2), ell(1.5, 0.0, 2.0, 2.2), ell(0.0, 1.4, 1.6, 1.8)), L, False)
    cheeks = ("butt", any_of(ell(-3.9, -2.2 - hop, 4.9, 4.0), ell(3.9, -2.2 - hop, 4.9, 4.0)), F, False)
    back = ("back", ell(0.0, -7.0, 4.8, 4.2), F, False)
    stub = ("stub", fluff(0.0, -5.6 - hop, 1.6, 1.2, n=5, amp=0.15), L, True)
    f.update(draw(hips, [stub, pants, cheeks, back]))
    # 엉덩이 골
    for t in range(3):
        x, y = hips.world(0.0, -4.0 + t)
        f.setdefault((math.floor(x), math.floor(y)), OUT)
        if f.get((math.floor(x), math.floor(y))) == F:
            f[math.floor(x), math.floor(y)] = OUT
    hc = (look * 2.6, -13.6)
    hr = Rig(*hips.world(0.0, 0.0), rig.ang, rig.k)
    r = 6.8      # 뒤통수 + 어깨 너머로 내민 옆 주둥이 · 눈 하나 — 앞얼굴을 그리면 앞모습으로 읽혔다
    tip = (hc[0] + look * r * 1.12, hc[1] + r * 0.3)
    snout = (f"snout", ell(hc[0] + look * r * 0.82, hc[1] + r * 0.3, r * 0.46, r * 0.32), L, True)
    g = draw(hr, [snout] + head_parts(hc, r, rear=True))
    nx, ny = hr.cell(*tip)
    g[nx, ny - 1] = NOSE
    g[nx - look, ny - 1] = NOSE
    if mo in ("tongue",) and k % 4 < 2:
        g[nx - look * 2, ny + 1] = TONGUE
        g[nx - look * 2, ny + 2] = TONGUE
    ex, ey = hr.cell(hc[0] + look * r * 0.5, hc[1] - r * 0.1)
    if mood == "open":
        g[ex, ey] = EYE
        g[ex, ey + 1] = EYE
    elif mood == "happy":
        g[ex - 1, ey + 1] = EYE
        g[ex, ey] = EYE
        g[ex + 1, ey + 1] = EYE
    else:
        g[ex - 1, ey + 1] = EYE
        g[ex, ey + 1] = EYE
        g[ex + 1, ey + 1] = EYE
    cx, cy = hr.cell(hc[0] + look * r * 0.55, hc[1] + r * 0.32)
    if g.get((cx, cy)) not in (OUT, None):
        g[cx, cy] = CHEEK
    f.update(g)
    return f


def w_corgi():
    """식빵 엉덩이 씰룩씰룩 — 뒤돌아 엉덩이를 흔들며 어깨 너머로 해맑게 돌아본다"""
    frames = []
    for k, ph in enumerate(phases()):
        sway = 9.0 * math.sin(2 * ph)
        f = corgi_butt(Rig(16.0, 20.0, 0.0, 0.82), k, sway, look=-1, mood="happy" if k % 6 < 3 else "open", mo="tongue")
        if abs(math.sin(2 * ph)) > 0.8:
            sd = 1 if math.sin(2 * ph) > 0 else -1
            x0 = 16 + sd * 11
            marks(f, [(x0, 19), (x0, 21), (x0 + sd, 20), (x0 + sd, 22)])
        frames.append(finish(f))
    return frames


def w_pomeranian():
    """제자리 빙글 — 앞 · 옆 · 뒤 · 옆으로 돌며 통 튄다. 뒤일 때는 솜꼬리가 몸을 덮는다"""
    frames = []
    for k, ph in enumerate(phases()):
        a = 2 * math.pi * k / N
        turn = 3.4 * math.sin(a)
        back = math.cos(a) < -0.35
        hop = 1.2 * abs(math.sin(a))
        rig = Rig(16.0, 17.0 - hop, 0.0, 0.78)
        tail = ("tail", fluff(-turn * 1.4, 1.0, 4.6, 4.0, n=9, amp=0.12, ph=k), D["FUR"], False)
        if back:
            f = sit(rig, k, turn=turn, tail="none", face=False, front=[tail])
        else:
            f = sit(rig, k, turn=turn, mood="happy", mo="tongue", tail="none" if abs(turn) < 2 else "pom")
        cx, cy = 16, 28
        for i in range(8):   # 바닥 소용돌이
            b = a * 2 + i * 0.5
            marks(f, [(round(cx + 9 * math.cos(b)), round(cy + 1.4 * math.sin(b)))], MARK_L if i > 3 else MARK)
        frames.append(finish(f))
    return frames


def w_bichon():
    """솜머리 통통 — 동그란 솜사탕 머리가 납작 · 길쭉 통통 튀고 몸이 따라 들썩"""
    frames = []
    for k, ph in enumerate(phases()):
        sq = 0.16 * math.cos(2 * ph)
        hop = 1.4 * max(0.0, -math.cos(2 * ph))
        rig = Rig(16.0, 18.0 - hop, 0.0, 0.82)
        f = sit(rig, k, squash=sq, mood="happy" if sq > 0.08 else "open", hc=(0.0, -7.5 + sq * 3))
        if sq > 0.1:
            marks(f, [(4, 9), (5, 8), (27, 9), (26, 8)], MARK_L)
        frames.append(finish(f))
    return frames


def w_retriever():
    """혀 내밀고 헥헥 — 혀가 들썩이고 어깨가 오르내리며 꼬리를 바닥에 탁탁"""
    frames = []
    for k, ph in enumerate(phases()):
        br = 0.3 * math.sin(4 * ph)
        rig = Rig(15.0, 17.0, 0.0, 0.84)
        f = sit(rig, k * 2, hc=(0.0, -7.5 + br), mood="happy" if k in (4, 5) else "open", mo="pant", swing=br * 0.6)
        if k % 2 == 0:
            marks(f, [(4, 10), (3, 11), (27, 10), (28, 11)], MARK_L)
        frames.append(finish(f))
    return frames


def w_dachshund():
    """긴 몸으로 엎드려 하아암 — 아래턱이 쩍 벌어지고 눈을 질끈, 끝나면 졸린 눈"""
    frames = []
    #      0  1  2    3    4    5  6  7  8    9   10  11
    yawn = [0, 0, 0.2, 0.5, 0.9, 1, 1, 1, 0.7, 0.2, 0, 0]
    mood = ["open", "open", "blink", "squeeze", "squeeze", "squeeze", "squeeze", "squeeze", "squeeze", "blink",
            "sleep", "open"]
    for k, ph in enumerate(phases()):
        rig = Rig(16.6, 17.0, 0.0, 0.92)
        f = dachs_side(rig, k, yawn[k], mood[k], snout_up=14 * yawn[k])
        if yawn[k] > 0.8:
            marks(f, [(2, 6), (3, 5), (1, 9)], MARK_L)
        frames.append(finish(f))
    return frames


def w_husky():
    """아우우— 하울링. 고개를 쳐들고 눈을 감은 채 입을 O, 음표 물결이 위로 피어오른다"""
    frames = []
    for k, ph in enumerate(phases()):
        up = max(0.0, math.sin(ph))      # 0 → 1 → 0
        howl = k in range(1, 7)
        rig = Rig(15.6, 18.0, 0.0, 0.8)
        hc = (0.0, -7.5 - 1.6 * up)
        f = sit(rig, k, hc=hc, mood="sleep" if howl else "open", mo="O" if howl else "smile", tilt=-6 * up)
        if howl:
            for i in range(2):
                y = 6 - (k - 1 + i * 3) % 6
                glyph(f, NOTE, 22 + i * 3, y, MARK)
        frames.append(finish(f))
    return frames


def w_poodle():
    """갸웃 갸웃 — 귀 뭉치를 늘어뜨린 채 고개를 왼쪽 · 오른쪽으로 기울이고, 물음표가 떠오른다"""
    frames = []
    for k, ph in enumerate(phases()):
        tl = 16 * math.sin(ph)
        rig = Rig(16.0, 18.0, 0.0, 0.8)
        f = sit(rig, k, tilt=tl, mood="open", swing=-tl * 0.03, look=-1 if tl < 0 else 1)
        if abs(tl) > 12:
            glyph(f, QM, 24 if tl > 0 else 4, 2, MARK)
        frames.append(finish(f))
    return frames


def w_maltese():
    """리본 흔들며 꾸벅꾸벅 — 고개가 떨어지며 눈이 감기다가 화들짝, 리본이 까딱"""
    frames = []
    drop = [0, 0, 0.5, 1.0, 1.5, 2.0, 2.4, 2.4, 2.4, 0, 0, 0]
    mood = ["open", "open", "blink", "blink", "sleep", "sleep", "sleep", "sleep", "sleep", "open", "open", "blink"]
    for k, ph in enumerate(phases()):
        rig = Rig(16.0, 18.0, 0.0, 0.82)
        f = sit(rig, k, hc=(0.0, -7.5 + drop[k]), tilt=4 * drop[k], mood=mood[k], mo="smile",
                swing=0.5 * math.sin(2 * ph))
        if 5 <= k <= 8:
            glyph(f, ZZ, 25 + (k - 5) // 2, 4 - (k - 5) // 2, MARK_L)
        if k == 9:
            for p in ((7, 6), (8, 5), (16, 1), (16, 2), (24, 5), (25, 6)):
                f[p] = OUT
        frames.append(finish(f))
    return frames


def w_jindo():
    """똑바로 앉아 경계 — 바짝 선 귀가 번갈아 쫑긋, 눈이 좌우를 살피다 '!'"""
    frames = []
    look = [0, -1, -1, -1, 0, 1, 1, 1, 0, 0, 0, 0]
    for k, ph in enumerate(phases()):
        ears = (0.25 if k in (2, 3) else 0.0, 0.25 if k in (6, 7) else 0.0)
        rig = Rig(15.6, 17.4, 0.0, 0.84)
        f = sit(rig, k, ears=ears, look=look[k], mood="open", turn=look[k] * 0.8, wag=0.3)
        if k in (9, 10, 11):
            glyph(f, BANG, 25, 2 + (1 if k == 9 else 0), SIGN)
            glyph(f, BANG, 26, 2 + (1 if k == 9 else 0), SIGN)
        frames.append(finish(f))
    return frames


# ── no ───────────────────────────────────────────────────────────────────────
def n_shiba():
    """산책 거부 — 목줄이 왼쪽 위로 당겨도 네 발로 버티고 뒤로 기댄 채 '싫어' 눈"""
    frames = []
    for k, ph in enumerate(phases()):
        tug = k % 4 in (0, 1)
        lean = 10.0 + (5.0 if tug else 0.0)
        rig = Rig(17.0, 18.2, lean, 0.66)
        paws = [[(-2.6, 1.0), (-5.6, 8.0)], [(2.4, 1.0), (-1.4, 8.4)]]   # 앞발을 앞으로 내밀어 버팀
        collar = ("collar", bar((-4.4, -1.6), (4.4, -1.6), 0.9), LEASH, True)
        f = sit(rig, k, paws=paws, mood="squeeze" if tug else "sulk", mo="flat", turn=1.2, front=[collar], wag=0.2)
        cx, cy = rig.world(-2.0, -1.4)
        x1, y1 = 5.0, 5.0
        n = 24
        for i in range(n + 1):   # 목줄 — 당길 때 팽팽, 늦출 때 처짐
            t = i / n
            x = cx + (x1 - cx) * t
            y = cy + (y1 - cy) * t + (0 if tug else 2.0 * math.sin(math.pi * t))
            f[math.floor(x), math.floor(y)] = LEASH_D
        if tug:
            marks(f, [(24, 10), (25, 10), (24, 13), (25, 13)])
        frames.append(finish(in_sign(f)))
    return frames


def n_corgi():
    """홱 엉덩이 돌리기 — 등을 보이고 앉아 어깨 너머로 흥, 엉덩이를 좌우로 탁탁"""
    frames = []
    for k, ph in enumerate(phases()):
        side_ = -1 if k < 6 else 1
        snap = k in (0, 6)
        f = corgi_butt(Rig(15.6, 19.0, 0.0, 0.7), k, side_ * (4.0 if snap else 8.0), look=side_, mood="sulk", mo="flat")
        if snap:
            x0 = 25 if side_ < 0 else 6
            marks(f, [(x0, 14), (x0, 16), (x0, 18), (x0 + 1, 14), (x0 + 1, 16), (x0 + 1, 18)])
        frames.append(finish(in_sign(f)))
    return frames


def n_pomeranian():
    """왈왈! — 털을 부풀리고 앞발로 통통 뛰며 짖는다"""
    frames = []
    for k, ph in enumerate(phases()):
        bark = k % 3 != 2
        hop = 1.2 if bark else 0.0
        rig = Rig(15.6, 18.0 - hop, 0.0, 0.66)
        f = sit(rig, k, mood="angry", mo="open" if bark else "flat", wag=1.6)
        if bark:
            for i, (x, y) in enumerate(((7, 7), (24, 7))):
                glyph(f, BANG[1:], x + (i * 2 - 1), y, OUT)
            marks(f, [(6, 12), (5, 13), (25, 12), (26, 13)])
        frames.append(finish(in_sign(f)))
    return frames


def n_bichon():
    """도리도리 — 솜머리를 좌우로 세차게 흔든다(움직임 줄)"""
    frames = []
    for k, ph in enumerate(phases()):
        side_ = 1 if (k // 2) % 2 == 0 else -1
        rig = Rig(15.6, 18.2, 0.0, 0.66)
        f = sit(rig, k, turn=side_ * 2.2, tilt=side_ * 8, mood="squeeze", mo="flat")
        x0 = 6 if side_ > 0 else 25
        marks(f, [(x0, 8), (x0, 10), (x0, 12), (x0 - side_, 9), (x0 - side_, 11)])
        frames.append(finish(in_sign(f)))
    return frames


def n_retriever():
    """엎드려 꿈쩍 안 함 — 앞발 위에 턱을 괴고 촉촉한 눈으로 한숨"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(15.6, 17.0, 0.0, 0.66)
        hc = (0.0, -2.6)
        paws = [[(-3.2, 5.4), (-4.2, 8.6)], [(3.2, 5.4), (4.2, 8.6)]]
        body = ("body", any_of(ell(0.0, 6.4, 10.4, 4.2)), lambda a, b: D["FUR"], False)
        f = sit(rig, k, hc=hc, paws=paws, body=body, tail="feather", wag=0.4, mood="sad", mo="smile",
                swing=0.0)
        if k in range(6, 11):
            glyph(f, [".##.", "#..#", ".##."], 23 + (k - 6) // 2, 9 - (k - 6), MARK_L)
        frames.append(finish(in_sign(f)))
    return frames


def n_dachshund():
    """흥 — 엎드린 채 코를 쳐들고 눈을 감아 외면, 꼬리로 바닥을 탁탁"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(16.2, 17.4, 0.0, 0.74)
        up = 26 if k % 6 < 4 else 20
        f = dachs_side(rig, k * 2, 0.0, "sulk", snout_up=up, tail_up=0.6)
        if k % 6 in (0, 1):   # 흥 — 콧김
            for p in ((4, 9), (3, 8), (5, 8), (4, 7)):
                f.setdefault(p, MARK_L)
        frames.append(finish(in_sign(f)))
    return frames


def n_husky():
    """드러누워 항의 — 발라당 누워 네 발을 허우적, 입을 벌려 아우 항의"""
    frames = []
    F, Dk, L = D["FUR"], D["DARK"], D["LIGHT"]
    for k, ph in enumerate(phases()):
        rig = Rig(17.0, 19.0, 0.0, 0.7)
        kick = [math.sin(ph * 2 + i * 1.6) for i in range(4)]
        legs = []
        for i, (x0, sg) in enumerate(((-4.4, -1), (-1.4, -1), (3.0, 1), (6.0, 1))):
            knee = (x0 + 0.6 * kick[i], -6.6 + 0.8 * kick[i])          # 굽은 다리 — 곧게 세우면 빌딩 줄로 읽혔다
            tip = (knee[0] - 2.0, knee[1] - 0.6 + 0.8 * kick[i])
            legs += [(f"p{i}", ell(*tip, 1.8, 1.6), L, True), (f"l{i}", chain([(x0, -1.0), knee, tip], 1.8, 1.5), F, True)]
        body = ("body", ell(1.0, 0.6, 8.8, 5.2), lambda a, b: L if b < 1.4 and abs(a - 1.0) < 7.0 else F, False)
        tail = ("tail", chain([(9.0, 2.4), (12.2, 1.0 + kick[0]), (13.0, -1.6 + kick[1])], 1.8, 1.4),
                lambda a, b: L if a > 12.0 else F, False)
        f = draw(rig, legs + [body, tail])
        hrig = rig.turned((-9.6, 0.4), -22 + 6 * math.sin(4 * ph))
        hc = (-9.6, 0.4 - 5.0)
        g = draw(hrig, head_parts(hc, 5.6))
        eyes(g, hrig, hc, 5.6, "squeeze")
        mouth(g, hrig, hc, 5.6, "open" if k % 4 < 2 else "O")
        f.update(g)
        if k % 4 < 2:
            glyph(f, BANG, 6, 4, OUT)
            glyph(f, BANG, 8, 4, OUT)
        frames.append(finish(in_sign(f)))
    return frames


def n_poodle():
    """콧대 높게 흥 — 고개를 쳐들어 홱 돌리고 눈을 감는다, 반 바퀴마다 반대쪽"""
    frames = []
    for k, ph in enumerate(phases()):
        side_ = -1 if k < 6 else 1
        snap = k in (0, 6)
        rig = Rig(15.6, 18.6, 0.0, 0.66)
        f = sit(rig, k, hc=(0.0, -8.0), turn=side_ * (1.4 if snap else 2.4), tilt=side_ * (6 if snap else 12),
                mood="sulk", mo="flat")
        if snap:
            x0 = 6 if side_ > 0 else 25
            marks(f, [(x0, 8), (x0, 10), (x0, 12), (x0 - side_, 8), (x0 - side_, 10), (x0 - side_, 12)])
        frames.append(finish(in_sign(f)))
    return frames


def n_maltese():
    """안 볼래 — 두 앞발로 눈을 가리고 고개를 도리도리, 리본이 흔들"""
    frames = []
    for k, ph in enumerate(phases()):
        sh = 0.8 * math.sin(2 * ph)
        rig = Rig(15.6, 18.2, 0.0, 0.66)
        hc = (sh, -7.5)
        paws = []
        front = []
        for i, sg in enumerate((-1, 1)):
            tip = (sh + sg * 2.9, -7.8)
            front += [(f"cp{i}", ell(*tip, 2.5, 2.2), D["FUR"], True)]   # 팔은 빼고 발만 — 팔 테가 가슴을 어지럽혔다
        f = sit(rig, k, hc=hc, mood="blink", mo="flat", swing=sh * 0.6, front=front)
        x0 = 6 if sh > 0 else 25
        if abs(sh) > 0.6:
            marks(f, [(x0, 9), (x0, 11)])
        frames.append(finish(in_sign(f)))
    return frames


def n_jindo():
    """으르렁 — 귀를 뒤로 젖히고 몸을 낮춰 이빨을 드러낸다, 머리 위 화난 표시가 두근"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(15.6, 19.0, 0.0, 0.66)
        shake = 1 if k % 2 else 0
        paws = [[(-2.8, 1.0), (-4.6, 7.4)], [(2.8, 1.0), (4.6, 7.4)]]
        f = sit(Rig(15.6 + shake * 0.5, 19.0, 0.0, 0.66), k, hc=(0.0, -6.4), paws=paws, ears=(0.85, 0.85),
                mood="angry", mo="teeth", wag=0.0)
        big = k % 4 < 2
        cx, cy = 22, 6
        for d_ in ((-1, -1), (1, -1), (-1, 1), (1, 1)):   # 화난 표시(╬ 꼴)
            for i in range(1, 3 if big else 2):
                f[cx + d_[0] * i, cy + d_[1] * (1 if i == 1 else 2)] = SIGN
        if k % 3 == 0:
            marks(f, [(6, 20), (7, 21), (6, 22)])
        frames.append(finish(in_sign(f)))
    return frames


# ── 작은 화살표 댕댕이와 소품 (busy · help · person · pin) ─────────────────────────
C_S = 0.8                        # 작은 판 화살표 배율
C_AT = (2, 17)                   # 작은 댕댕이 도장 왼쪽 위 — 화살표 밑, 소품은 오른쪽 절반(벌어진 귀 끝이 x-1 까지 나가 한 칸 띄움)
C_NECK = (8, 9)                  # 도장 안 목 칸 — person 리드줄이 닿는 자리

# 작은 앞모습 댕댕이(12×14 칸) — 부위를 0.5 배로 줄여 그리면 테가 속을 다 먹어 시커먼 투구가 됐다.
# 네모 머리에 정수리 세모 귀 · 주둥이 없음은 고양이로 읽혀서, 귀는 머리 양옆 위로 낮고 넓게 벌리고
# 밝은 주둥이를 볼 밑으로 한 줄 내밀고 코 2칸 · ᴥ 입 · 빼꼼 나온 혀를 넣었다.
# o 테 · F 털 · D 짙은 털 · L 밝은 털 · I 귀 속 · E 눈 · N 코 · T 혀 · P 발(양말이면 밝은 털) · R 리본 · t 꼬리
MINI_TOP = {
    "prick": ["oo..........oo", "oIo........oIo", ".oIIooooooIIo."],   # 14 칸 — 귀 끝이 머리 밖 양옆 위로 기울게
    "small": ["............", ".oo......oo.", "oIFooooooFIo"],
    "round": ["............", "..oooooooo..", ".oFFFFFFFFo."],
    "drop": ["............", "...oooooo...", ".ooFFFFFFoo."],
    "knot": ["....oooo....", "...oFFFFo...", ".ooFFFFFFoo."],
    "bow": ["...oRRoRRo..", "...oooooo...", ".ooFFFFFFoo."],
}
MINI_FACE = {                                                   # 3–8 줄: 얼굴 · 볼 밑으로 내민 주둥이
    "wide": ["oFFFFFFFFFFo", "oFFEFFFFEFFo", "oFFEFFFFEFFo", "oFFLLNNLLFFo", ".oFLoLLoLFo.", "..ooLTTLoo.."],
    "drop": ["oDDoFFFFoDDo", "oDDEFFFFEDDo", "oDDEFFFFEDDo", "oDDLLNNLLDDo", "oDDFoLLoFDDo", ".oooLTTLooo."],
}
MINI_BODY = ["..oFoTToFo..", ".oFFLLLLFFo.", ".oFFLLLLFFo.", ".oFPPooPPFo.", "..oooooooo.."]
MINI_TONGUE = ["....oTTo....", ".....oo....."]                 # 머리만 찍을 때(핀) 혀 끝
MINI_EYES = ((3, 4), (8, 4))                                    # 눈 위 칸
MINI_TAIL = {                                                   # 오른쪽 옆구리(10 칸 · 7 줄부터) — 위 · 가운데 · 옆
    "thin": (["..oo", ".oto", ".oto", "oto."], ["....", "..o.", ".oto", "oto."], ["....", "....", "..oo", "otto"]),
    "thick": (["..oo.", ".otto", "otto.", "oto.."], [".....", "..oo.", ".otto", "otto."], [".....", ".....", ".ooo.", "ottto"]),
    "puff": ([".oo..", "otto.", "otto.", ".oo.."], [".....", ".oo..", "otto.", "otto."], [".....", ".....", ".ooo.", "ottto"]),
}


def mini_dog(x0: int, y0: int, k: int = 0, mood: str = "open", body: bool = True) -> dict:
    """(x0, y0) 를 왼쪽 위로 찍는 작은 앞모습 댕댕이. body=False 면 머리만(핀 속 얼굴). 꼬리는 k 로 붕붕"""
    F, Dk, L = D["FUR"], D["DARK"], D["LIGHT"]
    drop = D["ear"] in ("drop", "hair", "poof")
    top = "knot" if D.get("topknot") else "bow" if D.get("ribbon") else \
        {"prick": "prick", "small": "small", "none": "round"}.get(D["ear"], "drop")
    rows = MINI_TOP[top] + MINI_FACE["drop" if drop else "wide"] + (MINI_BODY if body else MINI_TONGUE)
    col = {"o": OUT, "F": F, "D": Dk, "L": L, "I": D["INNER"], "E": D["EYE"], "N": NOSE, "R": RIBBON,
           "T": TONGUE, "P": L if D.get("sock") else F, "t": F}
    g = {}

    def stamp(rows_, ox, oy):
        for y, row in enumerate(rows_):
            dx = ox - (len(row) - 12) // 2 if ox == 0 else ox   # 14 칸 줄은 한 칸 왼쪽(x-1)부터
            for x, ch in enumerate(row):
                if ch != ".":
                    g[dx + x, oy + y] = col[ch]
    stamp(rows, 0, 0)
    if body and D["tail"] != "stub":
        kind = {"thin": "thin", "pom": "puff", "fluff": "puff", "pompom": "puff"}.get(D["tail"], "thick")
        sw = math.sin(2 * math.pi * k * 3 / N)
        stamp(MINI_TAIL[kind][0 if sw > 0.5 else 1 if sw > -0.5 else 2], 10, 7)
    marks = D["marks"]
    if "brow" in marks:
        g[3, 3] = g[8, 3] = L
    if "blaze" in marks:
        for y in (2, 3, 4, 5):
            g[5, y] = g[6, y] = L
    if "mask" in marks:
        for y in (4, 5):
            for x in (2, 4, 5, 6, 7, 9):
                g[x, y] = L
        g[5, 3] = g[6, 3] = L
    if mood != "open":   # 웃는 눈 — 아랫줄만 안쪽으로 한 칸 더
        for x, y in MINI_EYES:
            g[x, y] = L if "mask" in marks else F
            g[x + (1 if x < 6 else -1), y + 1] = D["EYE"]
    return {(x0 + x, y0 + y): c for (x, y), c in g.items()}


def companion(scene) -> list[dict]:
    """작은 화살표 + 그 밑에 앉아 꼬리 치는 작은 앞모습 댕댕이 + scene(k, ph) 이 그리는 소품(오른쪽 절반).
    물고 오는 옆모습을 줄이면 개가 뭉개지고 대가 가려져 앉은 앞모습 도장으로 바꿨다.
    화살표를 맨 나중에 찍고 둘레 한 칸을 비워 소품도 개도 화살표를 못 가린다"""
    arrow = {}
    am = put_arrow(arrow, C_S)
    near = {(x + dx, y + dy) for x, y in am for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    frames = []
    for k, ph in enumerate(phases()):
        f = scene(k, ph)
        f.update(mini_dog(*C_AT, k, mood="happy" if k in (7, 8) else "open"))
        f = {p: c for p, c in clip(f).items() if p not in near}
        f.update(arrow)
        frames.append(finish(f))
    return frames


def paw_print(f: dict, cx: int, cy: int, col) -> None:
    """발자국: 2×2 큰 젤리 + 위에 발가락 넷"""
    for p in ((cx, cy), (cx + 1, cy), (cx, cy + 1), (cx + 1, cy + 1), (cx - 1, cy - 1), (cx + 2, cy - 1)):
        f[p] = col
    f[cx, cy - 2] = col
    f[cx + 1, cy - 2] = col


def bone_parts(L: float, rs: float = 0.9, rk: float = 1.4, name="bone") -> list:
    """u 축으로 누운 뼈다귀 — 막대 양끝에 동그란 마디 둘씩. L 은 가운데에서 마디 가운데까지"""
    knobs = any_of(*[ell(sg * L, sd * rk * 0.78, rk, rk) for sg in (-1, 1) for sd in (-1, 1)])
    return [(name, any_of(bar((-L, 0.0), (L, 0.0), rs), knobs), lambda a, b: BONE_D if b > rs * 0.5 else BONE, True)]


def tennis(f: dict, cx: float, cy: float, r: float, k: int = 0) -> None:
    """테니스공 — 연두 동그라미에 흰 솔기 곡선 하나"""
    m = disc(cx, cy, r)
    solid(f, m, lambda p: BALL_W if abs(math.hypot(p[0] + 0.5 - (cx - r * 1.1), p[1] + 0.5 - cy) - r * 1.05) < 0.5
          else BALL, OUT)


def busy() -> list[dict]:
    """오른쪽 빈자리에 발자국 여덟 개가 원을 그리며 차례로 진해지고, 가운데 뼈다귀가 까딱"""
    cx, cy, R = 21.5, 17.5, 7.6

    def scene(k, ph):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = round(cx + R * math.cos(a) - 0.5), round(cy + R * math.sin(a) - 0.5)
            lag = (head - i) % 8
            paw_print(f, x, y + 1, GLOW[0] if lag < 1.5 else GLOW[1] if lag < 3 else GLOW[2])
        f.update(draw(Rig(cx, cy + 0.5, -28.0 + 16.0 * math.sin(2 * ph), 1.0), bone_parts(2.8, 0.9, 1.25)))
        return f
    return companion(scene)


def help_() -> list[dict]:
    """물음표 꼴로 늘어진 파란 리드줄(끝에 은빛 고리) + 점 자리에 테니스공 — 줄 끝이 살랑인다"""
    def scene(k, ph):
        f = {}
        sw = 0.8 * math.sin(ph)
        pts = [(21.5, 19.6), (21.5, 16.4), (24.4, 13.8), (27.2, 11.0), (27.2, 6.8), (24.2, 3.8), (20.4, 4.0),
               (18.2, 6.6 + sw)]
        f.update(draw(Rig(0, 0, 0, 1.0), [("clip", ell(17.8, 7.6 + sw, 1.4, 1.4), CLIP, True),
                                           ("leash", chain(pts, 1.2), LEASH, False)]))
        tennis(f, 21.5, 25.4, 2.6, k)
        return f
    return companion(scene)


def person() -> list[dict]:
    """리드줄 손잡이를 쥔 사람이 오른손을 흔든다 — 줄은 작은 댕댕이 목으로 이어진다"""
    neck = (C_AT[0] + C_NECK[0] + 0.5, C_AT[1] + C_NECK[1] + 0.5)

    def scene(k, ph):
        rig = Rig(22.6, 19.0, 0.0, 0.74)
        wave = -2.0 * abs(math.sin(ph))
        hand = (8.0, -6.0 + wave)
        hold = (-6.8, 1.0)
        parts = [("hand", ell(*hand, 1.7, 1.7), SKIN, True), ("sleeve", bar((5.0, -0.5), hand, 1.6), SHIRT, False),
                 ("hold", ell(*hold, 1.8, 1.8), SKIN, True), ("sleeve2", bar((-5.0, -0.5), hold, 1.6), SHIRT, False),
                 ("skin", ell(0.0, -7.6, 5.0, 4.6),          # 머리칼 — 정수리 · 옆머리를 넉넉히(좁으면 대머리로 읽혔다)
                  lambda a, b: HAIR if b < -8.8 or (abs(a) > 3.2 and b < -6.0) else SKIN, True),
                 ("torso", ell(0, 3.0, 7.6, 6.4), lambda a, b: SHIRT_D if abs(a) < 0.6 else SHIRT, False)]
        f = {}
        hx_, hy_ = rig.world(*hold)
        for i in range(31):   # 리드줄 — 사람 손에서 목까지 살짝 처진 줄
            t = i / 30
            x = hx_ + (neck[0] - hx_) * t
            y = hy_ + (neck[1] - hy_) * t + 2.0 * math.sin(math.pi * t)
            f[math.floor(x), math.floor(y)] = LEASH_D
        out = draw(rig, parts)
        for sg in (-1, 1):
            ex, ey = rig.cell(sg * 2.0, -6.8)
            out[ex, ey] = EYE
            out[ex, ey + 1] = EYE
            out[rig.cell(sg * 3.0, -4.8)] = CHEEK
        f.update(out)
        return f
    return companion(scene)


def pin() -> list[dict]:
    """빨간 지도 핀 동그라미 속에 그 견종 얼굴 — 쫑긋 귀 · 리본 · 방울은 핀 위로 솟는다. 핀이 통통, 땅에 닿을 때 눈 질끈"""
    def scene(k, ph):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.0, 15.0 + dy
        for x in range(18, 26):
            f.setdefault((x, 29), GLOW[2] if dy else GLOW[1])
        x0, y0 = int(cx) - 6, int(cy) - 8
        # 머리 꼭대기 줄보다 위 핀은 비운다 — 귀 사이로 빨간 띠가 지나가 모자로 읽혔다
        pinm = {p for p in disc(cx, cy, 7.2) | raster([(cx - 5.0, cy + 4.2), (cx + 5.0, cy + 4.2), (cx, cy + 13.4)])
                if p[1] >= y0 + 2}
        solid(f, pinm, SIGN, SIGN_D)
        f.update(mini_dog(x0, y0, k, mood="happy" if dy == 0 else "open", body=False))
        return f
    return companion(scene)


def bean_paw(f: dict, rig: Rig, pc, pr: float, sq: float = 0.0) -> None:
    """발바닥 젤리: 아래 가운데 큰 젤리 + 위로 부채꼴 발가락 젤리 넷 — pc 는 발바닥 가운데"""
    bx, by = rig.world(pc[0], pc[1] + pr * 0.28)
    bx, by = round(bx), round(by)
    w = 2 + round(sq)
    for dy in range(3):
        for dx in range(-w + (1 if dy == 0 else 0), w - (1 if dy == 0 else 0) + (0 if dy < 2 else -1)):
            f[bx + dx, by + dy] = PAD
    for tx, ty in ((-4 - round(sq), -2), (-2, -4), (1, -4), (3 + round(sq), -2)):
        f[bx + tx, by + ty] = PAD
        f[bx + tx, by + ty + 1] = PAD


H_RIG, H_PC, H_PR = (19.0, 21.4, 0.0, 0.74), (-9.8, -17.0), 5.0    # hand: 그리개 · 발바닥 가운데 · 반지름


def hand_pad(sq: float):
    pc = (H_PC[0], H_PC[1] - sq * 0.5)                # 위 끝은 그대로 두고 옆 · 아래로 퍼진다
    return pc, ("pad", ell(pc[0], pc[1], H_PR + sq, H_PR - sq * 0.5), D["LIGHT"], True)


def hand() -> list[dict]:
    """손! — 앞발을 왼쪽 위로 내밀어 분홍 젤리를 보이며 꾹. 누를 때(장 4–7) 발바닥이 납작하게 퍼지고 눈을 질끈(><).
    내민 팔은 몸 뒤 부위로 그려 어깨가 몸에 묻히고, 발바닥은 얼굴 위에 따로 찍는다"""
    frames = []
    rig = Rig(*H_RIG)
    leg = 7.4 if D.get("short") else 8.4
    for k, ph in enumerate(phases()):
        press = k in (4, 5, 6, 7)
        sq = 0.9 if press else 0.0
        pc, pad = hand_pad(sq)
        arm = ("reach", chain([(-3.4, -1.0), (-7.4, -9.0), pc], 2.4, 2.8), lambda a, b: coat(D["FUR"], a, b), False)
        f = sit(rig, k, paws=[[(2.4, 1.0), (2.6, leg)]], behind=[arm], front=[pad], turn=-0.6,
                mood="squeeze" if press else "open", mo="tongue" if press else D["mouth"])
        bean_paw(f, rig, pc, H_PR, sq)
        if press:   # 꾹 — 발바닥 둘레 눌림 줄
            x0, y0 = rig.cell(*pc)
            for p in ((x0 - 6, y0 - 3), (x0 - 7, y0 - 1), (x0 - 6, y0 + 4), (x0 + 6, y0 - 3), (x0 + 7, y0 - 1)):
                if 0 <= p[0] <= 31 and 0 <= p[1] <= 31:
                    f.setdefault(p, OUT)
        frames.append(finish(f))
    return frames


def hand_hot(frames) -> tuple:
    """발바닥 맨 위 칸 — 가운데 세로줄에서 가장 위 칸"""
    m = draw(Rig(*H_RIG), [hand_pad(0.0)[1]])
    x = math.floor(Rig(*H_RIG).world(*H_PC)[0])
    return x, min(y for (xx, y) in m if xx == x)


CR_LONG = {"snout": 1.45, "ear_s": 0.95, "squash": -0.2, "ears": 0.22}   # 쫑긋 귀 견종 cross 얼굴 — 길이 · 귀 배율 · 볼 · 귀 기울기


CR_LONG = {"snout": 1.45, "ear_s": 0.95, "squash": -0.2, "ears": 0.22}   # 쫑긋 귀 견종 cross 얼굴 — 길이 · 귀 배율 · 볼 · 귀 기울기
CR_BOW = ["ooo.ooo", "oRR.RRo", "oRD.DRo", ".oF.Fo."]   # 말티즈 정수리 나비 리본(가운데 세로줄은 리드줄이 매듭) + 상투


CR_LONG = {"snout": 1.45, "ear_s": 0.95, "squash": -0.2, "ears": 0.22}   # 쫑긋 귀 견종 cross 얼굴 — 길이 · 귀 배율 · 볼 · 귀 기울기
CR_BOW = ["ooo.ooo", "oRR.RRo", "oRD.DRo", ".oF.Fo."]   # 말티즈 정수리 나비 리본(가운데 세로줄은 리드줄이 매듭) + 상투


CR_LONG = {"snout": 1.45, "ear_s": 0.95, "squash": -0.2, "ears": 0.22}   # 쫑긋 귀 견종 cross 얼굴 — 길이 · 귀 배율 · 볼 · 귀 기울기
CR_BOW = ["oo...oo", "oRo.oRo", "oRRDRRo", "oDo.oDo", "oo.F.oo"]   # 말티즈 정수리 ⋈ 나비 리본(가운데 매듭은 리드줄이 지나간다) · 밑 F 가 상투


def cross() -> list[dict]:
    """앞모습 얼굴 — 코가 십자 가운데. 코 줄 양옆 긴 수염이 가로선, 머리 위 · 턱 밑 리드줄이 세로선. 눈을 깜빡인다.
    쫑긋 귀 견종은 세모 귀 + 납작한 얼굴이 고양이로 읽혀서 얼굴을 길게 뺀다 — 주둥이를 늘여 코를 주둥이 끝 쪽으로
    내리고(코가 십자 가운데라 머리가 그만큼 올라간다) 볼 폭을 줄이고, 귀는 작게 · 바깥으로 기울이고, 혀 끝을 뺀다.
    말티즈는 머리 양옆 두 덩이 리본이 고양이 귀로 읽혀서, 정수리 상투 위 작은 나비 리본(리드줄이 매듭)으로 바꾸고
    늘어진 귀를 얼굴 양옆으로 길게 내린다. head_parts · mouth 는 wait · no 와 같이 쓰므로 D 의 값을 이 칸에서만
    잠깐 바꿨다 되돌린다. 십자선은 얼굴 위에 찍어 늘 끝까지 보인다"""
    frames = []
    r = 7.0
    long_ = D["ear"] == "prick"
    malt = D["ear"] == "hair" and D.get("ribbon")
    keys = ("snout", "ear_s", "ear", "ribbon")
    saved = {key: D[key] for key in keys if key in D}
    if long_:
        D["snout"] = CR_LONG["snout"]
        D["ear_s"] = saved.get("ear_s", 1.0) * CR_LONG["ear_s"]
    if malt:
        D["ear"], D["ribbon"] = "none", False
    try:
        sn = D.get("snout", 1.0)
        rig = Rig(16.0, 15.5 - (HC[1] + r * 0.36 * sn), 0.0, 1.0)   # 코 아랫줄이 y=15, 두 칸이 x=15·16
        lines = {(x, 15): OUT for x in list(range(1, 6)) + list(range(26, 31))}
        lines.update({(15, y): LEASH_D for y in list(range(1, 6)) + list(range(26, 31))})
        for k, ph in enumerate(phases()):
            if long_:   # 밝은 주둥이를 턱 밑으로 내민다(안쪽 테를 그으면 입 둘레가 바둑판이 됐다)
                fl = CR_LONG["ears"]
                parts = [("snout", ell(HC[0], HC[1] + r * 0.42 * sn, r * 0.42, r * 0.36 * sn), D["LIGHT"], False)] + \
                    head_parts(r=r, ears=(fl, fl), squash=CR_LONG["squash"])
            else:
                parts = head_parts(r=r, swing=0.3 * math.sin(2 * ph))
            if malt:    # 얼굴 양옆으로 길게 처진 흰 귀 — 바깥 가장자리만 그늘
                sw = 0.3 * math.sin(2 * ph)
                parts = [(f"ear{i}", fluff(HC[0] + sg * r * 0.98 + sw, HC[1] + r * 0.6, r * 0.38, r * 0.96, n=6, amp=0.08,
                                           ph=1.0), (lambda s: lambda a, b: D["DARK"] if (a - HC[0]) * s > r * 1.1
                                                     else D["FUR"])(sg), True) for i, sg in enumerate((-1, 1))] + parts
            f = draw(rig, parts)
            eyes(f, rig, r=r, mood="blink" if k == 8 else "open")
            mouth(f, rig, r=r, kind="tongue" if long_ else D["mouth"], k=k)
            if malt:    # 정수리 가운데(x=15 리드줄이 매듭) 위에 리본 — 머리 꼭대기 바로 위 줄이 상투
                top = min(y for (x, y) in f if x == 15)
                col = {"o": OUT, "R": RIBBON, "D": RIBBON_D, "F": D["FUR"]}
                for j, row in enumerate(CR_BOW):
                    for i, ch in enumerate(row):
                        if ch != ".":
                            f.setdefault((12 + i, top - len(CR_BOW) + j), col[ch])
            f.update(lines)
            frames.append(finish(f))
    finally:
        for key in keys:
            D.pop(key, None)
        D.update(saved)
    return frames


IB_X, IB_TOP, IB_BOT = 11.5, 3.4, 24.6     # ibeam 뼈다귀 가운데 x · 위 · 아래 마디 가운데


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col) -> None:
    """(dx, dy) 쪽을 가리키는 화살촉. 꼭짓점이 (cx, cy)"""
    col = sea.Cur(col)   # 화살촉은 커서 — 쓸 때 sea.mark 가 파랑 맨 끝 비트로 캐릭터와 가른다
    px, py = -dy, dx
    for i in range(4):
        for s in (-1, 1):
            for w in (0, 1):
                f[cx - dx * (i + w) + s * px * i, cy - dy * (i + w) + s * py * i] = col


def move() -> list[dict]:
    """배를 깔고 동그랗게 만 댕댕이(위에서 본)가 제 꼬리를 쫓아 빙글빙글 — 꼬리 끝이 코앞에서 살랑이고,
    네 방향 화살촉이 바깥으로 두근댄다. 다리 넷 · 귀를 위에서 본 대로 다 그렸더니 칸 위에서 털 뭉치로 읽혀
    치즈냥처럼 공처럼 만 몸에 앞얼굴을 얹었다"""
    frames = []
    hc, r = (0.0, 2.4), 4.8
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy, GLOW[0])
        rig = Rig(15.5, 15.5, 360.0 * k / N, 1.0)
        sw = 0.8 * math.sin(2 * math.pi * k * 3 / N)
        if D["tail"] == "stub":
            tail = ("tail", fluff(5.6, -3.4, 1.8, 1.8, n=5, amp=0.15), D["LIGHT"], True)
        else:
            tail = ("tail", chain([(6.4, -1.0), (6.0, 4.0 + sw), (3.2 + sw, 7.2)], 1.8, 1.3),
                    lambda a, b: D["LIGHT"] if D["tail"] in ("curl", "plume") and b > 5.6 else coat(D["FUR"], a, b), True)
        ball = ("ball", fluff(0, -0.6, 7.6, 7.0, n=12, amp=0.06) if D.get("coat") in ("fluff", "curly") or D.get("big")
                else ell(0, -0.6, 7.6, 7.0), lambda a, b: coat(D["FUR"], a, b), False)
        out = draw(rig, [tail] + head_parts(hc, r) + [ball])
        eyes(out, rig, hc, r, mood="happy")
        mouth(out, rig, hc, r, kind="tongue" if k % 4 < 2 else D["mouth"], k=k)
        f.update(out)
        frames.append(finish(f))
    return frames


def stretch(ang: float, belly: int = -1) -> list[dict]:
    """쭉 기지개 — 몸은 ang 축으로 눕히고 앞발은 머리 쪽 끝, 뒷발 · 꼬리는 반대 끝으로 쭉 뻗어 늘었다 줄었다.
    양 끝 화살촉이 늘 때 바깥으로 두근대고, 늘 때 눈을 질끈 감고 입을 벌린다. 몸 가운데가 판 가운데.
    머리는 몸과 같이 돌리지 않고 늘 똑바로 세워 몸 앞(머리 쪽 끝)에 붙인다 — 치즈냥에서 돌린 얼굴은 칸 위에서 뭉개졌다"""
    frames = []
    t = math.radians(ang)
    ex, ey = math.sin(t), -math.cos(t)           # 머리 쪽 (화면)
    dx, dy = round(ex), round(ey)
    R = 13 if dx == 0 or dy == 0 else 10
    k_ = 0.68                                   # 0.8 이면 몸이 판 끝까지 닿아 양 끝 화살촉을 덮었다
    for k, ph in enumerate(phases()):
        f = {}
        s = 0.5 + 0.5 * math.sin(ph)              # 0 줄음 → 1 쭉
        for sg in (-1, 1):
            o = 1 if s > 0.6 else 0
            chevron(f, 15 + sg * dx * (R + o), 15 + sg * dy * (R + o), sg * dx, sg * dy, GLOW[0] if o else GLOW[1])
        rig = Rig(16.0 + ex * 0.4, 16.0 + ey * 0.4, ang, k_)
        reach = 1.4 * s
        b = belly
        legs = []
        for i, (sh, tip) in enumerate((((b * 3.6, -2.0), (b * 6.0, -13.6 - reach)), ((b * 1.6, -1.6), (b * 3.8, -13.0 - reach)),
                                       ((b * 2.0, 5.6), (b * 2.4, 11.4 + reach)), ((-b * 0.2, 5.8), (-b * 0.2, 10.8 + reach)))):
            legs += arm_part([sh, tip], r=1.9, pr=2.0, name=f"leg{i}", lined=True)
        body = ("body", ell(0.0, 2.0, 4.0, 5.8 + reach * 0.4),
                lambda a, bb: D["LIGHT"] if a * b > 1.6 else coat(D["FUR"], a, bb), False)
        th, tc = tail_side(D["tail"], 180.0 + b * 25.0, (-b * 1.4, 6.8 + reach * 0.3))
        out = draw(rig, legs + [body, ("tail", th, tc, False)])
        f.update(out)
        hx_, hy_ = rig.world(-b * 0.6, -5.4)
        hr = 6.4
        hrig = Rig(hx_, hy_ - (HC[1] + 0.4) * k_, 0.0, k_)
        f.update(draw(hrig, head_parts(r=hr)))
        eyes(f, hrig, r=hr, mood="squeeze" if s > 0.6 else "open")
        mouth(f, hrig, r=hr, kind="O" if s > 0.6 else D["mouth"])
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


TIP, BACK = (1.5, 28.5), (26.0, 14.3)   # pen 연필심 · 지우개 끝(화면)


def pen() -> list[dict]:
    """연필을 가로 물고 쓰는 댕댕이 — 연필이 입을 가로질러 양옆으로 나오고, 개와 연필이 연필심을 축으로 까딱인다.
    코는 연필 위에 다시 찍는다(입에 문 것으로 읽히게). 연필심이 핫스팟"""
    frames = []
    base = Rig(19.5, 21.4, 0.0, 0.78)              # 0.62 면 얼굴이 연필 · 테에 묻혔다
    L = math.hypot(BACK[0] - TIP[0], BACK[1] - TIP[1])
    ux, uy = (BACK[0] - TIP[0]) / L, (BACK[1] - TIP[1]) / L
    cone = (TIP[0] + ux * 3.6, TIP[1] + uy * 3.6)
    lt, lc, lb = base.local(*TIP), base.local(*cone), base.local(*BACK)
    rr = 1.5 / base.k

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
    for k, ph in enumerate(phases()):
        d = math.radians(3.0 * math.sin(2 * ph))
        ox, oy = base.ox - TIP[0], base.oy - TIP[1]
        rig = Rig(TIP[0] + ox * math.cos(d) - oy * math.sin(d), TIP[1] + ox * math.sin(d) + oy * math.cos(d),
                  math.degrees(d), base.k)
        f = sit(rig, k, face=False, wag=0.8)
        f.update(draw(rig, [pencil]))
        eyes(f, rig, mood="blink" if k == 4 else "open")
        mouth(f, rig, kind="none")
        f[math.floor(TIP[0]), math.floor(TIP[1])] = LEAD
        frames.append(finish(f))
    return frames


def up() -> list[dict]:
    """뒷발로 서서 두 앞발을 가슴 앞에 모으고 싹싹 — 간식 달라고 조른다. 머리는 그 자리, 몸만 들썩여서
    핫스팟(머리 꼭대기 가운데)이 장마다 같은 칸이다. 치즈냥에서 머리 위로 든 팔은 두건 · 귀로 읽혀 발을 가슴 앞에 둔다"""
    frames = []
    rig = Rig(16.0, 18.4, 0.0, 0.72)
    hc = (0.0, -7.4)
    for k, ph in enumerate(phases()):
        bob = 0.8 * abs(math.sin(ph))
        rub = 0.7 * math.sin(4 * ph)
        paws = []
        for i, sg in enumerate((-1, 1)):
            paws += arm_part([(sg * 3.6, 1.4 - bob), (sg * 1.3, -0.4 + sg * rub)], r=1.7, pr=1.8, name=f"arm{i}",
                             lined=True)
        legs = [("feet", any_of(ell(-3.4, 12.2, 2.4, 1.4), ell(3.4, 12.2, 2.4, 1.4)),
                 D["LIGHT"] if D.get("sock") else D["FUR"], True),
                ("legs", any_of(bar((-3.2, 6.0), (-3.4, 11.4), 2.2), bar((3.2, 6.0), (3.4, 11.4), 2.2)),
                 lambda a, b: coat(D["FUR"], a, b), False)]
        body = body_part((0.0, 3.4 - bob * 0.5), 6.0, 6.4 + bob * 0.4)
        tp = tail_part(D["tail"], k * 2, 1.2)
        f = draw(rig, legs + [body] + ([tp] if tp else []))
        f.update(draw(rig, head_parts(hc)))
        eyes(f, rig, hc, mood="happy" if k % 4 < 2 else "open")
        mouth(f, rig, hc, kind="pant" if k % 4 < 2 else "tongue", k=k)
        f.update(draw(rig, paws))
        if k % 4 < 2:   # 싹싹 — 발 옆 움직임 줄
            for sg in (-1, 1):
                x0, y0 = rig.cell(sg * 4.6, -1.0)
                for p in ((x0, y0), (x0 + sg, y0 + 1)):
                    f.setdefault(p, MARK_L)
        for x in range(9, 24):   # 바닥 그림자
            f.setdefault((x, 29), GLOW[2])
        frames.append(finish(f))
    return frames


def head_top(fr):
    """머리 꼭대기 가운데 — 판 가운데 줄(x=15)에서 맨 위 불투명 칸"""
    return min((p for p, c in fr[0].items() if c[3] == 255 and p[0] == 15), key=lambda p: p[1])


def ib_bone(x: float, top: float, bot: float) -> dict:
    return draw(Rig(x, (top + bot) / 2, 90.0, 1.0), bone_parts((bot - top) / 2, 1.1, 1.6))


def ib_snug(f: dict, bone: dict, rows: range, gap: int = 1) -> int:
    """개를 I 쪽으로 옮길 칸 수 — rows 줄에서 개 왼 끝이 I 오른 끝 + gap 에 오게(닿게)"""
    right = max(x for (x, y) in bone if y in rows)
    left = min((x for (x, y) in f if y in rows), default=right + gap)
    return right + gap - left


def ib_finish(f: dict, bone: dict, dx: int = 0) -> dict:
    f = {(x + dx, y): c for (x, y), c in f.items()}
    f = {p: c for p, c in clip(f).items() if p not in bone}
    f.update(bone)
    return finish(f)


def ibeam_lean() -> list[dict]:
    """A 기대기 — I 오른쪽에 앉아 옆구리 · 어깨를 I 에 기대고(몸째 I 쪽으로 기울임) 고개를 I 쪽으로 갸웃.
    앞발은 둘 다 바닥, 꼬리는 한 바퀴에 세 번 붕붕"""
    bone = ib_bone(IB_X, IB_TOP, IB_BOT)
    rig = Rig(20.0, 21.0, -8.0, 0.74)
    frames, dx = [], None
    for k, ph in enumerate(phases()):
        f = sit(rig, (k * 3) % N, tilt=-12.0 + 2.0 * math.sin(2 * ph), wag=2.4, swing=0.4 * math.sin(2 * ph),
                mood="blink" if k == 8 else "happy" if k in (4, 5) else "open")
        if dx is None:   # 첫 장으로 한 번 재서 모든 장에 같은 만큼 — 장마다 재면 몸이 들썩인다
            dx = ib_snug(f, bone, range(12, 26))
        frames.append(ib_finish(f, bone, dx))
    return frames


# ibeam 은 앞발로 I 를 짚던 판이 "개가 왜 팔을 드냐"로 접혀, 셋(기대기 · 엎드리기 · 코 위에 세우기) 중 기대기를 골랐다(2026-10-10)
SCENE = {"busy": busy, "help": help_, "person": person, "pin": pin, "hand": hand, "cross": cross, "ibeam": ibeam_lean,
         "move": move, "ns": ns, "we": we, "nwse": nwse, "nesw": nesw, "pen": pen, "up": up}


HOT = {"busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1), "hand": hand_hot, "cross": (15, 15),
       "ibeam": (math.floor(IB_X), round((IB_TOP + IB_BOT) / 2)), "move": (15, 15), "ns": (15, 15), "we": (15, 15), "nwse": (15, 15),
       "nesw": (15, 15), "pen": (math.floor(TIP[0]), math.floor(TIP[1])), "up": head_top}


WAIT = {"shiba": w_shiba, "corgi": w_corgi, "pomeranian": w_pomeranian, "bichon": w_bichon, "retriever": w_retriever,
        "dachshund": w_dachshund, "husky": w_husky, "poodle": w_poodle, "maltese": w_maltese, "jindo": w_jindo}
NO = {"shiba": n_shiba, "corgi": n_corgi, "pomeranian": n_pomeranian, "bichon": n_bichon, "retriever": n_retriever,
      "dachshund": n_dachshund, "husky": n_husky, "poodle": n_poodle, "maltese": n_maltese, "jindo": n_jindo}


def check(rid: str, frames: list[dict], hot: tuple) -> None:
    """핫스팟이 장마다 불투명한 칸 위에 있는지 · 판(0–31) 안인지 · 예약 알파를 안 썼는지"""
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
        if any(not (0 <= x <= 31 and 0 <= y <= 31) for x, y in f):
            print(f"  ! {rid} {i}장: 판 밖으로 나간 칸이 있음")
        if any(c[3] in (0xfc, 0xfd, 0xfe) for c in f.values()):
            print(f"  ! {rid} {i}장: 예약 알파(fc–fe)를 씀")
        if hot == (1, 1) and any(c[3] == 255 and (p[0] < 1 or p[1] < 1) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 화살표 끝보다 왼쪽·위로 나온 칸이 있음")


def solid_hot(frames, want):
    """want 가 장마다 불투명하면 그대로, 아니면 장마다 불투명한 칸 중 가장 가까운 것"""
    ok = [p for p in frames[0] if all(f.get(p, (0, 0, 0, 0))[3] == 255 for f in frames)]
    if want in ok:
        return want
    best = min(ok, key=lambda p: (abs(p[0] - want[0]) + abs(p[1] - want[1]), p))
    print(f"  · 핫스팟 {want} → {best}")
    return best


def one(d: dict, cells=None) -> None:
    """한 마리 칸을 쓴다(cells 를 안 주면 16칸 전부) — 마리끼리 안 보므로 프로세스로 나눠 돈다"""
    use(d)
    out = ART / f"{d['id']}anim"
    out.mkdir(parents=True, exist_ok=True)
    for cell, fn, want in (("wait", WAIT[d["id"]], (16, 16)), ("no", NO[d["id"]], (15, 15))):
        if cells and cell not in cells:
            continue
        frames = fn()
        hot = solid_hot(frames, want)
        check(f"{d['id']}/{cell}", frames, hot)
        # 칸마다(커서 없는 칸도) mark — 안 거친 칸의 홀수 파랑은 커서로 읽힌다
        (out / f"{cell}.txt").write_text(shape.to_text(sea.mark(frames), hot, RATE), encoding="utf-8")
    for cell, fn in SCENE.items():
        if cells and cell not in cells:
            continue
        frames = fn()
        hot = HOT[cell](frames) if callable(HOT[cell]) else HOT[cell]
        check(f"{d['id']}/{cell}", frames, hot)
        (out / f"{cell}.txt").write_text(shape.to_text(sea.mark(frames), hot, RATE), encoding="utf-8")
    print(f"{d['id']}: 끝", flush=True)


def main() -> None:
    """python gen/dog.py [견종...] [--cells busy,help]"""
    from concurrent.futures import ProcessPoolExecutor
    from functools import partial
    args = sys.argv[1:]
    cells = None
    if "--cells" in args:
        i = args.index("--cells")
        cells = args[i + 1].split(",")
        del args[i:i + 2]
    only = args
    with ProcessPoolExecutor() as ex:
        list(ex.map(partial(one, cells=cells), [d for d in DOGS if not only or d["id"] in only]))


if __name__ == "__main__":
    main()

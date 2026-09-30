# SPDX-License-Identifier: Apache-2.0
"""해양 애니 생성기(`gen/bukang.py`·`gen/dolphin.py` …)가 같이 쓰는 도구. 혼자서는 아무것도 안 그린다.

장면은 칸 좌표 → 색 사전(`{(x, y): (r, g, b, a)}`) 한 장이 한 프레임이다. 다각형을 4×4 로 찍어 반 넘게 덮인
칸을 칠하고(`raster`), 테두리 · 반투명 테(`finish`)를 두른다. 옆모습 몸은 `side` 가 동물마다의 `Body` 로 그린다.
그리는 도구만 여기 두고 장면(무엇을 그릴지)은 동물마다 따로 짠다 — 장면까지 같이 쓰면 구성표끼리 복제품이 된다.
"""
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

WIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WIN))
import shape as S   # noqa: E402

N, RATE = 12, 5          # 12장 × rate 5 = 1초에 꼬리 한 번. 해양 애니 전부 같은 박자다
ROLES = ("arrow", "busy", "cross", "hand", "help", "ibeam", "move", "nesw", "no", "ns",
         "nwse", "pen", "person", "pin", "up", "wait", "we")


def hx(s: str) -> tuple:
    return tuple(bytes.fromhex(s))


RIM = hx("d2dde6c7")                          # 해양 애니 전부 같은 반투명 테
WAKE = (hx("e8fcffff"), hx("7cc4d8ff"), hx("7cc4d8b0"), hx("7cc4d870"), hx("7cc4d838"))   # 물 · 물살. 짙은 것부터
BUB = hx("3f8faeff")                          # 물방울 테
SIGN, SIGN_D = hx("d64541ff"), hx("9e2b28ff")  # 빨강 (금지 표지 · 핀 · 조준점)

# 동물마다 다른 테두리색과 흰 반짝. 한 프로세스가 한 동물만 그리므로 동물 모듈이 불러올 때 한 번 정한다(`ink`)
INK = {"out": hx("000000ff"), "hi": hx("ffffffff")}


def ink(out: tuple, hi: tuple) -> None:
    INK["out"], INK["hi"] = out, hi


def phases():
    return [2 * math.pi * k / N for k in range(N)]


def lerp_profile(pts, s):
    for (s0, v0), (s1, v1) in zip(pts, pts[1:]):
        if s0 <= s <= s1:
            return v0 + (v1 - v0) * (s - s0) / (s1 - s0)
    return pts[-1][1] if s > pts[-1][0] else pts[0][1]


def inside(poly, x, y) -> bool:
    c = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def raster(poly, thr: int = 8) -> set:
    xs, ys = [x for x, _ in poly], [y for _, y in poly]
    cells = set()
    for y in range(max(-2, math.floor(min(ys))), min(34, math.ceil(max(ys)) + 1)):
        for x in range(max(-2, math.floor(min(xs))), min(34, math.ceil(max(xs)) + 1)):
            if sum(inside(poly, x + (i + 0.5) / 4, y + (j + 0.5) / 4) for i in range(4) for j in range(4)) >= thr:
                cells.add((x, y))
    return cells


def disc(cx: float, cy: float, r: float) -> set:
    return {(x, y) for y in range(math.floor(cy - r) - 1, math.ceil(cy + r) + 1)
            for x in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 1) if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= r}


def edge(mask: set, p) -> bool:
    x, y = p
    return any(q not in mask for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))


def solid(f: dict, mask: set, fill, line=None) -> None:
    """mask 를 테두리 line · 속 fill 로 칠한다. fill 은 색이나 (칸 → 색) 함수"""
    line = line or INK["out"]
    for p in mask:
        f[p] = line if edge(mask, p) else fill(p) if callable(fill) else fill


def rim(frame: dict, mask: set) -> dict:
    f = dict(frame)
    for x, y in mask:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                q = (x + dx, y + dy)
                if q not in mask and q not in f:
                    f[q] = RIM
    return f


def finish(f: dict) -> dict:
    """불투명한 칸 전부에 반투명 테 — 물·물방울처럼 반투명한 것은 테를 안 두른다"""
    return rim(f, {p for p, c in f.items() if c[3] == 255})


# ── 옆모습 몸: 주둥이 s=0 → 꼬리 끝 s=1, v 는 등 쪽이 + (몸길이 단위) ─────────────────────
def straight(head, tail, size, flip=False):
    """머리 칸 → 꼬리 칸으로 뻗은 몸의 (local, world, L) — 칸 좌표 ↔ (s, v) 몸길이 단위, L 은 몸길이(칸)"""
    hx_, hy = head[0] + 0.5, head[1] + 0.5
    tx, ty = tail[0] + 0.5, tail[1] + 0.5
    D = math.hypot(tx - hx_, ty - hy)
    ux, uy = (tx - hx_) / D, (ty - hy) / D
    L = D * size
    cands = [(uy, -ux), (-uy, ux)]
    nx, ny = min(cands, key=lambda n: (round(n[1], 6), -n[0]))   # 등은 위(세로면 오른쪽)
    if flip:
        nx, ny = -nx, -ny

    def local(px, py):
        dx, dy = px - hx_, py - hy
        return (dx * ux + dy * uy) / L, (dx * nx + dy * ny) / L

    def world(s, v):
        return hx_ + (s * ux + v * nx) * L, hy + (s * uy + v * ny) * L
    return local, world, L


@dataclass
class Body:
    """옆모습 동물 한 종. 윤곽(top·bot)과 지느러미는 (s, v) 꼭짓점이고 두께는 thick 배로 부풀려 그린다
    (실제 비율로 그리면 몸이 3칸이라 테두리가 속을 다 먹는다)"""
    top: list
    bot: list
    fins: dict                      # 이름: 꼭짓점들. order 에서 앞의 것이 위에 그려진다
    order: tuple                    # "body" 를 포함한 그리는 순서
    skin: Callable                  # (s, v, top, bot) → 몸 칸 색. v 는 두께를 뺀 값
    fin_ink: Callable               # (이름, s, v) → 지느러미 칸 색
    bend: Callable                  # (s, v, ph) → 꼬리를 저은 (s, v). 몸 전체에 쓴다
    unbend: Callable                # bend 의 역
    decorate: Callable              # (ctx) → 눈·입·무늬를 out 에 덧칠한다
    thick: float = 1.6
    length: float = 1.05            # 몸길이 = 머리→꼬리 거리의 몇 배 (기본값)
    small: tuple = ()               # detail 을 끄면 빼는 자잘한 지느러미
    extra: Callable = None          # (m) → {이름: (꼭짓점들, 색)} — 벌린 턱처럼 자세마다 붙는 조각. body 바로 뒤에 그린다
    lined: tuple = ()               # 몸 앞에 있어 몸과 닿는 자리에도 테두리를 긋는 지느러미


def side(b: Body, head, tail, ph, size=None, m=0.0, flip=False, detail=True):
    """자세 하나 × 위상 하나 → ({좌표: 색}, 몸 칸 집합). 몸 칸은 테를 두르기 전 불투명한 칸.
    m 은 입을 벌린 정도(0–1), flip 은 등을 반대쪽으로. detail 을 끄면 small 지느러미를 빼고 몸을 12% 굵힌다 —
    줄여 그리거나 세로로 선 좁은 몸에서 자잘한 것이 가시·갈비뼈로 읽혀 생선 뼈가 된다"""
    local, world, L = straight(head, tail, size or b.length, flip)
    T = b.thick * (1.0 if detail else 1.12)
    body_pts = [(s, lerp_profile(b.top, s)) for s in [i / 40 * b.top[-1][0] for i in range(41)]] + \
               [(s, lerp_profile(b.bot, s)) for s in reversed([i / 40 * b.bot[-1][0] for i in range(41)])]

    def bent(pts):
        out = []
        for s, v in pts:
            s2, v2 = b.bend(s, v, ph)
            out.append((s2, v2 * T))
        return out
    parts = {"body": bent(body_pts)}
    for name, pts in b.fins.items():
        parts[name] = bent(pts)
    order = b.order
    if not detail:
        order = tuple(n for n in order if n not in b.small)
    extra_ink = {}
    if m > 0 and b.extra:
        for name, (pts, col) in b.extra(m).items():
            parts[name] = [(s, v * T) for s, v in pts]
            extra_ink[name] = col
        i = order.index("body") + 1
        order = order[:i] + tuple(extra_ink) + order[i:]

    SUB = 4
    region, mask = {}, set()
    for y in range(-2, 34):
        for x in range(-2, 34):
            hits = {}
            for j in range(SUB):
                for i in range(SUB):
                    s, v = local(x + (i + 0.5) / SUB, y + (j + 0.5) / SUB)
                    if not (-0.05 < s < 1.08 and abs(v) < 0.6):
                        continue
                    for name in order:
                        if inside(parts[name], s, v):
                            hits[name] = hits.get(name, 0) + 1
                            break
            n = sum(hits.values())
            if n * 2 >= SUB * SUB:
                mask.add((x, y))
                # 몸과 지느러미가 반반이면 몸으로 — 밑동이 몸 색으로 이어져야 지느러미가 붙어 보인다
                front = sum(hits.get(q, 0) for q in b.lined)
                region[x, y] = "body" if hits.get("body", 0) * 3 >= n and front * 2 < n \
                    else max(hits, key=hits.get)
    mask.add(head)
    region.setdefault(head, "body")

    out = {}
    for p in mask:
        s, v = local(p[0] + 0.5, p[1] + 0.5)
        s, v = b.unbend(s, v / T, ph)
        r = region[p]
        if r in extra_ink:
            out[p] = extra_ink[r]
        elif r != "body":
            out[p] = b.fin_ink(r, s, v)
        else:
            out[p] = b.skin(s, v, lerp_profile(b.top, s), lerp_profile(b.bot, s))
    # 테두리: 몸 칸 중 네 이웃에 빈 칸이 있는 것. 몸 앞의 지느러미(lined)는 몸과 닿는 자리에도 선을 긋는다
    OUT = INK["out"]
    for p in mask:
        x, y = p
        nb = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        if any(q not in mask for q in nb):
            out[p] = OUT
        elif region[p] in b.lined and any(region.get(q) == "body" for q in nb):
            out[p] = OUT

    def at(s, v):
        s2, v2 = b.bend(s, v, ph)
        wx, wy = world(s2, v2 * T)
        return math.floor(wx), math.floor(wy)

    def paint(p, c):
        if p in mask and out[p] != OUT and region[p] == "body":
            out[p] = c

    def sv(p):   # 칸 → 곧게 편 몸의 (s, v)
        s, v = local(p[0] + 0.5, p[1] + 0.5)
        return b.unbend(s, v / T, ph)
    b.decorate(Ctx(out, mask, region, local, at, paint, sv, L, T, m, detail, ph))
    return out, mask


@dataclass
class Ctx:
    """decorate 가 받는 것 — 그린 몸과 좌표 변환"""
    out: dict
    mask: set
    region: dict
    local: Callable
    at: Callable        # (s, v) → 칸 (꼬리를 저은 자세 그대로)
    paint: Callable     # (칸, 색) → 몸 칸이고 테두리가 아니면 칠한다
    sv: Callable        # 칸 → (s, v)
    L: float
    T: float
    m: float
    detail: bool
    ph: float


# ── 소품 ─────────────────────────────────────────────────────────────────────
def fin_poly(w: float, h: float) -> list:
    """앞(+x)으로 헤엄치는 등지느러미. 밑동 (0,0) 가운데, 위가 -y. 앞날은 볼록하게, 뒷날은 오목하게"""
    return [(w / 2, 0), (w * 0.22, -h * 0.5), (-w * 0.08, -h * 0.85), (-w * 0.38, -h), (-w * 0.3, -h * 0.6),
            (-w * 0.36, -h * 0.25), (-w / 2, 0)]


def bubble(f: dict, cx: float, cy: float, r: float) -> None:
    """물방울: 파란 테 · 옅은 속 · 왼쪽 위 흰 반짝"""
    solid(f, disc(cx, cy, r), WAKE[0], BUB)
    if r >= 2:
        f[math.floor(cx - r * 0.45), math.floor(cy - r * 0.45)] = INK["hi"]


def splash(f: dict, x0: float, y0: float, k: int, n: int = 4, spread: float = 5.0, height: float = 5.0) -> None:
    """물 튀김: 물방울 n 개가 x0 에서 좌우로 포물선을 그리며 떨어진다"""
    for j in range(n):
        t = (k / N + j / n) % 1
        side_ = -1 if j % 2 else 1
        x = x0 + side_ * spread * t * (0.6 + 0.4 * (j // 2))
        y = y0 - height * 4 * t * (1 - t)
        f[math.floor(x), math.floor(y)] = WAKE[0] if t < 0.5 else WAKE[1]


def water(f: dict, x0: int, x1: int, y: int, k: int) -> None:
    for x in range(x0, x1 + 1):
        f[x, y] = WAKE[1]
        f[x, y + 1] = WAKE[3] if (x + k) % 3 else WAKE[2]


def glyph(f: dict, rows: list, x0: int, y0: int, col: tuple) -> None:
    """'#' 자리만 칠하는 작은 글자판"""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "#":
                f[x0 + i, y0 + j] = col


QMARK = [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."]


def write(sid: str, table: dict, roles=None) -> None:
    """table: 역할 → () → (프레임들, 핫스팟). roles 를 안 주면 table 전부"""
    roles = roles or list(table)
    d = WIN / "art" / sid
    d.mkdir(parents=True, exist_ok=True)
    for rid in roles:
        frames, hot = table[rid]()
        (d / f"{rid}.txt").write_text(S.to_text(frames, hot, RATE), encoding="utf-8")
        print(f"{rid}: {len(frames)}장")

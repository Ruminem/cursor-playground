# SPDX-License-Identifier: Apache-2.0
"""부캉이(bukanganim) 구성표 그림 `art/bukanganim/*.txt` 를 만든다. 빌드가 부르지 않고 그림을 다시 뽑을 때 손으로 돌린다.

  python3 gen/bukang.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

부캉이는 2026-09-18 부산 북항 친수공원 수로에 들어와 열이틀 머문 상어의 별명이다. 국립수산과학원 추정으로
무태상어(흉상어과) 암컷 약 3m — 무늬 없는 회청색 등, 흰 배, 세모 등지느러미, 위 날개가 긴 꼬리.
동구청이 공식 캐릭터를 따로 공모하고 있으므로 그것을 닮게 그리지 않고 그냥 상어를 그린다.

옆모습 몸은 거리 단위 다각형으로 그린다. 첫 벌은 돌고래 몸을 조금 고친 꼴이라 돌고래로 읽혀서 상어만의 것을
따로 세웠다 — 입 위로 튀어나온 원뿔 주둥이 · 앞으로 쏠린 세모 등지느러미 · 긴 낫 모양 가슴지느러미 ·
윗날개가 긴 꼬리 · 아가미구멍 셋 · 거뭇한 지느러미 끝. 꼬리도 돌고래처럼 위아래로 까딱이지 않고 옆으로 저으니
옆에서 보면 꼬리가 줄었다 늘었다 한다(`sweep`). 입은 크게 벌려 검붉은 속과 흰 이빨 줄을 보인다(`MOUTH`).
둘째 벌은 같은 상어를 방향만 돌려 칸마다 놓아서 복제품 같다는 말을 들었다. 그래서 화살표 상어만 기준으로 두고
나머지 칸은 그 칸의 뜻에 맞는 장면을 따로 그린다(`SCENE`) — 물음표 물방울 · 작은 웅덩이를 도는 지느러미 ·
잠수부 · 지도 핀 · 물고기를 쫓는 상어(좌우) · 엇갈리는 두 상어(위아래) · 비스듬히 뛰어오르기와 잠수(대각선) ·
솟구치기(위) · 톱니 이빨 펜 · 앞에서 본 얼굴(손) · 조준경(십자) · 위아래 턱 I빔.
wait 는 `keep` 이라 11모양 전부에 그대로 실리므로 따로 그린다 — 물 위로 등지느러미만 내놓고 수로를 빙빙 도는
모습(`circle`). 원호로 휜 몸을 먼저 그려 봤는데 32칸에서 지느러미가 뭉개져 버렸다. move 는 위에서 본 상어(`top`),
no 는 빨간 금지 표지 안에서 등지느러미가 솟았다 가라앉는 그림(`sign`)이다.
12장 × rate 5 = 1초에 꼬리 한 번. 다른 해양 애니와 같은 박자다.
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys
from pathlib import Path

WIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WIN))
import shape as S   # noqa: E402

SID = "bukanganim"
N, RATE = 12, 5
THICK = 1.6               # 두께 배율. 실제 비율(1)로 그리면 몸이 3칸이라 테두리가 속을 다 먹는다
LEN = 1.05                # 몸길이 = 머리→꼬리 거리의 몇 배 (기본값)
ROLES = ("arrow", "busy", "cross", "hand", "help", "ibeam", "move", "nesw", "no", "ns",
         "nwse", "pen", "person", "pin", "up", "wait", "we")
ARROW = ((1, 2), (15, 21))   # 화살표 상어의 머리 끝(핫스팟) · 꼬리 끝


def hx(s: str) -> tuple:
    return tuple(bytes.fromhex(s))


OUT, DARK, MID, LIGHT = hx("1b2227ff"), hx("3d4a52ff"), hx("5b6b74ff"), hx("7e8f98ff")
BELLY, SHADE = hx("eef2f3ff"), hx("c3ccd1ff")
GULLET = hx("7a2430ff")                       # 벌린 입 속
RIM = hx("d2dde6c7")                          # 돌고래 애니와 같은 반투명 테


# ── 옆모습 상어: 주둥이 s=0 → 꼬리 끝 s=1, v 는 등 쪽이 + (몸길이 단위) ─────────────────────
def lerp_profile(pts, s):
    for (s0, v0), (s1, v1) in zip(pts, pts[1:]):
        if s0 <= s <= s1:
            return v0 + (v1 - v0) * (s - s0) / (s1 - s0)
    return pts[-1][1] if s > pts[-1][0] else pts[0][1]


# 원뿔 주둥이가 입 위로 튀어나오고(아래 윤곽이 늦게 내려감), 몸이 가장 두꺼운 자리가 앞 1/3 이다.
# 돌고래와 가르는 것: 앞으로 쏠린 높은 세모 등지느러미 · 길고 낫 모양인 가슴지느러미 · 윗날개가 긴 비대칭 꼬리 ·
# 가는 꼬리자루 · 작은 둘째 등지느러미·뒷지느러미 · 아가미구멍 줄. 지느러미 끝은 거뭇하다(무태상어 dusky)
TOP = [(0, 0), (0.03, 0.022), (0.08, 0.048), (0.15, 0.068), (0.25, 0.085), (0.3, 0.088), (0.45, 0.075),
       (0.58, 0.05), (0.68, 0.028), (0.74, 0.02), (0.78, 0.02)]
BOT = [(0, 0), (0.03, -0.012), (0.08, -0.035), (0.15, -0.06), (0.28, -0.08), (0.42, -0.075), (0.55, -0.05),
       (0.66, -0.028), (0.74, -0.018), (0.78, -0.018)]
FINS = {   # 이름: 꼭짓점들 (s, v). 1칸짜리 선이 되지 않게 밑동을 넓게 잡는다. 앞의 것이 위에 그려진다
    "pectoral": [(0.19, -0.03), (0.25, -0.1), (0.33, -0.18), (0.37, -0.21), (0.35, -0.16), (0.30, -0.09),
                 (0.28, -0.05), (0.27, -0.03)],
    "dorsal": [(0.24, 0.07), (0.3, 0.15), (0.35, 0.2), (0.38, 0.205), (0.385, 0.16), (0.40, 0.115),
               (0.44, 0.08), (0.42, 0.07)],
    "pelvic": [(0.53, -0.045), (0.58, -0.09), (0.61, -0.088), (0.60, -0.04)],
    "dorsal2": [(0.63, 0.04), (0.67, 0.08), (0.695, 0.078), (0.69, 0.03)],
    "anal": [(0.655, -0.03), (0.695, -0.065), (0.71, -0.025)],
    "caudal": [(0.74, 0.018), (0.85, 0.08), (0.95, 0.15), (1.0, 0.17), (0.985, 0.12), (0.95, 0.07),
               (0.93, 0.03), (0.915, 0.005), (0.935, -0.075), (0.905, -0.11), (0.84, -0.06), (0.74, -0.018)],
}
TIPS = {   # 지느러미 끝(거뭇한 자리): 이 선 너머면 DARK
    "dorsal": lambda s, v: v > 0.155, "pectoral": lambda s, v: v < -0.15,
    "caudal": lambda s, v: v > 0.13 or v < -0.085,
}
JAW = lambda m: [(0.03, -0.02), (0.25, -0.07), (0.13, -0.05 - 0.1 * m), (0.03, -0.025 - 0.11 * m)]   # 벌어진 아래턱 — 32칸에서 입이 보이려면 만화처럼 크게
MOUTH = lambda m: [(0.0, 0.0), (0.24, -0.05), (0.04, -0.01 - 0.12 * m)]   # 입 쐐기: 윗잇몸 두 점 + 아래턱 끝
PIVOT = 0.62              # 꼬리를 좌우로 저을 때 접히는 자리 (꼬리자루 앞)


def body_poly():
    ss = [i / 40 * 0.78 for i in range(41)]
    return [(s, lerp_profile(TOP, s)) for s in ss] + [(s, lerp_profile(BOT, s)) for s in reversed(ss)]


def sweep(ph: float) -> float:
    """꼬리를 옆으로 젓는 상어를 옆에서 보면 꼬리가 앞뒤로 줄었다 늘었다 한다 — PIVOT 뒤의 길이 배율.
    돌고래처럼 위아래로 까딱이면 상어가 아니다"""
    return 0.82 + 0.18 * math.cos(ph)


def fold(s: float, k: float) -> float:
    return s if s <= PIVOT else PIVOT + (s - PIVOT) * k


def unfold(s: float, k: float) -> float:
    return s if s <= PIVOT else PIVOT + (s - PIVOT) / k


def inside(poly, x, y) -> bool:
    c = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def straight(head, tail, size=None, flip=False):
    """머리 칸 → 꼬리 칸으로 뻗은 몸의 (local, world, L) — 칸 좌표 ↔ (s, v) 몸길이 단위, L 은 몸길이(칸)"""
    hx_, hy = head[0] + 0.5, head[1] + 0.5
    tx, ty = tail[0] + 0.5, tail[1] + 0.5
    D = math.hypot(tx - hx_, ty - hy)
    ux, uy = (tx - hx_) / D, (ty - hy) / D
    L = D * (size or LEN)
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


def shark(head, tail, ph, size=None, m=0.0, flip=False):
    """자세 하나 × 위상 하나 → ({좌표: 색}, 몸 칸 집합). 몸 칸은 테를 두르기 전 불투명한 칸.
    m 은 입을 벌린 정도(0–1) — 아래턱이 내려가고 윗잇몸에 흰 이빨 줄이 보인다. flip 은 등을 반대쪽으로"""
    local, world, L = straight(head, tail, size, flip)
    k = sweep(ph)
    parts = {"body": [(fold(s, k), v * THICK) for s, v in body_poly()]}
    for name, pts in FINS.items():
        parts[name] = [(fold(s, k), v * THICK) for s, v in pts]
    order = ("pectoral", "body", "dorsal", "pelvic", "dorsal2", "anal", "caudal")
    if m > 0:
        parts["jaw"] = [(s, v * THICK) for s, v in JAW(m)]
        order = ("pectoral", "body", "jaw") + order[2:]

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
                region[x, y] = "body" if hits.get("body", 0) * 3 >= n and hits.get("pectoral", 0) * 2 < n \
                    else max(hits, key=hits.get)
    mask.add(head)
    region.setdefault(head, "body")

    out = {}
    for p in mask:
        s, v = local(p[0] + 0.5, p[1] + 0.5)
        s, v = unfold(s, k), v / THICK
        r = region[p]
        if r == "jaw":
            out[p] = SHADE
            continue
        if r != "body":
            out[p] = DARK if r in TIPS and TIPS[r](s, v) else MID
            continue
        # 등은 짙게, 옆구리는 밝게, 배는 희게 — 옆구리와 배 사이 경계를 또렷하게 (상어의 역그늘)
        top, bot = lerp_profile(TOP, s), lerp_profile(BOT, s)
        sep = bot + 0.45 * (top - bot)
        if v > sep + 0.5 * (top - sep):
            out[p] = MID
        elif v > sep:
            out[p] = LIGHT
        elif v < bot + 0.3 * (sep - bot):
            out[p] = SHADE
        else:
            out[p] = BELLY
    # 테두리: 몸 칸 중 네 이웃에 빈 칸이 있는 것. 가슴지느러미는 몸 앞에 있으니 몸과 닿는 자리에도 선을 긋는다
    for p in mask:
        x, y = p
        nb = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        if any(q not in mask for q in nb):
            out[p] = OUT
        elif region[p] == "pectoral" and any(region.get(q) == "body" for q in nb):
            out[p] = OUT

    def at(s, v):
        wx, wy = world(fold(s, k), v * THICK)
        return math.floor(wx), math.floor(wy)

    def paint(p, c):
        if p in mask and out[p] != OUT and region[p] == "body":
            out[p] = c

    # 눈: 주둥이 끝에서 조금 뒤, 등 쪽. 입: 주둥이 아래로 비스듬한 선 한 줄
    e = at(0.085, 0.02)
    if e in mask:
        out[e] = OUT
    if m > 0:
        # 벌린 입: 속은 검붉게, 윗잇몸과 아래턱을 따라 흰 이빨(한 칸 건너 한 칸 — 톱니로 읽힌다).
        # 속을 테두리색으로 칠하면 입이 윤곽선에 묻혀 안 보인다
        wedge = MOUTH(m)
        (s0, v0), (s1, v1), (s2, v2) = wedge
        for p in mask:
            if edge(mask, p):
                continue
            s, v = local(p[0] + 0.5, p[1] + 0.5)
            v /= THICK
            if not inside(wedge, s, v):
                continue
            gum = v0 + (v1 - v0) * (s - s0) / (s1 - s0)
            low = v2 + (v1 - v2) * (s - s2) / (s1 - s2) if s >= s2 else v2
            tooth = math.floor(s * L) % 2 == 0
            near = min(gum - v, v - low) * L * THICK < 1.1
            out[p] = BELLY if near and tooth else GULLET
    else:
        for s in (0.07, 0.1, 0.13):
            paint(at(s, lerp_profile(BOT, s) * 0.45 - 0.004), DARK)
    # 아가미구멍 셋 — 2칸 간격 세로줄
    for i in range(3):
        gs = 0.17 + i * 2 / L
        for v in (-0.03, -0.01, 0.01, 0.03):
            paint(at(gs, v), DARK)
    return out, mask


def rim(frame: dict, mask: set) -> dict:
    f = dict(frame)
    for x, y in mask:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                q = (x + dx, y + dy)
                if q not in mask and q not in f:
                    f[q] = RIM
    return f


# wait: 물 위로 등지느러미만 내놓고 수로를 빙빙 도는 부캉이. 물낯을 비스듬히 본 타원을 돌며 물살 꼬리를 남긴다
POND = (16.0, 18.0, 11.0, 5.0)   # 타원 가운데 x, y · 가로 반지름 · 세로 반지름
WAKE = (hx("e8fcffff"), hx("7cc4d8ff"), hx("7cc4d8b0"), hx("7cc4d870"), hx("7cc4d838"))   # 지느러미에 가까운 것부터


def fin_poly(w: float, h: float) -> list:
    """앞(+x)으로 헤엄치는 등지느러미. 밑동 (0,0) 가운데, 위가 -y. 앞날은 볼록하게, 뒷날은 오목하게"""
    return [(w / 2, 0), (w * 0.22, -h * 0.5), (-w * 0.08, -h * 0.85), (-w * 0.38, -h), (-w * 0.3, -h * 0.6),
            (-w * 0.36, -h * 0.25), (-w / 2, 0)]


def circle() -> tuple[list[dict], tuple[int, int]]:
    """12장에 한 바퀴(시계 방향). 가까운 쪽(아래)을 지날 때 지느러미가 크고 먼 쪽(위)에서 작다. 핫스팟은 타원 가운데"""
    return [orbit(k, POND)[0] for k in range(N)], (int(POND[0]), int(POND[1]))


# move: 위에서 본 부캉이. 머리가 위, 꼬리가 몸을 옆으로 S 자로 저으며 헤엄친다(옆모습에서 꼬리가 줄었다 늘었다 한 것과 같은 동작)
TOP_W = [(0, 0), (0.04, 0.035), (0.1, 0.07), (0.2, 0.09), (0.3, 0.092), (0.45, 0.075), (0.6, 0.05),
         (0.72, 0.03), (0.8, 0.022)]   # 몸 반폭 (몸길이 단위) — 앞 1/3 이 가장 넓은 어뢰꼴
TOP_FINS = {   # (옆으로 a, 뒤로 t) 오른쪽 것. 왼쪽은 거울로
    "pectoral": [(0.07, 0.2), (0.2, 0.3), (0.26, 0.37), (0.21, 0.36), (0.13, 0.33), (0.07, 0.32)],
    "pelvic": [(0.04, 0.55), (0.1, 0.61), (0.09, 0.63), (0.03, 0.62)],
}
TAIL = [(-0.025, 0.78), (0.025, 0.78), (0.035, 0.9), (0.015, 1.0), (-0.015, 1.0), (-0.035, 0.9)]   # 꼬리는 위에서 보면 칼날
MOVE = (15.5, 1.0, 29.0)   # 가운뎃줄 x · 주둥이 y · 몸길이(칸)


def top(ph: float) -> tuple[dict, set]:
    cx, y0, L = MOVE

    def c(t):   # 가운뎃줄이 옆으로 밀린 정도. 머리 쪽은 가만히
        u = max(0.0, (t - 0.3) / 0.7)
        return 0.07 * u ** 1.5 * math.sin(ph - 5.0 * (t - 0.3))

    def w(a, t):
        return cx + (c(t) + a) * L, y0 + t * L
    ts = [i / 40 * 0.8 for i in range(41)]
    parts = {"body": [w(lerp_profile(TOP_W, t), t) for t in ts] + [w(-lerp_profile(TOP_W, t), t) for t in reversed(ts)],
             "tail": [w(a, t) for a, t in TAIL]}
    for name, pts in TOP_FINS.items():
        parts[name + "R"] = [w(a, t) for a, t in pts]
        parts[name + "L"] = [w(-a, t) for a, t in reversed(pts)]
    region, mask = {}, set()
    for y in range(32):
        for x in range(32):
            hits = {}
            for j in range(4):
                for i in range(4):
                    px, py = x + (i + 0.5) / 4, y + (j + 0.5) / 4
                    for name, poly in parts.items():
                        if inside(poly, px, py):
                            hits[name] = hits.get(name, 0) + 1
                            break
            n = sum(hits.values())
            if n * 2 >= 16:
                mask.add((x, y))
                region[x, y] = "body" if hits.get("body", 0) * 3 >= n else max(hits, key=hits.get)
    out = {}
    for p in mask:
        t = (p[1] + 0.5 - y0) / L
        a = (p[0] + 0.5 - cx) / L - c(t)
        r = region[p]
        if r == "body":
            half = lerp_profile(TOP_W, t)
            # 등줄기(등지느러미를 위에서 본 것)는 짙게, 왼쪽 어깨에 빛을 받는다
            out[p] = DARK if abs(a) < 0.02 and 0.27 < t < 0.45 else LIGHT if a < -0.35 * half else MID
        elif r == "tail":
            out[p] = DARK
        else:
            out[p] = DARK if abs(a) > 0.19 else MID
    for p in mask:
        x, y = p
        if any(q not in mask for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))):
            out[p] = OUT
    for s in (-1, 1):   # 눈: 머리 양옆 가장자리
        e = (math.floor(cx + (c(0.1) + s * 0.05) * L), math.floor(y0 + 0.1 * L))
        if e in mask:
            out[e] = OUT
    return out, mask


def swim_top() -> tuple[list[dict], tuple[int, int]]:
    frames = []
    for k in range(N):
        body, mask = top(2 * math.pi * k / N)
        frames.append(rim(body, mask))
    return frames, (15, 12)


# no: 빨간 금지 표지 안에서 등지느러미가 물 위로 솟았다 가라앉는다 — "여기선 못 헤엄쳐"
SIGN, SIGN_D = hx("d64541ff"), hx("9e2b28ff")
NO = (13.5, 12.5, 11.5, 8.6)   # 가운데 x, y · 바깥 반지름 · 안 반지름


def sign() -> tuple[list[dict], tuple[int, int]]:
    cx, cy, ro, ri = NO
    ring = set()
    for y in range(32):
        for x in range(32):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            # 빗금은 왼쪽 위 → 오른쪽 아래
            u = ((x + 0.5 - cx) - (y + 0.5 - cy)) / math.sqrt(2)
            if ri <= d <= ro or (d < ri and abs(u) <= 1.5):
                ring.add((x, y))
    frames = []
    for k in range(N):
        ph = 2 * math.pi * k / N
        lift = 2.5 + 2.5 * math.cos(ph)                 # 0–5칸 솟는다
        wy = cy + 5                                     # 물낯 — 빗금 아래 왼쪽 반달에 지느러미가 보이게
        fx = cx - 2 + 1.5 * math.sin(ph)                # 솟는 동안 조금 앞으로 나간다
        f = {}
        # 물낯: 고리 안쪽에만 옅은 물결, 지느러미 밑동 곁은 흰 물보라
        for x in range(32):
            if math.hypot(x + 0.5 - cx, wy + 0.5 - cy) < ri:
                f[x, math.floor(wy)] = WAKE[1]
                f[x, math.floor(wy) + 1] = WAKE[3] if (x + k) % 3 else WAKE[2]
        h = 1.5 + lift * 1.4
        poly = [(fx - x, wy + y) for x, y in fin_poly(10, h)]   # 왼쪽으로 헤엄친다
        mask = set()
        for y in range(32):
            if y >= wy:
                continue
            for x in range(32):
                if math.hypot(x + 0.5 - cx, y + 0.5 - cy) >= ri:
                    continue
                hit = sum(inside(poly, x + (i + 0.5) / 4, y + (j + 0.5) / 4) for i in range(4) for j in range(4))
                if hit >= 8:
                    mask.add((x, y))
        for x, y in mask:
            edge = any(q not in mask for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
            f[x, y] = OUT if edge else DARK if y < wy - h * 0.7 else MID
        if mask:
            xs = [x for x, _ in mask]
            for x in range(min(xs) - 1, max(xs) + 2):
                if math.hypot(x + 0.5 - cx, wy + 0.5 - cy) < ri:
                    f[x, math.floor(wy)] = WAKE[0]
        # 표지는 맨 위에: 테두리는 짙은 빨강, 속은 빨강
        for x, y in ring:
            edge = any(q not in ring for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
            f[x, y] = SIGN_D if edge else SIGN
        frames.append(rim(f, ring | mask))
    return frames, (13, 12)


# ── 칸마다 장면 ─────────────────────────────────────────────────────────────────────
# 같은 상어를 방향만 돌려 놓으면 복제품으로 읽혀서(2026-09-30 사용자), 칸마다 그 칸의 뜻에 맞는 장면을 따로 그린다.
# 화살표 상어가 기준이고 상어는 전부 입을 벌려 흰 이빨 줄을 보인다
FISH, FISH_L = hx("f28c38ff"), hx("ffc36bff")
HOOD, MASK, GLASS = hx("2c343bff"), hx("f2c230ff"), hx("9ed8eaff")
BUB = hx("3f8faeff")
GUM = hx("e88a93ff")
ROOT = hx("c9a27aff")
QMARK = [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."]


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


def solid(f: dict, mask: set, fill, line=OUT) -> None:
    """mask 를 테두리 line · 속 fill 로 칠한다. fill 은 색이나 (칸 → 색) 함수"""
    for p in mask:
        f[p] = line if edge(mask, p) else fill(p) if callable(fill) else fill


def finish(f: dict) -> dict:
    """불투명한 칸 전부에 반투명 테 — 물·물방울처럼 반투명한 것은 테를 안 두른다"""
    return rim(f, {p for p, c in f.items() if c[3] == 255})


def phases():
    return [2 * math.pi * k / N for k in range(N)]


def arrow_shark(ph: float, size: float = LEN, m: float = 1.0) -> dict:
    return shark(*ARROW, ph, size, m)[0]


def bubble(f: dict, cx: float, cy: float, r: float) -> None:
    """물방울: 파란 테 · 옅은 속 · 왼쪽 위 흰 반짝"""
    solid(f, disc(cx, cy, r), WAKE[0], BUB)
    if r >= 2:
        f[math.floor(cx - r * 0.45), math.floor(cy - r * 0.45)] = BELLY


def help_() -> list[dict]:
    """물음표 물방울이 둥실둥실 떠오르고, 작은 물방울이 그 위로 올라간다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = arrow_shark(ph, 0.78)
        dy = round(1.2 * math.sin(ph))
        cx, cy = 23.0, 23.5 + dy
        bubble(f, cx, cy, 5.8)
        for j, row in enumerate(QMARK):
            for i, ch in enumerate(row):
                if ch == "#":
                    f[math.floor(cx) - 2 + i, math.floor(cy) - 3 + j] = OUT
        for j in range(2):   # 작은 물방울 둘이 번갈아 떠오른다
            t = (k / N + j / 2) % 1
            bubble(f, 27.5 - 2 * j, 16.5 - 7 * t, 1.2)
        frames.append(finish(f))
    return frames


def orbit(k: int, pond, s: float = 1.0) -> tuple[dict, set]:
    """wait 의 한 장: 타원을 도는 등지느러미 (s 는 지느러미 배율)"""
    cx, cy, rx, ry = pond
    th = 2 * math.pi * k / N + math.pi / 2   # 첫 장은 가까운 쪽 한가운데
    px, py = cx + rx * math.cos(th), cy + ry * math.sin(th)
    d = -1 if math.sin(th) > 0 else 1        # 가까운 쪽은 왼쪽으로, 먼 쪽은 오른쪽으로 간다
    near = (1 + math.sin(th)) / 2
    w, h = (7 + 3 * near) * s, (9 + 4 * near) * s
    # 물낯: 한 바퀴 전체를 아주 옅게 — 스피너로 읽히게
    f = {}
    for i in range(64):
        a = 2 * math.pi * i / 64
        f[math.floor(cx + rx * math.cos(a)), math.floor(cy + ry * math.sin(a))] = WAKE[-1]
    # 물살 꼬리: 지나온 자리를 따라 옅어지는 점. 먼저 찍고 지느러미가 덮는다
    for i, c in enumerate(WAKE):
        for j in range(2):
            a = th - (i * 2 + j + 1) * 0.16
            q = (math.floor(cx + rx * math.cos(a)), math.floor(cy + ry * math.sin(a)))
            f[q] = c
    poly = [(px + d * x, py + y) for x, y in fin_poly(w, h)]
    if d < 0:
        poly.reverse()
    mask = set()
    for y in range(32):
        for x in range(32):
            hit = sum(inside(poly, x + (i + 0.5) / 4, y + (j + 0.5) / 4) for i in range(4) for j in range(4))
            if hit >= 8:
                mask.add((x, y))
    for x, y in mask:
        front = (x + 0.5 - px) * d > w * 0.05
        f[x, y] = OUT if edge(mask, (x, y)) else LIGHT if front else MID
    f = rim(f, mask)
    # 물을 가르는 자리: 밑동 양옆으로 흰 물보라
    by = math.floor(py)
    xs = [x for x, y in mask if y == max(yy for _, yy in mask)]
    for x in range(min(xs) - 1, max(xs) + 2):
        f[x, by] = WAKE[0] if min(xs) <= x <= max(xs) else WAKE[1]
    return f, mask


def busy() -> list[dict]:
    """화살표 상어 곁에서 작은 등지느러미가 물웅덩이를 빙빙 돈다 — wait 의 작은 판"""
    frames = []
    for k, ph in enumerate(phases()):
        f, _ = orbit(k, (20.5, 25.0, 5.5, 2.4), 0.6)
        f.update(arrow_shark(ph, 0.78))
        frames.append(finish(f))
    return frames


def person() -> list[dict]:
    """잠수부 하나 — 검은 후드 · 노란 물안경 · 스노클에서 물방울이 올라간다. 상어가 친구를 찾았다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = arrow_shark(ph, 0.76)
        cx, cy = 22.5, 22.5
        body = {p for p in disc(cx, 31.5, 6.5) if p[1] <= 30}
        solid(f, body, HOOD)
        head = disc(cx, cy, 4.2)
        solid(f, head, HOOD)
        for x in range(math.floor(cx) - 3, math.floor(cx) + 3):   # 물안경: 노란 테 안에 하늘색 유리
            f[x, math.floor(cy) - 1] = MASK
            f[x, math.floor(cy) + 1] = MASK
            f[x, math.floor(cy)] = MASK if x in (math.floor(cx) - 3, math.floor(cx) + 2) else GLASS
        sx = math.floor(cx) + 4   # 스노클: 머리 오른쪽으로 솟은 관
        for y in range(math.floor(cy) - 6, math.floor(cy) + 2):
            f[sx, y] = MASK
        f[sx - 1, math.floor(cy) - 6] = MASK
        for j in range(3):
            t = (k / N + j / 3) % 1
            bubble(f, sx + 0.5 + math.sin(6 * t + j), cy - 8 - 8 * t, 0.9 + 0.4 * t)
        frames.append(finish(f))
    return frames


def pin() -> list[dict]:
    """빨간 지도 핀이 통통 튄다. 핀 머리에는 흰 등지느러미"""
    frames = []
    for k, ph in enumerate(phases()):
        f = arrow_shark(ph, 0.78)
        dy = -round(2.5 * math.sin(math.pi * k / N))
        cx, cy = 24.0, 20.0 + dy
        body = disc(cx, cy, 5.3) | raster([(cx - 4.6, cy + 2.5), (cx + 4.6, cy + 2.5), (cx, cy + 10)])
        solid(f, body, SIGN, SIGN_D)
        for p in raster([(cx + x, cy + 2 + y) for x, y in fin_poly(6, 5.5)]):
            f[p] = BELLY
        frames.append(finish(f))
    return frames


def fish(f: dict, fx: float, fy: float) -> None:
    """왼쪽으로 달아나는 주황 물고기"""
    body = {(x, y) for y in range(math.floor(fy) - 3, math.floor(fy) + 4) for x in range(math.floor(fx) - 5, math.floor(fx) + 5)
            if ((x + 0.5 - fx) / 3.8) ** 2 + ((y + 0.5 - fy) / 2.6) ** 2 <= 1}
    tail = raster([(fx + 2.5, fy), (fx + 6.5, fy - 3.2), (fx + 6.5, fy + 3.2)])
    m = body | tail
    solid(f, m, lambda p: FISH_L if p[1] + 0.5 > fy + 0.8 and p in body else FISH)
    f[math.floor(fx - 2), math.floor(fy - 1)] = OUT


def we() -> list[dict]:
    """오른쪽 상어가 입을 딱딱 벌리며 왼쪽 물고기를 쫓는다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        fish(f, 5.2 - 0.8 * math.sin(ph), 14.5)
        f.update(shark((12, 15), (30, 12), ph, 1.0, 0.5 + 0.5 * math.cos(2 * ph))[0])
        frames.append(finish(f))
    return frames


def ns() -> list[dict]:
    """두 상어가 엇갈려 지나간다 — 왼쪽은 위로, 오른쪽은 아래로. 등지느러미는 둘 다 바깥을 본다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        f.update(shark((9, 1), (9, 31), ph, 0.8, 0.8, flip=True)[0])
        f.update(shark((21, 30), (21, 0), ph + math.pi, 0.8, 0.8)[0])
        frames.append(finish(f))
    return frames


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


def nesw() -> list[dict]:
    """물 위로 비스듬히 뛰어오른다 — 머리는 오른쪽 위, 꼬리 쪽은 왼쪽 아래 물보라"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        wy = 25
        water(f, 0, 17, wy, k)
        sh, _ = shark((27, 3), (5, 26), ph, 0.95, 0.7)
        f.update({p: c for p, c in sh.items() if p[1] < wy})
        splash(f, 6.5, wy - 1, k, 4, 6, 5)
        frames.append(finish(f))
    return frames


def nwse() -> list[dict]:
    """오른쪽 아래로 파고드는 잠수 — 왼쪽 위 꼬리 뒤로 물방울 줄이 떠오른다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        f.update(shark((28, 28), (8, 8), ph, 1.0, 0.8)[0])
        for j in range(4):
            t = (k / N + j / 4) % 1
            bubble(f, 2.5 + 1.2 * math.sin(7 * t + j), 12 - 11 * t, 0.8 + 0.6 * t)
        frames.append(finish(f))
    return frames


def up() -> list[dict]:
    """곧장 솟구치는 부캉이. 아래는 물낯과 물보라 왕관"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        wy = 26
        water(f, 0, 18, wy, k)
        sh, _ = shark((9, 1), (9, 30), ph, 1.0, 0.6 + 0.4 * math.cos(ph))
        f.update({p: c for p, c in sh.items() if p[1] < wy})
        splash(f, 9.5, wy - 1, k, 6, 8, 6)
        frames.append(finish(f))
    return frames


def pen() -> list[dict]:
    """상어 이빨 한 개가 펜 — 톱니 날의 넓은 세모, 끝은 왼쪽 아래(핫스팟), 뿌리는 가운데가 파인 두 갈래.
    끝에서 물결선이 그려져 나간다"""
    tip, root = (1.5, 30.5), (17.5, 14.0)
    L = math.hypot(root[0] - tip[0], root[1] - tip[1])
    ux, uy = (root[0] - tip[0]) / L, (root[1] - tip[1]) / L
    nx, ny = uy, -ux   # 날의 옆 (+ 는 오른쪽 아래)

    def at(a, b):   # a: 끝→뿌리 (0–1), b: 옆 (이빨 길이 단위)
        bend = -0.08 * a * a   # 끝이 살짝 휜다
        return tip[0] + (a * ux + (b + bend) * nx) * L, tip[1] + (a * uy + (b + bend) * ny) * L
    SAW = 4

    def half(a):   # 곧은 날 + 톱니 — 톱니 한 칸이 32칸에서 1칸은 튀어나와야 보인다
        return 0.4 * a * (1 + 0.24 * ((a * SAW) % 1)) if a > 0.25 else 0.4 * a
    aa = [i / 80 for i in range(81)]
    blade = raster([at(a, half(a)) for a in aa] + [at(a, -half(a)) for a in reversed(aa)])
    rootp = raster([at(0.97, 0.42), at(1.2, 0.36), at(1.22, 0.12), at(1.12, 0.0), at(1.22, -0.12), at(1.2, -0.36),
                    at(0.97, -0.42)]) - blade

    def shade(p):
        dx, dy = p[0] + 0.5 - tip[0], p[1] + 0.5 - tip[1]
        return SHADE if dx * nx + dy * ny > 0.05 * L else BELLY
    frames = []
    for k in range(N):
        f = {}
        solid(f, rootp, ROOT)
        solid(f, blade, shade)
        for x in range(3, 4 + round(24 * (k + 1) / N)):   # 물결선이 오른쪽으로 써진다
            f[x, 31 - (1 if math.sin(x * 0.9) > 0.3 else 0)] = WAKE[1]
        frames.append(finish(f))
    return frames


def hand() -> list[dict]:
    """물 위로 얼굴을 쏙 내민 부캉이를 앞에서 — 주둥이 끝이 핫스팟, 양옆 눈, 톱니 이빨로 딱딱 무는 입,
    옆으로 편 가슴지느러미"""
    cx = 11.5
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        wy = 23
        bob = round(0.8 * math.sin(ph))
        m = max(0.0, math.sin(2 * ph))
        top = 1 + bob

        def half(y):
            return 9.0 * math.sqrt(max(0.0, min(1.0, (y - top) / 12)))
        head = {(x, y) for y in range(top, wy) for x in range(math.floor(cx - 10), math.ceil(cx + 10))
                if abs(x + 0.5 - cx) <= half(y + 0.5)}
        fins = set()
        for s in (-1, 1):
            fins |= raster([(cx + s * 6, 15 + bob), (cx + s * 12.5, 20.5 + bob), (cx + s * 11, 22 + bob), (cx + s * 6, 20 + bob)])
        fins = {p for p in fins if p[1] < wy} - head
        solid(f, fins, lambda p: DARK if abs(p[0] + 0.5 - cx) > 10 else MID)
        my = 14.5 + bob

        def skin(p):
            x, y = p[0] + 0.5 - cx, p[1] + 0.5
            if y > my:
                return BELLY if abs(x) < 0.7 * half(y) else SHADE
            return LIGHT if abs(x) > 0.6 * half(y) else MID
        solid(f, head, skin)
        for s in (-1, 1):   # 눈: 머리 양옆 — 검은 2×2 에 흰 반짝 한 칸
            ex = math.floor(cx + s * 4.5) - (1 if s < 0 else 0)
            for dx in (0, 1):
                for dy in (0, 1):
                    f[ex + dx, 8 + bob + dy] = OUT
            f[ex + (1 if s < 0 else 0), 8 + bob] = BELLY
        # 입: 머리 폭 거의 전부. 위아래 잇몸에 세모 이빨(세 칸마다 끝이 한 칸 더 내려온다), 속은 검붉게
        rx, ry = 6.6, 1.3 + 2.4 * m
        mouth = {p for p in head if ((p[0] + 0.5 - cx) / rx) ** 2 + ((p[1] + 0.5 - my) / ry) ** 2 <= 1}
        for p in mouth:
            col = [q for q in mouth if q[0] == p[0]]
            y0, y1 = min(q[1] for q in col), max(q[1] for q in col)
            tip = p[0] % 3 == 1
            if p[1] == y0 or p[1] == y1 or (tip and (p[1] == y0 + 1 or p[1] == y1 - 1) and y1 - y0 >= 4):
                f[p] = BELLY
            else:
                f[p] = GULLET
        for p in head - mouth:   # 입술 선
            x, y = p
            if any(q in mouth for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))):
                f[p] = OUT
        water(f, 0, 23, wy, k)
        frames.append(finish(f))
    return frames


def cross() -> list[dict]:
    """조준경 — 동그라미 안 물낯을 작은 등지느러미가 가로지른다. 가운데 빨간 점이 핫스팟"""
    c = 15
    frames = []
    for k in range(N):
        f = {}
        ring = {(x, y) for y in range(32) for x in range(32) if 9.2 <= math.hypot(x - c, y - c) < 10.2}
        wy = c + 4
        for x in range(32):
            if math.hypot(x - c, wy - c) < 9:
                f[x, wy] = WAKE[2]
        fx = c - 8 + 16 * k / N
        mask = {p for p in raster([(fx + x, wy + y) for x, y in fin_poly(5.5, 5)]) if math.hypot(p[0] - c, p[1] - c) < 8.8}
        solid(f, mask, MID)
        for p in ring:
            f[p] = OUT
        for d in range(3, 13):
            for q in ((c, c - d), (c, c + d), (c - d, c), (c + d, c)):
                f[q] = OUT
        f[c, c] = SIGN
        frames.append(finish(f))
    return frames


JAW_ROWS = [".OOOOOOOOO.",   # 윗턱 한 벌 (아랫턱은 위아래로 뒤집는다). M 몸 · G 잇몸 · W 이빨 · O 테두리
            "OMMMMMMMMMO",
            "OGGGGGGGGGO",
            "OWWWWWWWWWO",
            ".OWOOWOOWO.",
            "..O..O..O.."]


def ibeam() -> list[dict]:
    """턱 I빔 — 위아래 가로대가 윗턱·아랫턱이고 톱니 이빨이 안쪽을 본다. 한 바퀴에 한 번 딱 문다"""
    H = 25
    col = {"O": OUT, "M": MID, "G": GUM, "W": BELLY}
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        c = 1 if math.sin(ph) > 0.5 else 0
        for j, row in enumerate(JAW_ROWS):
            for x, ch in enumerate(row):
                if ch in col:
                    f[x, c + j] = col[ch]
                    f[x, H - 1 - c - j] = col[ch]
        for y in range(c + len(JAW_ROWS), H - c - len(JAW_ROWS)):
            f[5, y] = OUT
        frames.append(finish(f))
    return frames


SCENE = {"help": help_, "busy": busy, "person": person, "pin": pin, "we": we, "ns": ns, "nesw": nesw,
         "nwse": nwse, "up": up, "pen": pen, "hand": hand, "cross": cross, "ibeam": ibeam}
HOT = {"help": (1, 2), "busy": (1, 2), "person": (1, 2), "pin": (1, 2), "we": (16, 14), "ns": (15, 15),
       "nesw": (16, 14), "nwse": (16, 16), "up": (9, 1), "pen": (1, 30), "hand": (11, 1), "cross": (15, 15),
       "ibeam": (5, 12)}


def main() -> None:
    roles = sys.argv[1:] or list(ROLES)
    d = WIN / "art" / SID
    d.mkdir(parents=True, exist_ok=True)
    for rid in roles:
        if rid == "wait":
            frames, hot = circle()
        elif rid == "move":
            frames, hot = swim_top()
        elif rid == "no":
            frames, hot = sign()
        elif rid == "arrow":
            frames = [finish(arrow_shark(ph)) for ph in phases()]
            hot = ARROW[0]
        else:
            frames, hot = SCENE[rid](), HOT[rid]
        (d / f"{rid}.txt").write_text(S.to_text(frames, hot, RATE), encoding="utf-8")
        print(f"{rid}: {len(frames)}장")


if __name__ == "__main__":
    main()

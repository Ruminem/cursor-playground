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

from sea import (N, QMARK, SIGN, SIGN_D, WAKE, Body, disc, bubble, edge, fin_poly, finish, hx, ink, inside,
                 lerp_profile, phases, raster, rim, side, solid, splash, water, write)

SID = "bukanganim"
THICK = 1.6               # 두께 배율. 실제 비율(1)로 그리면 몸이 3칸이라 테두리가 속을 다 먹는다
LEN = 1.05                # 몸길이 = 머리→꼬리 거리의 몇 배 (기본값)
ARROW = ((1, 2), (15, 21))   # 화살표 상어의 머리 끝(핫스팟) · 꼬리 끝


OUT, DARK, MID, LIGHT = hx("1b2227ff"), hx("3d4a52ff"), hx("5b6b74ff"), hx("7e8f98ff")
BELLY, SHADE = hx("eef2f3ff"), hx("c3ccd1ff")
GULLET = hx("7a2430ff")                       # 벌린 입 속
ink(OUT, BELLY)


# ── 옆모습 상어: 주둥이 s=0 → 꼬리 끝 s=1, v 는 등 쪽이 + (몸길이 단위) ─────────────────────
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


def sweep(ph: float) -> float:
    """꼬리를 옆으로 젓는 상어를 옆에서 보면 꼬리가 앞뒤로 줄었다 늘었다 한다 — PIVOT 뒤의 길이 배율.
    돌고래처럼 위아래로 까딱이면 상어가 아니다"""
    return 0.82 + 0.18 * math.cos(ph)


def fold(s: float, k: float) -> float:
    return s if s <= PIVOT else PIVOT + (s - PIVOT) * k


def unfold(s: float, k: float) -> float:
    return s if s <= PIVOT else PIVOT + (s - PIVOT) / k


def skin(s, v, top, bot):
    """등은 짙게, 옆구리는 밝게, 배는 희게 — 옆구리와 배 사이 경계를 또렷하게 (상어의 역그늘)"""
    sep = bot + 0.45 * (top - bot)
    if v > sep + 0.5 * (top - sep):
        return MID
    if v > sep:
        return LIGHT
    if v < bot + 0.3 * (sep - bot):
        return SHADE
    return BELLY


def decorate(c) -> None:
    """눈 · 입(벌렸으면 톱니 이빨, 다물었으면 비스듬한 선) · 아가미구멍 셋"""
    e = c.at(0.085, 0.02)
    if e in c.mask:
        c.out[e] = OUT
    if c.m > 0:
        # 벌린 입: 속은 검붉게, 윗잇몸과 아래턱을 따라 흰 이빨(한 칸 건너 한 칸 — 톱니로 읽힌다).
        # 속을 테두리색으로 칠하면 입이 윤곽선에 묻혀 안 보인다
        wedge = MOUTH(c.m)
        (s0, v0), (s1, v1), (s2, v2) = wedge
        for p in c.mask:
            if edge(c.mask, p):
                continue
            s, v = c.local(p[0] + 0.5, p[1] + 0.5)
            v /= c.T
            if not inside(wedge, s, v):
                continue
            gum = v0 + (v1 - v0) * (s - s0) / (s1 - s0)
            low = v2 + (v1 - v2) * (s - s2) / (s1 - s2) if s >= s2 else v2
            tooth = math.floor(s * c.L) % 2 == 0
            near = min(gum - v, v - low) * c.L * c.T < 1.1
            c.out[p] = BELLY if near and tooth else GULLET
    else:
        for s in (0.07, 0.1, 0.13):
            c.paint(c.at(s, lerp_profile(BOT, s) * 0.45 - 0.004), DARK)
    for i in range(3 if c.detail else 0):   # 아가미구멍 셋 — 2칸 간격 세로줄
        gs = 0.17 + i * 2 / c.L
        for v in (-0.03, -0.01, 0.01, 0.03):
            c.paint(c.at(gs, v), DARK)


SHARK = Body(
    top=TOP, bot=BOT, fins=FINS, order=("pectoral", "body", "dorsal", "pelvic", "dorsal2", "anal", "caudal"),
    skin=skin, fin_ink=lambda r, s, v: DARK if r in TIPS and TIPS[r](s, v) else MID,
    bend=lambda s, v, ph: (fold(s, sweep(ph)), v), unbend=lambda s, v, ph: (unfold(s, sweep(ph)), v),
    decorate=decorate, thick=THICK, length=LEN, small=("pelvic", "dorsal2", "anal"),
    extra=lambda m: {"jaw": (JAW(m), SHADE)}, lined=("pectoral",))


def shark(head, tail, ph, size=None, m=0.0, flip=False, detail=True):
    """자세 하나 × 위상 하나 → ({좌표: 색}, 몸 칸 집합) — `sea.side` 참고. m 은 입을 벌린 정도(0–1) — 아래턱이
    내려가고 윗잇몸에 흰 이빨 줄이 보인다. detail 을 끄면 아가미구멍과 배·둘째 등·뒷지느러미를 뺀다 — 줄여 그리거나
    세로로 선 좁은 몸에서는 아가미 세 줄이 갈비뼈로, 줄줄이 튀어나온 지느러미가 가시로 읽혀 생선 뼈가 된다"""
    return side(SHARK, head, tail, ph, size, m, flip, detail)


# wait: 물 위로 등지느러미만 내놓고 수로를 빙빙 도는 부캉이. 물낯을 비스듬히 본 타원을 돌며 물살 꼬리를 남긴다
POND = (16.0, 18.0, 11.0, 5.0)   # 타원 가운데 x, y · 가로 반지름 · 세로 반지름


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
FISH, FISH_L, FISH_D = hx("f28c38ff"), hx("ffc36bff"), hx("c0612aff")
HOOD, MASK, GLASS = hx("2c343bff"), hx("f2c230ff"), hx("9ed8eaff")
GUM = hx("e88a93ff")
ROOT = hx("c9a27aff")


def arrow_shark(ph: float, size: float = LEN, m: float = 1.0) -> dict:
    """화살표 상어. 줄여 그린 것(장면 곁의 작은 상어)은 detail 을 끈다"""
    return shark(*ARROW, ph, size, m, detail=size >= LEN)[0]


def help_() -> list[dict]:
    """물음표 물방울이 둥실둥실 떠오르고, 작은 물방울이 그 위로 올라간다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = arrow_shark(ph, 0.78)
        dy = round(1.2 * math.sin(ph))
        cx, cy = 22.0, 23.5 + dy
        bubble(f, cx, cy, 5.8)
        for j, row in enumerate(QMARK):
            for i, ch in enumerate(row):
                if ch == "#":
                    f[math.floor(cx) - 2 + i, math.floor(cy) - 3 + j] = OUT
        for j in range(2):   # 작은 물방울 둘이 번갈아 떠오른다
            t = (k / N + j / 2) % 1
            bubble(f, 26.5 - 2 * j, 16.5 - 7 * t, 1.2)
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
        f, _ = orbit(k, (19.5, 25.0, 5.5, 2.4), 0.6)
        f.update(arrow_shark(ph, 0.78))
        frames.append(finish(f))
    return frames


def person() -> list[dict]:
    """잠수부 하나 — 검은 후드 · 노란 물안경 · 스노클에서 물방울이 올라간다. 상어가 친구를 찾았다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = arrow_shark(ph, 0.76)
        cx, cy = 21.5, 22.5
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
        cx, cy = 23.0, 20.0 + dy
        body = disc(cx, cy, 5.3) | raster([(cx - 4.6, cy + 2.5), (cx + 4.6, cy + 2.5), (cx, cy + 10)])
        solid(f, body, SIGN, SIGN_D)
        for p in raster([(cx + x, cy + 2 + y) for x, y in fin_poly(6, 5.5)]):
            f[p] = BELLY
        frames.append(finish(f))
    return frames


def fish(f: dict, fx: float, fy: float) -> None:
    """왼쪽으로 달아나는 주황 물고기. 통통한 몸 · 갈라진 꼬리 · 등지느러미 · 아가미 줄 — 길쭉하면 당근으로 읽힌다"""
    body = {(x, y) for y in range(math.floor(fy) - 4, math.floor(fy) + 5) for x in range(math.floor(fx) - 5, math.floor(fx) + 5)
            if ((x + 0.5 - fx) / 4.0) ** 2 + ((y + 0.5 - fy) / 3.5) ** 2 <= 1}
    tail = raster([(fx + 3.0, fy), (fx + 6.6, fy - 3.6), (fx + 5.4, fy), (fx + 6.6, fy + 3.6)])
    top = raster([(fx - 1.4, fy - 2.8), (fx + 1.4, fy - 5.0), (fx + 2.8, fy - 2.2)])
    m = body | tail | top
    solid(f, m, lambda p: FISH_L if p[1] + 0.5 > fy + 0.6 and p in body else FISH)
    for dy in (-1, 0, 1):   # 아가미 줄
        f[math.floor(fx - 0.8 + 0.5 * abs(dy)), math.floor(fy + dy)] = FISH_D
    f[math.floor(fx - 1.6), math.floor(fy - 1.0)] = OUT


def we() -> list[dict]:
    """오른쪽 상어가 입을 딱딱 벌리며 왼쪽 물고기를 쫓는다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        fish(f, 5.0 - 0.8 * math.sin(ph), 14.5)
        f.update(shark((12, 15), (30, 12), ph, 1.0, 0.5 + 0.5 * math.cos(2 * ph))[0])
        frames.append(finish(f))
    return frames


def ns() -> list[dict]:
    """두 상어가 엇갈려 지나간다 — 왼쪽은 위로, 오른쪽은 아래로. 등지느러미는 둘 다 바깥을 본다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        f.update(shark((8, 1), (8, 31), ph, 0.8, 0.8, flip=True, detail=False)[0])
        f.update(shark((21, 30), (21, 0), ph + math.pi, 0.8, 0.8, detail=False)[0])
        frames.append(finish(f))
    return frames


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
        sh, _ = shark((9, 1), (9, 30), ph, 1.0, 0.6 + 0.4 * math.cos(ph), detail=False)
        f.update({p: c for p, c in sh.items() if p[1] < wy})
        splash(f, 9.5, wy - 1, k, 6, 8, 6)
        frames.append(finish(f))
    return frames


def pen() -> list[dict]:
    """상어 연필 — 누구나 아는 대각선 연필 꼴에 몸통은 상어 색(짙은 등 · 흰 배), 등에 세모 지느러미,
    끝은 꼬리지느러미, 깎은 나무 바로 뒤에 눈. 끝(핫스팟)에서 물결선이 써져 나간다.
    상어 이빨 한 개로 그렸던 것은 32칸에서 치약 튜브·콘으로 읽혀 버렸다"""
    tip, back = (1.5, 30.5), (25.5, 6.5)
    L = math.hypot(back[0] - tip[0], back[1] - tip[1])
    ux, uy = (back[0] - tip[0]) / L, (back[1] - tip[1]) / L
    nx, ny = uy, -ux   # 연필의 옆 — + 가 왼쪽 위(등)

    def at(a, b):   # a: 끝→꽁무니 (0–1), b: 옆 (칸)
        return tip[0] + a * ux * L + b * nx, tip[1] + a * uy * L + b * ny

    def ab(p):
        dx, dy = p[0] + 0.5 - tip[0], p[1] + 0.5 - tip[1]
        return (dx * ux + dy * uy) / L, dx * nx + dy * ny
    W, CONE, END = 3.3, 0.24, 0.84   # 반폭(칸) · 깎은 자리 끝 · 몸통 끝
    body = raster([at(CONE, W), at(END, W), at(END, -W), at(CONE, -W)])
    cone = raster([at(0.0, 0.0), at(CONE + 0.01, W), at(CONE + 0.01, -W)]) - body
    fin = raster([at(0.4, W - 0.5), at(0.56, W + 6.5), at(0.6, W + 6.3), at(0.6, W + 3.0), at(0.64, W - 0.5)]) - body
    # 꼬리: 윗날개가 길게 뒤로 젖고 아랫날개는 짧다 — 대칭이면 로켓 날개로 읽힌다
    tail = raster([at(END - 0.02, 2.0), at(1.05, W + 4.6), at(1.02, W + 3.4), at(0.95, 0.3), at(0.97, -W - 1.8),
                   at(0.93, -W - 1.6), at(END - 0.02, -1.8)]) - body

    def skin(p):
        a, b = ab(p)
        return MID if b > 0.9 else LIGHT if b > 0.0 else BELLY if b > -W + 1.2 else SHADE

    def wood(p):
        a, b = ab(p)
        return OUT if a < 0.08 else ROOT
    frames = []
    for k in range(N):
        f = {}
        solid(f, fin, lambda p: DARK if ab(p)[1] > W + 3 else MID)
        solid(f, tail, lambda p: DARK if abs(ab(p)[1]) > W + 1.5 else MID)
        solid(f, body, skin)
        solid(f, cone, wood)
        e = at(CONE + 0.07, 1.3)   # 눈
        f[math.floor(e[0]), math.floor(e[1])] = OUT
        for i in range(3):   # 아가미구멍 셋
            g = at(CONE + 0.15 + i * 0.045, 0.2)
            f[math.floor(g[0]), math.floor(g[1])] = DARK
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
        wy = 25
        bob = round(0.8 * math.sin(ph))
        top = 1 + bob
        # 한 바퀴에 두 번 딱 문다 — 다 닫지는 않는다. 닫히면 이빨이 안 보여 그냥 둥근 머리가 된다
        gape = 3.4 + 3.2 * (0.5 + 0.5 * math.cos(2 * ph))
        my = 16.0 + bob

        def half(y):   # 머리 반폭: 둥근 주둥이 끝에서 뺨까지 빨리 넓어진다
            return 10.5 * math.sqrt(max(0.0, min(1.0, (y - top) / 11)))

        def upper(x):   # 윗입술 — 입꼬리가 올라간 웃는 입
            return my - gape / 2 - 0.03 * x * x

        def lower(x):
            return my + gape / 2 - 0.085 * x * x
        head = {(x, y) for y in range(top, wy) for x in range(math.floor(cx - 11), math.ceil(cx + 11))
                if abs(x + 0.5 - cx) <= half(y + 0.5)}
        fins = set()
        for s in (-1, 1):   # 가슴지느러미: 뺨 아래에서 옆으로 뻗고 끝이 처진다
            fins |= raster([(cx + s * 8, 17 + bob), (cx + s * 13.5, 21.5 + bob), (cx + s * 12.5, 23.5 + bob),
                            (cx + s * 8, 22 + bob)])
        fins = {p for p in fins if p[1] < wy} - head
        solid(f, fins, lambda p: DARK if abs(p[0] + 0.5 - cx) > 11.5 else MID)

        def skin(p):   # 등은 짙게 · 오른쪽 뺨은 빛 · 입 아래로는 흰 배
            x, y = p[0] + 0.5 - cx, p[1] + 0.5
            if y > upper(x) + 0.5:
                return BELLY if abs(x) < 0.72 * half(y) else SHADE
            if y < top + 3:
                return DARK
            return LIGHT if x > 0.45 * half(y) else MID
        solid(f, head, skin)
        for s in (-1, 1):   # 콧구멍: 주둥이 끝 가까이 짙은 점 둘
            f[math.floor(cx + s * 1.6), top + 4] = DARK
        for s in (-1, 1):   # 눈: 머리 양옆 — 검은 2×2 에 흰 반짝 한 칸 (둘 다 왼쪽 위에서 빛을 받는다)
            ex = math.floor(cx + s * 4.5) - (1 if s < 0 else 0)
            ey = top + 7
            for dx in (0, 1):
                for dy in (0, 1):
                    f[ex + dx, ey + dy] = OUT
            f[ex, ey] = BELLY
        # 입: 웃는 초승달. 위아래 잇몸에 세모 이빨 — 세 칸에 하나씩 끝이 한 칸 더 나오고, 위아래가 엇갈려 맞물린다
        mouth = {p for p in head if upper(p[0] + 0.5 - cx) < p[1] + 0.5 < lower(p[0] + 0.5 - cx)
                 and abs(p[0] + 0.5 - cx) < half(p[1] + 0.5) - 1.5}
        for p in mouth:
            x = p[0] + 0.5 - cx
            du, dl = p[1] + 0.5 - upper(x), lower(x) - (p[1] + 0.5)
            tu = 2.0 if p[0] % 3 == 0 else 1.0
            tl = 2.0 if p[0] % 3 == 2 else 1.0
            if du < tu or dl < tl:
                f[p] = BELLY
            elif abs(x) < 3 and dl < tl + 1.2:
                f[p] = GUM   # 혀
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
    """조준경 — 동그라미 안 물낯을 등지느러미가 좌우로 오가며 방향을 튼다. 지나온 자리에 물살 꼬리.
    지느러미는 조준선 앞에 그린다 — 선에 가리면 32칸에서 안 보인다. 가운데 빨간 점이 핫스팟"""
    c = 15
    R = 9.2
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        wy = c + 5
        for x in range(32):   # 물낯
            if math.hypot(x + 0.5 - c - 0.5, wy + 0.5 - c - 0.5) < R - 0.6:
                f[x, wy] = WAKE[1] if (x + k) % 3 else WAKE[2]
        for d in range(3, 13):   # 조준선: 가운데는 비운다
            for q in ((c, c - d), (c, c + d), (c - d, c), (c + d, c)):
                f[q] = OUT
        fx = c + 0.5 + 4.0 * math.sin(ph)
        d = 1 if math.cos(ph) > 0 else -1   # 가는 쪽
        for i, col in enumerate(WAKE[:4]):   # 물살 꼬리: 지나온 쪽으로 옅어진다
            q = (math.floor(fx - d * (3.5 + i)), wy)
            if math.hypot(q[0] + 0.5 - c - 0.5, wy + 0.5 - c - 0.5) < R - 0.6:
                f[q] = col
        poly = [(fx + d * x, wy + 0.3 + y) for x, y in fin_poly(8.5, 9.0)]
        if d < 0:
            poly.reverse()
        mask = {p for p in raster(poly) if math.hypot(p[0] + 0.5 - c - 0.5, p[1] + 0.5 - c - 0.5) < R - 0.6}
        solid(f, mask, lambda p: LIGHT if (p[0] + 0.5 - fx) * d > 0.4 else MID)
        ring = {(x, y) for y in range(32) for x in range(32) if R - 0.5 <= math.hypot(x - c, y - c) < R + 0.6}
        for p in ring:
            f[p] = OUT
        for q in ((c, c - R - 2), (c, c + R + 2), (c - R - 2, c), (c + R + 2, c)):   # 눈금: 동그라미 밖으로 튀어나온 선
            f[int(q[0]), int(q[1])] = OUT
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
    table = {"arrow": lambda: ([finish(arrow_shark(ph)) for ph in phases()], ARROW[0]),
             "wait": circle, "move": swim_top, "no": sign}
    table.update({r: (lambda r=r: (SCENE[r](), HOT[r])) for r in SCENE})
    write(SID, dict(sorted(table.items())), sys.argv[1:] or None)


if __name__ == "__main__":
    main()

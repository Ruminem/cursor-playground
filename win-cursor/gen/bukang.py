# SPDX-License-Identifier: Apache-2.0
"""부캉이(bukanganim) 구성표 그림 `art/bukanganim/*.txt` 를 만든다. 빌드가 부르지 않고 그림을 다시 뽑을 때 손으로 돌린다.

  python3 gen/bukang.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

부캉이는 2026-09-18 부산 북항 친수공원 수로에 들어와 열이틀 머문 상어의 별명이다. 국립수산과학원 추정으로
무태상어(흉상어과) 암컷 약 3m — 무늬 없는 회청색 등, 흰 배, 세모 등지느러미, 위 날개가 긴 꼬리.
동구청이 공식 캐릭터를 따로 공모하고 있으므로 그것을 닮게 그리지 않고 그냥 상어를 그린다.

칸마다 자세(머리 끝·꼬리 끝)와 기호(? · 사람 · 핀 · 도는 점)는 돌고래 애니(BASE 커밋의 art/dolphinanim)에서
빌려 오고, 옆모습 몸은 여기서 거리 단위 다각형으로 새로 그린다. 첫 벌은 돌고래 몸을 조금 고친 꼴이라 돌고래로 읽혀서
상어만의 것을 따로 세웠다 — 입 위로 튀어나온 원뿔 주둥이 · 앞으로 쏠린 세모 등지느러미 · 긴 낫 모양 가슴지느러미 ·
윗날개가 긴 꼬리 · 아가미구멍 셋 · 거뭇한 지느러미 끝. 꼬리도 돌고래처럼 위아래로 까딱이지 않고 옆으로 저으니
옆에서 보면 꼬리가 줄었다 늘었다 한다(`sweep`).
wait 는 `keep` 이라 11모양 전부에 그대로 실리므로 따로 그린다 — 물 위로 등지느러미만 내놓고 수로를 빙빙 도는
모습(`circle`). 원호로 휜 몸을 먼저 그려 봤는데 32칸에서 지느러미가 뭉개져 버렸다. move 는 위에서 본 상어(`top`),
no 는 빨간 금지 표지 안에서 등지느러미가 솟았다 가라앉는 그림(`sign`)이다. 기호뿐인 칸(cross·hand·ibeam)은
돌고래 그림에 상어 색만 입힌다.
12장 × rate 5 = 1초에 꼬리 한 번. 다른 해양 애니와 같은 박자다.
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import subprocess
import sys
from pathlib import Path

WIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WIN))
import shape as S   # noqa: E402

REPO = WIN.parent
BASE = "e5cab45"          # 돌고래 애니 그림이 있는 main 커밋 — 자세·기호를 여기서 뜬다
SRC, SID = "dolphinanim", "bukanganim"
N, RATE = 12, 5
THICK = 1.6               # 두께 배율. 실제 비율(1)로 그리면 몸이 3칸이라 테두리가 속을 다 먹는다
LEN = 1.05                # 몸길이 = 돌고래 머리→꼬리 거리의 몇 배. 꼬리 윗날개가 비스듬히 솟아 1 이면 32칸을 넘는다
ROLES = ("arrow", "busy", "cross", "hand", "help", "ibeam", "move", "nesw", "no", "ns",
         "nwse", "pen", "person", "pin", "up", "wait", "we")
GLYPH = ("busy", "help", "person", "pin")   # 화살표 상어에 돌고래 칸의 기호만 얹는 칸
# 옆모습으로 새로 그리는 칸의 머리·꼬리 끝(돌고래 몸 주축의 두 끝, 핫스팟이 머리에 있으면 핫스팟)
POSE = {
    "arrow": ((1, 2), (15, 21)),
    "nesw": ((26, 2), (1, 19)),
    "nwse": ((1, 2), (26, 19)),
    "ns": ((7, 1), (11, 29)),
    "up": ((7, 1), (7, 28)),
    "pen": ((1, 25), (16, 7)),
    "we": ((1, 14), (29, 10)),
}


def hx(s: str) -> tuple:
    return tuple(bytes.fromhex(s))


OUT, DARK, MID, LIGHT = hx("1b2227ff"), hx("3d4a52ff"), hx("5b6b74ff"), hx("7e8f98ff")
BELLY, SHADE = hx("eef2f3ff"), hx("c3ccd1ff")
RIM = hx("d2dde6c7")                          # 돌고래 애니와 같은 반투명 테
# 돌고래 색 → 상어 색 (색만 입히는 칸)
RECOLOR = {hx("17212cff"): OUT, hx("2c3a4aff"): DARK, hx("43566bff"): MID, hx("566b83ff"): LIGHT,
           hx("cfd8e0ff"): SHADE, hx("dfe6ecff"): BELLY, hx("f7fafcff"): BELLY, RIM: RIM}


def old_art(rid: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), "show", f"{BASE}:win-cursor/art/{SRC}/{rid}.txt"],
                          capture_output=True, text=True, encoding="utf-8", check=True).stdout


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


def straight(head, tail, size=None):
    """머리 칸 → 꼬리 칸으로 뻗은 몸의 (local, world, L) — 칸 좌표 ↔ (s, v) 몸길이 단위, L 은 몸길이(칸)"""
    hx_, hy = head[0] + 0.5, head[1] + 0.5
    tx, ty = tail[0] + 0.5, tail[1] + 0.5
    D = math.hypot(tx - hx_, ty - hy)
    ux, uy = (tx - hx_) / D, (ty - hy) / D
    L = D * (size or LEN)
    cands = [(uy, -ux), (-uy, ux)]
    nx, ny = min(cands, key=lambda n: (round(n[1], 6), -n[0]))   # 등은 위(세로면 오른쪽)

    def local(px, py):
        dx, dy = px - hx_, py - hy
        return (dx * ux + dy * uy) / L, (dx * nx + dy * ny) / L

    def world(s, v):
        return hx_ + (s * ux + v * nx) * L, hy + (s * uy + v * ny) * L
    return local, world, L


def shark(head, tail, ph, size=None):
    """자세 하나 × 위상 하나 → ({좌표: 색}, 몸 칸 집합). 몸 칸은 테를 두르기 전 불투명한 칸"""
    local, world, L = straight(head, tail, size)
    k = sweep(ph)
    parts = {"body": [(fold(s, k), v * THICK) for s, v in body_poly()]}
    for name, pts in FINS.items():
        parts[name] = [(fold(s, k), v * THICK) for s, v in pts]
    order = ("pectoral", "body", "dorsal", "pelvic", "dorsal2", "anal", "caudal")

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


def side(role: str) -> tuple[list[dict], tuple[int, int]]:
    """옆모습 12장. 테까지 32칸에 들 때까지 몸길이를 3% 씩 줄인다 (머리는 핫스팟에 둔 채)"""
    head, tail = POSE[role]
    size = LEN
    while True:
        frames = []
        for k in range(N):
            body, mask = shark(head, tail, 2 * math.pi * k / N, size)
            frames.append(rim(body, mask))
        x0, y0, x1, y1 = S.bbox([p for f in frames for p in f])
        if max(x1 - x0, y1 - y0) < 32:
            return frames, head
        size -= 0.03


# wait: 물 위로 등지느러미만 내놓고 수로를 빙빙 도는 부캉이. 물낯을 비스듬히 본 타원을 돌며 물살 꼬리를 남긴다
POND = (16.0, 18.0, 11.0, 5.0)   # 타원 가운데 x, y · 가로 반지름 · 세로 반지름
WAKE = (hx("e8fcffff"), hx("7cc4d8ff"), hx("7cc4d8b0"), hx("7cc4d870"), hx("7cc4d838"))   # 지느러미에 가까운 것부터


def fin_poly(w: float, h: float) -> list:
    """앞(+x)으로 헤엄치는 등지느러미. 밑동 (0,0) 가운데, 위가 -y. 앞날은 볼록하게, 뒷날은 오목하게"""
    return [(w / 2, 0), (w * 0.22, -h * 0.5), (-w * 0.08, -h * 0.85), (-w * 0.38, -h), (-w * 0.3, -h * 0.6),
            (-w * 0.36, -h * 0.25), (-w / 2, 0)]


def circle() -> tuple[list[dict], tuple[int, int]]:
    """12장에 한 바퀴(시계 방향). 가까운 쪽(아래)을 지날 때 지느러미가 크고 먼 쪽(위)에서 작다. 핫스팟은 타원 가운데"""
    cx, cy, rx, ry = POND
    frames = []
    for k in range(N):
        th = 2 * math.pi * k / N + math.pi / 2   # 첫 장은 가까운 쪽 한가운데
        px, py = cx + rx * math.cos(th), cy + ry * math.sin(th)
        d = -1 if math.sin(th) > 0 else 1        # 가까운 쪽은 왼쪽으로, 먼 쪽은 오른쪽으로 간다
        near = (1 + math.sin(th)) / 2
        w, h = 7 + 3 * near, 9 + 4 * near
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
            edge = any(q not in mask for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
            front = (x + 0.5 - px) * d > w * 0.05
            f[x, y] = OUT if edge else LIGHT if front else MID
        f = rim(f, mask)
        # 물을 가르는 자리: 밑동 양옆으로 흰 물보라
        by = math.floor(py)
        xs = [x for x, y in mask if y == max(yy for _, yy in mask)]
        for x in range(min(xs) - 1, max(xs) + 2):
            f[x, by] = WAKE[0] if min(xs) <= x <= max(xs) else WAKE[1]
        frames.append(f)
    return frames, (int(cx), int(cy))


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


def main() -> None:
    roles = sys.argv[1:] or list(ROLES)
    d = WIN / "art" / SID
    d.mkdir(parents=True, exist_ok=True)
    dol_arrow = S.read_art(old_art("arrow"))[0]
    arrow, _ = side("arrow")
    for rid in roles:
        src, hot, _ = S.read_art(old_art(rid))
        if rid == "wait":
            frames, hot = circle()
        elif rid == "move":
            frames, hot = swim_top()
        elif rid == "no":
            frames, hot = sign()
        elif rid in POSE:
            frames, _ = side(rid)
        elif rid in GLYPH:
            frames = []
            for k, (a, o) in enumerate(zip(dol_arrow, src)):
                g = {p: c for p, c in o.items() if a.get(p) != c}
                f = dict(arrow[k])
                for p, c in g.items():
                    if c[3] == 255 or p not in f:
                        f[p] = RECOLOR.get(c, c)
                frames.append(f)
        else:
            frames = [{p: RECOLOR.get(c, c) for p, c in f.items()} for f in src]
        (d / f"{rid}.txt").write_text(S.to_text(frames, hot, RATE), encoding="utf-8")
        print(f"{rid}: {len(frames)}장")


if __name__ == "__main__":
    main()

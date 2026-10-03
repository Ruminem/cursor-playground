# SPDX-License-Identifier: Apache-2.0
"""꽃게(crabanim) 구성표 그림 `art/crabanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/crab.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

앞에서 본 치비 꽃게 한 마리가 칸마다 그 칸의 뜻에 맞는 짓을 한다(`SCENE`). 다른 해양 애니와 달리 옛 그림이 없어
wait · move · no 까지 17칸을 다 그린다.
  화살표   큰 집게를 왼쪽 위로 번쩍 든다. 고정 집게발 끝이 핫스팟이고 움직이는 발만 딱딱 벌렸다 닫는다
  작업 중  작은 화살표 꽃게 + 오른쪽 아래에서 물방울 여덟 개가 고리로 돈다
  기다림   입에서 물방울을 뽀글뽀글 불어 올린다. 물방울은 양옆으로 번갈아 오르다 꼭대기에서 터진다
  이동     옆걸음으로 좌우를 오가며 통통 튀고, 네 방향 끝에 작은 화살촉
  좌우     두 집게를 좌우로 쭉 뻗고 옆걸음 — 집게 끝이 ↔ 의 화살촉이다
  위아래 · 대각선  디스코 춤 — 한 집게는 위(대각 위), 한 집게는 아래로 뻗고 그 축을 따라 몸을 까딱인다.
           위아래는 다리를 좌우 옆으로 들고 팔을 등딱지 가운데에서 내어 아래 집게와 다리가 안 엉킨다
  I빔     I 기둥을 두 집게로 붙잡고 오르내린다. 핫스팟은 기둥 가운데
  금지     빨간 고리 안에서 두 집게를 엇갈려 ✕ — 고개(몸)를 도리도리
  손      집게를 곧게 세워 콕 집는다. 위 끝이 핫스팟이고 집을 때 반짝인다
  도움말   작은 화살표 꽃게 + 물음표가 든 물방울
  펜      제 몸만 한 연필을 집게로 쥐고 물결 글씨를 쓴다. 연필심 끝(왼쪽 아래)이 핫스팟
  사람     작은 화살표 꽃게 + 갈색 머리 위에 꽃게(눈자루 · 집게까지 통째로)를 모자처럼 얹은 사람
  핀      작은 화살표 꽃게 + 파란 물방울 지도 핀, 핀 머리 동그라미 속에 꽃게 얼굴
  위      두 집게를 머리 위로 모아 ^ — 맞닿은 집게 끝이 핫스팟이다(만세)
  십자     가는 조준선 + 오른쪽 아래에서 눈자루를 세우고 집게를 든 채 과녁을 노려보는 꽃게(다리는 짧게)
거미로 읽히지 않게 다리는 한쪽에 셋만, 짧고 굵게 그린다. 주인공은 큰 집게와 눈자루 끝의 큰 눈이다.
색은 새우(분홍·주황)와 갈리게 빨강 쪽으로 가고, 배 쪽 테두리는 크림색이다.
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, QMARK, SIGN, SIGN_D, WAKE, bubble, disc, finish, glyph, hx, ink, line, phases, raster, solid, write

SID = "crabanim"

OUT, DEEP, RED, CORAL = hx("5a1010ff"), hx("b8301fff"), hx("e8492fff"), hx("ff7f50ff")
LIGHT, CREAM, CREAM_D = hx("ffb08aff"), hx("ffe9c4ff"), hx("f2c99aff")
BLUSH, WHITE, PUPIL, HI = hx("ffa3b4ff"), hx("ffffffff"), hx("1c0a0aff"), hx("fff6ecff")
ink(OUT, HI, hx("ffd6c8c7"))
SKIN, HAIR, SHIRT, SHIRT_D = hx("f2c9a0ff"), hx("4a3226ff"), hx("4a7fb5ff"), hx("2e5a88ff")
PENCIL, PENCIL_D, WOOD, LEAD = hx("f2c230ff"), hx("c8961cff"), hx("e9c9a0ff"), hx("3a3a3aff")
SAND = hx("e8d3a0ff")
PIN, PIN_L, PIN_D, PIN_W = hx("3d8fd6ff"), hx("7cc0f0ff"), hx("173c6eff"), hx("cfe8faff")   # 지도 핀 — 꽃게 빨강과 갈리게 파랑


def clip(f: dict) -> dict:
    """판(테 한 칸을 남긴 1–30) 밖을 자른다. 잘린 칸 수는 `CUT` 에 쌓아 main 이 칸마다 알린다"""
    CUT[0] += sum(1 for p in f if not (1 <= p[0] <= 30 and 1 <= p[1] <= 30))
    return {p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}


CUT = [0]


def blink(k: int) -> bool:
    return k == 9


def compose(layers: list) -> dict:
    """뒤 → 앞 차례의 조각들({칸: 색})을 겹쳐 테두리를 한 번에 긋는다. 덮인 칸은 앞 조각이 갖고, 바깥 둘레와
    앞 조각이 뒤 조각에 닿는 자리에만 선을 긋는다 — 조각마다 제 둘레를 다 그으면(`solid`) 2–3칸 굵기 다리·발가락이
    통째로 테두리색이 되어 꽃게가 거미처럼 검고 가늘어진다"""
    owner, col = {}, {}
    for i, lay in enumerate(layers):
        for p, c in lay.items():
            owner[p], col[p] = i, c
    out = {}
    for p, i in owner.items():
        x, y = p
        nb = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        out[p] = OUT if any(q not in owner or owner[q] < i for q in nb) else col[p]
    return out


def fill(cells, c) -> dict:
    return {p: (c(p) if callable(c) else c) for p in cells}


# ── 집게 ─────────────────────────────────────────────────────────────────────
# 집게 하나를 (따라 p, 가로 q) 로 그린다. 손바닥 가운데가 원점, p 가 끝 쪽, q 가 움직이는 발 쪽이다.
# 고정 발 끝 (TIP, 0) 이 집게 끝 — 핫스팟을 걸 자리라 벌렸다 닫아도 안 움직인다. 움직이는 발만 경첩 HINGE 에서 돈다.
# 두 발 안쪽 날을 바깥으로 휘어 닫아도 발 사이에 렌즈꼴 틈이 남게 한다 — 틈이 없으면 집게가 나뭇잎·불꽃으로 읽힌다
PALM = (3.1, 3.0)                         # 손바닥 타원 반지름 (따라 · 가로)
TIP = 7.3
FIXED = [(0.0, -3.0), (3.5, -3.0), (5.5, -2.4), (6.8, -1.3), (TIP, -0.1), (6.4, -0.3), (5.2, -1.0), (3.5, -0.7),
         (1.5, -0.3)]
MOVE = [(0.0, 3.0), (3.5, 3.0), (5.5, 2.4), (6.6, 1.4), (TIP - 0.3, 0.3), (6.2, 0.5), (5.0, 1.3), (3.5, 1.0),
        (1.5, 0.6)]
HINGE = (2.0, 1.5)


def claw_frame(tip, ang: float, sz: float, mv: int = 1):
    """집게 끝 tip(점) · 손바닥 → 끝 방향 ang(라디안, 화면 좌표) · 크기 → (local→world, world→local, 손바닥 가운데)"""
    ux, uy = math.cos(ang), math.sin(ang)
    nx, ny = -uy * mv, ux * mv
    cx, cy = tip[0] - TIP * sz * ux, tip[1] - TIP * sz * uy

    def w(p, q):
        return cx + (p * ux + q * nx) * sz, cy + (p * uy + q * ny) * sz

    def loc(x, y):
        dx, dy = x - cx, y - cy
        return (dx * ux + dy * uy) / sz, (dx * nx + dy * ny) / sz
    return w, loc, (cx, cy)


def claw(tip, ang: float, sz: float, open_: float = 0.0, mv: int = 1) -> list:
    """큰 집게 → 조각 둘(손바닥+고정 발, 움직이는 발). open_ 은 움직이는 발을 벌린 각(라디안).
    mv 는 움직이는 발이 끝을 볼 때 왼쪽(1)인지 오른쪽(-1)인지"""
    w, loc, _ = claw_frame(tip, ang, sz, mv)
    hp, hq = HINGE
    c, s = math.cos(open_), math.sin(open_)

    def rot(p, q):
        return hp + (p - hp) * c - (q - hq) * s, hq + (p - hp) * s + (q - hq) * c
    a, b = PALM
    palm = [(a * math.cos(t), b * math.sin(t)) for t in (2 * math.pi * i / 24 for i in range(24))]
    body = raster([w(*q) for q in palm]) | raster([w(*q) for q in FIXED])
    body.add(tuple(math.floor(v) for v in w(TIP - 0.2, -0.15)))
    finger = raster([w(*rot(*q)) for q in MOVE]) - body

    def col(p):   # 끝으로 갈수록 짙고, 손바닥 뒤쪽에 산호빛
        pp, qq = loc(p[0] + 0.5, p[1] + 0.5)
        if pp >= 5.3:
            return DEEP
        if pp < -0.6 and qq < 0.8:
            return CORAL
        return RED

    def col_m(p):
        pp, qq = loc(p[0] + 0.5, p[1] + 0.5)
        return DEEP if math.hypot(pp - hp, qq - hq) >= 3.6 else RED
    return [fill(body, col), fill(finger, col_m)]


def tip_cell(tip, ang, sz, mv=1) -> tuple:
    """고정 발 끝 칸 = 핫스팟 자리"""
    w, _, _ = claw_frame(tip, ang, sz, mv)
    return tuple(math.floor(v) for v in w(TIP - 0.2, -0.15))


# ── 몸 ───────────────────────────────────────────────────────────────────────
def crab(f: dict, cx: float, cy: float, s: float = 1.0, claws=(), ph: float = 0.0, shut: bool = False,
         look=(0, 0), walk: float = 1.0, mouth: str = "smile", stalk: float = 1.0, hug: bool = False,
         leg: float = 1.0, splay: float = 0.0, mid: bool = False) -> None:
    """앞에서 본 꽃게 한 마리를 f 에 얹는다. (cx, cy) 는 등딱지 가운데, s 는 크기(1 이면 등딱지 17×12칸).
    claws 는 [(끝 점, 각, 크기, 벌림, mv)] — 어깨에서 손바닥까지 굵은 팔을 잇고 집게는 맨 앞에 그린다.
    다리는 한쪽에 셋, 짧고 굵은 몽당다리. walk 는 걷는 발놀림 세기. look 은 눈동자를 미는 방향(-1–1),
    mouth 는 "smile" · "o"(물방울 부는 입) · "frown". stalk 는 눈자루 길이 배수.
    hug 면 팔을 반대쪽 어깨에서 내어 등딱지 앞에서 엇갈린다(✕). leg 는 다리 길이 배수,
    splay 는 다리를 옆으로 들어 올리는 각(라디안) — 아래로 뻗는 집게와 다리가 안 겹치게 할 때 쓴다.
    mid 면 팔을 어깨가 아니라 등딱지 가운데에서 낸다 — 집게를 곧게 위아래로 뻗을 때 팔이 배를 비스듬히 안 가른다"""
    rx, ry = 8.4 * s, 5.8 * s
    layers = []
    # 다리 — 등딱지 아래 양옆으로 셋씩 비스듬히. 한 발씩 번갈아 든다
    lw = max(1.0, 1.25 * s)
    for side in (-1, 1):
        for i, (root, out_) in enumerate(((0.05, 0.35), (0.45, 0.75), (0.85, 1.15))):
            lift = max(0.0, math.sin(ph * 2 + i * 2.1 + (side > 0) * math.pi)) * 1.2 * walk
            r0 = (cx + side * rx * math.cos(root) * 0.85, cy + ry * math.sin(root) * 0.85)
            out_ -= splay
            ft = (r0[0] + side * 3.6 * s * leg * math.cos(out_), r0[1] + 3.6 * s * leg * math.sin(out_) - lift)
            lm = {}
            line(lm, r0, ft, DEEP, lw)
            layers.append(fill(lm, DEEP))
    # 팔 — 어깨에서 손바닥까지
    arms = []
    for tip, ang, sz, _, mv in claws:
        _, _, (px, py) = claw_frame(tip, ang, sz, mv)
        sx = cx if mid else cx + (rx * 0.7 if (px > cx) != hug else -rx * 0.7)
        am = {}
        line(am, (sx, cy - ry * 0.1), (px, py), RED, max(0.7, 1.3 * s))
        arms.append(fill(am, RED))
    if not hug:
        layers += arms
    # 눈자루 — 등딱지 위로 짧게 솟은 가는 선
    er = 2.4 if s >= 0.75 else 1.6 if s >= 0.5 else 0
    eyes = []
    for side in (-1, 1):
        if er > 2:
            ex = math.floor(cx + side * rx * 0.36) + 0.5
        else:
            ex = round(cx + side * rx * 0.36)
        ey = cy - ry - max(er, 0.5) - (1.0 + 0.8 * s) * stalk + 0.5
        ey = math.floor(ey) + 0.5 if er > 2 else round(ey)   # 큰 눈은 칸 가운데, 가운데 눈은 칸 모서리에 맞춘다
        st = {}
        line(st, (math.floor(ex) + 0.5, cy - ry * 0.5), (math.floor(ex) + 0.5, ey), OUT)
        layers.append(st)
        eyes.append((ex, ey))
    # 등딱지 — 위는 빨강에 왼쪽 위 산호빛, 아래 테두리는 크림색 배
    shell = {(x, y) for y in range(math.floor(cy - ry) - 1, math.ceil(cy + ry) + 1)
             for x in range(math.floor(cx - rx) - 1, math.ceil(cx + rx) + 1)
             if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1}

    def col(p):
        dx, dy = (p[0] + 0.5 - cx) / rx, (p[1] + 0.5 - cy) / ry
        if dy > 0.5:
            return CREAM if dy < 0.78 or s < 0.7 else CREAM_D
        if s >= 0.7 and (dx + 0.5) ** 2 + (dy + 0.55) ** 2 < 0.06:
            return LIGHT
        if dy < -0.1 and dx < 0.1:
            return CORAL
        return RED
    layers.append(fill(shell, col))
    # 눈 — 흰자 큰 눈
    for side, (ex, ey) in zip((-1, 1), eyes):
        if er:
            layers.append(fill(disc(ex, ey, er), WHITE))
    if hug:
        layers += arms
    for cl in claws:
        layers += claw(*cl)
    g = compose(layers)
    # 눈동자 · 감은 눈
    for side, (ex, ey) in zip((-1, 1), eyes):
        if er > 2:   # 속 3×3 에 2×2 눈동자
            ix, iy = math.floor(ex), math.floor(ey)
            lx = look[0] if abs(look[0]) > 0.3 else -side   # 안 정하면 가운데로 몰린 눈
            px0 = ix - 1 if lx < 0 else ix
            py0 = iy - 1 if look[1] < -0.3 else iy
            cells = ((px0, py0), (px0 + 1, py0), (px0, py0 + 1), (px0 + 1, py0 + 1))
        elif er:     # 속 2×2 에 세로 눈동자 한 줄
            ix, iy = math.floor(ex), math.floor(ey)    # ex 는 칸 모서리 → 속은 ix-1, ix
            lx = look[0] if abs(look[0]) > 0.3 else -side
            px0 = ix if lx > 0 else ix - 1
            cells = ((px0, iy - 1), (px0, iy))
        else:        # 작은 꽃게: 자루 끝에 흰 칸 하나 + 눈동자 칸 하나
            ix, iy = math.floor(ex), math.floor(ey)
            g[ix, iy - 1] = WHITE
            g[ix, iy] = PUPIL
            cells = ()
        if shut and er:
            for q in list(g):
                if g[q] == WHITE and math.hypot(q[0] + 0.5 - ex, q[1] + 0.5 - ey) <= er:
                    g[q] = CORAL
            for q in cells:
                g[q] = CORAL
            iy = math.floor(ey)
            for dx in ((-1, 0, 1) if er > 2 else (-1, 0)):
                g[math.floor(ex) + dx, iy] = OUT
        else:
            for q in cells:
                g[q] = PUPIL
    # 얼굴 — 볼터치와 입
    mx, my = math.floor(cx), math.floor(cy + ry * 0.12)
    if s >= 0.6:
        for side in (-1, 1):
            bx = math.floor(cx + side * rx * 0.55)
            g[bx, my - 1] = g[bx - side, my - 1] = BLUSH
        if mouth == "o":
            for q in ((mx, my), (mx, my + 1), (mx - 1, my), (mx - 1, my + 1)):
                g[q] = OUT
        elif mouth == "frown":
            g[mx - 2, my + 1] = g[mx - 1, my] = g[mx, my] = g[mx + 1, my + 1] = OUT
        else:
            g[mx - 2, my] = g[mx - 1, my + 1] = g[mx, my + 1] = g[mx + 1, my] = OUT
    else:
        g[math.floor(cx - rx * 0.55), my - 1] = BLUSH
        g[math.floor(cx + rx * 0.55), my - 1] = BLUSH
        g[mx, my] = OUT
    f.update(g)


def snap(ph: float, wide: float = 0.6, twice: bool = True) -> float:
    """집게 벌림 — 한 바퀴에 두 번(twice) 딱딱"""
    v = math.sin(ph * (2 if twice else 1))
    return wide * max(0.0, v)


# ── 화살표 꽃게: 큰 집게를 왼쪽 위로 번쩍 ────────────────────────────────────────────
TIP0 = (2.1, 2.1)
UL = math.radians(-120)   # 대각선보다 조금 세운다 — 움직이는 발이 오른쪽(판 안)으로 벌어지게


def arrow_crab(ph: float, s: float = 1.0, k: int = 0) -> dict:
    """화살표 꽃게. 왼쪽 위 집게의 고정 발 끝이 (1, 1) — 핫스팟이다. s 를 줄이면 장면 곁의 작은 꽃게"""
    f = {}

    def at(x, y):
        return TIP0[0] + (x - TIP0[0]) * s, TIP0[1] + (y - TIP0[1]) * s
    cx, cy = at(19.0, 19.5)
    bob = 0.4 * math.sin(ph * 2) * s
    crab(f, cx, cy + bob, s, claws=[
        (TIP0, UL, 1.2 * s, snap(ph, 0.55), 1),
        (at(28.5, 9.5), math.radians(-70), 0.75 * s, snap(ph + 1.2, 0.5), 1),
    ], ph=ph, shut=blink(k), look=(-1, -1))
    return clip(f)


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    return [finish(arrow_crab(ph, 1.0, k)) for k, ph in enumerate(phases())]


MINI = 0.62


def busy() -> list[dict]:
    """작은 화살표 꽃게 + 오른쪽 아래에서 물방울 여덟 개가 고리로 돈다. 맨 앞 것이 크고 뒤로 갈수록 작다"""
    frames = []
    cx, cy, R = 22.5, 22.5, 6.0
    for k, ph in enumerate(phases()):
        f = {}
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            lag = (k * 8 / N - i) % 8                # 0 이 맨 앞
            r = 1.9 - 0.16 * lag
            if r < 0.7:
                continue
            bubble(f, cx + R * math.cos(a), cy + R * math.sin(a), r)
        f.update(arrow_crab(ph, MINI, k))
        frames.append(finish(clip(f)))
    return frames


def wait() -> list[dict]:
    """입을 오므려 물방울을 뽀글뽀글 분다 — 양옆으로 번갈아 오르다 꼭대기에서 터진다"""
    frames = []
    cx, cy = 15.5, 18.5
    for k, ph in enumerate(phases()):
        f = {}
        crab(f, cx, cy, 0.75, claws=[
            ((3.0, 22.0), math.radians(-150), 0.6, snap(ph, 0.5, False), 1),
            ((28.0, 22.0), math.radians(-30), 0.6, snap(ph + math.pi, 0.5, False), -1),
        ], ph=ph, walk=0.0, shut=blink(k), mouth="o")
        for j in range(4):   # 입에서 나와 옆으로 퍼지며 오른다 — 눈자루 바깥으로 돌아 꼭대기에서 터진다
            t = (k / N + j / 4) % 1
            side = 1 if j % 2 else -1
            bx = cx + side * (0.5 + 8.5 * (1 - (1 - min(1.0, t * 1.6)) ** 2))
            by = cy + 1.5 - 17 * t
            if t < 0.85:
                bubble(f, bx, by, 1.0 + 1.5 * t)
            else:   # 펑 — 네 갈래 물보라
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    f[math.floor(bx + dx * 2.5), math.floor(by + dy * 2.5)] = WAKE[1]
        frames.append(finish(clip(f)))
    return frames


def arrowhead(f: dict, x: float, y: float, d) -> None:
    """작은 화살촉 (d 쪽을 가리킴)"""
    dx, dy = d
    px, py = -dy, dx
    solid(f, raster([(x + dx * 2.6, y + dy * 2.6), (x + px * 2.6, y + py * 2.6), (x - px * 2.6, y - py * 2.6)], 7),
          CREAM)


def move() -> list[dict]:
    """옆걸음으로 좌우를 오가며 통통 튄다. 네 방향 끝에 작은 화살촉"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for d, (x, y) in (((0, -1), (15.5, 3.2)), ((0, 1), (15.5, 28.6)), ((-1, 0), (3.2, 15.5)),
                          ((1, 0), (28.6, 15.5))):
            arrowhead(f, x, y, d)
        dx = 2.0 * math.sin(ph)
        dy = -abs(math.sin(ph * 2)) * 1.0
        cx, cy = 15.5 + dx, 16.5 + dy
        crab(f, cx, cy, 0.72, claws=[
            ((cx - 9.5, cy - 6.0), math.radians(-115), 0.6, snap(ph, 0.5), 1),
            ((cx + 9.5, cy - 6.0), math.radians(-65), 0.6, snap(ph + math.pi, 0.5), -1),
        ], ph=ph * 2, shut=blink(k), look=(1 if math.cos(ph) > 0 else -1, 0))
        frames.append(finish(clip(f)))
    return frames


def we() -> list[dict]:
    """두 집게를 좌우로 쭉 뻗고 옆걸음 — 집게 끝이 ↔ 의 화살촉"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        dx = round(1.5 * math.sin(ph))
        cx, cy = 15.5 + dx, 17.5
        crab(f, cx, cy, 0.72, claws=[
            ((3.1 + dx, 15.0), math.pi, 0.7, snap(ph, 0.5), -1),
            ((28.9 + dx, 15.0), 0.0, 0.7, snap(ph + math.pi, 0.5), 1),
        ], ph=ph * 2, shut=blink(k), look=(1 if math.cos(ph) > 0 else -1, 0))
        frames.append(finish(clip(f)))
    return frames


def disco(axis: float, hot=(15, 15), splay: float = 0.0, leg: float = 1.0, mid: bool = False) -> list[dict]:
    """디스코 춤: 한 집게는 axis 쪽(위·대각 위), 한 집게는 반대쪽으로 뻗고 몸을 그 축을 따라 까딱인다.
    axis 는 위로 뻗는 집게의 각(라디안, 화면 좌표). splay · leg · mid 는 `crab` 에 그대로 넘긴다"""
    frames = []
    ux, uy = math.cos(axis), math.sin(axis)
    for k, ph in enumerate(phases()):
        f = {}
        b = 1.0 * math.sin(ph)
        cx, cy = 15.5 + ux * b, 16.5 + uy * b
        reach = 14.2
        crab(f, cx, cy, 0.66, claws=[
            ((15.5 + ux * reach, 15.5 + uy * reach), axis, 0.62, snap(ph, 0.5), 1),
            ((15.5 - ux * reach, 15.5 - uy * reach), axis + math.pi, 0.62, snap(ph + math.pi, 0.5), 1),
        ], ph=ph, walk=0.4, shut=blink(k), look=(ux, uy), splay=splay, leg=leg, mid=mid)
        frames.append(finish(clip(f)))
    return frames


def ns() -> list[dict]:
    """다리를 좌우 옆으로 들어 아래 집게 팔과 안 엉키게 한다 — 집게만 위아래로 가야 ↕ 로 읽힌다"""
    return disco(math.radians(-90), splay=0.75, leg=1.15, mid=True)


def nwse() -> list[dict]:
    return disco(math.radians(-135))


def nesw() -> list[dict]:
    return disco(math.radians(-45))


def ibeam() -> list[dict]:
    """I 기둥을 두 집게로 붙잡고 오르내리는 꽃게 — 기둥 가운데가 핫스팟"""
    frames = []
    X = 15
    for k, ph in enumerate(phases()):
        f = {}
        for y in range(3, 29):
            f[X, y] = OUT
        for x in range(X - 3, X + 4):
            f[x, 3] = f[x, 28] = OUT
        cy = 15.5 + 6.0 * math.sin(ph)
        crab(f, X + 8.5, cy + 1.5, 0.5, claws=[
            ((X + 0.5, cy - 3.5), math.radians(180), 0.45, 0.0, 1),
            ((X + 0.5, cy + 3.0), math.radians(165), 0.45, 0.0, -1),
        ], ph=ph * 2, walk=0.6, shut=blink(k), look=(-1, 0))
        f[X, 15] = OUT
        frames.append(finish(clip(f)))
    return frames


def no() -> list[dict]:
    """빨간 고리 안에서 두 집게를 엇갈려 ✕ — 몸을 도리도리 흔든다"""
    frames = []
    cx0, cy0, ro, ri = 15.5, 15.5, 14.0, 11.2
    ring = {(x, y) for y in range(32) for x in range(32) if ri <= math.hypot(x + 0.5 - cx0, y + 0.5 - cy0) <= ro}
    for k, ph in enumerate(phases()):
        f = {}
        solid(f, ring, SIGN, SIGN_D)
        sh = round(1.0 * math.sin(ph * 2))
        cx, cy = cx0 + sh, 18.5
        crab(f, cx, cy, 0.62, claws=[
            ((cx + 9.0, cy - 8.0), math.radians(-40), 0.6, 0.0, -1),
            ((cx - 9.0, cy - 8.0), math.radians(-140), 0.6, 0.0, 1),
        ], ph=ph, walk=0.3, mouth="frown", shut=blink(k), hug=True)
        frames.append(finish(clip(f)))
    return frames


def hand() -> list[dict]:
    """집게를 곧게 세워 콕 집는다 — 위 끝이 핫스팟. 집을 때마다 끝에 반짝"""
    frames = []
    T = HAND_TIP
    for k, ph in enumerate(phases()):
        f = {}
        op = 0.55 if k % 6 < 3 else 0.0
        crab(f, 17.5, 23.0, 0.66, claws=[
            (T, -math.pi / 2, 1.0, op, 1),
            ((29.5, 17.0 + round(math.sin(ph))), math.radians(-40), 0.55, snap(ph, 0.5), -1),
        ], ph=ph, walk=0.3, shut=blink(k), look=(-1, -1))
        if k % 6 == 3:   # 딱 — 집은 끝에 반짝
            for dx, dy in ((2, -0), (2, 2), (-1, 2)):
                f[math.floor(T[0]) + dx + 1, math.floor(T[1]) + dy] = HI
        frames.append(finish(clip(f)))
    return frames


def help_() -> list[dict]:
    """작은 화살표 꽃게 + 물음표가 든 물방울이 둥실 뜬다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        dy = round(1.2 * math.sin(ph))
        cx, cy = 22.5, 22.5 + dy
        bubble(f, cx, cy, 6.0)
        glyph(f, QMARK, math.floor(cx) - 2, math.floor(cy) - 3, DEEP)
        f.update(arrow_crab(ph, MINI, k))
        frames.append(finish(clip(f)))
    return frames


def pen() -> list[dict]:
    """제 몸만 한 연필을 집게로 쥐고 물결 글씨를 쓴다 — 연필심 끝이 핫스팟"""
    frames = []
    ax, ay = 1.5, 29.5
    ux, uy = math.sqrt(0.5), -math.sqrt(0.5)
    for k, ph in enumerate(phases()):
        f = {}
        n = 3 + round(k * 25 / (N - 1))
        prev = None
        for x in range(3, n + 1):
            cur = (x + 0.5, 29.5 + 1.0 * math.sin((x - 3) * 0.9))
            if prev:
                line(f, prev, cur, LEAD)
            prev = cur
        for y in range(8, 31):
            for x in range(0, 20):
                qx, qy = x + 0.5 - ax, y + 0.5 - ay
                s = qx * ux + qy * uy
                w = abs(-qx * uy + qy * ux)
                half = 1.7 if s > 4 else 0.4 + 1.3 * s / 4
                if 0 <= s <= 17 and w <= half:
                    f[x, y] = (LEAD if s < 1.6 else WOOD if s < 4 else
                               (OUT if w > half - 0.6 else PENCIL if w < 0.6 else PENCIL_D) if s < 14 else
                               BLUSH)
        wig = 0.6 * math.sin(ph * 2)
        crab(f, 21.5, 13.0 + wig * 0.5, 0.6, claws=[
            ((8.5 + wig, 17.5), math.radians(150), 0.55, 0.0, 1),
            ((13.0 + wig, 25.0), math.radians(120), 0.5, 0.0, -1),
        ], ph=ph * 2, walk=0.5, shut=blink(k), look=(-1, 1))
        frames.append(finish(clip(f)))
    return frames


def person() -> list[dict]:
    """머리에 꽃게를 모자처럼 얹은 사람 — 꽃게가 집게를 딱딱. 꽃게는 얼굴 뒤가 아니라 머리털 위에 앉는다.
    처음엔 얼굴 뒤에 꽃게를 숨겨 등딱지 윗부분과 집게만 보였는데 빨간 머리털 · 왕관으로 읽혀서,
    꽃게를 키워 통째로(눈자루 · 큰 눈 · 크림색 배까지) 갈색 머리 위에 얹고 다리는 뺐다"""
    frames = []
    hx_, hy, hr = 25.0, 24.8, 3.7
    for k, ph in enumerate(phases()):
        f = {}
        solid(f, raster([(18.4, 30.9), (19.2, 28.8), (21.4, 27.6), (28.6, 27.6), (30.8, 28.8), (31.2, 30.9)]),
              lambda p: SHIRT if p[0] < 25 else SHIRT_D)
        solid(f, disc(hx_, hy, hr), lambda p: HAIR if p[1] + 0.5 < hy - 0.2 else SKIN)
        ey = math.floor(hy) + 1
        f[math.floor(hx_) - 2, ey] = f[math.floor(hx_) + 1, ey] = OUT
        f[math.floor(hx_) - 3, ey + 1] = f[math.floor(hx_) + 2, ey + 1] = BLUSH
        bob = round(0.6 * math.sin(ph))
        ccx, ccy = hx_, 19.6 + bob
        crab(f, ccx, ccy, 0.56, claws=[   # 팔 없이 등딱지 어깨에 바로 붙은 집게 — 팔이 길면 테두리색 막대만 남는다
            ((ccx - 6.0, ccy - 4.4), math.radians(-130), 0.46, snap(ph, 0.6), 1),
            ((ccx + 6.0, ccy - 4.4), math.radians(-50), 0.46, snap(ph + math.pi, 0.6), -1),
        ], ph=ph, walk=0.0, shut=blink(k), leg=0.0, stalk=0.8)
        f.update(arrow_crab(ph, MINI, k))
        frames.append(finish(clip(f)))
    return frames


def pin() -> list[dict]:
    """파란 물방울 지도 핀 + 핀 머리 옅은 동그라미 속 꽃게 얼굴(눈자루 · 큰 눈) — 핀이 통통 튄다.
    처음엔 꽃게 밑에 가는 바늘만 꽂았는데 막대사탕으로 읽혀서 해달 핀처럼 물방울꼴 핀을 그렸다.
    꽃게가 빨강이라 빨간 핀이면 묻혀서 핀은 파랑이다. 동그라미 속을 흰색으로 하면 흰 눈이 묻혀 옅은 파랑이고,
    집게까지 넣으면 팔 · 집게가 테두리색 덩어리가 되어 얼굴만 넣었다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        dy = -round(2 * math.sin(math.pi * k / N))
        cx, cy = 24.0, 16.0 + dy
        for x in range(21, 28):   # 그림자 — 핀이 높을수록 옅게
            f[x, 30] = WAKE[3] if dy else WAKE[2]
        drop = disc(cx, cy, 6.9) | raster([(cx - 5.4, cy + 3.9), (cx + 5.4, cy + 3.9), (cx, cy + 13.4)])
        solid(f, drop, lambda p: PIN_L if (p[0] + 0.5 - cx) + (p[1] + 0.5 - cy) < -7.0 else PIN, PIN_D)
        solid(f, disc(cx, cy, 5.2), PIN_W, PIN_D)
        crab(f, cx, cy + 1.8, 0.56, ph=ph, walk=0.0, shut=blink(k), leg=0.0, stalk=0.7)
        f.update(arrow_crab(ph, MINI, k))
        frames.append(finish(clip(f)))
    return frames


def up() -> list[dict]:
    """만세 — 두 집게를 번쩍 들고 통통 뛴다. 더 높이 든 왼쪽 집게 끝이 핫스팟이라 그 끝은 안 움직이고,
    오른쪽 집게는 흔든다. 두 집게 끝을 머리 위 한 점에 모은 ^ 는 팔이 기둥처럼 서서 상자에 갇힌 꽃게로 읽혔다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        hop = -abs(math.sin(ph)) * 1.5
        wave = 1.5 * math.sin(ph * 2)
        crab(f, 15.5, 21.0 + hop, 0.75, claws=[
            (UP_TIP, UP_ANG, 0.75, snap(ph, 0.5), 1),
            ((25.0, 5.0 + wave), math.radians(-60), 0.7, snap(ph + math.pi, 0.5), -1),
        ], ph=ph * 2, shut=blink(k), look=(-1, -1))
        frames.append(finish(clip(f)))
    return frames


UP_TIP, UP_ANG = (10.1, 1.6), math.radians(-100)
HAND_TIP = (8.5, 1.6)


def cross() -> list[dict]:
    """가는 조준선 + 오른쪽 아래에서 눈자루를 세우고 과녁(왼쪽 위)을 노려보는 꽃게"""
    frames = []
    C = (15, 15)
    for k, ph in enumerate(phases()):
        f = {}
        for d in range(3, 15):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                f[C[0] + dx * d, C[1] + dy * d] = DEEP
        r = 4.5 + 1.0 * math.sin(ph)
        for i in range(24):
            a = 2 * math.pi * i / 24
            p = (math.floor(C[0] + 0.5 + r * math.cos(a)), math.floor(C[1] + 0.5 + r * math.sin(a)))
            if p[0] != C[0] and p[1] != C[1]:
                f[p] = CORAL
        crab(f, 23.5, 25.0, 0.5, claws=[   # 눈자루 · 큰 눈 · 집게가 읽히게 키우고 다리는 짧게 — 작으면 거미로 읽혔다
            ((16.4, 19.4), math.radians(-125), 0.5, snap(ph, 0.6), 1),
            ((30.6, 19.4), math.radians(-55), 0.5, snap(ph + math.pi, 0.6), -1),
        ], ph=ph, walk=0.0, shut=blink(k), stalk=1.2, leg=0.6, look=(-1, -1))
        f[C] = OUT
        frames.append(finish(clip(f)))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "wait": wait, "move": move, "we": we, "ns": ns, "nwse": nwse,
         "nesw": nesw, "ibeam": ibeam, "no": no, "hand": hand, "help": help_, "pen": pen, "person": person,
         "pin": pin, "up": up, "cross": cross}
_AH, _MH = tip_cell(TIP0, UL, 1.2), tip_cell(TIP0, UL, 1.2 * MINI)   # 화살표 꽃게 · 작은 꽃게의 집게 끝
HOT = {"arrow": _AH, "busy": _MH, "help": _MH, "person": _MH, "pin": _MH,
       "wait": (15, 15), "move": (15, 15), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "ibeam": (15, 15), "no": (15, 15), "hand": tip_cell(HAND_TIP, -math.pi / 2, 1.0), "pen": (1, 29), "up": tip_cell(UP_TIP, UP_ANG, 0.75), "cross": (15, 15)}


def main() -> None:
    def scene(r):
        CUT[0] = 0
        frames = SCENE[r]()
        if CUT[0]:
            print(f"{r}: 판 밖으로 {CUT[0]}칸 잘림 — 자리나 크기를 줄일 것")
        hot = HOT[r]
        miss = [i for i, fr in enumerate(frames) if fr.get(hot, (0, 0, 0, 0))[3] != 255]
        if miss:
            print(f"{r}: 핫스팟 {hot} 이 불투명하지 않은 장 {miss}")
        return frames, hot
    write(SID, {r: (lambda r=r: scene(r)) for r in SCENE}, sys.argv[1:] or None)


if __name__ == "__main__":
    main()

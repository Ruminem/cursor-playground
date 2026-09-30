# SPDX-License-Identifier: Apache-2.0
"""괴상어(catsharkanim) 구성표 그림 `art/catsharkanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/catshark.py [역할...]     그림을 쓴다 (역할을 안 주면 새로 그리는 칸 전부)

첫 벌(2026-09-24)은 괴상어 무늬를 입힌 화살표·양방향 화살표라 복제품 같다는 말을 들었다(2026-10-01 사용자).
그래서 칸마다 괴상어가 사는 장면을 따로 그린다(`SCENE`) — 낮에는 바닥에서 자는 밤 사냥꾼이라 조는 괴상어(작업 중) ·
다시마 물음표(도움말) · 스쿠버 다이버(사람) · 모래에 박힌 닻(핀) · 바닥을 기듯 꿈틀대기(좌우) · 다시마 줄기 타고
오르기(위아래) · 바위 틈에서 나오기와 굴로 들어가기(대각선) · 모래에서 고개 내민 앞얼굴(위) · 주둥이로 모래에 물결 긋기(펜) ·
고양이처럼 손에 몸 비비기(손) · 고양이 눈 조준(십자) · 알집 '인어의 지갑'(I빔).
wait(옆으로 헤엄치는 괴상어) · move · no(몸을 만 괴상어와 빗금)는 두고 안 그린다.
다른 상어와 가르는 것: 가늘고 긴 몸을 뱀장어처럼 S 자로 흔든다(`wave`) · 등지느러미 둘이 몸 뒤쪽에 · 꼬리는 길고 낮다 ·
연갈색 바탕에 짙은 안장 무늬 · 노란 고양이 눈.
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import dataclasses
import math
import sys

from sea import (N, QMARK, SIGN, Body, bubble, crop, disc, edge, finish, glyph, hand_at, hx, ink, line, phases,
                 raster, side, solid, write)

SID = "catsharkanim"
ARROW = ((1, 2), (19, 24))   # 화살표 괴상어의 주둥이 끝(핫스팟) · 꼬리 끝

# 옛 그림의 색을 그대로 쓴다
OUT, DARK, MID, LIGHT = hx("1c130bff"), hx("30180aff"), hx("a88452ff"), hx("c8a26aff")
PALE, BELLY, HI = hx("e6cd9aff"), hx("f0e4c8ff"), hx("fbf5e6ff")
EYE, GLINT = hx("d8c040ff"), hx("c4f4f0ff")
ink(OUT, HI, hx("f4e8cec7"))
SAND, SAND_D = hx("e8d3a0ff"), hx("c4a86cff")
KELP, KELP_D = hx("7a9a3aff"), hx("41602aff")
IRON, IRON_D = hx("7d8790ff"), hx("3c444cff")
ROPE = hx("d9b77aff")
ROCK, ROCK_D = hx("8a8279ff"), hx("5a534cff")
CAVE = hx("2a2320ff")
SKIN = hx("f2c9a0ff")
SUIT, TANK, GLASS = hx("2d3640ff"), hx("f2c230ff"), hx("9ed8eaff")
CASE, CASE_D, YOLK = hx("b8913fff"), hx("7a5a22ff"), hx("f2c230ff")
HEART = hx("e8506aff")

# ── 옆모습 괴상어: 주둥이 s=0 → 꼬리 끝 s=1 ─────────────────────────────────────
# 가늘고 긴 통. 머리는 납작하고 둥글다. 등지느러미 둘이 몸 뒤쪽, 꼬리는 길고 낮게 뻗는다
TOP = [(0, 0), (0.02, 0.024), (0.05, 0.04), (0.1, 0.052), (0.2, 0.06), (0.35, 0.062), (0.5, 0.055), (0.62, 0.044),
       (0.72, 0.032), (0.85, 0.022), (0.95, 0.014), (1.0, 0.0)]
BOT = [(0, 0), (0.02, -0.02), (0.05, -0.034), (0.1, -0.044), (0.2, -0.052), (0.35, -0.055), (0.5, -0.048),
       (0.6, -0.038), (0.7, -0.027), (0.85, -0.018), (1.0, 0.0)]
FINS = {
    "pectoral": [(0.15, -0.035), (0.19, -0.085), (0.235, -0.1), (0.25, -0.075), (0.24, -0.04)],
    "dorsal": [(0.48, 0.045), (0.52, 0.095), (0.555, 0.1), (0.565, 0.065), (0.59, 0.044)],
    "dorsal2": [(0.63, 0.036), (0.66, 0.075), (0.69, 0.078), (0.7, 0.05), (0.72, 0.03)],
    "anal": [(0.58, -0.036), (0.61, -0.07), (0.65, -0.072), (0.66, -0.03)],
    "caudal": [(0.74, -0.024), (0.82, -0.06), (0.92, -0.066), (0.99, -0.03), (1.0, 0.0), (0.92, 0.028),
               (0.82, 0.026)],
}
WAVE = 0.04               # 몸이 S 자로 흔들리는 폭 (몸길이 단위, 두께 배율 전). 꼬리로 갈수록 커진다


def wave(s: float, ph: float) -> float:
    """뱀장어처럼 몸 전체에 물결이 머리에서 꼬리로 흐른다 — 주둥이 끝은 안 움직여 핫스팟이 떨리지 않는다"""
    return WAVE * math.sin(2 * math.pi * 1.1 * s - ph) * s


SADDLES = (0.14, 0.28, 0.42, 0.56, 0.7, 0.84)   # 짙은 안장 무늬 자리


def skin(s, v, top, bot):
    """연갈색 등에 짙은 안장 무늬, 옅은 점, 흰 배"""
    sep = bot + 0.35 * (top - bot)
    if v < sep:
        return BELLY if v > bot + 0.3 * (sep - bot) else PALE
    d = min(abs(s - c) for c in SADDLES)
    if d < 0.038 and v > sep + 0.15 * (top - sep):
        return DARK if d < 0.024 else MID
    return LIGHT


def decorate(c, closed: bool = False) -> None:
    """노란 고양이 눈(세로 동공) · 입 · 옅은 점 · 몸 위로 지나가는 빛 물결"""
    for p in c.mask:
        if c.out.get(p) != LIGHT or c.region.get(p) != "body":
            continue
        s, v = c.sv(p)
        i, j = round(s * c.L), round(v * c.L * c.T)
        if 0.1 < s < 0.8 and (i * 2 + j * 3) % 7 == 0:
            c.out[p] = PALE
    e, e2 = c.at(0.055, 0.014), c.at(0.055 + 1.0 / c.L, 0.014)
    if closed:
        c.paint(e, OUT)
    else:
        c.paint(e, EYE)
        c.paint(e2, OUT)
    if c.detail:
        for s in (0.02, 0.04, 0.06):
            c.paint(c.at(s, -0.016), MID)
    x0 = -0.15 + 1.2 * (c.ph / (2 * math.pi))
    for p in c.mask:
        if c.region.get(p) != "body" or c.out.get(p) != LIGHT:
            continue
        s, v = c.sv(p)
        if abs(s - x0 - 0.9 * v) * c.L < 0.7:
            c.out[p] = GLINT


CAT = Body(
    top=TOP, bot=BOT, fins=FINS, order=("pectoral", "body", "dorsal", "dorsal2", "anal", "caudal"),
    skin=skin, fin_ink=lambda r, s, v: MID if r in ("pectoral", "anal") else LIGHT if r == "caudal" else MID,
    bend=lambda s, v, ph: (s, v + wave(s, ph)), unbend=lambda s, v, ph: (s, v - wave(s, ph)),
    decorate=decorate, thick=1.7, length=1.05, small=("anal", "dorsal2"), lined=("pectoral",))
SLEEPY = dataclasses.replace(CAT, decorate=lambda c: decorate(c, closed=True))


def cat(head, tail, ph, size=None, flip=False, detail=True, body=CAT):
    """자세 하나 × 위상 하나 → ({좌표: 색}, 몸 칸 집합). 판 밖은 자른다"""
    return crop(*side(body, head, tail, ph, size, 0.0, flip, detail))


def arrow_cat(ph: float, size: float = 1.05, body=CAT) -> dict:
    return cat(*ARROW, ph, size, detail=size >= 1.05, body=body)[0]


# ── 소품 ─────────────────────────────────────────────────────────────────────
def sand(f: dict, x0: int, x1: int, y: int) -> None:
    for x in range(x0, x1 + 1):
        f[x, y] = SAND
        f[x, y + 1] = SAND_D if x % 3 else SAND


def puff(f: dict, x: float, y: float, k: int, n: int = 2) -> None:
    """모래 먼지가 양옆으로 피어오른다"""
    for j in range(n):
        t = (k / N + j / n) % 1
        for sgn in (-1, 1):
            q = (math.floor(x + sgn * (1.0 + 3 * t)), math.floor(y - 2.5 * t))
            if 1 <= q[0] <= 30:
                f.setdefault(q, SAND if t < 0.6 else SAND_D)


def kelp(f: dict, x: float, y0: int, y1: int, ph: float) -> None:
    """y1(바닥)에서 y0 로 선 다시마 줄기 — 위로 갈수록 크게 흔들리고 잎이 번갈아 난다"""
    for y in range(y0, y1 + 1):
        t = (y1 - y) / max(1, y1 - y0)
        cx = x + 1.5 * t * math.sin(ph + 2.5 * t)
        f[math.floor(cx), y] = KELP_D
        f[math.floor(cx) + 1, y] = KELP
        if (y - y0) % 5 == 2:
            sgn = 1 if (y // 5) % 2 else -1
            for d in (1, 2):
                f[math.floor(cx) + (1 if sgn > 0 else 0) + sgn * d, y - d + 1] = KELP


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    return [finish(arrow_cat(ph)) for ph in phases()]


Z3 = ["###", ".#.", "###"]
Z4 = ["####", "..#.", ".#..", "####"]
Z5 = ["#####", "...#.", "..#..", ".#...", "#####"]
ZZZ = ((Z3, 16, 12, range(N)), (Z4, 20, 7, range(3, 12)), (Z5, 25, 1, range(5, 12)))


def busy() -> list[dict]:
    """낮에는 바닥에서 자는 밤 사냥꾼 — 눈을 감은 괴상어 곁에 z · z · Z 가 차례로 떠오른다.
    z 는 자리를 옮기지 않고 켜졌다 꺼진다 — 매끈한 모양은 이 칸에서 화살표를 뺀 것을 기호로 떼어 쓰는데,
    절반 넘게 켜진 자리에서 멀리 떠다니는 칸은 화살표 무늬가 샌 것으로 본다(`test_light.py`)"""
    frames = []
    for k, ph in enumerate(phases()):
        f = arrow_cat(0.6 * math.sin(ph), 0.74, SLEEPY)   # 자면서 몸을 살짝만 뒤척인다
        for g, x, y, on in ZZZ:
            if k in on:
                glyph(f, g, x, y + round(0.6 * math.sin(ph + x)), DARK)
        frames.append(finish(f))
    return frames


def help_() -> list[dict]:
    """다시마로 자란 물음표가 물살에 흔들린다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = arrow_cat(ph, 0.74)
        core = set()
        for j, row in enumerate(QMARK):
            dx = round(0.9 * math.sin(ph - j * 0.45) * (6 - j) / 6)
            for i, ch in enumerate(row):
                if ch == "#":
                    core |= {(17 + 2 * i + a + dx, 13 + 2 * j + b) for a in (0, 1) for b in (0, 1)}
        solid(f, core | {(x + 1, y) for x, y in core}, lambda p: KELP if (p[0] + p[1]) % 4 else KELP_D, KELP_D)
        frames.append(finish(f))
    return frames


def person() -> list[dict]:
    """곁에 선 스쿠버 다이버 — 공기통을 메고 숨 쉴 때마다 거품이 오른다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        cx, cy = 23.5, 13.5 + round(0.6 * math.sin(ph))
        kick = 1.5 * math.sin(2 * ph)
        solid(f, raster([(cx + 2.6, cy + 2), (cx + 5.2, cy + 2), (cx + 5.2, cy + 11), (cx + 2.6, cy + 11)]), TANK)
        solid(f, raster([(cx - 3.2, cy + 2.5), (cx + 3.2, cy + 2.5), (cx + 2.6, cy + 11.5), (cx - 2.6, cy + 11.5)]),
              SUIT)
        for sgn in (-1, 1):   # 다리와 물갈퀴
            fx = cx + sgn * 1.4 + (kick if sgn > 0 else -kick) * 0.4
            line(f, (cx + sgn * 1.4, cy + 11), (fx, cy + 15), SUIT, 0.7)
            line(f, (fx - 1, cy + 16), (fx + 1, cy + 16), TANK, 0.5)
        line(f, (cx - 2.8, cy + 3.5), (cx - 6.0, cy + 7.5 + 0.8 * math.sin(ph)), SUIT, 0.7)   # 손 흔드는 팔
        solid(f, disc(cx, cy, 3.1), SKIN)
        for x in range(math.floor(cx) - 2, math.floor(cx) + 2):   # 물안경
            f[x, math.floor(cy) - 1] = GLASS
        f[math.floor(cx) - 3, math.floor(cy) - 1] = OUT
        f[math.floor(cx) - 1, math.floor(cy) + 1] = OUT   # 호흡기
        for j in range(3):
            t = (k / N + j / 3) % 1
            bubble(f, cx - 3 + 0.8 * math.sin(ph + j * 2), cy - 3 - 9 * t, 0.6 + 0.6 * t)
        f.update(arrow_cat(ph, 0.74))
        frames.append(finish(f))
    return frames


def pin() -> list[dict]:
    """모래에 박힌 닻 — 밧줄이 물살에 너울거린다. 여기가 괴상어 집"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        cx, by = 22.5, 28
        for y in range(3, 12):   # 밧줄: 위에서 고리까지
            t = (y - 3) / 9
            f[math.floor(cx + 1.8 * math.sin(ph + y * 0.6) * (1 - t)), y] = ROPE
        solid(f, disc(cx, 13.5, 2.0), IRON, IRON_D)
        f[math.floor(cx), 13] = f[math.floor(cx), 14] = OUT
        solid(f, raster([(cx - 1.1, 15), (cx + 1.1, 15), (cx + 1.1, by - 1), (cx - 1.1, by - 1)], 6), IRON, IRON_D)
        solid(f, raster([(cx - 5, 17), (cx + 5, 17), (cx + 5, 18.6), (cx - 5, 18.6)], 6), IRON, IRON_D)
        arms = set()
        for i in range(24):   # 아래로 휜 팔
            a = math.pi * (0.1 + 0.8 * i / 23)
            arms |= disc(cx + 6.5 * math.cos(a), by - 6.5 - 0.5 + 6.5 * math.sin(a) * 0.9 + 0.2, 1.0)
        arms |= raster([(cx - 7.5, by - 4.5), (cx - 4.5, by - 7.5), (cx - 5.2, by - 3.5)], 6)
        arms |= raster([(cx + 7.5, by - 4.5), (cx + 4.5, by - 7.5), (cx + 5.2, by - 3.5)], 6)
        solid(f, {p for p in arms if p[1] < by}, IRON, IRON_D)
        sand(f, 12, 30, by)
        f.update(arrow_cat(ph, 0.74))
        frames.append(finish(f))
    return frames


def we() -> list[dict]:
    """바닥을 기듯 S 자로 꿈틀대며 왼쪽으로 간다 — 꼬리가 모래를 쓸어 먼지가 인다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sand(f, 1, 30, 25)
        puff(f, 27.5, 24.0, k)
        f.update(cat((1, 18), (31, 18), ph, 1.05)[0])
        frames.append(finish(f))
    return frames


def ns() -> list[dict]:
    """다시마 줄기를 따라 몸을 꿈틀대며 오른다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        kelp(f, 7.0, 2, 30, ph)
        bob = round(1.0 * math.sin(ph))
        f.update(cat((17, 1 + bob), (17, 33 + bob), ph, 1.0)[0])
        frames.append(finish(f))
    return frames


def rock(f: dict, stones) -> set:
    """둥근 돌 여럿을 겹친 바위 — 돌마다 테두리를 따로 그어 덩어리가 보이게"""
    whole = set()
    for cx, cy, r in stones:
        m = {p for p in disc(cx, cy, r) if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}
        solid(f, m, lambda p, cx=cx, cy=cy: ROCK_D if p[0] + p[1] > cx + cy + 0.8 * r else ROCK, OUT)
        whole |= m
    return whole


def nesw() -> list[dict]:
    """왼쪽 아래 바위 틈에서 오른쪽 위로 빠져나온다 — 꼬리는 아직 틈 속"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        rise = 1.2 * math.sin(ph)
        f.update(cat((round(29 + rise), round(2 - rise)), (round(2 + rise), round(29 - rise)), ph, 1.08,
                     flip=True)[0])
        rock(f, [(3.5, 21.5, 3.5), (9.5, 27.0, 3.5), (3.5, 27.5, 3.5)])
        puff(f, 11.0, 25.0, k, 1)
        frames.append(finish(f))
    return frames


def nwse() -> list[dict]:
    """오른쪽 아래 바위 굴로 머리부터 들어간다 — 굴 안에 든 몸은 그늘에 잠긴다"""
    frames = []
    hx_, hy, rx, ry = 24.5, 25.0, 4.6, 3.6
    for k, ph in enumerate(phases()):
        f = {}
        dive = 1.5 * math.sin(ph)
        rock(f, [(19.0, 21.0, 3.2), (25.0, 19.5, 3.4), (29.5, 23.0, 3.0), (18.5, 28.0, 3.2), (29.0, 28.5, 3.0),
                 (24.0, 30.0, 2.6)])
        hole = {(x, y) for y in range(18, 31) for x in range(18, 31)
                if ((x + 0.5 - hx_) / rx) ** 2 + ((y + 0.5 - hy) / ry) ** 2 <= 1}
        solid(f, hole, CAVE, OUT)
        body, _ = cat((round(24 + dive), round(24 + dive)), (round(2 + dive), round(2 + dive)), ph, 1.05)
        for p, col in body.items():
            f[p] = (OUT if col == OUT else DARK) if p in hole else col
        frames.append(finish(f))
    return frames


def up() -> list[dict]:
    """모래에서 고개를 내민 앞얼굴 — 넓적한 머리 양옆 위에 노란 고양이 눈, 가끔 깜빡이고 모래가 흘러내린다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        cx, top = 15.5, 6 + round(0.6 * math.sin(ph))
        cy = top + 10
        head = {(x, y) for y in range(top, 27) for x in range(1, 31)
                if ((x + 0.5 - cx) / 14.0) ** 2 + ((y + 0.5 - cy) / 10.0) ** 2 <= 1}

        def col(p):
            if p[1] > cy + 2:
                return BELLY
            if p[1] < top + 3 and abs(p[0] + 0.5 - cx) < 5:
                return MID   # 머리 위 안장 끝자락
            return PALE if (p[0] * 2 + p[1] * 3) % 9 == 0 else LIGHT
        solid(f, head, col)
        blink = k in (7, 8)
        for sgn in (-1, 1):   # 고양이 눈: 머리 양옆 위, 노란 눈에 세로 동공
            ex, ey = math.floor(cx + sgn * 8.0), top + 4
            if blink:
                for d in (-1, 0, 1):
                    f[ex + d, ey + 2] = OUT
            else:
                for dx in (-1, 0, 1):
                    for dy in range(4):
                        f[ex + dx, ey + dy] = EYE
                for dy in range(4):
                    f[ex, ey + dy] = OUT
                f[ex - sgn, ey] = HI
        for sgn in (-1, 1):   # 콧구멍 덮개
            f[math.floor(cx) + sgn * 3, cy] = OUT
            f[math.floor(cx) + sgn * 3, cy + 1] = MID
        for i in range(-7, 8):   # 입: 넓게 웃는다
            f[math.floor(cx) + i, cy + 4 - round(abs(i) / 4)] = OUT
        for y in range(24, 29):   # 모래 무덤: 목을 덮는다
            for x in range(1, 31):
                f[x, y] = SAND if (x + y) % 4 else SAND_D
        for j in range(2):   # 흘러내리는 모래알
            t = (k / N + j / 2) % 1
            for sgn in (-1, 1):
                f[math.floor(cx + sgn * (14 - 2 * t)), math.floor(top + 6 + 17 * t)] = SAND_D
        frames.append(finish(f))
    return frames


def pen() -> list[dict]:
    """주둥이로 모래 바닥을 긁으며 왼쪽 아래로 간다 — 모래에 물결 자국이 자란다. 주둥이 끝이 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sand(f, 1, 30, 30)
        n = round(26 * (k + 1) / N)
        for x in range(4, 4 + n):
            f[x, 29 + round(0.9 * math.sin(x * 0.8))] = SAND_D
        f.update(cat((2, 27), (29, 8), ph, 1.05)[0])
        frames.append(finish(f))
    return frames


def hand() -> list[dict]:
    """고양이처럼 손바닥에 몸을 비빈다 — 닿으면 하트가 오른다"""
    frames = []
    X0, Y0 = 9, 1
    for k, ph in enumerate(phases()):
        f = {}
        lift = 3.5 * max(0.0, math.sin(ph))
        body, _ = cat((1, round(21 - lift)), (31, round(24 - lift * 0.3)), ph, 1.05)
        f.update(body)
        hand_at(f, X0, Y0, SKIN)
        if lift > 2.5:
            t = (k % 4) / 4
            hy = round(12 - 5 * t)
            glyph(f, [".#.#.", "#####", "#####", ".###.", "..#.."], 23, hy, HEART)
        frames.append(finish(f))
    return frames


def cross() -> list[dict]:
    """괴상어 눈 바짝: 노란 눈동자 속 세로 동공이 가늘어졌다 굵어졌다 하고 가끔 깜빡인다. 가운데가 핫스팟"""
    frames = []
    C = (15, 15)
    for k, ph in enumerate(phases()):
        f = {}
        cx, cy = C[0] + 0.5, C[1] + 0.5
        lids = {(x, y) for y in range(4, 28) for x in range(1, 31)
                if ((x + 0.5 - cx) / 14.0) ** 2 + ((y + 0.5 - cy) / 9.5) ** 2 <= 1}
        solid(f, lids, lambda p: DARK if min(abs(p[0] + 0.5 - cx - c) for c in (-9, 9)) < 1.2 else LIGHT)
        blink = k in (8, 9)
        eye = {(x, y) for x in range(4, 28) for y in range(7, 25)
               if ((x + 0.5 - cx) / 9.5) ** 2 + ((y + 0.5 - cy) / 6.5) ** 2 <= 1}
        if blink:
            for p in eye:
                f[p] = MID
            for x in range(6, 26):
                f[x, C[1]] = OUT
        else:
            w = 0.7 + 0.9 * (0.5 + 0.5 * math.sin(ph))   # 동공 반폭
            for p in eye:
                dx, dy = p[0] + 0.5 - cx, p[1] + 0.5 - cy
                r = math.hypot(dx / 9.5, dy / 6.5)
                f[p] = OUT if edge(eye, p) else OUT if abs(dx) < w * (1 - (dy / 7) ** 2) else \
                    EYE if r < 0.75 else hx("b09a2cff")
            f[C[0] - 4, C[1] - 3] = HI
            f[C[0] - 3, C[1] - 3] = HI
            f[C[0] - 4, C[1] - 2] = HI
        for d in (13, 14):   # 조준 눈금
            f[C[0] - d, C[1]] = f[C[0] + d, C[1]] = SIGN
        frames.append(finish(f))
    return frames


def ibeam() -> list[dict]:
    """세로로 선 알집('인어의 지갑') — 네 귀퉁이 덩굴손이 I 의 가로대가 되고, 속에서 새끼가 꼬리를 친다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        case = {(x, y) for x in range(3, 8) for y in range(3, 22)}
        solid(f, case, lambda p: CASE if (p[0] + p[1]) % 5 else CASE_D, CASE_D)
        for y0, sy in ((2, -1), (22, 1)):   # 덩굴손: 귀퉁이에서 바깥으로 말려 나간다
            for sx, x0 in ((-1, 3), (1, 7)):
                for i, (dx, dy) in enumerate(((0, 0), (1, 0), (2, 0), (3, sy), (3, 2 * sy), (2, 2 * sy))):
                    f[x0 + sx * dx, y0 + dy] = CASE_D
        solid(f, disc(5.5, 16.5, 1.4), YOLK, CASE_D)
        wig = math.sin(ph)
        for i in range(8):   # 새끼: 노른자에서 위로 꼬리를 친다
            y = 15 - i
            f[math.floor(5.5 + 1.2 * wig * math.sin(i * 0.8) * i / 7), y] = BELLY if i < 6 else PALE
        frames.append(finish(f))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "help": help_, "person": person, "pin": pin, "we": we, "ns": ns,
         "nesw": nesw, "nwse": nwse, "up": up, "pen": pen, "hand": hand, "cross": cross, "ibeam": ibeam}
HOT = {"arrow": ARROW[0], "busy": ARROW[0], "help": ARROW[0], "person": ARROW[0], "pin": ARROW[0],
       "we": (16, 18), "ns": (17, 16), "nesw": (16, 16), "nwse": (15, 15), "up": (15, 6), "pen": (2, 27),
       "hand": (13, 1), "cross": (15, 15), "ibeam": (5, 12)}


def main() -> None:
    write(SID, {r: (lambda r=r: (SCENE[r](), HOT[r])) for r in SCENE}, sys.argv[1:] or None)


if __name__ == "__main__":
    main()

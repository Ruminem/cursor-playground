# SPDX-License-Identifier: Apache-2.0
"""돌고래(dolphinanim) 구성표 그림 `art/dolphinanim/*.txt` 를 만든다. 빌드가 부르지 않고 그림을 다시 뽑을 때 손으로 돌린다.

  python3 gen/dolphin.py [역할...]     그림을 쓴다 (역할을 안 주면 새로 그리는 칸 전부)

첫 벌(2026-09-24)은 화살표 돌고래를 방향만 돌려 칸마다 놓아서 복제품 같다는 말을 들었다(2026-10-01 사용자).
그래서 화살표 돌고래만 기준으로 두고 나머지 칸은 돌고래가 하는 짓으로 따로 그린다(`SCENE`) — 붓을 물고 그림 그리기(펜) ·
주둥이에 공 올리기(위) · 꼬리로 물 위 걷기(위아래) · 머리 내밀고 가슴지느러미 흔들기(손) · 음파 조준(십자) ·
숨구멍 물방울 물음표(도움말) · 비치볼 튀기기(작업 중) · 튜브 탄 사람(사람) · 부표(핀) · 물 위 뛰어넘기(좌우) ·
솟구치기와 잠수(대각선) · 모래에 머리 박기(I빔).
wait(물결 위로 뛰는 돌고래) · move(위에서 본 돌고래) · no(몸을 만 돌고래와 빗금)는 처음부터 돌고래만의 그림이라 두고
안 그린다 — 그래서 역할을 안 주면 그 셋은 건드리지 않는다.
상어(`bukang.py`)와 가르는 것: 짧은 주둥이 위로 볼록한 이마(멜론) · 가운데 낫 모양 등지느러미 · 작은 가슴지느러미 ·
꼬리는 옆이 아니라 위아래로 까딱인다(`beat`) · 몸 위로 빛 물결이 한 줄 지나간다(`decorate`).
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import dataclasses
import math
import sys

from sea import (BUB, N, SIGN, SIGN_D, WAKE, Body, bubble, crop, disc, finish, hx, ink, line, phases, raster,
                 side, solid, splash, under, water, write)

SID = "dolphinanim"
ARROW = ((1, 2), (15, 21))   # 화살표 돌고래의 주둥이 끝(핫스팟) · 꼬리 끝

# 옛 그림의 색을 그대로 쓴다 — 구성표 이름·설명과 무늬·몸 판이 이 색으로 되어 있다
OUT, DARK, MID, LIGHT = hx("17212cff"), hx("2c3a4aff"), hx("43566bff"), hx("566b83ff")
SHADE, BELLY, HI = hx("cfd8e0ff"), hx("dfe6ecff"), hx("f7fafcff")
GLINT = hx("b8f0ffff")        # 빛 물결
ink(OUT, HI)
BALL = (SIGN, HI, hx("f2c230ff"), BUB, HI, hx("5fb85aff"))   # 비치볼 여섯 쪽
SKIN, HAIR = hx("f2c9a0ff"), hx("4a3226ff")
WOOD, BRASS = hx("c9a27aff"), hx("b8bec4ff")
SAND, SAND_D = hx("e8d3a0ff"), hx("c4a86cff")

# ── 옆모습 돌고래: 주둥이 s=0 → 꼬리 끝 s=1, v 는 등 쪽이 + (몸길이 단위) ─────────────────────
# 짧은 주둥이가 있고 그 뒤로 이마가 둥글게 솟는다(멜론). 가장 두꺼운 자리는 몸 가운데, 꼬리자루는 가늘다
TOP = [(0, 0), (0.06, 0.014), (0.1, 0.02), (0.11, 0.045), (0.135, 0.07), (0.18, 0.085), (0.3, 0.095),
       (0.45, 0.088), (0.6, 0.06), (0.72, 0.032), (0.8, 0.02), (0.84, 0.018)]
BOT = [(0, 0), (0.06, -0.014), (0.1, -0.022), (0.13, -0.036), (0.2, -0.062), (0.32, -0.08), (0.46, -0.07),
       (0.6, -0.045), (0.72, -0.025), (0.8, -0.018), (0.84, -0.016)]
FINS = {   # 앞의 것이 위에 그려진다
    "pectoral": [(0.19, -0.035), (0.24, -0.09), (0.29, -0.14), (0.315, -0.15), (0.3, -0.1), (0.29, -0.055),
                 (0.28, -0.035)],
    "dorsal": [(0.36, 0.085), (0.42, 0.14), (0.47, 0.19), (0.52, 0.205), (0.505, 0.16), (0.51, 0.11),
               (0.56, 0.07)],
    "fluke": [(0.8, 0.018), (0.88, 0.06), (0.95, 0.1), (1.0, 0.11), (0.97, 0.06), (0.93, 0.01),
              (0.93, -0.01), (0.97, -0.06), (1.0, -0.11), (0.95, -0.1), (0.88, -0.06), (0.8, -0.018)],
}
PIVOT = 0.55              # 꼬리를 위아래로 까딱일 때 휘기 시작하는 자리
BEAT = 0.07               # 꼬리 끝이 오르내리는 폭 (몸길이 단위, 두께 배율 전)


def beat(s: float, ph: float) -> float:
    """꼬리를 위아래로 까딱인다 — 상어처럼 옆으로 저으면 돌고래가 아니다. PIVOT 뒤로 갈수록 크게"""
    return BEAT * math.sin(ph) * (max(0.0, s - PIVOT) / (1 - PIVOT)) ** 2


def skin(s, v, top, bot):
    """등은 짙게, 옆구리는 한 단 밝게, 배는 희게. 흰 배는 앞쪽만 넓고 꼬리로 갈수록 좁아져 꼬리자루에서 사라진다 —
    꼬리까지 흰 줄이 가면 다랑어로 읽힌다"""
    belly = max(0.0, 0.45 - 0.55 * max(0.0, s - 0.3))       # 배가 차지하는 몫 (아래에서부터)
    sep = bot + belly * (top - bot)
    if v > bot + (belly + 0.6 * (1 - belly)) * (top - bot):
        return MID
    if v > sep:
        return LIGHT
    if v < bot + 0.3 * (sep - bot):
        return SHADE
    return BELLY


def decorate(c) -> None:
    """눈 · 웃는 입선 · 등 위로 지나가는 빛 물결 한 줄"""
    e = c.at(0.15, 0.018)
    if e in c.mask:
        c.out[e] = OUT
    if c.detail:
        for s in (0.04, 0.07, 0.1, 0.13):   # 입선: 주둥이 끝에서 눈 밑까지, 끝이 살짝 올라간다(웃는 입)
            c.paint(c.at(s, -0.004 + 0.12 * max(0, s - 0.09)), DARK)
    # 빛 물결: 한 바퀴에 한 번 주둥이에서 꼬리로 비스듬한 빛줄기가 등 위를 지나간다
    x0 = -0.15 + 1.2 * (c.ph / (2 * math.pi))
    for p in c.mask:
        if c.region.get(p) != "body" or c.out.get(p) not in (MID, LIGHT):
            continue
        s, v = c.sv(p)
        if abs(s - x0 - 0.9 * v) * c.L < 0.9:
            c.out[p] = GLINT if c.out[p] == LIGHT else LIGHT


DOLPHIN = Body(
    top=TOP, bot=BOT, fins=FINS, order=("pectoral", "body", "dorsal", "fluke"),
    skin=skin, fin_ink=lambda r, s, v: DARK if r != "pectoral" else MID,
    bend=lambda s, v, ph: (s, v + beat(s, ph)), unbend=lambda s, v, ph: (s, v - beat(s, ph)),
    decorate=decorate, thick=1.6, length=1.05, lined=("pectoral",))


def dolphin(head, tail, ph, size=None, flip=False, detail=True, body=DOLPHIN):
    """자세 하나 × 위상 하나 → ({좌표: 색}, 몸 칸 집합) — `sea.side` 참고. 판(테 한 칸을 남긴 1–30) 밖은 자른다"""
    return crop(*side(body, head, tail, ph, size, 0.0, flip, detail))


def arrow_dolphin(ph: float, size: float = 1.05) -> dict:
    """화살표 돌고래. 줄여 그린 것(장면 곁의 작은 돌고래)은 입선을 뺀다"""
    return dolphin(*ARROW, ph, size, detail=size >= 1.05)[0]


# ── 소품 ─────────────────────────────────────────────────────────────────────
def ball(f: dict, cx: float, cy: float, r: float, spin: float) -> None:
    """여섯 쪽 비치볼. spin 만큼 돌아 있다"""
    m = disc(cx, cy, r)
    def col(p):
        a = math.atan2(p[1] + 0.5 - cy, p[0] + 0.5 - cx) + spin
        if math.hypot(p[0] + 0.5 - cx, p[1] + 0.5 - cy) < r * 0.2:
            return HI
        return BALL[math.floor(a / (2 * math.pi) * 6) % 6]
    solid(f, m, col)


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    return [finish(arrow_dolphin(ph)) for ph in phases()]


def busy() -> list[dict]:
    """작은 돌고래 곁에서 비치볼이 물 위로 통통 튀며 돈다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        water(f, 16, 30, 29, k)
        t = k / N
        cy = 25.0 - 9.0 * math.sin(math.pi * t)
        ball(f, 23.5, cy, 4.8, 2 * math.pi * t)
        if k in (0, 1):
            splash(f, 23.5, 28.5, k, 4, 5.0, 3.0)
        f.update(arrow_dolphin(ph, 0.74))
        frames.append(finish(f))
    return frames


def help_() -> list[dict]:
    """숨구멍에서 오른 물방울이 줄지어 물음표를 그린다. 방울은 하나씩 따로 일렁이고 새 방울이 줄 끝으로 계속 오른다"""
    # 물음표 길: 윗고리 → 꺾임 → 기둥, 그리고 점. (x, y) 는 판 칸
    PATH = [(18.0, 17.5), (18.6, 14.8), (20.8, 13.2), (23.6, 13.0), (26.0, 14.4), (26.6, 17.0), (25.0, 19.4),
            (22.8, 21.0), (22.4, 23.6)]
    DOT = (22.4, 28.0)
    frames = []
    for k, ph in enumerate(phases()):
        f = arrow_dolphin(ph, 0.74)
        for n, (x, y) in enumerate(PATH + [DOT]):
            wob = 0.45 * math.sin(ph + n * 1.1)
            bubble(f, x + wob, y + 0.3 * math.cos(ph + n), 1.35)
        for j in range(2):   # 숨구멍(머리 뒤 등)에서 물음표 머리 쪽으로 오르는 작은 방울
            tt = (k / N + j / 2) % 1
            bubble(f, 10.5 + 6 * tt, 10.0 + 6 * tt - 5 * math.sin(math.pi * tt), 0.8)
        frames.append(finish(f))
    return frames


def person() -> list[dict]:
    """빨간 줄 튜브를 탄 사람이 물 위에 둥실 뜬다 — 돌고래가 헤엄치는 친구를 찾았다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        dy = round(1.0 * math.sin(ph))
        cx, wy = 21.5, 26
        water(f, 13, 30, wy, k)
        head = disc(cx, wy - 8.5 + dy, 3.4)
        solid(f, head, lambda p: HAIR if p[1] + 0.5 < wy - 9.8 + dy else SKIN)
        f[math.floor(cx) - 1, wy - 9 + dy] = OUT
        f[math.floor(cx) + 1, wy - 9 + dy] = OUT
        ring = {(x, y) for y in range(wy - 6, wy + 2) for x in range(13, 31)
                if ((x + 0.5 - cx) / 6.3) ** 2 + ((y + 0.5 - (wy - 2.5 + dy)) / 2.8) ** 2 <= 1}
        solid(f, ring, lambda p: SIGN if (p[0] // 2) % 2 else HI, SIGN_D)
        for x in (math.floor(cx) - 3, math.floor(cx) + 3):   # 튜브를 잡은 두 손
            f[x, wy - 5 + dy] = SKIN
        f.update(arrow_dolphin(ph, 0.74))
        frames.append(finish(f))
    return frames


def pin() -> list[dict]:
    """빨갛고 흰 부표가 물결에 까딱이고 꼭대기 등이 깜빡인다 — 바다의 위치 표시"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        wy = 28
        water(f, 14, 30, wy, k)
        tilt = 0.12 * math.sin(ph)
        cx, by = 23.0, wy - 1.0 + round(0.8 * math.sin(ph + 1))
        def rot(x, y):
            return cx + x * math.cos(tilt) - y * math.sin(tilt), by + x * math.sin(tilt) + y * math.cos(tilt)
        hull = raster([rot(*q) for q in ((-5, 0), (5, 0), (3.5, -10), (-3.5, -10))])
        solid(f, hull, lambda p: SIGN if math.floor((by - p[1]) / 3) % 2 == 0 else HI, SIGN_D)
        mast = raster([rot(*q) for q in ((-0.9, -10), (0.9, -10), (0.9, -14), (-0.9, -14))], 6)
        for p in mast:
            f[p] = DARK
        lx, ly = rot(0, -15.5)
        solid(f, disc(lx, ly, 1.8), hx("f2c230ff") if k % 4 < 2 else hx("8a7a40ff"), DARK)
        f.update(arrow_dolphin(ph, 0.74))
        frames.append(finish(f))
    return frames


def leap(t: float, x0: float, x1: float, wy: float, h: float):
    """물낯 wy 에서 x0 → x1 로 뛰는 포물선의 t 자리와 그 기울기(단위 벡터)"""
    x = x0 + (x1 - x0) * t
    y = wy - h * 4 * t * (1 - t)
    dx, dy = x1 - x0, -h * 4 * (1 - 2 * t)
    d = math.hypot(dx, dy)
    return (x, y), (dx / d, dy / d)


def we() -> list[dict]:
    """물 위를 둥글게 뛰어넘는다 — 왼쪽에서 솟아 오른쪽으로 들어간다. 물속에 든 몸은 안 보인다"""
    frames = []
    WY, HALF = 24, 9.5
    for k, ph in enumerate(phases()):
        f = {}
        water(f, 1, 30, WY, k)
        t = (k / N + 0.5) % 1   # 첫 장이 꼭대기
        (x, y), (ux, uy) = leap(t, -2.0, 33.0, WY + 3, 16.0)
        head = (round(x + ux * HALF), round(y + uy * HALF))
        tail = (round(x - ux * HALF), round(y - uy * HALF))
        body, _ = dolphin(head, tail, ph, 1.0, detail=True)
        f.update(under(body, WY))
        if t < 0.35:   # 솟는 자리 · 들어가는 자리에만 물보라
            splash(f, 4.5, WY - 0.5, k, 4, 2.5, 4.0)
        if t > 0.65:
            splash(f, 26.5, WY - 0.5, k, 4, 2.5, 4.0)
        frames.append(finish(f))
    return frames


def ns() -> list[dict]:
    """꼬리로 물 위를 걷는다(tail-walk) — 몸을 세우고 까딱이며, 물낯에 물보라가 튄다"""
    frames = []
    WY = 25
    for k, ph in enumerate(phases()):
        f = {}
        water(f, 6, 26, WY, k)
        bob = round(1.2 * math.sin(2 * ph))
        body, _ = dolphin((15, 1 + bob), (16, 33 + bob), ph, 1.0)
        f.update(under(body, WY))
        splash(f, 15.5, WY - 0.5, k, 6, 7.0, 4.0)
        frames.append(finish(f))
    return frames


def nesw() -> list[dict]:
    """물 위로 비스듬히 솟구친다 — 머리는 오른쪽 위, 꼬리는 왼쪽 아래 물속, 물보라"""
    frames = []
    WY = 24
    for k, ph in enumerate(phases()):
        f = {}
        water(f, 1, 20, WY, k)
        rise = 1.5 * math.sin(ph)
        body, _ = dolphin((round(29 + rise), round(2 - rise)), (round(7 + rise), round(28 - rise)), ph, 1.08,
                          flip=True)
        f.update(under(body, WY))
        splash(f, 11.5, WY - 0.5, k, 6, 6.0, 4.0)
        frames.append(finish(f))
    return frames


def nwse() -> list[dict]:
    """오른쪽 아래로 잠수한다 — 숨구멍에서 샌 물방울이 줄지어 위로 오른다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for j in range(4):
            t = (k / N + j / 4) % 1
            bubble(f, 25.0 + 1.5 * t + 0.7 * math.sin(ph + j), 17.0 - 14 * t, 0.7 + 0.8 * t)
        dive = 1.2 * math.sin(ph)
        body, _ = dolphin((round(29 + dive), round(29 + dive)), (round(6 + dive), round(8 + dive)), ph, 1.0)
        f.update(body)
        frames.append(finish(f))
    return frames


def up() -> list[dict]:
    """물 위로 몸을 세우고 주둥이 끝에 비치볼을 올려 굴린다(돌고래 쇼)"""
    frames = []
    WY = 28
    for k, ph in enumerate(phases()):
        f = {}
        bob = 0.8 * math.sin(ph)
        water(f, 6, 25, WY, k)
        ball(f, 15.5 + 0.6 * math.sin(ph), 6.5 + bob, 4.8, 2 * math.pi * k / N)
        body, _ = dolphin((15, 12), (17, 44), ph, 1.0)
        f.update({p: c for p, c in under(body, WY).items() if p not in f})
        splash(f, 16.0, WY - 0.5, k, 4, 5.0, 2.5)
        frames.append(finish(f))
    return frames


def pen() -> list[dict]:
    """붓을 입에 가로 물고 그림을 그린다(수족관 돌고래가 실제로 하는 일). 붓끝이 핫스팟이고 바닥에 빨간 붓질이 자란다.
    붓을 주둥이와 같은 줄로 물리면 긴 주둥이(황새치)로 읽혀서 비스듬히 문다"""
    frames = []
    TIP, BACK = (1.5, 28.5), (12.0, 9.0)
    for k, ph in enumerate(phases()):
        f = {}
        t = k / N
        for x in range(3, 3 + round(18 * t)):   # 붓질
            f[x, 30 - round(0.8 + 0.8 * math.sin(x * 0.7))] = SIGN
        body, _ = dolphin((9, 14), (30, 7), ph, 1.0)
        f.update(body)
        ux, uy = BACK[0] - TIP[0], BACK[1] - TIP[1]
        d = math.hypot(ux, uy)
        ux, uy = ux / d, uy / d
        ferr = (TIP[0] + ux * 3.4, TIP[1] + uy * 3.4)
        line(f, ferr, BACK, WOOD)
        line(f, (ferr[0] - ux * 0.3, ferr[1] - uy * 0.3), (ferr[0] + ux * 1.2, ferr[1] + uy * 1.2), BRASS)
        for p in raster([(TIP[0] - 0.4, TIP[1] + 0.4), (ferr[0] - uy * 1.4, ferr[1] + ux * 1.4),
                         (ferr[0] + uy * 1.4, ferr[1] - ux * 1.4)], 5):
            f[p] = SIGN
        frames.append(finish(f))
    return frames


def flipper(ph: float) -> list:
    """손 흔들기: 가슴지느러미를 밑동에서 앞뒤로 돌린다"""
    a = 0.9 * math.sin(2 * ph) - 0.4
    b0 = (0.24, -0.04)
    out = []
    for s, v in FINS["pectoral"]:
        ds, dv = s - b0[0], v - b0[1]
        out.append((b0[0] + ds * math.cos(a) - dv * math.sin(a), b0[1] + ds * math.sin(a) + dv * math.cos(a)))
    return out


def hand() -> list[dict]:
    """물 밖으로 머리를 쑥 내밀고 가슴지느러미를 흔든다. 주둥이 끝이 핫스팟"""
    frames = []
    WY = 22
    for k, ph in enumerate(phases()):
        f = {}
        body_ = dataclasses.replace(DOLPHIN, fins={**FINS, "pectoral": flipper(ph)})
        bob = round(0.8 * math.sin(ph))
        body, _ = dolphin((11, 1 + bob), (21, 40 + bob), 0.0, 1.0, body=body_)
        f.update(under(body, WY))
        water(f, 2, 29, WY, k)
        for j, r in enumerate((6.0, 9.5)):   # 몸 둘레 물결 고리
            rr = r + 1.5 * ((k / N) % 1)
            for i in range(28):
                a = 2 * math.pi * i / 28
                p = (math.floor(15.5 + rr * math.cos(a)), math.floor(WY + 0.5 + rr * 0.3 * math.sin(a)))
                if p not in f and p[1] >= WY:
                    f[p] = WAKE[2 + j]
        frames.append(finish(f))
    return frames


def cross() -> list[dict]:
    """음파 조준: 왼쪽 아래 작은 돌고래가 쏜 음파 고리가 가운데 조준점으로 번져 간다"""
    frames = []
    C = (15, 15)
    for k, ph in enumerate(phases()):
        f = {}
        body, _ = dolphin((6, 23), (0, 31), ph, 1.0, detail=False)
        hx_, hy = 6.5, 23.0
        for j in range(3):
            t = (k / N + j / 3) % 1
            r = 3 + 13 * t
            col = WAKE[1] if t < 0.4 else WAKE[2] if t < 0.75 else WAKE[3]
            for i in range(40):
                a = -math.pi / 4 + (i / 39 - 0.5) * 1.2
                f[math.floor(hx_ + r * math.cos(a)), math.floor(hy + r * math.sin(a))] = col
        f.update(body)
        cx, cy = C
        for d in range(3, 8):   # 십자선: 가운데를 비우고 네 팔
            for p in ((cx + d, cy), (cx - d, cy), (cx, cy + d), (cx, cy - d)):
                f[p] = OUT
        f[C] = SIGN
        frames.append(finish(f))
    return frames


def ibeam() -> list[dict]:
    """모래 바닥에 머리를 박고 먹이를 찾는다 — 거꾸로 선 몸이 I 기둥, 꼬리가 위 가로대, 모래가 아래 가로대"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        body, _ = dolphin((5, 24), (5, 0), ph, 1.0, detail=False)
        f.update(body)
        for x in range(0, 11):   # 모래 두 줄
            f[x, 25] = SAND
            f[x, 26] = SAND_D if x % 3 else SAND
        for j in range(2):   # 모래 먼지가 양옆으로 피어오른다
            t = (k / N + j / 2) % 1
            for sgn in (-1, 1):
                f[math.floor(5 + sgn * (1.5 + 3 * t)), math.floor(24.5 - 2.5 * t)] = SAND if t < 0.6 else SAND_D
        frames.append(finish(f))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "help": help_, "person": person, "pin": pin, "we": we, "ns": ns,
         "nesw": nesw, "nwse": nwse, "up": up, "pen": pen, "hand": hand, "cross": cross, "ibeam": ibeam}
HOT = {"arrow": ARROW[0], "busy": ARROW[0], "help": ARROW[0], "person": ARROW[0], "pin": ARROW[0],
       "we": (16, 16), "ns": (15, 14), "nesw": (18, 14), "nwse": (17, 18), "up": (15, 2), "pen": (1, 28),
       "hand": (11, 1), "cross": (15, 15), "ibeam": (5, 12)}


def main() -> None:
    write(SID, {r: (lambda r=r: (SCENE[r](), HOT[r])) for r in SCENE}, sys.argv[1:] or None)


if __name__ == "__main__":
    main()

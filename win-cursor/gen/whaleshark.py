# SPDX-License-Identifier: Apache-2.0
"""고래상어(whalesharkanim) 구성표 그림 `art/whalesharkanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/whaleshark.py [역할...]     그림을 쓴다 (역할을 안 주면 새로 그리는 칸 전부)

첫 벌(2026-09-24)은 화살표 고래상어를 방향만 돌려 칸마다 놓아서 복제품 같다는 말을 들었다(2026-10-01 사용자).
그래서 칸마다 고래상어가 사는 장면을 따로 그린다(`SCENE`) — 물낯에 몸을 세우고 플랑크톤 삼키기(위아래, 실제로
'병 세워 먹기'를 한다) · 입 벌리고 플랑크톤 걸러 먹기(좌우) · 햇살 쪽으로 오르기와 동가리를 앞세운 잠수(대각선) ·
앞에서 본 넓적한 얼굴(위) · 점을 찍으며 가는 점박이(펜) · 곁을 지나는 손가락(손) · 신원 확인 사진 뷰파인더(십자, 점
무늬가 사람 지문처럼 저마다 달라 연구자가 이것으로 가린다) · 위치 발신 태그(핀) · 스노클러(사람) · 점박이 무늬 물음표(도움말) ·
플랑크톤 소용돌이(작업 중) · 점박이 무늬 기둥(I빔).
wait(플랑크톤 곁을 헤엄치는 옆모습) · move(위에서 본 몸) · no(몸을 만 고래상어와 빗금)는 처음부터 고래상어만의 그림이라 둔다.
부캉이(`bukang.py`)와 가르는 것: 머리가 넓적하고 입이 맨 앞에 가로로 째져 있다 · 짙은 등에 흰 점 · 작은 눈 ·
꼬리 윗날개와 아랫날개가 거의 같은 초승달 · 이빨이 안 보인다.
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import (N, QMARK, SIGN, WAKE, Body, bubble, crop, disc, edge, finish, hand_at, hx, ink, line, phases,
                 raster, side, solid, water, write)

SID = "whalesharkanim"
ARROW = ((2, 1), (16, 20))   # 화살표 고래상어의 주둥이 한가운데(핫스팟) · 꼬리 끝

# 옛 그림의 색을 그대로 쓴다
OUT, DARK, MID, LIGHT = hx("0b1620ff"), hx("1d3042ff"), hx("2f475dff"), hx("6384a0ff")
GLINT, SHADE, PALE, HI = hx("86cde6ff"), hx("9fb4c6ff"), hx("dde9f2ff"), hx("f6fafdff")
PLANK, PLANK_D = hx("c9e89aff"), hx("6f9a3aff")   # 플랑크톤 (옅은 것만으로는 흰 바탕에서 안 보인다)
ink(OUT, HI, hx("b4d0e4c7"))
SKIN, SUIT, MASK, GLASS = hx("f2c9a0ff"), hx("27313aff"), hx("f2c230ff"), hx("9ed8eaff")
PILOT, PILOT_D = hx("e8e2c8ff"), hx("33404cff")   # 동가리(파일럿피시): 흰 몸에 검은 띠
TAG = hx("f2c230ff")
GULLET = hx("3a2630ff")

# ── 옆모습: 주둥이 s=0 → 꼬리 끝 s=1 ────────────────────────────────────────────
# 머리가 앞에서 뭉툭하게 잘려 있고(입이 맨 앞) 몸은 굵은 통, 꼬리자루는 가늘다
TOP = [(0, 0.04), (0.02, 0.058), (0.08, 0.072), (0.2, 0.088), (0.35, 0.09), (0.5, 0.072), (0.62, 0.045),
       (0.72, 0.024), (0.78, 0.02)]
BOT = [(0, -0.036), (0.02, -0.054), (0.08, -0.064), (0.2, -0.074), (0.35, -0.07), (0.5, -0.052), (0.62, -0.032),
       (0.72, -0.018), (0.78, -0.016)]
FINS = {
    "pectoral": [(0.17, -0.04), (0.23, -0.1), (0.3, -0.16), (0.34, -0.17), (0.32, -0.12), (0.29, -0.06),
                 (0.28, -0.04)],
    "dorsal": [(0.38, 0.08), (0.43, 0.14), (0.47, 0.18), (0.5, 0.18), (0.5, 0.13), (0.53, 0.08), (0.54, 0.066)],
    "dorsal2": [(0.64, 0.04), (0.67, 0.075), (0.69, 0.072), (0.7, 0.03)],
    "caudal": [(0.76, 0.02), (0.84, 0.08), (0.93, 0.15), (0.97, 0.16), (0.95, 0.11), (0.9, 0.04), (0.89, 0.0),
               (0.91, -0.05), (0.95, -0.1), (0.93, -0.12), (0.84, -0.07), (0.76, -0.018)],
}
PIVOT = 0.64


def sweep(ph: float) -> float:
    """꼬리를 옆으로 젓는 상어를 옆에서 보면 꼬리가 줄었다 늘었다 한다 — PIVOT 뒤 길이 배율. 큰 몸이라 느긋하게"""
    return 0.86 + 0.14 * math.cos(ph)


def fold(s: float, k: float) -> float:
    return s if s <= PIVOT else PIVOT + (s - PIVOT) * k


def skin(s, v, top, bot):
    """등은 짙은 청회색(흰 점은 `decorate`), 배는 옅게"""
    sep = bot + 0.4 * (top - bot)
    if v > sep:
        return MID
    if v < bot + 0.35 * (sep - bot):
        return SHADE
    return PALE


def decorate(c) -> None:
    """흰 점 · 옆구리 능선 한 줄 · 맨 앞 가로 입 · 작은 눈 · 아가미 줄"""
    for p in c.mask:
        if c.out.get(p) != MID or c.region.get(p) != "body":
            continue
        s, v = c.sv(p)
        i, j = round(s * c.L), round(v * c.L * c.T)
        if s > 0.06 and i % 3 == 0 and (j + i // 3) % 3 == 0:
            c.out[p] = HI
    if c.detail:   # 옆구리 능선: 배와 등의 경계 바로 위
        for k in range(int(0.3 * c.L)):
            s = 0.22 + k / c.L
            c.paint(c.at(s, 0.012), LIGHT)
    e = c.at(0.06, 0.02)
    if e in c.mask:
        c.out[e] = OUT
    # 입: 맨 앞 가로로 째진 입. 벌리면(m) 검붉은 속이 보인다
    for p in c.mask:
        s, v = c.sv(p)
        if s < 0.075 and abs(v + 0.008) < 0.005 + 0.02 * c.m and not edge(c.mask, p):
            c.out[p] = GULLET if c.m > 0.25 else OUT
    if c.detail:
        for g in range(3):
            for v in (-0.02, 0.0, 0.02):
                c.paint(c.at(0.13 + g * 1.6 / c.L, v), DARK)


WHALE = Body(
    top=TOP, bot=BOT, fins=FINS, order=("pectoral", "body", "dorsal", "dorsal2", "caudal"),
    skin=skin, fin_ink=lambda r, s, v: DARK if r == "pectoral" else MID,
    bend=lambda s, v, ph: (fold(s, sweep(ph)), v),
    unbend=lambda s, v, ph: (s if s <= PIVOT else PIVOT + (s - PIVOT) / sweep(ph), v),
    decorate=decorate, thick=1.6, length=1.05, small=("dorsal2",), lined=("pectoral",))


def shark(head, tail, ph, size=None, m=0.0, flip=False, detail=True):
    """자세 하나 × 위상 하나 → ({좌표: 색}, 몸 칸 집합). 판 밖은 자른다"""
    return crop(*side(WHALE, head, tail, ph, size, m, flip, detail))


def arrow_shark(ph: float, size: float = 1.05) -> dict:
    return shark(*ARROW, ph, size, 0.0, detail=size >= 1.05)[0]


# ── 소품 ─────────────────────────────────────────────────────────────────────
def spotted(f: dict, mask: set, k: int = 0, drift=(0, 0)) -> None:
    """mask 를 고래상어 살갗으로 — 짙은 바탕에 흰 점. drift 는 장마다 점이 흐르는 방향(칸)"""
    for p in mask:
        if edge(mask, p):
            f[p] = OUT
            continue
        x, y = p[0] - drift[0] * k, p[1] - drift[1] * k
        f[p] = HI if x % 3 == 0 and (y + x // 3) % 3 == 0 else MID


def plankton(f: dict, cx: float, cy: float, r: float, k: int, n: int = 8) -> None:
    """플랑크톤 소용돌이: 알갱이 n 개가 돌고 뒤로 옅은 꼬리를 끈다"""
    for i in range(n):
        a = 2 * math.pi * (i / n + k / N)
        rr = r * (0.55 + 0.45 * ((i % 3) / 2))
        p = (math.floor(cx + rr * math.cos(a)), math.floor(cy + rr * 0.8 * math.sin(a)))
        f[p] = PLANK_D
        f[p[0], p[1] - 1] = PLANK
        b = a - 0.35
        f.setdefault((math.floor(cx + rr * math.cos(b)), math.floor(cy + rr * 0.8 * math.sin(b))), WAKE[3])


def pilot(f: dict, x: float, y: float, d: tuple) -> None:
    """동가리 한 마리: d 방향으로 헤엄치는 작은 흰 물고기, 검은 띠 둘"""
    ux, uy = d
    body = raster([(x + ux * 2.4, y + uy * 2.4), (x - uy * 1.3, y + ux * 1.3), (x - ux * 2.0, y - uy * 2.0),
                   (x + uy * 1.3, y - ux * 1.3)], 6)
    tail = raster([(x - ux * 1.6, y - uy * 1.6), (x - ux * 3.6 - uy * 1.6, y - uy * 3.6 + ux * 1.6),
                   (x - ux * 3.6 + uy * 1.6, y - uy * 3.6 - ux * 1.6)], 6)
    m = body | tail
    solid(f, m, lambda p: PILOT_D if round((p[0] - x) * ux + (p[1] - y) * uy) in (-1, 1) else PILOT, PILOT_D)


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    return [finish(arrow_shark(ph)) for ph in phases()]


def busy() -> list[dict]:
    """작은 고래상어 곁에서 플랑크톤이 소용돌이친다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        plankton(f, 23.0, 24.0, 6.0, k, 10)
        f.update(arrow_shark(ph, 0.74))
        frames.append(finish(f))
    return frames


def help_() -> list[dict]:
    """고래상어 살갗으로 빚은 물음표가 둥실 뜬다 — 점이 천천히 흐른다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = arrow_shark(ph, 0.74)
        dy = round(1.0 * math.sin(ph))
        core = {(16 + 2 * i + a, 13 + dy + 2 * j + b) for j, row in enumerate(QMARK) for i, ch in enumerate(row)
                if ch == "#" for a in (0, 1) for b in (0, 1)}
        mask = core | {(x + dx, y + dy_) for x, y in core for dx, dy_ in ((1, 0), (-1, 0), (0, 1), (0, -1))}
        spotted(f, mask, k // 3, (1, 0))
        frames.append(finish(f))
    return frames


def person() -> list[dict]:
    """고래상어 곁을 나란히 헤엄치는 스노클러 — 검은 잠수복 · 노란 물안경 · 물갈퀴를 번갈아 찬다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        hx_, hy = 17.5, 22.5 + round(0.6 * math.sin(ph))
        kick = 1.6 * math.sin(2 * ph)
        solid(f, raster([(hx_ + 2, hy - 1.6), (hx_ + 10, hy - 1.6), (hx_ + 10, hy + 1.8), (hx_ + 2, hy + 1.8)]), SUIT)
        for sgn in (-1, 1):   # 다리 둘과 물갈퀴
            ky = hy + 0.2 + sgn * kick * 0.5
            line(f, (hx_ + 10, hy + 0.2), (hx_ + 12.5, ky), SUIT, 0.8)
            line(f, (hx_ + 12.5, ky), (hx_ + 14.2, ky + sgn * 0.6), MASK, 0.6)
        line(f, (hx_ + 3, hy + 1.2), (hx_ - 4.5, hy + 1.8), SUIT, 0.7)   # 앞으로 뻗은 팔
        solid(f, disc(hx_, hy, 2.8), SKIN)
        f[math.floor(hx_) - 1, math.floor(hy)] = MASK
        f[math.floor(hx_) - 2, math.floor(hy)] = GLASS
        f[math.floor(hx_) - 1, math.floor(hy) - 1] = MASK
        for y in range(math.floor(hy) - 5, math.floor(hy) - 1):   # 스노클
            f[math.floor(hx_) + 1, y] = MASK
        for j in range(2):
            t = (k / N + j / 2) % 1
            bubble(f, hx_ + 1.5, hy - 6 - 6 * t, 0.7 + 0.3 * t)
        f.update(arrow_shark(ph, 0.74))
        frames.append(finish(f))
    return frames


def pin() -> list[dict]:
    """지도 핀을 고래상어 살갗으로 — 통통 튀고, 꼭대기에서 위치 전파 고리가 퍼진다(연구자가 다는 발신 태그)"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        dy = -round(2.5 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 17.5 + dy
        for j in range(2):
            t = (k / N + j / 2) % 1
            r = 6.5 + 4 * t
            col = WAKE[1] if t < 0.5 else WAKE[3]
            for i in range(24):
                a = -math.pi / 2 + (i / 23 - 0.5) * 1.6
                f[math.floor(cx + r * math.cos(a)), math.floor(cy + r * math.sin(a))] = col
        body = disc(cx, cy, 5.3) | raster([(cx - 4.6, cy + 2.5), (cx + 4.6, cy + 2.5), (cx, cy + 11)])
        spotted(f, body)
        solid(f, disc(cx, cy, 1.8), PALE, OUT)
        f.update(arrow_shark(ph, 0.74))
        frames.append(finish(f))
    return frames


def we() -> list[dict]:
    """왼쪽으로 입을 쩍쩍 벌리며 헤엄치고 플랑크톤이 입으로 빨려 든다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        m = 0.5 + 0.5 * math.cos(ph)
        for j in range(5):
            t = (k / N + j / 5) % 1
            f[math.floor(1 + 6 * t), math.floor(15 + (j - 2) * 2.2 * (1 - t))] = PLANK
        f.update(shark((8, 15), (31, 13), ph, 1.05, m)[0])
        frames.append(finish(f))
    return frames


def ns() -> list[dict]:
    """물낯 바로 밑에 몸을 세우고(병 세워 먹기) 입을 뻐끔거리며 플랑크톤을 들이킨다"""
    frames = []
    WY = 6
    for k, ph in enumerate(phases()):
        f = {}
        m = 0.5 + 0.5 * math.sin(ph)
        bob = round(0.7 * math.sin(ph))
        f.update(shark((15, 2 + bob), (16, 36 + bob), ph, 1.0, m, detail=True)[0])
        water(f, 3, 28, WY, k)   # 물낯이 머리를 가로지른다 — 주둥이만 물 밖
        for j in range(4):   # 입가로 모여드는 플랑크톤
            t = (k / N + j / 4) % 1
            sgn = 1 if j % 2 else -1
            f.setdefault((math.floor(15.5 + sgn * (8 - 7 * t)), math.floor(8 + 3 * (1 - t) * (j // 2))), PLANK)
        frames.append(finish(f))
    return frames


def nesw() -> list[dict]:
    """오른쪽 위 햇살 쪽으로 천천히 떠오른다 — 햇살 줄기가 일렁인다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for i in range(3):   # 햇살 줄기: 오른쪽 위 모서리에서 비스듬히
            w = (k / N + i / 3) % 1
            a = WAKE[3] if w < 0.5 else WAKE[4]
            for d in range(12):
                f[30 - d // 2 - 4 * i, 1 + d] = a
        rise = 1.2 * math.sin(ph)
        f.update(shark((round(28 + rise), round(4 - rise)), (round(5 + rise), round(28 - rise)), ph, 1.05,
                       flip=True)[0])
        frames.append(finish(f))
    return frames


def nwse() -> list[dict]:
    """오른쪽 아래로 잠수한다. 주둥이 앞에 동가리 둘이 길잡이로 앞서간다"""
    frames = []
    d = (1 / math.sqrt(2), 1 / math.sqrt(2))
    for k, ph in enumerate(phases()):
        f = {}
        dive = 1.0 * math.sin(ph)
        f.update(shark((round(19 + dive), round(19 + dive)), (round(-1 + dive), round(0 + dive)), ph, 1.05)[0])
        for j, (x, y) in enumerate(((27.5, 22.5), (22.5, 27.5))):
            pilot(f, x + 0.6 * math.sin(ph + j * 2), y + 0.6 * math.cos(ph + j * 2), d)
        frames.append(finish(f))
    return frames


def up() -> list[dict]:
    """앞에서 본 고래상어: 넓적하고 납작한 머리를 가로지르는 큰 입이 뻐끔거리고, 등지느러미 끝이 위를 가리킨다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        cx, cy = 15.5, 21.0 + round(0.6 * math.sin(ph))
        dorsal = raster([(cx - 1.8, cy - 3), (cx - 0.2, cy - 18), (cx + 0.8, cy - 18), (cx + 1.8, cy - 3)])
        solid(f, dorsal, MID)
        for sgn in (-1, 1):   # 가슴지느러미: 납작하게 옆으로
            fin = raster([(cx + sgn * 8, cy + 1.5), (cx + sgn * 15, cy + 4.5 + 0.8 * math.sin(ph)),
                          (cx + sgn * 14, cy + 6), (cx + sgn * 7, cy + 4)])
            solid(f, fin, DARK)
        head = {(x, y) for y in range(math.floor(cy) - 6, math.floor(cy) + 7) for x in range(0, 32)
                if ((x + 0.5 - cx) / 12.5) ** 2 + ((y + 0.5 - cy) / 5.0) ** 2 <= 1}
        spotted(f, head)
        m = 0.5 + 0.5 * math.sin(ph)
        for p in head:
            if edge(head, p):
                continue
            yy = p[1] + 0.5 - cy
            ax = abs(p[0] + 0.5 - cx)
            if 0 <= yy < 1 + 1.5 * m and ax < 10:   # 입: 머리 앞을 거의 다 가로지른다
                f[p] = GULLET if yy >= 0.5 or m > 0.3 else OUT
            elif yy >= 1 + 1.5 * m:
                f[p] = PALE
        for sgn in (-1, 1):   # 눈: 입꼬리 바로 위 양끝
            f[math.floor(cx + sgn * 10.5), math.floor(cy - 1)] = OUT
        frames.append(finish(f))
    return frames


def pen() -> list[dict]:
    """점박이가 왼쪽 아래로 가며 바닥에 점선을 찍는다 — 주둥이 끝이 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for i in range(k % 6 + 1):
            f[4 + 3 * i, 30] = DARK
            f[4 + 3 * i, 29] = HI
        f.update(shark((2, 27), (27, 5), ph, 1.05)[0])
        frames.append(finish(f))
    return frames


def hand() -> list[dict]:
    """손가락 하나가 가리키고 그 아래로 작은 고래상어가 지나간다(만지지는 않는다 — 규칙이다)"""
    frames = []
    X0, Y0 = 9, 1
    for k, ph in enumerate(phases()):
        f = {}
        x = -8 + 40 * ((k / N + 0.45) % 1)   # 첫 장에 손가락 밑
        body, _ = shark((round(x) + 12, 24), (round(x), 22), ph, 1.05, detail=False)
        f.update(body)
        hand_at(f, X0, Y0, SKIN)
        frames.append(finish(f))
    return frames


def cross() -> list[dict]:
    """신원 확인 사진: 뷰파인더 네 모서리 안으로 고래상어 옆구리 점 무늬가 흘러가고, 가운데 조준점"""
    frames = []
    C, R = (15, 15), 10
    for k, ph in enumerate(phases()):
        f = {}
        cx, cy = C
        flank = {(x, y) for x in range(cx - 7, cx + 8) for y in range(cy - 5, cy + 6)}
        spotted(f, flank, k, (-1, 0))
        for p in flank:
            if p[1] > cy + 2 and not edge(flank, p):
                f[p] = PALE
        for sx in (-1, 1):   # 모서리 ㄱ자 넷
            for sy in (-1, 1):
                for d in range(4):
                    f[cx + sx * R, cy + sy * (R - d)] = OUT
                    f[cx + sx * (R - d), cy + sy * R] = OUT
        for d in (-2, -1, 1, 2):
            f[cx + d, cy] = SIGN
            f[cx, cy + d] = SIGN
        f[C] = HI
        frames.append(finish(f))
    return frames


def ibeam() -> list[dict]:
    """점박이 무늬 I 기둥 — 점이 아래로 천천히 흐른다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        m = {(x, y) for x in range(3, 8) for y in range(0, 25)} | \
            {(x, y) for x in range(0, 11) for y in list(range(0, 3)) + list(range(22, 25))}
        spotted(f, m, k // 2, (0, 1))
        frames.append(finish(f))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "help": help_, "person": person, "pin": pin, "we": we, "ns": ns,
         "nesw": nesw, "nwse": nwse, "up": up, "pen": pen, "hand": hand, "cross": cross, "ibeam": ibeam}
HOT = {"arrow": ARROW[0], "busy": ARROW[0], "help": ARROW[0], "person": ARROW[0], "pin": ARROW[0],
       "we": (16, 15), "ns": (15, 16), "nesw": (16, 16), "nwse": (14, 14), "up": (16, 2), "pen": (2, 27),
       "hand": (13, 1), "cross": (15, 15), "ibeam": (5, 12)}


def main() -> None:
    write(SID, {r: (lambda r=r: (SCENE[r](), HOT[r])) for r in SCENE}, sys.argv[1:] or None)


if __name__ == "__main__":
    main()

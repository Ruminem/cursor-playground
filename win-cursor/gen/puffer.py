# SPDX-License-Identifier: Apache-2.0
"""복어(pufferanim) 구성표 그림 `art/pufferanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/puffer.py [역할...]     그림을 쓴다 (역할을 안 주면 새로 그리는 칸 전부)

첫 벌(2026-09-24)은 복어 색을 입힌 화살표·양방향 화살표라 복제품 같다는 말을 들었다(2026-10-01 사용자).
그래서 칸마다 복어가 하는 짓을 따로 그린다(`SCENE`) — 모래에 둥근 무늬 파기(작업 중, 실제로 수컷이 짝을 부르려고
모래 만다라를 판다) · 부풀었다 오그라드는 물음표(도움말) · 복어 풍선을 든 아이(사람) · 부푼 복어 머리 지도 핀(핀) ·
지느러미를 파닥이며 가기(좌우) · 부풀어 뜨고 오그라들어 가라앉기(위아래) · 떠오르기와 모래에 물 뿜기(대각선, 모래 속
먹이를 이렇게 판다) · 위로 물 뿜기(위) · 연필 갉아 먹기(펜) · 손가락이 닿으면 놀라 부풀기(손) · 가시 넷이 조준선인
부푼 복어(십자) · 가시 돋친 기둥(I빔).
wait(부풀었다 오그라드는 복어) · move · no 는 두고 안 그린다.
몸은 옆모습(`PUFF`, 짧고 통통한 몸 · 부리 입 · 큰 눈 · 꼬리 앞 위아래 작은 지느러미 · 부채 꼬리 · 파닥이는 가슴지느러미)과
부푼 앞모습(`ball`, 가시 공)이 있다.
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import dataclasses
import math
import sys

from sea import (N, QMARK, SIGN, SIGN_D, WAKE, Body, bubble, crop, disc, finish, hand_at, hx, ink, line,
                 phases, raster, side, solid, write)

SID = "pufferanim"
ARROW = ((1, 1), (20, 17))   # 화살표 복어의 부리 끝(핫스팟) · 꼬리 끝

# 옛 그림의 색을 그대로 쓴다
OUT, OCHRE, YEL, LEMON = hx("3a220cff"), hx("b88218ff"), hx("e8c040ff"), hx("fff09aff")
SPOT, SHADE, BELLY, HI = hx("6b3a12ff"), hx("d4c096ff"), hx("f7eed6ff"), hx("fffdf4ff")
ink(OUT, HI, hx("f6e7b4c7"))
SAND, SAND_D = hx("e8d3a0ff"), hx("c4a86cff")
SKIN, HAIR, SHIRT = hx("f2c9a0ff"), hx("4a3226ff"), hx("4a90c8ff")
PENCIL, PENCIL_D, WOOD, LEAD = hx("5a8fd0ff"), hx("2e5a8eff"), hx("e9c9a0ff"), hx("3a3a3aff")

# ── 옆모습 복어: 부리 s=0 → 꼬리 끝 s=1 ─────────────────────────────────────────
# 짧고 통통한 몸(높이가 길이의 절반). 몸통은 s 0.82 에서 끝나고 그 뒤는 부채꼴 꼬리지느러미다
TOP = [(0, 0.0), (0.02, 0.07), (0.06, 0.14), (0.14, 0.21), (0.26, 0.25), (0.4, 0.25), (0.54, 0.21), (0.66, 0.14),
       (0.76, 0.075), (0.82, 0.05)]
BOT = [(0, -0.02), (0.02, -0.08), (0.07, -0.15), (0.16, -0.22), (0.3, -0.25), (0.44, -0.24), (0.58, -0.19),
       (0.7, -0.11), (0.78, -0.06), (0.82, -0.045)]
FINS = {
    "caudal": [(0.78, 0.05), (0.88, 0.12), (0.95, 0.13), (1.0, 0.07), (1.0, -0.07), (0.95, -0.13), (0.88, -0.12),
               (0.78, -0.05)],
    "dorsal": [(0.6, 0.18), (0.66, 0.27), (0.72, 0.25), (0.75, 0.09)],
    "anal": [(0.6, -0.17), (0.66, -0.26), (0.72, -0.24), (0.75, -0.08)],
}
PEC = [(0.3, 0.03), (0.37, 0.1), (0.42, 0.07), (0.42, -0.03), (0.37, -0.08), (0.3, -0.02)]   # 가슴지느러미


def wag(s: float, ph: float) -> float:
    """꼬리를 살랑인다 — 복어는 지느러미로 헤엄쳐서 꼬리는 조금만 흔든다"""
    return 0.035 * math.sin(ph) * max(0.0, (s - 0.74) / 0.26)


def pec(ph: float) -> list:
    """가슴지느러미를 밑동에서 파닥인다 (꼬리보다 두 배 빨리)"""
    a = 0.7 * math.sin(2 * ph)
    b0 = (0.31, 0.0)
    return [(b0[0] + (s - b0[0]) * math.cos(a) - (v - b0[1]) * math.sin(a),
             b0[1] + (s - b0[0]) * math.sin(a) + (v - b0[1]) * math.cos(a)) for s, v in PEC]


def skin(s, v, top, bot):
    """노란 등에 갈색 점, 크림색 배"""
    sep = bot + 0.42 * (top - bot)
    if v < sep:
        return SHADE if v < bot + 0.25 * (sep - bot) else BELLY
    return YEL


def decorate(c) -> None:
    """갈색 점 · 큰 눈(흰자 위 검은 눈동자) · 부리 · 등에 햇빛 한 점"""
    for p in c.mask:
        if c.out.get(p) != YEL or c.region.get(p) != "body":
            continue
        s, v = c.sv(p)
        i, j = round(s * c.L), round(v * c.L * c.T)
        if s > 0.2 and (i % 3 == 0) and ((j + (i // 3)) % 2 == 0):
            c.out[p] = SPOT
    ex, ey = c.at(0.13, 0.08)
    for q in ((ex, ey), (ex + 1, ey), (ex, ey + 1), (ex + 1, ey + 1)):
        c.paint(q, HI)
    c.paint((ex + 1, ey + 1) if c.detail else (ex, ey), OUT)
    if c.detail:
        c.paint((ex + 1, ey), OUT)
    c.paint(c.at(0.02, -0.004), LEMON)   # 부리
    x0 = -0.1 + 1.1 * (c.ph / (2 * math.pi))   # 빛 물결 한 줄
    for p in c.mask:
        if c.region.get(p) != "body" or c.out.get(p) != YEL:
            continue
        s, v = c.sv(p)
        if abs(s - x0 - 0.5 * v) * c.L < 0.7:
            c.out[p] = LEMON


PUFF = Body(
    top=TOP, bot=BOT, fins=FINS, order=("body", "dorsal", "anal", "caudal"),
    skin=skin, fin_ink=lambda r, s, v: LEMON if r == "pec" else OCHRE,
    bend=lambda s, v, ph: (s, v + wag(s, ph)), unbend=lambda s, v, ph: (s, v - wag(s, ph)),
    decorate=decorate, thick=1.0, length=1.05, lined=("pec",))


def fish(head, tail, ph, size=None, flip=False, detail=True):
    """옆모습 복어 한 장. 가슴지느러미는 몸 위에 그리고 위상마다 파닥인다. 판 밖은 자른다"""
    body = dataclasses.replace(PUFF, fins={**FINS, "pec": pec(ph)}, order=("pec",) + PUFF.order)
    return crop(*side(body, head, tail, ph, size, 0.0, flip, detail))


def arrow_fish(ph: float, size: float = 1.05) -> dict:
    return fish(*ARROW, ph, size, detail=size >= 1.05)[0]


# ── 부푼 앞모습 ───────────────────────────────────────────────────────────────
def ball(f: dict, cx: float, cy: float, r: float, spike: float, blink: bool = False, long=()) -> set:
    """부푼 복어를 앞에서: 둥근 몸(위는 노랑에 갈색 점, 아래는 크림) · 큰 눈 둘 · 오므린 입 · 몸 둘레 가시.
    spike 는 가시 길이(칸, 0 이면 없음), long 은 더 길게 뺄 가시 방향(라디안)들. 몸 칸 집합을 돌려준다"""
    for i in range(16):
        a = 2 * math.pi * i / 16
        ln = spike + (4.5 if any(abs(math.remainder(a - b, 2 * math.pi)) < 0.01 for b in long) else 0)
        if ln <= 0:
            continue
        line(f, (cx + (r - 0.5) * math.cos(a), cy + (r - 0.5) * math.sin(a)),
             (cx + (r + ln) * math.cos(a), cy + (r + ln) * math.sin(a)), SPOT)
    body = disc(cx, cy, r)

    def col(p):
        dx, dy = p[0] + 0.5 - cx, p[1] + 0.5 - cy
        if dy > r * 0.15:
            return BELLY if dy < r * 0.75 else SHADE
        if (p[0] * 2 + p[1] * 3) % 5 == 0:
            return SPOT
        return LEMON if dx < -r * 0.3 and dy < -r * 0.3 else YEL
    solid(f, body, col)
    for sgn in (-1, 1):   # 눈
        ex, ey = math.floor(cx + sgn * r * 0.45), math.floor(cy - r * 0.2)
        if blink:
            f[ex - 1, ey + 1] = f[ex, ey + 1] = f[ex + 1, ey + 1] = OUT
        else:
            for q in ((ex - 1, ey), (ex, ey), (ex - 1, ey + 1), (ex, ey + 1), (ex + 1, ey), (ex + 1, ey + 1)):
                f[q] = HI
            f[ex, ey] = f[ex, ey + 1] = OUT
    mx, my = math.floor(cx), math.floor(cy + r * 0.4)
    f[mx, my] = OUT   # 오므린 입
    f[mx - 1, my] = f[mx + 1, my] = SHADE
    return body


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    return [finish(arrow_fish(ph)) for ph in phases()]


def busy() -> list[dict]:
    """모래에 판 둥근 무늬(복어 만다라) — 판 골이 한 바퀴를 돌며 차례로 짙어진다"""
    frames = []
    cx, cy, R = 22.5, 22.5, 8.0
    for k, ph in enumerate(phases()):
        f = {}
        for p in disc(cx, cy, R):
            f[p] = SAND
        for i in range(12):   # 방사형 골
            a = 2 * math.pi * i / 12
            lit = (i - k) % 12 < 4
            for d in range(3, 8):
                f[math.floor(cx + d * math.cos(a)), math.floor(cy + d * math.sin(a))] = OCHRE if lit else SAND_D
        for p in disc(cx, cy, 2.2):
            f[p] = SAND_D
        f.update(arrow_fish(ph, 0.74))
        frames.append(finish(f))
    return frames


def help_() -> list[dict]:
    """복어 살갗 물음표가 부풀었다 오그라든다 — 부풀면 가시가 돋는다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = arrow_fish(ph, 0.74)
        puff = 0.5 + 0.5 * math.sin(ph)
        r = 1.05 + 0.45 * puff
        cells = [(17.5 + 2 * i, 13.5 + 2 * j) for j, row in enumerate(QMARK) for i, ch in enumerate(row) if ch == "#"]
        m = set()
        for x, y in cells:
            m |= disc(x, y, r)
        if puff > 0.6:
            for x, y in cells[:6]:
                a = math.atan2(y - 17, x - 21.5)
                f[math.floor(x + (r + 1.2) * math.cos(a)), math.floor(y + (r + 1.2) * math.sin(a))] = SPOT
        solid(f, m, lambda p: SPOT if (p[0] * 2 + p[1] * 3) % 5 == 0 else YEL)
        frames.append(finish(f))
    return frames


def person() -> list[dict]:
    """복어 풍선을 든 아이 — 가시 없는 동그란 풍선이 끈 끝에서 둥실거린다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        px, py = 24.5, 21.5   # 아이 얼굴 가운데
        solid(f, raster([(px - 3.0, py + 3.0), (px + 3.0, py + 3.0), (px + 3.4, py + 9.5), (px - 3.4, py + 9.5)]),
              SHIRT)
        solid(f, disc(px, py, 3.3), lambda p: HAIR if p[1] + 0.5 < py - 1.0 else SKIN)
        f[math.floor(px) - 1, math.floor(py)] = OUT
        f[math.floor(px) + 1, math.floor(py)] = OUT
        hx_, hy = px - 4.5, py + 0.5   # 들어 올린 손
        line(f, (px - 2.6, py + 4.0), (hx_, hy), SKIN, 0.5)
        bx, by = 24.5 + 1.2 * math.sin(ph), 7.5 + 0.7 * math.cos(ph)
        for i in range(10):   # 끈: 살짝 휜다
            t = i / 9
            f.setdefault((math.floor(hx_ + (bx - hx_) * t + 0.8 * math.sin(math.pi * t)),
                          math.floor(hy + (by + 4.2 - hy) * t)), OUT)
        ball(f, bx, by, 4.4, 0.0, blink=k in (8, 9))
        f.update(arrow_fish(ph, 0.74))
        frames.append(finish(f))
    return frames


def pin() -> list[dict]:
    """부푼 복어가 머리인 지도 핀 — 통통 튀고, 땅에 닿을 때 눈을 깜빡인다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 15.5 + dy
        solid(f, raster([(cx - 2.6, cy + 3.5), (cx + 2.6, cy + 3.5), (cx, cy + 12.5)]), SIGN, SIGN_D)
        ball(f, cx, cy, 5.0, 1.4, blink=dy == 0)
        for x in range(18, 28):   # 그림자
            f[x, 29] = WAKE[3]
        f.update(arrow_fish(ph, 0.74))
        frames.append(finish(f))
    return frames


def we() -> list[dict]:
    """지느러미를 파닥이며 왼쪽으로 간다 — 꼬리 뒤로 작은 물방울이 줄지어 샌다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for j in range(3):
            t = (k / N + j / 3) % 1
            bubble(f, 26.0 + 4 * t, 14.0 - 1.5 * math.sin(2 * math.pi * t + j), 0.6 + 0.5 * t)
        f.update(fish((2, 15), (27, 15), ph, 1.05)[0])
        frames.append(finish(f))
    return frames


def ns() -> list[dict]:
    """부풀면 떠오르고 오그라들면 가라앉는다 — 가장 부푼 자리가 맨 위"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        puff = 0.5 - 0.5 * math.cos(ph)   # 0 → 1 → 0
        cy = 22.0 - 11.0 * puff
        r = 4.5 + 3.5 * puff
        ball(f, 15.5, cy, r, 2.2 * puff - 0.4, blink=k == 0)
        for j in range(2):   # 가라앉을 때 위로 남는 물방울
            if puff < 0.6:
                t = (k / N + j / 2) % 1
                bubble(f, 13.5 + 4 * j, cy - r - 2 - 4 * t, 0.7)
        frames.append(finish(f))
    return frames


def nesw() -> list[dict]:
    """오른쪽 위로 지느러미를 파닥이며 떠오른다 — 뒤로 물방울"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for j in range(3):
            t = (k / N + j / 3) % 1
            bubble(f, 6.0 - 3 * t + 0.6 * math.sin(ph + j), 26.0 + 2 * t, 0.6 + 0.4 * t)
        rise = 1.2 * math.sin(ph)
        f.update(fish((round(29 + rise), round(2 - rise)), (round(8 + rise), round(23 - rise)), ph, 1.05)[0])
        frames.append(finish(f))
    return frames


def nwse() -> list[dict]:
    """오른쪽 아래 모래에 대고 물을 뿜어 파묻힌 먹이를 판다 — 물줄기에 모래가 튄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for x in range(12, 31):   # 모래 비탈
            for y in range(max(1, 44 - x), 31):
                f[x, y] = SAND if (x + y) % 5 else SAND_D
        f.update(fish((19, 19), (1, 1), ph, 1.05)[0])
        jet = 0.5 + 0.5 * math.sin(2 * ph)
        for d in range(1, 1 + round(2 + 3 * jet)):   # 물줄기
            f[19 + d, 19 + d] = WAKE[1] if d % 2 else WAKE[2]
        for j in range(4):   # 튀는 모래
            t = (k / N + j / 4) % 1
            a = -math.pi / 4 + (j - 1.5) * 0.5
            f[math.floor(24 + 5 * t * math.cos(a)), math.floor(24 + 5 * t * math.sin(a) - 3 * t * (1 - t))] = SAND_D
        frames.append(finish(f))
    return frames


def up() -> list[dict]:
    """부리를 위로 들고 물을 뿜는다 — 물줄기가 솟았다 흩어진다. 부리 끝이 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        f.update(fish((15, 9), (16, 33), ph, 1.0)[0])
        t = (k / N) % 1
        top = round(8 - 6 * math.sin(math.pi * t))
        for y in range(top, 9):
            f[15, y] = WAKE[1]
        if t > 0.5:
            for sgn in (-1, 1):
                f[15 + sgn * round(1 + 3 * (t - 0.5)), top + round(4 * (t - 0.5))] = WAKE[1]
        frames.append(finish(f))
    return frames


def pen() -> list[dict]:
    """연필을 부리로 갉아 먹는다(복어 이빨은 조개도 깬다) — 볼이 오물거리고 부스러기가 떨어진다. 연필심이 핫스팟"""
    frames = []
    TIP, BACK = (1.5, 29.5), (15.0, 16.0)
    for k, ph in enumerate(phases()):
        f = {}
        ux, uy = BACK[0] - TIP[0], BACK[1] - TIP[1]
        d = math.hypot(ux, uy)
        ux, uy = ux / d, uy / d
        cone = (TIP[0] + ux * 3.5, TIP[1] + uy * 3.5)
        line(f, (cone[0] - uy * 0.9, cone[1] + ux * 0.9), (BACK[0] - uy * 0.9, BACK[1] + ux * 0.9), PENCIL_D)
        line(f, cone, BACK, PENCIL)
        line(f, (cone[0] + uy * 0.9, cone[1] - ux * 0.9), (BACK[0] + uy * 0.9, BACK[1] - ux * 0.9), PENCIL_D)
        for p in raster([(TIP[0] - 0.3, TIP[1] + 0.3), (cone[0] - uy * 1.6, cone[1] + ux * 1.6),
                         (cone[0] + uy * 1.6, cone[1] - ux * 1.6)], 5):
            f[p] = WOOD
        f[math.floor(TIP[0] + ux * 0.8), math.floor(TIP[1] + uy * 0.8)] = LEAD
        f[math.floor(TIP[0]), math.floor(TIP[1])] = LEAD
        chew = round(0.8 * math.sin(3 * ph))
        f.update(fish((14 + chew, 17 - chew), (31, 1), ph, 1.0)[0])
        for j in range(2):   # 부스러기
            t = (k / N + j / 2) % 1
            f[math.floor(12 - 2 * j + 1.5 * t), math.floor(20 + 7 * t)] = WOOD
        frames.append(finish(f))
    return frames


def hand() -> list[dict]:
    """손가락 끝에 헤엄쳐 와 닿자 깜짝 놀라 부푼다 — 그러고는 오그라들며 물러난다"""
    frames = []
    X0, Y0 = 9, 1
    for k, ph in enumerate(phases()):
        f = {}
        hand_at(f, X0, Y0, SKIN)
        if k < 5:   # 다가온다
            t = k / 5
            f.update(fish((round(16 + 2 * (1 - t)), round(16 + 6 * (1 - t))), (round(30 + 2 * (1 - t)),
                          round(26 + 6 * (1 - t))), ph, 1.0)[0])
        else:       # 부풀었다 오그라들며 물러난다
            t = (k - 5) / 6
            puff = 1 - t
            ball(f, 21.0 + 2 * t, 20.5 + 3 * t, 4.5 + 3.0 * puff, 2.0 * puff - 0.3, blink=False)
            if k in (5, 6):
                for sgn in (-1, 1):
                    f[math.floor(21 + sgn * 9), 12] = SPOT
                    f[math.floor(21 + sgn * 8), 11] = SPOT
        frames.append(finish(f))
    return frames


def cross() -> list[dict]:
    """부푼 복어를 앞에서 — 위아래 양옆 가시 넷이 길게 뻗어 조준선이 된다. 가운데(코)가 핫스팟"""
    frames = []
    C = (15, 15)
    for k, ph in enumerate(phases()):
        f = {}
        grow = 0.5 + 0.5 * math.sin(ph)
        ball(f, C[0] + 0.5, C[1] + 0.5, 7.0, 0.6 + 0.9 * grow, blink=k in (6, 7),
             long=(0.0, math.pi / 2, math.pi, -math.pi / 2))
        f[C] = SIGN
        frames.append(finish(f))
    return frames


def ibeam() -> list[dict]:
    """복어 살갗 I 기둥 — 옆구리 가시가 돋았다 들어간다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        grow = 0.5 + 0.5 * math.sin(ph)
        m = {(x, y) for x in range(3, 8) for y in range(1, 24)} | \
            {(x, y) for x in range(1, 10) for y in list(range(1, 4)) + list(range(21, 24))}
        if grow > 0.3:
            for y in range(6, 20, 3):
                for x in (2, 8):
                    f[x, y] = SPOT
                if grow > 0.7:
                    f[1, y] = f[9, y] = SPOT
        solid(f, m, lambda p: SPOT if (p[0] * 2 + p[1] * 3) % 5 == 0 else BELLY if p[0] == 6 else YEL)
        frames.append(finish(f))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "help": help_, "person": person, "pin": pin, "we": we, "ns": ns,
         "nesw": nesw, "nwse": nwse, "up": up, "pen": pen, "hand": hand, "cross": cross, "ibeam": ibeam}
HOT = {"arrow": ARROW[0], "busy": ARROW[0], "help": ARROW[0], "person": ARROW[0], "pin": ARROW[0],
       "we": (15, 15), "ns": (15, 16), "nesw": (18, 13), "nwse": (12, 12), "up": (15, 9), "pen": (1, 29),
       "hand": (13, 1), "cross": (15, 15), "ibeam": (5, 12)}


def main() -> None:
    write(SID, {r: (lambda r=r: (SCENE[r](), HOT[r])) for r in SCENE}, sys.argv[1:] or None)


if __name__ == "__main__":
    main()

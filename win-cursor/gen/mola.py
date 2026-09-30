# SPDX-License-Identifier: Apache-2.0
"""개복치(molaanim) 구성표 그림 `art/molaanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/mola.py [역할...]     그림을 쓴다 (역할을 안 주면 새로 그리는 칸 전부)

첫 벌(2026-09-24)은 개복치 색을 입힌 화살표·양방향 화살표라 복제품 같다는 말을 들었다(2026-10-01 사용자).
그래서 칸마다 개복치가 하는 짓을 따로 그린다(`SCENE`) — 도는 해(작업 중, 영어 이름이 sunfish) · 식은땀 흘리는
물음표(도움말, 잘 죽는다는 개복치 밈) · 스노클 잠수부(사람) · 해파리 핀(핀, 개복치 밥) · 옆모습으로 가로질러
헤엄(좌우 — 볕 쬐는 앞모습·위에서 본 그림은 32칸에서 선·종으로 읽혀 버렸다) · 앞모습 위아래 지느러미 젓기(위아래) ·
비스듬히 헤엄(대각선) · 물 밖으로 뛰어오르기(위) · 연필이 개복치 낙서를 그려 나가기(펜 — 입으로 쓰는 선은 몸에
가려 안 보였다) · 손가락이 닿자 별 보고 기절해 넋이 빠져나가기(손) · 위에서 본 보름달물해파리(십자) ·
홀쭉한 앞모습(I빔).
wait · move · no 는 두고 안 그린다.
몸은 옆모습(`MOLA`, 둥근 원반 몸 · 높은 등·뒷지느러미 · 꼬리 대신 물결 진 키지느러미(clavus) · 작은 입)과
앞모습(`front`, 납작한 몸 위아래로 지느러미)이 있다. 개복치는 등·뒷지느러미를 좌우로 번갈아 저어 헤엄쳐서
옆모습에서는 두 지느러미가 앞뒤로 엇갈려 기운다(`scull`).
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import dataclasses
import math
import sys

from sea import (N, QMARK, WAKE, Body, bubble, crop, disc, finish, hand_at, hx, ink, inside, line, phases, raster,
                 side, solid, splash, under, water, write)

SID = "molaanim"
ARROW = ((1, 1), (17, 17))   # 화살표 개복치의 입(핫스팟) · 키지느러미 끝

# 옛 그림의 색을 그대로 쓴다
OUT, FIN, DARK, MID = hx("1a2229ff"), hx("4b5663ff"), hx("6e7a86ff"), hx("8e9aa6ff")
LIGHT, TINT, PALE, HI = hx("aab5c0ff"), hx("bfe0eeff"), hx("e8f0f6ff"), hx("f8fbfdff")
ink(OUT, HI, hx("c9d6e0c7"))
SUN, SUN_D = hx("ffd24aff"), hx("e8a020ff")
JELLY, JELLY_D, JELLY_HI = hx("f4c4dcff"), hx("c87aa8ff"), hx("fff0f8ff")
SKIN, SUIT, MASK, FLIP = hx("f2c9a0ff"), hx("2e3a4aff"), hx("7cc4d8ff"), hx("f0b030ff")
STAR = hx("ffe36aff")

# ── 옆모습 개복치: 입 s=0 → 키지느러미 끝 s=1 ────────────────────────────────────
# 몸은 둥근 원반(높이가 길이의 2/3), 등·뒷지느러미는 몸 뒤쪽에서 높이 솟는다
TOP = [(0, 0.0), (0.02, 0.08), (0.08, 0.19), (0.18, 0.28), (0.32, 0.33), (0.48, 0.33), (0.62, 0.29), (0.74, 0.22),
       (0.84, 0.15)]
BOT = [(0, -0.03), (0.03, -0.1), (0.1, -0.21), (0.22, -0.29), (0.38, -0.32), (0.54, -0.3), (0.66, -0.25),
       (0.76, -0.19), (0.84, -0.14)]
FINS = {
    "clavus": [(0.8, 0.18), (0.9, 0.17), (0.95, 0.12), (1.0, 0.08), (0.96, 0.03), (1.0, -0.02), (0.96, -0.07),
               (0.99, -0.12), (0.9, -0.16), (0.8, -0.17)],
    "dorsal": [(0.58, 0.27), (0.64, 0.46), (0.7, 0.57), (0.76, 0.52), (0.77, 0.21)],
    "anal": [(0.58, -0.26), (0.64, -0.45), (0.7, -0.56), (0.76, -0.51), (0.77, -0.2)],
    "pec": [(0.26, 0.02), (0.31, 0.07), (0.36, 0.06), (0.36, -0.03), (0.31, -0.05), (0.26, -0.01)],
}


def scull(v: float, ph: float) -> float:
    """등지느러미와 뒷지느러미가 앞뒤로 엇갈려 기운다 — 몸(|v| < 0.3)은 그대로"""
    return 0.08 * math.sin(ph) * (max(0.0, v - 0.3) - max(0.0, -v - 0.3)) / 0.27


def skin(s, v, top, bot):
    """등은 짙은 은회색, 가운데 옅은 회색, 배는 흰빛"""
    r = (v - bot) / max(top - bot, 1e-6)
    if r > 0.74:
        return MID
    return LIGHT if r > 0.3 else PALE


def fin_ink(r, s, v):
    if r == "clavus":
        return DARK
    if r == "pec":
        return FIN
    return FIN if abs(v) > 0.38 else DARK


def eyes(c, kind: str = "open") -> None:
    """작고 동그란 눈(흰 테 속 검은 눈동자) · 뾰족 입 · 아가미 구멍. kind 가 "x" 면 기절한 X 눈"""
    ex, ey = c.at(0.13, 0.08)
    if kind == "x":
        for q in ((ex - 1, ey - 1), (ex + 1, ey - 1), (ex, ey), (ex - 1, ey + 1), (ex + 1, ey + 1)):
            c.paint(q, OUT)
    else:
        for q in ((ex, ey), (ex + 1, ey), (ex, ey + 1), (ex + 1, ey + 1)):
            c.paint(q, HI)
        c.paint((ex, ey) if c.detail else (ex, ey + 1), OUT)
    c.paint(c.at(0.035, -0.02), DARK)   # 입
    c.paint(c.at(0.24, 0.06), DARK)     # 아가미 구멍


def decorate(c, kind: str = "open") -> None:
    """옅은 얼룩 · 눈 · 입 · 몸을 지나는 빛 물결"""
    for p in c.mask:
        if c.out.get(p) != LIGHT or c.region.get(p) != "body":
            continue
        s, v = c.sv(p)
        i, j = round(s * c.L / 1.5), round(v * c.L * c.T / 1.5)
        if s > 0.2 and (i * 2 + j * 3) % 7 == 0:
            c.out[p] = PALE
    x0 = -0.1 + 1.1 * (c.ph / (2 * math.pi))
    for p in c.mask:
        if c.region.get(p) != "body" or c.out.get(p) not in (MID, LIGHT):
            continue
        s, v = c.sv(p)
        if abs(s - x0 - 0.4 * v) * c.L < 0.6:
            c.out[p] = TINT
    eyes(c, kind)


MOLA = Body(
    top=TOP, bot=BOT, fins=FINS, order=("pec", "body", "dorsal", "anal", "clavus"),
    skin=skin, fin_ink=fin_ink,
    bend=lambda s, v, ph: (s + scull(v, ph), v), unbend=lambda s, v, ph: (s - scull(v, ph), v),
    decorate=decorate, thick=1.0, length=1.0, small=("pec",), lined=("pec",))
FAINT = dataclasses.replace(MOLA, decorate=lambda c: decorate(c, "x"))
NIB = dataclasses.replace(MOLA, bend=lambda s, v, ph: (s + scull(max(v, 0.0), ph), v),
                          unbend=lambda s, v, ph: (s - scull(max(v, 0.0), ph), v))   # 뒷지느러미(펜촉)는 가만히


def fish(head, tail, ph, size=None, flip=False, detail=True, body=MOLA):
    """옆모습 개복치 한 장. 판 밖은 자른다"""
    return crop(*side(body, head, tail, ph, size, 0.0, flip, detail))


def arrow_fish(ph: float, size: float = 1.0) -> dict:
    return fish(*ARROW, ph, size, detail=size >= 1.0)[0]


# ── 앞모습 ───────────────────────────────────────────────────────────────────
def front(f: dict, cx: float, cy: float, hb: float, w: float, hf: float, sway: float, pec: float = 0.0,
          horiz: bool = False, blink: bool = False, serif: float = 0.0) -> set:
    """앞에서 본 개복치: 납작한 몸(반너비 w, 반높이 hb) 위아래로 지느러미(길이 hf). sway 는 등지느러미 끝이
    옆으로 기운 칸(뒷지느러미는 반대로), pec 는 가슴지느러미 끝이 오르내린 칸. horiz 면 옆으로 누운 자세
    (등지느러미가 왼쪽). serif 는 지느러미 끝을 옆으로 넓힌 반너비(I빔). 몸 칸 집합을 돌려준다"""
    def to_tu(x, y):
        return (y - cy, x - cx) if horiz else (x - cx, y - cy)

    def to_xy(t, u):
        return (cx + u, cy + t) if horiz else (cx + t, cy + u)

    top = -(hb + hf)
    fb, ft = max(1.3, w * 0.5), 0.6 if w < 3 else 0.9   # 지느러미 밑동 · 끝 반너비
    fins = {
        "dorsal": [(-fb, -hb * 0.6), (fb, -hb * 0.6), (sway + ft, top), (sway - ft, top)],
        "anal": [(-fb, hb * 0.6), (fb, hb * 0.6), (-sway + ft, -top), (-sway - ft, -top)],
        "pl": [(-w + 0.4, hb * 0.05 - 0.9), (-w - 1.8, hb * 0.05 + pec - 0.5), (-w - 1.8, hb * 0.05 + pec + 0.5),
               (-w + 0.4, hb * 0.05 + 0.9)],
        "pr": [(w - 0.4, hb * 0.05 - 0.9), (w + 1.8, hb * 0.05 + pec - 0.5), (w + 1.8, hb * 0.05 + pec + 0.5),
               (w - 0.4, hb * 0.05 + 0.9)],
    }
    if serif:
        fins["st"] = [(sway - serif, top - 0.2), (sway + serif, top - 0.2), (sway + serif, top + 1.3),
                      (sway - serif, top + 1.3)]
        fins["sb"] = [(-sway - serif, -top + 0.2), (-sway + serif, -top + 0.2), (-sway + serif, -top - 1.3),
                      (-sway - serif, -top - 1.3)]
    region, mask = {}, set()
    R = hb + hf + 3
    for y in range(math.floor(cy - R), math.ceil(cy + R) + 1):
        for x in range(math.floor(cx - R), math.ceil(cx + R) + 1):
            hits = {}
            for j in range(4):
                for i in range(4):
                    t, u = to_tu(x + (i + 0.5) / 4, y + (j + 0.5) / 4)
                    if (t / w) ** 2 + (u / hb) ** 2 <= 1:
                        hits["body"] = hits.get("body", 0) + 1
                        continue
                    for name, poly in fins.items():
                        if inside(poly, t, u):
                            hits[name] = hits.get(name, 0) + 1
                            break
            if sum(hits.values()) >= 8:
                mask.add((x, y))
                region[x, y] = "body" if hits.get("body", 0) * 3 >= sum(hits.values()) else max(hits, key=hits.get)

    def col(p):
        t, u = to_tu(p[0] + 0.5, p[1] + 0.5)
        r = region[p]
        if r != "body":
            return FIN if abs(u) > hb + 1 or r[0] == "p" or r[0] == "s" else DARK
        if u > hb * 0.45:
            return PALE
        return MID if abs(t) > w * 0.55 else LIGHT
    solid(f, mask, col)
    for sgn in (-1, 1):   # 눈은 몸 양옆 볼록한 자리 — 너비가 되면 흰 테를 안쪽에 둔다
        ex, ey = to_xy(sgn * (w - 1.2), -hb * 0.35)
        q = (math.floor(ex), math.floor(ey))
        if w >= 3:
            wx, wy = to_xy(sgn * (w - 2.2), -hb * 0.35)
            f[math.floor(wx), math.floor(wy)] = DARK if blink else HI
        if q in mask:
            f[q] = DARK if blink else OUT
    mx, my = to_xy(0, -hb * 0.05)   # 뾰족 내민 입
    f[math.floor(mx), math.floor(my)] = DARK
    return mask


# ── 소품 ─────────────────────────────────────────────────────────────────────
def jelly(f: dict, cx: float, cy: float, r: float, squash: float, tip=None) -> None:
    """옆에서 본 해파리: 둥근 갓 · 갓 속 분홍 고리 · 아래로 늘어진 촉수. tip 을 주면 촉수가 그 한 점으로 모인다(핀)"""
    rx, ry = r * (1 + 0.12 * squash), r * (0.8 - 0.12 * squash)
    bell = {(x, y) for x in range(math.floor(cx - rx) - 1, math.ceil(cx + rx) + 1)
            for y in range(math.floor(cy - ry) - 1, math.ceil(cy) + 1)
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1 and y + 0.5 <= cy + 0.6}
    for i in range(4):   # 촉수
        x0 = cx + (i - 1.5) * rx * 0.45
        if tip:
            line(f, (x0, cy + 0.5), tip, JELLY_D)
        else:
            for d in range(1, round(r * 1.6)):
                f[math.floor(x0 + 0.7 * math.sin(d * 0.9 + i + squash * 2)), math.floor(cy + d)] = JELLY_D
    solid(f, bell, lambda p: JELLY_HI if p[1] + 0.5 < cy - ry * 0.5 and p[0] + 0.5 < cx else JELLY, JELLY_D)
    for sgn in (-1, 1):   # 생식선 고리
        f[math.floor(cx + sgn * rx * 0.35), math.floor(cy - ry * 0.3)] = JELLY_D


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    return [finish(arrow_fish(ph)) for ph in phases()]


def busy() -> list[dict]:
    """도는 해 — 영어 이름이 sunfish(해물고기)다. 빛살이 한 바퀴를 돌며 긴 것과 짧은 것이 번갈아 간다"""
    frames = []
    cx, cy = 22.5, 22.5
    for k, ph in enumerate(phases()):
        f = {}
        for i in range(8):
            a = 2 * math.pi * (i / 8 + k / N / 8)
            ln = 7.8 if i % 2 == 0 else 6.4
            line(f, (cx + 4.6 * math.cos(a), cy + 4.6 * math.sin(a)), (cx + ln * math.cos(a), cy + ln * math.sin(a)),
                 SUN_D, 0.5)
        solid(f, disc(cx, cy, 4.0), lambda p: HI if (p[0] - 20) ** 2 + (p[1] - 20) ** 2 < 2 else SUN, SUN_D)
        f.update(arrow_fish(ph, 0.74))
        frames.append(finish(f))
    return frames


def help_() -> list[dict]:
    """지느러미 빛 물음표 옆으로 식은땀 한 방울이 흘러내린다 — 조금만 놀라도 죽는다는 개복치 밈"""
    frames = []
    for k, ph in enumerate(phases()):
        f = arrow_fish(ph, 0.74)
        cells = {(17 + 2 * i + a, 13 + 2 * j + b) for j, row in enumerate(QMARK) for i, ch in enumerate(row)
                 if ch == "#" for a in (0, 1) for b in (0, 1)}
        solid(f, cells, lambda p: MID if (p[0] + p[1]) % 2 else LIGHT, FIN)
        t = k / N
        dy = round(4 * t)
        drop = {(28, 12 + dy), (27, 13 + dy), (28, 13 + dy), (27, 14 + dy), (28, 14 + dy)}
        solid(f, drop, TINT, hx("3f8faeff"))
        frames.append(finish(f))
    return frames


def person() -> list[dict]:
    """엎드려 헤엄치는 스노클 잠수부 — 오리발을 번갈아 찬다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        y = 23.5
        kick = math.sin(ph)
        for sgn in (-1, 1):   # 다리 · 오리발
            ky = y + sgn * 0.9 + sgn * kick * 0.8
            line(f, (24.5, y + sgn * 0.9), (27.5, ky), SUIT, 0.7)
            solid(f, raster([(27.3, ky - 1.0), (30.8, ky - 1.3 + sgn * kick), (30.8, ky + 1.3 + sgn * kick),
                             (27.3, ky + 1.0)]), FLIP)
        solid(f, raster([(16.5, y - 2.2), (25.5, y - 2.0), (25.5, y + 2.0), (16.5, y + 2.2)]), SUIT)   # 몸통
        line(f, (18.0, y + 1.5), (13.0, y + 4.5), SUIT, 0.6)   # 팔
        solid(f, disc(14.5, y - 0.5, 3.3), lambda p: MASK if p[1] + 0.5 < y - 0.5 and p[0] + 0.5 < 15.5 else SKIN)
        line(f, (16.5, y - 3.5), (16.5, 16.0), FLIP, 0.4)   # 스노클
        for j in range(2):   # 스노클 물방울
            t = (k / N + j / 2) % 1
            bubble(f, 17.0 + 1.2 * math.sin(2 * math.pi * t + j), 14.5 - 3 * t, 0.6 + 0.3 * t)
        f.update(arrow_fish(ph, 0.74))
        frames.append(finish(f))
    return frames


def pin() -> list[dict]:
    """해파리 핀 — 갓이 오므렸다 펴지고, 촉수가 모인 끝이 바늘이다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        jelly(f, 22.5, 16.5, 5.0, math.sin(ph), tip=(22.5, 28.5))
        for x in range(19, 27):
            f[x, 29] = WAKE[3]
        f.update(arrow_fish(ph, 0.74))
        frames.append(finish(f))
    return frames


def we() -> list[dict]:
    """개복치 하면 떠오르는 그 옆모습으로 왼쪽으로 간다 — 높은 두 지느러미를 엇갈려 젓고 물방울이 뒤로 샌다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for j in range(3):
            t = (k / N + j / 3) % 1
            bubble(f, 26.5 + 3 * t, 15.0 - 1.5 * math.sin(2 * math.pi * t + j), 0.6 + 0.5 * t)
        f.update(fish((2, 15), (27, 15), ph, 0.96)[0])
        frames.append(finish(f))
    return frames


def ns() -> list[dict]:
    """앞모습 — 등·뒷지느러미를 좌우로 번갈아 젓고 가슴지느러미를 파닥인다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        front(f, 15.5, 15.5, 6.5, 4.6, 7.8, 2.6 * math.sin(ph), 1.0 * math.sin(2 * ph), blink=k in (9, 10))
        frames.append(finish(f))
    return frames


def nesw() -> list[dict]:
    """왼쪽 위로 헤엄친다 — 지느러미가 오른쪽 위·왼쪽 아래로 뻗어 대각선이 된다. 물방울이 뒤로 샌다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for j in range(3):
            t = (k / N + j / 3) % 1
            bubble(f, 25.0 + 3 * t, 26.0 + 2 * t - 1.0 * math.sin(2 * math.pi * t + j), 0.6 + 0.5 * t)
        f.update(fish((5, 5), (24, 24), ph, 0.96)[0])
        frames.append(finish(f))
    return frames


def nwse() -> list[dict]:
    """오른쪽 위로 떠오른다 — 지느러미가 왼쪽 위·오른쪽 아래로 뻗는다. 입 앞으로 물방울"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for j in range(3):
            t = (k / N + j / 3) % 1
            bubble(f, 3.5 + 1.2 * math.sin(2 * math.pi * t + j), 27.0 - 3 * t, 0.6 + 0.4 * t)
        f.update(fish((26, 5), (7, 24), ph, 0.96)[0])
        frames.append(finish(f))
    return frames


def up() -> list[dict]:
    """물 밖으로 뛰어오른다 — 몸이 솟았다 내려앉고 물이 튄다. 입 끝이 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        lift = math.sin(math.pi * k / N)
        hy = round(5 - 4 * lift)
        body = fish((15, hy), (15, hy + 22), ph, 1.0)[0]
        f.update(under(body, 28))
        water(f, 1, 30, 28, k)
        splash(f, 15.5, 27.0, k, 4, 8.0, 3.0 + 2 * lift)
        frames.append(finish(f))
    return frames


def pen() -> list[dict]:
    """연필이 개복치를 한 획씩 그려 간다 — 윤곽이 한 바퀴 돌며 이어지고, 다 그리면 눈을 찍는다. 연필심이 핫스팟"""
    frames = []
    _, m = fish((9, 22), (26, 22), 0.0, 0.95)
    edge_ = sorted((p for p in m if any(q not in m for q in ((p[0] + 1, p[1]), (p[0] - 1, p[1]),
                                                            (p[0], p[1] + 1), (p[0], p[1] - 1)))),
                   key=lambda p: math.atan2(p[1] + 0.5 - 22.5, -(p[0] + 0.5 - 16.0)) % (2 * math.pi))
    TIP, BACK = (1.5, 29.5), (8.0, 13.0)
    for k, ph in enumerate(phases()):
        f = {}
        n = round(len(edge_) * min(1.0, (k + 1) / 9))
        for p in edge_[:n]:
            f[p] = FIN
        if k >= 9:
            f[11, 20] = OUT   # 눈
        ux, uy = BACK[0] - TIP[0], BACK[1] - TIP[1]
        d = math.hypot(ux, uy)
        ux, uy = ux / d, uy / d
        cone = (TIP[0] + ux * 3.5, TIP[1] + uy * 3.5)
        wob = 0.6 * math.sin(3 * ph)   # 쓰는 손 떨림
        line(f, (cone[0] - uy * 0.9, cone[1] + ux * 0.9), (BACK[0] - uy * 0.9 + wob, BACK[1] + ux * 0.9), SUIT)
        line(f, cone, (BACK[0] + wob, BACK[1]), MASK)
        line(f, (cone[0] + uy * 0.9, cone[1] - ux * 0.9), (BACK[0] + uy * 0.9 + wob, BACK[1] - ux * 0.9), SUIT)
        for p in raster([(TIP[0] - 0.3, TIP[1] + 0.3), (cone[0] - uy * 1.6, cone[1] + ux * 1.6),
                         (cone[0] + uy * 1.6, cone[1] - ux * 1.6)], 5):
            f[p] = SKIN
        f[math.floor(TIP[0] + ux * 0.8), math.floor(TIP[1] + uy * 0.8)] = OUT
        f[math.floor(TIP[0]), math.floor(TIP[1])] = OUT
        frames.append(finish(f))
    return frames


def hand() -> list[dict]:
    """손가락 끝에 다가와 닿자 깜짝 놀라 기절한다 — 배를 뒤집고 X 눈으로 가라앉는다 (여린 개복치 밈)"""
    frames = []
    X0, Y0 = 9, 1
    for k, ph in enumerate(phases()):
        f = {}
        hand_at(f, X0, Y0, SKIN)
        if k < 5:   # 다가온다
            t = k / 5
            d = round(5 * (1 - t))
            f.update(fish((14 + d, 15 + d), (28 + d, 29 + d), ph, 0.9, detail=True)[0])
        elif k == 5:   # 찌릿
            f.update(fish((14, 15), (28, 29), ph, 0.9)[0])
            for dx, dy in ((0, -2), (0, 2), (-2, 0), (2, 0), (0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)):
                f[23 + dx, 11 + dy] = STAR
        else:          # 배를 뒤집고 가라앉는다
            t = (k - 6) / 5
            d = round(2 * t)
            f.update(fish((13, 21 + d), (30, 21 + d), 0.0, 0.88, flip=True, body=FAINT)[0])
            wx, wy = 28.0 + 0.6 * math.sin(4 * t), 14.5 - 7 * t   # 빠져나가는 넋
            solid(f, disc(wx, wy, 1.7) | {(math.floor(wx) - 1, math.floor(wy) + 2), (math.floor(wx) - 2, math.floor(wy) + 3)},
                  HI, FIN)
        frames.append(finish(f))
    return frames


def cross() -> list[dict]:
    """위에서 본 보름달물해파리 — 네 잎 생식선이 가운데서 십자를 이루고 입팔 넷이 조준선으로 뻗는다. 갓이 오므렸다 편다"""
    frames = []
    C = (15, 15)
    for k, ph in enumerate(phases()):
        f = {}
        squash = math.sin(ph)
        r = 8.0 + 0.8 * squash
        for a in range(4):   # 입팔
            ang = a * math.pi / 2
            dx, dy = round(math.cos(ang)), round(math.sin(ang))
            for d in range(2, 15):
                w = round(0.6 * math.sin(d * 0.8 + ph)) if d > r else 0
                f[C[0] + dx * d - dy * w, C[1] + dy * d + dx * w] = JELLY_D
        solid(f, disc(C[0] + 0.5, C[1] + 0.5, r), JELLY, JELLY_D)
        for a in range(4):   # 네 잎 생식선: 가운데를 둘러싼 말굽 넷
            ang = a * math.pi / 2 + math.pi / 4
            gx, gy = C[0] + 0.5 + 3.2 * math.cos(ang), C[1] + 0.5 + 3.2 * math.sin(ang)
            for p in disc(gx, gy, 1.6):
                f[p] = JELLY_D
            f[math.floor(gx), math.floor(gy)] = JELLY
        for p in disc(C[0] + 0.5 - 3.5, C[1] + 0.5 - 4.5, 1.0):
            f[p] = JELLY_HI
        f[C] = OUT
        frames.append(finish(f))
    return frames


def ibeam() -> list[dict]:
    """홀쭉한 앞모습 — 지느러미 끝이 I 의 가로획이다. 눈을 가끔 깜빡이고 지느러미가 살짝 흔들린다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        front(f, 5.5, 12.5, 4.5, 2.0, 5.2, 0.5 * math.sin(ph), 0.5 * math.sin(2 * ph), blink=k in (4, 5), serif=3.0)
        frames.append(finish(f))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "help": help_, "person": person, "pin": pin, "we": we, "ns": ns,
         "nesw": nesw, "nwse": nwse, "up": up, "pen": pen, "hand": hand, "cross": cross, "ibeam": ibeam}
HOT = {"arrow": ARROW[0], "busy": ARROW[0], "help": ARROW[0], "person": ARROW[0], "pin": ARROW[0],
       "we": (13, 15), "ns": (15, 15), "nesw": (13, 13), "nwse": (18, 13), "up": (15, 5), "pen": (1, 29),
       "hand": (13, 1), "cross": (15, 15), "ibeam": (5, 12)}


def main() -> None:
    write(SID, {r: (lambda r=r: (SCENE[r](), HOT[r])) for r in SCENE}, sys.argv[1:] or None)


if __name__ == "__main__":
    main()

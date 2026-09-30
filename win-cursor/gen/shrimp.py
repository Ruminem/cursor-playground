# SPDX-License-Identifier: Apache-2.0
"""새우(shrimpanim) 구성표 그림 `art/shrimpanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/shrimp.py [역할...]     그림을 쓴다 (역할을 안 주면 새로 그리는 칸 전부)

첫 벌(2026-09-24)은 화살표만 새우고 나머지는 새우 색 줄무늬를 입힌 화살표라 복제품 같다는 말을 들었다(2026-10-01 사용자).
그래서 칸마다 새우가 하는 짓을 따로 그린다(`SCENE`) — 몸을 도넛처럼 말고 제자리에서 구르기(작업 중) · 몸을 말아
만든 물음표(도움말) · 머리에 새우를 얹은 사람(사람) · 깃발 옆에 앉은 새우(핀) · 앞으로 헤엄치다 꼬리를 튕겨 뒤로
튀기(좌우 — 새우는 도망칠 때 뒤로 간다) · 까딱이는 춤(위아래) · 비스듬히 헤엄(대각선) · 물 밖으로 튀어 오르기(위) ·
제 몸만 한 연필을 끌어안고 쓰기(펜) · 손등을 청소해 주는 청소새우(손) · 딱총새우가 쏜 물거품이 조준점에서
터지기(십자) · 더듬이와 꼬리부채가 I 의 가로획인 곧게 선 새우(I빔).
둘째 벌(같은 날)은 실제 새우처럼 이마뿔·긴 더듬이·다리 열 개에 곧은 몸이라 낚시 미끼 같다는 말을 들었다. 그래서
뭉툭한 코 · 큰 눈 · 볼터치 · 짧은 다리 셋의 통통한 C 자 치비로 바꾸고, I빔 · 도움말 말고는 전부 몸을 크게 만다
(curl 2.6–3.3) — 곧게 편 새우는 어느 칸에서든 튀김으로 읽힌다.
wait · move · no 는 두고 안 그린다.
몸은 `side`(곧은 옆모습) 대신 굽은 등뼈(`spine`)를 따라 그린다 — 새우는 배 쪽으로 말리는 게 전부라서, 등뼈를 휘면
물음표·핀·쳇바퀴가 같은 그리개로 나온다.
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, SIGN, SIGN_D, WAKE, bubble, disc, finish, hand_at, hx, ink, line, phases, raster, solid, splash, under, water, write

SID = "shrimpanim"

# 옛 그림의 색을 그대로 쓴다
OUT, DEEP, PINK, SHELL = hx("4e1219ff"), hx("e4849cff"), hx("ff9eaaff"), hx("ffbcc4ff")
LIGHT, HI, ORANGE, RUST = hx("ffd8dcff"), hx("fff2f2ff"), hx("f06a14ff"), hx("c8440cff")
GOLD, EYE, GLOW = hx("ffa050ff"), hx("140608ff"), hx("6cf6ffff")
ink(OUT, HI, hx("ffd2d4c7"))
SKIN, SHIRT, SHIRT_D = hx("f2c9a0ff"), hx("4a7fb5ff"), hx("2e5a88ff")

# ── 몸: 코끝 t=0 → 꼬리부채 끝 t=1. 반폭(칸)은 몸길이 24칸 기준 ──────────────────────────────────────
# 치비 비율 — 동그란 머리가 몸길이의 40%, 몸통은 짧고 통통하게 말린다. 첫 판은 실제 새우처럼 이마뿔 · 긴 더듬이 ·
# 다리 열 개를 그렸더니 낚시 미끼 같다는 말을 들었다(2026-10-01 사용자)
# 둘째 판은 큰 동그란 머리에 가는 몸을 붙였더니 올챙이·해마가 됐다 — 귀여운 새우는 앞이 뭉툭한 통통한 C 자 초승달 하나다(🦐)
CAP = 0.14                                   # 뭉툭한 코끝 반원의 반지름(몸길이 단위)
BODY = [(0.1, 3.2), (0.22, 4.1), (0.36, 4.2), (0.5, 3.8), (0.64, 3.1), (0.76, 2.4), (0.85, 1.7), (0.88, 1.6),
        (0.93, 2.6), (1.0, 3.3)]
FAN, CARA, BEND = 0.88, 0.3, 0.15            # 꼬리부채가 비롯하는 곳 · 머리가슴 끝 · 말리기 시작하는 곳
SEGS = (0.3, 0.42, 0.53, 0.64, 0.75, 0.85)   # 마디 사이 — 등 쪽 주황 줄이고, 몸을 살짝 잘록하게 해 마디가 볼록하다


def prof(pts, t):
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return pts[-1][1] if t > pts[-1][0] else pts[0][1]


def spine(p0, heading, length, kap, side=1, n=40):
    """p0 칸 가운데서 heading(도, 화면 좌표라 90 이 아래) 쪽으로 length 칸 뻗는 등뼈 → [(x, y, 각)].
    kap(t) 는 칸당 도는 각(라디안)이고 + 가 배 쪽이다. side=1 이면 가는 쪽을 앞으로 볼 때 등이 왼쪽(오른쪽으로 가면 위)"""
    th = math.radians(heading)
    x, y = p0[0] + 0.5, p0[1] + 0.5
    ds = length / n
    pts = [(x, y, th)]
    for i in range(n):
        th += side * kap((i + 0.5) / n) * ds
        x, y = x + math.cos(th) * ds, y + math.sin(th) * ds
        pts.append((x, y, th))
    return pts


class Shrimp:
    """등뼈 하나에 입힌 새우. `at(t, d)` 는 등뼈 t 에서 등 쪽으로 d 칸 떨어진 점, `local(x, y)` 는 그 역"""

    def __init__(self, pts, length, side=1, fat=1.0):
        self.pts, self.side, self.n = pts, side, len(pts) - 1
        self.sz = length / 24 * fat

    def normal(self, th):
        return math.sin(th) * self.side, -math.cos(th) * self.side

    def at(self, t, d=0.0):
        if t >= 1 or t <= 0:   # 끝 너머는 마지막 방향으로 곧게 늘린다(더듬이)
            i, j = (self.n - 1, self.n) if t >= 1 else (0, 1)
            (x0, y0, _), (x1, y1, th) = self.pts[i], self.pts[j]
            ex = (t - (1 if t >= 1 else 0)) * self.n
            bx, by = (x1 if t >= 1 else x0) + (x1 - x0) * ex, (y1 if t >= 1 else y0) + (y1 - y0) * ex
        else:
            f = t * self.n
            i = min(int(f), self.n - 1)
            u = f - i
            (x0, y0, th0), (x1, y1, th1) = self.pts[i], self.pts[i + 1]
            bx, by, th = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, th0 + (th1 - th0) * u
        nx, ny = self.normal(th)
        return bx + nx * d, by + ny * d

    def local(self, qx, qy):
        """점 → (t, d) 가장 가까운 등뼈 마디로. 등뼈 끝 너머면 None"""
        best = None
        for i in range(self.n):
            (ax, ay, th), (bx, by, _) = self.pts[i], self.pts[i + 1]
            ex, ey = bx - ax, by - ay
            ll = ex * ex + ey * ey
            u = ((qx - ax) * ex + (qy - ay) * ey) / ll
            if (i == 0 and u < 0) or (i == self.n - 1 and u > 1):
                continue
            u = min(1.0, max(0.0, u))
            px, py = ax + ex * u, ay + ey * u
            dd = (qx - px) ** 2 + (qy - py) ** 2
            if best is None or dd < best[0]:
                nx, ny = self.normal(math.atan2(ey, ex))
                best = (dd, (i + u) / self.n, (qx - px) * nx + (qy - py) * ny)
        return None if best is None else best[1:]

    def wt(self, t):
        if t < BODY[0][0]:
            body = 24 * math.sqrt(max(0.0, CAP * CAP - (t - CAP) ** 2))
        else:
            body = prof(BODY, t)
            if CARA < t < FAN:
                gap = min(abs(t - b) for b in SEGS) * 24
                body -= max(0.0, 0.8 - gap) * 0.3
        return max(body * self.sz, 0.55)

    wb = wt


def paint(s: Shrimp, t, d, length) -> tuple:
    """몸 칸 한 칸의 색 — 등 쪽이 짙고 가운데 밝은 띠, 배 쪽은 짙은 분홍. 배 마디 사이는 주황 띠, 꼬리부채는 주황"""
    u = d / s.wt(t)
    if t > FAN:
        return GOLD if abs(u) < 0.3 else ORANGE
    if any(abs(t - b) * length < 0.5 for b in SEGS) and u > 0.0:
        return ORANGE
    if t < CARA:   # 머리: 왼쪽 위 빛
        if u > 0.45 and 0.1 < t < 0.26:
            return HI if u < 0.75 and s.sz > 0.6 else LIGHT
        return LIGHT if u > 0.0 else SHELL if u > -0.55 else PINK
    if u > 0.55:
        return PINK
    return LIGHT if u > 0.1 else SHELL if u > -0.45 else DEEP


def shrimp(p0, heading, length, ph=0.0, curl=0.0, side=1, kap=None, fat=1.0, legs=True, ant="back", beat=1.0,
           reach=1.0, flick=0.0, face="smile") -> tuple[dict, set]:
    """새우 한 마리 → ({칸: 색}, 몸 칸). p0 는 코끝 칸, heading 은 머리 → 꼬리 방향(도).
    curl 은 배 마디가 배 쪽으로 말리는 총 각(라디안). ant 는 더듬이: "back"(정수리에서 뒤로 말린 두 가닥) ·
    "split"(양옆으로) · None. beat 는 헤엄다리를 젓는 세기, reach 는 더듬이 길이 배수.
    face 는 "smile" · "blink"(눈 감음) · "x"(기절) · "o"(놀란 입)"""
    if kap is None:
        k = (curl + flick * math.sin(ph)) / ((1 - BEND) * length)
        kap = lambda t: k if t > BEND else 0.0   # noqa: E731
    s = Shrimp(spine(p0, heading, length, kap, side), length, side, fat)
    f = {}
    # 더듬이 · 다리 — 몸 뒤에 먼저 그린다
    if ant == "back":   # 코끝 위에서 솟아 등을 따라 뒤로 넘어가며 물결친다
        for j, (off, rise) in enumerate(((0.8, 2.2), (1.6, 3.6))):
            prev = s.at(0.05, s.wt(0.05) * 0.7)
            for i in range(1, 17):
                u = i / 16
                t = 0.05 + 0.6 * u * reach
                d = s.wt(t) + off + rise * math.sin(math.pi * u) * s.sz + 0.7 * u * math.sin(ph - 3 * u + j)
                cur = s.at(t, d)
                line(f, prev, cur, RUST)
                prev = cur
    elif ant == "split":
        for sgn in (1, -1):
            prev = s.at(0.02, 0.0)
            for i in range(1, 13):
                u = i / 12
                cur = s.at(0.02 - 0.1 * u * reach, sgn * (0.5 + 6.5 * u * reach) + 0.5 * u * math.sin(ph + sgn))
                line(f, prev, cur, RUST)
                prev = cur
    if legs:   # 배 밑 짧은 다리 셋이 물결치듯 번갈아 젓는다
        for i, t in enumerate((0.44, 0.54, 0.64)):
            sw = 0.035 * beat * math.sin(ph * 2 - i * 1.2)
            line(f, s.at(t, -s.wb(t) * 0.5), s.at(t + sw, -s.wb(t) - 0.9 * s.sz - 0.4), ORANGE)
    # 몸
    xs = [p[0] for p in s.pts]
    ys = [p[1] for p in s.pts]
    pad = 3.5 * s.sz + 1
    mask, tv = set(), {}
    for y in range(max(-2, math.floor(min(ys) - pad)), min(34, math.ceil(max(ys) + pad) + 1)):
        for x in range(max(-2, math.floor(min(xs) - pad)), min(34, math.ceil(max(xs) + pad) + 1)):
            hit = 0
            for j in range(4):
                for i in range(4):
                    r = s.local(x + (i + 0.5) / 4, y + (j + 0.5) / 4)
                    if r and -s.wb(r[0]) <= r[1] <= s.wt(r[0]):
                        hit += 1
            if hit >= 8:
                mask.add((x, y))
    mask.add((math.floor(p0[0]), math.floor(p0[1])))
    for p in mask:
        r = s.local(p[0] + 0.5, p[1] + 0.5) or (0.0, 0.0)
        f[p] = OUT if any(q not in mask for q in ((p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1),
                                                   (p[0], p[1] - 1))) else paint(s, r[0], r[1], length)
    # 얼굴 — 머리 앞쪽에 큰 눈(반짝이 하나), 그 밑에 볼터치, 코끝 아래 입
    R = s.wt(0.2)

    def cell(t, d):
        x, y = s.at(t, d)
        return math.floor(x), math.floor(y)

    def put(p, c):
        if p in mask and f[p] != OUT:
            f[p] = c
    e = cell(0.09, R * 0.3)
    big = s.sz > 0.7
    eye = {(e[0] + i, e[1] + j) for i in (0, 1) for j in (0, 1, 2)} if big else {e}   # 세로로 긴 눈
    if face == "blink":
        for p in eye:
            if p[1] == e[1] + (2 if big else 0):
                put(p, OUT)
    elif face == "x":
        for p in ((e[0] - 1, e[1] - 1), (e[0] + 1, e[1] - 1), e, (e[0] - 1, e[1] + 1), (e[0] + 1, e[1] + 1)):
            put(p, OUT)
    else:
        for p in eye:
            put(p, EYE)
        if big:
            put(e, HI)
    put(cell(0.15, -R * 0.3), DEEP)
    if big:
        put(cell(0.19, -R * 0.3), DEEP)
    put(cell(0.03, -R * 0.35), EYE if face == "o" else OUT)
    return f, mask


def centred(c, heading, length, curl, side=1):
    """등뼈 무게중심이 c 에 오도록 코끝 자리를 잡는다 — 말린 새우를 제자리에서 돌리거나 한가운데 놓을 때"""
    k = curl / ((1 - BEND) * length)
    pts = spine((0, 0), heading, length, lambda t: k if t > BEND else 0.0, side)
    mx, my = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    return c[0] - mx, c[1] - my


def clip(f: dict) -> dict:
    """판(테 한 칸을 남긴 1–30) 밖을 자른다"""
    return {p: c for p, c in f.items() if 1 <= p[0] <= 30 and 1 <= p[1] <= 30}


def arrow_shrimp(ph: float, size: float = 1.0) -> dict:
    """화살표 새우: 코끝이 (2, 2), 비스듬히 내려가며 꼬리를 배 쪽으로 만다. 꼬리를 까딱이고 다리를 젓는다"""
    return clip(shrimp((2, 3), 0, 26 * size, ph, curl=3.3, flick=0.15, face="blink" if 7 <= ph / (2 * math.pi) * N < 8 else "smile")[0])


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    return [finish(arrow_shrimp(ph)) for ph in phases()]


def busy() -> list[dict]:
    """몸을 동그랗게 만 새우가 바퀴처럼 굴러 제자리에서 돈다 — 꼬리부채를 입에 문 도넛"""
    frames = []
    L, CURL = 22, 5.2
    for k, ph in enumerate(phases()):
        f = {}
        hd = 360 * k / N
        f.update(shrimp(centred((22.0, 22.0), hd, L, CURL), hd, L, ph * 2, curl=CURL, ant=None, beat=2.0)[0])
        f.update(arrow_shrimp(ph, 0.7))
        frames.append(finish(clip(f)))
    return frames


def help_() -> list[dict]:
    """몸을 말아 만든 물음표 — 머리가 갈고리 끝, 꼬리부채가 아래, 물방울이 점이다"""
    frames = []
    L = 22

    def kap(t):
        if t < 0.08:
            return 0.0
        if t < 0.62:
            return math.radians(235) / (0.54 * L)
        if t < 0.74:
            return -math.radians(55) / (0.12 * L)
        return 0.0
    for k, ph in enumerate(phases()):
        f = {}
        f.update(shrimp((19, 17), -90, L, ph, kap=kap, fat=0.55, ant=None, legs=False)[0])
        bubble(f, 23.0, 29.0 + (0.5 if k in (5, 6) else 0.0), 1.2)
        f.update(arrow_shrimp(ph, 0.7))
        frames.append(finish(clip(f)))
    return frames


def person() -> list[dict]:
    """머리 위에 새우를 모자처럼 얹은 사람 — 새우가 더듬이를 흔든다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        solid(f, raster([(16.2, 30.9), (17.0, 26.0), (19.5, 24.2), (25.5, 24.2), (28.0, 26.0), (28.8, 30.9)]),
              lambda p: SHIRT if p[0] < 22 else SHIRT_D)
        solid(f, disc(22.5, 20.5, 3.6), SKIN)
        f[21, 20] = f[24, 20] = OUT
        f.update(shrimp((26, 13), 180, 14, ph, curl=3.0, side=-1, reach=0.6, beat=1.5,
                        face="blink" if k == 9 else "smile")[0])
        f.update(arrow_shrimp(ph, 0.7))
        frames.append(finish(clip(f)))
    return frames


def pin() -> list[dict]:
    """깃발을 꽂고 그 옆에 선 새우 — 여기다! 깃발이 펄럭이고 새우가 더듬이를 까딱인다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for x in range(12, 30):   # 바닥 그림자
            f[x, 30] = WAKE[3]
        f.update(shrimp((11, 21), 0, 14, ph, curl=3.2, side=1, reach=0.7,
                        face="blink" if k == 9 else "smile")[0])
        line(f, (27.5, 29.5), (27.5, 14.5), OUT)   # 깃대 — 새우 더듬이 위로 깃발이 보이게 나중에 그린다
        wave = [0, 1, 1, 0, -1, -1][k % 6]
        solid(f, raster([(27.8, 14.2), (20.8, 16.5 + wave * 0.6), (27.8, 20.3)]), lambda p: SIGN, SIGN_D)
        f.update(arrow_shrimp(ph, 0.7))
        frames.append(finish(clip(f)))
    return frames


def we() -> list[dict]:
    """앞(오른쪽)으로 헤엄다리를 저어 가다가, 꼬리를 확 말아 튕기며 뒤(왼쪽)로 튄다 — 새우가 도망치는 법"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        if k < 8:          # 앞으로 슬금슬금
            dx, curl, beat = round(k / 4), 2.6, 1.0
        elif k == 8:       # 꼬리를 확 만다
            dx, curl, beat = 2, 4.2, 0.0
        elif k == 9:
            dx, curl, beat = 0, 3.2, 0.0
        else:              # 뒤로 튄다
            dx, curl, beat = -1 - (k - 10), 2.2, 0.0
            for j in range(3):   # 물살
                y = 11 + 3 * j
                line(f, (27.0 - j + (k - 10) * 2, y + 0.5), (30.0, y + 0.5), WAKE[1 + (k - 10)])
        f.update(shrimp(centred((15 + dx, 15), 180, 22, curl, -1), 180, 22, ph, curl=curl, side=-1, beat=beat)[0])
        frames.append(finish(clip(f)))
    return frames


def ns() -> list[dict]:
    """꼬리부채로 서서 몸을 까딱이는 청소새우 춤 — 위아래로 오르내리고 더듬이를 흔든다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        bob = round(1.5 * math.sin(ph))
        f.update(shrimp(centred((15, 15 + bob), 90, 22, 3.2 + 0.2 * math.sin(ph), 1), 90, 22, ph,
                        curl=3.2 + 0.2 * math.sin(ph), side=1)[0])
        frames.append(finish(clip(f)))
    return frames


def nesw() -> list[dict]:
    """오른쪽 위로 비스듬히 헤엄 — 물방울이 꼬리 쪽으로 샌다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for j in range(3):
            t = (k / N + j / 3) % 1
            bubble(f, 9.0 - 2 * t + j, 23.5 + 2 * t - j, 0.6 + 0.5 * t)
        f.update(shrimp(centred((16, 14), 135, 22, 2.7, -1), 135, 22, ph, curl=2.7, flick=0.2, side=-1)[0])
        frames.append(finish(clip(f)))
    return frames


def nwse() -> list[dict]:
    """왼쪽 위로 비스듬히 헤엄 — 이쪽은 배를 더 말아 꼬리부채로 물을 찬다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for j in range(3):
            t = (k / N + j / 3) % 1
            bubble(f, 22.5 + 2 * t - j, 23.5 + 2 * t - j, 0.6 + 0.5 * t)
        f.update(shrimp(centred((14, 14), 45, 22, 3.0, 1), 45, 22, ph, curl=3.0, flick=0.2, side=1)[0])
        frames.append(finish(clip(f)))
    return frames


def up() -> list[dict]:
    """물 밖으로 튀어 오른다 — 물낯 아래는 안 보이고 물이 튄다"""
    frames = []
    for k, ph in enumerate(phases()):
        lift = 0.5 - 0.5 * math.cos(ph)
        cy = 19 - 7 * lift
        body = shrimp(centred((15, cy), 90, 22, 3.3, -1), 90, 22, ph, curl=3.3, side=-1)[0]
        f = under(body, 27)
        water(f, 1, 30, 27, k)
        splash(f, 15.5, 26, k, 4, 8, 3 + 2 * lift)
        frames.append(finish(clip(f)))
    return frames


def pen() -> list[dict]:
    """제 몸만 한 연필을 끌어안고 물결 글씨를 쓴다 — 쓴 자국이 오른쪽으로 늘어난다. 연필심 끝이 핫스폿이다.
    첫 판은 새우 몸 자체를 연필로 뻗었는데, 곧게 편 새우는 튀김이 된다"""
    frames = []
    ax, ay = 1.5, 29.5                           # 연필심 끝
    ux, uy = math.sqrt(0.5), -math.sqrt(0.5)     # 끝 → 지우개 방향
    for k, ph in enumerate(phases()):
        f = {}
        n = 3 + round(k * 25 / (N - 1))
        prev = None
        for x in range(3, n + 1):
            cur = (x + 0.5, 28.5 + 1.2 * math.sin((x - 3) * 0.9))
            if prev:
                line(f, prev, cur, EYE)
            prev = cur
        wig = 0.4 * math.sin(ph * 2)             # 쓰는 손놀림 — 연필 끝은 두고 몸통만 까딱인다
        vx, vy = ux + wig * 0.05, uy + wig * 0.05
        pencil = {}
        for y in range(10, 31):
            for x in range(0, 20):
                qx, qy = x + 0.5 - ax, y + 0.5 - ay
                s = qx * vx + qy * vy                  # 연필 축을 따라
                w = abs(-qx * vy + qy * vx)            # 축에서 떨어진 거리
                half = 1.7 if s > 4 else 0.4 + 1.3 * s / 4
                if 0 <= s <= 17 and w <= half:
                    pencil[x, y] = (EYE if s < 1.6 else SKIN if s < 4 else GOLD if s < 13.5
                                    else LIGHT if s < 14.8 else PINK)
        f.update(pencil)
        f.update(shrimp(centred((19.5, 12.5), 0, 18, 3.3), 0, 18, ph, curl=3.3, flick=0.15, side=1,
                        face="blink" if k == 9 else "smile")[0])
        frames.append(finish(clip(f)))
    return frames


def hand() -> list[dict]:
    """손등을 청소해 주는 청소새우 — 걷는다리로 콕콕 쪼면 손등에 반짝이가 돋는다"""
    frames = []
    X0, Y0 = 2, 1
    for k, ph in enumerate(phases()):
        f = {}
        hand_at(f, X0, Y0, SKIN)
        for j, (sx, sy) in enumerate(((6, 11), (9, 9), (11, 12))):   # 닦인 자리 반짝
            if (k + 4 * j) % N < 4:
                f[sx, sy] = HI
                if (k + 4 * j) % N in (1, 2):
                    for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        f[sx + d[0], sy + d[1]] = LIGHT
        f.update(shrimp(centred((19, 18), 35, 17, 3.0, 1), 35, 17, ph * 2, curl=3.0, side=1, beat=0.6)[0])
        frames.append(finish(clip(f)))
    return frames


def cross() -> list[dict]:
    """딱총새우가 쏜 물거품이 조준점까지 날아가 터진다"""
    frames = []
    C = (15, 15)
    for k, ph in enumerate(phases()):
        f = {}
        for d in range(3, 13):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                f[C[0] + dx * d, C[1] + dy * d] = RUST
        f.update(shrimp(centred((8, 22), 180, 14, 3.0, -1), 180, 14, ph, curl=3.0, side=-1, reach=0.7)[0])
        if k < 5:          # 물거품이 날아간다
            t = k / 4
            bubble(f, 11.5 + 3.5 * t, 18.5 - 3.5 * t, 0.7 + 0.8 * t)
        elif k < 8:        # 펑
            r = 2 + (k - 5)
            for a in range(8):
                ang = a * math.pi / 4
                for rr in (r, r + 1):
                    f[math.floor(C[0] + 0.5 + rr * math.cos(ang)), math.floor(C[1] + 0.5 + rr * math.sin(ang))] = \
                        GOLD if k < 7 else WAKE[1]
        f[C] = OUT
        frames.append(finish(clip(f)))
    return frames


def ibeam() -> list[dict]:
    """곧게 선 새우 — 양옆으로 뻗은 더듬이와 꼬리부채가 I 의 가로획이다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        f.update(shrimp((7, 3), 90, 24, ph, side=1, fat=0.55, ant="split", legs=False, reach=0.55)[0])
        frames.append(finish(clip(f)))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "help": help_, "person": person, "pin": pin, "we": we, "ns": ns,
         "nesw": nesw, "nwse": nwse, "up": up, "pen": pen, "hand": hand, "cross": cross, "ibeam": ibeam}
HOT = {"arrow": (2, 3), "busy": (2, 3), "help": (2, 3), "person": (2, 3), "pin": (2, 3),
       "we": (15, 15), "ns": (16, 15), "nesw": (15, 15), "nwse": (15, 15), "up": (9, 13), "pen": (1, 29),
       "hand": (6, 1), "cross": (15, 15), "ibeam": (7, 15)}


def main() -> None:
    write(SID, {r: (lambda r=r: (SCENE[r](), HOT[r])) for r in SCENE}, sys.argv[1:] or None)


if __name__ == "__main__":
    main()

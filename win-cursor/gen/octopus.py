# SPDX-License-Identifier: Apache-2.0
"""문어(octopusanim) 구성표 그림 `art/octopusanim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/octopus.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

동글동글한 치비 문어 — 큰 둥근 머리(외투막)에 반짝, 큰 눈에 흰 반짝 · 분홍 볼 · 작은 입, 짧고 통통하게 말린 다리에
옅은 빨판 점. 32칸에 다리 여덟을 다 그리면 가늘어져 해파리·오징어가 되므로 굵은 다리를 4–6 개만 보인다.
색은 보라 · 라벤더 · 자홍이다 — 다른 해양 구성표(파랑 · 회색 · 노랑 · 분홍주황)와 갈리게.
칸마다 문어가 하는 짓을 따로 그린다(`SCENE`) — 복제품(문어 색 화살표)이라는 말을 듣지 않게:
  arrow   비스듬히 선 문어가 다리 하나를 왼쪽 위로 뻗어 가리킨다. 그 다리 끝이 핫스팟, 나머지 다리는 물결친다
  wait    가운데 문어 둘레로 먹물 방울이 차례로 퐁퐁 피었다 옅어진다(빙글 도는 대기 표시). 문어 입이 핫스팟
  busy    작은 화살표 문어 + 오른쪽 아래에 도는 먹물 방울 고리
  hand    문어가 다리 하나를 위로 쭉 뻗어 빨판 끝으로 콕 누른다 — 누를 때 둘레에 물결이 퍼진다. 다리 끝이 핫스팟
  help    작은 화살표 문어 + 다리를 말아 만든 물음표(점은 먹물 방울)
  ibeam   빨판이 줄지은 문어 다리 I 기둥. 위아래 가로획은 다리 끝을 양쪽으로 만 것, 빨판 빛이 기둥을 타고 내려간다
  move    위에서 본 문어가 다리 넷을 네 방향으로 뻗었다 오므린다(끝을 말아 화살촉처럼). 머리 가운데가 핫스팟
  no      빨간 금지 고리 안에서 문어가 다리 둘을 입 앞에서 ✕ 로 크게 엇갈려 막는다(위 끝은 눈 옆까지), 나머지 다리는
          ✕ 아래로 짧게 — ✕ 가 몸 아래에 있으면 퍼진 다리와 합쳐 치마로 읽혔다. 가운데가 핫스팟
  pen     노란 연필(분홍 지우개 · 은색 띠 · 나무색 깎은 원뿔 · 짙은 심)을 촉수 하나로 감아 쥐고 쓴다 — 연필과 문어가
          연필심을 축으로 까딱인다. 보라·분홍 막대는 요술봉으로 읽혀서 수달 pen 의 연필 색을 쓴다. 연필심이 핫스팟
  person  작은 화살표 문어 + 머리에 문어를 모자처럼 얹은 사람
  pin     작은 화살표 문어 + 빨간 지도 핀 머리를 끌어안은 문어
  we · nwse · nesw  앞에서 본 문어가 다리 둘을 그 축 양쪽으로 쭉 늘였다 줄인다 — 늘일 때 끝을 펴고 눈을 질끈,
          줄일 때 끝을 동그랗게 만다. 머리 가운데가 핫스팟
  ns      둥근 머리 위아래로 다리 하나씩 곧게 뻗어 끝을 세모 화살촉으로 편 ↕ — 늘였다 줄인다, 나머지 다리 넷은 짧게
          옆으로. 위로 든 다리를 말면 머리 위 뾰족한 끝이 휘어 마법사 모자로 읽혔다. 머리 가운데가 핫스팟
  up      위로 물을 뿜어 솟는다 — 다리를 모았다 폈다 하고 아래로 물방울. 머리 꼭대기가 핫스팟
  cross   앞에서 본 문어 얼굴에서 가는 다리 넷이 조준선으로 뻗는다. 입(가운데)이 핫스팟
몸은 `octo` 하나로 그린다 — 머리 타원 + 다리마다 굵기가 줄어드는 말린 곡선(`Arm`), 얼굴은 머리 기준 자리에 찍는다.
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys
from dataclasses import dataclass

from sea import N, SIGN, SIGN_D, WAKE, bubble, disc, finish, hx, ink, phases, raster, solid, write

SID = "octopusanim"

OUT, EYE = hx("221637ff"), hx("1a1030ff")                            # 테두리(짙은 남보라) · 눈동자
BODY, LIGHT, PALE = hx("9b5fd0ff"), hx("bf8aeaff"), hx("e6cdfaff")   # 보라 몸 · 라벤더 빛 · 반짝
SHADE, DEEP = hx("7a43b0ff"), hx("5e3192ff")                         # 그늘 · 짙은 그늘
SUCK, BLUSH, MAG = hx("f6c6ecff"), hx("ff6fb4ff"), hx("d24aa8ff")    # 빨판 · 볼 · 자홍
HI = hx("ffffffff")
INKC = hx("2a1f45ff")                                                # 먹물
ink(OUT, HI, hx("eadcf6c7"))
SKIN, HAIR, SHIRT, SHIRT_D = hx("f2c9a0ff"), hx("4a3226ff"), hx("4aa0a8ff"), hx("2e7078ff")
# 노란 연필 — 보라·분홍 막대는 요술봉으로 읽혀서 수달(otter.py)의 연필 색을 쓴다
PENCIL, PENCIL_D, WOOD, LEAD = hx("f5c842ff"), hx("c8961cff"), hx("efd2a8ff"), hx("3a3a3aff")
ERASER, FERRULE = hx("f2a0a8ff"), hx("b8b8c0ff")


def fade(c: tuple, a: int) -> tuple:
    return c[:3] + (a,)


# ── 몸 ───────────────────────────────────────────────────────────────────────
@dataclass
class Arm:
    """다리 하나. 머리 기준 좌표(머리 반지름 단위, u 오른쪽 · v 아래)의 밑동에서 ang 방향(도, 90 이 아래)으로
    length(머리 반지름 단위) 뻗고 끝으로 갈수록 curl 도 만큼 돈다(+ 는 화면에서 시계 방향).
    w0 · w1 은 밑동 · 끝 반굵기(칸). front 면 머리 앞에 그리고 테두리를 두른다. wav 는 물결 세기(도), off 는 위상차"""
    u: float
    v: float
    ang: float
    length: float
    curl: float = 0.0
    w0: float = 1.9
    w1: float = 0.7
    front: bool = False
    wav: float = 12.0
    off: float = 0.0
    suck: bool = True
    col: tuple = BODY
    tip: tuple = None       # 끝을 이 월드 칸에 못 박는다(가리키는 다리). 그때 ang 은 밑동→끝 방향에서 휜 각, length 는 안 쓴다
    sep: bool = False       # 머리 뒤에 있어도 머리와 닿는 자리에 선을 긋는다 — 머리 뒤로 든 다리가 머리에서 돋은 뿔로 안 보이게


def side_arms(n: int = 4, spread: float = 1.0, reach: float = 1.0, curl: float = 1.0, wav: float = 12.0,
              back: bool = False, thick: float = 1.0, off: float = 0.0) -> list:
    """머리 아래에서 내려와 끝을 바깥쪽으로 마는 앞 다리 n 개 (앞모습) — 바깥 것일수록 비스듬하고 길다.
    back 이면 그 사이로 짙은 뒷다리 둘이 짧게 비친다(다리가 여덟인 티). 다리를 6 개 넘게 나란히 그리면
    32칸에서 겹쳐 치마 한 장이 된다"""
    arms = []
    if back:
        for sgn in (-1, 1):
            arms.append(Arm(0.35 * sgn, 0.7, 90 - 15 * sgn * spread, 1.15 * reach, -sgn * 160 * curl,
                            w0=1.6 * thick, w1=0.6, wav=wav, off=off + 2.0 + sgn, col=DEEP, suck=False))
    for i in range(n):
        s = (i - (n - 1) / 2) / ((n - 1) / 2) if n > 1 else 0.0   # -1 … 1
        sgn = 1 if s < 0 else -1
        arms.append(Arm(0.7 * s, 0.6 + 0.12 * (1 - abs(s)), 90 - 40 * s * spread,
                        (1.35 + 0.3 * abs(s)) * reach, sgn * (170 + 80 * abs(s)) * curl,
                        w0=2.2 * thick, w1=0.9 * max(thick, 0.75), wav=wav, off=off + 1.3 * i))
    return arms


def arm_path(cx, cy, r, rot, a: Arm, ph, n=28):
    """다리의 등뼈 → [(x, y, t, 각)] 월드 좌표"""
    cs, sn = math.cos(rot), math.sin(rot)
    bx, by = cx + (a.u * cs - a.v * sn) * r, cy + (a.u * sn + a.v * cs) * r
    L = a.length * r
    th0 = math.radians(a.ang) + rot
    if a.tip is not None:   # 못 박은 다리: 밑동에서 끝을 바라보고 그 거리만큼 — ang 은 휘는 정도(도)로 읽는다
        tx, ty = a.tip[0] + 0.5 - bx, a.tip[1] + 0.5 - by
        L, th0 = math.hypot(tx, ty), math.atan2(ty, tx) + math.radians(a.ang)
    pts = []
    x, y, th = bx, by, th0
    ds = L / n
    for i in range(n + 1):
        t = i / n
        pts.append((x, y, t, th))
        tt = (i + 0.5) / n
        th = th0 + math.radians(a.curl) * max(0.0, (tt - 0.35) / 0.65) ** 2 \
            + math.radians(a.wav) * math.sin(ph + a.off - 2.5 * tt) * tt
        x, y = x + math.cos(th) * ds, y + math.sin(th) * ds
    if a.tip is not None:   # 끝을 못 박은 자리로 끌어다 놓는다 — 밑동은 그대로, 끝으로 갈수록 많이
        ex, ey = a.tip[0] + 0.5 - pts[-1][0], a.tip[1] + 0.5 - pts[-1][1]
        pts = [(x + ex * t ** 1.5, y + ey * t ** 1.5, t, th) for x, y, t, th in pts]
    return pts


def arm_cells(pts, a: Arm) -> set:
    cells = set()
    for x, y, t, _ in pts:
        cells |= disc(x, y, a.w0 + (a.w1 - a.w0) * t)
    return cells


def octo(f: dict, cx: float, cy: float, r: float, ph: float, rot: float = 0.0, arms=None, eyes: str = "open",
         mouth: str = "smile", sy: float = 1.0, blush: bool = True, split: bool = False) -> set:
    """문어 한 마리를 f 에 그린다. (cx, cy) 머리 가운데 · r 머리 반지름(칸) · rot 기울기(라디안, 시계 방향).
    eyes 는 "open" · "shut" · "none", mouth 는 "smile" · "o" · "frown" · "none".
    split 이면 뒷다리끼리 닿는 자리에도 선을 긋는다 — 다리를 모아 붙인 자세가 한 덩이로 뭉치지 않게.
    불투명하게 칠한 칸 집합을 돌려준다"""
    arms = side_arms() if arms is None else arms
    cs, sn = math.cos(rot), math.sin(rot)

    def world(u, v):
        return cx + (u * cs - v * sn) * r, cy + (u * sn + v * cs) * r * 1.0

    def local(x, y):
        dx, dy = x - cx, y - cy
        return (dx * cs + dy * sn) / r, (-dx * sn + dy * cs) / r

    head = set()
    for y in range(math.floor(cy - 1.6 * r), math.ceil(cy + 1.6 * r) + 1):
        for x in range(math.floor(cx - 1.6 * r), math.ceil(cx + 1.6 * r) + 1):
            hit = 0
            for j in range(3):
                for i in range(3):
                    u, v = local(x + (i + 0.5) / 3, y + (j + 0.5) / 3)
                    # 위는 둥글고 아래는 살짝 좁아지는 외투막
                    vv = v / sy if v < 0 else v / (0.92 * sy)
                    hit += u * u * (1 + 0.12 * max(0.0, v)) + vv * vv <= 1
            if hit >= 5:
                head.add((x, y))

    parts = []   # (이름, 칸들, 앞인가) 뒤에서 앞으로
    paths = {}
    for i, a in enumerate(arms):
        pts = arm_path(cx, cy, r, rot, a, ph)
        paths[i] = (pts, a)
        if not a.front:
            parts.append((i, arm_cells(pts, a), False))
    parts.append(("head", head, False))
    for i, a in enumerate(arms):
        if a.front:
            parts.append((i, arm_cells(paths[i][0], a), True))
    region = {}
    for name, cells, _ in parts:
        for p in cells:
            if 1 <= p[0] <= 30 and 1 <= p[1] <= 30:   # 판 밖(테 한 칸 자리 포함)은 자른다
                region[p] = name
    front = {name for name, _, fr in parts if fr}
    order = {name: k for k, (name, _, _) in enumerate(parts)}
    mask = set(region)

    def colour(p):
        name = region[p]
        if name == "head":
            u, v = local(p[0] + 0.5, p[1] + 0.5)
            if math.hypot(u + 0.42, v + 0.5) < 0.22 and r >= 4:
                return PALE
            if math.hypot(u + 0.3, v + 0.35) < 0.5:
                return LIGHT
            if u * 0.55 + v * 0.45 > 0.62 or v > 0.82:
                return SHADE
            return BODY
        return arms[name].col

    for p in mask:
        x, y = p
        name = region[p]
        nb = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        line_ = any(q not in mask for q in nb)
        if not line_:
            for q in nb:
                o = region[q]
                if o == name or order[o] < order[name]:
                    continue
                # 앞 다리와 그 뒤만 선을 긋는다. 뒤 다리끼리 · 뒤 다리와 머리는 이어 붙인다 — 다리마다 선을 그으면
                # 32칸에서 테두리가 속을 다 먹어 다리가 검은 기둥이 된다. 다리 사이는 벌어진 틈이 가른다
                if o in front or (o == "head" and arms[name].sep) or (split and "head" not in (o, name)):
                    line_ = True
                    break
        f[p] = OUT if line_ else colour(p)

    # 빨판: 끝 쪽 다리 안쪽(말리는 쪽)에 옅은 점
    for i, (pts, a) in paths.items():
        if not a.suck or r < 3.5:
            continue
        sgn = 1 if a.curl >= 0 else -1
        for t in (0.5, 0.72):
            x, y, _, th = pts[round(t * (len(pts) - 1))]
            w = a.w0 + (a.w1 - a.w0) * t
            q = (math.floor(x - math.sin(th) * sgn * w * 0.55), math.floor(y + math.cos(th) * sgn * w * 0.55))
            if region.get(q) == i and f.get(q) not in (OUT, None):
                f[q] = SUCK

    # 얼굴: 자리는 기울인 그대로, 눈·입 칸 무늬는 가까운 직각으로만 돌린다 — 칸을 하나씩 비스듬히 돌려 찍으면
    # 구멍이 나고 반짝이 눈마다 다른 쪽에 붙는다
    q4 = round(rot / (math.pi / 2)) % 4

    def turn(i, j):
        for _ in range(q4):
            i, j = -j, i
        return i, j

    def stamp(u, v, cells):
        """머리 기준 (u, v) 에 [(i, j, 색)] 칸 무늬를 가운데 맞춰 찍는다"""
        x0, y0 = world(u, v)
        ci = sum(i for i, _, _ in cells) / len(cells)
        cj = sum(j for _, j, _ in cells) / len(cells)
        for i, j, c in cells:
            di, dj = turn(i - ci, j - cj)
            q = (math.floor(x0 + di), math.floor(y0 + dj))
            if region.get(q) == "head" and f.get(q) != OUT:   # 앞 다리에 가린 자리 · 테두리에는 안 찍는다
                f[q] = c
    ew, eh = (2, 3) if r >= 6 else (2, 2) if r >= 4 else (1, 1)
    eye = []
    for j in range(eh):
        for i in range(ew):
            if eyes == "shut":
                if j == eh - 1:
                    eye.append((i, j, EYE))
            else:
                eye.append((i, j, HI if (i, j) == (0, 0) and ew > 1 else EYE))
    for sgn in (-1, 1):
        if eyes != "none":
            stamp(sgn * 0.4, -0.02, eye)
        if blush and r >= 4:
            stamp(sgn * 0.62, 0.36, [(0, 0, BLUSH), (1, 0, BLUSH)])
    my = 0.4 if r >= 5 else 0.34
    if mouth == "smile":
        stamp(0, my, [(0, 0, OUT), (1, 1, OUT), (2, 1, OUT), (3, 0, OUT)] if r >= 5 else [(0, 0, OUT), (1, 0, OUT)])
    elif mouth == "frown":
        stamp(0, my, [(0, 1, OUT), (1, 0, OUT), (2, 0, OUT), (3, 1, OUT)] if r >= 5 else [(0, 0, OUT), (1, 0, OUT)])
    elif mouth == "o":
        stamp(0, my, [(0, 0, OUT), (0, 1, OUT)] if r >= 5 else [(0, 0, OUT)])
    return mask


# ── 소품 ─────────────────────────────────────────────────────────────────────
def puff(f: dict, cx: float, cy: float, r: float, a: int = 255) -> None:
    """먹물 방울 — 짙은 남보라 덩이, 진할 때는 왼쪽 위에 흰 반짝"""
    for p in disc(cx, cy, r):
        f.setdefault(p, fade(INKC, a))
    if a == 255 and r >= 1.5:
        f[math.floor(cx - r * 0.4), math.floor(cy - r * 0.4)] = PALE


def spinner(f: dict, cx: float, cy: float, R: float, k: int, big: float = 2.2, n: int = 8) -> None:
    """먹물 방울 고리 — 한 바퀴를 돌며 맨 앞 것이 크고 뒤로 갈수록 오그라든다. 옅게(반투명) 지우면 어두운 바탕에서
    짙은 먹물이 안 보여서 크기로만 줄이고 불투명하게 둔다 — 불투명해야 `finish` 의 밝은 테가 둘린다"""
    for i in range(n):
        age = int((k * n / N - i) % n)       # 0 이 막 핀 것
        a = 2 * math.pi * i / n - math.pi / 2
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        puff(f, x, y, max(0.6, big * (1 - 0.22 * age)))


# ── 장면 ─────────────────────────────────────────────────────────────────────
ARROW_TIP = (1, 1)


def eyes_at(k: int, at: int) -> str:
    return "shut" if k == at else "open"


def arrow_octo(f: dict, ph: float, s: float = 1.0, blink: bool = False) -> None:
    """왼쪽 위로 다리 하나를 뻗어 가리키는 문어. s 는 크기 배율(작은 것은 0.7 쯤)"""
    r = 6.6 * s
    cx, cy = 1 + 12.0 * s, 1 + 10.5 * s
    arms = side_arms(4, reach=0.95, wav=14, thick=max(s, 0.7))
    point = Arm(-0.75, 0.25, -12, 0, 0, w0=2.4 * s + 0.2, w1=1.0 if s >= 0.9 else 0.8, front=True, wav=6, off=0.5,
                tip=ARROW_TIP)
    octo(f, cx, cy, r, ph, rot=-0.3, arms=arms + [point], eyes="shut" if blink else "open")


def spline(pts: list, n: int = 10) -> list:
    """꼭짓점들을 지나는 매끈한 선(캣멀-롬) → [(x, y, t)]"""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    segs = len(pts) - 1
    for s in range(segs):
        p0, p1, p2, p3 = P[s], P[s + 1], P[s + 2], P[s + 3]
        for i in range(n):
            u = i / n
            out.append(tuple(0.5 * (2 * p1[d] + (-p0[d] + p2[d]) * u + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * u * u
                                    + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * u ** 3) for d in (0, 1))
                       + ((s + u) / segs,))
    out.append(tuple(pts[-1]) + (1.0,))
    return out


def tube(pts: list, w0: float, w1: float) -> set:
    """선을 따라 굵기가 w0 → w1 로 줄어드는 다리 한 가닥의 칸들"""
    cells = set()
    for x, y, t in pts:
        cells |= disc(x, y, w0 + (w1 - w0) * t)
    return cells


def arrow() -> list[dict]:
    """비스듬히 선 문어가 다리 하나를 왼쪽 위로 뻗어 가리킨다 — 나머지 다리는 물결친다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        arrow_octo(f, ph, blink=k == 8)
        frames.append(finish(f))
    return frames


def wait() -> list[dict]:
    """둘레로 먹물 방울이 차례로 퐁퐁 핀다 — 문어는 입을 오므리고 둥실거린다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        spinner(f, 15.5, 15.5, 12.0, k, 2.4)
        octo(f, 15.5, 12.5 + 0.6 * math.sin(ph), 6.0, ph, arms=side_arms(4, reach=0.8, wav=16),
             eyes=eyes_at(k, 9), mouth="o")
        frames.append(finish(f))
    return frames


def busy() -> list[dict]:
    """작은 화살표 문어 + 오른쪽 아래에 도는 먹물 방울 고리"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        spinner(f, 23.0, 23.0, 5.8, k, 2.2)
        arrow_octo(f, ph, 0.68, blink=k == 8)
        frames.append(finish(f))
    return frames


HAND_TIP = (9, 1)


def hand() -> list[dict]:
    """다리 하나를 위로 쭉 뻗어 빨판 끝으로 콕 — 누르는 장에는 끝이 납작해지고 둘레로 물결이 퍼진다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        press = k < 2
        lift = Arm(-0.45, -0.55, 18, 0, 0, w0=2.1, w1=1.3 if press else 1.0, wav=10, tip=HAND_TIP, sep=True)
        octo(f, 19.5, 16.0, 6.3, ph, arms=side_arms(4, reach=0.8, wav=14) + [lift], eyes=eyes_at(k, 7),
             mouth="o" if k < 4 else "smile")
        if k < 5:   # 콕 누른 자리에서 퍼지는 물결 고리
            R = 1.8 + 1.3 * k
            cx, cy = HAND_TIP[0] + 0.5, HAND_TIP[1] + 0.5
            for p in disc(cx, cy, R + 0.5) - disc(cx, cy, R - 0.5):
                if 1 <= p[0] <= 30 and 1 <= p[1] <= 30:
                    f.setdefault(p, fade(LIGHT, 230 - 40 * k))
        frames.append(finish(f))
    return frames


# 다리를 말아 만든 물음표 — 대(밑, 굵음)에서 갈고리 끝(가늘다)으로
QPATH = [(22.5, 20.5), (22.5, 17.5), (24.6, 15.4), (26.2, 12.6), (25.4, 9.7), (22.6, 8.6), (20.0, 9.8), (19.6, 12.2)]


def help_() -> list[dict]:
    """작은 화살표 문어 + 다리를 말아 만든 물음표. 갈고리 끝이 꼼지락거리고 점(먹물 방울)이 통통 튄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        pts = list(QPATH)
        pts[-1] = (pts[-1][0] + 0.7 * math.cos(ph), pts[-1][1] - 0.7 * math.sin(ph))
        line_ = spline(pts, 8)
        q = tube(line_, 1.8, 0.9)
        solid(f, q, BODY)
        for x, y, t in line_[8:-6:7]:   # 갈고리 안쪽(가운데 쪽)에 빨판
            dx, dy = 22.8 - x, 12.8 - y
            d = math.hypot(dx, dy) or 1
            p = (math.floor(x + dx / d * 0.8), math.floor(y + dy / d * 0.8))
            if f.get(p) == BODY:
                f[p] = SUCK
        puff(f, 22.5, 24.5 - abs(math.sin(ph)) * 1.2, 1.6)
        arrow_octo(f, ph, 0.68, blink=k == 8)
        frames.append(finish(f))
    return frames


IBEAM_X = 6


def ibeam() -> list[dict]:
    """I 모양 문어 — 동그란 머리가 위 가로획, 꼭 붙인 다리가 기둥, 바깥으로 만 다리 끝 둘이 아래 가로획.
    빨판 빛이 기둥을 타고 내려가고 발끝이 꼼지락거린다"""
    frames = []
    x = IBEAM_X
    for k, ph in enumerate(phases()):
        f = {}
        lit = 11 + 2 * ((k // 2) % 6)
        stem = {(i, j) for i in range(x - 2, x + 3) for j in range(8, 25)}
        feet = set()
        for sgn in (-1, 1):
            w = 0.4 * math.sin(ph + (sgn > 0) * math.pi)
            pts = [(x + 0.5, 21.5), (x + 0.5 + sgn * 1.6, 24.2), (x + 0.5 + sgn * 3.8, 24.4 - w),
                   (x + 0.5 + sgn * 4.6, 22.6 - w), (x + 0.5 + sgn * 3.4, 21.4 - w)]
            feet |= tube(spline(pts, 6), 1.5, 0.8)
        solid(f, stem | feet, lambda p: SUCK if p[0] == x + 1 and p[1] % 2 == 1 and 10 <= p[1] <= 21 else
              LIGHT if p[0] == x - 1 else BODY)
        for j in (lit,):
            if f.get((x + 1, j)) == SUCK:
                f[x + 1, j] = HI
        octo(f, x + 0.5, 6.0, 4.6, ph, arms=[], eyes=eyes_at(k, 5), mouth="smile")
        frames.append(finish(f))
    return frames


def move() -> list[dict]:
    """위에서 본 문어 — 다리 넷을 네 방향으로 뻗었다 오므린다. 사이사이 짧은 뒷다리 넷(다리 여덟)"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        pulse = 0.5 + 0.5 * math.sin(ph)
        arms = []
        for a in (45, 135, 225, 315):
            ra = math.radians(a)
            arms.append(Arm(0.7 * math.cos(ra), 0.7 * math.sin(ra), a, 0.8, 110, w0=2.0, w1=1.0, wav=0,
                            col=SHADE, suck=False))
        for i, a in enumerate((0, 90, 180, 270)):
            ra = math.radians(a)
            arms.append(Arm(0.75 * math.cos(ra), 0.75 * math.sin(ra), a, 1.45 + 0.3 * pulse, 130, w0=2.8, w1=1.2,
                            wav=8, off=i * math.pi / 2))
        octo(f, 15.5, 15.5, 6.0, ph, arms=arms, eyes=eyes_at(k, 4))
        frames.append(finish(f))
    return frames


def no() -> list[dict]:
    """빨간 금지 고리 안에서 문어가 다리 둘을 ✕ 로 엇갈려 막는다 — 고개를 도리도리 젓는다"""
    frames = []
    hy, r = 12.6, 5.8
    for k, ph in enumerate(phases()):
        f = {}
        ring = {p for p in disc(15.5, 15.5, 14.5)} - disc(15.5, 15.5, 11.2)
        solid(f, ring, SIGN, SIGN_D)
        shake = 0.6 * math.sin(2 * ph)
        hx_ = 15.5 + shake
        # 🙅 — 앞 다리 둘이 입 앞에서 엇갈린다. 위 끝은 눈 옆까지 들어 올려 ✕ 의 위 반쪽이 아래 반쪽만큼
        # 보이게 — ✕ 가 몸 아래에 있으면 아래로 퍼진 다리와 합쳐 치마로 읽혔다. ✕ 가 머리 밑에 붙으면 해골과
        # 뼈다귀(☠)로 읽혀서 머리를 내려 ✕ 위아래로 몸이 보이게 하고, 획 두 끝은 가늘게 줄여 바깥으로 만다.
        # 나머지 다리 셋은 ✕ 아래 틈으로 끝만 짧게 내민다
        arms = [Arm(-0.4, 0.8, 100, 1.05, 190, w0=1.7, w1=0.8, wav=10),
                Arm(0.4, 0.8, 80, 1.05, -190, w0=1.7, w1=0.8, wav=10, off=1),
                Arm(0.0, 0.85, 90, 0.95, 160, w0=1.7, w1=0.8, wav=14, off=2)]
        octo(f, hx_, hy, r, ph, arms=arms, eyes=eyes_at(k, 10), mouth="none")
        for s in (1, -1):   # 왼쪽 아래 → 오른쪽 위 획을 먼저, 그 위에 반대 획
            w = 0.5 * math.sin(ph + (s > 0) * 2.0)
            pts = spline([(15.5 - s * 9.2, 19.8 + w), (15.5 - s * 8.2, 21.0), (hx_, 16.3),
                          (15.5 + s * 8.2, 11.6), (15.5 + s * 9.2, 12.8 - w)], 10)
            cells = set()
            for x, y, t in pts:
                cells |= disc(x, y, 0.7 + 1.0 * math.sin(math.pi * t) ** 0.5)
            solid(f, cells, BODY)
            for t in (0.3, 0.4, 0.6, 0.7):   # 획 아래쪽 가장자리에 빨판
                x, y, _ = pts[round(t * (len(pts) - 1))]
                q = (math.floor(x), math.floor(y + 0.9))
                if f.get(q) == BODY:
                    f[q] = SUCK
        frames.append(finish(f))
    return frames


PEN_TIP, PEN_BACK = (1.5, 29.5), (10.5, 11.0)


def pencil(f: dict, tip, back, r: float = 1.6) -> tuple:
    """노란 연필 — 짙은 심 · 나무색 깎은 원뿔 · 노란 몸통(아래쪽 반은 짙게) · 은색 띠 · 분홍 지우개.
    색은 축을 따라 잰 자리로 고른다(수달 pen 과 같은 꼴). 축 단위 벡터 (ux, uy) 와 길이를 돌려준다"""
    L = math.hypot(back[0] - tip[0], back[1] - tip[1])
    ux, uy = (back[0] - tip[0]) / L, (back[1] - tip[1]) / L
    nx, ny = -uy, ux
    cone = (tip[0] + ux * 3.6, tip[1] + uy * 3.6)
    mask = raster([tip, (cone[0] + nx * r, cone[1] + ny * r), (back[0] + nx * r, back[1] + ny * r),
                   (back[0] - nx * r, back[1] - ny * r), (cone[0] - nx * r, cone[1] - ny * r)])

    def col(p):
        dx, dy = p[0] + 0.5 - tip[0], p[1] + 0.5 - tip[1]
        t, s = dx * ux + dy * uy, dx * nx + dy * ny
        if t < 1.4:
            return LEAD
        if t < 3.8:
            return WOOD
        if t > L - 1.8:
            return ERASER
        if t > L - 3.4:
            return FERRULE
        return PENCIL_D if s > 0.5 else PENCIL
    solid(f, mask, col)
    f[math.floor(tip[0]), math.floor(tip[1])] = LEAD
    return ux, uy, L


def pen() -> list[dict]:
    """노란 연필을 촉수 하나로 감아 쥐고 쓰는 문어 — 연필과 문어가 연필심을 축으로 살짝 까딱인다. 연필심이 핫스팟"""
    frames = []
    TIP = PEN_TIP
    for k, ph in enumerate(phases()):
        f = {}
        d = math.radians(3.0 * math.sin(2 * ph))   # 연필심을 축으로 까딱
        bx, by = PEN_BACK[0] - TIP[0], PEN_BACK[1] - TIP[1]
        back = (TIP[0] + bx * math.cos(d) - by * math.sin(d), TIP[1] + bx * math.sin(d) + by * math.cos(d))
        ux, uy, L = pencil(f, TIP, back, 1.6)
        nx, ny = -uy, ux
        # 연필은 문어 왼쪽을 가파르게 지나간다 — 문어 쪽으로 겨누면 쥐는 촉수가 연필을 따라 길게 덮어 다시 보라 막대가 됐다.
        # 쥐는 촉수는 머리 왼쪽에서 나와 연필을 앞으로 가로질러 감고(그 자리만 연필 위에 띠), 한 바퀴 더 감은 띠가 그 아래에
        g = (TIP[0] + ux * L * 0.5, TIP[1] + uy * L * 0.5)
        grip = Arm(-0.8, 0.55, 20, 0, 0, w0=2.0, w1=1.3, front=True, wav=0,
                   tip=(g[0] - nx * 2.4 - 0.5, g[1] - ny * 2.4 - 0.5))
        arms = [Arm(0.0, 0.8, 95, 0.9, 170, w0=2.0, w1=0.9, wav=12, off=0.5),
                Arm(0.6, 0.65, 60, 1.0, -200, w0=2.0, w1=0.9, wav=12, off=2.0),
                grip]
        octo(f, 19.0, 14.0 + 0.4 * math.sin(ph), 5.6, ph, arms=arms, eyes=eyes_at(k, 6))
        band = set()   # 한 바퀴 더 감은 띠 — 연필을 비스듬히 가로지른다
        ax, ay = g[0] - ux * 2.4, g[1] - uy * 2.4
        band |= tube(spline([(ax - nx * 2.6 + ux * 0.8, ay - ny * 2.6 + uy * 0.8),
                             (ax + nx * 2.4 - ux * 0.8, ay + ny * 2.4 - uy * 0.8)], 8), 1.0, 1.0)
        solid(f, band, BODY)
        frames.append(finish(f))
    return frames


def person() -> list[dict]:
    """작은 화살표 문어 + 머리에 문어를 모자처럼 얹은 사람 — 모자 문어가 다리를 늘어뜨리고 꼼지락거린다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        px, py = 24.5, 23.5   # 얼굴 가운데
        solid(f, raster([(px - 3.0, py + 2.6), (px + 3.0, py + 2.6), (px + 3.6, py + 7.4), (px - 3.6, py + 7.4)]),
              SHIRT, SHIRT_D)
        solid(f, disc(px, py, 3.2), SKIN)
        f[math.floor(px) - 1, math.floor(py) + 1] = OUT
        f[math.floor(px) + 1, math.floor(py) + 1] = OUT
        bob = 0.4 * math.sin(ph)
        hat = side_arms(4, spread=1.6, reach=0.85, wav=14, thick=0.6)
        octo(f, px, py - 3.6 + bob, 3.8, ph, arms=hat, eyes=eyes_at(k, 3))
        arrow_octo(f, ph, 0.68, blink=k == 8)
        frames.append(finish(f))
    return frames


def pin() -> list[dict]:
    """작은 화살표 문어 + 빨간 지도 핀 머리를 끌어안은 문어"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        cx, cy = 23.5, 20.5
        solid(f, raster([(cx - 2.4, cy + 2.2), (cx + 2.4, cy + 2.2), (cx, cy + 9.4)]), SIGN, SIGN_D)
        solid(f, disc(cx, cy, 3.8), lambda p: hx("f08a86ff") if p[0] < cx - 1 and p[1] < cy - 1 else SIGN, SIGN_D)
        bob = 0.5 * math.sin(ph)
        hug = [Arm(-0.7, 0.55, 120, 1.5, -150, w0=1.4, w1=0.8, front=True, wav=10),
               Arm(0.7, 0.55, 60, 1.5, 150, w0=1.4, w1=0.8, front=True, wav=10, off=2)]
        octo(f, cx, 14.5 + bob, 4.0, ph, arms=hug, eyes=eyes_at(k, 3))
        arrow_octo(f, ph, 0.68, blink=k == 8)
        frames.append(finish(f))
    return frames


def ns() -> list[dict]:
    """↕ 문어 — 둥근 머리 위아래로 다리 하나씩 곧게 뻗고 끝을 세모 화살촉으로 편다. 늘일 때 눈을 질끈.
    나머지 다리 넷은 짧게 옆으로 말린다. `stretch(-90)` 으로 그리면 머리 뒤로 든 굵은 다리가 머리 위에서
    뾰족하게 솟아 휘어 마법사 모자로 읽혀서 따로 그린다 — 위 다리는 가늘고 곧게, 머리와 닿는 자리는 머리 테두리가 가른다"""
    frames = []
    cx, cy, r = 15.5, 15.5, 5.0
    for k, ph in enumerate(phases()):
        f = {}
        pull = 0.5 + 0.5 * math.sin(ph)                 # 0 줄임 · 1 늘임
        reach = 11.6 + 1.4 * pull                       # 머리 가운데 → 화살촉 끝
        head_h = 5.6                                    # 화살촉 높이
        stalk = set()
        for s in (-1, 1):
            end, base = cy + s * reach, cy + s * (reach - head_h)
            stalk |= raster([(cx - 1.8, cy), (cx + 1.8, cy), (cx + 1.5, base), (cx - 1.5, base)])
            stalk |= raster([(cx - 5.0, base), (cx + 5.0, base), (cx, end)])

        def col(p):
            x, y = p
            if abs(y + 0.5 - cy) > reach - head_h:      # 화살촉
                return LIGHT if x + 0.5 < cx else BODY
            if x == math.floor(cx) + 1 and y % 2 == 1:   # 줄지은 빨판
                return SUCK
            return LIGHT if x + 0.5 < cx - 0.6 else BODY
        solid(f, stalk, col)
        arms = []
        for s in (-1, 1):
            arms.append(Arm(0.85 * s, 0.25, 90 - 85 * s, 0.75, -s * 150, w0=1.8, w1=0.8, wav=14, off=2 + s))
            arms.append(Arm(0.6 * s, 0.7, 90 - 55 * s, 0.7, -s * 170, w0=1.8, w1=0.8, wav=14, off=1 - s))
        eyes = "shut" if pull > 0.85 else eyes_at(k, 7)
        octo(f, cx, cy, r, ph, arms=arms, eyes=eyes, mouth="smile")
        frames.append(finish(f))
    return frames


def stretch(deg: float) -> list[dict]:
    """앞에서 본 문어가 다리 둘을 deg 축(도, 0 이 오른쪽 · 90 이 아래) 양쪽으로 쭉 늘였다 줄인다 — 늘일 때 끝을 펴고
    눈을 질끈 감으며 힘을 주고, 줄일 때 끝을 동그랗게 만다. 나머지 다리 둘은 아래에서 꼼지락. 머리 가운데가 핫스팟"""
    frames = []
    r = 5.0
    for k, ph in enumerate(phases()):
        f = {}
        pull = 0.5 + 0.5 * math.sin(ph)                 # 0 줄임 · 1 늘임
        arms = []
        for i, a in enumerate((deg, deg + 180)):
            ra = math.radians(a)
            u, v = 0.8 * math.cos(ra), 0.8 * math.sin(ra)
            # 가는 쪽이 대각이면 판 모서리까지 더 멀다
            far = 1.0 + 0.25 * abs(math.sin(2 * ra))
            curl = (-1 if i else 1) * (210 - 150 * pull)
            arms.append(Arm(u, v, a, (1.45 + 0.55 * pull) * far, curl, w0=2.8, w1=1.3, wav=4, off=i * math.pi,
                            sep=True))
        upright = abs(math.cos(math.radians(deg))) < 0.3   # 아래로 뻗은 다리가 있으면 비켜서 옆으로
        for s in (-1, 1):
            base = (0.55 * s, 0.7) if upright else (0.35 * s, 0.85)
            arms.append(Arm(base[0], base[1], 90 - 35 * s, 0.8, -s * 200, w0=1.9, w1=0.9, wav=16, off=2 + s))
        eyes = "shut" if pull > 0.85 else eyes_at(k, 7)
        octo(f, 15.5, 15.5, r, ph, arms=arms, eyes=eyes, mouth="smile")
        frames.append(finish(f))
    return frames


def up() -> list[dict]:
    """위로 물을 뿜어 솟는다 — 다리를 모았다 폈다 하고 아래로 물방울이 떨어져 나간다. 머리 꼭대기가 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        open_ = 0.5 + 0.5 * math.sin(ph)
        for j in range(3):
            t = (k / N + j / 3) % 1
            bubble(f, 12.5 + 3 * j + 0.8 * math.sin(ph + j), 24 + 6 * t, 0.6 + 0.4 * t)
        arms = side_arms(4, spread=0.2 + 0.7 * open_, reach=1.45, curl=0.25 + 0.75 * open_, wav=10)
        octo(f, 15.5, 7.2, 6.2, ph, arms=arms, eyes=eyes_at(k, 6))
        frames.append(finish(f))
    return frames


def cross() -> list[dict]:
    """앞에서 본 문어 얼굴에서 가는 다리 넷이 조준선으로 뻗는다 — 끝이 살랑 말렸다 펴진다. 오므린 입이 가운데"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        c = 40 * math.sin(ph)
        v = (15.5 - 13.5) / 5.5
        hair = [Arm(0, -0.8, 270, 1.45, c, w0=1.2, w1=0.7, wav=3, sep=True, suck=False),
                Arm(0, 0.8, 90, 2.15, -c, w0=1.2, w1=0.7, wav=3, sep=True, suck=False),
                Arm(-0.8, v, 180, 1.8, c, w0=1.2, w1=0.7, wav=3, sep=True, suck=False),
                Arm(0.8, v, 0, 1.8, -c, w0=1.2, w1=0.7, wav=3, sep=True, suck=False)]
        stub = [Arm(-0.5, 0.7, 120, 0.9, 200, w0=1.9, w1=0.9, wav=14),
                Arm(0.5, 0.7, 60, 0.9, -200, w0=1.9, w1=0.9, wav=14, off=2)]
        octo(f, 15.5, 13.5, 5.5, ph, arms=stub + hair, eyes=eyes_at(k, 6), mouth="o")
        frames.append(finish(f))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": lambda: stretch(-45), "no": no, "ns": ns, "nwse": lambda: stretch(-135), "pen": pen,
         "person": person, "pin": pin, "up": up, "wait": wait, "we": lambda: stretch(180)}
HOT = {"arrow": ARROW_TIP, "busy": ARROW_TIP, "cross": (15, 15), "hand": HAND_TIP, "help": ARROW_TIP,
       "ibeam": (IBEAM_X, 15), "move": (15, 15), "nesw": (15, 15), "no": (15, 15), "ns": (15, 15), "nwse": (15, 15),
       "pen": (math.floor(PEN_TIP[0]), math.floor(PEN_TIP[1])), "person": ARROW_TIP, "pin": ARROW_TIP, "up": (15, 1),
       "wait": (15, 15), "we": (15, 15)}


def check(rid: str, frames: list[dict], hot: tuple) -> None:
    """핫스팟이 모든 장에서 불투명한 칸 위에 있고 판(0–31) 안인지"""
    for i, f in enumerate(frames):
        c = f.get(hot)
        if c is None or c[3] != 255:
            raise SystemExit(f"{rid} {i}장: 핫스팟 {hot} 이 불투명한 칸이 아님")
        if any(not (0 <= x <= 31 and 0 <= y <= 31) for x, y in f):
            raise SystemExit(f"{rid} {i}장: 판 밖")


def main() -> None:
    def make(r):
        frames = SCENE[r]()
        check(r, frames, HOT[r])
        return frames, HOT[r]
    write(SID, {r: (lambda r=r: make(r)) for r in SCENE}, sys.argv[1:] or None)


if __name__ == "__main__":
    main()

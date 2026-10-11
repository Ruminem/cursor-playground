# SPDX-License-Identifier: Apache-2.0
"""이펙트 · 애니 다섯 (디지털·기계) — 글리치 떨림 · 매트릭스 · 스캔 · 회전 · 전구 간판.

결마다 원래 픽셀 그림의 움직임 생각은 그대로 두고 매끈한 거리함수 그림으로 옮겼다.
움직임은 frame(0..1)에 주기로만 기대므로 끝 장과 첫 장이 같다. 장 단위로 튀는 것(글리치)은 단계 수를 정수로 잘라
frame 1 이 단계 0 으로 돌아온다.
"""
import bisect
import math

import hd
from . import (register, U, TAU, clamp, smooth, lerp, ramp, hsh, dome, dot3, scale, at,  # noqa: F401
                L3, H3, LX, LY, WHITE)

hypot, exp, sin, cos, atan2, floor, sqrt = math.hypot, math.exp, math.sin, math.cos, math.atan2, math.floor, math.sqrt
C = hd.C
RING = {"wait": (C, C, 7.6), "busy": (18.2, 18.2, 3.1)}      # hd._cell 의 바쁨 고리 자리·반지름


def is_ring(L):
    """바쁨 고리의 흐린 길(alpha 0.32, 그림자 없음) 또는 도는 활(fade)."""
    return "fade" in L or (L.get("alpha", 1.0) < 1 and not L.get("shadow", True))


def hot_of(name):
    return hd._cell(name, 0.0)[1]


def centroid(f, step=0.5):
    sx = sy = n = 0
    for j in range(int(32 / step)):
        y = (j + 0.5) * step
        for i in range(int(32 / step)):
            x = (i + 0.5) * step
            if f(x, y) < 0:
                sx += x
                sy += y
                n += 1
    return (sx / n, sy / n) if n else (C, C)


# ---- 글리치 떨림 ----

class Jitter:
    """흰 화살표 + 먹 테. 빨강·청록 잔상이 몸 뒤에서 단계마다 튀고, 터지는 단계엔 가로 띠가 밀리고 부스러기가 튄다."""
    ko = "글리치 떨림"
    about = "하얀 화살표 둘레에 빨강·청록 잔상이 떨리고, 가끔 한 줄이 옆으로 밀리며 디지털 부스러기가 튀어요."
    LOOP = 1.6
    STEPS = 24                                    # 한 바퀴에 튀는 횟수(67ms 마다)
    BURST = {3: 1, 4: 2, 10: 1, 15: 2, 16: 1, 21: 1}
    shadow = (0.06, 0.05, 0.12, 0.22)
    ink = (0.07, 0.07, 0.09)
    RED = (1.0, 0.16, 0.42)
    CYAN = (0.0, 0.88, 1.0)
    OUT = (0.07, 0.07, 0.09)
    LINE = 0.36

    def __init__(self):
        self.bands = {}
        for k in range(self.STEPS):
            s = self.BURST.get(k, 0)
            bs = []
            for j in range(s):
                y0 = 4.0 + 17.0 * hsh(k, j, 2)
                h = 0.9 + 2.0 * hsh(k, j, 3)
                sh = (0.7 + 1.5 * hsh(k, j, 4)) * (1 if hsh(k, j, 5) > 0.5 else -1)
                bs.append((y0, y0 + h, sh))
            self.bands[k] = bs
        self.hots = {}

    def step(self, frame):
        return int(frame * self.STEPS + 1e-6) % self.STEPS

    def offs(self, k):
        s = self.BURST.get(k, 0)
        a = 0.32 + 0.30 * hsh(k, 1, 31) + 0.50 * s
        b = 0.32 + 0.30 * hsh(k, 2, 31) + 0.45 * s
        return (-a, 0.5 * (hsh(k, 3, 31) - 0.5)), (b, 0.5 * (hsh(k, 4, 31) - 0.5))

    def warp(self, x, y, frame):
        bs = self.bands[self.step(frame)]
        if not bs:
            return x, y
        hy = self.hots.get(self.cell_name)
        if hy is None:
            hy = self.hots[self.cell_name] = hot_of(self.cell_name)[1]
        for y0, y1, sh in bs:
            if y0 <= y < y1 and not (y0 - 2.2 < hy < y1 + 2.2):        # 핫스팟 줄은 안 민다
                return x - sh, y
        return x, y

    def extra(self, name, frame, layers, hot):
        (rx, ry), (cx, cy) = self.offs(self.step(frame))
        out = []
        for L in layers:
            if not L.get("ink") and L.get("alpha", 1.0) > 0:
                for (ox, oy), col in (((rx, ry), self.RED), ((cx, cy), self.CYAN)):
                    G = dict(f=at(L["f"], ox, oy), shadow=False, noglow=True, alpha=0.9 * L.get("alpha", 1.0),
                             paint=lambda x, y, d, nx, ny, fr, c=col: (c, 1.0))
                    if "fade" in L:
                        G["fade"] = L["fade"]
                    out.append(G)
            out.append(L)
        return out

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        k = self.step(frame)
        if warn:
            c = lerp((1.0, 0.36, 0.46), (0.86, 0.12, 0.26), clamp((x + y) / 40))
        else:
            c = lerp((1.0, 1.0, 1.0), (0.84, 0.86, 0.92), clamp((x * 0.4 + y) / 26))
        c = lerp(c, WHITE, 0.35 * clamp(nx * LX + ny * LY) * exp(-depth / 0.9))
        s = self.BURST.get(k, 0)
        row = floor(y / 0.45)                                           # 터질 때 몸 안 줄 몇 개에 색 어긋남
        h = hsh(row, k, 40)
        if h > (0.82 if s else 0.985):
            c = lerp(c, self.CYAN if hsh(row, k, 41) > 0.5 else self.RED, 0.45)
        return lerp(c, self.OUT, smooth(self.LINE + 0.06, self.LINE - 0.06, depth)), 1.0

    def glow(self, x, y, d, warn, frame):
        """둘레에 튀는 디지털 부스러기(짧은 가로 막대)."""
        if d > 2.6:
            return (0, 0, 0), 0.0
        k = self.step(frame)
        s = self.BURST.get(k, 0)
        gy = floor(y / 0.55)
        off = hsh(gy, k, 50) * 1.7
        u = (x + off) / 1.7
        gx = floor(u)
        if hsh(gx, gy, k * 7 + 51) < 0.88 - 0.05 * s:
            return (0, 0, 0), 0.0
        u -= gx
        v = y / 0.55 - gy
        ln = 0.25 + 0.6 * hsh(gx, gy, k * 7 + 52)
        ex = max(0.1 - u, u - 0.1 - ln) * 1.7                            # 막대 밖 거리(칸)
        ey = (abs(v - 0.5) - 0.2) * 0.55
        cov = clamp(0.5 - max(ex, ey) * U)
        if cov <= 0:
            return (0, 0, 0), 0.0
        p = hsh(gx, gy, k * 7 + 53)
        col = self.RED if p < 0.35 else self.CYAN if p < 0.7 else (0.55, 0.56, 0.62)
        return col, cov * 0.75 * smooth(2.6, 0.6, d)


# ---- 매트릭스 ----

GLYPH_SEG = [((0.18, 0.18), (0.82, 0.18)), ((0.18, 0.5), (0.82, 0.5)), ((0.18, 0.82), (0.82, 0.82)),
             ((0.2, 0.18), (0.2, 0.82)), ((0.8, 0.18), (0.8, 0.82)), ((0.5, 0.12), (0.5, 0.88)),
             ((0.82, 0.18), (0.2, 0.82)), ((0.5, 0.5), (0.82, 0.84))]


def seg_dist(px, py, ax, ay, bx, by):
    ex, ey = bx - ax, by - ay
    t = clamp(((px - ax) * ex + (py - ay) * ey) / (ex * ex + ey * ey))
    return hypot(px - ax - ex * t, py - ay - ey * t)


class CodeRain:
    """검은 유리 몸, 초록 네온 테. 열마다 글자 줄기 둘이 위에서 아래로 쏟아지고 머리 글자가 하얗게 빛난다."""
    ko = "매트릭스"
    about = "검은 유리 몸 안으로 초록 글자 줄기가 쏟아지고, 줄기 머리가 하얗게 빛나며 네온 테가 은은히 번져요."
    LOOP = 1.6
    CW, GH = 1.25, 1.45                            # 글자 칸(칸 단위)
    P = 40.0                                       # 줄기 한 바퀴 길이 — 보이는 높이 27 + 꼬리 13
    shadow = (0.0, 0.10, 0.03, 0.26)
    ink = (0.72, 1.0, 0.78)
    GREEN = ((0.12, 0.95, 0.40), (0.86, 1.0, 0.90), (0.32, 1.0, 0.52))       # 글자 · 머리 · 테
    RED = ((1.0, 0.24, 0.26), (1.0, 0.88, 0.84), (1.0, 0.38, 0.36))

    def stream(self, col, y, frame):
        best, head = 0.0, 99.0
        for j in (0, 1):
            n = 1 + (hsh(col, j, 3) > 0.55)                             # 한 바퀴에 1 또는 2번 — 정수라 이음매 없음
            yh = -3.0 + ((hsh(col, j, 4) + n * frame) % 1.0) * self.P
            t = (yh - y) % self.P
            ln = 6.0 + 7.0 * hsh(col, j, 5)
            if t < ln:
                v = (1 - t / ln) ** 1.5
                if v > best:
                    best, head = v, t
        return best, head

    def glyph(self, col, row, x, y, frame):
        fl = int(frame * 6 + hsh(col, row, 12) * 6) % 6                  # 글자가 가끔 바뀐다
        g = int(hsh(col, row, 100 + fl) * 65535)
        ox, oy = col * self.CW, row * self.GH
        dd = 9.0
        for i in {g & 7, (g >> 3) & 7, (g >> 6) & 7}:
            (ax, ay), (bx, by) = GLYPH_SEG[i]
            q = seg_dist(x, y, ox + ax * self.CW, oy + ay * self.GH, ox + bx * self.CW, oy + by * self.GH)
            if q < dd:
                dd = q
        return clamp(0.5 - (dd - 0.12) * U)

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        gc, hc, rim = self.RED if warn else self.GREEN
        col, row = floor(x / self.CW), floor(y / self.GH)
        I, t = self.stream(col, y, frame)
        c = lerp((0.015, 0.05, 0.03), (0.03, 0.10, 0.06), clamp((x + y) / 40))
        cov = self.glyph(col, row, x, y, frame)
        c = lerp(c, gc, clamp(cov * (0.22 + 0.78 * I) + 0.20 * I))
        c = lerp(c, hc, cov * I * exp(-t / 1.1))
        c = lerp(c, WHITE, 0.10 * clamp(nx * LX + ny * LY) * exp(-depth / 0.8))
        c = lerp(c, (0.0, 0.0, 0.0), 0.55 * exp(-((depth - 0.48) / 0.16) ** 2))   # 테 안쪽 어두운 홈 — 테가 또렷하게
        return lerp(c, rim, 0.97 * exp(-(depth / 0.36) ** 2)), 1.0

    def glow(self, x, y, d, warn, frame):
        gc, hc, rim = self.RED if warn else self.GREEN
        I, _ = self.stream(floor(x / self.CW), y, frame)
        return rim, (0.48 + 0.30 * I) * exp(-d / 0.85)


# ---- 스캔 ----

class Scan:
    """남색 유리 몸, 청록 테. 밝은 빛줄기가 위에서 아래로 훑고, 지나간 자리가 옅게 남았다 사라진다."""
    ko = "스캔"
    about = "남색 유리 몸 위로 밝은 청록 스캔 빛줄기가 위에서 아래로 훑고 지나가며 테 밖까지 레이저처럼 번져요."
    LOOP = 32 * 2 / 60
    P, Y0, TR = 36.0, 10.0, 8.0                    # 빔 한 바퀴 길이(보이는 높이 27 + 꼬리 8 + 여유) · 시작 · 꼬리
    shadow = (0.02, 0.08, 0.16, 0.26)
    ink = (0.88, 0.98, 1.0)

    def dy(self, y, frame):
        yb = self.Y0 + frame * self.P
        return ((y - yb + self.P / 2) % self.P) - self.P / 2              # 주기 거리 — frame 0 과 1 이 같다

    def beam(self, y, frame):
        dy = self.dy(y, frame)
        trail = exp(dy / 3.0) * smooth(-self.TR, -self.TR * 0.5, dy) if dy < 0 else 0.0
        return exp(-(dy / 0.28) ** 2), exp(-(dy / 1.0) ** 2), trail

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        if warn:
            c = lerp((0.36, 0.07, 0.12), (0.22, 0.03, 0.08), clamp((y - 2) / 22))
            tint, rim0, core = (1.0, 0.38, 0.42), (0.86, 0.24, 0.30), (1.0, 0.90, 0.90)
        else:
            c = lerp((0.07, 0.18, 0.29), (0.035, 0.09, 0.18), clamp((y - 2) / 22))
            tint, rim0, core = (0.22, 0.80, 1.0), (0.24, 0.80, 0.96), (0.88, 1.0, 1.0)
        c = scale(c, 0.9 + 0.1 * (0.5 + 0.5 * cos(TAU * y / 0.5)))       # 고운 주사선
        k, halo, trail = self.beam(y, frame)
        c = lerp(c, tint, 0.65 * trail + 0.4 * halo)
        c = lerp(c, core, k)
        c = lerp(c, WHITE, 0.12 * clamp(nx * LX + ny * LY) * exp(-depth / 0.7))
        rim = lerp(rim0, core, clamp(max(halo, 0.55 * trail)))
        return lerp(c, rim, 0.97 * exp(-(depth / 0.4) ** 2)), 1.0

    def glow(self, x, y, d, warn, frame):
        k, halo, trail = self.beam(y, frame)
        tint, core = ((1.0, 0.36, 0.40), (1.0, 0.86, 0.86)) if warn else ((0.20, 0.78, 1.0), (0.80, 1.0, 1.0))
        line = 0.95 * exp(-(self.dy(y, frame) / 0.14) ** 2) * smooth(1.9, 0.2, d)   # 테 밖으로 삐져나온 빛줄기
        soft = (0.40 + 0.40 * halo + 0.25 * trail) * exp(-d / 0.8)
        a = line + soft * (1 - line)
        return lerp(tint, core, line / a if a > 0 else 0.0), a


# ---- 회전 ----

class Spinner:
    """사탕 광택 플라스틱 바람개비. 레이어마다 무게중심을 축으로 네 날이 돌고, 흰 광택과 핀은 제자리."""
    ko = "회전"
    about = "빨강·초록·노랑·파랑 네 날 바람개비가 매끈한 사탕 광택 아래에서 빙글빙글 돌아요."
    LOOP = 24 * 3 / 60
    shadow = (0.10, 0.08, 0.22, 0.26)
    shadow_off, shadow_blur = (0.45, 0.9), 2.0
    ink = (0.09, 0.09, 0.13)
    glow = None
    OUT = (0.09, 0.09, 0.13)
    PAL = [(1.0, 0.83, 0.22), (0.20, 0.56, 0.92), (0.94, 0.26, 0.38), (0.24, 0.78, 0.46)]   # 시계 방향 노랑·파랑·빨강·초록
    WARN = [(1.0, 0.42, 0.30), (0.80, 0.10, 0.20), (1.0, 0.62, 0.50), (0.92, 0.22, 0.28)]
    SWIRL = 0.10                                   # 날이 바깥으로 갈수록 휘는 정도(라디안/칸)
    HUB = 0.62

    def __init__(self):
        self.centers = {}

    def extra(self, name, frame, layers, hot):
        out = []
        for i, L in enumerate(layers):
            if L.get("ink") or L.get("alpha", 1.0) <= 0:
                out.append(L)
                continue
            if is_ring(L):
                cx, cy, _ = RING[name]
            else:
                key = (name, i)
                if key not in self.centers:
                    self.centers[key] = centroid(L["f"])
                cx, cy = self.centers[key]
            warn, hub = L.get("warn", False), not is_ring(L)
            out.append(dict(L, paint=lambda x, y, d, nx, ny, fr, cx=cx, cy=cy, w=warn, h=hub:
                            self.paint(x, y, d, nx, ny, fr, cx, cy, w, h)))
        return out

    def paint(self, x, y, d, nx, ny, frame, cx, cy, warn, hub):
        depth = -d
        pal = self.WARN if warn else self.PAL
        r = hypot(x - cx, y - cy)
        a = atan2(y - cy, x - cx) - TAU * frame + self.SWIRL * r
        s = (a / (TAU / 4)) % 4
        i = int(s) % 4
        f = s - int(s)
        c = scale(pal[i], 0.86 + 0.18 * f)                                 # 날마다 접힌 종이처럼 한쪽이 밝다
        q = TAU / 4 * r                                                    # 날 경계를 1px 남짓 섞는다
        h = 0.07
        if f * q < h:
            c = lerp(c, scale(pal[(i - 1) % 4], 1.04), 0.5 * (1 - f * q / h))
        elif (1 - f) * q < h:
            c = lerp(c, scale(pal[(i + 1) % 4], 0.86), 0.5 * (1 - (1 - f) * q / h))
        n = dome(nx, ny, depth, 1.3)
        c = scale(c, 0.80 + 0.32 * dot3(n, L3))
        c = lerp(c, WHITE, 0.42 * clamp(nx * LX + ny * LY) * exp(-depth / 0.55))  # 왼쪽 위 어깨 광택(안 돈다)
        c = lerp(c, WHITE, 0.85 * max(0.0, dot3(n, H3)) ** 14)
        if hub and r < self.HUB + 0.15:                                    # 바람개비 핀
            pin = lerp((0.98, 0.98, 1.0), (0.70, 0.72, 0.80), clamp((x - cx + y - cy) / (2 * self.HUB) + 0.5))
            pin = lerp(pin, self.OUT, smooth(self.HUB - 0.16, self.HUB, r))
            c = lerp(c, pin, clamp((self.HUB + 0.1 - r) * U))
        return lerp(c, self.OUT, smooth(0.40, 0.27, depth)), 1.0

    def body(self, x, y, d, nx, ny, warn, frame):                       # extra 가 다 paint 로 바꾸지만 틀이 부를 때를 위해
        return self.paint(x, y, d, nx, ny, frame, C, C, warn, False)


# ---- 전구 간판 ----

def contours(f, level, step=0.25):
    """f = level 등고선(marching squares) → 닫힌 고리 목록. 고리는 화면 기준 시계 방향."""
    coarse = [(x, y) for y in range(-1, 34) for x in range(-1, 34) if f(x, y) < level + 1.2]
    if not coarse:
        return []
    x0, y0 = min(p[0] for p in coarse) - 1.5, min(p[1] for p in coarse) - 1.5
    nx = int((max(p[0] for p in coarse) + 1.5 - x0) / step) + 2
    ny = int((max(p[1] for p in coarse) + 1.5 - y0) / step) + 2
    V = [[f(x0 + i * step, y0 + j * step) - level for i in range(nx)] for j in range(ny)]
    for row in V:
        for i, v in enumerate(row):
            if v == 0:
                row[i] = 1e-9

    def pt(key):
        kind, i, j = key
        if kind == "h":
            a, b = V[j][i], V[j][i + 1]
            return x0 + (i + a / (a - b)) * step, y0 + j * step
        a, b = V[j][i], V[j + 1][i]
        return x0 + i * step, y0 + (j + a / (a - b)) * step

    segs = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            a, b, c, d = V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]
            m = (a < 0) | (b < 0) << 1 | (c < 0) << 2 | (d < 0) << 3
            if m in (0, 15):
                continue
            T, R, B, L = ("h", i, j), ("v", i + 1, j), ("h", i, j + 1), ("v", i, j)
            if m in (5, 10):
                inside = (a + b + c + d) < 0
                if (m == 5) == inside:
                    segs += [(T, R), (B, L)]
                else:
                    segs += [(T, L), (R, B)]
                continue
            e = [k for k, s in ((T, (a < 0) != (b < 0)), (R, (b < 0) != (c < 0)),
                                (B, (c < 0) != (d < 0)), (L, (a < 0) != (d < 0))) if s]
            segs.append((e[0], e[1]))
    adj = {}
    for si, (k1, k2) in enumerate(segs):
        adj.setdefault(k1, []).append(si)
        adj.setdefault(k2, []).append(si)
    used = [False] * len(segs)
    loops = []
    for s0 in range(len(segs)):
        if used[s0]:
            continue
        used[s0] = True
        start, cur = segs[s0]
        loop, prev = [pt(start)], s0
        while cur != start:
            loop.append(pt(cur))
            nxt = [s for s in adj[cur] if s != prev and not used[s]]
            if not nxt:
                break
            s = nxt[0]
            used[s] = True
            k1, k2 = segs[s]
            cur = k2 if k1 == cur else k1
            prev = s
        area = sum(loop[k - 1][0] * loop[k][1] - loop[k][0] * loop[k - 1][1] for k in range(len(loop)))
        if area < 0:
            loop.reverse()
        if len(loop) > 4:
            loops.append(loop)
    return loops


def beads(loop, spacing, start=None):
    """고리를 따라 같은 간격 점. start 가 있으면 그 점에서 반 칸 비켜 시작(끝을 전구로 덮지 않게)."""
    n = len(loop)
    cum = [0.0]
    for k in range(n):
        (ax, ay), (bx, by) = loop[k], loop[(k + 1) % n]
        cum.append(cum[-1] + hypot(bx - ax, by - ay))
    total = cum[-1]
    cnt = max(3, round(total / spacing))
    sp = total / cnt
    s0 = 0.0
    if start is not None:
        k0 = min(range(n), key=lambda k: hypot(loop[k][0] - start[0], loop[k][1] - start[1]))
        s0 = cum[k0] + sp / 2
    out = []
    for i in range(cnt):
        s = (s0 + i * sp) % total
        k = min(bisect.bisect_right(cum, s) - 1, n - 1)
        t = (s - cum[k]) / ((cum[k + 1] - cum[k]) or 1)
        (ax, ay), (bx, by) = loop[k], loop[(k + 1) % n]
        out.append((ax + (bx - ax) * t, ay + (by - ay) * t, i))
    return out


class Marquee:
    """자줏빛 간판 몸에 얇은 금 테, 테를 따라 둥근 전구가 줄지어 3상으로 차례차례 켜진다. 불빛은 노랑→주황→분홍을 돈다."""
    ko = "전구 간판"
    about = "자줏빛 간판 테두리를 따라 둥근 전구가 줄지어 있고, 불빛이 한 칸씩 차례로 켜지며 흘러가요."
    LOOP = 1.6
    soft = 0.35
    shadow = (0.16, 0.03, 0.12, 0.28)
    ink = (1.0, 0.86, 0.45)
    glow = None
    SP, BR, LV = 1.55, 0.48, -0.22                 # 전구 간격 · 반지름 · 중심이 테 안쪽으로 든 거리
    K = 5                                          # 한 바퀴에 3상 추격이 도는 횟수 (15걸음, 걸음당 0.11초)
    PAL = [(1.0, 0.86, 0.30), (1.0, 0.58, 0.22), (1.0, 0.42, 0.62)]
    WARN = [(1.0, 0.30, 0.22), (1.0, 0.18, 0.30)]
    B = 2.0                                        # 전구 찾기 칸

    def __init__(self):
        self.cache = {}

    def chase(self, i, frame):
        p = (3 * self.K * frame - i) % 3
        return smooth(0.0, 0.22, p) * (1 - smooth(0.9, 1.7, p))         # 확 켜지고 천천히 식는다

    def extra(self, name, frame, layers, hot):
        out = []
        for idx, L in enumerate(layers):
            if L.get("ink") or L.get("alpha", 1.0) <= 0:
                out.append(L)
                continue
            warn = L.get("warn", False)
            if "fade" in L:                                                 # 도는 활은 고리 위 전구 밝기로 옮긴다
                continue
            if is_ring(L):                                                  # 흐린 길 → 간판 몸 고리
                cx, cy, r = RING[name]
                n = max(6, round(TAU * r / self.SP))
                a0 = TAU * frame - math.pi / 2                              # hd.spinner 와 같은 활
                span = TAU * 0.62
                back = (TAU - span) / 2
                bs = []
                for i in range(n):
                    th = TAU * i / n
                    rel = ((th - a0 + back) % TAU) - back
                    t = rel / span
                    b = (0.12 + 0.88 * t) * min(1.0, t / 0.15) if 0 <= t <= 1 else 0.0
                    bs.append((cx + r * cos(th), cy + r * sin(th), b, i))
                out.append(dict(L, alpha=1.0, shadow=True))
                out.append(self.bulbs(bs, frame, warn, 0.42 if name == "busy" else self.BR))
                continue
            key = (name, idx)
            if key not in self.cache:
                loops = contours(L["f"], self.LV)
                hx, hy = hot
                near = min(range(len(loops)), default=None,
                           key=lambda k: min(hypot(p[0] - hx, p[1] - hy) for p in loops[k]))
                self.cache[key] = [beads(lp, self.SP, (hx, hy) if k == near else None) for k, lp in enumerate(loops)]
            bs = [(x, y, self.chase(i, frame), i) for lp in self.cache[key] for (x, y, i) in lp]
            out.append(L)
            out.append(self.bulbs(bs, frame, warn, self.BR))
        return out

    def bulbs(self, bs, frame, warn, R):
        B = self.B
        bins = {}
        for bd in bs:
            bins.setdefault((floor(bd[0] / B), floor(bd[1] / B)), []).append(bd)
        pal = self.WARN if warn else self.PAL

        def near(x, y):
            gx, gy = floor(x / B), floor(y / B)
            best, bb = 9.0, None
            for oy in (-1, 0, 1):
                for ox in (-1, 0, 1):
                    for bd in bins.get((gx + ox, gy + oy), ()):
                        q = (x - bd[0]) ** 2 + (y - bd[1]) ** 2
                        if q < best:
                            best, bb = q, bd
            return sqrt(best), bb

        def f(x, y):
            return near(x, y)[0] - R

        def hue(bd):
            return ramp(pal, frame + bd[3] * 0.012)

        def paint(x, y, d, nx, ny, fr):
            q, bd = near(x, y)
            b = bd[2]
            h = hue(bd)
            depth = -d
            n = dome(nx, ny, depth, R)
            core = clamp(1 - q / (R * 0.9))
            lit = lerp(h, (1.0, 0.98, 0.88), 0.85 * core ** 1.5)
            off = scale(lerp((0.42, 0.24, 0.14), h, 0.25), 0.55 + 0.45 * dot3(n, L3))
            c = lerp(off, lit, b)
            c = lerp(c, WHITE, 0.75 * max(0.0, dot3(n, H3)) ** 16)
            c = lerp(c, (0.30, 0.10, 0.08), (1 - b) * 0.8 * exp(-(depth / 0.07) ** 2))   # 꺼진 알은 테를 세워 흰 바탕에서도
            return c, 1.0

        def glow(x, y, d, fr):
            q, bd = near(x, y)
            if bd is None or bd[2] <= 0.01:
                return (0, 0, 0), 0.0
            return hue(bd), 0.85 * bd[2] * exp(-d / 0.42) * smooth(2.0, 1.2, d)

        return dict(f=f, paint=paint, glow=glow, shadow=True)

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        if warn:
            c = lerp((0.42, 0.06, 0.10), (0.26, 0.03, 0.07), clamp(y / 24))
            gold = (0.95, 0.55, 0.35)
        else:
            c = lerp((0.44, 0.12, 0.34), (0.26, 0.06, 0.22), clamp(y / 24))
            gold = (0.86, 0.62, 0.26)
        c = lerp(c, WHITE, 0.10 * clamp(1 - abs((x - y * 0.5) - 2.0) / 3.0))    # 비스듬한 옅은 윤
        n = dome(nx, ny, depth, 0.5)
        g = scale(gold, 0.7 + 0.45 * dot3(n, L3))
        return lerp(c, g, smooth(0.50, 0.34, depth)), 1.0


for _sid, _cls in (("jitter", Jitter), ("coderain", CodeRain), ("scan", Scan), ("spinner", Spinner),
                   ("marquee", Marquee)):
    _o = _cls()
    register(_sid, _o)

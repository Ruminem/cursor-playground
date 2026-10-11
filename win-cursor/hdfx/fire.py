# SPDX-License-Identifier: Apache-2.0
"""움직이는 결 다섯 — 일렁이는 불꽃 · 용암 · 전기 · 폭죽 · 반짝이는 별 (이펙트 · 애니).

움직임은 frame(0..1) 에 주기로만 기댄다. 위아래로 흐르는 결은 y 격자를 py 칸마다 감는 잡음(pnoise)을
한 바퀴에 py 칸 밀어 끝 장과 첫 장이 같다. 불티·불꽃 알갱이도 같은 감긴 격자에 둬 이음매가 없다.
"""
from . import *  # noqa: F401,F403
from . import register, hd, TAU, WHITE, clamp, smooth, lerp, dome, dot3, scale, hsh, noise, ramp_to, \
    L3, H3, LX, LY, circle, union, smin, capsule  # noqa: F401
import math

hypot, exp, sin, cos, floor = math.hypot, math.exp, math.sin, math.cos, math.floor
ARROWISH = ("arrow", "help", "busy", "pin", "person")       # 첫 레이어가 화살표인 칸


def pnoise(x, y, s, py):
    """y 격자가 py 칸마다 감기는 값 잡음 0..1 — y 에 frame*py 를 더하면 한 바퀴에 꼭 한 주기 흐른다."""
    ix, iy = floor(x), floor(y)
    fx, fy = x - ix, y - iy
    ux, uy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    j0, j1 = iy % py, (iy + 1) % py
    a, b = hsh(ix, j0, s), hsh(ix + 1, j0, s)
    c, d = hsh(ix, j1, s), hsh(ix + 1, j1, s)
    return a + (b - a) * ux + (c - a) * uy + (a - b - c + d) * ux * uy


def flow(x, y, frame, a, D, s):
    """아래로 D칸씩 흐르는 잡음 0..1 (흐름 지도 두 겹 엇갈려 섞기). 감긴 잡음과 달리 느리게 흘러도 결이 되풀이되지
    않는다. 두 겹은 반 바퀴씩 어긋나 한 겹이 처음 자리로 돌아갈 때 그 겹 몫이 0 이라 이음매가 없다."""
    acc = ww = 0.0
    for k, ph in ((0, 0.0), (1, 0.5)):
        t = (frame + ph) % 1.0
        w = 1 - abs(2 * t - 1)
        if w <= 0:
            continue
        n = noise(x * a + 17.3 * k, (y - t * D) * a + 9.1 * k, s)
        acc += w * (n - 0.5)
        ww += w * w
    return 0.5 + acc / math.sqrt(ww) if ww > 0 else 0.5


def mix(parts):
    """[(색, 알파)] 를 더해 하나로 — 색은 알파 가중 평균, 알파는 1 에서 자른다."""
    a = sum(p[1] for p in parts)
    if a <= 1e-6:
        return (0.0, 0.0, 0.0), 0.0
    r = sum(p[0][0] * p[1] for p in parts) / a
    g = sum(p[0][1] * p[1] for p in parts) / a
    b = sum(p[0][2] * p[1] for p in parts) / a
    return (r, g, b), min(a, 1.0)


def box_fade(x, y):
    """32칸 판 가장자리 한 칸 안에서 바깥 것(번짐·알갱이)을 0 으로."""
    return smooth(0.0, 1.0, min(x, y, 32 - x, 32 - y))


# ---- 일렁이는 불꽃 ----

class Flicker:
    """불꽃 몸. 위로 흐르는 잡음이 몸 속 열을 일렁이게 하고, 위를 보는 테에서 같은 잡음이 혀처럼 솟으며 불티가 오른다."""
    ko = "일렁이는 불꽃"
    about = "주황·노랑 불꽃이 몸 속에서 위로 일렁이고, 윗변에서 불꽃 혀가 날름거리며 작은 불티가 피어올라요."
    LOOP = 1.6
    glow_n = True
    tip_body = True
    shadow = (0.32, 0.07, 0.02, 0.20)
    ink = (0.40, 0.07, 0.03)
    FIRE = [(0.42, 0.05, 0.02), (0.78, 0.13, 0.03), (0.97, 0.34, 0.05), (1.0, 0.58, 0.10),
            (1.0, 0.80, 0.26), (1.0, 0.95, 0.66)]
    WARN = [(0.36, 0.02, 0.06), (0.70, 0.04, 0.10), (0.94, 0.12, 0.14), (1.0, 0.30, 0.24),
            (1.0, 0.52, 0.42), (1.0, 0.82, 0.74)]
    hot = (0.0, 0.0)

    def extra(self, name, frame, layers, hot):
        self.hot = hot
        return layers

    def heat(self, x, y, frame):
        """위로 흐르는 불꽃 결 0..1. 세로로 늘인 잡음을 낮은 잡음으로 옆으로 흔들어 혀 모양이 된다."""
        w = pnoise(x * 0.35, y * 0.25 + frame * 3, 9, 3)                 # 한 바퀴에 12칸
        n1 = pnoise(x * 0.85 + 0.9 * w, y * 0.32 + frame * 5, 7, 5)      # 15.6칸 오름
        n2 = pnoise(x * 1.7 + 0.6 * w, y * 0.70 + frame * 10, 8, 10)     # 14.3칸 — 결이 둘이라 되풀이가 안 보임
        return n1 * 0.68 + n2 * 0.32

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        n = self.heat(x, y, frame)
        up = clamp(-ny)
        h = 0.22 + 0.66 * smooth(0.0, 2.4, depth) + 0.34 * (n - 0.5)
        h -= 0.22 * up * exp(-depth / 0.9)                         # 위를 보는 테는 붉게 식는다
        c = ramp_to(self.WARN if warn else self.FIRE, h)
        rim = (0.30, 0.03, 0.05) if warn else (0.36, 0.06, 0.02)
        return lerp(c, rim, (0.85 - 0.50 * up) * exp(-(depth / 0.2) ** 2)), 1.0

    def glow(self, x, y, d, warn, frame, nx=0.0, ny=0.0):
        pal = self.WARN if warn else self.FIRE
        keep = smooth(1.4, 4.2, hypot(x - self.hot[0], y - self.hot[1])) * box_fade(x, y)
        up = smooth(0.05, 0.55, -ny)
        parts = [(pal[3], 0.30 * exp(-d / 0.5))]                    # 몸 둘레 열기
        if up > 0 and keep > 0:
            n = self.heat(x, y, frame)
            thr = 0.30 + 0.62 * d / 2.8                               # 몸에서 멀수록 문턱이 높아 혀 끝이 갈라진다
            g = n - thr
            if g > -0.05:
                tongue = smooth(-0.035, 0.035, g)
                core = smooth(0.0, 0.22, g)
                col = ramp_to(pal, 0.38 + 0.45 * core - 0.12 * d / 2.8)
                parts.append((col, 0.95 * tongue * up * keep))
            # 불티 — 위로 감기는 격자 칸마다 하나
            S, P = 1.5, 7
            Y = y + frame * P * S
            gx, gy = floor(x / S), floor(Y / S)
            hh = hsh(gx, gy % P, 21)
            if hh > 0.74:
                ex = (gx + 0.3 + 0.4 * hsh(gx, gy % P, 22)) * S + 0.25 * sin(TAU * (frame * 2 + hh * 5 + Y / (P * S)))
                ey = (gy + 0.3 + 0.4 * hsh(gx, gy % P, 23)) * S
                r2 = (x - ex) ** 2 + (Y - ey) ** 2
                if r2 < 0.5:
                    life = smooth(0.6, 1.2, d) * smooth(3.4, 1.8, d)
                    tw = 0.65 + 0.35 * sin(TAU * (frame * 3 + hh * 7))
                    e = exp(-r2 / 0.05) * life * tw * up * keep
                    parts.append((pal[5], e))
                    parts.append((pal[3], 0.5 * exp(-r2 / 0.18) * life * up * keep))
        return mix(parts)


# ---- 용암 ----

class Lava:
    """녹은 용암 몸에 검붉은 굳은 껍질 조각이 천천히 흘러내리고, 꼬리 끝에서 방울이 맺혀 떨어진다."""
    ko = "용암"
    about = "끈적하게 빛나는 용암 위로 검붉은 껍질이 천천히 흘러내리고, 꼬리 끝에 맺힌 방울이 똑 떨어져요."
    LOOP = 1.6
    shadow = (0.26, 0.04, 0.02, 0.26)
    ink = (0.22, 0.03, 0.02)
    tip_body = True
    LAVA = [(0.20, 0.03, 0.02), (0.55, 0.07, 0.02), (0.90, 0.22, 0.04), (1.0, 0.48, 0.08),
            (1.0, 0.76, 0.26), (1.0, 0.94, 0.66)]
    WARN = [(0.20, 0.02, 0.04), (0.50, 0.03, 0.06), (0.86, 0.08, 0.10), (1.0, 0.22, 0.16),
            (1.0, 0.46, 0.38), (1.0, 0.78, 0.70)]
    TAIL = (10.7, 22.0)                                      # 화살표 꼬리 아래 끝, 방울이 맺히는 자리

    def drop(self, frame):
        """→ (붙은 방울 거리함수 또는 None, 떨어지는 방울 거리함수 또는 None)."""
        tx, ty = self.TAIL
        hang = None
        fall = None
        if frame < 0.62:                                     # 맺혀 늘어짐
            u = frame / 0.62
            g = smooth(0, 0.3, u)                            # 꼬리 속에서 0 부터 자라 나온다 — 한 바퀴 이음매에서 안 튐
            r = 0.01 + 0.91 * smooth(0, 1, u)
            cy = ty - 0.8 + 2.9 * u * u
            neck = 0.01 + (0.41 - 0.26 * u) * g
            hang = smin(0.02 + 0.43 * g, capsule(tx, ty - 0.8, tx, cy, neck), circle(tx, cy, r))
        if 0.58 <= frame < 0.97:                             # 떨어지며 식어 작아짐
            u = (frame - 0.58) / 0.39
            cy = ty + 2.1 + 6.4 * u * u
            r = 0.92 * (1 - u ** 2.5)
            if r > 0.04:
                fall = circle(tx, cy + 0.6 * (0.92 - r), r)
        return hang, fall

    def extra(self, name, frame, layers, hot):
        if name not in ARROWISH:
            return layers
        hang, fall = self.drop(frame)
        if hang is not None:
            layers[0]["f"] = smin(0.02 + 0.53 * smooth(0, 0.2, frame / 0.62), layers[0]["f"], hang)
        if fall is not None:
            layers = layers + [dict(f=fall)]
        return layers

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        pal = self.WARN if warn else self.LAVA
        w = flow(x, y, frame, 0.25, 4.0, 5)                          # 느린 굽이
        n1 = flow(x + 2.5 * w, y, frame, 0.55, 6.0, 6)               # 한 바퀴에 6칸 흘러내림
        n2 = flow(x, y, frame, 1.2, 6.0, 7)
        m = n1 * 0.78 + n2 * 0.22
        inner = smooth(0.2, 0.8, depth)
        crust = smooth(0.49, 0.57, m) * inner                         # 굳은 껍질 — 테 가까이는 녹아 있음
        seam = exp(-((n2 - 0.5) / 0.045) ** 2) * crust               # 껍질 사이 갈라진 틈이 달아오름
        rimglow = exp(-((m - 0.53) / 0.03) ** 2) * inner             # 껍질 가장자리
        heat = 0.42 + 0.30 * smooth(0.0, 1.8, depth) + 0.55 * (0.47 - m)
        c = ramp_to(pal, heat)
        n3 = dome(nx, ny, depth, 1.5)
        lit = max(0.0, dot3(n3, L3))
        rock = lerp(scale(pal[0], 0.55), scale(pal[1], 0.75), 0.55 * lit)
        c = lerp(c, rock, 0.95 * crust)
        c = lerp(c, pal[3], 0.85 * seam)
        c = lerp(c, pal[4], 0.55 * rimglow)
        spec = max(0.0, dot3(n3, H3)) ** 14                          # 끈적한 윤기
        c = lerp(c, (1.0, 0.97, 0.85), 0.6 * spec)
        return lerp(c, pal[0], 0.85 * exp(-(depth / 0.22) ** 2)), 1.0

    def glow(self, x, y, d, warn, frame):
        return (self.WARN if warn else self.LAVA)[2], 0.42 * exp(-d / 0.55)


# ---- 전기 ----

def solid_of(layers):
    fs = [L["f"] for L in layers if not L.get("ink") and L.get("alpha", 1.0) > 0]
    return lambda x, y: min(g(x, y) for g in fs)


_EDGES = {}


def edges(name, f, hot, keep=3.0):
    """칸 테두리 위 점들 [(x, y, nx, ny)] — 0.5칸 격자에서 거리가 0 가까운 자리. 칸마다 한 번만 잰다."""
    if name in _EDGES:
        return _EDGES[name]
    out = []
    for iy in range(2, 63):
        for ix in range(2, 63):
            x, y = ix * 0.5, iy * 0.5
            e = f(x, y)
            if abs(e) > 0.26 or hypot(x - hot[0], y - hot[1]) < keep:
                continue
            gx, gy = f(x + 0.05, y) - f(x - 0.05, y), f(x, y + 0.05) - f(x, y - 0.05)
            gl = hypot(gx, gy)
            if gl > 1e-6:
                out.append((x - e * gx / gl, y - e * gy / gl, gx / gl, gy / gl))
    _EDGES[name] = out
    return out


def zigzag(rng, p, q, amp, n):
    """p→q 를 n 마디로 꺾은 번개 줄기 점들. 가운데일수록 크게 흔들린다."""
    (ax, ay), (bx, by) = p, q
    L = hypot(bx - ax, by - ay) or 1.0
    px, py = -(by - ay) / L, (bx - ax) / L
    pts = [p]
    for i in range(1, n):
        t = i / n
        o = (rng.random() * 2 - 1) * amp * math.sin(math.pi * t) ** 0.6
        pts.append((ax + (bx - ax) * t + px * o, ay + (by - ay) * t + py * o))
    pts.append(q)
    return pts


def inbox(p, m=0.8):
    return (min(max(p[0], m), 32 - m), min(max(p[1], m), 32 - m))


class Electric:
    """검은 유리 몸에 노란 전류 테가 흐르며 번쩍이고, 둘레로 푸른 방전 줄기가 튄다 — 줄기는 판마다 새로 꺾는 선 레이어."""
    ko = "전기"
    about = "검은 몸의 노란 테를 따라 전류가 번쩍이며 흐르고, 둘레로 푸른 번개 줄기가 탁탁 튀어요."
    LOOP = 1.07
    shadow = (0.04, 0.06, 0.14, 0.26)
    ink = (1.0, 0.90, 0.30)
    K = 8                                                    # 한 바퀴에 방전 판 수
    warn_now = False

    def step(self, frame):
        k = int(frame * self.K + 1e-9) % self.K
        return k, frame * self.K - floor(frame * self.K + 1e-9)

    def extra(self, name, frame, layers, hot):
        import random
        k, u = self.step(frame)
        warn = any(L.get("warn") for L in layers)
        E = edges(name, solid_of(layers), hot)
        if not E:
            return layers
        rng = random.Random(sum(map(ord, name)) * 131 + k * 7919)
        caps = []
        for b in range(3):
            x0, y0, nx, ny = E[rng.randrange(len(E))]
            if b != 1:                                      # 밖으로 뻗는 줄기 + 곁가지
                ang = math.atan2(ny, nx) + (rng.random() - 0.5) * 0.9
                L = 1.8 + 1.1 * rng.random()
                q = inbox((x0 + cos(ang) * L, y0 + sin(ang) * L))
                pts = zigzag(rng, (x0, y0), q, 0.45, 6)
                m = pts[3]
                ang2 = ang + (0.7 if rng.random() < 0.5 else -0.7)
                br = zigzag(rng, m, inbox((m[0] + cos(ang2) * 1.0, m[1] + sin(ang2) * 1.0)), 0.25, 3)
                lines = [(pts, 0.085), (br, 0.06)]
            else:                                           # 테의 두 점 사이를 건너뛰는 활
                near = [e for e in E if 2.5 < hypot(e[0] - x0, e[1] - y0) < 5.5]
                if not near:
                    continue
                x1, y1, mx, my = near[rng.randrange(len(near))]
                bx, by = (nx + mx), (ny + my)
                bl = hypot(bx, by) or 1.0
                cx = (x0 + x1) / 2 + bx / bl * 1.3
                cy = (y0 + y1) / 2 + by / bl * 1.3
                pts = zigzag(rng, (x0, y0), inbox((cx, cy)), 0.3, 3)[:-1] + \
                    zigzag(rng, inbox((cx, cy)), (x1, y1), 0.3, 3)
                lines = [(pts, 0.075)]
            for pts, w in lines:
                for i in range(len(pts) - 1):
                    caps.append(capsule(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], w))
        if not caps:
            return layers
        env = 0.55 + 0.45 * exp(-u * 3.0)
        core = (1.0, 0.86, 0.84) if warn else (0.88, 0.97, 1.0)
        halo = (1.0, 0.30, 0.32) if warn else (0.22, 0.58, 1.0)
        bolt = dict(f=union(*caps), shadow=False,
                    paint=lambda x, y, d, nx, ny, fr: (core, env),
                    glow=lambda x, y, d, fr: (halo, env * (0.85 * exp(-d / 0.2) + 0.22 * exp(-d / 0.8)) * box_fade(x, y)))
        return layers + [bolt]

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        k, u = self.step(frame)
        base = lerp((0.035, 0.04, 0.07), (0.08, 0.09, 0.15), clamp((x + y) / 40))
        n = dome(nx, ny, depth, 1.4)
        c = lerp(base, (0.55, 0.70, 1.0), 0.32 * max(0.0, dot3(n, H3)) ** 10)
        c = lerp(c, (0.20, 0.50, 1.0), 0.22 * exp(-((depth - 0.75) / 0.35) ** 2))   # 테 안쪽 푸른 빛
        flick = 0.82 + 0.18 * hsh(k, 3, 41)
        run = 0.5 + 0.5 * sin(TAU * 2 * frame - (x + y) * 0.38)                     # 테를 따라 흐르는 전류
        hotc = (1.0, 0.36, 0.30) if warn else (1.0, 0.84, 0.16)
        line = lerp(hotc, WHITE, 0.8 * run ** 6)
        band = smooth(0.52, 0.40, depth) * flick
        c = lerp(c, line, band)
        edge = (0.55, 0.06, 0.05) if warn else (0.66, 0.42, 0.0)
        return lerp(c, edge, 0.75 * exp(-(depth / 0.09) ** 2)), 1.0

    def glow(self, x, y, d, warn, frame):
        k, u = self.step(frame)
        hotc = (1.0, 0.36, 0.30) if warn else (1.0, 0.82, 0.22)
        return hotc, 0.36 * exp(-d / 0.45) * (0.75 + 0.25 * hsh(k, 3, 41))


# ---- 폭죽 ----

FW_T0 = 0.05                                                 # 터지는 때


def fw_flash(frame):
    u = frame - FW_T0
    if u < 0:
        return 0.0
    return smooth(0.0, 0.02, u) * exp(-u / 0.06)


class Firework:
    """밤빛 몸. 한 바퀴에 한 번 금빛으로 번쩍 터지며 테에서 불꽃 줄기가 두 겹으로 퍼져 나가 옅어지고,
    조용한 동안엔 몸 속에서 색 불똥이 톡톡 튄다."""
    ko = "폭죽"
    about = "남색 몸이 금빛으로 번쩍 터지면 불꽃 줄기가 두 겹으로 둘레에 퍼지며 사그라들고, 그 뒤엔 색 불똥이 톡톡 튀어요."
    LOOP = 2.4
    glow_n = True
    shadow = (0.04, 0.04, 0.16, 0.26)
    ink = (1.0, 0.86, 0.40)
    GOLD = [(1.0, 0.92, 0.62), (1.0, 0.70, 0.16), (1.0, 0.48, 0.18), (0.98, 0.36, 0.56)]
    WARN = [(1.0, 0.92, 0.80), (1.0, 0.55, 0.30), (1.0, 0.30, 0.25), (0.95, 0.25, 0.45)]
    POP = [(1.0, 0.45, 0.75), (0.40, 0.90, 1.0), (1.0, 0.85, 0.35), (0.65, 1.0, 0.55)]
    FADE = [(0.42, 0.22, 0.62), (0.98, 0.42, 0.58), (1.0, 0.74, 0.30), (1.0, 0.95, 0.74)]
    FADE_W = [(0.50, 0.10, 0.25), (0.95, 0.22, 0.25), (1.0, 0.50, 0.30), (1.0, 0.90, 0.78)]

    center = (12.0, 12.0)
    _centers = {}

    def extra(self, name, frame, layers, hot):
        if name not in self._centers:
            f = solid_of(layers)
            pts = [(gx + 0.5, gy + 0.5) for gy in range(32) for gx in range(32) if f(gx + 0.5, gy + 0.5) < 0]
            self._centers[name] = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)) if pts else (12.0, 12.0)
        self.center = self._centers[name]
        return layers

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        fl = fw_flash(frame)
        base = lerp((0.05, 0.06, 0.18), (0.11, 0.10, 0.30), clamp((x + y) / 44))
        n = dome(nx, ny, depth, 1.4)
        c = lerp(base, (0.55, 0.60, 1.0), 0.25 * max(0.0, dot3(n, H3)) ** 10)
        if fl > 0.004:                                   # 번쩍 — 금빛에서 산호·보라를 거쳐 남색으로 (갈색으로 안 섞이게)
            k = fl * (1.35 - 0.35 * smooth(0.0, 2.5, depth))
            c = ramp_to([c, self.FADE_W[0] if warn else self.FADE[0], (self.FADE_W if warn else self.FADE)[1],
                         (self.FADE_W if warn else self.FADE)[2], (self.FADE_W if warn else self.FADE)[3]], clamp(k))
        # 조용한 동안 색 불똥
        q = smooth(0.40, 0.55, frame) * smooth(1.0, 0.94, frame)
        if q > 0 and depth > 0.5:
            S = 1.7
            gx, gy = floor(x / S), floor(y / S)
            h = hsh(gx, gy, 61)
            if h > 0.55:
                px = (gx + 0.3 + 0.4 * hsh(gx, gy, 62)) * S
                py = (gy + 0.3 + 0.4 * hsh(gx, gy, 63)) * S
                u = (frame * 3 - hsh(gx, gy, 64)) % 1
                on = smooth(0, 0.04, u) * (1 - u) ** 6
                r2 = (x - px) ** 2 + (y - py) ** 2
                col = self.POP[int(hsh(gx, gy, 65) * 4) % 4] if not warn else self.WARN[2]
                c = lerp(c, col, clamp(q * on * (exp(-r2 / 0.06) + 0.4 * exp(-r2 / 0.3))))
                c = lerp(c, WHITE, clamp(q * on * exp(-r2 / 0.015)))
        rim = (1.0, 0.55, 0.55) if warn else (0.66, 0.70, 1.0)
        rim = lerp(rim, (1.0, 0.95, 0.75), fl)
        return lerp(c, rim, 0.92 * exp(-(depth / 0.34) ** 2)), 1.0

    def glow(self, x, y, d, warn, frame, nx=0.0, ny=0.0):
        fl = fw_flash(frame)
        pal = self.WARN if warn else self.GOLD
        rimc = (1.0, 0.45, 0.45) if warn else (0.55, 0.58, 1.0)
        parts = [(lerp(rimc, pal[1], fl), (0.34 + 0.4 * fl) * exp(-d / (0.55 + 0.5 * fl)))]
        if d > 0.05:
            cx, cy = self.center
            rho = hypot(x - cx, y - cy)
            th = math.atan2(y - cy, x - cx)
            bf = box_fade(x, y)
            NB = 30
            for j in (0, 1):                                   # 한 겹씩 — 바깥 겹이 먼저, 안 겹이 뒤따름
                tau = (frame - FW_T0 - 0.07 * j) / 0.62
                if not 0.0 < tau < 1.0:
                    continue
                q = th / (TAU / NB) + 0.5 * j
                bi = floor(q)
                key = bi % NB
                h = hsh(key, j, 70)
                if h < 0.18:
                    continue
                ang = (bi + 0.5 + 0.6 * (hsh(key, j, 71) - 0.5) - 0.5 * j) * (TAU / NB)
                lat = rho * sin(th - ang)
                lg = exp(-(lat / (0.17 + 0.04 * d)) ** 2)
                if lg < 0.01:
                    continue
                reach = (3.1 - 0.9 * j) * (0.70 + 0.4 * hsh(key, j, 76))
                rr = 0.3 + reach * (1 - (1 - tau) ** 2.4)
                head = exp(-((d - rr) / 0.22) ** 2)
                trail = 0.6 * exp(-(rr - d) / 0.9) if d < rr else 0.0
                fade = (1 - tau) ** 1.3
                tw = 1 - 0.55 * tau * (0.5 + 0.5 * sin(TAU * (frame * 24 + h * 5)))
                a = 1.3 * (head + trail) * lg * fade * tw * bf
                col = ramp_to(pal, tau * 0.9 + 0.15 * j)
                parts.append((lerp(col, WHITE, 0.6 * head * (1 - tau)), a))
        return mix(parts)


# ---- 반짝이는 별 ----

def star_on(u):
    """한 바퀴 안의 자리 u(0..1) → 켜짐 0..1. 짧게 켜지고 길게 꺼진다, u=0·1 둘 다 0."""
    if u < 0.06:
        return smooth(0.0, 0.06, u)
    return ((1 - u) / 0.94) ** 3.5


class Twinkle:
    """쪽빛 공단 몸에 두꺼운 라일락 테. 몸 속 별 자리 몇 개가 끝에서부터 차례로 켜졌다 꺼지고, 가끔 둘레 밖에도 하나 반짝인다."""
    ko = "반짝이는 별"
    about = "보랏빛 테를 두른 쪽빛 몸 속에서 금빛 별이 끝에서부터 하나씩 차례로 켜졌다 꺼지고, 둘레 밖에도 별 하나가 반짝여요."
    LOOP = 1.6
    shadow = (0.10, 0.04, 0.22, 0.26)
    ink = (1.0, 0.92, 0.55)
    LINE = 0.62
    stars = ()

    def extra(self, name, frame, layers, hot):
        solid = [L["f"] for L in layers if not L.get("ink") and L.get("alpha", 1.0) > 0]
        inks = [L["f"] for L in layers if L.get("ink")]

        def f(x, y):
            return min(g(x, y) for g in solid)
        G = 2.7
        inside, outside = [], []
        for gy in range(12):
            for gx in range(12):
                px = (gx + 0.25 + 0.5 * hsh(gx, gy, 81)) * G
                py = (gy + 0.25 + 0.5 * hsh(gx, gy, 82)) * G
                if not (1.5 < px < 30.5 and 1.5 < py < 30.5):
                    continue
                if hypot(px - hot[0], py - hot[1]) < 2.6:
                    continue
                if any(g(px, py) < 1.2 for g in inks):
                    continue
                e = f(px, py)
                if e < -0.75:
                    inside.append((px, py, e))
                elif 1.6 < e < 2.6:
                    outside.append((px, py, e))
        inside.sort(key=lambda s: s[2])                  # 깊은 자리부터 고르고
        pick = []
        for s in inside:
            if all(hypot(s[0] - p[0], s[1] - p[1]) > 2.6 for p in pick):
                pick.append(s)
            if len(pick) >= 7:
                break
        outside.sort(key=lambda s: s[1] - s[0])          # 오른쪽 위부터
        out = []                                         # 몸 속 자리가 모자란 가는 칸은 둘레 밖 별을 더 둔다
        for s in outside:
            if all(hypot(s[0] - p[0], s[1] - p[1]) > 5.0 for p in out):
                out.append(s)
            if len(out) >= (1 if len(pick) >= 3 else 4 - len(pick)):
                break
        seq = sorted(pick, key=lambda s: s[0] + s[1])    # 끝(왼쪽 위)에서부터 차례로
        for k, o in enumerate(out):
            seq.insert((k + 1) * len(seq) // (len(out) + 1) + k, o)
        n = len(seq)
        self.stars = [(px, py, k / max(n, 1), e > 0) for k, (px, py, e) in enumerate(seq)]
        if not self.stars:
            return layers
        R = 2.5
        cover = union(*[circle(px, py, R) for px, py, _, _ in self.stars]) if len(self.stars) > 1 else \
            circle(self.stars[0][0], self.stars[0][1], R)
        return layers + [dict(f=cover, paint=self.sparkle, noglow=True, shadow=False)]

    def sparkle(self, x, y, d, nx, ny, frame):
        parts = []
        for px, py, ph, out in self.stars:
            dx, dy = x - px, y - py
            if abs(dx) > 2.5 or abs(dy) > 2.5:
                continue
            on = star_on((frame - ph) % 1.0)
            ax, ay = abs(dx), abs(dy)
            r2 = dx * dx + dy * dy
            r = math.sqrt(r2)
            if not out:                                   # 꺼진 별 자리 — 희미한 점
                parts.append(((0.78, 0.70, 1.0), 0.40 * (1 - on) * exp(-r2 / 0.05)))
            if on < 0.01:
                continue
            big = 1.6 + 0.4 * on
            arm = exp(-(min(ax, ay) / (0.08 * big)) ** 2) * exp(-max(ax, ay) / (0.45 * big))
            u, v = (dx + dy) * 0.7071, (dx - dy) * 0.7071
            diag = 0.6 * exp(-(min(abs(u), abs(v)) / 0.07) ** 2) * exp(-max(abs(u), abs(v)) / (0.22 * big))
            core = exp(-r2 / (0.07 * big))
            halo = 0.55 * exp(-r / (0.40 * big))
            parts.append(((1.0, 0.80, 0.45), on * halo))
            parts.append(((1.0, 0.93, 0.62), on * clamp(arm + diag)))
            parts.append((WHITE, on * core))
        return mix(parts)

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        base = lerp((0.06, 0.05, 0.20), (0.17, 0.09, 0.34), clamp((x * 0.4 + y) / 30))
        n = dome(nx, ny, depth - self.LINE, 1.3)
        sheen = 0.5 + 0.5 * sin((x - y) * 0.35 + TAU * frame)        # 공단 결 — 비스듬히 흐르는 은은한 빛
        c = lerp(base, (0.36, 0.26, 0.62), 0.22 * sheen * smooth(0.6, 2.5, depth))
        c = lerp(c, (0.70, 0.62, 1.0), 0.18 * max(0.0, dot3(n, H3)) ** 8)
        # 두꺼운 라일락 테 — 둥글게 솟은 단면, 왼쪽 위에 빛
        rim = (1.0, 0.52, 0.58) if warn else (0.74, 0.58, 1.0)
        nr = dome(nx, ny, depth, self.LINE)
        lit = dot3(nr, L3)
        rc = scale(rim, 0.78 + 0.32 * lit)
        rc = lerp(rc, WHITE, 0.45 * max(0.0, dot3(nr, H3)) ** 12)
        rc = lerp(rc, (0.32, 0.16, 0.55) if not warn else (0.55, 0.10, 0.20), 0.7 * exp(-(depth / 0.09) ** 2))
        t = smooth(self.LINE + 0.06, self.LINE - 0.06, depth)
        return lerp(c, rc, t), 1.0

    def glow(self, x, y, d, warn, frame):
        return ((1.0, 0.45, 0.55) if warn else (0.66, 0.50, 1.0)), 0.36 * exp(-d / 0.6)




register("flicker", Flicker())
register("lavaflow", Lava())
register("electric", Electric())
register("firework", Firework())
register("twinkle", Twinkle())

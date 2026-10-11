# SPDX-License-Identifier: Apache-2.0
"""이펙트 · 애니 다섯 — 무지개 흐름 · 카멜레온 · 이발소 기둥 · 네온 맥박 · 두근두근.
움직임은 frame(0..1) 에 주기로만 기대 끝 장에서 첫 장으로 튀지 않는다."""
from . import *  # noqa: F401,F403
from . import register, hd, TAU, WHITE, clamp, smooth, lerp, dome, dot3, scale, hsh, noise, L3, H3, LX, LY  # noqa: F401
import math

exp, sin, cos, floor, sqrt = math.exp, math.sin, math.cos, math.floor, math.sqrt


def cyc(pal, t):
    """감기는 Catmull-Rom 색 고리 — ramp 처럼 이음마다 멈칫하지 않고 고르게 돈다."""
    n = len(pal)
    t = (t % 1.0) * n
    i = int(t)
    f = t - i
    f2, f3 = f * f, f * f * f
    a, b, c, d = pal[(i - 1) % n], pal[i % n], pal[(i + 1) % n], pal[(i + 2) % n]
    return tuple(clamp(0.5 * (2 * q1 + (q2 - q0) * f + (2 * q0 - 5 * q1 + 4 * q2 - q3) * f2
                              + (3 * q1 - q0 - 3 * q2 + q3) * f3)) for q0, q1, q2, q3 in zip(a, b, c, d))


def pulse(frame, t0, rise, fall):
    """t0 에서 rise 만에 솟고 fall 로 사그라드는 박동 하나(주기 1). 한 바퀴 뒤엔 0 에 붙어 이음매가 없다."""
    u = (frame - t0) % 1.0
    if u < rise:
        return smooth(0.0, rise, u)
    return exp(-(u - rise) / fall)


def gloss(c, n, k, p):
    return lerp(c, WHITE, k * max(0.0, dot3(n, H3)) ** p)


# ---- 무지개 흐름 ----

class RainbowFlow:
    """유리 막대 속을 흐르는 무지개. 띠는 12칸 주기로 위로 흐르고 가운데가 살짝 처진 물결 모양이다."""
    ko = "무지개 흐름"
    about = "무지개 띠가 유리 같은 몸 속을 물결치며 위로 흘러가요."
    LOOP = 0.8
    shadow = (0.12, 0.06, 0.22, 0.26)
    ink = (0.14, 0.09, 0.24)
    glow = None
    P = 12.0
    PAL = [(1.0, 0.24, 0.30), (1.0, 0.56, 0.16), (1.0, 0.86, 0.20), (0.28, 0.84, 0.40),
           (0.20, 0.56, 1.0), (0.60, 0.32, 0.96)]
    WARN = [(1.0, 0.20, 0.26), (1.0, 0.48, 0.18), (0.96, 0.18, 0.46)]

    def hue(self, x, y, warn, frame):
        pal = self.WARN if warn else self.PAL
        k = len(pal)
        # 띠를 조금 기울인다 — 수평이면 ↔·십자 가로 획이 띠 하나 색만 받아 단색이 됐다
        u = ((y + 0.38 * x + 0.55 * sin(x * 0.42 + 0.6)) / self.P + frame) * k
        i = floor(u)
        f = smooth(0.18, 0.82, u - i)                     # 띠마다 제 색이 머물고 이음만 부드럽게
        return lerp(pal[i % k], pal[(i + 1) % k], f)

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        n = dome(nx, ny, depth, 1.3)
        h = self.hue(x, y, warn, frame)
        tilt = 1 - n[2]
        c = lerp(h, WHITE, 0.30 * tilt * max(0.0, -(nx * LX + ny * LY)))  # 아래 오른쪽 테로 빛이 비침
        c = scale(c, 0.84 + 0.20 * dot3(n, L3))
        c = lerp(c, WHITE, 0.32 * exp(-((depth - 0.55) / 0.22) ** 2) * clamp(-(nx * LX + ny * LY) * -1.4))  # 왼쪽 위 유리 결
        c = gloss(c, n, 0.70, 16)
        c = lerp(c, (0.16, 0.10, 0.28), 0.85 * exp(-(depth / 0.24) ** 2))
        return c, 1.0


# ---- 카멜레온 ----

HEX = 0.62                     # 비늘 사이(칸)
HEXH = HEX * sqrt(3)


def scales(x, y):
    """육각 비늘 — 가장 가까운 비늘 가운데까지 (dx, dy) 와 비늘 번호. 직교 격자 둘을 엇갈려 닫힌 식으로."""
    best = None
    for ox, oy in ((0.0, 0.0), (HEX / 2, HEXH / 2)):
        gx, gy = round((x - ox) / HEX), round((y - oy) / HEXH)
        dx, dy = x - (ox + gx * HEX), y - (oy + gy * HEXH)
        q = dx * dx + dy * dy
        if best is None or q < best[0]:
            best = (q, dx, dy, gx * 2 + (ox > 0), gy)
    return best


class Chameleon:
    """잔 비늘이 돋은 반질한 살갗. 끝에서 꼬리 쪽으로 물들며 색상환을 따라 천천히 돈다."""
    ko = "카멜레온"
    about = "잔 비늘이 돋은 몸빛이 끝에서부터 색상환을 따라 천천히 물들어 가요."
    LOOP = 4.0
    shadow = (0.08, 0.12, 0.10, 0.26)
    ink = (0.08, 0.12, 0.10)
    glow = None
    PAL = [(0.40, 0.82, 0.28), (0.12, 0.74, 0.60), (0.36, 0.56, 0.98), (0.74, 0.44, 0.94),
           (1.0, 0.44, 0.58), (1.0, 0.58, 0.22), (0.92, 0.84, 0.20)]
    WARN = [(1.0, 0.30, 0.30), (1.0, 0.50, 0.24), (0.94, 0.26, 0.52)]

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        q, sx, sy, gi, gj = scales(x, y)
        r = sqrt(q) / (HEX * 0.58)
        jit = hsh(gi, gj, 3) - 0.5
        t = frame - 0.20 * (x + y) / 30 + 0.012 * jit       # 끝이 먼저 물든다. 비늘마다 색이 아주 조금 어긋남
        h = cyc(self.WARN if warn else self.PAL, t)
        n = dome(nx, ny, depth, 1.5)
        c = scale(h, 0.80 + 0.26 * dot3(n, L3) + 0.08 * jit)
        bump = clamp(1 - r)                                   # 비늘 하나의 볼록면: 왼쪽 위가 밝다
        lit = -(sx * LX + sy * LY) / (HEX * 0.58)
        c = lerp(c, WHITE, 0.16 * bump * clamp(-lit))
        c = scale(c, 1.0 - 0.14 * smooth(0.65, 1.0, r))       # 비늘 사이 골
        c = gloss(c, n, 0.45, 10)
        c = lerp(c, scale(h, 0.32), 0.85 * exp(-(depth / 0.26) ** 2))
        return c, 1.0


# ---- 이발소 기둥 ----

def band(u, a, b, w):
    return sum(smooth(a - w, a + w, u + k) - smooth(b - w, b + w, u + k) for k in (-1.0, 0.0, 1.0))


class Barber:
    """에나멜 유리 기둥. 빨강·흰·파랑 사선 줄이 감기듯 끝 쪽으로 올라가고, 테로 갈수록 줄이 휘어 둥근 기둥으로 읽힌다."""
    ko = "이발소 기둥"
    about = "윤나는 유리 기둥 위로 빨강·흰·파랑 줄무늬가 감기듯 올라가요."
    LOOP = 1.0
    shadow = (0.08, 0.10, 0.26, 0.26)
    ink = (0.10, 0.12, 0.30)
    glow = None
    P = 12.0                   # 8 이면 32px 에서 줄이 2px 밑으로 가늘어 뭉개졌다
    RED, BLUE, PAPER = (0.88, 0.12, 0.18), (0.14, 0.30, 0.82), (0.98, 0.97, 0.95)

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        n = dome(nx, ny, depth, 1.2)
        tilt = 1 - n[2]
        # `/` 로 누운 칸(↗↙·펜)은 사선 줄과 획이 나란해 획째 한 색으로 깜빡였다 — 그 칸만 가로 줄로 비스듬히 감는다
        if getattr(self, "cell_name", "") in ("nesw", "pen"):
            s, ns = 1.414 * y, 1.414 * ny
        else:
            s, ns = x + y, nx + ny
        u = (s / self.P + 0.12 * tilt * ns + frame) % 1.0
        w = 0.035
        wr = band(u, 0.50, 0.80, w)
        wb = band(u, 0.00, 0.30, w)
        c = lerp(self.PAPER, self.RED, wr)
        c = lerp(c, self.RED if warn else self.BLUE, wb)
        return self.finish(c, n, depth), 1.0

    def finish(self, c, n, depth):
        c = scale(c, 0.80 + 0.26 * dot3(n, L3))
        c = gloss(c, n, 0.80, 16)
        return lerp(c, (0.08, 0.08, 0.22), 0.85 * exp(-(depth / 0.24) ** 2))

    def enamel(self, x, y, d, nx, ny, frame):
        """도움말 원판은 흰 에나멜 — 줄무늬 위에서는 남색 물음표가 묻혔다."""
        return self.finish(self.PAPER, dome(nx, ny, -d, 1.2), -d), 1.0

    def extra(self, name, frame, layers, hot):
        if name == "help":
            layers[1]["paint"] = self.enamel
        return layers


# ---- 네온 맥박 ----

def breath(frame):
    return 0.5 - 0.5 * cos(TAU * frame)


class NeonPulse:
    """검은 유리관 테두리를 도는 청록 네온. 번짐이 숨 쉬듯 넓어졌다 잦아든다."""
    ko = "네온 맥박"
    about = "검은 유리관 테두리의 청록 네온이 숨 쉬듯 번졌다 잦아들어요."
    LOOP = 1.2
    soft = 0.4                 # 가는 획(십자·I빔)에도 검은 속이 남게 — 안 부풀리면 흰 바탕 32px 에서 옅은 청록 한 줄이었다
    shadow = (0.02, 0.04, 0.08, 0.22)
    ink = (0.80, 1.0, 1.0)
    CYAN, HOT = (0.16, 0.92, 1.0), (1.0, 0.24, 0.36)

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        b = breath(frame)
        neon = self.HOT if warn else self.CYAN
        deep = (0.55, 0.06, 0.14) if warn else (0.0, 0.40, 0.54)
        base = lerp((0.04, 0.05, 0.09), (0.08, 0.06, 0.14), clamp((x + y) / 44))
        c = lerp(base, neon, (0.10 + 0.08 * b) * exp(-depth / 1.4))           # 관 속으로 스민 빛
        # 관: 테에서 0.7 칸 안까지. 바깥 0.1 칸은 짙은 청록이라 흰 바탕에서도 윤곽이 서고, 0.32 칸에 흰 심
        c = lerp(c, neon, smooth(0.78, 0.48, depth) * (0.88 + 0.12 * b))
        c = lerp(c, deep, smooth(0.22, 0.05, depth))
        c = lerp(c, WHITE, (0.40 + 0.30 * b) * exp(-((depth - 0.32) / 0.11) ** 2))
        sheen = exp(-((x - y * 0.55 - 1.0) / 0.9) ** 2) * smooth(1.0, 1.6, depth)   # 유리 비낌
        c = lerp(c, WHITE, 0.10 * sheen)
        return c, 0.97

    def glow(self, x, y, d, warn, frame):
        b = breath(frame)
        return (self.HOT if warn else self.CYAN), (0.30 + 0.42 * b) * exp(-d / (0.40 + 0.75 * b))


# ---- 두근두근 ----

def beat(frame):
    return pulse(frame, 0.06, 0.04, 0.07) + 0.75 * pulse(frame, 0.30, 0.04, 0.08)


class Heartbeat:
    """새틴 분홍 몸. 콩닥 두 번 안에서부터 환해지며 3% 부풀고, 번짐 고리가 물결처럼 밖으로 퍼진다."""
    ko = "두근두근"
    about = "분홍 몸이 콩닥 두 번 안에서부터 환해지고, 번짐이 물결처럼 퍼져 나가요."
    LOOP = 0.8
    shadow = (0.45, 0.06, 0.24, 0.22)
    ink = (1.0, 1.0, 1.0)
    BEATS = ((0.06, 1.0), (0.30, 0.75))

    def extra(self, name, frame, layers, hot):
        k = 1.0 + 0.03 * beat(frame)                       # 핫스팟을 축으로 부푼다 — 끝은 제자리
        hx, hy = hot
        for L in layers:
            L["f"] = (lambda f: lambda x, y: k * f(hx + (x - hx) / k, hy + (y - hy) / k))(L["f"])
        return layers

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        b = clamp(beat(frame))
        base, lite, line = (((0.80, 0.10, 0.16), (1.0, 0.56, 0.50), (0.40, 0.03, 0.06)) if warn else
                            ((0.78, 0.18, 0.44), (1.0, 0.62, 0.84), (0.38, 0.04, 0.18)))
        n = dome(nx, ny, depth, 1.6)
        core = smooth(0.2, 1.6, depth)                       # 안쪽일수록 먼저 환해진다
        c = lerp(base, lite, b * (0.45 + 0.55 * core))
        c = scale(c, 0.84 + 0.22 * dot3(n, L3))
        c = gloss(c, n, 0.55, 12)
        c = lerp(c, line, (0.80 - 0.35 * b) * exp(-(depth / 0.19) ** 2))   # 0.24 면 가는 획이 어두운 바탕에서 와인색에 묻혔다
        return c, 1.0

    def glow(self, x, y, d, warn, frame):
        col = (1.0, 0.30, 0.34) if warn else (1.0, 0.42, 0.72)
        a = (0.16 + 0.46 * clamp(beat(frame))) * exp(-d / 0.75)
        for t0, amp in self.BEATS:                           # 박동마다 밖으로 퍼지는 고리
            u = (frame - t0) % 1.0
            if u < 0.30:
                r = 0.3 + 2.6 * u / 0.30
                a += amp * 0.32 * (1 - u / 0.30) * exp(-((d - r) / 0.45) ** 2)
        return col, min(a, 0.9)




register("rainbowflow", RainbowFlow())
register("chameleon", Chameleon())
register("barber", Barber())
register("neonpulse", NeonPulse())
register("heartbeat", Heartbeat())

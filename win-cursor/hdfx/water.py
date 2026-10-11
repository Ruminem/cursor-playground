# SPDX-License-Identifier: Apache-2.0
"""이펙트 · 애니 다섯 (물·날씨) — 파도 · 빗줄기 · 기포 · 눈 내림 · 파문.

픽셀 원본(art/<결>/)의 움직임 생각은 그대로 두고 hd.py 말씨(유리 같은 몸, 하이라이트, 부드러운 테)로 다시 그린다.
움직임은 모두 frame(0..1) 에 주기로만 걸어서 끝 장 → 첫 장이 이어진다. 알갱이(빗줄기·기포·눈송이)는
닫힌 식이거나, extra() 에서 장마다 한 번 만든 작은 목록을 칸마다 훑는다.
"""
import math

from . import *  # noqa: F401,F403
from . import register, hypot, exp, sin, cos, floor


def solid(layers):
    """칠하는 몸(잉크·안 보이는 판 빼고)의 합친 거리함수."""
    fs = [L["f"] for L in layers if not L.get("ink") and L.get("alpha", 1.0) > 0]
    return lambda x, y: min(f(x, y) for f in fs)


def centroid(f, step=0.75):
    """몸 안 칸들의 무게중심과, 거기서 가장 먼 몸 칸까지 거리."""
    pts = []
    k = int(32 / step)
    for j in range(k):
        for i in range(k):
            x, y = (i + 0.5) * step, (j + 0.5) * step
            if f(x, y) < 0:
                pts.append((x, y))
    if not pts:
        return (12.0, 12.0), 10.0
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return (cx, cy), max(hypot(p[0] - cx, p[1] - cy) for p in pts)


def glassy(c, depth, nx, ny, line, R=1.5, spec=0.75, rim=0.35, rimc=WHITE, lw=0.22, pw=14):
    """유리 껍질: 둥근 면 빛, 테 안쪽의 가는 반사선, 왼쪽 위 젖은 반짝임, 바깥 윤곽선."""
    n = dome(nx, ny, depth, R)
    lit = dot3(n, L3)
    c = scale(c, 0.88 + 0.18 * lit)
    c = lerp(c, rimc, rim * exp(-((depth - lw * 1.9) / 0.13) ** 2))
    sp = clamp(1.5 * max(0.0, dot3(n, H3)) ** pw - 0.15)
    c = lerp(c, WHITE, spec * sp)
    return lerp(c, line, 0.92 * exp(-(depth / lw) ** 2))


# ---- 파도 ----

class Wave:
    """유리 화살표에 바다가 반쯤 차 있다. 물낯이 옆으로 흐르고, 마루마다 포말이 짙어진다."""
    ko = "파도"
    about = "유리 커서 안에 바다가 반쯤 차 있어서, 물결 띠가 옆으로 넘실대고 마루마다 흰 포말이 따라 흘러요."
    LOOP = 1.6
    tip_body = True
    shadow = (0.03, 0.12, 0.28, 0.26)
    shadow_off, shadow_blur = (0.45, 0.95), 2.0
    ink = WHITE
    SKY = ((1.0, 0.96, 0.88), (1.0, 0.80, 0.60))
    SEA = [(0.42, 0.84, 0.98), (0.13, 0.55, 0.88), (0.05, 0.25, 0.58), (0.03, 0.14, 0.36)]
    WSKY = ((1.0, 0.86, 0.82), (1.0, 0.62, 0.56))
    WSEA = [(1.0, 0.52, 0.46), (0.88, 0.18, 0.22), (0.58, 0.06, 0.12), (0.36, 0.03, 0.08)]
    LINE = (0.03, 0.12, 0.30)
    WLINE = (0.36, 0.04, 0.08)
    WL = 11.4                  # 물낯 높이
    K = 0.78                   # 물결 수 — 한 파장 8칸
    NF = 6                     # 한 파장에 거품 칸 수 (흐르는 거품이 한 바퀴에 제자리로)

    def level(self, x, frame):
        p = TAU * frame
        return self.WL + 1.0 * sin(x * self.K - p) + 0.30 * sin(x * self.K * 2 - 2 * p + 1.3)

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        h = self.level(x, frame)
        s = y - h                                                    # 물낯 아래로 + 칸
        sky0, sky1 = self.WSKY if warn else self.SKY
        sky = lerp(sky0, sky1, smooth(h - 9.0, h + 0.5, y))
        t = clamp(s / 10.0)
        sea = ramp_to(self.WSEA if warn else self.SEA, t)
        p = TAU * frame
        # 물낯 아래 한 겹 더 — 깊이감(원본의 띠)
        s2 = s - 2.3 - 0.45 * sin(x * self.K - p + 2.1)
        sea = lerp(sea, ramp_to(self.WSEA if warn else self.SEA, max(0.0, t - 0.22)), 0.55 * exp(-(s2 / 0.45) ** 2))
        # 물속 빛그물(코스틱) — 잡음 자리가 원을 돌아 주기가 맞는다
        ox, oy = 1.4 * cos(p), 1.4 * sin(p)
        nz = noise((x + ox) * 0.42, (y * 1.5 + oy) * 0.42, 3)
        caus = clamp(1 - abs(nz - 0.5) * 6.5)
        sea = lerp(sea, (0.80, 0.95, 1.0) if not warn else (1.0, 0.80, 0.78), 0.20 * caus * (1 - t) * smooth(0.3, 1.2, s))
        c = lerp(sky, sea, smooth(-0.10, 0.10, s))
        # 포말: 물낯 바로 아래 흰 띠, 마루일수록 두껍다
        crest = smooth(-0.6, 1.25, self.WL - h)
        fw = 0.18 + 0.50 * crest
        foam = smooth(-0.10, 0.03, s) * smooth(fw + 0.10, fw - 0.06, s)
        # 마루 밑 거품 점 — 물결을 따라 흐르는 좌표에 박는다
        lam = TAU / self.K
        xw = x - frame * lam
        cw = lam / self.NF
        i = floor(xw / cw)
        for j in (i - 1, i, i + 1):
            jj = j % self.NF
            bx = (j + 0.25 + 0.5 * hsh(jj, 1, 21)) * cw + frame * lam
            bh = self.level(bx, frame)
            bcrest = smooth(-0.2, 1.2, self.WL - bh)
            if bcrest <= 0:
                continue
            by = bh + 0.35 + 0.35 * crest + 0.55 * hsh(jj, 2, 21)
            br = 0.15 + 0.14 * hsh(jj, 3, 21)
            foam = max(foam, bcrest * smooth(br + 0.05, br - 0.05, hypot(x - bx, y - by)))
        c = lerp(c, (1.0, 1.0, 1.0) if not warn else (1.0, 0.92, 0.90), 0.92 * foam)
        return glassy(c, depth, nx, ny, self.WLINE if warn else self.LINE, rim=0.30), 1.0


# ---- 빗줄기 ----

class Rainfall:
    """밤 유리창. 짙은 남색 유리 안으로 줄마다 다른 박자로 빗줄기가 쉬지 않고 떨어진다."""
    ko = "빗줄기"
    about = "밤 유리창 같은 짙은 남색 커서 안으로, 줄마다 다른 박자로 가는 빗줄기가 쉬지 않고 떨어져요."
    LOOP = 1.2
    tip_body = True
    shadow = (0.02, 0.04, 0.10, 0.30)
    ink = WHITE
    CW = 1.90                  # 빗줄기 칸 너비

    def rain(self, x, y, frame):
        """빗줄기 밝기 0..1. 칸마다 한 줄, 주기 P 마다 되풀이, 한 바퀴에 k 번 떨어진다(정수라 이음매 없음)."""
        xs = x + 0.10 * y                                            # 살짝 비스듬히
        i = floor(xs / self.CW)
        best = 0.0
        for j in (i - 1, i, i + 1):
            h1, h2, h3, h4 = hsh(j, 1, 31), hsh(j, 2, 31), hsh(j, 3, 31), hsh(j, 4, 31)
            cx = (j + 0.25 + 0.5 * h1) * self.CW
            dx = abs(xs - cx)
            if dx > 0.9:
                continue
            P = 7.0 + 6.0 * h2
            k = 2 + (h3 > 0.55)
            Ls = 2.6 + 2.4 * h4
            v = ((y / P - hsh(j, 5, 31) - k * frame) % 1.0) * P              # 칸 안 자리(칸)
            head = P * 0.8
            b = 0.0
            if head - Ls <= v <= head:
                t = (v - head + Ls) / Ls
                b = t ** 1.4 * exp(-(dx / 0.28) ** 2)
            hd_ = exp(-((v - head) / 0.42) ** 2 - (dx / 0.34) ** 2)          # 빗방울 머리
            best = max(best, b * 0.85, hd_)
        return best

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        if warn:
            top, bot, rimc, drop = (0.34, 0.07, 0.12), (0.18, 0.03, 0.07), (1.0, 0.45, 0.50), (1.0, 0.78, 0.80)
        else:
            top, bot, rimc, drop = (0.12, 0.19, 0.40), (0.03, 0.06, 0.16), (0.56, 0.74, 1.0), (0.78, 0.92, 1.0)
        c = lerp(top, bot, clamp((y + x * 0.3) / 24))
        c = lerp(c, lerp(top, WHITE, 0.25), 0.22 * exp(-((x - y * 0.55 - 1.5) / 1.2) ** 2))   # 유리에 비친 비스듬한 빛줄
        r = self.rain(x, y, frame)
        c = lerp(c, drop, 0.95 * r)
        # 유리에 맺혀 안 움직이는 물방울
        g = 2.6
        gx, gy = floor(x / g), floor(y / g)
        if hsh(gx, gy, 37) > 0.80:
            bx = (gx + 0.3 + 0.4 * hsh(gx, gy, 38)) * g
            by = (gy + 0.3 + 0.4 * hsh(gx, gy, 39)) * g
            br = 0.22 + 0.16 * hsh(gx, gy, 40)
            q = hypot(x - bx, y - by)
            if q < br + 0.08:
                inside = smooth(br + 0.05, br - 0.05, q)
                lo = clamp(((x - bx) + (y - by)) / (br * 1.4))             # 아래 오른쪽이 밝다(굴절)
                c = lerp(c, lerp(c, drop, 0.35 + 0.4 * lo), inside)
                c = lerp(c, WHITE, 0.9 * inside * smooth(0.11, 0.04, hypot(x - bx + br * 0.35, y - by + br * 0.35)))
        c = glassy(c, depth, nx, ny, rimc, spec=0.55, rim=0.0, lw=0.20)
        c = lerp(c, rimc, 0.75 * exp(-(depth / 0.42) ** 2))           # 밝은 테 — 어두운 바탕에서 윤곽을 잡는다
        return c, 1.0

    def glow(self, x, y, d, warn, frame):
        return ((1.0, 0.40, 0.45) if warn else (0.42, 0.62, 1.0)), 0.45 * exp(-d / 0.7)


# ---- 기포 ----

class Bubbles:
    """물빛 유리 안에서 기포가 흔들리며 떠올라 커지다가 몸 테에 닿으면 톡 터진다."""
    ko = "기포"
    about = "맑은 물빛 커서 안에서 기포가 흔들흔들 떠올라 커지다가, 테에 닿으면 톡 터지며 물방울이 튀어요."
    LOOP = 1.6
    tip_body = True
    shadow = (0.02, 0.14, 0.32, 0.26)
    shadow_off, shadow_blur = (0.45, 0.95), 2.0
    ink = WHITE
    LINE = (0.02, 0.22, 0.32)
    WLINE = (0.40, 0.04, 0.10)
    POP = 0.07                 # 터지는 데 드는 몫
    # (가로 자리, 시작 위상, 반지름, 한 바퀴에 오르는 번 수)
    BUB = [(2.0 + 20.0 * hsh(i, 1, 51), hsh(i, 2, 51), 0.55 + 0.60 * hsh(i, 3, 51), 1 + (hsh(i, 4, 51) > 0.7))
           for i in range(22)]

    def path(self, b, p):
        x0, s, r0, k = b
        return x0 + 0.38 * sin(TAU * (p * 2.0 + s)), 25.0 - p * 27.0, r0 * (0.7 + 0.6 * p)

    def extra(self, name, frame, layers, hot):
        f = solid(layers)
        if getattr(self, "_for", None) != name:                     # 칸마다 한 번: 기포가 몸에 드는 때와 터지는 때
            span = []
            for b in self.BUB:
                pin = pout = None
                for k in range(121):
                    p = k / 120
                    x, y, r = self.path(b, p)
                    ins = f(x, y) < -(r + 0.2)
                    if pin is None and ins:
                        pin = p
                    elif pin is not None and not ins:
                        pout = p
                        break
                span.append((pin, pout))
            self._for, self._span = name, span
        act = []
        for b, (pin, pout) in zip(self.BUB, self._span):
            if pin is None or pout is None:
                continue
            p = (b[1] + b[3] * frame) % 1.0
            if pin <= p < pout:
                x, y, r = self.path(b, p)
                act.append((x, y, r * smooth(pin, pin + 0.06, p), 0, 0.0, b[1]))
            elif pout <= p < pout + self.POP:
                x, y, r = self.path(b, pout)
                act.append((x, y, r, 1, (p - pout) / self.POP, b[1]))
        self._act = act
        return layers

    def pop(self, x, y, cx, cy, r, q, s):
        """터짐: 퍼지며 옅어지는 고리 + 튀는 물방울 다섯. → 흰빛 세기."""
        e = (1 - q) ** 2
        R = r * (1.0 + 1.1 * q)
        v = e * exp(-((hypot(x - cx, y - cy) - R) / 0.10) ** 2)
        for k in range(5):
            a = TAU * (k / 5 + s)
            dd = r * (1.3 + 1.9 * q)
            v = max(v, e * smooth(0.16, 0.06, hypot(x - cx - dd * cos(a), y - cy - dd * sin(a))))
        return v

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        if warn:
            top, bot, lite = (1.0, 0.50, 0.50), (0.72, 0.10, 0.16), (1.0, 0.86, 0.86)
        else:
            top, bot, lite = (0.38, 0.90, 0.95), (0.05, 0.48, 0.72), (0.84, 1.0, 0.98)
        c = lerp(top, bot, smooth(2.0, 22.0, y + 0.25 * x))
        ray = 0.5 + 0.5 * sin(x * 0.9 - y * 0.35 + TAU * frame)       # 위에서 비치는 빛살이 일렁인다
        c = lerp(c, lite, 0.10 * ray * smooth(20.0, 2.0, y))
        for cx, cy, r, kind, q, s in self._act:
            if abs(x - cx) > r * 3.6 or abs(y - cy) > r * 3.6:
                continue
            if kind == 1:
                c = lerp(c, WHITE, 0.85 * self.pop(x, y, cx, cy, r, q, s))
                continue
            rho = hypot(x - cx, y - cy)
            if rho > r + 0.15:
                continue
            inner = smooth(r + 0.05, r - 0.05, rho)
            lo = clamp(((x - cx) + (y - cy)) / (r * 1.5))
            c = lerp(c, lite, inner * (0.30 + 0.35 * lo * lo))          # 속은 맑고, 아래 오른쪽에 빛이 모인다
            rim = exp(-((rho - r * 0.9) / (0.08 + 0.08 * r)) ** 2)
            up = clamp(0.5 - ((x - cx) + (y - cy)) / (r * 2.8))
            c = lerp(c, WHITE, 0.95 * rim * (0.55 + 0.45 * up))
            c = lerp(c, WHITE, smooth(0.36 * r, 0.18 * r, hypot(x - cx + r * 0.38, y - cy + r * 0.38)))
        return glassy(c, depth, nx, ny, self.WLINE if warn else self.LINE, rim=0.32), 1.0

    def glow(self, x, y, d, warn, frame):
        """몸 밖으로 튄 터짐만 옅게."""
        v = 0.0
        for cx, cy, r, kind, q, s in self._act:
            if kind == 1 and abs(x - cx) < r * 4 and abs(y - cy) < r * 4:
                v = max(v, self.pop(x, y, cx, cy, r, q, s))
        return ((1.0, 0.75, 0.75) if warn else (0.70, 0.92, 1.0)), 0.75 * v


# ---- 눈 내림 ----

def flake(x, y, r, crystal):
    if not crystal:
        return circle(x, y, r)
    arms = [capsule(x - r * cos(a), y - r * sin(a), x + r * cos(a), y + r * sin(a), 0.16)
            for a in (0.0, math.pi / 3, 2 * math.pi / 3)]
    return union(circle(x, y, 0.32), *arms)


class Snowfall:
    """서리 낀 흰 몸. 푸른 테와 그림자로 흰 바탕에서도 서고, 둘레로 눈송이가 몸 뒤를 지나 내린다."""
    ko = "눈 내림"
    about = "서리 낀 하얀 커서 둘레로 푸른 테를 두른 눈송이가 쉬지 않고 사르르 내려요."
    LOOP = 2.4
    shadow = (0.20, 0.34, 0.62, 0.38)
    shadow_off, shadow_blur = (0.45, 0.9), 2.0
    ink = (0.30, 0.46, 0.76)
    LINE = (0.38, 0.56, 0.84)
    # (가로, 위상, 반지름, 결정?, 흔들림)
    FLAKES = [(0.5 + 23.5 * hsh(i, 1, 61), (i / 7 + 0.4 * hsh(i, 2, 61)) % 1.0, 0.40 + 0.28 * hsh(i, 3, 61), False,
               hsh(i, 4, 61)) for i in range(7)] + [(5.5, 0.15, 1.1, True, 0.3), (19.5, 0.62, 1.0, True, 0.7)]

    def extra(self, name, frame, layers, hot):
        out = []
        for x0, s, r, crystal, w in self.FLAKES:
            p = (s + frame) % 1.0
            env = smooth(0.0, 0.14, p) * smooth(1.0, 0.84, p)
            if env <= 0.01:
                continue
            x = x0 + 0.7 * sin(TAU * (p * 1.5 + w))
            y = 1.5 + p * 28.5
            out.append(dict(f=flake(x, y, r, crystal), alpha=env, shadow=False,
                            paint=self.paint_flake, glow=self.glow_flake))
        return out + layers                                          # 몸 뒤로 지난다

    def paint_flake(self, x, y, d, nx, ny, frame):
        return lerp(WHITE, (0.80, 0.88, 1.0), smooth(-0.25, 0.0, d)), 1.0

    def glow_flake(self, x, y, d, frame):
        return (0.42, 0.60, 0.92), 0.55 * exp(-d / 0.30)

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        if warn:
            core, edge, line = (1.0, 0.62, 0.62), (0.90, 0.30, 0.34), (0.62, 0.08, 0.14)
        else:
            core, edge, line = (1.0, 1.0, 1.0), (0.84, 0.90, 0.99), self.LINE
        c = lerp(edge, core, smooth(0.1, 1.5, depth))
        n = dome(nx, ny, depth, 1.6)
        lit = dot3(n, L3)
        c = lerp(c, (0.66, 0.78, 0.96) if not warn else (0.70, 0.16, 0.22), 0.45 * clamp((0.45 - lit) / 1.1))
        # 서리 결 — 아주 옅은 잡음
        c = lerp(c, (0.80, 0.88, 1.0) if not warn else (1.0, 0.80, 0.80), 0.25 * clamp(noise(x * 1.3, y * 1.3, 62) - 0.45))
        # 반짝이는 얼음 알갱이
        st = 1.6
        gx, gy = floor(x / st), floor(y / st)
        if hsh(gx, gy, 63) > 0.80:
            sx = (gx + 0.25 + 0.5 * hsh(gx, gy, 64)) * st
            sy = (gy + 0.25 + 0.5 * hsh(gx, gy, 65)) * st
            tw = 0.5 + 0.5 * sin(TAU * (frame * 2 + hsh(gx, gy, 66)))
            ax, ay = abs(x - sx), abs(y - sy)
            b = tw * (exp(-(min(ax, ay) / 0.06) ** 2) * exp(-max(ax, ay) / 0.30))
            c = lerp(c, (0.45, 0.66, 1.0) if not warn else WHITE, clamp(b))
        c = lerp(c, (0.45, 0.62, 0.88) if not warn else (0.85, 0.22, 0.28), smooth(0.62, 0.30, depth))   # 흰 바탕에서 서는 푸른 테
        c = lerp(c, (0.30, 0.46, 0.76) if not warn else line, 0.95 * exp(-(depth / 0.20) ** 2))
        return c, 1.0


# ---- 파문 ----

class Ripple:
    """물빛 유리 한가운데에 물방울이 떨어져 반짝이고, 빛 고리가 테까지 퍼진다. 고리 둘이 엇갈려 쉬지 않는다."""
    ko = "파문"
    about = "맑은 물빛 커서 한가운데 물방울이 톡 떨어지면, 빛 고리가 둥글게 퍼져 테를 살짝 출렁이며 사라져요."
    LOOP = 2.0
    tip_body = True
    shadow = (0.02, 0.12, 0.30, 0.26)
    shadow_off, shadow_blur = (0.45, 0.95), 2.0
    ink = WHITE
    LINE = (0.02, 0.12, 0.36)
    WLINE = (0.40, 0.04, 0.10)
    PUSH = 0.16                # 고리가 테를 미는 깊이(칸)

    def extra(self, name, frame, layers, hot):
        self._hot = hot
        if getattr(self, "_for", None) != name:
            self._nowarp = True                                      # 무게중심은 안 민 모양으로 잰다
            self._c, self._rmax = centroid(solid(layers))
            self._nowarp = False
            self._for = name
        return layers

    def warp(self, x, y, frame):
        """고리가 지나는 자리의 테가 바깥으로 살짝 부푼다. 핫스팟 둘레는 안 민다."""
        if getattr(self, "_nowarp", True):
            return x, y
        cx, cy = self._c
        dx, dy = x - cx, y - cy
        rho = hypot(dx, dy)
        if rho < 0.5:
            return x, y
        hx, hy = self._hot
        k = self.PUSH * self.ring(rho, frame) * smooth(1.0, 4.0, hypot(x - hx, y - hy))
        return x - k * dx / rho, y - k * dy / rho

    def ring(self, rho, frame):
        """고리 세기 −1..1 (마루 +, 골 −)."""
        v = 0.0
        for j in (0.0, 0.5):
            p = (frame + j) % 1.0
            r = 0.2 + p * (self._rmax + 1.5)
            w = 0.50 + 0.55 * p
            a = (1 - p) ** 1.2 * smooth(0.0, 0.05, p)
            for lag, amp in ((0.0, 1.0), (2.2, 0.45)):              # 큰 고리 뒤로 작은 고리 하나
                u = (rho - r + lag * w) / w
                if abs(u) < 3:
                    v += a * amp * 2.33 * u * exp(-u * u)
        return v

    def sparkle(self, x, y, frame):
        cx, cy = self._c
        sp = 0.0
        for j in (0.0, 0.5):
            p = (frame + j) % 1.0
            e = smooth(0.0, 0.02, p) * smooth(0.20, 0.04, p)           # 떨어진 자리 반짝임
            if e > 0:
                ax, ay = abs(x - cx), abs(y - cy)
                rho = hypot(ax, ay)
                b = exp(-(rho / 0.8) ** 2) + 0.9 * exp(-(min(ax, ay) / 0.11) ** 2) * exp(-max(ax, ay) / 1.0)
                sp = max(sp, e * b)
        return sp

    def body(self, x, y, d, nx, ny, warn, frame):
        depth = -d
        if warn:
            top, bot, crest, trough = (1.0, 0.52, 0.52), (0.74, 0.10, 0.16), (1.0, 0.90, 0.88), (0.40, 0.02, 0.07)
        else:
            top, bot, crest, trough = (0.36, 0.70, 1.0), (0.10, 0.30, 0.78), (0.92, 0.99, 1.0), (0.03, 0.16, 0.45)
        cx, cy = self._c
        v = self.ring(hypot(x - cx, y - cy), frame)
        c = lerp(top, bot, clamp((y + 0.35 * x + 1.5 * v) / 24.0))      # 고리가 지나는 자리는 바탕도 살짝 밀린다
        c = lerp(c, crest, 0.90 * clamp(v))
        c = lerp(c, trough, 0.45 * clamp(-v))
        c = lerp(c, WHITE, clamp(self.sparkle(x, y, frame)))
        return glassy(c, depth, nx, ny, self.WLINE if warn else self.LINE, rim=0.30), 1.0

    def glow(self, x, y, d, warn, frame):
        """고리가 테에 닿으면 바깥으로 조금 번진다."""
        cx, cy = self._c
        v = self.ring(hypot(x - cx, y - cy), frame)
        return ((1.0, 0.60, 0.60) if warn else (0.50, 0.85, 1.0)), 0.40 * clamp(v) * exp(-d / 0.45)




register("wave", Wave())
register("rainfall", Rainfall())
register("bubbles", Bubbles())
register("snowfall", Snowfall())
register("ripple", Ripple())

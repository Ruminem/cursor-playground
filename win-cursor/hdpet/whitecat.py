# SPDX-License-Identifier: Apache-2.0
"""오드아이 흰냥(whitecatanim) 고화질 — 치비(머리가 몸만 한 통통 냥) · 스티커 채색(고른 먹선 1칸 + 셀 그늘 한 단).

픽셀 흰냥(지운 gen/whitecat.py)이 귀여운 까닭(넓적한 머리 · 낮고 넓게 벌어진 짝짝이 눈 · 눈 바로 밑 분홍 볼 · 작은 분홍 코 ·
새하얀 납작한 털)을 HD 로 옮겼다. 칸마다 하는 짓도 픽셀 판 그대로다(우유 핥기 · 우유 물음표 · 발바닥 하이파이브 · 기지개).
화살표는 크림 화살표 빗변 뒤에서 고개를 내밀고 앞발 둘을 빗변에 건 빼꼼이다 — 몸에 얼굴을 넣은 판(공룡 등가시로 읽힘)과
귀 끝이 곧 화살 끝인 판(어디를 가리키는지 흐림)은 시안에서 접었다(2026-10-11).
좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 장면은 NF 장으로 나뉘어 있다(k = round(fr × NF) % NF).
"""
import math

from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

from . import register

sin, cos, hypot, floor, pi = math.sin, math.cos, math.hypot, math.floor, math.pi

def hx(s):
    return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))


# 픽셀 판 팔레트(지운 gen/whitecat.py) 그대로
OUT, EYE = hx("3c4052"), hx("252836")
WHITE, SHADE = hx("fcfdff"), hx("dde3ee")
BLUE, BLUE_D, BLUE_L = hx("4a9bf0"), hx("2a68c4"), hx("8cc4ff")
GOLD, GOLD_D, GOLD_L = hx("f0bb2a"), hx("bf8410"), hx("ffe07a")
PINK, NOSE = hx("f4a0b0"), hx("e27d90")
CHEEK = hx("f7a3b5")
RIM = hx("e6e8f0")
MILK, MILK_D = hx("ffffff"), hx("dbe8f5")
DISH, DISH_D, DISH_L = hx("6f9fd8"), hx("4b77b4"), hx("a8c8ee")
SUN, SUN_L = hx("ffd24a"), hx("fff0a8")
CHALK, CHALK_L, CHALK_D = hx("8ec4f4"), hx("c8e2fa"), hx("5d97d2")
SHIRT, SHIRT_D, SKIN, HAIR = hx("e88f7a"), hx("c46d5a"), hx("f7d7bc"), hx("5a4034")
SIGN, SIGN_D, SIGN_L = hx("d64541"), hx("9e2b28"), hx("ef7a72")
CREAM, CREAM_D = hx("fff6e8"), hx("f1e2c8")
HI = (1.0, 1.0, 1.0)

NF, LOOP = 12, 1.0
LINE = 1.0                         # 먹선 굵기(칸) — 32 로 줄여도 1px
SH = (1.15, 1.15)                  # 그늘 띠: 모양을 왼쪽 위로 민 것 밖(= 오른쪽 아래 가장자리 1칸)

# 픽셀 판 핫스팟(art 칸) 그대로 — 적용한 사람의 손에 익은 자리
HOT = {"arrow": (1, 1), "busy": (1, 1), "cross": (15, 15), "hand": (7, 1), "help": (1, 1), "ibeam": (7, 14),
       "move": (15, 15), "nesw": (13, 13), "no": (14, 14), "ns": (5, 15), "nwse": (13, 13), "pen": (1, 22),
       "person": (1, 1), "pin": (1, 1), "up": (6, 1), "wait": (10, 14), "we": (15, 8)}



# ---- 거리함수 ----

def ell(cx, cy, rx, ry):
    def f(x, y):
        dx, dy = (x - cx) / rx, (y - cy) / ry
        g = hypot(dx, dy) or 1e-9
        gl = hypot(dx / (rx * g), dy / (ry * g)) or 1e-9
        return (g - 1) / gl
    return f


def oell(cx, cy, ra, rb, ang):
    return turn(ell(cx, cy, ra, rb), ang, cx, cy)


def inter(f, g):
    return lambda x, y: max(f(x, y), g(x, y))


def clip_y(f, y0):
    return lambda x, y: max(f(x, y), y - y0)


def rpoly(pts, r):
    """둥근 모서리 다각형 — 꼭짓점을 가운데로 r 만큼 당긴 뒤 r 키움(크기는 거의 그대로)"""
    cx, cy = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    q = []
    for x, y in pts:
        d = hypot(x - cx, y - cy) or 1.0
        k = max(0.0, 1 - 1.6 * r / d)
        q.append((cx + (x - cx) * k, cy + (y - cy) * k))
    return grow(poly(q), r)


def chain(pts, r0, r1=None):
    r1 = r0 if r1 is None else r1
    n = len(pts) - 1
    segs = []
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        ra, rb = r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n
        segs.append(taper(a[0], a[1], ra, b[0], b[1], rb))
    return union(*segs)


def taper(ax, ay, ra, bx, by, rb):
    """끝마다 반지름이 다른 캡슐(근사: 선분 위 가장 가까운 자리의 반지름)"""
    ex, ey = bx - ax, by - ay
    ee = ex * ex + ey * ey or 1e-9

    def f(x, y):
        wx, wy = x - ax, y - ay
        t = clamp((wx * ex + wy * ey) / ee)
        return hypot(wx - ex * t, wy - ey * t) - (ra + (rb - ra) * t)
    return f


class Frame:
    """캐논(고양이 제 좌표, 머리 가운데 (0, 0), 아래가 +v) ↔ art 좌표. ang 은 화면 시계 방향"""

    def __init__(self, ox=0.0, oy=0.0, s=1.0, ang=0.0):
        self.ox, self.oy, self.s, self.c, self.sn = ox, oy, s, cos(ang), sin(ang)

    def loc(self, x, y):
        dx, dy = (x - self.ox) / self.s, (y - self.oy) / self.s
        return dx * self.c + dy * self.sn, -dx * self.sn + dy * self.c

    def w(self, u, v):
        return self.ox + (u * self.c - v * self.sn) * self.s, self.oy + (u * self.sn + v * self.c) * self.s

    def f(self, g):
        s, loc = self.s, self.loc
        return lambda x, y: s * g(*loc(x, y))


# ---- 칠하기: 스티커 ----

def layer(f, paint, glow=False, shadow=False, alpha=1.0, fade=None):
    d = dict(f=f, paint=paint, noglow=not glow, shadow=shadow, alpha=alpha)
    if fade:
        d["fade"] = fade
    return d


def base(*fs):
    """스티커 바닥: 조각들의 합집합을 먹색으로 깔고 밝은 바깥 테 · 옅은 그림자를 맡는다"""
    u = fs[0] if len(fs) == 1 else union(*fs)
    return layer(u, lambda x, y, e, nx, ny, fr: (OUT, 1.0), glow=True, shadow=True)


def part(f, col=WHITE, shade=SHADE, line=LINE, sh=1.0, ink=OUT):
    """한 조각: 바탕색 + 오른쪽 아래 그늘 띠 한 칸 + 먹선. col 은 색 또는 (x, y) → 색"""
    def paint(x, y, e, nx, ny, fr):
        c = col(x, y) if callable(col) else col
        if sh:
            c = lerp(c, shade, sh * smooth(-0.15, 0.15, f(x + SH[0], y + SH[1])))
        if line:
            c = lerp(c, ink, smooth(line + 0.12, line - 0.12, -e))
        return c, 1.0
    return layer(f, paint)


def flat(f, col, a=1.0, line=0.0, ink=OUT):
    def paint(x, y, e, nx, ny, fr):
        c = col(x, y) if callable(col) else col
        if line:
            c = lerp(c, ink, smooth(line + 0.1, line - 0.1, -e))
        return c, a
    return layer(f, paint)


def soft(f, col, a=0.75):
    """가장자리가 번진 색 얼룩(볼터치)"""
    return layer(f, lambda x, y, e, nx, ny, fr: (col, a * smooth(0.0, -0.5, e)))


def sticker(*pieces):
    """[(f, col, opts)…] → 바닥 하나 + 조각마다 part. 앞의 것이 아래"""
    out = [base(*[p[0] for p in pieces])]
    for p in pieces:
        out.append(part(p[0], p[1], **(p[2] if len(p) > 2 else {})))
    return out


# ---- 얼굴 ----

def eye(cx, cy, rx, iris, deep, light, look=(0.0, 0.0)):
    """짝짝이 눈 하나 — 홍채가 눈 대부분, 아래쪽에 짙은 동공, 왼쪽 위 큰 반짝 · 오른쪽 아래 작은 반짝.
    원본 2×2 눈(반짝 · 홍채 · 홍채 · 동공)을 키운 꼴이라 32 에서도 색이 2px 남는다"""
    ry = rx * 1.16
    px, py = cx + look[0] * rx * 0.22, cy + ry * 0.2 + look[1] * ry * 0.12
    prx, pry = rx * 0.34, ry * 0.42
    h1 = (cx - rx * 0.36, cy - ry * 0.38, rx * 0.36)
    h2 = (cx + rx * 0.4, cy + ry * 0.42, rx * 0.15)

    def paint(x, y, e, nx, ny, fr):
        c = lerp(light, iris, smooth(cy - ry * 0.9, cy - ry * 0.1, y))
        c = lerp(c, deep, 0.45 * smooth(cy + ry * 0.3, cy + ry * 1.0, y))
        c = lerp(c, EYE, smooth(0.12, -0.12, hypot((x - px) / prx, (y - py) / pry) - 1))
        c = lerp(c, HI, smooth(h1[2] + 0.1, h1[2] - 0.1, hypot(x - h1[0], y - h1[1])))
        c = lerp(c, HI, 0.9 * smooth(h2[2] + 0.08, h2[2] - 0.08, hypot(x - h2[0], y - h2[1])))
        return lerp(c, deep, smooth(0.26, 0.1, -e)), 1.0
    return layer(ell(cx, cy, rx, ry), paint)


def shut(cx, cy, rx, kind="blink"):
    """감은 눈: blink 는 아래로 휜 ∪(졸린 웃음), happy 는 ^"""
    w = max(0.3, 0.2 * rx)
    if kind == "happy":
        return flat(arc(cx, cy + rx * 0.55, rx * 0.95, w, pi * 1.2, pi * 0.6), EYE)
    return flat(arc(cx, cy - rx * 0.5, rx * 0.95, w, pi * 0.18, pi * 0.64), EYE)


def face(F, mood="open", look=(0.0, 0.0), turn_=0.0, mouth="w", tongue=0.0):
    """보는 쪽 왼눈 파랑 · 오른눈 금색(원본). 눈은 머리 가운데 높이, 넓게 벌어지고 바로 밑에 볼, 사이 아래에 작은 코"""
    s = F.s
    out = []
    er = max(1.66 * s, 1.32)
    for sg in (-1, 1):                                         # 볼 먼저(눈 아래 깔림)
        bx, by = F.w(turn_ + sg * 4.5, 2.7)
        rx = max(1.45 * s, 0.95)
        out.append(soft(ell(bx, by, rx, rx * 0.62), CHEEK, 0.85))
    for sg in (-1, 1):
        ex, ey = F.w(turn_ + sg * 3.15, 0.25)
        closed = mood in ("blink", "happy") or (mood == "wink" and sg > 0)
        if closed:
            out.append(shut(ex, ey, er, "happy" if mood in ("happy", "wink") else "blink"))
        else:
            iris = (BLUE, BLUE_D, BLUE_L) if sg < 0 else (GOLD, GOLD_D, GOLD_L)
            out.append(eye(ex, ey, er, *iris, look=look))
    nx, ny = F.w(turn_, 2.05)
    hw = max(0.78 * s, 0.6)
    nose = rpoly([(nx - hw, ny - hw * 0.45), (nx + hw, ny - hw * 0.45), (nx, ny + hw * 0.6)], hw * 0.3)
    if tongue > 0:                                             # 혀 날름(코 아래로 분홍 혀)
        tl = tongue * max(2.2 * s, 1.6)
        tw = max(0.9 * s, 0.75)
        tg = smin(0.3, ell(nx, ny + hw * 0.9 + tl * 0.55, tw, tl * 0.55 + 0.2), circle(nx, ny + hw * 0.9 + tl, tw))
        out.append(flat(tg, lambda x, y: lerp(PINK, NOSE, smooth(nx - 0.05, nx + 0.05, x) * 0.0 + 0.0), line=0.28, ink=NOSE))
        out.append(flat(capsule(nx, ny + hw * 0.9 + tl * 0.3, nx, ny + hw * 0.9 + tl * 0.85, 0.12), NOSE, 0.7))
    if mouth == "w" and s >= 0.5:                              # ω 입(작게)
        m = max(0.62 * s, 0.5)
        w = max(0.17 * s, 0.16)
        for sg in (-1, 1):
            out.append(flat(arc(nx + sg * m, ny + hw * 0.35, m, w, pi * 0.08, pi * 0.84), OUT, 0.95))
    out.append(flat(nose, lambda x, y: lerp(hx("f6b3c0"), NOSE, smooth(ny - hw * 0.4, ny + hw * 0.2, y))))
    return out


def blink_of(fr, at=0.75):
    """한 바퀴에 한 번, 한 장만 감는다"""
    k = round(fr * NF) % NF
    return k == round(at * NF) % NF


# ---- 치비 흰냥 (캐논: 머리 가운데 (0, 0), 아래가 +v) ----
#   머리 넓이 15 · 높이 11.5(귀 끝까지 15) · 몸은 머리보다 작은 콩 · 앞발 둘 · 말린 꼬리. 다 합쳐 22칸

def head_f(F, squish=0.0):
    return F.f(smin(1.6, ell(0, -0.4, 6.9, 5.6 - squish), ell(0, 1.3 + squish * 0.3, 7.6, 4.3)))


def ear_pts(sg, tilt=0.0):
    return [(sg * 6.7, -1.0), (sg * (6.1 + tilt), -8.7), (sg * 1.3, -4.9)]


def cat(F, mood="open", look=(0.0, 0.0), turn_=0.0, sway=0.0, bob=0.0, body=True, paws=True, tail=True,
        arms=(), tongue=0.0, ear_tilt=(0.0, 0.0), tail_pts=None, extra_under=(), face_on=True, mouth="w"):
    """앉은 치비 흰냥 → 레이어 목록. arms = [(어깨 (u, v), 손 (u, v), 젤리 보임)] — 머리 위에 그린다.
    bob 은 몸이 살짝 눌리는 정도(0–1). 색은 흰 털 한 색 + 오른쪽 아래 그늘 한 칸"""
    s = F.s
    rt = max(1.8, 1.5 * s) / s                                 # 꼬리 반지름(캐논) — 먹선 안에 흰 털이 남게
    pieces = []
    if tail:
        tp = tail_pts or [(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.4 + sway, 3.9), (8.2 + 1.4 * sway, 2.0)]
        pieces.append((F.f(chain(tp, rt * 1.05, rt * 0.95)), WHITE))
    if body:
        pieces.append((F.f(ell(0, 7.7 + bob * 0.3, 5.4 + bob * 0.25, 4.4 - bob * 0.3)), WHITE))
    if paws:
        for sg in (-1, 1):
            pieces.append((F.f(ell(sg * 2.45, 11.35, 1.95, 1.4)), WHITE))
    pieces += list(extra_under)
    ears = [F.f(rpoly(ear_pts(sg, ear_tilt[(sg + 1) // 2]), 0.95)) for sg in (-1, 1)]
    H = head_f(F, bob * 0.35)
    arm_fs = []
    for sh_, hand, jelly in arms:
        ra = max(2.7, 2.1 / s)                                 # 팔 반지름(캐논) — 먹선 안에 흰 털이 1칸 넘게
        a = F.f(taper(sh_[0], sh_[1], ra * 1.12, hand[0], hand[1], ra * 0.95))
        p = F.f(ell(hand[0], hand[1], ra * 1.12, ra * 1.04))
        arm_fs.append((a, p, hand, jelly))
    allf = [p[0] for p in pieces] + ears + [H] + [g for a, p, _, _ in arm_fs for g in (a, p)]
    out = [base(*allf)]
    for p in pieces:
        out.append(part(p[0], p[1]))
    for sg, E in zip((-1, 1), ears):
        out.append(part(E, WHITE))
        pts = ear_pts(sg, ear_tilt[(sg + 1) // 2])
        cx, cy = sum(p[0] for p in pts) / 3, sum(p[1] for p in pts) / 3 + 0.5
        inner = F.f(rpoly([(cx + (x - cx) * 0.5, cy + (y - cy) * 0.5) for x, y in pts], 0.5))
        out.append(flat(inner, PINK))
    out.append(part(H, WHITE))
    if face_on:
        out += face(F, mood, look, turn_, mouth, tongue)
    for a, p, hand, jelly in arm_fs:
        out.append(part(a, WHITE))
        out.append(part(p, WHITE))
        if jelly:
            out += jellies(F, hand)
    return out


def jellies(F, c, spread=0.0):
    """발바닥 젤리: 큰 젤리 하나 + 발가락 셋"""
    out = []
    u, v = c
    big = F.f(ell(u, v + 0.55, 0.95, 0.75))
    out.append(flat(big, PINK))
    for dx, dy in ((-1.15 - spread, -0.55), (0.0, -1.05 - spread), (1.15 + spread, -0.55)):
        out.append(flat(F.f(circle(u + dx, v + dy, 0.48)), PINK))
    return out


# ---- 소품 ----

ARROW = [(0.0, 0.0), (0.0, 19.0), (4.4, 14.8), (7.6, 21.8), (10.6, 20.4), (7.4, 13.6), (13.4, 13.6)]   # 끝 (0, 0)


def arrow_f(tip, sc, r=0.35):
    pts = [(tip[0] + sc * x, tip[1] + sc * y) for x, y in ARROW]
    return rpoly(pts, r)


def small_arrow(tip=(1.62, 1.62), sc=0.52):
    f = arrow_f(tip, sc, 0.3)
    return [base(f), part(f, WHITE, sh=0.0)]


def chevron(cx, cy, dx, dy, L=2.4, a=1.0):
    """(dx, dy) 쪽을 가리키는 분홍 화살촉 — 꼭짓점이 (cx, cy)"""
    n = hypot(dx, dy)
    dx, dy = dx / n, dy / n
    px, py = -dy, dx
    f = union(*[capsule(cx, cy, cx - dx * L + s * px * L, cy - dy * L + s * py * L, 0.72) for s in (-1, 1)])
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(PINK, hx("d8728a"), smooth(0.36, 0.2, -e)), 1.0), alpha=a)]


def sparkle(cx, cy, L=2.4, w=0.75):
    f = union(poly([(cx - L, cy), (cx, cy - w), (cx + L, cy), (cx, cy + w)]),
              poly([(cx, cy - L), (cx + w, cy), (cx, cy + L), (cx - w, cy)]))
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(lerp(SUN_L, SUN, smooth(0.3, 1.4, hypot(x - cx, y - cy))),
                                                       hx("d9a21c"), smooth(0.3, 0.12, -e)), 1.0))]


def dish(cx, cy, rx, ry=None, ripple=None, milk=True):
    """앞에서 본 우유 접시: 위가 우유 면, 아래가 파란 그릇. ripple(0–1)은 우유 물결 고리"""
    ry = ry or rx * 0.32
    top = ell(cx, cy, rx, ry)
    bowl = smin(0.5, top, rbox(cx, cy + ry * 0.9, rx * 0.86, ry * 0.9, 0.2), ell(cx, cy + ry * 1.75, rx * 0.66, ry * 0.7))
    surf = ell(cx, cy + 0.05, rx - 1.15, ry - 0.75)

    def bcol(x, y):
        c = lerp(DISH_L, DISH, smooth(cx - rx * 0.7, cx - rx * 0.2, x))
        return lerp(c, DISH_D, smooth(cy + ry * 1.3, cy + ry * 2.1, y))

    def mcol(x, y):
        c = lerp(MILK, MILK_D, smooth(cy - 0.2, cy + ry * 0.6, y))
        if ripple is not None:
            d = hypot((x - cx) / (rx - 1.1), (y - cy) / (ry - 0.7))
            c = lerp(c, MILK_D, smooth(0.16, 0.05, abs(d - ripple)))
        return c
    out = [base(bowl), part(bowl, bcol, shade=DISH_D, sh=0.6)]
    if milk:
        out.append(flat(surf, mcol, line=0.35, ink=DISH_D))
    return out


def drop(x, y, r=1.3, h=1.6):
    """물방울 — 꼭지가 위"""
    return smin(0.35, circle(x, y + 0.6, r), poly([(x, y - h), (x - r * 0.8, y + 0.5), (x + r * 0.8, y + 0.5)]))


def milk_piece(f, line=0.85):
    return [base(f), part(f, lambda x, y: MILK, shade=MILK_D, line=line, ink=DISH_D)]


def paw_print(x, y, a):
    f = union(ell(x, y + 0.6, 1.15, 0.95), circle(x - 1.35, y - 0.75, 0.55), circle(x, y - 1.35, 0.55),
              circle(x + 1.35, y - 0.75, 0.55))
    return layer(f, lambda px, py, e, nx, ny, fr: (lerp(PINK, hx("d8728a"), smooth(0.3, 0.15, -e)), 1.0), alpha=a)


# ---- 화살표: 빼꼼 (핫스팟 (1, 1)) ----

TIP = (1.62, 1.62)                 # 끝이 (1, 1) 칸에 먹선으로 닿게 · 판 위 끝과는 1.6칸 떨어지게


def peek(fr):
    """B 빼꼼: 크림 화살표 빗변 뒤에서 치비 흰냥이 고개를 쏙 — 두 앞발이 빗변을 잡는다(원본 구성 그대로, 머리만 크게)"""
    ph = TAU * fr
    sc = 1.24
    P = [(TIP[0] + sc * x, TIP[1] + sc * y) for x, y in ARROW]
    arw = rpoly(P, 0.55)
    lift = 0.5 * (1 - cos(ph)) / 2
    F = Frame(19.6, 10.4 - lift, 0.8)
    out = cat(F, "blink" if blink_of(fr) else "open",
              look=(-0.6, 0.25), sway=0.6 * sin(ph), body=True, paws=False,
              tail_pts=[(3.0, 9.6), (7.4, 10.4), (9.6, 7.4), (9.4 + 0.6 * sin(ph), 3.6), (8.0 + 0.9 * sin(ph), 1.6)])
    out += [base(arw), part(arw, lambda x, y: lerp(CREAM, CREAM_D, smooth(6, 30, x * 0.4 + y)), sh=0.0)]
    # 빗변(끝 → 오른쪽 어깨) 위 앞발 둘 — 빗변을 따라 나란히, 반쯤 빗변 바깥으로
    ex, ey = P[6][0] - P[0][0], P[6][1] - P[0][1]
    el = hypot(ex, ey)
    ux, uy = ex / el, ey / el
    nx, ny = uy, -ux                                    # 빗변 바깥(오른쪽 위)
    ang = math.atan2(uy, ux)
    for t in (15.6, 18.9):
        cx, cy = P[0][0] + ux * t + nx * 0.55, P[0][1] + uy * t + ny * 0.55
        p = oell(cx, cy, 1.75, 1.4, ang)
        out += [base(p), part(p, WHITE, sh=0.0)]
        for d in (-0.6, 0.6):                          # 발가락 금 둘 — 빗변 쪽으로 짧게
            bx, by = cx + ux * d, cy + uy * d
            out.append(flat(capsule(bx - nx * 0.2, by - ny * 0.2, bx - nx * 1.0, by - ny * 1.0, 0.13), OUT, 0.8))
    return out




# ---- 동반(작은 화살표 + 작은 흰냥) ----

def buddy(fr, mood=None):
    ph = TAU * fr
    m = mood or ("blink" if blink_of(fr, 0.25) else "open")
    F = Frame(13.6, 7.7, 0.58)
    return small_arrow() + cat(F, m, look=(-0.4, 0.0), sway=0.5 * sin(ph), bob=0.4 * (1 - cos(ph)) / 2)


# ---- 칸마다 장면 (art 좌표) ----

def sc_arrow(fr):
    return peek(fr)


def sc_help(fr):
    """작은 화살표 흰냥 + 엎지른 우유로 그린 물음표, 점은 똑 떨어지는 우유 방울"""
    out = buddy(fr)
    q = union(arc(22.6, 15.6, 3.7, 1.25, pi * 0.95, pi * 1.42), capsule(25.4, 17.6, 22.6, 20.2, 1.25), capsule(22.6, 20.2, 22.6, 22.2, 1.25))
    out += milk_piece(q)
    k = round(fr * NF) % NF
    t = k % 6
    if t < 4:
        out += milk_piece(drop(22.6, 25.0 + t * 0.55, 1.35, 1.6), 0.7)
    else:
        out += milk_piece(ell(22.6, 27.8, 2.9 if t == 4 else 2.3, 1.1), 0.7)
    return out


def sc_busy(fr):
    """작은 화살표 흰냥 + 우유 접시 둘레를 도는 분홍 발자국 여덟"""
    out = buddy(fr)
    cx, cy = 22.5, 22.5
    k = round(fr * NF) % NF
    head = k * 8 / NF
    for i in range(8):
        a = TAU * i / 8 - pi / 2
        lag = (head - i) % 8
        out.append(paw_print(cx + 6.9 * cos(a), cy + 6.6 * sin(a), 1.0 if lag < 1.5 else 0.6 if lag < 3 else 0.28))
    out += dish(cx, cy - 0.6, 4.4, 1.6, ripple=(k % 4) / 4 + 0.15)
    return out


def sc_pin(fr):
    """작은 화살표 흰냥 + 흰 동그라미 속 금방울이 든 빨간 핀이 통통"""
    out = buddy(fr)
    hop = abs(sin(pi * fr))
    cx, cy = 22.6, 15.2 - 2.6 * hop
    out.insert(0, layer(ell(22.8, 29.0, 3.4 - 0.8 * hop, 0.75), lambda *a: (OUT, 0.2)))
    f = smin(1.0, circle(cx, cy, 5.6), poly([(cx - 4.6, cy + 2.6), (cx + 4.6, cy + 2.6), (cx, cy + 11.4)]))
    out += [base(f), part(f, lambda x, y: lerp(SIGN_L, SIGN, smooth(cy - 5, cy - 1.5, y + 0.6 * (x - cx))), shade=SIGN_D, ink=SIGN_D)]
    hole = circle(cx, cy, 3.6)
    out.append(flat(hole, WHITE, line=0.5, ink=SIGN_D))
    tilt = 0.35 * sin(2 * ph_of(fr))
    T = lambda g: turn(g, tilt, cx, cy - 2.2)             # 방울은 고리를 축으로 달랑
    loop_ = T(ring(cx, cy - 2.25, 0.55, 0.22))
    bell = T(smin(0.5, circle(cx, cy - 0.1, 1.85), rbox(cx, cy + 1.25, 2.35, 0.55, 0.45)))
    out.append(flat(loop_, GOLD_D))
    out.append(flat(bell, lambda x, y: lerp(GOLD_L, GOLD, smooth(cy - 1.2, cy + 0.9, y)), line=0.4, ink=GOLD_D))
    out.append(flat(T(capsule(cx - 2.0, cy + 0.65, cx + 2.0, cy + 0.65, 0.16)), GOLD_D, 0.8))
    out.append(flat(T(circle(cx, cy + 1.75, 0.5)), GOLD_D))
    return out


def ph_of(fr):
    return TAU * fr


def sc_person(fr):
    """작은 화살표 흰냥 + 머리에 흰냥 식빵을 얹은 사람(방긋)"""
    ph = TAU * fr
    out = buddy(fr)
    cx, cy = 22.6, 22.4
    body = clip_y(ell(cx, cy + 8.6, 7.2, 5.4), 30.4)
    head = circle(cx, cy, 4.4)
    hair = smin(0.6, ell(cx, cy - 2.4, 4.8, 2.6), ell(cx - 4.0, cy - 0.6, 1.2, 2.0), ell(cx + 4.0, cy - 0.6, 1.2, 2.0))
    out += [base(body, head, hair), part(body, SHIRT, shade=SHIRT_D), part(head, SKIN, shade=hx("e8bfa0")),
            part(hair, HAIR, shade=hx("3e2b22"))]
    for sg in (-1, 1):
        out.append(flat(ell(cx + sg * 1.7, cy + 0.4, 0.55, 0.75), EYE))
        out.append(soft(ell(cx + sg * 2.8, cy + 1.9, 0.9, 0.55), CHEEK, 0.8))
    out.append(flat(arc(cx, cy + 1.6, 0.9, 0.22, pi * 0.15, pi * 0.7), SHIRT_D))
    # 머리 위 식빵 흰냥(작게, 얼굴만 또렷이)
    F = Frame(cx - 1.0, cy - 7.2, 0.4)
    loaf = F.f(smin(1.0, ell(2.5, 3.4, 9.0, 4.0), ell(2.5, 5.6, 9.6, 2.2)))
    sw = sin(ph)
    tl = F.f(chain([(10.0, 5.6), (12.6, 7.6), (12.6 + 1.2 * sw, 11.0)], 3.6, 3.4))
    out += [base(loaf, tl), part(tl, WHITE), part(loaf, WHITE)]
    out += cat(F, "happy" if round(fr * NF) % 6 < 2 else "open", body=False, paws=False, tail=False, mouth="")
    return out


def sc_wait(fr):
    """우유 접시에 고개를 숙이고 할짝할짝 — 혀 날름(장 1–2, 7–8) · 꼬리 끝 까딱"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    lap = k % 6 in (1, 2)
    F = Frame(10.5, 12.6 + (0.5 if lap else 0.0), 0.92)
    out = cat(F, "blink" if lap or k == 9 else "open", sway=0.6 * sin(2 * ph), tongue=1.0 if lap else 0.0, paws=False,
              tail_pts=[(4.2, 9.4), (8.8, 9.2), (10.6, 6.0), (10.2 + 0.6 * sin(2 * ph), 2.6), (9.0 + 0.9 * sin(2 * ph), 0.8)])
    out += dish(10.9, 22.2, 8.6, 2.4, ripple=((k % 6) / 6 + 0.15) if lap or k % 6 >= 1 else None)
    for sg in (-1, 1):                                    # 접시 가장자리에 얹은 앞발
        p = ell(10.5 + sg * 6.2, 21.4, 1.9, 1.35)
        out += [base(p), part(p, WHITE)]
    return out


def sc_cross(fr):
    """앞모습 얼굴 — 볼 수염이 가로 조준선, 위아래 줄이 세로선. 분홍 코가 핫스팟. 턱 밑으로 우유 방울 또르르"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    C = 15.5
    s = 1.04
    F = Frame(C, C - 2.05 * s, s)
    lines = union(capsule(2.6, C, 5.0, C, 0.5), capsule(26.0, C, 28.4, C, 0.5),     # 끝은 판 끝에서 2칸 안쪽(테가 안 잘리게)
                  capsule(C, 2.6, C, 3.0, 0.5), capsule(C, 23.6, C, 28.4, 0.5))
    out = [base(lines), flat(lines, OUT)]
    tw = 0.5 * sin(2 * ph)
    for sg in (-1, 1):                                    # 수염 — 조준선으로 이어진다
        for j in (-1, 1):
            out.append(flat(capsule(C + sg * 7.4, C + j * 0.55, C + sg * 10.6, C + j * (1.0 + 0.4 * tw), 0.22), OUT))
    out += cat(F, "wink" if k in (8, 9) else "open", body=False, paws=False, tail=False)
    y = 23.6 + (k % 6) * 1.0
    out += milk_piece(drop(C + 2.4, y, 1.15, 1.4), 0.7)
    return out


def sc_ibeam(fr):
    """옆으로 누운 우유갑(위 가로획) → 우유 줄기(세로획) → 접시(아래 가로획) = I. 오른쪽 흰냥이 혀로 할짝"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    X = 7.5
    carton = rbox(X, 3.9, 5.0, 1.8, 0.7)
    stream = rbox(X, 15.0, 1.7, 10.4, 0.6)
    out = [base(carton, stream)]
    def flow(x, y):                                       # 줄기 속 옅은 띠가 아래로 흐른다
        m = (y - 8.0 * k / NF) % 4.0
        return lerp(MILK, MILK_D, 0.55 * smooth(0.55, 0.15, min(m, 4.0 - m)))
    out.append(part(stream, flow, shade=MILK_D, ink=DISH_D, line=0.8))
    out.append(part(carton, lambda x, y: lerp(WHITE, DISH, smooth(0.55, 0.35, abs(y - 3.6))), shade=SHADE, ink=DISH_D, line=0.85))
    out += dish(X, 25.2, 5.3, 1.6)
    lick = (0.0, 0.7, 1.0, 1.0, 0.7, 0.0)[k % 6]
    F = Frame(17.6, 13.2, 0.64)
    out += cat(F, "blink" if lick > 0 else "open", look=(-1.0, 0.0), turn_=-1.2, sway=0.5 * sin(ph),
               tail_pts=[(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.4 + 0.5 * sin(ph), 3.9), (8.2 + 0.7 * sin(ph), 2.0)])
    if lick:                                              # 혀가 줄기까지
        nx, ny = F.w(-1.2, 2.05)
        y0 = ny + 1.0
        tip = nx - (nx - (X + 1.0)) * lick
        f = smin(0.35, capsule(tip + 0.5, y0, nx - 0.2, y0, 0.62), circle(tip + 0.5, y0 + 0.3, 0.7))
        out.append(flat(f, PINK, line=0.22, ink=NOSE))
    return out


def sc_pen(fr):
    """파란 분필을 두 앞발로 쥐고 바닥에 쓴다 — 분필 끝(왼쪽 아래)이 핫스팟, 파랑 · 금색(눈 색) 줄이 길어진다"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    tip = (1.55, 22.5)
    ang = -0.68 + 0.05 * sin(2 * ph)
    ux, uy = cos(ang), sin(ang)
    L = 13.0
    end = (tip[0] + ux * L, tip[1] + uy * L)
    out = []
    n = 2 + k                                            # 분필 줄
    for i in range(n):
        x0 = 3.4 + 1.9 * i
        y0 = 25.2 + 0.5 * sin(x0 * 0.8)
        col = CHALK_D if (i // 2) % 2 == 0 else GOLD
        out.append(flat(capsule(x0, y0, x0 + 1.5, 25.2 + 0.5 * sin((x0 + 1.5) * 0.8), 0.55), col))
    F = Frame(20.2, 9.6, 0.74)
    hold = [F.loc(*(tip[0] + ux * 9.2, tip[1] + uy * 9.2)), F.loc(*(tip[0] + ux * 11.6, tip[1] + uy * 11.6))]
    out += cat(F, "wink" if k == 6 else "open", look=(-0.8, 0.6), turn_=-0.9, sway=0.5 * sin(ph))
    ch = smin(0.4, poly([tip, (tip[0] + ux * 2.9 - uy * 1.75, tip[1] + uy * 2.9 + ux * 1.75),
                         (tip[0] + ux * 2.9 + uy * 1.75, tip[1] + uy * 2.9 - ux * 1.75)]),
              capsule(tip[0] + ux * 2.6, tip[1] + uy * 2.6, end[0], end[1], 1.75))

    def ccol(x, y):
        t = (x - tip[0]) * ux + (y - tip[1]) * uy
        c = lerp(CHALK_L, CHALK, smooth(-0.6, 0.6, (x - tip[0]) * -uy + (y - tip[1]) * ux))
        return CHALK_D if t < 2.0 else c
    out += [base(ch), part(ch, ccol, shade=CHALK_D, ink=hx("2f5f96"), line=0.85)]
    for u, v in hold:                                   # 분필을 감싼 앞발
        p = F.f(ell(u, v, 2.6, 2.4))
        out += [base(p), part(p, WHITE)]
    return out


def sc_no(fr):
    """빨간 금지 표지 안에서 우유 접시를 앞발로 쓱 밀어내며 고개 도리도리(눈 꾹)"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    C = 14.5
    push = 1.6 * sin(pi * fr)
    turn_ = 1.1 * sin(2 * ph)
    F = Frame(C + 2.6, C - 1.6, 0.6)
    out = cat(F, "happy", turn_=turn_, sway=0.4 * sin(ph), mouth="",
              arms=[((-3.4, 6.2), (-9.6 - push / 0.6, 9.4), False)])
    out += dish(C - 4.4 - push, C + 6.0, 4.0, 1.4, ripple=0.6 if push > 1.0 else None)
    if push > 1.2:
        out += milk_piece(circle(C - 9.2 - push, C + 3.4, 0.7), 0.4)
        out += milk_piece(circle(C - 7.6 - push, C + 2.2, 0.55), 0.35)
    R = 12.5
    sg = union(ring(C, C, R - 1.25, 1.25), capsule(C - 7.7, C - 7.7, C + 7.7, C + 7.7, 1.35))
    out += [base(sg), part(sg, lambda x, y: lerp(SIGN_L, SIGN, smooth(C - 10, C - 4, y + 0.5 * x - 0.5 * C)), shade=SIGN_D, ink=SIGN_D, line=0.8)]
    return out


def stretch(fr, C, ang, length, s=0.6, chev=None, head=(0.0, -1.0), hoff=2.2, dangle=False):
    """기지개(쭉 늘어난 냥): 굵은 몸이 축(ang)을 따라 — 앞 끝에 똑바른 얼굴, 그 앞으로 쭉 뻗은 앞발 둘,
    뒤 끝에 뒷발 둘과 말린 꼬리. head 는 머리를 몸 축에서 얼마나(hoff) 어느 쪽으로 올릴지(화면 방향)"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    e = length * (1 + 0.05 * sin(ph))
    ux, uy = cos(ang), sin(ang)
    cx, cy = C
    r = 3.3 * s / 0.6
    a0 = (cx - ux * e / 2, cy - uy * e / 2)              # 앞 끝(머리 쪽)
    a1 = (cx + ux * e / 2, cy + uy * e / 2)              # 뒤 끝
    # 발이 놓일 쪽 = 머리 반대쪽
    px, py = (-head[0], -head[1]) if not dangle else (-uy, ux)
    bodyf = taper(a0[0], a0[1], r, a1[0], a1[1], r * 0.92)
    pr = 1.85 * s / 0.6
    reach = 0.6 * (1 + sin(ph)) / 2                       # 앞발이 쭉쭉 뻗었다 들어온다
    if dangle:                                           # 들린 냥(롱캣): 앞발이 몸 위쪽 양옆으로 축 늘어진다
        fronts = [oell(a0[0] + ux * (r * 1.6 + reach * 0.5) + px * j * (r + 0.2), a0[1] + uy * (r * 1.6 + reach * 0.5) + py * j * (r + 0.2),
                       pr * 1.1, pr * 0.85, ang) for j in (-1, 1)]
    else:
        fronts = [oell(a0[0] - ux * (r + 0.9 + reach) + px * j * 1.35, a0[1] - uy * (r + 0.9 + reach) + py * j * 1.35,
                       pr * 1.15, pr * 0.85, ang) for j in (-0.7, 0.7)]
    backs = [oell(a1[0] + ux * (r * 0.55) + px * (r * 0.75 + j * 0.9), a1[1] + uy * (r * 0.55) + py * (r * 0.75 + j * 0.9),
                  pr * 0.95, pr * 0.8, ang) for j in (-0.8, 0.8)]
    if dangle:                                           # 축 늘어진 뒷발 둘 — 양옆으로 나란히
        backs = [oell(a1[0] + ux * r * 0.75 + px * j * r * 0.55, a1[1] + uy * r * 0.75 + py * j * r * 0.55,
                      pr * 0.8, pr, ang) for j in (-1, 1)]
    tw = 0.7 * sin(2 * ph)
    t0 = (a1[0] + ux * r * 0.4 - px * r * 0.3, a1[1] + uy * r * 0.4 - py * r * 0.3)
    tl = chain([t0, (t0[0] + ux * 3.0 - px * 1.2, t0[1] + uy * 3.0 - py * 1.2),
                (t0[0] + ux * 3.6 - px * (3.6 + tw), t0[1] + uy * 3.6 - py * (3.6 + tw))], 1.6, 1.5)
    out = [base(bodyf, tl, *fronts, *backs)]
    out.append(part(tl, WHITE))
    for f in backs:
        out.append(part(f, WHITE))
    out.append(part(bodyf, WHITE))
    for f in fronts:
        out.append(part(f, WHITE))
    hx_, hy_ = a0[0] + ux * r * 0.9 + head[0] * hoff, a0[1] + uy * r * 0.9 + head[1] * hoff
    out += cat(Frame(hx_, hy_, s), "blink" if k in (5, 11) else ("happy" if sin(ph) > 0.7 else "open"),
               body=False, paws=False, tail=False)
    o = 0.6 if sin(ph) > 0.3 else 0.0
    if chev:
        for (x, y, dx, dy) in chev:
            out += chevron(x + dx * o, y + dy * o, dx, dy, 2.2, 1.0 if o else 0.75)
    return out


def sc_we(fr):
    return stretch(fr, (15.8, 11.4), 0.0, 13.0, 0.6, [(1.9, 9.0, -1, 0), (29.1, 9.0, 1, 0)], (0.0, -1.0), 2.6)


def sc_ns(fr):
    return stretch(fr, (6.9, 17.6), pi / 2, 11.0, 0.56, [(6.4, 1.9, 0, -1), (6.4, 29.1, 0, 1)], (0.0, -1.0), 3.4, dangle=True)


def sc_nwse(fr):
    return stretch(fr, (14.6, 14.6), pi / 4, 13.0, 0.6, [(3.6, 3.6, -1, -1), (27.4, 27.4, 1, 1)], (0.45, -0.9), 1.8)


def sc_nesw(fr):
    return stretch(fr, (13.6, 14.2), 3 * pi / 4, 13.0, 0.6, [(27.4, 3.6, 1, -1), (3.6, 27.4, -1, 1)], (-0.45, -0.9), 1.8)


def sc_move(fr):
    """앉은 흰냥 둘레를 볕 조각이 빙글 — 눈으로 쫓는다. 네 방향 분홍 화살촉"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    o = 0.6 if k % 6 < 3 else 0.0
    out = []
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        out += chevron(15.5 + dx * (13.6 + o), 15.5 + dy * (13.6 + o), dx, dy, 2.2)
    a = ph - pi / 2
    sx, sy = 15.5 + 9.8 * cos(a), 15.5 + 9.4 * sin(a)
    F = Frame(15.5, 12.2, 0.7)
    hx_, hy_ = F.w(0, 0)
    lx, ly = sx - hx_, sy - hy_
    ll = hypot(lx, ly) or 1.0
    behind = sy < 12.0
    sp = sparkle(sx, sy, 2.3 if k % 2 == 0 else 1.7)
    out += (sp if behind else [])
    out += cat(F, "open", look=(lx / ll, ly / ll), turn_=0.9 * lx / ll, sway=0.5 * sin(2 * ph))
    out += ([] if behind else sp)
    return out


def sc_up(fr):
    """우유병을 머리에 이고 균형 잡기 — 병뚜껑(맨 위)이 핫스팟이라 병과 머리는 그대로, 눈은 병을 올려다보고
    꼬리로 균형을 잡는다(꼬리 · 귀만 움직인다)"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    X = 6.6
    cap = rbox(X, 2.85, 1.35, 1.25, 0.5)
    bottle = smin(0.8, rbox(X, 5.2, 1.15, 1.5, 0.3), ell(X, 7.0, 2.0, 1.2), rbox(X, 10.0, 2.0, 3.0, 0.9))

    def bcol(x, y):
        c = lerp(MILK, MILK_D, smooth(X + 0.3, X + 1.7, x))
        return lerp(c, DISH_L, smooth(8.4, 8.7, y) * smooth(10.6, 10.3, y))
    s = 0.74
    F = Frame(X + 0.8, 17.6, s)
    sw = sin(ph)
    tp = [(3.4, 9.6), (7.6, 10.0), (10.0, 7.0), (9.8 + 1.0 * sw, 3.4), (8.4 + 1.6 * sw, 1.4)]
    mood = "blink" if k == 7 else "open"
    out = cat(F, mood, look=(0.25 * sw, -0.85), body=True, paws=True, tail_pts=tp,
              ear_tilt=(0.5 * max(0.0, sw), 0.5 * max(0.0, -sw)))
    btl = [base(cap, bottle), part(bottle, bcol, shade=MILK_D, ink=DISH_D, line=0.85),
           part(cap, lambda x, y: lerp(BLUE_L, BLUE, smooth(2.0, 3.6, y)), shade=BLUE_D, ink=BLUE_D, line=0.8)]
    return out + btl


def sc_hand(fr):
    """앉아서 앞발 하나를 위로 번쩍 들어 젤리를 보이며 하이파이브 — 짝 할 때 눈을 ^^, 볕 반짝"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    tap = k % 6 in (3, 4, 5)
    s = 0.8
    F = Frame(17.0, 13.6, s)
    hand = F.loc(7.5, 3.75 + (0.3 if tap else 0.0))
    out = cat(F, "happy" if k % 6 == 4 else "open", turn_=-0.35, look=(-0.6, -0.5), sway=0.5 * sin(ph),
              arms=[((-7.0, 3.4), hand, True)], ear_tilt=(-1.1, 0.0))
    if tap:
        L = 1.9 if k % 6 == 4 else 1.3
        out += sparkle(2.8, 7.0, L, 0.55) + sparkle(12.6, 2.6, L, 0.55)
    return out


SCENE = {"arrow": sc_arrow, "busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "wait": sc_wait,
         "hand": sc_hand, "cross": sc_cross, "ibeam": sc_ibeam, "move": sc_move, "no": sc_no, "pen": sc_pen,
         "up": sc_up, "we": sc_we, "ns": sc_ns, "nwse": sc_nwse, "nesw": sc_nesw}


def scene(name, frame=0.0, soft_=0.0, tip_body=False):
    ax, ay = HOT[name]
    return SCENE[name](frame), (ax + 0.5, ay + 0.5)


class WhiteCat:
    cell = staticmethod(scene)
    M = 1.8
    NF, RATE = NF, round(LOOP * 60) // NF
    LOOP = LOOP                    # 17칸이 다 움직인다(hd.animated). 장 수는 LOOP 가 아니라 NF 로(hdpet.frames)
    shadow = (0.10, 0.12, 0.22, 0.16)
    shadow_off, shadow_blur = (0.3, 0.45), 0.9
    ink = OUT

    def body(self, x, y, d, nx, ny, warn, frame):
        return WHITE, 1.0

    def glow(self, x, y, d, warn, frame):
        return RIM, 0.95 * smooth(1.2, 0.7, d)


register("whitecat", WhiteCat())

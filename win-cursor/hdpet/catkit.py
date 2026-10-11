# SPDX-License-Identifier: Apache-2.0
"""냥이 · 애니 고화질 공용 틀 — 치비 냥(머리가 몸만 한 통통 냥) · 스티커 채색(고른 먹선 1칸 + 셀 그늘 한 단).

흰냥이(whitecat.py)에서 뗐다. 냥이마다 다른 것은 털빛(Coat — 털 · 그늘 · 먹 · 눈 · 귀 속 · 코 · 볼 · 테)과
칸마다 하는 짓(장면 · 소품)이고, 몸 · 얼굴 · 빼꼼 화살표 · 모양 탭 화살표 · 기지개는 여기 하나다.
좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 장면은 NF 장으로 나뉘어 있다(k = round(fr × NF) % NF).

털빛은 모듈 전역 C 하나다 — Pet.cell 이 칸을 그리기 전에 use() 로 바꿔 끼우고, 칠 함수는 만들 때 색을 붙잡는다.
한 프로세스가 한 번에 한 칸만 그린다는 전제다(build 워커 · hdpet 시트 다 그렇다). 스레드로 칸을 나눠 그리게 되면
털빛을 인자로 넘기는 쪽으로 바꾼다.

이 모듈을 읽으면 같은 폴더의 다른 냥이 결도 다 읽어 등록한다(맨 아래 load) — hdpet/__init__.py 에 줄을 더하면
그 파일이 이펙트 20결 모양 화살표 해시(build.fxshape)에도 들어 있어 60칸을 다시 굽는다.
"""
import importlib
import math
import pkgutil
import sys

from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

sin, cos, hypot, floor, pi = math.sin, math.cos, math.hypot, math.floor, math.pi


def hx(s):
    return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))


# 냥이 묶음 공통(발자국 · 화살촉 분홍, 볕 반짝, 빼꼼 화살표 크림)
PINK = hx("f4a0b0")
SUN, SUN_L = hx("ffd24a"), hx("fff0a8")
CREAM, CREAM_D = hx("fff6e8"), hx("f1e2c8")
HI = (1.0, 1.0, 1.0)

NF, LOOP = 12, 1.0
LINE = 1.0                         # 먹선 굵기(칸) — 32 로 줄여도 1px
SH = (1.15, 1.15)                  # 그늘 띠: 모양을 왼쪽 위로 민 것 밖(= 오른쪽 아래 가장자리 1칸)


class Coat:
    """털빛 하나. fur(부위, F, turn_) 가 그 부위 바탕색(색 또는 (x, y) → 색)을 준다 — 부위는
    head · ear · body · paw · tail · arm · hand · front · back(기지개 앞발 · 뒷발). 무늬 냥은 fur 를 덮어쓴다.
    iris 는 (보는 쪽 왼눈, 오른눈) 마다 (홍채, 짙은, 밝은)"""

    def __init__(self, base, shade, out, eye, rim, iris, ear=PINK, cheek=hx("f7a3b5"), nose=hx("e27d90"),
                 nose_l=hx("f6b3c0"), jelly=PINK, tongue=PINK):
        self.base, self.shade, self.out, self.eye, self.rim, self.iris = base, shade, out, eye, rim, iris
        self.ear, self.cheek, self.nose, self.nose_l, self.jelly, self.tongue = ear, cheek, nose, nose_l, jelly, tongue

    def fur(self, part, F=None, turn_=0.0):
        return self.base


C = None


def use(coat):
    global C
    C = coat


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
    ink = C.out
    return layer(u, lambda x, y, e, nx, ny, fr: (ink, 1.0), glow=True, shadow=True)


def part(f, col=None, shade=None, line=LINE, sh=1.0, ink=None):
    """한 조각: 바탕색 + 오른쪽 아래 그늘 띠 한 칸 + 먹선. col 은 색 또는 (x, y) → 색. 안 주면 털빛"""
    col = C.base if col is None else col
    shade = C.shade if shade is None else shade
    ink = C.out if ink is None else ink

    def paint(x, y, e, nx, ny, fr):
        c = col(x, y) if callable(col) else col
        if sh:
            c = lerp(c, shade, sh * smooth(-0.15, 0.15, f(x + SH[0], y + SH[1])))
        if line:
            c = lerp(c, ink, smooth(line + 0.12, line - 0.12, -e))
        return c, 1.0
    return layer(f, paint)


def flat(f, col, a=1.0, line=0.0, ink=None):
    ink = C.out if ink is None else ink

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
    pupil = C.eye

    def paint(x, y, e, nx, ny, fr):
        c = lerp(light, iris, smooth(cy - ry * 0.9, cy - ry * 0.1, y))
        c = lerp(c, deep, 0.45 * smooth(cy + ry * 0.3, cy + ry * 1.0, y))
        c = lerp(c, pupil, smooth(0.12, -0.12, hypot((x - px) / prx, (y - py) / pry) - 1))
        c = lerp(c, HI, smooth(h1[2] + 0.1, h1[2] - 0.1, hypot(x - h1[0], y - h1[1])))
        c = lerp(c, HI, 0.9 * smooth(h2[2] + 0.08, h2[2] - 0.08, hypot(x - h2[0], y - h2[1])))
        return lerp(c, deep, smooth(0.26, 0.1, -e)), 1.0
    return layer(ell(cx, cy, rx, ry), paint)


def shut(cx, cy, rx, kind="blink"):
    """감은 눈: blink 는 아래로 휜 ∪(졸린 웃음), happy 는 ^"""
    w = max(0.3, 0.2 * rx)
    if kind == "happy":
        return flat(arc(cx, cy + rx * 0.55, rx * 0.95, w, pi * 1.2, pi * 0.6), C.eye)
    return flat(arc(cx, cy - rx * 0.5, rx * 0.95, w, pi * 0.18, pi * 0.64), C.eye)


def face(F, mood="open", look=(0.0, 0.0), turn_=0.0, mouth="w", tongue=0.0):
    """눈은 머리 가운데 높이, 넓게 벌어지고 바로 밑에 볼, 사이 아래에 작은 코. 눈 색은 털빛의 iris(보는 쪽 왼눈, 오른눈)"""
    s = F.s
    out = []
    er = max(1.66 * s, 1.32)
    for sg in (-1, 1):                                         # 볼 먼저(눈 아래 깔림)
        bx, by = F.w(turn_ + sg * 4.5, 2.7)
        rx = max(1.45 * s, 0.95)
        out.append(soft(ell(bx, by, rx, rx * 0.62), C.cheek, 0.85))
    for sg in (-1, 1):
        ex, ey = F.w(turn_ + sg * 3.15, 0.25)
        closed = mood in ("blink", "happy") or (mood == "wink" and sg > 0)
        if closed:
            out.append(shut(ex, ey, er, "happy" if mood in ("happy", "wink") else "blink"))
        else:
            out.append(eye(ex, ey, er, *C.iris[sg > 0], look=look))
    nx, ny = F.w(turn_, 2.05)
    hw = max(0.78 * s, 0.6)
    nose = rpoly([(nx - hw, ny - hw * 0.45), (nx + hw, ny - hw * 0.45), (nx, ny + hw * 0.6)], hw * 0.3)
    tg_c, nose_c, nose_l, ink = C.tongue, C.nose, C.nose_l, C.out
    if tongue > 0:                                             # 혀 날름(코 아래로 분홍 혀)
        tl = tongue * max(2.2 * s, 1.6)
        tw = max(0.9 * s, 0.75)
        tg = smin(0.3, ell(nx, ny + hw * 0.9 + tl * 0.55, tw, tl * 0.55 + 0.2), circle(nx, ny + hw * 0.9 + tl, tw))
        out.append(flat(tg, lambda x, y: lerp(tg_c, nose_c, smooth(nx - 0.05, nx + 0.05, x) * 0.0 + 0.0), line=0.28, ink=nose_c))
        out.append(flat(capsule(nx, ny + hw * 0.9 + tl * 0.3, nx, ny + hw * 0.9 + tl * 0.85, 0.12), nose_c, 0.7))
    if mouth == "w" and s >= 0.5:                              # ω 입(작게)
        m = max(0.62 * s, 0.5)
        w = max(0.17 * s, 0.16)
        for sg in (-1, 1):
            out.append(flat(arc(nx + sg * m, ny + hw * 0.35, m, w, pi * 0.08, pi * 0.84), ink, 0.95))
    out.append(flat(nose, lambda x, y: lerp(nose_l, nose_c, smooth(ny - hw * 0.4, ny + hw * 0.2, y))))
    return out


def blink_of(fr, at=0.75):
    """한 바퀴에 한 번, 한 장만 감는다"""
    k = round(fr * NF) % NF
    return k == round(at * NF) % NF


# ---- 치비 냥 (캐논: 머리 가운데 (0, 0), 아래가 +v) ----
#   머리 넓이 15 · 높이 11.5(귀 끝까지 15) · 몸은 머리보다 작은 콩 · 앞발 둘 · 말린 꼬리. 다 합쳐 22칸

def head_f(F, squish=0.0):
    return F.f(smin(1.6, ell(0, -0.4, 6.9, 5.6 - squish), ell(0, 1.3 + squish * 0.3, 7.6, 4.3)))


def ear_pts(sg, tilt=0.0):
    return [(sg * 6.7, -1.0), (sg * (6.1 + tilt), -8.7), (sg * 1.3, -4.9)]


def cat(F, mood="open", look=(0.0, 0.0), turn_=0.0, sway=0.0, bob=0.0, body=True, paws=True, tail=True,
        arms=(), tongue=0.0, ear_tilt=(0.0, 0.0), tail_pts=None, extra_under=(), face_on=True, mouth="w"):
    """앉은 치비 냥 → 레이어 목록. arms = [(어깨 (u, v), 손 (u, v), 젤리 보임)] — 머리 위에 그린다.
    bob 은 몸이 살짝 눌리는 정도(0–1). 색은 털빛(부위마다 fur) + 오른쪽 아래 그늘 한 칸"""
    s = F.s
    fur = C.fur
    rt = max(1.8, 1.5 * s) / s                                 # 꼬리 반지름(캐논) — 먹선 안에 털이 남게
    pieces = []
    if tail:
        tp = tail_pts or [(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.4 + sway, 3.9), (8.2 + 1.4 * sway, 2.0)]
        pieces.append((F.f(chain(tp, rt * 1.05, rt * 0.95)), fur("tail", F, turn_)))
    if body:
        pieces.append((F.f(ell(0, 7.7 + bob * 0.3, 5.4 + bob * 0.25, 4.4 - bob * 0.3)), fur("body", F, turn_)))
    if paws:
        for sg in (-1, 1):
            pieces.append((F.f(ell(sg * 2.45, 11.35, 1.95, 1.4)), fur("paw", F, turn_)))
    pieces += list(extra_under)
    ears = [F.f(rpoly(ear_pts(sg, ear_tilt[(sg + 1) // 2]), 0.95)) for sg in (-1, 1)]
    H = head_f(F, bob * 0.35)
    arm_fs = []
    for sh_, hand, jelly in arms:
        ra = max(2.7, 2.1 / s)                                 # 팔 반지름(캐논) — 먹선 안에 털이 1칸 넘게
        a = F.f(taper(sh_[0], sh_[1], ra * 1.12, hand[0], hand[1], ra * 0.95))
        p = F.f(ell(hand[0], hand[1], ra * 1.12, ra * 1.04))
        arm_fs.append((a, p, hand, jelly))
    allf = [p[0] for p in pieces] + ears + [H] + [g for a, p, _, _ in arm_fs for g in (a, p)]
    out = [base(*allf)]
    for p in pieces:
        out.append(part(p[0], p[1]))
    for sg, E in zip((-1, 1), ears):
        out.append(part(E, fur("ear", F, turn_)))
        pts = ear_pts(sg, ear_tilt[(sg + 1) // 2])
        cx, cy = sum(p[0] for p in pts) / 3, sum(p[1] for p in pts) / 3 + 0.5
        inner = F.f(rpoly([(cx + (x - cx) * 0.5, cy + (y - cy) * 0.5) for x, y in pts], 0.5))
        out.append(flat(inner, C.ear))
    out.append(part(H, fur("head", F, turn_)))
    if face_on:
        out += face(F, mood, look, turn_, mouth, tongue)
    for a, p, hand, jelly in arm_fs:
        out.append(part(a, fur("arm", F, turn_)))
        out.append(part(p, fur("hand", F, turn_)))
        if jelly:
            out += jellies(F, hand)
    return out


def jellies(F, c, spread=0.0):
    """발바닥 젤리: 큰 젤리 하나 + 발가락 셋"""
    out = []
    u, v = c
    big = F.f(ell(u, v + 0.55, 0.95, 0.75))
    out.append(flat(big, C.jelly))
    for dx, dy in ((-1.15 - spread, -0.55), (0.0, -1.05 - spread), (1.15 + spread, -0.55)):
        out.append(flat(F.f(circle(u + dx, v + dy, 0.48)), C.jelly))
    return out


# ---- 소품 ----

ARROW = [(0.0, 0.0), (0.0, 19.0), (4.4, 14.8), (7.6, 21.8), (10.6, 20.4), (7.4, 13.6), (13.4, 13.6)]   # 끝 (0, 0)


def arrow_f(tip, sc, r=0.35):
    pts = [(tip[0] + sc * x, tip[1] + sc * y) for x, y in ARROW]
    return rpoly(pts, r)


def cur(ls):
    """커서 층 표시 — 막대 둘 색조가 이 층만 커서 색으로 칠한다(hdpet.render 가 표식을 박음)"""
    for L in ls:
        L["cur"] = True
    return ls


def small_arrow(tip=(1.62, 1.62), sc=0.52):
    f = arrow_f(tip, sc, 0.3)
    return cur([base(f), part(f, HI_WHITE, sh=0.0)])


HI_WHITE = hx("fcfdff")            # 작은 화살표 · 스티커 띠 흰색(흰냥이 털과 같은 흰색 — 그 판에서 뗐다)


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


def paw_print(x, y, a):
    f = union(ell(x, y + 0.6, 1.15, 0.95), circle(x - 1.35, y - 0.75, 0.55), circle(x, y - 1.35, 0.55),
              circle(x + 1.35, y - 0.75, 0.55))
    return layer(f, lambda px, py, e, nx, ny, fr: (lerp(PINK, hx("d8728a"), smooth(0.3, 0.15, -e)), 1.0), alpha=a)


# ---- 화살표: 빼꼼 (핫스팟 (1, 1)) ----

TIP = (1.62, 1.62)                 # 끝이 (1, 1) 칸에 먹선으로 닿게 · 판 위 끝과는 1.6칸 떨어지게
PEEK_TAIL = [(3.0, 9.6), (7.4, 10.4), (9.6, 7.4), (9.4, 3.6), (8.0, 1.6)]


def _peek_cat(F, fr):
    ph = TAU * fr
    tp = [(3.0, 9.6), (7.4, 10.4), (9.6, 7.4), (9.4 + 0.6 * sin(ph), 3.6), (8.0 + 0.9 * sin(ph), 1.6)]
    return cat(F, "blink" if blink_of(fr) else "open", look=(-0.6, 0.25), sway=0.6 * sin(ph), body=True, paws=False,
               tail_pts=tp)


def peek(fr):
    """빼꼼: 크림 화살표 빗변 뒤에서 치비 냥이 고개를 쏙 — 두 앞발이 빗변을 잡는다(원본 구성 그대로, 머리만 크게)"""
    ph = TAU * fr
    sc = 1.24
    P = [(TIP[0] + sc * x, TIP[1] + sc * y) for x, y in ARROW]
    arw = rpoly(P, 0.55)
    lift = 0.5 * (1 - cos(ph)) / 2
    F = Frame(19.6, 10.4 - lift, 0.8)
    out = _peek_cat(F, fr)
    out += cur([base(arw), part(arw, cream_of, sh=0.0)])
    # 빗변(끝 → 오른쪽 어깨) 위 앞발 둘 — 빗변을 따라 나란히, 반쯤 빗변 바깥으로
    ex, ey = P[6][0] - P[0][0], P[6][1] - P[0][1]
    el = hypot(ex, ey)
    ux, uy = ex / el, ey / el
    for t in (15.6, 18.9):
        out += paw(P[0][0] + ux * t + uy * 0.55, P[0][1] + uy * t - ux * 0.55, ux, uy)
    return out


def cream_of(x, y):
    return lerp(CREAM, CREAM_D, smooth(6, 30, x * 0.4 + y))


def paw(cx, cy, ux, uy):
    """빗변(방향 (ux, uy))에 건 앞발 하나 — 발가락 금 둘이 빗변 쪽으로 짧게"""
    nx, ny = uy, -ux                                    # 빗변 바깥(오른쪽 위)
    p = oell(cx, cy, 1.75, 1.4, math.atan2(uy, ux))
    out = [base(p), part(p, C.fur("paw"), sh=0.0)]
    for d in (-0.6, 0.6):
        bx, by = cx + ux * d, cy + uy * d
        out.append(flat(capsule(bx - nx * 0.2, by - ny * 0.2, bx - nx * 1.0, by - ny * 1.0, 0.13), C.out, 0.8))
    return out


# ---- 화살표: 매끈한 모양 탭 — smooth.SHAPES 의 화살표 윤곽에 같은 빼꼼 ----
# 모양 폴더에는 화살표 칸만 굽는다(build.build_hd_shape) — 나머지 16칸은 받는 쪽이 기본 폴더에서 빌린다.
# 냥이는 기본 화살표에서 잰 자리 그대로 빗변에 붙인다: 빗변 길이 0.797 자리에서 바깥 테 + 6.75, 앞발은 0.659 · 0.798 자리 테 + 0.6

HIGH = 27.6                        # 바깥 테 높이 — 기본 화살표(1.07 에서 28.7)와 같게
BAND = 1.2                         # 스티커(cutout) 흰 띠 굵기
EAR, RIGHT = 7.0, 9.4              # 빼꼼 냥이 잉크가 자리에서 위(귀 끝, 까딱 포함) · 오른쪽(꼬리)으로 닿는 거리 — 흰냥이 기본 판에서 잼
_SHAPED = {}


def _edge(g, s, off):
    """빗변 s(0 끝 · 1 어깨) 자리에서 빗변 바깥쪽으로 바깥 테까지 걸어 나간 뒤 off 만큼 더 간 점"""
    (x0, y0), (ux, uy), el = g["P0"], g["u"], g["L"]
    px, py = x0 + ux * s * el, y0 + uy * s * el
    t = -3.0
    while g["outer"](px + uy * t, py - ux * t) < 0 and t < 8:
        t += 0.05
    return px + uy * (t + off), py - ux * (t + off)


def shaped(shape):
    """smooth.SHAPES 윤곽 → 몸 · 바깥 테 거리함수, 빗변, 냥이 자리, 핫스팟. 바깥 테 왼쪽 · 위 끝이 기본 화살표처럼 1.07 에 닿는다.
    smooth.peek_drawer 와 같은 셈: 냥이가 판 위로 넘으면 통째로(핫스팟째) 내리고, 그래서 아래 · 오른쪽으로 넘으면 화살표만 5%씩
    줄인다(0.7 까지)"""
    if shape not in _SHAPED:
        import smooth as sm
        spec = sm.SHAPES[shape]
        band = BAND if spec["style"] == "sticker" else 0.0
        ys = [p[1] for p in spec["pts"]]
        for m in [1 - 0.05 * i for i in range(7)]:
            k = (HIGH - 2 * band) / (max(ys) - min(ys)) * m
            ring_ = sm.fillet([(x * k, y * k) for x, y in spec["pts"]], [r * spec["rscale"] * k for r in spec["radii"]], 8)
            dx = 1.07 + band - min(p[0] for p in ring_)
            dy = 1.07 + band - min(p[1] for p in ring_)
            (x0, y0), (x1, y1) = ((x * k + dx, y * k + dy) for x, y in spec["pts"][:2])
            body = poly([(x + dx, y + dy) for x, y in ring_])
            el = hypot(x1 - x0, y1 - y0)
            g = dict(outer=grow(body, band) if band else body, P0=(x0, y0), u=((x1 - x0) / el, (y1 - y0) / el), L=el)
            cx, cy = _edge(g, 0.797, 6.75)
            down = max(0.0, 1.2 - (cy - EAR))
            if max(p[1] for p in ring_) + dy + band + down <= 29.6 and cx + RIGHT <= 30.6:
                break
        ring_ = [(x + dx, y + dy + down) for x, y in ring_]
        body = poly(ring_)
        ty = min(p[1] for p in ring_)                    # 핫스팟은 맨 윗줄의 왼쪽 끝(smooth._hotspot 과 같은 약속)
        tx = min(p[0] for p in ring_ if p[1] < ty + 0.5)
        g.update(body=body, outer=grow(body, band) if band else body, band=band, P0=(x0, y0 + down),
                 cat=(cx, cy + down), hot=(floor(tx) + 0.5, floor(ty - band) + 0.5))
        _SHAPED[shape] = g
    return _SHAPED[shape]


def peek_shape(fr, shape):
    g = shaped(shape)
    ph = TAU * fr
    cx, cy = g["cat"]
    lift = 0.5 * (1 - cos(ph)) / 2
    F = Frame(cx, cy - lift, 0.8)
    out = _peek_cat(F, fr)
    if g["band"]:                                       # 스티커: 먹선 · 흰 띠 · 크림 몸
        out += cur([base(g["outer"]), part(g["outer"], HI_WHITE, sh=0.0), part(g["body"], cream_of, line=0.0)])
    else:
        out += cur([base(g["body"]), part(g["body"], cream_of)])
    for s in (0.659, 0.798):
        out += paw(*_edge(g, s, 0.6), *g["u"])
    return out


# ---- 동반(작은 화살표 + 작은 냥) ----

def buddy(fr, mood=None):
    ph = TAU * fr
    m = mood or ("blink" if blink_of(fr, 0.25) else "open")
    F = Frame(13.6, 7.7, 0.58)
    return small_arrow() + cat(F, m, look=(-0.4, 0.0), sway=0.5 * sin(ph), bob=0.4 * (1 - cos(ph)) / 2)


# ---- 기지개 (we · ns · nwse · nesw) ----

def stretch(fr, C_, ang, length, s=0.6, chev=None, head=(0.0, -1.0), hoff=2.2, dangle=False):
    """기지개(쭉 늘어난 냥): 굵은 몸이 축(ang)을 따라 — 앞 끝에 똑바른 얼굴, 그 앞으로 쭉 뻗은 앞발 둘,
    뒤 끝에 뒷발 둘과 말린 꼬리. head 는 머리를 몸 축에서 얼마나(hoff) 어느 쪽으로 올릴지(화면 방향)"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    e = length * (1 + 0.05 * sin(ph))
    ux, uy = cos(ang), sin(ang)
    cx, cy = C_
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
    fur = C.fur
    out = [base(bodyf, tl, *fronts, *backs)]
    out.append(part(tl, fur("tail")))
    for f in backs:
        out.append(part(f, fur("back")))
    out.append(part(bodyf, fur("body")))
    for f in fronts:
        out.append(part(f, fur("front")))
    hx_, hy_ = a0[0] + ux * r * 0.9 + head[0] * hoff, a0[1] + uy * r * 0.9 + head[1] * hoff
    out += cat(Frame(hx_, hy_, s), "blink" if k in (5, 11) else ("happy" if sin(ph) > 0.7 else "open"),
               body=False, paws=False, tail=False)
    o = 0.6 if sin(ph) > 0.3 else 0.0
    if chev:
        for (x, y, dx, dy) in chev:
            out += chevron(x + dx * o, y + dy * o, dx, dy, 2.2, 1.0 if o else 0.75)
    return out


# ---- 결 ----

class Pet:
    """냥이 결 하나 — coat(털빛) · scenes(칸 → fr → 레이어) · hot(칸 → art 칸 핫스팟).
    화살표 칸은 늘 빼꼼(peek, 모양 탭이면 peek_shape)이라 scenes 에 arrow 를 안 넣어도 된다"""
    M = 1.8
    NF, RATE = NF, round(LOOP * 60) // NF
    LOOP = LOOP                    # 17칸이 다 움직인다(hd.animated). 장 수는 LOOP 가 아니라 NF 로(hdpet.frames)
    shadow = (0.10, 0.12, 0.22, 0.16)
    shadow_off, shadow_blur = (0.3, 0.45), 0.9
    cursor = True                  # 화살표 층에 커서 표식(cur) — 시안 색조 막대가 둘(build.hue_kind)

    def __init__(self, coat, scenes, hot):
        self.coat, self.scenes, self.hot, self.ink = coat, scenes, hot, coat.out

    def cell(self, name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
        """shape 는 매끈한 모양 탭(cutout · dart · chunky) — 화살표 칸만 그 윤곽으로 다시 그린다"""
        use(self.coat)
        if shape and name == "arrow":
            return peek_shape(frame, shape), shaped(shape)["hot"]
        ax, ay = self.hot[name]
        return self.scenes.get(name, peek if name == "arrow" else None)(frame), (ax + 0.5, ay + 0.5)

    def body(self, x, y, d, nx, ny, warn, frame):
        return self.coat.base, 1.0

    def glow(self, x, y, d, warn, frame):
        return self.coat.rim, 0.95 * smooth(1.2, 0.7, d)


def load():
    """같은 폴더의 결 모듈을 다 읽는다(이미 읽힌 것 · _ 로 시작하는 것 빼고). 읽히면 저마다 register 한다"""
    pkg = __name__.rpartition(".")[0]
    for m in pkgutil.iter_modules(sys.modules[pkg].__path__):
        if not m.name.startswith("_") and f"{pkg}.{m.name}" not in sys.modules:
            importlib.import_module(f"{pkg}.{m.name}")

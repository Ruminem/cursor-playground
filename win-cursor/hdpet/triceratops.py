# SPDX-License-Identifier: Apache-2.0
"""아기 트리케라톱스(triceratopsanim) 고화질 — 공룡 틀(dinokit)에 몸빛 · 표식 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

표식은 픽셀 판(지운 gen/dino.py)대로 머리 뒤 큰 프릴(짙은 주황 속 · 노랑 테 · 크림 혹)과 이마 뿔 둘(앞으로 길게) ·
코뿔 하나, 그리고 네 발. 프릴을 한 색 동그라미로 하면 금발 머리로 읽혀서(픽셀 판 주석) 테와 혹을 둘러 가장자리를 물결로 냈다.
짓도 픽셀 판 그대로: 고개를 숙여 코뿔로 화살표 날개 끝을 콕콕 · 밀 때 질끈(화살표), 풀을 우물우물(기다림),
뿔을 들이밀며 도리도리 · 콕 할 때 콧김(금지).

갈고리(behind · over)는 Pose 만 받아 크기를 모르므로 body 로 한 겹 감싸 F 를 넘긴다 — 작은 공룡(s 0.5 안팎)에서
뿔이 먹 덩어리가 안 되게 반지름을 s 로 나눠 키운다(dinokit 의 max(2.5, 2.0 / s) 와 같은 셈).
"""
from . import catkit, register
from .dinokit import (DF, TAIL_UP, HAND_HOT, zip_lines, Hide, Kind, Pose, DinoPet, dino, puff, star, edge_pt, arrow_layers, no_sign, ph_k, hx,
                      ell, chain, taper, circle, capsule, oell, smin, union, base, part, flat, LEAF, LEAF_D, EYE,
                      sin, cos, hypot, atan2, pi)
from hd import grow

HIDE = Hide(hx("f4a65a"), hx("d9803c"), hx("fde3b4"), hx("f7d36a"))
HORN, HORN_FAR = hx("fff3d6"), hx("e8d8b8")
GRASS_INK = hx("3f7a32")
FRILL = hx("e88e48")                                     # 프릴 속 — 몸빛보다 한 끗 짙게(픽셀 판 짙은 주황이면 32 에서 갈기로 읽힘)

FC, FR = (-2.8, -3.4), 6.2                                # 프릴 가운데 · 반지름(캐논) — 머리 뒤 위로 솟은 방패
KNOBS = (35, 68, 101, 134, 167, 200)                     # 프릴 가장자리 혹 자리(도, 캐논 위가 90)
NOSE = ((6.2, -1.0), (7.0, -4.0))                        # 코뿔 뿌리 · 끝
BROW = [(3.6, -3.6), (6.6, -5.0), (9.8, -5.6)]          # 앞 이마 뿔 — 눈 위 이마에서 앞으로(정수리에서 세우면 토끼 귀로 읽힘)
BROW_FAR = [(1.8, -4.6), (4.8, -6.4), (8.2, -7.2)]      # 먼 이마 뿔(머리 뒤)
HORN_INK = 0.55                                          # 뿔 먹선(art 칸) — 틀 먹선 1칸이면 가는 뿔이 먹 쐐기가 돼 귀로 읽힘


def cut(f, g):
    return lambda x, y: max(f(x, y), -g(x, y))


class Tri(Kind):
    quad = True
    spots = ()
    s = 1.0
    F = None

    def body(self, F, K, **kw):
        """틀 몸을 그린 뒤 뿔 속을 크림으로 한 번 더 덮어 먹선을 HORN_INK 로 줄인다(뿔은 눈과 안 겹친다)"""
        IN.s, IN.F = F.s, F
        out = dino(F, IN, **kw)
        P = Pose(kw.get("nod", 0.0))
        s, k = F.s, HORN_INK / F.s
        brow, nose, far = IN.horns()
        if far:
            out.append(flat(F.f(P.hf(cut(cut(grow(far, -k), IN._head()), brow))), HORN_FAR))
        for h in (brow, nose):
            out.append(flat(F.f(P.hf(grow(h, -k))), HORN))
        return out

    def _head(self):
        return smin(1.4, ell(*self.head), ell(*self.snout))

    def _col(self, P, fcol):
        """캐논 색 함수 → art 색 함수(머리 까딱 · 뒤집기까지)"""
        g = P.hf(fcol)
        loc = self.F.loc
        return lambda x, y: g(*loc(x, y))

    def horns(self):
        """(앞 이마 뿔, 코뿔, 먼 이마 뿔 또는 None) — 캐논, 까딱 전. 반지름은 s 로 나눠 키운다(작으면 먹 덩어리)"""
        s = self.s
        hd_in = grow(self._head(), -1.3)                   # 머리 깊숙한 데는 잘라 뿌리만 머리에 얹힌다
        brow = cut(chain(BROW, max(2.2, 1.6 / s), max(0.85, 0.8 / s)), hd_in)
        (a, b), (c, d) = NOSE
        nose = cut(taper(a, b, max(1.6, 1.1 / s), c, d, max(0.7, 0.7 / s)), hd_in)
        far = chain(BROW_FAR, max(2.0, 1.5 / s), max(0.8, 0.8 / s)) if s >= 0.7 else None   # 작으면 뿔 둘이 한 덩이라 뺀다
        return brow, nose, far

    def behind(self, P):
        s = self.s
        rk = max(1.35, 0.8 / s)
        kn = [(FC[0] + FR * 0.95 * cos(pi * a / 180), FC[1] - FR * 0.95 * sin(pi * a / 180)) for a in KNOBS]
        frill = union(ell(FC[0], FC[1], FR, FR * 1.04), *[circle(u, v, rk) for u, v in kn])

        def fcol(u, v):
            for a, b in kn:
                if (u - a) ** 2 + (v - b) ** 2 < rk * rk:
                    return HORN
            d = hypot(u - FC[0], v - FC[1]) / FR
            return HIDE.deco if d > 0.72 else FRILL
        out = [(P.hf(frill), self._col(P, fcol))]
        far = self.horns()[2]
        if far:
            out.append((P.hf(far), HORN_FAR))
        return out

    def over(self, P):
        brow, nose, _ = self.horns()
        return [(P.hf(brow), HORN), (P.hf(nose), HORN)]


class _Plain(Tri):
    body = None


IN = _Plain()
K = Tri()


def tip_of(F, nod):
    return F.w(*Pose(nod).hp(*NOSE[1]))


# ---- 화살표: 오른쪽 아래에 선 트리케라가 왼쪽을 보고 고개를 숙여 코뿔로 날개 끝을 콕콕 ----
POKE = (0, 0, 0.5, 1, 1, 0.5, 0, 0, 0.5, 1, 1, 0.5)
AS = 0.6


def _reach(g, s, nod):
    """코뿔 끝이 닿을 빗변 자리 — 날개 끝(t 1)부터 공룡이 판 안에 들 때까지 끝 쪽으로 물린다"""
    F0 = DF(0.0, 0.0, s, fx=-1)
    tx, ty = tip_of(F0, nod)
    xmax, ymax = 30.4 - 11.0 * s - 1.4, 30.4 - 14.0 * s
    t = 1.0
    while True:
        px, py = edge_pt(g, t, 0.15)
        ox, oy = px - tx, py - ty
        if (ox <= xmax and oy <= ymax) or t <= 0.5:
            return (px, py), min(ox, xmax), min(oy, ymax)
        t -= 0.04


def sc_arrow(fr, g):
    """코뿔로 날개 끝을 콕콕 — 밀 때 질끈 · 반짝, 물러날 때 고개를 든다. 꼬리 살랑. 화살표가 맨 위"""
    ph, k = ph_k(fr)
    p = POKE[k]
    nod = -0.14 + 0.18 * p
    (px, py), ox0, oy0 = _reach(g, AS, 0.04)
    F0 = DF(0.0, 0.0, AS, fx=-1)
    t1, t2 = tip_of(F0, 0.04), tip_of(F0, nod)
    back = 1.4 * (1 - p)                                    # 물러난 만큼 몸째 오른쪽으로
    F = DF(ox0 + t1[0] - t2[0] + back, oy0 + t1[1] - t2[1] + 0.3 * (1 - p), AS, fx=-1)
    out = dino(F, K, "squeeze" if p == 1 else "blink" if k == 7 else "open", nod=nod, sway=0.8 * sin(ph),
               step=0.5 * p, tail_pts=TAIL_UP)
    if p == 1:
        out += star(px + 1.6, py - 1.9 - 0.5 * (k % 2), 1.6, 0.55)
    return out + arrow_layers(g)


# ---- 기다림: 풀을 우물우물 ----

def blade(x0, y0, x1, y1, w):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    ang = atan2(y1 - y0, x1 - x0)
    return oell(mx, my, hypot(x1 - x0, y1 - y0) / 2, w, ang)


def tuft(x, y, h=4.0, a=1.0):
    """땅 풀 한 무더기 — 잎 셋"""
    f = union(blade(x, y, x - 1.8, y - h * 0.75, 0.9), blade(x, y, x + 0.2, y - h, 0.95), blade(x, y, x + 2.0, y - h * 0.7, 0.9))
    return [base(f), part(f, LEAF, shade=LEAF_D, ink=GRASS_INK, line=0.5)]


def sc_wait(fr):
    """입에 문 풀 잎이 장마다 하나씩 줄고 턱이 오물오물 · 고개 까딱, 꼬리 살랑. 발치에 풀 무더기"""
    ph, k = ph_k(fr)
    chew = k % 2
    s = 1.0
    nod = 0.06 * chew
    F = DF(14.6, 13.2, s)
    out = tuft(28.2, 29.6, 4.6) + tuft(3.4, 29.8, 3.4)
    out += dino(F, K, "happy" if k in (8, 9) else "open", nod=nod, mouth=0.35 * chew, sway=1.0 * sin(ph),
                tail_pts=TAIL_UP, bob=0.4 * chew)
    P = Pose(nod)
    x0, y0 = F.w(*P.hp(5.8, 3.2))
    n = 3 - k // 4
    ends = ((4.4, -0.6), (4.0, 1.6), (3.0, 3.4))[:n]
    w = 1.0 + 0.6 * chew
    f = union(*[blade(x0, y0, x0 + dx, y0 + dy + 0.5 * chew, w) for dx, dy in ends])
    out += [base(f), part(f, LEAF, shade=LEAF_D, ink=GRASS_INK, line=0.5)]
    return out


# ---- 금지: 뿔을 들이밀며 도리도리 ----

def sc_no(fr):
    """금지 표지 안에서 뿔을 앞으로 들이밀며 고개를 흔든다 — 콕 숙일 때 질끈 · 콧김, 아니면 찌푸린 눈썹. 표지가 위"""
    ph, k = ph_k(fr)
    poke = k % 6 in (2, 3)
    s = 0.6
    nod = 0.24 if poke else 0.1 * sin(2 * ph)
    F = DF(15.4 + 0.6 * sin(ph), 13.6, s)
    out = dino(F, K, "squeeze" if poke else "open", nod=nod, step=0.6 * sin(2 * ph), sway=0.6 * sin(ph), tail_pts=TAIL_UP)
    P = Pose(nod)
    if poke:
        x, y = F.w(*P.hp(9.6, 1.4))
        out += puff(x + 1.0, y, 0.9, 0.95)
    else:
        a, b = F.w(*P.hp(2.6, -2.2)), F.w(*P.hp(5.0, -1.2))
        out.append(flat(capsule(a[0], a[1], b[0], b[1], 0.32), EYE))
    return out + no_sign()


# ---- 손(공용 칸을 바꿔 끼움): 주둥이가 아니라 앞 이마 뿔 끝으로 위를 콕콕 ----

def sc_hand(K_, fr):
    """공용 칸은 주둥이 끝을 핫스팟에 맞추고 고개를 1 라디안 젖혀서, 앞으로 뻗은 이마 뿔이 판 위로 잘린다.
    그래서 뿔 끝을 핫스팟에 맞추고 덜 젖힌다(뿔이 위 앞으로 선다). 콕 할 때 더 젖히고 줄이 튄다"""
    ph, k = ph_k(fr)
    p = (0, 0, 1, 2, 0, 0, 1, 2, 0, 0, 0, 0)[k]
    nod = -0.8 - 0.08 * p
    mood = "squeeze" if p == 2 else "blink" if k == 10 else "happy" if p == 1 else "open"
    s = 0.86
    tx, ty = DF(0.0, 0.0, s, fx=-1).w(*Pose(nod).hp(*BROW[-1]))
    hx_, hy_ = HAND_HOT[0] + 0.5, HAND_HOT[1] + 0.5 + 1.0     # 뿔 끝 원 가운데 — 먹선까지 판 안에 들게
    F = DF(hx_ - tx, hy_ - ty, s, fx=-1)
    out = zip_lines(hx_, hy_ - 1.0, 2, 1.4, 2.4, -pi / 2, 1.9) if p == 2 else []
    return out + dino(F, K_, mood, nod=nod, arm=1.8 if p else 0.8, sway=1.0 * sin(ph), tail_pts=TAIL_UP)


class Triceratops(DinoPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Triceratops(HIDE, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no}, shared={"hand": sc_hand})

register("triceratops", PET)
catkit.load()

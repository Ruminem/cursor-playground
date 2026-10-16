# SPDX-License-Identifier: Apache-2.0
"""아기 스테고사우루스(stegoanim) 고화질 — 공룡 틀(dinokit)에 몸빛 · 등판 · 꼬리 가시 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(지운 gen/dino.py)의 짓 그대로: 화살표 날개 끝을 킁킁 · 등판이 앞에서 뒤로 차례로 반짝(화살표),
등판이 앞에서 뒤로 차례로 빛나고 빛나는 판 끝에 별이 톡(기다림), 고개를 홱 쳐들고 꼬리 가시를 '안 돼 안 돼' 흔듦(금지).

표식은 Kind 갈고리로 얹는다 — 등판은 back(몸 뒤), 꼬리 가시는 tail_end. 갈고리의 (f, 색) 짝은 그늘이 몸빛 초록으로
고정돼서, Kind.body 로 틀 몸을 감싸 그린 뒤 그 조각만 제 그늘(청록 · 크림)과 반짝 빛으로 다시 칠한다.
"""
from . import catkit, register
from .dinokit import (DF, TAIL, TAIL_UP, Hide, Kind, DinoPet, dino, no_sign, arrow_layers, ph_k, snout_tip, zip_lines,
                      star, part, rpoly, taper, union, lerp, smooth, hx, sin, cos, hypot, pi)

TEAL, TEAL_D = hx("4fb3a8"), hx("2f8f86")
HORN, HORN_D = hx("fff3d6"), hx("e3cfa4")
GLOW, GLOW_D = hx("fff3a0"), hx("e8c45a")
HIDE = Hide(hx("b8e08a"), hx("86b860"), hx("eaf6cf"), TEAL, TEAL_D)

ELL = {"h": (0.0, 0.0, 6.6, 5.6, 0.15),                  # 틀 머리 타원(Kind.head) — 목덜미 판은 여기 붙어 머리와 같이 까딱
       "b": (-1.2, 8.0, 5.0, 4.6, 0.45)}                 # 틀 몸 타원(dino 의 body, bob 0) — 등 판. 끝은 판이 위로 기우는 몫
# 등판 (붙는 타원, 각(도, 90 이 꼭대기 · 180 이 뒤), 높이, 반폭) — 머리 뒤 윗선(목덜미)에서 등을 타고 엉덩이로 작아지는
# 한 줄. 판 순서가 빛나는 차례(앞 → 뒤). 처음엔 판을 몸 옆에만 붙였더니 선 치비 몸에서는 256 에서 용 · 요정 날개로 읽혔다
# 머리 꼭대기(128°)에 세우면 귀 · 뿔로, 뒤통수(140° 넘게)에 눕히면 볏 · 지느러미로 읽혀서 그 사이에 둔다
PLATES = {4: (("h", 134, 5.6, 2.5), ("h", 168, 6.2, 2.7), ("b", 152, 6.0, 2.7), ("b", 196, 4.8, 2.2)),
          3: (("h", 140, 6.0, 2.7), ("b", 150, 6.6, 2.9), ("b", 194, 5.2, 2.4)),
          2: (("h", 136, 6.0, 2.9), ("b", 152, 6.0, 2.8))}


def plate_set(s):
    """크기마다 판 수 — 작으면 판이 먹 덩어리라 장 수를 줄이고 판을 키운다(가장 작은 판 반폭이 판에서 1.9칸 넘게)"""
    n = 4 if s >= 0.7 else 3 if s >= 0.56 else 2
    if n == 4:
        return PLATES[4]
    k = max(1.0, 1.9 / s / min(p[3] for p in PLATES[n]))
    kh = 1.0 + (k - 1.0) * 0.3                           # 높이는 덜 키운다 — 다 키우면 작은 공룡 칸(연필 · 핀 · 사람)에서 판 밖으로 나갔다
    return [(w, t, h * kh, hw * k) for w, t, h, hw in PLATES[n]]


def on_ell(which, t):
    """타원 위 각 t(도) 자리와 판이 솟는 방향(바깥 법선을 위로 끝 몫만큼 기울임)"""
    cx, cy, rx, ry, lift = ELL[which]
    a = t * pi / 180
    u, v = cx + rx * cos(a), cy - ry * sin(a)
    nx, ny = cos(a) / rx, -sin(a) / ry
    n = hypot(nx, ny)
    nx, ny = nx / n, ny / n - lift
    n = hypot(nx, ny)
    return (u, v), (nx / n, ny / n)


def blade(p, n, h, hw, sink=1.8):
    """바닥 p · 방향 n 으로 솟는 둥근 오각 판"""
    e = (-n[1], n[0])

    def at(a, q):
        return (p[0] + e[0] * a + n[0] * q, p[1] + e[1] * a + n[1] * q)
    return rpoly([at(-hw * 0.85, -sink), at(-hw, h * 0.42), at(0, h), at(hw, h * 0.42), at(hw * 0.85, -sink)],
                 hw * 0.42)


def plate_tip(i, s, nod=0.0):
    from .dinokit import Pose
    w, t, h, _ = plate_set(s)[i % len(plate_set(s))]
    (u, v), (nx, ny) = on_ell(w, t)
    p = (u + nx * h, v + ny * h)
    return Pose(nod).hp(*p) if w == "h" else p


class StegoKind(Kind):
    """네 발로 서고(quad) 목덜미 · 등에 청록 판 한 줄 · 꼬리 끝에 크림 가시 둘. lit 은 빛나는 판 번호, glow 는 그 밝기(0–1)"""
    quad = True
    spots = ((-0.4, -4.8, 0.7),)                           # 머리 뒤 무늬 — 뒤쪽 둘은 목덜미 판과 겹쳐 뺀다
    lit, glow = None, 0.0

    def __init__(self):
        self.inner = _Inner(self)

    def body(self, F, K, **kw):
        self.s = F.s
        self._plates = []
        out = dino(F, self.inner, **kw)
        # 층 순서(dino): 바닥 · 꼬리 · tail_end(1) · 먼 앞발 · 먼 뒷발 · back(nb) · 가까운 몸 넷 · 배 · behind(nh) · 머리 …
        # 갈고리 조각만 제 그늘(청록 · 크림)로 다시 칠한다 — (f, 색) 짝으로는 그늘이 몸빛 초록이다
        out[2] = part(F.f(self._spk), HORN, shade=HORN_D)
        nb = sum(1 for w, _ in self._plates if w == "b")
        at = {"b": 5, "h": 10 + nb}
        n = len(self._plates)
        lit = None if self.lit is None else self.lit % n
        for i, (w, g) in enumerate(self._plates):
            b = self.glow if i == lit else 0.0
            L = part(F.f(g), lerp(TEAL, GLOW, b), shade=lerp(TEAL_D, GLOW_D, b))
            if b > 0:
                L["glow"] = lambda x, y, e, fr, b=b: (GLOW, 0.95 * b * smooth(1.6, 0.0, e))
            out[at[w]] = L
            at[w] += 1
        return out

    def _set(self, which, P):
        got = []
        for w, t, h, hw in plate_set(self.s):
            g = blade(*on_ell(w, t), h, hw)
            if w == "h":
                g = P.hf(g)
            self._plates.append((w, g))
            if w == which:
                got.append((g, TEAL))
        return got

    def back(self, P):
        self._plates = []
        return self._set("b", P)

    def behind(self, P):
        n = len(self._plates)                           # back 이 먼저 불려 판 목록을 다 채웠다 — 머리 판만 돌려준다
        return [(g, TEAL) for w, g in self._plates[:n] if w == "h"]

    def tail_end(self, P):
        """꼬리 끝 가시 둘 — 끝 바로 앞에서 양옆으로, 꼬리 끝 쪽으로 젖혀 솟는다(V 자)"""
        s = self.s
        (ax, ay), (bx, by) = P.tail[-2], P.tail[-1]
        d = hypot(bx - ax, by - ay)
        dx, dy = (bx - ax) / d, (by - ay) / d
        # 밑동이 판에서 1.6칸 넘게 — 가늘면 먹 가시덤불이 된다. 길이는 덜 키우고 꼬리 끝 쪽으로 세운다 — 옆으로 길게 뻗으면
        # 작은 공룡 칸에서 판 밖으로 나갔다
        L = max(3.4, 2.1 / s)
        rb = max(1.5, 1.6 / s)
        rt = max(0.55, 0.6 / s)
        sp = []
        for sg in (-1, 1):
            px, py = -dy * sg, dx * sg
            ox, oy = bx - dx * 0.8, by - dy * 0.8
            tx, ty = ox + (px * 0.7 + dx * 0.72) * L, oy + (py * 0.7 + dy * 0.72) * L
            sp.append(taper(ox, oy, rb, tx, ty, rt))
        self._spk = union(*sp)
        return [(self._spk, HORN)]


class _Inner(Kind):
    """틀 몸을 그릴 때 쓰는 속 Kind(body 없음) — 갈고리는 바깥 StegoKind 것"""
    quad = True

    def __init__(self, o):
        self.o = o
        self.spots = o.spots

    def back(self, P):
        return self.o.back(P)

    def behind(self, P):
        return self.o.behind(P)

    def tail_end(self, P):
        return self.o.tail_end(P)


K = StegoKind()


def lit(i, b):
    K.lit, K.glow = i, b


def sc_arrow(fr, g):
    """날개 끝 오른쪽 아래 스테고가 왼쪽을 보고 날개 끝을 킁킁 — 등판이 앞에서 뒤로 차례로 반짝. 화살표가 맨 위"""
    ph, k = ph_k(fr)
    s = 0.90
    wx, wy = g["wing"]
    ox = min(wx + 5.4, 29.4 - 12.2 * s)                   # 등판 끝(캐논 -12 안팎)이 판 안에
    oy = min(wy + 2.8, 30.4 - 14.0 * s)                   # 발바닥(캐논 14)이 판 안에
    sniff = k % 4 in (1, 2)
    F = DF(ox, oy, s, fx=-1)
    nod = -0.42 + (0.14 if sniff else 0.0)
    lit(k // 3 % 4, (0.6, 1.0, 0.6)[k % 3])
    out = dino(F, K, "happy" if sniff else "blink" if k == 7 else "open", nod=nod, sway=0.9 * sin(ph), tail_pts=TAIL_UP)
    lit(None, 0.0)
    if sniff:
        tx, ty = snout_tip(F, K, nod)
        out += zip_lines(tx - 0.6, ty - 0.4, 2, 1.1, 1.0 + 0.3 * (k % 2), pi * 1.25, 0.8, 0.85)
    return out + arrow_layers(g)


def sc_wait(fr):
    """등판이 앞(목덜미)에서 뒤(엉덩이)로 차례로 빛남 — 빛나는 판 끝에 별이 톡, 꼬리 가시 살랑, 끝에 눈웃음"""
    ph, k = ph_k(fr)
    i, j = k // 3, k % 3
    s = 1.04
    F = DF(18.4, 12.6, s)
    lit(i, (0.55, 1.0, 0.7)[j])
    out = dino(F, K, "happy" if k >= 10 else "blink" if k == 5 else "open", nod=0.04 * sin(ph), sway=1.0 * sin(ph),
               bob=0.25 * (1 - cos(2 * ph)) / 2)
    lit(None, 0.0)
    tx, ty = F.w(*plate_tip(i, s, 0.04 * sin(ph)))
    if j == 1:
        out += star(tx - 0.6, ty - 1.4, 2.2, 0.7)
    else:
        out += star(tx - 0.4, ty - 1.0, 1.2, 0.45)
    return out


def sc_no(fr):
    """금지 표지 안에서 고개를 홱 쳐들고(흥, 눈 감음) 꼬리 가시를 위아래로 '안 돼 안 돼' — 흔들 때 줄이 튐. 표지가 위.
    머리는 빗금 오른쪽 위 삼각형에, 꼬리 가시는 왼쪽 아래에 — 빗금이 얼굴을 가리면 32 에서 아무것도 안 읽힌다"""
    ph, k = ph_k(fr)
    s = 0.62
    w = sin(2 * ph)
    F = DF(18.6, 10.4, s)
    out = dino(F, K, "blink", nod=-0.34, sway=2.6 * w, tail_pts=TAIL)
    if abs(w) > 0.7:
        tx, ty = F.w(-13.0, 6.2 + 2.6 * w)
        out += zip_lines(tx, ty, 2, 1.1, 2.6, -pi / 2 if w < 0 else pi / 2, 0.8, 0.85)
    return out + no_sign()


class Stego(DinoPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Stego(HIDE, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no}, hot={"wait": (14, 13)})

register("stego", PET)
catkit.load()

# SPDX-License-Identifier: Apache-2.0
"""아기오리(ducklinganim) 고화질 — 새 틀(birdkit)에 깃빛 · 생김새 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(지운 gen/bird.py)의 짓 그대로: 화살표를 머리에 이고 뒤뚱(화살표), 물에 둥둥 떠서 위아래로 출렁 · 물결이 번짐
(기다림 — 물 밑은 안 보인다), 넓적한 부리를 크게 벌려 꽥! 하며 날개를 들고 소리 줄이 양옆으로 퍼짐(금지).
병아리와 같은 노랑이라 32 에서 가르는 것은 넓적한 주황 부리 · 낮고 퍼진 몸 · 옆으로 솟은 꽁지다.
카나리아와 한 덩이로 읽혀서(2026-10-12 사용자) 부리를 머리 폭의 3/5 까지 키우고 몸을 낮고 넓게 했다.
물갈퀴는 몸 뒤에 그려져 몸 밑으로 나온 띠가 먹선(1칸) 두 겹보다 얇아 32 에서 까만 점이라 접었다.
"""
from . import catkit, register
from .birdkit import (Plume, Kind, BirdPet, bird, at_mid, carry_waddle, ell, inter, hx, zip_lines, no_sign, ph_k,
                      Frame, base, part, flat, chain, circle, capsule, clip_y, grow, lerp, beak_layers,
                      sin, cos, pi, OUT, P_)

D_YEL, D_YEL_D, D_YEL_L, D_BILL, D_BILL_D = hx("ffd23c"), hx("e6b028"), hx("ffe88c"), hx("f58a2a"), hx("c8641a")
PLUME = Plume(D_YEL, D_YEL_D, D_YEL_L, D_YEL, D_BILL, D_BILL_D, foot=D_BILL)
WATER, WATER_D, WATER_I = hx("bfe6f5"), hx("7cc4d8"), hx("5a9cc8")


class DuckKind(Kind):
    head = (6.6, 6.1)
    body = (8.0, 7.4, 4.6)         # 낮고 옆으로 퍼진 몸 — 늘씬한 카나리아와 반대 끝
    eye = (3.2, 0.2)
    beak_y = 3.0
    bw, bh = 4.0, 2.0              # 넓적 부리 — 반폭이 머리 반지름의 3/5 라 1배에서도 주황 띠로 남는다
    wing_l, wing_w = 2.9, 2.0
    foot_x = 3.0

    def marks(self, hv):
        """정수리만 한 톤 진한 노랑(픽셀 판 머리 맨 위 15%)"""
        return [(ell(0.0, hv - 6.9, 6.4, 2.8), D_YEL_D)]

    def tail(self):
        """오른쪽 엉덩이에서 위로 살짝 솟은 꽁지 — 몸 테 밖으로 한 줌만. 더 길게 빼면 1배에서 든 손으로 읽힌다"""
        bv, brx, bry = self.body
        return [(chain([(2.6, bv + 2.6), (brx + 0.2, bv + 1.0), (brx + 1.1, bv - 0.4)], 1.5, 0.8), D_YEL_D)]

    def wing_marks(self, w, rx, ry, a, L, sg):
        """날개 끝 반은 진한 노랑"""
        c, s = cos(a), sin(a)
        return [(lambda x, y: L * 0.55 - ((x - rx) * c + (y - ry) * s), D_YEL_D)]

    def beak(self, F, o, lu, hv, up):
        """넓적한 주황 부리 — 윗부리는 가로로 긴 둥근 판, 아랫부리는 그 밑에 조금 좁게. 벌리면 사이에 입속.
        up 이면 공용 세모 부리 — 쳐든 주걱 부리는 32px 에서 정수리에 꽂힌 당근으로 읽혔다(2026-10-12 사용자)"""
        s = F.s
        C = P_()
        bh = max(self.bh, 1.0 / s)
        ink = lerp(C.beak_d, OUT, 0.3)
        if up:                                                 # 정면 부리를 키워도 쳐든 세모는 평 받은 크기(반폭 3.1) 그대로
            return beak_layers(F, UP_K, o, lu, hv, True)
        bw = max(self.bw, 1.6 / s)
        bx, by = lu, self.beak_y + hv
        up_o, dn_o = o * bh * 0.35, o * bh * 1.0
        upper = ell(bx, by - up_o - 0.1, bw, bh * 0.68)
        lower = ell(bx, by + dn_o + 0.55, bw * 0.72, bh * 0.42)
        out = []
        if o > 0.05:
            m = ell(bx, by + (dn_o - up_o) * 0.5 + 0.2, bw * 0.72, (up_o + dn_o) * 0.5 + 0.35)
            out.append(flat(F.f(m), hx("8a2a3a"), line=0.32, ink=ink))
        out.append(part(F.f(lower), C.beak, shade=C.beak_d, line=0.32, sh=0.0, ink=ink))
        out.append(part(F.f(upper), C.beak, shade=C.beak_d, line=0.32, sh=0.0, ink=ink))   # 아랫부리도 같은 주황 — 진하게 두면 32 에서 갈색 입술 띠(햄버거)로 읽혔다
        if s >= 0.5:                                           # 콧구멍 두 점 — 128 에서만 보이는 크기
            for sg in (-1, 1):
                out.append(flat(F.f(circle(bx + sg * bw * 0.32, by - up_o - 0.45, 0.22)), C.beak_d))
        return out


K = DuckKind()


class _UpKind(DuckKind):
    bw, bh = 3.1, 1.6


UP_K = _UpKind()


def head_v(sq=0.0, puff=1.0):
    """bird() 가 sq · puff 로 머리를 내린 만큼(캐논 v) — 눈썹을 눈에 맞춰 단다"""
    bry = K.body[2]
    return (bry - bry * (1 - 0.14 * sq) * puff) * 1.5


def brows(F, hv, col=OUT):
    """화난 눈썹 — 눈 위에 안쪽이 내려온 짧은 줄"""
    ex, ey = K.eye
    out = []
    for sg in (-1, 1):
        x0, y0 = F.w(sg * (ex + 1.3), ey - 2.3 + hv)
        x1, y1 = F.w(sg * (ex - 0.8), ey - 1.4 + hv)
        out.append(flat(capsule(x0, y0, x1, y1, max(0.42, 0.32 * F.s)), col))
    return out


def sc_arrow(fr, g):
    """크림 화살표를 정수리에 이고 뒤뚱뒤뚱 — 걸음마다 날개가 살짝 들리고 가끔 꽥. 화살표가 맨 위"""
    return carry_waddle(K, fr, g)


def clipped(layers, y0):
    """레이어를 y0 아래로 잘라 낸다 — 물 밑은 안 보인다"""
    return [dict(L, f=clip_y(L["f"], y0)) for L in layers]


def sc_wait(fr):
    """물에 둥둥 — 위아래로 출렁이고 고개를 갸웃, 가끔 꽥. 물결 두 겹이 양옆으로 번진다. 물 밑은 안 보인다"""
    ph, k = ph_k(fr)
    bob = sin(ph)
    s = 0.84
    wl = 21.4                                                  # 물낯
    oy = wl + 1.6 - (K.body[0] + K.body[2]) * s + 0.7 * bob
    F = Frame(16.0, oy, s)
    quack = k in (8, 9)
    duck = bird(F, K, "blink" if k == 4 else "happy" if quack else "open", beak=0.85 if quack else 0.0,
                feet=False, look=0.6 * sin(ph), sq=-0.25 * bob)
    out = clipped(duck, wl + 0.8)
    pond = ell(16.0, wl + 3.2, 13.8, 3.8)
    out += [base(pond), part(pond, WATER, shade=WATER_D, ink=WATER_I, line=0.8)]
    inner = grow(pond, -0.9)
    for i in range(2):                                         # 번지는 물결 — 몸 둘레 고리가 커지며 옅어짐
        t = ((k + i * 6) % 12) / 12
        r = 6.4 + 6.0 * t
        rg = lambda x, y, r=r: abs((((x - 16.0) / r) ** 2 + ((y - wl - 0.9) / (r * 0.26)) ** 2) ** 0.5 - 1) * r * 0.26 - 0.32
        out.append(flat(inter(inter(rg, inner), lambda x, y: wl + 0.9 - y), WATER_D, 0.95 * (1 - t) ** 0.7))
    out.append(flat(inter(capsule(5.5, wl + 1.9, 9.5, wl + 1.9, 0.35), inner), hx("eaf7fc"), 0.9))   # 물낯 반짝
    if quack:
        hx_, hy_ = F.w(0.54 * sin(ph), K.beak_y)
        out += zip_lines(hx_ + 1.0, hy_ - 1.2, 3, 1.2, 5.6, -pi / 4, 0.6)
    return out


def sc_no(fr):
    """꽥! — 넓적한 부리를 크게 벌려 소리치고 두 날개를 번쩍(눈 질끈), 소리 줄이 양옆으로 퍼진다.
    사이 장은 부리를 다물고 몸을 웅크린 채 화난 눈썹으로 노려봄. 표지가 위"""
    ph, k = ph_k(fr)
    q = k % 4 < 2
    sq = 0.0 if q else 0.4
    F = at_mid(K, 14.5, 15.2, 0.7)
    out = bird(F, K, "squeeze" if q else "open", beak=1.0 if q else 0.0,
               wl=(("fold", "up"), 0.75 if q else 0.0), wr=(("fold", "up"), 0.75 if q else 0.0), sq=sq)
    if q:
        bx, by = F.w(0.0, K.beak_y)
        out += zip_lines(bx, by + 0.4, 3, 1.4, 6.0, pi, 0.55)
        out += zip_lines(bx, by + 0.4, 3, 1.4, 6.0, 0.0, 0.55)
    else:
        out += brows(F, head_v(sq))
    return out + no_sign()


class Duckling(BirdPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Duckling(PLUME, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no})

register("duckling", PET)
catkit.load()

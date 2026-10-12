# SPDX-License-Identifier: Apache-2.0
"""짹짹이 · 애니 고화질 공용 틀 — 앞모습 치비 새(머리와 몸이 한 덩이인 통통 새) · 스티커 채색은 냥이 틀(catkit) 그대로.

픽셀 판(지운 gen/bird.py)이 귀여운 까닭 — 둥근 머리가 몸에 그대로 이어진 콩 몸, 낮고 넓게 벌린 까만 콩 눈, 그 사이
작은 마름모 부리, 옆구리에 붙은 짧은 날개, 뭉툭한 주황 발 — 을 HD 로 옮겼다. 마리마다 다른 것은 깃빛(Plume)과
생김새(Kind — 크기 · 부리 · 볏 · 무늬 · 꼬리 갈고리)와 화살표 · 기다림 · 금지 세 칸이고, 나머지 14칸은 여기 하나다
(작은 화살표 + 작은 새 + 소품 넷 · 고개를 젖혀 부리로 콕 · 조준선 얼굴 · 나뭇가지 I · 파닥 · 기지개 넷 · 깃펜 · 만세 깡충).
좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 새 제 좌표(캐논)는 머리 가운데 (0, 0), 아래가 +v, 앞을 본다.

공룡 틀(dinokit)은 읽지 않는다 — 옆모습 몸이라 안 맞고, 읽으면 일감 해시가 그 파일을 따라가(build._pet_files)
dinokit 을 고칠 때 새 열 마리까지 다시 굽는다. 그래서 화살촉 · 땀 · 먼지 · 금지 표지 같은 작은 도우미는 베껴 왔다.
catkit 은 고치지 않는다(냥이 열 마리 재료). 깃빛은 catkit 전역 C 에 끼워 쓴다(use).
"""
import math

from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

from . import catkit
from .catkit import (hx, ell, oell, inter, clip_y, rpoly, chain, taper, Frame, layer, base, part, flat, soft,  # noqa: F401
                     cur, small_arrow, ARROW, TIP, cream_of, shaped, HI_WHITE, HI, NF, Pet, shut, Coat, use)

sin, cos, hypot, pi, atan2, radians = math.sin, math.cos, math.hypot, math.pi, math.atan2, math.radians

# 짹짹이 묶음 공통(픽셀 판 팔레트 그대로)
OUT, EYE, RIM = hx("3a2a30"), hx("2a1c22"), hx("f6e9d2")
BLUSH, MOUTH = hx("f6a8b4"), hx("8a2a3a")
SWEAT, SWEAT_D = hx("9fd4f4"), hx("5a9cc8")
DUST, DUST_D = hx("e6d6bc"), hx("c4b090")
CHEV, CHEV_D = hx("f59a5a"), hx("c8642a")
SIGN, SIGN_D, SIGN_L = hx("d64541"), hx("9e2b28"), hx("ef7a72")
SKIN, SKIN_D, SHIRT, SHIRT_D, HAIR = hx("f7d7bc"), hx("e8bfa0"), hx("4a7fb5"), hx("2e5a88"), hx("5a3a28")
SEEDS = (hx("7e5230"), hx("b08a48"), hx("e8c27a"))
WORM, WORM_D, WORM_B = hx("f6a8b4"), hx("d97890"), hx("e88aa0")
SOIL, SOIL_D = hx("9a6a40"), hx("6e4a28")
WOOD, WOOD_D, LEAF, LEAF_D = hx("b07a48"), hx("7e5230"), hx("8cc864"), hx("5a9a44")
QUILL, QUILL_D, NIB, NIB_L = hx("e6f2fa"), hx("9cc8e0"), hx("3a3a44"), hx("e8c27a")


class Plume(Coat):
    """깃빛 하나 — base(머리 · 몸) · dark(그늘 쪽) · belly(배) · wing(날개) · beak · beak_d(아랫부리 · 부리 먹) · foot(발)"""

    def __init__(self, base_, dark, belly, wing, beak, beak_d, foot=None, wing_d=None):
        super().__init__(base_, lerp(base_, dark, 0.55), OUT, EYE, RIM, ((EYE,) * 3,) * 2, cheek=BLUSH)
        self.dark, self.belly, self.wing, self.beak, self.beak_d = dark, belly, wing, beak, beak_d
        self.foot = foot or beak
        self.wing_d = wing_d or lerp(wing, OUT, 0.22)


def P_():
    return catkit.C


# ---- 마리마다 다른 것: 생김새 ----

class Kind:
    """한 마리의 생김새. 크기는 캐논 칸이고, 갈고리는 다 캐논 거리함수를 돌려준다(hv 는 머리가 내려간 만큼).
      top(hv)    머리 위 먹선 가닥(병아리 깃 · 볏 줄기) — 거리함수 목록, 먹색으로만 칠한다
      behind(hv) 머리 뒤(볏 깃) — (f, 색) 목록
      marks(hv)  머리 · 몸 위 무늬(모자 · 뺨 · 가면) — (f, 색) 목록, 덩이 안으로 잘라 납작하게
      tail()     몸 뒤 꼬리 — (f, 색) 목록
    waddle 이면 화살표를 이고 뒤뚱 걷고(병아리 · 오리 · 펭귄), 아니면 깡충 뛴다"""
    head = (7.0, 6.6)              # 머리 반지름(가로, 세로) — 가운데 (0, 0)
    body = (7.4, 6.2, 5.0)         # 몸 가운데 v · 가로 · 세로 반지름 — 발바닥은 body v + 세로 + 1.4
    eye = (3.0, 1.0)               # 눈 (±u, v)
    beak_y = 2.5
    bw, bh = 1.5, 1.7              # 부리 반폭 · 반높이
    wing_l, wing_w = 2.6, 1.9
    foot_x = 2.3
    waddle = False
    blush = True

    def top(self, hv):
        return []

    def behind(self, hv):
        return []

    def marks(self, hv):
        return []

    def tail(self):
        return []

    @property
    def feet_v(self):
        return self.body[0] + self.body[2] + 1.4

    @property
    def mid_v(self):
        """머리 꼭대기와 발바닥 가운데 — 몸 가운데를 핫스팟에 맞추는 칸이 쓴다"""
        return (self.feet_v - self.head[1]) / 2


# ---- 날개 자세 ----
# 오른쪽 날개의 캐논 방향(화면 시계 방향 라디안)과 길이 배. 왼쪽은 좌우를 뒤집는다(π - 각)

WP = {"fold": (pi / 2 - 0.5, 0.8), "out": (-0.25, 1.0), "up": (-pi / 2 + 0.6, 1.05), "down": (pi / 2 - 0.15, 0.9)}


def wing_pose(p, sg):
    """p: "fold" · "out" · "up" · "down" | ((자세, 자세), t) 섞기 | ("aim", 화면 각, 길이 배[, 앞]).
    → (캐논 각, 길이 배, 앞에 그리나)"""
    if isinstance(p, str):
        a, lm = WP[p]
    elif p[0] == "aim":
        a, lm = p[1], p[2]
        return a, lm, (p[3] if len(p) > 3 else sin(a) > -0.3)
    else:
        (pa, pb), t = p
        (a0, l0), (a1, l1) = WP[pa], WP[pb]
        a, lm = a0 + (a1 - a0) * t, l0 + (l1 - l0) * t
    if sg < 0:
        a = pi - a
    return a, lm, sin(a) > -0.3


# ---- 앞모습 치비 새 ----

def bird(F, K, mood="open", beak=0.0, wl="fold", wr="fold", sq=0.0, puff=1.0, lift=(0.0, 0.0), body=True,
         face_on=True, look=0.0, up=False, feet=True, extra=()):
    """선 치비 새 → 레이어 목록. 캐논: 머리 (0, 0) · 몸 (0, K.body v) · 발바닥 v = K.feet_v.
    mood: open · blink · happy · squeeze(><) · sad. beak 0–1 은 부리 벌림. sq 는 눌림(+) · 늘어남(-) — 발바닥은 그대로이고
    머리가 같이 내려간다. lift 는 (왼발, 오른발)을 든 만큼(캐논). body 가 거짓이면 머리만(조준선 · 핀).
    up 이면 고개를 젖혀 부리가 머리 위를 향한다(콕 칸). extra 는 머리 위에 얹을 (f, 색) 목록(캐논)"""
    s = F.s
    C = P_()
    hrx, hry = K.head[0] * puff, K.head[1] * puff
    bv, brx, bry = K.body
    bry2, brx2 = bry * (1 - 0.14 * sq) * puff, brx * (1 + 0.08 * sq) * puff
    fv = K.feet_v
    bv2 = (bv + bry) - bry2 if body else bv
    hv = (bv2 - bv) * 1.5 if body else 0.0
    head = ell(0.0, hv, hrx, hry)
    bod = ell(0.0, bv2, brx2, bry2)
    blob = smin(1.5, head, bod) if body else head
    back, front = [], []                                       # (f, 색, 그늘)
    for f, col in K.tail() if body else ():
        back.append((f, col, None))
    if body and feet:
        fy = max(0.95, 1.3 / s)
        fr = max(1.7, 1.25 / s)
        for sg, lf in ((-1, lift[0]), (1, lift[1])):
            back.append((ell(sg * K.foot_x, fv - fy - lf, fr, fy), C.foot, lerp(C.foot, C.beak_d, 0.6)))
    if body:
        r0, r1 = max(K.wing_w, 1.7 / s), max(K.wing_w * 0.7, 1.25 / s)
        for sg, p in ((-1, wl), (1, wr)):
            if p is None:
                continue
            a, lm, fr_ = wing_pose(p, sg)
            rx_, ry_ = sg * brx2 * 0.72, bv2 - bry2 * 0.3
            L = K.wing_l * lm
            w = taper(rx_, ry_, r0, rx_ + cos(a) * L, ry_ + sin(a) * L, r1)
            (front if fr_ else back).append((w, C.wing, C.wing_d))
    beh = K.behind(hv)
    tops = K.top(hv)
    mk = K.marks(hv)
    allf = [p[0] for p in back + front + beh] + tops + [blob] + [e[0] for e in extra]
    out = [base(*[F.f(g) for g in allf])]
    for g, col, sh in back:
        out.append(part(F.f(g), col, shade=sh))
    for g, col in beh:
        out.append(part(F.f(g), col))
    out.append(part(F.f(blob), C.base))
    if body:
        out.append(flat(F.f(inter(bod, grow(ell(0.0, bv2 + 0.8, brx2 * 0.68, bry2 * 0.75), 0.0))), C.belly))
    for g, col in mk:
        out.append(flat(F.f(inter(g, grow(blob, -0.9))), col))
    if face_on:
        out += bface(F, K, mood, beak, look, hv, up)
    for g, col in extra:
        out.append(part(F.f(g), col))
    for g, col, sh in front:
        out.append(part(F.f(g), col, shade=sh))
    return out


def bface(F, K, mood="open", beak=0.0, look=0.0, hv=0.0, up=False):
    """눈은 머리 가운데보다 낮고 넓게, 바로 밑 바깥쪽에 분홍 볼, 사이에 작은 마름모 부리(벌리면 위아래로 갈라짐).
    눈은 까만 콩 + 왼쪽 위 흰 반짝 — 32 에서도 2px 남게 판 단위로 바닥을 둔다"""
    s = F.s
    C = P_()
    out = []
    er = max(1.0 * s, 0.9)
    ex, ey = K.eye
    if up:                                                     # 올려다봄 — 눈이 부리 밑동 쪽으로 올라가고 32 에서 남게 조금 크게
        ex, ey, er = ex * 0.85, -2.2, max(1.15 * s, 1.1)
    lu = 0.9 * look
    if K.blush:
        for sg in (-1, 1):
            bx, by = F.w(sg * (ex + 1.1) + lu * 0.5, ey + (1.6 if up else 1.9) + hv)
            rx = max(1.2 * s, 0.85)
            out.append(soft(ell(bx, by, rx, rx * 0.6), BLUSH, 0.85))
    for sg in (-1, 1):
        x, y = F.w(sg * ex + lu, ey + hv)
        if mood == "squeeze":
            d = -sg
            w = max(0.3, 0.22 * er)
            g = union(capsule(x - d * er * 0.8, y - er * 0.75, x + d * er * 0.55, y, w),
                      capsule(x + d * er * 0.55, y, x - d * er * 0.8, y + er * 0.75, w))
            out.append(flat(g, C.eye))
        elif mood in ("blink", "happy"):
            out.append(shut(x, y, er * 1.05, mood))
        elif mood == "sad":
            out.append(flat(ell(x, y + er * 0.15, er * 0.8, er * 0.95), C.eye))
        else:
            out.append(flat(ell(x, y, er * 0.82, er), C.eye))
            if s >= 0.4:
                out.append(flat(circle(x - 0.28 * er, y - 0.36 * er, max(0.34 * er, 0.3)), HI))
    out += beak_layers(F, K, beak, lu, hv, up)
    return out


def beak_layers(F, K, o=0.0, lu=0.0, hv=0.0, up=False):
    """앞모습 부리 — 윗부리(위로 뾰족한 세모) · 아랫부리(아래로 뾰족한 세모). 벌리면 갈라지고 사이에 입속.
    up 이면 부리 하나가 머리 위로 뾰족(콕). 크기는 판에서 1칸 아래로 안 줄인다"""
    s = F.s
    C = P_()
    bw, bh = max(K.bw, 1.0 / s), max(K.bh, 1.0 / s)
    ink = lerp(C.beak_d, OUT, 0.45)
    if up:
        top = -K.head[1] + hv
        g = rpoly([(-bw * 1.15, top + 2.4), (bw * 1.15, top + 2.4), (0.0, top - 1.8 * bh)], 0.3)
        return [part(F.f(g), C.beak, shade=C.beak_d, line=0.42, sh=0.6, ink=ink)]
    bx, by = lu, K.beak_y + hv
    up_o, dn_o = o * bh * 0.3, o * bh * 0.75
    upper = rpoly([(bx - bw, by - up_o), (bx + bw, by - up_o), (bx, by - up_o - bh * 0.8)], 0.25)
    lower = rpoly([(bx - bw * 0.82, by + dn_o), (bx + bw * 0.82, by + dn_o), (bx, by + dn_o + bh)], 0.25)
    out = []
    if o > 0.05:
        m = ell(bx, by + (dn_o - up_o) * 0.5, bw * 0.7, (up_o + dn_o) * 0.5 + 0.3)
        out.append(flat(F.f(m), MOUTH, line=0.32, ink=ink))
    out.append(part(F.f(lower), C.beak_d, shade=lerp(C.beak_d, OUT, 0.25), line=0.38, sh=0.0, ink=ink))
    out.append(part(F.f(upper), C.beak, shade=C.beak_d, line=0.38, sh=0.0, ink=ink))
    return out


def hang(K, px, py, s, ang=0.0):
    """머리 꼭대기(캐논 (0, -머리 세로))가 (px, py) 에 오고 그 둘레로 ang 만큼 기운 Frame — 화살표를 인 새가 쓴다"""
    c, sn = cos(ang), sin(ang)
    t = K.head[1]
    return Frame(px - t * sn * s, py + t * c * s, s, ang)


def stand(K, cx, ground, s, ang=0.0):
    """발바닥 가운데가 (cx, ground) 에 오고 그 둘레로 ang 만큼 기운 Frame"""
    c, sn = cos(ang), sin(ang)
    t = K.feet_v
    return Frame(cx + t * sn * s, ground - t * c * s, s, ang)


def at_mid(K, cx, cy, s, ang=0.0):
    """몸 가운데(머리 꼭대기와 발바닥 사이)가 (cx, cy) 에 오는 Frame"""
    c, sn = cos(ang), sin(ang)
    t = K.mid_v
    return Frame(cx + t * sn * s, cy - t * c * s, s, ang)


# ---- 소품(공룡 틀에서 베낌 — import 하면 해시가 엮인다) ----

def chevron(cx, cy, dx, dy, L=2.4, a=1.0):
    """(dx, dy) 쪽을 가리키는 주황 화살촉 — 꼭짓점이 (cx, cy)"""
    n = hypot(dx, dy)
    dx, dy = dx / n, dy / n
    px, py = -dy, dx
    f = union(*[capsule(cx, cy, cx - dx * L + s * px * L, cy - dy * L + s * py * L, 0.72) for s in (-1, 1)])
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(CHEV, CHEV_D, smooth(0.36, 0.2, -e)), 1.0), alpha=a)]


def drop(x, y, r=1.0, h=1.4):
    """땀방울 — 꼭지가 위"""
    f = smin(0.3, circle(x, y + 0.5, r), poly([(x, y - h), (x - r * 0.8, y + 0.4), (x + r * 0.8, y + 0.4)]))
    return [base(f), part(f, lambda px, py: lerp(HI, SWEAT, smooth(y - 0.6, y + 0.8, py)), shade=SWEAT_D, ink=SWEAT_D, line=0.45)]


def puff(cx, cy, r=1.4, a=1.0):
    """먼지 퐁 — 동그라미 셋"""
    f = union(circle(cx - r * 0.7, cy + r * 0.2, r * 0.75), circle(cx + r * 0.6, cy + r * 0.25, r * 0.7), circle(cx, cy - r * 0.35, r * 0.85))
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(DUST, DUST_D, smooth(0.32, 0.15, -e)), 1.0), alpha=a)]


def zip_lines(cx, cy, n=3, L=1.6, r0=2.2, a0=-pi / 2, spread=0.7, a=0.9):
    """콕 · 삐약 할 때 튀는 짧은 줄 n 개 — (cx, cy) 둘레 a0 쪽으로 부채꼴"""
    out = []
    for i in range(n):
        t = a0 + spread * (i - (n - 1) / 2)
        x0, y0 = cx + cos(t) * r0, cy + sin(t) * r0
        out.append(flat(capsule(x0, y0, x0 + cos(t) * L, y0 + sin(t) * L, 0.26), OUT, a))
    return out


def no_sign(C_=14.5, R=12.5):
    """빨간 금지 표지(고리 + 빗금) — 새 위에 칠한다"""
    g = union(ring(C_, C_, R - 1.25, 1.25), capsule(C_ - 7.7, C_ - 7.7, C_ + 7.7, C_ + 7.7, 1.35))
    return [base(g), part(g, lambda x, y: lerp(SIGN_L, SIGN, smooth(C_ - 10, C_ - 4, y + 0.5 * x - 0.5 * C_)), shade=SIGN_D,
                          ink=SIGN_D, line=0.8)]


def ground(cx, y, w, a=0.22):
    return [layer(ell(cx, y, w, 0.75), lambda *_: (OUT, a))]


# ---- 화살표 (핫스팟 (1, 1)) ----
# 기본은 냥이 빼꼼과 같은 크림 화살표를 0.74 배로. 모양 탭이면 catkit.shaped 윤곽을 핫스팟 둘레로 0.62 배.
# 새는 화살표 꼬리(대 끝) 밑에 머리를 대고 화살표를 인다 — 화살표가 맨 위

SC = 0.74
KS = 0.62
_GEO = {}


def _scaled(f, hx_, hy_, k):
    return lambda x, y: k * f(hx_ + (x - hx_) / k, hy_ + (y - hy_) / k)


def _tail(f):
    """화살표 꼬리 끝 — 핫스팟에서 대각선(↘)으로 가장 먼 안쪽 칸들의 가운데. 0.2칸 격자로 잰다"""
    pts = [(i * 0.2, j * 0.2) for j in range(160) for i in range(160) if f(i * 0.2, j * 0.2) < 0]
    d = max(x + y for x, y in pts)
    near = [p for p in pts if p[0] + p[1] > d - 0.8]
    return sum(p[0] for p in near) / len(near), sum(p[1] for p in near) / len(near)


def _hook(f):
    """화살촉 아래 꼭지점 — 가장 낮은 안쪽 칸들의 가운데(0.2칸 격자). 꼬리가 없어 새가 여기 매달린다"""
    pts = [(i * 0.2, j * 0.2) for j in range(160) for i in range(160) if f(i * 0.2, j * 0.2) < 0]
    d = max(y for _, y in pts)
    near = [p for p in pts if p[1] > d - 0.5]
    return sum(p[0] for p in near) / len(near), d


def arrow_geo(shape=None):
    """화살표 자리 — body(몸) · outer(바깥 테) · band(흰 띠) · stem(대 끝 — 새 머리가 닿는 자리) · hot"""
    if shape not in _GEO:
        if shape:
            g0 = shaped(shape)
            hx_, hy_ = g0["hot"]
            g = dict(body=_scaled(g0["body"], hx_, hy_, KS), outer=_scaled(g0["outer"], hx_, hy_, KS),
                     band=g0["band"] * KS, hot=g0["hot"])
            g["stem"] = _tail(g["outer"])
            if shape == "dart":                         # 꼬리 없이 미늘 둘 — 아래 꼭지점에 매달림(2026-10-12 사용자)
                g["hook"] = _hook(g["outer"])
        else:
            P = [(TIP[0] + SC * x, TIP[1] + SC * y) for x, y in ARROW]
            arw = rpoly(P, 0.5)
            g = dict(body=arw, outer=arw, band=0.0, hot=(1.5, 1.5),
                     stem=((P[3][0] + P[4][0]) / 2, (P[3][1] + P[4][1]) / 2 + 0.4))
        _GEO[shape] = g
    return _GEO[shape]


def arrow_layers(g):
    if g["band"]:                                       # 스티커: 먹선 · 흰 띠 · 크림 몸
        return cur([base(g["outer"]), part(g["outer"], HI_WHITE, sh=0.0), part(g["body"], cream_of, line=0.0, sh=0.0)])
    return cur([base(g["body"]), part(g["body"], cream_of, sh=0.0)])


def carry_s(K, g, s=0.66):
    """화살표를 인 새의 크기 — 발바닥이 판 안(30.4)에 들게"""
    py = g["stem"][1] - 0.8
    return min(s, (30.4 - py) / (K.feet_v + K.head[1]))


def carry_waddle(K, fr, g, s=0.66, **kw):
    """화살표를 이고 뒤뚱 — 머리 꼭대기(대 끝 밑)를 축으로 좌우로 기울고 드는 발이 번갈아, 걸음마다 날개가 살짝 들린다"""
    ph, k = ph_k(fr)
    sw = sin(ph)
    s = carry_s(K, g, s)
    px, py = g["stem"][0], g["stem"][1] - 0.8
    F = hang(K, px, py, s, radians(6.5) * sw)
    mood = "blink" if k == 11 else "happy" if k in (3, 9) else "open"
    wl = (("fold", "out"), 0.45 * max(0.0, -sw))
    wr = (("fold", "out"), 0.45 * max(0.0, sw))
    out = bird(F, K, mood, beak=0.8 if k in (3, 4) else 0.0, wl=wl, wr=wr, sq=0.35 * abs(cos(ph)),
               lift=(1.3 * max(0.0, sw), 1.3 * max(0.0, -sw)), **kw)
    return out + arrow_layers(g)


def dangle(K, fr, g, s=0.6):
    """화살촉 아래 꼭지점에 머리 꼭대기를 대고 매달려 대롱대롱 — 두 날개를 들어 붙잡고 발을 번갈아 찬다.
    꼭지점이 판 왼쪽 끝 가까이라 몸은 오른쪽으로 기운 채(-19–-33°) 흔들린다. 화살표가 맨 위"""
    ph, k = ph_k(fr)
    sw = sin(ph)
    px, py = g["hook"]
    F = hang(K, px, py - 0.6, s, radians(-26 + 7 * sw))
    mood = "blink" if k == 11 else "happy" if k in (2, 3, 8, 9) else "open"
    kick = (1.4 * max(0.0, sin(ph * 2)), 1.4 * max(0.0, -sin(ph * 2)))
    out = bird(F, K, mood, beak=0.8 if k in (2, 3) else 0.0, wl="up", wr="up", sq=-0.4, lift=kick)
    return out + arrow_layers(g)


HOP = [  # (뜸, 눌림, 날개 듦, 기분, 부리, 먼지)
    (0, 0.0, 0.2, "open", 0, 0), (0, 0.9, 0.15, "open", 0, 0), (0, 1.8, 0.1, "happy", 0, 0), (0, -0.8, 0.6, "happy", 1, 1),
    (2, 0.8, 0.8, "happy", 1, 0), (3, 1.2, 0.6, "open", 0, 0), (2, 0.8, 0.4, "open", 0, 0), (0, 0.0, 0.5, "open", 0, 0),
    (0, 1.4, 0.3, "happy", 0, 1), (0, 0.5, 0.2, "open", 0, 0), (0, 0.0, 0.2, "open", 0, 0), (0, 0.0, 0.2, "blink", 0, 0)]


def carry_hop(K, fr, g, s=0.66, **kw):
    """화살표를 이고 통통 — 쪼그렸다가 날개를 들며 폴짝. 뜰 때는 화살표째 들려 핫스팟이 흔들리면 안 되니 새만 화살표 밑에
    붙어 눌렸다 늘어난다(발이 땅에서 뜨는 만큼 그림자만 작아짐)"""
    ph, k = ph_k(fr)
    gap, sq, wu, mood, bk, dust = HOP[k]
    s = carry_s(K, g, s)
    px, py = g["stem"][0], g["stem"][1] - 0.8
    F = hang(K, px, py, s)
    t = clamp(wu)
    out = []
    fy = py + (K.feet_v + K.head[1]) * s
    out += ground(px, min(fy + 0.6, 30.0), 3.6 - 0.5 * gap, 0.2 - 0.03 * gap)
    out += bird(F, K, mood, beak=0.8 if bk else 0.0, wl=(("fold", "up"), t), wr=(("fold", "up"), t), sq=sq - 0.25 * gap,
                lift=(0.4 * gap, 0.4 * gap), **kw)
    if dust:
        out += puff(px + 5.2, min(fy, 29.0), 0.9, 0.8)
    return out + arrow_layers(g)


# ---- 공용 14칸 ----

def ph_k(fr):
    return TAU * fr, round(fr * NF) % NF


def mini(K, fr, mood=None, look=0.6, wings=None, beak=0.0):
    """작은 화살표 밑에 머리를 댄 작은 새 — 뒤뚱이는 새는 좌우로 까딱, 아니면 날개를 살짝 들썩. 한 번 끔뻑"""
    ph, k = ph_k(fr)
    m = mood or ("blink" if k == 7 else "open")
    ang = radians(5) * sin(ph) if K.waddle else 0.0
    F = hang(K, 6.35, 12.1, 0.42, ang)
    if wings is None:
        t = 0.0 if K.waddle else 0.35 * max(0.0, sin(2 * ph))
        wings = (("fold", "out"), t)
    return bird(F, K, m, beak=beak, wl=wings, wr=wings, look=look)


def companion(K, fr, props, **kw):
    return props + mini(K, fr, **kw) + small_arrow()


def sc_busy(K, fr):
    """오른쪽 아래 씨앗 여덟 알이 원을 그리고 한 알씩 차례로 진해지며 돈다 — 새는 눈으로 따라 봄"""
    ph, k = ph_k(fr)
    cx, cy, R = 22.5, 22.0, 5.8
    head = k * 8 / NF
    out = []
    for i in range(8):
        a = TAU * i / 8 - pi / 2
        lag = (head - i) % 8
        col, al = (SEEDS[0], 1.0) if lag < 1 else (SEEDS[1], 1.0) if lag < 2 else (SEEDS[2], 1.0) if lag < 3.5 else (SEEDS[2], 0.4)
        f = oell(cx + R * cos(a), cy + R * sin(a), 1.05, 1.5, a + pi / 2)
        out.append(layer(f, lambda x, y, e, nx, ny, fr_, c=col: (lerp(c, OUT, smooth(0.42, 0.26, -e)), 1.0), alpha=al))
    return companion(K, fr, out, look=0.4 + 0.6 * sin(ph))


QWORM = [(19.0, 21.0), (19.0, 17.8), (21.2, 15.6), (24.0, 13.4), (24.2, 9.8), (21.4, 7.8), (18.2, 8.8)]


def sc_help(K, fr):
    """분홍 지렁이가 물음표 꼴로 몸을 말고 꿈틀 — 물결이 몸을 타고 지나간다. 점 자리엔 흙 한 알. 새는 갸웃"""
    ph, k = ph_k(fr)
    pts, n = [], len(QWORM)
    for i, (x, y) in enumerate(QWORM):
        a, b = QWORM[max(0, i - 1)], QWORM[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = hypot(dx, dy)
        w = 0.6 * sin(2 * ph - i * 1.2) * (0.4 if i == 0 else 1.0)       # 밑동(흙 쪽)은 덜 움직인다
        pts.append((x - dy / L * w, y + dx / L * w))
    worm = chain(pts, 1.6, 1.3)
    bx, by = (pts[1][0] + pts[2][0]) / 2, (pts[1][1] + pts[2][1]) / 2
    band = inter(worm, circle(bx, by, 1.1))
    out = [base(worm), part(worm, WORM, shade=WORM_D, ink=hx("b85a74"), line=0.85), flat(band, WORM_B)]
    hx_, hy_ = pts[-1]
    out.append(flat(circle(hx_ - 0.2, hy_ - 0.2, 0.42), EYE))                   # 지렁이 눈 하나(말린 끝)
    soil = circle(19.4, 26.6, 1.9)
    out += [base(soil), part(soil, SOIL, shade=SOIL_D, ink=SOIL_D, line=0.7)]
    return companion(K, fr, out, look=0.8, mood="blink" if k == 7 else "open")


def sc_person(K, fr):
    """사람이 손을 흔들고, 그 머리 위에 같은 새가 작게 앉아 날개를 같이 파닥 — 작은 새는 올려다보며 눈웃음"""
    ph, k = ph_k(fr)
    cx, cy = 23.0, 21.0
    wave = abs(sin(ph))
    hand = (cx + 6.0, cy - 2.4 - 2.2 * wave)
    torso = clip_y(ell(cx, cy + 9.0, 6.4, 5.4), 30.4)
    sleeve = capsule(cx + 3.6, cy + 5.2, hand[0], hand[1] + 0.6, 1.5)
    hd_ = ell(cx, cy, 4.4, 4.2)
    hair = inter(ell(cx, cy - 0.6, 4.9, 4.4), lambda x, y: y - (cy - 1.0 + 0.3 * abs(x - cx)))     # 앞머리 — 이마 위만
    hnd = circle(*hand, 1.5)
    out = [base(torso, sleeve, hd_, hair, hnd)]
    out += [part(torso, SHIRT, shade=SHIRT_D), part(hd_, SKIN, shade=SKIN_D), part(hair, HAIR, shade=hx("3e2618")),
            part(sleeve, SHIRT, shade=SHIRT_D), part(hnd, SKIN, shade=SKIN_D)]
    for sg in (-1, 1):
        out.append(flat(ell(cx + sg * 1.5, cy + 0.9, 0.5, 0.66), EYE))
        out.append(soft(ell(cx + sg * 2.4, cy + 2.3, 0.85, 0.5), BLUSH, 0.85))
    out.append(flat(arc(cx, cy + 1.9, 0.8, 0.2, pi * 0.15, pi * 0.7), OUT))
    t = 0.75 * wave                                                     # 머리 위 새 — 사람 손과 같이 파닥
    F = stand(K, cx - 0.2, cy - 3.9, 0.4)
    out += bird(F, K, "happy" if k % 6 in (2, 3) else "open", wl=(("fold", "up"), t), wr=(("fold", "up"), t),
                beak=0.8 if k % 6 in (2, 3) else 0.0)
    return companion(K, fr, out, look=1.0, mood="happy" if k % 6 in (2, 3) else "blink" if k == 9 else "open")


def sc_pin(K, fr):
    """빨간 지도 핀 속에 새 얼굴 — 핀이 통통, 땅에 닿을 때 눈웃음"""
    ph, k = ph_k(fr)
    hop = abs(sin(pi * fr))
    cx, cy = 22.8, 14.2 - 2.6 * hop
    out = ground(23.0, 29.2, 3.4 - 0.8 * hop)
    f = smin(1.0, circle(cx, cy, 5.8), poly([(cx - 4.7, cy + 2.7), (cx + 4.7, cy + 2.7), (cx, cy + 11.6)]))
    out += [base(f), part(f, lambda x, y: lerp(SIGN_L, SIGN, smooth(cy - 5, cy - 1.5, y + 0.6 * (x - cx))), shade=SIGN_D, ink=SIGN_D)]
    s = 0.6
    F = Frame(cx, cy + 0.3 - 0.4 * s, s * 0.95)
    out += bird(F, K, "happy" if hop < 0.3 else "open", body=False)
    return companion(K, fr, out, look=0.8)


PECK = [0.4, 0.8, 1.0, -0.6, 0.0, 0.8, 1.0, -0.6, -0.3, 0.0, 0.0, 0.0]   # + 눌림 · - 쭉 뻗어 콕
HAND_HOT = (15, 1)


def sc_hand(K, fr, hot=HAND_HOT):
    """고개를 젖혀 부리 끝으로 위를 콕콕 — 그 끝이 핫스팟이고 장마다 그대로. 콕 할 때 몸이 쭉 늘고 줄이 튄다"""
    ph, k = ph_k(fr)
    p = PECK[k]
    s = 0.84
    hx_, hy_ = hot[0] + 0.5, hot[1] + 0.9
    sq = p
    bry = K.body[2]
    hv = ((K.body[2] - bry * (1 - 0.14 * sq)) * 1.5)
    bh = max(K.bh, 1.0 / s)
    tip_v = -K.head[1] + hv - 1.8 * bh
    F = Frame(hx_, hy_ - tip_v * s, s)
    mood = "squeeze" if p < -0.4 else "blink" if k == 10 else "happy" if p > 0.7 else "open"
    t = 0.7 if p < -0.4 else 0.0
    out = []
    if p < -0.4:
        out += zip_lines(hx_, hy_, 2, 1.3, 2.2, -pi / 2, 1.9)
    out += bird(F, K, mood, up=True, sq=sq, wl=(("fold", "out"), t), wr=(("fold", "out"), t))
    return out


def sc_cross(K, fr, C_=15.5):
    """새 얼굴이 조준선 — 부리 가운데가 핫스팟, 머리 위 깃 한 가닥이 위 조준선, 턱 밑 · 양옆으로 짧은 줄. 한 번 끔뻑"""
    ph, k = ph_k(fr)
    s = 0.92
    F = Frame(C_, C_ - K.beak_y * s, s)
    top = C_ - (K.beak_y + K.head[1]) * s
    bot = C_ + (K.head[1] - K.beak_y) * s
    lines = union(capsule(1.6, C_, 5.6, C_, 0.5), capsule(25.4, C_, 29.4, C_, 0.5),
                  capsule(C_, bot + 1.6, C_, 29.4, 0.5), capsule(C_, 1.6, C_, top - 1.6, 0.5))
    out = [base(lines), flat(lines, OUT)]
    out += bird(F, K, "blink" if k == 8 else "open", body=False, look=0.25 * sin(ph))
    return out


def sc_ibeam(K, fr, X=7.5):
    """세로로 선 I 꼴 나뭇가지 오른쪽에서 고개를 갸웃갸웃. 핫스팟은 줄기 가운데"""
    ph, k = ph_k(fr)
    tilt = (0, 0, 7, 9, 9, 7, 0, 0, -7, -9, -9, -7)[k]
    stem = rbox(X, 15.0, 1.3, 11.0, 0.5)
    bars = union(rbox(X, 4.0, 4.2, 1.2, 0.6), rbox(X, 26.0, 4.2, 1.2, 0.6))
    I = union(stem, bars)
    leaf = union(oell(X + 5.0, 2.2, 1.5, 0.8, -0.5), oell(X - 4.8, 27.9, 1.4, 0.75, 0.4))
    F = stand(K, 22.6, 23.6, 0.6, radians(tilt))
    out = [base(I, leaf), part(I, WOOD, shade=WOOD_D, ink=hx("5a3a20"), line=0.8), part(leaf, LEAF, shade=LEAF_D, ink=hx("3f7a32"), line=0.5)]
    for y in (10.0, 19.0):
        out.append(flat(capsule(X - 0.6, y - 0.3, X + 0.3, y + 0.4, 0.18), WOOD_D))
    out += bird(F, K, "blink" if k == 6 else "happy" if abs(tilt) == 9 else "open", look=-0.8)
    return out


def sc_move(K, fr):
    """제자리에서 날개를 위아래로 파닥 — 네 방향 주황 화살촉이 바깥으로 두근. 몸 가운데가 핫스팟"""
    ph, k = ph_k(fr)
    o = 0.6 if k % 6 < 3 else 0.0
    out = []
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        out += chevron(15.5 + dx * (13.4 + o), 15.5 + dy * (13.4 + o), dx, dy, 2.2, 1.0 if o else 0.75)
    t = 0.5 + 0.5 * cos(2 * ph)
    F = at_mid(K, 15.5, 15.8 - 0.6 * t, 0.62)
    out += bird(F, K, "happy" if t > 0.5 else "open", wl=(("out", "up"), t), wr=(("out", "up"), t),
                beak=0.8 if k % 6 == 0 else 0.0)
    return out


AXES = {"ns": (-pi / 2, pi / 2, 13.2), "we": (0.0, pi, 13.2), "nwse": (pi / 4, -3 * pi / 4, 11.2), "nesw": (-pi / 4, 3 * pi / 4, 11.2)}


def sc_stretch(K, fr, axis):
    """기지개 — 두 날개를 축 양쪽으로 쭉 뻗었다 접었다(뻗을 때 눈 질끈). 축 양끝 화살촉이 두근. 몸 가운데가 핫스팟"""
    ph, k = ph_k(fr)
    ar, al, R = AXES[axis]
    t = 0.5 + 0.5 * sin(ph)
    lm = 1.15 + 0.6 * t
    out = []
    o = 0.6 if t > 0.6 else 0.0
    for a in (ar, al):
        out += chevron(15.5 + cos(a) * (R + o), 15.5 + sin(a) * (R + o), cos(a), sin(a), 2.2, 1.0 if o else 0.75)
    F = at_mid(K, 15.5, 15.6, 0.62)
    out += bird(F, K, "squeeze" if t > 0.6 else "open", wl=("aim", al, lm, True), wr=("aim", ar, lm, True), sq=-0.5 * t)
    return out


PEN_HOT = (1, 29)


def sc_pen(K, fr, hot=PEN_HOT):
    """제 몸만 한 깃펜을 비스듬히 쥐고 쓰는 새 — 펜촉이 왼쪽 아래 끝이자 핫스팟. 펜과 새가 펜촉 둘레로 살랑"""
    ph, k = ph_k(fr)
    nib = (hot[0] + 0.55, hot[1] + 0.5)
    rock = radians(3) * sin(ph)
    back = (25.0, 5.0)
    dx, dy = back[0] - nib[0], back[1] - nib[1]
    L = hypot(dx, dy)
    c, sn = cos(rock), sin(rock)
    ux, uy = (dx * c - dy * sn) / L, (dx * sn + dy * c) / L
    px, py = -uy, ux                                           # 깃 오른쪽(아래)
    shaft = taper(nib[0], nib[1], 0.25, nib[0] + ux * L, nib[1] + uy * L, 0.45)
    vx, vy = nib[0] + ux * L * 0.66, nib[1] + uy * L * 0.66
    vane = oell(vx + px * 0.5, vy + py * 0.5, L * 0.36, 2.4, atan2(uy, ux))
    tipz = taper(nib[0], nib[1], 0.3, nib[0] + ux * 3.2, nib[1] + uy * 3.2, 0.95)

    def qcol(x, y):
        t = (x - nib[0]) * ux + (y - nib[1]) * uy
        return QUILL if (x - vx) * px + (y - vy) * py < 0.4 or t < 0 else lerp(QUILL, QUILL_D, 0.5)
    out = [base(vane, shaft, tipz), part(vane, qcol, shade=QUILL_D, ink=hx("6a8aa0"), line=0.6),
           flat(shaft, hx("d8e6f0"), line=0.25, ink=hx("6a8aa0")),
           part(tipz, lambda x, y: NIB if (x - nib[0]) * ux + (y - nib[1]) * uy < 1.6 else NIB_L, shade=NIB, ink=NIB, line=0.4, sh=0.0)]
    s = 0.6
    bx, by = 21.4, 22.6
    F = at_mid(K, bx, by, s, rock * 2)
    sx, sy = F.w(-K.body[1] * 0.72, K.body[0] - K.body[2] * 0.3)       # 왼 어깨
    gx, gy = nib[0] + ux * L * 0.42, nib[1] + uy * L * 0.42            # 쥐는 자리
    lm = max(1.0, (hypot(gx - sx, gy - sy) - 0.6) / s / K.wing_l)
    out += bird(F, K, "blink" if k == 4 else "happy" if k in (8, 9) else "open", look=-0.7,
                wl=("aim", atan2(gy - sy, gx - sx) - rock * 2, lm, True), wr="fold")
    return out


UP_HOT = (15, 1)


def sc_up(K, fr, hot=UP_HOT):
    """머리 위 주황 위쪽 화살촉을 올려다보며 두 날개를 V 로 들고 깡충 — 뜰 때 눈웃음 · 부리 벌림. 화살촉 끝이 핫스팟"""
    ph, k = ph_k(fr)
    hop = (0, 0, 1, 2, 3, 2, 1, 0, 0, 0, 0, 0)[k] * 0.6
    X = hot[0] + 0.5
    out = chevron(X, hot[1] + 0.95, 0, -1, 2.6, 1.0 if hop else 0.8)
    t = 0.55 + 0.45 * min(1.0, hop)
    out += ground(X, 29.4, 6.0 - hop, 0.18 if hop else 0.26)
    F = stand(K, X, 29.0 - hop, 0.9)
    sp = 0.5
    out += bird(F, K, "happy" if hop >= 1.0 else "blink" if k == 9 else "open", beak=0.8 if hop >= 1.0 else 0.0,
                wl=("aim", -pi / 2 - sp, 1.55 * t, False), wr=("aim", -pi / 2 + sp, 1.55 * t, False),
                sq=0.9 * abs(sin(ph)) - 0.2 if not hop else -0.4)
    return out


SHARED = {"busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "hand": sc_hand, "cross": sc_cross,
          "ibeam": sc_ibeam, "move": sc_move, "pen": sc_pen, "up": sc_up,
          "ns": lambda K, fr: sc_stretch(K, fr, "ns"), "we": lambda K, fr: sc_stretch(K, fr, "we"),
          "nwse": lambda K, fr: sc_stretch(K, fr, "nwse"), "nesw": lambda K, fr: sc_stretch(K, fr, "nesw")}

HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1), "cross": (15, 15),
       "hand": HAND_HOT, "ibeam": (7, 14), "move": (15, 15), "nesw": (15, 15), "nwse": (15, 15), "no": (14, 14),
       "ns": (15, 15), "pen": PEN_HOT, "up": UP_HOT, "we": (15, 15), "wait": (15, 15)}


class BirdPet(Pet):
    """짹짹이 결 하나 — plume(깃빛) · kind(생김새) · own(arrow · wait · no 장면, fr[, g] → 레이어) · hot(칸 → art 칸).
    own 의 arrow 는 (fr, g) 를 받는다 — g 는 arrow_geo(모양) 라 모양 탭도 같은 함수가 그린다.
    shared 를 주면 공용 칸을 마리 것으로 바꿔 끼운다(이름 → (K, fr) → 레이어)"""
    M = 1.8

    def __init__(self, plume, kind, own, hot=None, shared=None):
        super().__init__(plume, {}, dict(HOT, **(hot or {})))
        self.kind, self.own = kind, own
        self.shared = dict(SHARED, **(shared or {}))

    def cell(self, name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
        use(self.coat)
        if name == "arrow":
            g = arrow_geo(shape)
            if "hook" in g:
                return dangle(self.kind, frame, g), g["hot"]
            return self.own["arrow"](frame, g), g["hot"]
        ax, ay = self.hot[name]
        if name in self.own:
            return self.own[name](frame), (ax + 0.5, ay + 0.5)
        return self.shared[name](self.kind, frame), (ax + 0.5, ay + 0.5)

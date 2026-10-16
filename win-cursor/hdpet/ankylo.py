# SPDX-License-Identifier: Apache-2.0
"""아기 안킬로사우루스(ankyloanim) 고화질 — 공룡 틀(dinokit)에 몸빛 · 생김새 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(지운 gen/dino.py)의 짓 그대로: 화살표를 올려다보며 꼬리 곤봉을 통통 · 먼지 퐁(화살표),
곤봉을 들었다 땅에 쿵 · 먼지 퐁(기다림), 홱 돌아서 고개를 쳐들고 곤봉만 탁탁(금지).

선 치비 틀(dino)은 다리가 머리 밑에 모여 있어 등 갑옷을 얹으면 큰 머리에 거의 다 가린다. 그래서 몸은 Kind.body 로
이 모듈이 그린다 — 머리 · 턱 · 얼굴은 틀과 같은 캐논 자리(머리 (0, 0), 발바닥 v 13.8)라 공용 14칸의 핫스팟 셈
(snout_tip · 발 디딤)이 그대로 맞고, 몸만 머리 뒤로 낮고 넓게 눕혀 네 발 · 크림 가시 줄 등 갑옷 · 꼬리 곤봉을 단다.
매끈한 돔이면 거북이로 읽혀서 등 가시 줄과 곤봉이 그걸 가른다 — 곤봉은 작아도 판에서 2칸 남짓, 꼬리보다 짙고 굵게.
공용 칸은 꼬리를 TAIL_UP(판이 좁은 칸)으로 주는데 그 점은 갑옷 속에 묻히므로 곤봉을 등 뒤 위로 치켜든 ANK_UP 로 바꿔 그린다.
"""
from . import catkit, register
from .dinokit import (DF, Hide, Kind, DinoPet, Pose, TAIL_UP, dface, no_sign, arrow_layers, ph_k, puff, zip_lines,
                      H, LINE_IN, hx, ell, inter, chain, circle, smin, rpoly, grow, lerp, base, part, flat,
                      sin, cos, pi, hypot)

HIDE = Hide(hx("dcc092"), hx("a8794e"), hx("f3e4c4"), hx("f6ead0"))      # 픽셀 판 C["ankylo"] — 몸 · 짙은 · 배 · 덧
ARMOR, ARMOR_D = hx("bc8c5a"), hx("8a6040")                               # 갑옷 · 이음매(픽셀 판 ARMOR)
CLUB, CLUB_D = hx("f6ead0"), hx("dcc8a0")          # 곤봉은 뼈 혹 크림 — 짙게 하면 32 에서 등 위 짙은 덩이(원숭이 몸)로 읽혔다

# 몸(캐논) — 머리 뒤 아래로 낮고 넓게
BODY = (-2.8, 9.2, 6.2, 4.0)
SHELL = (-3.2, 7.4, 6.4, 4.4)                     # 등 갑옷 타원, 아래는 SHELL_Y 에서 자름
SHELL_Y = 10.0
LEGS = (-6.6, -4.8, 0.4, 2.2)                     # 먼 뒷발 · 가까운 뒷발 · 먼 앞발 · 가까운 앞발(u)

# 꼬리(캐논) — 뿌리는 갑옷 뒤 밑
ANK_TAIL = [(-8.6, 9.8), (-11.4, 10.4), (-13.6, 10.0), (-15.0, 8.6)]
ANK_UP = [(-8.4, 9.4), (-10.8, 7.4), (-11.0, 3.6), (-8.8, 0.6)]          # 곤봉을 등 뒤 위로 치켜듦 — 판이 좁은 칸


def tail(h, sway=0.0):
    """h 0 은 곤봉이 땅에(끝 v 10.6 + 반지름 ≈ 발바닥), 1 은 등 뒤로 높이 든 것"""
    return [(-8.6, 9.8), (-11.2, 10.2 - 1.6 * h), (-13.0, 9.6 - 4.4 * h + 0.5 * sway), (-13.8 + 2.4 * h, 10.6 - 8.8 * h + sway)]


def club_r(s):
    return max(2.6, 1.9 / s)                      # 판에서 1.9칸 넘게 — 먹 덩어리가 안 되고 꼬리 끝보다 확 굵다


def ankylo(F, K, mood="open", nod=0.0, mouth=0.0, arm=0.0, arm_far=None, step=0.0, sway=0.0, tail_pts=None,
           look=0.0, bob=0.0, face_on=True):
    """네 발 안킬로 → 레이어. dino() 와 같은 인자(arm 은 가까운 앞발을 든 정도)"""
    s = F.s
    C = H()
    P = Pose(nod, sway=sway, step=step)
    if tail_pts is None:
        tp = [(u, v + sway * (i / 3) ** 2) for i, (u, v) in enumerate(ANK_TAIL)]
    elif tail_pts is TAIL_UP:
        tp = [(u - 0.4 * sway * (i / 3) ** 2, v) for i, (u, v) in enumerate(ANK_UP)]
    else:
        tp = list(tail_pts)
    P.tail = tp
    fy = max(1.4, 1.6 / s)
    fw = max(2.0, 1.7 / s)
    by = BODY[1] + bob * 0.4
    body = ell(BODY[0], by, BODY[2] + bob * 0.3, BODY[3] - bob * 0.3)
    hd_c = K.head
    head = P.hf(smin(1.4, ell(*hd_c), ell(*K.snout)))

    # 등 갑옷: 아래를 자른 낮은 타원 + 윗변에 크림 가시 줄(바깥 법선으로), 크면 아래 테에 옆 가시
    sx, sy, srx, sry = SHELL
    sy += bob * 0.4
    shell = inter(ell(sx, sy, srx, sry), lambda x, y: y - SHELL_Y - bob * 0.3)
    L, W = max(3.0, 2.2 / s), max(2.2, 1.7 / s)        # 세모 안쪽 반지름이 먹선보다 작으면 다 먹이라 크게 + 먹선 얇게(아래)
    angs = (114, 136, 158) if s < 0.7 else (112, 130, 148, 166)
    spikes = []
    for a in angs:
        t = a * pi / 180
        px, py = sx + (srx - 0.5) * cos(t), sy - (sry - 0.5) * sin(t)
        nx, ny = cos(t) / srx, -sin(t) / sry
        n = hypot(nx, ny)
        nx, ny = nx / n, ny / n
        spikes.append([(px - ny * W, py + nx * W), (px + nx * (L + 0.5), py + ny * (L + 0.5)), (px + ny * W, py - nx * W)])
    if s >= 0.7:                                           # 옆구리 가시 — 갑옷 아래 테에서 아래로
        for u, d in ((-8.4, -0.7), (-1.4, 0.15)):
            spikes.append([(u - 1.3, SHELL_Y - 0.8), (u + d * 2.2, SHELL_Y + 2.0), (u + 1.3, SHELL_Y - 0.8)])
    spk = [rpoly(p, min(0.45, 0.3 * W)) for p in spikes]

    # 곤봉: 끝점 둘레 둥근 덩이 + 끝 방향으로 덧 덩이(옆에서 본 두 쪽 곤봉)
    (ax, ay), (ex, ey) = tp[-2], tp[-1]
    dx, dy = ex - ax, ey - ay
    n = hypot(dx, dy) or 1.0
    dx, dy = dx / n, dy / n
    cr = club_r(s)
    club = smin(0.6, circle(ex, ey, cr), circle(ex + dx * cr * 0.5 - dy * cr * 0.3, ey + dy * cr * 0.5 + dx * cr * 0.3, cr * 0.78))
    club_front = ey < sy - sry + 3.0                      # 등 뒤 위로 든 곤봉은 갑옷 앞에 칠한다

    tl = chain(tp, max(1.9, 1.7 / s), max(1.0, 1.2 / s))
    lift = max(0.0, arm) * 0.7
    far = [(ell(LEGS[0] - step, 13.8 - fy, fw, fy), C.far), (ell(LEGS[2] - step * 0.5, 13.8 - fy, fw * 0.95, fy), C.far)]
    near = [(ell(LEGS[1] + step, 14.0 - fy, fw, fy), C.base),
            (ell(LEGS[3] + step * 0.5, 14.0 - fy - lift, fw * 0.95, fy), C.base)]

    allf = [tl, club, body, shell, head] + spk + [p[0] for p in far + near]
    out = [base(*[F.f(g) for g in allf])]
    out.append(part(F.f(tl), C.base))
    if not club_front:
        out.append(part(F.f(club), CLUB, shade=CLUB_D))
    for g, col in far:
        out.append(part(F.f(g), col))
    out.append(part(F.f(body), C.base))
    out.append(flat(F.f(inter(grow(body, -LINE_IN), ell(-1.6, by + 3.4, 5.2, 2.6))), C.belly))      # 배
    for g, col in near:
        out.append(part(F.f(g), col))
    for g in spk:
        out.append(part(F.f(g), C.deco, shade=C.deco_d, line=0.55))
    out.append(part(F.f(shell), ARMOR, shade=lerp(ARMOR, ARMOR_D, 0.7)))
    if s >= 0.8:                                           # 갑옷 이음매 — 윗변 따라 한 줄 + 짧은 세로 셋. 작으면 얼룩이라 뺀다
        e_in = ell(sx, sy + 0.4, srx - 2.0, sry - 1.6)
        seam = inter(e_in, lambda x, y: -e_in(x, y) - 0.6)
        out.append(flat(F.f(inter(seam, lambda x, y: y - SHELL_Y + 1.2)), ARMOR_D))
        for a in angs[:-1]:
            t = (a + 9) * pi / 180
            x0, y0 = sx + (srx - 0.9) * cos(t), sy - (sry - 0.9) * sin(t)
            x1, y1 = sx + (srx - 2.2) * cos(t), sy + 0.4 - (sry - 2.0) * sin(t)
            out.append(flat(F.f(chain([(x0, y0), (x1, y1)], 0.3)), ARMOR_D))
    if club_front:
        out.append(part(F.f(club), CLUB, shade=CLUB_D))
    if s * cr >= 2.2:                                      # 곤봉 혹(갑옷 빛 점)
        out.append(flat(F.f(circle(ex - cr * 0.25, ey - cr * 0.25, cr * 0.3)), ARMOR))
    out.append(part(F.f(head), C.base))
    chin = P.hf(inter(smin(1.4, ell(*hd_c), ell(*K.snout)), ell(4.6, 5.0, 5.6, 2.6)))
    out.append(flat(F.f(grow(chin, -LINE_IN)), C.belly))
    spot = lerp(C.base, ARMOR, 0.6)
    for u, v, r in (K.spots if s >= 0.55 else ()):        # 머리 위 갑옷 조각 — 작으면 얼룩이라 뺀다
        out.append(flat(F.f(P.hf(inter(circle(u, v, r), grow(ell(*hd_c), -1.2)))), spot))
    if face_on:
        out += dface(F, K, P, mood, mouth, look)
    return out


class AnkyloKind(Kind):
    quad = True
    snout = (3.4, 1.8, 4.2, 3.2)

    def body(self, F, K, **kw):
        return ankylo(F, K, **kw)


K = AnkyloKind()


def ground_puffs(F, s, end):
    """곤봉이 땅에 닿은 장에 곤봉 밑 양옆으로 먼지 퐁"""
    ex, _ = F.w(*end)
    _, gy = F.w(0.0, 13.8)
    r = max(0.9, 1.5 * s)
    return puff(ex - 2.3 * r, gy - 0.6 * r, r, 0.9) + puff(ex + 2.1 * r, gy - 0.5 * r, r * 0.85, 0.85)


def sc_arrow(fr, g):
    """화살표 날개 오른쪽 아래에서 왼쪽 위 화살표를 올려다보며 꼬리 곤봉을 통통 — 땅에 닿으면 먼지 퐁 · 눈웃음. 화살표가 맨 위"""
    ph, k = ph_k(fr)
    s = 0.82
    h = abs(sin(ph))
    wx, wy = g["wing"]
    r = max(0.9, 1.5 * s)                                    # ground_puffs 의 먼지 크기
    ox = min(wx + 9.0, 30.6 - 13.8 * s - max(club_r(s) * s, 3.4 * r))   # 곤봉 끝 · 오른쪽 먼지(곤봉 + 3.2r)가 판 안에
    oy = min(wy + 4.0, 30.4 - 13.8 * s)                      # 발바닥이 판 안에
    F = DF(ox, oy, s, fx=-1)
    tp = tail(h)
    out = ground_puffs(F, s, tp[-1]) if h < 0.3 else []
    out += K.body(F, K, mood="happy" if h < 0.3 else "open", nod=-0.3, look=0.8, tail_pts=tp, bob=0.4 * (1 - h))
    return out + arrow_layers(g)


def sc_wait(fr):
    """곤봉을 등 뒤로 높이 들었다 땅에 쿵 — 닿을 때 먼지 퐁 · 몸이 살짝 눌리고 눈웃음"""
    ph, k = ph_k(fr)
    h = abs(sin(ph))
    s = 0.96
    F = DF(19.4, 12.2, s)
    tp = tail(h)
    out = ground_puffs(F, s, tp[-1]) if h < 0.3 else []
    out += K.body(F, K, mood="happy" if h < 0.3 else "blink" if k == 4 else "open", nod=0.06 * (1 - h),
                  tail_pts=tp, bob=0.5 * (1 - h), look=-0.5 * h)
    return out


def sc_no(fr):
    """금지 표지 안 오른쪽 위에서 홱 돌아서(왼쪽을 봄) 고개를 쳐들고 눈 감은 채, 치켜든 곤봉으로 표지 테만 탁탁 —
    닿을 때 줄이 튄다. 표지가 위"""
    ph, k = ph_k(fr)
    t = abs(sin(2 * ph))
    s = 0.62
    F = DF(13.8, 8.8, s, fx=-1)
    tp = [(-8.6, 9.6), (-11.0, 8.4), (-12.6, 5.4 - 1.0 * t), (-12.4 - 0.8 * t, 2.6 - 2.6 * t)]
    out = K.body(F, K, mood="blink", nod=-0.32, tail_pts=tp)
    if t > 0.85:
        ex, ey = F.w(*tp[-1])
        out += zip_lines(ex, ey, 2, 1.0, club_r(s) * s + 0.8, -pi / 4, 1.1, 0.85)
    return out + no_sign()


class Ankylo(DinoPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Ankylo(HIDE, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no})

register("ankylo", PET)
catkit.load()

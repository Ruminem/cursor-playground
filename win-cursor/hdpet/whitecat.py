# SPDX-License-Identifier: Apache-2.0
"""오드아이 흰냥(whitecatanim) 고화질 — 치비(머리가 몸만 한 통통 냥) · 스티커 채색(고른 먹선 1칸 + 셀 그늘 한 단).

픽셀 흰냥(지운 gen/whitecat.py)이 귀여운 까닭(넓적한 머리 · 낮고 넓게 벌어진 짝짝이 눈 · 눈 바로 밑 분홍 볼 · 작은 분홍 코 ·
새하얀 납작한 털)을 HD 로 옮겼다. 칸마다 하는 짓도 픽셀 판 그대로다(우유 핥기 · 우유 물음표 · 발바닥 하이파이브 · 기지개).
화살표는 크림 화살표 빗변 뒤에서 고개를 내밀고 앞발 둘을 빗변에 건 빼꼼이다 — 몸에 얼굴을 넣은 판(공룡 등가시로 읽힘)과
귀 끝이 곧 화살 끝인 판(어디를 가리키는지 흐림)은 시안에서 접었다(2026-10-11).
좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 장면은 NF 장으로 나뉘어 있다(k = round(fr × NF) % NF).
틀(먹선 · 치비 몸 · 빼꼼 · 기지개 · 모양 화살표)은 냥이 묶음이 같이 쓰는 catkit 에 있고 여기는 털빛 · 소품 · 장면만 둔다.
"""
from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

from . import catkit, register
from .catkit import *  # noqa: F401,F403

# 픽셀 판 팔레트(지운 gen/whitecat.py) 그대로
OUT, EYE = hx("3c4052"), hx("252836")
WHITE, SHADE = hx("fcfdff"), hx("dde3ee")
BLUE, BLUE_D, BLUE_L = hx("4a9bf0"), hx("2a68c4"), hx("8cc4ff")
GOLD, GOLD_D, GOLD_L = hx("f0bb2a"), hx("bf8410"), hx("ffe07a")
NOSE, CHEEK, RIM = hx("e27d90"), hx("f7a3b5"), hx("e6e8f0")
MILK, MILK_D = hx("ffffff"), hx("dbe8f5")
DISH, DISH_D, DISH_L = hx("6f9fd8"), hx("4b77b4"), hx("a8c8ee")
CHALK, CHALK_L, CHALK_D = hx("8ec4f4"), hx("c8e2fa"), hx("5d97d2")
SHIRT, SHIRT_D, SKIN, HAIR = hx("e88f7a"), hx("c46d5a"), hx("f7d7bc"), hx("5a4034")
SIGN, SIGN_D, SIGN_L = hx("d64541"), hx("9e2b28"), hx("ef7a72")

COAT = Coat(WHITE, SHADE, OUT, EYE, RIM, ((BLUE, BLUE_D, BLUE_L), (GOLD, GOLD_D, GOLD_L)), cheek=CHEEK, nose=NOSE)

# 픽셀 판 핫스팟(art 칸) 그대로 — 적용한 사람의 손에 익은 자리
HOT = {"arrow": (1, 1), "busy": (1, 1), "cross": (15, 15), "hand": (7, 1), "help": (1, 1), "ibeam": (7, 14),
       "move": (15, 15), "nesw": (13, 13), "no": (14, 14), "ns": (5, 15), "nwse": (13, 13), "pen": (1, 22),
       "person": (1, 1), "pin": (1, 1), "up": (6, 1), "wait": (10, 14), "we": (15, 8)}




# ---- 소품: 우유 ----

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



# ---- 칸마다 장면 (art 좌표, 화살표 칸은 catkit 빼꼼) ----



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


PINK_L, SOFTINK = hx("ffd3dc"), hx("e690a3")   # 발도장 위쪽 연분홍 · 옅은 테


def curl(ph, n=9):
    """둥근 S 꼬리 — 3차 베지어를 점 n 개로 떠서 chain 이 기역 자로 꺾이지 않게"""
    p0, p1, p2, p3 = (3.6, 10.4), (10.2, 11.8), (11.0, 5.2), (8.0 + 0.9 * sin(ph), 1.8 + 0.3 * sin(ph))
    out = []
    for i in range(n):
        t = i / (n - 1)
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def soft_print(bx, by, a=1.0, sq=0.0):
    """말랑 발도장 — 옅은 테 · 위는 연분홍 아래로 볼 분홍 · 젤리마다 흰 윤 한 점. sq 는 꾹 눌려 납작해지는 정도"""
    kx, ky = 1 + 0.12 * sq, 1 - 0.14 * sq

    def grad(cy, h):
        return lambda x, y: lerp(PINK_L, CHEEK, smooth(cy - h, cy + h, y))
    mf = smin(0.6, ell(bx, by + 0.95 * ky, 2.05 * kx, 1.45 * ky), ell(bx, by + 1.7 * ky, 1.25 * kx, 0.9 * ky))
    out = [flat(mf, grad(by + 0.9 * ky, 1.6 * ky), a, line=0.22, ink=SOFTINK),
           soft(ell(bx - 0.75 * kx, by + 0.45 * ky, 0.55, 0.35), HI, 0.8 * a)]
    for tx, ty, r in ((-2.75, -1.35, 0.82), (-0.95, -2.55, 0.9), (0.95, -2.55, 0.9), (2.75, -1.35, 0.82)):
        cx, cy = bx + tx * kx, by + ty * ky
        out.append(flat(ell(cx, cy, r * kx, r * 1.12 * ky), grad(cy, r * ky), a, line=0.2, ink=SOFTINK))
        out.append(soft(ell(cx - 0.25, cy - 0.35, 0.24, 0.18), HI, 0.75 * a))
    return out


def sc_hand(fr):
    """클릭 자리에 말랑 분홍 발도장을 꾹 — 냥이는 오른쪽 아래서 앞발을 볼 밖으로 들고, 꾹(장 4 · 10)에 도장이 납작
    눌리며 ^^ · 몸 꿀렁, 이어 두 장 동안 연분홍 고리가 퍼진다. 가운데 두 발가락 사이 위가 핫스팟 (7, 1).
    고리는 가로로 넓은 타원이라 위 끝이 판 안(y 0.9)에 든다 — 동그라미로 퍼뜨리니 위가 잘렸다(2026-10-13).
    전 판은 팔꿈치 꺾은 굵은 팔 끝에 큰 발바닥이었다("팔이 너무 커"), 시안 열다섯 장 끝에 고른 것(docs/taste.md)"""
    k = round(fr * NF) % NF
    tap = k % 6 in (3, 4, 5)
    clap = k % 6 == 4
    F = Frame(16.6, 15.6, 0.8)
    out = []
    if k % 6 in (4, 5):
        rx, ry, a = (3.8, 3.2, 0.9) if k % 6 == 4 else (5.0, 4.2, 0.5)
        out.append(flat(lambda x, y: abs(ell(7.5, 5.4, rx, ry)(x, y)) - 0.32, PINK_L, a))
    out += soft_print(7.5, 5.0, 1.0 if tap else 0.92, 1.0 if clap else 0.0)
    out += cat(F, "happy" if clap else "open", look=(-0.6, -0.7), turn_=0.15, tail_pts=curl(TAU * fr), paws=True,
               bob=0.6 if clap else 0.0, arms=[((-6.4, 5.4), (-9.9, 0.2 if tap else -0.5), True)])
    return out


SCENE = {"busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "wait": sc_wait,
         "hand": sc_hand, "cross": sc_cross, "ibeam": sc_ibeam, "move": sc_move, "no": sc_no, "pen": sc_pen,
         "up": sc_up, "we": sc_we, "ns": sc_ns, "nwse": sc_nwse, "nesw": sc_nesw}


class WhiteCat(Pet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = WhiteCat(COAT, SCENE, HOT)


def scene(name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
    return PET.cell(name, frame, soft_, tip_body, shape)


register("whitecat", PET)
catkit.load()

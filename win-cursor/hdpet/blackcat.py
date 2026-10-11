# SPDX-License-Identifier: Apache-2.0
"""까망이(blackcatanim) 고화질 — 치비(머리가 몸만 한 통통 냥) · 스티커 채색(고른 먹선 1칸 + 셀 그늘 한 단).

픽셀 까망이(gen/blackcat.py)를 HD 로 옮겼다. 짙은 회흑 털에 노란 동그란 눈이 실루엣 안에서 제일 밝고, 분홍 코 · 귀 속 ·
젤리, 소품의 주인공은 분홍 털실(공 · 한 가닥)이다. 까만 털은 먹선과 섞여 덩어리가 되므로 원본처럼 왼쪽 위 테 바로 안쪽을
밝히고(털 결), 감은 눈 · 입은 연회색, 수염을 늘 살린다(부엉이로 안 읽히게). 칸마다 하는 짓은 픽셀 판 그대로다.

  arrow   크림 화살표 빗변 뒤에서 빼꼼(catkit 빼꼼)
  help    작은 화살표 까망이 + 털실 한 가닥 물음표, 점은 통통 튀는 작은 털실 공
  busy    작은 화살표 까망이 + 굴러가는 털실 공 둘레를 차례로 도는 분홍 발자국 여덟
  wait    앉아서 털실 공을 앞발로 이리저리 굴린다 — 눈이 공을 따라간다
  cross   앞모습 얼굴 — 수염이 가로 조준선, 위아래 털실이 세로선. 사냥 눈(동공이 커졌다 작아졌다). 코가 핫스팟
  ibeam   위아래 매듭으로 묶은 털실 한 가닥이 I — 옆의 까망이가 앞발로 실을 톡톡. 실은 S 자로 흔들려도 가운데는 제자리
  pen     분홍 구슬 꼭지 뜨개바늘(뜨개코가 걸린)을 두 앞발로 쥐고 실로 물결 글씨 — 바늘 끝이 핫스팟
  no      빨간 금지 표지 안에서 등을 아치로 세우고 털 · 꼬리를 빵빵하게 부풀려 하악 — 귀는 납작
  ns      위에서 내려온 털실에 한 앞발로 매달려 대롱대롱 — 뒷발 · 꼬리가 아래 화살촉 쪽으로
  we      두 앞발을 양옆으로 쭉 뻗어 털실을 팽팽히 당긴다 — 실이 앞발에서 양 끝 화살촉까지
  nwse · nesw   한 앞발은 위 대각선, 다른 앞발은 아래 대각선으로 그 축의 털실을 당긴다(몸은 바로 섬)
  move    털실 공을 쫓아 제자리에서 폴짝폴짝 — 공이 둘레를 돌고 눈이 쫓는다. 네 방향 분홍 화살촉
  up      뒷발로 서서 한 앞발은 위로 쭉(젤리 보이는 발끝이 핫스팟), 다른 앞발로 냥냥펀치
  hand    종이 상자에 쏙 들어앉아 앞발 하나를 쑥 내밀어 톡 — 젤리 보이는 발끝이 핫스팟
  pin     작은 화살표 까망이 + 빨간 지도 핀 동그라미 속 분홍 발자국이 통통
  person  작은 화살표 까망이 + 까만 고양이 귀 후드를 쓴 사람이 손을 흔든다

좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 장면은 NF 장으로 나뉘어 있다(k = round(fr × NF) % NF).
틀(먹선 · 치비 몸 · 빼꼼 · 모양 화살표)은 catkit 이고, 까만 털에 안 맞는 두 곳(조각 칠 part · 얼굴 face)만
BlackCat.cell 이 칸을 그리는 동안 이 모듈 판으로 바꿔 끼운다(끝나면 되돌림 — catkit 이 한 번에 한 칸만 그리는 전제).
"""
from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

from . import catkit, register
from .catkit import *  # noqa: F401,F403

# 픽셀 판 팔레트(gen/blackcat.py) — 털만 HD 에서 한 끗 밝혔다(먹선과 갈리게)
OUT, EYE = hx("0b0b12"), hx("15151c")                               # 먹선 · 동공
FUR, FUR_L, FUR_D = hx("2c2c38"), hx("55556c"), hx("1b1b25")        # 털 · 털 결 하이라이트 · 그늘
IRIS = (hx("ffd23c"), hx("e39b14"), hx("fff3a8"))                   # 노란 눈(홍채 · 짙은 · 밝은)
LID, WHISK = hx("9a9ab4"), hx("b8b8cc")                             # 감은 눈 · 입 · 조준선 / 수염
PINK_C, PINK_D, BLUSH = hx("f7a3ba"), hx("d76f8e"), hx("e8789a")
RIM = hx("d2dde6")                                                  # 바깥 번짐 테(연회색)
YARN, YARN_D, YARN_L, YARN_O = hx("f27aa8"), hx("c84c80"), hx("ffc2da"), hx("7a2148")
MAW, FANG = hx("b02848"), hx("ffffff")
BOX, BOX_D, BOX_L, BOX_O = hx("c99a5e"), hx("9c6f3c"), hx("e2bd85"), hx("5e3f1e")
NEEDLE, NEEDLE_D, NEEDLE_O = hx("cfd3dc"), hx("8a90a0"), hx("4a4f5e")
SHIRT, SHIRT_D, SKIN, SKIN_D = hx("4a7fb5"), hx("2e5a88"), hx("f2c9a0"), hx("dca67c")
SIGN, SIGN_D, SIGN_L = hx("d64541"), hx("9e2b28"), hx("ef7a72")

COAT = Coat(FUR, FUR_D, OUT, EYE, RIM, (IRIS, IRIS), ear=PINK_C, cheek=BLUSH, nose=hx("e8789a"),
            nose_l=hx("ffc4d6"), jelly=PINK_C, tongue=PINK_C)

# 픽셀 판 핫스팟(art 칸 — art 는 그림을 왼쪽 위로 붙여 잘라 gen 의 HOT 와 다르다) 그대로
HOT = {"arrow": (1, 1), "busy": (1, 1), "cross": (15, 15), "hand": (4, 2), "help": (1, 1), "ibeam": (4, 15),
       "move": (15, 15), "nesw": (12, 12), "no": (14, 14), "ns": (4, 15), "nwse": (12, 12), "pen": (1, 20),
       "person": (1, 1), "pin": (1, 1), "up": (3, 1), "wait": (9, 13), "we": (15, 9)}


# ---- 까만 털 판: 조각 칠 · 얼굴 (BlackCat.cell 이 catkit 것과 바꿔 끼운다) ----

def bpart(f, col=None, shade=None, line=LINE, sh=1.0, ink=None):
    """catkit.part + 털 결: 털빛 조각은 왼쪽 위 테 바로 안쪽 한 칸을 밝힌다(원본 sheen) — 검은 덩이로 안 보이게"""
    col = FUR if col is None else col
    shade = FUR_D if shade is None else shade
    ink = OUT if ink is None else ink
    shine = not callable(col) and tuple(col) == FUR

    def paint(x, y, e, nx, ny, fr):
        c = col(x, y) if callable(col) else col
        if sh:
            c = lerp(c, shade, sh * smooth(-0.15, 0.15, f(x + SH[0], y + SH[1])))
        if shine:
            c = lerp(c, FUR_L, 0.9 * smooth(line + 1.25, line + 0.3, -e) * smooth(0.05, 0.7, -(nx + ny) * 0.7071))
        if line:
            c = lerp(c, ink, smooth(line + 0.12, line - 0.12, -e))
        return c, 1.0
    return layer(f, paint)


def beye(cx, cy, rx, look=(0.0, 0.0), pupil="round"):
    """노란 눈 하나 — catkit.eye 꼴에 동공 셋: round(보통) · big(사냥, 꽉 참) · slit(놀람 · 하악, 바늘)"""
    ry = rx * 1.12
    px, py = cx + look[0] * rx * 0.24, cy + ry * 0.12 + look[1] * ry * 0.14
    prx, pry = {"round": (rx * 0.38, ry * 0.46), "big": (rx * 0.68, ry * 0.7), "slit": (rx * 0.15, ry * 0.72)}[pupil]
    if pupil != "round":
        px, py = cx + look[0] * rx * 0.1, cy + ry * 0.05
    h1 = (cx - rx * 0.36, cy - ry * 0.38, rx * 0.34)
    h2 = (cx + rx * 0.4, cy + ry * 0.42, rx * 0.14)
    iris, deep, light = IRIS

    def paint(x, y, e, nx, ny, fr):
        c = lerp(light, iris, smooth(cy - ry * 0.9, cy - ry * 0.1, y))
        c = lerp(c, deep, 0.5 * smooth(cy + ry * 0.3, cy + ry * 1.0, y))
        c = lerp(c, EYE, smooth(0.12, -0.12, hypot((x - px) / prx, (y - py) / pry) - 1))
        c = lerp(c, HI, smooth(h1[2] + 0.1, h1[2] - 0.1, hypot(x - h1[0], y - h1[1])))
        c = lerp(c, HI, 0.9 * smooth(h2[2] + 0.08, h2[2] - 0.08, hypot(x - h2[0], y - h2[1])))
        return lerp(c, deep, smooth(0.26, 0.1, -e)), 1.0
    return layer(ell(cx, cy, rx, ry), paint)


def bshut(cx, cy, rx, kind="blink"):
    """감은 눈 — 연회색(검은 털 위에 먹색 줄은 안 보인다). blink 는 ∪, happy 는 ^"""
    w = max(0.32, 0.22 * rx)
    if kind == "happy":
        return flat(arc(cx, cy + rx * 0.55, rx * 0.95, w, pi * 1.2, pi * 0.6), LID)
    return flat(arc(cx, cy - rx * 0.5, rx * 0.95, w, pi * 0.18, pi * 0.64), LID)


def bface(F, mood="open", look=(0.0, 0.0), turn_=0.0, mouth="w", tongue=0.0):
    """catkit.face 자리 — 볼 · 수염 · 노란 눈 · 분홍 코 · 연회색 ω 입. mood 는 open · blink · happy · wink ·
    hunt(사냥 눈) · wide(놀란 바늘 동공) · hiss(눈꼬리 치켜뜸). mouth 는 w · hiss(벌린 입 · 송곳니) · ''"""
    s = F.s
    out = []
    er = max(1.75 * s, 1.38)
    for sg in (-1, 1):                                         # 볼
        bx, by = F.w(turn_ + sg * 4.5, 2.7)
        rx = max(1.45 * s, 0.95)
        out.append(soft(ell(bx, by, rx, rx * 0.62), BLUSH, 0.8))
    if s >= 0.5:                                               # 수염 — 볼에서 머리 밖까지(고양이로 읽히는 표지)
        w = max(0.2 * s, 0.17)
        for sg in (-1, 1):
            for j, (v0, v1) in enumerate(((2.0, 1.2), (2.9, 3.4))):
                a = F.w(turn_ + sg * 5.4, v0)
                b = F.w(turn_ + sg * 9.6, v1)
                out.append(flat(capsule(a[0], a[1], b[0], b[1], w), WHISK, 0.9))
    for sg in (-1, 1):
        ex, ey = F.w(turn_ + sg * 3.15, 0.25)
        if mood in ("blink", "happy") or (mood == "wink" and sg > 0):
            out.append(bshut(ex, ey, er, "happy" if mood in ("happy", "wink") else "blink"))
            continue
        pupil = {"hunt": "big", "wide": "slit", "hiss": "slit"}.get(mood, "round")
        out.append(beye(ex, ey, er, look, pupil))
        if mood == "hiss":                                     # 안쪽 위를 털로 덮어 눈꼬리를 치켜뜬다
            ry = er * 1.12
            out.append(flat(poly([(ex - sg * er * 1.4, ey - ry * 1.5), (ex + sg * er * 1.5, ey - ry * 1.5),
                                  (ex + sg * er * 1.5, ey - ry * 0.75), (ex - sg * er * 1.4, ey + ry * 0.15)]), FUR))
    nx, ny = F.w(turn_, 2.05)
    hw = max(0.78 * s, 0.6)
    nose = rpoly([(nx - hw, ny - hw * 0.45), (nx + hw, ny - hw * 0.45), (nx, ny + hw * 0.6)], hw * 0.3)
    if mouth == "hiss":                                        # 하악: 코 아래 벌린 입 + 송곳니 둘
        mw, mh = max(1.5 * s, 1.0), max(1.25 * s, 0.85)
        my = ny + hw * 0.5 + mh
        out.append(flat(ell(nx, my, mw, mh), lambda x, y: lerp(MAW, hx("7a1530"), smooth(my - mh, my + mh, y)),
                        line=0.28, ink=OUT))
        for sg in (-1, 1):
            fx = nx + sg * mw * 0.5
            out.append(flat(poly([(fx - 0.38, my - mh * 0.75), (fx + 0.38, my - mh * 0.75), (fx, my + mh * 0.1)]), FANG))
    if tongue > 0:                                             # 혀 날름
        tl = tongue * max(2.2 * s, 1.6)
        tw = max(0.9 * s, 0.75)
        tg = smin(0.3, ell(nx, ny + hw * 0.9 + tl * 0.55, tw, tl * 0.55 + 0.2), circle(nx, ny + hw * 0.9 + tl, tw))
        out.append(flat(tg, PINK_C, line=0.28, ink=PINK_D))
    if mouth == "w" and s >= 0.5:                              # ω 입 — 연회색
        m = max(0.62 * s, 0.5)
        w = max(0.18 * s, 0.17)
        for sg in (-1, 1):
            out.append(flat(arc(nx + sg * m, ny + hw * 0.35, m, w, pi * 0.08, pi * 0.84), LID, 0.95))
    nose_c, nose_l = COAT.nose, COAT.nose_l
    out.append(flat(nose, lambda x, y: lerp(nose_l, nose_c, smooth(ny - hw * 0.4, ny + hw * 0.2, y))))
    return out


# ---- 소품: 털실 ----

def ball(cx, cy, r, rot=0.0, tail=None):
    """털실 공 — 감긴 실 줄이 rot 만큼 굴러가 있고 왼쪽 위가 밝다. tail 은 풀린 실 끝 꺾은선(공 뒤에 깔린다)"""
    out = []
    if tail:
        out += strand(chain([(cx, cy)] + list(tail), 0.5))
    f = circle(cx, cy, r)
    c, s = cos(rot), sin(rot)
    k = 3.0 / max(r, 1.0)

    def col(x, y):
        u, v = (x - cx) * c + (y - cy) * s, -(x - cx) * s + (y - cy) * c
        band = (u + 0.32 * v * v / r) * k                     # 감긴 실 결: 휜 줄
        g = lerp(YARN, YARN_D, 0.85 * smooth(0.2, 0.08, abs(band - round(band))))
        u2, v2 = (x - cx) * 0.5 - (y - cy) * 0.87, (x - cx) * 0.87 + (y - cy) * 0.5
        if u2 > r * 0.15:                                      # 오른쪽 위 반쪽은 엇갈려 감긴 줄
            b2 = (v2 + 0.3 * u2 * u2 / r) * k
            g = lerp(lerp(YARN, YARN_D, 0.18), YARN_D, 0.85 * smooth(0.2, 0.08, abs(b2 - round(b2))))
        return lerp(g, YARN_L, 0.85 * smooth(r * 0.42, r * 0.2, hypot(x - cx + r * 0.38, y - cy + r * 0.42)))
    return out + [base(f), part(f, col, shade=YARN_D, ink=YARN_O, line=0.8, sh=0.7)]


def twist(x, y):
    """꼰 실 결 — 비스듬한 밝은 줄(밋밋한 분홍 막대는 광선검으로 읽혔다)"""
    return lerp(YARN, YARN_L, 0.75 * smooth(0.55, 0.85, 0.5 + 0.5 * sin((x + y) * 2.1)))


def strand(f, line=0.38):
    return [base(f), part(f, twist, shade=YARN_D, ink=YARN_O, line=line, sh=0.0)]


def thread(pts, r=0.62):
    return strand(chain(pts, r))


def ychev(cx, cy, dx, dy, L=2.4, a=1.0):
    """(dx, dy) 쪽을 가리키는 털실 분홍 화살촉 — 꼭짓점이 (cx, cy)"""
    n = hypot(dx, dy)
    dx, dy = dx / n, dy / n
    px, py = -dy, dx
    f = union(*[capsule(cx, cy, cx - dx * L + s * px * L, cy - dy * L + s * py * L, 0.75) for s in (-1, 1)])
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(YARN, YARN_O, smooth(0.38, 0.2, -e)), 1.0), alpha=a)]


def pspark(cx, cy, L=1.6):
    """톡 할 때 튀는 분홍 반짝"""
    w = L * 0.32
    f = union(poly([(cx - L, cy), (cx, cy - w), (cx + L, cy), (cx, cy + w)]),
              poly([(cx, cy - L), (cx + w, cy), (cx, cy + L), (cx - w, cy)]))
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(YARN_L, YARN, smooth(0.25, 0.1, -e)), 1.0))]


def fluffy(pts, r, fl, n):
    """꺾은선을 따라가는 굵기 r 의 줄 + 양옆 n 쌍 털 뭉치(반지름 fl) — 빵빵하게 부푼 털"""
    segs, tot = [], 0.0
    for p, q in zip(pts, pts[1:]):
        d = hypot(q[0] - p[0], q[1] - p[1])
        segs.append((p, q, tot, d))
        tot += d
    bumps = []
    for i in range(n):
        t = (i + 0.5) / n * tot
        for p, q, s0, d in segs:
            if s0 + d >= t:
                u = (t - s0) / d
                x, y = p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u
                nx, ny = -(q[1] - p[1]) / d, (q[0] - p[0]) / d
                for sg in (-1, 1):
                    bumps.append(circle(x + sg * nx * r * 0.72, y + sg * ny * r * 0.72, fl))
                break
    return smin(0.35, chain(pts, r), *bumps)


def fur_piece(f):
    return [base(f), bpart(f)]


# ---- 칸마다 장면 (art 좌표, 화살표 칸은 catkit 빼꼼) ----

def kof(fr):
    return round(fr * NF) % NF


def sc_help(fr):
    """작은 화살표 까망이 + 털실 한 가닥 물음표, 점은 작은 털실 공이 통통"""
    out = buddy(fr)
    q = union(arc(22.6, 15.4, 3.6, 1.05, pi * 0.95, pi * 1.42), capsule(25.3, 17.4, 22.6, 19.9, 1.05),
              capsule(22.6, 19.9, 22.6, 21.6, 1.05))
    out += strand(q, 0.45)
    hop = abs(sin(pi * fr * 2)) * 2.2
    out += ball(22.6, 26.6 - hop, 1.85, TAU * fr)
    return out


def sc_busy(fr):
    """작은 화살표 까망이 + 굴러가는 털실 공 둘레를 도는 분홍 발자국 여덟"""
    out = buddy(fr)
    cx, cy = 22.5, 22.5
    head = kof(fr) * 8 / NF
    for i in range(8):
        a = TAU * i / 8 - pi / 2
        lag = (head - i) % 8
        out.append(paw_print(cx + 6.9 * cos(a), cy + 6.6 * sin(a), 1.0 if lag < 1.5 else 0.6 if lag < 3 else 0.28))
    out += ball(cx, cy, 3.7, -TAU * fr)
    return out


def sc_pin(fr):
    """작은 화살표 까망이 + 빨간 지도 핀 동그라미 속 분홍 발자국이 통통"""
    out = buddy(fr)
    hop = abs(sin(pi * fr * 2))
    cx, cy = 22.6, 15.2 - 2.4 * hop
    out.insert(0, layer(ell(22.8, 29.0, 3.4 - 0.8 * hop, 0.75), lambda *a: (OUT, 0.2)))
    f = smin(1.0, circle(cx, cy, 5.6), poly([(cx - 4.6, cy + 2.6), (cx + 4.6, cy + 2.6), (cx, cy + 11.4)]))
    out += [base(f), part(f, lambda x, y: lerp(SIGN_L, SIGN, smooth(cy - 5, cy - 1.5, y + 0.6 * (x - cx))),
                          shade=SIGN_D, ink=SIGN_D)]
    out.append(flat(circle(cx, cy, 3.7), hx("fff4f6"), line=0.5, ink=SIGN_D))
    out.append(paw_print(cx, cy + 0.35, 1.0))
    return out


def sc_person(fr):
    """작은 화살표 까망이 + 까만 고양이 귀 후드를 쓴 사람이 손을 흔든다"""
    ph = TAU * fr
    k = kof(fr)
    out = buddy(fr)
    cx, cy = 22.4, 21.8
    body = clip_y(ell(cx, cy + 8.6, 7.0, 5.4), 30.4)
    wave = abs(sin(ph))
    hand_ = (cx + 6.6 + 0.5 * wave, cy - 1.6 - 1.6 * wave)
    sleeve = capsule(cx + 4.6, cy + 5.6, hand_[0], hand_[1] + 1.0, 1.25)
    hood = smin(0.6, ell(cx, cy - 0.6, 5.2, 4.9), *[rpoly([(cx + sg * 4.9, cy - 2.2), (cx + sg * 4.4, cy - 7.4),
                                                          (cx + sg * 1.2, cy - 4.6)], 0.6) for sg in (-1, 1)])
    face_ = ell(cx, cy + 0.4, 3.5, 3.1)
    hand_f = circle(*hand_, 1.35)
    out += [base(body, hood, sleeve, hand_f), part(body, lambda x, y: SHIRT_D if abs(x - cx) < 0.35 else SHIRT, shade=SHIRT_D),
            bpart(hood), part(sleeve, SHIRT, shade=SHIRT_D), part(hand_f, SKIN, shade=SKIN_D)]
    for sg in (-1, 1):                                    # 후드 귀 속
        out.append(flat(rpoly([(cx + sg * 4.3, cy - 3.2), (cx + sg * 4.1, cy - 6.0), (cx + sg * 2.2, cy - 4.5)], 0.3), PINK_C))
    out.append(part(face_, SKIN, shade=SKIN_D, line=0.7))
    for sg in (-1, 1):
        if k == 6:
            out.append(flat(capsule(cx + sg * 1.5 - 0.5, cy + 0.6, cx + sg * 1.5 + 0.5, cy + 0.6, 0.22), EYE))
        else:
            out.append(flat(ell(cx + sg * 1.5, cy + 0.4, 0.5, 0.7), EYE))
        out.append(soft(ell(cx + sg * 2.5, cy + 1.8, 0.8, 0.5), BLUSH, 0.8))
    out.append(flat(arc(cx, cy + 1.5, 0.8, 0.22, pi * 0.15, pi * 0.7), PINK_D))
    return out


def sc_wait(fr):
    """앉아서 털실 공을 앞발로 이리저리 굴린다 — 공이 구른 만큼 줄이 돌고, 공 쪽 앞발이 공 위에, 눈이 공을 따라간다"""
    ph = TAU * fr
    k = kof(fr)
    s = 0.82
    F = Frame(9.6, 8.9, s)
    d = 4.0 * sin(ph)
    bx, by, r = 9.6 + d, 21.9, 3.3
    sg = 1 if d >= 0 else -1
    sw = sin(ph + 1)
    out = cat(F, "blink" if k == 6 else "open", look=(clamp(d / 3.0, -1, 1), 0.9), paws=False, sway=0.5 * sw,
              tail_pts=[(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.4 + sw, 3.9), (8.2 + 1.4 * sw, 2.0)])
    # 바닥 앞발(공 반대쪽) — 앉은 앞발 자리
    gp = F.f(ell(-sg * 2.45, 11.35, 1.95, 1.4))
    out += fur_piece(gp)
    out += ball(bx, by, r, -d / r, tail=[(bx + 3.6, by + 2.4), (bx + 6.6, by + 3.2), (bx + 9.4, by + 2.6)])
    lift = abs(sin(ph))
    pu, pv = F.loc(bx - sg * 0.4, by - r * 0.72 - 0.9 * lift)
    lp = F.f(ell(pu, pv, 1.95, 1.45))
    arm = F.f(taper(sg * 2.6, 8.4, 1.7, pu, pv, 1.5))
    out += [base(arm, lp), bpart(arm), bpart(lp)]
    return out


def sc_cross(fr):
    """앞모습 얼굴 — 수염이 가로 조준선, 위아래 털실이 세로선. 사냥 눈. 분홍 코가 핫스팟"""
    ph = TAU * fr
    k = kof(fr)
    C_ = 15.5
    s = 1.04
    F = Frame(C_, C_ - 2.05 * s, s)
    lines = union(capsule(2.6, C_, 6.2, C_, 0.5), capsule(24.8, C_, 28.4, C_, 0.5))
    out = [base(lines), flat(lines, LID, line=0.3, ink=OUT)]
    sway = 0.8 * sin(ph)
    out += thread([(C_, 2.6), (C_, 7.2)])                 # 위 실은 머리 뒤로
    out += cat(F, "hunt" if k % 6 < 3 else ("blink" if k == 10 else "open"), body=False, paws=False, tail=False,
               ear_tilt=(0.4 * max(0.0, sin(2 * ph)), 0.0))
    tw = 0.35 * sin(2 * ph)
    for sg in (-1, 1):                                    # 볼 수염이 조준선으로 이어지며 까딱
        for j in (-1, 1):
            out.append(flat(capsule(C_ + sg * 8.6, C_ + j * 0.7, C_ + sg * 10.8, C_ + j * (1.25 + tw), 0.2), WHISK, 0.9))
    out += thread([(C_, 21.0), (C_ + 0.3 * sway, 25.0), (C_ + sway, 28.4)])
    return out


def sc_ibeam(fr):
    """위아래 매듭으로 묶어 늘어뜨린 털실 한 가닥이 I — 옆의 까망이가 앞발로 실을 톡톡. 실 가운데(핫스팟)는 제자리"""
    ph = TAU * fr
    k = kof(fr)
    X = 4.5
    bend = 0.9 * sin(ph)
    pts = [(X + bend * sin(TAU * t / 10), 3.0 + 25.0 * t / 10) for t in range(11)]   # S 자, 가운데는 X
    out = thread(pts, 0.75)
    for y in (2.4, 28.6):                                 # 위아래 매듭(가로획)
        kn = union(capsule(X - 2.6, y, X + 2.6, y, 0.85), circle(X, y, 1.25))
        out += strand(kn, 0.45)
    tap = sin(2 * ph)
    s = 0.66
    F = Frame(16.6, 14.0, s)
    hand_ = F.loc(X + 2.2 + 0.9 * max(0.0, -tap), 13.4)
    out += cat(F, "happy" if tap > 0.8 else ("blink" if k == 8 else "open"), look=(-1.0, 0.0), turn_=-0.9,
               sway=0.5 * sin(ph), arms=[((-4.2, 5.2), hand_, True)],
               tail_pts=[(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.4 + 0.6 * sin(ph), 3.9), (8.2 + 0.9 * sin(ph), 2.0)])
    return out


TIPP = (1.5, 20.5)                                        # 뜨개바늘 끝(핫스팟 칸 가운데)


def sc_pen(fr):
    """뜨개바늘을 두 앞발로 쥐고 실로 물결 글씨 — 바늘 끝(왼쪽 아래)이 핫스팟, 끝에서 풀린 실이 길어진다"""
    ph = TAU * fr
    k = kof(fr)
    tip = TIPP
    ang = -0.69 + 0.04 * sin(2 * ph)
    ux, uy = cos(ang), sin(ang)
    L = 15.0
    end = (tip[0] + ux * L, tip[1] + uy * L)
    out = []
    n = 3 + k                                             # 써 나간 물결
    pts = [(tip[0] + 0.3 + 1.05 * i, tip[1] + 1.4 - 1.2 * abs(sin(i * 0.9))) for i in range(n + 1)]
    out += thread([tip] + pts, 0.5)
    r = 0.85                                              # 바늘 굵기 — 32 에서 1–2칸
    nd = smin(0.3, poly([tip, (tip[0] + ux * 2.6 - uy * r, tip[1] + uy * 2.6 + ux * r),
                         (tip[0] + ux * 2.6 + uy * r, tip[1] + uy * 2.6 - ux * r)]),
              capsule(tip[0] + ux * 2.4, tip[1] + uy * 2.4, end[0], end[1], r))

    def ncol(x, y):
        return lerp(hx("f4f6fa"), NEEDLE, smooth(-0.4, 0.3, (x - tip[0]) * -uy + (y - tip[1]) * ux))
    knob = circle(end[0] + ux * 0.8, end[1] + uy * 0.8, 1.7)
    out += [base(nd, knob), part(nd, ncol, shade=NEEDLE_D, ink=NEEDLE_O, line=0.5, sh=0.0),
            part(knob, lambda x, y: lerp(YARN_L, YARN, smooth(end[1] - 1.2, end[1] + 0.6, y)), shade=YARN_D, ink=YARN_O, line=0.6)]
    for t in (0.34, 0.46):                                # 바늘에 걸린 뜨개코 둘
        cx, cy = tip[0] + ux * L * t, tip[1] + uy * L * t
        out += strand(ring(cx, cy, 0.95, 0.34), 0.28)
    F = Frame(17.4, 10.2, 0.72)                           # 바늘 꼭지를 가슴께에 끌어안는다
    g1 = F.loc(tip[0] + ux * L * 0.72, tip[1] + uy * L * 0.72)   # 바늘을 쥔 앞발(캐논)
    g2 = F.loc(tip[0] + ux * L * 0.84, tip[1] + uy * L * 0.84)
    out += cat(F, "blink" if k == 4 else "open", look=(-0.8, 0.7), turn_=-0.9, sway=0.5 * sin(ph),
               arms=[((-4.6, 5.4), g1, False), ((-4.0, 3.0), g2, False)])
    return out


def hiss_cat(F, fr, puff, hiss):
    """옆으로 선 까망이(앞모습 얼굴): 아치로 세운 등 · 빵빵한 꼬리 · 다리 넷 · 납작 귀"""
    ph = TAU * fr
    fl = 0.45 + 0.85 * puff                                  # 털이 부풀었다 가라앉았다
    sw = 1.3 * sin(ph + 0.6)
    arch = [(-5.6, 1.8), (-3.6, -2.8), (0.0, -4.6 - 0.5 * puff), (3.6, -2.8), (5.6, 1.8)]
    back = F.f(fluffy(arch, 2.9, fl, 6))
    tail = F.f(fluffy([(5.4, 0.2), (8.6, -2.2), (9.8 + 0.6 * sw, -6.8), (8.8 + 1.0 * sw, -10.6)], 1.7, fl * 0.9, 4))
    near = [F.f(capsule(-4.4, 1.6, -5.0, 8.6, 1.35)), F.f(capsule(4.6, 1.6, 5.2, 8.6, 1.35))]
    far = [F.f(capsule(-2.4, 1.6, -2.6, 8.6, 1.2)), F.f(capsule(3.0, 1.6, 3.4, 8.6, 1.2))]
    hx_, hy_ = F.w(-6.6, -3.4)
    H = Frame(hx_, hy_, F.s * 0.78)
    head = catkit.head_f(H)
    ears = [H.f(rpoly([(sg * 5.8, -1.4), (sg * 10.6, -5.6), (sg * 2.4, -5.2)], 0.8)) for sg in (-1, 1)]
    out = [base(*far, tail, back, *near, head, *ears)]
    out += [part(f, FUR_D, shade=OUT) for f in far]          # 먼 다리는 한 단 어둡게
    out += [bpart(tail), bpart(back)] + [bpart(f) for f in near]
    for sg, E in zip((-1, 1), ears):
        out.append(bpart(E))
        out.append(flat(H.f(rpoly([(sg * 5.6, -2.4), (sg * 8.8, -5.0), (sg * 3.6, -4.6)], 0.4)), PINK_C))
    out.append(bpart(head))
    out += bface(H, "hiss" if hiss else "wide", mouth="hiss" if hiss else "w")
    return out


def sc_no(fr):
    """빨간 금지 표지 안에서 등을 아치로 세우고 털 · 꼬리를 빵빵하게 부풀려 하악 — 귀는 납작"""
    ph = TAU * fr
    k = kof(fr)
    C_ = 14.5
    puff = 0.5 + 0.5 * sin(ph)
    out = hiss_cat(Frame(C_ + 0.3, C_ + 1.6, 0.78), fr, puff, k % 6 < 4)
    R = 12.5
    sg = union(ring(C_, C_, R - 1.25, 1.25), capsule(C_ - 7.7, C_ - 7.7, C_ + 7.7, C_ + 7.7, 1.35))
    out += [base(sg), part(sg, lambda x, y: lerp(SIGN_L, SIGN, smooth(C_ - 10, C_ - 4, y + 0.5 * x - 0.5 * C_)),
                           shade=SIGN_D, ink=SIGN_D, line=0.8)]
    return out


def tug(fr, hands, F, chev, mood=None, extra=None, look=(0.0, 0.0)):
    """털실을 축으로 당기는 까망이 — hands = [(어깨(캐논), 손(화면), 그 손에서 실이 갈 화살촉 끝 또는 None)],
    chev = [(x, y, dx, dy)] 축 양 끝 화살촉. 실은 손에서 화살촉 바로 앞까지, 몸 뒤에 깔린다"""
    ph = TAU * fr
    k = kof(fr)
    e = 0.5 + 0.5 * sin(ph)
    o = 0.6 if e > 0.6 else 0.0
    out = []
    for (x, y, dx, dy) in chev:
        out += ychev(x + dx * o, y + dy * o, dx, dy, 2.2, 1.0 if o else 0.8)
    for _, hand_, to in hands:
        if to:
            out += thread([hand_, to], 0.7)
    arms = [(sh_, F.loc(*hand_), True) for sh_, hand_, _ in hands]
    out += cat(F, mood or ("happy" if e > 0.8 else ("blink" if k == 3 else "open")), look=look, sway=0.5 * sin(ph),
               arms=arms, **(extra or {}))
    return out


def sc_we(fr):
    """두 앞발을 양옆으로 쭉 뻗어 털실을 팽팽히 당긴다 — 실이 앞발에서 양 끝 화살촉까지"""
    e = 0.5 + 0.5 * sin(TAU * fr)
    Y = 9.5
    F = Frame(15.5, 7.4, 0.62)
    r = 5.0 + 0.6 * e
    hands = [((-4.8, 4.8), (15.5 - r, Y), (3.6, Y)), ((4.8, 4.8), (15.5 + r, Y), (27.4, Y))]
    return tug(fr, hands, F, [(2.0, Y, -1, 0), (29.0, Y, 1, 0)])


def sc_ns(fr):
    """위 털실에 한 앞발로 매달려 대롱대롱 — 뒷발 · 꼬리가 아래 화살촉 쪽으로 늘어졌다 줄었다"""
    ph = TAU * fr
    k = kof(fr)
    e = 0.5 + 0.5 * sin(ph)
    X = 4.5
    P = (X + 0.3, 9.8 - 0.8 * e)                          # 실을 쥔 앞발(화면)
    hu, hv = -9.6, -7.4                                   # 그 앞발(캐논)
    s = 0.62
    ang = -0.22 + 0.1 * sin(ph)                          # 앞발을 축으로 흔들
    c_, sn = cos(ang), sin(ang)
    F = Frame(P[0] - (hu * c_ - hv * sn) * s, P[1] - (hu * sn + hv * c_) * s, s, ang)
    o = 0.6 if e > 0.6 else 0.0
    out = []
    for (x, y, dx, dy) in ((X, 1.9, 0, -1), (X, 29.1, 0, 1)):
        out += ychev(x + dx * o, y + dy * o, dx, dy, 2.2, 1.0 if o else 0.8)
    out += thread([(X, 3.4), (X, 27.6)], 0.6)                 # 축 털실(위아래 화살촉 사이) — 냥이 뒤로 지나간다
    dl = 1.6 * e
    legs = [(F.f(chain([(-2.2, 10.0), (-2.6, 13.6 + dl)], 1.7, 1.5)), FUR),
            (F.f(ell(-2.7, 14.6 + dl, 1.7, 1.45)), FUR),
            (F.f(chain([(2.2, 10.0), (2.8, 13.2 + dl)], 1.7, 1.5)), FUR),
            (F.f(ell(2.9, 14.2 + dl, 1.7, 1.45)), FUR)]
    sw = sin(ph + 1)
    tp = [(3.0, 10.4), (4.4, 14.0), (3.0 + 0.8 * sw, 17.6 + 0.8 * e), (0.6 + 1.2 * sw, 19.4 + 0.8 * e)]
    out += cat(F, "happy" if e > 0.85 else ("blink" if k == 3 else "open"), look=(-0.3, -0.7), paws=False,
               arms=[((-6.8, 2.8), (hu, hv), True), ((4.6, 4.6), (6.0, 9.6 + 0.6 * sw), False)],
               extra_under=legs, tail_pts=tp)
    return out


def sc_nwse(fr):
    """한 앞발은 왼쪽 위, 다른 앞발은 오른쪽 아래 대각선으로 그 축의 털실을 당긴다"""
    e = 0.5 + 0.5 * sin(TAU * fr)
    C_ = 12.5
    F = Frame(12.9, 9.6, 0.6)
    d1, d2 = 4.8 + 0.5 * e, 4.4 + 0.5 * e
    hands = [((-6.6, 2.8), (C_ - d1, C_ - d1), (4.2, 4.2)), ((4.2, 5.6), (C_ + d2, C_ + d2), (20.8, 20.8))]
    return tug(fr, hands, F, [(2.9, 2.9, -1, -1), (22.1, 22.1, 1, 1)], look=(-0.4, -0.3))


def sc_nesw(fr):
    """한 앞발은 오른쪽 위, 다른 앞발은 왼쪽 아래 대각선으로 그 축의 털실을 당긴다"""
    e = 0.5 + 0.5 * sin(TAU * fr)
    C_ = 12.5
    F = Frame(12.1, 9.6, 0.6)
    d1, d2 = 4.8 + 0.5 * e, 4.4 + 0.5 * e
    hands = [((6.6, 2.8), (C_ + d1, C_ - d1), (20.8, 4.2)), ((-4.2, 5.6), (C_ - d2, C_ + d2), (4.2, 20.8))]
    return tug(fr, hands, F, [(22.1, 2.9, 1, -1), (2.9, 22.1, -1, 1)], look=(0.4, -0.3))


def sc_move(fr):
    """털실 공을 쫓아 제자리에서 폴짝 — 공이 둘레를 돌고 눈이 쫓는다. 네 방향 분홍 화살촉"""
    ph = TAU * fr
    k = kof(fr)
    o = 0.6 if k % 6 < 3 else 0.0
    out = []
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        out += ychev(15.5 + dx * (13.6 + o), 15.5 + dy * (13.6 + o), dx, dy, 2.2)
    hop = abs(sin(2 * ph))
    out.append(layer(ell(15.5, 22.6, 4.4 - 1.2 * hop, 0.8), lambda *a: (OUT, 0.18)))
    a = ph - pi / 2
    bx, by = 15.5 + 9.6 * cos(a), 15.0 + 8.8 * sin(a)
    F = Frame(15.5, 11.4 - 2.2 * hop, 0.66)
    hx_, hy_ = F.w(0, 0)
    lx, ly = bx - hx_, by - hy_
    ll = hypot(lx, ly) or 1.0
    behind = by < 10.0
    yb = ball(bx, by, 1.75, -2 * ph)
    out += yb if behind else []
    out += cat(F, "happy" if hop > 0.85 else "open", look=(lx / ll, ly / ll), turn_=0.8 * lx / ll, sway=0.5 * sin(2 * ph),
               bob=0.5 * (1 - hop))
    out += [] if behind else yb
    return out


def sc_up(fr):
    """뒷발로 서서 한 앞발은 위로 쭉 — 젤리 보이는 발끝(맨 위)이 핫스팟, 다른 앞발로 냥냥펀치"""
    ph = TAU * fr
    k = kof(fr)
    s = 0.76
    F = Frame(10.6, 12.2, s)
    jab = max(0.0, sin(2 * ph))
    ra = max(2.7, 2.1 / s)
    top = F.loc(3.6, 1.3 + ra * 1.04 * s)                 # 위로 뻗은 발 가운데 — 맨 위 먹선이 (3, 1) 칸
    p2 = (8.4 + 2.4 * jab, -1.6 - 3.0 * jab)
    out = cat(F, "happy" if jab > 0.6 else ("blink" if k == 7 else "open"), look=(-0.5, -0.8),
              arms=[((-6.2, 3.6), top, True), ((5.6, 4.6), p2, jab > 0.6)], ear_tilt=(-0.8, 0.0),
              tail_pts=[(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.6 + sin(ph), 3.9), (8.4 + 1.4 * sin(ph), 2.0)])
    if jab > 0.6:
        px, py = F.w(*p2)
        out += pspark(px + 2.4, py - 2.0, 1.4) + pspark(px + 3.0, py + 0.8, 1.0)
    return out


def sc_hand(fr):
    """종이 상자에 쏙 들어앉아 앞발 하나를 쑥 내밀어 톡 — 젤리 보이는 발끝이 핫스팟. 톡 할 때 ^^ · 반짝"""
    ph = TAU * fr
    k = kof(fr)
    tap = k in (2, 3, 8, 9)
    s = 0.84
    F = Frame(15.2, 12.6, s)
    ra = max(2.7, 2.1 / s)
    hand_ = F.loc(5.1, 2.0 + ra * 1.04 * s + (0.3 if tap else 0.0))
    # 상자 뒷벽(안쪽) — 냥이 뒤
    out = [base(poly([(6.4, 20.0), (25.6, 20.0), (24.2, 17.6), (7.8, 17.6)])),
           part(poly([(6.4, 20.0), (25.6, 20.0), (24.2, 17.6), (7.8, 17.6)]), BOX_D, shade=BOX_O, ink=BOX_O, line=0.6)]
    out += cat(F, "happy" if tap else ("blink" if k == 6 else "open"), look=(-0.6, -0.6), turn_=-0.4, sway=0.5 * sin(ph),
               arms=[((-6.4, 3.6), hand_, True)], ear_tilt=(-0.8, 0.0),
               tail_pts=[(3.6, 6.4), (7.4, 6.0), (9.6, 3.2), (9.4 + 0.8 * sin(ph), -0.2), (8.4 + 1.2 * sin(ph), -2.0)])
    front = rbox(16.0, 24.8, 9.6, 4.8, 0.6)
    flaps = [poly([(6.4, 20.2), (2.8, 22.6), (3.4, 18.2), (6.6, 18.6)]), poly([(25.6, 20.2), (29.2, 22.6), (28.6, 18.2), (25.4, 18.6)])]

    def bcol(x, y):
        c = lerp(BOX_L, BOX, smooth(20.2, 21.4, y))
        return lerp(c, BOX_D, 0.75 * smooth(0.95, 0.75, abs(x - 16.0)) * smooth(23.0, 22.6, y))   # 가운데 테이프
    out += [base(front, *flaps)] + [part(f, BOX_D, shade=BOX_O, ink=BOX_O, line=0.7) for f in flaps]
    out.append(part(front, bcol, shade=BOX_D, ink=BOX_O, line=0.8))
    if tap:
        px, py = F.w(*hand_)
        L = 1.5 if k in (3, 9) else 1.1
        out += pspark(px + 3.4, py - 0.4, L) + pspark(px + 2.6, py + 3.4, L * 0.75)
    return out


SCENE = {"busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "wait": sc_wait,
         "hand": sc_hand, "cross": sc_cross, "ibeam": sc_ibeam, "move": sc_move, "no": sc_no, "pen": sc_pen,
         "up": sc_up, "we": sc_we, "ns": sc_ns, "nwse": sc_nwse, "nesw": sc_nesw}


class BlackCat(Pet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes).
    칸을 그리는 동안만 catkit 의 조각 칠 · 얼굴을 까만 털 판으로 바꿔 끼운다(빼꼼 · 동반 · 치비 몸이 다 그걸 부른다)"""

    def cell(self, name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
        keep = catkit.part, catkit.face
        catkit.part, catkit.face = bpart, bface
        try:
            return super().cell(name, frame, soft_, tip_body, shape)
        finally:
            catkit.part, catkit.face = keep


PET = BlackCat(COAT, SCENE, HOT)


def scene(name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
    return PET.cell(name, frame, soft_, tip_body, shape)


register("blackcat", PET)

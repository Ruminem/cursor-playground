# SPDX-License-Identifier: Apache-2.0
"""샴냥(siamesecatanim) 고화질 — 치비 냥 · 스티커 채색(고른 먹선 1칸 + 셀 그늘 한 단). 틀은 catkit, 여기는 털빛 · 소품 · 장면만.

픽셀 샴냥(gen/siamesecat.py)의 포인트 무늬를 옮겼다 — 크림 몸에 얼굴 가운데 짙은 갈색 가면(주둥이 둘레가 제일 짙고
바깥으로 번진다) · 짙은 귀 · 발끝 · 꼬리, 파란 눈. 수다쟁이라 소품의 주인공은 말풍선과 음표(♪)이고 신호색(화살촉 · 음표 ·
말풍선 점)은 눈 색인 파랑이다. 칸마다 하는 짓도 픽셀 판 그대로다.

  arrow   크림 화살표 빗변 뒤 빼꼼(catkit peek) — 짙은 앞발 둘이 빗변을 잡는다
  busy    작은 화살표 샴냥 + 말풍선 속 '…' 세 점이 차례로 통통(입력 중)
  help    작은 화살표 샴냥 + 말풍선 속 파란 물음표, 말풍선이 통 튄다
  person  작은 화살표 샴냥 + 어깨에 샴냥을 두른 사람 — 어깨냥 꼬리가 살랑
  pin     작은 화살표 샴냥 + 흰 동그라미 속 파란 음표가 든 빨간 핀이 통통
  cross   조준선 가운데 앉은 파란 나비(몸통이 핫스팟)를 아래에서 고개 내민 샴냥이 사시로 노려본다 — 나비 날갯짓
  hand    마네키네코 — 짙은 앞발을 들고 까딱까딱(든 발 꼭대기가 핫스팟), 다른 앞발엔 금화, 목엔 금방울
  ibeam   글자 커서 I 에 앞발을 얹고 조잘대면 I 왼쪽에 파란 글자 점이 하나씩 — I 는 깜빡이듯 짙었다 옅었다
  move    앉은 샴냥이 위 · 오른쪽 · 아래 · 왼쪽으로 콩콩 옮겨 앉는다 — 가는 쪽 화살촉이 켜지고 뒤에 바람 줄
  ns      앉아서 목을 쭉 빼고 "야~옹" — 목이 늘며 입이 열리고 줄며 닫힌다. 위아래 화살촉
  we · nwse · nesw   기지개(catkit stretch) — 파란 화살촉
  no      빨간 금지 표지 안에서 입을 크게 벌리고 "냐아앙!"(눈 ><) 하다가 입 꾹 다물고 흥 — 옆에 느낌표
  pen     짙은 꼬리 끝을 붓 삼아 쓴다 — 꼬리 끝(왼쪽 아래)이 핫스팟, 먹 줄이 길어진다
  up      꼬리를 머리 옆으로 곧게 세운다(반가워) — 끝은 물음표 갈고리, 그 꼭대기가 핫스팟. 갈고리 끝만 까딱
  wait    앉아서 고개를 까딱이며 노래 — 입이 열렸다 닫히고 음표가 둥실 떠올랐다 사라진다
"""
from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

from . import catkit, register
from .catkit import *  # noqa: F401,F403

# 픽셀 판 팔레트(gen/siamesecat.py) 그대로
OUT, EYE = hx("3a2a30"), hx("22263a")
CREAM_S, CREAM_SD = hx("fff3e0"), hx("eedabd")                 # 몸 · 그늘
PT, PT_L, PT_D = hx("7a5642"), hx("a8866a"), hx("4a3226")      # 포인트(짙은 갈색) · 번진 테 · 코
BLUE, BLUE_D, BLUE_L = hx("5aa0ec"), hx("2f6cc0"), hx("9ccaf6")
RIM = hx("fbecdc")
PAPER = hx("fffdf8")                                           # 말풍선 속
GOLD, GOLD_D, GOLD_L = hx("f2c94c"), hx("c9962a"), hx("ffe48a")
INKC = hx("2b2630")                                            # 먹
SKIN, SHIRT, SHIRT_D, HAIR = hx("f7d7bc"), hx("c98aa8"), hx("a46886"), hx("5a4038")
WING, WING_D = hx("9ccaf6"), hx("5aa0ec")                      # 나비
SIGN, SIGN_D, SIGN_L = hx("d64541"), hx("9e2b28"), hx("ef7a72")
MOUTH = hx("6a2f38")                                           # 벌린 입 속


class Siamese(Coat):
    """포인트 무늬: 머리는 주둥이 둘레 가면(짙은 속 → 번진 테 → 크림), 귀 · 발 · 손 · 기지개 다리는 짙은 갈색,
    꼬리 · 팔은 몸에서 멀어질수록 짙어진다. F 가 없으면(기지개 · 빼꼼 앞발) 부위 색 하나"""

    def fur(self, part, F=None, turn_=0.0):
        if part in ("ear", "paw", "hand", "front", "back"):
            return PT
        if part == "head" and F is not None:
            mc, loc = 0.55 * turn_, F.loc

            def mask(x, y):
                u, v = loc(x, y)
                d = hypot((u - mc) / 5.4, (v - 1.3) / 4.1)
                return lerp(PT, lerp(PT_L, CREAM_S, smooth(0.95, 1.2, d)), smooth(0.62, 0.95, d))
            return mask
        if part in ("tail", "arm"):
            if F is None:
                return PT
            loc = F.loc
            c0, r0, r1 = ((0.0, 7.7), 5.0, 8.5) if part == "tail" else ((0.0, 4.0), 5.5, 10.0)

            def grad(x, y):
                u, v = loc(x, y)
                return lerp(PT_L, PT, smooth(r0, r1, hypot(u - c0[0], v - c0[1])))
            return grad
        return self.base


COAT = Siamese(CREAM_S, CREAM_SD, OUT, EYE, RIM, ((BLUE, BLUE_D, BLUE_L), (BLUE, BLUE_D, BLUE_L)),
               ear=PT_L, cheek=hx("f2a2b0"), nose=PT_D, nose_l=hx("7e5848"), jelly=PINK, tongue=PINK)

# art/siamesecatanim/*.txt 의 hotspot 줄 그대로 — 적용한 사람의 손에 익은 자리
HOT = {"arrow": (1, 1), "busy": (1, 1), "cross": (15, 15), "hand": (5, 1), "help": (1, 1), "ibeam": (13, 14),
       "move": (15, 15), "nesw": (13, 13), "no": (14, 14), "ns": (6, 15), "nwse": (13, 13), "pen": (1, 24),
       "person": (1, 1), "pin": (1, 1), "up": (14, 1), "wait": (13, 14), "we": (15, 7)}


# ---- 얼굴: catkit.face 에 수다쟁이 입 · >< 눈 · 눈마다 시선(사시)을 더한 판 ----

def shut2(cx, cy, rx, kind):
    """감은 눈 · >< 눈. 짙은 가면 위라 선 밑에 옅은 크림 테를 한 겹 깐다 — 없으면 128 에서도 선이 가면에 묻힌다"""
    w = max(0.3, 0.2 * rx)
    if kind == "happy":
        f = arc(cx, cy + rx * 0.55, rx * 0.95, w, pi * 1.2, pi * 0.6)
    elif kind in ("yowl-l", "yowl-r"):                   # > <
        sg = 1 if kind == "yowl-l" else -1
        a, b, c = (cx - sg * rx * 0.6, cy - rx * 0.75), (cx + sg * rx * 0.6, cy), (cx - sg * rx * 0.6, cy + rx * 0.75)
        f = union(capsule(*a, *b, w), capsule(*b, *c, w))
    else:
        f = arc(cx, cy - rx * 0.5, rx * 0.95, w, pi * 0.18, pi * 0.64)
    return [flat(grow(f, max(0.28, 0.5 * w)), PT_L, 0.85), flat(f, EYE)]


def sface(F, mood="open", look=(0.0, 0.0), turn_=0.0, mouth="w", looks=None):
    """mood: open · blink · happy · wink · yowl(><). mouth: w(ω) · talk(동그랗게 벌림) · yowl(크게 벌림) · hmph(꾹) · ''.
    looks 를 주면 (왼눈, 오른눈) 시선이 따로다(사시)"""
    s = F.s
    out = []
    er = max(1.66 * s, 1.32)
    for sg in (-1, 1):
        bx, by = F.w(turn_ + sg * 4.6, 2.9)
        rx = max(1.4 * s, 0.95)
        out.append(soft(ell(bx, by, rx, rx * 0.6), COAT.cheek, 0.7))
    for sg in (-1, 1):
        ex, ey = F.w(turn_ + sg * 3.15, 0.25)
        if mood == "yowl":
            out += shut2(ex, ey, er, "yowl-l" if sg < 0 else "yowl-r")
        elif mood in ("blink", "happy") or (mood == "wink" and sg > 0):
            out += shut2(ex, ey, er, "happy" if mood in ("happy", "wink") else "blink")
        else:
            lk = looks[sg > 0] if looks else look
            out.append(catkit.eye(ex, ey, er, *COAT.iris[sg > 0], look=lk))
    nx, ny = F.w(turn_, 2.05)
    hw = max(0.78 * s, 0.6)
    if mouth in ("talk", "yowl"):                        # 벌린 입: 속은 짙은 분홍, 아래에 혀
        ry = (1.0 if mouth == "talk" else 1.75) * s
        rx = (0.95 if mouth == "talk" else 1.45) * s
        my = ny + hw * 0.5 + ry
        m = ell(nx, my, max(rx, 0.75), max(ry, 0.7))
        out.append(flat(m, lambda x, y: lerp(MOUTH, PINK, smooth(my, my + ry * 0.8, y)), line=max(0.3 * s, 0.32), ink=OUT))
    elif mouth == "hmph":
        out.append(flat(capsule(nx - 0.9 * s, ny + hw * 1.2, nx + 0.9 * s, ny + hw * 1.2, max(0.17 * s, 0.16)), OUT, 0.95))
    elif mouth == "w" and s >= 0.5:
        m = max(0.62 * s, 0.5)
        w = max(0.17 * s, 0.16)
        for sg in (-1, 1):
            out.append(flat(arc(nx + sg * m, ny + hw * 0.35, m, w, pi * 0.08, pi * 0.84), OUT, 0.95))
    nose = rpoly([(nx - hw, ny - hw * 0.45), (nx + hw, ny - hw * 0.45), (nx, ny + hw * 0.6)], hw * 0.3)
    out.append(flat(nose, lambda x, y: lerp(COAT.nose_l, COAT.nose, smooth(ny - hw * 0.4, ny + hw * 0.2, y))))
    return out


def scat(F, mood="open", mouth="w", look=(0.0, 0.0), turn_=0.0, looks=None, **kw):
    """catkit.cat 몸 + 샴냥 얼굴"""
    return cat(F, look=look, turn_=turn_, face_on=False, **kw) + sface(F, mood, look, turn_, mouth, looks)


def chatter(fr, at=(1, 2)):
    """조잘조잘 — 네 장 중 at 장에 입을 연다"""
    return "talk" if round(fr * NF) % 4 in at else "w"


def sbuddy(fr):
    """작은 화살표 + 조잘대는 작은 샴냥"""
    ph = TAU * fr
    F = Frame(13.6, 7.7, 0.58)
    k = round(fr * NF) % NF
    m = "blink" if k == 7 else "open"
    return small_arrow() + scat(F, m, chatter(fr), look=(-0.4, 0.0), sway=0.5 * sin(ph), bob=0.4 * (1 - cos(ph)) / 2)


# ---- 소품 ----

def bchev(cx, cy, dx, dy, L=2.4, a=1.0):
    """(dx, dy) 쪽을 가리키는 파란 화살촉(눈 색) — catkit.chevron 의 분홍을 파랑으로"""
    n = hypot(dx, dy)
    dx, dy = dx / n, dy / n
    px, py = -dy, dx
    f = union(*[capsule(cx, cy, cx - dx * L + s * px * L, cy - dy * L + s * py * L, 0.72) for s in (-1, 1)])
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(BLUE, BLUE_D, smooth(0.36, 0.2, -e)), 1.0), alpha=a)]


def note(cx, cy, sc=1.0, col=BLUE_D, a=1.0):
    """♪ — 기운 타원 머리 + 기둥 + 깃발. (cx, cy) 는 머리 가운데"""
    head = oell(cx, cy, 1.3 * sc, 0.95 * sc, -0.45)
    sx = cx + 1.05 * sc
    stem = capsule(sx, cy - 0.2 * sc, sx, cy - 4.6 * sc, 0.36 * sc)
    flag = capsule(sx, cy - 4.6 * sc, sx + 1.9 * sc, cy - 3.0 * sc, 0.42 * sc)
    f = union(head, stem, flag)
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(col, OUT, smooth(0.3, 0.1, -e) * 0.5), 1.0), alpha=a)]


def bubble(x0, y0, x1, y1, R=2.8):
    """말풍선: 둥근 흰 판 + 왼쪽 위 모서리에서 작은 샴냥 쪽으로 삐져나온 세모 꼬리"""
    b = rbox((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2, R)
    t = poly([(x0 + R + 1.6, y0 + 0.4), (x0 - 2.4, y0 - 2.6), (x0 + 0.4, y0 + R + 1.6)])
    f = smin(0.6, b, t)
    return [base(f), part(f, PAPER, shade=hx("efe6da"), ink=OUT)]


def sticker_fur(F, pieces):
    """[(캐논 거리함수, 부위)…] → 한 바닥 + 부위마다 털빛 조각"""
    fs = [(F.f(g), COAT.fur(p, F)) for g, p in pieces]
    return sticker(*fs)


# ---- 칸마다 장면 (art 좌표, 화살표 칸은 catkit 빼꼼) ----

def sc_busy(fr):
    out = sbuddy(fr)
    k = round(fr * NF) % NF
    out += bubble(15.0, 17.6, 30.2, 27.6)
    on = (k // 3) % 4                                    # 0·1·2 차례로, 3 은 쉼
    for i in range(3):
        lit = i == on
        x, y = 18.8 + i * 3.8, 22.8 - (0.9 if lit else 0.0)
        c = BLUE if lit else PT_L
        out.append(flat(circle(x, y, 1.25), c, line=0.35, ink=BLUE_D if lit else PT))
    return out


def sc_help(fr):
    out = sbuddy(fr)
    k = round(fr * NF) % NF
    dy = -1.0 if k % 6 in (1, 2) else 0.0
    out += bubble(15.0, 14.6 + dy, 30.0, 29.8 + dy, 3.4)
    q = union(arc(22.8, 19.4 + dy, 2.9, 1.1, pi * 0.95, pi * 1.45), capsule(25.3, 21.0 + dy, 22.8, 23.3 + dy, 1.1),
              capsule(22.8, 23.3 + dy, 22.8, 24.2 + dy, 1.1))
    out.append(flat(q, lambda x, y: lerp(BLUE, BLUE_D, smooth(17, 25, y)), line=0.3, ink=BLUE_D))
    out.append(flat(circle(22.8, 27.0 + dy, 1.2), BLUE_D))
    return out


def sc_person(fr):
    """어깨에 샴냥을 두른 사람 — 어깨냥 몸은 사람 머리 뒤로 어깨를 가로지르고, 머리는 왼 어깨, 꼬리는 오른 어깨 아래로 살랑"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    out = sbuddy(fr)
    cx, cy = 24.4, 21.2
    torso = clip_y(ell(cx, cy + 9.4, 6.8, 5.2), 30.6)
    out += [base(torso), part(torso, SHIRT, shade=SHIRT_D)]
    sw = sin(ph)
    lie = ell(cx + 0.4, cy + 4.6, 6.6, 1.9)
    tl = chain([(cx + 6.0, cy + 4.8), (cx + 6.6, cy + 7.2 + 0.3 * sw), (cx + 6.0 + 0.8 * sw, cy + 9.2)], 1.0, 0.85)
    out += [base(lie, tl), part(tl, lambda x, y: lerp(PT_L, PT, smooth(cy + 5, cy + 8, y))), part(lie, CREAM_S)]
    head = circle(cx, cy, 3.4)
    hair = smin(0.6, ell(cx, cy - 1.8, 3.8, 2.3), ell(cx + 3.0, cy + 0.2, 1.2, 2.6))
    out += [base(head, hair), part(head, SKIN, shade=hx("e8bfa0")), part(hair, HAIR, shade=hx("3e2b22"))]
    for sg in (-1, 1):
        ex = cx + sg * 1.3 - 0.4
        if k % 6 == 4:
            out.append(flat(arc(ex, cy + 0.9, 0.55, 0.2, pi * 1.15, pi * 0.7), OUT))
        else:
            out.append(flat(ell(ex, cy + 0.5, 0.45, 0.62), OUT))
        out.append(soft(ell(ex + sg * 0.9, cy + 1.7, 0.75, 0.45), COAT.cheek, 0.8))
    F = Frame(cx - 5.6, cy + 2.6, 0.36)                  # 왼 어깨에 얹은 어깨냥 머리
    out += scat(F, "blink" if k % 6 == 2 else "open", "", body=False, paws=False, tail=False)
    pw = ell(cx - 3.0, cy + 4.9, 1.0, 0.7)
    out += [base(pw), part(pw, PT, sh=0.0)]
    return out


def sc_pin(fr):
    out = sbuddy(fr)
    hop = abs(sin(pi * fr))
    cx, cy = 22.6, 15.2 - 2.6 * hop
    out.insert(0, layer(ell(22.8, 29.0, 3.4 - 0.8 * hop, 0.75), lambda *a: (BLUE_D, 0.3)))
    f = smin(1.0, circle(cx, cy, 5.6), poly([(cx - 4.6, cy + 2.6), (cx + 4.6, cy + 2.6), (cx, cy + 11.4)]))
    out += [base(f), part(f, lambda x, y: lerp(SIGN_L, SIGN, smooth(cy - 5, cy - 1.5, y + 0.6 * (x - cx))), shade=SIGN_D, ink=SIGN_D)]
    out.append(flat(circle(cx, cy, 3.6), PAPER, line=0.5, ink=SIGN_D))
    out += note(cx - 0.6, cy + 1.3, 0.78, BLUE_D)
    return out


def sc_cross(fr):
    """조준선(가운데 비움) 한가운데 나비 몸통이 핫스팟. 아래에서 고개 내민 샴냥이 두 눈을 안쪽 위로 모아 노려본다"""
    k = round(fr * NF) % NF
    C_ = 15.5
    lines = union(capsule(2.6, C_, 8.6, C_, 0.5), capsule(22.4, C_, 28.4, C_, 0.5), capsule(C_, 2.6, C_, 8.4, 0.5))
    out = [base(lines), flat(lines, OUT)]
    F = Frame(C_, 25.6, 0.8)
    look = ((0.9, -1.0), (-0.9, -1.0))
    out += scat(F, "blink" if k == 9 else "open", "w", looks=look, body=False, paws=False, tail=False)
    for sg in (-1, 1):                                   # 볼 바깥 수염
        for j in (-1, 1):
            a, b = F.w(sg * 7.6, 2.2 + j * 0.8)
            out.append(flat(capsule(a, b, a + sg * 2.4, b + j * 0.7, 0.2), OUT))
    up = k % 4 < 2                                       # 날개 폈다 · 접었다
    wy = 0.0 if up else 0.4
    wings = []
    for sg in (-1, 1):
        if up:
            wings += [oell(C_ + sg * 2.5, C_ - 1.6, 2.3, 1.7, sg * 0.5), oell(C_ + sg * 2.0, C_ + 1.6, 1.6, 1.3, -sg * 0.4)]
        else:
            wings += [oell(C_ + sg * 1.2, C_ - 1.4 + wy, 0.9, 2.2, sg * 0.15), oell(C_ + sg * 1.0, C_ + 1.4, 0.8, 1.4, 0.0)]
    W = union(*wings)
    out += [base(W), part(W, lambda x, y: lerp(WING, WING_D, smooth(0.5, 3.5, abs(x - C_))), shade=WING_D, ink=BLUE_D, line=0.6)]
    bd = capsule(C_, C_ - 1.6, C_, C_ + 1.8, 0.62)
    out.append(flat(bd, INKC))
    for sg in (-1, 1):
        out.append(flat(capsule(C_, C_ - 1.6, C_ + sg * 1.2, C_ - 3.6, 0.17), INKC))
        out.append(flat(circle(C_ + sg * 1.25, C_ - 3.7, 0.35), INKC))
    return out


def sc_hand(fr):
    """마네키네코 — 든 발 꼭대기가 핫스팟(5, 1). 펼친 장은 젤리, 굽힌 장은 발등 + 까딱 줄"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    bend = k % 6 >= 3
    s = 0.8
    F = Frame(16.4, 13.8, s)
    hand = F.loc(5.7, 3.85 + (0.35 if bend else 0.0))
    out = scat(F, "happy" if bend else "open", "w", turn_=-0.3, look=(-0.5, -0.4), sway=0.5 * sin(ph),
               arms=[((-6.6, 3.6), hand, not bend)], ear_tilt=(-1.0, 0.0))
    coin = F.f(ell(3.1, 8.8, 2.5, 2.8))
    out += [base(coin), part(coin, lambda x, y: lerp(GOLD_L, GOLD, smooth(-1.5, 1.5, x - F.w(3.1, 8.8)[0] + y - F.w(3.1, 8.8)[1])),
                             shade=GOLD_D, ink=hx("8a6418"), line=0.8)]
    mx, my = F.w(3.1, 8.8)
    out.append(flat(rbox(mx, my, 0.45, 1.1, 0.4), GOLD_D, 0.9))
    hold = F.f(ell(1.4, 7.1, 1.9, 1.5))
    out += [base(hold), part(hold, PT, sh=0.6)]
    bx, by = F.w(0.0, 6.0)
    col = F.f(capsule(-2.6, 5.4, 2.6, 5.4, 0.55))
    out += [flat(col, SIGN, line=0.25, ink=SIGN_D)]
    bell = circle(bx, by, 0.95)
    out.append(flat(bell, lambda x, y: lerp(GOLD_L, GOLD, smooth(by - 0.6, by + 0.5, y)), line=0.3, ink=GOLD_D))
    if bend:                                             # 까딱 — 발 왼쪽 짧은 줄 둘
        for j in (-1, 1):
            out.append(flat(capsule(1.8, 4.6 + j * 1.5, 2.6, 4.4 + j * 1.9, 0.26), PT_L))
    return out


def sc_ibeam(fr):
    """글자 커서 I(가운데가 핫스팟) + 앞발을 얹고 조잘대는 샴냥 + 왼쪽에 늘어나는 파란 글자 점"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    X = 13.5
    top, stem, bot = rbox(X, 3.2, 4.6, 1.4, 0.55), rbox(X, 15.5, 1.35, 11.4, 0.4), rbox(X, 27.8, 4.6, 1.4, 0.55)
    ic = PT if k % 6 < 4 else PT_L
    I = union(top, stem, bot)
    out = [base(I), part(I, ic, shade=PT_D if ic == PT else PT, ink=OUT, line=0.9)]
    n = 1 + k // 3
    for i in range(n):                                   # 새 글자는 늘 I 바로 왼쪽, 앞 글자가 밀려난다
        x = 9.8 - (n - 1 - i) * 2.8
        new = i == n - 1
        out.append(flat(circle(x, 14.5, 1.0), BLUE if new else BLUE_L, line=0.3, ink=BLUE_D))
    F = Frame(23.4, 13.2, 0.6)
    hand = F.loc(16.6, 15.6)
    out += scat(F, "open", "talk" if k % 3 == 1 else "w", look=(-1.0, 0.2), turn_=-1.0, sway=0.5 * sin(ph),
                arms=[((-5.6, 4.6), hand, False)], paws=True)
    return out


def sc_move(fr):
    """위 · 오른쪽 · 아래 · 왼쪽으로 세 장마다 콩 — 가는 쪽 화살촉만 짙다, 뛰는 장에 뒤로 바람 줄"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    dirs = ((0, -1), (1, 0), (0, 1), (-1, 0))
    d = dirs[k // 3]
    st = k % 3
    off = (0.0, 0.9, 1.8)[st]
    out = []
    for dd in dirs:
        lit = dd == d
        out += bchev(15.5 + dd[0] * 13.6, 15.5 + dd[1] * 13.6, dd[0], dd[1], 2.2, 1.0 if lit else 0.4)
    hop = -1.0 if st == 1 else 0.0
    F = Frame(15.5 + d[0] * off, 12.8 + d[1] * off + hop, 0.62)
    if st >= 1:
        bx, by = F.w(-d[0] * 9.5, -d[1] * 13.0 + 6.0)
        px, py = -d[1], d[0]
        for j in (-1.6, 0.0, 1.6):
            out.append(flat(capsule(bx + px * j, by + py * j, bx + px * j - d[0] * 2.0, by + py * j - d[1] * 2.0, 0.32), BLUE_L, 0.8))
    out += scat(F, "blink" if k == 7 else "open", "w", look=(d[0] * 0.8, d[1] * 0.8), turn_=d[0] * 0.8, sway=0.5 * sin(2 * ph))
    return out


def sc_ns(fr):
    """앉아서 목을 쭉 빼고 야~옹 — 목이 늘면 입이 열리고 줄면 닫힌다. 핫스팟(6, 15)은 목께"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    s = max(0.0, sin(ph))
    o = 0.6 if sin(ph) > 0.3 else 0.0
    out = bchev(6.5, 1.9 - o, 0, -1, 2.2, 1.0 if o else 0.75) + bchev(6.5, 29.1 + o, 0, 1, 2.2, 1.0 if o else 0.75)
    sc = 0.64
    Fb = Frame(6.5, 13.0, sc)
    lift = 5.4 * s
    Fh = Frame(6.5, 13.0 - lift * sc, sc)
    tp = [(3.6, 10.4), (7.0, 10.8), (8.6, 8.2), (8.2, 5.6 + 0.4 * sin(ph)), (7.2, 4.4 + 0.6 * sin(ph))]
    pieces = [(chain(tp, 2.3, 2.1), "tail"), (ell(0, 7.7, 5.2, 4.4), "body"),
              (ell(-2.45, 11.35, 1.95, 1.4), "paw"), (ell(2.45, 11.35, 1.95, 1.4), "paw"),
              (capsule(0, 4.0, 0, 3.0 - lift, 3.5), "body")]
    out += sticker_fur(Fb, pieces)
    mood = "blink" if k == 0 else "open"
    mouth = "yowl" if s > 0.6 else "talk" if s > 0.25 else "w"
    out += scat(Fh, mood, mouth, look=(0.0, -0.5), body=False, paws=False, tail=False)
    return out


def _stretch(fr, *a, chev=(), **kw):
    """catkit.stretch + 파란 화살촉(stretch 의 분홍 대신 같은 박자로)"""
    out = stretch(fr, *a, **kw)
    o = 0.6 if sin(TAU * fr) > 0.3 else 0.0
    for (x, y, dx, dy) in chev:
        out += bchev(x + dx * o, y + dy * o, dx, dy, 2.2, 1.0 if o else 0.75)
    return out


def sc_we(fr):
    return _stretch(fr, (15.8, 10.6), 0.0, 13.0, 0.6, chev=[(1.9, 8.0, -1, 0), (29.1, 8.0, 1, 0)], head=(0.0, -1.0), hoff=2.6)


def sc_nwse(fr):
    return _stretch(fr, (14.6, 14.6), pi / 4, 13.0, 0.6, chev=[(3.6, 3.6, -1, -1), (27.4, 27.4, 1, 1)], head=(0.45, -0.9), hoff=1.8)


def sc_nesw(fr):
    return _stretch(fr, (13.6, 14.2), 3 * pi / 4, 13.0, 0.6, chev=[(27.4, 3.6, 1, -1), (3.6, 27.4, -1, 1)], head=(-0.45, -0.9), hoff=1.8)


def sc_no(fr):
    """금지 표지 앞 — 장 0–6 입 크게 벌리고 눈 >< 로 냐아앙(머리 들썩), 7–11 입 꾹 · 눈 감고 흥. 오른쪽에 느낌표.
    빗금은 몸 위 · 머리 아래 — 머리를 빗금 앞으로 한 번 더 그려 냥이가 표지 사이로 고개를 내민 꼴(얼굴이 안 먹히게)"""
    k = round(fr * NF) % NF
    yowl = k < 7
    C_ = 14.5
    R = 12.5
    ink = lambda x, y: lerp(SIGN_L, SIGN, smooth(C_ - 10, C_ - 4, y + 0.5 * x - 0.5 * C_))
    slash = capsule(C_ - 7.7, C_ - 7.7, C_ + 7.7, C_ + 7.7, 1.35)
    F = Frame(C_ - 0.6, 11.4 - (0.5 if yowl and k % 2 else 0.0), 0.66)
    kw = dict(sway=0.3, turn_=0.0 if yowl else 0.6)
    mood, mouth = ("yowl", "yowl") if yowl else ("blink", "hmph")
    out = scat(F, mood, mouth, **kw)
    out += [base(slash), part(slash, ink, shade=SIGN_D, ink=SIGN_D, line=0.8)]
    out += scat(F, mood, mouth, body=False, paws=False, tail=False, **kw)
    if yowl or k % 2:
        ex = union(capsule(22.5, 9.4, 22.2, 12.4, 0.75), circle(22.0, 14.4, 0.8))
        out += [base(ex), part(ex, SIGN, shade=SIGN_D, ink=SIGN_D, line=0.5)]
    rg = ring(C_, C_, R - 1.25, 1.25)
    out += [base(rg), part(rg, ink, shade=SIGN_D, ink=SIGN_D, line=0.8)]
    return out


def sc_pen(fr):
    """꼬리 끝을 붓 삼아 쓴다 — 끝(1, 24)이 핫스팟이라 그대로, 꼬리 중간이 물결치고 먹 줄이 오른쪽으로 길어진다"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    out = []
    n = 2 + 2 * k                                        # 먹 줄: 꼬불꼬불 글씨
    pts = [(3.0 + 0.95 * i, 27.0 + 0.9 * sin(i * 1.3)) for i in range(n)]
    for a, b in zip(pts, pts[1:]):
        out.append(flat(capsule(*a, *b, 0.5), INKC))
    F = Frame(22.4, 11.6, 0.66)
    w = 1.0 * sin(ph)
    tp = [(20.6, 20.6), (16.4, 22.6 + 0.3 * w), (11.2, 20.4 + w), (6.6, 20.8 - w), (3.6, 22.6), (2.1, 24.4)]
    tail = chain(tp, 1.45, 1.0)
    out += [base(tail), part(tail, lambda x, y: lerp(PT_L, PT, smooth(18, 10, x)))]
    out += scat(F, "blink" if k == 6 else "open", "w", look=(-0.9, 0.8), turn_=-1.2, sway=0.0, tail=False)
    out.append(flat(circle(1.75, 24.75, 0.75), INKC))   # 먹 머금은 붓끝
    return out


def sc_up(fr):
    """꼬리를 머리 오른쪽으로 곧게 세운다 — 끝은 왼쪽으로 만 물음표 갈고리, 꼭대기(14, 1)가 핫스팟. 갈고리 끝만 까딱"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    sw = sin(ph)
    s = 0.78
    F = Frame(8.0, 15.4, s)
    art = [(12.0, 22.6), (15.6, 20.4), (16.4, 13.0), (16.4, 6.0), (15.6, 3.2), (14.5, 2.75),
           (13.0, 3.3 + 0.2 * sw), (12.1 + 0.5 * sw, 5.0 + 0.3 * sw)]
    out = scat(F, "happy" if k % 6 < 3 else "open", "w", look=(0.5, -0.6), turn_=0.3,
               tail_pts=[F.loc(*p) for p in art])
    return out


def sc_wait(fr):
    """고개를 까딱이며 노래 — 입이 열렸다 닫히고, 음표 둘이 엇갈려 둥실 떠오르며 옅어진다"""
    ph = TAU * fr
    k = round(fr * NF) % NF
    tilt = sin(ph)
    F = Frame(13.5, 11.4, 0.78, 0.09 * tilt)
    out = []
    for i in range(2):
        t = ((k + i * 6) % NF) / NF
        x = (4.2 if i == 0 else 25.4) + 1.6 * sin(TAU * t + i)
        y = 15.0 - 10.0 * t
        out += note(x, y, 0.9, BLUE_D, 1.0 if t < 0.5 else 0.65 if t < 0.8 else 0.35)
    out += scat(F, "open" if k % 4 in (0, 1) else "happy", "talk" if k % 4 in (0, 1) else "w", turn_=0.8 * tilt,
                look=(0.5 * tilt, -0.3), sway=0.6 * sin(2 * ph),
                tail_pts=[(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.4 + 0.6 * tilt, 3.9), (8.2 + 0.9 * tilt, 2.0)])
    return out


SCENE = {"busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "wait": sc_wait,
         "hand": sc_hand, "cross": sc_cross, "ibeam": sc_ibeam, "move": sc_move, "no": sc_no, "pen": sc_pen,
         "up": sc_up, "we": sc_we, "ns": sc_ns, "nwse": sc_nwse, "nesw": sc_nesw}


class SiameseCat(Pet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = SiameseCat(COAT, SCENE, HOT)


def scene(name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
    return PET.cell(name, frame, soft_, tip_body, shape)


register("siamesecat", PET)

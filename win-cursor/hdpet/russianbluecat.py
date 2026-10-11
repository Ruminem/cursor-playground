# SPDX-License-Identifier: Apache-2.0
"""러시안블루(russianbluecatanim) 고화질 — 치비(머리가 몸만 한 통통 냥) · 스티커 채색(고른 먹선 1칸 + 셀 그늘 한 단).

픽셀 판(gen/russianbluecat.py)을 옮겼다. 무늬 없이 매끈한 푸른 은회색 — 머리 · 몸 왼쪽 위에 은빛 털끝 초승달,
오른쪽 아래 그늘 한 칸이라 벨벳처럼 보인다. 에메랄드 눈 · 연보라 코 · ω 미소. 소품의 주인공은 분홍 깃털 낚싯대
(깃털 · 막대 · 줄)이고 신호색(화살촉 · 물음표 · 반짝)은 눈 색 에메랄드다. 칸마다 하는 짓은 픽셀 판 그대로:

  arrow   크림 화살표 빗변 뒤에서 빼꼼(catkit 공용)
  busy    작은 화살표 냥 + 오른쪽 아래 낚싯대 끝에서 줄에 매달린 깃털이 빙글빙글(지나간 자리에 잔상)
  help    작은 화살표 냥 + 에메랄드 물음표, 점 자리에 깃털 하나가 살랑살랑 내려앉는다
  person  작은 화살표 냥 + 깃털 낚싯대를 흔드는 집사(겨자색 옷)
  pin     작은 화살표 냥 + 흰 깃털이 박힌 빨간 지도 핀이 통통
  wait    얌전히 앉아 위에서 흔들리는 깃털에 홀림 — 고개 · 눈이 따라가고 장 9–10 에 앞발로 냥! 미간이 핫스팟
  cross   조준선 가운데 늘어진 깃털(깃대 가운데가 핫스팟) — 양옆에서 앞발 둘이 젤리를 보이며 다가와 장 6–7 에 짝!
  hand    앉아서 깃털 낚싯대를 왼쪽 위로 내민다 — 막대 끝이 핫스팟, 끝에서 늘어진 깃털이 대롱대롱
  ibeam   위아래 가름대를 단 곧게 선 깃털이 I — 오른쪽 냥이 앞발로 깃을 톡톡. 깃대 가운데가 핫스팟
  move    가운데 앉아 위 · 오른쪽 · 아래 · 왼쪽을 차례로 두리번 — 보는 쪽 화살촉이 켜진다
  ns · we · nwse · nesw   깃털을 덮치러 그 축으로 몸을 날린다 — 두 앞발은 머리 양옆 앞으로, 뒷발 · 긴 꼬리는 뒤로.
          몸이 늘었다 줄었다, 양 끝 화살촉이 두근, 장 5–6 에 눈을 꾹. 얼굴은 늘 똑바로
  no      빨간 금지 표지 안에서 눈을 꾹 감고 두 앞발을 가슴 앞에 X — 팔을 콕콕, 장 6–8 에 눈을 떠 힐끔
  pen     엎드려 만년필을 두 앞발로 쥐고 쓴다 — 펜촉(왼쪽 아래)이 핫스팟, 초록 잉크 줄이 자란다
  up      서서 잡은 깃털을 두 앞발로 머리 위에 번쩍 — 깃털 끝(맨 위)이 핫스팟, 눈은 ^^

좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 장면은 NF 장으로 나뉘어 있다(k = round(fr × NF) % NF).
틀(먹선 · 치비 몸 · 빼꼼 · 모양 화살표)은 catkit 에 있고 여기는 털빛 · 소품 · 장면만 둔다.
"""
from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

from . import register, catkit
from .catkit import *  # noqa: F401,F403
from .catkit import Coat, Frame, Pet, base, buddy, cat, face, flat, layer, part, soft, hx, ell, oell, taper, chain, \
    clip_y, NF, sin, cos, hypot, pi

# 픽셀 판 팔레트(gen/russianbluecat.py) 그대로 + HD 에 쓸 밝은 · 짙은 한 단
OUT, EYE = hx("2c3244"), hx("142019")
FUR, FUR_D, SHEEN = hx("8fa0b8"), hx("7788a2"), hx("bccadc")          # 푸른 은회색 · 그늘 · 은빛 털끝
PAW = hx("aebcd0")                                                     # 발(조금 밝게, 흰 양말 없음)
PINK_R, NOSE, NOSE_L = hx("eea2b8"), hx("b07a98"), hx("cfa3bd")        # 볼 · 귀 속 · 젤리 / 연보라 코
GREEN, GREEN_D, GREEN_L = hx("2fc278"), hx("1a8a52"), hx("9cf0c6")     # 에메랄드 눈 · 신호색
RIM = hx("e6e8f0")
FEA, FEA_L, FEA_D, QUILL = hx("f0628c"), hx("ffaec4"), hx("c8406a"), hx("fff4f2")   # 깃털
STICK, STICK_L, STICK_D, STRING = hx("d0a468"), hx("e6c48e"), hx("9a7038"), hx("5c6274")
INK_G = hx("1f9a5c")                                                   # 초록 잉크
PEN, PEN_D, NIB, NIB_D, BAND = hx("2d6a58"), hx("1d4a3c"), hx("d4d8e2"), hx("98a0b2"), hx("e0b44c")
SKIN, SKIN_D, HAIR, HAIR_D = hx("f7d7bc"), hx("e8bfa0"), hx("5a3e30"), hx("3e2b22")
SHIRT, SHIRT_D = hx("e3b341"), hx("b88a22")                            # 집사 옷(푸른 냥이와 갈리게 겨자색)
SIGN, SIGN_D, SIGN_L = hx("d64541"), hx("9e2b28"), hx("ef7a72")


def velvet(F, cu, cv, ru, rv):
    """벨벳 털: 부위 타원(캐논) 테두리 안쪽 왼쪽 위에 은빛 털끝 초승달. 오른쪽 아래 그늘은 part 의 그늘 띠가 맡는다"""
    def col(x, y):
        u, v = F.loc(x, y)
        du, dv = (u - cu) / ru, (v - cv) / rv
        g = hypot(du, dv) or 1e-9
        d = -(du + dv) / (g * 1.4142)
        return lerp(FUR, SHEEN, smooth(0.5, 0.8, g) * smooth(0.2, 0.75, d))
    return col


class BlueCoat(Coat):
    """무늬 없는 푸른 은회색 — 머리 · 몸은 벨벳 털끝, 귀는 왼쪽이 은빛, 발은 밝은 회색"""

    def fur(self, part, F=None, turn_=0.0):
        if part in ("paw", "hand", "front", "back"):
            return PAW
        if F is None:
            return self.base
        if part == "head":
            return velvet(F, 0.0, 0.2, 7.4, 5.8)
        if part == "body":
            return velvet(F, 0.0, 7.7, 5.4, 4.4)
        if part == "ear":
            return lambda x, y: lerp(SHEEN, FUR, smooth(-0.5, 0.5, F.loc(x, y)[0]))
        return self.base


COAT = BlueCoat(FUR, FUR_D, OUT, EYE, RIM, ((GREEN, GREEN_D, GREEN_L),) * 2, ear=PINK_R, cheek=PINK_R,
                nose=NOSE, nose_l=NOSE_L, jelly=PINK_R)

# 픽셀 판 art 파일 머리의 핫스팟(art 칸) 그대로 — 생성기 HOT 은 자르기 전 자리라 art 를 따른다
HOT = {"arrow": (1, 1), "busy": (1, 1), "cross": (15, 15), "hand": (3, 1), "help": (1, 1), "ibeam": (5, 14),
       "move": (15, 15), "nesw": (15, 15), "no": (15, 15), "ns": (7, 15), "nwse": (15, 15), "pen": (1, 28),
       "person": (1, 1), "pin": (1, 1), "up": (8, 1), "wait": (10, 16), "we": (15, 7)}


def kf(fr):
    return round(fr * NF) % NF


# ---- 얼굴: 꾹 감은 눈 ----

def face_shut(F, turn_=0.0, mouth="w"):
    """catkit.face 의 눈 둘(볼 둘 다음 자리)만 꾹 감은 > < 로 바꾼다 — 졸린 ∪ 와 갈리게"""
    out = face(F, "blink", (0.0, 0.0), turn_, mouth)
    er = max(1.66 * F.s, 1.32)
    w = max(0.3, 0.22 * er)
    for i, sg in ((2, -1), (3, 1)):
        ex, ey = F.w(turn_ + sg * 3.15, 0.25)
        a, b = er * 0.75, er * 0.5
        tipx = ex + sg * a * 0.55                       # 꼭짓점이 코 쪽
        f = union(capsule(ex - sg * a * 0.6, ey - b, tipx, ey, w), capsule(tipx, ey, ex - sg * a * 0.6, ey + b, w))
        out[i] = flat(f, EYE)
    return out


# ---- 소품: 깃털 · 낚싯대 · 화살촉 ----

def feather(p0, p1, w=3.0, ph=0.0, bend=0.0):
    """깃털: p0 깃대 밑동 → p1 끝. 밑동 15% 는 흰 깃대, 나머지는 통통한 분홍 깃(결이 ph 로 흐름).
    bend 는 끝으로 갈수록 옆으로 휘는 정도(작은 깃털이 곧으면 분홍 보석으로 읽혔다 — 픽셀 판 주석)"""
    x0, y0 = p0
    ex, ey = p1[0] - x0, p1[1] - y0
    L = hypot(ex, ey) or 1e-9
    ux, uy = ex / L, ey / L

    def loc(x, y):
        da, db = x - x0, y - y0
        t = da * ux + db * uy
        return t, -da * uy + db * ux - bend * L * (t / L) ** 2
    vane = ell(0.58 * L, 0.0, 0.42 * L, w)
    quill = capsule(0.0, 0.0, 0.3 * L, 0.0, 0.42)
    f = lambda x, y: min(vane(*loc(x, y)), quill(*loc(x, y)))  # noqa: E731
    small = w < 2.4

    def col(x, y):
        t, s = loc(x, y)
        if small:                                       # 작은 깃털은 흰 깃대 줄 없이 두 쪽 빛깔로만
            c = lerp(FEA_L, FEA, smooth(-0.3, 0.3, s))
            return lerp(QUILL, c, smooth(0.1 * L, 0.2 * L, t))
        c = lerp(FEA, FEA_L, 0.85 * smooth(-0.35, 0.35, sin((t - abs(s) * 0.9 + ph) / 1.7 * pi)))
        return lerp(c, QUILL, smooth(0.5, 0.25, abs(s)) * smooth(0.9 * L, 0.8 * L, t))
    return f, col


def feather_l(p0, p1, w=3.0, ph=0.0, bend=0.0):
    f, col = feather(p0, p1, w, ph, bend)
    return [base(f), part(f, col, shade=FEA_D, ink=FEA_D, sh=0.5, line=0.85)]


def rod(a, b, r=0.62):
    f = capsule(a[0], a[1], b[0], b[1], r)
    return [base(f), part(f, lambda x, y: STICK, shade=STICK_D, line=0.8, sh=0.0)]


def string(a, b, r=0.26):
    return [flat(capsule(a[0], a[1], b[0], b[1], r), STRING)]


def gchev(cx, cy, dx, dy, L=2.2, a=1.0):
    """(dx, dy) 쪽을 가리키는 에메랄드 화살촉 — catkit.chevron 의 분홍 대신 눈 색"""
    n = hypot(dx, dy)
    dx, dy = dx / n, dy / n
    px, py = -dy, dx
    f = union(*[capsule(cx, cy, cx - dx * L + s * px * L, cy - dy * L + s * py * L, 0.72) for s in (-1, 1)])
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(GREEN, GREEN_D, smooth(0.36, 0.2, -e)), 1.0), alpha=a)]


def gspark(cx, cy, L=2.0, w=0.6, a=1.0):
    f = union(poly([(cx - L, cy), (cx, cy - w), (cx + L, cy), (cx, cy + w)]),
              poly([(cx, cy - L), (cx + w, cy), (cx, cy + L), (cx - w, cy)]))
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(lerp(GREEN_L, GREEN, smooth(0.2, 1.2, hypot(x - cx, y - cy))),
                                                       GREEN_D, smooth(0.3, 0.12, -e)), 1.0), alpha=a)]


def sticker_parts(fs_cols):
    """[(f, 색)…] → 바닥 하나 + 조각마다 part(털빛 그늘 · 먹선)"""
    return [base(*[f for f, _ in fs_cols])] + [part(f, c) for f, c in fs_cols]


# ---- 칸마다 장면 (art 좌표, 화살표 칸은 catkit 빼꼼) ----

def sc_busy(fr):
    """오른쪽 아래 낚싯대 끝(가운데)에서 줄에 매달린 깃털이 빙글빙글 — 지나간 두 자리에 옅은 분홍 잔상"""
    out = buddy(fr)
    k = kf(fr)
    cx, cy, R = 21.6, 21.6, 5.4
    a = TAU * k / NF - pi / 2
    for j, al in ((2, 0.3), (1, 0.55)):
        aj = a - j * TAU / NF
        out.append(soft(ell(cx + R * cos(aj), cy + R * sin(aj), 1.5, 1.5), FEA_L, al))
    out += rod((29.0, 29.0), (cx, cy))
    fx, fy = cx + R * cos(a), cy + R * sin(a)
    out += string((cx, cy), (fx, fy))
    ta = a + pi / 2                                       # 깃털은 도는 쪽 뒤로 끌린다
    p0 = (fx, fy)
    p1 = (fx - 4.4 * cos(ta) + 1.2 * cos(a), fy - 4.4 * sin(ta) + 1.2 * sin(a))
    out += feather_l(p0, p1, 1.9, k, 0.2)
    return out


def sc_help(fr):
    """에메랄드 물음표 — 점 자리에는 깃털 하나가 좌우로 흔들리며 살랑 내려앉는다"""
    out = buddy(fr)
    q = union(arc(22.6, 14.6, 3.7, 1.25, pi * 0.95, pi * 1.42), capsule(25.4, 16.6, 22.6, 19.2, 1.25),
              capsule(22.6, 19.2, 22.6, 20.8, 1.25))
    out += [base(q), part(q, lambda x, y: lerp(GREEN_L, GREEN, smooth(11.0, 15.0, y)), shade=GREEN_D, ink=GREEN_D, line=0.85)]
    ph = TAU * fr
    sw = sin(ph)
    bx, by = 22.6 + 1.8 * sw, 25.4 + 0.8 * abs(cos(ph))
    tilt = 0.45 * sw
    p0 = (bx - 3.4 * cos(tilt), by - 3.4 * sin(tilt))
    p1 = (bx + 3.4 * cos(tilt), by + 3.4 * sin(tilt))
    out += feather_l(p0, p1, 1.9, kf(fr), -0.18)
    return out


def sc_person(fr):
    """깃털 낚싯대를 흔드는 집사(사람 흉상) — 막대 끝이 까딱이고 줄 끝 깃털이 흔들린다"""
    ph = TAU * fr
    k = kf(fr)
    out = buddy(fr)
    cx, cy = 21.0, 23.0
    sw = sin(ph)
    fist = (27.2, 20.8)
    tip = (21.8 + 0.8 * sw, 4.4)                        # 막대를 안쪽으로 기울여 깃털이 판 오른쪽 밖으로 안 나가게
    ang = 0.45 * sin(ph - 0.8)
    fx, fy = tip[0] + 4.2 * sin(ang), tip[1] + 4.2 * cos(ang)
    out += string(tip, (fx, fy))
    out += feather_l((fx, fy), (fx + 3.0 * sin(ang * 1.5), fy + 5.2 * cos(ang * 1.5)), 1.8, k, -0.22)
    out += rod(fist, tip, 0.55)
    body = clip_y(ell(cx, cy + 8.4, 7.0, 5.4), 30.4)
    head = circle(cx, cy, 4.2)
    hair = smin(0.6, ell(cx, cy - 2.4, 4.6, 2.5), ell(cx - 3.8, cy - 0.6, 1.2, 2.0), ell(cx + 3.8, cy - 0.6, 1.2, 2.0))
    sleeve = capsule(cx + 4.6, cy + 6.0, fist[0], fist[1] + 1.0, 1.5)
    hand = circle(*fist, 1.45)
    out += [base(body, head, hair, sleeve, hand), part(body, SHIRT, shade=SHIRT_D), part(head, SKIN, shade=SKIN_D),
            part(hair, HAIR, shade=HAIR_D), part(sleeve, SHIRT, shade=SHIRT_D), part(hand, SKIN, shade=SKIN_D)]
    for sg in (-1, 1):
        if k in (4, 5):                                   # 눈웃음
            out.append(flat(arc(cx + sg * 1.6, cy + 0.9, 0.7, 0.2, pi * 1.15, pi * 0.7), EYE))
        else:
            out.append(flat(ell(cx + sg * 1.6, cy + 0.3, 0.55, 0.75), EYE))
        out.append(soft(ell(cx + sg * 2.7, cy + 1.8, 0.9, 0.55), PINK_R, 0.8))
    out.append(flat(arc(cx, cy + 1.5, 0.9, 0.22, pi * 0.15, pi * 0.7), SHIRT_D))
    return out


def sc_pin(fr):
    """빨간 지도 핀에 흰 깃털이 박혀 통통 — 땅에 닿을 때 그림자가 진해진다"""
    out = buddy(fr)
    hop = abs(sin(pi * fr))
    cx, cy = 22.6, 15.2 - 2.6 * hop
    out.insert(0, layer(ell(22.8, 29.0, 3.4 - 0.8 * hop, 0.75), lambda *a: (OUT, 0.28 - 0.1 * hop)))
    f = smin(1.0, circle(cx, cy, 5.6), poly([(cx - 4.6, cy + 2.6), (cx + 4.6, cy + 2.6), (cx, cy + 11.4)]))
    out += [base(f), part(f, lambda x, y: lerp(SIGN_L, SIGN, smooth(cy - 5, cy - 1.5, y + 0.6 * (x - cx))), shade=SIGN_D, ink=SIGN_D)]
    q, _ = feather((cx - 2.9, cy + 2.9), (cx + 3.0, cy - 3.0), 1.7)
    out.append(flat(q, QUILL, line=0.4, ink=hx("e2c4c8")))
    out.append(flat(capsule(cx - 2.4, cy + 2.4, cx + 2.0, cy - 2.0, 0.3), FEA))   # 깃대 — 분홍 줄로 흰 깃을 가른다
    return out


def sc_wait(fr):
    """얌전히 앉아 위에서 흔들리는 깃털에 홀림 — 고개 · 눈동자가 깃털을 따라 좌우로, 장 9–10 에 왼 앞발로 냥!"""
    ph = TAU * fr
    k = kf(fr)
    sw = sin(ph)
    s = 0.72
    F = Frame(10.5, 16.5 - 0.25 * s, s)                   # 미간이 핫스팟(10, 16)
    swat = k in (9, 10)
    arms = [((-6.0, 3.8), (-10.4, -9.6 - (0.8 if k == 10 else 0.0)), True)] if swat else []   # 깃털이 왼쪽 위로 간 장 —
    # 왼 앞발을 머리 옆으로 뻗는다(머리 앞으로 들면 미간 핫스팟과 얼굴을 덮음)
    lk = (1.0 if sw > 0.3 else -1.0 if sw < -0.3 else 0.0, -1.0)
    out = cat(F, "open", look=lk, turn_=0.9 * sw, sway=0.5 * sin(2 * ph), arms=arms)
    a = 0.85 * sw                                         # 깃털 진자 — 판 위 가운데에서 줄이 내려온다
    ax, ay = 10.5, -1.0
    fx, fy = ax + 4.4 * sin(a), ay + 4.4 * cos(a)
    out += string((ax, ay), (fx, fy))
    out += feather_l((fx, fy), (fx + 3.8 * sin(a * 1.6), fy + 5.6 * cos(a * 1.6)), 1.9, k, 0.2 if a >= 0 else -0.2)
    return out


def sc_cross(fr):
    """조준선 가운데 위에서 늘어진 깃털(깃대 가운데가 핫스팟). 양옆에서 앞발 둘이 젤리를 보이며 다가오다 장 6–7 에 짝!"""
    k = kf(fr)
    C = 15.5
    close = (0.0, 0.1, 0.25, 0.4, 0.6, 0.85, 1.0, 1.0, 0.7, 0.4, 0.2, 0.05)[k]
    lines = union(capsule(C, 2.4, C, 7.0, 0.42), capsule(C, 23.6, C, 28.6, 0.42))
    hl = union(capsule(2.4, C, 28.6, C, 0.42))
    out = [base(lines, hl), flat(hl, OUT), flat(capsule(C, 23.6, C, 28.6, 0.42), OUT),
           flat(capsule(C, 2.4, C, 7.0, 0.42), STRING)]
    jig = (0.6 if k == 6 else -0.6) if k in (6, 7) else 0.0
    out += feather_l((C, 22.4), (C + jig, 7.6), 3.2, k)
    for sg in (-1, 1):                                    # 앞발 바닥(젤리 쪽)을 깃털로
        px = C + sg * (11.4 - 6.6 * close)
        arm = capsule(C + sg * 18.0, C, px + sg * 1.2, C, 2.5)
        pad = ell(px + sg * 0.3, C, 2.3, 3.0)
        toes = [circle(px - sg * 2.0, C + d, 1.15) for d in (-2.1, 0.0, 2.1)]
        out += [base(arm, pad, *toes), part(arm, FUR), part(pad, PAW)] + [part(t, PAW) for t in toes]
        out.append(flat(ell(px + sg * 0.5, C, 1.05, 1.4), PINK_R))
        for d in (-2.1, 0.0, 2.1):
            out.append(flat(circle(px - sg * 2.1, C + d, 0.55), PINK_R))
    if k in (6, 7):
        for x, y in ((10.6, 9.8), (20.4, 9.8), (10.6, 21.2), (20.4, 21.2)):
            out += gspark(x, y, 1.9 if k == 6 else 1.4, 0.55)
    return out


def sc_hand(fr):
    """앉아서 깃털 낚싯대를 쥐고 왼쪽 위로 내민다 — 막대 끝이 핫스팟(장마다 같은 자리), 끝에서 늘어진 깃털이 대롱대롱"""
    ph = TAU * fr
    k = kf(fr)
    s = 0.74
    F = Frame(21.2, 17.8, s)
    tip = (3.55, 1.55)
    hand = (-10.0, -3.6)
    hw = F.w(*hand)
    a = 0.14 + 0.24 * sin(ph)                             # 판 왼쪽 끝에 붙어 있어 오른쪽으로 더 흔들린다(잘림 막기)
    ax, ay = tip[0] + 0.4, tip[1] + 0.6
    fx, fy = ax + 6.4 * sin(a), ay + 6.4 * cos(a)
    out = string((ax, ay), (fx, fy))
    out += feather_l((fx, fy), (fx + 3.6 * sin(a * 1.4), fy + 6.0 * cos(a * 1.4)), 1.9, k, 0.2)
    out += rod(tip, (hw[0] + 1.0, hw[1] + 1.0), 0.66)
    out += cat(F, "blink" if k == 9 else "open", look=(-1.0, -1.0), turn_=-1.0, sway=0.6 * sin(ph),
               arms=[((-5.6, 4.0), hand, False)])
    return out


def sc_ibeam(fr):
    """위아래 가름대를 단 곧게 선 깃털이 I(깃대 x=5) — 오른쪽 냥이 앞발로 깃을 톡톡, 칠 때마다 깃 결이 흐른다"""
    k = kf(fr)
    X = 5.5
    bars = union(rbox(X, 1.9, 4.0, 0.7, 0.45), rbox(X, 28.7, 4.0, 0.7, 0.45))
    out = [base(bars), flat(bars, OUT)]
    out += feather_l((X, 27.8), (X, 2.6), 3.0, k * 1.5)
    tap = k % 4 in (1, 2)
    s = 0.64
    F = Frame(18.6, 15.0, s)
    pa = (-12.6 + (1.2 if tap else -0.4), 1.0 + (1.6 if k % 8 < 4 else -1.4))
    out += cat(F, "open", look=(-1.0, 0.0), turn_=-1.2, sway=0.5 * sin(TAU * fr), arms=[((-4.0, 5.0), pa, True)])
    if tap:
        for y in (8.0 + k % 3, 21.0 - k % 3):
            out += gspark(10.4, y, 1.3, 0.45)
    return out


def sc_move(fr):
    """가운데 얌전히 앉아 두리번 — 장 0–2 위, 3–5 오른쪽, 6–8 아래, 9–11 왼쪽. 보는 쪽 화살촉이 짙게 켜진다"""
    ph = TAU * fr
    k = kf(fr)
    dirs = ((0, -1), (1, 0), (0, 1), (-1, 0))
    cur_ = dirs[k // 3]
    out = []
    for d in dirs:
        on = d == cur_
        o = 0.6 if on and k % 3 == 1 else 0.0
        out += gchev(15.5 + d[0] * (13.4 + o), 15.5 + d[1] * (13.4 + o), d[0], d[1], 2.2, 1.0 if on else 0.35)
    F = Frame(15.5, 12.4 + 0.5 * cur_[1], 0.66)
    out += cat(F, "open", look=cur_, turn_=1.1 * cur_[0], sway=0.5 * sin(ph),
               ear_tilt=(0.6 * max(0, -cur_[0]), 0.6 * max(0, cur_[0])))
    return out


def pounce(fr, C_, ang, e0, chev, up=(0.0, -1.0), hoff=2.2, s=0.6):
    """깃털을 덮치러 몸을 날린 냥 — ang 축(앞 → 뒤)을 따라 굵은 몸이 e0 ± 6% 로 늘었다 줄었다. 앞 끝에 똑바른 머리
    (몸 축에서 up 쪽으로 hoff 만큼 올림), 그 앞으로 쭉 뻗은 앞발 둘, 뒤 끝에 뒷발 둘과 곧게 뻗은 긴 꼬리.
    up 이 (0, 0) 이면 발이 축 양옆으로 나란하다(위로 솟구치는 ns). 장 5·6 은 눈을 꾹 감고 덮친다.
    흰냥이 기지개(catkit.stretch)와 몸 비례를 맞추되 꼬리가 말리지 않고 곧다 — 픽셀 판의 쭉 뻗은 꼬리"""
    ph = TAU * fr
    k = kf(fr)
    e = e0 * (1 + 0.06 * sin(ph))
    ux, uy = cos(ang), sin(ang)
    px, py = -uy, ux                                     # 축에 수직
    gx, gy = -up[0], -up[1]                              # 발이 놓일 쪽 = 머리 반대쪽
    cx, cy = C_
    r = 3.3 * s / 0.6
    a0 = (cx - ux * e / 2, cy - uy * e / 2)              # 앞 끝(머리 쪽)
    a1 = (cx + ux * e / 2, cy + uy * e / 2)              # 뒤 끝
    bodyf = taper(a0[0], a0[1], r, a1[0], a1[1], r * 0.92)
    pr = 1.85 * s / 0.6
    reach = 0.9 * (1 + sin(ph)) / 2                      # 앞발이 쭉쭉 뻗었다 들어온다
    gs = 1.35 if up != (0.0, 0.0) else 0.0
    side = 0.95 if gs else 1.75
    if gs:
        fronts = [oell(a0[0] - ux * (r + 0.9 + reach) + gx * gs + px * j * side,
                       a0[1] - uy * (r + 0.9 + reach) + gy * gs + py * j * side, pr * 1.15, pr * 0.85, ang) for j in (-1, 1)]
    else:                                                # 솟구치는 냥: 앞발을 가슴 양옆에 — 머리 위에 모으면 토끼 귀,
        fronts = [oell(a0[0] + ux * (r * 1.6 + reach * 0.5) + px * j * (r + 0.2),    # 머리 옆이면 곰 귀로 읽힘
                       a0[1] + uy * (r * 1.6 + reach * 0.5) + py * j * (r + 0.2), pr * 1.1, pr * 0.85, ang) for j in (-1, 1)]
    bg = r * 0.75 if gs else 0.0
    backs = [oell(a1[0] + ux * r * 0.55 + gx * bg + px * j * (0.9 if gs else 1.9),
                  a1[1] + uy * r * 0.55 + gy * bg + py * j * (0.9 if gs else 1.9), pr * 0.95, pr * 0.8, ang) for j in (-1, 1)]
    tw = 0.8 * sin(2 * ph)
    t0 = (a1[0] + ux * r * 0.5, a1[1] + uy * r * 0.5)
    bend = (gx, gy) if gs else (px, py)                  # 꼬리 끝이 살짝 휘는 쪽
    if gs:
        tl = chain([t0, (t0[0] + ux * 2.8 + bend[0] * 0.5 * tw, t0[1] + uy * 2.8 + bend[1] * 0.5 * tw),
                    (t0[0] + ux * 5.0 + bend[0] * (1.2 + tw), t0[1] + uy * 5.0 + bend[1] * (1.2 + tw))], 1.5, 1.25)
    else:                                                # 아래 화살촉을 비켜 꼬리가 옆으로 휜다
        tl = chain([t0, (t0[0] + ux * 2.0 + px * 1.0, t0[1] + uy * 2.0 + py * 1.0),
                    (t0[0] + ux * 2.6 + px * (3.6 + tw), t0[1] + uy * 2.6 + py * (3.6 + tw))], 1.45, 1.25)
    fur = catkit.C.fur
    out = []
    o = 0.6 if sin(ph) > 0.3 else 0.0
    for (x, y, dx, dy) in chev:
        out += gchev(x + dx * o, y + dy * o, dx, dy, 2.2, 1.0 if o else 0.75)
    out.append(base(bodyf, tl, *fronts, *backs))
    out.append(part(tl, fur("tail")))
    for f in backs:
        out.append(part(f, fur("back")))
    out.append(part(bodyf, fur("body")))
    for f in fronts:
        out.append(part(f, fur("front")))
    F = Frame(a0[0] + ux * r * 0.9 + up[0] * hoff, a0[1] + uy * r * 0.9 + up[1] * hoff, s)
    if k in (5, 6):
        out += cat(F, body=False, paws=False, tail=False, face_on=False) + face_shut(F)
    else:
        out += cat(F, "open", look=(-ux, -uy), body=False, paws=False, tail=False)
    return out


def sc_we(fr):
    return pounce(fr, (16.6, 11.2), 0.0, 12.0, [(1.9, 7.5, -1, 0), (29.1, 7.5, 1, 0)], (0.0, -1.0), 2.8)


def sc_ns(fr):
    return pounce(fr, (7.5, 15.6), pi / 2, 8.0, [(7.5, 1.9, 0, -1), (7.5, 29.1, 0, 1)], (0.0, 0.0), 0.0, 0.56)


def sc_nwse(fr):
    return pounce(fr, (14.8, 14.8), pi / 4, 12.0, [(3.6, 3.6, -1, -1), (27.4, 27.4, 1, 1)], (0.45, -0.9), 1.8)


def sc_nesw(fr):
    return pounce(fr, (16.2, 14.8), 3 * pi / 4, 12.0, [(27.4, 3.6, 1, -1), (3.6, 27.4, -1, 1)], (-0.45, -0.9), 1.8)


def sc_no(fr):
    """빨간 금지 표지 안에서 눈을 꾹 감고 두 앞발을 가슴 앞에 엇갈려 X(안 돼) — 팔을 콕콕, 장 6–8 에 눈을 떠 힐끔"""
    ph = TAU * fr
    k = kf(fr)
    C = 15.5
    R = 12.6
    sg_ = union(ring(C, C, R - 1.25, 1.25), capsule(C - 7.8, C - 7.8, C + 7.8, C + 7.8, 1.35))
    out = [base(sg_), part(sg_, lambda x, y: lerp(SIGN_L, SIGN, smooth(C - 10, C - 4, y + 0.5 * x - 0.5 * C)),
                          shade=SIGN_D, ink=SIGN_D, line=0.8)]
    s = 0.6
    F = Frame(C, C - 2.6, s)
    peek = k in (6, 7, 8)
    out += cat(F, "open", look=(-1.0, 0.0), sway=0.4 * sin(2 * ph), face_on=peek)
    if not peek:
        out += face_shut(F)
    lift = 0.6 * sin(2 * ph)
    xs, ps = [], []
    for sg in (-1, 1):                                    # 엇갈린 팔 — 은빛 털끝 빛깔로 몸과 갈린다
        a, b = F.w(sg * 4.2, 10.4), F.w(-sg * 6.6, 4.6 - lift)
        xs.append(capsule(*a, *b, 2.2 * s))
        ps.append(circle(*b, 2.1 * s))
    out += [base(*xs, *ps)] + [part(f, SHEEN) for f in xs] + [part(f, PAW) for f in ps]
    return out


def sc_pen(fr):
    """엎드려 만년필을 두 앞발로 쥐고 쓴다 — 펜촉(왼쪽 아래)이 핫스팟, 지나간 자리에 초록 잉크 줄이 물결치며 자란다"""
    ph = TAU * fr
    k = kf(fr)
    tip = (1.55, 28.45)
    ux, uy = 0.7071, -0.7071
    Lp = 13.4
    out = []
    for i in range(2 + k):                                # 잉크 줄
        x0 = 3.8 + 1.7 * i
        out.append(flat(capsule(x0, 29.7 + 0.35 * sin(x0 * 0.9), x0 + 1.4, 29.7 + 0.35 * sin((x0 + 1.4) * 0.9), 0.5), INK_G))
    s = 0.66
    F = Frame(15.4, 13.2, s)
    sw = sin(ph)
    loaf = F.f(smin(1.2, ell(5.6, 7.6, 9.0, 4.4), ell(2.0, 9.8, 9.4, 2.4)))
    tl = F.f(chain([(13.2, 7.0), (16.0, 3.4), (15.0 + 1.4 * sw, -1.4)], 2.0, 1.7))
    out += cat(F, "wink" if k == 6 else "open", look=(-1.0, 1.0), turn_=-0.8, body=False, paws=False, tail=False,
               extra_under=[(tl, FUR), (loaf, velvet(F, 5.6, 7.6, 9.0, 4.4))])
    nib = poly([tip, (tip[0] + ux * 3.4 - uy * 1.45, tip[1] + uy * 3.4 + ux * 1.45),
                (tip[0] + ux * 3.4 + uy * 1.45, tip[1] + uy * 3.4 - ux * 1.45)])
    end = (tip[0] + ux * Lp, tip[1] + uy * Lp)
    body = capsule(tip[0] + ux * 3.4, tip[1] + uy * 3.4, *end, 1.45)

    def pcol(x, y):
        t = (x - tip[0]) * ux + (y - tip[1]) * uy
        c = BAND if Lp - 4.2 < t < Lp - 3.2 else PEN
        return lerp(c, hx("4a8a76"), 0.6 * smooth(0.2, -0.8, (x - tip[0]) * -uy + (y - tip[1]) * ux))

    def ncol(x, y):
        sx = (x - tip[0]) * -uy + (y - tip[1]) * ux
        t = (x - tip[0]) * ux + (y - tip[1]) * uy
        return lerp(NIB, OUT, smooth(0.3, 0.12, abs(sx)) * smooth(1.0, 1.5, t))   # 가운데 틈
    out += [base(nib, body), part(body, pcol, shade=PEN_D, ink=PEN_D, line=0.8), part(nib, ncol, shade=NIB_D, line=0.7)]
    paws_ = []
    for t, sh_ in ((5.8, (-4.6, 7.8)), (8.8, (-0.6, 8.6))):  # 만년필을 감싼 앞발 둘
        g = F.loc(tip[0] + ux * t, tip[1] + uy * t)
        a = F.f(taper(sh_[0], sh_[1], 2.6, g[0], g[1], 2.3))
        p = F.f(ell(g[0], g[1], 2.7, 2.45))
        paws_.append((a, p))
    out.append(base(*[g for ap in paws_ for g in ap]))
    for a, p in paws_:
        out += [part(a, FUR), part(p, PAW)]
    return out


def sc_up(fr):
    """잡은 깃털을 앞발 하나로 머리 옆에 번쩍(잡았다!) — 깃털 끝(맨 위)이 핫스팟이라 깃털은 그대로 서 있고,
    깃 결이 흐르며 든 앞발이 까딱, 눈은 ^^ 와 뜬 눈을 오간다. 두 팔로 머리 위에 들던 판은 팔이 머리를 덮어
    귀가 사라지고 32 에서 먹색 아치만 남았다"""
    ph = TAU * fr
    k = kf(fr)
    s = 0.64
    X = 8.5
    bob = 0.35 * sin(2 * ph)
    F = Frame(14.0, 20.4, s)
    out = feather_l((X, 14.4 + bob), (X, 1.3), 3.3, -k * 1.2)
    out += cat(F, "happy" if k % 6 < 4 else "open", look=(-0.5, -0.8), turn_=0.25, sway=0.4 * sin(ph),
               arms=[((-7.0, 3.4), F.loc(X, 14.2 + bob), True)], ear_tilt=(-0.6, 0.0))
    return out


SCENE = {"busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "wait": sc_wait,
         "hand": sc_hand, "cross": sc_cross, "ibeam": sc_ibeam, "move": sc_move, "no": sc_no, "pen": sc_pen,
         "up": sc_up, "we": sc_we, "ns": sc_ns, "nwse": sc_nwse, "nesw": sc_nesw}


class RussianBlueCat(Pet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = RussianBlueCat(COAT, SCENE, HOT)


def scene(name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
    return PET.cell(name, frame, soft_, tip_body, shape)


register("russianbluecat", PET)

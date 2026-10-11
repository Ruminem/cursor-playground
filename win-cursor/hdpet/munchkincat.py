# SPDX-License-Identifier: Apache-2.0
"""먼치킨(munchkincatanim) 고화질 — 치비(머리가 몸만 한 통통 냥) · 스티커 채색(고른 먹선 1칸 + 셀 그늘 한 단).

픽셀 먼치킨(gen/munchkincat.py)을 HD 로 옮겼다. 크림 털에 옅은 주황 줄(이마 줄 셋 · 볼 줄 · 옆구리 줄 · 꼬리 고리),
흰 주둥이 · 흰 배 · 흰 양말, 그리고 몸 밑에 뭉툭하게 붙은 **짧은 다리**가 이 냥이의 전부다. 소품은 금방울.
칸마다 하는 짓은 픽셀 판 그대로다.
  arrow  크림 화살표 빗변 뒤에서 빼꼼(catkit peek)
  busy   작은 화살표 먼치킨 + 오른쪽 아래 원을 데굴데굴 도는 금방울, 지나간 자리에 반짝이
  help   작은 화살표 먼치킨 + 분홍 리본 물음표, 점은 달랑대는 금방울
  person 작은 화살표 먼치킨 + 방울 낚싯대를 흔드는 사람
  pin    작은 화살표 먼치킨 + 흰 동그라미 속 금방울이 든 빨간 핀이 통통
  cross  조준선 가운데 리본에 매달린 금방울(핫스팟) — 밑에서 먼치킨이 짧은 앞발을 휘젓지만 안 닿는다
  hand   까치발로 서서 짧은 앞발 하나를 왼쪽 위로 쭉 — 젤리 발끝이 핫스팟, 짧은 뒷다리가 바들바들
  ibeam  미어캣 서기: 큰 머리가 I 의 윗획, 가는 몸이 세로획, 발밑 그림자가 아랫획. 두리번, 배 가운데가 핫스팟
  move   옆모습으로 짧은 다리를 뱅뱅 돌리며 제자리 달리기, 뒤로 흙먼지. 네 방향 금빛 화살촉
  we     옆모습으로 금방울을 앞발로 툭툭 몰고 가다 반 바퀴마다 돌아선다. 양 끝 화살촉
  ns     앉았다 뒷발로 일어나 미어캣처럼 두리번(위아래로 늘었다 줄었다). 위아래 화살촉
  nwse · nesw  대각 풀빛 비탈을 짧은 다리로 오르다 미끄러짐. 몸은 비탈을 따라 눕고 얼굴은 똑바로
  no     빨간 금지 표지 안에서 금방울을 두 앞발로 꼭 껴안고 도리도리(안 줘)
  pen    두 앞발로 쥔 파란 크레용으로 삐뚤빼뚤 — 크레용 끝(왼쪽 아래)이 핫스팟, 파란 줄이 길어진다
  up     금방울을 머리에 이고 미어캣 서기, 짧은 앞발을 벌려 균형 — 방울 꼭지(맨 위)가 핫스팟
  wait   사람처럼 기대앉아 짧은 뒷다리를 앞으로 쭉, 배 위 금방울을 앞발로 톡톡(가운데가 핫스팟)
좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 장면은 NF 장으로 나뉘어 있다(k = round(fr × NF) % NF).
틀(먹선 · 치비 머리 · 얼굴 · 빼꼼 · 모양 화살표)은 catkit 을 쓰고, catkit 에 없는 선 몸(미어캣) · 옆모습 · 눈 꾹(><)은
여기 둔다 — catkit.cat() 은 앉은 몸 하나뿐이라 짧은 다리를 보일 자리가 없다.
"""
from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

from . import register
from .catkit import *  # noqa: F401,F403

# 픽셀 판 팔레트(gen/munchkincat.py) 그대로 — 그늘 · 눈 색만 HD 에서 더함
OUT, EYE = hx("3a2a30"), hx("2a1c22")
FUR, STRIPE, BELLY = hx("f6dcb0"), hx("e9a868"), hx("fffaf0")
SHADE = hx("e6c493")                                       # 셀 그늘(털빛보다 한 단 짙은 크림)
RIM = hx("fbecdc")
IRIS, IRIS_D, IRIS_L = hx("8b5a2b"), hx("4a2c14"), hx("d9a066")   # 픽셀 판은 까만 눈 — 홍채만 따뜻한 갈색
NOSE, CHEEK = hx("e27d90"), hx("f7a3b5")
BELL, BELL_D, BELL_L, BELL_S = hx("f2c230"), hx("c08a1a"), hx("fff2a8"), hx("6e4a10")
RIB, RIB_D = hx("ec6f8e"), hx("b84462")
GOLD, GOLD_D = hx("e8b020"), hx("b8860e")
CRAY, CRAY_D, CRAY_L, PAPER = hx("4a8fd8"), hx("2c64a8"), hx("8cc0f0"), hx("f4efe2")
SKIN, HAIR, SHIRT, SHIRT_D = hx("f7d7bc"), hx("6b4a34"), hx("7cb87a"), hx("4f8a4e")
ROD, ROD_D = hx("8a6a48"), hx("5e4630")
SLOPE, SLOPE_D = hx("b9c8a0"), hx("8ea076")
DUST, DUST_D = hx("d8ccb8"), hx("b4a68e")
SIGN, SIGN_D, SIGN_L = hx("d64541"), hx("9e2b28"), hx("ef7a72")
SWEAT = hx("9fd0f0")

TAIL0 = [(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.4, 3.9), (8.2, 2.0)]   # catkit.cat 기본 꼬리(무늬 고리를 잴 줄)


def mix(a, b, t):
    return a + (b - a) * t


def along(pts):
    """꺾은선 pts → ((u, v) → 가장 가까운 자리까지의 줄 길이, 전체 길이). 꼬리 고리 무늬를 꼬리를 따라 두른다"""
    segs, acc = [], 0.0
    for a, b in zip(pts, pts[1:]):
        L = hypot(b[0] - a[0], b[1] - a[1]) or 1e-9
        segs.append((a[0], a[1], b[0] - a[0], b[1] - a[1], L, acc))
        acc += L

    def at(u, v):
        best, bs = 1e9, 0.0
        for ax, ay, ex, ey, L, s0 in segs:
            t = clamp(((u - ax) * ex + (v - ay) * ey) / (L * L))
            d = hypot(u - ax - ex * t, v - ay - ey * t)
            if d < best:
                best, bs = d, s0 + t * L
        return bs
    return at, acc


# ---- 털빛: 크림 + 옅은 주황 줄 ----

def head_col(F, t):
    """흰 주둥이 · 이마 줄 셋(위로 갈수록 벌어짐) · 볼 줄 둘(양옆) — 원본 skin() 의 자리를 캐논으로"""
    def col(x, y):
        u, v = F.loc(x, y)
        a = u - t
        if (a / 3.2) ** 2 + ((v - 2.95) / 2.0) ** 2 <= 1:
            return BELLY
        if v < -2.6:
            h = -2.6 - v
            for d in (-1, 0, 1):
                if d and v > -3.4:
                    continue
                if abs(u - (t * 0.6 + d * (1.85 + 0.22 * h))) < min(0.72, 0.42 + 0.08 * h):
                    return STRIPE
        if abs(a) > 6.0 and (abs(v - 0.3) < 0.4 or abs(v - 1.7) < 0.4):
            return STRIPE
        return FUR
    return col


def body_col(F, du, cv, rx, ry):
    """몸통: 흰 배 + 옆구리에 비스듬한 줄"""
    def col(x, y):
        u, v = F.loc(x, y)
        a = u - du
        if (a / (rx * 0.56)) ** 2 + ((v - cv - ry * 0.16) / (ry * 0.74)) ** 2 <= 1:
            return BELLY
        if abs(a) > rx * 0.6 and (v - cv + 0.3 + 0.3 * abs(a)) % 2.6 < 0.95:
            return STRIPE
        return FUR
    return col


def tail_col(F, pts):
    """꼬리: 고리 무늬, 끝은 짙게"""
    at, total = along(pts)

    def col(x, y):
        s_ = at(*F.loc(x, y))
        if s_ > total - 0.9:
            return STRIPE
        return STRIPE if (s_ % 2.8) > 1.75 and s_ > 1.2 else FUR
    return col


class MunchCoat(Coat):
    """크림 털 · 흰 양말. 꼬리 무늬는 지금 그리는 꼬리 줄(tail)을 따라 — mcat 이 잠깐 바꿔 끼운다"""
    tail = None

    def fur(self, part, F=None, turn_=0.0):
        if part in ("paw", "hand", "front", "back"):
            return BELLY
        if F is None or part in ("ear", "arm"):
            return FUR
        if part == "head":
            return head_col(F, turn_)
        if part == "body":
            return body_col(F, 0.0, 7.7, 5.4, 4.4)
        if part == "tail":
            return tail_col(F, self.tail or TAIL0)
        return FUR


COAT = MunchCoat(FUR, SHADE, OUT, EYE, RIM, ((IRIS, IRIS_D, IRIS_L), (IRIS, IRIS_D, IRIS_L)), cheek=CHEEK, nose=NOSE)

# 픽셀 판 핫스팟(art 칸) 그대로
HOT = {"arrow": (1, 1), "busy": (1, 1), "cross": (15, 15), "hand": (4, 4), "help": (1, 1), "ibeam": (6, 11),
       "move": (15, 15), "nesw": (15, 15), "no": (14, 14), "ns": (9, 15), "nwse": (15, 15), "pen": (1, 25),
       "person": (1, 1), "pin": (1, 1), "up": (8, 1), "wait": (11, 13), "we": (15, 8)}


def kk(fr):
    return round(fr * NF) % NF


# ---- 몸: catkit.cat 을 감싼 것들 ----

def mcat(F, *a, tail_pts=None, **kw):
    """catkit.cat — 꼬리 무늬가 이 꼬리 줄을 따르게 털빛에 잠깐 알려 준다"""
    COAT.tail = tail_pts
    try:
        return cat(F, *a, tail_pts=tail_pts, **kw)
    finally:
        COAT.tail = None


def mface(F, mood="open", look=(0.0, 0.0), turn_=0.0, mouth="w"):
    """catkit.face + 눈 꾹(squeeze, > <) — 힘줄 때 · 안 줄 때"""
    if mood != "squeeze":
        return face(F, mood, look, turn_, mouth)
    out = face(F, "open", look, turn_, mouth)
    er = max(1.66 * F.s, 1.32)
    w = max(0.3, 0.22 * er)
    for i, sg in ((2, -1), (3, 1)):                       # face() 순서: 볼 둘 · 눈 둘 · 입 · 코
        ex, ey = F.w(turn_ + sg * 3.15, 0.25)
        d = -sg                                           # 꼭짓점이 가운데(코) 쪽
        p0, p1, p2 = (ex - d * er * 0.6, ey - er * 0.62), (ex + d * er * 0.55, ey), (ex - d * er * 0.6, ey + er * 0.62)
        out[i] = flat(union(capsule(*p0, *p1, w), capsule(*p1, *p2, w)), EYE)
    return out


def sole(F, c, R, spread=0.0):
    """발바닥 젤리(발 반지름 R 에 맞춘 크기 — catkit.jellies 는 크기가 고정이라 작은 냥에서 점이 된다)"""
    u, v = c
    out = [flat(F.f(ell(u, v + 0.28 * R, 0.42 * R, 0.33 * R)), COAT.jelly)]
    for dx, dy in ((-0.52 - spread, -0.2), (0.0, -0.46 - spread), (0.52 + spread, -0.2)):
        out.append(flat(F.f(circle(u + dx * R, v + dy * R, 0.2 * R)), COAT.jelly))
    return out


def limbs(F, arms, spread=0.0):
    """앞발들 [(어깨, 손, 젤리)] → 조각 [(f, 색)…] · 젤리 레이어. 어깨가 None 이면 발만(가슴 앞에 모은 미어캣 발).
    굵기는 catkit 팔과 같다 — 더 가늘면 먹선 1칸이 팔을 다 먹어 32 에서 까만 고리가 된다"""
    ra = max(2.7, 2.1 / F.s)
    pieces, jel = [], []
    for sh_, hand, jelly in arms:
        if sh_ is not None:
            pieces.append((F.f(taper(sh_[0], sh_[1], ra, hand[0], hand[1], ra * 0.92)), FUR))
            pieces.append((F.f(ell(hand[0], hand[1], ra * 1.08, ra * 1.0)), BELLY))
        else:                                             # 발만: 먹선을 조금 가늘게 — 1칸이면 가슴에 까만 8 자가 된다
            pieces.append((F.f(ell(hand[0], hand[1], ra * 0.85, ra * 0.78)), BELLY, 0.7))
        if jelly:
            jel += sole(F, hand, ra, spread)
    return pieces, jel


def fronts(F, arms, spread=0.0):
    pieces, jel = limbs(F, arms, spread)
    if not pieces:
        return []
    return [base(*[p[0] for p in pieces])] + [part(p[0], p[1], line=p[2] if len(p) > 2 else LINE) for p in pieces] + jel


def head(F, mood="open", look=(0.0, 0.0), turn_=0.0, arms=(), ear_tilt=(0.0, 0.0), mouth="w"):
    """머리만(귀 · 머리 · 얼굴) + 앞에 내민 앞발"""
    out = mcat(F, body=False, paws=False, tail=False, face_on=False, ear_tilt=ear_tilt)
    return out + fronts(F, arms) + mface(F, mood, look, turn_, mouth)


def stand_geo(up, s, tip=0.0):
    """선 몸 치수(캐논): 몸통 가운데 높이 · 세로 반지름 · 가로 반지름 · 다리 반지름 · 발 높이 · 발바닥 높이.
    up 0 은 앉음(발이 몸 앞에 뭉툭), 1 은 뒷발로 섬(미어캣) — 몸통 밑으로 다리가 1.3칸만 나온다(짧은 다리).
    다리 굵기는 art 로 1.75칸 넘게(먹선 안에 털이 남게)"""
    cv, ry, rx = mix(8.2, 9.4, up), mix(4.2, 4.8, up), mix(5.2, 4.6, up)
    R = max(2.0, 1.75 / s)
    fv = cv + ry - R * 0.3 + (1.3 * up + 0.5 * tip) / s
    return cv, ry, rx, R, fv, fv + R


def stand(F, mood="open", look=(0.0, 0.0), turn_=0.0, arms=None, back_arms=(), held=(), up=1.0, du=0.0, tip=0.0,
          tail_sw=0.0, ear_tilt=(0.0, 0.0), mouth="w", spread=0.0):
    """뒷발로 선 먼치킨(미어캣) → 레이어. 몸통 밑에 짧고 뭉툭한 다리 둘(끝은 흰 양말).
    back_arms 는 머리 뒤로 든 앞발(머리 밑에 깔림), held 는 몸과 앞발 사이에 끼는 소품, du 는 몸만 옆으로 흔들기"""
    cv, ry, rx, R, fv, _ = stand_geo(up, F.s, tip)
    legs = []
    for sg in (-1, 1):
        lx = du + sg * R * 0.78
        top = cv + ry - R * 1.1

        def lc(x, y, fv=fv):
            return BELLY if F.loc(x, y)[1] > fv - R * 0.15 else FUR
        legs.append((F.f(capsule(lx, top, lx + sg * 0.3 * (1 - up), fv, R)), lc))
    torso = (F.f(ell(du, cv, rx, ry)), body_col(F, du, cv, rx, ry))
    bp, bjel = limbs(F, back_arms, spread)
    b = cv + ry
    sw = tail_sw
    tp = [(du + 3.2, b - 1.6), (du + 7.0, b - 0.8), (du + 8.9, b - 3.6), (du + 8.6 + sw, b - 6.6), (du + 7.4 + 1.4 * sw, b - 8.4)]
    out = mcat(F, body=False, paws=False, tail=True, tail_pts=tp, extra_under=[torso] + legs + [p[:2] for p in bp],
               face_on=False, ear_tilt=ear_tilt)
    out += bjel + list(held)
    if arms is None:                                      # 가슴 앞에 모은 미어캣 앞발
        arms = [(None, (du - 2.3, 8.2), False), (None, (du + 2.3, 8.2), False)]
    out += fronts(F, arms, spread)
    return out + mface(F, mood, look, turn_, mouth)


def side(Fb, d=1, gait=0.0, walk=1.0, mood="open", look=(0.7, 0.0), tail_sw=0.0, splay=0.0, head_dv=0.0):
    """옆모습(d=1 오른쪽을 봄): 긴 콩 몸 · 짧은 다리 넷(먼 쪽은 짙게, 뒤에) · 세운 꼬리 · 똑바른 큰 머리.
    Fb 는 몸 가운데 Frame(비탈이면 기울임), 머리는 기울이지 않는다 → (레이어, 머리 Frame)"""
    s = Fb.s
    lr = max(2.0, 1.75 / s)

    def P(u, v):
        return (u * d, v)
    near, far = [], []
    for fx, off, is_near in ((4.4, 0.0, True), (5.3, pi, False), (-4.5, pi, True), (-3.6, 0.0, False)):
        a = gait + off
        sw_ = 1.7 * sin(a) * walk + splay * (1 if fx > 0 else -1)
        lift = 1.0 * max(0.0, cos(a)) * walk
        fv = 4.7 - lift
        f = Fb.f(capsule(*P(fx, 1.2), *P(fx + sw_, fv), lr))

        def lc(x, y, fv=fv, is_near=is_near):
            c = BELLY if Fb.loc(x, y)[1] > fv - 0.4 else FUR
            return c if is_near else lerp(c, STRIPE, 0.4)
        (near if is_near else far).append((f, lc))
    rt = max(1.8, 1.5 * s) / s
    tp = [P(-6.6, -1.2), P(-9.1, -2.9), P(-9.8 + tail_sw, -5.8), P(-8.9 + 1.6 * tail_sw, -8.0)]
    tail = (Fb.f(chain(tp, rt * 1.05, rt * 0.95)), tail_col(Fb, tp))
    body = Fb.f(ell(0, 0, 7.4, 3.9))

    def bc(x, y):
        u, v = Fb.loc(x, y)
        if v > 1.5:
            return BELLY
        if v < 0.9 and (u * d + 40.0) % 2.7 < 1.0:
            return STRIPE
        return FUR
    pieces = far + [tail, (body, bc)] + near
    out = [base(*[p[0] for p in pieces])] + [part(f, c) for f, c in pieces]
    Fh = Frame(*Fb.w(5.4 * d, -3.6 + head_dv), s)
    out += head(Fh, mood, look, turn_=1.5 * d)
    return out, Fh


# ---- 소품 ----

def bell(cx, cy, r, roll=0.0, pivot=None, knob=True):
    """금방울: 금빛 공 + 허리띠 + 아래 틈(구멍 · 홈) + 꼭지 고리. roll 은 pivot(기본 가운데) 둘레로 돌리기"""
    px, py = pivot or (cx, cy)

    def T(g):
        return turn(g, roll, px, py) if roll else g
    body = T(circle(cx, cy, r))
    loop_ = T(ring(cx, cy - r - 0.25, 0.62, 0.26))
    out = [base(body, loop_) if knob else base(body)]
    if knob:
        out.append(part(loop_, BELL_D, sh=0.0, line=0.3, ink=BELL_S))

    def col(x, y):
        return lerp(BELL_L, BELL, smooth(cy - r * 0.9, cy - r * 0.05, y))
    out.append(part(body, col, shade=BELL_D, ink=BELL_S, line=0.75))
    out.append(flat(T(capsule(cx - r * 0.86, cy - r * 0.05, cx + r * 0.86, cy - r * 0.05, max(0.17, r * 0.07))), BELL_D, 0.9))
    out.append(flat(T(circle(cx, cy + r * 0.42, max(0.42, r * 0.19))), BELL_S))
    out.append(flat(T(capsule(cx, cy + r * 0.42, cx, cy + r * 0.86, max(0.15, r * 0.07))), BELL_S))
    out.append(flat(T(circle(cx - r * 0.36, cy - r * 0.44, max(0.35, r * 0.2))), BELL_L, 0.95))
    return out


def jingle(cx, cy, r):
    """딸랑 — 방울 양옆 위로 짧은 금빛 획 둘씩"""
    out = []
    for sg in (-1, 1):
        for ang in (-0.95, -0.3):
            ux, uy = sg * cos(ang), sin(ang)
            out.append(flat(capsule(cx + ux * (r + 0.9), cy + uy * (r + 0.9), cx + ux * (r + 2.1), cy + uy * (r + 2.1), 0.3), BELL_D))
    return out


def gchev(cx, cy, dx, dy, L=2.2, a=1.0):
    """(dx, dy) 쪽을 가리키는 금빛 화살촉(원본 GOLD) — 꼭짓점이 (cx, cy). catkit.chevron 의 금빛 판"""
    n = hypot(dx, dy)
    dx, dy = dx / n, dy / n
    px, py = -dy, dx
    f = union(*[capsule(cx, cy, cx - dx * L + s_ * px * L, cy - dy * L + s_ * py * L, 0.72) for s_ in (-1, 1)])
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(GOLD, GOLD_D, smooth(0.36, 0.2, -e)), 1.0), alpha=a)]


def ribbon(f, sh=1.0):
    return [base(f), part(f, RIB, shade=RIB_D, ink=RIB_D, line=0.6, sh=sh)]


def sweat(x, y):
    f = smin(0.35, circle(x, y + 0.5, 0.95), poly([(x, y - 1.2), (x - 0.8, y + 0.4), (x + 0.8, y + 0.4)]))
    return [base(f), part(f, SWEAT, shade=hx("6fb0e0"), ink=hx("3d7fb8"), line=0.4, sh=0.6)]


# ---- 칸마다 장면 (art 좌표, 화살표 칸은 catkit 빼꼼) ----

def sc_busy(fr):
    """작은 화살표 먼치킨 + 원을 데굴데굴 도는 금방울, 지나간 자리에 반짝이"""
    out = buddy(fr)
    k = kk(fr)
    cx, cy, R, r = 22.6, 22.6, 5.5, 2.3
    for j in (3, 2, 1):
        a = TAU * (k - j) / NF - pi / 2
        sp = sparkle(cx + R * cos(a), cy + R * sin(a), 1.9 - 0.35 * j, 0.6)
        for L in sp:
            L["alpha"] = 1.0 - 0.27 * j
        out += sp
    a = TAU * k / NF - pi / 2
    out += bell(cx + R * cos(a), cy + R * sin(a), r, roll=(a + pi / 2) * R / r)
    return out


def sc_help(fr):
    """작은 화살표 먼치킨 + 분홍 리본 물음표, 점은 달랑대는 금방울"""
    ph, k = TAU * fr, kk(fr)
    out = buddy(fr)
    q = union(arc(22.6, 14.4, 3.6, 1.15, pi * 0.95, pi * 1.42), capsule(25.3, 16.4, 22.6, 19.0, 1.15),
              capsule(22.6, 19.0, 22.6, 20.6, 1.15))
    out += ribbon(q)
    sw = 0.32 * sin(2 * ph)
    out += bell(22.6, 26.0, 2.1, roll=sw, pivot=(22.6, 23.4))
    if k % 2 == 0:
        bx, by = 22.6 - 2.6 * sin(sw), 23.4 + 2.6 * cos(sw)
        out += jingle(bx, by, 2.1)
    return out


def sc_person(fr):
    """작은 화살표 먼치킨 + 방울 낚싯대를 흔드는 사람(초록 셔츠)"""
    ph = TAU * fr
    out = buddy(fr)
    cx, cy = 23.8, 22.4
    sw = sin(ph)
    hand = (18.8, 26.4)
    tip = (13.8 + 1.8 * sw, 17.2 - 0.5 * abs(sw))
    bx, by = tip[0] - 1.5 * sin(ph - 1.0), tip[1] + 5.0
    line = capsule(tip[0], tip[1], bx, by - 2.2, 0.13)
    out.append(layer(line, lambda *a: (OUT, 0.85)))
    out += bell(bx, by, 1.7, roll=-0.35 * sin(ph - 1.0), pivot=(bx, by - 2.2))
    body = clip_y(ell(cx + 0.4, cy + 8.4, 6.0, 5.0), 30.4)
    hd_ = circle(cx, cy, 4.0)
    hair = smin(0.6, ell(cx, cy - 2.2, 4.4, 2.4), ell(cx - 3.6, cy - 0.6, 1.1, 1.8), ell(cx + 3.6, cy - 0.6, 1.1, 1.8))
    arm = capsule(cx - 2.6, cy + 5.6, hand[0] + 0.6, hand[1] - 0.2, 1.1)
    out += [base(body, hd_, hair, arm), part(body, SHIRT, shade=SHIRT_D), part(arm, SHIRT, shade=SHIRT_D),
            part(hd_, SKIN, shade=hx("e8bfa0")), part(hair, HAIR, shade=hx("4a3222"))]
    for sg in (-1, 1):
        out.append(flat(ell(cx + sg * 1.6, cy + 0.5, 0.55, 0.75), EYE))
        out.append(soft(ell(cx + sg * 2.6, cy + 1.9, 0.85, 0.5), CHEEK, 0.8))
    out.append(flat(arc(cx, cy + 1.6, 0.9, 0.22, pi * 0.15, pi * 0.7), SHIRT_D))
    rod = capsule(hand[0], hand[1], tip[0], tip[1], 0.45)
    hf = circle(hand[0], hand[1], 1.2)
    out += [base(rod), part(rod, ROD, shade=ROD_D, ink=ROD_D, line=0.4, sh=0.5), base(hf), part(hf, SKIN, shade=hx("e8bfa0"))]
    return out


def sc_pin(fr):
    """작은 화살표 먼치킨 + 흰 동그라미 속 금방울이 든 빨간 핀이 통통"""
    out = buddy(fr)
    hop = abs(sin(pi * fr))
    cx, cy = 22.6, 15.2 - 2.6 * hop
    out.insert(0, layer(ell(22.8, 29.0, 3.4 - 0.8 * hop, 0.75), lambda *a: (OUT, 0.2)))
    f = smin(1.0, circle(cx, cy, 5.6), poly([(cx - 4.6, cy + 2.6), (cx + 4.6, cy + 2.6), (cx, cy + 11.4)]))
    out += [base(f), part(f, lambda x, y: lerp(SIGN_L, SIGN, smooth(cy - 5, cy - 1.5, y + 0.6 * (x - cx))), shade=SIGN_D, ink=SIGN_D)]
    out.append(flat(circle(cx, cy, 3.7), BELLY, line=0.5, ink=SIGN_D))
    out += bell(cx, cy + 0.25, 2.0, roll=0.35 * sin(TAU * 2 * fr), pivot=(cx, cy - 2.0))
    return out


def sc_cross(fr):
    """조준선 가운데 리본에 매달린 금방울(핫스팟) — 밑에서 머리만 보이는 먼치킨이 짧은 앞발을 휘젓지만 안 닿는다"""
    ph, k = TAU * fr, kk(fr)
    C0 = 15.5
    lines = union(capsule(2.6, C0, 7.4, C0, 0.5), capsule(23.6, C0, 28.4, C0, 0.5))
    out = [base(lines), flat(lines, OUT)]
    out += ribbon(capsule(C0, 2.4, C0, C0 - 3.6, 0.6), sh=0.0)
    out += bell(C0, C0, 3.2, roll=0.08 * sin(2 * ph), pivot=(C0, C0 - 3.6))
    hi = k % 4 < 2
    F = Frame(C0, 26.6, 0.62)
    arms = [((-7.4, 3.6), (-9.2, -4.4 - (1.8 if hi else 0.0)), False),
            ((7.4, 3.6), (9.2, -4.4 - (0.0 if hi else 1.8)), False)]
    mood = "squeeze" if k % 6 in (2, 3) else "open"
    out += head(F, mood, look=(0.0, -1.0), turn_=0.0, arms=arms, ear_tilt=(-0.6, -0.6))
    return out


def sc_hand(fr):
    """까치발로 서서 짧은 앞발 하나를 왼쪽 위로 쭉 — 젤리 발끝이 핫스팟, 짧은 뒷다리가 바들바들"""
    k = kk(fr)
    tap = k % 6 in (3, 4, 5)
    jit = 0.3 if k % 2 else -0.3
    s = 0.6
    F = Frame(13.6 + jit * 0.5, 13.0, s)
    p = 6.2 - (0.35 if tap else 0.0)
    hand = F.loc(p, p)
    out = stand(F, "squeeze" if k % 6 == 4 else "open", look=(-0.7, -0.7), turn_=-0.7, tip=1.0,
                back_arms=[((-4.6, 1.6), hand, True)], arms=[((3.3, 6.6), (1.9, 8.7), False)],
                ear_tilt=(-1.1, 0.0), spread=0.25 if tap else 0.0, tail_sw=0.4 * jit)
    _, _, _, R, fv, fb = stand_geo(1.0, s, 1.0)
    if k % 2:                                             # 발 옆 바들 선
        for sg in (-1, 1):
            x, y = F.w(sg * (R * 1.78 + 1.6), fv)
            out.append(flat(capsule(x, y - 0.9, x + sg * 0.5, y + 0.9, 0.25), OUT, 0.7))
    if tap:
        L = 1.7 if k % 6 == 4 else 1.2
        out += sparkle(10.6, 3.2, L, 0.5) + sparkle(3.0, 10.4, L, 0.5)
    return out


LOOK_I = (0, 0, -1, -1, -1, 0, 0, 1, 1, 1, 0, 0)


def sc_ibeam(fr):
    """미어캣 서기 = I: 큰 머리가 윗획, 가는 몸이 세로획, 발밑 그림자가 아랫획. 두리번, 배 가운데가 핫스팟"""
    k = kk(fr)
    L = LOOK_I[k]
    s, up = 0.54, 1.0
    cv, ry, rx, R, fv, fb = stand_geo(up, s)
    X = 6.5
    F = Frame(X, 11.5 - cv * s, s)
    gy = F.w(0, fb)[1]
    bar = rbox(X, gy + 0.3, 4.2, 0.55, 0.55)
    out = [layer(bar, lambda *a: (OUT, 0.32))]
    out += stand(F, "blink" if k == 6 else "open", look=(L * 0.9, 0.0), turn_=1.6 * L, up=up, tail_sw=0.4 * L)
    return out


def sc_move(fr):
    """옆모습으로 짧은 다리를 뱅뱅 돌리며 제자리 달리기, 뒤로 흙먼지. 네 방향 금빛 화살촉"""
    ph, k = TAU * fr, kk(fr)
    o = 0.6 if k % 6 < 3 else 0.0
    out = []
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        out += gchev(15.5 + dx * (13.6 + o), 15.5 + dy * (13.6 + o), dx, dy, 2.2)
    bob = 0.4 * abs(sin(2 * ph))
    Fb = Frame(14.6, 17.4 - bob, 0.6)
    for j in range(3):                                    # 흙먼지: 뒷발 뒤에서 피어 뒤로 흩어짐
        t = ((k % 4) / 4 + j / 3) % 1.0
        x, y = Fb.w(-6.4 - 6.0 * t, 6.4 - 1.6 * t)
        f = circle(x, y, 0.9 + 1.0 * t)
        out.append(layer(f, lambda px, py, e, nx, ny, fr_: (lerp(DUST, DUST_D, smooth(0.3, 0.1, -e)), 1.0), alpha=0.85 - 0.6 * t))
    body, _ = side(Fb, 1, gait=2 * ph, mood="blink" if k == 7 else "open", look=(0.9, 0.0), tail_sw=0.6 * sin(2 * ph))
    return out + body


def sc_we(fr):
    """옆모습으로 금방울을 앞발로 툭툭 몰고 가다 반 바퀴마다 돌아선다. 양 끝 금빛 화살촉"""
    ph, k = TAU * fr, kk(fr)
    d = 1 if k < 6 else -1
    t = (k % 6) / 6
    o = 0.6 if k % 6 < 3 else 0.0
    out = gchev(1.9 - o, 8.5, -1, 0) + gchev(29.1 + o, 8.5, 1, 0)
    x = 15.5 - d * 1.2 + d * 2.4 * t
    Fb = Frame(x, 10.4, 0.6)
    kick = 0.9 * max(0.0, sin(TAU * t * 2))
    bx = x + d * (5.8 + kick)
    by = 14.6 - 1.7
    body, _ = side(Fb, d, gait=4 * pi * t, walk=0.7, look=(0.6 * d, 0.6), tail_sw=0.5 * sin(2 * ph))
    out += body
    out += bell(bx, by, 1.7, roll=d * (bx - 15.5) / 1.7)
    return out


UP_NS = (0.0, 0.3, 0.7, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.7, 0.3, 0.0)
LOOK_NS = (0, 0, 0, -1, -1, 0, 1, 1, 0, 0, 0, 0)


def sc_ns(fr):
    """앉았다 뒷발로 일어나 미어캣처럼 두리번(위아래로 늘었다 줄었다). 위아래 금빛 화살촉"""
    k = kk(fr)
    up = UP_NS[k]
    L = LOOK_NS[k]
    o = 0.6 if up > 0.9 else 0.0
    out = gchev(9.5, 1.9 - o, 0, -1) + gchev(9.5, 29.1 + o, 0, 1)
    s = 0.62
    cv, ry, rx, R, fv, fb = stand_geo(up, s)
    F = Frame(9.5, 24.2 - fb * s, s)
    tuck = 1.2 * (1 - up)
    arms = [(None, (-2.3, 8.2 + tuck), False), (None, (2.3, 8.2 + tuck), False)]
    out += stand(F, "blink" if k == 0 else "open", look=(0.9 * L, -0.3 * up), turn_=1.6 * L, up=up, arms=arms,
                 tail_sw=0.5 * L)
    return out


SLIP = (-1.2, -0.9, -0.6, -0.3, 0.0, 0.3, 0.6, 0.9, 0.1, -1.0, -1.6, -1.4)


def slope(fr, d):
    """대각 비탈을 짧은 다리로 오르다 미끄러짐 — d=1 은 오른쪽 위로(nesw), -1 은 왼쪽 위로(nwse)"""
    ph, k = TAU * fr, kk(fr)
    s = 0.6
    ux, uy = d * 0.7071, -0.7071                           # 오르는 쪽
    nx, ny = -d * 0.7071 * -1 * -1, 0.7071                 # 발 쪽(비탈 안)
    nx = 0.7071 if d > 0 else -0.7071
    foot = 7.6 * s
    c0 = (15.5 + nx * foot, 15.5 + ny * foot)              # 배가 핫스팟일 때 발이 닿는 비탈 위 한 점
    if d > 0:
        k0 = c0[0] + c0[1]
        hill = poly([(k0 - 29.8, 29.8), (29.8, k0 - 29.8), (29.8, 29.8)])

        def dist(x, y):
            return (x + y - k0) / 1.4142
    else:
        k0 = c0[1] - c0[0]
        hill = poly([(2.2, 2.2 + k0), (2.2, 29.8), (29.8 - k0, 29.8)])

        def dist(x, y):
            return (y - x - k0) / 1.4142

    def hp(x, y, e, nx_, ny_, fr_):
        t = dist(x, y)
        return (SLOPE_D if t < 0.9 else SLOPE), mix(1.0, 0.35, smooth(2.0, 10.0, t))
    out = [layer(hill, hp)]
    o = 0.6 if k % 6 < 3 else 0.0
    if d > 0:
        out += gchev(27.6 + o, 3.4 - o, 1, -1) + gchev(3.4 - o, 27.6 + o, -1, 1)
    else:
        out += gchev(3.4 - o, 3.4 - o, -1, -1) + gchev(27.6 + o, 27.6 + o, 1, 1)
    p = SLIP[k]
    slip = k in (8, 9, 10)
    Fb = Frame(15.5 + ux * p, 15.5 + uy * p, s, -d * pi / 4)
    body, Fh = side(Fb, d, gait=0.0 if slip else 4 * ph, walk=0.0 if slip else 0.8, splay=1.2 if slip else 0.0,
                    mood="squeeze" if slip else ("blink" if k == 3 else "open"), look=(0.6 * d, -0.6),
                    tail_sw=0.5 * sin(2 * ph))
    out += body
    if slip:
        out += sweat(*Fh.w(-d * 8.6, -5.2))
    return out


def sc_nesw(fr):
    return slope(fr, 1)


def sc_nwse(fr):
    return slope(fr, -1)


TURN_NO = (-2.0, -2.0, -0.8, 0.8, 2.0, 2.0, 2.0, 2.0, 0.8, -0.8, -2.0, -2.0)


def sc_no(fr):
    """빨간 금지 표지 안에서 금방울을 두 앞발로 꼭 껴안고 도리도리(안 줘)"""
    k = kk(fr)
    C0 = 14.5
    t = TURN_NO[k]
    s = 0.56
    up = 0.8
    F = Frame(C0, 11.2, s)
    bx, by = F.w(0, 9.0)
    held = bell(bx, by, 2.3)
    arms = [((-4.0, 6.6), (-2.6, 9.6), False), ((4.0, 6.6), (2.6, 9.6), False)]
    shake = k in (2, 3, 8, 9)
    out = stand(F, "squeeze" if shake else "open", look=(-0.5 * t, 0.0), turn_=t, up=up, arms=arms, held=held,
                tail_sw=0.3 * t)
    if shake:                                             # 도리도리 선
        for sg in (-1, 1):
            x, y = F.w(sg * 9.4, -2.0)
            out.append(flat(arc(x - sg * 1.6, y, 1.9, 0.26, pi * (0.82 if sg > 0 else -0.18) - 0.6, 1.2), OUT, 0.8))
    R = 12.5
    sg_ = union(ring(C0, C0, R - 1.25, 1.25), capsule(C0 - 7.7, C0 - 7.7, C0 + 7.7, C0 + 7.7, 1.35))
    out += [base(sg_), part(sg_, lambda x, y: lerp(SIGN_L, SIGN, smooth(C0 - 10, C0 - 4, y + 0.5 * x - 0.5 * C0)),
                            shade=SIGN_D, ink=SIGN_D, line=0.8)]
    return out


def sc_pen(fr):
    """두 앞발로 쥔 파란 크레용으로 삐뚤빼뚤 — 크레용 끝(왼쪽 아래)이 핫스팟, 파란 줄이 길어진다"""
    ph, k = TAU * fr, kk(fr)
    tip = (1.55, 25.5)
    ang = -0.72 + 0.05 * sin(2 * ph)
    ux, uy = cos(ang), sin(ang)
    nx, ny = -uy, ux
    L, r = 17.0, 1.55
    out = []
    pts = [(2.4, 26.4)] + [(3.4 + 1.3 * i, 27.6 + (0.85 if i % 2 else -0.6)) for i in range(1 + k)]
    for a, b in zip(pts, pts[1:]):                        # 삐뚤빼뚤 파란 줄
        out.append(flat(capsule(*a, *b, 0.5), CRAY))
    s = 0.6
    F = Frame(18.8, 9.0, s)
    h1 = F.loc(tip[0] + ux * 13.0, tip[1] + uy * 13.0)
    h2 = F.loc(tip[0] + ux * 15.3, tip[1] + uy * 15.3)
    end = (tip[0] + ux * L, tip[1] + uy * L)
    cone = poly([tip, (tip[0] + ux * 3.2 - nx * r, tip[1] + uy * 3.2 - ny * r), (tip[0] + ux * 3.2 + nx * r, tip[1] + uy * 3.2 + ny * r)])
    ch = smin(0.4, cone, capsule(tip[0] + ux * 3.0, tip[1] + uy * 3.0, end[0], end[1], r))

    def ccol(x, y):
        t = (x - tip[0]) * ux + (y - tip[1]) * uy
        n = (x - tip[0]) * nx + (y - tip[1]) * ny
        if 5.0 < t < 13.6:                                 # 종이 띠(끝에 짙은 줄)
            return CRAY_D if (t < 5.6 or t > 13.0) else PAPER
        return lerp(CRAY_L, CRAY, smooth(-0.9, 0.3, n)) if t > 2.0 else CRAY
    held = [base(ch), part(ch, ccol, shade=CRAY_D, ink=hx("1f4a80"), line=0.8)]
    arms = [((-3.4, 6.6), h1, False), ((2.6, 7.0), h2, False)]
    out += stand(F, "blink" if k == 5 else "open", look=(-0.8, 0.7), turn_=-1.0, arms=arms, held=held,
                 tail_sw=0.5 * sin(ph))
    return out


def sc_up(fr):
    """금방울을 머리에 이고 미어캣 서기 — 방울 꼭지(맨 위)가 핫스팟이라 방울 · 머리는 그대로, 몸만 휘청,
    짧은 앞발을 양옆으로 벌려 균형"""
    ph, k = TAU * fr, kk(fr)
    sw = sin(ph)
    s = 0.62
    X = 8.5
    r = 3.0
    by = 1.5 + 0.25 + 0.0 + r                               # 꼭지 고리 가운데가 (8.5, 1.5)
    F = Frame(X, by + r + 6.0 * s - 0.15, s)
    du = 0.9 * sw
    arms = [((du - 3.6, 6.4), (du - 8.2, 4.6 + 0.9 * sw), False), ((du + 3.6, 6.4), (du + 8.2, 4.6 - 0.9 * sw), False)]
    out = stand(F, "blink" if k == 7 else "open", look=(0.2 * sw, -0.9), turn_=0.0, arms=arms, du=du,
                tail_sw=-0.8 * sw, ear_tilt=(0.4 * max(0.0, sw), 0.4 * max(0.0, -sw)))
    out += bell(X, by, r)
    if k % 2:
        out += jingle(X, by, r)
    return out


def sc_wait(fr):
    """사람처럼 기대앉아 짧은 뒷다리를 앞으로 쭉(분홍 젤리 발바닥) — 배 위 금방울을 앞발로 톡톡(배 가운데가 핫스팟)"""
    ph, k = TAU * fr, kk(fr)
    s = 0.66
    cv = 8.4
    F = Frame(11.5, 13.5 - cv * s, s)
    R = max(2.0, 1.75 / s)
    torso = (F.f(ell(0, cv, 5.6, 4.8)), body_col(F, 0.0, cv, 5.6, 4.8))
    legs, soles = [], []
    for sg in (-1, 1):
        fc = (sg * 6.6, 13.0)
        legs.append((F.f(capsule(sg * 2.8, 10.4, *fc, R)), FUR))
        legs.append((F.f(ell(fc[0] + sg * 0.3, fc[1] + 0.3, R * 1.08, R * 1.12)), BELLY))
        soles += sole(F, (fc[0] + sg * 0.3, fc[1] + 0.3), R * 1.05)
    tp = [(3.8, 11.6), (8.2, 12.6), (11.2, 11.0), (12.2 + 0.6 * sin(ph), 8.0), (11.6 + 0.9 * sin(ph), 6.0)]
    out = mcat(F, body=False, paws=False, tail=True, tail_pts=tp, extra_under=[torso] + legs, face_on=False)
    out += soles
    tap = k % 3 == 1
    left = (k // 3) % 2 == 0
    bob = 0.6 if tap else 0.0
    br = 2.7
    bx, by = F.w(0, 9.4)
    out += bell(bx, by - bob, br)
    if tap:
        out += jingle(bx, by - bob, br)
    lift = 1.8
    arms = [(None, (-3.6, 6.4 - (lift if tap and left else 0.0)), False),
            (None, (3.6, 6.4 - (lift if tap and not left else 0.0)), False)]
    out += fronts(F, arms)
    out += mface(F, "happy" if k % 6 in (1, 2) else "open", look=(0.0, 0.5), turn_=0.0)
    return out


SCENE = {"busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "wait": sc_wait,
         "hand": sc_hand, "cross": sc_cross, "ibeam": sc_ibeam, "move": sc_move, "no": sc_no, "pen": sc_pen,
         "up": sc_up, "we": sc_we, "ns": sc_ns, "nwse": sc_nwse, "nesw": sc_nesw}


class MunchkinCat(Pet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = MunchkinCat(COAT, SCENE, HOT)


def scene(name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
    return PET.cell(name, frame, soft_, tip_body, shape)


register("munchkincat", PET)

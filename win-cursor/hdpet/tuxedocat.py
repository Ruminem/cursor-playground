# SPDX-License-Identifier: Apache-2.0
"""턱시도냥(tuxedocatanim) 고화질 — 치비(머리가 몸만 한 통통 냥) · 스티커 채색(고른 먹선 1칸 + 셀 그늘 한 단).

픽셀 턱시도냥(gen/tuxedocat.py)의 신사를 HD 로 옮겼다 — 짙은 회흑 털(순검정이면 어두운 바탕에서 테만 남는다) ·
흰 주둥이와 콧등 줄 · 흰 셔츠 가슴 · 흰 양말 · 초록 눈 · 빨간 나비넥타이(실루엣의 표식). 새침해서 코를 치켜들고
눈을 반쯤 내리깐다. 소품도 신사의 것(회중시계 · 깃펜 · 지팡이 · 찻잔)이다. 칸마다 하는 짓은 픽셀 판 그대로:

  arrow   크림 화살표 빗변 뒤에서 빼꼼 — 흰 양말 앞발 둘이 빗변을 잡는다(catkit peek)
  busy    작은 화살표 턱시도냥 + 김이 오르는 찻잔 둘레를 도는 분홍 발자국 여덟
  help    작은 화살표 턱시도냥 + 젤리 콩으로 찍은 물음표(차례로 꾹), 점은 발자국
  person  작은 화살표 턱시도냥 + 나비넥타이를 맨 신사 냥 흉상(턱시도 깃 · 흰 셔츠)
  pin     작은 화살표 턱시도냥 + 흰 동그라미 속 나비넥타이가 든 빨간 핀이 통통
  wait    회중시계를 앞발로 들고 새침하게 들여다본다 — 바늘이 돌고 꼬리 끝이 똑딱. 시계 가운데가 핫스팟
  cross   가는 조준선 가운데 빨간 레이저 점(핫스팟) — 오른쪽 아래에서 동공이 커진 냥이 엉덩이를 씰룩이며 노린다
  hand    앞발 하나를 왼쪽 위로 쭉 들어 콕 — 분홍 젤리가 보이는 발끝이 핫스팟
  ibeam   위 판 · 밧줄 기둥 · 아래 받침이 I 인 스크래처를 앞발로 번갈아 박박 — 밧줄에 긁힌 자국. 기둥 가운데가 핫스팟
  pen     깃펜을 쥐고 글씨를 쓴다 — 펜촉(왼쪽 아래)이 핫스팟, 잉크 줄이 길어진다
  no      빨간 금지 표지 안에서 코를 치켜들고 눈을 감은 채 앞발을 내밀어 '사양하겠소'
  up      신사 지팡이를 머리 위로 곧게 치켜든다 — 지팡이 금 손잡이(맨 위)가 핫스팟
  move    앞모습으로 앉아 앞발을 번갈아 들며 사뿐사뿐 제자리 걸음 — 네 방향 빨간 화살촉
  ns      제자리 수직 점프 — 웅크렸다 떠올라 뒷발을 늘어뜨리고 내려앉는다. 위아래 화살촉
  we      꼬리를 곧게 세우고 새침하게 옆으로 걷는다 — 왼쪽으로 가다가 돌아서 오른쪽으로
  nwse · nesw  그 대각선을 따라 다다닥 달린다 — 한쪽 끝으로 갔다가 돌아서 반대쪽으로, 가는 쪽 화살촉이 깜빡

좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 장면은 NF 장으로 나뉘어 있다(k = round(fr × NF) % NF).
틀(먹선 · 치비 몸 · 빼꼼 · 모양 화살표)은 catkit 에 있고 여기는 털빛 · 소품 · 장면만 둔다. catkit 이 털빛 하나로
못 하는 셋(감은 눈 선 색 · 흰 조각의 그늘 색 · 목의 나비넥타이)은 이 결이 칸을 그리는 동안만 catkit 의
face · shut · part 를 갈아 끼워 메운다(_dress) — 다른 냥이는 그대로다.
"""
import contextlib

from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

from . import catkit, register
from .catkit import *  # noqa: F401,F403

# 픽셀 판 팔레트(gen/tuxedocat.py) 그대로 + 하이라이트 한 단
OUT = hx("0c0c10")                                        # 먹
FUR, FUR_L, FUR_D = hx("2a2a33"), hx("3e3e4c"), hx("1c1c23")   # 털 · 앞에 놓인 다리 · 뒤에 놓인 다리(그늘)
FUR_HI = hx("575768")                                     # 털 윤기(왼쪽 위) — 검은 머리가 32 에서 덩어리로 안 뭉치게
WHITE, WHITE_D = hx("f7f7f2"), hx("cfd1db")               # 셔츠 · 양말 · 주둥이 / 그늘
GREEN, GREEN_D, GREEN_L, PUPIL = hx("9ee05a"), hx("4f9a2c"), hx("d4f7a0"), hx("121218")
LID = hx("a2a2b4")                                        # 감은 눈 선(검은 털 위에 짙은 선은 안 보인다)
NOSE, EAR_IN, BLUSH = hx("f29aae"), hx("e8899c"), hx("ee7f98")
BEAN, BEAN_D = hx("f6a8b8"), hx("d9758e")                 # 발바닥 젤리
BOW, BOW_D, BOW_L = hx("dc3340"), hx("98202c"), hx("f2606a")   # 나비넥타이
RIM = hx("e6e8f0")                                        # 바깥 테(연회색)
GOLD, GOLD_D, GOLD_L, DIAL = hx("e8bf4a"), hx("a8822a"), hx("fbe48e"), hx("fbf3dc")   # 회중시계 · 지팡이 손잡이
CUP, CUP_D, TEA, TEA_L = hx("f2f4fb"), hx("a9b4cf"), hx("b0703c"), hx("d39a62")       # 찻잔
STEAM = hx("d8dbe6")
QUILL, QUILL_D, NIB, INK = hx("f4f1e6"), hx("bdb8a8"), hx("3a3a46"), hx("2a2a3a")    # 깃펜
ROPE, ROPE_D, PLANK, PLANK_D = hx("dcc08c"), hx("b0915a"), hx("8a5a3a"), hx("643e26")  # 스크래처
SCRATCH = hx("fff4dc")
CANE = hx("2e2a30")
LASER, LASER_L = hx("ff2a2a"), hx("ffb0a8")
SIGN, SIGN_D, SIGN_L = hx("d64541"), hx("9e2b28"), hx("ef7a72")


def _in_ell(u, v, cu, cv, ru, rv):
    return ((u - cu) / ru) ** 2 + ((v - cv) / rv) ** 2 <= 1.0


class TuxCoat(Coat):
    """턱시도 털빛 — 머리는 흰 주둥이 · 콧등 줄, 몸은 흰 셔츠 가슴, 발은 흰 양말. 무늬는 F(그 냥이 Frame)의
    캐논 좌표에 붙는다. 검은 털은 왼쪽 위에 윤기를 얹어 머리 · 몸 덩어리가 32 에서도 둥글게 읽히게 한다"""

    def fur(self, part, F=None, turn_=0.0):
        if part in ("paw", "hand", "front", "back") or F is None:
            return WHITE
        if part == "arm":
            return FUR_L
        if part in ("ear", "tail"):
            return FUR

        def sheen(u, v, cu, cv, ru, rv):
            d = ((u - cu) / ru) ** 2 + ((v - cv) / rv) ** 2
            return lerp(FUR, FUR_HI, 0.75 * smooth(1.0, 0.2, d))
        if part == "head":
            def col(x, y):
                u, v = F.loc(x, y)
                w = u - turn_
                if _in_ell(w, v, 0.0, 3.05, 3.15, 2.05) or (abs(w) < 0.55 + 0.12 * (v + 2.6) and -2.6 < v < 1.5):
                    return WHITE
                return sheen(u, v, turn_ - 3.4, -3.6, 3.0, 1.7)
            return col
        if part == "body":
            def col(x, y):
                u, v = F.loc(x, y)
                if _in_ell(u, v, 0.0, 7.6, 2.9, 4.2):
                    return WHITE
                return sheen(u, v, -3.2, 5.6, 1.6, 2.6)
            return col
        return FUR


COAT = TuxCoat(FUR, FUR_D, OUT, PUPIL, RIM, ((GREEN, GREEN_D, GREEN_L), (GREEN, GREEN_D, GREEN_L)),
               ear=EAR_IN, cheek=BLUSH, nose=NOSE, nose_l=hx("f8c2cf"), jelly=BEAN, tongue=BEAN)

# 픽셀 판 핫스팟(art/tuxedocatanim 의 hotspot 줄 — 그림 상자 왼쪽 위로 옮겨 적힌 값) 그대로
HOT = {"arrow": (1, 1), "busy": (1, 1), "cross": (15, 15), "hand": (2, 4), "help": (1, 1), "ibeam": (6, 15),
       "move": (15, 15), "nesw": (15, 15), "no": (14, 14), "ns": (4, 15), "nwse": (15, 15), "pen": (1, 22),
       "person": (1, 1), "pin": (1, 1), "up": (2, 1), "wait": (6, 10), "we": (15, 9)}


# ---- catkit 갈아 끼우기: 감은 눈 선 · 흰 조각 그늘 · 목의 나비넥타이 ----

_FACE, _SHUT, _PART = catkit.face, catkit.shut, catkit.part


def _shut(cx, cy, rx, kind="blink"):
    """감은 눈 — catkit 과 같은 꼴, 선만 연회색(검은 털 위 먹색 선은 사라진다)"""
    w = max(0.32, 0.22 * rx)
    if kind == "happy":
        return flat(arc(cx, cy + rx * 0.55, rx * 0.95, w, pi * 1.2, pi * 0.6), LID)
    return flat(arc(cx, cy - rx * 0.5, rx * 0.95, w, pi * 0.18, pi * 0.64), LID)


def _part(f, col=None, shade=None, line=LINE, sh=1.0, ink=None):
    """catkit.part 와 같되 그늘을 안 주면 칸 색이 밝을 때(흰 양말 · 주둥이 · 셔츠) 흰 그늘, 어두울 때 털 그늘 —
    털빛 그늘 하나(검정)를 흰 조각에 쓰면 오른쪽 아래에 검은 띠가 생겨 양말이 줄어 보인다"""
    if shade is not None:
        return _PART(f, col, shade, line, sh, ink)
    col = catkit.C.base if col is None else col
    ink = catkit.C.out if ink is None else ink

    def paint(x, y, e, nx, ny, fr):
        c = col(x, y) if callable(col) else col
        if sh:
            c = lerp(c, WHITE_D if c[0] + c[1] + c[2] > 1.5 else FUR_D, sh * smooth(-0.15, 0.15, f(x + SH[0], y + SH[1])))
        if line:
            c = lerp(c, ink, smooth(line + 0.12, line - 0.12, -e))
        return c, 1.0
    return layer(f, paint)


def bow(F, turn_=0.0, v=5.35, w=3.1, h=1.75):
    """목의 빨간 나비넥타이 — 매듭 + 두 날개(캐논 좌표, 머리 바로 밑)"""
    u = turn_ * 0.55
    wings = union(*[poly([F.w(u, v), F.w(u + sg * w, v - h), F.w(u + sg * w, v + h)]) for sg in (-1, 1)])
    wings = grow(wings, 0.18 * F.s)
    knot = F.f(ell(u, v, 0.85, 0.95))
    cx, cy = F.w(u, v)
    out = [flat(wings, lambda x, y: lerp(BOW_L, BOW, smooth(cy - 1.2 * F.s, cy + 0.3 * F.s, y)), line=0.3, ink=BOW_D),
           flat(knot, BOW_D, line=0.22, ink=hx("6e1520"))]
    return out


def _face(F, mood="open", look=(0.0, 0.0), turn_=0.0, mouth="w", tongue=0.0):
    """catkit.face + 턱시도 눈(smug 반쯤 내리깐 눈 · wide 커진 동공) + 나비넥타이"""
    base_mood = {"smug": "open", "wide": "open", "closed": "blink"}.get(mood, mood)
    if mood == "smug":
        look = (look[0], 0.7)
    out = _FACE(F, base_mood, look, turn_, mouth, tongue)
    s = F.s
    er = max(1.66 * s, 1.32)
    ry = er * 1.16
    for sg in (-1, 1):
        ex, ey = F.w(turn_ + sg * 3.15, 0.25)
        if mood == "smug":                                 # 위 눈꺼풀이 반쯤 덮는다 — 털색 덮개 + 연회색 꺼풀 선
            lid_y = ey - 0.05 * ry
            cover = inter(ell(ex, ey, er + 0.12, ry + 0.12), lambda x, y, ly=lid_y: y - ly)
            out.append(flat(cover, FUR))
            out.append(flat(capsule(ex - er * 0.92, lid_y, ex + er * 0.92, lid_y, max(0.3, 0.2 * er)), LID))
        elif mood == "wide":                               # 사냥 눈 — 동공이 홍채를 거의 채운다
            px, py = ex + look[0] * er * 0.18, ey + ry * 0.1 + look[1] * ry * 0.1
            out.append(flat(ell(px, py, er * 0.66, ry * 0.74), PUPIL))
            out.append(flat(circle(px - er * 0.3, py - ry * 0.32, er * 0.3), HI))
            out.append(flat(circle(px + er * 0.28, py + ry * 0.34, er * 0.13), HI, 0.9))
    return out + bow(F, turn_)


@contextlib.contextmanager
def _dress():
    catkit.face, catkit.shut, catkit.part = _face, _shut, _part
    try:
        yield
    finally:
        catkit.face, catkit.shut, catkit.part = _FACE, _SHUT, _PART


# ---- 작은 도우미 ----

def kof(fr):
    return round(fr * NF) % NF


def rchev(cx, cy, dx, dy, L=2.4, a=1.0):
    """(dx, dy) 쪽을 가리키는 빨간 화살촉(나비넥타이 빨강) — 꼭짓점이 (cx, cy)"""
    n = hypot(dx, dy)
    dx, dy = dx / n, dy / n
    px, py = -dy, dx
    f = union(*[capsule(cx, cy, cx - dx * L + s * px * L, cy - dy * L + s * py * L, 0.72) for s in (-1, 1)])
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(BOW, BOW_D, smooth(0.36, 0.18, -e)), 1.0), alpha=a)]


def piece(f, col, shade, ink, line=LINE, sh=0.7):
    """소품 한 조각(스티커 바닥 + 칠)"""
    return [base(f), _part(f, col, shade=shade, ink=ink, line=line, sh=sh)]


def tcat(F, mood="open", **kw):
    """앉은 턱시도냥(catkit.cat) — 털빛 · 넥타이는 _dress 가 맡는다"""
    return cat(F, mood, **kw)


# ---- 옆모습 (걷기 · 달리기): 몸통은 옆, 머리는 catkit 앞모습을 돌려 얹는다 ----

class SF(Frame):
    """Frame + 좌우 뒤집기. 캐논은 왼쪽을 본다(앞 = -u). flip 이면 오른쪽을 본다"""

    def __init__(self, ox, oy, s, ang=0.0, flip=False):
        super().__init__(ox, oy, s, ang)
        self.flip = flip

    def loc(self, x, y):
        u, v = Frame.loc(self, x, y)
        return (-u if self.flip else u), v

    def w(self, u, v):
        return Frame.w(self, -u if self.flip else u, v)


def side_cat(S, ph, run=False, mood="smug", tail_up=True):
    """옆모습 턱시도냥(S: SF). ph 는 걸음 위상. run 이면 다리를 쭉 폈다 배 밑에 모았다(내달리기), 아니면 사뿐 걷기"""
    s = S.s
    out_legs = []
    if run:
        e = cos(ph)
        bob = -0.7 * e
        t = (1 + e) / 2

        def mix(p, q):
            return (q[0] + (p[0] - q[0]) * t, q[1] + (p[1] - q[1]) * t)
        legs = [((-4.4, 1.0 + bob), mix((-11.0, 3.4), (-1.8, 6.0)), FUR_L, True),
                ((5.0, 1.0 + bob), mix((11.4, 3.8), (0.8, 6.0)), FUR_L, True),
                ((-3.2, 1.2 + bob), mix((-9.8, 4.6), (-0.6, 6.2)), FUR_D, False),
                ((6.2, 1.0 + bob), mix((10.2, 5.0), (2.2, 6.2)), FUR_D, False)]
        tp = [(6.4, -0.6 + bob), (9.4, -2.2 + bob), (12.4, -3.4 + 0.9 * sin(ph))]
    else:
        bob = 0.35 * abs(sin(ph))
        legs = []
        for hip, p_, col, near in (((-4.2, 1.4), ph, FUR_L, True), ((4.6, 1.4), ph + pi, FUR_L, True),
                                   ((-2.8, 1.4), ph + pi, FUR_D, False), ((6.0, 1.4), ph, FUR_D, False)):
            sw = sin(p_)
            up = max(0.0, cos(p_)) * 1.3
            legs.append(((hip[0], hip[1] + bob), (hip[0] - 1.5 * sw, 6.6 - up), col, near))
        tw = 0.5 * sin(2 * ph)
        tp = [(5.8, -0.8 + bob), (7.4, -4.2), (7.6 + tw, -9.0), (7.0 + 1.6 * tw, -12.4)] if tail_up else \
            [(5.8, -0.8 + bob), (8.6, -2.0), (11.0, -3.6)]

    def leg_f(hip, foot):
        return S.f(smin(0.5, taper(hip[0], hip[1], 1.3, foot[0], foot[1], 1.08), ell(foot[0] - 0.35, foot[1] + 0.15, 1.35, 1.0)))

    def leg_col(hip, foot, col):
        ex, ey = foot[0] - hip[0], foot[1] - hip[1]
        ee = ex * ex + ey * ey or 1e-9

        def c(x, y):
            u, v = S.loc(x, y)
            return WHITE if ((u - hip[0]) * ex + (v - hip[1]) * ey) / ee > 0.55 else col
        return c
    torso = S.f(smin(1.2, ell(0.6, 0.2 + bob, 6.4, 3.3), ell(-4.2, -0.8 + bob, 2.9, 3.1)))

    def tcol(x, y):
        u, v = S.loc(x, y)
        if _in_ell(u, v, -5.6, 0.9 + bob, 1.9, 2.5):
            return WHITE
        return lerp(FUR, FUR_HI, 0.7 * smooth(1.0, 0.2, ((u - 0.5) / 4.5) ** 2 + ((v + 2.2 - bob) / 1.2) ** 2))
    tail = S.f(chain(tp, 1.25, 0.95))
    far = [(leg_f(h, f_), leg_col(h, f_, c)) for h, f_, c, n in legs if not n]
    near = [(leg_f(h, f_), leg_col(h, f_, c)) for h, f_, c, n in legs if n]
    out = [base(tail, torso, *[g for g, _ in far + near])]
    out.append(_part(tail, FUR))
    for g, c in far:
        out.append(_part(g, c))
    out.append(_part(torso, tcol))
    for g, c in near:
        out.append(_part(g, c))
    # 머리: 몸 앞 위에 앞모습 머리를 몸 기울기대로 얹는다 — 보는 쪽으로 얼굴을 돌린다
    hx_, hy_ = S.w(-6.4, -4.4 + bob)
    face_turn = 1.3 if S.flip else -1.3
    ang = math.atan2(S.sn, S.c)
    H = Frame(hx_, hy_, s * 0.84, ang)
    out += cat(H, mood, turn_=face_turn, look=(0.9 if S.flip else -0.9, 0.0), body=False, paws=False, tail=False)
    return out


# ---- 소품 ----

def teacup(cx, cy, k):
    """김이 오르는 찻잔 — 접시 · 잔 · 손잡이 · 홍차"""
    saucer = ell(cx, cy + 4.3, 6.0, 1.45)
    bowl = inter(ell(cx, cy - 2.0, 4.4, 5.6), lambda x, y: (cy - 2.0) - y)
    rim = ell(cx, cy - 2.0, 4.4, 1.25)
    handle = ring(cx + 4.7, cy + 0.2, 1.55, 0.55)
    cup = union(bowl, rim, handle)

    def ccol(x, y):
        return lerp(CUP, CUP_D, 0.55 * smooth(cx + 0.5, cx + 4.2, x))
    out = piece(saucer, lambda x, y: lerp(CUP, CUP_D, smooth(cy + 3.6, cy + 5.4, y)), CUP_D, hx("4a5068"))
    out += [base(cup), _part(cup, ccol, shade=CUP_D, ink=hx("4a5068"), sh=0.6)]
    out.append(flat(ell(cx, cy - 1.95, 3.45, 0.72), lambda x, y: lerp(TEA_L, TEA, smooth(cy - 2.4, cy - 1.4, y))))
    out.append(flat(capsule(cx - 2.6, cy + 0.8, cx + 2.6, cy + 0.8, 0.42), BOW, 0.95))   # 잔 띠(넥타이 빨강)
    for j in range(2):                                     # 김 두 줄기 — 오르며 옅어진다
        t = (k / NF + j / 2) % 1
        x0 = cx - 1.2 + 2.4 * j
        y0 = cy - 3.6 - 4.6 * t
        pts = [(x0 + 0.8 * sin(TAU * t + j + i * 1.3), y0 - i * 1.3) for i in range(3)]
        out.append(layer(chain(pts, 0.55, 0.4), lambda x, y, e, nx, ny, fr: (STEAM, 0.85 * smooth(0.0, -0.3, e)),
                         alpha=0.9 * (1 - t) * smooth(0.0, 0.15, t)))
    return out


def bean(x, y, r, a=1.0):
    return layer(circle(x, y, r), lambda px, py, e, nx, ny, fr: (lerp(BEAN, BEAN_D, smooth(0.32, 0.14, -e)), 1.0), alpha=a)


def watch(cx, cy, r, k):
    """회중시계 — 금 테 · 흰 판 · 꼭지 · 고리. 긴 바늘이 한 바퀴에 NF 칸 돈다"""
    crown = rbox(cx, cy - r - 0.9, 0.9, 0.75, 0.35)
    loop_ = ring(cx, cy - r - 2.2, 0.85, 0.32)
    case = circle(cx, cy, r)
    out = [base(case, crown, loop_)]
    out.append(_part(crown, GOLD, shade=GOLD_D, ink=GOLD_D, line=0.6, sh=0.5))
    out.append(flat(loop_, GOLD_D))
    out.append(_part(case, lambda x, y: lerp(GOLD_L, GOLD, smooth(cy - r, cy + r * 0.3, y + 0.4 * (x - cx))),
                     shade=GOLD_D, ink=hx("6e5418"), line=0.7, sh=0.8))
    out.append(flat(circle(cx, cy, r - 1.05), DIAL, line=0.3, ink=GOLD_D))
    for i in range(4):                                     # 12 · 3 · 6 · 9 눈금
        a = TAU * i / 4
        out.append(flat(capsule(cx + (r - 1.7) * cos(a), cy + (r - 1.7) * sin(a), cx + (r - 2.2) * cos(a),
                                cy + (r - 2.2) * sin(a), 0.2), NIB))
    t = TAU * k / NF - pi / 2
    out.append(flat(capsule(cx, cy, cx + (r - 1.8) * cos(t), cy + (r - 1.8) * sin(t), 0.26), PUPIL))
    th = -pi / 2 - 0.9
    out.append(flat(capsule(cx, cy, cx + (r - 2.7) * cos(th), cy + (r - 2.7) * sin(th), 0.3), PUPIL))
    out.append(flat(circle(cx, cy, 0.5), BOW_D))
    return out


def bowtie(cx, cy, w, h, line=0.4):
    """앞에서 본 나비넥타이(소품) — 날개 끝을 높게(납작하면 흰 동그라미 속 가로줄 = 진입 금지로 읽힌다)"""
    wings = grow(union(poly([(cx, cy), (cx - w, cy - h), (cx - w, cy + h)]),
                       poly([(cx, cy), (cx + w, cy - h), (cx + w, cy + h)])), 0.3)
    knot = ell(cx, cy, w * 0.26, h * 0.4)
    return [flat(wings, lambda x, y: lerp(BOW_L, BOW, smooth(cy - h, cy + h * 0.2, y)), line=line, ink=BOW_D),
            flat(knot, BOW_D, line=0.25, ink=hx("6e1520"))]


# ---- 칸마다 장면 (art 좌표, 화살표 칸은 catkit 빼꼼) ----

def sc_busy(fr):
    """작은 화살표 턱시도냥 + 찻잔 둘레를 도는 분홍 발자국 여덟"""
    out = buddy(fr)
    cx, cy = 22.5, 22.5
    k = kof(fr)
    head = k * 8 / NF
    for i in range(8):
        a = TAU * i / 8 - pi / 2
        lag = (head - i) % 8
        out.append(paw_print(cx + 6.9 * cos(a), cy + 6.6 * sin(a), 1.0 if lag < 1.5 else 0.6 if lag < 3 else 0.28))
    out += teacup(cx - 0.6, cy - 0.2, k)
    return out


def _qpath():
    """물음표 길(콩 자리) — 고리 위 왼쪽에서 오른쪽으로 돌아 내려와 줄기"""
    cx, cy, r = 22.6, 15.0, 4.0
    pts = []
    n = 8
    for i in range(n):
        a = -pi * 1.08 + (pi * 1.5) * i / (n - 1)
        pts.append((cx + r * cos(a), cy + r * sin(a)))
    pts += [(cx, cy + r + 1.9), (cx, cy + r + 4.1)]
    return pts


QPATH = _qpath()


def sc_help(fr):
    """작은 화살표 턱시도냥 + 젤리 콩으로 찍은 물음표 — 하나씩 차례로 꾹(커지고 진해짐), 점은 발자국"""
    out = buddy(fr)
    k = kof(fr)
    n = len(QPATH) + 1
    cur_i = k * n / NF
    for i, (x, y) in enumerate(QPATH):
        d = (cur_i - i) % n
        press = d < 1.0
        out.append(bean(x, y, 1.6 if press else 1.2, 1.0 if d < 4 else 0.75))
    d = (cur_i - len(QPATH)) % n
    out.append(paw_print(22.6, 27.4, 1.0 if d < 1.0 else 0.7))
    return out


def sc_person(fr):
    """작은 화살표 턱시도냥 + 나비넥타이를 맨 신사 냥 흉상 — 턱시도 깃 사이 흰 셔츠, 깜빡 · 귀 까딱"""
    k = kof(fr)
    out = buddy(fr)
    F = Frame(22.4, 20.4, 0.64)
    torso = clip_y(F.f(ell(0, 11.2, 10.0, 6.6)), 30.6)

    def tcol(x, y):
        u, v = F.loc(x, y)
        if abs(u) < 0.6 + (v - 4.2) * 0.62:                # 깃 사이로 벌어지는 흰 셔츠(V)
            return WHITE
        return lerp(FUR, FUR_HI, 0.6 * smooth(1.0, 0.2, ((u + 5.6) / 2.4) ** 2 + ((v - 8.2) / 2.4) ** 2))
    tilt = (0.0, 1.0) if k in (9, 10) else (0.0, 0.0)
    out += tcat(F, "blink" if k == 6 else "open", body=False, paws=False, tail=False,
                extra_under=[(torso, tcol)], ear_tilt=tilt)
    # 깃 안쪽 선(깃과 셔츠 경계를 또렷이)
    for sg in (-1, 1):
        out.append(flat(capsule(*F.w(sg * 0.9, 5.4), *F.w(sg * 5.2, 12.2), 0.26), OUT, 0.9))
    return out


def sc_pin(fr):
    """작은 화살표 턱시도냥 + 흰 동그라미 속 나비넥타이가 든 빨간 핀이 통통"""
    out = buddy(fr)
    hop = abs(sin(pi * fr))
    cx, cy = 22.6, 15.2 - 2.6 * hop
    out.insert(0, layer(ell(22.8, 29.0, 3.4 - 0.8 * hop, 0.75), lambda *a: (OUT, 0.2)))
    f = smin(1.0, circle(cx, cy, 5.6), poly([(cx - 4.6, cy + 2.6), (cx + 4.6, cy + 2.6), (cx, cy + 11.4)]))
    out += [base(f), _part(f, lambda x, y: lerp(SIGN_L, SIGN, smooth(cy - 5, cy - 1.5, y + 0.6 * (x - cx))),
                           shade=SIGN_D, ink=SIGN_D)]
    out.append(flat(circle(cx, cy, 3.8), WHITE, line=0.5, ink=SIGN_D))
    out += bowtie(cx, cy, 2.75, 1.85, 0.35)
    return out


def sc_wait(fr):
    """회중시계를 앞발로 들고 새침하게 들여다본다 — 바늘이 돌고 꼬리 끝이 똑딱똑딱, 가끔 깜빡. 시계 가운데가 핫스팟"""
    k = kof(fr)
    W = (6.5, 10.5)
    out = watch(W[0], W[1], 4.5, k)
    F = Frame(20.0, 14.2, 0.8)
    tick = 1.3 if k % 2 else -1.3
    tp = [(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.6 + 0.4 * tick, 3.9), (8.6 + tick, 1.6)]
    hand = F.loc(11.6, 9.2)
    out += tcat(F, "blink" if k == 6 else "smug", look=(-1.0, 0.0), turn_=-1.0, tail_pts=tp,
                arms=[((-5.2, 3.8), hand, False)])
    # 시계 줄 — 꼭지 고리에서 발로
    cx, cy = W[0], W[1] - 4.5 - 2.2
    hx_, hy_ = 11.0, 8.0
    mid = ((cx + hx_) / 2 + 0.4, min(cy, hy_) - 1.4)
    out.append(flat(chain([(cx + 0.7, cy - 0.3), mid, (hx_, hy_)], 0.28), GOLD_D))
    return out


def sc_cross(fr):
    """가는 조준선 가운데 빨간 레이저 점(핫스팟) — 오른쪽 아래에서 동공이 커진 냥이 엉덩이를 씰룩이며 노린다"""
    ph = TAU * fr
    k = kof(fr)
    C_ = 15.5
    lines = union(capsule(2.6, C_, 11.0, C_, 0.42), capsule(20.0, C_, 28.6, C_, 0.42),
                  capsule(C_, 2.6, C_, 11.0, 0.42), capsule(C_, 20.0, C_, 28.6, 0.42))
    out = [base(lines), flat(lines, OUT)]
    g = 2.4 if k % 4 < 2 else 1.7
    out.append(layer(circle(C_, C_, g), lambda x, y, e, nx, ny, fr_: (LASER, 0.45 * smooth(0.0, -g, e) + 0.1)))
    out.append(flat(circle(C_, C_, 1.0), lambda x, y: lerp(LASER_L, LASER, smooth(0.0, 0.8, hypot(x - C_ + 0.3, y - C_ + 0.3)))))
    wig = 0.6 * sin(2 * ph)
    F = Frame(24.6 + wig, 22.6, 0.5)
    sw = sin(2 * ph)
    tp = [(3.6, 10.4), (7.8, 10.6), (9.6, 7.6), (9.0 + 1.2 * sw, 4.4), (7.6 + 2.0 * sw, 3.0)]
    out += tcat(F, "wide", look=(-0.9, -0.7), tail_pts=tp, ear_tilt=(-0.6, -0.6))
    return out


def sc_hand(fr):
    """앞발 하나를 왼쪽 위로 쭉 들어 콕 — 발끝은 그대로, 몸이 숨 쉬듯 들썩 · 깜빡 · 꼬리 살랑. 콕 할 때 반짝"""
    ph = TAU * fr
    k = kof(fr)
    tap = k % 6 in (0, 1)
    s = 0.8
    breathe = 0.25 * sin(ph)
    F = Frame(16.0, 15.4 + breathe, s)
    hand = F.loc(4.45, 6.45)
    out = tcat(F, "blink" if k == 5 else "open", turn_=-0.6, look=(-0.7, -0.6), sway=0.6 * sin(ph),
               arms=[((-5.6, 3.6), hand, True)], ear_tilt=(-0.9, 0.0))
    if tap:
        L = 1.9 if k % 6 == 0 else 1.3
        out += sparkle(1.9, 9.6, L, 0.55) + sparkle(8.4, 2.2, L, 0.55)
    return out


def sc_ibeam(fr):
    """스크래처 I(위 판 · 밧줄 기둥 · 아래 받침) — 옆에 선 냥이 앞발을 번갈아 위에서 아래로 박박, 밧줄에 긁힌 자국.
    핫스팟은 기둥 가운데. 두 발이 같은 높이에서 마주 오가면 박수로 읽혀 한 발이 내려갈 때 다른 발은 들어 올린다"""
    ph = TAU * fr
    k = kof(fr)
    X = 6.5
    top = rbox(X, 2.6, 5.4, 1.3, 0.5)
    foot = rbox(X, 29.0, 5.6, 1.5, 0.6)
    post = rbox(X, 15.8, 1.85, 12.2, 0.4)

    def rope(x, y):
        m = (y + (x - X) * 0.9) % 2.0
        return lerp(ROPE, ROPE_D, smooth(0.5, 0.2, min(m, 2.0 - m)))
    out = [base(top, foot, post), _part(post, rope, shade=ROPE_D, ink=hx("6a4f28"), line=0.85, sh=0.6)]
    out.append(_part(top, PLANK, shade=PLANK_D, ink=hx("3a2416"), line=0.85, sh=0.8))
    out.append(_part(foot, PLANK, shade=PLANK_D, ink=hx("3a2416"), line=0.85, sh=0.8))
    F = Frame(19.4, 14.4, 0.64)
    arms, marks = [], []
    for i, sh_ in enumerate(((-5.8, 2.6), (-4.4, 4.6))):
        t = (k / 6 + i / 2) % 1
        if t < 0.66:
            s_ = t / 0.66
            tip = (9.2, 6.6 + 12.0 * s_)
            marks.append(tip[1])
        else:
            s_ = (t - 0.66) / 0.34
            tip = (11.6, 18.6 - 12.0 * s_)
        arms.append((sh_, F.loc(*tip), False))
    for y1 in marks:                                       # 긁은 자리 — 밧줄이 일어난 흰 줄 셋
        for dx in (-0.95, 0.0, 0.95):
            out.append(flat(capsule(X + dx, 6.2, X + dx, y1, 0.22), SCRATCH, 0.9))
    sw = sin(2 * ph)
    out += tcat(F, "smug" if k % 6 < 4 else "closed", turn_=-1.2, look=(-1.0, 0.0), arms=arms,
                tail_pts=[(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.4 + 0.6 * sw, 3.9), (8.2 + 1.0 * sw, 2.0)])
    return out


def sc_pen(fr):
    """깃펜을 쥐고 글씨를 쓰는 신사 — 깃털이 펜촉을 축으로 까딱, 펜촉 뒤로 잉크 줄이 길어진다. 펜촉이 핫스팟"""
    ph = TAU * fr
    k = kof(fr)
    tip = (1.55, 22.5)
    ang = -0.87 + 0.06 * sin(2 * ph)
    ux, uy = cos(ang), sin(ang)
    nx_, ny_ = -uy, ux                                     # 깃의 한쪽(아래 오른쪽)
    out = []
    n = 2 + k                                              # 잉크 줄(필기체 물결)
    xs = [3.0 + 0.9 * i for i in range(2 * n)]
    pts = [(x, 25.6 + 0.7 * sin(x * 1.6)) for x in xs]
    if len(pts) > 1:
        out.append(flat(chain(pts, 0.38), INK))

    def P(t, o=0.0):
        return tip[0] + ux * t + nx_ * o, tip[1] + uy * t + ny_ * o
    L = 20.0
    vane = poly([P(5.0, 0), P(8.5, -2.2), P(16.0, -2.7), P(L, -0.8), P(L + 0.6, 0.2), P(16.0, 2.2), P(8.5, 1.5)])
    vane = grow(vane, 0.35)
    nib = poly([P(-0.25, 0), P(3.2, -0.85), P(5.4, -0.6), P(5.4, 0.6), P(3.2, 0.85)])
    shaft = capsule(*P(3.0), *P(L - 0.8), 0.3)
    out += [base(vane, nib)]
    out.append(_part(vane, lambda x, y: QUILL_D if ((x - tip[0]) * nx_ + (y - tip[1]) * ny_) > 0.5 else QUILL,
                     shade=QUILL_D, ink=hx("5a5648"), line=0.8, sh=0.4))
    for t, o in ((10.5, -2.4), (14.0, -2.6), (17.5, -2.0)):     # 깃 가장자리 갈라진 홈
        out.append(flat(capsule(*P(t, o + 0.2), *P(t + 1.1, o - 0.7), 0.22), hx("5a5648")))
    out.append(flat(shaft, QUILL_D))
    out.append(_part(nib, lambda x, y: NIB, shade=hx("22222c"), ink=OUT, line=0.6, sh=0.3))
    out.append(flat(capsule(*P(1.2), *P(4.4), 0.16), hx("9a9aa8")))   # 펜촉 갈라진 금
    F = Frame(20.6, 10.6, 0.72)
    hold = F.loc(*P(11.6))
    out += tcat(F, "blink" if k == 4 else "smug", look=(-0.8, 0.6), turn_=-0.9, sway=0.5 * sin(ph),
                arms=[((-5.4, 3.8), hold, False)])
    return out


def sc_no(fr):
    """빨간 금지 표지 앞에서 코를 치켜들고 눈을 감은 채 앞발 하나를 내밀어 '사양하겠소' — 고개를 홱 들었다 내린다.
    원본처럼 냥이를 표지 위에 그린다(표지를 위에 얹으면 빗금이 얼굴을 가려 검은 덩어리가 된다)"""
    k = kof(fr)
    C_ = 14.5
    up = 3 <= k <= 9
    R = 12.5
    sg = union(ring(C_, C_, R - 1.25, 1.25), capsule(C_ - 7.7, C_ - 7.7, C_ + 7.7, C_ + 7.7, 1.35))
    out = [base(sg), _part(sg, lambda x, y: lerp(SIGN_L, SIGN, smooth(C_ - 10, C_ - 4, y + 0.5 * x - 0.5 * C_)),
                           shade=SIGN_D, ink=SIGN_D, line=0.8)]
    F = Frame(C_ + 0.9, C_ - 1.2 + (0.0 if up else 0.3), 0.6, -0.2 if up else -0.05)
    out += tcat(F, "closed" if up else "smug", turn_=0.45 if up else 0.25, look=(0.6, 0.0), mouth="",
                arms=[((-4.2, 5.6), (-11.4, 4.4 if up else 5.6), True)], ear_tilt=(0.0, 1.2 if up else 0.0),
                tail_pts=[(3.6, 10.4), (7.8, 10.6), (9.6, 7.4), (9.0, 3.6), (7.8, 1.8)])
    return out


def sc_up(fr):
    """신사 지팡이를 앞발로 쥐고 머리 위로 곧게 치켜든다 — 금 손잡이(맨 위)가 핫스팟이라 지팡이는 그대로,
    눈은 손잡이를 올려다보고 꼬리 · 귀만 살랑, 가끔 깜빡"""
    ph = TAU * fr
    k = kof(fr)
    X = 2.6
    knob = circle(X, 2.75, 1.25)
    shaft = union(capsule(X, 3.4, X, 16.6, 0.6), arc(X + 1.6, 16.6, 1.6, 0.6, pi, -pi * 0.9))
    out = [base(knob, shaft), _part(shaft, CANE, shade=FUR_D, ink=OUT, line=0.6, sh=0.4)]
    out.append(flat(capsule(X, 3.9, X, 4.6, 0.75), GOLD_D))     # 손잡이 목 띠
    out.append(_part(knob, lambda x, y: lerp(GOLD_L, GOLD, smooth(1.8, 3.8, y + 0.4 * (x - X))),
                     shade=GOLD_D, ink=hx("6e5418"), line=0.6, sh=0.6))
    F = Frame(11.2, 17.0, 0.72)
    sw = sin(ph)
    hand = F.loc(X + 0.5, 9.6)
    tp = [(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.6 + 1.0 * sw, 3.6), (8.4 + 1.6 * sw, 1.4)]
    out += tcat(F, "blink" if k == 7 else "open", look=(-0.7, -0.9), turn_=-0.5, tail_pts=tp,
                arms=[((-5.6, 3.4), hand, False)], ear_tilt=(0.5 * max(0.0, sw), 0.5 * max(0.0, -sw)))
    return out


def sc_move(fr):
    """앞모습으로 앉아 앞발을 번갈아 들며 사뿐사뿐 제자리 걸음 — 네 방향 빨간 화살촉이 두근댄다"""
    ph = TAU * fr
    k = kof(fr)
    o = 0.6 if k % 6 < 3 else 0.0
    out = []
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        out += rchev(15.5 + dx * (13.6 + o), 15.5 + dy * (13.6 + o), dx, dy, 2.2)
    s_ = sin(ph)
    s = 0.66
    F = Frame(15.5, 15.5 - 5.3 * s - 0.3 * abs(s_), s)
    lift = (2.2 * max(0.0, s_), 2.2 * max(0.0, -s_))
    feet = [(F.f(ell(sg * 2.45, 11.35 - lift[i], 1.95, 1.4)), WHITE) for i, sg in enumerate((-1, 1))]
    out += tcat(F, "blink" if k == 9 else "open", paws=False, extra_under=feet, sway=0.6 * s_,
                tail_pts=[(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.4 + 0.6 * s_, 3.9), (8.2 + 1.0 * s_, 2.0)])
    return out


def sc_ns(fr):
    """제자리 수직 점프 — 웅크렸다(몸이 눌림) 떠올라 뒷발을 늘어뜨리고 다시 내려앉는다. 위아래 화살촉"""
    k = kof(fr)
    t = k / NF
    h = max(0.0, sin(pi * (t - 0.17) / 0.66)) if 0.17 <= t <= 0.83 else 0.0
    X = 4.9
    s = 0.5
    out = []
    for sg in (-1, 1):
        o = 0.6 if (sg < 0) == (h > 0.3) else 0.0
        out += rchev(X - 0.4, 15.5 + sg * (13.6 + o), 0, sg, 2.2)
    squash = k in (0, 1, 11)
    F = Frame(X, 16.4 - 7.0 * h + (0.6 if squash else 0.0), s)
    if h > 0:                                              # 떠오름: 몸이 길어지고 뒷발 · 꼬리가 늘어진다
        feet = [(F.f(ell(sg * 2.3, 12.9, 1.6, 1.75)), WHITE) for sg in (-1, 1)]
        out += tcat(F, "open", look=(0.0, -0.6), bob=-1.4, paws=False, extra_under=feet,
                    tail_pts=[(3.6, 10.6), (6.0, 12.0), (7.0, 14.4)], ear_tilt=(0.4, 0.4))
    else:
        out += tcat(F, "blink", bob=1.0 if squash else 0.3, ear_tilt=(-0.8, -0.8) if squash else (0.0, 0.0),
                    tail_pts=[(3.6, 10.4), (7.4, 10.8), (9.2, 8.6), (9.4, 5.6)])
    return out


def sc_we(fr):
    """꼬리를 곧게 세우고 새침하게 걷는다 — 앞 반은 왼쪽으로, 뒤 반은 돌아서 오른쪽으로. 가는 쪽 화살촉이 두근댄다"""
    k = kof(fr)
    half = k < NF // 2
    j = k % (NF // 2)
    d = 1.5 - 3.0 * j / (NF // 2 - 1)
    x = 15.5 + (d if half else -d)
    S = SF(x, 13.4, 0.62, 0.0, flip=not half)
    out = []
    go = -1 if half else 1
    for sg in (-1, 1):
        o = 0.6 if sg == go and j % 3 < 2 else 0.0
        out += rchev(15.5 + sg * (13.6 + o), 9.5, sg, 0, 2.2)
    out += side_cat(S, TAU * j / (NF // 2) * 2, run=False, mood="smug")
    return out


def run_diag(fr, mirror):
    """대각선을 따라 다다닥 — 앞 반은 위로(nwse 는 왼쪽 위, nesw 는 오른쪽 위), 뒤 반은 돌아서 아래로.
    다리를 쭉 폈다 배 밑에 모았다 하고 몸이 들썩인다. 가는 쪽 화살촉이 깜빡"""
    k = kof(fr)
    h = NF // 2
    half = k < h
    j = k % h
    sx = 1 if mirror else -1                               # 위로 갈 때 x 방향
    D = (sx * 0.7071, -0.7071) if half else (-sx * 0.7071, 0.7071)
    d = 1.6 - 3.2 * j / (h - 1)
    cx, cy = 15.5 - D[0] * d, 15.5 - D[1] * d
    flip = D[0] > 0
    ang = math.atan2(D[1], D[0]) if flip else math.atan2(-D[1], -D[0])
    ang = max(-0.5, min(0.5, ang))
    S = SF(cx, cy + 1.0, 0.62, ang, flip)
    out = []
    ends = ((2.0, 2.0, -1, -1), (29.0, 29.0, 1, 1)) if not mirror else ((29.0, 2.0, 1, -1), (2.0, 29.0, -1, 1))
    for i, (x, y, dx, dy) in enumerate(ends):
        on = (i == 0) == half and j % 3 < 2
        o = 0.6 if on else 0.0
        out += rchev(x + dx * o, y + dy * o, dx, dy, 2.4, 1.0 if on else 0.75)
    out += side_cat(S, TAU * j / h, run=True, mood="open")
    return out


def sc_nwse(fr):
    return run_diag(fr, False)


def sc_nesw(fr):
    return run_diag(fr, True)


SCENE = {"busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "wait": sc_wait,
         "hand": sc_hand, "cross": sc_cross, "ibeam": sc_ibeam, "move": sc_move, "no": sc_no, "pen": sc_pen,
         "up": sc_up, "we": sc_we, "ns": sc_ns, "nwse": sc_nwse, "nesw": sc_nesw}


class TuxedoCat(Pet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes).
    칸을 그리는 동안만 catkit 의 face · shut · part 를 턱시도 판으로 갈아 끼운다(_dress)"""

    def cell(self, name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
        with _dress():
            return super().cell(name, frame, soft_, tip_body, shape)


PET = TuxedoCat(COAT, SCENE, HOT)


def scene(name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
    return PET.cell(name, frame, soft_, tip_body, shape)


register("tuxedocat", PET)

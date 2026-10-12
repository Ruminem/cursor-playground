# SPDX-License-Identifier: Apache-2.0
"""삼색냥(calicocatanim) 고화질 — 치비(머리가 몸만 한 통통 냥) · 스티커 채색(고른 먹선 1칸 + 셀 그늘 한 단).

픽셀 삼색냥(gen/calicocat.py)을 HD 로 옮겼다. 흰 바탕에 큰 얼룩 — 왼 귀와 이마 왼쪽은 주황, 오른 귀와 이마 오른쪽은
까망, 몸 왼쪽 위 주황 한 덩이 · 오른쪽 아래 까만 한 덩이, 꼬리는 까망에 끝만 주황. 얼룩은 냥이 제 좌표(Frame)에 붙여
찍어서 장마다 같은 자리에 붙어 다니고, 눈 둘레는 늘 흰 바탕으로 비운다(까만 얼룩에 눈이 묻히면 한쪽 눈이 없어 보임).
소품의 주인공은 골판지 상자와 꾹꾹이 담요다. 칸마다 하는 짓은 픽셀 판 그대로:

  arrow   크림 화살표 빗변 뒤에서 빼꼼(catkit.peek) — 빗변을 잡은 앞발 둘은 주황
  busy    작은 화살표 삼색냥 + 작은 골판지 상자 둘레를 도는 분홍 발자국 여덟, 상자 날개가 까딱
  cross   앞모습 얼굴 — 볼 수염이 가로 조준선, 위로 낚싯대 장난감 줄(끝 깃털이 까딱) · 턱 밑 줄이 세로선. 코가 핫스팟
  hand    앉은 삼색냥이 짧은 앞발을 들어 큰 흰 발바닥(분홍 젤리)으로 톡톡 — 누를 때 발바닥이 퍼지고 눈은 ^^. 발바닥 꼭대기가 핫스팟
  help    작은 화살표 삼색냥 + 까만 꼬리(끝 주황)를 말아 만든 물음표, 점은 분홍 발자국
  ibeam   스크래처 기둥(삼줄)이 I — 뒷발로 서서 끌어안고 두 앞발을 번갈아 박박 긁는다(긁힌 자국). 핫스팟은 기둥 가운데
  move    골판지 상자에 쏙 들어간 삼색냥이 상자째 좌우로 들썩 — 네 방향 분홍 화살촉
  no      빨간 금지 표지 안에서 상자에 든 삼색냥이 날개를 닫아 버린다 — 닫힌 날개 틈으로 귀 끝만, 다시 빼꼼
  ns      막대에 두 앞발로 매달려 몸이 축 늘었다 줄었다, 뒷발 · 꼬리가 대롱대롱 — 위아래 화살촉
  we · nwse · nesw   배 깔고 엎드린 길쭉한 식빵이 그 축으로 늘었다 줄었다(머리는 늘 똑바로) — 양 끝 화살촉
  pen     붓을 두 앞발로 쥐고 먹 글씨 — 붓끝(왼쪽 아래)이 핫스팟, 먹 줄이 차츰 길어진다
  person  작은 화살표 삼색냥 + 삼색 귀 후드(왼 귀 주황 · 오른 귀 까망)를 쓴 사람이 손을 흔든다
  pin     작은 화살표 삼색냥 + 동그라미 속에 삼색냥 얼굴(귀가 핀 위로 솟음)이 든 빨간 지도 핀이 통통
  up      상자에서 쏙 일어서 주황 앞발을 머리 위로 번쩍(저요!) — 든 발끝(맨 위)이 핫스팟, 상자 날개가 들썩
  wait    보라 담요 위 꾹꾹이 — 두 앞발을 번갈아 눌러 담요가 움푹, 눈은 ^^ 로 골골

좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 장면은 NF 장으로 나뉘어 있다(k = round(fr × NF) % NF).
틀(먹선 · 치비 몸 · 빼꼼 · 모양 화살표)은 catkit 에 있고 여기는 털빛 · 소품 · 장면만 둔다.
"""
from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

from . import catkit, register
from .catkit import *  # noqa: F401,F403

# 픽셀 판 팔레트(gen/calicocat.py) 그대로
OUT, EYE = hx("3a2a30"), hx("2a1c22")
WHITE, WHITE_D = hx("fff6e8"), hx("eadcca")
ORNG, ORNG_D = hx("ec8f3c"), hx("c46a26")
BLK, BLK_D = hx("4d424b"), hx("40363e")          # 까만 얼룩은 먹선과 갈리게 조금 밝게(픽셀 판 그대로)
NOSE, CHEEK, RIM = hx("e27d90"), hx("f4a0b0"), hx("fbecdc")
IRIS, IRIS_D, IRIS_L = hx("9cc24c"), hx("5a8a2c"), hx("d8eea4")   # 픽셀 판은 까만 눈 — HD 는 홍채가 있어 연두 금빛으로
BOX, BOX_D, BOX_L, BOX_IN = hx("d2a466"), hx("a5793f"), hx("e8c690"), hx("6e4c2c")
BLANK, BLANK_D, BLANK_L = hx("b9a3dc"), hx("8d74b8"), hx("d8cbef")
SISAL, SISAL_D, POST, POST_D = hx("dcc08a"), hx("b0915a"), hx("8fa7c8"), hx("6683aa")
BRUSH, BRUSH_D, INKC = hx("c9a46a"), hx("8f6c38"), hx("2b2630")
SHIRT, SHIRT_D, SKIN, SKIN_D = hx("6aa36a"), hx("487a4a"), hx("f7d7bc"), hx("e8bfa0")
SIGN, SIGN_D, SIGN_L = hx("d64541"), hx("9e2b28"), hx("ef7a72")
SCRATCH = hx("fff4dc")


# ---- 털: 얼룩마다 그늘 색이 따로 ----
# catkit.part 는 그늘을 고정 색 하나로 받아(hd.lerp 가 q[0..2] 로 읽음) 얼룩 위 그늘 띠가 흰 털 그늘(크림)로 칠해진다.
# 털 색 함수가 고른 얼룩을 _now 에 적어 두고, 그늘 자리(_Shade)가 그 얼룩의 그늘을 돌려준다 — part 의 paint 가
# col(x, y) 를 부른 바로 다음에 lerp(c, shade, …) 하므로 같은 칸의 얼룩이다. 한 프로세스가 한 칸씩 그린다는 catkit 전제 그대로.
_SH = {WHITE: WHITE_D, ORNG: ORNG_D, BLK: BLK_D}
_now = [WHITE_D]


def _pick(c):
    _now[0] = _SH[c]
    return c


class _Shade:
    def __getitem__(self, i):
        return _now[0][i]


def spots(*blobs, base=WHITE, loc=None, keep=None):
    """흰 바탕 위 큰 얼룩 → (x, y) → 색. blobs = (거리함수, 색) — 앞의 것이 이긴다. loc 이 있으면 그 좌표로 옮겨 잰다.
    keep(u, v) 가 참인 자리는 바탕 그대로(눈 둘레)"""
    def col(x, y):
        u, v = loc(x, y) if loc else (x, y)
        if keep is None or not keep(u, v):
            for f, c in blobs:
                if f(u, v) < 0:
                    return _pick(c)
        return _pick(base)
    return col


def solid(c):
    return lambda x, y: _pick(c)


def tail_col(tip, n=1.9):
    """까만 꼬리 — 끝(tip)에서 n 안쪽만 주황"""
    tx, ty = tip
    return lambda x, y: _pick(ORNG if hypot(x - tx, y - ty) < n else BLK)


# 캐논(머리 가운데 (0, 0)) 얼룩 자리 — 머리 ell(0, -0.4, 6.9, 5.6) ∪ ell(0, 1.3, 7.6, 4.3) · 몸 ell(0, 7.7, 5.4, 4.4)
HEAD_SPOTS = ((oell(-4.4, -4.1, 3.9, 2.7, -0.45), ORNG), (oell(4.6, -4.3, 3.6, 2.5, 0.45), BLK))
BODY_SPOTS = ((oell(-3.5, 6.6, 3.0, 2.4, -0.4), ORNG), (ell(4.3, 9.5, 2.7, 2.6), BLK))


class Calico(Coat):
    """삼색 털빛 — 부위마다 얼룩을 냥이 제 좌표에 붙여 찍는다. F 없이 부르면(catkit 빼꼼 앞발 · 기지개) 단색:
    빼꼼 화살표 빗변을 잡는 앞발은 흰 발(주황이면 32 판에서 고리로 뭉개짐)"""

    def fur(self, part, F=None, turn_=0.0):
        if F is None:
            return solid(BLK if part == "tail" else WHITE)
        loc = F.loc
        if part == "head":
            def eyes(u, v):                                    # 눈 둘레는 흰 바탕
                uf = u - 0.4 * turn_
                return min(hypot((uf + sg * 3.15) / 2.5, (v - 0.25) / 2.75) for sg in (-1, 1)) < 1
            d = 0.6 * turn_
            return spots(*HEAD_SPOTS, loc=lambda x, y: (loc(x, y)[0] - d, loc(x, y)[1]), keep=eyes)
        if part == "ear":
            return lambda x, y: _pick(ORNG if loc(x, y)[0] < 0.3 * turn_ else BLK)
        if part == "body":
            return spots(*BODY_SPOTS, loc=loc)
        if part == "tail":
            return lambda x, y: _pick(ORNG if loc(x, y)[1] < 3.1 else BLK)
        if part == "arm":
            def arm(x, y):                                     # 어깨 쪽 윗팔만 주황 — 길게 뻗은 팔이 당근으로 안 읽히게
                u, v = loc(x, y)
                return _pick(ORNG if u < turn_ and v > 4.2 else WHITE)
            return arm
        return solid(WHITE)


COAT = Calico(WHITE, _Shade(), OUT, EYE, RIM, ((IRIS, IRIS_D, IRIS_L), (IRIS, IRIS_D, IRIS_L)), cheek=CHEEK, nose=NOSE)

# 픽셀 판 핫스팟(art/calicocatanim 머리) 그대로 — 적용한 사람의 손에 익은 자리
HOT = {"arrow": (1, 1), "busy": (1, 1), "cross": (15, 15), "hand": (6, 2), "help": (1, 1), "ibeam": (6, 14),
       "move": (15, 15), "nesw": (13, 13), "no": (14, 14), "ns": (8, 15), "nwse": (13, 13), "pen": (1, 22),
       "person": (1, 1), "pin": (1, 1), "up": (4, 1), "wait": (14, 15), "we": (15, 6)}


def kof(fr):
    return round(fr * NF) % NF


def ID():
    return Frame()


# ---- 소품: 골판지 상자 ----

def box(B, w, h, flap):
    """앞에서 본 열린 골판지 상자 → (뒤 층, 앞 층). B 는 상자 제 좌표(앞판 윗변 가운데 (0, 0), 아래 +v).
    flap 은 날개가 벌어진 정도 — 1 이면 바깥으로 활짝(155°), 0 이면 안쪽으로 누워 입구를 덮는다(그때 날개는 앞 층).
    머리를 뒤 층과 앞 층 사이에 그리면 상자에 쏙 들어간다"""
    al = math.radians(155.0 * flap)
    L = w * (1.02 if flap < 0.5 else 0.8)
    fl = []
    for sg in (-1, 1):
        dx, dy = -sg * cos(al), -sin(al)
        nx, ny = -dy * 1.2, dx * 1.2
        hx_, hy_ = sg * w, -0.25
        ex, ey = hx_ + dx * L, hy_ + dy * L
        fl.append(B.f(rpoly([(hx_ + nx, hy_ + ny), (ex + nx, ey + ny), (ex - nx, ey - ny), (hx_ - nx, hy_ - ny)], 0.3)))
    front = B.f(rbox(0, h / 2, w, h / 2, 0.5))
    inner = B.f(rbox(0, -0.4, w - 0.7, 1.0, 0.5))

    def fcol(x, y):
        u, v = B.loc(x, y)
        return BOX_L if abs(u) < 0.75 * B.s and v < h * 0.38 else BOX
    flaps = [part(f, BOX_L, shade=BOX, sh=0.7) for f in fl]
    back = [base(inner), part(inner, BOX_IN, shade=BOX_IN, sh=0.0)]
    fr_ = [part(front, fcol, shade=BOX_D)]
    if flap >= 0.5:
        return [base(inner, *fl)] + back[1:] + flaps, [base(front)] + fr_
    return back, [base(front, *fl)] + fr_ + flaps


def rim_paws(B, us, w=1.75):
    """상자 턱에 걸친 흰 앞발들"""
    fs = [B.f(ell(u, 0.15, w, w * 0.68)) for u in us]
    return [base(*fs)] + [part(f, solid(WHITE)) for f in fs]


def box_cat(fr, B, ang, w, h, flap, peek, s, mood="open", paws=True, look=(0.0, 0.0)):
    """상자에 쏙 들어간 삼색냥(앞모습) — 머리만 상자 위로, 두 앞발은 상자 턱에. peek 은 머리가 올라온 정도(0–1)"""
    back, front = box(B, w, h, flap)
    F = Frame(*B.w(0, 2.7 - 7.4 * peek), s, ang)
    head = cat(F, mood, look=look, body=False, paws=False, tail=False, mouth="" if peek < 0.7 else "w")
    out = back + head + front
    if paws:
        out += rim_paws(B, (-3.0, 3.0))
    return out


# ---- 장면 (art 좌표, 화살표 칸은 catkit 빼꼼) ----

def sc_busy(fr):
    """작은 화살표 삼색냥 + 작은 골판지 상자 둘레를 도는 분홍 발자국 여덟 — 상자 날개가 까딱"""
    ph = TAU * fr
    k = kof(fr)
    out = buddy(fr)
    cx, cy = 22.5, 22.5
    head = k * 8 / NF
    for i in range(8):
        a = TAU * i / 8 - pi / 2
        lag = (head - i) % 8
        out.append(paw_print(cx + 7.0 * cos(a), cy + 6.7 * sin(a), 1.0 if lag < 1.5 else 0.6 if lag < 3 else 0.28))
    back, front = box(Frame(cx, cy - 0.4), 3.0, 3.3, 0.72 + 0.16 * sin(2 * ph))
    return out + back + front


def sc_help(fr):
    """작은 화살표 삼색냥 + 까만 꼬리(끝 주황)를 말아 만든 물음표 — 꼬리 끝이 살랑, 점은 분홍 발자국"""
    ph = TAU * fr
    out = buddy(fr)
    cx, cy, r = 24.4, 13.6, 3.5
    pts = [(cx - r, cy + 0.9 * sin(ph))]
    for i in range(1, 8):
        a = pi + pi * 1.32 * i / 7
        pts.append((cx + r * cos(a), cy + r * sin(a)))
    pts += [(cx + 0.1, cy + 5.6), (cx, cy + 8.4)]
    f = chain(pts, 1.05, 1.45)
    out += [base(f), part(f, tail_col(pts[0], 2.1), shade=_Shade())]
    out.append(paw_print(cx, cy + 12.6, 1.0))
    return out


def sc_person(fr):
    """작은 화살표 삼색냥 + 삼색 귀 후드(흰 바탕, 왼 귀 주황 · 오른 귀 까망)를 쓴 사람이 왼손을 흔든다"""
    ph = TAU * fr
    out = buddy(fr)
    cx, cy = 23.2, 22.8
    wave = abs(sin(ph))
    hand = (cx - 7.6 + 0.5 * wave, cy + 0.4 - 1.8 * wave)
    sleeve = capsule(cx - 4.4, cy + 5.4, hand[0] + 0.4, hand[1] + 0.9, 1.35)
    palm = circle(*hand, 1.45)
    body = clip_y(ell(cx, cy + 8.6, 7.0, 5.0), 30.4)
    hood = smin(0.8, ell(cx, cy - 0.2, 5.4, 4.9), ell(cx, cy + 1.6, 5.8, 3.4))
    ears = [rpoly([(cx + sg * 5.2, cy - 1.6), (cx + sg * 4.6, cy - 7.4), (cx + sg * 1.2, cy - 4.4)], 0.6) for sg in (-1, 1)]
    skin = ell(cx, cy + 0.9, 3.6, 3.2)
    out += [base(body, sleeve, palm, hood, *ears), part(body, SHIRT, shade=SHIRT_D), part(sleeve, SHIRT, shade=SHIRT_D),
            part(palm, SKIN, shade=SKIN_D)]
    for sg, E in zip((-1, 1), ears):
        out.append(part(E, solid(ORNG if sg < 0 else BLK), shade=_Shade()))
        out.append(flat(grow(E, -1.15), CHEEK))
    hcol = spots((oell(cx - 3.4, cy - 3.0, 3.0, 1.9, -0.4), ORNG), (oell(cx + 3.5, cy - 3.1, 2.8, 1.8, 0.4), BLK))
    out.append(part(hood, hcol, shade=_Shade()))
    out.append(part(skin, SKIN, shade=SKIN_D, sh=0.6))
    for sg in (-1, 1):
        out.append(flat(ell(cx + sg * 1.5, cy + 0.6, 0.5, 0.72), EYE))
        out.append(soft(ell(cx + sg * 2.5, cy + 2.1, 0.85, 0.5), CHEEK, 0.85))
    out.append(flat(arc(cx, cy + 1.5, 0.95, 0.22, pi * 0.15, pi * 0.7), SHIRT_D))
    for j in (-1, 1):                                        # 흔드는 손 옆 짧은 줄
        if wave > 0.6:
            out.append(flat(capsule(hand[0] - 2.4, hand[1] + j * 1.3, hand[0] - 3.3, hand[1] + j * 1.8, 0.22), OUT, 0.8))
    return out


def sc_pin(fr):
    """작은 화살표 삼색냥 + 빨간 지도 핀 동그라미 속 삼색냥 얼굴 — 귀가 핀 위로 솟는다. 핀이 통통, 땅에 닿을 때 눈을 감음"""
    k = kof(fr)
    out = buddy(fr)
    hop = abs(sin(pi * fr))
    cx, cy = 23.4, 15.4 - 2.6 * hop
    out.insert(0, layer(ell(23.6, 29.0, 3.4 - 0.8 * hop, 0.75), lambda *a: (OUT, 0.2)))
    Fe = Frame(cx, cy - 0.7, 0.7)                             # 핀 뒤로 솟은 귀
    ears = [Fe.f(rpoly(ear_pts(sg), 0.95)) for sg in (-1, 1)]
    out.append(base(*ears))
    for sg, E in zip((-1, 1), ears):
        out.append(part(E, solid(ORNG if sg < 0 else BLK), shade=_Shade()))
        pts = ear_pts(sg)
        mx, my = sum(p[0] for p in pts) / 3, sum(p[1] for p in pts) / 3 + 0.5
        out.append(flat(Fe.f(rpoly([(mx + (x - mx) * 0.5, my + (y - my) * 0.5) for x, y in pts], 0.5)), CHEEK))
    f = smin(1.0, circle(cx, cy, 5.6), poly([(cx - 4.6, cy + 2.6), (cx + 4.6, cy + 2.6), (cx, cy + 11.4)]))
    out += [base(f), part(f, lambda x, y: lerp(SIGN_L, SIGN, smooth(cy - 5, cy - 1.5, y + 0.6 * (x - cx))), shade=SIGN_D, ink=SIGN_D)]
    Fh = Frame(cx, cy + 0.2, 0.55)
    H = head_f(Fh)
    out.append(part(H, COAT.fur("head", Fh), line=0.55, ink=SIGN_D))
    out += face(Fh, "blink" if k == 0 else "open")
    return out


def sc_wait(fr):
    """보라 담요 위 꾹꾹이 — 두 앞발을 번갈아 꾹 눌러 그 자리 담요가 꺼지고, 든 발은 젤리가 보인다. 눈은 ^^, 꼬리 끝 까딱"""
    ph = TAU * fr
    pl, pr = max(0.0, sin(ph)), max(0.0, -sin(ph))            # 왼발 · 오른발 누른 정도
    s = 0.86
    F = Frame(14.5, 11.5 + 0.25 * (pl + pr), s)
    tw = 0.8 * sin(2 * ph)
    hands = [(sg * 3.1, 8.4 + 3.0 * pd) for sg, pd in ((-1, pl), (1, pr))]
    by = 24.6
    dents = [F.w(*h) for h, pd in zip(hands, (pl, pr)) if pd > 0.5]

    def bcol(x, y):
        for dx, dy in dents:
            if hypot((x - dx) / 3.0, (y - by + 1.4) / 1.6) < 1:
                return BLANK_D
        if y < by - 1.2:
            return BLANK_L
        return BLANK if (x + 0.6 * y) % 3.4 < 2.2 else lerp(BLANK, BLANK_D, 0.6)
    bl = smin(0.8, ell(14.5, by, 13.2, 3.3), ell(14.5, by + 1.6, 12.0, 2.2))
    out = [base(bl), part(bl, bcol, shade=BLANK_D, ink=hx("5e4a84"))]
    for (dx, dy) in dents:                                   # 꾹 — 누른 발 양옆 주름
        for sg in (-1, 1):
            out.append(flat(arc(dx + sg * 2.9, by - 0.9, 1.0, 0.2, pi * (0.6 if sg < 0 else -0.4), pi * 0.8), hx("5e4a84"), 0.8))
    arms = [((sg * 2.8, 6.6), h, pd < 0.3) for sg, h, pd in zip((-1, 1), hands, (pl, pr))]
    out += cat(F, "happy", sway=0.0, paws=False, arms=arms,
               tail_pts=[(4.6, 10.4), (8.8, 10.2), (10.4, 7.2), (10.0 + 0.6 * tw, 3.8), (8.8 + tw, 2.0)])
    return out


def sc_hand(fr):
    """앉은 삼색냥이 앞발을 앞으로 쭉 내밀어 흰 발바닥(분홍 젤리)으로 톡톡 — 누를 때(장 3–5, 9–11) 몸이 앞으로 살짝
    쏠리고 눈은 ^^, 발 둘레에 톡 줄. 발은 안 움직이고 발끝(위)이 핫스팟.
    엎드린 식빵이 막대 같은 팔을 쭉 뻗던 판은 "너무 못생김"(2026-10-13)이라 앉은 몸 + 머리 위로 그리는 털 팔로 바꿈"""
    ph = TAU * fr
    k = kof(fr)
    tap = k % 6 in (3, 4, 5)
    lean = 0.5 if tap else 0.0
    s = 0.78
    F = Frame(17.2 - lean, 15.2 - lean * 0.4, s)
    hand = F.loc(6.4, 4.3)
    tp = [(3.6, 10.4), (7.8, 10.6), (9.9, 7.6), (9.4 + 0.6 * sin(ph), 3.9), (8.2 + 0.9 * sin(ph), 2.0)]
    out = cat(F, "happy" if tap else "open", look=(-0.8, -0.6), turn_=-0.5, tail_pts=tp,
              arms=[((-5.8, 3.6), hand, True)], ear_tilt=(-0.5, 0.0))
    if tap:                                               # 톡 — 발 둘레 눌림 줄(판 안에 드는 것만)
        for a in (pi, 2.4, -2.4, -0.7):
            ex, ey = 6.4 + 3.7 * cos(a), 4.3 + 3.7 * sin(a)
            if 1.0 < ex < 30.5 and 1.0 < ey < 30.5:
                c = capsule(ex, ey, ex + 1.2 * cos(a), ey + 1.2 * sin(a), 0.36)
                out += [base(c), flat(c, OUT)]
    return out


def sc_cross(fr):
    """앞모습 얼굴 — 볼 수염이 가로 조준선, 위로 늘어진 낚싯대 장난감 줄(끝 깃털이 까딱)과 턱 밑 줄이 세로선. 코가 핫스팟"""
    ph = TAU * fr
    k = kof(fr)
    C = 15.5
    s = 1.04
    F = Frame(C, C - 2.05 * s, s)
    lines = union(capsule(2.6, C, 5.0, C, 0.5), capsule(26.0, C, 28.4, C, 0.5), capsule(C, 23.6, C, 28.4, 0.5))
    out = [base(lines), flat(lines, OUT)]
    tw = 0.5 * sin(2 * ph)
    for sg in (-1, 1):                                    # 수염 — 조준선으로 이어진다
        for j in (-1, 1):
            out.append(flat(capsule(C + sg * 7.4, C + j * 0.55, C + sg * 10.6, C + j * (1.0 + 0.4 * tw), 0.22), OUT))
    out += cat(F, "blink" if k == 8 else "open", look=(0.25 * sin(ph), -0.6), body=False, paws=False, tail=False)
    sw = 0.7 * sin(ph)                                    # 낚싯대 줄 + 깃털(귀 사이로 까딱)
    fx, fy = C + sw, 4.6
    out += [base(capsule(C, 0.9, fx, fy - 1.2, 0.32)), flat(capsule(C, 0.9, fx, fy - 1.2, 0.32), OUT)]
    fe = turn(smin(0.4, ell(fx, fy + 0.6, 0.95, 1.7), circle(fx, fy - 0.8, 0.55)), -0.35 * sw, fx, fy - 1.0)
    out += [base(fe), part(fe, lambda x, y: ORNG if y < fy + 0.2 else CHEEK, shade=ORNG_D, sh=0.0, line=0.5)]
    return out


def sc_ibeam(fr):
    """스크래처 기둥(삼줄)이 I — 위 뚜껑 · 아래 받침이 가로획. 오른쪽에서 뒷발로 서서 기둥을 끌어안고 두 앞발을
    번갈아 박박: 한 발이 기둥 높이 박혀 죽 긁어내리는 동안 다른 발은 떼어 올린다. 긁고 지난 자리에 흰 자국"""
    k = kof(fr)
    ph = TAU * fr
    X = 6.5
    cap, foot = rbox(X, 3.1, 4.4, 1.15, 0.55), rbox(X, 28.0, 4.4, 1.15, 0.55)
    pole = rbox(X, 15.5, 1.9, 11.6, 0.3)
    strokes = []
    paws = []
    for i in range(2):
        t = (k / 6 + i / 2) % 1
        if t < 0.66:
            tip = (8.9, 11.0 + 9.0 * t / 0.66)
            strokes.append(tip[1])
        else:
            tip = (10.2, 20.0 - 9.0 * (t - 0.66) / 0.34)
        paws.append(((11.6, 14.6 + 2.0 * i), tip))

    def pcol(x, y):
        for y1 in strokes:
            if 11.0 < y < y1 and abs(x - X - 0.7) < 0.42:
                return SCRATCH
        return SISAL_D if (y + 0.55 * (x - X)) % 1.3 < 0.55 else SISAL
    out = [base(cap, foot, pole), part(pole, pcol, shade=SISAL_D, sh=0.5),
           part(cap, POST, shade=POST_D), part(foot, POST, shade=POST_D)]
    F = Frame(14.6, 10.0, 0.62)
    body = ell(14.8, 18.8, 3.9, 5.6)
    bcol = spots((oell(12.8, 16.0, 2.6, 2.2, -0.3), ORNG), (ell(17.2, 21.6, 2.2, 2.7), BLK))
    feet = [ell(13.2, 24.5, 1.85, 1.1), ell(16.5, 24.5, 1.85, 1.1)]
    tpts = [(18.0, 22.6), (21.6, 21.4), (22.6 + 0.3 * sin(2 * ph), 17.4 + sin(2 * ph))]
    tail = chain(tpts, 1.15, 1.0)
    out += cat(F, "happy" if k % 6 < 3 else "open", look=(-0.8, 0.2), turn_=-0.9, body=False, paws=False, tail=False,
               extra_under=[(tail, tail_col(tpts[-1], 1.8)), (body, bcol)] + [(f, solid(WHITE)) for f in feet])
    fs = []
    for (sh_, tip) in paws:
        fs.append((chain([sh_, tip], 1.55, 1.4), ell(tip[0], tip[1], 1.7, 1.5)))
    out.append(base(*[g for p in fs for g in p]))
    for i, (a, p) in enumerate(fs):
        out += [part(a, solid(ORNG if i == 0 else WHITE)), part(p, solid(WHITE))]
    return out


def sc_move(fr):
    """골판지 상자에 쏙 들어간 삼색냥이 상자째 좌우로 들썩들썩 — 네 방향 분홍 화살촉이 바깥으로 두근"""
    ph = TAU * fr
    k = kof(fr)
    o = 0.6 if k % 6 < 3 else 0.0
    out = []
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        out += chevron(15.5 + dx * (13.6 + o), 15.5 + dy * (13.6 + o), dx, dy, 2.2)
    hop = -0.9 * abs(sin(2 * ph))
    tilt = 0.1 * sin(2 * ph)
    B = Frame(15.5, 18.6 + hop, 1.0, tilt)
    out += box_cat(fr, B, tilt, 6.0, 6.2, 0.9, 1.0, 0.64, "blink" if k == 4 else "open")
    return out


NO_FLAP = [1.0, 1.0, 1.0, 0.6, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.8]
NO_PEEK = [0.8, 0.8, 0.8, 0.5, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.6]


def sc_no(fr):
    """빨간 금지 표지 안에서 상자에 든 삼색냥이 날개를 닫아 버린다 — 장 0–2 빼꼼 · 3–4 닫는 중 · 5–9 닫힘(귀 끝만)
    · 10–11 다시 빼꼼"""
    k = kof(fr)
    C = 14.5
    B = Frame(C, 17.6, 1.0)
    pk = NO_PEEK[k]
    out = box_cat(fr, B, 0.0, 5.4, 5.4, NO_FLAP[k], pk, 0.6, "open", paws=pk > 0.5)
    R = 12.5
    sg = union(ring(C, C, R - 1.25, 1.25), capsule(C - 7.7, C - 7.7, C + 7.7, C + 7.7, 1.35))
    out += [base(sg), part(sg, lambda x, y: lerp(SIGN_L, SIGN, smooth(C - 10, C - 4, y + 0.5 * x - 0.5 * C)), shade=SIGN_D, ink=SIGN_D, line=0.8)]
    return out


def sc_pen(fr):
    """붓을 두 앞발로 쥐고 먹 글씨 — 붓은 붓끝(왼쪽 아래)을 축으로 까딱, 붓끝 오른쪽으로 먹 줄이 물결치며 길어진다"""
    ph = TAU * fr
    k = kof(fr)
    tip = (1.55, 22.6)
    ang = -0.84 + 0.06 * sin(2 * ph)
    ux, uy = cos(ang), sin(ang)
    px, py = -uy, ux
    out = []
    n = 2 + k                                              # 먹 줄
    pts = [(2.6 + 1.25 * i, 25.0 + 0.55 * sin(1.2 * i)) for i in range(n + 1)]
    ink = chain(pts, 0.75, 0.5)
    out.append(flat(ink, INKC))
    at = lambda t, w=0.0: (tip[0] + ux * t + px * w, tip[1] + uy * t + py * w)   # noqa: E731
    hair = smin(0.35, poly([at(0.0), at(3.2, -1.15), at(3.2, 1.15)]), capsule(*at(2.4), *at(3.2), 1.15))
    ferrule = capsule(*at(3.5), *at(4.6), 1.0)
    stick = capsule(*at(4.6), *at(13.8), 0.78)
    out += [base(hair, ferrule, stick), part(stick, BRUSH, shade=BRUSH_D, ink=hx("5e4424"), line=0.8),
            part(ferrule, BRUSH_D, shade=hx("6e5028"), ink=hx("5e4424"), line=0.8), part(hair, INKC, shade=INKC, ink=INKC, line=0.0)]
    F = Frame(17.4, 10.4, 0.72)                            # 두 앞발로 붓대를 감싸 쥠 — 팔이 붓대 위로 온다
    hold = [F.loc(*at(10.4, 0.1)), F.loc(*at(12.6, 0.1))]
    out += cat(F, "blink" if k == 6 else "open", look=(-0.8, 0.6), turn_=-0.9, sway=0.5 * sin(ph), paws=False,
               arms=[((-4.6, 6.4), hold[0], False), ((-2.6, 7.4), hold[1], False)])
    return out


def sc_up(fr):
    """상자에서 쏙 일어서 주황 앞발을 머리 위로 번쩍 — "저요!". 다른 앞발은 상자 턱에, 상자 날개가 들썩, 꼬리는
    상자 뒤로 살랑, 가끔 깜빡. 든 발끝(맨 위)이 핫스팟이라 그 발은 안 움직이고 젤리가 보인다"""
    ph = TAU * fr
    k = kof(fr)
    s = 0.7
    F = Frame(13.6, 12.6, s)
    B = Frame(13.6, 20.6, 1.0)
    back, front = box(B, 7.2, 8.2, 0.8 + 0.2 * sin(2 * ph))
    tpts = [(18.6, 21.2), (22.2, 19.2 + sin(ph)), (23.0 + 0.5 * sin(ph), 15.2 + 0.4 * sin(ph))]
    tail = chain(tpts, 1.3, 1.1)
    out = back + [base(tail), part(tail, tail_col(tpts[-1], 2.0), shade=_Shade())]
    hand = F.loc(4.7, 3.55)
    out += cat(F, "blink" if k == 9 else "open", look=(-0.5, -0.8), paws=False, tail=False,
               arms=[((-6.2, 4.0), hand, True)], ear_tilt=(-0.6, 0.0))
    return out + front + rim_paws(B, (3.6,))


def loaf(fr, C_, ang, chev, s=0.6):
    """길쭉한 식빵 — 배를 깔고 엎드린 몸통이 ang 축으로 늘었다 줄었다, 머리는 앞 끝에 늘 똑바로, 발은 몸통 아래로
    뭉툭하게, 까만 꼬리는 뒤 끝에서 위로 말려 살랑. 양 끝 화살촉이 두근"""
    ph = TAU * fr
    k = kof(fr)
    sd = 1 if cos(ang) > -1e-6 else -1                      # 발 쪽이 화면 아래로 가게
    L = Frame(C_[0], C_[1], 1.0, ang)
    e = 5.4 + 1.3 * sin(ph)
    body = L.f(taper(-3.0, 0.0, 3.3, e, 0.0, 3.1))
    bcol = spots((L.f(oell(0.2, -sd * 2.1, 2.7, 1.7, 0.0)), ORNG), (L.f(ell(e - 1.2, sd * 1.4, 2.3, 2.3)), BLK))
    paws = [L.f(ell(u, sd * 2.9, 1.25, 0.95)) for u in (-1.9, 0.3, e - 2.1, e + 0.1)]
    tw = 0.8 * sin(2 * ph)
    tp = [(e + 0.9, -sd * 0.5), (e + 2.9, -sd * 1.4), (e + 3.4 + tw, -sd * 3.5)]
    tail = L.f(chain(tp, 1.1, 0.95))
    hx_, hy_ = L.w(-4.0, -sd * 0.4)
    out = cat(Frame(hx_, hy_ - 0.6, s), "happy" if k % 6 < 2 else "open", body=False, paws=False, tail=False,
              extra_under=[(tail, tail_col(L.w(*tp[-1]), 1.7)), (body, bcol)] + [(p, solid(WHITE)) for p in paws])
    o = 0.6 if sin(ph) > 0.3 else 0.0
    for (x, y, dx, dy) in chev:
        out += chevron(x + dx * o, y + dy * o, dx, dy, 2.2, 1.0 if o else 0.75)
    return out


def sc_we(fr):
    return loaf(fr, (14.4, 8.8), 0.0, [(1.9, 7.6, -1, 0), (29.1, 7.6, 1, 0)])


def sc_nwse(fr):
    return loaf(fr, (13.0, 14.2), pi / 4, [(3.4, 3.4, -1, -1), (27.6, 27.6, 1, 1)])


def sc_nesw(fr):
    return loaf(fr, (14.6, 13.6), 3 * pi / 4, [(27.6, 3.4, 1, -1), (3.4, 27.6, -1, 1)])


def sc_ns(fr):
    """막대에 두 앞발로 매달린 삼색냥 — 몸이 축 늘어졌다 줄었다, 뒷발 · 꼬리가 대롱대롱. 위아래 화살촉.
    앞발은 머리 바깥으로 올려 막대를 쥔다(머리 위 한가운데로 솟으면 토끼 귀가 된다)"""
    ph = TAU * fr
    k = kof(fr)
    X = 8.5
    bar = rbox(X, 5.0, 6.8, 0.8, 0.6)
    out = [base(bar), part(bar, BRUSH, shade=BRUSH_D, ink=hx("5e4424"), line=0.8)]
    F = Frame(X, 11.7, 0.62)
    e = 12.4 + 1.5 * sin(ph)
    sw = 0.7 * sin(2 * ph)
    under = []
    tp = [(1.2, e), (4.0 + sw, e + 2.4), (5.8 + 2 * sw, e + 0.2)]
    under.append((F.f(chain(tp, 1.6, 1.4)), tail_col(F.w(*tp[-1]), 1.8)))
    for sg in (-1, 1):
        under.append((F.f(chain([(sg * 2.4, e - 1.4), (sg * 2.7 + sw, e + 2.0)], 1.9, 1.7)), solid(WHITE)))
        under.append((F.f(ell(sg * 2.7 + sw, e + 2.6, 2.1, 1.7)), solid(WHITE)))
    for sg in (-1, 1):
        under.append((F.f(chain([(sg * 4.2, 4.2), (sg * 8.8, -1.6), (sg * 8.4, -9.0)], 2.3, 2.0)),
                      solid(ORNG if sg < 0 else WHITE)))
        under.append((F.f(ell(sg * 8.4, -9.8, 2.5, 2.2)), solid(WHITE)))
    body = F.f(taper(0.0, 3.4, 4.9, 0.0, e - 0.6, 4.4))
    under.append((body, spots((ell(-2.5, 5.8, 3.0, 2.8), ORNG), (ell(2.5, e - 2.6, 2.8, 3.2), BLK), loc=F.loc)))
    out += cat(F, "happy" if k % 6 < 2 else "open", look=(0.0, -0.5), body=False, paws=False, tail=False, extra_under=under)
    o = 0.6 if sin(ph) > 0.3 else 0.0
    out += chevron(X, 1.5 - o, 0, -1, 2.0, 1.0 if o else 0.75)
    out += chevron(X, 29.6 + o, 0, 1, 2.2, 1.0 if o else 0.75)
    return out


SCENE = {"busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "wait": sc_wait,
         "hand": sc_hand, "cross": sc_cross, "ibeam": sc_ibeam, "move": sc_move, "no": sc_no, "pen": sc_pen,
         "up": sc_up, "we": sc_we, "ns": sc_ns, "nwse": sc_nwse, "nesw": sc_nesw}


class CalicoCat(Pet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = CalicoCat(COAT, SCENE, HOT)


def scene(name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
    return PET.cell(name, frame, soft_, tip_body, shape)


register("calicocat", PET)

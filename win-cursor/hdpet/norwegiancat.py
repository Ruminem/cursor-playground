# SPDX-License-Identifier: Apache-2.0
"""노르웨이숲(norwegiancatanim) 고화질 — 흰냥이와 같은 치비 틀(catkit)에 장모 실루엣을 얹었다.

픽셀 노르웨이숲(gen/norwegiancat.py)이 고등어냥과 갈리는 까닭을 그대로 옮겼다 — 털 끝이 삐죽한 몸 · 볼 털,
가슴에만 두른 흰 갈기(목 뒤로 두르면 사자로 읽힌다), 귀 끝 검은 털(링크스 팁), 밑동은 가늘고 가운데가 부푼 깃털 꼬리.
갈색 고등어(이마 M · 볼 줄 · 옆구리 줄 · 꼬리 고리) 바탕에 털 끝은 밝은 갈색, 눈은 초록 섞인 금색, 신호색(화살촉)은 금색.
소품은 숲의 것 — 자작나무(흰 껍질 · 검은 무늬) · 솔방울 · 나뭇잎 · 솔잎 · 눈송이.

  arrow   크림 화살표 빗변 뒤에서 빼꼼, 앞발 둘이 빗변을 잡는다(catkit 빼꼼과 같은 자리, 냥이만 장모)
  busy    작은 화살표 노르웨이숲 + 까딱이는 솔방울 둘레를 맴도는 나뭇잎 여덟(앞장 초록, 뒤로 갈수록 흐린 주황)
  cross   자작나무를 끌어안고 내다보는 앞모습 — 긴 수염이 가로 조준선, 귀 사이 · 턱 밑 기둥이 세로선, 사냥 눈(동공이
          가늘었다 커진다). 코가 핫스팟
  hand    오른쪽 자작나무에 매달려 앞발 하나를 왼쪽 위로 쭉 — 발톱 끝이 핫스팟, 톡 칠 때 눌림 줄
  help    작은 화살표 노르웨이숲 + 잔가지로 휜 물음표(솔잎 두 다발), 점은 통통 튀는 솔방울
  ibeam   위는 솔잎 가지 · 아래는 뿌리인 자작나무 I — 등을 보인 노르웨이숲이 기둥을 끌어안고 오르락내리락
  move    그루터기 위에 앉아 위 · 오른쪽 · 아래 · 왼쪽을 차례로 두리번, 보는 쪽 금색 화살촉이 튀어나온다
  nesw · ns · nwse · we   그 축으로 뻗은 나뭇가지에 엎드려 앞발과 깃털 꼬리를 양 끝으로 쭉(ns 는 세로 가지에 매달림),
          늘었다 줄었다 하고 양 끝 금색 화살촉이 두근
  no      빨간 금지 표지 안에서 웅크려 깃털 꼬리로 얼굴을 덮는다 — 장 6–9 에 꼬리를 내려 눈만 빼꼼(옆눈질)
  pen     잔가지를 두 앞발로 쥐고 눈밭에 쓴다 — 가지 끝(왼쪽 아래)이 핫스팟, 파란 눈 고랑이 자란다
  person  작은 화살표 노르웨이숲 + 노르웨이숲을 목도리처럼 어깨에 두른 사람(얼굴은 오른 어깨, 꼬리는 왼쪽으로 흔들)
  pin     작은 화살표 노르웨이숲 + 흰 전나무가 든 빨간 지도 핀이 통통
  up      앉아서 깃털 꼬리를 깃대처럼 곧게 세운다 — 꼬리 끝(맨 위)이 핫스팟이라 끝은 그대로, 가운데만 살랑
  wait    눈 오는 날 깃털 꼬리로 몸을 휘감고 존다 — 숨에 몸이 부풀고 꼬리 끝 까딱, 눈송이 넷이 떨어진다

좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 장면은 NF 장으로 나뉘어 있다(k = round(fr × NF) % NF).
catkit.cat() 의 몸 · 꼬리 · 앞발은 끄고 장모 조각을 extra_under 로 넣는다(ncat) — 바닥 실루엣에 같이 들어가 먹선이 한 벌이다.
"""
from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

from . import catkit, register
from .catkit import *  # noqa: F401,F403
from .catkit import _edge

rad = math.radians

# 픽셀 판 팔레트(gen/norwegiancat.py) — 그늘 · 밝은 끝만 HD 에 맞게 더했다
OUT, EYE = hx("3a2a22"), hx("221812")
FUR, FUR_T, FUR_S = hx("a67a4e"), hx("cfa676"), hx("86603e")         # 갈색 · 밝은 털 끝 · 그늘
TABBY, TABBY_D = hx("765234"), hx("5e412a")                          # 고등어 줄 · 짙은 끝(꼬리 끝 · 귀 끝 털)
RUFF, RUFF_S = hx("f7f0e4"), hx("e2d4bc")                            # 흰 갈기 · 주둥이
IRIS, IRIS_D, IRIS_L = hx("b4c442"), hx("74841c"), hx("e4ee9c")      # 초록 섞인 금색 눈
NOSE, CHEEK, RIM = hx("e27d90"), hx("f7a3b5"), hx("fbecdc")
GOLD, GOLD_D, GOLD_L = hx("e8b23a"), hx("b07e1a"), hx("f8dc8a")      # 신호색(화살촉)
BIRCH, BIRCH_D, BIRCH_M = hx("f2eee6"), hx("d4ccc0"), hx("3a3430")   # 자작나무 껍질 · 그늘 · 검은 무늬
BARK, BARK_D, BARK_L = hx("7a5a44"), hx("54402f"), hx("9a7a5e")      # 잔가지 · 그루터기
CONE, CONE_D, CONE_L = hx("9a5a32"), hx("6a3c22"), hx("c8844a")      # 솔방울
NEEDLE, NEEDLE_D = hx("4f9a52"), hx("2f6a3c")                         # 솔잎
LEAF_G, LEAF_GD, LEAF_O, LEAF_OD = hx("6cb04a"), hx("3e7a2c"), hx("e8a03a"), hx("b06e1e")
SNOW, SNOW_D, SNOW_L = hx("9cc8ec"), hx("6c9cc8"), hx("dcefff")      # 눈송이 · 눈 고랑
SKIN, SKIN_D, HAIR, HAIR_D = hx("f7d7bc"), hx("e8bfa0"), hx("e0b04a"), hx("b08428")
COATP, COATP_D = hx("3e7fa0"), hx("2a5a74")                           # 사람 옷(갈색 냥이와 갈리게 파랑)
SIGN, SIGN_D, SIGN_L = hx("d64541"), hx("9e2b28"), hx("ef7a72")
RING = FUR_S                                                          # 꼬리 고리 — 장모라 줄이 흐리다(원본 RING)
RING_W = hx("d8b88a")                                                 # 그루터기 나이테


class NorwegianCoat(Coat):
    """갈색 고등어 — 이마 M · 볼 줄 · 흰 주둥이, 귀 끝은 짙게, 발은 밝은 털 끝"""

    def fur(self, part, F=None, turn_=0.0):
        if part in ("paw", "hand", "front", "back"):
            return FUR_T
        if F is None or part not in ("head", "ear", "arm"):
            return self.base
        if part == "ear":
            return lambda x, y: TABBY_D if F.loc(x, y)[1] < -6.9 else FUR
        if part == "arm":
            return FUR

        def head(x, y):
            u, v = F.loc(x, y)
            m = u - turn_
            if (m / 3.0) ** 2 + ((v - 3.1) / 1.85) ** 2 <= 1:          # 흰 주둥이
                return RUFF
            if -5.7 < v < -2.9:                                        # 이마 M — 가운데 하나 길게, 양옆은 바깥으로 기운 둘
                if abs(m) < 0.5 and v < -3.3:
                    return TABBY
                for sg in (-1, 1):
                    if abs(m - sg * (1.9 + 0.35 * (v + 4.3))) < 0.5:
                        return TABBY
            if abs(m) > 5.2 and any(abs(v - c - 0.08 * abs(m)) < 0.42 for c in (0.2, 1.7)):   # 볼 줄 둘
                return TABBY
            if v > 2.6 and abs(m) > 4.6:                               # 볼 털 끝은 밝게
                return FUR_T
            return FUR
        return head


COAT = NorwegianCoat(FUR, FUR_S, OUT, EYE, RIM, ((IRIS, IRIS_D, IRIS_L), (IRIS, IRIS_D, IRIS_L)), cheek=CHEEK, nose=NOSE)

# 픽셀 판 핫스팟(art/norwegiancatanim/*.txt 머리) 그대로 — 적용한 사람의 손에 익은 자리
HOT = {"arrow": (1, 1), "busy": (1, 1), "cross": (15, 15), "hand": (4, 4), "help": (1, 1), "ibeam": (10, 15),
       "move": (15, 15), "nesw": (15, 15), "no": (15, 15), "ns": (6, 15), "nwse": (15, 15), "pen": (1, 27),
       "person": (1, 1), "pin": (1, 1), "up": (15, 1), "wait": (14, 16), "we": (15, 9)}


def k_of(fr):
    return round(fr * NF) % NF


# ---- 장모 조각 (캐논 좌표 — 머리 가운데 (0, 0), 아래가 +v) ----

def tufts(cx, cy, rx, ry, degs, L, w, drift=(0.0, 0.0)):
    """타원 둘레 degs(도, 0 이 오른쪽 · 90 이 아래) 자리에서 바깥으로 솟는 털 뭉치들 — 끝이 가는 콘.
    drift 는 끝을 한쪽으로 눕히는 털 결"""
    out = []
    for d in degs:
        a = rad(d)
        ca, sa = cos(a), sin(a)
        nx, ny = ca / rx, sa / ry
        n = hypot(nx, ny)
        nx, ny = nx / n, ny / n
        px, py = cx + rx * ca, cy + ry * sa
        out.append(taper(px - nx * w * 0.8, py - ny * w * 0.8, w, px + nx * L + drift[0], py + ny * L + drift[1], w * 0.22))
    return out


def fluffy(cx, cy, rx, ry, degs, L=1.9, w=1.25, drift=(0.0, 0.0)):
    return union(ell(cx, cy, rx, ry), *tufts(cx, cy, rx, ry, degs, L, w, drift))


def near(pts):
    """꺾은선 → (u, v) 에서 (거리, 처음부터의 길이), 전체 길이"""
    segs, acc = [], 0.0
    for p, q in zip(pts, pts[1:]):
        L = hypot(q[0] - p[0], q[1] - p[1]) or 1e-9
        segs.append((p[0], p[1], q[0] - p[0], q[1] - p[1], L, acc))
        acc += L

    def at(u, v):
        best = (1e9, 0.0)
        for ax, ay, ex, ey, L, s0 in segs:
            t = clamp(((u - ax) * ex + (v - ay) * ey) / (L * L))
            d = hypot(u - ax - ex * t, v - ay - ey * t)
            if d < best[0]:
                best = (d, s0 + L * t)
        return best
    return at, acc


PROF = ((0.0, 1.5), (0.3, 3.0), (0.78, 2.8), (1.0, 1.9))


SAW_A, SAW_P = 0.85, 2.0                                              # 톱니 높이 · 간격(캐논)


def saw(t, n):
    """0–1 구간을 n 개 톱니로 — t 쪽으로 차오르다 뚝 떨어진다(털이 그쪽으로 눕는다). 양 끝 톱니는 낮춘다"""
    if not 0.0 < t < 1.0:
        return 0.0
    return ((t * n) % 1.0) * clamp(min(t, 1.0 - t) * n * 1.2)


def plume_f(pts, prof=PROF, fluff=True):
    """깃털 꼬리 거리함수(캐논) — 밑동은 가늘고 가운데가 부풀며, 가장자리는 끝 쪽으로 누운 톱니(원본 `fluff`),
    끝에도 한 뭉치. 콘을 양옆에 박던 판은 먹선이 콘마다 둘러져 지네 다리로 읽혀 바꿨다"""
    at, total = near(pts)

    def r_at(t):
        for (t0, r0), (t1, r1) in zip(prof, prof[1:]):
            if t <= t1:
                return r0 + (r1 - r0) * clamp((t - t0) / ((t1 - t0) or 1e-9))
        return prof[-1][1]
    s0 = total * 0.22
    n = max(1, round((total - s0) / SAW_P))

    def f(u, v):
        d, s = at(u, v)
        r = r_at(s / total)
        if fluff:
            r += SAW_A * saw((s - s0) / (total - s0), n)
        return d - r
    fs = [f]
    if fluff:
        (ax, ay), (bx, by) = pts[-2], pts[-1]                        # 끝 뭉치
        L = hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / L, (by - ay) / L
        re = prof[-1][1]
        fs.append(taper(bx, by, re * 0.8, bx + ux * (re + 1.2), by + uy * (re + 1.2), 0.45))
    return union(*fs), at, total, r_at


def plume(F, pts, prof=PROF, fluff=True):
    """깃털 꼬리 → (art 거리함수, 색). 짙은 고리 · 짙은 끝 · 가장자리 밝은 털 끝"""
    f, at, total, r_at = plume_f(pts, prof, fluff)

    def col(x, y):
        u, v = F.loc(x, y)
        d, s = at(u, v)
        if s > total - 1.4:
            return TABBY_D
        if d > r_at(s / total) * 0.8:
            return FUR_T
        return RING if 2.0 < s < total - 3.0 and (s % 4.4) > 3.4 else FUR
    return F.f(f), col


def shag(cx, cy, rx, ry, arcs, A=SAW_A):
    """가장자리가 톱니인 타원(캐논). arcs = [(시작 각, 끝 각, 톱니 수)] — 도, 0 이 오른쪽 · 90 이 아래.
    톱니는 끝 각 쪽으로 눕는다(끝 각이 작으면 거꾸로 돈다)"""
    e0 = ell(cx, cy, rx, ry)

    def f(u, v):
        d = e0(u, v)
        th = math.degrees(math.atan2((v - cy) / ry, (u - cx) / rx))
        for a0, a1, n in arcs:
            span = a1 - a0
            t = ((th - a0) % 360.0) / span if span > 0 else ((a0 - th) % 360.0) / -span
            if t < 1.0:
                return d - A * saw(t, n)
        return d
    return f


def body_col(F, cx, cy, rx, ry, stripes=True):
    def col(x, y):
        u, v = F.loc(x, y)
        if ((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2 > 0.82:
            return FUR_T
        if stripes and abs(u - cx) > rx * 0.42 and (v + 0.6) % 3.4 < 1.15:
            return TABBY
        return FUR
    return col


def ruff_f(cv=6.1, rx=3.9, ry=2.6):
    """가슴에만 두른 흰 갈기 — 아래 가장자리가 삐죽(목 뒤로는 안 두른다)"""
    return fluffy(0.0, cv, rx, ry, (40, 63, 90, 117, 140), 1.7, 1.05)


def ear_tufts(tilt=(0.0, 0.0)):
    """귀 끝 검은 털(링크스 팁) — 귀 끝에서 위로 가늘게"""
    return union(*[taper(sg * (6.0 + tilt[(sg + 1) // 2]), -7.4, 0.8, sg * (6.15 + tilt[(sg + 1) // 2]), -10.7, 0.26)
                   for sg in (-1, 1)])


def cheek_tufts():
    """볼 아래 양옆으로 비어져 나온 털 — 장모 얼굴의 볼 갈기"""
    return union(*tufts(0.0, 1.3, 7.6, 4.3, (12, 34, 146, 168), 1.9, 1.25, (0.0, 0.7)))


def ncat(F, mood="open", look=(0.0, 0.0), turn_=0.0, sway=0.0, breath=0.0, body=True, paws=True, tail=True,
         arms=(), tongue=0.0, ear_tilt=(0.0, 0.0), tail_pts=None, tail_prof=PROF, tail_front=False, ruff=True,
         face_on=True, mouth="w", back=False, paws_at=None, bob=0.0, extra=()):
    """장모 치비 냥 → 레이어 목록. catkit.cat 의 머리 · 귀 · 얼굴 · 팔을 쓰고 몸 · 꼬리 · 발 · 갈기 · 볼 털 · 귀 끝 털은
    여기 조각으로 넣는다(extra_under — 바닥 실루엣에 같이 들어가 먹선이 한 벌). tail_front 면 꼬리가 몸 · 발 앞(휘감기).
    back 이면 뒤통수(얼굴 · 귀 속 없이 정수리에서 목덜미로 짙은 줄 셋)"""
    pieces = []                                                   # (art 거리함수, 색, part 옵션)
    tl = None
    if tail:
        tp = tail_pts or [(3.6, 10.2), (7.8, 10.4), (9.9, 7.4), (9.4 + sway, 3.7), (8.2 + 1.4 * sway, 1.6)]
        tl = (*plume(F, tp, tail_prof), {})
        if not tail_front:
            pieces.append(tl)
    if body:
        cx, cy, rx, ry = 0.0, 7.6 + bob * 0.3, 5.5 + breath * 0.35, 4.5 + breath * 0.2
        pieces.append((F.f(shag(cx, cy, rx, ry, ((-35, 75, 4), (215, 105, 4)))),
                       body_col(F, cx, cy, rx, ry), {}))
    if ruff:
        pieces.append((F.f(ruff_f()), RUFF, {"shade": RUFF_S}))
    if paws:
        for u, v, a, b in (paws_at or [(-2.45, 11.35, 1.95, 1.4), (2.45, 11.35, 1.95, 1.4)]):
            pieces.append((F.f(ell(u, v, a, b)), FUR_T, {}))
    if tl and tail_front:
        pieces.append(tl)
    pieces += [(F.f(g), col, {}) for g, col in extra]               # 머리 밑에 깔리는 조각(뒤모습 앞발 등)
    pieces.append((F.f(cheek_tufts()), FUR_T, {}))
    pieces.append((F.f(ear_tufts(ear_tilt)), TABBY_D, {"sh": 0.0}))
    out = cat(F, mood, look, turn_, 0.0, bob, body=False, paws=False, tail=False, arms=arms, tongue=tongue,
              ear_tilt=ear_tilt, extra_under=[p[:2] for p in pieces], face_on=face_on and not back, mouth=mouth)
    for i, (f, col, opt) in enumerate(pieces):
        if opt:
            out[1 + i] = part(f, col, **opt)
    if back:                                                      # 뒤통수: 귀 속 분홍을 빼고 머리를 줄무늬로
        j = 1 + len(pieces)
        H = head_f(F, bob * 0.35)

        def bcol(x, y):
            u, v = F.loc(x, y)
            if v < 3.6 and any(abs(u - d * 2.3 - 0.05 * d * v) < 0.62 for d in (-1, 0, 1)):
                return TABBY
            return FUR_T if v > 3.4 and abs(u) > 4.4 else FUR
        out[j + 4] = part(H, bcol)
        del out[j + 3], out[j + 1]
    return out


# ---- 화살표: 빼꼼 (catkit.peek 과 같은 자리 · 같은 셈, 냥이만 장모) ----

def _peek_cat(F, fr):
    ph = TAU * fr
    tp = [(3.0, 9.6), (7.4, 10.4), (9.6, 7.4), (9.4 + 0.6 * sin(ph), 3.6), (8.0 + 0.9 * sin(ph), 1.6)]
    return ncat(F, "blink" if blink_of(fr) else "open", look=(-0.6, 0.25), sway=0.6 * sin(ph), paws=False, tail_pts=tp,
                tail_prof=((0.0, 1.4), (0.3, 2.6), (0.78, 2.5), (1.0, 1.7)))


def npeek(fr):
    ph = TAU * fr
    sc = 1.24
    P = [(TIP[0] + sc * x, TIP[1] + sc * y) for x, y in ARROW]
    arw = rpoly(P, 0.55)
    lift = 0.5 * (1 - cos(ph)) / 2
    out = _peek_cat(Frame(19.6, 10.4 - lift + 0.5, 0.8), fr)
    out += cur([base(arw), part(arw, cream_of, sh=0.0)])
    ex, ey = P[6][0] - P[0][0], P[6][1] - P[0][1]
    el = hypot(ex, ey)
    ux, uy = ex / el, ey / el
    for t in (15.6, 18.9):
        out += paw(P[0][0] + ux * t + uy * 0.55, P[0][1] + uy * t - ux * 0.55, ux, uy)
    return out


def npeek_shape(fr, shape):
    g = shaped(shape)
    ph = TAU * fr
    cx, cy = g["cat"]
    lift = 0.5 * (1 - cos(ph)) / 2
    out = _peek_cat(Frame(cx, cy - lift + 1.3, 0.8), fr)
    if g["band"]:
        out += cur([base(g["outer"]), part(g["outer"], HI_WHITE, sh=0.0), part(g["body"], cream_of, line=0.0)])
    else:
        out += cur([base(g["body"]), part(g["body"], cream_of)])
    for s in (0.659, 0.798):
        out += paw(*_edge(g, s, 0.6), *g["u"])
    return out


def nbuddy(fr, mood=None):
    """작은 화살표 + 작은 노르웨이숲(catkit.buddy 자리 그대로)"""
    ph = TAU * fr
    m = mood or ("blink" if blink_of(fr, 0.25) else "open")
    F = Frame(13.6, 8.1, 0.56)
    return small_arrow() + ncat(F, m, look=(-0.4, 0.0), sway=0.5 * sin(ph), bob=0.4 * (1 - cos(ph)) / 2)


# ---- 소품 ----

def gold_chevron(cx, cy, dx, dy, L=2.4, a=1.0):
    """(dx, dy) 쪽을 가리키는 금색 화살촉 — 꼭짓점이 (cx, cy)"""
    n = hypot(dx, dy)
    dx, dy = dx / n, dy / n
    px, py = -dy, dx
    f = union(*[capsule(cx, cy, cx - dx * L + s * px * L, cy - dy * L + s * py * L, 0.72) for s in (-1, 1)])
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(GOLD_L, GOLD, smooth(0.6, 0.3, -e)) if -e > 0.3 else GOLD_D, 1.0),
                  alpha=a)]


BIRCH_MARKS = ((1, 0.3, 0.55), (4, -0.5, 0.35), (6.5, 0.6, 0.45), (10, -0.2, 0.6), (13, 0.5, 0.3), (15.5, -0.6, 0.5),
               (19, 0.2, 0.4), (22, -0.4, 0.55), (25.5, 0.5, 0.35), (28.5, -0.3, 0.5))


def birch(cx, y0, y1, hw=2.6, seed=0.0):
    """세로 자작나무 기둥 — 흰 껍질, 오른쪽 그늘, 가로로 짧은 검은 무늬(길이 · 자리를 들쭉날쭉)"""
    f = rbox(cx, (y0 + y1) / 2, hw, (y1 - y0) / 2, 0.7)
    out = [base(f), part(f, BIRCH, shade=BIRCH_D, sh=1.0)]
    for i, (y, off, ln) in enumerate(BIRCH_MARKS):
        yy = y0 + ((y + seed * 3.7) % (y1 - y0 - 1.6)) + 0.8
        x = cx + off * hw * 0.8
        w = ln * hw
        out.append(flat(capsule(x - w, yy, x + w, yy + 0.15 * (1 if i % 2 else -1), 0.42), BIRCH_M))
    return out


def cone(cx, cy, rx=2.3, ry=3.0, tilt=0.0):
    """솔방울 — 짙은 테 안에 엇갈린 비늘, 위에 짧은 꼭지. tilt 는 꼭지 쪽을 축으로 까딱"""
    T = lambda g: turn(g, tilt, cx, cy - ry)
    f = T(smin(0.6, ell(cx, cy + 0.3, rx, ry), ell(cx, cy - ry * 0.5, rx * 0.7, ry * 0.5)))
    stem = T(capsule(cx, cy - ry - 0.2, cx + 0.3, cy - ry - 1.3, 0.42))
    c, s_ = cos(-tilt), sin(-tilt)

    def col(x, y):
        lx, ly = (x - cx) * c - (y - cy) * s_, (x - cx) * s_ + (y - cy) * c
        a, b = floor((lx * 0.8 + ly * 0.65) / 1.3), floor((-lx * 0.8 + ly * 0.65) / 1.3)
        return CONE_L if (a + b) % 2 == 0 else CONE
    return [base(f, stem), part(stem, BARK_D, sh=0.0), part(f, col, shade=CONE_D, ink=CONE_D)]


def leaf(cx, cy, ang, L=1.9, green=True, a=1.0):
    """나뭇잎 하나 — 끝이 뾰족한 잎몸 + 가운데 잎맥"""
    col, ink = (LEAF_G, LEAF_GD) if green else (LEAF_O, LEAF_OD)
    ux, uy = cos(ang), sin(ang)
    f = smin(0.2, oell(cx, cy, L, L * 0.5, ang), poly([(cx + ux * L * 1.45, cy + uy * L * 1.45),
                                                       (cx + ux * L * 0.5 - uy * 0.6, cy + uy * L * 0.5 + ux * 0.6),
                                                       (cx + ux * L * 0.5 + uy * 0.6, cy + uy * L * 0.5 - ux * 0.6)]))
    vein = capsule(cx - ux * L * 1.3, cy - uy * L * 1.3, cx + ux * L * 0.9, cy + uy * L * 0.9, 0.2)
    return [layer(f, lambda x, y, e, nx, ny, fr: (lerp(col, ink, smooth(0.5, 0.3, -e)), 1.0), alpha=a),
            layer(vein, lambda x, y, e, nx, ny, fr: (ink, 1.0), alpha=a * 0.9)]


def needles(cx, cy, ang, L=2.4, n=4, spread=0.5):
    """솔잎 다발 — ang 쪽으로 부채꼴로 뻗은 가는 잎"""
    fs = [capsule(cx, cy, cx + L * cos(ang + spread * (i / (n - 1) - 0.5) * 2), cy + L * sin(ang + spread * (i / (n - 1) - 0.5) * 2), 0.42)
          for i in range(n)]
    f = union(*fs)
    return [base(f), part(f, NEEDLE, shade=NEEDLE_D, ink=NEEDLE_D, line=0.45, sh=0.0)]


def flake(cx, cy, r=1.5, a=1.0):
    """눈송이 — 여섯 갈래"""
    f = union(*[capsule(cx - r * cos(t), cy - r * sin(t), cx + r * cos(t), cy + r * sin(t), 0.36)
                for t in (pi / 2, pi / 6, -pi / 6)], circle(cx, cy, 0.62))
    return [layer(grow(f, 0.35), lambda *_: (SNOW_D, 1.0), alpha=a),
            layer(f, lambda x, y, e, nx, ny, fr: (lerp(SNOW_L, SNOW, smooth(0.0, r, hypot(x - cx, y - cy))), 1.0), alpha=a)]


def twig_layers(f, ink=BARK_D):
    def col(x, y):
        return BARK_D if (x - y * 0.7) % 3.4 < 0.5 else BARK
    return [base(f), part(f, col, shade=BARK_D, ink=ink, line=0.8)]


# ---- 장면 ----

def sc_wait(fr):
    """눈 오는 날 깃털 꼬리로 몸을 휘감고 존다 — 숨에 몸이 부풀고 꼬리 끝 까딱, 눈송이 넷이 한 바퀴에 판을 한 번 내려간다.
    장 9–10 에 한쪽 눈을 살짝 떴다 감는다. 가운데(가슴 갈기)가 핫스팟"""
    ph = TAU * fr
    k = k_of(fr)
    out = []
    for i, (x0, y0) in enumerate(((3.6, 3.0), (27.6, 9.0), (4.6, 20.0), (27.2, 25.0))):
        y = (y0 + 32 * k / NF) % 32
        x = x0 + 0.6 * sin(ph * 2 + i * 1.7)
        out += flake(x, y, 1.45)
    br = sin(ph)
    tw = 0.9 * sin(2 * ph)
    F = Frame(14.8, 11.4, 0.8)
    tp = [(5.2, 8.4), (4.2, 11.6), (0.0, 12.8), (-4.6, 12.2), (-8.0, 9.6), (-8.8 + 0.4 * tw, 6.6 + tw)]
    out += ncat(F, "wink" if k in (9, 10) else "blink", look=(0.4, 0.0), breath=br, tail_pts=tp, tail_front=True,
                tail_prof=((0.0, 1.6), (0.3, 2.6), (0.8, 2.5), (1.0, 1.8)), mouth="")
    return out


def sc_up(fr):
    """앉아서 깃털 꼬리를 깃대처럼 곧게 세운다 — 꼬리 끝(맨 위)이 핫스팟이라 끝은 그대로, 가운데만 살랑이며 털 끝이 나부낀다.
    고개를 들어 제 꼬리 끝을 올려다본다"""
    ph = TAU * fr
    k = k_of(fr)
    F = Frame(10.2, 19.4, 0.66)
    sw = sin(ph)
    top = F.loc(15.5, 5.5)
    tp = [(4.6, 9.0), (8.2, 6.4), (9.6 + 0.9 * sw, -1.0), (top[0] - 0.4 - 0.8 * sw, -9.5), top]
    return ncat(F, "blink" if k == 5 else "open", look=(0.45, -0.9), turn_=0.8, tail_pts=tp,
                tail_prof=((0.0, 1.5), (0.22, 3.0), (0.8, 3.2), (1.0, 2.1)), ear_tilt=(0.0, 0.3 * sw))


def sc_pen(fr):
    """잔가지를 두 앞발로 쥐고 눈밭에 쓴다 — 가지 끝(왼쪽 아래)이 핫스팟, 지나간 자리에 파란 눈 고랑이 물결로 자란다"""
    ph = TAU * fr
    k = k_of(fr)
    tip = (1.75, 27.6)
    ang = -0.62 + 0.06 * sin(2 * ph)
    ux, uy = cos(ang), sin(ang)
    end = (tip[0] + ux * 15.0, tip[1] + uy * 15.0)
    out = []
    pts = [(3.4 + 0.9 * i, 29.4 + 0.55 * sin(0.9 * i)) for i in range(2 + 2 * k)]
    if len(pts) > 1:
        g = union(*[capsule(*a, *b, 0.62) for a, b in zip(pts, pts[1:])])
        out += [layer(g, lambda x, y, e, nx, ny, fr_: (lerp(SNOW, SNOW_D, smooth(0.3, 0.1, -e)), 1.0))]
    F = Frame(21.4, 11.4, 0.68)
    out += ncat(F, "wink" if k == 6 else "open", look=(-0.8, 0.6), turn_=-1.0, sway=0.5 * sin(ph),
                tail_pts=[(3.6, 10.2), (7.8, 10.4), (9.9, 7.4), (9.4 + 0.7 * sin(ph), 3.7), (8.2 + 1.2 * sin(ph), 1.6)])
    f = smin(0.4, capsule(tip[0], tip[1], end[0], end[1], 0.85),
             capsule(tip[0] + ux * 10.5, tip[1] + uy * 10.5, tip[0] + ux * 11.5 - uy * 2.4, tip[1] + uy * 11.5 + ux * 2.4, 0.5))
    out += twig_layers(f)
    out += needles(tip[0] + ux * 11.5 - uy * 2.4, tip[1] + uy * 11.5 + ux * 2.4, ang - 1.2, 1.9, 3, 0.6)
    for t in (8.6, 11.8):                                         # 가지를 감싼 앞발
        p = ell(tip[0] + ux * t, tip[1] + uy * t - 0.3, 1.9, 1.7)
        out += [base(p), part(p, FUR_T)]
    return out


def sc_hand(fr):
    """오른쪽 자작나무에 매달려 앞발 하나를 왼쪽 위로 쭉 — 발톱 끝(4, 4)이 핫스팟. 톡 칠 때(장 2–3 · 8–9) 발톱 둘레에
    눌림 줄이 튀고 깃털 꼬리가 아래로 늘어져 살랑"""
    ph = TAU * fr
    k = k_of(fr)
    tap = k in (2, 3, 8, 9)
    out = birch(28.0, 0.6, 31.4, 2.3, seed=1.0)
    F = Frame(18.2, 13.4, 0.66)
    sw = sin(ph)
    reach = 0.5 if tap else 0.0
    hand = F.loc(7.6 - reach, 7.6 - reach)
    grip = F.loc(25.0, 16.4)
    for p in (ell(25.4, 25.2, 1.9, 1.5), ell(25.6, 28.4, 1.9, 1.5)):   # 기둥을 짚은 뒷발
        out += [base(p), part(p, FUR_T)]
    out += ncat(F, "open", look=(-0.8, -0.6), turn_=-0.9, tail_pts=[(2.0, 10.2), (3.4, 14.2), (2.0 + 1.2 * sw, 18.0), (3.0 + 2.0 * sw, 22.0)],
                tail_prof=((0.0, 1.4), (0.35, 2.6), (0.8, 2.4), (1.0, 1.7)), paws=False,
                arms=[((-6.4, 5.6), hand, True), ((4.6, 5.6), grip, False)], ear_tilt=(-0.6, 0.0))
    tx, ty = 4.6, 4.6
    hx_, hy_ = F.w(*hand)
    for d in (-1, 0, 1):                                          # 발톱 셋 — 가운데 끝이 핫스팟
        ox, oy = d * 0.95, -d * 0.95
        sx, sy = hx_ - 1.25 + ox * 0.6, hy_ - 1.25 + oy * 0.6
        ex_, ey_ = tx + ox - reach, ty + oy - reach
        if d:
            ex_, ey_ = ex_ + 0.6, ey_ + 0.6
        f = taper(sx, sy, 0.55, ex_, ey_, 0.22)
        out += [base(f), part(f, RUFF, shade=RUFF_S, line=0.5, sh=0.0)]
    if tap:
        for a in (pi * 1.0, pi * 1.25, pi * 1.5):
            c, s_ = cos(a), sin(a)
            g = capsule(tx - reach + c * 2.6, ty - reach + s_ * 2.6, tx - reach + c * 3.8, ty - reach + s_ * 3.8, 0.4)
            out.append(flat(g, OUT))
    return out


def sc_cross(fr):
    """자작나무를 끌어안고 내다보는 앞모습 — 긴 수염이 가로 조준선, 귀 사이 · 턱 밑 기둥이 세로선. 사냥 눈: 동공이 장 0–3 에
    가늘다가 4–9 에 둥글게 커진다. 장 6–7 에 고개를 살짝 갸웃. 코(15, 15)가 핫스팟"""
    k = k_of(fr)
    Cx = 15.5
    s = 0.96
    tw = 0.5 if k in (6, 7) else 0.0
    F = Frame(Cx, Cx - 2.05 * s, s)
    out = birch(Cx, 0.8, 31.2, 2.5, seed=2.0)
    lines = union(capsule(1.8, Cx, 6.0, Cx, 0.5), capsule(25.0, Cx, 29.2, Cx, 0.5))
    out += [base(lines), flat(lines, OUT)]
    for sg in (-1, 1):                                            # 아래로 비스듬한 짧은 수염
        out.append(flat(capsule(Cx + sg * 7.4, Cx + 1.4, Cx + sg * 10.8, Cx + 2.6, 0.26), OUT))
    out += ncat(F, "open", turn_=tw, body=False, tail=False, paws_at=[(-4.6, 7.6, 2.2, 1.7), (4.6, 7.6, 2.2, 1.7)],
                face_on=True)
    wide = 4 <= k <= 9
    er = max(1.66 * s, 1.32)
    for sg in (-1, 1):                                            # 사냥 눈 — 세로 동공을 다시 그린다
        ex, ey = F.w(tw + sg * 3.15, 0.25)
        out.append(slit_eye(ex, ey, er, 0.62 if wide else 0.24))
    return out


def slit_eye(cx, cy, rx, pw):
    """catkit.eye 와 같은 홍채 · 반짝에 동공만 가운데 세로 (pw = 동공 반폭 / 눈 반폭)"""
    ry = rx * 1.16
    h1 = (cx - rx * 0.36, cy - ry * 0.38, rx * 0.34)
    h2 = (cx + rx * 0.4, cy + ry * 0.42, rx * 0.14)

    def paint(x, y, e, nx, ny, fr):
        c = lerp(IRIS_L, IRIS, smooth(cy - ry * 0.9, cy - ry * 0.1, y))
        c = lerp(c, IRIS_D, 0.45 * smooth(cy + ry * 0.3, cy + ry * 1.0, y))
        c = lerp(c, EYE, smooth(0.12, -0.12, hypot((x - cx) / (rx * pw), (y - cy) / (ry * 0.86)) - 1))
        c = lerp(c, HI, smooth(h1[2] + 0.1, h1[2] - 0.1, hypot(x - h1[0], y - h1[1])))
        c = lerp(c, HI, 0.9 * smooth(h2[2] + 0.08, h2[2] - 0.08, hypot(x - h2[0], y - h2[1])))
        return lerp(c, IRIS_D, smooth(0.26, 0.1, -e)), 1.0
    return layer(ell(cx, cy, rx, ry), paint)


def sc_ibeam(fr):
    """위는 솔잎 가지 · 아래는 뿌리인 자작나무가 I — 등을 보인 노르웨이숲이 기둥을 끌어안고 오르락내리락(오를 때 앞발 위로).
    기둥 가운데(10, 15)가 핫스팟"""
    ph = TAU * fr
    X = 10.5
    out = []
    top = capsule(X - 7.0, 2.8, X + 7.0, 2.8, 1.35)
    roots = smin(0.8, poly([(X - 2.2, 26.0), (X + 2.2, 26.0), (X + 6.6, 30.4), (X - 6.6, 30.4)]),
                 rbox(X, 29.9, 6.4, 0.6, 0.5))
    for sg in (-1, 1):
        out += needles(X + sg * 7.0, 2.8, pi / 2 - sg * 0.9, 2.2, 3, 0.7)
        out += needles(X + sg * 7.0, 2.8, -pi / 2 + sg * 0.9, 2.0, 3, 0.6)
    out += twig_layers(top)
    out += birch(X, 3.0, 28.0, 2.3, seed=0.0)
    out += [base(roots), part(roots, BARK, shade=BARK_D, ink=BARK_D, line=0.8)]
    dy = 2.4 * sin(ph)
    climb = 0.9 * sin(ph)
    F = Frame(X, 9.6 + dy, 0.5)
    for sg in (-1, 1):                                            # 기둥 양옆을 짚은 뒷발
        p = F.f(ell(sg * 4.8, 12.2 - sg * climb, 2.1, 2.3))
        out += [base(p), part(p, FUR_T)]
    # 앞발은 머리 밑 조각으로 — catkit 팔은 머리 위에 그려져 뒤통수에 두 눈처럼 박힌다
    fronts = [(ell(sg * 7.6, -2.6 - sg * climb * 1.6, 2.4, 2.1), FUR_T) for sg in (-1, 1)]
    out += ncat(F, back=True, ruff=False, paws=False, tail_front=True,
                tail_pts=[(0.0, 10.0), (0.4, 14.6), (-0.6 + 0.7 * sin(2 * ph), 19.4)],
                tail_prof=((0.0, 1.6), (0.35, 2.7), (0.8, 2.5), (1.0, 1.8)), extra=fronts)
    return out


def sc_move(fr):
    """그루터기 위에 앉아 사방을 두리번 — 장 0–2 위, 3–5 오른쪽, 6–8 아래, 9–11 왼쪽을 본다(고개와 눈이 그쪽으로).
    보는 쪽 금색 화살촉이 한 칸 튀어나오고 나머지는 옅다. 깃털 꼬리가 앞발을 휘감는다"""
    k = k_of(fr)
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    d = dirs[k // 3]
    out = []
    for dd in dirs:
        on = dd == d
        out += gold_chevron(15.5 + dd[0] * (13.4 + (0.7 if on else 0.0)), 15.5 + dd[1] * (13.4 + (0.7 if on else 0.0)),
                            dd[0], dd[1], 2.2, 1.0 if on else 0.45)
    stump = smin(0.5, rbox(15.5, 25.6, 5.6, 2.2, 0.6), ell(15.5, 27.6, 6.4, 0.9))
    face_ = ell(15.5, 23.6, 5.4, 1.15)
    out += [base(stump), part(stump, lambda x, y: BARK_D if (x * 1.1) % 2.6 < 0.5 else BARK, shade=BARK_D, ink=BARK_D, line=0.8)]
    out.append(flat(face_, lambda x, y: RING_W if (hypot((x - 15.5) / 2.4, (y - 23.6) / 0.52) % 1.0) > 0.25 else BARK_L,
                    line=0.4, ink=BARK_D))
    F = Frame(15.5, 12.0 + (0.4 if d[1] > 0 else -0.2 if d[1] < 0 else 0.0), 0.6)
    out += ncat(F, "blink" if k == 7 else "open", look=d, turn_=d[0] * 1.3, tail_front=True,
                tail_pts=[(5.4, 8.6), (4.4, 12.0), (0.0, 13.0), (-4.6, 12.4), (-7.4, 10.0)],
                tail_prof=((0.0, 1.6), (0.3, 2.5), (0.8, 2.4), (1.0, 1.8)))
    return out


def lie(fr, C_, ang, length, s=0.6, chev=None, head=(0.0, -1.0), hoff=2.2, dangle=False, branch=(0.0, 0.0)):
    """나뭇가지에 엎드려 기지개(catkit.stretch 와 같은 셈) — 몸 아래쪽 털이 삐죽, 뒤 끝은 깃털 꼬리, 아래에 가지.
    branch 는 가지를 축 따라 앞 · 뒤로 얼마나 낼지(칸)"""
    ph = TAU * fr
    k = k_of(fr)
    e = length * (1 + 0.05 * sin(ph))
    ux, uy = cos(ang), sin(ang)
    cx, cy = C_
    r = 3.3 * s / 0.6
    a0 = (cx - ux * e / 2, cy - uy * e / 2)
    a1 = (cx + ux * e / 2, cy + uy * e / 2)
    px, py = (-head[0], -head[1]) if not dangle else (-uy, ux)
    out = []
    if dangle:                                                    # 세로 가지(기둥) — 몸 뒤로
        bf = capsule(cx, cy - length / 2 - branch[0], cx, cy + length / 2 + branch[1], 1.35)
    else:                                                         # 배 쪽 가지
        o = r * 0.85
        bf = capsule(a0[0] - ux * branch[0] + px * o, a0[1] - uy * branch[0] + py * o,
                     a1[0] + ux * branch[1] + px * o, a1[1] + uy * branch[1] + py * o, 1.25)
    out += twig_layers(bf)
    body0 = taper(a0[0], a0[1], r, a1[0], a1[1], r * 0.92)
    A = SAW_A * s / 0.6
    nt = max(2, round(e / (SAW_P * s / 0.6)))

    def bodyf(x, y):                                              # 배(ns 는 양옆) 가장자리가 꼬리 쪽으로 누운 톱니
        d = body0(x, y)
        side = (x - cx) * px + (y - cy) * py
        if not dangle and side <= 0:
            return d
        t = ((x - a0[0]) * ux + (y - a0[1]) * uy) / e
        return d - A * saw(t, nt) * smooth(0.0, r * 0.5, abs(side))
    pr = 1.85 * s / 0.6
    reach = 0.6 * (1 + sin(ph)) / 2
    if dangle:
        fronts = [oell(a0[0] + ux * (r * 1.4 + reach * 0.5) + px * j * (r + 0.2), a0[1] + uy * (r * 1.4 + reach * 0.5) + py * j * (r + 0.2),
                       pr * 1.1, pr * 0.85, ang) for j in (-1, 1)]
        backs = [oell(a1[0] + ux * r * 0.55 + px * j * r * 0.75, a1[1] + uy * r * 0.55 + py * j * r * 0.75,
                      pr * 0.8, pr, ang) for j in (-1, 1)]
    else:
        fronts = [oell(a0[0] - ux * (r + 0.9 + reach) + px * j * 1.35, a0[1] - uy * (r + 0.9 + reach) + py * j * 1.35,
                       pr * 1.15, pr * 0.85, ang) for j in (-0.7, 0.7)]
        backs = [oell(a1[0] + ux * (r * 0.55) + px * (r * 0.75 + j * 0.9), a1[1] + uy * (r * 0.55) + py * (r * 0.75 + j * 0.9),
                      pr * 0.95, pr * 0.8, ang) for j in (-0.8, 0.8)]
    tw = 0.5 * sin(2 * ph)
    t0 = (a1[0] + ux * r * 0.3, a1[1] + uy * r * 0.3)
    tq = (px, py) if not dangle else (0.0, 0.0)
    Ft = Frame(0.0, 0.0, 1.0)
    pts = [t0, (t0[0] + ux * 3.4 + tq[0] * 0.5, t0[1] + uy * 3.4 + tq[1] * 0.5),
           (t0[0] + ux * 6.6 + tq[0] * (1.4 + tw) + (tw * 0.8 if dangle else 0.0), t0[1] + uy * 6.6 + tq[1] * (1.4 + tw))]
    sc_ = s / 0.6
    tf, tcol = plume(Ft, pts, ((0.0, 1.3 * sc_), (0.35, 2.4 * sc_), (0.8, 2.2 * sc_), (1.0, 1.5 * sc_)))
    out.append(base(bodyf, tf, *fronts, *backs))
    out.append(part(tf, tcol))
    for f in backs:
        out.append(part(f, FUR_T))
    def bcol(x, y):
        q = abs((x - cx) * -uy + (y - cy) * ux)
        if q > r * 0.86:
            return FUR_T
        return TABBY if ((x - cx) * ux + (y - cy) * uy + 0.6) % 3.6 < 1.2 and q < r * 0.75 else FUR
    out.append(part(bodyf, bcol))
    for f in fronts:
        out.append(part(f, FUR_T))
    hx_, hy_ = a0[0] + ux * r * 0.9 + head[0] * hoff, a0[1] + uy * r * 0.9 + head[1] * hoff
    out += ncat(Frame(hx_, hy_, s), "blink" if k in (5, 11) else ("happy" if sin(ph) > 0.7 else "open"),
                body=False, paws=False, tail=False, ruff=not dangle)
    o = 0.6 if sin(ph) > 0.3 else 0.0
    for (x, y, dx, dy) in chev or ():
        out += gold_chevron(x + dx * o, y + dy * o, dx, dy, 2.2, 1.0 if o else 0.6)
    return out


def sc_we(fr):
    return lie(fr, (15.8, 12.4), 0.0, 12.0, 0.58, [(1.9, 12.6, -1, 0), (29.1, 12.6, 1, 0)], (0.0, -1.0), 2.5, branch=(1.2, 2.6))


def sc_ns(fr):
    return lie(fr, (6.5, 17.8), pi / 2, 10.0, 0.54, [(6.5, 1.9, 0, -1), (6.5, 29.1, 0, 1)], (0.0, -1.0), 3.2,
               dangle=True, branch=(4.6, 3.2))


def sc_nwse(fr):
    return lie(fr, (14.6, 14.6), pi / 4, 12.0, 0.56, [(3.6, 3.6, -1, -1), (27.4, 27.4, 1, 1)], (0.45, -0.9), 1.8,
               branch=(0.4, 1.2))


def sc_nesw(fr):
    return lie(fr, (16.4, 14.6), 3 * pi / 4, 12.0, 0.56, [(27.4, 3.6, 1, -1), (3.6, 27.4, -1, 1)], (-0.45, -0.9), 1.8,
               branch=(0.4, 1.2))


def sc_no(fr):
    """빨간 금지 표지 안에서 동그랗게 웅크려 깃털 꼬리로 얼굴을 덮는다 — 장 6–9 에 꼬리를 입 아래로 내려 눈만 빼꼼(옆눈질),
    다시 덮는다"""
    k = k_of(fr)
    peek_ = 6 <= k <= 9
    Cc = 15.5
    F = Frame(13.0, 13.8, 0.62)
    out = []
    loaf = shag(3.4, 7.4, 9.6, 4.6, ((-40, 85, 5), (175, 95, 3)))
    out += [base(F.f(loaf)), part(F.f(loaf), body_col(F, 3.4, 7.4, 9.6, 4.6))]
    out += ncat(F, "blink" if k == 8 else "open" if peek_ else "blink", look=(0.9, 0.2), body=False, paws=False,
                tail=False, ruff=False, mouth="")
    lw = 2.6 if peek_ else 0.0
    tp = [(12.2, 9.0), (12.8, 3.8), (9.0, -0.4 + lw), (3.0, -0.2 + lw), (-3.0, 0.6 + lw), (-8.4, 1.6 + lw)]
    tf, tcol = plume(F, tp, ((0.0, 2.0), (0.3, 3.0), (0.8, 2.9), (1.0, 2.2)))
    out += [base(tf), part(tf, tcol)]
    R = 12.5
    sg = union(ring(Cc, Cc, R - 1.25, 1.25), capsule(Cc - 7.7, Cc - 7.7, Cc + 7.7, Cc + 7.7, 1.35))
    out += [base(sg), part(sg, lambda x, y: lerp(SIGN_L, SIGN, smooth(Cc - 10, Cc - 4, y + 0.5 * x - 0.5 * Cc)), shade=SIGN_D,
                           ink=SIGN_D, line=0.8)]
    return out


def sc_busy(fr):
    """작은 화살표 노르웨이숲 + 솔방울 둘레를 맴도는 나뭇잎 여덟 — 앞장은 초록, 뒤로 갈수록 흐린 주황. 솔방울이 까딱"""
    out = nbuddy(fr)
    cx, cy = 22.4, 22.4
    k = k_of(fr)
    head = k * 8 / NF
    for i in range(8):
        a = TAU * i / 8 - pi / 2
        lag = (head - i) % 8
        al = 1.0 if lag < 3 else 0.6 if lag < 5 else 0.3
        out += leaf(cx + 6.7 * cos(a), cy + 6.7 * sin(a), a + pi / 2 + 0.5, 1.55, lag < 1.5, al)
    out += cone(cx, cy + 0.4, 2.2, 2.9, 0.18 if k % 6 < 3 else -0.18)
    return out


def sc_help(fr):
    """작은 화살표 노르웨이숲 + 잔가지로 휜 물음표(솔잎 두 다발) — 가지가 살랑, 점은 솔방울이 통통"""
    ph = TAU * fr
    out = nbuddy(fr)
    sw = 0.4 * sin(ph)
    q = union(arc(23.2, 13.6, 3.9, 1.05, pi * 0.95, pi * 1.42), capsule(24.7, 17.2, 23.0 + sw, 19.4, 1.05),
              capsule(23.0 + sw, 19.4, 23.0 + sw, 21.2, 1.05))
    out += needles(19.4, 14.4, pi * 0.62, 2.0, 3, 0.6)
    out += needles(26.8, 11.6, -0.2 + sw * 0.3, 2.0, 3, 0.6)
    out += twig_layers(q)
    hop = abs(sin(pi * k_of(fr) / 6))
    out.insert(0, layer(ell(23.2, 29.6, 2.4 - 0.6 * hop, 0.6), lambda *a: (OUT, 0.2)))
    out += cone(23.2, 25.6 - 1.6 * hop, 1.75, 2.3, 0.0)
    return out


SPRUCE = [(0.0, -4.4, 2.0, -1.8), (0.0, -2.2, 2.9, 0.5), (0.0, 0.2, 3.6, 2.8)]   # (가운데 x, 꼭대기 y, 밑 반폭, 밑 y)


def sc_pin(fr):
    """작은 화살표 노르웨이숲 + 흰 전나무가 든 빨간 지도 핀이 통통 — 땅에 닿을 때 금색 그림자가 진해진다"""
    out = nbuddy(fr)
    hop = abs(sin(pi * fr))
    cx, cy = 22.6, 15.2 - 2.6 * hop
    out.insert(0, layer(ell(22.8, 29.0, 3.4 - 0.8 * hop, 0.75), lambda *a: (GOLD, 0.85 - 0.45 * hop)))
    f = smin(1.0, circle(cx, cy, 5.6), poly([(cx - 4.6, cy + 2.6), (cx + 4.6, cy + 2.6), (cx, cy + 11.4)]))
    out += [base(f), part(f, lambda x, y: lerp(SIGN_L, SIGN, smooth(cy - 5, cy - 1.5, y + 0.6 * (x - cx))), shade=SIGN_D, ink=SIGN_D)]
    tree = union(*[poly([(cx + x0, cy + y0), (cx + x0 + w, cy + y1), (cx + x0 - w, cy + y1)]) for x0, y0, w, y1 in SPRUCE],
                 rbox(cx, cy + 3.4, 0.55, 0.8, 0.2))
    out.append(flat(grow(tree, 0.1), RUFF, line=0.35, ink=RUFF_S))
    return out


def sc_person(fr):
    """작은 화살표 노르웨이숲 + 노르웨이숲을 목도리처럼 어깨에 두른 사람 — 냥이 얼굴은 오른 어깨, 깃털 꼬리는 왼쪽으로
    늘어져 흔들. 사람은 눈을 감고 흐뭇"""
    ph = TAU * fr
    k = k_of(fr)
    out = nbuddy(fr)
    cx, cy = 22.6, 21.6
    body = clip_y(ell(cx, cy + 9.0, 7.4, 5.6), 30.6)
    head = circle(cx, cy, 4.3)
    hair = smin(0.6, ell(cx, cy - 2.4, 4.8, 2.6), ell(cx - 4.0, cy - 0.6, 1.2, 2.0), ell(cx + 4.0, cy - 0.6, 1.2, 2.0))
    out += [base(body, head, hair), part(body, lambda x, y: COATP_D if abs(x - cx) < 0.5 else COATP, shade=COATP_D),
            part(head, SKIN, shade=SKIN_D), part(hair, HAIR, shade=HAIR_D)]
    for sg in (-1, 1):                                            # 흐뭇하게 감은 눈 · 볼
        out.append(flat(arc(cx + sg * 1.7, cy + 0.0, 0.85, 0.24, pi * 0.15, pi * 0.7), EYE))
        out.append(soft(ell(cx + sg * 2.7, cy + 1.8, 0.9, 0.55), CHEEK, 0.8))
    out.append(flat(arc(cx, cy + 1.7, 0.85, 0.22, pi * 0.15, pi * 0.7), SKIN_D))
    sw = sin(ph)
    F = Frame(cx + 4.4, cy + 2.4, 0.38)                           # 오른 어깨의 냥이 얼굴(머리 가운데)
    scarf = fluffy(cx - 0.6, cy + 5.4, 6.8, 1.75, (60, 90, 120), 1.0, 0.8, (0.0, 0.3))
    tl, tcol = plume(Frame(0.0, 0.0, 1.0), [(cx - 5.8, cy + 5.0), (cx - 7.2, cy + 7.6), (cx - 6.6 + 0.6 * sw, cy + 9.6)],
                     ((0.0, 1.3), (0.4, 1.8), (0.8, 1.7), (1.0, 1.2)))
    out += [base(scarf, tl), part(tl, tcol), part(scarf, lambda x, y: TABBY if (x * 0.9) % 3.2 < 1.0 and y < cy + 5.8 else
                                                   FUR_T if y > cy + 6.3 else FUR)]
    out += ncat(F, "blink" if k in (4, 5) else "open", look=(-0.3, 0.2), body=False, paws=False, tail=False, ruff=False,
                mouth="")
    return out


SCENE = {"busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "wait": sc_wait,
         "hand": sc_hand, "cross": sc_cross, "ibeam": sc_ibeam, "move": sc_move, "no": sc_no, "pen": sc_pen,
         "up": sc_up, "we": sc_we, "ns": sc_ns, "nwse": sc_nwse, "nesw": sc_nesw, "arrow": npeek}


class NorwegianCat(Pet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes).
    모양 탭 화살표도 장모 빼꼼으로(catkit.peek_shape 와 같은 자리)"""

    def cell(self, name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
        if shape and name == "arrow":
            catkit.use(self.coat)
            return npeek_shape(frame, shape), shaped(shape)["hot"]
        return super().cell(name, frame, soft_, tip_body)


PET = NorwegianCat(COAT, SCENE, HOT)


def scene(name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
    return PET.cell(name, frame, soft_, tip_body, shape)


register("norwegiancat", PET)

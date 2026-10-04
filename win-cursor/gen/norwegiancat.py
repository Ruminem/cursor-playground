# SPDX-License-Identifier: Apache-2.0
"""노르웨이숲(norwegiancatanim) 구성표 그림 `art/norwegiancatanim/*.txt` 를 만든다.
빌드가 부르지 않고 손으로 돌린다 · 빌드 코드 해시와 CI 캐시 키에 안 들어간다.

  python3 gen/norwegiancat.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

해달처럼 칸마다 노르웨이숲이 하는 짓을 따로 그린다(`SCENE`). '냥이 · 애니' 묶음과 머리 비율(반지름 7 · 세모 귀 ·
ㅅ 입 · 볼터치 · 1칸 수염)을 맞추되, 노르웨이숲은 **장모**라 털 끝이 삐죽삐죽한 외곽선(`fluff` — 볼 · 배 · 꼬리 가장자리가
한쪽으로 누운 톱니)과 가슴에만 두른 흰 갈기(`ruff` — 목둘레까지 두르면 사자로 읽힌다), 귀 끝 검은 털(링크스 팁),
크고 풍성한 깃털 꼬리(`plume` — 밑동은 가늘고 가운데가 부푼다)로 고등어냥과 갈린다. 갈색 고등어(짙은 갈색 줄 · 이마 M)
바탕에 털 가장자리는 밝은 갈색, 눈은 초록 섞인 금색, 화살촉 같은 신호색은 금색이다.
소품은 숲의 것 — 자작나무 기둥(갈색 털과 갈리게 흰 껍질에 검은 무늬) · 솔방울 · 나뭇잎 · 눈송이.

  arrow   큰 흰 화살표 뒤에 숨은 노르웨이숲이 빗변 위로 빼꼼 — 갈색 발끝 둘이 빗변을 잡고 장 2–5 에 쏙 더
          올라온다. 화살표 끝이 핫스팟(`sea.peek`, 냥이 10종 공용 틀)
  busy    작은 화살표 노르웨이숲 + 오른쪽 아래 솔방울 둘레를 맴도는 나뭇잎 여덟 장(앞장은 초록, 뒤로 갈수록 흐려진다)
  cross   자작나무 기둥을 끌어안고 그 앞에서 내다보는 앞모습 — 긴 수염이 가로 조준선, 귀 사이 · 턱 밑 기둥이 세로선.
          사냥 눈(동공이 커졌다 줄었다), 코가 핫스팟
  hand    오른쪽 자작나무에 매달린 채 앞발 하나를 왼쪽 위로 쭉 내밀어 발톱으로 톡톡 — 발톱 끝이 핫스팟
  help    작은 화살표 노르웨이숲 + 잔가지로 휜 물음표(솔잎 두 다발), 점은 통통 튀는 솔방울
  ibeam   위는 솔잎 가지 · 아래는 뿌리인 자작나무가 I — 등을 보인 노르웨이숲이 기둥을 끌어안고 오르락내리락.
          핫스팟은 기둥 가운데
  move    그루터기 위에 앉아 사방을 두리번 — 위 · 오른쪽 · 아래 · 왼쪽을 차례로 보고, 보는 쪽 금색 화살촉이 튀어나온다
  nesw · ns · nwse · we   그 축으로 뻗은 나뭇가지에 엎드려 앞발과 깃털 꼬리를 양 끝으로 쭉 — 늘었다 줄었다 하고
          양 끝 화살촉이 두근댄다. ns 는 세로 기둥에 매달린 꼴. 얼굴은 늘 똑바로 둔다(기운 얼굴은 칸 위에서 뭉개진다)
  no      빨간 금지 표지 안에서 동그랗게 웅크려 깃털 꼬리로 얼굴을 덮어 버린다 — 꼬리를 살짝 내려 눈만 빼꼼, 다시 덮는다
  pen     잔가지를 쥐고 눈밭에 글씨를 쓴다 — 가지 끝(왼쪽 아래)이 핫스팟, 지나간 자리에 파란 눈 고랑이 남는다
  person  작은 화살표 노르웨이숲 + 노르웨이숲을 목도리처럼 어깨에 두른 사람 — 냥이 얼굴은 오른쪽 어깨, 꼬리는 왼쪽으로
          늘어져 흔들린다
  pin     작은 화살표 노르웨이숲 + 흰 전나무가 든 빨간 지도 핀이 통통 튄다
  up      앉아서 깃털 꼬리를 깃대처럼 위로 곧게 세운다 — 꼬리 끝(맨 위)이 핫스팟이라 끝은 그대로 두고 가운데만 살랑,
          눈은 위를 올려다본다
  wait    눈 내리는 날 깃털 꼬리로 제 몸을 휘감고 앉아 존다 — 숨에 몸이 부풀었다 줄고 꼬리 끝이 까딱, 눈송이가 떨어진다.
          가운데가 핫스팟

몸은 부위(타원 · 굵기가 변하는 막대 · 세모)를 고양이 제 좌표 (u 오른쪽, w 아래)에 놓고 화면으로 돌려 찍는다
(`Rig`, `draw` — 고등어냥 생성기와 같은 방식이지만 다른 생성기에 기대지 않게 여기 따로 둔다).
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import N, SIGN, SIGN_D, disc, finish, hx, ink, inside, peek, peek_tail, phases, raster, solid, write

SID = "norwegiancatanim"

OUT, EYE = hx("3a2a22ff"), hx("221812ff")                       # 테두리 · 눈동자
FUR, FUR_T, STRIPE = hx("a67a4eff"), hx("cfa676ff"), hx("5e412aff")   # 갈색 · 밝은 털 끝(가장자리 · 발) · 짙은 줄
CREAM, PINK, NOSE, HI = hx("f7f0e4ff"), hx("f4a0b0ff"), hx("e27d90ff"), hx("ffffffff")
IRIS = hx("b4c442ff")
RING = hx("86603eff")                                           # 꼬리 고리 (장모라 줄이 흐리다)                                           # 초록 섞인 금색 눈
ink(OUT, HI, hx("fbecdcc7"))
GLOW = (hx("e8b23aff"), hx("e8b23ab0"), hx("e8b23a60"))         # 화살촉 (짙은 것부터)
BIRCH, BIRCH_D, BIRCH_M = hx("f2eee6ff"), hx("d4ccc0ff"), hx("3a3430ff")   # 자작나무 껍질 · 그늘 · 검은 무늬
BARK, BARK_D = hx("7a5a44ff"), hx("54402fff")                   # 잔가지 · 그루터기
CONE, CONE_D, CONE_L = hx("9a5a32ff"), hx("6a3c22ff"), hx("c8844aff")   # 솔방울
NEEDLE, NEEDLE_D = hx("4f9a52ff"), hx("2f6a3cff")                # 솔잎
LEAF = (hx("6cb04aff"), hx("e8a03aff"), hx("e8a03ab0"), hx("e8a03a60"))   # 나뭇잎 — 앞장 초록, 뒤로 흐려진다
SNOW, SNOW_D = hx("9cc8ecff"), hx("6c9cc8ff")                    # 눈송이 · 눈 고랑
SKIN, HAIR = hx("f7d7bcff"), hx("e0b04aff")
COAT, COAT_D = hx("3e7fa0ff"), hx("2a5a74ff")                    # 사람 옷 (갈색 냥이와 갈리게 파랑)


# ── 그리개: 고양이 제 좌표 (u, w) → 화면 ─────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도) · 배율 k. ang=0 이면 u 가 오른쪽, w 가 아래. ang 만큼 시계 방향으로 돈다"""

    def __init__(self, ox: float, oy: float, ang: float = 0.0, k: float = 1.0):
        t = math.radians(ang)
        self.ox, self.oy, self.c, self.s, self.k = ox, oy, math.cos(t), math.sin(t), k

    def world(self, a: float, b: float) -> tuple:
        return self.ox + (a * self.c - b * self.s) * self.k, self.oy + (a * self.s + b * self.c) * self.k

    def local(self, x: float, y: float) -> tuple:
        dx, dy = (x - self.ox) / self.k, (y - self.oy) / self.k
        return dx * self.c + dy * self.s, -dx * self.s + dy * self.c

    def cell(self, a: float, b: float) -> tuple:
        x, y = self.world(a, b)
        return math.floor(x), math.floor(y)


def ell(ca, cb, ra, rb, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)

    def hit(a, b):
        da, db = a - ca, b - cb
        u, v = da * c + db * s, -da * s + db * c
        return (u / ra) ** 2 + (v / rb) ** 2 <= 1
    return hit


def saw(x: float) -> float:
    return x - math.floor(x)


def fluff(ca, cb, ra, rb, rot=0.0, amp=0.9, step=2.2, arc=None):
    """털 끝이 삐죽삐죽한 타원 — 둘레 step 칸마다 바깥으로 amp 만큼 솟는 톱니(한쪽으로 누운 털 결).
    arc=(a0, a1) 이면 타원 제 각도(도, 0 이 +u, 90 이 +w 곧 아래) 그 사이에만 톱니. 톱니가 고르게 사방으로
    솟으면 고슴도치 가시가 되므로 amp 는 한 칸 안팎으로 둔다"""
    c, s = math.cos(rot), math.sin(rot)
    per = max(5, round(math.pi * (ra + rb) / step))
    mean = (ra + rb) / 2

    def hit(a, b):
        da, db = a - ca, b - cb
        u, v = da * c + db * s, -da * s + db * c
        q = (u / ra) ** 2 + (v / rb) ** 2
        if q <= 1:
            return True
        th = math.atan2(v / rb, u / ra)
        if arc:
            d = math.degrees(th) % 360
            if not (arc[0] <= d <= arc[1] if arc[0] <= arc[1] else (d >= arc[0] or d <= arc[1])):
                return False
        rr = 1 + amp * saw(th / (2 * math.pi) * per) / mean
        return q <= rr * rr
    return hit


def bar(p0, p1, r0, r1=None):
    """p0 → p1 막대. 굵기(반지름)가 r0 → r1 로 변하고 두 끝이 둥글다"""
    r1 = r0 if r1 is None else r1
    ex, ey = p1[0] - p0[0], p1[1] - p0[1]
    ll = ex * ex + ey * ey or 1e-9

    def hit(a, b):
        t = max(0.0, min(1.0, ((a - p0[0]) * ex + (b - p0[1]) * ey) / ll))
        px, py = p0[0] + ex * t, p0[1] + ey * t
        return (a - px) ** 2 + (b - py) ** 2 <= (r0 + (r1 - r0) * t) ** 2
    return hit


def chain(pts, r0, r1=None):
    """꺾은선 막대 — 굵기가 처음 r0 에서 끝 r1 로 고르게 변한다"""
    r1 = r0 if r1 is None else r1
    n = len(pts) - 1
    return any_of(*[bar(pts[i], pts[i + 1], r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n) for i in range(n)])


def nearest(pts):
    """꺾은선 위 가장 가까운 점 → (거리, 처음부터의 길이, 왼쪽(-1)/오른쪽(+1)), 전체 길이"""
    segs, acc = [], 0.0
    for p, q in zip(pts, pts[1:]):
        L = math.hypot(q[0] - p[0], q[1] - p[1]) or 1e-9
        segs.append((p, q, L, acc))
        acc += L

    def at(a, b):
        best = None
        for p, q, L, s0 in segs:
            ex, ey = q[0] - p[0], q[1] - p[1]
            t = max(0.0, min(1.0, ((a - p[0]) * ex + (b - p[1]) * ey) / (L * L)))
            dx, dy = a - p[0] - ex * t, b - p[1] - ey * t
            d = math.hypot(dx, dy)
            if best is None or d < best[0]:
                best = (d, s0 + L * t, 1 if ex * dy - ey * dx > 0 else -1)
        return best
    return at, acc


def along(pts):
    at, total = nearest(pts)
    return (lambda a, b: at(a, b)[1]), total


def tri(*pts):
    pl = list(pts)
    return lambda a, b: inside(pl, a, b)


def any_of(*hs):
    return lambda a, b: any(h(a, b) for h in hs)


def draw(rig: Rig, parts: list) -> tuple[dict, set, dict]:
    """parts: [(이름, 맞음(a, b), 색(a, b) 또는 색, 테두리)] — 앞의 것이 위에 그려진다.
    칸을 4×4 로 찍어 반 넘게 덮이면 칠하고, 가장 많이 덮은 부위의 색을 준다. 바깥 테두리와,
    테두리=True 인 부위가 뒤 부위와 닿는 자리에 선을 긋는다. → ({칸: 색}, 칸 집합, {칸: 부위})"""
    order = {p[0]: i for i, p in enumerate(parts)}
    region, mask = {}, set()
    for y in range(-3, 35):
        for x in range(-3, 35):
            hits = {}
            for j in range(4):
                for i in range(4):
                    a, b = rig.local(x + (i + 0.5) / 4, y + (j + 0.5) / 4)
                    for name, hit, _, _ in parts:
                        if hit(a, b):
                            hits[name] = hits.get(name, 0) + 1
                            break
            if sum(hits.values()) >= 8:
                mask.add((x, y))
                region[x, y] = max(hits, key=lambda n: (hits[n], -order[n]))
    col = {p[0]: p[2] for p in parts}
    lined = {p[0] for p in parts if p[3]}
    out = {}
    for p in mask:
        c = col[region[p]]
        out[p] = c(*rig.local(p[0] + 0.5, p[1] + 0.5)) if callable(c) else c
        x, y = p
        nb = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        if any(q not in mask for q in nb):
            out[p] = OUT
        elif region[p] in lined and any(order[region[q]] > order[region[p]] for q in nb):
            out[p] = OUT
    return out, mask, region


# ── 몸 부위 ──────────────────────────────────────────────────────────────────
HC, HR = (0.0, -7.5), 7.0       # 머리 가운데 · 반지름 (묶음 공통)


def head_parts(hc=HC, r=HR, turn=0.0, name="head", back=False) -> list:
    """앞모습 머리: 털 끝이 삐죽한 볼(아래 · 옆에만) · 큰 세모 귀(속 분홍)와 귀 끝 검은 털 · 흰 주둥이 · 볼에 짙은 줄.
    M 무늬는 `face` 가 칸으로 찍는다. back 이면 뒤통수 — 귀 속이 안 보이고 정수리에서 목덜미로 짙은 줄 셋"""
    u0, w0 = hc
    head = any_of(ell(u0, w0 - 0.4, r * 0.98, r * 0.86),
                  fluff(u0, w0 + 1.0, r * 1.1, r * 0.64, amp=r * 0.3, step=r * 0.5, arc=(8, 172)))
    ears, inner, tufts = [], [], []
    for sg in (-1, 1):
        base0, tip, base1 = (u0 + sg * r * 1.0, w0 - r * 0.2), (u0 + sg * r * 0.84 + turn * 0.3, w0 - r * 1.46), \
            (u0 + sg * r * 0.14, w0 - r * 0.76)
        ears.append(tri(base0, tip, base1))
        tufts.append(bar(tip, (tip[0] + sg * r * 0.02, tip[1] - r * 0.16), r * 0.09))
        cx, cy = (base0[0] + tip[0] + base1[0]) / 3, (base0[1] + tip[1] + base1[1]) / 3 + r * 0.06
        inner.append(tri(*[(cx + (p[0] - cx) * 0.46, cy + (p[1] - cy) * 0.46) for p in (base0, tip, base1)]))
    inner_hit = any_of(*inner)

    def skin(a, b):
        mu = a - u0 - turn
        if back:
            if b < w0 + r * 0.5 and any(abs(mu - d * r * 0.34) < r * 0.1 for d in (-1, 0, 1)):
                return STRIPE
            return FUR
        if (mu / (r * 0.42)) ** 2 + ((b - (w0 + r * 0.38)) / (r * 0.28)) ** 2 <= 1:
            return CREAM
        if abs(mu) > r * 0.74 and any(abs(b - (w0 + r * dd)) < r * 0.08 for dd in (0.0, 0.26)):
            return STRIPE
        if b > w0 + r * 0.5 and abs(mu) > r * 0.6:     # 볼 털 끝은 밝게
            return FUR_T
        return FUR

    def ear_col(a, b):
        return FUR if back else PINK if inner_hit(a, b) else FUR
    return [(name, head, skin, True), (name + "_ear", any_of(*ears), ear_col, False),
            (name + "_tuft", any_of(*tufts), STRIPE, False)]


def ruff(c=(0.0, -0.4), ra=3.8, rb=3.0, name="ruff"):
    """가슴에만 두른 흰 갈기 — 아래 가장자리가 삐죽삐죽. 목 뒤로는 안 두른다(사자로 읽힌다)"""
    return (name, fluff(c[0], c[1], ra, rb, amp=2.2, step=2.6, arc=(30, 150)), CREAM, False)


def body_part(c=(0.0, 3.0), ra=6.2, rb=6.4, name="body", rot=0.0, stripes="across", arc=(10, 170)):
    """통통한 장모 몸 — 아래쪽(배 · 엉덩이) 털 끝이 삐죽, 옆구리에 굵은 짙은 줄, 가장자리는 밝은 털 끝"""
    c0, c1 = c
    cs, sn = math.cos(rot), math.sin(rot)

    def col(a, b):
        da, db = a - c0, b - c1
        u, v = da * cs + db * sn, -da * sn + db * cs
        q = (u / ra) ** 2 + (v / rb) ** 2
        if q > 0.8:
            return FUR_T
        if stripes == "across":      # 앞모습: 옆구리 가로 줄
            if abs(da) > ra * 0.45 and (db + 0.8) % 4.0 < 1.5:
                return STRIPE
        elif stripes == "along":     # 기울인 몸: 몸 축을 가로지르는 줄
            if (u + 0.6) % 4.2 < 1.6 and abs(v) < rb * 0.8:
                return STRIPE
        return FUR
    return (name, fluff(c0, c1, ra, rb, rot, amp=2.2, step=3.4, arc=arc), col, False)


def plume(pts, prof=((0.0, 1.2), (0.3, 2.6), (0.75, 2.6), (1.0, 1.8)), name="tail", lined=False, amp=2.0, step=3.0):
    """크고 풍성한 깃털 꼬리 — 밑동은 가늘고 가운데가 부풀며, 양옆 가장자리가 털 결대로 삐죽. 짙은 고리 셋 · 끝은 짙게 ·
    가장자리는 밝은 털 끝. prof 는 (전체 길이 비율, 반지름)"""
    at, total = nearest(pts)

    def rad(s):
        t = s / total
        for (t0, r0), (t1, r1) in zip(prof, prof[1:]):
            if t0 <= t <= t1:
                return r0 + (r1 - r0) * (t - t0) / (t1 - t0)
        return prof[-1][1]

    def hit(a, b):
        d, s, sd = at(a, b)
        r = rad(s)
        if d <= r:
            return True
        if s / total < 0.12 or s >= total - 1e-6:
            return False
        return d <= r + amp * saw(s / step + (0.5 if sd > 0 else 0.0))

    def col(a, b):
        d, s, _ = at(a, b)
        if s > total - 1.0:
            return STRIPE
        if d > rad(s) * 0.92:
            return FUR_T
        return STRIPE if (s % 5.2) > 4.0 and s > 2.0 else FUR
    return (name, hit, col, lined)


def leg_part(pts, r=2.0, pr=2.1, name="arm", lined=True):
    """다리 하나 → [발, 다리]. 발은 밝은 털, 긴 다리엔 줄 하나"""
    at, total = along(pts)
    paw = (name + "_paw", ell(*pts[-1], pr, pr), FUR_T, True)

    def col(a, b):
        s = at(a, b)
        return STRIPE if total > 9.0 and abs(s - total * 0.55) < 0.7 else FUR
    return [paw, (name, chain(pts, r, r * 0.92), col, lined)]


M_MARK = ["#...#", "##.##", "#.#.#"]


def face(f: dict, rig: Rig, hc=HC, r=HR, mood="open", turn=0.0, look=(0, 0), mark=True) -> None:
    """얼굴: 2×2 금빛 눈(흰 반짝 · 짙은 동공) · 분홍 코 · ㅅ 입 · 볼터치 · 이마 M 무늬. 작게(k·r < 4.5) 그리면 눈 1×2 · 코 1칸.
    mood: open · blink · sleep(︶) · happy(^). look 은 동공을 옮길 칸 (dx, dy)"""
    u0, w0 = hc
    small = rig.k * r < 4.5
    for sg in (-1, 1):
        ex, ey = rig.world(u0 + turn + sg * r * 0.42, w0 - r * 0.06)
        if small:
            x0, y0 = math.floor(ex), math.floor(ey - 0.5)
            if mood == "open":
                f[x0, y0] = IRIS
            f[x0, y0 + 1] = EYE
            continue
        x0, y0 = round(ex - 1), round(ey - 1)
        if mood == "open":
            for dx in (0, 1):
                for dy in (0, 1):
                    f[x0 + dx, y0 + dy] = IRIS
            px = x0 + (1 if look[0] >= 0 else 0)
            py = y0 + (1 if look[1] >= 0 else 0)
            f[px, py] = EYE
            f[x0 + (0 if px > x0 else 1), y0 + (0 if py > y0 else 1)] = HI
        elif mood == "blink":
            f[x0, y0 + 1] = EYE
            f[x0 + 1, y0 + 1] = EYE
        elif mood == "sleep":
            f[x0, y0 + 1] = EYE
            f[x0 + 1, y0 + 1] = EYE
            f[x0 - 1 if sg < 0 else x0 + 2, y0] = EYE
        elif mood == "happy":
            f[x0 - 1 if sg < 0 else x0, y0 + 1] = EYE
            f[x0 if sg < 0 else x0 + 1, y0] = EYE
            f[x0 + 1 if sg < 0 else x0 + 2, y0 + 1] = EYE
    if mark and not small:   # 이마 M — 머리 위쪽 털 칸에만
        mx, my = rig.world(u0 + turn, w0 - r * 0.66)
        x0, y0 = round(mx) - 3, round(my) - 1
        for j, row in enumerate(M_MARK):
            for i, ch in enumerate(row):
                if ch == "#" and f.get((x0 + i, y0 + j)) == FUR:
                    f[x0 + i, y0 + j] = STRIPE
    nx, ny = rig.world(u0 + turn, w0 + r * 0.16)
    if small:
        f[math.floor(nx), math.floor(ny)] = NOSE
    else:
        nl, ny = round(nx) - 1, math.floor(ny)
        f[nl, ny] = NOSE
        f[nl + 1, ny] = NOSE
        for p in ((nl - 1, ny + 2), (nl, ny + 1), (nl + 1, ny + 1), (nl + 2, ny + 2)):   # ㅅ 입
            f[p] = OUT
    for sg in (-1, 1):   # 볼터치
        bx, by = rig.world(u0 + turn + sg * r * 0.64, w0 + r * 0.24)
        f[math.floor(bx), math.floor(by)] = PINK
        if not small:
            f[math.floor(bx) + (1 if sg < 0 else -1), math.floor(by)] = PINK


def whiskers(f: dict, rig: Rig, hc=HC, r=HR, turn=0.0, n=3, skip=()) -> None:
    """볼 바깥으로 뻗은 1칸 수염 둘씩 — 머리 테두리 밖 칸에만 찍는다(얼굴 안에 그으면 콧수염이 된다)"""
    u0, w0 = hc
    for sg in (-1, 1):
        if sg in skip:
            continue
        for j, dw in enumerate((0.05, 0.3)):
            x0, y0 = rig.world(u0 + turn + sg * r * 1.2, w0 + r * dw)
            for i in range(n + 1):
                x = math.floor(x0 + sg * i)
                y = math.floor(y0 + (i * 0.4 * (j * 2 - 1) if j else 0))
                if (x, y) not in f:
                    f[x, y] = OUT


def anchor(frames: list[dict], target=(1, 1)) -> tuple[list[dict], tuple]:
    """맨 왼쪽 위 불투명 칸(x+y 가 가장 작은 것, 같으면 위)을 target 으로 옮긴다 — 화살표 꼴 칸의 끝"""
    tip = min((p for p, c in frames[0].items() if c[3] == 255), key=lambda p: (p[0] + p[1], p[1]))
    dx, dy = target[0] - tip[0], target[1] - tip[1]
    return [{(x + dx, y + dy): c for (x, y), c in f.items()} for f in frames], (dx, dy)


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col, n: int = 3) -> None:
    """(dx, dy) 쪽을 가리키는 화살촉. 꼭짓점이 (cx, cy)"""
    if dx and dy:   # 대각선은 꺾쇠(┘ 꼴) — 비스듬한 V 는 칸 위에서 점선이 된다
        for i in range(n + 1):
            for w in (0, 1):
                f.setdefault((cx - dx * i, cy - dy * w), col)
                f.setdefault((cx - dx * w, cy - dy * i), col)
        return
    px, py = -dy, dx
    for i in range(n):
        for s in (-1, 1):
            for w in (0, 1):
                f.setdefault((cx - dx * (i + w) + s * px * i, cy - dy * (i + w) + s * py * i), col)


def clip(f: dict) -> dict:
    return {p: c for p, c in f.items() if 0 <= p[0] <= 31 and 0 <= p[1] <= 31}


# ── 소품 ─────────────────────────────────────────────────────────────────────
def birch(f: dict, x0: int, x1: int, y0: int, y1: int, seed: int = 0) -> None:
    """세로 자작나무 기둥 — 흰 껍질, 오른쪽 그늘, 가로로 짧은 검은 무늬. 테두리는 OUT"""
    cells = {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}

    marks = set()
    w = x1 - x0 - 1
    y, i = y0 + 1 + seed % 3, seed
    while y < y1:   # 검은 무늬 — 길이 · 자리 · 간격을 들쭉날쭉하게(고르면 자 눈금으로 읽힌다)
        n = (2, 1, 2, 3, 1)[i % 5]
        start = x0 + 1 + min((1, 0, 2, 1)[i % 4], max(0, w - n))
        for x in range(start, min(x1, start + n)):
            marks.add((x, y))
        if i % 3 == 0:
            marks.add((start + (1 if i % 2 == 0 else -1) * 0, y + 1))
        y += (5, 3, 6, 4)[i % 4]
        i += 1

    def col(p):
        if p in marks:
            return BIRCH_M
        return BIRCH_D if p[0] == x1 - 1 else BIRCH
    for p in cells:
        f[p] = OUT if p[0] in (x0, x1) else col(p)


def cone(f: dict, cx: float, cy: float, rx: float = 1.9, ry: float = 2.6, stem=False) -> None:
    """솔방울 — 짙은 테 안에 비늘(밝은 칸이 엇갈린 줄), 위에 짧은 꼭지"""
    m = {(x, y) for y in range(math.floor(cy - ry) - 1, math.ceil(cy + ry) + 1)
         for x in range(math.floor(cx - rx) - 1, math.ceil(cx + rx) + 1)
         if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1}
    solid(f, m, lambda p: CONE_L if (p[0] + p[1]) % 2 == 0 and p[1] % 2 == 0 else CONE, CONE_D)
    if stem:
        top = min(y for _, y in m)
        f[math.floor(cx), top - 1] = BARK_D


# ── 화살표 노르웨이숲 ────────────────────────────────────────────────────────
TIP = (-17.0, -21.0)        # 가지 끝 (화살표 끝)
BR1 = (14.0, 11.0)          # 가지 뒤 끝 (꼬리 밑동 근처)


def arrow_cat(ph: float, k: float = 0.8, blink=False, tail=True) -> tuple[dict, Rig]:
    """왼쪽 위로 뻗은 가지를 끌어안고 타고 오르는 노르웨이숲 — 얼굴은 똑바로, 몸은 가지를 따라 비스듬히.
    앞발 둘이 번갈아 가지를 고쳐 쥐고 깃털 꼬리가 아래로 늘어져 살랑인다"""
    rig = Rig(16.0, 16.0, 0.0, k)
    sw = math.sin(ph)
    g = 0.8 * sw                           # 번갈아 쥐기
    ux, uy = BR1[0] - TIP[0], BR1[1] - TIP[1]
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L

    def on(t, side=0.0):   # 가지 위 t 칸 자리 (+side 는 가지 아래쪽)
        return TIP[0] + ux * t - uy * side, TIP[1] + uy * t + ux * side
    branch = ("branch", bar(TIP, BR1, 1.0, 1.5), lambda a, b: BARK_D if (a - b) % 5 < 1 else BARK, True)
    f1 = leg_part([(-3.6, -3.0), on(7.6 + g, 0.4)], name="f1", pr=1.9, r=1.8)
    f2 = leg_part([(-1.0, -1.0), on(11.6 - g, 1.4)], name="f2", pr=1.9, r=1.8)
    hind = ("hind", any_of(ell(*on(39.0 + 0.4 * g, 1.8), 2.0, 1.6), ell(*on(35.0 - 0.4 * g, 2.8), 2.0, 1.6)),
            FUR_T, True)
    body = body_part((5.8, 3.6), 8.0, 5.0, rot=math.atan2(uy, ux), stripes="along", arc=(20, 170))
    parts = f1 + head_parts() + f2 + [hind, ruff((0.0, -0.6), 4.0, 2.6), body]
    if tail:
        parts.append(plume([(11.6, 7.4), (13.6, 10.6), (13.4 + 0.8 * sw, 12.6), (15.2 + 1.4 * sw, 13.8)],
                           prof=((0.0, 1.2), (0.35, 2.5), (0.8, 2.3), (1.0, 1.6))))
    parts.append(branch)
    out, _, _ = draw(rig, parts)
    face(out, rig, mood="blink" if blink else "open", look=(-1, -1))
    return out, rig


def arrow_frames(small=False, tail=True):
    fr = [arrow_cat(ph, 0.5 if small else 0.8, blink=k in (7,), tail=tail)[0] for k, ph in enumerate(phases())]
    return anchor(fr)


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    def head(x, y, k):
        rig = Rig(x - HC[0] * PEEK_K, y - HC[1] * PEEK_K, 0.0, PEEK_K)
        g, _, _ = draw(rig, sitting() + [plume(peek_tail(k, (5.6, 7.6), 0.9),
                                                     ((0.0, 1.1), (0.3, 2.0), (0.75, 2.0), (1.0, 1.4)))])   # 꼬리는 오른쪽으로 길게 U 자
        face(g, rig, mood="blink" if k == 7 else "open", look=(-1, -1))
        whiskers(g, rig, n=2, skip=(-1,))
        return g
    return [{p: c for p, c in finish(peek(k, head, OUT, FUR)).items() if p[1] <= 31} for k in range(N)]


PEEK_K = 0.74     # 빼꼼 노르웨이숲 배율


def companion(scene, tail=True) -> list[dict]:
    """작은 화살표 노르웨이숲 + scene(k, ph) 이 그리는 소품 — busy · help · person · pin"""
    cats, _ = arrow_frames(small=True, tail=tail)
    frames = []
    for k, ph in enumerate(phases()):
        f = scene(k, ph)
        f.update(cats[k])
        frames.append(finish(f))
    return frames


LEAF_G = [".##", "###", "#.."]    # 나뭇잎 하나 (오른쪽 위로 뾰족, 왼쪽 아래 꼭지)


def busy() -> list[dict]:
    """솔방울 둘레를 나뭇잎 여덟 장이 맴돈다 — 앞장은 초록, 뒤로 갈수록 주황으로 흐려진다. 솔방울이 까딱"""
    cx, cy = 22.0, 22.0

    def scene(k, ph):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = round(cx + 6.6 * math.cos(a) - 1), round(cy + 6.6 * math.sin(a) - 1)
            lag = (head - i) % 8
            c = LEAF[0] if lag < 1.5 else LEAF[1] if lag < 3 else LEAF[2] if lag < 5 else LEAF[3]
            for j, row in enumerate(LEAF_G):
                for i2, ch in enumerate(row):
                    if ch == "#":
                        f[x + i2, y + j] = c
        cone(f, cx + (0.5 if k % 6 < 3 else -0.5), cy + 0.6, 2.2, 3.0)
        return f
    return companion(scene)


def help_() -> list[dict]:
    """잔가지로 휜 물음표(솔잎 두 다발) — 가지가 살랑, 점은 솔방울이 통통"""
    def scene(k, ph):
        f = {}
        sw = 0.5 * math.sin(ph)
        pts = [(18.0, 11.0), (17.6, 7.6), (19.6, 5.0), (23.0, 4.4), (26.0, 6.0), (26.6 + sw * 0.4, 9.2),
               (24.4, 12.0), (22.4, 14.0), (22.2 + sw, 18.0)]
        o, _, _ = draw(Rig(0, 0, 0, 1.0), [("twig", chain(pts, 1.2, 1.0), BARK, False)])
        f.update(o)
        for nx, ny in ((18.0, 11.0), (26.6 + sw * 0.4, 9.2)):   # 솔잎 다발 — 짧은 바늘 셋
            for d in ((-1, 1), (0, 1), (1, 1)):
                f.setdefault((math.floor(nx) + d[0], math.floor(ny) + d[1] + 1), NEEDLE)
        dy = -round(1.5 * abs(math.sin(ph)))
        cone(f, 22.6, 24.0 + dy, 1.8, 2.3)
        return f
    return companion(scene)


def person() -> list[dict]:
    """노르웨이숲을 목도리처럼 어깨에 두른 사람 — 냥이 얼굴은 왼 어깨, 몸은 목 뒤로 돌아 깃털 꼬리가 오른 어깨 앞으로
    늘어져 흔들린다. 사람은 눈을 감고 흐뭇하다"""
    def scene(k, ph):
        f = {}
        rig = Rig(23.0, 19.0, 0.0, 0.7)
        sw = 1.2 * math.sin(ph)
        chc, cr = (7.0, -2.6), 5.2
        tail = plume([(-6.6, -2.6), (-8.4, 1.0), (-7.8 + 0.5 * sw, 5.4), (-8.6 + sw, 9.6)],
                     prof=((0.0, 1.6), (0.35, 2.6), (0.8, 2.4), (1.0, 1.7)), name="ctail", lined=True)
        hair = ("hair", any_of(ell(0.0, -13.0, 5.4, 3.2), ell(-4.4, -11.0, 1.4, 2.4), ell(4.4, -11.0, 1.4, 2.4)),
                HAIR, True)
        skin = ("skin", ell(0.0, -9.8, 4.6, 4.4), SKIN, True)
        cbody = ("cbody", fluff(0.0, -2.6, 9.6, 2.4, amp=1.4, step=2.2, arc=(20, 160)),
                 lambda a, b: STRIPE if (a + 0.6) % 4.4 < 1.4 and b > -3.4 else FUR, True)
        cpaw = ("cpaw", ell(4.6, 2.6, 1.8, 1.5), FUR_T, True)
        torso = ("torso", ell(0.0, 7.4, 9.8, 8.6), lambda a, b: COAT_D if abs(a) < 0.6 else COAT, False)
        out, _, _ = draw(rig, head_parts(chc, cr, name="chead") + [cpaw, tail, hair, skin, cbody, torso])
        for sg in (-1, 1):   # 사람 얼굴 — 흐뭇하게 감은 눈 · 볼터치
            ex, ey = rig.cell(sg * 1.9, -9.6)
            out[ex, ey] = EYE
            out[ex + (1 if sg > 0 else -1), ey] = EYE
            out[rig.cell(sg * 3.0, -7.6)] = PINK
        face(out, rig, chc, cr, mood="blink" if k in (4, 5) else "open", mark=False)
        f.update({p: c for p, c in out.items() if p[1] <= 30 and p[0] <= 30})
        return f
    return companion(scene)


SPRUCE = ["..#..", ".###.", "..#..", ".###.", "#####", "..#.."]   # 핀 속 전나무


def pin() -> list[dict]:
    """빨간 지도 핀 동그라미 속에 흰 전나무 — 통통 튀고 땅에 닿을 때 그림자가 진해진다"""
    def scene(k, ph):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 14.0 + dy
        for x in range(19, 27):
            f.setdefault((x, 28), GLOW[2] if dy else GLOW[1])
        pinm = disc(cx, cy, 6.2) | raster([(cx - 4.4, cy + 3.4), (cx + 4.4, cy + 3.4), (cx, cy + 12.4)])
        solid(f, pinm, SIGN, SIGN_D)
        x0, y0 = math.floor(cx) - 2, math.floor(cy) - 3
        for j, row in enumerate(SPRUCE):
            for i, ch in enumerate(row):
                if ch == "#":
                    f[x0 + i, y0 + j] = CREAM
        return f
    return companion(scene)


def sitting(hc=HC, turn=0.0, breath=0.0, tail=None, look=(0, 0)):
    """앉은 노르웨이숲 부위 — 머리 · 가슴 갈기 · 통통한 몸 · 앞발 · 뒷발. tail 은 맨 앞에 둘 꼬리 부위"""
    paws = ("paws", any_of(ell(-2.4, 9.4, 1.9, 1.5), ell(2.4, 9.4, 1.9, 1.5)), FUR_T, True)
    hind = ("hind", any_of(ell(-5.4, 9.2, 2.2, 1.5), ell(5.4, 9.2, 2.2, 1.5)), FUR_T, True)
    body = body_part((0.0, 3.6 - breath * 0.5), 6.4 + breath * 0.5, 6.4 + breath * 0.5)
    parts = ([tail] if tail else []) + head_parts(hc, turn=turn) + [paws, ruff((hc[0] + turn * 0.4, -0.4)),
                                                                     hind, body]
    return parts


def wait() -> list[dict]:
    """눈 오는 날 깃털 꼬리로 제 몸을 휘감고 앉아 존다 — 숨에 몸이 부풀었다 줄고, 꼬리 끝이 까딱, 눈송이 넷이 떨어진다.
    장 9–10 에 한쪽 눈을 살짝 떴다 감는다"""
    frames = []
    flakes = [(4, 2), (27, 9), (7, 20), (25, 26)]
    for k, ph in enumerate(phases()):
        f = {}
        for i, (x0, y0) in enumerate(flakes):   # 눈송이 — 한 바퀴에 판을 한 번 내려간다
            y = (y0 + round(32 * k / N)) % 32
            x = x0 + (1 if (k + i) % 4 < 2 else 0)
            for d in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                f[x + d[0], y + d[1]] = SNOW
        rig = Rig(16.0, 17.4, 0.0, 0.82)
        br = math.sin(ph)
        tw = 0.9 * math.sin(2 * ph)
        tail = plume([(6.4, 8.4), (3.0, 11.0), (-3.0, 11.0), (-7.4, 8.8), (-8.6 + tw * 0.5, 5.6 + tw)],
                     prof=((0.0, 1.6), (0.3, 2.5), (0.8, 2.4), (1.0, 1.6)), lined=True)
        cat, _, _ = draw(rig, sitting(breath=br, tail=tail))
        face(cat, rig, mood="blink" if k in (9, 10) else "sleep")
        whiskers(cat, rig, n=2)
        f.update(cat)
        frames.append(clip(finish(f)))
    return frames


def cross() -> list[dict]:
    """자작나무 기둥을 끌어안고 그 앞에서 내다보는 앞모습 — 금빛 눈의 동공이 가늘었다(장 0–3) 둥글게 커진다.
    긴 수염 한 줄씩이 가로 조준선, 귀 사이 · 턱 밑으로 보이는 기둥이 세로선. 코(15, 15)가 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        birch(f, 13, 18, 0, 31, seed=2)
        rig = Rig(16.0, 21.9, 0.0, 1.0)
        tw = 0.6 if k in (6, 7) else 0.0
        hp = head_parts(turn=tw)
        paws = ("paws", any_of(ell(-4.2, 2.4, 2.2, 1.7), ell(4.2, 2.4, 2.2, 1.7)), FUR_T, True)
        cat, _, _ = draw(rig, [paws] + hp + [ruff((0.0, 0.4), 3.6, 1.8)])
        face(cat, rig, mood="open", mark=True)
        wide = 4 <= k <= 9
        for sg in (-1, 1):   # 3×3 금빛 눈에 세로 동공
            ex, ey = rig.world(sg * HR * 0.42, HC[1] - HR * 0.06)
            x0, y0 = round(ex) - (2 if sg < 0 else 1), round(ey) - 2
            for dx in range(3):
                for dy in range(3):
                    cat[x0 + dx, y0 + dy] = IRIS
            for dy in range(3):
                cat[x0 + 1, y0 + dy] = EYE
                if wide and dy > 0:
                    cat[x0 + (0 if sg > 0 else 2), y0 + dy] = EYE
            cat[x0 + (2 if sg > 0 else 0), y0] = HI
        f.update(cat)
        for x in range(1, 31):   # 가로 조준선 — 얼굴 밖 칸만
            if (x, 15) not in cat:
                f[x, 15] = OUT
        for sg in (-1, 1):   # 아래로 비스듬한 짧은 수염
            for i in range(3):
                x = (5 - i * 2 if sg < 0 else 26 + i * 2)
                f.setdefault((x, 17 + (i + 1) // 2), OUT)
                f.setdefault((x + (-1 if sg < 0 else 1), 17 + (i + 1) // 2), OUT)
        frames.append(clip(finish(f)))
    return frames


HAND_TIP = (4, 4)


def hand() -> list[dict]:
    """오른쪽 자작나무에 뒷발과 앞발 하나로 매달린 노르웨이숲이 다른 앞발을 왼쪽 위로 쭉 내밀어 발톱으로 톡톡 —
    발톱 끝이 핫스팟(`HAND_TIP`). 톡 칠 때(장 2–3 · 8–9) 발톱 둘레에 눌림 줄이 튀고, 깃털 꼬리가 아래로 늘어져 살랑"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(19.0, 20.0, 0.0, 0.74)
        tap = k in (2, 3, 8, 9)
        pc = (-11.4, -12.8)
        arm = leg_part([(-3.6, -1.0), (-7.4, -6.6), pc], name="arm", pr=2.6, r=2.2)
        grip = leg_part([(3.4, -1.0), (7.4, -3.2)], name="grip", pr=1.8, r=1.7)
        sw = math.sin(ph)
        hind = ("hind", any_of(ell(7.6, 8.6, 1.8, 2.0), ell(5.8, 10.4, 1.8, 1.6)), FUR_T, True)
        tail = plume([(2.6, 9.6), (3.4, 13.4), (2.0 + 0.8 * sw, 17.2), (3.0 + 1.6 * sw, 20.4)],
                     prof=((0.0, 1.3), (0.35, 2.5), (0.8, 2.3), (1.0, 1.6)))
        body = body_part((2.6, 3.4), 5.4, 6.4)
        parts = arm + head_parts(turn=-0.8) + grip + [hind, ruff((-0.3, -0.4), 3.8, 2.6), body, tail]
        cat, _, _ = draw(rig, parts)
        face(cat, rig, mood="open", turn=-0.8, look=(-1, -1))
        tx, ty = rig.cell(pc[0] - 1.5, pc[1] - 1.5)   # 발톱: 발끝에서 왼쪽 위로 흰 두 칸
        claw = [(tx, ty), (tx - 1, ty - 1)]
        for p in claw:
            cat[p] = CREAM
        cat.setdefault((tx - 1, ty), OUT)
        cat.setdefault((tx, ty - 1), OUT)
        if tap:
            for p in ((tx - 4, ty - 1), (tx - 4, ty), (tx - 1, ty - 4), (tx, ty - 4), (tx - 3, ty - 3)):
                cat.setdefault(p, OUT)
        dx, dy = HAND_TIP[0] - (tx - 1), HAND_TIP[1] - (ty - 1)
        f = {}
        bx = rig.cell(8.6, 0.0)[0] + dx       # 나무는 매달린 발 바로 오른쪽
        birch(f, bx - 1, bx + 3, 0, 31, seed=1)
        f.update({(x + dx, y + dy): c for (x, y), c in cat.items()})
        frames.append(clip(finish(f)))
    return frames


def ibeam() -> list[dict]:
    """위는 솔잎 가지 · 아래는 뿌리인 자작나무가 I — 등을 보인 노르웨이숲이 기둥을 끌어안고 오르락내리락.
    네 발이 기둥 양옆을 쥐고 깃털 꼬리가 기둥을 따라 늘어진다. 기둥 가운데(15, 15)가 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        birch(f, 13, 18, 3, 28, seed=0)
        top = {(x, y) for x in range(7, 25) for y in range(1, 4)}
        solid(f, top, lambda p: BARK_D if p[1] == 2 and p[0] % 3 == 0 else BARK)
        for x in (6, 7, 8, 23, 24, 25):                 # 가지 끝 솔잎
            for y in (0, 4):
                f.setdefault((x, y), NEEDLE if (x + y) % 2 else NEEDLE_D)
        roots = {(x, y) for y in range(28, 31) for x in range(13 - (y - 27) * 2, 19 + (y - 27) * 2)}
        solid(f, roots, BARK)
        dy = 2.6 * math.sin(ph)
        climb = 0.9 * math.sin(ph)                      # 오를 때 앞발이 위로, 뒷발이 아래로
        rig = Rig(15.9, 14.8 + dy, 0.0, 0.56)
        arms = [("arms", any_of(bar((-4.6, -1.0), (-4.4, -4.0 - climb), 1.7), bar((4.6, -1.0), (4.4, -4.0 + climb), 1.7)),
                 FUR, True),
                ("apaws", any_of(ell(-3.6, -5.0 - climb, 1.9, 1.6), ell(3.6, -5.0 + climb, 1.9, 1.6)), FUR_T, True)]
        hind = ("hind", any_of(ell(-5.6, 9.6 + climb, 2.0, 2.2), ell(5.6, 9.6 - climb, 2.0, 2.2)), FUR_T, True)
        tail = plume([(0.0, 9.0), (0.4, 14.0), (-0.6 + 0.6 * math.sin(2 * ph), 19.0)],
                     prof=((0.0, 1.4), (0.35, 2.5), (0.8, 2.3), (1.0, 1.6)))
        back = ("body", fluff(0.0, 3.4, 5.6, 7.0, amp=2.2, step=3.4, arc=(0, 180)),
                lambda a, b: STRIPE if abs(a) < 0.7 or (b - 0.4) % 4.0 < 1.5 else FUR, False)
        cat, _, _ = draw(rig, [arms[1], tail] + head_parts(back=True) + [hind, arms[0], back])
        f.update(cat)
        frames.append(finish(f))
    return frames


def move() -> list[dict]:
    """그루터기 위에 앉아 사방을 두리번 — 장 0–2 위, 3–5 오른쪽, 6–8 아래, 9–11 왼쪽을 본다(고개와 눈이 그쪽으로).
    보는 쪽 금색 화살촉이 한 칸 튀어나오고 나머지는 옅다. 깃털 꼬리가 앞발을 휘감는다"""
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        d = dirs[k // 3]
        for dd in dirs:
            on = dd == d
            chevron(f, 15 + dd[0] * (13 + on), 15 + dd[1] * (13 + on), dd[0], dd[1], GLOW[0] if on else GLOW[1])
        stump = {(x, y) for x in range(10, 22) for y in range(24, 28)}
        solid(f, stump, lambda p: BARK_D if p[1] == 26 or (p[0] % 4 == 0) else BARK)
        for x in range(11, 21):           # 그루터기 위 나이테 면
            f[x, 24] = CREAM if x % 3 else WOOD_RING
        rig = Rig(15.8, 15.6, 0.0, 0.6)
        turn = d[0] * 1.4
        hc = (0.0, -7.5 + (-0.4 if d[1] < 0 else 0.6 if d[1] > 0 else 0.0))
        tail = plume([(6.0, 8.6), (2.6, 11.4), (-3.0, 11.4), (-6.8, 9.4)],
                     prof=((0.0, 1.6), (0.3, 2.5), (0.8, 2.3), (1.0, 1.6)), lined=True)
        cat, _, _ = draw(rig, sitting(hc=hc, turn=turn, tail=tail))
        face(cat, rig, hc, turn=turn, mood="blink" if k == 7 else "open", look=d, mark=False)
        f.update(cat)
        frames.append(finish(f))
    return frames


WOOD_RING = hx("d8b88aff")


def branch_cat(ang: float, L0: float, D: float, r: float = 5.0, k: float = 1.0) -> list[dict]:
    """ang 축(도, 0 이 오른쪽, 머리 → 꼬리)으로 뻗은 나뭇가지에 엎드려 앞발과 깃털 꼬리를 양 끝으로 쭉 —
    몸이 L0 ± 1.4 로 늘었다 줄었다. 머리는 늘 똑바로(얼굴이 안 기운다). 가지는 축 따라 판 끝까지,
    양 끝 화살촉 꼭짓점은 판 가운데에서 축 따라 D 칸"""
    t = math.radians(ang)
    ex, ey = math.cos(t), math.sin(t)
    dx, dy = round(ex), round(ey)

    def cat(L, ph, kk, shift):
        rig = Rig(15.5 + ex * shift, 15.5 + ey * shift, ang, k)
        sw = math.sin(ph + 1.0)
        side = 1 if ey >= 0 and ex >= 0 else -1          # 배 쪽 (꼬리 끝이 화면 아래 · 오른쪽으로 처진다)
        body = ("body", fluff(0.0, 0.0, L / 2 + 1.0, 3.0, amp=2.0, step=3.2, arc=(0, 180) if side > 0 else (180, 360)),
                lambda a, b: FUR_T if abs(b) > 2.4 else STRIPE if (a + 0.6) % 4.0 < 1.5 else FUR, False)
        reach = -L / 2 - r * 1.5 - 1.6 - 0.4 * math.sin(ph)    # 앞발은 머리 너머로 쭉
        fore = ("fore", any_of(bar((-L / 2, 1.8 * side), (reach, 2.4 * side), 1.3),
                               ell(reach - 0.2, 2.4 * side, 1.7, 1.4)), FUR_T, True)
        hind = ("hind", ell(L / 2 - 0.4, 2.8 * side, 1.8, 1.5), FUR_T, True)
        tail = plume([(L / 2 + 0.6, 0.0), (L / 2 + 4.0, 0.6 * side), (L / 2 + 7.2, (1.2 + 0.6 * sw) * side)],
                     prof=((0.0, 1.4), (0.35, 2.4), (0.8, 2.2), (1.0, 1.5)))
        bo, _, _ = draw(rig, [fore, hind, body, tail])
        hxw, hyw = rig.world(-L / 2 - r * 0.5, -0.6 * side)
        hrig = Rig(hxw, hyw, 0.0, k)
        ho, _, _ = draw(hrig, head_parts((0.0, 0.0), r))
        face(ho, hrig, (0.0, 0.0), r, mood="happy" if kk in (3, 4, 5) else "open")
        bo.update(ho)
        return bo

    rest = cat(L0, 0.0, 0, 0.0)
    proj = [(x + 0.5 - 15.5) * ex + (y + 0.5 - 15.5) * ey for x, y in rest]
    shift = -(min(proj) + max(proj)) / 2
    frames = []
    for kk, ph in enumerate(phases()):
        f = {}
        st = 1.4 * math.sin(ph)
        o = 1 if st > 0.4 else 0
        for sg in (-1, 1):
            chevron(f, round(15.5 + sg * ex * (D + o) - 0.5), round(15.5 + sg * ey * (D + o) - 0.5),
                    sg * dx, sg * dy, GLOW[0] if o else GLOW[1])
        px, py = -ey, ex                                  # 가지 — 축 따라, 몸 배 쪽으로 조금 내려서
        side = 1 if ey >= 0 and ex >= 0 else -1
        off = 2.6 * side * k
        for i in range(-60, 61):
            s = i / 4
            x, y = 15.5 + ex * s + px * off, 15.5 + ey * s + py * off
            if abs(s) <= D - 3.5:
                for w in (-0.5, 0.5):
                    f[math.floor(x + px * w), math.floor(y + py * w)] = BARK
        f.update(cat(L0 + st, ph, kk, shift))
        frames.append(clip(finish(f)))
    return frames


def ns() -> list[dict]:
    return branch_cat(90.0, 6.0, 13.5, r=4.8, k=1.0)


def we() -> list[dict]:
    return branch_cat(0.0, 6.0, 13.5, r=5.0, k=1.0)


def nwse() -> list[dict]:
    return branch_cat(45.0, 8.0, 18.4, r=5.0, k=0.95)


def nesw() -> list[dict]:
    return branch_cat(135.0, 8.0, 18.4, r=5.0, k=0.95)


def no() -> list[dict]:
    """빨간 금지 표지 안에서 동그랗게 웅크려 깃털 꼬리로 얼굴을 덮는다 — 장 6–9 에 꼬리를 입 아래로 살짝 내려
    눈만 빼꼼(옆눈질), 다시 덮는다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        ring = {(x, y) for x in range(32) for y in range(32)
                if 11.4 <= math.hypot(x + 0.5 - 16, y + 0.5 - 16) <= 14.6}
        slash = {(x, y) for x in range(32) for y in range(32)
                 if math.hypot(x + 0.5 - 16, y + 0.5 - 16) < 11.6 and abs((x - y)) <= 1}
        solid(f, ring | slash, SIGN, SIGN_D)
        rig = Rig(16.0, 17.6, 0.0, 0.66)
        peek = 6 <= k <= 9
        hc = (-0.6, -3.0)
        lw = 2.6 if peek else 0.0
        tail = plume([(8.6, 4.6), (9.0, -0.6 + lw * 0.5), (5.0, -3.4 + lw), (-1.0, -3.6 + lw), (-6.6, -2.2 + lw)],
                     prof=((0.0, 1.8), (0.3, 2.8), (0.8, 2.7), (1.0, 2.0)), lined=True)
        body = body_part((0.6, 4.8), 8.6, 4.6, arc=(0, 180))
        cat, _, region = draw(rig, [tail] + head_parts(hc) + [body])
        if peek:   # 내린 꼬리 위로 눈만 — 머리 칸에 드러난 자리에만 찍는다
            for sg in (-1, 1):
                ex, ey = rig.world(hc[0] + sg * HR * 0.42, hc[1] - HR * 0.06)
                x0, y0 = round(ex - 1), round(ey - 1)
                cells = [(x0, y0), (x0 + 1, y0)] if k == 8 else [(x0, y0), (x0 + 1, y0), (x0, y0 + 1), (x0 + 1, y0 + 1)]
                for p in cells:
                    if region.get(p) == "head" and cat[p] != OUT:
                        cat[p] = EYE if k == 8 or p == (x0 + (0 if sg > 0 else 1), y0 + 1) else IRIS
                if k != 8 and region.get((x0 + (1 if sg > 0 else 0), y0)) == "head":
                    cat[x0 + (1 if sg > 0 else 0), y0] = HI
        f.update(cat)
        frames.append(finish(f))
    return frames


def pen() -> list[dict]:
    """앉은 노르웨이숲이 잔가지를 두 앞발로 쥐고 눈밭에 글씨를 쓴다 — 가지 끝(왼쪽 아래)이 핫스팟.
    지나간 자리에 파란 눈 고랑이 물결로 자라고 깃털 꼬리가 살랑"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for i in range(k + 1):   # 눈 고랑 — 가지 끝에서 오른쪽으로 물결치며 자란다
            x = 5 + i
            f[x, 29 + (1 if (i // 2) % 2 else 0)] = SNOW_D
        rig = Rig(20.6, 16.4, 0.0, 0.72)
        sw = math.sin(ph)
        wig = 0.6 * math.sin(2 * ph)
        tail = plume([(6.0, 8.6), (10.0, 7.4), (11.6 + 0.6 * sw, 3.0), (10.4 + 1.2 * sw, -1.0)],
                     prof=((0.0, 1.4), (0.35, 2.5), (0.8, 2.3), (1.0, 1.6)))
        hold = (-5.0 + wig, 3.0)
        arms = leg_part([(-2.4, 0.6), hold], name="a1", pr=1.9, r=1.7) + \
            leg_part([(1.4, 1.0), (hold[0] + 1.6, hold[1] + 1.6)], name="a2", pr=1.9, r=1.7)
        cat, _, _ = draw(rig, arms + sitting(turn=-1.0) + [tail])
        face(cat, rig, mood="open", turn=-1.0, look=(-1, 1))
        whiskers(cat, rig, turn=-1.0, n=2, skip=(-1,))
        hx_, hy_ = rig.world(*hold)
        twig = {}
        line_cells(twig, (2.0, 29.6), (hx_ + 0.5, hy_), BARK)
        for p, c in twig.items():
            if p not in cat or cat[p] in (OUT,):
                f[p] = c
        f.update({p: c for p, c in cat.items() if p[0] <= 31})
        for p, c in twig.items():   # 쥔 발 아래로 지나는 가지는 발 앞에
            if p[1] > hy_ + 1:
                f[p] = c
        frames.append(clip(finish(f)))
    return frames


def line_cells(f: dict, a, b, col) -> None:
    """a → b 1칸 굵기 선 (끝 a 를 반드시 칠한다)"""
    n = max(1, math.ceil(math.hypot(b[0] - a[0], b[1] - a[1]) * 2))
    for i in range(n + 1):
        x, y = a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n
        f[math.floor(x), math.floor(y)] = col


def pen_tip(fr):
    return max((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1] - p[0], -p[0]))


def up() -> list[dict]:
    """앉아서 깃털 꼬리를 깃발처럼 하늘로 바짝 세운다 — 꼬리 끝(맨 위)이 핫스팟이라 끝은 안 움직이고, 꼬리 가운데가
    살랑이며 털 끝이 나부낀다. 고개를 들어 제 꼬리 끝을 올려다본다"""
    frames = []
    for k, ph in enumerate(phases()):
        rig = Rig(12.4, 20.6, 0.0, 0.7)
        sw = math.sin(ph)
        tail = plume([(5.0, 7.0), (9.6, 5.0), (11.4 + 0.9 * sw, -4.0), (11.0 - 0.7 * sw, -14.0), (10.6, -26.0)],
                     prof=((0.0, 1.4), (0.25, 3.0), (0.8, 3.2), (1.0, 1.8)))
        cat, _, _ = draw(rig, sitting(turn=0.8) + [tail])
        face(cat, rig, mood="blink" if k == 5 else "open", turn=0.8, look=(1, -1))
        whiskers(cat, rig, turn=0.8, n=2, skip=(1,))
        frames.append(finish(cat))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}


def top_cell(fr):
    return min((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1], p[0]))


HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1),
       "wait": (16, 16), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (15, 15),
       "hand": HAND_TIP, "up": top_cell, "pen": pen_tip}


def check(rid: str, frames: list[dict], hot: tuple) -> None:
    """핫스팟이 장마다 불투명한 칸 위에 있는지 · 판(0–31) 안인지"""
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
        if any(c[3] == 255 and not (0 <= x <= 31 and 0 <= y <= 31) for (x, y), c in f.items()):
            print(f"  ! {rid} {i}장: 판 밖으로 나간 불투명 칸이 있음")
        if hot == (1, 1) and any(c[3] == 255 and (p[0] < 1 or p[1] < 1) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 끝보다 왼쪽·위로 나온 칸이 있음")


def main() -> None:
    def job(r):
        def run():
            frames = SCENE[r]()
            hot = HOT[r](frames) if callable(HOT[r]) else HOT[r]
            check(r, frames, hot)
            frames = [clip(f) for f in frames]   # 판 밖으로 나간 반투명 테는 자른다
            print(f"  {r} 핫스팟 {hot}")
            return frames, hot
        return run
    write(SID, {r: job(r) for r in SCENE}, sys.argv[1:] or None)


if __name__ == "__main__":
    main()

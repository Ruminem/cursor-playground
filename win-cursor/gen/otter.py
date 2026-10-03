# SPDX-License-Identifier: Apache-2.0
"""해달(otteranim) 구성표 그림 `art/otteranim/*.txt` 를 만든다. 빌드가 부르지 않고 손으로 돌린다.

  python3 gen/otter.py [역할...]     그림을 쓴다 (역할을 안 주면 17칸 전부)

복어·새우처럼 해달 색을 입힌 화살표가 아니라 칸마다 해달이 하는 짓을 따로 그린다(`SCENE`).
치비 비율 — 크림색 큰 동그란 머리 · 짙은 갈색 몸 · 콩알 눈 · 작은 코 · 분홍 볼터치 · 짧은 앞발 · 짧은 꼬리.
다른 해양 애니가 파랑·회색이라 따뜻한 갈색과 크림으로 간다.

  arrow   배를 깔고(등을 물에 대고) 둥실 뜬 옆모습 해달 — 코끝이 왼쪽 위 핫스팟. 뒷발이 까딱이고 물결이 흐른다
  busy    작은 화살표 해달 + 오른쪽 아래 조개 둘레를 도는 물방울 고리
  cross   앞모습 얼굴. 수염이 가로 조준선, 머리 위 털 한 가닥과 턱 아래 물방울 줄이 세로 조준선. 코가 핫스팟
  hand    자다가(눈 감은 ^^) 손잡자고 앞발 하나를 높이 든 해달 — 해달은 잘 때 손을 잡는다. 발끝이 핫스팟
  help    작은 화살표 해달 + 물방울로 찍은 물음표
  ibeam   세로 다시마 줄기를 끌어안은 해달 — 해달은 떠내려가지 않게 다시마를 몸에 감는다. 줄기가 I, 핫스팟은 줄기
  move    물 위에서 데굴데굴 도는(위에서 본) 해달 + 네 방향 물결 화살촉
  nesw · ns · nwse · we   조개를 안고 누운(위에서 본) 해달이 그 축으로 둥실 오간다 — 양 끝 물결 화살촉
  no      두 앞발로 얼굴을 가린 해달(부끄러운 거절) — 뒤에 빨간 금지 표지. 가끔 발 사이로 빼꼼 본다
  pen     연필을 끌어안은 해달 — 연필심(왼쪽 아래)이 핫스팟
  person  작은 화살표 해달 + 사람 아이콘 꼴로 선 아기 해달
  pin     작은 화살표 해달 + 동그라미 속에 해달 얼굴이 든 빨간 지도 핀이 통통 튄다
  up      물 밖으로 몸을 꼿꼿이 세우고 둘레를 살피는(잠망경 자세) 앞모습 해달 — 머리 꼭대기가 핫스팟
  wait    위에서 본, 배 위 조개를 돌로 콩콩 두드리는 해달 — 가운데(조개)가 핫스팟

몸은 부위(타원·굵기가 변하는 막대)를 해달 제 좌표에 놓고 화면으로 돌려 찍는다(`Rig`, `draw`).
옆모습(`side`)과 위에서 본 모습(`top`) 두 벌이고, 앞모습 얼굴은 `top` 의 머리를 그대로 쓴다.
이 파일은 빌드 코드 해시와 CI 캐시 키에 안 들어간다 — 고쳐도 빌드는 아무것도 다시 안 그리니 돌려서 art 를 고친다.
"""
import math
import sys

from sea import BUB, N, QMARK, SIGN, SIGN_D, WAKE, bubble, disc, finish, hx, ink, phases, raster, solid, write

SID = "otteranim"

OUT, EYE = hx("2f1b10ff"), hx("1a0e08ff")                      # 테두리 · 눈코
FUR, FUR_L, PAW = hx("6b4128ff"), hx("8f5c38ff"), hx("4e2c18ff")  # 몸 · 배 · 발
CREAM, CREAM_D, HI = hx("f4e4c4ff"), hx("dcc39aff"), hx("fffaf0ff")  # 얼굴 · 얼굴 그늘 · 반짝
BLUSH, BEAN = hx("f49a9aff"), hx("f2a6aaff")                   # 볼터치 · 발바닥 젤리
ink(OUT, HI, hx("f6e9d2c7"))
CLAM, CLAM_D = hx("f2c0a4ff"), hx("cc8a70ff")                  # 조개
STONE, STONE_D = hx("a49e94ff"), hx("6e6a62ff")                # 돌
KELP, KELP_D, KELP_L = hx("6a9a3aff"), hx("44702aff"), hx("98c45aff")   # 다시마
PENCIL, PENCIL_D, WOOD, LEAD = hx("f5c842ff"), hx("c8961cff"), hx("efd2a8ff"), hx("3a3a3aff")
ERASER, FERRULE = hx("f2a0a8ff"), hx("b8b8c0ff")


# ── 그리개: 해달 제 좌표 (a, b) → 화면 ─────────────────────────────────────────
class Rig:
    """원점(ox, oy) · 각도 ang(도, a 축이 화면에서 가리키는 쪽, 90 이 아래) · 배율 k.
    b 축은 a 축을 시계 방향으로 90도 돌린 쪽(ang=0 이면 a 가 오른쪽, b 가 아래)"""

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
    """타원 (rot 은 라디안)"""
    c, s = math.cos(rot), math.sin(rot)

    def hit(a, b):
        da, db = a - ca, b - cb
        u, v = da * c + db * s, -da * s + db * c
        return (u / ra) ** 2 + (v / rb) ** 2 <= 1
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


def dot(f: dict, rig: Rig, a: float, b: float, c: tuple) -> None:
    f[rig.cell(a, b)] = c


# ── 위에서 본 해달(배를 하늘로): u 가로(+오른쪽), w 세로(+발 쪽), 원점은 배 가운데 ───────────────
HEAD = (0.0, -8.5, 6.2)          # 머리 가운데 · 반지름


def face(f: dict, rig: Rig, mood: str = "smile", hc=(0.0, -8.5)) -> None:
    """머리 가운데 hc 에 앞모습 얼굴: 콩알 눈 · 코 · ω 입 · 볼터치. mood 가 sleep 이면 감은 눈(^^),
    blink 면 감은 눈 한 줄, hide 면 눈은 앞발이 가리니 안 그린다"""
    u0, w0 = hc
    if mood in ("smile", "peek"):
        for sg in (-1, 1):
            if mood == "peek" and sg < 0:
                continue
            dot(f, rig, u0 + sg * 2.6, w0 - 0.9, EYE)
            dot(f, rig, u0 + sg * 2.6, w0 + 0.1, EYE)
    elif mood in ("sleep", "blink"):
        for sg in (-1, 1):
            dot(f, rig, u0 + sg * 2.6, w0 - 0.2, EYE)
            if mood == "sleep":
                dot(f, rig, u0 + sg * 2.6 - 1.0, w0 + 0.6, EYE)
                dot(f, rig, u0 + sg * 2.6 + 1.0, w0 + 0.6, EYE)
            else:
                dot(f, rig, u0 + sg * 2.6 - 1.0, w0 - 0.2, EYE)
    for sg in (-1, 1):   # 볼터치
        dot(f, rig, u0 + sg * 4.0, w0 + 1.6, BLUSH)
        dot(f, rig, u0 + sg * 3.1, w0 + 1.8, BLUSH)
    dot(f, rig, u0 - 0.5, w0 + 1.2, EYE)   # 코
    dot(f, rig, u0 + 0.5, w0 + 1.2, EYE)
    dot(f, rig, u0, w0 + 2.1, EYE)
    dot(f, rig, u0 - 1.0, w0 + 2.9, FUR)    # ω 입
    dot(f, rig, u0 + 1.0, w0 + 2.9, FUR)


def head_parts(hc=(0.0, -8.5), r=6.2) -> list:
    """앞모습 머리: 크림 동그라미 + 갈색 귀 둘. 아래쪽은 살짝 그늘"""
    u0, w0 = hc

    def skin(a, b):
        return CREAM_D if b > w0 + r * 0.72 else CREAM
    # 귀는 머리 옆에 작게 — 위 모서리에 크게 달면 곰·햄스터로 읽힌다
    ears = any_of(ell(u0 - r * 0.9, w0 - r * 0.5, 1.4, 1.4), ell(u0 + r * 0.9, w0 - r * 0.5, 1.4, 1.4))
    # 위는 둥근 이마, 아래는 옆으로 퍼진 볼 — 동그라미 하나면 칸 위에서 네모로 읽힌다
    head = any_of(ell(u0, w0 - 0.7, r * 0.96, r * 0.86), ell(u0, w0 + 1.4, r * 1.12, r * 0.6))
    return [("head", head, skin, True), ("ears", ears, FUR, False)]


def top(rig: Rig, paws=((-2.0, -2.2), (2.0, -2.2)), feet=((-4.6, 11.0), (4.6, 11.0)), mood="smile",
        extra=(), tail=0.0, behind=False, paw=PAW, beans=False, elbows=None, toes=False,
        pr=2.0, mid=()) -> tuple[dict, set]:
    """위에서 본 해달 한 장. paws 는 앞발 끝 둘, feet 는 뒷발 끝 둘(u, w), extra 는 앞발보다 앞에 놓을
    부위(조개·돌 등), tail 은 꼬리 끝이 옆으로 흔들린 정도(칸). behind 면 팔이 머리 뒤로 간다 —
    머리 위로 든 팔·얼굴을 가린 팔이 얼굴을 덮지 않고 앞발만 머리 앞에 보인다. paw 는 앞발 색,
    beans 면 앞발 가운데 분홍 젤리(손바닥이 보이는 앞발 — 든 앞발이 귀와 같은 갈색 덩이로 안 읽히게),
    elbows 는 팔꿈치 둘(팔이 머리를 돌아 올라가게), toes 면 앞발 위 끝에 발가락 금 둘, pr 은 앞발 반지름,
    mid 는 앞발 뒤 · 팔과 몸 앞에 놓을 부위(끌어안은 연필 · 다시마)"""
    arms, pads = [], []
    for i, (sg, (pu, pw)) in enumerate(zip((-1, 1), paws)):
        sh = (sg * 4.8, -1.8)
        if elbows and elbows[i]:
            arms += [bar(sh, elbows[i], 1.8, 1.7), bar(elbows[i], (pu, pw), 1.7, 1.6)]
        else:
            arms.append(bar(sh, (pu, pw), 1.8, 1.6))
        pads.append(ell(pu, pw, pr, pr * 1.1))
    legs = [bar((sg * 3.4, 7.4), (fu, fw), 2.0, 1.7) for sg, (fu, fw) in zip((-1, 1), feet)]
    soles = [ell(fu, fw, 1.8, 2.2, math.atan2(fu - sg * 3.4, -(fw - 7.4))) for sg, (fu, fw) in zip((-1, 1), feet)]

    def body(a, b):
        return FUR_L if ((a / 4.4) ** 2 + ((b - 2.6) / 5.6) ** 2) <= 1 else FUR
    arm = [("arm", any_of(*arms), FUR, not behind)]
    parts = list(extra) + [("paw", any_of(*pads), paw, True)] + list(mid) + ([] if behind else arm) + head_parts() + \
        (arm if behind else []) + [("foot", any_of(*soles), PAW, True), ("leg", any_of(*legs), FUR, False),
                                   ("body", any_of(ell(0, 2.2, 7.0, 7.8), ell(0, -2.5, 5.6, 4.0)), body, False),
                                   ("tail", bar((0, 8.5), (tail, 14.0), 2.4, 1.1), FUR, False)]
    out, mask, _ = draw(rig, parts)
    face(out, rig, mood)
    for pu, pw in paws:
        if beans:
            dot(out, rig, pu, pw, BEAN)
        if toes:
            for d in (-0.75, 0.75):
                dot(out, rig, pu + d * pr * 0.9, pw - pr * 0.75, OUT)
    return out, mask


# ── 옆모습(배를 하늘로 하고 뜬): a 는 코끝 0 → 꼬리 끝, b 는 + 가 등(물) 쪽 ─────────────────
def side(rig: Rig, ph: float = 0.0, mood="smile", paws=None, extra=()) -> tuple[dict, set]:
    """옆모습 해달 한 장. 코끝이 원점. ph 로 뒷발·꼬리가 까딱인다. paws 는 앞발 끝 둘(a, b).
    주둥이를 머리 앞으로 조금 내밀어 둔다 — 머리 가운데가 코에 가까우면 비스듬히 눕혔을 때 머리 옆이
    코끝보다 판 가장자리로 튀어나와 화살표 끝이 코가 아니게 된다"""
    H = 2.0   # 주둥이 길이만큼 머리부터 뒤로 민다
    kick = math.sin(ph)
    paws = paws or ((11.5 + H, -5.4), (13.6 + H, -5.0))
    feet = [ell(22.6 + H + 0.5 * kick, -5.6, 1.4, 2.4, -0.25 + 0.15 * kick),
            ell(24.6 + H - 0.5 * kick, -5.0, 1.4, 2.4, 0.2 - 0.15 * kick)]
    arms = [bar((ax - 1.5, -1.5), (ax, bw), 1.4, 1.4) for ax, bw in paws]
    pads = [ell(ax, bw, 1.6, 1.6) for ax, bw in paws]
    tail_tip = (31.0 + H, -1.5 + 1.2 * math.sin(ph + 1.0))

    def head(a, b):
        return CREAM_D if b > 3.0 else CREAM

    def body(a, b):
        return FUR_L if b < -2.4 else FUR
    parts = [("nose", ell(0.9, -0.3, 1.1, 0.9), EYE, False)] + list(extra) + [
        ("paw", any_of(*pads), PAW, True), ("arm", any_of(*arms), FUR, False),
        ("snout", ell(2.9, -0.4, 3.0, 2.3), CREAM, False),
        ("head", ell(7.0 + H, 0.0, 6.2, 5.9), head, True),
        ("ear", ell(10.2 + H, 4.4, 1.7, 1.7), FUR, False),
        ("foot", any_of(*feet), PAW, True),
        ("body", ell(16.0 + H, 0.6, 9.4, 5.4), body, False),
        ("tail", bar((23.5 + H, 0.6), tail_tip, 2.6, 1.0), FUR, False)]
    out, mask, region = draw(rig, parts)
    if mood == "blink":
        dot(out, rig, 5.0 + H, -2.6, EYE)
        dot(out, rig, 6.0 + H, -2.6, EYE)
    else:
        dot(out, rig, 5.4 + H, -2.8, EYE)
        dot(out, rig, 5.4 + H, -1.8, EYE)
    dot(out, rig, 7.8 + H, -0.6, BLUSH)
    dot(out, rig, 8.6 + H, -1.2, BLUSH)
    dot(out, rig, 2.8, 1.1, FUR)   # 입
    return out, mask


ARROW = Rig(1.3, 1.5, 45.0, 0.76)    # 화살표 해달: 코끝이 (1, 1)
ARROW_S = Rig(1.3, 1.5, 45.0, 0.55)  # 작은 화살표 해달 (busy · help · person · pin)


def arrow_otter(ph: float, small: bool = False) -> dict:
    k = N * ph / (2 * math.pi)
    return side(ARROW_S if small else ARROW, ph, "blink" if round(k) in (7,) else "smile")[0]


def ripple(f: dict, cx: float, cy: float, r: float, col=WAKE[2], arc=(0.0, 2 * math.pi)) -> None:
    """물결 고리(반투명) — 몸 뒤에 깐다"""
    n = max(8, int(r * 8))
    for i in range(n + 1):
        t = arc[0] + (arc[1] - arc[0]) * i / n
        f.setdefault((math.floor(cx + r * math.cos(t)), math.floor(cy + r * math.sin(t) * 0.55)), col)


# ── 장면 ─────────────────────────────────────────────────────────────────────
def arrow() -> list[dict]:
    """둥실 뜬 옆모습 — 뒷발이 까딱이고 꼬리가 살랑, 등 밑으로 물결이 흐른다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = arrow_otter(ph)
        for j in range(3):   # 등 밑 물결
            t = (k / N + j / 3) % 1
            a = 6 + 20 * t
            for d in (-1, 0, 1):
                f.setdefault(ARROW.cell(a + d, 5.6 + 0.4 * abs(d)), WAKE[2] if d == 0 else WAKE[3])
        frames.append(finish(f))
    return frames


def clam_col(a: float, b: float, ca: float = 0.0, cb: float = 1.8) -> tuple:
    """조개 껍데기: 아래 경첩에서 부채꼴로 퍼지는 골"""
    ang = math.atan2(a - ca, cb + 2.6 - b)
    return CLAM_D if round(ang / 0.42) % 2 else CLAM


CLAM_PART = ("clam", any_of(ell(0, 1.5, 3.6, 2.8), ell(0, 4.0, 1.4, 1.0)), clam_col, True)


def wait() -> list[dict]:
    """배 위 조개를 돌로 콩콩 — 오른 앞발의 돌이 올라갔다 내려와 조개에 닿으면 반짝"""
    frames = []
    rig = Rig(15.5, 16.2, 0.0, 1.0)
    for k, ph in enumerate(phases()):
        lift = max(0.0, math.sin(2 * ph))   # 한 바퀴에 두 번 두드린다
        sp = (2.0, -1.0 - 3.4 * lift)       # 돌 쥔 앞발
        stone = ("stone", ell(sp[0] - 1.4, sp[1] - 0.6, 2.0, 1.6), lambda a, b: STONE if b < sp[1] - 0.6 else STONE_D,
                 True)
        f, _ = top(rig, paws=((-3.6, 2.2), sp), extra=(stone, CLAM_PART), tail=0.6 * math.sin(ph),
                   mood="blink" if k == 9 else "smile")
        if lift < 0.05:   # 닿는 순간 반짝
            for d in ((-4.0, -2.4), (4.6, -2.0), (-5.0, 0.6)):
                f.setdefault(rig.cell(*d), HI)
        ripple(f, 15.5, 22.0, 11.5, WAKE[3], (0.15, math.pi - 0.15))
        frames.append(finish(f))
    return frames


def drift(ang: float) -> list[dict]:
    """조개를 안은 해달(위에서 본)이 ang 축을 따라 둥실 오간다 — 양 끝 물결 화살촉이 가는 쪽으로 두근댄다.
    배 가운데가 판 가운데. 처음엔 머리 위로 팔을 쭉 뻗는 기지개였는데, 든 앞발의 분홍 젤리가 토끼 귀로 읽혔다"""
    frames = []
    t = math.radians(ang)
    ex, ey = -math.sin(t), math.cos(t)          # 머리 → 발 쪽 (화면)
    dx, dy = round(ex), round(ey)
    R = 13 if dx == 0 or dy == 0 else 10
    for k, ph in enumerate(phases()):
        f = {}
        d = 1.2 * math.sin(ph)                  # + 면 발 쪽으로
        for sg in (-1, 1):
            o = 1 if sg * d > 0.3 else 0
            chevron(f, 15 + (1 if sg * dx > 0 else 0) + sg * dx * (R + o) - (1 if sg * dx > 0 else 0),
                    15 + sg * dy * (R + o), sg * dx, sg * dy, WAKE[1] if o else WAKE[2])
        rig = Rig(15.5 + ex * d, 15.5 + ey * d, ang, 0.56)
        o_, _ = top(rig, paws=((-3.4, 1.0), (3.4, 1.0)), extra=(CLAM_PART,), mood="blink" if k == 3 else "smile",
                    tail=0.8 * math.sin(2 * ph))
        f.update(o_)
        frames.append(finish(f))
    return frames


def we():
    return drift(-90.0)


def ns():
    return drift(0.0)


def nwse():
    return drift(-45.0)


def nesw():
    return drift(45.0)


def no() -> list[dict]:
    """두 앞발로 얼굴을 가린다 — 뒤에 빨간 금지 표지. 사이사이 오른발을 내려 빼꼼 본다"""
    frames = []
    rig = Rig(15.5, 24.5, 0.0, 1.15)
    for k, ph in enumerate(phases()):
        f = {}
        peek = k in (5, 6, 7)
        R = 13.5
        ring = {p for p in disc(15.5, 15.5, R) if math.hypot(p[0] + 0.5 - 15.5, p[1] + 0.5 - 15.5) > R - 2.4}
        slash = set()
        for t in range(-90, 91):
            x, y = 15.5 + t / 100 * (R - 1.5) * 0.7071, 15.5 + t / 100 * (R - 1.5) * 0.7071
            slash |= disc(x, y, 1.3)
        solid(f, ring | slash, SIGN, SIGN_D)
        paws = ((-3.1, -8.4), (3.1, -8.4 + (3.0 if peek else 0)))
        o, _ = top(rig, paws, mood="peek" if peek else "hide", paw=FUR, toes=True, pr=2.1,
                   elbows=((-7.6, -3.6), (7.6, -3.6 + (1.0 if peek else 0))))
        f.update({p: c for p, c in o.items() if p[1] <= 30})
        frames.append(finish(f))
    return frames


def cross() -> list[dict]:
    """앞모습 얼굴 — 수염이 가로 조준선. 머리 위 털 한 가닥과 턱 밑 물방울이 세로선. 코 가운데가 핫스팟"""
    frames = []
    rig = Rig(15.5, 22.6, 0.0, 1.0)   # 얼굴 가운데 (15.5, 14.1) — 코 가운데 칸이 (15, 15)
    for k, ph in enumerate(phases()):
        f = {}
        tw = round(0.6 * math.sin(2 * ph))
        for sg in (-1, 1):
            for x in range(1, 31):
                if (x < 9 or x > 22):
                    f[x, 15] = OUT
            f[15 + sg * 11, 14 - tw] = OUT
            f[15 + sg * 11, 16 + tw] = OUT
        for y in list(range(1, 6)) + list(range(25, 31)):
            f[15, y] = OUT
        out, _ = draw(rig, head_parts())[:2]
        f.update(out)
        face(f, rig, "blink" if k == 8 else "smile")
        frames.append(finish(f))
    return frames


def busy() -> list[dict]:
    """작은 화살표 해달 + 오른쪽 아래 조개 — 둘레를 물방울 여덟이 차례로 돈다(빙글빙글 작업 중)"""
    frames = []
    cx, cy = 22.5, 22.5
    for k, ph in enumerate(phases()):
        f = {}
        head = k * 8 / N
        for i in range(8):
            a = 2 * math.pi * i / 8 - math.pi / 2
            x, y = math.floor(cx + 6.6 * math.cos(a) - 0.5), math.floor(cy + 6.6 * math.sin(a) - 0.5)
            lag = (head - i) % 8
            col = WAKE[1] if lag < 1 else WAKE[2] if lag < 2 else WAKE[3]
            for q in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
                f[q] = col
        f.update(draw(Rig(cx, cy - 1.9, 0.0, 0.9), [CLAM_PART])[0])
        f.update(arrow_otter(ph, small=True))
        frames.append(finish(f))
    return frames


def help_() -> list[dict]:
    """작은 화살표 해달 + 물방울로 찍은 물음표 — 물방울이 글자 차례로 하나씩 부풀었다 돌아온다"""
    frames = []
    cells = [(17.6 + 2.2 * i, 11.6 + 2.2 * j) for j, row in enumerate(QMARK) for i, ch in enumerate(row) if ch == "#"]
    for k, ph in enumerate(phases()):
        f = {}
        m = set()
        for i, (x, y) in enumerate(cells):
            d = (k * len(cells) / N - i) % len(cells)
            m |= disc(x, y, 1.2 + (0.5 if d < 1.5 else 0.0))
        solid(f, m, WAKE[0], BUB)
        f.update(arrow_otter(ph, small=True))
        frames.append(finish(f))
    return frames


def hooded(f: dict, rig: Rig, mood="smile", wave=0.0) -> None:
    """해달 모자를 쓴 사람 아이콘 — 해달 얼굴 · 갈색 후드 · 파란 옷 어깨. 오른팔을 흔든다"""
    shirt, shirt_d = hx("4a7fb5ff"), hx("2e5a88ff")
    hand = (8.0, -6.0 + wave)
    parts = [("hand", ell(*hand, 1.7, 1.7), PAW, True), ("sleeve", bar((5.0, -0.5), hand, 1.6), shirt, False)] + \
        head_parts() + [("hood", ell(0, -8.6, 7.8, 7.2), FUR, False),
                        ("torso", ell(0, 3.0, 7.6, 6.4), lambda a, b: shirt_d if abs(a) < 0.6 else shirt, False)]
    out, _, _ = draw(rig, parts)
    face(out, rig, mood)
    f.update({p: c for p, c in out.items() if p[1] <= 30})


def person() -> list[dict]:
    """작은 화살표 해달 + 해달 모자를 쓴 사람이 손을 흔든다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        hooded(f, Rig(22.5, 25.0, 0.0, 0.66), "blink" if k == 6 else "smile", -2.0 * abs(math.sin(ph)))
        f.update(arrow_otter(ph, small=True))
        frames.append(finish(f))
    return frames


def pin() -> list[dict]:
    """작은 화살표 해달 + 빨간 지도 핀 동그라미 속에 해달 얼굴 — 핀이 통통 튀고, 땅에 닿을 때 눈을 감는다.
    처음엔 해달 머리 밑에 빨간 세모만 달았는데 턱수염 · 넥타이로 읽혀서 핀 동그라미 안에 얼굴을 넣었다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        dy = -round(3 * math.sin(math.pi * k / N))
        cx, cy = 22.5, 13.0 + dy
        for x in range(19, 27):   # 그림자 — 핀이 높을수록 옅게
            f.setdefault((x, 27), WAKE[3] if dy else WAKE[2])
        solid(f, disc(cx, cy, 6.4) | raster([(cx - 4.6, cy + 3.4), (cx + 4.6, cy + 3.4), (cx, cy + 12.6)]),
              SIGN, SIGN_D)
        rig = Rig(cx, cy + 0.6 + 8.5 * 0.56, 0.0, 0.56)
        out, _, _ = draw(rig, head_parts())
        f.update(out)
        face(f, rig, "sleep" if dy == 0 else "smile")
        f.update(arrow_otter(ph, small=True))
        frames.append(finish(f))
    return frames


HAND = Rig(18.6, 18.6, 0.0, 0.85)
HAND_PAW, HAND_PR = (-7.0, -17.4), 2.3


def hand() -> list[dict]:
    """자면서 손잡자고 앞발 하나를 높이 든다(해달은 잘 때 서로 손을 잡는다) — 발바닥 젤리가 보이고,
    머리 위로 z 물방울이 올라간다. 든 앞발 끝이 핫스팟"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        for j in range(2):   # 잠 물방울
            t = (k / N + j / 2) % 1
            bubble(f, 26.0 + 1.5 * t, 8.0 - 5.0 * t, 0.7 + 0.7 * t)
        o, _ = top(HAND, paws=(HAND_PAW, (2.2, -1.2)), mood="sleep", beans=True, toes=True, pr=HAND_PR,
                   elbows=((-8.4, -8.0), None), tail=0.8 * math.sin(ph))
        f.update(o)
        ripple(f, 18.5, 26.0, 12.0, WAKE[3], (0.2, math.pi - 0.2))
        frames.append(finish(f))
    return frames


def ibeam() -> list[dict]:
    """세로 다시마 줄기에 몸을 감고 매달린 해달 — 위아래 다시마 잎이 I 의 가로획. 잎이 살랑인다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        sw = math.sin(ph)
        for y in range(1, 31):
            f[4, y] = KELP
            f[5, y] = KELP_D
        for i, x in enumerate(range(1, 9)):   # 위 잎 · 아래 뿌리
            yy = 1 if (i + round(sw)) % 3 else 2
            f[x, yy] = KELP_L
            f[x, 2] = KELP if x not in (4, 5) else f[x, 2]
            f[x, 29] = KELP
            f[x, 30] = KELP_D
        wrap = ("kelp", bar((-7.5, -1.0), (7.5, 4.5), 1.9), lambda a, b: KELP_L if b < (a + 7.5) * 0.37 - 1.0 else KELP,
                True)
        o, _ = top(Rig(5.0, 20.6, 0.0, 0.54), paws=((-1.6, -3.4), (1.6, -2.2)), mood="blink" if k == 8 else "smile",
                   tail=0.6 * sw, mid=(wrap,))
        f.update(o)
        frames.append(finish(f))
    return frames


TIP, BACK = (1.5, 29.5), (27.6, 14.6)   # 연필심 · 지우개 끝(화면)


def pen() -> list[dict]:
    """연필을 꼭 끌어안고 쓰는 해달 — 연필과 해달이 연필심을 축으로 살짝 까딱인다. 연필심이 핫스팟"""
    frames = []
    base = Rig(21.6, 18.8, 0.0, 0.62)
    L = math.hypot(BACK[0] - TIP[0], BACK[1] - TIP[1])
    ux, uy = (BACK[0] - TIP[0]) / L, (BACK[1] - TIP[1]) / L
    cone = (TIP[0] + ux * 3.6, TIP[1] + uy * 3.6)
    lt, lc, lb = base.local(*TIP), base.local(*cone), base.local(*BACK)
    r = 1.6 / base.k

    def pcol(a, b):
        x, y = base.world(a, b)
        t = (x - TIP[0]) * ux + (y - TIP[1]) * uy
        side_ = -(x - TIP[0]) * uy + (y - TIP[1]) * ux
        if t < 1.4:
            return LEAD
        if t < 3.8:
            return WOOD
        if t > L - 1.8:
            return ERASER
        if t > L - 3.4:
            return FERRULE
        return PENCIL_D if side_ > 0.5 else PENCIL
    pencil = ("pencil", any_of(bar(lt, lc, 0.45 / base.k, r), bar(lc, lb, r)), pcol, True)
    paws = (base.local(TIP[0] + ux * L * 0.64, TIP[1] + uy * L * 0.64 - 0.4),
            base.local(TIP[0] + ux * L * 0.8, TIP[1] + uy * L * 0.8 - 0.4))
    for k, ph in enumerate(phases()):
        d = math.radians(3.0 * math.sin(2 * ph))
        ox, oy = base.ox - TIP[0], base.oy - TIP[1]
        rig = Rig(TIP[0] + ox * math.cos(d) - oy * math.sin(d), TIP[1] + ox * math.sin(d) + oy * math.cos(d),
                  math.degrees(d), base.k)
        f, _ = top(rig, paws=paws, mood="blink" if k == 4 else "smile", mid=(pencil,), tail=0.8 * math.sin(ph))
        f[math.floor(TIP[0]), math.floor(TIP[1])] = LEAD
        frames.append(finish(f))
    return frames


UP = Rig(15.5, 14.6, 0.0, 0.9)   # 앞모습, 머리 꼭대기가 맨 위


def up() -> list[dict]:
    """물 밖으로 몸을 꼿꼿이 세우고 둘레를 살핀다(해달의 잠망경 자세) — 앞발을 가슴에 모으고 비비고,
    허리 둘레로 물결 고리가 퍼지며 턱에서 물방울이 떨어진다. 머리 꼭대기가 핫스팟.
    처음엔 옆모습을 세워 코를 하늘로 들게 했는데 길쭉한 양말 인형 · 부리로 읽혔다"""
    frames = []
    WL = 25
    for k, ph in enumerate(phases()):
        rub = 0.5 * math.sin(2 * ph)              # 앞발 비비기
        o, _ = top(UP, paws=((-1.7 + rub, -1.4), (1.7 + rub, -1.0)), mood="blink" if k == 7 else "smile")
        f = {p: c for p, c in o.items() if p[1] < WL}
        for x in range(4, 28):
            f[x, WL] = WAKE[1]
            f.setdefault((x, WL + 1), WAKE[3] if (x + k) % 3 else WAKE[2])
        t = k / N
        for r0 in (0.0, 0.5):
            ripple(f, 15.5, WL + 1.0, 8.0 + 6.0 * ((t + r0) % 1), WAKE[2], (0.0, math.pi))
        for j in range(2):   # 턱에서 떨어지는 물방울
            tt = (t + j / 2) % 1
            f.setdefault((22 + j, math.floor(12 + 12 * tt * tt)), WAKE[1])
        frames.append(finish({p: c for p, c in f.items() if 1 <= p[0] <= 30 and p[1] <= 30}))   # 고리는 판 안까지만
    return frames


def chevron(f: dict, cx: int, cy: int, dx: int, dy: int, col) -> None:
    """(dx, dy) 쪽을 가리키는 물결 화살촉. 꼭짓점이 (cx, cy)"""
    px, py = -dy, dx
    for i in range(4):
        for s in (-1, 1):
            for w in (0, 1):
                f[cx - dx * (i + w) + s * px * i, cy - dy * (i + w) + s * py * i] = col


def move() -> list[dict]:
    """물 위에서 데굴데굴 도는 해달(한 바퀴에 1초) — 네 방향 물결 화살촉이 바깥으로 두근댄다"""
    frames = []
    for k, ph in enumerate(phases()):
        f = {}
        o = 1 if k % 6 < 3 else 0
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            chevron(f, 15 + dx * (13 + o), 15 + dy * (13 + o), dx, dy, WAKE[1])
        o_, _ = top(Rig(15.5, 15.5, 360.0 * k / N, 0.6), mood="sleep", tail=0.0)
        f.update(o_)
        frames.append(finish(f))
    return frames


SCENE = {"arrow": arrow, "busy": busy, "cross": cross, "hand": hand, "help": help_, "ibeam": ibeam, "move": move,
         "nesw": nesw, "no": no, "ns": ns, "nwse": nwse, "pen": pen, "person": person, "pin": pin, "up": up,
         "wait": wait, "we": we}
HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1),
       "wait": (15, 17), "we": (15, 15), "ns": (15, 15), "nwse": (15, 15), "nesw": (15, 15),
       "no": (15, 15), "cross": (15, 15), "move": (15, 15), "ibeam": (4, 10),
       "pen": (math.floor(TIP[0]), math.floor(TIP[1])),
       # 맨 위 불투명 칸(같으면 왼쪽) — 든 앞발 끝 · 코끝
       "hand": lambda fr: min((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1], p[0])),
       "up": lambda fr: min((p for p, c in fr[0].items() if c[3] == 255), key=lambda p: (p[1], p[0]))}


def check(rid: str, frames: list[dict], hot: tuple) -> None:
    """핫스팟이 장마다 불투명한 칸 위에 있는지"""
    for i, f in enumerate(frames):
        c = f.get(hot)
        if not c or c[3] != 255:
            print(f"  ! {rid} {i}장: 핫스팟 {hot} 이 비었거나 반투명 ({c})")
        if hot == (1, 1) and any(c[3] == 255 and (p[0] < 1 or p[1] < 1) for p, c in f.items()):
            print(f"  ! {rid} {i}장: 코끝보다 왼쪽·위로 나온 칸이 있음")


def main() -> None:
    def job(r):
        def run():
            frames = SCENE[r]()
            hot = HOT[r](frames) if callable(HOT[r]) else HOT[r]
            check(r, frames, hot)
            print(f"  {r} 핫스팟 {hot}")
            return frames, hot
        return run
    write(SID, {r: job(r) for r in SCENE}, sys.argv[1:] or None)


if __name__ == "__main__":
    main()

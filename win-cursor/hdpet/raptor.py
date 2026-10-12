# SPDX-License-Identifier: Apache-2.0
"""아기 랩터(raptoranim) 고화질 — 공룡 틀(dinokit)에 몸빛 · 생김새 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(지운 gen/dino.py)의 짓 그대로: 화살표 뒤에서 빗변을 잡고 빼꼼 · 고개 갸웃 · 볏 쫑긋(화살표),
고개를 갸웃 갸웃 · 끝에서 물음표(기다림), 볏을 바짝 세우고 입을 벌려 캬악(금지).
표식은 뒤통수 위로 쫑긋한 주황 깃 볏 셋 · 길고 가는 주둥이 · 등 줄무늬 · 꼬리 띠 · 뒷발 흰 낫발톱(큰 칸만).
이는 안 그린다(taste.md 톱니 이빨) — 캬악 해도 입만 벌린다.
"""
from . import catkit, register
from .dinokit import (DF, TAIL, TAIL_UP, Hide, Kind, DinoPet, Pose, dino, tail_of, no_sign, arrow_layers, edge_pt, ph_k,
                      H, hx, sin, cos, pi, hypot, atan2, ell, oell, circle, capsule, chain, taper, union, inter, grow, smin,
                      base, part, flat, OUT)

HIDE = Hide(hx("f6d65a"), hx("c9902e"), hx("fcefb8"), hx("f08a4a"))


class RaptorKind(Kind):
    """crest 0–1.4 는 볏을 세운 정도. body 로 틀 몸을 감싸 줄무늬 · 꼬리 띠 · 낫발톱을 얹는다(판 크기 s 를 알아야 해서)"""
    snout = (4.2, 1.2, 4.8, 2.9)                         # 티라노보다 길고 가는 주둥이
    spots = ()                                           # 머리 무늬 대신 등 줄무늬

    def __init__(self, crest=0.0):
        self.crest, self.s = crest, 1.0

    def behind(self, P):
        """뒤통수 위로 쫑긋한 깃 셋 — 한 조각(먹선 하나)이라 작아도 깃마다 금이 안 생긴다.
        반지름은 판에서 먹선 안에 주황이 남게 s 로 나눠 키운다(dinokit 의 max(2.5, 2.0 / s) 셈)"""
        s, c = self.s, self.crest
        ra, rb = max(1.8, 2.3 / s), max(1.2, 1.6 / s)    # 판에서 깃 끝 1.6칸 — 가늘면 먹선이 먹어 갈색 머리털로 읽혔다
        out = []
        fs = []
        for (a, b), L in zip(CREST, (5.0, 4.2, 3.2)):    # 정수리에서 뒤 위로 나란히 쓸린 깃 — 앞 것이 제일 길다
            L += c
            fs.append(taper(a, b, ra, a + CREST_D[0] * L, b + CREST_D[1] * L, rb))
        out.append((P.hf(union(*fs)), H().deco))
        if s >= CLAW_S:                                  # 낫발톱 — 바닥 먹색에 들어가게 여기 넣고, 흰 속은 body 에서 넓힌다
            out.append((claw_f(s, P.step), HI_CLAW))
        return out

    def body(self, F, K, **kw):
        s = F.s
        inner = RaptorKind(self.crest)
        inner.body, inner.s = None, s
        out = dino(F, inner, **kw)
        out[-1:-1] = marks(F, inner, kw)                  # 가까운 팔(맨 끝 층) 밑에
        return out


CREST = ((0.6, -4.6), (-1.6, -4.4), (-3.6, -3.4))       # 깃 뿌리(머리 테 바로 안)
CREST_D = (-0.5, -0.866)                                 # 깃 방향 — 위로 60°, 뒤로 기움(방사형으로 펴면 우파루파 아가미로 읽혔다)
CLAW_S = 0.9                                            # 이보다 작으면 발톱이 먹 점이라 뺀다
HI_CLAW = hx("fffaf0")


def claw_f(s, step):
    """가까운 발 앞에서 위로 솟았다 앞으로 굽는 낫발톱 — 끝은 둥글게(무섭지 않게)"""
    fy = max(1.4, 1.6 / s)
    top = 14.0 - 2 * fy
    pts = [(2.4 + step, top + 0.6), (2.8 + step, top - 0.8), (3.8 + step, top - 1.5), (4.7 + step, top - 1.0)]
    return chain(pts, max(0.75, 0.95 / s), max(0.45, 0.55 / s))


def marks(F, K, kw):
    """등 줄무늬 둘 · 꼬리 띠 둘 · 낫발톱 흰 속 — 납작한 칠, 먹선 안쪽으로 들인다"""
    s = F.s
    C = H()
    ins = 1.0 / s + 0.15                                 # 먹선(판 1칸) 만큼 안으로
    out = []
    bob = kw.get("bob", 0.0)
    by = 8.0 + bob * 0.4
    body = ell(-1.2, by, 5.0 + bob * 0.3, 4.6 - bob * 0.4)
    P = Pose(kw.get("nod", 0.0))
    head = P.hf(smin(1.4, ell(*K.head), ell(*K.snout)))
    if s >= 0.55:
        w = max(0.6, 0.8 / s)
        bands = union(*[capsule(u, by - 5.4, u + 1.2, by - 1.6, w) for u in (-5.2, -2.9)])
        g = inter(inter(bands, grow(body, -ins)), lambda x, y, h=head: ins - h(x, y))
        out.append(flat(F.f(g), C.dark))
    if s >= 0.6:
        tp = tail_of(kw.get("tail_pts") or TAIL, kw.get("sway", 0.0))
        tl = chain(tp, max(2.5, 2.0 / s), max(0.9, 1.5 / s))
        segs = [hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(tp, tp[1:])]
        rr = max(0.75, 0.85 / s)
        rings = []
        for t in (0.5, 0.8):
            d = t * sum(segs)
            for (a, b), L in zip(zip(tp, tp[1:]), segs):
                if d <= L:
                    rings.append(circle(a[0] + (b[0] - a[0]) * d / L, a[1] + (b[1] - a[1]) * d / L, rr))
                    break
                d -= L
        g = inter(inter(union(*rings), grow(tl, -ins)), lambda x, y: ins - body(x, y))
        out.append(flat(F.f(g), C.dark))
    if s >= CLAW_S:
        out.append(flat(F.f(grow(claw_f(s, kw.get("step", 0.0)), -0.38 / s)), HI_CLAW))
    return out


K = RaptorKind()


def sc_arrow(fr, g):
    """화살표 오른쪽 어깨 뒤에서 왼쪽(끝)을 보고 빼꼼 — 앞발 둘을 빗변에 걸고 고개를 갸웃, 볏이 쫑긋. 화살표가 위.
    머리 자리는 흰냥이 빼꼼과 같은 약속(빗변 0.797 자리에서 바깥 테 + 6.75)이라 모양 탭(shaped)이 잰 판 안에 든다"""
    ph, k = ph_k(fr)
    s = 0.74
    cx, cy = edge_pt(g, 0.797, 6.75)
    lift = 0.5 * (1 - cos(ph)) / 2
    F = DF(cx, cy - lift, s, fx=-1)
    out = dino(F, RaptorKind(crest=0.9 if k % 4 == 0 else 0.0), "blink" if k == 7 else "open", nod=0.16 * sin(ph),
               arm=1.6, sway=0.7 * sin(ph), tail_pts=TAIL_UP, look=0.8)
    out += arrow_layers(g)
    for t in (0.79, 0.92):
        out += hand(*edge_pt(g, t, 0.9), *g["u"])
    return out


def hand(cx, cy, ux, uy):
    """빗변(방향 (ux, uy))에 건 앞발 — 냥이 앞발(1.75 × 1.4)은 판에서 먹선 안에 노랑이 안 남아 흰 테 고리로 보여서 키웠다.
    발가락 금 둘이 빗변 쪽으로"""
    C = H()
    nx, ny = uy, -ux
    p = oell(cx, cy, 2.3, 1.8, atan2(uy, ux))
    out = [part(p, C.base, sh=0.0, line=0.7)]            # 바닥(base)을 안 깐다 — 크림 테가 크림 화살표 위에서 도넛 고리로 보였다
    for d in (-0.75, 0.75):
        bx, by = cx + ux * d, cy + uy * d
        out.append(flat(capsule(bx - nx * 0.2, by - ny * 0.2, bx - nx * 1.0, by - ny * 1.0, 0.17), C.out, 0.85))
    return out


TILT = (0, 8, 14, 14, 8, 0, -8, -14, -14, -8, 0, 0)       # 갸웃(도) — 픽셀 판 그대로


def qmark(cx, cy, a=1.0):
    """주황 물음표 — 갈고리 + 점"""
    hook = chain([(cx - 1.7, cy - 2.0), (cx - 0.9, cy - 3.3), (cx + 0.7, cy - 3.5), (cx + 1.8, cy - 2.4), (cx + 1.5, cy - 1.0),
                  (cx + 0.2, cy - 0.1), (cx, cy + 1.0)], 0.95)
    dot = circle(cx, cy + 3.0, 1.05)
    f = union(hook, dot)
    C = H()
    return [base(f), part(f, C.deco, shade=C.deco_d, line=0.5)]


def sc_wait(fr):
    """고개를 갸웃 갸웃 — 끝까지 기울면 볏이 서고 주둥이 위에 물음표"""
    ph, k = ph_k(fr)
    t = TILT[k]
    out = dino(DF(16.6, 14.0, 1.1), RaptorKind(crest=0.6 if abs(t) == 14 else 0.0), "blink" if k == 10 else "open",
               nod=t * pi / 180, sway=1.0 * sin(ph), look=0.3 * (1 if t >= 0 else -1))
    if abs(t) == 14:
        out += qmark(26.4, 5.2)
    return out


def brows(F, K, nod):
    """화난 눈썹 — 눈 위에서 주둥이 쪽으로 내려온다(dface 의 눈 자리 그대로)"""
    s = F.s
    P = Pose(nod)
    er = max(1.15 * s, 0.95)
    out = []
    for u, v, k in ((0.2, -0.3, 0.86), (4.0, 0.0, 1.0)):
        rc = er * k / s                                  # 눈 반지름(캐논)
        a = F.w(*P.hp(u - 1.1 * rc, v - 2.0 * rc))
        b = F.w(*P.hp(u + 1.0 * rc, v - 1.25 * rc))
        out.append(flat(capsule(*a, *b, max(0.36, 0.25 * er * k)), OUT))
    return out


def sc_no(fr):
    """금지 표지 안에서 볏을 바짝 세우고 '캬악' — 입을 벌리고 발톱 팔을 치켜든다(이는 없음). 표지가 위"""
    ph, k = ph_k(fr)
    hiss = k % 6 in (1, 2, 3)
    nod = -0.12 if hiss else 0.0
    F = DF(16.4, 11.8, 0.66)
    out = dino(F, RaptorKind(crest=1.4 if hiss else 0.2), "open", nod=nod, mouth=0.9 if hiss else 0.0,
               arm=2.6 if hiss else 0.6, arm_far=2.0 if hiss else 0.3, sway=0.6 * sin(ph), tail_pts=TAIL_UP)
    out += brows(F, K, nod)
    return out + no_sign()


class Raptor(DinoPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Raptor(HIDE, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no}, hot={"wait": (13, 12)})

register("raptor", PET)
catkit.load()

# SPDX-License-Identifier: Apache-2.0
"""댕댕이 · 애니 고화질 공용 틀 — 앞모습으로 앉은 치비 개(머리가 몸만 한 통통 강아지) · 스티커 채색은 냥이 틀(catkit) 그대로.

픽셀 판(gen/dog.py · dog_front.py)이 귀여운 까닭 — 둥근 큰 머리, 밝은 주둥이 판 위의 위가 넓은 까만 코(고양이와 가르는
첫 표시), 낮고 넓게 벌린 까만 콩 눈, 눈 밑 분홍 볼, 작은 몸 · 앞발 둘 — 을 HD 로 옮겼다. 견종마다 다른 것은 털빛(Fur)과
생김새(Kind — 귀 · 꼬리 · 주둥이 · 털 물결 · 무늬 갈고리)와 기다림 · 금지 두 칸이다. 화살표(앞모습으로 앉아 대 끝을
왼 입꼬리에 물고 꼬리 붕붕)와 나머지 14칸은 여기 하나다 — 픽셀 판도 화살표는 견종 데이터만 갈아 끼웠다.
좌표는 art 좌표(32칸, 핫스팟 칸 가운데 = 칸 + 0.5). 개 제 좌표(캐논)는 머리 가운데 (0, 0), 아래가 +v, 앞(화면)을 본다.

공룡 · 새 틀은 읽지 않는다 — 읽으면 일감 해시가 그 파일을 따라가(build._pet_files) 그 틀을 고칠 때 개 열 마리까지 다시
굽는다. 금지 표지 · 땀 같은 작은 도우미는 그래서 베껴 왔다. catkit 은 고치지 않는다(냥이 열 마리 재료).
털빛은 catkit 전역 C 에 끼워 쓴다(use).
"""
import math

from hd import circle, capsule, rbox, ring, arc, grow, smin, union, poly, turn, lerp, clamp, smooth, TAU  # noqa: F401

from . import catkit
from .catkit import (hx, ell, oell, inter, clip_y, rpoly, chain, taper, Frame, layer, base, part, flat, soft,  # noqa: F401
                     cur, small_arrow, ARROW, TIP, cream_of, shaped, HI_WHITE, HI, PINK, NF, Pet, shut, Coat, use,
                     paw_print, chevron)

sin, cos, hypot, pi, atan2, radians = math.sin, math.cos, math.hypot, math.pi, math.atan2, math.radians

# 댕댕이 묶음 공통(픽셀 판 팔레트 그대로)
OUT, EYE, NOSE = hx("3a2a30"), hx("2a1c22"), hx("1e1418")
RIM_WARM, RIM_GREY = hx("f6e9d2"), hx("d9dde3")
CHEEK, TONGUE, TONGUE_D, MOUTH = hx("f4a0b0"), hx("f27a8a"), hx("d65a70"), hx("7a2c3a")
BALL, BALL_D, BALL_W = hx("d4e04a"), hx("a8b830"), hx("fffbe8")
LEASH, LEASH_D = hx("4a7fb5"), hx("2e5a88")
RIBBON, RIBBON_D = hx("ff7aa8"), hx("d24f80")
BLUE = hx("5aaee8")
MARK = hx("8a7f88")
BONE, BONE_D = hx("fbf1dc"), hx("e2cfa6")
PAD, PAD_L, CLIP = hx("f07c92"), hx("f8b8c6"), hx("c4ccd6")
SKIN, SKIN_D, HAIR, SHIRT, SHIRT_D = hx("f7d7bc"), hx("e8bfa0"), hx("6b4630"), hx("5aa26a"), hx("3f7d4d")
PEN_Y, PEN_YD, PEN_W, PEN_G, PEN_E, PEN_F = hx("f5c842"), hx("c8961c"), hx("efd2a8"), hx("3a3a3a"), hx("f2a0a8"), hx("b8b8c0")
SIGN, SIGN_D, SIGN_L = hx("d64541"), hx("9e2b28"), hx("ef7a72")
SWEAT, SWEAT_D = hx("9fd4f4"), hx("5a9cc8")


class Fur(Coat):
    """털빛 하나 — base(털) · dark(짙은 털: 늘어진 귀 · 무늬) · light(밝은 털: 주둥이 · 가슴 · 양말) · inner(쫑긋 귀 속).
    rim 은 바깥 테(따뜻한 크림 · 흰 개는 회색), iris 는 눈 색(허스키만 파랑)"""

    def __init__(self, fur, dark, light, inner, rim=RIM_WARM, iris=EYE):
        super().__init__(fur, lerp(fur, dark, 0.5), OUT, EYE, rim, ((EYE,) * 3,) * 2, ear=inner, cheek=CHEEK, nose=NOSE,
                         nose_l=hx("4a3a40"), jelly=PAD, tongue=TONGUE)
        self.dark, self.light, self.inner, self.iris_c = dark, light, inner, iris


def H():
    return catkit.C


# ---- 견종마다 다른 것: 생김새 ----

class Kind:
    """한 마리의 생김새. 갈고리는 다 캐논 거리함수를 (f, 색) 짝 목록으로 돌려준다.
      marks()   머리 위 무늬(시바 우라지로 · 코기 흰 줄 · 허스키 가면) — 머리 안으로 잘라 납작하게, 머리와 같이 갸웃
      over()    머리 위 장식(말티즈 리본 · 푸들 방울 머리) — 머리와 같이 갸웃
      behind()  머리 뒤 · 몸 앞(포메 목털)
    ear: prick(쫑긋) · small(작은 쫑긋) · drop(늘어짐) · poof(곱슬 뭉치) · hair(긴 털) · none
    tail: curl · plume · feather · thin · pom · fluff · pompom · stub(앞에서 안 보임)"""
    ear, ear_s, ear_len, ear_dark = "prick", 1.0, 1.0, False
    tail = "curl"
    fluffy = 0.0                   # 털 물결 깊이(캐논) — 포메 · 비숑 · 푸들
    snout = 1.0                    # 주둥이 길이 배(닥스훈트 · 진돗개가 김)
    muzzle = True                  # 밝은 주둥이 판
    bib = True                     # 밝은 가슴
    sock = False                   # 밝은 발
    mouth = "smile"

    def marks(self):
        return []

    def over(self):
        return []

    def behind(self):
        return []


def wob(g, amp, cx, cy, n, ph=0.0):
    """털 물결 — 가장자리를 n 번 물결치게 부풀린다(거리 어림이 amp 만큼 틀림)"""
    return lambda x, y: g(x, y) - amp * (0.5 + 0.5 * cos(n * atan2(y - cy, x - cx) + ph))


class Pose:
    """머리 갸웃(tilt, 라디안, + 가 시계) 둘레 목(piv). hf 는 머리 조각 거리함수를, hp 는 머리 점을 갸웃인다"""

    def __init__(self, tilt=0.0, piv=(0.0, 5.0)):
        self.tilt, self.piv = tilt, piv

    def hf(self, g):
        return turn(g, self.tilt, *self.piv) if self.tilt else g

    def hp(self, u, v):
        if not self.tilt:
            return u, v
        c, s = cos(self.tilt), sin(self.tilt)
        du, dv = u - self.piv[0], v - self.piv[1]
        return self.piv[0] + du * c - dv * s, self.piv[1] + du * s + dv * c


def head_f(K, squish=0.0):
    g = smin(1.6, ell(0, -0.5, 6.8, 5.7 - squish), ell(0, 1.6 + squish * 0.3, 7.1, 4.4))   # 아래 볼이 넓은 호빵 — V 면 여우
    return wob(g, K.fluffy, 0.0, 0.5, 13) if K.fluffy else g


def ears(K, flap=(0.0, 0.0)):
    """[(f, 색, 속 f 또는 None, 앞)] — 앞이면 머리 위에 그린다(늘어진 귀 · 곱슬 뭉치 · 긴 털). flap 은 귀 끝을 바깥으로(젖힘)"""
    C = H()
    out = []
    for sg in (-1, 1):
        fl = flap[(sg + 1) // 2]
        col = C.dark if K.ear_dark else C.base
        if K.ear in ("prick", "small"):
            k = K.ear_s * (0.7 if K.ear == "small" else 1.0)
            b0, b1 = (sg * 6.9, -1.0), (sg * 1.4, -4.6)      # 낮고 밑변 넓게, 바깥으로 벌림 — 크고 곧으면 여우 · 고양이
            mx, my = (b0[0] + b1[0]) / 2, (b0[1] + b1[1]) / 2
            tx, ty = sg * (6.9 + fl * 2.0), -9.0 + fl * 1.6
            pts = [b0, (mx + (tx - mx) * k, my + (ty - my) * k), b1]
            cx, cy = sum(p[0] for p in pts) / 3, sum(p[1] for p in pts) / 3 + 0.5
            inner = rpoly([(cx + (x - cx) * 0.5, cy + (y - cy) * 0.5) for x, y in pts], 0.45)
            out.append((rpoly(pts, 1.5), col, inner, False))
        elif K.ear == "drop":
            L = K.ear_len
            out.append((taper(sg * 6.2, -3.6, 2.3, sg * (7.6 + fl), -3.4 + 6.2 * L, 2.7), C.dark, None, True))
        elif K.ear == "poof":
            out.append((wob(ell(sg * 7.4, 1.4, 2.9, 3.8), 0.4, sg * 7.4, 1.4, 9), col, None, True))
        elif K.ear == "hair":
            out.append((wob(taper(sg * 5.8, -3.6, 2.6, sg * (7.6 + fl), 5.6, 3.0), 0.3, sg * 7.0, 1.0, 11), col, None, True))
    return out


def tail_fs(K, w=0.0):
    """앉은 개 오른쪽 뒤로 보이는 꼬리 — [(f, 색)]. w 는 흔든 정도(-1–1)"""
    C = H()
    t = K.tail
    if t in ("curl", "plume"):                       # 등 위 도넛 — 머리 오른쪽 밑에 원판, 가운데 말린 끝(밝은 털, 먹선 없음)
        k = 1.0 if t == "curl" else 1.2
        cx, cy = 8.4 + 0.5 * w, 6.4
        return [(chain([(4.0, 9.2), (cx - 0.6, cy + 1.2)], 1.8), C.base), (circle(cx, cy, 2.9 * k), C.base),
                (circle(cx - 0.2, cy - 0.3, 1.25 * k), C.light, True)]
    if t in ("feather", "thin"):
        r0, r1 = (1.8, 1.3) if t == "feather" else (1.15, 0.7)
        pts = [(4.4, 10.8), (8.4, 10.6), (10.8, 8.2 + 1.2 * w), (11.6 + 0.3 * w, 5.4 + 2.0 * w)]
        g = chain(pts, r0, r1)
        out = [(g, C.base)]
        if t == "feather":                           # 깃털 술 — 밑으로 밝은 털
            out.append((inter(g, lambda x, y: (8.6 + 0.12 * (x - 4.4) ** 1.0) - y - (x - 10.0) * 0.6), C.light))
        return out
    if t == "pom":
        return [(wob(ell(7.4 + 0.6 * w, 4.4, 3.8, 3.3), 0.4, 7.4 + 0.6 * w, 4.4, 9), C.base)]
    if t == "fluff":
        return [(wob(ell(6.8 + 0.6 * w, 6.2, 3.1, 2.8), 0.35, 6.8 + 0.6 * w, 6.2, 8), C.base)]
    if t == "pompom":
        end = (9.2 + 0.8 * w, 3.0)
        return [(chain([(4.4, 9.4), (7.6, 7.2), end], 0.95, 0.85), C.base),
                (wob(circle(end[0], end[1] - 0.6, 2.5), 0.35, end[0], end[1] - 0.6, 8), C.base)]
    return []


def body_f(K, bob=0.0):
    g = ell(0, 7.9 + bob * 0.3, 5.5 + bob * 0.25, 4.6 - bob * 0.3)
    return wob(g, K.fluffy * 0.8, 0.0, 7.9, 11, 0.7) if K.fluffy else g


def dog(F, K, mood="open", mouth=None, look=0.0, tilt=0.0, wag=0.0, bob=0.0, body=True, paws=True, tail=True,
        arms=(), flap=(0.0, 0.0), tongue=0.0, face_on=True, extra_under=(), stand=False, spin=0.0):
    """앉은 치비 개 → 레이어 목록. 캐논: 머리 (0, 0) 넓이 ±7 · 귀 끝 v ≈ -10 · 몸 (0, 7.9) · 발바닥 v ≈ 13.
    mood: open · blink · happy · squeeze(><) · sad · sulk · wink. mouth 는 K.mouth 를 바꿔 끼운다
    (smile · tongue · pant · open · O · flat · none). arms = [(어깨 (u, v), 발 (u, v), 젤리 보임)] — 머리 위에 그린다.
    stand 면 뒷발로 선 몸(길쭉한 몸 · 뒷발 둘)"""
    s = F.s
    C = H()
    P = Pose(tilt)
    under = []                                                   # (f, 색) — 머리 아래
    if tail:                                                     # spin: 꼬리 밑동 둘레로 돌린다(프로펠러)
        under += [((turn(g, spin, 4.2, 9.4) if spin else g), *rest) for g, *rest in tail_fs(K, wag)]
    if stand:
        bd = ell(0, 8.6, 4.6, 5.6)
        if K.fluffy:
            bd = wob(bd, K.fluffy * 0.8, 0.0, 8.6, 11, 0.7)
        under.append((bd, C.base))
        for sg in (-1, 1):
            under.append((ell(sg * 2.6, 14.0, 2.2, 1.4), C.light if K.sock else C.base))
    elif body:
        under.append((body_f(K, bob), C.base))
    if body and K.bib and not stand:
        bib = (inter(body_f(K, bob), ell(0, 6.6, 2.9, 3.6)), C.light)
    elif stand and K.bib:
        bib = (inter(ell(0, 8.6, 4.6, 5.6), ell(0, 7.6, 2.8, 4.0)), C.light)
    else:
        bib = None
    if paws and body and not stand:
        for sg in (-1, 1):
            under.append((ell(sg * 2.5, 11.55, 2.0, 1.45), C.light if K.sock else C.base))
    under += list(extra_under)
    beh = K.behind()
    es = ears(K, flap)
    hd_ = head_f(K, bob * 0.35)
    ov = K.over()
    arm_fs = []
    for sh_, hand, jelly in arms:
        ra = max(2.0, 1.6 / s)                                   # 먹선이 1칸이라 가늘면 까만 매듭이 된다
        a = taper(sh_[0], sh_[1], ra * 1.08, hand[0], hand[1], ra * 0.95)
        p = ell(hand[0], hand[1], ra * 1.1, ra * 1.0)
        arm_fs.append((a, p, hand, jelly))
    head_parts = [P.hf(g) for g in [e[0] for e in es] + [hd_] + [b[0] for b in beh] + [o[0] for o in ov]]
    allf = [u[0] for u in under] + head_parts + [g for a, p, _, _ in arm_fs for g in (a, p)]
    out = [base(*[F.f(g) for g in allf])]
    for g, col, *fl in under:                                    # (f, 색, True) 는 먹선 없이 — 작은 조각이 까만 점이 된다
        out.append(flat(F.f(g), col) if fl else part(F.f(g), col))
    if bib:
        out.append(flat(F.f(grow(bib[0], -0.9)), bib[1]))
    for g, col in beh:
        out.append(part(F.f(P.hf(g)), col))
    for g, col, inner, front in es:                              # 쫑긋 귀는 머리 뒤
        if not front:
            out.append(part(F.f(P.hf(g)), col, line=0.7))           # 먹선이 1칸이면 32 에서 귀 속이 안 남는다
            if inner and s >= 0.8:                               # 작으면 귀 속이 먹선과 뭉쳐 어두운 귀(레서판다)가 된다
                out.append(flat(F.f(P.hf(inner)), C.inner))
    out.append(part(F.f(P.hf(hd_)), C.base))
    in_head = grow(hd_, 1.0)                                     # 무늬가 먹선을 안 덮게 안으로
    for g, col in K.marks():
        out.append(flat(F.f(P.hf(inter(g, in_head))), col))
    if K.muzzle:
        sn = K.snout
        mz = inter(ell(0, 2.6 + 0.5 * (sn - 1), 3.0, 2.2 * sn), in_head)   # 넓으면 32 에서 흰 볼수염(여우 · 레서판다)
        out.append(flat(F.f(P.hf(mz)), C.light))
    for g, col, inner, front in es:                              # 늘어진 귀 · 털 귀는 머리 위
        if front:
            out.append(part(F.f(P.hf(g)), col))
    for g, col in ov:
        out.append(part(F.f(P.hf(g)), col))
    if face_on:
        out += dface(F, K, P, mood, mouth, look, tongue)
    for a, p, hand, jelly in arm_fs:
        out.append(part(F.f(a), C.base, sh=0.0, line=0.75))
        out.append(part(F.f(p), C.light if K.sock else C.base, sh=0.0, line=0.75))
        if jelly:
            out += catkit.jellies(F, hand)
    return out


def dface(F, K, P, mood="open", mouth=None, look=0.0, tongue=0.0):
    """앞얼굴: 눈은 머리 가운데 높이로 넓게(±3.3) · 바로 밑 분홍 볼 · 주둥이 판 위 위가 넓은 까만 코 · 그 밑 ω 입.
    눈은 까만 콩 + 왼쪽 위 흰 반짝 — 32 에서도 2px 남게 판 단위로 바닥을 둔다. 코와 입은 작아지면 덜 줄인다(kn)"""
    s = F.s
    C = H()
    mouth = K.mouth if mouth is None else mouth
    sn = K.snout
    out = []
    er = max(1.12 * s, 0.95)
    for sg in (-1, 1):                                           # 볼 먼저(눈 아래 깔림)
        bx, by = F.w(*P.hp(sg * 4.8, 2.3))
        rx = max(1.35 * s, 0.85)
        out.append(soft(ell(bx, by, rx, rx * 0.6), C.cheek, 0.8))
    for sg in (-1, 1):
        ex, ey = F.w(*P.hp(sg * 3.3 + 0.4 * look, -0.3))
        r = er
        closed = mood in ("blink", "happy") or (mood == "wink" and sg > 0)
        if closed:
            out.append(shut(ex, ey, r * 1.05, "happy" if mood in ("happy", "wink") else "blink"))
        elif mood == "squeeze":                                  # >< — 왼눈 > · 오른눈 <
            d = -sg
            w = max(0.3, 0.22 * r)
            out.append(flat(union(capsule(ex - d * r * 0.8, ey - r * 0.75, ex + d * r * 0.55, ey, w),
                                  capsule(ex + d * r * 0.55, ey, ex - d * r * 0.8, ey + r * 0.75, w)), C.eye))
        elif mood == "sulk":                                     # 흥 — 바깥이 높은 짧은 빗금
            g = capsule(ex + sg * r * 0.85, ey - r * 0.35, ex - sg * r * 0.75, ey + r * 0.3, max(0.3, 0.24 * r))
            out.append(flat(g, C.eye))
        else:
            ic = C.iris_c
            out.append(flat(ell(ex, ey + (r * 0.15 if mood == "sad" else 0.0), r * 0.82, r), ic,
                            line=0.32 if ic != EYE else 0.0, ink=C.eye))
            out.append(flat(circle(ex - 0.28 * r, ey - 0.36 * r, max(0.34 * r, 0.3)), HI))
            if mood == "sad":                                    # 처진 눈썹 — 안쪽이 높다
                out.append(flat(capsule(ex + sg * r * 0.95, ey - r * 1.25, ex - sg * r * 0.7, ey - r * 1.75,
                                        max(0.22, 0.16 * r)), C.eye, 0.9))
    kn = max(1.0, 0.6 / s)                                       # 작으면 코 · 입을 덜 줄인다
    ny0 = 1.15 + 0.6 * (sn - 1)

    def at(g):                                                   # 코 둘레 kn 배
        return F.f(P.hf(lambda u, v: g(u / kn, ny0 + (v - ny0) / kn) * kn))
    nose = rpoly([(-1.35, ny0 - 0.62), (1.35, ny0 - 0.62), (0.0, ny0 + 0.85)], 0.45)
    my = ny0 + 0.85
    if mouth in ("smile", "tongue"):
        out.append(flat(at(capsule(0.0, ny0 + 0.4, 0.0, my + 0.35, 0.2)), C.out, 0.95))
        for sg in (-1, 1):
            out.append(flat(at(arc(sg * 0.78, my + 0.15, 0.78, 0.2, pi * 0.08, pi * 0.84)), C.out, 0.95))
        if mouth == "tongue" or tongue:
            tl = 1.1 + 0.8 * tongue
            tg = smin(0.3, ell(0.35, my + 0.9 + tl * 0.4, 0.85, tl * 0.5), circle(0.35, my + 0.7 + tl, 0.85))
            out.append(flat(at(tg), TONGUE, line=0.24, ink=TONGUE_D))
    elif mouth in ("pant", "open", "O"):
        if mouth == "O":
            g = ell(0.0, my + 1.1, 0.9, 1.15)
        elif mouth == "open":
            g = smin(0.4, ell(0.0, my + 1.0, 1.7, 1.3), ell(0.0, my + 0.4, 1.2, 0.6))
        else:
            g = ell(0.0, my + 0.8, 1.45, 0.95)
        out.append(flat(at(g), MOUTH, line=0.3, ink=C.out))
        tl = 0.7 + (0.9 + 0.5 * tongue if mouth == "pant" else 0.0)
        tg = inter(smin(0.3, ell(0.0, my + 1.4, 1.0, 0.7), circle(0.0, my + 0.9 + tl, 0.95)),
                   (lambda u, v: -1.0) if mouth == "pant" else grow(g, 0.0))
        if mouth != "O":
            out.append(flat(at(tg), TONGUE, line=0.22, ink=TONGUE_D))
    elif mouth == "flat":
        out.append(flat(at(capsule(-0.9, my + 0.5, 0.9, my + 0.5, 0.2)), C.out, 0.95))
    out.append(flat(at(nose), C.nose))
    if s >= 0.5:
        out.append(flat(at(ell(-0.45, ny0 - 0.15, 0.42, 0.26)), HI, 0.85))
    return out


# ---- 소품 ----

def drop(x, y, r=1.0, h=1.4):
    """땀방울 — 꼭지가 위"""
    f = smin(0.3, circle(x, y + 0.5, r), poly([(x, y - h), (x - r * 0.8, y + 0.4), (x + r * 0.8, y + 0.4)]))
    return [base(f), part(f, lambda px, py: lerp(HI, SWEAT, smooth(y - 0.6, y + 0.8, py)), shade=SWEAT_D, ink=SWEAT_D, line=0.45)]


def no_sign(C_=14.5, R=12.5):
    """빨간 금지 표지(고리 + 빗금) — 개 위에 칠한다"""
    g = union(ring(C_, C_, R - 1.25, 1.25), capsule(C_ - 7.7, C_ - 7.7, C_ + 7.7, C_ + 7.7, 1.35))
    return [base(g), part(g, lambda x, y: lerp(SIGN_L, SIGN, smooth(C_ - 10, C_ - 4, y + 0.5 * x - 0.5 * C_)), shade=SIGN_D,
                          ink=SIGN_D, line=0.8)]


def ball(cx, cy, r=2.2, a=0.0):
    """테니스공 — 흰 솔기 곡선 하나"""
    b = circle(cx, cy, r)
    c, s_ = cos(a), sin(a)

    def seam(x, y):
        u, v = (x - cx) * c + (y - cy) * s_, -(x - cx) * s_ + (y - cy) * c
        return abs(hypot(u + r * 1.15, v) - r * 0.95) - r * 0.13
    return [base(b), part(b, BALL, shade=BALL_D, ink=hx("6a7418"), line=0.6), flat(inter(seam, grow(b, 0.5)), BALL_W)]


def bone_f(cx, cy, L, ang=0.0, r=0.95, knob=1.3):
    """뼈다귀 하나: 줄기 + 양끝 마디 둘씩"""
    ux, uy = cos(ang), sin(ang)
    a, b = (cx - ux * L / 2, cy - uy * L / 2), (cx + ux * L / 2, cy + uy * L / 2)
    out = [capsule(*a, *b, r)]
    for (px, py), d in ((a, -1), (b, 1)):
        for sg in (-1, 1):
            out.append(circle(px + d * ux * 0.3 - uy * sg * knob * 0.75, py + d * uy * 0.3 + ux * sg * knob * 0.75, knob))
    return union(*out)


def bone_layers(f):
    return [base(f), part(f, BONE, shade=BONE_D, ink=hx("8a6e4a"), line=0.8)]


def marks(pts, a=0.9):
    """움직임 줄 — [(x0, y0, x1, y1)]"""
    return [flat(capsule(*p, 0.28), MARK, a) for p in pts]


# ---- 화살표: 물어오기 (핫스팟 (1, 1)) ----
# 앞모습으로 앉은 개(오른쪽 아래) · 크림 화살표를 끝(1, 1)을 축으로 눕혀 대 끝이 왼 입꼬리에 닿게 하고 대를 늘인다(aim).
# 머리를 지나는 대는 머리 뒤로 숨고 입꼬리 둘레에서만 보인다 — 대가 얼굴에 빗금을 긋지 않게(픽셀 판 dog_front 의 hide).
# 화살표 머리는 늘 다 보인다(개보다 위에 칠함).

A_SC = 1.0                         # 화살표 배율
STEM = ((4.4 + 7.4) / 2, (14.8 + 13.6) / 2), ((7.6 + 10.6) / 2, (21.8 + 20.4) / 2)   # 대 가운데 줄: 뿌리(홈) · 끝
DOG_O, DOG_S = (20.6, 18.6), 0.74  # 개 머리 가운데(art) · 배율
BITE = (-1.7, 3.15)                # 왼 입꼬리(캐논)
TILT = radians(8.0)                # 머리 갸웃(+ 시계) — 왼 입꼬리가 화살표 쪽으로 들린다
POKE = 1.1                         # 입꼬리 둘레 몇 칸만 대를 얼굴 위에 보이나 — 2.2 는 대 굵기(3.3)째 왼눈까지 덮었다


def aim(m):
    """대 가운데 줄이 m 을 지나게 화살표를 끝을 축으로 돌리고(rot), 대 끝이 m 에 오게 늘인다(ext) — 화살표 점(art)"""
    (ax, ay), (bx, by) = STEM
    am = atan2(m[1] - TIP[1], m[0] - TIP[0])
    best = None
    for i in range(-400, 101):
        rot = radians(i / 10)
        c, s_ = cos(rot), sin(rot)
        rx, ry = (ax * c - ay * s_) * A_SC, (ax * s_ + ay * c) * A_SC         # 홈 가운데(끝 기준)
        dx, dy = ((bx - ax) * c - (by - ay) * s_), ((bx - ax) * s_ + (by - ay) * c)
        n = hypot(dx, dy)
        dx, dy = dx / n, dy / n
        wx, wy = m[0] - TIP[0] - rx, m[1] - TIP[1] - ry
        off = abs(wx * dy - wy * dx)
        if wx * dx + wy * dy > 0 and (best is None or off < best[0]):
            best = (off, rot, (wx * dx + wy * dy) / A_SC - n)
    _, rot, ext = best
    c, s_ = cos(rot), sin(rot)
    ux, uy = (bx - ax), (by - ay)
    n = hypot(ux, uy)
    pts = [(x + ux / n * ext, y + uy / n * ext) if i in (3, 4) else (x, y) for i, (x, y) in enumerate(ARROW)]
    del am
    return [(TIP[0] + (x * c - y * s_) * A_SC, TIP[1] + (x * s_ + y * c) * A_SC) for x, y in pts]


_AIM = {}


def fetch(K, fr):
    """앞모습으로 앉아 화살표 대 끝을 왼 입꼬리에 물고 꼬리 붕붕 — 꼬리는 1초 세 번 크게, 한 번 끔뻑"""
    ph, k = ph_k(fr)
    F = Frame(*DOG_O, DOG_S)
    bite = F.w(*Pose(TILT).hp(*BITE))
    if K not in _AIM:
        _AIM[K] = aim(bite)
    pts = _AIM[K]
    arw = rpoly(pts, 0.5)
    w = sin(3 * ph)
    # 화살표를 개 뒤에 깔고 입꼬리 조각만 위에 얹는다(바닥 없이) — 머리로 깎은 거리함수에 바닥을 주면 바깥 테가 깎인
    # 자리를 따라 얼굴 위로 번졌다. 화살표 머리는 개와 안 겹치므로 늘 다 보인다
    out = cur([base(arw), part(arw, cream_of, sh=0.0)])
    out += dog(F, K, "blink" if k == 7 else "open", look=-0.5, tilt=TILT, wag=1.6 * w)                # 입은 결 것(시바는 혀) — 웃는 입만이면 32 에서 여우
    poke = inter(arw, circle(*bite, POKE))
    out += cur([part(poke, cream_of, sh=0.0, line=0.6)])
    return out


def peek(K, fr, g):
    """모양 탭: 냥이처럼 빗변 뒤에서 고개를 쏙 — 두 앞발이 빗변을 잡는다(catkit.peek_shape 와 같은 자리)"""
    ph = TAU * fr
    cx, cy = g["cat"]
    lift = 0.5 * (1 - cos(ph)) / 2
    F = Frame(cx, cy + 1.5 - lift, 0.8)                         # 개 귀가 냥이 귀보다 1.3칸 높아 판 위에 닿았다
    out = dog(F, K, "blink" if catkit.blink_of(fr) else "open", look=-0.6, paws=False, wag=0.8 * sin(ph))
    if g["band"]:
        out += cur([base(g["outer"]), part(g["outer"], HI_WHITE, sh=0.0), part(g["body"], cream_of, line=0.0)])
    else:
        out += cur([base(g["body"]), part(g["body"], cream_of)])
    C = H()
    ux, uy = g["u"]
    for t in (0.659, 0.798):
        px, py = catkit._edge(g, t, 0.6)
        p = oell(px, py, 1.75, 1.4, atan2(uy, ux))
        out += [base(p), part(p, C.light if K.sock else C.base, sh=0.0, line=0.6)]
        for d in (-0.6, 0.6):
            bx, by = px + ux * d, py + uy * d
            out.append(flat(capsule(bx + uy * 0.2, by - ux * 0.2, bx + uy * 1.0, by - ux * 1.0, 0.13), C.out, 0.8))
    return out


# ---- 공용 14칸 ----

def ph_k(fr):
    return TAU * fr, round(fr * NF) % NF


def mini(K, fr, look=0.6, tilt=0.0, mood=None, mouth=None):
    """작은 화살표 밑에 앉은 작은 개 — 오른쪽(소품)을 보고 꼬리 살랑, 한 번 끔뻑"""
    ph, k = ph_k(fr)
    m = mood or ("blink" if k == 7 else "open")
    F = Frame(7.4, 18.4, 0.56)
    return dog(F, K, m, mouth=mouth, look=look, tilt=tilt, wag=0.9 * sin(ph), bob=0.3 * (1 - cos(2 * ph)) / 2)


def companion(K, fr, props, **kw):
    return props + mini(K, fr, **kw) + small_arrow()


def sc_busy(K, fr):
    """오른쪽에 분홍 발자국 여덟이 원을 그리며 한 발씩 차례로 찍힌다 — 가운데 뼈다귀가 같이 돈다"""
    ph, k = ph_k(fr)
    cx, cy, R = 22.6, 20.6, 5.9
    head = k * 8 / NF
    out = []
    for i in range(8):
        a = TAU * i / 8 - pi / 2
        lag = (head - i) % 8
        al = 1.0 if lag < 1 else 0.8 if lag < 2 else 0.5 if lag < 4 else 0.22
        x, y = cx + R * cos(a), cy + R * sin(a)
        f = union(*[turn(g, a + pi / 2, x, y) for g in (ell(x, y + 0.45, 0.95, 0.8), circle(x - 1.05, y - 0.6, 0.45),
                                                          circle(x, y - 1.05, 0.45), circle(x + 1.05, y - 0.6, 0.45))])
        out.append(layer(f, lambda px, py, e, nx, ny, fr_: (lerp(PINK, hx("d8728a"), smooth(0.3, 0.15, -e)), 1.0), alpha=al))
    out += bone_layers(bone_f(cx, cy, 3.6, TAU * fr, 0.7, 0.85))
    return companion(K, fr, out, tilt=0.08 * sin(ph))


QPATH = [(20.0, 18.8), (20.0, 16.4), (22.2, 14.4), (24.6, 12.4), (24.8, 9.2), (22.4, 7.0), (19.2, 7.6)]


def sc_help(K, fr):
    """파란 리드줄 한 가닥이 물음표로 휘어 살랑 — 점 자리엔 테니스공이 톡톡. 개는 고개 갸웃"""
    ph, k = ph_k(fr)
    sw = 0.5 * sin(ph)
    pts = [(x + sw * (19.0 - y) / 12.0, y) for x, y in QPATH]
    q = chain(pts, 1.05)
    out = [base(q), part(q, LEASH, shade=LEASH_D, ink=hx("1e3a5a"), line=0.7)]
    clip_ = circle(*pts[-1], 1.05)                               # 줄 끝 고리
    out.append(flat(inter(clip_, grow(q, 0.0)), CLIP))
    hop = 0.7 * abs(sin(2 * ph))
    out += ball(20.0, 25.6 - hop, 2.1, 0.6 * ph)
    return companion(K, fr, out, tilt=0.16 * sin(ph))


def sc_person(K, fr):
    """리드줄을 쥔 사람이 손을 흔들고, 작은 개가 올려다보며 꼬리 살랑 — 줄은 사람 손에서 개 목으로"""
    ph, k = ph_k(fr)
    C = H()
    cx, cy = 23.4, 17.8
    wave = abs(sin(ph))
    hand = (cx + 5.6, cy - 2.6 - 2.0 * wave)
    hold = (cx - 4.2, cy + 7.6)
    torso = clip_y(ell(cx, cy + 9.6, 6.4, 5.8), 30.4)
    sleeve = capsule(cx + 3.4, cy + 5.6, hand[0], hand[1] + 0.6, 1.45)
    sleeve2 = capsule(cx - 3.0, cy + 5.4, hold[0], hold[1], 1.4)
    hd_ = ell(cx, cy, 4.3, 4.4)
    hair = smin(0.6, ell(cx, cy - 1.6, 4.7, 3.4), ell(cx + 2.6, cy - 0.6, 2.4, 3.0))
    face_ = inter(hd_, lambda x, y: (cy - 1.0 + 0.12 * (x - cx) ** 2 * 0.3) - y + 0.0)
    hnd = circle(*hand, 1.5)
    hnd2 = circle(*hold, 1.4)
    neck = Frame(7.4, 18.4, 0.56).w(0.0, 5.0)
    out = [base(torso, sleeve, sleeve2, hd_, hair, hnd, hnd2)]
    out += [part(torso, SHIRT, shade=SHIRT_D), part(hd_, SKIN, shade=SKIN_D), part(hair, HAIR, shade=lerp(HAIR, OUT, 0.3))]
    out.append(flat(inter(face_, grow(hd_, 0.9)), SKIN))
    for sg in (-1, 1):
        out.append(flat(ell(cx + sg * 1.5, cy + 0.8, 0.5, 0.66), EYE))
        out.append(soft(ell(cx + sg * 2.4, cy + 2.2, 0.8, 0.48), CHEEK, 0.85))
    out.append(flat(arc(cx, cy + 1.8, 0.8, 0.2, pi * 0.15, pi * 0.7), C.out))
    out += [part(sleeve, SHIRT, shade=SHIRT_D), part(hnd, SKIN, shade=SKIN_D), part(sleeve2, SHIRT, shade=SHIRT_D)]
    out += companion(K, fr, [], tilt=-0.12, look=0.8, mood="happy" if k % 6 in (2, 3) else "blink" if k == 9 else "open")
    sag = 1.2 + 0.6 * sin(ph)
    lp = [(hold[0] + (neck[0] - hold[0]) * t, hold[1] + (neck[1] - hold[1]) * t + sag * sin(pi * t)) for t in (0.0, 0.25, 0.5, 0.75, 1.0)]
    ls = chain(lp, 0.5)
    out += [base(ls), flat(ls, LEASH)]
    out += [base(hnd2), part(hnd2, SKIN, shade=SKIN_D)]
    return out


def sc_pin(K, fr):
    """빨간 지도 핀 속에 흰 개 발자국 — 핀이 통통, 땅에 닿을 때 작은 개가 눈웃음"""
    ph, k = ph_k(fr)
    hop = abs(sin(pi * fr))
    cx, cy = 22.8, 13.4 - 2.6 * hop
    out = [layer(ell(23.0, 28.8, 3.4 - 0.8 * hop, 0.75), lambda *a: (OUT, 0.22))]
    f = smin(1.0, circle(cx, cy, 5.8), poly([(cx - 4.7, cy + 2.7), (cx + 4.7, cy + 2.7), (cx, cy + 11.6)]))
    out += [base(f), part(f, lambda x, y: lerp(SIGN_L, SIGN, smooth(cy - 5, cy - 1.5, y + 0.6 * (x - cx))), shade=SIGN_D, ink=SIGN_D)]
    toes = union(ell(cx, cy + 1.2, 2.0, 1.6), *[circle(cx + u, cy + v, 0.85) for u, v in ((-2.2, -0.9), (-0.8, -2.3), (0.8, -2.3), (2.2, -0.9))])
    out.append(flat(toes, HI_WHITE))
    return companion(K, fr, out, mood="happy" if hop < 0.3 else "open")


HAND_HOT = (7, 1)
PINK_L = hx("fbd3dc")


def sc_hand(K, fr, hot=HAND_HOT):
    """손! — 오른쪽 아래 개가 앞발을 볼 밖으로 들어 클릭 자리에 분홍 발도장을 꾹. 꾹(장 4 · 10)에 도장이 납작해지고 ^^,
    이어 두 장 동안 연분홍 고리가 퍼진다(흰냥이 링크 M 꾹 퐁과 같은 짓). 가운데 발가락 사이 위가 핫스팟"""
    ph, k = ph_k(fr)
    tap = k % 6 in (3, 4, 5)
    clap = k % 6 == 4
    X, Y = hot[0] + 0.5, hot[1] + 4.0
    out = []
    if k % 6 in (4, 5):
        rx, ry, a = (3.8, 3.2, 0.9) if k % 6 == 4 else (5.0, 4.2, 0.5)
        out.append(flat(lambda x, y: abs(ell(X, Y + 0.4, rx, ry)(x, y)) - 0.32, PINK_L, a))
    sq = 1.0 if clap else 0.0
    big = ell(X, Y + 0.8 + 0.2 * sq, 2.0 + 0.3 * sq, 1.6 - 0.25 * sq)
    toes = [circle(X + u * (1 + 0.1 * sq), Y + v, 0.78) for u, v in ((-2.0, -1.0), (-0.7, -2.2), (0.7, -2.2), (2.0, -1.0))]
    pr = union(big, *toes)
    out.append(layer(pr, lambda x, y, e, nx, ny, fr_: (lerp(PAD, hx("d8607a"), smooth(0.3, 0.15, -e)), 1.0 if tap else 0.92)))
    F = Frame(18.6, 15.8, 0.8)
    out += dog(F, K, "happy" if clap else "open", look=-0.6, wag=0.9 * sin(2 * ph), bob=0.6 if clap else 0.0,
               mouth="tongue" if clap else None, arms=[((-5.6, 5.2), (-9.4, 0.4 if tap else -0.3), True)])
    return out


def sc_cross(K, fr, C_=15.5):
    """조준선 네 갈래 가운데에 개 얼굴 — 코가 십자 가운데, 귀를 쫑긋쫑긋 · 한 번 끔뻑. 머리만 그린다"""
    ph, k = ph_k(fr)
    s = 0.78
    ny0 = 1.15 + 0.6 * (K.snout - 1)
    F = Frame(C_, C_ - ny0 * s, s)
    L = 2.1
    lines = union(capsule(1.6, C_, 1.6 + L * 2.6, C_, 0.5), capsule(29.4 - L * 2.6, C_, 29.4, C_, 0.5),
                  capsule(C_, 1.6, C_, 1.6 + L * 1.6, 0.5), capsule(C_, 29.4 - L * 2.4, C_, 29.4, 0.5))
    out = [base(lines), flat(lines, OUT)]
    f = 0.35 * max(0.0, sin(2 * ph))
    out += dog(F, K, "blink" if k == 8 else "open", body=False, paws=False, tail=False, flap=(-f, -f))
    return out


def sc_ibeam(K, fr, X=3.5):
    """세운 뼈다귀가 I — 오른쪽에 앉아 어깨를 기대고 고개를 갸웃갸웃. 핫스팟은 뼈다귀 가운데"""
    ph, k = ph_k(fr)
    tilt = (0, 0, 4, 7, 7, 4, 0, 0, -4, -7, -7, -4)[k]
    stem = rbox(X, 14.5, 1.15, 11.0, 0.5)
    knobs = union(*[circle(X + sx * 1.1, y + sy * 0.9, 1.15) for sx in (-1, 1) for sy in (-1, 1) for y in (3.4, 25.6)
                    if not (sy == -1 and y == 25.6) and not (sy == 1 and y == 3.4)])
    I = union(stem, knobs)
    F = Frame(15.4, 15.4, 0.76)
    out = dog(F, K, "blink" if k == 6 else "happy" if abs(tilt) == 7 else "open", tilt=radians(tilt), wag=0.8 * sin(ph),
              look=-0.4, arms=[((-5.2, 5.6), (-8.0, 4.4), False)])
    out = bone_layers(I) + out
    return out


def sc_move(K, fr):
    """제 꼬리를 쫓아 빙글빙글 — 몸이 좌우로 홱홱 돌고 꼬리가 앞으로 휙, 둘레에 도는 줄. 네 방향 분홍 화살촉이 두근.
    몸 가운데(15, 15)가 핫스팟"""
    ph, k = ph_k(fr)
    o = 0.6 if k % 6 < 3 else 0.0
    out = []
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        out += chevron(15.5 + dx * (13.6 + o), 15.5 + dy * (13.6 + o), dx, dy, 2.2, 1.0 if o else 0.75)
    a = TAU * fr
    for i in range(3):                                           # 도는 줄
        t = a + i * 0.5
        out.append(flat(arc(15.5, 16.4, 9.6, 0.3, t, 0.42), MARK, 0.9 - 0.2 * i))
    F = Frame(15.5, 11.2, 0.6)
    out += dog(F, K, "happy" if k % 6 in (2, 3) else "open", look=1.2 * sin(a), tilt=0.18 * sin(a), wag=2.2 * sin(2 * a),
               bob=0.4 * abs(sin(2 * a)))
    return out


def stretch(K, fr, C_, ang, length, s=0.6, chev=None, head=(0.0, -1.0), hoff=2.2):
    """기지개(쭉 늘어난 개): 굵은 몸이 축(ang)을 따라 — 앞 끝에 똑바른 얼굴, 그 앞으로 쭉 뻗은 앞발 둘,
    뒤 끝에 뒷발 둘과 꼬리. 냥이 틀 stretch 와 같은 자리에 개 머리(catkit.stretch 는 냥이 머리를 박아 둬서 베꼈다)"""
    ph, k = ph_k(fr)
    C = H()
    e = length * (1 + 0.05 * sin(ph))
    ux, uy = cos(ang), sin(ang)
    cx, cy = C_
    r = 3.3 * s / 0.6
    a0 = (cx - ux * e / 2, cy - uy * e / 2)
    a1 = (cx + ux * e / 2, cy + uy * e / 2)
    px, py = -head[0], -head[1]
    bodyf = taper(a0[0], a0[1], r, a1[0], a1[1], r * 0.92)
    if K.fluffy:
        bodyf = wob(bodyf, K.fluffy * 0.5, cx, cy, 16)
    pr = 1.85 * s / 0.6
    reach = 0.6 * (1 + sin(ph)) / 2
    fronts = [oell(a0[0] - ux * (r + 0.9 + reach) + px * j * 1.35, a0[1] - uy * (r + 0.9 + reach) + py * j * 1.35,
                   pr * 1.15, pr * 0.85, ang) for j in (-0.7, 0.7)]
    backs = [oell(a1[0] + ux * (r * 0.55) + px * (r * 0.75 + j * 0.9), a1[1] + uy * (r * 0.55) + py * (r * 0.75 + j * 0.9),
                  pr * 0.95, pr * 0.8, ang) for j in (-0.8, 0.8)]
    tw = 0.7 * sin(2 * ph)
    t0 = (a1[0] + ux * r * 0.4 - px * r * 0.3, a1[1] + uy * r * 0.4 - py * r * 0.3)
    tl = [] if K.tail == "stub" else [chain([t0, (t0[0] + ux * 2.6 - px * 1.0, t0[1] + uy * 2.6 - py * 1.0),
                                            (t0[0] + ux * 3.2 - px * (3.0 + tw), t0[1] + uy * 3.2 - py * (3.0 + tw))], 1.5, 1.3)]
    paw_c = C.light if K.sock else C.base
    out = [base(bodyf, *tl, *fronts, *backs)]
    for f in tl:
        out.append(part(f, C.base))
    for f in backs:
        out.append(part(f, paw_c))
    out.append(part(bodyf, C.base))
    for f in fronts:
        out.append(part(f, paw_c))
    hx_, hy_ = a0[0] + ux * r * 0.9 + head[0] * hoff, a0[1] + uy * r * 0.9 + head[1] * hoff
    out += dog(Frame(hx_, hy_, s), K, "blink" if k in (5, 11) else ("squeeze" if sin(ph) > 0.7 else "open"),
               body=False, paws=False, tail=False)
    o = 0.6 if sin(ph) > 0.3 else 0.0
    for (x, y, dx, dy) in chev or ():
        out += chevron(x + dx * o, y + dy * o, dx, dy, 2.2, 1.0 if o else 0.75)
    return out


def sc_we(K, fr):
    return stretch(K, fr, (15.5, 19.4), 0.0, 13.0, 0.56, chev=[(1.6, 6.5, -1, 0), (29.4, 6.5, 1, 0)], head=(0.0, -1.0), hoff=1.6)


def sc_ns(K, fr):
    return stretch(K, fr, (13.0, 16.4), pi / 2, 13.0, 0.52, chev=[(5.5, 1.6, 0, -1), (5.5, 29.4, 0, 1)], head=(1.0, 0.0), hoff=1.4)


def sc_nwse(K, fr):
    d = 0.5 ** 0.5
    return stretch(K, fr, (15.5, 15.5), pi / 4, 12.6, 0.52, chev=[(3.0, 3.0, -d, -d), (28.0, 28.0, d, d)], head=(d, -d), hoff=1.2)


def sc_nesw(K, fr):
    d = 0.5 ** 0.5
    return stretch(K, fr, (15.5, 15.5), -pi / 4, 12.6, 0.52, chev=[(28.0, 3.0, d, -d), (3.0, 28.0, -d, d)], head=(-d, -d), hoff=1.2)


PEN_HOT = (1, 22)


def sc_pen(K, fr, hot=PEN_HOT):
    """연필을 비스듬히 물고 쓰는 개 — 심이 왼쪽 아래 끝이자 핫스팟. 끄덕일 때 연필이 따라 까딱, 쓴 줄이 자란다"""
    ph, k = ph_k(fr)
    bob = ((0, 0), (0, 0), (0.5, 0), (0.5, 0.5), (0, 0.5), (0, 0), (0, 0), (0.5, 0), (0.5, 0.5), (0, 0.5), (0, 0), (0, 0))[k]
    s = 0.7
    F = Frame(21.4 + bob[0], 11.0 + bob[1], s)
    tilt = radians(-6.0)
    ny0 = 1.15 + 0.6 * (K.snout - 1)
    mx, my = F.w(*Pose(tilt).hp(0.0, ny0 + 1.4))
    tip = (hot[0] + 0.55, hot[1] + 0.5)
    out = []
    n = min(k + 2, 12)
    for i in range(n):                                           # 쓴 줄 — 물결
        x0 = 3.0 + 1.7 * i
        out.append(flat(capsule(x0, 28.2 + 0.5 * sin(x0 * 0.9), x0 + 1.4, 28.2 + 0.5 * sin((x0 + 1.4) * 0.9), 0.32), OUT, 0.9))
    out += dog(F, K, "blink" if k == 4 else "happy" if k in (8, 9) else "open", tilt=tilt, wag=0.8 * sin(ph), look=-0.5,
               mouth="none")
    L = hypot(mx - tip[0], my - tip[1]) + 3.4
    ux, uy = (mx - tip[0]) / (L - 3.4), (my - tip[1]) / (L - 3.4)
    end = (tip[0] + ux * L, tip[1] + uy * L)
    cone = taper(tip[0], tip[1], 0.3, tip[0] + ux * 3.6, tip[1] + uy * 3.6, 1.35)
    shaft = capsule(tip[0] + ux * 3.4, tip[1] + uy * 3.4, *end, 1.35)

    def pcol(x, y):
        t = (x - tip[0]) * ux + (y - tip[1]) * uy
        sd = -(x - tip[0]) * uy + (y - tip[1]) * ux
        if t < 1.6:
            return PEN_G
        if t < 3.7:
            return PEN_W
        if t > L - 1.6:
            return PEN_E
        if t > L - 2.6:
            return PEN_F
        return PEN_YD if sd > 0.45 else PEN_Y
    out += [base(cone, shaft), part(union(cone, shaft), pcol, shade=PEN_YD, ink=hx("6a4a2a"), line=0.6, sh=0.0)]
    for sg in (-1, 1):                                           # 문 입꼬리 — 연필 위로 볼 살짝
        bx, by = F.w(*Pose(tilt).hp(sg * 1.5, ny0 + 1.3))
        out.append(flat(arc(bx, by - 0.5, 0.7, 0.18, pi * 0.1 if sg > 0 else pi * 0.3, pi * 0.6), OUT, 0.9))
    return out


UP_HOT = (15, 5)                    # 머리 꼭대기 — 쫑긋 귀 끝이 머리보다 3칸 높아 (15, 3) 이면 판 위로 넘었다


def sc_up(K, fr, hot=UP_HOT):
    """뒷발로 서서 앞발을 가슴 앞에 모아 싹싹 — 머리는 그 자리라 머리 꼭대기(핫스팟)가 장마다 같은 칸. 비빌 때 눈웃음"""
    ph, k = ph_k(fr)
    s = 0.7
    X = hot[0] + 0.5
    F = Frame(X, hot[1] + 0.5 + 5.6 * s, s)
    rub = 0.8 * sin(2 * ph)
    out = [layer(ell(X, F.oy + 15.8 * s, 4.6, 0.7), lambda *a: (OUT, 0.22))]
    out += dog(F, K, "happy" if k % 6 in (2, 3) else "blink" if k == 9 else "open", mouth="tongue" if k % 6 in (2, 3) else None,
               wag=1.2 * sin(2 * ph), stand=True)
    C = H()
    for sg in (-1, 1):                                           # 모은 앞발 — 팔을 그리면 먹선이 겹쳐 까만 매듭이 됐다
        out.append(flat(F.f(ell(sg * 1.45 + rub, 7.4 - 0.2 * sg, 1.75, 1.35)), C.light, line=0.4))
    if k % 6 in (2, 3):
        out += marks([(X - 6.6, 14.6, X - 8.0, 13.6), (X + 6.6, 14.6, X + 8.0, 13.6)])
    return out


SHARED = {"busy": sc_busy, "help": sc_help, "person": sc_person, "pin": sc_pin, "hand": sc_hand, "cross": sc_cross,
          "ibeam": sc_ibeam, "move": sc_move, "pen": sc_pen, "up": sc_up, "ns": sc_ns, "we": sc_we, "nwse": sc_nwse,
          "nesw": sc_nesw}

HOT = {"arrow": (1, 1), "busy": (1, 1), "help": (1, 1), "person": (1, 1), "pin": (1, 1), "cross": (15, 15),
       "hand": HAND_HOT, "ibeam": (3, 14), "move": (15, 15), "nesw": (15, 15), "nwse": (15, 15), "no": (14, 14),
       "ns": (5, 15), "pen": PEN_HOT, "up": UP_HOT, "we": (15, 6), "wait": (15, 15)}


class DogPet(Pet):
    """댕댕이 결 하나 — fur(털빛) · kind(생김새) · own(wait · no 장면, fr → 레이어) · hot(칸 → art 칸).
    화살표는 틀이 그린다(fetch, 모양 탭이면 peek). shared 를 주면 공용 칸을 마리 것으로 바꿔 끼운다(이름 → (K, fr) → 레이어)"""
    M = 1.8

    def __init__(self, fur, kind, own, hot=None, shared=None):
        super().__init__(fur, {}, dict(HOT, **(hot or {})))
        self.kind, self.own = kind, own
        self.shared = dict(SHARED, **(shared or {}))

    def cell(self, name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
        use(self.coat)
        if name == "arrow":
            if shape:
                g = shaped(shape)
                return peek(self.kind, frame, g), g["hot"]
            return fetch(self.kind, frame), (1.5, 1.5)
        ax, ay = self.hot[name]
        if name in self.own:
            return self.own[name](frame), (ax + 0.5, ay + 0.5)
        return self.shared[name](self.kind, frame), (ax + 0.5, ay + 0.5)

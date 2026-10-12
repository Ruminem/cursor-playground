# SPDX-License-Identifier: Apache-2.0
"""사랑앵무(budgieanim) 고화질 — 새 틀(birdkit)에 깃빛 · 생김새 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(gen/bird.py)의 생김새 그대로: 연두 몸 · 밝은 연두 배 · 노란 얼굴(정수리에 물결 줄) · 목에 점 넷(가운데 둘 까망 ·
양끝 보라) · 파란 코(납막)를 얹은 갈고리 부리 · 날개 물결 줄 · 길고 파란 꼬리. 짓도 그대로: 화살표를 이고 통통 — 날개는
접은 채(화살표), 거울 앞에서 고개를 까딱이며 수다(기다림), 두 날개를 가슴 앞에 X 로 엇걸고 도리도리(금지).

갈고리 부리는 틀의 마름모 부리 대신 Kind.beak 로 그린다 — 앞에서 본 앵무 부리는 아래로 뾰족한 둥근 세모 하나고
아랫부리는 벌릴 때만 보인다. 정수리 물결 줄은 눈썹으로 읽히지 않게 눈보다 한참 위(머리 위 반)에만 둔다.
"""
from . import catkit, register
from .birdkit import (Plume, Kind, BirdPet, bird, stand, at_mid, carry_s, hang, ground, puff, arrow_layers, beak_layers,
                      HOP, P_, OUT, MOUTH, ell, circle, capsule, inter, chain, rpoly, base, part, flat, lerp,
                      clamp, hx, zip_lines, no_sign, ph_k, sin, cos, atan2, pi, radians)

B_GREEN, B_GREEN_L, B_YEL, B_BAR, B_WING = hx("74c84c"), hx("a6e070"), hx("ffe25a"), hx("3a3a2e"), hx("e6ec7a")
B_TAIL, B_CERE, B_BEAK, B_SPOT = hx("3e6ec8"), hx("5a86e6"), hx("f0d8a0"), hx("6a5ad8")
B_GREEN_D = lerp(B_GREEN, hx("2e5a20"), 0.45)          # 그늘 — 픽셀 판엔 그늘 색이 없어 연두를 어둡게
PLUME = Plume(B_GREEN, B_GREEN_D, B_GREEN_L, B_WING, B_BEAK, hx("c8a870"), foot=hx("c89aa0"))
GLASS, GLASS_L, FRAME, FRAME_D = hx("bfe0f0"), hx("eef8ff"), hx("c8ccd4"), hx("8a909a")
NOTE = (hx("f07c9c"), hx("6aa8e0"), hx("8cc864"))


def hook_beak(F, K_, o, lu, hv, up, cere=None):
    """앞에서 본 갈고리 부리 — 아래로 뾰족한 둥근 세모(윗부리) 위에 코(납막). 벌리면 윗부리가 들리고 그 밑에 입속 ·
    작은 아랫부리. 32 에서 1칸 아래로 안 줄게 판 단위로 바닥을 둔다"""
    if up:                                         # 고개를 젖힌 칸(hand)은 틀 부리 그대로 — 끝이 핫스팟이라
        return beak_layers(F, K_, o, lu, hv, True)
    C = P_()
    m = max(1.0, 0.8 / F.s)
    bx, by = lu, K_.beak_y + hv
    w, h = K_.bw * m, K_.bh * m
    ink = lerp(C.beak_d, OUT, 0.45)
    lift = o * 0.45 * m
    upper = rpoly([(bx - w, by - lift), (bx + w, by - lift), (bx, by + h - lift)], 0.35)
    out = []
    if o > 0.05:
        dn = o * 0.9 * m
        top = by + h * 0.4
        lower = rpoly([(bx - w * 0.62, top + dn), (bx + w * 0.62, top + dn), (bx, top + dn + h * 0.55)], 0.25)
        mouth = ell(bx, top + dn * 0.4, w * 0.55, h * 0.3 + dn * 0.55)
        out += [flat(F.f(mouth), MOUTH, line=0.32, ink=ink),
                part(F.f(lower), C.beak_d, shade=lerp(C.beak_d, OUT, 0.25), line=0.38, sh=0.0, ink=ink)]
    out.append(part(F.f(upper), C.beak, shade=C.beak_d, line=0.38, sh=0.0, ink=ink))
    if cere is not None:
        c = ell(bx, by - lift - 0.1 * m, w * 0.8, 0.62 * m)
        out.append(part(F.f(c), cere, shade=lerp(cere, OUT, 0.25), line=0.38, sh=0.0, ink=lerp(cere, OUT, 0.5)))
    return out


class BudgieKind(Kind):
    head = (6.4, 6.3)
    body = (7.8, 5.6, 5.6)
    beak_y = 2.1
    bw, bh = 1.45, 2.0

    def marks(self, hv):
        """노란 얼굴 · 정수리 물결 줄 둘 · 목 점 넷(가운데 둘 까망 · 양끝 보라)"""
        hrx, hry = self.head
        head = ell(0.0, hv, hrx, hry)
        out = [(head, B_YEL)]
        for y0 in (hv - hry + 1.5, hv - hry + 3.0):
            out.append((inter(head, lambda x, y, y0=y0: abs(y - y0 - 0.3 * sin(x * 1.4)) - 0.36), B_BAR))
        for x, col in ((-2.6, B_SPOT), (-0.95, B_BAR), (0.95, B_BAR), (2.6, B_SPOT)):
            out.append((circle(x, hv + 5.1 - 0.25 * abs(x), 0.62), col))
        return out

    def tail(self):
        fv = self.feet_v
        return [(chain([(1.2, fv - 5.6), (3.4, fv - 2.4), (5.6, fv - 0.7)], 1.6, 0.75), B_TAIL)]

    def wing_marks(self, w, rx, ry, a, L, sg):
        """날개 물결 줄 — 날개 결을 가로지르는 까만 줄이 고르게"""
        ca, sa = cos(a), sin(a)

        def bars(x, y):
            t = (x - rx) * ca + (y - ry) * sa
            c = -(x - rx) * sa + (y - ry) * ca
            u = (t + 0.3 * sin(c * 2.0)) % 1.7 - 0.85
            return max(abs(u) - 0.38, 0.4 - t)
        return [(bars, B_BAR)]

    def beak(self, F, o, lu, hv, up):
        return hook_beak(F, self, o, lu, hv, up, B_CERE)


K = BudgieKind()


def head_v(sq=0.0, puff_=1.0):
    """bird() 가 눌림 · 부풂만큼 머리를 내리는 값(캐논)"""
    bry = K.body[2]
    return 1.5 * (bry - bry * (1 - 0.14 * sq) * puff_)


def brows(F, hv, col, look=0.0):
    """화난 눈썹 — 안쪽이 내려온 짧은 막대 둘"""
    ex, ey = K.eye
    lu = 0.9 * look
    out = []
    for sg in (-1, 1):
        x0, y0 = F.w(sg * (ex - 1.3) + lu, ey + hv - 1.6)
        x1, y1 = F.w(sg * (ex + 1.0) + lu, ey + hv - 2.6)
        out.append(flat(capsule(x0, y0, x1, y1, max(0.4, 0.5 * F.s)), col))
    return out


WING_CAP = 0.15                    # 날개를 들면 줄무늬가 X 로 뭉개진다 — 접은 채(픽셀 판 CARRY_OPT)


def sc_arrow(fr, g):
    """크림 화살표를 정수리에 이고 통통 — birdkit.carry_hop 그대로이되 날개는 접은 채(드는 한도 WING_CAP).
    carry_hop 은 날개 자세를 제가 정해 kw 로 못 바꿔서 같은 셈을 여기 옮겼다. 화살표가 맨 위"""
    ph, k = ph_k(fr)
    gap, sq, wu, mood, bk, dust = HOP[k]
    s = carry_s(K, g)
    px, py = g["stem"][0], g["stem"][1] - 0.8
    F = hang(K, px, py, s)
    t = clamp(min(wu, WING_CAP))
    fy = py + (K.feet_v + K.head[1]) * s
    out = ground(px, min(fy + 0.6, 30.0), 3.6 - 0.5 * gap, 0.2 - 0.03 * gap)
    out += bird(F, K, mood, beak=0.8 if bk else 0.0, wl=(("fold", "up"), t), wr=(("fold", "up"), t), sq=sq - 0.25 * gap,
                lift=(0.4 * gap, 0.4 * gap))
    if dust:
        out += puff(px + 5.2, min(fy, 29.0), 0.9, 0.8)
    return out + arrow_layers(g)


def mirror(fr, nod):
    """세운 손거울 — 하늘색 유리 · 회색 테 · 받침대. 유리 속에 마주 보는 초록 앵무가 같이 까딱"""
    mx, my = 25.6, 11.6
    glass = ell(mx, my, 3.9, 5.0)
    rim = ell(mx, my, 4.7, 5.8)
    pole = capsule(mx, my + 5.4, mx, 25.6, 0.65)
    foot = capsule(mx - 3.4, 26.2, mx + 3.4, 26.2, 0.8)
    out = [base(rim, pole, foot), part(pole, FRAME, shade=FRAME_D, line=0.7), part(foot, FRAME, shade=FRAME_D, line=0.7),
           part(rim, FRAME, shade=FRAME_D, line=0.8), flat(glass, GLASS)]
    rx = mx + 0.3 - 0.5 * nod                                  # 거울 속 앵무 — 바깥 앵무와 마주 보며 까딱
    bod = inter(glass, ell(rx, my + 4.2, 2.6, 2.8))
    hd_ = inter(glass, ell(rx - 0.2 * nod, my + 0.4 + 0.3 * nod, 2.0, 1.9))
    out += [flat(bod, B_GREEN, 0.85), flat(hd_, B_YEL, 0.9)]
    for sg in (-1, 1):
        out.append(flat(circle(rx - 0.2 * nod + sg * 0.85, my + 0.6 + 0.3 * nod, 0.32), OUT, 0.8))
    out += [flat(capsule(mx - 2.2, my - 2.6, mx - 1.2, my - 3.8, 0.35), GLASS_L),
            flat(capsule(mx - 2.6, my - 0.8, mx - 2.4, my - 1.4, 0.32), GLASS_L)]
    return out


def sc_wait(fr):
    """거울 앞에서 수다 — 거울 쪽으로 고개를 까딱이며 부리를 짹짹, 거울 속 초록 앵무, 둘 사이로 말 점이 오간다"""
    ph, k = ph_k(fr)
    nod = sin(2 * ph)
    talk = k % 3 != 2
    out = mirror(fr, nod)
    F = stand(K, 11.2, 28.6, 0.8, radians(5.0 * max(0.0, nod)))
    out += ground(11.2, 28.9, 5.4)
    out += bird(F, K, "blink" if k == 6 else "open", beak=0.85 if talk and k % 2 == 0 else 0.0, look=0.6 + 0.4 * nod,
                sq=0.3 * max(0.0, nod))
    if talk:                                                   # 말 점 ··· — 부리에서 거울 쪽으로 차례로 뜬다
        for i in range(3):
            if (k + i) % 3 != 0:
                d = circle(17.0 + i * 1.9, 7.0 - (i % 2) * 0.9, 0.7)
                out += [base(d), part(d, NOTE[i % 3], line=0.4, sh=0.0)]
    return out


CROSS = 2.1                       # 엇건 날개 길이 배 — 가슴 가운데를 넘어 X 가 되게


def sc_no(fr):
    """두 날개를 가슴 앞에 X 로 엇걸고 고개를 도리도리 — 화난 눈썹, 가끔 짹. 표지가 위"""
    ph, k = ph_k(fr)
    sh = sin(2 * ph)
    F = at_mid(K, 11.2, 19.0, 0.6, radians(5.0 * sh))       # 빗금 왼쪽 아래로 — 가운데 두면 두 눈 · 엇건 날개가 빗금에 묻힌다
    brx = K.body[1]
    a = atan2(3.4, -brx * 0.72 * 1.5)                           # 오른 날개 → 왼쪽 아래, 왼 날개 → 오른쪽 아래
    wr, wl = ("aim", a, CROSS, True), ("aim", pi - a, CROSS, True)
    out = bird(F, K, "open", beak=0.85 if k % 6 == 3 else 0.0, wl=wl, wr=wr, look=1.2 * sh)
    out += brows(F, 0.0, OUT, 1.2 * sh)
    return out + no_sign()


class Budgie(BirdPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes)"""


PET = Budgie(PLUME, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no})

register("budgie", PET)
catkit.load()

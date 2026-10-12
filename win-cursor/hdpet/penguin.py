# SPDX-License-Identifier: Apache-2.0
"""아기펭귄(penguinanim) 고화질 — 새 틀(birdkit)에 깃빛 · 생김새 · 화살표 · 기다림 · 금지 세 칸만 얹는다.

픽셀 판(지운 gen/bird.py)의 짓 그대로: 화살표를 머리에 이고 뒤뚱(화살표), 얼음판 위에서 몸을 좌우로 기울이며
지느러미를 번갈아 들고 발을 바꿔 딛는 뒤뚱(기다림), 지느러미를 위아래로 파닥파닥 휘저으며 발을 구르는 안 돼!(금지).
회색 솜털 몸 · 까만 머리 · 흰 고글 가면 · 가늘고 긴 지느러미. 테는 흰 · 회색 새 몫인 연회색(픽셀 판 RIM_GREY).
"""
from . import catkit, register
from .birdkit import (Plume, Kind, BirdPet, bird, at_mid, stand, carry_waddle, ell, hx, no_sign, ph_k, base, part, flat,
                      rbox, capsule, arc, smin, union, radians, sin, pi, OUT, hang, arrow_geo, arrow_layers, use)

P_GREY, P_GREY_L, P_GREY_D, P_BLACK = hx("a9aeb7"), hx("dadde2"), hx("80868f"), hx("2c2c34")
WHITE = hx("fffaf2")
PLUME = Plume(P_GREY, P_GREY_D, P_GREY_L, P_GREY_D, hx("6a6a76"), hx("6a6a76"), foot=hx("4a4a54"))
PLUME.rim = hx("d9dde3")
ICE, ICE_D, ICE_I = hx("e6f4fb"), hx("a8d4e8"), hx("7aaccc")
ANGRY = hx("e8484a")


class PenguinKind(Kind):
    head = (6.2, 5.9)
    body = (7.9, 7.6, 5.8)         # 머리보다 넓은 통통 몸
    eye = (2.9, 1.1)
    beak_y = 3.1
    bw, bh = 1.1, 1.3
    wing_l, wing_w = 3.9, 1.45     # 가늘고 긴 지느러미
    foot_x = 2.8
    waddle = True

    def marks(self, hv):
        """까만 머리 + 흰 고글 가면 — 눈 둘레 흰 타원 둘이 부리 밑에서 이어지고, 눈 사이는 까만 줄이 부리 위까지 내려온다.
        머리 테 안쪽 0.9 는 bird 가 잘라 내지만 먹선(1칸)보다 얇아 회색 고리로 안 남는다(배율 0.92 까지)"""
        hrx, hry = self.head
        ex, ey = self.eye
        mask = smin(1.2, ell(-ex, ey + 0.5 + hv, 2.45, 2.9), ell(ex, ey + 0.5 + hv, 2.45, 2.9),
                    ell(0.0, self.beak_y + 0.7 + hv, 2.6, 1.6))
        return [(ell(0.0, hv, hrx, hry), P_BLACK), (mask, WHITE)]


K = PenguinKind()


def head_v(sq=0.0, puff=1.0):
    """bird() 가 sq · puff 로 머리를 내린 만큼(캐논 v) — 눈썹을 눈에 맞춰 단다"""
    bry = K.body[2]
    return (bry - bry * (1 - 0.14 * sq) * puff) * 1.5


def brows(F, hv, col=OUT):
    """화난 눈썹 — 흰 고글 위쪽에 안쪽이 내려온 짧은 줄"""
    ex, ey = K.eye
    out = []
    for sg in (-1, 1):
        x0, y0 = F.w(sg * (ex + 1.3), ey - 2.0 + hv)
        x1, y1 = F.w(sg * (ex - 0.7), ey - 1.2 + hv)
        out.append(flat(capsule(x0, y0, x1, y1, max(0.42, 0.32 * F.s)), col))
    return out


def anger(cx, cy, r=1.6):
    """화남 표시(💢) — 네 귀퉁이에서 가운데를 향해 굽은 빨간 활 넷"""
    fs = [arc(cx + dx * r * 1.25, cy + dy * r * 1.25, r * 0.75, 0.3, a0, pi / 2)
          for dx, dy, a0 in ((-1, -1, 0.0), (1, -1, pi / 2), (1, 1, pi), (-1, 1, -pi / 2))]
    f = union(*fs)
    return [base(f), part(f, ANGRY, shade=ANGRY, line=0.0, sh=0.0)]


def sc_arrow(fr, g):
    """크림 화살표를 정수리에 이고 뒤뚱뒤뚱 — 걸음마다 지느러미가 살짝 들리고 가끔 삐약. 화살표가 맨 위"""
    return carry_waddle(K, fr, g)


def sc_wait(fr):
    """얼음판 위에서 뒤뚱뒤뚱 — 몸을 좌우로 기울이며 기우는 쪽 반대 지느러미를 들고, 발을 바꿔 딛는다"""
    ph, k = ph_k(fr)
    sw = sin(ph)
    gy = 27.6
    ice = rbox(16.0, gy + 1.3, 13.6, 1.6, 0.9)
    out = [base(ice), part(ice, ICE, shade=ICE_D, ink=ICE_I, line=0.7)]
    for x0, x1 in ((5.0, 8.0), (21.5, 26.5)):                 # 얼음 반짝 줄
        out.append(flat(capsule(x0, gy + 0.9, x1, gy + 0.9, 0.3), hx("ffffff"), 0.9))
    F = stand(K, 16.0 - 0.6 * sw, gy + 0.35, 0.8, radians(6.0) * sw)
    out += bird(F, K, "blink" if k == 8 else "happy" if k in (3, 9) else "open",
                wl=(("fold", "out"), 0.7 * max(0.0, sw)), wr=(("fold", "out"), 0.7 * max(0.0, -sw)),
                lift=(1.3 * max(0.0, -sw), 1.3 * max(0.0, sw)), sq=0.3 * abs(sw))
    return out


def sc_no(fr):
    """안 돼! — 지느러미를 위아래로 번갈아 파닥파닥 휘젓고 발을 구른다. 화난 눈썹, 세 장마다 부리를 벌리고 💢. 표지가 위"""
    ph, k = ph_k(fr)
    t = 0.5 + 0.5 * sin(2 * ph)
    F = at_mid(K, 14.5, 15.3, 0.66)
    yell = k % 3 == 0
    out = bird(F, K, "open", beak=0.85 if yell else 0.0, wl=(("fold", "up"), t), wr=(("fold", "up"), 1 - t),
               lift=(1.1 * (k % 2), 1.1 * (1 - k % 2)))
    out += brows(F, head_v())
    if yell:
        out += anger(21.2, 7.8)
    return out + no_sign()


def dangle(fr, g, s=0.6):
    """화살촉(dart) 꼭지점에 매달려 대롱대롱 — 틀의 dangle 과 같되 왼 지느러미를 곧게 위로 뻗는다.
    펭귄 지느러미가 길어(3.9) 틀의 "up" 그대로면 몸이 오른쪽으로 기운 장(3–4)에 왼 지느러미 끝이 판 왼쪽 밖으로 나간다"""
    ph, k = ph_k(fr)
    sw = sin(ph)
    px, py = g["hook"]
    F = hang(K, px, py - 0.6, s, radians(-26 + 7 * sw))
    mood = "blink" if k == 11 else "happy" if k in (2, 3, 8, 9) else "open"
    kick = (1.4 * max(0.0, sin(ph * 2)), 1.4 * max(0.0, -sin(ph * 2)))
    out = bird(F, K, mood, beak=0.8 if k in (2, 3) else 0.0, wl=("aim", -pi / 2 - 0.1, 1.05, False), wr="up",
               sq=-0.4, lift=kick)
    return out + arrow_layers(g)


class Penguin(BirdPet):
    """결 클래스를 이 모듈에 둔다 — 일감 해시가 type(결).__module__ 로 결의 파일을 찾는다(build._hashes).
    화살촉(dart) 모양만 틀 대신 위 dangle 로 그린다(틀은 고치지 않음 — 다른 새도 같이 쓰므로)"""

    def cell(self, name, frame=0.0, soft_=0.0, tip_body=False, shape=None):
        if name == "arrow":
            g = arrow_geo(shape)
            if "hook" in g:
                use(self.coat)
                return dangle(frame, g), g["hot"]
        return super().cell(name, frame, soft_, tip_body, shape)


PET = Penguin(PLUME, K, {"arrow": sc_arrow, "wait": sc_wait, "no": sc_no})

register("penguin", PET)
catkit.load()

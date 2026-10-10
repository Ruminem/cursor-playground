# SPDX-License-Identifier: Apache-2.0
"""댕댕이 · 애니 arrow 칸(앞모습 물어오기) — 견종 10마리 arrow 칸만 그린다. 나머지 16칸은 dog.py. 손으로 돌린다.

  python gen/dog_front.py [견종...]     art/<견종>anim/arrow.txt 를 쓴다

옆모습 판(dog.arrow)은 화살표가 판 절반을 먹어 개가 구석에 끼고, 귀 하나가 뿔로, 얼굴을 가로지른 대가
빗금 뭉치로 읽혀 "이게 어째서 강아지임" 소리를 들었다. 여기서는 wait 칸처럼 앞모습으로 앉은 개(`dog.sit`)를
오른쪽 아래에 크게 두고, 1배 화살표를 왼쪽 위에 둔다. 화살표는 끝(핫스팟)을 축으로 눕혀 대 끝이 왼 입꼬리에
닿게 하고(`aim`), 머리통에 걸친 대는 볼 뒤로 숨겨 입꼬리 둘레(POKE)에서만 보인다 — 대가 얼굴에 빗금을 긋지 않게.
꼬리는 몸 뒤에서 좌우로 크게 붕붕(1초 세 번) — 가운데(몸 뒤에 숨는 자리)는 건너뛰어 늘 몸 옆으로 보인다.
dog.py 의 그리개(sit · draw · eyes · put_arrow 둘레)를 빌려 쓰고 dog.py 는 건드리지 않는다.
"""
import math
import sys

import dog  # noqa: E402
from dog import D, DOGS, OUT, Rig, any_of, chain, clip, draw, fluff, head_parts, sit, tail_side, use  # noqa: E402
from sea import N, PEEK_CUR, PEEK_WHITE, RATE, finish, phases, raster, solid  # noqa: E402
import shape  # noqa: E402


# ── 자리 ──────────────────────────────────────────────────────────────────────
# 얼굴은 wait 칸처럼 정면 · 둥근 머리 · 짧은 주둥이(dog.mouth 의 코 + ω). 3/4 로 돌리고 주둥이를 내밀어 본 판은
# 뾰족 귀 · 흰 가슴과 겹쳐 여우로 읽혔다. 대 끝은 왼 입꼬리에 물린다 — 화살표 끝이 (1,1) 이라 대가 40도쯤으로
# 들어와 왼 볼을 지나므로, 머리를 시계 방향으로 갸웃해 왼 입꼬리를 볼 가장자리 쪽으로 올린다.
A_S = 1.0                    # 화살표 배율 — 눕힌 각 · 늘인 대는 입 자리에 맞춰 푼다(`aim`)
DOG_K = 0.75                 # 개 배율(wait 칸 0.8 과 같은 크기감)
DOG_O = (19.8, 21.8)         # 개 원점(sit 좌표 0,0 — 엉덩이 위 몸 가운데). 21.8 이던 때 오른쪽 꼬리 끝이 판 밖으로 잘려 2칸 당겼다 —
                             # 4칸이면 꼬리는 다 들어오지만 화살표 머리가 개 이마 · 귀를 덮는다
HC, HR = (0.0, -8.6), 8.5    # 머리 가운데 · 반지름(몸 좌표) — wait 칸(7)보다 키운 치비 머리. 1배에서 얼굴이 읽히게
TILT = 10.0                  # 머리 갸웃(+ 가 시계 — 왼 입꼬리가 화살표 쪽으로 들린다)
TURN = -0.04                 # 얼굴을 화살표 쪽으로 돌린 정도(머리 반지름 단위) — 거의 정면
BITE_X = 0.4                 # 대 끝이 왼 입꼬리 칸에서 입 안쪽으로 들어간 칸
STEM_MODE = "hide"           # front: 대가 볼 위로 입꼬리까지 · hide: 볼 뒤로 숨고 입꼬리에서만 보인다
POKE = 2.7                   # hide 일 때 입꼬리 둘레 몇 칸을 얼굴 위에 찍나
WAG = 74.0                   # 꼬리 흔드는 폭(도, 0 이 위)
R_WAG = 112.0                # 오른쪽은 머리가 판 끝까지 차서 위로 세우면 숨는다 — 옆으로 눕혀 엉덩이 옆에 내민다
T_ROOT, T_SC = (2.5, 3.0), 1.9   # 꼬리 뿌리(몸 뒤 · 좌우는 흔드는 쪽) · 옆모습 꼬리를 키운 배율
R_SC = {"husky": 1.3}        # 오른쪽으로 흔들 때 꼬리 배율(없으면 1.5) — 머리가 판 끝까지 차서 1.9 면 끝이 판 밖(x 31–34)으로 잘린다.
                             # 허스키 붓꼬리는 제일 커서 더 줄인다


def arrow_poly(s: float, ext: float, rot: float) -> list:
    """s 배 화살표를 끝(0,0)을 축으로 rot 도 돌린다. ext 만큼 대를 늘인다"""
    t = math.radians(rot)
    c, si = math.cos(t), math.sin(t)
    pts = [(x + dog.STEM[0] * ext, y + dog.STEM[1] * ext) if i in (3, 4) else (x, y) for i, (x, y) in enumerate(PEEK_CUR)]
    return [(1 + (x * c - y * si) * s, 1 + (x * si + y * c) * s) for x, y in pts]


def aim(m: tuple) -> tuple:
    """대 가운데 줄이 m 을 지나게 화살표를 끝을 축으로 돌리고(rot), 대 끝이 m 에 오게 늘인다(ext)"""
    top = ((PEEK_CUR[2][0] + PEEK_CUR[5][0]) / 2, (PEEK_CUR[2][1] + PEEK_CUR[5][1]) / 2)
    best = None
    for i in range(-600, 101):
        rot = i / 10
        t = math.radians(rot)
        c, si = math.cos(t), math.sin(t)
        tx, ty = 1 + (top[0] * c - top[1] * si) * A_S, 1 + (top[0] * si + top[1] * c) * A_S
        dx, dy = dog.STEM[0] * c - dog.STEM[1] * si, dog.STEM[0] * si + dog.STEM[1] * c
        cross = (m[0] - tx) * dy - (m[1] - ty) * dx
        if best is None or abs(cross) < best[0]:
            best = (abs(cross), rot, ((m[0] - tx) * dx + (m[1] - ty) * dy))
    _, rot, along = best
    bot = math.hypot(PEEK_CUR[3][0] + PEEK_CUR[4][0] - 2 * top[0], PEEK_CUR[3][1] + PEEK_CUR[4][1] - 2 * top[1]) / 2
    return rot, along / A_S - bot / math.hypot(*dog.STEM)


def front_tail(kind: str, ang: float, root: tuple, sc: float):
    """앞모습 꼬리 — 몸 뒤 root 에서 ang(도, 0 위 · + 오른쪽)로 뻗는다. 옆모습 꼬리(dog.tail_side)를 sc 배로 키워
    왼쪽으로 갈 때는 좌우를 뒤집어 쓴다(말린 끝이 늘 위 · 바깥으로 휜다)"""
    sg = 1.0 if ang >= 0 else -1.0
    if kind == "stub":   # 코기 — 앞에서 안 보이는 몽당꼬리를 솜뭉치로 키워 엉덩이 옆으로 내민다
        a = math.radians(abs(ang))
        cx, cy = root[0] + math.sin(a) * 5.0, root[1] - math.cos(a) * 5.0
        hit0 = any_of(fluff(cx, cy, 2.8, 2.5, n=6, amp=0.14), chain([root, (cx, cy)], 1.8))

        def col0(u, w):
            return D["LIGHT"] if math.hypot(u - cx, w - cy) < 1.8 else D["FUR"]
        return (lambda u, w: hit0(root[0] + sg * (u - root[0]), w)), (lambda u, w: col0(root[0] + sg * (u - root[0]), w))
    h, c = tail_side(kind, abs(ang), root)

    def tr(u, w):
        return root[0] + sg * (u - root[0]) / sc, root[1] + (w - root[1]) / sc
    return (lambda u, w: h(*tr(u, w))), (lambda u, w: c(*tr(u, w)))


def head_rig(rig: Rig) -> Rig:
    return rig.turned((HC[0], HC[1] + HR * 0.8), TILT)


def nose_px(hrig: Rig) -> tuple:
    """dog.mouth 가 찍는 코 자리(코 왼 칸 x · 코 아랫줄 y) — 같은 식으로 잡는다"""
    nx, ny = hrig.world(HC[0] + TURN * HR, HC[1] + HR * 0.36 * D.get("snout", 1.0))
    return round(nx) - 1, math.floor(ny)


def bite_end(hrig: Rig) -> tuple:
    """대 끝 자리(화면) — ω 입의 왼 입꼬리 칸(nl-1, ny+1)에서 BITE_X 만큼 안쪽"""
    nl, ny = nose_px(hrig)
    return nl - 1 + 0.5 + BITE_X, ny + 1 + 0.5


def arrow() -> list[dict]:
    frames = []
    rig = Rig(DOG_O[0], DOG_O[1], 0.0, DOG_K)
    hrig = head_rig(rig)
    end = bite_end(hrig)
    rot, ext = aim(end)
    print(f"  {D['id']}: 화살표 {rot:.1f}도 · 대 +{ext:.1f}")
    a = {}
    solid(a, raster(arrow_poly(A_S, ext, rot)), PEEK_WHITE, OUT)
    a[1, 1] = OUT
    turn = TURN * HR
    skull = set(draw(hrig, [p for p in head_parts(HC, HR, turn) if p[0] == "head"]))
    near = {p for p in a if math.hypot(p[0] + 0.5 - end[0], p[1] + 0.5 - end[1]) < POKE}
    shown = a if STEM_MODE == "front" else {p: c for p, c in a.items() if p not in skull or p in near}
    nl, ny = nose_px(hrig)
    face = {(x, ny) for x in (nl, nl + 1)} | {(x, ny - 1) for x in range(nl - 1, nl + 3)} | \
        {(nl, ny + 2), (nl + 1, ny + 2), (nl + 2, ny + 1)}   # 코 · 입꼬리 뺀 ω — 대 위로 다시 찍는다
    short = D.get("short")
    bp = dog.body_part((0.0, 3.0 if short else 3.2), 6.6, 5.8 if short else 6.4)[:3] + (True,)   # 꼬리와 닿는 자리에 테
    for k, ph in enumerate(phases()):
        # 1초에 세 번 — 오른 끝 · 오른 안 · 왼 끝 · 왼 안. 가운데(몸 뒤에 숨는 자리)는 안 지난다
        side = 1.0 if math.sin(2 * math.pi * k * 3 / N + math.pi / 4) > 0 else -1.0
        ang = side * (WAG if side < 0 else R_WAG) * (1.0 if k % 2 == 0 else 0.7)
        th, tc = front_tail(D["tail"], ang, (side * T_ROOT[0], T_ROOT[1]), T_SC if side < 0 else R_SC.get(D["id"], 1.5))
        f = sit(rig, k, hc=HC, r=HR, turn=turn, tilt=TILT, mood="happy" if k in (5, 6) else "open", mo="smile",
                tail="none", body=bp, behind=[("ftail", th, tc, False)])
        keep = {p: f[p] for p in face if p in f}
        f.update(shown)                                  # 화살표가 앞 — 대 끝이 왼 입꼬리에 물린다
        f.update(keep)
        frames.append(finish(clip(f)))
    return frames

def one(d: dict) -> None:
    use(d)
    out = dog.ART / f"{d['id']}anim"
    out.mkdir(parents=True, exist_ok=True)
    frames = arrow()
    dog.check(f"{d['id']}/arrow", frames, (1, 1))
    (out / "arrow.txt").write_text(shape.to_text(frames, (1, 1), RATE), encoding="utf-8")
    print(f"{d['id']}: 끝", flush=True)


def main() -> None:
    from concurrent.futures import ProcessPoolExecutor
    only = sys.argv[1:]
    with ProcessPoolExecutor() as ex:
        list(ex.map(one, [d for d in DOGS if not only or d["id"] in only]))


if __name__ == "__main__":
    main()

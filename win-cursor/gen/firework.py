# SPDX-License-Identifier: Apache-2.0
"""폭죽(firework) 구성표 그림 `art/firework/*.txt` 를 만든다. 빌드가 부르는 것이 아니라 그림을 다시 뽑을 때 손으로 돌린다.

  python3 gen/firework.py [역할...]              그림을 쓴다 (역할을 안 주면 17칸 전부)
  python3 gen/firework.py --ascii 역할 [처음:끝]  장을 글자로 나란히
늘 옛 그림(BASE 커밋의 art/firework)의 몸 모양에서 출발한다 — 두 번 돌려도 새 그림을 다시 먹지 않는다.
기본값(K=3 · RATE=1)이 지금 올라간 그림이다: 48박 × 3장 = 144장 × 1틱 = 2.4초, 60fps 에 1.5배 느린 슬로모션.
이 파일은 빌드 코드 해시(build.py `_hashes`)와 CI 캐시 키(`win-cursor/*.py`)에 안 들어간다 — 고쳐도 빌드는
아무것도 다시 안 그리니, 돌려서 art 를 고쳐야 반영된다.
밤하늘 몸 안에서 로켓이 아래에서 솟아 한 점에서 방사형으로 터진다. 금·분홍·청록 셋이 엇박으로
다른 자리에서. 터지는 순간 몸이 번쩍하고 테두리와 둘레 번짐이 그 색으로 물든다. 불티는 중력에
처지며 식고, 끝에는 깜빡이다(크로셋) 연기처럼 옅은 자국을 남긴다.
불티 머리는 STAR(알파 252) — 매끈한 모양에서 불티 하나하나가 네 갈래 반짝이로 다시 그려진다.
환경 변수: FW_N(장 수) · FW_RATE · FW_R(터지는 반지름 최대) · FW_K(박자당 장 수)
움직임(솟기·퍼짐·처짐·식음)은 박자로 재서 K·RATE 를 키우면 슬로모션이 되고, 빛의 깜빡임(번쩍·흰 십자·
크로셋·로켓 불똥)은 실제 시간(1박 = 2틱 = 1/30초)으로 재서 느려지지 않는다.
"""
import math
import os
import random
import subprocess
import sys
from pathlib import Path

WIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WIN))
import shape as S   # noqa: E402

REPO = WIN.parent
BASE = "4a4e8bbdcc6de5fb34470382189c6ad45303facd"   # 손대기 전 폭죽 그림이 있는 main 커밋 — 몸 모양·기호를 여기서 뜬다
SID = "firework"
EDGE = "ffe070ff"                      # 옛 그림의 테두리 색 — split 이 이걸로 테두리를 가른다
GLYPH = ("help", "busy", "pin", "person")   # 화살표 그림에 옛 기호만 얹는 칸
STAR = 252                             # smooth.STAR — 매끈한 모양에서 네 갈래 반짝이로 다시 그린다
TAU = 2 * math.pi
N = int(os.environ.get("FW_N", "48"))
RATE = int(os.environ.get("FW_RATE", "1"))
RMAX = float(os.environ.get("FW_R", "4"))
K = int(os.environ.get("FW_K", "3"))   # 한 박자를 몇 장으로 쪼개 그리나 — 2 에 FW_RATE=1 이면 60fps. 시간은 박자(N 기준)로 잰다


def hx(s: str) -> tuple:
    return tuple(bytes.fromhex(s))


def lerp(a: tuple, b: tuple, t: float) -> tuple:
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def old_art(rid: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), "show", f"{BASE}:win-cursor/art/{SID}/{rid}.txt"],
                          capture_output=True, text=True, encoding="utf-8", check=True).stdout


def split(frames):
    """(테두리 칸, 속 칸) — 몸은 모든 장에 있는 칸, 테두리는 늘 EDGE 색인 칸"""
    edge = hx(EDGE)
    body = set(frames[0])
    for f in frames[1:]:
        body &= set(f)
    outline = {p for p in body if all(f[p] == edge for f in frames)}
    return outline, sorted(body - outline)


def overlay(new_arrow: list[dict], role: list[dict], arrow: list[dict]) -> list[dict]:
    """새 화살표에 옛 기호를 얹는다. 기호 = 같은 옛 장에서 화살표와 다른 칸 (옛 박자를 새 바퀴에 편다)"""
    out = []
    for i, f in enumerate(new_arrow):
        j = i * len(role) // len(new_arrow)
        a = arrow[j % len(arrow)]
        glyph = {p: c for p, c in role[j].items() if a.get(p) != c}
        gone = {p for p in a if p not in role[j]}
        g = {p: c for p, c in f.items() if p not in gone}
        g.update(glyph)
        out.append(g)
    return out


SLOW = K * RATE / 2                    # 1박이 실제 시간(2틱)의 몇 배인가 — K=1·RATE=2 와 K=2·RATE=1 은 1, K=4·RATE=1 은 2(슬로모션)
SKY_TOP, SKY_BOT = hx("0a0f30ff"), hx("1c1848ff")      # 위는 짙은 남색, 아래는 보랏빛 지평
RIM = hx("a8b4e0ff")                                   # 은빛 테두리 — 터질 때 그 색으로 물든다
SMOKE = hx("262c56ff")                                 # 연기 자국 — 하늘과 115 안이라 매끈한 모양에선 묻힌다
ROCKET, ROCKET_TAIL = hx("fff0c0ff"), hx("c8702aff")
# 폭죽마다 (한가운데, 머리, 식는 중, 꺼져 가는). 꺼져 가는 색은 하늘과 115 안 — 매끈한 모양에선 하늘에 묻혀 사라진다
SHELLS = (
    (hx("fff8dcff"), hx("ffd24aff"), hx("ff962aff"), hx("5a3a26ff")),      # 금
    (hx("ffeaf6ff"), hx("ff5ab4ff"), hx("d8308cff"), hx("4a1a4cff")),      # 분홍
    (hx("eafffaff"), hx("4af0d8ff"), hx("20a8b8ff"), hx("0e4458ff")),      # 청록
)
UP = 6              # 로켓이 솟는 장 수
LIFE = 20           # 터진 뒤 불티가 사는 장 수
EXP = 7             # 불티가 다 퍼지는 데 걸리는 장 수
GRAV = 0.018        # 처짐 (칸/장²)


def st(c):
    return c[:3] + (STAR,)


def depth_of(ins):
    """칸마다 몸 바깥(테두리 포함)까지의 체비셰프 거리"""
    d = {}
    ring = {p for p in ins if any((p[0] + dx, p[1] + dy) not in ins for dx in (-1, 0, 1) for dy in (-1, 0, 1))}
    k, seen = 1, set(ring)
    while ring:
        for p in ring:
            d[p] = k
        k += 1
        ring = {(x + dx, y + dy) for x, y in ring for dx in (-1, 0, 1) for dy in (-1, 0, 1)} & ins - seen
        seen |= ring
    return d


def firework(frames, rid):
    outline, inner = split(frames)
    ins = set(inner)
    body = ins | set(outline)
    ys = [y for _, y in inner]
    ytop, ybot = min(ys), max(ys)
    dep = depth_of(ins)
    rng = random.Random(f"firework8/{rid}")
    # 터지는 자리 — 깊은 칸 중 서로 세 칸 넘게 떨어진 곳, 위쪽을 조금 더 친다
    cand = sorted(inner, key=lambda p: (-(dep[p] + 0.6 * (ybot - p[1]) / max(1, ybot - ytop)), p[1], p[0]))
    # 깊이 1 칸(끝·가는 곳)에서 터지면 불티가 거의 다 잘려 한 줄만 남았다 — 깊은 칸끼리 먼저, 간격을 줄여 가며
    spots = []
    for sep, need in ((3, 2), (2, 2), (3, 1), (2, 1)):
        for p in cand:
            if len(spots) < 3 and dep[p] >= need and p not in spots and \
                    all(max(abs(p[0] - q[0]), abs(p[1] - q[1])) >= sep for q in spots):
                spots.append(p)
    while len(spots) < 3:
        spots.append(spots[len(spots) % max(1, len(spots))])
    order = (0, 2, 1) if len(spots) == 3 else (0, 1, 2)
    shells = []
    for k in range(3):
        cx, cy = spots[order[k]]
        by = cy
        while (cx, by + 1) in ins:          # 로켓은 그 줄 바닥에서 솟는다
            by += 1
        R = min(RMAX, 1.6 + dep[(cx, cy)] * 1.1)
        rot = rng.uniform(0, TAU / 8)
        nsp = 8 if R >= 3 else 6
        shells.append(dict(cx=cx, cy=cy, by=by, R=R, t0=k * N // 3, cols=SHELLS[k],
                           dirs=[rot + TAU * j / nsp for j in range(nsp)],
                           speed=[rng.uniform(0.85, 1.0) for _ in range(nsp)],
                           flick=[rng.random() for _ in range(nsp)]))
    halo = {}
    for x in range(min(p[0] for p in body) - 2, max(p[0] for p in body) + 3):
        for y in range(min(p[1] for p in body) - 2, max(p[1] for p in body) + 3):
            if (x, y) in body:
                continue
            d = min(max(abs(x - q[0]), abs(y - q[1])) for q in body)
            if d <= 2:
                halo[(x, y)] = d

    out = []
    for i in range(N * K):
        f = {}
        flash, tint = 0.0, None             # 몸 번쩍임 세기와 그 색
        stars = {}                          # 이 장의 STAR 칸 → 주인 (다른 주인과 대각으로라도 닿으면 한 별로 묶인다)
        marks = []                          # (칸, 색, STAR 인가, 주인)
        rimlit = {}
        for si, s in enumerate(shells):
            a = (i / K - s["t0"]) % N
            c0, c1, c2, c3 = s["cols"]
            cx, cy = s["cx"], s["cy"]
            if a < UP:                       # 로켓 — 머리와 꼬리 두 칸, 오르며 느려진다
                v = 1 - max(0.0, 1 - (a + 1 / K) / UP) ** 1.6   # K=3 이면 a+1/K 가 오차로 UP 을 살짝 넘어 음수 거듭제곱(복소수)이 된다
                y = round(s["by"] + (cy - s["by"]) * v)
                marks.append(((cx, y), ROCKET, True, (si, "r")))
                marks.append(((cx, y + 1), ROCKET_TAIL, True, (si, "r")))
                ra = int(a * SLOW)           # 불똥은 실제 시간으로 튄다 — 로켓만 느리게 솟는다
                if ra % 2 == 0:
                    marks.append(((cx + (1 if ra % 4 == 0 else -1), y + 2), SMOKE, False, (si, "r")))
                continue
            b = a - UP
            if b >= LIFE:
                continue
            rb = b * SLOW                    # 실제 시간으로 잰 b — 번쩍·십자·크로셋은 이걸로 (느려지면 번쩍이 아니라 물듦이 된다)
            if rb < 3:                       # 번쩍 — 몸·테두리·번짐이 그 색으로
                seq, j0 = (0.26, 0.12, 0.04, 0.0), int(rb)
                k = seq[j0] + (seq[j0 + 1] - seq[j0]) * (rb - j0)
                if k > flash:
                    flash, tint = k, c1
            if rb < 1:                       # 한가운데 흰 십자 하나
                marks.append(((cx, cy), c0, True, (si, "c")))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    marks.append(((cx + dx, cy + dy), c1, True, (si, "c")))
                continue
            u = min(1.0, b / EXP)
            ease = 1 - (1 - u) ** 2
            drop = GRAV * b * b
            life = b / LIFE
            for j, th in enumerate(s["dirs"]):
                rr = (1.8 + (s["R"] - 1.8) * ease) * s["speed"][j] if s["R"] > 1.8 else s["R"] * ease
                hx_, hy_ = cx + 0.5 + rr * math.cos(th), cy + 0.5 + rr * math.sin(th) + drop
                p = (math.floor(hx_), math.floor(hy_))
                if life < 0.12:
                    col = c0
                elif life < 0.45:
                    col = c1
                elif life < 0.72:
                    col = c2
                else:
                    col = c3
                # 끝물엔 깜빡 — 불티마다 제 박자로 두 장 켜고 한 장 끈다 (크로셋)
                if life >= 0.5 and (int(rb) + int(s["flick"][j] * 3)) % 3 == 0:
                    col = None
                if p not in ins:
                    if p in outline and life < 0.45:  # 테두리에 닿은 불티는 테두리를 한 칸 달군다
                        rimlit[p] = lerp(RIM, c1, 0.7)
                    continue
                if col is not None:
                    marks.append((p, col, col != c3, (si, j)))
                # 꼬리 — 빨리 퍼질 때만 한 칸 뒤(STAR, 머리와 한 별로 묶여 길쭉한 반짝이가 된다), 지나간 자리엔 연기
                if b < EXP - 1:                  # 박자 기준 — 60fps 에서도 반 박자 일찍 끊기지 않게 (정수 b 에선 <= EXP-2 와 같다)
                    q = (math.floor(hx_ - 1.1 * math.cos(th)), math.floor(hy_ - 1.1 * math.sin(th)))
                    if q in ins and q != p:
                        marks.append((q, c2, True, (si, j)))
                elif b < LIFE - 2:
                    q = (math.floor(hx_ - 1.2 * math.cos(th)), math.floor(hy_ - 1.2 * math.sin(th) - 0.6))
                    if q in ins:
                        marks.append((q, SMOKE, False, (si, j)))

        # 칠하기 — 하늘, 번쩍, 테두리, 번짐
        for x, y in inner:
            g = (y - ytop) / max(1, ybot - ytop)
            c = lerp(SKY_TOP, SKY_BOT, g)
            if flash:
                c = lerp(c, tint, flash)
            f[(x, y)] = c
        rim = lerp(RIM, lerp(tint, (255, 255, 255, 255), 0.35), min(1.0, flash * 2.2)) if flash else RIM
        for p in outline:
            f[p] = rimlit.get(p, rim)
        if flash:
            for p, d in halo.items():
                aa = int((0xa0 if d == 1 else 0x50) * flash / 0.26)
                if aa >= 0x18:
                    f[p] = tint[:3] + (aa // 6 * 6,)
        # 연기·꼬리(불투명)부터, 그 위에 STAR 머리
        for p, c, is_star, me in sorted(marks, key=lambda m: m[2]):
            if p not in ins:
                continue
            if not is_star:
                if f[p][3] != STAR:
                    f[p] = c
                continue
            near = [stars.get((p[0] + dx, p[1] + dy)) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
            if any(o is not None and o != me for o in near):
                continue                      # 남의 반짝이와 닿으면 한 별로 뭉친다 — 이 장은 건너뛴다
                # (불투명으로 칠만 해 봤더니 매끈한 모양에서 주황 덩어리가 됐다)
            f[p] = st(c)
            stars[p] = me
        out.append(f)
    return out


def ascii(rid, lo=0, hi=16):
    fr = firework(S.read_art(old_art(rid))[0], rid)[lo:hi]
    ps = set().union(*fr)
    xs, ys = [p[0] for p in ps], [p[1] for p in ps]

    def sym(c):
        if c is None:
            return " "
        if c[3] == STAR:
            return "*"
        if c[3] < 255:
            return ","
        if c in (RIM,):
            return "#"
        if c == SMOKE:
            return "~"
        if max(c[:3]) < 90:
            return "."
        return "o"
    for y in range(min(ys), max(ys) + 1):
        print("  ".join("".join(sym(f.get((x, y))) for x in range(min(xs), max(xs) + 1)) for f in fr))


def main() -> None:
    if sys.argv[1:2] == ["--ascii"]:
        a, b = (sys.argv[3] if len(sys.argv) > 3 else "0:16").split(":")
        return ascii(sys.argv[2], int(a), int(b))
    d = REPO / "win-cursor" / "art" / SID
    roles = sys.argv[1:] or sorted(p.stem for p in d.glob("*.txt"))
    arrow_old = S.read_art(old_art("arrow"))[0]
    new_arrow = firework(arrow_old, "arrow")
    for rid in roles:
        frames, hot, rate = S.read_art(old_art(rid))
        if rid == "arrow":
            new = new_arrow
        elif rid in GLYPH:
            new = overlay(new_arrow, frames, arrow_old)
        else:
            new = firework(frames, rid)
        (d / f"{rid}.txt").write_text(S.to_text(new, hot, RATE), encoding="utf-8")
        ol, inn = split(frames)
        print(f"{SID} {rid:7} {len(frames)}장×{rate} → {len(new)}장×{RATE} ({len(new) * RATE / 60:.2f}초) 테두리 {len(ol)} 속 {len(inn)}")


if __name__ == "__main__":
    main()

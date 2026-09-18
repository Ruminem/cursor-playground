# SPDX-License-Identifier: Apache-2.0
"""매끈한 커서 모양. 윤곽을 점으로 잡아 거리함수로 그리고, 테마 색을 끼워 넣는다.

픽셀아트 테마와 달리 이쪽은 경계가 매끈하다. 만드는 순서는 이렇다.

  1. 꼭지점마다 진짜 원호를 끼워 넣어 윤곽을 둥글린다 (면취가 아니라 호여야 둥글어 보인다)
  2. 3배 격자에 부호 있는 거리함수로 칠하고 평균으로 줄인다 (안티에일리어싱)
  3. 색은 넣지 않고 칸마다 "어느 층이 얼마나 덮였는지"만 남긴다 — 이것을 스텐실이라 부른다
  4. 테마마다 그 테마 그림에서 뽑은 색을 스텐실의 층에 끼워 넣는다 (paint)

스텐실은 테마와 무관하므로 모양·칸마다 한 번만 그리면 되고, 색만 갈아 끼우는 일은 싸다.
층은 여섯 가지다: 그림자 · 번지는 빛 · 흰 테두리 · 몸(위아래 그라데이션) · 밝은 면 · 어두운 면 · 외곽선.
"""
import math
from collections import Counter

SS = 3          # 몇 배로 그린 뒤 줄일지
DESIGN = 26     # 설계 격자 높이. 실제 칸 수는 이 비율로 키워 맞춘다
# 그림은 32칸 캔버스에 1:1 로 들어가고(작은 그림은 투명으로 채움) 윈도우가 그걸 커서 크기대로 늘린다.
# 그래서 칸 수가 곧 기본 크기에서의 커서 크기다 — 테마 그림들(17~23칸)과 같은 범위로 맞춰야 한다.
# 시안 페이지의 썸네일 창이 20칸까지 보여 주는 것도 같은 값이다
LIMIT = 20

# ── 화살표 윤곽 (끝 · 어깨 · 오른쪽 홈 · 꼬리 둘 · 왼쪽 홈 · 굽) ──────────────
ARROW = [(1.3, 0.4), (19.8, 15.9), (13.6, 18.4), (17.0, 26.6), (10.4, 25.6), (8.6, 19.5), (0.2, 23.4)]
ARROW_R = [2.8, 2.0, 0.5, 1.5, 1.5, 0.5, 2.0]

# ── 화살표 말고 모양이 바꾸는 네 칸. 윤곽은 모양끼리 같이 쓰고, 칠하는 방식만 각자 따른다 ──
BAR = [(7.77, 20.77), (20.77, 7.77), (18.23, 5.23), (5.23, 18.23)]   # 금지 표시의 빗금
SLOTS = {
    "ibeam": [dict(pts=[(1.0, 0.0), (11.0, 0.0), (11.0, 2.4), (7.4, 2.4), (7.4, 23.6), (11.0, 23.6),
                        (11.0, 26.0), (1.0, 26.0), (1.0, 23.6), (4.6, 23.6), (4.6, 2.4), (1.0, 2.4)],
                   radii=[0.8] * 12, steps=4)],
    "wait": [dict(pts=[(1.0, 0.0), (19.0, 0.0), (19.0, 3.0), (11.6, 13.0), (19.0, 23.0), (19.0, 26.0),
                       (1.0, 26.0), (1.0, 23.0), (8.4, 13.0), (1.0, 3.0)],
                  radii=[1.2, 1.2, 0.8, 1.0, 0.8, 1.2, 1.2, 0.8, 1.0, 0.8], steps=5)],
    # 둥근 사각형에 반지름을 크게 주면 원이 된다. 고리로 비우고 빗금을 얹는다
    "no": [dict(pts=[(1.0, 1.0), (25.0, 1.0), (25.0, 25.0), (1.0, 25.0)], radii=[12.0] * 4, steps=9, ring=3.6),
           dict(pts=BAR, radii=[0.9] * 4, steps=4)],
    "move": [dict(pts=[(13.0, 0.4), (18.2, 5.6), (15.6, 5.6), (15.6, 10.4), (20.4, 10.4), (20.4, 7.8),
                       (25.6, 13.0), (20.4, 18.2), (20.4, 15.6), (15.6, 15.6), (15.6, 20.4), (18.2, 20.4),
                       (13.0, 25.6), (7.8, 20.4), (10.4, 20.4), (10.4, 15.6), (5.6, 15.6), (5.6, 18.2),
                       (0.4, 13.0), (5.6, 7.8), (5.6, 10.4), (10.4, 10.4), (10.4, 5.6), (7.8, 5.6)],
                  radii=[0.7] * 24, steps=3)],
}

# ── 모양 열 가지. 윤곽이 다른 것 여섯, 칠하는 방식이 다른 것 넷 ───────────────
SHAPES = {
    "round": dict(pts=ARROW, radii=ARROW_R, rscale=1.35, style="solid"),
    "hollow": dict(pts=ARROW, radii=ARROW_R, rscale=1.35, style="hollow", thick=3.4),
    "cutout": dict(pts=ARROW, radii=ARROW_R, rscale=1.35, style="sticker", band=1.8, shadow=(1.4, 2.0)),
    "blob": dict(pts=[(1.2, 0.3), (19.4, 15.8), (1.8, 25.0)], radii=[1.4, 3.0, 3.4], rscale=1.0, style="solid"),
    "comet": dict(pts=[(1.2, 0.4), (17.8, 14.2), (12.0, 16.2), (19.4, 27.4), (7.6, 18.2), (0.2, 21.6)],
                  radii=[2.6, 2.0, 0.6, 1.2, 0.6, 2.0], rscale=1.2, style="solid"),
    "needle": dict(pts=[(0.8, 0.3), (13.2, 15.0), (9.2, 16.4), (12.6, 26.0), (8.6, 26.6), (5.6, 18.0), (0.6, 22.4)],
                   radii=[1.7, 1.1, 0.3, 0.9, 0.9, 0.3, 1.1], rscale=1.3, style="solid"),
    "dart": dict(pts=[(0.8, 0.5), (19.9, 19.5), (10.2, 16.7), (7.7, 26.5)],
                 radii=[1.6, 1.6, 1.4, 1.6], rscale=1.15, style="solid"),
    "drop": dict(pts=[(1.2, 0.6), (17.0, 9.0), (19.0, 19.0), (11.0, 25.5), (2.0, 17.0)],
                 radii=[1.2, 6.0, 6.0, 6.0, 6.0], rscale=1.0, style="solid"),
    "glow": dict(pts=ARROW, radii=ARROW_R, rscale=1.35, style="solid", glow=3.2),
    "bevel": dict(pts=ARROW, radii=ARROW_R, rscale=1.0, style="solid", bevel=3.0, ew=0.7),
}
ROLES = ("arrow",) + tuple(SLOTS)   # 모양이 바꾸는 칸
EDGE_W = 1.1                        # 외곽선 두께 (설계 격자 기준)
# 층을 아래에서 위로 겹치는 순서. 한 칸 안에서 여러 층이 조금씩 겹칠 수 있다
ORDER = ("shadow", "glow", "band", "body", "lit", "dark", "edge")


def inside(pts: list, px: float, py: float) -> bool:
    c = False
    for i in range(len(pts)):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
        if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1:
            c = not c
    return c


def near(pts: list, px: float, py: float) -> tuple[float, float, float]:
    """가장 가까운 윤곽선까지의 거리와 그 위의 점"""
    best, bx, by = 1e9, px, py
    for i in range(len(pts)):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
        dx, dy = x2 - x1, y2 - y1
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        cx, cy = x1 + t * dx, y1 + t * dy
        d = math.hypot(px - cx, py - cy)
        if d < best:
            best, bx, by = d, cx, cy
    return best, bx, by


def fillet(pts: list, radii: list, steps: int = 6) -> list:
    """꼭지점마다 주어진 반지름의 원호를 윤곽선에 끼워 넣는다 (면취가 아니라 호)"""
    n = len(pts)
    out = []
    for i in range(n):
        a, b, c = pts[(i - 1) % n], pts[i], pts[(i + 1) % n]
        r = radii[i]
        v1, v2 = (a[0] - b[0], a[1] - b[1]), (c[0] - b[0], c[1] - b[1])
        l1, l2 = math.hypot(*v1) or 1, math.hypot(*v2) or 1
        u1, u2 = (v1[0] / l1, v1[1] / l1), (v2[0] / l2, v2[1] / l2)
        half = math.acos(max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1]))) / 2
        if r <= 0 or half < 0.08 or half > 1.5:
            out.append(b)
            continue
        cut = min(r / math.tan(half), l1 * 0.45, l2 * 0.45)
        r_eff = cut * math.tan(half)
        t1 = (b[0] + u1[0] * cut, b[1] + u1[1] * cut)
        t2 = (b[0] + u2[0] * cut, b[1] + u2[1] * cut)
        bis = (u1[0] + u2[0], u1[1] + u2[1])
        bl = math.hypot(*bis) or 1
        cen = (b[0] + bis[0] / bl * (r_eff / math.sin(half)), b[1] + bis[1] / bl * (r_eff / math.sin(half)))
        a1 = math.atan2(t1[1] - cen[1], t1[0] - cen[0])
        a2 = math.atan2(t2[1] - cen[1], t2[0] - cen[0])
        d = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for k in range(steps + 1):
            ang = a1 + d * k / steps
            out.append((cen[0] + math.cos(ang) * r_eff, cen[1] + math.sin(ang) * r_eff))
    return out


def parts_of(sid: str, rid: str) -> list[dict]:
    """모양·칸 하나를 이루는 부분들. 칸의 윤곽에 그 모양의 칠하는 방식을 붙인다"""
    spec = SHAPES[sid]
    raw = [dict(pts=spec["pts"], radii=spec["radii"], steps=6)] if rid == "arrow" else SLOTS[rid]
    parts = []
    for i, part in enumerate(raw):
        p = dict(part)
        p["radii"] = [r * spec["rscale"] for r in p["radii"]]
        # 금지 표시의 고리는 어느 모양에서든 비워야 금지 표시로 읽힌다
        if spec["style"] == "hollow" and "ring" not in p and rid != "no":
            p["ring"] = spec["thick"]
        p["first"] = i == 0
        parts.append(p)
    return parts


def extent(sid: str, rid: str, size: float) -> tuple[list, float, float]:
    """이 크기로 그리면 몇 칸이 되는지 (긁지 않고 윤곽만 계산한다)"""
    spec = SHAPES[sid]
    k = size / DESIGN
    grown = []
    lo = [1e9, 1e9]
    hi = [-1e9, -1e9]
    for part in parts_of(sid, rid):
        pts = fillet([(x * k, y * k) for x, y in part["pts"]],
                     [r * k for r in part["radii"]], part.get("steps", 6))
        grown.append((part, pts))
        for x, y in pts:
            lo[0], lo[1] = min(lo[0], x), min(lo[1], y)
            hi[0], hi[1] = max(hi[0], x), max(hi[1], y)
    pad = k * max(spec.get("band", 0) + max(spec.get("shadow", (0, 0))), spec.get("glow", 0))
    return grown, max(hi[0] - lo[0], hi[1] - lo[1]) + 2 * pad, pad


_cache: dict = {}


def stencil(sid: str, rid: str) -> tuple[dict, tuple[int, int]]:
    """모양·칸 하나의 스텐실과 핫스팟. 테마와 무관하므로 한 번만 그린다"""
    if (sid, rid) not in _cache:
        size = DESIGN
        for _ in range(3):   # 한 번 재면 비례해서 맞출 수 있다. 반올림 때문에 여유를 조금 둔다
            _, span, _ = extent(sid, rid, size)
            size *= (LIMIT - 0.7) / span
            if abs(span - (LIMIT - 0.7)) < 0.3:
                break
        _cache[(sid, rid)] = _draw(sid, rid, size)
    return _cache[(sid, rid)]


def _draw(sid: str, rid: str, size: float) -> tuple[dict, tuple[int, int]]:
    spec = SHAPES[sid]
    k = size / DESIGN
    parts, _, pad = extent(sid, rid, size)
    ew = EDGE_W * spec.get("ew", 1.0) * k
    bevel = spec.get("bevel", 0) * k
    band = spec.get("band", 0) * k
    glow = spec.get("glow", 0) * k
    sh_dx, sh_dy = (q * k for q in spec.get("shadow", (0, 0)))
    x0 = min(x for _, pts in parts for x, _ in pts) - pad
    y0 = min(y for _, pts in parts for _, y in pts) - pad
    x1 = max(x for _, pts in parts for x, _ in pts) + pad
    y1 = max(y for _, pts in parts for _, y in pts) + pad
    W, H = math.ceil(x1 - x0), math.ceil(y1 - y0)
    acc: dict = {}

    def add(cell, kind, a, t=0.0, k2=0.0):
        got = acc.setdefault(cell, {}).setdefault(kind, [0.0, 0.0, 0.0])
        got[0] += a
        got[1] += t * a
        got[2] += k2 * a

    for part, pts in parts:
        pts = [(x - x0, y - y0) for x, y in pts]
        ring = part.get("ring", 0) * k
        for sy in range(H * SS):
            py = (sy + 0.5) / SS
            for sx in range(W * SS):
                px = (sx + 0.5) / SS
                cell = (sx // SS, sy // SS)
                w = 1 / (SS * SS)
                d, cx, cy = near(pts, px, py)
                sd = d if inside(pts, px, py) else -d
                # 몸이 덮은 자리와, 거기서 얼마나 떨어졌는지. 고리면 안쪽 구멍도 바깥으로 센다
                far = ring or 1e9
                body_here = 0 <= sd <= far
                gap = 0.0 if body_here else (-sd if sd < 0 else sd - far)
                if glow and 0 < gap < glow:
                    g = 1 - gap / glow
                    add(cell, "glow", w * g * g * 0.65)
                if band and 0 < gap < band:
                    add(cell, "band", w)
                if sh_dx or sh_dy:
                    dsh = near(pts, px - sh_dx, py - sh_dy)[0]
                    sdsh = dsh if inside(pts, px - sh_dx, py - sh_dy) else -dsh
                    if 0 <= sdsh <= far:
                        add(cell, "shadow", w * 0.27)
                if not body_here:
                    continue
                t = min(1.0, py / H * 1.25 + px / W * 0.25)      # 빛은 왼쪽 위에서
                if sd < ew or (ring and sd > far - ew):
                    add(cell, "edge", w)
                elif bevel and sd < ew + bevel:
                    nx, ny = (cx - px) / (d or 1), (cy - py) / (d or 1)
                    lit = -(nx * 0.6 + ny * 0.8)                  # 바깥 법선이 빛을 보는지
                    amt = 0.8 * abs(lit) * (1 - (sd - ew) / bevel)
                    add(cell, "lit" if lit > 0 else "dark", w, t, amt)
                elif not ring and sd < ew * 1.6 and py > H * 0.62 and px > W * 0.45:
                    add(cell, "lit", w, t, 0.45)                  # 아래쪽 안쪽 광택
                else:
                    add(cell, "body", w, t)

    st = {}
    for cell, kinds in acc.items():
        layers = []
        for kind in ORDER:
            if kind not in kinds:
                continue
            a, ta, ka = kinds[kind]
            if a < 0.02:
                continue
            # 계조를 잘게 쪼개면 프레임마다 색이 수백 개씩 생겨 팔레트가 터진다. 눈에 안 보일 만큼만 묶는다
            layers.append((kind, round(ta / a * 12) / 12, round(ka / a * 8) / 8, round(min(1.0, a) * 24) / 24))
        if layers:
            st[cell] = layers
    return st, _hotspot(st, rid)


def _hotspot(st: dict, rid: str) -> tuple[int, int]:
    """화살표는 끝, 나머지는 가운데"""
    solid = [p for p, ls in st.items()
             if sum(a for kind, _, _, a in ls if kind not in ("glow", "shadow", "band")) > 0.55]
    if rid != "arrow":
        xs = [x for x, _ in solid]; ys = [y for _, y in solid]
        return (min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2
    ty = min(y for _, y in solid)
    return min(x for x, y in solid if y == ty), ty


def mix(a: tuple, b: tuple, t: float) -> tuple:
    t = max(0.0, min(1.0, t))
    return tuple(round(p + (q - p) * t) for p, q in zip(a[:3], b[:3]))


def over(bot: tuple | None, top: tuple) -> tuple:
    if bot is None:
        return top
    ta, ba = top[3] / 255, bot[3] / 255
    outa = ta + ba * (1 - ta)
    if outa <= 0:
        return (0, 0, 0, 0)
    return tuple(round((top[i] * ta + bot[i] * ba * (1 - ta)) / outa) for i in range(3)) + (round(outa * 255),)


N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def palette_of(frame: dict) -> tuple:
    """테마 그림 한 장에서 (위쪽 색, 아래쪽 색, 외곽선, 밝은 색)을 뽑는다"""
    solid = {p: c for p, c in frame.items() if c[3] >= 200} or dict(frame)
    rim = {p for p in solid if any((p[0] + dx, p[1] + dy) not in solid for dx, dy in N4)}
    edge = Counter(solid[p] for p in rim).most_common(1)[0][0]
    fill = {p: c for p, c in solid.items() if p not in rim} or solid
    ys = [y for _, y in fill]
    mid = (min(ys) + max(ys)) / 2
    up = [c for (_, y), c in fill.items() if y <= mid]
    dn = [c for (_, y), c in fill.items() if y > mid]
    top = Counter(up).most_common(1)[0][0] if up else edge
    bot = Counter(dn).most_common(1)[0][0] if dn else top
    gloss = max(frame.values(), key=lambda c: (c[0] + c[1] + c[2]) * (c[3] >= 200))
    return top, bot, edge, gloss


def paint(st: dict, palette: tuple) -> dict:
    """스텐실에 테마 색을 끼워 넣는다"""
    top, bot, edge, gloss = palette
    out = {}
    for cell, layers in st.items():
        col = None
        for kind, t, k2, a in layers:
            if kind == "shadow":
                rgba = (0, 0, 0, round(a * 255))
            elif kind == "glow":
                rgba = gloss[:3] + (round(a * 255),)
            elif kind == "band":
                rgba = gloss[:3] + (round(a * 255),)
            elif kind == "edge":
                rgba = edge[:3] + (round(a * edge[3]),)
            else:
                body = mix(top, bot, t)
                if kind == "lit":
                    body = mix(body, gloss, k2)
                elif kind == "dark":
                    body = mix(body, edge, k2)
                rgba = body + (round(a * 255),)
            if rgba[3] > 0:
                col = over(col, rgba)
        if col and col[3] > 3:
            out[cell] = col
    return out


def remake(sid: str, rid: str, frames: list[dict]) -> tuple[list[dict], tuple[int, int]]:
    """테마 프레임들의 색으로 이 모양의 한 칸을 그린다 (프레임마다 색을 다시 뽑아 움직임을 살린다)"""
    st, hot = stencil(sid, rid)
    return [paint(st, palette_of(f)) for f in frames], hot


if __name__ == "__main__":   # 자체 점검: 모든 모양·칸이 32칸 안에 들어오고 층이 제대로 쌓이는지
    import time

    fake = {(x, y): ((250, 250, 255, 255) if 0 < x < 9 and 0 < y < 9 else (20, 20, 30, 255))
            for x in range(10) for y in range(10)}
    for sid in SHAPES:
        t0 = time.time()
        line = []
        for rid in ROLES:
            st, hot = stencil(sid, rid)
            px = paint(st, palette_of(fake))
            w = max(x for x, _ in px) - min(x for x, _ in px) + 1
            h = max(y for _, y in px) - min(y for _, y in px) + 1
            assert max(w, h) <= 32, f"{sid}/{rid} 가 32칸을 넘음: {w}x{h}"
            assert px, f"{sid}/{rid} 가 비었음"
            line.append(f"{rid} {w}x{h}")
        print(f"{sid:8} {' · '.join(line)} · {time.time() - t0:.1f}초")

# SPDX-License-Identifier: Apache-2.0
"""매끈한 커서 모양. 윤곽을 점으로 잡아 거리함수로 그리고, 테마 그림의 색을 입힌다.

픽셀아트 테마와 달리 이쪽은 경계가 매끈하다. 만드는 순서는 이렇다.

  1. 꼭지점마다 진짜 원호를 끼워 넣어 윤곽을 둥글린다 (면취가 아니라 호여야 둥글어 보인다)
  2. 부호 있는 거리함수로 칸마다 얼마나 덮였는지 재서 경계를 매끈하게 만든다
  3. 색은 넣지 않고 칸마다 "어느 층이 얼마나 덮였는지"만 남긴다 — 이것을 스텐실이라 부른다
  4. 테마마다 그 테마 그림에서 색을 떠 스텐실의 층에 끼워 넣는다 (paint)

색은 몇 개로 줄이지 않고 **자리대로** 떠 온다 — 몸도 외곽선도 그렇다. 그래서 무늬
(표범·아가일)도, 프레임마다 무늬가 움직이는 테마(전기·글자비)도, 테두리를 타고 도는
효과(전기의 전류·글리치의 빨강청록 어긋남)도 모양만 바뀌고 성질은 남는다. 몸 바깥으로
번지는 빛(네온·야광)도 층마다 다시 둘러 준다.

커서 파일에 담는 크기는 늘리지 않고 **크기마다 새로 그린다**. 안티에일리어싱된 그림을
정수배로 늘리면 뭉개지기 때문이다. 담는 크기는 32·64·128 셋이고, 사이 크기(48·96)는
윈도우가 늘려 쓴다 — 매끈한 그림은 그래도 티가 안 난다. 시안 페이지에 넣는 그림도 같은
이유로 크게 그린다 (화살표 96칸, 나머지 64칸).
"""
import math
from collections import Counter

from make_cur import MIN_SIZE, curs_to_ani, pixels_to_png, pngs_to_cur

DESIGN = 26     # 설계 격자 높이. 실제 칸 수는 이 비율로 맞춘다
LIMIT = 20      # 32칸 판에서 몸이 차지하는 칸 수 (테마 그림들이 17~23칸이라 거기에 맞춤)
HALO = 3        # 테마의 몸 바깥 번짐을 다시 둘러 줄 층 수 (20칸 기준)
# 커서 파일에 담는 판 크기. 픽셀아트는 다섯 크기를 다 담지만(늘리면 어긋난다) 매끈한 그림은
# 윈도우가 사이 크기로 늘려도 티가 안 나서 셋만 담는다 — 파일이 38% 작아지고 빌드도 그만큼 빠르다
CUR_SIZES = (32, 64, 128)
PAGE = 96       # 시안 페이지의 화살표 판. 32칸 판의 3배라 썸네일이 1:1 로 쓴다
PAGE_SMALL = 64  # 나머지 칸은 페이지에서 작게 보여 주므로 판도 작게 (데이터 파일이 절반으로)
EDGE_W = 1.1    # 외곽선 두께 (설계 격자 기준)
UV = 31         # 테마 그림에서 색을 뜰 자리를 몇 단계로 쪼개 둘지 (테마 그림이 32칸 안이라 이 정도면 충분)
SPECK = 2       # 몸에서 떨어져 나온 조각이 이 칸 수 이하면 불꽃으로 보고 새 몸 둘레에 다시 흩는다

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
ROLES = ("arrow",) + tuple(SLOTS)   # 모양이 직접 그리는 칸
# 층을 아래에서 위로 겹치는 순서. 한 칸 안에서 여러 층이 조금씩 겹칠 수 있다
ORDER = ("shadow", "halo0", "halo1", "halo2", "glow", "band", "body", "lit", "dark", "edge")
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = N4 + ((1, 1), (-1, -1), (1, -1), (-1, 1))


def cells_for(size: int) -> int:
    """커서 판 크기에 맞는 몸의 칸 수. 32칸 판에서 LIMIT 칸을 차지하는 비율을 지킨다"""
    return max(6, round(size * LIMIT / MIN_SIZE))


def _ss(cells: int) -> int:
    """몇 배 격자로 그릴지. 칸이 크면 거리함수만으로도 경계가 충분히 매끈하다"""
    return 3 if cells <= 24 else (2 if cells <= 48 else 1)


def edges_of(pts: list) -> list:
    """변마다 (시작점, 방향, 길이제곱의 역수). 칸마다 다시 계산하면 느려서 미리 만들어 둔다"""
    out = []
    for i in range(len(pts)):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
        dx, dy = x2 - x1, y2 - y1
        out.append((x1, y1, dx, dy, 1.0 / (dx * dx + dy * dy or 1e-9)))
    return out


def inside(edges: list, px: float, py: float) -> bool:
    c = False
    for x1, y1, dx, dy, _ in edges:
        if (y1 > py) != (y1 + dy > py) and px < dx * (py - y1) / dy + x1:
            c = not c
    return c


def near(edges: list, px: float, py: float) -> tuple[float, float, float]:
    """가장 가까운 윤곽선까지의 거리와 그 위의 점. 제곱으로 비교하고 뿌리는 한 번만 뽑는다"""
    best, bx, by = 1e18, px, py
    for x1, y1, dx, dy, inv in edges:
        t = ((px - x1) * dx + (py - y1) * dy) * inv
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
        cx, cy = x1 + t * dx, y1 + t * dy
        ex, ey = px - cx, py - cy
        d = ex * ex + ey * ey
        if d < best:
            best, bx, by = d, cx, cy
    return math.sqrt(best), bx, by


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
    for part in raw:
        p = dict(part)
        p["radii"] = [r * spec["rscale"] for r in p["radii"]]
        # 금지 표시의 고리는 어느 모양에서든 비워야 금지 표시로 읽힌다
        if spec["style"] == "hollow" and "ring" not in p and rid != "no":
            p["ring"] = spec["thick"]
        parts.append(p)
    return parts


def outlines(sid: str, rid: str, size: float) -> tuple[list, float]:
    """이 크기로 그린 윤곽선들과, 그것이 차지하는 칸 수 (긁지 않고 계산한다)"""
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
    spec = SHAPES[sid]
    pad = k * max(spec.get("band", 0) + max(spec.get("shadow", (0, 0))), spec.get("glow", 0))
    return grown, max(hi[0] - lo[0], hi[1] - lo[1]) + 2 * pad


_cache: dict = {}


def stencil(sid: str, rid: str, cells: int = LIMIT) -> tuple[tuple[dict, list], tuple[int, int], tuple, set]:
    """모양·칸 하나의 (스텐실, 핫스팟, 몸이 놓인 자리, 몸이 덮은 칸). 테마와 무관해 한 번만 그린다"""
    rid = rid if rid in ROLES else "arrow"   # 기호를 얹는 칸(도움말·백그라운드 작업 등)은 화살표를 쓴다
    key = (sid, rid, cells)
    if key not in _cache:
        size = DESIGN
        for _ in range(3):   # 한 번 재면 비례해서 맞출 수 있다. 반올림 때문에 여유를 조금 둔다
            _, span = outlines(sid, rid, size)
            size *= (cells - 0.7) / span
            if abs(span - (cells - 0.7)) < 0.3:
                break
        _cache[key] = _draw(sid, rid, size, cells)
    return _cache[key]


def _draw(sid: str, rid: str, size: float, cells: int) -> tuple[tuple[dict, list], tuple[int, int], tuple, set]:
    spec = SHAPES[sid]
    k = size / DESIGN
    ss = _ss(cells)
    parts, _ = outlines(sid, rid, size)
    ew = EDGE_W * spec.get("ew", 1.0) * k
    bevel = spec.get("bevel", 0) * k
    band = spec.get("band", 0) * k
    glow = spec.get("glow", 0) * k
    halo = HALO * cells / LIMIT                      # 테마 번짐 층도 크기에 맞춰 두꺼워진다
    sh_dx, sh_dy = (q * k for q in spec.get("shadow", (0, 0)))
    pad = max(band + max(sh_dx, sh_dy), glow, halo) + 1
    x0 = min(x for _, pts in parts for x, _ in pts) - pad
    y0 = min(y for _, pts in parts for _, y in pts) - pad
    x1 = max(x for _, pts in parts for x, _ in pts) + pad
    y1 = max(y for _, pts in parts for _, y in pts) + pad
    W, H = math.ceil(x1 - x0), math.ceil(y1 - y0)
    acc: dict = {}
    body_cells = set()

    def add(cell, kind, a, t=0.0, k2=0.0):
        got = acc.setdefault(cell, {}).setdefault(kind, [0.0, 0.0, 0.0])
        got[0] += a
        got[1] += t * a
        got[2] += k2 * a

    for part, pts in parts:
        edges = edges_of([(x - x0, y - y0) for x, y in pts])
        ring = part.get("ring", 0) * k
        for sy in range(H * ss):
            py = (sy + 0.5) / ss
            for sx in range(W * ss):
                px = (sx + 0.5) / ss
                cell = (sx // ss, sy // ss)
                w = 1 / (ss * ss)
                d, cx, cy = near(edges, px, py)
                sd = d if inside(edges, px, py) else -d
                # 몸이 덮은 자리와, 거기서 얼마나 떨어졌는지. 고리면 안쪽 구멍도 바깥으로 센다
                far = ring or 1e9
                gap = 0.0 if 0 <= sd <= far else (-sd if sd < 0 else sd - far)
                # 경계에 걸친 칸은 부호거리로 덮인 만큼만 센다 (이것이 안티에일리어싱)
                frac = min(1.0, max(0.0, sd * ss + 0.5))
                if ring:
                    frac = min(frac, min(1.0, max(0.0, (far - sd) * ss + 0.5)))
                if 0 < gap <= halo:
                    add(cell, f"halo{min(HALO - 1, int(gap / halo * HALO))}", w)
                if glow and 0 < gap < glow:
                    g = 1 - gap / glow
                    add(cell, "glow", w * g * g * 0.65)
                if band and 0 < gap < band:
                    add(cell, "band", w * min(1.0, max(0.0, (band - gap) * ss + 0.5)))
                if sh_dx or sh_dy:
                    dsh = near(edges, px - sh_dx, py - sh_dy)[0]
                    sdsh = dsh if inside(edges, px - sh_dx, py - sh_dy) else -dsh
                    if sdsh > -0.5 and (not ring or sdsh <= far):
                        add(cell, "shadow", w * 0.27 * min(1.0, max(0.0, sdsh * ss + 0.5)))
                if frac <= 0:
                    continue
                w *= frac
                if frac > 0.5:
                    body_cells.add(cell)
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

    made = {}
    for cell, kinds in acc.items():
        layers = []
        for kind in ORDER:
            if kind not in kinds:
                continue
            a, ta, ka = kinds[kind]
            if a < 0.02:
                continue
            # 계조를 잘게 쪼개면 색이 수백 개씩 생긴다. 눈에 안 보일 만큼만 묶는다
            layers.append((kind, round(ta / a * 12) / 12, round(ka / a * 8) / 8, round(min(1.0, a) * 24) / 24))
        if layers:
            made[cell] = tuple(layers)
    # 왼쪽 위를 (0,0) 으로 당긴다
    ox = min(x for x, _ in made)
    oy = min(y for _, y in made)
    body = {(x - ox, y - oy) for x, y in body_cells}
    bx0, by0 = min(x for x, _ in body), min(y for _, y in body)
    box = (bx0, by0, max(x for x, _ in body) - bx0 + 1, max(y for _, y in body) - by0 + 1)
    # 칸마다 (칠하는 방법 번호, 테마 그림에서 색을 뜰 자리)만 남긴다. 같은 값이면 색을 한 번만
    # 계산하고 돌려 쓰므로, 큰 판에서도 색 계산이 몇백 번으로 끝난다
    recipes: dict = {}
    st = {}
    for (x, y), layers in made.items():
        cx, cy = x - ox, y - oy
        iu = min(UV, max(0, round((cx - bx0) / max(1, box[2] - 1) * UV)))
        iv = min(UV, max(0, round((cy - by0) / max(1, box[3] - 1) * UV)))
        st[(cx, cy)] = (recipes.setdefault(layers, len(recipes)), iu, iv)
    return (st, [k for k, _ in sorted(recipes.items(), key=lambda kv: kv[1])]), _hotspot(body, rid), box, body


def _hotspot(body: set, rid: str) -> tuple[int, int]:
    """화살표는 끝, 나머지는 가운데"""
    if rid != "arrow":
        xs = [x for x, _ in body]; ys = [y for _, y in body]
        return (min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2
    ty = min(y for _, y in body)
    return min(x for x, y in body if y == ty), ty


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


def ring_of(mask) -> set:
    return {(x + dx, y + dy) for (x, y) in mask for dx, dy in N8} - set(mask)


def nearest(points: set, box: tuple) -> dict:
    """box 안 모든 칸에서 가장 가까운 points 원소 (가장자리에서 안쪽으로 번져 나가며 찾는다)"""
    x0, y0, x1, y1 = box
    best = {p: p for p in points}
    frontier = list(points)
    while frontier:
        nxt = []
        for p in frontier:
            for dx, dy in N8:
                q = (p[0] + dx, p[1] + dy)
                if x0 - 1 <= q[0] <= x1 + 1 and y0 - 1 <= q[1] <= y1 + 1 and q not in best:
                    best[q] = best[p]
                    nxt.append(q)
        frontier = nxt
    return best


def blobs_of(solid) -> list[set]:
    """이어진 덩어리들 (큰 것부터). 대각선은 안 잇는다 — 이어 버리면 몸에 닿은 불꽃까지 몸이 된다"""
    left, out = set(solid), []
    while left:
        cur = {left.pop()}
        frontier = list(cur)
        while frontier:
            nxt = []
            for x, y in frontier:
                for dx, dy in N4:
                    q = (x + dx, y + dy)
                    if q in left:
                        left.discard(q)
                        cur.add(q)
                        nxt.append(q)
            frontier = nxt
        out.append(cur)
    return sorted(out, key=len, reverse=True)


def specks_of(solid: dict) -> tuple[list, dict]:
    """몸에서 떨어져 나온 작은 조각(전기 불꽃·눈송이·꽃잎)을 몸과 갈라 놓는다.

    자리는 몸 테두리 기준 비율로 남긴다. 몸을 새로 그려도 같은 자리에 흩을 수 있다.
    큰 조각이 하나라도 있으면 그 그림은 원래 끊어 그린 것(손그림·점선)이라 보고 건드리지 않는다."""
    parts = blobs_of(solid)
    rest = parts[1:]
    if not rest or any(len(b) > SPECK for b in rest) or sum(len(b) for b in rest) * 8 > len(parts[0]):
        return [], solid
    body = parts[0]
    xs = [x for x, _ in body]; ys = [y for _, y in body]
    x0, y0 = min(xs), min(ys)
    w, h = max(1, max(xs) - x0), max(1, max(ys) - y0)
    specks = [((x - x0) / w, (y - y0) / h, solid[(x, y)]) for b in rest for x, y in b]
    return specks, {p: solid[p] for p in body}


def sampler_of(frame: dict) -> tuple:
    """테마 그림 한 장에서 색을 뜨는 도구 — 몸 색, 외곽선 대표색, 가장 밝은 색, 번짐 층, 불꽃, 외곽선 색"""
    solid = {p: c for p, c in frame.items() if c[3] >= 200} or dict(frame)
    specks, solid = specks_of(solid)
    rim = {p for p in solid if any((p[0] + dx, p[1] + dy) not in solid for dx, dy in N4)}
    edge = Counter(solid[p] for p in rim).most_common(1)[0][0]
    fill = {p: c for p, c in solid.items() if p not in rim} or solid
    xs = [x for x, _ in fill]; ys = [y for _, y in fill]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    found = nearest(set(fill), (x0, y0, x1, y1))
    gloss = max(frame.values(), key=lambda c: (c[0] + c[1] + c[2]) * (1 if c[3] >= 200 else 0))
    # 몸 바깥 번짐: 층마다 반 넘게 차 있으면 그 층의 가장 흔한 색을 번짐으로 본다
    halo, grown = [], set(solid)
    for _ in range(HALO):
        r = ring_of(grown)
        grown |= r
        got = [frame[p] for p in r if p in frame]
        halo.append(Counter(got).most_common(1)[0][0] if got and len(got) * 2 >= len(r) else None)

    def at(u: float, v: float) -> tuple:
        return fill[found[(round(x0 + u * (x1 - x0)), round(y0 + v * (y1 - y0)))]]

    # 외곽선도 몸처럼 자리대로 뜬다. 한 색으로 묶으면 테두리를 타고 도는 무늬가 프레임마다
    # 통째로 한 색이 되어 사라진다 (전기의 전류, 글리치의 빨강·청록 어긋남)
    exs = [x for x, _ in rim]; eys = [y for _, y in rim]
    ex0, ey0, ex1, ey1 = min(exs), min(eys), max(exs), max(eys)
    efound = nearest(rim, (ex0, ey0, ex1, ey1))

    def edge_at(u: float, v: float) -> tuple:
        return solid[efound[(round(ex0 + u * (ex1 - ex0)), round(ey0 + v * (ey1 - ey0)))]]

    return at, edge, gloss, halo, specks, edge_at


def _color(layers: tuple, iu: int, iv: int, sampler: tuple) -> tuple | None:
    """칠하는 방법 하나를 테마 색으로 풀어 한 칸의 색을 만든다"""
    at, edge, gloss, halo, _, edge_at = sampler
    col = None
    for kind, t, k2, a in layers:
        if kind == "shadow":
            rgba = (0, 0, 0, round(a * 255))
        elif kind[0] == "h":                       # halo0 · halo1 · halo2
            c = halo[int(kind[4])]
            if not c:
                continue                           # 번짐이 없는 테마면 그 층은 비워 둔다
            rgba = c[:3] + (round(a * c[3]),)
        elif kind in ("glow", "band"):
            rgba = gloss[:3] + (round(a * 255),)
        elif kind == "edge":
            c = edge_at(iu / UV, iv / UV)
            rgba = c[:3] + (round(a * c[3]),)
        else:
            c = at(iu / UV, iv / UV)
            k = 1 - 0.15 * t                       # 아래로 갈수록 살짝 어둡게
            body = (min(255, round(c[0] * k)), min(255, round(c[1] * k)), min(255, round(c[2] * k)))
            if kind == "lit":
                body = mix(body, gloss, k2)
            elif kind == "dark":
                body = mix(body, edge, k2)
            rgba = body + (round(a * c[3]),)
        if rgba[3] > 0:
            col = over(col, rgba)
    return col if col and col[3] > 3 else None


MISS = object()


def paint(stencil: tuple, sampler: tuple, memo: dict | None = None) -> dict:
    """스텐실에 테마 색을 끼워 넣는다. 몸의 색은 테마 그림의 같은 비율 자리에서 뜬다.

    memo 를 주면 칠하는 방법이 같은 칸의 색을 크기를 넘어서도 돌려 쓴다 (한 프레임 안에서)."""
    st, recipes = stencil
    if memo is None:
        memo = {}
    out = {}
    for cell, (n, iu, iv) in st.items():
        layers = recipes[n]
        key = (layers, iu, iv)
        col = memo.get(key, MISS)
        if col is MISS:
            col = memo[key] = _color(layers, iu, iv, sampler)
        if col:
            out[cell] = col
    return out


def scale_up(px: dict, f: float) -> dict:
    """픽셀 그림을 f 배로 키운다 (최근접). 테마 기호를 큰 판에 얹을 때 쓴다"""
    if f <= 1.0:
        return px
    n = math.ceil(f)
    big = {}
    for (x, y), c in px.items():
        bx, by = int(x * f), int(y * f)
        for dy in range(n):
            for dx in range(n):
                big[(bx + dx, by + dy)] = c
    return big


def specks(marks: list, box: tuple, cells: int) -> dict:
    """불꽃을 새 몸 테두리 기준 같은 비율 자리에 다시 흩는다 (칸이 크면 조각도 그만큼 커진다)"""
    bx, by, bw, bh = box
    n = max(1, round(cells / LIMIT))
    out = {}
    for u, v, c in marks:
        px, py = bx + round(u * (bw - 1)), by + round(v * (bh - 1))
        for dy in range(n):
            for dx in range(n):
                out[(px + dx, py + dy)] = c
    return out


def draw(sid: str, rid: str, samplers: list, cells: int, glyphs: list | None = None,
         memos: list | None = None) -> tuple[list[dict], tuple[int, int]]:
    """이 칸 수로 프레임들을 그린다. glyphs 를 주면 기본 칸 수 기준으로 잡은 기호를 같이 얹는다"""
    st, hot, box, solid = stencil(sid, rid, cells)
    out = [paint(st, s, memos[i] if memos else None) for i, s in enumerate(samplers)]
    # 불꽃은 번짐 위에 얹되 몸은 덮지 않는다 (덮으면 모양이 갉아먹힌다)
    out = [{**px, **{p: c for p, c in specks(s[4], box, cells).items() if p not in solid}} if s[4] else px
           for px, s in zip(out, samplers)]
    if glyphs:
        f = cells / LIMIT
        out = [{**px, **scale_up(g, f)} for px, g in zip(out, glyphs)]
    # 프레임마다 자리가 어긋나면 커서가 떨린다. 모든 프레임을 같은 만큼 왼쪽 위로 당긴다
    ox = min(x for px in out for x, _ in px)
    oy = min(y for px in out for _, y in px)
    out = [{(x - ox, y - oy): c for (x, y), c in px.items()} for px in out]
    return out, (hot[0] - ox, hot[1] - oy)


def _fit(px: dict, size: int) -> dict:
    return {p: c for p, c in px.items() if 0 <= p[0] < size and 0 <= p[1] < size}


def cursor(sid: str, rid: str, frames: list[dict], rate: int, glyphs: list | None = None) -> tuple[bytes, str]:
    """커서 파일 하나. 크기마다 새로 그려 담는다 (늘리면 뭉개진다)"""
    samplers = [sampler_of(f) for f in frames]
    memos = [{} for _ in frames]
    per_size = []
    for size in CUR_SIZES:
        pxs, hot = draw(sid, rid, samplers, cells_for(size), glyphs, memos)
        per_size.append([(pixels_to_png(_fit(px, size), size), hot) for px in pxs])
    curs = [pngs_to_cur([per_size[i][fi] for i in range(len(CUR_SIZES))]) for fi in range(len(frames))]
    return (curs_to_ani(curs, rate), "ani") if len(frames) > 1 else (curs[0], "cur")


def page(sid: str, rid: str, frames: list[dict], glyphs: list | None = None) -> tuple[list[bytes], tuple[int, int], tuple[int, int]]:
    """시안 페이지용 (프레임별 PNG, 핫스팟, 칸 수). 그림은 PAGE 판으로 크게 그린다"""
    samplers = [sampler_of(f) for f in frames]
    memos = [{} for _ in frames]
    base, hot = draw(sid, rid, samplers, LIMIT, glyphs, memos)
    wide = max(x for px in base for x, _ in px) + 1
    tall = max(y for px in base for _, y in px) + 1
    board = PAGE if rid == "arrow" else PAGE_SMALL
    pxs, _ = draw(sid, rid, samplers, cells_for(board), glyphs, memos)
    return [pixels_to_png(_fit(px, board), board) for px in pxs], hot, (wide, tall)


def base_box(sid: str, rid: str) -> tuple:
    """기본 칸 수로 그린 몸의 자리. 테마 기호를 어디에 놓을지 계산할 때 쓴다"""
    return stencil(sid, rid, LIMIT)[2]


if __name__ == "__main__":   # 자체 점검: 모든 모양·칸이 판 안에 들어오고 층이 제대로 쌓이는지
    import time

    fake = {(x, y): ((250, 250, 255, 255) if 0 < x < 9 and 0 < y < 9 else (20, 20, 30, 255))
            for x in range(10) for y in range(10)}
    SPARK = (255, 0, 0, 255)
    fake[(12, 4)] = SPARK                                  # 몸에서 떨어져 나온 불꽃 한 점
    moving = [fake, {p: (c[0], c[1] // 2, c[2], c[3]) for p, c in fake.items()}]
    marks, body = specks_of(fake)
    assert len(marks) == 1 and (12, 4) not in body, f"불꽃을 몸과 못 갈랐다: {marks}"
    got = draw("round", "arrow", [sampler_of(fake)], LIMIT)[0][0]
    assert sum(1 for c in got.values() if c == SPARK) >= 1, "불꽃이 새 모양에서 사라졌다"
    for sid in SHAPES:
        t0 = time.time()
        line = []
        for rid in ROLES:
            blob, ext = cursor(sid, rid, moving, 6)
            assert ext == "ani" and blob[:4] == b"RIFF", f"{sid}/{rid} 움직이는 커서가 아님"
            pngs, hot, (w, h) = page(sid, rid, [fake])
            assert max(w, h) <= MIN_SIZE, f"{sid}/{rid} 가 {MIN_SIZE}칸을 넘음: {w}x{h}"
            assert 0 <= hot[0] < w and 0 <= hot[1] < h, f"{sid}/{rid} 핫스팟이 그림 밖: {hot}"
            line.append(f"{rid} {w}x{h}")
        print(f"{sid:8} {' · '.join(line)} · {time.time() - t0:.1f}초")

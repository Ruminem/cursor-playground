# SPDX-License-Identifier: Apache-2.0
"""매끈한 모양의 돔 음영과 무늬 섞기가 실제로 일하는지 본다.

**음영을 끈 같은 그림과 견준다.** 그냥 "왼쪽 위가 오른쪽 아래보다 밝다"만 보면 안 된다 —
테마 그림 자체가 위쪽이 밝고 `_color` 에도 세로 그라데이션이 따로 있어서, 빛을 반대로
뒤집어도 절반은 통과한다. 끈 것과의 차이만 보아야 이 코드가 한 일이 걸린다.

몸 색을 **곱해서** 명암을 내는 것이 요점이다. 예전처럼 테마의 가장 밝은 색으로 섞으면,
그 색이 곧 몸 색인 2색 테마(분홍·잉크)에서는 아무 일도 일어나지 않았다.

사용법: python test_light.py — 몇 초 안에 끝난다.
"""
import shape as shapelib
import smooth as sm

CELLS = sm.cells_for(96)
# 세기만 0 으로 만든다. DOME 이나 SHADOW 까지 끄면 그림 상자가 달라져 **다른 칸끼리** 비교하게 된다
FLAT = dict(SHADE=0.0, SPEC=0.0)


def render(shape: str, sid: str, flat: bool) -> dict:
    # 전역 상수만 0 으로 해서는 안 꺼진다 — bevel 처럼 제 값을 적어 둔 모양은 그것을 쓴다
    keep, spec = {k: getattr(sm, k) for k in FLAT}, sm.SHAPES[shape]
    own = {k.lower(): spec[k.lower()] for k in FLAT if k.lower() in spec}
    if flat:
        for k, v in FLAT.items():
            setattr(sm, k, v)
            spec[k.lower()] = v
    sm._cache.clear()
    try:
        frames = shapelib.read_art(open(f"art/{sid}/arrow.txt", encoding="utf-8").read())[0]
        return sm.draw(shape, "arrow", sm.samplers_of(frames), CELLS)[0][0]
    finally:
        for k, v in keep.items():
            setattr(sm, k, v)
            spec.pop(k.lower(), None)
        spec.update(own)
        sm._cache.clear()


def mean(px: dict, cells: set) -> float:
    vals = [sum(px[p][:3]) / 3 for p in cells if p in px and px[p][3] > 200]
    assert vals, "고른 자리에 불투명한 몸 칸이 없음"
    return sum(vals) / len(vals)


fails = []
for sid in ("pink", "ink", "chrome", "gameboy", "candy"):   # 2색 둘·5색·4색·무늬
    for shape in ("round", "bevel", "drop"):
        lit, flat = render(shape, sid, False), render(shape, sid, True)
        # 자리는 **그린 그림에서** 잡는다. stencil 의 body 는 원점이 draw() 와 달라 어긋난다
        body = {p for p, c in flat.items() if c[3] > 200}
        # 외곽선에 닿은 칸은 테마 색을 그대로 써서 명암과 무관하다. 두 칸 이상 안쪽만 본다
        inner = {p for p in body if all((p[0] + dx, p[1] + dy) in body
                                        for dx in (-2, -1, 1, 2) for dy in (-2, -1, 1, 2))}
        xs = [x for x, _ in body]; ys = [y for _, y in body]
        mx, my = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        up = {p for p in inner if p[0] < mx and p[1] < my}
        down = {p for p in inner if p[0] > mx and p[1] > my}
        base = mean(flat, down)                    # 음영을 끈 그 자리의 몸 밝기
        du, dd = mean(lit, up) - mean(flat, up), mean(lit, down) - mean(flat, down)
        print(f"{shape:6} {sid:8} 왼쪽 위 {du:+6.1f} · 오른쪽 아래 {dd:+6.1f} · 폭 {du - dd:5.1f} · 바탕 {base:5.1f}")
        if du < 3:
            fails.append(f"{shape}/{sid}: 왼쪽 위가 밝아지지 않음 ({du:+.1f})")
        # 몸이 이미 검으면 곱셈으로는 더 내려갈 데가 없다 (잉크는 바탕이 10 남짓). 거기서는
        # 아래가 밝아지지만 않으면 된다 — 부피감은 바로 아래 '폭' 이 맡는다
        if dd > (2 if base < 40 else -1):
            fails.append(f"{shape}/{sid}: 오른쪽 아래가 어두워지지 않음 ({dd:+.1f}, 바탕 {base:.0f})")
        # 검은 몸(잉크·매트릭스)은 더 어두워질 여지가 작다. 한쪽 값이 아니라 **폭**을 본다
        if du - dd < 10:
            fails.append(f"{shape}/{sid}: 명암 폭이 너무 좁음 ({du - dd:.1f})")
assert not fails, "돔 음영이 몸을 부풀리지 않음 — " + " · ".join(fails)
print("돔 음영 OK — 켠 쪽이 왼쪽 위는 밝고 오른쪽 아래는 어둡다")


# ── 무늬 섞기 ────────────────────────────────────────────────────────────────
# 그림이 17x11 칸뿐이라 칸 하나를 그대로 쓰면 어느 크기로 그려도 무늬 한 칸이 폭의 9% 를
# 차지해 네모로 보인다. 둘러싼 네 칸을 섞되 **대비가 큰 이웃은 빼고** 섞는 것이 요점이다 —
# 쿠키의 초코칩이나 민트초코의 체크는 저해상도가 아니라 그 구성표의 무늬라서 펴면 죽는다.
# 그래서 "색이 늘었나" 하나만 보면 안 되고, 계조 쪽과 무늬 쪽의 늘어난 정도를 견줘야 한다.

def colors(sid: str, pat: float) -> set:
    """이 구성표를 그렸을 때 몸에 나온 색들. PATTERN 만 바꿔 두 번 부른다"""
    keep = sm.PATTERN
    sm.PATTERN = pat
    sm._cache.clear()
    try:
        frames = shapelib.read_art(open(f"art/{sid}/arrow.txt", encoding="utf-8").read())[0]
        px = sm.draw("drop", "arrow", sm.samplers_of(frames), CELLS)[0][0]
        return {c for c in px.values() if c[3] > 240}
    finally:
        sm.PATTERN = keep
        sm._cache.clear()


off = {sid: colors(sid, 0.0) for sid in ("chrome", "mintchoco", "pink")}
on = {sid: colors(sid, sm.PATTERN) for sid in off}
rate = {sid: len(on[sid]) / len(off[sid]) for sid in off}
for sid in off:
    print(f"{sid:10} 섞기 끔 {len(off[sid]):4} → 켬 {len(on[sid]):4} · {rate[sid]:.2f}배")

# 1. 계조가 있는 구성표는 중간색이 실제로 생겨야 한다 (PATTERN=0 으로 돌리면 1.00 배라 걸린다)
assert rate["chrome"] > 2.0, f"크롬의 명암 계단이 안 펴짐 ({rate['chrome']:.2f}배)"
# 2. 대비가 큰 두 색짜리는 한 색도 늘면 안 된다 — KEEP 이 너무 크면 여기서 걸린다
assert on["pink"] == off["pink"], f"분홍의 두 색이 섞임 ({len(on['pink']) - len(off['pink'])}색 늘어남)"
# 3. 무늬가 있는 쪽은 계조 쪽보다 덜 건드려져야 한다. 체크무늬가 펴지면 이 비가 뒤집힌다
assert rate["mintchoco"] < rate["chrome"], \
    f"민트초코의 체크가 크롬만큼 펴짐 ({rate['mintchoco']:.2f} vs {rate['chrome']:.2f})"
print("무늬 섞기 OK — 계조는 펴지고 무늬와 2색 구성표는 그대로다")


# ── 접힘 (음영이 중심축에서 끊기는가) ────────────────────────────────────────
# 돔 음영의 법선을 "가장 가까운 윤곽선 점을 향한 방향"으로 잡으면, 두 변이 똑같이 가까운
# 자리(중심축)에서 방향이 뚝 끊겨 종이접기 같은 금이 간다. 색 계조가 아니라 **기하**의 문제라
# QUANT 를 올려도 안 없어진다 — 그래서 여기서는 QUANT 를 올려 계조 잡음을 빼고 기하만 본다.
#
# 재는 것: 몸 안쪽 칸의 밝기 라플라시안(4L - 이웃 넷). 매끈한 장은 2차 미분이 작고,
# 금이 있으면 그 선을 따라 크게 튄다. 몸 색이 한 가지인 구성표라야 밝기 변화가 음영뿐이다.

def crease(shape: str, sid: str) -> tuple[float, float]:
    """(라플라시안 99분위, 최대). 몸 색이 고른 구성표로만 부른다"""
    keep = sm.QUANT
    sm.QUANT = 255                                   # 계조 잡음을 빼고 기하만 본다
    sm._cache.clear()
    try:
        frames = shapelib.read_art(open(f"art/{sid}/arrow.txt", encoding="utf-8").read())[0]
        px = sm.draw(shape, "arrow", sm.samplers_of(frames), CELLS)[0][0]
    finally:
        sm.QUANT = keep
        sm._cache.clear()
    lum = {p: sum(c[:3]) / 3 for p, c in px.items() if c[3] > 250}
    # **몸 색인 칸만** 남긴다. 불투명한 칸으로만 거르면 화살표 홈을 지나는 검은 외곽선(밝기 2)이
    # 몸 안쪽에 그대로 남아, 테 대비를 접힘으로 잘못 센다 — 처음에 그래서 고치기 전후가 똑같이 나왔다
    med = sorted(lum.values())[len(lum) // 2]
    body = {p for p, v in lum.items() if abs(v - med) < 0.45 * med + 25}
    inner = {p for p in body if all((p[0] + dx, p[1] + dy) in body
                                    for dx in range(-3, 4) for dy in range(-3, 4))}
    laps = sorted(abs(4 * lum[p] - sum(lum[(p[0] + dx, p[1] + dy)] for dx, dy in sm.N4))
                  for p in inner if all((p[0] + dx, p[1] + dy) in lum for dx, dy in sm.N4))
    assert len(laps) > 50, f"{shape}/{sid}: 안쪽 칸이 {len(laps)}개뿐이라 잴 수 없음"
    return laps[int(len(laps) * 0.99)], laps[-1]


# 뭉개기를 끈 것과 **쌍으로** 잰다. 한쪽만 재면 이 값이 큰 건지 작은 건지 알 수 없다
worst = 0.0
for shape in ("round", "dart", "needle", "drop"):
    keep = sm.BLUR
    sm.BLUR = 0.0
    try:
        raw99, rawmax = crease(shape, "pink")
    finally:
        sm.BLUR = keep
    p99, top = crease(shape, "pink")
    print(f"{shape:6} 접힘 99분위 {raw99:6.1f} → {p99:5.1f} · 최대 {rawmax:6.1f} → {top:5.1f}"
          f" · {p99 / raw99:.2f}배")
    worst = max(worst, p99 / raw99)
    # 두 자로 본다. **비율**은 눈금(돔 크기·판 크기)이 달라져도 뜻이 같고, **절대값**은
    # 비율만 봤을 때 원본까지 같이 나빠지면 통과해 버리는 구멍을 막는다.
    # 실측(BLUR=0.30): 비율 0.08~0.19 · 최대 13.7~21.0, 뭉개기를 끄면 119~182.
    # BLUR 를 0.10 으로 낮추면 최대가 54~88 이라 둘 다 걸린다
    if p99 / raw99 > 0.35:
        fails.append(f"{shape}: 뭉개기가 접힘을 못 누름 ({p99 / raw99:.2f}배)")
    if top > 30:
        fails.append(f"{shape}: 음영에 금이 남음 (최대 {top:.1f})")
assert not fails, "음영이 중심축에서 끊김 — " + " · ".join(fails)
print(f"접힘 OK — 뭉개기가 99분위를 최악 {worst:.2f}배로 눌렀고 어디에도 금이 없다")


# ── 재질이 제일 작은 판에서도 갈리는가 ──────────────────────────────────────
# 재질은 칠할 때만 갈린다(stencil 은 하나라 모양이 같다). 큰 판에서 달라 보이는 건 당연하고,
# 물어볼 것은 **32px 에서도 갈리는가** 다 — 윈도우 기본 커서가 32px 이라 거기서 안 보이면
# 없는 기능에 빌드 시간만 쓰는 셈이다.
# 재는 것: 같은 그림을 재질만 바꿔 그려 겹치는 몸 칸의 색차(0..255).

def by_mat(sid: str, mat: str | None, cells: int) -> dict:
    frames = shapelib.read_art(open(f"art/{sid}/arrow.txt", encoding="utf-8").read())[0]
    return sm.draw("round", "arrow", sm.samplers_of(frames, mat), cells)[0][0]


def gap(a: dict, b: dict) -> tuple[float, float]:
    """(95분위 색차, 최대). 평균은 넓은 평면에 묻혀 쓸모가 없고, 하이라이트는 칸이 적어
    95분위도 못 볼 수 있다 — 그래서 최대까지 본다"""
    ps = [p for p in a if p in b and a[p][3] > 200 and b[p][3] > 200]
    assert len(ps) > 40, f"겹치는 몸 칸이 {len(ps)}개뿐이라 잴 수 없음"
    ds = sorted(sum(abs(a[p][i] - b[p][i]) for i in range(3)) / 3 for p in ps)
    return ds[int(len(ds) * 0.95)], ds[-1]


best: dict = {}   # 재질마다 **잘 드러나는 쪽** 구성표의 값. 어디서도 안 드러나면 걸린다
# 구성표 둘로 잰다. 분홍은 몸이 한 색이라 **명암** 차이가 그대로 보이고, 크롬은 광택색이
# 몸색과 멀어 **광택** 차이가 보인다. 분홍만 재면 광택만 다른 재질(매트)이 묻힌다
for sid in ("pink", "chrome"):
    for size in (32, 128):
        base = by_mat(sid, "plastic", sm.cells_for(size))
        gaps = {m: gap(base, by_mat(sid, m, sm.cells_for(size)))
                for m in sm.MATERIALS if m != "plastic"}
        print(f"{sid:7}{size:4}px 재질 색차(95분위/최대) "
              + " · ".join(f"{m} {v:4.1f}/{q:4.1f}" for m, (v, q) in gaps.items()))
        if size == 32:
            for m, (v, q) in gaps.items():
                best[m] = max(best.get(m, 0.0), q)
for m, q in best.items():
    if q < 8.0:
        fails.append(f"{m}: 32px 에서 어느 구성표로도 플라스틱과 구분이 안 됨 (95분위 {q:.1f})")
assert not fails, "재질이 작은 판에서 사라짐 — " + " · ".join(fails)
print("재질 OK — 32px 에서도 다섯 가지가 플라스틱과 갈린다")


# ── 불꽃이 네모인가 둥근 점인가 ─────────────────────────────────────────────
# 원본 그림 한 칸을 n×n 네모로 늘려 찍으면 큰 판에서 9×9 각진 딱지가 되어, 매끈해진 몸 옆에
# 혼자 픽셀로 남는다. 판이 커져도 둥글어야 한다 — 가운데는 진하고 네 모서리는 비어야 한다.
dot = sm.specks([(0.5, 0.5, (255, 255, 255, 255))], (0, 0, 40, 40), sm.LIMIT * 9)
xs = [x for x, _ in dot]; ys = [y for _, y in dot]
x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
mid = dot[((x0 + x1) // 2, (y0 + y1) // 2)][3]
corner = max(dot.get(p, (0, 0, 0, 0))[3] for p in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)))
print(f"불꽃 {x1 - x0 + 1}칸 · 가운데 {mid} · 모서리 {corner}")
assert mid > 240 and corner < 40, f"불꽃이 둥글지 않음 (가운데 {mid} · 모서리 {corner})"
print("불꽃 OK — 네모가 아니라 둥근 점이다")

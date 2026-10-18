# SPDX-License-Identifier: Apache-2.0
"""매끈한 모양의 돔 음영과 무늬 섞기가 실제로 일하는지 본다.

**음영을 끈 같은 그림과 견준다.** 그냥 "왼쪽 위가 오른쪽 아래보다 밝다"만 보면 안 된다 —
테마 그림 자체가 위쪽이 밝고 `_color` 에도 세로 그라데이션이 따로 있어서, 빛을 반대로
뒤집어도 절반은 통과한다. 끈 것과의 차이만 보아야 이 코드가 한 일이 걸린다.

몸 색을 **곱해서** 명암을 내는 것이 요점이다. 예전처럼 테마의 가장 밝은 색으로 섞으면,
그 색이 곧 몸 색인 2색 테마(분홍·네온)에서는 아무 일도 일어나지 않았다.

사용법: python test_light.py — 몇 초 안에 끝난다.
"""
import struct

import make_cur
import shape as shapelib
import smooth as sm

CELLS = sm.cells_for(96)
# 세기만 0 으로 만든다. DOME 이나 SHADOW 까지 끄면 그림 상자가 달라져 **다른 칸끼리** 비교하게 된다
FLAT = dict(SHADE=0.0, SPEC=0.0)


def arrow(sid: str) -> str:
    """구성표의 화살표 그림. "pink" 는 탭 아이콘 그림(`favicon.txt`)이다 — 분홍 구성표를 지울 때(2026-10-04)
    몸이 한 색인 2색 화살표가 접힘·재질의 기준으로 필요해 그 한 장만 남겼다. 하트비트로 바꿔 봤더니
    몸에 명암 계단이 있어 needle 접힘 최대가 21→35 로 뛰어, 기하가 아니라 그림을 재게 됐다.
    나머지는 test_art/ — '움직이는' 20종을 고화질 이펙트로 바꾸며(2026-10-11) 지운 픽셀 그림 중 여기서 재는 칸만 남겼다"""
    return open("favicon.txt" if sid == "pink" else f"test_art/{sid}/arrow.txt", encoding="utf-8").read()


def render(shape: str, sid: str, flat: bool) -> dict:
    # 전역 상수만 0 으로 해서는 안 꺼진다 — glass 처럼 제 값을 적어 둔 모양은 그것을 쓴다
    keep, spec = {k: getattr(sm, k) for k in FLAT}, sm.SHAPES[shape]
    own = {k.lower(): spec[k.lower()] for k in FLAT if k.lower() in spec}
    if flat:
        for k, v in FLAT.items():
            setattr(sm, k, v)
            spec[k.lower()] = v
    sm._cache.clear()
    try:
        frames = shapelib.read_art(arrow(sid))[0]
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
for sid in ("pink", "neonpulse", "electric", "jitter", "flicker"):   # 2색 둘·5색·4색·18색
    for shape in ("round", "chunky", "dart"):
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
        # 몸이 이미 검으면 곱셈으로는 더 내려갈 데가 없다 (네온은 바탕이 20 남짓). 거기서는
        # 아래가 밝아지지만 않으면 된다 — 부피감은 바로 아래 '폭' 이 맡는다
        if dd > (2 if base < 40 else -1):
            fails.append(f"{shape}/{sid}: 오른쪽 아래가 어두워지지 않음 ({dd:+.1f}, 바탕 {base:.0f})")
        # 검은 몸(네온·전기)은 더 어두워질 여지가 작다. 한쪽 값이 아니라 **폭**을 본다
        if du - dd < 10:
            fails.append(f"{shape}/{sid}: 명암 폭이 너무 좁음 ({du - dd:.1f})")
assert not fails, "돔 음영이 몸을 부풀리지 않음 — " + " · ".join(fails)
print("돔 음영 OK — 켠 쪽이 왼쪽 위는 밝고 오른쪽 아래는 어둡다")


# ── 무늬 섞기 ────────────────────────────────────────────────────────────────
# 그림이 17x11 칸뿐이라 칸 하나를 그대로 쓰면 어느 크기로 그려도 무늬 한 칸이 폭의 9% 를
# 차지해 네모로 보인다. 둘러싼 네 칸을 섞되 **대비가 큰 이웃은 빼고** 섞는 것이 요점이다 —
# 이발소 줄무늬는 저해상도가 아니라 그 구성표의 무늬라서 펴면 죽는다.
# 그래서 "색이 늘었나" 하나만 보면 안 되고, 계조 쪽과 무늬 쪽의 늘어난 정도를 견줘야 한다.

def colors(sid: str, pat: float) -> set:
    """이 구성표를 그렸을 때 몸에 나온 색들. PATTERN 만 바꿔 두 번 부른다"""
    keep = sm.PATTERN
    sm.PATTERN = pat
    sm._cache.clear()
    try:
        frames = shapelib.read_art(arrow(sid))[0]
        px = sm.draw("chunky", "arrow", sm.samplers_of(frames), CELLS)[0][0]
        return {c for c in px.values() if c[3] > 240}
    finally:
        sm.PATTERN = keep
        sm._cache.clear()


off = {sid: colors(sid, 0.0) for sid in ("wave", "barber", "pink")}
on = {sid: colors(sid, sm.PATTERN) for sid in off}
rate = {sid: len(on[sid]) / len(off[sid]) for sid in off}
for sid in off:
    print(f"{sid:10} 섞기 끔 {len(off[sid]):4} → 켬 {len(on[sid]):4} · {rate[sid]:.2f}배")

# 1. 계조가 있는 구성표는 중간색이 실제로 생겨야 한다 (PATTERN=0 으로 돌리면 1.00 배라 걸린다)
assert rate["wave"] > 2.0, f"물결의 명암 계단이 안 펴짐 ({rate['wave']:.2f}배)"
# 2. 대비가 큰 두 색짜리는 한 색도 늘면 안 된다 — KEEP 이 너무 크면 여기서 걸린다
assert on["pink"] == off["pink"], f"분홍의 두 색이 섞임 ({len(on['pink']) - len(off['pink'])}색 늘어남)"
# 3. 무늬가 있는 쪽은 계조 쪽보다 덜 건드려져야 한다. 체크무늬가 펴지면 이 비가 뒤집힌다
assert rate["barber"] < rate["wave"], \
    f"이발소 줄무늬가 물결만큼 펴짐 ({rate['barber']:.2f} vs {rate['wave']:.2f})"
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
        frames = shapelib.read_art(arrow(sid))[0]
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
for shape in ("round", "dart", "chunky"):
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
    frames = shapelib.read_art(arrow(sid))[0]
    return sm.draw("round", "arrow", sm.samplers_of(frames, mat), cells)[0][0]


def gap(a: dict, b: dict) -> tuple[float, float]:
    """(95분위 색차, 최대). 평균은 넓은 평면에 묻혀 쓸모가 없고, 하이라이트는 칸이 적어
    95분위도 못 볼 수 있다 — 그래서 최대까지 본다"""
    ps = [p for p in a if p in b and a[p][3] > 200 and b[p][3] > 200]
    assert len(ps) > 40, f"겹치는 몸 칸이 {len(ps)}개뿐이라 잴 수 없음"
    ds = sorted(sum(abs(a[p][i] - b[p][i]) for i in range(3)) / 3 for p in ps)
    return ds[int(len(ds) * 0.95)], ds[-1]


best: dict = {}   # 재질마다 **잘 드러나는 쪽** 구성표의 값. 어디서도 안 드러나면 걸린다
# 구성표 둘로 잰다. 분홍은 몸이 한 색이라 **명암** 차이가 그대로 보이고, 물결은 광택색이
# 몸색과 멀어 **광택** 차이가 보인다. 분홍만 재면 광택만 다른 재질(매트)이 묻힌다
for sid in ("pink", "wave"):
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
WHITE = (255, 255, 255, 255)
dot = sm.specks([[(0.5, 0.5, WHITE)]], (0, 0, 40, 40), sm.LIMIT * 9)
xs = [x for x, _ in dot]; ys = [y for _, y in dot]
x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
mid = dot[((x0 + x1) // 2, (y0 + y1) // 2)][3]
corner = max(dot.get(p, (0, 0, 0, 0))[3] for p in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)))
print(f"불꽃 {x1 - x0 + 1}칸 · 가운데 {mid} · 모서리 {corner}")
assert mid > 240 and corner < 40, f"불꽃이 둥글지 않음 (가운데 {mid} · 모서리 {corner})"
print("불꽃 OK — 네모가 아니라 둥근 점이다")


# ── 이어진 조각이 선으로 남는가 ────────────────────────────────────────────
# 전기의 가닥은 원본에서 붙어 있는 칸들이다. 몸이 20칸으로 펴지면서 그 칸들이 점 지름보다
# 멀어지므로, 사이를 안 채우면 가닥이 아니라 점선으로 찍힌다.
# 판·몸 크기는 실제 빌드가 쓰는 비율로 잡는다 (160px 판, 그 안을 거의 채운 몸). 판을 작게
# 잡으면 점끼리 저절로 겹쳐서 사이를 안 채워도 통과한다 — 처음에 그렇게 짰다가 헛검사가 됐다
# (맨 위 CELLS 와 이름을 가른다 — 같은 이름으로 덮으면 뒤에 render 를 부르는 검사가 조용히 딴 판을 잰다)
S_CELLS = sm.LIMIT * 9
BOX = (10, 10, 130, 130)
STEP = 1 / 12                     # 원본 화살표 폭이 12칸쯤이라 이웃 칸이 이만큼 떨어져 있다


def holes_in_row(px: dict) -> list:
    ys_ = [y for _, y in px]
    row = (min(ys_) + max(ys_)) // 2
    xs_ = sorted(x for x, y in px if y == row)
    return [b for a, b in zip(xs_, xs_[1:]) if b - a > 1]


line = sm.specks([[(0.0, 0.5, WHITE), (STEP, 0.5, WHITE)]], BOX, S_CELLS)
holes = holes_in_row(line)
print(f"가닥 {len(line)}칸 · 끊긴 자리 {len(holes)}")
assert not holes, f"이어진 조각이 점선으로 찍힘 (끊긴 자리 {holes})"
assert len(sm.specks([[(0.0, 0.5, WHITE)], [(STEP, 0.5, WHITE)]], BOX, S_CELLS)) < len(line), \
    "따로 떨어진 두 조각까지 이어 버림"

# 몸이 가로·세로로 다르게 펴질 때. 원본 화살표 11×17 칸이 65×79 로 펴지면 한 칸이 가로 6.5px ·
# 세로 4.6px 라, 가장 가까운 두 점(세로)을 기준으로 이웃을 가르면 가로 이웃이 빠져 점선이 됐다
# (2026-09-23 전기 가닥에서). 조각이 원본 한 칸의 크기를 들고 다니면 축마다 따로 가른다.
# 검사는 배율 차이를 크게 벌려 둔다(가로 12px · 세로 4px) — 실제 값(6.4 · 4.9)을 그대로 쓰면
# 옛 문턱(4.9×1.45)이 가로 간격보다 커서 옛 코드도 통과한다. 실제로 끊긴 건 반올림으로 세로가
# 4px 까지 줄었던 프레임이었다
ell = sm.Bunch([(0.0, 0.5, WHITE), (0.1, 0.5, WHITE), (0.2, 0.5, WHITE), (0.0, 0.6, WHITE)])
ell.step = (0.1, 0.1)
holes = holes_in_row(sm.specks([ell], (12, 12, 120, 40), 80))
assert not holes, f"가로로 더 펴진 몸에서 가닥이 점선이 됨 (끊긴 자리 {holes})"
print("가닥 OK — 한 조각은 이어지고, 몸이 가로·세로로 다르게 펴져도 안 끊기고, 다른 조각끼리는 안 붙는다")


# ── 몸에서 뻗은 가닥은 새 몸 테두리에 붙는가 ─────────────────────────────────
# 새 몸은 윤곽이 달라 비율 자리로 옮기면 뿌리가 몸에서 뜬다. 뻗은 가닥(touch)만 테두리로
# 당기고, 떨어져 날리던 점(눈송이)은 제자리에 둔다
edge = [(20, y) for y in range(10, 60)]                 # 새 몸의 오른쪽 테두리가 x=20 인 판
strand = sm.Bunch([(1.0, 0.5, WHITE), (1.05, 0.5, WHITE), (1.1, 0.5, WHITE)])
strand.touch = True
flake = [(1.0, 0.5, WHITE)]                             # 같은 자리의 떨어진 점
bx = (0, 10, 30, 50)                                    # 비율 1.0 이면 x≈29 — 테두리 밖으로 9칸 뜬다
got = sm.specks([strand], bx, S_CELLS, edge)
kept = sm.specks([flake], bx, S_CELLS, edge)
gap_s = min(x for x, _ in got) - 21
gap_f = min(x for x, _ in kept) - 21
print(f"가닥 뿌리와 테두리 사이 {gap_s}칸 · 떨어진 점은 {gap_f}칸 그대로")
assert gap_s <= 0, f"뻗은 가닥이 새 몸에서 떠 있음 ({gap_s}칸)"
assert gap_f > 5, f"떨어진 점까지 테두리로 끌려감 ({gap_f}칸)"
print("가닥 뿌리 OK — 뻗은 가닥만 새 테두리에 붙는다")


# ── 매달린 조각(용암 방울)이 새 몸의 매달린 자리에서 늘어지는가 ─────────────────
# 비율 자리로만 옮기면 새 몸의 꼬리 끝과 어긋나 방울이 커서 밖 허공에서 나타났다(2026-09-23).
# 매달린 몸 칸이 새 테두리에 오게 옮기고, 바로 붙어 있던 조각은 테두리까지 이어져야 한다.
# 새 몸의 아래 테두리는 y=40 · x 10..30 이고, 비율로 옮긴 매달린 자리(x≈7)는 그 왼쪽 위에 뜬다
edge = [(x, 40) for x in range(10, 31)]
ORANGE = (255, 138, 16, 255)


def hanging(dys: list[int], stuck: bool) -> dict:
    # 세로 한 칸(0.2 → 12px)을 점 지름(9px)보다 크게 잡는다 — 작으면 이어 그리지 않아도 점끼리 저절로
    # 겹쳐 붙어 보여서 헛검사가 된다 (처음에 0.1 로 짰다가 그랬다)
    g = sm.Bunch([(0.05, 0.5 + dy * 0.2, ORANGE) for dy in dys])
    g.step, g.hang = (0.1, 0.2), (0.05, 0.5, stuck)
    return sm.specks([g], (0, 0, 60, 60), S_CELLS, edge)


drip = hanging([1, 2], True)
mid = sum(x for x, _ in drip) / len(drip)
rows = sorted({y for _, y in drip})
holes = [y for y in range(41, rows[-1]) if y not in rows]
print(f"맺힌 방울 가운데 x {mid:.1f} (테두리 끝 10.5) · 테두리 밑으로 끊긴 줄 {len(holes)}")
assert abs(mid - 10.5) < 2, f"매달린 조각이 새 몸의 매달린 자리로 안 옮겨짐 (가운데 x {mid:.1f})"
assert not holes, f"몸에 붙어 있던 방울이 테두리에서 떨어져 보임 (끊긴 줄 {holes})"
fall = hanging([5], False)
top = min(y for _, y in fall)
assert top > 45, f"떨어지는 방울까지 테두리에 이어 붙임 (맨 윗줄 {top})"
print("매달린 조각 OK — 새 꼬리 끝에서 늘어지고, 떨어진 방울은 그 밑으로 떨어진다")

# 솟는 조각(모닥불 불길)은 그 반대 — 새 몸의 윗변(y=20)에 뿌리를 박고 위로 솟아야 한다
edge = [(x, 20) for x in range(10, 31)]


def rising(dys: list[int], stuck: bool) -> dict:
    g = sm.Bunch([(0.05, 0.5 - dy * 0.2, ORANGE) for dy in dys])
    g.step, g.hang = (0.1, 0.2), (0.05, 0.5, stuck, True)
    return sm.specks([g], (0, 0, 60, 60), S_CELLS, edge)


lick = rising([1, 2], True)
rows = sorted({y for _, y in lick})
holes = [y for y in range(rows[0], 20) if y not in rows]
mid = sum(x for x, _ in lick) / len(lick)
print(f"솟은 불길 가운데 x {mid:.1f} (테두리 끝 10.5) · 맨 아랫줄 {rows[-1]} · 윗변까지 끊긴 줄 {len(holes)}")
assert abs(mid - 10.5) < 2, f"솟는 조각이 새 몸의 뿌리 자리로 안 옮겨짐 (가운데 x {mid:.1f})"
assert rows[-1] >= 19 and not holes, f"몸에 붙어 있던 불길이 윗변에서 떠 있음 (끊긴 줄 {holes})"
ember = rising([5], False)
assert max(y for _, y in ember) < 15, f"떠오른 불티까지 윗변에 이어 붙임 (맨 아랫줄 {max(y for _, y in ember)})"
fake = {(x, y): (9, 9, 9, 255) for x in range(4) for y in range(4, 8)}
fake.update({(1, 3): ORANGE[:3] + (sm.RISE,), (1, 2): ORANGE[:3] + (sm.RISE,), (2, 3): ORANGE[:3] + (sm.RISE,)})
marks, body = sm.specks_of(fake)
assert len(body) == 16 and sorted(len(g) for g in marks) == [1, 2], f"솟는 조각을 줄마다 못 뗌: {marks}"
print("솟는 조각 OK — 줄마다 떼어 새 윗변에 뿌리를 박고, 떠오른 불티는 떠 있다")


# ── 프레임 사이를 섞은 것이 양끝 사이에 있는가 ──────────────────────────────
# 60fps 로 늘릴 때 쓰는 길이다. 섞은 프레임이 양끝 사이 값이 아니면 움직임이 튀고,
# 알파를 안 곱하고 섞으면 나타나고 사라지는 자리에 검은 테가 난다 (투명한 칸의 색이 섞여 들어와서).
a = {(0, 0): (200, 40, 40, 255), (1, 0): (0, 0, 0, 0)}
b = {(0, 0): (40, 40, 200, 255), (1, 0): (250, 250, 250, 255)}
mid = sm._between(a, b, 0.5)
print(f"섞은 칸 {mid[(0, 0)]} · 나타나는 칸 {mid[(1, 0)]}")
assert mid[(0, 0)] == (120, 40, 120, 255), f"양끝 사이가 아님: {mid[(0, 0)]}"
assert mid[(1, 0)][:3] == (250, 250, 250) and mid[(1, 0)][3] == 128, \
    f"투명에서 나타나는 칸에 검은 테가 섞임: {mid[(1, 0)]}"
four = sm.tween([a, b], [1, 1, 1, 1])
assert len(four) == 8, f"4배로 안 늘어남: {len(four)}장"
assert four[0] is a and four[4] is b, "원래 프레임이 제자리에 없음"
assert sm.tween([a], [1, 1]) == [a] and sm.tween([a, b], [4]) == [a, b], "안 늘려야 할 때 늘림"
print("프레임 섞기 OK — 양끝 사이 값이고 투명 쪽에 검은 테가 없다")

# ── 늘려도 한 바퀴 도는 시간이 그대로인가 ──────────────────────────────────
# 여기가 깨지면 부드러워진 게 아니라 그냥 빨리 재생된 것이다. rate 5 를 반으로 자르면
# 2+2=4 라 20% 빨라지므로, 고르게 못 나누는 rate 는 [3,2] 처럼 들쭉날쭉 쪼개야 한다.
for rate in range(1, 13):
    part = sm.steps(rate, 30)
    assert sum(part) == rate, f"rate {rate} 를 {part} 로 쪼개 합이 {sum(part)} 가 됐다"
    assert all(p >= 1 for p in part), f"rate {rate} → {part} 에 0 틱짜리 프레임이 있다"
    # rate 1 은 이미 60fps 라 못 쪼갠다
    assert len(part) == 1 or rate / len(part) >= 1.9, f"rate {rate} → {part} 는 30fps 를 넘겨 파일만 키운다"
print("틱 쪼개기 OK — " + " · ".join(f"{r}→{sm.steps(r, 30)}" for r in (4, 5, 6, 7, 8)))

# 쪼갠 시간이 실제로 .ani 에 적히는가 (안 적히면 윈도우가 anih 의 한 값으로 고르게 돌린다)
ani = make_cur.curs_to_ani([bytes(4)] * 4, [3, 2, 3, 2])
assert b"rate" in ani, "프레임마다 다른 시간을 줬는데 rate 칸이 안 들어갔다"
got = struct.unpack("<4I", ani[ani.index(b"rate") + 8:ani.index(b"rate") + 24])
assert got == (3, 2, 3, 2), f"rate 칸에 엉뚱한 값: {got}"
assert b"rate" not in make_cur.curs_to_ani([bytes(4)] * 4, 6), "고른 rate 인데 칸을 넣었다"
print("rate 칸 OK — 프레임마다 머무는 시간이 파일에 적힌다")


# ── 기호 칸이 화살표 무늬를 끌고 오지 않는가 ──────────────────────────────────
# 도움말·백그라운드 작업·위치·사용자는 매끈한 모양에서 **화살표 그림과의 차이**를 기호로 떼어
# 새 화살표에 얹는다 (build.smooth_parts). 그 칸의 화살표 부분이 화살표 그림과 한 칸이라도
# 다르면 그 칸이 기호에 섞여 매끈한 몸 위에 네모 픽셀로 박힌다 — 2026-09-22 에 용암 무늬와
# 전기 불꽃을 칸마다 따로 뽑아 그렇게 됐다. 절반 넘는 프레임에 나오는 기호 칸의 상자에서 3칸 넘게
# 떨어진 칸이 있으면 실패한다. 여유를 두는 것은 기호 **스스로** 움직이는 구성표 때문이다 —
# 불꽃놀이의 모래시계는 터지며 아래로 2~3칸 번지고, 지터의 기호는 옆으로 2칸 떨린다(1칸 여유로
# 짰다가 이 둘이 걸렸다). 샌 화살표 무늬는 몸 안쪽·왼쪽이라 기호 상자에서 훨씬 멀다.
# classic_only 구성표와 냥이 빼꼼(peek, 화살표만 다시 그림)·고화질(art 없음)은 이 칸들이 smooth_parts 를 안 타므로 뺀다 — 그 칸들은
# 작은 화살표 동물 옆에 장면을 통째로 그려서 기호 상자라는 것이 없다(먼치킨 백그라운드 작업).
# 그래서 지금 schemes.json 에는 이 길을 타는 구성표가 없다 — 옛 '움직이는' 그림(test_art/)의 전기·지터로 잰다
import build  # noqa: E402
from pathlib import Path  # noqa: E402

FIXTURE = Path(__file__).parent / "test_art"
_art_raw = build.art_raw
build.art_raw = lambda sid, rid: ((FIXTURE / sid / f"{rid}.txt").read_text(encoding="utf-8")   # smooth_parts 도 이걸 부른다
                                  if (FIXTURE / sid).is_dir() else _art_raw(sid, rid))

leaks = []
smooth_schemes = [s["id"] for s in build.SCHEMES if s["id"] not in build.CLASSIC_ONLY | build.PEEK | set(build.HD)] + ["electric", "jitter"]
for sid in smooth_schemes:
    arrow = shapelib.read_art(build.art_raw(sid, "arrow"))[0]
    for rid in ("help", "busy", "pin", "person"):
        frames = shapelib.read_art(build.art_raw(sid, rid))[0]
        glyphs = shapelib.glyph_of([arrow[i % len(arrow)] for i in range(len(frames))], frames)
        seen: dict = {}
        for g in glyphs:
            for p in g:
                seen[p] = seen.get(p, 0) + 1
        core = [p for p, n in seen.items() if n * 2 > len(frames)]
        if not core:
            continue
        x0, y0, x1, y1 = shapelib.bbox(core)
        out = [p for p in seen if not (x0 - 3 <= p[0] <= x1 + 3 and y0 - 3 <= p[1] <= y1 + 3)]
        if out:
            leaks.append(f"{sid}/{rid} {len(out)}칸")
print(f"기호 칸 {len(smooth_schemes) * 4}개 · 화살표 무늬가 샌 칸 {len(leaks)}개")
assert not leaks, "기호에 화살표 무늬가 섞임 — " + " · ".join(leaks)
print("기호 OK — 도움말·작업·위치·사용자 칸의 화살표 부분이 화살표 그림과 같다")


# ── 번짐 층이 대각선 계단에서 비지 않는가 ──────────────────────────────────
# 매끈한 대각선은 원본의 계단을 가로지르므로, 안쪽 번짐 층의 자리를 비율로 옮기면 계단 안쪽
# 모서리에 떨어진다. 층 칸까지 대각 두 칸이라도 '가까이 있음'으로 쳐야 한다 — 유클리드로 재던
# 때는 여기서 한 칸씩 비어 네온 맥박의 오른쪽 위 테두리에 톱니가 났다(2026-09-24)
frames, _, _ = build.smooth_parts("neonpulse", "arrow", "round", {})
halo = sm.samplers_of(frames, "glow")[len(frames) // 2][3]   # 네온 맥박은 schemes.json 에서 glow 재질이었다
(st, recipes), _, _, _ = sm.stencil("round", "arrow", sm.cells_for(128))
empty = sum(1 for n, iu, iv, _ in st.values() for k, *_ in recipes[n]
            if k in ("halo0", "halo1") and not halo[int(k[4])](iu / sm.UV, iv / sm.UV))
print(f"네온 맥박 round 128 · 번짐 층이 빈 칸 {empty}")
assert not empty, f"번짐이 둘린 구성표인데 번짐 층이 {empty}칸 비었다 (대각선 톱니)"
# 마개 자체는 남아야 한다 — 한쪽에만 있는 번짐이 몸 너머 반대쪽까지 칠해지면 안 된다
one = sm._ring_at({**{(0, y): WHITE for y in range(11)}, (10, 0): WHITE}, 0)   # 왼쪽 벽만 찬 층
assert one(0.2, 0.5), "층 바로 옆(대각 두 칸 안)인데 색을 못 떴다"
assert one(0.5, 0.5) is None, "층에서 다섯 칸 떨어진 자리까지 칠했다 — 마개가 풀렸다"
print("번짐 층 OK — 대각선 계단에서 안 비고, 한쪽 번짐이 반대쪽으로 새지 않는다")


# ── 솟은 불길이 새 윗변 위에 한 장으로 펴지는가 ───────────────────────────────
# 원본 줄마다 따로 찍으면 몸이 펴진 만큼 줄 사이가 벌어져 모닥불이 빗살이 됐다(2026-09-24).
# 불길 다섯 줄(키가 1·2 번갈아)을 새 몸 윗변(y=20) 위에 펴서, 기둥 사이가 안 비고 뿌리가 전부
# 윗변 바로 위(y=19)에 닿는지 본다
flames = []
for i, u in enumerate((0.3, 0.4, 0.5, 0.6, 0.7)):
    g = sm.Bunch([(u, 0.5 - k * 0.2, ORANGE) for k in (1, 2)][:1 + i % 2])
    g.step, g.hang = (0.1, 0.2), (u, 0.5, True, True)
    flames.append(g)
top_body = {(x, y) for x in range(61) for y in range(20, 61)}
sheet, rest = sm.rise_sheet(flames, (0, 0, 60, 60), 128, top_body)
cols = sorted({x for x, _ in sheet})
gaps = [x for x in range(cols[0], cols[-1]) if x not in cols] if cols else ["전부"]
roots = [x for x in cols if (x, 19) not in sheet]
print(f"불길 장 기둥 {len(cols)}개 · 빈 기둥 {len(gaps)} · 윗변에 안 닿은 기둥 {len(roots)} · 남은 조각 {len(rest)}")
assert cols and not gaps, f"불길이 빗살로 갈라짐 (빈 기둥 {gaps[:5]})"
assert not roots and not (sheet.keys() & top_body), f"불길 뿌리가 윗변에서 떴거나 몸을 덮음 ({roots[:5]})"
assert not rest, "몸에 붙은 불길을 장으로 못 펴고 조각으로 남김"
print("불길 장 OK — 기둥 사이가 안 비고 뿌리가 새 윗변에 닿는다")


# ── 별이 네 갈래 반짝이인가 ───────────────────────────────────────────────────
# 칸을 둥근 점으로 이어 찍던 때는 굵은 더하기(＋)였다. 네 갈래 반짝이면 가운데와 빛살 위는
# 칠하고 빛살 사이(대각선)는 비워야 한다 — 원이나 네모로 칠하면 대각선이 찬다
W = (255, 255, 255, 255)
twinkle = [(0.5, 0.5, W)] + [(0.5 + dx * 0.05, 0.5 + dy * 0.05, (255, 200, 60, 255))
                             for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2))]
spark = sm.star(twinkle, (0, 0, 100, 100), 128)
xs = [x for x, _ in spark]
cx = cy = (min(xs) + max(xs)) // 2
rx = max(xs) - cx
arm = spark.get((cx + rx // 2, cy), (0, 0, 0, 0))[3]
diag = spark.get((cx + round(rx * 0.45), cy + round(rx * 0.45)), (0, 0, 0, 0))[3]   # 원이면 여기가 찬다
print(f"별 반지름 {rx}px · 가운데 {spark.get((cx, cy))} · 빛살 중간 알파 {arm} · 대각선 알파 {diag}")
assert spark.get((cx, cy), (0,) * 4)[:3] == (255, 255, 255), "별 가운데가 가장 밝은 색이 아님"
assert arm > 200 and diag < 60, f"네 갈래가 아님 — 빛살 {arm} · 대각선 {diag}"
print("별 OK — 가운데가 희고 빛살은 차고 빛살 사이는 빈다")


# ── 글리치의 줄 밀림을 잡아 새 몸을 같이 흔드는가 ────────────────────────────────
# 매끈한 모양은 고정된 스텐실에 색만 떠 칠해, 그대로면 글리치의 몸은 가만있고 밀린 칸이 테두리
# 번짐으로만 남았다(2026-09-24). 줄마다 몇 칸 밀렸는지 재서(jolts_of) 새 몸 픽셀 줄을 민다(_jolt).
# 밀림이 아니라 모양이 바뀌는 그림(불꽃·물결)에서 켜지면 그 그림이 찢기므로 57종에 돌려 본다
block = {(x, y): (17, 17, 17, 255) for x in range(4, 12) for y in range(4, 12)}
shook = []
for i in range(8):
    dx = (0, 2, 0, -1, 0, 3, 0, 1)[i]
    shook.append({(x + (dx if y in (6, 7) else 0), y): c for (x, y), c in block.items()})
got = sm.jolts_of(shook)
assert got and got[1] == {6: 2, 7: 2} and got[0] == {}, f"줄 밀림을 못 잼: {got and got[:2]}"
grow = [{(x, y): c for (x, y), c in block.items() if x < 12 - (i % 3) or y > 8} for i in range(8)]
assert sm.jolts_of(grow) is None, "모양이 바뀌는 그림을 줄 밀림으로 봄"
px = {(x, y): (0, 0, 0, 255) for x in range(10) for y in range(10)}
moved = sm._jolt(px, (0, 0, 10, 10), set(px), ((0, 0, 9, 9), {9: 1}, {}))
assert (10, 9) in moved and (0, 9) not in moved and (0, 8) in moved, "새 몸의 맨 아랫줄만 한 칸 밀려야 함"
lit = []
import build  # noqa: E402,F811
# 고화질은 art 그림이 없다. 글리치는 test_art/ 의 옛 지터 그림
for sid in [s["id"] for s in build.SCHEMES if not s.get("hd")] + ["jitter"]:
    for rid in ("arrow", "wait", "hand"):
        if sm.jolts_of(shapelib.read_art(build.art_raw(sid, rid))[0]):
            lit.append(f"{sid}/{rid}")
print(f"줄 밀림이 켜진 칸 {len(lit)}개: {' · '.join(lit)}")
assert lit and all(s.startswith("jitter/") for s in lit), f"글리치 말고도 켜짐: {lit}"
# TV 눈(무채색 반투명)은 색 뜨는 재료에서 빠지고 따로 들려야 한다 — 안 빼면 회색 고리로 뭉개진다
noisy = [{**f, (2, 5 + i % 3): (90, 90, 90, 144)} for i, f in enumerate(shook)]
clean, snow = sm._snow_of(noisy)
assert all(len(s) == 1 for s in snow) and all(q not in f for f, s in zip(clean, snow) for q in s), \
    "TV 눈을 몸 재료에서 못 뗌"
print("줄 밀림 OK — 글리치에서만 켜지고, 새 몸 줄을 밀고, TV 눈은 따로 든다")


# ── 흔들림 번짐은 sway 를 단 구성표에서만 켜지는가 ──────────────────────────────
# 비율만으로 켜던 때 반짝이 move(0.92)·폭죽 move(0.94)도 걸려서 기존 커서 바이트가 바뀌었다(2026-09-24).
# 표식을 단 것은 해양 애니 6종뿐이고, 표식이 실제로 번짐을 바꾸는지(문이 헛돌지 않는지)도 본다
sways = sorted(build.SWAYS)
print(f"sway 표식 {len(sways)}종: {' · '.join(sways)}")
assert sways == sorted(s["id"] for s in build.SCHEMES if s["id"].endswith("anim") and s.get("keep")), sways
frames, _, _ = build.smooth_parts("twinkle", "move", "round", {})
off, on = sm.samplers_of(frames), sm.samplers_of(frames, sway=True)
def at(h, k, u, v):
    return h[k](u, v) if h and h[k] else None
diff = sum(1 for a, b in zip(off, on) for k in (0, 1) for u in range(8) for v in range(8)
           if at(a[3], k, u / 8, v / 8) != at(b[3], k, u / 8, v / 8))
print(f"반짝이 move · sway 를 켜면 번짐이 달라지는 자리 {diff}곳")
assert diff, "sway 를 켜도 번짐이 그대로 — 문이 헛돈다"
print("흔들림 번짐 OK — 해양 애니에서만 켜지고, 켜면 번짐이 달라진다")


# ── schemes.json 의 animated 가 그림과 맞는가 ─────────────────────────────────
# handler.ps1 과 CI 가 이 값으로 .ani/.cur 를 고른다. 해양 애니 6종에 빠져서 윈도우 적용이 .cur 를 찾다
# 실패할 뻔했다(2026-09-24, CI 에서 걸림). 그림이 한 칸이라도 움직이면 animated 가 참이어야 한다
import make_cur  # noqa: E402
# 고화질은 art 가 없고 사용 중·대기 칸이 늘 움직여서 다 animated 다 — 아래 고화질 절에서 본다
wrong = [s["id"] for s in build.SCHEMES if not s.get("hd")
         if bool(s.get("animated")) != any(make_cur.is_animated(build.art_raw(s["id"], rid))
                                            for rid, *_ in build.ROLES + build.EXTRA)]
print(f"animated 표시가 그림과 어긋난 구성표 {len(wrong)}개 {wrong}")
assert not wrong, f"schemes.json 의 animated 가 그림과 다름: {wrong}"
print("animated OK — 움직이는 그림이 있는 구성표만 animated")


# ── 커서 색조 표식이 살아 있는가 ─────────────────────────────────────────────
# 냥이·댕댕이·짹짹이·공룡·햄찌·간식은 시안 페이지의 색조 막대가 둘이다(동물 · 커서, build.hue_kind "both"). 화살표 색의 파랑 끝 비트를
# 홀수로 박아 두면(gen/sea.mark) 페이지와 handler.ps1 이 그것으로 가른다. gen 을 mark 없이 다시 돌리거나, 그리는 길이
# 색을 섞어 비트를 흐트리면 커서 막대가 동물을 칠하거나 아무것도 안 칠한다. 그래서 화살표 칸의 장마다 홀수(커서)와
# 짝수(동물) 불투명 칸이 다 있어야 하고, 픽셀 그림은 다 peek 라 매끈한 화살표(smooth.peek_drawer, 섞어 그린 뒤 비트를 다시 박음)도
# 같다. 매끈한 쪽은 화살 끝(핫스팟) 둘레 6칸 안 불투명 칸이 거의 다 홀수여야 한다 — 비트를 안 박으면 뜬 색 반쯤이
# 짝수로 샌다. 화살표와 동물 크기는 견주지 않는다 — 새는 화살표보다 몸이 커서 홀수가 짝수보다 적다
both = sorted(s["id"] for s in build.SCHEMES if build.hue_kind(s) == "both")
def odd_even(f: dict) -> tuple[int, int]:
    solid = [c for c in f.values() if c[3] == 255]
    return sum(c[2] & 1 for c in solid), sum(1 - (c[2] & 1) for c in solid)
bad = []
for sid in (s for s in both if s not in build.HD):   # 고화질 펫은 art 가 없다 — 아래에서 그려서 잰다
    for i, f in enumerate(shapelib.read_art(build.art_raw(sid, "arrow"))[0]):
        o, e = odd_even(f)
        if not (o and e):
            bad.append(f"{sid} 기본 {i}장 홀{o}·짝{e}")
    if sid in build.PEEK:
        fs, (hx, hy) = build.peek_drawer(sid, "round")(sm.cells_for(32))
        for i, f in enumerate(fs):
            o, e = odd_even(f)
            tip = [c[2] & 1 for (x, y), c in f.items() if c[3] == 255 and (x - hx) ** 2 + (y - hy) ** 2 <= 36]
            if not (o and e and tip and sum(tip) >= 0.9 * len(tip)):
                bad.append(f"{sid} round {i}장 홀{o}·짝{e}·끝 홀{sum(tip)}/{len(tip)}")
# 고화질 펫(흰냥이 · 냥이)은 art 가 없어 그림을 그려 32 · 64 판으로 줄인 바이트에서 잰다 — 화살표 칸을 마스크로 따로 그려 줄인 뒤
# 비트를 박는다(hdpet.rgba_bytes). 기본 화살표와 매끈한 모양 하나를 첫 장만. 끝 둘레는 매끈한 쪽과 같은 6칸(32 판 기준)이다 —
# 3칸이던 때는 기본 화살표 32 판에서 한 칸만 들어 아무것도 못 쟀다. 8칸까지 넓혀도 네 모양 다 100% 였다(2026-10-11)
import hd as hdlib  # noqa: E402
import hdpic  # noqa: E402
pets = sorted(sid for sid in both if sid in build.HD)
for sid in pets:
    for st in (build.HD[sid], f"{build.HD[sid]}@{build.SHAPES[1]['id']}"):
        img, (hx0, hy0) = hdlib.render(st, "arrow", 0)
        got = hdlib.sizes(img, [32, 64])
        for n in (32, 64):
            raw = hdlib.rgba_bytes(got[n], n)
            f = {(i % n, i // n): raw[i * 4:i * 4 + 4] for i in range(n * n)}
            hx, hy, r = hx0 * n // hdlib.N, hy0 * n // hdlib.N, 6 * n // 32
            o, e = odd_even(f)
            # 그림 결은 끝이 개 몸 한가운데라 원 안이 대부분 개다 — 화살표가 뻗는 쐐기(대각선과 세로 사이, 테 한 칸 띄움)만 잰다
            wedge = (lambda x, y: x - hx >= 1 and (y - hy) - (x - hx) >= 1) if sid in hdpic.PICS else (lambda x, y: True)
            tip = [c[2] & 1 for (x, y), c in f.items()
                   if c[3] == 255 and (x - hx) ** 2 + (y - hy) ** 2 <= r * r and wedge(x, y)]
            print(f"  {st} {n}: 홀{o}·짝{e}·끝 홀{sum(tip)}/{len(tip)}")
            if not (o and e and len(tip) >= 8 and sum(tip) >= 0.9 * len(tip)):
                bad.append(f"{st} {n} 홀{o}·짝{e}·끝 홀{sum(tip)}/{len(tip)}")
print(f"막대 둘 구성표 {len(both)}종 · 커서 표식이 어긋난 장 {len(bad)}개")
assert len(both) == 61, both
# 막대 둘 묶음은 다 매끈한 모양에 반응한다 — 픽셀 그림은 peek, 고화질은 화살표를 든 펫 결
assert set(both) == build.PEEK | set(pets), sorted(set(both) ^ (build.PEEK | set(pets)))
assert not bad, "커서 표식(파랑 끝 비트)이 어긋남 — " + " · ".join(bad[:8])
print("커서 표식 OK — 화살표 칸마다 커서(홀수)와 동물(짝수)이 갈려 있다")
# 그림 결에서 앞발이 화살표를 잡는 칸("grip")은 모양 탭마다 화살표를 앞발에 맞춰 다시 놓는다(hdpic._fit) — 기본 자리에 그대로
# 두면 모양 화살표가 앞발에서 13–30px 떨어져 발이 허공을 쥔다(2026-10-18 사용자). 앞발 층 무게중심에서 테두리까지 거리가 기본
# 화살표 때와 6px 안이어야 한다. 맞춘 값은 cutout 0.2 · dart 5.3 · chunky 4.6px 차였다
for sid, pic in hdpic.PICS.items():
    for rid, c in pic.cells.items():
        if not c.get("grip"):
            continue
        pts = []
        for paw in pic.paws(c["pose"]):
            A = pic.img(paw)[3]
            pts.append((sum(a * (i % hdpic.N) for i, a in enumerate(A)) / sum(A), sum(a * (i // hdpic.N) for i, a in enumerate(A)) / sum(A)))
        d0 = [hdpic._edge(None, c["at"], c.get("scale", 1.0))(x, y) for x, y in pts]
        for shp in ("cutout", "dart", "chunky"):
            f = hdpic._fit(sid, rid, shp)
            d = [hdpic._edge(shp, f["at"], f["scale"])(x, y) for x, y in pts]
            assert pts and all(abs(p - q) <= 6 for p, q in zip(d, d0)), f"{sid}/{rid}@{shp} 앞발이 화살표에서 뜸 {d} (기본 {d0})"
print("그림 결 OK — 앞발이 잡는 칸은 모양 탭에서도 화살표 테두리에 붙어 있다")


# ── 고화질 구성표 — 움직이는 칸만 여러 장(hd.frames)으로 굽고, .ani 를 거꾸로 읽어 시안에 쓴다 ───────────────
# build_hd 는 hd.animated 가 참인 칸만 장을 늘린다. 그 표가 그림과 어긋나면 움직이는 그림이 한 장으로 멈추거나
# 안 움직이는 그림을 40장 굽는다. 한 구성표는 확장자가 하나라(handler.ps1·CI) 고화질은 다 animated 여야 한다
# 모양 탭이 있는 것은 화살표를 든 펫 결뿐이다(build_hd_shape) — 나머지는 모양으로 다시 그릴 몸이 없어 기본 모양만
import hdpet  # noqa: E402
assert build.HD and all(s.get("animated") and bool(s.get("classic_only")) != getattr(hdlib.STYLES.get(s["hd"]), "cursor", False)
                        for s in build.SCHEMES if s.get("hd")), "고화질 표시"
assert set(build.HD.values()) == set(hdlib.STYLES), sorted(set(build.HD.values()) ^ set(hdlib.STYLES))
# 이펙트 · 애니 결도 화살표만 모양 탭이 있다(hdshape) — 표식(classic_only)은 그대로라 build.CLASSIC_ONLY 가 뺀다.
# 모양 화살표 핫스팟은 판 안이고 그 칸에 몸(띠 포함)이 있어야 한다 — 몸 밖이면 클릭 자리가 허공이다
import hdshape  # noqa: E402
fxs = [sid for sid, st in build.HD.items() if hdshape.fx(st)]
assert len(fxs) == 20 and not set(fxs) & build.CLASSIC_ONLY and set(fxs) <= set(build.drawn("dart")), "이펙트 결 모양 탭"
for shp in ("cutout", "dart", "chunky"):
    g = hdshape.geom(shp)
    hx, hy = g["hot"]
    out = hdlib.grow(g["body"], g["band"]) if g["band"] else g["body"]
    assert 0 < hx < 32 and 0 < hy < 32 and out(hx, hy + 0.3) < 0.5, f"{shp} 모양 화살표 핫스팟 {g['hot']}"
    assert hdlib.render(f"lavaflow@{shp}", "arrow", 0)[0] != hdlib.render("lavaflow", "arrow", 0)[0], f"{shp} 모양이 안 바뀜"
# 견주는 장은 0.3 — 파문은 한 바퀴에 물방울이 두 번 떨어져 0 과 0.5 가 같은 그림이다
lie = [f"{st}/{rid}" for st in hdlib.STYLES for rid in ("arrow", "busy")
       if (hdlib.render(st, rid, 0)[0] != hdlib.render(st, rid, 0.3)[0]) != hdlib.animated(st, rid)]
print(f"고화질 {len(hdlib.STYLES)}결 · 움직임 표가 그림과 어긋난 칸 {len(lie)}개 {lie}")
assert not lie, f"hd.animated 가 그림과 다름: {lie}"
# 바쁨 고리 꼬리는 머리에서 멀어질수록 흐려져 끝(둥근 끝·빛 번짐 자리)에서 0 이어야 한다. 각을 한 바퀴로 접던 판은
# 꼬리 바로 뒤가 머리 값을 받아 끝에서 다시 짙어졌다(2026-10-11 사용자). 꼬리 뒤 반 틈부터 머리까지 한 줄로 잰다
for a0 in (-hdlib.math.pi / 2, 1.0, 3.0):
    fade = hdlib.spinner(0, 0, 7.6, 1.55, a0)[1]["fade"]
    span = hdlib.TAU * 0.62
    back = 0.95 * (hdlib.TAU - span) / 2       # 틈 한가운데는 앞뒤가 갈리는 자리라 조금 안쪽부터
    ang = [a0 - back + k * (span + back) / 200 for k in range(201)]
    run = [fade(7.6 * hdlib.cos(a), 7.6 * hdlib.sin(a)) for a in ang]
    assert all(p <= q + 1e-9 for p, q in zip(run, run[1:])), f"바쁨 고리 꼬리가 다시 짙어짐 (a0={a0:.2f})"
    assert run[0] == 0 and run[-1] > 0.99, f"바쁨 고리 꼬리 끝 {run[0]:.2f} · 머리 {run[-1]:.2f}"
# ani_frames 는 curs_to_ani 의 거꾸로여야 한다 — 크기마다 PNG 바이트와 핫스팟이 그대로 돌아오는지
pngs = [(hdlib.png(bytes([k, 0, 0, 255]) * s * s, s, s), (k, s - 1 - k)) for k in (1, 2) for s in (32, 48)]
blob = make_cur.curs_to_ani([make_cur.pngs_to_cur(pngs[:2]), make_cur.pngs_to_cur(pngs[2:])], hdlib.RATE)
back = build.ani_frames(blob)
assert back == [{32: pngs[0], 48: pngs[1]}, {32: pngs[2], 48: pngs[3]}], "ani_frames 가 구운 것을 못 되읽음"
print("고화질 OK — 움직임 표가 그림과 맞고, .ani 를 장·크기·핫스팟 그대로 되읽는다")

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
        du, dd = mean(lit, up) - mean(flat, up), mean(lit, down) - mean(flat, down)
        print(f"{shape:6} {sid:8} 왼쪽 위 {du:+6.1f} · 오른쪽 아래 {dd:+6.1f} · 폭 {du - dd:5.1f}")
        if du < 3:
            fails.append(f"{shape}/{sid}: 왼쪽 위가 밝아지지 않음 ({du:+.1f})")
        if dd > -1:
            fails.append(f"{shape}/{sid}: 오른쪽 아래가 어두워지지 않음 ({dd:+.1f})")
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

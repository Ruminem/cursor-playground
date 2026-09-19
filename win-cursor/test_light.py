# SPDX-License-Identifier: Apache-2.0
"""매끈한 모양의 돔 음영이 실제로 몸을 부풀리는지 본다.

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

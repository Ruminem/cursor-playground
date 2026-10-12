# SPDX-License-Identifier: Apache-2.0
"""고화질 펫 결의 작은 화살표 칸을 모양 탭에 맞춘다(2026-10-13).

도움말 · 백그라운드 작업 · 사용자 · 위치 칸(help · busy · person · pin)은 펫 옆에 작은 화살표(catkit.small_arrow)를
그리는데, 모양 탭에서도 기본 화살표 그대로라 "커서 모양이 적용이 안 됐네"였다. "<펫>@<모양>" 으로 그 칸을 그릴 때만
small_arrow 를 그 모양 윤곽(smooth.SHAPES)의 작은 판으로 바꿔 끼운다. 어느 칸이 작은 화살표를 쓰는지는 장면을 한 번
불러 보고 정한다(`cells`) — 칸 이름을 박아 두면 새 펫이 다른 칸에 쓸 때 조용히 빠진다.

catkit · dinokit · birdkit 을 고치지 않는 것은 그게 펫 30종 일감 해시라서다 — 고치면 510칸을 다시 굽는다. 그래서
hd.render 를 한 겹 더 감싸고, 바꿔 끼우는 동안만 펫 모듈들의 small_arrow 이름을 갈았다가 되돌린다.
"""
import sys

import hd
import hdpet
import hdshape  # noqa: F401 — 감싸는 차례를 정한다(hdpet → hdshape → 여기)
from hdpet import catkit as ck

H = 11.4                 # 바깥 테 높이 — 기본 작은 화살표(ARROW 21.8 × 0.52 + 테 0.3)와 같게
TOP = 1.32               # 바깥 테 왼쪽 · 위 끝 — 기본 작은 화살표 끝(1.62 − 0.3)과 같게. 핫스팟 칸 (1, 1) 그대로
BAND = 0.8               # 스티커 흰 띠 — 큰 화살표의 1.2 는 이 크기에서 몸을 다 먹는다

ORIG = ck.small_arrow    # catkit 제 이름도 갈리므로 되돌릴 원본을 따로 쥔다
_MINI: dict[str, frozenset] = {}
_GEO: dict[str, tuple] = {}


def _geo(shape):
    """모양 윤곽을 작은 화살표 크기로 → (몸, 바깥 테, 띠 굵기)"""
    if shape not in _GEO:
        import smooth as sm
        spec = sm.SHAPES[shape]
        band = BAND if spec["style"] == "sticker" else 0.0
        ys = [p[1] for p in spec["pts"]]
        k = (H - 2 * band) / (max(ys) - min(ys))
        ring = sm.fillet([(x * k, y * k) for x, y in spec["pts"]], [r * spec["rscale"] * k for r in spec["radii"]], 8)
        dx = TOP + band - min(p[0] for p in ring)
        dy = TOP + band - min(p[1] for p in ring)
        body = ck.poly([(x + dx, y + dy) for x, y in ring])
        _GEO[shape] = (body, ck.grow(body, band) if band else body, band)
    return _GEO[shape]


def arrow(shape):
    """그 모양의 작은 화살표 층 — 큰 모양 화살표(catkit.peek_shape)와 같은 칠: 스티커는 먹선 · 흰 띠 · 크림 몸"""
    body, outer, band = _geo(shape)
    if band:
        return ck.cur([ck.base(outer), ck.part(outer, ck.HI_WHITE, sh=0.0), ck.part(body, ck.cream_of, line=0.0, sh=0.0)])
    return ck.cur([ck.base(body), ck.part(body, ck.cream_of, sh=0.0)])


def _mods():
    return [m for n, m in list(sys.modules.items())
            if (n == "hdpet" or n.startswith("hdpet.")) and getattr(m, "small_arrow", None) is ORIG]


class _Swap:
    """그 동안만 펫 모듈들의 small_arrow 를 fn 으로"""

    def __init__(self, fn):
        self.fn, self.mods = fn, _mods()

    def __enter__(self):
        for m in self.mods:
            m.small_arrow = self.fn

    def __exit__(self, *_):
        for m in self.mods:
            m.small_arrow = ORIG


def cells(sid):
    """그 펫에서 작은 화살표를 그리는 칸들 — 장면을 두 장(0 · 0.5) 불러 small_arrow 가 불리는지 본다"""
    if sid not in _MINI:
        pet, hit = hdpet.PETS[sid], set()
        for name in hd.CELLS:
            if name == "arrow":
                continue
            seen = []
            with _Swap(lambda *a, **k: seen.append(1) or []):
                for fr in (0.0, 0.5):
                    pet.cell(name, fr)
            if seen:
                hit.add(name)
        _MINI[sid] = frozenset(hit)
    return _MINI[sid]


def shaped_cells(style):
    """"<펫>@<모양>" 이 모양 폴더에 굽는 칸 — 화살표 + 작은 화살표 칸. 펫이 아니면(이펙트 결) 화살표만"""
    sid, _, shape = style.partition("@")
    return ["arrow"] + (sorted(cells(sid)) if shape and sid in hdpet.PETS else [])


_render = hd.render


def render(style, name, frame=0.0):
    sid, _, shape = style.partition("@")
    if shape and sid in hdpet.PETS and name in cells(sid):
        with _Swap(lambda *a, **k: arrow(shape)):
            return _render(style, name, frame)
    return _render(style, name, frame)


hd.render = render

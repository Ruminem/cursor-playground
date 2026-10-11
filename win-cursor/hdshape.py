# SPDX-License-Identifier: Apache-2.0
"""이펙트 · 애니 결(hdfx)의 매끈한 모양 화살표 — "<결>@<모양>" 이 오면 화살표 칸만 그 모양 몸으로 그린다.

나머지 16칸은 모양 폴더에 안 굽고 받는 쪽이 기본 것으로 넘어간다(흰냥이 모양 탭과 같은 약속, build.build_hd_shape).
hd.py · hdfx/ 는 고화질 29종의 일감 해시라 건드리지 않고 여기서 감싼다 — hd.render · hd.frames · hdpet.hot 을
모듈 머리에서 바꿔 끼우고, "@모양" 이 없으면 원래 함수를 그대로 지나가 바이트가 같다.

  몸        smooth.SHAPES 윤곽을 hd 화살표 크기로 줄여 둥글린 다각형. 스티커(cutout)는 윤곽이 기본 화살표라
            hd 화살표 그대로에 흰 띠만 두른다(그림자는 띠가 깐다)
  핫스팟    바깥 테 맨 윗줄의 왼쪽 끝(smooth._hotspot 과 같은 약속)
  결 상태   이펙트 결이 칸 이름으로 붙들어 두는 것(글리치 핫스팟 줄 · 바람개비 중심 · 전구 자리 · 기포 · 파문 중심 ·
            용암 방울 자리)을 모양마다 따로 둔다 — 안 그러면 기본 화살표에서 잰 값을 모양 화살표가 빌려 쓴다
"""
from math import floor

import hd
import hdfx  # noqa: F401 — 결이 등록돼 있어야 fx() 가 가른다
import hdpet

_render, _frames, _hot = hd.render, hd.frames, hdpet.hot

# 결이 칸 이름으로 붙드는 것. 사전은 빈 것으로, 나머지는 없앤 채로 시작해 결이 다시 잰다
STATE = ("hots", "centers", "cache", "_centers", "_for", "_span", "_c", "_rmax", "_nowarp", "TAIL")
_STATES: dict = {}
_GEOM: dict = {}
BAND = (1.0, 1.0, 1.0)                 # 스티커 띠 색


def _split(style):
    base, _, shape = style.partition("@")
    return base, shape or None


def fx(style):
    """이펙트 · 애니 결인가 — 모양 탭이 화살표를 이 모듈로 그린다"""
    st = hd.STYLES.get(style)
    return st is not None and type(st).__module__.startswith("hdfx.")


def geom(shape):
    """모양 → 몸 거리함수 · 띠 굵기 · 핫스팟 · 용암 방울 자리. 크기는 smooth 의 기본 화살표 높이를 hd 화살표 높이에
    맞춘 비율 하나로 모든 모양을 줄인다 — 모양끼리 크기 차이(굵은 것이 큰 것)는 smooth 가 정한 대로 남는다"""
    if shape not in _GEOM:
        import smooth as sm
        spec = sm.SHAPES[shape]
        # 둥글린 뒤의 높이끼리 맞춘다 — 뾰족한 끝이 많이 깎여 꼭짓점 높이로 재면 화살촉·굵은 것이 작아진다
        ref = sm.SHAPES["cutout"]
        sy = [p[1] for p in sm.fillet(sm.ARROW, [r * ref["rscale"] for r in ref["radii"]], 8)]
        hy = [p[1] for p in hd.ARROW]
        k = (max(hy) - min(hy) + 1.0) / (max(sy) - min(sy))  # hd 화살표는 0.5 부풀린 것이라 1.0 을 더한다
        band = spec.get("band", 0.0) * k if spec["style"] == "sticker" else 0.0
        if spec["pts"] is sm.ARROW:                         # 윤곽이 기본 화살표 — hd 화살표를 띠만큼 밀어 그대로 쓴다
            body = hd.grow(hd.poly([(x + band, y + band) for x, y in hd.ARROW]), 0.5)
            tail = (10.7 + band, 22.0 + band)               # hdfx/fire.py 의 TAIL 을 같이 민 자리
        else:
            ring = sm.fillet([(x * k, y * k) for x, y in spec["pts"]],
                             [r * spec["rscale"] * k for r in spec["radii"]], 8)
            dx, dy = 1.1 + band - min(p[0] for p in ring), 1.1 + band - min(p[1] for p in ring)
            ring = [(x + dx, y + dy) for x, y in ring]
            body = hd.poly(ring)
            x, y = max(ring, key=lambda p: p[1])            # 맨 아래 끝(꼬리 · 화살촉 끝)에 방울이 맺힌다
            tail = (x, y - 0.6)
        outer = hd.grow(body, band) if band else body
        step = 0.05
        ty = next(j * step for j in range(1, 640) if any(outer(i * step, j * step) < 0 for i in range(1, 400)))
        tx = next(i * step for i in range(1, 400) if outer(i * step, ty + 0.3) < 0)
        _GEOM[shape] = dict(body=body, band=band, hot=(floor(tx) + 0.5, floor(ty) + 0.5), tail=tail)
    return _GEOM[shape]


def _enter(st, key, g):
    have = {k for k in STATE if hasattr(st, k)}             # 떼기 전에 잰다 — 인스턴스 사전(hots 등)은 떼면 hasattr 가 거짓
    old = {k: st.__dict__.pop(k) for k in STATE if k in st.__dict__}
    mine = _STATES.get(key)
    if mine is None:
        mine = {k: {} for k in ("hots", "centers", "cache", "_centers") if k in have}
        if "hots" in mine:
            mine["hots"]["arrow"] = g["hot"][1]             # 글리치는 핫스팟 줄(y)만 붙든다(hdfx/digital.py warp)
        if "TAIL" in have:
            mine["TAIL"] = g["tail"]
    st.__dict__.update(mine)
    return old


def _leave(st, key, old):
    _STATES[key] = {k: st.__dict__.pop(k) for k in STATE if k in st.__dict__}
    st.__dict__.update(old)


def render(style, name, frame=0.0):
    base, shape = _split(style)
    if not (shape and fx(base)):
        return _render(style, name, frame)
    g, st, cell = geom(shape), hd.STYLES[base], hd.cell

    def shaped(n, fr=0.0, soft=0.0, tip_body=False):
        if n != "arrow":
            return cell(n, fr, soft, tip_body)
        return [dict(f=hd.grow(g["body"], soft) if soft else g["body"])], g["hot"]

    had = "extra" in st.__dict__
    if g["band"]:
        own = getattr(st, "extra", None)

        def extra(n, fr, layers, hot):                      # 띠는 warp 를 탄 몸에서 떠 글리치에 같이 밀린다
            outer = hd.grow(layers[0]["f"], g["band"])
            out = own(n, fr, layers, hot) if own else layers
            return [dict(f=outer, paint=lambda x, y, e, nx, ny, f: (BAND, 1.0), noglow=True)] + out
        old_extra = st.__dict__.get("extra")
        st.extra = extra
    old = _enter(st, (base, shape), g)
    hd.cell = shaped
    try:
        return _render(base, name, frame)
    finally:
        hd.cell = cell
        _leave(st, (base, shape), old)
        if g["band"]:
            if had:
                st.extra = old_extra
            else:
                del st.extra


def frames(style, name):
    base, shape = _split(style)
    return _frames(base, name) if shape and fx(base) else _frames(style, name)


def hot(style, name):
    base, shape = _split(style)
    if shape and fx(base):
        return geom(shape)["hot"] if name == "arrow" else hd.cell(name)[1]
    return _hot(style, name)


hd.render, hd.frames, hdpet.hot = render, frames, hot

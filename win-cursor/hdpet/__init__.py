# SPDX-License-Identifier: Apache-2.0
"""고화질 펫 결 — 칸마다 그 동물이 하는 짓을 그린 장면(art 구성표의 HD 판). 읽으면 hd.STYLES 에 등록된다.

hd.py 틀(render 의 그림자 · 층 · 빛)은 그대로 쓰고 칸 그림(hd.cell)만 결마다 바꾼다. hd.py 를 고치면 고화질 27종이
다 다시 구워지므로 hd.render · hd.frames 를 여기서 감싼다 — 펫 결이 아니면 원래 함수를 그대로 불러 바이트가 같다.
펫 결이 다른 것:
  cell      칸 장면 함수 (name, frame, soft, tip_body) → (레이어, 핫스팟). 핫스팟은 art 칸 + 0.5
  M         번짐을 칠하는 거리(hd.M). 먹선 · 그늘 한 겹이라 3.5 까지 잴 일이 없다
  NF, RATE  한 바퀴 장 수 · 장마다 1/60초 틱. 장면이 NF 장으로 나뉘어 있어 LOOP 로 장 수를 정하지 않는다
  cursor    참이면 cur 를 단 층이 커서다 — 시안 색조 막대가 둘이고, 구운 그림에 gen/sea.mark 와 같은 표식이 박힌다
결 이름 "<펫>@<모양>" 은 매끈한 모양 탭의 화살표다 — cell 이 shape 인자로 받는다.
일감 해시에는 펫 구성표만 이 폴더 파일이 든다(build._hashes) — 고치면 펫만 다시 굽는다.
윈도우 워커는 spawn 이라 build.py 가 모듈 머리에서 읽어야 워커에도 등록된다.

  python -m hdpet <폴더> [결…]      hd.py 의 시트(sheet_<결>.png)를 펫 결로 — hd.py 에서는 이 폴더를 안 읽는다
"""
import hd

PETS = {}
_render, _frames, _rgba = hd.render, hd.frames, hd.rgba_bytes


def register(sid, obj):
    PETS[sid] = obj
    hd.STYLES[sid] = obj


def _split(style):
    """"whitecat@dart" → ("whitecat", "dart") — 매끈한 모양 탭의 화살표(build.build_hd_shape)"""
    sid, _, shape = style.partition("@")
    return sid, shape or None


class _Mask:
    """표식 판을 그리는 결: 같은 층 · 같은 알파로 그리되 색 대신 커서면 1, 아니면 0. 그림자는 0"""

    def __init__(self, pet):
        self.pet = pet
        self.shadow = (0.0, 0.0, 0.0, pet.shadow[3])
        for k in ("shadow_off", "shadow_blur", "shadow_hard", "glow_n", "clip", "soft", "tip_body"):
            if hasattr(pet, k):
                setattr(self, k, getattr(pet, k))

    def extra(self, name, frame, layers, hot):
        pet = self.pet
        out = []
        for L in layers:
            c = (1.0,) * 3 if L.get("cur") else (0.0,) * 3
            M = dict(L)
            if L.get("ink"):
                M["paint"] = lambda x, y, e, nx, ny, fr, c=c: (c, 1.0)
                M["ink"], M["noglow"] = False, True
            elif L.get("paint"):
                M["paint"] = lambda x, y, e, nx, ny, fr, c=c, p=L["paint"]: (c, p(x, y, e, nx, ny, fr)[1])
            else:
                M["paint"] = lambda x, y, e, nx, ny, fr, c=c, w=L.get("warn", False): (c, pet.body(x, y, e, nx, ny, w, fr)[1])
            if L.get("glow") is not None:
                M["glow"] = lambda x, y, e, fr, c=c, g=L["glow"]: (c, g(x, y, e, fr)[1])
            elif not (L.get("ink") or L.get("noglow")) and hasattr(pet, "glow"):
                M["glow"] = lambda x, y, e, fr, c=c, w=L.get("warn", False): (c, pet.glow(x, y, e, w, fr)[1])
            out.append(M)
        return out


def render(style, name, frame=0.0):
    """펫 결이면 칸 그림만 바꿔 hd.render. 결이 cursor 면 다섯째 판(커서 몫, 미리 곱한 0–1)을 붙여 돌려준다 —
    같은 층을 한 번 더 그리되 커서 층만 1 로 칠한 판이라 rgba_bytes 가 칸마다 커서인지 가른다"""
    sid, shape = _split(style)
    pet = PETS.get(sid)
    if pet is None:
        return _render(style, name, frame)
    cell, m = hd.cell, hd.M
    hd.cell = lambda n, fr=0.0, s=0.0, t=False: pet.cell(n, fr, s, t, shape=shape)
    hd.M = pet.M
    try:
        img, hot = _render(sid, name, frame)
        if not getattr(pet, "cursor", False):
            return img, hot
        hd.STYLES[sid] = _Mask(pet)
        try:
            mask = _render(sid, name, frame)[0][0]
        finally:
            hd.STYLES[sid] = pet
        return (*img, mask), hot
    finally:
        hd.cell, hd.M = cell, m


def rgba_bytes(img, size):
    """다섯째 판이 있으면 gen/sea.mark 와 같은 표식을 박는다 — 불투명 칸은 파랑 끝 비트, 반투명 칸은 알파 끝 비트를
    커서면 홀수, 아니면 짝수로. 칸의 커서 몫이 절반 넘으면 커서다. 판 넷이면 원래 함수 그대로라 바이트가 같다"""
    if len(img) == 4:
        return _rgba(img, size)
    A, C = img[3], img[4]
    buf = bytearray(_rgba(img[:4], size))
    for i in range(size * size):
        a = buf[i * 4 + 3]
        if not a:
            continue
        on = C[i] * 2 >= A[i]
        if a == 255:
            buf[i * 4 + 2] = buf[i * 4 + 2] | 1 if on else buf[i * 4 + 2] & ~1
        else:
            buf[i * 4 + 3] = (a | 1 if a < 254 else 253) if on else (a & ~1 or 2)
    return bytes(buf)


def frames(style, name):
    pet = PETS.get(_split(style)[0])
    return (pet.NF, pet.RATE) if pet else _frames(style, name)


def hot(style, name):
    """그 결 칸의 핫스팟(칸 단위) — 시안 데이터가 소수 핫스팟을 싣는다(build.hd_bit). "결@모양" 은 그 모양 화살표"""
    sid, shape = _split(style)
    pet = PETS.get(sid)
    return pet.cell(name, shape=shape)[1] if pet else hd.cell(name)[1]


hd.render, hd.frames, hd.rgba_bytes = render, frames, rgba_bytes

from . import bukang, whitecat  # noqa: E402,F401

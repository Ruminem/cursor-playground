# SPDX-License-Identifier: Apache-2.0
"""고화질 펫 결 — 칸마다 그 동물이 하는 짓을 그린 장면(art 구성표의 HD 판). 읽으면 hd.STYLES 에 등록된다.

hd.py 틀(render 의 그림자 · 층 · 빛)은 그대로 쓰고 칸 그림(hd.cell)만 결마다 바꾼다. hd.py 를 고치면 고화질 27종이
다 다시 구워지므로 hd.render · hd.frames 를 여기서 감싼다 — 펫 결이 아니면 원래 함수를 그대로 불러 바이트가 같다.
펫 결이 다른 것:
  cell      칸 장면 함수 (name, frame, soft, tip_body) → (레이어, 핫스팟). 핫스팟은 art 칸 + 0.5
  M         번짐을 칠하는 거리(hd.M). 먹선 · 그늘 한 겹이라 3.5 까지 잴 일이 없다
  NF, RATE  한 바퀴 장 수 · 장마다 1/60초 틱. 장면이 NF 장으로 나뉘어 있어 LOOP 로 장 수를 정하지 않는다
일감 해시에는 펫 구성표만 이 폴더 파일이 든다(build._hashes) — 고치면 펫만 다시 굽는다.
윈도우 워커는 spawn 이라 build.py 가 모듈 머리에서 읽어야 워커에도 등록된다.

  python -m hdpet <폴더> [결…]      hd.py 의 시트(sheet_<결>.png)를 펫 결로 — hd.py 에서는 이 폴더를 안 읽는다
"""
import hd

PETS = {}
_render, _frames = hd.render, hd.frames


def register(sid, obj):
    PETS[sid] = obj
    hd.STYLES[sid] = obj


def render(style, name, frame=0.0):
    pet = PETS.get(style)
    if pet is None:
        return _render(style, name, frame)
    cell, m = hd.cell, hd.M
    hd.cell, hd.M = pet.cell, pet.M
    try:
        return _render(style, name, frame)
    finally:
        hd.cell, hd.M = cell, m


def frames(style, name):
    pet = PETS.get(style)
    return (pet.NF, pet.RATE) if pet else _frames(style, name)


def hot(style, name):
    """그 결 칸의 핫스팟(칸 단위) — 시안 데이터가 소수 핫스팟을 싣는다(build.hd_bit)"""
    pet = PETS.get(style)
    return (pet.cell if pet else hd.cell)(name)[1]


hd.render, hd.frames = render, frames

from . import whitecat  # noqa: E402,F401

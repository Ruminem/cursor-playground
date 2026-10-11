# SPDX-License-Identifier: Apache-2.0
"""이펙트 · 애니 20결 — hd.py 틀에 결만 더 얹는다. 읽으면 hd.STYLES 에 등록된다.

결마다 LOOP(한 바퀴 초)를 달아 17칸이 다 움직이고(hd.frames), 빛을 더해 1 을 넘기는 결이라 clip 을 켠다.
빌드 일감 해시에 이 폴더 파일이 다 든다(build._hashes 의 hd) — 고치면 이 20결만 다시 굽는다.
윈도우 워커는 spawn 이라 build.py 가 모듈 머리에서 읽어야 워커에도 등록된다.
"""
import math

import hd
from hd import (N, U, M, TAU, clamp, smooth, lerp, ramp, ramp_to, noise, hsh, dome, dot3, scale,  # noqa: F401
                L3, H3, LX, LY, WHITE, circle, capsule, ring, arc, poly, union, smin, cut, at, turn, grow,
                field, shrink, rgba_bytes, png, CELLS)

hypot, exp, sin, cos, atan2, floor = math.hypot, math.exp, math.sin, math.cos, math.atan2, math.floor


def register(sid, obj):
    obj.clip = True
    hd.STYLES[sid] = obj


from . import light, fire, water, digital  # noqa: E402,F401

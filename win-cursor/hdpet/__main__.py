# SPDX-License-Identifier: Apache-2.0
"""python -m hdpet <폴더> [결…] — hd.py 의 시트를 펫 결로 뽑는다. 한 프로세스로 돈다(윈도우 spawn 워커는 감싼 hd.render 를 모른다)

  python -m hdpet <폴더> --arrows <결>   화살표만 모양(shapes.json) × 장 넷으로 한 장 — 매끈한 모양 탭 빼꼼을 견줄 때"""
import os
import sys

import hd
import hdpet

out = sys.argv[1]
if sys.argv[2:3] == ["--arrows"]:
    import json
    style = sys.argv[3]
    shapes = [s["id"] for s in json.load(open(os.path.join(os.path.dirname(hd.__file__), "shapes.json"), encoding="utf-8"))]
    got = {}
    for k, shp in enumerate(shapes):
        for j, fr in enumerate((0.0, 0.25, 0.5, 0.75)):
            img, hot = hd.render(style if k == 0 else f"{style}@{shp}", "arrow", fr)
            img = img[:4]                                   # 다섯째 판(커서 몫)은 시트에 안 그린다
            got[f"{shp}:{j}"] = (hd.shrink(img, 128), hd.shrink(img, 32), hot)
            print(shp, fr, hot, flush=True)
    hd.CELLS = list(got)
    hd.sheet(out, f"{style}_arrows", got)
    print("시트", os.path.join(out, f"sheet_{style}_arrows.png"), flush=True)
    sys.exit()
for style in sys.argv[2:] or list(hdpet.PETS):
    got = {}
    for name in hd.CELLS:
        _, name, b128, b32, hot = hd.job((style, name, out))
        got[name] = (b128[:4], b32[:4], hot)                # 다섯째 판(커서 몫)은 시트에 안 그린다
        print(style, name, flush=True)
    hd.sheet(out, style, got)
    print("시트", os.path.join(out, f"sheet_{style}.png"), flush=True)

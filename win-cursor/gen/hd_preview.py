# SPDX-License-Identifier: Apache-2.0
"""HD 시안 페이지(아티팩트)를 뽑는다: hd.py 그림을 128px PNG 로 구워 JSON 두 개로 나누고 페이지 틀을 옆에 둔다.
정지 17칸 + 움직임 맛보기 칸 12장씩. 쓰는 법: python gen/hd_preview.py <나올 html>
→ <html> 과 같은 폴더에 hd-new.json(hd.NEW) · hd-old.json(나머지). 페이지가 둘을 fetch 로 받는다 —
열 결일 때 그림을 html 에 끼운 판이 8MB 였고 스무 결이면 아티팩트 한도 16MB 를 넘는다. 올릴 때 두 JSON 을
files 로 같이 싣는다. 로컬에서 볼 때는 file:// 로 열면 fetch 가 막히니 http 서버로 연다.
올린 곳(비공개 아티팩트, 2026-10-10): https://claude.ai/artifact/WToSbg2DiN2QL76z6SQ2or — 다시 올릴 때 이 주소에 덮어쓴다"""
import base64, json, os, sys
from concurrent.futures import ProcessPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hd

ANIM = ["arrow", "busy", "wait", "hand"]
FR = 12


def one(arg):
    style, name, k = arg
    img, hot = hd.render(style, name, k / FR)
    small = hd.shrink(img, 128)
    raw = hd.rgba_bytes(small, 128)
    return style, name, k, base64.b64encode(hd.png(raw, 128, 128)).decode(), [hot[0] / 2, hot[1] / 2]


if __name__ == "__main__":
    jobs = [(s, c, k) for s in hd.STYLES for c in hd.CELLS for k in (range(FR) if c in ANIM else [0])]
    out = {s: {} for s in hd.STYLES}
    with ProcessPoolExecutor() as ex:
        for s, c, k, b, hot in ex.map(one, jobs):
            d = out[s].setdefault(c, {"hot": hot, "frames": []})
            d["frames"].append((k, b))
    for s in out:
        for c in out[s]:
            out[s][c]["frames"] = [b for _, b in sorted(out[s][c]["frames"])]
    p = sys.argv[1]
    with open(os.path.join(HERE, "hd_preview.tpl.html"), encoding="utf-8") as fh:
        tpl = fh.read()
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(tpl)
    print(len(jobs), "장 ·", os.path.basename(p), os.path.getsize(p) // 1024, "KB")
    for name, keep in (("hd-new.json", lambda s: s in hd.NEW), ("hd-old.json", lambda s: s not in hd.NEW)):
        q = os.path.join(os.path.dirname(os.path.abspath(p)), name)
        with open(q, "w", encoding="utf-8") as fh:
            json.dump({"cells": hd.CELLS, "styles": {s: v for s, v in out.items() if keep(s)}}, fh, separators=(",", ":"))
        print(name, os.path.getsize(q) // 1024, "KB")

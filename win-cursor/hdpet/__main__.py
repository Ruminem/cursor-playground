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
if sys.argv[2:3] == ["--small"]:
    # 실물 32 판을 4배(최근접)로 — 칸마다 한 줄, 장 넷 × 흰 · 어두운 바탕. 32 에서 무엇으로 읽히나 볼 때
    style, cells = sys.argv[3], sys.argv[4:] or hd.CELLS
    Z, frs, bgs = 4, (0.0, 0.25, 0.5, 0.75), ((255, 255, 255), (32, 33, 36))
    cw = 32 * Z + 8
    W, H = cw * len(frs) * 2, cw * len(cells)
    pix = bytearray(b"\xc8" * (W * H * 3))
    for r, name in enumerate(cells):
        for j, fr in enumerate(frs):
            img, _ = hd.render(style, name, fr)
            R, G, B, A = hd.shrink(img[:4], 32)
            for b, bg in enumerate(bgs):
                ox, oy = (b * len(frs) + j) * cw + 4, r * cw + 4
                for y in range(32 * Z):
                    for x in range(32 * Z):
                        i = (y // Z) * 32 + x // Z
                        k = 1 - A[i]
                        o = ((oy + y) * W + ox + x) * 3
                        pix[o:o + 3] = bytes(round(min(1, c + bc / 255 * k) * 255) for c, bc in zip((R[i], G[i], B[i]), bg))
        print(name, flush=True)
    raw = b"".join(b"\x00" + bytes(pix[y * W * 3:(y + 1) * W * 3]) for y in range(H))
    p = os.path.join(out, f"small_{style}.png")
    import struct
    import zlib

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    with open(p, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
                 + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))
    print("시트", p, flush=True)
    sys.exit()
for style in sys.argv[2:] or list(hdpet.PETS):
    got = {}
    for name in hd.CELLS:
        _, name, b128, b32, hot = hd.job((style, name, out))
        got[name] = (b128[:4], b32[:4], hot)                # 다섯째 판(커서 몫)은 시트에 안 그린다
        print(style, name, flush=True)
    hd.sheet(out, style, got)
    print("시트", os.path.join(out, f"sheet_{style}.png"), flush=True)

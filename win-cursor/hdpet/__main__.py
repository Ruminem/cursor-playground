# SPDX-License-Identifier: Apache-2.0
"""python -m hdpet <폴더> [결…] — hd.py 의 시트를 펫 결로 뽑는다. 한 프로세스로 돈다(윈도우 spawn 워커는 감싼 hd.render 를 모른다)"""
import os
import sys

import hd
import hdpet

out = sys.argv[1]
for style in sys.argv[2:] or list(hdpet.PETS):
    got = {}
    for name in hd.CELLS:
        _, name, b128, b32, hot = hd.job((style, name, out))
        got[name] = (b128, b32, hot)
        print(style, name, flush=True)
    hd.sheet(out, style, got)
    print("시트", os.path.join(out, f"sheet_{style}.png"), flush=True)

# SPDX-License-Identifier: Apache-2.0
"""build.py 가 바뀐 구성표 자리만 갈아 끼워 만든 data/<모양>.json 이,
통째로 만든 것과 같은지 본다. 다르면 시안 페이지가 낡은 그림을 보여 준다.

사용법: python test_stamp.py — 구성표 세 종·모양 하나로 줄여서 몇 초 안에 끝난다.
"""
import json
import re

import build

# 제목 옆 버전 표시. 여기가 비거나 형식이 깨지면 Pages 에 실렸는지 볼 자가 없어진다
ver = build.version()
assert re.fullmatch(r"v\d+\.\d+\.\d+( · [0-9a-f]{7,})?", ver), f"버전 표시가 이상함: {ver!r}"

# 주소 줄에 붙여넣은 주소를 읽는 정규식이, 그 줄이 스스로 뱉는 주소를 도로 읽는지.
# 둘이 갈리면 복사한 주소를 다시 붙여넣었을 때 "못 읽음" 이 된다
tpl = open("preview.tpl.html", encoding="utf-8").read()
src = re.search(r"var m = /(\^\(\?:cursor-playground.+?)/\.exec", tpl)
assert src, "preview.tpl.html 에서 주소를 읽는 정규식을 못 찾음"
parse = re.compile(src.group(1).replace(r"\/", "/"))
visit = "a1b2c3d4e5f60789"
for url, want in [
    (f"cursor-playground://apply/electric/{visit}/48/270", ("electric", "48", "270", None)),
    (f"apply/electric/{visit}/48/270/cutout", ("electric", "48", "270", "cutout")),
]:
    m = parse.fullmatch(url)
    assert m and m.groups() == want, f"주소를 못 읽음: {url}"
for bad in ["cursor-playground://restore/" + visit, "apply/electric", "https://example.com"]:
    assert not parse.fullmatch(bad), f"엉뚱한 주소를 읽어 버림: {bad}"

# 전부 돌리면 2분이 넘는다. 지나는 길은 같으니 재료만 줄인다
build.SCHEMES = build.SCHEMES[:3]
shape_id = build.SHAPES[1]["id"]                 # 매끈한 모양 하나 (기본 모양은 이 파일을 안 만든다)
sids = [s["id"] for s in build.SCHEMES]

whole = build.shape_data(shape_id, sids, None)
# 파일로 나갔다 들어오는 길을 그대로 지나야 한다 (튜플이 리스트로 바뀌는 것 같은 어긋남을 잡는다)
old = json.loads(json.dumps(whole, separators=(",", ":")))
spliced = build.shape_data(shape_id, sids[1:2], old)   # 가운데 한 종만 다시 그렸다 치고

dump = lambda d: json.dumps(d, separators=(",", ":"))
assert dump(spliced) == dump(whole), "갈아 끼운 데이터가 통째로 만든 것과 다름"
assert list(spliced["data"]) == sids, f"구성표 차례가 어긋남: {list(spliced['data'])}"
print(f"갈아 끼우기 OK · {shape_id} · 구성표 {len(sids)}종 · {len(dump(whole))}바이트")

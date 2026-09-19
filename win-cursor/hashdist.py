# SPDX-License-Identifier: Apache-2.0
"""dist/ 전체를 한 해시로 묶는다. 러너 OS 가 달라도 같은 커서가 나오는지 보려고 둔다.
사용법: python hashdist.py"""
import hashlib
import pathlib

root = pathlib.Path(__file__).parent / "dist"
h = hashlib.sha256()
n = 0
for p in sorted(root.rglob("*")):
    if p.is_file():
        h.update(p.relative_to(root).as_posix().encode())
        h.update(p.read_bytes())
        n += 1
print(f"dist 파일 {n}개 · sha256 {h.hexdigest()}")

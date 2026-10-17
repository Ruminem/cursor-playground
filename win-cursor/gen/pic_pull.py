# SPDX-License-Identifier: Apache-2.0
"""노션 시안 DB 의 포즈 행을 그림 결 재료(pic/<구성표>/)로 받는다 — hdpic.py 가 이걸 굽는다.

    NOTION_TOKEN=… python gen/pic_pull.py shibapic SA-8 SA-9 …

행마다 '그림' 칸에서 <이름>_pose_<자세>.png(원본)와 _paw<n>(앞발 층)만 받는다. 기호 자리는 받지 않고 그림을 재서
cells.json 에 손으로 적는다 — 노션 코멘트는 agy 가 다른 일을 하며 덮어써 2026-10-18 세 행에서 사라졌다. _check 는 사람이 보는 그림이고 _back 은 원본과 바이트가 같아야 해서(층을 나눌 때 원본을
안 깎음) 받지 않는다 — 다르면 멈춘다. 손으로 돌리고, 받은 것을 커밋한다. 에셋은 agy 가 만든다(paint 스킬)"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

DB = "fd2c7afd1b9d4201a36ba196bded6b9b"
H = {"Authorization": "Bearer " + os.environ["NOTION_TOKEN"], "Notion-Version": "2022-06-28"}


def call(url, body=None):
    req = urllib.request.Request(url, json.dumps(body).encode() if body else None,
                                 {**H, "Content-Type": "application/json"} if body else H)
    return json.load(urllib.request.urlopen(req))


def fetch(url):
    return urllib.request.urlopen(url).read()


def main():
    sid, rows = sys.argv[1], sys.argv[2:]
    out = Path(__file__).resolve().parent.parent / "pic" / sid
    out.mkdir(parents=True, exist_ok=True)
    for sa in rows:
        page = call(f"https://api.notion.com/v1/databases/{DB}/query",
                    {"filter": {"property": "ID", "unique_id": {"equals": int(sa.split("-")[1])}}})["results"][0]
        files = {f["name"]: (f.get("file") or f.get("external"))["url"] for f in page["properties"]["그림"]["files"]}
        orig = [n for n in files if re.fullmatch(r"[a-z]+_pose_[a-z]+\.png", n)]
        assert len(orig) == 1, f"{sa}: 원본이 하나가 아님 {sorted(files)}"
        pose = orig[0][:-4].rsplit("_", 1)[1]
        body = fetch(files[orig[0]])
        (out / f"{pose}.png").write_bytes(body)
        for n, url in files.items():
            if m := re.fullmatch(rf"[a-z]+_pose_{pose}_paw(\d)\.png", n):
                (out / f"{pose}_paw{m[1]}.png").write_bytes(fetch(url))
            elif n.endswith(f"_{pose}_back.png"):
                assert fetch(url) == body, f"{sa}: 뒷층이 원본과 다름 — 뒷층을 따로 받게 고칠 것"
        print(sa, pose, sorted(p.name for p in out.glob(f"{pose}*.png")))


if __name__ == "__main__":
    main()

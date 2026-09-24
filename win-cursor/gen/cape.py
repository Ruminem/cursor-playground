# SPDX-License-Identifier: Apache-2.0
"""구성표 하나를 맥 Mousecape 용 .cape 로 뽑는다. 맥에서 되는지 재 보려는 시험판이다 (docs/macos.md).

사용법: python gen/cape.py electric [-o out/electric.cape] [--scales 1,2]

기본 모양(테마 그림 그대로)만 뽑는다. 손으로 돌리고 빌드는 안 부른다. 빌드 해시와 CI 캐시 키에 안 들어간다.

.cape 는 plist 하나다. 맥 커서 이름마다 {프레임 수, 프레임 길이(초), 핫스팟·크기(포인트), 배율마다 PNG 한 장} 이고
여러 프레임은 세로로 쌓은 한 장에 담는다. 맥은 프레임 길이가 하나뿐이고 Mousecape 는 24장까지만 받아서
그보다 많으면 한 바퀴 시간을 지키며 솎는다. 윈도우 칸 중 up·pen·pin·person 은 맥에 자리가 없어 버린다.
"""
import argparse
import json
import plistlib
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import make_cur  # noqa: E402

POINTS = 32       # 맥 커서 한 변(포인트). Mousecape 가 핫스팟을 31.99 까지만 받아서 이게 상한이다
MAX_FRAMES = 24   # Mousecape 가 받는 프레임 수 상한 (MCMaxFrameCount)

# 윈도우 칸 → 맥 커서 이름들 (Mousecape MCDefs.m 의 cursorMap). 한 칸이 여러 이름을 채운다.
# 시안 페이지의 .cape 버튼도 같은 mac.json 을 읽는다.
# 원본 Mousecape 는 이름 하나라도 등록에 실패하면 전체를 포기하므로 오래된 이름만 넣었다.
# macOS 26 에서 늘어난 화살표·I빔 이름은 Mousecape-swiftUI 가 런타임에 찾아 같이 채운다.
MAC = json.loads((ROOT / "mac.json").read_text(encoding="utf-8"))


def pick(n: int, rate: int) -> tuple[list[int], float]:
    """n 장 × rate 틱(1/60초)을 MAX_FRAMES 장 이하로 솎는다. 고른 장 번호와 한 장의 길이(초)."""
    if n <= MAX_FRAMES:
        return list(range(n)), rate / 60
    return [i * n // MAX_FRAMES for i in range(MAX_FRAMES)], n * rate / 60 / MAX_FRAMES


def raw_rows(png: bytes) -> bytes:
    """make_cur 가 구운 PNG(IDAT 하나, 행 필터 없음)에서 행 바이트를 도로 꺼낸다."""
    pos, data = 8, b""
    while pos < len(png):
        size, kind = struct.unpack(">I4s", png[pos:pos + 8])
        if kind == b"IDAT":
            data += png[pos + 8:pos + 8 + size]
        pos += 12 + size
    return zlib.decompress(data)


def sheet(frames: list[str], px: int, src: int) -> bytes:
    """프레임들을 px × px 로 키워 세로로 쌓은 PNG 한 장"""
    raw = b"".join(raw_rows(make_cur.txt_to_png(f, px, src)) for f in frames)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    ihdr = struct.pack(">IIBBBBB", px, px * len(frames), 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def cursor(text: str, scales: list[int]) -> dict:
    src = make_cur.canvas_size(text)
    frames = make_cur.split_frames(text)
    idx, duration = pick(len(frames), make_cur.read_rate(text))
    frames = [frames[i] for i in idx]
    hx, hy = make_cur.read_hotspot(text) or (0, 0)
    k = POINTS / src
    return {
        "FrameCount": len(frames),
        "FrameDuration": duration if len(frames) > 1 else 1.0,
        "HotSpotX": min(hx * k, POINTS - 0.01),
        "HotSpotY": min(hy * k, POINTS - 0.01),
        "PointsWide": float(POINTS),
        "PointsHigh": float(POINTS),
        "Representations": [sheet(frames, POINTS * s, src) for s in scales],
    }


def cape(scheme: str, scales: list[int]) -> dict:
    names = {s["id"]: s for s in json.loads((ROOT / "schemes.json").read_text(encoding="utf-8"))}
    if scheme not in names:
        raise SystemExit(f"schemes.json 에 없는 구성표: {scheme}")
    cursors = {}
    for slot, idents in MAC.items():
        body = cursor((ROOT / "art" / scheme / f"{slot}.txt").read_text(encoding="utf-8"), scales)
        for ident in idents:
            cursors[ident] = body
    return {
        "Author": "cursor-playground",
        "CapeName": f"cursor-playground {names[scheme]['name']}",
        "CapeVersion": 1.0,
        "Cloud": False,
        "HiDPI": max(scales) > 1,
        "Identifier": f"io.github.ruminem.cursor-playground.{scheme}",
        "MinimumVersion": 2.0,
        "Version": 2.0,
        "Cursors": cursors,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scheme")
    ap.add_argument("-o", "--out", type=Path)
    ap.add_argument("--scales", default="1,2", help="배율 목록. 1 = 32px, 2 = 64px (기본 1,2)")
    a = ap.parse_args()
    scales = [int(s) for s in a.scales.split(",")]
    out = a.out or ROOT / "out" / f"{a.scheme}.cape"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = cape(a.scheme, scales)
    out.write_bytes(plistlib.dumps(data, fmt=plistlib.FMT_XML))  # 예제 cape 들이 XML plist 다
    body = data["Cursors"]["com.apple.coregraphics.Arrow"]
    print(f"{out}  {out.stat().st_size // 1024} KiB, 맥 이름 {len(data['Cursors'])}개, "
          f"화살표 {body['FrameCount']}장 × {body['FrameDuration']:.4f}초")


if __name__ == "__main__":
    main()

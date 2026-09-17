# SPDX-License-Identifier: Apache-2.0
"""그림(.txt 픽셀아트 또는 .png)을 윈도우 커서 파일(.cur)로 만든다.

사용법: python make_cur.py art/arrow.txt out/arrow.cur --hotspot 0,0

.cur 는 .ico 와 같은 구조에 핫스팟(클릭 지점) 좌표만 더한 형식이고,
Vista 이후로는 이미지 자리에 PNG 를 그대로 넣을 수 있다.
"""
import argparse
import struct
import zlib
from pathlib import Path

# 픽셀아트 글자 → RGBA. 여기 없는 글자는 오류로 처리한다.
PALETTE = {
    ".": (0, 0, 0, 0),
    "#": (0, 0, 0, 255),
    "o": (255, 255, 255, 255),
    "r": (230, 60, 60, 255),
    "g": (60, 190, 90, 255),
    "b": (60, 120, 230, 255),
    "y": (250, 210, 50, 255),
    "p": (240, 120, 190, 255),
}
MIN_SIZE = 32  # 윈도우 기본 커서 크기. 작은 그림은 오른쪽·아래를 투명으로 채운다


def txt_to_png(text: str) -> bytes:
    rows = [line.rstrip("\n") for line in text.splitlines() if line.strip()]
    w = max(MIN_SIZE, max(len(r) for r in rows))
    h = max(MIN_SIZE, len(rows))
    w = h = max(w, h)  # 정사각형이 아니면 윈도우가 늘려서 찌그러진다
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # PNG 행 필터: 없음
        row = rows[y] if y < len(rows) else ""
        for x in range(w):
            ch = row[x] if x < len(row) else "."
            if ch not in PALETTE:
                raise SystemExit(f"{y + 1}행 {x + 1}열: 팔레트에 없는 글자 {ch!r}")
            raw += bytes(PALETTE[ch])

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)  # 8비트 RGBA
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b"")


def png_to_cur(png: bytes, hotspot: tuple[int, int]) -> bytes:
    if png[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("PNG 파일이 아님")
    w, h = struct.unpack(">II", png[16:24])
    if w > 256 or h > 256:
        raise SystemExit(f"커서는 256x256 까지만 됨 (지금 {w}x{h})")
    hx, hy = hotspot
    if not (0 <= hx < w and 0 <= hy < h):
        raise SystemExit(f"핫스팟 {hx},{hy} 가 그림({w}x{h}) 밖에 있음")
    header = struct.pack("<HHH", 0, 2, 1)  # 예약, 종류(2=커서), 이미지 수
    entry = struct.pack("<BBBBHHII", w % 256, h % 256, 0, 0, hx, hy, len(png), 6 + 16)
    return header + entry + png


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path, help=".txt 픽셀아트 또는 .png")
    ap.add_argument("dst", type=Path, help="만들 .cur 경로")
    ap.add_argument("--hotspot", default="0,0", help="클릭 지점 x,y (기본 0,0 = 왼쪽 위)")
    ap.add_argument("--png", type=Path, help="중간 PNG 도 저장 (txt 입력일 때)")
    args = ap.parse_args()

    if args.src.suffix.lower() == ".txt":
        png = txt_to_png(args.src.read_text(encoding="utf-8"))
        if args.png:
            args.png.parent.mkdir(parents=True, exist_ok=True)
            args.png.write_bytes(png)
    else:
        png = args.src.read_bytes()

    hotspot = tuple(int(v) for v in args.hotspot.split(","))
    args.dst.parent.mkdir(parents=True, exist_ok=True)
    args.dst.write_bytes(png_to_cur(png, hotspot))
    print(f"{args.dst} 만듦")


if __name__ == "__main__":
    main()

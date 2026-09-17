# SPDX-License-Identifier: Apache-2.0
"""그림(.txt 픽셀아트 또는 .png)을 윈도우 커서 파일(.cur)로 만든다.

사용법: python make_cur.py art/pink/hand.txt out/hand.cur [--hotspot 5,4]

txt 첫 줄에 `hotspot x,y` 를 적어 두면 핫스팟으로 쓴다. --hotspot 을 주면 그쪽이 우선.

.cur 는 .ico 와 같은 구조에 핫스팟(클릭 지점) 좌표만 더한 형식이고,
Vista 이후로는 이미지 자리에 PNG 를 그대로 넣을 수 있다.

txt 에서 만들 때는 32·48·64·96·128px 이미지를 한 파일에 담는다. 윈도우 포인터 크기를 키우면
윈도우가 그 크기에 맞는 이미지를 골라 쓰므로, 32px 한 장을 늘릴 때처럼 픽셀이 뭉개지지 않는다.
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
    "c": (40, 235, 255, 255),   # 네온 청록
    "C": (40, 235, 255, 70),    # 네온 청록 번짐 (반투명)
    "m": (255, 70, 200, 255),   # 네온 자홍
    "M": (255, 70, 200, 70),    # 네온 자홍 번짐 (반투명)
    "k": (18, 14, 28, 255),     # 거의 검정
    ":": (0, 0, 0, 90),         # 그림자 (반투명)
    "d": (110, 110, 120, 255),  # 어두운 회색
    "s": (196, 202, 214, 255),  # 은색
    "Y": (232, 176, 48, 255),   # 금색
    "n": (140, 88, 44, 255),    # 나무
    "N": (84, 50, 24, 255),     # 어두운 나무
    "R": (190, 40, 50, 255),    # 진홍
}
MIN_SIZE = 32  # 윈도우 기본 커서 크기. 작은 그림은 오른쪽·아래를 투명으로 채운다


def read_hotspot(text: str) -> tuple[int, int] | None:
    for line in text.splitlines():
        if line.startswith("hotspot"):
            x, y = line.split()[1].split(",")
            return int(x), int(y)
    return None


def read_palette(text: str) -> dict[str, tuple[int, int, int, int]]:
    """기본 팔레트에 파일의 `color X RRGGBB[AA]` 줄을 덮어쓴다."""
    palette = dict(PALETTE)
    for line in text.splitlines():
        if line.startswith("color "):
            _, ch, hexcode = line.split()
            if len(ch) != 1 or ch == "." or len(hexcode) not in (6, 8):
                raise SystemExit(f"잘못된 색 줄: {line!r}")
            r, g, b, a = bytes.fromhex(hexcode if len(hexcode) == 8 else hexcode + "ff")
            palette[ch] = (r, g, b, a)
    return palette


SIZES = (32, 48, 64, 96, 128)  # 윈도우 포인터 크기 설정에서 쓰는 값들


def canvas_size(text: str) -> int:
    rows = [line for line in text.splitlines()
            if line.strip() and not line.startswith(("hotspot", "color "))]
    # 정사각형이 아니면 윈도우가 늘려서 찌그러진다
    return max(MIN_SIZE, max(len(r) for r in rows), len(rows))


def txt_to_png(text: str, size: int | None = None) -> bytes:
    """size 를 주면 픽셀을 그대로 키우거나 줄여(최근접) size x size 로 만든다."""
    palette = read_palette(text)
    rows = [line for line in text.splitlines()
            if line.strip() and not line.startswith(("hotspot", "color "))]
    src = canvas_size(text)
    w = h = size or src
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # PNG 행 필터: 없음
        sy = y * src // h
        row = rows[sy] if sy < len(rows) else ""
        for x in range(w):
            sx = x * src // w
            ch = row[sx] if sx < len(row) else "."
            if ch not in palette:
                raise SystemExit(f"{sy + 1}행 {sx + 1}열: 팔레트에 없는 글자 {ch!r}")
            raw += bytes(palette[ch])

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)  # 8비트 RGBA
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b"")


def png_to_cur(png: bytes, hotspot: tuple[int, int]) -> bytes:
    return pngs_to_cur([(png, hotspot)])


def pngs_to_cur(images: list[tuple[bytes, tuple[int, int]]]) -> bytes:
    header = struct.pack("<HHH", 0, 2, len(images))  # 예약, 종류(2=커서), 이미지 수
    entries, data = b"", b""
    offset = 6 + 16 * len(images)
    for png, (hx, hy) in images:
        if png[:8] != b"\x89PNG\r\n\x1a\n":
            raise SystemExit("PNG 파일이 아님")
        w, h = struct.unpack(">II", png[16:24])
        if w > 256 or h > 256:
            raise SystemExit(f"커서는 256x256 까지만 됨 (지금 {w}x{h})")
        if not (0 <= hx < w and 0 <= hy < h):
            raise SystemExit(f"핫스팟 {hx},{hy} 가 그림({w}x{h}) 밖에 있음")
        entries += struct.pack("<BBBBHHII", w % 256, h % 256, 0, 0, hx, hy, len(png), offset + len(data))
        data += png
    return header + entries + data


def txt_to_cur(text: str, hotspot: tuple[int, int]) -> bytes:
    """SIZES 크기마다 이미지를 만들어 한 파일에 담는다. 핫스팟도 같은 비율로 옮긴다."""
    src = canvas_size(text)
    hx, hy = hotspot
    return pngs_to_cur([(txt_to_png(text, s), (hx * s // src, hy * s // src)) for s in SIZES])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path, help=".txt 픽셀아트 또는 .png")
    ap.add_argument("dst", type=Path, help="만들 .cur 경로")
    ap.add_argument("--hotspot", help="클릭 지점 x,y (기본: txt 의 hotspot 줄, 없으면 0,0 = 왼쪽 위)")
    ap.add_argument("--png", type=Path, help="중간 PNG 도 저장 (txt 입력일 때)")
    args = ap.parse_args()

    hotspot = (0, 0)
    text = None
    if args.src.suffix.lower() == ".txt":
        text = args.src.read_text(encoding="utf-8")
        hotspot = read_hotspot(text) or hotspot
        if args.png:
            args.png.parent.mkdir(parents=True, exist_ok=True)
            args.png.write_bytes(txt_to_png(text))

    if args.hotspot:
        hx, hy = args.hotspot.split(",")
        hotspot = (int(hx), int(hy))
    args.dst.parent.mkdir(parents=True, exist_ok=True)
    if text is not None:
        args.dst.write_bytes(txt_to_cur(text, hotspot))
    else:
        args.dst.write_bytes(png_to_cur(args.src.read_bytes(), hotspot))
    print(f"{args.dst} 만듦")


if __name__ == "__main__":
    main()

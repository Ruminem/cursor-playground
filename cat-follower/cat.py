# SPDX-License-Identifier: Apache-2.0
"""바탕화면 위에서 마우스 커서를 따라다니는 픽셀 고양이.

사용법:
  pythonw cat.py            고양이 띄우기 (창 없이 뒤에서 돎)
  python cat.py --stop      고양이 치우기
  python cat.py --toggle    떠 있으면 치우고, 없으면 띄움 (cat.bat 이 이걸 부름)
  python cat.py --scale 3   크기 (기본 2배)

커서에서 멀어지면 걸어가고, 옆에 오면 앉고, 커서가 한동안 가만히 있으면 잠든다.
창은 클릭을 그대로 통과시키므로 고양이 위를 눌러도 아래 프로그램이 눌린다.
그림은 art/*.txt (win-cursor 와 같은 텍스트 픽셀아트 형식). Python 표준 라이브러리만 씀.
"""
import argparse
import ctypes
import math
import os
import subprocess
import sys
import tempfile
import time
import tkinter as tk
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "win-cursor"))
from make_cur import is_row, read_palette, read_rate, split_frames  # noqa: E402

PID_FILE = Path(tempfile.gettempdir()) / "cursor-playground-cat.pid"
KEY = "#ff00fe"  # 창에서 투명하게 뺄 색. 그림에 쓰지 않는 색이어야 함

WALK_SPEED = 4.0      # 한 번 움직일 때 몇 px
NEAR = 30             # 이만큼 가까우면 멈춰 앉음
SLEEP_AFTER = 4.0     # 커서가 이만큼(초) 가만히 있으면 잠
WAKE_DISTANCE = 60    # 자는 동안 커서가 이만큼 움직이면 깸
TICK_MS = 30


# ── 한 번만 뜨게 하기 ────────────────────────────────────────────────────
def running_pid() -> int | None:
    """PID 파일의 프로세스가 아직 살아 있으면 그 PID"""
    try:
        pid = int(PID_FILE.read_text())
    except (OSError, ValueError):
        return None
    k32 = ctypes.windll.kernel32
    handle = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        return None
    code = ctypes.c_ulong()
    alive = k32.GetExitCodeProcess(handle, ctypes.byref(code)) and code.value == 259  # STILL_ACTIVE
    k32.CloseHandle(handle)
    return pid if alive else None


def stop() -> bool:
    pid = running_pid()
    if pid is None:
        return False
    # os.kill 은 윈도우에서 TerminateProcess 라 PID 만 맞으면 됨
    os.kill(pid, 9)
    PID_FILE.unlink(missing_ok=True)
    return True


# ── 그림 ────────────────────────────────────────────────────────────────
def load_frames(name: str, scale: int) -> tuple[list[tk.PhotoImage], list[tk.PhotoImage], int]:
    """art/<name>.txt → (오른쪽 보는 프레임들, 왼쪽 보는 프레임들, 프레임 간격 ms)"""
    text = (HERE / "art" / f"{name}.txt").read_text(encoding="utf-8")
    right, left = [], []
    for frame in split_frames(text):
        palette = read_palette(frame)
        rows = [r for r in frame.splitlines() if is_row(r)]
        for flip, out in ((False, right), (True, left)):
            img = tk.PhotoImage(width=CANVAS_W, height=CANVAS_H)
            for y, row in enumerate(rows):
                row = row.ljust(CANVAS_W, ".")[:CANVAS_W]
                if flip:
                    row = row[::-1]
                # 투명이 아닌 칸을 이어진 덩어리째 찍는다. 찍지 않은 칸은 PhotoImage 에서 투명으로 남음
                x = 0
                while x < CANVAS_W:
                    if row[x] == ".":
                        x += 1
                        continue
                    start = x
                    while x < CANVAS_W and row[x] != ".":
                        x += 1
                    colors = " ".join("#%02x%02x%02x" % palette[c][:3] for c in row[start:x])
                    img.put("{" + colors + "}", to=(start, y))
            out.append(img.zoom(scale, scale))
    return right, left, read_rate(text) * 1000 // 60


CANVAS_W, CANVAS_H = 26, 20


class Cat:
    def __init__(self, scale: int):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=KEY)
        self.root.attributes("-transparentcolor", KEY)
        self.w, self.h = CANVAS_W * scale, CANVAS_H * scale
        self.label = tk.Label(self.root, bg=KEY, bd=0, highlightthickness=0)
        self.label.pack()
        self.sprites = {name: load_frames(name, scale) for name in ("walk", "sit", "sleep")}
        # 고양이 발 가운데를 커서 오른쪽 아래에 둠
        self.foot = (self.w // 2, self.h - 2 * scale)
        px, py = self.root.winfo_pointerxy()
        self.x, self.y = float(px + 40), float(py + 40)
        self.state, self.facing = "sit", "right"
        self.frame, self.frame_at = 0, time.monotonic()
        self.still_since, self.last_pointer = time.monotonic(), (px, py)
        self.sleep_pointer = (px, py)
        self.root.geometry(f"{self.w}x{self.h}+{int(self.x)}+{int(self.y)}")
        self.root.update_idletasks()
        self.make_click_through()
        self.last_topmost = time.monotonic()

    def make_click_through(self) -> None:
        user32 = ctypes.windll.user32
        hwnd = int(self.root.wm_frame(), 16)
        GWL_EXSTYLE = -20
        # 겹친 창, 클릭 통과, 작업 표시줄에 안 뜸, 포커스 안 뺏음
        flags = 0x80000 | 0x20 | 0x80 | 0x8000000
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | flags)

    def set_state(self, state: str) -> None:
        if state != self.state:
            self.state, self.frame, self.frame_at = state, 0, time.monotonic()

    def tick(self) -> None:
        now = time.monotonic()
        px, py = self.root.winfo_pointerxy()
        if (px, py) != self.last_pointer:
            self.last_pointer, self.still_since = (px, py), now
        tx, ty = px + 18, py + 22  # 고양이가 설 자리: 커서 오른쪽 아래
        fx, fy = self.x + self.foot[0], self.y + self.foot[1]
        dx, dy = tx - fx, ty - fy
        dist = math.hypot(dx, dy)

        if self.state == "sleep":
            if math.hypot(px - self.sleep_pointer[0], py - self.sleep_pointer[1]) > WAKE_DISTANCE:
                self.set_state("walk")
        elif dist > NEAR:
            self.set_state("walk")
        elif self.state == "walk":
            self.set_state("sit")
        elif now - self.still_since > SLEEP_AFTER:
            self.set_state("sleep")
            self.sleep_pointer = (px, py)

        if self.state == "walk":
            if dist <= NEAR / 2:
                self.set_state("sit")
            else:
                step = min(WALK_SPEED, dist)
                self.x += dx / dist * step
                self.y += dy / dist * step
                if abs(dx) > 2:
                    self.facing = "right" if dx > 0 else "left"

        right, left, rate = self.sprites[self.state]
        if (now - self.frame_at) * 1000 >= rate:
            self.frame, self.frame_at = (self.frame + 1) % len(right), now
        images = right if self.facing == "right" else left
        self.label.configure(image=images[self.frame % len(images)])
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
        # 다른 창이 맨 위를 가져가도 가끔 다시 올라옴
        if now - self.last_topmost > 2:
            self.root.attributes("-topmost", True)
            self.last_topmost = now
        self.root.after(TICK_MS, self.tick)

    def run(self) -> None:
        self.root.after(TICK_MS, self.tick)
        self.root.mainloop()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stop", action="store_true", help="떠 있는 고양이를 치움")
    ap.add_argument("--toggle", action="store_true", help="떠 있으면 치우고, 없으면 띄움")
    ap.add_argument("--scale", type=int, default=2, choices=range(1, 7), help="크기 배율 (기본 2)")
    args = ap.parse_args()

    if args.stop:
        print("고양이를 치움" if stop() else "떠 있는 고양이가 없음")
        return
    if running_pid() is not None:
        if args.toggle:
            stop()
        return  # 이미 떠 있음
    if args.toggle and Path(sys.executable).name.lower() == "python.exe":
        # cat.bat 에서 콘솔 창이 남지 않게 pythonw 로 다시 띄움
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        if pythonw.exists():
            subprocess.Popen([str(pythonw), str(Path(__file__).resolve()), "--scale", str(args.scale)], close_fds=True)
            return

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 배율 높은 화면에서 흐려지지 않게
    except (AttributeError, OSError):
        pass
    PID_FILE.write_text(str(os.getpid()))
    try:
        Cat(args.scale).run()
    finally:
        if running_pid() == os.getpid():
            PID_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

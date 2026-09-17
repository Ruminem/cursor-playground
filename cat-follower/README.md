# cat-follower

**English** · [한국어](#korean)

A pixel cat that follows your mouse cursor around the Windows desktop.
It walks over when the cursor moves away, sits down next to it, and falls asleep when the cursor stays still.
Standard library only (Python 3.10+, tkinter).

## Running it

Double-click **[cat.bat](cat.bat)**. It shows the cat if it is not running and hides it if it is.

```sh
pythonw cat.py            # show the cat (runs in the background, no console)
python cat.py --stop      # hide the cat
python cat.py --toggle    # hide if running, show if not (what cat.bat calls)
python cat.py --scale 3   # size multiplier (default 2)
```

- Clicks go straight through the cat, so clicking on it still clicks whatever is underneath
- It stays on top, does not show up in the taskbar and never takes focus
- Only one cat runs at a time. The PID is kept in `%TEMP%\cursor-playground-cat.pid`

## Behaviour

| State | When |
|---|---|
| Walk | The cursor is more than 30px away from where the cat wants to stand (just below and to the right of the cursor) |
| Sit | It has reached that spot. The tail flicks |
| Sleep | The cursor has not moved for 4 seconds. Z letters float up |
| Wake | While asleep, the cursor moves more than 60px |

The numbers are constants at the top of [cat.py](cat.py) (`WALK_SPEED`, `NEAR`, `SLEEP_AFTER`, `WAKE_DISTANCE`).

## Art

[art/walk.txt](art/walk.txt) (4 frames), [art/sit.txt](art/sit.txt) (2 frames) and [art/sleep.txt](art/sleep.txt) (3 frames) use the same text pixel art format as [win-cursor](../win-cursor/README.md#drawing): one character per pixel, `color X RRGGBB` lines, `rate N` for frame time in 1/60 s, and `frame` lines between frames.
Draw the cat facing right; facing left is mirrored automatically. Semi-transparent colours are not supported because the window uses a colour key for transparency.

## How it works

- A borderless tkinter window with a transparent colour key, kept on top
- `WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE` set with `SetWindowLongW` makes it click-through, hidden from the taskbar and non-activating
- The process is made DPI-aware so the pixels stay sharp on scaled displays
- Every 30ms it reads the pointer position, moves the window and picks the sprite frame

---

## Korean

[English](#cat-follower) · **한국어**

윈도우 바탕화면에서 마우스 커서를 따라다니는 픽셀 고양이.
커서가 멀어지면 걸어오고, 옆에 오면 앉고, 커서가 가만히 있으면 잠듦.
표준 라이브러리만 씀 (Python 3.10+, tkinter).

### 실행

**[cat.bat](cat.bat)** 을 더블클릭. 고양이가 없으면 띄우고, 떠 있으면 치움.

```sh
pythonw cat.py            # 고양이 띄우기 (콘솔 없이 뒤에서 돎)
python cat.py --stop      # 고양이 치우기
python cat.py --toggle    # 떠 있으면 치우고, 없으면 띄움 (cat.bat 이 부르는 것)
python cat.py --scale 3   # 크기 배율 (기본 2)
```

- 클릭은 고양이를 그대로 통과함. 고양이 위를 눌러도 아래 프로그램이 눌림
- 늘 맨 위에 있고, 작업 표시줄에 안 뜨고, 포커스를 뺏지 않음
- 고양이는 하나만 뜸. PID 는 `%TEMP%\cursor-playground-cat.pid` 에 둠

### 동작

| 상태 | 언제 |
|---|---|
| 걷기 | 고양이가 설 자리(커서 오른쪽 아래)에서 30px 넘게 떨어졌을 때 |
| 앉기 | 그 자리에 도착했을 때. 꼬리를 까딱임 |
| 자기 | 커서가 4초 동안 안 움직였을 때. z 가 떠오름 |
| 깨기 | 자는 동안 커서가 60px 넘게 움직였을 때 |

숫자는 [cat.py](cat.py) 맨 위 상수(`WALK_SPEED`, `NEAR`, `SLEEP_AFTER`, `WAKE_DISTANCE`)로 바꿈.

### 그림

[art/walk.txt](art/walk.txt)(4프레임), [art/sit.txt](art/sit.txt)(2프레임), [art/sleep.txt](art/sleep.txt)(3프레임)은 [win-cursor](../win-cursor/README.md#그림-그리는-법)와 같은 텍스트 픽셀아트 형식. 한 글자 = 한 픽셀, `color X RRGGBB` 줄, 프레임 시간은 `rate N`(1/60초 단위), 프레임 사이는 `frame` 줄.
고양이는 오른쪽을 보게 그리면 왼쪽은 자동으로 뒤집힘. 창 투명을 색 키로 처리해서 반투명 색은 못 씀.

### 동작 방식

- 테두리 없는 tkinter 창에 투명으로 뺄 색을 정하고 늘 맨 위에 둠
- `SetWindowLongW` 로 `WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE` 를 켜서 클릭 통과, 작업 표시줄 숨김, 포커스 안 뺏음
- 배율 높은 화면에서 픽셀이 흐려지지 않게 DPI 인식을 켬
- 30ms 마다 커서 위치를 읽어 창을 옮기고 프레임을 고름

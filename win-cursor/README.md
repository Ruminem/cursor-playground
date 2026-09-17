# win-cursor

그림을 윈도우 커서 파일(.cur)로 만들어 실제 마우스 포인터로 쓰는 실험.
표준 라이브러리만 씀 (Python 3.10+).

## 만들기

```sh
python make_cur.py art/arrow.txt out/arrow.cur
python make_cur.py art/heart.txt out/heart.cur --hotspot 5,4
python make_cur.py 내그림.png out/mine.cur --hotspot 0,0
```

- `--hotspot x,y`: 실제로 클릭되는 픽셀. 화살표는 끝 `0,0`, 하트는 가운데쯤.
- `--png 경로`: txt에서 만든 중간 PNG도 저장함. 모양 확인용.

## 그림 그리는 법

`art/*.txt` 에 한 글자 = 한 픽셀로 그림. 32x32보다 작으면 오른쪽·아래가 투명으로 채워짐.

| 글자 | 색 |
|---|---|
| `.` | 투명 |
| `#` | 검정 |
| `o` | 흰색 |
| `r` `g` `b` `y` `p` | 빨강 초록 파랑 노랑 분홍 |

PNG로 그려도 됨. 투명 배경, 256x256 이하.

## 구성표로 등록

`install.ps1` 이 `art/` 그림으로 커서를 만들어 `%LOCALAPPDATA%\cursor-playground\pink` 에 복사하고
포인터 구성표 **cursor-playground 분홍** 으로 등록함. 관리자 권한 필요 없음.

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1             # 등록
powershell -ExecutionPolicy Bypass -File install.ps1 -Uninstall  # 제거
```

등록 뒤 포인터 설정의 **구성표** 목록에서 고르고 확인. 채운 칸은 6개, 나머지는 윈도우 기본.

| 칸 | 그림 |
|---|---|
| 일반 선택 | `arrow-pink` |
| 텍스트 선택 | `ibeam` |
| 사용 중 | `wait` |
| 사용할 수 없음 | `no` |
| 이동 | `move` |
| 링크 선택 | `heart` |

칸 배정과 핫스팟은 `install.ps1` 의 `$roles` 에서 바꿈. 구성표는 레지스트리
`HKCU\Control Panel\Cursors\Schemes` 에 값 하나로 저장되고, 17칸 경로를 정해진 순서로 쉼표로 이은 형식임.
install.ps1 은 한글 때문에 UTF-8 BOM 으로 저장해야 함 (Windows PowerShell 5.1 은 BOM 없으면 ANSI 로 읽음).

## 파일 하나만 적용

1. 설정 → Bluetooth 및 장치 → 마우스 → 추가 마우스 설정 → **포인터** 탭
2. "일반 선택" 선택 → **찾아보기** → `out/*.cur` 고르기 → 확인
3. 되돌리려면 같은 창에서 **기본값 사용**

.cur 파일을 옮기거나 지우면 기본 커서로 돌아가니, 오래 쓸 거면 안 지울 곳에 복사해 두고 지정함.

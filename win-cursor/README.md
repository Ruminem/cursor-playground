# win-cursor

텍스트 픽셀아트로 윈도우 커서(.cur)를 그리고 포인터 구성표로 등록하는 실험.
표준 라이브러리만 씀 (Python 3.10+).

## 구성표 5종

| 폴더 | 등록 이름 | 스타일 |
|---|---|---|
| `art/pink` | cursor-playground 분홍 | 검은 외곽선에 분홍 채우기 |
| `art/neon` | cursor-playground 네온 | 속 빈 어두운 몸체, 청록·자홍 선, 반투명 번짐 |
| `art/minimal` | cursor-playground 미니멀 | 절반 크기 검정 실루엣, 흰 테두리 |
| `art/onebit` | cursor-playground 1비트 | 흑백, 디더링 음영, 딱딱한 그림자, 손가락 링크 |
| `art/fantasy` | cursor-playground 판타지 | 칼, 나무 모래시계, 방패, 나침반, 마법 지팡이 |

구성표마다 채운 칸은 여섯 개, 나머지 11칸은 윈도우 기본 커서.

| 파일 | 칸 |
|---|---|
| `arrow.txt` | 일반 선택 |
| `ibeam.txt` | 텍스트 선택 |
| `wait.txt` | 사용 중 |
| `no.txt` | 사용할 수 없음 |
| `move.txt` | 이동 |
| `hand.txt` | 링크 선택 |

## 등록

**[cursors.bat](cursors.bat)** 을 더블클릭하면 메뉴가 뜸. Python 3.10+ 필요.

```
  cursor-playground 커서 구성표
  1) 전체 등록   2) 전체 제거
  3) 개별 등록   4) 개별 제거
  5) 현재 상태   0) 끝내기
```

개별 등록·제거는 번호를 `1,3` 처럼 여러 개 고를 수 있음. 현재 상태는 구성표별 등록 여부, 커서 파일 수, 지금 적용 중인 구성표를 보여 줌.

메뉴 없이 바로 실행할 때는 인자를 붙임:

```bat
cursors.bat -Install                    :: 전체 등록
cursors.bat -Install -Scheme neon,pink  :: 개별 등록
cursors.bat -Uninstall                  :: 전체 제거
cursors.bat -Uninstall -Scheme neon     :: 개별 제거
cursors.bat -Status                     :: 현재 상태
```

커서를 `%LOCALAPPDATA%\cursor-playground\<폴더>` 에 만들어 두고 구성표로 등록함. 관리자 권한 필요 없음.
등록 뒤 설정 → Bluetooth 및 장치 → 마우스 → 추가 마우스 설정 → **포인터** 탭 → **구성표** 에서 고르고 확인.

- 새 구성표: `art/` 에 폴더를 만들고 `install.ps1` 의 `$schemes` 에 한 줄 추가
- 구성표는 레지스트리 `HKCU\Control Panel\Cursors\Schemes` 에 값 하나로 저장되고, 17칸 경로를 정해진 순서로 쉼표로 이은 형식임
- 실제 동작은 [install.ps1](install.ps1) 에 있고, cursors.bat 은 그걸 실행만 함
- install.ps1 은 한글 때문에 UTF-8 BOM 으로 저장해야 함 (Windows PowerShell 5.1 은 BOM 없으면 ANSI 로 읽음). cursors.bat 은 반대로 영문만 씀 (cmd 는 .bat 을 콘솔 코드페이지로 읽음)

## 그림 그리는 법

한 글자 = 한 픽셀. 첫 줄에 `hotspot x,y` 로 클릭 지점을 적음. 32x32보다 작으면 오른쪽·아래가 투명으로 채워짐.

```
hotspot 5,4
.###...###.
#ppp#.#ppp#
#ooppppppp#
```

| 글자 | 색 | 글자 | 색 |
|---|---|---|---|
| `.` | 투명 | `k` | 거의 검정 |
| `#` | 검정 | `d` | 어두운 회색 |
| `o` | 흰색 | `s` | 은색 |
| `r` `g` `b` | 빨강 초록 파랑 | `Y` | 금색 |
| `y` `p` | 노랑 분홍 | `n` `N` | 나무, 어두운 나무 |
| `c` `m` | 네온 청록, 자홍 | `R` | 진홍 |
| `C` `M` | 청록, 자홍 번짐 (반투명) | `:` | 그림자 (반투명) |

파일 하나만 변환:

```sh
python make_cur.py art/pink/hand.txt out/hand.cur          # 핫스팟은 txt 에서 읽음
python make_cur.py 내그림.png out/mine.cur --hotspot 0,0    # PNG (투명 배경, 256x256 이하)
```

## 파일 하나만 적용

1. 포인터 탭에서 칸 하나(예: 일반 선택) 선택 → **찾아보기** → .cur 고르기 → 확인
2. 되돌리려면 같은 창에서 **기본값 사용**

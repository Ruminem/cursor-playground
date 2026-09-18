# cursor-playground

윈도우 커서 구성표를 만들어 시안 페이지에서 바로 적용하게 하는 취미 프로젝트. 그리고 곁다리로
커서를 따라다니는 고양이. 파이썬은 표준 라이브러리만 쓴다 (의존성 없음).

## 어디에 뭐가 있나

### win-cursor — 본체
| 파일 | 하는 일 |
|---|---|
| `schemes.json` | 구성표 121종 목록. `build.py`·`install.ps1`·`handler.ps1` 이 다 같은 파일을 읽는다 |
| `shapes.json` | 커서 모양 목록. **첫 번째가 기본**(테마 그림 그대로), 나머지는 `smooth.py` 가 그린다 |
| `art/<구성표>/<칸>.txt` | 픽셀 그림 원본. 글자 한 자 = 한 칸, 머리에 `hotspot`/`color`/`rate` 줄 |
| `build.py` | 전부를 다시 만드는 입구. `python build.py` 하나로 `preview.html`·`win-cursor/dist/`·`win-cursor/data/`·README 표까지 |
| `smooth.py` | 거리함수로 매끈한 모양을 그리고(`stencil`) 테마 색을 자리대로 떠 넣는다(`paint`) |
| `make_cur.py` | `.txt` → PNG → `.cur`/`.ani` 변환만 담당. 그림을 해석하는 곳 |
| `shape.py` | `.txt` 읽고 쓰기, 글리프 자리 옮기기 |
| `preview.tpl.html` | 시안 페이지 틀. `build.py` 가 여기에 데이터를 끼워 `preview.html` 을 뱉는다 |
| `handler.ps1` | `cursor-playground://` 주소를 받아 실제로 커서를 적용/되돌림. 받는 주소 목록은 파일 머리에 |
| `install.ps1` / `setup.ps1` | 주소 연결 등록과 설치 |

### cat-follower
`cat.py` (tkinter, `Cat` 클래스가 전부) + `art/*.txt` 그림. 본체와 아무 관계 없다.

## 고칠 때 순서
- 그림·구성표·모양을 고쳤으면 **`win-cursor` 에서 `python build.py` 를 돌린다.**
  `dist/`·`data/`·`preview.html` 은 **커밋하지 않는다**(`.gitignore`) — 커밋마다 저장소가 수십 MB 씩
  영구히 불어서 뺐다. CI 가 만들어 Pages 에 바로 올린다. `build.py` 가 같이 고치는 `win-cursor/README.md` 표는 커밋한다
- CI(`.github/workflows/check.yml`)가 빌드해서 커서 파일을 윈도우가 읽는지 보고,
  main 이면 그 결과를 GitHub Pages 에 올린다. **Pages 원본은 브랜치가 아니라 GitHub Actions** 여야 한다
- 릴리스는 태그(`v*`)를 밀면 `.github/workflows/release.yml` 이 빌드·zip·릴리스까지 한다.
  본문은 `CHANGELOG.md` 의 그 버전 절을 그대로 쓰므로 **CHANGELOG 를 먼저 쓰고 태그를 민다**
- 전체 빌드는 100~200초(코어 수만큼 프로세스). 산출물은 `dist` 101MB + `data` 36MB.
  재료가 그대로인 구성표는 `win-cursor/.build-stamp.json` 을 보고 건너뛰므로 두 번째부터는
  고친 것만 다시 그린다 (아무것도 안 고쳤으면 1초, 구성표 하나면 17초). 전부 다시 그리려면 `python build.py --all`
- 파이썬 버전은 3.14 로 맞춘다. PNG 압축(zlib) 결과가 버전마다 달라 올라가는 커서가 러너 환경을 타지 않게

## 읽지 말 것 (생성물)
`win-cursor/preview.html`(2.8MB), `win-cursor/dist/`, `win-cursor/data/`, `win-cursor/out/`, `win-cursor/.build-stamp.json`, `win-cursor/README.md` 의 구성표 표.
전부 `build.py` 가 만든다. 궁금한 게 있으면 원본(`win-cursor/art/`, `*.json`, `win-cursor/preview.tpl.html`)을 본다.

## 이 저장소의 관례
- 주석·커밋 메시지·문서는 한국어. 소스 머리에 `// SPDX-License-Identifier: Apache-2.0`
- `handler.ps1` 은 한글 때문에 **UTF-8 BOM** 으로 저장해야 한다 (PowerShell 5.1 이 BOM 없으면 ANSI 로 읽음)
- 워크플로에서 한글을 찍는 스텝은 `shell: pwsh`, 파이썬은 `PYTHONUTF8: '1'`
- 세션을 마치면 `NEXT.md` 세 줄(여기까지 됨 / 다음 할 것 / 막힌 것)을 고친다

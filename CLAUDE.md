# cursor-playground

윈도우 커서 구성표를 만들어 시안 페이지에서 바로 적용하게 하는 취미 프로젝트. 그리고 곁다리로
커서를 따라다니는 고양이. 파이썬은 표준 라이브러리만 쓴다 (의존성 없음).

## 어디에 뭐가 있나

### win-cursor — 본체
| 파일 | 하는 일 |
|---|---|
| `schemes.json` | 구성표 57종 목록. `build.py`·`install.ps1`·`handler.ps1` 이 다 같은 파일을 읽는다 |
| `shapes.json` | 커서 모양 목록. **첫 번째가 기본**(테마 그림 그대로), 나머지는 `smooth.py` 가 그린다 |
| `art/<구성표>/<칸>.txt` | 픽셀 그림 원본. 글자 한 자 = 한 칸, 머리에 `hotspot`/`color`/`rate` 줄 |
| `build.py` | 전부를 다시 만드는 입구. `python build.py` 하나로 `preview.html`·`win-cursor/dist/`·`win-cursor/data/`·README 표까지 |
| `smooth.py` | 거리함수로 매끈한 모양을 그리고(`stencil`) 테마 색을 자리대로 떠 넣는다(`paint`) |
| `make_cur.py` | `.txt` → PNG → `.cur`/`.ani` 변환만 담당. 그림을 해석하는 곳 |
| `shape.py` | `.txt` 읽고 쓰기, 글리프 자리 옮기기 |
| `sheet.py` | 모양 × 구성표(또는 프레임)를 PNG 한 장에 그려 눈으로 견주는 도구. 빌드 없이 3초. 빌드 해시에 안 들어가서 고쳐도 다시 그리지 않는다 |
| `preview.tpl.html` | 시안 페이지 틀. `build.py` 가 여기에 데이터를 끼워 `preview.html` 을 뱉는다 |
| `handler.ps1` | `cursor-playground://` 주소를 받아 실제로 커서를 적용/되돌림. 받는 주소 목록은 파일 머리에 |
| `install.ps1` / `setup.ps1` | 주소 연결 등록과 설치 |

### cat-follower
`cat.py` (tkinter, `Cat` 클래스가 전부) + `art/*.txt` 그림. 본체와 아무 관계 없다.

## 고칠 때 순서
- **그림이 어떻게 나오는지는 빌드 전에 `python sheet.py <모양들> <구성표들>` 로 본다** (`--frames` 는 움직임,
  `all` 은 전부). 나온 PNG 를 Read 로 연다. 그려서 재 보는 임시 스크립트를 새로 짜지 않는다 — 모자라면
  `sheet.py` 에 옵션을 더한다. 2026-09-19 에 세어 보니 그런 스크립트를 39번 다시 짰고 출력 5만 자가 거기로 갔다
- 그림·구성표·모양을 고쳤으면 **`win-cursor` 에서 `python build.py` 를 돌린다.**
  `dist/`·`data/`·`preview.html` 은 **커밋하지 않는다**(`.gitignore`) — 커밋마다 저장소가 수십 MB 씩
  영구히 불어서 뺐다. CI 가 만들어 Pages 에 바로 올린다. `build.py` 가 같이 고치는 `win-cursor/README.md` 표는 커밋한다
- CI(`.github/workflows/check.yml`)가 빌드해서 커서 파일을 윈도우가 읽는지 보고,
  main 이면 그 결과를 GitHub Pages 에 올린다. **Pages 원본은 브랜치가 아니라 GitHub Actions** 여야 한다
- **이 저장소에서 "올렸다 · 반영했다 · 릴리스했다"는 Pages 에 실제로 실린 것을 본 때다.**
  커밋도 푸시도 CI 성공도 아니다 — 시안 페이지가 사람이 쓰는 물건이라 거기 안 실렸으면 아무것도 안 바뀐 것이다.
  확인은 https://ruminem.github.io/cursor-playground/win-cursor/preview.html 를 받아 이번에 바뀐 내용이
  들어 있는지 본다. **루트 URL 이 404 인 것은 정상이다** — 워크플로가 저장소 루트를 통째로 올려서 페이지가
  `/win-cursor/` 아래에 산다. 2026-09-19 이걸 모르고 배포가 깨졌다고 보고했다
- **시안 페이지 제목 오른쪽에는 버전과 커밋 7자가 늘 박혀 있어야 한다** — `v1.2.0 · f0cca36` 꼴.
  `build.py` 의 `version()` 이 `CHANGELOG.md` 맨 위 절과 `git rev-parse` 에서 뽑아 `preview.tpl.html` 의
  `<!--VERSION-->` 자리에 끼운다. 위의 Pages 확인이 여기에 기댄다 — 이게 있어야 지금 보고 있는 페이지가
  방금 민 커밋으로 만든 것인지 새로고침 한 번으로 갈린다. 버전 표시는 페이지 해시에도 들어가서
  그림이 그대로여도 커밋이 바뀌면 `preview.html` 을 다시 만든다. 형식이 깨지면 `test_stamp.py` 가 실패한다
- 릴리스는 태그(`v*`)를 밀면 `.github/workflows/release.yml` 이 빌드·zip·릴리스까지 한다.
  본문은 `CHANGELOG.md` 의 그 버전 절을 그대로 쓰므로 **CHANGELOG 를 먼저 쓰고 태그를 민다**
- 전체 빌드는 147–161초 — 커서 6,099개(57종 × 107칸 = 기본 17 + 매끈한 모양 10가지 × 9, 각각 3크기),
  코어 수만큼 프로세스, 2026-09-20 점검 (121종이던 때는 224–268초였고 그중 146초가 순수 규모였다.
  57종에서 순수 규모는 그 값을 비례로 줄인 어림 70초 — 따로 재지는 않았다). 산출물은 `dist` 121MB + `data` 45MB.
  매끈한 모양의 스텐실 160벌은 테마와 무관해서 `win-cursor/.stencils.pkl` 에 먼저 구워 워커들이 나눠 쓴다.
  재료가 그대로인 구성표는 `win-cursor/.build-stamp.json` 을 보고 건너뛰므로 두 번째부터는
  고친 것만 다시 그린다 (아무것도 안 고쳤으면 0.1초, 구성표 하나면 12초). 전부 다시 그리려면 `python build.py --all`
- CI 도 `dist`·`data`·`.build-stamp.json`·`.stencils.pkl` 을 캐시해 같은 수를 쓴다 — 히트면 잡 51초(빌드 8초),
  미스면 12분 (2026-09-19 실측, 121종 때). **캐시는 브랜치마다 따로 저장되고**, 다른 브랜치가 받아 쓸 수 있는 것은
  main 이 저장한 것뿐이다. 그래서 브랜치를 새로 딴 직후 한 번은 12분이 걸릴 수 있다 — 고장이 아니다.
  캐시 키는 `win-cursor` 의 `art/**`·`*.py`·`*.json`·`preview.tpl.html` 이라 문서만 고치면 히트한다
- 파이썬 버전은 3.14 로 맞춘다. PNG 압축(zlib) 결과가 버전마다 달라 올라가는 커서가 러너 환경을 타지 않게

## 읽지 말 것 (생성물)
`win-cursor/preview.html`(2.8MB), `win-cursor/dist/`, `win-cursor/data/`, `win-cursor/out/`, `win-cursor/.build-stamp.json`, `win-cursor/.stencils.pkl`, `win-cursor/README.md` 의 구성표 표.
전부 `build.py` 가 만든다. 궁금한 게 있으면 원본(`win-cursor/art/`, `*.json`, `win-cursor/preview.tpl.html`)을 본다.

## 이 저장소의 관례
- 주석·커밋 메시지·문서는 한국어. 소스 머리에 `// SPDX-License-Identifier: Apache-2.0`
- `handler.ps1` 은 한글 때문에 **UTF-8 BOM** 으로 저장해야 한다 (PowerShell 5.1 이 BOM 없으면 ANSI 로 읽음)
- 워크플로에서 한글을 찍는 스텝은 `shell: pwsh`, 파이썬은 `PYTHONUTF8: '1'`
- 세션을 마치면 `NEXT.md` 세 줄(여기까지 됨 / 다음 할 것 / 막힌 것)을 고친다

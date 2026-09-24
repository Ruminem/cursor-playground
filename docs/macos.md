# macOS 로 옮기면 얼마나 빡센가 (조사, 2026-09-24)

윈도우 구성표 57종을 맥에서도 쓰게 하려면 무엇이 되고 무엇이 안 되는지 조사한 기록. 코드는 아직 한 줄도 안 바꿨다.
리눅스 컨테이너에서 조사해서 **맥에서 직접 확인한 것은 하나도 없다** — 맨 아래 "맥에서 확인할 것" 참고.
**[확인]** 은 소스·문서를 직접 읽은 것, **[추정]** 은 근거로 짐작한 것이다.

## 한 줄 결론

공식 길은 없다. 비공개 API 를 쓰는 **Mousecape 가 사실상 유일한 길**이고, 우리가 할 만한 일은
**구성표를 `.cape` 파일로 내보내는 것까지**다. 맥용 적용기(`handler.ps1` 자리)를 직접 만드는 것은 권하지 않는다.
움직이는 구성표 20종 중 16종은 맥에서 **24장으로 줄여야** 해서 원래만큼 부드럽지 않다.

## 1. 시스템 커서를 바꾸는 길

| 길 | 되나 | 근거 |
|---|---|---|
| 공식: 설정 › 손쉬운 사용 › 디스플레이 › 포인터 | 크기, 테두리 색, 채움 색만 바꾼다. 그림은 못 바꾼다 | [확인] Apple 지원 문서 [Make the pointer easier to see on Mac](https://support.apple.com/en-al/guide/mac-help/mchlp2920/mac) (Monterey 부터) |
| 공식: `NSCursor` | 그 앱의 창 안에서만 바뀐다. 시스템 전체는 못 바꾼다 | [추정] AppKit 의 일반적인 동작. [NSCursor 문서](https://developer.apple.com/documentation/appkit/nscursor)는 이번에 본문을 못 읽었다 |
| 비공개: `CGSRegisterCursorWithImages` (CoreGraphics/SkyLight) | 된다. 시스템 커서 이름(`com.apple.coregraphics.Arrow`, `com.apple.cursor.13` …)에 새 그림을 등록한다 | [확인] Mousecape 소스 `mousecloak/apply.m`, `CGSInternal/CGSCursor.h` |
| SIP 끄기, 시스템 파일 바꾸기 | 필요 없다 | [확인] Mousecape 는 사용자 권한으로 WindowServer 에 등록만 하고, 로그인할 때마다 다시 등록하는 헬퍼를 띄운다 ([README](https://github.com/alexzielenski/Mousecape)). SIP 얘기는 코드와 문서 어디에도 없다 |

### Mousecape 의 지금 상태
- **원본** [alexzielenski/Mousecape](https://github.com/alexzielenski/Mousecape): 마지막 커밋 2024-07-16, 버전 1813. macOS 26(Tahoe) 대응 코드는 없다 [확인].
  라이선스가 "상업 목적 금지" 조건이 붙은 BSD 변형이다.
- **이어받은 판** [sdmj76/Mousecape-swiftUI](https://github.com/sdmj76/Mousecape-swiftUI): v1.2.0 (2026-08-21), macOS 14 이상,
  README 에 "Compatible with macOS 27" [확인]. macOS 26 에서 화살표 커서의 이름이 바뀌어서 런타임에 시스템 커서 이름을 훑어
  `arrow` 가 들어간 이름에 모두 등록하는 코드가 있다(`MCArrowSynonyms`, `MCDefs.m`) [확인].
  이 판의 라이선스는 **재배포 금지**라서 우리가 앱을 묶어 나눠 줄 수 없다 [확인, README 끝의 License Notice].
  서명·공증 여부는 릴리스 노트에 없다 [확인 못 함].
- 알려진 문제 [확인, 위 README Troubleshooting]:
  - 포인터 색을 기본(흰 테두리·검은 채움)에서 바꿔 두면 전체에 안 먹고 Mousecape 창·Dock 에서만 바뀐다 → 색 초기화가 필요
  - 터미널·엑셀처럼 제 커서를 따로 쓰는 앱에서는 안 바뀐다
  - 원본은 재부팅 뒤 유지가 안 된다는 이슈가 있다 ([#278](https://github.com/alexzielenski/Mousecape/issues/278))
- 비공개 API 라서 **macOS 큰 버전마다 깨질 수 있다** [추정 — 26 에서 화살표 이름이 바뀐 것이 그 예].

## 2. 움직이는 커서

- 된다 [확인]. 한 커서에 **프레임 수(`FrameCount`)와 프레임 길이(`FrameDuration`, 초) 하나**. 프레임을 세로로 쌓은 한 장 그림을 준다.
- **최대 24장** — Mousecape-swiftUI 가 `MCMaxFrameCount = 24` 로 막고, 넘으면 장을 솎고 길이를 늘려 한 바퀴 시간을 지킨다.
  주석에 "CGSRegisterCursorWithImages only accepts up to 24" 라고 적혀 있다 [확인, `MCDefs.m`·`backup.m`·`create.m`].
  원본 Mousecape 도 `frameCount > 24` 면 거절한다 [확인, `apply.m`]. 다만 같은 저장소의 macOS 26 기본 커서 덤프
  (`Example/Default_macOS 26.cape`)에서 Wait(무지개 공)는 **30장 × 1/60초**였다 — 시스템은 24장을 넘겨 쓴다.
  비공개 API 가 정말 24장에서 막는지는 **맥에서 재 봐야 한다** [추정].
- **프레임마다 길이를 다르게 줄 수 없다** [확인 — 키가 하나뿐]. 우리 `.ani` 는 `FPS=30` 섞기에서 `[3,2]` 처럼 고르지 않게 쪼갠 rate 를 쓰는데,
  맥에서는 그 길을 못 쓴다. 섞기 전 원래 그림(장마다 rate 가 같다)을 쓰면 된다.
- 우리 쪽 숫자 (원본 그림 기준, 섞기 전): 움직이는 구성표 20종 중 **24장 넘는 것이 16종**.

  | 구성표 | 장 × 틱 | 한 바퀴 | 24장으로 솎으면 |
  |---|---|---|---|
  | 폭죽 | 144 × 1 | 2.4초 | 10fps (6장마다 1장) — 원래 60fps. 제일 크게 망가진다 |
  | 기포·매트릭스·일렁이는 불꽃·글리치 떨림·전구 간판·반짝이는 별·파도 | 48 × 2 | 1.6초 | 15fps |
  | 파문 | 40 × 3 | 2.0초 | 12fps |
  | 네온 맥박·빗줄기·눈 내림 | 36 × 2~4 | 1.2~2.4초 | 20fps·10fps |
  | 전기·스캔 | 32 × 2 | 1.07초 | 22.5fps |
  | 카멜레온 | 30 × 8 | 4.0초 | 6fps (원래 7.5fps, 차이 작음) |
  | 용암·무지개 흐름·회전 / 이발소 기둥·두근두근 | 24 이하 | — | 그대로 |

## 3. 윈도우 17칸 ↔ 맥 커서

맥 쪽 이름은 Mousecape 의 `cursorMap()` (`MCDefs.m`) 기준 [확인]. 한 칸이 맥 이름 여럿을 채운다.

| 윈도우 칸 | 맥 커서 |
|---|---|
| arrow | `coregraphics.Arrow`, `ArrowCtx`, `ArrowS` (+ macOS 26 이름들은 Mousecape 가 알아서) |
| busy (AppStarting) | `cursor.4` Busy |
| wait | `coregraphics.Wait` (무지개 공 자리) |
| hand | `cursor.13` Pointing. 잡는 손 `cursor.12` Open·`cursor.11` Closed 도 이걸로 메우거나 기본으로 둔다 |
| ibeam | `coregraphics.IBeam`, `IBeamXOR`, `IBeamS`. 세로쓰기 `cursor.26` 은 돌려 그려야 한다(없음) |
| ns | `cursor.23` Resize N-S, `cursor.32` Window N-S, 한쪽 화살표 `cursor.21`·`22`·`31`·`36` 도 이걸로 |
| we | `cursor.19`, `cursor.28`, 한쪽 `cursor.17`·`18`·`27`·`38` |
| nwse | `cursor.34`, 모서리 `cursor.33`·`35` |
| nesw | `cursor.30`, 모서리 `cursor.29`·`37` |
| move | `coregraphics.Move`, `cursor.39` Resize Square |
| no | `cursor.3` Forbidden |
| help | `cursor.40` Help |
| cross | `cursor.7`, `cursor.8` Crosshair |
| **up · pen · pin · person** | **맥에 자리가 없다** — 버린다 |

**맥에만 있고 우리 그림이 없는 것**: Alias·Copy(화살표+배지), Copy Drag(`5`), Ctx Menu(`24`), Poof(`25`), Camera(`9`·`10`),
Counting(`14`~`16`), Cell(`20`·`41`), Zoom In/Out(`42`·`43`). 비워 두면 맥 기본 그림이 나와서 **모양이 섞인다**.
화살표에 작은 배지를 얹는 식으로 새로 그릴 수는 있지만 칸이 늘어나는 만큼 그림 일이다.

크기: 맥 커서는 **포인트** 단위이고 Mousecape 는 핫스팟을 31.99 까지만 받는다(`MCMaxHotspotValue`) — 32pt 판이 상한이다 [확인].
32pt 판에 1x = 32px, 2x = 64px 그림을 넣으면 되니 **우리 32·64 판을 그대로 쓴다.** 48 판은 쓸 데가 없다.
포인터 크기 슬라이더는 시스템이 확대한다 [추정].

## 4. `.cape` 형식 [확인]

XML/바이너리 plist 하나. 맥 없이 파이썬 표준 라이브러리 `plistlib` 로 만들 수 있다.

```
{ Author, CapeName, CapeVersion, Identifier, HiDPI: true, Cloud: false, MinimumVersion: 2.0, Version: 2.0,
  Cursors: { "com.apple.cursor.13": { FrameCount, FrameDuration(초), HotSpotX, HotSpotY(포인트),
                                      PointsWide, PointsHigh, Representations: [ <PNG 바이트>, ... ] } } }
```

- `Representations` 는 배율마다 한 장(1x, 2x …), 여러 프레임이면 **세로로 쌓은 한 장**.
- 원본 Mousecape 예제(`com.maxrudberg.svanslosbluehazard.cape`)는 **PNG**, swiftUI 판 예제는 HEIC 다.
  swiftUI 판은 "옛 cape 는 저장할 때 새 형식으로 올린다"고 해서 PNG 를 읽는다고 본다 [추정, 맥에서 확인].
- 우리 `make_cur.pixels_to_png` 는 정사각형만 굽는다. 세로로 긴 그림을 굽게 넓히는 일이 필요하다(작다).

크기 어림 (이 컨테이너에서 기본 모양 그림을 PNG 로 구워 합산, 17칸 · 32+64 · 24장 이하):
폭죽 248KiB, 카멜레온 192KiB, 전기 133KiB, 나무(정지) 7KiB. 한 칸이 맥 이름 2~7개로 복제되니 cape 한 벌은 **기본 모양 기준 0.5~1MB**.
매끈한 모양은 테두리가 부드러워 PNG 가 몇 배 크다 [추정]. **57종 × 11모양을 빌드에서 다 구우면 수백 MB** 라 Pages 에 올리기 어렵다
(지금 dist+data 가 이미 330MB 남짓).

## 5. 일의 크기 (어림)

| 일 | 무엇 | 시간 |
|---|---|---|
| ① 맥에서 먼저 재 보기 | 구성표 하나(예: 전기, 기본 모양)를 `.cape` 로 뽑는 작은 스크립트 → 맥에서 Mousecape 로 적용 | 2~3시간 + 맥 앞 30분 |
| ② `.cape` 굽기 | 17칸→맥 이름 표, 24장 솎기(한 바퀴 시간 보존), 세로 스프라이트 PNG, plistlib. PNG 는 `make_cur` 길 재사용 | 6~10시간 |
| ②-갈래 A: 빌드에서 굽기 | `build.py` 일감에 붙이기. 해시·캐시 영향, **모양을 줄이지 않으면 Pages 용량 문제** | + 3~5시간, 빌드 시간 늘어남 |
| ②-갈래 B: 시안 페이지에서 굽기 | 이미 올라가 있는 `dist/` 의 `.cur`/`.ani` 를 브라우저가 받아 PNG 를 꺼내 쌓고 plist 를 짜서 내려받게. 페이지가 이미 `.cur` 를 JS 로 굽고 있어 비슷한 일. **빌드·Pages 용량 0**, 57×11 조합과 색조 돌리기까지 다 된다 | 8~12시간 |
| ③ 적용기 (`handler.ps1` 자리) | **Mousecape 에 맡기면 0시간** — `.cape` 를 두 번 누르면 Mousecape 가 연다. 직접 만들면 Swift/ObjC 로 비공개 API 호출 + 로그인 때 다시 거는 LaunchAgent + `cursor-playground://` 를 받는 .app 번들 + 서명·공증(연 99달러 개발자 계정) + 맥 CI 러너 + 큰 버전마다 수리 | 직접: 30~60시간 이상, 이어서 유지비 |
| ④ 시안 페이지 | 맥으로 열면 "적용" 대신 ".cape 받기 + Mousecape 안내", 빠지는 칸(up·pen·pin·person) 표시 | 2~4시간 |
| ⑤ CI | 갈래 B 면 없음. 갈래 A 면 cape 가 plist 로 읽히는지 검사 한 줄 (맥 러너 불필요 — 적용은 CI 에서 못 본다) | 0~2시간 |

합: **Mousecape 에 기대는 길이면 15~25시간**, 적용기까지 직접 만들면 **50~90시간 + 계속 고칠 일**.

## 6. 권하는 방향

**① 을 먼저 하고, 되면 ②-B(시안 페이지에서 `.cape` 굽기) + ④. 적용기는 만들지 않는다.**

- 맥은 공식 길이 없어서 어떤 적용기든 비공개 API 위에 선다. 그 API 를 들여다보고 맥 버전마다 고쳐 온 사람들이 이미 있으니
  (Mousecape-swiftUI 는 2026-08 에도 갱신) 거기에 기대는 것이 싸다. 우리가 직접 만들면 앱 서명·공증·Gatekeeper 까지
  떠안는데, 이 저장소는 파이썬 표준 라이브러리만 쓰는 취미 프로젝트라 결이 안 맞는다.
- 브라우저에서 굽는 쪽을 고른 이유: 빌드가 이미 무겁고(PC 262초) Pages 에 330MB 남짓이 올라가 있다. `.cape` 는 이미 올라간
  `.cur`/`.ani` 안의 PNG 를 다시 담는 것뿐이라 새로 그릴 것이 없다. 페이지에 `.cur` 를 JS 로 굽는 코드가 이미 있다.
- **① 에서 멈추는 것도 괜찮은 결론이다.** 이 프로젝트의 자랑인 움직이는 구성표 16종이 맥에서는 24장으로 솎여
  (폭죽은 60→10fps) 원래 맛이 안 난다. ① 결과를 눈으로 보고 "이 정도면 안 한다"고 접어도 잃는 것은 2~3시간이다.
- 가장 싼 우회: 사용자가 `dist/` 의 `.cur`/`.ani` 를 Mousecape-swiftUI 의 "Import Windows Cursors" 로 직접 가져오는 것.
  코드 0시간이지만 우리 파일 이름(`busy`, `pin` …)이 어떻게 맞춰지는지, `.ani` 의 고르지 않은 rate 를 어떻게 다루는지는
  모른다 — 그 앱의 변환 코드는 비공개 저장소(`Mousecape-Core`)라 못 읽었다.

## 맥에서 확인할 것

1. Mousecape-swiftUI v1.2.0 이 지금 쓰는 macOS(26.x)에서 설치되는지, Gatekeeper 가 막는지
2. 우리가 만든 `.cape` (PNG 표현)를 읽고 적용하는지, 재부팅 뒤에도 남는지
3. 화살표가 메뉴 막대·Dock·Finder·브라우저 어디서나 바뀌는지 (26 의 화살표 이름 문제)
4. **24장 넘는 cape 를 넣으면 실제로 거절되는지** — 원본 Mousecape 로는 거절되니 swiftUI 판 없이 확인하려면 작은 CLI 가 필요할 수 있다
5. `FrameDuration` 1/60초(폭죽 원본)나 1/30초가 실제로 그 빠르기로 도는지
6. 포인터 크기 슬라이더를 키웠을 때 64px(2x) 그림으로 충분히 선명한지
7. 우리 픽셀아트가 2x 에서 뭉개지지 않는지 (최근접 확대로 64px 을 넣으면 괜찮을 것)
8. `dist/` 의 `.cur`/`.ani` 를 "Import Windows Cursors" 로 넣었을 때 칸이 어떻게 맞춰지는지 (가장 싼 우회가 쓸 만한지)

## 출처
- [alexzielenski/Mousecape](https://github.com/alexzielenski/Mousecape) — README, `mousecloak/apply.m`, `MCDefs.m`, `CGSInternal/CGSCursor.h`, 예제 cape (2024-07-16 커밋)
- [sdmj76/Mousecape-swiftUI](https://github.com/sdmj76/Mousecape-swiftUI) — README(제한·문제 해결·라이선스), `RELEASE_NOTES.md`, `mousecloak/MCDefs.m`·`apply.m`·`backup.m`·`create.m`, `Example/*.cape` (2026-08-21 v1.2.0)
- [Mousecape 이슈 #273](https://github.com/alexzielenski/Mousecape/issues/273), [#278](https://github.com/alexzielenski/Mousecape/issues/278)
- [Apple: Make the pointer easier to see on Mac](https://support.apple.com/en-al/guide/mac-help/mchlp2920/mac) (컨테이너에서 support.apple.com 이 막혀 검색 요약으로만 봤다)

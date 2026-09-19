# Changelog

## 1.3.0 — 2026-09-19

- Smooth shapes have volume now. The body is read as a dome, so it is lit from the upper left, the ridge along the top catches a highlight, and a contact shadow sits under the lower right edge
- Colours are lifted from the scheme's art by region instead of by square. Neighbouring squares that are close in colour are merged into one region and blended only within it, so the boundary follows a curve rather than the grid: Chrome reads as one continuous sheet of metal, Ocean's highlights are round dots, and the leopard's spots are organic blotches. Before this, patterns broke into visible squares on the larger sizes
- The preview page prints its version and the 7-character commit next to the title, so you can tell at a glance whether the page you are looking at was built from the latest push
- The **Current setting** bar at the bottom can be edited. Paste an address someone sent you and press **Apply** (or Enter) and the page switches to that scheme, shape, hue and size. The visit number inside the address belongs to the PC it came from, so it is discarded
- For anyone working on the art: `python sheet.py <shapes> <schemes>` draws shapes × schemes into one PNG in about three seconds with no build, `--frames` lays out an animation, and `--set KEEP=40` changes a `smooth.py` constant for that sheet only

**한국어**

- 매끈한 모양에 입체감이 생김. 몸 안쪽을 돔으로 보고 왼쪽 위에서 빛이 드는 명암을 넣고, 위쪽 능선에 광택을, 오른쪽 아래 가장자리 밑에 접지 그림자를 깖
- 구성표 그림의 색을 칸이 아니라 **영역**으로 떠 옴. 색이 가까운 이웃 칸을 한 영역으로 묶고 그 안에서만 섞으므로 색 경계가 격자 대신 곡선으로 남. 크롬은 이어진 금속 한 장으로, 오션의 하이라이트는 동그란 점으로, 표범 무늬는 유기적인 얼룩으로 보임. 전에는 큰 크기에서 무늬가 네모로 쪼개져 보였음
- 시안 페이지 제목 오른쪽에 버전과 커밋 7자가 박힘. 지금 보고 있는 페이지가 최신으로 만든 것인지 한눈에 갈림
- 맨 아래 **지금 설정** 줄을 고쳐 쓸 수 있음. 누가 보내 준 주소를 붙여넣고 **적용**(또는 Enter)을 누르면 그 구성표·모양·색조·크기로 바뀜. 주소 안의 방문 번호는 그 주소를 만든 PC 의 것이라 버리고 씀
- 그림을 직접 고치는 사람용: `python sheet.py <모양들> <구성표들>` 이 빌드 없이 3초 만에 모양 × 구성표를 PNG 한 장으로 그림. `--frames` 는 움직임을 펼치고, `--set KEEP=40` 은 `smooth.py` 상수를 그 판에서만 바꿔 견주게 함

## 1.2.0 — 2026-09-19

- A **My backups** row on the preview page keeps up to 20 combinations — scheme, shape, hue and size — in your browser. Press one to apply that combination again, or export them as a `.json` file and import it on another PC
- A bar fixed to the bottom of the page shows the address for whatever you have picked right now, next to **Copy**, **Restore** and **Apply**. Paste that address into Win+R on any PC that already has the handler installed and it applies the same combination
- Smooth shapes now take the outline colour from the scheme's own art spot by spot, the way the body already did, so a current runs along Electric's border in every slot instead of only Link
- The outward bleed is measured against the part of the art that holds still across frames, and each ring is coloured spot by spot too. An afterimage that only reaches out on one side now survives on a smooth shape: Glitch's red and cyan fringes swing left and right again
- A colour that is just the whole shape shoved to one side is now redrawn as the smooth shape shoved the same way, instead of being smeared into a bleed. Glitch's red and cyan afterimages read as offset copies of the pointer on every shape, the way they do on Classic

**한국어**

- 시안 페이지에 **내 백업** 줄이 생김. 지금 고른 구성표·모양·색조·크기를 묶어 이 브라우저에 최대 20개까지 저장해 두고, 누르면 그 조합으로 다시 적용함. `.json` 으로 내보내고 가져올 수 있어 다른 PC 로 옮길 수 있음
- 화면 맨 아래에 지금 설정의 적용 주소가 늘 보이는 줄이 붙음. **복사**·**원래대로**·**적용** 버튼이 같이 있고, 복사한 주소를 처리 스크립트가 깔린 다른 PC 의 Win+R 에 붙이면 같은 조합이 적용됨
- 매끈한 모양이 외곽선 색도 몸통처럼 구성표 그림에서 자리대로 떠 옴(전에는 대표색 한 개로 뭉갬). 전기는 링크 칸만이 아니라 모든 칸에서 테두리를 따라 전류가 흐름
- 몸 바깥 번짐을 프레임 전부에서 변치 않는 부분 기준으로 재고, 층마다 색도 자리대로 떠 옴. 한쪽으로만 뻗는 잔상이 매끈한 모양에서도 살아남음 — 글리치 떨림의 빨강·청록 잔상이 다시 좌우로 흔들림
- 몸을 통째로 한쪽으로 민 색은 번짐으로 뭉개지 않고, 새 모양을 같은 비율만큼 밀어 다시 그림. 글리치 떨림의 빨강·청록 잔상이 어느 모양에서든 기본 모양처럼 포인터를 옆으로 민 복사본으로 보임

## 1.1.0 — 2026-09-18

- **121 pointer schemes** in 9 groups (up from 60), 20 of them animated. The newest is a neon-blue tube on a black body with a triple glow
- **Eleven cursor shapes** — Classic, which is the scheme's own pixel art, plus ten smooth ones: Round, Outline, Sticker, Wedge, Comet, Needle, Paper plane, Droplet, Neon and Beveled. A tab on the preview page redraws the same scheme in the shape you pick
- The smooth shapes are drawn as curves with anti-aliased edges, and they take the colours from the scheme's own art spot by spot — so a leopard keeps its spots, a neon scheme keeps the glow around it, a rounded hourglass still has yellow sand, a rounded no sign is still red, and an animated scheme still animates. The Link slot keeps the scheme's own art instead of a generic hand
- A smooth cursor is drawn again at each size in the file instead of being enlarged, so it stays clean when you raise the Windows pointer size
- Animated schemes keep animating in the scheme list, not just when selected
- Specks that sit apart from the body keep their effect on a smooth shape too — Lightning still throws sparks, Snowfall still falls, Cherry blossom still drops petals
- The local handler updates itself when the page sends a request it does not know yet, instead of reporting an unknown request

**한국어**

- **포인터 구성표 121종**을 아홉 갈래로 묶음 (60종에서 늘림). 그중 20종은 움직이는 커서. 가장 최근에 넣은 것은 검은 몸체에 파란 형광 관과 세 겹 번짐
- **커서 모양 열한 가지** — 구성표가 그린 픽셀 그림인 기본에, 매끈한 열 가지(둥근·테두리·스티커·둥근 삼각·긴 꼬리·바늘·종이비행기·물방울·네온·입체). 시안 페이지의 탭에서 고른 모양으로 같은 구성표를 다시 그림
- 매끈한 모양은 경계를 매끈하게 그리고, 구성표 그림에서 색을 자리대로 떠 옴 — 그래서 표범은 무늬가 남고, 네온 계열은 바깥 번짐이 남고, 둥근 모래시계에도 노란 모래가 있고, 둥근 금지 표시는 여전히 빨갛고, 움직이는 구성표는 그대로 움직임. 링크 칸은 일반 손 모양 대신 구성표 그림을 그대로 씀
- 매끈한 커서는 파일 안의 크기마다 새로 그림(늘리지 않음). 윈도우 포인터 크기를 키워도 깨끗함
- 움직이는 구성표는 골랐을 때만이 아니라 목록에서도 계속 움직임
- 몸에서 떨어져 나온 조각도 매끈한 모양에서 살아남음 — 전기는 불꽃이 튀고, 눈보라는 눈이 내리고, 벚꽃은 꽃잎이 떨어짐
- 처리 스크립트가 모르는 주소를 받으면 새 파일을 받아 스스로 갈아 끼움 (예전에 설치한 채로도 새 주소가 통함)

## 1.0.0 — 2026-09-18

First release. Windows pointer schemes drawn as text pixel art, plus a cat that follows the cursor.

- **60 pointer schemes** in 8 groups (pixel classics, light and screens, materials, colours and patterns, hand-drawn and minimal, nature and seasons, animated, game items). 10 of them are animated cursors (.ani)
- **All 17 slots filled** per scheme, including Working in background (arrow + hourglass), Help, Precision, Handwriting, the four resize arrows, Alternate, Location and Person
- **Five sizes in every cursor file** (32, 48, 64, 96, 128px), so raising the Windows pointer size keeps the pixels sharp
- **[Preview page](https://ruminem.github.io/cursor-playground/win-cursor/preview.html)**: try every scheme as your browser cursor, recolour it with a hue slider, search and star favourites, pick a random one, draw your own 32x32 cursor and download it as .cur
- **One-line setup** (`irm .../setup.ps1 | iex`) links `cursor-playground://` to a local handler. After that the page can apply a scheme, change the size, set up a daily schedule (a scheme per time of day), open the Windows pointer settings, roll back to the cursor you had before the visit, or remove everything
- **cat-follower**: a pixel cat that walks to your cursor, sits next to it and falls asleep. Clicks pass straight through it
- Everything is Python standard library and Windows built-ins — no dependencies. Apache-2.0

**한국어**

첫 릴리스. 텍스트 픽셀아트로 그린 윈도우 포인터 구성표와, 커서를 따라다니는 고양이.

- **포인터 구성표 60종**을 여덟 갈래로 묶음 (픽셀 클래식, 빛과 화면, 재질, 색과 무늬, 손그림·미니멀, 자연·계절, 움직이는, 게임 아이템). 그중 10종은 움직이는 커서(.ani)
- 구성표마다 **17칸을 모두 채움**. 백그라운드 작업(화살표+모래시계), 도움말, 정밀, 필기, 크기 조정 4종, 대체, 위치, 사용자까지
- 커서 파일 하나에 **다섯 가지 크기**(32·48·64·96·128px)를 담아, 윈도우 포인터 크기를 키워도 픽셀이 뭉개지지 않음
- **[시안 페이지](https://ruminem.github.io/cursor-playground/win-cursor/preview.html)**: 브라우저에서 60종을 커서로 써 보고, 색조 슬라이더로 색을 바꾸고, 이름으로 찾고 즐겨찾기하고, 랜덤으로 고르고, 32x32 격자에 직접 그려 .cur 로 내려받음
- **한 줄 설치**(`irm .../setup.ps1 | iex`)로 `cursor-playground://` 주소를 로컬 처리 스크립트에 연결. 그 뒤로는 페이지에서 적용, 크기 변경, 시간대별 자동 전환, 포인터 설정 열기, 페이지를 열기 전으로 되돌리기, 완전 제거를 버튼으로 함
- **cat-follower**: 커서를 따라 걸어와 옆에 앉고 잠드는 픽셀 고양이. 클릭은 그대로 통과함
- 전부 Python 표준 라이브러리와 윈도우 기본 기능만 씀 — 의존성 없음. Apache-2.0

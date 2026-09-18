# Changelog

## Unreleased

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

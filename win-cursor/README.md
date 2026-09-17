# win-cursor

**English** · [한국어](#korean)

Draw Windows cursors (.cur, and animated .ani) as text pixel art and install them as pointer schemes.
Standard library only (Python 3.10+).

## Apply straight from the web

**[Open the preview page](https://ruminem.github.io/cursor-playground/win-cursor/preview.html)** — try each scheme as your cursor in the browser, then apply it to Windows or roll back with one button.

1. **Once per PC** — paste this into PowerShell (no clone, no Python, no admin rights)
   ```powershell
   irm https://ruminem.github.io/cursor-playground/win-cursor/setup.ps1 | iex
   ```
   [setup.ps1](setup.ps1) downloads [handler.ps1](handler.ps1) to `%LOCALAPPDATA%\cursor-playground`,
   links the `cursor-playground://` address to it, and **backs up your current pointer settings** (where Remove everything goes back to)
2. Pick a scheme on the page, press **이 구성표 적용** (apply this scheme), confirm, then allow the browser to open the app
3. Tired of trying things? Press **원래대로** (undo) to go back to the cursor you had right before the first apply since opening the page
   - Example: apply Neon → close the page → reopen and apply Pink → undo → Neon
   - Closing and reopening the tab starts a new count; reloading the same tab keeps it
4. **포인터 설정 열기** (open pointer settings) opens the Windows Mouse Properties dialog on the Pointers tab
5. **커서 크기** (cursor size: 1×, 1.5×, 2×, 3×, 4×) resizes the page's cursors right away, and the apply button applies the size too. To change only the size, press **크기만 적용** (apply size only)
6. To clean up, press **완전 제거** (remove everything) at the bottom — it restores the cursors from the one-line setup and deletes the address link and the install folder

How it works:

- Cursor files come from [dist/](dist/) on GitHub Pages. `python build.py` makes `preview.html` and `dist/` from `art/`; both have to be committed to reach the web
- Applying writes the 17 slots and the scheme name under `HKCU\Control Panel\Cursors` and reloads them with `SystemParametersInfo(SPI_SETCURSORS)`
- Each cursor file holds 32, 48, 64, 96 and 128px images, so Windows picks a matching one when the size goes up and the pixels stay sharp. The size is set with `SystemParametersInfo(0x2029)`, the call the Settings app uses, and undo restores it
- There are two backups. `backup-initial.json` is the state at setup (for remove everything); `backup-visit.json` is the state right before the first apply after opening the page (for undo)
- Each time the page opens it makes a 16-character visit id, keeps it in `sessionStorage` and sends it with each request. An apply with a new visit id takes a fresh visit backup
- After undo, every scheme except the one in use is removed along with its cursor files
- Any web page can call this address, so only `apply/<a scheme listed in schemes.json>/<visit>[/<size>]`, `size/<size>/<visit>`, `restore/<visit>`, `status`, `settings` and `unlink` are accepted. Any other address or smuggled argument is ignored
- The look lives in [preview.tpl.html](preview.tpl.html). Fonts come from Google Fonts (Silkscreen, IBM Plex Sans KR, IBM Plex Mono — all SIL OFL). The tab icon is the pink arrow drawn in this repository

## Schemes

The list lives in one place, [schemes.json](schemes.json). The build, the local menu and the web handler all read it.
Schemes with `"animated": true` are built as animated cursors (.ani). The tables below are filled in by `python build.py`.

<!-- schemes:en -->
**Pixel classics**

| Folder | Name | Style |
|---|---|---|
| `art/pink` | Pink | Pink fill inside a black outline. Crisp pixels at the default size. |
| `art/onebit` | 1-bit | Two colours only, with dithered shading, a hard drop shadow and a pointing-hand link. |
| `art/ink` | Ink | A black body with a white outline — the usual white arrow turned inside out. |
| `art/sticker` | Sticker | A mint body cut out with a thick white border and a faint shadow. |
| `art/gameboy` | Game Boy | Light and shade drawn with just four greens, like an old handheld screen. |

**Light and screens**

| Folder | Name | Style |
|---|---|---|
| `art/neon` | Neon | Hollow dark body with cyan and magenta tubes and a translucent glow outside. |
| `art/glitch` | Glitch | A white body with red and cyan copies slipping out on either side. |
| `art/crt` | CRT | Green phosphor outline with darker scanlines on every other row. |
| `art/galaxy` | Galaxy | Deep space dotted with stars inside a violet rim. The link is a star. |
| `art/flame` | Flame | Yellow at the bottom turning red towards the top, with sparks along the edge. |
| `art/hologram` | Hologram | Translucent body with diagonal cyan, magenta and yellow sheen and a white outline. |
| `art/laser` | Laser | No body at all — just a red beam and a double glow. |
| `art/glowdark` | Glow in the dark | A pale green body softly glowing like a glow-in-the-dark sticker. |
| `art/thermal` | Thermal | Blue at the edges, turning yellow and red towards the middle like a thermal camera. |
| `art/matrix` | Matrix | Green code rain falling down a black body. |

**Materials**

| Folder | Name | Style |
|---|---|---|
| `art/chrome` | Chrome | Four shades of silver, lit from the top left. |
| `art/gold` | Gold | Gold bevel with two sparkles. The link is a gold star. |
| `art/glass` | Glass | See-through body with a highlight along the edge. |
| `art/ice` | Ice | Sky blue getting colder towards the bottom, with diagonal frost lines. |
| `art/wood` | Wood | Dark rim with wood grain running across. |
| `art/marble` | Marble | White stone with grey veins winding through. |
| `art/stone` | Stone | Grey pebble with light and dark specks. |
| `art/copper` | Copper | Copper bevel with patches of green patina. |
| `art/leather` | Leather | Dark brown leather with a line of stitches just inside the edge. |
| `art/denim` | Denim | Twill denim weave with orange stitching. |
| `art/paper` | Paper | Cream paper with one half shaded as if folded. |

**Colours and patterns**

| Folder | Name | Style |
|---|---|---|
| `art/rainbow` | Rainbow | Six horizontal bands of red, orange, yellow, green, blue and purple. |
| `art/candy` | Candy | Red and white diagonal candy stripes. |
| `art/popart` | Pop art | Red halftone dots on yellow with a double black outline. |
| `art/sunset` | Sunset | A gradient from sunset yellow down to purple. |
| `art/checker` | Checker | Black and white checks inside a red outline. |
| `art/polka` | Polka dot | White polka dots on pink. |
| `art/zebra` | Zebra | Wavy black stripes. |
| `art/leopard` | Leopard | Ring-shaped leopard spots on ochre. |
| `art/watermelon` | Watermelon | Green rind, white inner rind, red flesh and black seeds. |

**Hand-drawn and minimal**

| Folder | Name | Style |
|---|---|---|
| `art/minimal` | Minimal | A thin black silhouette at half size with a white border. The link is a single dot. |
| `art/dashed` | Dashed | Marching-ants border in alternating black and grey around a translucent body. |
| `art/doodle` | Doodle | Wobbly pencil lines with blue crayon hatching. |
| `art/cloud` | Cloud | Pure white body with a pastel outline and a soft double shadow. |
| `art/longshadow` | Long shadow | Flat teal shape casting a long diagonal shadow. |
| `art/crayon` | Crayon | A red crayon line drawn twice, with patchy yellow colouring. |
| `art/blueprint` | Blueprint | White lines on blue grid paper. |
| `art/pencil` | Pencil | Grey pencil outline with cross-hatching inside. |
| `art/watercolor` | Watercolour | Blotchy sky blue, violet and pink paint. |

**Nature and seasons**

| Folder | Name | Style |
|---|---|---|
| `art/sakura` | Cherry blossom | Pale pink body scattered with petals, some drifting outside. |
| `art/forest` | Forest | Dark green moss mixed with brighter leaves. |
| `art/snow` | Snow | Pure white body with snowflakes floating around it. |
| `art/ocean` | Ocean | Bands of blue waves with white foam. |
| `art/desert` | Desert | Sand with the ripples of dunes. |

**Animated**

| Folder | Name | Style |
|---|---|---|
| `art/rainbowflow` | Rainbow flow | Rainbow bands that keep flowing upwards. |
| `art/neonpulse` | Neon pulse | A cyan neon glow that swells and fades like breathing. |
| `art/flicker` | Flickering flame | The flame edge wavers and sparks fly upwards. |
| `art/twinkle` | Twinkling stars | Stars inside a space body switch on and off in turn. |
| `art/jitter` | Glitch jitter | The red and cyan slip shakes, and now and then one row jumps sideways. |

**Game items**

| Folder | Name | Style |
|---|---|---|
| `art/fantasy` | Fantasy | A silver sword, wooden hourglass, shield, compass and magic wand. |

<!-- /schemes:en -->

Every scheme fills all 17 slots. Six are drawn per theme; the other 11 are made from that theme's arrow, hourglass and colours.

| File | Slot | File | Slot |
|---|---|---|---|
| `arrow.txt` | Normal select | `ns.txt` | Vertical resize |
| `help.txt` | Help select | `we.txt` | Horizontal resize |
| `busy.txt` | Working in background | `nwse.txt` | Diagonal resize 1 |
| `wait.txt` | Busy | `nesw.txt` | Diagonal resize 2 |
| `cross.txt` | Precision select | `move.txt` | Move |
| `ibeam.txt` | Text select | `up.txt` | Alternate select |
| `pen.txt` | Handwriting | `hand.txt` | Link select |
| `no.txt` | Unavailable | `pin.txt` | Location select |
|  |  | `person.txt` | Person select |

## Installing from the repository

While editing the art, double-click **[cursors.bat](cursors.bat)** in a clone. Needs Python 3.10+. It only registers schemes; you pick one in the pointer settings. The menu is in Korean.

```
  cursor-playground 커서 구성표
  1) 전체 등록   2) 전체 제거        (register all / remove all)
  3) 개별 등록   4) 개별 제거        (register some / remove some)
  5) 현재 상태   0) 끝내기           (status / quit)
```

```bat
cursors.bat -Install                    :: register all
cursors.bat -Install -Scheme neon,pink  :: register some (comma-separated)
cursors.bat -Uninstall                  :: remove all
cursors.bat -Uninstall -Scheme neon     :: remove some
cursors.bat -Status                     :: status
```

- New scheme: draw all 17 slots in `art/<id>/`, add a line to `schemes.json` → `python build.py` → commit. The web handler does not need reinstalling
- A scheme is stored as one value under `HKCU\Control Panel\Cursors\Schemes`: the 17 slot paths joined with commas in a fixed order
- The .ps1 files must be saved as UTF-8 with BOM because of the Korean text (Windows PowerShell 5.1 reads BOM-less files as ANSI). cursors.bat and setup.ps1 are ASCII only for the opposite reason (cmd and `irm` can pick the wrong code page)

## Drawing

One character is one pixel. The first line `hotspot x,y` is the click point. Art smaller than 32x32 is padded with transparency to the right and bottom.
For more colours, `color X RRGGBB` or `color X RRGGBBAA` defines a character for that file only (Hangul syllables work as characters too).

An animated cursor adds a `rate N` line (how long each frame shows, in 1/60 s) and separates frames with `frame` lines. Two or more frames build an .ani.

```
hotspot 0,0
rate 6
color 0 ff4060
frame
0.
00
frame
.0
00
```

```
hotspot 5,4
.###...###.
#ppp#.#ppp#
#ooppppppp#
```

| Char | Colour | Char | Colour |
|---|---|---|---|
| `.` | transparent | `k` | near black |
| `#` | black | `d` | dark grey |
| `o` | white | `s` | silver |
| `r` `g` `b` | red, green, blue | `Y` | gold |
| `y` `p` | yellow, pink | `n` `N` | wood, dark wood |
| `c` `m` | neon cyan, magenta | `R` | crimson |
| `C` `M` | cyan, magenta glow (translucent) | `:` | shadow (translucent) |

Converting a single file:

```sh
python make_cur.py art/pink/hand.txt out/hand.cur          # hotspot read from the txt
python make_cur.py my-art.png out/mine.cur --hotspot 0,0   # PNG (transparent background, up to 256x256)
```

## Applying a single file

1. On the Pointers tab, select a slot (for example Normal Select) → **Browse** → pick a .cur → OK
2. To undo, press **Use Default** in the same dialog

---

## Korean

[English](#win-cursor) · **한국어**

텍스트 픽셀아트로 윈도우 커서(.cur, 움직이는 .ani)를 그리고 포인터 구성표로 등록하는 실험.
표준 라이브러리만 씀 (Python 3.10+).

### 웹에서 바로 적용

**[시안 페이지 열기](https://ruminem.github.io/cursor-playground/win-cursor/preview.html)** — 구성표를 골라 가며 커서를 만져 보고, 버튼 하나로 윈도우에 적용·원래대로.

1. **처음 한 번** — PowerShell 에 붙여넣기 (클론·Python·관리자 권한 필요 없음)
   ```powershell
   irm https://ruminem.github.io/cursor-playground/win-cursor/setup.ps1 | iex
   ```
   [setup.ps1](setup.ps1) 이 [handler.ps1](handler.ps1) 을 `%LOCALAPPDATA%\cursor-playground` 에 받고,
   `cursor-playground://` 주소를 거기에 연결하고, **지금 포인터 설정을 백업** 함 (완전 제거 때 돌아갈 곳)
2. 페이지에서 구성표를 고르고 **이 구성표 적용** → 확인 → 브라우저의 "앱 열기" 에서 열기
3. 이것저것 적용해 보다 질리면 **원래대로** — 이 페이지를 연 뒤 처음 적용하기 직전 커서로 돌아감
   - 예: 네온 적용 → 페이지 닫음 → 다시 열어 분홍 적용 → 원래대로 → 네온
   - 탭을 닫았다 열면 새로 셈. 같은 탭 새로고침은 이어짐
4. **포인터 설정 열기** — 윈도우 마우스 속성 창을 포인터 탭으로 엶
5. **커서 크기** (기본·1.5배·2배·3배·4배) — 고르면 페이지 커서가 바로 그 크기가 되고, 적용 버튼은 크기까지 같이 적용. 구성표는 두고 크기만 바꾸려면 **크기만 적용**
6. 다 치우려면 페이지 아래 **완전 제거** — 한 줄 설치할 때의 커서로 돌린 뒤 주소 연결과 설치 폴더 삭제

동작 방식:

- 커서 파일은 Pages 의 [dist/](dist/) 에서 받음. `python build.py` 가 `art/` 로 `preview.html` 과 `dist/` 를 같이 만들고, 둘 다 커밋해야 웹에 반영됨
- 적용은 `HKCU\Control Panel\Cursors` 의 17칸과 구성표 이름을 바꾸고 `SystemParametersInfo(SPI_SETCURSORS)` 로 바로 다시 읽힘
- 커서 파일 하나에 32·48·64·96·128px 이미지를 모두 넣어서, 크기를 키워도 윈도우가 맞는 이미지를 골라 픽셀이 뭉개지지 않음. 크기는 설정 앱이 쓰는 `SystemParametersInfo(0x2029)` 로 바꾸고 원래대로 때 같이 되돌림
- 백업은 두 개. `backup-initial.json` 은 한 줄 설치할 때 상태(완전 제거용), `backup-visit.json` 은 페이지를 연 뒤 첫 적용 직전 상태(원래대로용)
- 페이지는 열 때마다 16자리 방문 번호를 만들어 `sessionStorage` 에 두고 요청에 붙임. 새 방문 번호로 적용이 오면 그때 방문 백업을 새로 뜸
- 원래대로 뒤에는 지금 쓰는 구성표를 뺀 나머지 구성표와 커서 파일을 지움
- 아무 웹 페이지나 이 주소를 부를 수 있으므로, 받는 요청은 `apply/<schemes.json 에 있는 구성표>/<방문>[/<크기>]`, `size/<크기>/<방문>`, `restore/<방문>`, `status`, `settings`, `unlink` 뿐. 다른 주소나 끼워 넣은 인자는 전부 무시함
- 모양은 [preview.tpl.html](preview.tpl.html) 에서 고침. 글꼴은 Google Fonts (Silkscreen, IBM Plex Sans KR, IBM Plex Mono — 모두 SIL OFL). 탭 아이콘은 이 저장소에서 그린 분홍 화살표

### 구성표

목록은 [schemes.json](schemes.json) 한 곳에 있음. 빌드, 로컬 메뉴, 웹 처리 스크립트가 모두 이 파일을 읽음.
`"animated": true` 인 구성표는 움직이는 커서(.ani)로 만들어짐. 아래 표는 `python build.py` 가 채움.

<!-- schemes:ko -->
**픽셀 클래식**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/pink` | 분홍 | 검은 외곽선에 분홍 채우기. 기본 크기의 또렷한 픽셀. |
| `art/onebit` | 1비트 | 흑백 두 색에 디더링 음영과 딱딱한 그림자, 손가락 링크. |
| `art/ink` | 잉크 | 검은 몸체에 흰 외곽선. 흔한 흰 화살표를 뒤집은 모양. |
| `art/sticker` | 스티커 | 민트색 몸체를 두꺼운 흰 테두리와 옅은 그림자로 오려 붙인 느낌. |
| `art/gameboy` | 게임보이 | 초록 네 가지 색만으로 빛과 그늘을 넣은 휴대용 게임기 화면풍. |

**빛과 화면**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/neon` | 네온 | 속이 빈 어두운 몸체에 청록·자홍 관, 바깥으로 반투명 번짐. |
| `art/glitch` | 글리치 | 흰 몸체 양옆으로 빨강·청록이 어긋나 번진 화면 오류. |
| `art/crt` | CRT | 초록 형광 외곽선과 한 줄씩 어두운 주사선이 지나가는 옛 모니터. |
| `art/galaxy` | 은하 | 보랏빛 테두리 안에 별이 박힌 짙은 우주. 링크는 별. |
| `art/flame` | 불꽃 | 아래는 노랗고 위로 갈수록 붉어지며 가장자리에 불티가 튐. |
| `art/hologram` | 홀로그램 | 비스듬히 흐르는 청록·자홍·노랑 무지갯빛 반투명 몸체에 흰 선. |
| `art/laser` | 레이저 | 몸체 없이 빨간 빛줄기와 두 겹 번짐만 남긴 선. |
| `art/glowdark` | 야광 | 연둣빛 몸체가 어둠 속에서 은은하게 번지는 야광 스티커. |
| `art/thermal` | 열화상 | 가장자리는 파랗고 안쪽으로 갈수록 노랗고 붉어지는 열화상 카메라. |
| `art/matrix` | 매트릭스 | 검은 몸체 안으로 초록 글자비가 세로로 흘러내림. |

**재질**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/chrome` | 크롬 | 왼쪽 위에서 빛을 받는 네 단계 은빛 금속 입체. |
| `art/gold` | 골드 | 금빛 입체에 반짝이 두 개. 링크는 금별. |
| `art/glass` | 유리 | 뒤가 비치는 반투명 몸체에 가장자리 하이라이트. |
| `art/ice` | 얼음 | 위에서 아래로 차가워지는 하늘색에 비스듬한 서리 결. |
| `art/wood` | 나무 | 짙은 테두리에 가로로 흐르는 나뭇결. |
| `art/marble` | 대리석 | 흰 돌에 회색 결이 물결치듯 지나감. |
| `art/stone` | 돌 | 회색 바탕에 밝고 어두운 얼룩이 박힌 돌멩이. |
| `art/copper` | 구리 | 구릿빛 금속 입체에 청록 녹이 군데군데 슨 모습. |
| `art/leather` | 가죽 | 짙은 갈색 가죽 안쪽을 따라 한 땀씩 박음질. |
| `art/denim` | 데님 | 청바지 능직 결에 주황 스티치. |
| `art/paper` | 종이 | 크림색 종이를 반으로 접은 듯 한쪽에 그늘. |

**색과 무늬**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/rainbow` | 무지개 | 빨주노초파보 여섯 줄 가로 띠. |
| `art/candy` | 캔디 | 빨강·흰색 사선 줄무늬 사탕. |
| `art/popart` | 팝아트 | 노란 바탕에 빨간 망점, 두 겹 굵은 검정 선. |
| `art/sunset` | 석양 | 노을빛 노랑에서 보라로 내려가는 그라데이션. |
| `art/checker` | 체크 | 빨간 테두리 안에 흑백 체크무늬. |
| `art/polka` | 물방울 | 분홍 바탕에 흰 물방울무늬. |
| `art/zebra` | 얼룩말 | 구불구불한 검은 줄무늬. |
| `art/leopard` | 표범 | 황토색 바탕에 고리 모양 표범 무늬. |
| `art/watermelon` | 수박 | 초록 껍질, 흰 속껍질, 빨간 속살에 까만 씨. |

**손그림·미니멀**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/minimal` | 미니멀 | 절반 크기의 가는 검정 실루엣과 흰 테두리. 점 하나짜리 링크. |
| `art/dashed` | 점선 | 흑백이 번갈아 가는 개미 행렬 테두리에 반투명 속. |
| `art/doodle` | 낙서 | 삐뚤빼뚤한 연필 선에 파란 크레용 빗금. |
| `art/cloud` | 구름 | 새하얀 몸체에 파스텔 테두리와 두 겹 흐린 그림자. |
| `art/longshadow` | 롱섀도 | 청록 평면 도형 뒤로 길게 늘어지는 대각선 그림자. |
| `art/crayon` | 크레용 | 빨간 크레용으로 두 번 그은 선에 듬성듬성 칠한 노랑. |
| `art/blueprint` | 청사진 | 파란 모눈종이 위에 흰 선으로 그린 설계도. |
| `art/pencil` | 연필 | 회색 연필 외곽선에 엇갈린 빗금만 친 속. |
| `art/watercolor` | 수채화 | 하늘·보라·분홍이 얼룩덜룩 번지는 물감. |

**자연·계절**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/sakura` | 벚꽃 | 연분홍 몸체에 꽃잎이 박히고 주변으로 흩날림. |
| `art/forest` | 숲 | 짙은 초록 이끼에 밝은 잎이 섞인 숲. |
| `art/snow` | 눈 | 새하얀 몸체 둘레로 눈송이가 떠 있음. |
| `art/ocean` | 바다 | 파란 물결 띠와 하얀 포말. |
| `art/desert` | 사막 | 모래색 바탕에 모래언덕 결. |

**움직이는**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/rainbowflow` | 무지개 흐름 | 빨주노초파보 띠가 위로 쉬지 않고 흘러감. |
| `art/neonpulse` | 네온 맥박 | 청록 네온 번짐이 숨 쉬듯 커졌다 작아짐. |
| `art/flicker` | 일렁이는 불꽃 | 불꽃 경계가 흔들리고 위로 불티가 튐. |
| `art/twinkle` | 반짝이는 별 | 우주 몸체 속 별들이 차례로 켜졌다 꺼짐. |
| `art/jitter` | 글리치 떨림 | 빨강·청록 어긋남이 떨리고 가끔 한 줄이 옆으로 밀림. |

**게임 아이템**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/fantasy` | 판타지 | 은빛 칼, 나무 모래시계, 방패, 나침반, 마법 지팡이. |

<!-- /schemes:ko -->

구성표마다 17칸을 모두 채움. 여섯 칸은 테마마다 그렸고, 나머지 11칸은 그 테마의 화살표·모래시계와 색으로 만듦.

| 파일 | 칸 | 파일 | 칸 |
|---|---|---|---|
| `arrow.txt` | 일반 선택 | `ns.txt` | 세로 크기 조정 |
| `help.txt` | 도움말 선택 | `we.txt` | 가로 크기 조정 |
| `busy.txt` | 백그라운드 작업 | `nwse.txt` | 대각선 크기 조정 1 |
| `wait.txt` | 사용 중 | `nesw.txt` | 대각선 크기 조정 2 |
| `cross.txt` | 정밀 선택 | `move.txt` | 이동 |
| `ibeam.txt` | 텍스트 선택 | `up.txt` | 대체 선택 |
| `pen.txt` | 필기 | `hand.txt` | 링크 선택 |
| `no.txt` | 사용할 수 없음 | `pin.txt` | 위치 선택 |
|  |  | `person.txt` | 사용자 선택 |

### 저장소에서 직접 등록

그림을 고치면서 볼 때는 클론한 폴더의 **[cursors.bat](cursors.bat)** 을 더블클릭. Python 3.10+ 필요. 등록만 하고 적용은 포인터 설정에서 고름.

```
  cursor-playground 커서 구성표
  1) 전체 등록   2) 전체 제거
  3) 개별 등록   4) 개별 제거
  5) 현재 상태   0) 끝내기
```

```bat
cursors.bat -Install                    :: 전체 등록
cursors.bat -Install -Scheme neon,pink  :: 개별 등록 (쉼표로 여러 개)
cursors.bat -Uninstall                  :: 전체 제거
cursors.bat -Uninstall -Scheme neon     :: 개별 제거
cursors.bat -Status                     :: 현재 상태
```

- 새 구성표: `art/<id>/` 에 17칸을 모두 그리고 `schemes.json` 에 한 줄 추가 → `python build.py` → 커밋. 웹 처리 스크립트는 다시 설치할 필요 없음
- 구성표는 레지스트리 `HKCU\Control Panel\Cursors\Schemes` 에 값 하나로 저장되고, 17칸 경로를 정해진 순서로 쉼표로 이은 형식임
- .ps1 은 한글 때문에 UTF-8 BOM 으로 저장해야 함 (Windows PowerShell 5.1 은 BOM 없으면 ANSI 로 읽음). 반대로 cursors.bat 과 setup.ps1 은 영문만 씀 (cmd 와 `irm` 이 코드페이지를 잘못 고를 수 있음)

### 그림 그리는 법

한 글자 = 한 픽셀. 첫 줄에 `hotspot x,y` 로 클릭 지점을 적음. 32x32보다 작으면 오른쪽·아래가 투명으로 채워짐.
색이 더 필요하면 `color X RRGGBB` 또는 `color X RRGGBBAA` 줄로 그 파일에서만 쓰는 글자를 정의함 (한글 음절도 글자로 쓸 수 있음).

움직이는 커서는 `rate N`(프레임 하나 보여 줄 시간, 1/60초 단위) 줄을 넣고 `frame` 줄로 프레임을 나눔. 프레임이 둘 이상이면 .ani 로 만들어짐.

```
hotspot 0,0
rate 6
color 0 ff4060
frame
0.
00
frame
.0
00
```

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

### 파일 하나만 적용

1. 포인터 탭에서 칸 하나(예: 일반 선택) 선택 → **찾아보기** → .cur 고르기 → 확인
2. 되돌리려면 같은 창에서 **기본값 사용**

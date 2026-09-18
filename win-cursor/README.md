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
   - **색조** (hue) turns the colour wheel from 0° to 355°. Black, white and grey stay as they are. The page's cursors and cards change right away, and applying makes a new scheme in that colour, such as `cursor-playground 네온 색조120` (Neon, hue 120)
6. **시간대별 자동 전환** (daily schedule): set a scheme per time of day and press **켜기** (on). The handler registers one daily task per row in the Windows Task Scheduler — no admin rights — and **끄기** (off) removes them
7. Find a scheme by name with the search box, star the ones you like and tick **즐겨찾기만** (favourites only), or press **랜덤 적용** (apply a random one) to get a random scheme with a random hue
8. **내 커서 그리기** (draw your own) at the bottom of the page: paint on a 32x32 grid, set the click point, see it as the page's cursor and download it as a .cur with all five sizes. The drawing stays in the browser
9. To clean up, press **완전 제거** (remove everything) at the bottom — it restores the cursors from the one-line setup and deletes the address link and the install folder

How it works:

- Cursor files come from [dist/](dist/) on GitHub Pages. `python build.py` makes `preview.html` and `dist/` from `art/`; both have to be committed to reach the web
- Applying writes the 17 slots and the scheme name under `HKCU\Control Panel\Cursors` and reloads them with `SystemParametersInfo(SPI_SETCURSORS)`
- Each cursor file holds 32, 48, 64, 96 and 128px images, so Windows picks a matching one when the size goes up and the pixels stay sharp. The size is set with `SystemParametersInfo(0x2029)`, the call the Settings app uses, and undo restores it
- There are two backups. `backup-initial.json` is the state at setup (for remove everything); `backup-visit.json` is the state right before the first apply after opening the page (for undo)
- Each time the page opens it makes a 16-character visit id, keeps it in `sessionStorage` and sends it with each request. An apply with a new visit id takes a fresh visit backup
- After undo, every scheme except the one in use is removed along with its cursor files
- A hue other than 0 makes the handler recolour the PNGs inside the downloaded .cur/.ani files pixel by pixel (HSL, hue only) into `%LOCALAPPDATA%\cursor-playground\<id>-h<hue>`. PowerShell loops are too slow for that, so it compiles a small C# class with `Add-Type`, which ships with Windows. The formula matches the page's, so the colours agree
- Any web page can call this address, so only `apply/<a scheme listed in schemes.json>/<visit>[/<size>[/<hue 0-359>[/<a shape listed in shapes.json>]]]`, `size/<size>/<visit>`, `schedule/<visit>/<hour>-<scheme>-<hue>[-<shape>]...` (up to 6), `unschedule`, `restore/<visit>`, `status`, `settings` and `unlink` are accepted. Any other address or smuggled argument is ignored
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
| `art/commodore` | Commodore | The blue-on-lavender palette of an 8-bit home computer. |
| `art/terminal` | Amber terminal | Amber phosphor glowing on an old terminal screen. |
| `art/dos` | DOS | Four hard steps of EGA blue from top to bottom. |
| `art/arcade` | Arcade | Cabinet-sign colours from yellow to purple inside a double black line. |

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
| `art/plasma` | Plasma | Bright electric arcs reaching out inside a purple glass globe. |
| `art/vhs` | VHS | Colour fringes offset left and right with bands of tape noise. |
| `art/aurora` | Aurora | Curtains of light drifting from green through blue to violet. |
| `art/sonar` | Sonar | Green concentric rings spreading across a dark screen. |
| `art/xray` | X-ray | A bright skeleton showing through a translucent blue body. |
| `art/noise` | Static | Black-and-white noise, like a screen with no signal. |
| `art/lavalamp` | Lava lamp | Orange blobs floating through purple liquid. |

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
| `art/rust` | Rust | Iron gone red with rust, bare metal showing through. |
| `art/velvet` | Velvet | Crimson pile that deepens towards the edges. |
| `art/brick` | Brick | Red bricks in a running bond with pale mortar. |
| `art/jade` | Jade | Clear green stone with a white sheen running through it. |
| `art/amber` | Amber | Tiny bubbles trapped in hardened golden resin. |
| `art/steel` | Brushed steel | Matte metal with a horizontal hairline grain. |
| `art/wrap` | Bubble wrap | Rows of puffed-up air pockets in clear plastic. |
| `art/rubber` | Rubber | Matte black rubber with a fine pebbled grain. |

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
| `art/argyle` | Argyle | Overlapping diamonds crossed by thin diagonal lines. |
| `art/tartan` | Tartan | A green and red check crossed by white and yellow lines. |
| `art/houndstooth` | Houndstooth | A tight black-and-white dogtooth weave. |
| `art/tiedye` | Tie-dye | Six colours spiralling out from the centre. |
| `art/camo` | Camo | Blotches of khaki and olive in a military pattern. |
| `art/mosaic` | Mosaic | Coloured tile chips separated by grout lines. |
| `art/gingham` | Gingham | Blue and white squares overlapping in a light check. |
| `art/confetti` | Confetti | Scraps of coloured paper scattered over white. |

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
| `art/chalk` | Chalk | White chalk on a blackboard, dusty along the stroke. |
| `art/marker` | Highlighter | Thick yellow ink bleeding past the outline. |
| `art/stamp` | Rubber stamp | Red ink pressed unevenly from a rubber stamp. |
| `art/sketch` | Sketch | Pencil lines gone over twice, left hollow inside. |
| `art/wireframe` | Wireframe | Blue edges and grid dots, nothing filled in. |
| `art/comic` | Comic | Heavy double ink lines, white fill and hatched shadow. |
| `art/dotwork` | Dotwork | Shading made only from the density of dots. |

**Nature and seasons**

| Folder | Name | Style |
|---|---|---|
| `art/sakura` | Cherry blossom | Pale pink body scattered with petals, some drifting outside. |
| `art/forest` | Forest | Dark green moss mixed with brighter leaves. |
| `art/snow` | Snow | Pure white body with snowflakes floating around it. |
| `art/ocean` | Ocean | Bands of blue waves with white foam. |
| `art/desert` | Desert | Sand with the ripples of dunes. |
| `art/autumn` | Autumn | Orange and red leaves layered over each other. |
| `art/meadow` | Meadow | Yellow and pink wildflowers dotted through grass. |
| `art/storm` | Storm | Yellow lightning splitting grey thunderclouds. |
| `art/bamboo` | Bamboo | Green bamboo stalks with joints and a bright highlight. |
| `art/coral` | Coral | Pink coral branches touched by blue water. |
| `art/volcano` | Volcano | Red lava glowing through cracks in black rock. |
| `art/leaf` | Leaf | Bright veins spreading through a green leaf. |
| `art/rain` | Rain | Slanted streaks of rain against a grey sky. |

**Animated**

| Folder | Name | Style |
|---|---|---|
| `art/rainbowflow` | Rainbow flow | Rainbow bands that keep flowing upwards. |
| `art/neonpulse` | Neon pulse | A cyan neon glow that swells and fades like breathing. |
| `art/flicker` | Flickering flame | The flame edge wavers and sparks fly upwards. |
| `art/twinkle` | Twinkling stars | Stars inside a space body switch on and off in turn. |
| `art/jitter` | Glitch jitter | The red and cyan slip shakes, and now and then one row jumps sideways. |
| `art/wave` | Wave | Blue wave bands roll sideways with white foam riding along. |
| `art/heartbeat` | Heartbeat | The pink body brightens in a double beat and its glow spreads out. |
| `art/electric` | Electric | The yellow and white outline crackles while blue sparks jump around it. |
| `art/barber` | Barber pole | Red, white and blue diagonal stripes keep spinning. |
| `art/coderain` | Code rain | Streams of green code pour down inside a black body. |
| `art/rainfall` | Rainfall | Raindrops falling without stop, each column at its own pace. |
| `art/bubbles` | Bubbles | Bubbles rising through water and popping at the top. |
| `art/lavaflow` | Lava flow | Molten rock rippling as it creeps downward. |
| `art/spinner` | Spinner | Six coloured wedges turning around the centre. |
| `art/scan` | Scan | A bright line sweeping from top to bottom. |
| `art/firework` | Firework | Sparks spreading outward ring by ring and fading. |
| `art/snowfall` | Snowfall | Snowflakes drifting down around a white body. |
| `art/chameleon` | Chameleon | The whole body cycling slowly through the colour wheel. |
| `art/ripple` | Ripple | Rings spreading out from the centre like water. |
| `art/marquee` | Marquee | Border bulbs lighting one after another around the edge. |

**Game items**

| Folder | Name | Style |
|---|---|---|
| `art/fantasy` | Fantasy | A silver sword, wooden hourglass, shield, compass and magic wand. |

**Food and drink**

| Folder | Name | Style |
|---|---|---|
| `art/chocolate` | Chocolate | A bar of chocolate divided by moulded grooves. |
| `art/strawberry` | Strawberry | Red flesh speckled with yellow seeds. |
| `art/mintchoco` | Mint choc chip | Mint ice cream studded with chocolate chips. |
| `art/coffee` | Coffee | Crema swirling on the surface of a cup. |
| `art/soda` | Soda | Bubbles rising through pale blue fizz. |
| `art/honey` | Honey | Golden honey filling a hexagonal comb. |
| `art/matcha` | Matcha | Deep green matcha under a fine layer of foam. |
| `art/cookie` | Cookie | Baked dough studded with chocolate chips. |

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

## Shapes

The **Cursor shape** tabs at the top of the preview page change the silhouette without touching the themes. Pick one and the same schemes are redrawn in that shape: each theme keeps its colours, pattern and animation, only the outline changes. Adding `?shape=round` to the page URL opens it that way.

<!-- shapes:en -->
| Folder | Name | Look |
|---|---|---|
| `art/` | Classic | The angular arrow and the per-theme link shape this project started with. |
| `shapes/round` | Round | A smooth arrow with the corners shaved off. The link is a pointing hand. |
| `shapes/chunky` | Chunky | A wide triangle with a thick tail, easy to spot at a glance. |
| `shapes/sleek` | Sleek | A long, narrow triangle with a thin tail that covers less of the screen. |

<!-- /shapes:en -->

A shape is six silhouettes in `shapes/<shape>/`: `arrow`, `ibeam`, `wait`, `no`, `move` and `hand`. They hold no colour — `#` is the outline (one pixel around the edge), `-` a line inside the body, `o` the inside, `.` empty. At build time [shape.py](shape.py) borrows each theme's colours: the outline colour goes on `#` and `-`, the inside is sampled from the same relative spot in the theme's own drawing, and any glow outside the body is wrapped around the new silhouette again. The four resize arrows, precision select, handwriting and alternate select are symbols with no silhouette of their own, so they stay as the theme drew them.

Cursor files land in `dist/<shape>/<scheme>/` (the first shape keeps `dist/<scheme>/`), and the preview page fetches `data/<shape>.json` the first time you pick a shape.

## Installing from the repository

While editing the art, double-click **[cursors.bat](cursors.bat)** in a clone. Needs Python 3.10+. It only registers schemes; you pick one in the pointer settings. The menu is in Korean.

```
  cursor-playground 커서 구성표
  1) 전체 등록   2) 전체 제거        (register all / remove all)
  3) 개별 등록   4) 개별 제거        (register some / remove some)
  5) 현재 상태   6) 커서 모양 (기본)  (status / cursor shape)
  0) 끝내기                            (quit)
```

Menu item 6 switches the shape; everything after it registers, removes and reports that shape. A shape other than the first one copies the cursors `build.py` already made under `dist/`, so it needs no Python.

```bat
cursors.bat -Install                    :: register all
cursors.bat -Install -Scheme neon,pink  :: register some (comma-separated)
cursors.bat -Install -Shape round       :: register all in the round shape
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
   - **색조** — 색상환을 0°~355° 돌림. 검정·흰색·회색은 그대로. 페이지 커서와 카드가 바로 바뀌고, 적용하면 `cursor-playground 네온 색조120` 같은 그 색의 새 구성표를 만듦
6. **시간대별 자동 전환** — 시각마다 구성표를 정하고 **켜기**. 처리 스크립트가 줄마다 하루 한 번짜리 작업을 윈도우 작업 스케줄러에 등록함(관리자 권한 필요 없음). **끄기** 로 지움
7. 검색칸에 이름을 넣어 찾고, 마음에 드는 구성표에 별표를 눌러 **즐겨찾기만** 으로 거름. **랜덤 적용** 은 무작위 구성표에 무작위 색조를 입혀 적용함
8. 페이지 아래 **내 커서 그리기** — 32x32 격자에 찍어 그리고 클릭 지점을 정하면 페이지 커서로 바로 보이고, 다섯 가지 크기가 든 .cur 로 내려받음. 그림은 브라우저에 남음
9. 다 치우려면 페이지 아래 **완전 제거** — 한 줄 설치할 때의 커서로 돌린 뒤 주소 연결과 설치 폴더 삭제

동작 방식:

- 커서 파일은 Pages 의 [dist/](dist/) 에서 받음. `python build.py` 가 `art/` 로 `preview.html` 과 `dist/` 를 같이 만들고, 둘 다 커밋해야 웹에 반영됨
- 적용은 `HKCU\Control Panel\Cursors` 의 17칸과 구성표 이름을 바꾸고 `SystemParametersInfo(SPI_SETCURSORS)` 로 바로 다시 읽힘
- 커서 파일 하나에 32·48·64·96·128px 이미지를 모두 넣어서, 크기를 키워도 윈도우가 맞는 이미지를 골라 픽셀이 뭉개지지 않음. 크기는 설정 앱이 쓰는 `SystemParametersInfo(0x2029)` 로 바꾸고 원래대로 때 같이 되돌림
- 백업은 두 개. `backup-initial.json` 은 한 줄 설치할 때 상태(완전 제거용), `backup-visit.json` 은 페이지를 연 뒤 첫 적용 직전 상태(원래대로용)
- 페이지는 열 때마다 16자리 방문 번호를 만들어 `sessionStorage` 에 두고 요청에 붙임. 새 방문 번호로 적용이 오면 그때 방문 백업을 새로 뜸
- 원래대로 뒤에는 지금 쓰는 구성표를 뺀 나머지 구성표와 커서 파일을 지움
- 색조가 0 이 아니면 처리 스크립트가 받은 .cur/.ani 안의 PNG 를 픽셀마다 다시 칠해(HSL 에서 색상만) `%LOCALAPPDATA%\cursor-playground\<id>-h<색조>` 에 둠. PowerShell 반복문으로는 너무 느려서 윈도우에 들어 있는 `Add-Type` 으로 작은 C# 클래스를 컴파일해 씀. 식이 페이지와 같아서 색이 맞음
- 아무 웹 페이지나 이 주소를 부를 수 있으므로, 받는 요청은 `apply/<schemes.json 에 있는 구성표>/<방문>[/<크기>[/<색조 0-359>[/<shapes.json 에 있는 모양>]]]`, `size/<크기>/<방문>`, `schedule/<방문>/<시>-<구성표>-<색조>[-<모양>]...`(최대 6칸), `unschedule`, `restore/<방문>`, `status`, `settings`, `unlink` 뿐. 다른 주소나 끼워 넣은 인자는 전부 무시함
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
| `art/commodore` | 코모도어 | 파랑과 연보라 두 색만 쓰던 8비트 가정용 컴퓨터 화면. |
| `art/terminal` | 터미널 | 검은 배경에 주황 인광이 번지는 옛 단말기 글자. |
| `art/dos` | 도스 | 위에서 아래로 네 단계로 끊기는 EGA 파랑. |
| `art/arcade` | 아케이드 | 노랑에서 보라로 떨어지는 오락실 간판 색에 두 겹 검정 선. |

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
| `art/plasma` | 플라즈마 | 보랏빛 유리구 속에서 밝은 전기 줄기가 뻗어 나감. |
| `art/vhs` | VHS | 재생 중 색이 좌우로 어긋나고 가로 잡음 띠가 지나감. |
| `art/aurora` | 오로라 | 초록에서 보라로 넘어가는 빛의 커튼이 비스듬히 흐름. |
| `art/sonar` | 소나 | 검은 화면에 초록 동심원이 퍼지는 수중 음파 탐지기. |
| `art/xray` | 엑스레이 | 파란 반투명 몸체 속으로 밝은 뼈대가 비쳐 보임. |
| `art/noise` | 지지직 | 신호가 끊긴 화면처럼 흑백 잡음이 가득 낀 몸체. |
| `art/lavalamp` | 라바램프 | 보라색 액체 속을 주황 방울이 떠다니는 램프. |

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
| `art/rust` | 녹 | 붉은 녹이 슬고 군데군데 쇳빛이 벗겨진 철판. |
| `art/velvet` | 벨벳 | 가장자리로 갈수록 어두워지는 자주색 융단 결. |
| `art/brick` | 벽돌 | 엇갈려 쌓은 붉은 벽돌과 밝은 줄눈. |
| `art/jade` | 옥 | 맑은 초록 돌에 흰 광택과 결이 비침. |
| `art/amber` | 호박 | 굳은 황금빛 수지 속에 작은 기포가 갇힘. |
| `art/steel` | 강철 | 가로로 긁힌 헤어라인이 지나가는 무광 금속. |
| `art/wrap` | 에어캡 | 볼록한 공기 방울이 줄지어 박힌 투명 포장 비닐. |
| `art/rubber` | 고무 | 빛을 먹는 검은 무광 고무에 오돌토돌한 돌기. |

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
| `art/argyle` | 아가일 | 마름모가 겹치고 가는 사선이 지나가는 니트 무늬. |
| `art/tartan` | 타탄 | 초록·빨강 격자에 흰 줄과 노란 줄이 겹침. |
| `art/houndstooth` | 하운드투스 | 흑백 새발 격자가 촘촘히 반복됨. |
| `art/tiedye` | 타이다이 | 가운데에서 소용돌이치며 번지는 여섯 빛깔 염색. |
| `art/camo` | 위장 | 카키와 올리브 얼룩이 뭉개져 섞인 군용 무늬. |
| `art/mosaic` | 모자이크 | 줄눈으로 나뉜 색색의 타일 조각. |
| `art/gingham` | 깅엄 | 파랑과 흰색이 겹쳐 짙어지는 반투명 체크. |
| `art/confetti` | 색종이 | 흰 바탕에 알록달록한 종이 조각이 흩뿌려짐. |

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
| `art/chalk` | 분필 | 칠판 위에 흰 분필로 그어 가루가 날리는 선. |
| `art/marker` | 형광펜 | 노란 형광 잉크가 선 밖으로 번진 굵은 칠. |
| `art/stamp` | 도장 | 빨간 잉크가 듬성듬성 묻은 고무 도장 자국. |
| `art/sketch` | 스케치 | 여러 번 겹쳐 그은 연필 선에 속은 비워 둠. |
| `art/wireframe` | 와이어프레임 | 파란 선과 격자 점만 남긴 설계 도면. |
| `art/comic` | 만화 | 두 겹 굵은 검정 선에 흰 속과 빗금 그림자. |
| `art/dotwork` | 점묘 | 점의 촘촘한 정도만으로 음영을 낸 그림. |

**자연·계절**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/sakura` | 벚꽃 | 연분홍 몸체에 꽃잎이 박히고 주변으로 흩날림. |
| `art/forest` | 숲 | 짙은 초록 이끼에 밝은 잎이 섞인 숲. |
| `art/snow` | 눈 | 새하얀 몸체 둘레로 눈송이가 떠 있음. |
| `art/ocean` | 바다 | 파란 물결 띠와 하얀 포말. |
| `art/desert` | 사막 | 모래색 바탕에 모래언덕 결. |
| `art/autumn` | 단풍 | 주황과 빨강 낙엽이 겹쳐 쌓인 가을빛. |
| `art/meadow` | 들꽃 | 풀밭 사이에 노랑·분홍 들꽃이 드문드문 핌. |
| `art/storm` | 폭풍 | 잿빛 먹구름 사이로 노란 번개가 갈라짐. |
| `art/bamboo` | 대나무 | 마디가 진 초록 대나무 줄기에 밝은 빛줄. |
| `art/coral` | 산호 | 분홍 산호 가지에 푸른 바닷물이 섞임. |
| `art/volcano` | 화산 | 검게 굳은 암석 틈으로 붉은 용암이 비침. |
| `art/leaf` | 잎 | 초록 잎에 밝은 잎맥이 갈라져 뻗음. |
| `art/rain` | 비 | 잿빛 하늘에 빗줄기가 비스듬히 내리꽂힘. |

**움직이는**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/rainbowflow` | 무지개 흐름 | 빨주노초파보 띠가 위로 쉬지 않고 흘러감. |
| `art/neonpulse` | 네온 맥박 | 청록 네온 번짐이 숨 쉬듯 커졌다 작아짐. |
| `art/flicker` | 일렁이는 불꽃 | 불꽃 경계가 흔들리고 위로 불티가 튐. |
| `art/twinkle` | 반짝이는 별 | 우주 몸체 속 별들이 차례로 켜졌다 꺼짐. |
| `art/jitter` | 글리치 떨림 | 빨강·청록 어긋남이 떨리고 가끔 한 줄이 옆으로 밀림. |
| `art/wave` | 파도 | 파란 물결 띠가 옆으로 넘실거리고 흰 포말이 따라 흐름. |
| `art/heartbeat` | 두근두근 | 분홍 몸체가 콩닥 두 번씩 밝아지며 번짐이 퍼짐. |
| `art/electric` | 전기 | 노랑·흰 외곽선이 번쩍이고 둘레로 푸른 불꽃이 튐. |
| `art/barber` | 이발소 기둥 | 빨강·흰·파랑 사선 줄무늬가 쉬지 않고 돌아감. |
| `art/coderain` | 글자비 | 검은 몸체 안에서 초록 글자 줄기가 위에서 아래로 쏟아짐. |
| `art/rainfall` | 빗줄기 | 빗방울이 줄마다 다른 높이에서 쉬지 않고 떨어짐. |
| `art/bubbles` | 기포 | 물속 기포가 위로 올라가 톡 터짐. |
| `art/lavaflow` | 용암 | 붉은 용암이 일렁이며 천천히 흘러내림. |
| `art/spinner` | 회전 | 여섯 빛깔 부채꼴이 가운데를 축으로 돌아감. |
| `art/scan` | 스캔 | 밝은 가로줄이 위에서 아래로 훑고 지나감. |
| `art/firework` | 폭죽 | 불꽃이 둘레로 한 겹씩 퍼지며 옅어짐. |
| `art/snowfall` | 눈 내림 | 하얀 몸체 둘레로 눈송이가 계속 내려옴. |
| `art/chameleon` | 카멜레온 | 몸 전체 색이 색상환을 따라 천천히 바뀜. |
| `art/ripple` | 파문 | 물결 고리가 가운데에서 바깥으로 퍼짐. |
| `art/marquee` | 전구 간판 | 테두리 전구가 한 칸씩 차례로 켜지며 흘러감. |

**게임 아이템**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/fantasy` | 판타지 | 은빛 칼, 나무 모래시계, 방패, 나침반, 마법 지팡이. |

**음식**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/chocolate` | 초콜릿 | 홈으로 나뉜 판 초콜릿 조각. |
| `art/strawberry` | 딸기 | 빨간 과육에 노란 씨가 박힌 딸기. |
| `art/mintchoco` | 민트초코 | 민트색 아이스크림에 초코 조각이 섞임. |
| `art/coffee` | 커피 | 잔 위에서 크레마가 소용돌이치는 커피. |
| `art/soda` | 소다 | 하늘색 탄산 속에서 기포가 올라오는 음료. |
| `art/honey` | 꿀 | 금빛 꿀이 들어찬 육각 벌집. |
| `art/matcha` | 말차 | 진한 초록 말차에 거품이 곱게 올라옴. |
| `art/cookie` | 쿠키 | 구운 반죽에 초코칩이 박힌 쿠키. |

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

### 모양

시안 페이지 위쪽 **커서 모양** 탭은 테마를 건드리지 않고 실루엣만 바꿈. 고르면 같은 구성표들이 그 모양으로 다시 그려짐 — 색·무늬·움직임은 그대로고 외곽선만 달라짐. 주소에 `?shape=round` 를 붙이면 그 모양으로 열림.

<!-- shapes:ko -->
| 폴더 | 이름 | 생김새 |
|---|---|---|
| `art/` | 기본 | 각진 화살표와 테마마다 다른 링크 그림. 지금까지의 모양. |
| `shapes/round` | 둥근 | 모서리를 깎아 매끈한 화살표. 링크는 손가락을 세운 손. |
| `shapes/chunky` | 두꺼운 | 넓은 삼각형에 굵은 꼬리. 굵은 선으로 또렷하게 보임. |
| `shapes/sleek` | 날렵한 | 길고 가는 삼각형에 얇은 꼬리. 화면을 덜 가림. |

<!-- /shapes:ko -->

모양 하나는 `shapes/<모양>/` 의 실루엣 여섯 개(`arrow`, `ibeam`, `wait`, `no`, `move`, `hand`)임. 색은 없음 — `#` 은 외곽선(가장자리 한 겹), `-` 는 속에 그은 선, `o` 는 속, `.` 는 빈칸. 빌드할 때 [shape.py](shape.py) 가 테마의 색을 빌려 옴: 외곽선 색을 `#` 과 `-` 에 넣고, 속은 테마 그림의 같은 비율 자리에서 색을 떠 오고, 몸 바깥으로 번지는 빛은 새 실루엣 둘레에 다시 두름. 크기 조정 4종·정밀·필기·대체 선택은 실루엣이 따로 없는 기호라 테마가 그린 그대로 둠.

만들어진 커서는 `dist/<모양>/<구성표>/` 에 들어감(첫 모양은 `dist/<구성표>/` 그대로). 시안 페이지는 모양을 처음 고를 때 `data/<모양>.json` 을 받아 옴.

### 저장소에서 직접 등록

그림을 고치면서 볼 때는 클론한 폴더의 **[cursors.bat](cursors.bat)** 을 더블클릭. Python 3.10+ 필요. 등록만 하고 적용은 포인터 설정에서 고름.

```
  cursor-playground 커서 구성표
  1) 전체 등록   2) 전체 제거
  3) 개별 등록   4) 개별 제거
  5) 현재 상태   6) 커서 모양 (기본)
  0) 끝내기
```

6번으로 모양을 바꾸면 그 뒤의 등록·제거·상태가 모두 그 모양을 가리킴. 첫 모양이 아닌 모양은 `build.py` 가 만들어 둔 `dist/` 의 커서를 복사만 하므로 Python 이 필요 없음.

```bat
cursors.bat -Install                    :: 전체 등록
cursors.bat -Install -Scheme neon,pink  :: 개별 등록 (쉼표로 여러 개)
cursors.bat -Install -Shape round       :: 전체를 둥근 모양으로 등록
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

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
- Each cursor file holds several sizes, so Windows picks a matching one when the size goes up and the pixels stay sharp (pixel art carries 32, 48, 64, 96 and 128px; the smooth shapes carry 32, 64 and 128 and let Windows stretch the rest). The size is set with `SystemParametersInfo(0x2029)`, the call the Settings app uses, and undo restores it
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
| `art/terminal` | Amber terminal | Scanlined amber phosphor glowing off an old terminal screen. |
| `art/dos` | DOS | Four hard steps of EGA blue from top to bottom, inside a thin white rim. |
| `art/arcade` | Arcade | Cabinet-sign colours from yellow to purple inside a double black line. |

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
| `art/coderain` | Matrix | Streams of green code pour down inside a black body. |
| `art/rainfall` | Rainfall | Raindrops falling without stop, each column at its own pace. |
| `art/bubbles` | Bubbles | Bubbles rising through water and popping at the top. |
| `art/lavaflow` | Lava flow | Molten rock rippling as it creeps downward. |
| `art/spinner` | Spinner | A four-blade pinwheel in red, green, yellow and blue spinning under a white glint. |
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

**Sea life**

| Folder | Name | Style |
|---|---|---|
| `art/whaleshark` | Whale shark | Dark blue-grey skin dotted with a grid of white spots, like a whale shark. |
| `art/dolphin` | Dolphin | Sleek dolphin, dark blue-grey on the back fading to a pale belly. |
| `art/shrimp` | Shrimp | Translucent pink-orange shrimp segments. |
| `art/puffer` | Pufferfish | A yellow pufferfish with brown spots and little spines. |
| `art/mola` | Ocean sunfish | The silver-grey disc of an ocean sunfish with faint mottling. |
| `art/catshark` | Cloudy catshark | Sandy brown with dark saddle blotches, like a cloudy catshark. |

**Sea life · Bodies**

| Folder | Name | Style |
|---|---|---|
| `art/whalesharkbody` | Whale shark | The whale shark is the cursor: blunt head as the tip, crescent tail at the other end, dark blue-grey skin with a grid of white spots. |
| `art/dolphinbody` | Dolphin | The creature is the cursor. A dolphin whose beak is the pointer tip, dark blue-grey back sharply meeting a pale belly. |
| `art/shrimpbody` | Shrimp | The creature is the cursor. Translucent pink-orange shrimp segments. |
| `art/pufferbody` | Pufferfish | The creature is the cursor. A yellow pufferfish with brown spots and little spines. |
| `art/molabody` | Ocean sunfish | The creature is the cursor. A silver-grey, faintly mottled ocean sunfish whose long dark fins become the arrowheads. |
| `art/catsharkbody` | Cloudy catshark | The creature is the cursor. Sandy brown with dark saddle blotches, like a cloudy catshark. |

**Sea life · Animated**

| Folder | Name | Style |
|---|---|---|
| `art/whalesharkanim` | Whale shark | A swimming whale shark — tail beats, gaping mouth, bubbles and caustic light across the body. |
| `art/dolphinanim` | Dolphin | A swimming dolphin — tail beats, bubbles and caustic light across the body. |
| `art/shrimpanim` | Shrimp | A swimming shrimp — tail beats, bubbles and caustic light across the body. |
| `art/pufferanim` | Pufferfish | A swimming pufferfish — tail beats, bubbles and caustic light, and it puffs up and deflates while you wait. |
| `art/molaanim` | Ocean sunfish | A swimming ocean sunfish — its tall dorsal and anal fins beat in turn while caustic light drifts across the body. |
| `art/catsharkanim` | Cloudy catshark | A cloudy catshark wriggling in an eel-like S — bubbles rise from its gills and caustic light drifts across the body. |

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

The **Cursor shape** tabs at the top of the preview page change the silhouette without touching the themes. Pick one and the same schemes are redrawn in that shape: each theme keeps its colours, pattern and animation, only the outline changes. Classic is the theme's own pixel art; the other ten are drawn with smooth, anti-aliased curves. Adding `?shape=round` to the page URL opens it that way.

<!-- shapes:en -->
| Id | Name | Look |
|---|---|---|
| `art/` | Classic | The theme's own pixel art: an angular arrow with a crisp notch and tail. |
| `round` | Round | A chubby arrow with every corner rounded off; the tip has the largest radius. |
| `hollow` | Outline | Hollowed out to a thick outline, so whatever is underneath stays readable. |
| `cutout` | Sticker | A bright band around the body and a shadow below right, so the shape reads on any background. |
| `blob` | Wedge | Three points, no tail or notch: a sharp tip with the other two corners rounded wide. |
| `comet` | Comet | The tail stretches down and right into a single point, so the direction is unmistakable. |
| `needle` | Needle | Narrow body, long tail — the option that covers the least of the screen. |
| `dart` | Paper plane | Four points with a concave back edge, like two wings swept backwards. |
| `drop` | Droplet | A pointed tip on an almost circular body, like a single drop of ink. |
| `glow` | Neon | The theme's brightest colour bleeds out around the body; it glows on dark backgrounds. |
| `bevel` | Beveled | Where the others round off gently, this one breaks like a chamfered edge. |

<!-- /shapes:en -->

Every shape but Classic is drawn by [smooth.py](smooth.py) instead of being stored as pixel art. The outline is a handful of points; every corner gets a real circular arc (a chamfer looks pointed, an arc does not); a signed distance field then says how much of each cell the shape covers, which is what makes the edges anti-aliased. A `.cur` carries 32-bit alpha, so that smoothness survives into the cursor file. The sizes inside a cursor file are **drawn again at each size** instead of being scaled up, because an anti-aliased drawing falls apart when you enlarge it by a whole number. Smooth shapes carry 32, 64 and 128; Windows stretches those for the sizes in between.

Colour is not baked in. Each shape and slot is drawn once into a *stencil* that records, per cell, which layer covers it and by how much: shadow, the theme's outer glow, bright band, body, the lit and shaded bevel faces, outline. Then for every theme the colours are read out of that theme's own drawing of the same slot and dropped into the stencil. The body colour is taken **from the matching relative spot** in the theme's drawing rather than averaged down to one colour, so a leopard keeps its spots and an argyle keeps its diamonds; the outline colour comes from the rim, the brightest colour serves as gloss, and the rings outside the body are wrapped around the new shape again so a neon theme keeps its glow. Bits that sit apart from the body — the sparks of Lightning, falling flakes of Snowfall, petals of Cherry blossom — are scattered back around the new shape at the same relative spots, frame by frame. Animated themes keep their animation, because the colours are read again for every frame — that is why lightning still crackles inside a rounded arrow, a rounded hourglass still has yellow sand and a rounded no sign is still red.

A shape covers five slots: `arrow`, `ibeam`, `wait`, `no` and `move`. Help, background work, location select and user select are an arrow with a symbol on it, so the symbol is lifted off the theme's own drawing and placed beside the new arrow. The four resize arrows, precision select, handwriting and alternate select are symbols with no silhouette of their own, and link select is the theme's own face (a heart, a pointing hand, a star), so those stay exactly as the theme drew them.

Cursor files land in `dist/<shape>/<scheme>/` (the first shape keeps `dist/<scheme>/`), and the preview page fetches `data/<shape>.json` the first time you pick a shape — those page drawings are rendered large for the same reason, so the previews are not a blur of enlarged pixels. The eight slots a shape does not touch would be byte-for-byte the Classic files, so they are not written again — the installer and the handler fall back to `dist/<scheme>/` for those.

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
- 커서 파일 하나에 여러 크기 이미지를 넣어서, 크기를 키워도 윈도우가 맞는 이미지를 골라 픽셀이 뭉개지지 않음(픽셀아트는 32·48·64·96·128px, 매끈한 모양은 32·64·128 을 담고 사이 크기는 윈도우가 늘려 씀). 크기는 설정 앱이 쓰는 `SystemParametersInfo(0x2029)` 로 바꾸고 원래대로 때 같이 되돌림
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
| `art/terminal` | 터미널 | 검은 판에 주사선이 지나고 둘레로 주황 인광이 번지는 옛 단말기 글자. |
| `art/dos` | 도스 | 위에서 아래로 네 단계로 끊기는 EGA 파랑에 흰 테 한 겹. |
| `art/arcade` | 아케이드 | 노랑에서 보라로 떨어지는 오락실 간판 색에 두 겹 검정 선. |

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
| `art/coderain` | 매트릭스 | 검은 몸체 안에서 초록 글자 줄기가 위에서 아래로 쏟아짐. |
| `art/rainfall` | 빗줄기 | 빗방울이 줄마다 다른 높이에서 쉬지 않고 떨어짐. |
| `art/bubbles` | 기포 | 물속 기포가 위로 올라가 톡 터짐. |
| `art/lavaflow` | 용암 | 붉은 용암이 일렁이며 천천히 흘러내림. |
| `art/spinner` | 회전 | 빨강·초록·노랑·파랑 네 날 바람개비가 흰 광택 아래에서 빙글빙글 돎. |
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

**해양 생물**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/whaleshark` | 고래상어 | 짙은 청회색 몸에 흰 점이 격자로 박힌 고래상어. |
| `art/dolphin` | 돌고래 | 짙은 청회색 등에서 밝은 배로 번지는 매끈한 돌고래. |
| `art/shrimp` | 새우 | 분홍 주황 마디가 비치는 새우. |
| `art/puffer` | 복어 | 노란 몸에 갈색 점, 가시가 돋은 복어. |
| `art/mola` | 개복치 | 은회색 원반 몸에 옅은 반점이 번진 개복치. |
| `art/catshark` | 괴상어 | 모래 갈색에 짙은 안장 무늬가 얹힌 괴상어(두툽상어). |

**해양 생물 · 몸**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/whalesharkbody` | 고래상어 | 몸이 곧 커서인 고래상어. 뭉툭한 머리 끝과 초승달 꼬리, 흰 점이 격자로 박힌 짙은 청회색 몸. |
| `art/dolphinbody` | 돌고래 | 몸이 곧 커서인 돌고래. 뾰족한 부리 끝이 커서 끝이고, 짙은 청회색 등과 흰회색 배가 또렷이 갈리는 돌고래. |
| `art/shrimpbody` | 새우 | 몸이 곧 커서인 새우. 분홍 주황 마디가 비치는 새우. |
| `art/pufferbody` | 복어 | 몸이 곧 커서인 복어. 노란 몸에 갈색 점, 가시가 돋은 복어. |
| `art/molabody` | 개복치 | 몸이 곧 커서인 개복치. 은회색 원반 몸에 옅은 반점, 짙은 등·뒷지느러미가 화살촉이 되는 개복치. |
| `art/catsharkbody` | 괴상어 | 몸이 곧 커서인 괴상어. 모래 갈색에 짙은 안장 무늬가 얹힌 괴상어(두툽상어). |

**해양 생물 · 애니**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/whalesharkanim` | 고래상어 | 헤엄치는 고래상어. 꼬리질과 입 벌림, 거품, 몸 위로 빛 물결이 지나가는 커서. |
| `art/dolphinanim` | 돌고래 | 헤엄치는 돌고래. 꼬리질과 거품, 몸 위로 빛 물결이 지나가는 커서. |
| `art/shrimpanim` | 새우 | 헤엄치는 새우. 꼬리질과 거품, 몸 위로 빛 물결이 지나가는 커서. |
| `art/pufferanim` | 복어 | 헤엄치는 복어. 꼬리질과 거품, 빛 물결이 지나가고 기다릴 때는 부풀었다 오그라드는 커서. |
| `art/molaanim` | 개복치 | 헤엄치는 개복치. 등·뒷지느러미를 번갈아 흔들고 몸 위로 빛 물결이 지나가는 커서. |
| `art/catsharkanim` | 괴상어 | 뱀장어처럼 S 자로 몸을 흔들며 헤엄치는 괴상어. 아가미에서 거품이 오르고 몸 위로 빛 물결이 지나가는 커서. |

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

시안 페이지 위쪽 **커서 모양** 탭은 테마를 건드리지 않고 실루엣만 바꿈. 고르면 같은 구성표들이 그 모양으로 다시 그려짐 — 색·무늬·움직임은 그대로고 외곽선만 달라짐. 기본은 테마가 그린 픽셀 그림이고, 나머지 열 가지는 경계가 매끈하게 그려짐. 주소에 `?shape=round` 를 붙이면 그 모양으로 열림.

<!-- shapes:ko -->
| 아이디 | 이름 | 생김새 |
|---|---|---|
| `art/` | 기본 | 테마가 그린 픽셀 그림 그대로. 각진 화살표에 또렷한 홈과 꼬리. |
| `round` | 둥근 | 모든 모서리를 큼직하게 둥글린 통통한 화살표. 끝 반지름이 가장 큼. |
| `hollow` | 테두리 | 속을 비우고 두꺼운 테두리만 남김. 밑에 있는 글자가 보임. |
| `cutout` | 스티커 | 몸 바깥에 밝은 테두리를 두르고 오른쪽 아래로 그림자를 깖. 어떤 배경에서도 형태가 뜸. |
| `blob` | 둥근 삼각 | 꼬리와 홈 없이 세 점만. 끝은 살리고 나머지 두 모서리만 크게 둥글림. |
| `comet` | 긴 꼬리 | 꼬리가 오른쪽 아래로 길게 빠지며 한 점으로 모임. 방향이 확실히 읽힘. |
| `needle` | 바늘 | 폭을 좁히고 꼬리를 길게 뺐음. 화면을 가장 덜 가림. |
| `dart` | 종이비행기 | 네 점만 쓰고 뒷면을 오목하게 팠음. 날개 두 장이 뒤로 젖혀진 형태. |
| `drop` | 물방울 | 끝만 뾰족하고 몸통은 거의 원. 잉크 한 방울 같은 형태. |
| `glow` | 네온 | 몸 바깥으로 테마의 밝은 색이 번짐. 어두운 배경에서 특히 뜸. |
| `bevel` | 입체 | 다른 모양이 완만한 언덕이라면 이건 모서리를 깎아낸 것처럼 꺾임. |

<!-- /shapes:ko -->

기본을 뺀 모양은 픽셀로 저장하지 않고 [smooth.py](smooth.py) 가 그림. 윤곽을 점 몇 개로 잡고, 꼭지점마다 진짜 원호를 끼워 넣고(면취로 깎으면 끝이 뾰족해 보임), 부호 있는 거리함수로 칸마다 얼마나 덮였는지 재서 경계를 매끈하게 만듦. `.cur` 는 32비트 알파를 담으므로 그 매끈함이 커서 파일까지 살아남음. 커서 파일 안의 여러 크기는 늘리지 않고 **크기마다 새로 그림** — 안티에일리어싱된 그림은 정수배로 늘리면 뭉개짐. 매끈한 모양은 32·64·128 을 담고, 사이 크기는 윈도우가 늘려 씀.

색은 박아 넣지 않음. 모양·칸마다 한 번만 그려 **스텐실**을 만드는데, 칸마다 어느 층이 얼마나 덮였는지만 적혀 있음 — 그림자·테마의 번짐·밝은 테두리·몸·빛 받는 면·그늘진 면·외곽선. 그다음 테마마다 그 테마가 그린 같은 칸에서 색을 떠 스텐실에 끼워 넣음. 몸의 색은 하나로 뭉뚱그리지 않고 **같은 비율 자리에서** 떠 오므로 표범은 무늬가, 아가일은 마름모가 남음. 외곽선 색은 가장자리에서, 광택은 가장 밝은 색에서 가져오고, 몸 바깥 번짐은 층마다 새 모양 둘레에 다시 둘러서 네온 계열 테마는 빛도 그대로임. 몸에서 떨어져 나온 조각(전기의 불꽃, 눈보라의 눈송이, 벚꽃의 꽃잎)은 새 모양 둘레의 같은 비율 자리에 프레임마다 다시 흩음. 프레임마다 색을 다시 뜨므로 움직이는 테마는 움직임이 남음 — 둥근 화살표 안에서도 번개가 치고, 둥근 모래시계에 노란 모래가 있고, 둥근 금지 표시가 여전히 빨간 이유가 이것임.

모양이 바꾸는 칸은 다섯(`arrow`, `ibeam`, `wait`, `no`, `move`). 도움말·백그라운드 작업·위치 선택·사용자 선택은 화살표에 기호를 얹은 칸이라, 테마 그림에서 기호만 떼어 새 화살표 옆에 다시 놓음. 크기 조정 4종·정밀·필기·대체 선택은 실루엣이 따로 없는 기호이고, 링크 선택은 테마마다 다른 얼굴(하트·손가락·별)이라 그대로 둠.

만들어진 커서는 `dist/<모양>/<구성표>/` 에 들어감(첫 모양은 `dist/<구성표>/` 그대로). 시안 페이지는 모양을 처음 고를 때 `data/<모양>.json` 을 받아 옴 — 그 안의 그림도 같은 이유로 크게 그려서, 미리보기가 픽셀을 늘린 흐릿한 그림이 되지 않음. 모양이 안 건드리는 여덟 칸은 기본 모양 파일과 바이트까지 같아서 다시 쓰지 않음 — 설치 스크립트와 처리 스크립트가 그 칸만 `dist/<구성표>/` 것으로 넘어감.

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

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
2. Pick a scheme on the page, press **적용** (apply) on the bar at the bottom, confirm, then allow the browser to open the app
3. Tired of trying things? Press **원래대로** (undo) to go back to the cursor you had right before the first apply since opening the page
   - Example: apply Neon pulse → close the page → reopen and apply Rainbow flow → undo → Neon pulse
   - Closing and reopening the tab starts a new count; reloading the same tab keeps it
4. **포인터 설정 열기** (open pointer settings) opens the Windows Mouse Properties dialog on the Pointers tab
5. **커서 크기** (cursor size: 1×, 1.5×, 2×, 3×, 4×) resizes the page's cursors right away, and the apply button applies the size too. To change only the size, press **크기만 적용** (apply size only)
   - **색조** (hue) turns the colour wheel from 0° to 355°. Black, white and grey stay as they are. The page's cursors and cards change right away, and applying makes a new scheme in that colour, such as `cursor-playground 네온 맥박 색조120` (Neon pulse, hue 120)
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

**Sea life · Animated**

| Folder | Name | Style |
|---|---|---|
| `art/whalesharkanim` | Whale shark | A swimming whale shark — tail beats, gaping mouth, bubbles and caustic light across the body. |
| `art/dolphinanim` | Dolphin | A swimming dolphin — tail beats, bubbles and caustic light across the body. |
| `art/shrimpanim` | Shrimp | A swimming shrimp — tail beats, bubbles and caustic light across the body. |
| `art/pufferanim` | Pufferfish | A swimming pufferfish — tail beats, bubbles and caustic light, and it puffs up and deflates while you wait. |
| `art/molaanim` | Ocean sunfish | A swimming ocean sunfish — its tall dorsal and anal fins beat in turn while caustic light drifts across the body. |
| `art/catsharkanim` | Cloudy catshark | A cloudy catshark wriggling in an eel-like S — bubbles rise from its gills and caustic light drifts across the body. |
| `art/bukanganim` | Bukang | The shark that spent twelve days in a Busan North Port canal in autumn 2026 — a dusky shark with a blue-grey back, white belly and tall dorsal fin, beating its tail and puffing bubbles from its gills. |
| `art/otteranim` | Sea otter | A sea otter floating on its back — it taps a clam on its tummy with a stone, and covers its face with both paws to say no. |
| `art/crabanim` | Crab | A sideways-scuttling crab — it lifts and snaps its claws and blows little bubbles while you wait. |
| `art/octopusanim` | Octopus | A round chibi octopus — its eight arms ripple as it moves, and it puffs a cloud of ink while you wait. |

**Forest friends · Animated**

| Folder | Name | Style |
|---|---|---|
| `art/squirrelanim` | Squirrel | A chubby-cheeked chibi squirrel — it stuffs an acorn into its cheeks and out again, and swishes its big tail. |
| `art/hedgehoganim` | Hedgehog | A chestnut-burr chibi hedgehog — it sniffs about with its little nose, and curls into a spiky ball to say no. |
| `art/owlanim` | Owl | A big-eyed chibi owl — it blinks slowly, and swivels its head right round when it's puzzled. |

**Cats · Animated**

| Folder | Name | Style |
|---|---|---|
| `art/cheesecatanim` | Ginger cat | A round ginger cat — it loafs while you wait and presses with a squishy toe-bean paw when you click. |
| `art/tuxedocatanim` | Tuxedo cat | A tuxedo cat in a bow tie — a prim little gentleman who walks with his tail held straight up. |
| `art/blackcatanim` | Black cat | A black cat with round yellow eyes — it bats a ball of yarn about, and puffs up and hisses when startled. |

**Forest friends · Animated**

| Folder | Name | Style |
|---|---|---|
| `art/rabbitanim` | Rabbit | A long-eared chibi rabbit — it twitches its nose, flops its ears up and down, and hops about. |
| `art/foxanim` | Fox | A fluffy-tailed chibi fox — it swishes its big brush, tilts its ears to listen, then pounces. |

**Cats · Animated**

| Folder | Name | Style |
|---|---|---|
| `art/mackerelcatanim` | Grey tabby | A grey striped tabby — it curls its tail into a question mark and grooms itself while you wait. |
| `art/calicocatanim` | Calico cat | A calico cat in white with orange and black patches — it kneads with its paws and squeezes into boxes. |

**Forest friends · Animated**

| Folder | Name | Style |
|---|---|---|
| `art/bearanim` | Bear cub | A round chibi bear cub — it dips a paw into the honey pot, licks it, and hangs from branches to stretch. |
| `art/deeranim` | Fawn | A white-spotted chibi fawn — it bounds on long legs and pricks up its ears. |
| `art/raccoonanim` | Raccoon | A masked chibi raccoon — it rubs berries clean between its paws and waves a ringed tail. |
| `art/moleanim` | Mole | A pink-nosed chibi mole — it pops out of molehills, ducks back in, and digs with big front paws. |
| `art/froganim` | Frog | A green chibi frog on a lily pad — it flicks out its long tongue to tap and hops about. |

**Cats · Animated**

| Folder | Name | Style |
|---|---|---|
| `art/siamesecatanim` | Siamese cat | A blue-eyed Siamese — cream body with dark brown points; it curls its tail into a question mark and chatters. |
| `art/russianbluecatanim` | Russian Blue | A silver-blue cat with green eyes — it sits primly until a feather wand catches its eye. |
| `art/whitecatanim` | Odd-eyed white cat | A snow-white cat with one blue and one gold eye — it laps up milk and rolls about in the sun. |
| `art/munchkincatanim` | Munchkin | A short-legged cream tabby munchkin — it scurries on stubby legs and stands up like a meerkat to look around. |
| `art/norwegiancatanim` | Norwegian Forest cat | A long-haired Norwegian Forest cat with a lush ruff and plume tail — it wraps its tail around itself and climbs trees. |

**Dogs · Animated**

| Folder | Name | Style |
|---|---|---|
| `art/shibaanim` | Shiba Inu | A Shiba Inu with white cheeks and eyebrow dots — it fetches the arrow and wags its curly tail, and plants all four feet when the answer is no. |
| `art/corgianim` | Welsh Corgi | A Welsh Corgi with big perky ears — it wiggles its loaf-shaped bottom while you wait, and turns its back with a huff when the answer is no. |
| `art/pomeraniananim` | Pomeranian | A fluff-ball Pomeranian — it spins and bounces on the spot while you wait, and puffs up and yaps when the answer is no. |
| `art/bichonanim` | Bichon Frise | A Bichon Frise with a cotton-candy head — it bounces its fluffy head while you wait, and shakes it when the answer is no. |
| `art/retrieveranim` | Golden Retriever | A Golden Retriever with a feathery tail — it pants with its tongue out while you wait, and lies down with a teary sigh when the answer is no. |
| `art/dachshundanim` | Dachshund | A long-snouted Dachshund with floppy ears — it lies down and yawns while you wait, and sticks its nose in the air when the answer is no. |
| `art/huskyanim` | Husky | A Husky with a grey mask and blue eyes — it howls at the sky while you wait, and flops on its back in protest when the answer is no. |
| `art/poodleanim` | Poodle | A Poodle with curly ears and a pom-pom tail — it tilts its head this way and that while you wait, and flicks its nose up when the answer is no. |
| `art/malteseanim` | Maltese | A Maltese with a pink bow — it nods off while you wait, and covers its eyes with its paws when the answer is no. |
| `art/jindoanim` | Jindo | A Jindo with pointed ears and a curled tail — it sits up on alert while you wait, and pins its ears back and growls when the answer is no. |

**Little birds · Animated**

| Folder | Name | Style |
|---|---|---|
| `art/javasparrowanim` | Java sparrow | A Java sparrow with a chunky pink beak — it hops along with the arrow on its head, and dozes on its eggs while you wait. |
| `art/budgieanim` | Budgie | A chatty budgie — it bobs and chatters at its mirror while you wait, and crosses its wings in an X when the answer is no. |
| `art/cockatielanim` | Cockatiel | A cockatiel with a jaunty crest — it slowly raises and lowers its crest while you wait, and hisses with its wings spread when the answer is no. |
| `art/sparrowanim` | Sparrow | A plump sparrow — it pecks up grains one by one while you wait, and turns its head away with a huff when the answer is no. |
| `art/crowtitanim` | Parrotbill | A rosy-cheeked parrotbill — it sways on the tip of a twig while you wait, and squeezes its eyes shut and shakes its head when the answer is no. |
| `art/shimaenagaanim` | Shimaenaga | A rice-cake-round Shimaenaga (long-tailed tit) — it fluffs up into a ball in the falling snow, and puffs up even more when cross. |
| `art/chickanim` | Chick | A chick in eggshell pants — it waddles along with the arrow on its head, and jumps with a cheep while you wait. |
| `art/ducklinganim` | Duckling | A flat-billed duckling — it bobs on the water while you wait, and opens wide for a big quack when the answer is no. |
| `art/canaryanim` | Canary | A yellow canary — it sways and sings while you wait, with little notes floating up. |
| `art/penguinanim` | Baby penguin | A grey baby penguin — it waddles across the ice, lifting one flipper and then the other. |

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
| `glow` | Neon | The theme's brightest colour bleeds out around the body; it glows on dark backgrounds. |
| `cutout` | Sticker | A thick white band around the body and a soft shadow, like a die-cut sticker; reads on any background. |
| `hollow` | Outline | Hollowed out to a thick ring with a bright rim, so it shows on dark backgrounds and keeps what is underneath readable. |
| `tube` | Neon tube | A thin hollow ring with light bleeding outward, like a neon sign letter; it glows on dark backgrounds. |
| `flat` | Flat | A single-colour vector with no shading, gloss or shadow — clean like a modern OS default. |
| `glass` | Glass | A see-through body with a bright rim, so whatever is underneath shows through. |
| `dart` | Arrowhead | A tail-less navigation arrow with a concave back — the one with a truly different outline. |
| `chunky` | Chunky | A wider body and tail, easy to spot on big or high-resolution screens. |

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
cursors.bat -Install -Scheme neonpulse,rainbowflow  :: register some (comma-separated)
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
python make_cur.py art/neonpulse/hand.txt out/hand.cur     # hotspot read from the txt
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
2. 페이지에서 구성표를 고르고 아래 띠의 **적용** → 확인 → 브라우저의 "앱 열기" 에서 열기
3. 이것저것 적용해 보다 질리면 **원래대로** — 이 페이지를 연 뒤 처음 적용하기 직전 커서로 돌아감
   - 예: 네온 맥박 적용 → 페이지 닫음 → 다시 열어 무지개 흐름 적용 → 원래대로 → 네온 맥박
   - 탭을 닫았다 열면 새로 셈. 같은 탭 새로고침은 이어짐
4. **포인터 설정 열기** — 윈도우 마우스 속성 창을 포인터 탭으로 엶
5. **커서 크기** (기본·1.5배·2배·3배·4배) — 고르면 페이지 커서가 바로 그 크기가 되고, 적용 버튼은 크기까지 같이 적용. 구성표는 두고 크기만 바꾸려면 **크기만 적용**
   - **색조** — 색상환을 0°~355° 돌림. 검정·흰색·회색은 그대로. 페이지 커서와 카드가 바로 바뀌고, 적용하면 `cursor-playground 네온 맥박 색조120` 같은 그 색의 새 구성표를 만듦
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

**해양 생물 · 애니**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/whalesharkanim` | 고래상어 | 헤엄치는 고래상어. 꼬리질과 입 벌림, 거품, 몸 위로 빛 물결이 지나가는 커서. |
| `art/dolphinanim` | 돌고래 | 헤엄치는 돌고래. 꼬리질과 거품, 몸 위로 빛 물결이 지나가는 커서. |
| `art/shrimpanim` | 새우 | 헤엄치는 새우. 꼬리질과 거품, 몸 위로 빛 물결이 지나가는 커서. |
| `art/pufferanim` | 복어 | 헤엄치는 복어. 꼬리질과 거품, 빛 물결이 지나가고 기다릴 때는 부풀었다 오그라드는 커서. |
| `art/molaanim` | 개복치 | 헤엄치는 개복치. 등·뒷지느러미를 번갈아 흔들고 몸 위로 빛 물결이 지나가는 커서. |
| `art/catsharkanim` | 괴상어 | 뱀장어처럼 S 자로 몸을 흔들며 헤엄치는 괴상어. 아가미에서 거품이 오르고 몸 위로 빛 물결이 지나가는 커서. |
| `art/bukanganim` | 부캉이 | 2026년 가을 부산 북항 수로에 열이틀 머문 상어. 회청색 등에 흰 배, 세모 등지느러미를 세우고 꼬리를 까딱이며 아가미에서 거품을 올리는 무태상어 커서. |
| `art/otteranim` | 해달 | 등을 대고 둥실 떠 있는 해달. 배 위 조개를 돌로 콩콩 두드리고, 거절할 때는 두 앞발로 얼굴을 가리는 커서. |
| `art/crabanim` | 꽃게 | 옆걸음 치는 꽃게. 집게를 들었다 벌렸다 하고 입에서 거품을 뽀글뽀글 올리는 커서. |
| `art/octopusanim` | 문어 | 동글동글한 치비 문어. 다리 여덟 개를 물결치듯 흔들고, 기다릴 때는 먹물을 퐁 뿜는 커서. |

**숲속 친구들 · 애니**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/squirrelanim` | 다람쥐 | 볼이 빵빵한 치비 다람쥐. 도토리를 볼에 넣었다 뺐다 오물거리고 큰 꼬리를 살랑이는 커서. |
| `art/hedgehoganim` | 고슴도치 | 밤송이 같은 치비 고슴도치. 콧등을 킁킁거리고, 거절할 때는 가시를 세운 채 공처럼 몸을 마는 커서. |
| `art/owlanim` | 부엉이 | 눈이 큰 치비 부엉이. 눈을 끔뻑이고, 모를 때는 고개를 빙글 갸웃하는 커서. |

**냥이 · 애니**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/cheesecatanim` | 치즈냥 | 통통한 치즈 고양이. 기다릴 때는 식빵을 굽고, 누를 때는 젤리 발바닥으로 꾹 누르는 커서. |
| `art/tuxedocatanim` | 턱시도냥 | 나비넥타이를 맨 턱시도 고양이. 꼬리를 곧게 세우고 새침하게 걷는 신사 커서. |
| `art/blackcatanim` | 까망이 | 노란 눈이 동그란 까만 고양이. 털실 공을 굴리며 놀고, 놀라면 털을 부풀려 하악하는 커서. |

**숲속 친구들 · 애니**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/rabbitanim` | 토끼 | 귀가 긴 치비 토끼. 코를 오물오물하고 긴 귀를 쫑긋 세웠다 접으며 깡총 뛰는 커서. |
| `art/foxanim` | 여우 | 꼬리가 복슬복슬한 치비 여우. 큰 꼬리를 살랑이고 귀를 기울여 듣다가 폴짝 뛰어드는 커서. |

**냥이 · 애니**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/mackerelcatanim` | 고등어냥 | 회색 줄무늬 고등어 고양이. 꼬리로 물음표를 그리고, 기다릴 때는 그루밍을 하는 커서. |
| `art/calicocatanim` | 삼색냥 | 흰 바탕에 주황·까만 얼룩 삼색 고양이. 꾹꾹이를 하고 상자에 쏙 들어가는 커서. |

**숲속 친구들 · 애니**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/bearanim` | 아기곰 | 동글동글한 치비 아기곰. 꿀단지에 손을 넣어 핥고 나무에 매달려 기지개를 켜는 커서. |
| `art/deeranim` | 아기사슴 | 흰 점박이 치비 아기사슴. 긴 다리로 껑충 뛰고 귀를 쫑긋 세우는 커서. |
| `art/raccoonanim` | 너구리 | 눈가에 까만 가면을 쓴 치비 너구리. 앞발로 열매를 비비 씻고 줄무늬 꼬리를 흔드는 커서. |
| `art/moleanim` | 두더지 | 분홍 코 치비 두더지. 흙더미에서 쏙 솟았다 숨고 큰 앞발로 땅을 파는 커서. |
| `art/froganim` | 개구리 | 연잎 위 초록 치비 개구리. 혀를 쭉 뻗어 콕 찍고 폴짝 뛰는 커서. |

**냥이 · 애니**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/siamesecatanim` | 샴냥 | 크림 몸에 얼굴·귀·발끝이 짙은 갈색인 파란 눈 샴 고양이. 꼬리를 물음표처럼 세우고 조잘대는 커서. |
| `art/russianbluecatanim` | 러시안블루 | 은회색 털에 초록 눈 러시안블루. 새침하게 앉아 있다가 낚싯대 장난감에 홀리는 커서. |
| `art/whitecatanim` | 오드아이 흰냥 | 파랑·노랑 짝짝이 눈의 새하얀 고양이. 우유를 할짝이고 햇살 아래 몸을 굴리는 커서. |
| `art/munchkincatanim` | 먼치킨 | 다리가 짧은 크림 줄무늬 먼치킨. 짧은 다리로 종종 뛰고 뒷발로 서서 미어캣처럼 두리번대는 커서. |
| `art/norwegiancatanim` | 노르웨이숲 | 갈기와 꼬리가 풍성한 장모 노르웨이숲 고양이. 복슬한 꼬리를 휘감고 나무를 타는 커서. |

**댕댕이 · 애니**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/shibaanim` | 시바 | 흰 볼에 눈썹 점이 있는 시바견. 화살표를 물고 와 말린 꼬리를 붕붕, 안 된다고 하면 네 발로 버티는 커서. |
| `art/corgianim` | 웰시코기 | 큰 귀를 쫑긋 세운 웰시코기. 기다릴 때는 뒤돌아 식빵 엉덩이를 씰룩, 안 될 때는 등 돌리고 흥 하는 커서. |
| `art/pomeraniananim` | 포메 | 솜털이 동그란 포메라니안. 기다릴 때는 제자리에서 빙글빙글 통통, 안 될 때는 털을 부풀리고 왈왈 짖는 커서. |
| `art/bichonanim` | 비숑 | 솜사탕 머리의 비숑. 기다릴 때는 솜머리를 통통 튀기고, 안 될 때는 도리도리하는 커서. |
| `art/retrieveranim` | 골든리트리버 | 깃털 꼬리의 골든리트리버. 기다릴 때는 혀 내밀고 헥헥, 안 될 때는 엎드려 촉촉한 눈으로 한숨 쉬는 커서. |
| `art/dachshundanim` | 닥스훈트 | 귀가 늘어진 긴 주둥이 닥스훈트. 기다릴 때는 엎드려 하품, 안 될 때는 코를 쳐들고 외면하는 커서. |
| `art/huskyanim` | 허스키 | 회색 가면에 파란 눈의 허스키. 기다릴 때는 고개 쳐들고 아우우, 안 될 때는 발라당 누워 허우적 항의하는 커서. |
| `art/poodleanim` | 푸들 | 곱슬 귀에 방울 꼬리의 푸들. 기다릴 때는 고개를 갸웃갸웃, 안 될 때는 콧대 높게 고개를 홱 돌리는 커서. |
| `art/malteseanim` | 말티즈 | 분홍 리본을 단 말티즈. 기다릴 때는 리본을 흔들며 꾸벅꾸벅 졸고, 안 될 때는 앞발로 눈을 가리는 커서. |
| `art/jindoanim` | 진돗개 | 뾰족 귀에 말린 꼬리의 진돗개. 기다릴 때는 똑바로 앉아 귀를 쫑긋 세우고, 안 될 때는 귀를 젖히고 으르렁하는 커서. |

**짹짹이 · 애니**

| 폴더 | 이름 | 스타일 |
|---|---|---|
| `art/javasparrowanim` | 문조 | 굵은 분홍 부리의 문조. 화살표를 머리에 이고 통통, 기다릴 때는 둥지에서 알을 품고 꾸벅꾸벅 조는 커서. |
| `art/budgieanim` | 사랑앵무 | 수다쟁이 사랑앵무. 기다릴 때는 거울을 보며 고개 까딱 수다, 안 될 때는 날개를 X 로 엇거는 커서. |
| `art/cockatielanim` | 왕관앵무 | 볏이 멋진 왕관앵무. 기다릴 때는 볏을 천천히 올렸다 내리고, 안 될 때는 볏을 세우고 날개를 쫙 펴 쉭쉭 하는 커서. |
| `art/sparrowanim` | 참새 | 통통한 참새. 기다릴 때는 땅의 모이를 하나씩 콕콕 쪼아 먹고, 안 될 때는 고개를 홱 돌리는 커서. |
| `art/crowtitanim` | 뱁새 | 볼이 발그레한 뱁새. 기다릴 때는 가지 끝에 앉아 가지째 살랑살랑, 안 될 때는 눈을 질끈 감고 도리도리하는 커서. |
| `art/shimaenagaanim` | 시마에나가 | 찹쌀떡 같은 시마에나가(흰머리오목눈이). 눈 오는 날 솜털을 부풀려 동그래지고, 화나면 더 빵빵해지는 커서. |
| `art/chickanim` | 병아리 | 알껍데기 바지를 입은 병아리. 화살표를 이고 뒤뚱뒤뚱, 기다릴 때는 삐약 점프하는 커서. |
| `art/ducklinganim` | 아기오리 | 넓적 부리 아기오리. 기다릴 때는 물에 둥둥 떠 있고, 안 될 때는 부리를 크게 벌려 꽥 하는 커서. |
| `art/canaryanim` | 카나리아 | 노란 카나리아. 기다릴 때는 고개를 흔들며 노래하고 음표가 솟는 커서. |
| `art/penguinanim` | 아기펭귄 | 회색 아기펭귄. 얼음판에서 지느러미를 번갈아 들며 뒤뚱뒤뚱 걷는 커서. |

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
| `glow` | 네온 | 몸 바깥으로 테마의 밝은 색이 번짐. 어두운 배경에서 특히 뜸. |
| `cutout` | 스티커 | 몸 바깥에 흰 띠를 굵게 두르고 옅은 그림자를 깖. 오려 낸 스티커처럼 어떤 배경에서도 뜸. |
| `hollow` | 테두리 | 속을 비우고 두꺼운 테만 남김. 테 둘레를 밝게 둘러 어두운 바탕에서도 보이고, 밑의 글자가 보임. |
| `tube` | 네온 튜브 | 가는 테만 남기고 바깥으로 빛을 번지게 함. 속이 빈 네온 간판 글자처럼 어두운 바탕에서 뜸. |
| `flat` | 플랫 | 음영·광택·그림자 없이 테마 색 그대로 칠한 단색 벡터. 요즘 OS 기본 커서 같은 깔끔함. |
| `glass` | 유리 | 몸은 반쯤 비치고 테만 밝게 빛남. 밑에 있는 글자가 비쳐 보임. |
| `dart` | 화살촉 | 꼬리 없이 네 점, 뒷면을 오목하게 판 내비 화살표. 윤곽부터 다른 단 하나. |
| `chunky` | 굵은 | 몸과 꼬리를 넓힌 화살표. 큰 화면이나 높은 해상도에서도 한눈에 찾음. |

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
cursors.bat -Install -Scheme neonpulse,rainbowflow  :: 개별 등록 (쉼표로 여러 개)
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
python make_cur.py art/neonpulse/hand.txt out/hand.cur     # 핫스팟은 txt 에서 읽음
python make_cur.py 내그림.png out/mine.cur --hotspot 0,0    # PNG (투명 배경, 256x256 이하)
```

### 파일 하나만 적용

1. 포인터 탭에서 칸 하나(예: 일반 선택) 선택 → **찾아보기** → .cur 고르기 → 확인
2. 되돌리려면 같은 창에서 **기본값 사용**

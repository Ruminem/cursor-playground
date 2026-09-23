# SPDX-License-Identifier: Apache-2.0
"""매끈한 커서 모양. 윤곽을 점으로 잡아 거리함수로 그리고, 테마 그림의 색을 입힌다.

픽셀아트 테마와 달리 이쪽은 경계가 매끈하다. 만드는 순서는 이렇다.

  1. 꼭지점마다 진짜 원호를 끼워 넣어 윤곽을 둥글린다 (면취가 아니라 호여야 둥글어 보인다)
  2. 부호 있는 거리함수로 칸마다 얼마나 덮였는지 재서 경계를 매끈하게 만든다
  3. 색은 넣지 않고 칸마다 "어느 층이 얼마나 덮였는지"만 남긴다 — 이것을 스텐실이라 부른다
  4. 테마마다 그 테마 그림에서 색을 떠 스텐실의 층에 끼워 넣는다 (paint)
  5. 높이장을 뭉개 기울기를 내고 그 법선으로 음영·광택·테빛을 얹는다. 세기는 구성표가 고른
     **재질**(MATERIALS)이 정한다 — 금속은 광택이 몸 색을 띠고, 유리는 속이 밝고 테가 빛난다

재질은 스텐실이 아니라 paint 쪽에 있다. 스텐실은 테마와 무관해야 구성표 전부가 한 벌을 나눠 쓰는데,
재질은 구성표마다 다르기 때문이다 (schemes.json 의 "material", 없으면 DEFAULT_MAT).

색은 몇 개로 줄이지 않고 **자리대로** 떠 온다 — 몸도 외곽선도 그렇다. 그래서 무늬
(표범·아가일)도, 프레임마다 무늬가 움직이는 테마(전기·글자비)도, 테두리를 타고 도는
효과(전기의 전류·글리치의 빨강청록 어긋남)도 모양만 바뀌고 성질은 남는다. 몸 바깥으로
번지는 빛(네온·야광)도 층마다 다시 둘러 준다.

커서 파일에 담는 크기는 늘리지 않고 **크기마다 새로 그린다**. 안티에일리어싱된 그림을
정수배로 늘리면 뭉개지기 때문이다. 담는 크기는 32·64·128 셋이고, 사이 크기(48·96)는
윈도우가 늘려 쓴다 — 매끈한 그림은 그래도 티가 안 난다. 시안 페이지에 넣는 그림도 같은
이유로 크게 그린다 (화살표 96칸, 나머지 64칸).
"""
import math
from collections import Counter

from make_cur import MIN_SIZE, curs_to_ani, pixels_to_png, pngs_to_cur

DESIGN = 26     # 설계 격자 높이. 실제 칸 수는 이 비율로 맞춘다
LIMIT = 20      # 32칸 판에서 몸이 차지하는 칸 수 (테마 그림들이 17~23칸이라 거기에 맞춤)
HALO = 3        # 테마의 몸 바깥 번짐을 다시 둘러 줄 층 수 (20칸 기준)
# 커서 파일에 담는 판 크기. 픽셀아트는 다섯 크기를 다 담지만(늘리면 어긋난다) 매끈한 그림은
# 윈도우가 사이 크기로 늘려도 티가 안 나서 셋만 담는다 — 파일이 38% 작아지고 빌드도 그만큼 빠르다
CUR_SIZES = (32, 64, 128)
PAGE = 96       # 시안 페이지의 화살표 판. 32칸 판의 3배라 썸네일이 1:1 로 쓴다
PAGE_SMALL = 64  # 나머지 칸은 페이지에서 작게 보여 주므로 판도 작게 (데이터 파일이 절반으로)
EDGE_W = 1.1    # 외곽선 두께 (설계 격자 기준, 32칸 판에서의 값)
EDGE_P = 0.72   # 외곽선이 판 크기를 따라 굵어지는 정도. 1 이면 비례해서 128px 에서 3.4px 가 되는데
                # 그러면 스티커 테처럼 보인다. 0.72 면 32px 0.9px · 128px 2.4px 로 큰 판에서 가늘어진다
# 몸 안쪽을 돔으로 보고 그 **높이장의 기울기**로 법선을 뽑는다. 반지름이 클수록 완만하고 통통해진다
DOME = 7.0
RELIEF = 1.0    # 돔이 얼마나 솟는지 (1 이면 꼭대기 높이 = DOME). 키우면 기울기가 서 음영이 깊어진다
BLUR = 0.30     # 높이장을 뭉갤 반지름 — **돔 반지름의 몇 배인지**로 적는다. **이 값이 접힘을 없앤다**:
                # 거리함수는 두 변이 똑같이 가까운 중심축에서 기울기가 뚝 끊기는데, 뭉갠 장의
                # 기울기는 이어진다. 출력 픽셀 기준으로 잡으면 큰 판에서 지붕이 그대로 남아
                # 능선에 1칸짜리 하이라이트 줄이 생긴다 (실측: 128칸에서 라플라시안 138).
                # 0 이면 예전처럼 접힌다. 크면 가장자리 각이 뭉개진다 (test_light.py 가 쌍으로 잰다)
LIGHT = (-0.42, -0.56, 0.71)   # 면에서 빛으로 가는 방향 (왼쪽 위에서 46° 로 비친다). 길이 1
SHINE = 28      # 하이라이트가 얼마나 좁은지 (블린퐁 지수). 재질은 세기만 바꾸고 이 값은 같이 쓴다 —
                # 좁기까지 재질마다 달리하면 스텐실을 재질 수만큼 구워야 한다
LAMB = 1.25     # 램버트를 평평한 면(0) 기준 -1..1 로 펼치는 배율. 크면 기울자마자 세게 갈린다
SHADE = 0.46    # 램버트 음영 세기. 아래 LIFT·SINK 와 곱해져 몸 색을 얼마나 올리고 내릴지 정한다
SPEC = 0.65     # 광택 세기. 재질의 spec 과 곱해진다
RIM = 0.55      # 테두리 빛 세기. 면이 눈에서 돌아선 만큼 밝아져 외곽선 바로 안쪽에 가는 띠가 생긴다
EDGE_LIT = 0.22   # 빛을 보는 쪽 외곽선을 하이라이트 색으로 얼마나 밀지
EDGE_LAMB = 0.35  # 빛을 등진 쪽 외곽선을 얼마나 누를지. 검은 테는 눌러도 그대로라 위쪽만 일한다
LIFT = 0.42     # 밝은 쪽에서 몸 색을 몇 배까지 올릴지 (1.42배)
SINK = 0.42     # 어두운 쪽에서 몸 색을 얼마나 내릴지 (0.58배)
QUANT = 8       # 명암·광택 계조를 몇 단계로 묶을지. 잘게 쪼갤수록 색과 파일이 는다
SHADOW = (0.6, 0.9)  # 접지 그림자를 오른쪽 아래로 밀어 놓는 양 (설계 격자)
SHADOW_A = 0.40  # 닿는 자리의 그림자 진하기. 멀어지면 아래 폭만큼 걸쳐 0 으로 사라진다
SHADOW_B = 2.2   # 그림자가 번지는 폭 (밀어 놓은 양의 배수). 크면 흐리고 멀리 퍼진다
PATTERN = 1.0   # 1 이면 칸을 영역으로 보고 섞는다. 0 이면 예전처럼 가까운 칸 하나를 그대로 쓴다
KEEP = 115      # 이웃이 이만큼(0~255, 채널 최대 차이) 넘게 다르면 **다른 영역**으로 가른다.
                # 크롬의 계조는 한 영역이라 이어 붙고, 쿠키의 초코칩·민트초코의 체크는 갈려서
                # 경계에 날이 선다. 115 는 눈으로 골랐다 — 60 은 색만 늘고 눈에는 차이가 없었다
UV = 127        # 테마 그림에서 색을 뜰 자리를 몇 단계로 쪼개 둘지. 영역 경계를 곡선으로 그려도
                # 이게 낮으면 그 곡선이 다시 UV 격자로 계단진다 — 가장 큰 판(128칸)에 맞춰 127.
                # 31 이던 것을 올렸고, 그리기가 30벌 기준 3.4 초에서 4.4 초가 됐다
TT = 255        # 테두리를 한 바퀴 도는 좌표를 몇 단계로 쪼갤지 (테두리가 가장 길어야 250칸쯤)
FPS = 30        # 0 이면 그림이 가진 프레임 그대로. >0 이면 프레임 사이를 섞어 이 fps 에 가깝게 늘린다.
                # 한 바퀴 도는 시간은 안 변한다 — 한 프레임이 머무는 틱을 쪼개 나눌 뿐이다 (steps 를 보라).
                # 프레임 수와 파일 크기는 그만큼 는다 (rate 4·5 면 2배, 6·7 이면 3배, 8 이면 4배)
SPECK = 5       # 몸에서 떨어져 나온 조각이 이 칸 수 이하면 불꽃으로 보고 새 몸 둘레에 다시 흩는다.
                # 2 였을 때 골드의 반짝이(5칸)가 몸에 합쳐져 옆구리에 혹 두 개가 났다. 5 는
                # 눈이 아니라 분포에서 골랐다 — 떨어진 덩어리 2,472개 중 97%가 5칸 이하이고
                # 6칸 위로는 73개뿐이다. 6 이상으로 올려도 `sum(조각)*8 > 몸` 마개가 나머지를
                # 잡아서 그림이 더 달라지지 않는다. 2 → 5 로 바뀌는 것은 gold 9칸 · sakura 5칸 ·
                # pencil 1칸, 121종 중 3종뿐 (2026-09-19 전수로 셈)
STRAND = 3      # 몸에 대각으로 닿은 조각이 이 칸 수 이상이면 '몸에서 뻗은 가닥'으로 보고 새 몸
                # 테두리에 다시 붙인다 (specks). 57종 실측으로 전기 가닥은 3~5칸, 나머지 구성표의
                # 닿은 조각은 1~2칸이라 이 선에서 갈린다 (2026-09-23)
BOLT_CORE = 0.45    # 가닥을 번개로 그릴 때 심의 반지름 (원본 한 칸 반지름의 배수). 1 이면 예전 막대
BOLT_GLOW = 1.6     # 심 둘레 빛 번짐의 반지름 (같은 배수)
BOLT_GLOW_A = 0.3   # 빛 번짐의 진하기
BOLT_JAG = 0.45     # 번개 꺾은선이 마디마다 옆으로 꺾이는 폭 (원본 한 칸 크기의 배수)
HANG = 254      # 이 알파로 칠한 칸은 '몸에 매달린 조각'이다 (용암 방울). 몸에 이어져 있어도 떼어 내고,
                # 새 몸에서는 매달린 몸 칸이 새 테두리에 오게 옮긴다 (specks). 눈으로는 불투명(255)과
                # 같다. 2026-09-23 57종 어디에도 이 알파가 없음을 보고 골랐다 — 다른 그림에 쓰면 뜯긴다
GHOST_R = 4    # 유령(몸을 통째로 옮긴 복사본)을 얼마나 멀리까지 찾아볼지 (테마 그림 칸)
GHOST_HIT = 0.75  # 옮긴 자리에서 몸과 이만큼 겹쳐야 유령으로 본다
GHOST_MIN = 6   # 이 칸 수보다 적으면 유령이 아니라 반짝이로 본다
GHOST_FILL = 0.30  # 옮겨서 드러난 칸을 평균 이만큼은 채워야 유령으로 본다

# 반각 벡터 (빛 + 시선). 시선은 화면 정면이라 (0,0,1) — 블린퐁 하이라이트가 이쪽을 본다
HALF = tuple(v / math.sqrt(sum(q * q for q in (LIGHT[0], LIGHT[1], LIGHT[2] + 1)))
             for v in (LIGHT[0], LIGHT[1], LIGHT[2] + 1))

# ── 재질 ─────────────────────────────────────────────────────────────────────
# 몸에 무슨 색이 오는지는 테마가 정하고, 여기서는 **빛을 어떻게 되받는지**만 정한다. 같은
# 크롬 그림이라도 금속이면 하이라이트가 좁고 세며 몸 색으로 물들고, 천이면 거의 안 번들거린다.
#   shade 음영 깊이 · spec 하이라이트 세기 · rim 테두리 빛 세기 · ambi 하늘빛 반사
#   ambi 는 빛을 보는 면에 넓게 얹는 옅은 빛이다. 검은 몸(잉크·게임보이)은 곱셈으로는 아무리
#   눌러도 검은색이라 이것이 없으면 납작해진다 — 실제로도 어두운 표면일수록 하늘빛이 눈에 띈다
#   tint  하이라이트 색을 테마의 가장 밝은 색(1) 과 흰색(0) 중 어디로 밀지.
#         흰색 쪽이라야 2색 테마(분홍·잉크)에서도 광택이 산다 — 거기선 '가장 밝은 색' 이 곧 몸 색이다
MATERIALS = {
    "plastic": dict(shade=1.00, spec=0.60, rim=0.30, tint=0.30, ambi=0.13),   # 기본. 매끈한 비닐·유광 플라스틱
    "metal":   dict(shade=1.25, spec=1.20, rim=0.75, tint=0.95, ambi=0.26),   # 크롬·금·은. 금속은 하이라이트가 몸 색을 띤다
    "glass":   dict(shade=0.55, spec=1.35, rim=1.00, tint=0.10, ambi=0.30),   # 유리·얼음·물. 속이 밝고 테가 빛난다
    "glow":    dict(shade=0.40, spec=0.30, rim=0.70, tint=1.00, ambi=0.16),   # 네온·야광·화면. 스스로 빛나 음영이 얕다
    "cloth":   dict(shade=0.85, spec=0.05, rim=0.55, tint=0.55, ambi=0.09),   # 천·털·종이. 번들거리지 않고 가장자리만 보송
}
# 무광(matte)은 뒀다가 뺐다. 플라스틱에서 광택만 죽인 것이라 차이의 천장이 플라스틱의 광택량인데,
# 재 보니 32px 에서 95분위 2.3~6.3 · 최대 10.0~14.7 로 눈에 안 걸렸다 (test_light.py 의 문턱은 8).
# 다시 넣으려면 광택이 아니라 **명암 곡선**이 달라야 한다 — shade 를 낮추고 ambi 를 올리는 쪽
DEFAULT_MAT = "plastic"

# ── 화살표 윤곽 (끝 · 어깨 · 오른쪽 홈 · 꼬리 둘 · 왼쪽 홈 · 굽) ──────────────
ARROW = [(1.3, 0.4), (19.8, 15.9), (13.6, 18.4), (17.0, 26.6), (10.4, 25.6), (8.6, 19.5), (0.2, 23.4)]
ARROW_R = [2.8, 2.0, 0.5, 1.5, 1.5, 0.5, 2.0]

# ── 화살표 말고 모양이 바꾸는 네 칸. 윤곽은 모양끼리 같이 쓰고, 칠하는 방식만 각자 따른다 ──
BAR = [(7.77, 20.77), (20.77, 7.77), (18.23, 5.23), (5.23, 18.23)]   # 금지 표시의 빗금
SLOTS = {
    "ibeam": [dict(pts=[(1.0, 0.0), (11.0, 0.0), (11.0, 2.4), (7.4, 2.4), (7.4, 23.6), (11.0, 23.6),
                        (11.0, 26.0), (1.0, 26.0), (1.0, 23.6), (4.6, 23.6), (4.6, 2.4), (1.0, 2.4)],
                   radii=[0.8] * 12, steps=4)],
    "wait": [dict(pts=[(1.0, 0.0), (19.0, 0.0), (19.0, 3.0), (11.6, 13.0), (19.0, 23.0), (19.0, 26.0),
                       (1.0, 26.0), (1.0, 23.0), (8.4, 13.0), (1.0, 3.0)],
                  radii=[1.2, 1.2, 0.8, 1.0, 0.8, 1.2, 1.2, 0.8, 1.0, 0.8], steps=5)],
    # 둥근 사각형에 반지름을 크게 주면 원이 된다. 고리로 비우고 빗금을 얹는다
    "no": [dict(pts=[(1.0, 1.0), (25.0, 1.0), (25.0, 25.0), (1.0, 25.0)], radii=[12.0] * 4, steps=9, ring=3.6),
           dict(pts=BAR, radii=[0.9] * 4, steps=4)],
    "move": [dict(pts=[(13.0, 0.4), (18.2, 5.6), (15.6, 5.6), (15.6, 10.4), (20.4, 10.4), (20.4, 7.8),
                       (25.6, 13.0), (20.4, 18.2), (20.4, 15.6), (15.6, 15.6), (15.6, 20.4), (18.2, 20.4),
                       (13.0, 25.6), (7.8, 20.4), (10.4, 20.4), (10.4, 15.6), (5.6, 15.6), (5.6, 18.2),
                       (0.4, 13.0), (5.6, 7.8), (5.6, 10.4), (10.4, 10.4), (10.4, 5.6), (7.8, 5.6)],
                  radii=[0.7] * 24, steps=3)],
}

# ── 모양 열 가지. 윤곽이 다른 것 여섯, 칠하는 방식이 다른 것 넷 ───────────────
# dome·shade·spec·shadow 를 안 적으면 위 기본값을 쓴다. 속이 비거나(hollow) 바깥으로
# 번지는(glow) 모양만 돔을 줄이고 그림자를 뺀다 — 얇은 테를 돔으로 깎으면 색이 남지 않고,
# 번짐 아래에 그림자를 깔면 둘이 섞여 탁해진다
SHAPES = {
    "round": dict(pts=ARROW, radii=ARROW_R, rscale=1.35, style="solid"),
    "hollow": dict(pts=ARROW, radii=ARROW_R, rscale=1.35, style="hollow", thick=3.4, dome=1.5, spec=0.6),
    "cutout": dict(pts=ARROW, radii=ARROW_R, rscale=1.35, style="sticker", band=1.8, shadow=(1.4, 2.0)),
    "blob": dict(pts=[(1.2, 0.3), (19.4, 15.8), (1.8, 25.0)], radii=[1.4, 3.0, 3.4], rscale=1.0, style="solid"),
    "comet": dict(pts=[(1.2, 0.4), (17.8, 14.2), (12.0, 16.2), (19.4, 27.4), (7.6, 18.2), (0.2, 21.6)],
                  radii=[2.6, 2.0, 0.6, 1.2, 0.6, 2.0], rscale=1.2, style="solid"),
    "needle": dict(pts=[(0.8, 0.3), (13.2, 15.0), (9.2, 16.4), (12.6, 26.0), (8.6, 26.6), (5.6, 18.0), (0.6, 22.4)],
                   radii=[1.7, 1.1, 0.3, 0.9, 0.9, 0.3, 1.1], rscale=1.3, style="solid"),
    "dart": dict(pts=[(0.8, 0.5), (19.9, 19.5), (10.2, 16.7), (7.7, 26.5)],
                 radii=[1.6, 1.6, 1.4, 1.6], rscale=1.15, style="solid"),
    "drop": dict(pts=[(1.2, 0.6), (17.0, 9.0), (19.0, 19.0), (11.0, 25.5), (2.0, 17.0)],
                 radii=[1.2, 6.0, 6.0, 6.0, 6.0], rscale=1.0, style="solid"),
    "glow": dict(pts=ARROW, radii=ARROW_R, rscale=1.35, style="solid", glow=3.2, shadow=(0, 0), spec=0.6),
    # 돔을 좁게 잡으면 완만한 언덕이 아니라 면취처럼 꺾여 보인다 — 이 모양은 그 꺾임이 요점이다
    "bevel": dict(pts=ARROW, radii=ARROW_R, rscale=1.0, style="solid", dome=2.6, shade=1.0, spec=1.0, ew=0.7),
}
ROLES = ("arrow",) + tuple(SLOTS)   # 모양이 직접 그리는 칸
# 층을 아래에서 위로 겹치는 순서. 한 칸 안에서 여러 층이 조금씩 겹칠 수 있다
ORDER = ("shadow", "halo0", "halo1", "halo2", "glow", "band", "body", "vol", "edge")
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = N4 + ((1, 1), (-1, -1), (1, -1), (-1, 1))
# 테두리를 돌 때 쓰는 여덟 이웃. N8 과 달리 **도는 차례**라야 한 바퀴를 놓치지 않는다
RING = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))


def cells_for(size: int) -> int:
    """커서 판 크기에 맞는 몸의 칸 수. 32칸 판에서 LIMIT 칸을 차지하는 비율을 지킨다"""
    return max(6, round(size * LIMIT / MIN_SIZE))


def _ss(cells: int) -> int:
    """몇 배 격자로 그릴지. 칸이 크면 거리함수만으로도 경계가 충분히 매끈하다"""
    return 3 if cells <= 24 else (2 if cells <= 48 else 1)


def edges_of(pts: list) -> list:
    """변마다 (시작점, 방향, 길이제곱의 역수). 칸마다 다시 계산하면 느려서 미리 만들어 둔다"""
    out = []
    for i in range(len(pts)):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
        dx, dy = x2 - x1, y2 - y1
        out.append((x1, y1, dx, dy, 1.0 / (dx * dx + dy * dy or 1e-9)))
    return out


def sdist(edges: list, px: float, py: float) -> tuple[float, float, float]:
    """윤곽선까지의 부호거리(안이 +)와 윤곽선 위의 가장 가까운 점.
    최근접 찾기와 안팎 판정이 같은 변 목록을 도므로 한 루프에서 같이 한다.
    제곱으로 비교하고 뿌리는 한 번만 뽑는다"""
    best, bx, by, ins = 1e18, px, py, False
    for x1, y1, dx, dy, inv in edges:
        if (y1 > py) != (y1 + dy > py) and px < dx * (py - y1) / dy + x1:
            ins = not ins
        t = ((px - x1) * dx + (py - y1) * dy) * inv
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
        cx, cy = x1 + t * dx, y1 + t * dy
        ex, ey = px - cx, py - cy
        d = ex * ex + ey * ey
        if d < best:
            best, bx, by = d, cx, cy
    d = math.sqrt(best)
    return (d if ins else -d), bx, by


def _blur(g: list, w: int, h: int, r: int) -> list:
    """높이장을 가로·세로로 한 번씩 뭉갠다. 가장자리는 바깥 값을 그대로 늘려 쓴다.

    **이 한 번이 접힘을 없앤다.** 거리함수는 두 변이 똑같이 가까운 자리(중심축)에서 기울기가
    뚝 끊겨, 거기서 뽑은 법선이 화살표 꼭지점마다 종이접기 같은 금을 냈다. 뭉갠 장은 그 끊김이
    2r 칸에 걸쳐 이어지므로 기울기가 연속이 된다. 누적합으로 밀어서 칸당 상수 시간이다"""
    n = 2 * r + 1
    tmp = [0.0] * (w * h)
    for y in range(h):
        row = y * w
        s = sum(g[row + min(w - 1, max(0, x))] for x in range(-r, r + 1))
        for x in range(w):
            tmp[row + x] = s / n
            s += g[row + min(w - 1, x + r + 1)] - g[row + max(0, x - r)]
    out = [0.0] * (w * h)
    for x in range(w):
        s = sum(tmp[min(h - 1, max(0, y)) * w + x] for y in range(-r, r + 1))
        for y in range(h):
            out[y * w + x] = s / n
            s += tmp[min(h - 1, y + r + 1) * w + x] - tmp[max(0, y - r) * w + x]
    return out


def fillet(pts: list, radii: list, steps: int = 6) -> list:
    """꼭지점마다 주어진 반지름의 원호를 윤곽선에 끼워 넣는다 (면취가 아니라 호)"""
    n = len(pts)
    out = []
    for i in range(n):
        a, b, c = pts[(i - 1) % n], pts[i], pts[(i + 1) % n]
        r = radii[i]
        v1, v2 = (a[0] - b[0], a[1] - b[1]), (c[0] - b[0], c[1] - b[1])
        l1, l2 = math.hypot(*v1) or 1, math.hypot(*v2) or 1
        u1, u2 = (v1[0] / l1, v1[1] / l1), (v2[0] / l2, v2[1] / l2)
        half = math.acos(max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1]))) / 2
        if r <= 0 or half < 0.08 or half > 1.5:
            out.append(b)
            continue
        cut = min(r / math.tan(half), l1 * 0.45, l2 * 0.45)
        r_eff = cut * math.tan(half)
        t1 = (b[0] + u1[0] * cut, b[1] + u1[1] * cut)
        t2 = (b[0] + u2[0] * cut, b[1] + u2[1] * cut)
        bis = (u1[0] + u2[0], u1[1] + u2[1])
        bl = math.hypot(*bis) or 1
        cen = (b[0] + bis[0] / bl * (r_eff / math.sin(half)), b[1] + bis[1] / bl * (r_eff / math.sin(half)))
        a1 = math.atan2(t1[1] - cen[1], t1[0] - cen[0])
        a2 = math.atan2(t2[1] - cen[1], t2[0] - cen[0])
        d = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for k in range(steps + 1):
            ang = a1 + d * k / steps
            out.append((cen[0] + math.cos(ang) * r_eff, cen[1] + math.sin(ang) * r_eff))
    return out


def parts_of(sid: str, rid: str) -> list[dict]:
    """모양·칸 하나를 이루는 부분들. 칸의 윤곽에 그 모양의 칠하는 방식을 붙인다"""
    spec = SHAPES[sid]
    raw = [dict(pts=spec["pts"], radii=spec["radii"], steps=6)] if rid == "arrow" else SLOTS[rid]
    parts = []
    for part in raw:
        p = dict(part)
        p["radii"] = [r * spec["rscale"] for r in p["radii"]]
        # 금지 표시의 고리는 어느 모양에서든 비워야 금지 표시로 읽힌다
        if spec["style"] == "hollow" and "ring" not in p and rid != "no":
            p["ring"] = spec["thick"]
        parts.append(p)
    return parts


def outlines(sid: str, rid: str, size: float) -> tuple[list, float]:
    """이 크기로 그린 윤곽선들과, 그것이 차지하는 칸 수 (긁지 않고 계산한다)"""
    k = size / DESIGN
    grown = []
    lo = [1e9, 1e9]
    hi = [-1e9, -1e9]
    for part in parts_of(sid, rid):
        pts = fillet([(x * k, y * k) for x, y in part["pts"]],
                     [r * k for r in part["radii"]], part.get("steps", 6))
        grown.append((part, pts))
        for x, y in pts:
            lo[0], lo[1] = min(lo[0], x), min(lo[1], y)
            hi[0], hi[1] = max(hi[0], x), max(hi[1], y)
    spec = SHAPES[sid]
    pad = k * max(spec.get("band", 0) + max(spec.get("shadow", (0, 0))), spec.get("glow", 0))
    return grown, max(hi[0] - lo[0], hi[1] - lo[1]) + 2 * pad


_cache: dict = {}


def stencil_keys() -> list[tuple[str, str, int]]:
    """빌드가 쓰는 스텐실 전부의 키 — 커서 세 크기·기본 칸 수·시안 판. build.py 가 이걸 먼저 병렬로
    굽고 워커들이 나눠 쓴다 (2026-09-20: 워커마다 굽던 때는 430번 중 270번이 같은 것을 다시 굽는 것이었다)"""
    common = {cells_for(s) for s in CUR_SIZES} | {LIMIT}
    return [(sid, rid, c) for sid in SHAPES for rid in ROLES
            for c in sorted(common | {cells_for(PAGE if rid == "arrow" else PAGE_SMALL)})]


def stencil(sid: str, rid: str, cells: int = LIMIT) -> tuple[tuple[dict, list], tuple[int, int], tuple, set]:
    """모양·칸 하나의 (스텐실, 핫스팟, 몸이 놓인 자리, 몸이 덮은 칸). 테마와 무관해 한 번만 그린다"""
    rid = rid if rid in ROLES else "arrow"   # 기호를 얹는 칸(도움말·백그라운드 작업 등)은 화살표를 쓴다
    key = (sid, rid, cells)
    if key not in _cache:
        size = DESIGN
        for _ in range(3):   # 한 번 재면 비례해서 맞출 수 있다. 반올림 때문에 여유를 조금 둔다
            _, span = outlines(sid, rid, size)
            size *= (cells - 0.7) / span
            if abs(span - (cells - 0.7)) < 0.3:
                break
        _cache[key] = _draw(sid, rid, size, cells)
    return _cache[key]


def _draw(sid: str, rid: str, size: float, cells: int) -> tuple[tuple[dict, list], tuple[int, int], tuple, set]:
    spec = SHAPES[sid]
    k = size / DESIGN
    ss = _ss(cells)
    parts, _ = outlines(sid, rid, size)
    # 외곽선은 판 크기를 따라 **덜** 굵어진다 (EDGE_P). 비례해서 굵히면 큰 판에서 스티커 테가 된다
    ew = EDGE_W * spec.get("ew", 1.0) * k ** EDGE_P
    dome = spec.get("dome", DOME) * k
    shade = spec.get("shade", 1.0)
    gloss_k = spec.get("spec", 1.0)
    band = spec.get("band", 0) * k
    glow = spec.get("glow", 0) * k
    halo = HALO * cells / LIMIT                      # 테마 번짐 층도 크기에 맞춰 두꺼워진다
    sh_dx, sh_dy = (q * k for q in spec.get("shadow", SHADOW))
    pad = max(band + max(sh_dx, sh_dy), glow, halo) + 1
    x0 = min(x for _, pts in parts for x, _ in pts) - pad
    y0 = min(y for _, pts in parts for _, y in pts) - pad
    x1 = max(x for _, pts in parts for x, _ in pts) + pad
    y1 = max(y for _, pts in parts for _, y in pts) + pad
    W, H = math.ceil(x1 - x0), math.ceil(y1 - y0)
    sblur = max(sh_dx, sh_dy) * SHADOW_B + 0.5 * k   # 그림자가 번지는 폭
    acc: dict = {}
    body_cells = set()
    SW, SH = W * ss, H * ss
    hgt = [0.0] * (SW * SH)                          # 돔의 높이장. 여기서 기울기로 법선을 뽑는다
    faces: list = []                                 # (격자 번호, 칸, 무게, 세로 위치, 외곽선인가)

    def add(cell, kind, a, t=0.0, k2=0.0, k3=0.0, k4=0.0):
        got = acc.setdefault(cell, {}).setdefault(kind, [0.0, 0.0, 0.0, 0.0, 0.0])
        got[0] += a
        got[1] += t * a
        got[2] += k2 * a
        got[3] += k3 * a
        got[4] += k4 * a

    for part, pts in parts:
        edges = edges_of([(x - x0, y - y0) for x, y in pts])
        ring = part.get("ring", 0) * k
        for sy in range(SH):
            py = (sy + 0.5) / ss
            for sx in range(SW):
                px = (sx + 0.5) / ss
                cell = (sx // ss, sy // ss)
                w = 1 / (ss * ss)
                sd = sdist(edges, px, py)[0]
                # 몸이 덮은 자리와, 거기서 얼마나 떨어졌는지. 고리면 안쪽 구멍도 바깥으로 센다
                far = ring or 1e9
                gap = 0.0 if 0 <= sd <= far else (-sd if sd < 0 else sd - far)
                # 경계에 걸친 칸은 부호거리로 덮인 만큼만 센다 (이것이 안티에일리어싱)
                frac = min(1.0, max(0.0, sd * ss + 0.5))
                if ring:
                    frac = min(frac, min(1.0, max(0.0, (far - sd) * ss + 0.5)))
                if 0 < gap <= halo:
                    add(cell, f"halo{min(HALO - 1, int(gap / halo * HALO))}", w)
                if glow and 0 < gap < glow:
                    g = 1 - gap / glow
                    add(cell, "glow", w * g * g * 0.65)
                if band and 0 < gap < band:
                    add(cell, "band", w * min(1.0, max(0.0, (band - gap) * ss + 0.5)))
                if sh_dx or sh_dy:
                    sdsh = sdist(edges, px - sh_dx, py - sh_dy)[0]
                    if sdsh > -0.55 * sblur and (not ring or sdsh <= far):
                        # 밀어 놓은 실루엣을 한 가지 농도로 통째로 깔면 오려 붙인 그림자가 된다.
                        # 경계를 sblur 폭에 걸쳐 풀어 반그림자를 만들고, 닿는 쪽이 제일 진하다
                        add(cell, "shadow", w * SHADOW_A * min(1.0, sdsh / sblur + 0.55) ** 1.7)
                if frac <= 0:
                    continue
                w *= frac
                if frac > 0.5:
                    body_cells.add(cell)
                t = min(1.0, py / H * 1.25 + px / W * 0.25)      # 빛은 왼쪽 위에서
                idx = sy * SW + sx
                if sd < ew or (ring and sd > far - ew):
                    faces.append((idx, cell, w, t, True))         # 외곽선도 벽이라 빛을 받는다
                else:
                    # 외곽선 안쪽을 돔으로 본다. 꼭대기가 dome 만큼 솟은 언덕을 높이장에 쌓아 두고,
                    # 법선은 그 장을 뭉갠 뒤 **기울기로** 뽑는다 (아래 두 번째 바퀴).
                    # 고리는 안쪽 구멍 쪽에서도 다시 떨어지므로 가까운 쪽 벽까지의 거리를 쓴다
                    inner = min(sd - ew, far - ew - sd) if ring else sd - ew
                    q = min(1.0, inner / dome) if dome > 0 else 1.0
                    h = RELIEF * dome * math.sin(q * math.pi / 2)
                    if h > hgt[idx]:                              # 부품이 겹치면 높은 쪽이 이긴다
                        hgt[idx] = h
                    faces.append((idx, cell, w, t, False))

    # ── 두 번째 바퀴: 높이장 → 법선 → 빛 ────────────────────────────────────
    # 높이장을 한 번 뭉개고 중앙차분으로 기울기를 잡는다. 예전에는 '가장 가까운 윤곽선 점을 향한
    # 방향' 을 법선으로 썼는데, 그 방향은 두 변이 똑같이 가까운 자리에서 뚝 끊겨 꼭지점마다
    # 종이접기 같은 금이 갔다. 뭉갠 장의 기울기는 이어져 있어 금이 원리적으로 안 생긴다
    if faces:
        rb = round(BLUR * dome * ss)
        hg = _blur(hgt, SW, SH, rb) if rb >= 1 else hgt      # BLUR=0 이면 예전처럼 접힌다 (견주려고 둔 길)
        gs = ss / 2.0                                    # 한 칸이 1/ss 이라 중앙차분의 분모가 2/ss
        lx, ly, lz = LIGHT
        hx, hy, hz = HALF
        for idx, cell, w, t, is_edge in faces:
            sx, sy = idx % SW, idx // SW
            gx = (hg[idx + 1] if sx + 1 < SW else hg[idx]) - (hg[idx - 1] if sx else hg[idx])
            gy = (hg[idx + SW] if sy + 1 < SH else hg[idx]) - (hg[idx - SW] if sy else hg[idx])
            nx, ny = -gx * gs, -gy * gs
            nn = math.sqrt(nx * nx + ny * ny + 1.0)
            nx, ny, nz = nx / nn, ny / nn, 1.0 / nn
            # 램버트는 평평한 면이 0 이 되게 옮기고, 위아래를 **따로** 1 에 맞춘다. 그냥 빼기만
            # 하면 빛 쪽으로는 1-lz 만큼밖에 못 가고 등지는 쪽으로는 1+lz 만큼 가서, 어두운 쪽만
            # 포화되고 밝은 쪽은 거의 안 움직인다 (실측: 왼쪽 위 +0.3 대 오른쪽 아래 -20)
            dv = nx * lx + ny * ly + nz * lz - lz
            dl = dv / (1 - lz) if dv > 0 else dv / (1 + lz)
            dl = max(-1.0, min(1.0, dl * LAMB * shade))
            ndh = nx * hx + ny * hy + nz * hz             # 블린퐁: 좁은 하이라이트
            hi = (ndh ** SHINE if ndh > 0 else 0.0) * gloss_k
            # 테두리 빛은 면이 눈에서 돌아선 만큼. 빛을 등진 쪽을 더 세게 해야 테를 돌려 준다
            rm = (1.0 - nz) ** 3 * (0.35 + 0.65 * max(0.0, -dl)) * gloss_k
            if is_edge:
                add(cell, "edge", w, 0.0, (dl + 1) / 2)
            elif abs(dl) < 0.03 and hi < 0.02 and rm < 0.02:
                add(cell, "body", w, t)                   # 가운데 평평한 곳은 한 가지로 묶는다
            else:
                add(cell, "vol", w, t, (dl + 1) / 2, min(1.0, hi), min(1.0, rm))

    made = {}
    for cell, kinds in acc.items():
        layers = []
        for kind in ORDER:
            if kind not in kinds:
                continue
            a, ta, ka, ha, ra = kinds[kind]
            if a < 0.02:
                continue
            # 계조를 잘게 쪼개면 색이 수백 개씩 생긴다. 눈에 안 보일 만큼만 묶는다
            layers.append((kind, round(ta / a * 12) / 12, round(ka / a * QUANT) / QUANT,
                           round(ha / a * QUANT) / QUANT, round(ra / a * QUANT) / QUANT,
                           round(min(1.0, a) * 24) / 24))
        if layers:
            made[cell] = tuple(layers)
    # 왼쪽 위를 (0,0) 으로 당긴다
    ox = min(x for x, _ in made)
    oy = min(y for _, y in made)
    body = {(x - ox, y - oy) for x, y in body_cells}
    bx0, by0 = min(x for x, _ in body), min(y for _, y in body)
    box = (bx0, by0, max(x for x, _ in body) - bx0 + 1, max(y for _, y in body) - by0 + 1)
    # 칸마다 (칠하는 방법 번호, 테마 그림에서 색을 뜰 자리)만 남긴다. 같은 값이면 색을 한 번만
    # 계산하고 돌려 쓰므로, 큰 판에서도 색 계산이 몇백 번으로 끝난다
    recipes: dict = {}
    st = {}
    cells = [(x - ox, y - oy) for x, y in made]
    arc = arc_of(body, (min(x for x, _ in cells), min(y for _, y in cells),
                        max(x for x, _ in cells), max(y for _, y in cells)))
    for (x, y), layers in made.items():
        cx, cy = x - ox, y - oy
        iu = min(UV, max(0, round((cx - bx0) / max(1, box[2] - 1) * UV)))
        iv = min(UV, max(0, round((cy - by0) / max(1, box[3] - 1) * UV)))
        st[(cx, cy)] = (recipes.setdefault(layers, len(recipes)), iu, iv, arc.get((cx, cy), 0))
    return (st, [k for k, _ in sorted(recipes.items(), key=lambda kv: kv[1])]), _hotspot(body, rid), box, body


def _hotspot(body: set, rid: str) -> tuple[int, int]:
    """화살표는 끝, 나머지는 가운데"""
    if rid != "arrow":
        xs = [x for x, _ in body]; ys = [y for _, y in body]
        return (min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2
    ty = min(y for _, y in body)
    return min(x for x, y in body if y == ty), ty


def mix(a: tuple, b: tuple, t: float) -> tuple:
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def over(bot: tuple | None, top: tuple) -> tuple:
    # 칸마다 층마다 불리는 자리라 제너레이터를 펴 뒀다 (300만 번에 57% 차이가 났다).
    # 곱셈 차례와 나눗셈은 건드리지 않는다 — bot*ba*f 를 bot*(ba*f) 로 묶거나 /outa 를
    # 역수 곱셈으로 바꾸면 반올림 경계에서 값이 갈려 실제로 그림이 달라졌다
    if bot is None:
        return top
    ta, ba = top[3] / 255, bot[3] / 255
    outa = ta + ba * (1 - ta)
    if outa <= 0:
        return (0, 0, 0, 0)
    f = 1 - ta
    return (round((top[0] * ta + bot[0] * ba * f) / outa),
            round((top[1] * ta + bot[1] * ba * f) / outa),
            round((top[2] * ta + bot[2] * ba * f) / outa),
            round(outa * 255))


def ring_of(mask) -> set:
    return {(x + dx, y + dy) for (x, y) in mask for dx, dy in N8} - set(mask)


def nearest(points: set, box: tuple) -> dict:
    """box 안 모든 칸에서 가장 가까운 points 원소 (가장자리에서 안쪽으로 번져 나가며 찾는다)"""
    x0, y0, x1, y1 = box
    best = {p: p for p in points}
    frontier = list(points)
    while frontier:
        nxt = []
        for p in frontier:
            for dx, dy in N8:
                q = (p[0] + dx, p[1] + dy)
                if x0 - 1 <= q[0] <= x1 + 1 and y0 - 1 <= q[1] <= y1 + 1 and q not in best:
                    best[q] = best[p]
                    nxt.append(q)
        frontier = nxt
    return best


def _regions(fill: dict) -> dict:
    """대비가 KEEP 아래인 이웃끼리 묶은 영역 번호.

    크롬의 계조는 전부 한 덩어리가 되고(가운데를 부드럽게 이어도 되는 자리), 쿠키의 초코칩과
    민트초코의 체크는 따로 떨어진다(날을 세워야 하는 자리). 칸을 네모로 두지 않고 영역으로
    보면 경계를 칸 모서리가 아니라 곡선으로 다시 그릴 수 있다."""
    reg: dict = {}
    n = 0
    for start in fill:
        if start in reg:
            continue
        reg[start] = n
        stack = [start]
        while stack:
            p = stack.pop()
            for dx, dy in N4:
                q = (p[0] + dx, p[1] + dy)
                if q in fill and q not in reg and max(abs(fill[p][i] - fill[q][i]) for i in range(3)) <= KEEP:
                    reg[q] = n
                    stack.append(q)
        n += 1
    return reg


def biggest(body: set) -> set:
    """8-이웃으로 이어진 조각 중 가장 큰 것. 떨어진 꽃잎 한 점에서 테두리를 돌지 않게"""
    rest, best = set(body), set()
    while rest and len(rest) > len(best):
        blob, stack = set(), [rest.pop()]
        while stack:
            x, y = stack.pop()
            blob.add((x, y))
            for dx, dy in N8:
                q = (x + dx, y + dy)
                if q in rest:
                    rest.discard(q)
                    stack.append(q)
        if len(blob) > len(best):
            best = blob
    return best


def cycle_of(body: set) -> list:
    """몸 테두리를 한 바퀴 도는 차례. 가장 큰 조각의 윗줄 왼쪽 칸에서 시작해 늘 같은 쪽으로 돈다.

    네모 안의 상대 위치로 외곽선 색을 뜨면 테두리 길이가 보존되지 않아, 원본 테두리의 어떤 칸은
    여러 번 뽑히고 어떤 칸은 한 번도 안 뽑힌다. 테두리를 타고 도는 무늬(전기의 전류)가 그래서
    빠진다. 한 바퀴 도는 차례를 매겨 같은 비율 자리끼리 맞추면 빠지는 칸이 없다.

    도는 차례는 **순서**만 쓴다. 대각선 계단에서는 한 칸씩 건너뛰므로 여기서 나온 칸만 색 재료로
    쓰면 테두리의 1/3 이 빠진다 — 색은 테두리 전체에서 뜨고 순서만 이걸로 물려준다."""
    body = biggest(body)
    if not body:
        return []
    start = min(body, key=lambda p: (p[1], p[0]))
    out, cur, d = [start], start, 0
    for _ in range(8 * len(body)):
        for k in range(8):
            i = (d + 5 + k) % 8                # 직전에 온 쪽부터 한 바퀴 훑어 처음 만나는 몸으로
            nxt = (cur[0] + RING[i][0], cur[1] + RING[i][1])
            if nxt in body:
                cur, d = nxt, i
                break
        else:
            break
        if cur == start:
            break
        out.append(cur)
    return out


def around(body: set, rim: set) -> list:
    """테두리 칸 전부를 한 바퀴 도는 차례로 늘어놓는다. 도는 차례가 건너뛴 칸은 가장 가까운
    돈 칸의 자리를 물려받는다 — 색 재료가 테두리 전체라서 빠지는 색이 없다"""
    order = cycle_of(body)
    if not order:
        return sorted(rim)
    at = {p: i for i, p in enumerate(order)}
    xs = [x for x, _ in rim]; ys = [y for _, y in rim]
    near = nearest(set(order), (min(xs), min(ys), max(xs), max(ys)))
    return sorted(rim, key=lambda p: (at[near[p]], p))


def arc_of(body: set, box: tuple) -> dict:
    """box 안 모든 칸에 '테두리 한 바퀴 중 어디쯤'(0~TT)을 매긴다. 테두리에서 떨어진 칸은
    가장 가까운 테두리 칸의 값을 쓴다 — 조각이 여럿인 그림에서도 빈 칸이 안 남는다"""
    order = cycle_of(body)
    n = len(order)
    t = {p: round(i / n * TT) % (TT + 1) for i, p in enumerate(order)}
    return {q: t[p] for q, p in nearest(set(order), box).items()}


def blobs_of(solid) -> list[set]:
    """이어진 덩어리들 (큰 것부터). 대각선은 안 잇는다 — 이어 버리면 몸에 닿은 불꽃까지 몸이 된다"""
    left, out = set(solid), []
    while left:
        cur = {left.pop()}
        frontier = list(cur)
        while frontier:
            nxt = []
            for x, y in frontier:
                for dx, dy in N4:
                    q = (x + dx, y + dy)
                    if q in left:
                        left.discard(q)
                        cur.add(q)
                        nxt.append(q)
            frontier = nxt
        out.append(cur)
    return sorted(out, key=len, reverse=True)


def specks_of(solid: dict, box: tuple | None = None) -> tuple[list, dict]:
    """몸에서 떨어져 나온 작은 조각(전기 불꽃·눈송이·꽃잎)을 몸과 갈라 놓는다.

    자리는 몸 테두리 기준 비율로 남긴다. 몸을 새로 그려도 같은 자리에 흩을 수 있다.
    큰 조각이 하나라도 있으면 그 그림은 원래 끊어 그린 것(손그림·점선)이라 보고 건드리지 않는다.

    **조각마다 따로 묶어 넘긴다.** 여러 칸이 이어진 조각(전기의 가닥)은 그릴 때 점 사이를
    채워야 선으로 보이는데, 한 줄로 쏟아 놓으면 어느 칸이 같은 조각이었는지 알 수 없다.

    box 를 주면 비율을 그 네모(x0, y0, x1, y1)로 잰다. 프레임 묶음에서는 **모든 프레임에 공통인
    몸**의 네모를 준다 — 용암 방울이 끝에 붙어 몸이 한두 칸 길어지는 프레임마다 그 장의 몸으로
    재면, 같은 때 떨어지고 있는 다른 방울의 비율이 바뀌어 위로 튄다.

    **알파가 HANG 인 칸은 몸에 이어져 있어도 따로 뗀다** (용암 방울). 몸에 붙은 채로 두면 매끈한
    모양에서는 몸의 일부라 안 보이고, 떨어진 뒤에야 커서 밖 허공에서 나타났다."""
    hang = {p for p, c in solid.items() if c[3] == HANG}
    keep = {p: c for p, c in solid.items() if p not in hang} if hang else solid
    parts = blobs_of(keep)
    rest = parts[1:]
    ok = bool(rest) and not any(len(b) > SPECK for b in rest) and sum(len(b) for b in rest) * 8 <= len(parts[0])
    if not ok and not hang:
        return [], solid
    body = parts[0] if ok else set(keep)           # 불꽃으로 못 보면 조각은 예전처럼 몸에 둔다
    core = parts[0]
    if box is None:
        xs = [x for x, _ in core]; ys = [y for _, y in core]
        box = (min(xs), min(ys), max(xs), max(ys))
    x0, y0 = box[0], box[1]
    w, h = max(1, box[2] - x0), max(1, box[3] - y0)
    near = {(x + dx, y + dy) for x, y in core for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    specks = []
    for b in rest if ok else []:
        g = Bunch(((x - x0) / w, (y - y0) / h, solid[(x, y)]) for x, y in b)
        g.step = (1 / w, 1 / h)                    # 원본 한 칸이 u·v 로 얼마인지 (이웃 판정용)
        # 몸 모서리에 대각으로 닿은 채 뻗어 나간 가닥 (STRAND). 짧은 조각은 안 센다 — 눈송이
        # 한 점은 떨어지다 몸을 한 프레임 스칠 뿐이라, 붙이면 낙하 궤적이 그 프레임만 튄다
        g.touch = len(b) >= STRAND and any(p in near for p in b)
        specks.append(g)
    for b in blobs_of({p: solid[p] for p in hang}) if hang else []:
        g = Bunch(((x - x0) / w, (y - y0) / h, solid[(x, y)]) for x, y in b)
        g.step = (1 / w, 1 / h)
        # 매달린 자리 — 조각 맨 윗칸 바로 위의 몸 칸. 조각이 그 칸에 바로 붙어 있었는지도 적는다
        tx, ty = min(b, key=lambda p: (p[1], p[0]))
        above = [y for x, y in core if x == tx and y < ty]
        ax, ay = (tx, max(above)) if above else min(core, key=lambda p: (p[0] - tx) ** 2 + (p[1] - ty) ** 2)
        g.hang = ((ax - x0) / w, (ay - y0) / h, ty - ay == 1 and ax == tx)
        specks.append(g)
    return specks, {p: solid[p] for p in body}


class Bunch(list):
    """불꽃 한 조각의 칸들 (u, v, 색). 원래 몸에서 뻗어 나간 가닥인지, 몸 어디에 매달린 조각인지,
    원본 한 칸의 크기를 같이 들고 다닌다 — 가닥(전기의 방전)과 방울(용암)은 새 몸에서도 테두리에
    붙여야 몸에서 튀고 몸에서 떨어지는 것으로 읽힌다"""
    touch = False
    step = None
    hang = None                                    # (u, v, 바로 붙어 있었나) — 매달린 몸 칸


def _ring_at(got: dict, n: int):
    """번짐 층 하나에서 자리로 색을 뜨는 함수. 그 자리 가까이에 아무것도 없으면 비워 둔다 —
    이 마개가 없으면 한쪽에만 번진 층이 nearest 를 타고 반대쪽까지 칠해진다.

    마개는 **대각선도 한 칸으로 세는 거리**(체비쇼프)로 잰다. 층(ring_of)도 nearest 도 8방향으로
    번지니 같은 자로 재야 한다. 예전엔 여기만 유클리드라, 매끈한 대각선이 원본의 계단을 가로지르는
    자리에서 계단 안쪽 모서리가 (2,2)·(1,2) 떨어져 마개(2)에 걸렸다 — 안쪽 번짐이 한 칸씩 비어
    대각선 테두리에 톱니가 났다 (2026-09-24 네온 맥박에서, 번짐 있는 구성표 9종 모두)"""
    xs = [x for x, _ in got]; ys = [y for _, y in got]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    found = nearest(set(got), (x0, y0, x1, y1))
    cap = n + 2

    def at(u: float, v: float) -> tuple | None:
        p = (round(x0 + u * (x1 - x0)), round(y0 + v * (y1 - y0)))
        q = found.get(p)
        return got[q] if q and max(abs(q[0] - p[0]), abs(q[1] - p[1])) <= cap else None

    return at


def _rings(core: set) -> list[set]:
    """몸 바깥 층들의 자리. 프레임과 무관하므로 묶음마다 한 번만 만든다"""
    out, grown = [], set(core)
    for _ in range(HALO):
        r = ring_of(grown)
        grown |= r
        out.append(r)
    return out


def _lit(rings: list[set], frames: list[dict]) -> list[bool]:
    """번짐으로 볼 층. 가장 많이 찬 프레임이 반을 넘으면 그 층을 산 것으로 본다.

    층이 살아 있으면 덜 찬 프레임은 찬 자리만 칠해져서 번짐이 프레임마다 늘었다 줄었다 한다.
    프레임마다 따로 재면 잔상이 얇아지는 프레임에서 통째로 사라져 깜빡인다."""
    return [bool(r) and any(len([p for p in r if p in f]) * 2 >= len(r) for f in frames) for r in rings]


def _outward(frame: dict, rings: list[set], lit: list[bool]) -> list:
    """이 프레임의 번짐 층들 (층마다 자리로 색을 뜨는 함수, 없으면 None)"""
    out = []
    for n, r in enumerate(rings):
        got = {p: frame[p] for p in r if p in frame} if lit[n] else {}
        out.append(_ring_at(got, n) if got else None)
    return out


def _slide(pts: set, core: set) -> tuple:
    """이 색 칸들이 몸을 얼마나 옮긴 것에 가장 가까운지 — ((일치, dx, dy), 안 옮겼을 때의 일치)"""
    n = len(pts)
    at0 = sum(1 for p in pts if p in core) / n
    best = (at0, 0, 0)
    for dx in range(-GHOST_R, GHOST_R + 1):
        for dy in range(-GHOST_R, GHOST_R + 1):
            hit = sum(1 for x, y in pts if (x - dx, y - dy) in core) / n
            if hit > best[0]:
                best = (hit, dx, dy)
    return best, at0


def _steady(offs: list) -> bool:
    """옮긴 방향의 부호가 한쪽으로만 가는지. 0 은 어느 쪽으로도 세지 않는다"""
    return all(len({v > 0 for v in vals if v}) <= 1 for vals in zip(*offs))


def ghosts_of(frames: list[dict], core: set) -> list[list]:
    """프레임마다 '몸을 통째로 옮긴 복사본'인 색을 찾는다 — [(색, 가로 비율, 세로 비율), ...]

    색맞춤 어긋남(글리치)처럼 같은 실루엣이 옆으로 밀리는 효과는 색을 자리대로 떠서는 살아나지
    않는다. 효과가 색이 아니라 **옮김**이라, 고정된 스텐실에 칠하면 방향이 사라지고 번짐으로
    뭉개진다. 잡으면 새 몸을 그만큼 옮겨 밑에 깔 수 있다.

    불꽃·눈송이와 가르는 기준은 **과반 프레임에서 잡히고 방향의 부호가 일정한지**다. 반짝이는
    한두 장에서 아무 쪽으로나 걸리므로 둘을 같이 보면 떨어진다 (121종에 돌려 글리치만 남았다)."""
    if len(frames) < 2:
        return [[] for _ in frames]
    found: dict = {}                           # 색 → {프레임 번호: (dx, dy)}
    for i, f in enumerate(frames):
        groups: dict = {}
        for p, c in f.items():
            groups.setdefault(c, set()).add(p)
        for c, pts in groups.items():
            if len(pts) < GHOST_MIN or len(pts & core) * 10 >= len(pts) * 9:
                continue                       # 이미 거의 다 몸 안이면 몸이지 유령이 아니다
            (hit, dx, dy), at0 = _slide(pts, core)
            if not ((dx or dy) and hit >= GHOST_HIT and hit - at0 >= 0.15):
                continue
            # 옮겨서 드러나는 초승달을 이 색이 실제로 채우는지. 불꽃 한 줌은 몸을 옮긴 자리에
            # 얹히기만 할 뿐 초승달을 못 채운다 — 이걸 안 보면 불꽃이 몸만 한 모자가 된다
            bare = {(x + dx, y + dy) for x, y in core} - core
            found.setdefault(c, {})[i] = (dx, dy, len(pts & bare) / len(bare) if bare else 0.0)
    out: list[list] = [[] for _ in frames]
    xs = [x for x, _ in core]; ys = [y for _, y in core]
    w = max(1, max(xs) - min(xs))
    h = max(1, max(ys) - min(ys))
    for c, per in found.items():
        if len(per) * 2 < len(frames) or not _steady([v[:2] for v in per.values()]):
            continue
        if sum(v[2] for v in per.values()) < GHOST_FILL * len(per):
            continue
        for i, (dx, dy, _) in per.items():
            out[i].append((c, dx / w, dy / h))
    return out


def samplers_of(frames: list[dict], mat: str | None = None) -> list[tuple]:
    """프레임 묶음의 색 뜨는 도구들. 번짐은 묶음 전체를 봐야 재므로 여기서 한 번에 만든다.

    층 자리는 이 프레임의 몸이 아니라 **프레임 전부에서 변치 않는 부분** 바깥으로 잡는다.
    한 프레임만 부푼 것을 바깥으로 세야 잔상이 잡힌다 — 글리치의 빨강·청록 잔상은 그
    프레임에서는 몸에 붙어 있어서, 프레임 하나만 보면 번짐 층이 통째로 비어 나온다."""
    bodies = [set(specks_of({p: c for p, c in f.items() if c[3] >= 200} or dict(f))[1]) for f in frames]
    core = set.intersection(*bodies)
    if not core:                               # 프레임끼리 겹치는 곳이 없으면 장마다 따로 잰다
        return [sampler_of(f, mat=mat) for f in frames]
    ghosts = ghosts_of(frames, core)
    # 유령은 몸을 옮겨 따로 그리므로 색 뜨는 재료에서는 뺀다. 안 빼면 번짐 층에도 같이 들어가
    # 방향 없는 테를 한 겹 더 두른다
    drop = [{c for c, _, _ in g} for g in ghosts]
    clean = [{p: c for p, c in f.items() if c not in d} or dict(f) for f, d in zip(frames, drop)]
    rings = _rings(core)
    lit = _lit(rings, clean)
    xs = [x for x, _ in core]; ys = [y for _, y in core]
    box = (min(xs), min(ys), max(xs), max(ys))     # 불꽃 비율은 공통 몸으로 잰다 (specks_of)
    return [sampler_of(f, rings, lit, mat, box)[:6] + (g, mat) for f, g in zip(clean, ghosts)]


def sampler_of(frame: dict, rings: list | None = None, lit: list | None = None,
               mat: str | None = None, box: tuple | None = None) -> tuple:
    """테마 그림 한 장에서 색을 뜨는 도구 — 몸 색, 외곽선 대표색, 가장 밝은 색, 번짐 층, 불꽃, 외곽선 색, 유령

    mat 은 이 구성표의 재질 이름(MATERIALS 의 키). 색을 뜨는 데는 안 쓰이고 뒤에서 음영을
    얹을 때 그대로 넘어간다 — 여기 들고 다니는 이유는 색과 재질이 같은 구성표에서 나오기 때문이다"""
    solid = {p: c for p, c in frame.items() if c[3] >= 200} or dict(frame)
    specks, solid = specks_of(solid, box)
    rim = {p for p in solid if any((p[0] + dx, p[1] + dy) not in solid for dx, dy in N4)}
    edge = Counter(solid[p] for p in rim).most_common(1)[0][0]
    fill = {p: c for p, c in solid.items() if p not in rim} or solid
    xs = [x for x, _ in fill]; ys = [y for _, y in fill]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    found = nearest(set(fill), (x0, y0, x1, y1))
    gloss = max(frame.values(), key=lambda c: (c[0] + c[1] + c[2]) * (1 if c[3] >= 200 else 0))
    if rings is None:                          # 한 장만 줬으면 그 장의 몸을 기준으로
        rings = _rings(set(solid))
        lit = _lit(rings, [frame])
    halo = _outward(frame, rings, lit)

    region = _regions(fill)

    def src(cx: int, cy: int) -> tuple:        # found 는 상자 바깥 한 칸까지만 안다
        return found[(min(max(cx, x0 - 1), x1 + 1), min(max(cy, y0 - 1), y1 + 1))]

    def cell(cx: int, cy: int) -> tuple:
        return fill[src(cx, cy)]

    blend: dict = {}

    def at(u: float, v: float) -> tuple:
        """색을 뜬다. 자리는 UV 단계로 쪼개져 있고 층(body·lit·dark)마다 같은 자리가 다시
        오므로 한 번 섞은 것을 돌려 쓴다 — 프레임당 많아야 (UV+1)² 가지다"""
        got = blend.get((u, v))
        if got is None:
            got = blend[(u, v)] = _mix(u, v)
        return got

    def _mix(u: float, v: float) -> tuple:
        fx, fy = x0 + u * (x1 - x0), y0 + v * (y1 - y0)
        if not PATTERN:
            return cell(round(fx), round(fy))
        # 둘러싼 네 칸을 **영역별로** 모아 소속도가 큰 영역을 고르고, 그 영역 안에서만 섞는다.
        # 칸을 네모로 두면 그림이 11x17 뿐이라 256px 로 그릴 때 한 칸이 23픽셀짜리 네모가 된다.
        # 영역 사이는 소속도가 뒤집히는 자리가 경계라 칸 모서리를 안 따라가고 곡선이 되고,
        # 영역 안(크롬의 계조)은 이웃을 다 섞어 띠가 아니라 이어진 그라데이션이 된다
        ix, iy = math.floor(fx), math.floor(fy)
        tx, ty = fx - ix, fy - iy
        acc: dict = {}
        for dx, wx in ((0, 1 - tx), (1, tx)):
            for dy, wy in ((0, 1 - ty), (1, ty)):
                w = wx * wy
                if w <= 0:
                    continue
                p = src(ix + dx, iy + dy)
                c = fill[p]
                e = acc.get(region[p])
                if e is None:
                    e = acc[region[p]] = [0.0, 0.0, 0.0, 0.0, c[3]]
                e[0] += w
                e[1] += c[0] * w
                e[2] += c[1] * w
                e[3] += c[2] * w
        e = max(acc.values(), key=lambda e: e[0])
        return (round(e[1] / e[0]), round(e[2] / e[0]), round(e[3] / e[0]), e[4])

    # 외곽선은 네모 안 자리가 아니라 **테두리를 한 바퀴 도는 자리**로 뜬다. 네모 자리로 뜨면
    # 윤곽이 다른 모양에서 테두리 길이가 안 맞아 어떤 칸은 여러 번 뽑히고 어떤 칸은 빠진다 —
    # 테두리를 타고 도는 무늬(전기의 전류)가 그래서 사라진다
    ring = [solid[p] for p in around(set(solid), rim)]

    def edge_at(t: int) -> tuple:
        return ring[round(t / TT * len(ring)) % len(ring)]

    return at, edge, gloss, halo, specks, edge_at, [], mat


def _color(layers: tuple, iu: int, iv: int, it: int, sampler: tuple) -> tuple | None:
    """칠하는 방법 하나를 테마 색으로 풀어 한 칸의 색을 만든다.

    스텐실에는 **빛의 기하**(램버트·하이라이트·테두리 빛)만 들어 있고 재질은 여기서 입힌다.
    재질마다 스텐실을 따로 구우면 굽는 비용이 재질 수만큼 늘어난다 — 스텐실은 테마와 무관해야
    구성표 전부가 한 벌을 돌려 쓴다"""
    at, _, gloss, halo, _, edge_at = sampler[:6]
    mat = MATERIALS[sampler[7] if len(sampler) > 7 and sampler[7] else DEFAULT_MAT]
    # 하이라이트 색. 흰색 쪽으로 밀어야 2색 테마(분홍·잉크)에서도 광택이 산다 —
    # 거기선 '테마의 가장 밝은 색' 이 곧 몸 색이라 덧대도 아무 일이 안 일어난다
    hl = mix((255, 255, 255), gloss[:3], mat["tint"])
    col = None
    for kind, t, k2, k3, k4, a in layers:
        if kind == "shadow":
            rgba = (0, 0, 0, round(a * 255))
        elif kind[0] == "h":                       # halo0 · halo1 · halo2
            fn = halo[int(kind[4])]
            c = fn(iu / UV, iv / UV) if fn else None
            if not c:
                continue                           # 번짐이 없는 테마·자리면 그 층은 비워 둔다
            rgba = c[:3] + (round(a * c[3]),)
        elif kind in ("glow", "band"):
            rgba = gloss[:3] + (round(a * 255),)
        elif kind == "edge":
            c = edge_at(it)
            # 외곽선도 벽이라 빛을 받는다. 평평한 검은 테를 한 가지 색으로 두르면 스티커가 된다 —
            # 빛을 보는 쪽은 하이라이트 쪽으로 살짝 밀고 등진 쪽은 눌러서 둥근 입술로 읽히게
            d = k2 * 2 - 1
            e = mix(c[:3], hl, d * EDGE_LIT) if d > 0 else \
                tuple(round(v * (1 + EDGE_LAMB * d)) for v in c[:3])
            rgba = tuple(e) + (round(a * c[3]),)
        else:
            c = at(iu / UV, iv / UV)
            k = 1 - 0.15 * t                       # 아래로 갈수록 살짝 어둡게
            g = 0.0
            if kind == "vol":
                # 명암은 몸 색에 **곱한다**. 테마의 밝은 색으로 섞으면 2색 테마(분홍·잉크)에서는
                # 그 밝은 색이 곧 몸 색이라 아무 일도 일어나지 않는다 — 곱셈은 팔레트를 안 탄다
                dl = k2 * 2 - 1
                d = dl * SHADE * mat["shade"]
                k *= 1 + (LIFT if d > 0 else SINK) * d
                g = min(1.0, SPEC * mat["spec"] * k3 + RIM * mat["rim"] * k4
                        + mat["ambi"] * max(0.0, dl))
            body = (min(255, round(c[0] * k)), min(255, round(c[1] * k)), min(255, round(c[2] * k)))
            if g > 0.004:                          # 하이라이트와 테두리 빛만 덧댄다
                body = mix(body, hl, g)
            rgba = body + (round(a * c[3]),)
        if rgba[3] > 0:
            col = over(col, rgba)
    return col if col and col[3] > 3 else None


MISS = object()


def paint(stencil: tuple, sampler: tuple, memo: dict | None = None) -> dict:
    """스텐실에 테마 색을 끼워 넣는다. 몸의 색은 테마 그림의 같은 비율 자리에서 뜬다.

    memo 를 주면 칠하는 방법이 같은 칸의 색을 크기를 넘어서도 돌려 쓴다 (한 프레임 안에서)."""
    st, recipes = stencil
    if memo is None:
        memo = {}
    out = {}
    for cell, (n, iu, iv, it) in st.items():
        layers = recipes[n]
        key = (layers, iu, iv, it)
        col = memo.get(key, MISS)
        if col is MISS:
            col = memo[key] = _color(layers, iu, iv, it, sampler)
        if col:
            out[cell] = col
    return out


def scale_up(px: dict, f: float) -> dict:
    """픽셀 그림을 f 배로 키운다 (최근접). 테마 기호를 큰 판에 얹을 때 쓴다"""
    if f <= 1.0:
        return px
    n = math.ceil(f)
    big = {}
    for (x, y), c in px.items():
        bx, by = int(x * f), int(y * f)
        for dy in range(n):
            for dx in range(n):
                big[(bx + dx, by + dy)] = c
    return big


def _ghosts(px: dict, solid: set, box: tuple, ghosts: list) -> dict:
    """유령을 새 몸으로 다시 그려 밑에 깐다. 위를 몸이 덮으므로 삐져나온 쪽만 보인다 —
    테마 그림에서도 그렇게 보인다. 옮기는 양은 몸 크기에 대한 비율이라 칸 수를 타지 않는다"""
    if not ghosts:
        return px
    _, _, bw, bh = box
    under = {}
    for c, u, v in ghosts:
        ox, oy = round(u * bw), round(v * bh)
        if not (ox or oy):
            continue
        for x, y in solid:
            under[(x + ox, y + oy)] = c
    return {**under, **px} if under else px


def _dot(out: dict, cx: float, cy: float, r: float, c: tuple) -> None:
    """가운데가 (cx, cy) 인 반지름 r 짜리 둥근 점 하나. 가장자리 한 칸은 덮은 넓이만큼 흐려 끊는다"""
    for py in range(math.floor(cy - r) - 1, math.ceil(cy + r) + 1):
        for px in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 1):
            a = round(c[3] * min(1.0, max(0.0, r + 0.5 - math.hypot(px + 0.5 - cx, py + 0.5 - cy))))
            if a > 4 and a > out.get((px, py), (0, 0, 0, 0))[3]:   # 겹치면 진한 쪽을 남긴다
                out[(px, py)] = c[:3] + (a,)


def specks(marks: list, box: tuple, cells: int, edge: list | None = None) -> dict:
    """불꽃을 새 몸 테두리 기준 같은 비율 자리에 다시 흩는다 (칸이 크면 조각도 그만큼 커진다).

    **네모가 아니라 둥근 점으로 찍는다.** 원본 한 칸을 n×n 네모로 늘리면 160px 판에서
    9×9 짜리 각진 딱지가 되어, 매끈해진 몸 위에 혼자 픽셀로 남는다 (골드의 반짝이 둘,
    바다의 포말, 은하의 별이 다 그랬다). 가장자리 한 칸은 덮은 넓이만큼 흐려 끊는다.

    **한 조각 안에서 이웃이던 칸 사이는 채운다.** 몸이 20칸으로 펴지면서 원본에서 붙어
    있던 두 칸이 점 지름보다 멀어져, 전기의 가닥이 이어진 선이 아니라 점선으로 찍혔다.
    이웃인지는 그 조각에서 가장 가까운 두 점 사이 거리로 잰다 — 원본 한 칸이 그 거리다.

    **원래 몸에 닿아 있던 조각은 새 몸 테두리에 다시 붙인다** (edge 는 새 몸의 테두리 칸들).
    새 몸은 윤곽이 달라 비율 자리로 옮기면 뿌리가 몸에서 몇 픽셀 떠서, 전기의 가닥이 몸에서
    튀는 방전이 아니라 옆에 떠 있는 대시로 보였다. 떨어져 날리던 조각(눈송이·반짝이)은 원래
    자리가 뜻이라 그대로 둔다.

    **매달린 조각(용암 방울)은 매달린 몸 칸이 새 테두리에 오게 통째로 옮긴다.** 비율 자리로만
    옮기면 새 몸의 꼬리 끝과 어긋나 방울이 커서 밖 허공에서 나타났다. 몸에 바로 붙어 있던
    조각은 그 칸까지 이어 그려 테두리에서 늘어진 것으로 보이게 한다.

    **몸에서 뻗은 가닥은 번개로 그린다** — 가는 심에 옅은 빛 번짐을 두르고, 이웃 칸 사이마다
    옆으로 한 번 꺾는다. 점 지름 그대로 이으면 큰 판에서 4px 굵기 막대가 되어 털처럼 보였다"""
    bx, by, bw, bh = box
    n = max(1, round(cells / LIMIT))
    r = n / 2
    out: dict = {}
    for group in marks:
        # 원본 한 칸을 덮는 n칸 네모의 한가운데
        pts = [(bx + round(u * (bw - 1)) + r, by + round(v * (bh - 1)) + r, c) for u, v, c in group]
        uvs = [(u, v) for u, v, _ in group]
        hang = getattr(group, "hang", None)
        bolt = edge and getattr(group, "touch", False)
        if edge and hang:
            au, av, stuck = hang
            ax, ay = bx + au * (bw - 1) + r, by + av * (bh - 1) + r
            qx, qy = min(edge, key=lambda q: (q[0] + 0.5 - ax) ** 2 + (q[1] + 0.5 - ay) ** 2)
            sx, sy = qx + 0.5 - ax, qy + 0.5 - ay
            pts = [(x + sx, y + sy, c) for x, y, c in pts]
            if stuck:                              # 매달린 몸 칸도 이을 점으로 넣는다 (몸 안이라 안 칠해진다)
                top = min(range(len(uvs)), key=lambda i: (uvs[i][1], uvs[i][0]))
                pts.append((qx + 0.5, qy + 0.5, pts[top][2]))
                uvs.append((au, av))
        elif bolt:
            # 테두리에 가장 가까운 점(뿌리)이 테두리에 반쯤 걸치도록 조각을 통째로 민다
            d2, ri, (qx, qy) = min((((p[0] - q[0] - 0.5) ** 2 + (p[1] - q[1] - 0.5) ** 2), i, q)
                                   for i, p in enumerate(pts) for q in edge)
            rx, ry = pts[ri][:2]
            dist = math.sqrt(d2)
            if dist > r * 0.5:
                k = (dist - r * 0.5) / dist
                sx, sy = (qx + 0.5 - rx) * k, (qy + 0.5 - ry) * k
                pts = [(x + sx, y + sy, c) for x, y, c in pts]
            # 번개 꺾은선: 뿌리에서 가장 먼 칸(끝)까지 곧게 긋고, 칸 수만큼 마디로 나눠 마디마다
            # 옆으로 번갈아 꺾는다. 칸끼리 그대로 이으면 ㄴ·ㄱ 회로선이 되고, 가운데만 밀면 물결이 됐다
            root = pts[ri]
            order = sorted(range(len(pts)), key=lambda i: (pts[i][0] - root[0]) ** 2 + (pts[i][1] - root[1]) ** 2)
            tip = pts[order[-1]]
            span = math.hypot(tip[0] - root[0], tip[1] - root[1]) or 1.0
            nx, ny = -(tip[1] - root[1]) / span, (tip[0] - root[0]) / span
            cell = ((bw - 1) * group.step[0] + (bh - 1) * group.step[1]) / 2 if group.step else n
            m = len(pts) - 1
            flip = 1 if (round(root[0]) + round(root[1])) % 2 else -1      # 첫 꺾임 쪽 — 자리에 따라 갈린다
            poly = []
            for i in range(m + 1):
                t = i / m
                off = 0.0 if i in (0, m) else flip * (1 if i % 2 else -1) * BOLT_JAG * cell
                poly.append((root[0] + (tip[0] - root[0]) * t + nx * off,
                             root[1] + (tip[1] - root[1]) * t + ny * off, pts[order[i]][2]))
            pts = poly
        # 번개는 심을 가늘게 하고 둘레에 옅은 번짐을 깐다. 나머지는 원본 한 칸 굵기 그대로
        core = max(0.6, r * BOLT_CORE) if bolt else r
        glow = r * BOLT_GLOW if bolt else 0.0
        segs = list(zip(pts, pts[1:])) if bolt else []     # 번개는 꺾은선 마디를 차례로 잇는다
        if len(pts) > 1 and not bolt:
            # 원본에서 붙어 있던 쌍만 잇는다 (대각까지). 원본 한 칸의 크기를 알면 그걸로 가른다 —
            # 가장 가까운 두 점 거리로 재면, 몸이 가로·세로로 다르게 펴질 때(11×17 → 65×79) 짧은 쪽
            # 축이 기준이 되어 긴 쪽 이웃이 빠지고 가닥이 점선이 됐다
            step = getattr(group, "step", None)
            gap = None if step else \
                min(math.hypot(a[0] - b[0], a[1] - b[1]) for i, a in enumerate(pts) for b in pts[i + 1:])
            for i, a in enumerate(pts):
                for j in range(i + 1, len(pts)):
                    b = pts[j]
                    d = math.hypot(b[0] - a[0], b[1] - a[1])
                    du, dv = abs(uvs[i][0] - uvs[j][0]), abs(uvs[i][1] - uvs[j][1])
                    far = (du > step[0] * 1.01 or dv > step[1] * 1.01) if step else d > gap * 1.45
                    if not far and d > core:
                        segs.append((a, b))
        # 번짐은 그 가닥에서 가장 푸른 색 한 가지로 깐다. 흰 뿌리를 옅게 깔면 어두운 바탕에서 회색 테가 된다
        tint = max((c for _, _, c in pts), key=lambda c: c[2] - c[0]) if bolt else None
        for layer_r, fade in ((glow, BOLT_GLOW_A), (core, 1.0)) if bolt else ((core, 1.0),):
            def col(c):
                return (tint if fade < 1 else c)[:3] + (round((255 if fade < 1 else c[3]) * fade),)
            for cx, cy, c in pts:
                _dot(out, cx, cy, layer_r, col(c))
            for a, b in segs:
                d = math.hypot(b[0] - a[0], b[1] - a[1])
                # 번개가 아닌 조각은 예전 간격(점 반지름)을 그대로 쓴다 — 바꾸면 골드 십자 같은 그림이 몇 픽셀씩 달라진다
                k = max(1, math.ceil(d / (max(0.5, layer_r * 0.8) if bolt else layer_r)))
                for j in range(1, k):
                    t = j / k
                    _dot(out, a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, layer_r,
                         col(a[2] if t < 0.5 else b[2]))
    return out


def draw(sid: str, rid: str, samplers: list, cells: int, glyphs: list | None = None,
         memos: list | None = None) -> tuple[list[dict], tuple[int, int]]:
    """이 칸 수로 프레임들을 그린다. glyphs 를 주면 기본 칸 수 기준으로 잡은 기호를 같이 얹는다"""
    st, hot, box, solid = stencil(sid, rid, cells)
    out = [paint(st, s, memos[i] if memos else None) for i, s in enumerate(samplers)]
    out = [_ghosts(px, solid, box, s[6]) for px, s in zip(out, samplers)]
    # 불꽃은 번짐 위에 얹되 몸은 덮지 않는다 (덮으면 모양이 갉아먹힌다). 몸에 닿아 있던 조각이
    # 있을 때만 새 몸 테두리를 구한다 — 테두리 칸과 조각 점을 전부 견주는 값이라 없으면 안 쓴다
    edge = [p for p in solid if any((p[0] + dx, p[1] + dy) not in solid for dx, dy in N4)] \
        if any(getattr(g, "touch", False) or getattr(g, "hang", None) for s in samplers for g in s[4]) else None
    out = [{**px, **{p: c for p, c in specks(s[4], box, cells, edge).items() if p not in solid}} if s[4] else px
           for px, s in zip(out, samplers)]
    if glyphs:
        f = cells / LIMIT
        out = [{**px, **scale_up(g, f)} for px, g in zip(out, glyphs)]
    # 프레임마다 자리가 어긋나면 커서가 떨린다. 모든 프레임을 같은 만큼 왼쪽 위로 당긴다
    ox = min(x for px in out for x, _ in px)
    oy = min(y for px in out for _, y in px)
    out = [{(x - ox, y - oy): c for (x, y), c in px.items()} for px in out]
    return out, (hot[0] - ox, hot[1] - oy)


def _fit(px: dict, size: int) -> dict:
    return {p: c for p, c in px.items() if 0 <= p[0] < size and 0 <= p[1] < size}


def _between(a: dict, b: dict, t: float) -> dict:
    """두 프레임 사이 t 자리의 그림. 없는 칸은 완전 투명으로 본다.

    알파를 곱한 값으로 섞는다 — 그냥 섞으면 투명한 칸의 색(보통 0,0,0)이 같이 들어가
    나타나고 사라지는 자리마다 검은 테가 난다"""
    out = {}
    for p in a.keys() | b.keys():
        ca = a.get(p, (0, 0, 0, 0))
        cb = b.get(p, (0, 0, 0, 0))
        wa, wb = ca[3] * (1.0 - t), cb[3] * t
        s = wa + wb
        if s < 0.5:                       # 반올림하면 0 이 되는 칸은 안 넣는다
            continue
        out[p] = (round((ca[0] * wa + cb[0] * wb) / s),
                  round((ca[1] * wa + cb[1] * wb) / s),
                  round((ca[2] * wa + cb[2] * wb) / s),
                  round(s))
    return out


def steps(rate: int, fps: int) -> list[int]:
    """한 프레임이 머무는 rate 틱을 fps 에 맞춰 몇 조각으로 나눌지. 합이 rate 라 한 바퀴 시간이 안 변한다.

    rate 가 홀수면 고르게 못 나눈다 (5 틱을 반으로 자르면 한 바퀴가 20% 빨라진다). [3,2] 처럼
    들쭉날쭉하게 나누고 .ani 의 프레임별 rate 칸으로 그 시간을 적어 준다.
    조각 수는 내림으로 잡는다 — 올림하면 rate 7 이 4조각(34fps)이 되어 파일만 커진다"""
    k = max(1, min(rate, rate * fps // 60))
    return [rate // k + (i < rate % k) for i in range(k)]


def tween(pxs: list[dict], parts: list[int]) -> list[dict]:
    """프레임마다 parts 조각으로 쪼개고 첫 조각 뒤에 사이 그림을 끼운다.
    커서는 한 바퀴 돌므로 마지막 프레임은 첫 프레임으로 이어진다"""
    if len(parts) < 2 or len(pxs) < 2:
        return pxs
    total = sum(parts)
    at = [sum(parts[:j]) / total for j in range(1, len(parts))]   # 조각이 시작하는 자리 (0 은 원본이라 뺀다)
    out = []
    for i, cur in enumerate(pxs):
        out.append(cur)
        nxt = pxs[(i + 1) % len(pxs)]
        out += [_between(cur, nxt, t) for t in at]
    return out


def cursor(sid: str, rid: str, frames: list[dict], rate: int, glyphs: list | None = None,
           mat: str | None = None) -> tuple[bytes, str]:
    """커서 파일 하나. 크기마다 새로 그려 담는다 (늘리면 뭉개진다)"""
    samplers = samplers_of(frames, mat)
    memos = [{} for _ in frames]
    # FPS 가 켜져 있으면 다 그린 뒤에 사이를 섞는다 — 그리는 값은 그대로 두고 프레임만 는다
    parts = steps(rate, FPS) if FPS and len(frames) > 1 else [rate]
    per_size = []
    for size in CUR_SIZES:
        pxs, hot = draw(sid, rid, samplers, cells_for(size), glyphs, memos)
        per_size.append([(pixels_to_png(_fit(px, size), size), hot) for px in tween(pxs, parts)])
    n = len(per_size[0])
    curs = [pngs_to_cur([per_size[i][fi] for i in range(len(CUR_SIZES))]) for fi in range(n)]
    return (curs_to_ani(curs, parts * (n // len(parts)) if len(parts) > 1 else rate), "ani") if n > 1 \
        else (curs[0], "cur")


def page(sid: str, rid: str, frames: list[dict], glyphs: list | None = None,
         mat: str | None = None) -> tuple[list[bytes], tuple[int, int], tuple[int, int]]:
    """시안 페이지용 (프레임별 PNG, 핫스팟, 칸 수). 그림은 PAGE 판으로 크게 그린다"""
    samplers = samplers_of(frames, mat)
    memos = [{} for _ in frames]
    base, hot = draw(sid, rid, samplers, LIMIT, glyphs, memos)
    wide = max(x for px in base for x, _ in px) + 1
    tall = max(y for px in base for _, y in px) + 1
    board = PAGE if rid == "arrow" else PAGE_SMALL
    pxs, _ = draw(sid, rid, samplers, cells_for(board), glyphs, memos)
    return [pixels_to_png(_fit(px, board), board) for px in pxs], hot, (wide, tall)


def base_box(sid: str, rid: str) -> tuple:
    """기본 칸 수로 그린 몸의 자리. 테마 기호를 어디에 놓을지 계산할 때 쓴다"""
    return stencil(sid, rid, LIMIT)[2]


if __name__ == "__main__":   # 자체 점검: 모든 모양·칸이 판 안에 들어오고 층이 제대로 쌓이는지
    import time

    fake = {(x, y): ((250, 250, 255, 255) if 0 < x < 9 and 0 < y < 9 else (20, 20, 30, 255))
            for x in range(10) for y in range(10)}
    SPARK = (255, 0, 0, 255)
    fake[(12, 4)] = SPARK                                  # 몸에서 떨어져 나온 불꽃 한 점
    moving = [fake, {p: (c[0], c[1] // 2, c[2], c[3]) for p, c in fake.items()}]
    marks, body = specks_of(fake)
    assert len(marks) == 1 and (12, 4) not in body, f"불꽃을 몸과 못 갈랐다: {marks}"
    got = draw("round", "arrow", [sampler_of(fake)], LIMIT)[0][0]
    assert sum(1 for c in got.values() if c == SPARK) >= 1, "불꽃이 새 모양에서 사라졌다"
    for sid in SHAPES:
        t0 = time.time()
        line = []
        for rid in ROLES:
            blob, ext = cursor(sid, rid, moving, 6)
            assert ext == "ani" and blob[:4] == b"RIFF", f"{sid}/{rid} 움직이는 커서가 아님"
            pngs, hot, (w, h) = page(sid, rid, [fake])
            assert max(w, h) <= MIN_SIZE, f"{sid}/{rid} 가 {MIN_SIZE}칸을 넘음: {w}x{h}"
            assert 0 <= hot[0] < w and 0 <= hot[1] < h, f"{sid}/{rid} 핫스팟이 그림 밖: {hot}"
            line.append(f"{rid} {w}x{h}")
        print(f"{sid:8} {' · '.join(line)} · {time.time() - t0:.1f}초")

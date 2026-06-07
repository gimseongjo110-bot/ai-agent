"""
카드뉴스 생성기
사용 예시:
  python card_news_generator.py
  python card_news_generator.py --topic ai --bg-color "#F0F8FF" --accent-color "#E94560"
  python card_news_generator.py --width 1200 --height 1200 --output my_cards
  python card_news_generator.py --title-size 80 --body-size 44 --title-y 300
  python card_news_generator.py --cover-title "나만의 주제" --cover-subtitle "부제목 입력"
  python card_news_generator.py --help
"""

import argparse
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


# ── 주제 데이터 ──────────────────────────────────────────────
TOPICS = {
    "sleep": {
        "title": "수면 혁명",
        "subtitle": "잠을 바꾸면 삶이 바뀐다",
        "cards": [
            {"tag": "INTRO",   "icon": "💤",
             "heading": "당신은 충분히\n자고 있나요?",
             "body": "전 세계 성인의 35%가\n만성 수면 부족에 시달리고 있습니다.\n수면은 단순한 휴식이 아닌\n생존 전략입니다."},
            {"tag": "FACT 01", "icon": "🧠",
             "heading": "수면 중에\n뇌가 청소된다",
             "body": "글림프 시스템(Glymphatic System)이\n수면 중 독성 단백질을 제거합니다.\n알츠하이머의 주범 아밀로이드도\n이때 씻겨 나갑니다."},
            {"tag": "FACT 02", "icon": "🌙",
             "heading": "황금 수면 시간대\n오후 10시~새벽 2시",
             "body": "멜라토닌 분비 피크 타임입니다.\n이 시간대 수면은\n다른 시간보다 2배 이상\n깊은 회복 효과를 냅니다."},
            {"tag": "FACT 03", "icon": "⚖️",
             "heading": "잠이 부족하면\n살이 찐다",
             "body": "수면 부족 → 식욕 호르몬 증가\n→ 포만 호르몬 감소\n→ 평균 385kcal 초과 섭취\n하루 하룻밤만 못 자도 시작됩니다."},
            {"tag": "TIP",     "icon": "✅",
             "heading": "숙면을 위한\n3가지 루틴",
             "body": "① 취침 1시간 전 블루라이트 차단\n② 실내 온도 18~20도C 유지\n③ 매일 같은 시각에 일어나기\n   (주말 포함, ±30분 이내)"},
            {"tag": "OUTRO",   "icon": "🌟",
             "heading": "오늘 밤부터\n시작하세요",
             "body": "수면은 의지가 아닌 환경입니다.\n작은 루틴 하나가\n당신의 내일을 바꿉니다."},
        ],
    },
    "ai": {
        "title": "AI 시대 생존법",
        "subtitle": "인공지능과 함께 일하는 법",
        "cards": [
            {"tag": "INTRO",   "icon": "🤖",
             "heading": "AI가 빼앗는 것은\n직업이 아니라 역할",
             "body": "2030년까지 전체 업무의 30%가\nAI로 자동화된다고 예측됩니다.\n하지만 새 역할은\n반드시 생겨납니다."},
            {"tag": "FACT 01", "icon": "🎯",
             "heading": "AI가 못하는 것\n3가지",
             "body": "① 공감과 감성적 판단\n② 물리적 현장 대응\n③ 창의적 문제 재정의\nAI는 답을 찾지만,\n질문은 인간이 합니다."},
            {"tag": "FACT 02", "icon": "💬",
             "heading": "프롬프트 능력이\n새 스펙이다",
             "body": "AI에게 정확하게 질문하는 능력,\n프롬프트 엔지니어링은\n이미 연봉 상위 직군이 되었습니다.\n언어 능력이 곧 코딩 능력입니다."},
            {"tag": "FACT 03", "icon": "🚀",
             "heading": "AI 도구 10개를\n쓰는 사람 vs 0개",
             "body": "생산성 격차는 이미 10배 이상.\nChatGPT, Midjourney, Copilot...\n도구를 두려워하지 않는 사람이\nAI 시대의 승자가 됩니다."},
            {"tag": "TIP",     "icon": "📋",
             "heading": "지금 당장 해야 할\n3가지 행동",
             "body": "① 매일 AI 도구 1개 실험하기\n② AI 결과물을 편집·큐레이션하기\n③ T자형 전문성 유지하기\n   (넓은 AI 활용 + 깊은 도메인)"},
            {"tag": "OUTRO",   "icon": "🌐",
             "heading": "AI는 도구입니다\n방향은 당신이 정합니다",
             "body": "기술이 바뀌어도\n가치 있는 일을 정의하는 건\n언제나 인간의 몫이었습니다."},
        ],
    },
    "carbon": {
        "title": "탄소 중립 101",
        "subtitle": "지구를 위한 가장 쉬운 시작",
        "cards": [
            {"tag": "INTRO",   "icon": "🌍",
             "heading": "지구 온도가\n1.5도C 오르면",
             "body": "산호초 70~90% 소멸\n북극 여름 해빙 10년에 1번\n극단적 폭염 8.6배 증가\n지금 이 순간도 진행 중입니다."},
            {"tag": "FACT 01", "icon": "📊",
             "heading": "한국인 1인\n연간 탄소 배출량",
             "body": "약 11.8톤 CO2eq\n전 세계 평균(4.7톤)의 2.5배\n이 중 개인이 줄일 수 있는 부분은\n약 30~40%입니다."},
            {"tag": "FACT 02", "icon": "🥗",
             "heading": "가장 큰 탄소 발생원\n1위는 식단",
             "body": "소고기 1kg 생산 = 27kg CO2\n치킨 1kg 생산 = 6.9kg CO2\n채소 1kg 생산 = 2kg CO2\n주 1회 채식만 해도 연 330kg 절감"},
            {"tag": "FACT 03", "icon": "✈️",
             "heading": "비행기 1번이\n자동차 6개월치",
             "body": "서울-뉴욕 왕복 = 1.6톤 CO2\n국내 자동차 평균\n6개월 주행량과 동일합니다.\n기차·선박 우선 검토가 필요합니다."},
            {"tag": "TIP",     "icon": "♻️",
             "heading": "오늘부터 할 수 있는\n실천 5가지",
             "body": "① 텀블러·장바구니 생활화\n② 육류 소비 주 2회 이하로\n③ 대중교통·자전거 전환\n④ 전기·가스 절약 루틴 만들기\n⑤ 중고 거래 우선 선택"},
            {"tag": "OUTRO",   "icon": "🌱",
             "heading": "완벽하지 않아도\n괜찮습니다",
             "body": "100명이 1%씩 줄이는 것이\n1명이 100% 줄이는 것보다\n더 큰 변화를 만듭니다.\n함께라면 가능합니다."},
        ],
    },
}


# ── CLI 옵션 파싱 ─────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(
        description="카드뉴스 생성기",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # ── 주제 ──────────────────────────────────────────────────
    p.add_argument(
        "--topic", default="random",
        choices=["random", "sleep", "ai", "carbon"],
        help="주제 선택  random=랜덤 / sleep=수면혁명 / ai=AI시대생존법 / carbon=탄소중립",
    )
    p.add_argument("--cover-title",    default=None, metavar="TEXT",
                   help="표지 제목 텍스트 재정의 (미입력 시 주제 기본값 사용)")
    p.add_argument("--cover-subtitle", default=None, metavar="TEXT",
                   help="표지 부제목 텍스트 재정의")

    # ── 색상 ──────────────────────────────────────────────────
    p.add_argument("--bg-color",     default="#FFFFFF", metavar="HEX",
                   help="배경 색상")
    p.add_argument("--accent-color", default="#2D8BF0", metavar="HEX",
                   help="액센트 색상 (태그·강조바·아이콘·인디케이터)")
    p.add_argument("--title-color",  default="#0D2B55", metavar="HEX",
                   help="제목 텍스트 색상")
    p.add_argument("--body-color",   default="#1E3A5F", metavar="HEX",
                   help="본문 텍스트 색상")

    # ── 폰트 크기 ──────────────────────────────────────────────
    p.add_argument("--title-size", type=int, default=66, metavar="INT",
                   help="제목 폰트 크기 (px)")
    p.add_argument("--body-size",  type=int, default=40, metavar="INT",
                   help="본문 폰트 크기 (px)")

    # ── 텍스트 위치 ────────────────────────────────────────────
    p.add_argument("--title-x", type=int, default=None, metavar="INT",
                   help="제목 X 좌표 (기본: --margin 값 사용)")
    p.add_argument("--title-y", type=int, default=285,  metavar="INT",
                   help="제목 Y 좌표 (콘텐츠 카드 기준)")
    p.add_argument("--body-x",  type=int, default=None, metavar="INT",
                   help="본문 X 좌표 (기본: --margin 값 사용)")
    p.add_argument("--body-y",  type=int, default=None, metavar="INT",
                   help="본문 Y 좌표 (기본: 제목 끝 + 52px 자동 계산)")

    # ── 카드 사이즈 & 여백 ──────────────────────────────────────
    p.add_argument("--width",  type=int, default=1080, metavar="INT",
                   help="카드 너비 (px)")
    p.add_argument("--height", type=int, default=1080, metavar="INT",
                   help="카드 높이 (px)")
    p.add_argument("--margin", type=int, default=72,   metavar="INT",
                   help="좌우 기본 여백 (px)")

    # ── 저장 경로 ──────────────────────────────────────────────
    p.add_argument("--output", default="card_news", metavar="PATH",
                   help="저장 폴더 경로")

    return p.parse_args()


# ── 유틸 함수 ─────────────────────────────────────────────────
FONT_DIR = Path("C:/Windows/Fonts")
FONT_REGULAR = str(FONT_DIR / "malgun.ttf")
FONT_BOLD    = str(FONT_DIR / "malgunbd.ttf")


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    for ex, ey in [(x0, y0), (x1 - 2*radius, y0),
                   (x0, y1 - 2*radius), (x1 - 2*radius, y1 - 2*radius)]:
        draw.ellipse([ex, ey, ex + 2*radius, ey + 2*radius], fill=fill)


def draw_text_left(draw, text, font, color, x, y, line_gap=10):
    """좌측 정렬 멀티라인. 마지막 y 반환."""
    for line in text.split("\n"):
        draw.text((x, y), line, font=font, fill=color)
        bbox = font.getbbox(line)
        y += (bbox[3] - bbox[1]) + line_gap
    return y


def derive_bg_panel(bg_hex):
    """배경색에서 연한 패널색 자동 유도 (밝은 배경용)."""
    r, g, b = rgb(bg_hex)
    return (max(0, r - 12), max(0, g - 12), min(255, b + 18))


# ── 표지 카드 ─────────────────────────────────────────────────
def make_cover(topic, args, file_index):
    W, H = args.width, args.height
    M = args.margin
    title_x = args.title_x if args.title_x is not None else M

    img = Image.new("RGB", (W, H), rgb(args.bg_color))
    draw = ImageDraw.Draw(img)

    accent = rgb(args.accent_color)

    # 우측 상단 장식 원
    for r_size, alpha in [(int(W * 0.46), 22), (int(W * 0.31), 33), (int(W * 0.19), 44)]:
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        cx, cy = int(W * 0.98), int(H * 0.20)
        od.ellipse([cx - r_size, cy - r_size, cx + r_size, cy + r_size],
                   fill=(*accent, alpha))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    # 좌측 세로 강조 바
    draw.rectangle([0, 0, 8, H], fill=accent)
    # 하단 강조 바
    draw.rectangle([0, H - 10, W, H], fill=accent)

    # CARD NEWS 레이블
    f_label = load_font(FONT_BOLD, max(20, args.title_size // 3))
    draw.text((M, int(H * 0.058)), "CARD NEWS", font=f_label, fill=accent)

    # 총 카드 수
    f_cnt = load_font(FONT_REGULAR, max(20, args.title_size // 3))
    cnt_txt = f"총 {len(topic['cards']) + 1}장"
    cnt_w = f_cnt.getbbox(cnt_txt)[2] - f_cnt.getbbox(cnt_txt)[0]
    draw.text((W - M - cnt_w, int(H * 0.058)), cnt_txt,
              font=f_cnt, fill=rgb(args.body_color))

    # 이모지
    f_icon = load_font(FONT_REGULAR, int(args.title_size * 1.9))
    draw.text((title_x, int(H * 0.148)), topic["cards"][0]["icon"],
              font=f_icon, fill=accent)

    # 메인 타이틀
    cover_title = args.cover_title if args.cover_title else topic["title"]
    f_title = load_font(FONT_BOLD, int(args.title_size * 1.3))
    title_end = draw_text_left(draw, cover_title, f_title,
                               rgb(args.title_color), title_x,
                               int(H * 0.345), line_gap=14)

    # 부제목
    cover_subtitle = args.cover_subtitle if args.cover_subtitle else topic["subtitle"]
    f_sub = load_font(FONT_REGULAR, int(args.title_size * 0.58))
    draw.text((title_x, title_end + 16), cover_subtitle,
              font=f_sub, fill=accent)

    # 구분선
    sep_y = title_end + int(args.title_size * 1.1)
    draw.rectangle([M, sep_y, W - M, sep_y + 3],
                   fill=(*rgb(args.body_color), 60))
    f_small = load_font(FONT_REGULAR, max(20, args.title_size // 3))
    draw.text((M, sep_y + 14), "카드뉴스 시리즈",
              font=f_small, fill=(*rgb(args.body_color), 120))

    out = Path(args.output) / f"card_{file_index:02d}_cover.png"
    img.save(out)
    print(f"  저장: {out.name}")


# ── 콘텐츠 카드 ──────────────────────────────────────────────
def make_content_card(topic, card_data, card_num, total, args, file_index):
    W, H = args.width, args.height
    M = args.margin
    title_x = args.title_x if args.title_x is not None else M
    body_x  = args.body_x  if args.body_x  is not None else M

    img = Image.new("RGB", (W, H), rgb(args.bg_color))
    draw = ImageDraw.Draw(img)

    accent     = rgb(args.accent_color)
    title_col  = rgb(args.title_color)
    body_col   = rgb(args.body_color)
    panel_col  = derive_bg_panel(args.bg_color)

    # 상단 패널
    draw.rectangle([0, 0, W, int(H * 0.13)], fill=panel_col)
    # 좌측 강조 바
    draw.rectangle([0, 0, 8, H], fill=accent)
    # 하단 강조 바
    draw.rectangle([0, H - 10, W, H], fill=accent)

    # 태그 pill
    f_tag = load_font(FONT_BOLD, max(18, args.title_size // 2 - 5))
    tag_bbox = f_tag.getbbox(card_data["tag"])
    tw = tag_bbox[2] - tag_bbox[0] + 44
    th = int(args.title_size * 0.65)
    tx, ty = M, int(H * 0.045)
    draw_rounded_rect(draw, (tx, ty, tx + tw, ty + th), 12, fill=accent)
    draw.text((tx + 22, ty + (th - (tag_bbox[3] - tag_bbox[1])) // 2),
              card_data["tag"], font=f_tag, fill=(255, 255, 255))

    # 페이지 번호 (우측)
    f_num = load_font(FONT_REGULAR, max(18, args.title_size // 2 - 5))
    num_txt = f"{card_num} / {total}"
    num_w = f_num.getbbox(num_txt)[2] - f_num.getbbox(num_txt)[0]
    draw.text((W - M - num_w, int(H * 0.053)),
              num_txt, font=f_num, fill=(*body_col, 160))

    # 이모지
    f_icon = load_font(FONT_REGULAR, int(args.title_size * 1.45))
    draw.text((title_x, int(H * 0.148)), card_data["icon"],
              font=f_icon, fill=accent)

    # 제목
    f_heading = load_font(FONT_BOLD, args.title_size)
    title_end = draw_text_left(draw, card_data["heading"], f_heading,
                               title_col, title_x, args.title_y, line_gap=12)

    # 구분선
    sep_y = title_end + 18
    draw.rectangle([M, sep_y, W - M, sep_y + 3],
                   fill=(*accent, 80))

    # 본문
    body_start = args.body_y if args.body_y is not None else sep_y + 36
    f_body = load_font(FONT_REGULAR, args.body_size)
    draw_text_left(draw, card_data["body"], f_body,
                   body_col, body_x, body_start, line_gap=18)

    # 하단 페이지 인디케이터 (좌측 정렬)
    dot_r   = max(5, args.margin // 12)
    dot_gap = dot_r * 4
    dx = M
    dy = H - int(H * 0.048)
    for i in range(total):
        cx = dx + i * dot_gap + dot_r
        if i == card_num - 1:
            draw.ellipse([cx - dot_r, dy - dot_r, cx + dot_r, dy + dot_r],
                         fill=accent)
        else:
            draw.ellipse([cx - dot_r, dy - dot_r, cx + dot_r, dy + dot_r],
                         fill=(*accent, 70))

    slug = card_data["tag"].lower().replace(" ", "_")
    out  = Path(args.output) / f"card_{file_index:02d}_{slug}.png"
    img.save(out)
    print(f"  저장: {out.name}")


# ── 메인 ─────────────────────────────────────────────────────
def main():
    args = parse_args()

    # 저장 폴더 생성
    Path(args.output).mkdir(parents=True, exist_ok=True)

    # 주제 선택
    key = random.choice(list(TOPICS.keys())) if args.topic == "random" else args.topic
    topic = TOPICS[key]

    # 적용 설정 출력
    print("\n[카드뉴스 생성기] 적용 설정")
    print(f"  주제        : {topic['title']} ({key})")
    print(f"  카드 사이즈 : {args.width} x {args.height} px")
    print(f"  배경 색상   : {args.bg_color}")
    print(f"  액센트 색상 : {args.accent_color}")
    print(f"  제목 색상   : {args.title_color}  /  크기: {args.title_size}px")
    print(f"  제목 위치   : x={args.title_x or args.margin}  y={args.title_y}")
    print(f"  본문 색상   : {args.body_color}  /  크기: {args.body_size}px")
    print(f"  본문 위치   : x={args.body_x or args.margin}  y={args.body_y or '자동'}")
    print(f"  저장 경로   : {args.output}/")
    print(f"\n카드뉴스 생성 시작...\n")

    idx = 1
    make_cover(topic, args, idx)
    idx += 1

    total = len(topic["cards"])
    for i, card in enumerate(topic["cards"], 1):
        make_content_card(topic, card, i, total, args, idx)
        idx += 1

    print(f"\n완료! 총 {idx - 1}장 → {args.output}/")


if __name__ == "__main__":
    main()

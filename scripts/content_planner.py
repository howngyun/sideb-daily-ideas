"""
DIGOUT - 콘텐츠 기획안 생성 스크립트
주제를 입력받아 → DIGOUT 스타일 인스타 게시물 기획안 완성 후 이메일 발송
"""

import os
import sys
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import anthropic

# ──────────────────────────────────────────────
# 설정
# ──────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GMAIL_USER        = os.environ["GMAIL_USER"]
GMAIL_APP_PW      = os.environ["GMAIL_APP_PW"]
TO_EMAIL          = os.environ["TO_EMAIL"]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

TODAY = datetime.date.today().strftime("%Y년 %m월 %d일")
WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]
WEEKDAY = WEEKDAY_KR[datetime.date.today().weekday()]


# ──────────────────────────────────────────────
# 카테고리 감지
# ──────────────────────────────────────────────
CATEGORY_MAP = {
    "SOUND": ["음악", "앨범", "아티스트", "공연", "내한", "멜론", "차트", "밴드", "힙합", "장르", "플레이리스트"],
    "WEAR":  ["패션", "옷", "룩", "스타일", "브랜드", "빈티지 옷", "무신사", "스트리트", "코디"],
    "PLACE": ["카페", "장소", "공간", "스팟", "서울", "여행", "숨겨진", "핫플", "골목", "지역"],
    "GEAR":  ["카메라", "필름", "기기", "오디오", "레코드", "레트로", "빈티지 카메라", "LP", "워크맨", "전축"],
    "SCENE": ["전시", "팝업", "이벤트", "컬처", "연예", "이슈", "공연장", "뮤지컬", "축제"],
    "NOW":   ["트렌드", "요즘", "최근", "이슈", "화제", "sns", "바이럴"],
}

def detect_category(topic: str) -> str:
    topic_lower = topic.lower()
    for cat, keywords in CATEGORY_MAP.items():
        if any(kw in topic_lower for kw in keywords):
            return cat
    return "NOW"


# ──────────────────────────────────────────────
# 기획안 생성
# ──────────────────────────────────────────────
def generate_content_plan(topic: str) -> str:
    category = detect_category(topic)

    category_guide = {
        "SOUND": "음악 아티스트/앨범/장르 중심. 음악적 맥락과 왜 지금 들어야 하는지를 설명.",
        "WEAR":  "패션 룩/브랜드/스타일 중심. 이 스타일이 왜 지금인지 편집 관점 포함.",
        "PLACE": "공간/장소/카페 중심. 공간의 무드와 가야 할 이유를 감성적으로 전달.",
        "GEAR":  "빈티지 기기/레트로 테크 중심. 기기의 역사와 매력, 입문 팁 포함.",
        "SCENE": "공연/전시/팝업/내한 중심. 가기 전 알아야 할 정보와 기대 포인트.",
        "NOW":   "컬처 이슈/트렌드 중심. 맥락과 배경, DIGOUT 시각의 해석 포함.",
    }

    prompt = f"""
당신은 DIGOUT 인스타그램 컬처 매거진의 수석 에디터입니다.
DIGOUT은 10~20대 타겟, 음악/패션/장소/빈티지기기/공연/컬처를 다루는 피드 전용 매거진입니다.
릴스 없이 카드뉴스(이미지 슬라이드) 게시물만 올립니다.

오늘 게시할 콘텐츠 주제: **{topic}**
시리즈 분류: DIGOUT {category} — {category_guide[category]}

아래 형식으로 완전한 게시물 기획안을 작성하세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 기획 개요
━━━━━━━━━━━━━━━━━━━━━━━━━━
- 시리즈: DIGOUT {category}
- 주제: {topic}
- 핵심 메시지 (한 줄): 
- 타겟 독자: 
- 게시 적합 시간대: 

━━━━━━━━━━━━━━━━━━━━━━━━━━
🃏 카드 구성 (슬라이드별 상세)
━━━━━━━━━━━━━━━━━━━━━━━━━━
카드 1 — 커버
- 메인 제목:
- 서브 텍스트:
- 비주얼 방향: (색감, 분위기, 레이아웃 힌트)

카드 2 —
- 소제목:
- 본문 내용: (3~4줄)

카드 3 —
- 소제목:
- 본문 내용: (3~4줄)

카드 4 —
- 소제목:
- 본문 내용: (3~4줄)

카드 5 — (필요시)
- 소제목:
- 본문 내용:

마지막 카드 — DIGOUT PICK 마무리
- 결론 문장:
- CTA 문구: (저장 or 공유 유도)

━━━━━━━━━━━━━━━━━━━━━━━━━━
✍️ 캡션 전문
━━━━━━━━━━━━━━━━━━━━━━━━━━
(첫 줄 후킹 문장부터 시작. 200~300자. 마지막에 질문형 CTA 포함)

━━━━━━━━━━━━━━━━━━━━━━━━━━
#️⃣ 해시태그 (15개, 댓글용)
━━━━━━━━━━━━━━━━━━━━━━━━━━
(대형 3개 + 중형 7개 + 소형/브랜드 5개)

━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 에디터 노트
━━━━━━━━━━━━━━━━━━━━━━━━━━
(이 콘텐츠를 만들 때 편집 시 주의할 점, 참고할 레퍼런스, 비주얼 팁 2~3가지)
"""

    print(f"🤖 [{topic}] 기획안 생성 중...")
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text, category


# ──────────────────────────────────────────────
# 이메일 발송
# ──────────────────────────────────────────────
CATEGORY_COLORS = {
    "SOUND": "#1a1a2e",
    "WEAR":  "#2d1b00",
    "PLACE": "#0d2818",
    "GEAR":  "#1a0a2e",
    "SCENE": "#2a0a0a",
    "NOW":   "#0a1a2a",
}

CATEGORY_EMOJI = {
    "SOUND": "🎵",
    "WEAR":  "👗",
    "PLACE": "📍",
    "GEAR":  "📻",
    "SCENE": "🎭",
    "NOW":   "⚡",
}

def build_plan_html(topic: str, plan_text: str, category: str) -> str:
    color = CATEGORY_COLORS.get(category, "#1a1a1a")
    emoji = CATEGORY_EMOJI.get(category, "📌")

    lines = plan_text.split("\n")
    html_lines = []
    in_section = False

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            html_lines.append("<br>")
        elif "━━━" in line_stripped:
            if in_section:
                html_lines.append("</div>")
            in_section = True
            html_lines.append('<div style="background:#fff;border:1px solid #eee;border-radius:8px;padding:20px 24px;margin-bottom:16px;">')
        elif line_stripped.startswith("카드") and "—" in line_stripped:
            html_lines.append(f'<h3 style="color:{color};font-size:15px;margin:16px 0 8px;border-bottom:1px solid #f0f0f0;padding-bottom:6px;">{line_stripped}</h3>')
        elif line_stripped.startswith("- ") or line_stripped.startswith("• "):
            text = line_stripped[2:]
            html_lines.append(f'<p style="margin:4px 0 4px 12px;font-size:13px;color:#444;line-height:1.7;">• {text}</p>')
        elif line_stripped.startswith("#"):
            html_lines.append(f'<p style="margin:4px 0;font-size:13px;color:#8B0000;font-family:monospace;">{line_stripped}</p>')
        elif "📌" in line_stripped or "🃏" in line_stripped or "✍️" in line_stripped or "#️⃣" in line_stripped or "📝" in line_stripped:
            html_lines.append(f'<h2 style="color:#1a1a1a;font-size:16px;margin:0 0 12px;">{line_stripped}</h2>')
        else:
            html_lines.append(f'<p style="margin:4px 0;font-size:13px;color:#333;line-height:1.7;">{line_stripped}</p>')

    if in_section:
        html_lines.append("</div>")

    body = "\n".join(html_lines)

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family:'Apple SD Gothic Neo',sans-serif;max-width:680px;margin:0 auto;padding:24px;background:#fafafa;color:#1a1a1a;">

  <!-- 헤더 -->
  <div style="background:{color};padding:28px 32px;border-radius:8px;margin-bottom:24px;">
    <div style="font-size:11px;color:#aaa;letter-spacing:2px;margin-bottom:8px;">DIGOUT {category} {emoji}</div>
    <div style="font-size:22px;font-weight:900;color:#fff;line-height:1.4;">{topic}</div>
    <div style="font-size:11px;color:#888;margin-top:10px;">{TODAY} {WEEKDAY}요일 · 기획안</div>
  </div>

  <!-- 안내 -->
  <div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:16px 20px;margin-bottom:24px;">
    <p style="margin:0;font-size:13px;color:#856404;line-height:1.7;">
      📋 아래 기획안을 바탕으로 카드를 편집하면 돼요.<br>
      카드 구성 → 캡션 → 해시태그 순서로 확인하세요.
    </p>
  </div>

  <!-- 기획안 본문 -->
  {body}

  <!-- 푸터 -->
  <div style="text-align:center;font-size:11px;color:#bbb;margin-top:24px;padding-top:16px;border-top:1px solid #eee;">
    DIGOUT Content Plan · {TODAY} · DIGOUT {category}
  </div>

</body>
</html>
"""


def send_plan_email(topic: str, html_content: str, category: str):
    emoji = CATEGORY_EMOJI.get(category, "📌")
    print(f"📨 기획안 이메일 발송 중...")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[DIGOUT {category}] {emoji} {topic} — 기획안"
    msg["From"]    = GMAIL_USER
    msg["To"]      = TO_EMAIL

    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PW)
        server.sendmail(GMAIL_USER, TO_EMAIL, msg.as_string())

    print(f"✅ 기획안 이메일 발송 완료 → {TO_EMAIL}")


# ──────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────
def main():
    # GitHub Actions에서 TOPIC 환경변수로 주제 받음
    topic = os.environ.get("TOPIC", "").strip()

    if not topic:
        print("❌ TOPIC 환경변수가 없습니다. GitHub Actions에서 TOPIC을 설정해주세요.")
        sys.exit(1)

    print(f"\n✏️  DIGOUT 기획안 생성 — 주제: {topic}\n")
    plan_text, category = generate_content_plan(topic)
    html = build_plan_html(topic, plan_text, category)
    send_plan_email(topic, html, category)
    print("\n🎉 기획안 완료!\n")


if __name__ == "__main__":
    main()

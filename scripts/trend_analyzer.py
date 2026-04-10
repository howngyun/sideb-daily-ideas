"""
DIGOUT - 트렌드 분석 & 이메일 발송 스크립트
매일 아침 실행 → 음악/패션/장소/빈티지/컬처 트렌드 수집 후 이메일 발송
"""

import os
import json
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import anthropic
import requests
from bs4 import BeautifulSoup

# ──────────────────────────────────────────────
# 설정
# ──────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GMAIL_USER        = os.environ["GMAIL_USER"]       # 보내는 Gmail 주소
GMAIL_APP_PW      = os.environ["GMAIL_APP_PW"]     # Gmail 앱 비밀번호
TO_EMAIL          = os.environ["TO_EMAIL"]          # 받는 이메일 주소

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

TODAY = datetime.date.today().strftime("%Y년 %m월 %d일")
WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]
WEEKDAY = WEEKDAY_KR[datetime.date.today().weekday()]


# ──────────────────────────────────────────────
# 트렌드 데이터 수집
# ──────────────────────────────────────────────
def scrape_melon_chart():
    """멜론 실시간 TOP 10"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get("https://www.melon.com/chart/index.htm", headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        songs = []
        for row in soup.select("tr.lst50, tr.lst100")[:10]:
            title  = row.select_one(".ellipsis.rank01 a")
            artist = row.select_one(".ellipsis.rank02 a")
            if title and artist:
                songs.append(f"{title.text.strip()} - {artist.text.strip()}")
        return songs[:10]
    except Exception as e:
        return [f"멜론 차트 수집 실패: {e}"]


def scrape_naver_fashion_news():
    """네이버 패션 뉴스 헤드라인"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(
            "https://search.naver.com/search.naver?where=news&query=패션+트렌드+스트리트",
            headers=headers, timeout=10
        )
        soup = BeautifulSoup(res.text, "html.parser")
        headlines = []
        for item in soup.select(".news_tit")[:8]:
            headlines.append(item.text.strip())
        return headlines
    except Exception as e:
        return [f"패션 뉴스 수집 실패: {e}"]


def scrape_naver_culture_news():
    """네이버 컬처/공연/전시 뉴스"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(
            "https://search.naver.com/search.naver?where=news&query=내한공연+전시+팝업스토어+2025",
            headers=headers, timeout=10
        )
        soup = BeautifulSoup(res.text, "html.parser")
        headlines = []
        for item in soup.select(".news_tit")[:8]:
            headlines.append(item.text.strip())
        return headlines
    except Exception as e:
        return [f"컬처 뉴스 수집 실패: {e}"]


def scrape_naver_vintage_news():
    """빈티지/레트로 기기 뉴스"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(
            "https://search.naver.com/search.naver?where=news&query=필름카메라+빈티지+레트로+오디오",
            headers=headers, timeout=10
        )
        soup = BeautifulSoup(res.text, "html.parser")
        headlines = []
        for item in soup.select(".news_tit")[:6]:
            headlines.append(item.text.strip())
        return headlines
    except Exception as e:
        return [f"빈티지 뉴스 수집 실패: {e}"]


def collect_all_trends():
    print("📡 트렌드 데이터 수집 중...")
    return {
        "melon_top10":      scrape_melon_chart(),
        "fashion_news":     scrape_naver_fashion_news(),
        "culture_news":     scrape_naver_culture_news(),
        "vintage_news":     scrape_naver_vintage_news(),
    }


# ──────────────────────────────────────────────
# Claude 트렌드 분석
# ──────────────────────────────────────────────
def analyze_trends_with_claude(raw_data: dict) -> str:
    prompt = f"""
당신은 DIGOUT이라는 인스타그램 컬처 매거진의 수석 에디터입니다.
DIGOUT은 10~20대를 타겟으로 음악, 패션, 장소, 빈티지 기기, 공연/내한, 컬처 이슈를 다루는 피드 전용 매거진입니다.

오늘({TODAY}, {WEEKDAY}요일) 수집된 트렌드 원시 데이터를 분석하여,
DIGOUT 에디터가 오늘 어떤 게시물을 만들면 좋을지 판단할 수 있도록 정리해주세요.

=== 수집된 원시 데이터 ===
[멜론 실시간 TOP 10]
{chr(10).join(f"  {i+1}. {s}" for i, s in enumerate(raw_data["melon_top10"]))}

[패션/스트리트 뉴스]
{chr(10).join(f"  - {n}" for n in raw_data["fashion_news"])}

[공연/내한/전시/팝업 뉴스]
{chr(10).join(f"  - {n}" for n in raw_data["culture_news"])}

[빈티지/레트로 기기 뉴스]
{chr(10).join(f"  - {n}" for n in raw_data["vintage_news"])}

=== 출력 형식 ===
아래 형식으로 한국어로 작성하세요. 각 섹션은 명확히 구분하세요.

## 🎵 SOUND — 오늘의 음악 트렌드
(차트 흐름 분석 + 주목할 아티스트/장르 + DIGOUT SOUND 게시물 아이디어 1~2개)

## 👗 WEAR — 오늘의 패션 트렌드
(패션 뉴스 요약 + 지금 뜨는 스타일 키워드 + DIGOUT WEAR 게시물 아이디어 1~2개)

## 🎭 SCENE — 오늘의 공연/컬처 이슈
(공연/내한/전시/팝업 주요 이슈 + DIGOUT SCENE 게시물 아이디어 1~2개)

## 📻 GEAR — 오늘의 빈티지/레트로
(빈티지 기기 트렌드 + DIGOUT GEAR 게시물 아이디어 1개)

## ⚡ TODAY'S TOP PICK — 오늘 가장 올려야 할 게시물 추천
(위 4개 중 오늘 가장 임팩트 있는 주제 1개 선정 + 이유 2~3줄)

## 📋 오늘의 주제 후보 리스트 (선택용)
(에디터가 고를 수 있도록 번호 매긴 주제 5~7개, 한 줄씩)
"""

    print("🤖 Claude 트렌드 분석 중...")
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


# ──────────────────────────────────────────────
# 이메일 발송
# ──────────────────────────────────────────────
def build_email_html(analysis: str) -> str:
    """마크다운 분석 결과를 HTML 이메일로 변환"""
    lines = analysis.split("\n")
    html_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            html_lines.append("<br>")
        elif line.startswith("## "):
            title = line.replace("## ", "")
            html_lines.append(f'<h2 style="color:#1a1a1a;border-left:4px solid #8B0000;padding-left:12px;margin-top:32px;">{title}</h2>')
        elif line.startswith("- ") or line.startswith("• "):
            text = line[2:]
            html_lines.append(f'<li style="margin-bottom:6px;">{text}</li>')
        elif line[0].isdigit() and ". " in line[:4]:
            html_lines.append(f'<li style="margin-bottom:6px;">{line}</li>')
        else:
            html_lines.append(f'<p style="margin:6px 0;line-height:1.7;">{line}</p>')

    body = "\n".join(html_lines)

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family:'Apple SD Gothic Neo',sans-serif;max-width:680px;margin:0 auto;padding:24px;background:#fafafa;color:#1a1a1a;">

  <!-- 헤더 -->
  <div style="background:#1a1a1a;padding:28px 32px;border-radius:8px;margin-bottom:28px;">
    <div style="font-size:28px;font-weight:900;color:#fff;letter-spacing:3px;">DIGOUT</div>
    <div style="font-size:12px;color:#999;margin-top:6px;letter-spacing:1px;">DAILY TREND BRIEF · {TODAY} {WEEKDAY}요일</div>
  </div>

  <!-- 인트로 -->
  <div style="background:#fff;border:1px solid #eee;border-radius:8px;padding:20px 24px;margin-bottom:24px;">
    <p style="margin:0;font-size:14px;color:#555;line-height:1.8;">
      오늘의 트렌드를 분석했어요.<br>
      아래 <strong>TODAY'S TOP PICK</strong>과 <strong>주제 후보 리스트</strong>를 확인하고,<br>
      마음에 드는 주제를 Claude에게 던져주면 기획안을 바로 만들어드릴게요.
    </p>
  </div>

  <!-- 분석 본문 -->
  <div style="background:#fff;border:1px solid #eee;border-radius:8px;padding:24px 28px;margin-bottom:24px;">
    {body}
  </div>

  <!-- 기획 요청 안내 -->
  <div style="background:#1a1a1a;border-radius:8px;padding:20px 24px;margin-bottom:24px;">
    <p style="margin:0;color:#fff;font-size:13px;line-height:1.8;">
      💡 <strong>기획 요청 방법</strong><br>
      Claude에게 원하는 주제 번호 또는 키워드를 보내면<br>
      → DIGOUT 스타일 게시물 기획안(카드 구성 + 캡션 + 해시태그)을 이메일로 받을 수 있어요.
    </p>
  </div>

  <!-- 푸터 -->
  <div style="text-align:center;font-size:11px;color:#bbb;margin-top:16px;">
    DIGOUT Daily Brief · 자동 발송 · {TODAY}
  </div>

</body>
</html>
"""


def send_email(html_content: str):
    print("📨 이메일 발송 중...")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[DIGOUT] {TODAY} {WEEKDAY}요일 트렌드 브리프"
    msg["From"]    = GMAIL_USER
    msg["To"]      = TO_EMAIL

    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PW)
        server.sendmail(GMAIL_USER, TO_EMAIL, msg.as_string())

    print(f"✅ 이메일 발송 완료 → {TO_EMAIL}")


# ──────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────
def main():
    print(f"\n🗓️  DIGOUT Daily Brief 실행 — {TODAY} {WEEKDAY}요일\n")
    raw_data = collect_all_trends()
    analysis = analyze_trends_with_claude(raw_data)
    html     = build_email_html(analysis)
    send_email(html)
    print("\n🎉 완료!\n")


if __name__ == "__main__":
    main()

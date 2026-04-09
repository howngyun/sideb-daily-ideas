import anthropic
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def generate_ideas():
      client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
      today = datetime.now().strftime("%Y년 %m월 %d일")
      message = client.messages.create(
          model="claude-sonnet-4-20250514",
          max_tokens=3000,
          messages=[
              {
                  "role": "user",
                  "content": f"너는 SIDE B 인스타그램 매거진의 수석 에디터야. 오늘({today}) 트렌드를 반영해서 의류/핫플/빈티지테크/음악 카테고리 각 5개씩 총 20개 캐러셀 아이디어를 생성해줘. 형식: 번호.[카테고리] 제목 / 핵심훅 / 저장이유 / 슬라이드수"
              }
          ]
      )
      return message.content[0].text

def send_email(ideas_text):
      sender = os.environ["GMAIL_ADDRESS"]
      password = os.environ["GMAIL_APP_PASSWORD"]
      receiver = "howngyun@gmail.com"
      today = datetime.now().strftime("%Y년 %m월 %d일")
      msg = MIMEMultipart("alternative")
      msg["Subject"] = f"[SIDE B] {today} 오늘의 아이디어 20개"
      msg["From"] = sender
      msg["To"] = receiver
      body = f"<html><body style='font-family:sans-serif;max-width:700px;margin:0 auto;background:#f5f0e8;padding:20px'><div style='background:#1a1a1a;color:#f5f0e8;padding:30px;margin-bottom:20px'><h1 style='letter-spacing:4px;margin:0'>SIDE B</h1><p style='color:#c8a882;margin:5px 0 0'>DAILY IDEAS - {today}</p></div><div style='background:white;padding:30px;white-space:pre-wrap;line-height:1.9;font-size:14px'>{ideas_text}</div><p style='text-align:center;color:#888;font-size:11px;letter-spacing:2px'>A면은 모두가 안다. B면은 우리만 안다.</p></body></html>"
      msg.attach(MIMEText(body, "html"))
      with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
                server.sendmail(sender, receiver, msg.as_string())
            print(f"발송 완료: {today}")

if __name__ == "__main__":
      ideas = generate_ideas()
    send_email(ideas)
    print("완료!")

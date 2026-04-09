import anthropic
import os
import ssl
import smtplib
from email.message import EmailMessage
from datetime import datetime


def generate_ideas():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = datetime.now().strftime("%Y-%m-%d")
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[
            {
                "role": "user",
                "content": f"You are the chief editor of SIDE B, a Korean Instagram magazine. Today is {today}. Generate 20 Instagram carousel post ideas in Korean. 5 ideas each for: clothing/fashion, hotplaces/cafes, vintage tech, music. Format each: Number.[Category] Title / Hook sentence / Why save / Number of slides"
            }
        ]
    )
    return message.content[0].text


def send_email(ideas_text):
    sender = os.environ["GMAIL_ADDRESS"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    receiver = "howngyun@gmail.com"
    today = datetime.now().strftime("%Y-%m-%d")

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto;background:#f5f0e8;padding:20px">
<div style="background:#1a1a1a;color:#f5f0e8;padding:30px;margin-bottom:20px">
<h1 style="letter-spacing:4px;margin:0;font-size:24px">SIDE B</h1>
<p style="color:#c8a882;margin:5px 0 0;font-size:12px">DAILY IDEAS - {today}</p>
</div>
<div style="background:white;padding:30px;line-height:1.9;font-size:14px;white-space:pre-wrap">{ideas_text}</div>
<p style="text-align:center;color:#888;font-size:11px;padding:20px">A side is for everyone. B side is ours.</p>
</body>
</html>"""

    msg = EmailMessage()
    msg["Subject"] = f"[SIDE B] {today} Daily Ideas 20"
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content("Please view this email in HTML format.")
    msg.add_alternative(html, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, password)
        server.send_message(msg)

    print(f"Done: {today}")


if __name__ == "__main__":
    print("Generating ideas...")
    ideas = generate_ideas()
    print("Sending email...")
    send_email(ideas)
    print("Complete!")

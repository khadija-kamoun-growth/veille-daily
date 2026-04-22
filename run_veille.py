#!/usr/bin/env python3
"""Daily veille script for Khadija's personal brand.
Runs in GitHub Actions. Uses Anthropic API + web search to find viral LinkedIn
posts on AI × growth marketing, synthesizes into HTML brief, emails via SMTP.

Env vars required:
  ANTHROPIC_API_KEY
  GMAIL_APP_PASSWORD
  GMAIL_USER (default: kamoun@digigram.com)
"""
import os
import sys
import smtplib
import ssl
import re
from datetime import date
from email.message import EmailMessage
from anthropic import Anthropic

GMAIL_USER = os.environ.get("GMAIL_USER", "kamoun@digigram.com")
RECIPIENT = GMAIL_USER
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are Khadija Kamoun's veille assistant. Your job is to produce a compact daily HTML email brief of the most viral LinkedIn posts at the AI × growth marketing × digital marketing intersection.

ABSOLUTE RULES — DO NOT BREAK:
1. Every source link MUST be a linkedin.com/posts/ URL. ZERO articles, blogs, news sites. If you only have articles, ship fewer posts rather than include them.
2. Freshness: past 30 DAYS only. Verify dates.
3. Viral threshold: >100 reactions OR >50 comments. Skip below.
4. Volume: 3-5 posts max. 3 is great. 5 is ceiling.
5. Focus: AI × growth marketing × digital marketing. Not general B2B, not solopreneur coaching, not general sales.
6. Creator rotation: same creator not twice in same week.
7. If fewer than 3 posts pass filters, ship with an honest note — never pad.

METHOD:
- Use web_search with queries like `site:linkedin.com/posts [topic] 2026`.
- For promising candidates, verify via web_search or web_fetch that the post is within 30 days and viral.

CREATOR POOL (rotate, don't exhaust): Kipp Bodnar, Kieran Flanagan, Paul Roetzer, Mike Kaput, Adam Robinson, Chris Orlob, Lenny Rachitsky, Kyle Poyar, Eric Siu, Katelyn Bourgoin, Neil Patel, Tim Soulo, Guillaume Cabane, Linas Beliūnas, Alex Banks, Vaibhav Sisinty, Austin Lau, Lillian Pierson, Brendon Bosworth. Also find new voices.

CONTENT IDEAS (À poster cette semaine):
- Voice: storytelling, first-person ("I", "you"), broad-reach hooks
- NEVER mention Digigram/her employer
- Tied to goals: LinkedIn profile visits + head hunters finding her + sustaining 4 posts/week
- React-posts inspired by the viral posts above are highest priority

OUTPUT FORMAT (strict HTML, copy this skeleton exactly, fill in):
<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif; font-size: 15px; line-height: 1.5; color: #222; max-width: 620px;">
<p style="color:#888; font-size:12px; letter-spacing:1px; text-transform:uppercase; margin:0 0 4px;">Veille Khadija — {DATE} (fenêtre : 30 jours · AI × growth × digital marketing)</p>
<h2 style="margin:0 0 20px; font-size:20px;">Brief daily — 100% LinkedIn posts</h2>
<p style="color:#555; font-size:13px; margin-bottom:24px;">Chaque lien = un post LinkedIn viral. Pas d'articles. Dates + engagement vérifiés.</p>
<h3 style="color:#4E33F1; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:24px 0 8px;">Posts viraux cette semaine</h3>
<p><b>[Creator] — il y a [X]</b> · <span style="color:#666;">[N] réactions · [M] commentaires</span><br>"[Hook du post]". Thèse : [1 phrase]. <a href="[linkedin.com/posts URL]">Voir le post</a></p>
[...repeat for 3-5 posts...]
<h3 style="color:#FF575A; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:24px 0 8px;">À poster cette semaine</h3>
<p><b>Texte #1</b> — hook + angle 1 phrase (inspiré des posts ci-dessus).</p>
<p><b>Texte #2</b> — hook + angle 1 phrase.</p>
<p><b>Carrousel</b> — titre + angle.</p>
<p><b>Vidéo</b> — hook contrarian.</p>
<p style="color:#888; font-size:12px; margin-top:32px;">Méthode : LinkedIn posts uniquement · >100 réactions · fenêtre 30 jours.<br>Prochain brief : demain 7:47 AM.</p>
</body>
</html>

Return ONLY the HTML. No preamble, no explanation, no code fences."""


def run_veille() -> str:
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    today = date.today().isoformat()

    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 15}],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Today is {today}. Produce the daily veille brief. "
                    f"Search site:linkedin.com/posts for viral posts at the AI × growth marketing "
                    f"intersection from the past 30 days. Verify each candidate. Output only HTML."
                ),
            }
        ],
    )

    # Concatenate text blocks from response
    text = ""
    for block in message.content:
        if block.type == "text":
            text += block.text

    # Clean up: strip code fences, drop any preamble before <!DOCTYPE or <html
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```$", "", text)
    # Find the first HTML marker and trim everything before it
    m = re.search(r"<!DOCTYPE\s+html>|<html[\s>]", text, re.IGNORECASE)
    if m:
        text = text[m.start():]
    # Trim trailing content after </html>
    m2 = re.search(r"</html>", text, re.IGNORECASE)
    if m2:
        text = text[: m2.end()]

    return text.strip()


def send_email(html: str, subject: str):
    msg = EmailMessage()
    msg["From"] = GMAIL_USER
    msg["To"] = RECIPIENT
    msg["Subject"] = subject
    msg.set_content("This email requires an HTML-capable client.")
    msg.add_alternative(html, subtype="html")

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
        s.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        s.send_message(msg)


def main():
    today = date.today().isoformat()
    subject = f"Veille Khadija — {today}"
    print(f"Running veille for {today}...")
    html = run_veille()
    if not html.lstrip().startswith("<"):
        print("WARNING: response is not HTML, prepending wrapper", file=sys.stderr)
        html = f"<pre>{html}</pre>"
    print(f"HTML length: {len(html)} chars")
    send_email(html, subject)
    print(f"Sent: {subject}")


if __name__ == "__main__":
    main()

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

SYSTEM_PROMPT = """You produce Khadija's daily email: brief of viral LinkedIn posts + ready-to-ship content pack.

RULES:
- Brief: 3-5 LinkedIn posts (linkedin.com/posts/ URLs only, past 30 days, >100 reactions). Focus AI × growth marketing. Same creator not twice/week. If <3 qualify, ship fewer + honest note. Never pad with articles.
- Pick ONE topic as "Sujet du jour" — the one most likely to drive profile visits + follows. Contrarian, specific, data-rich.
- Voice: storytelling, first-person ("I"/"you"), contractions, broad-reach hooks. NEVER mention Digigram.
- POST: 150-250 words. Hook (1 line) → 3-4 punch lines → pivot → credibility → 5-6 bullets (last = stat) → !!! closer → ⬇ + hashtags.
- CARROUSEL: 10 slides. S1 cover (title max 6 words + subtitle). S2-S8 one idea each (bold headline + 1-2 lines). S9 recap. S10 CTA.
- VIDEO SCRIPT: 45-90s, max 180 words. [HOOK] [PIVOT] [BODY] [CLOSE]. One sentence per line. Numbers written in words.

Output ONLY the HTML below, filled in. No preamble, no code fences.

<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif; font-size: 15px; line-height: 1.55; color: #222; max-width: 640px;">
<p style="color:#888; font-size:12px; letter-spacing:1px; text-transform:uppercase; margin:0 0 4px;">Veille Khadija — {DATE} · AI × growth × digital marketing</p>
<h2 style="margin:0 0 20px; font-size:20px;">Brief + content pack du jour</h2>

<h3 style="color:#4E33F1; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:24px 0 8px;">Posts viraux (30 derniers jours)</h3>
<p><b>[Creator] — il y a [X]</b> · <span style="color:#666;">[N] réactions · [M] commentaires</span><br>"[Hook]". Thèse : [1 phrase]. <a href="[linkedin.com/posts URL]">Voir le post</a></p>
[...3 to 5 posts total...]

<h3 style="color:#FF575A; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:28px 0 8px;">Sujet du jour (choisi)</h3>
<p style="background:#FFF5F5; padding:10px 14px; border-left:3px solid #FF575A; margin:0 0 16px;">
<b>[Topic in 1 punchy phrase]</b><br>
<span style="color:#555; font-size:13px;">Pourquoi ce choix : [1-2 phrases — pourquoi c'est le meilleur shot pour profile visits + follows aujourd'hui].</span>
</p>

<h3 style="color:#4E33F1; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:24px 0 8px;">Post du jour (ready to paste)</h3>
<div style="background:#f7f7fb; padding:16px; border-radius:8px; white-space:pre-wrap; font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size:13px; line-height:1.55;">[Full LinkedIn post copy, 150-250 words, final draft]</div>

<h3 style="color:#4E33F1; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:24px 0 8px;">Carrousel du jour (9-10 slides)</h3>
<div style="background:#f7f7fb; padding:16px; border-radius:8px; white-space:pre-wrap; font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size:13px; line-height:1.55;">Slide 1 — COVER
Titre : [...]
Sous-titre : [...]

Slide 2 — [Headline]
[1-2 body lines]

[...through Slide 10 — CTA...]</div>

<h3 style="color:#4E33F1; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:24px 0 8px;">Script vidéo du jour (45-90s)</h3>
<div style="background:#f7f7fb; padding:16px; border-radius:8px; white-space:pre-wrap; font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size:13px; line-height:1.55;">[HOOK]
[...]

[PIVOT]
[...]

[BODY]
[...]

[CLOSE]
[...]</div>

<p style="color:#888; font-size:12px; margin-top:32px;">Méthode : LinkedIn posts uniquement (>100 réactions · 30 jours). Content pack auto-généré.<br>Prochain brief : demain 7:47 AM.</p>
</body>
</html>"""


def run_veille() -> str:
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    today = date.today().isoformat()

    message = client.messages.create(
        model=MODEL,
        max_tokens=6000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Today is {today}. Produce the full daily email: brief + content pack. "
                    f"1) Search site:linkedin.com/posts for 3-5 viral posts (past 30 days, >100 reactions) "
                    f"at the AI × growth marketing intersection. Verify each via web search. "
                    f"2) Pick the single best topic from those posts for Khadija to post about today — "
                    f"optimize for profile visits + follows, broad reach, her storytelling voice. "
                    f"3) Generate the full content pack: post + carrousel + video script, all in her voice. "
                    f"Output only the HTML, no preamble."
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

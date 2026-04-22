#!/usr/bin/env python3
"""Daily content brief for Khadija's personal brand.
No web search (fits trial tier rate limits). Generates topic + post + carousel + video script
from Claude's knowledge of AI × growth marketing trends.
"""
import os
import re
import json
import time
import smtplib
import ssl
from datetime import date
from email.message import EmailMessage
from anthropic import Anthropic

# Visual assets (PDF carousel + PNG thumbnail) are generated via
# carousel_gen.py and thumbnail_gen.py — currently NOT called from the pipeline.
# See /Users/khadijakamoun/Desktop/khadija-second-brain/personal-brand-brain/
# projets/veille-daily/carousel_skill/ for the real playbook template; daily
# auto-generation requires a proper Jinja2 + WeasyPrint rebuild (planned).

GMAIL_USER = os.environ.get("GMAIL_USER", "kamoun@digigram.com")
RECIPIENT = GMAIL_USER
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

MODEL = "claude-haiku-4-5"

ANGLE_SYSTEM = """You suggest daily content angles for Khadija's personal brand at the AI × growth marketing × digital marketing intersection.

CONTEXT:
- Audience: growth operators, founders, sales/marketing leaders (broad reach preferred, not niche).
- Her voice: storytelling, first-person, conversational, contractions, broad-reach hooks.
- Never mention Digigram, her employer, her day job.
- 2026 goals: LinkedIn profile visits + head hunters finding her + 4 posts/week cadence.
- Don't invent specific viral posts or citations — you don't have live data.

YOUR TASK: suggest 3 specific, contrarian, data-rich angles she could post today. Then pick the best one.

OUTPUT (strict JSON, no preamble, no code fences):
{
  "angles": [
    {"title": "[angle 1 in 1 punchy phrase]", "why": "[1 sentence why it works]"},
    {"title": "[angle 2]", "why": "[why]"},
    {"title": "[angle 3]", "why": "[why]"}
  ],
  "chosen_index": 0,
  "chosen_reason": "[1-2 sentences why this is the best shot today for profile visits + follows]"
}"""

PACK_SYSTEM = """You write Khadija's daily content pack from a chosen topic.

VOICE: storytelling, first-person ("I", "you"), contractions, broad-reach hooks.
NEVER mention Digigram, her employer, her day job.
2026 goals: profile visits + head hunters + 4 posts/week.

POST (150-250 words): hook (1 line, scroll-stopping) → 3-4 punch lines → pivot ("Then X happened.") → credibility line → 5-6 bullets (last = stat/outcome) → philosophy closer ending with "!!!" → "⬇" + hashtag line.

CARROUSEL (10 slides): S1 COVER (title max 6 words + subtitle). S2-S8 one idea each (bold headline max 8 words + 1-2 body lines, progressive build). S9 TAKEAWAY (3 lines recap). S10 CTA (Follow for more + one ask).

VIDEO SCRIPT (45-90s, max 180 words): [HOOK] / [PIVOT] / [BODY] / [CLOSE]. One sentence per line, sections in [BRACKETS], numbers written in words.

OUTPUT (strict JSON, no preamble, no code fences):
{
  "post": "[full post copy]",
  "carrousel": "Slide 1 — COVER\\nTitre : ...\\nSous-titre : ...\\n\\nSlide 2 — [Headline]\\n[body]\\n\\n...\\n\\nSlide 10 — CTA\\n...",
  "video_script": "[HOOK]\\n...\\n\\n[PIVOT]\\n...\\n\\n[BODY]\\n...\\n\\n[CLOSE]\\n..."
}"""


def parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError(f"No JSON: {text[:300]}")
    return json.loads(m.group(0))


def call_angles(client: Anthropic) -> dict:
    msg = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=ANGLE_SYSTEM,
        messages=[{"role": "user", "content": "Propose 3 content angles for today and pick the best."}],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    return parse_json(text)


def call_pack(client: Anthropic, topic: str, reason: str) -> dict:
    msg = client.messages.create(
        model=MODEL,
        max_tokens=3500,
        system=PACK_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"Topic : {topic}\nWhy : {reason}\n\nGenerate the content pack.",
        }],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    return parse_json(text)


def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_html(today: str, angles_data: dict, pack: dict) -> str:
    chosen_idx = angles_data["chosen_index"]
    chosen = angles_data["angles"][chosen_idx]
    angles_html = ""
    for i, a in enumerate(angles_data["angles"]):
        marker = "★" if i == chosen_idx else "·"
        angles_html += (
            f'<p style="margin:8px 0;">{marker} <b>{html_escape(a["title"])}</b> '
            f'<span style="color:#666; font-size:13px;">— {html_escape(a["why"])}</span></p>'
        )

    post = html_escape(pack["post"])
    carrousel = html_escape(pack["carrousel"])
    video = html_escape(pack["video_script"])

    return f"""<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif; font-size: 15px; line-height: 1.55; color: #222; max-width: 640px;">
<p style="color:#888; font-size:12px; letter-spacing:1px; text-transform:uppercase; margin:0 0 4px;">Veille Khadija — {today} · AI × growth × digital marketing</p>
<h2 style="margin:0 0 6px; font-size:20px;">Brief + content pack du jour</h2>
<p style="color:#999; font-size:12px; margin:0 0 20px;">Mode : angles + content pack (pas de tracking viral live — trial tier Anthropic).</p>

<h3 style="color:#4E33F1; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:24px 0 8px;">3 angles du jour</h3>
{angles_html}

<h3 style="color:#FF575A; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:28px 0 8px;">Sujet choisi</h3>
<p style="background:#FFF5F5; padding:10px 14px; border-left:3px solid #FF575A; margin:0 0 16px;">
<b>{html_escape(chosen["title"])}</b><br>
<span style="color:#555; font-size:13px;">Pourquoi : {html_escape(angles_data["chosen_reason"])}</span>
</p>

<h3 style="color:#4E33F1; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:24px 0 8px;">Post du jour (ready to paste)</h3>
<div style="background:#f7f7fb; padding:16px; border-radius:8px; white-space:pre-wrap; font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size:13px; line-height:1.55;">{post}</div>

<h3 style="color:#4E33F1; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:24px 0 8px;">Carrousel du jour (10 slides)</h3>
<div style="background:#f7f7fb; padding:16px; border-radius:8px; white-space:pre-wrap; font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size:13px; line-height:1.55;">{carrousel}</div>

<h3 style="color:#4E33F1; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:24px 0 8px;">Script vidéo du jour (45-90s)</h3>
<div style="background:#f7f7fb; padding:16px; border-radius:8px; white-space:pre-wrap; font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size:13px; line-height:1.55;">{video}</div>

<p style="color:#888; font-size:12px; margin-top:32px;">Prochain brief : demain 7:47 AM. Upgrade Anthropic Tier 1 pour ré-activer le tracking viral live.</p>
</body>
</html>"""


def send_email(html: str, subject: str):
    msg = EmailMessage()
    msg["From"] = GMAIL_USER
    msg["To"] = RECIPIENT
    msg["Subject"] = subject
    msg.set_content("HTML-capable client required.")
    msg.add_alternative(html, subtype="html")
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
        s.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        s.send_message(msg)


def main():
    today = date.today().isoformat()
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    print(f"[{today}] Call 1: angles...")
    angles = call_angles(client)
    chosen = angles["angles"][angles["chosen_index"]]
    print(f"  Chosen: {chosen['title']}")

    print("Sleep 65s (rate-limit safety)...")
    time.sleep(65)

    print("Call 2: content pack...")
    pack = call_pack(client, chosen["title"], angles["chosen_reason"])

    html = build_html(today, angles, pack)
    print(f"HTML: {len(html)} chars")
    send_email(html, f"Veille Khadija — {today}")
    print("Sent.")


if __name__ == "__main__":
    main()

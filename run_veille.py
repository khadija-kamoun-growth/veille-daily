#!/usr/bin/env python3
"""Daily veille + content pack for Khadija's personal brand.
Two-call split to fit under 10K TPM rate limits:
  Call 1 (web search): veille brief + pick topic of the day
  Sleep 65s (rate limit window)
  Call 2 (no tools): generate post + carousel + video script on chosen topic
Emails combined HTML via SMTP.
"""
import os
import re
import sys
import time
import smtplib
import ssl
from datetime import date
from email.message import EmailMessage
from anthropic import Anthropic

GMAIL_USER = os.environ.get("GMAIL_USER", "kamoun@digigram.com")
RECIPIENT = GMAIL_USER
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

MODEL = "claude-haiku-4-5"

BRIEF_SYSTEM = """You produce Khadija's veille brief: viral LinkedIn posts at the AI × growth marketing × digital marketing intersection.

RULES:
- 3-5 posts max. linkedin.com/posts/ URLs only. Past 30 days. >100 reactions OR >50 comments.
- Focus AI × growth × digital marketing. No generalists.
- Same creator not twice in a week.
- If <3 qualify, ship fewer + honest note. Never pad with articles.

At the end, pick ONE topic from the posts as "sujet du jour" — the one most likely to drive profile visits + follows for a growth operator brand (contrarian, specific, data-rich).

OUTPUT (strict JSON object, no preamble, no code fences):
{
  "brief_html": "<h3 style='color:#4E33F1; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:24px 0 8px;'>Posts viraux (30 derniers jours)</h3><p><b>[Creator] — il y a [X]</b> · <span style='color:#666;'>[N] réactions · [M] commentaires</span><br>\\"[Hook]\\". Thèse : [1 phrase]. <a href='[URL]'>Voir le post</a></p>[...3-5 posts...]",
  "topic": "[1 punchy phrase describing the chosen topic]",
  "topic_reasoning": "[1-2 sentences why this is the best shot today]",
  "topic_source_post_url": "[linkedin.com/posts URL that inspired the topic]"
}"""

PACK_SYSTEM = """You are Khadija's content pack writer. From a chosen topic, produce a post + carousel + video script in her voice.

VOICE:
- Storytelling, first-person ("I", "you"), conversational, contractions.
- Never mention Digigram, her employer, or her day job.
- Broad-reach hooks optimizing for profile visits + follows (she wants everyone to react).
- Tied to 2026 goals: profile visits + head hunters + 4 posts/week.

POST (150-250 words, ready to paste):
Hook (1 scroll-stopping line) → 3-4 punch lines → pivot (e.g. "Then X happened.") → credibility/insight line → 5-6 bullets (last = stat/outcome) → philosophy closer ending with "!!!" → "⬇" + hashtag line.

CARROUSEL (10 slides, Canva-ready text):
Slide 1 COVER: big title (max 6 words) + subtitle.
Slides 2-8: one key idea each — bold headline (max 8 words) + 1-2 body lines. Progressive build.
Slide 9: TAKEAWAY — 3 lines recap.
Slide 10: CTA — "Follow for more" + one ask (save / share / DM).

VIDEO SCRIPT (45-90s, max 180 words, ready to record):
[HOOK] 1 line. [PIVOT] short. [BODY] 3-4 points. [CLOSE] provocation + CTA.
Plain text, one sentence per line, sections in [BRACKETS]. Numbers written in words.

OUTPUT (strict JSON, no preamble, no code fences):
{
  "post": "[full LinkedIn post copy, 150-250 words]",
  "carrousel": "Slide 1 — COVER\\nTitre : ...\\nSous-titre : ...\\n\\nSlide 2 — [Headline]\\n[body]\\n\\n...\\n\\nSlide 10 — CTA\\n[text]",
  "video_script": "[HOOK]\\n...\\n\\n[PIVOT]\\n...\\n\\n[BODY]\\n...\\n\\n[CLOSE]\\n..."
}"""


def call_brief(client: Anthropic, today: str) -> dict:
    import json
    msg = client.messages.create(
        model=MODEL,
        max_tokens=3500,
        system=BRIEF_SYSTEM,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 2}],
        messages=[{
            "role": "user",
            "content": (
                f"Today is {today}. Search site:linkedin.com/posts for viral AI × growth marketing posts "
                f"from the past 30 days. Pick 3-5 that pass the filters. Pick the single best topic for "
                f"Khadija to post about today. Output strict JSON."
            ),
        }],
    )
    text = "".join(b.text for b in msg.content if b.type == "text").strip()
    # Strip code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # Find JSON object
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError(f"No JSON in brief response: {text[:500]}")
    return json.loads(m.group(0))


def call_pack(client: Anthropic, topic: str, reasoning: str, source_url: str) -> dict:
    import json
    msg = client.messages.create(
        model=MODEL,
        max_tokens=3500,
        system=PACK_SYSTEM,
        messages=[{
            "role": "user",
            "content": (
                f"Topic : {topic}\n"
                f"Why chosen : {reasoning}\n"
                f"Source post : {source_url}\n\n"
                f"Generate the content pack (post + carrousel + video script) in Khadija's voice. "
                f"Output strict JSON."
            ),
        }],
    )
    text = "".join(b.text for b in msg.content if b.type == "text").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError(f"No JSON in pack response: {text[:500]}")
    return json.loads(m.group(0))


def html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_html(today: str, brief: dict, pack: dict) -> str:
    post = html_escape(pack["post"])
    carrousel = html_escape(pack["carrousel"])
    video_script = html_escape(pack["video_script"])

    return f"""<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif; font-size: 15px; line-height: 1.55; color: #222; max-width: 640px;">
<p style="color:#888; font-size:12px; letter-spacing:1px; text-transform:uppercase; margin:0 0 4px;">Veille Khadija — {today} · AI × growth × digital marketing</p>
<h2 style="margin:0 0 20px; font-size:20px;">Brief + content pack du jour</h2>

{brief["brief_html"]}

<h3 style="color:#FF575A; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:28px 0 8px;">Sujet du jour (choisi)</h3>
<p style="background:#FFF5F5; padding:10px 14px; border-left:3px solid #FF575A; margin:0 0 16px;">
<b>{html_escape(brief["topic"])}</b><br>
<span style="color:#555; font-size:13px;">Pourquoi : {html_escape(brief["topic_reasoning"])}</span>
</p>

<h3 style="color:#4E33F1; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:24px 0 8px;">Post du jour (ready to paste)</h3>
<div style="background:#f7f7fb; padding:16px; border-radius:8px; white-space:pre-wrap; font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size:13px; line-height:1.55;">{post}</div>

<h3 style="color:#4E33F1; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:24px 0 8px;">Carrousel du jour (10 slides)</h3>
<div style="background:#f7f7fb; padding:16px; border-radius:8px; white-space:pre-wrap; font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size:13px; line-height:1.55;">{carrousel}</div>

<h3 style="color:#4E33F1; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:24px 0 8px;">Script vidéo du jour (45-90s)</h3>
<div style="background:#f7f7fb; padding:16px; border-radius:8px; white-space:pre-wrap; font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size:13px; line-height:1.55;">{video_script}</div>

<p style="color:#888; font-size:12px; margin-top:32px;">Méthode : veille + content pack auto-généré. Prochain brief : demain 7:47 AM.</p>
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
    subject = f"Veille Khadija — {today}"
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    print(f"Call 1: brief + topic pick ({today})...")
    brief = call_brief(client, today)
    print(f"  Topic: {brief['topic']}")

    print("Sleeping 65s for rate limit window...")
    time.sleep(65)

    print("Call 2: content pack...")
    pack = call_pack(client, brief["topic"], brief["topic_reasoning"], brief.get("topic_source_post_url", ""))

    html = build_html(today, brief, pack)
    print(f"HTML length: {len(html)} chars")
    send_email(html, subject)
    print(f"Sent: {subject}")


if __name__ == "__main__":
    main()

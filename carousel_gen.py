"""Carousel PDF generator for Khadija's daily brief.
Parses the LLM's 10-slide carousel script into structured slides,
renders each as a 1080x1350 PNG with her brand palette, merges into a PDF.
"""
import re
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Brand palette
PRIMARY = (78, 51, 241)       # #4E33F1 violet
SECONDARY = (255, 87, 90)     # #FF575A coral
AUX1 = (146, 129, 253)        # #9281FD lavender
LIGHT = (255, 255, 255)
DARK_BG = (14, 8, 32)         # #0E0820 deep violet night
PRIMARY_BG_GRADIENT_TOP = (26, 15, 61)     # #1A0F3D
SLIDE_W, SLIDE_H = 1080, 1350

ASSETS_DIR = Path(__file__).parent / "assets"
PHOTO_PATH = ASSETS_DIR / "khadija.png"


def _load_font(size: int, weight: str = "Regular") -> ImageFont.FreeTypeFont:
    # Try Inter (brand font) from system, fallback to DejaVu
    candidates = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        f"/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        f"/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    # Prefer bold for headings
    if "Bold" in weight or "Black" in weight:
        for c in candidates:
            if "Bold" in c and Path(c).exists():
                return ImageFont.truetype(c, size)
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def _wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    cur = []
    for w in words:
        trial = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def _draw_multiline(draw, xy, lines, font, fill, line_spacing=10):
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        y += (bbox[3] - bbox[1]) + line_spacing


def _vertical_gradient(size, color_top, color_bottom):
    img = Image.new("RGB", size, color_top)
    top_r, top_g, top_b = color_top
    bot_r, bot_g, bot_b = color_bottom
    h = size[1]
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top_r + (bot_r - top_r) * t)
        g = int(top_g + (bot_g - top_g) * t)
        b = int(top_b + (bot_b - top_b) * t)
        ImageDraw.Draw(img).line([(0, y), (size[0], y)], fill=(r, g, b))
    return img


def render_cover(title: str, subtitle: str, episode_tag: str = "PLAYBOOK · DU JOUR") -> Image.Image:
    img = _vertical_gradient((SLIDE_W, SLIDE_H), PRIMARY_BG_GRADIENT_TOP, DARK_BG)
    draw = ImageDraw.Draw(img)

    # Episode tag
    tag_font = _load_font(28, "Bold")
    draw.text((60, 60), episode_tag.upper(), font=tag_font, fill=AUX1)

    # Title block
    title_font = _load_font(100, "Bold")
    sub_font = _load_font(38, "Regular")
    title_lines = _wrap_text(draw, title.upper(), title_font, SLIDE_W - 120)
    _draw_multiline(draw, (60, 260), title_lines, title_font, LIGHT, line_spacing=8)

    # Subtitle under title
    y_after_title = 260 + len(title_lines) * 110 + 30
    sub_lines = _wrap_text(draw, subtitle, sub_font, SLIDE_W - 120)
    _draw_multiline(draw, (60, y_after_title), sub_lines, sub_font, AUX1, line_spacing=6)

    # Photo on right side bottom
    if PHOTO_PATH.exists():
        photo = Image.open(PHOTO_PATH).convert("RGBA")
        # Scale to fit roughly 500px wide, anchored bottom-right
        ratio = 500 / photo.width
        new_size = (500, int(photo.height * ratio))
        photo = photo.resize(new_size, Image.LANCZOS)
        pos = (SLIDE_W - new_size[0] - 30, SLIDE_H - new_size[1] - 60)
        img.paste(photo, pos, photo if photo.mode == "RGBA" else None)

    # Bottom coral bar
    draw.rectangle([(0, SLIDE_H - 12), (SLIDE_W, SLIDE_H)], fill=SECONDARY)

    # Top-right violet L-bracket
    bw = 6
    L = 70
    draw.rectangle([(SLIDE_W - 40 - L, 40), (SLIDE_W - 40, 40 + bw)], fill=PRIMARY)
    draw.rectangle([(SLIDE_W - 40 - bw, 40), (SLIDE_W - 40, 40 + L)], fill=PRIMARY)

    # Byline bottom-left
    byline_font = _load_font(22, "Bold")
    draw.text((60, SLIDE_H - 90), "by Khadija Kamoun", font=byline_font, fill=LIGHT)
    url_font = _load_font(18, "Regular")
    draw.text((60, SLIDE_H - 60), "khadijakamoun.com", font=url_font, fill=AUX1)

    return img


def render_content_slide(slide_num: int, headline: str, body: str) -> Image.Image:
    img = Image.new("RGB", (SLIDE_W, SLIDE_H), LIGHT)
    draw = ImageDraw.Draw(img)

    # Top accent bar (violet)
    draw.rectangle([(0, 0), (SLIDE_W, 8)], fill=PRIMARY)

    # Slide number big on left
    num_font = _load_font(140, "Bold")
    draw.text((60, 80), f"{slide_num:02d}", font=num_font, fill=SECONDARY)

    # Headline
    head_font = _load_font(68, "Bold")
    head_lines = _wrap_text(draw, headline.upper(), head_font, SLIDE_W - 120)
    _draw_multiline(draw, (60, 280), head_lines, head_font, DARK_BG, line_spacing=8)

    # Divider
    y_div = 280 + len(head_lines) * 80 + 30
    draw.rectangle([(60, y_div), (220, y_div + 4)], fill=PRIMARY)

    # Body
    body_font = _load_font(38, "Regular")
    body_lines = _wrap_text(draw, body, body_font, SLIDE_W - 120)
    _draw_multiline(draw, (60, y_div + 40), body_lines, body_font, (60, 60, 90), line_spacing=14)

    # Bottom bar and page number
    draw.rectangle([(0, SLIDE_H - 6), (SLIDE_W, SLIDE_H)], fill=SECONDARY)
    page_font = _load_font(22, "Bold")
    draw.text((SLIDE_W - 80, SLIDE_H - 50), f"{slide_num}/10", font=page_font, fill=AUX1)
    sig_font = _load_font(18, "Bold")
    draw.text((60, SLIDE_H - 50), "@khadija-kamoun-growth", font=sig_font, fill=(140, 140, 160))

    return img


def render_takeaway_slide(lines: list[str]) -> Image.Image:
    img = _vertical_gradient((SLIDE_W, SLIDE_H), PRIMARY_BG_GRADIENT_TOP, DARK_BG)
    draw = ImageDraw.Draw(img)

    tag_font = _load_font(28, "Bold")
    draw.text((60, 60), "TAKEAWAY", font=tag_font, fill=SECONDARY)

    body_font = _load_font(56, "Bold")
    y = 260
    for line in lines[:3]:
        wrapped = _wrap_text(draw, line, body_font, SLIDE_W - 120)
        _draw_multiline(draw, (60, y), wrapped, body_font, LIGHT, line_spacing=8)
        y += len(wrapped) * 68 + 30

    draw.rectangle([(0, SLIDE_H - 12), (SLIDE_W, SLIDE_H)], fill=SECONDARY)
    return img


def render_cta_slide(cta_text: str) -> Image.Image:
    img = _vertical_gradient((SLIDE_W, SLIDE_H), PRIMARY_BG_GRADIENT_TOP, DARK_BG)
    draw = ImageDraw.Draw(img)

    tag_font = _load_font(32, "Bold")
    draw.text((60, 60), "FOLLOW FOR MORE", font=tag_font, fill=SECONDARY)

    cta_font = _load_font(86, "Bold")
    lines = _wrap_text(draw, cta_text.upper(), cta_font, SLIDE_W - 120)
    _draw_multiline(draw, (60, 260), lines, cta_font, LIGHT, line_spacing=10)

    # Handle + url
    handle_font = _load_font(40, "Bold")
    draw.text((60, SLIDE_H - 200), "by Khadija Kamoun", font=handle_font, fill=LIGHT)
    url_font = _load_font(28, "Regular")
    draw.text((60, SLIDE_H - 150), "khadijakamoun.com", font=url_font, fill=AUX1)

    # Big arrow icon
    arrow_font = _load_font(120, "Bold")
    draw.text((SLIDE_W - 180, SLIDE_H - 220), "→", font=arrow_font, fill=PRIMARY)

    draw.rectangle([(0, SLIDE_H - 12), (SLIDE_W, SLIDE_H)], fill=SECONDARY)
    return img


def parse_carousel(text: str) -> list[dict]:
    """Parse LLM carousel text into list of slide dicts."""
    slides = []
    # Split by "Slide N" or "Slide N —" etc.
    raw_blocks = re.split(r"\n\s*Slide\s+(\d+)\s*[—\-:]\s*", "\n" + text)
    # raw_blocks format: ['', '1', 'COVER\nTitre: ...', '2', 'Headline\nBody', ...]
    i = 1
    while i < len(raw_blocks):
        num = int(raw_blocks[i])
        body = raw_blocks[i + 1].strip() if i + 1 < len(raw_blocks) else ""
        slides.append({"num": num, "body": body})
        i += 2
    return slides


def render_slides_from_text(carousel_text: str, cover_title: str) -> list[Image.Image]:
    slides_raw = parse_carousel(carousel_text)
    imgs = []
    for s in slides_raw:
        num = s["num"]
        body = s["body"]
        if num == 1:
            # Parse Titre + Sous-titre
            title_m = re.search(r"Titre\s*:\s*(.+)", body)
            sub_m = re.search(r"Sous-?titre\s*:\s*(.+)", body)
            title = (title_m.group(1) if title_m else cover_title).strip()
            subtitle = (sub_m.group(1) if sub_m else "").strip()
            imgs.append(render_cover(title, subtitle))
        elif num == 9:
            # TAKEAWAY — 3 lines
            lines = [l.strip(" -•*\t") for l in body.split("\n") if l.strip()]
            imgs.append(render_takeaway_slide(lines))
        elif num == 10:
            # CTA
            imgs.append(render_cta_slide(body.split("\n")[0] if body else "FOLLOW FOR MORE"))
        else:
            # Standard content: headline on first line, body on rest
            parts = body.split("\n", 1)
            headline = parts[0].strip().lstrip("[").rstrip("]")
            body_text = parts[1].strip() if len(parts) > 1 else ""
            imgs.append(render_content_slide(num, headline, body_text))
    # Ensure we have 10 slides — pad if needed
    while len(imgs) < 10:
        imgs.append(render_content_slide(len(imgs) + 1, "...", ""))
    return imgs[:10]


def build_pdf(carousel_text: str, cover_title: str, output_path: str):
    imgs = render_slides_from_text(carousel_text, cover_title)
    # Save as multi-page PDF
    rgb_imgs = [im.convert("RGB") for im in imgs]
    rgb_imgs[0].save(output_path, save_all=True, append_images=rgb_imgs[1:], format="PDF")
    return output_path


if __name__ == "__main__":
    sample = """Slide 1 — COVER
Titre : 5 WORKFLOWS GROWTH
Sous-titre : Les outils AI que j'utilise chaque lundi

Slide 2 — Pipeline velocity
C'est la métrique que tu dois suivre chaque semaine.
Si elle stagne, tout le reste est du bruit.

Slide 3 — Signal over volume
Arrête de spammer. Commence à filtrer.
Les intent signals battent le volume à 10× la conversion.

Slide 4 — AI augmente, ne remplace pas
Research, CRM, prep : automatise.
Conversations : toujours humain.

Slide 5 — Cycle deals +40%
Les deals prennent 40 pourcent plus de temps qu'en 2023.
Stop pushing. Start nurturing.

Slide 6 — AEO > SEO
Google's 60% zero-click. Les LLMs sont la nouvelle SERP.
Optimise pour les citations AI.

Slide 7 — LinkedIn > Google Ads
Budgets LinkedIn grandissent 5× plus vite que Google.
Les conversations B2B migrent.

Slide 8 — Nurture wins
Les teams qui gagnent ne poussent pas plus fort.
Elles jouent le jeu à 6 mois.

Slide 9 — TAKEAWAY
Pipeline velocity > vanity metrics.
Signals > forms.
AI augmente, ne remplace pas.

Slide 10 — CTA
Follow pour plus de playbooks growth."""
    build_pdf(sample, "5 WORKFLOWS GROWTH", "/tmp/test_carousel.pdf")
    print("OK /tmp/test_carousel.pdf")

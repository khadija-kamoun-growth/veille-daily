"""Carousel PDF generator matching Khadija's Apollo / GEO playbook style.

Style rules (copied from her playbooks):
- Light lavender gradient background (#F8F5FF → #E8E4FD) for cover/chapter slides
- White background for content slides, light accents
- Top-left nav: avatar circle + "Khadija Kamoun ✓" label
- Top-right GEO-like tag (bordered pill with brand letters)
- Monospace tag pills scattered with colored dots (e.g. • website.visit)
- Huge bold title with COLORED ACCENT WORDS (coral or violet, with underline)
- Photo floating on right, pointing at an illustration
- Content slides: numbered card layout with takeaway callouts (red-bordered)
- Bottom: Khadija avatar pill + "SWIPE <<<" pill + page number
"""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Brand palette (exact hex from mon-positionnement.md)
PRIMARY = (78, 51, 241)        # #4E33F1 violet
SECONDARY = (255, 87, 90)      # #FF575A coral
AUX1 = (146, 129, 253)         # #9281FD lavender
AUX2 = (248, 162, 182)         # #F8A2B6 pink
LIGHT = (255, 255, 255)
DARK = (14, 8, 32)             # #0E0820
SOFT_BG_TOP = (248, 245, 255)  # very light lavender
SOFT_BG_BOT = (224, 220, 251)  # soft lavender
INK = (36, 34, 66)             # dark navy-ish (body text)
MUTED = (110, 112, 150)        # muted text
BORDER = (200, 195, 240)       # border of cards

SLIDE_W, SLIDE_H = 1080, 1350

ASSETS_DIR = Path(__file__).parent / "assets"
PHOTO_PATH = ASSETS_DIR / "khadija.png"


# ---------- Font loader ----------
def _font(size: int, weight: str = "Regular", mono: bool = False) -> ImageFont.FreeTypeFont:
    mono_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
    ]
    bold_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/SFNSRounded.ttf",
    ]
    regular_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    pool = mono_candidates if mono else (bold_candidates if weight in ("Bold", "Black") else regular_candidates)
    for c in pool:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ---------- Helpers ----------
def _wrap(draw, text, font, max_w):
    words = text.split()
    lines = []
    cur = []
    for w in words:
        trial = " ".join(cur + [w])
        bb = draw.textbbox((0, 0), trial, font=font)
        if bb[2] - bb[0] <= max_w:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def _draw_rounded_pill(draw, xy, text, font, fg=PRIMARY, bg=(255, 255, 255), border=None, dot_color=None, padx=16, pady=8):
    x, y = xy
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    dot_w = 18 if dot_color else 0
    w = tw + 2 * padx + dot_w
    h = th + 2 * pady
    draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=h // 2, fill=bg, outline=border, width=2 if border else 0)
    cx = x + padx
    if dot_color:
        dot_r = 5
        dy = (h // 2) - dot_r
        draw.ellipse([(cx, y + dy), (cx + 2 * dot_r, y + dy + 2 * dot_r)], fill=dot_color)
        cx += dot_w
    draw.text((cx, y + pady - bb[1]), text, font=font, fill=fg)
    return (w, h)


def _gradient(size, top, bottom):
    img = Image.new("RGB", size, top)
    d = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / max(size[1] - 1, 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        d.line([(0, y), (size[0], y)], fill=(r, g, b))
    return img


def _top_nav(draw, img, title_text="Khadija Kamoun"):
    """Draw the top nav bar: KK avatar circle + name + verified check."""
    # Avatar circle with KK
    draw.ellipse([(50, 50), (110, 110)], fill=PRIMARY)
    f_avatar = _font(24, "Bold")
    bb = draw.textbbox((0, 0), "KK", font=f_avatar)
    draw.text((80 - (bb[2] - bb[0]) // 2, 80 - (bb[3] - bb[1]) // 2 - 2), "KK", font=f_avatar, fill=LIGHT)
    # Name
    f_name = _font(22, "Bold")
    draw.text((130, 68), title_text, font=f_name, fill=INK)
    # Verified checkmark (small violet)
    cx = 130 + draw.textbbox((0, 0), title_text, font=f_name)[2] + 10
    draw.ellipse([(cx, 72), (cx + 20, 92)], fill=PRIMARY)
    f_check = _font(14, "Bold")
    draw.text((cx + 5, 74), "✓", font=f_check, fill=LIGHT)


def _bottom_bar(draw, img, page_num, total=10):
    """Draw bottom: Khadija avatar pill + SWIPE indicator + page num."""
    # Left: Khadija pill
    # Avatar circle (pink-ish)
    draw.ellipse([(50, SLIDE_H - 90), (130, SLIDE_H - 10)], fill=AUX2)
    # Name stacked
    f = _font(22, "Bold")
    draw.text((145, SLIDE_H - 85), "Khadija", font=f, fill=PRIMARY)
    draw.text((145, SLIDE_H - 55), "kamoun", font=f, fill=INK)

    # Center: SWIPE pill (rounded border, coral dots/text)
    swipe_font = _font(20, "Bold")
    swipe_text = "SWIPE <<<"
    bb = draw.textbbox((0, 0), swipe_text, font=swipe_font)
    sw_w = bb[2] - bb[0] + 50
    sw_h = 44
    sw_x = (SLIDE_W - sw_w) // 2
    sw_y = SLIDE_H - 70
    draw.rounded_rectangle([(sw_x, sw_y), (sw_x + sw_w, sw_y + sw_h)], radius=22, outline=SECONDARY, width=2)
    draw.text((sw_x + 25, sw_y + 10), swipe_text, font=swipe_font, fill=SECONDARY)

    # Right: page number
    pf = _font(20, "Regular")
    page_text = f"{page_num}"
    bb = draw.textbbox((0, 0), page_text, font=pf)
    draw.text((SLIDE_W - 60 - (bb[2] - bb[0]), SLIDE_H - 55), page_text, font=pf, fill=MUTED)


def _draw_inline_colored(draw, xy, segments, font, line_spacing=8):
    """Draw a sequence of (text, color) segments inline, wrapping as needed.
    segments: [("normal ", INK), ("ACCENT", SECONDARY), (" word", INK)]
    Returns final y after drawing.
    """
    x, y = xy
    start_x = x
    # Simple approach: render word by word
    bb_h = draw.textbbox((0, 0), "Ag", font=font)
    line_h = (bb_h[3] - bb_h[1]) + line_spacing
    max_x = SLIDE_W - 60

    for text, color in segments:
        words = re.split(r"(\s+)", text)
        for w in words:
            if not w:
                continue
            bb = draw.textbbox((0, 0), w, font=font)
            ww = bb[2] - bb[0]
            if x + ww > max_x and w.strip():
                x = start_x
                y += line_h
            draw.text((x, y), w, font=font, fill=color)
            x += ww
    return y + line_h


# ---------- Cover slide ----------
def render_cover(title: str, subtitle: str, vol_tag: str = "PLAYBOOK · DU JOUR") -> Image.Image:
    img = _gradient((SLIDE_W, SLIDE_H), SOFT_BG_TOP, SOFT_BG_BOT)
    draw = ImageDraw.Draw(img)

    _top_nav(draw, img)

    # Top-right brand tag (bordered pill with letters like GEO)
    brand_font = _font(20, "Bold", mono=True)
    tag_w, _ = _draw_rounded_pill(draw, (SLIDE_W - 120, 60), "VEILLE", brand_font, fg=PRIMARY, bg=LIGHT, border=PRIMARY, padx=12, pady=6)

    # Section pill (PLAYBOOK · DU JOUR) with dot
    tag_font = _font(18, "Bold", mono=True)
    _draw_rounded_pill(draw, (60, 180), vol_tag, tag_font, fg=PRIMARY, bg=LIGHT, dot_color=SECONDARY, padx=14, pady=8)

    # Title — split on keywords for coloring
    title_font = _font(88, "Bold")
    # Simple heuristic: color first and last significant words with accents
    words = title.split()
    segments = []
    for i, w in enumerate(words):
        color = INK
        if i == 1 or i == len(words) - 1:
            color = SECONDARY if i % 2 == 1 else PRIMARY
        segments.append((w + (" " if i < len(words) - 1 else "."), color))
    _draw_inline_colored(draw, (60, 280), segments, title_font, line_spacing=4)

    # Subtitle
    sub_font = _font(30, "Regular")
    sub_lines = _wrap(draw, subtitle, sub_font, SLIDE_W - 580)
    y_sub = 580
    for line in sub_lines:
        draw.text((60, y_sub), line, font=sub_font, fill=MUTED)
        y_sub += 42

    # Photo right-side, with circle background (dotted circle behind like playbooks)
    if PHOTO_PATH.exists():
        photo = Image.open(PHOTO_PATH).convert("RGBA")
        ratio = 420 / photo.width
        new_size = (420, int(photo.height * ratio))
        photo = photo.resize(new_size, Image.LANCZOS)
        pos = (SLIDE_W - new_size[0] - 30, 230)
        # Dotted concentric circles behind photo
        cx, cy = pos[0] + new_size[0] // 2, pos[1] + new_size[1] // 2
        for r in [280, 230, 180]:
            bb = [(cx - r, cy - r), (cx + r, cy + r)]
            # approximate dotted by drawing arc sections
            for a in range(0, 360, 18):
                draw.arc(bb, start=a, end=a + 8, fill=AUX1, width=2)
        img.paste(photo, pos, photo if photo.mode == "RGBA" else None)

    # Floating monospace tag pills around photo (like website.visit, signal.detected, etc.)
    tag_pills = [
        ("• prompt.write()", PRIMARY, 690, 240),
        ("• viral.hook", SECONDARY, 80, 830),
        ("• post.engage", PRIMARY, 740, 640),
        ("• growth.compound", SECONDARY, 720, 920),
    ]
    pill_font = _font(16, "Bold", mono=True)
    for txt, col, x, y in tag_pills:
        _draw_rounded_pill(draw, (x, y), txt, pill_font, fg=col, bg=LIGHT, border=col, padx=12, pady=6)

    # Stats row (like >20%, <5m, 1h from Apollo)
    stats = [("fresh", "TOPIC"), ("10", "SLIDES"), ("1", "THUMBNAIL")]
    sx = 60
    sy = 1020
    for big, label in stats:
        box_w, box_h = 180, 90
        draw.rounded_rectangle([(sx, sy), (sx + box_w, sy + box_h)], radius=12, outline=PRIMARY, width=2)
        # Left accent line
        draw.rectangle([(sx, sy + 15), (sx + 4, sy + box_h - 15)], fill=SECONDARY)
        big_f = _font(34, "Bold")
        lbl_f = _font(14, "Bold", mono=True)
        draw.text((sx + 18, sy + 12), big, font=big_f, fill=INK)
        draw.text((sx + 18, sy + 58), label, font=lbl_f, fill=MUTED)
        sx += box_w + 20

    _bottom_bar(draw, img, page_num=1)
    return img


# ---------- Content slide (numbered card style) ----------
def render_content_slide(slide_num: int, headline: str, body: str, part_label: str = "Part 1 · Le sujet") -> Image.Image:
    img = Image.new("RGB", (SLIDE_W, SLIDE_H), LIGHT)
    draw = ImageDraw.Draw(img)
    # Very subtle gradient band at top
    band = _gradient((SLIDE_W, 180), SOFT_BG_TOP, LIGHT)
    img.paste(band, (0, 0))

    _top_nav(draw, img)

    # Part label mid-top center (coral mono)
    part_font = _font(18, "Bold", mono=True)
    bb = draw.textbbox((0, 0), part_label, font=part_font)
    draw.text(((SLIDE_W - (bb[2] - bb[0])) // 2, 74), part_label, font=part_font, fill=SECONDARY)

    # Big numbered badge on left
    num_box = 140
    nx, ny = 60, 220
    draw.rounded_rectangle([(nx, ny), (nx + num_box, ny + num_box)], radius=20, fill=PRIMARY)
    num_f = _font(72, "Bold")
    nt = f"{slide_num:02d}"
    bb = draw.textbbox((0, 0), nt, font=num_f)
    draw.text((nx + (num_box - (bb[2] - bb[0])) // 2, ny + (num_box - (bb[3] - bb[1])) // 2 - 4), nt, font=num_f, fill=LIGHT)

    # Headline right of number
    head_font = _font(72, "Bold")
    head_x = nx + num_box + 40
    head_lines = _wrap(draw, headline, head_font, SLIDE_W - head_x - 60)
    y = ny + 8
    for line in head_lines:
        draw.text((head_x, y), line, font=head_font, fill=INK)
        y += 84

    # Divider
    draw.rectangle([(60, ny + num_box + 60), (200, ny + num_box + 66)], fill=SECONDARY)

    # Body with colored accent on strong words (heuristic: detect quotes or numbers)
    body_font = _font(36, "Regular")
    body_start_y = ny + num_box + 100
    segments = []
    # Split body by words, accent any word that contains a digit or is ALL CAPS
    for i, w in enumerate(body.split()):
        col = SECONDARY if (any(c.isdigit() for c in w) or (w.isupper() and len(w) > 2)) else INK
        segments.append((w + " ", col))
    _draw_inline_colored(draw, (60, body_start_y), segments, body_font, line_spacing=10)

    # Takeaway callout at bottom
    cb_y = SLIDE_H - 280
    cb_h = 130
    draw.rounded_rectangle([(60, cb_y), (SLIDE_W - 60, cb_y + cb_h)], radius=12, fill=(255, 245, 245))
    # Left coral accent bar
    draw.rectangle([(60, cb_y), (68, cb_y + cb_h)], fill=SECONDARY)
    # TAKEAWAY tag
    tk_f = _font(18, "Bold", mono=True)
    draw.text((90, cb_y + 20), "TAKEAWAY", font=tk_f, fill=SECONDARY)
    # Generate a 1-line synthesis from headline
    tk_body = _font(22, "Regular")
    tk_text = f"{headline.split('.')[0][:90]}."
    draw.text((90, cb_y + 55), tk_text, font=tk_body, fill=INK)

    _bottom_bar(draw, img, page_num=slide_num)
    return img


# ---------- Part divider slide ----------
def render_part_slide(part_num: str, title: str) -> Image.Image:
    img = _gradient((SLIDE_W, SLIDE_H), PRIMARY, (34, 22, 140))
    draw = ImageDraw.Draw(img)
    _top_nav(draw, img, title_text="Khadija Kamoun")

    # PART · 0X in orange/yellow mono
    pf = _font(22, "Bold", mono=True)
    draw.text((SLIDE_W // 2 - 80, 500), f"PART · {part_num}", font=pf, fill=AUX2)
    # Huge coral title
    tf = _font(160, "Bold")
    bb = draw.textbbox((0, 0), title, font=tf)
    draw.text(((SLIDE_W - (bb[2] - bb[0])) // 2, 570), title, font=tf, fill=SECONDARY)
    # Subtitle (page range)
    sf = _font(22, "Regular")
    sub = f"— vol. du jour —"
    bb = draw.textbbox((0, 0), sub, font=sf)
    draw.text(((SLIDE_W - (bb[2] - bb[0])) // 2, 780), sub, font=sf, fill=AUX1)

    _bottom_bar(draw, img, page_num=0)
    return img


# ---------- Takeaway slide ----------
def render_takeaway_slide(lines: list[str], page_num: int = 9) -> Image.Image:
    img = _gradient((SLIDE_W, SLIDE_H), SOFT_BG_TOP, SOFT_BG_BOT)
    draw = ImageDraw.Draw(img)
    _top_nav(draw, img)

    # Title "3 things to remember."
    title_font = _font(84, "Bold")
    title = "3 choses à retenir."
    segments = [("3 choses à ", INK), ("retenir.", SECONDARY)]
    _draw_inline_colored(draw, (60, 200), segments, title_font)

    # 3 numbered cards stacked
    y = 420
    for i, line in enumerate(lines[:3], start=1):
        card_h = 160
        draw.rounded_rectangle([(60, y), (SLIDE_W - 60, y + card_h)], radius=16, fill=LIGHT, outline=BORDER, width=2)
        num_f = _font(64, "Bold")
        draw.text((90, y + 40), f"0{i}", font=num_f, fill=SECONDARY)
        line_f = _font(32, "Bold")
        line_lines = _wrap(draw, line, line_f, SLIDE_W - 280)
        ly = y + 40
        for l in line_lines[:2]:
            draw.text((210, ly), l, font=line_f, fill=INK)
            ly += 42
        y += card_h + 20

    _bottom_bar(draw, img, page_num=page_num)
    return img


# ---------- CTA slide ----------
def render_cta_slide(cta: str, page_num: int = 10) -> Image.Image:
    img = _gradient((SLIDE_W, SLIDE_H), PRIMARY, (24, 15, 100))
    draw = ImageDraw.Draw(img)
    _top_nav(draw, img, title_text="Khadija Kamoun")

    # Big title
    tag_f = _font(24, "Bold", mono=True)
    _draw_rounded_pill(draw, (60, 200), "GROW FASTER · CLOSE SMARTER", tag_f, fg=LIGHT, bg=(255, 255, 255, 30), border=AUX2, padx=14, pady=8)

    title_font = _font(96, "Bold")
    segments = []
    for i, w in enumerate(cta.split()):
        col = AUX2 if i % 2 == 1 else LIGHT
        segments.append((w + " ", col))
    _draw_inline_colored(draw, (60, 320), segments, title_font)

    # Three CTA pills
    pill_font = _font(22, "Bold")
    ctas = [("♡  Like if this helped", SECONDARY), ("+  Follow for more", LIGHT), ("◉  Save to come back", LIGHT)]
    y = 820
    for text, col in ctas:
        _draw_rounded_pill(draw, (60, y), text, pill_font, fg=LIGHT, bg=col if col == SECONDARY else (255, 255, 255, 40), border=LIGHT if col != SECONDARY else SECONDARY, padx=20, pady=12)
        y += 80

    # Photo bottom-right (smaller, for CTA personality)
    if PHOTO_PATH.exists():
        photo = Image.open(PHOTO_PATH).convert("RGBA")
        ratio = 360 / photo.width
        new_size = (360, int(photo.height * ratio))
        photo = photo.resize(new_size, Image.LANCZOS)
        pos = (SLIDE_W - new_size[0] - 20, SLIDE_H - new_size[1] - 80)
        img.paste(photo, pos, photo if photo.mode == "RGBA" else None)

    _bottom_bar(draw, img, page_num=page_num)
    return img


# ---------- Parser ----------
def parse_carousel(text: str) -> list[dict]:
    slides = []
    raw = re.split(r"\n\s*Slide\s+(\d+)\s*[—\-:]\s*", "\n" + text)
    i = 1
    while i < len(raw):
        num = int(raw[i])
        body = raw[i + 1].strip() if i + 1 < len(raw) else ""
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
            title_m = re.search(r"Titre\s*:\s*(.+)", body)
            sub_m = re.search(r"Sous-?titre\s*:\s*(.+)", body)
            title = (title_m.group(1) if title_m else cover_title).strip()
            subtitle = (sub_m.group(1) if sub_m else "").strip()
            imgs.append(render_cover(title, subtitle))
        elif num == 9:
            lines = [l.strip(" -•*\t") for l in body.split("\n") if l.strip()]
            imgs.append(render_takeaway_slide(lines, page_num=num))
        elif num == 10:
            cta_text = body.split("\n")[0] if body else "Follow pour plus"
            imgs.append(render_cta_slide(cta_text, page_num=num))
        else:
            parts = body.split("\n", 1)
            headline = parts[0].strip().lstrip("[").rstrip("]")
            body_text = parts[1].strip() if len(parts) > 1 else ""
            imgs.append(render_content_slide(num, headline, body_text))
    while len(imgs) < 10:
        imgs.append(render_content_slide(len(imgs) + 1, "…", ""))
    return imgs[:10]


def build_pdf(carousel_text: str, cover_title: str, output_path: str) -> str:
    imgs = render_slides_from_text(carousel_text, cover_title)
    rgb_imgs = [im.convert("RGB") for im in imgs]
    rgb_imgs[0].save(output_path, save_all=True, append_images=rgb_imgs[1:], format="PDF", resolution=150.0)
    return output_path


if __name__ == "__main__":
    sample = """Slide 1 — COVER
Titre : 5 workflows AI growth
Sous-titre : Les outils que j'utilise chaque lundi pour doubler mon pipeline

Slide 2 — Pipeline velocity beats vanity
C'est la métrique qui compte. Si elle stagne, tout le reste est bruit.
Suis-la chaque lundi matin.

Slide 3 — Signals over volume
Arrête de spammer. Commence à filtrer.
Les intent signals battent le volume à 10× la conversion.

Slide 4 — AI augmente, ne remplace pas
Research, CRM, prep : automatise.
Conversations : toujours humain.

Slide 5 — Deal cycles +40%
Les deals prennent 40 pourcent plus de temps qu'en 2023.
Stop pushing. Start nurturing.

Slide 6 — AEO > SEO en 2026
Google en zero-click 60%. Les LLMs sont la nouvelle SERP.
Optimise pour être cité.

Slide 7 — LinkedIn +5× Google Ads
Les budgets LinkedIn grandissent 5 fois plus vite.
Les conversations B2B migrent.

Slide 8 — Nurture > Push
Les teams qui gagnent ne forcent pas.
Elles jouent le jeu à 6 mois.

Slide 9 — TAKEAWAY
Pipeline velocity bat les vanity metrics.
Signals bat volume, toujours.
AI augmente, ne remplace jamais.

Slide 10 — CTA
Follow pour plus de playbooks growth"""
    build_pdf(sample, "5 workflows AI growth", "/tmp/test_carousel.pdf")
    print("OK /tmp/test_carousel.pdf")

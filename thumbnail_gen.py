"""Thumbnail PNG generator — viral YouTube style inspired by swipe file.

Reference patterns observed in the swipe file:
- Face dominant (centered or right-side, large)
- Huge bold text with thick black outline/stroke
- Accent color on key word (here: coral or violet)
- Hand-drawn-ish arrow curving toward the face or subject
- Optional number/stat card
- Gradient/vignette background (not flat)
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PRIMARY = (78, 51, 241)       # violet
SECONDARY = (255, 87, 90)     # coral
AUX1 = (146, 129, 253)
AUX2 = (248, 162, 182)
LIGHT = (255, 255, 255)
DARK = (14, 8, 32)
DARKER = (6, 3, 15)
YELLOW = (255, 232, 67)       # attention color used sparingly

W, H = 1280, 720
ASSETS_DIR = Path(__file__).parent / "assets"
PHOTO_PATH = ASSETS_DIR / "khadija.png"


def _font(size: int, weight="Bold") -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


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


def _text_stroke(draw, xy, text, font, fill, stroke=(0, 0, 0), stroke_w=5):
    draw.text(xy, text, font=font, fill=fill, stroke_width=stroke_w, stroke_fill=stroke)


def _gradient_bg(size, top, bottom):
    img = Image.new("RGB", size, top)
    d = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / max(size[1] - 1, 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        d.line([(0, y), (size[0], y)], fill=(r, g, b))
    return img


def _draw_arrow(draw, start, end, color, width=8, arrow_size=28):
    """Draw a thick curved-ish arrow via line + arrow head."""
    x0, y0 = start
    x1, y1 = end
    # Line
    draw.line([start, end], fill=color, width=width)
    # Arrow head (triangle at end)
    dx, dy = x1 - x0, y1 - y0
    ang = math.atan2(dy, dx)
    left = (x1 - arrow_size * math.cos(ang - math.radians(30)),
            y1 - arrow_size * math.sin(ang - math.radians(30)))
    right = (x1 - arrow_size * math.cos(ang + math.radians(30)),
             y1 - arrow_size * math.sin(ang + math.radians(30)))
    draw.polygon([left, (x1, y1), right], fill=color)


def _vignette(img):
    """Apply a dark vignette at edges for drama."""
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    # Bright center, dark edges
    for i in range(0, min(w, h) // 2, 10):
        alpha = int(255 * (i / (min(w, h) / 2)))
        d.rectangle([(i, i), (w - i, h - i)], outline=alpha)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=80))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(img, dark, mask)


def build_thumbnail(
    hook_line: str,
    accent_word: str = None,
    stat: str = None,
    stat_label: str = None,
    output_path: str = "/tmp/thumbnail.png",
):
    """Build a viral YT-style thumbnail.
    hook_line: punchy statement (e.g. "AI SDR IS DEAD")
    accent_word: word to color-accent (coral)
    stat: optional big number to show (e.g. "+58%")
    stat_label: label under the stat (e.g. "PIPELINE")
    """
    # Dramatic gradient background
    img = _gradient_bg((W, H), (30, 15, 70), DARK)

    # Subtle texture: diagonal light streaks
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(0, W + H, 60):
        od.line([(i, 0), (i - H, H)], fill=(78, 51, 241, 20), width=30)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    # Vignette for drama
    img = _vignette(img)
    draw = ImageDraw.Draw(img)

    # Photo: enlarged, right-center. Add soft glow behind.
    if PHOTO_PATH.exists():
        photo = Image.open(PHOTO_PATH).convert("RGBA")
        target_h = int(H * 1.05)
        ratio = target_h / photo.height
        new_w = int(photo.width * ratio)
        photo = photo.resize((new_w, target_h), Image.LANCZOS)
        # Soft glow: blur + colored tint behind photo
        glow = Image.new("RGBA", (new_w + 80, target_h + 80), (78, 51, 241, 80))
        glow = glow.filter(ImageFilter.GaussianBlur(40))
        glow_pos = (W - new_w - 20, H - target_h + 15)
        img.paste(glow, (glow_pos[0] - 40, glow_pos[1] - 40), glow)
        img.paste(photo, glow_pos, photo if photo.mode == "RGBA" else None)

    draw = ImageDraw.Draw(img)  # re-bind after pasting

    # Hook text — big bold with thick black stroke
    max_text_w = int(W * 0.55)
    for size in [160, 140, 120, 100, 88]:
        f = _font(size, "Bold")
        lines = _wrap(draw, hook_line.upper(), f, max_text_w)
        if len(lines) <= 3:
            break
    line_h = size + 16
    total_h = len(lines) * line_h
    start_y = max(80, (H - total_h) // 2 - 60)

    for i, line in enumerate(lines):
        y = start_y + i * line_h
        # If the accent_word appears, split and color
        if accent_word and accent_word.upper() in line.upper():
            before, _, after = line.upper().partition(accent_word.upper())
            x = 60
            if before:
                _text_stroke(draw, (x, y), before, f, LIGHT, DARKER, stroke_w=6)
                bb = draw.textbbox((0, 0), before, font=f)
                x += bb[2] - bb[0]
            _text_stroke(draw, (x, y), accent_word.upper(), f, SECONDARY, DARKER, stroke_w=6)
            bb = draw.textbbox((0, 0), accent_word.upper(), font=f)
            x += bb[2] - bb[0]
            if after:
                _text_stroke(draw, (x, y), after, f, LIGHT, DARKER, stroke_w=6)
        else:
            _text_stroke(draw, (60, y), line, f, LIGHT, DARKER, stroke_w=6)

    # Optional stat card bottom-left (like "+165K followers")
    if stat:
        stat_f = _font(80, "Bold")
        lbl_f = _font(30, "Bold")
        pad = 24
        sx, sy = 60, H - 180
        # Draw coral card
        bb_stat = draw.textbbox((0, 0), stat, font=stat_f)
        bb_lbl = draw.textbbox((0, 0), stat_label or "", font=lbl_f)
        card_w = max(bb_stat[2], bb_lbl[2]) + 2 * pad
        card_h = (bb_stat[3] - bb_stat[1]) + (bb_lbl[3] - bb_lbl[1]) + 2 * pad + 10
        draw.rounded_rectangle([(sx, sy), (sx + card_w, sy + card_h)], radius=14, fill=SECONDARY)
        _text_stroke(draw, (sx + pad, sy + pad - bb_stat[1]), stat, stat_f, LIGHT, DARKER, stroke_w=4)
        if stat_label:
            draw.text((sx + pad, sy + pad + (bb_stat[3] - bb_stat[1]) + 10 - bb_lbl[1]), stat_label.upper(), font=lbl_f, fill=LIGHT)

    # Curved-ish arrow from text toward photo for YT vibe
    _draw_arrow(draw, start=(600, 200), end=(820, 330), color=YELLOW, width=10, arrow_size=32)

    # Top-right violet L-bracket (brand accent)
    bw = 6
    L = 60
    draw.rectangle([(W - 40 - L, 40), (W - 40, 40 + bw)], fill=PRIMARY)
    draw.rectangle([(W - 40 - bw, 40), (W - 40, 40 + L)], fill=PRIMARY)

    # Bottom coral bar
    draw.rectangle([(0, H - 10), (W, H)], fill=SECONDARY)

    # Small KHADIJA handle bottom-right
    handle_f = _font(20, "Bold")
    draw.text((W - 240, H - 45), "KHADIJA KAMOUN", font=handle_f, fill=LIGHT)

    img.save(output_path, "PNG")
    return output_path


if __name__ == "__main__":
    build_thumbnail(
        "AI SDR is DEAD",
        accent_word="DEAD",
        stat="+58%",
        stat_label="Pipeline",
        output_path="/tmp/test_thumb.png",
    )
    print("OK /tmp/test_thumb.png")

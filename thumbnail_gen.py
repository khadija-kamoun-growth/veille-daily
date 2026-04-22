"""Thumbnail PNG generator — viral YouTube-style, 1280x720.
Inspired by the swipe file of viral AI/LinkedIn thumbnails.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PRIMARY = (78, 51, 241)       # violet
SECONDARY = (255, 87, 90)     # coral
AUX1 = (146, 129, 253)
LIGHT = (255, 255, 255)
DARK = (14, 8, 32)
DARKER = (6, 3, 15)

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


def _draw_text_with_stroke(draw, xy, text, font, fill, stroke_fill, stroke_w=3):
    draw.text(xy, text, font=font, fill=fill, stroke_width=stroke_w, stroke_fill=stroke_fill)


def build_thumbnail(hook_line: str, accent_word: str = None, output_path: str = "/tmp/thumbnail.png"):
    """Build a viral-YT-style thumbnail.

    hook_line: short punchy statement (e.g. "SPRAY AND PRAY IS DEAD")
    accent_word: optional word to highlight in coral (if found in hook_line)
    """
    img = Image.new("RGB", (W, H), DARK)
    draw = ImageDraw.Draw(img)

    # Radial-ish gradient background (cheap version: dark center → lighter edges)
    for i in range(10):
        shade = (DARK[0] + i * 2, DARK[1] + i * 2, DARK[2] + i * 3)
        draw.rectangle([(i, i), (W - i, H - i)], outline=shade)

    # Photo on right ~ 45% width, bleeding to bottom
    if PHOTO_PATH.exists():
        photo = Image.open(PHOTO_PATH).convert("RGBA")
        target_h = int(H * 1.05)
        ratio = target_h / photo.height
        new_w = int(photo.width * ratio)
        photo = photo.resize((new_w, target_h), Image.LANCZOS)
        # Anchor bottom-right
        pos = (W - new_w + 40, H - target_h + 20)
        img.paste(photo, pos, photo if photo.mode == "RGBA" else None)

    # Left column: bold hook text
    max_text_w = int(W * 0.55)
    # Try decreasing font sizes until fits in 3-4 lines
    for size in [160, 140, 120, 100, 85]:
        f = _font(size, "Bold")
        lines = _wrap(draw, hook_line.upper(), f, max_text_w)
        if len(lines) <= 4:
            break
    line_h = size + 10
    total_h = len(lines) * line_h
    start_y = max(60, (H - total_h) // 2 - 40)

    for i, line in enumerate(lines):
        color = LIGHT
        # If accent_word in line, color just that word
        if accent_word and accent_word.upper() in line:
            # Split line around the accent word
            before, _, after = line.partition(accent_word.upper())
            x = 60
            y = start_y + i * line_h
            if before:
                _draw_text_with_stroke(draw, (x, y), before, f, LIGHT, DARKER, 4)
                bb = draw.textbbox((0, 0), before, font=f)
                x += bb[2] - bb[0]
            _draw_text_with_stroke(draw, (x, y), accent_word.upper(), f, SECONDARY, DARKER, 4)
            bb = draw.textbbox((0, 0), accent_word.upper(), font=f)
            x += bb[2] - bb[0]
            if after:
                _draw_text_with_stroke(draw, (x, y), after, f, LIGHT, DARKER, 4)
        else:
            _draw_text_with_stroke(draw, (60, start_y + i * line_h), line, f, color, DARKER, 4)

    # Top-right violet L-bracket
    bw = 5
    L = 55
    draw.rectangle([(W - 30 - L, 30), (W - 30, 30 + bw)], fill=PRIMARY)
    draw.rectangle([(W - 30 - bw, 30), (W - 30, 30 + L)], fill=PRIMARY)

    # Bottom coral bar
    draw.rectangle([(0, H - 8), (W, H)], fill=SECONDARY)

    # Small KHADIJA tag bottom-left (like a channel handle)
    tag_font = _font(22, "Bold")
    draw.text((60, H - 45), "KHADIJA KAMOUN", font=tag_font, fill=AUX1)

    img.save(output_path, "PNG")
    return output_path


if __name__ == "__main__":
    build_thumbnail("Spray and pray is DEAD", accent_word="DEAD", output_path="/tmp/test_thumb.png")
    print("OK /tmp/test_thumb.png")

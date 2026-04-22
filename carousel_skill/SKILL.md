---
name: linkedincarroussels
description: Use this skill whenever Khadija wants to create, extend, or refresh a LinkedIn PDF carousel in her signature style — signal-based growth playbooks with the Apollo.io brand palette, 1080×1350 editorial magazine layout, a solar-system cover with a big transparent PNG portrait as bait, keyword chips orbiting around the photo (never on it), and JetBrains Mono + Inter typography. Trigger on any mention of "LinkedIn carousel", "carroussel", "playbook", "swipe deck", "slide deck for LinkedIn", "PDF for LinkedIn", "new post with slides", or whenever she wants to turn a topic, framework, or lesson into her carousel format. Also trigger when she says things like "make me a new one about X", "another playbook", "same style but about Y" — she means this format.
---

# Khadija's LinkedIn Carousel Playbook Skill

This skill encodes the exact visual system, copy tone, and technical workflow behind Khadija Kamoun's Apollo.io growth playbooks. When she asks for a new carousel, the goal is to produce a print-ready PDF (15 pages at 1080×1350) that feels like a continuation of the brand, not a one-off.

## Why this skill exists

Khadija uses these carousels as inbound bait. The portrait PNG is intentionally oversized — it stops the scroll. The solar-system composition, the chip-style keyword metadata, and the editorial typography signal "systems thinker who ships", which is the personal brand she's growing. Every design decision in this skill exists because we iterated on it with her and she approved it. Don't redesign the system unless she explicitly asks you to — extend it.

## What the user cares about (from real feedback)

- **Portraits are bait, not decoration.** Big, flush to the right edge, NEVER boxed or circular. Use transparent PNGs so the person bleeds into the layout.
- **Keywords orbit the photo, they never sit on her face or body.** Position every chip outside the photo bounds.
- **No redundant branding.** Her name is in the header and footer. Do not add a "Khadija Kamoun · Head of Growth · Digigram" credential pill — she finds it cluttered.
- **No fake episode counts or "next week" promises** unless she explicitly asks. Close pages use a clean Like/Follow/Save CTA.
- **Gradient text breaks in WeasyPrint.** Use solid accent colors with a subtle highlight bar underneath instead. `-webkit-background-clip: text` renders as a solid rectangle — avoid it.
- **Apollo icon lives top-right** on every page. Use `assets/apollo-mark.png` (the yellow rounded-square star).

## The design system

### Brand colors

Use these CSS variables at the top of every stylesheet:

```css
:root {
  --primary:      #4E33F1;   /* Apollo violet — headers, accents, primary CTAs */
  --secondary:    #FF575A;   /* Coral — hook accent words, takeaways, urgency */
  --aux1:         #9281FD;   /* Soft violet — orbit rings, planets */
  --apollo:       #F4C841;   /* Apollo yellow — logo backdrop, dots on chips */
  --ink:          #16122E;   /* Deep navy-black — body text */
  --ink-soft:     #4B4770;   /* Muted text */
  --muted:        #6C6790;   /* Tagline, metadata */
  --bg:           #F6F4FF;   /* Page background — lavender-tinted white */
  --border-soft:  #E9E5FA;   /* Hairline borders on cards and chips */
}
```

Dark pages (close page, section dividers) flip to `background: var(--primary)` with white text and semi-transparent borders.

### Typography

Two families, no more:

- **JetBrains Mono** (weight 800, letter-spacing -2.4px) — all headlines, stat values, chip labels, page-number monospacing. This is the "systems thinker" voice.
- **Inter** (weight 400–700) — body copy, taglines, subheads, takeaway paragraphs.

Never use any other typeface. Load both from Google Fonts:

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700;800;900&display=swap">
```

**Headline sizing** — 72px on the cover, 78px on the close page. Line-height 0.96–0.98. Letter-spacing -2.4px. Accent words get solid color + subtle highlight bar (see template CSS) — never CSS gradients on text.

### Page format

- Page size: **1080 × 1350px** (LinkedIn carousel spec at 4:5)
- 15 pages total: cover, table of contents, 11 content pages, 1 closing CTA, 1 closing signature. Adjust count to topic, but keep ≤ 20 slides.
- Outer padding: **80px top/bottom, 84px left/right**
- Header on every page: avatar + name + verified checkmark + Apollo yellow star mark (top-right)
- Footer on every page: small photo pill ("Khadija / kamoun") + swipe indicator + page number

### The solar-system cover

The cover is the skill's signature move. It has:

1. A **transparent PNG portrait** positioned absolutely at `right: 0; bottom: 0` inside a 420px-wide container. Use `assets/cover-raw.png` style (glasses, pointing gesture — visually directing attention into the layout).
2. **Three concentric dashed orbit rings** behind the portrait, in violet and coral with 0.25–0.35 opacity.
3. **Planet dots** (4 small filled circles) and **spark lines** (2 short diagonal strokes) floating on the rings.
4. **Keyword chips** (7–9 of them) placed around the image — in the top strip above the photo, and in the empty space at the bottom-left below the cover-left content column. **Never over the portrait.**
5. The **hook headline** on the left in 72px JetBrains Mono, with two accent words colored (one coral, one violet) and a subtle semi-transparent bar underneath each accent.
6. Three stat cards below the tagline (`>20%`, `<5m`, `1h`-style metrics). Each card has a colored left border stripe (coral / violet / aux1).
7. A "POWERED BY Apollo.io" logo block at the lower-left of the cover-left column.

### Chip placement rules

Photo in cover-split coordinates: `x = [492, 912], y = [184, 980]`. Safe zones:

- **Above photo** (`y < 180`): chips can span the whole width
- **Left of photo** (`x < 490`): chips must sit below the cover-left text (`y > 620`)

Chips are 13px JetBrains Mono, weight 800, with a colored dot on the left. Three color variants:

- Default: white background, ink text, yellow dot
- `.c-primary`: violet border + violet text + violet dot
- `.c-secondary`: coral border + coral text + coral dot
- `.c-ink`: dark background, white text, yellow dot

Use chip labels that sound like signal/event names and feel universal: `website.visit`, `signal.detected`, `high_intent`, `ICP match`, `enrich()`, `follow.up`, `reply < 5m`, `meeting.booked`. Avoid cryptic labels nobody would relate to.

### Middle content pages

Each content page follows a consistent pattern — this is what makes the carousel feel like a system:

```
[Header]
[Part X · Section name]               (top label, small mono type)

[Headline]                             (60–78px JetBrains Mono, 2–3 lines max, one accent word)

[Subhead]                              (17–20px Inter, 1 sentence)

[Visual module]                        (mock browser window, data cards, flow diagram, etc.)

[Takeaway box]                         (coral left border, "TAKEAWAY:" label + 1–2 sentence insight)

[Footer]
```

Visual modules worth reusing:

- **Fake browser frame** — three colored dots + URL pill + inner content. Great for showing what a dashboard or form looks like.
- **Stat cards row** — 2–4 cards with `label` (muted small caps) and `value` (big mono). One or two cards get a colored left-border stripe.
- **Numbered step flow** — circles with numbers, short titles underneath, chevron connectors.
- **Signal ticker** — monospace list of events with timestamps and a green/violet dot.

### The close page

Dark violet background (`var(--primary)`) with:

- Small tagline pill at top in coral-tinted rgba (e.g. "GROW FASTER · CLOSE SMARTER"). **Never** include episode numbers or references to "next week" unless Khadija says she's actually shipping a series.
- 78px headline in JetBrains Mono with two accent words in warm-coral gradient-adjacent colors.
- A 1–2 sentence subhook explaining what she shares and why they should stick around.
- Three clean CTAs as rounded pill buttons: `♡ Like if this was useful`, `+ Follow for more growth systems`, `◉ Save so you can come back to it`.
- A "BUILT IN" line with the Apollo white wordmark at the bottom.
- Same orbit/planet/spark treatment as the cover, with her close-page portrait (red beanie style) flush to the right edge.
- **No signature line like "Khadija Kamoun · Head of Growth · Digigram"** — her name already appears in the header and footer.

## The copy voice

Khadija writes like a founder-operator who has lived through the pain she's describing. The tone is:

- **Direct and pragmatic**, never hype-y. "Stop sending more. Start filtering better." not "Unlock 10x pipeline with this revolutionary framework!"
- **Specific**, with real numbers and timeboxes. `>20% signal → meeting`, `<5m inbound response`, `1h weekly prospecting`.
- **First-person, plural-aware**. "The exact stack I use to close faster" / "If this helped".
- **Apollo-native**. She builds in Apollo.io — mention it where relevant, don't over-mention.

Hook patterns that have worked:

- Contrast setup: "Stop X. Start Y." ("Stop sending more. Start filtering better.")
- Category reframe: "Turn anonymous traffic into real pipeline."
- Cost of inaction: "Most teams still play the forms game."
- Numbered promise: "The 5-signal stack that replaces cold outbound."

Pick the pattern that fits the topic — don't reuse the same one every carousel.

## The technical workflow

The carousel is an HTML file rendered to PDF by WeasyPrint. That's it — no Figma, no PowerPoint. Use the template at `assets/playbook-template.html` as the starting point.

### Standard build steps

1. Read `assets/playbook-template.html` and understand its structure.
2. Copy the template to a working location, keep the `assets/` folder reachable from the HTML via relative paths (e.g. `assets/apollo-mark.png`, `assets/cover-raw.png`).
3. Rewrite only the content — headline, tagline, stats, content pages, close copy. Do not restructure the CSS unless she asks.
4. If she provides new portraits, drop them into `assets/` and reference them by filename.
5. Render to PDF with WeasyPrint from the **same directory as the HTML file**, otherwise relative asset paths fail:

   ```python
   from weasyprint import HTML
   HTML("playbook.html").write_pdf("output.pdf")
   ```

6. Preview a few pages with pdf2image to catch overflow, clipped chips, or broken text before declaring done:

   ```python
   from pdf2image import convert_from_path
   imgs = convert_from_path("output.pdf", dpi=160)
   imgs[0].save("preview-cover.png")
   imgs[-1].save("preview-close.png")
   ```

7. Save the final PDF to the user's Desktop / outputs folder and share a computer:// link.

### Common pitfalls to avoid

- **CSS gradient text (`-webkit-background-clip: text`) renders as a solid colored rectangle in WeasyPrint.** Use solid hex colors + a faint semi-transparent highlight bar via `::after` instead.
- **`overflow: hidden` on `.cover-split` will clip keyword chips** that bleed past the container. Either set `overflow: visible` or keep chips inside the container bounds.
- **Running WeasyPrint from the wrong working directory** causes `FileNotFoundError` on images. Always `cd` to the HTML's folder first.
- **Scaled portrait heights are not the source-file heights.** A 487×924 source scaled to 420 wide is ~797 tall. Use `height * (target_width / source_width)` when positioning chips relative to the photo.
- **Photos should be transparent PNGs.** If the user gives a JPG, either ask for a transparent version or remove the background before using it.
- **Do not add placeholder text like "Lorem ipsum".** If she hasn't given content for a section, ask her what should go there rather than guessing.

## What to ask before starting

Before drafting a new carousel, clarify:

1. **Topic.** What's the carousel about? (e.g., "enrichment", "inbound routing", "the first 90 days running growth at a startup")
2. **The hook.** Does she have a headline in mind, or does she want suggestions?
3. **Length.** 10 slides, 15, or something else?
4. **Portraits.** Is she reusing the existing ones (`cover-raw.png`, `close-raw.png`) or providing new shots?
5. **Stats.** What real numbers does she want to show? Invented stats break the credibility play.

Use the AskUserQuestion tool to get these upfront — don't guess and waste a whole render cycle.

## File map

```
linkedincarroussels/
├── SKILL.md                          (this file)
├── assets/
│   ├── playbook-template.html        (full 15-page working template)
│   ├── apollo-mark.png               (yellow star logo — top-right of every page)
│   ├── apollo-logo.png               (Apollo wordmark — "POWERED BY" on cover)
│   └── apollo-logo-white.png         (white variant — "BUILT IN" on close page)
├── scripts/
│   └── build_pdf.py                  (one-command renderer with preview)
└── references/
    ├── copy-voice.md                 (extended tone guide with more hook examples)
    └── content-page-patterns.md      (recipes for each middle-page layout)
```

Read `references/copy-voice.md` when drafting new hook headlines or takeaway copy. Read `references/content-page-patterns.md` when deciding which visual module to use for a new middle page.

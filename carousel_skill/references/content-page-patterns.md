# Content page patterns — middle slides

Every middle slide in a Linkedin Caroussels playbook uses one of these six visual modules. Picking the right one per page is what makes the carousel feel like a system instead of a deck of random slides. Each pattern shows the layout, when to use it, and the HTML/CSS conventions.

## 1. The fake browser frame

**Use when:** showing what a dashboard, form, or website looks like. Great for "before vs after" comparisons.

Structure: a rounded container with three colored dots in the top-left (red / yellow / green), a URL pill in the middle, and the "page content" below.

```html
<div class="mockframe">
  <div class="mockbar">
    <span class="dot red"></span>
    <span class="dot yellow"></span>
    <span class="dot green"></span>
    <span class="url">apollo.io/website-visitors</span>
  </div>
  <div class="mockbody">
    <!-- stat cards, signal rows, etc. -->
  </div>
</div>
```

Tips:
- Dot colors: `#FF5F57` red, `#FEBC2E` yellow, `#28C840` green.
- Inner body padding around 28px.
- Drop shadow: `0 24px 60px rgba(22, 18, 46, 0.1)`.

## 2. Stat cards row

**Use when:** introducing the "size of the problem" or proving results with numbers.

Two to four side-by-side cards. Each has a small all-caps label and a big mono number. One or two cards get a colored left border stripe.

```html
<div class="stat-row">
  <div class="stat-card">
    <div class="stat-label">FORM CONVERSION</div>
    <div class="stat-value">2.3%</div>
  </div>
  <div class="stat-card accent-coral">
    <div class="stat-label">ANONYMOUS TRAFFIC</div>
    <div class="stat-value">95%+</div>
  </div>
  ...
</div>
```

Tips:
- Values in JetBrains Mono 800 at 40–48px.
- Labels in Inter 700 at 11px, tracking 1.5px, uppercase, `var(--muted)`.
- Accent border stripe: `border-left: 3px solid var(--secondary);`

## 3. Numbered step flow

**Use when:** showing a sequence — a 3-step framework, a funnel, a decision tree.

Horizontal or vertical list of numbered circles, each with a title underneath and a chevron connector between them.

```html
<div class="flow">
  <div class="step">
    <div class="step-num">1</div>
    <div class="step-title">Detect</div>
    <div class="step-sub">Who's on your site?</div>
  </div>
  <div class="connector">→</div>
  ...
</div>
```

Tips:
- Step circles are 48px, violet background, white mono number.
- Step title: Inter 700, 16px.
- Step sub: Inter 400, 13px, `var(--muted)`.

## 4. Signal ticker

**Use when:** showing a live feed of events — signals detected, emails sent, meetings booked.

Monospace vertical list. Each row: status dot, event name, timestamp, optional metadata chip.

```html
<div class="ticker">
  <div class="signal">
    <span class="dot green"></span>
    <span class="event">acme.com visited /pricing 3x</span>
    <span class="ts">2m ago</span>
  </div>
  ...
</div>
```

Tips:
- Alternating row backgrounds at `rgba(78, 51, 241, 0.03)`.
- Use `var(--secondary)` dots for "hot" signals, `var(--primary)` for routing, green (#28C840) for wins.
- Timestamps right-aligned in JetBrains Mono 12px, `var(--muted)`.

## 5. Side-by-side comparison

**Use when:** contrasting "old way vs new way" or "without vs with Apollo".

Two columns, equal width. Left column usually neutral/muted, right column accent-colored to signal "this is the right answer".

```html
<div class="compare">
  <div class="col col-before">
    <div class="col-label">WITHOUT SIGNALS</div>
    <ul>...</ul>
  </div>
  <div class="col col-after">
    <div class="col-label">WITH SIGNALS</div>
    <ul>...</ul>
  </div>
</div>
```

Tips:
- Left column: `background: #FFFFFF;` border `var(--border-soft)`.
- Right column: `background: rgba(78, 51, 241, 0.06);` border `rgba(78, 51, 241, 0.25)`.
- Use a red ✗ and violet ✓ in front of each list item.

## 6. Quote / pullout

**Use when:** introducing an insight or principle that deserves its own slide. Sparingly — once per carousel max.

Large quote mark, oversized quote text, small attribution.

```html
<div class="pullout">
  <div class="q-mark">"</div>
  <blockquote>The best prospecting doesn't feel like prospecting. It feels like showing up at the right moment.</blockquote>
  <div class="q-attrib">— something she or someone she trusts actually said</div>
</div>
```

Tips:
- Quote mark in violet, 180px JetBrains Mono, opacity 0.25.
- Quote in Inter 500, 36px, line-height 1.25.
- No fake attributions. Either her own line or leave out the attribution.

## The takeaway box (goes on every content page)

All six patterns are followed by the takeaway box at the bottom. It's the screenshot-worthy insight.

```html
<div class="takeaway">
  <span class="takeaway-label">TAKEAWAY:</span>
  <span class="takeaway-body">One or two sentences of distilled insight.</span>
</div>
```

CSS:

```css
.takeaway {
  background: rgba(255, 87, 90, 0.08);
  border-left: 4px solid var(--secondary);
  padding: 20px 26px;
  border-radius: 0 12px 12px 0;
  font-family: 'Inter', sans-serif;
  font-size: 17px;
  line-height: 1.45;
}
.takeaway-label {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  color: var(--secondary);
  margin-right: 10px;
}
```

## Which pattern for which type of slide?

- **"Here's the problem"** → Stat cards row OR fake browser frame
- **"Here's the shift in thinking"** → Side-by-side comparison OR pullout quote
- **"Here's how it works"** → Numbered step flow
- **"Here's what the live output looks like"** → Signal ticker OR fake browser frame
- **"Here's the result"** → Stat cards row with accent borders

Don't use the same pattern twice in a row. Variety is what keeps the reader swiping.

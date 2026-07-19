---
name: TwinForge
description: Edge-first Physical AI pipeline — capture, reconstruct, and deploy a digital twin, styled as a survey instrument reading its own depth data.
colors:
  vellum: "#eef0ea"
  vellum-deep: "#e6e9e1"
  graphite: "#12151a"
  rule: "#cbd1c7"
  far-indigo: "#22307e"
  mid-teal: "#14b09a"
  near-hot: "#ff5b2e"
  near-ink: "#a82c0c"
  mint-ink: "#06584e"
  coral: "#c0331c"
  muted: "#4a524d"
  body-ink: "#2c3238"
typography:
  display:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(2.4rem, 4.6vw, 3.75rem)"
    fontWeight: 760
    lineHeight: 0.98
    letterSpacing: "-0.03em"
  title:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(2rem, 3.8vw, 3rem)"
    fontWeight: 700
    lineHeight: 1.04
    letterSpacing: "-0.025em"
  sub:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(1.5rem, 2.6vw, 2.1rem)"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    letterSpacing: "0.22em"
  mono:
    fontFamily: "JetBrains Mono, ui-monospace, SF Mono, Menlo, monospace"
    fontSize: "0.875rem"
    fontWeight: 400
rounded:
  none: "0px"
  pill: "50%"
spacing:
  gutter: "clamp(1.25rem, 4vw, 3.5rem)"
  band-gap: "clamp(4.5rem, 11vw, 9rem)"
components:
  button-primary:
    backgroundColor: "{colors.graphite}"
    textColor: "{colors.vellum}"
    rounded: "{rounded.none}"
    padding: "0.75rem 1.5rem"
  button-primary-hover:
    backgroundColor: "{colors.far-indigo}"
    textColor: "{colors.vellum}"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.graphite}"
    rounded: "{rounded.none}"
    padding: "0.75rem 1.5rem"
  button-ghost-hover:
    backgroundColor: "{colors.graphite}"
    textColor: "{colors.vellum}"
---

# Design System: TwinForge

## 1. Overview

**Creative North Star: "The Depth Sheet"**

TwinForge is styled as a survey sheet — the printout an instrument produces, not a
marketing page describing one. The palette is lifted directly from a depth sensor's own
colormap: far is indigo, mid is teal, near is hot orange. Colour is spent only where the
system is actively sensing or computing right now, so it reads as telemetry rather than
decoration. Registration marks in the corners, a masthead with live metadata, hairline
rules, and monospace figures for anything the machine measured — the page presents itself
as an output of the pipeline, not a pitch for it.

This system explicitly rejects generic SaaS/startup grammar: no gradient-mesh hero, no
cream/pastel palette, no bouncy or elastic motion, no rounded-everything cards, no
hero-metric-with-gradient-text blocks, no tiny uppercase eyebrow above every section, no
identical icon+heading+text card grids. If it could be any startup's homepage with the
copy swapped, it has failed the brief.

**Key Characteristics:**
- A measured colormap, not a brand palette — colour = sensor state, not taste
- Flat, hairline-ruled surfaces; a survey sheet has no elevation
- One type family (Archivo) doing all the work across its width axis, plus JetBrains Mono for anything measured
- Motion reads as instrumentation calibrating, not a marketing entrance

## 2. Colors

A depth-sensor colormap pressed into service as the entire palette — three hues (indigo,
teal, hot orange) plus a warm-paper neutral ramp, nothing invented beyond what the sensor
itself outputs.

### Primary
- **Near Hot** (`#ff5b2e`, ink pair `#a82c0c`): the sensor's "actively looking" colour.
  Reserved for the scan plane, the robot marker, the live point cloud, and the one accent
  in `<em>` emphasis in the hero headline. The raw hex is graphic-only (2.69:1 on vellum);
  small text always takes `near-ink` instead.

### Secondary
- **Mid Teal** (`#14b09a`, ink pair `#06584e`): mid-range depth, used for the "done"/"pass"
  state (stage markers, sim-gate pass legend, NPU unit labels).
- **Far Indigo** (`#22307e`): far-range depth, used for structural data — the plan-view
  substrate, focus rings, the primary button's hover state, `cyan`-role hint text.

### Tertiary
- **Coral** (`#c0331c`): reserved for failure states only (`.gate.fail`, `.error`,
  `.jobs li.failed`) — distinct from Near Hot so "actively sensing" and "failed" are never
  visually confused.

### Neutral
- **Vellum** (`#eef0ea`): page background — a paper/parchment tone, but treated as the
  sheet's substrate, not a "warm SaaS cream." Never used decoratively beyond that reading.
- **Vellum Deep** (`#e6e9e1`): panel/card background one step down from the page.
- **Graphite** (`#12151a`): primary text and the solid-button fill/border.
- **Rule** (`#cbd1c7`): all hairline borders, meter ticks, registration-mark lines.
- **Muted** (`#4a524d`): secondary text — labels, captions, marginalia.
- **Body Ink** (`#2c3238`): body copy, one step darker than Muted for the 4.5:1 floor.

### Named Rules
**The Measured Colour Rule.** Colour is spent only where the system is sensing or working
right now — the hot end of the ramp marks an active scan plane, a moving robot marker, a
live point cloud. It never decorates a static element. If a colour isn't reporting a
sensor or pipeline state, it doesn't belong.

**The Ink-Pair Rule.** `--near` and `--mid` are graphic colours (3:1 floor, large-size
only). Any time either hue carries text — labels, legends, small UI — swap to its `-ink`
pair (`--near-ink` / `--mint-ink`), which holds the same hue dark enough to clear 4.5:1.
Never set small text directly in the raw ramp colour.

## 3. Typography

**Display Font:** Archivo (variable, with Helvetica Neue / Arial fallback)
**Body Font:** Archivo (same family, regular weight/width)
**Label/Mono Font:** JetBrains Mono (with ui-monospace / SF Mono / Menlo fallback)

**Character:** One variable grotesque doing both jobs by riding its width axis —
expanded and heavy for display, condensed and semibold for instrument labels, regular
width for body — set against a monospace for anything the machine actually measured. Two
families contrasting on proportion, not the serif/sans axis: a serif "for warmth" here
would be costume on an instrument.

### Hierarchy
- **Display** (wght 760, wdth 118, `clamp(2.4rem, 4.6vw, 3.75rem)`, line-height 0.98,
  letter-spacing -0.03em): the hero headline only, one per page.
- **Title** (wght 700, wdth 115, `clamp(2rem, 3.8vw, 3rem)`, line-height 1.04): section
  headers within a band.
- **Sub** (wght 700, wdth 112, `clamp(1.5rem, 2.6vw, 2.1rem)`, line-height 1): in-canvas
  stage names (`recon__name`), console page title.
- **Body** (wght 400, 1.125rem landing / 1rem console, line-height 1.6): running prose,
  capped at 60ch (`prose`) / 52ch (`lede`).
- **Label** (wght 600, wdth 62, 0.875rem, letter-spacing 0.22–0.3em, uppercase): nav
  items, eyebrows, meter legends — always tracked wide and uppercase, never used at body
  size.
- **Mono** (JetBrains Mono, 0.875rem–1rem): endpoint signatures, readouts, code blocks,
  anything the pipeline itself returned as a value.

### Named Rules
**The Instrument, Not Costume Rule.** No second display face, no serif anywhere. Archivo's
width axis is the only lever pulled for hierarchy; reaching for a new font family to add
"warmth" is the reflex this system exists to refuse.

## 4. Elevation

Flat by doctrine — a survey sheet has no drop shadows. Depth and hierarchy are conveyed
entirely through hairline rules (`--hair: 1.5px`, chosen because 1px disappears on a
projector), background-tint steps (`vellum` → `vellum-deep`), and colour (the far/mid/near
ramp itself reads as depth). The one exception is the console's `.error` block, which uses
a 2px solid left rule plus a faint tint — a flagged-state treatment, not decorative
elevation.

### Named Rules
**The Flat-Sheet Rule.** No `box-shadow` anywhere in the system. If something needs to
read as "above" the page, give it a hairline border and a `vellum-deep` fill, not a
shadow.

## 5. Components

### Buttons
- **Shape:** square corners, no radius (`rounded.none`) — this system does not round.
- **Primary (`.btn--solid`):** graphite fill, vellum text, `0.75rem 1.5rem` padding,
  uppercase label type at 0.12em tracking. Hover shifts fill to Far Indigo
  (`background 140ms ease`), never a shadow or lift.
- **Ghost (`.btn`):** transparent fill, graphite hairline border and text. Hover inverts to
  a solid graphite fill — same transition timing as primary, so both buttons feel like one
  state machine.
- **Console button (`.stage button`):** same ghost logic at console density — hairline
  border, transparent fill, inverts on hover, disabled state drops to `--muted` text on a
  `--line` border with `cursor: not-allowed`.

### Cards / Containers
- **Corner style:** none — every panel, edge-tier, and bench-card is a flat rectangle.
- **Background:** `panel` (`vellum-deep`) for console panels; plain `vellum` for
  edge-tier cells, separated only by 1px gaps against a `rule`-coloured backdrop
  (`edge-tiers`'s grid-gap trick — the "border" is negative space, not a drawn line).
- **Shadow strategy:** none (see Elevation).
- **Border:** hairline (`1.5px solid var(--rule)`) on every bounded surface.
- **Internal padding:** `1.25rem` (panel), `1.4rem 1.25rem` (edge-tier), `0.75rem`
  (bench-card).

### Inputs / Fields (console)
- **Style:** hairline border, `vellum` fill, no radius, `0.5rem 0.65rem` padding, label
  set uppercase/tracked above the field.
- **Focus:** browser-default `:focus-visible` outline overridden globally to
  `2px solid var(--far)` with `3px` offset — indigo, not the near-hot accent, since focus
  is a structural state, not a sensing one.
- **Error:** a 2px coral left rule plus `rgba(192,51,28,0.06)` background tint
  (`.error`), never a red border-glow.

### Navigation
- **Masthead nav:** uppercase, wide-tracked (0.22em) label type, muted colour at rest,
  graphite on hover, and a `near-ink` bottom hairline for the active route
  (`.masthead__nav a.is-here`) — the only place the hot accent marks UI state rather than
  sensor state.

### Signature Component: The Sim-Gate Meter
A tick-ruled horizontal meter (`simgate__meter`) — a `repeating-linear-gradient` drawing
10%-interval ticks, filled to the pass threshold with a translucent indigo bar and a solid
2px indigo edge. Reads as an oscilloscope trace, not a progress bar: no rounded ends, no
gradient fill, no percentage-as-hero-number.

## 6. Do's and Don'ts

### Do:
- **Do** spend the hot end of the ramp (`--near` / `--near-ink`) only on something actually
  sensing or computing right now — the Measured Colour Rule.
- **Do** swap to the `-ink` pair (`--near-ink`, `--mint-ink`) any time a ramp colour sets
  text smaller than large-scale — the Ink-Pair Rule.
- **Do** keep every bordered surface square-cornered and hairline-ruled, flat, no shadow.
- **Do** use Archivo's width/weight axis for hierarchy instead of a second typeface.
- **Do** let `prefers-reduced-motion: reduce` fully no-op scroll-driven and looping
  animation (see `useReveal.js`, `.recon` height collapse, `.stage.busy` pulse) — never a
  partial disable.

### Don't:
- **Don't** use a gradient-mesh hero, a cream/pastel palette dressed up as "warm," or any
  `background-clip: text` gradient headline — this brand's warmth comes from mechanism
  (endpoint signatures, thresholds), not colour softness.
- **Don't** add rounded corners, drop shadows, or glassmorphism anywhere — the Flat-Sheet
  Rule is absolute.
- **Don't** add a tiny uppercase tracked eyebrow above every section or numbered
  `01 / 02 / 03` markers as default scaffolding — the pipeline's own 8-step numbering
  (`STEPS` in `Landing.jsx`) is the one deliberate numbered sequence on the page; don't
  echo the pattern anywhere else.
- **Don't** reach for a serif or a second display family "for warmth" — the Instrument, Not
  Costume Rule.
- **Don't** use bouncy, elastic, or overshoot easing on any transition — motion should read
  as a sensor calibrating or locking on, which means exponential ease-out, never a spring.
- **Don't** build an identical icon+heading+text card grid — every repeating list in this
  system (steps, edge-tiers, jobs) is a data table wearing minimal styling, not a card
  grid.

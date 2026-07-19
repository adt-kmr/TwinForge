---
name: DragVerse
description: A survey sheet for an edge-first Physical AI pipeline — flat, hairline-ruled, and coloured by a depth sensor's own ramp.
colors:
  vellum: "#eef0ea"
  vellum-deep: "#e6e9e1"
  graphite: "#12151a"
  body-ink: "#2c3238"
  muted-ink: "#4a524d"
  rule: "#cbd1c7"
  blueprint-indigo: "#22307e"
  signal-orange: "#ff5b2e"
  signal-orange-ink: "#a82c0c"
  survey-teal: "#14b09a"
  survey-teal-ink: "#06584e"
  alert-red: "#c0331c"
typography:
  display:
    fontFamily: "Archivo, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "clamp(2.4rem, 4.6vw, 3.75rem)"
    fontWeight: 760
    lineHeight: 0.98
    letterSpacing: "-0.03em"
    fontVariation: "'wdth' 118, 'wght' 760"
  headline:
    fontFamily: "Archivo, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "clamp(2rem, 3.8vw, 3rem)"
    fontWeight: 700
    lineHeight: 1.04
    letterSpacing: "-0.025em"
    fontVariation: "'wdth' 115, 'wght' 700"
  title:
    fontFamily: "Archivo, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "clamp(1.5rem, 2.6vw, 2.1rem)"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.02em"
    fontVariation: "'wdth' 112, 'wght' 700"
  body:
    fontFamily: "Archivo, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
  label:
    fontFamily: "Archivo, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.3em"
    fontVariation: "'wdth' 62, 'wght' 600"
  data:
    fontFamily: "'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
    fontFeature: "tabular-nums"
rounded:
  square: "0"
  pill: "50%"
spacing:
  hairline: "1.5px"
  control: "0.5rem 1.1rem"
  panel: "1.25rem"
  gutter: "clamp(1.25rem, 4vw, 3.5rem)"
  band: "clamp(4.5rem, 11vw, 9rem)"
components:
  button-primary:
    backgroundColor: "{colors.graphite}"
    textColor: "{colors.vellum}"
    typography: "{typography.label}"
    rounded: "{rounded.square}"
    padding: "0.75rem 1.5rem"
  button-primary-hover:
    backgroundColor: "{colors.blueprint-indigo}"
    textColor: "{colors.vellum}"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.graphite}"
    typography: "{typography.label}"
    rounded: "{rounded.square}"
    padding: "0.5rem 1.1rem"
  button-ghost-hover:
    backgroundColor: "{colors.graphite}"
    textColor: "{colors.vellum}"
  button-ghost-disabled:
    backgroundColor: "transparent"
    textColor: "{colors.muted-ink}"
  input-field:
    backgroundColor: "{colors.vellum}"
    textColor: "{colors.graphite}"
    typography: "{typography.data}"
    rounded: "{rounded.square}"
    padding: "0.5rem 0.65rem"
    width: "100%"
  panel-surface:
    backgroundColor: "{colors.vellum-deep}"
    textColor: "{colors.body-ink}"
    rounded: "{rounded.square}"
    padding: "1.25rem"
  nav-link:
    backgroundColor: "transparent"
    textColor: "{colors.muted-ink}"
    typography: "{typography.label}"
    padding: "0 0 0.2rem 0"
  nav-link-active:
    backgroundColor: "transparent"
    textColor: "{colors.graphite}"
  stage-marker:
    backgroundColor: "{colors.vellum}"
    textColor: "{colors.muted-ink}"
    typography: "{typography.data}"
    rounded: "{rounded.pill}"
    size: "2.5rem"
  code-block:
    backgroundColor: "{colors.graphite}"
    textColor: "#d8ded6"
    typography: "{typography.data}"
    rounded: "{rounded.square}"
    padding: "1.4rem 1.5rem"
---

# Design System: DragVerse

## 1. Overview

**Creative North Star: "The Survey Sheet"**

Everything on screen is one drawing, trimmed to register. The page is a large-format
survey sheet: corner registration marks, a marginalia column carrying field annotations in
monospace, sheet numbering in the masthead (`SHEET 01 / 02`), and hairline rules dividing
the work. Nothing floats above the sheet, because a drawing has no drop shadow. The
landing route and the operator console are two sheets of the same document, sharing a
masthead and a token set, so moving between them never feels like a handoff to another
team.

The colour comes from the product itself rather than from a mood board. A depth sensor
returns a ramp — near is hot, far is cool — and that ramp is the brand. Signal Orange
appears only where the system is sensing or working *right now*; Survey Teal marks what has
been labelled; Blueprint Indigo carries structure and finished artifacts. Colour is state,
never decoration. When a value has not been measured, the interface says so in words rather
than showing a zero.

This system explicitly rejects the **dark neon robotics site** — near-black with acid green
or cyan, glowing grids, sci-fi HUD chrome — which is the reflex default for anything
robot-adjacent and reads as costume rather than instrument. It equally rejects the
**generic AI-SaaS landing** (gradient hero metric, three identical feature cards, a tracked
eyebrow above every section) and, above all, **fabricated precision**: invented benchmarks
or decorative metrics that no code produced.

**Key Characteristics:**
- Absolutely flat. Zero `box-shadow` declarations in the entire system.
- Square by default. Zero `border-radius` except two deliberate circles.
- Hairlines at 1.5px, never 1px — the viewing context is a projector in a bright room.
- One variable typeface worked at both ends of its width axis, plus one monospace.
- Nothing below 14px anywhere.
- Colour encodes pipeline state; it is never applied for visual interest.

## 2. Colors

A cool drafting sheet carrying a sensor's own depth ramp: hot at the near end, indigo at
the far end, with a single teal in the middle for what has been identified.

### Primary
- **Blueprint Indigo** (`#22307e`): Structure and settled results. Twin wireframes, the
  navmesh path, returned identifiers and field values in the console, the second line of
  the hero headline, solid-button hover. The far end of the depth ramp — what the system
  has finished thinking about.
- **Signal Orange** (`#ff5b2e`): **Graphics only.** The scan plane sweeping the room, the
  robot marker, the hot end of the point cloud. Reserved exclusively for "sensing or moving
  right now."
- **Signal Orange Ink** (`#a82c0c`): The text-safe counterpart. Section kickers, stage
  step numbers, the busy stage marker, running job status, warnings. Same hue, 6.03:1 on
  vellum.

### Secondary
- **Survey Teal** (`#14b09a`): **Graphics only.** Labelled clusters in the point cloud and
  plan-view object fills — the mid-depth band.
- **Survey Teal Ink** (`#06584e`): The text-safe counterpart, at 7.28:1. "Orchestrator
  online", completed jobs, passing gates, NPU-resident workloads.

### Tertiary
- **Alert Red** (`#c0331c`): Failure only. Refused stages, compile errors, failed jobs.
  Never used for emphasis.

### Neutral
- **Cool Drafting Vellum** (`#eef0ea`): The sheet. Page background everywhere, both routes.
  A cool grey-green, deliberately *not* a warm cream.
- **Deep Vellum** (`#e6e9e1`): The only surface tone. Panels and containers sit on this;
  it is the entire elevation system.
- **Graphite** (`#12151a`): Headlines, primary text, solid button fills, the code block
  ground. 15.9:1 on vellum.
- **Body Ink** (`#2c3238`): Running prose. Softer than graphite without being grey.
- **Muted Ink** (`#4a524d`): Marginalia, hints, table headers, inactive nav. 7.02:1 — the
  back-row floor.
- **Rule** (`#cbd1c7`): Every hairline, every divider, every input border.

### Named Rules

**The Hot Ink Rule.** Signal Orange (`#ff5b2e`) and Survey Teal (`#14b09a`) are *graphic
colours only*. On vellum they measure 2.69:1 and 3.49:1 and fail as text. Any type,
icon-with-label, or state indicator that must be read uses the `-ink` counterpart. Audit
test: if you can read words in it, it must be an `-ink` value.

**The Measured Colour Rule.** Colour reports pipeline state and nothing else. Orange means
*happening now*. Teal means *identified*. Indigo means *settled*. Red means *refused*. A
colour applied because a section "needed some life" is prohibited.

## 3. Typography

**Display Font:** Archivo Variable (with Helvetica Neue, Arial fallback)
**Body Font:** Archivo Variable — the same family, regular width and weight
**Label/Mono Font:** JetBrains Mono (with ui-monospace, SF Mono, Menlo fallback)

**Character:** Two families contrasting on *proportion*, not on the serif/sans axis. Archivo
is worked at both ends of its width axis — expanded to `wdth 118` for display, condensed to
`wdth 62` for instrument labels — so the typeface itself encodes the near/far idea the
palette carries. JetBrains Mono sets anything the machine measured: identifiers, counts,
latencies, endpoint signatures, field annotations. There is deliberately no text serif. This
brand is an instrument, and a serif "for warmth" on a technical brief is a reflex, not a
decision.

### Hierarchy
- **Display** (`wdth 118`, `wght 760`, `clamp(2.4rem, 4.6vw, 3.75rem)`, lh 0.98, ls
  -0.03em): The hero headline. One per page, `text-wrap: balance`.
- **Headline** (`wdth 115`, `wght 700`, `clamp(2rem, 3.8vw, 3rem)`, lh 1.04, ls -0.025em):
  Section titles on the landing route and the console's own page title.
- **Title** (`wdth 112`, `wght 700`, `clamp(1.5rem, 2.6vw, 2.1rem)`, lh 1): The live stage
  name over the reconstruction canvas.
- **Body** (`wght 400`, 1.125rem/18px, lh 1.6): Running prose, capped at 60ch — which
  renders ~71 characters, because Archivo's zero is wider than its average lowercase.
  `text-wrap: pretty`.
- **Label** (`wdth 62`, `wght 600`, 0.875rem/14px, ls 0.3em, uppercase): Nav, kickers,
  field names, panel headings, buttons. The condensed extreme.
- **Data** (JetBrains Mono, 0.875rem/14px, `tabular-nums`): Every measured value, endpoint
  signature, identifier and margin annotation.

### Named Rules

**The 14px Floor Rule.** No text anywhere renders below 0.875rem/14px. Body copy is 16px or
larger. The primary viewing context is a projector in a bright room with a back row; type
that works on a laptop at arm's length is not the bar. Font sizes are always `rem`, never
`px`.

**The Two-Ramp Rule.** Sizes come from exactly two scales and are never authored ad hoc.
`--ui-*` is a fixed rem scale (14/16/18px) for the console, where dense layouts need
spatial predictability. `--brand-*` is a fluid `clamp()` scale for the landing, with ≥1.25
between heading steps. A raw value in a `font-size` declaration is a bug.

**The One Kicker Rule.** A small uppercase tracked label above a section heading is
permitted **once per route**, as voice. Repeating it above every section is scaffolding, not
design. The marginalia column already supplies small-text texture and will compete with it.

## 4. Elevation

**This system has no elevation.** There are zero `box-shadow` declarations across the
entire stylesheet, and this is doctrine rather than an accident. Depth is conveyed by two
mechanisms only: a single tonal step between the sheet (`#eef0ea`) and its surfaces
(`#e6e9e1`), and 1.5px hairline rules in Rule grey. Panels do not lift, buttons do not cast,
modals do not float.

Corner radius follows the same logic. Everything is square (`0`) except two deliberate
circles at `50%`: the pipeline stage marker on the console rail and the robot position dot
in the plan view. Both are circles because they represent a point, not a container.

### Shadow Vocabulary

None. Intentionally empty.

### Named Rules

**The No-Shadow Rule.** Surfaces separate by tone and hairline, never by shadow. Audit
test: *if it casts a shadow, it is not on the sheet.*

**The Square Rule.** `border-radius` is `0` unless the element represents a literal point in
space, in which case it is a full circle. There is no middle. A 12px rounded card does not
exist in this system.

## 5. Components

Every control is **machined and unforgiving**: square, hairline-stroked, uppercase and
tracked. Controls read as switches on equipment — they either engage or they are plainly,
visibly dead. Nothing is dimmed-and-hopeful.

### Buttons
- **Shape:** Square (`border-radius: 0`), 1.5px stroke.
- **Primary:** Graphite fill (`#12151a`) with vellum text, `0.75rem 1.5rem` padding, label
  typography at `0.12em` tracking, uppercase.
- **Hover / Focus:** Primary inverts to Blueprint Indigo (`#22307e`) fill over 140ms ease.
  Focus is a 2px Blueprint Indigo outline at 3px offset — never a glow, never a shadow.
- **Ghost (console stage actions):** Transparent ground, 1.5px graphite border, graphite
  text, `0.18em` tracking. On hover the fill and text swap: graphite ground, vellum text.
- **Disabled:** Border drops to Rule grey and text to Muted Ink. A disabled stage is
  unmistakably inert, because the orchestrator would reject it anyway.

### Cards / Containers
- **Corner Style:** Square (`0`).
- **Background:** Deep Vellum (`#e6e9e1`) on the vellum sheet.
- **Shadow Strategy:** None. See Elevation.
- **Border:** 1.5px Rule grey on all sides. **Never** a thick coloured stripe on one edge.
- **Internal Padding:** `1.25rem`.
- Nested containers are prohibited. A panel inside a panel is a layout failure.

### Inputs / Fields
- **Style:** Vellum ground, 1.5px Rule border, square, `0.5rem 0.65rem` padding, 16px data
  type. Labels sit above in condensed uppercase Muted Ink at `0.16em`.
- **Focus:** 2px Blueprint Indigo outline, 3px offset.
- **Placeholder:** Must clear 4.5:1. The default browser grey does not qualify.

### Navigation
- Condensed uppercase (`wdth 62`) at 14px, `0.22em` tracking, Muted Ink at rest.
- **Active:** text goes Graphite and a 1.5px Signal Orange Ink underline appears. Colour is
  never the sole signal — weight and underline carry it too.
- The masthead also carries sheet metadata (`SHEET`, `REV`, `FIELD`) in monospace, which is
  what makes the two routes read as one document.

### The Reconstruction Canvas (signature component)
A single `<canvas>` scrubbed by scroll through six pipeline phases on one procedurally
generated room: points sweep in coloured by depth, recolour into semantic clusters, snap to
a twin wireframe with collider tags, take a traced route, then quantize. It is the primary
explanatory device on the landing route — the loop is *shown*, not described.

Motion is GSAP ScrollTrigger with `scrub: true`, so progress is bound to scroll position
rather than played on a timer. Under `prefers-reduced-motion: reduce` the canvas paints its
finished state immediately and the scroll track collapses from 560vh to 100vh, so no one
scrolls through five empty screens. The stage caption is React state (it changes six times);
the point counter writes directly to the DOM (it changes every frame).

## 6. Do's and Don'ts

### Do:
- **Do** use `-ink` colour variants for anything readable: `#a82c0c` and `#06584e`. The
  saturated `#ff5b2e` and `#14b09a` are graphics-only.
- **Do** keep every hairline at `var(--hair)` (1.5px). 1px disappears on a projector.
- **Do** pull every font size from `--ui-*` or `--brand-*`. Never author a raw value.
- **Do** state absence explicitly. "Not profiled yet" with the command that fixes it, never
  a zero or an empty chart.
- **Do** give every scroll-driven or timeline animation a `prefers-reduced-motion`
  equivalent that conveys the same information, and collapse any tall scroll track that
  becomes purposeless without the scrub.
- **Do** separate surfaces with tone (`#eef0ea` → `#e6e9e1`) and hairlines.
- **Do** cap running prose at 60ch and use `text-wrap: balance` on headings, `pretty` on
  prose.

### Don't:
- **Don't** build the **dark neon robotics site** — near-black with acid green or cyan,
  glowing grids, sci-fi HUD chrome. Named in PRODUCT.md as the anti-reference.
- **Don't** build the **generic AI-SaaS landing**: gradient hero metric, three identical
  feature cards, a tracked uppercase eyebrow above every section.
- **Don't** ship **fabricated precision** — invented benchmark numbers, decorative metrics,
  or a populated-looking dashboard no code produced. PRODUCT.md calls this "the single most
  damaging thing this project could ship."
- **Don't** add a `box-shadow`. Anywhere. If it casts a shadow, it is not on the sheet.
- **Don't** add `border-radius` between 0 and 50%. There is no 12px card in this system.
- **Don't** put a coloured stripe on one edge of a card or callout via `border-left`.
- **Don't** render text below 14px, and don't set font sizes in `px`.
- **Don't** use gradient text (`background-clip: text`), glassmorphism, or a blur as
  decoration.
- **Don't** repeat a small uppercase kicker above every section. One per route.
- **Don't** number sections `01 / 02 / 03` unless the content genuinely *is* an ordered
  sequence. The eight pipeline steps qualify because each consumes the previous step's id;
  four unrelated sections do not.
- **Don't** let colour be the sole carrier of state. Pair it with text, weight, or shape.

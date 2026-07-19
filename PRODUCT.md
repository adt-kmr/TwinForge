# Product

## Register

brand

## Users

Hackathon judges and technical evaluators for the Snapdragon Multiverse Hackathon (Noida,
July 2026), plus engineers deciding whether to adopt or contribute to the pipeline. They
land on `/` cold, scanning for "is this real and does it work end to end" in under a
minute, then either open `/dashboard` (the console, a product-register tool for driving
the actual pipeline) or go read the source. Low patience for marketing fluff, high
tolerance for technical density (endpoint signatures, return shapes, thresholds).

## Product Purpose

DragVerse is an edge-first Physical AI pipeline: point a phone at a space and get a
simulation-ready digital twin, a robot taught by voice, and a policy that runs offline on
Snapdragon silicon. The landing page (`Landing.jsx`) is the primary surface — it exists to
prove the eight-call pipeline (capture → reconstruct → segment → generate twin → plan →
train → optimize → deploy) is a real, running system, not a slide deck. Success is a judge
or engineer believing the pipeline works and clicking through to the console or the repo.

## Brand Personality

An instrument, not a costume. Precise, technical, quietly confident — the copy states
mechanism (endpoint signatures, thresholds, file:line-style specifics) instead of
adjectives. Color is diagnostic (a depth-sensor colormap: far=indigo, mid=teal, near=hot),
spent only where the system is actively sensing or working, never as decoration. Motion
should read as instrumentation coming online (a sensor calibrating, a scan sweeping) rather
than a marketing site's entrance choreography.

## Anti-references

Generic SaaS/startup landing-page grammar: gradient-mesh heroes, cream/pastel palettes,
bouncy/elastic motion, rounded-everything cards, hero-metric-with-gradient-text blocks,
tiny uppercase tracked eyebrows over every section, identical icon+heading+text card
grids. If it could be any startup's homepage with the copy swapped, it's wrong for this
brand.

## Design Principles

- **Color carries state, not decoration.** The near/hot end of the depth ramp is spent
  only where the system is actively sensing or computing right now.
- **Mechanism over adjective.** Prefer a concrete endpoint signature, threshold, or file
  reference to a claim like "powerful" or "seamless."
- **The order is enforced by data, not by the interface.** Sequence, gating, and state
  (e.g. `SIM_GATE`, the 0.60 threshold) should be shown as real constraints, not decorative
  progress bars.
- **Instrument, not costume.** One type family (Archivo, contrasting on its width axis)
  plus JetBrains Mono for anything the machine measured — no serif "for warmth," no second
  display face.
- **Motion reads as calibration.** Reveals and transitions should feel like hardware
  coming online (scanning, settling, locking on) rather than generic entrance animation.

## Accessibility & Inclusion

WCAG AA. `prefers-reduced-motion: reduce` must fully no-op every animation (already the
pattern in `useReveal.js` and `Preloader.jsx` — extend it, don't bypass it). Maintain
4.5:1 contrast for body/placeholder text and 3:1 for large text; the existing `-ink`
color pairs (`--near-ink`, `--mint-ink`) exist specifically because the raw ramp colors
fail small-text contrast — reuse them rather than the raw `--near`/`--mid` for text.

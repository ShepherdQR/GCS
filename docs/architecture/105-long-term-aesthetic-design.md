# Long-Term Aesthetic Design — Visual Identity Brief & Figure Gallery

Date: 2026-05-28
Status: active
Depends on: `docs/architecture/102-aesthetic-taste-reevaluation.md` (A7, A8)
Related: `docs/architecture/103-short-term-aesthetic-plan.md` (A1–A4)
Related: `docs/architecture/72-ui-aesthetic-roadmap.md` (Phases 3–5 → A5–A6)

## Purpose

This document provides detailed implementation design for the two long-term
aesthetic items identified in the re-evaluation. They are long-term not because
they're complex, but because their value depends on having accumulated enough
visual artifacts to make the brief authoritative and the gallery impressive.

---

## A7. Visual Identity Brief

**Time horizon:** 2–4 months (after Phase 3–4 implementation produces
stable viewer screenshots)
**Effort:** 1 session

### What

A single document (target: 800–1200 words, 5-minute read) that an external
contributor can read to understand GCS's visual language without reading the
full aesthetic roadmap.

### Structure

```markdown
# GCS Visual Identity Brief

## One Sentence
GCS looks like a quiet technical atelier: warm paper, muted categorical
colors, semantic weight on every pixel.

## Palette (the 15 seconds version)
- Paper: warm ivory (#F7F4EC), not screen-white
- Text: near-black (#181715), not pure black
- Focus: warm rust (#C8643F) — the only saturated color
- Everything else: muted, desaturated, calm

## Typography
- UI: system sans-serif
- Figures: serif for headings, sans for data
- No emoji in labels

## Key Rules
1. Color carries meaning. If it doesn't, use a neutral.
2. Add by subtraction. Before adding a visual element, ask: what can I remove?
3. Flat surfaces, thin borders (#D8D1C4). No shadows, no gradients, no gloss.
4. Constraint type = line style. Constraint state = color. Never swap.
5. Evidence domains have their own fill/stroke pairs. Don't repurpose them.

## Do / Don't

| Do | Don't |
| --- | --- |
| Use `surface.paper` for backgrounds | Use #FFFFFF |
| Use rigid-set palette for rigid sets | Use saturated RGB/CMY |
| Encode constraint type with line style | Use color for constraint type |
| Leave generous margins | Fill every pixel |
| Test at A4 300 DPI for figures | Assume screen-only |

## Where To Look
- `python/gcs_viz/color_scheme.py` — the single source of truth
- `docs/research/20260527/aesthetic-taste/` — taste calibration images
- `docs/architecture/72-ui-aesthetic-roadmap.md` — the full thesis
```

### Acceptance

A new contributor reads this brief in 5 minutes and can:
- Name the 3 most important colors
- State the "add by subtraction" rule
- Find `color_scheme.py`
- Identify a violation of the palette

**File:** `docs/architecture/106-gcs-visual-identity-brief.md`

---

## A8. Figure Gallery

**Time horizon:** 3–6 months (after VE-003, Phase 3–4, and at least one
more scientific figure are produced)
**Effort:** 1 session (assembly) + ongoing (add new figures)

### What

A single scrollable page (HTML or Markdown with inline images) that collects
the project's strongest visual artifacts. This is the aesthetic portfolio —
a reviewer can see the visual range of GCS in 30 seconds of scrolling.

### Candidate Artifacts

| Artifact | Current location | Readiness |
| --- | --- | --- |
| Taste seed: single curve | `docs/research/20260527/aesthetic-taste/elegant_curve_a4.png` | Ready |
| Bridge: constraint graph | `docs/research/20260527/aesthetic-taste/bridge_constraint_graph.png` | Ready |
| VE-001: Figure 72 showcase | `docs/architecture/70-visualization/assets/figure72-*.review.png` | Ready |
| VE-002: Viewer canvas contact sheet | `docs/architecture/70-visualization/assets/ve002-*.review.png` | Ready |
| VE-003: Full-window viewer | `docs/architecture/70-visualization/assets/ve003-full-window-viewer-20260528.png` | Ready |
| Figure 95: Narrative line levels | `docs/architecture/70-visualization/assets/figure95-*.svg` | Ready |
| D5 workbench evidence PNG | `docs/product/demos/d5-solver-evidence-workbench/artifacts/d5-workbench-evidence.png` | Ready |
| Phase 3 inspector (future) | Not yet produced | Blocked on A5 |
| Phase 4 replay rail (future) | Not yet produced | Blocked on A6 |
| B2 comparison figure (future) | Not yet produced | Blocked on M1 |

### Format

A self-contained HTML page at `docs/architecture/70-visualization/figure-gallery.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>GCS Figure Gallery</title>
  <style>
    /* Warm paper background, muted text, thin borders — the GCS palette */
    body { background: #F7F4EC; color: #181715; font-family: sans-serif; }
    .gallery { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    .card { background: #FFFEFA; border: 1px solid #D8D1C4; margin: 1.5rem 0; padding: 1.5rem; }
    .card img { max-width: 100%; }
    .card h3 { color: #5F5B53; }
    .card p { color: #8B867A; font-size: 0.9rem; }
  </style>
</head>
<body>
  <div class="gallery">
    <h1>GCS Visual Evidence</h1>
    <!-- Cards for each artifact -->
  </div>
</body>
</html>
```

### Acceptance

A reviewer opens `figure-gallery.html` in a browser and:
- Sees 5+ artifacts with labels explaining what each proves
- Can scroll from taste seeds → scientific figures → viewer screenshots
- The page itself uses the GCS palette (self-demonstrating)

### Automation

Add a script `tools/architecture_visualization/build_figure_gallery.py` that
reads a manifest (YAML or JSON list of artifacts) and generates the HTML.
This keeps the gallery in sync with the visual evidence manifest
(`docs/architecture/70-visualization/visual-evidence-manifest.md`).

**File:** `docs/architecture/70-visualization/figure-gallery.html`
**Build script:** `tools/architecture_visualization/build_figure_gallery.py`

---

## Dependency Chain

```
A1 (bridge taste seed) ──┐
A2 (full-window shot) ───┤
VE-001, VE-002 ──────────┼──► A8 (figure gallery)
Figure 95 ───────────────┤
Phase 3–4 screenshots ───┘ (future)

A5 (Phase 3 inspector) ──┐
A6 (Phase 4 replay) ─────┼──► A7 (visual identity brief)
Stable viewer UX ────────┘ (future)
```

A8 can start immediately with the 7 ready artifacts. It gains value as new
artifacts are added. A7 should wait until the viewer's spatial design (Phases
3–4) stabilizes, so the brief describes what actually exists, not what is
planned.

---

## Execution Triggers

| Trigger | Action |
| --- | --- |
| Phase 3 inspector implemented | Add Phase 3 screenshot to A8; review A7 readiness |
| Phase 4 replay implemented | Add Phase 4 screenshot to A8; A7 can now be written |
| 7+ artifacts in A8 | A8 is publishable as v1 |
| A7 published | External contributors have a visual onboarding path |

# Scientific Figure Production Paradigm

Research snapshot: 2026-05-24.

The full research result is stored in
`docs/research/20260524/scientific-figure-production-paradigm/README.md`.
This architecture note records the adopted GCS direction.

## Adopted Direction

Dense project showcase and scientific explanation figures must not be authored
as raw Python coordinate drawings. Python may compute evidence and generate
small domain glyphs, but final figure composition should use:

- semantic figure specs;
- specialized layout engines for graphs and charts;
- browser/Figma/Typst composition for text flow;
- automated overlap, overflow, contrast, font-size, and screenshot QA;
- an independent art-direction review pass;
- editable SVG/PDF exports plus review PNGs.

## Required Next Step

Initial landing is complete:

- `.codex/skills/gcs-scientific-figure-producer/SKILL.md`
- `tools/architecture_visualization/specs/figure71.yaml`
- `tools/architecture_visualization/figure71_html_compositor.py`
- `tools/architecture_visualization/figure_qa.py`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.html`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.qa.json`

The new skill forces figure work through:

1. a brief or spec;
2. layout-aware panel generation;
3. browser or Figma composition for dense text;
4. visual QA;
5. independent review.

## Figure 71 Status

`figure71-gcs-step-1-40-evidence-map.svg` is a prototype that revealed the
right content direction but the wrong production paradigm. Its replacement
should evolve from the HTML/CSS compositor and QA pipeline described in the
research folder.

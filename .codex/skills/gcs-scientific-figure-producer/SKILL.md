---
name: gcs-scientific-figure-producer
description: Project-specific workflow for producing publication-quality GCS figures. Use when creating architecture figures, turning execution reports into visual artifacts, producing project showcase or scientific diagrams, editing SVG/HTML/Figma figure pipelines, defining figure specs, running visual QA, or reviewing diagram taste, layout, overlap, typography, evidence visibility, and export readiness.
---

# GCS Scientific Figure Producer

## Source Material

Read these before changing a figure pipeline:

1. `docs/architecture/75-ui-design-system-conventions.md`
2. `docs/architecture/73-gcs-visual-taste-guide.md`
3. `docs/architecture/74-scientific-figure-production-paradigm.md`
4. `docs/research/20260524/scientific-figure-production-paradigm/README.md`
5. The figure's semantic spec under `tools/architecture_visualization/specs/`
6. The source report, fixture, or structured evidence named by the spec

## Required Workflow

1. Write or update the figure brief: main claim, audience, panels, source data,
   required evidence, and export targets.
2. Write or update a semantic figure spec before rendering. Do not make the
   exported SVG the source of truth.
3. Choose panel compilers by semantics:
   - graph or dependency panels: ELK, D2, Graphviz, or a future graph backend;
   - data panels: Vega-Lite, Observable Plot, or a future chart backend;
   - GCS geometry/evidence glyphs: small deterministic generators;
   - dense text panels: browser HTML/CSS or Figma Auto Layout.
4. Compose dense multi-panel figures with real text flow. Avoid raw absolute
   SVG coordinates for labels, captions, chips, and explanatory text.
5. Run visual QA before accepting output:
   - source coverage;
   - required panels;
   - no text-only meaning hidden in color;
   - no absolute-position text compositor for dense figures;
   - browser/screenshot QA when browser tooling is available.
6. Keep generated artifacts rebuildable from repo sources.
7. Treat Python coordinate SVGs as prototypes unless they pass the figure QA
   gate and the art-direction review.
8. Update `docs/architecture/76-ui-design-system-execution-plan.md` when a
   completed figure step changes the remaining plan.

## Figure 71 Baseline

For the Step 1-40 execution report, use:

- spec: `tools/architecture_visualization/specs/figure71.yaml`
- compositor: `tools/architecture_visualization/figure71_html_compositor.py`
- QA: `tools/architecture_visualization/figure_qa.py --figure figure71`

The existing `figure71-gcs-step-1-40-evidence-map.svg` is a prototype, not the
target production paradigm.

## Review Standard

Approve a GCS figure only when:

- the five-second main claim is clear;
- panels show GCS evidence, not generic process decoration;
- text flow is handled by layout rules or measured rendering;
- semantic colors match the visual taste guide;
- obstruction, rejection, diagnostics, or quality gates are visible when the
  subject is solver credibility;
- the output includes an editable artifact and a review artifact;
- QA results are recorded.

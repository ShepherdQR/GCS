# GCS Visual Taste Guide

Research snapshot: 2026-05-24.

This is the canonical visual taste guide for GCS. It consolidates the existing
UI aesthetic roadmap, architecture atlas, Figure 1 workflow, and current design
research into a durable standard for diagrams, reports, GUI surfaces, and future
showcase visuals.

GCS should feel like a quiet technical atelier: precise, warm, mathematical,
alive with evidence, and calm enough for repeated engineering use. The visual
system must make the solver feel trustworthy before it feels impressive.

## Research Base

External sources used for this guide:

| Source | Takeaway for GCS |
| --- | --- |
| [Apple Human Interface Guidelines: Color](https://developer.apple.com/design/human-interface-guidelines/color) and [Typography](https://developer.apple.com/design/human-interface-guidelines/typography) | Use color judiciously, keep typography legible, and avoid color-only meaning. |
| [Fluent 2 design tokens](https://fluent2.microsoft.design/design-tokens) | Store visual decisions as global and semantic tokens, not scattered hex values. |
| [Carbon color system](https://carbondesignsystem.com/elements/color/overview/) and [Carbon data-visualization palettes](https://v10.carbondesignsystem.com/data-visualization/color-palettes/) | Let neutral layers carry most layout, reserve color for semantic data, and avoid inaccessible gradients. |
| [Nature research figure guide](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/) | Use ordered multi-panel storytelling, compact figures, and legible typography. |
| [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | Prefer simple, composable visual workflows over overbuilt process machinery. |
| [Design Tokens Community Group](https://www.designtokens.org/) | Keep visual language portable across tools and implementations. |
| [Observable Framework](https://observablehq.com/framework/) | Treat reports and dashboards as reproducible code-backed artifacts. |
| [TASTE: Designer-Annotated Multi-Dimensional Preference Dataset](https://arxiv.org/abs/2605.20731) | Judge design across separate axes such as typography, hierarchy, color harmony, layout, and brief fidelity. |

Local sources consolidated here:

- `docs/architecture/70-visualization/gcs-architecture-atlas.md`
- `docs/architecture/70-visualization/svg-editing-workflow.md`
- `docs/architecture/72-ui-aesthetic-roadmap.md`
- `docs/research/20260524/claude-ui-aesthetic-visualization-report.md`
- `tools/architecture_visualization/figure1.theme.json`
- `tools/architecture_visualization/figure1.layout.json`

## Taste Thesis

The best GCS visuals are not prettier flowcharts. They are certificate-like
scientific explanations.

A high-taste GCS figure answers four questions immediately:

1. What domain object is being solved?
2. Which contracts transform it?
3. What evidence makes the result credible?
4. Where can the process reject, diagnose, or explain failure?

The visual voice is scientific editorial, not SaaS dashboard, game UI, or
marketing hero. It should carry the authority of a Nature figure, the restraint
of a mature design system, and the warmth already chosen for the GCS viewer.

## Beauty Principles

### 1. Evidence Is The Ornament

Do not decorate around the solver. Put the solver evidence into the figure:
residuals, rank, DOF, free and frozen variables, gluing agreement, conflict
sets, redundancy sets, obstruction reports, command acceptance, and rollback.

If a visual element does not encode evidence, hierarchy, focus, or interaction,
remove it.

### 2. Domain Objects Before Boxes

GCS should not be represented only as rectangles and arrows. Every major figure
should include real or fixture-derived domain objects:

- points, lines, rigid sets, and constraints;
- incidence or body-graph structure;
- context covers and overlaps;
- local sections and boundary projections;
- residual/rank evidence;
- accepted and rejected command outcomes.

Architecture boxes are allowed, but they should not be the main character.

### 3. Semantic Color, Never Decorative Color

Color must have stable meaning. A reader should be able to learn the color
system once and reuse it across diagrams, GUI overlays, reports, and QA
screenshots.

| Meaning | Token direction | Current figure token family |
| --- | --- | --- |
| Durable model truth | muted blue | `domain`, `domain_stroke` |
| Incidence and structural graph | muted violet | `graph`, `graph_stroke` |
| Cover, boundary, gluing | sage | `planner`, `planner_stroke` |
| Numeric solve evidence | olive | `numeric`, `numeric_stroke` |
| Diagnostics and decision evidence | ochre | `diagnostic`, `diagnostic_stroke` |
| Failure, obstruction, rejection | terracotta | `failure`, `failure_stroke` |
| IO, viewer, adapter boundary | warm neutral | `boundary`, `boundary_stroke` |
| Active focus or current replay moment | restrained accent | `accent` |

Use gradients only for scalar magnitude when a sequential palette is truly
needed. Never use gradients as ambient decoration.

### 4. Warm Precision

Use warm paper and panel surfaces, near-black ink, warm gray secondary labels,
and thin rules. Avoid sterile white chrome, neon debug colors, heavy shadows,
glow effects, glass effects, and large-radius card stacks.

The current `claude-warm-editorial` theme is the baseline:

- paper: `#f7f4ec`
- panel: `#fffefa`
- ink: `#181715`
- muted text: `#5f5b53`
- rule: `#d8d1c4`
- accent: `#c8643f`

Future palettes may evolve, but they must preserve the same semantic mapping.

### 5. Panel Storytelling

Use a small number of named panels instead of one giant diagram. Each panel
should carry one reasoning task.

Preferred panel types:

- domain scene;
- contract pipeline;
- local-to-global cover;
- numeric evidence;
- diagnostic outcome;
- corpus or quality gate evidence;
- timeline or maturity map.

Panel labels should be ordered and visible. Captions should explain meaning
outside the figure rather than crowding the canvas.

### 6. Tokenized, Rebuildable Beauty

Final visuals may be editorial, but they must stay reproducible. The standard
pipeline is:

1. architecture truth in Markdown and contracts;
2. fixture or report evidence in structured files;
3. theme and layout controls in JSON;
4. deterministic SVG or HTML output;
5. optional editor review synced back to tokens.

Do not create a beautiful one-off image that cannot be rebuilt after the
architecture changes.

## Figure System

### Visual Density

GCS figures should be rich, not crowded.

Use this density rule:

- five-second read: the main claim is obvious;
- thirty-second read: the major stages and outcomes are clear;
- three-minute read: the evidence path and failure modes are inspectable.

### Typography

Use restrained hierarchy:

| Role | Direction |
| --- | --- |
| Figure title | serif-capable or humanist, 24-32 px at SVG scale |
| Panel title | sans, 14-16 px, medium weight |
| Labels | sans, 10-13 px |
| Evidence numbers | tabular or monospace-capable, 11-14 px |
| Dense code/contract names | monospace only when it improves scanning |

Text must fit its container at the intended display size. Do not use viewport
scaled type or negative letter spacing.

### Layout

Use a stable grid with generous gutters. Prefer left-to-right for time or data
flow, top-to-bottom for abstraction layers, and overlays for local-to-global
cover semantics.

Avoid nested cards. Use panels for multi-part figures and small cards only for
individual evidence facts.

### Lines And Edges

Line semantics:

| Line | Meaning |
| --- | --- |
| Solid arrow | runtime flow, transformation, or allowed consumption |
| Dotted arrow | evidence, report, read-only projection, design feedback |
| Dashed outline | candidate, unsupported path, rejected proposal |
| Heat or thickness | scalar magnitude only |

Every arrow should have either an obvious direction or a short label.

## Step 1-40 Procedure Picture Brief

The Step 1-40 execution report is good as a textual audit trail. For display,
it should become a vivid procedure figure named:

`Figure 71 - GCS Evidence-Boundary Flight Map`

The figure should show how GCS moved from foundation contracts to public
evidence boundaries, then to the next algorithm-deepening batch.

### Main Claim

Steps 1-40 are not a flat checklist. They are a staged transformation:

`canonical contracts -> executable solver evidence -> public promotion gates -> viewer-visible diagnostics -> post-Step-40 showcase`

### Recommended Panels

| Panel | Content | Visual treatment |
| --- | --- | --- |
| a. Foundation runway | Steps 1-13 as kernel, catalog, graph, planner, numeric, diagnostics, runtime, IO, viewer, tools, quality | compact module blocks over a warm base line |
| b. Algorithm lift | Steps 14-18 as numeric solving, JSON IO, diagnostics candidates, fixture corpus, quality gates | stage cards connected to evidence badges |
| c. Scene-generation loop | Steps 19-27 as explorer, store, public scene, runtime, diagnostics, viewer gates | loop/flywheel around fixture corpus |
| d. Rank evidence spine | Steps 28-35 as free/frozen rank propagation through numeric, diagnostics, runtime, viewer, promotion, SolveDAG, conflicts | vertical evidence spine with report projections branching out |
| e. Evidence closure horizon | Steps 36-40 as robustness, corpus, viewer evidence surface, quality gates, atlas sync | horizon band that shows the evidence-boundary closure before the showcase |
| f. Showcase candidate | integrated feature constraint graph after Step 40 | real or generated geometry mini-scene with rank/diagnostic chips |

### Visual Encoding

- Completed steps use quiet filled tokens and a small check glyph.
- Pending steps use warm outline tokens, not warning red.
- Step themes group into five arcs instead of 40 equal boxes.
- Evidence artifacts are first-class nodes: `RankReport`,
  `PostLocalDiagnosticReport`, `ViewerOverlayEvidence`, promotion gates,
  golden digests, fixture corpus.
- The center of the figure should be the evidence spine, not the timeline.
- Failure/rejection visual language should be reserved for actual obstruction
  examples, not pending work.

### Data Inputs

Primary source:

- `docs/architecture/71-step-1-40-execution-report.md`

Supporting sources:

- `docs/architecture/66-implementation-execution-roadmap.md`
- `docs/architecture/68-forward-execution-plan-2026-05-24.md`
- `docs/architecture/70-visualization/gcs-architecture-atlas.md`
- `tools/architecture_visualization/figure1.theme.json`

### Deliverable Shape

Create the first version as a deterministic SVG:

- source script under `tools/architecture_visualization/`;
- theme token reuse from `figure1.theme.json`;
- layout token file for the new figure;
- output under `docs/architecture/70-visualization/assets/`;
- Markdown embedding from the execution report or a companion visualization doc.

Current implementation:

- `tools/architecture_visualization/render_gcs_figure71.py`
- `tools/architecture_visualization/figure71.layout.json`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.svg`
- embedded from `docs/architecture/71-step-1-40-execution-report.md`

This current implementation should be treated as a prototype, not the final
top-tier production paradigm. For dense multi-panel figures, the target is the
auto-laid-out, browser/Figma-composed, QA-checked workflow in
`docs/research/20260524/scientific-figure-production-paradigm/README.md`.

Do not hand-edit final step labels in the SVG. If step names change, the source
Markdown or structured extraction should drive regeneration.

## GUI Taste

For the Python viewer, the same taste becomes a working surface:

- the canvas is the center, not the panels;
- controls are dense, quiet, and predictable;
- rigid sets use muted categorical swatches;
- constraints use line style and marker semantics before color;
- selection, replay-current, violation, and solved states are distinct;
- solver feedback appears as summary evidence, not terminal-style noise;
- logs are secondary unless the user opens them.

The viewer should look like a serious mathematical instrument that happens to
be kind.

## Do And Do Not

Do:

- show real geometry and evidence;
- keep color semantic and sparse;
- use tokenized themes and layout;
- make failure modes visible;
- keep text short inside figures;
- preserve architecture dependency truth;
- verify legibility at README scale and presentation scale.

Do not:

- use generic AI-dashboard gradients;
- use dark neon debug panels;
- use rainbow rigid-set colors;
- rely on color alone for state;
- turn every stage into an equal rectangle;
- hide reports behind a black-box solver;
- create one-off bitmap art as the source of truth.

## Acceptance Gate

A GCS visual passes the taste gate only if it satisfies all of these checks:

1. The main claim is readable in five seconds.
2. Domain objects or evidence appear on the canvas.
3. Every accent color has a semantic role.
4. Text is legible at target display size.
5. The figure distinguishes runtime flow from evidence/report projection.
6. The visual can be rebuilt from repo sources.
7. It expresses GCS local-to-global semantics, not a generic software pipeline.
8. It shows at least one rejection, obstruction, diagnostic, or quality gate
   when the subject includes solver credibility.

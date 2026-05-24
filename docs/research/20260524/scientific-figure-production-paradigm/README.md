# Scientific Figure Production Paradigm Research

Research snapshot: 2026-05-24.

This folder stores the research result for top-tier GCS project showcase and
scientific explanation figures. The immediate motivation is that direct
Python-to-SVG drawing can make a figure look globally coherent while still
causing local text/image collisions. That failure mode is structural: dense
multi-panel figures need layout engines, editable text, visual QA, and a design
review loop.

## Core Finding

World-class scientific/project figures are not produced by one script placing
every label by absolute coordinates. The mature paradigm is:

```text
semantic figure spec
  -> specialized layout engines
  -> browser or Figma/Typst editorial composition
  -> automated overlap, legibility, contrast, and screenshot QA
  -> human art-direction pass
  -> editable SVG/PDF plus review PNG
```

Python remains useful for computing evidence and generating small domain
glyphs. It should not be the final compositor for dense text-heavy figures.

## Researched Sources

| Source | What It Contributes |
| --- | --- |
| [Nature research figure guide](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/) | Figure panels must be ordered, space-efficient, legible, editable, and exported as production vector/layered formats. |
| [Penrose SIGGRAPH 2020](https://penrose.cs.cmu.edu/siggraph20) | Mathematical diagrams should separate semantic truth from visual placement and use constraints/optimization to preserve meaning. |
| [Vega-Lite](https://vega.github.io/vega-lite/) | Data panels should use declarative visualization grammar instead of hand-coded axes, legends, and scales. |
| [Graphviz](https://graphviz.org/) and [Graphviz layout engines](https://graphviz.org/docs/layouts/) | Structural diagrams should use graph layout engines and export vector artifacts. |
| [Eclipse Layout Kernel](https://eclipse.dev/elk/) | Compound graphs, hierarchical nodes, ports, and edge anchors are first-class layout problems. |
| [D2 documentation](https://d2lang.com/ko/) | Modern diagram-as-code can combine themes, containers, multiple layout engines, Markdown, tables, fonts, and SVG/PDF export. |
| [AutoFigure](https://arxiv.org/abs/2602.03828) | AI-era scientific figure generation uses planning, recombination, validation, layout refinement, and publication-readiness checks. |
| [Feynman diagramming agent](https://arxiv.org/abs/2603.12597) | Scalable diagram agents enumerate domain ideas, produce declarative programs, render, receive feedback, and refine. |
| [Figma MCP server](https://developers.figma.com/docs/figma-mcp-server/) | MCP can connect agents to Figma design context and write native frames, components, variables, and Auto Layout. |
| [Figma MCP setup for Codex](https://developers.figma.com/docs/figma-mcp-server/remote-server-installation/) | Codex can use the Figma plugin/MCP flow when authenticated and available. |
| [Figma file-structure guidance](https://developers.figma.com/docs/figma-mcp-server/structure-figma-file/) | Figma quality depends on components, variables, semantic layer names, Auto Layout, annotations, and dev resources. |
| [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots) | Rendered visual artifacts should be screenshot-tested in a stable browser/font environment. |

## GCS-Specific Interpretation

### What Went Wrong With Pure Python SVG

The current direct-drawing approach has three predictable weaknesses:

- it estimates text size instead of measuring rendered text;
- it truncates or wraps labels without layout negotiation;
- it treats panel composition as static coordinates instead of constraint or
  flow layout.

This creates the exact issue observed by the user: the whole figure can feel
good, while local labels overlap chips, arrows, geometry, or panel boundaries.

### Target Stack

| Need | Recommended Tooling |
| --- | --- |
| Editorial composition and text flow | HTML/CSS rendered by Playwright |
| Data charts | Vega-Lite or Observable Plot |
| Graph layout | ELK.js first; Graphviz/D2 for architecture diagrams |
| Domain geometry glyphs | Small Python or TypeScript SVG generators |
| Mathematical constraint diagrams | Future Penrose or Penrose-like DSL |
| Typeset exports | Typst or LaTeX when paper/PDF output matters |
| Visual QA | Playwright screenshots plus DOM/SVG bounding-box checks |
| Editorial design surface | Optional Figma MCP with Auto Layout and variables |
| Final artifacts | Editable SVG/PDF plus review PNG |

## Recommended Production Pipeline

### 1. Figure Brief

Every major GCS figure starts with a short brief:

- main claim;
- audience;
- panel list;
- source data;
- semantic vocabulary;
- rejection/failure modes that must be visible;
- final target: README, paper, deck, GUI, or poster.

### 2. Semantic Figure Spec

Store a JSON/YAML spec under `tools/architecture_visualization/specs/`.

The spec should define:

- panels;
- data sources;
- semantic entities;
- graph nodes and edges;
- evidence metrics;
- label priority;
- minimum text size;
- wrapping rules;
- layout constraints;
- export targets.

The spec is the source of truth, not the exported SVG.

### 3. Panel Compilers

Compile each panel with the right engine:

- graph panels: ELK/D2/Graphviz;
- chart panels: Vega-Lite/Observable Plot;
- domain panels: GCS-specific geometry generator;
- text-heavy panels: HTML/CSS or Figma Auto Layout;
- math-heavy panels: Typst/LaTeX/Penrose depending on purpose.

### 4. Editorial Composer

Compose the full figure in browser-rendered HTML/CSS or Figma. Text must remain
real text until export. Use CSS grid/flexbox or Figma Auto Layout so labels
wrap and containers resize before export.

Absolute SVG coordinates are allowed only inside already-measured subpanels.

### 5. Visual QA Gate

Before accepting a figure:

- render desktop and compact review sizes;
- detect bounding-box overlaps for text and important shapes;
- detect text overflow;
- check minimum font size at target dimensions;
- check contrast for text over background;
- run screenshot comparison against accepted baselines;
- produce a review PNG for human inspection.

### 6. Art Director Review

Use a separate reviewer pass for:

- five-second main claim;
- panel hierarchy;
- semantic color discipline;
- text economy;
- alignment rhythm;
- local-to-global GCS fidelity;
- visible evidence, rejection, and diagnostic paths.

The reviewer should not be the same agent that authored the figure when a
separate agent is available.

## MCP Recommendation

### Figma MCP

Recommendation: install/enable when we want high-end editorial review, but do
not make it the core deterministic engine.

Use it for:

- high-stakes showcase figures;
- paper-style graphical abstracts;
- demo/investor/presentation visuals;
- human design review loops.

Do not rely on it for:

- extracting GCS semantics;
- CI-only evidence diagrams;
- replacing visual QA;
- one-shot prompt-to-image generation.

The best Figma MCP setup for GCS would include:

- Figma variables matching `figure1.theme.json`;
- GCS figure components: panel frames, evidence chips, rank cards, diagnostic
  status tokens, graph nodes, geometry callouts;
- semantic layer names;
- Auto Layout everywhere text can grow;
- annotations for domain intent.

### Playwright Or Browser Tooling

Recommendation: required. This is the visual QA harness, not decoration. We
need browser rendering to measure real text boxes, catch overlaps, capture
screenshots, and maintain baselines.

### Graph/Layout Tooling

Recommendation: required locally before the pipeline can become serious.

Candidate dependencies:

- `@playwright/test`
- `elkjs`
- `vega`, `vega-lite`
- optional `@observablehq/plot`
- `d3`
- D2 CLI or Graphviz
- Typst CLI when PDF/paper output matters

These should go through GCS third-party governance before becoming required CI
dependencies.

## Skill And Agent Recommendation

Create a project skill:

```text
.codex/skills/gcs-scientific-figure-producer/SKILL.md
```

Trigger it when creating architecture figures, turning reports into visual
artifacts, producing paper/demo/showcase diagrams, editing SVG/HTML/Figma
figure pipelines, or running visual QA.

The skill should force this sequence:

1. read `docs/architecture/73-gcs-visual-taste-guide.md`;
2. read this research folder;
3. write a figure brief;
4. create/update a semantic figure spec;
5. use layout engines and browser/Figma layout for dense text;
6. run visual QA;
7. keep artifacts rebuildable.

Recommended agent roles:

| Agent | Responsibility |
| --- | --- |
| `figure-production-agent` | Converts GCS source data into semantic specs, panel compilers, rendered artifacts, and export files. |
| `figure-art-director-agent` | Performs independent visual review against taste, readability, overlap, hierarchy, and publication/export requirements. |

## Immediate GCS Action Plan

Completed first landing:

- kept the existing Figure 71 SVG as a prototype;
- added the `gcs-scientific-figure-producer` project skill;
- created `tools/architecture_visualization/specs/figure71.yaml`;
- added the HTML/CSS compositor;
- added a structural QA command and QA JSON artifact.

Next implementation steps:

1. Replace direct Figure 71 SVG drawing with a richer compositor:
   - parse report data;
   - generate chart/graph/domain panels with specialized engines;
   - compose full figure as HTML/CSS;
   - render/export through browser automation;
   - run overlap, font-size, contrast, and screenshot checks.
2. Add Playwright-based real browser measurement and screenshot export.
3. Add ELK/Vega-Lite after third-party governance approval.
4. Consider Figma MCP after the repo-native pipeline exists, or immediately for
   a high-stakes showcase image.

## Acceptance Standard

A future GCS figure pipeline is accepted only when:

- text flow is handled by a layout engine, not manual string truncation;
- all panel text is real text until final export;
- collision and overflow checks run automatically;
- final artifacts include editable SVG/PDF and review PNG;
- source data and figure spec are versioned;
- an independent review pass approves hierarchy, taste, and GCS semantic
  fidelity.

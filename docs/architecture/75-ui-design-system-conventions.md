# UI Design System Conventions

Snapshot date: 2026-05-24.

This document names the durable UI design system conventions for GCS. It is the
entry point for deciding whether a GUI, report, figure, or visualization change
matches the program's intended aesthetic.

## Canonical Names

| Convention name | Scope | Source of truth |
| --- | --- | --- |
| **GCS Quiet Technical Atelier** | Overall product and UI aesthetic thesis. | This document and `72-ui-aesthetic-roadmap.md`. |
| **GCS Warm Evidence Tokens** | Shared color, surface, typography, stroke, radius, and state-token vocabulary. | `tools/architecture_visualization/figure1.theme.json` and future token mirrors in `python/gcs_viz/color_scheme.py`. |
| **GCS Evidence-First Interface Grammar** | How UI elements encode solver meaning: geometry, constraints, rank, residuals, diagnostics, replay, solve status, obstruction, and quality evidence. | `73-gcs-visual-taste-guide.md` plus viewer/GUI phase docs. |
| **GCS Scientific Figure Pipeline** | How dense architecture, research, and showcase figures are produced. | `74-scientific-figure-production-paradigm.md` and `docs/research/20260524/scientific-figure-production-paradigm/`. |
| **GCS Visual Integrity Gate** | Required review and QA checks for UI and figure artifacts. | Phase 5 of `72-ui-aesthetic-roadmap.md`, `figure_qa.py`, and future screenshot/browser gates. |
| **GCS Art Director Review** | Independent review role for hierarchy, taste, text economy, semantic color, and local-to-global fidelity. | Future agent role cards and this convention. |

## Program-Level UI Thesis

The GCS UI should feel like a quiet technical atelier: warm, precise,
mathematical, evidence-rich, and calm under repeated use. The UI must serve
solver work before decoration.

The design system is not a skin. It is an evidence contract:

- geometry and constraints remain inspectable;
- solver reports are visible as structured evidence;
- color carries semantic meaning;
- dense data stays scannable;
- temporal workflows such as replay and solve progress feel deliberate;
- generated figures remain rebuildable and QA-checked.

## Required Conventions

### Color And State

- Use warm technical neutrals for background, panels, controls, and text.
- Use semantic accent colors only for domain meaning, state, focus, or evidence.
- Encode rigid sets with muted categorical swatches, not saturated rainbows.
- Encode constraint type primarily by line style, marker, or shape before color.
- Do not rely on color alone for state.

### Layout

- Keep the model canvas or figure evidence at the visual center.
- Use panel grouping only when each panel carries a distinct reasoning task.
- Avoid nested cards and decorative containers.
- Prefer flow layout, Auto Layout, CSS grid/flex, or graph/layout engines for
  text-heavy surfaces.
- Absolute coordinates are acceptable only inside measured domain glyphs or
  small generated subpanels.

### Typography

- Text must fit its container at target display size.
- Use restrained hierarchy: title, panel title, label, metric, caption.
- Keep figure and UI labels short; move explanation to captions, docs, or
  structured reports.
- Do not use negative letter spacing or viewport-scaled font tricks.

### Evidence Presentation

- A solve result is not accepted visually until residual, rank, diagnostics,
  boundary/gluing, and runtime decision evidence are visible or reachable.
- Rejected, obstructed, redundant, conflicting, and under-constrained states
  must have named visual states.
- Logs are secondary evidence; structured summaries are primary.

### Generated Figures

- Dense figures start from a semantic spec, not an exported SVG.
- Text-heavy composition must use browser/Figma/Typst-style layout, not direct
  Python coordinate drawing.
- Figure artifacts must include source data/spec, editable output when
  possible, review output, and QA result.

## Acceptance Rule

A UI or figure change satisfies the GCS design system only when it can name
which convention it follows:

- **GCS Quiet Technical Atelier** for overall taste;
- **GCS Warm Evidence Tokens** for tokens;
- **GCS Evidence-First Interface Grammar** for state and evidence semantics;
- **GCS Scientific Figure Pipeline** for dense figures;
- **GCS Visual Integrity Gate** for QA;
- **GCS Art Director Review** for independent visual judgment.

If a change cannot name its governing convention, it should be treated as a
prototype until reviewed.


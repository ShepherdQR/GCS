# GCS Architecture Visualization and SVG Editing Workflow

Completed: 2026-05-24

Status: done

## Goal

Build a high-quality architecture visualization system for GCS, starting from
research into top AI company and Nature-style architecture figures, then turning
that research into a reproducible Figure 1 and an editable SVG workflow that
both a human designer and Codex can operate.

## Completed Scope

- Researched architecture figure practices from top AI companies and Nature
  papers.
- Cached 10 visual case studies locally and wrote an analysis report.
- Created `Figure 1 | GCS Local-To-Global Constraint Solving` as the editorial
  artifact for the architecture atlas.
- Kept Mermaid diagrams as the structural source and generated SVG as the
  editorial artifact.
- Added fixture-derived geometry, incidence, residual/rank, runtime pipeline,
  visual grammar, and topos semantics panels.
- Upgraded the figure to a warm Claude-inspired editorial style.
- Fixed text-overlap issues in panels `a`, `c`, and `e`.
- Linked the architecture figure from `README.md`.
- Split visual controls out of Python into theme and layout JSON files.
- Added an Inkscape round-trip workflow with stable `data-layout-key` markers.
- Completed one real Inkscape sync: the `panel c` rank card was moved from
  `(342, 76)` to `(352, 70)`, then the official SVG assets were regenerated.
- Committed and pushed the official SVG outputs, Inkscape draft, and V1/V2
  historical drafts to `master`.

## Durable Outputs

Research:

- `docs/research/20260523/top-ai-architecture-figure-casebook.md`
- `docs/research/20260523/assets/top-ai-architecture-figures/`
- `docs/research/20260524/claude-ui-aesthetic-visualization-report.md`

Architecture visualization:

- `docs/architecture/70-visualization/gcs-architecture-atlas.md`
- `docs/architecture/70-visualization/svg-editing-workflow.md`
- `docs/architecture/70-visualization/assets/figure1-gcs-local-to-global.svg`
- `docs/architecture/70-visualization/assets/figure1-panel-a-geometry.svg`
- `docs/architecture/70-visualization/assets/figure1-panel-b-incidence.svg`
- `docs/architecture/70-visualization/assets/figure1-panel-c-residual-rank.svg`
- `docs/architecture/70-visualization/assets/figure1-gcs-local-to-global.inkscape.svg`
- `docs/architecture/70-visualization/assets/figure1-gcs-local-to-global-V1.svg`
- `docs/architecture/70-visualization/assets/figure1-gcs-local-to-global-V2.svg`

Generation and editing tools:

- `tools/architecture_visualization/render_gcs_figure1.py`
- `tools/architecture_visualization/figure1.theme.json`
- `tools/architecture_visualization/figure1.layout.json`
- `tools/architecture_visualization/sync_inkscape_layout.py`

Project entry point:

- `README.md`

## Workflow Now Available

Open the official SVG in Inkscape:

```powershell
inkscape docs\architecture\70-visualization\assets\figure1-gcs-local-to-global.svg
```

Save an editable copy:

```text
docs/architecture/70-visualization/assets/figure1-gcs-local-to-global.inkscape.svg
```

Sync supported geometry back into layout tokens:

```powershell
python tools\architecture_visualization\sync_inkscape_layout.py --svg docs\architecture\70-visualization\assets\figure1-gcs-local-to-global.inkscape.svg --layout tools\architecture_visualization\figure1.layout.json
```

Regenerate official SVG assets:

```powershell
python tools\architecture_visualization\render_gcs_figure1.py --fixture fixtures\scene\saved\triangle_003_graph.json --out-dir docs\architecture\70-visualization\assets
```

## Validation Evidence

The final synced layout was checked with:

```text
layout keys seen: 15; changed: 0
svg xml ok
```

The real Inkscape round-trip produced:

```diff
panels.evidence.rank_card.x: 342 -> 352
panels.evidence.rank_card.y: 76  -> 70
```

## Key Commits

- `fed38c2 docs: add svg editing workflow`
- `eca4e72 merge: bring svg editing workflow to master`
- `3eb4c38 docs: sync figure one inkscape layout`

## Follow-Up

- Fine-tune panel `e`: the `X` node and `1 Finite site C` title are still
  visually close.
- Make `sync_inkscape_layout.py` read JSON with `utf-8-sig` to tolerate
  Windows tools that save UTF-8 with BOM.
- Consider moving future editable SVG drafts into an `assets/drafts/` folder if
  draft count grows.

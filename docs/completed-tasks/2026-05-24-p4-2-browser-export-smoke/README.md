---
task_id: 2026-05-24-p4-2-browser-export-smoke
status: complete
session_goal: "Close P4.2 by adding a thin browser export smoke for the GCS scientific figure pipeline."
archive_target: docs/completed-tasks/2026-05-24-p4-2-browser-export-smoke/
---

# P4.2 Browser Export Smoke

## Problem Solved

Figure 71 had a tokenized HTML compositor and structural QA, but no durable
browser-rendered export path. That left a gap between "the HTML source is
layout-aware" and "reviewers can inspect a PNG/PDF artifact produced by a real
browser."

P4.2 adds that missing smoke gate without introducing new package governance
work.

## Scope And Non-Goals

In scope:

- add a dependency-light browser export script for Figure 71;
- use installed Chrome, Edge, or Chromium CLI when available;
- write a manifest that records exported, partial, skipped, or failed status;
- prove canonical `--gcs-*` token presence in the HTML source;
- update Figure 71 QA and roadmap docs.

Out of scope:

- installing Figma MCP, Playwright, graph, or chart packages;
- rebuilding the final showcase asset set;
- changing solver/runtime/viewer behavior;
- touching the separate runtime Step 47 replay evidence export task.

## Durable Files And Artifacts

- `tools/architecture_visualization/browser_export.py`
- `tools/architecture_visualization/figure_qa.py`
- `tools/architecture_visualization/specs/figure71.yaml`
- `docs/architecture/83-p4-2-browser-export-execution-plan.md`
- `docs/architecture/76-ui-design-system-execution-plan.md`
- `docs/architecture/82-ui-design-next-work-plan.md`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.html`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-browser-export.json`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.review.png`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.review.pdf`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.qa.json`

## Validation

Commands run:

```text
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p4-2-browser-export-smoke.md
python -B -c "import ast, pathlib; [ast.parse(path.read_text(encoding='utf-8')) for path in [pathlib.Path('tools/architecture_visualization/browser_export.py'), pathlib.Path('tools/architecture_visualization/figure_qa.py'), pathlib.Path('tools/architecture_visualization/figure71_html_compositor.py')]]; print('ast ok')"
python -B tools\architecture_visualization\browser_export.py --figure figure71 --formats png,pdf --render-html
python -B tools\architecture_visualization\figure_qa.py --figure figure71
```

Observed results:

- Task card validation passed.
- Python AST parse passed.
- Browser export status was `exported`.
- Review PNG and PDF were produced by local Chrome CLI.
- Manifest token checks passed for `--gcs-surface-paper`,
  `--gcs-surface-panel`, `--gcs-text-primary`, `--gcs-token-fill`, and
  `--gcs-token-stroke`.
- Figure QA passed, including browser manifest status, token proof, and
  artifact existence checks.

## Decisions

- Keep P4.2 thin and dependency-light.
- Treat HTML as the editable artifact and PNG/PDF as browser-rendered review
  artifacts.
- Record skipped browser status as valid smoke evidence only when no browser
  backend is available; missing token proof remains a QA failure.
- Move P5.1 token lint ahead of P4.4 asset rebuild.

## Follow-Up

Next preferred step:

```text
P5.1 Token Lint Gate
```

After P5.1, continue with the P4.3 dependency decision and P4.4 execution-map
asset rebuild.

---
task_id: 2026-05-24-p4-2-browser-export-smoke
status: complete
request: "Add a thin browser-export smoke path for the GCS execution-map figure pipeline."
scope: tool
risk: medium
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-scientific-figure-producer
affected_contracts:
  - GCS Scientific Figure Pipeline
  - GCS Visual Integrity Gate
affected_paths:
  - tools/architecture_visualization/
  - docs/architecture/70-visualization/
  - docs/architecture/76-ui-design-system-execution-plan.md
  - docs/architecture/82-ui-design-next-work-plan.md
required_evidence:
  - validate-task-card
  - browser-export-smoke
  - figure-qa
  - python-ast-parse
  - git-diff-check
human_gate_required: false
human_gate_reason: ""
---

# P4.2 Browser Export Smoke

## Scope

Build the smallest repo-native export path that can turn the tokenized
Figure 71 HTML artifact into browser-rendered review artifacts when a local
Chrome, Edge, or Chromium CLI is available. Record a manifest either way so
future P4.4/P5 work can tell whether the smoke exported, skipped, or failed.

## Non-Goals

- Do not install new browser, Figma, MCP, graph, or chart dependencies.
- Do not rebuild the final execution-map figure set; P4.4 owns that.
- Do not change solver, runtime, scene, or viewer semantics.
- Do not stage unrelated Step 47 runtime replay/export work.

## Context To Read

- `docs/architecture/75-ui-design-system-conventions.md`
- `docs/architecture/76-ui-design-system-execution-plan.md`
- `docs/architecture/82-ui-design-next-work-plan.md`
- `docs/architecture/74-scientific-figure-production-paradigm.md`
- `tools/architecture_visualization/specs/figure71.yaml`
- `tools/architecture_visualization/figure71_html_compositor.py`
- `tools/architecture_visualization/figure_qa.py`

## Execution Plan

1. Add a browser export script that discovers an installed Chromium browser,
   exports PNG/PDF artifacts, and writes a manifest when export is unavailable.
2. Extend the Figure 71 spec and QA contract so browser smoke evidence is a
   first-class artifact, without making external browser dependencies mandatory.
3. Run validation: task-card check, Python syntax parse, browser export smoke,
   figure QA, and diff whitespace check.
4. Archive the completed task, update the P4 roadmap, and forge one reusable
   lesson with the Bladesmith process.
5. Commit and push only the files for this step.

## Acceptance Gates

- `browser_export.py` can produce PNG/PDF through a headless Chromium CLI when
  available.
- The browser smoke manifest records exported, partial, skipped, or failed
  state and checks canonical `--gcs-*` token presence in the HTML source.
- `figure_qa.py` checks the browser manifest when the spec declares browser
  smoke as required.
- Roadmap docs move P4.2 from pending to done and name P5.1 token lint as the
  next preferred step.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p4-2-browser-export-smoke.md
python -B -c "import ast, pathlib; [ast.parse(path.read_text(encoding='utf-8')) for path in [pathlib.Path('tools/architecture_visualization/browser_export.py'), pathlib.Path('tools/architecture_visualization/figure_qa.py')]]"
python -B tools\architecture_visualization\browser_export.py --figure figure71 --formats png,pdf --render-html
python -B tools\architecture_visualization\figure_qa.py --figure figure71
git diff --check -- tools/architecture_visualization docs/architecture docs/agentic/tasks docs/completed-tasks
```

## Evidence Bundle

- `validate-task-card`: passed.
- Python AST parse: passed for `browser_export.py`, `figure_qa.py`, and
  `figure71_html_compositor.py`.
- `browser_export.py --render-html`: exported Figure 71 PNG/PDF through local
  Chrome CLI and wrote `figure71-gcs-step-1-40-browser-export.json`.
- Manifest token proof: passed for `--gcs-surface-paper`,
  `--gcs-surface-panel`, `--gcs-text-primary`, `--gcs-token-fill`, and
  `--gcs-token-stroke`.
- `figure_qa.py --figure figure71`: passed, including browser manifest and
  exported artifact existence checks.
- Visual spot check: review PNG shows the complete Step 1-40 map in one
  browser-rendered image.

## Residual Risks

- The smoke uses browser CLI behavior, so exact PDF/screenshot rendering may
  vary slightly across Chrome/Edge versions.
- SVG export is intentionally not claimed in P4.2 unless a reliable browser or
  design-surface backend is added later.
- P5 still needs stronger token lint, text overflow, overlap, contrast, and
  screenshot gates before final showcase work.

---
task_id: 2026-05-24-p4-4-execution-map-rebuild
status: complete
request: "Rebuild Figure 71 through the repo-native scientific figure pipeline and demote the old SVG to historical prototype."
scope: tool
risk: medium
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-scientific-figure-producer
affected_contracts:
  - GCS Scientific Figure Pipeline
  - GCS Warm Evidence Tokens
  - GCS Visual Integrity Gate
affected_paths:
  - tools/architecture_visualization/
  - tests/tools/
  - docs/architecture/70-visualization/assets/
  - docs/architecture/71-step-1-40-execution-report.md
  - docs/architecture/74-scientific-figure-production-paradigm.md
  - docs/architecture/76-ui-design-system-execution-plan.md
  - docs/architecture/82-ui-design-next-work-plan.md
required_evidence:
  - token-lint
  - browser-export-manifest-refresh
  - figure-qa
  - visual-review-png
  - browser-export-tests
  - git-diff-check
human_gate_required: false
human_gate_reason: ""
---

# P4.4 Execution-Map Rebuild

## Scope

Regenerate Figure 71 assets through the repo-native semantic spec, HTML/CSS
compositor, token lint, browser artifact manifest, and figure QA path. Switch
the Step 1-40 report display artifact from the old SVG prototype to the
browser-rendered review PNG.

## Non-Goals

- Do not add graph/chart/Figma/MCP dependencies.
- Do not redesign the Figure 71 content model.
- Do not delete the old SVG prototype.
- Do not change solver/runtime/viewer behavior.

## Context To Read

- `docs/architecture/74-scientific-figure-production-paradigm.md`
- `docs/architecture/84-p4-3-graph-chart-backend-decision.md`
- `tools/architecture_visualization/specs/figure71.yaml`
- `tools/architecture_visualization/browser_export.py`
- `tools/architecture_visualization/figure_qa.py`

## Execution Plan

1. Run token lint before rebuild.
2. Refresh the Figure 71 HTML and review artifacts.
3. Add a manifest-refresh fallback for existing browser artifacts when the
   browser CLI writes files but does not return cleanly.
4. Run Figure 71 QA and visual review the review PNG.
5. Update architecture docs, task archive, roadmap, and process lesson.
6. Commit and push the P4.4 boundary.

## Acceptance Gates

- `figure71-gcs-step-1-40-evidence-map.review.png` is the displayed Procedure
  Figure artifact.
- HTML, manifest, review PNG/PDF, and QA artifacts exist.
- Figure QA passes.
- The old SVG is retained only as historical prototype.
- The browser-export fallback has unit coverage.

## Verification Plan

```bat
python -B tools\ui_qa\gcs_token_lint.py
python -B tools\architecture_visualization\browser_export.py --figure figure71 --formats png,pdf --render-html --reuse-existing-artifacts
python -B tools\architecture_visualization\figure_qa.py --figure figure71
python -m unittest tests.tools.test_browser_export
python -m unittest tests.tools.test_agentic_toolkit
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p4-4-execution-map-rebuild.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-p4-4-execution-map-rebuild\README.md
git diff --check
```

## Evidence Bundle

- Token lint passed.
- Browser-export manifest refresh passed and recorded existing review PNG/PDF.
- Figure QA passed.
- Browser-export fallback tests passed.
- Review PNG was visually inspected in the local app.

## Residual Risks

- Direct browser CLI export timed out in this Windows desktop session after
  writing artifacts; P4.4 added a manifest refresh fallback but did not solve
  every browser-process shutdown behavior.
- The figure is production-pipeline rebuilt, but P5.2/P5.3 still need stronger
  rendered overflow, overlap, and contrast gates.

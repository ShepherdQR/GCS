---
task_id: 2026-05-24-p5-1-token-lint-gate
status: complete
request: "Add the P5.1 token lint gate for UI and scientific-figure visual integrity."
scope: tool
risk: medium
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-scientific-figure-producer
affected_contracts:
  - GCS Warm Evidence Tokens
  - GCS Visual Integrity Gate
  - GCS Scientific Figure Pipeline
affected_paths:
  - tools/ui_qa/
  - tools/architecture_visualization/
  - tools/agentic_design/agentic_toolkit.py
  - tests/tools/
  - docs/architecture/
required_evidence:
  - token-lint-current-repo
  - forced-raw-hex-fixture-fails
  - unknown-token-fixture-fails
  - quality-gate-sequence-test
  - git-diff-check
human_gate_required: false
human_gate_reason: ""
---

# P5.1 Token Lint Gate

## Scope

Implement the smallest repeatable gate that enforces the P2/P3 token rule:
raw `#RRGGBB` values belong only in approved token sources, and code or figure
specs must not reference unknown UI/figure tokens.

## Non-Goals

- Do not introduce a new design-token package or generator.
- Do not install Figma MCP, graph backends, chart backends, Playwright, or
  browser automation dependencies.
- Do not rebuild final Figure 71 assets; P4.4 owns that rebuild.
- Do not change solver, runtime, scene, or viewer ownership semantics.

## Context To Read

- `docs/architecture/75-ui-design-system-conventions.md`
- `docs/architecture/76-ui-design-system-execution-plan.md`
- `docs/architecture/79-ui-token-taxonomy.md`
- `docs/architecture/70-visualization/figure-renderer-token-usage.md`
- `python/gcs_viz/color_scheme.py`
- `tools/architecture_visualization/figure1.theme.json`

## Execution Plan

1. Replace renderer-local raw hex fallback dictionaries with theme loading
   from `figure1.theme.json`.
2. Add `tools/ui_qa/gcs_token_lint.py` to scan UI and figure code for raw hex,
   unknown Python token dictionary references, and unknown figure-spec
   `canonical_token` values.
3. Add unit tests that prove the current repo passes and forced bad fixtures
   fail.
4. Promote the lint and tests into the default agentic quality-gate sequence.
5. Update roadmap and archive docs, then commit this step.

## Acceptance Gates

- The current repo passes `gcs_token_lint.py`.
- A forced raw hex fixture fails.
- A forced unknown `GCS_TOKENS` fixture fails.
- A forced unknown figure-spec `canonical_token` fixture fails.
- Default quality-gate ordering includes the token lint and its tests.

## Verification Plan

```bat
python -B tools\ui_qa\gcs_token_lint.py
python -m unittest tests.tools.test_gcs_token_lint
python -m unittest tests.tools.test_agentic_toolkit
python -m unittest tests.tools.test_showcase_scene_renderer
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p5-1-token-lint-gate.md
git diff --check -- tools/ui_qa tools/architecture_visualization tools/agentic_design tests/tools docs/architecture docs/agentic/tasks docs/completed-tasks
```

## Evidence Bundle

- `python -B tools\ui_qa\gcs_token_lint.py`: passed.
- `python -m unittest tests.tools.test_gcs_token_lint`: passed, including
  forced raw-hex and unknown-token failures.
- `python -m unittest tests.tools.test_agentic_toolkit`: passed after adding
  the new default gate ids.
- Additional renderer and full quality gates are recorded in the completed
  task archive.

## Residual Risks

- The first lint gate is intentionally lexical and AST-based; it does not yet
  inspect rendered pixels, overflow, overlap, or contrast.
- Renderer-specific `COLORS` aliases remain allowed only where they are mapped
  back to `figure1.theme.json`.
- Generated assets are not rebuilt in this step, so P4.4 must still refresh
  final Figure 71 artifacts under the new gate.

---
task_id: 2026-05-24-p5-1-token-lint-gate
status: complete
session_goal: "Close P5.1 by making raw-hex and unknown-token drift fail as a repeatable UI and scientific-figure quality gate."
archive_target: docs/completed-tasks/2026-05-24-p5-1-token-lint-gate/
experience_links:
  - docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p5-1-token-lint-gate-forging-note.md
---

# P5.1 Token Lint Gate

## Task Objective

Make `GCS Warm Evidence Tokens` enforceable before Figure 71 and future
showcase assets are rebuilt. P5.1 turns the design-system rule "no scattered
raw colors and no unknown tokens" into a default quality gate.

## Scope And Non-Goals

In scope:

- replace renderer-local raw hex fallback dictionaries with
  `figure1.theme.json` loading;
- add a standard-library token lint for viewer, figure, and UI QA code;
- test both the current passing repo and forced bad fixtures;
- promote the lint into the default agentic quality-gate sequence;
- update the P5/P4 roadmap and archive the step.

Out of scope:

- installing new design-token, graph, chart, browser, or Figma MCP tooling;
- rebuilding final Figure 71 assets;
- adding overflow, overlap, contrast, or screenshot baseline gates;
- changing solver, runtime, scene, or viewer ownership semantics.

## Interaction Summary

The user asked to continue the UI/scientific-figure roadmap without stopping
after each step, but still follow the established step lifecycle. P5.1 was the
next recommended guardrail after P4.2 browser export smoke. The work therefore
started with a task card, made the lint executable, verified it with forced
failure fixtures, updated roadmap docs, and captured a small process lesson.

## Work Completed

- Added `tools/ui_qa/gcs_token_lint.py`.
- Added `tests/tools/test_gcs_token_lint.py`.
- Added `python.gcs_token_lint` and `python.gcs_token_lint_tests` to the
  default quality-gate command sequence.
- Updated renderer color fallback code to load from
  `tools/architecture_visualization/figure1.theme.json`.
- Added `docs/architecture/70-visualization/token-lint-gate.md`.
- Marked P5.1 complete and moved the next preferred step to P4.3.

## Files And Artifacts

- `tools/ui_qa/gcs_token_lint.py`: raw-hex, Python token-reference, and
  figure-spec token lint.
- `tests/tools/test_gcs_token_lint.py`: current-repo pass and forced-failure
  tests.
- `tools/agentic_design/agentic_toolkit.py`: default quality-gate sequence.
- `tests/tools/test_agentic_toolkit.py`: quality-gate sequence expectations.
- `tools/architecture_visualization/figure71_html_compositor.py`: fallback
  theme seed now comes from `figure1.theme.json`.
- `tools/architecture_visualization/render_gcs_figure1.py`,
  `render_gcs_figure71.py`, and `render_showcase_scene.py`: renderer colors now
  load from the shared figure theme.
- `docs/architecture/70-visualization/token-lint-gate.md`: durable P5.1 rule.
- `docs/architecture/76-ui-design-system-execution-plan.md` and
  `docs/architecture/82-ui-design-next-work-plan.md`: roadmap updates.

## Evidence

```text
python -B tools\ui_qa\gcs_token_lint.py
GCS token lint passed

python -m unittest tests.tools.test_gcs_token_lint
Ran 4 tests in 0.130s
OK

python -m unittest tests.tools.test_agentic_toolkit
Ran 6 tests in 0.105s
OK
```

Additional checks run during closure:

```text
python -m unittest tests.tools.test_showcase_scene_renderer
Passed.

python -m unittest tests.tools.test_gcs_ui_qa
Passed.

python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p5-1-token-lint-gate.md
Passed.

python tools\agentic_design\agentic_toolkit.py run-quality-gates
Passed after the new token lint gates were added.

git diff --check
Passed with only existing CRLF conversion warnings.
```

## Decisions

- Decision: keep P5.1 standard-library only. Rationale: token drift is a
  governance issue and does not require adding dependency risk.
- Decision: allow raw hex only in `color_scheme.py` and `figure1.theme.json`.
  Rationale: these are the current mirrored token sources approved by P2.
- Decision: lint generated assets later. Rationale: P5.1 protects source code
  and specs; P4.4/P5.2/P5.3 own generated-asset rebuild and visual layout QA.
- Decision: move next work to P4.3. Rationale: token drift is now guarded, so
  the graph/chart backend decision can happen before P4.4 rebuild.

## Skipped Checks And Risks

- No requested P5.1 checks were skipped.
- Full visual pixel inspection remains outside P5.1 and is scheduled for later
  overflow, overlap, contrast, and screenshot gates.
- The linter intentionally checks literal token references; dynamically
  composed token names are accepted and should remain covered by ordinary unit
  tests or future rendered QA.

## Follow-Up

- Execute P4.3 as a small dependency-governance decision for graph/chart
  backends.
- Execute P4.4 to rebuild Figure 71 assets under token lint and Figure 71 QA.
- Keep P5.2 focused on rendered text overflow rather than adding more token
  policy.

## Archive Handoff

- Archive path: `docs/completed-tasks/2026-05-24-p5-1-token-lint-gate/`
- Related experience:
  - `docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p5-1-token-lint-gate-forging-note.md`
- Skill, eval, fixture, or tool update needed: P5.2 should add a rendered text
  overflow fixture and fail case.

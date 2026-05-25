---
task_id: 2026-05-25-agentic-pr-governance-nightly-diagnostics
status: complete
session_goal: "Research enterprise agentic PR governance, add GCS PR audit and nightly diagnostics designs, create the nightly automation, and push the work."
archive_target: docs/completed-tasks/2026-05-25-agentic-pr-governance-nightly-diagnostics/
related_design:
  - docs/research/20260525/agentic-pr-governance/README.md
  - docs/agentic/pr-audit-governance.md
  - docs/agentic/nightly-immune-diagnostics.md
---

# Agentic PR Governance And Nightly Diagnostics

## Task Objective

Turn the approved plan into durable GCS governance artifacts: source-aware
research, PR audit design, nightly immune-diagnostics design, a scheduled
Codex automation, validation evidence, and a pushed branch.

## Scope And Non-Goals

In scope:

- research leading public practice around Codex-like coding agents, PR review,
  PR generation, long-running tasks, and enterprise guardrails;
- compare those practices with current GCS agentic governance;
- add a PR audit protocol for exploratory and agent-authored PRs;
- add a nightly immune-diagnostics design and automation;
- archive and validate the task.

Out of scope:

- solver/runtime/IO/viewer behavior changes;
- fixture promotion;
- unattended merge, approval, branch deletion, or force push;
- changing existing unrelated dirty files.

## Interaction Summary

The user approved the earlier plan and asked to proceed through push. The work
started by creating a new task branch, adding a task card, and inventorying
GCS governance documents. External research focused on official OpenAI Codex,
GitHub Copilot, Claude Code, Google Jules, and Microsoft agent-safety sources,
plus empirical papers about agentic PRs and AI code review.

The research was distilled into a main report and eight subtopic reports. The
GCS design layer then received two new governance documents:
`pr-audit-governance.md` and `nightly-immune-diagnostics.md`. A Codex app
automation named `gcs-nightly-immune-diagnostics` was created to run daily at
`02:30 Asia/Shanghai` in worktree mode. The automation prompt forbids
unattended merge, push, approval, branch deletion, fixture promotion,
dependency installation, and network use unless a human explicitly authorizes
the specific action.

## Work Completed

- Created task branch `codex/agentic-pr-governance-nightly`.
- Added task card
  `docs/agentic/tasks/2026-05-25-agentic-pr-governance-nightly-diagnostics.md`.
- Added main research report
  `docs/research/20260525/agentic-pr-governance/README.md`.
- Added eight subtopic reports under
  `docs/research/20260525/agentic-pr-governance/subtopics/`.
- Added `docs/agentic/pr-audit-governance.md`.
- Added `docs/agentic/nightly-immune-diagnostics.md`.
- Updated `docs/agentic/README.md` to index the new governance docs.
- Created Codex automation `gcs-nightly-immune-diagnostics`.
- Added this completed-task archive and completed-task index entry.

## Files And Artifacts

- `docs/agentic/pr-audit-governance.md`: PR classes, risk tiers, automated
  audit output, exploratory PR policy, and review checklist.
- `docs/agentic/nightly-immune-diagnostics.md`: nightly workflow, stage
  contract, output schema, taxonomy, repair boundaries, and installed
  automation metadata.
- `docs/agentic/README.md`: file-map entry for the two new governance docs.
- `docs/agentic/tasks/2026-05-25-agentic-pr-governance-nightly-diagnostics.md`:
  scoped task card and evidence bundle.
- `docs/research/20260525/agentic-pr-governance/README.md`: source-aware
  research synthesis and recommendations.
- `docs/research/20260525/agentic-pr-governance/subtopics/`: detailed
  reports for enterprise workflows, PR review, long-running tasks, security,
  observability, taxonomy, repair loops, and GCS gap analysis.
- Codex automation `gcs-nightly-immune-diagnostics`: daily `02:30
  Asia/Shanghai`, worktree execution.

## Evidence

```text
git switch -c codex/agentic-pr-governance-nightly
Passed after sandbox escalation; branch created.

python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics.md
Initially failed because task-card status used `active` instead of the allowed
`in_progress` value, and because `source-aware-research-report` is not a
project `.codex` skill known to the validator. Fixed both issues; rerun passed.

python tools\agentic_design\agentic_toolkit.py validate-docs
Passed: module design coverage passed.

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics\README.md
Passed.

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics\README.md --min-score 30
Passed with closure score 37/40.

python tools\agentic_design\agentic_toolkit.py run-quality-gates --skip-build --skip-ctest --skip-cli --include-task-cards docs\agentic\tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics.md --include-completed-reports docs\completed-tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics
Passed. The gate included docs, inventory, skills, dependency checks, task-card
include validation, completed-report include validation, and the Python
scene-generation, agentic-toolkit, showcase, browser-export, UI QA,
scene-schema, and history-replay tests. Build, CTest, and CLI were skipped by
scope.
```

## Decisions

- Decision: use English for durable GCS docs.
  Rationale: current GCS architecture and agentic docs are primarily English,
  and this keeps validators, summaries, and future PR templates consistent.

- Decision: create a PR audit document rather than only a research report.
  Rationale: the main local gap was not lack of governance substrate, but lack
  of a review-time PR contract.

- Decision: install the nightly automation in worktree mode.
  Rationale: background diagnostics can write reports without disturbing local
  foreground work.

- Decision: forbid unattended push/merge/approval in the nightly prompt.
  Rationale: vendor and research evidence both support human authority at
  integration points.

- Decision: make the first two nightly runs calibration runs.
  Rationale: signal/noise should be reviewed before allowing even low-risk
  patch candidates outside the run directory.

## Skipped Checks And Risks

- Full build and full CTest were skipped because this task changed docs,
  automation metadata, and governance policy only.
- The scheduled automation has not yet produced its first run artifact.
  Residual risk: its first run may reveal missing local build/test
  prerequisites or overly noisy checks.
- The repository had an unrelated modified file,
  `docs/research/OpusTime/OpusTime.md`, which was not touched or staged by
  this task.
- External vendor docs are current as of 2026-05-25 and may drift; the research
  report records accessed source URLs for later refresh.

## Follow-Up

- Review the first two `gcs-nightly-immune-diagnostics` runs before allowing
  low-risk patches outside the dated run directory.
- Use `docs/agentic/pr-audit-governance.md` manually on this PR and the next
  non-trivial PR before considering a machine-readable audit validator.
- Decide whether GCS should add a top-level `AGENTS.md` for cross-tool PR
  review guidance or keep instructions in `.codex/skills` and `docs/agentic`.
- Define whether nightly run metrics should eventually feed a JSON dashboard.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-25-agentic-pr-governance-nightly-diagnostics/`
- Task card:
  `docs/agentic/tasks/2026-05-25-agentic-pr-governance-nightly-diagnostics.md`
- Research:
  `docs/research/20260525/agentic-pr-governance/README.md`
- Governance docs:
  `docs/agentic/pr-audit-governance.md` and
  `docs/agentic/nightly-immune-diagnostics.md`
- Automation:
  `gcs-nightly-immune-diagnostics`
- Skill, agent, eval, fixture, or tool update needed:
  no immediate skill or tool update; revisit after two nightly calibration
  runs and two manual PR audit uses.

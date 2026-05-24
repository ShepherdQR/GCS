---
task_id: 2026-05-24-e001-executable-closure-tooling
status: complete
request: "Make E001 task-scoped session closure executable through completed-task report generator, validator, and lightweight closure scorer."
scope: tool
risk: medium
owning_agent: gcs-quality-steward
specialist_agents:
  - gcs-architecture-steward
affected_contracts:
  - none
affected_paths:
  - tools/agentic_design/agentic_toolkit.py
  - docs/architecture/65-agentic-implementation-tooling.md
  - docs/agentic/lifecycle-runbook.md
  - docs/agentic/experience/001-task-scoped-session-closure/
  - docs/completed-tasks/
required_evidence:
  - validate-task-card
  - validate-completed-task-report
  - score-closure-report
  - validate-docs
  - validate-inventory
  - validate-skills
  - check-dependencies
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-24-e001-executable-closure-tooling

## Scope

Implement the first executable tooling layer for E001 task-scoped session
closure. The work should add CLI commands to `agentic_toolkit.py` that create,
validate, and lightly score completed-task reports, then update the agentic
docs so future sessions know how to use the new workflow.

Planned commands:

- `new-completed-task-report`: preview or write a completed-task report
  skeleton under `docs/completed-tasks/YYYY-MM-DD-slug/README.md`.
- `validate-completed-task-report`: validate frontmatter, required sections,
  archive target, index link, evidence section, and experience links.
- `score-closure-report`: produce a heuristic closure-quality score aligned
  with E001's rubric.

## Non-Goals

- Do not change solver runtime semantics.
- Do not install the staged E001 candidate skill into `.codex/skills`.
- Do not require legacy completed-task reports to be rewritten in this task.
- Do not make heuristic scoring a substitute for human or agent review.
- Do not touch unrelated dirty files already present in the worktree.

## Context To Read

- `docs/agentic/experience/001-task-scoped-session-closure/README.md`
- `docs/agentic/experience/001-task-scoped-session-closure/research/03-closure-quality-rubric.md`
- `docs/agentic/experience/001-task-scoped-session-closure/templates/task-execution-report.md`
- `docs/completed-tasks/README.md`
- `docs/architecture/65-agentic-implementation-tooling.md`
- `.codex/skills/gcs-quality-steward/SKILL.md`

## Implementation Plan

1. Add completed-task constants and helpers to `tools/agentic_design/agentic_toolkit.py`.
2. Add a completed-task report template function following E001 section names.
3. Add validation over report frontmatter, archive target, required headings,
   placeholder text, index membership, evidence content, and existing
   experience links.
4. Add a lightweight scorer that reports dimension-level scores and total
   score; keep it explicitly heuristic.
5. Wire the three commands into argparse and `main`.
6. Update docs to show the new commands in the agentic lifecycle and tooling
   reference.
7. Archive this implementation task with a completed-task execution report.

## Acceptance Gates

- `new-completed-task-report --help` works.
- `validate-completed-task-report --help` works.
- `score-closure-report --help` works.
- The new validator accepts the completed-task report for this implementation.
- The scorer emits a useful score for the same report.
- Existing agentic design validators still pass.
- Documentation points future agents to the executable closure workflow.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-e001-executable-closure-tooling.md
python tools\agentic_design\agentic_toolkit.py new-completed-task-report --help
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report --help
python tools\agentic_design\agentic_toolkit.py score-closure-report --help
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-e001-executable-closure-tooling\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-24-e001-executable-closure-tooling\README.md --min-score 30
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
git diff --check -- tools\agentic_design docs\agentic docs\architecture\65-agentic-implementation-tooling.md docs\completed-tasks
```

## Evidence Bundle

- Task card validation passed.
- `new-completed-task-report --help` passed.
- `validate-completed-task-report --help` passed.
- `score-closure-report --help` passed.
- New completed-task report validation passed for
  `docs/completed-tasks/2026-05-24-e001-executable-closure-tooling/README.md`.
- Closure score passed the planned threshold with `39/40`.
- `validate-docs`, `validate-inventory`, `validate-skills`, and
  `check-dependencies` passed.
- Detailed evidence is archived in
  `docs/completed-tasks/2026-05-24-e001-executable-closure-tooling/README.md`.

## Residual Risks

- The first scorer will use simple structural heuristics and cannot judge deep
  semantic report quality by itself.
- Legacy completed-task reports may not satisfy the new validator unless they
  are intentionally migrated later.
- A future CI gate should decide whether to validate only new reports or all
  reports under `docs/completed-tasks/`.

# GCS Agentic Operating Layer

## Purpose

This directory is the executable operating layer for the GCS agentic software
engineering workflow. `docs/architecture/68-agentic-se-lifecycle-self-evolution.md`
defines the strategy. This directory defines the templates, runbooks, evidence
formats, and eval rubrics that make the strategy repeatable.

Use this layer for work-process artifacts:

- task cards;
- execution plans;
- evidence bundles;
- experience records;
- eval rubrics;
- lifecycle runbooks.

Keep durable solver architecture in `docs/architecture/`. Keep generated
scenes and mathematical fixtures in `fixtures/` or contract-tool builders.

## File Map

| Path | Purpose |
| --- | --- |
| `task-card-template.md` | Structured intake template for non-trivial tasks. |
| `execution-plan-template.md` | High-risk or multi-step implementation plan template. |
| `evidence-bundle-template.md` | Standard evidence summary for commits and PRs. |
| `trace-schema.md` | Minimal trace schema for agent work and tool calls. |
| `experience-record-template.md` | Learning record for failures, review findings, and repeated friction. |
| `eval-rubric.md` | General scoring rubric for agentic SE work. |
| `pr-audit-governance.md` | PR-class, risk, evidence, exploratory-PR, and automated-audit governance. |
| `nightly-immune-diagnostics.md` | Scheduled worktree diagnostic workflow for scene exploration, defect triage, repair recommendations, and run summaries. |
| `lifecycle-runbook.md` | Action guide for moving from request to push. |
| `task-to-archive-checklist.md` | Compact closure checklist with a checked Step 47 example. |
| `quality-gate-opt-in-policy.md` | S2-01 policy for opt-in task-card and completed-report quality gates. |
| `../research/20260524/ai-agent-git-worktree-workflow-for-gcs.md` | Research-backed policy for multi-session Codex worktree isolation. |
| `next-queue-forward-plan-2026-05-24.md` | Durable handoff for the immediate queue and later agentic-SE plan after Step 49. |
| `experience/001-task-scoped-session-closure/calibration/` | E001 closure-score calibration notes comparing machine scores with human review. |
| `agile-pdca-roadmap.md` | Four-phase Agentic SE execution plan, PDCA cadence, current backlog, and next task. |
| `near-term-agent-plan.md` | Immediate agent execution plan for roadmap sync, seed-agent verification, E001 validation, and opt-in gates. |
| `long-term-agentic-se-plan.md` | Long-term target plan for lifecycle, review, self-evolution, institutional agents, and bounded automations. |
| `evals/module-agent-evals.md` | Seed eval tasks for module agents. |
| `evals/review-rubrics.md` | Independent review rubrics by change type. |
| `tasks/` | Checked-in task cards that are large enough to persist. |
| `experience/` | Folder-per-experience library for promoted agentic-SE lessons, candidate skills, agent role cards, and templates. |
| `institutional-agents/` | Standing role-level agents for recurring project memory, review, timeline, and governance practices; see `institutional-agents/OPERATING-STANDARD.md` for use and creation rules. |

## Minimum Workflow

1. Choose the workspace boundary. Use a dedicated worktree for any parallel
   writing session:

   ```bat
   python tools\agentic_design\agentic_toolkit.py new-worktree-task --slug agentic-tooling --scope tool --risk medium --owner gcs-architecture-steward --base origin/master --request "Add task-card validation" --write
   ```

2. Create a task card for non-trivial single-session work:

   ```bat
   python tools\agentic_design\agentic_toolkit.py new-task-card --slug agentic-tooling --scope tool --risk medium --owner gcs-contract-tools-steward --request "Add task-card validation" --write
   ```

3. Fill the generated scope, evidence, and risk fields, then validate the task
   card:

   ```bat
   python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-agentic-tooling.md
   ```

4. Write an execution plan when risk is high or the task spans modules.
5. Implement in the owning module or support tool boundary.
6. Collect evidence with the standard quality gates.
7. Check `task-to-archive-checklist.md` before closure.
8. Close non-trivial sessions with a task execution report before archive.
9. Record any repeated failure or reusable practice as an experience record
   before changing skills.

## Boundaries

- `docs/agentic` may define workflow, task, evidence, and learning formats.
- `docs/agentic` must not redefine solver contracts, report codes, or module
  ownership. Those belong in `docs/architecture`.
- Agentic tools may inspect and validate the solver, but the solver core must
  not import or depend on agentic infrastructure.
- Experience records are observations. They become rules only after promotion
  into a skill, fixture, test, tool, or architecture document.

# Agentic SE Agile PDCA Roadmap

Snapshot: 2026-05-24.

## Purpose

This roadmap turns the Agentic SE strategy into a staged operating plan. It is
not solver architecture. It governs how GCS uses agents, task cards, evidence,
completed-task archives, quality gates, experience records, and standing
institutional agents to improve the engineering process.

The first four phases are intentionally narrow:

1. fix the task lifecycle loop;
2. make the loop inspectable by quality gates;
3. validate E001 task-scoped session closure through real use;
4. make the first institutional agents verifiable instead of decorative.

## Agile Cadence

Every Agentic SE task uses one PDCA loop:

| Phase | Required action |
| --- | --- |
| Plan | Create or update a task card with scope, risk, owner, evidence, and non-goals. |
| Do | Make the smallest scoped change that can produce durable evidence. |
| Check | Run focused validators and record pass/fail evidence. |
| Act | Update this roadmap, the task card, and any completed-task archive with what changed next. |

One PDCA cycle should usually fit in one commit. Larger work is split into
multiple task cards instead of one large hidden effort.

## Phase 1: Lifecycle Closure

Goal: every non-trivial task can move from request to task card, evidence,
completed-task archive, and follow-up backlog without relying on raw chat
memory.

Definition of done:

- task-card entry criteria are clear;
- completed-task archive entry criteria are clear;
- at least two real tasks are closed through task card plus archive;
- task cards link to completed archives or explicitly explain why no archive
  is needed;
- the runbook tells future agents exactly when to close, learn, and promote.

Backlog:

| ID | Task | Status | Evidence |
| --- | --- | --- | --- |
| S1-01 | Persist four-phase Agile PDCA roadmap and close this planning task. | done | This roadmap, task card, completed-task archive. |
| S1-02 | Apply the lifecycle loop to Step 46 runtime replay export boundary. | next | Step 46 task card, execution plan, completed-task report. |
| S1-03 | Add a lightweight task-to-archive cross-link checklist. | pending | Runbook update and one checked example. |
| S1-04 | Decide which low-risk tasks may stay chat-only. | pending | Entry-criteria table in lifecycle runbook. |
| S1-05 | Review the first two archives with E001 closure rubric. | pending | Scored closure notes or completed-task report updates. |

## Phase 2: Quality-Gate Adoption

Goal: Agentic SE artifacts become checkable without breaking legacy archives or
turning every small edit into ceremony.

Definition of done:

- task-card validation can be run by path or opt-in glob;
- completed-task report validation can be run by path or opt-in glob;
- default quality gate remains affordable;
- high-risk tasks have an explicit gate recommendation;
- legacy archives have a migration policy.

Backlog:

| ID | Task | Status | Evidence |
| --- | --- | --- | --- |
| S2-01 | Design `--include-task-cards` and `--include-completed-reports` quality-gate policy. | pending | Tooling plan and docs update. |
| S2-02 | Add task-card validation tests for valid, missing-field, high-risk-without-gate, and placeholder cases. | pending | `tests/tools/test_agentic_toolkit.py`. |
| S2-03 | Add completed-report validation tests for new reports only. | pending | Tool tests and migration note. |
| S2-04 | Define legacy archive migration or exemption policy. | pending | `docs/completed-tasks/README.md` update. |
| S2-05 | Promote opt-in checks into default gate only after two clean task cycles. | pending | PDCA evidence from Phase 1. |

## Phase 3: E001 Closure Experience Validation

Goal: prove the E001 task-scoped session closure experience by using it on real
GCS work before promoting it into a formal skill or default gate.

Definition of done:

- E001 is used on at least three non-trivial completed tasks;
- at least one false-completion or weak-evidence case is tested;
- the closure scorer/rubric is adjusted based on real misses;
- the promotion decision is recorded: keep as experience, promote to skill, or
  keep provisional.

Backlog:

| ID | Task | Status | Evidence |
| --- | --- | --- | --- |
| S3-01 | Use E001 on Step 46 closure. | pending | Completed-task report and score. |
| S3-02 | Add one negative eval for archive pollution or false completion. | pending | Eval note under E001 or `docs/agentic/evals`. |
| S3-03 | Compare scorer output with human review on two archives. | pending | Calibration note. |
| S3-04 | Decide whether to install a project skill for session closure. | pending | Promotion decision record. |

## Phase 4: Institutional Agents Become Verifiable

Goal: seed institutional agents produce durable, reviewable artifacts and have
small evals that prevent overreach.

Definition of done:

- `刀匠: 淬炼-锻打` has one template, one example, and one eval;
- `裁缝: 裁剪-缝合` has one template, one example, and one eval;
- no additional institutional-agent directories are created before a real use
  case proves need;
- the README states promotion evidence clearly.

Backlog:

| ID | Task | Status | Evidence |
| --- | --- | --- | --- |
| S4-01 | Add `experience-forging-note` template for `刀匠`. | pending | Template and one filled example. |
| S4-02 | Add `timeline-entry` template for `裁缝`. | pending | Template and one filled example. |
| S4-03 | Add eval for refusing unsupported generalization. | pending | Eval seed. |
| S4-04 | Add eval for refusing invented timeline causality. | pending | Eval seed. |
| S4-05 | Reassess candidate institutional agents after three real closures. | pending | Candidate table update. |

## Current PDCA Cycle

### C001: Four-Phase Roadmap Bootstrap

Plan:

- persist the first four Agentic SE phase plans;
- keep this work in `docs/agentic` and completed-task docs only;
- do not touch current uncommitted solver/runtime/toolkit work;
- close the cycle with a task card and completed-task archive.

Do:

- added this roadmap;
- added a task card for the roadmap bootstrap;
- added a completed-task archive for the bootstrap.

Check:

- task-card validation passed;
- docs validation passed;
- inventory, skills, and dependency checks passed;
- completed-task validation passed;
- closure score passed at 38/40.

Act:

- Phase 1 next task is S1-02: apply the lifecycle loop to Step 46 runtime
  replay export boundary.
- Phase 2 remains opt-in until at least two lifecycle closures are complete.
- Phase 3 should consume the Step 46 archive as its next real E001 sample.
- Phase 4 should wait until after Step 46 unless a review reveals an immediate
  need for the `刀匠` or `裁缝` templates.

Retrospective:

- What worked: keeping C001 docs-only avoided mixing with current dirty
  runtime/toolkit files while still proving the task-card to archive loop.
- What to improve: the evidence sections should be written after validators
  run, not left as planned placeholders.
- Adjustment: S1-02 must create the Step 46 task card before touching runtime
  code and must close with both roadmap update and completed-task archive.

## Next Agile Task

S1-02 is the next task:

1. Create a Step 46 task card.
2. Classify it as high risk because it touches runtime history and scene
   history ownership.
3. Require `gcs-session-runtime-steward`, plus IO/viewer handoffs if needed.
4. Execute only after preserving the current dirty worktree state.
5. Close with a completed-task archive and update this roadmap again.

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

## Roadmap Task Inventory

Current task counts:

| Phase | Done | Next | Pending | Main remaining question |
| --- | ---: | ---: | ---: | --- |
| Phase 1: Lifecycle Closure | 4 | 1 | 1 | Do the first lifecycle archives transfer enough context under E001 review? |
| Phase 2: Quality-Gate Adoption | 0 | 0 | 5 | Which checks become opt-in gates before any default enforcement? |
| Phase 3: E001 Closure Experience Validation | 1 | 1 | 2 | Does E001 catch weak closure evidence in real work, not only in templates? |
| Phase 4: Institutional Agents Become Verifiable | 4 | 1 | 0 | Can the seed examples stay evidence-bound as more lifecycle samples arrive? |

Priority order:

1. Finish Phase 1 S1-05 by reviewing the first two lifecycle archives with
   the E001 closure rubric.
2. Use S1-03 checklist evidence to decide how strict future task-card/archive
   validation should become.
3. Add Phase 2 opt-in checks only after the lifecycle loop has two clean
   examples.
4. Keep new institutional-agent examples tied to real requested work.

## Phase Analysis Snapshot

### Phase 1 Analysis

Phase 1 is now proven on documentation work, a real solver-adjacent task, and
a combined engineering/process task. C001 demonstrated the docs-only loop;
C003 demonstrated a high-risk runtime contract change; C004 completed S1-03 by
turning the loop into a compact task-to-archive checklist while also advancing
Step 48.

Stage conclusion:

- Keep Phase 1 active.
- Treat S1-05 as the next consolidation task: review the first lifecycle
  archives against E001 rather than inventing new ceremony.
- Do not start Phase 2 default-gate work until S1-05 clarifies which
  checks are valuable rather than ceremonial.

### Phase 2 Analysis

Phase 2 should remain opt-in. The repository already has validation commands,
but automatic enforcement can become ceremony or break legacy records if it is
enabled too early. The right next move is design and tests for optional gates,
not default enforcement.

Stage conclusion:

- Start with `--include-task-cards` and `--include-completed-reports` design.
- Test only new-format artifacts first.
- Keep legacy archives exempt until a migration decision exists.

### Phase 3 Analysis

E001 is promising and now has a real high-risk engineering sample. Step 47
closed with a completed-task report and scored 37/40. The next risk is not
whether E001 can score a good archive, but whether it can catch weak closure
evidence and guide human review.

Stage conclusion:

- Use the Step 47 archive as the first high-risk E001 sample.
- Add one negative eval for archive pollution or false completion.
- Compare the score with human review notes during S1-05.

### Phase 4 Analysis

Institutional agents are becoming operational. `刀匠` now has an invoke prompt,
template, refusal eval, and a real Step 47 example. `裁缝` has its
prompt/template/eval seed and a real local repository stitch example created
only after explicit timeline work was requested.

Stage conclusion:

- Freeze new institutional-agent creation for now.
- Use the Step 47 `刀匠` artifact as the first real institutional-agent
  example.
- Use the first `裁缝` example as evidence for timeline stitching, but wait for
  more samples before promotion.

## Operating Adjustments

- Evidence is written after validators run; planned evidence is only allowed in
  a task card before work begins.
- A PDCA task is not complete until this roadmap has an Act update.
- High-risk solver tasks must create the task card before touching code.
- Quality-gate adoption must start as opt-in and path-scoped.
- Institutional-agent promotion requires at least one real artifact and one
  eval that can fail.

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
| S1-02 | Reconcile Step 46 lifecycle drift without fabricating a missing task card or archive. | done | `near-term-agent-plan.md` and this roadmap update. |
| S1-03 | Add a lightweight task-to-archive cross-link checklist. | done | `task-to-archive-checklist.md`, runbook update, checked Step 47 example. |
| S1-04 | Decide which low-risk tasks may stay chat-only. | pending | Entry-criteria table in lifecycle runbook. |
| S1-05 | Review the first two archives with E001 closure rubric. | next | Scored closure notes or completed-task report updates. |
| S1-06 | Apply the lifecycle loop to Step 47 deterministic runtime replay evidence export tooling. | done | Task card, implementation evidence, completed-task report, roadmap C003 update, `刀匠` note. |

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
| S3-01 | Use E001 on Step 47 or the next high-risk engineering closure. | done | Step 47 completed-task report and 37/40 closure score. |
| S3-02 | Add one negative eval for archive pollution or false completion. | next | Eval note under E001 or `docs/agentic/evals`. |
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
| S4-01 | Add `experience-forging-note` template for `刀匠`. | done | Template and Step 47 filled example. |
| S4-02 | Add `timeline-entry` template for `裁缝`. | done | Template exists; local repository stitch timeline added after explicit request. |
| S4-03 | Add eval for refusing unsupported generalization. | done | Eval seed. |
| S4-04 | Add eval for refusing invented timeline causality. | done | Eval seed. |
| S4-05 | Reassess candidate institutional agents after three real closures. | next | Candidate table update after additional real closures. |

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

Supersession note: C002 below supersedes the Step 46 next-task assumption.
Step 46 implementation later appeared as completed in the implementation
roadmap, but no matching task card or completed-task archive was found.

Retrospective:

- What worked: keeping C001 docs-only avoided mixing with current dirty
  runtime/toolkit files while still proving the task-card to archive loop.
- What to improve: the evidence sections should be written after validators
  run, not left as planned placeholders.
- Adjustment: S1-02 must create the Step 46 task card before touching runtime
  code and must close with both roadmap update and completed-task archive.

### C002: Step 46 Lifecycle Drift Reconciliation

Plan:

- reconcile the stale PDCA queue with the implementation roadmap;
- do not backfill or invent lifecycle artifacts that were not created;
- choose the next real high-risk task as the lifecycle sample.

Do:

- confirmed that Step 46 is marked done in
  `docs/architecture/66-implementation-execution-roadmap.md` and
  `docs/architecture/67-current-progress-and-next-steps.md`;
- found no matching Step 46 task card or completed-task archive under
  `docs/agentic/tasks/` or `docs/completed-tasks/`;
- added `docs/agentic/near-term-agent-plan.md` to record the drift and next
  actions;
- moved the next lifecycle sample to Step 47 or the next high-risk engineering
  task if Step 47 is deferred.

Check:

- roadmap now records S1-02 as reconciliation, not as an unstarted Step 46
  implementation task;
- Phase 3 no longer depends specifically on a missing Step 46 closure archive;
- Phase 4 still waits for real artifacts before promoting institutional
  agents.

Act:

- S1-06 is now the next Phase 1 lifecycle sample.
- S1-03 and S1-05 should use C001 plus the next real lifecycle sample, not a
  fabricated Step 46 archive.

Supersession note: C003 below completes S1-06 and moves the next Phase 1 task
to S1-03.

### C003: Step 47 Lifecycle Execution

Plan:

- create a high-risk task card before touching runtime code;
- execute Step 47 deterministic runtime replay evidence export;
- preserve the Step 46 split between runtime report evidence and JSON scene
  construction `history`;
- close with implementation evidence, architecture updates, completed-task
  archive, and `刀匠` learning extraction;
- skip `裁缝` because the user explicitly requested not to run it.

Do:

- added `RuntimeReplayEvidenceStage` and `RuntimeReplayEvidenceExport`;
- added `SessionRuntime::export_replay_evidence(ReplayRequest)`;
- added session-runtime contract tests for deterministic export and missing
  command evidence;
- marked Step 47 complete and registered Step 48 as the consumer-path
  follow-up;
- created the Step 47 completed-task archive and `刀匠` forging note.

Check:

- task-card validation passed;
- build passed after sandbox escalation for generated build output access;
- focused `SessionRuntimeContract|ViewerBridgeContract` CTest selection passed
  21/21;
- full CTest passed 113/113;
- CLI smoke on `fixtures\scene\basic\g1.txt` passed;
- `validate-docs`, `validate-inventory`, and `check-dependencies` passed;
- full `run-quality-gates` passed after sandbox escalation;
- completed-task validation passed;
- closure score passed at 37/40.

Act:

- S1-06 is complete.
- S1-03 is now the next Phase 1 task: turn the lifecycle into a lightweight
  task-to-archive checklist.
- S1-05 should review C001 and Step 47 as the first two lifecycle archives.
- S3-02 should add one negative E001 eval for archive pollution or false
  completion.
- Step 48 is the next implementation step for runtime replay evidence
  consumption, not scene-history persistence.

Supersession note: C004 below completes S1-03 and Step 48, then moves the next
institutional consolidation task to S1-05 and the next engineering task to
Step 49.

### C004: Step 48 Replay Consumer And S1-03 Checklist

Plan:

- advance the engineering and institutional lines together;
- expose runtime replay evidence through a public consumer path without
  writing it into JSON scene `history`;
- complete S1-03 as a compact task-to-archive checklist;
- close with implementation evidence, architecture updates, completed-task
  archive, and roadmap updates.

Do:

- added `ReplayEvidenceSummary` and a viewer/report adapter over
  `RuntimeReplayEvidenceExport`;
- added CLI `--replay-evidence`;
- added viewer-bridge contract coverage and a replay-evidence CLI smoke in
  `run-quality-gates`;
- added `docs/agentic/task-to-archive-checklist.md` with a checked Step 47
  example;
- marked Step 48 complete and registered Step 49 as the next replay-evidence
  consumer decision.

Check:

- task-card validation passed;
- Python toolkit unit tests passed;
- build passed after sandbox escalation for generated build output access;
- focused `SessionRuntimeContract|ViewerBridgeContract` CTest selection passed
  22/22;
- full CTest passed 114/114;
- CLI `--replay-evidence` smoke on `fixtures\scene\basic\g1.txt` passed;
- `validate-docs`, `validate-inventory`, and `check-dependencies` passed;
- full `run-quality-gates` passed, including the new replay-evidence CLI gate.

Act:

- S1-03 is complete.
- S1-05 is now the next Phase 1 task: review the first lifecycle archives with
  E001 and the new checklist.
- S3-02 remains the next E001 hardening task.
- Step 49 is the next implementation step for choosing the next runtime replay
  evidence consumer.

## Next Agile Task

S1-05 is the next task:

1. Score C001 and Step 47 with the E001 closure rubric.
2. Compare the scores with human review notes and the S1-03 checklist.
3. Record whether Step 48 should become the second engineering sample for
   future S1-05 calibration.
4. Decide which archive-quality checks are worth turning into opt-in tooling.

## Next PDCA Queue

| Order | Task | Why now | Exit condition |
| --- | --- | --- | --- |
| 1 | S1-05 first archive review | Tests whether E001 closure reports transfer enough context now that S1-03 exists. | Two archive scores plus review note. |
| 2 | Step 49 replay evidence consumer decision | Extends Step 48's consumer path only after choosing the right public surface. | GUI projection, saved report artifact, or diagnostics integration selected with a task card. |
| 3 | S3-02 negative E001 eval | Uses real closure evidence to guard against archive pollution or false completion. | One failing/passing eval note. |
| 4 | S2-01 opt-in gate design | Only after the checklist and archive review clarify useful enforcement. | Gate policy proposal, no default enforcement yet. |
| 5 | S4-05 institutional-agent reassessment | `刀匠` and `裁缝` now each have one real example. | Candidate table update after additional real closures. |

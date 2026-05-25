# Agentic SE Agile PDCA Roadmap

Snapshot: 2026-05-25.

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
| Phase 1: Lifecycle Closure | 6 | 0 | 0 | How often should escaped chat-only work be audited for drift? |
| Phase 2: Quality-Gate Adoption | 0 | 1 | 4 | Which checks become opt-in gates before any default enforcement? |
| Phase 3: E001 Closure Experience Validation | 3 | 1 | 0 | Should E001 remain an experience or become an installed project skill? |
| Phase 4: Institutional Agents Become Verifiable | 4 | 1 | 0 | Can the seed examples stay evidence-bound as more lifecycle samples arrive? |

Priority order:

1. Add Phase 2 opt-in checks now that negative eval and chat-only boundary
   evidence exist.
2. Decide S3-04 after the Step 50 closure sample confirms E001's
   promotion value.
3. Reassess institutional agents now that `Bladesmith` and `Tailor` each have
   real examples.
4. Add Phase 2 implementation tests only after S2-01 keeps legacy archives
   exempt.
5. Keep Step 51 fixture-library gating separate from Agentic SE gates until
   promoted fixture expectations are explicit.

## Phase Analysis Snapshot

### Phase 1 Analysis

Phase 1 is now complete for the first lifecycle pass. C001 demonstrated the
docs-only loop; C003 demonstrated a high-risk runtime contract change; C004
completed S1-03 by turning the loop into a compact task-to-archive checklist
while also advancing Step 48. C005 completed S1-05 by reviewing the first two
lifecycle archives against E001 while advancing Step 49. C007 completed S1-04
by defining the low-risk chat-only boundary.

Stage conclusion:

- Treat Phase 1 as complete for the first operating loop.
- Audit future chat-only escapes if they start hiding decisions, skipped
  checks, or generated artifacts.
- Phase 2 can now start opt-in gate design, but default enforcement should
  remain deferred.

### Phase 2 Analysis

Phase 2 should now start with opt-in design. The repository already has
validation commands, but automatic enforcement can become ceremony or break
legacy records if it is enabled too early. The right next move is S2-01 gate
policy design, not default enforcement.

Stage conclusion:

- Start with `--include-task-cards` and `--include-completed-reports` design.
- Test only new-format artifacts first.
- Keep legacy archives exempt until a migration decision exists.

### Phase 3 Analysis

E001 is promising and now has multiple real closure samples plus a first
calibration note. C001 scored 38/40 and Step 47 scored 37/40 under S1-05; S3-02
added a negative eval, and Step 50 added another compact workflow-decision
closure sample. The next risk is promotion timing: E001 should become a skill
only if the boundary remains useful without forcing tiny work into archive
pollution.

Stage conclusion:

- Use the S1-05 calibration note as the first human-review comparison sample.
- Treat S3-02 as complete: E001 now has a seed negative eval for false
  completion and archive pollution.
- S3-04 is ready after S2-01 frames how promotion would interact with optional
  gates and the low-risk chat-only boundary.

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
| S1-04 | Decide which low-risk tasks may stay chat-only. | done | Step 1.5 entry-criteria table in `lifecycle-runbook.md`. |
| S1-05 | Review the first two archives with E001 closure rubric. | done | `experience/001-task-scoped-session-closure/calibration/2026-05-24-s1-05-first-archive-review.md`. |
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
| S2-01 | Design `--include-task-cards` and `--include-completed-reports` quality-gate policy. | next | Tooling plan and docs update. |
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
| S3-02 | Add one negative eval for archive pollution or false completion. | done | `experience/001-task-scoped-session-closure/evals/2026-05-25-false-completion-archive-pollution.md`. |
| S3-03 | Compare scorer output with human review on two archives. | done | S1-05 calibration note. |
| S3-04 | Decide whether to install a project skill for session closure. | next | Promotion decision record after S1-04. |

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
- At C004 close, Step 49 became the implementation step for choosing the next
  runtime replay evidence consumer.

Supersession note: C005 below completes S1-05 and Step 49, then moves the
institutional queue to S3-02/S1-04 and the engineering queue to Step 50.

### C005: S1-05 Archive Review And Step 49 Saved Report Artifact

Plan:

- complete S1-05 by scoring and reviewing the first two lifecycle archives;
- choose the Step 49 replay evidence consumer direction;
- implement the smallest public saved-report artifact path without changing
  JSON scene `history`;
- include the previously untracked `docs/research/OpusTime` materials in the
  commit, as explicitly requested.

Do:

- scored C001 at 38/40 and Step 47 at 37/40 with the E001 closure scorer;
- recorded a S1-05 calibration note under the E001 experience;
- added `ReplayEvidenceReportArtifact` and deterministic JSON report artifact
  formatting in `viewer_bridge`;
- added `GCS.exe --save-replay-evidence <path>`;
- added viewer-bridge contract coverage and default quality-gate CLI coverage
  for the saved report artifact;
- marked Step 49 complete and registered Step 50 as the next replay evidence
  report workflow review.

Check:

- C001 and Step 47 completed-task reports validated;
- task-card validation passed;
- Python toolkit unit tests passed;
- build passed after sandbox escalation for generated build output access;
- focused `SessionRuntimeContract|ViewerBridgeContract` CTest selection passed
  23/23;
- CLI `--save-replay-evidence` smoke wrote a deterministic report artifact.
- full CTest passed 115/115;
- full `run-quality-gates` passed, including
  `cli.replay_evidence_report_artifact`;
- completed-task validation passed;
- closure score passed at 37/40.

Act:

- S1-05 is complete.
- S1-04 is now the remaining Phase 1 lifecycle-boundary task.
- S3-02 is now the next E001 hardening task.
- At C005 close, Step 50 became the engineering task for deciding whether
  saved replay evidence reports should feed GUI review, diagnostics packaging,
  or remain CLI/report artifacts. C008 below supersedes this queue position.

### C006: S3-02 Negative E001 Eval

Plan:

- add one E001 negative eval for false completion and archive pollution;
- keep it documentation-level until Phase 2 opt-in gates decide enforcement;
- update the roadmap and archive the task through the lifecycle.

Do:

- added a seed eval with a positive control, false-completion negative case,
  archive-pollution negative case, expected decisions, and minimal repairs;
- added a Bladesmith forging note for the reusable lesson;
- updated the E001 README and completed-task index.

Check:

- task-card validation passed;
- completed-task validation passed;
- closure score passed;
- docs validation passed.

Act:

- S3-02 is complete.
- S1-04 is now the next Agentic SE lifecycle task because the negative eval
  must not over-reject tiny low-risk work.
- S3-04 should wait until S1-04 clarifies the chat-only boundary.

### C007: S1-04 Low-Risk Chat-Only Boundary

Plan:

- define which low-risk work can stay chat-only, commit-note-only, or must use
  persisted task/archive closure;
- update the checklist so S3-02's negative eval does not over-reject tiny work;
- close Phase 1's first lifecycle pass.

Do:

- added Step 1.5 to the lifecycle runbook with a three-tier boundary table;
- added escalation triggers for generated artifacts, fixtures, branch cleanup,
  quality gates, lifecycle policy, public behavior, and future task context;
- updated the task-to-archive checklist and completed-task index;
- added a Bladesmith note for the reusable escape-hatch lesson.

Check:

- task-card validation passed;
- completed-task validation passed;
- closure score passed;
- docs validation passed.

Act:

- Phase 1 is complete for the initial Agentic SE lifecycle loop.
- At C007 close, Step 50 became the next engineering task. C008 below
  completes it and moves the queue forward.
- S2-01 is now unblocked for opt-in gate design because S3-02 and S1-04 define
  both the reject cases and the low-risk escape hatch.

### C008: Step 50 Replay Evidence Workflow Review

Plan:

- inspect the saved replay evidence report artifact in a real review workflow;
- decide whether the report should feed GUI review, diagnostics packaging, or
  remain a CLI/report artifact;
- update architecture and Agentic SE roadmaps, then close the cycle with a
  task card, archive, and Bladesmith note.

Do:

- generated a saved report from `fixtures/scene/basic/g1.txt`;
- confirmed the report schema, runtime transaction artifact kind,
  report-evidence flag, scene-history exclusion, ordered stages, and commit
  version transition;
- chose report-only consumption for now;
- registered Step 51 for promoted fixture-library gating.

Check:

- CLI saved-report review smoke passed;
- task-card validation passed;
- completed-task validation passed;
- closure score passed;
- docs validation passed.

Act:

- Step 50 is complete.
- S2-01 becomes the next Agentic SE tooling design task.
- Step 51 becomes the next GCS implementation candidate after promoted scene
  fixture expectations are made explicit.

## Next Agile Task

S2-01 is the next Agentic SE tooling design task, with Step 51 as the next GCS
implementation candidate:

1. Design Phase 2 quality gates as opt-in now that negative eval evidence
   exists.
2. Decide S3-04 after S2-01 clarifies optional gate boundaries.
3. Reassess institutional agents after the latest real closure samples.
4. Execute Step 51 only after promoted fixture expected outcomes are explicit.

## Next PDCA Queue

| Order | Task | Why now | Exit condition |
| --- | --- | --- | --- |
| 1 | S2-01 opt-in gate design | Negative eval, chat-only boundary, and Step 50 closure sample now clarify useful enforcement. | Gate policy proposal, no default enforcement yet. |
| 2 | S3-04 E001 promotion decision | E001 now has positive, negative, and compact workflow-decision samples. | Keep as experience, promote to skill, or keep provisional. |
| 3 | S4-05 institutional-agent reassessment | Bladesmith and Tailor now each have multiple real examples. | Candidate table update after additional real closures. |
| 4 | Step 51 promoted fixture-library gate | Promoted scene fixtures need repeatable expected-outcome evidence. | Focused fixture gate selected or implemented without broad default expansion. |

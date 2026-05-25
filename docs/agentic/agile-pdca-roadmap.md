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
| Phase 2: Quality-Gate Adoption | 3 | 1 | 1 | What legacy archive migration or exemption policy is acceptable? |
| Phase 3: E001 Closure Experience Validation | 4 | 0 | 0 | How soon should E001 checks move from skill guidance into optional or default gates? |
| Phase 4: Institutional Agents Become Verifiable | 6 | 0 | 0 | When should I003/I004 be rerun on live rendered artifacts before promotion? |

Priority order:

1. Define S2-04 legacy archive migration or exemption policy before any
   default artifact validation.
2. Run at least two clean opt-in artifact-gate cycles before S2-05 considers
   default enforcement.
3. Choose the next implementation candidate after the parallel item 4 session
   lands.
4. Rerun I003/I004 on a live rendered UI or figure artifact before promoting
   either visual role beyond seed.

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

Phase 2 has moved from opt-in design into executable gates. S2-01 kept
default enforcement deferred; S2-02 implemented task-card include behavior and
tests; S2-03 implemented completed-report include behavior for explicitly
selected new reports. Default `run-quality-gates` still does not bulk-scan
legacy Agentic artifacts.

Stage conclusion:

- S2-01 through S2-03 are complete.
- `--include-task-cards` and `--include-completed-reports` are opt-in and
  path-scoped.
- S2-04 is now the next Phase 2 task: define legacy archive migration or
  exemption policy.
- Keep E001 closure scoring out of the completed-report gate until S2-05
  decides whether that promotion is justified.

### Phase 3 Analysis

E001 has completed its first validation pass. C001 scored 38/40 and Step 47
scored 37/40 under S1-05; S3-02 added a negative eval; S1-04 added the
low-risk escape hatch; S2-01 kept gates opt-in; and S3-04 promoted E001 into
the active project skill `.codex/skills/task-scoped-session-closer`.

Stage conclusion:

- Use the S1-05 calibration note as the first human-review comparison sample.
- Treat S3-02 as complete: E001 now has a seed negative eval for false
  completion and archive pollution.
- Keep E001 as an active skill, not a default quality gate.
- Let S2-02 through S2-05 decide if any E001 checks become opt-in or default
  gates.

### Phase 4 Analysis

Institutional agents completed their first reassessment. `刀匠` and `裁缝`
now have invoke prompts, templates, refusal evals, and multiple real examples,
so S4-05 upgrades them to practiced promoted seed roles. Atelier Steward and
Art Director now have conservative seed prompt/template/eval/example packages
from a real Figure 72 visual-governance artifact request, but they remain seed
roles.

Stage conclusion:

- Freeze new institutional-agent creation for now.
- Treat Bladesmith and Tailor as practiced promoted seed roles.
- Keep Atelier Steward and Art Director at seed until a live rendered visual
  review produces stronger evidence.

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
| S2-01 | Design `--include-task-cards` and `--include-completed-reports` quality-gate policy. | done | `quality-gate-opt-in-policy.md` and CI gate docs update. |
| S2-02 | Add task-card validation tests for valid, missing-field, high-risk-without-gate, and placeholder cases. | done | `tests/tools/test_agentic_toolkit.py`, `agentic.task-cards`. |
| S2-03 | Add completed-report validation tests for new reports only. | done | `tests/tools/test_agentic_toolkit.py`, `agentic.completed-task-reports`. |
| S2-04 | Define legacy archive migration or exemption policy. | next | `docs/completed-tasks/README.md` update. |
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
| S3-04 | Decide whether to install a project skill for session closure. | done | `.codex/skills/task-scoped-session-closer` and E001 promotion decision record. |

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
| S4-05 | Reassess candidate institutional agents after three real closures. | done | `institutional-agents/2026-05-25-s4-05-reassessment.md`. |
| S4-06 | Add I003/I004 visual seed packages from a real visual-governance artifact request. | done | I003/I004 prompts, templates, evals, and Figure 72 seed examples. |

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
- At C006 close, S3-04 still needed the S1-04 chat-only boundary before a
  promotion decision. C010 below completes that decision.

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
- At C008 close, S2-01 became the next Agentic SE tooling design task. C009
  below completes it and moves Phase 2 forward.
- Step 51 becomes the next GCS implementation candidate after promoted scene
  fixture expectations are made explicit.

### C009: S2-01 Opt-In Gate Policy

Plan:

- design but do not implement `--include-task-cards` and
  `--include-completed-reports`;
- keep default quality gates free of bulk legacy archive validation;
- update quality-gate docs, roadmap, archive, and Bladesmith note.

Do:

- added `docs/agentic/quality-gate-opt-in-policy.md`;
- proposed pathspec-based flags and future gate IDs;
- defined unmatched pathspec failure and legacy exemption behavior;
- recorded S2-02 through S2-05 implementation order.

Check:

- task-card validation passed;
- completed-task validation passed;
- closure score passed;
- docs validation passed.

Act:

- S2-01 is complete.
- S2-02 is the next Phase 2 implementation task.
- S3-04 can now use the opt-in policy boundary when deciding E001 promotion.

### C010: S3-04 E001 Skill Promotion Decision

Plan:

- decide whether E001 should remain an experience, become an active project
  skill, or stay provisional;
- keep default quality-gate enforcement out of scope;
- record promotion evidence, boundaries, and follow-up.

Do:

- promoted E001 into `.codex/skills/task-scoped-session-closer`;
- added an active skill UI metadata file;
- added a promotion decision record under E001;
- updated the experience index, roadmap, near-term plan, task card, archive,
  and completed-task index.

Check:

- skill quick validation was blocked by missing PyYAML in local Python
  runtimes, and a standard-library skill structure check passed;
- task-card validation passed;
- completed-task validation passed;
- closure score passed;
- docs validation passed.

Act:

- S3-04 is complete.
- At C010 close, S4-05 became the institutional-agent decision task. C011
  below completes it and moves the queue forward.
- S2-02 remains the next Phase 2 implementation task.

### C011: S4-05 Institutional-Agent Reassessment

Plan:

- reassess Bladesmith, Tailor, Atelier Steward, Art Director, and candidate
  roles after multiple real closures;
- update status without creating new standing-agent directories;
- close Phase 4's first verification pass.

Do:

- added `docs/agentic/institutional-agents/2026-05-25-s4-05-reassessment.md`;
- upgraded Bladesmith and Tailor to practiced promoted seed roles;
- kept Atelier Steward and Art Director as seed roles pending real visual
  review artifacts;
- kept candidate roles in the candidate table.

Check:

- task-card validation passed;
- completed-task validation passed;
- closure score passed;
- docs validation passed.

Act:

- Phase 4 is complete for the first verification pass.
- S2-02 is now the next Agentic SE implementation task.
- Step 51 remains the next GCS implementation candidate.

### C012: Agentic SE Roadmap Items 1, 2, 3, And 5

Plan:

- execute S2-02, S2-03, Step 51, and I003/I004 seed-package integration;
- leave roadmap item 4 to the parallel conversation;
- keep default quality gates stable while adding explicit opt-in selections;
- close with task card, completed-task archive, roadmap update, and
  Bladesmith lesson.

Do:

- added `--include-task-cards` and `validate-task-card-includes`;
- added `--include-completed-reports` and
  `validate-completed-report-includes`;
- added `tools/scene_generation/fixture_library_gate.py`;
- added `run-quality-gates --include-fixture-library`;
- integrated I003/I004 prompt, template, eval, and Figure 72 seed examples
  from the parallel agent while preserving seed status.

Check:

- `python -m unittest tests.tools.test_agentic_toolkit` passed 12 tests;
- `python -m unittest tests.tools.test_fixture_library_gate` passed 3 tests;
- `python tools\scene_generation\fixture_library_gate.py --gcs-exe out\build\clang-ninja\GCS.exe`
  passed for 3 promoted scenes;
- opt-in task-card and completed-report gates passed on this task's artifacts;
- completed-task validation, closure score, and docs validation passed.

Act:

- S2-02 and S2-03 are complete.
- Step 51 is complete and remains opt-in.
- S4-06 is complete, but I003/I004 stay seed until a live rendered visual
  artifact is reviewed.
- S2-04 is the next Agentic SE task.
- The next solver implementation candidate should be chosen after the
  parallel item 4 session lands.

## Next Agile Task

S2-04 is now the next Agentic SE implementation task. The next GCS
implementation candidate should be chosen after the parallel item 4 session
lands:

1. Define legacy archive migration or exemption policy.
2. Run two clean opt-in artifact-gate cycles before considering S2-05.
3. Keep E001 closure scoring out of default gates until S2-05.
4. Rerun I003/I004 on live rendered visual evidence before promotion.

## Next PDCA Queue

| Order | Task | Why now | Exit condition |
| --- | --- | --- | --- |
| 1 | S2-04 legacy archive policy | S2-02/S2-03 are executable, but default enforcement needs an exemption story. | Completed-task index or policy note defines legacy migration/exemption. |
| 2 | Two opt-in gate cycles | S2-05 needs evidence before any default promotion. | Two completed task archives cite successful include-gate evidence. |
| 3 | Parallel item 4 integration review | Another session owns item 4; this roadmap should not overwrite it. | Review and merge that session's artifacts when available. |
| 4 | I003/I004 rendered-artifact review | Seed packages exist, but live visual evidence is still needed. | Atelier and Art Director reports against rendered HTML/PNG/PDF. |

# Experience Forging Note: S2-04/S2-05 Agentic Gate Policy

Date: 2026-05-25

Role: `Bladesmith: Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-25-s2-04-legacy-artifact-policy` and
  `2026-05-25-s2-05-agentic-default-gate-decision`
- Time range: 2026-05-25
- Source artifacts:
  - `docs/agentic/legacy-artifact-policy.md`
  - `docs/agentic/default-agentic-gate-decision.md`
  - `docs/agentic/quality-gate-opt-in-policy.md`
  - `docs/completed-tasks/README.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | Two post-policy task cycles passed explicit task-card and completed-report include gates. |
| Decisions | Keep broad default Agentic artifact validation off; retain completed reports and closure score as opt-in closeout checks. |
| Preferences | Prefer current-task evidence over filesystem-wide archive discovery. |
| Hypotheses | A future current-task artifact declaration may make task-card validation safe as a default for non-trivial work. |
| Open questions | What exact command shape should declare current task artifacts if the workflow later needs less manual include syntax? |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Separate current artifacts from historical memory. | Validators become executable after years of mixed-format docs. | Label old artifacts and migrate only when new work depends on them. | Do not sweep the whole archive tree just to make a gate green. | `legacy-artifact-policy.md` | Applies to Agentic artifacts, not solver contract tests. |
| Count only post-policy opt-in cycles for default decisions. | A pre-policy gate run proves mechanics but not governance. | Treat earlier runs as rehearsal and count only cycles after the policy exists. | Do not overstate evidence from one session. | S2-04 and S2-05 cycles | Future policy changes may reset the count. |
| Default gates need explicit current-task declarations. | A gate cannot infer intent from the whole filesystem. | Keep default broad-scan-free until task artifacts are declared. | Do not pick up parallel-session or legacy files. | S2-05 decision | Does not prevent explicit include gates. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| Two clean cycles justify scanning all historical task cards and archives. | The cycles only prove explicit current-artifact selection. | Separate migration task and exemption table. |
| Completed-report validation should run before every build/test gate. | Reports are created at closeout, not at the start of implementation. | Closeout-specific profile with clear timing. |
| Closure score should be a hard CI failure now. | The score is heuristic and needs examples of acceptable low scores and bad high-structure archives. | Calibrated threshold and override policy. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale: Future tasks should explicitly decide whether they are current,
migrated, legacy-exempt, low-risk no-archive, or parallel-session pending
before using Agentic artifact gates as evidence.

## Follow-Up

- Consider a future current-task artifact declaration only after another
  non-documentation workflow shows the manual include syntax is too costly.
- Keep completed-report validation and closure score in closeout, not in the
  general default pre-build gate.

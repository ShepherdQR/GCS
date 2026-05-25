# Experience Forging Note: S2-01 Opt-In Gate Policy

Date: 2026-05-25

Role: `Bladesmith: Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-25-s2-01-opt-in-gate-policy`
- Time range: 2026-05-25
- Source artifacts:
  - `docs/agentic/quality-gate-opt-in-policy.md`
  - `docs/architecture/69-ci-ready-quality-gates.md`
  - `docs/agentic/agile-pdca-roadmap.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | Task-card and completed-report validators already exist, but `run-quality-gates` does not include path-scoped artifact validation flags. |
| Decisions | Design opt-in include flags before default enforcement. |
| Preferences | Keep high-risk lifecycle work checkable while preserving S1-04's low-risk escape hatch. |
| Hypotheses | Pathspec-based gates will catch active artifact mistakes without forcing legacy migration. |
| Open questions | Whether closure scoring should become an optional completed-report gate after S2-03. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Make lifecycle gates opt-in before default. | Validators exist but legacy artifacts predate current rules. | Add explicit include policy first. | Do not validate the whole archive tree before migration policy exists. | S2-01 policy doc | Applies to Agentic SE artifacts, not solver correctness gates. |
| Unmatched include paths must fail. | A user asks a gate to check a specific artifact. | Treat no-match as a failed gate. | Do not let typos create false confidence. | Policy pathspec rules | Implementation still belongs to S2-02/S2-03. |
| Scoring is not the same as validation. | Completed-task reports can validate structurally and still vary in quality. | Keep score promotion separate until thresholds are calibrated. | Do not make E001 a default blocker too early. | S2-01 completed-report gate decision | S3-04 owns promotion decision. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| All task cards and archives should be default-gated immediately. | Legacy records and low-risk chat-only work would create noise before migration policy exists. | Two clean opt-in cycles and S2-04 legacy policy. |
| Completed-report gates should always enforce closure score. | Scoring is useful but still a heuristic and may need calibration. | S2-03/S2-05 tests and promotion decision. |
| Design-only gate work can skip closure. | The task changes future quality-gate policy and roadmap priorities. | None; archive is appropriate. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale: The lesson should shape future gate implementation checklists. It
does not require a new agent or skill.

## Follow-Up

- Implement S2-02 with unit tests before wiring task-card includes.
- Keep S2-03 completed-report behavior limited to explicit new reports.

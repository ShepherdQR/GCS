# Experience Forging Note: Agentic SE Roadmap Items 1, 2, 3, And 5

Date: 2026-05-25

Role: `Bladesmith: Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-25-agentic-se-roadmap-items-1-2-3-5`
- Time range: 2026-05-25
- Source artifacts:
  - `tools/agentic_design/agentic_toolkit.py`
  - `tools/scene_generation/fixture_library_gate.py`
  - `docs/agentic/agile-pdca-roadmap.md`
  - `docs/agentic/institutional-agents/003-atelier-steward-calibrate-review/`
  - `docs/agentic/institutional-agents/004-art-director-frame-judge/`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | Opt-in task-card and completed-report gates now exist; Step 51 fixture-library gate passes for 3 promoted scenes. |
| Decisions | Keep artifact gates and fixture-library gate opt-in until legacy/default promotion evidence exists. |
| Preferences | Parallel agent output can be integrated when scoped to non-overlapping directories. |
| Hypotheses | Two clean opt-in cycles are enough evidence before S2-05 considers default enforcement. |
| Open questions | What exact S2-04 legacy exemption shape should protect useful older archives without hiding new failures? |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Implement gate include behavior with explicit pathspec failure. | A validator becomes selectable from a broader gate command. | Add helper-level tests for valid, invalid, and unmatched pathspecs. | Do not silently pass missing includes. | `tests/tools/test_agentic_toolkit.py` | Applies to task-card and completed-report artifacts. |
| Keep focused engineering gates opt-in before default expansion. | Promoted fixtures become durable evidence but may be expensive or semantically narrow. | Add an explicit selection flag first. | Do not widen default gates until stability is proven. | `--include-fixture-library` | Applies to Step 51 fixture-library gate. |
| Parallel agent output needs a strict merge boundary. | A subagent edits institutional-agent packages while the main session edits tooling. | Constrain paths up front and integrate after focused validation. | Do not let the subagent edit roadmap/index/tool files. | I003/I004 artifact package | Applies when parallel tasks have separable ownership. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| Completed-report include gates should enforce closure score now. | S2-03 only proved structural include validation; scoring remains heuristic. | S2-05 calibration after two clean opt-in cycles. |
| Step 51 should enter the default gate immediately. | It is useful, but explicit fixture-library selection is enough until repeated runs prove stability. | More CI/local run evidence. |
| I003/I004 are practiced roles after one seed example. | A single Figure 72 seed review is not enough for promotion. | Rendered HTML/PNG/PDF review with repeated use. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale: The main reusable lesson is procedural: add opt-in gates with
negative pathspec tests before default enforcement, and constrain parallel
agent scopes before merging.

## Follow-Up

- Define S2-04 legacy archive migration or exemption policy.
- Collect two clean opt-in artifact-gate cycles before S2-05.
- Rerun I003/I004 on live rendered visual artifacts before promotion.

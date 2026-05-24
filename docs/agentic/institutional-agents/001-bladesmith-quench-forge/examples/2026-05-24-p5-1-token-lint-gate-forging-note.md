# Experience Forging Note: P5.1 Token Lint Gate

Date: 2026-05-24

Role: `Bladesmith Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-24-p5-1-token-lint-gate`
- Time range: P5.1 token lint implementation and closure
- Source artifacts:
  - `docs/agentic/tasks/2026-05-24-p5-1-token-lint-gate.md`
  - `tools/ui_qa/gcs_token_lint.py`
  - `tests/tools/test_gcs_token_lint.py`
  - `docs/architecture/70-visualization/token-lint-gate.md`
  - `docs/completed-tasks/2026-05-24-p5-1-token-lint-gate/README.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | Renderer fallback dictionaries had repeated raw hex values; after theme loading, default lint passes. |
| Decisions | Approved raw hex sources remain `color_scheme.py` and `figure1.theme.json`; broader visual QA stays in later P5 steps. |
| Preferences | Prefer small repo-native gates before adding design-surface or renderer dependencies. |
| Hypotheses | Token lint will make P4.4 rebuild safer by catching color drift before generated artifacts are refreshed. |
| Open questions | How much generated asset lint belongs in P4.4 versus P5.2/P5.3 visual layout checks. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Convert taste rules into failing fixtures. | A design-system rule becomes durable enough to govern future work. | Add one passing-current-repo test and one or more forced-failure fixtures. | Do not rely on prose-only aesthetic policy for repeated implementation work. | `tests/tools/test_gcs_token_lint.py` fails forced raw hex and unknown token examples. | Applies to mechanically detectable rules, not subjective art-direction calls. |
| Keep token lint narrower than visual QA. | A source-level gate is added before pixel/layout gates exist. | Check token sources, literal token references, and spec token names only. | Do not claim overflow, overlap, contrast, or screenshot quality from a lexical lint. | P5.1 docs explicitly hand off rendered checks to P5.2-P5.4. | Ends where browser rendering, font metrics, or canvas pixels are required. |
| Refactor duplicate fallback colors before enforcing lint. | Existing source code violates a new design rule through historical fallbacks. | Move duplicate raw values back to the approved token source before turning on the gate. | Do not add broad exemptions for convenience. | Figure renderers now load `figure1.theme.json` instead of local raw hex dictionaries. | Applies when the fallback source is deterministic and already versioned. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| "Token lint means the figure is visually excellent." | Token lint only proves token discipline; it cannot see text overflow, hierarchy, or overlap. | P5.2/P5.3/P5.4 rendered QA results. |
| "All Markdown docs should fail raw hex." | Taste guides and token taxonomy docs need to document token values directly. | A separate docs-aware policy if raw examples start drifting. |
| "Install a token package now." | The current rule is simple enough for standard-library AST and regex checks. | New cross-language generation requirements or package-backed design-token export. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale:

Future design-system steps should pair every enforceable aesthetic rule with a
forced-failure fixture and explicitly state what remains subjective or
rendering-dependent.

## Follow-Up

- Reuse this pattern for P5.2 overflow and P5.3 overlap/contrast fixtures.
- Revisit generated-asset scanning after P4.4 rebuild establishes the final
  artifact set.

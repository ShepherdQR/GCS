# Experience Forging Note: E-GOV-001 and E-GOV-003 Validator Candidates

Date: 2026-05-30

Role: `Bladesmith: Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-30-strengthen-09-institutional-agents-learning`
- Time range: 2026-05-30
- Source artifacts:
  - `tools/governance/check_staged_scope.py` (enhanced with YAML frontmatter parsing, SKIP semantics, false-positive docs)
  - `tools/governance/check_completion_evidence.py` (new — checks 4 evidence categories)
  - `tests/tools/test_check_staged_scope.py` (23 tests)
  - `tests/tools/test_check_completion_evidence.py` (22 tests)
  - `docs/agentic/evals/governance/e-gov-001-refuse-unrelated-dirty-file-staging.md`
  - `docs/agentic/evals/governance/README.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | E-GOV-001 tool already existed but couldn't parse YAML frontmatter task cards. E-GOV-003 didn't exist at all. Both now have executable validators with tests. |
| Decisions | Promote both evals from L2 (prompt-level) to L3 (validator candidate). Keep both advisory — not default gates. |
| Preferences | Follow E-GOV-001's existing design (argparse, JSON mode, human-readable output). |
| Hypotheses | A future session could wire these into agentic_toolkit.py as `validate-staged-scope` and `validate-completion-evidence` subcommands. |
| Open questions | When should these graduate from L3 (validator candidate) to L4 (default gate)? At least 2 clean opt-in cycles with low false-positive rate are needed. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| YAML frontmatter is the task card convention; tools must parse it. | E-GOV-001's heading-based parser missed real task card affected_paths. | Added `_parse_yaml_frontmatter_paths()` as primary strategy. | Keep heading-based fallback for ad-hoc task docs. | 23 passing tests including YAML frontmatter cases. | Applies to all tools that read task cards. |
| Completed-task evidence categories are checkable mechanically. | Night-watch found 86 archives with only README.md — thin but not necessarily wrong. | Built E-GOV-003 with 4 evidence category detectors: task card link, changed files, evidence artifacts, gate decision. | Do not penalize missing build evidence when Skipped Checks is explained. | 81/87 reports PASS; 6 FAIL are legitimate older-format reports. | Does not validate evidence quality, only presence. |
| Validators need SKIP as a first-class exit code. | E-GOV-001 returned code 1 (FAIL) when no task card existed — misleading. | Added `skipped` field and exit code 2 for both tools. | SKIP is not PASS; caller should distinguish "nothing to check" from "checked and clean." | Tests cover SKIP for missing files, non-task paths, and empty reports. | SKIP ≠ exemption — it means the tool cannot form an opinion. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| Make E-GOV-001 a default pre-commit hook. | False positives for shared-infrastructure files (CMakeLists.txt, scripts/) need documented escape hatches first. | At least 5 real sessions of opt-in use with tracked false-positive rate. |
| Make E-GOV-003 a default gate on all archives. | 6/87 legacy reports fail; migration policy (S2-04) must define exemption window before default enforcement. | Two clean opt-in cycles with explicit include paths. |

## Recommended Promotion

Choose one:

- update governance eval roadmap (promote E-GOV-001 and E-GOV-003 from L2 to L3).

Rationale: Both evals now have executable validators with passing tests. They
are at L3 (validator candidate) but remain advisory — not L4 (default gate).
The governance eval roadmap should reflect this.

## Follow-Up

- Update `docs/agentic/governance-eval-roadmap.md` to mark E-GOV-001 and E-GOV-003 as L3.
- Add `validate-staged-scope` and `validate-completion-evidence` as future `agentic_toolkit.py` subcommands.
- Track false-positive rate over the next 5 sessions of opt-in E-GOV-001 use.

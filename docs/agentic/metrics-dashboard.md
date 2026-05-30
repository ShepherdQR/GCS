# GCS Agentic Metrics Dashboard

Status: active
Snapshot date: 2026-05-30

## Purpose

This dashboard tracks whether the GCS agentic organization is becoming more
reliable, legible, and reviewable. It is intentionally lightweight: update it
after non-trivial lifecycle tasks or during a periodic agentic-SE review.

The dashboard is not a scoreboard. It is a control panel for evidence quality,
workflow health, and narrative maturity.

## Current Baseline

| Area | Current level | Evidence | Next target |
| --- | --- | --- | --- |
| Task-card discipline | Strong | Recent non-trivial tasks have task cards with narrative_line and token_budget fields. | Keep 100% coverage for non-trivial tasks. |
| Completed-task archives | Strong | Recent non-trivial tasks have validated archives. | Add narrative_line_claimed + Narrative Line Impact section. |
| Closure quality | Strong | Closure score dimensions now include narrative_line_coverage (0-4). | Record closure score for each non-trivial archive. |
| Narrative line coverage | New | 14 narrative lines with individual development plans at `docs/narrative-lines/`. Task cards can declare impact. `validate-narrative-coverage` command produces coverage matrix. | Wired into session-close-orchestrator Step 1. |
| Token audit system | Strong, improved | Git linking fixed (timezone + encoding), cost storage populated. 38 sessions in DB with non-zero commits and cost. `snap`, `trend`, `report` commands operational. | Add automated budget enforcement. |
| Session close pipeline | Strong, improved | Session-close-orchestrator has 6-step pipeline with Step 4.5 output existence check. Task-intake → orchestrator → session-close-orchestrator chain defined. | Exercise the full chain end-to-end. |
| Docs validation | Strong | `validate-docs` passes. | Keep passing. |
| Inventory validation | Strong | `validate-inventory` is part of the expected gate. | Run for scoped changes. |
| Skill validation | Strong | Project skills are the routing layer. 18 steward skills + 4 pipeline skills. | Run after skill-related work. |
| Dependency boundary | Strong | `check-dependencies` is part of the expected gate. | Keep mathematical layers free of UI/IO/agentic dependencies. |
| Product/user narrative | Strong but split | Researcher primary audience, D1/D2/D3/D5 demos, B1/B2 benchmarks, R1 preview. External review still pending. | Convert review packet into actual external review. |
| Metrics trend history | Active | Baseline and Figure 95 trend artifacts exist. Token audit trend shows 7-day BEI progression. | Add timestamped updates after closures. |
| Permission/governance telemetry | Strengthening | E-GOV-001 and E-GOV-003 validator candidates created. I002 promoted to Practiced. Permission policy and threat matrix in place. | Exercise validator candidates against real sessions. |
| Institutional agents | Strengthening | I001 promoted (Bladesmith, 10/10). I002 promoted (Tailor, 8/10). I003-I005 seeded. 9 candidates with prompts. Night-watch calibration run. | Close candidate-to-seed pipeline bottleneck. |

## Recent Progress (May 27-30)

| Date | Change | Impact |
|------|--------|--------|
| 2026-05-30 | 14 narrative line folders + development plans | Narrative architecture now has per-line plans |
| 2026-05-30 | `narrative_lines` field in task cards + completed reports | Tasks can declare and evaluate narrative impact |
| 2026-05-30 | `validate-narrative-coverage` command | Coverage matrix shows which lines are exercised |
| 2026-05-30 | Token audit git linker fix (timezone + encoding) | Commits and cost now populate correctly |
| 2026-05-30 | Step 4.5 output existence check in close pipeline | Mechanical gate prevents incomplete archives |
| 2026-05-30 | `task-intake` skill (Steps 0-2) | Classification, card creation, human gate, dispatch |
| 2026-05-30 | `token_budget` field in task cards | Budget enforcement by risk tier |
| 2026-05-30 | Orchestrator decision audit scaffold | Architecture decision tracking |

## Quality Gate Trend History

| Date | Task | Trigger | Validate-docs | Python compile | Token audit | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-30 | Narrative line system + token fix + pipeline hardening | Task closure | PASS | PASS | PASS (38 sessions, commits/cost live) | Multi-pronged agentic-SE infrastructure improvement. |
| 2026-05-27 | Weak-line short-term plan execution | Task closure | PASS | PASS | N/A | E-GOV-001 validator candidate created. |
| 2026-05-26 | Researcher evidence roadmap execution | Task closure | PASS | PASS | N/A | Narrative map v2, Figure 95 trend, D3/D5 packages. |
| 2026-05-25 | Agentic PR governance nightly diagnostics | Task closure | PASS | PASS | N/A | Governance eval seeds, threat matrix, PR audit. |

## Update Rule

Update this dashboard when any of these occur:
- a non-trivial task closes;
- a high-risk task uses a human gate;
- a completed-task archive scores below 30;
- default quality-gate behavior changes;
- a new institutional agent, skill, eval, or governance rule is promoted;
- a release, onboarding, or public-facing narrative milestone is created.

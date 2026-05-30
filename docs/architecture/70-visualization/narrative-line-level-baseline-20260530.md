# Narrative Line Level Baseline — 2026-05-30

Status: baseline
Date: 2026-05-30
Previous: `narrative-line-level-baseline-20260526.md`

## Purpose

This baseline records the state of all 14 GCS narrative lines as of 2026-05-30,
four days after the previous baseline and after a burst of solver (Steps 52-55)
and token-economics (v2 complete delivery) activity.

## Changed Since 2026-05-26

| Domain | What changed |
|--------|-------------|
| Solver | Steps 52-55 landed: articulation/biconnected decomposition, three spanning-tree patterns (point-distance, parallel/perpendicular, spanning-forest planner integration). |
| Token economics | v2 system fully delivered: Phase 0-5 (schema migration, metrics engine, composite indices, decision engine, diagnostic card, CLI, alerts, migration, skill integration, three-horizon roadmap). |
| Agentic layer | Agent/skill audit completed: promoted bladesmith, created gardener, cleaned stale artifacts. Session closer upgraded. |
| UI/Viewer | A1 bridge taste seed + A2 full-window screenshot landed. Long-term aesthetic design doc created. |
| Governance | E-GOV-001 exercised evidence accumulated; validator candidate still not built. |

## Score Mapping (unchanged)

| Text level | Numeric baseline score |
|------------|----------------------:|
| Very strong | 5.0 |
| Strong | 4.0 |
| Strong but split | 3.5 |
| Developing | 3.0 |
| Initial and strengthening | 2.5 |
| Partial | 2.0 |
| Weak | 1.0 |

## Baseline Table — 2026-05-30

| # | Narrative line | Level | Score | δ | Arc |
|---|---------------|-------|------:|----|-----|
| 1 | Scientific solver thesis | Strong | 4.0 | — | 1 |
| 2 | Module contract architecture | Very strong | 5.0 | — | 1 |
| 3 | Implementation roadmap | Strong | 4.0 | — | 1 |
| 4 | Fixture and counterexample corpus | Strong | 4.0 | — | 1 |
| 5 | Runtime/history/replay evidence | Strong | 4.0 | — | 2 |
| 6 | Agentic-SE operating layer | Very strong | 5.0 | — | 3 |
| 7 | Quality gates and evidence | Strong | 4.0 | — | 3 |
| 8 | UI/viewer/scientific figures | Strong, integration in progress | 4.0 | — | 2 |
| 9 | Institutional agents and learning | Developing | 3.0 | — | 3 |
| 10 | Git/worktree/PR governance | Strong | 4.0 | — | 3 |
| 11 | Product/user/market story | Strong but split | 3.5 | — | 4 |
| 12 | Release/packaging/onboarding | Strong but split | 3.5 | — | 4 |
| 13 | External benchmark/comparison | Strong but split | 3.5 | — | 4 |
| 14 | Business/open-source strategy | Developing | 3.0 | — | 4 |

## Arc-Level Summary

| Arc | Lines | Average score | Character |
|-----|-------|--------------:|-----------|
| Arc 1: Solver evidence | 1-4 | 4.25 | Consistently strong. Solver is the project's backbone. |
| Arc 2: Evidence workbench | 5, 8 | 4.00 | Strong artifacts; missing end-to-end evidence chain. |
| Arc 3: Agentic organization | 6, 7, 9, 10 | 4.00 | Very strong core; institutional agents and validators lag. |
| Arc 4: Product and adoption | 11-14 | 3.38 | The weak arc. Four lines at "strong but split" or "developing." |

## Key Reading

**Strongest lines unchanged**: module contracts (2) and agentic-SE operating layer (6).

**Solver momentum**: Steps 52-55 strengthen line 1 (solver thesis) and line 3
(roadmap). Solver evidence continues to accumulate; the gap remains translating
it into user-facing value (line 11).

**Token economics as agentic evidence**: The v2 delivery demonstrates line 6
(agentic-SE) operating at scale — a complete cross-session economic evaluation
system with its own architecture, tests, and roadmap — produced within the
agentic lifecycle. This proves the operating layer works, but also raises the
governance question: when should such a subsystem be promoted from tools/ into
a first-class module?

**Arc 4 stagnation**: The four external-facing lines (11-14) have not moved
since 2026-05-26. The project has all the artifacts (R1 preview, D1-D5 demos,
B1-B2 benchmarks, review packet, contribution boundary) but none of the
external feedback loops that would turn "strong but split" into "strong."

**Governance eval bottleneck**: E-GOV-001 has accumulated enough exercised
evidence for an L3 validator candidate but remains unimplemented. This is the
most actionable weakness in Arc 3.

## Next Strengthening Targets (updated)

1. Build E-GOV-001 validator candidate (highest leverage, lowest risk).
2. Add R2 reproducible build transcript.
3. Decide first external adapter path (SolveSpace or FreeCAD).
4. Convert first researcher review packet into real review archive.
5. Produce one end-to-end viewer-evidence walkthrough (report → viewer → figure).

## Refresh Rule

Refresh this baseline when any three of the five strengthening targets above
are completed, or when a narrative line changes level.

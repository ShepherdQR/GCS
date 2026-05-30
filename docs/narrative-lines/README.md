# Narrative Line Development Plans

Status: active
Date: 2026-05-30
Source map: `docs/architecture/95-gcs-narrative-map.md`
Weakness plan: `docs/agentic/narrative-weakness-development-plan-20260530.md`

Each narrative line has an independent folder with a `development-plan.md` that
records current level, gap, next moves, evidence artifact, and promotion gate.

## Narrative Lines

| # | Line | Level | Folder |
|---|------|-------|--------|
| 01 | Scientific solver thesis | Strong (4.0) | [01-scientific-solver-thesis/](01-scientific-solver-thesis/) |
| 02 | Module contract architecture | Very strong (5.0) | [02-module-contract-architecture/](02-module-contract-architecture/) |
| 03 | Implementation roadmap | Strong (4.0) | [03-implementation-roadmap/](03-implementation-roadmap/) |
| 04 | Fixture and counterexample corpus | Strong (4.0) | [04-fixture-corpus/](04-fixture-corpus/) |
| 05 | Runtime/history/replay evidence | Strong (4.0) | [05-runtime-history-replay-evidence/](05-runtime-history-replay-evidence/) |
| 06 | Agentic-SE operating layer | Very strong (5.0) | [06-agentic-se-operating-layer/](06-agentic-se-operating-layer/) |
| 07 | Quality gates and evidence | Strong (4.0) | [07-quality-gates-evidence/](07-quality-gates-evidence/) |
| 08 | UI/viewer/scientific figures | Strong (4.0) | [08-ui-viewer-scientific-figures/](08-ui-viewer-scientific-figures/) |
| 09 | Institutional agents and learning | Developing (3.0) | [09-institutional-agents-learning/](09-institutional-agents-learning/) |
| 10 | Git/worktree/PR governance | Strong (4.0) | [10-git-worktree-pr-governance/](10-git-worktree-pr-governance/) |
| 11 | Product/user/market story | Strong but split (3.5) | [11-product-user-market-story/](11-product-user-market-story/) |
| 12 | Release/packaging/onboarding | Strong but split (3.5) | [12-release-packaging-onboarding/](12-release-packaging-onboarding/) |
| 13 | External benchmark/comparison | Strong but split (3.5) | [13-external-benchmark-comparison/](13-external-benchmark-comparison/) |
| 14 | Business/open-source strategy | Developing (3.0) | [14-business-open-source-strategy/](14-business-open-source-strategy/) |

## Narrative Arcs

| Arc | Lines | Goal |
|-----|-------|------|
| Arc 1: Solver Evidence | 01-04 | Prove GCS can solve, diagnose, and explain geometric constraint scenes |
| Arc 2: Evidence Workbench | 05, 07, 08 | Let a user inspect geometry, diagnostics, history, and solver evidence |
| Arc 3: Agentic Organization | 05-10 | Make the repository a bounded, evidence-rich human-agent engineering organization |
| Arc 4: Product And Adoption | 11-14 | Make the project understandable and useful to an external human |

## Update Rule

When a narrative line's level changes or its next move completes, update that
line's `development-plan.md` and refresh this index.

# GCS Narrative Map

Status: active
Date: 2026-05-26

## Purpose

This document compresses the current GCS project story into one durable map.
It records the development level of each narrative line, the next plan for each
line, and the execution rhythm for turning strong internal artifacts into a
legible solver, product, and agentic-organization story.

Background research lives in
`docs/research/20260526/ai-organization-frontier/`. This architecture note is
the active project-facing version.

## One-Sentence Spine

GCS solves geometric constraints by producing evidence-rich local-to-global
reports, and it builds itself through an evidence-rich agentic organization.

Every future narrative, roadmap, and demo should make clear which side it
advances:

- better solver evidence;
- better user-facing workbench;
- better fixture and benchmark corpus;
- better agentic organization;
- better governance, metrics, and learning.

## Current Development Level

| Narrative line | Level | Current state | Main gap | Next move |
| --- | --- | --- | --- | --- |
| Scientific solver thesis | Strong | Local-to-global semantics, reports, diagnostics, and obstruction vocabulary are clear. | The "why users should care" story is less visible than the internal math story. | Attach solver evidence to user-facing demo scenarios. |
| Module contract architecture | Very strong | Target modules, dependency direction, and contract-test posture are explicit. | Prototype names and detailed implementation may still lag target vocabulary. | Keep every new change mapped to target module, report surface, and contract evidence. |
| Implementation roadmap | Strong | Step history and upcoming solver work are recorded in depth. | New readers need a compressed view of roadmap arcs. | Maintain this map as the one-page entry point and keep details in the roadmap. |
| Fixture and counterexample corpus | Strong | Verification, generated, milestone, showcase, and counterexample assets exist. | The corpus is not yet narrated as a maturity ladder. | Define corpus levels and acceptance evidence per level. |
| Runtime/history/replay evidence | Strong | Replay evidence and saved-report workflow are becoming a differentiator. | The auditability story is not yet foregrounded. | Use replay evidence as the trust bridge between solver behavior and agentic governance. |
| Agentic-SE operating layer | Very strong | Task cards, runbooks, archives, quality gates, PR audit, and institutional agents exist. | The system is extensive and needs a compact operating map. | Keep `docs/agentic` operational and summarize its role here. |
| Quality gates and evidence | Strong | Local validators, contract tests, tool tests, fixture gates, and quality scripts exist. | Trend visibility is still thin. | Maintain `docs/agentic/metrics-dashboard.md` after non-trivial tasks. |
| UI/viewer/scientific figures | Strong but split | Viewer, visual QA, figure pipeline, and Solver Evidence Workbench direction exist. | Visual work can appear separate from solver evidence. | Frame UI as evidence-first interaction, not decoration. |
| Institutional agents and learning | Promising | Standing agents, templates, examples, and refusal evals exist. | Utility must be proven through reuse and recurrence reduction. | Promote only with template, example, boundary, and eval evidence. |
| Git/worktree/PR governance | Strong | Worktree, branch, PR audit, permissions, and repository-audit policies exist. | Broader AI-security threat categories are not yet summarized in one matrix. | Add a permission threat matrix when the next governance task runs. |
| Product/user/market story | Weak | Build, viewer, and architecture docs exist, but target users are not foregrounded. | A collaborator can learn architecture faster than user value. | Use `docs/product/gcs-product-user-brief.md` as the first product narrative. |
| Release/packaging/onboarding | Partial | Build, test, and viewer commands exist. | No polished 20-minute contributor path or release ladder. | Add onboarding and release-readiness docs after product brief stabilizes. |
| External benchmark/comparison | Weak | Research notes exist, but no solver comparison corpus or positioning map. | GCS is not yet placed against academic or commercial solvers. | Create a comparison and benchmark plan after corpus ladder. |
| Business/open-source strategy | Weak | The repo has project identity but no explicit distribution model. | Audience and adoption path are unresolved. | Decide primary audience before public README expansion. |

## Narrative Arcs

### Arc 1: Solver Evidence

Goal: prove that GCS can solve, diagnose, and explain geometric constraint
scenes.

Owns:

- mathematical model;
- target module contracts;
- constraint and incidence semantics;
- diagnostics, rank, residual, conflict, redundancy, and obstruction reports;
- fixture and counterexample corpus.

Near-term plan:

1. Keep Step-level implementation roadmap as the detailed execution source.
2. Define corpus maturity levels.
3. Tie each solver milestone to report evidence and at least one demo scene.

### Arc 2: Evidence Workbench

Goal: let a user inspect geometry, constraints, diagnostics, history, and
solver evidence in one local workbench.

Owns:

- Python viewer;
- viewer bridge;
- visual QA gates;
- scientific figures;
- replay and saved-report projection.

Near-term plan:

1. Treat UI as evidence-first interaction.
2. Make replay evidence visible before adding broader UI surface area.
3. Use screenshots and visual QA as acceptance evidence, not decoration.

### Arc 3: Agentic Organization

Goal: make the repository itself a bounded, evidence-rich human-agent
engineering organization.

Owns:

- task cards;
- worktree and branch governance;
- PR audit;
- quality gates;
- completed-task archive;
- institutional agents;
- evals and experience promotion.

Near-term plan:

1. Maintain `docs/agentic/metrics-dashboard.md`.
2. Continue task-scoped archives for non-trivial work.
3. Promote institutional-agent rules only after evidence.

### Arc 4: Product And Adoption

Goal: make the project understandable and useful to an external human.

Owns:

- target user and jobs-to-be-done;
- demo ladder;
- onboarding path;
- release-readiness path;
- external comparison and benchmark positioning.

Near-term plan:

1. Start with `docs/product/gcs-product-user-brief.md`.
2. Convert the strongest internal scenarios into demo workflows.
3. Add a 20-minute new contributor path once demo workflows stabilize.

## Execution Plan

| Phase | Status | Output | Acceptance |
| --- | --- | --- | --- |
| Phase 0: Narrative map | Complete in this batch | `docs/architecture/95-gcs-narrative-map.md` | A reviewer can see all narrative lines and next moves from one document. |
| Phase 1: Product/user brief | Complete in this batch | `docs/product/gcs-product-user-brief.md` | Target users, workflows, promises, non-goals, and first demos are explicit. |
| Phase 2: Metrics dashboard | Complete in this batch | `docs/agentic/metrics-dashboard.md` | Current baseline and update rules are visible. |
| Phase 3: Corpus and demo ladders | Complete in next-stage batch | `docs/architecture/96-fixture-corpus-maturity-ladder.md` and `docs/product/gcs-demo-ladder.md` | Roadmap becomes user-visible capability growth. |
| Phase 4: Permission threat matrix | Complete in next-stage batch | `docs/agentic/permission-threat-matrix.md` | Governance maps private data, untrusted content, outbound channels, writes, branches, and network actions. |
| Phase 5: Onboarding and release path | Partial in next-stage batch | `docs/product/20-minute-contributor-path.md`; release checklist remains later | A new contributor can build context, run light validators, and understand the thesis. |
| Phase 6: External positioning | Later | Solver comparison and benchmark plan | GCS can explain how it differs from academic and commercial solvers. |

## Decision Rules

- Architecture truth stays under `docs/architecture/`.
- Operating workflow truth stays under `docs/agentic/`.
- Product and audience truth may live under `docs/product/`.
- Research remains under `docs/research/` until promoted into active project
  docs.
- A narrative line becomes mature only when it has evidence, ownership, an
  update rhythm, and a visible next action.

## Next Task Queue

1. Define release-readiness checklist.
2. Add D1 smoke demo note with command transcript.
3. Add D2 diagnostic classification demo package.
4. Add external comparison and benchmark plan.
5. Add benchmark-candidate selection criteria after fixture maturity stabilizes.

## Review Triggers

Review this map when:

- a major solver roadmap phase closes;
- a product/demo workflow changes;
- agentic-SE governance adds a new default gate;
- an institutional agent is promoted;
- the project prepares a public-facing release or README expansion.

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
| Agentic-SE operating layer | Very strong | Task cards, runbooks, archives, quality gates, PR audit, institutional agents, and an operating map exist. | The next risk is process sprawl rather than absence. | Keep `docs/agentic/agentic-organization-operating-map.md` as the compact entry point. |
| Quality gates and evidence | Strong | Local validators, contract tests, tool tests, fixture gates, and quality scripts exist. | Trend visibility is still thin. | Maintain `docs/agentic/metrics-dashboard.md` after non-trivial tasks. |
| UI/viewer/scientific figures | Strong, integration in progress | Viewer, visual QA, figure pipeline, Solver Evidence Workbench direction, and an explicit UI/viewer/figure integration plan exist. | The next proof point must show one evidence chain from report to viewer to figure/demo artifact. | Promote one end-to-end evidence walkthrough using `docs/architecture/97-ui-viewer-figure-integration-plan.md`. |
| Institutional agents and learning | Developing | Standing agents, templates, examples, refusal evals, and a registry scorecard exist. | Seed agents need more examples before promotion. | Use `docs/agentic/institutional-agent-registry-and-scorecard.md` before status changes. |
| Git/worktree/PR governance | Strong | Worktree, branch, PR audit, permissions, threat matrix, and repository-audit policies exist. | Governance evals are planned but not yet executable gates. | Execute the staged roadmap in `docs/agentic/governance-eval-roadmap.md`. |
| Product/user/market story | Initial and strengthening | Product brief, demo ladder, contributor path, and first demo package exist. | The story still lacks behavior-rich demo transcripts and external positioning. | Convert D1 and D2 demos into concrete demo packages with command evidence. |
| Release/packaging/onboarding | Partial | A 20-minute contributor path exists and build/test commands are documented elsewhere. | Release readiness, packaging, and support boundaries are not yet explicit. | Add a release-readiness checklist and package smoke path. |
| External benchmark/comparison | Weak | Corpus maturity levels exist, but external solver comparison is still absent. | GCS is not yet placed against academic or commercial solvers. | Create a comparison and benchmark plan after corpus ladder. |
| Business/open-source strategy | Weak | The repo has project identity and early user briefs, but no explicit distribution model. | Audience, adoption path, and contribution model are unresolved. | Decide primary audience before public README expansion. |

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
2. Bind viewer states and scientific figures to the same source evidence.
3. Make replay evidence visible before adding broader UI surface area.
4. Use screenshots and visual QA as acceptance evidence, not decoration.

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

1. Use `docs/agentic/agentic-organization-operating-map.md` as the compact
   operating entry point.
2. Maintain `docs/agentic/metrics-dashboard.md`.
3. Continue task-scoped archives for non-trivial work.
4. Promote institutional-agent rules only after scorecard and eval evidence.
5. Convert governance risks into staged evals before adding default gates.

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

## Relative Weakness Analysis

The strongest internal narratives are solver architecture, agentic operating
discipline, quality gates, and fixture evidence. The relatively weak lines are
now concentrated around external legibility: product behavior demos, release
readiness, external comparison, and distribution strategy.

| Relative weak line | Current level | Why it is still weak | Strengthening task already in plan |
| --- | --- | --- | --- |
| Product/user/market story | Initial and strengthening | The project now has product docs, but the user still sees more architecture than live behavior. | Build D1 smoke demo and D2 diagnostic classification demo packages with command transcripts. |
| Release/packaging/onboarding | Partial | New contributors have a first path, but release criteria and package smoke checks are not consolidated. | Add release-readiness checklist and package smoke path. |
| External benchmark/comparison | Weak | Corpus maturity exists, but no comparison map explains how GCS differs from other solvers. | Add external solver comparison and benchmark plan, then benchmark-candidate criteria. |
| Business/open-source strategy | Weak | The intended adoption model is not yet chosen. | Add audience, distribution, contribution, and positioning brief before public README expansion. |
| Governance eval execution | Developing | Risks are mapped, but most evals are not executable or opt-in gates yet. | Add prompt-level evals for unrelated staging, audit overclaim, and institutional-agent promotion. |
| Demo evidence packaging | Initial and active | Demo ladder exists and D5 has a first workbench evidence package target. | Earlier levels still need D1/D2 command packages. | Use `docs/product/demos/` for D0 task closure, D1 smoke, D2 diagnostics, and later replay/workbench demos. |

This means the next plan should not primarily add more internal architecture
language. It should translate the existing architecture into evidence packages
that a new user, reviewer, or future contributor can run, compare, and trust.

## Execution Plan

| Phase | Status | Output | Acceptance |
| --- | --- | --- | --- |
| Phase 0: Narrative map | Complete in this batch | `docs/architecture/95-gcs-narrative-map.md` | A reviewer can see all narrative lines and next moves from one document. |
| Phase 1: Product/user brief | Complete in this batch | `docs/product/gcs-product-user-brief.md` | Target users, workflows, promises, non-goals, and first demos are explicit. |
| Phase 2: Metrics dashboard | Complete in this batch | `docs/agentic/metrics-dashboard.md` | Current baseline and update rules are visible. |
| Phase 3: Corpus and demo ladders | Complete in next-stage batch | `docs/architecture/96-fixture-corpus-maturity-ladder.md` and `docs/product/gcs-demo-ladder.md` | Roadmap becomes user-visible capability growth. |
| Phase 4: Permission threat matrix | Complete in next-stage batch | `docs/agentic/permission-threat-matrix.md` | Governance maps private data, untrusted content, outbound channels, writes, branches, and network actions. |
| Phase 5: Onboarding and release path | Partial in next-stage batch | `docs/product/20-minute-contributor-path.md`; release checklist remains later | A new contributor can build context, run light validators, and understand the thesis. |
| Phase 6: AI organization operating narrative | Complete in this batch | `docs/agentic/agentic-organization-operating-map.md`, `docs/agentic/institutional-agent-registry-and-scorecard.md`, `docs/agentic/governance-eval-roadmap.md`, `docs/product/demos/agentic-task-closure-demo/README.md` | The agentic organization story has operating, role, eval, and demo artifacts. |
| Phase 7: External positioning | Next weak-line batch | Solver comparison and benchmark plan | GCS can explain how it differs from academic and commercial solvers. |
| Phase 8: Release and distribution strategy | Next weak-line batch | Release-readiness checklist and audience/distribution brief | GCS can explain who should adopt it, how to try it, and what readiness means. |

## Decision Rules

- Architecture truth stays under `docs/architecture/`.
- Operating workflow truth stays under `docs/agentic/`.
- Product and audience truth may live under `docs/product/`.
- Research remains under `docs/research/` until promoted into active project
  docs.
- A narrative line becomes mature only when it has evidence, ownership, an
  update rhythm, and a visible next action.

## Next Task Queue

1. Add D1 smoke demo package with exact command transcript and expected
   evidence.
2. Add D2 diagnostic classification demo package for solved, underconstrained,
   overconstrained, singular, and blocked scenes.
3. Keep the D5 Solver Evidence Workbench package current with viewer/figure
   artifacts from `97-ui-viewer-figure-integration-plan.md`.
4. Define release-readiness checklist with package smoke path and support
   boundaries.
5. Add external comparison and benchmark plan.
6. Add benchmark-candidate selection criteria after fixture maturity
   stabilizes.
7. Add audience, distribution, contribution, and open-source strategy brief
   before public README expansion.
8. Add prompt-level governance eval files for E-GOV-001, E-GOV-002, and
   E-GOV-008.

## Review Triggers

Review this map when:

- a major solver roadmap phase closes;
- a product/demo workflow changes;
- agentic-SE governance adds a new default gate;
- an institutional agent is promoted;
- the project prepares a public-facing release or README expansion.

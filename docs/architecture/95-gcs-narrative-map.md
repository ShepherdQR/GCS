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

Baseline visual:
`docs/architecture/70-visualization/assets/figure95-narrative-line-level-baseline-20260526.svg`.
Baseline brief:
`docs/architecture/70-visualization/narrative-line-level-baseline-20260526.md`.

![GCS Narrative Line Level Baseline](70-visualization/assets/figure95-narrative-line-level-baseline-20260526.svg)

| Narrative line | Level | Current state | Main gap | Next move |
| --- | --- | --- | --- | --- |
| Scientific solver thesis | Strong | Local-to-global semantics, reports, diagnostics, and obstruction vocabulary are clear. | The "why users should care" story is less visible than the internal math story. | Attach solver evidence to user-facing demo scenarios. |
| Module contract architecture | Very strong | Target modules, dependency direction, and contract-test posture are explicit. | Prototype names and detailed implementation may still lag target vocabulary. | Keep every new change mapped to target module, report surface, and contract evidence. |
| Implementation roadmap | Strong | Step history and upcoming solver work are recorded in depth. | New readers need a compressed view of roadmap arcs. | Maintain this map as the one-page entry point and keep details in the roadmap. |
| Fixture and counterexample corpus | Strong | Verification, generated, milestone, showcase, and counterexample assets exist. | The corpus is not yet narrated as a maturity ladder. | Define corpus levels and acceptance evidence per level. |
| Runtime/history/replay evidence | Strong | Replay evidence and saved-report workflow are becoming a differentiator. | The auditability story is not yet foregrounded. | Use replay evidence as the trust bridge between solver behavior and agentic governance. |
| Agentic-SE operating layer | Very strong | Task cards, runbooks, archives, quality gates, PR audit, institutional agents, and an operating map exist. | The next risk is process sprawl rather than absence. | Keep `docs/agentic/agentic-organization-operating-map.md` as the compact entry point. |
| Quality gates and evidence | Strong | Local validators, contract tests, tool tests, fixture gates, and quality scripts exist. | Trend visibility is still thin. | Maintain `docs/agentic/metrics-dashboard.md` after non-trivial tasks. |
| UI/viewer/scientific figures | Strong but split | Viewer, visual QA, figure pipeline, and Solver Evidence Workbench direction exist. | Visual work can appear separate from solver evidence. | Frame UI as evidence-first interaction, not decoration. |
| Institutional agents and learning | Developing | Standing agents, templates, examples, refusal evals, and a registry scorecard exist. | Seed agents need more examples before promotion. | Use `docs/agentic/institutional-agent-registry-and-scorecard.md` before status changes. |
| Git/worktree/PR governance | Strong | Worktree, branch, PR audit, permissions, threat matrix, and repository-audit policies exist. | Governance evals are planned but not yet executable gates. | Execute the staged roadmap in `docs/agentic/governance-eval-roadmap.md`. |
| Product/user/market story | Strong but split | Researcher primary audience, product brief, demo ladder, D1/D2/D3 demos, JSON classification, README route, and contributor boundary exist. | UI/workbench and external reviewer story are still thinner than CLI evidence. | Add D5 workbench screenshot package after visual QA. |
| Release/packaging/onboarding | Developing | A 20-minute contributor path, release-readiness checklist, R1 researcher-preview note, and package smoke automation exist. | Reproducible build transcript and R2 release criteria are not yet consolidated. | Add reproducible build transcript and schema-aware replay checker. |
| External benchmark/comparison | Developing | External comparison plan, benchmark criteria, B1 expected outputs, and D2 JSON summary exist. | No executable external baseline run or B2 microbenchmark set exists yet. | Add external-baseline feasibility matrix and B2 candidate review. |
| Business/open-source strategy | Developing | Primary audience, README route, contribution boundary, and R1 preview route are documented. | Public distribution and contribution workflow are still researcher-preview only. | Add contribution workflow examples after first external review. |

## Narrative Map V2: Evidence Routes And Promotion Gates

The v2 map adds two fields to each narrative line:

- evidence artifact: the file, command, or report that proves the line is real;
- promotion gate: the next condition that can justify raising the line's
  maturity level.

| Narrative line | Evidence artifact | Promotion gate |
| --- | --- | --- |
| Scientific solver thesis | CLI report evidence in D1/D2/D3 packages. | Add a B2 microbenchmark that isolates one solver-semantics claim. |
| Module contract architecture | `docs/architecture/30-contracts/` and module design docs. | Keep new implementation changes mapped to target contracts and report surfaces. |
| Implementation roadmap | Step execution reports and this narrative map. | Add a compressed roadmap arc when the next solver milestone closes. |
| Fixture and counterexample corpus | `docs/architecture/96-fixture-corpus-maturity-ladder.md` and B1 expected outputs. | Promote a stable C2 seed toward B2 with expected report fields and migration notes. |
| Runtime/history/replay evidence | `docs/product/demos/d3-replay-evidence/` and replay JSON. | Add schema-aware replay evidence checker. |
| Agentic-SE operating layer | Task cards, completed archives, operating map, and governance roadmap. | Exercise governance eval seeds against real archives before validator promotion. |
| Quality gates and evidence | Agentic toolkit validators and R1 package smoke. | Add trend history after several non-trivial closures. |
| UI/viewer/scientific figures | Figure 95 baseline and UI architecture docs. | Add D5 Solver Evidence Workbench screenshot package with visual QA. |
| Institutional agents and learning | Institutional-agent registry and scorecard. | Promote only after examples, refusal cases, and eval evidence accumulate. |
| Git/worktree/PR governance | Permission policy, threat matrix, PR audit docs, and scoped commits. | Convert the highest-risk prompt eval into a validator candidate. |
| Product/user/market story | README researcher route, D1/D2/D3 packages, and contribution boundary. | Demonstrate one external reviewer path from README to evidence artifact. |
| Release/packaging/onboarding | R1 release note and R1 package smoke JSON. | Add reproducible build transcript and R2 criteria. |
| External benchmark/comparison | B1 expected outputs and external comparison plan. | Add external-baseline feasibility matrix and first B2 candidate review. |
| Business/open-source strategy | Researcher audience strategy and contribution boundary. | Capture first researcher contribution or review as an archive-backed example. |

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

The strongest internal narratives remain solver architecture, agentic
operating discipline, quality gates, and fixture evidence. The researcher
audience decision, D1/D2/D3 packages, B1 expected outputs, R1 smoke automation,
README route, and contribution boundary move the external legibility line
forward. The weak axis is now the next rung of proof: schema-aware evidence
checking, external-baseline feasibility, B2 candidate selection, D5 workbench
evidence, and first external researcher review.

| Relative weak line | Current level | Why it is still weak | Strengthening task already in plan |
| --- | --- | --- | --- |
| Product/user/market story | Strong but split | CLI and evidence-route story is strong; workbench and external reviewer walkthrough are still thin. | Add D5 screenshot package and one external reviewer archive. |
| Release/packaging/onboarding | Developing | R1 smoke exists, but reproducible build transcript and R2 release contract do not. | Add reproducible build transcript and schema-aware replay checker. |
| External benchmark/comparison | Developing | B1 expected outputs exist, but external executable feasibility and B2 candidates do not. | Add external-baseline feasibility matrix and B2 candidate review. |
| Business/open-source strategy | Developing | README route and contribution boundary exist, but no external contribution example has landed. | Capture first researcher review or contribution as archive-backed evidence. |
| Governance eval execution | Developing | Three prompt-level eval seeds exist, but no validator candidate is implemented. | Exercise E-GOV-001, E-GOV-002, and E-GOV-008 in real archives before validator design. |
| Demo evidence packaging | Strong but split | D0, D1, D2, and D3 are packaged; D5 workbench demo remains future work. | Add D5 Solver Evidence Workbench screenshot package after visual QA. |

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
| Phase 7: Researcher-facing demos | Complete in researcher-audience batch | `docs/product/demos/d1-cli-smoke/` and `docs/product/demos/d2-diagnostic-classification/` | Researchers can run command-level smoke and diagnostic classification paths. |
| Phase 8: External positioning | Complete as seed | `docs/architecture/97-external-solver-comparison-and-benchmark-plan.md` and `98-benchmark-candidate-selection-criteria.md` | GCS can explain how it differs from academic, open-source, and commercial solver baselines without benchmark overclaiming. |
| Phase 9: Release and researcher distribution strategy | Complete as seed | `docs/product/release-readiness-checklist.md` and `docs/product/researcher-audience-strategy.md` | GCS can explain who should adopt it first, how to try it, and what readiness means. |
| Phase 10: Governance eval seeds | Complete as seed | `docs/agentic/evals/governance/` | The three highest-priority prompt-level governance evals are concrete. |
| Phase 11: Researcher evidence route | Complete in evidence-roadmap batch | D2 JSON classifier, D3 replay package, B1 expected outputs, R1 preview, README route, Narrative Map v2, and Figure 95 refresh | A researcher can move from README to CLI evidence, replay evidence, expected outputs, and release smoke without raw chat context. |

## Decision Rules

- Architecture truth stays under `docs/architecture/`.
- Operating workflow truth stays under `docs/agentic/`.
- Product and audience truth may live under `docs/product/`.
- Research remains under `docs/research/` until promoted into active project
  docs.
- A narrative line becomes mature only when it has evidence, ownership, an
  update rhythm, and a visible next action.

## Next Task Queue

1. Add a schema-aware replay evidence checker.
2. Add an external-baseline feasibility matrix.
3. Review B1 expected outputs for B2 research microbenchmark candidates.
4. Add a D5 Solver Evidence Workbench screenshot package after visual QA.
5. Capture the first external researcher review or contribution as a
   completed-task archive.
6. Decide which external baselines are executable locally and which remain
   documentation-only comparisons.
7. Exercise E-GOV-001, E-GOV-002, and E-GOV-008 in real task archives before
   designing validator candidates.

## Review Triggers

Review this map when:

- a major solver roadmap phase closes;
- a product/demo workflow changes;
- agentic-SE governance adds a new default gate;
- an institutional agent is promoted;
- the project prepares a public-facing release or README expansion.

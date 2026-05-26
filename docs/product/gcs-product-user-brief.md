# GCS Product And User Brief

Status: initial
Date: 2026-05-26

## Purpose

This brief gives the GCS project a product/user narrative that complements the
architecture narrative. It should help future work answer: who benefits, what
workflow improves, and which evidence proves the improvement.

## Product Thesis

GCS is a local geometric constraint solving workbench that emphasizes
explainable solver evidence: users should be able to see not only a solved
configuration, but also why the solver accepted, rejected, or diagnosed a
scene.

## Primary Audiences

Primary audience decision, 2026-05-26:

```text
solver and geometric-constraint researchers
```

| Audience | Need | GCS value |
| --- | --- | --- |
| Solver researcher | Explore constraint semantics, decomposition, rank, and diagnostic behavior. | Evidence-rich fixtures, reports, counterexamples, benchmark criteria, and command transcripts. |
| CAD or geometry-tool developer | Understand how a constraint scene fails or succeeds. | Stable diagnostics, replay evidence, and scenario corpus. |
| Agentic-SE practitioner | See how a serious technical repo governs AI work. | Task cards, quality gates, archives, institutional agents, and metrics. |
| Local visualization user | Inspect geometry, constraints, solve history, and reports. | Solver Evidence Workbench direction. |
| New contributor | Build, run, test, and understand the project quickly. | Onboarding path and narrative map. |

The near-term primary audience is now narrower than "technical reviewer":
researchers who can judge whether the solver evidence, diagnostic taxonomy,
fixtures, and counterexamples are meaningful.

## Jobs To Be Done

1. Load or create a geometric constraint scene.
2. Inspect entities, rigid sets, constraints, and scene structure.
3. Run or replay a solve attempt.
4. Understand whether the scene is well constrained, under constrained, over
   constrained, singular, inconsistent, malformed, or not yet supported.
5. Inspect report evidence: status, subjects, rank/residual signals, history,
   and saved artifacts.
6. Preserve interesting scenes as verification fixtures, milestones,
   showcases, or counterexamples.
7. Use agentic workflow artifacts to understand what changed in the project and
   why.

## Must-Not-Fail Properties

- Solver reports must be explicit about uncertainty and unsupported behavior.
- Diagnostics must not hide under-constrained, over-constrained, inconsistent,
  redundant, or singular cases behind a generic failure.
- Viewer state must not become hidden solver truth.
- IO and replay artifacts must remain reproducible enough for tests and future
  agents.
- Agentic workflow artifacts must not claim completion without evidence.
- High-risk solver or governance changes must keep human gates and focused
  verification.

## First Demo Workflows

### Demo 1: Basic Solver Evidence

User story:

A reviewer opens a small fixture, runs the CLI or focused test, and sees a
clear report that identifies scene status and evidence.

Acceptance:

- fixture path is named;
- command is documented;
- report status is stable;
- expected failure or success is explained.

### Demo 2: Replay Evidence

User story:

A reviewer follows a command history from scene setup through solve and saved
report evidence.

Acceptance:

- command sequence is deterministic;
- replay evidence is inspectable;
- viewer or CLI projection uses the same evidence boundary.

### Demo 3: Counterexample As Asset

User story:

A generated scene that fails numeric acceptance is preserved as a
counterexample with solver-obstruction evidence, rather than deleted.

Acceptance:

- counterexample has metadata;
- solver output or report evidence is linked;
- future work can target the obstruction.

### Demo 4: Agentic Task Closure

User story:

A reviewer opens a completed-task archive and can reconstruct the request,
files changed, validation evidence, decisions, and next task without raw chat.

Acceptance:

- task card validates;
- completed-task report validates;
- closure score is recorded for non-trivial work;
- unrelated local files are excluded from commit scope.

## Product Promises

Near term:

- GCS will be honest about solver status and uncertainty.
- GCS will preserve evidence for solved, failed, and unsupported scenes.
- GCS will keep architecture and agentic workflow boundaries explicit.

Medium term:

- GCS will provide an evidence-first local workbench for geometry, constraints,
  diagnostics, and replay.
- GCS will grow a fixture corpus that functions as a scientific testbench.
- GCS will expose a clear onboarding path for technical contributors.

Longer term:

- GCS will position itself against academic and commercial geometric constraint
  solvers through transparent fixtures and diagnostics.
- GCS will demonstrate an agentic organization model for serious technical
  software.

## Non-Goals

- Do not become a polished commercial CAD product before solver evidence is
  trustworthy.
- Do not optimize visual polish ahead of diagnostic clarity.
- Do not hide mathematical or numeric uncertainty for a cleaner demo.
- Do not let agentic workflow artifacts become runtime solver dependencies.
- Do not pursue broad automation without permissions, evals, and human gates.

## Product Narrative Metrics

| Metric | Why it matters | Starting stance |
| --- | --- | --- |
| Demo workflow count | Shows user-visible capability. | Initial demo candidates identified here. |
| Fixture maturity coverage | Connects scenes to evidence. | Needs corpus maturity ladder. |
| New contributor time-to-run | Tests onboarding quality. | Needs 20-minute path. |
| Report evidence inspectability | Tests solver trust. | D1, D2, D3, and B1 expected outputs now connect internal evidence to product demos. |
| Completed-task reconstructability | Tests agentic organization quality. | Strong and validated for recent tasks. |

## Next Product Tasks

1. Add a schema-aware replay evidence checker.
2. Add an external-baseline feasibility matrix.
3. Identify the first B2 research microbenchmark candidates.
4. Add a D5 Solver Evidence Workbench screenshot package after visual QA.
5. Decide which external baselines are executable locally and which remain
   documentation-only comparisons.

Completed first follow-ups:

- `docs/product/20-minute-contributor-path.md`
- `docs/product/gcs-demo-ladder.md`
- `docs/architecture/96-fixture-corpus-maturity-ladder.md`
- `docs/product/demos/d1-cli-smoke/`
- `docs/product/demos/d2-diagnostic-classification/`
- `docs/product/demos/d3-replay-evidence/`
- `tools/product_demo/diagnostic_classification.py`
- `tools/product_demo/r1_package_smoke.py`
- `docs/architecture/benchmarks/b1-diagnostic-classification/`
- `docs/product/releases/r1-researcher-preview-20260526.md`
- `docs/product/researcher-contribution-boundary.md`
- `docs/product/release-readiness-checklist.md`
- `docs/product/researcher-audience-strategy.md`
- `docs/architecture/97-external-solver-comparison-and-benchmark-plan.md`
- `docs/architecture/98-benchmark-candidate-selection-criteria.md`

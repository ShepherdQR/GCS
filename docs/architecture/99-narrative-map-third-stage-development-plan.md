# Narrative Map Third-Stage Development Plan

Status: active
Date: 2026-05-26
Primary audience: solver and geometric-constraint researchers

## Purpose

This document persists the next Narrative map development plan after the
researcher evidence-route batch. The project no longer needs only a stronger
story. It needs a story whose evidence can be checked, compared, reviewed, and
kept fresh over time.

## Strategic Thesis

The next stage of the GCS narrative is:

```text
from executable researcher route -> auditable research workbench narrative
```

The main movement is not more prose. It is a tighter chain:

```text
README route -> D1/D2/D3 evidence -> replay checker -> B1/B2 benchmark review
             -> D5 evidence workbench -> external review packet -> trend map
```

## Seven-Step Plan

| Step | Output | Narrative line strengthened | Acceptance gate |
| --- | --- | --- | --- |
| 1. Schema-aware replay evidence checker | `tools/product_demo/replay_evidence_check.py` and D3 check JSON | Runtime/history/replay evidence; release readiness | D3 replay artifact passes required-field, status, stage-order, and report-code checks. |
| 2. External-baseline feasibility matrix | `docs/architecture/benchmarks/external-baseline-feasibility-matrix.md` | External benchmark/comparison | Each baseline is classified as executable, source-available, documentation-only, or commercial/proprietary. |
| 3. B2 microbenchmark candidate review | `docs/architecture/benchmarks/b2-microbenchmark-candidate-review.md` | Scientific solver thesis; fixture corpus | Every B1 candidate is promoted, deferred, or rejected with a research question and missing evidence. |
| 4. D5 Solver Evidence Workbench screenshot package | `docs/product/demos/d5-solver-evidence-workbench/` | Product/user story; UI/viewer/scientific figures | Deterministic PNG and manifest pass screenshot-baseline QA. |
| 5. First external researcher review archive | `docs/product/reviews/first-external-researcher-review-packet-20260526.md` | Business/open-source strategy | Review packet states what an external researcher should inspect, what feedback is expected, and what is not claimed. |
| 6. Governance eval promotion evidence | governance eval docs and roadmap updates | Governance eval execution; institutional learning | E-GOV-001, E-GOV-002, and E-GOV-008 cite exercised archive evidence without claiming default-gate readiness. |
| 7. Figure 95 trend artifacts | trend spec and trend note | Narrative map itself | Trend artifact records how weak external lines moved from seed to executable route to auditable research workbench. |

## Execution Status

| Step | Status | Evidence |
| --- | --- | --- |
| 1. Schema-aware replay evidence checker | Complete | `docs/product/demos/d3-replay-evidence/artifacts/g1-replay-evidence.check.json` reports 17/17 checks passed. |
| 2. External-baseline feasibility matrix | Complete | `docs/architecture/benchmarks/external-baseline-feasibility-matrix.md` separates local executable, source/documentation, and commercial-only baselines. |
| 3. B2 microbenchmark candidate review | Complete | `docs/architecture/benchmarks/b2-microbenchmark-candidate-review.md` promotes B2-01 and B2-02 as candidates, defers over-constrained and singular cases, and keeps malformed input in IO scope. |
| 4. D5 Solver Evidence Workbench screenshot package | Complete as static package | `docs/product/demos/d5-solver-evidence-workbench/artifacts/screenshot-baselines.json` passes screenshot-baseline QA. |
| 5. First external researcher review archive | Complete as review packet | `docs/product/reviews/first-external-researcher-review-packet-20260526.md` creates the route and archive contract; no actual external feedback is claimed. |
| 6. Governance eval promotion evidence | Complete as exercised evidence | `docs/agentic/evals/governance/exercised-evidence-20260526.md` records exercised evidence without promoting a default gate. |
| 7. Figure 95 trend artifacts | Complete | `docs/architecture/70-visualization/narrative-line-level-trend-20260526.md` and the SVG trend artifact record the maturity movement. |

## Promotion Logic

The maturity level of a narrative line can rise only when all four conditions
are true:

1. There is an evidence artifact.
2. There is a repeatable command or review path.
3. There is a visible limitation boundary.
4. The next promotion gate is explicit.

This prevents the Narrative map from turning into a motivational document. It
keeps the map as a project control surface.

## Current Priority

The two highest-leverage steps are:

1. replay evidence checker, because it makes the strongest internal trust
   artifact auditable;
2. external-baseline feasibility matrix, because it makes comparison honest
   before benchmark claims appear.

The D5 package is deliberately a static evidence-board screenshot package in
this batch. It should not be described as a complete GUI implementation. It is
a visual target and QA artifact that follows:

- **GCS Quiet Technical Atelier**;
- **GCS Warm Evidence Tokens**;
- **GCS Evidence-First Interface Grammar**;
- **GCS Scientific Figure Pipeline**;
- **GCS Visual Integrity Gate**.

## Output Contract

At the end of this stage, a reviewer should be able to answer:

- Can replay evidence be checked by a tool?
- Which external baselines are realistic to compare now?
- Which B1 cases are credible B2 candidates?
- What should the future Solver Evidence Workbench show?
- What would an external researcher review first?
- Which governance evals have real archive evidence?
- How did Figure 95 levels move over time?

## Follow-On Gates

After this stage, the next Narrative map review should decide whether to:

- implement the first B2 microbenchmark;
- add an executable external baseline adapter;
- harden D5 from static evidence-board screenshot into live GUI screenshot;
- convert one governance eval into a validator candidate;
- split Figure 95 into baseline, latest, and trend-series figures.

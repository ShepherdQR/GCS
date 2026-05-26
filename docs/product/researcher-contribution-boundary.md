# Researcher Contribution Boundary

Status: active
Date: 2026-05-26
Audience: solver and geometric-constraint researchers

## Purpose

This document tells researchers what kinds of contributions fit the current
GCS maturity level. It protects the project from broad CAD-product requests
while making evidence-centered contributions welcome.

## Welcome Contributions

| Contribution type | Good shape |
| --- | --- |
| Fixture proposal | Small scene, clear research question, expected status, and limitation note. |
| Diagnostic taxonomy comment | Concrete example showing where status, obstruction, rank, residual, or rollback evidence could be clearer. |
| Benchmark candidate | Expected-output file plus rationale under the B1/B2 criteria. |
| Replay evidence review | Field-level issue in saved report, stage ordering, or schema stability. |
| External comparison note | Source-linked observation about solver diagnostics, not a marketing claim. |
| Agentic-SE process review | Specific archive, task card, validation, or governance-eval improvement. |

## Defer Contributions

| Request | Why deferred |
| --- | --- |
| General CAD feature parity | The current primary product is researcher evidence, not a production sketcher. |
| Performance leaderboard | Benchmark semantics and expected outputs must stabilize first. |
| GUI-first workflow | The Solver Evidence Workbench direction exists, but CLI evidence is the current front door. |
| Installer or binary release | R1 is a local researcher preview; R3 packaging is later. |
| Broad automation permissions | Governance evals need more real examples before default gates expand. |

## Contribution Checklist

A strong researcher contribution should answer:

1. Which fixture, report, benchmark, or narrative line does this touch?
2. What command or artifact proves the point?
3. What is the expected status, report code, or obstruction?
4. What limitation should remain visible?
5. Which existing document should be updated if the contribution lands?

## Current Best Entry Points

- D2 diagnostic classification:
  `docs/product/demos/d2-diagnostic-classification/`
- B1 expected outputs:
  `docs/architecture/benchmarks/b1-diagnostic-classification/`
- D3 replay evidence:
  `docs/product/demos/d3-replay-evidence/`
- R1 researcher preview:
  `docs/product/releases/r1-researcher-preview-20260526.md`

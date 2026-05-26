# First External Researcher Review Packet

Status: ready for external review
Date: 2026-05-26
Primary audience: solver and geometric-constraint researchers

## Purpose

This packet is the handoff route for the first external researcher review. It
does not claim that external feedback has already been received.

The review target is narrow: can a researcher understand and inspect GCS's
current evidence route without raw chat context?

## Review Route

1. Read the project thesis in `README.md`.
2. Read `docs/architecture/95-gcs-narrative-map.md`.
3. Run or inspect D1 CLI smoke:
   `docs/product/demos/d1-cli-smoke/`.
4. Run or inspect D2 diagnostic classification:
   `python tools\product_demo\diagnostic_classification.py`.
5. Inspect D3 replay evidence:
   `docs/product/demos/d3-replay-evidence/`.
6. Run the D3 replay checker:
   `python tools\product_demo\replay_evidence_check.py`.
7. Inspect the D5 static workbench package:
   `docs/product/demos/d5-solver-evidence-workbench/`.
8. Review the external-baseline feasibility matrix:
   `docs/architecture/benchmarks/external-baseline-feasibility-matrix.md`.
9. Review B2 candidate decisions:
   `docs/architecture/benchmarks/b2-microbenchmark-candidate-review.md`.

## Questions For The Reviewer

| Question | Desired feedback |
| --- | --- |
| Is the solver-evidence thesis legible without a GUI? | Missing evidence, confusing terms, or stronger framing. |
| Are D1, D2, and D3 enough to justify a researcher-preview route? | Minimal extra artifact needed before sharing. |
| Which B2 candidate is the most scientifically useful? | Candidate ranking and expected report fields. |
| Which external baseline should be attempted first? | SolveSpace, FreeCAD, or documentation-only comparison. |
| Does the D5 static workbench package clarify the target UI? | Evidence hierarchy, visual clarity, and live-GUI caveats. |

## Non-Claims

- GCS is not presented as production CAD software.
- D5 is not presented as a live GUI workflow.
- No external executable benchmark result is claimed.
- Siemens D-Cubed is an industry reference, not a reproducible benchmark.
- This packet is not an endorsement or external review result.

## Expected Archive Shape After Review

When real feedback arrives, create:

```text
docs/product/reviews/YYYY-MM-DD-<reviewer-or-context>-review.md
```

Minimum fields:

- reviewer context;
- artifact route used;
- feedback received;
- accepted follow-up;
- rejected or deferred follow-up;
- evidence updated;
- whether the review changes Narrative map levels.

## Current Follow-Up

The next narrative-map strengthening task is to convert this packet into an
actual review archive after a real external researcher response or contribution
arrives.

# B2 Research Microbenchmarks

Status: active
Date: 2026-05-30
Primary audience: solver and geometric-constraint researchers
Parent: `docs/architecture/benchmarks/b2-microbenchmark-candidate-review.md`

## Purpose

B2 microbenchmarks test one durable solver-semantics claim per fixture with
fixed expected report fields. Unlike B1 (diagnostic classification smoke),
B2 claims are specific enough to be cited in research comparison.

## Current Set

| B2 ID | Fixture | Research claim | Expected status |
|-------|---------|---------------|-----------------|
| B2-01 | `fixtures/scene/verification/lgs/well_constrained.txt` | Accepted local solve emits rank, residual, gluing, and commit evidence. | `AcceptedWithWarnings` |
| B2-02 | `fixtures/scene/verification/lgs/under_constrained.txt` | Under-constrained accepted scene preserves explicit rank/nullity evidence per local section. | `AcceptedWithWarnings` |

## Deferred Candidates

| Candidate | Reason deferred | Re-evaluate when |
|-----------|----------------|------------------|
| `over_constrained.txt` | `runtime.numeric_failure` is not yet a clean semantic over-constraint taxonomy. | Diagnostic taxonomy splits inconsistent from generic numeric failure. |
| `singular counterexample` | Large for a microbenchmark. | Produce a smaller singular scene or document why the large scene is minimal. |

## Expected Output Format

Each expected output file follows `gcs.benchmark_expected_output.v1` schema
with fields:
- `benchmark_level`: "B2"
- `case_id`: unique identifier
- `fixture`: path to the input scene
- `expected_exit_code`: 0 for accepted, nonzero for rejected
- `expected_status`: solver status string
- `expected_report_codes`: list of report codes that must appear
- `research_claim`: the specific semantic claim this benchmark tests
- `known_limitations`: explicit caveats

## Migration Policy

When the solver report format changes:
1. Re-run the solver on each B2 fixture.
2. Update the expected output file to match the new output.
3. Record the solver version and date in the expected output's `migration_policy` field.
4. If a research claim is no longer valid, document why in the B2 README.

## Non-Goals

- B2 is not an external benchmark. External comparison requires an adapter
  decision (P1.3 in the weakness plan).
- B2 does not claim superiority over any other solver.
- B2 expected outputs are internal regression evidence, not public performance
  claims.

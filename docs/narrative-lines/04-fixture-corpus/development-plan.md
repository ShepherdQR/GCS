# 04 — Fixture and Counterexample Corpus

Status: active
Date: 2026-05-30
Parent map: `docs/architecture/95-gcs-narrative-map.md`

## Current Level

**Strong (4.0)**

## Current State

Verification, generated, milestone, showcase, and counterexample assets exist.
The corpus covers multiple fixture categories and is used in testing and demos.

## Main Gap

The corpus is not yet narrated as a maturity ladder. A new user cannot see
which fixtures represent basic capability vs. advanced stress tests.

## Evidence Artifact

`docs/architecture/96-fixture-corpus-maturity-ladder.md` and B1 expected
outputs.

## Promotion Gate

Promote a stable C2 seed toward B2 with expected report fields and migration
notes.

## Next Move

Define corpus levels and acceptance evidence per level.

## Development Plan

### Short-term (next 2-4 weeks)

1. Complete the fixture corpus maturity ladder
   (`docs/architecture/96-fixture-corpus-maturity-ladder.md`) with explicit
   levels: C1 (basic), C2 (intermediate), C3 (advanced), B1 (benchmark),
   B2 (microbenchmark).
2. Assign each existing fixture to a maturity level.
3. Define acceptance evidence required for a fixture to promote to the next
   level.

### Medium-term (4-8 weeks)

4. Promote one stable C2 fixture seed to B2: add expected report fields,
   migration notes, and version pinning.
5. Add a counterexample catalog that lists known failure modes and the fixture
   that exercises each.

### Long-term (8+ weeks)

6. Build a corpus health script that checks: every fixture loads, every
   expected output matches, no fixture is orphaned from its maturity level.
7. Integrate corpus health into CI or pre-commit quality gates.

## Dependencies

- Solver evidence (01): fixtures are the input to solver-evidence claims.
- Quality gates (07): corpus health checks are quality gates.
- External benchmark (13): B2 fixtures are shared between GCS benchmarks and
  external comparisons.

## Related

- Arc 1: Solver Evidence
- `docs/architecture/96-fixture-corpus-maturity-ladder.md`
- `fixtures/scene/`

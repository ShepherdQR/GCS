# 01 — Scientific Solver Thesis

Status: active
Date: 2026-05-30
Parent map: `docs/architecture/95-gcs-narrative-map.md`

## Current Level

**Strong (4.0)**

## Current State

Local-to-global semantics, reports, diagnostics, and obstruction vocabulary are
clear. The mathematical model, target module contracts, constraint and incidence
semantics, diagnostics, rank, residual, conflict, redundancy, and obstruction
reports are all in place.

## Main Gap

The "why users should care" story is less visible than the internal math story.
The solver evidence is strong internally but not yet translated into
user-visible demo scenarios.

## Evidence Artifact

CLI report evidence in D1/D2/D3 packages.

## Promotion Gate

Add a B2 microbenchmark that isolates one solver-semantics claim.

## Next Move

Attach solver evidence to user-facing demo scenarios.

## Development Plan

### Short-term (next 2-4 weeks)

1. Identify one solver-semantics claim (e.g., obstruction detection, rank
   reporting) that can be isolated into a B2 microbenchmark.
2. Write the B2-01 expected-output file that captures the exact expected report
   for that claim.
3. Tie the selected claim to an existing D1 or D2 demo scene so the demo path
   and the benchmark path both exercise it.

### Medium-term (next 4-8 weeks)

4. Add a B2-02 microbenchmark for a second solver-semantics claim (e.g.,
   redundancy detection, conflict set reporting).
5. Review whether the obstruction vocabulary is discoverable by a new reader;
   add glossary entries where needed.

### Long-term (8+ weeks)

6. Build a solver-evidence walkthrough that traces one scene through the full
   diagnostic pipeline: input → solve → rank → residual → obstruction → export.
7. Reference this walkthrough from README and demo ladder.

## Dependencies

- Fixture corpus (04): B2 microbenchmarks need stable fixtures.
- Runtime/replay evidence (05): report export and replay are the evidence
  delivery mechanism.

## Related

- Arc 1: Solver Evidence
- `docs/architecture/20-solver-pipeline/`
- `docs/architecture/30-contracts/`

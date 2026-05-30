# 12 — Release/Packaging/Onboarding

Status: active
Date: 2026-05-30
Parent map: `docs/architecture/95-gcs-narrative-map.md`
Weakness plan: `docs/agentic/narrative-weakness-development-plan-20260530.md`

## Current Level

**Strong but split (3.5)**

## Current State

A 20-minute contributor path, release-readiness checklist, R1 researcher-preview
note, package smoke automation, and D3 replay checker exist. R1 smoke and replay
checker are concrete.

## Main Gap

Reproducible build transcript and R2 release criteria are not yet consolidated.
A new user cannot verify that their build matches the expected behavior.

## Weakness Root Cause

Reproducible build and R2 criteria not consolidated.

## Evidence Artifact

R1 release note, R1 package smoke JSON, and D3 replay checker.

## Promotion Gate

Add reproducible build transcript and R2 criteria.

## Next Move

Add R2 reproducible build transcript and wire replay checker into the release
gate.

## Development Plan

### Phase 1: Close Smallest Feedback Loops (next 2-4 weeks)

1. Produce a dated build transcript at
   `docs/product/releases/artifacts/r2-build-transcript-YYYYMMDD.md`.
   Contents:
   - OS version, compiler version, CMake configuration, build command
   - Full build output (or representative excerpt for large output)
   - GCS.exe self-test output
   - A short note on what "reproducible" means at this stage (same toolchain →
     same binary behavior; full byte-for-byte reproducibility is not claimed).
2. Wire the D3 schema-aware replay checker into the R2 release-readiness
   checklist as a required gate.
3. Update `docs/product/release-readiness-checklist.md` with R2 criteria.

### Medium-term (4-8 weeks)

4. Add a "one-command release smoke" script that runs: build (if needed) →
   self-test → replay check → package smoke.
5. Test the 20-minute contributor path from a fresh clone and update it with
   any friction found.

### Long-term (8+ weeks)

6. Define R3 release criteria based on R2 feedback and external reviewer
   experience.
7. Consider CI automation for the release smoke script.

## Dependencies

- Runtime/replay (05): replay checker is an R2 gate component.
- Product/user (11): release quality affects reviewer experience.
- External benchmark (13): release stability affects benchmark reproducibility.

## Related

- Arc 4: Product And Adoption
- `docs/product/release-readiness-checklist.md`
- `docs/product/20-minute-contributor-path.md`
- `docs/agentic/narrative-weakness-development-plan-20260530.md` (P1.2)

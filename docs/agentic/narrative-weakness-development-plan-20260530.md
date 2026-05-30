# Narrative Weakness Development Plan

Status: active
Date: 2026-05-30
Baseline: `docs/architecture/70-visualization/narrative-line-level-baseline-20260530.md`

## Thesis

The GCS project is strong where it faces inward (solver, architecture, agentic
discipline) and weak where it faces outward (external feedback, reproducible
release, benchmark comparison, open-source contribution). This plan targets the
five weak lines with concrete, sequenced moves that do not require inflating
the process layer.

Principle: **translate existing evidence into external legibility before
creating new evidence types.**

## The Five Weak Lines

| # | Weak line | Current level | Root cause |
|---|-----------|--------------|------------|
| 11 | Product/user/market | Strong but split (3.5) | No actual external reviewer has touched the project. |
| 12 | Release/packaging/onboarding | Strong but split (3.5) | Reproducible build and R2 criteria not consolidated. |
| 13 | External benchmark/comparison | Strong but split (3.5) | No executable external baseline run exists. |
| 14 | Business/open-source strategy | Developing (3.0) | No real external contribution or review has landed. |
| E-GOV-001 | Governance eval execution | Developing (3.0) | Validator candidate not implemented despite exercised evidence. |

## Phase 1: Close the Smallest Feedback Loops (next 2-4 sessions)

These items are **actionable now** and do not depend on external people.

### P1.1 — Build E-GOV-001 Validator Candidate (L3)

**Why first**: This is the only weakness where the project controls all inputs
and outputs. Multiple scoped-staging examples exist. No external dependency.

**Acceptance**:
- A Python tool at `tools/governance/check_staged_scope.py` or similar.
- Compares `git diff --cached --name-only` against task-card affected paths.
- Returns PASS (all staged files in scope or explicit allowlist), FAIL (staged
  file outside scope with no allowlist entry), or SKIP (no task card found).
- Includes documented false-positive cases.
- A test that verifies detection of unrelated dirty-file staging.

**Risk**: Low. The tool is advisory, not a default gate. False positives are
acceptable per L3 policy.

### P1.2 — Add R2 Reproducible Build Transcript

**Why second**: Strengthens line 12 without external dependency. Uses existing
build infrastructure.

**Acceptance**:
- A dated build transcript at `docs/product/releases/artifacts/r2-build-transcript-YYYYMMDD.md`.
- Contains: OS version, compiler version, CMake configuration, build command,
  full build output (or representative excerpt for large output), GCS.exe
  self-test output.
- A short note on what "reproducible" means at this stage (same toolchain →
  same binary behavior; full byte-for-byte reproducibility is not claimed).

**Risk**: Low. Pure documentation from existing build process.

### P1.3 — Decide External Adapter Path

**Why third**: Unblocks line 13. The feasibility matrix and B2 review already
exist; this is the decision, not the implementation.

**Acceptance**:
- A short decision record choosing either SolveSpace (application-level
  comparison) or FreeCAD Sketcher (solver-level comparison) as the first
  external adapter target, or explicitly deferring with a dated rationale.
- If chosen: a one-paragraph scope for the adapter (what GCS scenes map to
  what external inputs, what outputs are compared).
- If deferred: what specific condition would trigger reconsideration.

**Risk**: Low. This is a decision document, not implementation.

## Phase 2: Seek External Feedback (next 4-8 weeks)

These items require finding or waiting for an external person. The plan is to
**prepare the packet perfectly** so that when a reviewer appears, the
turnaround is fast.

### P2.1 — Convert Review Packet Into Real Archive

**Acceptance**:
- A real external person (researcher, colleague, open-source contributor)
  reviews the R1 researcher preview.
- Their feedback (raw, attributed only with permission) is recorded at
  `docs/product/reviews/`.
- A short response note classifies feedback as: accepted (with task link),
  deferred (with trigger condition), or declined (with reason).
- The narrative map and metrics dashboard are updated.

**Fallback**: If no external reviewer appears within 8 weeks, downgrade this
target to "internal structured walkthrough with a fresh reader" and record
that as a provisional review with explicit caveats.

### P2.2 — First External Contribution Workflow

**Acceptance**:
- A real external person submits a PR, issue, or email patch.
- The contribution boundary doc is tested against this real case.
- Any friction in the contributor path is recorded as an experience note.
- The PR is reviewed, merged or declined, and the outcome archived.

**Fallback**: If no external contribution appears, simulate one by having an
internal contributor follow the 20-minute contributor path from a fresh clone
and record every friction point.

## Phase 3: Benchmark Execution (next 4-12 weeks)

### P3.1 — Run First External Baseline

**Precondition**: P1.3 (adapter decision) is complete.

**Acceptance**:
- An external solver (SolveSpace or FreeCAD Sketcher) is run on a subset of
  GCS fixtures or a common benchmark scene.
- The output is compared against GCS output on the same scene.
- A comparison note (not a benchmark claim) records: what was compared, what
  was comparable, what was not, and what differences mean.
- The note lives at `docs/architecture/benchmarks/` with links to raw outputs.

**Risk**: Medium. External solver behavior may differ for legitimate
mathematical reasons. The output must be a comparison note, not a score.

### P3.2 — Add B2 Expected-Output Files

Status: Complete (2026-05-30).

**Acceptance**:
- [x] Expected output files for B2-01 and B2-02 microbenchmarks.
- [x] Format follows B1 conventions.
- [x] Each file links to the solver version and fixture version that produced it.

## Phase 4: Open-Source Maturation (beyond 12 weeks)

### P4.1 — Public Distribution Decision

**Precondition**: At least one real external review (P2.1) and one external
contribution (P2.2) exist.

**Acceptance**:
- A decision record on whether to make the repository public, keep it
  researcher-access-only, or adopt a staged release model.
- If public: license confirmation, README expansion, CONTRIBUTING.md, and
  issue template.

### P4.2 — Live Workbench Walkthrough

**Precondition**: Viewer evidence projection is ready (structured report
projection in viewer bridge).

**Acceptance**:
- A recorded or documented walkthrough of D5 Solver Evidence Workbench.
- Shows: load scene → solve → inspect diagnostics → replay history → export
  evidence.
- The walkthrough is referenced from README and demo ladder.

## Dependency Graph

```text
P1.1 (E-GOV-001)          ← independent, start immediately
P1.2 (R2 build)           ← independent, start immediately
P1.3 (adapter decision)   ← independent, start immediately
P3.1 (external baseline)  ← depends on P1.3
P3.2 (B2 outputs)         ← independent, can run any time
P2.1 (real review)        ← depends on external person availability
P2.2 (contribution)       ← depends on external person availability
P4.1 (public distribution)← depends on P2.1 + P2.2
P4.2 (live walkthrough)   ← depends on viewer projection readiness
```

## Anti-Patterns To Avoid

1. **Creating more process docs because external progress is slow.**
   The response to "no external reviewer" is not another internal narrative
   document — it's the fallback (internal structured walkthrough).

2. **Overclaiming benchmark results.**
   Every external comparison must use the language of "difference" and
   "observation," not "superiority" or "score."

3. **Rushing to public before feedback loops exist.**
   Making the repo public before at least one real external review exists
   turns "strong but split" into "public but unverified."

4. **Treating E-GOV-001 as optional because it's "only governance."**
   Governance validators are the immune system of the agentic organization.
   Without one working validator, all governance docs are aspirational.

## Update Rule

Update this plan when:
- Any phase completes or a precondition changes.
- A new external person interacts with the project.
- A fallback is activated.
- The narrative map weakness analysis is refreshed.

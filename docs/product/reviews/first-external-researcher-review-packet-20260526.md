# First External Researcher Review Packet

Status: ready for external review
Date: 2026-05-27 (polished 2026-05-27)
Primary audience: solver and geometric-constraint researchers

## Executive Summary

GCS is a research workbench for geometric constraint solving. It does not claim
to be production CAD software. Its differentiator is *inspectable solver
evidence*: when you load a scene and solve it, GCS produces structured reports
about rank, residuals, constraint conflicts, redundancies, and obstructions —
not just coordinates. The pipeline is local-to-global: decomposition, local
numeric solves, diagnostics, gluing, and commit. Every stage leaves a report
trace.

This packet asks you to verify one narrow claim: that a technically strong
researcher can understand and inspect GCS's current evidence route without
access to raw development chat logs or internal context.

For context on what GCS currently considers its strongest and weakest narrative
lines, see the accompanying analysis:
[`docs/architecture/99-narrative-weakness-analysis-20260527.md`](../architecture/99-narrative-weakness-analysis-20260527.md).

## Before You Start

### Prerequisites

| Requirement | Minimum | Verified with |
|---|---|---|
| Operating system | Windows 10/11 x64 | Windows 11 |
| C++ compiler | Clang 18+ with C++23 modules support | Clang 19.1.0 |
| Build system | CMake 3.28+ + Ninja | CMake 3.30 + Ninja 1.12 |
| Python | 3.11+ | Python 3.12 |
| Python packages | `pip install -r python/requirements.txt` | matplotlib, numpy |
| Disk space | ~500 MB for build artifacts | — |
| Time | ~30 minutes for full build + review | — |

### One-Time Build

Before any demo steps, build the solver:

```bat
scripts\build_clang_ninja.cmd
```

This produces `out/build/clang-ninja/GCS.exe`. All subsequent commands assume
this path.

### Troubleshooting

- **Build fails with module errors**: Ensure Clang version is 18+. Older Clang
  releases have incomplete C++23 module support.
- **Python import errors**: Run `python -m pip install -r python/requirements.txt`.
- **GCS.exe not found**: The build may have failed silently. Check
  `out/build/clang-ninja/` for `GCS.exe`. If absent, re-run the build script
  and inspect console output.
- **Replay evidence save fails**: Ensure the target directory exists and is
  writable.

## Review Route (estimated 25-35 minutes after build)

### Step 1: Project Orientation (~5 min)

Read these two documents to understand what GCS claims and how it is organized:

- `README.md` (top of repository)
- [`docs/architecture/95-gcs-narrative-map.md`](../architecture/95-gcs-narrative-map.md)

After reading, you should be able to state:
- The one-sentence project thesis.
- The four narrative arcs and which are strongest.
- The target module vocabulary (kernel, incidence_graph, diagnostics, etc.).

### Step 2: D1 CLI Smoke (~3 min)

Run the basic solver on a small scene:

```bat
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt
```

Expected: `Status: AcceptedWithWarnings`, `Accepted: true`, rank and residual
report lines visible in console output.

Full walkthrough: [`docs/product/demos/d1-cli-smoke/`](demos/d1-cli-smoke/).

### Step 3: D2 Diagnostic Classification (~5 min)

Run the diagnostic classifier across well-constrained, under-constrained,
over-constrained, and malformed scenes:

```bat
python tools\product_demo\diagnostic_classification.py
```

This produces a structured JSON summary. Inspect whether each scene's reported
status matches its known classification.

Full walkthrough: [`docs/product/demos/d2-diagnostic-classification/`](demos/d2-diagnostic-classification/).

### Step 4: D3 Replay Evidence (~5 min)

Save replay evidence as a structured JSON artifact:

```bat
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt --save-replay-evidence docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.report.json
```

Then run the schema-aware checker:

```bat
python tools\product_demo\replay_evidence_check.py --input docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.report.json --output docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.check.json
```

Expected: `17/17 checks passed`.

Full walkthrough: [`docs/product/demos/d3-replay-evidence/`](demos/d3-replay-evidence/).

### Step 5: D5 Static Workbench (~5 min)

Inspect the Solver Evidence Workbench static package. This is a screenshot
baseline, not a live GUI — it shows the target UI direction.

Open [`docs/product/demos/d5-solver-evidence-workbench/`](demos/d5-solver-evidence-workbench/)
and review `evidence.md` plus the screenshot artifacts.

Note: D5 is *not* a live interactive workbench. The "live workbench walkthrough"
remains a future milestone gated on structured report projection from C++ into
the Python viewer.

### Step 6: External Baseline Feasibility (~3 min)

Review how GCS positions itself against other solvers:

[`docs/architecture/benchmarks/external-baseline-feasibility-matrix.md`](../architecture/benchmarks/external-baseline-feasibility-matrix.md)

This matrix classifies each external baseline as executable, source-available,
documentation-only, or commercial/proprietary — without claiming benchmark
results that don't exist yet.

### Step 7: B2 Microbenchmark Candidates (~3 min)

Review which B1 cases are promoted to B2 candidates:

[`docs/architecture/benchmarks/b2-microbenchmark-candidate-review.md`](../architecture/benchmarks/b2-microbenchmark-candidate-review.md)

Each candidate is promoted, deferred, or rejected with a research question and
missing evidence.

## Questions For The Reviewer

| # | Question | Desired feedback |
|---|---|---|
| 1 | Is the solver-evidence thesis legible without a GUI? | Missing evidence types, confusing terminology, or framing that could be stronger. |
| 2 | Are D1, D2, and D3 sufficient to justify a researcher-preview route? | The single most important artifact or check still missing before wider sharing. |
| 3 | Which B2 candidate (B2-01 or B2-02) is more scientifically useful? | Candidate ranking with rationale and expected report fields. |
| 4 | Which external baseline should be attempted first? | SolveSpace executable, FreeCAD Sketcher source, or documentation-only comparison. |
| 5 | Does the D5 static workbench package clarify the target UI direction? | Whether the evidence hierarchy, visual clarity, and live-GUI caveats are convincing. |
| 6 | What is the single biggest gap between the README researcher route and your actual experience following it? | Concrete friction: missing command, unclear output, wrong expectation, broken path. |

## Non-Claims

- GCS is not presented as production CAD software.
- D5 is not presented as a live GUI workflow.
- No external executable benchmark result is claimed.
- Siemens D-Cubed is an industry reference, not a reproducible benchmark.
- This packet is not an endorsement or external review result.
- The project does not claim that its current solver implementation is complete.

## Expected Archive Shape After Review

When real feedback arrives, create:

```text
docs/product/reviews/feedback/YYYY-MM-DD-<reviewer-context>-review.md
```

Minimum fields for the feedback archive:

- Reviewer context (role, background, relationship to project).
- Artifact route used (which steps were followed).
- Feedback received (verbatim or summarized).
- Accepted follow-up (what the project will change based on feedback).
- Rejected or deferred follow-up (what the project considered but will not act on).
- Evidence updated (which artifacts, docs, or tests changed).
- Whether the review changes any Narrative Map levels (see `docs/architecture/95-gcs-narrative-map.md`).

## Current Status

This packet has been polished for standalone legibility (2026-05-27) but has not
yet been sent to any external researcher. The next action is to identify 1-2
candidate reviewers and send this packet.

## Related Documents

- [`docs/architecture/95-gcs-narrative-map.md`](../architecture/95-gcs-narrative-map.md) — All 13 narrative lines, levels, gaps, and next moves.
- [`docs/architecture/99-narrative-weakness-analysis-20260527.md`](../architecture/99-narrative-weakness-analysis-20260527.md) — The five most critical weaknesses and their development plans.
- [`docs/product/gcs-product-user-brief.md`](gcs-product-user-brief.md) — Target users, jobs-to-be-done, and must-not-fail properties.
- [`docs/product/gcs-demo-ladder.md`](gcs-demo-ladder.md) — D0 through D7 demo progression.
- [`docs/product/researcher-audience-strategy.md`](researcher-audience-strategy.md) — Why researchers are the primary audience.
- [`docs/product/researcher-contribution-boundary.md`](researcher-contribution-boundary.md) — What contributions fit GCS's current maturity.

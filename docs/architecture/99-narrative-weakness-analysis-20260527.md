# GCS Narrative Weakness Analysis And Development Plan

Status: active
Date: 2026-05-27
Primary source: `docs/architecture/95-gcs-narrative-map.md`

## Purpose

This document distills the narrative-line weakness analysis from the 2026-05-27
session into a durable architecture note. It identifies the five most critical
shortcomings across GCS's four narrative arcs and defines an executable
development plan for each. It is meant to be read alongside the Narrative Map
(`95-gcs-narrative-map.md`) and should be refreshed when promotion gates close.

## Overall Diagnosis

GCS's four narrative arcs are asymmetrically mature:

| Arc | Maturity | Core characteristic |
|---|---|---|
| Arc 3: Agentic Organization | **Strongest** | Lifecycle runbook, quality gates, institutional agents, governance evals, and evidence culture are all operational. |
| Arc 1: Solver Evidence | **Strong** | 51 implementation steps, module contracts, diagnostics, replay evidence, and fixture corpus form a coherent chain. |
| Arc 2: Evidence Workbench | **Medium** | UI tokens, visual QA, and screenshot baselines exist, but the workbench is a static package — no live interactive diagnostic workflow. |
| Arc 4: Product & Adoption | **Weakest** | Roadmap, demo ladder, and review packet exist, but there is zero external researcher feedback and no reproducible build transcript for R2. |

This asymmetry is natural for a research project — internal engineering
maturates before external legibility. The key insight from the Narrative Map is:

> "The next plan should not primarily add more internal architecture language.
> It should translate the existing architecture into evidence packages that a
> new user, reviewer, or future contributor can run, compare, and trust."

## Five Weaknesses (Priority Order)

### Weakness 1: External Feedback Vacuum

**Current state**: The product/user story line is scored 3.5 ("Strong but
split"). D1-D5 demo packages, the researcher review packet, and the README
route exist, but none have been exercised by an actual external researcher.
Every "external review" promotion gate remains a TODO.

**Why it matters**: Without external signal, the project's entire narrative runs
in a closed loop. The team cannot know whether the research direction is
compelling, whether the evidence workbench interaction model makes sense to real
users, or whether benchmark comparisons are convincing.

**Evidence of gap**:
- `docs/product/reviews/first-external-researcher-review-packet-20260526.md`
  exists but has never been sent.
- Trend note explicitly records: "true external feedback is still missing."

**Development plan**:
1. Review and polish the existing researcher review packet for standalone
   legibility.
2. Identify 1-2 candidate external researchers (academic collaborators or
   open-source community members).
3. Send the packet and create a feedback archive at
   `docs/product/reviews/feedback/`.
4. Treat the first external response as a promotion gate for the product/user
   narrative line.

### Weakness 2: Thin C++ Solver Core

**Current state**: The solver has 10 modules totaling 9,134 lines (7,239
implementation + 1,895 interface), but module maturity varies sharply:

| Module | Lines | Assessment |
|---|---|---|
| `io_adapters` | 1,339 | Relatively complete |
| `numeric_engine` | 941 | Damped Gauss-Newton only; no sparse solver, no manifold retraction |
| `constraint_catalog` | 827 | Adequate for current scope |
| `contract_tools` | 667 | Adequate |
| `session_runtime` | 653 | Adequate |
| `viewer_bridge` | 642 | C++ side complete; Python side not consuming |
| `kernel` | 638 | Adequate as domain model |
| `diagnostics` | 620 | Adequate |
| `decomposition_planner` | 561 | SolveDAG exists but no hierarchical decomposition |
| `incidence_graph` | 351 | Self-described as "connected-component decomposition prototype" |

The 51-step implementation history is distributed unevenly: many steps refined
scene-generation, promotion gates, and viewer bridge infrastructure, while core
algorithm modules (incidence graph, planner, numeric engine) received less
deepening.

**Why it matters**: The mathematical thesis — local-to-global solving with
certificate-like evidence — depends on structural graph decomposition. The
current incidence_graph module is explicitly a prototype.

**Evidence of gap**:
- README: "current connected-component decomposition prototype"
- `docs/research/20260525/lgs-spanning-tree/` contains 5 detailed implementation
  design documents for LGS-style structural decomposition that have not been
  implemented.

**Development plan**:
1. Implement LGS spanning tree structural decomposition in
   `src/gcs/incidence_graph/`, following the existing research design in
   `docs/research/20260525/lgs-spanning-tree/`.
2. Upgrade `decomposition_planner` to consume spanning-tree evidence for
   hierarchical decomposition.
3. Add contract tests for spanning tree detection, well-constrained component
   identification, and decomposition boundary evidence.
4. Use `fixtures/scene/basic/g1.txt` and generated scenes as verification
   inputs.

### Weakness 3: Live Evidence Workbench Missing

**Current state**: D5 Solver Evidence Workbench is a static screenshot package
— PNG files that pass screenshot-baseline QA. The architecture docs explicitly
note it "should not be described as a complete GUI implementation." Meanwhile,
the C++ `viewer_bridge` module already exposes structured diagnostic evidence:
`ReplayEvidenceSummary`, `RankEvidenceProjection`, `DiagnosticOverlay` with
residual/conflict/redundancy/obstruction evidence items (Steps 31-38).

**Why it matters**: The most compelling evidence for external researchers —
interactive diagnostic visualization — remains inaccessible. The bridge from
C++ evidence to Python GUI rendering exists on the C++ side but is not consumed.

**Evidence of gap**:
- D5 package: `docs/product/demos/d5-solver-evidence-workbench/artifacts/` —
  static PNG only.
- "Live workbench walkthrough" deferred in Narrative Map next-task queue item 5
  with condition "only after structured report projection is ready" — but Steps
  31-38 completed structured report projection on the C++ side.
- `python/gcs_viz/` has not been updated to consume the new viewer_bridge
  diagnostic surfaces.

**Development plan**:
1. Extend `python/gcs_viz/viewer_bridge.py` facede to expose
   `ReplayEvidenceSummary`, `RankEvidenceProjection`, and `DiagnosticOverlay`.
2. Add diagnostic overlay rendering to `python/gcs_viz/visualizer.py`.
3. Wire the "Load → Solve → Inspect Diagnostics" workflow end-to-end.
4. Capture a live screenshot as the first non-static D5 evidence artifact.

### Weakness 4: Governance Evals Not Engineered

**Current state**: Three governance eval seeds exist:
- E-GOV-001: refuse-unrelated-dirty-file-staging
- E-GOV-002: refuse-audit-approval-overclaim
- E-GOV-008: refuse-agent-promotion-overclaim

Exercised evidence was recorded in
`docs/agentic/evals/governance/exercised-evidence-20260526.md`, but no validator
candidate has been implemented. "Build E-GOV-001 validator candidate" appears
repeatedly in next-step queues across multiple planning documents without being
executed.

**Why it matters**: Governance evals that exist only as prompt-level instructions
rely entirely on AI self-discipline. Without automated validators, quality gates
cannot detect governance violations. The gap between "we have eval seeds" and
"we have enforceable checks" is the difference between aspiration and mechanism.

**Evidence of gap**:
- Narrative Map next task queue item 2: "Build an E-GOV-001 validator candidate
  for scoped staging evidence."
- Trend note next strengthening target 2: same item.
- Third-stage plan lists governance eval promotion as Step 6 but records only
  "exercised evidence" — no validator code.

**Development plan**:
1. Create `tools/governance/check_staged_scope.py`: a script that compares
   `git diff --cached --name-only` against a task card's declared file scope.
2. Create `tests/tools/test_check_staged_scope.py` with positive (clean scope)
   and negative (scope violation) test cases.
3. Document the validator in the E-GOV-001 eval spec.
4. Optionally integrate into `run-quality-gates` as a non-blocking advisory gate.

### Weakness 5: Reproducible Build And R2 Release

**Current state**: R1 preview exists with smoke automation
(`docs/product/release-readiness-checklist.md`). D3 replay checker validates
schema. But R2 release criteria — reproducible build transcript, deterministic
binary hash, release-gate contract — are not consolidated.

**Why it matters**: External researchers cannot independently verify build
results. Benchmark comparisons require trusted binary artifacts. The release
pipeline is a key part of the "evidence-rich" thesis: if the solver itself
cannot be reproducibly built, its output evidence is harder to trust.

**Evidence of gap**:
- Narrative Map: "Reproducible build transcript and R2 release criteria are not
  yet consolidated."
- Trend: Release/packaging moved from 3.0 to 3.5 after D3 replay checker, but
  "reproducible build transcript is still missing."
- No `docs/product/r2-build-transcript.md` exists.

**Development plan**:
1. Execute a clean build from `git clone` through `GCS.exe` and record every
   step in `docs/product/r2-build-transcript.md`.
2. Document environment requirements (Clang version, Ninja version, CMake
   version, Windows SDK).
3. Record expected build output hash for the GCS.exe binary.
4. Update `docs/product/release-readiness-checklist.md` with R2 criteria.

## Execution Order

| Sequence | Task | Primary output | Depends on |
|---|---|---|---|
| 1 | Persist this analysis | `docs/architecture/99-narrative-weakness-analysis-20260527.md` | None |
| 2 | Polish external review packet | Updated `docs/product/reviews/` | 1 |
| 3 | LGS spanning tree C++ implementation | Updated `src/gcs/incidence_graph/`, `decomposition_planner/` | 1 |
| 4 | Python GUI diagnostic evidence integration | Updated `python/gcs_viz/` | 3 |
| 5 | E-GOV-001 validator candidate | New `tools/governance/` | 1 |
| 6 | R2 reproducible build transcript | New `docs/product/r2-build-transcript.md` | 1 |

Tasks 3 and 5 can proceed in parallel after task 1. Task 4 depends on task 3
(because the C++ evidence surfaces must be confirmed stable before Python
consumption). Tasks 2 and 6 are documentation-heavy and can proceed in parallel
with the code tasks.

## Verification

After each task:
```bat
python tools\agentic_design\agentic_toolkit.py run-quality-gates
```

After code tasks (3, 4, 5):
```bat
scripts\build_clang_ninja.cmd
ctest --test-dir out\build\clang-ninja
```

## Relationship To Narrative Map

This document is a tactical supplement to `docs/architecture/95-gcs-narrative-map.md`.
The Narrative Map defines the 13 narrative lines, their levels, gaps, and next
moves. This document selects the five highest-leverage weaknesses and turns them
into executable work items. When any of these five tasks close, update both the
Narrative Map promotion gates and this document's status.

## Execution Results (2026-05-27 Session)

| Task | Status | Evidence |
|---|---|---|
| 1. Persist this analysis | Done | This document. |
| 2. Polish review packet | Done | Added executive summary, prerequisites, time estimates, troubleshooting. |
| 3. LGS spanning tree M1 | Done | Types + functions in `incidence_graph` and `decomposition_planner`; deterministic Kruskal forest, BFS orientation, constraint partition; all 115 CTest pass. |
| 4. Python GUI evidence | Done | `parse_replay_evidence_report()` and `format_evidence_summary()` in `viewer_bridge.py`; `solve_with_evidence()` in `engine_bridge.py`; end-to-end JSON chain verified. |
| 5. E-GOV-001 validator | Done | `tools/governance/check_staged_scope.py` + 14 passing tests. |
| 6. R2 build transcript | Done | `docs/product/r2-build-transcript.md` with env, steps, SHA-256, R2 criteria checklist. |

## Remaining Plan

### Phase A: External Signal (highest leverage, requires real human)

| # | Task | Narrative line | Blocked by |
|---|---|---|---|
| A1 | Send review packet to 1-2 real researchers | Product/user, Release, Benchmark, Business | Finding reviewers |
| A2 | Archive first external feedback | Product/user | A1 |
| A3 | Update Narrative Map promotion gates based on feedback | All external-facing lines | A2 |

### Phase B: Solver Algorithm Deepening (LGS M2-M7)

| # | Task | Narrative line | Priority |
|---|---|---|---|
| B1 | M2: Pattern catalog v0 (1-3 safe patterns) | Solver thesis | After M1 tests |
| B2 | M3: Spanning tree fixture corpus (8 fixtures) | Fixture corpus | After B1 |
| B3 | M4: Reduced NumericTask prototype (opt-in) | Solver thesis, Numeric engine | After B2 |
| B4 | B2 expected-output files for B2-01, B2-02 | Benchmark, Fixture corpus | Independent |
| B5 | Decide SolveSpace/FreeCAD external adapter path | External benchmark | Independent |

### Phase C: Live Evidence Workbench

| # | Task | Narrative line | Priority |
|---|---|---|---|
| C1 | Wire parsed evidence into GUI solve panel | UI/Viewer | High — builds on Task 4 |
| C2 | D5 live workbench walkthrough (full solve→diagnostics→replay in GUI) | Product/user | After C1 |
| C3 | Structured report projection from C++ to Python viewer | UI/Viewer | After C2 |

### Phase D: Governance Engineering

| # | Task | Narrative line | Priority |
|---|---|---|---|
| D1 | Integrate E-GOV-001 into quality-gates as advisory | Governance eval | High |
| D2 | E-GOV-002 validator candidate (refuse-audit-approval-overclaim) | Governance eval | After D1 |
| D3 | Metrics dashboard trend update after non-trivial closure | Quality gates | Trigger-based |

### Phase E: Release & Distribution

| # | Task | Narrative line | Priority |
|---|---|---|---|
| E1 | Wire replay checker into R2 release gate | Release/packaging | Medium |
| E2 | Verify build transcript on second machine | Release/packaging | Needs second researcher |
| E3 | Contribution workflow example | Business/open-source | After A2 |

## Review Triggers

Refresh this analysis when:
- An external researcher provides feedback on the review packet.
- LGS spanning tree implementation passes contract tests.
- Python GUI displays live diagnostic evidence.
- E-GOV-001 validator produces its first refusal.
- R2 build transcript is verified in a clean environment.

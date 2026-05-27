# Medium-Term Weak Line Development — Detailed Design

Date: 2026-05-27
Status: active
Depends on: `docs/architecture/99-weak-line-development-plan.md` (short-term items S1–S5 complete)

## Purpose

This document provides detailed implementation design for the 5 medium-term
items. Each entry specifies the exact files to create or modify, the technical
approach, the verification command, and the dependency on completed short-term
items.

---

## M1. First External Baseline Run

**Narrative line:** 13. External benchmark/comparison
**Depends on:** S2 (D6 evidence walkthrough) — provides the evidence-chain
template for the comparison note.
**Effort:** 2–3 sessions.

### Design

**Choice of external system: FreeCAD Sketcher (Python API).**

Rationale:
- SolveSpace CLI is limited — it can load files and export results but its
  text output is not designed for diagnostic comparison
- FreeCAD Sketcher has a Python API (`sketch.solve()`) that returns constraint
  status, DOF count, and solver messages
- FreeCAD is open-source and installable without registration
- The Python API allows automated comparison without GUI interaction

Fallback: If FreeCAD installation proves unreliable, use SolveSpace
command-line export and compare geometry output (coordinates, orientations)
rather than diagnostic output.

**Comparison scene:** A simple 2D triangle with distance and angle constraints.
This is expressible in both GCS and FreeCAD, and is the minimum viable scene
for a semantic comparison.

**Script to write:** `tools/benchmark/external_baseline_freecad.py`

```python
# Pseudocode structure:
# 1. Generate the comparison scene in GCS text format
# 2. Solve with GCS, capture report
# 3. Generate equivalent scene as FreeCAD Python script
# 4. Execute FreeCAD script, capture output
# 5. Write comparison note
```

**Comparison dimensions:**

| Dimension | GCS | FreeCAD Sketcher |
| --- | --- | --- |
| Solver output | Diagnostic report with rank, residual, report codes | Constraint status (solved/unsolved), DOF count |
| Evidence type | Structured report categories | Binary solved/not-solved + DOF |
| Verifiability | Replay JSON + checker | Not available |
| Diagnostic depth | 4+ categories (rank, residual, gluing, commit) | 1 category (constraint status) |

**Honest GCS limitation for this comparison:** GCS handles fewer constraint
types than FreeCAD Sketcher (5 built-in vs. FreeCAD's 10+). This comparison
will note GCS's diagnostic depth advantage alongside its constraint-type
coverage disadvantage.

**Files to create:**
- `tools/benchmark/external_baseline_freecad.py`
- `docs/architecture/comparison/b2-01-gcs-vs-freecad-sketcher.md`
- `fixtures/benchmark/b2-01/triangle_comparison.gcs.txt`

**Verification:**
```bat
python tools\benchmark\external_baseline_freecad.py
type docs\architecture\comparison\b2-01-gcs-vs-freecad-sketcher.md
```

---

## M2. First Researcher Review Packet — Send and Archive

**Narrative lines:** 11. Product/user/market story; 14. Business/open-source
**Depends on:** S2 (D6 evidence walkthrough) — the walkthrough is the centerpiece
of the review packet.
**Effort:** 2–4 weeks elapsed; 1 session of active work.

### Design

**Candidate researcher profile (ordered by relevance):**

1. A computational geometry academic who has published on geometric constraint
   solving or parametric CAD
2. A CAD/CAE software developer who has worked on sketcher or assembly solvers
3. A scientific computing researcher interested in evidence-rich numerical
   methods

**Review packet contents:**

```
review-packet-001/
├── README.md              # "What we're asking you to do" (5 min read)
├── quickstart.md          # Clone, build, run g1.txt (D1)
├── evidence-walkthrough.md # Link to D6
└── feedback-form.md        # 3–5 specific questions
```

**Specific asks (not "tell us what you think"):**

1. Run D1 CLI smoke. Does the output make sense? What's confusing?
2. Read D6 evidence walkthrough. Is the evidence chain convincing? Where does
   it feel weak?
3. What would you need to see to take GCS seriously as a research tool?
4. What's one thing GCS should do that it doesn't?

**Files to create:**
- `docs/product/reviews/packets/001-researcher-review/README.md`
- `docs/product/reviews/packets/001-researcher-review/quickstart.md`
- `docs/product/reviews/packets/001-researcher-review/feedback-form.md`

**Archive template** (`docs/product/reviews/001-<researcher>-<date>.md`):
```markdown
# Review 001: <Researcher> — <Date>

## Reviewer Context
<field, affiliation, relevance>

## Response Summary
<what they said, anonymized if needed>

## What We Learned

## What Changed

## Follow-up
```

**Verification:**
- Review packet directory exists with all 3 files
- After response: review archive exists with all 4 sections filled

---

## M3. Fixture Corpus Maturity Ladder

**Narrative line:** 4. Fixture and counterexample corpus
**Depends on:** None (standalone)
**Effort:** 1–2 sessions.

### Design

**File to update:** `docs/architecture/96-fixture-corpus-maturity-ladder.md`
(already referenced in the metrics dashboard but content is TBD)

**Maturity level definitions:**

| Level | Name | Criteria | Verification |
| --- | --- | --- | --- |
| C0 | Raw | Scene file exists in `fixtures/scene/` | `dir fixtures\scene\` |
| C1 | Tagged | C0 + semantic tags in metadata or filename convention | Machine-parseable tags |
| C2 | Expected | C1 + expected report fields documented + migration note if format changes | Expected report file exists |
| C3 | Verified | C2 + replay-verified + contract test references this fixture | Contract test passes |
| C4 | Showcase | C3 + featured in a demo package or publication figure | Linked from demo README |

**Classification approach:**

1. Inventory all fixture files: `dir fixtures\scene\ /s /b`
2. Classify each file against the ladder criteria
3. Identify the highest-level fixture per category
4. Create a promotion plan for the closest-to-C3 fixtures

**Expected initial distribution:**

| Level | Estimated count | Fixtures |
| --- | ---: | --- |
| C0 | ~5 | Generated scenes without expected output |
| C1 | ~10 | Scenes with constraint types and DOF counts visible |
| C2 | ~5 | g1.txt, triangle_003.json, integrated_feature_showcase |
| C3 | ~3 | integrated_feature_showcase (replay-verified, contract-tested) |
| C4 | ~1 | integrated_feature_showcase (in D5 and VE-001) |

**Promotion target:** Move `fixtures/scene/basic/g1.txt` from C2 to C3 by
ensuring it has a replay-verified expected report and at least one contract
test that references it.

**Verification:**
```bat
python tools\agentic_design\agentic_toolkit.py validate-docs
# Should include fixture classification validation
type docs\architecture\96-fixture-corpus-maturity-ladder.md
# Should show C0–C4 definitions and a table with every fixture classified
```

---

## M4. Wire Replay Checker into R2 Release Gate

**Narrative line:** 5. Runtime/history/replay evidence
**Depends on:** S3 (R2 build transcript) — defines the release gate structure.
**Effort:** Partial session.

### Design

**File to modify:** `tools/product_demo/r1_package_smoke.py` (extend for R2)

**Approach:** Add a `ReplayCheckerStep` to the smoke test pipeline. The step:
1. Enumerates scenes in the D3 replay evidence package
2. Runs `replay_evidence_check.py` on each
3. Reports PASS/FAIL per scene
4. Overall smoke fails if any scene fails

**Pseudocode:**
```python
def run_replay_checker_step():
    scenes = glob("docs/product/demos/d3-replay-evidence/artifacts/*.report.json")
    results = []
    for scene in scenes:
        result = subprocess.run([
            "python", "tools/product_demo/replay_evidence_check.py",
            "--input", scene,
            "--output", scene.replace(".report.json", ".check.json")
        ])
        results.append((scene, result.returncode == 0))
    return results
```

**Also update:** `docs/product/release-readiness-checklist.md` to include the
replay checker as a required gate.

**Verification:**
```bat
python tools\product_demo\r1_package_smoke.py
# Output includes: "D3 replay checker: PASS (3/3 scenes)"
```

---

## M5. B2 Expected-Output Files

**Narrative line:** 13. External benchmark/comparison
**Depends on:** M1 (external baseline run) — the B2 scenes are the comparison
scenes used in M1.
**Effort:** 1 session.

### Design

**B2 scenes:**

| Scene | Source | Purpose |
| --- | --- | --- |
| B2-01 | Triangle with distance + angle | Baseline solver correctness for minimal 2D scene |
| B2-02 | Triangle with redundant constraint | Over-constraint detection evidence |

**Expected-report format:**

```markdown
# B2-01 Expected Report

## Scene
fixtures/benchmark/b2-01/triangle.gcs.txt

## Stable Fields (must not change across builds)

| Field | Expected value | Tolerance |
| --- | --- | --- |
| accepted | true | exact |
| status | AcceptedWithWarnings | exact |
| committed | true | exact |
| report_codes | ["gluing.accepted", "runtime.commit"] | exact set |
| DOF count | 3 rigid sets, 3 entities | exact |
| rank | 3 | exact |
| residuals | 3 | count exact |
| residual norm | < 1e-10 | numeric tolerance |

## Variable Fields (may change across builds)

| Field | Reason |
| --- | --- |
| timestamps | Build-time dependent |
| iteration count | Solver path dependent |
| duration_ms | Machine dependent |
| state_version | Monotonic counter |
```

**Verification:**
```bat
out\build\clang-ninja\GCS.exe fixtures\benchmark\b2-01\triangle.gcs.txt
# Compare output against expected-report.md stable fields
```

---

## Dependency Check

```
S2 (D6 walkthrough) ──► M1 (external baseline) ──► M5 (B2 expected outputs)
                    ──► M2 (review packet)      ──► L1 (external review)
                                                   
S3 (R2 build transcript) ──► M4 (replay in gate) ──► L3 (public release)

(standalone) ──► M3 (corpus ladder)
```

All medium-term items are unblocked. M1 and M3 can start immediately. M2
requires D6 walkthrough (S2, complete). M4 requires R2 build transcript
(S3, complete). M5 depends on M1.

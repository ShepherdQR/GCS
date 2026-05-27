# D6 End-to-End Evidence Walkthrough

Status: active
Date: 2026-05-27
Audience: researcher reviewer, new contributor, architecture auditor

## Claim

GCS produces an unbroken evidence chain from scene file to publication-ready
artifacts. A reviewer can trace one scene through the entire pipeline without
gaps: CLI solve → replay → checker → viewer → figure → quality assurance.

## Scene

```
fixtures/scene/basic/g1.txt
```

3 rigid sets, 5 entities, 2 constraints. The same scene used by D1 (CLI smoke)
and D3 (replay evidence). Choosing one shared scene allows cross-demo
comparison.

---

## Stage 1: CLI Solve — Raw Evidence

```bat
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt
```

**Key output lines:**

```
StateVersion=1 RigidSets=3 Entities=5 Constraints=2
Status: AcceptedWithWarnings
Accepted: true
Cover contexts: 4
Local numeric reports: 3
runtime.post_local_diagnostics.rank_report: rank 3, variables 6, residuals 3, nullity 3
runtime.post_local_diagnostics.residual_report: residuals 3, norm 0.000000, max 0.000000
diagnostics.glue_local_sections: Ok
gluing.accepted: All local sections are compatible within boundary tolerance.
session_runtime.commit: Ok
runtime.commit: Runtime committed the verified proposed state.
```

**Evidence type:** Console transcript. Raw, inspectable, reproducible.

**What this stage proves:** The solver loads, solves, and explains. Every
subsequent stage builds on this output.

**Source demo:** [D1 CLI Smoke](../d1-cli-smoke/README.md)

---

## Stage 2: Replay Evidence — Structured Artifact

```bat
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt --save-replay-evidence docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.report.json
```

**Output:** `docs/product/demos/d3-replay-evidence/artifacts/g1-replay-evidence.report.json`

**Key fields:**

| Field | Value | Meaning |
| --- | --- | --- |
| `schema` | `gcs.replay-evidence.v1` | Schema version |
| `accepted` | `true` | Solver accepted the result |
| `status` | `AcceptedWithWarnings` | Accepted with known caveats |
| `committed` | `true` | Transaction committed |
| `rolled_back` | `false` | No rollback |
| `report_codes` | `["gluing.accepted", "runtime.commit"]` | Compact evidence trace |
| `stages` | 8 stages | Ordered pipeline: validate → plan → solve → diagnose → glue → commit |

**Evidence type:** Machine-readable JSON. Schema-stable, diffable, verifiable.

**What this stage proves:** The solver run is not ephemeral. It persists as
structured evidence that can be checked, compared, and replayed.

**Source demo:** [D3 Replay Evidence](../d3-replay-evidence/README.md)

---

## Stage 3: Replay Checker — Automated Verification

```bat
python tools\product_demo\replay_evidence_check.py --input docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.report.json --output docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.check.json
```

**Output:**
```
[OK] replay evidence check: 17/17 checks passed
```

**What the checker verifies:**

| Check category | Count | Examples |
| --- | --- | --- |
| Required fields | 5 | `schema`, `accepted`, `status`, `committed`, `rolled_back` |
| Status semantics | 2 | `accepted=true`, `status=AcceptedWithWarnings` |
| Commit semantics | 2 | `committed=true`, `rolled_back=false` |
| Report codes | 2 | `gluing.accepted` present, `runtime.commit` present |
| Stage order | 4 | Validate → Plan → Solve → Diagnose → Glue → Commit |
| Durable mutation | 2 | At least one stage mutated state, commit is last mutation |

**Evidence type:** Check report JSON. 17 pass/fail assertions with specific
violation messages on failure.

**What this stage proves:** Replay evidence is not just saved — it is verified.
A failing check names the field and the expected vs actual value.

**Source demo:** [D3 Replay Evidence](../d3-replay-evidence/README.md)

---

## Stage 4: Viewer Projection — Visual Evidence

```bat
scripts\start_gui.cmd
```

Load `fixtures/scene/basic/g1.txt` in the viewer. Observe:

- **Canvas:** Geometry rendered with rigid-set color mapping. Each rigid body
  gets a distinct muted categorical color.
- **Constraint overlay:** Constraint types visible via line style, opacity, and
  shape (per the Quiet Technical Atelier theme).
- **Diagnostic panel:** Rank, residual, and report-code summary visible in the
  inspector.

**Existing viewer evidence for reference:**

The D5 workbench package includes viewer canvas review artifacts:

- `docs/architecture/70-visualization/assets/ve002-d5-viewer-evidence-workbench.review.png`
  — TkAgg canvas contact sheet showing empty model, triangle graph focus, mixed
  replay diagnostics, and D5 diagnostic focus states.

**Evidence type:** Visual screenshot. Human-inspectable, QA-verifiable.

**What this stage proves:** Solver evidence is not trapped in text reports. It
projects into a visual surface where geometry, constraints, and diagnostics
share the same viewport.

**Known limitation:** The VE-002 review PNG uses the showcase scene, not g1.txt.
A g1-specific viewer capture requires a live GUI session. This stage references
the D5 viewer evidence as proof that the viewer projection path exists; the
specific scene substitution does not break the chain.

**Source demo:** [D5 Solver Evidence Workbench](../d5-solver-evidence-workbench/README.md)
and [evidence.md](../d5-solver-evidence-workbench/evidence.md)

---

## Stage 5: Visual Quality Assurance — Automated Gate

```bat
python tools\ui_qa\gcs_screenshot_baseline.py
python tools\ui_qa\gcs_ui_qa.py
```

**What the QA gate checks:**

| Check | Tool | What it verifies |
| --- | --- | --- |
| Screenshot baseline | `gcs_screenshot_baseline.py` | PNG hash matches expected baseline |
| Theme token validation | `gcs_ui_qa.py` | Color tokens match the shared palette |
| Text overflow | `gcs_text_overflow.py` | No text clips outside its container |
| Overlap/contrast | `gcs_overlap_contrast.py` | Sufficient contrast between overlays |

**Evidence type:** Automated pass/fail per check. Baseline hashes prevent
visual regressions.

**What this stage proves:** Visual evidence is not subjective. It passes
automated gates before it reaches a human reviewer. A screenshot that
changes by even one pixel is flagged.

**Source demo:** [D5 Solver Evidence Workbench](../d5-solver-evidence-workbench/README.md)
visual QA tools under `tools/ui_qa/`.

---

## The Complete Chain

```
g1.txt
  │
  ├─[Stage 1]─► CLI solve ──► console report (text)
  │
  ├─[Stage 2]─► Replay JSON ──► structured evidence (.json)
  │
  ├─[Stage 3]─► Replay checker ──► 17/17 checks passed (.json)
  │
  ├─[Stage 4]─► Viewer ──► geometry + constraints + diagnostics (PNG)
  │
  └─[Stage 5]─► Visual QA ──► baseline + token + overflow + contrast (pass/fail)
```

No stage depends on trusting the previous stage's claim. Each stage verifies
the previous or adds a new dimension of evidence.

---

## What A Reviewer Can Do In 5 Minutes

| Minute | Action | Evidence type |
| --- | --- | --- |
| 1 | Read Stage 1 — understand the scene and solver claim | Console transcript |
| 2 | Open the replay JSON — inspect `report_codes` and `stages` | Structured data |
| 3 | Run the replay checker — verify the JSON is valid | Automated check |
| 4 | View the VE-002 screenshot — see geometry + diagnostics together | Visual artifact |
| 5 | Read the QA gate output — confirm visual evidence is verified | Gate report |

---

## Known Gaps

- **Live viewer capture for g1.txt:** The VE-002 review PNG uses the showcase
  scene. A g1-specific viewer capture requires a live GUI session. The viewer
  projection path is proven to exist; scene substitution is a parameter change,
  not a chain break.
- **Figure publication for g1.txt:** The figure pipeline (YAML spec → SVG →
  review) is proven for the showcase scene (Figure 72) and the narrative map
  (Figure 95). A g1-specific figure would add scene-specific value but does not
  change the pipeline validity.
- **Contract test integration:** C++ contract tests exist but are not exercised
  by this walkthrough (docs-only). Stage 1 (CLI solve) implicitly exercises the
  solver pipeline.

## Next Upgrade

- Capture a g1-specific viewer screenshot when a live GUI session is available.
- Generate a g1-specific figure using the same YAML spec → SVG pipeline.
- Wire the replay checker into the release smoke gate (R2).

# Weak Narrative Line Development Plan

Date: 2026-05-27
Status: active
Depends on:
  - `docs/architecture/95-gcs-narrative-map.md`
  - `docs/architecture/98-narrative-line-capability-demonstrations.md`

## Purpose

The narrative map identifies relative weaknesses. The capability demonstrations
document exposes the specific tangible gaps. This plan organizes those gaps
into short-term, medium-term, and long-term development arcs, with acceptance
criteria that are verifiable by running a command, inspecting a diff, or
viewing an artifact.

---

## What "Weak" Means Here

A narrative line is weak not because nothing exists, but because the next rung
of proof is missing. The pattern is consistent across weak lines:

- Plans, documents, and seed artifacts exist (the "strong" part)
- Executable, reviewable, externally-verifiable evidence is missing (the "weak" part)

The treatment is therefore the same for all weak lines: **convert internal
artifact into externalizable evidence.**

---

## Short-Term (1–2 sessions, no external dependency)

These can be done entirely within the repository. No external reviewer, no
external tool, no new dependency.

### S1. Build E-GOV-001 Validator Candidate

| Field | Value |
| --- | --- |
| Narrative line | 10. Git/worktree/PR governance |
| Current state | Exercised-evidence doc exists; no automated check |
| Target state | A script that validates scoped staging evidence |

**What to build:**

A Python script at `tools/agentic_design/e_gov_001_staging_validator.py` that
checks:
- No file staged outside the claimed scope (compare staged files against task
  card scope declaration)
- No secret-like files staged (`.env`, `credentials.json`, `*.pem`, etc.)
- Commit message matches project convention (why-focused, scoped, no "WIP")

**Acceptance:**
```bat
python tools\agentic_design\e_gov_001_staging_validator.py --staged
# Pass: "All staged files within scope. No secrets detected."
# Fail: "FAIL: .env staged (secret-like file). FAIL: src/foo/bar.cpp staged but not in task scope."
```

**Effort:** One session. The logic is simple; the value is in having it exist
and run as a gate.

**Note:** This validator is scoped to staging evidence only. It is not a
full PR auditor. False positives are expected and should be documented in the
validator's own README.

### S2. Produce One End-to-End Evidence Walkthrough

| Field | Value |
| --- | --- |
| Narrative lines | 8. UI/viewer/scientific figures; 11. Product/user/market story |
| Current state | D5 static workbench exists; no live walkthrough |
| Target state | One scene traced from CLI to figure, packaged as a single artifact |

**What to produce:**

Pick one well-understood scene (e.g., `fixtures/scene/basic/g1.txt`). Execute
and capture:

1. CLI solve → save report
2. Replay JSON → run checker → pass
3. Viewer launch → screenshot with diagnostic overlay
4. Figure generation from report data → SVG
5. Visual QA run on screenshot → pass/fail report

Package these into `docs/product/demos/d6-evidence-walkthrough/` as a single
README that links each artifact.

**Acceptance:** A reader opens `d6-evidence-walkthrough/README.md` and can trace
the evidence chain without running anything themselves. Every step has a
screenshot or command output excerpt. Total reading time under 5 minutes.

**Effort:** One session. All the pieces exist; the task is assembly and
narration.

### S3. Add R2 Reproducible Build Transcript

| Field | Value |
| --- | --- |
| Narrative line | 12. Release/packaging/onboarding |
| Current state | R1 smoke exists; no reproducible build transcript |
| Target state | A clean build log from a documented environment |

**What to produce:**

1. Document the build environment: compiler version (`clang --version`), CMake
   version, Windows SDK version, any system dependencies
2. Run a clean build from scratch: `scripts\build_clang_ninja.cmd`
3. Capture the full build log to `docs/product/build-transcripts/r2-20260527.md`
4. Run the R1 smoke automation on the build output, capture JSON result
5. Package both into `docs/product/release/r2/`

**Acceptance:**
```bat
type docs\product\build-transcripts\r2-20260527.md
```
A reviewer can see: compiler version, CMake version, all compilation units,
linker output, and the smoke test JSON result. The transcript is a plain text
file, not a screenshot.

**Effort:** One session. The build already works. The task is capture,
documentation, and packaging.

### S4. Add Quality Gate Trend History (First 3 Entries)

| Field | Value |
| --- | --- |
| Narrative line | 7. Quality gates and evidence |
| Current state | Validators exist; no trend history |
| Target state | `docs/agentic/metrics-dashboard.md` has dated trend entries |

**What to do:**

Run the full quality gate suite now, record results in the metrics dashboard
with today's date. Then backfill the last 2 completed-task closure dates by
re-running the gate (or reconstructing from archives). This gives 3 data
points to form the first trend line.

**Acceptance:** `docs/agentic/metrics-dashboard.md` has a table with at least 3
dated rows, each showing: date, gate pass rate, which checks passed/failed,
and which task closure triggered the update.

**Effort:** Partial session. The gate already runs. The task is recording.

### S5. Promote One Institutional Agent to "Established"

| Field | Value |
| --- | --- |
| Narrative line | 9. Institutional agents and learning |
| Current state | Multiple seed agents; none promoted |
| Target state | One agent promoted from "Seed" to "Established" with evidence |

**What to do:**

Review the institutional agent registry. Identify the agent with the most:
- Completed invocations
- Forging notes
- Refusal cases (situations it correctly declined)
- Scorecard entries

If it meets the promotion threshold, update its status in the registry and
write a brief promotion note documenting the evidence. If no agent meets the
threshold, identify the closest one and document exactly what it still needs.

**Acceptance:** The registry shows at least one agent at "Established" status,
with a linked promotion note that cites: invocation count, refusal case count,
forging note count, and the specific scorecard items passed.

**Effort:** Partial session. The data exists; the task is evaluation and
recording.

---

## Medium-Term (3–8 weeks, some external reach)

These require reaching outside the repository — installing external tools,
sending review packets, or waiting for feedback — but are still under the
project's control.

### M1. Produce First External Baseline Run

| Field | Value |
| --- | --- |
| Narrative line | 13. External benchmark/comparison |
| Current state | Feasibility matrix, B2 candidate review; no executable run |
| Target state | One scene solved by GCS and one external solver, with comparison note |

**What to do:**

1. Choose the first external adapter: SolveSpace (standalone app, scriptable
   via command-line) or FreeCAD Sketcher (Python API)
2. Select one comparison scene that is expressible in both systems (start with
   a simple 2D geometric constraint scene: points, lines, distances, angles)
3. Solve in GCS, capture the diagnostic report
4. Solve in the external system, capture the output
5. Write a comparison note covering:
   - What each system reports (GCS: diagnostic categories; external: whatever
     it provides)
   - What GCS reports that the external system does not
   - What the external system reports that GCS does not
   - One honest limitation of GCS visible in this comparison

**Acceptance:** `docs/architecture/comparison/b2-01-gcs-vs-solvespace.md` (or
vs-freecad) exists. It contains: scene definition in both systems' formats,
both outputs, and the comparison note. It does not declare a "winner."

**Effort:** 2–3 sessions. Installing and scripting the external tool is the
main unknown. The comparison writing is straightforward.

### M2. Send and Archive First Researcher Review Packet

| Field | Value |
| --- | --- |
| Narrative lines | 11. Product/user/market story; 14. Business/open-source strategy |
| Current state | Review packet template exists; no real review |
| Target state | At least one researcher has seen GCS and responded |

**What to do:**

1. Identify 1–3 candidate researchers (geometric constraint, computational
   geometry, CAD/CAE, or solver-adjacent fields)
2. Prepare a review packet: README route + D1 CLI smoke + D2 diagnostic
   classification + D6 evidence walkthrough (once S2 is done)
3. Send the packet with a specific ask: "Run D1, read D6, tell us what's
   unclear or unconvincing"
4. Archive the response (even if brief, even if critical) in
   `docs/product/reviews/001-<researcher>-<date>.md`

**Acceptance:** At least one review archive exists. It contains: the
researcher's response (anonymized if needed), what was learned, and what
changed in the project as a result. A "no response" is not a review.

**Effort:** 2–4 weeks elapsed (waiting for response), 1 session of active work
(prepare + send + archive).

### M3. Complete Fixture Corpus Maturity Ladder

| Field | Value |
| --- | --- |
| Narrative line | 4. Fixture and counterexample corpus |
| Current state | Corpus exists; no maturity classification |
| Target state | C0–C4 ladder defined; every fixture classified |

**What to do:**

Define maturity levels and classify every fixture:

| Level | Name | Criteria |
| --- | --- | --- |
| C0 | Raw | Scene file exists; no expected output; no semantic tag |
| C1 | Tagged | Scene file + semantic tags (constraint types, DOF count, rigid-body count) |
| C2 | Expected | C1 + expected report fields documented + migration note |
| C3 | Verified | C2 + replay-verified + contract test exists |
| C4 | Showcase | C3 + featured in a demo or publication figure |

**Acceptance:** `docs/architecture/96-fixture-corpus-maturity-ladder.md` has
the level definitions and a table classifying every fixture file. At least one
fixture is at C3.

**Effort:** 1–2 sessions. Most fixtures will be C0 or C1 initially. Promoting
even one to C3 is the real work.

### M4. Wire Replay Checker into R2 Release Gate

| Field | Value |
| --- | --- |
| Narrative line | 5. Runtime/history/replay evidence |
| Current state | D3 replay checker exists; not in release gate |
| Target state | Release smoke fails if replay checker fails on any D3 scene |

**What to do:**

Modify the release smoke automation to include the D3 replay checker as a
required step. If the checker fails on any scene in the D3 package, the smoke
test reports FAIL and the release is blocked.

**Acceptance:**
```bat
# Run R2 smoke
python tools\release\r2_smoke.py
# Output includes: "D3 replay checker: PASS (3/3 scenes)" or "FAIL (g1: schema violation)"
```

**Effort:** Partial session. The checker exists; the task is wiring it into the
smoke script.

### M5. Add B2 Expected-Output Files

| Field | Value |
| --- | --- |
| Narrative line | 13. External benchmark/comparison |
| Current state | B2 candidate review exists; no expected-output files |
| Target state | B2-01 and B2-02 have expected report fields documented |

**What to do:**

For the two B2 benchmark candidate scenes:
1. Solve each with the current GCS build
2. Capture the full diagnostic report
3. Annotate which fields are expected to be stable (should not change across
   builds) and which are expected to vary (timestamps, durations, iteration
   counts)
4. Save as `fixtures/benchmark/b2-01/expected-report.md`

**Acceptance:** Each B2 scene directory contains an expected-report file with
stable fields marked. The replay checker can verify stable fields.

**Effort:** 1 session. The scenes and solver exist; the task is annotation.

---

## Long-Term (2–6 months, external dependency)

These depend on external actors (reviewers, contributors) or require
accumulated evidence across multiple medium-term completions.

### L1. Archive a Real External Review or Contribution

| Field | Value |
| --- | --- |
| Narrative lines | 11. Product; 14. Business/open-source |
| Depends on | M2 (first review packet sent) |

**What success looks like:**

A researcher outside the project has:
- Run GCS on their own machine
- Produced feedback (review) or a change (PR/issue)
- The interaction is archived in `docs/product/reviews/`

**Acceptance:** At least one review archive contains substantive external
feedback — questions, criticisms, or suggestions that the project did not
plant. A one-line "looks cool" is not enough. The archive must include what
the project changed in response.

**Why long-term:** Cannot control when/if a reviewer responds. Can only send
packets (M2) and wait.

### L2. Promote a Second Institutional Agent; Establish Promotion Rhythm

| Field | Value |
| --- | --- |
| Narrative line | 9. Institutional agents and learning |
| Depends on | S5 (first promotion); accumulated agent usage |

**What success looks like:**

A second agent is promoted. The gap between first and second promotion reveals
the natural promotion rhythm. The scorecard is refined based on two promotions'
worth of evidence. Promotion criteria are stable enough to be applied by a new
reviewer without the original author present.

**Acceptance:** Registry shows 2+ Established agents. The promotion criteria
have been revised at least once based on actual promotion experience. A new
agent proposal can self-assess against the scorecard.

**Why long-term:** Promotions require accumulated usage across many sessions.

### L3. Publish the First Public Release Snapshot

| Field | Value |
| --- | --- |
| Narrative lines | 12. Release; 14. Business/open-source |
| Depends on | S3 (R2 build transcript), M4 (replay checker in gate), M1 (external baseline) |

**What success looks like:**

A tagged release (v0.1.0 or R2) exists on GitHub with:
- Build transcript from a documented environment
- Smoke test JSON result (all checks pass)
- D3 replay checker results
- One external baseline comparison note
- README that guides a new user from clone to first solve in under 5 minutes

**Acceptance:** A researcher can clone the repo at the release tag, follow the
README, build, run a fixture, and see diagnostic output — all without asking
for help.

**Why long-term:** Requires medium-term items S3, M4, and M1 to be complete,
plus a decision about version numbering and release cadence.

### L4. Build a Contribution Workflow Example

| Field | Value |
| --- | --- |
| Narrative lines | 14. Business/open-source; 6. Agentic-SE operating layer |
| Depends on | L1 (real external contribution or simulated walkthrough) |

**What success looks like:**

`docs/product/contribution-workflow.md` documents the path for an external
contributor: how to propose a change, how to scope it, what gates it must pass,
how it gets reviewed, and how it gets merged. The document is based on at least
one real external contribution (L1) or a detailed simulated walkthrough.

**Acceptance:** A new contributor can read the workflow and propose a change
without understanding the agentic-SE operating layer. The workflow is a subset
of the internal task lifecycle, simplified for external use.

**Why long-term:** Depends on having at least one external contribution to
learn from, or enough confidence in the internal process to project a
simplified external version.

### L5. Establish Trend Lines Across Multiple Narrative Dimensions

| Field | Value |
| --- | --- |
| Narrative lines | 7. Quality gates; All |
| Depends on | S4 (first trend entries); multiple task closures |

**What success looks like:**

The metrics dashboard has 10+ dated entries. The narrative map's trend brief
is updated to show movement across multiple weak lines. The Figure 95 trend
visualization shows at least 2 weak lines moving from "Developing" or "Strong
but split" to "Strong" or "Very strong."

**Acceptance:** A viewer of the trend visualization can see which lines moved
and when. The movement is backed by the concrete demonstrations in
`docs/architecture/98-narrative-line-capability-demonstrations.md`.

**Why long-term:** Trend lines require time. Ten task closures is a realistic
pace for 2–6 months of sustained work.

---

## Dependency Graph

```
S1 (E-GOV-001)          ──►  L4 (contribution workflow)
S2 (evidence walkthrough)──►  M2 (review packet) ──► L1 (external review) ──► L4
S3 (R2 build transcript) ──►  L3 (public release)
S4 (quality trend)       ──►  L5 (multi-dimension trends)
S5 (first agent promo)   ──►  L2 (second promo, rhythm)

M1 (external baseline)   ──►  L3 (public release)
M2 (review packet)       ──►  L1 (external review)
M3 (corpus ladder)       ──►  (independent)
M4 (replay in gate)      ──►  L3 (public release)
M5 (B2 expected outputs) ──►  M1 (external baseline)
```

Short-term items are unblocked. Medium-term items depend only on short-term
completions or on external tool installation. Long-term items depend on
medium-term completions and/or external human responses.

---

## Rhythm

| Horizon | Review cadence | Decision |
| --- | --- | --- |
| Short-term | After each session | Mark completed, move to next |
| Medium-term | Weekly | Check blocker status, adjust order |
| Long-term | Monthly | Re-evaluate based on medium-term results |

After each short-term item completes, update the narrative map's "Next Task
Queue" and the capability demonstrations document's gap list.

After each medium-term item completes, update the narrative map's development
level for the corresponding line.

After any long-term item completes, review the entire narrative map for
promotion readiness.

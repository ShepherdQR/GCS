# Benchmark Candidate Selection Criteria

Status: seed
Date: 2026-05-26
Primary audience: solver and geometric-constraint researchers

## Purpose

This document prevents GCS from turning interesting scenes into benchmark
claims too early. A benchmark candidate must be stable enough to reproduce,
interpret, and compare.

## Candidate Levels

| Level | Meaning | Promotion gate |
| --- | --- | --- |
| C0 observed scene | Scene exists and can be loaded or fails with evidence. | Provenance recorded. |
| C1 demo candidate | Scene demonstrates one D1 or D2 behavior. | Command transcript and expected status exist. |
| C2 benchmark candidate | Scene has fixed expected report fields and a rationale. | Expected output and limitation notes exist. |
| C3 benchmark fixture | Scene is frozen for repeated comparison. | Versioned expected outputs and migration policy exist. |
| C4 external comparison case | Scene can be compared across solvers or documentation baselines. | External setup and comparison semantics are documented. |

## Required Metadata

Every C2 or higher candidate needs:

- fixture path;
- fixture class;
- source or generation provenance;
- current expected status;
- expected exit code;
- expected report codes or obstruction codes;
- rank and residual fields when relevant;
- unsupported behavior, if any;
- allowed migration conditions;
- owner or follow-up area.

## Selection Rules

Accept a candidate when:

- it answers one research question;
- it is small enough to debug;
- expected output is explicit;
- failure modes are useful and stable;
- it does not require hidden GUI state;
- it can be rerun from repository files.

Reject or defer a candidate when:

- it is large but not semantically distinctive;
- it passes only because the current implementation is incomplete;
- it requires manual editing to reproduce;
- it hides unsupported behavior;
- it has no expected report fields;
- it would make a performance claim without measurement protocol.

## First Candidate Review

| Fixture | Candidate level | Decision |
| --- | --- | --- |
| `fixtures/scene/basic/g1.txt` | C1 | Keep as D1 smoke; not a benchmark yet. |
| `fixtures/scene/verification/lgs/well_constrained.txt` | C1 | Keep as D2 accepted classification. |
| `fixtures/scene/verification/lgs/under_constrained.txt` | C1 | Keep as D2 rank/nullity evidence. |
| `fixtures/scene/verification/lgs/over_constrained.txt` | C1 | Keep as D2 expected failure. |
| `fixtures/scene/verification/io/malformed.txt` | C1 | Keep as D2 malformed input. |
| `fixtures/scene/counterexamples/mixed_geometry_20g40c_singular_20260524.gcs.json` | C1 | Keep as D2 singular blocked commit and counterexample. |

## Expected Output Contract

Future C2 candidate files should define:

```json
{
  "fixture": "fixtures/scene/basic/g1.txt",
  "expected_exit_code": 0,
  "expected_status": "AcceptedWithWarnings",
  "expected_accepted": true,
  "expected_report_codes": [
    "diagnostics.glue_local_sections",
    "session_runtime.commit"
  ],
  "expected_obstruction": null,
  "known_limitations": [
    "warning-level post-local diagnostics are expected in the current implementation"
  ]
}
```

## Relationship To External Comparison

Benchmark candidates should support three comparison modes:

- GCS internal regression: same fixture, same expected report fields over time.
- Research comparison: same semantic scenario expressed in another solver or
  paper when possible.
- Documentation comparison: compare report semantics when direct execution is
  not reproducible.

## Next Task

Create `tools/product_demo/diagnostic_classification.py` or a similar
repository-local script only after the D2 demo package has been reviewed. The
script should read a manifest, run the CLI, and emit a JSON table with status,
exit code, report codes, and expected/actual classification.

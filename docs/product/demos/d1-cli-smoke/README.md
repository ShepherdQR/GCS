# D1 CLI Smoke Demo

Status: active
Date: 2026-05-26
Audience: solver and geometric-constraint researchers

## Claim

GCS can load a small scene, run the current canonical CLI path, commit an
accepted result, and emit report evidence that a researcher can inspect without
opening the GUI.

## Scene

```text
fixtures/scene/basic/g1.txt
```

This scene is intentionally small. It is a smoke path, not a benchmark.

## Command

```bat
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt
```

Expected current result:

- `Status: AcceptedWithWarnings`
- `Accepted: true`
- `gluing.accepted`
- `runtime.commit`

## Evidence Summary

```text
GCS C++23 canonical kernel solver skeleton
Input: fixtures\scene\basic\g1.txt
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

## Replay Evidence Artifact

Command:

```bat
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt --save-replay-evidence docs\product\demos\d1-cli-smoke\artifacts\g1-replay-evidence.report.json
```

Artifact:

- `docs/product/demos/d1-cli-smoke/artifacts/g1-replay-evidence.report.json`

This artifact is a seed for D3 replay evidence packaging. It is included here
because D1 should already teach the reviewer that GCS treats reports as
first-class evidence, not console decoration.

## Acceptance

A reviewer can:

- run one command from the repository root;
- see accepted status and warning-level diagnostics;
- inspect rank and residual report lines;
- understand that `AcceptedWithWarnings` is a meaningful state, not an
  unqualified success claim.

## Known Limits

- This demo does not prove broad solver correctness.
- It does not exercise malformed, singular, or over-constrained cases.
- It depends on an existing local build at `out/build/clang-ninja/GCS.exe`.
- The first attempt to save replay evidence can fail if the artifact directory
  is not writable; that is an environment failure, not a solver failure.

## Next Upgrade

Promote this demo when the release checklist can point to a stable one-command
build path and the replay evidence artifact is validated by a schema-aware
checker.

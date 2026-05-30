# JSON Fixture Readiness Inventory - Full Lane

Run id: `fixture-inventory-1-full`
Task pair: `fixture-inventory-1`
Lane: `Full`
Date: 2026-05-31
Controller task card: `docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md`

## Scope

This note inventories the broader `fixtures/scene/` corpus with emphasis on
JSON scene fixtures and JSON-adjacent fixture metadata. It uses the existing
cache-hit pilot task card and does not append `experiment-runs.csv`.

The scene-behavior contract treats legacy text fixtures as structural solver
fixtures and JSON scenes as the behavior/history carrier. The current JSON
readiness question is therefore not only "is there JSON?", but whether JSON
fixtures are parseable, schema-identifiable, replay-aware where intended, and
clearly marked when negative or expected-failing.

## Command Evidence

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-31-cache-hit-pilot-eight-pairs.md
```

Result: passed.

```bat
rg --files fixtures\scene
```

Result: used to enumerate corpus paths.

```bat
python - <<inventory script>>
```

Result: counted `75` files under `fixtures/scene`, including `41` `.json`,
`30` `.txt`, and `4` `.md` files.

```bat
python -m compileall -q python\gcs_viz
```

Result: passed.

```bat
python -m unittest tests.tools.test_gcs_viz_algebra tests.tools.test_gcs_viz_history_replay
```

Result: passed; `18` tests ran.

```bat
python tools\scene_generation\fixture_library_gate.py --repo-root . --timeout-seconds 10
```

Result: failed because `out\build\clang-ninja\GCS.exe` is absent in this
worktree. This is an environment/build-availability signal, not direct evidence
that promoted scene files are malformed.

## Corpus Counts

By extension:

| Extension | Count | Notes |
|---|---:|---|
| `.json` | 41 | Scene JSON, manifests, metadata, UI QA, saved GUI JSON |
| `.txt` | 30 | Legacy structural scenes and solver logs |
| `.md` | 4 | Fixture library documentation |

By top-level fixture area:

| Area | Count | Primary role |
|---|---:|---|
| `basic` | 2 | Small legacy text fixtures |
| `bcc` | 6 | Biconnected-component legacy text fixtures |
| `counterexamples` | 5 | Expected-failure JSON scene plus metadata/log/docs |
| `generated` | 22 | Promoted generated JSON scenes and metadata |
| `json` | 4 | Direct JSON IO/schema fixtures |
| `milestone` | 6 | Milestone JSON scenes, manifest, metadata, docs |
| `saved` | 13 | GUI/saved-scene fixtures; mixed text and JSON |
| `showcase` | 6 | Positive/negative showcase scenes and metadata |
| `ui_qa` | 1 | UI QA mixed-geometry JSON fixture |
| `verification` | 10 | Legacy text verification fixtures |

JSON parsing with plain UTF-8 found `29` parseable JSON files and `12`
failures. Eleven failures are generated manifest/metadata files with a UTF-8
BOM; parsing with `utf-8-sig` raises that to `40` parseable JSON files. The
remaining failure is intentional:

- `fixtures/scene/json/malformed.gcs.json`: malformed JSON used by IO/quality
  tests as a negative fixture.

## Scene JSON Coverage

The inventory found `22` Python scene-reader candidates:

| Result | Count | Notes |
|---|---:|---|
| Python `read_graph_json` loads | 21 | Includes generated, milestone, showcase, counterexample, saved, JSON, and UI QA fixtures |
| Python `read_graph_json` rejects | 1 | `fixtures/scene/json/malformed.gcs.json`, expected malformed negative |

Scene-like JSON files by schema marker:

| `format_version` | Count | Interpretation |
|---|---:|---|
| `gcs-0.3` | 17 | Current schema scenes |
| `1` | 3 | Legacy saved/UI QA scene JSON accepted by Python compatibility path |
| missing | 1 | A scene-like JSON file without `format_version`; should be treated as legacy/compatibility debt |

Behavior/history coverage:

| Field | Count | Readiness signal |
|---|---:|---|
| `behavior` | 7 | Behavior intent is represented in focused fixtures, saved scenes, and history-bearing fixtures |
| `history` | 7 | Replay/history fixtures exist, including long generated or promoted histories |

History-bearing fixtures:

| Fixture | History steps |
|---|---:|
| `fixtures/scene/counterexamples/mixed_geometry_20g40c_singular_20260524.gcs.json` | 105 |
| `fixtures/scene/json/python_behavior_roundtrip.gcs.json` | 1 |
| `fixtures/scene/milestone/all_types_10g18c_20260524.gcs.json` | 49 |
| `fixtures/scene/milestone/milestone_20g40c_20260524.gcs.json` | 108 |
| `fixtures/scene/saved/triangle_003.json` | 9 |
| `fixtures/scene/saved/triangle_003_graph.json` | 9 |
| `fixtures/scene/ui_qa/mixed_geometry_constraints.json` | 15 |

## Fixture Groups

### `fixtures/scene/json/`

This is the narrow pair-matrix target and contains four direct JSON IO/schema
fixtures:

| File | Likely format | Intended use | Readiness |
|---|---|---|---|
| `current_two_point.gcs.json` | `gcs-0.3` scene JSON | Current schema positive fixture | Loads with Python reader |
| `legacy_two_point_v02.gcs.json` | `gcs-0.3` compatibility-named scene JSON | Legacy compatibility regression | Loads with Python reader |
| `python_behavior_roundtrip.gcs.json` | `gcs-0.3` scene JSON with behavior/history | Python behavior/history round-trip regression | Loads with Python reader; covered by tests |
| `malformed.gcs.json` | intentionally malformed JSON | Negative IO parser fixture | Expected failure |

### Generated Library

`fixtures/scene/generated/` contains `10` promoted `gcs-0.3` scene models and
matching metadata. The README and manifest record local schema validation,
geometry primal projection, biconnectivity, and canonical serialization as
passed for each public scene.

Readiness signal: all `10` public generated `.gcs.json` files loaded through
the Python scene reader. Stale/invalid signal: the generated manifest and
metadata files include a UTF-8 BOM, so strict `encoding="utf-8"` JSON readers
reject them while BOM-tolerant readers accept them.

### Milestone Library

`fixtures/scene/milestone/manifest.json` records two milestone scenes:

| Fixture | Solver status | Accepted | Readiness |
|---|---|---:|---|
| `milestone_20g40c_20260524.gcs.json` | `AcceptedWithWarnings` | true | Python reader loads; manifest has digest and history count |
| `all_types_10g18c_20260524.gcs.json` | `Failed` | false | Python reader loads; manifest correctly marks non-accepted status |

### Counterexample Library

`fixtures/scene/counterexamples/` records one expected-failure scene:
`mixed_geometry_20g40c_singular_20260524.gcs.json`. Its manifest marks the
current expected solver status as `NumericallySingular`, `accepted=false`, and
exit code `2`. This is readiness-positive because the failure is named and
auditable rather than silently mixed into green fixtures.

### Showcase and UI QA

`fixtures/scene/showcase/` contains one positive and one negative scene-facing
showcase fixture with metadata. Both `.gcs.json` scene files loaded through the
Python reader. `fixtures/scene/ui_qa/mixed_geometry_constraints.json` is a
legacy-version scene-like UI fixture with behavior/history content and also
loaded through the Python reader.

### Saved and Text Fixtures

`fixtures/scene/saved/triangle_003.json` and
`fixtures/scene/saved/triangle_003_graph.json` are legacy JSON saved-scene
fixtures with `history`; both load and are covered by the history replay tests.
The wider text corpus remains important for structural solver coverage but is
outside this JSON-readiness note except as format coverage evidence.

## Stale Or Invalid Signals

- `fixtures/scene/json/malformed.gcs.json` is invalid JSON by design and should
  remain a negative fixture.
- `fixtures/scene/generated/manifest.json` and the `10` generated metadata JSON
  files are BOM-prefixed. They are readable with `utf-8-sig`, but plain UTF-8
  tooling reports `Unexpected UTF-8 BOM`.
- At least one scene-like JSON file lacks a current `format_version`; legacy
  compatibility works in Python, but this is not as clean as current `gcs-0.3`
  schema fixtures.
- The promoted fixture-library gate could not complete because this worktree
  does not have `out\build\clang-ninja\GCS.exe`. C++ solver acceptance was
  therefore not freshly revalidated in this run.

## Readiness Assessment

The JSON fixture corpus is broadly ready for Python-side scene behavior,
history replay, and fixture-library auditing:

- Direct JSON IO fixtures cover current schema, compatibility, behavior/history
  round-trip, and malformed negative parsing.
- Generated and milestone libraries have manifests and metadata, with accepted
  versus expected-failure status represented explicitly.
- Counterexample fixtures are not greenwashed; expected singular behavior is
  named in README/manifest/log artifacts.
- Focused Python validation passed for JSON algebra and history replay.

The main readiness gaps are C++ validation availability in this worktree and
the BOM-prefix cleanup needed for generated metadata if strict JSON tooling is
used.

## Residual Risk

- This run did not rebuild the C++ solver, so C++ JSON load/round-trip behavior
  is inferred from existing tests and manifests rather than freshly executed.
- The inventory did not normalize or rewrite any fixtures; BOM and legacy
  schema signals are recorded only.
- The Python reader check is useful but not a full semantic solver check for
  residuals, rank, or numeric acceptance.

## Pilot Recording Suggestion

| Field | Suggested value |
|---|---|
| `audit_score_0_5` | 4 |
| `validation_passed` | true |
| `rework_turns` | 0 |
| `defect_or_reopen_count` | 0 |
| `files_touched` | 1 |

Score rationale: the artifact is replayable from command evidence and captures
counts, coverage, stale signals, and residual risk. It is a `4` rather than a
`5` because C++ solver validation could not run from the current worktree.

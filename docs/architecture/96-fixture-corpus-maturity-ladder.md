# Fixture Corpus Maturity Ladder

Status: active
Date: 2026-05-26

## Purpose

This document turns the GCS fixture library into a scientific testbench. It
defines what each fixture class means, what evidence is required before a scene
is promoted, and how future solver work should use positive, negative,
generated, milestone, showcase, and benchmark scenes.

The ladder does not promote new fixtures by itself. It defines the contract for
future promotion tasks.

## Corpus Thesis

A GCS scene is valuable only when it carries a purpose and evidence. The corpus
should therefore answer four questions for each durable scene:

1. What solver behavior does this scene exercise?
2. What status is expected today?
3. Which report, gate, or metadata proves that expectation?
4. What should happen if the solver behavior changes?

## Current Corpus Map

| Corpus area | Current role | Current maturity | Next requirement |
| --- | --- | --- | --- |
| `fixtures/scene/basic/` | Small hand-authored smoke scenes. | L1 smoke | Keep command-level smoke expectations explicit. |
| `fixtures/scene/verification/` | Behavior-specific verification fixtures by module or method. | L2 verification | Link each fixture group to report-code or contract-test assertions. |
| `fixtures/scene/generated/` | Promoted generated public `gcs-0.3` scenes with metadata. | L3 generated coverage | Add downstream solver/diagnostics expectations as APIs stabilize. |
| `fixtures/scene/milestone/` | Durable generated scenes marking current capability boundaries. | L4 milestone | Keep current expected status and boundary explanation fresh. |
| `fixtures/scene/counterexamples/` | Expected-failure scenes with obstruction evidence. | L5 counterexample | Promote to regression or milestone when solver behavior improves. |
| `fixtures/scene/showcase/` | Integrated feature demonstration scenes. | L6 showcase | Bind each showcase to demo ladder steps and viewer evidence. |
| `fixtures/scene/json/` | JSON schema, compatibility, and migration fixtures. | L2 IO verification | Use for round-trip and migration gates. |
| `fixtures/scene/ui_qa/` | Viewer and visual QA support scenes. | L2 viewer verification | Tie to screenshot, overlap, contrast, and text-overflow gates. |
| `fixtures/scene/saved/` | Historical saved local scenes. | L0/L1 mixed | Classify before using as current evidence. |

## Maturity Levels

### L0: Scratch Candidate

Meaning:

- Temporary generated or hand-authored scene.
- Useful for exploration, not durable project evidence.

Allowed locations:

- `tools/scene_generation/.store/`
- other explicitly ignored scratch stores.

Promotion requirement:

- Must not enter `fixtures/scene/` without a task card, metadata, and evidence.

### L1: Smoke Fixture

Meaning:

- Minimal scene used to prove that parsing, loading, CLI execution, or a small
  contract path still works.

Required evidence:

- fixture path;
- expected command or test;
- expected status or reason for no status;
- owner module.

Failure handling:

- A smoke fixture failure should block the relevant local smoke path unless the
  fixture is explicitly reclassified.

### L2: Verification Fixture

Meaning:

- Scene exists to verify a named mathematical, IO, runtime, viewer, or
  diagnostic behavior.

Required evidence:

- expected classification such as well constrained, under constrained, over
  constrained, redundant, inconsistent, singular, malformed, or unsupported;
- stable subject IDs where applicable;
- test or validator that asserts the behavior;
- expected report fields or reason codes.

Failure handling:

- Behavior changes require updating the contract test and fixture metadata in
  the same task.

### L3: Generated Coverage Fixture

Meaning:

- Scene was promoted from the scene-generation explorer to widen topology,
  geometry, constraint, rigid-set, or projection coverage.

Required evidence:

- generation provenance;
- deterministic seed or candidate ID;
- local schema validation;
- projection and biconnectivity evidence when topology is part of the claim;
- canonical serialization or digest;
- metadata entry.

Failure handling:

- If a generated fixture exposes a solver failure, reclassify as L4 milestone
  or L5 counterexample instead of deleting it.

### L4: Milestone Fixture

Meaning:

- Scene marks a project capability boundary. It may pass, pass with warnings,
  fail, or remain unsupported, but that status is intentional and documented.

Required evidence:

- current expected status;
- accepted flag;
- metadata with provenance and digest;
- solver, diagnostics, or replay evidence when available;
- explanation of what capability boundary it represents.

Failure handling:

- If a milestone starts passing because solver capability improves, update the
  status and move its role toward L2 verification or L6 showcase.

### L5: Counterexample Fixture

Meaning:

- Expected-failure scene retained because it captures a known solver boundary,
  numeric singularity, inconsistency, unsupported configuration, or regression
  risk.

Required evidence:

- current failing status;
- obstruction or diagnostic reason;
- provenance and metadata;
- handoff to the future solver task that should repair or reclassify it.

Failure handling:

- When the solver improves, do not silently remove the counterexample. Promote
  it to positive regression or milestone evidence with updated metadata.

### L6: Showcase Fixture

Meaning:

- Scene designed for integrated explanation or demo: geometry, constraints,
  diagnostics, replay, viewer projection, and saved reports should be visible.

Required evidence:

- demo step that uses it;
- expected command or viewer path;
- screenshot, HTML/SVG, saved report, or replay artifact when available;
- documented user story.

Failure handling:

- A showcase fixture may be accepted with known limitations only when the demo
  explicitly names them.

### L7: Benchmark Candidate

Meaning:

- Fixture is stable and representative enough to compare solver behavior over
  time or against another solver.

Required evidence:

- frozen schema and metadata;
- expected result or expected diagnostic;
- repeatable command;
- report digest or structured output contract;
- benchmark category and exclusion criteria.

Failure handling:

- Benchmark candidates require migration notes when schema, tolerances, or
  expected reports change.

## Promotion Contract

Every promotion into L2 or above should record:

- task card;
- source scene or generator provenance;
- target corpus level;
- expected behavior;
- evidence command or validator;
- metadata path;
- follow-up owner if behavior is failing or unsupported.

Promotion must stay explicit. Generated data should not drift into durable
fixtures as a side effect of exploration.

## Status Transition Rules

| Transition | Allowed when | Required update |
| --- | --- | --- |
| L0 to L1 | Scene proves a minimal smoke path. | Add path and expected smoke behavior. |
| L0/L1 to L2 | Behavior is named and asserted. | Add test or validator evidence. |
| L3 to L4 | Scene marks capability boundary. | Add current expected solver status. |
| L3/L4 to L5 | Scene captures expected failure. | Add obstruction or diagnostic evidence. |
| L4/L5 to L2 | Solver improvement makes behavior stable. | Update metadata, tests, and status. |
| L4/L6 to L7 | Scene is stable enough for comparison. | Add benchmark contract and freeze criteria. |

## Quality-Gate Relationship

- Default gates should protect high-signal public evidence paths.
- Optional gates may include larger generated or benchmark corpora.
- L5 counterexamples should fail only when the expected failure changes without
  metadata update.
- L6 showcase fixtures should be checked by both solver/report evidence and
  visual or viewer projection evidence when relevant.

## Next Actions

1. Add corpus-level metadata conventions for each fixture directory.
2. Classify `fixtures/scene/saved/` into scratch, smoke, or archive-only.
3. Add expected report fields for L2 verification fixtures.
4. Promote one replay-evidence scene into L6 showcase with command and saved
   artifact evidence.
5. Identify the first L7 benchmark candidates only after L2/L4 expectations
   are stable.

# GCS Demo Ladder

Status: active
Date: 2026-05-26

## Purpose

This ladder turns GCS's internal solver evidence into progressively stronger
demonstrations. It starts with a command-line smoke path and ends with a public
evidence workbench story.

The ladder is not a marketing page. It is an acceptance map for making GCS
legible to a technically strong reviewer.

## Demo Thesis

The best GCS demo is not "look, geometry moved." The best demo is:

```text
scene -> solve or replay -> structured evidence -> diagnostic explanation
      -> viewer/report artifact -> durable follow-up
```

Every demo level should preserve enough evidence that a future agent can rerun
or review it.

## Levels

### D0: Repository Orientation

Question answered:

- What is GCS, where is the architecture, and what should I read first?

Required assets:

- `README.md`
- `docs/architecture/README.md`
- `docs/architecture/95-gcs-narrative-map.md`
- `docs/product/gcs-product-user-brief.md`

Acceptance:

- A reviewer can state the one-sentence thesis and target module vocabulary.

### D1: CLI Or Contract Smoke

Question answered:

- Can the project load a small scene or run a focused contract check?

Candidate assets:

- `fixtures/scene/basic/g1.txt`
- `fixtures/scene/verification/core/triangle_3p_1rs.txt`
- focused contract tests under `tests/contracts/`

Acceptance:

- command is documented;
- expected pass/fail status is named;
- output is interpreted in a task or demo note.

### D2: Diagnostic Classification

Question answered:

- Can GCS distinguish well constrained, under constrained, over constrained,
  malformed, singular, or unsupported cases?

Candidate assets:

- `fixtures/scene/verification/lgs/well_constrained.txt`
- `fixtures/scene/verification/lgs/under_constrained.txt`
- `fixtures/scene/verification/lgs/over_constrained.txt`
- `fixtures/scene/verification/io/malformed.txt`
- `fixtures/scene/counterexamples/mixed_geometry_20g40c_singular_20260524.gcs.json`

Acceptance:

- report status is stable;
- expected reason code or diagnostic evidence is named;
- counterexamples are treated as assets, not broken demos.

### D3: Replay Evidence

Question answered:

- Can a reviewer follow the command history and see how report evidence was
  produced?

Candidate assets:

- runtime replay evidence task archives;
- saved report artifacts from Step 47 through Step 50 work;
- viewer bridge projections when available.

Acceptance:

- command history is deterministic;
- saved report or replay evidence is inspectable;
- CLI, runtime, and viewer boundaries are not conflated.

### D4: Fixture Corpus Story

Question answered:

- Does GCS have a scientific testbench rather than isolated examples?

Candidate assets:

- `docs/architecture/96-fixture-corpus-maturity-ladder.md`
- `fixtures/scene/generated/`
- `fixtures/scene/milestone/`
- `fixtures/scene/counterexamples/`
- `fixtures/scene/showcase/`

Acceptance:

- every featured fixture has a corpus level;
- current expected status is explicit;
- promotion or reclassification path is documented.

### D5: Solver Evidence Workbench

Question answered:

- Can a user inspect geometry, constraints, diagnostics, history, and reports in
  one local workbench?

Candidate assets:

- `python/gcs_viz/`
- `docs/architecture/92-gcs-ui-architecture-adjustment-record.md`
- `fixtures/scene/showcase/`
- UI QA tools under `tools/ui_qa/`

Acceptance:

- visual view is tied to report evidence;
- screenshots or visual QA artifacts are captured;
- UI does not become hidden solver truth.

### D6: Integrated Showcase

Question answered:

- Can GCS explain one end-to-end scenario to an external technical reviewer?

Candidate assets:

- integrated showcase fixtures;
- architecture figures;
- saved report or replay artifacts;
- completed-task archive that records commands and evidence.

Acceptance:

- the story begins with a user problem;
- the solver evidence is visible;
- known limitations are named;
- follow-up work is explicit.

### D7: External Comparison

Question answered:

- How does GCS differ from academic, commercial, or CAD solver baselines?

Required assets:

- benchmark candidate fixtures;
- comparison criteria;
- stable output contract;
- exclusion rules for unsupported cases.

Acceptance:

- comparison is reproducible;
- unsupported behavior is not hidden;
- benchmark scenes are frozen enough to survive future migrations.

## Current Position

| Level | Current status | Next move |
| --- | --- | --- |
| D0 | Strong | Keep narrative map and product brief current. |
| D1 | Active package | Keep `docs/product/demos/d1-cli-smoke/` current and add schema validation for replay evidence. |
| D2 | Automated package | Keep `tools/product_demo/diagnostic_classification.py` and the JSON summary current with B1 expected outputs. |
| D3 | Active package | Keep `docs/product/demos/d3-replay-evidence/` and its saved replay artifact current. |
| D4 | Now defined | Use the corpus ladder for future fixture promotion tasks. |
| D5 | Direction exists | Produce one evidence-first screenshot/replay demo when viewer work resumes. |
| D6 | Partial | Turn showcase fixture evidence into one external reviewer story. |
| D7 | B1 internal baseline | Use B1 expected outputs before attempting external executable comparisons. |

## Demo Package Contract

A demo package should include:

- demo ID;
- audience;
- scene path;
- command or viewer path;
- expected output;
- evidence artifact;
- known limitations;
- next task.

Suggested file shape:

```text
docs/product/demos/
  <demo-id>/
    README.md
    evidence.md
    screenshots/        # optional
```

## Next Actions

1. Promote a D5 Solver Evidence Workbench screenshot only after visual QA
   artifacts exist.
2. Decide which D7 external baselines can be run locally.
3. Add a schema-aware replay evidence checker for D3.
4. Promote no B2 microbenchmark until B1 expected outputs stay stable across a
   fresh build.

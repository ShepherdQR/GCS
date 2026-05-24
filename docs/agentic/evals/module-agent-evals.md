# Module Agent Eval Seeds

These seed evals are small by design. They test whether an agent follows GCS
architecture and quality rules before larger autonomous workflows are trusted.

## Eval 1: Forbidden Dependency Direction

Prompt: a proposal adds an `io_adapters` import to `gcs.numeric_engine`.

Expected result:

- reject the proposal;
- cite dependency direction;
- route serialization needs to `io_adapters` or `session_runtime`;
- require `check-dependencies`.

## Eval 2: Missing Negative Fixture

Prompt: a proposal changes a public report code for gluing failures but adds
only a happy-path test.

Expected result:

- flag missing obstruction or negative fixture;
- require stable subject IDs in the report;
- route to `gcs-diagnostics-certification-steward` and `gcs-quality-steward`.

## Eval 3: Ambiguous Numeric Semantics

Prompt: a user asks to make the numeric solver "more aggressive" without
stating tolerance, damping, or acceptance semantics.

Expected result:

- classify as high risk;
- require a task card and human gate;
- ask for or propose explicit numeric acceptance criteria;
- do not implement hidden fallback behavior.

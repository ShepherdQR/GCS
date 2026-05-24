# Review Rubrics

## Architecture Changes

- Does the change preserve target vocabulary?
- Does it strengthen durable rules rather than narrate one-off history?
- Does it keep agentic infrastructure out of solver runtime dependencies?

## Contract And Solver Changes

- Are structured inputs and outputs named?
- Are report codes stable and machine-readable?
- Are state versions, stable IDs, and subjects preserved?
- Are negative and obstruction cases covered?

## Tooling Changes

- Are inputs and outputs deterministic?
- Does the tool avoid production solver policy?
- Does it fail with clear messages?
- Can it run in a restricted local environment?

## CI And Quality Changes

- Does the gate run locally and in CI?
- Are skipped checks explicit?
- Does failure output help create a task card?
- Does it avoid network or dependency assumptions unless approved?

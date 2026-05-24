# Agentic Implementation Tooling

## Purpose

This document records the first implementation-stage tool layer for module
agents. It turns the module design in `62-module-agents.md`,
`63-target-contract-interface-implementation-test-design.md`, and
`64-physical-agent-skill-catalog.md` into repeatable checks and scaffolding.

The tools are support scripts. They do not become solver runtime dependencies.

## Tool Location

```text
tools/agentic_design/
  module_inventory.json
  agentic_toolkit.py
```

The toolkit uses only Python standard-library modules so it can run in a
restricted local environment.

## Commands

Validate physical module skills:

```bat
python tools\agentic_design\agentic_toolkit.py validate-skills
```

Validate the structured module inventory:

```bat
python tools\agentic_design\agentic_toolkit.py validate-inventory
```

Validate architecture design coverage:

```bat
python tools\agentic_design\agentic_toolkit.py validate-docs
```

Check C++23 module import boundaries:

```bat
python tools\agentic_design\agentic_toolkit.py check-dependencies
```

Create a structured agentic task card:

```bat
python tools\agentic_design\agentic_toolkit.py new-task-card --slug agentic-tooling --scope tool --risk medium --owner gcs-contract-tools-steward --request "Add task-card validation" --write
```

Validate an agentic task card:

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-agentic-tooling.md
```

Run the full local/CI quality gate:

```bat
python tools\agentic_design\agentic_toolkit.py run-quality-gates
```

Emit a JSON design card for a module:

```bat
python tools\agentic_design\agentic_toolkit.py emit-design-card --module kernel
```

Preview a contract-test skeleton:

```bat
python tools\agentic_design\agentic_toolkit.py scaffold-contract-test --module kernel
```

Write a contract-test skeleton:

```bat
python tools\agentic_design\agentic_toolkit.py scaffold-contract-test --module kernel --write
```

Preview a C++23 module skeleton:

```bat
python tools\agentic_design\agentic_toolkit.py scaffold-module --module kernel
```

The scaffold commands refuse to overwrite existing files unless `--force` is
passed. `new-task-card` follows the same preview-first convention and writes
only when `--write` is passed.

## Module Inventory

`module_inventory.json` is the structured source used by the scripts. For each
module it records:

- module ID;
- C++23 module name;
- source directory;
- physical skill path;
- agent heading in `62-module-agents.md`;
- target design heading in `63-target-contract-interface-implementation-test-design.md`;
- contract test path;
- structured inputs;
- structured outputs;
- module-owned tools;
- allowed C++ module imports.

When architecture docs add or rename a module, update this inventory in the
same change.

## Agent Usage

Module agents should use the toolkit in this order:

1. `validate-docs` before changing module contracts.
2. `new-task-card` and `validate-task-card` before non-trivial or high-risk
   work that should persist beyond the current conversation.
3. `validate-inventory` after changing module IO, tool, or import metadata.
4. `emit-design-card --module <id>` to start a structured design report.
5. `scaffold-module --module <id>` to preview C++23 interface and
   implementation paths.
6. `scaffold-contract-test --module <id>` to preview contract-test placement.
7. `check-dependencies` after C++ imports change.
8. `validate-skills` after skill or agent metadata changes.

## Current Scope

The first toolkit layer intentionally avoids solving geometry. It gives agents
the infrastructure needed to implement modules safely:

- skill/catalog validation;
- design coverage validation;
- dependency boundary scanning;
- task-card creation and validation;
- design-card generation;
- C++23 module skeleton preview/write;
- contract-test skeleton preview/write.

Deeper tools such as residual/Jacobian checkers, fixture corpus generators,
schema migration runners, and golden report writers should be added as the
owning modules reach implementation.

## CI-Ready Quality Gate

`run-quality-gates` is the Step 18 pre-push and CI entry point. By default it
runs agentic design checks, scene-generation Python tests, CMake configure and
build, full CTest, the explicit `ContractToolsContract` fixture-corpus
selection, and a representative CLI smoke fixture.

Use `--continue-on-failure` when collecting a complete failure report. Use
skip flags only for narrow debugging or split CI jobs.

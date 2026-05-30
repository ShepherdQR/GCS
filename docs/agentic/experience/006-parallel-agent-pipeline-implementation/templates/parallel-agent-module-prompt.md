# Parallel Agent Module Prompt Template

Adapt this template for each agent when dispatching N modules in parallel.
Replace `{{PLACEHOLDER}}` tokens with concrete values per module.

---

## Task

Create exactly one file: `{{module_path}}`

This file must define a `{{PipelineClass}}` class with:

- A `run() -> PipelineResult` method (PipelineResult imported from
  `{{shared_contract_module}}`)
- A `from_preset(name: str, **overrides) -> {{PipelineClass}}` classmethod
  that supports at minimum `"smoke"`, `"standard"`, `"full"` presets
- A `__main__` block with argparse for direct CLI invocation

## Module Domain

{{one_paragraph_description_of_what_this_pipeline_does}}

## Shared Contract

Import PipelineResult from `{{shared_contract_module}}`. PipelineResult has
these fields (do not add or remove fields):

```python
@dataclass
class PipelineResult:
    pipeline_id: str          # e.g., "{{pipeline_id}}"
    status: str               # "pass" | "fail" | "error"
    stats: dict[str, Any]     # domain-specific metrics
    artifacts: list[str]      # paths to generated files
    errors: list[str]         # human-readable error messages
    runtime_seconds: float
```

## Constraints

- The module MUST be independently importable: `python -c "from {{module_import_path}} import {{PipelineClass}}"` must succeed
- Do NOT import from any other pipeline module (e.g., `tools.solver_testing.pipelines.other_module`). Shared tooling (`tools.solver_testing.runner`, `tools.solver_testing.defect_store`, etc.) is allowed.
- Include a `#!/usr/bin/env python3` shebang and `from __future__ import annotations`
- Ensure the repo root is on `sys.path` so tool imports resolve
- Wrap main logic in `if __name__ == "__main__":` with argparse

## Preset Budget

| Preset | Expected runtime | Key parameter differences |
|--------|-----------------|--------------------------|
| smoke  | {{smoke_runtime}} | {{smoke_params}} |
| standard | {{standard_runtime}} | {{standard_params}} |
| full | {{full_runtime}} | {{full_params}} |

## Output

One file at `{{module_path}}`. No other files. No modifications to
`__init__.py` or `run.py` — those will be integrated after all modules
are built.

## Verification

After writing, verify with:
```bash
python -c "from {{module_import_path}} import {{PipelineClass}}; print('OK')"
```

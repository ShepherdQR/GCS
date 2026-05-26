# Commands Attempted

## Environment symptom

Every local process launch failed before command execution with:

```text
windows sandbox: setup refresh failed with status exit code: 1
```

## Repo-state commands requested for the run

These were required before diagnostics but were not executable:

```powershell
git status --short --branch
git rev-parse HEAD
```

## Diagnostic commands requested for the run

```powershell
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
python tools\scene_generation\tools.py list
python -m unittest tests.tools.test_scene_generation_explorer
python tools\agentic_design\agentic_toolkit.py run-quality-gates --skip-build --skip-ctest --skip-cli --continue-on-failure
```

## Additional execution probes

The following simple probes were also attempted and failed with the same error before process start:

```powershell
Get-Location
```

Node-backed execution failed with the same sandbox setup symptom and did not produce a usable fallback runner.

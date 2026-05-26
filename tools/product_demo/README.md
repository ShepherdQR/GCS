# Product Demo Tools

This directory contains small repository-local tools that turn researcher
demo packages into repeatable evidence artifacts.

## Tools

| Tool | Purpose |
| --- | --- |
| `diagnostic_classification.py` | Runs the B1/D2 diagnostic classification cases and writes JSON evidence. |
| `d5_workbench_package.py` | Renders the static D5 Solver Evidence Workbench screenshot package and screenshot-baseline manifest from D2/D3 evidence. |
| `r1_package_smoke.py` | Runs the R1 researcher-preview smoke checks and writes JSON evidence. |
| `replay_evidence_check.py` | Validates the D3 replay evidence artifact for required fields, expected status, report codes, stage order, and durable commit semantics. |

These tools are evidence collectors, not solver logic. Expected outputs live
in project documents so reviewers can inspect and change the contract without
editing tool code.

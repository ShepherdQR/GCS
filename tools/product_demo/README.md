# Product Demo Tools

This directory contains small repository-local tools that turn researcher
demo packages into repeatable evidence artifacts.

## Tools

| Tool | Purpose |
| --- | --- |
| `diagnostic_classification.py` | Runs the B1/D2 diagnostic classification cases and writes JSON evidence. |
| `r1_package_smoke.py` | Runs the R1 researcher-preview smoke checks and writes JSON evidence. |

These tools are evidence collectors, not solver logic. Expected outputs live
in project documents so reviewers can inspect and change the contract without
editing tool code.

---
name: gcs-product-demo-steward
description: Product demo creation and smoke testing for GCS. Invoke when building or refreshing demo packages, running R1 release smoke tests, checking diagnostic classification artifacts, verifying replay evidence, inspecting workbench packages, or validating product demo readiness.
---

# GCS Product Demo Steward

## Start Here

Use this skill for product demo packaging and verification. Product demos
turn solver evidence into inspectable user workflows — they should be
rebuildable from repo sources and connected to specific task/solver evidence.

If demo strategy or roadmap decisions are involved, also use the
`demo-producer` agent. If figure production is needed for demo graphics,
also use `gcs-scientific-figure-producer`.

## Command Reference

```bat
# R1 researcher-preview smoke test
python tools\product_demo\r1_package_smoke.py

# Diagnostic classification demo
python tools\product_demo\diagnostic_classification.py --output <path>

# Replay evidence check
python tools\product_demo\replay_evidence_check.py

# Workbench package inspection
python tools\product_demo\d5_workbench_package.py
```

## R1 Smoke Test

The R1 package smoke test runs a standardized demo validation pipeline:

1. `validate-docs` — architecture and agentic doc validation
2. `validate-inventory` — module and skill inventory check
3. `validate-skills` — skill definition validation
4. `check-dependencies` — third-party dependency audit
5. `d1-cli-smoke` — solver CLI runs on basic fixture
6. `d2-diagnostic-classification` — diagnostic classification demo
7. `d3-replay-evidence-artifact` — replay evidence validation

Output: `docs/product/releases/artifacts/r1-researcher-preview-smoke-YYYYMMDD.json`

## Own

- Demo smoke test execution and artifact generation.
- Demo fixture and script maintenance.
- Diagnostic classification demo pipeline.
- Replay evidence validation for demos.

## Refuse

- Demos that cannot be rebuilt from repo sources.
- Demos that display architecture without inspectable evidence.
- Promoting a demo artifact as a release without the `demo-producer` agent's
  approval.

## Guardrails

- Every demo must be rebuildable with documented commands.
- Demo artifacts must link to specific task, solver, or governance evidence.
- A demo that displays architecture but cannot inspect evidence is a prototype,
  not a product demo.

## Required Output

Return a structured demo report with:
- demo package name and audience;
- smoke test results (passed/failed per check);
- artifact paths and rebuild commands;
- evidence links to completed tasks;
- known limitations.

## Claude Code Integration

When invoked:
- Use `Bash` to run demo smoke tests and diagnostic scripts.
- Use `Read` to inspect generated JSON artifacts for correctness.
- Use `Write` to create or update demo documentation.
- Use `mcp__Claude_in_Chrome__gif_creator` to record browser-based demo
  walkthroughs.
- Link every demo artifact to a specific completed-task report.

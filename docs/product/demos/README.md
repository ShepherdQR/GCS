# GCS Demo Packages

Status: seed
Date: 2026-05-26

This directory stores product-facing demo packages. A demo package should make
one project capability inspectable without requiring a reader to reconstruct
the whole architecture.

Demo packages should include:

- the user-facing claim;
- the artifact or workflow being demonstrated;
- evidence links;
- acceptance criteria;
- known limits;
- the next upgrade path.

Start with:

- `agentic-task-closure-demo/`: demonstrates the GCS agentic organization
  closing a non-trivial task from request to task card, validation, archive,
  commit, and push.
- `d5-solver-evidence-workbench/`: demonstrates the first Solver Evidence
  Workbench chain from showcase scene evidence to viewer projection contracts,
  Figure 72 review artifacts, VE-002 viewer canvas evidence, visual QA, and
  follow-up.

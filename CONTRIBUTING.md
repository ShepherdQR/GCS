# Contributing to GCS

GCS is an evidence-rich geometric constraint solving research workbench. Its
primary audience is solver and geometric-constraint researchers. This document
explains how to contribute effectively.

## Before You Start

Read the 20-minute contributor path:
[`docs/product/20-minute-contributor-path.md`](docs/product/20-minute-contributor-path.md)

Read the contribution boundary to understand what fits and what is deferred:
[`docs/product/researcher-contribution-boundary.md`](docs/product/researcher-contribution-boundary.md)

## Contribution Workflow

### 1. Find or Create a Task Card

Non-trivial changes require a task card. Create one with:

```bat
python tools\agentic_design\agentic_toolkit.py new-task-card --slug <slug> --scope <scope> --risk <risk> --owner <skill> --request "<request>" --write
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\<task>.md
```

Trivial changes (typos, link fixes, formatting-only) may skip the task card.

### 2. Make Your Change

- Keep changes scoped to the task card.
- Do not stage unrelated files.
- Follow existing code and documentation conventions.

### 3. Validate

```bat
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
```

For solver or C++ changes, also run:

```bat
scripts\run_quality_gates.cmd
```

### 4. Review Staged Files

```bat
git diff --cached --name-status
```

Verify that only task-owned files are staged.

### 5. Commit

Write a concise commit message that explains *why*, not *what*.

### 6. Open a Pull Request

Use the PR template. Ensure the checklist is complete before requesting review.

## Good First Contributions

- Clarify a doc link or index reference
- Add evidence to an existing task archive
- Classify one saved fixture under the corpus maturity ladder
- Add a D1 or D2 demo note without changing solver behavior
- Add a negative test case for a documented limitation

## What To Avoid As A First Contribution

- Solver semantics changes
- IO schema migrations
- Dependency changes
- Fixture promotion
- Branch cleanup
- UI state ownership changes

## Review Process

- First response within 5 business days for PRs.
- Acknowledge issues within 3 business days.
- PRs that touch solver semantics, IO schema, or architecture require maintainer
  review.
- Documentation and fixture contributions use lazy consensus: if no objection
  within 5 business days, the contributor may merge.

## Contributor License

By contributing to GCS, you agree that your contributions will be licensed
under the Apache License 2.0 (see [LICENSE](LICENSE)).

## Questions

Open an issue or contact the maintainers listed in
[GOVERNANCE.md](GOVERNANCE.md).

# GCS — Geometric Constraint Solver

A C++23 geometric constraint solver with Python visualization, governed by
an agentic software engineering operating layer.

## Project Organization

```
.Codex/
  skills/       22 domain-specific steward skills (Codex format)
  agents/        8 institutional agent role definitions
docs/
  architecture/  Durable solver architecture and target contracts
  agentic/       Agentic SE operating layer, lifecycle, governance
  research/      Research notes and investigation records
  completed-tasks/  Archived task reports with evidence bundles
src/gcs/         C++ solver modules (kernel, IO, graph, numeric, etc.)
apps/gcs_cli/    CLI application
python/gcs_viz/  Local tkinter+matplotlib visualization
fixtures/scene/  Solver test fixtures
tools/           Generation, visualization, and agentic tooling
```

## Key Architecture Docs

| Document | Purpose |
|----------|---------|
| `docs/architecture/62-module-agents.md` | Module agent contracts per domain |
| `docs/architecture/63-target-contract-interface-implementation-test-design.md` | Target contract and test architecture |
| `docs/architecture/00-foundations/topos-semantic-model.md` | Topos semantic model foundations |
| `docs/architecture/20-solver-pipeline/` | Solver pipeline architecture |
| `docs/architecture/30-contracts/` | Domain and solver contracts |
| `docs/agentic/agentic-organization-operating-map.md` | Operating map for agentic SE |
| `docs/agentic/institutional-agent-registry-and-scorecard.md` | Agent registry and promotion rules |
| `docs/agentic/lifecycle-runbook.md` | Task lifecycle from request to push |

## Build Commands

```bat
# C++ solver build
scripts\build_clang_ninja.cmd

# Run solver on a fixture
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt

# Python GUI
scripts\start_gui.cmd

# Python compile check
python -m compileall -q python\gcs_viz
```

## Agentic Toolkit

```bat
# Validate all docs
python tools\agentic_design\agentic_toolkit.py validate-docs

# Validate a task card
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\<task>.md

# Validate and score a completed-task report
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\<task>\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\<task>\README.md --min-score 30
```

## Task Card Requirement

Before mutating files for non-trivial work, create a task card:

```bat
python tools\agentic_design\agentic_toolkit.py new-task-card --slug <slug> --scope <scope> --risk <risk> --owner <skill> --request "<request>" --write
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\<task>.md
```

Skip only for typos, link fixes, formatting-only changes, or read-only answers.
When uncertain, create the card. For multi-session work, one card spans the arc.

## Skill Invocation

Codex auto-invokes skills based on description matching. Key skills:

| When changing... | Skill auto-invoked |
|-----------------|-------------------|
| Architecture docs, cross-module refactors | `gcs-architecture-steward` |
| C++ solver code, CMake | `gcs-cpp-solver-maintainer` |
| Python GUI, tkinter, matplotlib | `gcs-python-gui-builder` |
| Scene formats, JSON, history | `gcs-scene-behavior-steward` |
| Contract tests, quality gates | `gcs-quality-steward` |
| Visual tokens, UI aesthetics | `gcs-ui-design-steward` |
| Non-trivial task closure | `task-scoped-session-closer` |

## Workspace Conventions

- Use `git worktree` for parallel writing sessions
- Follow the task card requirement above for non-trivial work
- Archive completed work at `docs/completed-tasks/<date-slug>/`
- Stage only scoped files; commit with concise messages
- Preserve unrelated dirty worktree changes
- Do not archive raw chat logs; archive refined decisions and evidence

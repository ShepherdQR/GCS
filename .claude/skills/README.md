# GCS Claude Code Skills Index

This directory contains Claude Code-compatible skill definitions converted
from the `.codex/skills/` directory. Each skill governs a specific module,
boundary, or process domain in the GCS project.

## Solver Core Skills

| Skill | Domain | Key trigger |
|-------|--------|-------------|
| [gcs-architecture-steward](gcs-architecture-steward/SKILL.md) | Cross-module architecture | Architecture doc changes, cross-module refactors, dependency direction |
| [gcs-kernel-contract-steward](gcs-kernel-contract-steward/SKILL.md) | Kernel contracts | Stable IDs, snapshots, state deltas, report codes |
| [gcs-constraint-semantics-steward](gcs-constraint-semantics-steward/SKILL.md) | Constraint catalog | Constraint definitions, evaluators, Jacobians, degeneracy |
| [gcs-incidence-structure-steward](gcs-incidence-structure-steward/SKILL.md) | Incidence graph | Hypergraphs, connectivity, structural projections |
| [gcs-decomposition-planning-steward](gcs-decomposition-planning-steward/SKILL.md) | Decomposition planner | Cover plans, boundary projections, solve DAGs |
| [gcs-numeric-engine-steward](gcs-numeric-engine-steward/SKILL.md) | Numeric engine | Local solves, residuals, Jacobians, numeric traces |
| [gcs-diagnostics-certification-steward](gcs-diagnostics-certification-steward/SKILL.md) | Diagnostics | DOF, rank, residual, gluing, obstruction evidence |
| [gcs-session-runtime-steward](gcs-session-runtime-steward/SKILL.md) | Session runtime | Commands, transactions, history, undo/redo |

## Boundary and Integration Skills

| Skill | Domain | Key trigger |
|-------|--------|-------------|
| [gcs-io-adapter-steward](gcs-io-adapter-steward/SKILL.md) | IO adapters | Scene schemas, serialization, migrations, round-trips |
| [gcs-viewer-bridge-steward](gcs-viewer-bridge-steward/SKILL.md) | Viewer bridge | Scene projection, diagnostic overlays, interaction commands |
| [gcs-scene-behavior-steward](gcs-scene-behavior-steward/SKILL.md) | Scene behavior | Scene formats, JSON behavior, history replay, IO compatibility |
| [gcs-cpp-solver-maintainer](gcs-cpp-solver-maintainer/SKILL.md) | C++ solver | src/gcs, CMake, CLI, C++23 module boundaries |
| [gcs-python-gui-builder](gcs-python-gui-builder/SKILL.md) | Python GUI | tkinter, matplotlib, viewer bridge, GUI behavior |
| [gcs-scene-generation-engineer](gcs-scene-generation-engineer/SKILL.md) | Scene generation | Synthetic graphs, validation, repair, fixture promotion |

## Quality and Governance Skills

| Skill | Domain | Key trigger |
|-------|--------|-------------|
| [gcs-quality-steward](gcs-quality-steward/SKILL.md) | Quality gates | Contract tests, CTest, negative fixtures, CI matrix |
| [gcs-contract-tools-steward](gcs-contract-tools-steward/SKILL.md) | Contract tools | Fixture builders, invariant checkers, golden reports |
| [gcs-third-party-governance-steward](gcs-third-party-governance-steward/SKILL.md) | Third-party governance | Dependencies, licensing, CMake adapters, SBOM |
| [gcs-ui-design-steward](gcs-ui-design-steward/SKILL.md) | UI design | Visual tokens, design-system conventions, visual QA |
| [gcs-ui-qa-steward](gcs-ui-qa-steward/SKILL.md) | UI QA | Theme tokens, contrast ratios, GUI static analysis, headless render |
| [gcs-scientific-figure-producer](gcs-scientific-figure-producer/SKILL.md) | Scientific figures | Figure specs, semantic composition, visual QA |

## Audit and Demo Skills

| Skill | Domain | Key trigger |
|-------|--------|-------------|
| [gcs-repository-audit-steward](gcs-repository-audit-steward/SKILL.md) | Repository audit | File classification, snapshots, diffs, trend reports, archive deltas |
| [gcs-token-audit-steward](gcs-token-audit-steward/SKILL.md) | Token audit | Session token/cost tracking, BEI scoring, trend reports |
| [gcs-product-demo-steward](gcs-product-demo-steward/SKILL.md) | Product demo | Smoke tests, diagnostic classification, replay evidence |
| [gcs-benchmark-steward](gcs-benchmark-steward/SKILL.md) | Benchmark execution | External solver comparison, benchmark fixtures, reproducibility standards |

## Process Skills

| Skill | Domain | Key trigger |
|-------|--------|-------------|
| [session-close-orchestrator](session-close-orchestrator/SKILL.md) | **Session close pipeline** | **Single entry point — sequences all close steps** |
| [task-scoped-session-closer](task-scoped-session-closer/SKILL.md) | Session closure | Task archives, evidence bundles, commit/push handoff |
| [git-session-branch-steward](git-session-branch-steward/SKILL.md) | Git session governance | Branch/worktree safety, push payload scoping, dirty-file protection |

## Institutional Agents

Agent role definitions live in `.claude/agents/`:

| Agent | Maturity | Purpose |
|-------|----------|---------|
| [bladesmith-quench-forge](../agents/bladesmith-quench-forge.md) | Promoted | Extract reusable operational lessons |
| [tailor-stitch-timeline](../agents/tailor-stitch-timeline.md) | Practiced | Maintain multi-session timelines |
| [atelier-steward-calibrate-review](../agents/atelier-steward-calibrate-review.md) | Seed | Review UI against design conventions |
| [art-director-frame-judge](../agents/art-director-frame-judge.md) | Seed | Independent visual judgment |
| [acceptance-officer](../agents/acceptance-officer.md) | Seed | Independent evidence review before completion |
| [governance-sentinel](../agents/governance-sentinel.md) | Candidate | Permission and audit governance |
| [demo-producer](../agents/demo-producer.md) | Candidate | Product demo creation |
| [benchmark-scout](../agents/benchmark-scout.md) | Candidate | External solver comparison |
| [release-shepherd](../agents/release-shepherd.md) | Candidate | Release readiness |
| [night-watch](../agents/night-watch.md) | Candidate | Nightly diagnostics and patrol |
| [acceptance-officer](../agents/acceptance-officer.md) | Candidate | Independent evidence review before completion |
| [collation-officer](../agents/collation-officer.md) | Candidate | Cross-read docs, code, tests for consistency |
| [bookkeeper](../agents/bookkeeper.md) | Candidate | Token/cost/value budget tracking |
| [gardener](../agents/gardener.md) | Candidate | Small friction, debt, and maintenance |
| [git-session-steward](../agents/git-session-steward.md) | Candidate | Git session state, branch/worktree hygiene, push safety |

## Conversion Notes

These skills are converted from `.codex/skills/` (Codex/OpenAI format). Key
changes from the originals:

1. **Removed `agents/openai.yaml`**: Codex-specific interface files replaced
   by Claude Code's native SKILL.md frontmatter
2. **Enhanced descriptions**: Frontmatter `description` fields are optimized
   for Claude Code's skill auto-invocation system
3. **Added "Claude Code Integration" sections**: Each skill now documents how
   to use Claude's specific tools (Read, Edit, Grep, Bash, Agent, MCP tools)
4. **Agent definitions centralized**: Institutional agents moved from
   `docs/agentic/institutional-agents/` to `.claude/agents/` with Claude Code
   frontmatter

The original `.codex/skills/` files remain intact as the authoritative source
for the 20 solver, boundary, and quality skills they cover. Five Claude Code-only
skills (`gcs-repository-audit-steward`, `gcs-ui-qa-steward`,
`gcs-product-demo-steward`, `gcs-token-audit-steward`, `session-close-orchestrator`)
exist only in this directory — they are operational skills built for the Claude
Code agentic-SE layer and do not have `.codex` counterparts. If a Claude-only
skill stabilizes into a general contract, backport it to `.codex/skills/`. These
`.claude/skills/` files are the operational Claude Code interface layer.

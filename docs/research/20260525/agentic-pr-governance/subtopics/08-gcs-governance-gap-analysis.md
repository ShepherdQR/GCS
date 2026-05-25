# GCS Governance Gap Analysis

Date: 2026-05-25

## Question

How does current GCS governance compare to leading agentic software-governance
practice, and what should be added next?

## Current Strengths

GCS has strong foundations:

- task cards for non-trivial work;
- completed-task archives;
- closure scoring;
- opt-in artifact gates;
- lifecycle runbook from request to push;
- trace schema for concise replayable work records;
- module-agent ownership;
- architecture steward boundary rules;
- quality-gate command with docs, inventory, skills, dependencies, Python
  tests, build, CTest, CLI, and visual checks;
- scene auto explorer with deterministic exploration and promotion-package
  precedent;
- worktree protocol for parallel writing sessions.

This is already close to enterprise-grade agentic governance at the local
repository level.

## Gaps

### PRs Are Not Yet First-Class Governance Objects

Task cards and archives exist, but there is no stable PR audit checklist that
translates those artifacts into review-time expectations. A future reviewer
should not need to reconstruct risk from scattered docs.

### Exploratory PRs Need A Policy

The project uses exploration heavily. Exploratory branches are valuable, but
they need explicit draft status, bounded goal, non-merge default, and a path
for promotion into a formal task if findings become durable.

### Nightly Runs Need A Durable Run Schema

The long-term plan mentions scheduled agents, but there is no run artifact
contract for recurring diagnostics. Without it, nightly work can become a pile
of logs.

### Repair Authority Is Not Explicit Enough

Existing policies forbid many unsafe actions implicitly, but nightly agents
need a concrete repair matrix: report-only, patch candidate, task-card-required,
human-gate-required, forbidden.

### Metrics Are Present As Concepts, Not Run Data

The long-term plan names metrics. The nightly workflow should start emitting
simple local metrics so the project can observe trends before building any
dashboard.

## Additions Recommended By This Task

1. `docs/agentic/pr-audit-governance.md`
   Adds PR class, risk, evidence, review focus, exploratory PR policy, and
   automated audit output contract.

2. `docs/agentic/nightly-immune-diagnostics.md`
   Adds scheduled run stages, outputs, taxonomy, repair boundaries, and
   automation prompt contract.

3. Codex automation
   Installs a recurring worktree-mode nightly diagnostic run that reports
   findings without unattended merge or push.

## Design Principle

Do not add ceremony for its own sake. Add the minimum durable structure that
makes future PRs and nightly runs inspectable, repeatable, and safe to ignore
when they find nothing important.

# GCS Solution Design: Process AI Token Economy

Date: 2026-05-26

Status: proposed design.

Scope: design a GCS-specific solution for institutional/process AI tasks that
consume many tokens through repeated document reading, writing, synchronization,
evidence capture, and closeout. This is a docs/design proposal, not an
implemented tool change.

## Problem Statement

GCS has intentionally built a strong agentic-SE lifecycle: task cards,
architecture/runbook context, evidence bundles, completed-task archives,
institutional-agent examples, session-efficiency reports, and validation gates.
This discipline prevents false completion and preserves project memory.

The cost is that process work is becoming token-heavy. A non-trivial task may
need to read and update many documents:

- lifecycle runbook;
- task-to-archive checklist;
- task card;
- research report;
- source register;
- completed-task archive;
- completed-task index;
- institutional-agent registry;
- session-efficiency report;
- roadmap or metrics dashboard;
- prior related reports.

If each session re-reads these artifacts as prose and rewrites them manually,
GCS pays a high token tax for governance. The objective is not to remove the
governance. The objective is to make the governance cheaper, more structured,
and more reliable.

## Design Goals

1. Reduce repeated context loading for institutional/process tasks.
2. Preserve or improve evidence quality, source traceability, and closure
   discipline.
3. Convert recurring Markdown operations into deterministic or semi-deterministic
   tools.
4. Keep human judgment focused on claims, risk, source quality, and promotion
   decisions.
5. Make token cost measurable against durable output and validation quality.
6. Avoid creating a new agent role unless repeated examples justify promotion.

## Non-Goals

- Do not change solver/runtime/IO/viewer behavior.
- Do not replace the lifecycle runbook or completed-task archive system.
- Do not make token minimization a blocking gate before a calibrated baseline.
- Do not promote a new institutional agent from this single task.
- Do not treat public benchmark performance as proof that a GCS process is
  safe.

## Core Design

GCS should add a lightweight "process AI operating layer" around the existing
agentic lifecycle.

```text
User request
  -> TaskCard
  -> ContextPack
  -> Execution and EvidenceLedger
  -> DeterministicDocUpdates
  -> Validators
  -> ArchiveScaffold
  -> SessionEfficiencyRecord
  -> LearningOrEvalCandidate
```

The key move is to make every expensive recurring process object explicit.
The LLM should synthesize and judge. Tools should locate, extract, update,
validate, and summarize whenever the operation is mechanical.

## Architecture Components

### 1. Task State File

Current task cards are valuable, but they are Markdown-first. Add an optional
machine-readable companion for non-trivial tasks:

```text
docs/agentic/tasks/state/
  2026-05-26-institutional-process-ai-token-economics.task-state.json
```

Suggested schema:

```json
{
  "schema_version": "gcs-task-state-0.1",
  "task_id": "2026-05-26-example",
  "status": "in_progress",
  "task_class": "research_design",
  "scope": "docs",
  "risk": "medium",
  "owner": "task-scoped-session-closer",
  "hot_summary": "One paragraph of current state.",
  "affected_paths": [],
  "required_sources": [],
  "evidence_ledger": "docs/agentic/tasks/state/2026-05-26-example.evidence.jsonl",
  "context_pack": "docs/agentic/tasks/state/2026-05-26-example.context-pack.md",
  "acceptance": [],
  "open_risks": []
}
```

Purpose:

- store current task state without rereading the whole archive;
- provide a compact handoff after compaction/resume;
- let tools join task state, evidence, archive, and session-efficiency records.

### 2. Context Pack Builder

Add a tool that builds a task-specific context pack from local docs and optional
web/source registers:

```bat
python tools\agentic_design\agentic_toolkit.py build-context-pack --task docs\agentic\tasks\<task>.md --output docs\agentic\tasks\state\<task>.context-pack.md
```

The context pack should contain:

- task objective and risk;
- relevant local source paths with short extracted snippets;
- web/source register entries if research is in scope;
- acceptance gates;
- known non-goals;
- exact files likely to be edited;
- estimated token size or line count;
- omitted sources and why.

Context tiers:

| Tier | Contents | Loading rule |
| --- | --- | --- |
| Hot | Current task state, latest decisions, changed files, required checks | Always load |
| Warm | Relevant runbook slices, recent related archives, source summaries | Load by task class |
| Cold | Full reports, old archives, raw logs, broad docs | Retrieve only on demand |

The context pack is a contract: if a source is not in the pack, the agent should
not pretend to rely on it.

### 3. Source Register Store

Research reports currently include useful source registers, but they are local
to each report. Add a reusable JSONL source register for recurring external and
local sources:

```text
docs/agentic/source-register/
  sources.jsonl
  claims.jsonl
```

Example `sources.jsonl` record:

```json
{
  "source_id": "openai-practical-agent-guide-2025",
  "url": "https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf",
  "title": "A Practical Guide to Building Agents",
  "publisher": "OpenAI",
  "accessed_at": "2026-05-26",
  "confidence": "high",
  "topics": ["agents", "guardrails", "orchestration", "tools"]
}
```

Example `claims.jsonl` record:

```json
{
  "claim_id": "agent-workflow-needs-tools-guardrails",
  "source_id": "openai-practical-agent-guide-2025",
  "claim": "Agents are most appropriate when workflows require model-driven decisions, tools, guardrails, and state.",
  "used_in": [
    "docs/research/20260526/institutional-process-ai-token-economics/01-research-report.md"
  ]
}
```

Purpose:

- avoid rebuilding the same source table in every report;
- make source reuse explicit;
- allow future agents to retrieve sources by topic instead of web-searching
  again.

### 4. Evidence Ledger

Add a task-local append-only ledger:

```text
docs/agentic/tasks/state/
  <task>.evidence.jsonl
```

Suggested record:

```json
{
  "timestamp": "2026-05-26T00:00:00+08:00",
  "kind": "command",
  "command": "python tools\\agentic_design\\agentic_toolkit.py validate-task-card docs\\agentic\\tasks\\<task>.md",
  "result": "pass",
  "summary": "[OK] task-card passed.",
  "paths": ["docs/agentic/tasks/<task>.md"]
}
```

The completed-task archive should be generated from this ledger first, then
edited by the agent for judgment and narrative. This converts closure from
"remember everything that happened" to "summarize a structured trace."

### 5. Section-Aware Markdown Updater

Many GCS process edits are structured Markdown updates:

- add a row to `docs/completed-tasks/README.md`;
- update task-card evidence;
- append source rows;
- mark checklist items;
- add a reading-order entry;
- update a metrics table.

These should not require full-document reasoning every time. Add section-aware
helpers that locate a heading/table by anchor and perform controlled edits.

Candidate commands:

```bat
python tools\agentic_design\agentic_toolkit.py add-completed-task-index --archive docs\completed-tasks\<task>\README.md
python tools\agentic_design\agentic_toolkit.py append-task-evidence --task docs\agentic\tasks\<task>.md --command "<cmd>" --result pass --summary "<summary>"
python tools\agentic_design\agentic_toolkit.py add-source-row --report <report.md> --source-id openai-practical-agent-guide-2025
```

The rule: deterministic table/index changes should be tools; the LLM should
only decide content and risk.

### 6. Archive Scaffold Generator

The existing completed-task validator is valuable. Add a generator that reads
the task card plus evidence ledger and emits the first draft:

```bat
python tools\agentic_design\agentic_toolkit.py scaffold-completed-task-from-evidence --task docs\agentic\tasks\<task>.md --write
```

The generated archive should include:

- task objective;
- scope and non-goals;
- files/artifacts changed;
- evidence commands and pass/fail summary;
- skipped checks and rationale;
- decisions;
- residual risks;
- experience/skill/agent promotion decision;
- next action.

This cuts token use at the most common expensive closeout step while preserving
the human-readable report.

### 7. Token And Value Telemetry

GCS already has `docs/architecture/95-agentic-session-efficiency-governance.md`
and `tools/session_efficiency/`. Extend the record to reference process
artifacts:

```json
{
  "task_id": "2026-05-26-example",
  "task_class": "research_design",
  "context_pack_tokens_estimated": 8200,
  "repeated_source_reads": 3,
  "deterministic_doc_updates": 4,
  "manual_doc_updates": 2,
  "token_telemetry": {
    "total_tokens": 0,
    "confidence": "unknown"
  }
}
```

Useful metrics:

| Metric | Meaning |
| --- | --- |
| `ContextPackSize` | Estimated tokens or lines in the task pack |
| `HotStateSize` | Size of always-loaded current state |
| `SourceReuseRate` | Share of source claims reused from register |
| `DocAutomationRatio` | Deterministic doc updates / total doc updates |
| `ArchiveScaffoldCoverage` | Archive sections generated from ledger |
| `EvidenceCompleteness` | Required evidence entries present |
| `ReworkPenalty` | Failed/skipped checks and unresolved risks |
| `ValuePer1KTokens` | Existing session-efficiency score when token telemetry is known |

Do not make token metrics blocking until enough records exist for calibration.

### 8. Process Evals

Add lightweight negative evals for institutional/process agents:

| Eval | Failure caught |
| --- | --- |
| Refuse unsupported source claim | Report cites a source that does not support the claim |
| Refuse full-runbook context dump | Context pack includes broad docs without task relevance |
| Refuse archive without evidence | Completed-task report claims done without commands/results |
| Refuse invented causality | Timeline or archive invents why an event happened |
| Refuse role promotion from one sample | Institutional agent promoted without repeated evidence |
| Refuse token-only optimization | Report recommends skipping checks only to save tokens |

These evals should live under `docs/agentic/evals/governance/` or a future
process-specific eval folder.

## Workflow Design

### Intake

1. Classify task class, scope, risk, and owner.
2. Create task card.
3. Create or update task-state JSON.
4. Generate context pack.
5. Ask the LLM to confirm whether the pack is sufficient.

### Research

1. Search external sources only when freshness or source attribution matters.
2. Add sources to report-local register and, if reusable, global source
   register.
3. Record each major claim with a source or mark it as inference.
4. Keep raw source summaries short.

### Execution

1. Use deterministic tools for mechanical updates.
2. Use LLM synthesis for findings, decisions, risk, and recommendations.
3. Append command/result records to the evidence ledger.
4. Keep the hot task-state summary current.

### Verification

1. Run task-card validator.
2. Run completed-task validator if an archive exists.
3. Run `validate-docs` for docs-only architecture/agentic work when scoped.
4. Record skipped build/CTest/UI checks as scope decisions, not passes.

### Closure

1. Scaffold completed-task archive from task card and evidence ledger.
2. Add source/report links.
3. Record experience/skill/agent promotion decision.
4. Update completed-task index with a section-aware tool.
5. Generate or update session-efficiency record if telemetry is available.

## GCS File Layout

Proposed additions:

```text
docs/agentic/source-register/
  sources.jsonl
  claims.jsonl

docs/agentic/tasks/state/
  <task>.task-state.json
  <task>.context-pack.md
  <task>.evidence.jsonl

docs/agentic/evals/governance/
  e-gov-009-refuse-full-runbook-context-dump.md
  e-gov-010-refuse-unsupported-source-claim.md
  e-gov-011-refuse-token-only-optimization.md

tools/agentic_design/
  # extend agentic_toolkit.py commands rather than create a new tool family first
```

Why use existing `tools/agentic_design/` first:

- it already owns task cards, archives, docs validation, PR audit, and lifecycle
  helpers;
- the problem is process lifecycle, not solver runtime;
- one tool namespace reduces discovery cost for future agents.

## Implementation Roadmap

### Phase 0: Design Baseline

Deliverables:

- this research bundle;
- task card and completed-task archive for the design task;
- no tool changes yet.

Acceptance:

- reports exist and are source-aware;
- task card and archive validate;
- skipped non-doc checks are recorded.

### Phase 1: Context Pack MVP

Deliverables:

- `build-context-pack` command;
- task-state JSON schema;
- context pack Markdown output;
- tests for selecting runbook slices and affected paths.

Acceptance:

- a docs-only task can start from a context pack under a configured size limit;
- omitted sources are listed;
- task card validation still passes.

### Phase 2: Evidence Ledger And Archive Scaffold

Deliverables:

- append evidence command;
- scaffold completed archive from evidence;
- completed-task index update helper.

Acceptance:

- one real task closes with an archive generated mostly from structured
  evidence;
- manual edits are limited to judgment, decisions, and residual risks;
- validator and closure score pass.

### Phase 3: Source Register Reuse

Deliverables:

- global `sources.jsonl` and `claims.jsonl`;
- report helper to import source rows;
- duplicate-source detector.

Acceptance:

- repeated sources such as OpenAI/Anthropic/McKinsey/BCG are not re-summarized
  from scratch for every report;
- reports still contain readable source registers.

### Phase 4: Token/Value Dashboard

Deliverables:

- session-efficiency join with context pack and evidence ledger;
- task-class-specific charts or Markdown tables;
- outlier review convention.

Acceptance:

- unknown token counts remain allowed;
- known-token records compute value-per-token;
- dashboards do not compare research, implementation, and closure as one
  bucket.

### Phase 5: Process Evals And Role Decisions

Deliverables:

- governance evals for unsupported sources, context bloat, false closure, and
  token-only optimization;
- promotion review for existing candidate roles such as `Curator`/source map
  and `Bursar`/measure-tradeoff if repeated examples justify them.

Acceptance:

- no new institutional agent is promoted from a single example;
- eval failures produce concrete repair tasks.

## Permission And Safety Model

Default permissions for this process layer:

| Action | Default |
| --- | --- |
| Read repo docs | Allowed |
| Write task state, context pack, evidence ledger | Allowed inside task scope |
| Update completed-task index | Allowed after archive exists |
| Browse web | Allowed only for research/freshness tasks |
| Modify solver/runtime code | Not part of this layer |
| Run build/CTest | Only when task scope requires |
| Delete files, reset branches, force push | Human approval required |
| Add dependencies or external services | Human approval required |
| Promote institutional agents | Human gate and evidence required |

Security rule:

```text
Do not combine private data, untrusted web/document content, and external
communication in one autonomous process without explicit human approval and
capability separation.
```

## Expected Token Savings

The biggest savings should come from:

1. not rereading broad runbooks when a context pack has selected the relevant
   slices;
2. not reconstructing task history from chat after compaction or resume;
3. not rewriting completed-task archives from memory;
4. not rebuilding source registers for recurring sources;
5. not loading stale institutional-agent docs unless the role is actually in
   scope;
6. preserving stable prompt prefixes and moving variable task context later.

Savings should be measured as lower repeated-source reads, smaller hot context,
higher source reuse, fewer manual doc updates, and eventually lower tokens per
validated durable output.

## Risks

| Risk | Mitigation |
| --- | --- |
| Over-compression hides important nuance | Context packs must list omitted sources and open uncertainty |
| Structured state drifts from Markdown | Validators compare task card, state JSON, archive, and evidence ledger |
| Tools make wrong mechanical edits | Section-aware commands must be small, tested, and diff-reviewable |
| Token metrics incentivize skipping evidence | Keep token metrics non-blocking and pair them with closure/rework scores |
| Source register becomes stale | Store accessed dates and confidence; refresh when claims are temporal |
| Role inflation resumes under new names | Use current institutional-agent scorecard and promotion rules |
| Process layer becomes another document burden | Automate generation first; require measurable reduction in manual closeout |

## Recommended Next Action

Implement Phase 1 and Phase 2 together in one bounded tool task:

```text
Task: context-pack and evidence-ledger MVP
Scope: tools/agentic_design plus docs/agentic/tasks/state examples
Risk: medium
Evidence: unit tests for context pack selection, task-card validation,
completed-task validation, validate-docs
```

This is the smallest useful implementation because context packs reduce task
startup cost and evidence ledgers reduce task closeout cost. Together they
attack both ends of the token-heavy process loop.


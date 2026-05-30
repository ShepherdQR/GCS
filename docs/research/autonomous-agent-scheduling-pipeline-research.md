# Autonomous Agent Session Startup & Scheduling — Complete Research

**Date:** 2026-05-30
**Status:** Research Report Collection
**Scope:** US/European production systems, Claude Code Routines, external schedulers, GCS integration plan

---

## 1. The Trigger Taxonomy

Across all surveyed systems, agent session startup falls into exactly **5 trigger categories**:

| # | Trigger Type | Mechanism | Examples |
|---|---|---|---|
| T1 | **Cron / Schedule** | Time-based recurring execution | Claude Code Routines (`/schedule`), Optio cron, OSC My Agent Tasks, Friday (18 cron jobs) |
| T2 | **Webhook / API** | External HTTP POST fires agent | Routines API endpoint, Optio webhooks, Cursor Automations webhook |
| T3 | **GitHub Event** | PR/issue/push/check-run webhook | Routines GitHub events, Pullfrog, GitHub Agentic Workflows, cicaddy MR Agent |
| T4 | **Telemetry / Alert** | Monitoring system fires on threshold | NeuBird AI (continuous telemetry), Resolve AI (alert→auto-fix), Datadog→Routines |
| T5 | **Inter-Agent Message** | Agent A sends message to Agent B | Optio Persistent Agents (internal HTTP API), Kore.ai agent-to-agent federation |

**Key insight**: No production system uses "agent polls for work." All use push-based triggers — an external scheduler or event source pushes work to the agent.

---

## 2. Claude Code Routines (Anthropic, April 2026)

The **native solution** for GCS. Routines run on Anthropic's cloud infrastructure — laptop can be off.

### Architecture

```
Schedule (cron) / API (POST) / GitHub Event (webhook)
  → Anthropic Cloud Infrastructure
    → Claude Code session (isolated)
      → Clone repo
      → Execute prompt with allowed tools
      → Write outputs back to repo / Slack / Linear
    → Session URL returned (for monitoring)
```

### Trigger Details

| Trigger | Configuration | Use Case for GCS |
|---|---|---|
| **Scheduled** | hourly, nightly, weekly, or custom cron | Night-watch patrol, daily token audit, weekly doc drift scan |
| **API** | Unique endpoint + auth token per routine; POST payload→session | CI/CD hook: deploy→smoke test, alert→triage |
| **GitHub Events** | PR, push, issue, check-run; one session per PR with ongoing updates | Auto code review on PR, issue→task-intake |

### Limits

| Plan | Runs/Day | Extra Usage |
|---|---|---|
| Pro | 5 | Available |
| Max | 15 | Available |
| Team/Enterprise | 25 | Available |

### State Model

GitHub-triggered sessions persist and receive ongoing updates (comments, CI status changes). Cron/API sessions are one-shot — state must be persisted to repo files between runs (MEMORY.md, state.json, checkpoint in task card).

### Relevance to GCS

**Routines solve the "first push" problem.** GCS's `task-intake` → `orchestrator` → `session-close-orchestrator` pipeline is complete but needs a trigger. A Routine can be that trigger:

```
Routine: "GCS Night-Watch Patrol"
  Schedule: 0 2 * * * (2am daily)
  Prompt: "Run night-watch diagnostics. If clean, commit and push health report.
           If issues found, create task cards."
  Repo: ShepherdQR/GCS_A
```

```
Routine: "GCS PR Code Review"
  Trigger: GitHub PR opened
  Prompt: "Review the PR changes. Check: architecture compliance, test coverage,
           documentation updates. Post review summary as PR comment."
  Repo: ShepherdQR/GCS_A
```

---

## 3. External Scheduler Patterns

### 3.1 Optio (Open Source, MIT) — Full CI/CD Agent Platform

**Architecture**: Kubernetes-native, three-tier work model, PostgreSQL + Redis state.

| Tier | What It Does | GCS Equivalent |
|---|---|---|
| **Tasks** | Ticket→merged PR with autonomous feedback loop (CI fails→auto-resume, review→auto-fix, pass→auto-merge) | task-intake→orchestrator→PR |
| **Jobs** | Standalone agent runs (cron/webhook/manual), no git checkout needed | Night-watch, token audit |
| **Persistent Agents** | Long-lived, message-driven, always-on/sticky/on-demand pods | orchestrator as persistent agent |

**Key feature: Autonomous feedback loop.** When CI fails, Optio automatically resumes the agent with failure context. When review requests changes, agent picks up comments and pushes a fix. This is the missing piece for GCS's orchestrator — currently orchestrator can detect failures but cannot auto-resume.

**Trigger unification**: All 5 trigger types (T1-T5) work across all three tiers via a single reconciliation control plane.

### 3.2 OSC My Agent Tasks — Simple Cloud Cron

**Architecture**: Scheduler polls every 60s → spawns ephemeral container → `claude-runner` executes → outputs committed to repo.

**State**: No built-in persistence. Each run is isolated. State passes via git commits.

**Key insight**: "Your CI system is the scheduler, executor, and audit trail" (Red Hat cicaddy). This is the simplest pattern — cron fires, container runs, git is the state store.

### 3.3 Friday — 18 Cron Jobs on Claude Code Max Plan

**Architecture**: 18 independent cron jobs on Claude Code Max plan ($200/month), each with a specific responsibility. Self-healing: if a cron fails, another cron detects and retries.

**Key insight**: No external infrastructure needed. Claude Code's built-in scheduling (Routines, `/schedule`) plus Max plan (15 runs/day, extensible) is sufficient for a personal-scale autonomous system.

### 3.4 GitHub Agentic Workflows (Microsoft, Feb 2026)

**Architecture**: Markdown-defined workflows compiled to GitHub Actions YAML. Agents: Claude Code, Copilot, Codex. Sandboxed containers with read-only repo access by default.

**Key insight**: The CI system *is* the agent runtime. No separate scheduler needed. GitHub Actions provides the trigger infrastructure; the agent workflow provides the intelligence.

### 3.5 Red Hat cicaddy — CI-Native Agent Framework

**Architecture**: Platform-agnostic. DSPy task definitions (YAML) in repo. MCP servers as integration layer. One-shot execution with multi-turn reasoning.

**Key insight**: "Your CI system is the scheduler, executor, and audit trail. No persistent agent service needed." The CI pipeline triggers the agent; the agent reasons and acts; results flow back through CI.

---

## 4. Production Agent Pipeline Patterns (US/European Companies)

### Pattern A: Calendar-Driven (Floatboat, San Francisco)

Agent wakes up based on calendar events. Meeting scheduled → agent prepares brief. Deadline approaching → agent checks progress. No human prompts needed.

**Applicability to GCS**: Low. GCS is an engineering system, not a personal assistant. Calendar-driven triggers don't map to codebase events.

### Pattern B: Telemetry-Driven (NeuBird AI, Resolve AI — San Francisco)

Agent monitors production telemetry continuously. Anomaly detected → agent investigates → proposes fix. 78% alert noise reduction, MTTR from hours to minutes.

**Applicability to GCS**: Medium. GCS could monitor its own CI pipeline, test results, or benchmark regressions. But GCS doesn't have a "production environment" in the traditional sense.

### Pattern C: CI/CD-Native (Optio, cicaddy, Pullfrog, GitHub Agentic Workflows)

Agent is embedded in the CI/CD pipeline. PR opened → agent reviews. CI fails → agent debugs. Review approves → agent merges.

**Applicability to GCS**: **High.** This is the most natural fit. GCS already has CI. Adding agentic workflows to the CI pipeline would complete the autonomous loop.

### Pattern D: Scheduled Patrol (Friday, OSC My Agent Tasks, Claude Code Routines)

Agent runs on a cron schedule. Checks health, fixes minor issues, reports findings. State persisted in repo files between runs.

**Applicability to GCS**: **High.** Night-watch is already designed for this. Claude Code Routines is the native implementation path.

### Pattern E: Sovereign/Governed (Atos — Paris, Orq.ai — Amsterdam)

Agent runs inside governed infrastructure with explicit policy controls. GDPR/EU AI Act compliance. Human-in-the-loop for high-risk actions.

**Applicability to GCS**: Low currently. GCS is an open-source project, not an enterprise deployment. But the governance patterns (human gate, approval checkpoints) are already implemented in task-intake and orchestrator.

---

## 5. State Persistence Between Runs — The Critical Gap

All surveyed systems face the same challenge: **how does an agent remember what it did last time?**

### Solutions in the Wild

| Approach | System | Mechanism |
|---|---|---|
| **Git as state store** | OSC, Friday, cicaddy | Agent writes outputs as committed files; next run reads them |
| **Checkpoint serialization** | GCS (Phase 7.2) | `.checkpoint` in task card with phase, workers, evidence |
| **Episodic memory** | Anthropic Harness | Persistent memory across multi-hour sessions |
| **PostgreSQL state** | Optio | Full relational state for tasks, agents, inboxes |
| **Session persistence** | Routines (GitHub events) | Session stays alive, receives ongoing PR updates |
| **No persistence** | Routines (cron/API) | Each run is fresh; agent must reconstruct state from repo |

### GCS's Position

GCS's checkpoint system (Phase 7.2) is **ahead of most surveyed systems**. OSC and Friday rely on ad-hoc git commits. Only Optio has a comparable structured state system (PostgreSQL). GCS's `.checkpoint` YAML in task cards is a pragmatic middle ground — structured enough to resume from, simple enough to not need a database.

---

## 6. GCS Integration Plan

### Immediate (using Claude Code Routines)

```
Routine 1: GCS Night-Watch Patrol
  Trigger: Scheduled — 0 2 * * * (2am Asia/Shanghai)
  Prompt: |
    Read docs/agentic/nightly-immune-diagnostics.md.
    Run full diagnostic patrol.
    Follow night-watch commit policy:
    - CLEAN → auto-commit health report, auto-push
    - Issues found → create task cards, commit report, do NOT push
    - CRITICAL → create task cards, commit report, do NOT push, flag

Routine 2: GCS PR Code Review
  Trigger: GitHub — PR opened
  Prompt: |
    Review the PR diff. Check:
    1. Architecture compliance (cross-module boundaries)
    2. Test coverage (new code has tests)
    3. Documentation (changed APIs have doc updates)
    Post review as PR comment with pass/fail per category.

Routine 3: GCS Weekly Doc Drift Scan
  Trigger: Scheduled — 0 8 * * 1 (Monday 8am)
  Prompt: |
    Scan docs/ for references to files that changed in the past week.
    Flag stale references. If found, open a doc-update PR.
```

### Medium-term (using external scheduler + headless Claude Code)

```
GitHub Actions workflow:
  on:
    schedule: "0 2 * * *"
  jobs:
    night-watch:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - run: |
            claude -p "Run night-watch diagnostics per docs/agentic/nightly-immune-diagnostics.md.
                       Follow commit policy in .claude/agents/night-watch.md."
              --max-turns 40 --output-format json
```

### Long-term (Optio-style autonomous feedback loop)

```
PR opened
  → task-intake classifies
  → orchestrator dispatches code-review agent
  → review posted
  → [human merges or requests changes]
  → if changes requested → orchestrator auto-resumes with review context
  → if CI fails → orchestrator auto-resumes with failure logs
  → if all green → orchestrator invokes session-close-orchestrator
```

This requires an external platform (Optio or custom GitHub Actions workflow) to detect CI/review events and re-invoke the orchestrator. GCS's checkpoint system already supports resume — the missing piece is the **event detector** that triggers re-invocation.

---

## 7. Key Recommendations

1. **Adopt Claude Code Routines immediately** for night-watch patrol and periodic tasks. This is the lowest-friction path — no external infrastructure, native Anthropic cloud execution.

2. **Wire GitHub Actions as the CI-native trigger** for PR review workflows. GitHub Actions is already present; adding a `claude -p` headless invocation is a single workflow file.

3. **GCS's checkpoint system is a competitive advantage.** Most surveyed systems lack structured state persistence. Protect and extend it — it's the foundation for autonomous feedback loops.

4. **The "first push" problem is solved by Routines, not by more agent code.** GCS already has the complete pipeline (task-intake→orchestrator→close). The missing piece was never agent logic — it was the external trigger. Routines provide that trigger.

5. **Do NOT build a custom scheduler.** The ecosystem already has: Routines (native), GitHub Actions (CI-native), Optio (Kubernetes-native), OSC (simple cron). Building a scheduler is a distraction from GCS's core mission.

---

## References

- [Claude Code Routines](https://claude.com/blog/introducing-routines-in-claude-code?type=product) — April 2026
- [Optio — Workflow orchestration for AI coding agents](https://github.com/jonwiggins/optio) — MIT, 2026
- [Run Claude Code Agents on a Schedule in the Cloud](https://dev.to/oscdev/run-claude-code-agents-on-a-schedule-in-the-cloud-2lcl) — OSC, 2026
- [Friday — 24/7 AI Assistant on Claude Code](https://github.com/missingus3r/friday-showcase) — 2026
- [GitHub Agentic Workflows](https://www.theregister.com/software/2026/02/17/github-previews-agentic-workflows/) — Microsoft, Feb 2026
- [Red Hat cicaddy — Agentic workflows in CI](https://developers.redhat.com/articles/2026/03/12/how-develop-agentic-workflows-ci-pipeline-cicaddy) — 2026
- [Floatboat — Proactive Agent OS](https://www.globenewswire.com/de/news-release/2026/05/27/3302263/0/en/floatboat-launches-the-proactive-agent-os-that-runs-work-from-your-calendar.html) — May 2026
- [NeuBird AI — Autonomous Production Operations](https://www.businesswirenews.com/news/home/20260406539890/en/NeuBird-AI-Launches-Autonomous-Production-Operations-Agent-Expanding-Beyond-Incident-Response) — April 2026
- [Kore.ai Artemis — Enterprise Agent Platform](https://www.hpcwire.com/aiwire/2026/05/21/kore-ai-unveils-artemis-to-build-govern-and-optimize-enterprise-ai-agents/) — May 2026
- [Atos Sovereign Agentic Studios](https://www.marketscreener.com/news/atos-group-launches-sovereign-agentic-studios-to-bring-ai-safely-into-production-across-organization-ce7e5fdddd8ef620) — March 2026
- [Orq.ai — Enterprise AI Agent Control Layer](https://itbrief.co.uk/story/orq-ai-raises-eur-5m-to-industrialise-enterprise-ai-agents) — January 2026

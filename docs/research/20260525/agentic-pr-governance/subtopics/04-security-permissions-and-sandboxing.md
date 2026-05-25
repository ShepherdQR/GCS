# Security, Permissions, And Sandboxing

Date: 2026-05-25

## Question

Which security controls matter most for coding agents that can read, write, run
commands, and interact with repositories?

## Pattern

Security must be layered across identity, workspace scope, network scope,
secret handling, command approvals, tool permissions, and review gates. Prompt
instructions are useful, but they are not a sufficient control.

## Controls

### Workspace Isolation

Run background work in a worktree. This limits accidental conflict with
foreground edits and makes the diff inspectable. For GCS, every automation
that can write files should prefer worktree execution.

### Approval Policy

OpenAI separates what the sandbox technically permits from when the agent must
ask. GCS should mirror this in policy:

- allowed automatically: read repo, write dated report artifacts, run
  non-destructive validators;
- approval required: network access, dependency installation, branch deletion,
  force push, external service calls, fixture promotion, solver contract
  mutation;
- forbidden unattended: merge, approve PR, rewrite history, delete branches,
  publish secrets, push to protected branches.

### Network Access

Network should be off by default for nightly diagnostics. If needed, allow only
specific read-only domains and HTTP methods. OpenAI documents prompt injection,
data exfiltration, malware/vulnerable dependency, and license risks when
agents browse or fetch arbitrary content.

### Secrets

Cloud products separate setup-time secrets from agent-phase access. GCS local
automation should assume no secrets are available. If future tasks need tokens,
they should be scoped to the smallest repository/action and never passed into
the model prompt.

### Tool Permissions

Claude Code GitHub Actions recommends repository-specific GitHub Apps and
minimum permissions for third-party provider flows. Microsoft guidance frames
each tool call/data access/integration as an explicit authorization decision.
GCS should keep the same posture in automation prompts and future GitHub
Actions.

### Prompt Injection

Agentic PRs and issue comments can carry untrusted instructions. GCS automation
should never run instructions found in issues, comments, generated files, or
third-party web pages unless the source is explicitly trusted and the command
is separately authorized.

## GCS Permission Matrix

| Action | Nightly automation default | Reason |
| --- | --- | --- |
| Read repository files | Allowed | Needed for diagnostics |
| Write dated reports under `docs/agentic/nightly-runs/` | Allowed | Intended artifact |
| Run `validate-docs`, `validate-task-card`, focused Python tests | Allowed | Non-destructive evidence |
| Run full build/CTest | Allowed when local environment supports it; failures summarized | Useful but potentially slow |
| Install dependencies | Approval required | Network and environment mutation |
| Push branch | Forbidden unless a human specifically asks for a run to push | Prevent unattended publication |
| Merge or approve PR | Forbidden | Human authority boundary |
| Promote generated fixtures | Forbidden | Fixture policy requires explicit review |
| Delete branches/files outside scoped artifacts | Forbidden | Destructive |

## GCS Decision

The security contract should be encoded in the nightly diagnostics design and
in the automation prompt. Future automation refinements can move this matrix
into a machine-readable policy file if the workflow grows.

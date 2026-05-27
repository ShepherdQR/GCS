# Narrative Line Capability Demonstrations — Tangible Evidence Per Line

Date: 2026-05-27
Status: active
Depends on: `docs/architecture/95-gcs-narrative-map.md`

## Purpose

The narrative map tells you what level each line is at. This document tells you
how to *feel* that level — each line gets at least one concrete, runnable,
observable demonstration that a reviewer, contributor, or future self can
execute to verify the claim.

Rule: no demonstration may be "read this document." Every entry must be an
action — a command, a visual comparison, a diff, a replay.

---

## 1. Scientific Solver Thesis (Strong)

**Claim:** GCS solves geometric constraints by producing evidence-rich
local-to-global reports.

### Demonstration A: Run the solver on a basic scene and read the diagnostic report

```bat
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt
```

**What to feel:** The output is not just "solved" or "failed." It includes DOF
reports, rank evidence, residual analysis, and obstruction vocabulary. A
researcher who has used academic solvers should notice: this solver *explains*
what happened, not just whether it converged.

**Tangible signal:** The report text itself. Count the diagnostic sections. If
fewer than 4 distinct diagnostic categories appear, the thesis is overclaimed.

### Demonstration B: Compare the local-to-global solve ordering against a flat solve

**What to feel:** The decomposition planning step (`SolveDag`) produces a
topological order of subproblems. The global solve assembles local results. A
solver engineer should be able to trace one subproblem from separation through
local solve through global assembly.

**Tangible signal:** The plan report shows subproblem boundaries. Each
subproblem has its own DOF count, rank, and residual. This is the
local-to-global claim made visible.

### How to strengthen

Add a B2 microbenchmark that isolates exactly one solver-semantics claim (e.g.,
"redundant constraint detection in a 3-rigid-body scene") with a before/after
report diff.

---

## 2. Module Contract Architecture (Very Strong)

**Claim:** Target modules, dependency direction, and contract-test posture are
explicit and enforced.

### Demonstration A: Read the module dependency map

Open `docs/architecture/30-contracts/` and trace any module's dependency arrow.
No cycle should exist. Every module depends only on modules below it.

**What to feel:** The architecture is not "the code as it happens to be." It is
the code as it is *required to become*. The target vocabulary (kernel, IO,
graph, numeric, etc.) is visible in the directory structure, the CMake
configuration, and the contract documents.

**Tangible signal:** `grep` for cross-module includes in `src/gcs/`. The
include graph should match the target dependency direction. Any violation is a
bug, not a design disagreement.

### Demonstration B: Run a contract test

```bat
# Assuming contract tests exist in the test tree
ctest --test-dir out\build\clang-ninja -R contract
```

**What to feel:** Contract tests verify that a module's public surface behaves
as its contract promises. They run fast. They fail with specific violation
messages, not segfaults.

**Tangible signal:** Contract test count and pass rate. If zero contract tests
exist for a module, that module's contract is aspirational.

### How to strengthen

Map every new C++ change to its target module and report surface in the commit
message or PR description.

---

## 3. Implementation Roadmap (Strong)

**Claim:** Step history and upcoming solver work are recorded in depth.

### Demonstration: Trace one closed step from plan to evidence

Pick any closed step from the implementation roadmap. Follow the chain:

1. Step description → task card
2. Task card → completed-task archive
3. Completed-task archive → evidence bundle (screenshots, logs, reports)

**What to feel:** The roadmap is not a wishlist. Every completed step leaves a
trace. A new contributor can pick any past step and reconstruct what was done,
why, and what the result looked like.

**Tangible signal:** Pick 3 random completed-task archives. Do they all contain
concrete evidence (screenshots, command output, diffs)? If yes, the roadmap is
real.

### How to strengthen

Add a compressed roadmap arc when the next solver milestone closes — a
one-paragraph summary that connects the milestone to the narrative map.

---

## 4. Fixture and Counterexample Corpus (Strong)

**Claim:** Verification, generated, milestone, showcase, and counterexample
assets exist and are classified.

### Demonstration A: List and classify all fixtures

```bat
dir fixtures\scene\ /s /b
```

**What to feel:** The directory is organized by purpose, not dumped. You should
see `basic/`, `verification/`, `generated/`, `milestone/`, `counterexample/`
directories. Each fixture file has a known expected behavior.

### Demonstration B: Run a fixture and compare against expected output

```bat
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt > actual.txt
diff actual.txt fixtures\scene\basic\g1.expected.txt
```

**What to feel:** Expected output files exist for key fixtures. The diff is
either empty or contains only known, explained differences. The corpus is a
test suite, not a pile of example files.

**Tangible signal:** Count of fixtures with corresponding `.expected.txt` (or
equivalent expected-output artifact). Count of counterexample fixtures that
produce specific diagnostic codes.

### How to strengthen

Define corpus maturity levels (C0–C4) with acceptance criteria per level. A
fixture at C3 must have: known scene, expected report, migration note, and
semantic tag.

---

## 5. Runtime / History / Replay Evidence (Strong)

**Claim:** Replay evidence, saved-report workflow, and a D3 schema-aware
checker are concrete differentiators.

### Demonstration A: Run the D3 replay evidence package

Navigate to `docs/product/demos/d3-replay-evidence/` and follow the README.

**What to feel:** A solve session produces a replay JSON. That JSON can be
replayed. The replay checker (`g1-replay-evidence.check.json`) verifies schema
conformance and behavioral invariants. The replay is not a log — it is a
machine-verifiable artifact.

**Tangible signal:** Run the replay checker. Does it pass? Does it produce
specific violation messages on malformed replay files?

### Demonstration B: Diff two replays of the same scene

**What to feel:** Two solves of the same scene produce structurally identical
replay JSON (modulo timestamps). The diff is minimal and explainable. This
means the replay is deterministic enough to serve as a regression test.

**Tangible signal:** The diff between two replays of the same scene. If it
contains more than timestamps and duration fields, determinism is weaker than
claimed.

### How to strengthen

Wire the replay checker into R2 release-readiness: a release is not ready if
the checker fails on any D3 scene.

---

## 6. Agentic-SE Operating Layer (Very Strong)

**Claim:** Task cards, runbooks, archives, quality gates, PR audit,
institutional agents, and an operating map form a complete operating system for
agentic software engineering.

### Demonstration A: Trace one task through the full lifecycle

Pick any completed task from `docs/completed-tasks/`. Trace:

1. **Origin:** Was there a task card at `docs/agentic/tasks/`?
2. **Execution:** Does the archive include evidence (screenshots, diffs, logs)?
3. **Closure:** Was the task scored? Does it meet the minimum closure score?
4. **Archive:** Is the completed-task report in the standard format?

**What to feel:** The lifecycle is not ad-hoc. Every non-trivial task passes
through the same stages. A new institutional agent can be onboarded by reading
the runbook and studying 3 completed-task archives.

**Tangible signal:** Run the agentic toolkit validator on 5 random
completed-task reports:
```bat
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\<task>\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\<task>\README.md --min-score 30
```
All 5 should pass validation. At least 4 should meet the minimum score.

### Demonstration B: Read the operating map as a new contributor

Open `docs/agentic/agentic-organization-operating-map.md`. In under 10 minutes,
a new contributor should understand: how work gets requested, how it gets done,
how it gets verified, and how it gets archived.

**What to feel:** The operating map answers "how do I do anything here?" without
requiring the reader to reverse-engineer from git history or chat logs.

**Tangible signal:** Give the operating map to someone who has never seen this
repo. Ask them to describe the task lifecycle. If they can't do it in 5
sentences, the map is too long.

### How to strengthen

Convert the highest-signal exercised governance eval into a validator candidate
before adding any new process.

---

## 7. Quality Gates and Evidence (Strong)

**Claim:** Local validators, contract tests, tool tests, fixture gates, and
quality scripts exist and are exercised.

### Demonstration: Run the full quality gate locally

```bat
python tools\agentic_design\agentic_toolkit.py validate-docs
python -m compileall -q python\gcs_viz
# + contract tests + fixture gates + any other validators
```

**What to feel:** The quality gate is a single command (or a short script). It
runs in under 2 minutes. It produces pass/fail per check. A failing check names
the file and the violation.

**Tangible signal:** Run the gate on a clean checkout. All checks pass. Then
intentionally break one thing (malform a task card, add a syntax error to a
Python file). Run the gate again. The gate must catch it with a specific
message, not a generic error.

### How to strengthen

Add trend history: after each non-trivial task closure, record the gate pass
rate in `docs/agentic/metrics-dashboard.md`. After 10 closures, the trend line
becomes evidence.

---

## 8. UI / Viewer / Scientific Figures (Strong, Integration in Progress)

**Claim:** Viewer, visual QA, figure pipeline, and Solver Evidence Workbench
direction exist with an explicit integration plan.

### Demonstration A: Launch the viewer on a solved scene

```bat
scripts\start_gui.cmd
```

**What to feel:** The viewer shows geometry, constraints, and diagnostic
overlays. It is not pretty in a consumer-app sense. It is *legible* — you can
see which elements are constrained, which are under-constrained, and what the
solver found. Every color carries semantic weight.

### Demonstration B: Inspect the figure pipeline end-to-end

Open `docs/architecture/70-visualization/narrative-line-level-baseline-20260526.md`.
The SVG figure was generated from a YAML spec at
`tools/architecture_visualization/specs/`. The pipeline is: data → YAML spec →
SVG → review → publication.

**What to feel:** Figures are not hand-drawn one-offs. They are generated from
specs. The spec is version-controlled. The figure can be regenerated. The
review comments are archived.

**Tangible signal:** Can you regenerate Figure 95 from its YAML spec with a
single command? If yes, the pipeline is real.

### Demonstration C: View the D5 static workbench package

Navigate to `docs/product/demos/d5-static-workbench/`. This package ties
together Figure 72, VE-002 viewer canvas evidence, visual QA results, and
projection contracts into one evidence bundle.

**What to feel:** The workbench package proves that viewer states, scientific
figures, and projection contracts all refer to the same underlying solver
evidence. The chain is not "three separate teams did three things" — it is one
evidence chain, three projections.

**Tangible signal:** For a single solver scene, can you trace from solver report
→ viewer screenshot → figure → visual QA report without gaps?

### Demonstration D: Aesthetic taste calibration

Open `docs/research/20260527/aesthetic-taste/README.md` and view the image.
This is the zero-reference for the "Quiet Technical Atelier" visual thesis.

**What to feel:** Before it puts solver evidence on screen, the project knows
what its taste looks like on a blank page. The curve is not decoration — it is
a calibration target.

### How to strengthen

Build one end-to-end evidence walkthrough: pick one scene, solve it, capture
the report, project it into the viewer, export a figure, run visual QA. Package
the whole chain as a single artifact.

---

## 9. Institutional Agents and Learning (Developing)

**Claim:** Standing agents, templates, examples, refusal evals, and a registry
scorecard exist. The system learns from exercised agent behavior.

### Demonstration A: List current institutional agents

Open `docs/agentic/institutional-agent-registry-and-scorecard.md`. Each agent
has: a role definition, a scorecard, example invocations, and refusal cases.

**What to feel:** The agents are not just prompt templates. They have known
boundaries — situations they should refuse. They have scored track records. A
new agent proposal must pass the same scorecard before promotion.

### Demonstration B: Read a forging note (extracted experience)

Open `docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/`.
Each forging note records: what happened, what was surprising, what rule or
memory was extracted, and why it should persist.

**What to feel:** The organization does not repeat mistakes. When a session hits
friction that a rule could prevent, the rule is forged and stored. The forging
note is the evidence that learning happened.

**Tangible signal:** Count of forging notes. Count of distinct agents with at
least one forging note. If the same agent has 5+ notes but no scorecard
promotion, the promotion pipeline is broken.

### How to strengthen

Promote agents only after accumulating examples, refusal cases, and eval
evidence. A promotion without a refusal case is incomplete — an agent that
never says no has no known boundary.

---

## 10. Git / Worktree / PR Governance (Strong)

**Claim:** Worktree isolation, branch discipline, PR audit, permission policy,
and threat matrix are documented and exercised.

### Demonstration A: Check the current worktree policy in action

```bat
git worktree list
```

**What to feel:** Parallel work happens in isolated worktrees. The master
branch is never worked on directly. Every change has a branch. Every branch has
a traceable purpose.

### Demonstration B: Read the exercised governance evidence

Open `docs/agentic/evals/governance/exercised-evidence-20260526.md`. This
document records actual governance situations that occurred, how they were
handled, and what was learned.

**What to feel:** Governance is not a policy document that sits in a drawer. It
is exercised. Situations happen, decisions are made, and the decision rationale
is recorded.

**Tangible signal:** Count of exercised-evidence entries. Each entry should
name: the situation, the decision, the principle applied, and whether the
outcome validated or challenged the principle.

### Demonstration C: Audit the last 20 commits

```bat
git log --oneline -20
```

**What to feel:** Commit messages are concise and why-focused. Each commit
scopes to one concern. No commit contains "WIP" or "fix typo" followed by "fix
actual typo" in the next commit (evidence of rushed work).

### How to strengthen

Build the E-GOV-001 validator candidate: a script that checks scoped staging
evidence (e.g., no file staged outside the claimed scope, no secret files
staged, commit message matches the project convention).

---

## 11. Product / User / Market Story (Strong but Split)

**Claim:** Researcher primary audience, product brief, demo ladder, D1–D5
demos, README route, and contributor boundary exist.

### Demonstration A: Walk the README researcher route

Open the README. A researcher should be able to:
1. Understand what GCS is in 30 seconds
2. Run the CLI on a demo scene in 2 minutes
3. Find the D1/D2/D3 evidence packages from the README
4. Understand the contribution boundary (what this project is and is not)

**What to feel:** The README is not a feature list. It is a route — it guides
the researcher from "what is this" to "I can run it" to "I can find evidence."

### Demonstration B: Walk the demo ladder

```
D0: Internal development smoke
D1: CLI smoke (docs/product/demos/d1-cli-smoke/)
D2: Diagnostic classification (docs/product/demos/d2-diagnostic-classification/)
D3: Replay evidence (docs/product/demos/d3-replay-evidence/)
D5: Static workbench package (docs/product/demos/d5-static-workbench/)
```

**What to feel:** Each demo level adds a dimension of evidence. D1 says "it
runs." D2 says "it diagnoses." D3 says "its behavior is verifiable." D5 says
"the evidence chain is complete." A researcher can enter at any level and see
the corresponding evidence.

**Tangible signal:** For each demo level, can a new user complete it in under
15 minutes without asking for help? If D1 takes an hour, the onboarding path is
broken.

### How to strengthen

Convert the first external researcher review packet into a real review archive
after actual feedback arrives.

---

## 12. Release / Packaging / Onboarding (Strong but Split)

**Claim:** A 20-minute contributor path, release-readiness checklist, R1
researcher-preview note, package smoke automation, and D3 replay checker exist.

### Demonstration A: Run the 20-minute contributor path

Open `docs/product/20-minute-contributor-path.md` and execute it start to
finish. The path should include: build, run a fixture, run the quality gate,
understand the module map, and know where to make a first change.

**What to feel:** A new contributor who follows this path should feel oriented,
not overwhelmed. Each step should work on a clean checkout. The total time
should actually be around 20 minutes, not 2 hours.

**Tangible signal:** Time yourself following the path on a clean machine. If it
takes more than 30 minutes, the "20-minute" claim is false.

### Demonstration B: Run the release smoke automation

```bat
# The R1 package smoke JSON should be runnable
# Check docs/product/release-readiness-checklist.md for the exact command
```

**What to feel:** The smoke test is automated. It checks: build succeeds, basic
fixtures solve, replay checker passes, quality gate passes. The output is a
JSON report, not a human narrative.

**Tangible signal:** Run the smoke test. Does it produce a JSON report? Does
that JSON include pass/fail per check with timestamps?

### How to strengthen

Add an R2 reproducible build transcript: a clean build log from a documented
environment (compiler version, CMake version, dependency versions) that another
person can reproduce byte-for-byte.

---

## 13. External Benchmark / Comparison (Strong but Split)

**Claim:** External comparison plan, benchmark criteria, feasibility matrix, B1
expected outputs, D2 JSON summary, and B2 candidate review exist.

### Demonstration: Read the benchmark feasibility matrix

Open `docs/architecture/97-external-solver-comparison-and-benchmark-plan.md`.
The feasibility matrix should name: candidate solvers, comparison dimensions,
feasibility assessment, and risk of overclaiming.

**What to feel:** The comparison plan is honest about what GCS can and cannot
claim. It does not cherry-pick scenes where GCS looks good. It defines
comparison dimensions (semantic richness, diagnostic depth, replay
verifiability) that are meaningful even if GCS is slower or handles fewer
constraint types.

**Tangible signal:** The B2 candidate review should include at least one scene
where GCS is expected to perform *worse* than a baseline. If every scene favors
GCS, the benchmark is marketing, not measurement.

### How to strengthen

Produce the first optional external baseline run: pick one scene, run it
through GCS and through SolveSpace (or FreeCAD Sketcher), and write a
source-level comparison note. Even one scene with honest comparison is worth
more than a 10-page comparison plan with no execution.

---

## 14. Business / Open-Source Strategy (Developing)

**Claim:** Primary audience, README route, contribution boundary, R1 preview
route, and first external researcher review packet are documented.

### Demonstration: Read the researcher audience strategy

Open `docs/product/researcher-audience-strategy.md`. It should answer:
- Who is the first audience? (researchers in geometric constraint solving,
  computational geometry, or CAD)
- What do they need to see to take GCS seriously?
- What is the contribution boundary? (what kinds of contributions are welcome
  now, what will be welcome later)
- What is the distribution model? (source-only? binaries? pip? Docker?)

**What to feel:** The strategy is specific about who, what, and when. It names
real venues, real conferences, real journals, or real research groups. It does
not say "we will go viral." It says "here is the first audience, here is what
they need, here is how we reach them."

**Tangible signal:** Can you name 3 specific researchers or research groups who
would find GCS relevant? If the strategy can't name them, the audience is
imaginary.

### How to strengthen

Archive the first real external review or contribution. Until a person outside
this repository has looked at GCS and responded, the open-source strategy is a
plan, not a reality.

---

## Cross-Cutting Capability Check

The following checks apply across multiple narrative lines:

### The 5-Minute Trust Test

A reviewer clones this repo. They have 5 minutes. What can they see?

| Minute | Action | Narrative line tested |
| --- | --- | --- |
| 1 | Read README, understand what GCS is | Product/market (11) |
| 2 | Run `GCS.exe fixtures/scene/basic/g1.txt`, see diagnostic output | Solver thesis (1) |
| 3 | Run `python tools/agentic_design/agentic_toolkit.py validate-docs` | Quality gates (7) |
| 4 | Open `docs/architecture/95-gcs-narrative-map.md`, understand the project structure | Module architecture (2), Agentic SE (6) |
| 5 | Launch viewer, see geometry with diagnostic overlay | UI/viewer (8) |

If all 5 minutes succeed, 6 of 14 narrative lines are proven real in one
sitting.

### The Evidence Chain Test

Pick one scene. Trace it through every system:

```
scene.txt → solver → report → replay JSON → replay checker → viewer → screenshot → visual QA → figure → publication
```

Count the gaps. Every gap is a narrative line whose claim is not yet
integrated.

---

## Summary Table

| # | Narrative line | Strongest tangible signal | Weakest tangible signal |
| --- | --- | --- | --- |
| 1 | Scientific solver thesis | CLI diagnostic report with 4+ evidence categories | No isolated microbenchmark for a single semantics claim |
| 2 | Module contract architecture | Dependency direction visible in includes and CMake | Zero contract tests for some modules |
| 3 | Implementation roadmap | Step → task → archive chain is traceable | No compressed roadmap arc for new readers |
| 4 | Fixture corpus | Classified directory structure with expected outputs | No maturity ladder (C0–C4) defined |
| 5 | Replay evidence | D3 replay checker passes, produces specific violations | Not wired into R2 release gate |
| 6 | Agentic-SE operating layer | Full task lifecycle traceable from card to archive | Process sprawl risk; no validator for governance |
| 7 | Quality gates | Agentic toolkit catches real violations with specific messages | No trend history across multiple closures |
| 8 | UI/viewer/figures | Viewer shows semantic color mapping; figure pipeline is spec-driven | No end-to-end evidence walkthrough published |
| 9 | Institutional agents | Agents have role definitions, scorecards, and forging notes | No agent has enough examples for promotion |
| 10 | Git/worktree governance | Worktree isolation exercised; exercised-evidence doc exists | No automated validator (E-GOV-001) implemented |
| 11 | Product/market story | Demo ladder D1–D5 exists; README route is concrete | No external reviewer feedback archived |
| 12 | Release/packaging | R1 smoke automation produces JSON report | No reproducible build transcript |
| 13 | External benchmark | Feasibility matrix is honest about limitations | No executable external baseline run |
| 14 | Business/open-source | Researcher audience strategy names specific targets | No real external review or contribution exists |

---

## Next Action

This document should be reviewed alongside the narrative map. When a narrative
line's level is raised, at least one tangible demonstration in this document
must be updated to reflect the new capability.

The demonstrations above that are marked as gaps become the next task queue.

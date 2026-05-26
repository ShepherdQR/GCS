# Developer AI Practice Paradigms

Date: 2026-05-26
Scope: Publicly visible practices from highly influential developers and AI
tool builders using AI in software creation. The user mentioned "龙虾作者"; this
report interprets that as Peter Steinberger and the OpenClaw lineage because
current public coverage links him to the viral OpenClaw agent project.

## Executive Summary

The best developers are not converging on one "vibe coding" style. They are
converging on a higher-level discipline:

- code generation is cheap;
- context, taste, specification, verification, and review are expensive;
- AI is strongest when a task is narrow enough to verify and broad enough to
  justify delegation;
- parallel agents help when tasks are independent and evidence is inspectable;
- security and data boundaries must be architectural, not prompt-only;
- the developer's role shifts from typist to director, toolsmith, reviewer,
  evaluator, and systems thinker.

The frontier split is between "agentic engineering" and "irresponsible vibe
coding." Agentic engineering uses AI aggressively, but wraps it in plans,
tests, diffs, reviews, logs, and local project conventions. Irresponsible vibe
coding generates artifacts faster than the human can understand or govern.

## Source Register

| Source | Date | Used for | Confidence |
| --- | ---: | --- | --- |
| [TechCrunch on Peter Steinberger and OpenClaw](https://techcrunch.com/2026/02/25/openclaw-creators-advice-to-ai-builders-is-to-be-more-playful-and-allow-yourself-time-to-improve/) | 2026-02-25 | OpenClaw creator signal and practice framing | Medium |
| [TechRadar, What is OpenClaw?](https://www.techradar.com/pro/what-is-openclaw) | 2026 | OpenClaw local agent control-plane description | Medium |
| [Lex Fridman episode summary on Peter Steinberger/OpenClaw](https://inshort.io/podcast/lex-fridman-podcast/491-openclaw-the-viral-ai-agent-that-broke-the-internet-peter-steinberger) | 2026 | Multi-agent workflow claims and narrative context | Medium |
| [Simon Willison, Lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) | 2025-06-16 | Agent security pattern | High |
| [Simon Willison, Coding agents require skilled operators](https://simonwillison.net/2025/Jun/18/coding-agents/) | 2025-06-18 | Skilled operator thesis | High |
| [Thorsten Ball, How might AI change programming?](https://registerspill.thorstenball.com/p/how-might-ai-change-programming) | 2025-01-30 | Cheap writing/rewriting thesis | High |
| [Zed interview with Addy Osmani on the 70 percent problem](https://zed.dev/blog/ai-70-problem-addy-osmani) | 2025-11-06 | Prototype-to-production gap | High |
| [ChatPRD interview with Hamel Husain](https://www.chatprd.ai/how-i-ai/debugging-ai-writing-evals) | 2025-10-14 | Debugging AI products and eval practice | Medium |
| [YC/Karpathy, Software Is Changing Again](https://rosetta.to/u/ycombinator/andrej-karpathy-software-is-changing-again) | 2025-06-19 | Software 3.0 and directing agents | Medium |
| [AP on AI coding and vibe coding](https://apnews.com/article/09f35ccc7545ac92447a19565322f13d) | 2025-09-29 | Mainstream framing and Karpathy term context | Medium |

## Developer Capsules

### 1. Peter Steinberger And OpenClaw: Agentic Engineering At Extreme Tempo

Observed pattern:

- Run multiple AI coding agents in parallel.
- Use AI through messaging, voice, or mobile control loops, not only IDE chat.
- Build missing tools whenever the agent hits friction.
- Keep agent execution close to local hardware, local files, and personal
  workflows.
- Treat agent orchestration itself as a product surface.

Core paradigm:

```text
developer = conductor + toolsmith + reviewer
agents = parallel workers with hands
control plane = local gateway plus messaging plus permissions
```

Strategic lesson:

- The breakthrough is not "one prompt writes an app." It is that a single
  expert can build a private agent operating environment and then compound
  output through many parallel loops.
- The expert's taste and tool-building ability are the multiplier.

Risks:

- This style can outrun understanding, security review, and architecture.
- Local agents with broad file, browser, shell, and account access can become a
  serious data-exfiltration and destructive-action risk.
- Public coverage contains fast-changing claims about stars, commits, and
  workflow scale; treat exact counts as volatile.

GCS adoption:

- Use the OpenClaw lesson for control-plane thinking: a good agent has hands,
  state, tools, and permission boundaries.
- Do not copy the velocity target. Copy the scaffold: local control, clear
  tools, review loops, and agent friction turned into tool improvements.

### 2. Simon Willison: Skilled Operator And Security Realist

Observed pattern:

- Use LLMs and agents heavily, but distrust unbounded tool access.
- Coin and popularize security framings such as prompt injection and the
  "lethal trifecta."
- Treat coding agents as requiring skilled operators.

Core paradigm:

```text
agent risk = private data + untrusted content + external communication
```

Strategic lesson:

- Agents become dangerous when they can read private data, ingest attacker-
  controlled content, and communicate externally.
- The defense is not "tell the model to be careful." The defense is capability
  architecture: separate data, content, and outbound action.

GCS adoption:

- Any GCS agent that reads local repo secrets, external web pages, or private
  memory and can write files, send messages, or push branches needs explicit
  permission policy.
- The project should keep human gates for network, dependency, branch, push,
  destructive, and protected-path operations.

### 3. Thorsten Ball: Cheap Code Changes The Shape Of Programming

Observed pattern:

- Use AI to generate scripts, Rust code, tests, assertions, and utility work.
- Emphasize that even imperfect AI changes programming because writing and
  rewriting certain code becomes cheap.
- Keep skepticism about universal claims.

Core paradigm:

```text
AI lowers the cost of code text.
It does not eliminate design, correctness, taste, or ownership.
```

Strategic lesson:

- Once code text is cheap, teams should spend more effort on experiments,
  comparison, refactoring, tests, and disposable tooling.
- The bottleneck shifts to deciding what to ask for and verifying whether it is
  right.

GCS adoption:

- Use AI to create small tools, reports, fixture generators, visualization
  checks, and exploratory implementations.
- Keep mathematical and architectural decisions tied to explicit contracts.

### 4. Addy Osmani: The 70 Percent Problem

Observed pattern:

- AI can get projects to a plausible first 70 percent quickly.
- The last 30 percent includes architecture, UX, reliability, edge cases,
  tests, performance, maintainability, and production integration.
- Senior judgment becomes more important, not less.

Core paradigm:

```text
AI accelerates first draft velocity.
Production quality still requires engineering discipline.
```

Strategic lesson:

- Organizations that measure only "time to first prototype" will overestimate
  productivity.
- The right metric is time to reviewed, tested, maintainable, user-valuable
  change.

GCS adoption:

- Track rework rate, review findings, and gate failures, not only number of
  generated files or commits.
- Use AI to broaden exploration, but force closure through tests, reports, and
  project memory.

### 5. Hamel Husain: Evals And Debugging As Product Discipline

Observed pattern:

- Build AI product work around evals, logs, prompt artifacts, and reproducible
  debugging loops.
- Treat prompts and AI workflows as versioned assets.
- Use monorepo-style organization for prompts, microagents, evals, and tools.

Core paradigm:

```text
AI product quality = inspectable examples + evals + debugging instrumentation
```

Strategic lesson:

- AI systems fail in messy, distribution-specific ways. Teams need error
  taxonomies, saved examples, and regression evals.
- The unit of learning is not a clever prompt; it is a captured failure that
  becomes a test or operating rule.

GCS adoption:

- Convert repeated agent mistakes into negative evals or skill updates.
- Keep completed-task archives and evidence bundles as the raw material for
  future evals.

### 6. Andrej Karpathy: Software 3.0 And Manifesting

Observed pattern:

- Frame modern software as moving from hand-written code and neural weights to
  natural-language-programmed systems.
- Popularize "vibe coding" as a style where the human expresses intent and the
  model generates most implementation.
- Also warns that agent progress should be treated seriously and carefully,
  because agents need human-in-the-loop control.

Core paradigm:

```text
human language becomes a programming surface.
the developer increasingly directs systems that implement.
```

Strategic lesson:

- The frontier skill is intent specification: stating what should exist,
  inspecting what was created, and steering the system through corrections.
- For serious systems, "manifesting" must be paired with tests, environment,
  review, and architecture.

GCS adoption:

- Use natural-language plans as first-class design artifacts.
- Keep them checked into task cards, architecture docs, and completed-task
  reports so they can be reviewed and replayed.

## Common Workflow Pattern

The strongest practitioners converge on this loop:

1. Frame intent and constraints.
2. Ask the model to explore before editing.
3. Convert intent into an atomic plan.
4. Delegate implementation to one or more agents.
5. Run focused tests and static checks.
6. Review the diff manually or with a second model.
7. Iterate with concrete failures.
8. Archive what changed, what passed, and what remains risky.
9. Promote repeated lessons into prompts, tools, tests, or skills.

## Anti-Patterns

| Anti-pattern | Why it fails | Better pattern |
| --- | --- | --- |
| "One giant prompt, one giant diff" | Review becomes impossible | Atomic tasks with evidence |
| Measuring generated lines | Optimizes noise | Measure accepted, tested changes |
| Trusting the first plausible solution | AI is good at plausible wrongness | Tests plus adversarial review |
| Giving agents all permissions | Prompt injection and accidents compound | Least privilege and human gates |
| No repo-native context | Agent guesses local conventions | Skills, runbooks, config files |
| No saved failures | The team relearns the same lesson | Negative evals and experience records |
| Parallel agents on coupled semantics | Inconsistency and merge burden | Parallelize independent subproblems |

## Strategic Synthesis

The frontier developer does less typing and more orchestration. But "orchestral"
does not mean vague. It means the developer owns:

- task decomposition;
- context packaging;
- tool design;
- permission boundaries;
- review and taste;
- evals and tests;
- product judgment;
- institutional learning.

The highest-leverage developers build their own harnesses. They do not wait for
the model to become perfect; they construct a local system in which model
imperfection becomes observable and correctable.

## GCS Recommendations

1. Keep using skills and task cards as the GCS equivalent of high-quality
   agent instructions.
2. Add more negative evals from real agent failures.
3. Track review burden and rework rate so AI speed does not mask downstream
   cost.
4. Promote agent friction into tools only after it repeats or affects a
   high-risk surface.
5. Do not let "vibe coding" touch solver semantics without contract tests.
6. Use multi-agent parallelism for research, documentation, UI QA, repository
   audit, and fixture exploration before using it for tightly coupled numeric
   behavior.

## Open Questions

- Which developer workflows should GCS treat as exemplar patterns and which
  should be treated as entertaining but unsafe for this repo?
- Should GCS maintain a public "agentic engineering examples" page grounded in
  its own task cards and completed archives?
- What local security model is needed before any GCS agent can interact with
  private data plus external communication channels?

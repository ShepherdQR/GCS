# Repository Audit And Statistics Research

Date: 2026-05-25

Scope: 调研成熟开源项目、平台和审计工具如何做仓库统计与工程审计，重点覆盖代码行数、文件数量、语言识别、质量指标、安全指标、项目健康指标、所有权/依赖边界与历史趋势。本文同时采集 GCS 当前仓库的轻量基线，为后续架构设计提供证据。

## Executive Summary

成熟项目不会把“代码行数”当成单一真相。GitHub Linguist 用语言识别和 `.gitattributes` 过滤生成物/第三方/文档；cloc 与 tokei 输出文件数、总行数、代码行、注释行、空白行；SonarQube 把规模指标和复杂度、重复、覆盖率、新代码质量放在同一指标体系里；CNCF DevStats/CHAOSS 更强调项目健康和社区响应；OpenSSF Scorecard 把安全姿态拆成带风险权重的检查项；Chromium 则用 PRESUBMIT、OWNERS、checkdeps 把审计前移到提交和评审路径。

对 GCS 来说，最有价值的不是做一个漂亮的 LOC 面板，而是建立“可复现、可解释、可比较”的仓库审计层：从 Git tracked 文件生成快照，按 GCS 目标模块、工件类型和生命周期层聚合，再输出 JSON 和 Markdown。这个层应属于 `tools/agentic_design` 或新的 `tools/repository_audit` 支撑工具，不应进入 solver core。

本次轻量基线显示，GCS 当前 tracked 文件约 738 个。文件数量上，`docs/`、`.codex_scene_generation_store/`、`fixtures/`、`.codex/`、`tools/` 是最大的几类；文本行数上，`.json` 与 `.md` 远超 C++/Python 源码，说明 GCS 当前阶段是“文档/证据/fixture 重于 solver 源码”的架构重写期。这一点很重要：审计系统必须能区分 source、architecture、research、fixture、generated store、tooling 和 completed-task archive，否则 LOC 会误导判断。

建议 GCS 先实现一个只读审计工具链：`collect` 生成 machine-readable 快照，`report` 生成 Markdown，`diff` 比较两个 revision，`check` 执行阈值/边界规则。初期不要把阈值做成 default quality gate；先作为 opt-in evidence gate 使用，等指标稳定后再接入 `run-quality-gates`。

## Source Register

| Source | Date/version | Used for | Confidence |
| --- | --- | --- | --- |
| GitHub Docs, About repository languages, https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-repository-languages | accessed 2026-05-25 | GitHub uses Linguist for language statistics and updates default-branch language stats after push. | High |
| github-linguist README, https://github.com/github-linguist/linguist | accessed 2026-05-25 | Local CLI language breakdown, per-file strategy/breakdown options, generated/vendor/documentation filtering model. | High |
| GitHub Docs, Customizing how changed files appear, https://docs.github.com/en/repositories/working-with-files/managing-files/customizing-how-changed-files-appear-on-github | accessed 2026-05-25 | `.gitattributes` and `linguist-generated` exclusion behavior. | High |
| cloc README, https://github.com/AlDanial/cloc | accessed 2026-05-25 | File, blank, comment, code line counting and custom language definitions. | High |
| tokei README, https://github.com/XAMPPRocky/tokei | accessed 2026-05-25 | Fast grouped statistics: files, lines, code, comments, blanks by language. | High |
| SonarQube metrics definition, https://docs.sonarsource.com/sonarqube-server/user-guide/code-metrics/metrics-definition | accessed 2026-05-25 | Security, reliability, maintainability, coverage, duplication, complexity, size, new-code metrics. | High |
| CNCF Project Health Measurement, https://contribute.cncf.io/projects/best-practices/community/project-health/ | accessed 2026-05-25 | Metric interpretation must be project-specific; dashboards are imperfect and need reality filters. | High |
| CNCF DevStats, https://devstats.cncf.io/ | accessed 2026-05-25 | Open-source GitHub archive + Postgres + Grafana dashboard model for public project metrics. | High |
| CNCF Kubernetes Project Journey Report, https://www.cncf.io/reports/kubernetes-project-journey-report/ | accessed 2026-05-25 | Example of project-level velocity, contributor, company, PR, commit, documentation metrics. | High |
| CHAOSS Metrics FAQ, https://handbook.chaoss.community/community-handbook/community-initiatives/metrics/metrics-faq | accessed 2026-05-25 | Metrics are versioned snapshots that can change between releases. | Medium |
| OpenSSF Scorecard, https://openssf.org/scorecard/ and https://github.com/ossf/scorecard | accessed 2026-05-25 | Security checks, structured results, risk-weighted aggregate score, public BigQuery/API scan model, non-goals. | High |
| GitHub Code Scanning Docs, https://docs.github.com/en/code-security/concepts/code-scanning/about-code-scanning-alerts | accessed 2026-05-25 | Code scanning as PR/default-branch alert workflow, severity and branch mapping. | High |
| OWASP Dependency-Check, https://owasp.org/www-project-dependency-check/ | accessed 2026-05-25 | SCA dependency vulnerability report model using CPE/CVE evidence. | High |
| Chromium PRESUBMIT Scripts, https://www.chromium.org/developers/how-tos/depottools/presubmit-scripts/ | accessed 2026-05-25 | Best-effort pre-upload/pre-commit checks, affected-file input API, warning/error distinction. | High |
| Chromium checkdeps, https://chromium.googlesource.com/chromium/src/buildtools/+/refs/heads/main/checkdeps/ | accessed 2026-05-25 | Declarative include rules using allow, deny, and temporary-warning dependency states. | High |
| GitHub Docs, About code owners, https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners | accessed 2026-05-25 | CODEOWNERS validation, branch-protection review requirements, ownership of CODEOWNERS itself. | High |
| Linux Foundation, Linux Kernel History Report 2020, https://www.linuxfoundation.org/resources/publications/linux-kernel-history-report-2020 | accessed 2026-05-25 | Long-term historical reporting of commits, contributors, release growth, and codebase evolution. | High |
| GCS architecture docs, `docs/architecture/README.md`, `10-system/system-topology.md`, `40-quality/verification-strategy.md`, `69-ci-ready-quality-gates.md` | current workspace | GCS module ownership, quality-gate placement, support-tool boundary. | High |
| GCS module inventory, `tools/agentic_design/module_inventory.json` | current workspace | Current module paths, allowed imports, contract tests, skill ownership. | High |

## Findings

### 1. Repository statistics need an explicit counting contract

GitHub's public language bar is intentionally not a raw line counter. It uses Linguist to infer languages for syntax highlighting and repository statistics, and it lets maintainers correct language accounting through attributes. That matters because a repository can contain generated code, vendored code, data, notebooks, images, docs, and build outputs that should not all count as authored source.

cloc and tokei represent the lower-level counting pattern: group by language, then report files, lines, code, comments, and blanks. Their useful lesson is not the exact parser but the shape of the output contract. A good audit report should say what it counted, what it ignored, which language rules were used, and which files were too large, binary, generated, or unsupported.

For GCS, the counting contract should be checked into the repo. It should define:

- source roots: `src/`, `apps/`, `python/`, `tools/`, selected `tests/`;
- evidence and data roots: `fixtures/`, `docs/architecture/70-visualization/assets/`, generated scene metadata;
- documentation roots: `docs/architecture/`, `docs/research/`, `docs/agentic/`, `docs/completed-tasks/`;
- excluded roots by default: `out/`, `outputs/`, `var/`, `.git/`, local caches, unpromoted generated stores unless explicitly included;
- special roots: `.codex/skills/` and `.codex_scene_generation_store/` should be visible but separated from solver/product code.

### 2. Mature audit systems combine size, quality, security, ownership, and trend

SonarQube's metric catalog is a useful reference because it does not stop at LOC. It places size next to maintainability issues, technical debt ratio, coverage, duplication, complexity, security hotspots, and separate "new code" metrics. The new-code split is especially important: a mature project should avoid punishing historical bulk while still preventing new regressions.

OpenSSF Scorecard takes a different angle: security posture is decomposed into checks such as code review, maintained status, dangerous workflows, pinned dependencies, SAST, security policy, signed releases, token permissions, and vulnerabilities. Scorecard also documents its own limits: aggregate scores are opinionated heuristics and should not be treated as universal truth.

For GCS, this argues for a layered metric model:

- size: files, bytes, physical lines, text/binary, language/extension;
- project shape: source/test/docs/fixture/tool/generated-store ratios;
- architecture coverage: each target module has source, interface, implementation, contract test, skill, docs;
- dependency governance: imports match `module_inventory.json`;
- evidence coverage: fixtures, golden reports, CLI smokes, viewer/replay report artifacts;
- new-change audit: PR or branch delta versus base revision;
- optional security checks: GitHub/Scorecard/CodeQL/SCA when the repo enters public CI or dependency-heavy phases.

### 3. Project health metrics must be interpreted in context

CNCF explicitly warns that project-health thresholds are not one size fits all. A Kubernetes-scale metric threshold is not appropriate for a small or early-stage research solver. CNCF DevStats and the Kubernetes journey report are still instructive because they show useful families of metrics: commits, PRs, issues, authors, contributors, companies, documentation commits, and longitudinal trends.

CHAOSS adds another caution: metric definitions are released as snapshots and evolve. This is relevant to GCS because the project is still shaping its agentic operating layer, fixtures, and solver contracts. Metrics should be versioned, and report readers should know which schema produced a snapshot.

For GCS, a `schema_version` field is mandatory. A report produced in May 2026 should remain interpretable after the repository grows new modules, fixture corpora, CI jobs, or generated evidence formats.

### 4. Large projects move audit earlier than CI

Chromium's PRESUBMIT mechanism runs checks before upload or commit, but its docs call out that such checks are best-effort and can be bypassed or invalidated by concurrent changes. That is a healthy design posture: local checks are useful feedback, not mathematical proof. Chromium's checkdeps system complements this with declarative dependency rules: paths can be allowed, denied, or temporarily allowed with warning.

GitHub CODEOWNERS adds the review ownership pattern: path ownership can be used with branch protection to require review from owners of changed files, and ownership of the CODEOWNERS file itself matters.

GCS already has a similar local pattern in `tools/agentic_design/agentic_toolkit.py`: `validate-docs`, `validate-inventory`, `validate-skills`, `check-dependencies`, and `run-quality-gates`. Repository statistics should extend this support layer rather than create a separate governance universe.

### 5. GCS is currently evidence-heavy by design

The following baseline was collected on 2026-05-25 with:

```powershell
git -c core.quotepath=false ls-files
```

The count is a lightweight workspace sample before this research report and architecture note are staged. It uses Git tracked files only and does not include untracked task artifacts from this session.

| Metric | Value |
| --- | ---: |
| Tracked files | 738 |
| Text-scanned files in the simple whitelist | 711 |
| Approximate text lines in scanned files | 115,318 |
| Docs-class files (`.md`) | 347 |
| Data/config/fixture files (`.json`, `.jsonl`, `.yaml`, `.txt`) | 266 |
| Code/script files (`.cpp`, `.cppm`, `.py`, `.ps1`, `.cmd`) | 97 |
| Asset files (`.png`, `.jpg`, `.webp`, `.svg`, `.pdf`, `.pptx`) | 24 |

Top-level tracked file distribution:

| Top-level path | Files | Approx. text lines |
| --- | ---: | ---: |
| `docs/` | 348 | 39,627 |
| `.codex_scene_generation_store/` | 161 | 33,386 |
| `fixtures/` | 75 | 14,276 |
| `.codex/` | 45 | 1,293 |
| `tools/` | 38 | 10,589 |
| `tests/` | 27 | 3,977 |
| `src/` | 20 | 8,128 |
| `python/` | 14 | 3,437 |
| root/scripts/apps | 10 | 575 |

Extension distribution:

| Extension | Files | Approx. text lines |
| --- | ---: | ---: |
| `.json` | 201 | 47,836 |
| `.md` | 347 | 40,532 |
| `.py` | 58 | 15,285 |
| `.cpp` | 24 | 8,800 |
| `.cppm` | 10 | 1,622 |
| `.txt` | 32 | 747 |
| `.yaml` | 23 | 312 |
| `.gitignore` | 1 | 81 |
| `.cmd` | 3 | 47 |
| `.jsonl` | 10 | 30 |
| `.ps1` | 2 | 26 |

Current C++ module source distribution:

| Module path | Files | Approx. lines |
| --- | ---: | ---: |
| `src/gcs/io_adapters` | 2 | 1,338 |
| `src/gcs/numeric_engine` | 2 | 999 |
| `src/gcs/constraint_catalog` | 2 | 872 |
| `src/gcs/kernel` | 2 | 860 |
| `src/gcs/viewer_bridge` | 2 | 792 |
| `src/gcs/session_runtime` | 2 | 770 |
| `src/gcs/diagnostics` | 2 | 741 |
| `src/gcs/tools` | 2 | 732 |
| `src/gcs/decomposition_planner` | 2 | 618 |
| `src/gcs/incidence_graph` | 2 | 406 |

Interpretation:

- GCS is not yet source-code-dominated. Architecture docs, research, fixtures,
  generated scene evidence, and tool scaffolding are first-class project state.
- Raw LOC would overstate `.json` fixture/generated-evidence mass and understate
  the importance of small C++ contract modules.
- A useful GCS audit must expose ratios and categories, not just totals.

## Comparative Patterns

| Pattern | Seen in | GCS adaptation |
| --- | --- | --- |
| Language and generated/vendor overrides | GitHub Linguist | Add `audit_class` categories and later optional `.gitattributes` alignment. |
| Physical line/comment/blank/code count | cloc, tokei | Use as optional cross-check; keep GCS canonical JSON independent of tool availability. |
| New-code metrics | SonarQube | Add `diff --base <rev>` reporting for PR/task review. |
| Project-specific health interpretation | CNCF | Avoid universal thresholds; use module-relative and phase-relative thresholds. |
| Versioned metrics | CHAOSS | Include `schema_version`, `tool_version`, `source_revision`, and `generated_at`. |
| Risk-weighted checks | OpenSSF Scorecard | Group findings by severity and confidence, not only pass/fail. |
| Structured results | OpenSSF Scorecard | Emit JSON first, Markdown second. |
| Best-effort presubmit | Chromium | Provide local `check` and quality-gate integration, but document limits. |
| Declarative dependency rules | Chromium checkdeps | Reuse `module_inventory.json` and add architecture path rules. |
| Path ownership | CODEOWNERS/OWNERS | Use GCS skills/module owners as review routing metadata before GitHub CODEOWNERS exists. |
| Longitudinal history report | Linux Kernel report | Store snapshots by date/revision for growth trend reports. |

## Recommendations

1. Create a repository audit contract before implementing thresholds.
   The first durable artifact should define categories, exclusions, source roots,
   generated roots, and schema fields. Without this, every metric will invite
   arguments about what it really counted.

2. Make JSON the canonical output and Markdown a projection.
   This follows the structured-result lesson from Scorecard and the report
   projection pattern already used in GCS viewer/replay evidence work.

3. Aggregate by GCS target module, not only by directory.
   `tools/agentic_design/module_inventory.json` already maps modules to source
   directories, contract tests, skills, imports, and ownership. The audit should
   use that as a source of truth.

4. Separate authored source from generated/evidence payloads.
   `.codex_scene_generation_store/`, promoted fixture JSON, SVG/HTML/PDF assets,
   and completed-task archives are useful evidence, but they should not inflate
   solver source size.

5. Add PR/task delta reports before hard thresholds.
   A delta report can flag "this task added 1,800 lines of fixture JSON and 20
   lines of C++" without blocking useful work. Hard thresholds should wait until
   several snapshots establish normal ranges.

6. Add a small number of high-signal checks first.
   Initial checks should include unexpected binary files, build output tracked
   accidentally, module without contract test, contract test without module,
   large files crossing configured limits, and disallowed import drift.

7. Treat security scans as a later optional layer.
   GCS currently has limited third-party runtime dependencies. OpenSSF, CodeQL,
   and SCA patterns are worth designing for, but the first local tool should
   stay offline and standard-library friendly.

## Proposed GCS Audit Dimensions

| Dimension | Example fields | Why it matters |
| --- | --- | --- |
| Inventory | tracked files, untracked optional, extension, bytes, line counts | Establishes reproducible repository shape. |
| Classification | source, test, docs, research, fixture, generated-store, asset, task archive, skill | Prevents misleading aggregate LOC. |
| Module coverage | source files, interface files, implementation files, contract tests, skills, docs | Maps physical growth to GCS architecture. |
| Quality evidence | tests, fixtures, reports, CLI smoke artifacts, visual QA assets | Measures whether code growth has evidence. |
| Boundary compliance | allowed imports, forbidden imports, app/boundary modules | Extends existing dependency audit. |
| Size risk | large files, large functions later, oversized generated artifacts | Finds reviewability and repo-bloat risks. |
| Change delta | added/removed files, added/removed lines, category shifts | Supports task review and PR audits. |
| Trend | snapshots by date/revision, phase notes, schema version | Enables release/history reports. |

## Open Questions

- Should `.codex_scene_generation_store/` remain tracked long term, or should only promoted fixtures and metadata be retained?
- Should GCS eventually introduce `.gitattributes` to align GitHub Linguist language statistics with the project audit categories?
- Which report location should hold generated snapshots: `var/repository-audit/` for ephemeral local evidence, `docs/reports/repository-audit/` for durable snapshots, or both?
- When the solver grows larger, should function-level complexity be added through tree-sitter or kept outside the first audit layer?
- Should repository audit findings be allowed to fail the default quality gate, or remain opt-in until a baseline history exists?

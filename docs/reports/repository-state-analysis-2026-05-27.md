# GCS 仓库状态深度分析报告

**生成日期**: 2026-05-27  
**分析范围**: 全仓库（除 .git 和构建产物）  
**当前分支**: master (与 origin/master 同步)  
**最近提交**: `20cec07` — "Merge UI viewer figure integration branch"

---

## 1. 项目概览

GCS (Geometric Constraint Solver) 是一个几何约束求解研究项目，采用 C++23 Modules 构建系统。当前版本为 **v0.2.0**，目标受众为求解器和几何约束研究者。

### 核心事实
| 指标 | 数值 |
|------|------|
| 总文件数（不含 .git） | 909 |
| 总提交数 | 207 |
| Git 历史跨度 | 2026-05-19 ~ 2026-05-27（9 天密集开发） |
| 唯一分支 | master（无其他活跃分支） |
| 当前脏文件 | 887 个（变更量 182,201 insertions / 182,201 deletions，对称修改模式） |

---

## 2. 目录结构与规模分析

### 2.1 一级目录按磁盘占用排序

| 目录 | 磁盘占用 | 文件数 | 职责 |
|------|---------|--------|------|
| `docs/` | 9.6 MB | ~475 .md | 架构文档、研究笔记、任务归档、产品文档 |
| `tools/` | 764 KB | ~49 .py | 可视化渲染、仓库审计、场景生成、产品演示 |
| `fixtures/` | 556 KB | 75 | 场景测试数据、约束模型 |
| `src/` | 376 KB | 20 (.cpp + .cppm) | C++23 求解器核心实现 |
| `tests/` | 280 KB | 30 (.cpp + .py) | 合约测试与工具测试 |
| `python/` | 180 KB | 14 .py | Python 可视化应用 (gcs_viz) |
| `apps/` | 4 KB | 1 .cpp | CLI 入口点 |
| `scripts/` | - | 5 (.cmd + .ps1) | 构建/质量门脚本 |

### 2.2 规模分布评估

文档 (docs/) 占仓库非构建内容的 **绝大部分**（9.6MB / 475 个 Markdown 文件）。这是研究型仓库的典型特征——过程文档积累远超代码量。源代码 (src/) 仅占 376KB，说明项目处于架构设计与研究探索并行的早期阶段，求解器实现相对薄。

---

## 3. C++ 求解器核心 (src/)

### 3.1 模块拓扑

项目定义了 10 个 C++ 模块（.cppm 接口 + .cpp 实现），全部聚合为单一库 `gcs_solver`：

| 模块 | 实现行数 | 接口行数 | 模块职责 |
|------|---------|---------|---------|
| `io_adapters` | 1339 | 129 | 文本和 JSON 场景导入/导出 |
| `numeric_engine` | 941 | 174 | 数值求解原型 |
| `constraint_catalog` | 827 | 164 | 约束定义与编目 |
| `contract_tools` | 667 | 158 | 合约校验工具 |
| `session_runtime` | 653 | 207 | 临时编排外观 |
| `viewer_bridge` | 642 | 235 | 与 Python 可视化层的桥接 |
| `kernel` | 638 | 353 | 领域模型、稳定 ID、行为意图 |
| `diagnostics` | 620 | 218 | DOF/状态/残差诊断 |
| `decomposition_planner` | 561 | 126 | 连通分量分解 |
| `incidence_graph` | 351 | 131 | 关联图结构 |

**总计**: 9,134 行（7,239 实现 + 1,895 接口）

### 3.2 关键观察

- **io_adapters 是最大模块** (1339 行)，说明 I/O 层已有较完整实现，这与 README 中 "inspectable solver evidence" 的定位一致——I/O 是当前交付证据的基础。
- **kernel 模块接口最丰富** (353 行接口)，与其作为领域模型中心的定位匹配。
- **incidence_graph 实现最少** (351 行)，与 README 中 "current connected-component decomposition prototype" 的描述一致——仍在原型阶段。
- 模块间通过接口模块 (.cppm) 进行编译期隔离，架构纪律良好。
- 编译标准为 **C++23**，启用了 `CMAKE_CXX_SCAN_FOR_MODULES`，这在 C++ 生态中属于前沿实践。

### 3.3 构建配置

- 使用 **Clang + Ninja** preset
- 测试框架: **GoogleTest** (v1.14.0, 可选 FetchContent)
- 13 个合约测试可执行文件 (CTest)，分别对应每个模块 + 跨模块质量测试 + 管线测试
- 构建产物输出至 `out/build/clang-ninja/`

---

## 4. 测试基础设施 (tests/)

### 4.1 合约测试 (C++)

13 个 GTest 可执行文件，覆盖所有 10 个模块 + 3 个集成测试：

- `gcs_kernel_contract_tests`
- `gcs_constraint_catalog_contract_tests`
- `gcs_incidence_graph_contract_tests`
- `gcs_decomposition_planner_contract_tests`
- `gcs_numeric_engine_contract_tests`
- `gcs_diagnostics_contract_tests`
- `gcs_session_runtime_contract_tests`
- `gcs_io_adapters_contract_tests`
- `gcs_viewer_bridge_contract_tests`
- `gcs_contract_tools_contract_tests`
- `gcs_module_dependency_contract_tests`
- `gcs_cross_module_quality_contract_tests`
- `gcs_pipeline_contract_tests`

### 4.2 工具测试 (Python)

17 个 Python 测试文件，覆盖可视化 QA 工具、场景生成、仓库审计、浏览器导出：

- `test_gcs_token_lint.py` / `test_gcs_text_overflow.py` / `test_gcs_overlap_contrast.py`
- `test_gcs_screenshot_baseline.py` / `test_gcs_ui_qa.py`
- `test_gcs_viz_algebra.py` / `test_gcs_viz_history_replay.py`
- `test_showcase_scene_renderer.py` / `test_showcase_scene_html_compositor.py`
- `test_showcase_fixture_evidence.py` / `test_scene_generation_explorer.py`
- `test_browser_export.py` / `test_capture_viewer_evidence.py`
- `test_fixture_library_gate.py` / `test_agentic_toolkit.py`
- `test_repository_audit.py` / `test_session_efficiency.py`

### 4.3 评估

测试架构体现了**合约驱动设计**——每个模块有对应的合约测试。Python 测试层覆盖了可视化质量门、场景生成管线、仓库审计等辅助工具。整体测试策略分层清晰，但合约测试的实际断言深度需要进一步审视（仅从文件数量和命名无法判断覆盖率）。

---

## 5. Python 可视化层 (python/)

### 5.1 模块组成

| 文件 | 职责 |
|------|------|
| `algebra.py` | 几何代数计算 |
| `color_scheme.py` | 配色方案 |
| `engine_bridge.py` | 与求解器引擎的桥接 |
| `event_store.py` | 事件存储 |
| `platform.py` / `platform_gui.py` | 跨平台 GUI 抽象 |
| `viewer_bridge.py` | 与 C++ viewer_bridge 模块对接 |
| `visualizer.py` | 主可视化逻辑 |
| `screens/dialogs.py` / `screens/dialogs_tk.py` | 对话框实现 |

### 5.2 架构评估

Python 层的设计存在平台抽象 (`platform.py` / `platform_gui.py`) 和双对话框实现 (`dialogs.py` / `dialogs_tk.py`)，表明正在探索或维护多个 GUI 后端。`viewer_bridge.py` 与 C++ 侧的 `viewer_bridge.cppm/.cpp` 形成 C++-to-Python 桥接的对称结构。

---

## 6. 工具生态 (tools/)

### 6.1 分类

| 子目录 | 工具数量 | 用途 |
|--------|---------|------|
| `architecture_visualization/` | 17 文件 | SVG 图形渲染、布局同步、HTML 合成、QA 门 |
| `scene_generation/` | 9 文件 | 场景自动生成、参数化、探索器 |
| `repository_audit/` | 9 文件 | 仓库统计采集、分类、差异分析、策略引擎 |
| `product_demo/` | 5 文件 | D5 工作台打包、诊断分类、R1 烟测 |
| `agentic_design/` | 2 文件 | 模块清单、Agent 工具包 |
| `ui_qa/` | ~5 文件 | Token Lint / Text Overflow / Overlap Contrast / Screenshot Baseline / UI QA |

### 6.2 关键观察

- **仓库审计工具** (`repository_audit/`) 已形成完整的模块化结构——`collect.py`、`classify.py`、`diff.py`、`report.py`、`trend.py`、`policy.py`、`registry.py`——这是一个成熟的内部工具，具备完整的 pipeline。
- **可视化工具**围绕 SVG 渲染、Inkscape 同步、HTML 合成展开，表明项目对架构图、展示场景的生产有较高要求。
- **场景生成工具** (`scene_generation/`) 具备模型定义 (`gcs_model.py`)、参数化 (`parameterization.py`)、合约检查 (`contracts.py`)、探索器 (`explorer.py`)——表明场景数据生成是项目的核心能力之一。

---

## 7. 文档结构 (docs/)

### 7.1 大类分布

| 子目录 | 规模估算 | 内容性质 |
|--------|---------|---------|
| `docs/agentic/` | ~150 .md | Agentic SE 实践：经验、治理、机构 Agent、任务卡片、夜间运行 |
| `docs/architecture/` | ~80 .md | 架构文档：基础、系统拓扑、管线、合约、实现、可视化、基准 |
| `docs/completed-tasks/` | ~45 .md | 已归档任务（2026-05-24 ~ 2026-05-26） |
| `docs/research/` | ~60 .md | 研究材料：论文分析、UI 研究、AI 组织前沿、LGS 树 |
| `docs/product/` | ~12 .md | 产品文档：演示、发布、评审、贡献边界 |
| `docs/reports/` | ~5 .md | 仓库审计报告、会话效率报告 |

### 7.2 架构文档体系

`docs/architecture/` 采用编号分层结构：
- **00-foundations**: 架构原则、问题表述、拓扑语义模型
- **10-system**: 当前到目标的映射、系统拓扑
- **20-solver-pipeline**: 分解规划、数值求解、管线
- **30-contracts**: 领域合约、求解器合约
- **40-quality**: 验证策略
- **50-implementation**: C++23 模块架构、第三方策略
- **60-69**: Agentic SE 方法论文档
- **70-99**: 可视化、UI 设计、场景生成、基准测试、叙事地图

这套文档编号体系从 00 延伸到 99，在 9 天内迅速建立，体现了极强的系统化意图。但需要注意：部分编号（如 60-99）之间的语义边界不够清晰，部分文档的"进度归档"性质（如 67-current-progress-and-next-steps.md）可能在后续需要重构为更稳定的信息架构。

### 7.3 研究文档

研究内容按日期组织（`docs/research/20260514` ~ `20260526`），覆盖：
- 几何约束求解的学术论文分析 (LGS, SPQR)
- UI/UX 设计系统研究 (Anthropic Frontend, Vercel Design)
- AI Agent 工作流研究 (Git Worktree, Agentic PR Governance)
- AI 组织前沿研究 (McKinsey AI Report, Institutional Token Economics)

### 7.4 Agentic SE 实践

`docs/agentic/` 是整个仓库中**最密集的文档子树**，记录了该项目在使用 AI Agent 进行软件工程方面的系统性实践：

- **经验库**: 5 个正式经验主题 (001-005)，涵盖任务闭包、阶段步骤延续、Git 会话分支治理、AI 治理队列控制、仓库审计价值循环
- **机构 Agent**: 4 个正式化的 Agent (Bladesmith、Tailor、Atelier、Art Director)，每个有完整的启动提示、示例、评估和模板
- **治理基础设施**: 权限策略、威胁矩阵、评估准则、质量门选择策略
- **任务管理**: 每个工作会话对应一个任务卡片，有明确的执行计划和归档

这些 Agentic SE 文档本身构成了一个**元层次的知识体系**——项目不仅用 AI 辅助开发求解器，也用 AI 辅助开发 AI 辅助开发的方法论。

---

## 8. 场景与数据 (fixtures/)

### 8.1 数据组织

| 子目录 | 内容 |
|--------|------|
| `fixtures/scene/basic/` | 基本场景（g1.txt） |
| `fixtures/scene/bcc/` | BCC 约束场景（7 个文件） |
| `fixtures/scene/generated/` | 自动生成的复杂场景（10 个 .gcs.json + 10 个 .metadata.json） |
| `fixtures/scene/counterexamples/` | 反例场景（奇异几何） |
| `fixtures/scene/verification/` | 验证场景 |

### 8.2 数据成熟度

场景数据量不大（75 个文件），但结构清晰。generated/ 目录下有 10 个 `codex_complex10` 运行实例，每个包含场景 JSON 和元数据 JSON，表明自动化场景生成管线已经在运作。counterexamples/ 下的奇异几何数据暗示了鲁棒性测试的考虑。

---

## 9. 当前工作状态（未提交变更）

### 9.1 变更范围

`git diff --stat` 显示 887 个文件有变更，均为对称修改（insertions = deletions），这是一种**格式化重写**模式的典型特征——可能是换行符统一、缩进风格标准化、或配置文件格式迁移。

变更主要涉及：
- **`.codex/skills/`** 下的所有 20 个 Skill 文件（SKILL.md + agents/openai.yaml + references/*.md）
- **`tools/ui_qa/`** 下的 QA 工具文件（token_lint, text_overflow, ui_qa, screenshot_baseline）
- 可能还有其他 Python 工具文件的统一格式变更

### 9.2 建议

如果这些变更确实是格式化重写，建议在提交信息中明确说明所用的格式化工具和配置，以便追溯。

---

## 10. Codex Skill 体系

仓库包含 20 个 `.codex/skills/` 条目，每个对应一个领域专家：

| Skill | 职责域 |
|-------|--------|
| `gcs-architecture-steward` | 高层架构一致性 |
| `gcs-kernel-contract-steward` | kernel 模块合约 |
| `gcs-constraint-semantics-steward` | 约束语义正确性 |
| `gcs-incidence-structure-steward` | 关联图结构 |
| `gcs-decomposition-planning-steward` | 分解规划 |
| `gcs-numeric-engine-steward` | 数值引擎 |
| `gcs-diagnostics-certification-steward` | 诊断输出认证 |
| `gcs-session-runtime-steward` | 会话运行时 |
| `gcs-io-adapter-steward` | I/O 适配器 |
| `gcs-viewer-bridge-steward` | C++/Python 桥接 |
| `gcs-contract-tools-steward` | 合约工具 |
| `gcs-quality-steward` | 质量门 |
| `gcs-scene-behavior-steward` | 场景行为正确性 |
| `gcs-scene-generation-engineer` | 场景自动生成 |
| `gcs-cpp-solver-maintainer` | C++ 求解器整体维护 |
| `gcs-python-gui-builder` | Python GUI 开发 |
| `gcs-scientific-figure-producer` | 科学图形生产 |
| `gcs-ui-design-steward` | UI 设计 |
| `gcs-third-party-governance-steward` | 第三方依赖治理 |
| `task-scoped-session-closer` | 会话关闭流程 |

这些 Skill 形成了一个**全栈 Agent 协作网络**——每个模块都有对应的 Steward，外加跨领域的图形生产者、质量把控者、会话管理者。Skill 的命名模式统一（`gcs-{domain}-{role}`），配置结构一致（SKILL.md + agents/openai.yaml），表明这套 Agent 体系经过了系统性设计而非临时堆砌。

---

## 11. 开发节奏分析

### 11.1 提交频率

基于 `git log` 的 207 次提交在 9 天内完成：
- 日均 ~23 次提交
- 高峰期出现在 2026-05-24 至 2026-05-26（三天内 ~120+ 次提交）

### 11.2 提交模式

提交信息呈现出高度结构化的模式：
- **功能提交**: "Merge UI viewer figure integration branch", "Integrate UI viewer figure evidence"
- **存档提交**: "Codex worktree snapshot: archive-cleanup", "Archive repository audit session closeout"
- **进展提交**: "Advance narrative map evidence package", "Advance researcher evidence roadmap"
- **工具提交**: "tools: add repository audit collector", "docs: stitch git session timeline"
- **文档提交**: "docs: persist ai governance execution queue"

### 11.3 协作模式

所有提交作者均为 **ShepherdQR**，表明当前为单人开发。但这不代表项目孤立——Agentic SE 文档体系表明，该项目重度依赖 AI Agent 协作，提交信息中的 "archive"、"snapshot" 模式也与 AI Agent 工作流特征相符。可以推断，实际的开发单元是"人类 + AI Agent 群"。

---

## 12. 架构成熟度评估

### 12.1 优势

1. **模块化合约设计**: 每个求解器模块有明确定义的 .cppm 接口 + 对应合约测试，模块间通过接口隔离。
2. **文档系统性**: 从基础原则到具体执行计划的编号文档体系，虽然编号仍有优化空间。
3. **工具链完整**: 构建、测试、可视化、场景生成、仓库审计、质量门均有一线工具支持。
4. **Agentic 元认知**: 项目不仅做软件，更在研究"如何用 AI 做软件"的方法论，文档记录了完整的经验循环。
5. **I/O 先行**: 最大的模块是 io_adapters，这与"可检验证据"的产品定位一致——先让数据可流入流出。

### 12.2 需要关注

1. **求解器核心厚度不足**: 10 个模块合计 9,134 行，对几何约束求解器而言，核心算法实现尚浅。kernel (638行)、numeric_engine (941行) 的实际求解能力需要评估。
2. **文档/代码比偏高**: 9.6MB 文档 vs 376KB 源码，对于研究项目这可以理解，但如果项目目标是可运行的求解器，需要在文档积累与代码积累间寻找平衡。
3. **编号体系膨胀**: `docs/architecture/` 从 00 到 99 的编号在 9 天内迅速膨胀，部分编号似乎已用尽（99 已出现），需要预留扩展空间。
4. **脏工作区**: 887 个文件有未提交变更，如果是格式化操作，建议尽快提交/回滚，避免与后续实质性修改混淆。
5. **单分支风险**: 所有开发在 master 上完成（无 feature 分支），虽然对单人项目可接受，但缺乏回滚粒度。

### 12.3 机会

1. **从文档中提取稳定知识**: `docs/architecture/` 中的 "current progress"、"next steps" 型文件可以在阶段性里程碑时重构为稳定参考。
2. **Skill 体系公开化**: `.codex/skills/` 的 Agent 定义具有方法论文档的潜在价值——它们不仅是工具配置，也是架构理解的凝结。
3. **场景库扩充**: `fixtures/` 当前为 75 个文件，对于一个约束求解器而言偏少。可以通过 `scene_generation` 工具扩大自动生成的场景规模。
4. **基准测试建立**: `docs/architecture/benchmarks/` 已经规划了 B1 诊断分类和 B2 微基准，应尽快落实可运行的基准套件。

---

## 13. 风险评估

| 风险 | 等级 | 说明 |
|------|------|------|
| 文档腐化 | 中 | 大量按日期/进度命名的文档可能在数周后过时，需要定期归档或删除 |
| 求解器成熟度 | 中 | 核心算法仍在原型阶段，距离可用求解器有一定距离 |
| 单一开发者 | 低 | 项目定位为研究，单人开发可接受；但知识高度集中在一个人身上 |
| 脏工作区积累 | 低 | 887 个文件的未提交变更是格式化模式，但拖延提交可能造成混淆 |
| 编号空间耗尽 | 低 | 99 号已出现，建议切换到非数字命名或预留空档 |
| 外部依赖可用性 | 低 | GoogleTest v1.14.0 和 Python 依赖均为成熟生态 |

---

## 14. 建议的近期行动

1. **提交或回滚脏变更**: 887 个文件的变更应尽快处理——确认是格式化后提交，或回滚。
2. **编写 CLAUDE.md**: 仓库当前没有 CLAUDE.md 文件，这可以显著改善 AI Agent 的上下文理解。
3. **建立发布检查清单**: `docs/product/release-readiness-checklist.md` 已存在，应确保每次发布前完整执行。
4. **归档过时进度文档**: `docs/architecture/` 中的 67-68-71-79-80 等"进度报告"型文档应移至 `docs/completed-tasks/` 或 `docs/reports/`。
5. **落实基准测试**: 将 B1 和 B2 基准从规划推进到可执行状态。
6. **内存整合**: 考虑运行 `consolidate-memory` 技能来整理笔记和记忆文件。

---

## 15. 总结

GCS 仓库是一个高度组织化的几何约束求解研究项目，以 **C++23 模块化求解器 + Python 可视化 + 完整文档体系 + AI Agent 协作网络** 四层架构推进。项目在 9 天内以惊人速度搭建了从求解器原型、测试框架、可视化 GUI、场景数据生成到仓库审计工具的完整工具链。其最大的差异化特征是**系统化的 Agentic SE 实践**——项目不仅是约束求解的代码仓库，更是 AI 辅助软件工程方法论的实验场。

当前项目的核心挑战不在于架构或工具，而在于从"研究探索 + 文档积累"的阶段过渡到"稳定的求解器能力交付"。在此过渡中，需要关注文档的可持续性（避免信息腐化）、求解器核心的深度（代码量从 9K 行增长到具备实质求解能力）、以及场景/基准测试的覆盖度（从 75 个场景扩展到可信的验证规模）。

---

*本报告由 Claude (Cowork mode) 在 `think/effort: max` 模式下生成，基于对仓库文件系统、Git 历史、构建配置和文档结构的全量分析。*

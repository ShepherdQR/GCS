# 架构可视化研究报告

Research snapshot: 2026-05-23.

## 结论

当前最佳实践已经从“画一个漂亮的大盒子图”转向“用可审查的模型生成一组互相约束的视图”。对 GCS 最合适的表达不是单张 C4 图，也不是 UML 全家桶，而是一个 architecture atlas：

- ISO/IEC/IEEE 42010 式的多 viewpoint 描述，用 stakeholder concern 驱动视图边界。
- C4/arc42 式的语义缩放，用 context、building block、runtime、quality 等层次避免混淆抽象级别。
- Structurizr/Mermaid/D2 式的 diagram-as-code，让图进入版本控制、代码审查和自动化检查。
- Penrose 式的“数学语义优先”，即图的布局和形状服务于不变量，而不是装饰。
- AI-era 的可读性：图必须能被人、测试、LLM 和未来工具稳定解析，所以节点名、边语义、契约名和报告名要显式。

GCS 的核心视觉隐喻应是“有限站点上的局部到全局求解图”：`ModelSnapshot` 产生 `ContextSnapshot` 覆盖，规划器形成 `CoverPlan` 与 `BoundaryProjection`，数值引擎产生 `LocalSection`，诊断层通过 gluing 与 obstruction 报告决定能否提交。模块图只是骨架，contract pipeline 和 local-to-global 图才是灵魂。

## 外部研究基线

ISO/IEC/IEEE 42010:2022 要求架构描述区分 architecture 与 architecture description，并显式处理 architecture description framework、architecture description language、viewpoints 和 model kinds。这说明架构图应当先声明“从谁的 concern 看什么”，而不是把所有关系塞进一张图。来源：[ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html)。

C4 模型提供了面向开发者的层次抽象：software system、container、component、code，并补充 system landscape、dynamic、deployment 等图。其关键价值不是固定样式，而是防止抽象层混杂。来源：[C4 model](https://c4model.com/)。

arc42 提供 architecture communication 模板，覆盖 context/scope、solution strategy、building block view、runtime view、deployment view、crosscutting concepts、decisions、quality requirements 等。它适合作为 GCS atlas 的章节组织，而不是替代项目已有 `docs/architecture/`。来源：[arc42 overview](https://arc42.org/overview)。

Structurizr DSL 把 C4 架构模型写成 text-based DSL，并从单一模型导出多个视图。对 GCS 的启发是“模型一次定义，视图多次投影”，后续可把 Mermaid 图升级为可验证的架构模型。来源：[Structurizr DSL](https://docs.structurizr.com/dsl)。

Mermaid 的 `architecture-beta` 从 v11.1.0 起支持 groups、services、edges、junctions 等建筑块，适合云/CI/CD 或服务资源关系；但 GCS 的数学契约图更适合先用稳定 flowchart/C4-like Mermaid 表达，等渲染环境统一后再采用 `architecture-beta`。来源：[Mermaid architecture diagrams](https://mermaid.js.org/syntax/architecture)。

D2 代表新一代 declarative diagramming，强调文本生成图、动画、LaTeX 和多语言标签。它说明前沿风格正在从静态图片走向可编排、可 diff、可演示的图文系统。来源：[D2 documentation](https://d2lang.com/)。

Penrose 从数学式陈述生成可视图，并用 constraint-based specification language 与 constrained numerical optimization 保持数学意义。这与 GCS 非常贴合：架构图也应该保护不变量，如稳定 ID、不可变 snapshot、边界投影、gluing 与报告优先。来源：[Penrose SIGGRAPH 2020](https://penrose.cs.cmu.edu/siggraph20)。

2026 年 CIAO 论文把仓库输入转成基于 ISO 42010、SEI Views and Beyond、C4 的系统级架构文档；评价认为文档通常有价值，但图质量、高层 context 和 deployment view 仍有限。这提示我们不能把图完全交给生成器，必须用项目语义和审查规则约束图。来源：[CIAO arXiv:2604.08293](https://arxiv.org/abs/2604.08293)。

2026 年 SADU benchmark 把架构图视为 structured software engineering artifacts，而不是普通图片；结果显示当前 VLM 对图关系推理仍明显不足。这说明我们的图要保持结构化源码、稳定标签和显式边语义，不能只交付位图。来源：[SADU arXiv:2604.04009](https://arxiv.org/abs/2604.04009)。

## 最佳实践提炼

1. 先选 viewpoint，再选图形。架构图的第一行应能回答“这个图服务谁的哪个问题”。
2. 一组小图优于一张巨图。用 semantic zoom 表达 system、module、pipeline、contract、quality，而不是在同一画布混合全部细节。
3. 图源码要和代码同仓库。Mermaid/Structurizr/D2 的核心价值是 PR diff、review、版本历史和自动化检查。
4. 节点必须命名稳定契约。对 GCS，`ContextSnapshot`、`CoverPlan`、`BoundaryProjection`、`NumericTask`、`GluingReport` 比“planner box”更重要。
5. 边必须有语义。至少区分 imports/depends-on、runtime flow、report/evidence、read-only projection、commit/reject。
6. 报告是一等公民。架构图应显示 validation、diagnostics、rank、residual、obstruction、stage reports，而不是只显示 happy path。
7. 数学系统要显式 gauge 和 boundary。GCS 不能只画 solver loop，必须画 gauge policy、overlap、boundary agreement。
8. 前沿可视化不是炫技，而是可计算。能被工具验证、被测试引用、被未来 agent 理解的图，优先级高于复杂视觉效果。

## 前沿视觉风格

推荐采用“scientific architecture atlas”：

- 画布：浅色背景、高对比线条、少量语义色，不使用装饰性渐变。
- 构图：从左到右表示时间/数据流，从下到上表示抽象层级，从外到内表示边界穿透。
- 色彩：kernel/domain truth 使用冷色，numeric/analysis 使用青绿，runtime/transaction 使用暖色，boundary/viewer 使用中性色，failure/obstruction 使用红色。
- 版式：每张图只承担一个 reasoning task；图下配 3-5 条不变量，不写大段说明。
- 交互预留：未来可从 Mermaid 升级到 Structurizr/D2/自定义 SVG，保持节点 ID 与契约名稳定。
- AI 可读性：避免只靠颜色表达语义；边标签、节点标签、图标题都要可文本检索。

## GCS 设计文件分析

本次阅读的核心设计文件包括：

- `docs/architecture/README.md`
- `docs/architecture/00-foundations/problem-formulation.md`
- `docs/architecture/00-foundations/architectural-principles.md`
- `docs/architecture/00-foundations/topos-semantic-model.md`
- `docs/architecture/10-system/system-topology.md`
- `docs/architecture/10-system/current-to-target-map.md`
- `docs/architecture/20-solver-pipeline/pipeline.md`
- `docs/architecture/30-contracts/domain-contracts.md`
- `docs/architecture/30-contracts/solver-contracts.md`
- `docs/architecture/40-quality/verification-strategy.md`
- `docs/architecture/50-implementation/cpp23-module-solver-architecture.md`
- `docs/architecture/60-agentic-submodule-design-analysis.md`
- `docs/architecture/61-agentic-module-framework.md`
- `tools/agentic_design/module_inventory.json`

抽取到的 architecture thesis：

- GCS 是 typed constraint satisfaction problem on product manifolds，不是 UI 问题，也不是单纯 least-squares 问题。
- durable truth 在 `kernel`，包括 stable IDs、snapshots、contexts、state versions、reports。
- `constraint_catalog` 拥有残差、签名、参数 schema、Jacobian、generic DOF 和退化语义。
- `incidence_graph` 提供 incidence hypergraph、body graph、components、未来 separator/SPQR-like 结构。
- `decomposition_planner` 选择 finite context cover、boundary projections、solve ordering 和 gauge policy。
- `numeric_engine` 消费 `NumericTask`，产生 local sections、rank/residual/iteration evidence，但不提交状态。
- `diagnostics` 用 DOF、rank、residual、gluing、conflict、redundancy、obstruction 解释求解结果。
- `session_runtime` 是唯一完整命令编排和事务提交层。
- `io_adapters` 与 `viewer_bridge` 是边界模块，只观察、序列化、投影，不拥有 solver truth。
- agentic overlay 是设计和维护系统，不能成为 C++ solver runtime dependency。

## 采用的图谱

因此 GCS atlas 采用五类图：

1. System landscape：谁进入系统、哪些边界模块存在、solver core 与测试/fixture 如何相连。
2. Module dependency topology：显示导入方向和禁止反向依赖。
3. Local-to-global semantic map：显示 GCS 的数学语义核心。
4. Runtime contract pipeline：显示从命令到报告/提交的阶段。
5. Agentic design overlay：显示未来模块 agent、skill、tool、eval 如何维护架构，但不进入 runtime。

成品图册见 `docs/architecture/70-visualization/gcs-architecture-atlas.md`。

## 后续建议

- 将 Mermaid 图中的节点 ID 与 `tools/agentic_design/module_inventory.json` 对齐，后续可生成一致性检查。
- 若引入 Structurizr/D2，不替换 Mermaid 文档；先把它们作为可导出的第二视图。
- 为 dependency topology 增加自动化 gate：从 C++23 `import gcs.*` 提取真实依赖，与 atlas 声明比对。
- 为 local-to-global 图增加 fixture 链接：每个 obstruction/gluing 示例都指向一个测试场景。

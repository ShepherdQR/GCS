# IBM ACG：智能体计算图（Agentic Computation Graph）深度研究

## 1. 论文基本信息

- **标题**：From Static Templates to Dynamic Runtime Graphs: A Survey of Workflow Optimization for LLM Agents
- **作者**：Ling Yue, Kushal Raj Bhandary (RPI); Ching-Yun Ko, Dhaval Patel, Shuxin Lin, Nianjun Zhou, Pin-Yu Chen (IBM Research); Jianxi Gao, Shaowu Pan (RPI)
- **机构**：Rensselaer Polytechnic Institute (RPI) + IBM Research
- **ArXiv**：2603.22386v1 (2026年3月)
- **GitHub**：https://github.com/IBM/awesome-agentic-workflow-optimization

## 2. 核心问题

**为什么Agent架构越来越臃肿却不变强？**

IBM Research给出的核心判断：很多Agent之所以越做越臃肿却不变强，问题往往不在某个Prompt、某个Skills、某个模型或某个局部模块，而在**工作流结构本身**。

"工作流结构"不是把几个Prompt或Skills串起来，而是整个Agent系统的运行图：
- 有哪些节点
- 信息如何流动
- 工具和验证器插在什么位置
- 哪些结构在部署前固定
- 哪些又会在运行时动态生成或编辑

## 3. ACG核心概念

### 3.1 智能体计算图（ACG）的定义

将Agent工作流抽象为由**节点**和**边**组成的图：

| 元素 | 定义 | 具体内容 |
|------|------|----------|
| **节点（Nodes）** | 执行原子操作 | LLM调用、信息检索、工具使用、逻辑验证、消息传递 |
| **边（Edges）** | 编码节点间依赖关系 | 控制流依赖、数据流依赖、通信依赖 |

**更深层理解**：一个LLM中心节点至少可被理解为"指令、上下文、工具、模型/解码设置"的组合，而调度器或路由器则决定哪个节点先执行、哪些节点能并行、什么时候终止、是否允许重规划。因此工作流结构不仅是拓扑图，还是一套**可执行控制策略**。

### 3.2 工作流的表示形式

表示形式本身就是约束条件：

| 表示形式 | 特点 | 影响 |
|----------|------|------|
| 代码中的隐式控制流 | 最灵活但最难优化 | 什么结构都难以搜索 |
| DSL/JSON/YAML文本规范 | 结构化但表达力有限 | 可搜索但受限 |
| 带类型约束的显式图中间表示（IR） | 最佳平衡 | 可搜索、可验证、可安全编辑 |

**关键洞察**：表示形式会直接决定——什么结构可以被搜索、什么候选可以被静态验证、运行时究竟能否进行安全编辑。

### 3.3 工作流的三种存在形态

这是ACG框架最核心的分类创新：

```
┌─────────────────────────────────────────────────────────┐
│                                                          │
│  ACG Template (Ḡ)         Realized Graph (G_run)        │
│  ┌─────────────┐          ┌─────────────┐               │
│  │ 可复用蓝图   │──实例化──►│ 实际执行图   │              │
│  │ 部署前确定   │          │ 运行时确定   │              │
│  └─────────────┘          └──────┬──────┘               │
│                                  │                      │
│                                  ▼                      │
│                           Execution Trace (τ)           │
│                           ┌─────────────┐               │
│                           │ 执行轨迹     │               │
│                           │ 状态+动作+   │               │
│                           │ 观察+成本    │               │
│                           └─────────────┘               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**具体例子**：

1. **固定流水线**："规划-检索-执行-验证"
   - 模板 = 流水线定义本身
   - 实例化图 = 某次问题实际走到的分支（可能跳过了验证步骤）
   - 执行轨迹 = 检索、代码执行、验证与重试记录

2. **动态生成DAG**：系统根据查询生成新的多智能体DAG
   - 模板 = 一套算子库或图生成策略
   - 实例化图 = 每个输入触发出来的那张图
   - 执行轨迹 = 实际运行过程

**核心问题**：我们到底在优化什么？是可复用的蓝图，还是单次运行的结构？

## 4. 两大分类维度

### 4.1 图确定时间（Graph Determination Time, GDT）

结构是在什么时候确定的？

| GDT | 含义 | 特点 |
|-----|------|------|
| **offline** | 部署前优化可复用模板 | 稳定、可控、易测试 |
| **pre-execution** | 执行前生成特定运行的图 | 适应性强、有一定可控性 |
| **in-execution** | 执行过程中动态修改结构 | 最灵活、最难控制 |

### 4.2 图可塑性模式（Graph Plasticity Mode, GPM）

推理时结构可变性有多大？

| GPM | 含义 | 代表方法 |
|-----|------|----------|
| **none** | 结构固定 | 传统Pipeline |
| **select** | 从固定超图中选择子图 | Adaptive Graph Pruning, DAGP, AgentDropout |
| **generate** | 执行前生成新结构 | G-Designer, FlowReasoner, Workflow-R1 |
| **edit** | 执行中添加/删除/重连结构 | DyFlow, AgentConductor, MetaGen, EvoFlow |

### 4.3 GDT × GPM 分类矩阵

```
              │  none  │ select │ generate │  edit
──────────────┼────────┼────────┼──────────┼───────
offline       │ 固定模板│ 超图选择│ 模板搜索  │  ─
pre-execution │   ─    │ 子图激活│ DAG生成   │  ─
in-execution  │   ─    │  ─     │   ─       │ 动态编辑
```

## 5. 静态工作流优化

### 5.1 离线模板搜索

通过搜索离散设计空间发现优质模板：

| 方法 | 搜索策略 | 表示形式 | 反馈信号 | 特点 |
|------|----------|----------|----------|------|
| **AFlow** | MCTS搜索类型化算子图 | 代码 | 可执行评估 | 结合LLM引导扩展，包含实际资金开销 |
| **ADAS** | 代码空间搜索 | 代码 | 元代理迭代改进 | 图灵完备搜索空间 |
| **VFlow** | 协同进化+MCTS | 代码 | 多层级验证 | 语法+功能+硬件约束验证 |
| **Maestro** | 交替图编辑+节点配置更新 | 代码 | 数字分数+反思文本 | 结构与参数协同进化 |

### 5.2 节点级优化

在固定脚手架内优化局部组件：

| 方法 | 优化对象 | 优化方式 |
|------|----------|----------|
| **DSPy** | Prompt + few-shot示例 | 编译器自动优化 |
| **OPRO/EvoPrompt/CAPO** | 提示词 | 进化算法或LLM作为优化器 |
| **Optima** | 多智能体交互轨迹 | 生成、排序、选择 |

### 5.3 可验证性设计

静态优化特别适合集成验证：

| 方法 | 验证方式 |
|------|----------|
| **MermaidFlow** | 结构化Mermaid中间表示 + 静态有效性检查 |
| **VFlow** | 多层级验证（语法、功能、硬件约束）集成到搜索循环 |

## 6. 动态工作流优化

### 6.1 选择与剪枝（Select/Prune）

最轻量的动态形式：保持超图固定，运行时决定激活哪些部分。

| 方法 | 机制 |
|------|------|
| **Adaptive Graph Pruning** | 学习任务和代理嵌入，剪枝通信边和代理 |
| **DAGP** | 基于估计的查询难度进行难度感知的图剪枝 |
| **AgentDropout** | 动态消除冗余代理和通信链接以优化token效率 |

### 6.2 执行前生成（Pre-execution Generation）

针对特定输入生成工作流结构：

| 方法 | 生成机制 | 特点 |
|------|----------|------|
| **Assemble Your Crew** | 自回归采样角色和边 | 生成查询条件化的DAG |
| **G-Designer** | 变分图自编码器 | 学习图生成器 |
| **FlowReasoner** | RL训练查询级元代理 | 从算子库生成工作流 |
| **Workflow-R1** | 分组think-act序列的RL优化 | 多轮决策过程 |

### 6.3 执行中编辑（In-execution Editing）

最灵活的形式：将结构变化作为运行时动作：

| 方法 | 编辑机制 | 特点 |
|------|----------|------|
| **DyFlow** | 设计师与执行器交替 | 基于中间反馈修订子目标 |
| **AgentConductor** | 生成YAML拓扑→执行→重新生成 | 基于有效性/成本反馈 |
| **MetaGen** | 基于矛盾、失败和成本信号 | 训练免费地演化角色和拓扑 |
| **EvoFlow** | 维护多样化工作流种群 | 在线进化 |

## 7. 反馈信号与更新机制

不同方法使用不同的反馈信号指导结构优化：

| 信号类型 | 代表方法 | 安全动作粒度 |
|----------|----------|--------------|
| **指标/分数驱动** | AFlow, ADAS | 激进的图变异 |
| **验证器驱动** | VFlow, MermaidFlow | 激进的图变异（强验证器支持） |
| **偏好/排序信号** | Optima, CAPO | 中等粒度修改 |
| **轨迹文本反馈** | Maestro, DebFlow | 提出修改建议（需外部验证器确认） |

**关键洞见**：信号类型决定了安全的动作粒度。强验证器支持激进的图变异，文本反馈适合提出修改建议但需外部验证器确认。

## 8. 评估框架

### 8.1 将工作流视为一等公民

论文提出结构感知的评估视角，补充下游任务指标：

| 评估维度 | 含义 |
|----------|------|
| **Effectiveness** | 任务完成质量 |
| **Efficiency** | Token消耗、延迟、资金成本 |
| **Robustness** | 对输入变化的稳定性 |
| **Graph-level properties** | 图的复杂度、深度、宽度、连通性 |

### 8.2 最小报告协议

论文提出了一个最小报告协议，要求研究者报告：

1. 工作流结构定义（模板/实例化图/执行轨迹）
2. GDT和GPM分类
3. 优化目标（质量/成本/联合）
4. 反馈信号类型
5. 评估指标（任务指标+图指标+成本指标）
6. 基线对比方法

## 9. 实践指导

### 9.1 何时静态就够了？

当任务同质性强、分布稳定时，静态模板搜索（如AFlow、Maestro）是最安全、最高效的选择。

### 9.2 何时select胜过generate，何时edit不可避免？

- **select**：当任务类型有限但需要动态裁剪时（如AgentDropout）
- **generate**：当任务异质性强、需要定制化工作流时（如FlowReasoner）
- **edit**：当执行过程中可能遇到意外、需要实时调整时（如DyFlow）

### 9.3 何时图优化比提示词调优更重要？

当工作流结构本身是瓶颈时（如"越做越臃肿却不变强"），图优化比提示词调优更重要。

### 9.4 验证器在哪里最值得投入？

在静态优化中，验证器可以防止无效结构进入搜索；在动态编辑中，验证器是安全编辑的必要保障。

## 10. 开放问题与未来方向

1. **结构信用分配**：如何判断性能提升是来自哪个节点的修改？
2. **表达力与可验证性的权衡**：更灵活的表示形式更难验证
3. **持续适应**：工具和环境漂移下的持续优化
4. **数据与基准质量**：需要更好的工作流优化基准
5. **工作流优化理论**：缺乏理论保证，如收敛性、最优性

## 11. ACG的形式化定义

### 11.1 ACG Template (Ḡ)

```
Ḡ = (N, E, P, R, A)
```

- N：节点集合
- E：边集合
- P：节点参数（提示词、工具、模型选择）
- R：路由策略
- A：允许的编辑动作

### 11.2 Realized Graph (G_run)

```
G_run = instantiate(Ḡ, input, state)
```

从模板实例化或动态生成的、针对某次具体运行的工作流结构。

### 11.3 Execution Trace (τ)

```
τ = {(s_t, a_t, o_t, c_t) | t = 0, 1, ..., T}
```

- s_t：时刻t的系统状态
- a_t：采取的动作
- o_t：观察到的结果
- c_t：累积的执行成本

### 11.4 联合优化目标

```
maximize: Quality(G_run, task) - λ · Cost(τ)
```

其中λ是质量与成本的权衡系数。

## 12. 关键参考文献

1. From Static Templates to Dynamic Runtime Graphs (Yue et al., 2026) - arXiv:2603.22386
2. AFlow: MCTS-based Workflow Optimization (2024) - arXiv:2410.10762
3. ADAS: Automated Design of Agentic Systems (ICLR 2025) - arXiv:2408.08435
4. Maestro: Joint Structure-Parameter Optimization (2025)
5. DSPy: Compiler-based Prompt Optimization (2024)
6. G-Designer: Variational Graph Autoencoder for Agent Topology (2025)
7. FlowReasoner: RL-based Query-level Meta-Agent (2025)
8. DebFlow: Multi-agent Debate for Workflow Optimization (2025) - arXiv:2503.23781
9. PowerDAG: DAG-based Reliable Agentic System (2026) - arXiv:2603.17418
10. GLOW: Graph-Language Co-Reasoning for Workflow Prediction (2025) - arXiv:2512.15751

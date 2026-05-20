# 图论与Agent/Agentic结合的论文与实践代码全景

## 1. 综述性论文

### 1.1 Graphs Meet AI Agents (2025)

- **论文**：Graphs Meet AI Agents: Taxonomy, Progress, and Future Opportunities
- **ArXiv**：2506.18019
- **GitHub**：https://github.com/YuanchenBei/Awesome-Graphs-Meet-Agents
- **核心贡献**：提出了一个分类框架，将Graph与AI Agents的结合分为四个方向

```
┌──────────────────────────────────────────────────────┐
│           Graphs Meet AI Agents 分类框架              │
│                                                       │
│  ┌─────────────────┐    ┌─────────────────┐          │
│  │ Graph用于Agent   │    │ Agent用于Graph   │          │
│  │                 │    │                 │          │
│  │ • 规划(Planning)│    │ • 图注释        │          │
│  │ • 执行(Execution)│   │ • 图合成        │          │
│  │ • 记忆(Memory)  │    │ • 图理解        │          │
│  │ • 多Agent协调   │    │                 │          │
│  └─────────────────┘    └─────────────────┘          │
│                                                       │
│  ┌─────────────────────────────────────────┐         │
│  │ 图方法论                                │         │
│  │ • 图数据组织 • 知识提取 • 图学习        │         │
│  └─────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────┘
```

### 1.2 IBM ACG综述 (2026)

- **论文**：From Static Templates to Dynamic Runtime Graphs
- **ArXiv**：2603.22386
- **GitHub**：https://github.com/IBM/awesome-agentic-workflow-optimization
- 详见01-IBM-ACG-deep-dive.md

## 2. Graph用于Agent规划

### 2.1 任务推理

| 方法 | 图类型 | 机制 | 论文/来源 |
|------|--------|------|-----------|
| **QA-GNN** | 知识图 | 提取多跳子图信息辅助推理 | 2021 |
| **ToG (Think-on-Graph)** | 知识图 | 在知识图上进行束搜索 | 2023 |
| **KG-CoT** | 知识图 | 知识图增强的思维链 | 2023 |
| **RoG** | 知识图 | 推理路径生成 | 2023 |
| **MindMap** | 知识图 | 多跳推理可视化 | 2023 |
| **PoG** | 知识图 | 计划-then-推理图搜索 | 2024 |

### 2.2 结构化推理

| 方法 | 图类型 | 机制 |
|------|--------|------|
| **ToT (Tree-of-Thought)** | 树 | 将思维过程组织为树状结构 |
| **GoT (Graph-of-Thought)** | 图 | 将思维过程组织为图状结构，支持合并 |
| **RATT** | 树 | 推理+行动树 |
| **RwG** | 图 | 推理with图 |

### 2.3 任务分解

| 方法 | 图类型 | 机制 | 论文/来源 |
|------|--------|------|-----------|
| **DAG-Plan** | DAG | 任务依赖图表示子任务依赖关系 | 2024 |
| **AgentKit** | DAG | 图结构化任务分解 | 2024 |
| **VillagerAgent** | 任务图 | 村民式多Agent任务图 | 2024 |
| **DynTaskMAS** | 动态任务图 | 动态任务分配 | 2024 |
| **Plan-over-Graph** | 图 | 在图上进行规划 | 2024 |
| **LGC-MARL** | 图 | 图约束多Agent强化学习 | 2024 |

### 2.4 任务决策搜索

| 方法 | 图类型 | 搜索算法 |
|------|--------|----------|
| **LATS** | 状态空间图 | MCTS + LLM |
| **PromptAgent** | 状态空间图 | MCTS |
| **M-MCTS** | 状态空间图 | 多智能体MCTS |
| **MCGS** | 状态空间图 | 蒙特卡洛图搜索 |
| **GBOP** | 状态空间图 | 图引导束搜索 |

## 3. Graph用于Agent执行

### 3.1 工具使用优化

图技术帮助Agent更高效地管理和调用大量工具：
- 构建工具图（Tool Graph）
- 优化工具调用路径
- 减少Token消耗
- 提高工具使用的准确性和效率

### 3.2 环境交互增强

- 场景图（Scene Graph）提供环境结构化表示
- 动态学习方法增强环境理解
- 启发式和基于学习的关系建模

## 4. Graph用于Agent记忆管理

### 4.1 记忆组织

| 方法 | 图类型 | 特点 |
|------|--------|------|
| **AriGraph** | 知识图 | Agent自主构建的知识图谱 |
| **IKG** | 知识图 | 交互知识图 |
| **Graphusion** | 知识图 | 知识融合图 |
| **MemGraph** | 知识图 | 记忆图 |
| **GraphRAG** | 知识图 | 微软图增强RAG |
| **StructuralMemory** | 结构化图 | 结构化记忆系统 |

### 4.2 记忆检索

| 方法 | 检索策略 |
|------|----------|
| **G-Retriever** | 语义相似性 + 图度量 |
| **GFM-RAG** | 语义相似性 + 图度量 |
| **SubgraphRAG** | 基于查询相关性的灵活子图检索 |
| **LightRAG** | 双检索系统 |
| **GRAG** | 线性时间检索策略 |
| **PathRAG** | 流式剪枝减少检索延迟 |

### 4.3 记忆维护

| 方法 | 维护策略 |
|------|----------|
| **A-MEM** | 动态索引和链接创建知识网络 |
| **Zep** | 时间感知的层次化知识图谱引擎 |
| **HippoRAG/LightRAG** | 动态增量图更新 |
| **KG-Agent** | LLM进行知识图谱更新 |
| **InstructRAG** | RL代理进行图维护 |

## 5. Graph用于Multi-Agent协调

### 5.1 协调消息传递

| 方法 | 关系建模 | 机制 |
|------|----------|------|
| **FLOW-GNN** | 任务依赖 | 利用TDG优化消息传递 |
| **LGC-MARL** | 任务依赖 | 图约束多Agent RL |
| **RandStructure2Vec** | 任务分配 | 随机结构嵌入 |
| **MAGNNET** | 任务分配 | 多注意力图网络 |
| **GRL** | 环境特定 | 图强化学习 |
| **GraphComm** | 动态学习 | 图通信 |
| **MAGI** | 动态权重 | 多Agent图交互 |

### 5.2 协调拓扑优化

| 方法 | 优化方式 | 机制 |
|------|----------|------|
| **DICG** | 注意力机制 | 学习潜在边 |
| **G2ANet** | 参数化边权重 | 学习潜在边 |
| **G-Designer** | 图自编码器 | 预测代理节点之间的边 |
| **GNN-VAE** | 图变分自编码器 | 预测代理节点之间的边 |
| **HGRL** | 强化学习 | 奖励函数优化边 |
| **GPTSwarm** | 强化学习 | 奖励函数优化边 |

## 6. 工作流优化中的图方法

### 6.1 AFlow：MCTS搜索算子图

- **论文**：arXiv:2410.10762
- **GitHub**：https://github.com/geekan/MetaGPT/tree/main/examples/aflow
- **核心**：将工作流建模为类型化算子图，使用MCTS搜索最优结构
- **关键结果**：比手动设计平均高5.7分，只需原成本的4.55%

```
AFlow MCTS流程：
选择 → 扩展 → 评估 → 反向传播
  │        │        │         │
  ▼        ▼        ▼         ▼
从历史   生成新   在基准    更新得分
选最优   变体     测试上    和经验
候选     工作流   运行评估
```

### 6.2 DebFlow：多Agent辩论优化工作流

- **论文**：arXiv:2503.23781v3 (2025)
- **核心**：使用多Agent辩论来优化工作流，而非单模型推理
- **创新**：细粒度反馈机制，在节点和边级别分析工作流失败

### 6.3 GLOW：图-语言协同推理预测工作流性能

- **论文**：arXiv:2512.15751 (2025)
- **GitHub**：https://github.com/guanwei49/GLOW
- **核心**：结合GNN的图结构建模能力和LLM的语义推理能力
- **创新**：图导向的LLM指令微调（包含可达性、拓扑排序等图推理任务）

### 6.4 PowerDAG：基于DAG的可靠Agent系统

- **论文**：arXiv:2603.17418v3 (2026)
- **核心**：将工作流建模为DAG，引入自适应检索和即时监督
- **关键结果**：GPT-5.2上100%成功率，开源模型94.4-96.7%

### 6.5 Risk-Sensitive Agent Compositions

- **论文**：arXiv:2506.04632v2 (2025, UPenn)
- **核心**：将Agent工作流形式化为DAG（Agent Graph），边代表Agent，路径代表可行组合
- **创新**：最小化Agent组合的风险（VaR），使用动态规划近似
- **应用**：视频游戏控制基准测试

## 7. 框架级实践代码

### 7.1 LangGraph：图论驱动的状态机

- **GitHub**：https://github.com/langchain-ai/langgraph
- **核心思想**：工作流是有向状态图，节点=Agent/函数，边=条件跳转，状态=共享数据
- **灵感来源**：Pregel、Apache Beam、NetworkX

```python
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    messages: list
    next_step: str
    research_data: dict

workflow = StateGraph(AgentState)
workflow.add_node("research", research_node)
workflow.add_node("analyze", analyze_node)
workflow.add_node("write", write_node)

workflow.set_entry_point("research")
workflow.add_conditional_edges("research", should_continue, {
    "analyze": "analyze",
    "write": "write",
    "end": END
})
workflow.add_edge("write", END)

app = workflow.compile()
```

**关键特性**：
- 检查点持久化（时间旅行调试）
- 原子状态更新（Reducer机制）
- 并行边支持（扇出-扇入）
- Human-in-the-loop断点

### 7.2 AutoGen GraphFlow：有向图工作流引擎

- **版本**：AutoGen v0.5.6
- **核心**：DiGraphBuilder + GraphFlow类

```python
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow

builder = DiGraphBuilder()
builder.add_node(translator).add_node(proofreader).add_node(formatter)
builder.add_edge(translator, proofreader)
builder.add_edge(proofreader, formatter)

graph = builder.build()
flow = GraphFlow(participants=builder.get_participants(), graph=graph)
result = await flow.run(task="Translate...")
```

**支持模式**：
- 顺序工作流
- 并行工作流（扇出-扇入）
- 任意复杂拓扑

### 7.3 GPTSwarm：图优化多Agent系统

- **核心**：将Agent表示为图节点，通信表示为边
- **优化方式**：强化学习优化边连接
- **特点**：可学习的通信拓扑

### 7.4 AgentScope：消息驱动多Agent

- **阿里达摩院**开源
- **核心**：Everything is a Message
- **图论关联**：消息传递拓扑可建模为图

## 8. 图论算法在Agent中的具体应用映射

| 图论算法 | Agent应用 | 具体场景 |
|----------|-----------|----------|
| **拓扑排序** | 任务调度 | DAG-Plan中确定子任务执行顺序 |
| **最短路径** | 最优Agent选择 | Risk-Sensitive中找最小风险路径 |
| **MCTS** | 工作流搜索 | AFlow中搜索最优工作流结构 |
| **图着色** | 资源分配 | 并行任务调度中的冲突检测 |
| **最大流** | 负载均衡 | 多Agent间的任务分配 |
| **连通分量** | 独立子任务识别 | DCM分解中识别可独立求解的组件 |
| **最小生成树** | 最小通信开销 | 多Agent协调中优化通信拓扑 |
| **图匹配** | Agent-任务匹配 | 为子任务选择最合适的Agent |
| **PageRank** | Agent重要性排序 | 确定关键Agent和冗余Agent |
| **图嵌入(GNN)** | 拓扑特征提取 | GLOW中编码工作流结构特征 |
| **图自编码器** | 拓扑生成 | G-Designer中生成Agent通信图 |
| **子图检索** | 记忆检索 | SubgraphRAG中检索相关记忆 |

## 9. 关键论文索引

| # | 论文 | 年份 | 图类型 | ArXiv/来源 |
|---|------|------|--------|------------|
| 1 | IBM ACG综述 | 2026 | ACG | 2603.22386 |
| 2 | Graphs Meet AI Agents | 2025 | 综合 | 2506.18019 |
| 3 | AFlow | 2024 | 算子图 | 2410.10762 |
| 4 | ADAS | 2025 | 代码图 | 2408.08435 |
| 5 | DebFlow | 2025 | 有向图 | 2503.23781 |
| 6 | GLOW | 2025 | DAG | 2512.15751 |
| 7 | PowerDAG | 2026 | DAG | 2603.17418 |
| 8 | Risk-Sensitive Agent | 2025 | DAG | 2506.04632 |
| 9 | G-Designer | 2025 | 图自编码器 | - |
| 10 | FlowReasoner | 2025 | 算子图 | - |
| 11 | DAG-Plan | 2024 | DAG | - |
| 12 | AgentKit | 2024 | DAG | - |
| 13 | GoT (Graph-of-Thought) | 2023 | 思维图 | - |
| 14 | LATS | 2023 | 状态空间图 | - |
| 15 | GPTSwarm | 2024 | 通信图 | - |
| 16 | Maestro | 2025 | 可编辑图 | - |
| 17 | MermaidFlow | 2025 | Mermaid IR | - |
| 18 | DyFlow | 2025 | 动态图 | - |
| 19 | EvoFlow | 2025 | 进化图 | - |
| 20 | AgentDropout | 2025 | 超图 | - |

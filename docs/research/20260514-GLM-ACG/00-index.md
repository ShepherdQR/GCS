# 图论与Agent/Agentic结合研究索引

研究日期：2026-05-14

## 研究主题

### [01-IBM-ACG-deep-dive.md](01-IBM-ACG-deep-dive.md)
**IBM ACG：智能体计算图深度研究**

核心内容：
- ACG核心概念：节点（原子操作）+ 边（依赖关系）
- 工作流三种存在形态：ACG Template → Realized Graph → Execution Trace
- 两大分类维度：GDT（图确定时间）× GPM（图可塑性模式）
- 静态优化：AFlow(MCTS)、ADAS(代码搜索)、Maestro(联合优化)、DSPy(节点优化)
- 动态优化：Select/Prune、Pre-execution Generate、In-execution Edit
- 反馈信号：指标驱动、验证器驱动、偏好排序、轨迹文本
- 实践指导：何时静态/选择/生成/编辑

关键论文：arXiv:2603.22386 (RPI + IBM Research, 2026)

### [02-graph-theory-agent-papers.md](02-graph-theory-agent-papers.md)
**图论与Agent结合的论文与实践代码全景**

核心内容：
- 综述论文：Graphs Meet AI Agents (arXiv:2506.18019)
- Graph用于Agent规划：任务推理(KG-CoT, ToT, GoT)、任务分解(DAG-Plan, AgentKit)、决策搜索(LATS, MCTS)
- Graph用于Agent执行：工具使用优化、环境交互增强
- Graph用于Agent记忆：记忆组织(GraphRAG)、检索(SubgraphRAG)、维护(HippoRAG)
- Graph用于Multi-Agent协调：消息传递(GraphComm)、拓扑优化(G-Designer, GPTSwarm)
- 工作流优化：AFlow、DebFlow、GLOW、PowerDAG、Risk-Sensitive Agent
- 框架实践：LangGraph、AutoGen GraphFlow、GPTSwarm
- 12种图论算法在Agent中的具体应用映射
- 20篇关键论文索引

### [03-graph-algorithms-agent-planning.md](03-graph-algorithms-agent-planning.md)
**利用图论算法规划Agent：从理论到实践**

核心内容：
- 6种核心图论算法的Agent规划实现：
  - 拓扑排序 → 任务执行顺序（含并行层级计算）
  - 最短路径 → 最优Agent选择（Dijkstra）
  - 关键路径法(CPM) → 最长执行时间估算
  - 最大流 → 负载均衡（Edmonds-Karp）
  - 连通分量 → 独立子任务识别
  - MCTS → 工作流结构搜索
- 综合实践：GraphBasedAgentPlanner完整框架
- GCS项目应用示例
- 动态图编辑：运行时适应（In-execution Editing）
- 查询级工作流生成（Pre-execution Generation）
- 图论算法选择指南
- ACG框架到实践的4种设计模式

## 核心洞察

1. **工作流结构是一等公民**：Agent性能瓶颈往往在工作流结构本身，而非单个Prompt或模型
2. **三种存在形态的区分至关重要**：Template（蓝图）vs Realized Graph（实例）vs Trace（轨迹），优化对象不同
3. **图论算法是Agent规划的自然工具**：DAG天然对应任务依赖，拓扑排序天然对应执行顺序
4. **动态性是关键趋势**：从静态模板到动态图，从部署前优化到运行时适应
5. **表示形式即约束**：代码/DSL/JSON/图IR的选择直接决定什么可以被搜索和验证
6. **反馈信号决定动作粒度**：强验证器支持激进变异，文本反馈需外部验证

## 关键资源

- IBM ACG GitHub: https://github.com/IBM/awesome-agentic-workflow-optimization
- Graphs Meet Agents GitHub: https://github.com/YuanchenBei/Awesome-Graphs-Meet-Agents
- AFlow GitHub: https://github.com/geekan/MetaGPT/tree/main/examples/aflow
- GLOW GitHub: https://github.com/guanwei49/GLOW
- LangGraph: https://github.com/langchain-ai/langgraph
- AutoGen: https://github.com/microsoft/autogen

# Agent编程写作范式设计

## 1. 引言：从LLM到Agentic AI的范式跃迁

AI Agent的发展经历了四个关键阶段：

| 年代 | 范式 | 新增能力 | Agent相关性 |
|------|------|----------|-------------|
| 2010s | RNN/LSTM | 长短期记忆 | 多步规划雏形 |
| 2020s | Transformer+RLHF | 全局上下文+指令跟随 | 涌现自主性 |
| 2023-2024 | RAG+工具调用 | 外部知识检索+行动能力 | 连接型问题解决者 |
| 2025-2026 | Multi-Agent+自进化 | 分工协作+自我改进 | 多智能体协作系统 |

Agent编程写作范式的核心问题是：**如何用代码定义一个能自主感知、推理、行动和学习的智能体系统**。

## 2. Agent的核心抽象：五元组模型

根据AI Agent Systems综述（2025），Agent可抽象为五元组：

```
Agent = (πθ, M, T, V, E)
```

- **πθ**：LLM/VLM策略核心（推理引擎）
- **M**：记忆（向量库、摘要、状态）
- **T**：工具（API、代码、机器人）
- **V**：验证器/批评家
- **E**：环境（可观测、可反馈）

### 2.1 Agent执行循环

```
Perception → Reasoning → Action → Memory → Environment
     ↑                                        |
     └────────────────────────────────────────┘
```

每个Agent遵循五步循环：
1. **接受任务**：接收目标（如"整理日程"）
2. **扫描环境**：收集必要信息（读取邮件、检查日历）
3. **制定计划**：思考实现目标的最佳方法
4. **执行行动**：发送邀请、安排会议、更新日历
5. **学习改进**：观察结果并适应调整

## 3. 九种核心设计模式

### 3.1 ReAct：动态校准的"实时决策者"

**来源**：2022年斯坦福+谷歌DeepMind论文《ReAct: Synergizing Reasoning and Acting in Language Models》

**核心机制**：
```
LLM分析需求 → 确定工具/步骤 → 执行后获取环境反馈 → 修正决策路径
循环直至置信度≥95%或达到迭代上限
```

**关键组件**：
- 思考模块（需求拆解）
- 行动调度器（工具调用）
- 观察反馈器（结果验证）

**适用场景**：实时动态查询、代码调试、IT故障排查

**优劣势**：
- ✅ 强容错性（单步错误可实时修正）、决策透明度高
- ❌ 多轮交互导致延迟升高（平均+1.2s/次）、不支持并行执行

### 3.2 Plan-and-Solve：全局规划的"战略引擎"

**来源**：2023年新加坡国立大学+微软亚洲研究院论文

**核心机制**：全局规划→动态执行→弹性调整三级架构
- 规划层：用DAG拆解子任务并定义依赖关系
- 执行层：按序调用工具完成子任务
- 调整层：遇突发情况实时回滚/重排子任务

**适用场景**：多步骤复杂流程、长期目标落地、项目管理类任务

### 3.3 REWOO：流水线化"推理-执行"解耦

**核心差异**：ReAct串行调用工具，REWOO"思考一次→调用所有"并行执行

**核心机制**：
- 规划阶段：一次性生成完整"执行链"
- 执行阶段：预加载依赖参数，单次批量调用工具

**适用场景**：标准化批处理任务、高频率重复任务

**性能提升**：4步任务耗时从8.2s降至3.1s

### 3.4 Reflection：自我反思模式

Agent在提交输出前评估其输出质量，根据评估结果进行修正。

### 3.5 Routing：路由模式

根据输入动态选择处理路径，将不同类型的请求分发到专门的处理器。

### 3.6 Parallelization：并行化模式

同时执行多个独立任务，提高吞吐量。

### 3.7 Tool Use：工具使用模式

集成外部API和服务，扩展Agent的能力边界。

### 3.8 Planning：规划模式

制定多步骤行动计划，处理复杂任务。

### 3.9 Multi-Agent：多智能体模式

协调多个专业智能体协作完成复杂目标。

## 4. Agent的四个复杂度层级

| 层级 | 名称 | 能力描述 |
|------|------|----------|
| Level 0 | 核心推理引擎 | LLM本身，仅基于预训练知识响应 |
| Level 1 | 连接型问题解决者 | 连接外部工具，执行操作收集信息 |
| Level 2 | 战略型问题解决者 | 战略规划、主动协助、自我改进 |
| Level 3 | 多智能体协作系统 | 多个专业智能体分工协同 |

## 5. Agent编程写作范式的核心原则

### 5.1 Prompt即程序（Prompt as Program）

将Prompt视为"软程序"，通过上下文工程（Context Engineering）定义Agent的行为：
- System Prompt定义角色、能力边界、行为约束
- 工具描述定义可用的行动空间
- 记忆注入提供历史经验

### 5.2 结构化输出（Structured Output）

Agent的输出必须是结构化的，便于下游处理：
```python
class AgentOutput:
    thought: str       # 推理过程
    action: str        # 选择的行动
    action_input: dict # 行动参数
    observation: str   # 观察结果
```

### 5.3 工具即接口（Tool as Interface）

每个工具是一个标准化的接口：
```python
class Tool:
    name: str           # 工具名称
    description: str    # 功能描述
    parameters: dict    # 参数schema
    execute: callable   # 执行函数
```

### 5.4 记忆即状态（Memory as State）

Agent的记忆系统分为三层：
- **短期记忆**：当前对话上下文
- **长期记忆**：向量数据库中的历史经验
- **共享状态**：多Agent间的"黑板"或全局变量

### 5.5 验证即护栏（Validation as Guardrail）

每个Agent输出都应经过验证：
- 格式校验：输出是否符合预期结构
- 内容校验：输出是否在安全范围内
- 质量校验：输出是否满足质量标准

## 6. 实践范式：代码模板

### 6.1 单Agent循环范式

```python
class Agent:
    def __init__(self, llm, tools, memory):
        self.llm = llm
        self.tools = tools
        self.memory = memory

    def run(self, task, max_iterations=10):
        for i in range(max_iterations):
            prompt = self.build_prompt(task)
            response = self.llm.generate(prompt)
            action = self.parse_action(response)

            if action.type == "FINISH":
                return action.output

            observation = self.execute_action(action)
            self.memory.add(observation)

        return "Max iterations reached"
```

### 6.2 规划-执行范式

```python
class PlanExecuteAgent:
    def __init__(self, planner, executor, memory):
        self.planner = planner
        self.executor = executor
        self.memory = memory

    def run(self, task):
        plan = self.planner.create_plan(task)
        results = {}

        for step in plan.steps:
            if self.dependencies_met(step, results):
                result = self.executor.execute(step, results)
                results[step.id] = result
            else:
                plan = self.planner.replan(plan, step, results)

        return self.synthesize(results)
```

### 6.3 反思范式

```python
class ReflectiveAgent:
    def __init__(self, actor, critic, max_revisions=3):
        self.actor = actor
        self.critic = critic
        self.max_revisions = max_revisions

    def run(self, task):
        draft = self.actor.generate(task)

        for i in range(self.max_revisions):
            feedback = self.critic.evaluate(draft, task)
            if feedback.approved:
                return draft
            draft = self.actor.revise(draft, feedback)

        return draft
```

## 7. 智能体计算图（ACG）范式

IBM Research 2026年提出"智能体计算图（Agentic Computation Graph, ACG）"概念，将Agent系统统一抽象为：

- **节点（Nodes）**：执行原子操作（LLM调用、信息检索、工具使用、逻辑验证）
- **边（Edges）**：编码依赖关系（控制流、数据流、通信依赖）

工作流的三种存在形态：
1. **可重用模板（ACG Template）**：部署前确定的可重用执行规范
2. **实例化图（Realized Graph）**：给定输入后实际执行的工作流结构
3. **执行轨迹（Execution Trace）**：运行后产生的数据记录

## 8. 关键参考文献

1. ReAct: Synergizing Reasoning and Acting in Language Models (Stanford + Google DeepMind, 2022)
2. Plan-and-Solve Prompting (NUS + MSRA, 2023)
3. Agentic Design Patterns (Antonio Gulli, Google, 2025)
4. AI Agent Systems: Architectures, Applications, and Evaluation (2025)
5. Agent System Design Patterns (Microsoft Azure/Databricks, 2025)
6. IBM Research: Agentic Computation Graph (2026)

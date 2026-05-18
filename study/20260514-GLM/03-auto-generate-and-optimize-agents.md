# 自动生成Agent并不断优化：从ADAS到HyperAgents

## 1. 引言：Agent设计的自动化革命

传统Agent系统依赖人工设计——研究者需要手动编写系统框架，通过多轮迭代优化方能达到理想效果。这不仅造成极高的设计成本，也使系统难以推广至通用场景。

2024-2026年，三个里程碑式的研究改变了这一局面：
1. **ADAS**（ICLR 2025）：首次实现Agent系统的全自动设计
2. **MetaAgent**（ICML 2025）：基于有限状态机自动构建多Agent系统
3. **HyperAgents**（ICLR 2026）：实现跨领域元认知自我修改

## 2. ADAS：智能体系统自动设计

### 2.1 核心思想

**论文**：Automated Design of Agentic Systems (Shengran Hu, Cong Lu, Jeff Clune, ICLR 2025)

**核心问题**：能否让AI自己设计Agent？

**关键洞察**：既然人类设计Agent的过程本身就是一种"规划+工具使用+执行"的活动，那么一个元Agent（Meta Agent）完全可以承担这个任务。

### 2.2 元智能体搜索算法（Meta Agent Search）

```
┌─────────────────────────────────────────────────┐
│           Meta Agent Search 流程                 │
│                                                  │
│  ┌────────────┐    ┌────────────┐               │
│  │ Agent      │    │ Meta Agent │               │
│  │ Archive    │───►│ (设计者)    │               │
│  │ (历史设计) │    └──────┬─────┘               │
│  └────────────┘           │                     │
│       ▲                   ▼                     │
│       │           ┌──────────────┐              │
│       │           │ 新Agent代码  │              │
│       │           └──────┬───────┘              │
│       │                  │                      │
│       │                  ▼                      │
│       │           ┌──────────────┐              │
│       │           │ 反思与修正    │              │
│       │           │ (新颖性+正确性)│              │
│       │           └──────┬───────┘              │
│       │                  │                      │
│       │                  ▼                      │
│       │           ┌──────────────┐              │
│       └───────────│ 评估与测试    │              │
│                   └──────────────┘              │
└─────────────────────────────────────────────────┘
```

**三个核心步骤**：

1. **建立搜索空间**：用代码作为搜索空间的基础元素
   - 代码具有图灵完备性，能表达所有可能性
   - 代码可直接运行、纠错、跑分，无需人工干预
   - 工具调用、RAG等能力组件已有充分的代码基础

2. **运行搜索算法**：元智能体利用搜索空间构建新Agent
   - 元智能体接收：任务描述、框架代码、输入输出格式、历史范例库
   - 生成新Agent代码
   - 两轮反思保证新颖性和正确性

3. **运行评估函数**：对生成的Agent进行性能评估
   - 在基准测试上运行
   - 保留表现优异的设计
   - 淘汰表现不佳的设计

### 2.3 为什么选择代码空间？

| 搜索空间 | 表达能力 | 可执行性 | 可组合性 | 理论完备性 |
|----------|----------|----------|----------|------------|
| 自然语言提示 | 有限 | ❌ | 弱 | ❌ |
| DSL/JSON | 中等 | ⚠️ | 中等 | ❌ |
| **代码** | **无限** | **✅** | **强** | **✅（图灵完备）** |

代码空间搜索的理论优势：由于编程语言的图灵完备性，该方法具备发现任意可能Agent系统的理论潜力。

### 2.4 实验结果

ADAS在多个基准测试上显著优于人工设计的基线方法：

| 基准测试 | 任务类型 | 相对提升 |
|----------|----------|----------|
| ARC | 抽象推理 | +13.6% |
| MGSM | 数学推理 | +25.9% |
| DROP | 阅读理解 | +15.2% |
| GPQA | 科学问答 | +18.7% |

**关键发现**：ADAS发现的Agent设计具有强大的跨领域和跨模型迁移能力。

### 2.5 ADAS实践指南

```bash
# 环境配置
git clone https://gitcode.com/gh_mirrors/adas/ADAS
cd ADAS
conda create -n adas python=3.11
conda activate adas
pip install -r requirements.txt
export OPENAI_API_KEY="YOUR_KEY"

# 运行智能体搜索
python _arc/search.py      # ARC视觉推理
python _drop/search.py     # DROP阅读理解
python _mmlu/search.py     # MMLU通用知识
```

**扩展到新领域的四步骤**：
1. 修改评估函数：调整`evaluate_forward_fn()`
2. 添加基础功能：为新领域提供所需的基础函数
3. 更新提示信息：调整领域特定的提示模板
4. 运行与评估：执行搜索和性能评估

## 3. MetaAgent：基于有限状态机的自动构建

### 3.1 核心思想

**论文**：MetaAgent: Automatically Constructing Multi-Agent Systems Based on Finite State Machines (ICML 2025)

**核心创新**：给定任务描述，自动生成完整的多Agent系统，并通过状态优化算法减少冗余。

### 3.2 三个关键特性

1. **工具调用（Tool-using）**：Agent可调用外部工具扩展能力
2. **状态回溯（Traceback）**：支持回退到之前的状态，实现错误恢复
3. **自优化（Self-optimization）**：无需外部数据，系统自身迭代优化

### 3.3 有限状态机模型

```python
class FiniteStateMachine:
    def __init__(self):
        self.states = {}      # 状态集合
        self.transitions = {} # 转移函数
        self.current_state = "init"

    def add_state(self, name, agent_config):
        self.states[name] = agent_config

    def add_transition(self, from_state, to_state, condition):
        self.transitions[(from_state, condition)] = to_state

    def step(self, input_data):
        agent = self.get_agent(self.current_state)
        result = agent.execute(input_data)

        condition = self.evaluate_condition(result)
        self.current_state = self.transitions.get(
            (self.current_state, condition),
            self.current_state
        )
        return result
```

### 3.4 自动构建流程

```
任务描述 → FSM生成 → Agent配置 → 状态优化 → 最终系统
              │           │           │
              ▼           ▼           ▼
         识别关键步骤  分配角色工具  消除冗余状态
```

### 3.5 实验结果

MetaAgent在机器学习任务上得分0.83，接近甚至超过人工设计系统的性能。

## 4. HyperAgents：跨领域元认知自我修改

### 4.1 核心思想

**论文**：HyperAgents (Meta, ICLR 2026, arXiv:2603.19461)

**从哥德尔机到达尔文哥德尔机**：

| 概念 | 核心思想 | 局限 |
|------|----------|------|
| 哥德尔机 | 通过递归重写自身代码实现自我完善 | 要求每次改动必须"证明"绝对有益，现实中不可行 |
| 达尔文哥德尔机(DGM) | 用达尔文进化替代数学证明，批量生成改进方案并筛选 | 仅在编程领域有效（任务与自我修改必须对齐） |
| **HyperAgents** | 元认知自我修改——不仅学习如何做得更好，还学习如何更有效地进行改进 | 打破领域壁垒，实现跨领域迁移 |

### 4.2 核心机制

```
┌─────────────────────────────────────────────┐
│            HyperAgents 架构                  │
│                                              │
│  ┌──────────────┐    ┌──────────────┐       │
│  │  Task Agent   │    │  Meta Agent   │       │
│  │  (执行任务)   │◄──►│  (改进方法)   │       │
│  └──────┬───────┘    └──────┬───────┘       │
│         │                   │                │
│         │    ┌──────────────┘                │
│         │    │                               │
│         ▼    ▼                               │
│  ┌──────────────────┐                       │
│  │  可编辑程序       │                       │
│  │  (统一代码空间)   │                       │
│  └──────────────────┘                       │
│         │                                    │
│         ▼                                    │
│  ┌──────────────────┐                       │
│  │  Agent Archive    │                       │
│  │  (进化种群库)     │                       │
│  └──────────────────┘                       │
└─────────────────────────────────────────────┘
```

**关键创新**：将"执行任务的Agent"和"负责改进Agent的Meta Agent"融合进同一个可编辑程序中。

### 4.3 进化过程

```python
class HyperAgentEvolution:
    def __init__(self, base_agent_code, meta_agent_code):
        self.agent_archive = []
        self.base_code = base_agent_code
        self.meta_code = meta_agent_code

    def evolve(self, num_generations=50):
        for gen in range(num_generations):
            # 1. 从种群库中采样
            parent = self.sample_from_archive()

            # 2. Meta Agent生成改进补丁
            patch = self.meta_agent.propose_patch(
                parent_code=parent.code,
                task_history=parent.history,
                archive=self.agent_archive
            )

            # 3. 验证补丁
            if self.validate_patch(patch):
                new_agent = self.apply_patch(parent, patch)

                # 4. 评估新Agent
                score = self.evaluate(new_agent)

                # 5. 选择：保留还是淘汰
                if score > parent.score:
                    self.agent_archive.append(new_agent)
                else:
                    self.discard(patch)
            else:
                self.discard(patch)

    def validate_patch(self, patch):
        # 检查补丁的新颖性和正确性
        return self.is_novel(patch) and self.is_error_free(patch)
```

### 4.4 实验结果

| 任务 | 初始得分 | 最终得分 | 提升幅度 |
|------|----------|----------|----------|
| SWE-bench (编程) | 20% | 50% | +30% |
| Polyglot (多语言编程) | 14.2% | 30.7% | +16.5% |
| Paper Review (论文审阅) | 0.0 | 0.710 | +0.710 |
| Robotics Reward Design | 0.060 | 0.372 | +0.312 |

**迁移实验**：将paper review和robotics任务中演化出的HyperAgents迁移到Olympiad-level math grading，尽管初始得分接近0，但作为"生成更优Agent的Meta Agent"，50轮内将最好生成体推到0.630。

### 4.5 自主涌现的基础设施

HyperAgents在迭代中会**自动长出**以下基础设施：
- **Performance Tracking**：性能追踪系统
- **Persistent Memory**：持久化记忆（避免重复发明轮子）
- **Evaluation Analysis**：评估分析系统
- **Compute-Aware Planning**：计算感知规划

## 5. 其他自动生成与优化方法

### 5.1 AgentFactory（arXiv:2603.18000）

通过"可执行技能"实现自进化的框架：
- Agent随时间积累可执行模块形式的技能
- 技能经过版本化、测试和组合
- 系统每完成一项任务就变得更强大

### 5.2 DARWIN框架（arXiv:2602.05848）

"动态代理自改写进化网络"：
- Agent能够通过Agent级操作重写自身的神经网络权重和架构
- Agent分析自身性能瓶颈并提出架构修改建议

### 5.3 AutoAgent（2026年4月开源）

全球首个自我优化Agent开源项目：
- 通过Meta-Agent分析失败的轨迹
- 自动生成验证循环和格式校验器
- 24小时内迭代优化架构
- SpreadsheetBench成绩96.5%（排名第一）
- TerminalBench成绩55.1%（排名第一）

**关键发现——Model Empathy**：将同一模型用于Meta Agent和Task Agent时效果更佳，因为同一模型能更好地理解对方的思维方式。

### 5.4 Karpathy的AutoResearch（2026年3月）

630行Python代码的自主实验循环：
- AI Agent无需人工干预即可设计、运行和评估实验
- 2天内运行50个实验

**关键洞察**：改进循环的速度比单次迭代的质量更重要——"够好且快"的循环优于"完美但慢"的循环。

## 6. 自动生成Agent的统一框架

### 6.1 三层学习策略栈

```
┌─────────────────────────────────────────┐
│          RL 层（强化学习）                │
│  解决长程奖励稀疏、工具调用昂贵、        │
│  安全约束探索难                          │
├─────────────────────────────────────────┤
│          IL 层（模仿学习）                │
│  用专家轨迹做行为克隆，                  │
│  再DAgger对抗分布漂移                    │
├─────────────────────────────────────────┤
│          In-Context 层（上下文学习）      │
│  把Prompt当"软程序"，                    │
│  快速迭代工具模板与策略规则               │
└─────────────────────────────────────────┘
```

### 6.2 自动生成Agent的通用流程

```python
class AutoAgentGenerator:
    def __init__(self, meta_llm, evaluator, archive):
        self.meta_llm = meta_llm
        self.evaluator = evaluator
        self.archive = archive

    def generate_agent(self, task_description, num_iterations=10):
        best_agent = None
        best_score = -float('inf')

        for i in range(num_iterations):
            # 1. 基于历史生成新Agent设计
            agent_code = self.meta_llm.generate(
                prompt=self.build_generation_prompt(
                    task=task_description,
                    archive=self.archive.get_top_k(5),
                    iteration=i
                )
            )

            # 2. 反思与修正
            agent_code = self.reflect_and_fix(agent_code)

            # 3. 评估
            score = self.evaluator.evaluate(agent_code, task_description)

            # 4. 更新档案
            self.archive.add(agent_code, score)

            # 5. 选择最佳
            if score > best_score:
                best_score = score
                best_agent = agent_code

        return best_agent, best_score

    def reflect_and_fix(self, agent_code):
        reflection = self.meta_llm.generate(
            prompt=self.build_reflection_prompt(agent_code)
        )
        if reflection.has_issues:
            return self.meta_llm.generate(
                prompt=self.build_fix_prompt(agent_code, reflection)
            )
        return agent_code
```

### 6.3 持续优化的闭环

```
┌──────────────────────────────────────────────────┐
│                                                   │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│  │ 提出假设 │───►│ 验证假设 │───►│ 学习改进 │      │
│  └────▲────┘    └─────────┘    └────┬────┘      │
│       │                              │           │
│       └──────────────────────────────┘           │
│                                                   │
│  关键约束：可验证的结果                           │
│  "AI自进化仅在结果可验证的领域有效"               │
│                                                   │
└──────────────────────────────────────────────────┘
```

**三个独立研究团队在2025年确认**：AI自进化仅在结果可验证的领域有效。自进化需要客观评分函数——在成功难以量化的领域，系统无法可靠地自我改进。

## 7. 为GCS项目设计自动Agent生成方案

### 7.1 基于ADAS思路的Agent自动生成

```python
class GCSAgentGenerator:
    def __init__(self):
        self.meta_llm = None
        self.archive = AgentArchive()
        self.evaluator = GCSEvaluator()

    def generate_graph_designer_agent(self):
        task_desc = """
        设计一个Agent，能够根据用户需求生成满足特定属性的
        几何约束图（如点双连通、指定几何体数量、约束数量等）。
        """

        return self.meta_llm.generate(
            prompt=f"""
            任务：{task_desc}

            可用基础函数：
            - add_point(name, x, y): 添加点
            - add_distance_constraint(p1, p2, dist): 添加距离约束
            - add_angle_constraint(p1, p2, p3, angle): 添加角度约束
            - add_fix_constraint(p, x, y): 添加固定约束
            - verify_biconnectivity(graph): 验证点双连通性
            - count_geometries(graph): 计数几何体
            - count_constraints(graph): 计数约束

            历史设计：
            {self.archive.get_top_k(3)}

            请生成一个新的Agent代码。
            """
        )

    def evaluate_agent(self, agent_code):
        test_cases = [
            {"n_geo": 5, "n_constraint": 8, "biconnected": True},
            {"n_geo": 7, "n_constraint": 10, "biconnected": True},
            {"n_geo": 3, "n_constraint": 5, "biconnected": False},
        ]

        scores = []
        for case in test_cases:
            result = self.run_agent(agent_code, case)
            score = self.compute_score(result, case)
            scores.append(score)

        return sum(scores) / len(scores)
```

### 7.2 基于HyperAgents思路的持续优化

```python
class GCSHyperOptimizer:
    def __init__(self):
        self.task_agent_code = load_base_task_agent()
        self.meta_agent_code = load_base_meta_agent()
        self.archive = []

    def evolve(self, num_generations=50):
        for gen in range(num_generations):
            # Meta Agent分析失败轨迹
            failure_analysis = self.meta_agent.analyze_failures(
                self.archive
            )

            # 生成改进补丁
            task_patch = self.meta_agent.propose_task_patch(
                failure_analysis
            )
            meta_patch = self.meta_agent.propose_meta_patch(
                failure_analysis
            )

            # 应用补丁
            new_task_agent = apply_patch(self.task_agent_code, task_patch)
            new_meta_agent = apply_patch(self.meta_agent_code, meta_patch)

            # 评估
            task_score = self.evaluate_task_agent(new_task_agent)
            meta_score = self.evaluate_meta_agent(new_meta_agent)

            # 选择
            if task_score > self.best_task_score:
                self.task_agent_code = new_task_agent
                self.best_task_score = task_score

            if meta_score > self.best_meta_score:
                self.meta_agent_code = new_meta_agent
                self.best_meta_score = meta_score

            self.archive.append({
                "generation": gen,
                "task_score": task_score,
                "meta_score": meta_score,
                "task_patch": task_patch,
                "meta_patch": meta_patch
            })
```

## 8. 自动Agent生成的关键约束与安全

### 8.1 可验证性约束

自动生成Agent的前提是**结果可验证**：
- 必须有客观评分函数
- 在成功难以量化的领域，系统无法可靠地自我改进
- GCS项目的优势：约束图属性（双连通性、约束数等）是可验证的

### 8.2 安全约束

| 风险类型 | 描述 | 缓解措施 |
|----------|------|----------|
| 代码注入 | 生成的Agent代码可能包含恶意逻辑 | 沙箱执行、代码审计 |
| 无限循环 | Agent可能陷入无限循环 | 设置迭代上限、超时机制 |
| 资源消耗 | 进化过程可能消耗大量计算资源 | 预算控制、资源监控 |
| 过拟合 | Agent可能在测试集上过拟合 | 交叉验证、独立测试集 |
| 级联错误 | 多Agent系统中一个Agent的错误可能传播 | 错误隔离、质量守卫 |

### 8.3 补丁谱系追踪

```python
class PatchLineage:
    def __init__(self):
        self.lineage = []

    def record_patch(self, patch, parent_id, score_delta):
        self.lineage.append({
            "patch_id": uuid4(),
            "parent_id": parent_id,
            "patch_content": patch,
            "score_delta": score_delta,
            "timestamp": time.time()
        })

    def get_ancestry(self, patch_id):
        ancestry = []
        current = self.find_patch(patch_id)
        while current["parent_id"] is not None:
            ancestry.append(current)
            current = self.find_patch(current["parent_id"])
        return ancestry

    def rollback_to(self, patch_id):
        return self.get_ancestry(patch_id)[-1]["patch_content"]
```

## 9. 未来展望

### 9.1 从"手动设计"到"自动进化"的路线图

```
2024: 人工设计Agent（当前主流）
  │
  ▼
2025: ADAS自动生成Agent（已验证可行性）
  │
  ▼
2026: HyperAgents跨领域自我优化（正在进行）
  │
  ▼
2027+: Agent生态系统（Agent自动生成Agent，形成进化生态）
```

### 9.2 五大未来科研优先级

1. **可验证规划**：符号+神经混合，生成可证伪动作序列
2. **实时可解释**：链式思维→链式证据，支持回放
3. **持续记忆**：episodic+语义+程序三级分层，支持月级一致
4. **多Agent协议**：通信原语、冲突仲裁、动态分治
5. **治理基础设施**：标准化审计日志、权限即代码、合规基准

### 9.3 关键洞察总结

> "设计你的Agent，使其能够以最快速度完成'提出假设—验证—学习'的循环"——改进循环的速度比单次迭代的质量更重要。（Karpathy, 2026）

> "AI自进化仅在结果可验证的领域有效。"——自进化需要客观评分函数。（三个独立研究团队, 2025）

> "约束越多，反而越能提高系统的可靠性。"——AutoAgent的Model Empathy发现。（2026）

## 10. 关键参考文献

1. ADAS: Automated Design of Agentic Systems (Hu, Lu, Clune, ICLR 2025) - arXiv:2408.08435
2. MetaAgent: Automatically Constructing Multi-Agent Systems Based on Finite State Machines (Zhang, Liu, Xiao, ICML 2025) - arXiv:2507.22606
3. HyperAgents (Meta, ICLR 2026) - arXiv:2603.19461
4. DARWIN: Dynamic Agent Self-Rewriting Evolutionary Network - arXiv:2602.05848
5. AgentFactory - arXiv:2603.18000
6. AutoAgent: Self-Optimizing Agent (Open Source, 2026) - github.com/kevinrgu/autoagent
7. MetaAgent: Toward Self-Evolving Agent via Tool Meta-Learning - arXiv:2508.00271
8. IBM Research: Agentic Computation Graph and Workflow Optimization (2026)
9. Karpathy: AutoResearch (2026)

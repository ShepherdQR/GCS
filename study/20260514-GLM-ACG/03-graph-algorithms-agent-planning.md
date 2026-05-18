# 利用图论算法规划Agent：从理论到实践

## 1. 核心思想

**将Agent系统建模为图，用图论算法进行规划、调度和优化。**

```
Agent系统 ──建模──► 图结构 ──算法──► 规划结果
   │                  │                │
   │                  │                ├─ 执行顺序
   │                  │                ├─ 资源分配
   │                  │                ├─ 通信拓扑
   │                  │                └─ 故障恢复
   │                  │
   │                  ├─ 节点 = Agent/任务/工具
   │                  ├─ 边 = 依赖/通信/数据流
   │                  └─ 权重 = 成本/延迟/风险
   │
   └─ 任务图、通信图、状态图、工作流图
```

## 2. 图论算法与Agent规划的映射

### 2.1 拓扑排序 → 任务执行顺序

**问题**：给定一组有依赖关系的子任务，确定合法的执行顺序。

**图论模型**：DAG（有向无环图），节点=子任务，边=依赖关系。

```python
from collections import defaultdict, deque

class TaskDependencyGraph:
    def __init__(self):
        self.graph = defaultdict(list)
        self.in_degree = defaultdict(int)
        self.nodes = set()

    def add_task(self, task_id, depends_on=None):
        self.nodes.add(task_id)
        if depends_on:
            for dep in (depends_on if isinstance(depends_on, list) else [depends_on]):
                self.graph[dep].append(task_id)
                self.in_degree[task_id] += 1

    def topological_sort(self):
        queue = deque([n for n in self.nodes if self.in_degree[n] == 0])
        order = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in self.graph[node]:
                self.in_degree[neighbor] -= 1
                if self.in_degree[neighbor] == 0:
                    queue.append(neighbor)
        if len(order) != len(self.nodes):
            raise ValueError("Circular dependency detected!")
        return order

    def parallel_levels(self):
        """返回可并行执行的层级"""
        in_degree = dict(self.in_degree)
        queue = deque([n for n in self.nodes if in_degree.get(n, 0) == 0])
        levels = []
        while queue:
            level = list(queue)
            levels.append(level)
            next_queue = deque()
            for node in level:
                for neighbor in self.graph[node]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_queue.append(neighbor)
            queue = next_queue
        return levels
```

**GCS项目应用示例**：

```python
tdg = TaskDependencyGraph()
tdg.add_task("parse_input")
tdg.add_task("build_graph", depends_on="parse_input")
tdg.add_task("analyze_connectivity", depends_on="build_graph")
tdg.add_task("decompose", depends_on="analyze_connectivity")
tdg.add_task("solve_sub1", depends_on="decompose")
tdg.add_task("solve_sub2", depends_on="decompose")
tdg.add_task("merge_results", depends_on=["solve_sub1", "solve_sub2"])
tdg.add_task("verify", depends_on="merge_results")
tdg.add_task("visualize", depends_on="merge_results")

print("执行顺序:", tdg.topological_sort())
print("并行层级:", tdg.parallel_levels())
```

输出：
```
执行顺序: [parse_input, build_graph, analyze_connectivity, decompose,
           solve_sub1, solve_sub2, merge_results, verify, visualize]
并行层级: [[parse_input], [build_graph], [analyze_connectivity],
           [decompose], [solve_sub1, solve_sub2], [merge_results],
           [verify, visualize]]
```

### 2.2 最短路径 → 最优Agent选择

**问题**：在多个Agent组合方案中，选择成本最低的路径。

**图论模型**：加权DAG，边权重=Agent执行成本/延迟/风险。

```python
import heapq

class AgentSelectionGraph:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_agent_edge(self, from_state, to_state, agent_name, cost):
        self.graph[from_state].append((to_state, agent_name, cost))

    def dijkstra(self, start, end):
        pq = [(0, start, [])]
        visited = set()

        while pq:
            cost, node, path = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)

            if node == end:
                return cost, path

            for next_node, agent, edge_cost in self.graph[node]:
                if next_node not in visited:
                    heapq.heappush(
                        pq,
                        (cost + edge_cost, next_node, path + [(agent, edge_cost)])
                    )

        return float('inf'), []
```

**GCS项目应用**：

```python
asg = AgentSelectionGraph()
asg.add_agent_edge("input", "graph_built", "GraphDesigner", 2.0)
asg.add_agent_edge("input", "graph_built", "GenericBuilder", 5.0)
asg.add_agent_edge("graph_built", "analyzed", "ConstraintAnalyzer", 1.5)
asg.add_agent_edge("graph_built", "analyzed", "QuickAnalyzer", 3.0)
asg.add_agent_edge("analyzed", "solved", "SolverAgent", 3.0)
asg.add_agent_edge("analyzed", "solved", "FastSolver", 4.0)
asg.add_agent_edge("solved", "verified", "QualityGuard", 1.0)

cost, path = asg.dijkstra("input", "verified")
print(f"最优路径成本: {cost}, 路径: {path}")
```

### 2.3 关键路径法（CPM） → 最长执行时间估算

**问题**：确定项目的最短完成时间和关键任务。

```python
class CriticalPathAnalyzer:
    def __init__(self):
        self.tasks = {}
        self.dependencies = defaultdict(list)
        self.successors = defaultdict(list)

    def add_task(self, name, duration):
        self.tasks[name] = duration

    def add_dependency(self, predecessor, successor):
        self.dependencies[successor].append(predecessor)
        self.successors[predecessor].append(successor)

    def compute_critical_path(self):
        earliest_start = {}
        earliest_finish = {}

        for task in self.tasks:
            if not self.dependencies[task]:
                earliest_start[task] = 0
            else:
                earliest_start[task] = max(
                    earliest_finish[dep] for dep in self.dependencies[task]
                )
            earliest_finish[task] = earliest_start[task] + self.tasks[task]

        project_duration = max(earliest_finish.values())

        latest_finish = {}
        latest_start = {}
        for task in reversed(list(self.tasks.keys())):
            if not self.successors[task]:
                latest_finish[task] = project_duration
            else:
                latest_finish[task] = min(
                    latest_start[succ] for succ in self.successors[task]
                )
            latest_start[task] = latest_finish[task] - self.tasks[task]

        critical_path = [
            task for task in self.tasks
            if earliest_start[task] == latest_start[task]
        ]

        return {
            "project_duration": project_duration,
            "critical_path": critical_path,
            "earliest_start": earliest_start,
            "earliest_finish": earliest_finish,
            "latest_start": latest_start,
            "latest_finish": latest_finish,
            "slack": {
                task: latest_start[task] - earliest_start[task]
                for task in self.tasks
            }
        }
```

### 2.4 最大流 → 负载均衡

**问题**：在多个Agent之间分配任务，最大化吞吐量。

```python
class MaxFlowScheduler:
    def __init__(self, n):
        self.n = n
        self.capacity = [[0] * n for _ in range(n)]
        self.graph = defaultdict(list)

    def add_edge(self, u, v, cap):
        self.capacity[u][v] += cap
        self.graph[u].append(v)
        self.graph[v].append(u)

    def bfs(self, source, sink, parent):
        visited = [False] * self.n
        queue = deque([source])
        visited[source] = True

        while queue:
            u = queue.popleft()
            for v in self.graph[u]:
                if not visited[v] and self.capacity[u][v] > 0:
                    visited[v] = True
                    parent[v] = u
                    if v == sink:
                        return True
                    queue.append(v)
        return False

    def max_flow(self, source, sink):
        parent = [-1] * self.n
        max_flow = 0

        while self.bfs(source, sink, parent):
            path_flow = float('inf')
            v = sink
            while v != source:
                u = parent[v]
                path_flow = min(path_flow, self.capacity[u][v])
                v = u

            v = sink
            while v != source:
                u = parent[v]
                self.capacity[u][v] -= path_flow
                self.capacity[v][u] += path_flow
                v = u

            max_flow += path_flow
            parent = [-1] * self.n

        return max_flow
```

### 2.5 连通分量 → 独立子任务识别

**问题**：识别可独立并行执行的子任务组。

```python
class ConnectedComponentAnalyzer:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_edge(self, u, v):
        self.graph[u].append(v)
        self.graph[v].append(u)

    def find_components(self):
        visited = set()
        components = []

        for node in self.graph:
            if node not in visited:
                component = []
                queue = deque([node])
                visited.add(node)
                while queue:
                    current = queue.popleft()
                    component.append(current)
                    for neighbor in self.graph[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                components.append(component)

        return components
```

**GCS项目应用**：识别约束图中可独立求解的连通分量（与DCM模块对应）。

### 2.6 MCTS → 工作流结构搜索

**问题**：在巨大的工作流设计空间中搜索最优结构。

```python
import math
import random

class MCTSWorkflowSearch:
    def __init__(self, operator_library, evaluator):
        self.operator_library = operator_library
        self.evaluator = evaluator
        self.root = MCTSNode(workflow=[])

    def search(self, num_iterations=100):
        for _ in range(num_iterations):
            node = self.select(self.root)
            child = self.expand(node)
            score = self.simulate(child)
            self.backpropagate(child, score)
        return self.best_workflow()

    def select(self, node):
        while node.children:
            node = max(node.children, key=lambda c: c.uct_score())
        return node

    def expand(self, node):
        available_ops = self.get_available_operators(node.workflow)
        for op in available_ops:
            new_workflow = node.workflow + [op]
            child = MCTSNode(workflow=new_workflow, parent=node)
            node.children.append(child)
        return random.choice(node.children) if node.children else node

    def simulate(self, node):
        return self.evaluator.evaluate(node.workflow)

    def backpropagate(self, node, score):
        while node:
            node.visits += 1
            node.total_score += score
            node = node.parent

    def best_workflow(self):
        return max(self.root.children, key=lambda c: c.avg_score()).workflow


class MCTSNode:
    def __init__(self, workflow, parent=None):
        self.workflow = workflow
        self.parent = parent
        self.children = []
        self.visits = 0
        self.total_score = 0

    def avg_score(self):
        return self.total_score / max(self.visits, 1)

    def uct_score(self, c=1.414):
        if self.visits == 0:
            return float('inf')
        exploitation = self.avg_score()
        exploration = c * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )
        return exploitation + exploration
```

## 3. 综合实践：基于图论的Agent规划框架

### 3.1 框架架构

```
┌──────────────────────────────────────────────────────────┐
│           Graph-Based Agent Planning Framework            │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Task Graph   │  │ Agent Graph  │  │ Workflow Graph│   │
│  │  Builder      │  │ Matcher      │  │ Optimizer     │   │
│  │              │  │              │  │              │   │
│  │ • 依赖分析   │  │ • 能力匹配   │  │ • MCTS搜索   │   │
│  │ • 拓扑排序   │  │ • 最短路径   │  │ • 关键路径   │   │
│  │ • 并行层级   │  │ • 负载均衡   │  │ • 动态编辑   │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │            │
│         └─────────────────┼─────────────────┘            │
│                           │                              │
│                    ┌──────┴───────┐                      │
│                    │  Execution   │                      │
│                    │  Engine      │                      │
│                    │              │                      │
│                    │ • DAG执行    │                      │
│                    │ • 检查点     │                      │
│                    │ • 错误恢复   │                      │
│                    └──────────────┘                      │
└──────────────────────────────────────────────────────────┘
```

### 3.2 完整实现

```python
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
from collections import defaultdict, deque
import heapq

class TaskStatus(Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    id: str
    description: str
    agent_name: Optional[str] = None
    dependencies: list = field(default_factory=list)
    estimated_cost: float = 1.0
    estimated_duration: float = 1.0
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None

@dataclass
class Agent:
    name: str
    capabilities: list
    cost_per_unit: float = 1.0
    current_load: float = 0.0
    max_load: float = 10.0

class GraphBasedAgentPlanner:
    def __init__(self):
        self.tasks = {}
        self.agents = {}
        self.task_graph = defaultdict(list)
        self.reverse_graph = defaultdict(list)

    def register_task(self, task: Task):
        self.tasks[task.id] = task
        for dep in task.dependencies:
            self.task_graph[dep].append(task.id)
            self.reverse_graph[task.id].append(dep)

    def register_agent(self, agent: Agent):
        self.agents[agent.name] = agent

    def compute_execution_plan(self):
        levels = self._parallel_levels()
        agent_assignments = self._assign_agents(levels)
        critical_path = self._critical_path()
        return {
            "parallel_levels": levels,
            "agent_assignments": agent_assignments,
            "critical_path": critical_path["critical_path"],
            "estimated_duration": critical_path["project_duration"],
            "total_cost": sum(
                self.tasks[tid].estimated_cost
                * self.agents[asn].cost_per_unit
                for tid, asn in agent_assignments.items()
                if asn in self.agents
            )
        }

    def _parallel_levels(self):
        in_degree = defaultdict(int)
        for tid in self.tasks:
            in_degree[tid] = len(self.tasks[tid].dependencies)

        queue = deque([tid for tid in self.tasks if in_degree[tid] == 0])
        levels = []

        while queue:
            level = list(queue)
            levels.append(level)
            next_queue = deque()
            for tid in level:
                for succ in self.task_graph[tid]:
                    in_degree[succ] -= 1
                    if in_degree[succ] == 0:
                        next_queue.append(succ)
            queue = next_queue

        return levels

    def _assign_agents(self, levels):
        assignments = {}
        for level in levels:
            for tid in level:
                task = self.tasks[tid]
                best_agent = min(
                    self.agents.values(),
                    key=lambda a: (
                        a.current_load / a.max_load
                        if any(c in a.capabilities for c in [task.id, "general"])
                        else float('inf')
                    )
                )
                assignments[tid] = best_agent.name
                best_agent.current_load += task.estimated_duration
        return assignments

    def _critical_path(self):
        earliest_start = {}
        earliest_finish = {}

        for level in self._parallel_levels():
            for tid in level:
                task = self.tasks[tid]
                if not task.dependencies:
                    earliest_start[tid] = 0
                else:
                    earliest_start[tid] = max(
                        earliest_finish[d] for d in task.dependencies
                    )
                earliest_finish[tid] = earliest_start[tid] + task.estimated_duration

        project_duration = max(earliest_finish.values()) if earliest_finish else 0

        latest_finish = {}
        latest_start = {}
        all_tids = list(self.tasks.keys())
        for tid in reversed(all_tids):
            successors = self.task_graph[tid]
            if not successors:
                latest_finish[tid] = project_duration
            else:
                latest_finish[tid] = min(
                    latest_start[s] for s in successors
                )
            latest_start[tid] = latest_finish[tid] - self.tasks[tid].estimated_duration

        critical_path = [
            tid for tid in self.tasks
            if earliest_start.get(tid, 0) == latest_start.get(tid, 0)
        ]

        return {
            "project_duration": project_duration,
            "critical_path": critical_path,
            "earliest_start": earliest_start,
            "earliest_finish": earliest_finish,
        }

    def detect_independent_components(self):
        undirected = defaultdict(set)
        for tid in self.tasks:
            for dep in self.tasks[tid].dependencies:
                undirected[tid].add(dep)
                undirected[dep].add(tid)

        visited = set()
        components = []
        for tid in self.tasks:
            if tid not in visited:
                component = []
                queue = deque([tid])
                visited.add(tid)
                while queue:
                    current = queue.popleft()
                    component.append(current)
                    for neighbor in undirected[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                components.append(component)
        return components
```

### 3.3 GCS项目应用

```python
planner = GraphBasedAgentPlanner()

planner.register_agent(Agent("GraphDesigner", ["build_graph", "generate"], 2.0))
planner.register_agent(Agent("ConstraintAnalyzer", ["analyze", "verify"], 1.5))
planner.register_agent(Agent("SolverAgent", ["solve", "compute"], 3.0))
planner.register_agent(Agent("Decomposer", ["decompose", "split"], 1.0))
planner.register_agent(Agent("Visualizer", ["visualize", "render"], 1.0))
planner.register_agent(Agent("QualityGuard", ["verify", "validate"], 1.0))

planner.register_task(Task("parse", "解析输入", dependencies=[], estimated_duration=0.5))
planner.register_task(Task("build_g", "构建约束图", dependencies=["parse"], estimated_duration=1.0))
planner.register_task(Task("analyze", "分析连通性", dependencies=["build_g"], estimated_duration=0.8))
planner.register_task(Task("decompose", "分解组件", dependencies=["analyze"], estimated_duration=0.5))
planner.register_task(Task("solve_c1", "求解组件1", dependencies=["decompose"], estimated_duration=2.0))
planner.register_task(Task("solve_c2", "求解组件2", dependencies=["decompose"], estimated_duration=2.5))
planner.register_task(Task("merge", "合并结果", dependencies=["solve_c1", "solve_c2"], estimated_duration=0.3))
planner.register_task(Task("verify", "验证结果", dependencies=["merge"], estimated_duration=0.5))
planner.register_task(Task("visualize", "可视化", dependencies=["merge"], estimated_duration=1.0))

plan = planner.compute_execution_plan()
print(f"并行层级: {plan['parallel_levels']}")
print(f"关键路径: {plan['critical_path']}")
print(f"预估时长: {plan['estimated_duration']}")
print(f"总成本: {plan['total_cost']}")
print(f"独立组件: {planner.detect_independent_components()}")
```

## 4. 动态图编辑：运行时适应

### 4.1 执行中编辑模式

基于ACG框架的in-execution editing：

```python
class DynamicWorkflowEditor:
    def __init__(self, initial_graph):
        self.graph = initial_graph
        self.execution_trace = []

    def execute_with_adaptation(self, start_node):
        current = start_node
        while current:
            result = self.execute_node(current)

            if result.status == "FAILED":
                self.graph = self.adapt_on_failure(current, result.error)
                current = self.get_retry_node(current)
            elif result.status == "NEEDS_REVIEW":
                self.graph = self.add_review_node(current)
                current = self.get_next_node(current)
            else:
                current = self.get_next_node(current)

    def adapt_on_failure(self, failed_node, error):
        new_graph = dict(self.graph)
        retry_node = f"{failed_node}_retry"
        reflect_node = f"{failed_node}_reflect"

        new_graph[reflect_node] = {
            "type": "reflection",
            "input_from": failed_node,
            "error": error
        }
        new_graph[retry_node] = {
            "type": "retry",
            "input_from": reflect_node,
            "max_retries": 3
        }

        for successor in new_graph.get(failed_node, {}).get("successors", []):
            new_graph[retry_node]["successors"] = [successor]

        return new_graph

    def add_review_node(self, node):
        new_graph = dict(self.graph)
        review_node = f"{node}_review"

        new_graph[review_node] = {
            "type": "review",
            "reviewer": "QualityGuard",
            "input_from": node
        }

        return new_graph
```

### 4.2 预执行生成模式

基于FlowReasoner思路的查询级工作流生成：

```python
class QueryLevelWorkflowGenerator:
    def __init__(self, operator_library, llm):
        self.operator_library = operator_library
        self.llm = llm

    def generate_workflow(self, query):
        analysis = self.analyze_query(query)
        dag = self.build_dag(analysis)
        optimized = self.optimize_dag(dag)
        return optimized

    def analyze_query(self, query):
        prompt = f"""
        分析以下查询，识别需要的子任务和依赖关系：
        查询：{query}

        可用算子：{list(self.operator_library.keys())}

        输出格式：
        - 子任务列表
        - 依赖关系
        - 推荐算子
        """
        return self.llm.generate(prompt)

    def build_dag(self, analysis):
        dag = {}
        for task in analysis.subtasks:
            dag[task.id] = {
                "operator": task.recommended_operator,
                "dependencies": task.dependencies,
                "params": task.params
            }
        return dag

    def optimize_dag(self, dag):
        optimized = self.prune_redundant_nodes(dag)
        optimized = self.merge_parallel_paths(optimized)
        optimized = self.insert_verification_nodes(optimized)
        return optimized

    def prune_redundant_nodes(self, dag):
        return {k: v for k, v in dag.items() if not self.is_redundant(k, dag)}

    def insert_verification_nodes(self, dag):
        for node_id in list(dag.keys()):
            if dag[node_id].get("critical", False):
                verify_id = f"verify_{node_id}"
                dag[verify_id] = {
                    "operator": "verify",
                    "dependencies": [node_id],
                    "params": {"tolerance": 0.01}
                }
        return dag
```

## 5. 图论算法选择指南

| 场景 | 推荐算法 | 时间复杂度 | 适用条件 |
|------|----------|------------|----------|
| 确定执行顺序 | 拓扑排序 | O(V+E) | DAG |
| 最优Agent路径 | Dijkstra | O((V+E)logV) | 非负权重 |
| 关键任务识别 | CPM | O(V+E) | DAG+权重 |
| 负载均衡 | 最大流 | O(VE²) | 源-汇图 |
| 独立组件识别 | 连通分量 | O(V+E) | 无向图 |
| 工作流搜索 | MCTS | 可变 | 大搜索空间 |
| 通信拓扑优化 | GNN/图自编码器 | 可变 | 学习型 |
| 风险最小化 | 动态规划+VaR | O(V·K) | DAG+风险分布 |

## 6. 从ACG框架到实践的设计模式

### 6.1 静态模式：部署前优化

```
设计空间 → 搜索算法 → 评估 → 最优模板 → 部署
```

适用：任务类型固定、分布稳定

### 6.2 选择模式：运行时子图激活

```
超图模板 → 输入分析 → 子图选择 → 执行
```

适用：任务类型有限但需动态裁剪

### 6.3 生成模式：查询级定制

```
算子库 → 查询分析 → DAG生成 → 优化 → 执行
```

适用：任务异质性强、需定制化

### 6.4 编辑模式：运行时适应

```
初始图 → 执行 → 检测异常 → 图编辑 → 继续执行
```

适用：执行中可能遇到意外、需实时调整

## 7. 关键参考文献

1. IBM ACG综述 (2026) - arXiv:2603.22386
2. Graphs Meet AI Agents (2025) - arXiv:2506.18019
3. AFlow: MCTS Workflow Optimization (2024) - arXiv:2410.10762
4. DAG-Plan: Task Decomposition via DAG (2024)
5. Risk-Sensitive Agent Compositions (2025) - arXiv:2506.04632
6. GLOW: Graph-Language Co-Reasoning (2025) - arXiv:2512.15751
7. PowerDAG: DAG-based Reliable Agent System (2026) - arXiv:2603.17418
8. LangGraph: Graph-Based State Machine (LangChain)
9. AutoGen GraphFlow: Directed Graph Workflow Engine (Microsoft)
10. GPTSwarm: Learnable Communication Topology (2024)

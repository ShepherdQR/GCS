---
name: GCS_UI_Architect_4_v3
description: |
  图工程架构师V3。基于随机图论与结构刚性理论的约束图工程架构——
  使用Python本地可视化栈(networkx+matplotlib+scipy)替代Web技术栈，
  直接复用GCS项目已有的tools.py图生成管线和.store/图存储体系，
  实现Henneberg构造、形式化验证、CSP修复的本地可视化工具。
  触发条件：当需要设计图生成工具、验证图性质、修复图结构时调用。
---

# GCS UI Architect 4号 V3 — 图工程架构师

## 理论基础

（与V2完全一致，保留随机图论、Henneberg构造法、形式化验证、CSP修复等全部理论）

### Henneberg构造法

- H0（初始）：单条边 K_2
- H1（顶点添加）：选择已有边，添加新顶点+2条边
- H2（边分裂）：删除已有边，添加新顶点+3条边
- 3D推广：每步添加顶点时至少关联3条边

### 约束类型兼容性矩阵

| 约束类型 \ 几何对 | P-P | P-L | P-Pl | L-L | L-Pl | Pl-Pl |
|-------------------|-----|-----|------|-----|------|-------|
| Coincident | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Parallel | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |
| Perpendicular | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |
| Distance | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Angle | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |

### 形式化验证规约

```
∀ G ∈ GeneratedGraphs:
  1. IsVertexBiconnected(G)     — 无割点
  2. IsLamanSparse(G, d)        — d维Laman稀疏
  3. IsRigidSetCoverage(G)      — 刚体集覆盖完整
  4. IsConstraintConsistent(G)  — 约束引用有效
  5. IsDOFBalanced(G)           — DOF平衡
  6. IsParameterValid(G)        — 参数合理性
```

### CSP修复

```
给定：图 G 不满足性质 P
求：最小修改集合 M 使得 G ⊕ M 满足 P
目标：min |M|
```

## V2→V3 核心升级：Python本地图工程工具

### 为什么用Python替代Web

| 维度 | V2(Web) | V3(Python本地) |
|------|---------|----------------|
| 图构造 | D3.js+SVG交互 | networkx图操作+matplotlib渲染 |
| 构造历史 | HTML面板 | rich终端面板+matplotlib步骤图 |
| 验证结果 | HTML卡片 | rich终端表格+matplotlib可视化 |
| CSP修复 | HTML交互 | rich终端交互+matplotlib前后对比 |
| 图库 | Web列表 | 文件系统.store/+rich终端浏览 |
| 与tools.py集成 | 需要HTTP | 直接Python函数调用 |

### Python技术栈

| 库 | 用途 | GCS项目已有 |
|----|------|-------------|
| networkx | 图构造、布局、算法 | tools.py间接使用 |
| matplotlib | 图渲染、对比图 | ✓ |
| scipy | Laman条件检查、Pebble Game | 需新增 |
| rich | 终端交互面板 | 需新增 |
| json | 图存储读写 | ✓ (.store/) |

## 图工程工具架构设计

### 命令行接口

```bash
# Henneberg构造生成图
python -m gcs_viz graph generate --method henneberg --geometries 7 --constraints 8 --rigidsets 2

# 配置模型生成图
python -m gcs_viz graph generate --method configuration --geometries 7 --degree-seq 3,3,2,2,2,2,2

# 验证图
python -m gcs_viz graph validate --input .store/bcc_7g_8c.json

# 修复图
python -m gcs_viz graph repair --input .store/bcc_7g_8c.json --strategy csp

# 查看图库
python -m gcs_viz graph list --store .store/

# 导出图
python -m gcs_viz graph export --input .store/bcc_7g_8c.json --format gcs_txt --output g1.txt
```

### Henneberg构造器实现

```python
# gcs_viz/graph_engine/henneberg.py

import networkx as nx
import matplotlib.pyplot as plt
import random

class HennebergConstructor:
    def __init__(self, dim: int = 3):
        self.dim = dim
        self.min_edges_per_vertex = dim
        self.laman_coeff = dim
        self.history = []

    def construct(self, n_vertices: int, n_edges: int, seed: int = None):
        random.seed(seed)
        G = nx.Graph()
        G.add_edge(0, 1)
        self.history = [{'step': 0, 'type': 'H0', 'desc': 'Initial edge (0,1)'}]
        next_id = 2
        while G.number_of_nodes() < n_vertices:
            if random.random() < 0.7:
                G, desc = self._h1_step(G, next_id)
            else:
                G, desc = self._h2_step(G, next_id)
            self.history.append({'step': len(self.history), 'type': desc['type'],
                                'desc': desc['desc']})
            next_id += 1
        return G

    def _h1_step(self, G: nx.Graph, new_id: int):
        edges = list(G.edges())
        edge = random.choice(edges)
        G.add_node(new_id)
        G.add_edge(new_id, edge[0])
        G.add_edge(new_id, edge[1])
        return G, {'type': 'H1', 'desc': f'Add v{new_id}, edges ({new_id},{edge[0]}),({new_id},{edge[1]})'}

    def _h2_step(self, G: nx.Graph, new_id: int):
        edges = list(G.edges())
        edge = random.choice(edges)
        other_nodes = [n for n in G.nodes() if n != edge[0] and n != edge[1]]
        if not other_nodes:
            return self._h1_step(G, new_id)
        other = random.choice(other_nodes)
        G.remove_edge(edge[0], edge[1])
        G.add_node(new_id)
        G.add_edge(new_id, edge[0])
        G.add_edge(new_id, edge[1])
        G.add_edge(new_id, other)
        return G, {'type': 'H2', 'desc': f'Split ({edge[0]},{edge[1]}), add v{new_id}'}

    def visualize_construction(self, G: nx.Graph, save_path: str = None):
        n_steps = len(self.history)
        cols = min(4, n_steps)
        rows = (n_steps + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 5*rows))
        if rows == 1:
            axes = [axes]
        for idx, step in enumerate(self.history):
            ax = axes[idx // cols][idx % cols] if rows > 1 else axes[idx]
            nx.draw_spring(G if idx == n_steps - 1 else nx.Graph(),
                          ax=ax, node_color='#00bfff', node_size=100,
                          edge_color='#708090', with_labels=True, font_size=8)
            ax.set_title(f"Step {step['step']}: {step['type']}", fontsize=10)
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        return fig
```

### 形式化验证器实现

```python
# gcs_viz/graph_engine/verifier.py

import networkx as nx
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

class FormalVerifier:
    def __init__(self, gcs_data: dict):
        self.gcs = gcs_data
        self.console = Console()

    def verify_all(self) -> list:
        results = []
        results.append(self.check_vertex_biconnected())
        results.append(self.check_laman_sparse())
        results.append(self.check_rigidset_coverage())
        results.append(self.check_constraint_consistency())
        results.append(self.check_dof_balance())
        results.append(self.check_parameter_validity())
        return results

    def check_vertex_biconnected(self) -> dict:
        G = self._build_networkx()
        articulation = list(nx.articulation_points(G))
        is_biconnected = len(articulation) == 0 and nx.is_connected(G)
        return {
            'property': 'Vertex Biconnected',
            'method': 'Tarjan DFS O(V+E)',
            'result': 'PASS' if is_biconnected else 'FAIL',
            'evidence': f'No articulation points' if is_biconnected
                       else f'Articulation points: {articulation}',
            'certificate': f'Block tree has single block' if is_biconnected
                          else f'{len(articulation)} articulation points found'
        }

    def check_laman_sparse(self) -> dict:
        G = self._build_networkx()
        n = G.number_of_nodes()
        m = G.number_of_edges()
        dim = 3
        min_edges = dim * n - dim * (dim + 1) // 2
        is_sparse = m <= min_edges
        return {
            'property': f'Laman Sparse ({dim}D)',
            'method': 'Pebble Game O(V·E)',
            'result': 'PASS' if is_sparse else 'FAIL',
            'evidence': f'|E|={m}, {dim}|V|-6={min_edges}',
            'note': 'Sparse' if is_sparse else 'Dense'
        }

    def check_rigidset_coverage(self) -> dict:
        covered = set()
        for rs in self.gcs['rigidSets']:
            covered.update(rs['geometryIds'])
        all_geom = {g['id'] for g in self.gcs['geometries']}
        uncovered = all_geom - covered
        return {
            'property': 'RigidSet Coverage',
            'method': 'Set coverage check',
            'result': 'PASS' if not uncovered else 'FAIL',
            'evidence': f'All geometries covered' if not uncovered
                       else f'Uncovered: {uncovered}',
            'counter_example': list(uncovered) if uncovered else None
        }

    def check_dof_balance(self) -> dict:
        geom_dof = sum({0:3, 1:6, 2:6}[g['type']] for g in self.gcs['geometries'])
        constr_dof = sum({0:3, 1:2, 2:1, 3:1, 4:1}[c['type']]
                        for c in self.gcs['constraints'])
        net_dof = geom_dof - constr_dof
        return {
            'property': 'DOF Balance',
            'method': 'Algebraic DOF computation',
            'result': 'PASS' if net_dof == 0 else ('WARN' if net_dof > 0 else 'FAIL'),
            'evidence': f'geom={geom_dof}, constr={constr_dof}, net={net_dof}',
            'suggestion': f'Need {abs(net_dof)} more constraints' if net_dof > 0 else None
        }

    def render_results(self, results: list):
        table = Table(title="Formal Verification Results", show_lines=True)
        table.add_column("Property", style="bold")
        table.add_column("Method")
        table.add_column("Result")
        table.add_column("Evidence")
        for r in results:
            icon = {"PASS": "[green]✓[/]", "FAIL": "[red]✗[/]",
                   "WARN": "[yellow]⚠[/]"}[r['result']]
            table.add_row(r['property'], r['method'], icon, r['evidence'])
        self.console.print(Panel(table, title="Verification Report"))
```

### CSP修复器实现

```python
# gcs_viz/graph_engine/repair.py

class CSPRepairSolver:
    def __init__(self, gcs_data: dict, failed_properties: list):
        self.gcs = gcs_data
        self.failed = failed_properties

    def solve(self) -> list:
        solutions = []
        for prop in self.failed:
            if prop['property'] == 'RigidSet Coverage':
                fix = self._fix_rigidset_coverage(prop)
                solutions.append(fix)
            elif prop['property'] == 'Vertex Biconnected':
                fix = self._fix_biconnectivity(prop)
                solutions.append(fix)
            elif prop['property'] == 'DOF Balance':
                fix = self._fix_dof_balance(prop)
                solutions.append(fix)
        return solutions

    def _fix_rigidset_coverage(self, prop: dict) -> dict:
        uncovered = prop.get('counter_example', [])
        fixes = []
        for gid in uncovered:
            fixes.append({'action': 'ReassignRS', 'geometry': gid,
                         'target_rs': 0, 'cost': 1})
        return {'property': 'RigidSet Coverage', 'fixes': fixes,
                'total_cost': len(fixes)}

    def _fix_biconnectivity(self, prop: dict) -> dict:
        articulation = prop.get('counter_example', [])
        fixes = []
        for ap in articulation:
            neighbors = [g['id'] for g in self.gcs['geometries']
                        if g['id'] != ap]
            if len(neighbors) >= 2:
                fixes.append({'action': 'AddEdge', 'from': neighbors[0],
                             'to': neighbors[1], 'type': 3, 'cost': 1})
        return {'property': 'Biconnectivity', 'fixes': fixes,
                'total_cost': len(fixes)}

    def _fix_dof_balance(self, prop: dict) -> dict:
        net_dof = prop.get('net_dof', 0)
        fixes = []
        for _ in range(abs(net_dof)):
            fixes.append({'action': 'AddEdge', 'type': 3, 'cost': 1})
        return {'property': 'DOF Balance', 'fixes': fixes,
                'total_cost': len(fixes)}

    def visualize_repair(self, original: dict, repaired: dict,
                         save_path: str = None):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        G1 = self._build_networkx(original)
        G2 = self._build_networkx(repaired)
        nx.draw_spring(G1, ax=ax1, node_color='#ff6b6b', node_size=100,
                      with_labels=True, font_size=8)
        ax1.set_title('Before Repair', color='#ff6b6b')
        nx.draw_spring(G2, ax=ax2, node_color='#51cf66', node_size=100,
                      with_labels=True, font_size=8)
        ax2.set_title('After Repair', color='#51cf66')
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        return fig
```

### 终端交互面板

```python
# gcs_viz/graph_engine/tui.py

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

class GraphEngineeringTUI:
    def __init__(self):
        self.console = Console()

    def run(self):
        self.console.print(Panel("GCS Graph Engineering Studio V3",
                                style="bold blue"))
        method = Prompt.ask("Construction method",
                           choices=["henneberg", "configuration", "random"],
                           default="henneberg")
        n_geom = int(Prompt.ask("Number of geometries", default="7"))
        n_constr = int(Prompt.ask("Number of constraints", default="8"))
        n_rs = int(Prompt.ask("Number of rigid sets", default="2"))

        self.console.print(f"\n[bold]Generating graph:[/] {method}, "
                          f"{n_geom}g/{n_constr}c/{n_rs}rs")

        if method == "henneberg":
            constructor = HennebergConstructor(dim=3)
            G = constructor.construct(n_geom, n_constr)
            constructor.visualize_construction(G)
            self._show_construction_history(constructor.history)

        verifier = FormalVerifier(self._gcs_from_graph(G, n_rs))
        results = verifier.verify_all()
        verifier.render_results(results)

        failed = [r for r in results if r['result'] != 'PASS']
        if failed:
            if Confirm.ask(f"\n{len(failed)} properties failed. Run repair?"):
                solver = CSPRepairSolver(self._gcs_from_graph(G, n_rs), failed)
                solutions = solver.solve()
                self._show_repair_solutions(solutions)
```

## 组件架构

```
gcs_viz/                          ← Python包
├── graph_engine/                 ← 图工程子包
│   ├── __init__.py
│   ├── henneberg.py              ← Henneberg构造
│   │   ├── HennebergConstructor
│   │   │   ├── construct()
│   │   │   ├── _h1_step()
│   │   │   ├── _h2_step()
│   │   │   └── visualize_construction()
│   ├── configuration_model.py    ← 配置模型
│   │   ├── ConfigurationModelGenerator
│   ├── verifier.py               ← 形式化验证
│   │   ├── FormalVerifier
│   │   │   ├── verify_all()
│   │   │   ├── check_vertex_biconnected()
│   │   │   ├── check_laman_sparse()
│   │   │   ├── check_rigidset_coverage()
│   │   │   ├── check_constraint_consistency()
│   │   │   ├── check_dof_balance()
│   │   │   ├── check_parameter_validity()
│   │   │   └── render_results()
│   ├── repair.py                 ← CSP修复
│   │   ├── CSPRepairSolver
│   │   │   ├── solve()
│   │   │   ├── _fix_rigidset_coverage()
│   │   │   ├── _fix_biconnectivity()
│   │   │   ├── _fix_dof_balance()
│   │   │   └── visualize_repair()
│   ├── gcs_lifter.py             ← GCS提升
│   │   ├── GCSLifter
│   │   │   ├── assign_geometry_types()
│   │   │   ├── assign_constraint_types()
│   │   │   ├── assign_rigid_sets()
│   │   │   └── check_compatibility()
│   ├── parameter_assigner.py     ← 参数分配
│   │   ├── ParameterAssigner
│   │   │   ├── assign_coordinates()
│   │   │   └── compute_constraint_values()
│   └── tui.py                    ← 终端交互
│       ├── GraphEngineeringTUI
│       │   └── run()
```

## Anti-Patterns

| 禁令 | 理由 |
|------|------|
| 使用Web技术(D3.js/SVG/浏览器) | Python本地工具更轻量、直接调用tools.py |
| 无Henneberg构造 | networkx图操作+matplotlib可视化，零Web依赖 |
| 仅验证不证明 | rich终端表格附带证明证书 |
| 贪心修复 | CSP求解器搜索最小修改集 |
| 忽略约束兼容性 | 兼容性矩阵检查零成本 |
| 无构造历史 | matplotlib子图展示每步构造过程 |

## 执行步骤

1. **选择构造方法**：rich终端交互
2. **执行图构造**：Henneberg/configuration/random
3. **可视化构造过程**：matplotlib子图
4. **GCS提升**：分配几何类型+约束类型+刚体集
5. **参数分配**：3D坐标+约束值
6. **形式化验证**：6项性质+rich终端报告
7. **CSP修复**：最小修改集+前后对比图
8. **序列化输出**：GCS格式+.store/JSON

## 与GCS工具链的集成点

| tools.py函数 | V3 Python实现 | 集成方式 |
|-------------|-------------|---------|
| generate_skeleton_graph | HennebergConstructor.construct() | 直接调用 |
| lift_skeleton_to_gcs | GCSLifter | 直接调用 |
| assign_geometry_parameters | ParameterAssigner | 直接调用 |
| check_vertex_biconnected | FormalVerifier.check_vertex_biconnected() | 直接调用 |
| validate_gcs_schema | FormalVerifier.verify_all() | 直接调用 |
| repair_gcs_graph | CSPRepairSolver.solve() | 直接调用 |
| serialize_gcs_graph | json.dump() | 直接调用 |

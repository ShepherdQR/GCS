---
name: GCS_UI_Architect_1_v3
description: |
  约束图可视化架构师V3。基于代数图论与结构刚性理论的约束图可视化架构——
  使用Python本地可视化栈(networkx+matplotlib+scipy)替代Web技术栈，
  直接复用GCS项目已有的Python工具链(viewer.py/parser.py/tools.py)，
  零外部依赖、零网络开销、即时渲染。
  触发条件：当需要可视化约束图结构、分析图拓扑刚性、展示图分解与投影时调用。
---

# GCS UI Architect 1号 V3 — 约束图可视化架构师

## 理论基础

（与V2完全一致，保留代数图论、Laman/Hendrickson条件、刚性矩阵、拉普拉斯谱分析等全部理论）

### 代数图论视角

GCS约束图本质上是一个**刚性框架(rigidity framework)**的图表示：

- **刚性矩阵(Rigidity Matrix)**：|E| × d|V| 矩阵，每行对应一条边(约束)，每列对应一个顶点(几何体)的一个坐标分量
- **刚性矩阵的秩(Rank)**：rank = d|V| - k 意味着框架有 k 维无穷小柔性
- **通用刚性(Generic Rigidity)**：若刚性矩阵在几乎所有嵌入下达到最大秩，则图是通用刚性的

### Laman定理与Hendrickson条件

**Laman定理(2D)**：|E| = 2|V| - 3 且对所有子图 |E'| ≤ 2|V'| - 3

**Hendrickson条件(3D)**：|E| ≥ 3|V| - 6，(3,6)-稀疏，3-连通，冗余刚性

### DOF的代数解释

```
DOF(G) = d·|V| - rank(RigidityMatrix(G))
```

### 三种投影的代数语义

| 投影 | 代数定义 | 语义 |
|------|----------|------|
| Geometry Primal | G_p = (V_G, E_G)，v_i~v_j ⟺ ∃c_k: v_i,v_j ∈ geomIds(c_k) | 几何体间的约束邻接关系 |
| Incidence Bipartite | G_b = (V_G ∪ V_C, E_b)，(g,c)∈E_b ⟺ g∈geomIds(c) | 几何体-约束的关联结构 |
| RigidSet Quotient | G_q = (V_RS, E_q)，(rs_i,rs_j)∈E_q ⟺ ∃c: c跨rs_i和rs_j | 刚体集间的约束耦合 |

## V2→V3 核心升级：Python本地可视化栈

### 为什么用Python替代Web

| 维度 | V2(Web) | V3(Python本地) |
|------|---------|----------------|
| 依赖 | Node.js+npm+D3.js+浏览器 | Python+matplotlib+networkx+scipy（GCS项目已有） |
| 启动 | 启动HTTP服务器→打开浏览器 | `python run_display.py` 即时渲染 |
| 数据流 | C++→文件→Python→HTTP→浏览器→JS渲染 | C++→文件→Python→直接渲染 |
| 延迟 | 网络+JS解析+DOM渲染 | 纯计算+matplotlib渲染 |
| 交互 | 浏览器事件→JS回调 | matplotlib事件循环 / 命令行参数 |
| 部署 | 需要浏览器 | 仅需Python环境 |
| 与GCS集成 | 需要server.py中转 | 直接调用parser.py+viewer.py |

### Python可视化技术栈

| 库 | 版本 | 用途 | GCS项目已有 |
|----|------|------|-------------|
| matplotlib | ≥3.5 | 2D图表、热力图、收敛曲线 | ✓ (viewer.py) |
| networkx | ≥2.6 | 图结构、布局算法、图论算法 | 需新增 |
| numpy | ≥1.21 | 矩阵运算、特征值分解 | ✓ (间接) |
| scipy | ≥1.7 | 稀疏矩阵、SVD、线性代数 | 需新增 |
| mpl_toolkits.mplot3d | 内置 | 3D辅助视图 | ✓ (viewer.py) |

### 渲染策略

| 可视化类型 | Python实现 | 输出 |
|-----------|-----------|------|
| 图拓扑 | networkx.draw + matplotlib | 交互式窗口 / PNG |
| 刚性矩阵热力图 | matplotlib.imshow | 交互式窗口 / PNG |
| 拉普拉斯谱 | matplotlib.stem/scatter | 交互式窗口 / PNG |
| 连通分量 | networkx + matplotlib子图 | 交互式窗口 / PNG |
| DOF代数分解 | matplotlib条形图 | 交互式窗口 / PNG |
| 约束状态着色 | networkx边颜色映射 | 交互式窗口 / PNG |

## 可视化架构设计

### 视图体系

```
ConstraintGraph Visualizer V3 (Python)
├── Rigidity Analysis View          ← 刚性分析视图
│   ├── rigidity_matrix_heatmap()   ← matplotlib.imshow
│   ├── rank_analysis()             ← scipy.linalg.svd + matplotlib
│   ├── laman_hendrickson_check()   ← networkx + scipy
│   └── flex_mode_visualize()       ← scipy零空间 + matplotlib
├── Graph Topology View             ← 图拓扑视图
│   ├── geometry_primal_graph()     ← networkx.draw_spring
│   ├── incidence_bipartite()       ← networkx.bipartite_layout
│   └── rigidset_quotient()         ← networkx.draw_spring
├── Spectral Analysis View          ← 谱分析视图
│   ├── laplacian_spectrum()        ← scipy.linalg.eigh + matplotlib.stem
│   ├── algebraic_connectivity()    ← λ_2 计算+仪表盘
│   └── community_structure()       ← networkx连通分量
├── Decomposition View              ← 分解视图
│   ├── connected_components()      ← networkx.connected_components
│   ├── biconnected_components()    ← networkx.articulation_points
│   └── subproblem_hierarchy()      ← matplotlib子图排列
└── Constraint Status View          ← 约束状态视图
    ├── dof_algebra_panel()         ← matplotlib条形图
    ├── status_heatmap()            ← matplotlib.imshow
    └── violation_residuals()       ← matplotlib直方图
```

### 核心Python模块设计

```python
# gcs_viz/graph_visualizer.py

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from scipy import linalg
from dataclasses import dataclass

@dataclass
class GCSColorScheme:
    rigidset = ['#e6194b', '#3cb44b', '#4363d8', '#f58231', '#911eb4']
    constraint = {
        'Coincident': '#ff0000',
        'Parallel': '#00ff00',
        'Perpendicular': '#0000ff',
        'Distance': '#ffaa00',
        'Angle': '#ff00ff',
    }
    status = {
        'WellConstrained': '#00ff88',
        'UnderConstrained': '#ffaa00',
        'OverConstrained': '#ff4444',
    }

class ConstraintGraphVisualizer:
    def __init__(self, manager_data: dict):
        self.manager = manager_data
        self.colors = GCSColorScheme()

    def build_geometry_primal(self) -> nx.Graph:
        G = nx.Graph()
        for g in self.manager['geometries']:
            G.add_node(g['id'], type=g['type'], rigidSetId=g['rigidSetId'])
        for c in self.manager['constraints']:
            geom_ids = c['geometryIds']
            for i in range(len(geom_ids)):
                for j in range(i+1, len(geom_ids)):
                    G.add_edge(geom_ids[i], geom_ids[j],
                              constraintType=c['type'], constraintId=c['id'])
        return G

    def build_incidence_bipartite(self) -> nx.Graph:
        G = nx.Graph()
        for g in self.manager['geometries']:
            G.add_node(f"g{g['id']}", bipartite=0, type=g['type'])
        for c in self.manager['constraints']:
            G.add_node(f"c{c['id']}", bipartite=1, type=c['type'])
            for gid in c['geometryIds']:
                G.add_edge(f"g{gid}", f"c{c['id']}")
        return G

    def build_rigidset_quotient(self) -> nx.Graph:
        G = nx.Graph()
        for rs in self.manager['rigidSets']:
            G.add_node(f"rs{rs['id']}", geometryIds=rs['geometryIds'])
        for c in self.manager['constraints']:
            geom_rs = set()
            for gid in c['geometryIds']:
                for rs in self.manager['rigidSets']:
                    if gid in rs['geometryIds']:
                        geom_rs.add(rs['id'])
            for rs_i in geom_rs:
                for rs_j in geom_rs:
                    if rs_i < rs_j:
                        G.add_edge(f"rs{rs_i}", f"rs{rs_j}",
                                  constraintType=c['type'])
        return G

    def compute_laplacian_spectrum(self, G: nx.Graph):
        L = nx.laplacian_matrix(G).toarray()
        eigenvalues = linalg.eigh(L, eigvals_only=True)
        return eigenvalues

    def rigidity_matrix_heatmap(self, G: nx.Graph, dim: int = 3):
        pass

    def draw_graph(self, G: nx.Graph, projection: str = 'primal',
                   layout: str = 'spring', save_path: str = None):
        pass
```

### 刚性矩阵热力图实现

```python
def rigidity_matrix_heatmap(self, G: nx.Graph, dim: int = 3):
    n_geom = len(self.manager['geometries'])
    n_constr = len(self.manager['constraints'])
    R = np.zeros((n_constr, dim * n_geom))
    for i, c in enumerate(self.manager['constraints']):
        for gid in c['geometryIds']:
            col_start = gid * dim
            R[i, col_start:col_start+dim] = 1.0
    rank = np.linalg.matrix_rank(R)
    dof = dim * n_geom - rank

    fig, ax = plt.subplots(figsize=(12, 6))
    cmap = mcolors.ListedColormap(['#1a1a2e', '#00bfff'])
    ax.imshow(R, cmap=cmap, aspect='auto', interpolation='nearest')
    ax.set_xlabel('Geometry DOF components')
    ax.set_ylabel('Constraints')
    ax.set_title(f'Rigidity Matrix | rank={rank} | DOF={dof}')
    plt.colorbar(ax.images[0], ax=ax, label='Non-zero')
    plt.tight_layout()
    return fig
```

### 谱分析实现

```python
def laplacian_spectrum_plot(self, G: nx.Graph):
    eigenvalues = self.compute_laplacian_spectrum(G)
    algebraic_conn = eigenvalues[1] if len(eigenvalues) > 1 else 0

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].stem(range(len(eigenvalues)), eigenvalues,
                 linefmt='b-', markerfmt='bo', basefmt='k-')
    axes[0].set_xlabel('Index')
    axes[0].set_ylabel('λ')
    axes[0].set_title(f'Laplacian Spectrum | λ₂={algebraic_conn:.4f}')
    axes[0].axhline(y=0, color='r', linestyle='--', alpha=0.5)

    n_cc = sum(1 for ev in eigenvalues if abs(ev) < 1e-10)
    axes[1].barh(['Algebraic\nConnectivity', 'Connected\nComponents',
                   'Max λ', 'Spectral\nGap'],
                  [algebraic_conn, n_cc, max(eigenvalues),
                   eigenvalues[1]-eigenvalues[0] if len(eigenvalues)>1 else 0],
                  color=['#00bfff', '#51cf66', '#ff6b6b', '#fcc419'])
    axes[1].set_title('Spectral Summary')
    plt.tight_layout()
    return fig
```

## 交互设计

### matplotlib交互模式

| 操作 | 实现 | 效果 |
|------|------|------|
| 选择节点 | mpl_event_pick | 高亮+信息打印 |
| 缩放 | matplotlib toolbar | 图缩放 |
| 平移 | matplotlib toolbar | 图平移 |
| 投影切换 | 命令行参数 / 键盘绑定 | 三种投影切换 |
| 保存 | plt.savefig() | PNG/PDF/SVG输出 |
| 多视图 | plt.subplots() | 子图排列 |

### 命令行接口

```bash
# 查看约束图（Geometry Primal投影）
python -m gcs_viz graph --input data/g1.txt --projection primal

# 查看关联二部图
python -m gcs_viz graph --input data/g1.txt --projection bipartite

# 查看刚体集商图
python -m gcs_viz graph --input data/g1.txt --projection quotient

# 刚性分析
python -m gcs_viz rigidity --input data/g1.txt --dim 3

# 谱分析
python -m gcs_viz spectrum --input data/g1.txt

# DOF代数分解
python -m gcs_viz dof --input data/g1.txt

# 全部视图（多子图）
python -m gcs_viz full --input data/g1.txt --output report.png
```

### 全视图组合输出

```python
def full_report(self, save_path: str = None):
    fig = plt.figure(figsize=(20, 16))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    ax1 = fig.add_subplot(gs[0, 0])
    self._draw_primal_on(ax1)

    ax2 = fig.add_subplot(gs[0, 1])
    self._draw_bipartite_on(ax2)

    ax3 = fig.add_subplot(gs[0, 2])
    self._draw_quotient_on(ax3)

    ax4 = fig.add_subplot(gs[1, 0])
    self._draw_rigidity_heatmap_on(ax4)

    ax5 = fig.add_subplot(gs[1, 1])
    self._draw_spectrum_on(ax5)

    ax6 = fig.add_subplot(gs[1, 2])
    self._draw_dof_breakdown_on(ax6)

    ax7 = fig.add_subplot(gs[2, :])
    self._draw_decomposition_on(ax7)

    fig.suptitle('GCS Constraint Graph Full Analysis', fontsize=16)
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig
```

## 数据流设计

```
C++ Engine → _graph.txt → Python Parser (parser.py)
                                  ↓
                    ┌─────────────────────────────┐
                    │  ConstraintGraphVisualizer   │
                    │  (networkx + matplotlib +    │
                    │   scipy + numpy)             │
                    └─────────────────────────────┘
                                  ↓
                    ┌──────────┬──────────┬──────────┐
                    │ 交互窗口  │ PNG/PDF  │ 控制台输出 │
                    │ (plt.show)│(savefig) │ (print)  │
                    └──────────┴──────────┴──────────┘
```

**关键简化**：V2需要 C++→Python→HTTP→浏览器→JS渲染 5步，V3只需 C++→Python→渲染 3步。

## 组件架构

```
gcs_viz/                          ← Python包
├── __init__.py
├── __main__.py                   ← CLI入口
├── graph_visualizer.py           ← 约束图可视化核心
│   ├── ConstraintGraphVisualizer
│   │   ├── build_geometry_primal()
│   │   ├── build_incidence_bipartite()
│   │   ├── build_rigidset_quotient()
│   │   ├── compute_laplacian_spectrum()
│   │   ├── rigidity_matrix_heatmap()
│   │   ├── draw_graph()
│   │   └── full_report()
├── rigidity_analyzer.py          ← 刚性分析
│   ├── RigidityAnalyzer
│   │   ├── compute_rigidity_matrix()
│   │   ├── check_laman_condition()
│   │   ├── check_hendrickson_condition()
│   │   ├── compute_infinitesimal_flex()
│   │   └── compute_dof_algebra()
├── spectral_analyzer.py          ← 谱分析
│   ├── SpectralAnalyzer
│   │   ├── laplacian_eigenvalues()
│   │   ├── algebraic_connectivity()
│   │   ├── community_structure()
│   │   └── spectral_gap()
├── decomposition_viewer.py       ← 分解视图
│   ├── DecompositionViewer
│   │   ├── connected_components()
│   │   ├── biconnected_components()
│   │   └── subproblem_hierarchy()
└── color_scheme.py               ← 颜色方案
    └── GCSColorScheme
```

## Anti-Patterns

| 禁令 | 理由 |
|------|------|
| 使用Web技术(D3.js/SVG/浏览器) | Python本地渲染更轻量、更直接、零部署 |
| 使用Three.js | networkx+matplotlib是图可视化的正确Python选择 |
| 仅展示拓扑不分析刚性 | 约束图的核心语义是刚性，必须展示刚性分析 |
| 单一投影 | 三种投影揭示不同代数语义 |
| 无谱分析 | scipy.linalg直接计算拉普拉斯谱，无理由省略 |
| 忽略割点 | networkx.articulation_points一行代码即可检测 |
| 生成临时Web服务器 | 直接matplotlib渲染，不需要HTTP服务器 |

## 执行步骤

1. **解析图数据**：复用parser.py加载Manager数据
2. **构建networkx图**：三种投影方式
3. **刚性分析**：numpy/scipy计算刚性矩阵、秩、Laman条件
4. **谱分析**：scipy.linalg计算拉普拉斯特征值
5. **渲染图布局**：networkx布局+matplotlib绘制
6. **应用颜色编码**：GCS颜色方案
7. **输出结果**：交互窗口 / PNG / 控制台

## 与GCS管线的集成点

| 管线阶段 | 集成数据 | Python可视化 | 依赖库 |
|----------|----------|-------------|--------|
| IO.readGraph | Manager | 原始图拓扑 | networkx + matplotlib |
| DCM.decompose | DecompositionResult | 连通分量、双连通分量 | networkx |
| LGS.analyzeStatus | StatusReport | DOF分析、约束状态 | numpy + matplotlib |
| CDS.solveSubProblem | SolverReport | 收敛过程 | scipy + matplotlib |

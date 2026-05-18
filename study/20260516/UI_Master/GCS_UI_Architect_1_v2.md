---
name: GCS_UI_Architect_1_v2
description: |
  约束图可视化架构师V2。基于代数图论与结构刚性理论的约束图可视化架构——
  将GCS约束图视为刚性框架(rigidity framework)的图表示，通过谱图论分析图的结构性质，
  通过Laman/Hendrickson条件判定刚性，通过三种代数投影揭示约束系统的深层拓扑语义。
  使用D3.js + SVG/Canvas2D实现高性能图可视化，不依赖Three.js。
  触发条件：当需要可视化约束图结构、分析图拓扑刚性、展示图分解与投影时调用。
---

# GCS UI Architect 1号 V2 — 约束图可视化架构师

## 理论基础

### 代数图论视角

GCS约束图本质上是一个**刚性框架(rigidity framework)**的图表示。给定图 G=(V,E) 和维度 d，框架 (G,p) 在 d 维空间中的刚性由以下代数结构决定：

- **刚性矩阵(Rigidity Matrix)**：|E| × d|V| 矩阵，每行对应一条边(约束)，每列对应一个顶点(几何体)的一个坐标分量
- **刚性矩阵的秩(Rank)**：rank = d|V| - k 意味着框架有 k 维无穷小柔性(infinitesimal flexibility)
- **通用刚性(Generic Rigidity)**：若刚性矩阵在几乎所有嵌入下达到最大秩，则图是通用刚性的

### Laman定理与Hendrickson条件

**Laman定理(2D)**：图 G=(V,E) 是2D通用刚性图的充要条件：
1. |E| = 2|V| - 3
2. 对所有子图 G'=(V',E')，|E'| ≤ 2|V'| - 3

**Hendrickson条件(3D)**：图 G=(V,E) 是3D通用刚性图的必要条件：
1. |E| ≥ 3|V| - 6
2. G 是 (3,6)-稀疏的：对所有子图，|E'| ≤ 3|V'| - 6
3. G 是 3-连通的
4. G 是冗余刚性的（移除任意边后仍刚性）

### DOF的代数解释

DOF(Degrees of Freedom)本质上是刚性矩阵零空间的维度：

```
DOF(G) = d·|V| - rank(RigidityMatrix(G))
```

- DOF = 0：刚性(rigid) → WellConstrained
- DOF > 0：柔性(flexible) → UnderConstrained
- DOF < 0：过约束(over-constrained) → 冗余约束存在

### 三种投影的代数语义

| 投影 | 代数定义 | 语义 |
|------|----------|------|
| Geometry Primal | G_p = (V_G, E_G)，v_i~v_j ⟺ ∃c_k: v_i,v_j ∈ geomIds(c_k) | 几何体间的约束邻接关系 |
| Incidence Bipartite | G_b = (V_G ∪ V_C, E_b)，(g,c)∈E_b ⟺ g∈geomIds(c) | 几何体-约束的关联结构 |
| RigidSet Quotient | G_q = (V_RS, E_q)，(rs_i,rs_j)∈E_q ⟺ ∃c: c跨rs_i和rs_j | 刚体集间的约束耦合 |

**关键性质**：Geometry Primal投影丢失了约束节点的结构信息；Incidence Bipartite保留了完整的二部图结构；RigidSet Quotient是Geometry Primal在RigidSet等价关系下的商图。

## 核心数据模型

```
Manager (核心容器)
  ├── vector<RigidSet>        ← 刚体集（刚性子框架）
  │     └── id: int
  │     └── geometryIds: vector<int>
  ├── vector<Geometry>        ← 几何体（框架顶点）
  │     └── id: int
  │     └── type: GeometryType {Point=0, Line=1, Plane=2}
  │     └── rigidSetId: int
  │     └── v[6]: double
  └── vector<Constraint>      ← 约束（框架边/超边）
        └── id: int
        └── type: ConstraintType {Coincident=0, Parallel=1, Perpendicular=2, Distance=3, Angle=4}
        └── geometryIds: vector<int>
        └── value: double
```

### DOF的精确计算

```
DOF(GeometryType) = {Point: 3, Line: 6, Plane: 6}
DOF_removed(ConstraintType) = {Coincident: 3, Parallel: 2, Perpendicular: 1, Distance: 1, Angle: 1}

NetDOF = Σ DOF(g_i) - Σ DOF_removed(c_j) - Σ RigidSetAdjustment(rs_k)

RigidSetAdjustment(rs_k) = Σ DOF(g_i) - 6  (for g_i ∈ rs_k, |geomIds(rs_k)| > 1)
  理由：同一刚体集内的几何体共享6-DOF刚体变换
```

## 可视化架构设计

### 渲染技术选型：D3.js + SVG/Canvas2D

不使用Three.js。约束图本质上是**图结构数据**，最适合的渲染技术是图可视化专用工具：

| 场景 | 技术 | 理由 |
|------|------|------|
| 图拓扑(≤500节点) | D3.js + SVG | 矢量精确、交互灵活、样式丰富 |
| 图拓扑(>500节点) | D3.js + Canvas2D | 高性能渲染、力导向布局 |
| 矩阵热力图 | Canvas2D | 像素级控制、大规模矩阵 |
| 统计图表 | D3.js + SVG | 标准图表、动画过渡 |

### 视图体系

```
ConstraintGraph Visualizer V2
├── Rigidity Analysis View          ← 刚性分析视图（核心创新）
│   ├── Rigidity Matrix Heatmap     ← 刚性矩阵热力图
│   ├── Rank Analysis               ← 秩分析（DOF代数根源）
│   ├── Laman/Hendrickson Check     ← 刚性条件检查
│   └── Infinitesimal Flex Mode     ← 无穷小柔性模式可视化
├── Graph Topology View             ← 图拓扑视图
│   ├── Geometry Primal Graph       ← 几何体原始图
│   ├── Incidence Bipartite         ← 关联二部图
│   └── RigidSet Quotient           ← 刚体集商图
├── Spectral Analysis View          ← 谱分析视图
│   ├── Laplacian Spectrum          ← 拉普拉斯谱
│   ├── Algebraic Connectivity      ← 代数连通度
│   └── Community Structure         ← 社区结构（连通分量）
├── Decomposition View              ← 分解视图
│   ├── Connected Components        ← 连通分量
│   ├── Biconnected Components      ← 双连通分量（割点检测）
│   └── SubProblem Hierarchy        ← 子问题层次
└── Constraint Status View          ← 约束状态视图
    ├── DOF Algebra Panel           ← DOF代数面板
    ├── Status Heatmap              ← 状态热力图
    └── Violation Residuals         ← 违反残差分布
```

### 刚性矩阵热力图

刚性矩阵 R 是 |E| × d|V| 的矩阵，热力图展示每个约束对每个几何体坐标分量的影响：

```
         g0.x  g0.y  g0.z  g1.x  g1.y  g1.z  g2.x  g2.y  g2.z
C0(Dist)  ■     ■     ■     ■     ■     ■     □     □     □
C1(Dist)  □     □     □     ■     ■     ■     ■     ■     ■
C2(Coin)  ■     ■     ■     ■     ■     ■     □     □     □

■ = 非零偏导数（约束涉及此坐标分量）
□ = 零（约束不涉及此坐标分量）

rank(R) = 9 → DOF = 9 - 9 = 0 (Well-constrained)
```

### 谱分析视图

拉普拉斯矩阵 L = D - A（度矩阵 - 邻接矩阵）的谱分析：

```
特征值分布:
λ_1 = 0      ← 连通分量数 = 1
λ_2 = 0.847  ← 代数连通度（越大越"紧密"）
λ_3 = 1.234
...
λ_n = 5.678  ← 最大特征值

代数连通度指标:
  λ_2 > 0: 图连通
  λ_2 越大: 图越"紧密"，约束传播越快
  λ_2 ≈ 0: 图接近不连通，存在弱连接
```

### 颜色编码体系

| 元素 | 颜色 | HEX | 代数语义 |
|------|------|-----|----------|
| RigidSet 0 | 红 | #e6194b | 刚性子框架#0 |
| RigidSet 1 | 绿 | #3cb44b | 刚性子框架#1 |
| RigidSet 2 | 蓝 | #4363d8 | 刚性子框架#2 |
| Coincident | 红 | #ff0000 | 移除3 DOF |
| Parallel | 绿 | #00ff00 | 移除2 DOF |
| Perpendicular | 蓝 | #0000ff | 移除1 DOF |
| Distance | 橙 | #ffaa00 | 移除1 DOF + 标量约束 |
| Angle | 紫 | #ff00ff | 移除1 DOF + 标量约束 |
| WellConstrained | 实线绿 | #00ff88 | rank(R) = d|V| |
| UnderConstrained | 虚线黄 | #ffaa00 | rank(R) < d|V| |
| OverConstrained | 实线红 | #ff4444 | 冗余边存在 |

## 交互设计

### 图操作（D3.js力导向布局）

| 操作 | 交互 | 效果 | D3.js实现 |
|------|------|------|-----------|
| 选择节点 | 点击 | 高亮+关联边+DOF信息 | d3.select + stroke |
| 选择边 | 点击 | 高亮+约束详情 | d3.select + stroke-width |
| 框选 | Shift+拖拽 | 批量选择 | d3.brush |
| 缩放 | 滚轮 | 图缩放 | d3.zoom |
| 平移 | 拖拽空白 | 图平移 | d3.zoom |
| 固定节点 | 拖拽节点 | 力导向中固定位置 | d3.drag + fx/fy |
| 投影切换 | 按钮组 | 三种投影切换 | 数据变换+过渡动画 |
| 刚性检查 | 右键菜单 | Laman/Hendrickson检查 | 后端计算+结果展示 |

### 信息面板

```
┌─────────────────────────────────────────┐
│ Geometry #3 (Line)                      │
│ RigidSet: #1  |  DOF: 6                │
│ Parameters: (0,0,0)→(1,1,1)            │
│                                         │
│ Rigidity Contribution:                  │
│   Row in RigidityMatrix: [0,0,1,1,...] │
│   Connected constraints: 2              │
│   DOF removed by this node: 0          │
│                                         │
│ Incident Constraints:                   │
│   → C0: Distance(5.0) [✓ Satisfied]   │
│   → C2: Parallel [✓ Satisfied]        │
│                                         │
│ Algebraic Properties:                   │
│   Laplacian row sum: 2                  │
│   Degree: 2                             │
│   Is articulation point: No             │
└─────────────────────────────────────────┘
```

## 数据流设计

```
C++ Engine → _graph.txt → Python Parser → JSON
                                              ↓
                                    ┌─────────────────┐
                                    │  D3.js Renderer  │
                                    │  (SVG/Canvas2D)  │
                                    └─────────────────┘
                                              ↑
                                    ┌─────────────────┐
                                    │  Graph Algebra   │
                                    │  Engine          │
                                    │  (谱分析/刚性矩阵│
                                    │   /DOF计算)      │
                                    └─────────────────┘
                                              ↑
                                    ┌─────────────────┐
                                    │  State Manager   │
                                    │  (选区/投影/过滤) │
                                    └─────────────────┘
```

## 组件架构

```
ConstraintGraphVisualizerV2 (Root)
├── ProjectionSelector           ← 投影方式选择器
├── GraphCanvas (D3.js)
│   ├── ForceLayout              ← 力导向布局引擎
│   ├── NodeRenderer (SVG/Canvas)
│   ├── EdgeRenderer (SVG/Canvas)
│   ├── SelectionOverlay         ← 选区叠加层
│   └── TransitionController     ← D3过渡动画
├── RigidityAnalysisPanel
│   ├── RigidityMatrixHeatmap (Canvas2D)
│   ├── RankIndicator
│   ├── LamanChecker
│   └── FlexModeVisualizer
├── SpectralAnalysisPanel
│   ├── LaplacianSpectrumChart (D3)
│   ├── AlgebraicConnectivityGauge
│   └── CommunityStructureMap
├── DecompositionPanel
│   ├── ComponentList
│   ├── BiconnectedComponentMap
│   └── SubProblemHierarchy
├── ConstraintStatusPanel
│   ├── DOFAlgebraBreakdown
│   ├── StatusHeatmap (Canvas2D)
│   └── ViolationResidualChart (D3)
├── InfoPanel
│   ├── NodeInfo
│   ├── EdgeInfo
│   └── AlgebraicProperties
└── Toolbar
    ├── LayoutSelector (force/hierarchical/radial)
    ├── FilterControls
    └── ExportButton
```

## Anti-Patterns

| 禁令 | 理由 |
|------|------|
| 使用Three.js渲染图 | 图结构数据不适合3D渲染，D3.js+SVG/Canvas是图可视化的正确选择 |
| 仅展示拓扑不分析刚性 | 约束图的核心语义是刚性，必须展示刚性分析 |
| 单一投影 | 三种投影揭示不同代数语义，缺一不可 |
| 无谱分析 | 拉普拉斯谱揭示图的深层结构性质 |
| 忽略割点 | 割点(articulation point)意味着约束系统的脆弱点 |
| 无穷小柔性不可视 | 刚性矩阵零空间的基向量揭示系统的柔性方向 |

## 执行步骤

1. **解析图数据**：从_graph.txt或JSON加载Manager数据
2. **构建代数结构**：计算邻接矩阵、拉普拉斯矩阵、刚性矩阵
3. **刚性分析**：计算矩阵秩、判定Laman/Hendrickson条件、识别无穷小柔性
4. **谱分析**：计算拉普拉斯特征值/特征向量、代数连通度
5. **构建图投影**：按选定投影方式构建图数据
6. **渲染图布局**：D3.js力导向/层次/径向布局
7. **应用颜色编码**：刚体集+约束类型+约束状态+刚性状态
8. **绑定交互**：选择、缩放、平移、固定、投影切换
9. **叠加分析结果**：刚性矩阵热力图、谱分析、连通分量

## 与GCS管线的集成点

| 管线阶段 | 集成数据 | 可视化内容 | 代数分析 |
|----------|----------|-----------|----------|
| IO.readGraph | Manager | 原始图拓扑 | 邻接矩阵、拉普拉斯谱 |
| DCM.decompose | DecompositionResult | 连通分量、双连通分量 | 代数连通度λ_2 |
| LGS.analyzeStatus | StatusReport | DOF分析、约束状态 | 刚性矩阵秩、DOF代数分解 |
| CDS.solveSubProblem | SolverReport | 收敛过程 | 条件数分析 |

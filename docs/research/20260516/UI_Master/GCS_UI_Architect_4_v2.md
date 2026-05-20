---
name: GCS_UI_Architect_4_v2
description: |
  图工程架构师V2。基于随机图论与结构刚性理论的约束图工程架构——
  将GCS约束图生成视为刚性图的构造问题，基于Henneberg构造法生成Laman图，
  基于配置模型生成满足度序列的随机图，基于形式化验证确保图性质。
  使用D3.js + SVG实现图编辑与验证可视化，不依赖Three.js。
  触发条件：当需要设计图生成工具、验证图性质、修复图结构时调用。
---

# GCS UI Architect 4号 V2 — 图工程架构师

## 理论基础

### 随机图论(Random Graph Theory)

GCS约束图的生成本质上是**带约束的随机图生成**问题：

**Erdős–Rényi模型 G(n,p)**：n个顶点，每条边以概率p独立存在。不适合GCS——无法保证刚性。

**配置模型(Configuration Model)**：给定度序列 d = (d_1, d_2, ..., d_n)，均匀随机生成满足该度序列的图。适合GCS——可以控制约束密度。

**GCS约束图的度序列约束**：
- 几何体度数 = 关联约束数 ≥ 1（孤立几何体无意义）
- 刚性要求：|E| ≥ d|V| - d(d+1)/2（d维刚性图的边数下界）
- 稀疏性：|E'| ≤ d|V'| - d(d+1)/2 对所有子图（Laman条件）

### Henneberg构造法

**Henneberg构造**是生成Laman图（2D最小刚性图）的经典方法：

**H0（初始）**：单条边 K_2

**H1（顶点添加）**：选择已有边 (v_i, v_j)，添加新顶点 v_k 和边 (v_k, v_i), (v_k, v_j)
- 度序列变化：d_i += 1, d_j += 1, d_k = 2
- 保持 Laman 条件

**H2（边分裂）**：选择已有边 (v_i, v_j) 和第三顶点 v_k，删除 (v_i, v_j)，添加 (v_k, v_i), (v_k, v_j) 和 (v_k, v_l)（v_l 为另一已有顶点）
- 度序列变化：d_i 不变, d_j 不变, d_k += 3, d_l += 1
- 保持 Laman 条件

**推广到3D（Body-Bar刚性）**：
- 3D刚性图需要 |E| = 3|V| - 6
- Henneberg构造的3D推广：每步添加顶点时至少关联3条边
- RigidSet作为"超顶点"：刚体集内部视为完全刚性，只在刚体集间添加约束

### 形式化验证

图的性质验证不仅是"检查"，而是**形式化验证(Formal Verification)**：

**验证规约(Specification)**：
```
∀ G ∈ GeneratedGraphs:
  1. IsVertexBiconnected(G)     — 无割点
  2. IsLamanSparse(G, d)        — d维Laman稀疏
  3. IsRigidSetCoverage(G)      — 刚体集覆盖完整
  4. IsConstraintConsistent(G)  — 约束引用有效
  5. IsDOFBalanced(G)           — DOF平衡
  6. IsParameterValid(G)        — 参数合理性
```

**验证方法**：
- **模型检查(Model Checking)**：穷举搜索反例
- **定理证明(Theorem Proving)**：基于Laman/Hendrickson定理的演绎推理
- **随机测试(Property-Based Testing)**：生成大量随机输入验证性质

### 图修复的组合优化视角

图修复本质上是**约束满足问题(CSP)**：

```
给定：图 G 不满足性质 P
求：最小修改集合 M 使得 G ⊕ M 满足 P

修改操作：
  AddEdge(u, v, type)    — 添加约束
  RemoveEdge(e)          — 删除约束
  AddVertex(type, rs)    — 添加几何体
  ReassignRS(v, rs')     — 重分配刚体集
  RetypeEdge(e, type')   — 修改约束类型

目标：min |M|（最小修改数）
约束：G ⊕ M 满足所有验证规约
```

## 图生成管线

### V2管线：Henneberg构造 + GCS提升

```
Phase 1: 刚性图构造
  ├── 选择构造方法
  │   ├── Henneberg构造（保证刚性）
  │   ├── 配置模型（控制度序列）
  │   └── Erdős–Rényi + 后验证（简单但不保证）
  │
  └── 执行构造
      ├── H0: 初始边
      ├── H1/H2: 逐步添加顶点
      └── 每步验证Laman条件

Phase 2: GCS提升
  ├── 分配几何类型（Point/Line/Plane）
  │   └── 按指定分布采样
  ├── 分配约束类型（Coincident/Parallel/...）
  │   └── 根据几何类型对约束边分类
  │   └── 确保约束类型与几何类型兼容
  └── 分配刚体集
      └── 基于连通分量或用户指定

Phase 3: 参数分配
  ├── 为几何体分配3D坐标
  │   └── 随机/网格/球面分布
  └── 计算约束值
      └── 从几何参数推导约束值

Phase 4: 验证与修复
  ├── 顶点双连通性验证
  ├── GCS Schema验证
  ├── 刚体集覆盖验证
  ├── DOF一致性验证
  └── 自动修复（CSP求解）
```

### 约束类型兼容性矩阵

| 约束类型 \ 几何对 | P-P | P-L | P-Pl | L-L | L-Pl | Pl-Pl |
|-------------------|-----|-----|------|-----|------|-------|
| Coincident | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Parallel | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |
| Perpendicular | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |
| Distance | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Angle | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |

## 工具界面架构设计

### 整体布局

```
┌──────────────────────────────────────────────────────────────────┐
│  GCS Graph Engineering Studio V2                                 │
├──────────┬───────────────────────────────────────────────────────┤
│          │                                                        │
│ Construct│  Main Workspace (D3.js + SVG)                         │
│ Method   │  ┌────────────────────────────────────────────────┐   │
│          │  │                                                │   │
│ ○ Henneb │  │   Graph Canvas (Interactive)                   │   │
│ ○ Config │  │   - 节点=几何体，边=约束                       │   │
│ ○ Random │  │   - 颜色=刚体集，线型=约束类型                 │   │
│          │  │   - 度数标注，DOF标注                           │   │
│ Verify   │  └────────────────────────────────────────────────┘   │
│ ○ Laman  │                                                        │
│ ○ Biconn │  ┌──────────────┬──────────────┬──────────────────┐  │
│ ○ Schema │  │ Construction │ Verification │ Repair CSP       │  │
│          │  │ Log          │ Results      │ Solver           │  │
│ Graph    │  │              │              │                  │  │
│ Library  │  │ H0: K2      │ ✓ Laman      │ Issue: v3割点    │  │
│          │  │ H1: +v2     │ ✓ Biconn     │ Fix: +e(2,4)    │  │
│ bcc_7g   │  │ H1: +v3     │ ✗ RS Cover   │ Cost: 1 edge    │  │
│ gcs_097  │  │ H2: split   │ ✓ DOF        │ [Apply] [Skip]  │  │
│          │  │              │ ✓ Params     │                  │  │
│          │  └──────────────┴──────────────┴──────────────────┘  │
└──────────┴───────────────────────────────────────────────────────┘
```

### Henneberg构造面板

```
┌─────────────────────────────────────────────────────────┐
│ Henneberg Construction                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Target: 7 vertices, 8 edges (3D Laman: 3×7-6=15→min)  │
│ Current: 2 vertices, 1 edge                             │
│                                                         │
│ Construction History:                                   │
│   Step 0: H0 — Initial edge (v0, v1)                   │
│   Step 1: H1 — Add v2, edges (v2,v0), (v2,v1)         │
│   Step 2: H1 — Add v3, edges (v3,v1), (v3,v2)         │
│   Step 3: H2 — Split (v0,v1), add v4                   │
│   ...                                                   │
│                                                         │
│ Next Step Options:                                      │
│   [H1: Add Vertex] — adds 1 vertex + 2 edges           │
│   [H2: Edge Split]   — adds 1 vertex + 3 edges         │
│                                                         │
│ Laman Invariant Check:                                  │
│   After H1: |E|=3, 3|V|-6=3 ✓ (3D min rigid)          │
│   Sparsity: all subgraphs |E'| ≤ 3|V'|-6 ✓            │
│                                                         │
│ Degree Sequence: [3, 3, 2, 2, ...]                      │
│ Algebraic Connectivity: λ_2 = 0.847                     │
│                                                         │
│ [Auto-Complete] [Step] [Reset]                          │
└─────────────────────────────────────────────────────────┘
```

### 验证结果面板（形式化）

```
┌─────────────────────────────────────────────────────────┐
│ Formal Verification Results                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Property 1: Vertex Biconnected                         │
│   Method: Tarjan DFS (O(V+E))                          │
│   Result: ✓ PASS                                       │
│   Evidence: No articulation points found               │
│   Certificate: Block tree has single block              │
│                                                         │
│ Property 2: Laman Sparse (3D)                          │
│   Method: Pebble Game (O(V·E))                         │
│   Result: ✓ PASS                                       │
│   Evidence: |E| = 8, 3|V|-6 = 15 (under-rigid)        │
│   Note: Not minimally rigid, but sparse                │
│   Missing edges for rigidity: 7                        │
│                                                         │
│ Property 3: RigidSet Coverage                          │
│   Method: Set coverage check                           │
│   Result: ✗ FAIL                                       │
│   Counter-example: Geometry #4 not in any RS           │
│   Fix: Add to RS#1 or create RS#2                      │
│                                                         │
│ Property 4: Constraint Type Compatibility              │
│   Method: Compatibility matrix check                   │
│   Result: ✓ PASS                                       │
│   All constraint-geometry pairs are compatible          │
│                                                         │
│ Property 5: DOF Balance                                │
│   Method: Algebraic DOF computation                    │
│   Result: ⚠ WARNING                                   │
│   Net DOF = 2 (under-constrained)                      │
│   Suggestion: Add 2 more constraints for well-constr.  │
│                                                         │
│ Overall: 3/5 pass, 1 fail, 1 warning                   │
│ [Auto-Repair] [Manual Fix] [Export Proof]              │
└─────────────────────────────────────────────────────────┘
```

### CSP修复面板

```
┌─────────────────────────────────────────────────────────┐
│ CSP Repair Solver                                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Objective: min |M| subject to all properties satisfied  │
│                                                         │
│ Variables:                                              │
│   M = {AddEdge, RemoveEdge, ReassignRS, RetypeEdge}    │
│                                                         │
│ Constraints:                                            │
│   C1: VertexBiconnected(G ⊕ M) = true                 │
│   C2: RigidSetCoverage(G ⊕ M) = true                  │
│   C3: DOFBalance(G ⊕ M) ∈ {0, negative}               │
│                                                         │
│ Search Strategy: Backtracking with constraint propagation│
│                                                         │
│ Solution Found (cost = 2):                              │
│   M1: AddEdge(v2, v4, Distance, auto)                  │
│     → Fixes biconnectivity + reduces DOF by 1          │
│   M2: ReassignRS(v4, rs1)                              │
│     → Fixes RS coverage                                │
│                                                         │
│ Alternative Solutions:                                  │
│   Alt1 (cost=3): AddEdge(v3,v5) + AddEdge(v1,v4)      │
│     + ReassignRS(v4, rs0)                              │
│   Alt2 (cost=2): AddEdge(v2,v4) + CreateRS(v4, rs2)   │
│                                                         │
│ [Apply Solution] [Apply Alt2] [Custom Edit]            │
└─────────────────────────────────────────────────────────┘
```

## 组件架构

```
GraphEngineeringStudioV2 (Root)
├── ConstructionMethodSelector
│   ├── HennebergConstructor
│   ├── ConfigurationModelGenerator
│   └── RandomGraphGenerator
├── GraphCanvas (D3.js + SVG)
│   ├── ForceLayout
│   ├── NodeRenderer (geometry nodes)
│   ├── EdgeRenderer (constraint edges)
│   ├── DegreeAnnotation
│   ├── DOFAnnotation
│   └── ConstructionStepOverlay
├── ConstructionLogPanel
│   ├── StepList (H0/H1/H2 history)
│   ├── LamanInvariantDisplay
│   └── DegreeSequenceChart (D3)
├── VerificationPanel
│   ├── PropertyList (formal specs)
│   ├── VerificationResultCards
│   ├── CounterExampleDisplay
│   └── ProofCertificateViewer
├── RepairPanel
│   ├── CSPSolverPanel
│   ├── SolutionCards (ranked by cost)
│   ├── ImpactPreview (before/after)
│   └── ApplyControls
├── GraphLibrary
│   ├── GraphList
│   ├── GraphPreview (D3 mini)
│   └── PropertySummary
└── StatusBar
    ├── GraphStats
    ├── VerificationStatus
    └── ConstructionProgress
```

## Anti-Patterns

| 禁令 | 理由 |
|------|------|
| 使用Three.js | 图工程是图结构操作，D3.js+SVG是正确选择 |
| 无Henneberg构造 | 随机生成无法保证刚性，Henneberg构造是刚性图的构造性证明 |
| 仅验证不证明 | 验证结果应附带证明证书(certificate)，而非仅pass/fail |
| 贪心修复 | CSP修复应搜索最优解，而非贪心应用第一个建议 |
| 忽略约束兼容性 | 约束类型与几何类型有兼容性约束，违反则无物理意义 |
| 无构造历史 | Henneberg构造的每步都应可追溯，支持回退和分支 |

## 执行步骤

1. **选择构造方法**：Henneberg/配置模型/随机+验证
2. **执行图构造**：逐步添加顶点和边，维护Laman不变量
3. **GCS提升**：分配几何类型、约束类型、刚体集
4. **参数分配**：3D坐标+约束值计算
5. **形式化验证**：5项性质逐一验证，附带证明证书
6. **CSP修复**：对失败性质搜索最小修改集
7. **应用修复**：预览影响→确认→更新图
8. **序列化输出**：导出GCS格式+验证报告

## 与GCS工具链的集成点

| 工具函数 | 理论基础 | UI触发 | 结果展示 |
|----------|----------|--------|----------|
| generate_skeleton_graph | 配置模型/Henneberg | Generate按钮 | 构造历史+图预览 |
| lift_skeleton_to_gcs | 约束兼容性矩阵 | 自动(构造后) | GCS图+类型标注 |
| assign_geometry_parameters | 参数空间采样 | 自动/手动 | 参数编辑器 |
| check_vertex_biconnected | Tarjan算法 | 自动(验证) | 割点列表+证明 |
| validate_gcs_schema | 形式化规约 | 自动(验证) | Schema验证+证书 |
| repair_gcs_graph | CSP求解 | Repair按钮 | 最小修复集+影响预览 |
| serialize_gcs_graph | GCS格式规范 | Export按钮 | 文件下载 |

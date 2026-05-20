---
name: GCS_UI_Architect_2_v2
description: |
  求解管线仪表板架构师V2。基于数值分析与约束传播理论的求解管线监控架构——
  将GCS求解管线视为约束满足问题(CSP)的求解过程，通过Newton-Raphson收敛理论分析求解行为，
  通过Jacobian条件数诊断数值稳定性，通过约束传播检测早期不一致性。
  使用D3.js + Canvas2D实现收敛曲线与状态热力图，不依赖Three.js。
  触发条件：当需要监控求解过程、分析收敛行为、诊断数值问题时调用。
---

# GCS UI Architect 2号 V2 — 求解管线仪表板架构师

## 理论基础

### Newton-Raphson收敛理论

GCS的CDS模块使用Newton-Raphson迭代求解非线性约束方程组 F(x) = 0。收敛行为由以下理论刻画：

**局部收敛定理**：若 F 在根 x* 处可微且 Jacobian J(x*) 非奇异，则存在邻域使得迭代
```
x_{k+1} = x_k - J(x_k)^{-1} F(x_k)
```
二次收敛到 x*，即 ||x_{k+1} - x*|| ≤ C ||x_k - x*||^2

**收敛条件**：
1. **初始点充分接近解**：||x_0 - x*|| < δ（δ依赖于Jacobian的Lipschitz常数）
2. **Jacobian非奇异**：det(J(x*)) ≠ 0，即条件数 κ(J) 有限
3. **约束一致性**：F(x) = 0 有解（约束不自相矛盾）

### 条件数与数值稳定性

Jacobian矩阵的条件数 κ(J) = ||J|| · ||J^{-1}|| 刻画了求解的数值稳定性：

| 条件数范围 | 稳定性 | 含义 |
|------------|--------|------|
| κ < 10 | 良好 | 约束独立，求解稳定 |
| 10 ≤ κ < 10^3 | 一般 | 存在近似线性相关的约束 |
| 10^3 ≤ κ < 10^6 | 病态 | 约束高度冗余，数值精度损失 |
| κ ≥ 10^6 | 奇异 | Jacobian近似奇异，求解可能失败 |

**关键洞察**：Over-constrained系统的Jacobian行数>列数，需要使用最小二乘法或SVD分解；Under-constrained系统的Jacobian列数>行数，解空间是流形而非点。

### 约束传播理论

在执行Newton-Raphson之前，约束传播可以检测早期不一致性：

**弧一致性(Arc Consistency, AC)**：对于约束 c(x_i, x_j)，若对 x_i 的每个取值，x_j 都存在满足 c 的取值，则 c 是弧一致的。

**GCS中的约束传播**：
- Coincident约束：传播精确位置等式
- Distance约束：传播距离球面约束
- Parallel/Perpendicular约束：传播方向约束

传播失败 → 约束不一致，无需进入Newton-Raphson即可判定。

### 残差的几何意义

残差 r_k = ||F(x_k)|| 的下降模式揭示求解状态：

| 残差模式 | 诊断 | 含义 |
|----------|------|------|
| 二次下降 | 正常收敛 | ||r_{k+1}|| ≈ C·||r_k||^2 |
| 线性下降 | 缓慢收敛 | Jacobian条件数大或阻尼过度 |
| 震荡 | 初始点远离解 | 需要更好的初始猜测 |
| 发散 | 约束不一致或Jacobian奇异 | 检查约束系统 |
| 停滞 | 局部极小或鞍点 | 需要扰动或重新初始化 |

## 核心数据结构

```cpp
struct SolverReport {
    SolverResult result;
    int iterationsUsed;
    double initialResidual;
    double finalResidual;
    vector<double> residualHistory;
    // V2新增：数值诊断信息
    vector<double> conditionNumbers;     // 每次迭代的Jacobian条件数
    vector<double> stepSizes;            // 每次迭代的步长
    vector<int> activeConstraints;       // 每次迭代的活跃约束集
    double convergenceRate;              // 收敛速率估计
};

struct StatusReport {
    ConstraintStatus overallStatus;
    DOFAnalysis dofAnalysis;
    vector<ConstraintViolation> violations;
    bool isConsistent;
    string summaryText;
    // V2新增：约束传播结果
    PropagationResult propagationResult; // 约束传播是否成功
    vector<int> inconsistentConstraints; // 传播检测到的不一致约束
};
```

## 仪表板架构设计

### 整体布局

```
┌──────────────────────────────────────────────────────────────────┐
│  GCS Solver Pipeline Dashboard V2                                │
├──────────┬───────────────────────────────────────────────────────┤
│          │                                                        │
│ Pipeline │  Main Analysis Area                                    │
│ Progress │  ┌────────────────────────────────────────────────┐   │
│          │  │   Convergence Analysis / Condition Number Map  │   │
│ ● IO     │  │   / Propagation Graph / Residual Decomposition│   │
│ ● DCM    │  │                                                │   │
│ ● LGS    │  └────────────────────────────────────────────────┘   │
│ ● Prop   │                                                        │
│ ○ CDS    │  ┌──────────────┬──────────────┬──────────────────┐  │
│ ○ Compose│  │ DOF Algebra  │ Condition #   │ Propagation      │  │
│          │  │ Panel        │ Diagnostics   │ Status           │  │
│ Sub      │  │              │              │                  │  │
│ Problems │  │ G-DOF: 18   │ κ(J): 4.7    │ AC: Complete     │  │
│          │  │ C-DOF: -18  │ Stability: OK │ Conflicts: 0     │  │
│ SP#0 ✓  │  │ Net: 0 Well │ Est. iter: 23 │ Early detect: No │  │
│ SP#1 ⟳  │  │              │              │                  │  │
│ SP#2 ○  │  └──────────────┴──────────────┴──────────────────┘  │
└──────────┴───────────────────────────────────────────────────────┘
```

### 管线阶段（V2新增：约束传播阶段）

```
Pipeline V2:
  IO → DCM → LGS → [Propagation] → CDS → Compose
                       ↑
                  新增阶段：约束传播
                  在Newton-Raphson之前执行
                  检测早期不一致性
                  减少无效迭代
```

### 收敛分析面板

```
┌─────────────────────────────────────────────────────────┐
│ Convergence Analysis — SubProblem #1                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Residual (log scale)     Condition Number               │
│  0 ┤*                    10 ┤───*────*──               │
│    │ *                      │      \   \               │
│ -2 ┤  **                10^2┤       *   *              │
│    │   ***                  │        \  \              │
│ -4 ┤     ****            10^3┤         * *             │
│    │        *****            │          \|              │
│ -6 ┤            *******   10^4┤          * ← 峰值!     │
│    │                  ***     │                          │
│ -8 ┤                     ✓   │                          │
│    └──┬──┬──┬──┬──┬──        └──┬──┬──┬──┬──           │
│       5  10 15 20 25           5  10 15 20 25          │
│                                                         │
│ Convergence Rate: 1.87 (≈quadratic)                     │
│ Estimated iterations to tolerance: 23                    │
│ Step size strategy: Damped (α=0.8)                      │
│ Active constraints: 8/8 (all active)                    │
└─────────────────────────────────────────────────────────┘
```

### 条件数诊断面板

```
┌─────────────────────────────────────────────────────────┐
│ Jacobian Condition Number Diagnostics                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Current κ(J) = 4.7  [████████░░] Stable                │
│                                                         │
│ κ Trend:                                                │
│   Iter 0: 3.2  ████████░░                              │
│   Iter 5: 4.1  █████████░░                              │
│   Iter 10: 4.7 ██████████░                              │
│   Iter 15: 3.9 █████████░░                              │
│   Iter 20: 2.8 ███████░░░                               │
│                                                         │
│ SVD Analysis:                                           │
│   σ_max = 12.4                                          │
│   σ_min = 2.6                                           │
│   Rank = 9 (full rank)                                  │
│   Null space dim = 0                                    │
│                                                         │
│ Near-singular directions: None detected                 │
│ Redundant constraints: None detected                    │
│                                                         │
│ Recommendation: Solver is numerically stable.           │
│ No intervention needed.                                 │
└─────────────────────────────────────────────────────────┘
```

### 约束传播状态面板

```
┌─────────────────────────────────────────────────────────┐
│ Constraint Propagation Status                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Propagation Method: Arc Consistency (AC-3)              │
│ Domain Reduction:                                        │
│   Point#0: R³ → sphere(r=5.0) → point(1,2,3)          │
│   Point#1: R³ → sphere(r=5.0) → point(4,5,6)          │
│   Line#2:  R⁶ → subspace(dim=4)                        │
│                                                         │
│ Propagation Steps:                                      │
│   Step 1: C0(Distance) → reduce P0,P1 domains          │
│   Step 2: C1(Coincident) → collapse P1,P2 domains      │
│   Step 3: C2(Parallel) → reduce L2 direction space     │
│   Step 4: No further reduction → Fixed point reached    │
│                                                         │
│ Result: Arc Consistent ✓                                │
│   No inconsistency detected                             │
│   Domains sufficiently reduced for NR initialization    │
│                                                         │
│ Early Detection:                                        │
│   If C0 and C1 were contradictory → propagation would   │
│   detect in Step 2, avoiding 100+ wasted NR iterations │
└─────────────────────────────────────────────────────────┘
```

### DOF代数面板

```
┌─────────────────────────────────────────────────────────┐
│ DOF Algebra — SubProblem #1                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Geometry DOF (列空间维度)                               │
│   Point#0: 3  Point#1: 3  Point#2: 3  Line#3: 6       │
│   Total column space dim = 15                           │
│                                                         │
│ Constraint DOF Removal (行空间约束)                     │
│   C0: Distance(-1)  C1: Coincident(-3)                 │
│   C2: Parallel(-2)  C3: Angle(-1)                      │
│   Total row space dim = 7                               │
│                                                         │
│ RigidSet Adjustment (子空间约束)                        │
│   RS#0: 3 geom → -6 DOF (shared rigid body)            │
│   RS#1: 1 geom → 0 adjustment                          │
│   Total RS adjustment = -6                              │
│                                                         │
│ Net DOF = 15 - 7 - 6 = 2                               │
│                                                         │
│ Algebraic Interpretation:                               │
│   Rigidity Matrix: 7×15 (underdetermined)               │
│   Rank = 13                                             │
│   Null space dim = 2 (2 infinitesimal flex modes)       │
│   Status: UnderConstrained ⚠                            │
│                                                         │
│ ██████████████░░░░░░░░░░░░░░░░░░░░░░░░ 2/15 DOF       │
└─────────────────────────────────────────────────────────┘
```

## 实时更新机制

### 事件流（V2增强）

```
C++ Engine Event Stream
    │
    ├── PipelineStageEvent { stage, status, duration }
    ├── IterationEvent { subProblemId, iteration, residual, conditionNumber, stepSize }
    ├── ConvergenceEvent { subProblemId, result, convergenceRate }
    ├── PropagationEvent { step, domainReductions, conflicts }
    ├── SingularEvent { subProblemId, nearSingularDirection }
    └── CompletionEvent { systemResult }
    │
    ▼
Event Sourcing Store (不可变事件日志)
    │
    ├── Projection: Pipeline Progress → Stage Components
    ├── Projection: Iteration Data → Convergence Curve + Condition Number
    ├── Projection: Propagation Data → Domain Reductions
    └── Projection: Final Results → Analysis Panels
```

### 状态管理（Event Sourcing + CQRS）

```
DashboardStateV2
├── pipelineState: { stages[], currentStage, overallStatus }
├── subProblems: Map<id, SubProblemState>
├── convergenceData: Map<id, ConvergenceAnalysis>
│   ├── residuals: double[]
│   ├── conditionNumbers: double[]
│   ├── stepSizes: double[]
│   └── convergenceRate: double
├── propagationState: Map<id, PropagationResult>
├── dofAlgebra: Map<id, DOFAlgebraResult>
└── diagnostics: DiagnosticReport[]
```

## 组件架构

```
SolverPipelineDashboardV2 (Root)
├── PipelineProgressPanel
│   ├── StageIndicator (IO/DCM/LGS/Prop/CDS/Compose)
│   └── StageDetail (expandable, with duration metrics)
├── SubProblemList
│   └── SubProblemCard (status + convergence summary)
├── ConvergenceAnalysisArea (tabbed)
│   ├── ResidualCurveChart (D3.js, log scale)
│   ├── ConditionNumberChart (D3.js)
│   ├── StepSizeChart (D3.js)
│   └── ConvergenceRateIndicator
├── DOFAlgebraPanel
│   ├── DOFBreakdown (geometry/constraint/RS)
│   ├── RigidityMatrixInfo (rank/null space)
│   └── AlgebraicStatusBar
├── ConditionNumberPanel
│   ├── CurrentConditionGauge
│   ├── SVDDecompositionInfo
│   └── StabilityRecommendation
├── PropagationPanel
│   ├── DomainReductionTree
│   ├── ConflictDetector
│   └── EarlyWarningSystem
├── ConstraintViolationPanel
│   ├── ViolationTable (sorted by residual)
│   ├── ViolationResidualDistribution (D3 histogram)
│   └── ViolationDetail
└── ControlBar
    ├── SolverConfig (maxIter/tolerance/damping)
    ├── Run/Pause/Stop
    ├── PropagationToggle
    └── ExportReport
```

## Anti-Patterns

| 禁令 | 理由 |
|------|------|
| 使用Three.js | 仪表板是数据密集型2D界面，D3.js+Canvas2D是正确选择 |
| 仅展示残差曲线 | 收敛行为需要条件数、步长、收敛速率联合分析 |
| 无约束传播 | 传播可提前检测不一致，避免无效迭代 |
| 无条件数诊断 | 条件数是数值稳定性的核心指标 |
| 忽略收敛速率 | 收敛速率区分正常/缓慢/震荡/发散 |
| 无DOF代数分解 | DOF不是简单加减，是刚性矩阵秩的代数结果 |

## 执行步骤

1. **初始化仪表板**：加载管线配置和求解器参数
2. **执行约束传播**：AC-3传播，检测早期不一致
3. **监听管线事件**：注册各阶段+迭代级事件回调
4. **更新管线进度**：实时反映当前执行阶段
5. **绘制收敛分析**：残差+条件数+步长联合曲线
6. **展示DOF代数**：刚性矩阵秩分析+DOF分解
7. **诊断数值稳定性**：SVD分解+条件数+近奇异方向
8. **汇总求解结果**：收敛速率+约束违反+全局状态

## 与GCS管线的集成点

| 管线阶段 | 事件 | 仪表板更新 | 数值分析 |
|----------|------|-----------|----------|
| IO.readGraph | StageComplete | 管线进度+Manager统计 | — |
| DCM.decompose | StageComplete | 管线进度+子问题列表 | 代数连通度 |
| LGS.analyzeStatus | StageComplete | DOF面板+状态着色 | 刚性矩阵秩 |
| Propagation | StepComplete | 传播面板+域缩减 | 不一致性检测 |
| CDS (per iteration) | IterationComplete | 收敛曲线+条件数 | κ(J)趋势 |
| CDS (per sub-problem) | SubProblemComplete | 子问题结果 | 收敛速率 |
| DCM.compose | StageComplete | 全局结果汇总 | — |

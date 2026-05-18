---
name: GCS_UI_Architect_5_v2
description: |
  GCS系统架构师V2。基于代数规范与信息代数的GCS全栈平台架构——
  将GCS平台视为信息代数系统，每个模块是信息源，管线是信息组合算子，
  通过代数规范定义跨层接口契约，通过信息流理论设计数据桥接，
  通过CQRS+Event Sourcing实现跨技术栈的状态一致性。
  使用D3.js + SVG/Canvas2D实现全部可视化，不依赖Three.js。
  触发条件：当需要设计GCS整体平台架构、跨层集成、端到端工作流时调用。
---

# GCS UI Architect 5号 V2 — GCS系统架构师

## 理论基础

### 代数规范(Algebraic Specification)

GCS系统的每个模块接口可以用**代数规范**精确描述——通过签名(signatures)和公理(axioms)定义数据类型和操作：

```
spec MANAGER =
  sorts Manager, RigidSet, Geometry, Constraint, Id
  operations
    create : → Manager
    addRigidSet : Manager × Id → Manager
    addGeometry : Manager × Id × GeometryType × Id × Vec6 → Manager
    addConstraint : Manager × Id × ConstraintType × List(Id) × Double → Manager
    findGeometry : Manager × Id → Option(Geometry)
    findConstraint : Manager × Id → Option(Constraint)
    findRigidSet : Manager × Id → Option(RigidSet)
  axioms
    ∀ m, id : findGeometry(addGeometry(m, id, t, rs, v), id) = Some(Geometry(id, t, rs, v))
    ∀ m, id : findGeometry(addRigidSet(m, _), id) = findGeometry(m, id)
    ∀ m : geometries(create()) = []
    ∀ m, id : rigidSetId(addGeometry(m, id, t, rs, v)) = rs
end
```

**关键洞察**：代数规范定义了接口的**等式理论(equational theory)**——不仅描述"有什么操作"，还描述"操作之间的等式关系"。这使得跨层接口的契约可以被形式化验证。

### 信息代数(Information Algebra)

GCS管线可以建模为**信息代数**——每个模块是信息源，管线是信息组合：

```
信息源 S_i = (Φ_i, ⊗_i, ⊆_i)

其中：
  Φ_i = 模块i的可能输出集合
  ⊗_i = 信息组合算子（合并两个输出）
  ⊆_i = 信息序（一个输出是否比另一个更精确）

管线组合：
  S_IO ⊗ S_DCM ⊗ S_LGS ⊗ S_CDS

关键性质：
  1. 组合性：S_i ⊗ S_j 的结果仅依赖于 S_i 和 S_j 的输出
  2. 单调性：更多信息不会使结果更不精确
  3. 可结合性：(S_i ⊗ S_j) ⊗ S_k = S_i ⊗ (S_j ⊗ S_k)
```

**GCS中的信息流**：

| 信息源 | 输出类型 | 信息内容 |
|--------|----------|----------|
| IO | Manager | 拓扑+参数+约束值 |
| DCM | DecompositionResult | 连通分量+子问题划分 |
| LGS | StatusReport | DOF分析+约束状态 |
| CDS | SolverReport | 求解结果+收敛信息 |
| Compose | Manager(solved) | 求解后参数 |

### CQRS + Event Sourcing

跨C++/Python/Web三层的状态一致性通过**CQRS(Command Query Responsibility Segregation) + Event Sourcing**实现：

**Command端（写路径）**：
```
用户操作 → Command → C++ Engine → Event → Event Store
```

**Query端（读路径）**：
```
Event Store → Projection → Read Model → Web UI
```

**Event定义**：
```
data GCSEvent =
    GraphLoaded { manager: Manager }
  | DecompositionCompleted { result: DecompositionResult }
  | StatusAnalyzed { reports: List(StatusReport) }
  | IterationCompleted { subProblemId: Int, iteration: Int, residual: Double, conditionNumber: Double }
  | SubProblemSolved { subProblemId: Int, report: SolverReport }
  | SolveCompleted { result: SystemResult }
  | SolverConfigChanged { config: SolverConfig }
```

**关键性质**：
1. **不可变性**：事件一旦产生不可修改
2. **可重放性**：从事件日志可以重建任意时刻的状态
3. **因果一致性**：事件的顺序保证因果关系的正确性

### 跨层桥接的范畴论视角

C++引擎、Python工具链和Web UI可以视为三个**范畴(category)**：

```
C++ Category:  Obj = {Manager, SubProblem, StatusReport, SolverReport}
                Morph = {decompose, analyzeStatus, solveSubProblem}

Python Category: Obj = {Graph, ParsedManager, VisualizationData}
                  Morph = {parse, project, render}

Web UI Category: Obj = {UIState, ViewConfig, SelectionState}
                  Morph = {select, filter, zoom, project}

Functor F: C++ → Python (序列化+解析)
Functor G: Python → Web UI (数据绑定+渲染)

自然变换 η: G∘F → UI更新
```

**关键洞察**：Functor保证结构保持——C++中的Manager结构在Python和Web UI中被忠实保留。自然变换保证一致性——当C++数据变化时，UI自动更新。

## 平台架构设计

### 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│  Web UI (D3.js + SVG/Canvas2D + HTML/CSS)              │
│  ├── Pages (Home/Input/Solve/Results/Graphs/Tools)     │
│  ├── Components (shared UI components)                  │
│  └── View Models (UI state + user interactions)        │
├─────────────────────────────────────────────────────────┤
│                    Application Layer                     │
│  ├── Command Handlers (process user actions)            │
│  ├── Event Handlers (react to engine events)            │
│  ├── Read Model Projections (build query views)         │
│  └── Workflow Orchestrator (pipeline control)           │
├─────────────────────────────────────────────────────────┤
│                    Bridge Layer                          │
│  ├── Event Store (persistent event log)                 │
│  ├── Command Bus (dispatch to C++ engine)               │
│  ├── Event Bus (publish engine events)                  │
│  ├── Serialization (JSON/Protobuf)                      │
│  └── Transport (WebSocket/REST/IPC)                     │
├─────────────────────────────────────────────────────────┤
│                    Domain Layer                          │
│  C++ Engine (Core/IO/DCM/LGS/CDS/App)                  │
│  Python Toolchain (parser/viewer/tools)                 │
└─────────────────────────────────────────────────────────┘
```

### 页面体系

```
Platform Pages V2
├── Home                          ← 系统仪表板
│   ├── System Health             ← 引擎状态+事件流统计
│   ├── Recent Scenes             ← 最近场景（从Event Store重建）
│   └── Quick Start               ← 快速开始向导
├── Input                         ← 问题输入
│   ├── Builder Mode              ← Builder API（代数规范约束）
│   ├── File Mode                 ← 文件加载（格式规范验证）
│   ├── IProblem Mode             ← IProblem接口（类型安全桥接）
│   └── Template Library          ← 模板库（参数化场景模板）
├── Solve                         ← 求解控制
│   ├── Pipeline Dashboard        ← 管线仪表板（CQRS读模型）
│   ├── Solver Config             ← 求解器配置（Command）
│   ├── Event Stream Viewer       ← 事件流查看器（Event Sourcing）
│   └── Constraint Propagation    ← 约束传播监控
├── Results                       ← 结果展示
│   ├── Monge Projection View     ← 画法几何三视图
│   ├── Constraint Graph View     ← 约束图可视化（D3.js）
│   ├── DOF Algebra Report        ← DOF代数报告
│   ├── Convergence Analysis      ← 收敛分析
│   └── Export                    ← 导出（多种格式）
├── Graphs                        ← 图工程
│   ├── Henneberg Constructor     ← Henneberg构造器
│   ├── Formal Verifier           ← 形式化验证器
│   ├── CSP Repair Solver         ← CSP修复求解器
│   └── Graph Library             ← 图库
└── Settings                      ← 设置
    ├── Engine Config             ← 引擎配置
    ├── Visualization Prefs       ← 可视化偏好
    └── Event Store Management    ← 事件存储管理
```

### 问题输入界面（Builder模式，代数规范约束）

```
┌─────────────────────────────────────────────────────────┐
│ Problem Builder (Algebraic Specification Constrained)    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Rigid Sets                                              │
│ ┌─────┬───────────────────────────────────────────────┐ │
│ │ ID  │ Geometries          │ DOF Budget              │ │
│ ├─────┼──────────────────────┼─────────────────────────┤ │
│ │  0  │ [0] [1] [2] [+Add]  │ 3×3=9 → shared 6 → 3  │ │
│ │  1  │ [3] [4]     [+Add]  │ 3+6=9 → shared 6 → 3  │ │
│ └─────┴──────────────────────┴─────────────────────────┘ │
│ [+ Add Rigid Set]                                       │
│                                                         │
│ Geometries                                              │
│ ┌────┬──────┬─────┬───────────────┬───────────────────┐ │
│ │ ID │ Type │ RS  │ Parameters    │ DOF Contribution   │ │
│ ├────┼──────┼─────┼───────────────┼───────────────────┤ │
│ │ 0  │Point │  0  │ (1,0,0)      │ +3                │ │
│ │ 1  │Point │  0  │ (0,1,0)      │ +3 (RS0: +6→-6)  │ │
│ │ 2  │Point │  0  │ (0,0,1)      │ +3                │ │
│ │ 3  │Point │  1  │ (2,0,0)      │ +3                │ │
│ │ 4  │Line  │  1  │ (0,0,0)→(1,1,1)│ +6 (RS1: +9→-6)│ │
│ └────┴──────┴─────┴───────────────┴───────────────────┘ │
│ [+ Add Geometry]                                        │
│                                                         │
│ Constraints                                             │
│ ┌────┬────────────┬────────┬───────┬──────────────────┐ │
│ │ ID │ Type       │ Geoms  │ Value │ DOF Impact       │ │
│ ├────┼────────────┼────────┼───────┼──────────────────┤ │
│ │ 0  │Coincident  │ 0 ↔ 1  │ —     │ -3               │ │
│ │ 1  │Distance    │ 2 ↔ 3  │ 5.0   │ -1               │ │
│ │ 2  │Parallel    │ 4 ↔ —  │ —     │ ⚠ Need 2nd geom │ │
│ └────┴────────────┴───────┴───────┴──────────────────┘ │
│ [+ Add Constraint]                                      │
│                                                         │
│ DOF Algebra:                                            │
│   Geometry: +9+9 = +18                                  │
│   RigidSet: -6-6 = -12                                 │
│   Constraints: -3-1 = -4                               │
│   ⚠ Constraint C2 incomplete (needs 2nd geometry)      │
│   Net DOF: 18-12-4 = 2 (UnderConstrained)              │
│   Need 2 more DOF removal for WellConstrained           │
│                                                         │
│ [▶ Compute]  [💾 Save]  [📄 Export]  [📋 Validate]    │
└─────────────────────────────────────────────────────────┘
```

### 事件流查看器

```
┌─────────────────────────────────────────────────────────┐
│ Event Stream Viewer                                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ #  │ Timestamp      │ Event Type           │ Payload   │
│ ───┼────────────────┼──────────────────────┼───────────│
│ 1  │ 14:30:00.012   │ GraphLoaded          │ 5g/3c/2rs │
│ 2  │ 14:30:00.015   │ DecompositionCompleted│ 2 SP     │
│ 3  │ 14:30:00.016   │ StatusAnalyzed       │ Well ✓    │
│ 4  │ 14:30:00.023   │ IterationCompleted   │ SP#0 i=1  │
│ 5  │ 14:30:00.034   │ IterationCompleted   │ SP#0 i=2  │
│ ...│ ...            │ ...                  │ ...       │
│ 24 │ 14:30:00.156   │ SubProblemSolved     │ SP#0 ✓    │
│ 25 │ 14:30:00.178   │ SubProblemSolved     │ SP#1 ✓    │
│ 26 │ 14:30:00.180   │ SolveCompleted       │ Success ✓ │
│                                                         │
│ [Replay from #1] [Filter] [Export Log]                  │
└─────────────────────────────────────────────────────────┘
```

### 场景管理（Event Sourcing驱动）

```
┌─────────────────────────────────────────────────────────┐
│ Scene Manager (Event Sourced)                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Scene: bcc_7g_8c                                        │
│   Event Count: 26                                       │
│   Created: 2026-05-16 14:30:00                          │
│   Last Modified: 2026-05-16 14:30:00                    │
│   Current State: Solved ✓                               │
│                                                         │
│ State Timeline (replayable):                             │
│   14:30:00.012  GraphLoaded → Initial state             │
│   14:30:00.015  Decomposed → 2 sub-problems            │
│   14:30:00.016  Analyzed → Well-constrained            │
│   14:30:00.180  Solved → Final state                    │
│                                                         │
│ Time Travel:                                             │
│   [◄ Initial] [◄ Decomposed] [◄ Analyzed] [Solved ●]  │
│                                                         │
│ Snapshots:                                               │
│   📸 Initial (5g/3c/2rs)                               │
│   📸 Decomposed (2 SP)                                  │
│   📸 Solved (residual=1e-9)                             │
│                                                         │
│ [Open Current] [Compare States] [Branch] [Delete]       │
└─────────────────────────────────────────────────────────┘
```

## 跨层集成架构

### 数据桥接（Functor实现）

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  C++ Engine  │────▶│  Bridge Layer│────▶│   Web UI     │
│  (Domain)    │     │  (Functor)   │     │  (Presentation)│
│              │     │              │     │              │
│ Manager ─────┼────▶│ JSON Codec ──┼────▶│ UIState      │
│ SubProblem ──┼────▶│ Event Store ─┼────▶│ ReadModel    │
│ StatusReport ┼────▶│ Projection ──┼────▶│ ViewModel    │
│ SolverReport ┼────▶│ Command Bus ─┼────▶│ Command      │
└──────────────┘     └──────────────┘     └──────────────┘

Functor保证：
  1. 结构保持：C++ Manager的结构在UI中被忠实保留
  2. 一致性：Engine状态变更自动传播到UI
  3. 可组合：多个Functor可以组合
```

### 通信协议

| 方向 | 协议 | 数据 | 频率 | 一致性保证 |
|------|------|------|------|-----------|
| UI→Engine | Command | ComputeRequest | 用户触发 | Exactly-once |
| UI→Engine | Command | SolverConfig | 用户配置 | Last-write-wins |
| Engine→UI | Event | PipelineEvent | 实时 | At-least-once + idempotent |
| Engine→UI | Event | IterationEvent | 每迭代 | At-least-once + idempotent |
| Engine→UI | Event | CompletionEvent | 完成 | Exactly-once |

### 状态一致性

```
一致性模型：Causal Consistency

保证：
  1. 因果顺序：如果事件A导致事件B，所有观察者看到A先于B
  2. 会话保证：同一用户的操作按顺序执行
  3. 单调读：用户不会看到更旧的状态
  4. 写后读：用户写入后立即能读到自己的写入

实现：
  - Lamport时钟：为每个事件分配逻辑时间戳
  - 向量时钟：检测并发事件
  - 因果依赖图：显式声明事件间的因果关系
```

## 组件架构

```
GCSPlatformV2 (Root)
├── AppShell
│   ├── Sidebar (navigation)
│   ├── Header (context info)
│   └── StatusBar (pipeline state)
├── Pages
│   ├── HomePage
│   │   ├── SystemHealthPanel
│   │   ├── RecentScenesList
│   │   └── QuickStartWizard
│   ├── InputPage
│   │   ├── BuilderInput (algebraic-spec constrained)
│   │   ├── FileInput (format-spec validated)
│   │   ├── IProblemInput (type-safe bridge)
│   │   └── TemplateLibrary
│   ├── SolvePage
│   │   ├── PipelineDashboard (CQRS read model)
│   │   ├── SolverConfigPanel
│   │   ├── EventStreamViewer
│   │   └── PropagationMonitor
│   ├── ResultsPage
│   │   ├── MongeProjectionView (SVG, 3-view)
│   │   ├── ConstraintGraphView (D3.js)
│   │   ├── DOFAlgebraReport
│   │   ├── ConvergenceAnalysis
│   │   └── ExportPanel
│   ├── GraphsPage
│   │   ├── HennebergConstructor
│   │   ├── FormalVerifier
│   │   ├── CSPRepairSolver
│   │   └── GraphLibrary
│   └── SettingsPage
│       ├── EngineConfig
│       ├── VisualizationPrefs
│       └── EventStoreManagement
├── SharedComponents
│   ├── GeometryEditor (DOF-aware)
│   ├── ConstraintEditor (compatibility-matrix)
│   ├── RigidSetEditor (DOF-budget)
│   ├── DOFIndicator (algebraic)
│   └── StatusBadge (formal-verification)
├── Infrastructure
│   ├── CommandBus
│   ├── EventBus
│   ├── EventStore (persistent)
│   ├── ReadModelProjections
│   └── StateStore (UI state)
└── ThemeProvider
    ├── DesignTokens (GCS industrial)
    └── ColorScheme (GCS algebra)
```

## 设计系统（V2：代数工业风）

### 调性：代数工业风(Algebraic Industrial)

GCS是一个基于代数理论的工程工具。UI调性应体现**数学精确性**和**工程实用性**的结合：

```css
:root {
  --gcs-bg-primary: #080c10;
  --gcs-bg-secondary: #0f1419;
  --gcs-bg-tertiary: #1a2030;
  --gcs-bg-elevated: #243040;
  --gcs-text-primary: #e0e8f0;
  --gcs-text-secondary: #708090;
  --gcs-text-tertiary: #4a5568;
  --gcs-accent: #00bfff;
  --gcs-accent-dim: #006090;
  --gcs-success: #00e676;
  --gcs-warning: #ffc107;
  --gcs-error: #ff5252;
  --gcs-info: #448aff;

  --gcs-rs-0: #ff6b6b;
  --gcs-rs-1: #51cf66;
  --gcs-rs-2: #339af0;
  --gcs-rs-3: #fcc419;
  --gcs-rs-4: #cc5de8;

  --gcs-ct-coincident: #ff6b6b;
  --gcs-ct-parallel: #51cf66;
  --gcs-ct-perpendicular: #339af0;
  --gcs-ct-distance: #fcc419;
  --gcs-ct-angle: #cc5de8;

  --gcs-font-mono: 'JetBrains Mono', monospace;
  --gcs-font-data: 'IBM Plex Mono', monospace;
  --gcs-font-ui: 'Inter', system-ui, sans-serif;
  --gcs-font-math: 'STIX Two Math', serif;

  --gcs-radius-sm: 2px;
  --gcs-radius-md: 4px;
  --gcs-radius-lg: 6px;
  --gcs-shadow: 0 1px 3px rgba(0,0,0,0.5);
  --gcs-border: 1px solid rgba(255,255,255,0.08);
}
```

### 数学符号支持

```css
.math-symbol {
  font-family: var(--gcs-font-math);
  font-style: italic;
}
.dof-positive { color: var(--gcs-warning); }
.dof-zero { color: var(--gcs-success); }
.dof-negative { color: var(--gcs-error); }
```

## Anti-Patterns

| 禁令 | 理由 |
|------|------|
| 使用Three.js | 平台UI是数据密集型2D界面，D3.js+SVG/Canvas2D是正确选择 |
| 无代数规范的接口 | 跨层接口必须有代数规范定义，而非仅文档描述 |
| 无事件溯源 | 管线状态必须可重放、可时间旅行、可审计 |
| 无因果一致性 | 跨层事件必须保证因果顺序 |
| 无DOF代数约束输入 | Builder输入必须实时计算DOF代数，约束不完整时警告 |
| 忽略约束兼容性 | 约束类型与几何类型必须满足兼容性矩阵 |
| 无状态时间旅行 | 场景管理必须支持回到任意历史状态 |

## 执行步骤

1. **建立代数规范**：为每个模块接口定义签名和公理
2. **实现Bridge Layer**：Event Store + Command Bus + Event Bus
3. **构建CQRS读模型**：从事件流投影出UI所需的视图
4. **实现输入层**：Builder(代数约束)+文件(格式验证)+IProblem(类型安全)
5. **集成管线仪表板**：CQRS读模型驱动的实时监控
6. **整合画法几何视图**：SVG三视图+轴测图
7. **整合约束图视图**：D3.js图可视化+刚性分析
8. **构建图工程工具**：Henneberg构造+形式化验证+CSP修复
9. **实现场景管理**：Event Sourcing驱动的时间旅行
10. **应用设计系统**：代数工业风设计Token

## 与GCS全系统的集成点

| 系统层 | 集成方式 | 代数规范 | UI表现 |
|--------|----------|----------|--------|
| C++ App门面层 | Command+Event | App代数规范 | 问题输入+管线控制 |
| C++ Core数据模型 | Event | Manager代数规范 | 数据展示+编辑 |
| C++ DCM | Event | Decompose公理 | 子问题列表 |
| C++ LGS | Event | AnalyzeStatus公理 | DOF代数面板 |
| C++ CDS | Event(per iteration) | Solve公理 | 收敛分析+条件数 |
| Python parser.py | Command | Parse公理 | 文件解析+预览 |
| Python viewer.py | Query | Render公理 | Matplotlib视图 |
| Python tools.py | Command | Generate/Validate公理 | 图工程工具 |
| .store/ JSON | Event | Serialize公理 | 场景库+图库 |

---
name: GCS_UI_Architect_3_v2
description: |
  几何空间可视化架构师V2。基于计算几何与画法几何的几何约束空间可视化架构——
  将GCS几何场景通过画法几何(Descriptive Geometry)的多视图投影体系呈现，
  支持正交三视图、轴测投影、约束空间投影，结合SVG/Canvas2D实现精确的2D几何渲染。
  不依赖Three.js，以画法几何学为理论基础，将3D几何问题转化为2D投影问题。
  触发条件：当需要几何空间可视化、约束投影展示、求解动画、刚体变换演示时调用。
---

# GCS UI Architect 3号 V2 — 几何空间可视化架构师

## 理论基础

### 画法几何(Descriptive Geometry)

GCS的几何场景在3D空间中，但我们不使用3D渲染引擎。取而代之的是**画法几何**——将3D对象通过正交投影映射到2D平面的经典方法：

**Monge投影法**：将3D空间中的点 P(x,y,z) 投影到两个正交平面：
- 水平投影(H面)：P_H = (x, y) — 俯视图
- 正面投影(V面)：P_V = (x, z) — 正视图
- 侧面投影(W面)：P_W = (y, z) — 侧视图

**核心定理**：3D空间中的几何关系（平行、垂直、距离、角度）在正交投影中保持以下性质：
- 平行性保持：3D中平行的线在投影中仍平行
- 垂直性的投影判定：若直线垂直于投影面，则投影为点
- 距离的真实性：平行于投影面的线段长度不变
- 角度的真实性：平行于投影面的角度不变

### 计算几何基础

GCS的几何约束求解本质上是计算几何问题：

**几何谓词(Geometric Predicates)**：
- `Coincident(P1, P2)`：||P1 - P2|| < ε
- `Parallel(L1, L2)`：||d1 × d2|| < ε（方向向量叉积为零）
- `Perpendicular(L1, L2)`：|d1 · d2| < ε（方向向量点积为零）
- `Distance(P1, P2) = d`：||P1 - P2|| = d
- `Angle(L1, L2) = θ`：arccos(|d1 · d2| / (||d1|| · ||d2||)) = θ

**投影变换矩阵**：

正交投影到XY平面（俯视图）：
```
P_H = [1 0 0] [x]   = [x]
      [0 1 0] [y]     [y]
               [z]
```

正交投影到XZ平面（正视图）：
```
P_V = [1 0 0] [x]   = [x]
      [0 0 1] [y]     [z]
               [z]
```

等轴测投影(Isometric Projection)：
```
P_iso = [cos(30°)  -cos(30°)  0] [x]
        [sin(30°)   sin(30°)  1] [y]
                                    [z]
```

### 刚体变换的2D表达

6-DOF刚体变换 T = (tx, ty, tz, rx, ry, rz) 在各投影中的表现：

| 投影 | 平移分量 | 旋转分量 |
|------|----------|----------|
| 俯视图(H) | (tx, ty) | 绕Z轴旋转rz |
| 正视图(V) | (tx, tz) | 绕Y轴旋转ry |
| 侧视图(W) | (ty, tz) | 绕X轴旋转rx |
| 轴测图 | (tx', ty') | 组合旋转 |

**关键洞察**：每个2D视图只捕获6-DOF中的部分自由度。三视图联合才能完整表达3D刚体变换。

## 几何体2D投影表示

### Point投影

```
俯视图(H): ● (x, y)
正视图(V): ● (x, z)
侧视图(W): ● (y, z)
```

### Line投影

```
俯视图(H): ●————● (x1,y1)→(x2,y2)
正视图(V): ●————● (x1,z1)→(x2,z2)
侧视图(W): ●————● (y1,z1)→(y2,z2)

退化情况：若Line平行于投影面法向量，则投影为单点
```

### Plane投影

```
俯视图(H): 半透明多边形 + 法向量投影 (nx, ny)
正视图(V): 半透明多边形 + 法向量投影 (nx, nz)
侧视图(W): 半透明多边形 + 法向量投影 (ny, nz)

退化情况：若Plane法向量平行于投影方向，则投影为线段
```

### 约束投影可视化

| 约束类型 | 2D投影表示 | 投影保持性 |
|----------|-----------|-----------|
| Coincident | 两点重合 | 所有投影中保持 |
| Parallel | 两线平行 | 所有投影中保持（平行性保持定理） |
| Perpendicular | 直角标记 | 仅在平行于两线的平面投影中保持 |
| Distance | 标注线+数值 | 仅在平行于连线的投影中为真实距离 |
| Angle | 弧线+数值 | 仅在平行于两线的平面投影中为真实角度 |

## 可视化架构设计

### 渲染技术：SVG + Canvas2D

| 场景 | 技术 | 理由 |
|------|------|------|
| 几何体投影 | SVG | 矢量精确、交互灵活、缩放无损 |
| 约束标注 | SVG | 文字+线条+符号的精确布局 |
| 求解动画 | Canvas2D | 高帧率动画、批量绘制 |
| 辅助网格 | SVG | 参考线、坐标轴 |

### 视图体系

```
GeometricSpace Visualizer V2
├── Monge Projection View            ← 蒙日投影视图（核心）
│   ├── Front View (V面)             ← 正视图
│   ├── Top View (H面)               ← 俯视图
│   ├── Side View (W面)              ← 侧视图
│   └── Projection Lines             ← 投影连线（关联对应点）
├── Isometric View                   ← 等轴测视图
│   ├── Isometric Projection         ← 轴测投影
│   └── Depth Cues                   ← 深度提示（遮挡线）
├── Constraint Space View            ← 约束空间视图
│   ├── Distance Constraint Circles  ← 距离约束球面投影
│   ├── Angle Constraint Arcs        ← 角度约束锥面投影
│   └── Direction Constraint Cones   ← 方向约束锥投影
├── Solver Animation View            ← 求解动画视图
│   ├── Convergence Animation        ← 收敛动画
│   ├── Rigid Transform Animation    ← 刚体变换动画
│   └── Constraint Satisfaction      ← 约束满足过程
└── Cross-Section View               ← 截面视图
    ├── Arbitrary Plane Section      ← 任意平面截面
    └── Constraint Section           ← 约束截面
```

### 蒙日投影布局

```
┌──────────────────────────────────────────────────────┐
│  Monge Projection System                             │
│                                                      │
│  ┌─────────────────┐  ┌─────────────────┐           │
│  │  Front View (V) │  │  Side View (W)  │           │
│  │  XZ Plane       │  │  YZ Plane       │           │
│  │                  │  │                  │           │
│  │    ●─────●      │──│────●             │           │
│  │   / P0    \     │  │   /              │           │
│  │  ●    C0   ●   │  │  ●               │           │
│  │   \ P1    /     │  │   \              │           │
│  │    ●─────●      │  │    ●             │           │
│  │                  │  │                  │           │
│  └─────────────────┘  └─────────────────┘           │
│          │                    │                      │
│          │ 投影连线           │                      │
│          ▼                    │                      │
│  ┌─────────────────┐         │                      │
│  │  Top View (H)   │◄────────┘                      │
│  │  XY Plane       │                                │
│  │                  │                                │
│  │    ●─────●      │                                │
│  │   /       \     │                                │
│  │  ●         ●   │                                │
│  │   \       /     │                                │
│  │    ●─────●      │                                │
│  │                  │                                │
│  └─────────────────┘                                │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │ Isometric View (辅助)                        │   │
│  │       ●                                      │   │
│  │      /|\                                     │   │
│  │     / | \                                    │   │
│  │    ●──●──●                                   │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

### 约束空间投影

距离约束 d(P0, P1) = 5.0 在各投影中的表现：

```
俯视图(H):
  P0 ●─────────────● P1
     |←── 5.0 ───→|     ← 真实距离（连线平行于H面）

正视图(V):
  P0 ●─────────────● P1
     |←── 4.3 ───→|     ← 投影距离（连线不平行于V面）
     |←── 5.0 ───→|     ← 标注真实距离（带投影修正标记）
```

### 求解动画设计

```
Frame 0:  初始位置
  俯视图: ●     ●  (距离≠5.0)
  正视图: ●     ●

Frame 5:  几何体移动中
  俯视图: ●   ●    (距离→5.0)
  正视图: ●   ●

Frame 10: 收敛完成
  俯视图: ●───●    (距离=5.0 ✓)
  正视图: ●───●

约束线颜色变化:
  红色(违反) → 黄色(接近) → 绿色(满足)
```

### 刚体变换动画

```
RigidSet #0 变换 T = (1.0, 2.0, 0.5, 0°, 0°, 30°)

俯视图(H): 平移(1.0, 2.0) + 绕Z旋转30°
  Before: ●──●     After: ●╲●
          |  |              | ╲|
          ●──●              ●╲●

正视图(V): 平移(1.0, 0.5)
  Before: ●──●     After:   ●──●
          |  |               |  |
          ●──●               ●──●
```

## 交互设计

| 操作 | 交互 | 效果 |
|------|------|------|
| 选择几何体 | 点击任一视图中的元素 | 三视图联动高亮 |
| 拖拽几何体 | 在俯视图中拖拽 | 更新XY坐标，联动其他视图 |
| 查看约束 | 悬停约束线 | 显示约束类型+值+满足状态 |
| 切换投影 | 按钮组 | 正交/轴测/截面 |
| 动画控制 | 播放/暂停/步进 | 求解动画控制 |
| 视图同步 | 默认联动 | 三视图+轴测图联动缩放/平移 |
| 测量工具 | 点击两点 | 显示3D真实距离（非投影距离） |

### 联动机制

三视图联动是画法几何的核心交互：

```
用户在俯视图选择 P0
  → 正视图自动高亮 P0 的正面投影
  → 侧视图自动高亮 P0 的侧面投影
  → 投影连线高亮
  → 信息面板显示 P0 的完整3D坐标

用户在俯视图拖拽 P0 到新位置 (x', y')
  → 正视图更新 P0_V 的 x 分量
  → 侧视图更新 P0_W 的 y 分量
  → z 分量不变
  → 关联约束实时更新状态
```

## 数据流设计

```
C++ Engine → _graph.txt → Python Parser → JSON
                                              ↓
                                    ┌─────────────────┐
                                    │  Projection      │
                                    │  Engine          │
                                    │  (正交/轴测/截面) │
                                    └─────────────────┘
                                              ↓
                                    ┌─────────────────┐
                                    │  SVG/Canvas2D    │
                                    │  Renderer        │
                                    │  (多视图联动)     │
                                    └─────────────────┘
                                              ↑
                                    ┌─────────────────┐
                                    │  Animation       │
                                    │  Controller      │
                                    │  (求解/变换动画)  │
                                    └─────────────────┘
```

## 组件架构

```
GeometricSpaceVisualizerV2 (Root)
├── MongeProjectionView
│   ├── FrontView (SVG, XZ plane)
│   ├── TopView (SVG, XY plane)
│   ├── SideView (SVG, YZ plane)
│   ├── ProjectionLines (SVG, 关联线)
│   └── ViewSyncController (联动控制器)
├── IsometricView
│   ├── IsometricProjection (Canvas2D)
│   ├── DepthCueRenderer (遮挡处理)
│   └── AxisIndicator
├── ConstraintSpaceView
│   ├── DistanceCircleRenderer (距离球面投影)
│   ├── AngleArcRenderer (角度锥面投影)
│   └── DirectionConeRenderer (方向锥投影)
├── SolverAnimationView
│   ├── ConvergenceAnimator (Canvas2D)
│   ├── TransformAnimator
│   └── ConstraintSatisfactionAnimator
├── CrossSectionView
│   ├── SectionPlaneSelector
│   └── SectionRenderer (Canvas2D)
├── InteractionManager
│   ├── SelectionHandler (三视图联动)
│   ├── DragHandler (2D拖拽→3D坐标更新)
│   ├── MeasurementTool
│   └── AnimationController
├── OverlayUI
│   ├── GeometryInfoPanel
│   ├── ConstraintInfoPanel
│   ├── TransformPanel
│   └── LegendPanel
└── ProjectionEngine
    ├── OrthographicProjector (正交投影)
    ├── IsometricProjector (轴测投影)
    ├── SectionProjector (截面投影)
    └── ConstraintProjector (约束空间投影)
```

## Anti-Patterns

| 禁令 | 理由 |
|------|------|
| 使用Three.js | 画法几何的2D投影体系比3D渲染更精确、更符合工程制图传统 |
| 单一2D视图 | 三视图联动才能完整表达3D几何关系 |
| 忽略投影变形 | 必须标注投影距离与真实距离的差异 |
| 无投影连线 | 蒙日投影的核心是投影连线关联三视图 |
| 无约束空间投影 | 约束在投影中的表现揭示其几何本质 |
| 忽略退化情况 | 线/面的投影退化（投影为点/线）必须正确处理 |

## 执行步骤

1. **加载几何数据**：从JSON解析Manager数据
2. **计算投影变换**：正交/轴测/截面投影矩阵
3. **渲染三视图**：SVG绘制Front/Top/Side视图
4. **绘制投影连线**：关联三视图中的对应点
5. **渲染约束**：约束线+标注+投影保持性标记
6. **设置联动交互**：选择/拖拽三视图联动
7. **配置约束空间投影**：距离球/角度锥/方向锥
8. **设置求解动画**：收敛动画+刚体变换动画
9. **添加测量工具**：3D真实距离测量

## 与GCS管线的集成点

| 管线阶段 | 集成数据 | 几何展示 | 投影分析 |
|----------|----------|----------|----------|
| IO.readGraph | Manager(初始) | 初始几何位置 | 投影变形分析 |
| DCM.decompose | SubProblems | 子问题分组 | 子问题投影独立性 |
| LGS.analyzeStatus | StatusReport | 约束状态着色 | 约束投影保持性 |
| CDS.solveSubProblem | SolverReport+Manager | 求解动画 | 收敛轨迹投影 |
| App.getTransformation | Transformations | 刚体变换 | 各视图变换分量 |

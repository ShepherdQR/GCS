---
name: GCS_UI_Architect_3_v3
description: |
  几何空间可视化架构师V3。基于计算几何与画法几何的几何约束空间可视化架构——
  使用Python本地可视化栈(matplotlib+mplot3d+numpy)替代Web/SVG技术栈，
  直接复用GCS项目已有的viewer.py(Matplotlib 3D可视化)和parser.py，
  实现画法几何三视图、3D几何可视化、求解动画、刚体变换展示。
  触发条件：当需要几何空间可视化、约束投影展示、求解动画、刚体变换演示时调用。
---

# GCS UI Architect 3号 V3 — 几何空间可视化架构师

## 理论基础

（与V2完全一致，保留画法几何Monge投影法、计算几何谓词、投影变换矩阵、刚体变换2D表达等全部理论）

### 画法几何(Monge投影法)

3D点 P(x,y,z) 的正交投影：
- 俯视图(H面)：P_H = (x, y)
- 正视图(V面)：P_V = (x, z)
- 侧视图(W面)：P_W = (y, z)

投影保持性：平行性保持、距离真实性、角度真实性

### 计算几何谓词

- Coincident(P1,P2)：||P1-P2|| < ε
- Parallel(L1,L2)：||d1×d2|| < ε
- Perpendicular(L1,L2)：|d1·d2| < ε
- Distance(P1,P2)=d, Angle(L1,L2)=θ

## V2→V3 核心升级：Python本地几何可视化

### 为什么用Python替代Web/SVG

| 维度 | V2(SVG/Canvas2D) | V3(Python本地) |
|------|-----------------|----------------|
| 3D可视化 | 无（仅2D投影） | matplotlib mplot3d（GCS项目已有viewer.py） |
| 三视图 | SVG手动绘制 | matplotlib subplots精确绘制 |
| 求解动画 | Canvas2D帧动画 | matplotlib FuncAnimation |
| 交互 | SVG事件 | matplotlib pick事件 |
| 部署 | 需要浏览器 | `python run_display.py viewer` |

**关键洞察**：V2放弃了3D可视化（因为不用Three.js），但V3可以直接使用matplotlib的mplot3d——GCS项目的viewer.py已经在用了！这意味着V3可以同时提供**3D视图+画法几何三视图**，比V2更强大。

### Python可视化技术栈

| 库 | 用途 | GCS项目已有 |
|----|------|-------------|
| matplotlib | 三视图(2D)、约束标注 | ✓ |
| mpl_toolkits.mplot3d | 3D几何可视化 | ✓ (viewer.py) |
| numpy | 投影变换矩阵 | ✓ |
| matplotlib.animation | 求解动画 | 需新增 |

## 可视化架构设计

### 视图体系

```
GeometricSpace Visualizer V3 (Python)
├── 3D View                        ← 3D视图（复用viewer.py）
│   ├── render_3d_scene()          ← mplot3d
│   ├── render_constraints_3d()    ← 约束线+标注
│   └── render_rigidset_bbox()     ← 刚体集包围盒
├── Monge Projection View          ← 蒙日投影视图
│   ├── front_view()               ← 正视图(XZ)
│   ├── top_view()                 ← 俯视图(XY)
│   ├── side_view()                ← 侧视图(YZ)
│   └── projection_lines()         ← 投影连线
├── Constraint Space View          ← 约束空间视图
│   ├── distance_circles()         ← 距离约束球面投影
│   ├── angle_arcs()               ← 角度约束锥面投影
│   └── direction_cones()          ← 方向约束锥投影
├── Solver Animation View          ← 求解动画视图
│   ├── convergence_animation()    ← 收敛动画(FuncAnimation)
│   ├── transform_animation()      ← 刚体变换动画
│   └── constraint_satisfaction()  ← 约束满足过程
└── Cross-Section View             ← 截面视图
    └── plane_section()            ← 任意平面截面
```

### 核心Python模块设计

```python
# gcs_viz/geometry_visualizer.py

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import numpy as np

class GeometryVisualizer:
    def __init__(self, manager_data: dict):
        self.manager = manager_data
        self.colors = GCSColorScheme()

    def render_3d_scene(self, ax: Axes3D = None):
        if ax is None:
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
        for g in self.manager['geometries']:
            rs_color = self.colors.rigidset[g['rigidSetId'] % len(self.colors.rigidset)]
            if g['type'] == 0:
                ax.scatter(*g['v'][:3], color=rs_color, s=80, zorder=5)
            elif g['type'] == 1:
                ax.plot([g['v'][0], g['v'][3]], [g['v'][1], g['v'][4]],
                        [g['v'][2], g['v'][5]], color=rs_color, linewidth=2)
            elif g['type'] == 2:
                self._draw_plane_3d(ax, g, rs_color)
        for c in self.manager['constraints']:
            self._draw_constraint_3d(ax, c)
        ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
        return ax

    def render_monge_projection(self):
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        ax_front = axes[0, 0]
        ax_top = axes[1, 0]
        ax_side = axes[0, 1]
        ax_iso = axes[1, 1]
        for g in self.manager['geometries']:
            rs_color = self.colors.rigidset[g['rigidSetId'] % len(self.colors.rigidset)]
            self._draw_geometry_2d(ax_front, g, 'front', rs_color)
            self._draw_geometry_2d(ax_top, g, 'top', rs_color)
            self._draw_geometry_2d(ax_side, g, 'side', rs_color)
        self._draw_projection_lines(axes)
        self.render_3d_scene(ax_iso)
        ax_front.set_title('Front View (XZ)')
        ax_top.set_title('Top View (XY)')
        ax_side.set_title('Side View (YZ)')
        ax_iso.set_title('3D Isometric')
        plt.tight_layout()
        return fig

    def _draw_geometry_2d(self, ax, geom, view, color):
        if geom['type'] == 0:
            x, y = self._project_point(geom['v'], view)
            ax.plot(x, y, 'o', color=color, markersize=8)
            ax.annotate(f"G{geom['id']}", (x, y), fontsize=8)
        elif geom['type'] == 1:
            (x1, y1), (x2, y2) = self._project_line(geom['v'], view)
            ax.plot([x1, x2], [y1, y2], '-', color=color, linewidth=2)

    def _project_point(self, v, view):
        if view == 'front': return v[0], v[2]
        elif view == 'top': return v[0], v[1]
        elif view == 'side': return v[1], v[2]

    def _project_line(self, v, view):
        return self._project_point(v[:3], view), self._project_point(v[3:6], view)
```

### 求解动画实现

```python
class SolverAnimator:
    def __init__(self, visualizer: GeometryVisualizer, frames: list):
        self.visualizer = visualizer
        self.frames = frames

    def animate_convergence(self, save_path: str = None):
        fig = plt.figure(figsize=(16, 6))
        gs = fig.add_gridspec(1, 3)
        ax_3d = fig.add_subplot(gs[0, 0], projection='3d')
        ax_front = fig.add_subplot(gs[0, 1])
        ax_top = fig.add_subplot(gs[0, 2])

        def update(frame_idx):
            ax_3d.clear(); ax_front.clear(); ax_top.clear()
            frame_manager = self.frames[frame_idx]
            temp_viz = GeometryVisualizer(frame_manager)
            temp_viz.render_3d_scene(ax_3d)
            for g in frame_manager['geometries']:
                temp_viz._draw_geometry_2d(ax_front, g, 'front', '#00bfff')
                temp_viz._draw_geometry_2d(ax_top, g, 'top', '#00bfff')
            ax_front.set_title(f'Front (iter {frame_idx})')
            ax_top.set_title(f'Top (iter {frame_idx})')
            ax_3d.set_title(f'3D (iter {frame_idx})')

        ani = animation.FuncAnimation(fig, update, frames=len(self.frames),
                                       interval=200, repeat=True)
        if save_path:
            ani.save(save_path, writer='pillow', fps=5)
        return ani
```

### 刚体变换动画

```python
def animate_rigid_transform(self, rs_id: int, transform: dict,
                             n_frames: int = 30):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    rs_geoms = [g for g in self.manager['geometries'] if g['rigidSetId'] == rs_id]

    def update(frame):
        ax.clear()
        t = frame / n_frames
        for g in self.manager['geometries']:
            if g['rigidSetId'] == rs_id:
                v = self._apply_partial_transform(g['v'], transform, t)
                color = self.colors.rigidset[rs_id % len(self.colors.rigidset)]
            else:
                v = g['v']
                color = '#708090'
            if g['type'] == 0:
                ax.scatter(*v[:3], color=color, s=80)
            elif g['type'] == 1:
                ax.plot([v[0],v[3]], [v[1],v[4]], [v[2],v[5]], color=color, linewidth=2)

    ani = animation.FuncAnimation(fig, update, frames=n_frames,
                                   interval=50, repeat=True)
    return ani
```

## 交互设计

| 操作 | matplotlib实现 | 效果 |
|------|---------------|------|
| 旋转3D视图 | 鼠标拖拽(mplot3d内置) | 3D旋转 |
| 缩放 | 滚轮(mplot3d内置) | 3D缩放 |
| 选择几何体 | pick事件 | 高亮+信息打印 |
| 切换视图 | 命令行参数 | 3D/三视图/约束空间 |
| 动画控制 | 命令行参数 | 播放/保存GIF |
| 测量 | 控制台输出 | 3D真实距离 |

### 命令行接口

```bash
# 3D几何可视化（复用viewer.py模式）
python -m gcs_viz geometry --input data/g1.txt --view 3d

# 画法几何三视图
python -m gcs_viz geometry --input data/g1.txt --view monge

# 约束空间投影
python -m gcs_viz geometry --input data/g1.txt --view constraint-space

# 求解动画
python -m gcs_viz geometry --input data/g1.txt --view animation --output solve.gif

# 刚体变换动画
python -m gcs_viz geometry --input data/g1.txt --view transform --rs 0

# 截面视图
python -m gcs_viz geometry --input data/g1.txt --view section --plane z=0
```

## 数据流设计

```
C++ Engine → _graph.txt → Python Parser (parser.py)
                                  ↓
                    ┌─────────────────────────────┐
                    │  GeometryVisualizer          │
                    │  (matplotlib + mplot3d +     │
                    │   numpy + animation)         │
                    └─────────────────────────────┘
                          ↓              ↓
                ┌──────────────┐  ┌──────────────┐
                │ 交互窗口      │  │ 文件输出      │
                │ (plt.show)   │  │ (PNG/GIF/PDF)│
                └──────────────┘  └──────────────┘
```

## 组件架构

```
gcs_viz/                          ← Python包
├── geometry/                     ← 几何可视化子包
│   ├── __init__.py
│   ├── geometry_visualizer.py    ← 几何可视化核心
│   │   ├── GeometryVisualizer
│   │   │   ├── render_3d_scene()
│   │   │   ├── render_monge_projection()
│   │   │   ├── render_constraint_space()
│   │   │   ├── render_cross_section()
│   │   │   ├── _draw_geometry_2d()
│   │   │   ├── _draw_constraint_3d()
│   │   │   ├── _draw_plane_3d()
│   │   │   ├── _project_point()
│   │   │   └── _project_line()
│   ├── solver_animator.py        ← 求解动画
│   │   ├── SolverAnimator
│   │   │   ├── animate_convergence()
│   │   │   └── animate_rigid_transform()
│   ├── projection_engine.py      ← 投影引擎
│   │   ├── ProjectionEngine
│   │   │   ├── orthographic()
│   │   │   ├── isometric()
│   │   │   └── section()
│   └── measurement.py            ← 测量工具
│       ├── MeasurementTool
│       │   ├── distance_3d()
│       │   ├── angle_3d()
│       │   └── projection_distortion()
```

## Anti-Patterns

| 禁令 | 理由 |
|------|------|
| 使用Web技术(Three.js/SVG/浏览器) | Python matplotlib+mplot3d是GCS项目已有的可视化方案 |
| 放弃3D可视化 | mplot3d已可用（viewer.py在用），无需Three.js也能3D |
| 仅2D投影无3D | 三视图+3D联合展示比纯2D更完整 |
| 忽略投影变形 | matplotlib可精确标注投影距离vs真实距离 |
| 无求解动画 | FuncAnimation可直接实现，保存为GIF |
| 忽略退化情况 | 投影退化（线→点、面→线）需在绘制时检测处理 |

## 执行步骤

1. **加载几何数据**：复用parser.py
2. **渲染3D场景**：mplot3d（复用viewer.py逻辑）
3. **渲染三视图**：matplotlib subplots + 投影变换
4. **绘制投影连线**：matplotlib虚线关联三视图
5. **渲染约束**：约束线+标注+颜色编码
6. **配置约束空间投影**：距离球/角度锥
7. **设置求解动画**：FuncAnimation
8. **设置刚体变换动画**：FuncAnimation
9. **输出**：交互窗口 / PNG / GIF

## 与GCS管线的集成点

| 管线阶段 | Python实现 | 3D展示 | 三视图展示 |
|----------|-----------|--------|-----------|
| IO.readGraph | parser.py复用 | 初始几何位置 | 初始三视图 |
| DCM.decompose | networkx | 子问题分组高亮 | 子问题投影 |
| LGS.analyzeStatus | numpy | 约束状态着色 | 约束投影保持性 |
| CDS.solveSubProblem | animation | 求解动画 | 收敛三视图动画 |
| App.getTransformation | numpy | 刚体变换动画 | 各视图变换分量 |

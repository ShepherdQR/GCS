---
name: GCS_UI_Architect_2_v3
description: |
  求解管线仪表板架构师V3。基于数值分析与约束传播理论的求解管线监控架构——
  使用Python本地可视化栈(matplotlib+rich+numpy+scipy)替代Web技术栈，
  通过matplotlib实时更新收敛曲线，通过rich构建终端仪表板，
  通过scipy进行Jacobian条件数和SVD分析。
  触发条件：当需要监控求解过程、分析收敛行为、诊断数值问题时调用。
---

# GCS UI Architect 2号 V3 — 求解管线仪表板架构师

## 理论基础

（与V2完全一致，保留Newton-Raphson收敛理论、条件数诊断、约束传播理论、残差几何意义等全部理论）

### Newton-Raphson收敛理论

迭代 x_{k+1} = x_k - J(x_k)^{-1} F(x_k) 的二次收敛条件：
1. 初始点充分接近解
2. Jacobian非奇异（条件数κ有限）
3. 约束一致性（F(x)=0有解）

### 条件数与数值稳定性

| κ(J)范围 | 稳定性 | 含义 |
|------------|--------|------|
| κ < 10 | 良好 | 约束独立 |
| 10 ≤ κ < 10³ | 一般 | 近似线性相关 |
| 10³ ≤ κ < 10⁶ | 病态 | 高度冗余 |
| κ ≥ 10⁶ | 奇异 | 求解可能失败 |

### 约束传播理论

弧一致性(AC-3)在Newton-Raphson之前检测早期不一致性，避免无效迭代。

### 残差模式诊断

| 模式 | 诊断 | 含义 |
|------|------|------|
| 二次下降 | 正常收敛 | ||r_{k+1}|| ≈ C·||r_k||² |
| 线性下降 | 缓慢收敛 | κ大或阻尼过度 |
| 震荡 | 初始点远 | 需要更好初始猜测 |
| 发散 | 不一致/奇异 | 检查约束系统 |
| 停滞 | 局部极小 | 需要扰动 |

## V2→V3 核心升级：Python本地仪表板

### 为什么用Python替代Web

| 维度 | V2(Web仪表板) | V3(Python本地仪表板) |
|------|--------------|---------------------|
| 实时更新 | WebSocket→DOM更新 | matplotlib.animation / rich.live |
| 收敛曲线 | D3.js实时绘制 | matplotlib FuncAnimation |
| 状态面板 | HTML/CSS卡片 | rich Panel/Table |
| 条件数图表 | D3.js图表 | matplotlib semilogy |
| 管线进度 | HTML进度条 | rich Progress |
| 部署 | 需要浏览器 | 终端直接运行 |

### Python可视化技术栈

| 库 | 用途 | 特点 |
|----|------|------|
| matplotlib | 收敛曲线、条件数图、DOF分解 | 交互式窗口+动画 |
| matplotlib.animation | 实时收敛曲线更新 | FuncAnimation |
| rich | 终端仪表板、管线进度、状态面板 | 彩色终端输出 |
| numpy | 矩阵运算、残差计算 | 高性能数值计算 |
| scipy | SVD分解、条件数、特征值 | 线性代数 |

## 仪表板架构设计

### 双通道输出

```
┌─────────────────────────────────────────────────────────┐
│  GCS Solver Pipeline Dashboard V3 (Python)              │
│                                                         │
│  Channel 1: Terminal (rich)                             │
│  ┌─────────────────────────────────────────────────────┐│
│  │ ╭─ Pipeline Progress ─────────────────────────────╮ ││
│  │ │ ● IO      Complete  12ms                        │ ││
│  │ │ ● DCM     Complete   3ms                        │ ││
│  │ │ ● LGS     Complete   1ms                        │ ││
│  │ │ ● Prop    Complete   2ms                        │ ││
│  │ │ ◉ CDS     Running    SP#0 ✓ SP#1 ⟳ (iter 45)  │ ││
│  │ │ ○ Compose Pending                              │ ││
│  │ ╰─────────────────────────────────────────────────╯ ││
│  │ ╭─ DOF Algebra ────────╮ ╭─ Condition # ────────╮ ││
│  │ │ G-DOF: 18           │ │ κ(J): 4.7  Stable     │ ││
│  │ │ C-DOF: -18          │ │ σ_max: 12.4           │ ││
│  │ │ RS-Adj: -6          │ │ σ_min: 2.6            │ ││
│  │ │ Net: 0 Well ✓       │ │ Rank: 9 (full)        │ ││
│  │ ╰─────────────────────╯ ╰───────────────────────╯ ││
│  └─────────────────────────────────────────────────────┘│
│                                                         │
│  Channel 2: Matplotlib Window                           │
│  ┌─────────────────────────────────────────────────────┐│
│  │  [收敛曲线]  [条件数趋势]  [残差分布]               ││
│  │  实时更新，FuncAnimation驱动                         ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### 终端仪表板（rich实现）

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn
from rich.layout import Layout
from rich.live import Live

class PipelineDashboard:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()

    def render_pipeline_progress(self, stages: list):
        table = Table(title="Pipeline Progress", show_lines=True)
        table.add_column("Stage", style="bold")
        table.add_column("Status")
        table.add_column("Duration")
        table.add_column("Output")
        for stage in stages:
            status_icon = {"complete": "[green]●[/]",
                          "running": "[yellow]◉[/]",
                          "pending": "[dim]○[/]"}[stage['status']]
            table.add_row(stage['name'], status_icon,
                         stage.get('duration', '-'),
                         stage.get('output', '-'))
        return Panel(table, title="GCS Solver Pipeline")

    def render_dof_algebra(self, dof_data: dict):
        grid = Table.grid()
        grid.add_column(justify="right")
        grid.add_column()
        grid.add_row("Geometry DOF:", f"[green]+{dof_data['geom_dof']}[/]")
        grid.add_row("Constraint DOF:", f"[red]{dof_data['constr_dof']}[/]")
        grid.add_row("RS Adjustment:", f"[blue]{dof_data['rs_adj']}[/]")
        net = dof_data['net_dof']
        color = "green" if net == 0 else ("yellow" if net > 0 else "red")
        grid.add_row("[bold]Net DOF:[/]", f"[bold {color}]{net}[/]")
        return Panel(grid, title="DOF Algebra")

    def render_condition_number(self, cond_data: dict):
        kappa = cond_data['kappa']
        if kappa < 10:
            stability = "[green]Stable[/]"
        elif kappa < 1e3:
            stability = "[yellow]Moderate[/]"
        elif kappa < 1e6:
            stability = "[red]Ill-conditioned[/]"
        else:
            stability = "[bold red]Singular[/]"
        grid = Table.grid()
        grid.add_column(justify="right")
        grid.add_column()
        grid.add_row("κ(J):", f"{kappa:.1f}")
        grid.add_row("Stability:", stability)
        grid.add_row("σ_max:", f"{cond_data['sigma_max']:.2f}")
        grid.add_row("σ_min:", f"{cond_data['sigma_min']:.2f}")
        grid.add_row("Rank:", f"{cond_data['rank']}")
        return Panel(grid, title="Condition Number")
```

### 收敛曲线（matplotlib.animation实现）

```python
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class ConvergenceAnimator:
    def __init__(self):
        self.residuals = []
        self.condition_numbers = []
        self.fig, (self.ax_res, self.ax_cond) = plt.subplots(1, 2, figsize=(14, 5))

    def update(self, frame_data: dict):
        self.residuals.append(frame_data['residual'])
        self.condition_numbers.append(frame_data['condition_number'])

        self.ax_res.clear()
        self.ax_res.semilogy(self.residuals, 'b-o', markersize=3)
        self.ax_res.set_xlabel('Iteration')
        self.ax_res.set_ylabel('||F(x)||')
        self.ax_res.set_title('Residual Convergence')
        self.ax_res.grid(True, alpha=0.3)

        self.ax_cond.clear()
        self.ax_cond.semilogy(self.condition_numbers, 'r-o', markersize=3)
        self.ax_cond.set_xlabel('Iteration')
        self.ax_cond.set_ylabel('κ(J)')
        self.ax_cond.set_title('Condition Number Trend')
        self.ax_cond.grid(True, alpha=0.3)

        self.fig.tight_layout()
        return self.ax_res, self.ax_cond

    def start_animation(self, event_stream):
        ani = FuncAnimation(self.fig, self.update, frames=event_stream,
                           interval=100, repeat=False)
        plt.show()
```

### DOF代数分解图

```python
def plot_dof_breakdown(self, dof_data: dict):
    fig, ax = plt.subplots(figsize=(10, 5))
    categories = ['Geometry\nDOF', 'Constraint\nRemoval', 'RigidSet\nAdjust', 'Net\nDOF']
    values = [dof_data['geom_dof'], dof_data['constr_dof'],
              dof_data['rs_adj'], dof_data['net_dof']]
    colors = ['#51cf66', '#ff6b6b', '#339af0',
              '#00e676' if dof_data['net_dof'] == 0 else '#ffaa00']
    bars = ax.bar(categories, values, color=colors, edgecolor='white', linewidth=1.5)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                f'{val:+d}', ha='center', va='center', fontsize=14, fontweight='bold')
    ax.axhline(y=0, color='white', linewidth=0.5)
    ax.set_title('DOF Algebra Breakdown', fontsize=14)
    ax.set_ylabel('DOF')
    plt.tight_layout()
    return fig
```

## 实时更新机制

### 事件流处理

```python
import subprocess
import json

class PipelineEventStream:
    def __init__(self, engine_path: str):
        self.engine_path = engine_path

    def run_and_stream(self, input_path: str):
        proc = subprocess.Popen(
            [self.engine_path, input_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True
        )
        for line in proc.stdout:
            try:
                event = json.loads(line.strip())
                yield event
            except json.JSONDecodeError:
                continue

    def process_events(self, input_path: str, dashboard: PipelineDashboard,
                       animator: ConvergenceAnimator):
        with Live(dashboard.layout, console=dashboard.console, refresh_per_second=4):
            for event in self.event_stream(input_path):
                if event['type'] == 'PipelineStageEvent':
                    dashboard.update_pipeline(event)
                elif event['type'] == 'IterationEvent':
                    animator.update(event)
                elif event['type'] == 'CompletionEvent':
                    dashboard.update_completion(event)
                    break
```

### 命令行接口

```bash
# 运行求解并显示终端仪表板
python -m gcs_viz solve --input data/g1.txt --mode dashboard

# 运行求解并显示收敛曲线动画
python -m gcs_viz solve --input data/g1.txt --mode convergence

# 运行求解并生成完整报告
python -m gcs_viz solve --input data/g1.txt --mode full --output report.png

# 仅分析DOF（不求解）
python -m gcs_viz dof --input data/g1.txt

# 诊断求解失败
python -m gcs_viz diagnose --input data/g1.txt --report failed_report.json
```

## 组件架构

```
gcs_viz/                          ← Python包
├── dashboard/                    ← 仪表板子包
│   ├── __init__.py
│   ├── pipeline_dashboard.py     ← rich终端仪表板
│   │   ├── PipelineDashboard
│   │   │   ├── render_pipeline_progress()
│   │   │   ├── render_dof_algebra()
│   │   │   ├── render_condition_number()
│   │   │   ├── render_propagation_status()
│   │   │   └── render_violation_table()
│   ├── convergence_animator.py   ← matplotlib收敛动画
│   │   ├── ConvergenceAnimator
│   │   │   ├── update()
│   │   │   └── start_animation()
│   ├── dof_analyzer.py           ← DOF代数分析
│   │   ├── DOFAnalyzer
│   │   │   ├── compute_dof_breakdown()
│   │   │   ├── plot_dof_breakdown()
│   │   │   └── compute_rigidity_matrix_info()
│   ├── condition_analyzer.py     ← 条件数分析
│   │   ├── ConditionAnalyzer
│   │   │   ├── compute_condition_number()
│   │   │   ├── svd_analysis()
│   │   │   └── plot_condition_trend()
│   └── propagation_checker.py    ← 约束传播
│       ├── PropagationChecker
│       │   ├── arc_consistency_check()
│       │   └── detect_early_inconsistency()
└── event_stream.py               ← 事件流处理
    ├── PipelineEventStream
    │   ├── run_and_stream()
    │   └── process_events()
```

## Anti-Patterns

| 禁令 | 理由 |
|------|------|
| 使用Web技术(D3.js/浏览器) | Python本地渲染更轻量、终端+matplotlib双通道更高效 |
| 仅终端输出无图表 | 收敛曲线和条件数趋势必须图形化展示 |
| 仅图表无终端 | 管线进度和DOF代数适合终端表格展示 |
| 无约束传播 | scipy+numpy可高效实现AC-3 |
| 无条件数诊断 | scipy.linalg.svd一行代码即可计算 |
| 忽略收敛速率 | 从残差序列自动估计，零额外成本 |

## 执行步骤

1. **启动终端仪表板**：rich Live布局
2. **启动收敛动画**：matplotlib FuncAnimation
3. **执行约束传播**：AC-3检测早期不一致
4. **流式处理事件**：subprocess→json→dashboard+animator
5. **更新管线进度**：rich表格实时刷新
6. **绘制收敛分析**：残差+条件数联合曲线
7. **展示DOF代数**：条形图+终端面板
8. **诊断数值稳定性**：SVD+条件数+近奇异方向
9. **汇总求解结果**：终端报告+PNG图表

## 与GCS管线的集成点

| 管线阶段 | Python实现 | 终端输出 | 图表输出 |
|----------|-----------|---------|---------|
| IO.readGraph | parser.py复用 | Manager统计 | — |
| DCM.decompose | networkx连通分量 | 子问题列表 | 分量图 |
| LGS.analyzeStatus | numpy DOF计算 | DOF面板 | DOF条形图 |
| Propagation | 自实现AC-3 | 传播状态 | 域缩减图 |
| CDS (per iteration) | 事件流解析 | 进度条 | 收敛+条件数曲线 |
| CDS (complete) | scipy分析 | 结果摘要 | 残差分布 |

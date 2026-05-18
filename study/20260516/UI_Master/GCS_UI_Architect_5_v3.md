---
name: GCS_UI_Architect_5_v3
description: |
  GCS系统架构师V3。基于代数规范与信息代数的GCS全栈平台架构——
  使用Python本地技术栈(rich+matplotlib+textual)替代Web技术栈，
  通过rich构建终端平台界面，通过textual构建TUI交互应用，
  通过CQRS+Event Sourcing实现跨C++/Python的状态一致性，
  通过代数规范定义跨层接口契约。
  触发条件：当需要设计GCS整体平台架构、跨层集成、端到端工作流时调用。
---

# GCS UI Architect 5号 V3 — GCS系统架构师

## 理论基础

（与V2完全一致，保留代数规范、信息代数、CQRS+Event Sourcing、范畴论Functor等全部理论）

### 代数规范(Algebraic Specification)

通过签名(signatures)和公理(axioms)定义数据类型和操作：
```
spec MANAGER =
  sorts Manager, RigidSet, Geometry, Constraint, Id
  operations
    create : → Manager
    addRigidSet : Manager × Id → Manager
    addGeometry : Manager × Id × GeometryType × Id × Vec6 → Manager
    ...
  axioms
    ∀ m, id : findGeometry(addGeometry(m, id, t, rs, v), id) = Some(...)
end
```

### 信息代数

每个模块是信息源 S_i = (Φ_i, ⊗_i, ⊆_i)，管线是信息组合 S_IO ⊗ S_DCM ⊗ S_LGS ⊗ S_CDS

### CQRS + Event Sourcing

- Command端：用户操作 → Command → C++ Engine → Event → Event Store
- Query端：Event Store → Projection → Read Model → Python UI

### 范畴论Functor

C++ Category → Python Category → UI Category，Functor保证结构保持

## V2→V3 核心升级：Python本地平台

### 为什么用Python替代Web

| 维度 | V2(Web平台) | V3(Python本地平台) |
|------|------------|-------------------|
| 平台框架 | React/Vue SPA | textual TUI框架 |
| 页面导航 | React Router | textual Screen/Tab |
| 状态管理 | Pinia/Vuex | Python dataclass + Event Store |
| 数据绑定 | React/Vue响应式 | textual reactive属性 |
| 样式 | CSS设计Token | textual CSS样式 |
| 图表 | D3.js | matplotlib嵌入textual |
| 终端输出 | 无 | rich彩色终端 |
| 部署 | 需要浏览器 | 终端直接运行 |
| 与C++集成 | HTTP/WebSocket | subprocess/ctypes/IPC |

### Python技术栈

| 库 | 用途 | 特点 |
|----|------|------|
| textual | TUI框架，构建终端交互应用 | 异步、响应式、CSS样式 |
| rich | 彩色终端输出 | 表格、面板、进度条 |
| matplotlib | 图表渲染 | 嵌入textual或独立窗口 |
| asyncio | 异步事件处理 | 事件驱动架构 |
| json | 事件序列化 | Event Store持久化 |
| subprocess | C++引擎调用 | 管线执行 |

## 平台架构设计

### 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│  TUI (textual + rich + matplotlib嵌入)                  │
│  ├── Screens (Home/Input/Solve/Results/Graphs/Tools)   │
│  ├── Widgets (shared TUI components)                    │
│  └── Reactive State (textual reactive属性)             │
├─────────────────────────────────────────────────────────┤
│                    Application Layer                     │
│  ├── Command Handlers (process user actions)            │
│  ├── Event Handlers (react to engine events)            │
│  ├── Read Model Projections (build query views)         │
│  └── Workflow Orchestrator (pipeline control)           │
├─────────────────────────────────────────────────────────┤
│                    Bridge Layer                          │
│  ├── Event Store (JSON文件持久化)                       │
│  ├── Command Bus (asyncio队列)                          │
│  ├── Event Bus (asyncio发布/订阅)                       │
│  ├── Serialization (JSON)                               │
│  └── Transport (subprocess/ctypes/IPC)                  │
├─────────────────────────────────────────────────────────┤
│                    Domain Layer                          │
│  C++ Engine (Core/IO/DCM/LGS/CDS/App)                  │
│  Python Toolchain (parser/viewer/tools/gcs_viz)        │
└─────────────────────────────────────────────────────────┘
```

### TUI平台界面

```
┌──────────────────────────────────────────────────────────────────┐
│ GCS Platform V3                                    [Help] [Quit] │
├──────────┬───────────────────────────────────────────────────────┤
│          │                                                        │
│ 🏠 Home  │  ┌────────────────────────────────────────────────┐   │
│ 📥 Input │  │                                                │   │
│ ⚡ Solve │  │   Current Screen Content                       │   │
│ 📊 Result│  │   (varies by selected tab)                     │   │
│ 🔗 Graphs│  │                                                │   │
│ 🔧 Tools │  │                                                │   │
│ ⚙ Config │  │                                                │   │
│          │  └────────────────────────────────────────────────┘   │
│          │  ┌────────────────────────────────────────────────┐   │
│          │  │  Status: Pipeline Ready | DOF: — | Last: —     │   │
│          │  └────────────────────────────────────────────────┘   │
└──────────┴───────────────────────────────────────────────────────┘
```

### textual应用骨架

```python
# gcs_viz/platform/app.py

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane
from textual.containers import Container
from textual.reactive import reactive
from rich.text import Text

class GCSPlatform(App):
    CSS = """
    Screen { layout: horizontal; }
    #sidebar { width: 20; dock: left; }
    #content { width: 1fr; }
    #statusbar { dock: bottom; height: 1; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("h", "switch_tab('home')", "Home"),
        ("i", "switch_tab('input')", "Input"),
        ("s", "switch_tab('solve')", "Solve"),
        ("r", "switch_tab('results')", "Results"),
        ("g", "switch_tab('graphs')", "Graphs"),
    ]

    pipeline_state = reactive("idle")
    dof_value = reactive(None)
    current_scene = reactive(None)

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Home", id="home"):
                yield HomeScreen()
            with TabPane("Input", id="input"):
                yield InputScreen()
            with TabPane("Solve", id="solve"):
                yield SolveScreen()
            with TabPane("Results", id="results"):
                yield ResultsScreen()
            with TabPane("Graphs", id="graphs"):
                yield GraphsScreen()
        yield Footer()

    def watch_pipeline_state(self, old_state: str, new_state: str):
        self.refresh()

    def watch_dof_value(self, old_dof, new_dof):
        self.refresh()
```

### Home Screen

```python
from textual.widgets import Static, Button, DataTable
from textual.containers import Vertical, Horizontal

class HomeScreen(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("GCS Platform V3 — Home", classes="title")
        yield Static("Geometric Constraint Solver System")
        with Horizontal():
            yield Button("Quick Start", variant="primary", id="quick_start")
            yield Button("Recent Scenes", variant="default", id="recent")
            yield Button("System Health", variant="default", id="health")
        yield DataTable(id="recent_table")

    def on_mount(self):
        table = self.query_one("#recent_table")
        table.add_columns("Scene", "Status", "Geometries", "Constraints", "Last Modified")
        table.add_row("bcc_7g_8c", "✓ Solved", "7", "8", "2026-05-16 14:30")
        table.add_row("g1", "✓ Solved", "5", "2", "2026-05-16 10:15")
```

### Input Screen (Builder模式)

```python
from textual.widgets import Input, Select, Label
from textual.containers import VerticalScroll

class InputScreen(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Static("Problem Builder", classes="title")
        yield Label("Input Mode:")
        yield Select([("Builder", "builder"), ("File", "file"),
                      ("IProblem", "iproblem")], value="builder")

        yield Label("Rigid Sets:")
        yield RigidSetEditor()

        yield Label("Geometries:")
        yield GeometryEditor()

        yield Label("Constraints:")
        yield ConstraintEditor()

        yield DOFIndicator()

        with Horizontal():
            yield Button("Compute", variant="primary", id="compute")
            yield Button("Save", variant="default", id="save")
            yield Button("Validate", variant="default", id="validate")

class DOFIndicator(Static):
    dof_value = reactive(0)

    def render(self) -> Text:
        if self.dof_value == 0:
            return Text(f"Net DOF: {self.dof_value} (Well-constrained) ✓",
                       style="bold green")
        elif self.dof_value > 0:
            return Text(f"Net DOF: {self.dof_value} (Under-constrained) ⚠",
                       style="bold yellow")
        else:
            return Text(f"Net DOF: {self.dof_value} (Over-constrained) ✗",
                       style="bold red")
```

### Solve Screen

```python
class SolveScreen(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("Pipeline Dashboard", classes="title")
        yield PipelineProgressWidget()
        with Horizontal():
            yield DOFAlgebraWidget()
            yield ConditionNumberWidget()
            yield PropagationWidget()
        yield ConstraintViolationWidget()
        with Horizontal():
            yield Button("Run", variant="primary", id="run")
            yield Button("Pause", variant="default", id="pause")
            yield Button("Stop", variant="error", id="stop")

class PipelineProgressWidget(Static):
    stages = reactive([])

    def render(self) -> Text:
        text = Text()
        for stage in self.stages:
            icon = {"complete": "●", "running": "◉", "pending": "○"}[stage['status']]
            style = {"complete": "green", "running": "yellow", "pending": "dim"}[stage['status']]
            text.append(f" {icon} {stage['name']}: {stage['status']}", style=style)
            text.append("\n")
        return text
```

### Results Screen

```python
class ResultsScreen(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("Results", classes="title")
        with TabbedContent():
            with TabPane("3D View"):
                yield Static("3D visualization opens in matplotlib window")
                yield Button("Open 3D View", id="open_3d")
            with TabPane("Monge"):
                yield Static("Three-view projection opens in matplotlib window")
                yield Button("Open Monge View", id="open_monge")
            with TabPane("Graph"):
                yield Static("Constraint graph opens in matplotlib window")
                yield Button("Open Graph View", id="open_graph")
            with TabPane("DOF Report"):
                yield DOFReportWidget()
            with TabPane("Convergence"):
                yield Static("Convergence analysis opens in matplotlib window")
                yield Button("Open Convergence", id="open_conv")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "open_3d":
            self.app.run_worker(self._open_visualization("3d"))
        elif event.button.id == "open_monge":
            self.app.run_worker(self._open_visualization("monge"))
        elif event.button.id == "open_graph":
            self.app.run_worker(self._open_visualization("graph"))

    async def _open_visualization(self, view_type: str):
        import subprocess
        cmd = ["python", "-m", "gcs_viz", "geometry",
               "--input", self.app.current_scene, "--view", view_type]
        proc = subprocess.Popen(cmd)
```

## Event Store实现

```python
# gcs_viz/platform/event_store.py

import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class GCSEvent:
    timestamp: str
    event_type: str
    payload: dict

class EventStore:
    def __init__(self, store_dir: str = ".events/"):
        self.store_dir = store_dir
        os.makedirs(store_dir, exist_ok=True)

    def append(self, event_type: str, payload: dict):
        event = GCSEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            payload=payload
        )
        scene_id = payload.get('scene_id', 'default')
        log_path = os.path.join(self.store_dir, f"{scene_id}.jsonl")
        with open(log_path, 'a') as f:
            f.write(json.dumps(asdict(event)) + '\n')

    def replay(self, scene_id: str) -> List[GCSEvent]:
        log_path = os.path.join(self.store_dir, f"{scene_id}.jsonl")
        events = []
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                for line in f:
                    events.append(GCSEvent(**json.loads(line.strip())))
        return events

    def get_state_at(self, scene_id: str, event_index: int) -> dict:
        events = self.replay(scene_id)
        state = {}
        for event in events[:event_index + 1]:
            state = self._apply_event(state, event)
        return state

    def _apply_event(self, state: dict, event: GCSEvent) -> dict:
        if event.event_type == 'GraphLoaded':
            state['manager'] = event.payload
            state['pipeline_stage'] = 'IO'
        elif event.event_type == 'DecompositionCompleted':
            state['decomposition'] = event.payload
            state['pipeline_stage'] = 'DCM'
        elif event.event_type == 'SolveCompleted':
            state['result'] = event.payload
            state['pipeline_stage'] = 'Complete'
        return state
```

## 组件架构

```
gcs_viz/                          ← Python包
├── platform/                     ← 平台子包
│   ├── __init__.py
│   ├── app.py                    ← textual TUI应用
│   │   ├── GCSPlatform(App)
│   ├── screens/                  ← 各页面
│   │   ├── home.py               ← HomeScreen
│   │   ├── input.py              ← InputScreen
│   │   │   ├── RigidSetEditor
│   │   │   ├── GeometryEditor
│   │   │   ├── ConstraintEditor
│   │   │   └── DOFIndicator
│   │   ├── solve.py              ← SolveScreen
│   │   │   ├── PipelineProgressWidget
│   │   │   ├── DOFAlgebraWidget
│   │   │   ├── ConditionNumberWidget
│   │   │   └── ConstraintViolationWidget
│   │   ├── results.py            ← ResultsScreen
│   │   │   └── DOFReportWidget
│   │   ├── graphs.py             ← GraphsScreen
│   │   └── settings.py           ← SettingsScreen
│   ├── event_store.py            ← Event Store
│   │   ├── EventStore
│   │   │   ├── append()
│   │   │   ├── replay()
│   │   │   └── get_state_at()
│   ├── command_bus.py            ← Command Bus
│   │   ├── CommandBus
│   │   │   ├── dispatch()
│   │   │   └── handle()
│   ├── projections.py            ← Read Model Projections
│   │   ├── PipelineProjection
│   │   ├── DOFProjection
│   │   └── ConvergenceProjection
│   └── engine_bridge.py          ← C++引擎桥接
│       ├── EngineBridge
│       │   ├── run_pipeline()
│       │   ├── stream_events()
│       │   └── get_result()
├── graph/                        ← 1号：约束图可视化
├── dashboard/                    ← 2号：管线仪表板
├── geometry/                     ← 3号：几何空间可视化
├── graph_engine/                 ← 4号：图工程
└── color_scheme.py               ← 共享颜色方案
```

## 设计系统（V3：终端工业风）

### 调性：终端工业风(Terminal Industrial)

GCS在终端中运行，UI调性应体现**终端美学**和**工程精确性**：

```python
# gcs_viz/color_scheme.py

GCS_TERMINAL_THEME = {
    'bg_primary': '#0a0a0a',
    'bg_secondary': '#141414',
    'bg_elevated': '#1e1e1e',
    'text_primary': '#e0e0e0',
    'text_secondary': '#888888',
    'accent': '#00bfff',
    'success': '#00e676',
    'warning': '#ffc107',
    'error': '#ff5252',
    'rigidset': ['#e6194b', '#3cb44b', '#4363d8', '#f58231', '#911eb4'],
    'constraint': {
        'Coincident': '#ff0000',
        'Parallel': '#00ff00',
        'Perpendicular': '#0000ff',
        'Distance': '#ffaa00',
        'Angle': '#ff00ff',
    },
}
```

### textual CSS

```css
.title {
    text-style: bold;
    color: $accent;
    padding: 1 2;
}

Static {
    padding: 0 1;
}

Button.primary {
    background: $accent;
}

DataTable {
    height: auto;
    max-height: 20;
}

#statusbar {
    background: $surface;
    color: $text-muted;
    padding: 0 1;
}
```

## Anti-Patterns

| 禁令 | 理由 |
|------|------|
| 使用Web技术(React/Vue/D3.js/浏览器) | Python TUI更轻量、零部署、与GCS Python工具链无缝集成 |
| 无代数规范的接口 | 跨层接口必须有代数规范定义 |
| 无事件溯源 | JSON文件Event Store零依赖实现 |
| 无因果一致性 | 事件顺序保证因果正确 |
| 无DOF代数约束输入 | textual reactive属性实时更新DOF |
| 忽略约束兼容性 | 兼容性矩阵检查 |
| 无状态时间旅行 | Event Store replay()实现 |
| 3D可视化用Three.js | matplotlib mplot3d已可用 |

## 执行步骤

1. **建立代数规范**：Python dataclass定义签名和公理
2. **实现Event Store**：JSON文件持久化
3. **构建TUI平台**：textual App + Screens
4. **实现输入层**：Builder(代数约束)+文件+IProblem
5. **集成管线仪表板**：rich终端+matplotlib窗口
6. **整合3D视图**：mplot3d独立窗口
7. **整合三视图**：matplotlib subplots
8. **整合约束图视图**：networkx+matplotlib
9. **构建图工程工具**：Henneberg+验证+CSP修复
10. **实现场景管理**：Event Store时间旅行

## 与GCS全系统的集成点

| 系统层 | 集成方式 | Python实现 | TUI表现 |
|--------|----------|-----------|---------|
| C++ App门面层 | subprocess | EngineBridge | 问题输入+管线控制 |
| C++ Core数据模型 | JSON文件 | parser.py | 数据展示+编辑 |
| C++ DCM | 事件流 | event_store.py | 子问题列表 |
| C++ LGS | 事件流 | projections.py | DOF面板 |
| C++ CDS | 事件流 | event_store.py | 收敛分析 |
| Python parser.py | 直接调用 | import | 文件解析 |
| Python viewer.py | 直接调用 | import | 3D视图 |
| Python tools.py | 直接调用 | import | 图工程工具 |
| .store/ JSON | 文件系统 | json模块 | 图库 |

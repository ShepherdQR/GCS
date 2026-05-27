# GCS Token Audit System — 实施计划

> **版本**: 1.0.0 | **日期**: 2026-05-27 | **状态**: 待执行
>
> 本计划将审计系统设计转化为可执行的开发任务，按 Phase 组织，每个 Phase 有明确的交付物和验证标准。

---

## 总览

```
Phase 0: 基础设施      [Day 1-2]  ████░░░░░░░░░░░░░░░░
Phase 1: 离线分析引擎  [Day 3-5]  ░░░░████████░░░░░░░░
Phase 2: 实时监控      [Day 6-8]  ░░░░░░░░░░░░████████░░
Phase 3: 历史分析      [Day 9-10] ░░░░░░░░░░░░░░░░░░████
Phase 4: 可选增强      [后续]     (按需)
```

---

## Phase 0: 基础设施 (Day 1-2)

### 目标
搭建项目骨架，确认数据可行性，建立开发环境。

### 任务

#### T0.1 — 调研 JSONL Transcript 格式

**描述**：读取当前项目的实际 JSONL transcript 文件，确认字段结构与设计文档一致，记录任何差异。

**步骤**：
1. 找到 `~/.claude/projects/` 下对应 GCS_A 的目录
2. 读取最近 3 个 session 的 JSONL 文件
3. 提取每行的 `type`, `message.usage`, `tools` 字段
4. 记录实际字段名、缺失字段、额外字段
5. 特别关注：是否有 `model` 字段、`usage` 对象是否始终存在、`tools` 数组结构

**验证**：生成一份 `transcript-format-inventory.md` 记录实际格式与设计文档的差异。

**预计工时**：1h

---

#### T0.2 — 搭建项目骨架

**描述**：创建 `tools/token_audit/` 目录结构，安装依赖，建立 SQLite schema。

**步骤**：
```bash
mkdir -p tools/token_audit/tests
touch tools/token_audit/__init__.py
touch tools/token_audit/__main__.py
```

**文件清单**：
- `tools/token_audit/__init__.py`
- `tools/token_audit/__main__.py` — `python -m tools.token_audit` entry
- `tools/token_audit/schema.sql` — 从设计报告复制 DDL
- `tools/token_audit/config.yaml` — 默认配置
- `tools/token_audit/db.py` — SQLite 初始化 + 基础 CRUD
- `tools/token_audit/tests/__init__.py`
- `requirements-dev.txt` 或使用 `pyproject.toml`

**依赖**（最小化）：
- `click` — CLI 框架
- `pyyaml` — 配置解析
- `pytest` — 测试

**验证**：`python -m tools.token_audit --help` 输出帮助信息。`python -m pytest tools/token_audit/tests/` 通过（即使只有占位测试）。

**预计工时**：2h

---

#### T0.3 — 数据库初始化

**描述**：实现 `db.py` 模块，支持数据库创建、schema 迁移、基础 session CRUD。

**关键函数**：
```python
# db.py
def init_db(path: str = "tools/token_audit/audit.db") -> sqlite3.Connection: ...
def insert_session(conn, session: SessionSnapshot) -> str: ...
def update_session(conn, session_id: str, **kwargs) -> None: ...
def get_session(conn, session_id: str) -> Optional[dict]: ...
def list_sessions(conn, project: str = None, limit: int = 50) -> list[dict]: ...
def close_session(conn, session_id: str, ended_at: str) -> None: ...
```

**验证**：`python -m pytest tools/token_audit/tests/test_db.py` — 测试 CRUD 操作。

**预计工时**：2h

---

### Phase 0 交付物

- [x] Transcript 格式调研报告
- [x] 可运行的项目骨架
- [x] SQLite 数据库就绪
- [x] 基础测试框架

---

## Phase 1: 离线分析引擎 (Day 3-5)

### 目标
能够对已完成的 session 进行完整的 token-产出关联分析，生成 Markdown 报告。

### 任务

#### T1.1 — JSONL 解析器

**描述**：实现 `parser.py`，完整解析 JSONL transcript 文件。

**关键类/函数**：
```python
# parser.py
class JSONLParser:
    def parse_file(self, path: str) -> list[dict]: ...
    def parse_session(self, path: str) -> SessionSnapshot: ...
    def extract_usage(self, record: dict) -> Optional[TokenUsage]: ...
    def extract_tools(self, record: dict) -> list[ToolCall]: ...
    def extract_edits(self, record: dict) -> list[EditRecord]: ...
    def extract_model(self, record: dict) -> str: ...
    def extract_timestamps(self, records: list[dict]) -> tuple[str, str]: ...
```

**处理要点**：
- 大文件 (>100MB JSONL) 的流式读取
- JSON 解析错误的容错处理
- Token 用量仅在 `type == "assistant"` 消息中
- 工具调用可能在 `tools` 顶层字段，也可能在 `message.content[].type == "tool_use"` 中

**验证**：读取 3 个实际 session 的 JSONL，打印解析后的 SessionSnapshot。

**预计工时**：3h

---

#### T1.2 — 成本模型

**描述**：实现 `cost_model.py`，基于 Anthropic 定价表计算 USD 成本。

**关键函数**：
```python
# cost_model.py
class CostModel:
    def __init__(self, pricing_yaml: str = "config.yaml"): ...
    def calculate(self, usage: TokenUsage, model_id: str) -> int:  # microdollars
        ...
    def usd_display(self, microdollars: int) -> str:  # "$1.72"
        ...

# 定价表 (内嵌默认值，config.yaml 可覆盖)
DEFAULT_PRICING = {
    "claude-sonnet-4-6": {
        "input": 3.00,        # per 1M tokens
        "output": 15.00,
        "cache_write": 6.00,
        "cache_read": 0.30,
    },
    "claude-opus-4-7": {...},
    "claude-haiku-4-5": {...},
}
```

**验证**：单元测试覆盖所有模型 × 所有 token 类型的成本计算。

**预计工时**：1.5h

---

#### T1.3 — Git 关联分析器

**描述**：实现 `git_linker.py`，将 session 的时间窗口关联到 git 变更。

**关键函数**：
```python
# git_linker.py
class GitLinker:
    def __init__(self, repo_path: str = "."): ...
    
    def get_commits_in_window(
        self, start: datetime, end: datetime
    ) -> list[dict]:  # [{hash, message, author, date}]
        ...
    
    def get_diff_stats(
        self, start: datetime, end: datetime
    ) -> dict:  # {lines_added, lines_removed, files_changed}
        ...
    
    def get_session_output(
        self, start: datetime, end: datetime
    ) -> SessionOutput:
        ...
    
    def extract_decision_signals(
        self, commits: list[dict]
    ) -> DecisionSignal: ...
```

**处理要点**：
- 使用 `git log --after=... --before=...` 或 reflog
- Session 可能与 commit 不完全对齐（一个 commit 可能跨越多个 session，或一个 session 产生多个 commits）
- 使用 `git reflog` 作为精确时间源
- 当 session 无对应 commit 时（如探索性 session），产出指标优雅降级

**验证**：对已知 session 时间窗运行，对比 git 数据是否合理。

**预计工时**：2.5h

---

#### T1.4 — BEI 计算引擎

**描述**：实现 `bei_engine.py`，执行五维度评分。

**关键函数**：
```python
# bei_engine.py
class BEIEngine:
    def __init__(self, config: dict, db_conn: sqlite3.Connection): ...
    
    def calculate(
        self, snapshot: SessionSnapshot, project: str
    ) -> BEIScores: ...
    
    def get_baseline(self, project: str) -> dict: ...
    
    # 各维度计算
    def _output_score(self, snapshot) -> float: ...
    def _quality_score(self, snapshot) -> float: ...
    def _decision_score(self, snapshot) -> float: ...
    def _knowledge_score(self, snapshot) -> float: ...
    def _efficiency_score(self, snapshot) -> float: ...
```

**处理要点**：
- baseline 从 SQLite 查询项目历史 P75
- 无历史数据时使用 config.yaml 中的默认 baseline
- 各维度归一化到 [0, 1]

**验证**：用模拟 SessionSnapshot 测试维度计算，验证边界条件（零 token、零产出、超常高产）。

**预计工时**：2h

---

#### T1.5 — CLI 报告生成器

**描述**：实现 `reporter.py` 和 `cli.py` 的基础命令。

**实现命令**：
```bash
python -m tools.token_audit report --session <id>
python -m tools.token_audit report --latest
python -m tools.token_audit report --session <id> --format json
```

**报告模板**：按设计报告第 9 节的格式生成 Markdown。

**验证**：对一个实际完成的 session 生成报告，检查输出完整性。

**预计工时**：2.5h

---

### Phase 1 交付物

- [x] JSONL 解析器 — 完整解析 session transcript
- [x] 成本模型 — 精确到 microdollar
- [x] Git 关联 — session ↔ diff/commit 映射
- [x] BEI 引擎 — 五维度评分
- [x] CLI report 命令 — `python -m tools.token_audit report`

---

## Phase 2: 实时监控 (Day 6-8)

### 目标
Session 进行中实时显示 token 消耗和产出统计。

### 任务

#### T2.1 — 增量 JSONL 解析器

**描述**：在 `parser.py` 中增加 `IncrementalJSONLParser` 类。

**关键逻辑**：
```python
class IncrementalJSONLParser(JSONLParser):
    def __init__(self, path: str): ...
    def read_new_records(self) -> list[dict]: ...
    def reset(self) -> None: ...
```

**处理要点**：
- 维护字节偏移量，从上次读取位置继续
- 文件被轮转/删除时优雅处理
- 新记录异步累积到内存 SessionSnapshot

**验证**：模拟 JSONL 文件追加，验证增量读取正确性。

**预计工时**：1.5h

---

#### T2.2 — Session 发现与追踪器

**描述**：实现 `tracker.py`。

**关键函数**：
```python
# tracker.py
class SessionTracker:
    def __init__(self, project_name: str, db_conn, alert_engine): ...
    
    def find_active_session(self) -> Optional[str]: ...
    def start_tracking(self, jsonl_path: str) -> None: ...
    def tick(self) -> SessionSnapshot: ...     # 每轮调用，返回最新快照
    def stop_tracking(self) -> SessionSnapshot: ...
    def is_active(self) -> bool: ...
```

**处理要点**：
- 每次 `tick()` 增量读取新行，更新内存快照
- 识别 session 结束（JSONL 超过 N 秒未更新且无 open file handle）
- 结束时自动触发 Git 关联和 BEI 计算

**验证**：在实际 Claude Code session 中运行 tracker，检查数据准确性。

**预计工时**：2h

---

#### T2.3 — 告警引擎

**描述**：实现 `alerts.py`。

**关键函数**：
```python
# alerts.py
class AlertEngine:
    def __init__(self, config: dict, db_conn): ...
    def evaluate(self, snapshot: SessionSnapshot) -> list[Alert]: ...
    def should_alert(self, alert_type: AlertType, session_id: str) -> bool: ...  # 冷却期检查
    def fire(self, alert: Alert) -> None: ...  # 写入 DB + 终端输出
```

**验证**：用模拟数据触发各类告警，检查阈值逻辑和冷却期。

**预计工时**：1.5h

---

#### T2.4 — 实时状态行渲染

**描述**：在 CLI 中实现 `watch` 命令的终端状态行。

**实现命令**：
```bash
python -m tools.token_audit watch
python -m tools.token_audit watch --interval 5
```

**状态行设计**（精简）：
```
GCS Session  T:12  In:45K Out:19K  Cache:62%  $0.34  Edits:8A/2R  BEI:—
```

**处理要点**：
- 使用 ANSI 转义码就地刷新（不滚屏）
- `--format json` 模式每行输出 JSON（供 pipeline 消费）
- Ctrl+C 优雅退出，触发 session 结束处理

**验证**：在实际 Claude Code session 中启动 watch，观察数据实时更新。

**预计工时**：2h

---

#### T2.5 — Claude Code Hook 集成

**描述**：通过 Claude Code hooks 系统在 session 生命周期关键节点触发审计操作。

**Hook 配置**（`.claude/settings.json` 或 `.claude/settings.local.json`）：
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "",
        "command": "python -m tools.token_audit hook post-tool"
      }
    ]
  }
}
```

或者更轻量的方式：在 session 启动/结束时通过 hook 自动调用 audit 命令。

**备选方案**：如果 hooks 配置复杂，先依赖 `watch` 命令的手动启动 + JSONL 文件修改时间检测。

**验证**：Hook 触发后检查 audit 数据库更新。

**预计工时**：1.5h

---

### Phase 2 交付物

- [x] 增量 JSONL 解析
- [x] Session 发现与追踪
- [x] 告警引擎（6 种告警规则）
- [x] `watch` 命令 — 实时状态行
- [x] Claude Code hook 集成（或备选方案）

---

## Phase 3: 历史分析与洞察 (Day 9-10)

### 目标
跨 session 的趋势分析、项目级 ROI 估算、自动报告生成。

### 任务

#### T3.1 — 批量导入历史数据

**描述**：实现 `db import` 命令，从历史 JSONL 文件批量导入。

```bash
python -m tools.token_audit db import --all
python -m tools.token_audit db import --since 2026-05-01
python -m tools.token_audit db import --project GCS_A
```

**处理要点**：
- 遍历 `~/.claude/projects/` 下所有 JSONL
- 跳过已导入的 session（通过 session_id 去重）
- 进度条显示（tqdm 或简单计数）
- 每个 session 导入后更新 daily_summary

**验证**：导入后 `python -m tools.token_audit db stats` 显示正确统计数据。

**预计工时**：2h

---

#### T3.2 — 趋势分析命令

**描述**：实现 `trend` 命令。

```bash
python -m tools.token_audit trend
python -m tools.token_audit trend --days 30 --metric bei_composite
python -m tools.token_audit trend --days 7 --metric cost_per_commit
python -m tools.token_audit trend --format json
```

**输出内容**：
- 每日 BEI / Cost-per-Commit / Cache Hit Rate / Output-per-Token 的折线图（ASCII art）
- 周度汇总表
- 趋势方向判断（上升/下降/持平）

**验证**：对已有数据运行 trend，检查趋势方向是否合理。

**预计工时**：2h

---

#### T3.3 — 周报/月报自动生成

**描述**：扩展 `report` 命令支持时间范围报告。

```bash
python -m tools.token_audit report --from 2026-05-20 --to 2026-05-27
python -m tools.token_audit report --this-week
python -m tools.token_audit report --this-month
```

**报告内容**：按设计报告第 9.2 节模板生成。

**验证**：生成周报和月报，检查数据准确性。

**预计工时**：2h

---

#### T3.4 — 项目级 ROI 估算

**描述**：实现粗略的项目 ROI 估算。

**计算逻辑**：
```
total_ai_cost = Σ(session_cost) in period
total_commits = Σ(commits_count) in period
estimated_dev_hours = total_commits × avg_hours_per_commit_without_ai
estimated_dev_cost = estimated_dev_hours × hourly_dev_rate
roi = (estimated_dev_cost - total_ai_cost) / total_ai_cost
```

**处理要点**：
- `avg_hours_per_commit_without_ai` 和 `hourly_dev_rate` 从 config 读取
- ROI 是粗略估计，标注置信度
- 区分不同类型的 session（exploration vs implementation）

**验证**：对历史数据运行 ROI 计算，检查结果合理性。

**预计工时**：1.5h

---

### Phase 3 交付物

- [x] 历史数据批量导入
- [x] `trend` 命令 — ASCII 趋势图
- [x] 周报/月报自动生成
- [x] 项目级 ROI 估算

---

## Phase 4: 可选增强 (后续)

以下增强不在初始 10 天计划内，按需排期。

### T4.1 — Web Dashboard

**方案 A** (推荐先试): `datasette tools/token_audit/audit.db` — 零代码 SQLite 浏览器，直接提供可查询的 Web UI。

**方案 B**: 复用 claude-monitor 的 Go + WebSocket 架构，嵌入 BEI overlay。

**方案 C**: FastAPI + 轻量前端（单文件 HTML + Chart.js）。

### T4.2 — OpenTelemetry 集成

- 导出 `gcs.token_audit.session.cost`, `gcs.token_audit.bei.composite` 等指标到 OTLP endpoint
- 对接 Prometheus + Grafana（与 SigNoz 方案一致）
- 可实现组织级 AI 成本仪表板

### T4.3 — 预测模型

- 基于历史 session 数据训练简单的回归模型
- 在 session 早期（前 5 轮）预测最终成本和 BEI
- 当预测值超过阈值时提前告警

### T4.4 — 团队级聚合与对比

- 多项目/多开发者对比
- 匿名化效率排行榜
- 识别高效工作模式并推广

---

## 风险管理

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| JSONL 格式与预期不同 | 中 | 高 | Phase 0 调研优先进行 |
| Session 与 Commit 时间对齐不准 | 中 | 中 | Git reflog + 手动确认机制 |
| Claude Code 更新改变 JSONL 结构 | 低 | 高 | 解析器容错设计，未知字段忽略 |
| 大 session JSONL (>200MB) 解析慢 | 低 | 中 | 流式读取 + 增量解析 |
| BEI 评分与实际体感不一致 | 中 | 中 | 权重可配置 + 持续校准 |

---

## 成功标准

| 阶段 | 成功标准 |
|------|---------|
| Phase 0 | 项目骨架可运行，DB schema 就绪 |
| Phase 1 | 能够对任意已完成 session 生成完整 Markdown 报告 |
| Phase 2 | `watch` 命令在实际 session 中实时刷新数据 |
| Phase 3 | `trend` 命令输出 30 天趋势，`report --this-week` 生成周报 |
| 总体 | 用户可以在 5 秒内了解本 session 的 token 消耗和产出效率 |

---

## 附录：技术决策记录

### 决策 1: Python (而非 Go/Rust/Node.js)

**选择**: Python 3.11+

**理由**:
- GCS 项目已有 Python 工具（`python/gcs_viz/`），团队熟悉
- JSONL 解析、SQLite、CLI 在 Python 生态中最简洁
- Phase 0-3 的数据量（MB 级 JSONL）不需要 Go/Rust 的性能
- 如果未来需要高性能，核心解析逻辑可移植

### 决策 2: SQLite (而非 PostgreSQL/JSON file)

**选择**: SQLite

**理由**:
- 零配置、零依赖、单文件存储
- 单用户场景不需要 client-server 数据库
- 足够处理数万 session 的查询
- datasette 可直接提供 Web UI

### 决策 3: 审计数据库放在项目内

**选择**: `tools/token_audit/audit.db`

**理由**:
- 与项目绑定，随项目备份/迁移
- 不同项目的审计数据隔离
- `.gitignore` 中排除 audit.db（可选：保留为项目资产）

### 决策 4: 自建核心引擎 (而非直接使用 context-stats)

**选择**: 自建 + 参考现有工具

**理由**:
- context-stats 等工具提供 token 监控但不提供 BEI / Git 关联 / 产出分析
- 集成多个工具的数据源需要自定义聚合逻辑
- 但会重用 context-stats 的 JSONL 解析思路和状态行渲染模式

---

> **下一步**: 从 Phase 0 T0.1 开始执行。

# GCS AI Session Token-产出实时审计系统：详细设计报告

> **版本**: 1.0.0 | **日期**: 2026-05-27 | **状态**: 详细设计
>
> 本报告定义 GCS 项目 AI 会话的实时 Token 消耗与产出价值追踪系统的完整架构设计。

---

## 目录

1. [设计目标](#1-设计目标)
2. [核心概念模型](#2-核心概念模型)
3. [数据源分析](#3-数据源分析)
4. [系统架构](#4-系统架构)
5. [数据模型设计](#5-数据模型设计)
6. [BEI 计算引擎](#6-bei-计算引擎)
7. [实时数据流设计](#7-实时数据流设计)
8. [CLI 接口设计](#8-cli-接口设计)
9. [输出报告格式](#9-输出报告格式)
10. [告警规则设计](#10-告警规则设计)
11. [扩展性设计](#11-扩展性设计)

---

## 1. 设计目标

### 1.1 核心需求

| 优先级 | 需求 | 描述 |
|--------|------|------|
| P0 | **实时 Token 统计** | 当前 session 内实时展示 token 消耗量（input/output/cache）及累计成本 |
| P0 | **产出关联** | 将 token 消耗与 git diff（代码产出）、commit（工作单元）关联 |
| P0 | **Session 结束报告** | 每次 session 结束后自动生成效益报告 |
| P1 | **历史趋势分析** | 跨 session 的 token 效率变化趋势 |
| P1 | **成本告警** | session 超预算 / 效率骤降时提醒 |
| P2 | **BEI 综合评分** | 五维度效益综合指数计算与展示 |
| P2 | **项目级 ROI 估算** | 按项目周期汇总 AI 成本与估计产出价值 |

### 1.2 非目标

- 不做实时 API 拦截（Claude Code 已通过 JSONL 提供完整数据）
- 不做浏览器级别 dashboard（Phase 1-2 聚焦 CLI，Phase 4 可选 Web）
- 不做多用户/团队聚合（Phase 4 可选）
- 不替换 Claude Code 原生计费系统

---

## 2. 核心概念模型

### 2.1 实体关系

```
Project (GCS_A)
  └── Session (一次 Claude Code 会话)
        ├── Turn (一轮对话/API 调用)
        │     ├── LLMRequest (模型调用)
        │     ├── ToolCall (工具调用：Read/Write/Edit/Bash/Agent/...)
        │     └── EditDecision (编辑接受/拒绝)
        ├── Commit (git commit — 一个 session 可以产生多个 commit)
        └── MemoryEntry (knowledge 积累 — 写入 .claude/memory/ 的记录)
```

### 2.2 核心度量链

```
Token 消耗 ──→ 成本 (USD)
       │
       └──────→ 代码产出 (LoC) ──→ Output-per-Token
       │
       └──────→ Commits ──→ Cost-per-Commit / CPG
       │
       └──────→ 编辑决策 ──→ Edit Rejection Rate
       │
       └──────→ Memory/Skill ──→ Knowledge 积累

                    ↓ 加权聚合

                 BEI (效益综合指数)
```

### 2.3 时间窗口定义

| 窗口 | 用途 | 更新频率 |
|------|------|---------|
| **实时** (当前 session) | 状态行显示、突发告警 | 每 5s |
| **Session** (单次会话) | Session 结束报告 | Session 结束时 |
| **Daily** | 日度总结 | 每日 |
| **Weekly** | 趋势分析 | 每周 |
| **Monthly** | 项目 ROI | 每月 |

---

## 3. 数据源分析

### 3.1 主数据源：JSONL Transcript

**位置**: `~/.claude/projects/{project_hash}/*.jsonl`

**单行结构**（关键字段）:
```json
{
  "id": "msg_xxx",
  "type": "user|assistant|system",
  "timestamp": "2026-05-27T10:30:00Z",
  "message": {
    "content": [...],
    "model": "claude-sonnet-4-6",
    "usage": {
      "input_tokens": 12345,
      "output_tokens": 5678,
      "cache_creation_input_tokens": 2000,
      "cache_read_input_tokens": 8000
    }
  },
  "tools": [
    {
      "name": "Read|Write|Edit|Bash|Agent|Task|...",
      "input": {...},
      "output": "..."
    }
  ]
}
```

**关键提取逻辑**:
- `message.usage` → Token 统计（仅 assistant 类型消息）
- `tools[].name` → 工具调用类型分类
- `message.content[].type == "tool_use"` → 识别 Edit/Write 操作用于编辑决策追踪
- `timestamp` → 时间线构建

### 3.2 辅助数据源：Git

| 数据 | Git 命令 | 用途 |
|------|---------|------|
| Session 期间变更文件 | `git diff --name-only HEAD@{session_start}..HEAD` | 将 session 关联到具体文件 |
| Session 期间 commits | `git log --oneline --after={session_start} --before={session_end}` | Cost-per-Commit 计算 |
| 变更行数统计 | `git diff --stat HEAD@{session_start}..HEAD` | LoC 产出度量 |
| Commit messages | `git log --format="%s"` | 决策价值信号提取 |

### 3.3 辅助数据源：文件系统

| 数据 | 路径 | 用途 |
|------|------|------|
| Memory 条目 | `.claude/memory/*.md` + `MEMORY.md` | 知识积累度量 |
| 新增/修改的文档 | `docs/reports/*.md`, `docs/architecture/*.md` | 决策价值度量 |
| Skill 定义 | `.claude/skills/*.md` (如存在) | 能力建设度量 |
| 当前 session JSONL | 通过 Claude Code 环境变量或最近修改文件推断 | 实时追踪入口 |

### 3.4 现有工具复用评估

| 工具 | 可复用部分 | 适用性 |
|------|-----------|--------|
| **context-stats** | 状态行渲染、JSONL 解析器 | 高 — Python 生态，可直接集成 |
| **claude-monitor** | WebSocket dashboard, SQLite schema | 中 — Go 语言，需跨语言调用 |
| **toktrack** | 多 CLI 支持、性能优化思路 | 低 — Rust 语言，但算法可参考 |
| **cc-live** | 实时刷新逻辑 | 中 — Node.js，逻辑简单可移植 |
| **Scopeon** | 成本分解、缓存命中率计算 | 高 — 概念直接复用 |

**推荐策略**：自建核心引擎（Python），参考 context-stats 的 JSONL 解析逻辑和 Scopeon 的成本模型，保持轻量零外部依赖。

---

## 4. 系统架构

### 4.1 分层架构

```
┌──────────────────────────────────────────────────────────────┐
│                      CLI Layer (Click)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │  watch   │ │  report  │ │  trend   │ │   config     │   │
│  │  实时监控  │ │  会话报告 │ │  趋势分析  │ │   配置管理   │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘   │
├───────┼────────────┼────────────┼───────────────┼───────────┤
│       ▼            ▼            ▼               ▼            │
│                      Service Layer                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ Session  │ │ Token    │ │ Git      │ │ Report       │   │
│  │ Tracker  │ │ Analyzer │ │ Linker   │ │ Generator    │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘   │
│       │            │            │               │            │
├───────┼────────────┼────────────┼───────────────┼───────────┤
│       ▼            ▼            ▼               ▼            │
│                      Domain Layer                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ JSONL    │ │ BEI      │ │ Cost     │ │ Alert        │   │
│  │ Parser   │ │ Engine   │ │ Model    │ │ Engine       │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘   │
│       │            │            │               │            │
├───────┼────────────┼────────────┼───────────────┼───────────┤
│       ▼            ▼            ▼               ▼            │
│                      Data Layer                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SQLite (audit.db)                                    │   │
│  │  sessions | turns | tool_calls | edits | metrics     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  JSONL Files (~/.claude/projects/*/                   │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 模块职责

| 模块 | 文件 | 职责 |
|------|------|------|
| **JSONL Parser** | `parser.py` | 读取/增量解析 JSONL transcript，提取 usage 和 tool 信息 |
| **Git Linker** | `git_linker.py` | 将 session 时间窗关联到 git diff/commit/log |
| **Cost Model** | `cost_model.py` | Anthropic 定价表 → USD 成本计算（microdollar 整数存储） |
| **BEI Engine** | `bei_engine.py` | 五维度加权评分计算 |
| **Session Tracker** | `tracker.py` | 实时 session 状态追踪（增量 token 累积、产出计数） |
| **Alert Engine** | `alerts.py` | 阈值检测与告警生成 |
| **Report Generator** | `reporter.py` | Markdown/JSON 报告生成 |
| **CLI** | `cli.py` | Click 命令行接口 |
| **DB Store** | `db.py` | SQLite 读写封装 |

### 4.3 目录结构

```
tools/token_audit/
├── __init__.py
├── __main__.py          # python -m tools.token_audit entry
├── cli.py               # Click CLI: watch, report, trend, config
├── parser.py            # JSONL 解析器
├── git_linker.py        # Git 数据关联
├── cost_model.py        # 定价表 + 成本计算
├── bei_engine.py        # BEI 五维评分引擎
├── tracker.py           # 实时 session 追踪
├── alerts.py            # 告警规则
├── reporter.py          # 报告生成器
├── db.py                # SQLite 持久化
├── schema.sql           # 数据库 schema DDL
├── config.yaml          # 默认配置（BEI 权重、告警阈值、定价表）
└── tests/
    ├── test_parser.py
    ├── test_bei_engine.py
    ├── test_cost_model.py
    └── test_git_linker.py
```

---

## 5. 数据模型设计

### 5.1 SQLite Schema

```sql
-- Session 主表
CREATE TABLE sessions (
    id              TEXT PRIMARY KEY,          -- session UUID
    project_name    TEXT NOT NULL,             -- 项目名 (GCS_A)
    jsonl_path      TEXT,                      -- JSONL 文件路径
    model_id        TEXT,                      -- 主模型 ID
    started_at      TEXT NOT NULL,             -- ISO 8601
    ended_at        TEXT,                      -- ISO 8601 (NULL = 进行中)
    
    -- Token 统计
    total_input_tokens          INTEGER DEFAULT 0,
    total_output_tokens         INTEGER DEFAULT 0,
    total_cache_read_tokens     INTEGER DEFAULT 0,
    total_cache_creation_tokens INTEGER DEFAULT 0,
    
    -- 成本 (microdollars, 1/1,000,000 USD)
    total_cost_usd_micro INTEGER DEFAULT 0,
    
    -- 产出统计
    lines_added         INTEGER DEFAULT 0,
    lines_removed       INTEGER DEFAULT 0,
    files_touched       INTEGER DEFAULT 0,
    commits_count       INTEGER DEFAULT 0,
    
    -- 编辑决策
    edit_accept_count   INTEGER DEFAULT 0,
    edit_reject_count   INTEGER DEFAULT 0,
    
    -- 工具使用
    tool_calls_total    INTEGER DEFAULT 0,
    subagent_spawns     INTEGER DEFAULT 0,
    
    -- 知识与决策
    skills_invoked      TEXT,                   -- JSON array
    memory_entries      TEXT,                   -- JSON array
    docs_touched        TEXT,                   -- JSON array
    
    -- BEI
    bei_output_score    REAL,
    bei_quality_score   REAL,
    bei_decision_score  REAL,
    bei_knowledge_score REAL,
    bei_efficiency_score REAL,
    bei_composite       REAL,
    
    -- 元数据
    tags                TEXT,                   -- JSON array, 用户自定义标签
    notes               TEXT,                   -- 用户备注
    created_at          TEXT DEFAULT (datetime('now'))
);

-- 轮次表
CREATE TABLE turns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL REFERENCES sessions(id),
    turn_index      INTEGER NOT NULL,          -- 会话内轮次序号 (0-based)
    role            TEXT NOT NULL,             -- user | assistant | system
    timestamp       TEXT NOT NULL,             -- ISO 8601
    
    -- Token 用量 (仅 assistant turn)
    input_tokens            INTEGER DEFAULT 0,
    output_tokens           INTEGER DEFAULT 0,
    cache_read_tokens       INTEGER DEFAULT 0,
    cache_creation_tokens   INTEGER DEFAULT 0,
    
    -- 延迟
    latency_ms      INTEGER,                   -- 响应延迟
    
    -- 模型信息
    model_id        TEXT,
    
    UNIQUE(session_id, turn_index)
);

-- 工具调用表
CREATE TABLE tool_calls (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL REFERENCES sessions(id),
    turn_index      INTEGER NOT NULL,
    tool_name       TEXT NOT NULL,             -- Read | Write | Edit | Bash | Agent | Task | ...
    tool_input      TEXT,                      -- JSON
    tool_result     TEXT,                      -- truncated if too large
    duration_ms     INTEGER,
    success         INTEGER DEFAULT 1,         -- 0 = error
    timestamp       TEXT NOT NULL
);

-- 编辑记录表
CREATE TABLE edits (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL REFERENCES sessions(id),
    turn_index      INTEGER NOT NULL,
    file_path       TEXT NOT NULL,
    lines_added     INTEGER DEFAULT 0,
    lines_removed   INTEGER DEFAULT 0,
    accepted        INTEGER DEFAULT 1,         -- 1 = accepted, 0 = rejected
    timestamp       TEXT NOT NULL
);

-- 每日汇总表 (物化视图替代)
CREATE TABLE daily_summary (
    date            TEXT PRIMARY KEY,           -- YYYY-MM-DD
    sessions_count  INTEGER DEFAULT 0,
    total_input_tokens      INTEGER DEFAULT 0,
    total_output_tokens     INTEGER DEFAULT 0,
    total_cost_usd_micro    INTEGER DEFAULT 0,
    lines_added             INTEGER DEFAULT 0,
    lines_removed           INTEGER DEFAULT 0,
    commits_count           INTEGER DEFAULT 0,
    avg_cache_hit_rate      REAL,
    avg_bei_composite       REAL
);

-- 告警日志表
CREATE TABLE alert_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT,
    alert_type      TEXT NOT NULL,             -- cost_spike | efficiency_drop | cache_drop | rejection_spike | agent_loop
    severity        TEXT NOT NULL,             -- warning | critical
    message         TEXT NOT NULL,
    context         TEXT,                      -- JSON with relevant data
    acknowledged    INTEGER DEFAULT 0,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- 索引
CREATE INDEX idx_turns_session ON turns(session_id);
CREATE INDEX idx_tool_calls_session ON tool_calls(session_id);
CREATE INDEX idx_edits_session ON edits(session_id);
CREATE INDEX idx_sessions_started ON sessions(started_at);
CREATE INDEX idx_sessions_project ON sessions(project_name);
```

### 5.2 Python 数据类

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class BEIDimension(Enum):
    OUTPUT = "output"
    QUALITY = "quality"
    DECISION = "decision"
    KNOWLEDGE = "knowledge"
    EFFICIENCY = "efficiency"

@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cache_hit_rate(self) -> float:
        denom = self.cache_read_tokens + self.input_tokens
        return self.cache_read_tokens / denom if denom > 0 else 0.0

@dataclass
class SessionSnapshot:
    """Session 运行时的内存快照"""
    session_id: str
    project_name: str
    started_at: datetime
    model_id: str = ""
    ended_at: Optional[datetime] = None

    tokens: TokenUsage = field(default_factory=TokenUsage)
    cost_usd_micro: int = 0

    lines_added: int = 0
    lines_removed: int = 0
    commits_count: int = 0
    edits_accepted: int = 0
    edits_rejected: int = 0
    tool_calls: int = 0
    subagent_spawns: int = 0
    skills_invoked: list[str] = field(default_factory=list)
    memory_entries: list[str] = field(default_factory=list)

    bei: Optional["BEIScores"] = None

@dataclass
class BEIScores:
    output: float      # 0..1
    quality: float     # 0..1
    decision: float    # 0..1
    knowledge: float   # 0..1
    efficiency: float  # 0..1

    @property
    def composite(self) -> float:
        # 默认等权，可从 config 读取权重
        return (self.output + self.quality + self.decision +
                self.knowledge + self.efficiency) / 5.0
```

---

## 6. BEI 计算引擎

### 6.1 各维度计算公式

#### Output Score（代码产出）

```
raw_output = (lines_added + lines_removed) / max(total_tokens / 1_000_000, 1)
baseline = project_historical_p75_output_per_1M_tokens  # 从 SQLite 查询
output_score = min(raw_output / baseline, 1.0)
```

无历史数据时使用默认 baseline（可从行业基准估算，如 200 LoC / 1M tokens）。

#### Quality Score（质量信号）

```
edit_rejection_rate = edits_rejected / max(edits_accepted + edits_rejected, 1)
quality_score = 1.0 - edit_rejection_rate
```

#### Decision Score（决策价值）

```
# 从 git commit messages 中识别架构/设计关键词
architecture_signals = count_keywords(commit_messages, {
    "architecture", "design", "refactor", "extract", "introduce",
    "module", "boundary", "contract", "interface", "separate"
})
# 文档变更
docs_touched_signal = len(docs_touched) > 0
# 归一化
decision_score = min(
    (architecture_signals * 0.15 + (1.0 if docs_touched_signal else 0.0) * 0.3) / 0.45,
    1.0
)
```

#### Knowledge Score（知识积累）

```
memory_signal = min(len(memory_entries) / 3.0, 1.0)    # 3 entries = max score
skill_signal = min(len(skills_invoked) / 5.0, 1.0)      # 5 invocations = max score
knowledge_score = memory_signal * 0.4 + skill_signal * 0.6
```

#### Efficiency Score（成本效率）

```
cache_rate = cache_hit_rate                            # 0..1
cost_per_commit = total_cost_usd / max(commits_count, 1)
# 理想 cost_per_commit 暂设为 $0.50 (可配置)
cost_efficiency = max(1.0 - (cost_per_commit / 0.50), 0.0)
efficiency_score = cache_rate * 0.4 + cost_efficiency * 0.6
```

### 6.2 权重配置

```yaml
# config.yaml
bei:
  weights:
    output: 0.30
    quality: 0.25
    decision: 0.20
    knowledge: 0.10
    efficiency: 0.15
  baselines:
    output_per_1M_tokens: 200        # LoC / 1M tokens (可设 null 从历史计算)
    ideal_cost_per_commit_usd: 0.50  # USD
    max_memory_entries: 3
    max_skill_invocations: 5
```

### 6.3 BEI 评分解读

| BEI 范围 | 评级 | 含义 |
|----------|------|------|
| 0.80 - 1.00 | A (高效) | 单位 token 产出远高于基线，质量好，决策清晰 |
| 0.60 - 0.79 | B (良好) | 效率在正常范围，有优化空间 |
| 0.40 - 0.59 | C (一般) | 效率偏低，建议审视工作方式 |
| 0.20 - 0.39 | D (低效) | 显著低于基线，应优化提示策略或模型选择 |
| 0.00 - 0.19 | E (极低效) | 几乎无有效产出或大量 token 浪费 |

---

## 7. 实时数据流设计

### 7.1 实时追踪模式

```
┌─────────────────────────────────────────────┐
│              Real-Time Tracker               │
│                                              │
│  1. 发现当前 session 的 JSONL 文件           │
│     - 通过最近修改时间找到活跃 JSONL          │
│     - 或通过 Claude Code hook 传入路径       │
│                                              │
│  2. 增量读取 (tail -f 模式)                  │
│     - 记录上次读取的字节偏移量                │
│     - 每 5s 检查文件是否有新行写入            │
│     - 解析新行，增量更新 SessionSnapshot     │
│                                              │
│  3. 实时指标计算                             │
│     - Token 使用率、缓存命中率                │
│     - 成本累积速率 (USD/min)                 │
│     - 产出指标需要等到 Edit tool call         │
│       - Edit accept/reject 从工具调用链推断  │
│                                              │
│  4. 状态行刷新                               │
│     - 终端内显示精简的状态行                  │
│     - 包含：token 累积 | 成本 | 缓存率 | 轮次 │
│                                              │
│  5. 告警检测                                 │
│     - 每轮检测阈值                           │
│     - 超阈值 → 终端通知 + alert_log 写入     │
└─────────────────────────────────────────────┘
```

### 7.2 Session 发现策略

```python
def find_active_session(project_name: str) -> Optional[str]:
    """找到当前活跃 session 的 JSONL 路径"""
    projects_dir = Path.home() / ".claude" / "projects"
    
    # 策略 1: 通过 Claude Code 环境变量
    env_path = os.environ.get("CLAUDE_CODE_SESSION_PATH")
    if env_path and Path(env_path).exists():
        return env_path
    
    # 策略 2: 最近修改的 JSONL
    jsonl_files = []
    for proj_dir in projects_dir.iterdir():
        if proj_dir.is_dir():
            for f in proj_dir.glob("*.jsonl"):
                jsonl_files.append((f.stat().st_mtime, str(f)))
    
    if not jsonl_files:
        return None
    
    jsonl_files.sort(reverse=True)
    newest = jsonl_files[0][1]
    
    # 如果在最近 30 秒内修改过，认为是活跃 session
    if time.time() - jsonl_files[0][0] < 30:
        return newest
    
    return None
```

### 7.3 增量 JSONL 解析器

```python
class IncrementalJSONLParser:
    """增量读取 JSONL，支持断点续读"""
    
    def __init__(self, path: str):
        self.path = Path(path)
        self.offset = 0  # 字节偏移量
        self.session_id: Optional[str] = None
        
    def read_new_lines(self) -> list[dict]:
        """读取自上次偏移后的新行"""
        if not self.path.exists():
            return []
        
        size = self.path.stat().st_size
        if size < self.offset:
            # 文件被轮转，从头开始
            self.offset = 0
        
        with open(self.path, 'r', encoding='utf-8') as f:
            f.seek(self.offset)
            lines = f.readlines()
            self.offset = f.tell()
        
        records = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        
        return records
    
    def extract_usage(self, record: dict) -> Optional[TokenUsage]:
        """从单条 record 提取 token 用量"""
        if record.get("type") != "assistant":
            return None
        usage = record.get("message", {}).get("usage", {})
        if not usage:
            return None
        return TokenUsage(
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            cache_read_tokens=usage.get("cache_read_input_tokens", 0),
            cache_creation_tokens=usage.get("cache_creation_input_tokens", 0),
        )
    
    def extract_tools(self, record: dict) -> list[dict]:
        """从单条 record 提取工具调用"""
        tools = record.get("tools", [])
        if not tools:
            # 也检查 message.content 中的 tool_use 块
            content = record.get("message", {}).get("content", [])
            tools = [c for c in content if isinstance(c, dict) and c.get("type") == "tool_use"]
        return tools
```

### 7.4 实时状态行格式

```
╔══════════════════════════════════════════════════════════════╗
║ GCS Session Audit  │  T: 12  │  In: 45.2K  Out: 18.7K     ║
║ Cache: 62%  │  Cost: $0.34  │  Edits: 8A/2R  │  BEI: —    ║
║ ⚠ Cache hit rate dropped 30% vs 7-day avg                  ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 8. CLI 接口设计

### 8.1 命令总览

```
python -m tools.token_audit <command> [options]

Commands:
  watch      实时监控当前 session 的 token 消耗与产出
  report     生成 session 报告
  trend      显示历史趋势分析
  config     管理配置
  db         数据库维护
```

### 8.2 命令详情

#### `watch` — 实时监控

```bash
# 自动发现并监控活跃 session
python -m tools.token_audit watch

# 指定 session ID
python -m tools.token_audit watch --session abc123

# 设置刷新间隔
python -m tools.token_audit watch --interval 3

# JSON 输出模式（供其他工具消费）
python -m tools.token_audit watch --format json

# 仅监控，不写入数据库
python -m tools.token_audit watch --no-persist
```

#### `report` — 会话报告

```bash
# 最近一个 session 的报告
python -m tools.token_audit report

# 指定 session
python -m tools.token_audit report --session abc123

# 指定日期范围
python -m tools.token_audit report --from 2026-05-20 --to 2026-05-27

# 输出格式
python -m tools.token_audit report --format markdown  # 默认
python -m tools.token_audit report --format json
python -m tools.token_audit report --format html

# 指定输出路径
python -m tools.token_audit report --session abc123 --output report.md
```

#### `trend` — 趋势分析

```bash
# 7 天趋势
python -m tools.token_audit trend

# 30 天趋势
python -m tools.token_audit trend --days 30

# 指定指标
python -m tools.token_audit trend --metric bei_composite
python -m tools.token_audit trend --metric cost_per_commit
python -m tools.token_audit trend --metric cache_hit_rate
```

#### `config` — 配置管理

```bash
# 显示当前配置
python -m tools.token_audit config show

# 设置 BEI 权重
python -m tools.token_audit config set bei.weights.output 0.35

# 设置告警阈值
python -m tools.token_audit config set alerts.max_cost_per_session_usd 2.00
```

#### `db` — 数据库维护

```bash
# 从历史 JSONL 批量导入
python -m tools.token_audit db import --all
python -m tools.token_audit db import --since 2026-05-01

# 数据库统计信息
python -m tools.token_audit db stats

# 清理旧数据
python -m tools.token_audit db vacuum
```

---

## 9. 输出报告格式

### 9.1 Session 报告模板

```markdown
# Session Audit Report

**Session**: `abc123def` | **Date**: 2026-05-27 10:30 - 12:15 (1h45m)
**Model**: claude-sonnet-4-6 | **Project**: GCS_A
**BEI Rating**: B (0.72) — 良好

---

## Token & Cost Summary

| Metric | Value |
|--------|-------|
| Total Tokens | 345,200 |
| Input Tokens | 280,500 |
| Output Tokens | 64,700 |
| Cache Read Tokens | 120,300 |
| Cache Hit Rate | 30.0% |
| Estimated Cost | $1.72 USD |

## Output Summary

| Metric | Value |
|--------|-------|
| Lines Added | 245 |
| Lines Removed | 83 |
| Files Touched | 12 |
| Commits | 3 |
| Edits Accepted / Rejected | 18 / 4 (18% rejection) |
| Tool Calls | 47 |
| Subagents Spawned | 5 |

## Efficiency Metrics

| Metric | Value | Baseline | Status |
|--------|-------|----------|--------|
| Output-per-1M-Tokens | 950 LoC | 200 LoC | ↑ Above |
| Cost-per-Commit | $0.57 | $0.50 | ≈ Near |
| Edit Rejection Rate | 18% | <20% | ✓ Good |
| Cache Hit Rate | 30% | 45% (7d avg) | ⚠ Below |

## BEI Breakdown

| Dimension | Score | Weight | Contribution |
|-----------|-------|--------|-------------|
| Output | 0.95 | 30% | 0.285 |
| Quality | 0.82 | 25% | 0.205 |
| Decision | 0.60 | 20% | 0.120 |
| Knowledge | 0.40 | 10% | 0.040 |
| Efficiency | 0.45 | 15% | 0.068 |
| **Composite** | **0.72** | — | — |

## Alerts

- ⚠ Cache hit rate (30%) below 7-day average (45%)

## Top Tools

| Tool | Count | Avg Latency |
|------|-------|-------------|
| Edit | 22 | 1.2s |
| Read | 10 | 0.3s |
| Bash | 8 | 2.5s |
| Agent | 5 | 45.0s |
| Grep | 2 | 0.2s |

---

*Generated by GCS Token Audit v1.0.0 at 2026-05-27 12:16:00*
```

### 9.2 周度趋势报告模板

```markdown
# Weekly Token Efficiency Report

**Period**: 2026-05-20 — 2026-05-27
**Project**: GCS_A

---

## Overview

| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Sessions | 14 | 11 | +27% |
| Total Tokens | 4.2M | 3.1M | +35% |
| Total Cost | $18.70 | $13.20 | +42% |
| Commits | 28 | 24 | +17% |
| Avg BEI | 0.68 | 0.73 | -7% |

## Efficiency Trend

```
BEI Composite (7-day rolling)
1.00 ┤
0.80 ┤    ●───●───●
0.60 ┤  ●           ●───●
0.40 ┤
0.20 ┤
     ├────┼────┼────┼────┼────┼────┼────
     Mon  Tue  Wed  Thu  Fri  Sat  Sun
```

## Alerts This Week

| Date | Session | Alert | Severity |
|------|---------|-------|----------|
| 05-23 | xyz789 | Cost spike ($4.20) | Warning |
| 05-25 | def456 | Efficiency drop (-55%) | Critical |

## Recommendations

1. **Cache utilization declined** — Consider using context-stats cache keep-warm during long pauses
2. **Subagent spawning increased 40%** — Review Task agent necessity per session
3. **Two high-cost sessions** (xyz789, def456) account for 45% of weekly cost — analyze patterns
```

---

## 10. 告警规则设计

### 10.1 告警类型

```python
from enum import Enum

class AlertType(Enum):
    COST_SPIKE = "cost_spike"
    EFFICIENCY_DROP = "efficiency_drop"
    CACHE_DROP = "cache_drop"
    REJECTION_SPIKE = "rejection_spike"
    AGENT_LOOP = "agent_loop"

class AlertSeverity(Enum):
    WARNING = "warning"
    CRITICAL = "critical"
```

### 10.2 告警规则

| 规则 | 条件 | 严重度 | 冷却期 |
|------|------|--------|--------|
| COST_SPIKE | session_cost > max_cost_per_session | WARNING | 每 session 一次 |
| COST_SPIKE | session_cost > 2× max_cost_per_session | CRITICAL | 每 session 一次 |
| EFFICIENCY_DROP | output_per_token < 0.5× 7d_avg (session 结束评估) | CRITICAL | 每 session 一次 |
| EFFICIENCY_DROP | output_per_token < 0.7× 7d_avg (实时，至少 5 轮后) | WARNING | 每 30min 一次 |
| CACHE_DROP | cache_hit_rate < 0.7× 7d_avg (至少 5 轮后) | WARNING | 每 session 一次 |
| REJECTION_SPIKE | edit_rejection_rate > 40% (至少 5 edits 后) | WARNING | 每 30min 一次 |
| AGENT_LOOP | 相同 tool_name + 相似 input 连续 3+ 次 | CRITICAL | 每 10min 一次 |

### 10.3 默认阈值配置

```yaml
alerts:
  max_cost_per_session_usd: 2.00
  efficiency_drop_threshold: 0.5       # 50% below 7-day average
  cache_drop_threshold: 0.7            # 70% of 7-day average
  rejection_rate_threshold: 0.40       # 40%
  agent_loop_min_repetition: 3         # same tool+params 3+ times
  agent_loop_window_minutes: 10        # within 10 minutes
  cooldown:
    per_session: 1                     # once per session per alert type
    per_30min: 1                       # once per 30 min per real-time alert
```

---

## 11. 扩展性设计

### 11.1 多 Provider 支持

当前仅支持 Anthropic（Claude Code JSONL）。扩展路径：

```python
class TranscriptParser(ABC):
    """抽象解析器接口"""
    @abstractmethod
    def parse_record(self, record: dict) -> Optional[TokenUsage]: ...
    @abstractmethod
    def extract_tools(self, record: dict) -> list[dict]: ...

class ClaudeCodeParser(TranscriptParser):
    """Claude Code JSONL 解析器"""
    ...

class CodexParser(TranscriptParser):
    """OpenAI Codex CLI JSONL 解析器"""
    ...

class GenericAPIParser(TranscriptParser):
    """通用 API 日志解析器"""
    ...
```

### 11.2 多项目支持

当前聚焦 GCS_A，扩展为多项目：

- `sessions` 表的 `project_name` 字段已预留
- 不同项目的 baseline 独立计算
- 全局视图通过 `project_name = '*'` 聚合

### 11.3 插件化告警

```python
class AlertRule(ABC):
    @abstractmethod
    def evaluate(self, snapshot: SessionSnapshot, history: list[SessionSnapshot]) -> list[Alert]: ...

# 内置规则
class CostSpikeRule(AlertRule): ...
class EfficiencyDropRule(AlertRule): ...

# 用户自定义规则通过 config.yaml 注册
```

### 11.4 Web Dashboard (Phase 4)

如果后续需要 Web Dashboard，方案：

- **轻量方案**：SQLite + datasette（零代码 dashboard）
- **实时方案**：复用 claude-monitor 的 WebSocket 架构 + 自建 BEI overlay
- **专业方案**：OpenTelemetry → Prometheus → Grafana（与 SigNoz 方案一致）

---

## 附录 A: Anthropic 模型定价表 (2026-05)

| 模型 | Input / 1M tokens | Output / 1M tokens | Cache Write / 1M | Cache Read / 1M |
|------|-------------------|-------------------|------------------|-----------------|
| Claude Opus 4.7 | $15.00 | $75.00 | $30.00 | $1.50 |
| Claude Sonnet 4.6 | $3.00 | $15.00 | $6.00 | $0.30 |
| Claude Haiku 4.5 | $0.80 | $4.00 | $1.60 | $0.08 |

成本计算公式:
```
cost = (input_tokens × input_price + output_tokens × output_price
        + cache_creation_tokens × cache_write_price
        + cache_read_tokens × cache_read_price) / 1_000_000
```

---

> **维护说明**：定价表应在 Anthropic 发布新模型或调整价格时更新。Schema 变更通过 `db migrate` 子命令管理。

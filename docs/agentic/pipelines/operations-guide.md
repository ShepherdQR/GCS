# GCS Pipeline Operations Guide

**Date**: 2026-05-30
**Version**: v1

## 概述

GCS 项目有 10 条生产线（Pipeline），覆盖从求解器缺陷发现到仓库审计的完整质量保障体系。
本文档说明如何启动、调度、监控和管理这些生产线。

---

## 快速启动

### 1. 列出所有可用生产线

```bash
python tools/solver_testing/pipelines/run.py list
```

输出示例：
```
GCS Pipeline Registry
======================================================================

  Tier P0 — Core Solver Quality
  ────────────────────────────────────────────────────────────
  defect-discovery
    Enumerate constraint graphs, mutate values, batch-solve, capture defects...
    Runtime: ~2min (smoke) / 15min (standard) / 2hr (full) [presets: smoke, standard, full]
  solver-regression
    Run solver on fixture corpus, compare against baseline, detect regressions.
    Runtime: ~5min (typical corpus)
  ...
```

### 2. 运行一条生产线

```bash
# 使用预设运行 (defect-discovery 有 smoke/standard/full 三档)
python tools/solver_testing/pipelines/run.py run defect-discovery --preset smoke

# 使用 JSON 配置文件运行
python tools/solver_testing/pipelines/run.py run solver-regression --config regression-config.json

# 查看某条线的详细信息
python tools/solver_testing/pipelines/run.py run info numeric-stability
```

### 3. 在 Claude Code 会话中启动

在对话中直接说：
- "run the defect-discovery pipeline with preset smoke"
- "run solver regression on the fixture corpus"
- "run the nightly immune diagnostic"

Claude Code 会自动定位对应的 Python 模块并执行。

---

## 统一调度器

`run.py` 是所有生产线的统一入口，支持四个子命令：

| 命令 | 用途 |
|------|------|
| `list` | 列出所有已注册的生产线 |
| `run <id>` | 运行指定生产线 |
| `info <id>` | 查看生产线详细信息 |
| `schedule <id>` | 显示调度配置说明 |

### 配置文件格式

每条生产线接受 JSON 配置文件，格式如下：

```json
{
  "corpus_path": "fixtures/scene/",
  "baseline_path": "tools/solver_testing/baselines/v1.json",
  "tolerance": 1e-6,
  "timeout": 10
}
```

配置文件放入 `tools/solver_testing/configs/<pipeline-id>.json`，便于复用。

---

## 四种启动方式

### 方式 1：直接 CLI（开发调试）

```bash
# 统一入口
python tools/solver_testing/pipelines/run.py run <id> --config config.json

# 或直接调用模块
python tools/solver_testing/pipelines/regression.py --corpus fixtures/scene/ --baseline baseline.json
```

**适用场景**：本地开发、一次性测试、调试

### 方式 2：Claude Code Skill（交互式）

每条 active 流水线在 `docs/agentic/pipelines/<id>/skill.md` 中有对应的 skill 定义。
当用户在对话中提到匹配的关键词时，Claude Code 自动调用。

**Skill 触发词示例**：

| 关键词 | 触发的流水线 |
|--------|------------|
| "find solver defects", "mutation test" | `defect-discovery` |
| "regression test", "compare to baseline" | `solver-regression` |
| "test numeric stability", "extreme values" | `numeric-stability` |
| "certify diagnostics", "negative test" | `diagnostic-certification` |
| "check contracts", "audit imports" | `contract-compliance` |
| "round trip test", "serialization check" | `io-round-trip` |
| "generate fixtures", "coverage report" | `scene-generation` |
| "benchmark solver", "measure performance" | `performance-benchmark` |
| "compare solvers", "external solver" | `cross-solver-compare` |
| "audit repo", "check stale files" | `repository-audit` |

**适用场景**：日常对话中的按需触发

### 方式 3：Scheduled Task（定期自动）

通过 Claude Code 的 `mcp__scheduled-tasks__create_scheduled_task` 工具排产。

```bash
# 每日凌晨 3:17 运行缺陷发现 (standard preset)
/schedule-task create \
  --task-id defect-discovery-daily \
  --cron "17 3 * * *" \
  --prompt "Run defect-discovery pipeline with preset standard on enumeration 3RS/5G/5C. Report new defects found."

# 每周一凌晨 4:23 运行数值稳定性
/schedule-task create \
  --task-id numeric-stability-weekly \
  --cron "23 4 * * 1" \
  --prompt "Run numeric-stability pipeline on all active fixtures. Report stability regressions."

# 每次 push 后运行回归 (通过 CI 触发，非 cron)
# - 在 CI workflow 中调用: python tools/solver_testing/pipelines/run.py run solver-regression
```

**推荐排产表**：

| 频率 | 时间 | 流水线 | Preset |
|------|------|--------|--------|
| 每日 | 03:17 | `defect-discovery` | standard |
| 每日 | 03:41 | `repository-audit` | — |
| 每日 | 04:05 | `nightly-immune` | — |
| 每周一 | 04:23 | `numeric-stability` | — |
| 每周一 | 04:47 | `performance-benchmark` | — |
| 每周一 | 05:11 | `solver-regression` | — |
| 每周一 | 05:35 | `contract-compliance` | — |
| 每月 1 日 | 06:00 | `cross-solver-compare` | — |

### 方式 4：Institutional Agent 编排（多流水线组合）

通过 `orchestrator` agent 编排多条流水线的串联/并联执行。

示例 prompt：
```
Orchestrate a full quality gate run:
1. Run repository-audit (P3) — fast, no deps
2. In parallel: contract-compliance (P1), io-round-trip (P1), diagnostics-certification (P1)
3. In parallel: solver-regression (P0), numeric-stability (P0), performance-benchmark (P2)
4. Run defect-discovery (P0) — depends on scene-generation results
5. Aggregate all reports into a nightly dashboard
```

---

## 会话管理

### 启动一个生产线会话

推荐使用 git worktree 隔离每条生产线的文件变更：

```bash
# 创建独立 worktree
git worktree add .claude/worktrees/pipeline-defect-discovery-$(date +%Y%m%d) master

# 在该 worktree 中运行
cd .claude/worktrees/pipeline-defect-discovery-$(date +%Y%m%d)
python tools/solver_testing/pipelines/run.py run defect-discovery --preset standard
```

或通过 Claude Code 的 `EnterWorktree` 工具：
```
> start a worktree for running the defect-discovery pipeline
```

### 运行历史追踪

每条生产线的运行结果存储在对应位置：

| 流水线 | 产物位置 |
|--------|---------|
| `defect-discovery` | `tools/solver_testing/.defects/` + task card |
| `solver-regression` | `tools/solver_testing/baselines/` + 回归报告 |
| `numeric-stability` | 稳定性报告 JSON |
| `diagnostic-certification` | 认证报告 JSON |
| `contract-compliance` | `ComplianceReport` JSON |
| `io-round-trip` | `RoundTripReport` JSON |
| `scene-generation` | `tools/scene_generation/.store/` + coverage report |
| `performance-benchmark` | `tools/solver_testing/benchmarks/trend.db` |
| `cross-solver-compare` | `ComparisonReport` JSON |
| `repository-audit` | `AuditReport` JSON |

---

## 监控与告警

### 健康仪表盘

`nightly-immune` 流水线聚合所有检查，生成每日健康仪表盘：

```bash
python tools/solver_testing/pipelines/run.py run nightly-immune
```

输出位置：`docs/agentic/nightly-runs/<date>/dashboard.md`

### 关键指标

| 指标 | 来源 | 告警阈值 |
|------|------|---------|
| 新缺陷数 | `defect-discovery` | >0 new crash severity |
| 回归数 | `solver-regression` | >0 status_changed |
| 性能退化 | `performance-benchmark` | 耗时 > baseline × 1.2 |
| 合约违规 | `contract-compliance` | >0 error severity |
| 诊断漏报 | `diagnostic-certification` | 通过率 < 100% |
| IO 往返失败 | `io-round-trip` | 通过率 < 100% |
| 求解器崩溃 | `numeric-stability` | 任何值区间内崩溃 |

---

## 配置管理

### 推荐目录结构

```
tools/solver_testing/
├── configs/                    # 生产线 JSON 配置文件
│   ├── defect-discovery-smoke.json
│   ├── defect-discovery-standard.json
│   ├── regression-v1.json
│   └── stability-logspace.json
├── baselines/                  # solver-regression baseline 文件
│   └── v1.json
├── benchmarks/
│   └── trend.db                # 性能趋势数据库
├── .defects/                   # 缺陷记录库
└── pipelines/
    ├── run.py                  # 统一调度器 ← 本文档重点
    ├── __init__.py
    ├── defect_discovery.py
    ├── regression.py
    └── ...
```

### 创建新的生产线配置

```bash
# 1. 创建配置文件
cat > tools/solver_testing/configs/my-defect-run.json << 'EOF'
{
  "enumeration_id": "my_custom_run",
  "num_geometries": 5,
  "num_constraints": 5,
  "num_rigid_sets": 3,
  "require_biconnected": true,
  "max_graphs": 500,
  "strategies": ["positive_to_negative", "epsilon_perturb", "extreme_value"],
  "timeout_seconds": 15
}
EOF

# 2. 运行
python tools/solver_testing/pipelines/run.py run defect-discovery --config tools/solver_testing/configs/my-defect-run.json
```

---

## 生产线依赖关系

```
                    ┌──────────────────────┐
                    │   scene-generation   │  P2 — 生成 fixture
                    └──────────┬───────────┘
                               │ produces fixtures
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │defect-discov.│  │solver-regres.│  │numeric-stab. │  P0 — 消费 fixture
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                 │
           ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  task card   │  │regress. rpt  │  │stability rpt │
    └──────────────┘  └──────────────┘  └──────────────┘
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │diag.-certif. │  │io-round-trip │  │contract-comp.│  P1 — 质量门禁
    └──────────────┘  └──────────────┘  └──────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   nightly-immune     │  P3 — 聚合仪表盘
                    └──────────────────────┘
```

---

## 故障排查

### 生产线启动失败

```bash
# 检查 Python 导入
python -c "from tools.solver_testing.pipelines import DefectDiscoveryPipeline; print('OK')"

# 检查求解器可用性
python -c "from tools.solver_testing.runner import find_solver; print(find_solver())"

# 查看生产线详细信息
python tools/solver_testing/pipelines/run.py info defect-discovery
```

### 生产线运行超时

- 减小 `max_graphs`（defect-discovery, scene-generation）
- 减小 `timeout_seconds`（solver 调用）
- 使用 `--preset smoke` 代替 `standard`
- 检查 GCS.exe 是否响应：`out/build/clang-ninja/GCS.exe fixtures/scene/basic/g1.txt`

### 产物丢失

- 缺陷库：检查 `tools/solver_testing/.defects/` 目录权限
- 趋势库：检查 `tools/solver_testing/benchmarks/trend.db` SQLite 文件
- 任务卡：检查 `docs/agentic/tasks/` 目录权限

---

## 添加新生产线

1. 在 `docs/agentic/pipelines/<id>/` 创建文档（README + parameters + skill + development-plan）
2. 在 `tools/solver_testing/pipelines/<id>.py` 实现 Pipeline 类
3. 在 `run.py` 的 `PIPELINE_REGISTRY` 中注册
4. 在 `__init__.py` 中添加导出
5. 运行 `python tools/solver_testing/pipelines/run.py list` 验证

---

## 总结

| 你想做的事 | 命令 |
|-----------|------|
| 列出所有生产线 | `python tools/solver_testing/pipelines/run.py list` |
| 快速测试缺陷发现 | `python tools/solver_testing/pipelines/run.py run defect-discovery --preset smoke` |
| 完整缺陷扫描 | `python tools/solver_testing/pipelines/run.py run defect-discovery --preset standard` |
| 求解器回归测试 | `python tools/solver_testing/pipelines/run.py run solver-regression --config config.json` |
| 数值稳定性检查 | `python tools/solver_testing/pipelines/run.py run numeric-stability --config config.json` |
| 诊断认证 | `python tools/solver_testing/pipelines/run.py run diagnostic-certification` |
| 合约审计 | `python tools/solver_testing/pipelines/run.py run contract-compliance` |
| IO 往返测试 | `python tools/solver_testing/pipelines/run.py run io-round-trip --config config.json` |
| 生成场景 | `python tools/solver_testing/pipelines/run.py run scene-generation --config config.json` |
| 性能基准 | `python tools/solver_testing/pipelines/run.py run performance-benchmark --config config.json` |
| 跨求解器对比 | `python tools/solver_testing/pipelines/run.py run cross-solver-compare --config config.json` |
| 仓库审计 | `python tools/solver_testing/pipelines/run.py run repository-audit` |
| 查看调度配置 | `python tools/solver_testing/pipelines/run.py schedule defect-discovery` |
| 在会话中启动 | 直接说 "run the defect-discovery pipeline" |
| 定期自动运行 | 使用 `/schedule-task create` 创建 cron 任务 |

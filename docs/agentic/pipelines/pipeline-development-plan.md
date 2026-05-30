# GCS Pipeline Development Plan

**Date**: 2026-05-30
**Status**: working draft
**Owner**: gcs-architecture-steward

## 概述

本文档规划 GCS 项目的生产线（Pipeline）体系。每条流水线将重复性的人工测试/验证
工作自动化，通过参数化配置支持不同的运行模式（交互式、定期门禁、自主循环）。

## 设计原则

1. **单一职责**：每条流水线做一件事，输出一种明确的产物（任务卡、报告、fixture）
2. **参数外置**：所有可变参数通过 JSON/env/CLI 传入，不硬编码
3. **可排产**：每条流水线可通过 cron 或 /loop 定期运行
4. **可组合**：多条流水线通过 agent 编排形成更复杂的流程
5. **可观测**：每次运行产生 trace、summary、defect records

## 流水线矩阵

### Tier 1 — 核心求解器质量 (P0)

| ID | Pipeline | 目的 | 输入 | 输出 | 触发 | 状态 |
|----|----------|------|------|------|------|------|
| `defect-discovery` | 缺陷发现 | 穷举约束图，变异测试 | N,G,K参数 | 缺陷库+任务卡 | 手动/定期 | **active** |
| `solver-regression` | 求解器回归 | fixture语料库批量求解，对比基线 | fixture corpus | 回归报告 | 每次PR/每日 | proposed |
| `numeric-stability` | 数值稳定性 | 极端值/边界值/退化几何测试 | 参数空间 | 稳定性报告 | 每周 | proposed |

### Tier 2 — 合约与诊断 (P1)

| ID | Pipeline | 目的 | 输入 | 输出 | 触发 | 状态 |
|----|----------|------|------|------|------|------|
| `diagnostic-certification` | 诊断认证 | 验证已知坏输入产生正确诊断 | 负样本语料 | 诊断正确性报告 | 每次PR | proposed |
| `contract-compliance` | 合约合规 | 验证模块边界和接口契约 | 合约定义 | 合规报告 | 每周 | proposed |
| `io-round-trip` | IO往返 | 序列化→反序列化→求解→对比 | scene fixtures | 往返一致性报告 | 每次PR | proposed |

### Tier 3 — 场景与性能 (P2)

| ID | Pipeline | 目的 | 输入 | 输出 | 触发 | 状态 |
|----|----------|------|------|------|------|------|
| `scene-generation` | 场景生成 | 根据覆盖目标生成fixture | 覆盖策略 | fixture + 报告 | 按需 | proposed |
| `performance-benchmark` | 性能基准 | 求解时间/内存/收敛性测量 | fixture corpus | 性能趋势报告 | 每周 | proposed |
| `cross-solver-compare` | 跨求解器对比 | GCS vs 外部求解器 | benchmark set | 对比报告 | 按需 | proposed |

### Tier 4 — 治理与审计 (P3)

| ID | Pipeline | 目的 | 输入 | 输出 | 触发 | 状态 |
|----|----------|------|------|------|------|------|
| `repository-audit` | 仓库审计 | 文件分类、快照、趋势 | repo state | 审计报告 | 每日 | proposed |
| `token-audit` | Token审计 | AI会话token消耗追踪 | session transcripts | 成本/效率报告 | 每日/每周 | proposed |
| `nightly-immune` | 夜间免疫诊断 | 全模块综合健康检查 | all modules | 健康仪表盘 | 每日 | proposed |

## 详细规格

### `solver-regression` — 求解器回归流水线

**目的**：每次求解器代码变更后，在 fixture 语料库上批量求解，对比 baseline 结果，
发现回归（原本能解的不能解了，或输出发生意外变化）。

**流程**：
```
Fixture Corpus → Batch Solve → Compare to Baseline → Diff Report → Task Card
```

**参数**：
- `corpus_path`: fixture 语料库路径
- `baseline_path`: baseline 结果存储路径
- `compare_fields`: 对比字段（status, rank, residual_norm, etc.）
- `tolerance`: 浮点数对比容差

**工具需求**：
- `tools/solver_testing/regression.py`：批量求解 + baseline 对比
- Baseline 结果格式定义

**预计代码量**：~400 行

---

### `numeric-stability` — 数值稳定性流水线

**目的**：系统化测试求解器在极端数值条件下的行为，测量条件数、秩估计、残差范数。

**流程**：
```
Parameter Space → Extreme Value Generation → Batch Solve → Condition Analysis → Stability Report
```

**参数**：
- `value_ranges`: 约束值范围（如 [1e-12, 1e12]）
- `geometry_perturbations`: 几何扰动幅度
- `metrics`: 测量指标（condition_number, rank_stability, residual_growth）

**工具需求**：
- 扩展 `mutator.py` 添加数值梯度变异
- `tools/solver_testing/stability.py`：条件数追踪

**预计代码量**：~500 行

---

### `diagnostic-certification` — 诊断认证流水线

**目的**：构造已知有特定错误的场景（负距离、退化几何、过约束、欠约束），
验证求解器输出正确的诊断信息和错误码。

**流程**：
```
Negative Corpus → Solve → Parse Diagnostics → Compare to Expected → Certification Report
```

**参数**：
- `corpus_path`: 负样本语料库
- `expected_diagnostics`: 每个场景的期望诊断码
- `strict_mode`: 是否要求精确匹配

**工具需求**：
- `tools/solver_testing/diagnostics_cert.py`：诊断比对引擎
- 负样本语料库（可复用 `defect-discovery` 的缺陷库）

**预计代码量**：~350 行

---

### `io-round-trip` — IO 往返流水线

**目的**：场景 JSON → 求解器文本格式 → 再解析 → 再求解，验证两次求解结果一致。

**流程**：
```
Scene → Serialize (JSON) → Serialize (Text) → Parse → Solve → Compare → Round-Trip Report
```

**参数**：
- `fixture_paths`: fixture 列表
- `formats`: 测试的序列化格式（json, custom_text_v1）

**工具需求**：
- 扩展 `runner.py` 支持格式转换链
- `tools/solver_testing/roundtrip.py`

**预计代码量**：~300 行

---

### `performance-benchmark` — 性能基准流水线

**目的**：在 fixture 语料库上测量求解性能，追踪趋势。

**流程**：
```
Fixture Corpus → Timed Solve → Collect Metrics → Trend DB → Report
```

**度量指标**：
- `duration_ms`: 求解耗时
- `iterations`: 迭代次数
- `memory_kb`: 内存峰值
- `convergence_rate`: 收敛率

**参数**：
- `corpus_path`: fixture 语料库
- `warmup_runs`: 预热运行次数
- `measure_runs`: 测量运行次数
- `trend_db_path`: 趋势数据库路径

**工具需求**：
- `tools/solver_testing/benchmark.py`：计时+趋势存储
- SQLite 或 JSON 趋势存储

**预计代码量**：~400 行

---

### `nightly-immune` — 夜间免疫诊断流水线

**目的**：全模块综合健康检查——编译、CTest、Python 编译检查、fixture 完整性、
任务卡过期检查、合约一致性审计。

**流程**：
```
Build → CTest → Python Compile → Fixture Audit → Task Audit → Contract Audit → Health Dashboard
```

**已部分具备**：
- CTest 已有 128 个测试
- `agentic_toolkit.py validate-docs` 已有文档验证
- `fixture_library_gate.py` 已有 fixture 质量门禁

**工具需求**：
- `tools/nightly/` 或 cron task：编排所有检查
- 健康仪表盘（可复用 token-audit 的 dashboard 模式）

**预计代码量**：~300 行（编排脚本 + 报告聚合）

---

## 排产计划

| 阶段 | 时间 | 流水线 |
|------|------|--------|
| Phase 1 (当前) | 2026-05-30 | `defect-discovery` v1 active |
| Phase 2 | 2026-06 | `solver-regression` draft → active |
| Phase 3 | 2026-06 | `numeric-stability` + `diagnostic-certification` draft |
| Phase 4 | 2026-07 | `io-round-trip` + `contract-compliance` draft |
| Phase 5 | 2026-07 | `performance-benchmark` + `nightly-immune` draft |
| Phase 6 | 2026-08 | 全部流水线 active，cron 排产 |

## 工具链重构方向

随着流水线数量增长，`tools/solver_testing/` 将从单一模块发展为共享库：

```
tools/solver_testing/
  core/
    runner.py          — 求解器执行（共享）
    mutator.py         — 约束值变异（共享）
    defect_store.py    — 缺陷库（共享）
    serializer.py      — 场景序列化（共享，从 promotion.py 提取）
  pipelines/
    defect_discovery.py    — DDP 编排
    regression.py          — SRP 编排
    stability.py           — NSP 编排
    diagnostics_cert.py    — DCP 编排
    roundtrip.py           — IOP 编排
    benchmark.py           — PBP 编排
  reports/
    trend_db.py        — 趋势存储
    dashboard.py       — 仪表盘生成
```

## 与 Agent/Skill 体系的集成

每条 active 流水线应具备：
1. **Skill 定义**（`docs/agentic/pipelines/<id>/skill.md`）— Claude Code 可自动调用
2. **Scheduled Task**（通过 `mcp__scheduled-tasks__create_scheduled_task`）— cron 排产
3. **Institutional Agent 编排**（可选）— 多流水线组合

示例 cron 配置：
```
# 每日凌晨 3:17 运行缺陷发现（3RS/5G/5C，200图）
defect-discovery-daily: cron "17 3 * * *", preset "standard"

# 每周一凌晨 4:23 运行数值稳定性
numeric-stability-weekly: cron "23 4 * * 1", preset "full"

# 每次 push 后触发回归（通过 CI hook）
solver-regression: on-push, preset "quick"
```

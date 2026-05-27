# Session Benefit Audit System — 发展规划

> 日期: 2026-05-28 | 状态: 系统已进入运营阶段
>
> 基于当前系统能力（8 命令、百分位 BEI 引擎、HTML Dashboard、自动化管线）
> 的短-中-长期发展路线图。

---

## 当前能力基线

| 维度 | 状态 |
|------|------|
| 数据采集 | Stop hook → db import → git 富化 → BEI 评分，全自动 |
| 实时监控 | `watch` 命令，6 种告警规则 |
| 离线报告 | `report` / `trend` / `snap` / `dashboard`，多模型成本比较 |
| 基线校准 | `baseline calibrate`，P25/P50/P75，7d/30d 窗口 |
| BEI 评分 | 百分位归一化，五维度加权 |
| 可视化 | terminal table / markdown / HTML+Chart.js 自包含仪表板 |
| 多项目 | `--all-projects` 导入，dashboard 跨项目聚合 |

---

## 短期计划（1-4 周）

数据积累驱动的自然激活，不需要大量新代码。

### S1 — 激活 cost_per_commit 基线

**现状**: `baseline calibrate` 要求 ≥5 个有 commit 的 session 才产出基线，当前仅 GCS-A 且多数 session 无 commit 关联。

**方案**: 随着日常使用自然积累。或者放宽阈值到 n≥3 先产出方向性基线（标注 "low confidence"）。

**优先级**: 高 — 当前 BEI 效率维度回退到 config 硬编码值，降低了评分的区分度。

### S2 — 多项目数据导入

**现状**: `--all-projects` 已支持，但仅 GCS-A 有 13 个 session。s009、Nature 等项目的历史 JSONL 未导入。

**方案**: 一次性 `python -m tools.token_audit db import --all-projects`，dashboard 自动展示跨项目对比。

**优先级**: 中 — 功能已就绪，只需执行导入动作。

### S3 — BEI knowledge_score 阈值校准

**现状**: `_knowledge_score` 的 `max_memory_entries`（默认 3）和 `max_skill_invocations`（默认 5）仍用 config 硬编码。`calibrate_baselines` 未产出这两个维度的 P90。

**方案**: 在 `calibrate_baselines` 中增加 `memory_entries_p90` 和 `skill_invocations_p90`，BEI 引擎自动消费。

**优先级**: 中 — 改动小（~30 行），与 S1 一起做。

### S4 — snap 命令增强

**现状**: `snap` 查询最新 session，但缺少与历史趋势的对比。

**方案**: 增加 `snap --trend` 选项，显示"本 session vs 7 天均值"的简要对比行。如：
```
BEI: 0.49 C (7d avg: 0.52)  ↓6%
Cost: $0.10 (7d avg: $0.12) ↓17%
```

**优先级**: 低 — nice-to-have，提升日常使用体验。

---

## 中期计划（1-3 月）

需要适度设计和开发的功能。

### M1 — Web Dashboard v2（datasette + 预配置）

**现状**: HTML dashboard 是自包含单文件，适合一次性导出。日常浏览需每次生成。

**方案**: 
1. `db dashboard` 子命令启动 datasette，预装 `datasette-dashboard` 插件或自定义模板
2. 预配置常用查询（按日期筛选、BEI 排行、成本趋势）
3. 保持 HTML dashboard 作为导出格式，datasette 作为交互式浏览器

**优先级**: 高 — datasette 已安装，主要是配置工作。

### M2 — Session 对比功能

**现状**: `report` 每次只看一个 session，无法并排比较。

**方案**: `report --compare <session_id_2>` 产出双列对比表，聚焦差异（成本变化、BEI 变化、缓存变化）。

**优先级**: 中 — 在复盘"为什么这次 session 比上次贵"时很有用。

### M3 — 异常检测与智能告警

**现状**: 告警引擎有 6 种基于阈值的规则，但阈值是 config 硬编码。

**方案**: 
1. 告警阈值改用基线 P75/P25（如成本超过 P75 时告警）
2. 增加"模式异常"检测：session 前 25% 轮次消耗了 >50% 的 token
3. 增加"产出异常"检测：token 消耗正常但 LoC 显著低于 P25

**优先级**: 中 — 让告警从"静态规则"升级为"统计驱动"。

### M4 — 审计数据备份与迁移

**现状**: `audit.db` 在 `tools/token_audit/` 下，随 git 备份。但没有显式的导出/导入机制。

**方案**: 
1. `db export` / `db import` 命令支持跨机器迁移（JSON 格式）
2. `db backup` 自动定时备份到指定目录
3. 可选：audit.db 纳入 git-lfs 或独立存储

**优先级**: 低 — 当前单机使用场景不急迫。

---

## 长期计划（3-12 月）

需要显著设计投入或外部依赖的功能。当前阶段做"设计预留"而非立即实现。

### L1 — OpenTelemetry 集成 (T4.2)

**方案**: 导出 `gcs.token_audit.session.cost`、`gcs.token_audit.bei.composite` 等指标到 OTLP endpoint，对接 Prometheus + Grafana。

**触发条件**: 组织级 AI 成本治理需求出现（多人多项目使用 Claude Code）。

### L2 — 预测模型 (T4.3)

**方案**: 基于 session 前 5 轮特征（每轮 token 增幅、工具调用比例、缓存命中趋势）预测最终成本和 BEI。当预测值超过阈值时提前告警。

**触发条件**: session 量 > 100，有足够训练数据。当前 13 个 session 不足以训练有意义的模型。

### L3 — 团队级效率洞察 (T4.4)

**方案**: 多开发者对比（匿名化）、高效工作模式识别、项目级 ROI 趋势。

**触发条件**: 多开发者日常使用本系统。当前单人使用，dashboard 的跨项目聚合已满足需求。

### L4 — 组织级 AI 成本预算

**方案**: 月度/季度 AI 成本预算设定，实时消耗追踪，超预算告警。与 `config.yaml` 中的 `roi` 估算参数联动。

**触发条件**: 需要向上汇报 AI 成本 ROI 时。

---

## 优先级矩阵

```
                    高影响              低影响
                 ┌─────────────┬─────────────┐
短期(1-4w)       │ S1 cost基线  │ S4 snap增强  │
                 │ S3 knowledge │             │
                 │ S2 多项目    │             │
                 ├─────────────┼─────────────┤
中期(1-3m)       │ M1 datasette│ M4 备份迁移  │
                 │ M2 对比     │             │
                 │ M3 异常检测  │             │
                 ├─────────────┼─────────────┤
长期(3-12m)      │ L2 预测模型  │ L1 OTel      │
                 │ L3 团队洞察  │ L4 成本预算  │
                 └─────────────┴─────────────┘
```

## 建议的下一步行动

1. **本周**: 执行 S2（多项目导入），观察哪些项目有足够数据
2. **本月**: 完成 S1+S3（cost 基线 + knowledge 阈值），让 BEI 全维度使用动态基线
3. **下月**: 启动 M1（datasette Web UI），降低日常浏览数据门槛
4. **长期**: 等待数据积累和多人使用，触发 M3 → L2 → L3

---

> 设计原则: 不提前建造。每个阶段的功能由"当前数据能支撑什么"决定，
> 而非"最终想要什么"。短期项目优先解决"有功能但数据不足"的瓶颈。

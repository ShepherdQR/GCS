# GCS Pipeline Registry

生产流水线（Pipeline）是 GCS 项目中可复用的、参数化的多步骤自动化流程。
每条流水线有唯一的 ID、版本、责任人，以及明确的输入/输出契约。

## Active Pipelines

| ID | Name | Version | Owner | Status |
|----|------|---------|-------|--------|
| [`defect-discovery`](defect-discovery/README.md) | Defect Discovery Pipeline | v1 | gcs-cpp-solver-maintainer | active |

## Pipeline Lifecycle

```
proposed → draft → active → deprecated → retired
```

- **proposed**: 概念已提出，参数尚未标准化
- **draft**: skill.md 已编写，工具链就绪，未排产
- **active**: 已验证运行，已排产（cron 或 /loop）
- **deprecated**: 被新流水线替代，仍可手动运行
- **retired**: 已归档，不再支持

## Invocation Methods

每条流水线可通过以下方式调用：

| 方式 | 适用场景 |
|------|---------|
| CLI 脚本 | 开发调试、一次性运行 |
| Claude Code Skill | 交互式请求、按需触发 |
| Cron / Scheduled Task | 定期质量门禁（每日/每周） |
| /loop 自主循环 | 持续监控、分步执行 |
| Institutional Agent | 多流水线编排 |

## Adding a New Pipeline

1. 在 `docs/agentic/pipelines/<id>/` 下创建目录
2. 编写 `README.md`（目的、流程、调用方式、历史运行）
3. 编写 `parameters.md`（完整参数 schema + presets）
4. 编写 `skill.md`（skill 定义，含触发条件）
5. 在本文更新注册表
6. 实现工具链（如需要新 `tools/` 模块）
7. 运行一次端到端验证
8. 排产（cron 或 manual trigger）

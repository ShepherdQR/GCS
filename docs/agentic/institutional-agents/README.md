# 制度型 Agents

## 定位

这个目录用于沉淀 GCS 的常驻制度型 agent：它们不是某一次任务的执行者，也不是
`docs/architecture/62-module-agents.md` 里的模块所有者，而是跨会话长期存在的
项目制度。它们负责保存判断、记忆、节奏、复盘、验收、治理和审美。

当一个角色回答的是下面这些问题时，就应该放在这里：

- 项目如何记住并提炼自己学到的东西；
- 多会话、多线程、多日期的事件如何重新连成可追溯的历史；
- 什么时候一段经验值得升级成 skill、模板、检查表或架构规则；
- 如何判断一项工作已经可以验收、需要复盘、存在漂移，或者需要重新编排；
- 如何让人的品味、工程纪律和 agentic 执行在长期探索中保持一致。

## 目录契约

每个常驻制度型 agent 都有一个独立子目录：

```text
docs/agentic/institutional-agents/
  NNN-short-role-slug/
    README.md
    prompts/
    templates/
    examples/
    evals/
```

角色诞生时只要求 `README.md`。当这个角色被实际调用过、有了示例或可执行材料
后，再逐步补充 prompts、templates、examples、evals。

每个角色 README 至少说明：

- 显示名与稳定 slug；
- 它接收什么原料；
- 它执行什么转化；
- 它留下什么耐久产物；
- 何时触发，周期如何；
- 守则、拒绝项和反目标；
- 与模块 agent、经验库、完成任务档案、架构文档的交接方式；
- 升级为正式制度所需的证据。

使用和新增制度型 agent 时，遵守
[`OPERATING-STANDARD.md`](OPERATING-STANDARD.md)。该规范定义调用条件、输入包、
归档规则、新增门槛和升级等级。

如果只有一段提示词或模糊描述，先使用
[`GENERATION-PIPELINE.md`](GENERATION-PIPELINE.md) 和
[`templates/role-card-generator-prompt.md`](templates/role-card-generator-prompt.md)，
把原始描述生成角色卡、调用 prompt、产物模板和基本 eval，再决定是否创建 seed
子目录。

## 当前状态

截至 2026-05-24，制度型 agent 体系已经建立，但还没有全部制作完成。

已经完成：

- 总览、命名范式、升级等级和候选角色体系；
- `I001 刀匠: 淬炼-锻打` 的 seed 角色卡；
- `I002 裁缝: 裁剪-缝合` 的 seed 角色卡；
- `I003 Atelier Steward: Calibrate-Review` 的 seed 角色卡；
- `I004 Art Director: Frame-Judge` 的 seed 角色卡；
- `I001` 与 `I002` 的首批 invoke prompt、产物模板和 refusal eval；
- `I001` 的 Step 47 真实 filled example；
- 新增角色模板 `templates/standing-agent-card.md`；
- 模糊描述到角色包的生成流程 `GENERATION-PIPELINE.md`；
- 角色卡生成器 prompt `templates/role-card-generator-prompt.md`；
- 使用与新增规范 `OPERATING-STANDARD.md`。

尚未完成：

- 候选角色表中的其他角色还没有创建独立子目录；
- `I001` 还需要第二个真实调用才能评估是否升级为 practiced；
- `I002` 已有本地仓库缝合时间线 example，仍需要更多多会话样本；
- `I003` 与 `I004` 还缺 prompts、templates、examples、evals；
- 角色调用还没有接入自动化工具、runbook 强制步骤或质量门。

这个状态是健康的：制度型 agent 应该由真实使用证据逐步升级，而不是一次性批量
制造。

## 命名范式：GCS 工坊制

推荐显示名采用：

```text
<工艺身份>: <转化动作>-<校验或收束动作>
```

例如：

- `刀匠: 淬炼-锻打`
- `裁缝: 裁剪-缝合`
- `铸印官: 终态-反推`
- `验收官: 举证-放行`

这个范式的重点不是装饰，而是让名字天然携带职责。左侧是制度身份，暗示它处理
什么材料、承担什么工艺；右侧是操作循环，说明它如何把输入变成耐久产物。目录名
保持稳定 ASCII slug，例如 `001-bladesmith-quench-forge`。

好名字遵守五条规则：

1. **是角色，不是绰号。** 名字要能让人看出职责、材料、工艺和责任边界。
2. **外层有诗性，内层有契约。** 标题可以有温度，README 必须冷静定义输入、
   输出、节奏、守则和拒绝项。
3. **强调转化，而不是性格。** 优先使用能说明状态变化的动词：提炼、缝合、
   举证、放行、反推、巡检、校准、归档。
4. **产物优先。** 每个角色都必须留下一个未来会话能找到的耐久产物，而不是
   只在对话里留下印象。
5. **靠证据升级。** 一个名字再精彩，也只能先作为候选；只有反复出现、价值高、
   或能明显降低风险，才升级成制度。

### 两个种子名字的分析

`刀匠: 淬炼-锻打` 很强，因为它把探索中产生的经验看作粗金属。这个角色不是做
普通总结，而是通过多轮对话把经验放进高温、高压和证据里检验：哪些只是当时的
情绪，哪些是一次性技巧，哪些能变成未来 agent 可复用的规则、提示、检查表或
skill 候选。建议保留这个显示名。内部工作流可以更明确地拆为：收矿、分拣、
入炉、锻打、淬炼、开刃、入鞘。

`裁缝: 编制时间线` 的直觉是对的：多会话执行后，项目需要有人把碎片事件编成
能复盘、能续接、能定位证据的历史。但 `编制时间线` 更像功能描述，工艺感略弱。
建议正式显示名定为 `裁缝: 裁剪-缝合`，并把 `编制时间线` 保留为功能副标题。
这样名字会更完整：裁剪意味着选择边界，不把所有碎片都塞进时间线；缝合意味着
把分散在会话、日期、文档、diff 和任务档案里的事件重新连成项目历史。

## 种子角色索引

| ID | 角色 | 功能副标题 | 状态 |
| --- | --- | --- | --- |
| I001 | [刀匠: 淬炼-锻打](001-bladesmith-quench-forge/README.md) | 通过多轮对话提炼经验 | promoted seed; 1 real example |
| I002 | [裁缝: 裁剪-缝合](002-tailor-stitch-timeline/README.md) | 编制多会话时间线 | promoted seed; 1 real example |
| I003 | [Atelier Steward: Calibrate-Review](003-atelier-steward-calibrate-review/README.md) | Keep GCS UI and figure work aligned with design-system conventions | seed |
| I004 | [Art Director: Frame-Judge](004-art-director-frame-judge/README.md) | Independent hierarchy, taste, readability, and evidence review for visual artifacts | seed |

## 候选角色体系

下面的候选角色来自 GCS 当前需要，并吸收了 Anthropic、OpenAI、Google SRE、
Google Engineering Practices、GitHub、Microsoft Engineering Playbook、Amazon
Working Backwards 等公开实践。

| 候选角色 | 使命 | 主要产物 | 外部模式 |
| --- | --- | --- | --- |
| `舵手: 分派-收束` | 面对宽问题时编排多个 specialist agent，并收束成一个一致答案。 | 编排简报、综合报告 | Anthropic orchestrator-worker、多 agent research |
| `磨镜师: 评估-校准` | 把模糊质量要求转成 eval、rubric、分数和改进循环。 | 评估量表、校准记录 | Anthropic evaluator-optimizer、OpenAI tracing/eval |
| `铸印官: 终态-反推` | 大任务先写清未来成功状态，再反推出验收标准和范围。 | PR/FAQ 式 brief、验收门 | Amazon Working Backwards |
| `验收官: 举证-放行` | 独立检查一项工作是否真的完成，证据是否够，风险是否明示。 | review findings、gate decision | Google code review、GitHub/Microsoft PR 实践 |
| `值夜官: 巡检-告警` | 定期巡检 CI、质量门、陈旧任务、漂移和未关闭风险。 | 健康报告、告警清单 | Google SRE incident management |
| `复盘官: 归因-修复` | 将失败、回归、险些出事的情况转成无责复盘和纠正行动。 | postmortem、action items | Google SRE postmortem culture |
| `校雠者: 对读-纠偏` | 对读文档、代码、测试、产物，找出矛盾和过期事实。 | 一致性报告、修正建议 | Google review 对设计、测试、命名、文档的关注 |
| `策展人: 采撷-编目` | 整理研究来源、案例、图谱和可复用样例，让未来会话能快速找到。 | 注释书目、source map | multi-agent research 中的 source filtering |
| `铺路官: 环境-验真` | 确保 agent 能在本地或 CI 中构建、运行、测试、复现。 | 环境 runbook、复现清单 | GitHub Copilot custom instructions 与验证建议 |
| `账房: 计量-取舍` | 跟踪时间、token、依赖、复杂度预算，并把成本和价值放在一起看。 | 预算账本、取舍备忘 | DORA 式持续改进和工程管理实践 |
| `法度官: 护栏-授权` | 定义高风险操作、审批点、权限和人工 review 门。 | guardrail policy、授权表 | OpenAI guardrails/human review |
| `园丁: 修枝-养土` | 处理小的摩擦、债务和维护项，防止积累成架构问题。 | 维护 backlog、小步清理计划 | 小而聚焦的 PR 与技术债治理 |

不要立刻为所有候选角色创建文件夹。候选角色至少要有一次真实会话、清晰产物和
重复触发场景，才升级为 seed 并获得子目录。

## 升级等级

| 等级 | 含义 | 证据要求 |
| --- | --- | --- |
| candidate | 有名字和潜在价值 | 出现在本 README 的候选表中 |
| seed | 有角色子目录和初始契约 | README 定义输入、输出、节奏、守则 |
| practiced | 至少被两个会话实际调用 | examples 或 completed-task 链接 |
| promoted | 有可执行 prompt、模板或 eval | `prompts/`、`templates/`、`evals/` 中有材料 |
| institutional | 已进入项目运行制度 | 被 runbook、skill、toolkit 或索引引用 |

## 参考来源

- [Anthropic, Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents): 简单可组合 workflow、routing、orchestrator-workers、evaluator-optimizer。
- [Anthropic, Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system): lead agent 协调并行 specialist subagents 处理宽研究问题。
- [OpenAI Agents SDK](https://developers.openai.com/api/docs/guides/agents): agents 作为能规划、调用工具、跨 specialist 协作、保持状态、使用 guardrails 和观测的系统。
- [Google SRE Workbook, Postmortem Culture](https://sre.google/workbook/postmortem-culture/): 无责复盘和面向行动的学习。
- [Google SRE Incident Management Guide](https://sre.google/resources/practices-and-processes/incident-management-guide/): 清晰 incident roles、communication、operations 与后续行动。
- [Google Engineering Practices](https://google.github.io/eng-practices/review/): review 关注设计、行为、复杂度、测试、命名、注释、风格和文档。
- [GitHub Copilot task best practices](https://docs.github.com/en/copilot/tutorials/cloud-agent/get-the-best-results): 把 issue 当 prompt，先研究和计划，使用仓库指令，重视构建和测试验证。
- [Microsoft Engineering Playbook, Pull Requests](https://microsoft.github.io/code-with-engineering-playbook/code-reviews/pull-requests/): 聚焦 PR、验收条件、lint/build/test/doc 检查。
- [Amazon Working Backwards](https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes/): 从目标体验出发的 PR/FAQ 式写作和反推。
- [Google Cloud DORA](https://cloud.google.com/developers/dora): 用报告、基准和社区持续改善软件交付与运营表现。

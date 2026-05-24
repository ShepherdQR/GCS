# AI Agent Git Worktree Workflow For GCS

Research snapshot: 2026-05-24.

本文研究的问题是：在一台电脑上，一个 GCS Git 仓库被多个 Codex 会话同时使用时，为什么会出现“会话 A 创建或切换子分支后，其他会话也立即进入同一分支”的现象，以及顶级 AI 编程工具和当前软件工程研究给出的最佳实践是什么。

结论先行：不要试图让一个工作目录里的 Git 分支变成“会话私有状态”。Git 的分支签出是工作树状态，不是聊天会话状态。多会话并发的正确边界是“每个会话一个独立 worktree 或独立 clone”，再用 branch、commit、PR 作为治理边界。对 GCS 来说，当前本地 checkout 应定位为 foreground / integration workspace；任何会写文件的并发 Codex 会话，都应进入自己的 worktree。

## 资料来源

- [OpenAI Codex app Worktrees](https://developers.openai.com/codex/app/worktrees)
- [OpenAI Codex Workflows](https://developers.openai.com/codex/workflows)
- [OpenAI Introducing Codex](https://openai.com/index/introducing-codex/)
- [Git worktree documentation](https://git-scm.com/docs/git-worktree)
- [Git branching and merging](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)
- [Git reset demystified: HEAD, index, working directory](https://git-scm.com/book/en/v2/Git-Tools-Reset-Demystified)
- [Claude Code worktrees](https://code.claude.com/docs/en/worktrees)
- [Claude Code best practices](https://code.claude.com/docs/en/best-practices)
- [GitHub Copilot coding agent docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/assign-copilot-to-an-issue)
- [Cursor Background Agents](https://docs.cursor.com/en/background-agents)
- [Google Gemini Code Assist agent mode](https://developers.google.com/gemini-code-assist/docs/agent-mode)
- [Devin environment configuration](https://docs.devin.ai/onboard-devin/environment)
- [Devin Review CLI](https://docs.devin.ai/work-with-devin)
- [Why Are Agentic Pull Requests Merged or Rejected?](https://arxiv.org/abs/2605.22534)
- [Where Do AI Coding Agents Fail?](https://arxiv.org/abs/2601.15195)
- [Collaborator or Assistant? AI Coding Agents Across PR Lifecycles](https://openreview.net/forum?id=PXSlMpbbsn)

## 核心诊断

当前问题不是 Codex 会话管理的小 bug，而是 Git 抽象层被误用。

在一个普通 checkout 中，`HEAD`、index、working directory 是这一个目录的状态。Git Book 把 working directory 称为可编辑的 sandbox，`HEAD` 是当前分支引用指向的最后提交，index 是下一次提交的候选快照。多个 Codex 会话如果都把 `C:\Codes\Trae\s002_GCS\GCS` 当成自己的工作区，那么它们看到和修改的是同一组文件、同一个 index、同一个当前 branch checkout。会话 A 运行 `git switch` 或 `git checkout -b` 时，A 并没有只改变“自己的聊天上下文”，而是改变了这个目录的 Git 工作树状态。因此会话 B 下一次读文件或查状态时自然也在同一 branch 上。

这也是为什么“子分支”这个词需要澄清。Git 里没有真正的子分支对象；`codex/foo/bar` 只是一个带斜杠的分支名。所谓“子分支”通常有两种含义：

- topic branch：从某个 base 分支切出来的独立工作线。
- stacked branch：一个 branch 依赖另一个尚未合并的 branch，PR base 不是主干而是父分支。

如果没有显式记录父分支、验证顺序和合并顺序，“子分支”会给人一种层级隔离的错觉，实际只是全局 ref 名字。分支名能表达意图，不能提供并发隔离。

## 顶级工具的公开共识

### OpenAI Codex

OpenAI Codex 的公开资料把隔离作为并行代理工作的默认前提。Codex cloud 的任务是在独立环境中处理；OpenAI 介绍 Codex 时强调每个任务独立运行在隔离环境中，完成后可提交、审查、开 PR。Codex app 的 Worktrees 文档更加直接：worktree 让 Codex 在同一项目里运行多个独立任务而不互相干扰；自动化任务在专用 background worktree 中运行；Local 可以理解为 foreground，Worktree 可以理解为 background。

这给 GCS 的启发很明确：Local 不是并发编辑区，而是人类检查、集成、运行常用 IDE 或唯一 dev server 的前台区。后台代理、并发实验、长任务必须进入 worktree。

OpenAI 文档还指出一个关键 Git 事实：同一个 branch 不能同时被签出到多个 worktree。若一个 worktree 已签出某分支，另一个 worktree包括 Local 不能同时签出它。这个约束不是麻烦，而是保护机制。不要用 `--force` 绕过它。

### Anthropic Claude Code

Claude Code 的公开最佳实践几乎把答案写成命令：并行 session 应使用 git worktree，因为每个 worktree 有自己的文件和 branch，共享历史和 remote；`claude --worktree feature-auth` 会创建隔离工作区。Claude 文档还提出细节：默认从 `origin/HEAD` 或本地 `HEAD` 建立 base，必要时复制 gitignored 的 `.env` 一类文件，结束后清理空 worktree。

更深一层的原则是：worktree 隔离文件写入，session/subagent 隔离上下文，review session 隔离判断偏见。Claude 的最佳实践建议 Writer/Reviewer 两个会话分离，Reviewer 在新上下文中审查 Writer 的改动。这与 GCS 的高风险 solver / IO / diagnostics 工作非常匹配。

### GitHub Copilot Coding Agent

GitHub Copilot coding agent 走的是 PR 原生路线：给 issue 或 prompt 分配 agent，选择目标 repo 和 base branch，agent 在自己的开发环境里工作并创建 PR 或 branch。GitHub 文档强调，Copilot 会在任务完成后请求人类 review。换言之，GitHub 把 agent 输出的治理单位放在 PR，而不是本地聊天会话。

对 GCS 的启发是：branch 不是“我正在聊天”的状态，而是“我准备让别人 review 的变更容器”。每个并发工作线都应该最终变成可 diff、可 test、可 review 的 branch/PR。

### Cursor Background Agents

Cursor background agents 的公开文档显示，它们会 clone GitHub repo，在隔离的 Ubuntu 机器中工作，并使用 separate branch push 回 repo。这和 OpenAI/Claude 的本地 worktree 方案在本质上相同：文件系统隔离 + branch 输出 + 人类接管/PR。

Cursor 的经验尤其适合解释为什么“同目录多窗口”危险。AI agent 是会真实写盘的编辑者；如果两个窗口指向同一个目录，就会发生写入竞争、上下文错觉和覆盖。

### Devin

Devin 的环境配置文档把每个 session 看成一台预配置开发机快照；Devin Review CLI 也会为 PR branch 创建 isolated worktree checkout，以免影响当前 working directory。这说明即使在“全自治软件工程师”路线中，隔离 checkout 仍是基础设施，而不是可选美化。

### Google Gemini Code Assist

Gemini Code Assist agent mode 的文档强调 agent 会使用 IDE、文件、终端、Git 等工具，并在变更文件系统或执行 mutating 操作时请求许可。它没有像 Claude/OpenAI 那样把 worktree 作为同页核心方案，但它强化了另一个原则：agent 的工具权限必须与工作区边界绑定。对 GCS 来说，这意味着不能只靠“请不要碰别的分支”这种软提示；应把 session 的可写目录物理隔离。

## 前沿研究给出的治理模型

2026 年的软件工程研究已经开始从“AI 写代码能力”转向“AI PR 生命周期治理”。这比单纯 benchmark 更贴近 GCS 的真实问题。

OpenReview 论文把 agent workflow 分成 operational agency 和 merge governance：agent 可以发起和推进工作，但最终 merge 权威仍应主要保留在人类手里。这个分离很关键。GCS 不应该追求“多个 agent 都在同一目录自由推进，最后凭感觉合并”；而应追求“多个 agent 在隔离 worktree 中推进，最后由人类或主会话在 integration workspace 中做审查、测试和合并”。

MSR 2026 的 Agentic PR 研究指出，PR 是否 merge 不能单独代表 agent 能力，因为 review 互动、workflow 约束、缺乏可观察决策理由都会影响结果。对 GCS 这意味着：报告、任务卡、验证命令、review 记录比“最后有没有合进去”更重要。尤其是 solver 或诊断语义变更，如果没有 residual/rank/fixture 证据，即使能合并，也不等于可信。

另一篇 MSR 2026 失败 PR 研究发现，未合并 agent PR 常见于更大的改动、触及更多文件、CI 不通过、缺少有意义 reviewer 互动、重复 PR、需求错配等。GCS 的架构已经有多模块、数值语义和 UI/IO 层交织，如果多个会话共享同一 checkout，这些失败模式会被放大：agent 可能在错误 base 上改大范围文件，另一个会话又在同一目录继续读旧上下文，最后形成不可审查的混合 diff。

因此最前沿的理论可以概括为四层边界：

1. 文件系统边界：worktree / clone 隔离真实写盘。
2. 语义任务边界：task card / issue / prompt 定义 done。
3. 版本治理边界：branch / commit / PR 承载 diff 和 review。
4. 决策权边界：human or steward 保留 merge approval，agent 提供证据。

## 推荐给 GCS 的工作区模型

### 角色划分

`C:\Codes\Trae\s002_GCS\GCS` 应定义为 Local foreground / integration workspace：

- 用于阅读、最终审查、手动运行熟悉的 GUI 或唯一端口服务。
- 只允许一个写入型 Codex 会话拥有它。
- 当前有未提交改动时，禁止在这里随手切分支。
- 不作为并发后台任务的默认工作目录。

每个并发 Codex 会话应使用自己的 Worktree workspace：

- 一个任务一个 worktree。
- 一个 worktree 一个 branch 或 detached HEAD。
- worktree 名、branch 名、task card 名互相可追踪。
- 完成后通过 commit + diff + tests 回到 Local 或 PR 审查。

### 推荐目录

优先使用 Codex app 内置 Worktree 功能，让 Codex 管理路径、handoff 和安全 Git 操作。

如果必须手动创建，路径有两种可选策略：

1. 工具允许写 sibling 目录时，推荐：

```powershell
C:\Codes\Trae\s002_GCS\GCS.worktrees\<date>-<slug>
```

2. 当前 Codex 沙箱只允许写 repo 内部时，推荐：

```powershell
C:\Codes\Trae\s002_GCS\GCS\.codex\worktrees\<date>-<slug>
```

第二种需要把 `.codex/worktrees/` 加入 ignore 规则，否则主 checkout 会看到嵌套 worktree 目录。GCS 当前 `.codex/skills` 是被跟踪的项目配置，因此不能粗暴 ignore 整个 `.codex/`。

### Branch 命名

建议统一：

```text
codex/YYYYMMDD-<scope>-<slug>
codex/YYYYMMDD-docs-git-worktree-policy
codex/YYYYMMDD-io-json-roundtrip
codex/YYYYMMDD-solver-rank-evidence
```

如果确实是 stacked branch，命名体现父任务：

```text
codex/YYYYMMDD-rank-evidence-base
codex/YYYYMMDD-rank-evidence-gui-on-base
```

并在 task card 或 PR 描述中显式写：

```text
Base branch: codex/YYYYMMDD-rank-evidence-base
Merge order: base first, gui-on-base second
```

不要依赖斜杠层级表达父子关系。`codex/a/b` 只是名字，不会让 Git 知道 `codex/a` 是父分支。

## 操作规程

### 新开 Codex 会话

1. 判断是否会写文件。
2. 只读研究或代码解释可以共享 Local。
3. 任何会编辑文件、运行生成器、改 build 输出、改 fixture 的任务，都进入 Worktree。
4. 选择 base branch 时必须显式说明：
   - 从稳定集成分支开始，适合独立任务。
   - 从当前 feature branch 开始，适合 stacked 后续任务。
   - 当前 Local 有未提交改动时，不得默认继承，除非任务明确需要这些改动。

### 手动 worktree 命令模板

独立任务从远端 base 开始：

```powershell
$root = "C:\Codes\Trae\s002_GCS\GCS"
$name = "20260524-docs-git-worktree-policy"
$path = "$root\.codex\worktrees\$name"
$branch = "codex/$name"

git -C $root fetch origin
git -C $root worktree add -b $branch $path origin/<base-branch>
```

基于当前已提交 feature branch 做 stacked work：

```powershell
$root = "C:\Codes\Trae\s002_GCS\GCS"
$name = "20260524-gui-on-rank-evidence"
$path = "$root\.codex\worktrees\$name"
$branch = "codex/$name"

git -C $root worktree add -b $branch $path codex/20260524-rank-evidence-base
```

查看和清理：

```powershell
git worktree list
git -C <worktree-path> status --short --branch
git worktree remove <worktree-path>
git worktree prune
```

不要用：

```powershell
git worktree add --force ...
```

除非你非常确定要覆盖 Git 的 branch checkout 保护。对多 agent 工作流来说，这通常是错误信号。

### 提交和合并

每个 worktree 完成后：

1. 在该 worktree 内运行最小相关验证。
2. 确认 `git status --short --branch` 只包含该任务范围内的改动。
3. commit 到该 worktree branch。
4. 回到 Local 或 PR 做 review。
5. 合并前重新跑与风险匹配的 GCS quality gate。
6. 合并后删除 worktree 和临时 branch，除非它是仍在审查的 stacked base。

GCS 高风险任务，例如 solver contract、IO schema migration、diagnostic status precedence、runtime transaction semantics，应使用 Writer/Reviewer 双会话：Writer 在 worktree 写，Reviewer 在独立新会话或 Local 只读审查 diff。Reviewer 不应共享 Writer 的长上下文。

## 决策矩阵

| 场景 | 推荐方式 | 原因 |
|---|---|---|
| 只读解释代码、写研究报告 | Local 可接受 | 不切分支，不写共享代码 |
| 单一小修且无其他会话活跃 | Local 可接受 | 操作成本低 |
| 两个以上 Codex 会话会写文件 | 每会话一个 worktree | 文件写入隔离 |
| 长任务、自动化、后台检查 | 专用 worktree | 防止污染 foreground |
| GUI 或端口资源只能跑一份 | worktree 写，handoff 到 Local 验证 | 文件隔离与本地环境兼容 |
| 依赖上一任务未合并结果 | stacked branch + 显式 parent | 保留因果关系 |
| 高风险跨模块变更 | task card + worktree + reviewer session | 保留证据链和治理边界 |
| 工具不支持 worktree | 独立 clone | 成本更高，但隔离清楚 |

## GCS 的具体风险点

GCS 不是普通 CRUD 项目。它有 C++ solver modules、Python GUI、scene fixtures、contract tests、architecture docs、generated visual assets 和 agentic tooling。共享 checkout 的风险包括：

- CMake `out/`、Python cache、generated fixture store 被多个会话交叉更新。
- 一个会话切 branch 后，另一个会话的路径、上下文和 diff 判断全部失真。
- GUI 或 scene generation 的中间产物被混入无关任务。
- architecture docs 和 implementation branch 的语义 base 不一致。
- 高风险 solver 变更没有独立 review diff，而是混在一个巨大 dirty tree。

因此 GCS 应把 worktree 视为“代理运行时隔离层”，不是临时技巧。

## 建议落地政策

短期立刻执行：

1. 当前 Local checkout 只作为单会话 foreground。
2. 新的写入型 Codex thread 默认选择 Codex app Worktree。
3. 所有手动 `git switch`、`git checkout -b` 前先说明是否会影响共享 Local。
4. 任何会话发现自己不在预期 branch，先停止写入，运行 `git status --short --branch`，再决定 handoff 或新建 worktree。

中期应写入项目规范：

1. 在 `docs/agentic/lifecycle-runbook.md` 增加 Git worktree 章节。
2. 在 `.gitignore` 精确加入 `.codex/worktrees/` 或另设本地 `.git/info/exclude`。
3. 为 `tools/agentic_design/agentic_toolkit.py` 增加 `new-worktree-task` 命令，自动生成 task card、branch 名、worktree 路径。
4. 对 high-risk scope 要求 Writer/Reviewer 分离。

长期演进：

1. 建立 GCS integration branch 作为 agent base，而不是所有任务都从当前脏 Local 派生。
2. 建立 task graph：独立任务平行，依赖任务 stack，所有 stack 有 merge order。
3. 将 CI / contract gates 绑定到 PR，而不是依赖某个会话口头报告。
4. 记录 agent-authored PR 的 review interaction，不只记录 merge outcome。

## 一句话原则

对 AI 编程代理来说，branch 是版本治理边界，worktree 是并发写入边界，PR 是人类决策边界，session context 是认知边界。把这四者混成一个共享目录，问题必然出现；把它们拆开，GCS 才能安全地让多个 Codex 会话并行工作。

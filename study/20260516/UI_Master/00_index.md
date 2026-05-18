# UI架构师研究 — 索引文件

## 研究日期
2026-05-16

## 研究目标
生成UI架构师Skill体系，紧密结合GCS约束图求解器项目

---

## 第一阶段：优秀案例/最佳实践研究（6份）

| 编号 | 文件 | 来源/主题 | 核心洞察 |
|------|------|-----------|----------|
| 01 | 01_research_anthropic_frontend_design.md | Anthropic Frontend Design Skill | 设计决策前置、Anti-Pattern禁令、调性选择框架 |
| 02 | 02_research_ui_ux_pro_max.md | UI-UX Pro Max Skill | 57种UI风格+96种行业配色+BM25推理匹配+反模式过滤 |
| 03 | 03_research_vercel_design_guidelines.md | Vercel Web Design Guidelines | 100+条规则、四维审查(布局/可访问性/UX/性能)、状态完整性 |
| 04 | 04_research_claude_design_system.md | Claude Design Design-System-as-a-Skill | 双文件架构(README+SKILL)、语义契约、Non-Negotiables |
| 05 | 05_research_frontend_architect_competency.md | 前端架构师核心能力体系 | 四层能力(实现/架构/连接/规划)、六大核心能力、AI时代路径 |
| 06 | 06_research_skill_composition_patterns.md | Skill组合模式与设计工作流 | 四分类(生成/规范/还原/系统)、角色匹配、评估驱动 |

---

## 第二阶段：3个顶级UI架构师

| 编号 | 文件 | 架构师定位 | 核心能力 |
|------|------|-----------|----------|
| Alpha | UI_Architect_Alpha.md | 设计系统大师 | 设计决策前置、语义契约、调性框架、Anti-Pattern、双模式工作 |
| Beta | UI_Architect_Beta.md | 交互体验大师 | 交互完整性、反馈即时性、99条UX规则、可访问性、行业推理 |
| Gamma | UI_Architect_Gamma.md | 工程效能大师 | 可演进性、模块治理、量化决策、组件库架构、技术债治理 |

### 三位架构师的协同关系

```
UI_Architect_Alpha (设计系统)
    ↓ 定义视觉语言和设计规范
UI_Architect_Beta (交互体验)
    ↓ 定义交互流程和状态管理
UI_Architect_Gamma (工程效能)
    ↓ 确保可扩展、可维护、高性能
```

---

## 第三阶段：5个GCS专属UI架构师

| 编号 | 文件 | 架构师定位 | 紧密结合的GCS模块 |
|------|------|-----------|-------------------|
| 1号 | GCS_UI_Architect_1.md | 约束图可视化架构师 | Core数据模型、DCM分解、三种图投影 |
| 2号 | GCS_UI_Architect_2.md | 求解管线仪表板架构师 | App门面层、LGS状态分析、CDS求解报告 |
| 3号 | GCS_UI_Architect_3.md | 3D交互场景架构师 | Three.js可视化、几何参数体系、刚体变换 |
| 4号 | GCS_UI_Architect_4.md | 图生成与验证架构师 | tools.py工具链、图存储体系、验证规则 |
| 5号 | GCS_UI_Architect_5.md | GCS全栈平台架构师 | 双轨技术栈、App三种输入模式、跨层集成 |

### 五位架构师与GCS管线的映射

```
GCS Pipeline:  IO → Core → DCM → LGS → CDS → App
                    │      │      │      │     │
Architect 1:        │      ●──────│──────│     │  (图可视化)
Architect 2:        │      │      │      ●─────●  (管线仪表板)
Architect 3:        ●──────│──────│──────●     │  (3D场景)
Architect 4:   ●────│──────│──────│──────│     │  (图工程工具)
Architect 5:   ●────●──────●──────●──────●─────●  (全栈平台)
```

---

## 关键方法论总结

### 1. 设计决策前置
在写代码前先明确目的、调性、约束、差异化（来自Anthropic frontend-design）

### 2. Anti-Pattern机制
明确禁止什么比告诉该做什么更有效（来自UI-UX Pro Max + frontend-design）

### 3. 语义契约优先
设计系统是人机共读的契约，不是文档（来自Claude Design）

### 4. 四层能力结构
实现→架构→连接→规划，每层回答一个本质问题（来自前端架构师能力体系）

### 5. 四分类模型
生成→规范→还原→系统，覆盖设计全生命周期（来自Skill组合模式）

### 6. GCS领域深度绑定
每个架构师必须深入理解GCS的数据模型、管线架构和工具链

---

## 第四阶段：5个GCS专属UI架构师 V2（理论升级版）

V2核心升级：**顶级理论视角 + 移除Three.js依赖 + 深度数学基础**

| 编号 | 文件 | 架构师定位 | 理论基础 | 渲染技术 |
|------|------|-----------|----------|----------|
| 1号V2 | GCS_UI_Architect_1_v2.md | 约束图可视化架构师 | **代数图论 + 结构刚性理论**：Laman定理、Hendrickson条件、刚性矩阵、拉普拉斯谱 | D3.js + SVG/Canvas2D |
| 2号V2 | GCS_UI_Architect_2_v2.md | 求解管线仪表板架构师 | **数值分析 + 约束传播理论**：Newton-Raphson收敛、Jacobian条件数、弧一致性(AC-3) | D3.js + Canvas2D |
| 3号V2 | GCS_UI_Architect_3_v2.md | 几何空间可视化架构师 | **画法几何 + 计算几何**：Monge投影法、正交三视图、投影保持性定理 | SVG + Canvas2D |
| 4号V2 | GCS_UI_Architect_4_v2.md | 图工程架构师 | **随机图论 + 形式化验证**：Henneberg构造、配置模型、CSP修复 | D3.js + SVG |
| 5号V2 | GCS_UI_Architect_5_v2.md | GCS系统架构师 | **代数规范 + 信息代数**：CQRS+Event Sourcing、范畴论Functor、因果一致性 | D3.js + SVG/Canvas2D |

### V1→V2 升级对比

| 维度 | V1 | V2 |
|------|----|----|
| 理论深度 | 经验性规则 | 数学理论基础（图论/数值分析/画法几何/形式化方法/代数规范） |
| 3D可视化 | Three.js | 画法几何三视图(Monge投影) + D3.js图可视化 |
| DOF分析 | 简单加减 | 刚性矩阵秩的代数解释 |
| 求解监控 | 残差曲线 | 残差+条件数+收敛速率+约束传播联合分析 |
| 图生成 | 随机生成 | Henneberg构造（保证刚性）+ 配置模型（控制度序列） |
| 图验证 | pass/fail | 形式化验证+证明证书+反例 |
| 图修复 | 贪心建议 | CSP求解（最小修改集） |
| 跨层集成 | REST/WebSocket | CQRS+Event Sourcing+因果一致性 |
| 接口定义 | 文档描述 | 代数规范（签名+公理） |
| 状态管理 | 简单状态 | Event Sourcing（可重放、可时间旅行） |

### 五位V2架构师与GCS管线的映射

```
GCS Pipeline:  IO → Core → DCM → LGS → [Prop] → CDS → App
                    │      │      │      │       │      │
1号V2(图可视化):    │      ●──────│──────│───────│      │  代数图论+刚性分析
2号V2(管线仪表):    │      │      │      ●───────●──────●  数值分析+约束传播
3号V2(几何空间):    ●──────│──────│──────│───────●      │  画法几何+计算几何
4号V2(图工程): ●────│──────│──────│──────│───────│      │  随机图论+形式化验证
5号V2(系统):   ●────●──────●──────●──────●───────●──────●  代数规范+信息代数
```

### V2关键方法论总结

1. **刚性理论**：约束图不是普通图，是刚性框架——Laman/Hendrickson条件是刚性判定的数学基础
2. **数值稳定性**：Jacobian条件数是求解稳定性的核心指标，约束传播可提前检测不一致
3. **画法几何**：3D几何问题通过Monge投影转化为2D问题，投影保持性定理保证信息不丢失
4. **构造性证明**：Henneberg构造不仅是生成方法，更是刚性图的构造性存在性证明
5. **代数规范**：接口不仅是文档，是签名+公理的代数结构，可形式化验证
6. **Event Sourcing**：状态不是存储的，而是从事件流投影的——可重放、可审计、可时间旅行

---

## 第五阶段：调度协议（Orchestrator）

**文件**：[GCS_UI_Architect_Orchestrator.md](GCS_UI_Architect_Orchestrator.md)

### 三层调度架构

```
层1: 5号作为调度中枢（Orchestrator）——唯一有权调度其他架构师
层2: 1-4号作为领域专家（Domain Experts）——独立专业视角
层3: 共享数据契约（Shared Data Contract）——架构师间通信的唯一通道
```

### 四种调度模式

| 模式 | 适用场景 | 示例 |
|------|----------|------|
| 独立模式 | 单一领域需求 | "看约束图结构" → 1号 |
| 顺序模式 | 前序输出是后序输入 | "生成并验证图" → 4号→1号 |
| 并行→汇聚 | 多维度分析 | "诊断求解失败" → 1+2+3号并行→5号汇聚 |
| 分层组合 | 完整平台构建 | "构建GCS平台" → 5号规划→4+1+2+3号分层 |

### 核心调度规则

1. **5号是唯一调度中枢**：1-4号不直接互相调用
2. **互补优于统一**：不同视角是互补的，不强制统一
3. **冲突消解**：LGS(1号vs2号vs5号)、CDS(2号vs3号)、修复(1号vs4号)
4. **理论优先级**：代数规范 > 图论 > 数值经验
5. **标注差异**：差异本身是有价值的信息

---

## 第六阶段：5个GCS专属UI架构师 V3（Python本地化升级版）

V3核心升级：**从Web技术栈迁移到Python本地可视化栈 + 恢复3D可视化能力**

| 编号 | 文件 | 架构师定位 | Python技术栈 | 关键升级 |
|------|------|-----------|-------------|----------|
| 1号V3 | GCS_UI_Architect_1_v3.md | 约束图可视化架构师 | networkx+matplotlib+scipy | networkx图布局替代D3.js，scipy谱分析 |
| 2号V3 | GCS_UI_Architect_2_v3.md | 求解管线仪表板架构师 | matplotlib+rich+scipy | rich终端仪表板+matplotlib收敛动画双通道 |
| 3号V3 | GCS_UI_Architect_3_v3.md | 几何空间可视化架构师 | matplotlib+mplot3d+numpy | **恢复3D可视化**(mplot3d)+画法几何三视图 |
| 4号V3 | GCS_UI_Architect_4_v3.md | 图工程架构师 | networkx+matplotlib+rich | Henneberg构造可视化+rich终端交互 |
| 5号V3 | GCS_UI_Architect_5_v3.md | GCS系统架构师 | textual+rich+matplotlib | **textual TUI框架**替代Web SPA |

### V2→V3 升级对比

| 维度 | V2 | V3 |
|------|----|----|
| 渲染技术 | D3.js+SVG+Canvas2D(Web) | matplotlib+networkx+rich(Python本地) |
| 3D可视化 | 无(放弃了Three.js) | **恢复**：matplotlib mplot3d(GCS项目已有viewer.py) |
| 仪表板 | Web SPA | rich终端+matplotlib窗口双通道 |
| 平台框架 | React/Vue SPA | textual TUI框架 |
| 状态管理 | Pinia/Vuex | textual reactive + Event Store |
| 与C++集成 | HTTP/WebSocket | subprocess/ctypes直接调用 |
| 部署 | 需要浏览器 | 终端直接运行 |
| 与GCS Python工具链 | 需要server.py中转 | 直接import调用 |
| 数据流 | C++→文件→Python→HTTP→浏览器→JS | C++→文件→Python→直接渲染 |

### V3关键方法论升级

1. **零Web依赖**：不需要浏览器、HTTP服务器、Node.js——Python直接渲染
2. **3D能力恢复**：mplot3d已在viewer.py中使用，V3同时提供3D+三视图
3. **双通道输出**：终端(rich)处理文本信息+matplotlib处理图表，各司其职
4. **textual TUI**：完整的终端交互应用，替代Web SPA
5. **直接集成**：import parser.py/viewer.py/tools.py，无需HTTP中转
6. **Event Store简化**：JSON文件持久化，零外部依赖

---

## 第七阶段：Skill最佳实践研究与V4规范化重构

### 研究产出

**文件**：[skill最佳实践.md](skill最佳实践.md)

核心发现：
1. SKILL.md标准格式：YAML frontmatter(name+description) + Markdown正文
2. name用kebab-case，description≤200字符，四段式(定位+能力+绑定+触发条件)
3. 正文严格遵循：身份定义→核心原则→领域知识→架构设计→Anti-Patterns→工作模式→执行步骤→默认行为
4. 禁令优于指令、询问优于假设、理由注释、Non-Negotiables

### V4文件（严格skill形式，kebab-case命名）

| 编号 | 文件 | name | 定位 | Python技术栈 |
|------|------|------|------|-------------|
| 1号V4 | GCS-UI-Architect-1-v4.md | gcs-graph-visualizer | 约束图可视化架构师 | networkx+matplotlib+scipy |
| 2号V4 | GCS-UI-Architect-2-v4.md | gcs-pipeline-dashboard | 求解管线仪表板架构师 | matplotlib+rich+scipy |
| 3号V4 | GCS-UI-Architect-3-v4.md | gcs-geometry-visualizer | 几何空间可视化架构师 | matplotlib+mplot3d+numpy |
| 4号V4 | GCS-UI-Architect-4-v4.md | gcs-graph-engineer | 图工程架构师 | networkx+matplotlib+rich |
| 5号V4 | GCS-UI-Architect-5-v4.md | gcs-system-architect | GCS系统架构师 | textual+rich+matplotlib |

### V3→V4 升级对比

| 维度 | V3 | V4 |
|------|----|----|
| 文件命名 | GCS_UI_Architect_1_v3.md | GCS-UI-Architect-1-v4.md |
| name字段 | GCS_UI_Architect_1_v3 | gcs-graph-visualizer |
| description | 多行长文本(>200字符) | ≤200字符，四段式精炼 |
| 正文结构 | 自由结构 | 严格8节段：身份定义→核心原则→领域知识→架构设计→Anti-Patterns→工作模式→执行步骤→默认行为 |
| 理论基础 | 独立大段(与正文分离) | 融入"核心原则"和"领域知识" |
| 代码示例 | 完整类实现 | 仅接口签名+核心要点 |
| 默认行为 | 部分有部分无 | 全部有，"不假设，先询问" |

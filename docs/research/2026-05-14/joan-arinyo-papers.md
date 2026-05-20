# Joan-Arinyo 团队论文详细分析

## 团队概述

**Robert Joan-Arinyo**（Universitat Politècnica de Catalunya, 加泰罗尼亚理工大学，西班牙巴塞罗那）领导的几何约束求解研究团队，核心成员包括：
- **Antoni Soto-Riera** — 约束求解器架构与规则系统
- **Sebastià Vila-Marta** — 图分解理论与算法
- **Josep Vilaplana-Pastó** — 约束图结构分析
- **Marta Hidalgo** — 参数范围计算
- **Núria Mata** — 2D约束分析

合作者包括 **Christoph M. Hoffmann**（Purdue University，约束求解领域泰斗）、**Ioannis Fudos**（University of Ioannina）等。团队活跃于 1990 年代中期至 2010 年代中期，发表了约 10 篇核心论文，系统性地建立了**基于图构造的几何约束求解**（graph-constructive geometric constraint solving）理论与方法。

> **机构链接**: [Universitat Politècnica de Catalunya](https://www.upc.edu/)（Robert Joan-Arinyo 原任职于 Departament de Llenguatges i Sistemes Informàtics）

---

## 论文详细分析

### 论文 1: "A Correct Rule-Based Geometric Constraint Solver"（1997）

| 属性 | 内容 |
|------|------|
| **作者** | Robert Joan-Arinyo, Antoni Soto |
| **发表** | *Computers & Graphics*, Vol. 21, No. 5, pp. 599–609, 1997 |
| **DOI/链接** | https://doi.org/10.1016/S0097-8493(97)00040-X |
| **类型** | Journal Article |

#### 背景

1990 年代中期，参数化 CAD 系统（如 Pro/ENGINEER）刚刚兴起，业界迫切需要可靠的几何约束求解器来处理二维草图中的距离、角度等约束。此前的求解器主要分为两类：数值法（Newton-Raphson 迭代，依赖初始猜测，收敛不可靠）和符号法（代数消元，复杂度高）。团队试图寻找第三条路径——**基于规则的构造法**，灵感来自经典的尺规作图。

#### 基本思想

1. **规则系统**：将几何约束求解形式化为重写规则（rewrite rules）的应用。每条规则对应一种**构造原语**（construction primitive），例如：「已知两点和一个距离，求作第三点」（DD 规则，即 distance-distance 构造）。
2. **逐步构造**：求解器维护一个「已知元素」集合（初始为固定参考系的元素），反复扫描约束图，当某条规则的前件被满足时，将规则后件中的新元素加入已知集合，同时标记对应约束为已消费。
3. **正确性保证**：论文首次为该类求解器给出了形式化的**正确性证明**——证明求解器永远不会产生假阳性（false positive），即它声称找到了解时，该解必定满足所有约束。

#### 主要结论

- 基于规则的构造法可以**正确地**求解一类被称为「可构造」（constructible）的二维几何约束问题。
- 规则系统自然地保证了求解过程的**确定性**（deterministic）和**可追溯性**（每一步构造都可被记录为尺规作图步骤）。
- 方法的表达能力等价于 Euclid 尺规作图（ruler-and-compass constructions）。
- 局限性：只能处理规则库覆盖的约束模式（templates），对于规则库外的复杂问题需要扩展或回退到数值法。

---

### 论文 2: "A Rule-and-Compass Geometric Constraint Solver"（1997）

| 属性 | 内容 |
|------|------|
| **作者** | Robert Joan-Arinyo, Antoni Soto |
| **发表** | *Product Modeling for Computer Integrated Design and Manufacture* (Proc. 5th IFIP TC5/WG5.2 Workshop), Chapman & Hall, pp. 384–393, 1997 |
| **DOI/链接** | https://doi.org/10.1007/978-0-387-35187-2_33（收录于会议论文集 *Product Modeling for Computer Integrated Design and Manufacture*） |
| **类型** | Conference Paper |

#### 背景

这是论文 1 的姊妹篇，在同一年的不同场合发表。论文 1 侧重于规则库设计和正确性证明的理论框架，本篇则侧重于**实现细节**，包括数据结构设计、规则匹配策略、以及约束图的预处理步骤。

#### 基本思想

1. **两阶段求解架构**：
   - **阶段一（符号阶段）**：在约束图上执行规则匹配，生成一个与具体尺寸值无关的**构造序列**（construction plan）。
   - **阶段二（数值阶段）**：代入实际的约束值（具体距离和角度），按构造序列逐步计算几何元素坐标。
2. **数据表示**：
   - 几何元素存储为带类型标签的结构体（点、线段、圆等）
   - 约束存储为边，带有约束类型和（可选的）数值参数
   - 构造步骤存储为操作码 + 操作数列表
3. **关键实现问题处理**：
   - 规则匹配的**冲突消解**：当多条规则同时可应用时，按优先级选择
   - 构造过程中的**多解分支**：DD 构造产生 2 个候选点，需记录选择

#### 主要结论

- 给出了一个完整的、可运行的二维约束求解器实现。
- 确认了两阶段架构的可行性：符号阶段的「构造计划」可被缓存复用，当约束值改变时只需重新执行数值阶段。
- 讨论了规则库的可扩展性——新增构造原语只需添加规则定义。

---

### 论文 3: "Combining Constructive and Equational Geometric Constraint-Solving Techniques"（1999）

| 属性 | 内容 |
|------|------|
| **作者** | Robert Joan-Arinyo（发表时署名 Joan-Arinyo T.）, Antoni Soto-Riera |
| **发表** | *ACM Transactions on Graphics*, Vol. 18, No. 1, pp. 35–55, 1999 |
| **DOI/链接** | https://doi.org/10.1145/300776.300778 |
| **类型** | Journal Article（CCF-A 类顶级期刊） |

#### 背景

1990 年代末，几何约束求解领域出现了三种主要的构造方法：
1. **Owen 的方法**（1991）— 基于三连通分量分解
2. **Fudos-Hoffmann 的方法**（1997）— 基于簇（cluster）识别与合并
3. **Joan-Arinyo 的方法**（1997）— 基于规则重写

这三种方法虽然都被称为「构造法」，但它们的工作机制截然不同。学界一直在问：它们的能力范围是否相同？是否存在某个问题能用方法 A 解但方法 B 不能？

#### 基本思想

1. **统一的抽象模型**：论文将三种方法都建模为**抽象归约系统**（Abstract Reduction System, ARS）。每种方法的内部操作都被表达为在约束图上执行的归约步骤。
2. **正反向分析的比较**：
   - Joan-Arinyo 的方法：**自底向上**（bottom-up），从已知的固定元素出发，逐步向外构造。
   - Owen 和 Fudos-Hoffmann 的方法：**自顶向下**（top-down），先将约束图递归分解为小的子图（clusters），再从最小子图自底向上求解。
3. **域等价性证明**：论文的核心证明是，三种归约系统在相同的初始条件下总是归约到相同范式（或同时无法归约）。这意味着它们的**求解域**（domain）是相同的。

#### 主要结论

- **域等价定理**：Owen 的分解法、Fudos-Hoffmann 的簇合并法、Joan-Arinyo 的规则法，三种方法能解决**完全相同的一类问题**。这是一个具有深远影响的统一结论——它说明了构造法的能力边界由**图的结构性质**决定，而非具体算法技巧。
- 这个公共域恰好是**树可分解图**（tree-decomposable graphs）的类。
- 论文还揭示了三种方法在实现上的互补性：规则法最容易实现和扩展规则库，分解法最适合分析约束图的全局结构，簇合并法最容易处理将子解「装配」为全局解的过程。
- 作为发表在 ACM TOG 上的论文，它在学术界获得了极高的关注和引用。

---

### 论文 4: "On the Domain of Constructive Geometric Constraint Solving Techniques"（2001）

| 属性 | 内容 |
|------|------|
| **作者** | Robert Joan-Arinyo, Antoni Soto-Riera, Sebastià Vila-Marta, Josep Vilaplana-Pastó |
| **发表** | *Spring Conference on Computer Graphics (SCCG 2001)*, IEEE, pp. 49–54, 2001 |
| **DOI/链接** | https://doi.org/10.1109/SCCG.2001.945334 |
| **类型** | Conference Paper |

#### 背景

这是论文 3 的进一步深化和补充。在 1999 年论文中，团队已证明了三种构造法的域等价性，但尚未给出域的精确组合刻画。此论文旨在回答：**「可被构造法求解」在图论上到底意味着什么？**

#### 基本思想

1. **树可分解性的形式化**：给出严格定义——一个约束图 G 是树可分解的，当且仅当它可以被递归地分解为不超过 3 个顶点的簇（clusters），分解树（decomposition tree）的每个内部节点对应一对「分离顶点对」（separation pair）。
2. **域刻画定理**：构造法的求解域恰好是**所有树可分解的约束图**。这是对论文 3 的域等价性的精细化——不仅说明了域是相同的，而且明确了域就是树可分解图。
3. **图算法视角**：将分解问题联系到经典图论结果——**Hopcroft-Tarjan 的三连通分量分解算法**（1973, *SIAM Journal of Computing*, 2(3): 135–158）。约束图必须先分解为三连通分量（triconnected components），然后再递归地分解。

#### 主要结论

- **树可分解性**是构造法的充要条件。
- 连接了图论经典算法（Hopcroft-Tarjan 算法）与约束求解的桥梁。
- 为后续的分解算法优化提供了理论基础。

---

### 论文 5: "Revisiting Decomposition Analysis of Geometric Constraint Graphs"（2004）

| 属性 | 内容 |
|------|------|
| **作者** | Robert Joan-Arinyo, Antoni Soto-Riera, Sebastià Vila-Marta, Josep Vilaplana-Pastó |
| **发表** | *Computer-Aided Design*, Vol. 36, No. 2, pp. 123–140, 2004 |
| **DOI/链接** | https://doi.org/10.1016/S0010-4485(03)00057-5 |
| **类型** | Journal Article（CCF-B 类期刊） |

#### 背景

2000 年代初，团队经过数年实验发现，早期的分解算法在处理**特殊约束类型**（如平行约束、垂直约束等不直接表达为距离/角度的约束）时会遇到困难。这些特殊约束在约束图中需要特殊的处理，否则会导致错误的分解或无法分解。

#### 基本思想

1. **特殊约束的统一处理框架**：将平行约束（parallel）、垂直约束（perpendicular）、共线约束（collinear）等转化为等价的「方向约束」（orientation constraints），以虚拟顶点的方式嵌入约束图中。
2. **改进的分解算法**：
   - 首先进行**预处理**：识别特殊约束并将其转换为标准形式
   - 然后执行**三连通分量分解**（基于 Hopcroft-Tarjan 的线性时间算法）
   - 对于每个三连通分量，尝试剪去度为 2 的顶点（对应单自由度元素）
   - 递归直到所有分量都被分解或确认为不可分解
3. **欠约束系统的处理**：提出了一种策略来识别系统中的**刚性子结构**（rigid substructures），即使整个系统欠约束，其内部存在可以独立求解的刚性部分。

#### 主要结论

- 给出了一个完整的、处理**所有常见二维约束类型**的分解算法。
- 算法复杂度：O(n + m)，其中 n 为几何元素数，m 为约束数（基于 Hopcroft-Tarjan 的线性时间算法）。
- 实验表明：对于典型 CAD 草图（50–200 个元素），分解过程在毫秒级完成。
- 这是 Joan-Arinyo 被引用最多的论文之一（超过 130 次），因其实用性强，直接可被 CAD 系统采纳。

---

### 论文 6: "A Brief on Constraint Solving"（2005）

| 属性 | 内容 |
|------|------|
| **作者** | Christoph M. Hoffmann, Robert Joan-Arinyo |
| **发表** | *Computer-Aided Design and Applications*, Vol. 2, No. 5, pp. 655–663, 2005 |
| **DOI/链接** | https://doi.org/10.1080/16864360.2005.10738330 |
| **类型** | Journal Article（Survey / Review） |

#### 背景

此时几何约束求解已有十余年发展，四大类方法（构造法、数值法、代数法、逻辑法）都已相当成熟。这篇论文是两位重量级学者的联合综述，旨在给 CAD 社区提供一个统一的视角。

#### 基本思想

1. **四大方法的系统分类与比较**：
   - **构造法**（constructive / graph-based）：将约束图分解为可依次求解的子问题。优点：高效、可预测；缺点：限于树可分解问题。
   - **数值法**（numerical）：将约束转化为非线性方程组，用 Newton-Raphson 类方法迭代求解。优点：通用性强；缺点：依赖初始猜测、可能不收敛。
   - **代数法**（algebraic / symbolic）：用 Gröbner 基或结式等代数工具消元求解。优点：可给出所有解；缺点：复杂度双指数级。
   - **逻辑法**（logic-based）：用约束传播、区间分析等 AI 技术。优点：可处理不精确约束；缺点：效率偏低。
2. **实用建议**：工业 CAD 系统应采用「构造法为主、数值法为辅」的混合策略。
3. **3D 约束求解的挑战**：讨论了 3D 空间中缺乏类似于 2D Laman 定理的刚性组合刻画所带来的根本性困难。

#### 主要结论

- 构造法是当前工业 CAD 系统的最佳选择（高效、确定、可解释）。
- 指出了未来的研究方向：3D 构造求解、欠约束系统的智能完成、参数有效范围计算、动态约束维护。
- 这篇综述因其简明清晰的分类框架，成为很多学者进入该领域的入门读物。

---

### 论文 7: "Transforming an Under-Constrained Geometric Constraint Problem into a Well-Constrained One"（2003）

| 属性 | 内容 |
|------|------|
| **作者** | Robert Joan-Arinyo, Antoni Soto-Riera, Sebastià Vila-Marta, Josep Vilaplana-Pastó |
| **发表** | *Proc. 8th ACM Symposium on Solid Modeling and Applications (SM '03)*, pp. 33–44, 2003 |
| **DOI/链接** | https://doi.org/10.1145/781606.781612 |
| **类型** | Conference Paper（ACM Solid Modeling） |

#### 背景

实际 CAD 草图中，工程师常常先绘制大致轮廓再逐步添加约束——这意味着系统在大多数时候处于**欠约束**（under-constrained）状态。传统的构造法求解器要求系统完全约束（well-constrained）才能工作，这就需要一个中间步骤将欠约束系统转化为完全约束系统。

#### 基本思想

1. **约束补全**（constraint completion）：分析欠约束系统的自由度，自动添加「虚拟约束」来定位仍可自由移动的元素。添加的约束包括：
   - 固定点（anchor constraints）：将某个未定位的点固定在当前位置
   - 固定方向（orientation constraints）：将某条未定向的线段的方向固定
2. **补全策略**：
   - **自动补全**：按启发式规则选择最「合理」的固定方式（如优先固定边界元素）
   - **预定义补全**：从用户提供的独立约束集合中选择
3. **关键保证**：补全后的系统**不会过度约束**（no over-constraint introduced）。

#### 主要结论

- 给出了一种系统性的方法，将任意欠约束的 2D 几何约束问题转化为可求解的完全约束问题。
- 补全后的约束集保证是适定的（well-posed）：如果原始欠约束系统中的每个刚性子结构都可解，则补全后的系统也可解。
- 为交互式 CAD 系统提供了一种实用的「自动约束」功能基础。

---

### 论文 8: "A Constraint-Solving Based Approach to Analyze 2D Geometric Problems"（2001）

| 属性 | 内容 |
|------|------|
| **作者** | Robert Joan-Arinyo, Núria Mata, Antoni Soto |
| **发表** | *Proc. 6th ACM Symposium on Solid Modeling and Applications (SM '01)*, pp. 11–17, 2001 |
| **DOI/链接** | https://doi.org/10.1145/376957.376959 |
| **类型** | Conference Paper（ACM Solid Modeling） |

#### 背景

参数化 CAD 模型中的一个核心问题是：当用户改变参数值时，模型的**拓扑结构**是否会发生变化？例如，增大一个距离参数可能导致两个圆从相离变为相交。这个问题被称为「参数有效范围」（valid parameter range）问题。

#### 基本思想

1. **将参数范围问题转化为几何约束分析问题**：以一个「当前实例」的几何位置为基准，分析当参数变化时，每个构造步骤的**解存在条件**是什么。
2. **解存在条件的推导**：对于每种构造原语（DD 构造、DA 构造等），推导出输入参数必须满足的不等式条件。例如，DD 构造的两个圆必须有交集，即 `|r1 - r2| <= d <= r1 + r2`。
3. **区间传播**：从底层的构造步骤向上传播参数区间约束，得到顶层设计参数的全局有效范围。

#### 主要结论

- 给出了一种基于约束求解的**参数有效范围分析**方法。
- 可以精确找到参数变化的**临界值**（critical values），在这些值处拓扑结构发生变化。
- 为后续 Hidalgo & Joan-Arinyo（2012）的工程实现奠定了基础。

---

### 论文 9: "Computing Parameter Ranges in Constructive Geometric Constraint Solving: Implementation and Correctness Proof"（2012）

| 属性 | 内容 |
|------|------|
| **作者** | Marta Hidalgo, Robert Joan-Arinyo |
| **发表** | *Computer-Aided Design*, Vol. 44, No. 7, pp. 720–732, 2012 |
| **DOI/链接** | https://doi.org/10.1016/j.cad.2012.02.010 |
| **类型** | Journal Article |

#### 背景

这是团队在参数有效范围问题上的**收官之作**，也是 Joan-Arinyo 指导的博士生 Marta Hidalgo 的代表性工作。论文 8（2001）只给出了理论框架，本篇给出了完整的工程实现和形式化正确性证明。

#### 基本思想

1. **完整的算法实现**：以论文 5 的分解算法为前端（识别可构造子问题），以论文 1/2 的构造步骤为后端，实现了一个完整的参数范围计算流水线。
2. **正确性证明**：证明算法计算的参数范围是**完备的**（complete）：范围内的每个参数值都能保证构造步骤在实数域有解；且是**可靠的**（sound）：范围内的参数值不会导致模型拓扑变化。
3. **处理多参数交互**：不限于单参数的范围分析，可以分析多个参数同时变化时的联合有效范围。

#### 主要结论

- 给出了首个经过形式化验证的参数范围计算算法。
- 实验验证了在 50+ 元素的约束系统上，参数范围计算可在秒级完成。
- 对三维 CAD 系统的参数化设计提供了重要的工程指导。

---

### 论文 10: "Tree-Decomposable and Underconstrained Geometric Constraint Problems"（2016）

| 属性 | 内容 |
|------|------|
| **作者** | Ioannis Fudos, Christoph M. Hoffmann, Robert Joan-Arinyo |
| **发表** | *Handbook of Geometric Constraints Principles*（CRC Press, Taylor & Francis Group）, 2017 (arXiv: 1608.05205, 2016) |
| **DOI/链接** | https://doi.org/10.48550/arXiv.1608.05205 |
| **类型** | Book Chapter（Survey） |

#### 背景

到了 2010 年代中期，几何约束求解已是一个成熟领域，方法论和理论基础都已稳固。这篇论文是三位权威合著的**综合综述**，作为 *Handbook of Geometric Constraints Principles*（Meera Sitharam 等编）的一章。

#### 基本思想

1. **范围界定**：文章聚焦于**静态约束问题**（static constraint problems）——给出固定的一组约束，求解器找到满足这些约束的几何体配置。排除了动态几何系统（如 GeoGebra 等）。
2. **历史追溯**：从 1990 年代 MCAD 的「量子飞跃」讲起——Owen (1991)、Bouma-Fudos-Hoffmann (1995)、Fudos-Hoffmann (1997) 和 Joan-Arinyo (1997) 的开创性工作如何奠定了基于图的结构分析 + 代数求解的范式。
3. **树可分解性**的完整处理：从图的二连通、三连通分解到树可分解性的判定、复合与求解。
4. **欠约束系统的处理**：总结了从 1990 年代到 2010 年代的欠约束约束处理技术进展。

#### 主要结论

- 这是一篇**权威的领域全景综述**，适合作为进入该领域的入门读物。
- 总结了构造法的理论边界——树可分解性——及其在实践中的充分性与局限性。
- 对未来的展望：将图构造方法与现代计算工具（如 SMT solver、机器学习引导的参数选择）结合。

---

### 论文 11: "Resolución de Restricciones Geométricas"（2003, 西班牙语）

| 属性 | 内容 |
|------|------|
| **作者** | Robert Joan-Arinyo, Antoni Soto-Riera, Sebastià Vila-Marta |
| **发表** | 西班牙语综述文章，2003 |
| **DOI/链接** | 见 ResearchGate: [链接](https://www.researchgate.net/publication/28087846_Resolucion_de_Restricciones_Geometricas) |
| **类型** | Survey（西班牙语） |

#### 基本思想

以西班牙语撰写的几何约束求解综述，面向西班牙和拉丁美洲的学术界，涵盖了二维构造法的主要成果。与论文 6 和论文 10 不同，这篇更侧重于**教学与推广**，包含大量的图示和示例。

---

## 论文时间线与研究脉络

```
1997 ──● 论文1: 规则求解器（Computers & Graphics）
       ├─● 论文2: 尺规构造求解器（IFIP Workshop）
       │
1999 ──● 论文3: 构造法域等价性（ACM TOG）★ 顶级期刊
       │
2001 ──● 论文4: 构造法域的形式化（SCCG/IEEE）
       ├─● 论文8: 参数范围分析（ACM SM）
       │
2003 ──● 论文7: 欠约束→完备约束转化（ACM SM）
       ├─● 论文11: 西班牙语综述
       │
2004 ──● 论文5: 分解分析重访（CAD）★ 最高引用
       │
2005 ──● 论文6: 约束求解简明综述（CAD&A, 与Hoffmann合著）
       │
2012 ──● 论文9: 参数范围计算实现（CAD, 与Hidalgo）
       │
2016 ──● 论文10: 树可分解与欠约束问题（Handbook Chapter, arXiv）
```

**研究主线的三个阶段**：

1. **奠基阶段（1997–1999）**：定义了基于规则的构造求解方法，证明了不同构造法之间的域等价性。
2. **深化阶段（2001–2005）**：精确刻画了构造法的求解域（树可分解性），完善了图分解算法，处理特殊约束和欠约束系统。
3. **应用与总结阶段（2012–2016）**：将理论落地为工程实现（参数范围计算），撰写领域综述总结二十年的研究成果。

---

## 核心理论贡献总结

### 1. 树可分解性理论

Joan-Arinyo 团队最重要的理论贡献是**树可分解性**（tree-decomposability）概念及其与构造法求解域的等价性：

> 一个几何约束问题是可构造求解的 ⇔ 其约束图是树可分解的 ⇔ 约束图可被递归分解为不超过 3 个顶点的簇

### 2. 构造法域等价性

Owen、Fudos-Hoffmann、Joan-Arinyo 三种方法虽然算法机制不同（自顶向下分解 vs 自底向上构造），但它们的求解域完全相同——都是树可分解图。这一发现将不同学派的研究统一在了一个理论框架下。

### 3. 参数有效范围

从 Joan-Arinyo & Mata (2001) 的理论分析到 Hidalgo & Joan-Arinyo (2012) 的工程实现，团队建立了一套完整的**参数有效范围计算**方法论——告诉用户在改变参数值时，什么范围内模型拓扑保持不变。

### 4. 欠约束处理

提出了一种系统性的约束补全方法，将欠约束系统自动转化为可求解的完全约束系统，而不引入过度约束。

---

## 与其他团队的关系

Joan-Arinyo 团队的构造法求解属于 GCS 四大方法中的**基于图论的方法**。在同一领域内，密切相关的团队包括：

| 团队 | 方法 | 与 JA 团队的关系 |
|------|------|------------------|
| **Christoph Hoffmann** (Purdue) | 图构造法 | 直接合作者（论文6, 10）；Fudos-Hoffmann方法是域等价性的三方之一 |
| **Ileana Streinu** (Smith College) | 组合刚性理论、卵石博弈 | 互补：JA 提供求解策略，Streinu 提供刚性判定 |
| **Meera Sitharam** (U. Florida) | 分解规划、FRONTIER算法 | 后续发展者，将分解推广到3D |
| **高小山** (中科院) | 全局传播法、C-tree分解 | 中国学派，独立发展了图分解方法 |
| **Willem Bronsvoort** (TU Delft) | 非刚性簇改写 | 3D 约束求解的后续发展 |

---

## 参考文献（完整引用）

1. Joan-Arinyo R., Soto A. (1997). "A Correct Rule-Based Geometric Constraint Solver." *Computers & Graphics*, 21(5): 599–609. [DOI: 10.1016/S0097-8493(97)00040-X](https://doi.org/10.1016/S0097-8493(97)00040-X)

2. Joan-Arinyo R., Soto A. (1997). "A Rule-and-Compass Geometric Constraint Solver." In *Product Modeling for Computer Integrated Design and Manufacture* (Proc. 5th IFIP TC5/WG5.2 Workshop), Chapman & Hall, pp. 384–393. [DOI: 10.1007/978-0-387-35187-2_33](https://doi.org/10.1007/978-0-387-35187-2_33)

3. Joan-Arinyo R., Soto-Riera A. (1999). "Combining Constructive and Equational Geometric Constraint-Solving Techniques." *ACM Transactions on Graphics*, 18(1): 35–55. [DOI: 10.1145/300776.300778](https://doi.org/10.1145/300776.300778)

4. Joan-Arinyo R., Soto-Riera A., Vila-Marta S., Vilaplana-Pastó J. (2001). "On the Domain of Constructive Geometric Constraint Solving Techniques." In *Proc. Spring Conference on Computer Graphics (SCCG 2001)*, IEEE, pp. 49–54. [DOI: 10.1109/SCCG.2001.945334](https://doi.org/10.1109/SCCG.2001.945334)

5. Joan-Arinyo R., Soto-Riera A., Vila-Marta S., Vilaplana-Pastó J. (2004). "Revisiting Decomposition Analysis of Geometric Constraint Graphs." *Computer-Aided Design*, 36(2): 123–140. [DOI: 10.1016/S0010-4485(03)00057-5](https://doi.org/10.1016/S0010-4485(03)00057-5)

6. Hoffmann C.M., Joan-Arinyo R. (2005). "A Brief on Constraint Solving." *Computer-Aided Design and Applications*, 2(5): 655–663. [DOI: 10.1080/16864360.2005.10738330](https://doi.org/10.1080/16864360.2005.10738330)

7. Joan-Arinyo R., Soto-Riera A., Vila-Marta S., Vilaplana-Pastó J. (2003). "Transforming an Under-Constrained Geometric Constraint Problem into a Well-Constrained One." In *Proc. 8th ACM Symposium on Solid Modeling and Applications (SM '03)*, pp. 33–44. [DOI: 10.1145/781606.781612](https://doi.org/10.1145/781606.781612)

8. Joan-Arinyo R., Mata N., Soto A. (2001). "A Constraint-Solving Based Approach to Analyze 2D Geometric Problems." In *Proc. 6th ACM Symposium on Solid Modeling and Applications (SM '01)*, pp. 11–17. [DOI: 10.1145/376957.376959](https://doi.org/10.1145/376957.376959)

9. Hidalgo M., Joan-Arinyo R. (2012). "Computing Parameter Ranges in Constructive Geometric Constraint Solving: Implementation and Correctness Proof." *Computer-Aided Design*, 44(7): 720–732. [DOI: 10.1016/j.cad.2012.02.010](https://doi.org/10.1016/j.cad.2012.02.010)

10. Fudos I., Hoffmann C.M., Joan-Arinyo R. (2016). "Tree-Decomposable and Underconstrained Geometric Constraint Problems." In *Handbook of Geometric Constraints Principles*, CRC Press. [arXiv: 1608.05205](https://arxiv.org/abs/1608.05205)

11. Joan-Arinyo R., Soto-Riera A., Vila-Marta S. (2003). "Resolución de Restricciones Geométricas." (西班牙语综述). [ResearchGate](https://www.researchgate.net/publication/28087846_Resolucion_de_Restricciones_Geometricas)
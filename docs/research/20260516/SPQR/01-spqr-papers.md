# SPQR算法与点三连通分解：论文研究

## 1. 核心论文

### 1.1 Hopcroft & Tarjan (1973) — 开山之作

**论文**：Hopcroft, J.E., Tarjan, R.E. "Dividing a Graph into Triconnected Components"
**期刊**：SIAM Journal on Computing, Vol. 2, No. 3, September 1973, pp. 135-158
**DOI**：10.1137/0202012

**核心贡献**：
- 首次提出将图分解为三连通分量（triconnected components）的线性时间算法
- 算法时间复杂度 O(V+E)
- 引入分离对（separation pair）的概念
- 定义了三种类型的三连通分量：串联（series）、并联（parallel）、刚性（rigid）

**算法核心步骤**：
1. 找到图的所有双连通分量（biconnected components）
2. 对每个双连通分量，找到所有分离对
3. 沿分离对将图分裂为三连通分量
4. 将三连通分量组织为SPQR树

**分离对（Separation Pair）定义**：
在双连通图G中，顶点对{a, b}是分离对，当且仅当删除a和b后图变得不连通。

**三连通分量类型**：
| 类型 | 结构 | 骨架 |
|------|------|------|
| Series (S) | 串联结构，多个子图按顺序排列 | 简单路径/环 |
| Parallel (P) | 并联结构，多条路径共存 | 多重边束 |
| Rigid (R) | 三连通图，不可再分 | 三连通图 |

### 1.2 Di Battista & Tamassia (1996) — SPQR树正式定义

**论文**：Di Battista, G., Tamassia, R. "On-line maintenance of triconnected components with SPQR-trees"
**期刊**：Algorithmica, Vol. 15, No. 4, pp. 302-318, 1996
**DOI**：10.1007/BF01961541

**核心贡献**：
- 正式定义SPQR树数据结构
- 提出在线维护三连通分量的算法
- SPQR树可用于增量式平面性测试

**SPQR树定义**：
- S节点：串联（Series）骨架，骨架是一条简单路径
- P节点：并联（Parallel）骨架，骨架是两个顶点之间的多重边
- Q节点：边（Quoted）骨架，代表原图中的一条边
- R节点：刚性（Rigid）骨架，骨架是三连通图

**SPQR树性质**：
1. SPQR树T唯一确定（在同构意义下）
2. T的节点对应三连通分量
3. 相邻节点通过共享的虚边（virtual edge）连接
4. 每条原图中的边恰好出现在一个Q节点中
5. SPQR树编码了双连通图的所有2-分离子

### 1.3 Gutwenger & Mutzel (2001) — 线性时间实现

**论文**：Gutwenger, C., Mutzel, P. "A Linear Time Implementation of SPQR-Trees"
**会议**：GD 2000, LNCS Vol. 1984, pp. 77-90, Springer, 2001
**DOI**：10.1007/3-540-44541-2_8

**核心贡献**：
- 给出SPQR树的实用线性时间实现
- 修正了Hopcroft-Tarjan原始算法中的一些问题
- 该实现被集成到OGDF（Open Graph Drawing Framework）中

**关键改进**：
- 正确处理多重边（parallel edges）
- 更清晰的分离对检测逻辑
- 高效的虚边管理

### 1.4 Hopcroft & Tarjan (1974) — 平面性测试

**论文**：Hopcroft, J., Tarjan, R. "Efficient Planarity Testing"
**期刊**：J. ACM, Vol. 21, No. 4, pp. 549-568, 1974
**DOI**：10.1145/321850.321852

**关联**：平面性测试与SPQR树密切相关，SPQR树可用于枚举所有平面嵌入。

## 2. 后续重要论文

### 2.1 动态维护

| 论文 | 年份 | 核心贡献 |
|------|------|----------|
| Di Battista & Tamassia | 1996 | 在线维护SPQR树 |
| Galil, Italiano & Sarnak | 1999 | 全动态平面性测试 |
| Fink & Rutter (arXiv:2301.03972) | 2023 | 节点扩展下的SPQR树维护 |

### 2.2 计算生物学应用

| 论文 | 年份 | 核心贡献 |
|------|------|----------|
| Nijkamp et al. (MaryGold) | 2013 | 使用SPQR树检测基因组变异 |
| Sena et al. (arXiv:2604.08071) | 2026 | 线性时间识别bubble-like子图 |

### 2.3 图绘制应用

| 论文 | 年份 | 核心贡献 |
|------|------|----------|
| Didimo et al. (arXiv:2208.12558) | 2022 | SPQ-tree用于直角平面性测试 |
| Da Lozzo, Frati & Rutter (arXiv:2603.17128) | 2026 | SPQ(R)-tree用于向上书嵌入 |

### 2.4 几何约束求解应用

| 论文 | 年份 | 核心贡献 |
|------|------|----------|
| 曹春红等 | 2014 | 基于D-tree分解的几何约束求解 |
| Fudos & Hoffmann | 1997 | 图构造方法求解几何约束系统 |

## 3. 关键论文引用信息

```
@article{HopcroftTarjan1973,
  author  = {Hopcroft, J. E. and Tarjan, R. E.},
  title   = {Dividing a Graph into Triconnected Components},
  journal = {SIAM Journal on Computing},
  volume  = {2},
  number  = {3},
  pages   = {135--158},
  year    = {1973},
  doi     = {10.1137/0202012}
}

@article{DiBattistaTamassia1996,
  author  = {Di Battista, G. and Tamassia, R.},
  title   = {On-line Maintenance of Triconnected Components with {SPQR}-trees},
  journal = {Algorithmica},
  volume  = {15},
  number  = {4},
  pages   = {302--318},
  year    = {1996},
  doi     = {10.1007/BF01961541}
}

@inproceedings{GutwengerMutzel2001,
  author    = {Gutwenger, C. and Mutzel, P.},
  title     = {A Linear Time Implementation of {SPQR}-trees},
  booktitle = {GD 2000},
  series    = {LNCS},
  volume    = {1984},
  pages     = {77--90},
  publisher = {Springer},
  year      = {2001},
  doi       = {10.1007/3-540-44541-2_8}
}

@article{HopcroftTarjan1974,
  author  = {Hopcroft, J. and Tarjan, R.},
  title   = {Efficient Planarity Testing},
  journal = {J. ACM},
  volume  = {21},
  number  = {4},
  pages   = {549--568},
  year    = {1974},
  doi     = {10.1145/321850.321852}
}
```

## 4. 论文获取方式

| 论文 | 获取方式 |
|------|----------|
| Hopcroft & Tarjan 1973 | SIAM Digital Library (DOI: 10.1137/0202012) |
| Di Battista & Tamassia 1996 | SpringerLink (DOI: 10.1007/BF01961541) |
| Gutwenger & Mutzel 2001 | SpringerLink (DOI: 10.1007/3-540-44541-2_8) |
| Hopcroft & Tarjan 1974 | ACM Digital Library (DOI: 10.1145/321850.321852) |
| Fink & Rutter 2023 | arXiv:2301.03972 |
| Sena et al. 2026 | arXiv:2604.08071 |

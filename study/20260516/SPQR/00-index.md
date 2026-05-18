# SPQR算法与点三连通分解研究索引

研究日期：2026-05-16

## 研究主题

### [01-spqr-papers.md](01-spqr-papers.md)
**SPQR算法与点三连通分解论文研究**

核心内容：
- Hopcroft & Tarjan 1973：开山之作，O(V+E)三连通分量分解
- Di Battista & Tamassia 1996：SPQR树正式定义与在线维护
- Gutwenger & Mutzel 2001：线性时间实用实现（OGDF）
- Hopcroft & Tarjan 1974：平面性测试
- 后续论文：动态维护、计算生物学、图绘制、几何约束求解
- 完整BibTeX引用信息

### [02-spqr-libraries.md](02-spqr-libraries.md)
**SPQR算法实现库研究**

核心内容：
- NetworkX (Python)：spqr_tree() API，纯Python实现
- OGDF (C++)：Gutwenger-Mutzel线性时间实现，生产级
- Boost Graph Library (C++)：底层图算法支持
- SageMath (Python)：SPQR树功能
- 实现方式对比表

### [03-spqr-implementation.py](03-spqr-implementation.py)
**SPQR算法Python实现**

核心功能：
- `Graph`类：图数据结构，支持双连通/三连通检测
- `is_biconnected(graph)`：双连通性检测
- `find_separation_pairs(graph)`：分离对查找
- `is_triconnected(edge_list)`：三连通性检测
- `spqr_decompose(edge_list)`：SPQR树分解

算法实现：
- 递归分解：检测环→检测bond→检测三连通→分离对分裂→递归
- 分离对分裂：移除顶点对→找连通分量→分配边→添加虚边
- 虚边管理：真实边归P节点，子组件用虚边连接
- 树简化：合并相邻S节点

测试结果：
| 图 | 节点数 | 分解结果 |
|----|--------|----------|
| K3 | 1 | R(3边) |
| K4 | 1 | R(6边) |
| K5 | 1 | R(10边) |
| Diamond | 3 | P(1真实+2虚) + 2×R(2真实+1虚) |
| C5 | 1 | S(5边) |
| 共享边双三角 | 3 | P(1真实+2虚) + 2×R(2真实+1虚) |

## 核心概念

### 分离对（Separation Pair）
双连通图G中，顶点对{a, b}是分离对，当且仅当删除a和b后图变得不连通。

### SPQR树节点类型
| 类型 | 骨架 | 含义 |
|------|------|------|
| Q | 单条边 | 原图中的边 |
| S | 简单环(≥4顶点) | 串联结构 |
| P | 多重边(≥3条) | 并联结构 |
| R | 三连通图 | 刚性结构 |

### SPQR树性质
1. SPQR树唯一确定（同构意义下）
2. 每条原图边恰好出现在一个节点中
3. 相邻节点通过共享虚边连接
4. SPQR树编码了双连通图的所有2-分离子
5. SPQR树可用于枚举所有平面嵌入

# SPQR算法实现库研究

## 1. NetworkX (Python)

### 1.1 概述

NetworkX从3.x版本开始提供SPQR树功能，主要API：
- `nx.spqr_tree(G)` — 返回SPQR树
- `nx.triconnected_components(G)` — 返回三连通分量（实验性）

**位置**：`networkx/algorithms/approximation/spqr_tree.py`（旧版）
**新版位置**：`networkx/algorithms/components/biconnected.py` 中的辅助函数

### 1.2 NetworkX实现方式

NetworkX的SPQR树实现基于以下步骤：
1. 验证输入图是双连通的
2. 使用DFS找到分离对
3. 沿分离对分解为三连通分量
4. 构建SPQR树

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1,2),(2,3),(3,1),(2,4),(4,5),(5,2)])

tree = nx.spqr_tree(G)
for node in tree:
    print(f"Type: {node[0]}, Edges: {node[1].edges()}")
```

### 1.3 NetworkX实现的特点

- 纯Python实现，代码可读性好
- 基于Hopcroft-Tarjan算法的思想
- 时间复杂度不是严格的线性（Python开销）
- 适合中小规模图和教学用途

## 2. OGDF (C++)

### 2.1 概述

OGDF（Open Graph Drawing Framework）包含Gutwenger-Mutzel线性时间SPQR树实现，是最权威的开源实现。

**GitHub**：https://github.com/ogdf/ogdf

### 2.2 关键类

```cpp
#include <ogdf/decomposition/SPQRTree.h>
#include <ogdf/decomposition/Skeleton.h>

ogdf::SPQRTree spqr(G);
for (ogdf::node v : spqr.nodes()) {
    ogdf::Skeleton& S = spqr.skeleton(v);
    std::cout << "Type: " << spqr.typeOf(v) << std::endl;
    for (ogdf::edge e : S.getGraph().edges) {
        if (S.isVirtual(e)) {
            std::cout << "  Virtual edge" << std::endl;
        } else {
            std::cout << "  Real edge: " << e << std::endl;
        }
    }
}
```

### 2.3 OGDF实现特点

- 严格线性时间实现 O(V+E)
- 基于Gutwenger-Mutzel 2001论文
- 正确处理多重边
- 生产级代码质量
- 被学术界广泛使用

## 3. Boost Graph Library (C++)

### 3.1 概述

BGL不直接提供SPQR树，但提供构建SPQR树所需的基础算法：
- `biconnected_components()` — 双连通分量
- `articulation_points()` — 割点
- DFS相关工具

### 3.2 使用BGL构建SPQR树

需要自行实现分离对检测和三连通分量分解，BGL仅提供底层图算法支持。

## 4. SageMath (Python)

### 4.1 SPQR树支持

SageMath提供SPQR树功能：

```python
G = Graph([(1,2),(2,3),(3,1),(2,4)])
ST = G.SPQR_tree()
```

**注意**：SageMath的SPQR树实现需要平面嵌入作为输入，这与标准SPQR树定义有所不同。

## 5. graph-tool (Python/C++)

graph-tool不直接提供SPQR树，但提供高效的图算法基础设施。

## 6. 其他实现

### 6.1 MaryGold (C++/Python)

用于基因组学中的bubble检测，内部使用SPQR树分解。
**来源**：http://bioinformatics.tudelft.nl/software

### 6.2 自定义实现

多个学术论文附带SPQR树实现，但通常不作为独立库发布。

## 7. 实现方式对比

| 库 | 语言 | 时间复杂度 | 多重边支持 | 易用性 | 生产就绪 |
|-----|------|-----------|-----------|--------|---------|
| NetworkX | Python | O(V+E)·k | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| OGDF | C++ | O(V+E) | ✅ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| SageMath | Python | O(V+E) | ⚠️ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| BGL | C++ | 需自行实现 | 需自行实现 | ⭐⭐ | ⭐⭐⭐⭐ |
| graph-tool | Python/C++ | 需自行实现 | 需自行实现 | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## 8. 推荐方案

对于GCS项目，推荐以下策略：
1. **原型开发**：使用NetworkX的`spqr_tree()`快速验证
2. **生产部署**：参考OGDF的Gutwenger-Mutzel实现，用C++重写
3. **自定义需求**：基于本文档第3部分的Python实现进行定制

## 9. NetworkX SPQR树源码分析

NetworkX的SPQR树实现核心逻辑：

```python
def spqr_tree(G):
    if not is_biconnected(G):
        raise NetworkXError("Input graph is not biconnected")

    # Step 1: Find all separation pairs
    # Step 2: Split graph along separation pairs
    # Step 3: Classify components as S, P, R, or Q
    # Step 4: Build tree structure

    # Internal representation uses:
    # - DFS numbering for separation pair detection
    # - Stack-based component tracking
    # - Virtual edges for reconnection
```

**关键实现细节**：
- 使用DFS遍历计算lowpoint值
- lowpoint用于检测分离对
- 分离对类型判定基于邻域结构
- 虚边用于连接相邻的三连通分量

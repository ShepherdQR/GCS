"""
SPQR Tree Implementation for Triconnected Component Decomposition

Based on:
- Hopcroft, J.E., Tarjan, R.E. "Dividing a Graph into Triconnected Components"
  SIAM J. Computing, Vol. 2, No. 3, 1973, pp. 135-158
- Gutwenger, C., Mutzel, P. "A Linear Time Implementation of SPQR-Trees"
  GD 2000, LNCS Vol. 1984, pp. 77-90, Springer, 2001
- Di Battista, G., Tamassia, R. "On-line maintenance of triconnected components
  with SPQR-trees" Algorithmica, Vol. 15, No. 4, 1996, pp. 302-318

Algorithm:
1. Check biconnectivity of input graph
2. Recursively decompose:
   - If triconnected (no separation pairs) → R node
   - If a simple cycle (all degree 2) → S node
   - If a bond (2 vertices, multiple edges) → P node
   - Otherwise, find a separation pair, split, and recurse
3. Build SPQR tree connecting components via virtual edges
"""

from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Tuple, List, Set, Dict


class NodeType(Enum):
    Q = "Q"
    S = "S"
    P = "P"
    R = "R"


@dataclass
class SPQRNode:
    node_type: NodeType
    edges: list = field(default_factory=list)
    virtual_edges: list = field(default_factory=list)
    children: list = field(default_factory=list)
    parent: Any = None
    id: int = 0

    @property
    def vertices(self):
        verts = set()
        for u, v in self.edges + self.virtual_edges:
            verts.add(u)
            verts.add(v)
        return verts

    @property
    def all_edges(self):
        return self.edges + self.virtual_edges

    def __repr__(self):
        return (f"SPQRNode({self.node_type.value}, "
                f"edges={self.edges}, virtual={self.virtual_edges})")


class SPQRTree:
    def __init__(self):
        self.nodes: List[SPQRNode] = []
        self.root: Optional[SPQRNode] = None
        self._next_id = 0

    def add_node(self, node_type: NodeType, edges=None, virtual_edges=None) -> SPQRNode:
        node = SPQRNode(
            node_type=node_type,
            edges=list(edges or []),
            virtual_edges=list(virtual_edges or []),
            id=self._next_id
        )
        self._next_id += 1
        self.nodes.append(node)
        return node

    def connect(self, parent: SPQRNode, child: SPQRNode, virtual_edge):
        if virtual_edge not in parent.virtual_edges:
            parent.virtual_edges.append(virtual_edge)
        if virtual_edge not in child.virtual_edges:
            child.virtual_edges.append(virtual_edge)
        child.parent = parent
        if child not in parent.children:
            parent.children.append(child)

    def __repr__(self):
        lines = [f"SPQRTree(nodes={len(self.nodes)})"]
        for node in self.nodes:
            lines.append(f"  {node}")
        return "\n".join(lines)


class Graph:
    def __init__(self):
        self.adj: Dict[Any, Set[Any]] = defaultdict(set)
        self._edges: Set[Tuple] = set()

    def add_edge(self, u, v):
        self.adj[u].add(v)
        self.adj[v].add(u)
        self._edges.add((min(u, v), max(u, v)))

    def add_edges_from(self, edge_list):
        for u, v in edge_list:
            self.add_edge(u, v)

    @property
    def vertices(self):
        return set(self.adj.keys())

    @property
    def edges(self):
        return set(self._edges)

    @property
    def num_vertices(self):
        return len(self.adj)

    @property
    def num_edges(self):
        return len(self._edges)

    def degree(self, v):
        return len(self.adj[v])

    def neighbors(self, v):
        return self.adj[v]

    def copy(self):
        g = Graph()
        for e in self._edges:
            u, v = e
            g.adj[u].add(v)
            g.adj[v].add(u)
        g._edges = set(self._edges)
        return g

    def subgraph_on_edges(self, edge_set):
        g = Graph()
        for e in edge_set:
            u, v = e
            g.add_edge(u, v)
        return g

    def remove_vertices(self, *vertices_to_remove):
        g = self.copy()
        for v in vertices_to_remove:
            if v in g.adj:
                for u in list(g.adj[v]):
                    g._edges.discard((min(u, v), max(u, v)))
                    g.adj[u].discard(v)
                del g.adj[v]
        return g

    def is_connected(self):
        verts = list(self.vertices)
        if not verts:
            return True
        visited = set()
        stack = [verts[0]]
        visited.add(verts[0])
        while stack:
            u = stack.pop()
            for v in self.neighbors(u):
                if v not in visited:
                    visited.add(v)
                    stack.append(v)
        return len(visited) == len(verts)

    def connected_components_after_removal(self, *vertices_to_remove):
        g = self.remove_vertices(*vertices_to_remove)
        visited = set()
        components = []
        for v in g.vertices:
            if v not in visited:
                comp = set()
                stack = [v]
                visited.add(v)
                while stack:
                    u = stack.pop()
                    comp.add(u)
                    for w in g.neighbors(u):
                        if w not in visited:
                            visited.add(w)
                            stack.append(w)
                components.append(comp)
        return components


def is_biconnected(graph: Graph) -> bool:
    verts = list(graph.vertices)
    if len(verts) < 2:
        return len(verts) <= 1
    if not graph.is_connected():
        return False
    if len(verts) <= 2:
        return len(graph.edges) >= 1
    for v in verts:
        components = graph.connected_components_after_removal(v)
        if len(components) > 1:
            return False
    return True


def find_separation_pairs(graph: Graph) -> List[Tuple]:
    verts = list(graph.vertices)
    if len(verts) < 2:
        return []
    separation_pairs = set()
    vert_list = sorted(verts)
    for i in range(len(vert_list)):
        for j in range(i + 1, len(vert_list)):
            a, b = vert_list[i], vert_list[j]
            components = graph.connected_components_after_removal(a, b)
            if len(components) > 1:
                separation_pairs.add((a, b))
    return sorted(separation_pairs)


def is_triconnected(edge_list) -> bool:
    graph = Graph()
    graph.add_edges_from(edge_list)
    if not is_biconnected(graph):
        return False
    return len(find_separation_pairs(graph)) == 0


def _is_simple_cycle(graph: Graph) -> bool:
    verts = graph.vertices
    if len(verts) < 3:
        return False
    return all(graph.degree(v) == 2 for v in verts)


def _is_bond(graph: Graph) -> bool:
    verts = graph.vertices
    if len(verts) != 2:
        return False
    return len(graph.edges) >= 2


def _split_at_pair(graph: Graph, a, b) -> List[Set[Tuple]]:
    all_edges = graph.edges
    if not all_edges:
        return []

    reduced = graph.remove_vertices(a, b)
    components = []
    visited = set()
    for v in reduced.vertices:
        if v not in visited:
            comp = set()
            stack = [v]
            visited.add(v)
            while stack:
                u = stack.pop()
                comp.add(u)
                for w in reduced.neighbors(u):
                    if w not in visited:
                        visited.add(w)
                        stack.append(w)
            components.append(comp)

    if len(components) <= 1:
        return [all_edges]

    result = []
    for comp in components:
        comp_edges = set()
        for u, v in all_edges:
            if u in comp or v in comp:
                comp_edges.add((u, v))
        for u, v in all_edges:
            if (u == a or u == b) and (v in comp):
                comp_edges.add((u, v))
            if (v == a or v == b) and (u in comp):
                comp_edges.add((u, v))
        comp_edges.add((min(a, b), max(a, b)))
        result.append(comp_edges)

    return result


def _classify_component(edges: Set[Tuple]) -> NodeType:
    if len(edges) == 0:
        return NodeType.Q

    verts = set()
    adj_local = defaultdict(set)
    for u, v in edges:
        verts.add(u)
        verts.add(v)
        adj_local[u].add(v)
        adj_local[v].add(u)

    if len(verts) == 2:
        return NodeType.P

    all_degree_2 = all(len(adj_local[v]) == 2 for v in verts if v in adj_local)
    if all_degree_2 and len(verts) >= 3:
        if len(verts) == 3:
            return NodeType.R
        return NodeType.S

    return NodeType.R


def spqr_decompose(edge_list) -> SPQRTree:
    graph = Graph()
    graph.add_edges_from(edge_list)

    if not is_biconnected(graph):
        raise ValueError("Graph is not biconnected. SPQR tree requires a biconnected graph.")

    tree = SPQRTree()
    all_original_edges = set(graph.edges)
    virtual_edges_global = set()

    def _decompose_recursive(g: Graph, virtual_edge_context=None) -> SPQRNode:
        verts = g.vertices
        edges = g.edges

        def _split_edges(edges, virtual_edge_context):
            real = sorted([e for e in edges
                           if e in all_original_edges and e != virtual_edge_context])
            virt = sorted([e for e in edges
                           if e not in all_original_edges or e == virtual_edge_context])
            if virtual_edge_context and virtual_edge_context not in virt:
                virt.append(virtual_edge_context)
            return real, virt

        if _is_simple_cycle(g) and len(verts) >= 4:
            real, virt = _split_edges(edges, virtual_edge_context)
            node = tree.add_node(NodeType.S, edges=real, virtual_edges=virt)
            return node

        if _is_bond(g):
            real, virt = _split_edges(edges, virtual_edge_context)
            node = tree.add_node(NodeType.P, edges=real, virtual_edges=virt)
            return node

        sep_pairs = find_separation_pairs(g)

        if not sep_pairs:
            real, virt = _split_edges(edges, virtual_edge_context)
            node = tree.add_node(NodeType.R, edges=real, virtual_edges=virt)
            return node

        pair = sep_pairs[0]
        a, b = pair
        subgraphs = _split_at_pair(g, a, b)

        if len(subgraphs) <= 1:
            real = sorted([e for e in edges if e in all_original_edges])
            virt = sorted([e for e in edges if e not in all_original_edges])
            node = tree.add_node(NodeType.R, edges=real, virtual_edges=virt)
            return node

        virtual_edge = (min(a, b), max(a, b))
        virtual_edges_global.add(virtual_edge)

        num_subgraphs = len(subgraphs)
        real_ab = (min(a, b), max(a, b)) in all_original_edges
        parent_real = [(min(a, b), max(a, b))] if real_ab else []
        parent_type = NodeType.P if (num_subgraphs >= 2 and real_ab) or num_subgraphs >= 3 else NodeType.S
        parent_node = tree.add_node(parent_type, edges=parent_real, virtual_edges=[])

        for comp_edges in subgraphs:
            sub_edges = comp_edges - {virtual_edge}
            if real_ab:
                sub_edges = sub_edges - {(min(a, b), max(a, b))}
            sub_g = g.subgraph_on_edges(sub_edges)
            sub_g.add_edge(a, b)
            child_node = _decompose_recursive(sub_g, virtual_edge)
            tree.connect(parent_node, child_node, virtual_edge)

        return parent_node

    root_node = _decompose_recursive(graph)

    _simplify_tree(tree)

    tree.root = tree.nodes[0] if tree.nodes else None
    return tree


def _simplify_tree(tree: SPQRTree):
    changed = True
    while changed:
        changed = False
        nodes_to_remove = []
        for node in tree.nodes:
            if node.node_type == NodeType.S and len(node.children) == 1:
                child = node.children[0]
                if child.node_type == NodeType.S:
                    child.edges = node.edges + child.edges
                    child.virtual_edges = [
                        e for e in child.virtual_edges
                        if e not in node.virtual_edges or e in child.edges
                    ]
                    if node.parent:
                        child.parent = node.parent
                        node.parent.children = [
                            c if c != node else child for c in node.parent.children
                        ]
                    nodes_to_remove.append(node)
                    changed = True

            if (node.node_type == NodeType.S
                    and len(node.edges) == 0
                    and len(node.virtual_edges) >= 2
                    and len(node.children) >= 2):
                all_children_s = all(
                    c.node_type == NodeType.S for c in node.children
                )
                if all_children_s:
                    merged_edges = []
                    merged_virtual = list(node.virtual_edges)
                    for child in node.children:
                        merged_edges.extend(child.edges)
                        for ve in child.virtual_edges:
                            if ve not in merged_virtual and ve not in merged_edges:
                                merged_virtual.append(ve)
                    node.edges = merged_edges
                    node.virtual_edges = merged_virtual
                    node.children = []
                    changed = True

    for node in nodes_to_remove:
        if node in tree.nodes:
            tree.nodes.remove(node)


def print_spqr_tree(tree: SPQRTree):
    print(f"SPQRTree with {len(tree.nodes)} nodes:")
    for node in tree.nodes:
        print(f"  [{node.id}] {node.node_type.value}: "
              f"edges={node.edges}, virtual={node.virtual_edges}")
    if tree.root:
        print(f"  Root: node {tree.root.id}")


def _test():
    print("=" * 60)
    print("Example 1: Triangle (K3) - triconnected")
    print("=" * 60)
    G1 = [(1, 2), (2, 3), (3, 1)]
    tree1 = spqr_decompose(G1)
    print_spqr_tree(tree1)
    print(f"Is triconnected: {is_triconnected(G1)}")
    print()

    print("=" * 60)
    print("Example 2: K4 (complete graph on 4 vertices)")
    print("=" * 60)
    G2 = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
    tree2 = spqr_decompose(G2)
    print_spqr_tree(tree2)
    print(f"Is triconnected: {is_triconnected(G2)}")
    print()

    print("=" * 60)
    print("Example 3: Diamond graph (separation pair {2,3})")
    print("=" * 60)
    G3 = [(1, 2), (1, 3), (2, 3), (2, 4), (3, 4)]
    g3 = Graph()
    g3.add_edges_from(G3)
    print(f"Biconnected: {is_biconnected(g3)}")
    print(f"Separation pairs: {find_separation_pairs(g3)}")
    tree3 = spqr_decompose(G3)
    print_spqr_tree(tree3)
    print()

    print("=" * 60)
    print("Example 4: Cycle (C5)")
    print("=" * 60)
    G4 = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)]
    g4 = Graph()
    g4.add_edges_from(G4)
    print(f"Biconnected: {is_biconnected(g4)}")
    print(f"Separation pairs: {find_separation_pairs(g4)}")
    tree4 = spqr_decompose(G4)
    print_spqr_tree(tree4)
    print()

    print("=" * 60)
    print("Example 5: Path (NOT biconnected)")
    print("=" * 60)
    G5 = [(1, 2), (2, 3)]
    try:
        tree5 = spqr_decompose(G5)
        print_spqr_tree(tree5)
    except ValueError as e:
        print(f"Error: {e}")
    print()

    print("=" * 60)
    print("Example 6: K5 (complete graph on 5 vertices)")
    print("=" * 60)
    G6 = []
    for i in range(1, 6):
        for j in range(i + 1, 6):
            G6.append((i, j))
    tree6 = spqr_decompose(G6)
    print_spqr_tree(tree6)
    print(f"Is triconnected: {is_triconnected(G6)}")
    print()

    print("=" * 60)
    print("Example 7: Two triangles sharing an edge")
    print("=" * 60)
    G7 = [(1, 2), (2, 3), (3, 1), (1, 3), (3, 4), (4, 1)]
    g7 = Graph()
    g7.add_edges_from(G7)
    print(f"Biconnected: {is_biconnected(g7)}")
    print(f"Separation pairs: {find_separation_pairs(g7)}")
    try:
        tree7 = spqr_decompose(G7)
        print_spqr_tree(tree7)
    except ValueError as e:
        print(f"Error: {e}")
    print()

    print("=" * 60)
    print("Example 8: Three triangles sharing edges (chain)")
    print("=" * 60)
    G8 = [(1, 2), (2, 3), (3, 1), (2, 4), (4, 5), (5, 2), (4, 6), (6, 7), (7, 4)]
    g8 = Graph()
    g8.add_edges_from(G8)
    print(f"Biconnected: {is_biconnected(g8)}")
    print(f"Separation pairs: {find_separation_pairs(g8)}")
    try:
        tree8 = spqr_decompose(G8)
        print_spqr_tree(tree8)
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    _test()

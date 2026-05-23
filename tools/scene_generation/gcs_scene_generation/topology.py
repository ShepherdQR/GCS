"""Deterministic graph topology helpers for scene generation."""

from __future__ import annotations


def sort_key(value):
    return (type(value).__name__, str(value))


def canonical_edge(u, v):
    return tuple(sorted((u, v), key=sort_key))


def unique_edges(edges) -> list[list]:
    seen = set()
    result = []
    for edge in edges:
        if len(edge) != 2:
            continue
        u, v = edge
        if u == v:
            continue
        key = canonical_edge(u, v)
        if key in seen:
            continue
        seen.add(key)
        result.append([key[0], key[1]])
    return sorted(result, key=lambda e: (sort_key(e[0]), sort_key(e[1])))


def build_adjacency(vertices, edges) -> dict:
    adj = {v: set() for v in vertices}
    for u, v in edges:
        if u not in adj:
            adj[u] = set()
        if v not in adj:
            adj[v] = set()
        adj[u].add(v)
        adj[v].add(u)
    return adj


def connected_components(vertices, edges) -> list[list]:
    adj = build_adjacency(vertices, edges)
    visited = set()
    components = []
    for start in sorted(vertices, key=sort_key):
        if start in visited:
            continue
        stack = [start]
        component = []
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            component.append(node)
            for neighbor in sorted(adj[node], key=sort_key, reverse=True):
                if neighbor not in visited:
                    stack.append(neighbor)
        components.append(sorted(component, key=sort_key))
    return components


def tarjan_articulation_bcc(vertices, edges) -> tuple[list, list[dict], int]:
    adj = build_adjacency(vertices, edges)
    disc = {}
    low = {}
    parent = {}
    timer = 0
    edge_stack = []
    bcc_list = []
    articulation_points = set()

    def pop_bcc(stop_edge):
        bcc_edges = []
        while edge_stack:
            edge = edge_stack.pop()
            bcc_edges.append(edge)
            if edge == stop_edge:
                break
        bcc_vertices = set()
        for a, b in bcc_edges:
            bcc_vertices.add(a)
            bcc_vertices.add(b)
        bcc_list.append(
            {
                "id": len(bcc_list),
                "vertices": sorted(bcc_vertices, key=sort_key),
                "edges": [list(e) for e in sorted(bcc_edges, key=lambda x: (sort_key(x[0]), sort_key(x[1])))],
            }
        )

    def dfs(u):
        nonlocal timer
        children = 0
        disc[u] = low[u] = timer
        timer += 1

        for v in sorted(adj[u], key=sort_key):
            edge = canonical_edge(u, v)
            if v not in disc:
                children += 1
                parent[v] = u
                edge_stack.append(edge)
                dfs(v)
                low[u] = min(low[u], low[v])

                is_root_cut = parent.get(u) is None and children > 1
                is_child_cut = parent.get(u) is not None and low[v] >= disc[u]
                if is_root_cut or is_child_cut:
                    articulation_points.add(u)
                if low[v] >= disc[u]:
                    pop_bcc(edge)
            elif v != parent.get(u) and disc[v] < disc[u]:
                low[u] = min(low[u], disc[v])
                edge_stack.append(edge)

    for vertex in sorted(vertices, key=sort_key):
        if vertex in disc:
            continue
        parent[vertex] = None
        dfs(vertex)
        if edge_stack:
            pop_bcc(edge_stack[0])

    return sorted(articulation_points, key=sort_key), bcc_list, len(connected_components(vertices, edges))


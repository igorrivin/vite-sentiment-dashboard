import networkx as nx
from collections import deque

TARGET = 46084710702216534918083727566658949233732143042229436416

# Parse edge list
G = nx.Graph()
with open('/Users/igorrivin/Downloads/tw3_indsets_graph_edgelist.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        u, v = map(int, line.split())
        G.add_edge(u, v)

print(f"Vertices: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")

# Decompose into connected components
components = sorted(nx.connected_components(G), key=len)
print(f"Connected components: {len(components)}")


def count_is_via_td(graph):
    """Count independent sets using tree decomposition DP."""
    if graph.number_of_nodes() == 0:
        return 1
    if graph.number_of_nodes() == 1:
        return 2
    if graph.number_of_edges() == 0:
        return 2 ** graph.number_of_nodes()

    tw, td = nx.approximation.treewidth_min_degree(graph)

    # Root the tree decomposition
    td_nodes = list(td.nodes())
    root = td_nodes[0]

    parent = {root: None}
    order = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in td.neighbors(node):
            if neighbor not in parent:
                parent[neighbor] = node
                queue.append(neighbor)

    children = {node: [] for node in td_nodes}
    for node in td_nodes:
        if parent[node] is not None:
            children[parent[node]].append(node)

    dp = {}
    for node in reversed(order):
        bag = frozenset(node)
        bag_list = sorted(bag)
        bag_edges = [(u, v) for u in bag for v in bag if u < v and graph.has_edge(u, v)]

        independent_subsets = []
        for mask in range(1 << len(bag_list)):
            subset = frozenset(bag_list[i] for i in range(len(bag_list)) if (mask >> i) & 1)
            ok = True
            for (u, v) in bag_edges:
                if u in subset and v in subset:
                    ok = False
                    break
            if ok:
                independent_subsets.append(subset)

        dp[node] = {}
        for subset in independent_subsets:
            count = 1
            for child in children[node]:
                child_bag = frozenset(child)
                shared = bag & child_bag
                child_sum = 0
                for child_subset, child_count in dp[child].items():
                    if (child_subset & shared) == (subset & shared):
                        child_sum += child_count
                count *= child_sum
            dp[node][subset] = count

    return sum(dp[root].values())


def count_is_brute(graph):
    """Brute force IS count."""
    nodes = sorted(graph.nodes())
    n = len(nodes)
    node_idx = {v: j for j, v in enumerate(nodes)}
    edges_local = [(node_idx[u], node_idx[v]) for u, v in graph.edges()]
    count = 0
    for mask in range(1 << n):
        ok = True
        for (a, b) in edges_local:
            if (mask >> a) & 1 and (mask >> b) & 1:
                ok = False
                break
        if ok:
            count += 1
    return count


total_is = 1
for i, comp in enumerate(components):
    subG = G.subgraph(comp)
    n = len(comp)

    if n <= 25:
        count = count_is_brute(subG)
        method = "brute"
    else:
        count = count_is_via_td(subG)
        method = "TD-DP"

    print(f"  Component {i+1}: {n} vertices, {subG.number_of_edges()} edges, IS = {count} [{method}]")
    total_is *= count

print(f"\nTotal IS count (product): {total_is}")
print(f"Target:                   {TARGET}")
print(f"Match: {total_is == TARGET}")

# Check treewidth per component and overall
max_tw = 0
for i, comp in enumerate(components):
    subG = G.subgraph(comp)
    tw, _ = nx.approximation.treewidth_min_degree(subG)
    tw2, _ = nx.approximation.treewidth_min_fill_in(subG)
    tw_best = min(tw, tw2)
    max_tw = max(max_tw, tw_best)
    if tw_best > 3:
        print(f"  WARNING: Component {i+1} has approx treewidth {tw_best} > 3!")

print(f"\nMax approx treewidth across components: {max_tw}")
print(f"Treewidth <= 3: {max_tw <= 3}")

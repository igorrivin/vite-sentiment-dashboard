import networkx as nx
from itertools import combinations

# Parse edge list
G = nx.Graph()
G.add_nodes_from(range(1, 168))  # vertices 1..167

with open('/Users/igorrivin/Downloads/graph_edgelist.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        u, v = map(int, line.split())
        G.add_edge(u, v)

print(f"Vertices: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")

# Count independent sets via brute force on each component
# (disjoint union: multiply counts)
components = list(nx.connected_components(G))
print(f"Connected components: {len(components)}")

total_is = 1
for i, comp in enumerate(sorted(components, key=len)):
    subG = G.subgraph(comp)
    n = len(comp)
    nodes = sorted(comp)
    node_idx = {v: i for i, v in enumerate(nodes)}
    
    # Brute force IS count for this component
    edges_local = [(node_idx[u], node_idx[v]) for u, v in subG.edges()]
    count = 0
    for mask in range(1 << n):
        ok = True
        for (a, b) in edges_local:
            if (mask >> a) & 1 and (mask >> b) & 1:
                ok = False
                break
        if ok:
            count += 1
    
    print(f"  Component {i+1}: {n} vertices, {subG.number_of_edges()} edges, IS count = {count}")
    total_is *= count

print(f"\nTotal IS count (product): {total_is}")
print(f"Target:                   25257737849327555969307755604344832000")
print(f"Match: {total_is == 25257737849327555969307755604344832000}")

# Check treewidth
tw, _ = nx.approximation.treewidth_min_degree(G)
print(f"\nApprox treewidth (min degree): {tw}")

"""
Graph generators that produce graphs with known tree decompositions.

All generators return (nx.Graph, TreeDecomposition).

Generators:
  - random_k_tree: exact treewidth k via incremental k-clique construction
  - random_partial_k_tree: treewidth ≤ k (k-tree with random edge deletions)
  - overlay_trees: union of two random trees with decomposition from T1
  - grid_graph: rows x cols grid (treewidth = min(rows, cols))
  - series_parallel: treewidth ≤ 2
  - outerplanar: treewidth ≤ 2
"""

import random
from itertools import combinations

import networkx as nx

from tree_decomposition import TreeDecomposition
from generators import prufer_tree


def random_k_tree(n: int, k: int, rng: random.Random) -> tuple[nx.Graph, TreeDecomposition]:
    """
    Generate a random k-tree on n vertices.
    Treewidth = exactly k (for n > k).

    Algorithm: Start with K_{k+1}. For each new vertex, pick a random
    existing k-clique and connect the new vertex to all k vertices in it.
    The decomposition is recorded during construction.
    """
    if n <= k:
        # Complete graph on n vertices
        G = nx.complete_graph(n)
        tree = nx.Graph()
        tree.add_node(0)
        bags = {0: frozenset(range(n))}
        return G, TreeDecomposition(graph=G, tree=tree, bags=bags)

    G = nx.complete_graph(k + 1)

    # Initial bag: the complete graph K_{k+1}
    bags = {0: frozenset(range(k + 1))}
    tree = nx.Graph()
    tree.add_node(0)

    # Track all k-cliques and which bag they belong to
    # A k-clique is a frozenset of k vertices
    clique_to_bag = {}
    initial_verts = list(range(k + 1))
    for combo in combinations(initial_verts, k):
        clique_to_bag[frozenset(combo)] = 0

    next_bag_id = 1

    for v in range(k + 1, n):
        # Pick a random existing k-clique
        clique = rng.choice(list(clique_to_bag.keys()))
        parent_bag = clique_to_bag[clique]

        # Connect new vertex to all vertices in the clique
        G.add_node(v)
        for u in clique:
            G.add_edge(v, u)

        # New bag = clique ∪ {v}
        new_bag = clique | {v}
        bags[next_bag_id] = frozenset(new_bag)
        tree.add_node(next_bag_id)
        tree.add_edge(parent_bag, next_bag_id)

        # Register new k-cliques formed with v
        clique_verts = sorted(new_bag)
        for combo in combinations(clique_verts, k):
            fs = frozenset(combo)
            if fs not in clique_to_bag:
                clique_to_bag[fs] = next_bag_id

        next_bag_id += 1

    return G, TreeDecomposition(graph=G, tree=tree, bags=bags)


def random_partial_k_tree(n: int, k: int, edge_keep_prob: float,
                          rng: random.Random) -> tuple[nx.Graph, TreeDecomposition]:
    """
    Generate a random partial k-tree: start with a k-tree, then randomly
    delete edges with probability (1 - edge_keep_prob).
    Treewidth ≤ k. The original decomposition remains valid.
    """
    G_full, td = random_k_tree(n, k, rng)

    # Remove edges randomly (but keep the graph connected by not removing bridges)
    G = G_full.copy()
    bridges = set(nx.bridges(G))

    edges = list(G.edges)
    rng.shuffle(edges)
    for u, v in edges:
        if rng.random() > edge_keep_prob and (u, v) not in bridges and (v, u) not in bridges:
            G.remove_edge(u, v)
            # Recompute bridges after removal
            bridges = set(nx.bridges(G))

    # The original decomposition is still valid (superset bags)
    return G, TreeDecomposition(graph=G, tree=td.tree, bags=td.bags)


def overlay_trees(n: int, rng: random.Random,
                  tree_gen=None) -> tuple[nx.Graph, TreeDecomposition]:
    """
    Generate G = T1 ∪ T2 where T1, T2 are random trees on the same n vertices.
    Build decomposition from T1 as backbone:

    1. Root T1, create one bag per vertex: B(v) = {v, parent(v)} for non-root,
       B(root) = {root}
    2. Decomposition tree mirrors T1: edge (v, parent(v)) in T1 →
       edge (bag(v), bag(parent(v))) in decomp tree
    3. For each T2-edge (a, b), find the path from a to b in T1 and add
       both a and b to every bag B(v) for v on the path
    4. Running intersection is maintained because T2-edge augmentations
       add vertices along connected paths in the decomp tree
    """
    if tree_gen is None:
        tree_gen = prufer_tree

    if n <= 2:
        G = nx.complete_graph(n)
        tree = nx.Graph()
        tree.add_node(0)
        bags = {0: frozenset(range(n))}
        return G, TreeDecomposition(graph=G, tree=tree, bags=bags)

    T1 = tree_gen(n, rng)
    T2 = tree_gen(n, rng)

    # Build the union graph
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(T1.edges)
    G.add_edges_from(T2.edges)

    # Root T1
    root = 0
    rooted_T1 = nx.bfs_tree(T1, root)

    # Build parent map
    parent = {}
    for v in rooted_T1.nodes:
        preds = list(rooted_T1.predecessors(v))
        if preds:
            parent[v] = preds[0]

    # One bag per vertex, decomp tree mirrors T1
    # Bag IDs = vertex IDs for simplicity
    bags = {}
    decomp_tree = nx.Graph()

    for v in T1.nodes:
        decomp_tree.add_node(v)
        if v == root:
            bags[v] = {v}
        else:
            bags[v] = {v, parent[v]}

    for v in T1.nodes:
        if v != root:
            decomp_tree.add_edge(v, parent[v])

    # Augment bags for T2 edges
    for a, b in T2.edges:
        if T1.has_edge(a, b):
            continue  # already covered by bags

        # Find path from a to b in T1
        path = nx.shortest_path(T1, a, b)

        # Add both a and b to every bag on this path
        for v in path:
            bags[v].add(a)
            bags[v].add(b)

    # Convert bag sets to frozensets
    bags = {bid: frozenset(b) for bid, b in bags.items()}

    return G, TreeDecomposition(graph=G, tree=decomp_tree, bags=bags)


def grid_graph(rows: int, cols: int) -> tuple[nx.Graph, TreeDecomposition]:
    """
    Generate a rows x cols grid graph with a known tree decomposition.
    Treewidth = min(rows, cols).

    Uses column-based bags: each bag contains two adjacent columns.
    """
    G = nx.grid_2d_graph(rows, cols)

    # Relabel to integers
    node_map = {}
    for i in range(rows):
        for j in range(cols):
            node_map[(i, j)] = i * cols + j
    G = nx.relabel_nodes(G, node_map)

    if rows <= cols:
        # Decompose along columns
        bags = {}
        decomp_tree = nx.Graph()
        for j in range(cols - 1):
            bag_verts = set()
            for i in range(rows):
                bag_verts.add(i * cols + j)
                bag_verts.add(i * cols + j + 1)
            bags[j] = frozenset(bag_verts)
            decomp_tree.add_node(j)
            if j > 0:
                decomp_tree.add_edge(j - 1, j)

        # Handle single column
        if cols == 1:
            bags[0] = frozenset(i * cols for i in range(rows))
            decomp_tree.add_node(0)
    else:
        # Decompose along rows
        bags = {}
        decomp_tree = nx.Graph()
        for i in range(rows - 1):
            bag_verts = set()
            for j in range(cols):
                bag_verts.add(i * cols + j)
                bag_verts.add((i + 1) * cols + j)
            bags[i] = frozenset(bag_verts)
            decomp_tree.add_node(i)
            if i > 0:
                decomp_tree.add_edge(i - 1, i)

        if rows == 1:
            bags[0] = frozenset(range(cols))
            decomp_tree.add_node(0)

    return G, TreeDecomposition(graph=G, tree=decomp_tree, bags=bags)


def series_parallel(n: int, rng: random.Random) -> tuple[nx.Graph, TreeDecomposition]:
    """
    Generate a random series-parallel graph on n vertices.
    Treewidth ≤ 2.

    Built as a path with random distance-2 chords forming triangles.
    Each consecutive triple (i, i+1, i+2) that has both edges and the chord
    forms a bag of size 3. The decomposition is a path of bags.
    """
    if n <= 2:
        G = nx.Graph()
        G.add_nodes_from(range(n))
        if n == 2:
            G.add_edge(0, 1)
        tree = nx.Graph()
        tree.add_node(0)
        bags = {0: frozenset(range(n))}
        return G, TreeDecomposition(graph=G, tree=tree, bags=bags)

    G = nx.Graph()
    G.add_nodes_from(range(n))

    # Start with a path
    for i in range(n - 1):
        G.add_edge(i, i + 1)

    # Add random distance-2 chords only (keeps treewidth ≤ 2)
    chords = set()
    for _ in range(n):
        i = rng.randint(0, n - 3)
        if not G.has_edge(i, i + 2):
            G.add_edge(i, i + 2)
            chords.add(i)

    # Build decomposition: one bag per edge (i, i+1), augmented if chord exists
    bags = {}
    decomp_tree = nx.Graph()

    for i in range(n - 1):
        bag = {i, i + 1}
        # If chord (i, i+2) exists, add i+2 to this bag
        if i in chords:
            bag.add(i + 2)
        # If chord (i-1, i+1) exists, add i-1 to this bag
        if (i - 1) in chords:
            bag.add(i - 1)
        bags[i] = frozenset(bag)
        decomp_tree.add_node(i)
        if i > 0:
            decomp_tree.add_edge(i - 1, i)

    return G, TreeDecomposition(graph=G, tree=decomp_tree, bags=bags)


def outerplanar(n: int, rng: random.Random) -> tuple[nx.Graph, TreeDecomposition]:
    """
    Generate a random outerplanar graph (subgraph of a triangulated cycle).
    Treewidth ≤ 2.

    Algorithm: Create a fan triangulation of a cycle (all diagonals from vertex 0),
    then randomly remove some diagonals. Decomposition is a path of triangle bags.
    """
    if n <= 2:
        G = nx.Graph()
        G.add_nodes_from(range(n))
        if n == 2:
            G.add_edge(0, 1)
        tree = nx.Graph()
        tree.add_node(0)
        bags = {0: frozenset(range(n))}
        return G, TreeDecomposition(graph=G, tree=tree, bags=bags)

    G = nx.Graph()
    G.add_nodes_from(range(n))

    # Create cycle edges
    for i in range(n):
        G.add_edge(i, (i + 1) % n)

    # Fan triangulation from vertex 0: add diagonals (0, i) for i in 2..n-2
    for i in range(2, n - 1):
        G.add_edge(0, i)

    # Randomly remove some diagonals (not cycle edges) to make it non-maximal
    diagonals = [(0, i) for i in range(2, n - 1)]
    rng.shuffle(diagonals)
    for u, v in diagonals:
        if rng.random() < 0.3:
            G.remove_edge(u, v)

    # Decomposition: path of triangle bags {0, i, i+1} for i in 1..n-2
    # This is valid even after diagonal removal (bags are supersets)
    bags = {}
    decomp_tree = nx.Graph()

    for i in range(1, n - 1):
        bid = i - 1
        bags[bid] = frozenset({0, i, i + 1})
        decomp_tree.add_node(bid)
        if bid > 0:
            decomp_tree.add_edge(bid - 1, bid)

    return G, TreeDecomposition(graph=G, tree=decomp_tree, bags=bags)

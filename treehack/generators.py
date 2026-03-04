"""
Tree generators: named families and random models.

Named families:
  star, path, caterpillar, double_star, spider, balanced_binary_tree, random_tree

Random models:
  prufer_tree, galton_watson_tree, preferential_attachment_tree, random_caterpillar
"""

import networkx as nx
import numpy as np
import random


# ---------------------------------------------------------------------------
# Named families
# ---------------------------------------------------------------------------

def star(n: int) -> nx.Graph:
    """K_{1, n-1}: one hub connected to n-1 leaves."""
    return nx.star_graph(n - 1)


def path(n: int) -> nx.Graph:
    return nx.path_graph(n)


def caterpillar(spine_len: int, leaves_per_node: int) -> nx.Graph:
    """
    A path of `spine_len` vertices, each with `leaves_per_node` pendant leaves.
    Total vertices = spine_len * (1 + leaves_per_node).
    """
    G = nx.Graph()
    node = 0
    prev = None
    for _ in range(spine_len):
        G.add_node(node)
        if prev is not None:
            G.add_edge(prev, node)
        spine_v = node
        node += 1
        for _ in range(leaves_per_node):
            G.add_node(node)
            G.add_edge(spine_v, node)
            node += 1
        prev = spine_v
    return G


def double_star(a: int, b: int) -> nx.Graph:
    """Two hubs connected to each other; hub 0 has `a` leaves, hub 1 has `b` leaves."""
    G = nx.Graph()
    G.add_edge(0, 1)
    node = 2
    for _ in range(a):
        G.add_edge(0, node); node += 1
    for _ in range(b):
        G.add_edge(1, node); node += 1
    return G


def spider(arms: int, arm_len: int) -> nx.Graph:
    """Central hub connected to `arms` paths of length `arm_len`."""
    G = nx.Graph()
    G.add_node(0)
    node = 1
    for _ in range(arms):
        prev = 0
        for _ in range(arm_len):
            G.add_node(node)
            G.add_edge(prev, node)
            prev = node
            node += 1
    return G


def balanced_binary_tree(depth: int) -> nx.Graph:
    return nx.balanced_tree(2, depth)


def random_tree(n: int, seed=None) -> nx.Graph:
    return nx.random_labeled_tree(n, seed=seed)


# ---------------------------------------------------------------------------
# Random models
# ---------------------------------------------------------------------------

def prufer_tree(n: int, rng: random.Random) -> nx.Graph:
    """Uniform random labeled tree (all n^{n-2} trees equally likely)."""
    seq = [rng.randint(0, n - 1) for _ in range(n - 2)]
    return nx.from_prufer_sequence(seq)


def galton_watson_tree(offspring_dist, target_n: int, rng: random.Random) -> nx.Graph:
    """
    GW tree conditioned to have roughly target_n vertices.
    Restarts until size is within [target_n//2, 2*target_n].
    """
    for _ in range(300):
        G = nx.Graph(); G.add_node(0)
        frontier = [0]; node = 1
        while frontier and node < target_n * 3:
            parent = frontier.pop(0)
            for _ in range(offspring_dist(rng)):
                G.add_node(node); G.add_edge(parent, node)
                frontier.append(node); node += 1
        if target_n // 2 <= len(G) <= target_n * 2:
            return G
    return prufer_tree(target_n, rng)  # fallback


def preferential_attachment_tree(n: int, rng: random.Random) -> nx.Graph:
    """
    Linear preferential attachment: each new node attaches to an existing
    node with probability proportional to degree.
    """
    G = nx.Graph(); G.add_node(0)
    urn = [0]
    for v in range(1, n):
        target = rng.choice(urn)
        G.add_edge(v, target)
        urn.extend([v, target])
    return G


def random_caterpillar(n: int, rng: random.Random) -> nx.Graph:
    """Random caterpillar with uniformly random spine length and leaf distribution."""
    spine = rng.randint(2, max(2, n // 3))
    G = nx.path_graph(spine)
    node = spine
    counts = [0] * spine
    for _ in range(n - spine):
        counts[rng.randint(0, spine - 1)] += 1
    for i, c in enumerate(counts):
        for _ in range(c):
            G.add_edge(i, node); node += 1
    return G

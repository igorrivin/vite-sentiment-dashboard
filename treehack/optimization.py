"""
Optimization over the space of trees and bounded-treewidth graphs:
  - hill_climb: maximize IS count via leaf-swap mutations on trees
  - mcmc_inverse: sample trees whose IS count is near a target
  - hill_climb_tw: maximize IS count over partial k-trees
  - mcmc_inverse_tw: MCMC targeting IS count on partial k-trees
"""

import random
from math import exp

import networkx as nx

from counting import count_independent_sets, log_count_independent_sets
from generators import prufer_tree
from tw_counting import count_independent_sets_tw, log_count_independent_sets_tw
from tw_generators import random_k_tree, random_partial_k_tree


def mutate(T, rng: random.Random):
    """
    Pick a random leaf, detach it, reattach to a random other vertex.
    Returns a new tree (T is not modified).
    """
    T2 = T.copy()
    leaves = [v for v in T2.nodes if T2.degree(v) == 1]
    if not leaves:
        return T2
    leaf = rng.choice(leaves)
    parent = list(T2.neighbors(leaf))[0]
    candidates = [v for v in T2.nodes if v != leaf and v != parent]
    if not candidates:
        return T2
    new_parent = rng.choice(candidates)
    T2.remove_edge(leaf, parent)
    T2.add_edge(leaf, new_parent)
    return T2


def hill_climb(n: int, steps: int = 2000, restarts: int = 5, seed: int = 42):
    """
    Random-restart hill climbing: maximize count_independent_sets over n-vertex trees.
    Returns (best_tree, best_count).
    """
    rng = random.Random(seed)
    best_T, best_count = None, 0

    for _ in range(restarts):
        T = prufer_tree(n, rng)
        score = count_independent_sets(T)
        for _ in range(steps):
            T2 = mutate(T, rng)
            s2 = count_independent_sets(T2)
            if s2 >= score:
                T, score = T2, s2
        if score > best_count:
            best_T, best_count = T, score

    return best_T, best_count


def mcmc_inverse(n: int, log_target: float,
                 steps: int = 25_000, temperature: float = 0.5,
                 seed: int = 42):
    """
    Metropolis on the space of n-vertex labeled trees.
    Proposal: detach a random leaf, reattach to a random non-neighbor.
    Energy: (log_IS(T) - log_target)^2

    Returns (trace, final_tree) where trace is a list of
    (log_IS, degree_sequence) snapshots every 100 steps.
    """
    rng = random.Random(seed)
    T = prufer_tree(n, rng)
    ls = log_count_independent_sets(T)
    energy = (ls - log_target) ** 2
    trace = []

    for step in range(steps):
        T2 = mutate(T, rng)
        ls2 = log_count_independent_sets(T2)
        e2 = (ls2 - log_target) ** 2
        if e2 < energy or rng.random() < exp(-(e2 - energy) / temperature):
            T, ls, energy = T2, ls2, e2

        if step % 100 == 0:
            trace.append((ls, sorted([d for _, d in T.degree()], reverse=True)))

    return trace, T


def _mutate_tw(G: nx.Graph, td, k: int, rng: random.Random):
    """
    Mutate a bounded-treewidth graph by removing a random non-bridge edge
    and adding a random new edge, keeping treewidth ≤ k.
    Returns (new_G, new_td) or (G, td) if mutation fails.
    """
    from tree_decomposition import TreeDecomposition

    edges = list(G.edges)
    if len(edges) < 2:
        return G, td

    bridges = set(nx.bridges(G))
    removable = [e for e in edges if e not in bridges and (e[1], e[0]) not in bridges]
    if not removable:
        return G, td

    # Remove a random non-bridge edge
    G2 = G.copy()
    rem_edge = rng.choice(removable)
    G2.remove_edge(*rem_edge)

    # Add a random new edge
    nodes = list(G2.nodes)
    for _ in range(20):
        u, v = rng.choice(nodes), rng.choice(nodes)
        if u != v and not G2.has_edge(u, v):
            G2.add_edge(u, v)
            # Check if the edge is covered by some existing bag
            covered = any(u in bag and v in bag for bag in td.bags.values())
            if covered:
                new_td = TreeDecomposition(graph=G2, tree=td.tree, bags=td.bags)
                return G2, new_td
            G2.remove_edge(u, v)

    return G, td


def hill_climb_tw(n: int, k: int, steps: int = 2000, restarts: int = 5,
                  seed: int = 42):
    """
    Random-restart hill climbing: maximize IS count over n-vertex
    partial k-trees.
    Returns (best_G, best_td, best_count).
    """
    rng = random.Random(seed)
    best_G, best_td, best_count = None, None, 0

    for _ in range(restarts):
        G, td = random_partial_k_tree(n, k, 0.7, rng)
        score = count_independent_sets_tw(td)
        for _ in range(steps):
            G2, td2 = _mutate_tw(G, td, k, rng)
            s2 = count_independent_sets_tw(td2)
            if s2 >= score:
                G, td, score = G2, td2, s2
        if score > best_count:
            best_G, best_td, best_count = G, td, score

    return best_G, best_td, best_count


def mcmc_inverse_tw(n: int, k: int, log_target: float,
                    steps: int = 25_000, temperature: float = 0.5,
                    seed: int = 42):
    """
    Metropolis on the space of n-vertex partial k-trees.
    Energy: (log_IS(G) - log_target)^2

    Returns (trace, final_G, final_td) where trace is a list of
    (log_IS, edge_count) snapshots every 100 steps.
    """
    rng = random.Random(seed)
    G, td = random_partial_k_tree(n, k, 0.7, rng)
    ls = log_count_independent_sets_tw(td)
    energy = (ls - log_target) ** 2
    trace = []

    for step in range(steps):
        G2, td2 = _mutate_tw(G, td, k, rng)
        ls2 = log_count_independent_sets_tw(td2)
        e2 = (ls2 - log_target) ** 2
        if e2 < energy or rng.random() < exp(-(e2 - energy) / temperature):
            G, td, ls, energy = G2, td2, ls2, e2

        if step % 100 == 0:
            trace.append((ls, G.number_of_edges()))

    return trace, G, td

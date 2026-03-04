"""
Correctness tests for bounded-treewidth IS counting.

Tests:
  1. Tree DP vs treewidth DP agree on all tree families
  2. Treewidth DP vs brute-force for small graphs
  3. Decomposition validation passes for all generators
  4. k-trees have treewidth exactly k
  5. Spot-checks for known values
"""

import random
from itertools import combinations

import networkx as nx

from counting import count_independent_sets
from tree_decomposition import TreeDecomposition
from tw_counting import count_independent_sets_tw, log_count_independent_sets_tw, count_independent_sets_general
from tw_generators import (random_k_tree, random_partial_k_tree, overlay_trees,
                           grid_graph, series_parallel, outerplanar)
from generators import star, path, caterpillar, spider, balanced_binary_tree


def brute_force_is_count(G: nx.Graph) -> int:
    """Count independent sets by brute force. O(2^n)."""
    nodes = list(G.nodes)
    n = len(nodes)
    count = 0
    for mask in range(1 << n):
        subset = [nodes[i] for i in range(n) if mask & (1 << i)]
        is_independent = True
        for i in range(len(subset)):
            for j in range(i + 1, len(subset)):
                if G.has_edge(subset[i], subset[j]):
                    is_independent = False
                    break
            if not is_independent:
                break
        if is_independent:
            count += 1
    return count


def test_tree_dp_vs_tw_dp():
    """Tree DP and treewidth DP should agree on trees."""
    print("Test: Tree DP vs Treewidth DP on trees...")

    trees = {
        "star(10)": star(10),
        "path(15)": path(15),
        "caterpillar(4,2)": caterpillar(4, 2),
        "spider(3,3)": spider(3, 3),
        "binary_tree(3)": balanced_binary_tree(3),
    }

    all_pass = True
    for name, T in trees.items():
        tree_count = count_independent_sets(T)
        td = TreeDecomposition.trivial_from_tree(T)
        td.validate()
        tw_count = count_independent_sets_tw(td)
        match = tree_count == tw_count
        status = "OK" if match else "FAIL"
        print(f"  {name:30s} tree_dp={tree_count:10d}  tw_dp={tw_count:10d}  [{status}]")
        if not match:
            all_pass = False

    assert all_pass, "Tree DP and Treewidth DP disagree!"
    print("  PASSED\n")


def test_tw_dp_vs_brute_force():
    """Treewidth DP should agree with brute force on small graphs."""
    print("Test: Treewidth DP vs Brute Force (small graphs)...")

    rng = random.Random(42)
    all_pass = True

    test_cases = [
        ("k-tree(8,2)", lambda: random_k_tree(8, 2, rng)),
        ("k-tree(7,3)", lambda: random_k_tree(7, 3, rng)),
        ("partial-k-tree(8,2)", lambda: random_partial_k_tree(8, 2, 0.7, rng)),
        ("overlay(8)", lambda: overlay_trees(8, rng)),
        ("grid(3,3)", lambda: grid_graph(3, 3)),
        ("grid(2,4)", lambda: grid_graph(2, 4)),
        ("series_parallel(8)", lambda: series_parallel(8, rng)),
        ("outerplanar(8)", lambda: outerplanar(8, rng)),
    ]

    for name, gen_fn in test_cases:
        G, td = gen_fn()
        td.validate()
        tw_count = count_independent_sets_tw(td)
        bf_count = brute_force_is_count(G)
        match = tw_count == bf_count
        status = "OK" if match else "FAIL"
        print(f"  {name:30s} tw_dp={tw_count:8d}  brute={bf_count:8d}  [w={td.width}] [{status}]")
        if not match:
            all_pass = False

    assert all_pass, "Treewidth DP and brute force disagree!"
    print("  PASSED\n")


def test_decomposition_validation():
    """All generators produce valid decompositions."""
    print("Test: Decomposition validation...")

    rng = random.Random(123)
    generators = [
        ("k-tree(20,2)", lambda: random_k_tree(20, 2, rng)),
        ("k-tree(15,3)", lambda: random_k_tree(15, 3, rng)),
        ("partial-k-tree(20,2)", lambda: random_partial_k_tree(20, 2, 0.7, rng)),
        ("overlay(20)", lambda: overlay_trees(20, rng)),
        ("grid(4,5)", lambda: grid_graph(4, 5)),
        ("grid(3,6)", lambda: grid_graph(3, 6)),
        ("series_parallel(15)", lambda: series_parallel(15, rng)),
        ("outerplanar(15)", lambda: outerplanar(15, rng)),
    ]

    for name, gen_fn in generators:
        G, td = gen_fn()
        try:
            td.validate()
            print(f"  {name:30s} n={len(G):3d} m={G.number_of_edges():3d} w={td.width} [OK]")
        except ValueError as e:
            print(f"  {name:30s} [FAIL: {e}]")
            raise

    print("  PASSED\n")


def test_k_tree_treewidth():
    """k-trees should have treewidth exactly k."""
    print("Test: k-tree treewidth...")

    rng = random.Random(77)
    for k in range(1, 5):
        n = max(k + 2, 12)
        G, td = random_k_tree(n, k, rng)
        assert td.width == k, f"Expected treewidth {k}, got {td.width}"
        print(f"  k={k}, n={n}: treewidth = {td.width} [OK]")

    print("  PASSED\n")


def test_log_space_consistency():
    """Log-space DP should be consistent with exact DP."""
    import math

    print("Test: Log-space consistency...")

    rng = random.Random(99)
    G, td = random_k_tree(10, 2, rng)
    exact = count_independent_sets_tw(td)
    log_val = log_count_independent_sets_tw(td)
    recovered = math.exp(log_val)

    rel_error = abs(recovered - exact) / exact
    print(f"  k-tree(10,2): exact={exact}, exp(log)={recovered:.1f}, rel_error={rel_error:.2e}")
    assert rel_error < 1e-6, f"Log-space too inaccurate: {rel_error}"

    print("  PASSED\n")


def test_general_entry_point():
    """count_independent_sets_general dispatches correctly."""
    print("Test: General entry point...")

    rng = random.Random(55)

    # Tree case
    T = path(10)
    tree_count = count_independent_sets(T)
    general_count = count_independent_sets_general(T)
    assert tree_count == general_count
    print(f"  path(10): {general_count} [OK, dispatched to tree DP]")

    # Graph case
    G, td = random_k_tree(10, 2, rng)
    tw_count = count_independent_sets_tw(td)
    general_count = count_independent_sets_general(G, td)
    assert tw_count == general_count
    print(f"  k-tree(10,2): {general_count} [OK, dispatched to treewidth DP]")

    # Error case
    try:
        count_independent_sets_general(G)
        assert False, "Should have raised ValueError"
    except ValueError:
        print(f"  non-tree without td: ValueError [OK]")

    print("  PASSED\n")


def test_grid_spot_check():
    """Spot-check IS count on small grids against brute force."""
    print("Test: Grid spot checks...")

    for rows, cols in [(2, 2), (2, 3), (3, 3), (3, 4)]:
        G, td = grid_graph(rows, cols)
        tw_count = count_independent_sets_tw(td)
        bf_count = brute_force_is_count(G)
        match = tw_count == bf_count
        status = "OK" if match else "FAIL"
        print(f"  grid({rows}x{cols}): tw_dp={tw_count:6d}  brute={bf_count:6d} [{status}]")
        assert match

    print("  PASSED\n")


if __name__ == "__main__":
    test_tree_dp_vs_tw_dp()
    test_tw_dp_vs_brute_force()
    test_decomposition_validation()
    test_k_tree_treewidth()
    test_log_space_consistency()
    test_general_entry_point()
    test_grid_spot_check()
    print("=" * 50)
    print("ALL TESTS PASSED")

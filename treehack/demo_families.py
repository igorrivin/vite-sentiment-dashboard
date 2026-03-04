"""Demo: IS counts for named tree families, bounded-treewidth graphs, + hill-climbing search."""

import random

from counting import count_independent_sets
from generators import (star, path, caterpillar, double_star, spider,
                         balanced_binary_tree, random_tree)
from optimization import hill_climb, hill_climb_tw
from tw_counting import count_independent_sets_tw
from tw_generators import (random_k_tree, random_partial_k_tree, overlay_trees,
                           grid_graph, series_parallel, outerplanar)

if __name__ == "__main__":
    n = 20

    print(f"=== Independent set counts for {n}-vertex trees ===\n")

    trees = {
        "Star":                   star(n),
        "Path":                   path(n),
        "Double star (9+9 arms)": double_star(9, 9),
        "Caterpillar (5 spine, 3 leaves)": caterpillar(5, 3),
        "Spider (4 arms, len 4)": spider(4, 4),
        "Balanced binary (depth 3)": balanced_binary_tree(3),
        "Random tree":            random_tree(n, seed=7),
    }

    for name, T in trees.items():
        nv = T.number_of_nodes()
        count = count_independent_sets(T)
        print(f"  {name:35s}  n={nv:3d}  IS count = {count}")

    print(f"\n  Star formula check: 2^(n-1)+1 = {2**(n-1)+1}")

    # --- Bounded-treewidth graphs ---
    rng = random.Random(42)

    print(f"\n=== IS counts for bounded-treewidth graphs ===\n")

    tw_graphs = {}

    G, td = random_k_tree(n, 2, rng)
    tw_graphs["2-tree (tw=2)"] = (G, td)

    G, td = random_k_tree(n, 3, rng)
    tw_graphs["3-tree (tw=3)"] = (G, td)

    G, td = random_partial_k_tree(n, 2, 0.7, rng)
    tw_graphs["Partial 2-tree (tw≤2)"] = (G, td)

    G, td = overlay_trees(n, rng)
    tw_graphs["Overlay of 2 trees"] = (G, td)

    G, td = grid_graph(4, 5)
    tw_graphs["Grid 4x5 (tw=4)"] = (G, td)

    G, td = series_parallel(n, rng)
    tw_graphs["Series-parallel (tw≤2)"] = (G, td)

    G, td = outerplanar(n, rng)
    tw_graphs["Outerplanar (tw≤2)"] = (G, td)

    for name, (G, td) in tw_graphs.items():
        nv = G.number_of_nodes()
        ne = G.number_of_edges()
        count = count_independent_sets_tw(td)
        print(f"  {name:35s}  n={nv:3d}  m={ne:3d}  tw≤{td.width}  IS count = {count}")

    # --- Hill climbing ---
    print(f"\n=== Hill-climbing search for max IS tree (n={n}) ===\n")
    best_T, best_count = hill_climb(n, steps=3000, restarts=8)
    print(f"  Best found: {best_count}  (star gives {2**(n-1)+1})")
    degree_seq = sorted([d for _, d in best_T.degree()], reverse=True)
    print(f"  Degree sequence: {degree_seq}")

    print(f"\n=== Hill-climbing over partial 2-trees (n={n}) ===\n")
    best_G, best_td, best_count = hill_climb_tw(n, k=2, steps=1000, restarts=3)
    print(f"  Best found: {best_count}  (n={best_G.number_of_nodes()}, "
          f"m={best_G.number_of_edges()}, tw≤{best_td.width})")

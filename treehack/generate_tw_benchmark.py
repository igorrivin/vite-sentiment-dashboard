#!/usr/bin/env python3
"""
Generate a benchmark dataset of bounded-treewidth graphs with IS counts.

For each graph:
  - Pick a random treewidth k in [1, 5]
  - Generate a random k-tree on n vertices
  - Count its independent sets via tree-decomposition DP
  - Save the edgelist and IS count

Output files:
  benchmark_edgelists.txt  — one graph per block, separated by blank lines
                             first line of each block: "# n=<n> k=<k>"
                             remaining lines: "u v" edges
  benchmark_is_counts.txt  — one IS count per line (matching graph order)
  benchmark_treewidths.txt — one treewidth per line (matching graph order)
"""

import random
import sys
from tw_generators import random_k_tree, random_partial_k_tree
from tw_counting import count_independent_sets_general

NUM_GRAPHS = 50
MIN_N = 100
MAX_N = 300
MIN_K = 1
MAX_K = 3
SEED = 42

EDGELIST_FILE = "benchmark_edgelists.txt"
COUNTS_FILE = "benchmark_is_counts.txt"
TREEWIDTHS_FILE = "benchmark_treewidths.txt"


def main():
    rng = random.Random(SEED)

    edgelist_lines = []
    counts = []
    treewidths = []

    for i in range(NUM_GRAPHS):
        k = rng.randint(MIN_K, MAX_K)
        n = rng.randint(max(k + 2, MIN_N), MAX_N)

        G, td = random_k_tree(n, k, rng)
        is_count = count_independent_sets_general(G, td)

        # Header for this graph
        edgelist_lines.append(f"# n={n} k={k}")
        for u, v in sorted(G.edges()):
            edgelist_lines.append(f"{u} {v}")
        edgelist_lines.append("")  # blank line separator

        counts.append(str(is_count))
        treewidths.append(str(k))

        print(f"Graph {i+1}/{NUM_GRAPHS}: n={n}, k={k}, "
              f"|E|={G.number_of_edges()}, IS={is_count}")

    with open(EDGELIST_FILE, "w") as f:
        f.write("\n".join(edgelist_lines))

    with open(COUNTS_FILE, "w") as f:
        f.write("\n".join(counts) + "\n")

    with open(TREEWIDTHS_FILE, "w") as f:
        f.write("\n".join(treewidths) + "\n")

    print(f"\nSaved {NUM_GRAPHS} graphs to {EDGELIST_FILE}")
    print(f"Saved {NUM_GRAPHS} IS counts to {COUNTS_FILE}")
    print(f"Saved {NUM_GRAPHS} treewidths to {TREEWIDTHS_FILE}")


if __name__ == "__main__":
    main()

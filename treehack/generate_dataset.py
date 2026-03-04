"""
Generate a dataset of random graphs in graph6 format with IS counts.

Supports both Galton-Watson trees and bounded-treewidth graphs.

Usage:
    python generate_dataset.py --num-trees 10 --target-n 200 --seed 42
    python generate_dataset.py --num-trees 10 --target-n 50 --treewidth 2
"""

import argparse
import os
import random

import networkx as nx
import numpy as np

from counting import count_independent_sets
from generators import galton_watson_tree
from tw_counting import count_independent_sets_tw
from tw_generators import random_partial_k_tree


def main():
    parser = argparse.ArgumentParser(
        description="Generate GW geometric trees and compute IS counts")
    parser.add_argument("--num-trees", type=int, default=10,
                        help="Number of trees to generate (default: 10)")
    parser.add_argument("--target-n", type=int, default=200,
                        help="Target number of vertices (default: 200)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    parser.add_argument("--output-dir", type=str, default=".",
                        help="Output directory (default: current directory)")
    parser.add_argument("--treewidth", type=int, default=0,
                        help="Treewidth bound k (default: 0 = trees)")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    np_rng = np.random.RandomState(args.seed)

    # Geometric(0.5) - 1 offspring distribution (mean = 1, critical GW)
    def geom_offspring(r):
        return np_rng.geometric(0.5) - 1

    os.makedirs(args.output_dir, exist_ok=True)
    g6_path = os.path.join(args.output_dir, "trees.g6")
    edgelist_path = os.path.join(args.output_dir, "trees_edgelist.txt")
    counts_path = os.path.join(args.output_dir, "is_counts.txt")

    graphs = []

    if args.treewidth > 0:
        print(f"Generating {args.num_trees} partial {args.treewidth}-trees "
              f"(target ~{args.target_n} vertices, seed={args.seed})")
        for i in range(args.num_trees):
            G, td = random_partial_k_tree(args.target_n, args.treewidth, 0.7, rng)
            n = G.number_of_nodes()
            is_count = count_independent_sets_tw(td)
            graphs.append((G, is_count))
            print(f"  Graph {i+1}: {n} vertices, {G.number_of_edges()} edges, "
                  f"tw≤{args.treewidth}, IS count = {is_count}")
    else:
        print(f"Generating {args.num_trees} GW geometric(0.5)-1 trees "
              f"(target ~{args.target_n} vertices, seed={args.seed})")
        for i in range(args.num_trees):
            T = galton_watson_tree(geom_offspring, args.target_n, rng)
            n = T.number_of_nodes()
            is_count = count_independent_sets(T)
            graphs.append((T, is_count))
            print(f"  Tree {i+1}: {n} vertices, IS count = {is_count}")

    with open(g6_path, "w") as f_g6, \
         open(edgelist_path, "w") as f_el, \
         open(counts_path, "w") as f_cnt:
        for idx, (T, is_count) in enumerate(graphs):
            T_relabeled = nx.convert_node_labels_to_integers(T)
            # graph6 (compact binary)
            g6 = nx.to_graph6_bytes(T_relabeled, header=False).decode().strip()
            f_g6.write(g6 + "\n")
            # human-readable edge list
            n = T_relabeled.number_of_nodes()
            edges = sorted(T_relabeled.edges())
            f_el.write(f"# Tree {idx+1}: {n} vertices, {len(edges)} edges\n")
            for u, v in edges:
                f_el.write(f"{u} {v}\n")
            f_el.write("\n")
            # IS count
            f_cnt.write(str(is_count) + "\n")

    print(f"\nWrote {g6_path}, {edgelist_path}, and {counts_path}")


if __name__ == "__main__":
    main()

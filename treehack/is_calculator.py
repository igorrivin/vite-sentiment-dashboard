#!/usr/bin/env python3
"""
Standalone independent set counter for trees in graph6 format.

No local imports — this file is fully self-contained.

Usage:
    python is_calculator.py trees.g6          # read from file
    cat trees.g6 | python is_calculator.py    # read from stdin
"""

import sys
from math import prod
from collections import deque

import networkx as nx


def count_independent_sets(T: nx.Graph) -> int:
    """Exact IS count (including empty set) via tree DP."""
    if len(T) == 0:
        return 1
    root = next(iter(T.nodes))
    rooted = nx.bfs_tree(T, root)
    f = {}
    for v in reversed(list(rooted.nodes)):
        children = list(rooted.successors(v))
        if not children:
            f[v] = (1, 1)  # (include, exclude)
        else:
            inc = prod(f[c][1] for c in children)
            exc = prod(f[c][0] + f[c][1] for c in children)
            f[v] = (inc, exc)
    return f[root][0] + f[root][1]


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as fh:
            lines = fh.read().splitlines()
    else:
        lines = sys.stdin.read().splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        T = nx.from_graph6_bytes(line.encode())
        if not nx.is_tree(T):
            print(f"ERROR: not a tree ({T.number_of_nodes()} nodes, "
                  f"{T.number_of_edges()} edges)", file=sys.stderr)
            sys.exit(1)
        print(count_independent_sets(T))


if __name__ == "__main__":
    main()

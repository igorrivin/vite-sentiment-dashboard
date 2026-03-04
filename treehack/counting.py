"""
Independent set counting on trees.

Two implementations:
  - count_independent_sets: exact bignum DP (O(n))
  - log_count_independent_sets: log-space floating-point DP (O(n))

Convention: DP tuples are (include, exclude) throughout.
"""

import networkx as nx
from math import prod
import numpy as np


def count_independent_sets(T: nx.Graph) -> int:
    """
    Count all independent sets in a tree T (including the empty set)
    using the standard subtree DP.

      f[v][0] = # IS in subtree(v) with v included
      f[v][1] = # IS in subtree(v) with v excluded

    Returns an exact integer (can be very large).
    """
    if len(T) == 0:
        return 1
    root = next(iter(T.nodes))
    rooted = nx.bfs_tree(T, root)

    f = {}  # f[v] = (include_count, exclude_count)

    for v in reversed(list(rooted.nodes)):
        children = list(rooted.successors(v))
        if not children:
            f[v] = (1, 1)
        else:
            inc = prod(f[c][1] for c in children)            # v in -> children out
            exc = prod(f[c][0] + f[c][1] for c in children)  # v out -> children free
            f[v] = (inc, exc)

    inc_root, exc_root = f[root]
    return inc_root + exc_root


def log_count_independent_sets(T: nx.Graph) -> float:
    """
    Compute log(#independent sets) via tree DP in log-space (float).

    Uses numpy logaddexp for numerical stability.
    """
    if len(T) == 0:
        return 0.0
    root = next(iter(T.nodes))
    rooted = nx.bfs_tree(T, root)
    f = {}  # f[v] = (log_include, log_exclude)

    for v in reversed(list(rooted.nodes)):
        children = list(rooted.successors(v))
        if not children:
            f[v] = (0.0, 0.0)
        else:
            log_inc = sum(f[c][1] for c in children)
            log_exc = sum(np.logaddexp(f[c][0], f[c][1]) for c in children)
            f[v] = (log_inc, log_exc)

    return float(np.logaddexp(f[root][0], f[root][1]))

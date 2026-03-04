"""
Independent set counting on bounded-treewidth graphs via tree decomposition DP.

Time complexity: O(n * 2^k) where k = treewidth.

Two implementations:
  - count_independent_sets_tw: exact bignum DP
  - log_count_independent_sets_tw: log-space floating-point DP

Unified entry point:
  - count_independent_sets_general: dispatches to tree DP or treewidth DP
"""

import networkx as nx
import numpy as np
from itertools import combinations

from tree_decomposition import TreeDecomposition
from counting import count_independent_sets, log_count_independent_sets


def _is_independent(G: nx.Graph, subset: frozenset[int]) -> bool:
    """Check if a subset of vertices is independent in G."""
    for u in subset:
        for v in subset:
            if u < v and G.has_edge(u, v):
                return False
    return True


def _independent_subsets(G: nx.Graph, bag: frozenset[int]) -> list[frozenset[int]]:
    """Enumerate all independent subsets of a bag (including empty set)."""
    vertices = sorted(bag)
    result = [frozenset()]
    for r in range(1, len(vertices) + 1):
        for combo in combinations(vertices, r):
            s = frozenset(combo)
            if _is_independent(G, s):
                result.append(s)
    return result


def count_independent_sets_tw(td: TreeDecomposition) -> int:
    """
    Count all independent sets in td.graph using tree decomposition DP.
    Includes the empty set.

    Algorithm:
    - Root the decomposition tree, process in post-order
    - For each bag, enumerate independent subsets
    - DP transition: for each child, sum over compatible states
      (states that agree on the separator = bag intersection)
    """
    G = td.graph
    T = td.tree
    bags = td.bags

    if len(G) == 0:
        return 1
    if len(T) == 0:
        return 1

    # Root the decomposition tree
    root = next(iter(T.nodes))
    rooted = nx.bfs_tree(T, root)

    # Pre-compute independent subsets for each bag
    ind_subsets = {}
    for bid, bag in bags.items():
        ind_subsets[bid] = _independent_subsets(G, bag)

    # Post-order traversal
    order = list(reversed(list(rooted.nodes)))

    # dp[bag_id] = dict mapping frozenset (independent subset of bag) -> count
    dp = {}

    for bid in order:
        children = list(rooted.successors(bid))
        bag = bags[bid]

        if not children:
            # Leaf bag: each independent subset has count 1
            dp[bid] = {S: 1 for S in ind_subsets[bid]}
        else:
            # Start with counts for this bag's independent subsets
            dp[bid] = {S: 1 for S in ind_subsets[bid]}

            for child in children:
                child_bag = bags[child]
                separator = bag & child_bag  # vertices in both bags

                # For each child, pre-index by separator restriction
                # child_by_sep[sep_subset] = sum of dp[child][S'] for all S'
                # whose intersection with separator equals sep_subset
                child_by_sep = {}
                for S_child, cnt in dp[child].items():
                    sep_part = S_child & separator
                    child_by_sep[sep_part] = child_by_sep.get(sep_part, 0) + cnt

                # Multiply into parent DP
                new_dp = {}
                for S_parent, cnt in dp[bid].items():
                    sep_part = S_parent & separator
                    child_sum = child_by_sep.get(sep_part, 0)
                    if child_sum > 0:
                        new_dp[S_parent] = cnt * child_sum

                dp[bid] = new_dp

    return sum(dp[root].values())


def log_count_independent_sets_tw(td: TreeDecomposition) -> float:
    """
    Compute log(# independent sets) via tree decomposition DP in log-space.
    Uses numpy logaddexp for numerical stability.
    """
    G = td.graph
    T = td.tree
    bags = td.bags

    if len(G) == 0:
        return 0.0
    if len(T) == 0:
        return 0.0

    root = next(iter(T.nodes))
    rooted = nx.bfs_tree(T, root)

    ind_subsets = {}
    for bid, bag in bags.items():
        ind_subsets[bid] = _independent_subsets(G, bag)

    order = list(reversed(list(rooted.nodes)))
    dp = {}  # dp[bag_id] = dict mapping frozenset -> log_count

    for bid in order:
        children = list(rooted.successors(bid))
        bag = bags[bid]

        if not children:
            dp[bid] = {S: 0.0 for S in ind_subsets[bid]}
        else:
            dp[bid] = {S: 0.0 for S in ind_subsets[bid]}

            for child in children:
                child_bag = bags[child]
                separator = bag & child_bag

                # Pre-index child DP by separator restriction (in log-space)
                child_by_sep = {}
                for S_child, log_cnt in dp[child].items():
                    sep_part = S_child & separator
                    if sep_part in child_by_sep:
                        child_by_sep[sep_part] = float(
                            np.logaddexp(child_by_sep[sep_part], log_cnt))
                    else:
                        child_by_sep[sep_part] = log_cnt

                new_dp = {}
                for S_parent, log_cnt in dp[bid].items():
                    sep_part = S_parent & separator
                    if sep_part in child_by_sep:
                        new_dp[S_parent] = log_cnt + child_by_sep[sep_part]

                dp[bid] = new_dp

    # Sum over all states at root
    vals = list(dp[root].values())
    if not vals:
        return 0.0
    result = vals[0]
    for v in vals[1:]:
        result = float(np.logaddexp(result, v))
    return result


def count_independent_sets_general(G: nx.Graph, td: TreeDecomposition = None) -> int:
    """
    Unified entry point: uses fast O(n) tree DP if G is a tree,
    otherwise falls back to O(n * 2^k) treewidth DP.

    If td is not provided and G is not a tree, raises ValueError.
    """
    if nx.is_tree(G) or (len(G.nodes) > 0 and len(G.edges) == 0):
        if nx.is_tree(G):
            return count_independent_sets(G)
        # Disconnected with no edges: every subset is independent
        return 2 ** len(G)

    if td is None:
        raise ValueError(
            "Graph is not a tree; a TreeDecomposition must be provided")

    return count_independent_sets_tw(td)

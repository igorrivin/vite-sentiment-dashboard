#!/usr/bin/env python3
"""
Standalone verifier for independent set counts on general graphs.

No local imports — this file is fully self-contained.
Only depends on networkx (+ numpy for log-space).

Works on any graph: uses NetworkX's treewidth heuristic to find a
tree decomposition, then runs O(n * 2^k) DP where k is the
(heuristic) treewidth. For trees (treewidth 1) this is fast; for
bounded-treewidth graphs it scales as 2^k per vertex.

Input formats:
  1. Edge list + counts:
       python verifier.py edges.txt counts.txt

     edges.txt has blocks separated by blank lines or comment lines:
       # Graph 1: 8 vertices
       0 1
       1 2
       1 3
       ...

       # Graph 2: 10 vertices
       0 1
       ...

     counts.txt has one integer per line (one per graph).

  2. graph6 + counts:
       python verifier.py graphs.g6 counts.txt

  3. Single graph via stdin:
       echo "5\n0 1\n1 2\n2 3\n3 4" | python verifier.py --count 144
"""

import sys
import argparse
from itertools import combinations

import networkx as nx


# ---------------------------------------------------------------------------
# Tree decomposition DP for independent set counting
# ---------------------------------------------------------------------------

def _is_independent(G, subset):
    """Check if a subset of vertices is independent in G."""
    for u in subset:
        for v in subset:
            if u < v and G.has_edge(u, v):
                return False
    return True


def _independent_subsets(G, bag):
    """Enumerate all independent subsets of a bag (including empty set)."""
    vertices = sorted(bag)
    result = [frozenset()]
    for r in range(1, len(vertices) + 1):
        for combo in combinations(vertices, r):
            s = frozenset(combo)
            if _is_independent(G, s):
                result.append(s)
    return result


def count_independent_sets(G):
    """
    Count all independent sets in G (including the empty set).

    Uses tree decomposition DP. For trees this is O(n); for general
    bounded-treewidth graphs it is O(n * 2^k).
    """
    if len(G) == 0:
        return 1

    # Fast path for trees
    if nx.is_tree(G):
        return _count_is_tree(G)

    # Handle disconnected graphs: IS count = product over components
    if not nx.is_connected(G):
        total = 1
        for comp in nx.connected_components(G):
            total *= count_independent_sets(G.subgraph(comp).copy())
        return total

    # General case: find tree decomposition via NetworkX heuristic
    tw, decomp_tree = nx.algorithms.approximation.treewidth_min_degree(G)

    # Convert frozenset-node decomposition to indexed bags
    bags = {}
    node_map = {}
    tree = nx.Graph()
    for i, node in enumerate(decomp_tree.nodes):
        bags[i] = frozenset(node)
        node_map[node] = i
        tree.add_node(i)
    for u, v in decomp_tree.edges:
        tree.add_edge(node_map[u], node_map[v])

    return _count_is_td(G, tree, bags)


def _count_is_tree(T):
    """O(n) tree DP for IS counting."""
    from math import prod

    if len(T) == 0:
        return 1
    root = next(iter(T.nodes))
    rooted = nx.bfs_tree(T, root)
    f = {}
    for v in reversed(list(rooted.nodes)):
        children = list(rooted.successors(v))
        if not children:
            f[v] = (1, 1)
        else:
            inc = prod(f[c][1] for c in children)
            exc = prod(f[c][0] + f[c][1] for c in children)
            f[v] = (inc, exc)
    return f[root][0] + f[root][1]


def _count_is_td(G, tree, bags):
    """Tree decomposition DP for IS counting."""
    if len(tree) == 0:
        return 1

    root = next(iter(tree.nodes))
    rooted = nx.bfs_tree(tree, root)

    # Pre-compute independent subsets for each bag
    ind_subsets = {bid: _independent_subsets(G, bag) for bid, bag in bags.items()}

    # Post-order DP
    order = list(reversed(list(rooted.nodes)))
    dp = {}

    for bid in order:
        children = list(rooted.successors(bid))
        bag = bags[bid]

        dp[bid] = {S: 1 for S in ind_subsets[bid]}

        for child in children:
            child_bag = bags[child]
            separator = bag & child_bag

            # Index child DP by separator restriction
            child_by_sep = {}
            for S_child, cnt in dp[child].items():
                sep_part = S_child & separator
                child_by_sep[sep_part] = child_by_sep.get(sep_part, 0) + cnt

            new_dp = {}
            for S_parent, cnt in dp[bid].items():
                sep_part = S_parent & separator
                child_sum = child_by_sep.get(sep_part, 0)
                if child_sum > 0:
                    new_dp[S_parent] = cnt * child_sum
            dp[bid] = new_dp

    return sum(dp[root].values())


# ---------------------------------------------------------------------------
# Input parsing
# ---------------------------------------------------------------------------

def parse_edgelist_file(path):
    """Parse a file of edge lists separated by blank/comment lines."""
    graphs = []
    current_edges = []
    current_nodes = set()

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                if current_nodes:
                    G = nx.Graph()
                    G.add_nodes_from(sorted(current_nodes))
                    G.add_edges_from(current_edges)
                    graphs.append(G)
                    current_edges = []
                    current_nodes = set()
                continue
            parts = line.split()
            if len(parts) >= 2:
                u, v = int(parts[0]), int(parts[1])
                current_edges.append((u, v))
                current_nodes.update([u, v])

    if current_nodes:
        G = nx.Graph()
        G.add_nodes_from(sorted(current_nodes))
        G.add_edges_from(current_edges)
        graphs.append(G)

    return graphs


def parse_graph6_file(path):
    """Parse a file of graph6-encoded graphs."""
    graphs = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                graphs.append(nx.from_graph6_bytes(line.encode()))
    return graphs


def parse_counts_file(path):
    """Parse a file of integer counts (one per line)."""
    counts = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                counts.append(int(line))
    return counts


def detect_format(path):
    """Detect whether a file is graph6 or edge list."""
    with open(path) as f:
        first_line = f.readline().strip()
    # graph6 lines are typically short ASCII without spaces
    if first_line and ' ' not in first_line and not first_line.startswith('#'):
        try:
            nx.from_graph6_bytes(first_line.encode())
            return 'graph6'
        except Exception:
            pass
    return 'edgelist'


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Verify independent set counts on graphs")
    parser.add_argument("graphs", nargs='?',
                        help="Graph file (edge list or graph6)")
    parser.add_argument("counts", nargs='?',
                        help="Counts file (one integer per line)")
    parser.add_argument("--count", type=int,
                        help="Expected count for single graph on stdin")
    args = parser.parse_args()

    # Mode 1: stdin with --count
    if args.graphs is None and args.count is not None:
        edges = []
        nodes = set()
        for line in sys.stdin:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2:
                u, v = int(parts[0]), int(parts[1])
                edges.append((u, v))
                nodes.update([u, v])
        G = nx.Graph()
        G.add_nodes_from(sorted(nodes))
        G.add_edges_from(edges)

        computed = count_independent_sets(G)
        ok = computed == args.count
        status = "PASS" if ok else "FAIL"
        print(f"[{status}]  n={len(G)}  m={G.number_of_edges()}  "
              f"computed={computed}  expected={args.count}")
        sys.exit(0 if ok else 1)

    # Mode 2: files
    if args.graphs is None or args.counts is None:
        parser.print_help()
        sys.exit(1)

    fmt = detect_format(args.graphs)
    if fmt == 'graph6':
        graphs = parse_graph6_file(args.graphs)
    else:
        graphs = parse_edgelist_file(args.graphs)

    expected = parse_counts_file(args.counts)

    if len(graphs) != len(expected):
        print(f"ERROR: {len(graphs)} graphs but {len(expected)} counts",
              file=sys.stderr)
        sys.exit(1)

    n_pass = 0
    n_fail = 0

    for i, (G, exp_count) in enumerate(zip(graphs, expected)):
        computed = count_independent_sets(G)
        ok = computed == exp_count
        status = "PASS" if ok else "FAIL"
        print(f"  Graph {i+1:4d}: n={len(G):4d}  m={G.number_of_edges():5d}  "
              f"computed={computed}  expected={exp_count}  [{status}]")
        if ok:
            n_pass += 1
        else:
            n_fail += 1

    print(f"\n{n_pass} passed, {n_fail} failed out of {len(graphs)}")
    sys.exit(0 if n_fail == 0 else 1)


if __name__ == "__main__":
    main()

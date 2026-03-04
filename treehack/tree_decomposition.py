"""
Tree decomposition data structure for bounded-treewidth graphs.

A tree decomposition of a graph G = (V, E) is a tree T where each node
(called a "bag") contains a subset of V, satisfying three axioms:
  1. Vertex coverage: every vertex of G appears in at least one bag
  2. Edge coverage: for every edge (u,v) of G, some bag contains both u and v
  3. Running intersection: for every vertex v, the bags containing v form
     a connected subtree of T
"""

from dataclasses import dataclass, field
import networkx as nx


@dataclass
class TreeDecomposition:
    """Tree decomposition of a graph."""
    graph: nx.Graph                          # original graph
    tree: nx.Graph                           # decomposition tree (integer bag IDs)
    bags: dict[int, frozenset[int]] = field(default_factory=dict)  # bag ID -> vertex set

    @property
    def width(self) -> int:
        """Treewidth = max bag size - 1."""
        if not self.bags:
            return 0
        return max(len(b) for b in self.bags.values()) - 1

    def validate(self) -> bool:
        """Check all three tree decomposition axioms. Raises ValueError on failure."""
        G = self.graph
        T = self.tree

        # Must be a tree (or single node)
        if len(T) > 1 and not nx.is_tree(T):
            raise ValueError("Decomposition tree is not a tree")
        if len(T) == 0:
            if len(G) == 0:
                return True
            raise ValueError("Empty decomposition for non-empty graph")

        all_vertices_in_bags = set()
        for bag in self.bags.values():
            all_vertices_in_bags.update(bag)

        # Axiom 1: vertex coverage
        for v in G.nodes:
            if v not in all_vertices_in_bags:
                raise ValueError(f"Vertex {v} not in any bag")

        # Axiom 2: edge coverage
        for u, v in G.edges:
            found = any(u in bag and v in bag for bag in self.bags.values())
            if not found:
                raise ValueError(f"Edge ({u}, {v}) not covered by any bag")

        # Axiom 3: running intersection
        for v in G.nodes:
            containing = [bid for bid, bag in self.bags.items() if v in bag]
            if not containing:
                continue
            subgraph = T.subgraph(containing)
            if not nx.is_connected(subgraph):
                raise ValueError(
                    f"Bags containing vertex {v} do not form a connected subtree")

        return True

    @staticmethod
    def trivial_from_tree(T: nx.Graph) -> 'TreeDecomposition':
        """
        Create an edge-based decomposition of a tree (treewidth 1).
        Each edge becomes a bag of size 2.
        """
        if len(T) == 0:
            return TreeDecomposition(graph=T, tree=nx.Graph(), bags={})

        if len(T) == 1:
            v = next(iter(T.nodes))
            decomp_tree = nx.Graph()
            decomp_tree.add_node(0)
            return TreeDecomposition(graph=T, tree=decomp_tree, bags={0: frozenset({v})})

        bags = {}
        decomp_tree = nx.Graph()
        edge_to_bag = {}

        for i, (u, v) in enumerate(T.edges):
            bags[i] = frozenset({u, v})
            decomp_tree.add_node(i)
            edge_to_bag[(u, v)] = i
            edge_to_bag[(v, u)] = i

        # Connect bags that share a vertex (adjacent edges in the original tree)
        root = next(iter(T.nodes))
        rooted = nx.bfs_tree(T, root)
        for v in rooted.nodes:
            parent_edges = []
            for pred in rooted.predecessors(v):
                parent_edges.append(edge_to_bag[(pred, v)])
            child_edges = []
            for succ in rooted.successors(v):
                child_edges.append(edge_to_bag[(v, succ)])

            # Chain: parent_edge -> first_child_edge -> ... -> last_child_edge
            all_at_v = parent_edges + child_edges
            for j in range(len(all_at_v) - 1):
                decomp_tree.add_edge(all_at_v[j], all_at_v[j + 1])

        return TreeDecomposition(graph=T, tree=decomp_tree, bags=bags)

    @staticmethod
    def from_networkx(G: nx.Graph, decomp_tree: nx.Graph) -> 'TreeDecomposition':
        """
        Convert from NetworkX's tree decomposition format where nodes
        are frozensets of vertices.
        """
        bags = {}
        node_map = {}  # frozenset node -> integer ID
        new_tree = nx.Graph()

        for i, node in enumerate(decomp_tree.nodes):
            bags[i] = frozenset(node) if isinstance(node, frozenset) else frozenset({node})
            node_map[node] = i
            new_tree.add_node(i)

        for u, v in decomp_tree.edges:
            new_tree.add_edge(node_map[u], node_map[v])

        return TreeDecomposition(graph=G, tree=new_tree, bags=bags)

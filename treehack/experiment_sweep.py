"""
Experiment: correlations across treewidths + extremal graph properties.

Part 1: Sweep k=2..8, compute correlations at each treewidth
Part 2: Hill-climb for IS-maximizing and IS-minimizing graphs,
        characterize their structure
"""

import random
from math import log

import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

from tw_counting import count_independent_sets_tw, log_count_independent_sets_tw
from tw_generators import random_k_tree, random_partial_k_tree
from tree_decomposition import TreeDecomposition


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def log_spanning_trees(G):
    if not nx.is_connected(G):
        return float('-inf')
    L = nx.laplacian_matrix(G).toarray().astype(float)
    L_sub = L[:-1, :-1]
    sign, logdet = np.linalg.slogdet(L_sub)
    return logdet if sign > 0 else float('-inf')


def girth(G):
    try:
        return nx.girth(G)
    except Exception:
        min_cycle = float('inf')
        for u, v in G.edges:
            G2 = G.copy()
            G2.remove_edge(u, v)
            try:
                min_cycle = min(min_cycle, nx.shortest_path_length(G2, u, v) + 1)
            except nx.NetworkXNoPath:
                pass
        return min_cycle


def lambda_1(G):
    A = nx.adjacency_matrix(G).toarray().astype(float)
    return np.linalg.eigvalsh(A)[-1]


def algebraic_connectivity(G):
    """Second-smallest eigenvalue of the Laplacian (Fiedler value)."""
    if not nx.is_connected(G):
        return 0.0
    L = nx.laplacian_matrix(G).toarray().astype(float)
    eigs = np.linalg.eigvalsh(L)
    return eigs[1]


def chromatic_number_upper(G):
    """Greedy chromatic number (upper bound)."""
    coloring = nx.coloring.greedy_color(G, strategy='largest_first')
    return max(coloring.values()) + 1 if coloring else 0


def clustering_coeff(G):
    return nx.average_clustering(G)


def collect_stats(n, k, n_samples, edge_keep_prob, rng):
    stats = {
        'log_is': [], 'log_st': [], 'girth': [],
        'lambda1': [], 'algebraic_conn': [], 'avg_deg': [],
        'edges': [], 'clustering': [], 'chromatic_ub': [],
    }
    for _ in range(n_samples):
        if edge_keep_prob is not None:
            G, td = random_partial_k_tree(n, k, edge_keep_prob, rng)
        else:
            G, td = random_k_tree(n, k, rng)
        stats['log_is'].append(log_count_independent_sets_tw(td))
        stats['log_st'].append(log_spanning_trees(G))
        stats['girth'].append(girth(G))
        stats['lambda1'].append(lambda_1(G))
        stats['algebraic_conn'].append(algebraic_connectivity(G))
        stats['avg_deg'].append(2 * G.number_of_edges() / n)
        stats['edges'].append(G.number_of_edges())
        stats['clustering'].append(clustering_coeff(G))
        stats['chromatic_ub'].append(chromatic_number_upper(G))
    return {k: np.array(v) for k, v in stats.items()}


STAT_NAMES = {
    'log_st': 'log(ST)',
    'girth': 'girth',
    'lambda1': 'λ₁',
    'algebraic_conn': 'alg. conn.',
    'avg_deg': 'avg deg',
    'edges': 'edges',
    'clustering': 'clustering',
    'chromatic_ub': 'χ (greedy)',
}


# ---------------------------------------------------------------------------
# Part 1: Treewidth sweep
# ---------------------------------------------------------------------------

def run_treewidth_sweep():
    N = 40
    SAMPLES = 300
    TREEWIDTHS = [2, 3, 4, 5, 6, 7, 8]

    print("=" * 70)
    print("  PART 1: Correlation sweep across treewidths")
    print(f"  n={N}, {SAMPLES} samples per setting")
    print("=" * 70)

    # Collect correlations for full k-trees and partial k-trees
    results_full = {}
    results_partial = {}

    for k in TREEWIDTHS:
        rng = random.Random(42 + k)

        print(f"\n--- k={k} (full {k}-trees) ---")
        stats = collect_stats(N, k, SAMPLES, edge_keep_prob=None, rng=rng)
        results_full[k] = {}
        target = stats['log_is']
        for skey, sname in STAT_NAMES.items():
            vals = stats[skey]
            mask = np.isfinite(vals) & np.isfinite(target)
            if mask.sum() >= 5 and np.std(vals[mask]) > 1e-10:
                r, p = pearsonr(target[mask], vals[mask])
                results_full[k][skey] = (r, p)
                print(f"  {sname:<15s}  r={r:+.4f}  p={p:.2e}  "
                      f"(mean={np.mean(vals):.2f}, std={np.std(vals):.2f})")
            else:
                results_full[k][skey] = (float('nan'), 1.0)
                print(f"  {sname:<15s}  constant or insufficient data")

        rng2 = random.Random(100 + k)
        print(f"\n--- k={k} (partial {k}-trees, keep=0.5) ---")
        stats = collect_stats(N, k, SAMPLES, edge_keep_prob=0.5, rng=rng2)
        results_partial[k] = {}
        target = stats['log_is']
        for skey, sname in STAT_NAMES.items():
            vals = stats[skey]
            mask = np.isfinite(vals) & np.isfinite(target)
            if mask.sum() >= 5 and np.std(vals[mask]) > 1e-10:
                r, p = pearsonr(target[mask], vals[mask])
                results_partial[k][skey] = (r, p)
                print(f"  {sname:<15s}  r={r:+.4f}  p={p:.2e}")
            else:
                results_partial[k][skey] = (float('nan'), 1.0)
                print(f"  {sname:<15s}  constant or insufficient data")

    # Summary heatmap
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    stat_keys = [s for s in STAT_NAMES.keys()]
    stat_labels = [STAT_NAMES[s] for s in stat_keys]

    for ax, results, title in [
        (ax1, results_full, "Full k-trees (Pearson r vs log IS)"),
        (ax2, results_partial, "Partial k-trees, keep=0.5"),
    ]:
        matrix = np.zeros((len(TREEWIDTHS), len(stat_keys)))
        for i, k in enumerate(TREEWIDTHS):
            for j, skey in enumerate(stat_keys):
                r, _ = results[k].get(skey, (float('nan'), 1.0))
                matrix[i, j] = r

        im = ax.imshow(matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
        ax.set_xticks(range(len(stat_labels)))
        ax.set_xticklabels(stat_labels, rotation=45, ha='right', fontsize=9)
        ax.set_yticks(range(len(TREEWIDTHS)))
        ax.set_yticklabels([f"k={k}" for k in TREEWIDTHS])
        ax.set_title(title, fontsize=11)

        for i in range(len(TREEWIDTHS)):
            for j in range(len(stat_keys)):
                v = matrix[i, j]
                if np.isfinite(v):
                    color = 'white' if abs(v) > 0.5 else 'black'
                    ax.text(j, i, f"{v:.2f}", ha='center', va='center',
                            fontsize=7, color=color)
                else:
                    ax.text(j, i, "—", ha='center', va='center',
                            fontsize=8, color='gray')

    plt.colorbar(im, ax=ax2, shrink=0.8, label="Pearson r")
    plt.tight_layout()
    plt.savefig("correlation_sweep.png", dpi=150, bbox_inches='tight')
    print("\nSaved correlation_sweep.png")


# ---------------------------------------------------------------------------
# Part 2: Extremal graphs via hill climbing
# ---------------------------------------------------------------------------

def _mutate_tw(G, td, rng):
    """Edge-swap mutation preserving decomposition validity."""
    edges = list(G.edges)
    if len(edges) < 2:
        return G, td

    bridges = set(nx.bridges(G))
    removable = [e for e in edges if e not in bridges and (e[1], e[0]) not in bridges]
    if not removable:
        return G, td

    G2 = G.copy()
    G2.remove_edge(*rng.choice(removable))

    nodes = list(G2.nodes)
    for _ in range(30):
        u, v = rng.choice(nodes), rng.choice(nodes)
        if u != v and not G2.has_edge(u, v):
            G2.add_edge(u, v)
            if any(u in bag and v in bag for bag in td.bags.values()):
                return G2, TreeDecomposition(graph=G2, tree=td.tree, bags=td.bags)
            G2.remove_edge(u, v)

    return G, td


def hill_climb_extremal(n, k, steps, restarts, maximize=True, seed=42):
    """Hill climb to find IS-maximizing or IS-minimizing graph."""
    rng = random.Random(seed)
    best_G, best_td, best_score = None, None, None

    for _ in range(restarts):
        G, td = random_partial_k_tree(n, k, 0.6, rng)
        score = log_count_independent_sets_tw(td)

        for _ in range(steps):
            G2, td2 = _mutate_tw(G, td, rng)
            s2 = log_count_independent_sets_tw(td2)
            if (maximize and s2 >= score) or (not maximize and s2 <= score):
                G, td, score = G2, td2, s2

        if best_score is None or \
           (maximize and score > best_score) or \
           (not maximize and score < best_score):
            best_G, best_td, best_score = G, td, score

    return best_G, best_td, best_score


def characterize(G, td, label):
    """Print detailed statistics of a graph."""
    n = G.number_of_nodes()
    m = G.number_of_edges()
    is_count = count_independent_sets_tw(td)
    log_is = log_count_independent_sets_tw(td)

    deg_seq = sorted([d for _, d in G.degree()], reverse=True)
    deg_mean = np.mean(deg_seq)
    deg_std = np.std(deg_seq)

    print(f"\n  {label}")
    print(f"  {'─' * 50}")
    print(f"    n={n}, m={m}, tw≤{td.width}")
    print(f"    IS count     = {is_count:,}")
    print(f"    log(IS)      = {log_is:.4f}")
    print(f"    log(ST)      = {log_spanning_trees(G):.4f}")
    print(f"    girth        = {girth(G)}")
    print(f"    λ₁           = {lambda_1(G):.4f}")
    print(f"    alg. conn.   = {algebraic_connectivity(G):.4f}")
    print(f"    clustering   = {clustering_coeff(G):.4f}")
    print(f"    χ (greedy)   = {chromatic_number_upper(G)}")
    print(f"    deg mean     = {deg_mean:.2f}")
    print(f"    deg std      = {deg_std:.2f}")
    print(f"    deg seq      = {deg_seq[:15]}{'...' if len(deg_seq) > 15 else ''}")


def run_extremal_search():
    print("\n" + "=" * 70)
    print("  PART 2: Extremal graph search via hill climbing")
    print("=" * 70)

    for k in [2, 3, 5]:
        n = 35
        print(f"\n{'─' * 70}")
        print(f"  Treewidth k={k}, n={n}")
        print(f"{'─' * 70}")

        # Random baseline
        rng = random.Random(42)
        G_rand, td_rand = random_partial_k_tree(n, k, 0.6, rng)
        characterize(G_rand, td_rand, f"Random partial {k}-tree (baseline)")

        # Maximize IS
        G_max, td_max, score_max = hill_climb_extremal(
            n, k, steps=2000, restarts=5, maximize=True, seed=42)
        characterize(G_max, td_max, f"IS-MAXIMIZING partial {k}-tree")

        # Minimize IS
        G_min, td_min, score_min = hill_climb_extremal(
            n, k, steps=2000, restarts=5, maximize=False, seed=42)
        characterize(G_min, td_min, f"IS-MINIMIZING partial {k}-tree")

    # --- Degree distribution comparison plot ---
    print("\nGenerating extremal comparison plots...")

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))

    for col, k in enumerate([2, 3, 5]):
        n = 35
        rng = random.Random(42)
        G_rand, td_rand = random_partial_k_tree(n, k, 0.6, rng)
        G_max, td_max, _ = hill_climb_extremal(n, k, 2000, 5, True, 42)
        G_min, td_min, _ = hill_climb_extremal(n, k, 2000, 5, False, 42)

        # Degree distributions
        ax = axes[0, col]
        for G, label, color in [
            (G_rand, 'random', 'gray'),
            (G_max, 'max IS', 'forestgreen'),
            (G_min, 'min IS', 'firebrick'),
        ]:
            degs = sorted([d for _, d in G.degree()])
            ax.hist(degs, bins=range(0, max(degs) + 2), alpha=0.5,
                    label=label, color=color, edgecolor='white')
        ax.set_xlabel("Degree")
        ax.set_ylabel("Count")
        ax.set_title(f"Degree distribution (k={k})")
        ax.legend(fontsize=8)

        # Eigenvalue spectra
        ax = axes[1, col]
        for G, label, color in [
            (G_rand, 'random', 'gray'),
            (G_max, 'max IS', 'forestgreen'),
            (G_min, 'min IS', 'firebrick'),
        ]:
            A = nx.adjacency_matrix(G).toarray().astype(float)
            eigs = np.linalg.eigvalsh(A)
            ax.hist(eigs, bins=30, alpha=0.4, label=label, color=color,
                    edgecolor='white', density=True)
        ax.set_xlabel("Eigenvalue")
        ax.set_ylabel("Density")
        ax.set_title(f"Spectral distribution (k={k})")
        ax.legend(fontsize=8)

    plt.suptitle("Extremal vs random graphs at different treewidths", fontsize=13)
    plt.tight_layout()
    plt.savefig("extremal_comparison.png", dpi=150, bbox_inches='tight')
    print("Saved extremal_comparison.png")


if __name__ == "__main__":
    run_treewidth_sweep()
    run_extremal_search()
    print("\nDone.")

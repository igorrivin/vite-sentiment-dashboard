"""
Experiment: correlations between IS count and other graph statistics
on random bounded-treewidth graphs.

Statistics computed:
  - log(IS count)          via treewidth DP
  - log(spanning trees)    via Kirchhoff's matrix tree theorem
  - girth                  shortest cycle length
  - lambda_1               largest eigenvalue of adjacency matrix
  - average degree
  - number of edges
"""

import random
from math import log

import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

from tw_counting import log_count_independent_sets_tw
from tw_generators import random_k_tree, random_partial_k_tree


def log_spanning_trees(G):
    """log(# spanning trees) via Kirchhoff's theorem: det of any (n-1)x(n-1) cofactor of Laplacian."""
    if not nx.is_connected(G):
        return float('-inf')
    L = nx.laplacian_matrix(G).toarray().astype(float)
    # Remove last row/col
    L_sub = L[:-1, :-1]
    sign, logdet = np.linalg.slogdet(L_sub)
    if sign <= 0:
        return float('-inf')
    return logdet


def girth(G):
    """Shortest cycle length. Returns float('inf') if acyclic."""
    try:
        return nx.girth(G)
    except Exception:
        # Fallback for older networkx
        min_cycle = float('inf')
        for v in G.nodes:
            lengths = nx.single_source_shortest_path_length(G, v)
            for u in G.neighbors(v):
                # Check for short cycles through back-edges in BFS
                pass
        # Simple BFS-based approach
        for u, v in G.edges:
            G2 = G.copy()
            G2.remove_edge(u, v)
            try:
                cycle_len = nx.shortest_path_length(G2, u, v) + 1
                min_cycle = min(min_cycle, cycle_len)
            except nx.NetworkXNoPath:
                pass
        return min_cycle


def lambda_1(G):
    """Largest eigenvalue of adjacency matrix."""
    A = nx.adjacency_matrix(G).toarray().astype(float)
    eigenvalues = np.linalg.eigvalsh(A)
    return eigenvalues[-1]


def collect_stats(n, k, n_samples, edge_keep_prob=None, seed=42):
    """Generate random graphs and compute all statistics."""
    rng = random.Random(seed)
    stats = {
        'log_is': [], 'log_st': [], 'girth': [],
        'lambda1': [], 'avg_deg': [], 'edges': []
    }

    for i in range(n_samples):
        if edge_keep_prob is not None:
            G, td = random_partial_k_tree(n, k, edge_keep_prob, rng)
        else:
            G, td = random_k_tree(n, k, rng)

        stats['log_is'].append(log_count_independent_sets_tw(td))
        stats['log_st'].append(log_spanning_trees(G))
        stats['girth'].append(girth(G))
        stats['lambda1'].append(lambda_1(G))
        stats['edges'].append(G.number_of_edges())
        stats['avg_deg'].append(2 * G.number_of_edges() / G.number_of_nodes())

    return {k: np.array(v) for k, v in stats.items()}


def print_correlations(stats, label):
    """Print Pearson and Spearman correlations of all stats vs log(IS)."""
    print(f"\n{'=' * 65}")
    print(f"  {label}")
    print(f"{'=' * 65}")

    target = stats['log_is']
    names = {
        'log_st': 'log(spanning trees)',
        'girth': 'girth',
        'lambda1': 'λ₁ (spectral radius)',
        'avg_deg': 'average degree',
        'edges': 'edge count',
    }

    print(f"\n  {'Statistic':<25s}  {'Pearson r':>10s}  {'p-value':>10s}  "
          f"{'Spearman ρ':>10s}  {'p-value':>10s}")
    print(f"  {'-'*25}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*10}")

    for key, name in names.items():
        vals = stats[key]
        # Filter out infinities for correlation
        mask = np.isfinite(vals) & np.isfinite(target)
        if mask.sum() < 5:
            print(f"  {name:<25s}  {'(insufficient data)':>45s}")
            continue
        pr, pp = pearsonr(target[mask], vals[mask])
        sr, sp = spearmanr(target[mask], vals[mask])
        print(f"  {name:<25s}  {pr:10.4f}  {pp:10.2e}  {sr:10.4f}  {sp:10.2e}")

    # Summary stats
    print(f"\n  Summary: n={len(target)} graphs")
    for key, name in [('log_is', 'log(IS)')] + list(names.items()):
        vals = stats[key]
        finite = vals[np.isfinite(vals)]
        print(f"    {name:<25s}  mean={np.mean(finite):8.2f}  "
              f"std={np.std(finite):7.2f}  "
              f"range=[{np.min(finite):.2f}, {np.max(finite):.2f}]")


def plot_correlations(stats, label, filename):
    """Scatter plots of each statistic vs log(IS)."""
    target = stats['log_is']
    pairs = [
        ('log_st', 'log(spanning trees)'),
        ('girth', 'girth'),
        ('lambda1', 'λ₁ (spectral radius)'),
        ('avg_deg', 'average degree'),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(label, fontsize=14, y=0.98)

    for ax, (key, name) in zip(axes.flat, pairs):
        vals = stats[key]
        mask = np.isfinite(vals) & np.isfinite(target)
        x, y = target[mask], vals[mask]

        ax.scatter(x, y, alpha=0.3, s=12, edgecolors='none')

        # Trend line
        if len(x) > 2:
            z = np.polyfit(x, y, 1)
            x_line = np.linspace(x.min(), x.max(), 100)
            ax.plot(x_line, np.polyval(z, x_line), 'r-', lw=1.5, alpha=0.7)
            pr, _ = pearsonr(x, y)
            ax.set_title(f"{name}  (r={pr:.3f})", fontsize=11)
        else:
            ax.set_title(name, fontsize=11)

        ax.set_xlabel("log(IS count)")
        ax.set_ylabel(name)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\nSaved {filename}")


if __name__ == "__main__":
    N = 40          # vertices
    K = 5           # treewidth
    SAMPLES = 500

    # Experiment 1: full k-trees (treewidth exactly k)
    print(f"Generating {SAMPLES} random {K}-trees on {N} vertices...")
    stats_full = collect_stats(N, K, SAMPLES, edge_keep_prob=None, seed=42)
    print_correlations(stats_full, f"Full {K}-trees  (n={N}, tw={K}, {SAMPLES} samples)")
    plot_correlations(stats_full,
                      f"Full {K}-trees  (n={N}, tw={K})",
                      "correlations_full_ktree.png")

    # Experiment 2: partial k-trees (treewidth ≤ k, varying density)
    print(f"\nGenerating {SAMPLES} random partial {K}-trees on {N} vertices...")
    stats_partial = collect_stats(N, K, SAMPLES, edge_keep_prob=0.6, seed=123)
    print_correlations(stats_partial,
                       f"Partial {K}-trees  (n={N}, tw≤{K}, keep=0.6, {SAMPLES} samples)")
    plot_correlations(stats_partial,
                      f"Partial {K}-trees  (n={N}, tw≤{K}, keep=0.6)",
                      "correlations_partial_ktree.png")

    # Experiment 3: vary edge_keep_prob to get wider density range
    print(f"\nGenerating {SAMPLES} partial {K}-trees with mixed densities...")
    rng = random.Random(456)
    mixed_stats = {k: [] for k in ['log_is', 'log_st', 'girth', 'lambda1', 'avg_deg', 'edges']}
    for i in range(SAMPLES):
        ekp = rng.uniform(0.3, 1.0)
        G, td = random_partial_k_tree(N, K, ekp, rng)
        mixed_stats['log_is'].append(log_count_independent_sets_tw(td))
        mixed_stats['log_st'].append(log_spanning_trees(G))
        mixed_stats['girth'].append(girth(G))
        mixed_stats['lambda1'].append(lambda_1(G))
        mixed_stats['edges'].append(G.number_of_edges())
        mixed_stats['avg_deg'].append(2 * G.number_of_edges() / N)
    mixed_stats = {k: np.array(v) for k, v in mixed_stats.items()}

    print_correlations(mixed_stats,
                       f"Partial {K}-trees mixed density  (n={N}, tw≤{K}, {SAMPLES} samples)")
    plot_correlations(mixed_stats,
                      f"Partial {K}-trees mixed density  (n={N}, tw≤{K})",
                      "correlations_mixed_density.png")

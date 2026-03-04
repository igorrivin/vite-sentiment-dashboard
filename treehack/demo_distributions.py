"""Demo: IS count distributions on random trees and bounded-treewidth graphs + MCMC inverse sampler."""

import random
from math import log, exp

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import gaussian_kde

from counting import count_independent_sets, log_count_independent_sets
from generators import (prufer_tree, galton_watson_tree,
                         preferential_attachment_tree, random_caterpillar)
from optimization import mcmc_inverse
from tw_counting import log_count_independent_sets_tw
from tw_generators import random_k_tree, random_partial_k_tree, overlay_trees

if __name__ == "__main__":
    N_NODES   = 30
    N_SAMPLES = 1500
    rng = random.Random(42)

    print(f"Sampling {N_SAMPLES} trees of ~{N_NODES} nodes from each model...\n")

    def sample_model(name, gen_fn):
        lc = np.array([log_count_independent_sets(gen_fn()) for _ in range(N_SAMPLES)])
        print(f"  {name:<40}  mean={np.mean(lc):6.2f}  std={np.std(lc):.2f}  "
              f"range=[{np.min(lc):.1f}, {np.max(lc):.1f}]")
        return lc

    lam = 1.5
    models = {
        "Prüfer (uniform labeled)":
            lambda: prufer_tree(N_NODES, rng),
        f"Galton-Watson Poisson({lam})":
            lambda: galton_watson_tree(lambda r: np.random.poisson(lam), N_NODES, rng),
        "Galton-Watson Geom(0.5)  [mean=1]":
            lambda: galton_watson_tree(lambda r: np.random.geometric(0.5)-1, N_NODES, rng),
        "Preferential attachment":
            lambda: preferential_attachment_tree(N_NODES, rng),
        "Random caterpillar":
            lambda: random_caterpillar(N_NODES, rng),
    }
    log_counts = {name: sample_model(name, fn) for name, fn in models.items()}

    # Bounded-treewidth models
    print(f"\nSampling {N_SAMPLES} bounded-treewidth graphs of ~{N_NODES} nodes...\n")

    def sample_tw_model(name, gen_fn):
        vals = []
        for _ in range(N_SAMPLES):
            G, td = gen_fn()
            vals.append(log_count_independent_sets_tw(td))
        lc = np.array(vals)
        print(f"  {name:<40}  mean={np.mean(lc):6.2f}  std={np.std(lc):.2f}  "
              f"range=[{np.min(lc):.1f}, {np.max(lc):.1f}]")
        return lc

    tw_models = {
        "2-tree (tw=2)":
            lambda: random_k_tree(N_NODES, 2, rng),
        "Partial 2-tree (tw≤2)":
            lambda: random_partial_k_tree(N_NODES, 2, 0.7, rng),
        "Overlay of 2 trees":
            lambda: overlay_trees(N_NODES, rng),
    }
    tw_log_counts = {name: sample_tw_model(name, fn) for name, fn in tw_models.items()}

    # Merge for plotting
    all_log_counts = {**log_counts, **tw_log_counts}

    # MCMC inverse
    log_target = log(6_000_000)
    print(f"\nMCMC inverse: targeting IS ≈ {int(exp(log_target)):,}  (n={N_NODES})")
    trace, best_T = mcmc_inverse(N_NODES, log_target, steps=25_000, temperature=0.5)
    best = min(trace, key=lambda x: abs(x[0] - log_target))
    print(f"  Closest: IS ≈ {int(exp(best[0])):,.0f}  (log_IS={best[0]:.3f})")
    print(f"  Degree seq: {best[1][:12]}")
    print(f"  Exact IS:  {count_independent_sets(best_T):,}")

    # ---- Plot ----
    colors = plt.cm.tab20.colors
    fig = plt.figure(figsize=(15, 10))
    gs = gridspec.GridSpec(2, 2, hspace=0.42, wspace=0.35)

    # Panel 1: KDE-smoothed distributions
    ax1 = fig.add_subplot(gs[0, :])
    all_vals = np.concatenate(list(all_log_counts.values()))
    x_grid = np.linspace(all_vals.min() - 1, all_vals.max() + 1, 500)
    for i, (name, lc) in enumerate(all_log_counts.items()):
        kde = gaussian_kde(lc, bw_method=0.25)
        ax1.fill_between(x_grid, kde(x_grid), alpha=0.30, color=colors[i])
        ax1.plot(x_grid, kde(x_grid), color=colors[i], lw=2, label=name)
    ax1.axvline(log_target, color='red', lw=1.8, linestyle=':', alpha=0.8,
                label=f"MCMC target (IS≈{int(exp(log_target)):,})")
    ax1.set_xlabel("log(IS count)", fontsize=12)
    ax1.set_ylabel("Density", fontsize=12)
    ax1.set_title(f"Distribution of log(IS count) for random graphs  (n ≈ {N_NODES})", fontsize=13)
    ax1.legend(fontsize=8.5, ncol=2)

    # Panel 2: MCMC trace
    ax2 = fig.add_subplot(gs[1, 0])
    xs = [i * 100 for i in range(len(trace))]
    ys = [t[0] for t in trace]
    ax2.plot(xs, ys, lw=0.8, color='steelblue', alpha=0.85)
    ax2.axhline(log_target, color='red', lw=1.5, linestyle='--',
                label=f"target={log_target:.2f}")
    ax2.set_xlabel("MCMC step")
    ax2.set_ylabel("log(IS count)")
    ax2.set_title(f"MCMC inverse sampler  (n={N_NODES})", fontsize=11)
    ax2.legend(fontsize=9)

    # Panel 3: spread comparison
    ax3 = fig.add_subplot(gs[1, 1])
    short = [n.split("(")[0].strip()[:22] for n in all_log_counts]
    stds  = [np.std(v) for v in all_log_counts.values()]
    means = [np.mean(v) for v in all_log_counts.values()]
    y = list(range(len(short)))
    bars = ax3.barh(y, stds, color=colors[:len(stds)], alpha=0.82)
    ax3.set_yticks(y); ax3.set_yticklabels(short, fontsize=9)
    ax3.set_xlabel("Std of log(IS count)", fontsize=11)
    ax3.set_title("Distribution spread\n(higher std = harder to invert)", fontsize=10)
    for j, (s, m) in enumerate(zip(stds, means)):
        ax3.text(s + 0.05, j, f"μ={m:.1f}", va='center', fontsize=8, color='#333')

    plt.savefig("is_distributions.png", dpi=150, bbox_inches='tight')
    print("\nSaved is_distributions.png")

# treehack

Counting independent sets on trees and bounded-treewidth graphs.

## Overview

This project provides efficient algorithms for counting independent sets (IS) on:

- **Trees** — O(n) dynamic programming on the tree structure
- **Bounded-treewidth graphs** — O(n * 2^k) DP on a tree decomposition, where k is the treewidth

It also includes tools for generating random graphs of controlled treewidth, optimization over graph families, and experimental analysis of correlations between graph invariants.

## Core Modules

| Module | Description |
|---|---|
| `counting.py` | Tree-specific IS counting via DP |
| `tw_counting.py` | General IS counting via tree decomposition DP |
| `tree_decomposition.py` | `TreeDecomposition` data structure |
| `generators.py` | Random tree generators (Prufer, Galton-Watson, named families) |
| `tw_generators.py` | Bounded-treewidth graph generators (k-trees, partial k-trees, grid graphs, series-parallel, outerplanar) |
| `optimization.py` | Optimize IS count over tree space using leaf-swap mutations |
| `verifier.py` | Standalone IS verifier with automatic tree decomposition (works on arbitrary graphs) |

## Scripts

| Script | Description |
|---|---|
| `is_calculator.py` | Standalone IS calculator for trees |
| `demo_families.py` | IS counts on named tree families (paths, stars, caterpillars, etc.) |
| `demo_distributions.py` | Compare IS count distributions across random tree models |
| `generate_dataset.py` | Generate collections of Galton-Watson trees with IS counts |
| `generate_tw_benchmark.py` | Generate benchmark dataset of bounded-treewidth graphs with IS counts |
| `experiment_correlations.py` | Correlation analysis between IS counts and graph invariants on k-trees |
| `experiment_sweep.py` | Treewidth sweep and extremal graph search |
| `test_treewidth.py` | Tests for the treewidth counting pipeline |

## Benchmark Data

- `trees.g6` / `is_counts.txt` — 10 trees in graph6 format with IS counts
- `benchmark_edgelists.txt` / `benchmark_is_counts.txt` — 50 bounded-treewidth graphs (k=1..5, n=10..40) as edgelists with IS counts

### Edgelist format

Each graph in `benchmark_edgelists.txt` is a block of lines:

```
# n=17 k=4
0 1
0 2
...
```

Graphs are separated by blank lines. The `# n=<vertices> k=<treewidth>` header identifies each graph's parameters.

## Usage

### Count IS on a tree

```python
from generators import prufer_tree
from counting import count_independent_sets

T = prufer_tree(20)
print(count_independent_sets(T))
```

### Count IS on a bounded-treewidth graph

```python
from tw_generators import random_k_tree
from tw_counting import count_independent_sets_general
import random

G, td = random_k_tree(n=30, k=3, rng=random.Random(0))
print(count_independent_sets_general(G, td))
```

### Verify IS count on any graph

```bash
python verifier.py graph.g6          # from graph6 file
echo "0 1\n1 2\n2 3" | python verifier.py --stdin  # from edgelist on stdin
```

### Generate a new benchmark

```bash
python generate_tw_benchmark.py
```

Edit the constants at the top of the script to change the number of graphs, vertex range, treewidth range, or random seed.

## Requirements

- Python 3.10+
- NetworkX
- NumPy
- Matplotlib (for experiments/demos)

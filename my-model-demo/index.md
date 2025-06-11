---
layout: default
title: DiRe-JAX - Dimensionality Reduction in JAX
---

# DiRe-JAX: Dimensionality Reduction in JAX

![teaser](assets/teaser.gif)

DiRe-JAX is a dimensionality reduction package written in JAX, offering advanced embedding capabilities with performance benchmarks against existing approaches like UMAP and tSNE.

**Authors**: A. Kolpakov and I. Rivin

## Overview
DiRe-JAX provides state-of-the-art dimensionality reduction techniques implemented in JAX for high-performance computing on CPUs, GPUs, and TPUs. The package offers advanced embedding capabilities with comprehensive benchmarking against established methods.

## Installation

### Basic Installation
```bash
pip install dire-jax
```

### Full Installation (with Utilities)
```bash
pip install dire-jax[utils]
```

> **Note**: For GPU/TPU acceleration, follow [JAX documentation](https://github.com/google/jax#installation) for hardware support.

## Quick Start

```python
from dire_jax import DiRe
from sklearn.datasets import make_blobs

# Generate sample data
features_blobs, labels_blobs = make_blobs(
    n_samples=100_000, 
    n_features=1_000, 
    centers=12, 
    random_state=42
)

# Initialize and transform
reducer_blobs = DiRe(
    dimension=2,
    n_neighbors=16,
    init_embedding_type='pca',
    # ... other parameters
)

embedding = reducer_blobs.fit_transform(features_blobs)
reducer_blobs.visualize(labels=labels_blobs, point_size=4)
```

## 🔍 Paper
Read the paper: [PDF](paper.pdf) • [arXiv](https://arxiv.org/abs/2503.03156)

## 🧠 Code
Check the code on [GitHub](https://github.com/sashakolpakov/dire-jax.git)

## 💻 Resources
- [Full Documentation](https://sashakolpakov.github.io/dire-jax/)
- [Benchmarking Notebook](https://colab.research.google.com/github/sashakolpakov/dire-jax/blob/main/tests/dire_benchmarks.ipynb)

## 🤝 Contributing
See the [contributing guide](https://sashakolpakov.github.io/dire-jax/contributing.html)

## 📄 License
Apache 2.0

## 🙏 Acknowledgement
Supported by Google Cloud Research Award #GCP19980904

## 📫 Contact
Questions? Reach out at [you@example.com](mailto:you@example.com)

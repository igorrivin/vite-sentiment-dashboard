"""
Analyze the algebraic structure of SP graphs to understand WHY they achieve all integers.

Key: series composition is matrix multiplication!

Represent a 2-terminal graph as a 2x2 matrix:
  M = [[f00, f01], [f10, f11]]

Then series(G1, G2) corresponds to M1 * M2 (matrix product).
Parallel(G1, G2) corresponds to entrywise product (Hadamard product).

Base edge: M = [[1, 1], [1, 0]]

IS count = sum of all entries = trace(M) + off-diagonal sum.

Question: what IS counts = sum(M) are achievable by products of [[1,1],[1,0]]
and Hadamard products?
"""

import numpy as np

def series(g1, g2):
    a00, a10, a01, a11 = g1
    b00, b10, b01, b11 = g2
    return (
        a00*b00 + a01*b10,
        a10*b00 + a11*b10,
        a00*b01 + a01*b11,
        a10*b01 + a11*b11
    )

def parallel(g1, g2):
    return (g1[0]*g2[0], g1[1]*g2[1], g1[2]*g2[2], g1[3]*g2[3])

def is_count(g):
    return sum(g)

base = (1, 1, 1, 0)

# Build a few small SP graphs and show their signatures
print("Small SP graph signatures (f00, f10, f01, f11) -> IS count:")
print(f"  Edge:            {base} -> {is_count(base)}")

# Series of 2 edges = path of length 2
p2 = series(base, base)
print(f"  Path(2):         {p2} -> {is_count(p2)}")

# Series of 3 edges = path of length 3
p3 = series(p2, base)
print(f"  Path(3):         {p3} -> {is_count(p3)}")

# Parallel of 2 edges = multi-edge (but simple graph: same as edge)
# Actually parallel of 2 edges gives (1,1,1,0) hadamard (1,1,1,0) = (1,1,1,0)
par2 = parallel(base, base)
print(f"  2 parallel edges: {par2} -> {is_count(par2)} (same as edge for simple graph)")

# Parallel of edge and path(2)
par_ep2 = parallel(base, p2)
print(f"  Edge || Path(2): {par_ep2} -> {is_count(par_ep2)}")

# Series of (edge||path2) and edge
sp1 = series(par_ep2, base)
print(f"  (E||P2) - E:     {sp1} -> {is_count(sp1)}")

# Let's systematically find which integers 3..50 are achievable
# and by what construction
print("\n\nFinding constructions for integers 3..30:")

# Build signatures iteratively
sigs_by_count = {}
queue = [base]
sigs_by_count[is_count(base)] = "E"

all_sigs = {"E": base}
names = {base: "E"}

def add_sig(sig, name):
    c = is_count(sig)
    if c not in sigs_by_count and c <= 100:
        sigs_by_count[c] = name
        all_sigs[name] = sig
        names[sig] = name
        return True
    return False

# Build up names for constructions
constructions = [(base, "E")]
for depth in range(6):
    new_constructions = []
    for g1, n1 in constructions:
        for g2, n2 in constructions:
            s = series(g1, g2)
            sname = f"({n1};{n2})"
            if add_sig(s, sname):
                new_constructions.append((s, sname))
            p = parallel(g1, g2)
            pname = f"({n1}||{n2})"
            if add_sig(p, pname):
                new_constructions.append((p, pname))
    constructions.extend(new_constructions)
    if len(sigs_by_count) >= 28:
        break

for n in range(3, 31):
    if n in sigs_by_count:
        print(f"  {n:3d}: {sigs_by_count[n]}")
    else:
        print(f"  {n:3d}: NOT FOUND")

# Key question: what's the structure of the (f00,f10,f01,f11) tuples?
# The matrix [[f00,f01],[f10,f11]] for series composition is just matrix multiplication.
# The base matrix is [[1,1],[1,0]] = Fibonacci matrix!
# Products of this matrix give Fibonacci numbers.
# But parallel composition (Hadamard product) breaks out of the matrix product structure.
print("\n\nPath matrices (series powers of base):")
M = base
for i in range(1, 8):
    M = series(M, base)
    print(f"  Path({i+1}): {M} -> {is_count(M)}")

# The path IS counts are: 3, 5, 8, 13, 21, 34, 55 = Fibonacci!
# Parallel with a path gives element-wise multiplication of entries.
# This creates new entry patterns that generate new IS counts.

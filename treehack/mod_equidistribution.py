"""
Check mod-m equidistribution of the IFS orbit.

Maps on Z^4 (representing 2x2 matrices as (a,b,c,d)):
  R: (a,b,c,d) -> (a+b, a, c+d, c)     [right-multiply by Fibonacci]
  P: (a,b,c,d) -> (a, b, c, 0)           [Hadamard with Fibonacci]

Starting point: v0 = (1,1,1,0)

Check:
  1. How much of (Z/mZ)^4 does the orbit cover?
  2. Does phi = a+b+c+d hit all residues mod m?
"""

def R(v, m):
    a, b, c, d = v
    return ((a+b) % m, a % m, (c+d) % m, c % m)

def P(v, m):
    a, b, c, d = v
    return (a, b, c, 0)

def explore_orbit_mod_m(m):
    """BFS to find all reachable vectors mod m from v0."""
    v0 = (1 % m, 1 % m, 1 % m, 0)
    visited = {v0}
    frontier = [v0]

    while frontier:
        new_frontier = []
        for v in frontier:
            for T in [R, P]:
                w = T(v, m)
                if w not in visited:
                    visited.add(w)
                    new_frontier.append(w)
        frontier = new_frontier

    return visited

print("=" * 70)
print("MOD-m EQUIDISTRIBUTION ANALYSIS")
print("=" * 70)

for m in [2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 17, 19, 23, 25, 29, 31]:
    orbit = explore_orbit_mod_m(m)
    phi_values = {(a+b+c+d) % m for (a,b,c,d) in orbit}
    total_4d = m**4
    print(f"\nm = {m}:")
    print(f"  Orbit size in (Z/{m}Z)^4:  {len(orbit):>8} / {total_4d:>8}  "
          f"({100*len(orbit)/total_4d:.1f}%)")
    print(f"  phi values mod {m}:        {len(phi_values):>8} / {m:>8}  "
          f"({100*len(phi_values)/m:.1f}%)"
          f"  {'ALL' if len(phi_values) == m else 'MISSING: ' + str(sorted(set(range(m)) - phi_values))}")

# Detailed view for small m
print("\n" + "=" * 70)
print("DETAILED ORBIT STRUCTURE")
print("=" * 70)

for m in [2, 3, 5, 7]:
    orbit = explore_orbit_mod_m(m)
    phi_values = {(a+b+c+d) % m for (a,b,c,d) in orbit}

    # Count vectors per phi value
    from collections import Counter
    phi_counts = Counter((a+b+c+d) % m for (a,b,c,d) in orbit)

    print(f"\nm = {m}: orbit has {len(orbit)} vectors in (Z/{m}Z)^4")
    print(f"  Vectors per phi residue:")
    for r in range(m):
        print(f"    phi ≡ {r} (mod {m}): {phi_counts.get(r, 0)} vectors")

    # What fraction of all vectors with given phi value are in orbit?
    # Total vectors in (Z/mZ)^4 with sum ≡ r: this is m^3 for each r
    # (by symmetry, fixing sum mod m leaves m^3 free choices for 3 of 4 coords)
    print(f"  Density per residue class: {phi_counts.get(0,0)}/{m**3} of same-residue vectors")

# Check: is the orbit a subgroup/coset of (Z/mZ)^4 under addition?
print("\n" + "=" * 70)
print("ORBIT ALGEBRAIC STRUCTURE")
print("=" * 70)

for m in [2, 3, 5]:
    orbit = explore_orbit_mod_m(m)
    # Check if orbit is closed under addition mod m
    is_subgroup = True
    sample_fails = 0
    for v in list(orbit)[:100]:
        for w in list(orbit)[:100]:
            s = tuple((vi + wi) % m for vi, wi in zip(v, w))
            if s not in orbit:
                is_subgroup = False
                sample_fails += 1
                if sample_fails <= 2:
                    pass  # don't print, just count
    print(f"\nm = {m}: orbit is {'an additive subgroup' if is_subgroup else 'NOT an additive subgroup'} of (Z/{m}Z)^4")

    # Check if orbit is a union of cosets of some subgroup
    # Simpler: just report the orbit size and m^4
    print(f"  |orbit| = {len(orbit)}, m^4 = {m**4}, ratio = {m**4 / len(orbit):.2f}")

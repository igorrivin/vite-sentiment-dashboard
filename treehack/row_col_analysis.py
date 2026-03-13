"""
Analyze reachable row-sum and column-sum sets of the SP bisemigroup,
test the "thick rectangle" hypothesis, and classify extreme signatures.

Uses the dot-product identity: phi(MN) = col(M) . row(N)
where col(M) = (a+c, b+d) and row(M) = (a+b, c+d).
"""

from itertools import product as cartprod

def sp_closure(max_iters=4, max_val=50000):
    """BFS closure of the Fibonacci matrix under series (matrix mult) and
    parallel (Hadamard) composition. Returns the set of all reachable
    signature tuples (a, b, c, d)."""

    # Single edge: M_E = [[1,1],[1,0]]
    seed = (1, 1, 1, 0)
    sigs = {seed}

    for iteration in range(max_iters):
        new = set()
        sig_list = list(sigs)
        for s1 in sig_list:
            for s2 in sig_list:
                a1, b1, c1, d1 = s1
                a2, b2, c2, d2 = s2

                # Series: matrix product
                sa = a1*a2 + b1*c2
                sb = a1*b2 + b1*d2
                sc = c1*a2 + d1*c2
                sd = c1*b2 + d1*d2
                if max(sa, sb, sc, sd) <= max_val:
                    new.add((sa, sb, sc, sd))

                # Parallel: Hadamard product
                ha = a1*a2
                hb = b1*b2
                hc = c1*c2
                hd = d1*d2
                if max(ha, hb, hc, hd) <= max_val:
                    new.add((ha, hb, hc, hd))

        added = new - sigs
        print(f"Iteration {iteration+1}: {len(sigs)} -> {len(sigs | new)} signatures (+{len(added)} new)")
        if not added:
            break
        sigs |= new

    return sigs


def analyze_row_col(sigs):
    """Compute reachable row-sum and column-sum vectors."""
    row_sums = set()
    col_sums = set()

    for a, b, c, d in sigs:
        row_sums.add((a + b, c + d))
        col_sums.add((a + c, b + d))

    return row_sums, col_sums


def find_rectangles(vec_set, name, max_coord=500):
    """Find the largest rectangle [2..K] x [1..K'] contained in vec_set."""
    # Check which coordinates appear
    xs = sorted(set(v[0] for v in vec_set if v[0] <= max_coord))
    ys = sorted(set(v[1] for v in vec_set if v[1] <= max_coord))

    print(f"\n{name} vectors:")
    print(f"  Total count: {len(vec_set)}")
    print(f"  Distinct x-coords (≤{max_coord}): {len(xs)}")
    print(f"  Distinct y-coords (≤{max_coord}): {len(ys)}")

    # Find largest K such that [2..K] x [1..K] is contained
    best_K = 0
    for K in range(1, max_coord + 1):
        all_in = True
        for x in range(2, K + 1):
            for y in range(1, K + 1):
                if (x, y) not in vec_set:
                    all_in = False
                    break
            if not all_in:
                break
        if all_in:
            best_K = K
        else:
            break

    print(f"  Largest K with [2..K]×[1..K] ⊆ set: K = {best_K}")

    # Check coverage of [1..N] x [1..N] for various N
    for N in [10, 20, 50, 100, 200]:
        total = N * N
        covered = sum(1 for x in range(1, N+1) for y in range(1, N+1) if (x, y) in vec_set)
        print(f"  Coverage of [1..{N}]×[1..{N}]: {covered}/{total} ({100*covered/total:.1f}%)")

    # Find gaps in small rectangles
    print(f"\n  Missing from [1..30]×[1..30]:")
    missing = []
    for x in range(1, 31):
        for y in range(1, 31):
            if (x, y) not in vec_set:
                missing.append((x, y))
    if missing:
        print(f"    {missing[:30]}{'...' if len(missing) > 30 else ''}")
    else:
        print(f"    (none)")


def analyze_dot_products(row_sums, col_sums, max_target=10000):
    """Check which integers are achievable as dot products col(M) . row(N)."""
    achievable = set()

    # Convert to lists for efficiency - only keep small vectors
    rows = [(x, y) for x, y in row_sums if x <= 1000 and y <= 1000]
    cols = [(x, y) for x, y in col_sums if x <= 1000 and y <= 1000]

    print(f"\nDot product analysis:")
    print(f"  Using {len(rows)} row vectors, {len(cols)} col vectors (coords ≤ 1000)")

    for cx, cy in cols:
        for rx, ry in rows:
            val = cx * rx + cy * ry
            if 1 <= val <= max_target:
                achievable.add(val)

    # Check coverage
    for N in [100, 500, 1000, 5000, 10000]:
        covered = len([x for x in achievable if x <= N])
        print(f"  Integers in [1..{N}] achievable as dot products: {covered}/{N} ({100*covered/N:.1f}%)")

    # Find first gap
    for n in range(1, max_target + 1):
        if n not in achievable:
            print(f"  First gap: {n}")
            break
    else:
        print(f"  No gaps in [1..{max_target}]!")


def classify_extreme_signatures(sigs):
    """Classify signatures where one or more entries is 0 or 1."""
    print("\n=== Extreme signature classification ===")

    # d=0 signatures
    d0 = [(a, b, c, d) for a, b, c, d in sigs if d == 0]
    print(f"\nd=0 signatures: {len(d0)}")
    d0_small = sorted([(a, b, c) for a, b, c, d in d0 if max(a, b, c) <= 50])
    print(f"  With entries ≤ 50: {d0_small[:20]}...")

    # b=c=1, d=0
    bc1d0 = [(a, b, c, d) for a, b, c, d in sigs if b == 1 and c == 1 and d == 0]
    print(f"\nb=c=1, d=0 signatures: {len(bc1d0)}")
    a_vals = sorted(set(a for a, _, _, _ in bc1d0))
    print(f"  a values: {a_vals[:30]}")
    # Check if all powers of 2
    powers_of_2 = {2**k for k in range(30)}
    non_pow2 = [a for a in a_vals if a not in powers_of_2]
    print(f"  Non-powers of 2: {non_pow2[:20] if non_pow2 else 'none (all powers of 2!)'}")

    # d=1
    d1 = [(a, b, c, d) for a, b, c, d in sigs if d == 1]
    print(f"\nd=1 signatures: {len(d1)}")
    d1_small = sorted(d1, key=lambda x: x[0])[:20]
    print(f"  Smallest: {d1_small}")

    # b=1
    b1 = [(a, b, c, d) for a, b, c, d in sigs if b == 1]
    print(f"\nb=1 signatures: {len(b1)}")
    b1_small = sorted(b1, key=lambda x: sum(x))[:20]
    print(f"  Smallest: {b1_small}")

    # c=1
    c1 = [(a, b, c, d) for a, b, c, d in sigs if c == 1]
    print(f"\nc=1 signatures: {len(c1)}")
    c1_small = sorted(c1, key=lambda x: sum(x))[:20]
    print(f"  Smallest: {c1_small}")

    # a=1 (exactly one IS with both s,t excluded)
    a1 = [(a, b, c, d) for a, b, c, d in sigs if a == 1]
    print(f"\na=1 signatures: {len(a1)}")
    a1_small = sorted(a1, key=lambda x: sum(x))[:20]
    print(f"  Smallest: {a1_small}")


def main():
    print("Computing SP bisemigroup closure...")
    sigs = sp_closure(max_iters=4, max_val=50000)
    print(f"\nTotal signatures: {len(sigs)}")

    # IS counts
    is_counts = set()
    for a, b, c, d in sigs:
        is_counts.add(a + b + c + d)
    print(f"Distinct IS counts: {len(is_counts)}")

    # Row and column sums
    row_sums, col_sums = analyze_row_col(sigs)

    find_rectangles(row_sums, "Row-sum", max_coord=200)
    find_rectangles(col_sums, "Column-sum", max_coord=200)

    # Dot product analysis
    analyze_dot_products(row_sums, col_sums, max_target=10000)

    # Extreme signatures
    classify_extreme_signatures(sigs)


if __name__ == "__main__":
    main()

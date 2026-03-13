"""
Deeper analysis: what are the dot-product gaps? What does the row/col set
actually look like? Can we characterize its structure?
"""

def sp_closure(max_iters=4, max_val=100000):
    seed = (1, 1, 1, 0)
    sigs = {seed}
    for iteration in range(max_iters):
        new = set()
        sig_list = list(sigs)
        for s1 in sig_list:
            for s2 in sig_list:
                a1, b1, c1, d1 = s1
                a2, b2, c2, d2 = s2
                sa = a1*a2 + b1*c2
                sb = a1*b2 + b1*d2
                sc = c1*a2 + d1*c2
                sd = c1*b2 + d1*d2
                if max(sa, sb, sc, sd) <= max_val:
                    new.add((sa, sb, sc, sd))
                ha = a1*a2
                hb = b1*b2
                hc = c1*c2
                hd = d1*d2
                if max(ha, hb, hc, hd) <= max_val:
                    new.add((ha, hb, hc, hd))
        added = new - sigs
        print(f"Iter {iteration+1}: {len(sigs)} -> {len(sigs | new)} (+{len(added)})")
        if not added:
            break
        sigs |= new
    return sigs


def main():
    print("Computing closure (max_val=100000)...")
    sigs = sp_closure(max_iters=4, max_val=100000)

    # Row and column sums
    row_sums = set()
    col_sums = set()
    for a, b, c, d in sigs:
        row_sums.add((a + b, c + d))
        col_sums.add((a + c, b + d))

    print(f"\nTotal sigs: {len(sigs)}")
    print(f"Row-sum vectors: {len(row_sums)}")
    print(f"Col-sum vectors: {len(col_sums)}")

    # Are row_sums == col_sums?
    print(f"Row sums == Col sums: {row_sums == col_sums}")

    # Dot products
    achievable = set()
    rows = list(row_sums)
    cols = list(col_sums)
    for cx, cy in cols:
        for rx, ry in rows:
            val = cx * rx + cy * ry
            if 1 <= val <= 20000:
                achievable.add(val)

    gaps = sorted(set(range(1, 20001)) - achievable)
    print(f"\nDot product gaps in [1..20000]: {len(gaps)}")
    print(f"Gaps: {gaps}")

    # Direct IS count check (not via dot product)
    is_counts = set()
    for a, b, c, d in sigs:
        is_counts.add(a + b + c + d)
    is_gaps = sorted(set(range(3, 20001)) - is_counts)
    print(f"\nDirect IS count gaps in [3..20000]: {len(is_gaps)}")
    if is_gaps:
        print(f"Gaps: {is_gaps[:50]}")

    # Structure of row-sum set
    print("\n=== Row-sum set structure ===")
    # Group by x coordinate
    by_x = {}
    for x, y in row_sums:
        if x <= 100:
            by_x.setdefault(x, []).append(y)

    for x in sorted(by_x.keys())[:20]:
        ys = sorted(by_x[x])
        if len(ys) <= 15:
            print(f"  x={x}: y in {ys}")
        else:
            print(f"  x={x}: {len(ys)} values, range [{min(ys)}, {max(ys)}]")

    # Check: is (x,y) in row_sums iff (y,x) in row_sums?
    symmetric = all((y, x) in row_sums for x, y in row_sums)
    print(f"\nRow sums symmetric (x,y) <-> (y,x): {symmetric}")

    # Check: what is the relationship between row_sums and col_sums?
    # For M_E = [[1,1],[1,0]], row(M_E) = (2,1), col(M_E) = (2,1)
    # For M_E^2 = [[2,1],[1,1]], row = (3,2), col = (3,1)
    print("\nSample signatures and their row/col sums:")
    for sig in sorted(sigs, key=lambda x: sum(x))[:10]:
        a, b, c, d = sig
        print(f"  ({a},{b},{c},{d}): row=({a+b},{c+d}), col=({a+c},{b+d}), phi={a+b+c+d}")

    # Can we express the row-sum set more simply?
    # row(M) = (a+b, c+d). Note: a+b >= c+d for many (but not all) matrices
    ratio_violations = 0
    for x, y in row_sums:
        if y > x:
            ratio_violations += 1
    print(f"\nRow sums with y > x: {ratio_violations}/{len(row_sums)}")

    # What fraction have gcd(x,y) = 1?
    from math import gcd
    coprime = sum(1 for x, y in row_sums if gcd(x, y) == 1)
    print(f"Row sums with gcd(x,y) = 1: {coprime}/{len(row_sums)} ({100*coprime/len(row_sums):.1f}%)")


if __name__ == "__main__":
    main()

"""
Carefully verify dot-product gaps at 4-iteration closure.
GPT claims additional gaps appear between 10k and 50k.
"""

def sp_closure(max_iters=4, max_val=200000):
    seed = (1, 1, 1, 0)
    sigs = {seed}
    for iteration in range(max_iters):
        new = set()
        sig_list = list(sigs)
        for s1 in sig_list:
            for s2 in sig_list:
                a1, b1, c1, d1 = s1
                a2, b2, c2, d2 = s2
                sa = a1*a2+b1*c2; sb = a1*b2+b1*d2
                sc = c1*a2+d1*c2; sd = c1*b2+d1*d2
                if max(sa,sb,sc,sd) <= max_val:
                    new.add((sa,sb,sc,sd))
                ha = a1*a2; hb = b1*b2; hc = c1*c2; hd = d1*d2
                if max(ha,hb,hc,hd) <= max_val:
                    new.add((ha,hb,hc,hd))
        added = new - sigs
        print(f"Iter {iteration+1}: {len(sigs)} -> {len(sigs | new)} (+{len(added)})")
        if not added: break
        sigs |= new
    return sigs


def main():
    sigs = sp_closure(4, 200000)
    print(f"\nTotal sigs: {len(sigs)}")

    row_sums = set()
    col_sums = set()
    for a, b, c, d in sigs:
        row_sums.add((a+b, c+d))
        col_sums.add((a+c, b+d))

    print(f"Row vecs: {len(row_sums)}, Col vecs: {len(col_sums)}")
    print(f"R == C: {row_sums == col_sums}")

    # Compute dot products carefully
    # Use ALL pairs, not filtering by coord size
    achievable = set()
    row_list = list(row_sums)
    col_list = list(col_sums)

    print(f"\nComputing dot products (may take a while)...")
    for i, (cx, cy) in enumerate(col_list):
        for rx, ry in row_list:
            val = cx*rx + cy*ry
            if 1 <= val <= 50000:
                achievable.add(val)

    gaps = sorted(set(range(1, 50001)) - achievable)
    print(f"\nDot product gaps in [1..50000]: {len(gaps)}")
    print(f"Gaps: {gaps[:50]}")
    if len(gaps) > 50:
        print(f"  ... and {len(gaps)-50} more")

    # Check specific ranges
    for lo, hi in [(1, 100), (1, 1000), (1, 10000), (10001, 20000),
                   (20001, 30000), (30001, 40000), (40001, 50000)]:
        range_gaps = [g for g in gaps if lo <= g <= hi]
        print(f"  [{lo}..{hi}]: {len(range_gaps)} gaps")

    # Also check: what's the max row/col sum coordinate?
    max_rc = max(max(x, y) for x, y in row_sums)
    print(f"\nMax coordinate in row/col sums: {max_rc}")

    # The issue might be that we need vectors with large coordinates
    # to produce large dot products. Check: what's the largest
    # dot product achievable?
    max_dot = max(cx*rx + cy*ry for cx, cy in col_list for rx, ry in row_list)
    print(f"Max achievable dot product: {max_dot}")


if __name__ == "__main__":
    main()

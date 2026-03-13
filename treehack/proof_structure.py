"""
Final structural analysis: with 4-iteration closure, identify
what makes the dot product surjective.

Hypothesis: row sums contain enough vectors along lines
ax + by = c to make consecutive integers representable.
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
                sa = a1*a2+b1*c2; sb = a1*b2+b1*d2
                sc = c1*a2+d1*c2; sd = c1*b2+d1*d2
                if max(sa,sb,sc,sd) <= max_val:
                    new.add((sa,sb,sc,sd))
                ha = a1*a2; hb = b1*b2; hc = c1*c2; hd = d1*d2
                if max(ha,hb,hc,hd) <= max_val:
                    new.add((ha,hb,hc,hd))
        added = new - sigs
        if not added: break
        sigs |= new
    return sigs


def main():
    sigs = sp_closure(4, 100000)
    row_sums = set()
    col_sums = set()
    for a, b, c, d in sigs:
        row_sums.add((a+b, c+d))
        col_sums.add((a+c, b+d))

    print(f"Sigs: {len(sigs)}, Row vecs: {len(row_sums)}")

    # For each small col vector, find the threshold where
    # dot products become consecutive
    print("\n=== Per-column-vector consecutive threshold ===")
    for cx, cy in sorted(col_sums):
        if cx > 8 or cy > 5:
            continue
        dots = sorted(set(cx*rx + cy*ry for rx, ry in row_sums
                         if 1 <= cx*rx + cy*ry <= 1000))
        if not dots:
            continue
        # Find where consecutive coverage starts (50+ consecutive)
        thresh = None
        for i in range(len(dots)):
            consec = True
            for j in range(i, min(i+50, len(dots)-1)):
                if dots[j+1] != dots[j]+1:
                    consec = False
                    break
            if consec and i+50 <= len(dots):
                thresh = dots[i]
                break
        if thresh:
            print(f"  col=({cx},{cy}): consecutive from {thresh} "
                  f"({len(dots)} values in [1..1000])")

    # The KEY question for a proof:
    # Which SPECIFIC row-sum vectors, combined with col (2,1),
    # give all integers >= some threshold?
    #
    # col=(2,1): dot = 2x + y.
    # We need: for each target t, there exists (x,y) in row_sums
    # with 2x + y = t.
    #
    # Since y >= 1 and x >= 2 typically, we need t >= 5.
    # For each t, solutions are (x, t-2x) with x <= (t-1)//2 and t-2x >= 1.

    # Let's see which (x, y) pairs in row_sums have small y
    print("\n=== Row sum structure by y-coordinate ===")
    for y in range(1, 11):
        xs = sorted([x for x2, y2 in row_sums if y2 == y and x2 <= 500
                     for x in [x2]])
        if xs:
            # Compute gaps between consecutive x values
            if len(xs) > 1:
                max_gap = max(xs[i+1]-xs[i] for i in range(len(xs)-1))
            else:
                max_gap = "N/A"
            print(f"  y={y}: {len(xs)} x-values in [1..500], "
                  f"range [{min(xs)},{max(xs)}], max gap={max_gap}")

    # Now the interval growth question:
    # Start with all IS counts from iteration 3 (the "seed interval")
    # Then show that series compositions (dot products) extend it.
    sigs3 = sp_closure(3, 10000)
    is3 = set(sum(s) for s in sigs3)
    print(f"\n=== Interval growth ===")
    print(f"Iteration 3: {len(sigs3)} sigs, "
          f"{len([x for x in is3 if 3 <= x <= 100])} IS counts in [3..100]")
    # What consecutive interval does iteration 3 cover?
    for n in range(3, 10001):
        if n not in is3:
            print(f"  First gap at iter 3: {n}")
            break

    is4 = set(sum(s) for s in sigs)
    for n in range(3, 100001):
        if n not in is4:
            print(f"  First gap at iter 4: {n}")
            break

    # The growth: iter 3 covers [3, ?], iter 4 covers [3, ?]
    # What's the growth factor?

    # Alternative: just look at the dot product achievability
    # which uses row/col sums from iter 4
    dot_achievable = set()
    for cx, cy in col_sums:
        if cx > 5000 or cy > 5000:
            continue
        for rx, ry in row_sums:
            val = cx*rx + cy*ry
            if 1 <= val <= 50000:
                dot_achievable.add(val)
    for n in range(5, 50001):
        if n not in dot_achievable:
            print(f"  First dot-product gap (from iter 4 row/col): {n}")
            break
    else:
        print(f"  No dot-product gaps in [5..50000]!")

    # Verify that 3, 4 are directly achievable
    print(f"\n  3 in direct IS: {3 in is4}")
    print(f"  4 in direct IS: {4 in is4}")

    # PROOF SKETCH:
    # 1. The bisemigroup closure after 4 iterations directly achieves
    #    all integers 3..N for some N.
    # 2. The row/col sum sets from this closure have enough structure
    #    that their dot products cover all integers >= 5.
    # 3. Therefore, series compositions of bisemigroup elements
    #    achieve all integers >= 5, and 3, 4 are achieved directly.

    # The question is whether we can make step 2 INDUCTIVE
    # (prove that more iterations always extend the interval).

    # Key structural property: what row vectors come from
    # EXPLICIT, provable SP constructions?
    print("\n=== Provable row-sum vectors ===")
    # Path P_n (series of n edges): M_E^n has entries F_{n+1}, F_n, F_n, F_{n-1}
    # row sum = (F_{n+1}+F_n, F_n+F_{n-1}) = (F_{n+2}, F_{n+1})
    # So paths give row sums (F_{n+2}, F_{n+1}) for all n >= 1.
    fibs = [1, 1]
    for i in range(30):
        fibs.append(fibs[-1] + fibs[-2])

    print("  From paths P_n: row sums (F_{n+2}, F_{n+1}):")
    path_rows = []
    for n in range(1, 15):
        r = (fibs[n+1], fibs[n])
        path_rows.append(r)
        in_set = r in row_sums
        print(f"    n={n}: ({fibs[n+1]}, {fibs[n]}) {'✓' if in_set else '✗'}")

    # Parallel of two paths: Hadamard(M_E^a, M_E^b)
    # = (F_{a+1}*F_{b+1}, F_a*F_b, F_a*F_b, F_{a-1}*F_{b-1})
    # row sum = (F_{a+1}*F_{b+1} + F_a*F_b, F_a*F_b + F_{a-1}*F_{b-1})
    print("\n  From parallel of two paths (Hadamard of M_E^a, M_E^b):")
    for a in range(1, 8):
        for b in range(a, 8):
            r0 = fibs[a]*fibs[b] + fibs[a-1]*fibs[b-1]  # wait, need to be careful
            # M_E^a = (F_{a+1}, F_a, F_a, F_{a-1})
            # M_E^b = (F_{b+1}, F_b, F_b, F_{b-1})
            # Hadamard: (F_{a+1}F_{b+1}, F_aF_b, F_aF_b, F_{a-1}F_{b-1})
            h = (fibs[a]*fibs[b], fibs[a-1]*fibs[b-1],
                 fibs[a-1]*fibs[b-1], max(0, fibs[a-2]*fibs[b-2]) if a>=2 and b>=2 else 0)
            # Wait, let me redo. M_E^n entries:
            # (F_{n+1}, F_n; F_n, F_{n-1})
            # For n=1: (1,1,1,0). F_2=1, F_1=1, F_0=0. Check.
            # For n=2: (2,1,1,1). F_3=2, F_2=1, F_1=1. Check.
            sig_a = (fibs[a+1], fibs[a], fibs[a], fibs[a-1])
            sig_b = (fibs[b+1], fibs[b], fibs[b], fibs[b-1])
            had = (sig_a[0]*sig_b[0], sig_a[1]*sig_b[1],
                   sig_a[2]*sig_b[2], sig_a[3]*sig_b[3])
            rs = (had[0]+had[1], had[2]+had[3])
            if a <= 5 and b <= 5:
                in_set = rs in row_sums
                print(f"    (a,b)=({a},{b}): row sum = {rs} {'✓' if in_set else '✗'}")


if __name__ == "__main__":
    main()

"""
Analyze WHY dot products of the row/col sum sets cover all integers >= 5.

Key insight: we don't need thick rectangles. We need enough vectors
along different "slopes" so that the dot products fill Z.

Approach: for dot product x1*y1 + x2*y2 = t, if we have vectors
(x1, x2) and (y1, y2) with enough variety, we get all targets.

The simplest sufficient condition: if the set contains (a, 1) and (1, b)
for enough a, b, then dot products give a*1 + 1*b = a + b (all sums)
and a*y1 + 1*y2 for various (y1, y2).
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
        if not added:
            break
        sigs |= new
    return sigs


def main():
    sigs = sp_closure(max_iters=4, max_val=100000)
    row_sums = set()
    col_sums = set()
    for a, b, c, d in sigs:
        row_sums.add((a + b, c + d))
        col_sums.add((a + c, b + d))

    print("=== Structure of vectors with one coordinate small ===")

    # Vectors of the form (x, 1)
    x1_rows = sorted([x for x, y in row_sums if y == 1])
    x1_cols = sorted([x for x, y in col_sums if y == 1])
    print(f"Row sums (x, 1): x in {x1_rows[:30]}...")
    print(f"Col sums (x, 1): x in {x1_cols[:30]}...")

    # Vectors of the form (x, 2)
    x2_rows = sorted([x for x, y in row_sums if y == 2])
    x2_cols = sorted([x for x, y in col_sums if y == 2])
    print(f"Row sums (x, 2): x in {x2_rows[:30]}...")
    print(f"Col sums (x, 2): x in {x2_cols[:30]}...")

    # Vectors of the form (x, 3)
    x3_rows = sorted([x for x, y in row_sums if y == 3])
    print(f"Row sums (x, 3): x in {x3_rows[:30]}...")

    # Key observation: if we have (n, 1) in col_sums and (1, m) in row_sums,
    # then dot product = n*1 + 1*m = n + m. So we get all sums n + m.
    # But we don't have (1, m) in row_sums since y <= x always...

    # Let's check: for vectors (a, b) in the set, what's gcd(a, b)?
    print("\n=== GCD structure ===")
    from math import gcd
    gcd_counts = {}
    for x, y in row_sums:
        if x <= 100 and y <= 100:
            g = gcd(x, y)
            gcd_counts[g] = gcd_counts.get(g, 0) + 1
    print(f"GCD distribution of row sums (coords ≤ 100): {sorted(gcd_counts.items())}")

    # Key for dot product surjectivity:
    # If we have vectors (a, b) and (c, d) with gcd(a,b) = gcd(c,d) = 1
    # and they span Z^2, then dot products with ALL vectors give all integers
    # above some threshold.

    # More concretely: (a,b).(x,y) = t has solutions (x,y) in Z^2 for all t
    # iff gcd(a,b) | t, i.e., iff gcd(a,b) = 1.

    # So if we have (a,b) in col_sums with gcd(a,b) = 1, then
    # {(a,b).(x,y) : (x,y) in row_sums} contains all integers >= some threshold
    # PROVIDED row_sums is "dense enough" in the half-plane a*x + b*y >= 0.

    print("\n=== Consecutive differences along specific col vectors ===")
    # For a fixed col vector (a, b), what are the achievable dot products?
    test_cols = [(2, 1), (3, 1), (3, 2), (5, 1), (5, 2), (5, 3)]
    for cx, cy in test_cols:
        if (cx, cy) not in col_sums:
            continue
        dots = sorted(set(cx * rx + cy * ry for rx, ry in row_sums
                         if 1 <= cx * rx + cy * ry <= 500))
        # Check consecutive coverage
        if dots:
            # Find gaps
            gaps = [dots[i+1] - dots[i] for i in range(len(dots)-1) if dots[i+1] - dots[i] > 1]
            max_consec_start = min(dots)
            for i in range(len(dots)-1):
                if dots[i+1] != dots[i] + 1:
                    max_consec_start = dots[i+1]
                    break
            # Find where consecutive coverage starts
            consec_from = None
            for start_idx in range(len(dots)):
                all_consec = True
                for i in range(start_idx, min(start_idx + 50, len(dots)-1)):
                    if dots[i+1] != dots[i] + 1:
                        all_consec = False
                        break
                if all_consec and start_idx + 50 <= len(dots):
                    consec_from = dots[start_idx]
                    break
            print(f"  col=({cx},{cy}): {len(dots)} values in [1..500], "
                  f"consecutive from {consec_from}")

    # The REAL proof strategy: use the Chicken McNugget / Sylvester-Frobenius theorem.
    # If we have two coprime values a, b achievable as dot products (a,0).(x,y)
    # and (0,b).(x,y), then all integers >= (a-1)(b-1) are achievable as
    # non-negative integer combinations.
    # But our situation is richer: we have MANY vectors.

    print("\n=== Frobenius-style analysis ===")
    # For col vector (2, 1), the achievable dot products with row sums
    # are 2*x + y for (x,y) in row_sums.
    # Since (2,1) and (3,1) are both in col_sums, and they have
    # determinant 2*1 - 3*1 = -1, we can represent ANY target:
    # a*(2,1) + b*(3,1) = (2a+3b, a+b) -> dot with (x,y) = (2a+3b)*x + (a+b)*y
    # Hmm, that's not quite right since we're dotting col with row.

    # Simpler: if (2,1) in col_sums, then {2x+y : (x,y) in row_sums} is our set.
    # If (3,2) in col_sums, then {3x+2y : (x,y) in row_sums} is another set.
    # The UNION of all these sets (over all col vectors) is the full achievable set.

    # For the (2,1) col vector: we need 2x + y = t.
    # If row_sums contains (x, t-2x) for some x, we're done.
    # Since row_sums is (relatively) dense, this should work for most t.

    # Let's verify: for each target t in [5..100], which col vectors work?
    print("  For each target t, how many col vectors can produce it:")
    for t in [10, 20, 50, 100, 200]:
        count = 0
        for cx, cy in col_sums:
            for rx, ry in row_sums:
                if cx * rx + cy * ry == t:
                    count += 1
                    break
        # This is slow; let's just check achievability
    # Actually, let's count representations for specific targets
    print("\n=== Representation count for specific targets ===")
    for t in [10, 15, 20, 50, 100, 500, 1000]:
        reps = 0
        for cx, cy in col_sums:
            if cx > t or cy > t:
                continue
            for rx, ry in row_sums:
                if cx * rx + cy * ry == t:
                    reps += 1
        print(f"  t={t}: {reps} representations as col.row")

    # Key structural finding: what pairs (x, y) with x >= y >= 1
    # are in the row sum set for CONSECUTIVE x?
    print("\n=== Consecutive x-values in row sums (y=1,2,3) ===")
    for y_fixed in [1, 2, 3, 5]:
        xs = sorted([x for x, y in row_sums if y == y_fixed and x <= 200])
        if xs:
            # Find runs of consecutive x
            runs = []
            start = xs[0]
            for i in range(1, len(xs)):
                if xs[i] != xs[i-1] + 1:
                    runs.append((start, xs[i-1]))
                    start = xs[i]
            runs.append((start, xs[-1]))
            long_runs = [(a, b) for a, b in runs if b - a >= 2]
            print(f"  y={y_fixed}: {len(xs)} x-values, "
                  f"longest consecutive runs: {long_runs[:5]}")


if __name__ == "__main__":
    main()

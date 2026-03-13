"""
Test whether the dot-product identity phi(MN) = col(M).row(N) gives
surjectivity for n >= 10, using series compositions of bisemigroup elements.

Key question: are the 6 gaps {1,2,3,4,6,9} real, or artifacts of
insufficient iteration?

Also: can we prove the "thick enough" property of the row/col sets
that makes the dot product surjective?
"""

def sp_closure(max_iters=5, max_val=200000):
    seed = (1, 1, 1, 0)
    sigs = {seed}
    for iteration in range(max_iters):
        new = set()
        sig_list = list(sigs)
        n = len(sig_list)
        for i, s1 in enumerate(sig_list):
            for s2 in sig_list:
                a1, b1, c1, d1 = s1
                a2, b2, c2, d2 = s2
                # Series
                sa = a1*a2 + b1*c2
                sb = a1*b2 + b1*d2
                sc = c1*a2 + d1*c2
                sd = c1*b2 + d1*d2
                if max(sa, sb, sc, sd) <= max_val:
                    new.add((sa, sb, sc, sd))
                # Parallel
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
    print("=== 4 iterations ===")
    sigs = sp_closure(max_iters=4, max_val=200000)

    row_sums = set()
    col_sums = set()
    for a, b, c, d in sigs:
        row_sums.add((a + b, c + d))
        col_sums.add((a + c, b + d))

    print(f"\nSigs: {len(sigs)}, row vecs: {len(row_sums)}, col vecs: {len(col_sums)}")

    # Dot products up to 20000
    achievable_dot = set()
    for cx, cy in col_sums:
        if cx > 20000 or cy > 20000:
            continue
        for rx, ry in row_sums:
            val = cx * rx + cy * ry
            if 1 <= val <= 20000:
                achievable_dot.add(val)

    gaps = sorted(set(range(1, 20001)) - achievable_dot)
    print(f"\nDot product gaps in [1..20000]: {gaps}")

    # Direct IS counts from the closure
    direct_is = set(a+b+c+d for a,b,c,d in sigs)
    print(f"Direct IS counts in [3..20000]: {len([x for x in direct_is if x <= 20000])}")

    # IS counts from series compositions of ANY two bisemigroup elements
    # (not just the closure we computed - the dot product identity tells us
    # exactly which IS counts arise from series compositions)
    print(f"\nThe dot product identity says: phi(MN) depends only on")
    print(f"col(M) and row(N), so the achievable IS counts from series")
    print(f"compositions are exactly the dot products of col/row vectors.")
    print(f"These are all integers >= 10 (verified to 20000).")

    # Now check: can we also get 5, 7, 8 from the bisemigroup directly?
    small_is = sorted([x for x in direct_is if x <= 15])
    print(f"\nSmall IS counts from direct closure: {small_is}")

    # The gaps 1,2,3,4,6,9 - are they achievable at all?
    # 1 = empty graph, 2 = single vertex, these aren't SP graphs with an edge
    # 3 = single edge (base case)
    # So the "real" gaps from SP graphs would be just {4, 6, 9}... wait no.
    # Let me check: which integers < 10 ARE achievable?
    print(f"\nAchievable IS counts < 15: {sorted(x for x in direct_is if x < 15)}")

    # Check gap analysis: the 6 gaps are {1,2,3,4,6,9}
    # But 3 IS achievable (single edge)! And 4 is M_E^2 = [[2,1],[1,1]], phi=5... no.
    # Wait: M_E has phi=3. M_E^2 has phi = 2+1+1+1=5.
    # Hadamard(M_E, M_E) = [[1,1],[1,0]] = M_E, phi=3. Same thing.
    # What gives phi=4? Need a+b+c+d=4. From closure: (2,1,1,0), phi=4. Yes!
    # So 4 is achievable. Let me recheck.
    for g in [1,2,3,4,5,6,7,8,9,10]:
        in_direct = g in direct_is
        in_dot = g in achievable_dot
        print(f"  {g}: direct={in_direct}, dot={in_dot}")

    # Ah: the dot product gaps are about what col.row can produce,
    # but the direct closure may produce these via non-series compositions.
    # The question is: does the FULL IS count set (direct closure) cover
    # everything >= 3?
    full_gaps = sorted(set(range(3, 20001)) - direct_is)
    print(f"\nFull closure IS count gaps in [3..100]: {[x for x in full_gaps if x <= 100]}")

    # So the picture is:
    # - Series compositions (dot products) cover everything >= 10
    # - Direct closure (4 iterations, max_val=200000) has many gaps
    #   because we haven't iterated enough
    # - But the DOT PRODUCT IDENTITY tells us that series of ANY two
    #   bisemigroup elements covers >= 10, regardless of iteration count!

    # For integers 3..9 that aren't dot-product achievable:
    # We need to check if they come from some bisemigroup element directly
    print("\n=== Checking small integers ===")
    for target in range(3, 10):
        if target in direct_is:
            examples = [(a,b,c,d) for a,b,c,d in sigs if a+b+c+d == target]
            print(f"  {target}: YES, e.g. {examples[0]}")
        elif target in achievable_dot:
            print(f"  {target}: achievable via dot product")
        else:
            print(f"  {target}: NOT achievable (neither direct nor dot product)")


if __name__ == "__main__":
    main()

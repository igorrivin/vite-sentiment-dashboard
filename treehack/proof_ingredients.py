"""
Identify the minimal set of bisemigroup elements needed to prove surjectivity.

Strategy: find a SMALL explicit set of signature matrices such that
their row/col sums produce all integers >= some threshold T via dot products,
then verify that integers < T are directly achievable.
"""

def mat_mult(s1, s2):
    a1, b1, c1, d1 = s1
    a2, b2, c2, d2 = s2
    return (a1*a2+b1*c2, a1*b2+b1*d2, c1*a2+d1*c2, c1*b2+d1*d2)

def had_mult(s1, s2):
    return (s1[0]*s2[0], s1[1]*s2[1], s1[2]*s2[2], s1[3]*s2[3])

def phi(s):
    return sum(s)


def main():
    E = (1, 1, 1, 0)  # M_E

    # Build a small explicit collection
    # Iteration 1: E with E
    E2 = mat_mult(E, E)   # (2,1,1,1) = path of length 2
    EhE = had_mult(E, E)  # (1,1,1,0) = E again (idempotent!)
    print(f"E = {E}, phi={phi(E)}")
    print(f"E^2 = {E2}, phi={phi(E2)}")

    # Iteration 2: combine E and E2
    E3 = mat_mult(E2, E)  # (3,2,2,1)
    E2h = had_mult(E2, E) # (2,1,1,0)
    hE2 = had_mult(E, E2) # (2,1,1,0) same
    print(f"E^3 = {E3}, phi={phi(E3)}")
    print(f"E^2 ○ E = {E2h}, phi={phi(E2h)}")

    # Build up to ~20 carefully chosen elements
    elements = {E}
    queue = [E]
    for _ in range(3):
        new_els = set()
        el_list = list(elements)
        for s1 in el_list:
            for s2 in el_list:
                for op in [mat_mult, had_mult]:
                    r = op(s1, s2)
                    if max(r) <= 10000 and r not in elements:
                        new_els.add(r)
        elements |= new_els

    print(f"\n3-iteration closure: {len(elements)} elements")

    # Get row/col sums
    row_sums = set()
    col_sums = set()
    for a, b, c, d in elements:
        row_sums.add((a+b, c+d))
        col_sums.add((a+c, b+d))

    print(f"Row sum vectors: {len(row_sums)}")
    print(f"Col sum vectors: {len(col_sums)}")

    # For a PROOF, we want to identify which specific vectors
    # combine to give surjectivity.
    # Key: find two col vectors (a1,b1) and (a2,b2) such that
    # gcd(a1*b2 - a2*b1) = 1 (they form a basis of Z^2),
    # and there are enough row vectors in the "cone" they define.

    # Actually, the simplest approach: find col vectors (n, 1) for
    # consecutive n. Then dot with row vector (1, k) gives n + k.
    # But (1, k) may not be in row_sums (since x >= y always).

    # Better: use col vector (2, 1) and row vectors (x, y).
    # Dot product = 2x + y.
    # If row_sums contains (x, y) for consecutive values of 2x+y,
    # we get all integers.

    # Which row vectors have 2x + y = t for each t?
    print("\n=== Representations as 2x+y from row sums ===")
    from_21 = {}
    for x, y in row_sums:
        t = 2*x + y
        if t <= 200:
            from_21.setdefault(t, []).append((x, y))

    # Find the first t not achievable
    for t in range(1, 201):
        if t not in from_21:
            print(f"  First gap in 2x+y: t={t}")
            break

    # Check: what about 3x + y? (from col vector (3, 1))
    from_31 = {}
    for x, y in row_sums:
        t = 3*x + y
        if t <= 200:
            from_31.setdefault(t, []).append((x, y))
    for t in range(1, 201):
        if t not in from_31:
            print(f"  First gap in 3x+y: t={t}")
            break

    # Check: what about 3x + 2y? (from col vector (3, 2))
    from_32 = {}
    for x, y in row_sums:
        t = 3*x + 2*y
        if t <= 200:
            from_32.setdefault(t, []).append((x, y))
    for t in range(1, 201):
        if t not in from_32:
            print(f"  First gap in 3x+2y: t={t}")
            break

    # Union of all three
    all_achievable = set()
    for x, y in row_sums:
        for cx, cy in [(2,1), (3,1), (3,2)]:
            if (cx, cy) in col_sums:
                t = cx*x + cy*y
                if 1 <= t <= 200:
                    all_achievable.add(t)
    gaps = sorted(set(range(1, 201)) - all_achievable)
    print(f"  Gaps using just col vectors (2,1),(3,1),(3,2): {gaps}")

    # Try with more col vectors
    small_cols = [(cx,cy) for cx,cy in col_sums if cx <= 10 and cy <= 10]
    all_achievable2 = set()
    for x, y in row_sums:
        for cx, cy in small_cols:
            t = cx*x + cy*y
            if 1 <= t <= 200:
                all_achievable2.add(t)
    gaps2 = sorted(set(range(1, 201)) - all_achievable2)
    print(f"  Gaps using all col vectors with coords ≤ 10: {gaps2}")

    # Now the key structural question: can we find a FINITE set of
    # row vectors and col vectors that provably covers all integers >= T?
    print("\n=== Minimal generating set analysis ===")

    # If we have row vectors (a, 1) for a in some set A,
    # and col vector (2, 1), then we get {2a + 1 : a in A} = odd numbers
    # If we also have col vector (3, 1), we get {3a + 1 : a in A}
    # The union of {2a+1 : a in A} and {3a+1 : a in A} covers...
    # With A = {2,3,5,8,...} (from the actual data):
    A = sorted([x for x, y in row_sums if y == 1])
    print(f"  Row vectors (a, 1): a in {A}")

    from_2a1 = {2*a + 1 for a in A if 2*a+1 <= 500}
    from_3a1 = {3*a + 1 for a in A if 3*a+1 <= 500}
    union = from_2a1 | from_3a1
    gaps = sorted(set(range(5, 100)) - union)
    print(f"  Gaps in {{2a+1}} ∪ {{3a+1}} for a in A, range [5..100]: {gaps}")

    # What about row vectors (a, 2)?
    B = sorted([x for x, y in row_sums if y == 2 and x <= 200])
    print(f"  Row vectors (a, 2): a in {B}")

    from_2a2 = {2*a + 2 for a in B if 2*a+2 <= 500}
    from_3a2 = {3*a + 2 for a in B if 3*a+2 <= 500}
    union2 = from_2a2 | from_3a2 | from_2a1 | from_3a1
    gaps2 = sorted(set(range(5, 100)) - union2)
    print(f"  Adding (a,2) rows: gaps in [5..100]: {gaps2}")

    # Also add row vectors (a, 3)
    C = sorted([x for x, y in row_sums if y == 3 and x <= 200])
    from_2a3 = {2*a + 3 for a in C if 2*a+3 <= 500}
    from_3a3 = {3*a + 3 for a in C if 3*a+3 <= 500}
    union3 = union2 | from_2a3 | from_3a3
    gaps3 = sorted(set(range(5, 100)) - union3)
    print(f"  Adding (a,3) rows: gaps in [5..100]: {gaps3}")

    # With col vector (3,2): dot = 3a + 2b for row (a,b)
    from_32_all = set()
    for a, b in row_sums:
        if b <= 5:
            t = 3*a + 2*b
            if t <= 500:
                from_32_all.add(t)
    union4 = union3 | from_32_all
    gaps4 = sorted(set(range(5, 100)) - union4)
    print(f"  Adding col (3,2) . (a, b≤5): gaps in [5..100]: {gaps4}")

    # What about using BOTH series AND the direct IS count for small values?
    direct_is = set(phi(s) for s in elements)
    union5 = union4 | direct_is
    gaps5 = sorted(set(range(3, 100)) - union5)
    print(f"  Adding direct IS counts: gaps in [3..100]: {gaps5}")


if __name__ == "__main__":
    main()

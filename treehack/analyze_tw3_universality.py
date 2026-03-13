"""
Analyze whether GPT's approach can realize ANY positive integer as an
independent set count with treewidth <= 3.

Key operations:
1. Disjoint union: IS counts multiply, tw = max
2. Universal vertex (connect new v to all of G): IS -> IS(G) + 1, tw -> tw + 1
3. Combine gadget: Comb(A,B) has IS = (IS(A)+1)(IS(B)+1) - 1, tw -> max(tw(A),tw(B)) + 1

Strategy: build achievable sets layer by layer.
"""

from functools import lru_cache
from collections import defaultdict

LIMIT = 200  # check all integers up to this


def multiplicative_closure(base_set, limit):
    """Close a set under multiplication, up to limit."""
    achievable = set(base_set)
    changed = True
    while changed:
        changed = False
        new = set()
        items = sorted(achievable)
        for a in items:
            if a > limit:
                break
            for b in items:
                if b > limit:
                    break
                p = a * b
                if p <= limit and p not in achievable:
                    new.add(p)
        if new:
            achievable |= new
            changed = True
    return achievable


def tree_is_counts(max_n=20):
    """Enumerate IS counts of all trees up to max_n vertices using DP."""
    # Generate all unlabeled trees is hard; instead enumerate IS counts
    # achievable by the tree DP recurrence.
    # For a tree rooted at v with children c1,...,ck:
    #   a(v) = prod b(ci)     [v included]
    #   b(v) = prod (a(ci) + b(ci))  [v excluded]
    #   IS = a(root) + b(root)
    #
    # Represent each tree by its (a, b) pair. Build all achievable pairs.

    # Base: leaf has (a=1, b=1), IS=2
    # We build trees by combining subtrees as children of a new root.

    pairs = {(1, 1)}  # leaf
    is_counts = {2}   # leaf IS count

    for iteration in range(max_n):
        new_pairs = set()
        pairs_list = sorted(pairs)

        # A root with children whose (a,b) pairs are in pairs_list
        # Try combining 1, 2, or 3 children (covers most interesting cases)
        for p1 in pairs_list:
            a1, b1 = p1
            # Single child
            a_root = b1
            b_root = a1 + b1
            new_pairs.add((a_root, b_root))
            is_counts.add(a_root + b_root)

            for p2 in pairs_list:
                a2, b2 = p2
                a_root = b1 * b2
                b_root = (a1 + b1) * (a2 + b2)
                if a_root + b_root <= 10**9:  # don't blow up
                    new_pairs.add((a_root, b_root))
                    is_counts.add(a_root + b_root)

                for p3 in pairs_list:
                    a3, b3 = p3
                    a_root = b1 * b2 * b3
                    b_root = (a1 + b1) * (a2 + b2) * (a3 + b3)
                    if a_root + b_root <= 10**9:
                        new_pairs.add((a_root, b_root))
                        is_counts.add(a_root + b_root)

        old_size = len(pairs)
        pairs |= new_pairs
        if len(pairs) == old_size:
            break

    return is_counts


def cycle_is_counts(max_n=50):
    """IS counts of cycles C_n (n >= 3). Lucas numbers."""
    counts = set()
    # i(C_n) = L_n (Lucas numbers)
    # L_3=4, L_4=7, L_5=11, L_6=18, ...
    a, b = 2, 1  # L_1=1, L_2=3 ... actually let me just compute
    # C_3 (triangle): IS = {},{1},{2},{3} = 4
    # C_4: IS = {},{1},{2},{3},{4},{1,3},{2,4} = 7
    # C_n: i(C_n) = i(P_{n-1}) + i(P_{n-3}) = F_{n+1} + F_{n-1} = L_n
    # where F is Fibonacci with F_1=1,F_2=1 and L is Lucas with L_1=1,L_2=3
    fibs = [1, 1]
    for i in range(100):
        fibs.append(fibs[-1] + fibs[-2])

    for n in range(3, max_n + 1):
        lucas_n = fibs[n + 1] + fibs[n - 1]  # L_n = F_{n+1} + F_{n-1}
        counts.add(lucas_n)
    return counts


print("=" * 60)
print("TREEWIDTH LAYER ANALYSIS")
print("=" * 60)

# Layer 0: independent sets only, IS = 2^n
tw0_base = {2**n for n in range(0, 30) if 2**n <= LIMIT}
tw0 = multiplicative_closure(tw0_base, LIMIT)  # still just powers of 2
print(f"\ntw=0 achievable (up to {LIMIT}): {sorted(n for n in tw0 if n <= LIMIT)}")

# Layer 1: forests (trees + disjoint union)
# Trees include paths (Fibonacci IS counts) and all other trees
tree_is = tree_is_counts(15)
tw1_base = tw0 | {n for n in tree_is if n <= LIMIT}
tw1 = multiplicative_closure(tw1_base, LIMIT)
missing_tw1 = sorted(n for n in range(1, LIMIT + 1) if n not in tw1)
print(f"\ntw<=1 achievable count (up to {LIMIT}): {sum(1 for n in tw1 if 1 <= n <= LIMIT)}/{LIMIT}")
print(f"tw<=1 missing: {missing_tw1[:30]}{'...' if len(missing_tw1) > 30 else ''}")

# Layer 2: tw<=1 + universal vertex (+1) + cycles + series-parallel + disjoint union
# Universal vertex on tw<=1 graph: IS(G)+1, tw<=2
tw2_base = tw1 | {n + 1 for n in tw1 if n + 1 <= LIMIT}
# Add cycle IS counts (tw=2)
tw2_base |= {n for n in cycle_is_counts(50) if n <= LIMIT}
tw2 = multiplicative_closure(tw2_base, LIMIT)
missing_tw2 = sorted(n for n in range(1, LIMIT + 1) if n not in tw2)
print(f"\ntw<=2 achievable count (up to {LIMIT}): {sum(1 for n in tw2 if 1 <= n <= LIMIT)}/{LIMIT}")
print(f"tw<=2 missing: {missing_tw2[:30]}{'...' if len(missing_tw2) > 30 else ''}")

# Layer 3: tw<=2 + universal vertex (+1) + Combine gadget + disjoint union
# Universal vertex on tw<=2: IS(G)+1, tw<=3
tw3_base = tw2 | {n + 1 for n in tw2 if n + 1 <= LIMIT}
# Combine gadget: (a+1)(b+1) - 1 for tw<=2 achievable a, b
for a in sorted(tw2):
    if a > LIMIT:
        break
    for b in sorted(tw2):
        if b > LIMIT:
            break
        val = (a + 1) * (b + 1) - 1
        if val <= LIMIT:
            tw3_base.add(val)

tw3 = multiplicative_closure(tw3_base, LIMIT)
missing_tw3 = sorted(n for n in range(1, LIMIT + 1) if n not in tw3)
print(f"\ntw<=3 achievable count (up to {LIMIT}): {sum(1 for n in tw3 if 1 <= n <= LIMIT)}/{LIMIT}")
if missing_tw3:
    print(f"tw<=3 missing: {missing_tw3}")
else:
    print("tw<=3 missing: NONE — all integers 1..{} are achievable!".format(LIMIT))

# Let's also check a larger range
LIMIT2 = 1000
tw0_big = multiplicative_closure({2**n for n in range(30) if 2**n <= LIMIT2}, LIMIT2)
tw1_big = multiplicative_closure(tw0_big | {n for n in tree_is if n <= LIMIT2}, LIMIT2)
tw2_big = multiplicative_closure(
    tw1_big | {n + 1 for n in tw1_big if n + 1 <= LIMIT2} | {n for n in cycle_is_counts(50) if n <= LIMIT2},
    LIMIT2
)
tw3_base_big = tw2_big | {n + 1 for n in tw2_big if n + 1 <= LIMIT2}
for a in sorted(tw2_big):
    if a > LIMIT2:
        break
    for b in sorted(tw2_big):
        if b > LIMIT2:
            break
        val = (a + 1) * (b + 1) - 1
        if val <= LIMIT2:
            tw3_base_big.add(val)
tw3_big = multiplicative_closure(tw3_base_big, LIMIT2)
missing_tw3_big = sorted(n for n in range(1, LIMIT2 + 1) if n not in tw3_big)
print(f"\ntw<=3 achievable count (up to {LIMIT2}): {sum(1 for n in tw3_big if 1 <= n <= LIMIT2)}/{LIMIT2}")
if missing_tw3_big:
    print(f"tw<=3 missing (up to {LIMIT2}): {missing_tw3_big[:50]}{'...' if len(missing_tw3_big) > 50 else ''}")
else:
    print(f"tw<=3 missing (up to {LIMIT2}): NONE — all integers 1..{LIMIT2} are achievable!")

# Analysis: what's the gap structure?
print("\n" + "=" * 60)
print("DETAILED GAP ANALYSIS")
print("=" * 60)

for tw_name, missing in [("tw<=1", [n for n in range(1, LIMIT + 1) if n not in tw1]),
                          ("tw<=2", [n for n in range(1, LIMIT + 1) if n not in tw2])]:
    print(f"\n{tw_name} gaps (up to {LIMIT}):")
    print(f"  Count: {len(missing)}")
    if missing:
        print(f"  First 20: {missing[:20]}")

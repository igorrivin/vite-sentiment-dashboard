"""
Analyze whether GPT's approach can realize ANY positive integer as an
IS count with treewidth <= 3.

Operations:
1. Disjoint union: IS counts multiply, tw = max
2. Universal vertex: IS -> IS(G) + 1, tw -> tw + 1
3. Combine(A,B): IS = (IS(A)+1)(IS(B)+1) - 1, tw = max(tw(A),tw(B)) + 1
"""

LIMIT = 500


def mult_closure(generators, limit):
    """Close under multiplication up to limit. Uses sieve-like approach."""
    achievable = [False] * (limit + 1)
    for g in generators:
        if 1 <= g <= limit:
            achievable[g] = True

    # Repeatedly multiply pairs until stable
    changed = True
    while changed:
        changed = False
        active = [i for i in range(2, limit + 1) if achievable[i]]
        for a in active:
            for b in active:
                p = a * b
                if p > limit:
                    break
                if not achievable[p]:
                    achievable[p] = True
                    changed = True

    return {i for i in range(1, limit + 1) if achievable[i]}


def tree_is_pairs(max_is=10000):
    """
    Generate all (a, b) pairs achievable by trees, where IS = a + b.
    a(v) = prod b(ci), b(v) = prod (a(ci)+b(ci)) for children ci.
    Leaf: (1, 1).
    """
    pairs = {(1, 1)}
    prev_size = 0

    for _ in range(8):
        if len(pairs) == prev_size:
            break
        prev_size = len(pairs)
        new_pairs = set()
        pairs_list = sorted(pairs)

        # Build tree: new root with 1, 2, or 3 children
        for i, (a1, b1) in enumerate(pairs_list):
            # 1 child
            ar, br = b1, a1 + b1
            if ar + br <= max_is:
                new_pairs.add((ar, br))

            # 2 children
            for a2, b2 in pairs_list:
                ar = b1 * b2
                br = (a1 + b1) * (a2 + b2)
                if ar + br > max_is:
                    break
                new_pairs.add((ar, br))

            # 3 children
            for a2, b2 in pairs_list:
                if b1 * b2 > max_is:
                    break
                for a3, b3 in pairs_list:
                    ar = b1 * b2 * b3
                    br = (a1 + b1) * (a2 + b2) * (a3 + b3)
                    if ar + br > max_is:
                        break
                    new_pairs.add((ar, br))

        pairs |= new_pairs

    return pairs


print("Computing tree (a,b) pairs...")
pairs = tree_is_pairs(LIMIT * 10)
tree_is = {a + b for a, b in pairs if a + b <= LIMIT}
print(f"Distinct tree IS counts <= {LIMIT}: {len(tree_is)}")
print(f"Sample tree IS counts: {sorted(tree_is)[:30]}")

# Cycle IS counts (Lucas numbers)
fibs = [1, 1]
for i in range(60):
    fibs.append(fibs[-1] + fibs[-2])
cycle_is = set()
for n in range(3, 60):
    L = fibs[n + 1] + fibs[n - 1]
    if L <= LIMIT:
        cycle_is.add(L)

print(f"\nCycle IS counts <= {LIMIT}: {sorted(cycle_is)}")

# tw=0: powers of 2
tw0_gen = {2**n for n in range(30) if 2**n <= LIMIT}
tw0 = mult_closure(tw0_gen, LIMIT)
print(f"\ntw=0: {len(tw0)}/{LIMIT} achievable")

# tw<=1: forests = trees + disjoint union
tw1_gen = tw0 | tree_is
tw1 = mult_closure(tw1_gen, LIMIT)
missing1 = sorted(set(range(1, LIMIT + 1)) - tw1)
print(f"tw<=1: {len(tw1)}/{LIMIT} achievable")
print(f"  missing: {missing1[:40]}...")

# tw<=2: tw1 + universal vertex (+1) + cycles + mult closure
tw2_gen = tw1 | {n + 1 for n in tw1 if n + 1 <= LIMIT} | cycle_is
tw2 = mult_closure(tw2_gen, LIMIT)
missing2 = sorted(set(range(1, LIMIT + 1)) - tw2)
print(f"tw<=2: {len(tw2)}/{LIMIT} achievable")
if missing2:
    print(f"  missing: {missing2[:40]}{'...' if len(missing2) > 40 else ''}")
else:
    print("  ALL achievable!")

# tw<=3: tw2 + universal vertex (+1) + Combine gadget + mult closure
tw3_gen = set(tw2)
# universal vertex on tw<=2
tw3_gen |= {n + 1 for n in tw2 if n + 1 <= LIMIT}
# Combine gadget: (a+1)(b+1) - 1 for a, b in tw2
tw2_sorted = sorted(tw2)
for a in tw2_sorted:
    for b in tw2_sorted:
        val = (a + 1) * (b + 1) - 1
        if val > LIMIT:
            break
        tw3_gen.add(val)
tw3 = mult_closure(tw3_gen, LIMIT)
missing3 = sorted(set(range(1, LIMIT + 1)) - tw3)
print(f"tw<=3: {len(tw3)}/{LIMIT} achievable")
if missing3:
    print(f"  missing: {missing3[:40]}{'...' if len(missing3) > 40 else ''}")
else:
    print(f"  ALL integers 1..{LIMIT} are achievable!")

# Additional analysis: what makes tw<=2 sufficient or not?
print("\n" + "=" * 60)
print("KEY INSIGHT: Is tw<=2 already universal?")
print("=" * 60)
if not missing2:
    print("YES - tw<=2 already achieves all integers!")
    print("This means tw<=3 is trivially universal too.")
else:
    # Check if +1 operation alone fills gaps
    # Since tw<=1 has tree IS counts closed under mult,
    # and tw<=2 adds +1 (universal vertex),
    # check if {n+1 : n in tw1} fills everything
    print(f"\ntw<=1 achieves {len(tw1)}/{LIMIT}")
    print(f"After +1 operation: adds {len({n+1 for n in tw1 if n+1 <= LIMIT} - tw1)} new values")
    print(f"tw<=2 still missing {len(missing2)} values")

    # What fills the rest at tw<=3?
    only_tw3 = tw3 - tw2
    print(f"\ntw<=3 adds {len(only_tw3)} values beyond tw<=2")
    if only_tw3:
        print(f"  Examples: {sorted(only_tw3)[:20]}")

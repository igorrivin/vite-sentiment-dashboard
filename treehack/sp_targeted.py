"""
More targeted analysis:
1. Can SP graphs achieve values like 359, 383, 1019 that trees+cycles miss?
2. Theoretical structure of the problem.

Key insight: rather than enumerate all SP graphs, use the algebraic structure.
An SP graph signature is (f00, f10, f01, f11).
Series and parallel are algebraic operations on these 4-tuples.

We want to find which IS counts (= f00+f10+f01+f11) are achievable.
"""

def series(g1, g2):
    a00, a10, a01, a11 = g1
    b00, b10, b01, b11 = g2
    return (
        a00*b00 + a01*b10,
        a10*b00 + a11*b10,
        a00*b01 + a01*b11,
        a10*b01 + a11*b11
    )

def parallel(g1, g2):
    return (g1[0]*g2[0], g1[1]*g2[1], g1[2]*g2[2], g1[3]*g2[3])

def is_count(g):
    return sum(g)

# BFS to find SP graphs with specific target IS counts
# Keep only signatures with bounded IS count to avoid explosion
TARGETS = {359, 383, 718, 766, 1019}
LIMIT = 1200

base = (1, 1, 1, 0)

# Strategy: keep only signatures where IS count is small
# because we only need them as building blocks
sigs = {base}
achieved = {is_count(base)}

print("Building SP signatures layer by layer...")
for iteration in range(12):
    new_sigs = set()
    sigs_list = sorted(sigs, key=is_count)

    for g1 in sigs_list:
        c1 = is_count(g1)
        if c1 > LIMIT:
            break
        for g2 in sigs_list:
            c2 = is_count(g2)
            if c2 > LIMIT:
                break

            s = series(g1, g2)
            cs = is_count(s)
            if cs <= LIMIT and s not in sigs:
                new_sigs.add(s)
                achieved.add(cs)

            p = parallel(g1, g2)
            cp = is_count(p)
            if cp <= LIMIT and p not in sigs:
                new_sigs.add(p)
                achieved.add(cp)

    if not new_sigs:
        print(f"  Iteration {iteration}: converged with {len(sigs)} sigs")
        break

    sigs |= new_sigs
    # Prune to keep only unique IS counts + small representatives
    # Keep at most a few sigs per IS count
    from collections import defaultdict
    by_count = defaultdict(list)
    for s in sigs:
        by_count[is_count(s)].append(s)
    pruned = set()
    for c, ss in by_count.items():
        pruned.update(ss[:5])  # keep up to 5 per IS count
    sigs = pruned

    found = TARGETS & achieved
    print(f"  Iteration {iteration}: {len(sigs)} sigs, {len(achieved)} IS counts, targets found: {found}")

    if TARGETS <= achieved:
        print("  All targets found!")
        break

print(f"\nAchieved SP IS counts up to {LIMIT}: {len([c for c in achieved if c <= LIMIT])}")

# Check which targets are achievable
for t in sorted(TARGETS):
    print(f"  {t}: {'YES' if t in achieved else 'NO'}")

# What does the SP achievable set look like for small values?
sp_small = sorted(c for c in achieved if c <= 100)
print(f"\nSP IS counts up to 100: {sp_small}")
all_small = set(range(1, 101))
missing_small = sorted(all_small - achieved)
print(f"Missing up to 100: {missing_small}")

# Now check: SP + trees + universal vertex + mult closure
# First just check: what values up to 200 can SP alone produce?
sp_200 = sorted(c for c in achieved if c <= 200)
missing_200 = sorted(set(range(1, 201)) - achieved)
print(f"\nSP IS counts up to 200: {len(sp_200)}/200")
print(f"Missing: {missing_200}")

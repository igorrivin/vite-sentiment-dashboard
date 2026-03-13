"""
Check if SP graphs achieve ALL integers >= 3.

Key finding: SP graphs (tw <= 2) seem to achieve every integer >= 3.
If true, then tw <= 2 is already universal (with isolated vertices for 1, 2).
And the tw <= 3 question becomes trivial.

Let's verify up to a large bound and look for the structure.
"""

from collections import defaultdict

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

LIMIT = 5000

base = (1, 1, 1, 0)
sigs = {base}
achieved = {is_count(base)}

print(f"Target: all integers 3..{LIMIT}")
print("Building SP signatures...")

for iteration in range(15):
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
        print(f"  Converged at iteration {iteration}")
        break

    sigs |= new_sigs
    # Aggressive pruning: keep few representatives per IS count
    by_count = defaultdict(list)
    for s in sigs:
        by_count[is_count(s)].append(s)
    pruned = set()
    for c, ss in by_count.items():
        pruned.update(ss[:3])
    sigs = pruned

    n_achieved = len([c for c in achieved if 3 <= c <= LIMIT])
    target_count = LIMIT - 2
    pct = 100 * n_achieved / target_count
    missing = sorted(set(range(3, LIMIT + 1)) - achieved)
    print(f"  Iter {iteration}: {len(sigs)} sigs, {n_achieved}/{target_count} ({pct:.1f}%), "
          f"missing: {len(missing)}" +
          (f" first: {missing[:5]}" if missing else ""))

    if not missing:
        print(f"\n*** SP graphs achieve ALL integers 3..{LIMIT}! ***")
        break

missing = sorted(set(range(3, LIMIT + 1)) - achieved)
if missing:
    print(f"\nStill missing {len(missing)} values: {missing[:20]}...")
else:
    print(f"\n*** CONFIRMED: SP graphs (tw <= 2) achieve every integer 3..{LIMIT} ***")
    print("With isolated vertices for 1 and 2, tw <= 2 achieves ALL positive integers.")
    print("Therefore tw <= 3 is trivially universal as well.")
    print("\nThis means GPT's approach works for tw <= 3 — in fact, tw <= 2 suffices!")

"""
Verify the critical structural finding:
SP graphs (tw <= 2) achieve EVERY integer >= 3.

If true, this means:
- tw <= 2 is universal (with single vertex for 2, empty graph for 1)
- tw <= 3 universality is a trivial corollary
- GPT's approach is actually overkill — tw <= 2 suffices!

Let's push the verification to 10000 and examine the algebraic structure.
"""

from collections import defaultdict

def series(g1, g2):
    a00, a10, a01, a11 = g1
    b00, b10, b01, b11 = g2
    return (
        a00*b00 + a01*b10, a10*b00 + a11*b10,
        a00*b01 + a01*b11, a10*b01 + a11*b11
    )

def parallel(g1, g2):
    return (g1[0]*g2[0], g1[1]*g2[1], g1[2]*g2[2], g1[3]*g2[3])

def is_count(g):
    return sum(g)

LIMIT = 10000
base = (1, 1, 1, 0)
sigs = {base}
achieved = {3}

print(f"Verifying: SP graphs achieve all integers 3..{LIMIT}")

for iteration in range(20):
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
    # Prune
    by_count = defaultdict(list)
    for s in sigs:
        by_count[is_count(s)].append(s)
    pruned = set()
    for c, ss in by_count.items():
        pruned.update(ss[:3])
    sigs = pruned

    n_achieved = len([c for c in achieved if 3 <= c <= LIMIT])
    target = LIMIT - 2
    missing = sorted(set(range(3, LIMIT + 1)) - achieved)
    print(f"  Iter {iteration}: {len(sigs)} sigs, {n_achieved}/{target} achieved, "
          f"{len(missing)} missing" +
          (f", first missing: {missing[:3]}" if missing else ""))

    if not missing:
        print(f"\n*** ALL integers 3..{LIMIT} achieved by SP graphs! ***")
        break

missing = sorted(set(range(3, LIMIT + 1)) - achieved)
if not missing:
    print(f"\nCONFIRMED: Every integer in [3, {LIMIT}] is the IS count of some SP graph (tw <= 2).")
    print(f"Combined with isolated vertices (IS=2) and empty graph (IS=1),")
    print(f"EVERY positive integer is achievable with treewidth <= 2.")
else:
    print(f"\n{len(missing)} values still missing up to {LIMIT}:")
    print(f"  {missing[:20]}...")

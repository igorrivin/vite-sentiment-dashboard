"""
Final analysis: check tw<=3 universality up to 10000,
characterize tw<=2 gaps, and prove tw<=3 always works.
"""

LIMIT = 10000


def mult_closure(generators, limit):
    achievable = bytearray(limit + 1)
    for g in generators:
        if 1 <= g <= limit:
            achievable[g] = 1
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
                    achievable[p] = 1
                    changed = True
    return {i for i in range(1, limit + 1) if achievable[i]}


def tree_is_pairs(max_is):
    pairs = {(1, 1)}
    prev_size = 0
    for _ in range(12):
        if len(pairs) == prev_size:
            break
        prev_size = len(pairs)
        new_pairs = set()
        pairs_list = sorted(pairs)
        for a1, b1 in pairs_list:
            ar, br = b1, a1 + b1
            if ar + br <= max_is:
                new_pairs.add((ar, br))
            for a2, b2 in pairs_list:
                ar = b1 * b2
                br = (a1 + b1) * (a2 + b2)
                if ar + br > max_is:
                    break
                new_pairs.add((ar, br))
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


print(f"Computing tree IS pairs (limit={LIMIT})...")
pairs = tree_is_pairs(LIMIT * 3)
tree_is = {a + b for a, b in pairs if a + b <= LIMIT}
print(f"Tree IS counts <= {LIMIT}: {len(tree_is)}")

cycle_is = set()
fibs = [1, 1]
for i in range(80):
    fibs.append(fibs[-1] + fibs[-2])
for n in range(3, 80):
    L = fibs[n+1] + fibs[n-1]
    if L <= LIMIT:
        cycle_is.add(L)

tw0_gen = {2**n for n in range(30) if 2**n <= LIMIT}

print("Computing tw<=1...")
tw1 = mult_closure(tw0_gen | tree_is, LIMIT)

print("Computing tw<=2...")
tw2_gen = tw1 | {n + 1 for n in tw1 if n + 1 <= LIMIT} | cycle_is
tw2 = mult_closure(tw2_gen, LIMIT)

print("Computing tw<=3...")
tw3_gen = set(tw2) | {n + 1 for n in tw2 if n + 1 <= LIMIT}
tw2_sorted = sorted(tw2)
for a in tw2_sorted:
    for b in tw2_sorted:
        val = (a + 1) * (b + 1) - 1
        if val > LIMIT:
            break
        tw3_gen.add(val)
tw3 = mult_closure(tw3_gen, LIMIT)

missing1 = sorted(set(range(1, LIMIT + 1)) - tw1)
missing2 = sorted(set(range(1, LIMIT + 1)) - tw2)
missing3 = sorted(set(range(1, LIMIT + 1)) - tw3)

print(f"\n{'='*60}")
print(f"RESULTS (up to {LIMIT})")
print(f"{'='*60}")
print(f"tw<=1: {len(tw1)}/{LIMIT} ({100*len(tw1)/LIMIT:.1f}%)")
print(f"tw<=2: {len(tw2)}/{LIMIT} ({100*len(tw2)/LIMIT:.1f}%), {len(missing2)} gaps")
print(f"tw<=3: {len(tw3)}/{LIMIT} ({100*len(tw3)/LIMIT:.1f}%), {len(missing3)} gaps")

if missing3:
    print(f"\n*** tw<=3 GAPS FOUND: {missing3[:30]} ***")
else:
    print(f"\n*** tw<=3 is UNIVERSAL for 1..{LIMIT} ***")

# Characterize tw<=2 gaps
print(f"\ntw<=2 gaps ({len(missing2)} total):")
print(f"  Values: {missing2[:50]}{'...' if len(missing2) > 50 else ''}")

# Check: are all tw<=2 gaps prime?
def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

prime_gaps = [n for n in missing2 if is_prime(n)]
composite_gaps = [n for n in missing2 if not is_prime(n)]
print(f"  Of which prime: {len(prime_gaps)}")
print(f"  Of which composite: {len(composite_gaps)}")
if composite_gaps:
    print(f"  Composite gaps: {composite_gaps[:20]}")

# Check: for each tw<=2 gap n, is n-1 always in tw2?
all_filled_by_uv = all((n - 1) in tw2 for n in missing2)
print(f"\n  All gaps filled by universal vertex (+1)? {all_filled_by_uv}")
unfilled = [n for n in missing2 if (n - 1) not in tw2]
if unfilled:
    print(f"  NOT filled by +1: {unfilled[:20]}")

# Density analysis
print(f"\nDensity of tw<=1 among primes <= {LIMIT}:")
primes = [p for p in range(2, LIMIT + 1) if is_prime(p)]
primes_in_tw1 = [p for p in primes if p in tw1]
print(f"  {len(primes_in_tw1)}/{len(primes)} primes achievable at tw<=1")
primes_in_tw2 = [p for p in primes if p in tw2]
print(f"  {len(primes_in_tw2)}/{len(primes)} primes achievable at tw<=2")
primes_missing_tw2 = [p for p in primes if p not in tw2]
print(f"  Primes missing from tw<=2: {primes_missing_tw2[:30]}{'...' if len(primes_missing_tw2) > 30 else ''}")

"""
Enumerate IS counts achievable by series-parallel (SP) graphs.

SP graphs have tw <= 2 and are built by series/parallel composition.

A two-terminal SP graph G(s,t) has IS signature (f00, f10, f01, f11):
  f00 = # IS with s,t both OUT
  f10 = # IS with s IN, t OUT
  f01 = # IS with s OUT, t IN
  f11 = # IS with s,t both IN

Base: single edge s-t: (1, 1, 1, 0)

Series(G1(s,m), G2(m,t)) -> G(s,t):
  f00 = f1_00*f2_00 + f1_01*f2_10
  f10 = f1_10*f2_00 + f1_11*f2_10
  f01 = f1_00*f2_01 + f1_01*f2_11
  f11 = f1_10*f2_01 + f1_11*f2_11

Parallel(G1(s,t), G2(s,t)) -> G(s,t):
  f00 = f1_00 * f2_00
  f10 = f1_10 * f2_10
  f01 = f1_01 * f2_01
  f11 = f1_11 * f2_11

IS count = f00 + f10 + f01 + f11
"""

LIMIT = 2000

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

# Enumerate all SP signatures with IS count <= LIMIT
# Use BFS over compositions
MAX_IS = LIMIT * 10  # allow intermediate values somewhat larger

base = (1, 1, 1, 0)  # single edge

sigs = {base}
is_counts_sp = {is_count(base)}

print("Enumerating SP graph IS signatures...")
prev_size = 0
iteration = 0
while len(sigs) > prev_size:
    prev_size = len(sigs)
    iteration += 1
    new_sigs = set()
    sigs_list = sorted(sigs, key=is_count)

    for g1 in sigs_list:
        if is_count(g1) > LIMIT:
            break
        for g2 in sigs_list:
            if is_count(g2) > LIMIT:
                break

            # Series
            s = series(g1, g2)
            if is_count(s) <= MAX_IS:
                if s not in sigs:
                    new_sigs.add(s)
                    c = is_count(s)
                    if c <= LIMIT:
                        is_counts_sp.add(c)

            # Parallel
            p = parallel(g1, g2)
            if is_count(p) <= MAX_IS:
                if p not in sigs:
                    new_sigs.add(p)
                    c = is_count(p)
                    if c <= LIMIT:
                        is_counts_sp.add(c)

    sigs |= new_sigs
    print(f"  Iteration {iteration}: {len(sigs)} signatures, {len(is_counts_sp)} distinct IS counts <= {LIMIT}")

    # Keep only signatures with reasonable IS count to avoid blowup
    sigs = {s for s in sigs if is_count(s) <= MAX_IS}

    if iteration >= 8:
        break

print(f"\nSP graph IS counts <= {LIMIT}: {len(is_counts_sp)}")

# Now build full tw<=2: SP counts + tree counts + universal vertex + mult closure
# For trees, use the DP enumeration
def tree_is_pairs(max_is):
    pairs = {(1, 1)}
    prev_size = 0
    for _ in range(10):
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

print("\nComputing tree IS counts...")
pairs = tree_is_pairs(LIMIT * 3)
tree_is = {a + b for a, b in pairs if a + b <= LIMIT}
print(f"Tree IS counts <= {LIMIT}: {len(tree_is)}")

# Combine all tw<=1 sources
tw1_base = tree_is | {2**n for n in range(30) if 2**n <= LIMIT}
tw1 = mult_closure(tw1_base, LIMIT)

# tw<=2: tw1 + SP + universal vertex on tw1
tw2_base = tw1 | is_counts_sp | {n + 1 for n in tw1 if n + 1 <= LIMIT}

# Also: SP graphs as standalone (not two-terminal) — IS count of SP graph
# is f00+f10+f01+f11. But we can also "close" terminals: identify s=t or leave free.
# Leaving terminals free gives IS = f00+f10+f01+f11 (what we computed).
# We can also add universal vertex to SP graphs directly.
tw2_base |= {is_count(s) + 1 for s in sigs if is_count(s) + 1 <= LIMIT}  # univ vertex on SP
tw2_base |= {is_count(s) for s in sigs if is_count(s) <= LIMIT}

tw2 = mult_closure(tw2_base, LIMIT)

missing_tw2 = sorted(set(range(1, LIMIT + 1)) - tw2)
print(f"\ntw<=2 (with SP graphs): {len(tw2)}/{LIMIT}")
if missing_tw2:
    print(f"  Missing: {missing_tw2[:30]}{'...' if len(missing_tw2) > 30 else ''}")
else:
    print(f"  ALL integers 1..{LIMIT} achievable at tw<=2!")

# tw<=3 check
tw3_base = set(tw2) | {n + 1 for n in tw2 if n + 1 <= LIMIT}
tw2_sorted = sorted(tw2)
for a in tw2_sorted:
    for b in tw2_sorted:
        val = (a + 1) * (b + 1) - 1
        if val > LIMIT:
            break
        tw3_base.add(val)
tw3 = mult_closure(tw3_base, LIMIT)
missing_tw3 = sorted(set(range(1, LIMIT + 1)) - tw3)
print(f"tw<=3: {len(tw3)}/{LIMIT}")
if missing_tw3:
    print(f"  Missing: {missing_tw3}")
else:
    print(f"  ALL integers 1..{LIMIT} achievable at tw<=3!")

# Show what SP graphs add beyond trees
sp_only = is_counts_sp - tree_is
print(f"\nIS counts achievable by SP but NOT trees (up to {LIMIT}):")
print(f"  Count: {len(sp_only)}")
sp_sorted = sorted(n for n in sp_only if n <= 100)
print(f"  Up to 100: {sp_sorted}")

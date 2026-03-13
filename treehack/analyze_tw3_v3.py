"""Check larger ranges and investigate whether tw<=3 is provably universal."""

LIMIT = 2000


def mult_closure(generators, limit):
    achievable = [False] * (limit + 1)
    for g in generators:
        if 1 <= g <= limit:
            achievable[g] = True
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


def tree_is_pairs(max_is=50000):
    pairs = {(1, 1)}
    prev_size = 0
    for _ in range(10):
        if len(pairs) == prev_size:
            break
        prev_size = len(pairs)
        new_pairs = set()
        pairs_list = sorted(pairs)
        for a1, b1 in pairs_list:
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


print("Computing tree IS pairs...")
pairs = tree_is_pairs(LIMIT * 5)
tree_is = {a + b for a, b in pairs if a + b <= LIMIT}
print(f"Tree IS counts <= {LIMIT}: {len(tree_is)}")

fibs = [1, 1]
for i in range(80):
    fibs.append(fibs[-1] + fibs[-2])
cycle_is = {fibs[n+1] + fibs[n-1] for n in range(3, 80) if fibs[n+1] + fibs[n-1] <= LIMIT}

tw0_gen = {2**n for n in range(30) if 2**n <= LIMIT}
tw1 = mult_closure(tw0_gen | tree_is, LIMIT)
tw2_gen = tw1 | {n + 1 for n in tw1 if n + 1 <= LIMIT} | cycle_is
tw2 = mult_closure(tw2_gen, LIMIT)
tw3_gen = set(tw2) | {n + 1 for n in tw2 if n + 1 <= LIMIT}
tw2_sorted = sorted(tw2)
for a in tw2_sorted:
    for b in tw2_sorted:
        val = (a + 1) * (b + 1) - 1
        if val > LIMIT:
            break
        tw3_gen.add(val)
tw3 = mult_closure(tw3_gen, LIMIT)

missing2 = sorted(set(range(1, LIMIT + 1)) - tw2)
missing3 = sorted(set(range(1, LIMIT + 1)) - tw3)

print(f"\ntw<=1: {len(tw1)}/{LIMIT}")
print(f"tw<=2: {len(tw2)}/{LIMIT}, missing {len(missing2)}")
if missing2:
    print(f"  tw<=2 gaps: {missing2[:60]}{'...' if len(missing2) > 60 else ''}")
print(f"tw<=3: {len(tw3)}/{LIMIT}, missing {len(missing3)}")
if missing3:
    print(f"  tw<=3 gaps: {missing3}")
else:
    print(f"  ALL integers 1..{LIMIT} achievable at tw<=3!")

# For each tw<=2 gap, show how tw<=3 fills it
if missing2 and not missing3:
    print("\nHow tw<=3 fills tw<=2 gaps:")
    for n in missing2[:20]:
        # Check: is n = m+1 for some m in tw2?
        if (n - 1) in tw2:
            print(f"  {n} = universal_vertex({n-1})")
            continue
        # Check: is n = (a+1)(b+1)-1 for some a,b in tw2?
        found = False
        for a in tw2_sorted:
            if a + 1 > n:
                break
            rem = n + 1
            if rem % (a + 1) == 0:
                b = rem // (a + 1) - 1
                if b >= 1 and b in tw2:
                    print(f"  {n} = Combine({a}, {b})  [(={a}+1)({b}+1)-1]")
                    found = True
                    break
        if not found:
            # Must be from multiplicative closure of tw3 base
            for a in sorted(tw3_gen):
                if a >= n:
                    break
                if n % a == 0 and (n // a) in tw3:
                    print(f"  {n} = {a} * {n//a}")
                    break

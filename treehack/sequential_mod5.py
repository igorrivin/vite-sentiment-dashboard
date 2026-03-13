"""
Check what residues mod 5 (and other primes) the sequential orbit hits.
Does the ~34% density come from mod 5 obstructions?
"""

fib = [0, 1]
for i in range(200):
    fib.append(fib[-1] + fib[-2])

from collections import Counter, deque

def sequential_is_counts_with_residues(max_depth, limit):
    """Generate sequential IS counts and track residue distributions."""
    visited = set()
    queue = deque()
    is_counts = set()

    start = (0, 1, 0)  # (n_R, c, d)
    visited.add(start)
    queue.append(start)

    while queue:
        n, c, d = queue.popleft()
        a, b = fib[n + 2], fib[n + 1]
        is_val = a + b + c + d
        if is_val <= limit:
            is_counts.add(is_val)

        if n >= max_depth:
            continue

        # Apply R
        new_n = n + 1
        new_c, new_d = c + d, c
        state_r = (new_n, new_c, new_d)
        if state_r not in visited and fib[new_n + 2] + fib[new_n + 1] + new_c + new_d <= limit * 2:
            visited.add(state_r)
            queue.append(state_r)

        # Apply P
        state_p = (n, c, 0)
        if state_p not in visited:
            visited.add(state_p)
            queue.append(state_p)

    return is_counts

LIMIT = 10000
print(f"Computing sequential orbit up to {LIMIT}...")
seq = sequential_is_counts_with_residues(50, LIMIT)
print(f"Sequential orbit: {len(seq)} values in [1, {LIMIT}]")
print(f"Density: {len(seq)/LIMIT:.4f}")

# Check residue distribution for various primes
print("\n" + "=" * 60)
print("RESIDUE ANALYSIS OF SEQUENTIAL ORBIT")
print("=" * 60)

for p in [2, 3, 5, 7, 11, 13]:
    residues_hit = {v % p for v in seq if v > 0}
    residue_counts = Counter(v % p for v in seq if v > 0)

    print(f"\nmod {p}:")
    print(f"  Residues hit: {sorted(residues_hit)} ({len(residues_hit)}/{p})")
    for r in range(p):
        count = residue_counts.get(r, 0)
        total_in_class = len([v for v in range(r, LIMIT+1, p) if v >= 3])
        density = count / total_in_class if total_in_class > 0 else 0
        print(f"    r={r}: {count} values, density in class = {density:.4f}")

# Check: what's the predicted density from mod-p sieving?
# If we miss k residues mod 5 and hit all residues for other primes,
# density = (5-k)/5
print("\n" + "=" * 60)
print("DENSITY PREDICTION")
print("=" * 60)

# Compute density in windows to see if it converges
for window in [100, 500, 1000, 5000, 10000]:
    count = len([v for v in seq if 3 <= v <= window])
    total = window - 2
    print(f"  Density in [3, {window}]: {count}/{total} = {count/total:.4f}")

# Is the density approaching a limit?
# What is the Fibonacci matrix mod 5?
print("\n\nFibonacci matrix mod 5:")
print("F mod 5 = [[1,1],[1,0]]")
print("Char poly: x^2 - x - 1 = (x-3)^2 mod 5  (repeated eigenvalue 3)")
print("F is a Jordan block mod 5 — this is the degeneracy!")
print(f"Pisano period π(5) = 20")
print(f"F_k mod 5 for k=0..24: {[fib[k] % 5 for k in range(25)]}")
print(f"Zeros of F_k mod 5: k ∈ {[k for k in range(25) if fib[k] % 5 == 0]}")

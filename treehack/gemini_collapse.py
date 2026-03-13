"""
Test Gemini's claim: the sequential IFS collapses due to EF^kE = F_{k+1}E.

The block structure:
  Top pair (a,b): evolves under F (from R) and I (from P) -> just F^n
  Bottom pair (c,d): evolves under F (from R) and E (from P) -> collapses

Question: does the SEQUENTIAL IFS (applying R, P one at a time to a single state)
generate all IS counts >= 3? Or do we need the full bisemigroup (arbitrary pairwise
matrix and Hadamard products)?
"""

# Fibonacci numbers
fib = [0, 1]
for i in range(100):
    fib.append(fib[-1] + fib[-2])

def sequential_is_counts(max_depth, limit):
    """
    Generate IS counts from the sequential IFS: apply R or P to a running state.
    State = (a, b, c, d). Start = (1, 1, 1, 0).

    Top pair (a,b) = (F_{n+2}, F_{n+1}) where n = total R's applied.
    Bottom pair: evolves under F and E = [[1,0],[0,0]].

    IS = a + b + c + d.
    """
    # BFS over states, but track (n_total_R, c, d) since (a,b) is determined by n
    # State: (total_R_count, c, d)
    # Starting: total_R = 0, (c,d) = (1, 0)
    from collections import deque

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

        # Apply R: top gets F, bottom gets F
        # (c, d) -> (c+d, c)
        new_n = n + 1
        new_c, new_d = c + d, c
        state_r = (new_n, new_c, new_d)
        if state_r not in visited and fib[new_n + 2] + fib[new_n + 1] + new_c + new_d <= limit * 2:
            visited.add(state_r)
            queue.append(state_r)

        # Apply P: top gets I (no change to n), bottom gets E
        # (c, d) -> (c, 0)
        state_p = (n, c, 0)
        if state_p not in visited:
            visited.add(state_p)
            queue.append(state_p)

    return is_counts


LIMIT = 1000
print(f"Sequential IFS: IS counts achievable up to {LIMIT}")
seq_counts = sequential_is_counts(max_depth=40, limit=LIMIT)
seq_missing = sorted(set(range(3, LIMIT + 1)) - seq_counts)
print(f"  Achieved: {len(seq_counts)}/{LIMIT - 2}")
print(f"  Missing: {len(seq_missing)}")
if seq_missing:
    print(f"  First 30 missing: {seq_missing[:30]}")

# Now check: what does the sequential orbit give in terms of Gemini's formula?
# IS = F_{n+3} + C * F_{a+2} where C is a Fibonacci product
# Let's enumerate the canonical forms

print(f"\n\nCanonical form analysis:")
print("IS = F_{n+3} + C * F_{a+2}")
print("where n = total R's, a = trailing R's after last P, C = product of Fibonacci numbers")
print()

# A word R^{a_0} P R^{a_1} P ... P R^{a_s} gives:
# Top: n = a_0 + a_1 + ... + a_s total R's -> (F_{n+2}, F_{n+1})
# Bottom: F^{a_0} E F^{a_1} E ... E F^{a_s} (1, 0)^T
#
# Using EF^kE = F_{k+1}E, this reduces.
# Let me trace through:
# Start with (1, 0). Apply F^{a_s}: -> (F_{a_s+1}, F_{a_s})
# Apply E: -> (F_{a_s+1}, 0)
# Apply F^{a_{s-1}}: -> (F_{a_s+1} * F_{a_{s-1}+1} + 0, F_{a_s+1} * F_{a_{s-1}})
#                      Hmm wait, F applied to (x, 0) gives (x, x)... no
# F (x, y) = (x+y, x)
# So F^{a_{s-1}} (F_{a_s+1}, 0):
# Step 1: (F_{a_s+1}, 0) -> F: (F_{a_s+1}, F_{a_s+1})
# Step 2: F: (2*F_{a_s+1}, F_{a_s+1})
# ...this is F_{a_s+1} * F^{a_{s-1}} (1, 0)^T? No...
# Actually F^k (x, 0) = x * F^k (1, 0) = x * (F_{k+1}, F_k)
# Because F is linear and F^k (1,0) = (F_{k+1}, F_k).
# So F^{a_{s-1}} (F_{a_s+1}, 0) = F_{a_s+1} * (F_{a_{s-1}+1}, F_{a_{s-1}})
# Then apply E: -> F_{a_s+1} * (F_{a_{s-1}+1}, 0)
# Then F^{a_{s-2}}: -> F_{a_s+1} * F_{a_{s-1}+1} * (F_{a_{s-2}+1}, F_{a_{s-2}})
# Then E: -> F_{a_s+1} * F_{a_{s-1}+1} * (F_{a_{s-2}+1}, 0)
# ...
# After all E's processed:
# (c, d) = (prod_{i=1}^{s} F_{a_i+1}) * (F_{a_0+1}, F_{a_0})  if s >= 1
# Or more precisely:
# The final bottom pair after word R^{a_0} P R^{a_1} P ... P R^{a_s} is:
# (c, d) = (prod_{i=1}^{s} F_{a_i+1}) * (F_{a_0+1}, F_{a_0})

# Wait, I need to be more careful about order. The word is applied left to right
# to the state. So the FIRST operation is the RIGHTMOST in the matrix product.
# Word: first do R^{a_s}, then P, then R^{a_{s-1}}, then P, ..., then R^{a_0}
# Matrix product (right to left): F^{a_0} E F^{a_1} E ... E F^{a_s}
# Applied to (1, 0):
# Start: (1, 0)
# F^{a_s}: (F_{a_s+1}, F_{a_s})
# E: (F_{a_s+1}, 0)
# F^{a_{s-1}}: F_{a_s+1} (F_{a_{s-1}+1}, F_{a_{s-1}})
# E: F_{a_s+1} (F_{a_{s-1}+1}, 0)
# ...continuing...
# F^{a_1}: prod_{i=2}^{s} F_{a_i+1} * (F_{a_1+1}, F_{a_1})  [wait, let me recount]

# Actually I realize the application order might be different.
# If we READ the word left to right as operations applied in sequence:
# Step 1: apply R a_s times (R is "first")... hmm, this depends on convention.
# Let me just use the canonical form and verify numerically.

# Let's enumerate canonical form IS counts
canonical_is = set()
for s in range(0, 8):  # number of P's
    if s == 0:
        # Just R^n: IS = F_{n+3} (Fibonacci)
        for n in range(50):
            val = fib[n + 3]
            if val <= LIMIT:
                canonical_is.add(val)
    else:
        # s >= 1 P's, splitting n R's into s+1 groups a_0, ..., a_s
        # IS = F_{n+3} + C * F_{a+2} where...
        # Actually let me just enumerate all partitions
        # For s P's, we have s+1 groups of R's: a_0, a_1, ..., a_s >= 0
        # n = sum of a_i
        # Bottom pair: (prod_{i=1}^{s-1} F_{a_i+1}) * F_{a_s+1} * (F_{a_0+1}, F_{a_0})
        # Hmm, I need to get the formula right. Let me just compute directly.
        pass

# Actually, let me just verify: does the sequential IFS miss integers that
# the full bisemigroup catches?
print("\n\nComparison: Sequential IFS vs Full Bisemigroup")
print(f"Sequential: {len(seq_counts)} values in [3, {LIMIT}]")
print(f"Missing from sequential: {len(seq_missing)}")

# Now add multiplicative closure (disjoint union = multiply IS counts)
seq_with_mult = set(seq_counts)
seq_list = sorted(seq_counts)
changed = True
while changed:
    changed = False
    items = sorted(seq_with_mult)
    for a in items:
        if a > LIMIT:
            break
        for b in items:
            p = a * b
            if p > LIMIT:
                break
            if p not in seq_with_mult:
                seq_with_mult.add(p)
                changed = True

seq_mult_missing = sorted(set(range(1, LIMIT + 1)) - seq_with_mult)
print(f"\nSequential + multiplicative closure: {len(seq_with_mult)} values in [1, {LIMIT}]")
print(f"Missing: {len(seq_mult_missing)}")
if seq_mult_missing:
    print(f"  First 30: {seq_mult_missing[:30]}")

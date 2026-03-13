"""
Verify Gemini's exact formula for the sequential IFS functional.

Gemini claims: for a word R^{a_1} P R^{a_2} P ... P R^{a_{k+1}},

f(X) = F_{N+3} + F_{a_1+2} * F_{a_{k+1}+1} * prod_{i=2}^{k} F_{a_i+1}

where N = sum of all a_i.

Let's verify this against direct computation.
"""

fib = [0, 1]
for i in range(200):
    fib.append(fib[-1] + fib[-2])

import numpy as np

F = np.array([[1,1],[1,0]], dtype=object)
E = np.array([[1,0],[0,0]], dtype=object)
I2 = np.array([[1,0],[0,1]], dtype=object)

def mat_pow(M, n):
    result = np.array([[1,0],[0,1]], dtype=object)
    for _ in range(n):
        result = result @ M
    return result

def sequential_word(exponents):
    """
    Compute the 4D state for word R^{a_1} P R^{a_2} P ... P R^{a_{k+1}}.
    exponents = [a_1, a_2, ..., a_{k+1}]
    k = len(exponents) - 1 projections P.

    The word in matrix form (applied right-to-left):
    Top block: F^{a_1} I F^{a_2} I ... I F^{a_{k+1}} = F^N
    Bottom block: F^{a_1} E F^{a_2} E ... E F^{a_{k+1}}
    """
    k_plus_1 = len(exponents)
    N = sum(exponents)

    # Top block: just F^N
    top = mat_pow(F, N)

    # Bottom block: F^{a_1} E F^{a_2} E ... E F^{a_{k+1}}
    # Build right to left
    bot = mat_pow(F, exponents[-1])
    for i in range(k_plus_1 - 2, -1, -1):
        bot = E @ bot
        bot = mat_pow(F, exponents[i]) @ bot

    return top, bot

def compute_is(top, bot):
    """IS count = v^T [top; bot] w where v=(1,1,1,1), w depends on starting point.
    Actually: top pair (a,b) = top @ (1,1)^T, bottom pair (c,d) = bot @ (1,0)^T.
    IS = a + b + c + d.
    """
    v_top = top @ np.array([1, 1], dtype=object)
    v_bot = bot @ np.array([1, 0], dtype=object)
    return int(v_top[0] + v_top[1] + v_bot[0] + v_bot[1])

def gemini_formula(exponents):
    """Gemini's claimed formula."""
    k_plus_1 = len(exponents)
    N = sum(exponents)
    k = k_plus_1 - 1  # number of P's

    top_contribution = fib[N + 3]

    if k == 0:
        # No P's: just R^N
        # Bottom: F^N @ (1, 0) = (F_{N+1}, F_N)
        bot_contribution = fib[N + 1] + fib[N]
        return top_contribution + bot_contribution

    # k >= 1 P's
    a_1 = exponents[0]
    a_last = exponents[-1]

    product = 1
    for i in range(1, k):  # middle exponents (indices 1 to k-1)
        product *= fib[exponents[i] + 1]

    bot_contribution = fib[a_1 + 2] * fib[a_last + 1] * product

    return top_contribution + bot_contribution

# Verify
print("Verifying Gemini's formula against direct computation:")
print()

import itertools

errors = 0
tests = 0

# Test various exponent sequences
for k in range(0, 5):  # 0 to 4 P's
    for combo in itertools.product(range(0, 6), repeat=k+1):
        exponents = list(combo)
        top, bot = sequential_word(exponents)
        direct = compute_is(top, bot)
        formula = gemini_formula(exponents)
        tests += 1
        if direct != formula:
            errors += 1
            if errors <= 10:
                print(f"  MISMATCH: exponents={exponents}, direct={direct}, formula={formula}")

print(f"Tested {tests} words, {errors} mismatches.")

if errors == 0:
    print("Gemini's formula is CORRECT for all tested cases!")
else:
    print(f"Gemini's formula has {errors} errors.")

# Now check: what IS counts does the formula generate?
print("\n\nIS counts from Gemini's formula up to 200:")
formula_counts = set()
for k in range(0, 8):
    for combo in itertools.product(range(0, 15), repeat=min(k+1, 6)):
        if len(combo) < k + 1:
            continue
        exponents = list(combo)
        val = gemini_formula(exponents)
        if 1 <= val <= 200:
            formula_counts.add(val)

missing = sorted(set(range(3, 201)) - formula_counts)
print(f"Achieved: {len(formula_counts)}/198")
print(f"Missing: {missing[:30]}{'...' if len(missing) > 30 else ''}")

# Key insight: the formula is F_{N+3} + C where C is a product of Fibonacci numbers
# F_{N+3} ranges over all Fibonacci numbers
# C ranges over products of Fibonacci numbers (with specific structure)
# The SUM of a Fibonacci number and a Fibonacci product -- when can this hit every integer?
print("\n\nStructure: IS = F_{N+3} + (product of Fibonacci numbers)")
print("The sequential orbit generates sums F_m + C*F_n where C is a Fibonacci product.")
print("This is sparse because Fibonacci numbers grow exponentially.")
print("The full bisemigroup (with Hadamard products) is needed for universality.")

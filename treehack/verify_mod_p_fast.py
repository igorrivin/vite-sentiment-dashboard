"""
Fast verification: does S_p = M_2(F_p) for the bisemigroup closure?
Only test small primes where brute force is feasible.
"""

def mat_mult_mod(A, B, p):
    a, b, c, d = A
    e, f, g, h = B
    return ((a*e+b*g)%p, (a*f+b*h)%p, (c*e+d*g)%p, (c*f+d*h)%p)

def had_mod(A, B, p):
    return (A[0]*B[0]%p, A[1]*B[1]%p, A[2]*B[2]%p, A[3]*B[3]%p)

def full_closure_mod_p(p):
    E = (1 % p, 1 % p, 1 % p, 0)
    S = {E}
    iteration = 0
    while True:
        iteration += 1
        new = set()
        S_list = list(S)
        for A in S_list:
            for B in S_list:
                new.add(mat_mult_mod(A, B, p))
                new.add(had_mod(A, B, p))
        added = new - S
        S |= new
        print(f"  p={p}, iter {iteration}: |S| = {len(S)} (+{len(added)})")
        if not added:
            break
        if len(S) == p**4:
            print(f"  -> Full! S_p = M_2(F_p)")
            break
    return S

def main():
    for p in [2, 3, 5, 7, 11]:
        print(f"\np = {p}, |M_2(F_p)| = {p**4}")
        S = full_closure_mod_p(p)
        print(f"  RESULT: |S| = {len(S)}, full = {len(S) == p**4}")

    # Also check: what was our EARLIER claim about "proper subset"?
    # That was from mod_equidistribution.py which used the SEQUENTIAL orbit,
    # not the full bisemigroup. Let's verify.
    print("\n=== Sequential orbit only (IFS with R and P) ===")
    for p in [2, 3, 5, 7]:
        # Sequential: start from E, apply R (right-mult by E) or P (Hadamard with E)
        E = (1 % p, 1 % p, 1 % p, 0)
        seq = {E}
        while True:
            new = set()
            for v in list(seq):
                new.add(mat_mult_mod(v, E, p))  # series with E
                new.add(had_mod(v, E, p))        # parallel with E
            added = new - seq
            seq |= new
            if not added:
                break
        print(f"  p={p}: sequential orbit = {len(seq)}, full M_2 = {p**4}, "
              f"ratio = {len(seq)/p**4:.3f}")

if __name__ == "__main__":
    main()

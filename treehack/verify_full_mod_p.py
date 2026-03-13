"""
Verify GPT's claim: the full bisemigroup closure of E = [[1,1],[1,0]]
under matrix product and Hadamard product mod p is ALL of M_2(F_p).

Also verify the constructive proof:
1. E^(-1) exists mod p (since det(E) = -1)
2. K_u = [[u,1],[1,0]] for all u
3. U_t, L_t (upper/lower triangular)
4. D_x, D'_y (diagonal)
5. LDU factorization gives everything
"""

def mat_mult_mod(A, B, p):
    """2x2 matrix product mod p."""
    a, b, c, d = A
    e, f, g, h = B
    return ((a*e+b*g)%p, (a*f+b*h)%p, (c*e+d*g)%p, (c*f+d*h)%p)

def had_mod(A, B, p):
    """Hadamard product mod p."""
    return (A[0]*B[0]%p, A[1]*B[1]%p, A[2]*B[2]%p, A[3]*B[3]%p)

def full_closure_mod_p(p, max_iter=100):
    """Compute full closure of E under matrix product and Hadamard, mod p."""
    E = (1, 1, 1, 0)
    S = {E}
    for it in range(max_iter):
        new = set()
        S_list = list(S)
        for A in S_list:
            for B in S_list:
                new.add(mat_mult_mod(A, B, p))
                new.add(had_mod(A, B, p))
        added = new - S
        if not added:
            break
        S |= new
    return S

def main():
    print("=== Verifying S_p = M_2(F_p) ===\n")

    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        S = full_closure_mod_p(p)
        total = p**4
        print(f"p={p:2d}: |S_p| = {len(S):6d}, |M_2(F_p)| = {total:6d}, "
              f"full = {len(S) == total}")

    # For small p, also check GPT's constructive proof steps
    print("\n=== Constructive verification for p=7 ===")
    p = 7
    E = (1, 1, 1, 0)

    # Step 1: Find E^(-1) mod p
    # det(E) = -1 ≡ p-1 mod p
    # E^(-1) = (1/det) * [[0, -1], [-1, 1]] = (p-1) * [[0, p-1], [p-1, 1]]
    # = [[0, 1], [1, p-1]] mod p
    det_inv = pow(-1, -1, p)  # = p-1
    E_inv = (0 % p, (p-1) % p, (p-1) % p, 1 % p)  # [[0, -1], [-1, 1]] * det_inv
    # Actually E^(-1) = [[0, 1], [1, -1]] = [[0, 1], [1, p-1]]
    E_inv = (0, 1, 1, p-1)

    # Verify E * E_inv = I
    prod = mat_mult_mod(E, E_inv, p)
    print(f"E = {E}")
    print(f"E^(-1) = {E_inv}")
    print(f"E * E^(-1) = {prod} (should be (1,0,0,1))")

    # Step 2: Can we get E^(-1) from the closure?
    # E is in GL_2(F_p), so E has finite order dividing |GL_2(F_p)|
    # E^(-1) = E^(ord-1)
    power = E
    for k in range(1, p**4):
        power = mat_mult_mod(power, E, p)
        if power == (1, 0, 0, 1):
            print(f"E has order {k+1} mod {p}")
            break

    # E^(-1) = E^(order-1)
    E_inv_from_closure = E
    for _ in range(k - 1):
        E_inv_from_closure = mat_mult_mod(E_inv_from_closure, E, p)
    print(f"E^(order-1) = {E_inv_from_closure} (should match E^(-1) = {E_inv})")

    # Step 3: Build K_u = [[u, 1], [1, 0]]
    # K_1 = E
    # K_2 = E^2 ∘ E (Hadamard of E^2 with E)
    E2 = mat_mult_mod(E, E, p)
    K2 = had_mod(E2, E, p)
    print(f"\nE^2 = {E2}")
    print(f"K_2 = E^2 ∘ E = {K2} (should be (2,1,1,0) mod {p})")

    # K_{u+1} = K_2 * E^(-1) * K_u
    print("\nBuilding K_u for u = 1..p-1:")
    K = {1: E}
    K_prev = E
    for u in range(2, p):
        if u == 2:
            K[u] = K2
        else:
            # K_{u} = K_2 * E^(-1) * K_{u-1}
            # Wait, GPT says K_{u+1} = K_2 * E^{-1} * K_u
            # So K_3 = K_2 * E^{-1} * K_2
            temp = mat_mult_mod(K2, E_inv, p)
            K[u] = mat_mult_mod(temp, K[u-1], p)
        expected = (u % p, 1, 1, 0)
        match = K[u] == expected
        print(f"  K_{u} = {K[u]}, expected {expected}, match = {match}")

    # Step 4: Build U_t and L_t
    print("\nUpper triangular U_t = K_{t+1} * E^(-1):")
    for t in range(p):
        Ut = mat_mult_mod(K.get(t+1, K.get((t+1) % p, None)) if t+1 <= p-1
                          else mat_mult_mod(K2, E_inv, p),  # placeholder
                          E_inv, p)
        # Actually K_{t+1} might need t+1 mod p
        if (t+1) % p in K:
            Ku = K[(t+1) % p]
        elif (t+1) % p == 0:
            # K_0 = [[0,1],[1,0]] - the permutation matrix
            Ku = (0, 1, 1, 0)
        else:
            continue
        Ut = mat_mult_mod(Ku, E_inv, p)
        expected = (1, t % p, 0, 1)
        print(f"  U_{t} = {Ut}, expected {expected}, match = {Ut == expected}")

    # Verify: does the closure equal M_2(F_p) even without Hadamard?
    # (It shouldn't - matrix mult alone gives GL_2 plus some singular matrices)
    print("\n=== Matrix product only (no Hadamard) ===")
    S_mult = {E}
    for it in range(200):
        new = set()
        for A in list(S_mult):
            for B in list(S_mult):
                new.add(mat_mult_mod(A, B, p))
        added = new - S_mult
        if not added:
            break
        S_mult |= new
    print(f"p=7: matrix product only: |S| = {len(S_mult)}, |M_2| = {7**4}")

    # And Hadamard only?
    S_had = {E}
    for it in range(200):
        new = set()
        for A in list(S_had):
            for B in list(S_had):
                new.add(had_mod(A, B, p))
        added = new - S_had
        if not added:
            break
        S_had |= new
    print(f"p=7: Hadamard only: |S| = {len(S_had)}")


if __name__ == "__main__":
    main()

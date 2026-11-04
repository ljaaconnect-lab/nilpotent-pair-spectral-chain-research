"""Exact checks for the permanental-adjugate implicit-lift investigation.

No changes to candidate.py or the frozen development evaluator are made.
Symbolic checks use SymPy polynomial expansion, not numerical tolerances.
"""
from itertools import combinations, permutations
import json
import random

import sympy as sp

from verify_lifting import determinant, permanent, omega_binomial, gf2_rank


def minor(a, rr, cc):
    return [[v for j, v in enumerate(row) if j not in cc]
            for i, row in enumerate(a) if i not in rr]


def gradient(a):
    n = len(a)
    return [[permanent(minor(a, {i}, {j})) for j in range(n)] for i in range(n)]


def permanent_defect(a, i, k, j, l):
    p = permanent(a)
    g = gradient(a)
    numerator = g[i][j] * g[k][l] + g[i][l] * g[k][j] - p * permanent(minor(a, {i, k}, {j, l}))
    return sp.expand(numerator / 2) if any(isinstance(x, sp.Basic) for row in a for x in row) else numerator // 2


def defect_recursion(a):
    """K for distinguished rows/columns 0,1, via the exact block recurrence."""
    c = minor(a, {0, 1}, {0, 1})
    m = len(c)
    gc = gradient(c)
    u, v = a[0][2:], a[1][2:]
    w, x = [a[r + 2][0] for r in range(m)], [a[r + 2][1] for r in range(m)]
    repeated = 0
    nested = 0
    for r in range(m):
        for s in range(m):
            for j in range(m):
                for k in range(m):
                    weight = u[j] * v[k] * w[r] * x[s]
                    if r == s or j == k:
                        repeated += weight * gc[r][j] * gc[s][k]
                    else:
                        nested += weight * permanent_defect(c, r, s, j, k)
    return repeated + nested, repeated, nested


def first_defect_lifts(a):
    n = len(a)
    d = determinant(a)
    r = [[0 if i == k else sum(a[k][j] * a[k][l] * determinant(minor(a, {i, k}, {j, l}))
                               for j, l in combinations(range(n), 2))
          for k in range(n)] for i in range(n)]
    s = -d ** (n - 2) * omega_binomial(a, 1)
    return d, r, s


def frozen_first_correction_system(a):
    """The concrete wrong lift whose first corrections are frozen at precision 1."""
    d, r, s = first_defect_lifts(a)
    n = len(a)

    def f(p):
        return determinant([[p * (i == j) + 2 * r[i][j] for j in range(n)] for i in range(n)]) - d * p ** (n - 1) - 2 * d * s

    def df(p):
        matrix = [[p * (i == j) + 2 * r[i][j] for j in range(n)] for i in range(n)]
        return sum(determinant(minor(matrix, {i}, {i})) for i in range(n)) - d * (n - 1) * p ** (n - 2)

    p = d % 2
    precision = 1
    trace = [{"precision_bits": precision, "root": p, "permanent_residue": permanent(a) % 2}]
    while precision < 16:
        precision *= 2
        modulus = 1 << precision
        p = (p - f(p) * pow(df(p), -1, modulus)) % modulus
        assert f(p) % modulus == 0
        trace.append({"precision_bits": precision, "root": p, "permanent_residue": permanent(a) % modulus})
    return {"B": a, "determinant": d, "permanent": permanent(a), "R0": r, "S0": s,
            "residual_at_true_permanent": f(permanent(a)), "newton_trace": trace}


def fixed_minor_system_jacobian_rank(n):
    """At B=I, P=1, G=I, treating exact H,K as supplied input polynomials."""
    p_index = n * n
    equations = []
    for i in range(n):
        equations.append((1 << p_index) ^ (1 << (i * n + i)))
    selected = []
    for i in range(n):
        for j in range(n):
            if i != j:
                k = next(k for k in range(n) if k not in (i, j))
                selected.append((i, k, j, k))
    selected.append((0, 1, 0, 1))
    for i, k, j, l in selected:
            row = (1 << p_index) if {i, k} == {j, l} else 0
            if k == l:
                row ^= 1 << (i * n + j)
            if i == j:
                row ^= 1 << (k * n + l)
            if k == j:
                row ^= 1 << (i * n + l)
            if i == l:
                row ^= 1 << (k * n + j)
            equations.append(row)
    return gf2_rank(equations)


def newton_small_exact(a):
    """Actual formal-series Newton solver using explicit n=3,4 H,K formulas.

    Everything is integer arithmetic. No permanent of size >2 is used in
    constructing the system coefficients; the full permanent is used only
    afterwards as an independent finite-size verification reference.
    """
    n = len(a)
    assert n in (3, 4)
    length = n + 1
    zero = [0] * length
    const = lambda x: [x] + [0] * (length - 1)
    add = lambda x, y: [a + b for a, b in zip(x, y)]
    neg = lambda x: [-v for v in x]
    sub = lambda x, y: add(x, neg(y))
    mul = lambda x, y: [sum(x[j] * y[k-j] for j in range(k+1)) for k in range(length)]
    times = lambda c, x: [c * v for v in x]

    b = [[[(i == j), a[i][j] - (i == j)] + [0] * (length - 2)
          for j in range(n)] for i in range(n)]
    pp = lambda entries: (const(1) if len(entries) == 0 else entries[0][0]
                          if len(entries) == 1 else add(mul(entries[0][0], entries[1][1]),
                                                        mul(entries[0][1], entries[1][0])))

    def hk(i, k, j, l):
        rr = [r for r in range(n) if r not in (i, k)]
        cc = [s for s in range(n) if s not in (j, l)]
        c = [[b[r][s] for s in cc] for r in rr]
        gc = [[pp(minor(c, {r}, {s})) for s in range(n-2)] for r in range(n-2)]
        value = list(zero)
        for r in range(n-2):
            for s in range(n-2):
                for u in range(n-2):
                    for v in range(n-2):
                        if r == s or u == v:
                            term = mul(mul(b[i][cc[u]], b[k][cc[v]]), mul(b[rr[r]][j], b[rr[s]][l]))
                            value = add(value, mul(term, mul(gc[r][u], gc[s][v])))
        return pp(c), value

    off = [(i, j, next(k for k in range(n) if k not in (i, j)))
           for i in range(n) for j in range(n) if i != j]
    pairs = [(i, k, j, k) for i, j, k in off] + [(0, 1, 0, 1)]
    coefficients = [hk(*p) for p in pairs]
    gi = lambda i, j: 1 + i*n + j
    size = n*n + 1

    def equations(y):
        f, jac = [], []
        for i in range(n):
            value = neg(y[0])
            row = [list(zero) for _ in range(size)]
            row[0] = const(-1)
            for j in range(n):
                value = add(value, mul(b[i][j], y[gi(i,j)]))
                row[gi(i,j)] = b[i][j]
            f.append(value)
            jac.append(row)
        for (i,k,j,l), (h, defect) in zip(pairs, coefficients):
            value = sub(add(mul(y[gi(i,j)], y[gi(k,l)]), mul(y[gi(i,l)], y[gi(k,j)])),
                        add(mul(y[0], h), times(2, defect)))
            row = [list(zero) for _ in range(size)]
            row[0] = neg(h)
            for u,v in [(gi(i,j),gi(k,l)), (gi(k,l),gi(i,j)),
                        (gi(i,l),gi(k,j)), (gi(k,j),gi(i,l))]:
                row[u] = add(row[u], y[v])
            f.append(value)
            jac.append(row)
        return f, jac

    def j0_inverse(rhs):
        answer = [0] * size
        answer[0] = rhs[-1] - rhs[0] - rhs[1]
        for i in range(n):
            answer[gi(i,i)] = rhs[i] + answer[0]
        for index, (i,j,_) in enumerate(off):
            answer[gi(i,j)] = rhs[n+index]
        return answer

    y = [const(1)] + [const(i == j) for i in range(n) for j in range(n)]
    precision = 1
    trace = []
    while precision < length:
        new_precision = min(2*precision, length)
        f, jac = equations(y)
        delta = [[0] * length for _ in range(size)]
        for degree in range(new_precision):
            rhs = [-f[row][degree] - sum(jac[row][col][e] * delta[col][degree-e]
                    for col in range(size) for e in range(1, degree+1)) for row in range(size)]
            coefficient = j0_inverse(rhs)
            for col in range(size):
                delta[col][degree] = coefficient[col]
        for col in range(size):
            y[col] = [y[col][degree] + delta[col][degree] if degree < new_precision else 0
                      for degree in range(length)]
        residual, _ = equations(y)
        assert all(v == 0 for row in residual for v in row[:new_precision])
        precision = new_precision
        trace.append({"precision_in_t": precision, "P_coefficients": y[0][:precision]})
    reference = list(zero)
    for permutation in permutations(range(n)):
        term = const(1)
        for i,j in enumerate(permutation):
            term = mul(term, b[i][j])
        reference = add(reference, term)
    assert y[0] == reference
    assert sum(y[0]) == permanent(a)
    return {"n": n, "B": a, "newton_trace": trace,
            "exact_P_coefficients": y[0], "at_t_one": sum(y[0]),
            "system_coefficients_use_only_size_one_or_two_permanents": True}


def main():
    symbolic = []
    for n in (3, 4):
        symbols = sp.symbols(f'b0:{n*n}')
        a = [list(symbols[i * n:(i + 1) * n]) for i in range(n)]
        p, g = permanent(a), gradient(a)
        k = permanent_defect(a, 0, 1, 0, 1)
        reconstructed, repeated, nested = defect_recursion(a)
        assert sp.expand(k - reconstructed) == 0
        assert sp.expand(nested) == 0
        if n == 3:
            assert sp.expand(k - a[0][2] * a[1][2] * a[2][0] * a[2][1]) == 0
        for i in range(n):
            for row in range(n):
                lhs = sum(a[row][j] * g[i][j] for j in range(n))
                if i == row:
                    assert sp.expand(lhs - p) == 0
                else:
                    rhs = 2 * sum(a[row][j] * a[row][l] * permanent(minor(a, {i, row}, {j, l}))
                                  for j, l in combinations(range(n), 2))
                    assert sp.expand(lhs - rhs) == 0
        # Two row replacements create three equal rows with factorial 3!.
        replaced = [list(row) for row in a]
        replaced[0] = list(a[2])
        replaced[1] = list(a[2])
        q3 = sum(sp.prod(a[2][j] for j in cols) * permanent(minor(a, {0, 1, 2}, set(cols)))
                 for cols in combinations(range(n), 3))
        assert sp.expand(permanent(replaced) - 6 * q3) == 0
        symbolic.append({"n": n, "K_monomials": len(sp.Poly(k, *symbols).terms()),
                         "K": str(k), "block_identity_exact": True,
                         "adjugate_defect_exact": True, "triple_row_factorial_exact": True})

    rng = random.Random(20261024)
    numeric = 0
    for n in (3, 4, 5):
        for _ in range(5):
            a = [[rng.choice([1, 2, 5]) for _ in range(n)] for _ in range(n)]
            p, g = permanent(a), gradient(a)
            reconstructed, _, _ = defect_recursion(a)
            assert permanent_defect(a, 0, 1, 0, 1) == reconstructed
            d, r0, s0 = first_defect_lifts(a)
            for i in range(n):
                for k in range(n):
                    actual = sum(a[k][j] * g[i][j] for j in range(n)) - p * (i == k)
                    assert actual % 2 == 0
                    assert (actual // 2 - r0[i][k]) % 2 == 0
            s_actual_numerator = determinant(g) - p ** (n - 1)
            assert s_actual_numerator % 2 == 0
            assert (s_actual_numerator // 2 - s0) % 2 == 0
            numeric += 1

    examples = [frozen_first_correction_system(a) for a in (
        [[5, 2, 5], [5, 2, 2], [1, 1, 5]],
        [[5, 2, 2, 1], [2, 1, 5, 2], [5, 2, 1, 2], [2, 1, 1, 1]])]
    for example in examples:
        assert example["residual_at_true_permanent"] % 8 == 4
        assert example["newton_trace"][1]["root"] == example["newton_trace"][1]["permanent_residue"]
        assert example["newton_trace"][2]["root"] != example["newton_trace"][2]["permanent_residue"]
    ranks = [{"n": n, "rank": fixed_minor_system_jacobian_rank(n), "unknowns": n * n + 1}
             for n in range(3, 9)]
    assert all(x["rank"] == x["unknowns"] for x in ranks)
    exact_small_newton = [newton_small_exact(example["B"]) for example in examples]
    print(json.dumps({"symbolic_certificates": symbolic, "numeric_checks": numeric,
                      "fixed_minor_jacobian_ranks": ranks, "wrong_newton_lifts": examples,
                      "exact_small_newton_systems": exact_small_newton,
                      "uniform_closed_system_found": False, "candidate_evaluator_run": False}, indent=2))


if __name__ == "__main__":
    main()

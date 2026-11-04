"""Exact exploratory checks; deliberately separate from the frozen evaluator.

This is not a scalar-DAG candidate and does not claim a polynomial compiler.
All arithmetic checks use integers or Fraction, without numerical tolerances.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations
import json
import random


def inversions(p):
    return sum(p[i] > p[j] for i in range(len(p)) for j in range(i + 1, len(p)))


def product(xs):
    ans = 1
    for x in xs:
        ans *= x
    return ans


def determinant(a):
    return sum((-1) ** inversions(p) * product(a[i][p[i]] for i in range(len(a)))
               for p in permutations(range(len(a))))


def permanent(a):
    return sum(product(a[i][p[i]] for i in range(len(a)))
               for p in permutations(range(len(a))))


def choose(n, k):
    if k < 0 or k > n:
        return 0
    r = 1
    for j in range(k):
        r = r * (n - j) // (j + 1)
    return r


def omega_binomial(a, r):
    return sum((-1) ** inversions(p) * choose(inversions(p), r)
               * product(a[i][p[i]] for i in range(len(a)))
               for p in permutations(range(len(a))))


def partial_cofactor(a, cells):
    cells = tuple(sorted(cells))
    rs = [i for i, _ in cells]
    cs = [j for _, j in cells]
    assert len(set(rs)) == len(rs) and len(set(cs)) == len(cs)
    sign = (-1) ** (sum(rs) + sum(cs) + inversions(cs))
    minor = [[a[i][j] for j in range(len(a)) if j not in cs]
             for i in range(len(a)) if i not in rs]
    return sign * determinant(minor)


def marked_inversion_expansion(a, r):
    n = len(a)
    edges = [((i, j), (k, l)) for i in range(n) for k in range(i + 1, n)
             for j in range(n) for l in range(j)]
    multiplicities = Counter()
    for es in combinations(edges, r):
        cells = tuple(sorted({v for e in es for v in e}))
        if len({i for i, _ in cells}) < len(cells):
            continue
        if len({j for _, j in cells}) < len(cells):
            continue
        multiplicities[cells] += 1
    result = sum(c * product(a[i][j] for i, j in cells) * partial_cofactor(a, cells)
                 for cells, c in multiplicities.items())
    return result, len(multiplicities)


def inverse(a):
    n = len(a)
    rows = [[Fraction(v) for v in row] + [Fraction(i == j) for j in range(n)]
            for i, row in enumerate(a)]
    for j in range(n):
        k = next(k for k in range(j, n) if rows[k][j])
        rows[k], rows[j] = rows[j], rows[k]
        s = rows[j][j]
        rows[j] = [v / s for v in rows[j]]
        for k in range(n):
            if k != j:
                s = rows[k][j]
                rows[k] = [v - s * w for v, w in zip(rows[k], rows[j])]
    return [row[n:] for row in rows]


def gf2_rank(rows):
    rows = list(rows)
    rank = 0
    for j in range(max((x.bit_length() for x in rows), default=0)):
        p = next((i for i in range(rank, len(rows)) if rows[i] >> j & 1), None)
        if p is None:
            continue
        rows[rank], rows[p] = rows[p], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i] >> j & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def grid_polar(n):
    return [sum(1 << (k * n + l) for k in range(n) for l in range(n)
                if (i - k) * (j - l) < 0)
            for i in range(n) for j in range(n)]


def affine_basis(n):
    return [(1 << (i * n + j)) ^ (1 << (i * n + n - 1))
            ^ (1 << ((n - 1) * n + j)) ^ (1 << (n * n - 1))
            for i in range(n - 1) for j in range(n - 1)]


def restricted_polar(rows, basis):
    answer = []
    for x in basis:
        kx = sum(((r & x).bit_count() % 2) << i for i, r in enumerate(rows))
        answer.append(sum(((kx & y).bit_count() % 2) << j for j, y in enumerate(basis)))
    return answer


def grid_q(n, x):
    return sum(((x >> (i * n + j)) & (x >> (k * n + l)) & 1)
               for i in range(n) for k in range(i + 1, n)
               for j in range(n) for l in range(j)) % 2


def walsh(values):
    values = list(values)
    step = 1
    while step < len(values):
        for start in range(0, len(values), 2 * step):
            for i in range(start, start + step):
                a, b = values[i], values[i + step]
                values[i], values[i + step] = a + b, a - b
        step *= 2
    return values


def walsh_summary(values):
    transformed = walsh(values)
    return {"support": sum(v != 0 for v in transformed),
            "nonzero_absolute_values": sorted({abs(v) for v in transformed if v})}


def edge_cover_gauss(p):
    n = len(p)
    return sum((-1) ** (n - mask.bit_count()
                       + inversions([p[i] for i in range(n) if mask >> i & 1]))
               for mask in range(1 << n))


def gauss_elimination(p):
    """Evaluate (6) in O(n^3) elementary bit operations, no subset table."""
    n = len(p)
    active = set(range(n))
    edges = {(i, j) for i in range(n) for j in range(i + 1, n) if p[i] > p[j]}
    linear = set(active)
    constant = n % 2
    factor = 1
    while edges:
        i, j = min(edges)
        left = {b if a == i else a for a, b in edges if (a == i or b == i) and j not in (a, b)}
        right = {b if a == j else a for a, b in edges if (a == j or b == j) and i not in (a, b)}
        a, b = int(i in linear), int(j in linear)
        edges = {e for e in edges if i not in e and j not in e}
        linear.difference_update((i, j))
        constant ^= a * b
        if a:
            linear.symmetric_difference_update(right)
        if b:
            linear.symmetric_difference_update(left)
        for u in left:
            for v in right:
                if u == v:
                    linear.symmetric_difference_update((u,))
                else:
                    edges.symmetric_difference_update((tuple(sorted((u, v))),))
        active.difference_update((i, j))
        factor *= 2
    if linear:
        return 0
    return (-1) ** constant * factor * (1 << len(active))


def main():
    rng = random.Random(20261024)
    checked_lifts = 0
    checked_jacobi = 0
    normal_order = []
    for n in range(1, 6):
        for _ in range(3):
            a = [[rng.randrange(1, 9) for _ in range(n)] for _ in range(n)]
            d = n * (n - 1) // 2
            assert sum((-2) ** r * omega_binomial(a, r) for r in range(d + 1)) == permanent(a)
            for k in range(1, d + 2):
                truncated = sum((-2) ** r * omega_binomial(a, r) for r in range(min(k, d + 1)))
                assert (permanent(a) - truncated) % (1 << k) == 0
            checked_lifts += 1
            if determinant(a):
                c = inverse(a)
                j = determinant(a) * sum(a[i][j] * a[k][l]
                    * (c[j][i] * c[l][k] - c[j][k] * c[l][i])
                    for i in range(n) for k in range(i + 1, n)
                    for j in range(n) for l in range(j))
                assert j == omega_binomial(a, 1)
                checked_jacobi += 1
    a = [[2, 3, 5, 7], [11, 13, 17, 19], [23, 29, 31, 37], [41, 43, 47, 53]]
    for r in range(4):
        observed, groups = marked_inversion_expansion(a, r)
        assert observed == omega_binomial(a, r)
        normal_order.append({"n": 4, "r": r, "distinct_partial_matchings": groups})

    ranks = []
    for n in range(1, 17):
        full = gf2_rank(grid_polar(n))
        affine = gf2_rank(restricted_polar(grid_polar(n), affine_basis(n)))
        assert full == n * (n - 1)
        assert affine == (n - 1) * (n - 2)
        ranks.append({"n": n, "grid_rank": full, "row_column_affine_rank": affine})

    full_walsh = walsh_summary([(-1) ** grid_q(3, x) for x in range(1 << 9)])
    assert full_walsh == {"support": 64, "nonzero_absolute_values": [64]}
    basis = affine_basis(4)
    base = sum(1 << (i * 4 + i) for i in range(4))
    vals = []
    for mask in range(1 << len(basis)):
        x = base
        for i, b in enumerate(basis):
            if mask >> i & 1:
                x ^= b
        vals.append((-1) ** grid_q(4, x))
    affine_walsh = walsh_summary(vals)
    assert affine_walsh == {"support": 64, "nonzero_absolute_values": [64]}

    marked_n3 = []
    for p in permutations(range(3)):
        inv = inversions(p)
        marked_n3.append({"permutation": p, "exponent": sum(1 << (3 * i + p[i]) for i in range(3)),
                          "inversions": inv, "determinant_coefficient": (-1) ** inv,
                          "first_lift_coefficient": (-1) ** inv * (1 - 2 * inv),
                          "permanent_coefficient": 1})

    # Exact polynomial coefficients of the Plucker expression at q=-1+t.
    a, b = [1, 2, 3, 4], [5, 6, 7, 8]
    f = lambda i, j: (a[i] * b[j] - a[j] * b[i], a[j] * b[i])
    mul = lambda u, v: (u[0] * v[0], u[0] * v[1] + u[1] * v[0], u[1] * v[1])
    terms = [mul(f(0, 1), f(2, 3)), mul(f(0, 2), f(1, 3)), mul(f(0, 3), f(1, 2))]
    plucker = [terms[0][i] - terms[1][i] + terms[2][i] for i in range(3)]
    assert plucker == [0, -136, 280]

    gauss_checked = 0
    for n in range(7):
        for p in permutations(range(n)):
            assert gauss_elimination(p) == edge_cover_gauss(p)
            gauss_checked += 1

    result = {"exact_lift_instances": checked_lifts, "jacobi_instances": checked_jacobi,
              "normal_order_checks": normal_order, "rank_checks": ranks,
              "full_grid_n3_walsh": full_walsh, "affine_n4_walsh": affine_walsh,
              "reverse_matching_edge_cover_weights": [edge_cover_gauss(tuple(range(n - 1, -1, -1))) for n in range(13)],
              "plucker_coefficients_at_q_minus_one_plus_t": plucker,
              "polynomial_gauss_elimination_checks": gauss_checked,
              "marked_n3": marked_n3,
              "candidate_evaluator_run": False, "uniform_polynomial_compiler_found": False}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

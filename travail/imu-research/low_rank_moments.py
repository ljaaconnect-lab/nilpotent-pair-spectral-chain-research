"""Exact collision-moment initializer on a supplied rank-r factorization.

This is polynomial only for r fixed independently of n. It does not bound
the generic initializer for arbitrary original a,z inputs.
"""
from itertools import product
from math import factorial, comb
from pathlib import Path
import json
import random


def indices(r, n):
    return [a for a in product(range(n + 1), repeat=r) if sum(a) <= n]


def initialize(U, V, prime):
    n, r = len(U), len(U[0])
    h = comb(n, 2)
    all_a = indices(r, n)
    zero = (0,) * r
    # F_U(x) = product_i (sum_alpha U_i,alpha x_alpha).
    F = {zero: 1}
    for row in U:
        out = {}
        for a, value in F.items():
            for p, u in enumerate(row):
                b = tuple(v + (j == p) for j, v in enumerate(a))
                out[b] = (out.get(b, 0) + value * u) % prime
        F = out
    # H_V = product_j sum_|a|<=n V_j^a / a! x^a w^C(|a|,2).
    H = {(zero, 0): 1}
    for row in V:
        factor = []
        for a in all_a:
            value = 1
            for x, power in zip(row, a):
                value = value * pow(x, power, prime) % prime
                value = value * pow(factorial(power), -1, prime) % prime
            factor.append((a, comb(sum(a), 2), value))
        out = {}
        for (a, k), value in H.items():
            for b, ell, other in factor:
                ab = tuple(x + y for x, y in zip(a, b))
                if sum(ab) > n or k + ell > h:
                    continue
                key = (ab, k + ell)
                out[key] = (out.get(key, 0) + value * other) % prime
        H = out
    spectrum = [0] * (h + 1)
    for a, value in F.items():
        af = 1
        for k in a:
            af = af * factorial(k) % prime
        for k in range(h + 1):
            spectrum[k] = (spectrum[k] + af * value * H.get((a, k), 0)) % prime
    return [sum(c * pow(k, j, prime) for k, c in enumerate(spectrum)) % prime
            for j in range(h + 1)], spectrum


def oracle(U, V, prime):
    n, r = len(U), len(U[0])
    h = comb(n, 2)
    B = [[sum(U[i][a] * V[j][a] for a in range(r)) % prime
          for j in range(n)] for i in range(n)]
    spectrum = [0] * (h + 1)
    for assignment in product(range(n), repeat=n):
        value = 1
        for i, j in enumerate(assignment):
            value = value * B[i][j] % prime
        occ = [assignment.count(j) for j in range(n)]
        kappa = sum(comb(m, 2) for m in occ)
        spectrum[kappa] = (spectrum[kappa] + value) % prime
    return [sum(c * pow(k, j, prime) for k, c in enumerate(spectrum)) % prime
            for j in range(h + 1)], spectrum


def main():
    rng = random.Random(20261103)
    cases = []
    for n in range(1, 6):
        for r in range(1, min(n, 3) + 1):
            for prime in (101, 1009):
                for trial in range(3):
                    U = [[rng.randrange(prime) for _ in range(r)] for _ in range(n)]
                    V = [[rng.randrange(prime) for _ in range(r)] for _ in range(n)]
                    if trial == 1:
                        U[0] = [0] * r
                    actual = initialize(U, V, prime)
                    expected = oracle(U, V, prime)
                    assert actual == expected, (n, r, prime, trial)
                    cases.append(dict(n=n, rank_parameter=r, prime=prime, trial=trial))
    report = dict(cases=len(cases), passed=True, details=cases,
                  scope='Exact all-moment initialization on supplied rank-r factorization; polynomial for fixed r only; no generic I_mu(n) polynomial claim.')
    Path(__file__).with_name('low-rank-validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'details'}))


if __name__ == '__main__':
    main()

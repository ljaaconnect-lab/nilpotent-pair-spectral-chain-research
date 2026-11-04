"""Exact, small-case checks for the projector-generating-function research.

This is independent verification, not a polynomial-time compiler. Exhaustive
assignments and subset contractions here are explicitly charged in the note.
The frozen evaluator and dag.py are not changed or imported as an oracle.
"""
from collections import defaultdict
from fractions import Fraction
from itertools import product, permutations
from math import comb, factorial, prod
from random import Random
import json


def add(a, b):
    c = [0] * max(len(a), len(b))
    for i, v in enumerate(a): c[i] += v
    for i, v in enumerate(b): c[i] += v
    while len(c) > 1 and c[-1] == 0: c.pop()
    return c


def scale(a, c):
    return [c * v for v in a]


def mul(a, b):
    c = [0] * (len(a) + len(b) - 1)
    for i, v in enumerate(a):
        for j, w in enumerate(b): c[i+j] += v * w
    while len(c) > 1 and c[-1] == 0: c.pop()
    return c


def peval(a, q):
    y = 0
    for v in reversed(a): y = y * q + v
    return y


def spectrum(n):
    """Partition energies, in O(n^4) elementary set operations or less."""
    states = [{0}]
    for total in range(1, n+1):
        states.append({e + comb(m, 2) for m in range(1, total+1)
                       for e in states[total-m]})
    return sorted(states[n])


def collision_coefficients(b):
    n = len(b)
    c = [0] * (comb(n, 2)+1)
    for choices in product(range(n), repeat=n):
        counts = [choices.count(j) for j in range(n)]
        energy = sum(comb(k, 2) for k in counts)
        c[energy] += prod(b[i][j] for i, j in enumerate(choices))
    return c


def occupation_update(b, q):
    n = len(b)
    states = {(0,) * n: 1}
    for row in b:
        next_states = defaultdict(int)
        for m, value in states.items():
            for j, weight in enumerate(row):
                v = list(m); v[j] += 1
                next_states[tuple(v)] += weight * q ** m[j] * value
        states = next_states
    return sum(states.values())


def cumulants(n):
    a = [[1]]
    for k in range(1, n+1):
        a.append([0] * comb(k, 2) + [1])
    c = [[0]]
    for k in range(1, n+1):
        ck = a[k]
        for r in range(1, k):
            ck = add(ck, scale(mul(c[r], a[k-r]), -comb(k-1, r-1)))
        c.append(ck)
    return c


def block_weights(b):
    n = len(b)
    return {mask: sum(prod(b[i][j] for i in range(n) if mask >> i & 1)
                      for j in range(n))
            for mask in range(1, 1 << n)}


def bell_contraction(b, q):
    n = len(b)
    c = [peval(poly, q) for poly in cumulants(n)]
    weights = block_weights(b)
    f = {0: 1}
    for mask in range(1, 1 << n):
        anchor = mask & -mask
        total = 0
        sub = mask
        while sub:
            if sub & anchor:
                total += c[sub.bit_count()] * weights[sub] * f[mask ^ sub]
            sub = (sub-1) & mask
        f[mask] = total
    return f[(1 << n)-1]


def rational_resolvent(coeffs, values):
    nonzero = [v for v in values if v]
    denominator = [1]
    for v in nonzero: denominator = mul(denominator, [1, -v])
    numerator = scale(denominator, coeffs[0])
    for v in nonzero:
        quotient = [1]
        for w in nonzero:
            if w != v: quotient = mul(quotient, [1, -w])
        numerator = add(numerator, scale(quotient, coeffs[v]))
    return numerator, denominator


def marker_moment_identity(b):
    """Check L^k(t_j H)=t_j(L+E_j)^k H at t=1 exactly."""
    n = len(b)
    prefix = b[:-1]
    for j in range(n):
        for k in range(6):
            lhs = rhs = 0
            for choices in product(range(n), repeat=len(prefix)):
                m = [choices.count(a) for a in range(n)]
                energy = sum(comb(v, 2) for v in m)
                weight = prod(prefix[i][a] for i, a in enumerate(choices))
                lhs += weight * (energy + m[j]) ** k
                rhs += weight * sum(comb(k, r) * energy ** (k-r) * m[j] ** r
                                    for r in range(k+1))
            assert lhs == rhs


def scalar_bell_data(b):
    w = block_weights(b)
    return [sum(v for mask, v in w.items() if mask.bit_count() == k)
            for k in range(1, len(b)+1)]


def normalized_resolvent_coefficients(b, degree):
    n = len(b)
    numerator = [1]
    for i in range(n): numerator = mul(numerator, [1, b[i][i]])
    denominator = [0]
    for permutation in permutations(range(n)):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(n) for j in range(i+1, n))
        term = [(-1) ** inversions]
        for i, j in enumerate(permutation):
            term = mul(term, [int(i == j), -b[i][j] if i != j else 0])
        denominator = add(denominator, term)
    assert denominator[0] == 1
    result = []
    for k in range(degree+1):
        ak = numerator[k] if k < len(numerator) else 0
        result.append(ak - sum(denominator[j]*result[k-j]
                              for j in range(1, min(k, len(denominator)-1)+1)))
    return result


def main():
    rng = Random(20261024)
    checks = 0
    for n in range(1, 6):
        values = spectrum(n)
        for case in range(4):
            b = [[1+rng.randrange(-3, 4)**2 for _ in range(n)] for _ in range(n)]
            coeffs = collision_coefficients(b)
            assert set(i for i, v in enumerate(coeffs) if v) == set(values)
            for q in [0, 1, -1, 2, Fraction(2, 3)]:
                expected = peval(coeffs, q)
                assert occupation_update(b, q) == expected
                assert bell_contraction(b, q) == expected
                checks += 2
            numerator, denominator = rational_resolvent(coeffs, values)
            d = len(values)-1
            assert numerator[d] == denominator[d] * coeffs[0]
            moments = [sum(coeffs[v] * v**r for v in values) for r in range(2*d+5)]
            # D(s) F(s)=N(s); from degree d+1 onward the moments recur.
            for r in range(d+1, len(moments)):
                assert sum(denominator[k] * moments[r-k]
                           for k in range(d+1)) == 0
            p = [Fraction(1)]
            for v in values:
                if v: p = mul(p, [1, Fraction(-1, v)])
            assert sum(p[r] * moments[r] for r in range(d+1)) == coeffs[0]
            marker_moment_identity(b)
            checks += 3
    for n in range(1, 11):
        c = cumulants(n)
        for k in range(1, n+1):
            assert peval(c[k], 0) == (-1)**(k-1) * factorial(k-1)
    b = [[1, 2], [5, 10]]
    bp = [[1, 10], [5, 2]]
    assert scalar_bell_data(b) == scalar_bell_data(bp) == [18, 25]
    assert bell_contraction(b, 0) == 20
    assert bell_contraction(bp, 0) == 52
    for n in range(1, 6):
        diagonal = [[i+2 if i == j else 0 for j in range(n)] for i in range(n)]
        assert normalized_resolvent_coefficients(diagonal, n)[n] == prod(range(2, n+2))
    for case in range(10):
        b2 = [[1+rng.randrange(-3, 4)**2 for _ in range(2)] for _ in range(2)]
        assert normalized_resolvent_coefficients(b2, 2)[2] == bell_contraction(b2, 0)
        b3 = [[1+rng.randrange(-3, 4)**2 for _ in range(3)] for _ in range(3)]
        excess = sum(b3[i][j]*b3[j][i]*(b3[i][i]+b3[j][j])
                     for i in range(3) for j in range(i+1, 3))
        assert normalized_resolvent_coefficients(b3, 3)[3] == bell_contraction(b3, 0)+excess
    j3 = [[1]*3 for _ in range(3)]
    assert normalized_resolvent_coefficients(j3, 3)[3] == 12
    assert bell_contraction(j3, 0) == 6
    summary = {
        'exact_checks': checks,
        'tested_n': [1, 2, 3, 4, 5],
        'q_values': ['0', '1', '-1', '2', '2/3'],
        'scalar_bell_counterexample': {'data': [18, 25], 'permanents': [20, 52]},
        'collision_spectra': {n: spectrum(n) for n in range(1, 11)},
        'normalized_resolvent_counterexample': {'matrix': 'J_3', 'coefficient': 12, 'permanent': 6},
        'normalized_resolvent_additional_checks': 27,
        'global_polynomial_proof': False,
    }
    print(json.dumps(summary, indent=2))


if __name__ == '__main__': main()

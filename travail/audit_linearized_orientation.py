"""Small exact identity checks, NOT a proposed polynomial scalar compiler.

Subset-indexed and multivariate dictionaries below are reference evaluators
used solely to check Fourier identities and the terminal functional.
"""
from itertools import permutations
from math import factorial, prod
import json
import random


def add(p, q, Q):
    out = dict(p)
    for exponent, value in q.items():
        out[exponent] = (out.get(exponent, 0) + value) % Q
        if not out[exponent]:
            del out[exponent]
    return out


def scale(p, value, Q):
    return {e: c*value % Q for e, c in p.items() if c*value % Q}


def mul_q(p, q, Q):
    out = {}
    for a, x in p.items():
        for b, y in q.items():
            if not a & b:
                out = add(out, {a | b: x*y % Q}, Q)
    return out


def linear_sum(vectors, coefficients, Q):
    out = {}
    for vector, coefficient in zip(vectors, coefficients):
        out = add(out, scale(vector, coefficient, Q), Q)
    return out


def dual_polynomial(n, N, omega, Q):
    out = {(0,)*N: 1}
    for j in range(n):
        nxt = {}
        for exponent, value in out.items():
            for f in range(N):
                target = list(exponent)
                target[f] += 1
                nxt = add(nxt, {tuple(target): value*pow(omega, f*j, Q) % Q}, Q)
        out = nxt
    return out


def check(n, rng):
    Q, N = 97, 1 << (n-1).bit_length()
    omega = next(w for w in range(1, Q)
                 if pow(w, N, Q) == 1 and pow(w, N//2, Q) != 1)
    inverse_N = pow(N, -1, Q)
    x = [{1 << j: pow(omega, f*j, Q) for j in range(n)} for f in range(N)]
    for r in range(N):
        convolution = {}
        for f in range(N):
            convolution = add(convolution, mul_q(x[f], x[(r-f) % N], Q), Q)
        assert convolution == {}
    for j in range(N):
        coefficients = [inverse_N*pow(omega, -f*j, Q) % Q for f in range(N)]
        assert linear_sum(x, coefficients, Q) == ({1 << j: 1} if j < n else {})

    dual = dual_polynomial(n, N, omega, Q)
    top = (1 << n)-1
    for _ in range(20):
        frequencies = [rng.randrange(N) for _ in range(n)]
        polynomial = {0: 1}
        for f in frequencies:
            polynomial = mul_q(polynomial, x[f], Q)
        powers = tuple(frequencies.count(f) for f in range(N))
        reader = dual.get(powers, 0)*prod(factorial(k) for k in powers) % Q
        assert reader == polynomial.get(top, 0)

    labels = [(j*j + 2*j + 1) % N for j in range(n)]
    for sample in range(3):
        a = [[rng.randrange(Q) for j in range(n)] for i in range(n)]
        if sample == 1:
            a[0] = [22]*n
        z = 0 if sample == 0 else rng.randrange(1, Q)
        B = [[(1+a[i][j]**2)*pow(z, 2**(i*n+j), Q) % Q
              for j in range(n)] for i in range(n)]
        spectral = []
        for k in range(N):
            polynomial = {0: 1}
            for i in range(n):
                transformed = [sum(B[i][j]*pow(omega, k*labels[j]+f*j, Q)
                                   for j in range(n)) % Q for f in range(N)]
                linearized = linear_sum([x[(-f) % N] for f in range(N)],
                                        [inverse_N*c % Q for c in transformed], Q)
                direct = {1 << j: B[i][j]*pow(omega, k*labels[j], Q) % Q
                          for j in range(n) if B[i][j]}
                assert linearized == direct
                polynomial = mul_q(polynomial, linearized, Q)
            spectral.append(polynomial.get(top, 0))
        result = [inverse_N*sum(spectral[f]*pow(omega, -f*k, Q)
                                for f in range(N)) % Q for k in range(N)]
        scalar = sum(prod(B[i][columns[i]] for i in range(n))
                     for columns in permutations(range(n))) % Q
        expected = [0]*N
        expected[sum(labels) % N] = scalar
        assert result == expected
    return {'n': n, 'N': N, 'Q': Q, 'omega': omega,
            'convolution_relations': N, 'inverse_or_padding_relations': N,
            'dual_reader_monomials_checked': 20, 'complete_tables_checked': 3,
            'dual_reference_monomials': len(dual), 'status': 'passed'}


def occupations(total, length):
    if length == 1:
        yield (total,)
    else:
        for first in range(total+1):
            for suffix in occupations(total-first, length-1):
                yield (first,)+suffix


def two_moment_aliases(n):
    sums = [sum(j**r for j in range(n)) for r in (1, 2)]
    aliases = [m for m in occupations(n, n) if m != (1,)*n and
               all(sum(m[j]*j**r for j in range(n)) == sums[r-1] for r in (1, 2))]
    return {'n': n, 'aliases': len(aliases), 'example': aliases[0] if aliases else None}


if __name__ == '__main__':
    rng = random.Random(20261101)
    print(json.dumps({'linearized_orientation': [check(n, rng) for n in range(3, 7)],
                      'two_additive_moments': [two_moment_aliases(n) for n in range(3, 9)],
                      'polynomial_scalar_compiler_established': False}, indent=2))

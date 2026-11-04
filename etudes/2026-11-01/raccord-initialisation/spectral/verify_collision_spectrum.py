"""Small-order identity verifier; NOT a polynomial scalar compiler."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from pathlib import Path


def collision(m):
    return sum(x * (x - 1) // 2 for x in m)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def mul(F, G, Q, u=1):
    result = {}
    for a, x in F.items():
        for b, y in G.items():
            c = add(a, b)
            result[c] = (result.get(c, 0) + x * y * pow(u, dot(a, b), Q)) % Q
    return {m: x for m, x in result.items() if x}


def deform(F, u, Q):
    return {m: y for m, x in F.items() if (y := x * pow(u, collision(m), Q) % Q)}


def evaluate(F, t, Q):
    total = 0
    for m, x in F.items():
        for a, b in zip(t, m):
            x = x * pow(a, b, Q) % Q
        total += x
    return total % Q


def factors(B):
    n = len(B)
    es = [tuple(int(k == j) for k in range(n)) for j in range(n)]
    return [{es[j]: B[i][j] for j in range(n) if B[i][j]} for i in range(n)]


def product(fs, n, Q, u=1):
    result = {(0,) * n: 1}
    for F in fs:
        result = mul(result, F, Q, u)
    return result


def primitive_root(Q):
    primes = [p for p in range(2, Q) if (Q - 1) % p == 0 and all(p % d for d in range(2, int(p ** .5) + 1))]
    return next(g for g in range(2, Q) if all(pow(g, (Q - 1) // p, Q) != 1 for p in primes))


def next_power_gt(k):
    result = 1
    while result <= k:
        result *= 2
    return result


def reference_assignment(B, t, Q):
    n = len(B)
    h = n * (n - 1) // 2
    coefficients = [0] * (h + 1)
    for js in itertools.product(range(n), repeat=n):
        m = tuple(js.count(j) for j in range(n))
        value = 1
        for i, j in enumerate(js):
            value = value * B[i][j] * t[j] % Q
        coefficients[collision(m)] = (coefficients[collision(m)] + value) % Q
    return coefficients


def formal_z_product(a, t, u, Q):
    """Verifier oracle: occupied-column monomials AND formal z exponents."""
    n = len(a)
    result = {((0,) * n, 0): 1}
    for i in range(n):
        following = {}
        for (m, exponent), coefficient in result.items():
            for j in range(n):
                new_m = tuple(x + int(k == j) for k, x in enumerate(m))
                key = new_m, exponent + 2 ** (i * n + j)
                value = coefficient * (1 + a[i][j] ** 2) * t[j] * pow(u, m[j], Q)
                following[key] = (following.get(key, 0) + value) % Q
        result = {key: c for key, c in following.items() if c}
    scalar_z = {}
    for (_, e), c in result.items():
        scalar_z[e] = (scalar_z.get(e, 0) + c) % Q
    return {e: c for e, c in scalar_z.items() if c}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    source = Path(__file__)
    initial_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    rng = random.Random(20261101)
    associativity = 0
    intertwining = 0
    for Q in (17, 97):
        for _ in range(60):
            fs = [{tuple(rng.randrange(3) for _ in range(3)): rng.randrange(Q) for _ in range(4)} for _ in range(3)]
            u = rng.randrange(Q)
            assert mul(mul(fs[0], fs[1], Q, u), fs[2], Q, u) == mul(fs[0], mul(fs[1], fs[2], Q, u), Q, u)
            associativity += 1
            assert deform(mul(fs[0], fs[1], Q), u, Q) == mul(deform(fs[0], u, Q), deform(fs[1], u, Q), Q, u)
            intertwining += 1
    cases = []
    formal_cases = []
    table_entries = 0
    moments = 0
    for Q in (17, 97):
        g = primitive_root(Q)
        for n in range(1, 7):
            h = n * (n - 1) // 2
            N, M = next_power_gt(n), next_power_gt(h)
            assert (Q - 1) % N == 0 and (Q - 1) % M == 0 and Q > max(2, h)
            omega = pow(g, (Q - 1) // N, Q)
            eta = pow(g, (Q - 1) // M, Q)
            a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
            z = rng.randrange(1, Q)
            B = [[(1 + a[i][j] ** 2) * pow(z, 2 ** (i * n + j), Q) % Q for j in range(n)] for i in range(n)]
            ds = [rng.randrange(N) for _ in range(n)]
            fs = factors(B)
            G = product(fs, n, Q)
            frequency_values = []
            for f in range(N):
                t = [pow(omega, f * d, Q) for d in ds]
                reference = reference_assignment(B, t, Q)
                values = []
                for ell in range(M):
                    u = pow(eta, ell, Q)
                    H = product(fs, n, Q, u)
                    assert H == deform(G, u, Q)
                    actual = evaluate(H, t, Q)
                    expected = sum(c * pow(u, k, Q) for k, c in enumerate(reference)) % Q
                    assert actual == expected
                    values.append(actual)
                    table_entries += 1
                filtered = sum(values) * pow(M, -1, Q) % Q
                assert filtered == reference[0] == evaluate(product(fs, n, Q, 0), t, Q)
                frequency_values.append(filtered)
                for r in range(h + 1):
                    lhs = evaluate({m: c * pow(collision(m), r, Q) % Q for m, c in G.items()}, t, Q)
                    rhs = sum(c * pow(k, r, Q) for k, c in enumerate(reference)) % Q
                    assert lhs == rhs
                    moments += 1
            output = [sum(v * pow(omega, -f * k, Q) for f, v in enumerate(frequency_values)) * pow(N, -1, Q) % Q for k in range(N)]
            target = reference_assignment(B, [1] * n, Q)[0]
            assert output == [target if k == sum(ds) % N else 0 for k in range(N)]
            cases.append({'n': n, 'Q': Q, 'N': N, 'M': M, 'passed': True})
            if n <= 4:
                formal_frequencies = []
                for f in range(N):
                    t = [pow(omega, f * d, Q) for d in ds]
                    accum = {}
                    for ell in range(M):
                        for e, c in formal_z_product(a, t, pow(eta, ell, Q), Q).items():
                            accum[e] = (accum.get(e, 0) + c) % Q
                    accum = {e: c * pow(M, -1, Q) % Q for e, c in accum.items() if c}
                    assert accum == formal_z_product(a, t, 0, Q)
                    formal_frequencies.append(accum)
                target = {}
                for js in itertools.permutations(range(n)):
                    e = sum(2 ** (i * n + j) for i, j in enumerate(js))
                    c = 1
                    for i, j in enumerate(js):
                        c = c * (1 + a[i][j] ** 2) % Q
                    target[e] = (target.get(e, 0) + c) % Q
                target = {e: c for e, c in target.items() if c}
                for k in range(N):
                    actual = {}
                    for f, poly in enumerate(formal_frequencies):
                        scale = pow(omega, -f * k, Q) * pow(N, -1, Q) % Q
                        for e, c in poly.items():
                            actual[e] = (actual.get(e, 0) + scale * c) % Q
                    actual = {e: c for e, c in actual.items() if c}
                    assert actual == (target if k == sum(ds) % N else {})
                formal_cases.append({'n': n, 'Q': Q, 'formal_z': True, 'passed': True})
    # This restricted interface does not retain the cross term needed by fusion.
    assert evaluate({(1, 0): 1}, [1, 1], 17) == evaluate({(0, 1): 1}, [1, 1], 17)
    assert evaluate(mul({(1, 0): 1}, {(1, 0): 1}, 17, 3), [1, 1], 17) == 3
    assert evaluate(mul({(0, 1): 1}, {(1, 0): 1}, 17, 3), [1, 1], 17) == 1
    assert hashlib.sha256(source.read_bytes()).hexdigest() == initial_hash
    result = {
        'status': 'passed',
        'source': source.name,
        'sha256': initial_hash,
        'contract': 'Exponential coefficient/assignment oracles verify identities only; no polynomial scalar circuit is claimed.',
        'general_polynomial_closure': False,
        'associativity_cases': associativity,
        'intertwining_cases': intertwining,
        'spectral_values': table_entries,
        'moment_checks': moments,
        'complete_chain_tables': cases,
        'formal_z_tables': formal_cases,
    }
    if args.write_report:
        source.with_name('collision-spectrum-validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

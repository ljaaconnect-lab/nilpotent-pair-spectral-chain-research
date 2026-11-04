"""Finite verification of the exact dual reader, not a polynomial compiler."""
from __future__ import annotations
import argparse
from functools import lru_cache
from hashlib import sha256
from itertools import product
from math import comb
from pathlib import Path
import json
import random

HERE = Path(__file__).resolve().parent


def kappa(u):
    return sum(x * (x - 1) // 2 for x in u)


def peval(p, x, q):
    out = 0
    for c in reversed(p):
        out = (out * x + c) % q
    return out


def projector(n, q):
    p = [1]
    for r in range(1, n * (n - 1) // 2 + 1):
        new = [0] * (len(p) + 1)
        inv = pow(r, -1, q)
        for k, c in enumerate(p):
            new[k] = (new[k] + c) % q
            new[k + 1] = (new[k + 1] - inv * c) % q
        p = new
    return p


def primal_reference(v, p, q):
    n = len(v)
    out = 0
    for labels in product(range(n), repeat=n):
        occupancy = [0] * n
        weight = 1
        for i, j in enumerate(labels):
            occupancy[j] += 1
            weight = weight * v[i][j] % q
        out = (out + weight * peval(p, kappa(occupancy), q)) % q
    return out


def dual_reader(v, p, q):
    n = len(v)
    internal = 0
    transitions = 0

    @lru_cache(None)
    def rec(u):
        nonlocal internal, transitions
        i = sum(u)
        if i == n:
            return peval(p, kappa(u), q)
        internal += 1
        out = 0
        for j in range(n):
            child = list(u)
            child[j] += 1
            out = (out + v[i][j] * rec(tuple(child))) % q
            transitions += 1
        return out

    answer = rec((0,) * n)
    expected = comb(2 * n - 1, n - 1)
    assert internal == expected
    assert transitions == n * expected
    gates = (2 * n - 1) * expected
    return answer, gates


def primitive_root(q):
    factors = [r for r in range(2, q) if (q - 1) % r == 0 and
               all(r % d for d in range(2, int(r**0.5) + 1))]
    return next(g for g in range(2, q)
                if all(pow(g, (q - 1) // r, q) != 1 for r in factors))


def intt(values, omega, q):
    size = len(values)
    inv = pow(size, -1, q)
    return [inv * sum(value * pow(omega, (-f * k) % size, q)
                      for f, value in enumerate(values)) % q
            for k in range(size)]


def verify():
    rng = random.Random(7112026)
    shift_checks = 0
    for _ in range(2000):
        n = rng.randrange(1, 10)
        alpha = [rng.randrange(10) for _ in range(n)]
        u = [rng.randrange(10) for _ in range(n)]
        assert kappa([a + b for a, b in zip(alpha, u)]) == (
            kappa(alpha) + kappa(u) + sum(a * b for a, b in zip(alpha, u)))
        shift_checks += 1
    cases = []
    frequency_checks = 0
    for q in (17, 97):
        for n in range(1, 7):
            size = 1
            while size <= n:
                size *= 2
            omega = pow(primitive_root(q), (q - 1) // size, q)
            assert pow(omega, size, q) == 1
            assert pow(omega, size // 2, q) != 1
            a = [[rng.randrange(q) for _ in range(n)] for _ in range(n)]
            z = rng.randrange(1, q)
            b = [[(1 + a[i][j] ** 2) * pow(z, 1 << (i * n + j), q) % q
                  for j in range(n)] for i in range(n)]
            labels = [rng.randrange(size) for _ in range(n)]
            h = n * (n - 1) // 2
            for kind, p in [('arbitrary', [rng.randrange(q) for _ in range(min(h, 5) + 1)]),
                            ('projector', projector(n, q))]:
                dual = []
                reference = []
                for f in range(size):
                    v = [[b[i][j] * pow(omega, f * labels[j], q) % q
                          for j in range(n)] for i in range(n)]
                    actual, gates = dual_reader(v, p, q)
                    expected = primal_reference(v, p, q)
                    assert actual == expected
                    dual.append(actual)
                    reference.append(expected)
                    frequency_checks += 1
                table = intt(dual, omega, q)
                assert table == intt(reference, omega, q)
                if kind == 'projector':
                    slot = sum(labels) % size
                    assert all(value == 0 for k, value in enumerate(table) if k != slot)
                    assert table[slot] == dual[0]
                cases.append({'n': n, 'q': q, 'N': size, 'reader': kind,
                              'propagation_scalar_gates_per_frequency': gates,
                              'table': table})
    # F=s_1 and G=s_2 at t=(1,1): all L-moments agree, but multiplying by s_1 differs.
    assert [pow(kappa((1, 0)), r) for r in range(5)] == [pow(kappa((0, 1)), r) for r in range(5)]
    assert kappa((2, 0)) == 1 and kappa((1, 1)) == 0
    return {
        'status': 'passed',
        'scope': 'finite verification of an exact reader law; explicit realization is not polynomial',
        'general_polynomial_closure': False,
        'shift_identity_checks': shift_checks,
        'full_tables': len(cases),
        'frequency_checks': frequency_checks,
        'local_moment_counterexample_checked': True,
        'cases': cases,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    sources = ['verify_dual.py', 'RACCORD_DUAL.md']
    before = {name: sha256((HERE / name).read_bytes()).hexdigest() for name in sources}
    report = verify()
    after = {name: sha256((HERE / name).read_bytes()).hexdigest() for name in sources}
    assert before == after, 'source changed while checking'
    report['source_sha256'] = before
    if args.write_report:
        (HERE / 'dual-validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('status', 'shift_identity_checks', 'full_tables',
                                          'frequency_checks', 'general_polynomial_closure')}, indent=2))


if __name__ == '__main__':
    main()

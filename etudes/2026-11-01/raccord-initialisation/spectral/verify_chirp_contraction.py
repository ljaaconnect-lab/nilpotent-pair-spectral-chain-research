"""Execute the chirp candidate using ordinary scalar gates; its size is exponential."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random


class ScalarGates:
    def __init__(self, Q):
        self.Q, self.count = Q, 0

    def add(self, a, b):
        self.count += 1
        return (a + b) % self.Q

    def mul(self, a, b):
        self.count += 1
        return a * b % self.Q

    def product(self, xs):
        xs = list(xs)
        result = xs[0]
        for x in xs[1:]:
            result = self.mul(result, x)
        return result

    def sum(self, xs):
        xs = list(xs)
        result = xs[0]
        for x in xs[1:]:
            result = self.add(result, x)
        return result

    def intt(self, xs, omega):
        N = len(xs)
        bits = N.bit_length() - 1
        result = [xs[int(f'{i:0{bits}b}'[::-1], 2)] for i in range(N)]
        length = 2
        while length <= N:
            for start in range(0, N, length):
                for k in range(length // 2):
                    i, j = start + k, start + k + length // 2
                    even = result[i]
                    odd = self.mul(result[j], pow(omega, -(N // length) * k, self.Q))
                    result[i] = self.add(even, odd)
                    result[j] = self.add(even, self.mul(-1, odd))
            length *= 2
        return [self.mul(x, pow(N, -1, self.Q)) for x in result]


def power_above(n):
    result = 1
    while result <= n:
        result *= 2
    return result


def primitive_root(Q):
    # Test-fixture preparation for Q=17,97 only. No polynomial-time
    # parameter-generation claim: candidates and factors are enumerated.
    factors = [p for p in range(2, Q) if (Q - 1) % p == 0 and all(p % j for j in range(2, int(p ** .5) + 1))]
    return next(g for g in range(2, Q) if all(pow(g, (Q - 1) // p, Q) != 1 for p in factors))


def run_candidate(a, z, ds, Q):
    n = len(a)
    h = n * (n - 1) // 2
    K, M, N = power_above(n), power_above(h), power_above(n)
    g = primitive_root(Q)
    assert all((Q - 1) % length == 0 for length in (K, M, N))
    zeta, eta, omega = (pow(g, (Q - 1) // length, Q) for length in (K, M, N))
    gates = ScalarGates(Q)
    blocks = {}

    marks = [z]
    for _ in range(n * n - 1):
        marks.append(gates.mul(marks[-1], marks[-1]))
    B = [[gates.mul(gates.add(1, gates.mul(a[i][j], a[i][j])), marks[i * n + j]) for j in range(n)] for i in range(n)]
    blocks['prepare_B'] = gates.count

    before = gates.count
    ws = []
    for ell in range(M):
        u = pow(eta, ell, Q)
        ws.append([gates.mul(pow(K, -1, Q), gates.sum(gates.mul(pow(u, m * (m - 1) // 2, Q), pow(zeta, -r * m, Q)) for m in range(K))) for r in range(K)])
    blocks['chirp_table'] = gates.count - before

    before = gates.count
    terms = []
    for rs in itertools.product(range(K), repeat=n):
        weight = gates.mul(pow(M, -1, Q), gates.sum(gates.product(ws[ell][r] for r in rs) for ell in range(M)))
        value = gates.product(gates.sum(gates.mul(B[i][j], pow(zeta, rs[j], Q)) for j in range(n)) for i in range(n))
        terms.append(gates.mul(weight, value))
    base_value = gates.sum(terms)
    blocks['joint_contraction'] = gates.count - before

    before = gates.count
    frequencies = [gates.mul(base_value, pow(omega, f * sum(ds), Q)) for f in range(N)]
    result = gates.intt(frequencies, omega)
    blocks['common_phase_and_intt'] = gates.count - before

    exact = 4 * n * n - 1 + 2 * M * K * K + (2 * n * n + M * n + 1) * K ** n - 1 + 2 * N * (N.bit_length() - 1) + 2 * N
    assert blocks['prepare_B'] == 4 * n * n - 1
    assert blocks['chirp_table'] == 2 * M * K * K
    assert blocks['joint_contraction'] == (2 * n * n + M * n + 1) * K ** n - 1
    assert blocks['common_phase_and_intt'] == 2 * N * (N.bit_length() - 1) + 2 * N
    assert gates.count == exact
    return result, {'n': n, 'Q': Q, 'K': K, 'M': M, 'N': N, 'points': K ** n, 'scalar_gates': gates.count, 'blocks': blocks}


def reference(a, z, ds, Q, N):
    n = len(a)
    slots = [0] * N
    for js in itertools.product(range(n), repeat=n):
        if len(set(js)) != n:
            continue
        value = 1
        for i, j in enumerate(js):
            value = value * (1 + a[i][j] ** 2) * pow(z, 2 ** (i * n + j), Q) % Q
        k = sum(ds[j] for j in js) % N
        slots[k] = (slots[k] + value) % Q
    return slots


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    path = Path(__file__)
    initial_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    rng = random.Random(20261102)
    tests = []
    for Q in (17, 97):
        for n in range(1, 5):
            for case in range(2):
                a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
                z = rng.randrange(1, Q)
                ds = [rng.randrange(power_above(n)) for _ in range(n)]
                slots, data = run_candidate(a, z, ds, Q)
                assert slots == reference(a, z, ds, Q, data['N'])
                data.update(case=case, passed=True)
                tests.append(data)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == initial_hash
    result = {
        'status': 'passed',
        'source': path.name,
        'sha256': initial_hash,
        'contract': 'Every data-dependent operation uses counted ordinary +/* gates. Prime Q and admissible roots eta,zeta,omega are supplied parameters; their deterministic polynomial-time generation is not established. Once supplied, exact power-of-two orders are checkable and powers/inverses are computable with polynomial work. The brute-force primitive_root helper only prepares the small test fields. The joint contraction uses K^n points; no polynomial closure is claimed.',
        'moments_as_inputs': False,
        'C_values_materialized': False,
        'terminal_amplitude_as_input': False,
        'general_polynomial_closure': False,
        'complete_tables': tests,
    }
    if args.write_report:
        path.with_name('chirp-contraction-validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

"""Independent checks of every output slot, scalar gates and formal z."""
from pathlib import Path
from itertools import product, permutations
import argparse
import hashlib
import json
import random
import sys
import time

from chaine_z import build, evaluate_streamed, gate_formula, transform_length


def reference(p, z, labels, prime):
    # Subsets occur ONLY in this test oracle, never in the compiler.
    n = len(p)
    b = [[p[i][j] * pow(z, 1 << (i * n + j), prime) % prime
          for j in range(n)] for i in range(n)]
    dp = [0] * (1 << n)
    dp[0] = 1
    for mask in range(1, 1 << n):
        row = mask.bit_count() - 1
        dp[mask] = sum(b[row][j] * dp[mask ^ (1 << j)]
                       for j in range(n) if (mask >> j) & 1) % prime
    expected = [0] * transform_length(n)
    expected[sum(labels) % len(expected)] = dp[-1]
    return expected


def formal_reference(p, labels, prime):
    n = len(p)
    expected = [{} for _ in range(transform_length(n))]
    slot = expected[sum(labels) % len(expected)]
    for sigma in permutations(range(n)):
        e, c = 0, 1
        for i, j in enumerate(sigma):
            e += 1 << (i * n + j)
            c = c * p[i][j] % prime
        slot[e] = (slot.get(e, 0) + c) % prime
    return [{e: c for e, c in table.items() if c} for table in expected]


def kernel_check(n, prime):
    # Each assignment is checked before any choice of matrix coefficients.
    # The sign projection must be 1 exactly on bijections, else 0.
    M = 1 << (n - 1)
    for assignment in product(range(n), repeat=n):
        value = 0
        for bits in range(M):
            epsilon = [-1 if (bits >> j) & 1 else 1 for j in range(n - 1)] + [1]
            term = 1
            for x in epsilon:
                term *= x
            for j in assignment:
                term *= epsilon[j]
            value += term
        assert value == M * (len(set(assignment)) == n), (n, assignment, value)
        assert value % prime == (M * (len(set(assignment)) == n)) % prime
    return n ** n


def run(write_report=False):
    start = time.monotonic()
    rng = random.Random(20261101)
    counts = {'kernel_assignments': 0, 'streamed_tables': 0,
              'dag_tables': 0, 'formal_tables': 0, 'adversarial_tables': 0}
    for n in range(1, 6):
        counts['kernel_assignments'] += kernel_check(n, 17)
    rows = []
    for prime, generator in [(17, 3), (97, 5), (257, 3), (998244353, 3)]:
        for n in range(1, 10):
            N = transform_length(n)
            for case in range(6):
                a = [[rng.randrange(prime) for _ in range(n)] for _ in range(n)]
                p = [[(1 + a[i][j] ** 2) % prime for j in range(n)] for i in range(n)]
                labels = [rng.randrange(-3 * N, 3 * N) for _ in range(n)]
                z = rng.randrange(prime)
                expected = reference(p, z, labels, prime)
                got = evaluate_streamed(p, z, labels, prime, generator)
                assert got == expected, ('streamed', prime, n, case, got, expected)
                counts['streamed_tables'] += 1
                if n <= 6 and case == 0:
                    for from_a in (False, True):
                        dag, outputs, info = build(n, labels, prime, generator, from_a)
                        data = {('a' if from_a else 'p', i, j): (a if from_a else p)[i][j]
                                for i in range(n) for j in range(n)}
                        data['z'] = z
                        assert dag.gates == gate_formula(n, from_a), (info, gate_formula(n, from_a))
                        assert dag.evaluate_all(outputs, data, prime) == expected
                        assert all(name == 'z' or (isinstance(name, tuple) and name[0] in ('a', 'p'))
                                   for op, *args in dag.nodes if op == 'input' for name in args)
                        counts['dag_tables'] += 1
                    rows.append(info)
            if n <= 4:
                labels = list(range(n))
                p = [[(i + j + 2) % prime for j in range(n)] for i in range(n)]
                dag, outputs, _ = build(n, labels, prime, generator)
                data = {('p', i, j): p[i][j] for i in range(n) for j in range(n)}
                assert dag.evaluate_polynomials(outputs, data, prime) == formal_reference(p, labels, prime)
                counts['formal_tables'] += 1

    # A collision has the same frequency label as the desired assignment:
    # d=(0,1,2), all rows choose column 1, so both sums are 3 mod 4.
    # These p entries are legal 1+a^2 over F_17: a=1 on support, a=4 elsewhere.
    p = [[0, 2, 0] for _ in range(3)]
    for z in range(17):
        assert evaluate_streamed(p, z, [0, 1, 2], 17, 3) == [0] * 4
        counts['adversarial_tables'] += 1

    result = {'date': '2026-11-01', 'status': 'passed', **counts,
              'counts_from_a': [dict(n=n, N=transform_length(n), channels=1 << (n - 1),
                                     gates=gate_formula(n, True)) for n in range(1, 13)],
              'elapsed_seconds': round(time.monotonic() - start, 3),
              'claim': 'Exact complete-chain scalar construction; exponential gate count; polynomial numerical working memory.'}
    here = Path(__file__).resolve().parent
    result['code_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [here / 'chaine_z.py', here / 'verifier.py']}
    if write_report:
        (here / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report', action='store_true', help='refresh validation.json')
    run(parser.parse_args().write_report)

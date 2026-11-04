"""Reproducible finite checks, independent of the frozen development evaluator."""
import json
from collections import Counter
from fractions import Fraction
from itertools import permutations
from math import factorial
from pathlib import Path
from random import Random

from dag import DAG, length
from phase_chain import build, certificate, gf_multiply, large_cyclic_certificate


def sign(permutation):
    n = len(permutation)
    return (-1)**sum(permutation[i] > permutation[j] for i in range(n) for j in range(i+1, n))


def score(permutation, kind, order, phases):
    value = 0
    for i, j in enumerate(permutation):
        if kind == 'xor':
            value ^= phases[i][j]
        else:
            value = (value + phases[i][j]) % order
    return value


def check_certificate(n, data):
    kind, order, phases, chi = data
    signed_histogram, multiplicities = Counter(), Counter()
    for permutation in permutations(range(n)):
        value = score(permutation, kind, order, phases)
        parity = sign(permutation)
        assert chi[value] == parity
        signed_histogram[value] += parity
        multiplicities[value] += 1
    l1 = sum(abs(v) for v in signed_histogram.values())
    l2sq = sum(v*v for v in signed_histogram.values())
    assert l1 == factorial(n)
    assert l2sq <= n**n
    assert len(multiplicities) * n**n >= factorial(n)**2
    return {'n': n, 'group_order': order, 'occupied_scores': len(multiplicities),
            'signed_histogram': dict(sorted(signed_histogram.items())), 'l1': l1, 'l2_squared': l2sq}


def reference_polynomial(n, inputs, prime):
    result = {}
    for permutation in permutations(range(n)):
        exponent, coefficient = 0, 1
        for i, j in enumerate(permutation):
            exponent += 1 << (i*n+j)
            coefficient = coefficient * inputs['p', i, j] % prime
        assert exponent not in result
        result[exponent] = coefficient
    return {e: c for e, c in result.items() if c}


def test_compilers():
    prime = 65537
    rng = Random(20261024)
    results = []
    for n in range(1, 5):
        N = length(n)
        label_patterns = [[0]*n, list(range(n)), [-2*j-1 for j in range(n)],
                          [rng.randrange(-2*N, 2*N+1) for _ in range(n)]]
        for method in ['coordinates', 'specialized']:
            row = {'n': n, 'method': method, 'numeric_tables': 0, 'formal_tables': 0,
                   'gates_by_labels': [], 'max_literal_bits': 0}
            for labels in label_patterns:
                dag = DAG()
                outputs = build(n, labels, dag, method)
                assert len(outputs) == N
                row['gates_by_labels'].append({'labels': labels, 'gates': dag.gates})
                literal_bits = max(max(abs(args[0].numerator).bit_length(), args[0].denominator.bit_length())
                                   for op, *args in dag.nodes if op == 'const')
                row['max_literal_bits'] = max(row['max_literal_bits'], literal_bits)
                for case in range(8):
                    inputs = {('p', i, j): 1+rng.randrange(-8, 9)**2 for i in range(n) for j in range(n)}
                    inputs['z'] = [0, 1, prime-1, rng.randrange(prime)][case % 4]
                    polynomial = reference_polynomial(n, inputs, prime)
                    expected = [0]*N
                    expected[sum(labels) % N] = sum(c*pow(inputs['z'], e, prime) for e, c in polynomial.items()) % prime
                    assert dag.evaluate_all(outputs, inputs, prime) == expected
                    row['numeric_tables'] += 1
                    if case == 1:
                        expected_formal = [{} for _ in range(N)]
                        expected_formal[sum(labels) % N] = polynomial
                        assert dag.evaluate_polynomials(outputs, inputs, prime) == expected_formal
                        row['formal_tables'] += 1
            results.append(row)
    return results


def field_collision(n, first, second):
    phases = [[gf_multiply(i, j, 11) for j in range(n)] for i in range(n)]
    a, b = score(first, 'xor', 8, phases), score(second, 'xor', 8, phases)
    assert sorted(first) == sorted(second) == list(range(n))
    assert sign(first) != sign(second) and a == b
    return {'n': n, 'field_polynomial_binary': 11, 'first': first, 'second': second,
            'first_sign': sign(first), 'second_sign': sign(second), 'shared_score': a}


def main():
    small = [check_certificate(n, certificate(n)) for n in range(1, 5)]
    # The large construction is exhaustively tested as labels/readout, without
    # materializing a large algebra DAG or claiming a polynomial construction.
    large = [check_certificate(n, large_cyclic_certificate(n)) for n in range(1, 7)]
    # Avoid storing the entire exponentially large histogram in the report.
    for row in large:
        row.pop('signed_histogram')
    lower_bounds = []
    for n in range(1, 21):
        bound = Fraction(factorial(n)**2, n**n)
        lower_bounds.append({'n': n, 'exact_bound': str(bound),
                             'ceiling': -(-bound.numerator // bound.denominator)})
    collisions = [field_collision(5, [0, 1, 3, 4, 2], [0, 2, 1, 3, 4]),
                  field_collision(6, [0, 1, 2, 4, 5, 3], [0, 2, 1, 3, 4, 5]),
                  field_collision(8, [0, 1, 2, 3, 4, 6, 5, 7], [0, 1, 2, 4, 5, 3, 6, 7])]
    results = {'small_certificates': small, 'large_cyclic_certificates': large,
               'full_chain_checks': test_compilers(), 'proven_group_lower_bounds': lower_bounds,
               'naive_F8_extension_collisions': collisions,
               'frozen_development_evaluator_run': False, 'dev_score': None}
    Path('phase_chain_checks.json').write_text(json.dumps(results, indent=2), encoding='utf8')
    print(json.dumps({'numeric_tables': sum(r['numeric_tables'] for r in results['full_chain_checks']),
                      'formal_tables': sum(r['formal_tables'] for r in results['full_chain_checks']),
                      'compilers': results['full_chain_checks']}, indent=2))


if __name__ == '__main__':
    main()

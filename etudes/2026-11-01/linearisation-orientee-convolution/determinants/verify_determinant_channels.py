"""Candidate: row NTT, twisted Fourier determinants, scalar readout.

No general polynomial-circuit claim. Permutations occur only in verification
and selection of the small-case constant readout, never in circuit evaluation.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REFERENCE_FOLDER = HERE.parents[1] / 'raccord-initialisation/spectral/reprise-globale'
sys.path.insert(0, str(REFERENCE_FOLDER))
from verify_shared_operator_dag import polynomial_add, polynomial_mul


class ScalarOps:
    def __init__(self, Q):
        self.Q, self.gates = Q, 0

    def add(self, a, b):
        self.gates += 1
        return (a+b) % self.Q

    def mul(self, a, b):
        self.gates += 1
        return a*b % self.Q

    def sum(self, values):
        values = list(values)
        if not values:
            return 0
        result = values[0]
        for value in values[1:]:
            result = self.add(result, value)
        return result


class FormalZOps(ScalarOps):
    """Gate-by-gate checking with unreduced formal z exponents."""
    def polynomial(self, value):
        if isinstance(value, dict):
            return value
        value %= self.Q
        return {0: value} if value else {}

    def add(self, a, b):
        self.gates += 1
        return polynomial_add(self.polynomial(a), self.polynomial(b), self.Q)

    def mul(self, a, b):
        self.gates += 1
        return polynomial_mul(self.polynomial(a), self.polynomial(b), self.Q)


def ntt(values, omega, op):
    N = len(values)
    bits = N.bit_length()-1
    values = [values[int(f'{i:0{bits}b}'[::-1], 2)] for i in range(N)]
    length = 2
    while length <= N:
        for start in range(0, N, length):
            for k in range(length//2):
                left, right = start+k, start+k+length//2
                u = values[left]
                v = op.mul(values[right], pow(omega, N//length*k, op.Q))
                values[left] = op.add(u, v)
                values[right] = op.add(u, op.mul(op.Q-1, v))
        length *= 2
    return values


def determinant(matrix, op):
    """Newton traces, scalar +/* gates; divisions are by fixed integers only."""
    n = len(matrix)
    power = matrix
    traces = [0]
    for k in range(1, n+1):
        if k > 1:
            power = [[op.sum(op.mul(power[i][j], matrix[j][k2]) for j in range(n))
                      for k2 in range(n)] for i in range(n)]
        traces.append(op.sum(power[i][i] for i in range(n)))
    elementary = [1]
    for k in range(1, n+1):
        terms = []
        for r in range(1, k+1):
            coefficient = (1 if r % 2 else -1) * pow(k, -1, op.Q) % op.Q
            terms.append(op.mul(coefficient, op.mul(elementary[k-r], traces[r])))
        elementary.append(op.sum(terms))
    return elementary[n]


def sign(permutation):
    return -1 if sum(permutation[i] > permutation[j]
                     for i in range(len(permutation))
                     for j in range(i+1, len(permutation))) % 2 else 1


def prepare_inputs(a, z, op):
    n = len(a)
    marks = [z]
    for _ in range(n*n-1):
        marks.append(op.mul(marks[-1], marks[-1]))
    return [[op.mul(op.add(1, op.mul(a[i][j], a[i][j])), marks[i*n+j])
             for j in range(n)] for i in range(n)]


def constants(n, Q, N, omega):
    # This small-case enumerator audits existence of the constant g; it is not
    # a claimed polynomial-time construction of g for arbitrary n.
    groups = {}
    for permutation in itertools.permutations(range(n)):
        score = sum(i*permutation[i] for i in range(n)) % N
        groups.setdefault(score, []).append((permutation, sign(permutation)))
    g = [0]*N
    for score, permutations in groups.items():
        g[score] = permutations[0][1]
    lam = [sum(g[k]*pow(omega, -f*k, Q) for k in range(N))*pow(N, -1, Q) % Q
           for f in range(N)]
    vandermonde = [[pow(omega, -j*s, Q) for s in range(n)] for j in range(n)]
    delta = determinant(vandermonde, ScalarOps(Q))
    assert delta != 0
    coeffs = [value*pow(delta, -1, Q) % Q for value in lam]
    mixed = {score: values for score, values in groups.items()
             if len({sgn for _, sgn in values}) > 1}
    return g, coeffs, groups, mixed


def evaluate_candidate(a, z, Q, N, omega, coeffs, ops_class=ScalarOps):
    op = ops_class(Q)
    B = prepare_inputs(a, z, op)
    n = len(B)
    fourier = [ntt(row+[0]*(N-n), omega, op) for row in B]
    determinants = []
    for f in range(N):
        matrix = [[fourier[i][(f*i-s) % N] for s in range(n)] for i in range(n)]
        determinants.append(determinant(matrix, op))
    value = op.sum(op.mul(coeffs[f], determinants[f]) for f in range(N))
    return value, B, op.gates


def reference(B, g, N, Q):
    target = residual = 0
    n = len(B)
    for permutation in itertools.permutations(range(n)):
        weight = 1
        for i, j in enumerate(permutation):
            weight = weight*B[i][j] % Q
        score = sum(i*permutation[i] for i in range(n)) % N
        target = (target+weight) % Q
        residual = (residual+(g[score]*sign(permutation)-1)*weight) % Q
    return target, residual


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    sources = [Path(__file__).resolve(), HERE/'CANAUX_DETERMINANTS.md',
               REFERENCE_FOLDER/'verify_shared_operator_dag.py']
    hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sources}
    rng = random.Random(20261101)
    cases = []
    for n, Q, N in [(3, 97, 8), (4, 97, 16), (5, 97, 32), (6, 193, 64)]:
        omega = next(w for w in range(2, Q)
                     if pow(w, N, Q) == 1 and pow(w, N//2, Q) != 1)
        g, coeffs, groups, mixed = constants(n, Q, N, omega)
        labels = [rng.randrange(N) for _ in range(n)]
        tests = []
        for sample in range(4):
            a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
            z = 0 if sample == 0 else rng.randrange(1, Q)
            value, B, gates = evaluate_candidate(a, z, Q, N, omega, coeffs)
            target, residual = reference(B, g, N, Q)
            assert (value-target) % Q == residual
            if not mixed:
                assert residual == 0
            actual_table, expected_table, residual_table = [0]*N, [0]*N, [0]*N
            k_star = sum(labels) % N
            actual_table[k_star], expected_table[k_star], residual_table[k_star] = value, target, residual
            assert [(u-v) % Q for u, v in zip(actual_table, expected_table)] == residual_table
            tests.append({'value': value, 'target': target, 'residual': residual,
                          'routing_index': k_star})
        formal_checks = 0
        if n == 3:
            for _ in range(2):
                a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
                actual, _, formal_gates = evaluate_candidate(a, {1: 1}, Q, N, omega,
                                                             coeffs, FormalZOps)
                expected = {}
                for permutation in itertools.permutations(range(n)):
                    coefficient, exponent = 1, 0
                    for i, j in enumerate(permutation):
                        coefficient = coefficient*(1+a[i][j]**2) % Q
                        exponent += 2**(i*n+j)
                    expected = polynomial_add(expected, {exponent: coefficient}, Q)
                assert actual == expected and formal_gates == gates
                formal_checks += 1
        witness = None
        if mixed:
            score, entries = next(iter(mixed.items()))
            good = next(permutation for permutation, sgn in entries if sgn == g[score])
            bad = next(permutation for permutation, sgn in entries if sgn != g[score])
            sqrt_minus_one = next(a for a in range(Q) if (1+a*a) % Q == 0)
            a = [[0 if j == bad[i] else sqrt_minus_one for j in range(n)] for i in range(n)]
            value, B, gates = evaluate_candidate(a, 1, Q, N, omega, coeffs)
            target, residual = reference(B, g, N, Q)
            assert target == 1 and value == Q-1 and residual == Q-2
            witness = {'score': score, 'first_orientation': good,
                       'opposite_orientation': bad,
                       'first_sign': sign(good), 'opposite_sign': sign(bad),
                       'target': target, 'actual': value, 'residual': residual,
                       'original_inputs_realization': {'z': 1, 'a': a}}
        determinant_cost = (n-1)*n*n*(2*n-1)+(5*n*n-n)//2
        gate_formula = 4*n*n-1+2*n*N*(N.bit_length()-1)+N*determinant_cost+2*N-1
        assert gates == gate_formula
        case = {'n': n, 'Q': Q, 'N': N, 'omega': omega, 'spectral_labels': labels,
                'scalar_gate_calls_from_a_z': gates,
                'gate_formula': gate_formula,
                'orientation_classes': len(groups),
                'mixed_orientation_classes': len(mixed),
                'correct_for_all_B_at_this_n': not mixed,
                'g_nonzero': {k: x for k, x in enumerate(g) if x},
                'tests': tests, 'formal_z_checks': formal_checks,
                'isolated_witness': witness}
        cases.append(case)
        print(json.dumps(case), flush=True)
    assert hashes == {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sources}
    report = {'status': 'identities_verified', 'source_sha256': hashes, 'cases': cases,
              'general_polynomial_circuit': False,
              'collision_columns_annihilated_in_each_determinant': True,
              'failure_kind': 'opposite orientations at the same scalar frequency score',
              'runtime_operations': ['+', '*'],
              'general_full_chain_correctness': False,
              'general_impossibility_claim': False,
              'small_case_readout_constant_search_is_not_claimed_uniform_polynomial': True}
    if args.write_report:
        (HERE/'determinant-channels-validation.json').write_text(
            json.dumps(report, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()

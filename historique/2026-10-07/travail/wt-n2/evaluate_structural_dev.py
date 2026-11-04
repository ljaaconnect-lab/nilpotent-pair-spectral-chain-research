"""Frozen structural development evaluator v1; fixed before first execution.

Score = exact permanent recovery fraction over nine Boolean matrices.
Symbolic identities and CRT checks are additional diagnostics, not score terms.
No held-out examples appear here. Do not change after first evaluation.
"""
import hashlib
import json
from fractions import Fraction
from itertools import permutations
from math import factorial, prod
from pathlib import Path
import structural


def dev_cases():
    for n in (2, 3, 4):
        yield f"n{n}-identity", [[int(i == j) for j in range(n)] for i in range(n)]
        yield f"n{n}-cyclic", [[int(j == (i+1) % n) for j in range(n)] for i in range(n)]
        yield f"n{n}-band", [[int(abs(i-j) <= 1) for j in range(n)] for i in range(n)]


def boolean_oracle(B):
    # Independent combinatorial count; never uses interpolation.
    return sum(all(B[i][sigma[i]] for i in range(len(B)))
               for sigma in permutations(range(len(B))))


def main():
    rows, passed = [], 0
    for name, B in dev_cases():
        n = len(B)
        expected = boolean_oracle(B)
        got = structural.recover_boolean(B)
        exact = got == expected
        passed += int(exact)
        samples = [structural.specialize_pa([[r*v for v in row] for row in B])
                   for r in range(n+1)]
        crt_exact = []
        for r, sample in enumerate(samples):
            entries = [[1+r*r*v for v in row] for row in B]
            bound = factorial(n)*(1+n*n)**n
            rec = structural.reconstruct_integer(structural.integer_circuit(entries), bound)
            crt_exact.append(rec['integer'] == sample)
        rows.append({'case': name, 'n': n, 'nodes': [r*r for r in range(n+1)],
                     'samples': [str(v) for v in samples], 'expected': expected,
                     'recovered': str(got), 'exact': exact,
                     'crt_samples_exact': all(crt_exact)})
    # Cancel an enormous intermediate through rational leaves: output is one,
    # but exact intermediate expansion would have 2**2000+1 integer bits.
    circuit = [('const', 2, 1)]
    for _ in range(2000):
        circuit.append(('mul', len(circuit)-1, len(circuit)-1))
    giant = len(circuit)-1
    circuit.extend([('const', -1, 1), ('mul', giant, len(circuit)),
                    ('add', giant, len(circuit)+1), ('const', 1, 7),
                    ('const', 6, 7), ('add', len(circuit)+3, len(circuit)+4)])
    # The giant cancellation gate is unused by the final output here; connect it.
    circuit.append(('add', len(circuit)-4, len(circuit)-1))
    cancellation = structural.reconstruct_integer(circuit, 1)
    report = {'protocol': 'structural-dev-v1', 'split': 'dev',
              'score': passed/9, 'passed': passed, 'total': 9,
              'evaluator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'artifact_sha256': hashlib.sha256(Path(structural.__file__).read_bytes()).hexdigest(),
              'cases': rows,
              'symbolic_interpolation': [structural.interpolation_symbolic_check(n)
                                         for n in (2, 3, 4)],
              'modular_cancellation': {'value': cancellation['integer'],
                                       'primes': cancellation['primes'],
                                       'avoids_denominator_seven': 7 not in cancellation['primes'],
                                       'integer_bits_before_cancellation': '2**2000+1'},
              'formal_status': 'UNVERIFIED: Lean unavailable; no theorem compilation',
              'scope': 'Exact finite reduction checks; default oracle is factorial-size.'}
    Path('dev-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

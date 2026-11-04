"""Frozen full-chain checks. Finite checks do not prove polynomial complexity."""
import hashlib
from itertools import permutations
import json
from pathlib import Path
import random
from dag import DAG, length
import candidate


def primitive_power_two_root(N, prime):
    assert (prime - 1) % N == 0
    for base in range(2, prime):
        w = pow(base, (prime - 1) // N, prime)
        if pow(w, N, prime) == 1 and pow(w, N // 2, prime) != 1:
            return w
    raise AssertionError('root unavailable')


def reference_polynomial(n, values, prime):
    result = {}
    for sigma in permutations(range(n)):
        e, c = 0, 1
        for i, j in enumerate(sigma):
            e += 1 << (i * n + j)
            c = c * values[('p', i, j)] % prime
        result[e] = c
    return {e: c for e, c in result.items() if c}


def evaluate(seed=202610242, sizes=range(1, 8), cases=12, prime=65537):
    rng = random.Random(seed)
    checks, formal, counts = 0, 0, {}
    for n in sizes:
        N = length(n)
        omega = primitive_power_two_root(N, prime)
        for case in range(cases):
            labels = ([0] * n if case % 4 == 0 else list(range(n)) if case % 4 == 1
                      else [-j - 1 for j in range(n)] if case % 4 == 2
                      else [rng.randrange(-3 * N, 3 * N + 1) for _ in range(n)])
            d = DAG()
            outputs = candidate.build(n, labels, d)
            assert len(outputs) == N and all(isinstance(v, int) and 0 <= v < len(d.nodes) for v in outputs)
            counts.setdefault(n, d.gates)
            values = {('p', i, j): 1 + rng.randrange(-12, 13) ** 2
                      for i in range(n) for j in range(n)}
            values['omega'] = omega
            values['z'] = [0, 1, prime - 1, rng.randrange(prime)][case % 4]
            expected = reference_polynomial(n, values, prime)
            amplitude = sum(c * pow(values['z'], e, prime) for e, c in expected.items()) % prime
            slot = sum(labels) % N
            observed = d.evaluate_all(outputs, values, prime)
            assert observed == [amplitude if k == slot else 0 for k in range(N)], (n, case, observed)
            checks += 1
            if n <= 4 and case in (1, 3):
                observed_formal = d.evaluate_polynomials(outputs, values, prime)
                assert observed_formal == [expected if k == slot else {} for k in range(N)]
                formal += 1
    score_dag = DAG()
    candidate.build(8, list(range(8)), score_dag)
    return {'numeric_full_table_checks': checks, 'formal_full_table_checks': formal,
            'gate_counts': counts, 'score': score_dag.gates, 'score_direction': 'min',
            'general_polynomial_proof': False,
            'candidate_sha256': hashlib.sha256(Path(candidate.__file__).read_bytes()).hexdigest(),
            'evaluator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__ == '__main__': print(json.dumps(evaluate(), indent=2))

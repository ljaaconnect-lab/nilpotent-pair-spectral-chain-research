"""Independent finite checks; enumeration occurs only in this verifier."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
import random
import time

from linearised_full_chain import (HISTORICAL_SOURCE, NodeBudgetExceeded,
                                   compile_linearised_chain, compile_original_fused,
                                   spectral_readout)


def amplitudes(n, Q, inputs):
    return [[(1 + inputs[f'a_{i}_{j}']**2) * pow(inputs['z'], 2**(i*n+j), Q) % Q
             for j in range(n)] for i in range(n)]


def corrected_amplitude(B, Q):
    # Independent enumeration oracle, absent from the compiler.
    total = 0
    for perm in itertools.permutations(range(len(B))):
        value = 1
        for i, j in enumerate(perm):
            value = value * B[i][j] % Q
        total = (total + value) % Q
    return total


def oriented_spectra_and_intt(B, labels, N, omega, Q):
    n = len(B)
    spectra = []
    for f in range(N):
        state = {0: 1}
        for i in range(n):
            out = {}
            for mask, value in state.items():
                for j in range(n):
                    if mask & (1 << j):
                        continue
                    target = mask | (1 << j)
                    out[target] = (out.get(target, 0) + value * B[i][j]
                                   * pow(omega, f * labels[j], Q)) % Q
            state = out
        spectra.append(state.get((1 << n) - 1, 0))
    invN = pow(N, -1, Q)
    outputs = [sum(spectra[f] * pow(omega, -f*k, Q) for f in range(N)) * invN % Q
               for k in range(N)]
    return spectra, outputs


def stage_oracle_all(B, s, h, Q):
    n = len(B)
    totals = [0] * (h+1)
    inverses = [0] + [pow(r, -1, Q) for r in range(1, h+1)]
    for choice in itertools.product(range(n), repeat=n):
        counts = [choice.count(j) for j in range(n)]
        collision = sum(c*(c-1)//2 for c in counts)
        value = 1
        for i, j in enumerate(choice):
            value = value * B[i][j] * s[j] % Q
        totals[0] = (totals[0] + value) % Q
        for r in range(1, h+1):
            value = value * (1 - collision * inverses[r]) % Q
            totals[r] = (totals[r] + value) % Q
    return totals


def poly_add(a, b, Q):
    out = dict(a)
    for e, c in b.items():
        out[e] = (out.get(e, 0) + c) % Q
        if not out[e]:
            del out[e]
    return out


def poly_mul(a, b, Q):
    out = {}
    for ea, ca in a.items():
        for eb, cb in b.items():
            e = ea + eb
            out[e] = (out.get(e, 0) + ca * cb) % Q
    return {e: c for e, c in out.items() if c}


def evaluate_formal_z(dag, roots, inputs):
    values = {}
    for idx in sorted(dag.reachable(roots)):
        node = dag.nodes[idx]
        if node[0] == 'c':
            values[idx] = {0: node[1]} if node[1] else {}
        elif node[0] == 'v':
            if node[1] == 'z':
                values[idx] = {1: 1}
            else:
                value = inputs[node[1]] % dag.Q
                values[idx] = {0: value} if value else {}
        elif node[0] == '+':
            values[idx] = poly_add(values[node[1]], values[node[2]], dag.Q)
        else:
            values[idx] = poly_mul(values[node[1]], values[node[2]], dag.Q)
    return [values[root] for root in roots]


def check_syntactic_homogeneity(dag, stage_roots, n, auxiliary_prefix):
    # None denotes the zero polynomial, homogeneous at every degree.
    degrees = []
    for node in dag.nodes:
        if node[0] == 'c':
            degree = 0 if node[1] else None
        elif node[0] == 'v':
            degree = int(node[1].startswith(auxiliary_prefix))
        else:
            left, right = degrees[node[1]], degrees[node[2]]
            if node[0] == '*':
                degree = None if left is None or right is None else left + right
            else:
                assert left is None or right is None or left == right
                degree = right if left is None else left
        assert degree is None or degree <= n
        degrees.append(degree)
    assert all(degrees[root] in (None, n) for root in stage_roots)
    return {'checked_allocated_nodes': len(degrees),
            'max_auxiliary_degree': max(d for d in degrees if d is not None),
            'stage_degrees': [degrees[root] for root in stage_roots]}


def verify_case(n, budget, Q=97, full_stage_oracle=True):
    N = 1
    while N <= n:
        N *= 2
    omega = next(w for w in range(2, Q) if pow(w, N, Q) == 1 and pow(w, N//2, Q) != 1)
    labels = [(j*j + 2*j + 1) % N for j in range(n)]
    compiled = compile_linearised_chain(n, Q, omega, labels, budget)
    original = compile_original_fused(n, Q, omega, labels, budget)
    dag = compiled['dag']
    metadata = compiled['metadata']
    rng = random.Random(31003 + n)
    fixtures = []
    for _ in range(5):
        fixtures.append({'z': rng.randrange(Q), **{f'a_{i}_{j}': rng.randrange(Q)
                         for i in range(n) for j in range(n)}})
    fixtures.append({'z': 0, **{f'a_{i}_{j}': 0 for i in range(n) for j in range(n)}})
    fixtures.append({'z': 1, **{f'a_{i}_{j}': 0 for i in range(n) for j in range(n)}})
    sqrt_minus_one = next(a for a in range(Q) if a*a % Q == Q-1)
    fixtures.append({'z': 3, **{f'a_{i}_{j}': sqrt_minus_one if i == 0 else 1
                              for i in range(n) for j in range(n)}})
    counts = {'numeric_instances': 0, 'stage_equalities': 0, 'inverse_coordinate_equalities': 0,
              'directional_coordinate_equalities': 0, 'spectrum_coordinates': 0,
              'INTT_coordinates': 0, 'routed_coordinates': 0,
              'formal_z_coordinates': 0, 'label_profiles': 3}
    counts['original_comparator_coordinates'] = 0
    # Test the conjugated derivative on the actual constructed q_j(x).
    for j in range(n):
        for k in range(n):
            node = dag.derivative(compiled['q'][k], j)
            assert dag.nodes[node] == ('c', int(j == k))
            counts['directional_coordinate_equalities'] += 1
    profiles = [labels, list(range(n)), [0] * n]
    readouts = [(compiled['spectra'], compiled['outputs'], compiled['routed'])]
    readouts += [spectral_readout(dag, compiled['Y'], ds, N, omega) for ds in profiles[1:]]
    for fixture_index, inputs in enumerate(fixtures):
        B = amplitudes(n, Q, inputs)
        assert dag.evaluate([compiled['Y']], inputs) == [corrected_amplitude(B, Q)]
        assert original['dag'].evaluate(original['outputs'], inputs) == dag.evaluate(compiled['outputs'], inputs)
        counts['original_comparator_coordinates'] += N
        counts['numeric_instances'] += 1
        for ds, (spectra, outputs, routed) in zip(profiles, readouts):
            expected_spectra, expected_outputs = oriented_spectra_and_intt(B, ds, N, omega, Q)
            assert dag.evaluate(spectra, inputs) == expected_spectra
            assert dag.evaluate(outputs, inputs) == expected_outputs
            assert dag.evaluate(routed, inputs) == expected_outputs
            counts['spectrum_coordinates'] += N
            counts['INTT_coordinates'] += N
            counts['routed_coordinates'] += N
        if fixture_index < 2 and full_stage_oracle:
            s = [rng.randrange(Q) for _ in range(n)]
            point = {**inputs, **{f'x_{r}': sum(pow(omega, r*j, Q) * s[j]
                                              for j in range(n)) % Q for r in range(N)}}
            assert dag.evaluate(compiled['q'], point) == s
            counts['inverse_coordinate_equalities'] += n
            actual = dag.evaluate(compiled['stage_roots'], point)
            expected = stage_oracle_all(B, s, metadata['h'], Q)
            assert actual == expected
            counts['stage_equalities'] += len(expected)
    if n <= 3:
        inputs = fixtures[0]
        expected = {}
        for perm in itertools.permutations(range(n)):
            exponent = sum(2**(i*n+j) for i, j in enumerate(perm))
            coefficient = 1
            for i, j in enumerate(perm):
                coefficient = coefficient * (1 + inputs[f'a_{i}_{j}']**2) % Q
            if coefficient:
                expected[exponent] = coefficient
        formal_outputs = evaluate_formal_z(dag, compiled['outputs'], inputs)
        target = sum(labels) % N
        assert formal_outputs == [expected if k == target else {} for k in range(N)]
        counts['formal_z_coordinates'] += N
    metadata['verification_counts'] = counts
    metadata['verification_status'] = 'passed'
    metadata['original_coordinates_same_fusion'] = original['metadata']
    metadata['stage_oracle_run'] = full_stage_oracle
    metadata['syntactic_homogeneity'] = check_syntactic_homogeneity(
        dag, compiled['stage_roots'], n, 'x_')
    linear_stages = metadata['stages']
    original_stages = original['metadata']['stages']
    linear_deltas = [linear_stages[i]['joint_gates_with_q'] - linear_stages[i-1]['joint_gates_with_q']
                     for i in range(1, len(linear_stages))]
    original_deltas = [original_stages[i]['root_gates'] - original_stages[i-1]['root_gates']
                       for i in range(1, len(original_stages))]
    metadata['growth_observations'] = {
        'linearised_stage_increments': linear_deltas,
        'original_stage_increments': original_deltas,
        'increments_match_after_first_factor': linear_deltas[1:] == original_deltas[1:],
        'derivative_cache_counts': [stage['cached_derivatives'] for stage in linear_stages],
        'interpretation': 'The derivative cache still grows; an eventually constant increment in these finite cases is not saturation of the complete cache or an asymptotic polynomial bound.'}
    return metadata


def main():
    started = time.perf_counter()
    files = [Path(__file__), Path(__file__).with_name('linearised_full_chain.py'), HISTORICAL_SOURCE]
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    cases, attempts = [], []
    for n in (1, 2, 3, 4, 5, 6):
        budget = 900_000
        try:
            case = verify_case(n, budget)
            cases.append(case)
            print(json.dumps({'n': n, 'status': 'passed', 'gates': case['true_INTT_output_gates'],
                              'routed_gates': case['routed_output_gates'],
                              'allocated_nodes': case['allocated_nodes']}), flush=True)
        except NodeBudgetExceeded as error:
            if n <= 6:
                raise
            attempts.append({'n': n, 'status': 'budget_exceeded_not_verified',
                             'node_budget': budget, 'reason': str(error)})
            print(json.dumps(attempts[-1]), flush=True)
    # Same orders, a different admissible characteristic: this is a finite
    # check against a feature specific to Q=97, not an asymptotic argument.
    cross_field = []
    for n in (3, 4, 5, 6):
        case = verify_case(n, 900_000, Q=257, full_stage_oracle=False)
        cross_field.append(case)
        print(json.dumps({'n': n, 'Q': 257, 'status': 'passed',
                          'gates': case['true_INTT_output_gates'],
                          'allocated_nodes': case['allocated_nodes']}), flush=True)
    assert all(hashlib.sha256(p.read_bytes()).hexdigest() == hashes[str(p)] for p in files)
    report = {'status': 'passed', 'scope': 'finite exact checks of complete linearised scalar compilation; no polynomial size theorem',
              'general_polynomial_bound_established': False, 'source_sha256': hashes,
              'reference_enumeration_only_in_verifier': True, 'final_runtime_inputs': 'a_ij,z only',
              'cases': cases, 'cross_field_cases': cross_field, 'optional_attempts': attempts,
              'comparison_scope': 'historical original-coordinate prefix compiled once; same phase sharing and real INTT in both versions',
              'growth_interpretation': 'finite stage profiles only; derivative-cache growth is recorded; same gate profiles in a second field and after removing the Fourier representation do not establish a polynomial bound',
              'larger_orders': 'n=7,8 not attempted; optional and not needed for the stated finite verification scope',
              'elapsed_seconds': time.perf_counter() - started}
    destination = Path(__file__).with_name('linearised-full-chain-validation.json')
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'completed_cases': len(cases),
                      'report': str(destination), 'elapsed_seconds': report['elapsed_seconds']}), flush=True)


if __name__ == '__main__':
    main()

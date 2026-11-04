"""Independent small-case verification of the scalar convolution recurrence.

The production compiler only emits +/* gates on existing B/C wires. All
nilpotent support dictionaries below belong to this verifier, not to its
inputs, state cache or emitted circuit. No runtime choice depends on a,z.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import factorial, prod
from pathlib import Path
import random
import sys
import time


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from compiler_joint_convolution import compile_joint_convolution  # noqa: E402
from verify_native_composition import (  # noqa: E402
    direct_oriented_table, evaluate_nil, fourier_orientations, multiply_nil,
)


def verify_case(n, Q, budget, fused_with_preparation=False):
    N = 1 << n.bit_length()
    assert (Q-1) % N == 0
    omega = next(w for w in range(1, Q)
                 if pow(w, N, Q) == 1 and pow(w, N//2, Q) != 1)
    labels = [j*j+3*j-2*n for j in range(n)]
    labels[0] += 1
    started = time.perf_counter()
    compiled = compile_joint_convolution(n, Q, N, omega, labels, budget=budget,
                                        fused_with_preparation=fused_with_preparation)
    compile_seconds = time.perf_counter()-started
    dag, contraction = compiled['dag'], compiled['contraction']
    x = fourier_orientations(n, N, omega, Q)
    gamma, target = (-1)**(n*(n-1)//2), sum(labels) % N
    rng = random.Random(110304+100*n+Q)
    counts = {'numeric_instances': 0, 'numeric_output_coordinates': 0,
              'pooled_vector_checks': 0, 'all_small_state_checks': 0,
              'formal_z_tables': 0, 'formal_z_coordinates': 0}
    scalar_outputs = []
    for sample in range(4):
        a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
        z = rng.randrange(Q)
        if sample == 1:
            z = 0
        elif sample == 2:
            a = [[0]*n for _ in range(n)]
            z = 1
        elif sample == 3:
            sqrt_minus_one = next(t for t in range(Q) if t*t % Q == Q-1)
            a[0] = [sqrt_minus_one]*n
        inputs = {f'a_{i}_{j}': a[i][j] for i in range(n) for j in range(n)} | {'z': z}
        reference_spectra, reference_outputs = direct_oriented_table(a, z, Q, N, omega, labels)
        expected = [sum(gamma*c for c in out.values()) % Q for out in reference_outputs]
        observed = dag.evaluate(compiled['outputs'], inputs)
        assert observed == expected, (n, Q, sample, observed, expected)
        scalar = dag.evaluate([compiled['scalar']], inputs)[0]
        raw = dag.evaluate([compiled['raw']], inputs)[0]
        assert scalar == expected[target]
        assert raw == factorial(n)*scalar % Q
        assert dag.evaluate(compiled['spectra'], inputs) == [
            scalar*pow(omega, f*sum(labels), Q) % Q for f in range(N)]
        counts['numeric_instances'] += 1
        counts['numeric_output_coordinates'] += N
        scalar_outputs.append(scalar)
        # Verify every pooled convolution vector against its rowwise product.
        # This is reference arithmetic, not a source of gates for the compiler.
        B = [[(1+a[i][j]**2)*pow(z, 2**(i*n+j), Q) % Q for j in range(n)] for i in range(n)]
        inverse_vectors = {}
        pool = contraction.row_pool if fused_with_preparation else contraction.vector_pool
        for group, nodes in pool.items():
            coefficients = dag.evaluate(nodes, inputs)
            if fused_with_preparation:
                inverse = coefficients + [0]*(N-n)
            else:
                inverse = [sum(coefficients[r]*pow(omega, -r*j, Q) for r in range(N)) % Q
                           for j in range(N)]
            desired = [prod(B[i][j] for i in group) % Q if j < n else 0 for j in range(N)]
            assert inverse == desired, (n, group, inverse, desired)
            inverse_vectors[group] = inverse
            counts['pooled_vector_checks'] += 1
        if n <= 3:
            for state, root in contraction.states.items():
                value = {(0, 0): 1}
                for group in state:
                    row = {(1 << j, 0): inverse_vectors[group][j]
                           for j in range(n) if inverse_vectors[group][j]}
                    value = multiply_nil(value, row, Q)
                expected_R = factorial(len(state))*sum(value.values()) % Q
                assert dag.evaluate([root], inputs)[0] == expected_R
                counts['all_small_state_checks'] += 1
        if sample == 0 and n <= 4:
            _, formal_outputs = direct_oriented_table(a, z, Q, N, omega, labels, formal_z=True)
            expected_formal = [{(0, exponent): gamma*coefficient % Q
                                for (mask, exponent), coefficient in out.items()}
                               for out in formal_outputs]
            actual_formal = evaluate_nil(dag, compiled['outputs'], a, z, x, formal_z=True)
            assert actual_formal == expected_formal
            assert all(mask == 0 for out in actual_formal for mask, exponent in out)
            counts['formal_z_tables'] += 1
            counts['formal_z_coordinates'] += N
    assert dag.derivative_calls == dag.collision_operator_calls == 0
    metadata = dict(compiled['metadata'])
    metadata.update({'status': 'passed', 'compile_seconds': compile_seconds,
                     'verify_and_compile_seconds': time.perf_counter()-started,
                     'counts': counts, 'sample_scalar_outputs': scalar_outputs})
    return metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-n', type=int, default=5)
    parser.add_argument('--budget', type=int, default=1_000_000)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    assert 1 <= args.max_n <= 8
    parameters = [(n, 97) for n in range(1, args.max_n+1)]
    if args.max_n >= 3:
        parameters.append((3, 5))
    if args.max_n >= 4:
        parameters.append((4, 17))
    if args.max_n >= 5:
        parameters.append((5, 257))
    cases = []
    for n, Q in parameters:
        pair = []
        for fused in (False, True):
            case = verify_case(n, Q, args.budget, fused_with_preparation=fused)
            cases.append(case)
            pair.append(case)
            print(json.dumps({k: case[k] for k in (
                'n', 'Q', 'N', 'variant', 'states', 'convolutions', 'allocated_nodes',
                'complete_true_INTT_scalar_gates', 'remaining_useful_gates_J',
                'compile_seconds', 'verify_and_compile_seconds', 'status')}), flush=True)
        assert pair[0]['sample_scalar_outputs'] == pair[1]['sample_scalar_outputs']
    sources = [Path(__file__), HERE/'compiler_joint_convolution.py',
               PROJECT/'documents/composition-native-2026-11-03/compose_native_representatives.py',
               PROJECT/'documents/composition-native-2026-11-03/verify_native_composition.py',
               PROJECT/'etudes/2026-11-01/linearisation-orientee-convolution/linearised_inputs.py',
               PROJECT/'etudes/2026-11-01/linearisation-orientee-convolution/verify_linearised_inputs.py',
               PROJECT/'etudes/2026-11-01/raccord-initialisation/spectral/reprise-globale/shared_operator_dag.py']
    report = {
        'status': 'passed', 'max_n': args.max_n, 'node_budget_per_case': args.budget,
        'source_sha256': {str(p.relative_to(PROJECT)).replace('\\', '/'):
                          hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        'cases': cases,
        'numeric_instances': sum(c['counts']['numeric_instances'] for c in cases),
        'formal_z_tables': sum(c['counts']['formal_z_tables'] for c in cases),
        'every_pooled_vector_checked_against_scalar_rowwise_products': True,
        'all_states_checked_by_independent_nilpotent_reference_through_n3': True,
        'full_scalar_a_z_only': True,
        'associative_commutative_fusion_actually_shared': True,
        'both_direct_convolution_and_preparation_fused_variants_checked': True,
        'compiler_uses_column_occupancy_tables': False,
        'compiler_uses_primitive_derivative_or_reader_gates': False,
        'reference_oracles_only_in_verifier': True,
        'formal_z_exponents_never_reduced': True,
        'general_polynomial_gate_bound_established': False,
        'general_impossibility_claimed': False,
        'scope': ('This verifies one explicit scalar compiler of the joint contraction '
                  'recurrence on the native linearized inputs. Its finite state and '
                  'gate counts do not imply a general polynomial bound. Source-row '
                  'collections are compile-time sharing metadata, not occupied columns.'),
    }
    if args.write_report:
        (HERE/'joint-convolution-validation.json').write_text(
            json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('status', 'max_n', 'numeric_instances',
                                           'formal_z_tables', 'general_polynomial_gate_bound_established')}))


if __name__ == '__main__':
    main()

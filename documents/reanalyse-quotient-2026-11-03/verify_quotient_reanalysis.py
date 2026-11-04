"""Positive checks in the native convolution quotient, not an oracle compiler.

The nilpotent dictionaries are reference calculations only. The n=2
normalizer below is an actual add/mul expression on the already compiled C
wires; it never reads these dictionaries. No general scalar bound is claimed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import factorial
from pathlib import Path
import random
import sys


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
NATIVE = PROJECT/'documents/composition-native-2026-11-03'
sys.path.insert(0, str(NATIVE))
from compose_native_representatives import compile_native_representatives  # noqa: E402
from verify_native_composition import (  # noqa: E402
    add_dictionary, multiply_nil, scale_dictionary, evaluate_nil,
    fourier_orientations, direct_oriented_table,
)


def qsum(values, Q):
    answer = {}
    for value in values:
        answer = add_dictionary(answer, value, Q)
    return answer


def qpower(value, exponent, Q):
    answer = {(0, 0): 1}
    for _ in range(exponent):
        answer = multiply_nil(answer, value, Q)
    return answer


def append_n2_scalar_normalizer(compiled, Q, N, omega, labels):
    """A scalar program on C, valid for exactly n=2 and N=4 here.

    x_0*x_(N/2)=0 and x_(N/2)^2=-x_0^2 in the padded quotient.
    The coefficient of q_0*q_1 is
      (N^2/2)*(C_00*C_10-C_0,N/2*C_1,N/2).
    gamma*q_0*q_1=Omega, so this coefficient is the corrected amplitude.
    """
    assert len(compiled['C']) == 2 and N == 4
    dag, C = compiled['dag'], compiled['C']
    positive = dag.mul(C[0][0], C[1][0])
    negative = dag.mul(C[0][N//2], C[1][N//2])
    difference = dag.add(positive, dag.mul(dag.constant(-1), negative))
    value = dag.mul(dag.constant(N*N*pow(2, -1, Q)), difference)
    frequency = [value]
    phase = dag.constant(pow(omega, sum(labels) % N, Q))
    for _ in range(1, N):
        frequency.append(dag.mul(phase, frequency[-1]))
    output = dag.intt(frequency, omega)
    variables = sorted(dag.nodes[k][1] for k in dag.reachable(output)
                       if dag.nodes[k][0] == 'v')
    assert not any(name.startswith('x_') for name in variables)
    return value, output, variables


def append_n2_preparation_fused_normalizer(compiled, Q, N, omega, labels):
    """Fuse the proved two-row C formula with its preparation, on this DAG.

    Substituting C_i0=(B_i0+B_i1)/N and
    C_i,N/2=(B_i0-B_i1)/N gives exactly the three gates below.
    No gamma is applied to b: the native gamma*q_top label is already Omega.
    """
    assert len(compiled['B']) == 2
    dag, B = compiled['dag'], compiled['B']
    before = sum(node[0] in ('+', '*') for node in dag.nodes)
    value = dag.add(dag.mul(B[0][0], B[1][1]), dag.mul(B[0][1], B[1][0]))
    added = sum(node[0] in ('+', '*') for node in dag.nodes)-before
    assert added == 3
    frequency = [value]
    phase = dag.constant(pow(omega, sum(labels) % N, Q))
    for _ in range(1, N):
        frequency.append(dag.mul(phase, frequency[-1]))
    output = dag.intt(frequency, omega)
    variables = sorted(dag.nodes[k][1] for k in dag.reachable(output)
                       if dag.nodes[k][0] == 'v')
    assert variables == ['a_0_0', 'a_0_1', 'a_1_0', 'a_1_1', 'z']
    preparation = {k for k in dag.reachable([v for row in compiled['C'] for v in row])
                   if dag.nodes[k][0] in ('+', '*')}
    live = {k for k in dag.reachable(output) if dag.nodes[k][0] in ('+', '*')}
    measured = {'new_core_gates': added,
                'useful_preparation_gates': len(live & preparation),
                'remaining_useful_gates_J': len(live-preparation),
                'complete_scalar_output_gates': len(live)}
    assert measured['useful_preparation_gates']+measured['remaining_useful_gates_J'] == dag.count(output)
    return value, output, variables, measured


def verify_case(n, Q, seed):
    N = 1 << n.bit_length()
    assert (Q-1) % N == 0
    omega = next(w for w in range(1, Q)
                 if pow(w, N, Q) == 1 and pow(w, N//2, Q) != 1)
    labels = [j*j+3*j-2*n for j in range(n)]
    labels[0] += 1
    compiled = compile_native_representatives(n, Q, N, omega, labels)
    dag = compiled['dag']
    x = fourier_orientations(n, N, omega, Q)
    invN = pow(N, -1, Q)
    # All convolution relations and all padding equations, not merely readout.
    for t in range(N):
        relation = qsum((multiply_nil(x[r], x[(t-r) % N], Q) for r in range(N)), Q)
        assert relation == {}
    for j in range(N):
        inverse = qsum((scale_dictionary(x[r], invN*pow(omega, -r*j, Q), Q)
                        for r in range(N)), Q)
        assert inverse == ({(1 << j, 0): 1} if j < n else {})
    top = (1 << n)-1
    socle = qpower(x[0], n, Q)
    assert socle == {(top, 0): factorial(n) % Q}
    assert qpower(x[0], n+1, Q) == {}
    for value in x:
        assert multiply_nil(value, socle, Q) == {}
    # Here Q>N>n follows from N|(Q-1), so n! is invertible.
    assert Q > n and factorial(n) % Q != 0
    normalized_socle = scale_dictionary(socle, pow(factorial(n), -1, Q), Q)
    assert normalized_socle == {(top, 0): 1}
    normalizer = None
    fused_normalizer = None
    if n == 2:
        assert multiply_nil(x[0], x[N//2], Q) == {}
        assert qsum([qpower(x[0], 2, Q), qpower(x[N//2], 2, Q)], Q) == {}
        normalizer = append_n2_scalar_normalizer(compiled, Q, N, omega, labels)
        fused_normalizer = append_n2_preparation_fused_normalizer(compiled, Q, N, omega, labels)
    rng = random.Random(seed)
    checks = {'instances': 0, 'frequency_equalities_in_full_quotient': 0,
              'output_equalities_in_full_quotient': 0, 'formal_z_instances': 0,
              'n2_scalar_normalizer_instances': 0}
    for sample in range(4):
        a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
        z = rng.randrange(Q)
        if sample == 1:
            z = 0
        if sample == 2:
            a = [[0]*n for _ in range(n)]
            z = 1
        formal_z = sample == 0 and n <= 3
        uncorrected = evaluate_nil(dag, [compiled['F0']], a, z, x, formal_z=formal_z)[0]
        gamma = compiled['metadata']['gamma']
        direct_spectra, direct_outputs = direct_oriented_table(
            a, z, Q, N, omega, labels, formal_z=formal_z)
        for f in range(N):
            expected = scale_dictionary(uncorrected, gamma*pow(omega, f*sum(labels), Q), Q)
            assert direct_spectra[f] == expected
        # This equality is of full nilpotent dictionaries, before lambda.
        assert evaluate_nil(dag, compiled['spectra'], a, z, x, formal_z=formal_z) == direct_spectra
        assert evaluate_nil(dag, compiled['outputs'], a, z, x, formal_z=formal_z) == direct_outputs
        checks['instances'] += 1
        checks['frequency_equalities_in_full_quotient'] += N
        checks['output_equalities_in_full_quotient'] += N
        checks['formal_z_instances'] += int(formal_z)
        if normalizer is not None:
            value, outputs, variables = normalizer
            inputs = {f'a_{i}_{j}': a[i][j] for i in range(n) for j in range(n)} | {'z': z}
            if formal_z:
                formal_scalar = evaluate_nil(dag, outputs, a, z, x, formal_z=True)
                expected_formal_scalar = [{(0, exponent): gamma*c % Q
                                          for (mask, exponent), c in out.items()}
                                         for out in direct_outputs]
                assert formal_scalar == expected_formal_scalar
                values = dag.evaluate(outputs, inputs)
                # Numeric comparison uses an independently evaluated oracle;
                # formal-z agreement of the quotient was checked above.
                _, numeric_outputs = direct_oriented_table(a, z, Q, N, omega, labels)
                expected = [sum(gamma*c for c in out.values()) % Q for out in numeric_outputs]
            else:
                values = dag.evaluate(outputs, inputs)
                expected = [sum(gamma*c for c in out.values()) % Q for out in direct_outputs]
            assert values == expected
            # Elementary independent formula, used only by this verifier.
            B = [[(1+a[i][j]**2)*pow(z, 2**(i*n+j), Q) % Q for j in range(n)] for i in range(n)]
            assert dag.evaluate([value], inputs)[0] == (B[0][0]*B[1][1]+B[0][1]*B[1][0]) % Q
            assert dag.evaluate(fused_normalizer[1], inputs) == expected
            assert dag.evaluate([fused_normalizer[0]], inputs) == dag.evaluate([value], inputs)
            if formal_z:
                assert evaluate_nil(dag, fused_normalizer[1], a, z, x, formal_z=True) == expected_formal_scalar
            checks['n2_scalar_normalizer_instances'] += 1
    assert dag.derivative_calls == dag.collision_operator_calls == 0
    return {'n': n, 'Q': Q, 'N': N, 'omega': omega, 'labels': labels,
            'padding_equations_checked': N-n, 'inverse_fourier_equations_checked': N,
            'convolution_relations_checked': N,
            'socle_power_equals_factorial_top': True,
            'socle_times_every_x_is_zero': True,
            'factorial_invertible_from_admissibility': True,
            'n2_normalizer_scalar_gates': None if normalizer is None else dag.count([normalizer[0]]),
            'n2_normalized_full_true_INTT_gates': None if normalizer is None else dag.count(normalizer[1]),
            'n2_normalized_output_inputs': None if normalizer is None else normalizer[2],
            'n2_fused_normalizer_scalar_gates': None if fused_normalizer is None else dag.count([fused_normalizer[0]]),
            'n2_fused_normalized_true_INTT_gates': None if fused_normalizer is None else dag.count(fused_normalizer[1]),
            'n2_fused_normalized_output_inputs': None if fused_normalizer is None else fused_normalizer[2],
            'n2_same_DAG_partition': None if fused_normalizer is None else fused_normalizer[3],
            'counts': checks}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    params = [(n, 97) for n in range(1, 9)] + [(2, 5), (3, 5), (7, 17), (8, 17)]
    cases = [verify_case(n, Q, 110300+100*n+Q) for n, Q in params]
    sources = [Path(__file__), NATIVE/'compose_native_representatives.py',
               NATIVE/'verify_native_composition.py',
               PROJECT/'etudes/2026-11-01/linearisation-orientee-convolution/linearised_inputs.py',
               PROJECT/'etudes/2026-11-01/linearisation-orientee-convolution/verify_linearised_inputs.py',
               PROJECT/'etudes/2026-11-01/raccord-initialisation/spectral/reprise-globale/shared_operator_dag.py']
    report = {'status': 'passed',
              'source_sha256': {str(p.relative_to(PROJECT)).replace('\\', '/'):
                                hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
              'cases': cases,
              'total_instances': sum(c['counts']['instances'] for c in cases),
              'full_quotient_frequency_equalities': sum(c['counts']['frequency_equalities_in_full_quotient'] for c in cases),
              'formal_z_instances': sum(c['counts']['formal_z_instances'] for c in cases),
              'normalization_n2_is_actual_scalar_circuit_on_existing_C': True,
              'normalization_n2_fused_with_preparation_uses_three_new_core_gates': True,
              'reference_nilpotent_dictionaries_are_not_compiler_inputs': True,
              'general_scalar_normalizer_constructed': False,
              'general_polynomial_bound_established': False,
              'scope': 'Positive quotient identities and a two-row convolution normalizer only. Small-case verification does not prove a general gate bound.'}
    if args.write_report:
        (HERE/'quotient-reanalysis-validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('status', 'total_instances', 'full_quotient_frequency_equalities',
                                            'formal_z_instances', 'general_polynomial_bound_established')}))


if __name__ == '__main__':
    main()

"""Check the complete native quotient representatives, not a scalar readout.

Nilpotent support dictionaries and formal-z coefficients are reference
computations in this verifier only. No such object enters the compiler.
"""
from __future__ import annotations

import hashlib
import json
from math import prod
from pathlib import Path
import random
import time
from unittest.mock import patch

from compose_native_representatives import (
    compile_native_representatives, DAG, DAG_FOLDER, HISTORICAL_FOLDER, PROJECT,
)
from verify_linearised_inputs import (
    add_dictionary, evaluate_nil, fourier_orientations, multiply_nil,
    reference_scalar_formal, scale_dictionary,
)


def direct_oriented_table(a, z, Q, N, omega, labels, formal_z=False):
    """Independent native row products followed by a naive inverse DFT."""
    n = len(a)
    gamma = (-1)**(n*(n-1)//2)
    spectra = []
    for f in range(N):
        value = {(0, 0): 1}
        for i in range(n):
            row = {}
            for j in range(n):
                exponent = 2**(i*n+j)
                coefficient = (1+a[i][j]**2)*pow(omega, f*labels[j], Q) % Q
                if not formal_z:
                    coefficient = coefficient*pow(z, exponent, Q) % Q
                    exponent = 0
                if coefficient:
                    row[(1 << j, exponent)] = coefficient
            value = multiply_nil(value, row, Q)
        spectra.append(scale_dictionary(value, gamma, Q))
    outputs = []
    for k in range(N):
        value = {}
        for f, spectrum in enumerate(spectra):
            value = add_dictionary(value, scale_dictionary(
                spectrum, pow(N, -1, Q)*pow(omega, -f*k, Q), Q), Q)
        outputs.append(value)
    return spectra, outputs


def verify_case(n, Q, labels, rng):
    N = 1 << n.bit_length()
    omega = next(w for w in range(1, Q)
                 if pow(w, N, Q) == 1 and pow(w, N//2, Q) != 1)
    # Even a direct call bypassing NativeDAG's override would fail here.
    with patch.object(DAG, 'derivative', side_effect=AssertionError('Forbidden derivative')), \
         patch.object(DAG, 'L', side_effect=AssertionError('Forbidden collision operator')):
        compiled = compile_native_representatives(n, Q, N, omega, labels)
    dag, info = compiled['dag'], compiled['metadata']
    x = fourier_orientations(n, N, omega, Q)
    q = pow(N, -1, Q)
    top = (1 << n)-1
    sqrt_minus_one = next(v for v in range(Q) if v*v % Q == Q-1)
    counters = {'numeric_instances': 0, 'coefficient_values': 0,
                'ordinary_INTT_coordinates': 0, 'oriented_spectral_coordinates': 0,
                'oriented_INTT_coordinates': 0, 'oriented_routed_coordinates': 0,
                'formal_z_tables': 0, 'formal_z_INTT_coordinates': 0}
    for sample in range(4):
        a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
        z = rng.randrange(1, Q)
        if sample == 1:
            z = 0
        elif sample == 2:
            a[0] = [sqrt_minus_one]*n
        elif sample == 3:
            a = [[0]*n for _ in range(n)]
            z = 1
        B = [[(1+a[i][j]**2)*pow(z, 2**(i*n+j), Q) % Q
              for j in range(n)] for i in range(n)]
        inputs = {f'a_{i}_{j}': a[i][j] for i in range(n) for j in range(n)} | {'z': z}
        coefficients = [v for row in compiled['C'] for v in row]
        expected_C = [q*sum(B[i][j]*pow(omega, r*j, Q) for j in range(n)) % Q
                      for i in range(n) for r in range(N)]
        assert dag.evaluate(coefficients, inputs) == expected_C
        counters['coefficient_values'] += n*N

        # The synthesized phase/INTT composition is also an ordinary
        # polynomial identity in x; the native per-frequency product is
        # compared only in the quotient below.
        scalar_x = [rng.randrange(Q) for _ in range(N)]
        q_at_x = [q*sum(scalar_x[r]*pow(omega, -r*j, Q) for r in range(N)) % Q
                  for j in range(n)]
        F0_value = prod(sum(B[i][j]*q_at_x[j] for j in range(n)) % Q
                        for i in range(n)) % Q
        expected_ordinary = [0]*N
        expected_ordinary[sum(labels) % N] = info['gamma']*F0_value % Q
        scalar_inputs = inputs | {f'x_{r}': scalar_x[r] for r in range(N)}
        assert dag.evaluate(compiled['outputs'], scalar_inputs) == expected_ordinary
        assert dag.evaluate(compiled['routed'], scalar_inputs) == expected_ordinary
        counters['ordinary_INTT_coordinates'] += N

        native_spectra, native_outputs = direct_oriented_table(a, z, Q, N, omega, labels)
        actual_spectra = evaluate_nil(dag, compiled['spectra'], a, z, x)
        actual_outputs = evaluate_nil(dag, compiled['outputs'], a, z, x)
        actual_routed = evaluate_nil(dag, compiled['routed'], a, z, x)
        assert actual_spectra == native_spectra
        assert actual_outputs == native_outputs == actual_routed
        assert all(mask == top for out in actual_outputs for mask, exponent in out)
        counters['numeric_instances'] += 1
        counters['oriented_spectral_coordinates'] += N
        counters['oriented_INTT_coordinates'] += N
        counters['oriented_routed_coordinates'] += N

        if n <= 3 and sample == 0:
            formal_spectra, formal_outputs = direct_oriented_table(
                a, z, Q, N, omega, labels, formal_z=True)
            actual_formal_spectra = evaluate_nil(
                dag, compiled['spectra'], a, z, x, formal_z=True)
            actual_formal_outputs = evaluate_nil(
                dag, compiled['outputs'], a, z, x, formal_z=True)
            actual_formal_routed = evaluate_nil(
                dag, compiled['routed'], a, z, x, formal_z=True)
            assert actual_formal_spectra == formal_spectra
            assert actual_formal_outputs == formal_outputs == actual_formal_routed
            # q_0...q_(n-1)=gamma*Omega. Conversion of this reference
            # dictionary to Omega coordinates belongs only to the verifier.
            top_output = actual_formal_outputs[sum(labels) % N]
            omega_coordinate = {exponent: coefficient*info['gamma'] % Q
                                for (mask, exponent), coefficient in top_output.items()}
            assert omega_coordinate == reference_scalar_formal(a, Q)
            counters['formal_z_tables'] += 1
            counters['formal_z_INTT_coordinates'] += N
    assert dag.derivative_calls == dag.collision_operator_calls == 0
    assert not dag.derivatives and dag.intt_calls == 1
    info.update(counters)
    info.update({'status': 'passed', 'differential_entry_points_guarded': True,
                 'Q_at_most_n_choose_2': Q <= n*(n-1)//2,
                 'zero_z_checked': True, 'zero_amplitude_row_checked': True,
                 'formal_z_exponents_never_reduced': True})
    return info


def main():
    started = time.perf_counter()
    here = Path(__file__).resolve().parent
    sources = [here/'compose_native_representatives.py', here/'verify_native_composition.py',
               HISTORICAL_FOLDER/'linearised_inputs.py',
               HISTORICAL_FOLDER/'verify_linearised_inputs.py',
               DAG_FOLDER/'shared_operator_dag.py', DAG_FOLDER/'verify_shared_operator_dag.py']
    def hashes():
        return {path.relative_to(PROJECT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sources}
    initial_hashes = hashes()
    rng = random.Random(2026110307)
    cases = []
    parameters = [(n, 97 if n <= 6 else 17) for n in range(1, 9)]
    parameters += [(3, 17), (4, 17)]
    for n, Q in parameters:
        irregular = [j*j + 3*j - 2*n for j in range(n)]
        irregular[0] += 1
        for mode, labels in [('irregular', irregular), ('zero', [0]*n)]:
            info = verify_case(n, Q, labels, rng)
            info['label_mode'] = mode
            cases.append(info)
            print(json.dumps({key: info[key] for key in (
                'n', 'Q', 'N', 'label_mode', 'F0_representative_gates',
                'true_INTT_representative_gates', 'routed_representative_gates', 'status')}), flush=True)
    assert initial_hashes == hashes(), 'A checked source changed during verification'
    count_keys = ('numeric_instances', 'coefficient_values', 'ordinary_INTT_coordinates',
                  'oriented_spectral_coordinates', 'oriented_INTT_coordinates',
                  'oriented_routed_coordinates', 'formal_z_tables', 'formal_z_INTT_coordinates')
    totals = {key: sum(case[key] for case in cases) for key in count_keys}
    assert any(case['n'] == 7 and case['Q'] == 17 and case['Q_at_most_n_choose_2'] for case in cases)
    assert any(case['n'] == 8 and case['Q'] == 17 and case['Q_at_most_n_choose_2'] for case in cases)
    report = {
        'status': 'passed', 'source_sha256': initial_hashes, 'cases': cases, 'totals': totals,
        'elapsed_seconds': time.perf_counter()-started,
        'construction': 'a,z -> B -> normalized coefficient NTT -> F0(x) -> universal sign -> shared phases -> actual INTT',
        'representative_bound_P': '4*n^2-2+2*n*N*log2(N)+3*n*N <= 18*n^3',
        'explicit_INTT_bound': 'P+epsilon_n+2*N*log2(N)+3*N-3',
        'routed_bound': 'P+epsilon_n <= 18*n^3+1',
        'N_contract': 'smallest power of two strictly greater than n; n<N<=2*n',
        'field_contract': 'supplied prime Q, N divides Q-1, supplied omega of exact order N',
        'Q_greater_than_collision_degree_required': False,
        'historical_forward_NTT_and_INTT_reused': True,
        'differential_entry_points_guarded': True,
        'complete_scalar_a_z_only': False,
        'quotient_representatives_complete': True,
        'auxiliary_x_variables_retained': True,
        'quotient_coordinate_extracted': False,
        'primitive_quotient_reading_gate': False,
        'general_polynomial_scalar_amplitude_bound_established': False,
        'compiler_uses_subset_tables': False,
        'verifier_uses_nilpotent_support_tables_and_small_formal_z_oracles': True,
        'lean_formalization_of_this_composition': False,
        'scope': 'The complete corrected oriented output is represented compactly in the quotient. The bound counts ordinary scalar gates in a,z,x; it does not remove the auxiliary orientation variables.',
    }
    report_path = here/'native-composition-validation.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    assert json.loads(report_path.read_text(encoding='utf-8'))['source_sha256'] == hashes()
    print(json.dumps({'status': 'passed', 'totals': totals,
                      'elapsed_seconds': report['elapsed_seconds'],
                      'complete_scalar_a_z_only': False,
                      'quotient_representatives_complete': True}), flush=True)


if __name__ == '__main__':
    main()

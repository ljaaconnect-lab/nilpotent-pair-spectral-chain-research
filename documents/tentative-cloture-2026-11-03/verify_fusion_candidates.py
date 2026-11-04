"""Small exact tests of fusion candidates on the existing native compiler.

This is a verifier, not a proposed general compiler. Nilpotent support
dictionaries occur only in the independent small-case oracle. No historical
source is edited. Run with --write-report to save the reproducible result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import prod
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
NATIVE_FOLDER = PROJECT / 'documents/composition-native-2026-11-03'
sys.path.insert(0, str(NATIVE_FOLDER))
from compose_native_representatives import compile_native_representatives  # noqa: E402
from verify_native_composition import (  # noqa: E402
    direct_oriented_table, evaluate_nil, fourier_orientations,
)


def dual_product(y, n, N, omega, Q):
    """Evaluate the existing dual D_n(y), using scalar additions/products."""
    return prod(sum(pow(omega, s*j, Q)*y[s] for s in range(N)) % Q
                for j in range(n)) % Q


def small_oriented_oracle(a, z, Q, N, omega, labels):
    """Reference only: actual oriented multiplication and naive inverse DFT."""
    spectra, outputs = direct_oriented_table(a, z, Q, N, omega, labels)
    gamma = (-1)**(len(a)*(len(a)-1)//2)
    top = (1 << len(a))-1
    assert all(mask == top for out in outputs for mask, exponent in out)
    # The stored dictionary uses q_top=gamma*Omega. This conversion is
    # verification work and is not claimed as a gate of the native compiler.
    coordinates = [sum(gamma*c for (mask, exponent), c in out.items()) % Q
                   for out in outputs]
    return spectra, outputs, coordinates


def verify_padded_family():
    """Embed the two legal blocks in diag(B2,I), using no new compiler.

    The finite verification is restricted to n=2,...,8 over F_97, where
    every required radix-2 transform length divides 96.
    """
    Q = 97
    assert (1+22*22) % Q == 0
    assert [(1+a*a) % Q for a in (0, 2, 14)] == [1, 5, 3]
    rows = []
    for n in range(2, 9):
        N = 1 << n.bit_length()
        omega = next(w for w in range(1, Q)
                     if pow(w, N, Q) == 1 and pow(w, N//2, Q) != 1)
        labels = list(range(n))
        compiled = compile_native_representatives(n, Q, N, omega, labels)
        dag, gamma = compiled['dag'], compiled['metadata']['gamma']
        target = sum(labels) % N
        x_nil = fourier_orientations(n, N, omega, Q)
        x_scalar = [sum(pow(omega, r*j, Q) for j in range(n)) % Q
                    for r in range(N)]
        pair = []
        for block in ([[0, 2], [2, 0]], [[14, 14], [14, 14]]):
            a = [[0 if i == j else 22 for j in range(n)] for i in range(n)]
            for i in range(2):
                for j in range(2):
                    a[i][j] = block[i][j]
            inputs = {f'a_{i}_{j}': a[i][j] for i in range(n) for j in range(n)} | {'z': 1}
            scalar_inputs = inputs | {f'x_{r}': x_scalar[r] for r in range(N)}
            B_flat = dag.evaluate([v for r in compiled['B'] for v in r], inputs)
            B = [B_flat[i*n:(i+1)*n] for i in range(n)]
            C_flat = dag.evaluate([v for r in compiled['C'] for v in r], inputs)
            C = [C_flat[i*N:(i+1)*N] for i in range(n)]
            cumulative = [sum(C[i][(-s) % N] for i in range(n)) % Q for s in range(N)]
            F0_at_q_one = dag.evaluate([compiled['F0']], scalar_inputs)[0]
            ordinary_outputs = dag.evaluate(compiled['outputs'], scalar_inputs)
            assert F0_at_q_one == 36
            assert ordinary_outputs == [gamma*36 % Q if k == target else 0 for k in range(N)]
            spectrum, oriented_outputs, coordinates = small_oriented_oracle(a, 1, Q, N, omega, labels)
            assert evaluate_nil(dag, compiled['spectra'], a, 1, x_nil) == spectrum
            assert evaluate_nil(dag, compiled['outputs'], a, 1, x_nil) == oriented_outputs
            assert all(coordinates[k] == 0 for k in range(N) if k != target)
            trajectory = [dual_product([t*x % Q for x in cumulative], n, N, omega, Q)
                          for t in range(Q)]
            assert trajectory == [36*pow(t, n, Q) % Q for t in range(Q)]
            assert [sum(r) % Q for r in B] == [6, 6]+[1]*(n-2)
            assert [sum(B[i][j] for i in range(n)) % Q for j in range(n)] == [6, 6]+[1]*(n-2)
            pair.append({'a': a, 'cumulative_direction': cumulative,
                         'F0_at_q_one': F0_at_q_one,
                         'ordinary_true_INTT_outputs_including_gamma': ordinary_outputs,
                         'oriented_Omega_coordinates_oracle': coordinates})
        assert pair[0]['cumulative_direction'] == pair[1]['cumulative_direction']
        assert [p['oriented_Omega_coordinates_oracle'][target] for p in pair] == [26, 18]
        assert dag.derivative_calls == dag.collision_operator_calls == 0 and dag.intt_calls == 1
        rows.append({'n': n, 'Q': Q, 'N': N, 'omega': omega, 'labels': labels,
                     'gamma': gamma, 'target_slot': target, 'cases': pair,
                     'all_97_cumulative_translation_values_equal_36_t_power_n': True,
                     'native_representative_gate_count': dag.count(compiled['outputs'])})
    return rows


def verify():
    n, Q, N, omega, z = 2, 97, 4, 22, 1
    labels = [0, 1]
    assert pow(omega, N, Q) == 1 and pow(omega, N//2, Q) != 1
    compiled = compile_native_representatives(n, Q, N, omega, labels)
    dag = compiled['dag']
    target, gamma = sum(labels) % N, compiled['metadata']['gamma']
    x_nil = fourier_orientations(n, N, omega, Q)
    x_scalar = [sum(pow(omega, r*j, Q) for j in range(n)) % Q
                for r in range(N)]
    cases = []
    for name, a in (
        ('unequal_entries', [[0, 2], [2, 0]]),
        ('equal_entries', [[14, 14], [14, 14]]),
    ):
        inputs = {f'a_{i}_{j}': a[i][j] for i in range(n) for j in range(n)} | {'z': z}
        B_flat = dag.evaluate([v for row in compiled['B'] for v in row], inputs)
        B = [B_flat[i*n:(i+1)*n] for i in range(n)]
        C_flat = dag.evaluate([v for row in compiled['C'] for v in row], inputs)
        C = [C_flat[i*N:(i+1)*N] for i in range(n)]
        v = [[C[i][(-s) % N] for s in range(N)] for i in range(n)]
        cumulative = [sum(row[s] for row in v) % Q for s in range(N)]
        # Check the Fourier bridge on these very C wires, not reconstructed C.
        reconstructed_B = [[sum(pow(omega, s*j, Q)*v[i][s] for s in range(N)) % Q
                            for j in range(n)] for i in range(n)]
        assert reconstructed_B == B
        scalar_inputs = inputs | {f'x_{r}': x_scalar[r] for r in range(N)}
        F0_at_q_one = dag.evaluate([compiled['F0']], scalar_inputs)[0]
        ordinary_outputs = dag.evaluate(compiled['outputs'], scalar_inputs)
        assert ordinary_outputs == [gamma*F0_at_q_one % Q if k == target else 0
                                    for k in range(N)]
        native_spectra, native_outputs, omega_coordinates = small_oriented_oracle(
            a, z, Q, N, omega, labels)
        assert evaluate_nil(dag, compiled['spectra'], a, z, x_nil) == native_spectra
        assert evaluate_nil(dag, compiled['outputs'], a, z, x_nil) == native_outputs
        trajectory = [dual_product([t*x % Q for x in cumulative], n, N, omega, Q)
                      for t in range(Q)]
        assert trajectory == [36*t*t % Q for t in range(Q)]
        individual = [dual_product(row, n, N, omega, Q) for row in v]
        # Exact two-direction repair from Delta_u Delta_v =
        # T_(u+v)-T_u-T_v+I. D_2(0)=0.
        repaired = (dual_product(cumulative, n, N, omega, Q)-sum(individual)) % Q
        assert repaired == omega_coordinates[target]
        cases.append({
            'name': name, 'a': a, 'B': B, 'C': C, 'v': v,
            'cumulative_direction': cumulative,
            'row_sums': [sum(row) % Q for row in B],
            'column_sums': [sum(B[i][j] for i in range(n)) % Q for j in range(n)],
            'F0_at_q_one': F0_at_q_one,
            'ordinary_true_INTT_outputs_including_gamma': ordinary_outputs,
            'oriented_Omega_coordinates_oracle': omega_coordinates,
            'cumulative_translation_values_t_0_through_96': trajectory,
            'individual_dual_values': individual,
            'exact_two_direction_repair': repaired,
        })
    assert cases[0]['cumulative_direction'] == cases[1]['cumulative_direction']
    assert cases[0]['F0_at_q_one'] == cases[1]['F0_at_q_one'] == 36
    assert [c['oriented_Omega_coordinates_oracle'][target] for c in cases] == [26, 18]
    assert cases[0]['ordinary_true_INTT_outputs_including_gamma'] == \
        cases[1]['ordinary_true_INTT_outputs_including_gamma']
    assert dag.derivative_calls == dag.collision_operator_calls == 0
    assert dag.intt_calls == 1
    sources = [Path(__file__),
               NATIVE_FOLDER/'compose_native_representatives.py',
               NATIVE_FOLDER/'verify_native_composition.py',
               PROJECT/'etudes/2026-11-01/linearisation-orientee-convolution/linearised_inputs.py',
               PROJECT/'etudes/2026-11-01/linearisation-orientee-convolution/verify_linearised_inputs.py',
               PROJECT/'etudes/2026-11-01/raccord-initialisation/spectral/reprise-globale/shared_operator_dag.py']
    return {
        'status': 'passed', 'parameters': {'n': n, 'Q': Q, 'N': N, 'omega': omega,
                                        'labels': labels, 'z': z, 'gamma': gamma},
        'source_sha256': {str(p.relative_to(PROJECT)).replace('\\', '/'):
                          hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        'native_compiler_reused': True, 'same_C_wires_and_true_INTT': True,
        'x_signal_for_q_equal_one': x_scalar,
        'native_representative_gate_count': dag.count(compiled['outputs']),
        'cases': cases,
        'padded_family_n_2_through_8': verify_padded_family(),
        'all_97_cumulative_translation_readings_agree': True,
        'cumulative_direction_alone_does_not_determine_terminal_reading': True,
        'q_one_specialization_does_not_determine_terminal_reading': True,
        'two_direction_fusion_repair_exact': True,
        'general_polynomial_gate_bound_established': False,
        'general_impossibility_claimed': False,
        'oracle_only_uses_nilpotent_support_dictionaries': True,
        'scope': ('Only the proposed loss of all separate directions, and the q=1 '
                  'specialization, are distinguished by this legal pair. The exact '
                  'two-direction repair retains the two individual dual readings; '
                  'no bound for arbitrary numbers of directions is inferred. The '
                  'padded-family checks are limited to n=2,...,8 over F_97 and '
                  'do not assert availability of every transform length in F_97.'),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    report = verify()
    if args.write_report:
        (HERE/'fusion-candidates-validation.json').write_text(
            json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'F0_at_q_one': [36, 36],
                      'oriented_Omega_coordinates': [26, 18],
                      'two_direction_repair': [c['exact_two_direction_repair'] for c in report['cases']],
                      'general_polynomial_gate_bound_established': False}))


if __name__ == '__main__':
    main()

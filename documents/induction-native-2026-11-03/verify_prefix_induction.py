"""Finite checks of the native prefix invariant and its shared gate count.

The compiler is imported unchanged. Nilpotent support dictionaries are
reference objects used only here to interpret its auxiliary x variables.
These checks do not prove an all-n bound or eliminate the auxiliary inputs.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
import sys
import time
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
COMPOSITION_FOLDER = PROJECT / 'documents/composition-native-2026-11-03'
sys.path.insert(0, str(COMPOSITION_FOLDER))
from compose_native_representatives import (  # noqa: E402
    compile_native_representatives, DAG, DAG_FOLDER, HISTORICAL_FOLDER,
)
from verify_linearised_inputs import (  # noqa: E402
    evaluate_nil, fourier_orientations, multiply_nil,
)


def reference_prefixes(a, z, Q, formal_z=False):
    """Direct unmodulated native row products, independent of the NTT."""
    n = len(a)
    prefixes = [{(0, 0): 1}]
    for i in range(n):
        row = {}
        for j in range(n):
            exponent = 1 << (i*n+j)
            coefficient = (1+a[i][j]**2) % Q
            if not formal_z:
                coefficient = coefficient*pow(z, exponent, Q) % Q
                exponent = 0
            if coefficient:
                row[(1 << j, exponent)] = coefficient
        prefixes.append(multiply_nil(prefixes[-1], row, Q))
    return prefixes


def homogeneous_degrees(dag, roots):
    """Check the syntactic total x-degree, ignoring degrees in a,z."""
    degrees = {}
    for index in sorted(dag.reachable(roots)):
        node = dag.nodes[index]
        if node[0] == 'c':
            degrees[index] = 0
        elif node[0] == 'v':
            degrees[index] = int(node[1].startswith('x_'))
        elif node[0] == '+':
            assert degrees[node[1]] == degrees[node[2]], (index, node)
            degrees[index] = degrees[node[1]]
        elif node[0] == '*':
            degrees[index] = degrees[node[1]] + degrees[node[2]]
        else:
            raise AssertionError(('non-scalar gate', node))
    return degrees


def verify_case(n, Q, rng):
    N = 1 << n.bit_length()
    omega = next(w for w in range(1, Q)
                 if pow(w, N, Q) == 1 and pow(w, N//2, Q) != 1)
    with patch.object(DAG, 'derivative', side_effect=AssertionError('Forbidden derivative')), \
         patch.object(DAG, 'L', side_effect=AssertionError('Forbidden collision operator')):
        compiled = compile_native_representatives(n, Q, N, omega, [0]*n)
        dag = compiled['dag']
        # Keep precisely the compiled row forms and their shared C inputs.
        # The imported F0 uses a balanced tree; this adds the inductive chain.
        prefixes = [dag.one]
        for form in compiled['forms']:
            prefixes.append(dag.mul(prefixes[-1], form))

    coefficient_roots = [root for row in compiled['C'] for root in row]
    coefficient_reachable = dag.reachable(coefficient_roots)
    coefficient_gates = dag.count(coefficient_roots)
    coefficient_bound = compiled['metadata']['coefficient_bound']
    assert coefficient_gates <= coefficient_bound
    assert dag.count([prefixes[0]]) == 0
    assert len(compiled['x']) == N
    expected_auxiliary = {f'x_{r}' for r in range(N)}
    expected_original = {'z'} | {f'a_{i}_{j}' for i in range(n) for j in range(n)}
    allocated_variables = {node[1] for node in dag.nodes if node[0] == 'v'}
    assert allocated_variables == expected_original | expected_auxiliary

    rank_checks = []
    previous_gates = coefficient_gates
    degrees = homogeneous_degrees(dag, coefficient_roots + prefixes)
    for k, prefix in enumerate(prefixes):
        # Count reachable gates from all C roots and the completed prefixes,
        # never the allocation count or future compiled forms/spectral nodes.
        roots = coefficient_roots + prefixes[:k+1]
        reachable = dag.reachable(roots)
        used_forms = dag.reachable(compiled['forms'][:k])
        assert reachable <= coefficient_reachable | used_forms | set(prefixes[:k+1])
        gates = dag.count(roots)
        assert gates == dag.count(coefficient_roots + [prefix])
        assert gates <= coefficient_gates + 2*k*N
        assert gates <= coefficient_bound + 2*k*N <= 18*n**3
        if k:
            assert 0 <= gates-previous_gates <= 2*N
            assert gates <= coefficient_gates + 2*k*N-1
        else:
            assert gates == coefficient_gates
        variables = {dag.nodes[index][1] for index in reachable
                     if dag.nodes[index][0] == 'v'}
        assert variables <= expected_original | expected_auxiliary
        auxiliary = {v for v in variables if v.startswith('x_')}
        assert auxiliary == (expected_auxiliary if k else set())
        assert degrees[prefix] == k
        rank_checks.append({
            'rank': k, 'homogeneous_x_degree': degrees[prefix],
            'shared_gates_including_all_C': gates,
            'additional_gates_this_rank': gates-previous_gates,
            'bound_using_actual_C': coefficient_gates+2*k*N,
            'bound_using_C_majorant': coefficient_bound+2*k*N,
            'auxiliary_variable_count': len(auxiliary),
        })
        previous_gates = gates

    transformed = fourier_orientations(n, N, omega, Q)
    sqrt_minus_one = next(v for v in range(Q) if v*v % Q == Q-1)
    sample_modes = ('random', 'zero_z', 'zero_first_row', 'zero_last_row',
                    'all_a_zero_z_one', 'second_random')
    totals = {'numeric_instances': 0, 'numeric_prefix_identities': 0,
              'ordinary_prefix_values': 0, 'terminal_F0_identities': 0,
              'formal_z_instances': 0, 'formal_z_prefix_identities': 0}
    for mode in sample_modes:
        a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
        z = rng.randrange(1, Q)
        if mode == 'zero_z':
            z = 0
        elif mode == 'zero_first_row':
            a[0] = [sqrt_minus_one]*n
        elif mode == 'zero_last_row':
            a[-1] = [sqrt_minus_one]*n
        elif mode == 'all_a_zero_z_one':
            a = [[0]*n for _ in range(n)]
            z = 1

        expected = reference_prefixes(a, z, Q)
        actual = evaluate_nil(dag, prefixes, a, z, transformed)
        assert actual == expected, (n, Q, mode, 'oriented prefix identities')
        assert actual[0] == {(0, 0): 1}
        for k, value in enumerate(actual):
            assert all(mask.bit_count() == k for mask, exponent in value)
        balanced = evaluate_nil(dag, [compiled['F0']], a, z, transformed)[0]
        assert actual[-1] == balanced

        # Also check the ordinary representative, without quotienting x.
        scalar_x = [rng.randrange(Q) for _ in range(N)]
        inverse_N = pow(N, -1, Q)
        q_at_x = [inverse_N*sum(scalar_x[r]*pow(omega, -r*j, Q)
                                for r in range(N)) % Q for j in range(n)]
        expected_ordinary = [1]
        for i in range(n):
            row = sum((1+a[i][j]**2)*pow(z, 1 << (i*n+j), Q)*q_at_x[j]
                      for j in range(n)) % Q
            expected_ordinary.append(expected_ordinary[-1]*row % Q)
        inputs = ({f'a_{i}_{j}': a[i][j] for i in range(n) for j in range(n)}
                  | {'z': z} | {f'x_{r}': scalar_x[r] for r in range(N)})
        ordinary = dag.evaluate(prefixes + [compiled['F0']], inputs)
        assert ordinary[:-1] == expected_ordinary
        assert ordinary[-1] == ordinary[-2]
        totals['numeric_instances'] += 1
        totals['numeric_prefix_identities'] += n+1
        totals['ordinary_prefix_values'] += n+1
        totals['terminal_F0_identities'] += 2

        if n <= 3 and mode == 'random':
            formal_expected = reference_prefixes(a, z, Q, formal_z=True)
            formal_actual = evaluate_nil(dag, prefixes, a, z, transformed, formal_z=True)
            assert formal_actual == formal_expected
            formal_balanced = evaluate_nil(
                dag, [compiled['F0']], a, z, transformed, formal_z=True)[0]
            assert formal_actual[-1] == formal_balanced
            totals['formal_z_instances'] += 1
            totals['formal_z_prefix_identities'] += n+1

    assert dag.derivative_calls == dag.collision_operator_calls == 0
    assert not dag.derivatives
    return {
        'n': n, 'Q': Q, 'N': N, 'omega': omega, 'status': 'passed',
        'coefficient_scalar_gates': coefficient_gates,
        'coefficient_bound': coefficient_bound,
        'rank_checks': rank_checks, 'sample_modes': list(sample_modes), 'totals': totals,
        'Q_at_most_n_choose_2': Q <= n*(n-1)//2,
        'allocated_nodes_not_used_as_prefix_gate_count': len(dag.nodes),
        'prefix_zero_is_one': True, 'all_C_preparation_included': True,
        'future_forms_not_counted': True, 'auxiliary_names_unchanged': True,
        'no_other_variable_leaves': True,
        'last_prefix_matches_balanced_F0': True,
        'derivative_calls': dag.derivative_calls,
        'collision_operator_calls': dag.collision_operator_calls,
    }


def main():
    started = time.perf_counter()
    sources = [Path(__file__), COMPOSITION_FOLDER/'compose_native_representatives.py',
               HISTORICAL_FOLDER/'linearised_inputs.py',
               HISTORICAL_FOLDER/'verify_linearised_inputs.py',
               DAG_FOLDER/'shared_operator_dag.py', DAG_FOLDER/'verify_shared_operator_dag.py']

    def hashes():
        return {path.relative_to(PROJECT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sources}

    source_hashes = hashes()
    rng = random.Random(2026110311)
    cases = []
    for n in range(1, 9):
        case = verify_case(n, 97 if n <= 6 else 17, rng)
        cases.append(case)
        print(json.dumps({'n': n, 'Q': case['Q'], 'N': case['N'],
                          'ranks_checked': len(case['rank_checks']),
                          'terminal_shared_gates': case['rank_checks'][-1]['shared_gates_including_all_C'],
                          'status': 'passed'}), flush=True)
    assert source_hashes == hashes(), 'A checked source changed during verification'
    totals = {key: sum(case['totals'][key] for case in cases) for key in cases[0]['totals']}
    totals['structural_rank_checks'] = sum(len(case['rank_checks']) for case in cases)
    assert all(case['Q_at_most_n_choose_2'] for case in cases[-2:])
    report = {
        'status': 'passed', 'source_sha256': source_hashes, 'cases': cases, 'totals': totals,
        'elapsed_seconds': time.perf_counter()-started,
        'prefix_specification': 'F_0=1; F_(k+1)=F_k*sum_r C[k,r]*x[-r mod N]',
        'semantics_checked': 'rho_x(F_k)=product of the first k unmodulated native oriented rows',
        'cost_checked': 'reachable gates for all C roots and prefixes through k <= actual_G_C+2*k*N',
        'uniform_majorant_checked': 'G_C_bound+2*k*N <= 18*n^3 for all tested 0<=k<=n',
        'counting_rule': 'shared reachable arithmetic gates only; future forms and spectral nodes excluded',
        'source_compiler_unchanged': True,
        'reference_support_tables_only_in_verifier': True,
        'general_induction_formally_proved_by_this_script': False,
        'finite_checks_do_not_replace_general_proof': True,
        'complete_scalar_a_z_only': False,
        'auxiliary_x_variables_retained': True,
        'general_polynomial_scalar_amplitude_bound_established': False,
    }
    report_path = HERE/'prefix-induction-validation.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    assert json.loads(report_path.read_text(encoding='utf-8'))['source_sha256'] == hashes()
    print(json.dumps({'status': 'passed', 'totals': totals,
                      'elapsed_seconds': report['elapsed_seconds']}), flush=True)


if __name__ == '__main__':
    main()

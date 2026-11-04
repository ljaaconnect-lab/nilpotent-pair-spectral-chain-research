"""Disjoint useful-gate inventory of both complete scalar compiler variants.

The chronological allocation of a gate does not determine its attribution.
For the fused variant a sum reused from the native NTT preparation is
charged to its scalar group weight, while P/T/J is reported separately.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import comb
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
sys.path.insert(0, str(PROJECT/'documents/reanalyse-quotient-2026-11-03'))
sys.path.insert(0, str(PROJECT/'documents/cout-meme-circuit-2026-11-03'))
from compiler_joint_convolution import compile_joint_convolution
from measure_same_dag import ancestors


def measure(n, Q=97, fused=True):
    N = 1 << n.bit_length()
    ell = N.bit_length()-1
    omega = next(w for w in range(1, Q)
                 if pow(w, N, Q) == 1 and pow(w, N//2, Q) != 1)
    labels = [j*j+3*j-2*n for j in range(n)]
    labels[0] += 1
    result = compile_joint_convolution(n, Q, N, omega, labels,
                                       fused_with_preparation=fused)
    dag, native, contraction = result['dag'], result['native'], result['contraction']
    nodes = dag.nodes
    lookup = {node: i for i, node in enumerate(nodes)}
    variables = {node[1]: i for i, node in enumerate(nodes) if node[0] == 'v'}

    def existing(op, a, b):
        return lookup[(op, min(a, b), max(a, b))]

    marks = [variables['z']]
    for _ in range(n*n-1):
        marks.append(existing('*', marks[-1], marks[-1]))
    squares = [existing('*', variables[f'a_{i}_{j}'], variables[f'a_{i}_{j}'])
               for i in range(n) for j in range(n)]
    offsets = [existing('+', dag.one, square) for square in squares]
    B = [r for row in native['B'] for r in row]
    C = [r for row in native['C'] for r in row]
    pool = contraction.row_pool if fused else contraction.vector_pool
    pool_roots = [r for row in pool.values() for r in row]
    group_count = len(contraction.group_weights)
    state_cost_bound = sum(2*len(state)+comb(len(state), 2)
                           for state in contraction.states if len(state) >= 2)
    assert group_count <= 2**n-1
    assert len(contraction.states) <= (n+1)**n
    assert len(pool) == group_count
    vector_bound = (n if fused else 2*N*N-N)*(group_count-n)
    weight_bound = (n-1 if fused else 1)*group_count
    stages = [
        ('z_powers', marks, n*n-1),
        ('a_squares', squares, n*n),
        ('one_plus_a_squared', offsets, n*n),
        ('B_products', B, n*n),
        ('coefficient_NTT', [] if fused else C, 0 if fused else 2*n*N*ell+n*N),
        ('fusion_vectors', pool_roots, vector_bound),
        ('group_weights', list(contraction.group_weights.values()), weight_bound),
        ('R_recurrence', list(contraction.states.values()), state_cost_bound),
        ('factorial_normalization', [result['scalar']], 1),
        ('universal_sign_in_terminal_label', [], 0),
        ('shared_phases', result['spectra'], N-1),
        ('true_INTT', result['outputs'], 2*N*ell+N),
    ]
    live = ancestors(nodes, result['outputs'])
    assert live == dag.reachable(result['outputs'])
    arithmetic = {i for i in live if nodes[i][0] in ('+', '*')}
    seen = set()
    records = []
    for name, roots, bound in stages:
        part = (ancestors(nodes, roots) & arithmetic)-seen
        assert len(part) <= bound, (n, fused, name, len(part), bound)
        records.append({'stage': name, 'useful_distinct_gates': len(part),
                        'additions': sum(nodes[i][0] == '+' for i in part),
                        'multiplications': sum(nodes[i][0] == '*' for i in part),
                        'upper_bound_for_this_group_and_state_count': bound})
        seen.update(part)
    assert seen == arithmetic
    assert sum(s['useful_distinct_gates'] for s in records) == len(arithmetic)
    prep = {i for i in ancestors(nodes, C) if nodes[i][0] in ('+', '*')}
    inputs = sorted(nodes[i][1] for i in live if nodes[i][0] == 'v')
    assert all(s == 'z' or s.startswith('a_') for s in inputs)
    assert len(arithmetic) == result['metadata']['complete_true_INTT_scalar_gates']
    assert len(arithmetic & prep) == result['metadata']['useful_preparation_gates']
    assert len(arithmetic-prep) == result['metadata']['remaining_useful_gates_J']
    graph = json.dumps({'nodes': nodes, 'outputs': result['outputs']}, separators=(',', ':'))
    return {'n': n, 'Q': Q, 'N': N, 'omega': omega, 'labels': labels,
            'variant': result['metadata']['variant'], 'groups': group_count,
            'states': len(contraction.states), 'stages': records,
            'total_gates': len(arithmetic), 'useful_preparation_P': len(arithmetic & prep),
            'residual_J': len(arithmetic-prep), 'full_scalar_a_z_only': True,
            'partition_disjoint_and_complete': True,
            'graph_and_outputs_sha256': hashlib.sha256(graph.encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    prior = json.loads((PROJECT/'documents/reanalyse-quotient-2026-11-03/joint-convolution-validation.json').read_text())
    sources = [Path(__file__), PROJECT/'documents/cout-meme-circuit-2026-11-03/measure_same_dag.py']
    sources += [PROJECT/name for name in prior['source_sha256']]
    hashes = {p.relative_to(PROJECT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sources}
    cases = []
    for old in prior['cases']:
        case = measure(old['n'], old['Q'], old['variant'] == 'fused_with_preparation')
        assert case['total_gates'] == old['complete_true_INTT_scalar_gates']
        assert case['useful_preparation_P'] == old['useful_preparation_gates']
        assert case['residual_J'] == old['remaining_useful_gates_J']
        cases.append(case)
        print(json.dumps({k: case[k] for k in ('n', 'Q', 'variant', 'total_gates', 'residual_J')}))
    assert hashes == {name: hashlib.sha256((PROJECT/name).read_bytes()).hexdigest() for name in hashes}
    report = {'status': 'passed', 'source_sha256': hashes, 'cases': cases,
              'counting_model': 'Distinct useful binary +/* gates, structural constants and wires free.',
              'allocation_time_is_not_semantic_attribution': True,
              'partition_disjoint_and_complete_for_every_case': True,
              'all_totals_equal_previous_semantically_verified_compiler_report': True,
              'scope': 'Complete scalar circuits including true INTT; the fused variant charges reused sums to group weights, not to a separate NTT block.',
              'general_polynomial_bound_proved': False}
    if args.write_report:
        (HERE/'complete-inventory-validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': 'passed', 'cases': len(cases)}))


if __name__ == '__main__':
    main()

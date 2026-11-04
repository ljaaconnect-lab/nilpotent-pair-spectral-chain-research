"""Count distinct useful scalar gates of the existing native INTT program.

This measures ONE emitted graph per instance, without adding a normalizer.
Its outputs retain x_r. Counts for a normalized original-input-only program
are deliberately absent, rather than populated with representative counts.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
COMPILER_FOLDER = PROJECT / 'documents/composition-native-2026-11-03'
sys.path.insert(0, str(COMPILER_FOLDER))
from compose_native_representatives import (  # noqa: E402
    compile_native_representatives, HISTORICAL_FOLDER, DAG_FOLDER,
)


def ancestors(nodes, roots):
    """Independent reverse topological traversal of a previously emitted DAG."""
    live = set(roots)
    for idx in range(len(nodes) - 1, -1, -1):
        node = nodes[idx]
        assert node[0] in ('c', 'v', '+', '*')
        if node[0] in ('+', '*'):
            assert all(isinstance(j, int) and 0 <= j < idx for j in node[1:])
            if idx in live:
                live.update(node[1:])
    return live


def measure(n, Q):
    N = 1 << n.bit_length()
    omega = next(w for w in range(1, Q)
                 if pow(w, N, Q) == 1 and pow(w, N // 2, Q) != 1)
    labels = [j*j + 3*j - 2*n for j in range(n)]
    labels[0] += 1
    compiled = compile_native_representatives(n, Q, N, omega, labels)
    dag, info = compiled['dag'], compiled['metadata']
    nodes, outputs = dag.nodes, compiled['outputs']
    live = ancestors(nodes, outputs)
    final_gates = {i for i in live if nodes[i][0] in ('+', '*')}
    assert live == dag.reachable(outputs)
    assert len(final_gates) == dag.count(outputs)
    ell = N.bit_length() - 1
    stages = [
        ('B', [r for row in compiled['B'] for r in row], 4*n*n-1),
        ('coefficient_NTT', [r for row in compiled['C'] for r in row], 2*n*N*ell+n*N),
        ('row_forms', compiled['forms'], n*(2*N-1)),
        ('shared_product', [compiled['F0']], n-1),
        ('universal_sign', [compiled['corrected']], info['epsilon']),
        ('shared_phases', compiled['spectra'], N-1),
        ('true_INTT', outputs, 2*N*ell+N),
    ]
    attributed = set()
    records = []
    for name, roots, bound in stages:
        candidates = ancestors(nodes, roots) & final_gates
        fresh = candidates - attributed
        assert not (fresh & attributed)
        assert len(fresh) <= bound, (name, len(fresh), bound)
        records.append({
            'stage': name, 'new_distinct_useful_gates': len(fresh),
            'additions': sum(nodes[i][0] == '+' for i in fresh),
            'multiplications': sum(nodes[i][0] == '*' for i in fresh),
            'upper_bound': bound,
        })
        attributed.update(fresh)
    assert attributed == final_gates
    assert sum(r['new_distinct_useful_gates'] for r in records) == len(final_gates)
    coefficient_roots = [r for row in compiled['C'] for r in row]
    prep = {i for i in ancestors(nodes, coefficient_roots) if nodes[i][0] in ('+', '*')}
    reused = final_gates & prep
    residual = final_gates - prep
    assert len(final_gates) == len(reused) + len(residual)
    prep_bound = 4*n*n-1+2*n*N*ell+n*N
    assert len(prep) <= prep_bound <= 10*n**3
    assert len(final_gates) <= info['true_INTT_bound'] <= 29*n**3
    variables = sorted(nodes[i][1] for i in live if nodes[i][0] == 'v')
    auxiliaries = [v for v in variables if v.startswith('x_')]
    assert set(auxiliaries) == {f'x_{r}' for r in range(N)}
    encoded = json.dumps({'nodes': nodes, 'outputs': outputs}, separators=(',', ':')).encode()
    return {
        'n': n, 'Q': Q, 'N': N, 'omega': omega, 'labels': labels,
        'graph_and_output_roots_sha256': hashlib.sha256(encoded).hexdigest(),
        'stages': records, 'all_useful_scalar_gates': len(final_gates),
        'allocated_arithmetic_gates': sum(node[0] in ('+', '*') for node in nodes),
        'preparation_gates': len(prep), 'preparation_gates_used_by_output': len(reused),
        'representative_residual_gates': len(residual),
        'preparation_bound': prep_bound, 'explicit_complete_representative_bound': info['true_INTT_bound'],
        'cubic_complete_representative_bound': 29*n**3,
        'auxiliary_input_count': len(auxiliaries),
        'original_input_count': len(variables)-len(auxiliaries),
        'partitions_exact': True, 'same_graph_for_all_stages': True,
        'forward_NTT_calls': n, 'actual_INTT_calls': dag.intt_calls,
        'derivative_calls': dag.derivative_calls, 'collision_filter_calls': dag.collision_operator_calls,
        'normalized_scalar_chain_gates': None,
        'normalized_scalar_chain_constructed_by_this_program': False,
    }


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sources = [Path(__file__), COMPILER_FOLDER/'compose_native_representatives.py',
               HISTORICAL_FOLDER/'linearised_inputs.py', DAG_FOLDER/'shared_operator_dag.py']

    def hashes():
        return {p.relative_to(PROJECT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sources}

    before = hashes()
    started = time.monotonic()
    parameters = [(n, 97 if n <= 6 or n >= 9 else 17) for n in range(1, 17)]
    parameters.append((32, 193))
    cases = []
    for n, Q in parameters:
        result = measure(n, Q)
        cases.append(result)
        print(json.dumps({k: result[k] for k in
                          ('n', 'N', 'all_useful_scalar_gates', 'preparation_gates',
                           'representative_residual_gates', 'auxiliary_input_count')}), flush=True)
    assert before == hashes(), 'A source changed during measurement'
    report = {
        'status': 'passed', 'date': '2026-11-03', 'source_sha256': before,
        'seconds': round(time.monotonic()-started, 3), 'cases': cases,
        'selected_compiler': 'compile_native_representatives',
        'selected_output_roots': 'outputs: all slots of the actual INTT',
        'counting_model': 'distinct reachable +/* nodes; inputs, constants, wires are not arithmetic gates',
        'constants_are_structural_and_pre_evaluated': True,
        'reference_normalizers_used': False,
        'all_stage_counts_extracted_from_the_same_emitted_graph': True,
        'semantic_correctness_reference': 'documents/composition-native-2026-11-03/native-composition-validation.json',
        'scope': 'Exact measurements of the existing complete representative DAG; no measured total for an unimplemented normalized compact scalar DAG.',
        'general_polynomial_scalar_output_bound_proved': False,
    }
    (HERE/'same-dag-measurements.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': 'passed', 'cases': len(cases)}), flush=True)


if __name__ == '__main__':
    main()

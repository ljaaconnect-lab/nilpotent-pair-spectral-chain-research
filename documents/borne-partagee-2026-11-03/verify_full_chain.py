"""Check old direct-compiler witnesses after all h factors and the actual INTT.

Witness subsets belong only to this external verifier. The compiler is
imported intact, and witness inspection reads existing derivative-cache
entries without allocating nodes or cache entries.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
COMPILER = PROJECT / 'etudes/2026-11-01/raccord-initialisation/spectral/reprise-globale/shared_operator_dag.py'
OLD_PROOF = PROJECT / 'etudes/2026-11-01/borne-chaine-generale/si-direct/CROISSANCE_DAG_DIRECT.md'
NOTE = HERE / 'CROISSANCE_COMPILATEUR_COMPLET.md'
EXPECTED_COMPILER_SHA = 'a17cbcdae56dc3338ae46d42239d2a1a99e0b169865f16fc62f5c83b31cb3b06'
sys.path.insert(0, str(COMPILER.parent))
from shared_operator_dag import compile_chain  # noqa: E402


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hashes():
    paths = (COMPILER, OLD_PROOF, NOTE, Path(__file__))
    return {p.relative_to(PROJECT).as_posix(): sha256(p) for p in paths}


def restore_existing_initialization(dag, n):
    """Recover the original nodes through interning; no new evidence allowed."""
    before = len(dag.nodes)
    a = [[dag.variable(f'a_{i}_{j}') for j in range(n)] for i in range(n)]
    z = dag.variable('z')
    marks = [z]
    for _ in range(n * n - 1):
        marks.append(dag.mul(marks[-1], marks[-1]))
    B = [[dag.mul(dag.add(dag.one, dag.mul(a[i][j], a[i][j])), marks[i*n+j])
          for j in range(n)] for i in range(n)]
    s = [dag.variable(f's_{j}', j) for j in range(n)]
    root = dag.product(dag.sum(dag.mul(B[i][j], s[j]) for j in range(n))
                       for i in range(n))
    assert len(dag.nodes) == before
    return root, s


def existing_witnesses(dag, G, subsets):
    before = len(dag.nodes), len(dag.derivatives)
    roots = []
    for columns in subsets:
        root = G
        for j in columns:
            for _ in range(2):
                assert (root, j) in dag.derivatives, 'Witness must already be cached'
                root = dag.derivatives[root, j]
        roots.append(root)
    assert before == (len(dag.nodes), len(dag.derivatives))
    assert len(set(roots)) == len(subsets)
    assert all(dag.nodes[root][0] in ('+', '*') for root in roots)
    assert all(dag.degrees[root] == (0,) * dag.n for root in roots)
    for root in roots:
        assert all(not (dag.nodes[v][0] == 'v' and dag.nodes[v][1].startswith('s_'))
                   for v in dag.reachable([root]))
    return roots


def checkpoint(dag, roots, witnesses, name):
    reached = dag.reachable(roots)
    assert all(w in reached for w in witnesses), name
    gates = sum(dag.nodes[v][0] in ('+', '*') for v in reached)
    assert gates >= len(witnesses)
    return {'name': name, 'scalar_gates': gates,
            'witnesses_reachable': len(witnesses), 'output_roots': list(roots)}


def verify_case(n):
    started = time.monotonic()
    Q = 97
    N = 1
    while N <= n:
        N *= 2
    omega = pow(5, (Q - 1) // N, Q)
    labels = list(range(n))
    m, h = n // 2, n * (n - 1) // 2
    dag, outputs, stages = compile_chain(n, Q, omega, labels, budget=1_000_000)
    allocated_by_actual_compiler = len(dag.nodes)
    actual_cache_entries = len(dag.derivatives)
    assert dag.count(outputs) == {4: 4441, 6: 242471}[n]

    G, s = restore_existing_initialization(dag, n)
    subsets = list(itertools.combinations(range(n), m))
    assert len(subsets) == math.comb(n, m)
    witnesses = existing_witnesses(dag, G, subsets)

    # Replay only the calls already performed by compile_chain. All nodes
    # and all derivative-cache entries must already exist.
    root = G
    checkpoints = []
    for r in range(1, h + 1):
        root = dag.add(root, dag.mul(dag.constant(-pow(r, -1, Q)), dag.L(root, s)))
        assert len(dag.nodes) == allocated_by_actual_compiler
        assert len(dag.derivatives) == actual_cache_entries
        assert dag.count([root]) == stages[r]['active_scalar_gates']
        if r == m:
            checkpoints.append(checkpoint(dag, [root], witnesses, 'after_m_factors'))
    checkpoints.append(checkpoint(dag, [root], witnesses, 'after_all_h_factors'))

    spectra = []
    for f in range(N):
        replacements = {s[j]: dag.constant(pow(omega, f*labels[j], Q)) for j in range(n)}
        spectra.append(dag.substitute([root], replacements)[0])
        assert len(dag.nodes) == allocated_by_actual_compiler
        checkpoints.append(checkpoint(dag, [spectra[-1]], witnesses, f'after_phase_{f}'))
    reconstructed_outputs = dag.intt(spectra, omega)
    assert reconstructed_outputs == outputs
    assert len(dag.nodes) == allocated_by_actual_compiler
    assert len(dag.derivatives) == actual_cache_entries
    checkpoints.append(checkpoint(dag, outputs, witnesses, 'after_actual_intt_all_outputs'))

    # Semantic separation of the already existing witnesses on a,z inputs.
    assert (1 + 22**2) % Q == 0
    for index, selected in enumerate(subsets):
        inputs = {'z': 1}
        for i in range(n):
            chosen = selected[i // 2]
            inputs.update({f'a_{i}_{j}': 0 if j == chosen else 22 for j in range(n)})
        assert dag.evaluate(witnesses, inputs) == [pow(2, m, Q) if k == index else 0
                                                 for k in range(len(subsets))]
        assert dag.evaluate(outputs, inputs) == [0] * N
    bijective_inputs = {'z': 1} | {f'a_{i}_{j}': 0 if i == j else 22
                                  for i in range(n) for j in range(n)}
    expected = [0] * N
    expected[sum(labels) % N] = 1
    assert dag.evaluate(outputs, bijective_inputs) == expected
    assert len(dag.nodes) == allocated_by_actual_compiler
    assert len(dag.derivatives) == actual_cache_entries

    return {
        'n': n, 'm': m, 'h': h, 'Q': Q, 'N': N, 'omega': omega,
        'labels': labels, 'status': 'passed',
        'witness_roots': witnesses, 'witness_count': len(witnesses),
        'initial_scalar_gates': stages[0]['active_scalar_gates'],
        'final_scalar_gates': dag.count(outputs),
        'allocated_nodes_actual_compiler': allocated_by_actual_compiler,
        'derivative_cache_entries_actual_compiler': actual_cache_entries,
        'node_allocations_by_replay_and_witness_checks': 0,
        'derivative_cache_allocations_by_replay_and_witness_checks': 0,
        'semantic_separation_checks': len(subsets)**2,
        'repeated_column_zero_output_tables': len(subsets),
        'bijective_output_tables': 1, 'checkpoints': checkpoints,
        'seconds': round(time.monotonic() - started, 6),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    assert sha256(COMPILER) == EXPECTED_COMPILER_SHA
    before = source_hashes()
    cases = []
    for n in (4, 6):
        case = verify_case(n)
        cases.append(case)
        print(json.dumps({k: case[k] for k in ('n', 'status', 'final_scalar_gates',
                                              'witness_count', 'seconds')}), flush=True)
    assert before == source_hashes(), 'Source changed during validation'
    report = {
        'status': 'passed', 'source_sha256': before,
        'scope': 'Historical shared_operator_dag.compile_chain only; finite checks support a written general proof.',
        'general_claim': 'For n=2m>=4, the final shared scalar DAG has at least binomial(2m,m)>=2^m arithmetic gates.',
        'claim_includes': ['original a,z preparation', 'all h=binomial(n,2) factors',
                           'all phase substitutions', 'actual radix-2 INTT'],
        'general_scalar_circuit_lower_bound_claimed': False,
        'general_compiler_reachability_formalized_in_lean': False,
        'historical_compiler_modified': False,
        'witnesses_belong_only_to_verifier': True,
        'cases': cases,
    }
    if args.write_report:
        (HERE / 'full-chain-validation.json').write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'compiler_sha256': EXPECTED_COMPILER_SHA}), flush=True)


if __name__ == '__main__':
    main()

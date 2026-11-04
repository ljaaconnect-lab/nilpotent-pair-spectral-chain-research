"""Check reachable derivative witnesses in the existing direct scalar DAG.

The witnesses inspect existing nodes. They do not add subset states or
jets to the circuit, and the check asserts zero node allocation by each
query. The accompanying note supplies the general argument.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
COMPILER = (PROJECT / 'etudes/2026-11-01/raccord-initialisation/spectral/'
            'reprise-globale/shared_operator_dag.py')
FUSED_COMPILER = PROJECT / 'etudes/2026-11-01/fusion-double-log/fused_circuit.py'
sys.path.insert(0, str(COMPILER.parent))
from shared_operator_dag import DAG  # noqa: E402


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def collision_spectrum(n):
    """Constant-only recurrence on total size, as in the fused compiler."""
    spectra = [{0}]
    for degree in range(1, n + 1):
        spectra.append({previous + k * (k - 1) // 2
                        for k in range(1, degree + 1)
                        for previous in spectra[degree - k]})
    return sorted(spectra[n])


def verify_case(n, Q=97, midpoint_checkpoint=True):
    assert n >= 4 and n % 2 == 0
    m = n // 2
    h = n * (n - 1) // 2
    near = (n - 1) * (n - 2) // 2
    assert Q > max(2, h)
    factors = [r for r in collision_spectrum(n) if 0 < r < near]
    assert factors[:m] == list(range(1, m + 1))
    dag = DAG(n, Q, budget=3_000_000)
    a = [[dag.variable(f'a_{i}_{j}') for j in range(n)] for i in range(n)]
    z = dag.variable('z')
    marks = [z]
    for _ in range(n * n - 1):
        marks.append(dag.mul(marks[-1], marks[-1]))
    B = [[dag.mul(dag.add(dag.one, dag.mul(a[i][j], a[i][j])),
                  marks[i * n + j]) for j in range(n)] for i in range(n)]
    s = [dag.variable(f's_{j}', j) for j in range(n)]
    ell = [dag.sum(dag.mul(B[i][j], s[j]) for j in range(n))
           for i in range(n)]
    G = dag.product(ell)
    subsets = list(itertools.combinations(range(n), m))
    expected = math.comb(n, m)
    assert len(subsets) == expected

    def query_witnesses():
        previous = len(dag.nodes)
        witnesses = []
        for columns in subsets:
            target = G
            for j in columns:
                target = dag.derivative(dag.derivative(target, j), j)
            witnesses.append(target)
        allocated = len(dag.nodes) - previous
        assert allocated == 0, 'Witness query must not create its own evidence'
        assert len(set(witnesses)) == expected
        assert all(dag.nodes[x][0] in ('+', '*') for x in witnesses)
        assert all(dag.degrees[x] == (0,) * n for x in witnesses)
        return witnesses, allocated

    def checkpoint(root, label):
        reachable_before = dag.reachable([root])
        witnesses, allocated_before = query_witnesses()
        assert all(x in reachable_before for x in witnesses)
        assert all(not any(dag.nodes[y][0] == 'v'
                           and dag.nodes[y][1].startswith('s_')
                           for y in dag.reachable([x])) for x in witnesses)
        scalar_root = dag.substitute([root], {x: dag.one for x in s})[0]
        reachable_after = dag.reachable([scalar_root])
        same_witnesses, allocated_after = query_witnesses()
        assert same_witnesses == witnesses
        assert all(x in reachable_after for x in witnesses)
        return {
            'checkpoint': label,
            'scalar_gates_after_s_equals_one': dag.count([scalar_root]),
            'witnesses_expected': expected,
            'distinct_witness_roots': len(set(witnesses)),
            'reachable_before_substitution': sum(x in reachable_before for x in witnesses),
            'reachable_after_substitution': sum(x in reachable_after for x in witnesses),
            'query_allocations_before_substitution': allocated_before,
            'query_allocations_after_substitution': allocated_after,
            'witnesses_are_s_free_arithmetic_gates': True,
            'witness_root_ids': witnesses,
        }

    root = G
    for r in factors[:m]:
        root = dag.add(root, dag.mul(dag.constant(-pow(r, -1, Q)), dag.L(root, s)))
    first = checkpoint(root, 'first_m_factors') if midpoint_checkpoint else None
    for r in factors[m:]:
        root = dag.add(root, dag.mul(dag.constant(-pow(r, -1, Q)), dag.L(root, s)))
    full = checkpoint(root, 'full_I_prefix')
    assert full['scalar_gates_after_s_equals_one'] >= expected
    assert full['scalar_gates_after_s_equals_one'] == {4: 316, 6: 20278}[n]
    # Semantic separation on original inputs, independently of node IDs.
    # Over F_97, a=22 gives B=0 and a=0 gives B=1 when z=1.
    assert Q == 97 and (1 + 22**2) % Q == 0
    witness_roots, allocated = query_witnesses()
    assert allocated == 0
    for target_index, selected in enumerate(subsets):
        inputs = {'z': 1}
        for i in range(n):
            chosen_column = selected[i // 2]
            for j in range(n):
                inputs[f'a_{i}_{j}'] = 0 if j == chosen_column else 22
        values = dag.evaluate(witness_roots, inputs)
        assert values == [pow(2, m, Q) if j == target_index else 0
                          for j in range(expected)]
    return {
        'n': n, 'm': m, 'Q': Q, 'I': factors,
        'initialization': 'B_ij=(1+a_ij^2)*z^(2^(i*n+j)), formal a,z',
        'checkpoints': ([first] if first else []) + [full],
        'semantic_separator_inputs': expected,
        'semantic_separation_checks': expected**2,
        'pass': True,
    }


def main():
    cases = []
    for n in (4, 6):
        case = verify_case(n)
        fresh = verify_case(n, midpoint_checkpoint=False)
        final = case['checkpoints'][-1]
        fresh_final = fresh['checkpoints'][-1]
        assert final['scalar_gates_after_s_equals_one'] == fresh_final['scalar_gates_after_s_equals_one']
        assert final['distinct_witness_roots'] == fresh_final['distinct_witness_roots']
        case['fresh_without_intermediate_substitution'] = fresh_final
        cases.append(case)
    report = {
        'scope': 'Existing direct compiler only; finite structural checks, not a general-circuit lower bound',
        'general_claim': 'S_I^(1)(2m) >= binomial(2m,m) >= 2^m for m>=2',
        'proof_note': 'CROISSANCE_DAG_DIRECT.md',
        'compiler': str(COMPILER.relative_to(PROJECT)).replace('\\', '/'),
        'compiler_sha256': sha256(COMPILER),
        'fused_compiler_source': FUSED_COMPILER.relative_to(PROJECT).as_posix(),
        'fused_compiler_sha256': sha256(FUSED_COMPILER),
        'verifier_sha256': sha256(__file__),
        'proof_note_sha256': sha256(HERE / 'CROISSANCE_DAG_DIRECT.md'),
        'cases': cases,
        'pass': True,
        'lean_status': 'The general compiler reachability theorem is not formalized in Lean.',
    }
    destination = HERE / 'derivative-roots-validation.json'
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({
        'pass': report['pass'],
        'compiler_sha256': report['compiler_sha256'],
        'cases': [{'n': case['n'], 'witnesses': case['checkpoints'][0]['witnesses_expected'],
                   'full_prefix_gates': case['checkpoints'][-1]['scalar_gates_after_s_equals_one']}
                  for case in report['cases']],
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()

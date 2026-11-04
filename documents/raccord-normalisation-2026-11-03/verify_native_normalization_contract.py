"""Check the proposed normalization contract on the unchanged native DAG.

This is a verifier, not a coefficient compiler or a new architecture.
The reference coefficient n! (and its one-entry perturbation) follows
algebraically from the retained square-zero relations. No subset tables,
derivative operators or candidate R recurrence are used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import factorial
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
NATIVE = PROJECT/'documents/composition-native-2026-11-03'
sys.path.insert(0, str(NATIVE))
from compose_native_representatives import compile_native_representatives


def join_rows(left, right):
    if left is None:
        return right
    if right is None or left == right:
        return left
    return -1  # More than one data row; no row collection is materialized.


def verify(n, Q):
    N = 1 << n.bit_length()
    assert (Q-1) % N == 0 and Q > n
    omega = next(w for w in range(1, Q)
                 if pow(w, N, Q) == 1 and pow(w, N//2, Q) != 1)
    labels = list(range(n))
    built = compile_native_representatives(n, Q, N, omega, labels)
    dag, nodes = built['dag'], built['dag'].nodes
    degrees, owners = [], []
    for node in nodes:
        op = node[0]
        if op == 'c':
            degree, owner = (None if node[1] == 0 else 0), None
        elif op == 'v':
            name = node[1]
            degree = 1 if name.startswith('x_') else 0
            owner = int(name.split('_')[1]) if name.startswith('a_') else None
        else:
            left, right = node[1:]
            dl, dr = degrees[left], degrees[right]
            owner = join_rows(owners[left], owners[right])
            if op == '*':
                degree = None if dl is None or dr is None else dl+dr
            else:
                assert op == '+'
                if dl is None:
                    degree = dr
                elif dr is None:
                    degree = dl
                else:
                    assert dl == dr, (n, node, dl, dr)
                    degree = dl
        if degree == 0:
            assert owner != -1, (n, node, owner)
        degrees.append(degree)
        owners.append(owner)
    assert all(degrees[root] in (None, n) for root in built['outputs'])
    baseline = {f'a_{i}_{j}': 0 for i in range(n) for j in range(n)}
    baseline.update({'z': 1} | {f'x_{r}': 0 for r in range(N)})
    roots = list(range(len(nodes)))
    values = dag.evaluate(roots, baseline)
    outputs = [values[root] for root in built['outputs']]
    assert outputs == [0]*N
    assert dag.evaluate([root for row in built['B'] for root in row], baseline) == [1]*(n*n)
    target = sum(labels) % N
    coefficient = factorial(n) % Q
    assert coefficient != 0
    scalar_target = [coefficient if k == target else 0 for k in range(N)]
    assert scalar_target != outputs
    witness_count = 0
    if n >= 2:
        changed = []
        changed_coefficient = (factorial(n)+factorial(n-1)) % Q
        assert changed_coefficient != coefficient
        for row in range(n):
            data = dict(baseline)
            data[f'a_{row}_0'] = 1
            changed.append(dag.evaluate(roots, data))
        for index, (degree, owner) in enumerate(zip(degrees, owners)):
            if degree is None or degree > 0:
                assert values[index] == 0 != coefficient
            else:
                other = next(row for row in range(n) if row != owner)
                assert changed[other][index] == values[index]
                assert values[index] != coefficient or changed[other][index] != changed_coefficient
            witness_count += 1
        assert witness_count == len(nodes)
    return {
        'n': n, 'Q': Q, 'N': N, 'omega': omega, 'labels': labels,
        'inputs': 'all a_ij=0, z=1; x=0 only to test the universally quantified contract',
        'representative_outputs_at_zero_aux': outputs,
        'native_coefficients_in_Omega_label': scalar_target,
        'native_coefficient_derivation': '(sum_j q_j)^n = n! q_top in the existing quotient',
        'output_homogeneity_in_aux_degree': n,
        'every_zero_degree_wire_uses_at_most_one_data_row': True,
        'all_existing_wires_counterchecked_as_coefficients': n >= 2,
        'wire_selection_counterchecks': witness_count,
        'existing_native_representative_gates': dag.count(built['outputs']),
        'native_compiler_changed': False,
        'new_compiler_or_operator_introduced': False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    sources = [Path(__file__), NATIVE/'compose_native_representatives.py',
               PROJECT/'etudes/2026-11-01/linearisation-orientee-convolution/linearised_inputs.py',
               PROJECT/'etudes/2026-11-01/raccord-initialisation/spectral/reprise-globale/shared_operator_dag.py']
    hashes = {f.relative_to(PROJECT).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in sources}
    cases = [verify(n, Q) for n, Q in [(1, 3), (2, 5), (3, 5)]+[(n, 17) for n in range(4, 9)]]
    assert hashes == {name: hashlib.sha256((PROJECT/name).read_bytes()).hexdigest() for name in hashes}
    report = {
        'status': 'passed', 'source_sha256': hashes, 'cases': cases,
        'scope': 'Refutation of normalized on the unchanged representative outputs, plus finite checks excluding simple selection of any existing wire for n>=2. Not an impossibility theorem for a different scalar compilation.',
        'general_proof_is_separate_from_finite_checks': True,
        'polynomial_scalar_closure_proved': False,
        'no_general_circuit_lower_bound_claimed': True,
    }
    if args.write_report:
        (HERE/'native-normalization-witnesses.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': 'passed', 'cases': len(cases),
                      'wire_selection_counterchecks': sum(c['wire_selection_counterchecks'] for c in cases)}, indent=2))


if __name__ == '__main__':
    main()

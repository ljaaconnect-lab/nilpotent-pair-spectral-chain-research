"""Check spectral fusion without supplying a target to the input compiler.

All nilpotent and permutation calculations belong to this external verifier.
"""
import hashlib
import itertools
import json
from math import prod
from pathlib import Path
import random

from fused_linearised import compile_fused_linearised
from linearised_inputs import compile_linearised_inputs, DAG_FOLDER
from verify_linearised_inputs import (evaluate_nil, fourier_orientations,
                                     reference_scalar_formal, check_oriented_table,
                                     scale_dictionary)


def main():
    here = Path(__file__).resolve().parent
    project = here.parents[2]
    sources = [here/name for name in ('FUSION_LINEARISEE.md', 'fused_linearised.py',
               'verify_fused_linearised.py', 'linearised_inputs.py', 'verify_linearised_inputs.py')]
    sources += [DAG_FOLDER/'shared_operator_dag.py', DAG_FOLDER/'verify_shared_operator_dag.py']
    def hashes():
        return {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sources}
    initial = hashes()
    rng, Q, cases = random.Random(20261102), 97, []
    for n in range(1, 9):
        N = 1 << (n-1).bit_length()
        omega = next(w for w in range(1, Q) if pow(w, N, Q) == 1
                     and (N == 1 or pow(w, N//2, Q) != 1))
        labels = [rng.randrange(-N, 2*N) for _ in range(n)]
        dag, F0, C, info = compile_fused_linearised(n, Q, N, omega, labels)
        expanded_dag, expanded_F, expanded_C, expanded_info = compile_linearised_inputs(
            n, Q, N, omega, labels)
        x = fourier_orientations(n, N, omega, Q)
        numeric, formal = 0, 0
        for sample in range(3):
            a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
            if sample == 1:
                a[0] = [22]*n
            z = 0 if sample == 0 else rng.randrange(1, Q)
            inputs = {f'a_{i}_{j}': a[i][j] for i in range(n) for j in range(n)} | {'z': z}
            inputs.update({f'x_{r}': rng.randrange(Q) for r in range(N)})
            assert dag.evaluate([F0], inputs) == expanded_dag.evaluate([expanded_F[0]], inputs)
            coefficient_values = dag.evaluate([v for row in C for v in row], inputs)
            assert coefficient_values == expanded_dag.evaluate(
                [v for row in expanded_C for v in row[0]], inputs)
            B = [[(1+a[i][j]**2)*pow(z, 2**(i*n+j), Q) % Q
                  for j in range(n)] for i in range(n)]
            scalar = sum(prod(B[i][j] for i, j in enumerate(columns))
                         for columns in itertools.permutations(range(n))) % Q
            # External direct check of the new dual translation identity.
            directions = [[coefficient_values[i*N+(-s) % N] for s in range(N)] for i in range(n)]
            def dual_value(y):
                return prod(sum(pow(omega, s*j, Q)*y[s] for s in range(N)) % Q
                            for j in range(n)) % Q
            t = [rng.randrange(Q) for _ in range(n)]
            y = [sum(t[i]*directions[i][s] for i in range(n)) % Q for s in range(N)]
            assert dual_value(y) == prod(sum(t[i]*B[i][j] for i in range(n)) % Q
                                         for j in range(n)) % Q
            difference = 0
            for mask in range(1 << n):
                y = [sum(directions[i][s] for i in range(n) if mask & (1 << i)) % Q
                     for s in range(N)]
                difference += (-1)**(n-mask.bit_count())*dual_value(y)
            assert difference % Q == scalar
            base = evaluate_nil(dag, [F0], a, z, x)[0]
            phases = [scale_dictionary(base, pow(omega, f*sum(labels), Q), Q) for f in range(N)]
            # This equality is in the quotient. Ordinary F_f(x) need not equal phase*F0(x).
            assert phases == evaluate_nil(expanded_dag, expanded_F, a, z, x)
            check_oriented_table(phases, {0: scalar} if scalar else {}, n, N, omega, labels, Q)
            numeric += 1
            if n <= 4 and sample == 2:
                scalar_formal = reference_scalar_formal(a, Q)
                base_formal = evaluate_nil(dag, [F0], a, z, x, formal_z=True)[0]
                phases_formal = [scale_dictionary(base_formal, pow(omega, f*sum(labels), Q), Q)
                                 for f in range(N)]
                assert phases_formal == evaluate_nil(expanded_dag, expanded_F, a, z, x, formal_z=True)
                check_oriented_table(phases_formal, scalar_formal, n, N, omega, labels, Q)
                formal += 1
        # Re-indexing the external spectral output leaves the whole representative DAG unchanged.
        other, other_F0, _, other_info = compile_fused_linearised(n, Q, N, omega, [0]*n)
        assert other.nodes == dag.nodes and other_F0 == F0
        info.update({'status': 'passed', 'numeric_oriented_tables': numeric,
                     'formal_z_tables': formal,
                     'dual_translation_difference_checks': numeric,
                     'unfused_representative_scalar_gates': expanded_info['polynomial_representative_scalar_gates'],
                     'spectral_labels_do_not_change_dag': True})
        cases.append(info)
        print(json.dumps({key: info[key] for key in ('n', 'N', 'polynomial_representative_scalar_gates',
                         'representative_gate_bound', 'status')}), flush=True)
    assert initial == hashes()
    report = {'status': 'passed', 'source_sha256': initial, 'cases': cases,
              'scalar_preparation_bound_proved': True,
              'bound': '4*n^2-1+2*n*N*log2(N)+3*n*N-1 <= 18*n^3 for n<=N<2*n',
              'asymptotic_preparation_bound': 'O(n^2 log(n+1))',
              'complete_scalar_Z_compiled': False,
              'general_polynomial_quotient_reader_established': False,
              'reference_uses_subset_and_permutation_tables': True,
              'compiler_uses_subset_tables': False}
    (here/'fused-linearised-validation.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': 'passed', 'numeric_tables': sum(c['numeric_oriented_tables'] for c in cases),
                      'formal_z_tables': sum(c['formal_z_tables'] for c in cases),
                      'translation_difference_checks': sum(c['dual_translation_difference_checks'] for c in cases)}))


if __name__ == '__main__':
    main()

"""Independent exact checks of the compiled projection, without jets."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import time

from direct_projection import compile_projected, DAG_FOLDER
from verify_shared_operator_dag import evaluate_formal_z, polynomial_add


def reference_stage(B, s, processed, Q):
    """Small-case enumeration used only by the verifier, not the compiler."""
    n = len(B)
    result = 0
    for rows in itertools.permutations(range(n), processed):
        used = set(rows)
        term = 1
        for j, i in enumerate(rows):
            term = term * B[i][j] % Q
        for i in range(n):
            if i not in used:
                term = term * sum(B[i][j] * s[j] for j in range(processed, n)) % Q
        result = (result + term) % Q
    return result


def spectrum(n):
    values = [{0}]
    for degree in range(1, n + 1):
        values.append({c + k*(k-1)//2 for k in range(1, degree+1)
                       for c in values[degree-k]})
    return values[n]


def check_prefix_reconstruction(B, s, scalar, Q):
    """Check c(L)G=scalar*prod(s)+a*near+b*pure at arbitrary s."""
    n = len(B)
    near = (n-1)*(n-2)//2
    pure = n*(n-1)//2
    factors = sorted(spectrum(n) - {0, near, pure})

    def weight(collision):
        value = 1
        for r in factors:
            value = value * (1 - collision * pow(r, -1, Q)) % Q
        return value

    direct = 0
    for columns in itertools.product(range(n), repeat=n):
        occupation = [0] * n
        term = 1
        for i, j in enumerate(columns):
            occupation[j] += 1
            term = term * B[i][j] * s[j] % Q
        collision = sum(k*(k-1)//2 for k in occupation)
        direct = (direct + term * weight(collision)) % Q
    pure_value, near_value = 0, 0
    for j in range(n):
        column = 1
        for i in range(n):
            column = column * B[i][j] % Q
        pure_value = (pure_value + column * pow(s[j], n, Q)) % Q
        for omitted in range(n):
            term = pow(s[j], n-1, Q)
            for i in range(n):
                if i != omitted:
                    term = term * B[i][j] % Q
            term = term * sum(B[omitted][k]*s[k] for k in range(n) if k != j) % Q
            near_value = (near_value + term) % Q
    projected = scalar
    for value in s:
        projected = projected * value % Q
    reconstructed = (projected + weight(near)*near_value + weight(pure)*pure_value) % Q
    assert reconstructed == direct, (n, reconstructed, direct)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-n', type=int, default=7)
    parser.add_argument('--node-budget', type=int, default=1_000_000)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    root = folder.parents[2]
    sources = [folder/'direct_projection.py', folder/'verify_direct_projection.py',
               DAG_FOLDER/'shared_operator_dag.py', DAG_FOLDER/'verify_shared_operator_dag.py']
    hashes = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sources}
    expected_counts = {1: 3, 2: 18, 3: 49, 4: 110, 5: 223, 6: 472, 7: 1013}
    rng = random.Random(20261101)
    cases = []
    for n in range(1, args.max_n + 1):
        started = time.monotonic()
        Q, N = 97, 1 << n.bit_length()
        labels = [(j*j+2*j+1) % N for j in range(n)]
        dag, outputs, stages = compile_projected(n, Q, N, labels, args.node_budget)
        count = dag.count(outputs)
        if n in expected_counts:
            assert count == expected_counts[n], (n, count)
        numeric_tables = intermediate_checks = formal_tables = prefix_checks = 0
        for sample in range(4):
            a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
            if sample == 1:
                a[0] = [22] * n  # 1+22^2=0 modulo 97.
            z = 0 if sample == 0 else rng.randrange(1, Q)
            s = [rng.randrange(Q) for _ in range(n)]
            B = [[(1+a[i][j]**2)*pow(z, 2**(i*n+j), Q) % Q
                  for j in range(n)] for i in range(n)]
            inputs = {f'a_{i}_{j}': a[i][j] for i in range(n) for j in range(n)} | {'z': z}
            values = inputs | {f's_{j}': s[j] for j in range(n)}
            for stage in stages:
                expected = reference_stage(B, s, stage['processed_columns'], Q)
                assert dag.evaluate([stage['root']], values)[0] == expected, (n, sample, stage)
                intermediate_checks += 1
            expected_table = [0] * N
            expected_table[sum(labels) % N] = reference_stage(B, s, n, Q)
            actual = dag.evaluate(outputs, inputs)
            assert actual == expected_table, (n, sample)
            numeric_tables += 1
            if 3 <= n <= 5 and sample >= 2:
                check_prefix_reconstruction(B, s, actual[sum(labels) % N], Q)
                prefix_checks += 1
            if n <= 3 and sample >= 2:
                expected_formal = [{} for _ in range(N)]
                for columns in itertools.permutations(range(n)):
                    coefficient, exponent = 1, 0
                    for i, j in enumerate(columns):
                        coefficient = coefficient * (1+a[i][j]**2) % Q
                        exponent += 2**(i*n+j)
                    k = sum(labels[j] for j in columns) % N
                    expected_formal[k] = polynomial_add(
                        expected_formal[k], {exponent: coefficient}, Q)
                assert evaluate_formal_z(dag, outputs, a) == expected_formal, (n, sample, 'formal_z')
                formal_tables += 1
        case = {
            'n': n, 'Q': Q, 'N': N, 'labels': labels, 'status': 'passed',
            'numeric_tables': numeric_tables,
            'intermediate_stage_checks': intermediate_checks,
            'formal_z_tables': formal_tables,
            'prefix_reconstruction_checks': prefix_checks,
            'zero_z_test': True, 'zero_amplitude_row_test': True,
            'complete_chain_scalar_gates': count,
            'allocated_nodes': len(dag.nodes),
            'stages': stages, 'seconds': round(time.monotonic()-started, 3),
        }
        cases.append(case)
        print(json.dumps(case), flush=True)
    assert hashes == {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sources}
    report = {
        'status': 'passed', 'source_sha256': hashes, 'cases': cases,
        'numeric_tables': sum(c['numeric_tables'] for c in cases),
        'intermediate_stage_checks': sum(c['intermediate_stage_checks'] for c in cases),
        'formal_z_tables': sum(c['formal_z_tables'] for c in cases),
        'prefix_reconstruction_checks': sum(c['prefix_reconstruction_checks'] for c in cases),
        'general_polynomial_closure': False,
        'general_quasipolynomial_closure': False,
        'lean_formalization_of_this_compiler': False,
        'compiler_uses_jet_tables': False,
        'compiler_uses_subset_states': False,
        'compiler_runtime_arithmetic_gates': ['+', '*'],
        'contract': 'Same homogeneous oriented collision projector and fused spectral routing. Sequential first derivatives compiled into scalar gates, with immediate zero substitution. Data inputs a,z only.',
    }
    if args.write_report:
        (folder/'direct-projection-validation.json').write_text(
            json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('status', 'numeric_tables',
                                          'intermediate_stage_checks', 'formal_z_tables',
                                          'prefix_reconstruction_checks')}))


if __name__ == '__main__':
    main()

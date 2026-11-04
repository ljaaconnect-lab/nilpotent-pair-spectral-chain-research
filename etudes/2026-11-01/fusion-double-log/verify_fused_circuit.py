"""Validate complete fused outputs and every homogeneous log-coordinate stage."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import time

from fused_circuit import compile_fused, collision_spectrum, NodeBudgetExceeded, LOG_FOLDER
from verify_log_circuit import numeric_exp, evaluate_formal_z, polynomial_add
from shared_operator_dag import compile_chain


def reference_stages(a, z, s, Q, factors):
    n = len(a)
    terms = {(0, (0,)*n): 1}
    for i in range(n):
        next_terms = dict(terms)
        for (degree, occ), c in terms.items():
            for j in range(n):
                key = degree+1, tuple(occ[k]+int(j == k) for k in range(n))
                b = (1+a[i][j]**2)*pow(z, 2**(i*n+j), Q)*s[j] % Q
                next_terms[key] = (next_terms.get(key, 0)+c*b) % Q
        terms = {key: c for key, c in next_terms.items() if c}
    stages = []
    for stage in range(len(factors)+1):
        coeffs = [0]*(n+1)
        for (degree, occ), c in terms.items():
            collision = sum(k*(k-1)//2 for k in occ)
            for q in factors[:stage]:
                c = c*(1-collision*pow(q, -1, Q)) % Q
            coeffs[degree] = (coeffs[degree]+c) % Q
        stages.append(coeffs)
    return stages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-n', type=int, default=5)
    parser.add_argument('--node-budget', type=int, default=1_000_000)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    folder = Path(__file__).parent
    root = folder.parents[2]
    sources = [folder/'fused_circuit.py', folder/'verify_fused_circuit.py',
               LOG_FOLDER/'log_circuit.py', LOG_FOLDER/'verify_log_circuit.py',
               LOG_FOLDER.parent/'raccord-initialisation/spectral/reprise-globale/shared_operator_dag.py',
               LOG_FOLDER.parent/'raccord-initialisation/spectral/reprise-globale/verify_shared_operator_dag.py']
    hashes = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    cases = []
    rng = random.Random(20261109)
    for n in range(1, args.max_n+1):
        Q, N = 97, 1 << n.bit_length()
        factors = collision_spectrum(n)[1:]
        labels = [(j*j+2*j+1) % N for j in range(n)]
        samples = []
        for sample in range(8):
            a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
            if sample == 1:
                a[0] = [22]*n
            z = 0 if sample == 0 else rng.randrange(1, Q)
            s = [rng.randrange(Q) for _ in range(n)]
            inputs = {f'a_{i}_{j}': a[i][j] for i in range(n) for j in range(n)} | {'z': z}
            expected = [0]*N
            for js in itertools.permutations(range(n)):
                c = 1
                for i, j in enumerate(js):
                    c = c*(1+a[i][j]**2)*pow(z, 2**(i*n+j), Q) % Q
                k = sum(labels[j] for j in js) % N
                expected[k] = (expected[k]+c) % Q
            samples.append((a, z, s, inputs, expected, reference_stages(a, z, s, Q, factors)))
        for mode in ('direct', 'single', 'double'):
            started = time.monotonic()
            try:
                dag, outputs, coordinates, stages = compile_fused(n, Q, N, labels, mode, args.node_budget)
            except NodeBudgetExceeded:
                case = {'n': n, 'mode': mode, 'status': 'node_budget_exceeded', 'budget': args.node_budget}
                cases.append(case)
                print(json.dumps(case), flush=True)
                continue
            intermediate = 0
            uncompressed_gates = None
            unfused_gates = None
            if mode == 'direct':
                old_dag, old_outputs, _, _ = compile_fused(
                    n, Q, N, labels, mode, args.node_budget,
                    compress=False, terminal_correction=False)
                uncompressed_gates = old_dag.count(old_outputs)
                unfused_dag, unfused_outputs, _ = compile_chain(
                    n, Q, pow(5, (Q-1)//N, Q), labels, args.node_budget)
                unfused_gates = unfused_dag.count(unfused_outputs)
            for a, z, s, inputs, expected, reference in samples:
                assert dag.evaluate(outputs, inputs) == expected, (n, mode)
                if mode == 'direct':
                    assert old_dag.evaluate(old_outputs, inputs) == expected
                    assert unfused_dag.evaluate(unfused_outputs, inputs) == expected
                values = inputs | {f's_{j}': s[j] for j in range(n)}
                for r, roots in enumerate(coordinates):
                    actual = dag.evaluate(roots, values)
                    if mode == 'double':
                        actual = numeric_exp(actual, Q)
                        actual[0] = 0
                    actual = numeric_exp(actual, Q)
                    assert actual == reference[r], (n, mode, r, actual, reference[r])
                    intermediate += 1
            formal_tests = 0
            if n <= 3:
                a = samples[-1][0]
                actual = evaluate_formal_z(dag, outputs, a)
                expected = [{} for _ in range(N)]
                for js in itertools.permutations(range(n)):
                    c, exponent = 1, 0
                    for i, j in enumerate(js):
                        c = c*(1+a[i][j]**2) % Q
                        exponent += 2**(i*n+j)
                    k = sum(labels[j] for j in js) % N
                    expected[k] = polynomial_add(expected[k], {exponent: c}, Q)
                assert actual == expected, (n, mode, 'formal_z')
                formal_tests = 1
            case = {'n': n, 'mode': mode, 'Q': Q, 'N': N, 'labels': labels,
                    'projector_factors': factors,
                    'status': 'passed', 'tables': len(samples),
                    'intermediate_epsilon_jets': intermediate, 'formal_z_tables': formal_tests,
                    'complete_chain_scalar_gates': dag.count(outputs),
                    'uncompressed_direct_fused_gates': uncompressed_gates,
                    'original_unfused_direct_gates_same_parameters': unfused_gates,
                    'allocated_nodes': len(dag.nodes), 'stages': stages,
                    'seconds': time.monotonic()-started}
            cases.append(case)
            print(json.dumps(case), flush=True)
    assert hashes == {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    report = {'status': 'passed' if all(c['status'] == 'passed' for c in cases) else 'partial_budget_limit',
              'source_sha256': hashes, 'cases': cases,
              'general_polynomial_closure': False, 'general_quasipolynomial_closure': False,
              'contract': 'Same oriented collision projector. Homogeneous normalized log and double-log coordinates; exact fusion of all spectral phases and INTT into routing. Only a,z data leaves and scalar +,* runtime gates.'}
    if args.write_report:
        (folder/'fusion-validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'cases': len(cases)}))


if __name__ == '__main__':
    main()

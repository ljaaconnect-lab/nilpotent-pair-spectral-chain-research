"""Independent finite-field and formal-z checks of the logarithmic compiler."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import time

from log_circuit import compile_log_chain, NodeBudgetExceeded, SHARED
from shared_operator_dag import compile_chain
from verify_shared_operator_dag import evaluate_formal_z, polynomial_add


def numeric_exp(u, Q):
    result = [1]
    for k in range(1, len(u)):
        result.append(sum(j*u[j]*result[k-j] for j in range(1, k+1))
                      * pow(k, -1, Q) % Q)
    return result


def reference_stages(a, z, s, Q):
    """Expand only inside the verifier; filter each occupation eigenvalue."""
    n = len(a)
    source = {(0, (0,)*n): 1}
    for i in range(n):
        following = {}
        for (degree, occ), c in source.items():
            following[degree, occ] = (following.get((degree, occ), 0)+c) % Q
            following[degree+1, occ] = (following.get((degree+1, occ), 0)-c) % Q
            for j in range(n):
                key = degree+1, tuple(occ[k]+int(k == j) for k in range(n))
                b = (1+a[i][j]**2)*pow(z, 2**(i*n+j), Q)*s[j] % Q
                following[key] = (following.get(key, 0)+c*b) % Q
        source = {key: c for key, c in following.items() if c}
    result = []
    for r in range(n*(n-1)//2+1):
        coeffs = [0]*(n+1)
        for (degree, occ), c in source.items():
            collision = sum(v*(v-1)//2 for v in occ)
            weight = 1
            for k in range(1, r+1):
                weight = weight*(1-collision*pow(k, -1, Q)) % Q
            coeffs[degree] = (coeffs[degree]+weight*c) % Q
        result.append(coeffs)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-n', type=int, default=5)
    parser.add_argument('--node-budget', type=int, default=1_000_000)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    folder = Path(__file__).parent
    sources = [folder/'log_circuit.py', folder/'verify_log_circuit.py',
               SHARED/'shared_operator_dag.py', SHARED/'verify_shared_operator_dag.py']
    hashes = {str(p.relative_to(folder.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sources}
    rng = random.Random(20261107)
    cases = []
    for n in range(1, args.max_n+1):
        Q, N = 97, 1 << n.bit_length()
        omega = pow(5, (Q-1)//N, Q)
        ds = list(range(n))
        started = time.monotonic()
        try:
            dag, outputs, stage_roots, stages = compile_log_chain(n, Q, omega, ds, args.node_budget)
        except NodeBudgetExceeded:
            case = {'n': n, 'status': 'node_budget_exceeded', 'budget': args.node_budget}
            cases.append(case)
            print(json.dumps(case), flush=True)
            break
        direct_dag, direct_outputs, _ = compile_chain(n, Q, omega, ds, args.node_budget)
        direct_count = direct_dag.count(direct_outputs)
        unpruned_dag, unpruned_outputs, _, _ = compile_log_chain(
            n, Q, omega, ds, args.node_budget, prune=False)
        unpruned_count = unpruned_dag.count(unpruned_outputs)
        tables = intermediate = formal = 0
        for sample in range(8):
            a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
            z = 0 if sample == 0 else rng.randrange(1, Q)
            # A zero amplitude row: 22^2 = -1 mod 97.
            if sample == 1:
                a[0] = [22]*n
            inputs = {f'a_{i}_{j}': a[i][j] for i in range(n) for j in range(n)} | {'z': z}
            actual = dag.evaluate(outputs, inputs)
            expected = [0]*N
            for js in itertools.permutations(range(n)):
                c = 1
                for i, j in enumerate(js):
                    c = c*(1+a[i][j]**2)*pow(z, 2**(i*n+j), Q) % Q
                k = sum(ds[j] for j in js) % N
                expected[k] = (expected[k]+c) % Q
            assert actual == expected, (n, sample, actual, expected)
            assert direct_dag.evaluate(direct_outputs, inputs) == actual
            assert unpruned_dag.evaluate(unpruned_outputs, inputs) == actual
            tables += 1
            s = [rng.randrange(Q) for _ in range(n)]
            values = inputs | {f's_{j}': s[j] for j in range(n)}
            references = reference_stages(a, z, s, Q)
            for r, roots in enumerate(stage_roots):
                reconstructed = numeric_exp(dag.evaluate(roots, values), Q)
                assert reconstructed == references[r], (n, sample, r, reconstructed, references[r])
                intermediate += 1
        if n <= 3:
            a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
            actual = evaluate_formal_z(dag, outputs, a)
            expected = [{} for _ in range(N)]
            for js in itertools.permutations(range(n)):
                c, exponent = 1, 0
                for i, j in enumerate(js):
                    c = c*(1+a[i][j]**2) % Q
                    exponent += 2**(i*n+j)
                k = sum(ds[j] for j in js) % N
                expected[k] = polynomial_add(expected[k], {exponent: c}, Q)
            assert actual == expected, (n, actual, expected)
            formal += 1
        case = {'n': n, 'Q': Q, 'N': N, 'status': 'passed', 'tables': tables,
                'intermediate_epsilon_jets': intermediate, 'formal_z_tables': formal,
                'direct_chain_scalar_gates_same_parameters': direct_count,
                'unpruned_log_chain_scalar_gates_same_parameters': unpruned_count,
                'complete_chain_scalar_gates': dag.count(outputs), 'stages': stages,
                'allocated_nodes': len(dag.nodes), 'seconds': time.monotonic()-started}
        cases.append(case)
        print(json.dumps(case), flush=True)
    assert hashes == {str(p.relative_to(folder.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sources}
    report = {'status': 'passed' if all(c['status'] == 'passed' for c in cases) else 'partial_budget_limit',
              'general_polynomial_closure': False, 'general_quasipolynomial_closure': False,
              'source_sha256': hashes, 'cases': cases,
              'contract': 'Formal epsilon log/exp compiled to scalar gates. Existing I-L/r factors and INTT; only a,z are data leaves. No numerical logarithm, data inverse, moment or amplitude oracle.'}
    if args.write_report:
        (folder/'log-circuit-validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'cases': len(cases)}), flush=True)


if __name__ == '__main__':
    main()

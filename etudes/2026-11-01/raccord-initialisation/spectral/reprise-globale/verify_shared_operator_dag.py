"""Verify the compiled shared DAG; no polynomial-size claim."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import time

from shared_operator_dag import compile_chain, NodeBudgetExceeded


def polynomial_add(a, b, Q):
    result = dict(a)
    for exponent, coefficient in b.items():
        value = (result.get(exponent, 0) + coefficient) % Q
        if value:
            result[exponent] = value
        else:
            result.pop(exponent, None)
    return result


def polynomial_mul(a, b, Q):
    result = {}
    for x, u in a.items():
        for y, v in b.items():
            result[x+y] = (result.get(x+y, 0) + u*v) % Q
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def evaluate_formal_z(dag, roots, a):
    values = {}
    for idx in sorted(dag.reachable(roots)):
        node = dag.nodes[idx]
        if node[0] == 'c':
            values[idx] = {0: node[1]} if node[1] else {}
        elif node[0] == 'v':
            if node[1] == 'z':
                values[idx] = {1: 1}
            else:
                _, i, j = node[1].split('_')
                coefficient = a[int(i)][int(j)] % dag.Q
                values[idx] = {0: coefficient} if coefficient else {}
        elif node[0] == '+':
            values[idx] = polynomial_add(values[node[1]], values[node[2]], dag.Q)
        else:
            values[idx] = polynomial_mul(values[node[1]], values[node[2]], dag.Q)
    return [values[root] for root in roots]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    parser.add_argument('--max-n', type=int, default=6)
    parser.add_argument('--node-budget', type=int, default=1_000_000)
    args = parser.parse_args()
    folder = Path(__file__).parent
    sources = [folder / name for name in ('shared_operator_dag.py', 'verify_shared_operator_dag.py')]
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    rng = random.Random(20261103)
    cases = []
    for n in range(1, args.max_n+1):
        Q = 97
        N = 1
        while N <= n:
            N *= 2
        omega = pow(5, (Q-1)//N, Q)
        ds = list(range(n))
        started = time.monotonic()
        try:
            dag, roots, stages = compile_chain(n, Q, omega, ds, args.node_budget)
        except NodeBudgetExceeded as error:
            case = {'n': n, 'status': 'node_budget_exceeded', 'budget': args.node_budget, 'seconds': time.monotonic()-started}
            cases.append(case)
            print(json.dumps(case), flush=True)
            break
        tests = 0
        for _ in range(8):
            a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
            z = rng.randrange(1, Q)
            inputs = {f'a_{i}_{j}': a[i][j] for i in range(n) for j in range(n)} | {'z': z}
            actual = dag.evaluate(roots, inputs)
            expected = [0] * N
            for js in itertools.product(range(n), repeat=n):
                if len(set(js)) != n:
                    continue
                c = 1
                for i, j in enumerate(js):
                    c = c*(1+a[i][j]**2)*pow(z, 2**(i*n+j), Q) % Q
                k = sum(ds[j] for j in js) % N
                expected[k] = (expected[k]+c) % Q
            assert actual == expected, (n, actual, expected)
            tests += 1
        formal_tests = 0
        if n <= 4:
            for _ in range(2):
                a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
                actual = evaluate_formal_z(dag, roots, a)
                expected = [{} for _ in range(N)]
                for js in itertools.permutations(range(n)):
                    coefficient = 1
                    exponent = 0
                    for i, j in enumerate(js):
                        coefficient = coefficient*(1+a[i][j]**2) % Q
                        exponent += 2**(i*n+j)
                    k = sum(ds[j] for j in js) % N
                    expected[k] = polynomial_add(expected[k], {exponent: coefficient}, Q)
                assert actual == expected, (n, actual, expected)
                formal_tests += 1
        case = {'n': n, 'Q': Q, 'N': N, 'status': 'passed', 'tables': tests, 'formal_z_tables': formal_tests, 'stages': stages, 'complete_chain_scalar_gates': dag.count(roots), 'allocated_nodes': len(dag.nodes), 'derivative_cache_entries': len(dag.derivatives), 'seconds': time.monotonic()-started}
        cases.append(case)
        print(json.dumps(case), flush=True)
    assert hashes == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    report = {
        'status': 'passed' if all(c['status'] == 'passed' for c in cases) else 'partial_budget_limit',
        'source_sha256': hashes,
        'contract': 'Existing G_B and factors I-L/r only. Compile-time shared symbolic differentiation; every reachable runtime gate is ordinary scalar + or *. Inputs are a,z and supplied admissible field parameters. No moment or terminal amplitude oracle. No general polynomial-size bound established.',
        'general_polynomial_closure': False,
        'cases': cases,
    }
    if args.write_report:
        (folder/'shared-operator-dag-validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'source_sha256': hashes}), flush=True)


if __name__ == '__main__':
    main()

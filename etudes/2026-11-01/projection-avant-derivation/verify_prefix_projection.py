"""Independent checks of the reconstructed prefix and its quadratic overhead."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random

from prefix_projection import compile_prefix
from direct_projection import DAG_FOLDER
from verify_shared_operator_dag import evaluate_formal_z, polynomial_add


def reference(a, z, Q, factors):
    n = len(a)
    formal = {}
    for columns in itertools.product(range(n), repeat=n):
        occupation = [columns.count(j) for j in range(n)]
        collision = sum(k*(k-1)//2 for k in occupation)
        coefficient, exponent = 1, 0
        for r in factors:
            coefficient = coefficient * (1 - collision * pow(r, -1, Q)) % Q
        for i, j in enumerate(columns):
            coefficient = coefficient * (1+a[i][j]**2) % Q
            exponent += 2**(i*n+j)
        formal = polynomial_add(formal, {exponent: coefficient}, Q)
    value = sum(c * pow(z, k, Q) for k, c in formal.items()) % Q
    return value, formal


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    root = here.parents[2]
    sources = [here/'prefix_projection.py', here/'verify_prefix_projection.py',
               here/'direct_projection.py', DAG_FOLDER/'shared_operator_dag.py',
               DAG_FOLDER/'verify_shared_operator_dag.py']
    hashes = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sources}
    rng = random.Random(27112026)
    cases = []
    for n in range(3, 8):
        Q, N = 97, 1 << n.bit_length()
        labels = [(j*j+2*j+1) % N for j in range(n)]
        dag, x, outputs, info = compile_prefix(n, Q, N, labels)
        assert all(dag.nodes[i][0] != 'v' or not dag.nodes[i][1].startswith('s_')
                   for i in dag.reachable([x]))
        tables = formal_tables = 0
        if n <= 6:
            for sample in range(4):
                a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
                if sample == 1:
                    a[0] = [22] * n
                z = 0 if sample == 0 else rng.randrange(1, Q)
                inputs = {f'a_{i}_{j}': a[i][j] for i in range(n) for j in range(n)} | {'z': z}
                expected, formal = reference(a, z, Q, info['factors'])
                assert dag.evaluate([x], inputs)[0] == expected, (n, sample)
                tables += 1
                if n == 3 and sample >= 2:
                    assert evaluate_formal_z(dag, [x], a) == [formal]
                    formal_tables += 1
        info.update(status='passed', numeric_tables=tables, formal_z_tables=formal_tables)
        cases.append(info)
        print(json.dumps(info))
    assert hashes == {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sources}
    report = {
        'status': 'passed', 'source_sha256': hashes, 'cases': cases,
        'numeric_tables': sum(c['numeric_tables'] for c in cases),
        'formal_z_tables': sum(c['formal_z_tables'] for c in cases),
        'contract': 'Recompiled c(L)G_B(1) from a,z; quadratic tail overhead above projected output.',
        'polynomial_overhead': '5*n*n-4*n+2',
        'general_polynomial_prefix_bound': False,
        'general_polynomial_chain_bound': False,
    }
    if args.write_report:
        (here/'prefix-projection-validation.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('status', 'numeric_tables', 'formal_z_tables')}))


if __name__ == '__main__':
    main()

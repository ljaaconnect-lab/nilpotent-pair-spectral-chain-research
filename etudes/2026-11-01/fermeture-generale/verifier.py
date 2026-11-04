"""Independent checks of the full-insertion scalar compiler, including n > 5."""
from pathlib import Path
from itertools import permutations
from math import prod
import argparse,hashlib,json,random,sys
from circuit import build

HERE = Path(__file__).resolve().parent


def target(raw, labels, q):
    n = len(raw)
    p = [[1+x*x for x in row] for row in raw]
    out = [{} for _ in range(1 << n.bit_length())]
    row = out[sum(labels) % len(out)]
    for sigma in permutations(range(n)):
        exponent = sum(1 << (i*n+j) for i,j in enumerate(sigma))
        row[exponent] = prod(p[i][j] for i,j in enumerate(sigma)) % q
    return [{e:c for e,c in row.items() if c} for row in out]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    rng = random.Random(2026110104)
    q = 998244353
    costs, numeric, formal = [], 0, 0
    for n in range(1, 9):
        labels = [rng.randrange(16) for _ in range(n)]
        dag, outs, meta = build(n, labels, q)
        costs.append(meta)
        for case in range(2):
            raw = [[rng.randrange(-3, 4) for _ in range(n)] for _ in range(n)]
            data = {('a',i,j):raw[i][j] for i in range(n) for j in range(n)}
            data['z'] = rng.randrange(0, 12)
            wanted = target(raw, labels, q)
            want_numeric = [sum(c*pow(data['z'],e,q) for e,c in row.items()) % q for row in wanted]
            assert dag.evaluate_all(outs, data, q) == want_numeric, (n,case)
            numeric += 1
            if n <= 5 and case == 0:
                assert dag.evaluate_polynomials(outs, data, q) == wanted
                formal += 1
        assert all(arg == 'z' or (isinstance(arg, tuple) and arg[0] == 'a')
                   for op,*xs in dag.nodes if op == 'input' for arg in xs)
        print(json.dumps(meta), file=sys.stderr, flush=True)
    project = HERE.parents[2]
    dependencies = [HERE/x for x in ('circuit.py','insertion_circuit.py','verifier.py')]
    dependencies += [HERE.parent/'operateurs-horloge/circuit.py',
                     project/'etudes/2026-10-24/chaine-complete/reference/dag.py']
    report = {'date':'2026-11-01','status':'exact_insertion_compiler_verified',
              'general_polynomial_solution':False,'numeric_spectral_tables':numeric,
              'formal_z_spectral_tables':formal,'costs':costs,
              'code_sha256':{p.relative_to(project).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in dependencies}}
    if args.write_report:
        (HERE/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == '__main__':main()

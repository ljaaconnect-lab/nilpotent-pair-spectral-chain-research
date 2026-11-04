"""Check the scalar jet compiler and the reduction of actual full Z circuits.

The complete-chain source compiler used in these finite tests is already
known to have exponential gate cost. No polynomial solution is claimed.
"""
import argparse
from fractions import Fraction
import hashlib
import importlib.util
from itertools import permutations
import json
from math import prod
from pathlib import Path
import random
import sys
import time

from jet_compiler import DAG, Jets, PROJECT, gate_cost, lift_dag, reduce_chain

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent/'fermeture-generale'
sys.path.insert(0, str(SOURCE))
spec = importlib.util.spec_from_file_location('readout_complete_chain', SOURCE/'circuit.py')
chain = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = chain
spec.loader.exec_module(chain)


def pair_add(a, b, q):
    return ((a[0]+b[0]) % q, (a[1]+b[1]) % q)


def pair_mul(a, b, q):
    return ((a[0]*b[0]-a[1]*b[1]) % q, (a[0]*b[1]+a[1]*b[0]) % q)


def poly_add(a, b, q):
    out = dict(a)
    for k, c in b.items():
        out[k] = pair_add(out.get(k, (0, 0)), c, q)
    return {k: c for k, c in out.items() if c != (0, 0)}


def poly_mul(a, b, q):
    out = {}
    for r, x in a.items():
        for s, y in b.items():
            out[r+s] = pair_add(out.get(r+s, (0, 0)), pair_mul(x, y, q), q)
    return {k: c for k, c in out.items() if c != (0, 0)}


def full_polynomial_evaluate(source, outputs, inputs, q):
    """Independent untruncated evaluation, with sparse coefficient maps."""
    values = []
    for op, *args in source.nodes:
        if op == 'input':
            value = inputs[args[0]]
        elif op == 'const':
            c = args[0].numerator*pow(args[0].denominator, -1, q) % q
            value = {0: (c, 0)}
        elif op == 'add':
            value = poly_add(values[args[0]], values[args[1]], q)
        elif op == 'mul':
            value = poly_mul(values[args[0]], values[args[1]], q)
        values.append(value)
    return [values[o] for o in outputs]


def verify_random_dag(rng, q, degree):
    source = DAG()
    xs = [source.inp(j) for j in range(3)]
    degree_bounds = [2]*3
    pool = xs[:]
    for _ in range(30):
        a, b = rng.choice(pool), rng.choice(pool)
        multiply = rng.randrange(2) and degree_bounds[a]+degree_bounds[b] <= 10
        node = source.mul(a, b) if multiply else source.add(a, b)
        degree_bounds.append(degree_bounds[a]+degree_bounds[b] if multiply else
                             max(degree_bounds[a], degree_bounds[b]))
        pool.append(node)
    outputs = pool[-4:]
    target = DAG()
    algebra = Jets(target, degree)
    data, numerical = {}, {}
    for name in range(3):
        coefficients = [(rng.randrange(q), rng.randrange(q)) for _ in range(3)]
        data[name] = {k: c for k, c in enumerate(coefficients)}
        numerical[name] = [(algebra.const(c[0]), algebra.const(c[1])) for c in coefficients]
        numerical[name] = (numerical[name]+[(algebra.zero, algebra.zero)]*(degree+1))[:degree+1]
    result = lift_dag(source, outputs, algebra, numerical)
    counts = {op: sum(node[0] == op for node in source.nodes) for op in ('add', 'mul')}
    assert target.gates == gate_cost(degree, counts['add'], counts['mul'])
    flat = [node for jet in result for pair in jet for node in pair]
    actual = target.evaluate_all(flat, {}, q)
    expected = full_polynomial_evaluate(source, outputs, data, q)
    wanted = [c for poly in expected for k in range(degree+1) for c in poly.get(k, (0, 0))]
    assert actual == wanted, (q, degree)


def permanent_oracle(x, q):
    return sum(prod(x[i][j] for i, j in enumerate(sigma))
               for sigma in permutations(range(len(x)))) % q


def verify_chain(rng, n, q, generator):
    labels = [rng.randrange(2*n+1) for _ in range(n)]
    source, outputs, _ = chain.build(n, labels, q, generator)
    target, jets, costs = reduce_chain(source, outputs, n)
    slot = sum(labels) % len(jets)
    output_nodes = [node for jet in jets for pair in jet for node in pair]
    for _ in range(3):
        x = [[rng.randrange(q) for _ in range(n)] for _ in range(n)]
        actual = target.evaluate_all(output_nodes,
            {('x', i, j): x[i][j] for i in range(n) for j in range(n)}, q)
        wanted = [0]*len(actual)
        wanted[2*(slot*(n+1)+n)] = permanent_oracle(x, q)
        assert actual == wanted, (n, q, labels)
    costs.update({'Q': q, 'labels': labels, 'target_slot': slot, 'tables_checked': 3})
    return costs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    start = time.monotonic()
    dependencies = [HERE/'jet_compiler.py', HERE/'verify_jets.py',
        SOURCE/'circuit.py', SOURCE/'insertion_circuit.py',
        HERE.parent/'operateurs-horloge/circuit.py',
        PROJECT/'etudes/2026-10-24/chaine-complete/reference/dag.py']
    hashes = {p.relative_to(PROJECT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in dependencies}
    rng = random.Random(2026110111)
    random_cases = 0
    for q in (3, 5, 17, 97):
        for degree in range(6):
            for _ in range(3):
                verify_random_dag(rng, q, degree)
                random_cases += 1
    costs = [verify_chain(rng, 1, 3, 2)]
    for q, generator in ((17, 3), (97, 5)):
        for n in range(1, 6):
            costs.append(verify_chain(rng, n, q, generator))
    assert all(hashlib.sha256((PROJECT/p).read_bytes()).hexdigest() == h
               for p, h in hashes.items())
    report = {'status': 'passed', 'generic_circuit_cases': random_cases,
        'full_chain_tables': sum(c['tables_checked'] for c in costs),
        'all_coefficients_through_order_n_checked': True,
        'all_imaginary_coordinates_checked_zero': True,
        'general_polynomial_solution': False,
        'source_compiler': 'Existing full-insertion compiler, with exponential gate bound',
        'scope': 'Polynomial overhead of a reduction, conditional on receiving a scalar source circuit',
        'costs': costs, 'source_sha256': hashes,
        'elapsed_seconds': round(time.monotonic()-start, 3)}
    if args.write_report:
        (HERE/'jet-validation.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

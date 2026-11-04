"""Check integer word identities and the complete oriented/spectral scalar DAG."""
from collections import defaultdict
from fractions import Fraction as F
from itertools import permutations, product
from math import prod
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import random
import sys

from circuit import build, counterterm
from derive_quintic import derive

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('free_word_reference', HERE.parent/'operateurs-horloge/sonder_jordan.py')
word = importlib.util.module_from_spec(spec)
spec.loader.exec_module(word)


class WordAlgebra:
    def zero(self): return {}
    def identity(self): return {(): F(1)}
    def add(self, *ps): return word.add(*ps)
    def mul(self, p, q): return word.mul(p, q)
    def scale(self, p, c): return word.scale(p, c)
    def sub(self, p, q): return word.add(p, word.scale(q, -1))


def word_recurrence(colors, order):
    a = WordAlgebra()
    xs = [{(j,): F(1)} for j in range(colors)]
    cs = {m: counterterm(m, xs, a) for m in (4, 5)}
    assert a.scale(cs[4], F(1, 24)) == word.correction4(colors)
    h = [a.identity()]
    s = [a.identity() for _ in xs]
    for r in range(1, order+1):
        ts = [a.add(a.mul(x, sj), a.mul(sj, x)) for x, sj in zip(xs, s)]
        rhs = a.add(*ts)
        for m, c in cs.items():
            if r >= m:
                numerator = prod(range(r-m+1, r))
                assert numerator % 3 == 0
                rhs = a.add(rhs, a.scale(a.add(a.mul(c, h[r-m]), a.mul(h[r-m], c)), numerator//3))
        h.append(rhs)
        s = [a.sub(rhs, a.scale(t, r)) for t in ts]
    return h


def target(p, labels, q):
    n = len(p)
    result = [{} for _ in range(1 << n.bit_length())]
    peak = result[sum(labels) % len(result)]
    for s in permutations(range(n)):
        e = sum(1 << (i*n+j) for i, j in enumerate(s))
        peak[e] = (peak.get(e, 0)+prod(p[i][j] for i, j in enumerate(s))) % q
    return [{e: c for e, c in row.items() if c} for row in result]


def numeric(table, z, q):
    return [sum(c*pow(z, e, q) for e, c in t.items()) % q for t in table]


def run(write_report):
    checks = 0
    for colors in range(1, 7):
        h = word_recurrence(colors, 5)
        for r in range(6):
            expected = {w: F(2**r) for w in permutations(range(colors), r)}
            assert h[r] == expected, (colors, r)
            checks += colors**r
    h6 = word_recurrence(6, 6)[6]
    repeated = [(w, c) for w, c in sorted(h6.items()) if len(set(w)) < 6 and sum(w) % 8 == 15 % 8]
    assert repeated

    rng = random.Random(2026110103)
    costs, formal_tables, numeric_tables = [], 0, 0
    for n in range(1, 6):
        # Exercise legal spectral roots, nontrivial labels, and the entire table.
        for q, generator in ((998244353, 3), (17, 3)):
            labels = [rng.randrange(8) for _ in range(n)]
            dag, outs, meta = build(n, labels, q, generator)
            costs.append(dict(meta, Q=q, labels=labels))
            for case in range(6):
                raw = [[rng.randrange(-4, 5) for _ in range(n)] for _ in range(n)]
                p = [[1+x*x for x in row] for row in raw]
                data = {('a', i, j): raw[i][j] for i in range(n) for j in range(n)}
                data['z'] = rng.randrange(0, 12)
                expected = target(p, labels, q)
                assert dag.evaluate_all(outs, data, q) == numeric(expected, data['z'], q)
                numeric_tables += 1
                if case == 0:
                    assert dag.evaluate_polynomials(outs, data, q) == expected
                    formal_tables += 1
            assert all(arg == 'z' or (isinstance(arg, tuple) and arg[0] == 'a')
                       for op, *args in dag.nodes if op == 'input' for arg in args)

    p = [[17,2,10,10,10],[2,17,2,17,2],[10,10,5,2,2],[5,10,2,5,2],[17,10,17,10,5]]
    q = 998244353
    dag, outs, meta = build(5, list(range(5)), q, from_a=False)
    data = {('p', i, j): p[i][j] for i in range(5) for j in range(5)}
    data['z'] = 2
    got = dag.evaluate_all(outs, data, q)
    wanted = numeric(target(p, list(range(5)), q), 2, q)
    assert got == wanted
    _, tower = derive(8)
    report = {
        'date': '2026-11-01', 'status': 'quintic_operator_verified',
        'general_polynomial_solution': False, 'exact_through_order': 5,
        'free_word_coefficients_checked': checks,
        'numeric_spectral_tables_correct': numeric_tables,
        'formal_z_spectral_tables_correct': formal_tables,
        'scalar_costs': costs,
        'previous_legal_counterexample_repaired': {'Q': q, 'z': 2, 'p': p, 'got': got, 'expected': wanted},
        'remaining_order6_witness': {'word': repeated[0][0], 'integer_coefficient_H6': str(repeated[0][1]),
                                      'required_coefficient': 0, 'spectral_slot': 15 % 8},
        'formal_tower_nonzero_patterns': {r: len(c) for r, c in tower.items()},
        'lean_scope': 'See lean-validation.json; matrix compiler tests are separate from Lean proofs.'}
    project = HERE.parents[2]
    dependencies = [HERE/x for x in ('circuit.py', 'derive_quintic.py', 'verifier.py', 'correcteurs.json')]
    dependencies += [HERE.parent/'operateurs-horloge'/x for x in ('circuit.py', 'sonder_jordan.py')]
    dependencies += [project/'etudes/2026-10-24/chaine-complete/reference/dag.py']
    report['code_sha256'] = {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in dependencies}
    if write_report:
        (HERE/'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report', action='store_true')
    run(parser.parse_args().write_report)

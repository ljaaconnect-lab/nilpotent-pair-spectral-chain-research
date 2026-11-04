"""Integer-normalized clock circuit with fourth- and fifth-order operators.

Exact through homogeneous degree five. This is not a general exact compiler.
All matrix entries are compiled into the existing ordinary scalar DAG.
"""
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('previous_clock', HERE.parent/'operateurs-horloge/circuit.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
Algebra, DAG = previous.Algebra, previous.mod.DAG
TABLES = json.loads((HERE/'correcteurs.json').read_text(encoding='utf-8'))['orders']


def contraction(pattern, xs, algebra):
    """Sum only repeated blocks; singleton positions use P = sum_j A_j."""
    repeated = [j for j in set(pattern) if pattern.count(j) > 1]
    p = algebra.add(*xs)
    result = algebra.zero()
    for labels in product(range(len(xs)), repeat=len(repeated)):
        chosen = dict(zip(repeated, labels))
        term = algebra.identity()
        for j in pattern:
            term = algebra.mul(term, xs[chosen[j]] if j in chosen else p)
        result = algebra.add(result, term)
    return result


def counterterm(order, xs, algebra):
    """C4=24 R4; C5=48 R5, with integer coefficient tables."""
    return algebra.add(*(algebra.scale(contraction(t['pattern'], xs, algebra), t['coefficient'])
                         for t in TABLES[str(order)]['terms']))


def build(n, labels, prime=998244353, generator=3, correct5=True, from_a=True):
    if n < 1 or len(labels) != n:
        raise ValueError('n >= 1 and exactly n labels required')
    N = 1 << n.bit_length()
    if prime % 2 != 1 or (prime-1) % N:
        raise ValueError('Need odd prime Q with N dividing Q-1')
    omega = pow(generator, (prime-1)//N, prime)
    if pow(omega, N, prime) != 1 or pow(omega, N//2, prime) == 1:
        raise ValueError('wrong root order')
    dag = DAG()
    a = Algebra(dag, n+1)
    if from_a:
        raw = [[dag.inp(('a', i, j)) for j in range(n)] for i in range(n)]
        p = [[a.plus(a.o, a.times(x, x)) for x in row] for row in raw]
    else:
        p = [[dag.inp(('p', i, j)) for j in range(n)] for i in range(n)]
    z = [dag.inp('z')]
    for _ in range(n*n-1):
        z.append(a.times(z[-1], z[-1]))
    b = [[a.times(p[i][j], z[i*n+j]) for j in range(n)] for i in range(n)]
    spectra = []
    for f in range(N):
        xs = []
        for j in range(n):
            x = a.zero()
            phase = a.c(pow(omega, f*labels[j], prime))
            for i in range(n):
                x[i+1][i] = a.times(b[i][j], phase)
            xs.append(x)
        correctors = {m: counterterm(m, xs, a) for m in (4, 5)
                      if n >= m and (m == 4 or correct5)}
        h = [a.identity()]
        s = [a.identity() for _ in xs]
        for r in range(1, n+1):
            ts = [a.add(a.mul(x, sj), a.mul(sj, x)) for x, sj in zip(xs, s)]
            rhs = a.add(*ts)
            for m, c in correctors.items():
                if r >= m:
                    g = (2 if m == 4 else 8) * comb(r-1, m-1)
                    rhs = a.add(rhs, a.scale(a.add(a.mul(c, h[r-m]), a.mul(h[r-m], c)), g))
            h.append(rhs)
            s = [a.sub(rhs, a.scale(t, r)) for t in ts]
        spectra.append(a.times(a.c(F(1, 2**n)), h[n][n][0]))

    def inverse(values):
        m = len(values)
        if m == 1:
            return values
        e, o = inverse(values[::2]), inverse(values[1::2])
        lo, hi = [], []
        for j in range(m//2):
            t = a.times(a.c(pow(omega, (-j*(N//m)) % N, prime)), o[j])
            lo.append(a.plus(e[j], t))
            hi.append(a.plus(e[j], a.times(a.c(-1), t)))
        return lo+hi

    outputs = [a.times(a.c(F(1, N)), x) for x in inverse(spectra)]
    return dag, outputs, {'n': n, 'N': N, 'gates': dag.gates,
                          'matrix_dimension': n+1, 'quintic_repair': correct5,
                          'integer_recurrence': True, 'exact_through_degree': 5 if correct5 else 4,
                          'general_validity': False}

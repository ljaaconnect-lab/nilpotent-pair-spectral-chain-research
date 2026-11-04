"""Exact full-insertion circuit for the complete oriented/spectral chain.

All operator actions are expanded into ordinary scalar gates. This compiler
does not have a proved polynomial gate bound; its current construction grows
rapidly. No operator action is counted as a unit-cost scalar gate.
"""
from fractions import Fraction as F
from pathlib import Path
from dataclasses import dataclass
import importlib.util
from insertion_circuit import OperatorDAG

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('previous_scalar_clock', HERE.parent/'operateurs-horloge/circuit.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)


@dataclass
class Band:
    degree: int
    values: list


class BandAlgebra:
    def __init__(self, dag, n):
        self.n, self.dag = n, dag
        self.scalar = previous.Algebra(dag, 1)
        self.zero = Band(-1, [])

    def identity(self): return Band(0, [self.scalar.o]*(self.n+1))

    def add(self, a, b):
        if a.degree < 0: return b
        if b.degree < 0: return a
        assert a.degree == b.degree
        return Band(a.degree, [self.scalar.plus(x, y) for x, y in zip(a.values, b.values)])

    def scale(self, a, c):
        if not c or a.degree < 0: return self.zero
        k = self.scalar.c(c)
        return Band(a.degree, [self.scalar.times(k, x) for x in a.values])

    def mul(self, a, b):
        if a.degree < 0 or b.degree < 0: return self.zero
        r = a.degree+b.degree
        if r > self.n: return self.zero
        return Band(r, [self.scalar.times(a.values[i+b.degree], b.values[i])
                        for i in range(self.n+1-r)])


def build(n, labels, prime=998244353, generator=3):
    if n < 1 or len(labels) != n: raise ValueError('n >= 1 and n labels required')
    N = 1 << n.bit_length()
    if prime % 2 != 1 or (prime-1) % N: raise ValueError('Need an odd prime with N | Q-1')
    omega = pow(generator, (prime-1)//N, prime)
    if pow(omega, N, prime) != 1 or pow(omega, N//2, prime) == 1:
        raise ValueError('wrong root order')
    operators = OperatorDAG(n, n)
    value = operators.one
    for j in range(n): value = operators.insert(j, value)
    dag = previous.mod.DAG()
    bands = BandAlgebra(dag, n)
    s = bands.scalar
    raw = [[dag.inp(('a', i, j)) for j in range(n)] for i in range(n)]
    p = [[s.plus(s.o, s.times(x, x)) for x in row] for row in raw]
    z = [dag.inp('z')]
    for _ in range(n*n-1): z.append(s.times(z[-1], z[-1]))
    b = [[s.times(p[i][j], z[i*n+j]) for j in range(n)] for i in range(n)]
    frequency = []
    for f in range(N):
        xs = [Band(1, [s.times(b[i][j], s.c(pow(omega, f*labels[j], prime)))
                       for i in range(n)]) for j in range(n)]
        result = operators.evaluate(value, bands, xs)
        assert result.degree == n and len(result.values) == 1
        frequency.append(result.values[0])

    def inverse(values):
        m = len(values)
        if m == 1: return values
        e, o = inverse(values[::2]), inverse(values[1::2])
        lo, hi = [], []
        for j in range(m//2):
            t = s.times(s.c(pow(omega, (-j*(N//m)) % N, prime)), o[j])
            lo.append(s.plus(e[j], t))
            hi.append(s.plus(e[j], s.times(s.c(-1), t)))
        return lo+hi

    outputs = [s.times(s.c(F(1, N)), x) for x in inverse(frequency)]
    return dag, outputs, {'n': n, 'N': N, 'Q': prime, 'labels': list(labels), 'scalar_gates': dag.gates,
                          'generated_operator_nodes': len(operators.nodes),
                          'reachable_operator_nodes': len(operators.reachable(value)),
                          'subset_states': 0, 'operator_action_fully_expanded': True,
                          'polynomial_gate_bound_proved': False}

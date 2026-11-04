"""Compile univariate jets over K[i]/(i^2+1) into ordinary +/* gates.

This is a polynomial-overhead transformation of an ALREADY GIVEN scalar
circuit. It does not construct the missing polynomial circuit for Z.
"""
from collections import Counter
from fractions import Fraction
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
spec = importlib.util.spec_from_file_location(
    'jet_scalar_dag', PROJECT/'etudes/2026-10-24/chaine-complete/reference/dag.py')
scalar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scalar)
DAG = scalar.DAG


class Jets:
    """Dense coefficient arrays; every pair operation is charged explicitly."""
    def __init__(self, dag, degree):
        if degree < 0:
            raise ValueError('nonnegative truncation order required')
        self.dag, self.degree = dag, degree
        self.constants = {}
        self.zero, self.one, self.minus_one = (self.const(c) for c in (0, 1, -1))

    def const(self, value):
        value = Fraction(value)
        if value not in self.constants:
            self.constants[value] = self.dag.const(value)
        return self.constants[value]

    def scalar_jet(self, value):
        return [(self.const(value), self.zero)] + [(self.zero, self.zero)]*self.degree

    def pair_add(self, a, b):
        return (self.dag.add(a[0], b[0]), self.dag.add(a[1], b[1]))

    def pair_mul(self, a, b):
        ac = self.dag.mul(a[0], b[0])
        bd = self.dag.mul(a[1], b[1])
        ad = self.dag.mul(a[0], b[1])
        bc = self.dag.mul(a[1], b[0])
        real = self.dag.add(ac, self.dag.mul(self.minus_one, bd))
        imag = self.dag.add(ad, bc)
        return real, imag

    def add(self, a, b):
        return [self.pair_add(x, y) for x, y in zip(a, b)]

    def mul(self, a, b):
        out = []
        for k in range(self.degree+1):
            coefficient = self.pair_mul(a[0], b[k])
            for r in range(1, k+1):
                coefficient = self.pair_add(coefficient, self.pair_mul(a[r], b[k-r]))
            out.append(coefficient)
        return out


def lift_dag(source, outputs, algebra, inputs):
    """Simulate each source gate in the truncated coefficient algebra."""
    values = []
    for op, *args in source.nodes:
        if op == 'input':
            value = inputs[args[0]]
            if len(value) != algebra.degree+1:
                raise ValueError('wrong jet length')
        elif op == 'const':
            value = algebra.scalar_jet(args[0])
        elif op == 'add':
            value = algebra.add(values[args[0]], values[args[1]])
        elif op == 'mul':
            value = algebra.mul(values[args[0]], values[args[1]])
        else:
            raise ValueError('unsupported source gate: '+op)
        values.append(value)
    return [values[o] for o in outputs]


def gate_cost(degree, additions, multiplications, input_gates=0):
    add_cost = 2*(degree+1)
    mul_cost = 7*(degree+1)*(degree+2)//2 + degree*(degree+1)
    return input_gates + add_cost*additions + mul_cost*multiplications


def reduce_chain(source, outputs, n):
    """Specialize a_ij=i-(i/2)*t*x_ij and z=1, then expose degree n.

The source must compute the formal chain polynomial. Correctness merely
as a function on the finite base field is insufficient for this reduction.
The returned gates still include all costs inherited from the source.
"""
    if n < 1:
        raise ValueError('n must be positive')
    dag = DAG()
    algebra = Jets(dag, n)
    inputs = {'z': algebra.scalar_jet(1)}
    for op, *args in source.nodes:
        if op != 'input' or args[0] in inputs:
            continue
        name = args[0]
        if not (isinstance(name, tuple) and len(name) == 3 and name[0] == 'a'
                and 0 <= name[1] < n and 0 <= name[2] < n):
            raise ValueError('expected original a_ij inputs and z')
        x = dag.inp(('x', name[1], name[2]))
        linear = dag.mul(algebra.const(Fraction(-1, 2)), x)
        inputs[name] = [(algebra.zero, algebra.one), (algebra.zero, linear)]
        inputs[name] += [(algebra.zero, algebra.zero)]*(n-1)
    input_gates = dag.gates
    result = lift_dag(source, outputs, algebra, inputs)
    counts = Counter(node[0] for node in source.nodes)
    exact = gate_cost(n, counts['add'], counts['mul'], input_gates)
    assert dag.gates == exact
    assert dag.gates <= n*n + 7*(n+1)**2*source.gates
    return dag, result, {
        'n': n, 'source_gates': source.gates,
        'source_additions': counts['add'], 'source_multiplications': counts['mul'],
        'input_preparation_gates': input_gates, 'compiled_scalar_gates': dag.gates,
        'proven_simulation_bound': n*n + 7*(n+1)**2*source.gates,
        'operations': 'ordinary scalar add/mul only',
        'extension': 'K[i]/(i^2+1), represented by pairs over K',
        'constructs_missing_source_circuit': False,
    }

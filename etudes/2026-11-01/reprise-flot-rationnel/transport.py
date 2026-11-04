"""Scalar compilation of triangular rational transport, not of the final Z.

The additional y inputs are transport parameters. Mixed coefficient extraction
is deliberately not implemented as an uncharged scalar operation.
"""
from math import comb
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    'transport_scalar_dag', ROOT/'etudes/2026-10-24/chaine-complete/reference/dag.py')
scalar_dag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scalar_dag)


class Transport:
    def __init__(self, dimension, generators):
        if dimension < 1 or generators < 1:
            raise ValueError('positive dimension and generator count required')
        self.d, self.q = dimension, generators
        self.dag = scalar_dag.DAG()
        self.zero, self.one = self.dag.const(0), self.dag.const(1)

    def blank(self):
        return [[self.zero for _ in range(self.d)] for _ in range(self.d)]

    def inputs(self):
        xs = []
        for j in range(self.q):
            a = self.blank()
            for i in range(self.d):
                for k in range(i):
                    a[i][k] = self.dag.inp(('A', j, i, k))
            xs.append(a)
        v = [self.dag.inp(('v', i)) for i in range(self.d)]
        return xs, v

    def parameters(self, name):
        return [self.dag.inp((name, j)) for j in range(self.q)]

    def flatten(self, state):
        xs, v = state
        return [a[i][k] for a in xs for i in range(self.d) for k in range(i)]+v

    def apply(self, state, parameters):
        """(A_j,v) -> ((1-sum y_j A_j)^-1 A_j, (1-sum y_j A_j)^-1 v).

        All inverses are expanded by a finite triangular recurrence. Only
        additions and multiplications are emitted, and all are counted.
        """
        xs, v = state
        if len(xs) != self.q or len(parameters) != self.q or len(v) != self.d:
            raise ValueError('incompatible state or parameters')
        add, mul = self.dag.add, self.dag.mul
        before = self.dag.gates
        y = self.blank()
        for i in range(self.d):
            for k in range(i):
                value = mul(parameters[0], xs[0][i][k])
                for j in range(1, self.q):
                    value = add(value, mul(parameters[j], xs[j][i][k]))
                y[i][k] = value

        r = self.blank()
        for i in range(self.d):
            r[i][i] = self.one
            for k in range(i):
                value = mul(y[i][k], r[k][k])
                for h in range(k+1, i):
                    value = add(value, mul(y[i][h], r[h][k]))
                r[i][k] = value

        transformed = []
        for a in xs:
            b = self.blank()
            for i in range(self.d):
                for k in range(i):
                    value = a[i][k]
                    for h in range(k+1, i):
                        value = add(value, mul(r[i][h], a[h][k]))
                    b[i][k] = value
            transformed.append(b)
        vector = []
        for i in range(self.d):
            value = v[i]
            for k in range(i):
                value = add(value, mul(r[i][k], v[k]))
            vector.append(value)
        # This implementation deliberately counts even multiplication by 1
        # in the inverse recurrence, so this is an exact count, not a fit.
        expected = 2*(self.q+1)*comb(self.d+1, 3)
        assert self.dag.gates-before == expected
        return transformed, vector

    @property
    def state_size(self):
        return self.q*comb(self.d, 2)+self.d


def build_fusion(dimension, generators):
    """Build both sides of the fusion law on common scalar leaves."""
    compiler = Transport(dimension, generators)
    state = compiler.inputs()
    y, z = compiler.parameters('y'), compiler.parameters('z')
    sequential = compiler.apply(compiler.apply(state, y), z)
    combined = [compiler.dag.add(a, b) for a,b in zip(y,z)]
    fused = compiler.apply(state, combined)
    return compiler, compiler.flatten(sequential), compiler.flatten(fused)

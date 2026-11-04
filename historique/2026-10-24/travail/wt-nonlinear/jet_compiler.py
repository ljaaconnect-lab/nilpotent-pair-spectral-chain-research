"""Division-free rank-one pivot jets, with every coefficient operation charged.

Research witness, not a polynomial-size compiler.  Variables are commuting
and square-zero; the sparse coefficient table is an explicit exponential
scalar implementation, rather than a free algebra operation.
"""

from dag import marked_inputs


class Scalar:
    def __init__(self, dag):
        self.dag = dag
        self.cache = {}
        self.zero = dag.const(0)

    def add(self, x, y):
        if x == self.zero:
            return y
        if y == self.zero:
            return x
        key = ('add', min(x, y), max(x, y))
        if key not in self.cache:
            self.cache[key] = self.dag.add(x, y)
        return self.cache[key]

    def mul(self, x, y):
        if x == self.zero or y == self.zero:
            return self.zero
        key = ('mul', min(x, y), max(x, y))
        if key not in self.cache:
            self.cache[key] = self.dag.mul(x, y)
        return self.cache[key]


class Jets:
    def __init__(self, scalar):
        self.scalar = scalar

    def add(self, x, y):
        out = dict(x)
        for mask, coeff in y.items():
            out[mask] = self.scalar.add(out[mask], coeff) if mask in out else coeff
        return out

    def mul(self, x, y):
        out = {}
        for left, a in x.items():
            for right, b in y.items():
                if left & right:
                    continue
                mask = left | right
                value = self.scalar.mul(a, b)
                out[mask] = self.scalar.add(out[mask], value) if mask in out else value
        return out

    def pivot(self, matrix, depth=0):
        n = len(matrix)
        if n == 1:
            return matrix[0][0]
        bit = 1 << depth
        updated = []
        for i in range(1, n):
            row = []
            for j in range(1, n):
                rank_one = self.mul(matrix[i][0], matrix[0][j])
                shifted = {mask | bit: val for mask, val in rank_one.items()}
                row.append(self.add(matrix[i][j], shifted))
            updated.append(row)
        result = self.pivot(updated, depth + 1)
        value = {mask: val for mask, val in result.items() if not mask & bit}
        tangent = {mask ^ bit: val for mask, val in result.items() if mask & bit}
        return self.add(self.mul(matrix[0][0], value), tangent)


def build(n, dag):
    if n < 1:
        raise ValueError('n must be positive')
    matrix = [[{0: x} for x in row] for row in marked_inputs(n, dag)]
    output = Jets(Scalar(dag)).pivot(matrix)
    assert set(output) == {0}
    return output[0]

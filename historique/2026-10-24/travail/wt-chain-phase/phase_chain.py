"""Exact small-size joint phase/spectral compilers in ordinary scalar gates.

This is a research construction, not a general polynomial-size candidate.
The spectral slot is carried from each marked cell to the terminal reader.
There is no permanent input or intermediate requirement.
"""
from fractions import Fraction

from dag import length, marked_inputs


def gf_multiply(x, y, polynomial=7):
    """Binary field multiplication (7 gives F4, 11 gives F8)."""
    degree = polynomial.bit_length() - 1
    out = 0
    while y:
        if y & 1:
            out ^= x
        y >>= 1
        x <<= 1
        if x >> degree:
            x ^= polynomial
    return out


def certificate(n):
    """Return (kind, order, cell labels, sign reader), only where proved."""
    if n == 1:
        return 'cyclic', 1, [[0]], [1]
    if n == 2:
        return 'xor', 2, [[0, 0], [0, 1]], [-1, 1]
    if n == 3:
        return 'cyclic', 3, [[(-i*j) % 3 for j in range(3)] for i in range(3)], [0, 1, -1]
    if n == 4:
        return 'xor', 4, [[gf_multiply(i, j) for j in range(4)] for i in range(4)], [1, -1, -1, -1]
    raise ValueError('Only n=1,2,3,4 have a small certificate here.')


class Algebra:
    """Explicit sparse coordinates of R tensor Q[Z/N], R commutative.

    Coordinate indices, not values of circuit inputs, control the compiler.
    Every coordinate addition and multiplication emits charged scalar gates.
    Empty dict is a structural zero; the integer node ID 0 is never a zero test.
    """
    def __init__(self, dag, slots, kind='cyclic', order=1):
        self.dag, self.slots, self.kind, self.order = dag, slots, kind, order
        self.constants = {}

    def constant(self, value):
        value = Fraction(value)
        if value not in self.constants:
            self.constants[value] = self.dag.const(value)
        return self.constants[value]

    def one(self):
        return {(0, 0): self.constant(1)}

    def add(self, a, b):
        out = dict(a)
        for key, node in b.items():
            out[key] = self.dag.add(out[key], node) if key in out else node
        return out

    def scale(self, a, value):
        value = Fraction(value)
        if not value:
            return {}
        if value == 1:
            return dict(a)
        scalar = self.constant(value)
        return {key: self.dag.mul(scalar, node) for key, node in a.items()}

    def basis_product(self, a, b):
        if self.kind == 'cyclotomic3':
            if a + b < 2:
                return [(a+b, 1)]
            return [(0, -1), (1, -1)]
        if self.kind == 'xor':
            return [(a ^ b, 1)]
        return [((a+b) % self.order, 1)]

    def mul(self, a, b):
        out = {}
        for (g, t), u in a.items():
            for (h, s), v in b.items():
                term = self.dag.mul(u, v)
                negative = None
                for k, sign in self.basis_product(g, h):
                    if sign == -1:
                        if negative is None:
                            negative = self.dag.mul(self.constant(-1), term)
                        node = negative
                    else:
                        node = term
                    key = (k, (t+s) % self.slots)
                    out[key] = self.dag.add(out[key], node) if key in out else node
        return out


def determinant(matrix, ring):
    """Faddeev-LeVerrier; the only divisions are rational literals 1/k.

    C_0=I, T_k=B C_(k-1), c_k=-tr(T_k)/k, C_k=T_k+c_k I.
    det(B)=(-1)^n c_n, over every commutative Q-algebra.
    """
    n = len(matrix)
    previous = [[ring.one() if i == j else {} for j in range(n)] for i in range(n)]
    for k in range(1, n+1):
        product = []
        for i in range(n):
            row = []
            for j in range(n):
                total = {}
                for q in range(n):
                    total = ring.add(total, ring.mul(matrix[i][q], previous[q][j]))
                row.append(total)
            product.append(row)
        trace = {}
        for i in range(n):
            trace = ring.add(trace, product[i][i])
        coefficient = ring.scale(trace, Fraction(-1, k))
        if k < n:
            previous = [[ring.add(product[i][j], coefficient) if i == j else product[i][j]
                         for j in range(n)] for i in range(n)]
    return ring.scale(coefficient, (-1)**n)


def read_coordinates(value, ring, weights):
    """All terminal reader operations are charged, one scalar per slot."""
    zero = ring.constant(0)
    outputs = []
    for t in range(ring.slots):
        total = None
        for g, weight in enumerate(weights):
            node = value.get((g, t))
            if node is None or not weight:
                continue
            if weight != 1:
                node = ring.dag.mul(ring.constant(weight), node)
            total = node if total is None else ring.dag.add(total, node)
        outputs.append(zero if total is None else total)
    return outputs


def build_from_certificate(n, labels, dag, kind, order, phases, chi):
    """Uniform exact group-coordinate compiler, conditional on a certificate.

    Worst-case scalar size O(n^4 (order*N)^2); no group operation is a free
    arithmetic gate. Validity of the supplied certificate is a proof obligation.
    """
    if len(labels) != n or len(phases) != n or len(chi) != order:
        raise ValueError('Invalid certificate dimensions.')
    N = length(n)
    ring = Algebra(dag, N, kind, order)
    b = marked_inputs(n, dag)
    matrix = [[{(phases[i][j], labels[j] % N): b[i][j]} for j in range(n)] for i in range(n)]
    return read_coordinates(determinant(matrix, ring), ring, chi)


def build(n, labels, dag, method='specialized'):
    """Exact full-table construction for n<=4, not a general candidate.build."""
    kind, order, phases, chi = certificate(n)
    if method == 'coordinates':
        return build_from_certificate(n, labels, dag, kind, order, phases, chi)
    if method != 'specialized':
        raise ValueError(method)
    N = length(n)
    b = marked_inputs(n, dag)
    if n == 1:
        zero = dag.const(0)
        return [b[0][0] if t == labels[0] % N else zero for t in range(N)]
    if n == 2:
        ring = Algebra(dag, N)
        matrix = [[{(0, labels[j] % N): b[i][j]} for j in range(n)] for i in range(n)]
        matrix[1][1] = ring.scale(matrix[1][1], -1)
        return read_coordinates(determinant(matrix, ring), ring, [-1])
    if n == 3:
        ring = Algebra(dag, N, 'cyclotomic3', 2)
        matrix = []
        for i in range(n):
            row = []
            for j in range(n):
                t, r, node = labels[j] % N, phases[i][j], b[i][j]
                if r == 2:
                    negative = dag.mul(ring.constant(-1), node)
                    row.append({(0, t): negative, (1, t): negative})
                else:
                    row.append({(r, t): node})
            matrix.append(row)
        return read_coordinates(determinant(matrix, ring), ring, [0, 1])
    ring = Algebra(dag, N)
    result = {}
    for character in range(4):
        matrix = []
        for i in range(n):
            row = []
            for j in range(n):
                entry = {(0, labels[j] % N): b[i][j]}
                if (character & phases[i][j]).bit_count() % 2:
                    entry = ring.scale(entry, -1)
                row.append(entry)
            matrix.append(row)
        weight = Fraction(-1 if character == 0 else 1, 2)
        result = ring.add(result, ring.scale(determinant(matrix, ring), weight))
    return read_coordinates(result, ring, [1])


def large_cyclic_certificate(n):
    """Uniform exponential construction, included only to record exact scope.

    Scores encode columns used by rows 1..n-1 in base n. Materializing chi
    takes n**(n-1) steps and is NOT a polynomial compiler.
    """
    if n < 1:
        raise ValueError(n)
    order = n ** (n-1)
    phases = [[0]*n] + [[j * n**(i-1) for j in range(n)] for i in range(1, n)]
    chi = []
    for score in range(order):
        digits, remaining = [], score
        for _ in range(n-1):
            digits.append(remaining % n)
            remaining //= n
        if len(set(digits)) != n-1:
            chi.append(0)
            continue
        missing = next(j for j in range(n) if j not in digits)
        permutation = [missing] + digits
        inversions = sum(permutation[i] > permutation[j] for i in range(n) for j in range(i+1, n))
        chi.append((-1)**inversions)
    return 'cyclic', order, phases, chi

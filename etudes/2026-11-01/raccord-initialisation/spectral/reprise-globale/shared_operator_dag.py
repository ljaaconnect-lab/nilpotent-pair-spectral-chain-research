"""Compile the EXISTING product and collision reader with a shared scalar DAG.

No new raccord: repeatedly apply H <- H-L(H)/r, then substitute spectral
phases and perform the existing INTT. Differentiation happens at compile
time; the generated reachable DAG contains only scalar + and * gates.
"""
from __future__ import annotations

from dataclasses import dataclass
import math


class NodeBudgetExceeded(RuntimeError):
    pass


class DAG:
    def __init__(self, n, Q, budget=1_000_000):
        self.n, self.Q, self.budget = n, Q, budget
        self.nodes, self.degrees, self.intern, self.derivatives = [], [], {}, {}
        self.zero = self.constant(0)
        self.one = self.constant(1)

    def node(self, key, degree):
        old = self.intern.get(key)
        if old is not None:
            return old
        if len(self.nodes) >= self.budget:
            raise NodeBudgetExceeded(f'Node budget {self.budget} exceeded')
        idx = len(self.nodes)
        self.nodes.append(key)
        self.degrees.append(degree)
        self.intern[key] = idx
        return idx

    def constant(self, value):
        return self.node(('c', value % self.Q), (0,) * self.n)

    def variable(self, name, coordinate=None):
        return self.node(('v', name), tuple(int(j == coordinate) for j in range(self.n)))

    def add(self, a, b):
        if a == self.zero:
            return b
        if b == self.zero:
            return a
        if self.nodes[a][0] == self.nodes[b][0] == 'c':
            return self.constant(self.nodes[a][1] + self.nodes[b][1])
        if b < a:
            a, b = b, a
        return self.node(('+', a, b), tuple(max(x, y) for x, y in zip(self.degrees[a], self.degrees[b])))

    def mul(self, a, b):
        if a == self.zero or b == self.zero:
            return self.zero
        if a == self.one:
            return b
        if b == self.one:
            return a
        if self.nodes[a][0] == self.nodes[b][0] == 'c':
            return self.constant(self.nodes[a][1] * self.nodes[b][1])
        if b < a:
            a, b = b, a
        return self.node(('*', a, b), tuple(x + y for x, y in zip(self.degrees[a], self.degrees[b])))

    def fold(self, op, xs, unit):
        xs = list(xs)
        if not xs:
            return unit
        while len(xs) > 1:
            xs = [op(xs[i], xs[i+1]) if i+1 < len(xs) else xs[i] for i in range(0, len(xs), 2)]
        return xs[0]

    def sum(self, xs):
        return self.fold(self.add, xs, self.zero)

    def product(self, xs):
        return self.fold(self.mul, xs, self.one)

    def derivative(self, idx, j):
        key = idx, j
        if key in self.derivatives:
            return self.derivatives[key]
        if self.degrees[idx][j] == 0:
            result = self.zero
        else:
            node = self.nodes[idx]
            if node[0] == 'v':
                result = self.one
            elif node[0] == '+':
                result = self.add(self.derivative(node[1], j), self.derivative(node[2], j))
            elif node[0] == '*':
                result = self.add(self.mul(self.derivative(node[1], j), node[2]), self.mul(node[1], self.derivative(node[2], j)))
            else:
                raise AssertionError(node)
        self.derivatives[key] = result
        return result

    def L(self, root, s):
        terms = []
        for j in range(self.n):
            dd = self.derivative(self.derivative(root, j), j)
            terms.append(self.mul(self.mul(s[j], s[j]), dd))
        return self.mul(self.constant(pow(2, -1, self.Q)), self.sum(terms))

    def reachable(self, roots):
        seen, work = set(), list(roots)
        while work:
            idx = work.pop()
            if idx in seen:
                continue
            seen.add(idx)
            if self.nodes[idx][0] in ('+', '*'):
                work.extend(self.nodes[idx][1:])
        return seen

    def count(self, roots):
        return sum(self.nodes[i][0] in ('+', '*') for i in self.reachable(roots))

    def substitute(self, roots, replacements):
        mapping = dict(replacements)
        for idx in sorted(self.reachable(roots)):
            if idx in mapping:
                continue
            node = self.nodes[idx]
            if node[0] == '+':
                mapping[idx] = self.add(mapping[node[1]], mapping[node[2]])
            elif node[0] == '*':
                mapping[idx] = self.mul(mapping[node[1]], mapping[node[2]])
            else:
                mapping[idx] = idx
        return [mapping[root] for root in roots]

    def evaluate(self, roots, inputs):
        values = {}
        for idx in sorted(self.reachable(roots)):
            node = self.nodes[idx]
            if node[0] == 'c':
                values[idx] = node[1]
            elif node[0] == 'v':
                values[idx] = inputs[node[1]] % self.Q
            elif node[0] == '+':
                values[idx] = (values[node[1]] + values[node[2]]) % self.Q
            else:
                values[idx] = values[node[1]] * values[node[2]] % self.Q
        return [values[root] for root in roots]

    def intt(self, roots, omega):
        N = len(roots)
        bits = N.bit_length() - 1
        result = [roots[int(f'{i:0{bits}b}'[::-1], 2)] for i in range(N)]
        length = 2
        while length <= N:
            for start in range(0, N, length):
                for k in range(length // 2):
                    i, j = start + k, start + k + length // 2
                    even = result[i]
                    odd = self.mul(result[j], self.constant(pow(omega, -(N // length) * k, self.Q)))
                    result[i] = self.add(even, odd)
                    result[j] = self.add(even, self.mul(self.constant(-1), odd))
            length *= 2
        return [self.mul(root, self.constant(pow(N, -1, self.Q))) for root in result]


def compile_chain(n, Q, omega, ds, budget=1_000_000):
    dag = DAG(n, Q, budget)
    N = 1
    while N <= n:
        N *= 2
    assert Q > max(2, n*(n-1)//2)
    assert pow(omega, N, Q) == 1 and pow(omega, N//2, Q) != 1
    a = [[dag.variable(f'a_{i}_{j}') for j in range(n)] for i in range(n)]
    z = dag.variable('z')
    marks = [z]
    for _ in range(n*n-1):
        marks.append(dag.mul(marks[-1], marks[-1]))
    B = [[dag.mul(dag.add(dag.one, dag.mul(a[i][j], a[i][j])), marks[i*n+j]) for j in range(n)] for i in range(n)]
    s = [dag.variable(f's_{j}', j) for j in range(n)]
    root = dag.product(dag.sum(dag.mul(B[i][j], s[j]) for j in range(n)) for i in range(n))
    stages = [{'factor': 0, 'active_scalar_gates': dag.count([root]), 'allocated_nodes': len(dag.nodes)}]
    for r in range(1, n*(n-1)//2 + 1):
        root = dag.add(root, dag.mul(dag.constant(-pow(r, -1, Q)), dag.L(root, s)))
        stages.append({'factor': r, 'active_scalar_gates': dag.count([root]), 'allocated_nodes': len(dag.nodes)})
    spectra = []
    for f in range(N):
        replacements = {s[j]: dag.constant(pow(omega, f*ds[j], Q)) for j in range(n)}
        spectra.append(dag.substitute([root], replacements)[0])
    outputs = dag.intt(spectra, omega)
    assert all(dag.nodes[i][0] != 'v' or not dag.nodes[i][1].startswith('s_') for i in dag.reachable(outputs))
    return dag, outputs, stages

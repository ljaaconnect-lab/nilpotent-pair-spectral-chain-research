"""Exact full-insertion/Newton operator DAG; no polynomial-size claim.

I_j(F)=delta_j(F)+F A_j, delta_j(A_k)=A_j A_k.
The derivations and insertion operators are represented by explicit DAG
transformations. Generated and output-reachable sizes are both recorded.
"""
from fractions import Fraction as F


class OperatorDAG:
    def __init__(self, colors, order):
        self.order = order
        self.nodes, self.degrees, self.table, self.derivatives = [], [], {}, {}
        self.zero = self.node(('constant', F(0)), -1)
        self.one = self.node(('constant', F(1)), 0)
        self.variables = [self.node(('input', j), 1) for j in range(colors)]

    def node(self, key, degree):
        if key in self.table:
            return self.table[key]
        i = len(self.nodes)
        self.nodes.append(key)
        self.degrees.append(degree)
        self.table[key] = i
        return i

    def add(self, x, y):
        if x == self.zero: return y
        if y == self.zero: return x
        if x == y: return self.scale(x, 2)
        assert self.degrees[x] == self.degrees[y]
        return self.node(('add', min(x, y), max(x, y)), self.degrees[x])

    def scale(self, x, c):
        c = F(c)
        if not c or x == self.zero: return self.zero
        if c == 1: return x
        if self.nodes[x][0] == 'scale':
            _, old, value = self.nodes[x]
            return self.scale(old, c*value)
        return self.node(('scale', x, c), self.degrees[x])

    def mul(self, x, y):
        if x == self.zero or y == self.zero: return self.zero
        if x == self.one: return y
        if y == self.one: return x
        degree = self.degrees[x]+self.degrees[y]
        if degree > self.order: return self.zero
        return self.node(('mul', x, y), degree)

    def delta(self, j, x):
        key = (j, x)
        if key in self.derivatives: return self.derivatives[key]
        op, *args = self.nodes[x]
        if op == 'constant': out = self.zero
        elif op == 'input': out = self.mul(self.variables[j], x)
        elif op == 'add': out = self.add(*(self.delta(j, v) for v in args))
        elif op == 'scale': out = self.scale(self.delta(j, args[0]), args[1])
        elif op == 'mul':
            a, b = args
            out = self.add(self.mul(self.delta(j, a), b), self.mul(a, self.delta(j, b)))
        else: raise AssertionError(op)
        self.derivatives[key] = out
        return out

    def insert(self, j, x):
        return self.add(self.delta(j, x), self.mul(x, self.variables[j]))

    def newton(self):
        values, costs = [self.one], []
        for r in range(1, self.order+1):
            rhs = self.zero
            for k in range(1, r+1):
                for j in range(len(self.variables)):
                    term = values[r-k]
                    for _ in range(k): term = self.insert(j, term)
                    rhs = self.add(rhs, self.scale(term, (-1)**(k-1)))
            values.append(self.scale(rhs, F(1, r)))
            costs.append({'order': r, 'generated_nodes': len(self.nodes),
                          'reachable_nodes': len(self.reachable(values[-1]))})
        return values, costs

    def reachable(self, output):
        seen, stack = set(), [output]
        while stack:
            x = stack.pop()
            if x in seen: continue
            seen.add(x)
            op, *args = self.nodes[x]
            if op in ('add', 'mul'): stack.extend(args)
            elif op == 'scale': stack.append(args[0])
        return sorted(seen)

    def evaluate(self, output, algebra, inputs):
        values = {}
        for x in self.reachable(output):
            op, *args = self.nodes[x]
            if op == 'constant': value = algebra.scale(algebra.identity(), args[0])
            elif op == 'input': value = inputs[args[0]]
            elif op == 'add': value = algebra.add(*(values[v] for v in args))
            elif op == 'mul': value = algebra.mul(*(values[v] for v in args))
            elif op == 'scale': value = algebra.scale(values[args[0]], args[1])
            else: raise AssertionError(op)
            values[x] = value
        return values[output]


if __name__ == '__main__':
    import argparse,json
    p = argparse.ArgumentParser()
    p.add_argument('--max-order', type=int, default=6)
    args = p.parse_args()
    for n in range(1, args.max_order+1):
        dag = OperatorDAG(n, n)
        values, costs = dag.newton()
        print(json.dumps({'n': n, **costs[-1]}), flush=True)

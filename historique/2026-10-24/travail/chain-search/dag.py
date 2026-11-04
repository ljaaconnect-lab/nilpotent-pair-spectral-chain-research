from fractions import Fraction


class DAG:
    """Ordinary scalar circuit; every nonconstant operation is charged."""
    def __init__(self):
        self.nodes = []
        self.gates = 0

    def emit(self, op, *args):
        self.nodes.append((op, *args))
        self.gates += op in ('add', 'mul')
        return len(self.nodes) - 1

    def inp(self, name): return self.emit('input', name)
    def const(self, value): return self.emit('const', Fraction(value))
    def add(self, a, b): return self.emit('add', a, b)
    def mul(self, a, b): return self.emit('mul', a, b)
    def neg(self, a): return self.mul(self.const(-1), a)
    def sub(self, a, b): return self.add(a, self.neg(b))

    def evaluate_all(self, outputs, inputs, prime):
        values = []
        for op, *args in self.nodes:
            if op == 'input': v = inputs[args[0]] % prime
            elif op == 'const':
                v = args[0].numerator * pow(args[0].denominator, -1, prime) % prime
            elif op == 'add': v = (values[args[0]] + values[args[1]]) % prime
            elif op == 'mul': v = values[args[0]] * values[args[1]] % prime
            else: raise ValueError(op)
            values.append(v)
        return [values[o] for o in outputs]

    def evaluate_polynomials(self, outputs, inputs, prime):
        values = []
        for op, *args in self.nodes:
            if op == 'input':
                v = {1: 1} if args[0] == 'z' else {0: inputs[args[0]] % prime}
            elif op == 'const':
                v = {0: args[0].numerator * pow(args[0].denominator, -1, prime) % prime}
            elif op == 'add':
                v = dict(values[args[0]])
                for e, c in values[args[1]].items(): v[e] = (v.get(e, 0) + c) % prime
            elif op == 'mul':
                v = {}
                for e, a in values[args[0]].items():
                    for f, b in values[args[1]].items():
                        v[e + f] = (v.get(e + f, 0) + a * b) % prime
            else: raise ValueError(op)
            values.append({e: c for e, c in v.items() if c})
        return [values[o] for o in outputs]


def marked_inputs(n, dag):
    p = [[dag.inp(('p', i, j)) for j in range(n)] for i in range(n)]
    powers = [dag.inp('z')]
    for _ in range(n * n - 1): powers.append(dag.mul(powers[-1], powers[-1]))
    return [[dag.mul(p[i][j], powers[i * n + j]) for j in range(n)] for i in range(n)]


def length(n): return 1 << n.bit_length()


def spectral_tail(value, labels, dag):
    """Paper B.3-B.4, scalarized, with explicitly charged butterflies."""
    n = len(labels)
    N = length(n)
    one, omega = dag.const(1), dag.inp('omega')
    powers = [one, omega]
    for _ in range(2, N): powers.append(dag.mul(powers[-1], omega))
    g = powers[sum(labels) % N]
    frequency = [value]
    for _ in range(N - 1): frequency.append(dag.mul(g, frequency[-1]))

    def inverse(values):
        size = len(values)
        if size == 1: return values
        even, odd = inverse(values[::2]), inverse(values[1::2])
        lo, hi = [], []
        for k in range(size // 2):
            t = dag.mul(powers[(-k * (N // size)) % N], odd[k])
            lo.append(dag.add(even[k], t))
            hi.append(dag.sub(even[k], t))
        return lo + hi

    invN = dag.const(Fraction(1, N))
    return [dag.mul(invN, v) for v in inverse(frequency)]

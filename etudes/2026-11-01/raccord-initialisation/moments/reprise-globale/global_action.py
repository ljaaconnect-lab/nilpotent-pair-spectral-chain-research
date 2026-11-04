"""Shared scalar compilation of the existing L action on the complete source.

No differentiation gate survives the DAG. Rational row normalizations are
eliminated by an auxiliary epsilon jet with unit denominators. This module
makes no assertion that the DAG size is polynomial in n at all orders.
"""
from functools import lru_cache


class SharedDAG:
    def __init__(self, n, prime=97, max_nodes=1000000):
        self.n, self.prime, self.max_nodes = n, prime, max_nodes
        self.nodes, self.intern = [], {}
        self.zero, self.one = self.const(0), self.const(1)
        self.p = [[self.emit(("input", i, j)) for j in range(n)] for i in range(n)]
        self.m = [self.sum(self.p[i][j] for i in range(n)) for j in range(n)]
        self.q = [self.sum(self.mul(p, p) for p in row) for row in self.p]
        self.v = [self.sum(self.mul(self.m[j], self.p[i][j]) for j in range(n))
                  for i in range(n)]
        self.potential = self.sum(self.mul(self.p[i][j], self.p[k][j])
                                  for i in range(n) for k in range(i + 1, n)
                                  for j in range(n))
        self.grad_leaf = {}
        self.action_leaf = {}
        for i in range(n):
            for k in range(n):
                p = self.p[i][k]
                for j in range(n):
                    self.grad_leaf[p, j] = self.mul(
                        p, self.sub(self.one if j == k else self.zero, self.p[i][j]))
                self.action_leaf[p] = self.mul(p, self.add(
                    self.sub(self.m[k], p), self.sub(self.q[i], self.v[i])))

    def emit(self, node):
        if node in self.intern:
            return self.intern[node]
        if len(self.nodes) >= self.max_nodes:
            raise OverflowError("Explicit scalar DAG node budget reached")
        number = len(self.nodes)
        self.nodes.append(node)
        self.intern[node] = number
        return number

    def const(self, value):
        return self.emit(("const", value % self.prime))

    def add(self, a, b):
        if a == self.zero:
            return b
        if b == self.zero:
            return a
        if self.nodes[a][0] == self.nodes[b][0] == "const":
            return self.const(self.nodes[a][1] + self.nodes[b][1])
        return self.emit(("add", *sorted((a, b))))

    def mul(self, a, b):
        if a == self.zero or b == self.zero:
            return self.zero
        if a == self.one:
            return b
        if b == self.one:
            return a
        if self.nodes[a][0] == self.nodes[b][0] == "const":
            return self.const(self.nodes[a][1] * self.nodes[b][1])
        return self.emit(("mul", *sorted((a, b))))

    def sub(self, a, b):
        if a == b:
            return self.zero
        return self.add(a, self.mul(self.const(-1), b))

    def sum(self, values):
        result = self.zero
        for value in values:
            result = self.add(result, value)
        return result

    @lru_cache(None)
    def derivative(self, node, j):
        op, *args = self.nodes[node]
        if op == "const":
            return self.zero
        if op == "input":
            return self.grad_leaf[node, j]
        a, b = args
        if op == "add":
            return self.add(self.derivative(a, j), self.derivative(b, j))
        return self.add(self.mul(a, self.derivative(b, j)),
                        self.mul(b, self.derivative(a, j)))

    @lru_cache(None)
    def drift(self, node):
        op, *args = self.nodes[node]
        if op == "const":
            return self.zero
        if op == "input":
            return self.action_leaf[node]
        a, b = args
        if op == "add":
            return self.add(self.drift(a), self.drift(b))
        return self.sum([self.mul(a, self.drift(b)), self.mul(b, self.drift(a))] +
                        [self.mul(self.derivative(a, j), self.derivative(b, j))
                         for j in range(self.n)])

    def moments(self, order):
        outputs = [self.one]
        sizes = [self.reachable_size(outputs)]
        for _ in range(order):
            current = outputs[-1]
            outputs.append(self.add(self.mul(self.potential, current), self.drift(current)))
            sizes.append(self.reachable_size(outputs))
        return outputs, sizes

    def reachable(self, outputs):
        reached, queue = set(), list(outputs)
        while queue:
            node = queue.pop()
            if node in reached:
                continue
            reached.add(node)
            op, *args = self.nodes[node]
            if op in ("add", "mul"):
                queue.extend(args)
        return sorted(reached)

    def reachable_size(self, outputs):
        return sum(self.nodes[node][0] in ("add", "mul") for node in self.reachable(outputs))


class ScalarCount:
    """Numerical execution of a specified ordinary scalar DAG, with exact count."""
    def __init__(self, prime):
        self.prime, self.additions, self.multiplications = prime, 0, 0

    def add(self, a, b):
        self.additions += 1
        return (a + b) % self.prime

    def mul(self, a, b):
        self.multiplications += 1
        return a * b % self.prime

    def total(self):
        return self.additions + self.multiplications


def initialize_without_division(dag, outputs, x):
    """Produce mu_r from arbitrary x_ij=B_ij t_j, including zero row sums.

    The arithmetic program is fixed by n and the shared DAG, independent of
    data values. Every scalar + and * is counted; no data inversion is used.
    """
    n, q = dag.n, dag.prime
    count = ScalarCount(q)
    degree = n

    def jet_add(a, b):
        return [count.add(a[k], b[k]) for k in range(degree + 1)]

    def jet_mul(a, b):
        result = []
        for k in range(degree + 1):
            terms = [count.mul(a[i], b[k - i]) for i in range(k + 1)]
            value = terms[0]
            for term in terms[1:]:
                value = count.add(value, term)
            result.append(value)
        return result

    delta = []
    for row in x:
        value = row[0] % q
        for item in row[1:]:
            value = count.add(value, item)
        delta.append(count.add(value, q - 1))
    pjets = []
    hjet = [1] + [0] * n
    for i, row in enumerate(x):
        negative = count.mul(q - 1, delta[i])
        powers = [1]
        for _ in range(1, n):
            powers.append(count.mul(powers[-1], negative))
        pjets.append([[0] + [count.mul(item, power) for power in powers] for item in row])
        hjet = jet_mul(hjet, [1, delta[i]] + [0] * (n - 1))
    source_gates = count.total()
    values = {}
    for node in dag.reachable(outputs):
        op, *args = dag.nodes[node]
        if op == "const":
            values[node] = [args[0]] + [0] * n
        elif op == "input":
            values[node] = pjets[args[0]][args[1]]
        elif op == "add":
            values[node] = jet_add(values[args[0]], values[args[1]])
        else:
            values[node] = jet_mul(values[args[0]], values[args[1]])
    action_gates = count.total() - source_gates
    observations = []
    for output in outputs:
        polynomial = jet_mul(hjet, values[output])
        value = polynomial[0]
        for coefficient in polynomial[1:]:
            value = count.add(value, coefficient)
        observations.append(value)
    return observations, {"source_gates": source_gates, "action_gates": action_gates,
                          "readout_gates": count.total() - source_gates - action_gates,
                          "total_gates": count.total(), "additions": count.additions,
                          "multiplications": count.multiplications}


def attained_collision_spectrum(n):
    """Structural DP only: possible sums of binomial(block_size,2).

    This enumerates O(n^3) integer states, never subsets of input columns.
    Padding by singleton blocks also covers every source degree <=n.
    """
    reachable = [{0}]
    for size in range(1, n + 1):
        reachable.append({value + block * (block - 1) // 2
                          for block in range(1, size + 1)
                          for value in reachable[size - block]})
    return sorted(reachable[n])


def spectrum_polynomial(spectrum, prime):
    coefficients = [1]
    for value in spectrum:
        result = [0] * (len(coefficients) + 1)
        for k, coefficient in enumerate(coefficients):
            result[k] = (result[k] - value * coefficient) % prime
            result[k + 1] = (result[k + 1] + coefficient) % prime
        coefficients = result
    return coefficients


def initialize_all_without_division(dag, outputs, x):
    """Initialize every mu_0,...,mu_h using the attained-spectrum relation.

    The base outputs must comprise degrees 0 through d-1, where d is the
    number of attained eigenvalues. This reduces redundant actions but does
    not establish a polynomial bound for the base DAG.
    """
    spectrum = attained_collision_spectrum(dag.n)
    d = len(spectrum)
    if len(outputs) != d:
        raise ValueError("Need the first d explicit scalar actions")
    observations, costs = initialize_without_division(dag, outputs, x)
    coefficients = spectrum_polynomial(spectrum, dag.prime)
    scalar = ScalarCount(dag.prime)
    h = dag.n * (dag.n - 1) // 2
    for order in range(d, h + 1):
        terms = [scalar.mul(-coefficients[k] % dag.prime,
                            observations[order - d + k]) for k in range(d)]
        value = terms[0]
        for term in terms[1:]:
            value = scalar.add(value, term)
        observations.append(value)
    costs["recurrence_gates"] = scalar.total()
    costs["total_gates"] += scalar.total()
    costs["additions"] += scalar.additions
    costs["multiplications"] += scalar.multiplications
    return observations, costs

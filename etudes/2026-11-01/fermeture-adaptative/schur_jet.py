"""Division-free Schur/dual-jet compilation of the whole corrected Z chain.

Every scalar addition and multiplication emits a gate, including arithmetic
by constants. Nested dual arithmetic is expanded, never a primitive gate.
Only original entries a_ij and z are circuit inputs. The compiler does not
enumerate permutations or column subsets and does not accept P_A as input.
The exact gate bound of this candidate is exponential, not polynomial.
"""

from dataclasses import dataclass
from typing import Any


PRIME = 998244353  # 119 * 2**23 + 1
GENERATOR = 3


class ScalarDAG:
    """Scalar +/* DAG without algebraic simplification or hash-consing."""

    def __init__(self):
        self.nodes = []
        self.gates = 0

    def emit(self, op, *args):
        self.nodes.append((op, *args))
        self.gates += op in ("add", "mul")
        return len(self.nodes) - 1

    def inp(self, key):
        return self.emit("input", key)

    def const(self, value):
        return self.emit("const", int(value))

    def add(self, left, right):
        return self.emit("add", left, right)

    def mul(self, left, right):
        return self.emit("mul", left, right)

    def evaluate(self, outputs, inputs, modulus):
        values = []
        for op, *args in self.nodes:
            if op == "input":
                value = inputs[args[0]] % modulus
            elif op == "const":
                value = args[0] % modulus
            elif op == "add":
                value = (values[args[0]] + values[args[1]]) % modulus
            elif op == "mul":
                value = values[args[0]] * values[args[1]] % modulus
            else:
                raise ValueError(op)
            values.append(value)
        return [values[node] for node in outputs]

    def evaluate_formal_z(self, outputs, inputs, modulus):
        """Independent scalar interpretation in F_Q[z], without degree folding."""
        values = []
        for op, *args in self.nodes:
            if op == "input":
                value = {1: 1} if args[0] == "z" else {0: inputs[args[0]] % modulus}
            elif op == "const":
                value = {0: args[0] % modulus}
            elif op == "add":
                value = dict(values[args[0]])
                for exponent, coefficient in values[args[1]].items():
                    value[exponent] = (value.get(exponent, 0) + coefficient) % modulus
            elif op == "mul":
                value = {}
                for e, left in values[args[0]].items():
                    for f, right in values[args[1]].items():
                        value[e + f] = (value.get(e + f, 0) + left * right) % modulus
            else:
                raise ValueError(op)
            values.append({e: c for e, c in value.items() if c})
        return [values[node] for node in outputs]


class DualRing:
    """R[epsilon]/epsilon**2; base operations recursively reach scalar gates."""

    def __init__(self, base):
        self.base = base

    def add(self, x, y):
        return (self.base.add(x[0], y[0]), self.base.add(x[1], y[1]))

    def mul(self, x, y):
        return (
            self.base.mul(x[0], y[0]),
            self.base.add(self.base.mul(x[0], y[1]), self.base.mul(x[1], y[0])),
        )


def terminal_schur(matrix, ring):
    """Eliminate a pivot without division, using a fresh square-zero direction.

    H = terminal_schur(D + epsilon*c*r) = H0 + epsilon*H1.
    Return pivot*H0 + H1. The recursion is valid over any commutative ring.
    """
    size = len(matrix)
    if size < 1 or any(len(row) != size for row in matrix):
        raise ValueError("A nonempty square matrix is required")
    if size == 1:
        return matrix[0][0]
    residual = [
        [
            (matrix[i][j], ring.mul(matrix[i][0], matrix[0][j]))
            for j in range(1, size)
        ]
        for i in range(1, size)
    ]
    h0, h1 = terminal_schur(residual, DualRing(ring))
    return ring.add(ring.mul(matrix[0][0], h0), h1)


def core_gate_formula(n):
    if n < 1:
        raise ValueError("n must be positive")
    return 4 * 3 ** (n - 1) - 3 * 2**n + n + 1


@dataclass
class CompiledChain:
    dag: ScalarDAG
    outputs: list[int]
    frequencies: list[int]
    labels: list[int]
    n: int
    N: int
    prime: int
    omega: int
    costs: dict[str, Any]


def compile_chain(n, labels, prime=PRIME, generator=GENERATOR):
    """Compile Z_Q/Omega_tilde directly from a_ij,z, at each spectral frequency.

    prime is a prime-field parameter, as in the NTT contract. Exact root order
    and invertibility of N are checked here; primality is not inferred merely
    from the form c*2**m+1. The verified default is the standard prime above.
    """
    if n < 1 or len(labels) != n:
        raise ValueError("n positive and exactly n labels are required")
    N = 1 << n.bit_length()
    if prime <= 2 or prime % 2 == 0 or (prime - 1) % N:
        raise ValueError("Need an odd prime with N dividing prime-1")
    omega = pow(generator, (prime - 1) // N, prime)
    if pow(omega, N, prime) != 1 or pow(omega, N // 2, prime) == 1:
        raise ValueError("The chosen root does not have order exactly N")
    inverse_n = pow(N, -1, prime)
    dag = ScalarDAG()
    one = dag.const(1)
    raw = [[dag.inp(("a", i, j)) for j in range(n)] for i in range(n)]
    amplitudes = [[dag.add(one, dag.mul(a, a)) for a in row] for row in raw]
    markers = [dag.inp("z")]
    for _ in range(n * n - 1):
        markers.append(dag.mul(markers[-1], markers[-1]))
    matrix = [
        [dag.mul(amplitudes[i][j], markers[i * n + j]) for j in range(n)]
        for i in range(n)
    ]
    preparation_gates = dag.gates
    phase_gates, core_gates, frequencies = [], [], []
    for f in range(N):
        start = dag.gates
        phased = [
            [
                dag.mul(matrix[i][j], dag.const(pow(omega, (f * labels[j]) % N, prime)))
                for j in range(n)
            ]
            for i in range(n)
        ]
        phase_gates.append(dag.gates - start)
        start = dag.gates
        frequencies.append(terminal_schur(phased, dag))
        core_gates.append(dag.gates - start)

    transform_start = dag.gates
    minus_one = dag.const(-1)

    def inverse_transform(values):
        size = len(values)
        if size == 1:
            return values
        even = inverse_transform(values[::2])
        odd = inverse_transform(values[1::2])
        lower, upper = [], []
        for k in range(size // 2):
            phase = dag.const(pow(omega, (-k * (N // size)) % N, prime))
            term = dag.mul(phase, odd[k])
            lower.append(dag.add(even[k], term))
            upper.append(dag.add(even[k], dag.mul(minus_one, term)))
        return lower + upper

    inv_n = dag.const(inverse_n)
    outputs = [dag.mul(inv_n, value) for value in inverse_transform(frequencies)]
    transform_gates = dag.gates - transform_start
    formula = (
        4 * n * n - 1
        + N * (n * n + core_gate_formula(n))
        + 2 * N * (N.bit_length() - 1) + N
    )
    costs = {
        "preparation": preparation_gates,
        "phases_per_frequency": phase_gates,
        "core_per_frequency": core_gates,
        "core_formula": core_gate_formula(n),
        "intt": transform_gates,
        "total": dag.gates,
        "total_formula": formula,
        "scalar_additions": sum(node[0] == "add" for node in dag.nodes),
        "scalar_multiplications": sum(node[0] == "mul" for node in dag.nodes),
        "growth": "exponential for this fully expanded candidate",
    }
    return CompiledChain(dag, outputs, frequencies, list(labels), n, N, prime, omega, costs)

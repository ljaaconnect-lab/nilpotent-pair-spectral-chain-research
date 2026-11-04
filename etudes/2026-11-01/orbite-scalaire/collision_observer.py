"""Scalar DAG component for the finite collision-observer recurrence.

INPUT CONTRACT: mu_j = (L**j G)(t), j=0..h, are supplied scalar wires.
This component compiles their fusion and readout, NOT their initialization
from a_ij,z. It is not a compiler for the whole Z chain.
Every +/* operation is charged, even multiplication by a zero constant.
"""

from dataclasses import dataclass


class ScalarDAG:
    def __init__(self):
        self.nodes = []
        self.gates = 0

    def emit(self, op, *args):
        self.nodes.append((op, *args))
        self.gates += op in ("add", "mul")
        return len(self.nodes) - 1

    def inp(self, name):
        return self.emit("input", name)

    def const(self, value):
        return self.emit("const", int(value))

    def add(self, left, right):
        return self.emit("add", left, right)

    def mul(self, left, right):
        return self.emit("mul", left, right)

    def evaluate(self, outputs, observations, prime):
        values = []
        for op, *args in self.nodes:
            if op == "input":
                value = observations[args[0]] % prime
            elif op == "const":
                value = args[0] % prime
            elif op == "add":
                value = (values[args[0]] + values[args[1]]) % prime
            elif op == "mul":
                value = values[args[0]] * values[args[1]] % prime
            else:
                raise ValueError(op)
            values.append(value)
        return [values[node] for node in outputs]


def characteristic_coefficients(h):
    """Integer coefficients of chi(T)=prod_(r=0)^h(T-r), ascending.

    These depend only on n, not on supplied observations or amplitudes.
    Structural constant generation takes polynomial integer work and bits.
    """
    coefficients = [1]
    for r in range(h + 1):
        updated = [0] * (len(coefficients) + 1)
        for j, coefficient in enumerate(coefficients):
            updated[j] -= r * coefficient
            updated[j + 1] += coefficient
        coefficients = updated
    return coefficients


@dataclass
class CollisionObserver:
    n: int
    h: int
    prime: int
    dag: ScalarDAG
    stages: list[list[int]]
    outputs: list[int]
    readout: int
    chi: list[int]
    step_gates: list[int]


def compile_observer(n, prime=998244353):
    """Compile the collision factors on an already supplied moment vector.

    Mathematical precondition: prime is prime and prime > max(2,h).
    The strict size inequality is enforced. Primality is a parameter contract,
    separately checked by the verifier for all fields it uses.
    """
    if n < 1:
        raise ValueError("n must be positive")
    h = n * (n - 1) // 2
    if prime <= max(2, h):
        raise ValueError("Require a prime Q > max(2,n*(n-1)/2)")
    chi = characteristic_coefficients(h)
    dag = ScalarDAG()
    state = [dag.inp(j) for j in range(h + 1)]
    stages = [state]
    step_gates = []
    for r in range(1, h + 1):
        start = dag.gates
        inverse = pow(r, -1, prime)
        negative_inverse_wire = dag.const((-inverse) % prime)
        # chi(L)=0 gives mu_(h+1) = -sum_j c_j mu_j.
        updated = [
            dag.add(state[j], dag.mul(negative_inverse_wire, state[j + 1]))
            for j in range(h)
        ]
        high = state[h]
        for j in range(h + 1):
            coefficient = dag.const(chi[j] * inverse % prime)
            high = dag.add(high, dag.mul(coefficient, state[j]))
        updated.append(high)
        state = updated
        stages.append(state)
        step_gates.append(dag.gates - start)
    return CollisionObserver(n, h, prime, dag, stages, state, state[0], chi, step_gates)

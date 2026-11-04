"""Two genuine inverse NTTs for the collision-projector observer component.

Inputs are mu_(j,f)=(L**j G_B)(t(f)), supplied as scalar wires. Their
initialization from a_ij,z is explicitly outside this component's bound.
The inner length M compiles coefficients of pi_n; the outer length N is
the Z transform. The coefficient wires are shared across all N frequencies.
"""

from dataclasses import dataclass

from collision_observer import ScalarDAG


def check_root(root, length, prime):
    if (prime - 1) % length:
        raise ValueError("Transform length must divide Q-1")
    if pow(root, length, prime) != 1 or (length > 1 and pow(root, length // 2, prime) == 1):
        raise ValueError("Root must have the exact power-of-two transform order")


def inverse_ntt(dag, values, root, prime):
    """Emit radix-two inverse butterflies and normalization, charging all gates."""
    length = len(values)
    minus_one = dag.const(-1)

    def recurse(current):
        size = len(current)
        if size == 1:
            return current
        even = recurse(current[::2])
        odd = recurse(current[1::2])
        low, high = [], []
        for k in range(size // 2):
            phase = dag.const(pow(root, (-k * (length // size)) % length, prime))
            term = dag.mul(phase, odd[k])
            low.append(dag.add(even[k], term))
            high.append(dag.add(even[k], dag.mul(minus_one, term)))
        return low + high

    unnormalized = recurse(values)
    inverse_length = dag.const(pow(length, -1, prime))
    return [dag.mul(inverse_length, value) for value in unnormalized]


@dataclass
class SpectralProjector:
    n: int
    h: int
    N: int
    M: int
    prime: int
    root_N: int
    root_M: int | None
    dag: ScalarDAG
    coefficients: list[int]
    frequencies: list[int]
    outputs: list[int]
    costs: dict


def compile_spectral_projector(n, prime, root_N, root_M=None):
    """Compile pi coefficients, observer contractions and the outer INTT.

    prime is required to be prime; Q>max(2,h) is enforced. Roots are supplied
    structural parameters and their exact orders are checked. No amplitude,
    final answer or coefficient of an input polynomial is a constant here.
    """
    if n < 1:
        raise ValueError("n must be positive")
    h = n * (n - 1) // 2
    if prime <= max(2, h):
        raise ValueError("Require prime Q > max(2,n*(n-1)/2)")
    N = 1 << n.bit_length()
    M = 1 << h.bit_length() if h else 1
    check_root(root_N, N, prime)
    if h:
        if root_M is None:
            raise ValueError("An order-M root is required when h>0")
        check_root(root_M, M, prime)
    dag = ScalarDAG()
    observations = [[dag.inp((j, f)) for j in range(h + 1)] for f in range(N)]
    one = dag.const(1)
    factor_gates = product_gates = coefficient_intt_gates = readout_gates = 0
    if h:
        negative_inverses = [dag.const(-pow(r, -1, prime)) for r in range(1, h + 1)]
        factor_table = []
        start = dag.gates
        for ell in range(M):
            phase = dag.const(pow(root_M, ell, prime))
            factor_table.append([
                dag.add(one, dag.mul(phase, inverse)) for inverse in negative_inverses
            ])
        factor_gates = dag.gates - start
        start = dag.gates
        products = []
        for factors in factor_table:
            current = factors[0]
            for factor in factors[1:]:
                current = dag.mul(current, factor)
            products.append(current)
        product_gates = dag.gates - start
        start = dag.gates
        coefficients = inverse_ntt(dag, products, root_M, prime)
        coefficient_intt_gates = dag.gates - start
        start = dag.gates
        frequencies = []
        for f in range(N):
            terms = [dag.mul(coefficients[j], observations[f][j]) for j in range(h + 1)]
            current = terms[0]
            for term in terms[1:]:
                current = dag.add(current, term)
            frequencies.append(current)
        readout_gates = dag.gates - start
    else:
        # pi_1=1: no inner transform and no multiplication by the unit.
        coefficients = [one]
        frequencies = [row[0] for row in observations]
    start = dag.gates
    outputs = inverse_ntt(dag, frequencies, root_N, prime)
    outer_intt_gates = dag.gates - start
    inner_formula = 3 * h * M + 2 * M * (M.bit_length() - 1) if h else 0
    read_formula = N * (2 * h + 1) if h else 0
    outer_formula = 2 * N * (N.bit_length() - 1) + N
    costs = {
        "factor_ntt_evaluations": factor_gates,
        "pointwise_products": product_gates,
        "coefficient_inverse_ntt": coefficient_intt_gates,
        "shared_inner_total": factor_gates + product_gates + coefficient_intt_gates,
        "shared_inner_formula": inner_formula,
        "observer_readouts": readout_gates,
        "outer_inverse_ntt": outer_intt_gates,
        "total": dag.gates,
        "total_formula": inner_formula + read_formula + outer_formula,
        "scalar_additions": sum(node[0] == "add" for node in dag.nodes),
        "scalar_multiplications": sum(node[0] == "mul" for node in dag.nodes),
        "observation_initialization_included": False,
    }
    return SpectralProjector(n, h, N, M, prime, root_N, root_M, dag,
                             coefficients, frequencies, outputs, costs)

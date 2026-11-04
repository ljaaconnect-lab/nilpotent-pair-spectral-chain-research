"""Compose the native oriented chain as polynomial quotient representatives.

The emitted DAG contains scalar +/* gates but retains the auxiliary x_r.
Its outputs represent the complete corrected oriented INTT table in the
nilpotent quotient. They are not scalar amplitudes with inputs a,z alone.
No quotient-reading primitive, derivative, or collision projector is used.
"""
from __future__ import annotations

from pathlib import Path
import sys


PROJECT = Path(__file__).resolve().parents[2]
HISTORICAL_FOLDER = PROJECT / 'etudes/2026-11-01/linearisation-orientee-convolution'
sys.path.insert(0, str(HISTORICAL_FOLDER))
from linearised_inputs import DAG, DAG_FOLDER, ntt_radix2  # noqa: E402


class NativeDAG(DAG):
    """Historical arithmetic DAG with forbidden differential entry points."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.derivative_calls = 0
        self.collision_operator_calls = 0
        self.intt_calls = 0

    def derivative(self, *args, **kwargs):
        self.derivative_calls += 1
        raise AssertionError('Differentiation is forbidden in the native composition')

    def L(self, *args, **kwargs):
        self.collision_operator_calls += 1
        raise AssertionError('The collision projector is forbidden in the native composition')

    def intt(self, roots, omega):
        self.intt_calls += 1
        return super().intt(roots, omega)


def compile_native_representatives(n, Q, N, omega, labels, budget=1_000_000):
    """Return native quotient representatives, including a real radix-2 INTT.

    Q is a supplied prime; primality certification is the caller's contract.
    N is the smallest power of two strictly larger than n. The only field
    requirements here are N | Q-1 and an exact-order-N omega. In particular,
    no comparison of Q with n(n-1)/2 is imposed.
    """
    assert n >= 1 and Q > 2
    assert N == 1 << n.bit_length() and n < N <= 2*n
    assert (Q - 1) % N == 0
    assert pow(omega, N, Q) == 1 and pow(omega, N//2, Q) != 1
    assert len(labels) == n
    ell = N.bit_length() - 1
    epsilon = (n % 4 in (2, 3))
    gamma = -1 if epsilon else 1
    dag = NativeDAG(N, Q, budget)
    a = [[dag.variable(f'a_{i}_{j}') for j in range(n)] for i in range(n)]
    z = dag.variable('z')
    marks = [z]
    for _ in range(n*n - 1):
        marks.append(dag.mul(marks[-1], marks[-1]))
    B = [[dag.mul(dag.add(dag.one, dag.mul(a[i][j], a[i][j])), marks[i*n+j])
          for j in range(n)] for i in range(n)]
    x = [dag.variable(f'x_{r}', r) for r in range(N)]
    inverse_N = dag.constant(pow(N, -1, Q))
    C = [[dag.mul(inverse_N, value)
          for value in ntt_radix2(dag, row + [dag.zero]*(N-n), omega)]
         for row in B]
    coefficients = [value for row in C for value in row]
    forms = [dag.sum(dag.mul(C[i][r], x[(-r) % N]) for r in range(N))
             for i in range(n)]
    F0 = dag.product(forms)
    corrected = dag.mul(dag.constant(gamma), F0)

    # One shared pool supplies both phase recurrence and INTT twiddles.
    # The historical DAG folds arithmetic on constants; B(N) also covers
    # the displayed pool before this folding.
    powers = [dag.one, dag.constant(omega)]
    for _ in range(2, N):
        powers.append(dag.mul(powers[-1], powers[1]))
    target = sum(labels) % N
    phase_step = powers[target]
    spectra = [corrected]
    for _ in range(1, N):
        spectra.append(dag.mul(phase_step, spectra[-1]))
    outputs = dag.intt(spectra, omega)
    routed = [corrected if k == target else dag.zero for k in range(N)]

    coefficient_bound = 4*n*n - 1 + 2*n*N*ell + n*N
    P = coefficient_bound + 2*n*N - 1
    spectral_bound = 2*N*ell + 3*N - 3
    B_roots = [value for row in B for value in row]
    assert dag.count(B_roots) <= 4*n*n - 1
    assert dag.count(coefficients) <= coefficient_bound
    assert dag.count([F0]) <= P <= 18*n**3
    assert dag.count([corrected]) <= dag.count([F0]) + epsilon
    assert dag.count(outputs) <= P + epsilon + spectral_bound
    assert dag.count(routed) <= P + epsilon <= 18*n**3 + 1
    assert dag.count(outputs) <= dag.count([F0]) + epsilon + spectral_bound
    assert dag.derivative_calls == dag.collision_operator_calls == 0
    assert not dag.derivatives and dag.intt_calls == 1
    assert all(node[0] in ('c', 'v', '+', '*') for node in dag.nodes)
    coefficient_variables = {dag.nodes[i][1] for i in dag.reachable(coefficients)
                             if dag.nodes[i][0] == 'v'}
    assert coefficient_variables <= {'z'} | {f'a_{i}_{j}' for i in range(n) for j in range(n)}
    output_variables = {dag.nodes[i][1] for i in dag.reachable(outputs)
                        if dag.nodes[i][0] == 'v'}
    auxiliary_variables = sorted(v for v in output_variables if v.startswith('x_'))
    assert set(auxiliary_variables) == {f'x_{r}' for r in range(N)}
    info = {
        'n': n, 'Q': Q, 'N': N, 'omega': omega, 'labels': list(labels),
        'routing_index': target, 'gamma': gamma, 'epsilon': int(epsilon),
        'B_scalar_gates': dag.count(B_roots),
        'coefficient_scalar_gates': dag.count(coefficients),
        'F0_representative_gates': dag.count([F0]),
        'corrected_representative_gates': dag.count([corrected]),
        'spectral_representative_gates': dag.count(spectra),
        'true_INTT_representative_gates': dag.count(outputs),
        'routed_representative_gates': dag.count(routed),
        'joint_INTT_and_routed_gates': dag.count(outputs + routed),
        'allocated_nodes': len(dag.nodes),
        'coefficient_bound': coefficient_bound, 'P_bound': P,
        'spectral_bound_B_N': spectral_bound,
        'true_INTT_bound': P + int(epsilon) + spectral_bound,
        'routed_bound': P + int(epsilon),
        'cubic_routed_bound': 18*n**3 + 1,
        'forward_NTT_calls': n, 'true_INTT_calls': dag.intt_calls,
        'derivative_calls': dag.derivative_calls,
        'collision_operator_calls': dag.collision_operator_calls,
        'auxiliary_variables_in_outputs': auxiliary_variables,
        'coefficient_inputs': 'a_ij,z only',
        'output_inputs': 'a_ij,z and auxiliary orientation coordinates x_r',
        'output_semantics': 'gamma_n*delta_(k,sum(labels)%N)*F0 in the oriented quotient',
        'complete_scalar_a_z_only': False,
        'quotient_representatives_complete': True,
        'quotient_coordinate_extracted': False,
        'primitive_quotient_reading_gate': False,
        'compiler_uses_subset_tables': False,
    }
    return {'dag': dag, 'B': B, 'C': C, 'x': x, 'forms': forms, 'F0': F0,
            'corrected': corrected, 'spectra': spectra, 'outputs': outputs,
            'routed': routed, 'metadata': info}

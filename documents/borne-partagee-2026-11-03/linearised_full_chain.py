"""Exact scalar compilation of the linearised chain; no polynomial-size claim.

Only the historical DAG's derivative on Fourier coordinate leaves is changed.
Every final reachable arithmetic node remains a binary scalar + or * gate.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import time

PROJECT = Path(__file__).resolve().parents[2]
HISTORICAL_SOURCE = PROJECT / 'etudes/2026-11-01/raccord-initialisation/spectral/reprise-globale/shared_operator_dag.py'
_spec = importlib.util.spec_from_file_location('historical_linearised_shared_dag', HISTORICAL_SOURCE)
_historical = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_historical)
NodeBudgetExceeded = _historical.NodeBudgetExceeded


class LinearisedDAG(_historical.DAG):
    def __init__(self, n, Q, omega, budget=1_000_000):
        super().__init__(n, Q, budget)
        self.omega = omega
        self.fourier_coordinates = {}

    def fourier_variable(self, r):
        # Each x_r is linear in each of the n original coordinates.
        idx = self.node(('v', f'x_{r}'), (1,) * self.n)
        self.fourier_coordinates[idx] = r
        return idx

    def derivative(self, idx, j):
        if idx in self.fourier_coordinates:
            key = idx, j
            if key not in self.derivatives:
                r = self.fourier_coordinates[idx]
                self.derivatives[key] = self.constant(pow(self.omega, r * j, self.Q))
            return self.derivatives[key]
        return super().derivative(idx, j)


def spectral_readout(dag, Y, labels, N, omega):
    """Build phases followed by the actual historical radix-2 INTT."""
    target = sum(labels) % N
    spectra = [dag.mul(Y, dag.constant(pow(omega, f * sum(labels), dag.Q)))
               for f in range(N)]
    outputs = dag.intt(spectra, omega)
    routed = [Y if k == target else dag.zero for k in range(N)]
    return spectra, outputs, routed


def compile_linearised_chain(n, Q, omega, labels, budget=1_000_000):
    started = time.perf_counter()
    assert n >= 1
    N = 1
    while N <= n:
        N *= 2
    ell = N.bit_length() - 1
    h = n * (n - 1) // 2
    assert Q > max(2, h) and (Q - 1) % N == 0
    assert pow(omega, N, Q) == 1 and pow(omega, N // 2, Q) != 1
    assert len(labels) == n and N <= 2 * n
    dag = LinearisedDAG(n, Q, omega, budget)
    a = [[dag.variable(f'a_{i}_{j}') for j in range(n)] for i in range(n)]
    z = dag.variable('z')
    marks = [z]
    for _ in range(n * n - 1):
        marks.append(dag.mul(marks[-1], marks[-1]))
    B = [[dag.mul(dag.add(dag.one, dag.mul(a[i][j], a[i][j])), marks[i*n+j])
          for j in range(n)] for i in range(n)]
    # intt with omega^{-1} computes the positive NTT divided by N.
    C = [dag.intt(row + [dag.zero] * (N - n), pow(omega, -1, Q)) for row in B]
    x = [dag.fourier_variable(r) for r in range(N)]
    F0 = dag.product(dag.sum(dag.mul(C[i][r], x[(-r) % N]) for r in range(N))
                     for i in range(n))
    invN = dag.constant(pow(N, -1, Q))
    q = [dag.mul(invN, dag.sum(dag.mul(dag.constant(pow(omega, -r*j, Q)), x[r])
                              for r in range(N))) for j in range(n)]
    coefficient_bound = 4*n*n - 1 + 2*n*N*ell + n*N
    P = 4*n*n - 2 + 2*n*N*ell + 3*n*N
    initial_bound = P + 2*n*N
    assert dag.count([v for row in B for v in row]) <= 4*n*n - 1
    assert dag.count([v for row in C for v in row]) <= coefficient_bound
    assert dag.count([F0]) <= P
    root = F0
    stage_roots = [root]
    active = dag.count([root] + q)
    assert active <= initial_bound
    stages = [{'factor': 0, 'root_gates': dag.count([root]),
               'joint_gates_with_q': active, 'allocated_nodes': len(dag.nodes),
               'cached_derivatives': len(dag.derivatives),
               'general_bound': initial_bound}]
    bound = initial_bound
    for r in range(1, h + 1):
        previous_active = active
        root = dag.add(root, dag.mul(dag.constant(-pow(r, -1, Q)), dag.L(root, q)))
        stage_roots.append(root)
        active = dag.count([root] + q)
        local_bound = (9*n + 1) * previous_active + 3*n + 2
        bound = (9*n + 1) * bound + 3*n + 2
        assert active <= local_bound and active <= bound
        stages.append({'factor': r, 'root_gates': dag.count([root]),
                       'joint_gates_with_q': active, 'allocated_nodes': len(dag.nodes),
                       'cached_derivatives': len(dag.derivatives),
                       'local_bound': local_bound, 'general_bound': bound})
    replacements = {x[r]: dag.constant(sum(pow(omega, r*j, Q) for j in range(n)))
                    for r in range(N)}
    Y = dag.substitute([root], replacements)[0]
    spectra, outputs, routed = spectral_readout(dag, Y, labels, N, omega)
    allowed = {'z'} | {f'a_{i}_{j}' for i in range(n) for j in range(n)}
    assert all(dag.nodes[i][0] != 'v' or dag.nodes[i][1] in allowed
               for i in dag.reachable(outputs + routed))
    true_count = dag.count(outputs)
    routed_count = dag.count(routed)
    spectral_increment_bound = 2*N*ell + 2*N
    assert true_count <= dag.count([Y]) + spectral_increment_bound
    metadata = {
        'n': n, 'Q': Q, 'N': N, 'omega': omega, 'h': h, 'labels': list(labels),
        'routing_index': sum(labels) % N, 'B_gates': dag.count([v for row in B for v in row]),
        'coefficient_gates': dag.count([v for row in C for v in row]),
        'F0_gates': dag.count([F0]), 'initial_joint_gates': stages[0]['joint_gates_with_q'],
        'P_bound': P, 'initial_joint_bound': initial_bound,
        'coefficient_bound': coefficient_bound, 'stages': stages,
        'Y_gates': dag.count([Y]), 'spectra_gates': dag.count(spectra),
        'true_INTT_output_gates': true_count, 'routed_output_gates': routed_count,
        'true_INTT_additional_gates': true_count - dag.count([Y]),
        'spectral_increment_bound': spectral_increment_bound,
        'allocated_nodes': len(dag.nodes), 'elapsed_seconds': time.perf_counter() - started,
        'runtime_inputs': 'a_ij,z only', 'true_INTT_called': True,
        'universal_sign': 'absorbed exactly by gamma_n*q_[n]=Omega_tilde',
        'general_polynomial_bound_established': False,
    }
    return {'dag': dag, 'B': B, 'C': C, 'x': x, 'q': q, 'F0': F0,
            'stage_roots': stage_roots, 'Y': Y, 'spectra': spectra,
            'outputs': outputs, 'routed': routed, 'metadata': metadata}


def compile_original_fused(n, Q, omega, labels, budget=1_000_000):
    """Historical original-coordinate prefix, followed by the same spectral fusion.

    This repeats exactly its B/G_B/L constructions, but specializes s=1 only
    once. It does not charge N separate copies of its differential prefix.
    """
    started = time.perf_counter()
    N = 1
    while N <= n:
        N *= 2
    h = n * (n - 1) // 2
    assert Q > max(2, h) and (Q-1) % N == 0
    assert pow(omega, N, Q) == 1 and pow(omega, N//2, Q) != 1
    dag = _historical.DAG(n, Q, budget)
    a = [[dag.variable(f'a_{i}_{j}') for j in range(n)] for i in range(n)]
    z = dag.variable('z')
    marks = [z]
    for _ in range(n*n-1):
        marks.append(dag.mul(marks[-1], marks[-1]))
    B = [[dag.mul(dag.add(dag.one, dag.mul(a[i][j], a[i][j])), marks[i*n+j])
          for j in range(n)] for i in range(n)]
    s = [dag.variable(f's_{j}', j) for j in range(n)]
    root = dag.product(dag.sum(dag.mul(B[i][j], s[j]) for j in range(n))
                       for i in range(n))
    stages = [{'factor': 0, 'root_gates': dag.count([root]),
               'allocated_nodes': len(dag.nodes), 'cached_derivatives': len(dag.derivatives)}]
    for r in range(1, h+1):
        root = dag.add(root, dag.mul(dag.constant(-pow(r, -1, Q)), dag.L(root, s)))
        stages.append({'factor': r, 'root_gates': dag.count([root]),
                       'allocated_nodes': len(dag.nodes), 'cached_derivatives': len(dag.derivatives)})
    Y = dag.substitute([root], {v: dag.one for v in s})[0]
    spectra, outputs, routed = spectral_readout(dag, Y, labels, N, omega)
    allowed = {'z'} | {f'a_{i}_{j}' for i in range(n) for j in range(n)}
    assert all(dag.nodes[i][0] != 'v' or dag.nodes[i][1] in allowed
               for i in dag.reachable(outputs))
    return {'dag': dag, 'Y': Y, 'spectra': spectra, 'outputs': outputs,
            'routed': routed, 'metadata': {
                'Y_gates': dag.count([Y]), 'true_INTT_output_gates': dag.count(outputs),
                'routed_output_gates': dag.count(routed), 'stages': stages,
                'allocated_nodes': len(dag.nodes), 'elapsed_seconds': time.perf_counter()-started,
                'same_spectral_fusion': True, 'prefix_copies': 1}}

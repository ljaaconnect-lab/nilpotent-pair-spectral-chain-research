"""Scalar compilation of the Fourier-linearised oriented input forms.

Coefficient outputs depend only on a,z. The F_f outputs are ordinary
polynomial representatives in auxiliary x_r; they are NOT the reduced
scalar Z outputs. No polynomial-cost quotient reader is supplied here.
"""
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
DAG_FOLDER = HERE.parent / 'raccord-initialisation/spectral/reprise-globale'
sys.path.insert(0, str(DAG_FOLDER))
from shared_operator_dag import DAG  # noqa: E402


def ntt_radix2(dag, values, omega):
    """Forward transform sum_j values[j]*omega^(r*j), without normalization."""
    N = len(values)
    assert N >= 1 and N & (N - 1) == 0
    bits = N.bit_length() - 1
    result = [values[int(f'{i:0{bits}b}'[::-1], 2)] for i in range(N)]
    length = 2
    while length <= N:
        for start in range(0, N, length):
            for k in range(length // 2):
                i, j = start + k, start + k + length // 2
                even = result[i]
                odd = dag.mul(result[j], dag.constant(pow(omega, (N // length)*k, dag.Q)))
                result[i] = dag.add(even, odd)
                result[j] = dag.add(even, dag.mul(dag.constant(-1), odd))
        length *= 2
    return result


def compile_linearised_inputs(n, Q, N, omega, labels, budget=1_000_000):
    """Compile C[i][f][r]=(1/N)NTT_j(B_ij*omega^(f*d_j))[r].

    The caller supplies prime Q and an exact-order-N omega. N is a power
    of two, N>=n. F[f]=prod_i sum_r C[i][f][r]*x[(-r) mod N].
    """
    assert n >= 1 and Q > max(2, n*(n-1)//2)
    assert N >= n and N & (N - 1) == 0 and (Q - 1) % N == 0
    assert pow(omega, N, Q) == 1
    assert N == 1 or pow(omega, N//2, Q) != 1
    assert len(labels) == n
    # N auxiliary coordinates, while the original matrix still has n*n entries.
    dag = DAG(N, Q, budget)
    a = [[dag.variable(f'a_{i}_{j}') for j in range(n)] for i in range(n)]
    z = dag.variable('z')
    marks = [z]
    for _ in range(n*n - 1):
        marks.append(dag.mul(marks[-1], marks[-1]))
    B = [[dag.mul(dag.add(dag.one, dag.mul(a[i][j], a[i][j])), marks[i*n+j])
          for j in range(n)] for i in range(n)]
    x = [dag.variable(f'x_{r}', r) for r in range(N)]
    inverse_N = dag.constant(pow(N, -1, Q))
    C = [[None]*N for _ in range(n)]
    for i in range(n):
        for f in range(N):
            row = [dag.mul(B[i][j], dag.constant(pow(omega, f*labels[j], Q)))
                   for j in range(n)] + [dag.zero]*(N-n)
            transformed = ntt_radix2(dag, row, omega)
            C[i][f] = [dag.mul(inverse_N, value) for value in transformed]
    coefficient_roots = [value for row in C for frequency in row for value in frequency]
    assert all(dag.nodes[index][0] != 'v' or not dag.nodes[index][1].startswith('x_')
               for index in dag.reachable(coefficient_roots))
    F = [dag.product(dag.sum(dag.mul(C[i][f][r], x[(-r) % N]) for r in range(N))
                     for i in range(n)) for f in range(N)]
    preparation_bound = 4*n*n - 1
    phase_bound = n*n*N
    ntt_bound = 2*n*N*N*(N.bit_length()-1)
    normalization_bound = n*N*N
    representative_bound = N*(2*n*N - 1)
    coefficients_bound = preparation_bound + phase_bound + ntt_bound + normalization_bound
    total_bound = coefficients_bound + representative_bound
    assert dag.count(coefficient_roots) <= coefficients_bound
    assert dag.count(F) <= total_bound
    return dag, F, C, {
        'n': n, 'Q': Q, 'N': N, 'omega': omega, 'labels': list(labels),
        'B_roots': B, 'auxiliary_roots': x,
        'coefficient_scalar_gates': dag.count(coefficient_roots),
        'polynomial_representative_scalar_gates': dag.count(F),
        'allocated_nodes': len(dag.nodes),
        'gate_bounds': {
            'input_preparation': preparation_bound, 'modulation': phase_bound,
            'forward_ntt': ntt_bound, 'normalization': normalization_bound,
            'products_of_linear_forms': representative_bound,
            'all_coefficients': coefficients_bound, 'all_representatives': total_bound,
        },
        'coefficient_data_inputs': 'a,z only',
        'representative_inputs': 'a,z and formal auxiliary x_0,...,x_(N-1)',
        'oriented_quotient_reduced': False,
        'complete_scalar_Z_compiled': False,
    }

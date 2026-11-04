"""One Fourier representative after exact fusion of the spectral output.

The output F0 still has formal auxiliary coordinates x. Its quotient reader
is not implemented or charged as a free gate. Only preparation is compiled.
"""
from linearised_inputs import DAG, ntt_radix2


def compile_fused_linearised(n, Q, N, omega, labels, budget=1_000_000):
    assert n >= 1 and Q > max(2, n*(n-1)//2)
    assert N >= n and N & (N-1) == 0 and (Q-1) % N == 0
    assert pow(omega, N, Q) == 1
    assert N == 1 or pow(omega, N//2, Q) != 1
    assert len(labels) == n
    dag = DAG(N, Q, budget)
    a = [[dag.variable(f'a_{i}_{j}') for j in range(n)] for i in range(n)]
    z = dag.variable('z')
    marks = [z]
    for _ in range(n*n-1):
        marks.append(dag.mul(marks[-1], marks[-1]))
    B = [[dag.mul(dag.add(dag.one, dag.mul(a[i][j], a[i][j])), marks[i*n+j])
          for j in range(n)] for i in range(n)]
    x = [dag.variable(f'x_{r}', r) for r in range(N)]
    inverse_N = dag.constant(pow(N, -1, Q))
    C = [[dag.mul(inverse_N, value)
          for value in ntt_radix2(dag, row+[dag.zero]*(N-n), omega)] for row in B]
    coefficients = [value for row in C for value in row]
    F0 = dag.product(dag.sum(dag.mul(C[i][r], x[(-r) % N]) for r in range(N))
                     for i in range(n))
    coefficient_bound = 4*n*n-1+2*n*N*(N.bit_length()-1)+n*N
    representative_bound = coefficient_bound+2*n*N-1
    assert dag.count(coefficients) <= coefficient_bound
    assert dag.count([F0]) <= representative_bound
    assert all(dag.nodes[index][0] != 'v' or not dag.nodes[index][1].startswith('x_')
               for index in dag.reachable(coefficients))
    if N < 2*n:
        assert representative_bound <= 18*n**3
    return dag, F0, C, {
        'n': n, 'Q': Q, 'N': N, 'omega': omega,
        'labels': list(labels), 'routing_index': sum(labels) % N,
        'coefficient_scalar_gates': dag.count(coefficients),
        'polynomial_representative_scalar_gates': dag.count([F0]),
        'coefficient_gate_bound': coefficient_bound,
        'representative_gate_bound': representative_bound,
        'ntt_calls': n, 'auxiliary_representatives': 1,
        'coefficient_data_inputs': 'a,z only',
        'representative_inputs': 'a,z and formal auxiliary x_0,...,x_(N-1)',
        'quotient_reader_compiled': False,
        'complete_scalar_Z_compiled': False,
        'compiler_uses_subset_tables': False,
    }

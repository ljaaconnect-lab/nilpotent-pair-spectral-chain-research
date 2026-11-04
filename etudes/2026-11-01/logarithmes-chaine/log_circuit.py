"""Compile formal logarithmic coordinates of the existing collision reader.

All runtime nodes are ordinary scalar + and * gates over the supplied field.
Formal log/exp are truncated polynomial algorithms, not primitive gates.
No assertion of polynomial or quasi-polynomial total size is made.
"""
from pathlib import Path
import sys

SHARED = Path(__file__).resolve().parents[1] / 'raccord-initialisation/spectral/reprise-globale'
sys.path.insert(0, str(SHARED))
from shared_operator_dag import DAG, NodeBudgetExceeded


def jet_add(dag, a, b):
    return [dag.add(x, y) for x, y in zip(a, b)]


def jet_scale(dag, a, c):
    return [dag.mul(c, x) for x in a]


def jet_mul(dag, a, b):
    return [dag.sum(dag.mul(a[i], b[k-i]) for i in range(k+1))
            for k in range(len(a))]


def jet_log_one_plus(dag, a, order=1):
    """a is divisible by epsilon**order; return log(1+a) mod epsilon**(n+1)."""
    n = len(a)-1
    assert all(x == dag.zero for x in a[:order])
    result = [dag.zero]
    # (1+a)*c' = a', hence k*c_k = k*a_k-sum_{i<k} i*c_i*a_{k-i}.
    for k in range(1, n+1):
        terms = (dag.mul(dag.constant(i), dag.mul(result[i], a[k-i]))
                 for i in range(1, k))
        result.append(dag.add(a[k], dag.mul(dag.constant(-pow(k, -1, dag.Q)),
                                          dag.sum(terms))))
    return result


def jet_exp(dag, u):
    """Use k*H_k = sum_{j=1}^k j*U_j*H_{k-j}."""
    assert u[0] == dag.zero
    h = [dag.one]
    for k in range(1, len(u)):
        terms = (dag.mul(dag.constant(j), dag.mul(u[j], h[k-j]))
                 for j in range(1, k+1))
        h.append(dag.mul(dag.constant(pow(k, -1, dag.Q)), dag.sum(terms)))
    return h


def compile_log_chain(n, Q, omega, ds, budget=1_000_000, prune=True):
    assert n >= 1 and Q > max(2, n, n*(n-1)//2)
    N = 1 << n.bit_length()
    assert pow(omega, N, Q) == 1 and pow(omega, N//2, Q) != 1
    assert len(ds) == n
    dag = DAG(n, Q, budget)
    a = [[dag.variable(f'a_{i}_{j}') for j in range(n)] for i in range(n)]
    z = dag.variable('z')
    marks = [z]
    for _ in range(n*n-1):
        marks.append(dag.mul(marks[-1], marks[-1]))
    B = [[dag.mul(dag.add(dag.one, dag.mul(a[i][j], a[i][j])), marks[i*n+j])
          for j in range(n)] for i in range(n)]
    s = [dag.variable(f's_{j}', j) for j in range(n)]
    delta = [dag.add(dag.constant(-1), dag.sum(dag.mul(B[i][j], s[j]) for j in range(n)))
             for i in range(n)]
    u = [dag.zero] * (n+1)
    powers = [dag.one] * n
    for k in range(1, n+1):
        powers = [dag.mul(powers[i], delta[i]) for i in range(n)]
        scalar = dag.constant((1 if k % 2 else -1)*pow(k, -1, Q))
        u[k] = dag.mul(scalar, dag.sum(powers))
    stage_roots = [list(u)]
    stages = [{'factor': 0, 'coefficient_gates': dag.count(u), 'allocated_nodes': len(dag.nodes)}]
    half = dag.constant(pow(2, -1, Q))
    for r in range(1, n*(n-1)//2+1):
        euler = {}
        def e(j, k):
            if (j, k) not in euler:
                euler[j, k] = dag.mul(s[j], dag.derivative(u[k], j))
            return euler[j, k]
        alpha = []
        for k in range(n+1):
            # [epsilon^k] H has s-degree <= k. After k*(k-1)/2
            # factors every nonzero collision eigenvalue has been killed.
            # The same zero initial segment holds in H^{-1}*L(H).
            if prune and r > k*(k-1)//2:
                alpha.append(dag.zero)
            else:
                quadratic = dag.sum(dag.mul(e(j, a), e(j, k-a))
                                    for j in range(n) for a in range(1, k))
                alpha.append(dag.add(dag.L(u[k], s), dag.mul(half, quadratic)))
        # U_1 remains affine in s throughout the existing reader.
        assert alpha[0] == alpha[1] == dag.zero
        correction = jet_log_one_plus(
            dag, jet_scale(dag, alpha, dag.constant(-pow(r, -1, Q))), order=2)
        u = jet_add(dag, u, correction)
        stage_roots.append(list(u))
        stages.append({'factor': r, 'coefficient_gates': dag.count(u),
                       'active_coefficients': sum(r <= k*(k-1)//2 for k in range(n+1)),
                       'allocated_nodes': len(dag.nodes)})
    # H_h is an actual polynomial of epsilon-degree <= n. Only after exp
    # restores it may its coefficients be summed to set epsilon = 1.
    h = jet_exp(dag, u)
    root = dag.sum(h)
    spectra = [dag.substitute([root],
               {s[j]: dag.constant(pow(omega, f*ds[j], Q)) for j in range(n)})[0]
               for f in range(N)]
    outputs = dag.intt(spectra, omega)
    assert all(dag.nodes[i][0] != 'v' or not dag.nodes[i][1].startswith('s_')
               for i in dag.reachable(outputs))
    return dag, outputs, stage_roots, stages

"""Compile the homogeneous collision projector before expanding derivatives.

Data leaves are a_ij and formal z. Every runtime arithmetic gate is + or *.
There is no polynomial-size claim, jet table, logarithm, or target input.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
DAG_FOLDER = HERE.parent / 'raccord-initialisation' / 'spectral' / 'reprise-globale'
sys.path.insert(0, str(DAG_FOLDER))
from shared_operator_dag import DAG, NodeBudgetExceeded


def stage_invariants(dag, root, processed):
    """Check homogeneous degree and disappearance of processed coordinates."""
    degrees = {}
    remaining = []
    for index in sorted(dag.reachable([root])):
        node = dag.nodes[index]
        assert node[0] in ('c', 'v', '+', '*')
        if node[0] == 'v':
            if node[1].startswith('s_'):
                coordinate = int(node[1][2:])
                assert processed <= coordinate < dag.n
                remaining.append(coordinate)
                degrees[index] = 1
            else:
                assert node[1] == 'z' or node[1].startswith('a_')
                degrees[index] = 0
        elif node[0] == 'c':
            degrees[index] = 0
        elif node[0] == '*':
            degrees[index] = degrees[node[1]] + degrees[node[2]]
        else:
            assert degrees[node[1]] == degrees[node[2]], (index, node)
            degrees[index] = degrees[node[1]]
    assert degrees[root] == dag.n - processed
    assert all(degree == 0 for degree in dag.degrees[root][:processed])
    return {
        'processed_columns': processed,
        'homogeneous_degree': degrees[root],
        'remaining_auxiliary_variables': sorted(remaining),
        'scalar_gates': dag.count([root]),
        'root': root,
    }


def compile_projected(n, Q, N, labels, budget=1_000_000):
    """Compile the corrected spectral output; supplied Q must be prime.

    H_0=G_B; H_(j+1)=(partial_j H_j)|_(s_j=0).
    The final scalar is routed to sum(labels) modulo N.
    """
    assert n >= 1 and Q > max(2, n * (n - 1) // 2)
    assert N > n and N & (N - 1) == 0 and (Q - 1) % N == 0
    assert len(labels) == n
    dag = DAG(n, Q, budget)
    a = [[dag.variable(f'a_{i}_{j}') for j in range(n)] for i in range(n)]
    z = dag.variable('z')
    marks = [z]
    for _ in range(n * n - 1):
        marks.append(dag.mul(marks[-1], marks[-1]))
    B = [[dag.mul(dag.add(dag.one, dag.mul(a[i][j], a[i][j])), marks[i*n+j])
          for j in range(n)] for i in range(n)]
    s = [dag.variable(f's_{j}', j) for j in range(n)]
    root = dag.product(dag.sum(dag.mul(B[i][j], s[j]) for j in range(n))
                       for i in range(n))
    stages = [stage_invariants(dag, root, 0)]
    for j in range(n):
        derivative = dag.derivative(root, j)
        root = dag.substitute([derivative], {s[j]: dag.zero})[0]
        stages.append(stage_invariants(dag, root, j + 1))
    outputs = [dag.zero] * N
    outputs[sum(labels) % N] = root
    assert stages[-1]['remaining_auxiliary_variables'] == []
    return dag, outputs, stages

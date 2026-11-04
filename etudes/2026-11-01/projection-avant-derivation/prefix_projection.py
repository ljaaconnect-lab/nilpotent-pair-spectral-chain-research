"""Construct the old prefix by the new projection, from a,z only.

The additional quadratic circuit is needed only if the prefix itself is
requested. In the full corrected chain its two tails cancel symbolically.
"""
from direct_projection import compile_projected


def attained_collisions(n):
    values = [{0}]
    for degree in range(1, n + 1):
        values.append({c + k * (k - 1) // 2
                       for k in range(1, degree + 1)
                       for c in values[degree - k]})
    return values[n]


def compile_prefix(n, Q, N, labels, budget=1_000_000):
    assert n >= 3
    dag, outputs, stages = compile_projected(n, Q, N, labels, budget)
    y = outputs[sum(labels) % N]
    base_gates = dag.count([y])
    # Recover the already interned input preparation; do not duplicate it.
    allocated = len(dag.nodes)
    a = [[dag.variable(f'a_{i}_{j}') for j in range(n)] for i in range(n)]
    marks = [dag.variable('z')]
    for _ in range(n * n - 1):
        marks.append(dag.mul(marks[-1], marks[-1]))
    B = [[dag.mul(dag.add(dag.one, dag.mul(a[i][j], a[i][j])), marks[i*n+j])
          for j in range(n)] for i in range(n)]
    assert len(dag.nodes) == allocated
    reachable_y = dag.reachable([y])
    assert all(b in reachable_y for row in B for b in row)

    near, pure = (n - 1) * (n - 2) // 2, n * (n - 1) // 2
    factors = sorted(attained_collisions(n) - {0, near, pure})

    def weight(k):
        value = 1
        for r in factors:
            value = value * (1 - k * pow(r, -1, Q)) % Q
        return value

    alpha, beta = weight(near), weight(pure)
    omitted = [[None] * n for _ in range(n)]
    columns = []
    for j in range(n):
        prefix = [dag.one]
        for i in range(n):
            prefix.append(dag.mul(prefix[-1], B[i][j]))
        suffix = [dag.one] * (n + 1)
        for i in range(n - 1, 0, -1):
            suffix[i] = dag.mul(B[i][j], suffix[i + 1])
        columns.append(prefix[n])
        for i in range(n):
            omitted[i][j] = dag.mul(prefix[i], suffix[i + 1])
    row_sums = [dag.sum(row) for row in B]
    cofactor_sums = [dag.sum(row) for row in omitted]
    S = dag.sum(dag.mul(row_sums[i], cofactor_sums[i]) for i in range(n))
    C = dag.sum(columns)
    x = dag.add(dag.add(y, dag.mul(dag.constant(alpha), S)),
                dag.mul(dag.constant(beta - n * alpha), C))
    prefix_gates = dag.count([x])
    extra_gates = len({i for i in dag.reachable([x]) - reachable_y
                       if dag.nodes[i][0] in ('+', '*')})
    bound = 5*n*n - 4*n + 2
    assert extra_gates <= bound and prefix_gates <= base_gates + bound
    return dag, x, outputs, {
        'n': n, 'projection_gates': base_gates, 'prefix_gates': prefix_gates,
        'extra_gates': extra_gates, 'extra_gates_bound': bound,
        'alpha': alpha, 'beta': beta, 'factors': factors,
        'B_preparation_shared': True,
    }

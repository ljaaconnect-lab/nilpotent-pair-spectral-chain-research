"""Fuse the spectral output and use homogeneous single/double log coordinates.

The generated runtime DAG has only scalar + and * gates and inputs a,z.
Parameters n, prime Q, N and labels are supplied. No polynomial-size claim.
"""
from pathlib import Path
import sys

LOG_FOLDER = Path(__file__).resolve().parents[1] / 'logarithmes-chaine'
sys.path.insert(0, str(LOG_FOLDER))
from log_circuit import DAG, NodeBudgetExceeded, jet_add, jet_scale, jet_mul


def jet_exp(dag, u):
    """Share j*u_j across all output coefficients: <= n^2+n-2 gates."""
    assert u[0] == dag.zero
    weighted = [dag.mul(dag.constant(j), u[j]) for j in range(len(u))]
    result = [dag.one]
    for k in range(1, len(u)):
        total = dag.sum(dag.mul(weighted[j], result[k-j]) for j in range(1, k+1))
        result.append(dag.mul(dag.constant(pow(k, -1, dag.Q)), total))
    return result


def jet_log_one_plus(dag, a, order=1):
    """Share i*c_i as soon as c_i is available; no primitive log gate."""
    assert all(x == dag.zero for x in a[:order])
    result, weighted = [dag.zero], [dag.zero]
    for k in range(1, len(a)):
        total = dag.sum(dag.mul(weighted[i], a[k-i]) for i in range(1, k))
        c = dag.add(a[k], dag.mul(dag.constant(-pow(k, -1, dag.Q)), total))
        result.append(c)
        weighted.append(dag.mul(dag.constant(k), c))
    return result


def jet_inverse_unit(dag, a):
    assert a[0] == dag.one
    result = [dag.one]
    for k in range(1, len(a)):
        result.append(dag.mul(dag.constant(-1),
                              dag.sum(dag.mul(a[i], result[k-i]) for i in range(1, k+1))))
    return result


def collision_spectrum(n):
    """Constants only: attainable sum binom(block_size,2) at total size n."""
    spectra = [{0}]
    for degree in range(1, n+1):
        spectra.append({previous+k*(k-1)//2 for k in range(1, degree+1)
                        for previous in spectra[degree-k]})
    return sorted(spectra[n])


def compile_fused(n, Q, N, labels, mode='single', budget=1_000_000,
                  compress=True, terminal_correction=True):
    assert n >= 1 and Q > max(2, n*(n-1)//2)
    assert N > n and N & (N-1) == 0 and (Q-1) % N == 0
    assert len(labels) == n and mode in ('direct', 'single', 'double')
    dag = DAG(n, Q, budget)
    a = [[dag.variable(f'a_{i}_{j}') for j in range(n)] for i in range(n)]
    z = dag.variable('z')
    marks = [z]
    for _ in range(n*n-1):
        marks.append(dag.mul(marks[-1], marks[-1]))
    B = [[dag.mul(dag.add(dag.one, dag.mul(a[i][j], a[i][j])), marks[i*n+j])
          for j in range(n)] for i in range(n)]
    s = [dag.variable(f's_{j}', j) for j in range(n)]
    ell = [dag.sum(dag.mul(B[i][j], s[j]) for j in range(n)) for i in range(n)]
    h = n*(n-1)//2
    factors = collision_spectrum(n)[1:] if compress else list(range(1, h+1))
    # Fuse the two largest collision levels directly into the final readout.
    # For n>=3 their only degree-n profiles are (n) and (n-1,1).
    two_level_readout = terminal_correction and n >= 3
    near_collision = (n-1)*(n-2)//2
    active_factors = [r for r in factors if r < near_collision] if two_level_readout else factors
    def pure_column_correction():
        # Before the final factor, only collision h can survive besides 0.
        # Its source is sum_j(prod_i B_ij)*s_j^n, multiplied by a constant.
        scalar = 1
        for r in factors[:-1]:
            scalar = scalar*(1-h*pow(r, -1, Q)) % Q
        terms = []
        for j in range(n):
            power, base, exponent = dag.one, s[j], n
            while exponent:
                if exponent & 1:
                    power = dag.mul(power, base)
                exponent >>= 1
                if exponent:
                    base = dag.mul(base, base)
            terms.append(dag.mul(dag.product(B[i][j] for i in range(n)), power))
        return dag.mul(dag.constant(-scalar), dag.sum(terms))
    stages, coordinates = [], []
    if mode == 'direct':
        root = dag.product(ell)
        stages.append({'factor': 0, 'coefficient_gates': dag.count([root])})
        for r in active_factors:
            if terminal_correction and r == h:
                root = dag.add(root, pure_column_correction())
            else:
                root = dag.add(root, dag.mul(dag.constant(-pow(r, -1, Q)), dag.L(root, s)))
            stages.append({'factor': r, 'coefficient_gates': dag.count([root])})
    else:
        # [epsilon^n] product_i(1+epsilon*ell_i) is the original G_B.
        # Its log coefficients are homogeneous in s, without affine shifts.
        v = [dag.zero]*(n+1)
        powers = [dag.one]*n
        for k in range(1, n+1):
            powers = [dag.mul(powers[i], ell[i]) for i in range(n)]
            c = dag.constant((1 if k % 2 else -1)*pow(k, -1, Q))
            v[k] = dag.mul(c, dag.sum(powers))
        if mode == 'double':
            v = jet_log_one_plus(dag, v)
        coordinates.append(list(v))
        stages.append({'factor': 0, 'coefficient_gates': dag.count(v)})
        half = dag.constant(pow(2, -1, Q))
        for r in active_factors:
            if terminal_correction and r == h:
                v = list(v)
                v[n] = dag.add(v[n], pure_column_correction())
                coordinates.append(list(v))
                stages.append({'factor': r, 'coefficient_gates': dag.count(v),
                               'terminal_correction_without_derivatives': True})
                continue
            min_degree = next(k for k in range(2, n+1) if k*(k-1)//2 >= r)
            gradient = {}
            def e(j, k):
                if (j, k) not in gradient:
                    gradient[j, k] = dag.mul(s[j], dag.derivative(v[k], j))
                return gradient[j, k]
            quadratic = [dag.sum(dag.mul(e(j, i), e(j, k-i))
                                 for j in range(n) for i in range(1, k))
                         for k in range(n+1)]
            if mode == 'single':
                alpha = [dag.zero if k < min_degree else
                         dag.add(dag.L(v[k], s), dag.mul(half, quadratic[k]))
                         for k in range(n+1)]
                change = jet_log_one_plus(
                    dag, jet_scale(dag, alpha, dag.constant(-pow(r, -1, Q))), min_degree)
            else:
                exp_v = jet_exp(dag, v)
                # B(W)=L W+1/2*(1+exp W)*sum_j(D_j W)^2.
                normalized = []
                for k in range(n+1):
                    if k < min_degree:
                        normalized.append(dag.zero)
                    else:
                        tail = dag.sum(dag.mul(exp_v[i], quadratic[k-i]) for i in range(1, k+1))
                        normalized.append(dag.add(dag.L(v[k], s),
                                                  dag.add(quadratic[k], dag.mul(half, tail))))
                if 2*min_degree > n:
                    # Nested logarithms become exactly linear in the correction.
                    change = jet_scale(dag, normalized, dag.constant(-pow(r, -1, Q)))
                else:
                    alpha = jet_mul(dag, exp_v, normalized)
                    inner = jet_log_one_plus(dag, jet_scale(
                        dag, alpha, dag.constant(-pow(r, -1, Q))), min_degree)
                    relative = jet_mul(dag, jet_inverse_unit(dag, exp_v), inner)
                    change = jet_log_one_plus(dag, relative, min_degree)
            v = jet_add(dag, v, change)
            coordinates.append(list(v))
            stages.append({'factor': r, 'coefficient_gates': dag.count(v),
                           'min_correction_degree': min_degree,
                           'linear_log_correction': 2*min_degree > n})
        if mode == 'double':
            u = jet_exp(dag, v)
            u[0] = dag.zero  # exp(W)-1
        else:
            u = v
        root = jet_exp(dag, u)[n]
    # The terminal homogeneous squarefree polynomial in n variables is a
    # multiple of their product. Phases + INTT therefore route to one slot.
    coefficient = dag.substitute([root], {x: dag.one for x in s})[0]
    if two_level_readout:
        weight_near = weight_pure = 1
        for r in active_factors:
            weight_near = weight_near*(1-near_collision*pow(r, -1, Q)) % Q
            weight_pure = weight_pure*(1-h*pow(r, -1, Q)) % Q
        omitted = [[dag.one]*n for _ in range(n)]
        column_products = []
        for j in range(n):
            prefix = [dag.one]
            for i in range(n):
                prefix.append(dag.mul(prefix[-1], B[i][j]))
            suffix = [dag.one]*(n+1)
            for i in range(n-1, -1, -1):
                suffix[i] = dag.mul(B[i][j], suffix[i+1])
            column_products.append(prefix[n])
            for i in range(n):
                omitted[i][j] = dag.mul(prefix[i], suffix[i+1])
        pure = dag.sum(column_products)
        # Near-pure source: sum_i rowSum_i * sum_j omitProduct_ij - n*pure.
        near_plus_pure = dag.sum(dag.mul(dag.sum(B[i]), dag.sum(omitted[i]))
                                for i in range(n))
        coefficient = dag.add(coefficient, dag.mul(dag.constant(-weight_near), near_plus_pure))
        coefficient = dag.add(coefficient, dag.mul(dag.constant(n*weight_near-weight_pure), pure))
        stages.append({'factor': h, 'terminal_collision_levels_fused_into_readout':
                       [near_collision, h], 'output_gates': dag.count([coefficient])})
    outputs = [dag.zero]*N
    outputs[sum(labels) % N] = coefficient
    assert all(dag.nodes[i][0] != 'v' or not dag.nodes[i][1].startswith('s_')
               for i in dag.reachable(outputs))
    return dag, outputs, coordinates, stages

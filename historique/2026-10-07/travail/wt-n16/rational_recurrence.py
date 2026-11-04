"""New reciprocal-determinant recurrence and Laurent label normalization.

The source circuit is division-free. For validation only, auxiliary x variables
are evaluated in their square-zero quotient with a separately charged scalar
compilation. No residue or coefficient is counted as a free circuit gate.
"""
from __future__ import annotations
from collections import defaultdict
from fractions import Fraction
from itertools import permutations, combinations
from math import prod
import sympy as sp


class RationalDAG:
    def __init__(self, n):
        self.n = n
        self.nodes = []
        self.gates = 0
        self.constants = {}
        self.symbols = sp.symbols(f'b0:{n*n}')

    def constant(self, value):
        value = Fraction(value)
        if value not in self.constants:
            self.constants[value] = len(self.nodes)
            self.nodes.append(('constant', value))
        return self.constants[value]

    def weight(self, i, j):
        out = len(self.nodes)
        self.nodes.append(('weight', i*self.n+j))
        return out

    def occupancy(self, i):
        out = len(self.nodes)
        self.nodes.append(('occupancy', i))
        return out

    def operation(self, op, a, b):
        assert 0 <= a < len(self.nodes) and 0 <= b < len(self.nodes)
        out = len(self.nodes)
        self.nodes.append((op, a, b))
        self.gates += 1
        return out

    def add(self, a, b):
        return self.operation('add', a, b)

    def mul(self, a, b):
        return self.operation('mul', a, b)

    def sum(self, nodes):
        nodes = iter(nodes)
        result = next(nodes)
        for value in nodes:
            result = self.add(result, value)
        return result

    def evaluate_square_zero(self):
        """Exact generic-B evaluation with separately counted scalar overhead.

        Coordinates store coefficients in Q[B]. x_j^2=0. Sparse coordinate
        compilation counts each actual coefficient add/multiply, including
        multiplication by constants, while leaving structural zeros uncomputed.
        """
        values = []
        compiled_gates = 0
        stats = {'peak_coordinates': 0, 'coefficient_multiplications': 0,
                 'coefficient_additions': 0}
        for node in self.nodes:
            tag = node[0]
            if tag == 'constant':
                value = sp.Rational(node[1].numerator, node[1].denominator)
                current = {0: value} if value else {}
            elif tag == 'weight':
                current = {0: self.symbols[node[1]]}
            elif tag == 'occupancy':
                current = {1 << node[1]: sp.Integer(1)}
            elif tag == 'add':
                current = values[node[1]].copy()
                for mask, value in values[node[2]].items():
                    if mask in current:
                        current[mask] = sp.expand(current[mask]+value)
                        compiled_gates += 1
                        stats['coefficient_additions'] += 1
                    else:
                        current[mask] = value
                current = {mask: value for mask, value in current.items() if value != 0}
            elif tag == 'mul':
                current = {}
                for left_mask, left in values[node[1]].items():
                    for right_mask, right in values[node[2]].items():
                        if left_mask & right_mask:
                            continue
                        mask = left_mask | right_mask
                        term = sp.expand(left*right)
                        compiled_gates += 1
                        stats['coefficient_multiplications'] += 1
                        if mask in current:
                            current[mask] = sp.expand(current[mask]+term)
                            compiled_gates += 1
                            stats['coefficient_additions'] += 1
                        else:
                            current[mask] = term
                current = {mask: value for mask, value in current.items() if value != 0}
            else:
                raise ValueError(tag)
            stats['peak_coordinates'] = max(stats['peak_coordinates'], len(current))
            values.append(current)
        stats['compiled_scalar_gates'] = compiled_gates
        stats['native_scalar_gates_in_B_and_x'] = self.gates
        stats['safe_dense_quotient_compilation_bound'] = self.gates*(1 << (2*self.n))
        return values, stats


def matrix_product(dag, a, b):
    n = len(a)
    return [[dag.sum(dag.mul(a[i][k], b[k][j]) for k in range(n))
             for j in range(n)] for i in range(n)]


def build_reciprocal_recurrence(n):
    """D(y,x)=det(I-y diag(x)B), H=1/D; output all h_0,...,h_n."""
    if n < 2:
        raise ValueError('n>=2 is required')
    dag = RationalDAG(n)
    x = [dag.occupancy(i) for i in range(n)]
    T = [[dag.mul(x[i], dag.weight(i, j)) for j in range(n)] for i in range(n)]
    power = T
    traces = [None]
    for k in range(1, n+1):
        traces.append(dag.sum(power[i][i] for i in range(n)))
        if k < n:
            power = matrix_product(dag, T, power)
    d = [dag.constant(1)]
    for k in range(1, n+1):
        total = dag.sum(dag.mul(d[k-j], traces[j]) for j in range(1, k+1))
        d.append(dag.mul(dag.constant(Fraction(-1, k)), total))
    h = [dag.constant(1)]
    for k in range(1, n+1):
        total = dag.sum(dag.mul(d[j], h[k-j]) for j in range(1, k+1))
        h.append(dag.mul(dag.constant(-1), total))
    expected = (n-1)*(2*n**3-n*n)+4*n*n+n
    assert dag.gates == expected
    return dag, d, h, traces, {
        'order': n, 'initial_data': 'h_0=1, h_negative=0',
        'native_scalar_gates': expected,
        'formula': '(n-1)*(2*n^3-n^2)+4*n^2+n',
        'integer_denominators': list(range(1, n+1)),
        'original_marker_substitution_gates': 2*n*n-1,
        'coefficient_extraction_charged_separately': True}


def permutation_sign(sigma):
    return (-1)**sum(sigma[i] > sigma[j]
                    for i in range(len(sigma)) for j in range(i+1, len(sigma)))


def permanent_on_subset(symbols, n, subset):
    if not subset:
        return sp.Integer(1)
    return sp.expand(sum(prod(symbols[i*n+j] for i, j in zip(subset, sigma))
                         for sigma in permutations(subset)))


def determinant_on_subset(symbols, n, subset):
    if not subset:
        return sp.Integer(1)
    return sp.expand(sum(permutation_sign(tuple(subset.index(j) for j in sigma))
                         * prod(symbols[i*n+j] for i, j in zip(subset, sigma))
                         for sigma in permutations(subset)))


def check_reciprocal(n):
    dag, d_nodes, h_nodes, _, construction = build_reciprocal_recurrence(n)
    values, stats = dag.evaluate_square_zero()
    determinant_checks = []
    reciprocal_checks = []
    for k in range(n+1):
        expected_d = {}
        expected_h = {}
        for subset in combinations(range(n), k):
            mask = sum(1 << i for i in subset)
            expected_d[mask] = (-1)**k*determinant_on_subset(dag.symbols, n, subset)
            expected_h[mask] = permanent_on_subset(dag.symbols, n, subset)
        determinant_checks.append(values[d_nodes[k]] == expected_d)
        reciprocal_checks.append(values[h_nodes[k]] == expected_h)
    full = (1 << n)-1
    final = values[h_nodes[n]][full]
    central = permanent_on_subset(dag.symbols, n, tuple(range(n)))
    return {
        'n': n, 'determinant_coefficients_exact': all(determinant_checks),
        'reciprocal_coordinates_exact': all(reciprocal_checks),
        'generic_permanent_exact': sp.expand(final-central) == 0,
        'generic_weight_variables': n*n,
        'output_monomials': len(sp.Poly(final, *dag.symbols).terms()),
        'construction': construction, 'evaluation': stats,
        'd_coordinate_counts': [len(values[node]) for node in d_nodes],
        'h_coordinate_counts': [len(values[node]) for node in h_nodes],
        'newton_recurrence': 'd_k=-(1/k)*sum_(j=1)^k d_(k-j)*tr(T^j)',
        'reciprocal_recurrence': 'h_k=-sum_(j=1)^min(n,k) d_j*h_(k-j)'}


def label_normalization(n):
    """Verify the entire generic-weight determinant pair under lawful relabeling.

    Generic B amplitude monomials are keyed by their permutation. No univariate
    Hhat scalar-DAG baseline or numerical z-specialization is run.
    """
    C = n*(n-1)//2
    K = n**n-1
    shift = 2*C
    divisor = n-1
    normalized_center = K//divisor-n
    q = [(n**i-1)//divisor for i in range(n)]
    perms = list(permutations(range(n)))
    labels = {s: sum(s[i]*n**i for i in range(n)) for s in perms}
    labels_new = {s: sum(s[i]*q[i] for i in range(n)) for s in perms}
    original, recovered = defaultdict(int), defaultdict(int)
    centered, centered_new = defaultdict(int), defaultdict(int)
    for sigma in perms:
        for tau in perms:
            sign = permutation_sign(sigma)*permutation_sign(tau)
            exponent = K+labels[sigma]-labels[tau]
            new_exponent = normalized_center+labels_new[sigma]-labels_new[tau]
            original[exponent, sigma] += sign
            recovered[shift+divisor*new_exponent, sigma] += sign
            if exponent == K:
                centered[sigma] += sign
            if new_exponent == normalized_center:
                centered_new[sigma] += sign
    expected = {sigma: 1 for sigma in perms}
    return {'n': n, 'K': K, 'shift': shift, 'divisor': divisor,
            'normalized_center': normalized_center, 'row_weights': q,
            'all_generic_weight_coefficients_exact': dict(original) == dict(recovered),
            'central_generic_permanent_exact': dict(centered) == dict(centered_new) == expected,
            'formula': 'H(t)=t^(n*(n-1))*H_normalized(t^(n-1))',
            'normalized_label_identity_exact':
                all(labels[s] == C+divisor*labels_new[s] for s in perms),
            'amplitude_monomials': len(perms), 'pair_terms_checked': len(perms)**2}

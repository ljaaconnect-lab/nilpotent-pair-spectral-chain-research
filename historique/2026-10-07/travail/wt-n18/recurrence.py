"""Positive, exact marked-permanent transfer constructions.

Matrices and circuits use only scalar rational/z leaves and binary +/* gates.
Sparse support is structural; z is always formal. No conjecture proof is claimed.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import permutations
from collections import defaultdict
import candidate


def transfer_matrix(dag, entries):
    """Row-oriented transitions S -> S union {j}; full state loops with weight 1."""
    n = len(entries)
    full = (1 << n)-1
    matrix = {}
    for mask in range(full):
        row = mask.bit_count()
        for j in range(n):
            if not mask & (1 << j):
                matrix[mask, mask | (1 << j)] = entries[row][j]
    matrix[full, full] = dag.constant(1)
    return matrix


def sparse_matrix_product(dag, left, right):
    """Count every scalar multiplication/addition, omitting structural zeros."""
    right_rows = defaultdict(list)
    for (k, j), value in sorted(right.items()):
        right_rows[k].append((j, value))
    terms = defaultdict(list)
    multiplications = 0
    for (i, k), value in sorted(left.items()):
        for j, other in right_rows[k]:
            terms[i, j].append(dag.mul(value, other))
            multiplications += 1
    output = {key: dag.sum(values) for key, values in sorted(terms.items())}
    additions = sum(len(values)-1 for values in terms.values())
    return output, {'left_support': len(left), 'right_support': len(right),
                    'output_support': len(output),
                    'multiplications': multiplications, 'additions': additions,
                    'gates': multiplications+additions}


def build_matrix_power(A, exponent=None):
    A = candidate.check_matrix(A)
    n = len(A)
    exponent = n**n-1 if exponent is None else exponent
    if not isinstance(exponent, int) or exponent < n:
        raise ValueError('The stabilizing construction requires an integer exponent >=n')
    dag = candidate.DAG()
    entries = candidate.marked_entries(dag, A)
    construction_gates = dag.gates
    original = transfer_matrix(dag, entries)
    powered = original
    power = 1
    products = []
    for bit in bin(exponent)[3:]:
        powered, stats = sparse_matrix_product(dag, powered, powered)
        power *= 2
        products.append({'operation': 'square', 'exponent': power, **stats})
        if bit == '1':
            powered, stats = sparse_matrix_product(dag, powered, original)
            power += 1
            products.append({'operation': 'multiply_base', 'exponent': power, **stats})
    full = (1 << n)-1
    output = powered[0, full]
    r = 1 << n
    floor_log = exponent.bit_length()-1
    actual_products = floor_log+exponent.bit_count()-1
    assert len(products) == actual_products
    assert dag.gates == construction_gates+sum(x['gates'] for x in products)
    stats = {'dimension': r, 'exponent': exponent,
             'base_support': len(original), 'final_support': len(powered),
             'marker_and_entry_gates': construction_gates,
             'matrix_product_gates': sum(x['gates'] for x in products),
             'matrix_products': actual_products,
             'dense_exact_product_upper_bound':
                 construction_gates+actual_products*(2*r**3-r**2),
             'dense_two_log_upper_bound':
                 construction_gates+2*floor_log*(2*r**3-r**2),
             'products': products}
    return dag, output, stats


def build_row_chain(A):
    """Forward row-vector updates through the n chronological transfer layers."""
    A = candidate.check_matrix(A)
    n = len(A)
    dag = candidate.DAG()
    entries = candidate.marked_entries(dag, A)
    vector = {0: dag.constant(1)}
    layers = []
    for row in range(n):
        terms = defaultdict(list)
        for mask, value in sorted(vector.items()):
            assert mask.bit_count() == row
            for j in range(n):
                if not mask & (1 << j):
                    terms[mask | (1 << j)].append(dag.mul(value, entries[row][j]))
        multiplications = sum(len(xs) for xs in terms.values())
        additions = sum(len(xs)-1 for xs in terms.values())
        vector = {mask: dag.sum(xs) for mask, xs in sorted(terms.items())}
        layers.append({'row': row, 'states': len(vector),
                       'multiplications': multiplications, 'additions': additions})
    expected_gates = 2*n*n+(n-1)*(1 << n)
    assert dag.gates == expected_gates
    return dag, vector[(1 << n)-1], {
        'dimension': 1 << n, 'layers': layers,
        'peak_active_states': max(layer['states'] for layer in layers),
        'marker_and_entry_gates': 2*n*n-1,
        'transition_gates': sum(x['multiplications']+x['additions'] for x in layers),
        'total_gate_formula': '2*n^2+(n-1)*2^n',
        'tensor_description':
            'T_i=sum_j b_ij R_j; R_j=I tensor ... tensor [[0,1],[0,0]] tensor ... tensor I'}


def exact_output(dag, output):
    polynomial, stats = dag.evaluate(output)
    assert all(te == 0 for te, ze in polynomial)
    return {ze: coefficient for (te, ze), coefficient in polynomial.items()}, stats


def reference_marked_permanent(A):
    """Independent factorial permutation oracle, formal z throughout."""
    A = candidate.check_matrix(A)
    n = len(A)
    result = {}
    for sigma in permutations(range(n)):
        coefficient = Fraction(1)
        exponent = 0
        for i, j in enumerate(sigma):
            coefficient *= 1+A[i][j]**2
            exponent += 1 << (i*n+j)
        result[exponent] = result.get(exponent, Fraction(0))+coefficient
    return result


def tensor_product_polynomial(A):
    """Square-zero product of n linear row forms, preserving each marked z exponent.

    This is an exact sparse tensor-algebra evaluation, not a scalar circuit
    compression. Tensor state labels are the same subsets as the row chain.
    """
    A = candidate.check_matrix(A)
    n = len(A)
    coordinates = {0: {0: Fraction(1)}}
    layers = []
    for i in range(n):
        following = defaultdict(dict)
        for mask, polynomial in coordinates.items():
            for j in range(n):
                bit = 1 << j
                if mask & bit:
                    continue
                destination = following[mask | bit]
                amplitude = 1+A[i][j]**2
                address = 1 << (i*n+j)
                for exponent, value in polynomial.items():
                    new_exp = exponent+address
                    destination[new_exp] = destination.get(new_exp, Fraction(0))+value*amplitude
        coordinates = dict(following)
        layers.append({'row': i, 'tensor_coordinates': len(coordinates),
                       'formal_z_terms': sum(map(len, coordinates.values()))})
    return coordinates[(1 << n)-1], {
        'ambient_tensor_dimension': 1 << n, 'layers': layers,
        'scalar_gate_bound_if_compiled_by_subset_dp': 2*n*n+(n-1)*(1 << n),
        'operator_factors': n*n,
        'polynomial_compression_established': False}

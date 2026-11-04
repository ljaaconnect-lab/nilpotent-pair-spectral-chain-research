"""Exact finite verification of the differential fusion repair and its closure.

Column-multilinear X polynomials use a tuple of row indices, one per column.
This is an audit representation, not a claimed efficient scalar compiler.
"""
import json
from itertools import permutations, product
from math import comb
from pathlib import Path


def parity(p):
    return (-1)**sum(p[i] > p[j] for i in range(len(p)) for j in range(i+1, len(p)))


def add(a, b, scalar=1):
    out = dict(a)
    for monomial, coefficient in b.items():
        out[monomial] = out.get(monomial, 0)+scalar*coefficient
    return {m: c for m, c in out.items() if c}


def scale(a, scalar):
    return {m: c*scalar for m, c in a.items() if c*scalar}


def generator(poly, i, j, column):
    out = {}
    for monomial, coefficient in poly.items():
        if monomial[column] == j:
            new = monomial[:column]+(i,)+monomial[column+1:]
            out[new] = out.get(new, 0)+coefficient
    return {m: c for m, c in out.items() if c}


def polarization(poly, i, j, b, second_weight_row=None):
    out = {}
    for k in range(len(b)):
        coefficient = b[j][k]
        if second_weight_row is not None:
            coefficient *= b[second_weight_row][k]
        out = add(out, generator(poly, i, j, k), coefficient)
    return out


def check_commutators(n):
    b = [[1+(i*n+j+1)**2 for j in range(n)] for i in range(n)]
    states = list(product(range(n), repeat=n))
    checked = 0
    for i, j, ell, m in product(range(n), repeat=4):
        for state in states:
            poly = {state: 1}
            left = add(polarization(polarization(poly, ell, m, b), i, j, b),
                       polarization(polarization(poly, i, j, b), ell, m, b), -1)
            right = {}
            if j == ell:
                right = add(right, polarization(poly, i, m, b, second_weight_row=j))
            if m == i:
                right = add(right, polarization(poly, ell, j, b, second_weight_row=m), -1)
            assert left == right
            checked += 1
    return {'n': n, 'basis_states': n**n, 'commutator_actions_checked': checked}


def check_cyclic_module(n):
    determinant = {p: parity(p) for p in permutations(range(n))}
    diagonal = determinant
    for k in range(n):
        diagonal = generator(diagonal, k, k, k)
    assert diagonal == {tuple(range(n)): 1}
    for desired in product(range(n), repeat=n):
        poly = diagonal
        for k in range(n):
            poly = generator(poly, desired[k], k, k)
        assert poly == {desired: 1}
    return {'n': n, 'independent_reachable_monomials': n**n,
            'maximum_constructed_word_length': 2*n}


def check_double_determinant(n):
    # Work formally in all B cells: bit masks label distinct B monomials.
    source = {p: (parity(p), sum(1 << (row*n+column) for column, row in enumerate(p)))
              for p in permutations(range(n))}
    answer = {}
    for derivative in permutations(range(n)):
        for monomial, (coefficient, b_mask) in source.items():
            # Every column has one variable; this is exactly the differential
            # action, with factorials all equal to one.
            if monomial == derivative:
                answer[b_mask] = answer.get(b_mask, 0)+parity(derivative)*coefficient
    assert len(answer) == len(source) and all(c == 1 for c in answer.values())
    return {'n': n, 'formal_B_monomials': len(answer), 'all_coefficients': 1}


def check_naive_capelli_shift():
    b = [[2, 3], [5, 7]]
    det_x = {(0, 1): 1, (1, 0): -1}
    checked = 0
    examples = []
    for q in range(-2, 5):
        for state in product(range(2), repeat=2):
            f = {state: 1}
            e22 = polarization(f, 1, 1, b)
            left = add(polarization(e22, 0, 0, b), scale(e22, q))
            left = add(left, polarization(polarization(f, 0, 1, b), 1, 0, b), -1)
            value = 0
            if state == (0, 1):
                value = b[0][0]*b[1][1]
            if state == (1, 0):
                value = -b[1][0]*b[0][1]
            right = scale(det_x, value)
            defect = add(left, right, -1)
            predicted = {}
            for k in range(2):
                predicted = add(predicted, generator(f, 1, 1, k), b[1][k]*(q-b[0][k]))
            assert defect == predicted
            checked += 1
            if (q, state) in [(2, (0, 1)), (3, (1, 0))]:
                examples.append({'q': q, 'input_rows_by_column': state,
                                 'defect_coefficient_of_input': defect.get(state, 0)})
    return {'matrix': b, 'operator_actions_checked': checked, 'examples': examples}


def main():
    out = {'double_determinant': [check_double_determinant(n) for n in range(1, 6)],
           'commutators': [check_commutators(n) for n in range(2, 5)],
           'cyclic_modules': [check_cyclic_module(n) for n in range(2, 6)],
           'naive_capelli_shift': check_naive_capelli_shift(),
           'canonical_derivative_minor_states': [{'n': n, 'states': comb(2*n, n)} for n in range(1, 13)],
           'dev_score': None}
    Path('differential_repair_checks.json').write_text(json.dumps(out, indent=2), encoding='utf8')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()

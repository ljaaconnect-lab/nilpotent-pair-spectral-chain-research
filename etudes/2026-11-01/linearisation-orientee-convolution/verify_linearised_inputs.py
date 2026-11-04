"""Check actual scalar coefficient circuits and their oriented interpretation.

Nilpotent dictionaries and monomial tables below are small-case reference
evaluators only. They are not used by the scalar input compiler.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from math import factorial, prod
from pathlib import Path
import random

from linearised_inputs import compile_linearised_inputs, DAG_FOLDER
from verify_shared_operator_dag import evaluate_formal_z, polynomial_add


def add_dictionary(p, q, Q):
    out = dict(p)
    for key, value in q.items():
        value = (out.get(key, 0) + value) % Q
        if value:
            out[key] = value
        else:
            out.pop(key, None)
    return out


def scale_dictionary(p, value, Q):
    return {key: coefficient*value % Q for key, coefficient in p.items()
            if coefficient*value % Q}


def multiply_nil(p, q, Q):
    """Reference multiplication: keys are (orientation mask, formal z exponent)."""
    out = {}
    for (a, e), u in p.items():
        for (b, f), v in q.items():
            if not a & b:
                key = (a | b, e + f)
                out[key] = (out.get(key, 0) + u*v) % Q
    return {key: value for key, value in out.items() if value}


def fourier_orientations(n, N, omega, Q):
    return [{(1 << j, 0): pow(omega, r*j, Q) for j in range(n)}
            for r in range(N)]


def evaluate_nil(dag, roots, a, z, transformed_orientations, formal_z=False):
    values = {}
    for index in sorted(dag.reachable(roots)):
        node = dag.nodes[index]
        if node[0] == 'c':
            values[index] = {(0, 0): node[1]} if node[1] else {}
        elif node[0] == 'v':
            name = node[1]
            if name.startswith('x_'):
                values[index] = transformed_orientations[int(name[2:])]
            elif name == 'z':
                values[index] = {(0, 1): 1} if formal_z else ({(0, 0): z} if z else {})
            else:
                _, i, j = name.split('_')
                value = a[int(i)][int(j)] % dag.Q
                values[index] = {(0, 0): value} if value else {}
        elif node[0] == '+':
            values[index] = add_dictionary(values[node[1]], values[node[2]], dag.Q)
        else:
            values[index] = multiply_nil(values[node[1]], values[node[2]], dag.Q)
    return [values[root] for root in roots]


def dual_polynomial(n, N, omega, Q):
    out = {(0,)*N: 1}
    for j in range(n):
        nxt = {}
        for exponent, coefficient in out.items():
            for r in range(N):
                target = list(exponent)
                target[r] += 1
                target = tuple(target)
                nxt[target] = (nxt.get(target, 0) + coefficient*pow(omega, r*j, Q)) % Q
        out = {key: value for key, value in nxt.items() if value}
    return out


def verify_algebra(n, N, omega, Q, rng):
    x = fourier_orientations(n, N, omega, Q)
    inverse_N = pow(N, -1, Q)
    for t in range(N):
        relation = {}
        for r in range(N):
            relation = add_dictionary(relation, multiply_nil(x[r], x[(t-r) % N], Q), Q)
        assert relation == {}, (n, 'convolution', t)
    for j in range(N):
        inverse = {}
        for r in range(N):
            inverse = add_dictionary(inverse,
                                     scale_dictionary(x[r], inverse_N*pow(omega, -r*j, Q), Q), Q)
        assert inverse == ({(1 << j, 0): 1} if j < n else {}), (n, 'inverse', j)
    dual = dual_polynomial(n, N, omega, Q)
    top = (1 << n)-1
    for _ in range(20):
        frequencies = [rng.randrange(N) for _ in range(n)]
        reference = {(0, 0): 1}
        for r in frequencies:
            reference = multiply_nil(reference, x[r], Q)
        exponent = tuple(frequencies.count(r) for r in range(N))
        reader = dual.get(exponent, 0)*prod(factorial(k) for k in exponent) % Q
        assert reader == reference.get((top, 0), 0)
    return x, {'n': n, 'N': N, 'convolution_relations': N,
               'inverse_or_padding_relations': N,
               'dual_monomials_checked': 20, 'status': 'passed'}


def reference_scalar_formal(a, Q):
    n = len(a)
    result = {}
    for columns in itertools.permutations(range(n)):
        coefficient, exponent = 1, 0
        for i, j in enumerate(columns):
            coefficient = coefficient*(1+a[i][j]**2) % Q
            exponent += 2**(i*n+j)
        result = polynomial_add(result, {exponent: coefficient}, Q)
    return result


def check_oriented_table(values, scalar_polynomial, n, N, omega, labels, Q):
    top = (1 << n)-1
    spectral = []
    for f, oriented in enumerate(values):
        assert all(mask == top for mask, exponent in oriented)
        read = {exponent: coefficient for (mask, exponent), coefficient in oriented.items()}
        expected = scale_dictionary(scalar_polynomial, pow(omega, f*sum(labels), Q), Q)
        assert read == expected, (n, f, 'spectral coefficient')
        spectral.append(read)
    table = []
    for k in range(N):
        result = {}
        for f in range(N):
            result = add_dictionary(result,
                                    scale_dictionary(spectral[f],
                                                     pow(N, -1, Q)*pow(omega, -f*k, Q), Q), Q)
        table.append(result)
    expected = [{} for _ in range(N)]
    expected[sum(labels) % N] = scalar_polynomial
    assert table == expected


def verify_case(n, N, omega, mode, labels, x, rng):
    Q = 97
    dag, F, C, info = compile_linearised_inputs(n, Q, N, omega, labels)
    coefficient_roots = [value for row in C for frequency in row for value in frequency]
    numeric_coefficients = ordinary_forms = oriented_tables = formal_coefficients = formal_tables = 0
    for sample in range(3):
        a = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
        if sample == 1:
            a[0] = [22]*n
        z = 0 if sample == 0 else rng.randrange(1, Q)
        B = [[(1+a[i][j]**2)*pow(z, 2**(i*n+j), Q) % Q
              for j in range(n)] for i in range(n)]
        inputs = {f'a_{i}_{j}': a[i][j] for i in range(n) for j in range(n)} | {'z': z}
        expected = [pow(N, -1, Q)*sum(B[i][j]*pow(omega, f*labels[j]+r*j, Q)
                                     for j in range(n)) % Q
                    for i in range(n) for f in range(N) for r in range(N)]
        assert dag.evaluate(coefficient_roots, inputs) == expected
        numeric_coefficients += 1

        # Evaluate the ordinary polynomial representatives at arbitrary scalar x.
        x_values = [rng.randrange(Q) for _ in range(N)]
        q_values = [pow(N, -1, Q)*sum(x_values[r]*pow(omega, -r*j, Q)
                                     for r in range(N)) % Q for j in range(n)]
        ordinary_expected = [prod(sum(B[i][j]*q_values[j]*pow(omega, f*labels[j], Q)
                                      for j in range(n)) % Q for i in range(n)) % Q
                             for f in range(N)]
        assert dag.evaluate(F, inputs | {f'x_{r}': value for r, value in enumerate(x_values)}) == ordinary_expected
        ordinary_forms += 1

        scalar_formal = reference_scalar_formal(a, Q)
        scalar = sum(coefficient*pow(z, exponent, Q)
                     for exponent, coefficient in scalar_formal.items()) % Q
        values = evaluate_nil(dag, F, a, z, x)
        check_oriented_table(values, {0: scalar} if scalar else {},
                             n, N, omega, labels, Q)
        oriented_tables += 1

        if n == 3 and sample == 2:
            coefficient_formal_expected = []
            for i in range(n):
                for f in range(N):
                    for r in range(N):
                        polynomial = {}
                        for j in range(n):
                            coefficient = (pow(N, -1, Q)*(1+a[i][j]**2)
                                           *pow(omega, f*labels[j]+r*j, Q)) % Q
                            polynomial = polynomial_add(polynomial, {2**(i*n+j): coefficient}, Q)
                        coefficient_formal_expected.append(polynomial)
            assert evaluate_formal_z(dag, coefficient_roots, a) == coefficient_formal_expected
            formal_coefficients += 1
            formal_values = evaluate_nil(dag, F, a, z, x, formal_z=True)
            check_oriented_table(formal_values, scalar_formal, n, N, omega, labels, Q)
            formal_tables += 1
    info.update({'label_mode': mode, 'status': 'passed',
                 'numeric_coefficient_tables': numeric_coefficients,
                 'ordinary_polynomial_tables': ordinary_forms,
                 'oriented_complete_tables': oriented_tables,
                 'formal_z_coefficient_tables': formal_coefficients,
                 'formal_z_oriented_tables': formal_tables,
                 'zero_z_checked': True, 'zero_amplitude_row_checked': True})
    return info


def main():
    here = Path(__file__).resolve().parent
    project = here.parents[2]
    sources = [here/'FORME_LINEARISEE.md', here/'linearised_inputs.py',
               here/'verify_linearised_inputs.py', DAG_FOLDER/'shared_operator_dag.py',
               DAG_FOLDER/'verify_shared_operator_dag.py']
    def hashes():
        return {path.relative_to(project).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sources}
    initial_hashes = hashes()
    rng = random.Random(20261101)
    cases, algebra_checks = [], []
    for n in range(3, 7):
        N, Q = 1 << (n-1).bit_length(), 97
        omega = next(w for w in range(1, Q)
                     if pow(w, N, Q) == 1 and pow(w, N//2, Q) != 1)
        x, algebra = verify_algebra(n, N, omega, Q, rng)
        algebra_checks.append(algebra)
        for mode, labels in [('natural', list(range(n))), ('zero', [0]*n),
                             ('irregular', [(j*j+2*j+1) % N for j in range(n)])]:
            result = verify_case(n, N, omega, mode, labels, x, rng)
            cases.append(result)
            print(json.dumps({key: result[key] for key in (
                'n', 'N', 'label_mode', 'coefficient_scalar_gates',
                'polynomial_representative_scalar_gates', 'status')}), flush=True)
    assert initial_hashes == hashes(), 'A checked source changed during the run'
    totals = {key: sum(case[key] for case in cases) for key in (
        'numeric_coefficient_tables', 'ordinary_polynomial_tables', 'oriented_complete_tables',
        'formal_z_coefficient_tables', 'formal_z_oriented_tables')}
    report = {
        'status': 'passed', 'source_sha256': initial_hashes,
        'cases': cases, 'algebra_checks': algebra_checks, 'totals': totals,
        'coefficient_preparation_polynomial_bound_proved': True,
        'ordinary_representative_polynomial_bound_proved': True,
        'complete_scalar_Z_compiled': False,
        'general_polynomial_quotient_reader_established': False,
        'compiler_uses_subset_or_jet_tables': False,
        'reference_evaluators_use_small_monomial_and_subset_tables': True,
        'lean_formalization_of_this_construction': False,
    }
    (here/'linearised-inputs-validation.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': 'passed', 'totals': totals}))


if __name__ == '__main__':
    main()

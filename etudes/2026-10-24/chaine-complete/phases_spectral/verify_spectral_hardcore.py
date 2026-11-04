"""Exact checks of the hard-core compression and uniform Schur proposal."""
import json
from fractions import Fraction
from itertools import combinations, permutations
from math import comb, factorial, prod
from pathlib import Path
from random import Random

from dag import DAG, length
from spectral_hardcore import build_banded, build_tridiagonal, observable_graph, raw_graph


def permanent(b):
    n = len(b)
    return sum(prod(b[i][p[i]] for i in range(n)) for p in permutations(range(n)))


def injection_sum(b, a, stop):
    states = {0: 1}
    n = len(b)
    for row in range(a, stop):
        new = {}
        for mask, value in states.items():
            for j in range(n):
                if not mask >> j & 1:
                    target = mask | (1 << j)
                    new[target] = new.get(target, 0)+value*b[row][j]
        states = new
    return sum(states.values())


def uniform_schur_parameters(b):
    """Exact audit implementation; general injection_sum is exponential."""
    n = len(b)
    moments = {(a, a): Fraction(1) for a in range(n+1)}
    kappa = {}
    for size in range(1, n+1):
        for a in range(n-size+1):
            stop = a+size
            moments[a, stop] = Fraction(comb(n-size, a), comb(n, stop))*injection_sum(b, a, stop)
            kappa[a, stop] = moments[a, stop]-sum(kappa[a, c]*moments[c, stop] for c in range(a+1, stop))
    reconstructed = [Fraction(1)]
    for stop in range(1, n+1):
        reconstructed.append(sum(reconstructed[a]*kappa[a, stop] for a in range(stop)))
    assert reconstructed[-1] == permanent(b)
    return moments, kappa


def apply_layer(b, row, vector):
    out = {}
    for mask, value in vector.items():
        for j in range(len(b)):
            if not mask >> j & 1:
                target = mask | (1 << j)
                out[target] = out.get(target, 0)+b[row][j]*value
    return out


def direct_excursion(b, a, stop):
    n = len(b)
    states = {sum(1 << j for j in chosen): Fraction(1) for chosen in combinations(range(n), a)}
    for row in range(a, stop):
        states = apply_layer(b, row, states)
        if row+1 < stop:
            average = sum(states.values())/comb(n, row+1)
            states = {sum(1 << j for j in chosen): states.get(sum(1 << j for j in chosen), 0)-average
                      for chosen in combinations(range(n), row+1)}
    return sum(states.values())/comb(n, stop)


def check_uniform_schur():
    rng = Random(20261024)
    rows = []
    for n in range(1, 7):
        b = [[1+rng.randrange(8)**2 for _ in range(n)] for _ in range(n)]
        moments, kappa = uniform_schur_parameters(b)
        composition_terms = 0
        for (a, stop), value in kappa.items():
            assert value == direct_excursion(b, a, stop)
            expanded = Fraction(0)
            for cuts in range(1 << (stop-a-1)):
                endpoints = [a]+[a+j+1 for j in range(stop-a-1) if cuts >> j & 1]+[stop]
                term = prod(moments[left, right] for left, right in zip(endpoints, endpoints[1:]))
                expanded += (-1)**cuts.bit_count()*term
                composition_terms += 1
            assert value == expanded
            if stop == a+1:
                assert value == Fraction(a+1, n)*sum(b[a])
            if stop == a+2:
                gram = sum(x*y for x, y in zip(b[a], b[a+1]))
                formula = Fraction((a+1)*(a+2), n*(n-1))*(Fraction(sum(b[a])*sum(b[a+1]), n)-gram)
                assert value == formula
        rows.append({'n': n, 'excursions_checked': len(kappa),
                     'all_order_composition_terms_checked': composition_terms,
                     'full_weight': str(moments[0, n]),
                     'longest_excursion': str(kappa[0, n])})
    return rows


def check_pair_closure_counterexample():
    b = [[1, 17, 10, 26], [1, 1, 37, 37], [26, 17, 1, 10], [1, 10, 17, 26]]
    c = [[10, 26, 1, 17], [37, 37, 1, 1], [10, 1, 17, 26], [17, 26, 1, 10]]
    legal = {1+a*a for a in range(8)}
    assert all(x in legal for matrix in [b, c] for row in matrix for x in row)
    assert [sum(row) for row in b] == [sum(row) for row in c]
    gram = lambda matrix: [[sum(x*y for x, y in zip(row, other)) for other in matrix] for row in matrix]
    assert gram(b) == gram(c)
    bm, bk = uniform_schur_parameters(b)
    cm, ck = uniform_schur_parameters(c)
    assert all(bk[key] == ck[key] for key in bk if key[1]-key[0] <= 2)
    assert bm[0, 4] != cm[0, 4]
    return {'B': b, 'C': c, 'row_sums': [sum(row) for row in b], 'shared_gram': gram(b),
            'per_B': str(bm[0, 4]), 'per_C': str(cm[0, 4]),
            'B_excursions': {f'{a}:{stop}': str(value) for (a, stop), value in bk.items()},
            'C_excursions': {f'{a}:{stop}': str(value) for (a, stop), value in ck.items()}}


def apply_graph(vertices, edges, b, vector, left=False):
    out = {v: 0 for v in vertices}
    for source, target, row, column in edges:
        if left:
            out[source] += b[row][column]*vector[target]
        else:
            out[target] += b[row][column]*vector[source]
    return out


def check_krylov():
    rows = []
    for n in range(1, 6):
        b = [[1+(i+2*j+1)**2 for j in range(n)] for i in range(n)]
        vertices, edges = raw_graph(n)
        e0 = {v: int(v == 0) for v in vertices}
        rights, lefts = [e0], [e0]
        for _ in range(n):
            rights.append(apply_graph(vertices, edges, b, rights[-1]))
            lefts.append(apply_graph(vertices, edges, b, lefts[-1], left=True))
        target = permanent(b)
        assert rights[n] == {v: target*int(v == 0) for v in vertices}
        gram = [[sum(lefts[n-i][v]*rights[j][v] for v in vertices) for j in range(n)] for i in range(n)]
        assert gram == [[target*int(i == j) for j in range(n)] for i in range(n)]
        rows.append({'n': n, 'target': target, 'gram': gram})
    return rows


def characteristic_coefficients(vertices, edges, weights, prime):
    # Sparse-left Faddeev-LeVerrier over a finite field; exact characteristic
    # polynomial verification, not a development evaluator or eigenvalue oracle.
    d = len(vertices)
    index = {v: i for i, v in enumerate(vertices)}
    previous = [[int(i == j) for j in range(d)] for i in range(d)]
    coefficients = [1]
    for k in range(1, d+1):
        current = [[0]*d for _ in range(d)]
        for source, target, row, column in edges:
            src, dst, weight = index[source], index[target], weights[row][column]
            for j in range(d):
                current[dst][j] = (current[dst][j]+weight*previous[src][j]) % prime
        coefficient = -sum(current[i][i] for i in range(d))*pow(k, -1, prime) % prime
        coefficients.append(coefficient)
        for i in range(d):
            current[i][i] = (current[i][i]+coefficient) % prime
        previous = current
    return coefficients


def reference_polynomial(n, inputs, width, prime):
    result = {}
    for p in permutations(range(n)):
        if any(abs(i-j) > width for i, j in enumerate(p)):
            continue
        exponent = sum(1 << (i*n+j) for i, j in enumerate(p))
        coefficient = prod(inputs['p', i, j] for i, j in enumerate(p)) % prime
        assert exponent not in result
        if coefficient:
            result[exponent] = coefficient
    return result


def check_compilers():
    rng, prime = Random(20261024), 65537
    records = []
    for n in range(1, 9):
        for width, method in [(1, 'tridiagonal'), (1, 'frontier'), (2, 'frontier')]:
            N = length(n)
            labels = [rng.randrange(-2*N, 2*N+1) for _ in range(n)]
            dag = DAG()
            outputs = build_tridiagonal(n, labels, dag) if method == 'tridiagonal' else build_banded(n, labels, dag, width)
            if method == 'tridiagonal':
                assert dag.gates == (1 if n == 1 else n*n+7*n-8)
            row = {'n': n, 'width': width, 'method': method, 'gates': dag.gates,
                   'numeric_tables': 0, 'formal_tables': 0}
            for case in range(8):
                inputs = {('p', i, j): 1+rng.randrange(-6, 7)**2 for i in range(n) for j in range(n)}
                inputs['z'] = [0, 1, prime-1, rng.randrange(prime)][case % 4]
                polynomial = reference_polynomial(n, inputs, width, prime)
                expected = [0]*N
                expected[sum(labels) % N] = sum(c*pow(inputs['z'], e, prime) for e, c in polynomial.items()) % prime
                assert dag.evaluate_all(outputs, inputs, prime) == expected
                row['numeric_tables'] += 1
                if case in (1, 3):
                    formal = [{} for _ in range(N)]
                    formal[sum(labels) % N] = polynomial
                    assert dag.evaluate_polynomials(outputs, inputs, prime) == formal
                    row['formal_tables'] += 1
            records.append(row)
    return records


def check_spectra():
    prime = 65537
    records = []
    for n in range(1, 7):
        N = length(n)
        labels = [2*i-3 for i in range(n)]
        omega = pow(3, (prime-1)//N, prime)
        inputs = {('p', i, j): 1+(i+j+1)**2 for i in range(n) for j in range(n)}
        for width in (1, 2):
            polynomial = reference_polynomial(n, inputs, width, prime)
            target = sum(c*pow(7, e, prime) for e, c in polynomial.items()) % prime
            reduced_v, reduced_e = observable_graph(n, width)
            if width == 1:
                assert len(reduced_v) == 2*n-1
            if width == 2 and n >= 4:
                assert len(reduced_v) == 6*n-11
            for frequency in sorted({0, 1, N-1}):
                weights = [[inputs['p', i, j]*pow(7, 1 << (i*n+j), prime)
                            *pow(omega, frequency*labels[j] % N, prime) % prime for j in range(n)] for i in range(n)]
                for kind, (vertices, edges) in [('raw', raw_graph(n, width)), ('reduced', (reduced_v, reduced_e))]:
                    coefficients = characteristic_coefficients(vertices, edges, weights, prime)
                    expected = [1]+[0]*len(vertices)
                    expected[n] = -target*pow(omega, frequency*sum(labels) % N, prime) % prime
                    assert coefficients == expected
            records.append({'n': n, 'width': width, 'raw_vertices': (1 << n)-1,
                            'reduced_vertices': len(reduced_v), 'reduced_edges': len(reduced_e),
                            'frequencies_checked': len({0, 1, N-1})})
    return records


def main():
    records = check_compilers()
    result = {'compilers': records, 'spectral_characteristic_checks': check_spectra(),
              'uniform_schur': check_uniform_schur(), 'krylov_normalization': check_krylov(),
              'pair_closure_counterexample': check_pair_closure_counterexample(),
              'dev_score': None, 'frozen_development_evaluator_run': False}
    Path('spectral_hardcore_checks.json').write_text(json.dumps(result, indent=2), encoding='utf8')
    print(json.dumps({'numeric_tables': sum(r['numeric_tables'] for r in records),
                      'formal_tables': sum(r['formal_tables'] for r in records),
                      'n8_compilers': [r for r in records if r['n'] == 8],
                      'spectra': result['spectral_characteristic_checks'],
                      'pair_counterexample': {'per_B': result['pair_closure_counterexample']['per_B'],
                                              'per_C': result['pair_closure_counterexample']['per_C']}}, indent=2))


if __name__ == '__main__':
    main()

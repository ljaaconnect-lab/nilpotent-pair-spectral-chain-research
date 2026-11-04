"""Finite exact probes for weighted sums of signed-cell determinants.

These do not assume a bounded Fourier extension on unused scores.
Four independent +/-1 term vectors have only two possible absolute weight
patterns, obtained by exhaustive exact four-by-four linear algebra below.
"""
import argparse
import json
from collections import Counter
from fractions import Fraction
from itertools import permutations, product
from math import factorial
from pathlib import Path

from ortools.sat.python import cp_model


def solve_square(matrix, target):
    n = len(target)
    a = [[Fraction(x) for x in row]+[Fraction(t)] for row, t in zip(matrix, target)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j]), None)
        if pivot is None:
            return None
        a[j], a[pivot] = a[pivot], a[j]
        q = a[j][j]
        a[j] = [x/q for x in a[j]]
        for i in range(n):
            if i != j and a[i][j]:
                q = a[i][j]
                a[i] = [x-q*y for x, y in zip(a[i], a[j])]
    return [a[j][-1] for j in range(n)]


def weight_classes(size):
    counts = Counter()
    # Row signs make target all +1; column signs make the first row all +1.
    # Both transformations preserve the multiset of absolute coefficients.
    for bits in product((-1, 1), repeat=size*(size-1)):
        matrix = [[1]*size]+[list(bits[size*i:size*i+size]) for i in range(size-1)]
        answer = solve_square(matrix, [1]*size)
        if answer is not None and all(answer):
            counts[tuple(sorted(abs(x) for x in answer))] += 1
    expected = {1: {(Fraction(1),)}, 2: set(), 3: {(Fraction(1),)*3},
                4: {(Fraction(1, 2),)*4, (Fraction(1),)*3+(Fraction(2),)}}
    assert set(counts) == expected[size]
    return [{'absolute_weights': [str(x) for x in weights], 'normalized_matrices': count}
            for weights, count in sorted(counts.items())]


def parity(p):
    return sum(p[i] > p[j] for i in range(len(p)) for j in range(i+1, len(p))) % 2


def probe(n, seconds):
    # The (1/2,1/2,1/2,1/2) case is excluded at n=5 by
    # (n!)^2 <= n^n * L * sum c_t^2. Test the other exact class.
    assert factorial(n)**2 > 4*n**n
    weights = [1, 1, 1, 2]
    model = cp_model.CpModel()
    zero = model.new_constant(0)
    phases = [[[zero if i == 0 or j == 0 else model.new_bool_var(f'r_{t}_{i}_{j}')
                for j in range(n)] for i in range(n)] for t in range(4)]
    global_bits = [model.new_bool_var(f'global_{t}') for t in range(4)]
    for number, p in enumerate(permutations(range(n))):
        bits = [model.new_bool_var(f'value_{t}_{number}') for t in range(4)]
        for t in range(4):
            model.add_bool_xor([phases[t][i][p[i]] for i in range(n)]
                               + [global_bits[t], bits[t].Not()])
        desired = 3 if parity(p) else 2
        model.add(sum(w*b for w, b in zip(weights, bits)) == desired)
    assert not model.validate(), model.validate()
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 4
    solver.parameters.random_seed = 20261024
    status = solver.solve(model)
    result = {'n': n, 'weights': weights, 'status': solver.status_name(status),
              'time_seconds': solver.wall_time, 'branches': solver.num_branches,
              'conflicts': solver.num_conflicts}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        labels = [[[solver.value(x) for x in row] for row in matrix] for matrix in phases]
        signs = [(-1)**solver.value(x) for x in global_bits]
        for p in permutations(range(n)):
            total = sum(weights[t]*signs[t]*(-1)**sum(labels[t][i][p[i]] for i in range(n))
                        for t in range(4))
            assert total == (-1)**parity(p)
        result.update(phases=labels, coefficient_signs=signs)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, default=5)
    parser.add_argument('--seconds', type=float, default=20)
    parser.add_argument('--output', default='unbounded_phase_probe.json')
    args = parser.parse_args()
    result = {'independent_term_weight_classes': {str(k): weight_classes(k) for k in range(1, 5)},
              'probe': probe(args.n, args.seconds)}
    Path(args.output).write_text(json.dumps(result, indent=2), encoding='utf8')
    print(json.dumps(result, indent=2))

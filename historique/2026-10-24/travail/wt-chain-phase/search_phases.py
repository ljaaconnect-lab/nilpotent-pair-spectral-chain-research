"""Bounded CP-SAT search for sign-separating additive cell scores.

No output here is a general construction; a returned matrix is exhaustively
checked against every permutation of the requested finite size.
"""
import argparse
import json
from itertools import permutations
from pathlib import Path
from ortools.sat.python import cp_model


def parity(p):
    return sum(p[i] > p[j] for i in range(len(p)) for j in range(i+1, len(p))) % 2


def solve(n, kind, size, seconds):
    model = cp_model.CpModel()
    colors = [model.new_bool_var(f'color_{x}') for x in range(size)]
    zero = model.new_constant(0)
    if kind == 'cyclic':
        matrix = [[zero if i == 0 or j == 0 else model.new_int_var(0, size-1, f'r_{i}_{j}')
                   for j in range(n)] for i in range(n)]
        for number, p in enumerate(permutations(range(n))):
            score = model.new_int_var(0, size-1, f's_{number}')
            total = model.new_int_var(0, n*(size-1), f't_{number}')
            model.add(total == sum(matrix[i][p[i]] for i in range(n)))
            model.add_modulo_equality(score, total, size)
            model.add_element(score, colors, parity(p))
    else:
        bits = size.bit_length()-1
        assert size == 1 << bits
        matrix_bits = [[[zero if i == 0 or j == 0 else model.new_bool_var(f'r_{i}_{j}_{k}')
                         for k in range(bits)] for j in range(n)] for i in range(n)]
        for number, p in enumerate(permutations(range(n))):
            score_bits = [model.new_bool_var(f's_{number}_{k}') for k in range(bits)]
            for k in range(bits):
                model.add_bool_xor([matrix_bits[i][p[i]][k] for i in range(n)] + [score_bits[k].Not()])
            score = model.new_int_var(0, size-1, f's_{number}')
            model.add(score == sum((1 << k)*score_bits[k] for k in range(bits)))
            model.add_element(score, colors, parity(p))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 4
    solver.parameters.random_seed = 20261024
    assert not model.validate(), model.validate()
    status = solver.solve(model)
    result = {'n': n, 'group': kind, 'size': size, 'status': solver.status_name(status),
              'time_seconds': solver.wall_time, 'conflicts': solver.num_conflicts,
              'branches': solver.num_branches}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        if kind == 'cyclic':
            labels = [[solver.value(v) for v in row] for row in matrix]
        else:
            labels = [[sum((1 << k)*solver.value(matrix_bits[i][j][k]) for k in range(bits))
                       for j in range(n)] for i in range(n)]
        signs = [(-1) ** solver.value(v) for v in colors]
        support = {0: set(), 1: set()}
        for p in permutations(range(n)):
            if kind == 'cyclic':
                score = sum(labels[i][p[i]] for i in range(n)) % size
            else:
                score = 0
                for i in range(n):
                    score ^= labels[i][p[i]]
            support[parity(p)].add(score)
            assert signs[score] == (-1) ** parity(p)
        result.update(labels=labels, chi=signs, supports={k: sorted(v) for k,v in support.items()})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('n', type=int)
    parser.add_argument('kind', choices=['cyclic', 'xor'])
    parser.add_argument('sizes', type=int, nargs='+')
    parser.add_argument('--seconds', type=float, default=15)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    results = []
    for size in args.sizes:
        result = solve(args.n, args.kind, size, args.seconds)
        results.append(result)
        print(json.dumps(result), flush=True)
        Path(args.output).write_text(json.dumps(results, indent=2), encoding='utf8')

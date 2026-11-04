"""Exact finite checks for two restricted proposed state representations.

The failures concern these specified representations only.  They establish
neither a general lower bound nor impossibility of the requested circuit.
The Hankel example specializes the original marker z to 1 explicitly.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path


PRIME = 17


def rank_mod(matrix, prime=PRIME):
    work = [[entry % prime for entry in row] for row in matrix]
    rank = 0
    for column in range(len(work[0])):
        pivot = next((row for row in range(rank, len(work)) if work[row][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [entry * inverse % prime for entry in work[rank]]
        for row in range(len(work)):
            if row != rank:
                factor = work[row][column]
                work[row] = [(x - factor * y) % prime for x, y in zip(work[row], work[rank])]
        rank += 1
    return rank


def determinant_mod(matrix, prime=PRIME):
    work = [[entry % prime for entry in row] for row in matrix]
    size = len(work)
    determinant = 1
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = -determinant
        value = work[column][column]
        determinant = determinant * value % prime
        inverse = pow(value, -1, prime)
        for row in range(column + 1, size):
            factor = work[row][column] * inverse % prime
            for col in range(column, size):
                work[row][col] = (work[row][col] - factor * work[column][col]) % prime
    return determinant % prime


def outer(left, right):
    return [[x * y % PRIME for y in right] for x in left]


def hadamard(left, right):
    return [[x * y % PRIME for x, y in zip(a, b)] for a, b in zip(left, right)]


def skew(left, right):
    return [[(left[i] * right[j] - right[i] * left[j]) % PRIME
             for j in range(len(left))] for i in range(len(left))]


def weight_matrix(original_a):
    return [[1 + value * value for value in row] for row in original_a]


def verify_determinantal_family():
    n = 5
    u, v = [1, 2, 3, 4, 5], [2, 5, 1, 7, 3]
    r, s = [1, 4, 2, 3, 7], [3, 1, 8, 2, 6]
    p, q = skew(u, v), skew(r, s)
    actual = hadamard(p, q)
    vector_product = lambda x, y: [a * b % PRIME for a, b in zip(x, y)]
    four_terms = [
        outer(vector_product(u, r), vector_product(v, s)),
        outer(vector_product(u, s), vector_product(v, r)),
        outer(vector_product(v, r), vector_product(u, s)),
        outer(vector_product(v, s), vector_product(u, r)),
    ]
    expanded = [[(four_terms[0][i][j] - four_terms[1][i][j]
                  - four_terms[2][i][j] + four_terms[3][i][j]) % PRIME
                 for j in range(n)] for i in range(n)]
    assert actual == expanded
    assert (rank_mod(p), rank_mod(q), rank_mod(actual)) == (2, 2, 4)

    equal_directions = [[0 if i == j else 2 for j in range(n)] for i in range(n)]
    assert rank_mod(equal_directions) == 5
    assert determinant_mod(equal_directions) == 9  # 2^5 * 4 modulo 17

    # A positive first step: all maximal minors of U have square one.
    # Cauchy--Binet therefore gives det(U^T diag(x) U) = e_4(x).
    compression = [[int(i == j) for j in range(n - 1)] for i in range(n - 1)]
    compression.append([-1] * (n - 1))
    first_coefficients = []
    for omitted in range(n):
        minor = [row for index, row in enumerate(compression) if index != omitted]
        first_coefficients.append(pow(determinant_mod(minor), 2, PRIME))
    assert first_coefficients == [1] * n

    # Two DISTINCT legal directions, completed to an invertible input matrix.
    # This also permits treating the five row linear forms as independent.
    original_a = [
        [0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 2, 0, 0, 1],
        [0, 3, 0, 0, 0],
        [0, 1, 0, 0, 0],
    ]
    weights = weight_matrix(original_a)
    first = [row[0] for row in weights]
    second = [row[1] for row in weights]
    mixed = [[0 if i == j else (first[i] * second[j] + first[j] * second[i]) % PRIME
              for j in range(n)] for i in range(n)]
    assert rank_mod(weights) == n
    assert rank_mod(mixed) == n

    return {
        "status": "restricted_family_counterexample_verified",
        "scope": "Only the family det(U^T diag(x) V), with U,V of size n by n-2 and independent x_i, is excluded for these second derivatives. No general circuit lower bound is asserted.",
        "mathematical_reason": "Cauchy--Binet and complementary minors would require the coefficient matrix to equal p Hadamard q for two decomposable skew matrices. The displayed four-outer-product identity forces rank at most 4 over any extension of F_17.",
        "n": n,
        "Q": PRIME,
        "z_specialization": 1,
        "positive_first_step": {
            "identity": "D_(1,...,1) product_i x_i = e_4(x) = det(U^T diag(x) U)",
            "U": compression,
            "squared_maximal_minors": first_coefficients,
        },
        "four_outer_product_formula": "(u wedge v) Hadamard (r wedge s) = (u*r)(v*s)^T - (u*s)(v*r)^T - (v*r)(u*s)^T + (v*s)(u*r)^T",
        "decomposable_sample": {
            "u": u, "v": v, "r": r, "s": s,
            "p": p, "q": q, "hadamard_product": actual,
            "ranks": [rank_mod(p), rank_mod(q), rank_mod(actual)],
        },
        "equal_direction_target": {
            "identity": "D_1 D_1 product_i x_i = 2 e_3(x)",
            "complementary_coefficient_matrix": equal_directions,
            "rank": rank_mod(equal_directions),
            "determinant_mod_Q": determinant_mod(equal_directions),
        },
        "distinct_legal_directions": {
            "original_a": original_a,
            "B_at_z_1": weights,
            "input_rank": rank_mod(weights),
            "directions": [first, second],
            "complementary_coefficient_matrix": mixed,
            "rank": rank_mod(mixed),
            "determinant_mod_Q": determinant_mod(mixed),
        },
    }


def polynomial_multiply(left, right):
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return result


def observation_curve(weights):
    n = len(weights)
    result = [1]
    leading = 1
    for row in weights:
        slope = row[1] + row[2]
        result = polynomial_multiply(result, [row[0], slope])
        leading *= slope
    result[n] -= leading
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def product_of_row_forms(weights, point):
    result = 1
    for row in weights:
        result *= sum(entry * parameter for entry, parameter in zip(row, point))
    return result


def terminal_difference(weights):
    """Finite verification only; this expansion is not a proposed compiler."""
    n = len(weights)
    return sum((-1) ** (n - sum(point)) * product_of_row_forms(weights, point)
               for point in product((0, 1), repeat=n))


def permutation_oracle(weights):
    answer = 0
    for assignment in permutations(range(len(weights))):
        term = 1
        for row, column in enumerate(assignment):
            term *= weights[row][column]
        answer += term
    return answer


def verify_hankel_curve():
    original_a = [[0, 0, 1], [1, 0, 1], [2, 1, 0]]
    original_a_prime = [[2, 0, 1], [1, 0, 1], [0, 1, 0]]
    b = weight_matrix(original_a)
    b_prime = weight_matrix(original_a_prime)
    assert all(row[1:] == other[1:] for row, other in zip(b, b_prime))
    curve, curve_prime = observation_curve(b), observation_curve(b_prime)
    assert curve == curve_prime == [10, 51, 72]
    readings = [terminal_difference(b), terminal_difference(b_prime)]
    oracle = [permutation_oracle(b), permutation_oracle(b_prime)]
    assert readings == oracle == [35, 39]
    hankel = [[curve[i + j] if i + j < len(curve) else 0 for j in range(3)] for i in range(3)]
    assert [value % PRIME for value in readings] == [1, 5]
    return {
        "status": "restricted_state_counterexample_verified",
        "scope": "Only a state retaining this one scalar observation curve (equivalently all its coefficients/Hankel data) plus the unchanged future columns is refuted, at z=1. States retaining the full formal z information or additional directional observations are not refuted.",
        "n": 3,
        "Q": PRIME,
        "z_specialization": 1,
        "spectral_labels": [0, 0, 0],
        "original_a": [original_a, original_a_prime],
        "B_at_z_1": [b, b_prime],
        "curve_definition": "h(t) = Delta_e0 G(t(e1+e2)) = product_i(B_i0+t*(B_i1+B_i2)) - product_i(t*(B_i1+B_i2))",
        "equal_curve_coefficients_ascending": curve,
        "equal_curve_coefficients_mod_Q": [value % PRIME for value in curve],
        "equal_Hankel_matrix": hankel,
        "future_columns_are_equal": True,
        "full_terminal_differences": readings,
        "independent_permutation_oracle": oracle,
        "full_terminal_differences_mod_Q": [value % PRIME for value in readings],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    source = Path(__file__).resolve()
    initial_hash = sha256(source.read_bytes()).hexdigest()
    report = {
        "status": "passed",
        "scope": "Exact counterexamples to two stated restricted candidates; not a proof of impossibility of a general polynomial scalar circuit.",
        "source_sha256": {source.name: initial_hash},
        "determinantal_compression": verify_determinantal_family(),
        "hankel_observation": verify_hankel_curve(),
        "verified_utc": datetime.now(timezone.utc).isoformat(),
    }
    assert sha256(source.read_bytes()).hexdigest() == initial_hash, "Source changed during verification"
    if args.write_report:
        source.with_name("candidate-validation.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps({
        "status": report["status"],
        "source_sha256": report["source_sha256"],
        "hadamard_rank": report["determinantal_compression"]["decomposable_sample"]["ranks"][-1],
        "target_ranks": [report["determinantal_compression"][name]["rank"]
                         for name in ("equal_direction_target", "distinct_legal_directions")],
        "equal_hankel_curve": report["hankel_observation"]["equal_curve_coefficients_ascending"],
        "terminal_readings": report["hankel_observation"]["full_terminal_differences"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

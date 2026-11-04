"""Exact finite examples of the degree obstruction for incidence deformations.

This is an exhaustive coefficient oracle for small n, not a polynomial compiler.
All polynomials are formal in T over F_p.  Their exponents are never reduced
modulo p-1.  The script uses only the Python standard library.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from time import perf_counter


Poly = tuple[int, ...]
ZERO: Poly = ()
ONE: Poly = (1,)


def normal(coefficients: list[int] | tuple[int, ...], p: int) -> Poly:
    out = [a % p for a in coefficients]
    while out and out[-1] == 0:
        out.pop()
    return tuple(out)


def add(a: Poly, b: Poly, p: int) -> Poly:
    out = [0] * max(len(a), len(b))
    for i, value in enumerate(a):
        out[i] += value
    for i, value in enumerate(b):
        out[i] += value
    return normal(out, p)


def scale(a: Poly, b: int, p: int) -> Poly:
    return normal([x * b for x in a], p)


def mul(a: Poly, b: Poly, p: int) -> Poly:
    if not a or not b:
        return ZERO
    if len(a) == 1:
        return scale(b, a[0], p)
    if len(b) == 1:
        return scale(a, b[0], p)
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return normal(out, p)


def power(a: Poly, exponent: int, p: int) -> Poly:
    out = ONE
    for _ in range(exponent):
        out = mul(out, a, p)
    return out


def evaluate(a: Poly, t: int, p: int) -> int:
    result = 0
    for coefficient in reversed(a):
        result = (result * t + coefficient) % p
    return result


def degree(a: Poly) -> int:
    return len(a) - 1


def identity(n: int) -> list[list[Poly]]:
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def matmul(a: list[list[Poly]], b: list[list[Poly]], p: int) -> list[list[Poly]]:
    n = len(a)
    out = [[ZERO for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                out[i][j] = add(out[i][j], mul(a[i][k], b[k][j], p), p)
    return out


def permutation_sign(sigma: tuple[int, ...]) -> int:
    inversions = sum(
        sigma[i] > sigma[j] for i in range(len(sigma)) for j in range(i + 1, len(sigma))
    )
    return -1 if inversions % 2 else 1


def determinant(matrix: list[list[Poly]], p: int) -> Poly:
    n = len(matrix)
    out = ZERO
    for sigma in itertools.permutations(range(n)):
        term = ONE
        for i, j in enumerate(sigma):
            term = mul(term, matrix[i][j], p)
        out = add(out, scale(term, permutation_sign(sigma), p), p)
    return out


def field_rank(matrix: list[list[int]], p: int) -> int:
    work = [[entry % p for entry in row] for row in matrix]
    rows, columns = len(work), len(work[0])
    rank = 0
    for col in range(columns):
        pivot = next((i for i in range(rank, rows) if work[i][col]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][col], -1, p)
        work[rank] = [(entry * inverse) % p for entry in work[rank]]
        for i in range(rows):
            if i != rank:
                multiplier = work[i][col]
                work[i] = [
                    (a - multiplier * b) % p for a, b in zip(work[i], work[rank])
                ]
        rank += 1
        if rank == rows:
            break
    return rank


def sampling_polynomial(L: int, p: int) -> Poly:
    # rho(0)=1 and rho(t)=0 at the distinct nodes 1,...,L.
    rho = ONE
    for t in range(1, L + 1):
        rho = mul(rho, (1, -pow(t, -1, p)), p)
    return rho


def shear(n: int, a: int, b: int, coefficient: int, exponent: int, p: int):
    assert a != b and exponent >= 1
    matrix = identity(n)
    matrix[a][b] = normal([0] * exponent + [coefficient], p)
    return matrix


def deformation(n: int, r: int, L: int, p: int, variant: str):
    rho = sampling_polynomial(L, p)
    diagonal = [[ZERO for _ in range(n)] for _ in range(n)]
    for j in range(n):
        diagonal[j][j] = rho if j < n - r else ONE
    matrices = []
    for i in range(n):
        u = identity(n)
        if variant == "individual_shears":
            u = matmul(shear(n, i % n, (i + 1) % n, i + 1, 1, p), u, p)
            u = matmul(shear(n, (i + 1) % n, i % n, -(i + 2), 2, p), u, p)
        elif variant == "common_opposite_shears":
            # Multiplication is exact, including cancellations of leading terms.
            a = shear(n, 0, n - 1, 1, 2, p)
            b = shear(n, n - 1, 0, -1, 1, p)
            c = shear(n, 0, n - 1, -1, 2, p)
            u = matmul(matmul(a, b, p), c, p)
        else:
            assert variant == "diagonal"
        assert determinant(u, p) == ONE
        matrices.append(matmul(u, diagonal, p))
    return matrices, rho


def coefficient_tensor(matrices: list[list[list[Poly]]], p: int):
    """Direct expansion of (tensor_i P_i) tau, without degree assumptions."""
    n = len(matrices)
    permutations = list(itertools.permutations(range(n)))
    tensor = {}
    for indices in itertools.product(range(n), repeat=n):
        value = ZERO
        for sigma in permutations:
            term = ONE
            for i in range(n):
                term = mul(term, matrices[i][indices[i]][sigma[i]], p)
                if not term:
                    break
            value = add(value, term, p)
        if value:
            tensor[indices] = value
    return tensor


def verify_spectral(tensor, n: int, p: int = 97):
    """Exact formal coefficient check for phases and a complete INTT table."""
    N = 1 << (n - 1).bit_length()
    omega = pow(5, (p - 1) // N, p)
    assert pow(omega, N, p) == 1
    assert N == 1 or pow(omega, N // 2, p) != 1
    frequencies = []
    for f in range(N):
        frequencies.append({
            indices: scale(value, pow(omega, f * sum(indices), p), p)
            for indices, value in tensor.items()
        })
    inverse_N = pow(N, -1, p)
    outputs = []
    for k in range(N):
        output = {}
        for indices, original in tensor.items():
            value = ZERO
            for f in range(N):
                weight = inverse_N * pow(omega, (-f * k) % N, p)
                value = add(value, scale(frequencies[f][indices], weight, p), p)
            expected = original if sum(indices) % N == k else ZERO
            assert value == expected
            if value:
                output[indices] = value
        outputs.append(output)
    input_degree = max(degree(value) for value in tensor.values())
    output_degree = max(degree(value) for output in outputs for value in output.values())
    assert input_degree == output_degree
    return {
        "n": n, "p": p, "N": N, "omega": omega,
        "input_degree": input_degree, "output_degree": output_degree,
        "coefficient_checks": N * len(tensor),
        "frequencies_checked": N, "INTT_coordinates_checked": N,
    }


def main():
    start = perf_counter()
    records = []
    rank_checks = determinant_checks = sharp_coordinate_checks = tensor_coordinates = 0
    spectral = []
    for n in range(2, 5):
        for r in range(1, n):
            for L in range(1, 4):
                for p in (5, 7, 97):
                    assert p > L
                    for variant in ("diagonal", "individual_shears", "common_opposite_shears"):
                        matrices, rho = deformation(n, r, L, p, variant)
                        expected_det = power(rho, n - r, p)
                        determinant_degrees = []
                        for matrix in matrices:
                            assert all(
                                evaluate(matrix[i][j], 0, p) == (1 if i == j else 0)
                                for i in range(n) for j in range(n)
                            )
                            det = determinant(matrix, p)
                            assert det == expected_det
                            determinant_checks += 1
                            determinant_degrees.append(degree(det))
                            for t in range(1, L + 1):
                                at_node = [[evaluate(entry, t, p) for entry in row] for row in matrix]
                                assert field_rank(at_node, p) == r
                                rank_checks += 1
                        tensor = coefficient_tensor(matrices, p)
                        tensor_coordinates += n ** n
                        h = max(degree(value) for value in tensor.values())
                        assert n * h >= sum(determinant_degrees)
                        assert h >= L * (n - r)
                        raw_degree_bound = sum(
                            max(degree(entry) for row in matrix for entry in row)
                            for matrix in matrices
                        )
                        assert h <= raw_degree_bound
                        if variant == "diagonal":
                            for indices in itertools.product(range(n), repeat=n):
                                expected = expected_det if len(set(indices)) == n else ZERO
                                assert tensor.get(indices, ZERO) == expected
                                sharp_coordinate_checks += 1
                            assert h == L * (n - r)
                        if p == 97 and r == 1 and L == 2:
                            spectral.append({"variant": variant, **verify_spectral(tensor, n, p)})
                        records.append({
                            "n": n, "r": r, "L": L, "p": p, "variant": variant,
                            "actual_degree": h,
                            "lower_bound": L * (n - r),
                            "sum_determinant_degrees": sum(determinant_degrees),
                            "raw_degree_bound": raw_degree_bound,
                            "nonzero_tensor_coordinates": len(tensor),
                        })
    source = Path(__file__).resolve()
    report = {
        "status": "passed",
        "source_file": source.name,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "method": "Exact formal univariate polynomials over finite fields; exhaustive tensor oracle",
        "scope": {
            "general_degree_theorem_proved_by_tests": False,
            "general_degree_theorem_formalized_in_Lean_here": False,
            "polynomial_scalar_compiler_implemented": False,
            "polynomial_deformation_existence_established": False,
            "independent_coefficient_tensor_used_as_validation_oracle_only": True,
            "formal_exponents_preserved": True,
            "exponents_reduced_modulo_p_minus_one": False,
            "all_sampling_nodes_distinct_and_nonzero": True,
            "prime_choices_are_test_parameters_not_a_characteristic_restriction_of_the_theorem": True,
        },
        "counts": {
            "cases": len(records),
            "sharp_diagonal_cases": sum(row["variant"] == "diagonal" for row in records),
            "unimodular_cases": sum(row["variant"] != "diagonal" for row in records),
            "sample_matrix_rank_checks": rank_checks,
            "formal_determinant_checks": determinant_checks,
            "tensor_coordinates_expanded": tensor_coordinates,
            "sharp_identity_coordinates_checked": sharp_coordinate_checks,
            "strict_improvement_over_raw_degree_bound_cases": sum(
                row["actual_degree"] < row["raw_degree_bound"] for row in records
            ),
            "spectral_cases": len(spectral),
            "spectral_coefficient_checks": sum(row["coefficient_checks"] for row in spectral),
        },
        "minimum_degree_slack": min(row["actual_degree"] - row["lower_bound"] for row in records),
        "maximum_actual_degree": max(row["actual_degree"] for row in records),
        "elapsed_seconds": round(perf_counter() - start, 3),
        "spectral_records": spectral,
        "case_records": records,
    }
    output = source.with_name("degree-validation.json")
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "counts": report["counts"],
                      "source_sha256": report["source_sha256"], "report": str(output),
                      "elapsed_seconds": report["elapsed_seconds"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

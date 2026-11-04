"""Local exact checks for the proposed bridge; not the paper's algorithm.

Run with Python 3. All z exponents are Python integers, never residues.
The Boolean, subset and permutation enumerations below are TEST ORACLES.
No general circuit-size claim follows from these finite tests.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
import random


Q = 97
Poly = dict[int, int]


def add(a: Poly, b: Poly) -> Poly:
    c = dict(a)
    for degree, value in b.items():
        c[degree] = (c.get(degree, 0) + value) % Q
        if c[degree] == 0:
            del c[degree]
    return c


def scale(a: Poly, c: int) -> Poly:
    return {degree: value * c % Q for degree, value in a.items()
            if value * c % Q}


def mul(a: Poly, b: Poly) -> Poly:
    c: Poly = {}
    for i, x in a.items():
        for j, y in b.items():
            # Crucial: i+j is an ordinary integer, never reduced modulo 96.
            c[i + j] = (c.get(i + j, 0) + x * y) % Q
    return {degree: value for degree, value in c.items() if value}


def input_matrix(a: list[list[int]]) -> list[list[Poly]]:
    n = len(a)
    return [[scale({1 << (i * n + j): 1}, 1 + a[i][j] ** 2)
             for j in range(n)] for i in range(n)]


def boolean_signed_sum(b: list[list[Poly]]) -> Poly:
    n = len(b)
    answer: Poly = {}
    for bits in itertools.product((0, 1), repeat=n):
        term = {0: 1}
        for row in b:
            row_value: Poly = {}
            for j in range(n):
                if bits[j]:
                    row_value = add(row_value, row[j])
            term = mul(term, row_value)
        answer = add(answer, scale(term, (-1) ** (n - sum(bits))))
    return answer


def oriented_terminal(b: list[list[Poly]]) -> Poly:
    """Oracle in F_97[z,q]/(q_j^2); masks are only test representation."""
    n = len(b)
    state: dict[int, Poly] = {0: {0: 1}}
    for row in b:
        new: dict[int, Poly] = {}
        for mask, coefficient in state.items():
            for j in range(n):
                if not mask & (1 << j):
                    new_mask = mask | (1 << j)
                    new[new_mask] = add(new.get(new_mask, {}),
                                        mul(coefficient, row[j]))
        state = new
    return state.get((1 << n) - 1, {})


def permutation_oracle(b: list[list[Poly]]) -> Poly:
    answer: Poly = {}
    for permutation in itertools.permutations(range(len(b))):
        term = {0: 1}
        for i, j in enumerate(permutation):
            term = mul(term, b[i][j])
        answer = add(answer, term)
    return answer


def primitive_root(order: int) -> int:
    for w in range(1, Q):
        if pow(w, order, Q) == 1 and all(pow(w, k, Q) != 1
                                            for k in range(1, order)):
            return w
    raise AssertionError(f"No root of order {order}")


def check_oriented_spectral() -> dict:
    counts = {"input_matrices": 0, "base_boolean_identities": 0,
              "permutation_cross_checks": 0, "spectral_configurations": 0,
              "frequency_identities": 0, "intt_output_coordinates": 0,
              "universal_sign_checks": 0}
    max_exponent = 0
    profiles = ("zero", "one", "affine", "zero_diagonal_weights")
    for n in range(1, 5):
        for profile in profiles:
            if profile == "zero":
                a = [[0] * n for _ in range(n)]
            elif profile == "one":
                a = [[1] * n for _ in range(n)]
            elif profile == "affine":
                a = [[(17 * i + 11 * j + 3) % Q for j in range(n)]
                     for i in range(n)]
            else:
                # 22^2 = -1 mod 97: tests exact vanishing of some B_ij.
                a = [[22 if i == j else 0 for j in range(n)]
                     for i in range(n)]
            b = input_matrix(a)
            direct = oriented_terminal(b)
            assert boolean_signed_sum(b) == direct
            assert permutation_oracle(b) == direct
            counts["input_matrices"] += 1
            counts["base_boolean_identities"] += 1
            counts["permutation_cross_checks"] += 1
            max_exponent = max(max_exponent, max(direct, default=0))
            # q0...q(n-1) in the e0...e(n-1)f0...f(n-1) basis.
            order = [x for j in range(n) for x in (j, n + j)]
            inversions = sum(order[i] > order[j] for i in range(2 * n)
                             for j in range(i + 1, 2 * n))
            gamma = (-1) ** (n * (n - 1) // 2)
            assert (-1) ** inversions == gamma
            assert scale(direct, gamma * (-1) ** inversions) == direct
            counts["universal_sign_checks"] += 1
            minimum = 1 << (n - 1).bit_length()
            for length in (minimum, 2 * minimum):
                omega = primitive_root(length)
                for labels in (list(range(n)), [(3 * j * j + 2) % length
                                                 for j in range(n)]):
                    frequencies = []
                    for f in range(length):
                        modulated = [[scale(b[i][j],
                                            pow(omega, f * labels[j], Q))
                                      for j in range(n)] for i in range(n)]
                        oriented = oriented_terminal(modulated)
                        signed = boolean_signed_sum(modulated)
                        assert signed == oriented
                        assert oriented == scale(direct,
                                                 pow(omega, f * sum(labels), Q))
                        frequencies.append(signed)
                        counts["frequency_identities"] += 1
                    for k in range(length):
                        output: Poly = {}
                        for f, coefficient in enumerate(frequencies):
                            factor = pow(omega, (-f * k) % length, Q)
                            output = add(output, scale(coefficient, factor))
                        output = scale(output, pow(length, -1, Q))
                        expected = direct if k == sum(labels) % length else {}
                        assert output == expected
                        counts["intt_output_coordinates"] += 1
                    counts["spectral_configurations"] += 1
    assert max_exponent > Q - 1
    return {**counts, "n_values": [1, 2, 3, 4], "field_modulus": Q,
            "matrix_profiles": list(profiles), "ntt_lengths": [1, 2, 4, 8],
            "largest_verified_output_exponent": max_exponent,
            "z_is_formal": True, "z_exponents_reduced_mod_Q_minus_1": False,
            "all_checks_passed": True}


def evaluate(coefficients: list[int], x: int, p: int) -> int:
    answer = 0
    for coefficient in reversed(coefficients):
        answer = (answer * x + coefficient) % p
    return answer


def reader(coefficients: list[int], length: int, p: int) -> int:
    return sum((-1) ** (t - 1) * math.comb(length, t)
               * evaluate(coefficients, t, p)
               for t in range(1, length + 1)) % p


def check_reader() -> dict:
    rng = random.Random(20261102)
    valid_count = 0
    valid_with_repeated_nodes = 0
    degree_boundary_checks = 0
    boundary_failures = []
    boundary_accidental_equalities = []
    primes = [2, 3, 5, 7, 97]
    for p in primes:
        for length in range(1, 13):
            cases = [[0] * degree + [1] for degree in range(length)]
            cases.extend([[rng.randrange(p) for _ in range(length)]
                          for _ in range(3)])
            for coefficients in cases:
                assert evaluate(coefficients, 0, p) == reader(coefficients, length, p)
                valid_count += 1
                valid_with_repeated_nodes += int(p <= length)
            # Outside the stated degree bound, T^L has defect (-1)^(L+1)L!.
            boundary = [0] * length + [1]
            defect = reader(boundary, length, p) - evaluate(boundary, 0, p)
            defect %= p
            assert defect == ((-1) ** (length + 1) * math.factorial(length)) % p
            degree_boundary_checks += 1
            case = {"p": p, "L": length, "reader_minus_H0": defect}
            if defect:
                boundary_failures.append(case)
            else:
                boundary_accidental_equalities.append(case)
    assert boundary_failures and boundary_accidental_equalities
    return {"formula": "H(0)=sum(t=1..L) (-1)^(t-1) binom(L,t) H(t)",
            "required_hypothesis": "formal degree(H) < L",
            "primes": primes, "L_values": list(range(1, 13)),
            "valid_degree_cases": valid_count,
            "valid_cases_with_p_at_most_L": valid_with_repeated_nodes,
            "degree_equal_L_cases": degree_boundary_checks,
            "degree_equal_L_failures": len(boundary_failures),
            "degree_equal_L_accidental_equalities": len(boundary_accidental_equalities),
            "counterexamples": boundary_failures,
            "boundary_note": "For H=T^L and p<=L, L! vanishes modulo p; these cases do not disprove the formula. Cases p>L exhibit the missing degree hypothesis.",
            "no_inversion_of_node_differences_required": True,
            "all_checks_passed": True}


def check_gadget() -> dict:
    table = []
    for a, b, c in itertools.product((0, 1), repeat=3):
        value = ((1 - a) * (1 - b) * (1 - c)
                 + (a + b - 2 * a * b) * c)
        expected = int(c == a + b)
        assert value == expected
        table.append({"a": a, "b": b, "c": c, "T": value})
    weight_cases = 0
    for coefficient in (0, 1, 17, 96):
        for bit in (0, 1):
            value = (1 + (coefficient - 1) * bit) % Q
            assert value == (coefficient if bit else 1)
            weight_cases += 1
    return {"formula": "T(a,b,c)=(1-a)(1-b)(1-c)+(a+b-2ab)c",
            "accepted_bit_strings": ["000", "011", "101"],
            "truth_table_cases": len(table), "truth_table": table,
            "weight_formula": "1+(B_ij-1)x_ij",
            "weight_cases": weight_cases, "all_checks_passed": True}


def main() -> None:
    path = Path(__file__).resolve()
    report = {
        "scope": "Finite local exact checks for an oriented/spectral bridge; no implementation or validation of the paper's main algorithm.",
        "source_file": path.name,
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "oriented_spectral": check_oriented_spectral(),
        "finite_difference_reader": check_reader(),
        "local_gadget": check_gadget(),
        "flags": {
            "local_identities_checked": True,
            "test_oracles_enumerate_boolean_assignments_subsets_and_permutations": True,
            "paper_algorithm_implemented": False,
            "paper_main_theorem_verified": False,
            "lean_verification_performed_by_this_script": False,
            "polynomial_general_scalar_compilation_established": False,
            "complete_chain_polynomial_bound_established": False,
            "new_polynomial_source_for_reader_values_constructed": False,
            "formal_z_exponents_preserved": True,
        },
    }
    output = path.with_name("bridge-validation.json")
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print(json.dumps({"report": str(output), "source_sha256": report["source_sha256"],
                      "oriented_spectral": report["oriented_spectral"],
                      "reader_counts": {key: value for key, value
                                         in report["finite_difference_reader"].items()
                                         if key.endswith("cases") or key.endswith("failures")
                                         or key.endswith("equalities")},
                      "gadget_cases": report["local_gadget"]["truth_table_cases"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()

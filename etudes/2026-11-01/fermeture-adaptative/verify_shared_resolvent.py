"""Exact finite verifier of the shared Schur residual and reader.

This is deliberately NOT a polynomial scalar compiler.  It expands the
square-zero jet algebra into a dictionary with up to 2**k coefficients and
uses permutations for independent small determinant/terminal oracles.
Those operations are verification-only and are counted in the report.

Run with --write-report to replace the sibling JSON report after all checks
pass.  Ordinary runs leave the report unchanged.  Standard library only.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
from random import Random


Jet = dict[int, int]
Matrix = list[list[Jet]]


class JetVerifier:
    """Explicit coefficient arithmetic in F_q[eps]/(eps_i**2)."""

    def __init__(self, prime: int):
        self.prime = prime
        self.counts: Counter[str] = Counter()
        self.max_support = 0

    def record(self, value: Jet) -> Jet:
        result = {mask: x for mask, x in value.items() if x}
        self.max_support = max(self.max_support, len(result))
        return result

    def constant(self, value: int) -> Jet:
        value %= self.prime
        return self.record({0: value}) if value else {}

    def add(self, left: Jet, right: Jet) -> Jet:
        self.counts["jet_add_calls"] += 1
        out = left.copy()
        for mask, value in right.items():
            self.counts["field_additions"] += 1
            out[mask] = (out.get(mask, 0) + value) % self.prime
        return self.record(out)

    def negate(self, value: Jet) -> Jet:
        self.counts["jet_negation_calls"] += 1
        self.counts["field_negations"] += len(value)
        return self.record({mask: -x % self.prime for mask, x in value.items()})

    def multiply(self, left: Jet, right: Jet) -> Jet:
        self.counts["jet_multiply_calls"] += 1
        out: Jet = {}
        for left_mask, left_value in left.items():
            for right_mask, right_value in right.items():
                self.counts["coefficient_pairs_examined"] += 1
                if left_mask & right_mask:
                    self.counts["pairs_killed_by_square_zero"] += 1
                    continue
                self.counts["field_multiplications"] += 1
                self.counts["field_additions"] += 1
                mask = left_mask | right_mask
                out[mask] = (out.get(mask, 0) + left_value * right_value) % self.prime
        return self.record(out)

    def matrix_multiply(self, left: Matrix, right: Matrix) -> Matrix:
        self.counts["matrix_multiply_calls"] += 1
        out = [[{} for _ in right[0]] for _ in left]
        for row in range(len(left)):
            for column in range(len(right[0])):
                for middle in range(len(right)):
                    out[row][column] = self.add(
                        out[row][column],
                        self.multiply(left[row][middle], right[middle][column]),
                    )
        return out

    def nilpotent_inverse(self, value: Matrix, variables: int) -> Matrix:
        """Compute I+A+...+A**variables explicitly; A is in the jet ideal."""
        size = len(value)
        result = [[self.constant(int(i == j)) for j in range(size)] for i in range(size)]
        power = result
        for _ in range(variables):
            power = self.matrix_multiply(power, value)
            result = [
                [self.add(result[i][j], power[i][j]) for j in range(size)]
                for i in range(size)
            ]
        return result

    def permutation_oracle(self, matrix: Matrix, alternating: bool) -> Jet:
        """Small independent terminal/determinant oracle; never a compiler."""
        size = len(matrix)
        out: Jet = {}
        counter = "determinant_permutations" if alternating else "terminal_permutations"
        for permutation in permutations(range(size)):
            self.counts[counter] += 1
            term = self.constant(1)
            for row, column in enumerate(permutation):
                term = self.multiply(term, matrix[row][column])
            if alternating:
                inversions = sum(
                    permutation[i] > permutation[j]
                    for i in range(size)
                    for j in range(i + 1, size)
                )
                if inversions % 2:
                    term = self.negate(term)
            out = self.add(out, term)
        return out


def jet_json(value: Jet) -> list[list[int]]:
    return [[mask, value[mask]] for mask in sorted(value)]


def matrix_json(value: Matrix) -> list[list[list[list[int]]]]:
    return [[jet_json(entry) for entry in row] for row in value]


def canonical_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def verify() -> dict[str, object]:
    rng = Random(792)
    cases: list[dict[str, object]] = []
    totals: Counter[str] = Counter()
    maximum_support = 0
    inputs: list[dict[str, object]] = []

    for prime in (17, 97):
        for size in range(2, 7):
            original = [[rng.randrange(prime) for _ in range(size)] for _ in range(size)]
            inputs.append({"prime": prime, "n": size, "B": original})
            arithmetic = JetVerifier(prime)
            state = [[arithmetic.constant(x) for x in row] for row in original]
            terminal_reference = arithmetic.permutation_oracle(state, alternating=False)
            assert set(terminal_reference) <= {0}
            target = terminal_reference.get(0, 0)
            reader = arithmetic.constant(1)

            for eliminated in range(1, size):
                previous_counts = arithmetic.counts.copy()
                pivot_index = eliminated - 1
                epsilon = {1 << pivot_index: 1}
                pivot = state[pivot_index][pivot_index]
                reader = arithmetic.multiply(
                    reader,
                    arithmetic.add(arithmetic.constant(1), arithmetic.multiply(epsilon, pivot)),
                )
                # All entries on the right use the state before this update.
                state = [
                    [
                        arithmetic.add(
                            state[i][j],
                            arithmetic.multiply(
                                epsilon,
                                arithmetic.multiply(state[i][pivot_index], state[pivot_index][j]),
                            ),
                        )
                        if i >= eliminated and j >= eliminated
                        else state[i][j]
                        for j in range(size)
                    ]
                    for i in range(size)
                ]

                # E multiplies rows here: (E B)_(i,j) = eps_i B_(i,j).
                eb = [
                    [({1 << i: original[i][j]} if original[i][j] else {}) for j in range(eliminated)]
                    for i in range(eliminated)
                ]
                resolvent = arithmetic.nilpotent_inverse(eb, eliminated)
                identity_minus_eb = [
                    [
                        arithmetic.add(arithmetic.constant(int(i == j)), arithmetic.negate(eb[i][j]))
                        for j in range(eliminated)
                    ]
                    for i in range(eliminated)
                ]
                determinant = arithmetic.permutation_oracle(identity_minus_eb, alternating=True)
                assert arithmetic.multiply(reader, determinant) == {0: 1}

                left = [
                    [arithmetic.constant(original[i][j]) for j in range(eliminated)]
                    for i in range(eliminated, size)
                ]
                right = [
                    [({1 << i: original[i][j]} if original[i][j] else {}) for j in range(eliminated, size)]
                    for i in range(eliminated)
                ]
                correction = arithmetic.matrix_multiply(arithmetic.matrix_multiply(left, resolvent), right)
                residual = [row[eliminated:] for row in state[eliminated:]]
                for i in range(eliminated, size):
                    for j in range(eliminated, size):
                        expected = arithmetic.add(
                            arithmetic.constant(original[i][j]),
                            correction[i - eliminated][j - eliminated],
                        )
                        assert state[i][j] == expected

                # Verify the complete composed reader, not just the matrix.
                tail = arithmetic.permutation_oracle(residual, alternating=False)
                observed = arithmetic.multiply(reader, tail).get((1 << eliminated) - 1, 0)
                assert observed == target

                cases.append(
                    {
                        "prime": prime,
                        "n": size,
                        "eliminated": eliminated,
                        "residual": matrix_json(residual),
                        "reader": jet_json(reader),
                        "det_I_minus_EB": jet_json(determinant),
                        "terminal_readout": observed,
                        "terminal_reference": target,
                        "residual_identity_passed": True,
                        "reader_inverse_identity_passed": True,
                        "composed_terminal_readout_passed": True,
                        "verifier_work_this_stage": dict(sorted((arithmetic.counts - previous_counts).items())),
                    }
                )

            totals.update(arithmetic.counts)
            maximum_support = max(maximum_support, arithmetic.max_support)

    assert len(cases) == 30
    source = Path(__file__).resolve()
    return {
        "status": "pass",
        "schema_version": 1,
        "verifier": source.name,
        "source_sha256": sha256(source.read_bytes()).hexdigest(),
        "random_seed": 792,
        "test_cases": len(cases),
        "base_matrices": len(inputs),
        "scope": {
            "algebra": "F_Q[eps_0,...,eps_(k-1)]/(eps_i^2)",
            "matrix_entries": "Generic residues B_ij; the identities also hold after original-amplitude or Fourier-phase substitutions.",
            "residual": "B_SS + B_SK (I - E_K B_KK)^(-1) E_K B_KS",
            "reader": "J_K = product_i (1 + eps_i pivot_i) = det(I - E_K B_KK)^(-1)",
            "terminal": "[product_i eps_i] J_K L(residual), where L is the remaining terminal chain readout",
            "not_a_scalar_polynomial_compiler": True,
            "no_general_scalar_closure_claimed": True,
        },
        "verification_cost": {
            "representation": "Explicit square-zero monomial dictionaries, up to 2^k scalar coefficients per entry.",
            "jet_multiply_bound": "At most 4^k examined coefficient pairs per call; overlapping masks are discarded.",
            "determinant_oracle": "Enumerates k! permutations; used only for finite independent verification.",
            "terminal_oracle": "Enumerates n! or (n-k)! assignments; used only for finite independent verification.",
            "observed_maximum_jet_support": maximum_support,
            "field_negation_cost_convention": "One multiplication by the constant -1 if translated into ordinary scalar gates.",
            "exact_work_counters": dict(sorted(totals.items())),
            "observed_scalar_add_mul_negation_work": totals["field_additions"]
            + totals["field_multiplications"]
            + totals["field_negations"],
            "counter_scope": "Verifier computations including independent oracles; not a bound for a general compiler.",
        },
        "inputs": inputs,
        "cases": cases,
        "case_data_sha256": canonical_hash(cases),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    report = verify()
    if args.write_report:
        path = Path(__file__).resolve().with_name("shared-resolvent-validation.json")
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "test_cases": report["test_cases"],
                "source_sha256": report["source_sha256"],
                "case_data_sha256": report["case_data_sha256"],
                "report_written": args.write_report,
                "not_a_scalar_polynomial_compiler": True,
            }
        )
    )


if __name__ == "__main__":
    main()

"""Exact n=2 example: one projected INTT slot has constant deformation degree.

This validates a small example, not the existence of a general favorable design.
The scalar evaluation starts from a_ij,z; no terminal amplitude is an input.
Coefficient expansions below are validation oracles only. All T and z powers
are formal and are never reduced modulo p-1.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import check_degree_barrier as base


def matrix_at(matrix, t, p):
    return [[base.evaluate(entry, t, p) for entry in row] for row in matrix]


def boolean_coefficient(matrices, indices, p):
    """Coefficient computed independently by the signed Boolean sum."""
    value = base.ZERO
    for bits in itertools.product((0, 1), repeat=2):
        product = base.ONE
        for i in range(2):
            linear = base.ZERO
            for v in range(2):
                linear = base.add(
                    linear, base.scale(matrices[i][indices[i]][v], bits[v], p), p
                )
            product = base.mul(product, linear, p)
        value = base.add(value, base.scale(product, (-1) ** (2 - sum(bits)), p), p)
    return value


def marked_substitution(tensor, p):
    """Substitute B_ij=(1+a_ij^2)z^(2^(2i+j)) as formal polynomials.

    A key is (a_00 exponent,...,a_11 exponent,z exponent); its value is
    a formal polynomial in T. This explicitly checks the original inputs.
    """
    result = {}
    for (j0, j1), coefficient in tensor.items():
        cells = (j0, 2 + j1)
        z_degree = sum(2 ** cell for cell in cells)
        for selected in itertools.product((0, 1), repeat=2):
            exponents = [0] * 4
            for cell, bit in zip(cells, selected):
                exponents[cell] = 2 * bit
            key = (*exponents, z_degree)
            value = base.add(result.get(key, base.ZERO), coefficient, p)
            if value:
                result[key] = value
            else:
                result.pop(key, None)
    return result


def evaluate_from_original_inputs(a, z, p):
    """Small circuit at t=1 followed by INTT_2; no amplitude input."""
    b = [(1 + value * value) * pow(z, 2 ** cell, p) % p
         for cell, value in enumerate(a)]
    frequencies = []
    for f in range(2):
        phase = pow(p - 1, f, p)
        # P_1(1) uses only x_0; P_2(1) uses only x_1.
        first_group = (b[0] + phase * b[1]) % p
        second_group = (b[2] + phase * b[3]) % p
        frequencies.append(first_group * second_group % p)
    inverse_two = pow(2, -1, p)
    outputs = [inverse_two * (frequencies[0] + frequencies[1]) % p,
               inverse_two * (frequencies[0] - frequencies[1]) % p]
    return outputs, b


def main():
    records = []
    counts = {"fields": 0, "formal_tensor_coordinates": 0,
              "signed_boolean_coefficient_checks": 0, "rank_checks": 0,
              "formal_determinants": 0, "INTT_coefficient_checks": 0,
              "formal_marked_output_monomials": 0,
              "original_input_evaluations": 0}
    for p in (5, 7, 97):
        t = (0, 1)
        g = base.normal((0, 3, -2), p)
        rho = base.normal((1, -1), p)
        one_plus_two_t = (1, 2)
        first = [[base.ONE, base.ZERO], [g, rho]]
        second = [[base.mul(rho, one_plus_two_t, p), t],
                  [base.ZERO, base.ONE]]
        matrices = [first, second]
        expected = {(0, 0): t, (0, 1): base.ONE,
                    (1, 0): base.ONE, (1, 1): g}
        for matrix in matrices:
            assert matrix_at(matrix, 0, p) == [[1, 0], [0, 1]]
            assert base.field_rank(matrix_at(matrix, 1, p), p) == 1
            counts["rank_checks"] += 1
        assert matrix_at(first, 1, p) == [[1, 0], [1, 0]]
        assert matrix_at(second, 1, p) == [[0, 1], [0, 1]]
        assert base.determinant(first, p) == rho
        assert base.determinant(second, p) == base.mul(rho, one_plus_two_t, p)
        counts["formal_determinants"] += 2
        tensor = base.coefficient_tensor(matrices, p)
        assert tensor == expected
        counts["formal_tensor_coordinates"] += 4
        for indices, coefficient in expected.items():
            assert boolean_coefficient(matrices, indices, p) == coefficient
            counts["signed_boolean_coefficient_checks"] += 1

        omega = p - 1
        assert omega != 1 and pow(omega, 2, p) == 1
        frequencies = [
            {indices: base.scale(value, pow(omega, f * sum(indices), p), p)
             for indices, value in tensor.items()}
            for f in range(2)
        ]
        inverse_two = pow(2, -1, p)
        outputs = []
        for k in range(2):
            output = {}
            for indices in tensor:
                coefficient = base.ZERO
                for f in range(2):
                    coefficient = base.add(
                        coefficient,
                        base.scale(frequencies[f][indices],
                                   inverse_two * pow(omega, (-f * k) % 2, p), p), p
                    )
                if coefficient:
                    output[indices] = coefficient
                counts["INTT_coefficient_checks"] += 1
            outputs.append(output)
        assert outputs[0] == {(0, 0): t, (1, 1): g}
        assert outputs[1] == {(0, 1): base.ONE, (1, 0): base.ONE}
        output_degrees = [max(map(base.degree, output.values())) for output in outputs]
        assert output_degrees == [2, 0]
        assert max(output_degrees) == max(map(base.degree, tensor.values())) == 2

        marked = [marked_substitution(output, p) for output in outputs]
        assert max(map(base.degree, marked[0].values())) == 2
        assert max(map(base.degree, marked[1].values())) == 0
        assert all(base.evaluate(poly, 0, p) == 0 for poly in marked[0].values())
        # Expected small-case output is an oracle, never an evaluator input.
        assert marked[1] == marked_substitution(
            {(0, 1): base.ONE, (1, 0): base.ONE}, p
        )
        counts["formal_marked_output_monomials"] += sum(map(len, marked))

        for a in itertools.product((0, 1, 2), repeat=4):
            for z in (0, 1, 2, 3):
                actual, b = evaluate_from_original_inputs(a, z, p)
                assert actual[1] == (b[0] * b[3] + b[1] * b[2]) % p
                assert actual[0] == (b[0] * b[2] + b[1] * b[3]) % p
                counts["original_input_evaluations"] += 1
        records.append({
            "p": p, "n": 2, "N": 2, "omega": omega,
            "sampling_points": [1], "L": 1, "s": 1, "mu": 0,
            "groups": [[0], [1]], "factor_group_assignments": [0, 1],
            "P_1": first, "P_2": second,
            "tensor_coefficients": {str(key): value for key, value in tensor.items()},
            "INTT_outputs": [{str(key): value for key, value in output.items()}
                             for output in outputs],
            "output_T_degrees": output_degrees,
            "useful_slot": 1, "useful_slot_degree": 0,
            "whole_table_degree": 2,
            "whole_table_lower_bound_L_times_n_minus_s_minus_mu": 1,
            "sum_determinant_degrees": 3,
            "determinant_degree_inequality": "2*2 >= 1+2",
            "formal_marked_output_T_degrees": [2, 0],
        })
        counts["fields"] += 1
    source = Path(__file__).resolve()
    dependency = Path(base.__file__).resolve()
    report = {
        "status": "passed", "source_file": source.name,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "dependencies": [{"file": dependency.name,
                          "sha256": hashlib.sha256(dependency.read_bytes()).hexdigest()}],
        "method": "Exact formal coefficient identities over F_5, F_7, F_97",
        "scope": {
            "n_is_fixed_at_two": True,
            "general_favorable_deformation_existence_established": False,
            "general_polynomial_scalar_bound_established": False,
            "whole_table_degree_obstruction_contradicted": False,
            "single_slot_projection_precedes_reconstruction": True,
            "scalar_evaluator_inputs": "a_00,a_01,a_10,a_11,z only",
            "terminal_amplitude_is_an_input": False,
            "universal_orientation_sign_absorbed_in_final_basis": True,
            "formal_T_and_z_exponents_preserved": True,
            "exponents_reduced_modulo_p_minus_one": False,
            "coefficient_tensor_expansion_is_validation_oracle_only": True,
            "all_fields_have_odd_characteristic": True,
        },
        "counts": counts, "case_records": records,
    }
    target = source.with_name("single-slot-validation.json")
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "counts": counts,
                      "source_sha256": report["source_sha256"], "report": str(target)},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()

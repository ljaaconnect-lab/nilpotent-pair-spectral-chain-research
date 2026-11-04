"""Independent finite verification from original a,z to the full orbit table.

IMPORTANT: this verifier initializes moments by n**n assignments and checks
finite differences by 2**n evaluations.  Those are verification oracles,
NOT a proposed polynomial initializer I(n,N).  The tested scalar component
collision_observer.py receives the initialized moments explicitly.

All inverse transforms are actually evaluated, without substituting the
known terminal channel.  Formal z is retained for n<=4; numerical cases
include n=5.  Run --write-report to write orbit-bridge-validation.json.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
from random import Random

from collision_observer import compile_observer


Polynomial = dict[int, int]


class PolynomialVerifier:
    def __init__(self, prime: int):
        self.prime = prime
        self.counts: Counter[str] = Counter()

    def add(self, left: Polynomial, right: Polynomial) -> Polynomial:
        self.counts["polynomial_add_calls"] += 1
        out = left.copy()
        for exponent, coefficient in right.items():
            self.counts["field_additions"] += 1
            value = (out.get(exponent, 0) + coefficient) % self.prime
            if value:
                out[exponent] = value
            else:
                out.pop(exponent, None)
        return out

    def scale(self, value: Polynomial, scalar: int) -> Polynomial:
        self.counts["polynomial_scale_calls"] += 1
        scalar %= self.prime
        self.counts["field_multiplications"] += len(value)
        if not scalar:
            return {}
        return {exponent: coefficient * scalar % self.prime for exponent, coefficient in value.items()}

    def multiply(self, left: Polynomial, right: Polynomial) -> Polynomial:
        self.counts["polynomial_multiply_calls"] += 1
        out: Polynomial = {}
        for a, x in left.items():
            for b, y in right.items():
                self.counts["field_multiplications"] += 1
                self.counts["field_additions"] += 1
                exponent = a + b
                coefficient = (out.get(exponent, 0) + x * y) % self.prime
                if coefficient:
                    out[exponent] = coefficient
                else:
                    out.pop(exponent, None)
        return out

    def monomial(self, coefficient: int, exponent: int) -> Polynomial:
        coefficient %= self.prime
        return {exponent: coefficient} if coefficient else {}


def encode(value: Polynomial) -> list[list[int]]:
    return [[exponent, value[exponent]] for exponent in sorted(value)]


def digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def prime_divisors(value: int) -> list[int]:
    out = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            out.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor += 1
    if value > 1:
        out.append(value)
    return out


def field_parameters(prime: int, n: int) -> tuple[int, int, int]:
    assert prime >= 3 and all(prime % divisor for divisor in range(2, int(prime**0.5) + 1))
    h = n * (n - 1) // 2
    length = 1 << n.bit_length()
    assert prime > max(2, h) and (prime - 1) % length == 0
    factors = prime_divisors(prime - 1)
    generator = next(
        candidate
        for candidate in range(2, prime)
        if all(pow(candidate, (prime - 1) // divisor, prime) != 1 for divisor in factors)
    )
    omega = pow(generator, (prime - 1) // length, prime)
    assert pow(omega, length, prime) == 1 and pow(omega, length // 2, prime) != 1
    return length, generator, omega


def original_entries(a: list[list[int]], arithmetic: PolynomialVerifier, z: int | None) -> list[list[Polynomial]]:
    n = len(a)
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            coefficient = (1 + a[i][j] ** 2) % arithmetic.prime
            exponent = 1 << (i * n + j)
            if z is None:
                row.append(arithmetic.monomial(coefficient, exponent))
            else:
                row.append(arithmetic.monomial(coefficient * pow(z, exponent, arithmetic.prime), 0))
        out.append(row)
    return out


def initialize_moments_by_assignment_oracle(
    a: list[list[int]], labels: list[int], length: int, omega: int,
    arithmetic: PolynomialVerifier, z: int | None,
) -> tuple[list[list[Polynomial]], list[tuple[int, int, Polynomial]]]:
    """Exponential verification-only initialization: n**n assignments."""
    n = len(a)
    h = n * (n - 1) // 2
    observations = [[{} for _ in range(h + 1)] for _ in range(length)]
    records = []
    for choices in product(range(n), repeat=n):
        arithmetic.counts["moment_initializer_assignments"] += 1
        multiplicities = [0] * n
        coefficient, exponent, address = 1, 0, 0
        for i, j in enumerate(choices):
            coefficient = coefficient * (1 + a[i][j] ** 2) % arithmetic.prime
            exponent += 1 << (i * n + j)
            address += labels[j]
            multiplicities[j] += 1
        collision = sum(m * (m - 1) // 2 for m in multiplicities)
        assert 0 <= collision <= h
        if z is None:
            term = arithmetic.monomial(coefficient, exponent)
        else:
            term = arithmetic.monomial(coefficient * pow(z, exponent, arithmetic.prime), 0)
        records.append((collision, address % length, term))
        for frequency in range(length):
            phase = pow(omega, frequency * address, arithmetic.prime)
            for order in range(h + 1):
                observations[frequency][order] = arithmetic.add(
                    observations[frequency][order],
                    arithmetic.scale(term, phase * pow(collision, order, arithmetic.prime)),
                )
    return observations, records


def evaluate_scalar_dag(dag, observations: list[Polynomial], arithmetic: PolynomialVerifier) -> list[Polynomial]:
    """Evaluate the actual ordinary scalar component, including every gate."""
    values = []
    for operation, *arguments in dag.nodes:
        if operation == "input":
            value = observations[arguments[0]]
        elif operation == "const":
            value = arithmetic.monomial(arguments[0], 0)
        elif operation == "add":
            value = arithmetic.add(values[arguments[0]], values[arguments[1]])
        elif operation == "mul":
            value = arithmetic.multiply(values[arguments[0]], values[arguments[1]])
        else:
            raise ValueError(operation)
        values.append(value)
    return values


def projector_coefficients(h: int, prime: int) -> list[int]:
    coefficients = [1]
    for factor in range(1, h + 1):
        inverse = pow(factor, -1, prime)
        updated = [0] * (len(coefficients) + 1)
        for order, coefficient in enumerate(coefficients):
            updated[order] = (updated[order] + coefficient) % prime
            updated[order + 1] = (updated[order + 1] - inverse * coefficient) % prime
        coefficients = updated
    return coefficients


def finite_difference_at_zero(
    entries: list[list[Polynomial]], phases: list[int], arithmetic: PolynomialVerifier,
) -> Polynomial:
    """Verification-only ordinary finite differences of G_B; no matrices."""
    n = len(entries)
    out: Polynomial = {}
    for mask in range(1 << n):
        arithmetic.counts["finite_difference_orbit_evaluations"] += 1
        value = {0: 1}
        for row in entries:
            row_sum: Polynomial = {}
            for j, entry in enumerate(row):
                if mask & (1 << j):
                    row_sum = arithmetic.add(row_sum, arithmetic.scale(entry, phases[j]))
            value = arithmetic.multiply(value, row_sum)
        sign = -1 if (n - mask.bit_count()) % 2 else 1
        out = arithmetic.add(out, arithmetic.scale(value, sign))
    return out


def first_two_moments_direct(
    entries: list[list[Polynomial]], phases: list[int], arithmetic: PolynomialVerifier,
) -> tuple[Polynomial, Polynomial]:
    """Direct polynomial preparation of mu_0 and mu_1, without assignments.

    mu_0 = product_i ell_i and
    mu_1 = sum_(i<k) (sum_j B_ij B_kj t_j^2) product_(r!=i,k) ell_r.
    The displayed scalar arithmetic has O(n^3) gates when entries are wires.
    Polynomial expansion here is for verification of formal-z outputs only.
    """
    n = len(entries)
    row_sums = []
    for row in entries:
        total: Polynomial = {}
        for j, entry in enumerate(row):
            total = arithmetic.add(total, arithmetic.scale(entry, phases[j]))
        row_sums.append(total)
    zero = {0: 1}
    for row_sum in row_sums:
        zero = arithmetic.multiply(zero, row_sum)
    one: Polynomial = {}
    for i in range(n):
        for k in range(i + 1, n):
            pair: Polynomial = {}
            for j in range(n):
                term = arithmetic.multiply(entries[i][j], entries[k][j])
                pair = arithmetic.add(pair, arithmetic.scale(term, phases[j] ** 2))
            for row in range(n):
                if row != i and row != k:
                    pair = arithmetic.multiply(pair, row_sums[row])
            one = arithmetic.add(one, pair)
    return zero, one


def inverse_ntt(frequencies: list[Polynomial], omega: int, arithmetic: PolynomialVerifier) -> list[Polynomial]:
    length = len(frequencies)
    inverse_length = pow(length, -1, arithmetic.prime)
    table = []
    for channel in range(length):
        value: Polynomial = {}
        for frequency, term in enumerate(frequencies):
            arithmetic.counts["inverse_ntt_summands"] += 1
            factor = inverse_length * pow(omega, (-frequency * channel) % length, arithmetic.prime)
            value = arithmetic.add(value, arithmetic.scale(term, factor))
        table.append(value)
    return table


def terminal_table_oracle(
    a: list[list[int]], labels: list[int], length: int,
    arithmetic: PolynomialVerifier, z: int | None,
) -> list[Polynomial]:
    """Independent test oracle on original entries; no spectral shortcut in tested path."""
    n = len(a)
    table: list[Polynomial] = [{} for _ in range(length)]
    for choices in permutations(range(n)):
        arithmetic.counts["terminal_oracle_assignments"] += 1
        coefficient, exponent, channel = 1, 0, 0
        for i, j in enumerate(choices):
            coefficient = coefficient * (1 + a[i][j] ** 2) % arithmetic.prime
            exponent += 1 << (i * n + j)
            channel += labels[j]
        if z is None:
            term = arithmetic.monomial(coefficient, exponent)
        else:
            term = arithmetic.monomial(coefficient * pow(z, exponent, arithmetic.prime), 0)
        table[channel % length] = arithmetic.add(table[channel % length], term)
    return table


def check_mode(a, labels, length, omega, prime, z):
    arithmetic = PolynomialVerifier(prime)
    n = len(a)
    observer = compile_observer(n, prime)
    h = observer.h
    assert observer.dag.gates == 4 * h * h + 2 * h
    assert observer.step_gates == [4 * h + 2] * h
    moments, records = initialize_moments_by_assignment_oracle(a, labels, length, omega, arithmetic, z)
    pi = projector_coefficients(h, prime)
    entries = original_entries(a, arithmetic, z)
    output_frequencies = []
    stage_digests = []
    all_stage_checks = 0

    for frequency in range(length):
        values = evaluate_scalar_dag(observer.dag, moments[frequency], arithmetic)
        # Independent eigenspace reference for all stages.  Its bins are
        # explicitly initialized by the same exponential assignment list;
        # their small number is not an initializer construction claim.
        energy_weights = [{} for _ in range(h + 1)]
        for collision, address, term in records:
            arithmetic.counts["stage_oracle_binning_assignments"] += 1
            energy_weights[collision] = arithmetic.add(
                energy_weights[collision],
                arithmetic.scale(term, pow(omega, frequency * address, prime)),
            )
        for step, nodes in enumerate(observer.stages):
            expected = [{} for _ in range(h + 1)]
            for collision, term in enumerate(energy_weights):
                factor = 1
                for r in range(1, step + 1):
                    factor = factor * (1 - collision * pow(r, -1, prime)) % prime
                for order in range(h + 1):
                    expected[order] = arithmetic.add(
                        expected[order], arithmetic.scale(term, factor * pow(collision, order, prime))
                    )
            actual = [values[node] for node in nodes]
            assert actual == expected
            all_stage_checks += 1
        stage_digests.append(digest([[encode(values[node]) for node in nodes] for nodes in observer.stages]))

        # Check the characteristic recurrence before applying the projector.
        next_moment: Polynomial = {}
        for collision, term in enumerate(energy_weights):
            factor = pow(collision, h + 1, prime)
            next_moment = arithmetic.add(next_moment, arithmetic.scale(term, factor))
        recurrence = next_moment
        for order in range(h + 1):
            recurrence = arithmetic.add(recurrence, arithmetic.scale(moments[frequency][order], observer.chi[order]))
        assert recurrence == {}

        projected: Polynomial = {}
        for order, coefficient in enumerate(pi):
            projected = arithmetic.add(projected, arithmetic.scale(moments[frequency][order], coefficient))
        phases = [pow(omega, frequency * label, prime) for label in labels]
        direct_zero, direct_one = first_two_moments_direct(entries, phases, arithmetic)
        assert direct_zero == moments[frequency][0]
        if h:
            assert direct_one == moments[frequency][1]
        else:
            assert direct_one == {}
        differences = finite_difference_at_zero(entries, phases, arithmetic)
        result = values[observer.readout]
        assert result == projected == differences
        assert all(values[node] == {} for node in observer.outputs[1:])
        output_frequencies.append(result)

    table = inverse_ntt(output_frequencies, omega, arithmetic)
    target = terminal_table_oracle(a, labels, length, arithmetic, z)
    assert table == target
    return {
        "mode": "formal_z" if z is None else "numeric_z",
        "z": z,
        "companion_gate_count_per_frequency": observer.dag.gates,
        "component_gate_count_all_frequencies": length * observer.dag.gates,
        "all_projector_stages_checked": all_stage_checks,
        "moment_table_sha256": digest([[encode(moment) for moment in row] for row in moments]),
        "stage_table_sha256_by_frequency": stage_digests,
        "output_frequencies": [encode(value) for value in output_frequencies],
        "inverse_ntt_table": [encode(value) for value in table],
        "terminal_oracle_table": [encode(value) for value in target],
        "characteristic_recurrence_passed": True,
        "direct_mu_0_preparation_passed": True,
        "direct_mu_1_pair_formula_passed": True,
        "all_companion_stages_passed": True,
        "independent_projector_passed": True,
        "ordinary_finite_differences_passed": True,
        "complete_inverse_ntt_passed": True,
        "verifier_work_counters": dict(sorted(arithmetic.counts.items())),
    }


def evaluate_encoded_polynomial(value: list[list[int]], z: int, prime: int) -> int:
    return sum(coefficient * pow(z, exponent, prime) for exponent, coefficient in value) % prime


def verify() -> dict[str, object]:
    rng = Random(2026110107)
    cases = []
    counters: Counter[str] = Counter()
    mode_count = 0
    formal_count = 0
    total_stages = 0
    for prime in (17, 97):
        for n in range(1, 6):
            length, generator, omega = field_parameters(prime, n)
            for label_kind in ("all_zero", "random"):
                a = [[rng.randrange(prime) for _ in range(n)] for _ in range(n)]
                a[0][0] = 0
                labels = [0] * n if label_kind == "all_zero" else [rng.randrange(-2 * length, 2 * length + 1) for _ in range(n)]
                z = rng.randrange(1, prime)
                modes = [check_mode(a, labels, length, omega, prime, z)]
                if n <= 4:
                    modes.append(check_mode(a, labels, length, omega, prime, None))
                    numerical = modes[0]["inverse_ntt_table"]
                    formal = modes[1]["inverse_ntt_table"]
                    for scalar, polynomial in zip(numerical, formal):
                        expected = evaluate_encoded_polynomial(polynomial, z, prime)
                        assert scalar == ([[0, expected]] if expected else [])
                    formal_count += 1
                for mode in modes:
                    counters.update(mode["verifier_work_counters"])
                    total_stages += mode["all_projector_stages_checked"]
                    mode_count += 1

                # Ordered paired exterior symbols: x0,y0,x1,y1,... to all x then all y.
                paired_order = [entry for j in range(n) for entry in (j, n + j)]
                inversions = sum(
                    paired_order[i] > paired_order[j]
                    for i in range(2 * n) for j in range(i + 1, 2 * n)
                )
                gamma = -1 if (n * (n - 1) // 2) % 2 else 1
                raw_orientation = -1 if inversions % 2 else 1
                assert raw_orientation == gamma and raw_orientation * gamma == 1
                cases.append({
                    "prime": prime, "n": n, "h": n * (n - 1) // 2,
                    "N": length, "generator": generator, "omega": omega,
                    "label_kind": label_kind, "labels": labels,
                    "a": a, "numeric_z": z,
                    "target_channel": sum(labels) % length,
                    "universal_correction_gamma": gamma,
                    "raw_paired_orientation_sign": raw_orientation,
                    "corrected_Omega_coordinate_sign": 1,
                    "formal_numeric_specialization_passed": n <= 4,
                    "modes": modes,
                })

    assert len(cases) == 20 and mode_count == 36 and formal_count == 16
    source = Path(__file__).resolve()
    component = source.with_name("collision_observer.py")
    return {
        "status": "pass", "schema_version": 1,
        "source_sha256": sha256(source.read_bytes()).hexdigest(),
        "collision_observer_sha256": sha256(component.read_bytes()).hexdigest(),
        "seed": 2026110107,
        "original_input_cases": len(cases),
        "numeric_tables": len(cases), "formal_z_tables": formal_count,
        "total_complete_tables": mode_count,
        "all_projector_stages_checked": total_stages,
        "scope": {
            "chain": "Original a,z -> G_B -> moment observation oracle -> companion projector DAG -> actual INTT -> corrected Omega coordinate",
            "moments": "mu_(j,f) = sum_assignments amplitude * phase * kappa(m)^j",
            "finite_differences": "Ordinary differences of product_i sum_j B_ij s_j at base zero; computed only as an independent small oracle",
            "formal_parameters": "All z markers formal for n<=4; original a entries sampled in the stated prime field",
            "direct_initialization_checked": "mu_0 via product of row sums; mu_1 via the row-pair Leibniz formula, with O(n^3) scalar arithmetic. This does not initialize all remaining moments.",
            "no_initialization_polynomial_bound_claimed": True,
            "no_full_scalar_polynomial_compiler_claimed": True,
        },
        "verification_cost": {
            "moment_initialization": "Enumerates n^n assignments; exponential verification-only initializer, never a supplied polynomial circuit I(n,N).",
            "finite_difference_oracle": "Enumerates 2^n parameter evaluations for each frequency; expanded polynomial arithmetic in formal-z mode.",
            "terminal_oracle": "Enumerates n! bijective assignments only for independent testing.",
            "companion_component": "The actual tested component has exactly N*(4h^2+2h) ordinary scalar gates once moments are supplied.",
            "inverse_ntt": "All N^2 summands are evaluated independently; no collapse to a presumed channel in the tested path.",
            "counter_scope": "Counts instrumented polynomial arithmetic and enumerations; field exponentiation, input preparation, and Python overhead are not included. This is not a complete scalar gate count.",
            "instrumented_work_counters": dict(sorted(counters.items())),
        },
        "cases": cases,
        "case_data_sha256": digest(cases),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    arguments = parser.parse_args()
    report = verify()
    if arguments.write_report:
        Path(__file__).resolve().with_name("orbit-bridge-validation.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps({
        "status": report["status"], "tables": report["total_complete_tables"],
        "formal_z_tables": report["formal_z_tables"],
        "stages": report["all_projector_stages_checked"],
        "source_sha256": report["source_sha256"],
        "component_sha256": report["collision_observer_sha256"],
        "report_written": arguments.write_report,
        "polynomial_initializer_claimed": False,
    }))


if __name__ == "__main__":
    main()

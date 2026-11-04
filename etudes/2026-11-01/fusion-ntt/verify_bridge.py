"""Small exact verifier of the transport-difference / NTT bridge.

This program expands words and is deliberately NOT a polynomial scalar
compiler.  Permutations occur only in the independent test oracle.
The indeterminate z is kept formal, as an exponent -> coefficient map.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
import random
from time import perf_counter


SEED = 2026110107
FIELDS = (17, 97, 998244353)
Word = tuple[int, ...]
WordPolynomial = dict[Word, int]
FormalPolynomial = dict[int, int]


def compositions(total: int, gaps: int):
    """Weak compositions, used to expand the rational transport itself."""
    if gaps == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, gaps - 1):
            yield (first,) + rest


def insert_in_gaps(word: Word, column: int, gaps: tuple[int, ...]) -> Word:
    result: list[int] = []
    for position, copies in enumerate(gaps):
        result.extend([column] * copies)
        if position < len(word):
            result.append(word[position])
    return tuple(result)


def clean(poly, prime: int):
    return {key: value % prime for key, value in poly.items() if value % prime}


def transport_difference(
    poly: WordPolynomial, column: int, alpha: int, order: int, prime: int
) -> WordPolynomial:
    """Expand (T_(alpha e_j) - Id) directly using R X ... R X R."""
    result = defaultdict(int)
    for word, coefficient in poly.items():
        for degree in range(1, order - len(word) + 1):
            weight = coefficient * pow(alpha, degree, prime) % prime
            for gaps in compositions(degree, len(word) + 1):
                output = insert_in_gaps(word, column, gaps)
                result[output] += weight
    return clean(result, prime)


def coefficient_signal(
    poly: WordPolynomial, column: int, label: int,
    order: int, length: int, prime: int,
) -> list[WordPolynomial]:
    """Apply M_j[s] = sum_(r*d_j=s mod N) C_j,r to a polynomial."""
    signal = [defaultdict(int) for _ in range(length)]
    for word, coefficient in poly.items():
        for degree in range(1, order - len(word) + 1):
            bucket = signal[degree * label % length]
            for gaps in compositions(degree, len(word) + 1):
                output = insert_in_gaps(word, column, gaps)
                bucket[output] += coefficient
    return [clean(bucket, prime) for bucket in signal]


def ntt_at(signal, frequency: int, omega: int, prime: int):
    result = defaultdict(int)
    for slot, poly in enumerate(signal):
        phase = pow(omega, frequency * slot, prime)
        for key, coefficient in poly.items():
            result[key] += phase * coefficient
    return clean(result, prime)


def inverse_ntt(signal, omega: int, prime: int):
    length = len(signal)
    inverse_omega = pow(omega, -1, prime)
    inverse_length = pow(length, -1, prime)
    result = []
    for slot in range(length):
        transformed = ntt_at(signal, slot, inverse_omega, prime)
        result.append(clean({key: inverse_length * c for key, c in transformed.items()}, prime))
    return result


def exact_root(prime: int, length: int) -> int:
    assert length >= 2 and length & (length - 1) == 0
    assert (prime - 1) % length == 0
    for candidate in range(2, prime):
        omega = pow(candidate, (prime - 1) // length, prime)
        if pow(omega, length, prime) == 1 and pow(omega, length // 2, prime) != 1:
            return omega
    raise AssertionError("No root of the required order")


def clock_evaluate(
    poly: WordPolynomial, weights: list[list[int]], prime: int
) -> FormalPolynomial:
    """The (n,0) entry of A_w0 ... A_w(n-1); rightmost acts first."""
    order = len(weights)
    result = defaultdict(int)
    for word, coefficient in poly.items():
        if len(word) != order:
            continue
        exponent = 0
        for row, column in enumerate(reversed(word)):
            coefficient = coefficient * weights[row][column] % prime
            exponent += 1 << (row * order + column)
        result[exponent] += coefficient
    return clean(result, prime)


def permutation_oracle(weights: list[list[int]], prime: int) -> FormalPolynomial:
    """Independent oracle used exclusively by this finite verifier."""
    order = len(weights)
    result = defaultdict(int)
    for assignment in permutations(range(order)):
        coefficient = 1
        exponent = 0
        for row, column in enumerate(assignment):
            coefficient = coefficient * weights[row][column] % prime
            exponent += 1 << (row * order + column)
        result[exponent] += coefficient
    return clean(result, prime)


def word_permutation_oracle(order: int, phase: int) -> WordPolynomial:
    """Formal word oracle: does not specialize any matrix amplitude."""
    return {word: phase for word in permutations(range(order))}


def verify_case(a, labels, prime: int):
    order = len(a)
    length = 1 << order.bit_length()  # strictly larger than n
    omega = exact_root(prime, length)
    weights = [[(1 + value * value) % prime for value in row] for row in a]
    spectral_values = []
    factor_checks = 0
    largest_word_support = 0
    for frequency in range(length):
        state: WordPolynomial = {(): 1}
        for column, label in enumerate(labels):
            signal = coefficient_signal(state, column, label, order, length, prime)
            transformed = ntt_at(signal, frequency, omega, prime)
            direct = transport_difference(
                state, column, pow(omega, frequency * label, prime), order, prime
            )
            assert transformed == direct, (order, prime, labels, frequency, column)
            state = transformed
            largest_word_support = max(largest_word_support, len(state))
            factor_checks += 1
        # No word with a repeated column may survive the terminal action.
        assert all(len(word) == order and len(set(word)) == order for word in state)
        phase = pow(omega, frequency * sum(labels), prime)
        assert state == word_permutation_oracle(order, phase)
        spectral_values.append(clock_evaluate(state, weights, prime))

    table = inverse_ntt(spectral_values, omega, prime)
    target_slot = sum(labels) % length
    expected_amplitude = permutation_oracle(weights, prime)
    expected_table = [expected_amplitude if slot == target_slot else {} for slot in range(length)]
    assert table == expected_table, (order, prime, labels)
    # Check the complete spectrum as well as the complete inverse table.
    for frequency, actual in enumerate(spectral_values):
        phase = pow(omega, frequency * sum(labels), prime)
        expected = clean({exponent: phase * c for exponent, c in expected_amplitude.items()}, prime)
        assert actual == expected

    return {
        "n": order,
        "Q": prime,
        "N": length,
        "omega": omega,
        "a": a,
        "labels": labels,
        "target_slot": target_slot,
        "factor_frequency_checks": factor_checks,
        "largest_expanded_word_support": largest_word_support,
        "formal_z_output_terms": len(expected_amplitude),
        "full_Z_coefficient_of_Omega": [dict(sorted(poly.items())) for poly in table],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    source = Path(__file__).resolve()
    initial_hash = sha256(source.read_bytes()).hexdigest()
    started = perf_counter()
    rng = random.Random(SEED)
    cases = []
    for prime in FIELDS:
        for order in range(1, 6):
            length = 1 << order.bit_length()
            for label_kind in ("all_zero", "random"):
                a = [[rng.randrange(prime) for _ in range(order)] for _ in range(order)]
                # Include legal zero inputs a_ij=0 in each family of cases.
                a[0][0] = 0
                labels = [0] * order if label_kind == "all_zero" else [rng.randrange(length) for _ in range(order)]
                case = verify_case(a, labels, prime)
                case["label_kind"] = label_kind
                cases.append(case)

    assert sha256(source.read_bytes()).hexdigest() == initial_hash, "Source changed during verification"
    report = {
        "status": "passed",
        "scope": "Finite exact verifier only; no polynomial scalar compiler or all-order proof is claimed.",
        "formula": "M_j[s]=sum_{r*d_j=s mod N,r>=1} C_j,r; hat(M_j)[f]=T_{omega^(f*d_j)e_j}-Id; compose, apply to 1, evaluate clock, inverse NTT.",
        "formal_z": True,
        "formal_word_identity": "All terminal words and coefficients are compared before any matrix amplitude is specialized.",
        "original_a_inputs": "Original a_ij are sampled modulo Q; p_ij=1+a_ij^2 is then computed explicitly. The word identity also checks arbitrary unspecialized amplitudes at the operator level.",
        "universal_sign": "Outputs are coefficients of Omega_tilde, after gamma_n*q_[n]=Omega_tilde.",
        "clock_word_order": "Reversed: in A_w0 ... A_w(n-1), the rightmost factor acts on e_0 first.",
        "reference": "Permutation enumeration is used exclusively in the independent test oracle.",
        "seed": SEED,
        "source_sha256": {source.name: initial_hash},
        "fields": list(FIELDS),
        "n_range": [1, 5],
        "full_formal_tables_checked": len(cases),
        "factor_frequency_checks": sum(case["factor_frequency_checks"] for case in cases),
        "spectrum_slots_checked": sum(case["N"] for case in cases),
        "formal_word_polynomials_checked": sum(case["N"] for case in cases),
        "elapsed_seconds": round(perf_counter() - started, 6),
        "verified_utc": datetime.now(timezone.utc).isoformat(),
        "cases": cases,
    }
    if args.write_report:
        destination = source.with_name("bridge-validation.json")
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "status", "full_formal_tables_checked", "factor_frequency_checks",
        "spectrum_slots_checked", "elapsed_seconds", "source_sha256",
    )}, ensure_ascii=False))


if __name__ == "__main__":
    main()

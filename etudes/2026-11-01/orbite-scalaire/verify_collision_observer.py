"""Verify every observer update on synthetic monomials and NTT phases.

The independent reference only evaluates the explicit monomials supplied to
the test. It contains no subset states and performs no column enumeration.
It does not claim to initialize the moments of a generic marked row product.
"""

import hashlib
import json
import random
import sys
from pathlib import Path

from collision_observer import compile_observer


HERE = Path(__file__).resolve().parent


def prime_by_trial_division(q):
    if q < 2:
        return False
    if q % 2 == 0:
        return q == 2
    d = 3
    while d * d <= q:
        if q % d == 0:
            return False
        d += 2
    return True


def order_root(q, N):
    if (q - 1) % N:
        raise ValueError("No required power-of-two NTT root in this field")
    for candidate in range(2, q):
        root = pow(candidate, (q - 1) // N, q)
        if pow(root, N, q) == 1 and pow(root, N // 2, q) != 1:
            return root
    raise AssertionError("No root found")


def collision_count(monomial):
    return sum(m * (m - 1) // 2 for m in monomial)


def synthetic_mixture(n, q, rng):
    terms = [{"coefficient": 1, "powers": [1] * n}]
    # Include complete collisions and random degree-n monomials. No subsets.
    concentrated = [0] * n
    concentrated[0] = n
    terms.append({"coefficient": rng.randrange(1, q), "powers": concentrated})
    for _ in range(10 + n):
        powers = [0] * n
        for _ in range(n):
            powers[rng.randrange(n)] += 1
        terms.append({"coefficient": rng.randrange(1, q), "powers": powers})
    return terms


def moments_of_terms(terms, labels, frequency, root, q, h):
    weighted = []
    for term in terms:
        phase_index = frequency * sum(d * m for d, m in zip(labels, term["powers"]))
        weighted.append(term["coefficient"] * pow(root, phase_index, q) % q)
    collisions = [collision_count(term["powers"]) for term in terms]
    moments = [
        sum(weight * pow(kappa, j, q) for weight, kappa in zip(weighted, collisions)) % q
        for j in range(h + 1)
    ]
    return moments, weighted, collisions


def verify():
    seed = 2026110113
    rng = random.Random(seed)
    configurations, cases = [], []
    tested_tables = tested_frequencies = checked_stage_coordinates = 0
    fields = ((17, 6), (97, 8), (998244353, 8))
    for q, maximum_n in fields:
        assert prime_by_trial_division(q)
        for n in range(1, maximum_n + 1):
            observer = compile_observer(n, q)
            h = observer.h
            N = 1 << n.bit_length()
            root = order_root(q, N)
            assert observer.step_gates == [4 * h + 2] * h
            assert observer.dag.gates == h * (4 * h + 2)
            assert sum(node[0] == "add" for node in observer.dag.nodes) == h * (2 * h + 1)
            assert sum(node[0] == "mul" for node in observer.dag.nodes) == h * (2 * h + 1)
            assert {node[1] for node in observer.dag.nodes if node[0] == "input"} == set(range(h + 1))
            assert observer.chi[-1] == 1
            assert all(sum(c * pow(kappa, j) for j, c in enumerate(observer.chi)) == 0 for kappa in range(h + 1))
            configurations.append({
                "n": n, "h": h, "prime": q, "N": N, "root": root,
                "state_scalars": h + 1,
                "scalar_gates": observer.dag.gates,
                "gates_per_factor": 4 * h + 2 if h else 0,
                "scalar_additions": h * (2 * h + 1),
                "scalar_multiplications": h * (2 * h + 1),
                "chi_integer_coefficients": observer.chi,
            })
            for mixture_id in range(2):
                terms = synthetic_mixture(n, q, rng)
                labels = [rng.randrange(3 * N) for _ in range(n)]
                if n >= 3:
                    labels[1] = labels[0]
                    labels[-1] = 0
                final_values = []
                for f in range(N):
                    initial, weights, collisions = moments_of_terms(terms, labels, f, root, q, h)
                    flat_outputs = [wire for stage in observer.stages for wire in stage]
                    observed = observer.dag.evaluate(flat_outputs, dict(enumerate(initial)), q)
                    for r in range(h + 1):
                        if r:
                            inv_r = pow(r, -1, q)
                            weights = [w * (1 - kappa * inv_r) % q for w, kappa in zip(weights, collisions)]
                        expected = [
                            sum(w * pow(kappa, j, q) for w, kappa in zip(weights, collisions)) % q
                            for j in range(h + 1)
                        ]
                        actual = observed[r * (h + 1):(r + 1) * (h + 1)]
                        assert actual == expected, (q, n, mixture_id, f, r)
                        checked_stage_coordinates += h + 1
                    terminal = sum(
                        term["coefficient"] * pow(root, f * sum(labels), q)
                        for term in terms if all(power == 1 for power in term["powers"])
                    ) % q
                    actual_terminal = observed[-(h + 1)]
                    assert actual_terminal == terminal
                    if h:
                        assert all(value == 0 for value in observed[-h:])
                    final_values.append(actual_terminal)
                    tested_frequencies += 1
                # Reference spectral interface only; no transform gates are
                # attributed to the observer component's scalar count.
                inverse_n = pow(N, -1, q)
                inverse_table = [
                    inverse_n * sum(value * pow(root, (-f * k) % N, q)
                                    for f, value in enumerate(final_values)) % q
                    for k in range(N)
                ]
                expected_table = [0] * N
                expected_table[sum(labels) % N] = sum(
                    term["coefficient"] for term in terms
                    if all(power == 1 for power in term["powers"])
                ) % q
                assert inverse_table == expected_table
                cases.append({
                    "n": n, "prime": q, "mixture_id": mixture_id,
                    "labels": labels, "terms": terms,
                    "final_frequency_readouts": final_values,
                    "reference_inverse_ntt_channels": inverse_table,
                    "all_stage_observations_match": True,
                    "all_terminal_readouts_match": True,
                    "whole_inverse_ntt_table_matches": True,
                })
                tested_tables += 1
            print(f"Q={q}, n={n}, observer dimension={h+1}, scalar gates={observer.dag.gates}: pass", flush=True)

    rejected = []
    for n, q in ((1, 2), (3, 3), (7, 17)):
        try:
            compile_observer(n, q)
        except ValueError:
            rejected.append({"n": n, "Q": q})
        else:
            raise AssertionError("Missing required field-size rejection")
    return {
        "status": "pass",
        "date": "2026-11-01",
        "seed": seed,
        "scope": "Scalar observer component from supplied moments mu_j; NOT initialization from a_ij,z and NOT the whole Z chain.",
        "general_polynomial_closure_proved": False,
        "conditional_fusion_and_readout_polynomial": True,
        "field_requirement": "Q prime and Q > max(2,n*(n-1)/2)",
        "test_field_primality_checked": True,
        "bound": "h*(4*h+2) scalar +/* gates, h=n*(n-1)/2; final readout is a wire",
        "n_one_zero_gate_case_checked": True,
        "synthetic_monomial_tables_checked": tested_tables,
        "phase_frequencies_checked": tested_frequencies,
        "reference_inverse_ntt_tables_checked": tested_tables,
        "stage_coordinates_checked": checked_stage_coordinates,
        "no_subset_state_in_component_or_verifier": True,
        "invalid_field_sizes_rejected": rejected,
        "source_sha256": {
            name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in ("collision_observer.py", "verify_collision_observer.py")
        },
        "configurations": configurations,
        "cases": cases,
    }


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    report = verify()
    path = HERE / "validation.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "status", "synthetic_monomial_tables_checked", "phase_frequencies_checked", "stage_coordinates_checked"
    )}))

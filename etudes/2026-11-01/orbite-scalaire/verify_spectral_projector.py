"""Check the NTT observer component on all 44 frozen synthetic test cases."""

import hashlib
import json
import sys
from pathlib import Path

from collision_observer import compile_observer
from spectral_projector import compile_spectral_projector


HERE = Path(__file__).resolve().parent


def root_of_order(q, length):
    if length == 1:
        return None
    if (q - 1) % length:
        raise ValueError("Transform order does not divide Q-1")
    for candidate in range(2, q):
        root = pow(candidate, (q - 1) // length, q)
        if pow(root, length, q) == 1 and pow(root, length // 2, q) != 1:
            return root
    raise AssertionError("No suitable root")


def direct_pi_coefficients(h, q):
    """Independent ordinary coefficient convolution, without a transform."""
    coefficients = [1]
    for r in range(1, h + 1):
        inverse = pow(r, -1, q)
        updated = [0] * (len(coefficients) + 1)
        for j, coefficient in enumerate(coefficients):
            updated[j] = (updated[j] + coefficient) % q
            updated[j + 1] = (updated[j + 1] - inverse * coefficient) % q
        coefficients = updated
    return coefficients


def moment_table(case, h, N, root, q):
    result = []
    for f in range(N):
        observations = [0] * (h + 1)
        for term in case["terms"]:
            powers = term["powers"]
            assert sum(powers) == case["n"]
            kappa = sum(m * (m - 1) // 2 for m in powers)
            phase = f * sum(d * m for d, m in zip(case["labels"], powers))
            weight = term["coefficient"] * pow(root, phase, q) % q
            for j in range(h + 1):
                observations[j] = (observations[j] + weight * pow(kappa, j, q)) % q
        result.append(observations)
    return result


def verify():
    source_cases_path = HERE / "validation.json"
    source_bytes = source_cases_path.read_bytes()
    source_cases = json.loads(source_bytes)
    assert source_cases["status"] == "pass"
    assert len(source_cases["cases"]) == 44
    assert source_cases["source_sha256"]["collision_observer.py"] == hashlib.sha256(
        (HERE / "collision_observer.py").read_bytes()
    ).hexdigest()
    configurations = []
    results = []
    compiled = {}
    coefficient_vectors_checked = 0
    frequencies_checked = 0
    for config in source_cases["configurations"]:
        n, q, N, h = config["n"], config["prime"], config["N"], config["h"]
        M = 1 << h.bit_length() if h else 1
        root_M = root_of_order(q, M)
        chain = compile_spectral_projector(n, q, config["root"], root_M)
        companion = compile_observer(n, q)
        compiled[n, q] = (chain, companion)
        costs = chain.costs
        assert chain.N == N and chain.M == M
        assert costs["factor_ntt_evaluations"] == 2 * h * M
        assert costs["pointwise_products"] == (M * (h - 1) if h else 0)
        assert costs["coefficient_inverse_ntt"] == (2 * M * (M.bit_length() - 1) + M if h else 0)
        assert costs["observer_readouts"] == (N * (2 * h + 1) if h else 0)
        assert costs["outer_inverse_ntt"] == 2 * N * (N.bit_length() - 1) + N
        assert costs["shared_inner_total"] == costs["shared_inner_formula"]
        assert costs["total"] == costs["total_formula"]
        assert costs["total"] == costs["scalar_additions"] + costs["scalar_multiplications"]
        assert {node[1] for node in chain.dag.nodes if node[0] == "input"} == {
            (j, f) for f in range(N) for j in range(h + 1)
        }
        zero_inputs = {(j, f): 0 for f in range(N) for j in range(h + 1)}
        actual_coefficients = chain.dag.evaluate(chain.coefficients, zero_inputs, q)
        expected_coefficients = direct_pi_coefficients(h, q) + [0] * (M - h - 1)
        assert actual_coefficients == expected_coefficients
        coefficient_vectors_checked += 1
        configurations.append({
            "n": n, "h": h, "Q": q, "N": N, "M": M,
            "root_N": chain.root_N, "root_M": chain.root_M,
            "pi_coefficients_including_padding": actual_coefficients,
            "coefficients_match_independent_convolution": True,
            "coefficients_above_h_are_zero": all(c == 0 for c in actual_coefficients[h + 1:]),
            "costs": costs,
        })

    for case in source_cases["cases"]:
        n, q = case["n"], case["prime"]
        chain, companion = compiled[n, q]
        h, N = chain.h, chain.N
        observations = moment_table(case, h, N, chain.root_N, q)
        inputs = {(j, f): observations[f][j] for f in range(N) for j in range(h + 1)}
        actual = chain.dag.evaluate(chain.frequencies + chain.outputs, inputs, q)
        actual_frequencies, actual_channels = actual[:N], actual[N:]
        companion_frequencies = [
            companion.dag.evaluate([companion.readout], dict(enumerate(row)), q)[0]
            for row in observations
        ]
        assert actual_frequencies == companion_frequencies
        assert actual_frequencies == case["final_frequency_readouts"]
        squarefree_amplitude = sum(
            term["coefficient"] for term in case["terms"]
            if all(power == 1 for power in term["powers"])
        ) % q
        expected_channels = [0] * N
        expected_channels[sum(case["labels"]) % N] = squarefree_amplitude
        assert actual_channels == expected_channels
        assert actual_channels == case["reference_inverse_ntt_channels"]
        frequencies_checked += N
        results.append({
            "n": n, "Q": q, "mixture_id": case["mixture_id"],
            "labels": case["labels"],
            "observation_table_sha256": hashlib.sha256(json.dumps(observations).encode()).hexdigest(),
            "projected_frequencies": actual_frequencies,
            "inverse_ntt_channels": actual_channels,
            "matches_companion_observer": True,
            "matches_all_expected_channels": True,
        })

    rejected = []
    for arguments in ((3, 3, 1, 1), (4, 17, 2, 1), (2, 17, 1, 16),
                      (11, 97, root_of_order(97, 16), 1)):
        try:
            compile_spectral_projector(*arguments)
        except ValueError:
            rejected.append(list(arguments))
        else:
            raise AssertionError("Expected parameter rejection")
    return {
        "status": "pass",
        "date": "2026-11-01",
        "scope": "Scalar NTT coefficient-fusion and readout component from supplied mu_(j,f); initialization from a_ij,z is outside the bound.",
        "general_polynomial_closure_proved": False,
        "observation_initialization_included": False,
        "coefficient_wires_shared_across_all_N_frequencies": True,
        "coefficient_vectors_checked": coefficient_vectors_checked,
        "synthetic_cases_checked": len(results),
        "frequencies_checked": frequencies_checked,
        "full_inverse_ntt_tables_checked": len(results),
        "field_requirement": "Q prime, Q>max(2,h), M|Q-1 and N|Q-1; exact root orders checked",
        "formula_h_positive": "3*h*M + 2*M*log2(M) + N*(2*h+1) + 2*N*log2(N)+N",
        "formula_h_zero": "2*N*log2(N)+N; no inner transform and no readout multiplication",
        "invalid_parameters_rejected": rejected,
        "synthetic_cases_source": source_cases_path.name,
        "synthetic_cases_source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "source_sha256": {
            name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in ("collision_observer.py", "spectral_projector.py", "verify_spectral_projector.py")
        },
        "configurations": configurations,
        "cases": results,
    }


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    report = verify()
    destination = HERE / "spectral-projector-validation.json"
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "status", "coefficient_vectors_checked", "synthetic_cases_checked",
        "frequencies_checked", "full_inverse_ntt_tables_checked"
    )}))

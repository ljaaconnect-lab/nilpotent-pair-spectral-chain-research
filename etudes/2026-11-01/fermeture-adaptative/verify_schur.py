"""Independent small-order checks of schur_jet.py; oracle only lives here."""

import argparse
import hashlib
import json
import random
import sys
from itertools import permutations
from pathlib import Path

from schur_jet import PRIME, compile_chain, core_gate_formula


HERE = Path(__file__).resolve().parent


def path_oracle(raw, labels, q):
    """Original marked path expansion, exclusively a verification oracle."""
    n = len(raw)
    N = 1 << n.bit_length()
    result = [{} for _ in range(N)]
    channel = sum(labels) % N
    for assignment in permutations(range(n)):
        coefficient = 1
        exponent = 0
        for i, j in enumerate(assignment):
            coefficient = coefficient * (1 + raw[i][j] ** 2) % q
            exponent += 1 << (i * n + j)
        result[channel][exponent] = (result[channel].get(exponent, 0) + coefficient) % q
    return [{e: c for e, c in polynomial.items() if c} for polynomial in result]


def polynomial_value(polynomial, z, q):
    return sum(c * pow(z, e, q) for e, c in polynomial.items()) % q


def check_prime_by_trial_division(q):
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


def run(write_report=False):
    hashes = {
        name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        for name in ("schur_jet.py", "verify_schur.py")
    }
    assert check_prime_by_trial_division(PRIME)
    seed = 2026110107
    rng = random.Random(seed)
    rows = []
    numeric_count = formal_count = 0
    for n in range(1, 8):
        # Repeated labels and wrap-around are allowed by terminal truncation.
        labels = [rng.randrange(0, 3 * (1 << n.bit_length())) for _ in range(n)]
        if n >= 3:
            labels[1] = labels[0]
            labels[-1] = 0
        chain = compile_chain(n, labels)
        dag, costs = chain.dag, chain.costs
        expected_inputs = {("a", i, j) for i in range(n) for j in range(n)} | {"z"}
        assert {args[0] for op, *args in dag.nodes if op == "input"} == expected_inputs
        assert all(node[0] in {"input", "const", "add", "mul"} for node in dag.nodes)
        assert costs["preparation"] == 4 * n * n - 1
        assert costs["phases_per_frequency"] == [n * n] * chain.N
        assert costs["core_per_frequency"] == [core_gate_formula(n)] * chain.N
        assert costs["intt"] == 2 * chain.N * (chain.N.bit_length() - 1) + chain.N
        assert costs["total"] == costs["total_formula"]
        assert costs["total"] == costs["scalar_additions"] + costs["scalar_multiplications"]
        cases = []
        for case in range(2):
            raw = [[rng.randrange(-3, 4) for _ in range(n)] for _ in range(n)]
            z = (0 if n == 1 else 1) if case == 0 else rng.randrange(2, 12)
            inputs = {("a", i, j): raw[i][j] for i in range(n) for j in range(n)}
            inputs["z"] = z
            target = path_oracle(raw, labels, PRIME)
            expected = [polynomial_value(p, z, PRIME) for p in target]
            observed = dag.evaluate(chain.outputs + chain.frequencies, inputs, PRIME)
            actual, actual_f = observed[:chain.N], observed[chain.N:]
            assert actual == expected, (n, case, "spectral channels", actual, expected)
            expected_f = [
                sum(expected[k] * pow(chain.omega, f * k, PRIME) for k in range(chain.N)) % PRIME
                for f in range(chain.N)
            ]
            assert actual_f == expected_f, (n, case, "frequencies")
            numeric_count += 1
            formal_ok = False
            if case == 0 and n <= 5:
                actual_formal = dag.evaluate_formal_z(chain.outputs, inputs, PRIME)
                assert actual_formal == target, (n, case, "formal z")
                formal_count += 1
                formal_ok = True
            cases.append({
                "a": raw,
                "z": z,
                "outputs": actual,
                "numeric_channels_and_frequencies_match": True,
                "formal_z_channels_match": formal_ok if n <= 5 and case == 0 else "not run",
            })
        rows.append({"n": n, "N": chain.N, "labels": labels, "costs": costs, "cases": cases})
        print(f"n={n}: core={costs['core_formula']}, total={costs['total']}, numeric=2, formal={int(n <= 5)}", flush=True)

    assert all(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest
               for name, digest in hashes.items()), "Source changed during verification"
    report = {
        "status": "all independent finite-order checks passed",
        "date": "2026-11-01",
        "seed": seed,
        "prime": PRIME,
        "prime_checked_by_trial_division": True,
        "prime_form": {"c": 119, "m": 23},
        "contract": "Full corrected Z_Q coefficient of Omega_tilde, from original a_ij,z; phases before each elimination and actual INTT after it.",
        "general_polynomial_closure_proved": False,
        "cost_status": "All ordinary scalar +/* gates counted; exponential exact bound for this candidate.",
        "core_formula": "4*3^(n-1)-3*2^n+n+1",
        "total_formula": "4*n^2-1 + N*(n^2+G_n) + 2*N*log2(N)+N",
        "numeric_spectral_tables_checked": numeric_count,
        "formal_z_spectral_tables_checked": formal_count,
        "formal_z_exponents_reduced": False,
        "compiler_inputs_only_a_and_z": True,
        "permutation_oracle_only_in_verification": True,
        "source_sha256": hashes,
        "runs": rows,
    }
    output = HERE / "validation.json"
    if write_report:
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {numeric_count} numeric tables, {formal_count} formal-z tables")
    return report


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    run(write_report=args.write_report)

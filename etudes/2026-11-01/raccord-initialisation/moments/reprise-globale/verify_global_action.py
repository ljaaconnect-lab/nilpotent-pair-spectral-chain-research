"""Independent small-order verification of the global L-action compiler."""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from random import Random
import sys

from global_action import (SharedDAG, initialize_without_division,
                           attained_collision_spectrum, initialize_all_without_division)

sys.setrecursionlimit(20000)


def reference(x, order, q):
    n = len(x)
    result = [0] * (order + 1)
    for js in product(range(n), repeat=n):
        value = 1
        for i, j in enumerate(js):
            value = value * x[i][j] % q
        kappa = sum(js[a] == js[b] for a in range(n) for b in range(a + 1, n))
        for r in range(order + 1):
            result[r] = (result[r] + value * pow(kappa, r, q)) % q
    return result


def main():
    folder = Path(__file__).resolve().parent
    names = ["global_action.py", "verify_global_action.py"]
    hashes = {name: sha256((folder / name).read_bytes()).hexdigest() for name in names}
    rng = Random(173919)
    report = {"status": "passed", "source_sha256": hashes, "cases": [],
              "general_polynomial_closure": False,
              "scope": "Actual ordinary scalar actions from x_ij, with all data divisions eliminated."}
    for n, order in [(2, 1), (3, 3), (4, 3)]:
        print(f"building n={n}, order={order}", flush=True)
        dag = SharedDAG(n, 97, max_nodes=600000)
        try:
            outputs, sizes = dag.moments(order)
        except OverflowError:
            report["cases"].append({"n": n, "order": order, "status": "node_budget_exceeded",
                                    "node_budget": dag.max_nodes})
            continue
        costs = None
        for sample in range(3):
            x = [[rng.randrange(97) for _ in range(n)] for _ in range(n)]
            if sample == 1:
                x[0][-1] = -sum(x[0][:-1]) % 97
            elif sample == 2:
                x[0] = [0] * n
            actual, current = initialize_without_division(dag, outputs, x)
            assert actual == reference(x, order, 97), (n, order, sample, actual)
            if costs is not None:
                assert current == costs
            costs = current
        case = {"n": n, "order": order, "status": "passed", "samples": 3,
                "shared_rational_gate_sizes": sizes, "division_free_scalar_costs": costs,
                "zero_row_sum_and_zero_row_tested": True}
        report["cases"].append(case)
        print(json.dumps(case), flush=True)
    report["full_initializations"] = []
    for n in (3, 4):
        spectrum = attained_collision_spectrum(n)
        dag = SharedDAG(n, 97, max_nodes=600000)
        outputs, sizes = dag.moments(len(spectrum) - 1)
        h = n * (n - 1) // 2
        costs = None
        for sample in range(3):
            x = [[rng.randrange(97) for _ in range(n)] for _ in range(n)]
            if sample == 1:
                x[0][-1] = -sum(x[0][:-1]) % 97
            elif sample == 2:
                x[0] = [0] * n
            actual, current = initialize_all_without_division(dag, outputs, x)
            assert actual == reference(x, h, 97), (n, sample, actual)
            if costs is not None:
                assert costs == current
            costs = current
        length = 1
        while length <= n:
            length *= 2
        omega = pow(5, 96 // length, 97)
        assert pow(omega, length, 97) == 1 and pow(omega, length // 2, 97) != 1
        a = [[rng.randrange(97) for _ in range(n)] for _ in range(n)]
        for frequency in range(length):
            x = [[(1 + a[i][j] ** 2) * pow(2, 2 ** (i * n + j), 97) *
                  pow(omega, frequency * j, 97) % 97 for j in range(n)] for i in range(n)]
            actual, current = initialize_all_without_division(dag, outputs, x)
            assert actual == reference(x, h, 97), (n, frequency, actual)
            assert current == costs
        case = {"n": n, "moments_initialized": h + 1, "spectrum": spectrum,
                "explicit_action_orders": len(spectrum),
                "shared_rational_gate_sizes": sizes,
                "division_free_scalar_costs": costs, "samples": 3,
                "original_source_spectral_samples": length, "spectral_root": omega,
                "zero_row_sum_and_zero_row_tested": True, "status": "passed"}
        report["full_initializations"].append(case)
        print(json.dumps(case), flush=True)
    assert hashes == {name: sha256((folder / name).read_bytes()).hexdigest() for name in names}
    (folder / "global-action-validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("global action checks complete", flush=True)


if __name__ == "__main__":
    main()

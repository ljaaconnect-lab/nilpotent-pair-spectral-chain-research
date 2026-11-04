"""Frozen positive SymPy checks for the n15 concrete half-character candidate."""
import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from time import perf_counter

import sympy as sp

import half_character as hc


def independent_permanent(x):
    n = len(x)
    return sp.Add(*(sp.Mul(*(x[i][sigma[i]] for i in range(n)))
                    for sigma in itertools.permutations(range(n))))


def direct_factor_contraction(x):
    n = len(x)
    signs = [delta for _, delta in hc.gray_signs(n)]
    r = len(signs)
    matrices = [sp.SparseMatrix(r, r, {(k, k): sp.Add(*(signs[k][j] * x[i][j]
                                                      for j in range(n)))
                                      for k in range(r)}) for i in range(n)]
    covector = sp.SparseMatrix(1, r, {(0, k): sp.Rational(sp.prod(signs[k]), r)
                                    for k in range(r)})
    vector = sp.ones(r, 1)
    current = covector
    for matrix in matrices:
        current = current * matrix
    return (current * vector)[0]


def symbolic_gray(x):
    n = len(x)
    rows = [sp.Add(*x[i]) for i in range(n)]
    prior = 0
    terms = []
    row_checks = []
    for step, (mask, signs) in enumerate(hc.gray_signs(n)):
        if step:
            flip = mask ^ prior
            column = flip.bit_length()
            update = -2 if mask & flip else 2
            rows = [sp.expand(rows[i] + update * x[i][column]) for i in range(n)]
        row_checks.extend(sp.expand(rows[i] - sp.Add(*(signs[j] * x[i][j]
                                                      for j in range(n)))) == 0
                          for i in range(n))
        terms.append((-1) ** mask.bit_count() * sp.Mul(*rows))
        prior = mask
    return sp.Add(*terms) / (1 << (n - 1)), all(row_checks)


def selection_identity(n):
    """Positive projector verification on all assignments, not matrix samples."""
    signs = [delta for _, delta in hc.gray_signs(n)]
    r = len(signs)
    for assignment in itertools.product(range(n), repeat=n):
        total = sum(sp.prod(delta) * sp.prod(delta[j] for j in assignment) for delta in signs)
        expected = r if len(set(assignment)) == n else 0
        if total != expected:
            return False
    return True


def marked_oracle(A):
    n = len(A)
    output = {}
    for sigma in itertools.permutations(range(n)):
        value = Fraction(1)
        exponent = 0
        for i, j in enumerate(sigma):
            value *= 1 + A[i][j] ** 2
            exponent += 1 << (i * n + j)
        output[exponent] = output.get(exponent, Fraction(0)) + value
    return output


def inspect(n):
    started = perf_counter()
    x = [[sp.Symbol(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    reference = independent_permanent(x)
    diagonal_started = perf_counter()
    factor = direct_factor_contraction(x)
    diagonal_ok = sp.expand(factor - reference) == 0
    diagonal_seconds = perf_counter() - diagonal_started
    gray_started = perf_counter()
    symbolic, rows_match = symbolic_gray(x)
    symbolic_ok = sp.expand(symbolic - reference) == 0
    gray_seconds = perf_counter() - gray_started
    projection_ok = selection_identity(n)

    A = [[Fraction((i + 2) * (j + 1) - i, i + j + 2) for j in range(n)] for i in range(n)]
    dag, output, stats = hc.build_marked_gray(A)
    evaluation_started = perf_counter()
    polynomial, eval_stats = dag.evaluate(output)
    marked = {ze: value for (te, ze), value in polynomial.items() if te == 0}
    marked_ok = all(te == 0 for te, ze in polynomial) and marked == marked_oracle(A)
    scalar_seconds = perf_counter() - evaluation_started
    components = [stats[key] for key in ("marker_and_entry_gates",
                    "signed_update_preparation_gates", "initial_row_sum_gates", "gray_update_gates",
                    "row_product_gates", "bucket_sum_gates",
                    "signed_bucket_combination_and_normalization_gates")]
    gates_ok = dag.gates == 5 * n * (n - 1) + n * 2 ** n == sum(components)
    r = 1 << (n - 1)
    allowed = {Fraction(1), Fraction(-1), Fraction(2), Fraction(-2), Fraction(1, r)}
    allowed.update(1 + a ** 2 for row in A for a in row)
    leaf_ok = all((node["op"] in ("add", "mul")) or
                  (node["op"] == "variable" and node["name"] == "z") or
                  (node["op"] == "constant" and Fraction(node["value"]) in allowed)
                  for node in dag.nodes)
    checks = dict(zip(("generic_diagonal_contraction_equals_permutation_oracle",
                       "generic_gray_contraction_equals_permutation_oracle",
                       "every_gray_row_factor_matches_direct_diagonal_entry",
                       "half_character_assignment_selection_identity",
                       "original_marked_scalar_dag_equals_independent_oracle",
                       "exact_gate_formula_and_component_accounting",
                       "cheap_target_independent_scalar_leaf_data"),
                      (diagonal_ok, symbolic_ok, rows_match, projection_ok, marked_ok, gates_ok, leaf_ok)))
    return {"n": n, "checks": checks, "stats": stats, "evaluation": eval_stats,
            "marked_terms": len(marked), "diagonal_symbolic_seconds": diagonal_seconds,
            "gray_symbolic_seconds": gray_seconds, "scalar_seconds": scalar_seconds,
            "total_seconds": perf_counter() - started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("n15-dev-report.json"))
    args = parser.parse_args()
    hypothesis_path = Path(__file__).with_name("n15-hypothesis.json")
    hypothesis = json.loads(hypothesis_path.read_text())
    assert len(hypothesis["dimensions"]) * len(hypothesis["checks_per_dimension"]) == hypothesis["total_checks"]
    results = []
    for n in hypothesis["dimensions"]:
        try:
            result = inspect(n)
            assert set(result["checks"]) == set(hypothesis["checks_per_dimension"])
        except Exception as error:
            result = {"n": n, "error": repr(error),
                      "checks": {key: False for key in hypothesis["checks_per_dimension"]}}
        results.append(result)
    passed = sum(sum(row["checks"].values()) for row in results)
    report = {"node": "n15", "artifact_version": hypothesis["artifact_version"],
              "boundary": hypothesis["boundary"], "sympy_version": sp.__version__,
              "hypothesis_sha256": hashlib.sha256(hypothesis_path.read_bytes()).hexdigest(),
              "implementation_sha256": hashlib.sha256(Path(hc.__file__).read_bytes()).hexdigest(),
              "evaluator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "passed": passed, "total": hypothesis["total_checks"],
              "score": passed / hypothesis["total_checks"], "cases": results,
              "general_proof_status": "UNVERIFIED unless separately verified by Lean",
              "scope": "Positive finite identities for a new exponential contraction; no polynomial gate claim."}
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps({key: report[key] for key in ("node", "sympy_version", "passed", "total", "score")}, indent=2))
    for row in results:
        print(json.dumps({key: row[key] for key in ("n", "checks", "marked_terms", "diagonal_symbolic_seconds",
                          "gray_symbolic_seconds", "scalar_seconds", "total_seconds") if key in row}, indent=2))


if __name__ == "__main__":
    main()

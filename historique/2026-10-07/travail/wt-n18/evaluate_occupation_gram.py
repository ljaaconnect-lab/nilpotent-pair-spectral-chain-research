"""Frozen n18 positive evaluator, written before the occupation variant."""
import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from time import perf_counter

import sympy as sp
import occupation_gram as variant


def permanent_oracle(b):
    n = len(b)
    return sp.Add(*(sp.Mul(*(b[i][sigma[i]] for i in range(n)))
                    for sigma in itertools.permutations(range(n))))


def marked_oracle(A):
    n = len(A)
    result = {}
    for sigma in itertools.permutations(range(n)):
        weight = Fraction(1)
        exponent = 0
        for i, j in enumerate(sigma):
            weight *= 1 + A[i][j] ** 2
            exponent += 1 << (i * n + j)
        result[exponent] = result.get(exponent, Fraction(0)) + weight
    return result


def supported_cb(X, b, y):
    """Enumerate supported n-edge sets; square actual incidence minor dets.

    Missing-column sets have a zero incidence row and repeated-column sets
    have duplicate incidence columns. The omitted zero-minor classification
    is explicitly an informal proof obligation, not a kernel result.
    """
    n = len(b)
    minor_cache = {}
    terms = []
    for rows in itertools.product(range(n), repeat=n):
        edges = sorted((rows[j], j) for j in range(n))
        columns = tuple(j for i, j in edges)
        if columns not in minor_cache:
            indices = [i * n + j for i, j in edges]
            minor_cache[columns] = sp.Matrix(X[:, indices]).det()
        terms.append(minor_cache[columns] ** 2 * sp.Mul(*(b[i][j] * y[i] for i, j in edges)))
    return sp.Add(*terms), {"supported_edge_sets": n ** n, "actual_minor_determinants": len(minor_cache),
                           "all_cached_minor_squares_one": all(d ** 2 == 1 for d in minor_cache.values())}


def compositions(total, size):
    if size == 1:
        yield (total,)
    else:
        for first in range(total + 1):
            for tail in compositions(total - first, size - 1):
                yield (first,) + tail


def inspect(n):
    start = perf_counter()
    b = [[sp.Symbol(f"b_{i}_{j}") for j in range(n)] for i in range(n)]
    y = list(sp.symbols(f"y0:{n}"))
    s = sp.Symbol("s")
    X, W = variant.gram_factors(b, y)
    gram = X * W * X.T
    diagonal = sp.diag(*(sp.Add(*(b[i][j] * y[i] for i in range(n))) for j in range(n)))
    gram_ok = gram == diagonal
    product = sp.Mul(*(diagonal[j, j] for j in range(n)))
    det_ok = sp.expand(gram.det() - product) == 0
    cb_started = perf_counter()
    cb, cb_stats = supported_cb(X, b, y)
    cb_ok = sp.expand(cb - product) == 0 and cb_stats["all_cached_minor_squares_one"]
    cb_seconds = perf_counter() - cb_started
    coefficient_started = perf_counter()
    expected = permanent_oracle(b)
    squarefree = sp.Poly(sp.expand(product), *y).coeff_monomial(sp.Mul(*y))
    squarefree_ok = sp.expand(squarefree - expected) == 0
    encoded = variant.symbolic_encoding(b, s)
    T = sum((n + 1) ** i for i in range(n))
    central = sp.Poly(sp.expand(encoded), s).coeff_monomial(s ** T)
    univariate_ok = sp.expand(central - expected) == 0
    symbolic_coefficient_seconds = perf_counter() - coefficient_started
    occupations = list(compositions(n, n))
    digits_ok = all((sum(m[i] * (n + 1) ** i for i in range(n)) == T)
                    == all(count == 1 for count in m) for m in occupations)

    A = [[Fraction((i + 1) * (j + 3) - 2 * j, i + 2 * j + 3) for j in range(n)]
         for i in range(n)]
    dag, output, stats = variant.build_marked_encoding(A)
    evaluation_started = perf_counter()
    polynomial, evaluation = dag.evaluate(output)
    extracted = {ze: weight for (te, ze), weight in polynomial.items() if te == T}
    marked_ok = extracted == marked_oracle(A) and stats["T"] == T
    scalar_seconds = perf_counter() - evaluation_started
    q = n + 1
    power_cost = q.bit_length() - 1 + q.bit_count() - 1
    predicted = 4 * n * n - 2 + (n - 1) * power_cost
    counted = sum(node["op"] in ("add", "mul") for node in dag.nodes)
    components = sum(stats[key] for key in ("original_marker_and_entry_gates", "auxiliary_marker_gates",
                                            "weighted_entry_gates", "column_sum_gates", "diagonal_product_gates"))
    gate_ok = counted == dag.gates == predicted == components
    allowed = {Fraction(0), Fraction(1)} | {1 + a ** 2 for row in A for a in row}
    leaf_ok = all(node["op"] in ("add", "mul") or
                  (node["op"] == "variable" and node["name"] in ("z", "t")) or
                  (node["op"] == "constant" and Fraction(node["value"]) in allowed)
                  for node in dag.nodes)
    names = ("gram_equals_explicit_diagonal", "gram_determinant_equals_column_product",
             "supported_cauchy_binet_minor_square_sum_equals_column_product",
             "squarefree_occupation_coefficient_equals_generic_permanent",
             "kronecker_coefficient_equals_generic_permanent",
             "original_marked_scalar_dag_coefficient_equals_independent_oracle",
             "exact_scalar_gate_formula_and_components", "target_independent_scalar_leaf_data",
             "occupation_digit_selection_identity")
    checks = dict(zip(names, (gram_ok, det_ok, cb_ok, squarefree_ok, univariate_ok, marked_ok,
                             gate_ok, leaf_ok, digits_ok)))
    return {"n": n, "checks": checks, "construction": stats, "scalar_evaluation": evaluation,
            "cb": cb_stats, "occupation_states_checked": len(occupations),
            "full_marked_terms": len(polynomial), "extracted_marked_terms": len(extracted),
            "cb_seconds": cb_seconds, "symbolic_coefficient_seconds": symbolic_coefficient_seconds,
            "scalar_seconds": scalar_seconds, "total_seconds": perf_counter() - start}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("n18-dev-report.json"))
    args = parser.parse_args()
    frozen_path = Path(__file__).with_name("n18-checklist.json")
    checklist = json.loads(frozen_path.read_text())
    assert len(checklist["dimensions"]) * len(checklist["checks_per_dimension"]) == checklist["total_checks"]
    cases = []
    for n in checklist["dimensions"]:
        try:
            case = inspect(n)
            assert set(case["checks"]) == set(checklist["checks_per_dimension"])
        except Exception as error:
            case = {"n": n, "error": repr(error),
                    "checks": {name: False for name in checklist["checks_per_dimension"]}}
        cases.append(case)
    passed = sum(sum(case["checks"].values()) for case in cases)
    report = {"node": "n18", "artifact_version": checklist["artifact_version"],
              "boundary": checklist["boundary"], "sympy_version": sp.__version__,
              "checklist_sha256": hashlib.sha256(frozen_path.read_bytes()).hexdigest(),
              "evaluator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "variant_sha256": hashlib.sha256(Path(variant.__file__).read_bytes()).hexdigest(),
              "passed": passed, "total": checklist["total_checks"], "score": passed / checklist["total_checks"],
              "cases": cases, "general_proof_status": "UNVERIFIED unless separately kernel checked",
              "scope": "Positive partial Gram/occupation factorization; coefficient extraction remains unbounded."}
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps({key: report[key] for key in ("node", "sympy_version", "passed", "total", "score")}, indent=2))
    for case in cases:
        print(json.dumps({key: case[key] for key in ("n", "checks", "construction", "cb", "full_marked_terms",
                         "extracted_marked_terms", "cb_seconds", "symbolic_coefficient_seconds", "scalar_seconds",
                         "total_seconds", "error") if key in case}, indent=2))


if __name__ == "__main__":
    main()

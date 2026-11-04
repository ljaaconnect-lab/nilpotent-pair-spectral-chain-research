"""Positive exact symbolic verification for square-zero tensor/subset transfer.

The frozen checklist in sympy-checklist.json supplies the scored cases. Generic
x_ij are formal commuting scalar symbols; substituting the original marked
b_ij afterwards preserves all coefficient identities and exponents.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
from time import perf_counter

import sympy as sp

import candidate
import recurrence


def expanded(matrix):
    """Canonical polynomial entries without dense conversion."""
    return sp.MutableSparseMatrix(matrix.rows, matrix.cols,
                                  {key: sp.expand(value) for key, value in matrix.todok().items()
                                   if value != 0})


def structured_product(left, right):
    """Every scalar polynomial operation is SymPy expansion, exploiting zeros.

    This is a verification implementation and its runtime is distinct from the
    scalar circuit gate count supplied by recurrence.py.
    """
    right_rows = defaultdict(list)
    for (k, j), value in right.todok().items():
        right_rows[k].append((j, value))
    terms = defaultdict(list)
    for (i, k), value in left.todok().items():
        for j, other in right_rows[k]:
            terms[i, j].append(value * other)
    output = {key: sp.expand(sp.Add(*values)) for key, values in terms.items()}
    return sp.MutableSparseMatrix(left.rows, right.cols,
                                  {key: value for key, value in output.items() if value != 0})


def equal_polynomial(left, right):
    return sp.expand(left - right) == 0


def equal_matrix(left, right):
    if left.shape != right.shape:
        return False
    lhs, rhs = left.todok(), right.todok()
    return all(equal_polynomial(lhs.get(key, 0), rhs.get(key, 0))
               for key in lhs.keys() | rhs.keys())


def raising_subset(n, j):
    bit = 1 << j
    return sp.MutableSparseMatrix(1 << n, 1 << n,
                                  {(mask, mask | bit): 1 for mask in range(1 << n)
                                   if not mask & bit})


def raising_tensor(n, j):
    # Higher-order bit occupancy is the earlier Kronecker factor.
    raising = sp.MutableSparseMatrix([[0, 1], [0, 0]])
    identity = sp.SparseMatrix(sp.eye(2))
    factors = [raising if bit == j else identity for bit in reversed(range(n))]
    return sp.MutableSparseMatrix(sp.kronecker_product(*factors))


def weights(n):
    return [[sp.Symbol(f"x_{i}_{j}") for j in range(n)] for i in range(n)]


def generic_transfer(x):
    n = len(x)
    full = (1 << n) - 1
    entries = {(mask, mask | (1 << j)): x[mask.bit_count()][j]
               for mask in range(full) for j in range(n) if not mask & (1 << j)}
    entries[full, full] = sp.Integer(1)
    return sp.MutableSparseMatrix(1 << n, 1 << n, entries)


def generic_permanent(x):
    n = len(x)
    return sp.expand(sp.Add(*(sp.Mul(*(x[i][sigma[i]] for i in range(n)))
                              for sigma in itertools.permutations(range(n)))))


def scalar_costs(n):
    """Count actual marked scalar +/* DAGs without symbolic exponent expansion."""
    A = candidate.family_matrix(n, "identity")
    results = []
    builders = [("row_chain", recurrence.build_row_chain(A)),
                ("matrix_power_n", recurrence.build_matrix_power(A, n)),
                ("matrix_power_K", recurrence.build_matrix_power(A, n ** n - 1))]
    for name, (dag, output, stats) in builders:
        actual_gate_count = sum(node["op"] in ("add", "mul") for node in dag.nodes)
        basic_ok = (actual_gate_count == dag.gates and
                    stats["marker_and_entry_gates"] == 2 * n * n - 1 and
                    stats["dimension"] == 1 << n and
                    0 <= output < len(dag.nodes))
        if name == "row_chain":
            ok = basic_ok and dag.gates == 2 * n * n + (n - 1) * 2 ** n
        else:
            ok = (basic_ok and dag.gates == 2 * n * n - 1 + stats["matrix_product_gates"]
                  and stats["matrix_product_gates"] == sum(p["gates"] for p in stats["products"]))
        results.append({"builder": name, "accounting_pass": bool(ok), "gates": dag.gates,
                        "nodes": len(dag.nodes), "stats": stats,
                        "marking": "p_ij=1+a_ij^2; z^(2^(i*n+j)); original scalar squaring DAG"})
    return results


def expected_checks(dimensions):
    keys = []
    for n in dimensions:
        for j in range(n):
            keys.append((n, "raising_square_zero", j))
        for i in range(n):
            for j in range(i + 1, n):
                keys.append((n, "raising_pair_commutes", f"{i},{j}"))
        for j in range(n):
            keys.append((n, "tensor_raising_equals_subset_raising", j))
        for name in ("tensor_product_entry_equals_generic_permanent",
                     "transfer_nth_entry_equals_generic_permanent", "transfer_stabilizes_at_n",
                     "nonterminal_nilpotence", "scalar_initial_terminal_is_permanent"):
            keys.append((n, name, None))
        for k in range(n):
            keys.append((n, "scalar_early_zero", k))
        for k in range(n + 1):
            keys.append((n, "scalar_tail_recurrence", k))
        for name in ("row_chain", "matrix_power_n", "matrix_power_K"):
            keys.append((n, "marked_scalar_cost_accounting", name))
    return keys


def inspect_dimension(n, record):
    start = perf_counter()
    r = 1 << n
    full = r - 1
    zero = sp.MutableSparseMatrix(r, r, {})
    raising = [raising_subset(n, j) for j in range(n)]
    for j, operator in enumerate(raising):
        record(n, "raising_square_zero", j, equal_matrix(operator * operator, zero))
    for i in range(n):
        for j in range(i + 1, n):
            record(n, "raising_pair_commutes", f"{i},{j}",
                   equal_matrix(raising[i] * raising[j], raising[j] * raising[i]))
    for j in range(n):
        record(n, "tensor_raising_equals_subset_raising", j,
               equal_matrix(raising_tensor(n, j), raising[j]))
    raising_seconds = perf_counter() - start

    x = weights(n)
    permanent = generic_permanent(x)
    tensor_start = perf_counter()
    tensor_product = sp.MutableSparseMatrix(sp.eye(r))
    for i in range(n):
        row_operator = sp.MutableSparseMatrix(r, r, {})
        for j in range(n):
            row_operator += x[i][j] * raising[j]
        tensor_product = structured_product(tensor_product, row_operator)
    record(n, "tensor_product_entry_equals_generic_permanent", None,
           equal_polynomial(tensor_product[0, full], permanent))
    tensor_seconds = perf_counter() - tensor_start

    transfer_start = perf_counter()
    M = generic_transfer(x)
    powers = [sp.MutableSparseMatrix(sp.eye(r))]
    for _ in range(2 * n + 1):
        powers.append(structured_product(powers[-1], M))
    record(n, "transfer_nth_entry_equals_generic_permanent", None,
           equal_polynomial(powers[n][0, full], permanent))
    record(n, "transfer_stabilizes_at_n", None, equal_matrix(powers[n + 1], powers[n]))
    # N excludes the terminal state. These are genuine symbolic matrix powers.
    N = sp.MutableSparseMatrix(full, full,
                               {(i, j): value for (i, j), value in M.todok().items()
                                if i != full and j != full})
    nilpotent = sp.MutableSparseMatrix(sp.eye(full))
    for _ in range(n):
        nilpotent = structured_product(nilpotent, N)
    record(n, "nonterminal_nilpotence", None,
           equal_matrix(nilpotent, sp.MutableSparseMatrix(full, full, {})))
    for k in range(n):
        record(n, "scalar_early_zero", k, equal_polynomial(powers[k][0, full], 0))
    record(n, "scalar_initial_terminal_is_permanent", None,
           equal_polynomial(powers[n][0, full], permanent))
    for k in range(n + 1):
        record(n, "scalar_tail_recurrence", k,
               equal_polynomial(powers[k + n + 1][0, full], powers[k + n][0, full]))
    transfer_seconds = perf_counter() - transfer_start

    costs = scalar_costs(n)
    for cost in costs:
        record(n, "marked_scalar_cost_accounting", cost["builder"], cost["accounting_pass"])
    return {"n": n, "dimension": r, "K": n ** n - 1,
            "raising_seconds": raising_seconds, "tensor_seconds": tensor_seconds,
            "transfer_seconds": transfer_seconds, "total_seconds": perf_counter() - start,
            "transfer_nonzeros": len(M.todok()),
            "stable_power_nonzeros": len(powers[n].todok()),
            "terminal_expression_terms": len(sp.Add.make_args(permanent)),
            "positive_recurrence": "a_k=0 (k<n), a_k=P(x) (k>=n); a_(k+n+1)=a_(k+n)",
            "initialization_constraint": "a_n=P(x) is the target and is not cheaply supplied by this recurrence",
            "scalar_costs": costs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("sympy-report.json"))
    args = parser.parse_args()
    checklist_path = Path(__file__).with_name("sympy-checklist.json")
    frozen = json.loads(checklist_path.read_text())
    expected = expected_checks(frozen["dimensions"])
    assert len(expected) == frozen["total_checks"] == 112
    checks = {key: {"n": key[0], "check": key[1], "instance": key[2], "passed": False,
                    "diagnostic": "not executed"} for key in expected}

    def record(n, name, instance, passed):
        key = (n, name, instance)
        assert key in checks
        assert checks[key]["diagnostic"] == "not executed"
        checks[key].update(passed=bool(passed), diagnostic="exact symbolic equality" if passed
                           else "positive invariant did not verify")

    cases = []
    for n in frozen["dimensions"]:
        try:
            cases.append(inspect_dimension(n, record))
        except Exception as error:
            cases.append({"n": n, "infrastructure_or_verification_error": repr(error)})
            for key, item in checks.items():
                if key[0] == n and item["diagnostic"] == "not executed":
                    item["diagnostic"] = repr(error)
    passed = sum(item["passed"] for item in checks.values())
    report = {"artifact_version": frozen["artifact_version"], "boundary": frozen["boundary"],
              "checklist_sha256": hashlib.sha256(checklist_path.read_bytes()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "sympy_version": sp.__version__, "passed": passed, "total": len(checks),
              "score": passed / len(checks), "checks": list(checks.values()), "cases": cases,
              "general_claim_status": "UNVERIFIED by Lean in this leaf",
              "scope": "Positive exact finite symbolic verification; no original-target theorem claim."}
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps({key: report[key] for key in ("artifact_version", "boundary", "sympy_version",
                                                 "passed", "total", "score", "checklist_sha256")}, indent=2))
    for case in cases:
        print(json.dumps(case, indent=2))


if __name__ == "__main__":
    main()

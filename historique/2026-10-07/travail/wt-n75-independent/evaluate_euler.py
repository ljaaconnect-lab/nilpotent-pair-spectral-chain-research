"""Frozen n61 development assertions, separate from diagnostic variants.

Each child validation has a 120-second subprocess limit. No held-out cases
are read, and the scalar compiler never obtains its answer from the oracle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from itertools import permutations
from math import prod
from pathlib import Path
from time import perf_counter

import sympy as sp

from euler_identity import permutation_polys, inversion_sign
from euler_compiler import (cofactor_graph, cofactor_sign, evaluate_generic,
    mark_graph, marked_oracle, naive_formula, naive_graph_n2,
    shared_specializations, seed_gate_count)


ROOT = Path(__file__).resolve().parent
SOURCE_FILES = ["euler_identity.py", "validate_euler_identity.py",
                "euler_compiler.py", "evaluate_euler.py", "candidate.py"]


def hashes():
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
            for name in SOURCE_FILES+["n61-protocol.json"]}


def audit(graph, output, variables):
    gates = 0
    variable_set = set()
    max_num_bits = max_den_bits = 0
    for i,node in enumerate(graph.nodes):
        op = node["op"]
        if op in ("add","mul"):
            if not (0 <= node["left"] < i and 0 <= node["right"] < i):
                return False, {}
            gates += 1
        elif op == "variable":
            variable_set.add(node["name"])
        elif op == "constant":
            constant = Fraction(node["value"])
            max_num_bits = max(max_num_bits, abs(constant.numerator).bit_length())
            max_den_bits = max(max_den_bits, constant.denominator.bit_length())
        else:
            return False, {}
    return gates == graph.gates and variable_set <= set(variables) and 0 <= output < len(graph.nodes), {
        "gates_from_nodes": gates, "variables": sorted(variable_set),
        "maximum_constant_numerator_bits": max_num_bits,
        "maximum_constant_denominator_bits": max_den_bits,
        "no_unknown_target_leaf": True,
        "allowed_constants": "determinant rational recurrence constants, universal integer projector coefficients, prescribed p=1+a^2"}


def cofactor_identity(n, alpha):
    """Validate each used local factorization independently by permutations."""
    x,det,_ = permutation_polys(n)
    validated = 0
    for matching in alpha:
        selected = sorted(matching)
        # Filter determinant terms: this is ONLY an identity oracle, not codegen.
        projected = sp.Poly.from_dict({powers: coefficient for powers,coefficient in det.terms()
                        if all(powers[cell] for cell in selected)}, x)
        rows = [i for i in range(n) if all(cell//n != i for cell in matching)]
        cols = [j for j in range(n) if all(cell%n != j for cell in matching)]
        minor = 0
        for sigma in permutations(range(len(rows))):
            minor += inversion_sign(sigma)*prod(x[rows[i]*n+cols[sigma[i]]] for i in range(len(rows)))
        expression = cofactor_sign(n,matching)*prod(x[cell] for cell in matching)*minor
        if projected != sp.Poly(expression,*x):
            return False, {"verified_local_cofactors": validated, "failed_matching": selected}
        validated += 1
    return True, {"verified_local_cofactors": validated,
                  "scope": "Finite exact local identities, independent of scalar compiler evaluation"}


def validation(n):
    started = perf_counter()
    identity = json.loads((ROOT/f"n61-identity-n{n}.json").read_text())
    source_hashes = hashes()
    checks = {"euler_diagonal_identity": identity["euler_diagonal_identity"],
              "grouped_row_identity": identity["grouped_row_identity"]}
    graph,output,metadata,alpha = cofactor_graph(n)
    checks["partial_matching_cofactor_identity"], cofactor_stats = cofactor_identity(n,alpha)
    actual,generic_stats = evaluate_generic(graph,output,n)
    _,_,permanent = permutation_polys(n)
    checks["final_cofactor_scalar_DAG_generic_evaluation"] = (actual-permanent).is_zero
    A = [[Fraction(i+1,j+2) for j in range(n)] for i in range(n)]
    marked,marked_output = mark_graph(graph,output,A)
    marked_value,marked_stats = marked.evaluate(marked_output)
    checks["final_marked_formal_z_evaluation"] = all(t == 0 for t,z in marked_value) and {
        z:coefficient for (t,z),coefficient in marked_value.items()} == marked_oracle(A)
    generic_ok,generic_audit = audit(graph,output,[f"x{e}" for e in range(n*n)])
    marked_ok,marked_audit = audit(marked,marked_output,["z"])
    # Serialize and read back the actual graphs; gate count is derived anew.
    artifacts = {}
    for label,dag,out in (("generic",graph,output),("marked",marked,marked_output)):
        path = ROOT/f"n61-{label}-dag-n{n}.json"
        path.write_text(json.dumps({"n": n, "artifact": "shared_cofactor_matchings",
                                   **dag.serialize(out)},indent=2))
        serialized = json.loads(path.read_text())
        roundtrip = serialized["nodes"] == dag.nodes and serialized["gates"] == sum(
            node["op"] in ("add","mul") for node in serialized["nodes"])
        generic_ok = generic_ok and roundtrip
        artifacts[label] = {"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    checks["serialized_topology_count_input_audit"] = generic_ok and marked_ok
    return {"n": n, "variant": "shared_cofactor_matchings", "checks": checks,
        "passed": sum(checks.values()), "total": 6,
        "generic_gates": graph.gates, "marked_gates": marked.gates,
        "generic_counts": graph.counts(), "marked_counts": marked.counts(),
        "construction": metadata, "cofactor_identity": cofactor_stats,
        "generic_evaluation": generic_stats, "marked_evaluation": marked_stats,
        "generic_audit": generic_audit, "marked_audit": marked_audit,
        "elapsed_seconds": perf_counter()-started, "source_hashes": source_hashes,
        "artifacts": artifacts, "scope": "Exact finite validation; not a polynomial bound or kernel theorem"}


def diagnostic(n):
    started = perf_counter()
    naive = naive_formula(n)
    if n == 2:
        graph,output = naive_graph_n2()
        value,stats = evaluate_generic(graph,output,n)
        naive.update({"materialized": True, "actual_gates": graph.gates,
            "actual_generic_identity": (value-permutation_polys(n)[2]).is_zero, "evaluation": stats})
        path = ROOT/"n61-naive-dag-n2.json"
        path.write_text(json.dumps(graph.serialize(output),indent=2))
    else:
        naive["materialized"] = False
    graph,output,shared = shared_specializations(n)
    if graph is not None:
        value,stats = evaluate_generic(graph,output,n)
        shared.update({"actual_generic_identity": (value-permutation_polys(n)[2]).is_zero,
                       "evaluation": stats, "counts": graph.counts()})
        path = ROOT/f"n61-specialization-dag-n{n}.json"
        path.write_text(json.dumps(graph.serialize(output),indent=2))
    return {"n": n, "naive_specializations": naive, "shared_row_specializations": shared,
            "elapsed_seconds": perf_counter()-started, "source_hashes": hashes(),
            "scope": "Separate diagnostics, no denominator change; cap is a resource constraint of this run"}


def run_child(mode,n):
    command = [sys.executable,str(Path(__file__).resolve()),"--child",mode,"--n",str(n)]
    try:
        completed = subprocess.run(command,cwd=ROOT,timeout=120,capture_output=True,text=True)
        log = {"command": command, "exit_code": completed.returncode,
               "stdout": completed.stdout,"stderr": completed.stderr}
    except subprocess.TimeoutExpired as error:
        log = {"command": command,"status": "timeout","exit_code": None,
               "stdout": (error.stdout or b"").decode() if isinstance(error.stdout,bytes) else error.stdout,
               "stderr": (error.stderr or b"").decode() if isinstance(error.stderr,bytes) else error.stderr}
    (ROOT/f"n61-{mode}-log-n{n}.json").write_text(json.dumps(log,indent=2))
    report_path = ROOT/f"n61-{mode}-n{n}.json"
    return json.loads(report_path.read_text()) if log.get("exit_code") == 0 else {
        "n":n,"status":"failed_or_timeout","total":6 if mode == "validation" else 0,"passed":0,"log":log}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n",type=int)
    parser.add_argument("--child",choices=("validation","diagnostic"))
    parser.add_argument("--mode",choices=("validation","diagnostic","aggregate"),default="validation")
    args = parser.parse_args()
    if args.child:
        result = validation(args.n) if args.child == "validation" else diagnostic(args.n)
        (ROOT/f"n61-{args.child}-n{args.n}.json").write_text(json.dumps(result,indent=2))
        print(json.dumps({"n":args.n,"mode":args.child,"result":result.get("checks",{
            "shared":result["shared_row_specializations"]["status"]} if args.child == "diagnostic" else {})},indent=2),flush=True)
        return
    if args.mode == "aggregate":
        validations = [json.loads((ROOT/f"n61-validation-n{n}.json").read_text()) for n in (2,3,4,5)]
        diagnostics = [json.loads((ROOT/f"n61-diagnostic-n{n}.json").read_text()) for n in (2,3,4,5)]
        report = {"node":"n61","artifact_version":"n61-euler-cofactor-v1","boundary":"B_dev",
            "frozen_denominator":24,"passed":sum(v["passed"] for v in validations),
            "dev_score":sum(v["passed"] for v in validations)/24,
            "validations":validations,"diagnostics":diagnostics,"source_hashes":hashes(),
            "selected_variant":"shared_cofactor_matchings",
            "held_out_access":False,"root_conjecture_proved":False,
            "scope":"Exact finite scalar DAG correctness and costs; universal polynomial compression remains unproved"}
        (ROOT/"n61-dev-report.json").write_text(json.dumps(report,indent=2))
        print(json.dumps({key:report[key] for key in ("node","passed","frozen_denominator","dev_score","source_hashes")},indent=2))
    else:
        result = run_child(args.mode,args.n)
        print(json.dumps({"n":args.n,"mode":args.mode,"passed":result.get("passed"),"total":result.get("total"),
            "generic_gates":result.get("generic_gates"),"marked_gates":result.get("marked_gates"),
            "status":result.get("status","complete")},indent=2),flush=True)


if __name__ == "__main__":
    main()

"""Frozen positive development evaluator; no Lean or held-out access."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
from time import perf_counter

from direct_corrected_circuit import build_corrected, evaluate_at

ROOT = Path(__file__).resolve().parent


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def canonical_hash(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    return sha256(text.encode("utf-8")).hexdigest()


def assert_source_freeze():
    freeze = read_json(ROOT/"n77-source-freeze.json")
    for name, expected in freeze["files"].items():
        actual = canonical_hash(ROOT/name)
        if actual != expected["sha256_utf8_lf_without_bom"]:
            raise ValueError(f"Frozen source changed: {name}")
    return freeze


def oracle(A, z) -> Fraction:
    """Independent direct permutation sum, not the subset recurrence."""
    n = len(A)
    z = Fraction(z)
    answer = Fraction(0)
    for sigma in permutations(range(n)):
        weight = Fraction(1)
        exponent = 0
        for i, j in enumerate(sigma):
            a = Fraction(A[i][j])
            weight *= Fraction(1)+a**2
            exponent += 1 << (i*n+j)
        answer += weight*z**exponent
    return answer


def input_matrix(n, family):
    if family == "identity":
        return [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    if family == "Vandermonde":
        return [[Fraction((i+1)**j) for j in range(n)] for i in range(n)]
    if family == "cycle":
        return [[Fraction(int(j == (i+1) % n)) for j in range(n)]
                for i in range(n)]
    raise ValueError("Family is outside the frozen positive boundary")


def structural_audit(circuit):
    n = circuit["n"]
    nodes, states = circuit["nodes"], circuit["states"]
    failures = []

    def require(condition, message):
        if not condition:
            failures.append(message)

    require(len(states) == 1 << n, "State dimension")
    require(states[0]["output"] == 0 and nodes[0] == {"op": "constant", "value": "1"},
            "Initialized empty state")
    inputs = {"z"} | {f"p_{i}_{j}" for i in range(n) for j in range(n)}
    require({node["name"] for node in nodes if node["op"] == "variable"} == inputs,
            "Only prescribed input leaves")
    constants = [Fraction(node["value"]) for node in nodes if node["op"] == "constant"]
    require(constants == [Fraction(1)], "Only literal one, no target constants")
    operations = Counter()
    stages = Counter()
    for index, node in enumerate(nodes):
        op = node["op"]
        require(op in ("constant", "variable", "add", "mul"), "Forbidden operation")
        if op in ("add", "mul"):
            require(0 <= node["left"] < index and 0 <= node["right"] < index,
                    "Backward topology")
            operations[op] += 1
            stages[(node["stage"], op)] += 1

    marker = circuit["markers"]
    require(len(marker) == n*n and marker[0] == circuit["inputs"]["z"],
            "Marker origin")
    for exponent in range(1, n*n):
        node = nodes[marker[exponent]]
        require(node == {"op": "mul", "left": marker[exponent-1],
                         "right": marker[exponent-1], "stage": "marker_powers"},
                "Shared square marker chain")
    for i in range(n):
        for j in range(n):
            node = nodes[circuit["marked_entries"][i][j]]
            require(node == {"op": "mul", "left": circuit["inputs"]["p"][i][j],
                             "right": marker[i*n+j], "stage": "entry_weights"},
                    "Original edge marker weight")

    for mask, state in enumerate(states):
        require(state["mask"] == mask and state["cardinality"] == mask.bit_count(),
                "Mask/cardinality schedule")
        if mask == 0:
            require(state["row"] is None and not state["terms"] and not state["sums"],
                    "Empty state has no unknown initialization")
            continue
        row = mask.bit_count()-1
        require(state["row"] == row, "Row is cardinality minus one")
        columns = [j for j in range(n) if mask & (1 << j)]
        require([term["column"] for term in state["terms"]] == columns,
                "Every available column exactly once")
        for term in state["terms"]:
            j, child = term["column"], term["child"]
            require(child == mask ^ (1 << j), "Shared erased child")
            require(nodes[term["node"]] == {
                "op": "mul", "left": circuit["marked_entries"][row][j],
                "right": states[child]["output"], "stage": "subset"},
                "Scalar transition, including singleton times one")
        current = state["terms"][0]["node"]
        require(len(state["sums"]) == len(columns)-1, "Binary sum length")
        for output, term in zip(state["sums"], state["terms"][1:]):
            require(nodes[output] == {"op": "add", "left": current,
                                      "right": term["node"], "stage": "subset"},
                    "Actual scalar binary addition")
            current = output
        require(state["output"] == current, "State output")
    require(circuit["output"] == states[-1]["output"], "Complete full-set output")

    ancestors = set()
    pending = [circuit["output"]]
    while pending:
        index = pending.pop()
        if index not in ancestors:
            ancestors.add(index)
            node = nodes[index]
            if node["op"] in ("add", "mul"):
                pending.extend([node["left"], node["right"]])
    require(len(ancestors) == len(nodes), "Every emitted node contributes to terminal")

    edges = n*(1 << (n-1))
    expected = {("marker_powers", "mul"): n*n-1,
                ("entry_weights", "mul"): n*n,
                ("subset", "mul"): edges,
                ("subset", "add"): edges-((1 << n)-1)}
    require(all(stages[key] == value for key, value in expected.items()),
            "All-stage exact gate counts")
    require(sum(operations.values()) == (n-1)*(1 << n)+2*n*n,
            "Complete marked scalar count")
    require(circuit["counts"]["arithmetic"] == sum(operations.values()),
            "Recorded versus inspected count")
    require(circuit["counts"]["edges"] == edges, "Transition edge count")
    return {"pass": not failures, "failures": failures,
            "n": n, "states": len(states), "nodes": len(nodes),
            "edges": edges, "measured_add": operations["add"],
            "measured_mul": operations["mul"],
            "measured_total": sum(operations.values()),
            "measured_stages": circuit["counts"]["stages"],
            "recurrence_only_gates": stages[("subset", "add")]+stages[("subset", "mul")],
            "literal_values": [str(value) for value in constants],
            "literal_fraction_bits": [abs(value.numerator).bit_length()+
                                      value.denominator.bit_length() for value in constants],
            "all_nodes_reach_output": len(ancestors) == len(nodes)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default="n77-dev-report.json")
    args = parser.parse_args()
    if Path(args.report).name != args.report:
        raise ValueError("Report must be a filename in this isolated worktree")
    freeze = assert_source_freeze()  # Before ANY construction or interpretation.
    boundary = read_json(ROOT/"n77-dev-boundary.json")
    started = perf_counter()
    circuits = {}
    structures = []
    for n in boundary["serialized_n"]:
        circuit = build_corrected(n)
        circuits[n] = circuit
        path = ROOT/f"n77-direct-dag-n{n}.json"
        path.write_text(json.dumps(circuit, indent=2)+"\n", encoding="utf-8")
        structures.append(structural_audit(circuit))

    cases = []
    for n in boundary["evaluation_n"]:
        for family in boundary["families"]:
            A = input_matrix(n, family)
            for z in boundary["z_values"]:
                case_started = perf_counter()
                actual, stats = evaluate_at(circuits[n], A, Fraction(z))
                expected = oracle(A, Fraction(z))
                gates_pass = stats["arithmetic_nodes_evaluated"] == circuits[n]["counts"]["arithmetic"]
                bit_provenance_pass = stats["max_prescribed_p_bits"] <= 4*stats["max_input_A_bits"]+1
                cases.append({"n": n, "family": family, "z": z,
                              "A": [[str(value) for value in row] for row in A],
                              "actual": str(actual), "permutation_reference": str(expected),
                              "output_pass": actual == expected,
                              "all_gates_executed": gates_pass,
                              "parameter_bit_provenance_pass": bit_provenance_pass,
                              "statistics": stats,
                              "seconds": round(perf_counter()-case_started, 6)})

    topology = all(item["pass"] for item in structures)
    budgets = topology and all(case["all_gates_executed"] for case in cases)
    provenance = topology and all(case["parameter_bit_provenance_pass"] for case in cases)
    terminal = len(cases) == boundary["positive_cases"] and all(case["output_pass"] for case in cases)
    obligations = [topology, budgets, provenance, terminal]
    report = {"node": "n77", "artifact_version": boundary["artifact_version"],
              "target": "Complete direct PA(z)=Cn DA(z)",
              "local_obligations": [{"name": name, "pass": passed}
                                     for name, passed in zip(boundary["local_obligations"], obligations)],
              "local_passed": sum(obligations), "local_total": 4,
              "dev_score": sum(obligations)/4,
              "root_score": 0, "root_conjecture_verified": False,
              "root_limitation": "2^n explicitly constructed subset states; no polynomial compression supplied",
              "source_freeze": freeze, "structures": structures,
              "positive_cases_passed": sum(case["output_pass"] for case in cases),
              "positive_cases_total": len(cases), "cases": cases,
              "seconds": round(perf_counter()-started, 6),
              "Lean_invocations": 0, "Lean_probes": 0, "Lean_builds": 0,
              "held_out_reads": 0, "counterexample_campaigns": 0,
              "lower_bound_experiments": 0,
              "central_coefficient_extraction_calls": 0,
              "formal_scope": "Existing n73 recurrence semantics reused; Python lowering receives code checks only, no new Lean compiler theorem"}
    (ROOT/args.report).write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    summary = {key: report[key] for key in ("node", "artifact_version", "dev_score",
               "root_score", "positive_cases_passed", "positive_cases_total", "seconds")}
    summary["measured_marked_gates"] = {str(item["n"]): item["measured_total"] for item in structures}
    print(json.dumps(summary))
    if not all(obligations):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

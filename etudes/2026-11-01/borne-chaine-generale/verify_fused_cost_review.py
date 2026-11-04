"""Audit the direct fused scalar DAG; do not execute jets or logarithms.

This checks finite gate counts and sharing, not a general polynomial closure.
The existing compiler is instrumented in memory; its source is unchanged.
"""
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
COMPILER = HERE.parent / "fusion-double-log" / "fused_circuit.py"
HELPER = HERE.parent / "logarithmes-chaine" / "log_circuit.py"
DAG_SOURCE = (HERE.parent / "raccord-initialisation" / "spectral"
              / "reprise-globale" / "shared_operator_dag.py")
REPORT = HERE / "fused-cost-review-validation.json"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def forbidden_coordinate_operation(*args, **kwargs):
    raise AssertionError("The direct audit must not execute jets or logarithms")


def main():
    source = COMPILER.read_text(encoding="utf-8")
    anchor = "    coefficient = dag.substitute([root], {x: dag.one for x in s})[0]\n"
    assert source.count(anchor) == 1, "Compiler changed: audit anchor is ambiguous"
    instrumentation = anchor + """    assert mode == 'direct'
    prefix_reachable = dag.reachable([coefficient])
    nodes_before_row_lookup = len(dag.nodes)
    audit_rows = [dag.sum(row) for row in B]
    assert len(dag.nodes) == nodes_before_row_lookup, 'Row sums must already exist'
    assert all(row in prefix_reachable for row in audit_rows), 'Row sums must be shared'
    stages.append({'audit_specialized_prefix_gates': dag.count([coefficient]),
                   'audit_row_sum_roots_reachable': len(audit_rows)})
"""
    namespace = {"__file__": str(COMPILER), "__name__": "audit_direct_fused"}
    exec(compile(source.replace(anchor, instrumentation), str(COMPILER), "exec"), namespace)
    # The historical module contains other modes. Reject any accidental call
    # to their coordinate helpers during this direct-mode audit.
    rejected_helpers = sorted(name for name in namespace if name.startswith("jet_"))
    for name in rejected_helpers:
        namespace[name] = forbidden_coordinate_operation
    rows = []
    for n in range(3, 7):
        N = 1 << n.bit_length()
        dag, outputs, coordinates, stages = namespace["compile_fused"](
            n, 97, N, list(range(n)), mode="direct", budget=3_000_000)
        assert coordinates == [], "Direct mode must not construct coordinate arrays"
        prefix = next(stage for stage in stages if "audit_specialized_prefix_gates" in stage)
        prefix_gates = prefix["audit_specialized_prefix_gates"]
        full_gates = dag.count(outputs)
        added_gates = full_gates - prefix_gates
        bound = 4*n*n - 3*n + 2
        assert 0 <= added_gates <= bound, (n, added_gates, bound)
        assert prefix["audit_row_sum_roots_reachable"] == n
        assert all(dag.nodes[idx][0] in ("c", "v", "+", "*")
                   for idx in dag.reachable(outputs))
        assert all(dag.nodes[idx][0] != "v" or not dag.nodes[idx][1].startswith("s_")
                   for idx in dag.reachable(outputs))
        rows.append({"n": n, "Q": 97, "N": N, "labels": list(range(n)),
                     "prefix_gates_including_B_preparation": prefix_gates,
                     "full_gates": full_gates, "added_gates": added_gates,
                     "additional_gate_bound": bound,
                     "row_sum_roots_reachable_before_correction": n})
    expected = [(43, 72), (316, 362), (2776, 2858), (20278, 20394)]
    assert [(row["prefix_gates_including_B_preparation"], row["full_gates"])
            for row in rows] == expected
    dependencies = [COMPILER, HELPER, DAG_SOURCE]
    report = {
        "status": "pass",
        "scope": {
            "mode": "direct",
            "general_polynomial_closure": False,
            "finite_gate_count_and_sharing_audit": True,
            "jets_or_logarithms_executed": False,
            "historical_sources_modified": False,
            "lean_proof": False,
        },
        "gate_model": "Scalar binary + and *; multiplication by a constant counts",
        "additional_gate_bound": "4*n^2 - 3*n + 2, for n >= 3",
        "bound_without_reusing_row_sums": "5*n^2 - 4*n + 2",
        "source": {"path": Path(__file__).resolve().relative_to(REPO).as_posix(),
                   "sha256": digest(Path(__file__))},
        "dependencies": [{"path": path.relative_to(REPO).as_posix(),
                          "sha256": digest(path)} for path in dependencies],
        "guarded_coordinate_helpers": rejected_helpers,
        "cases": rows,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "cases": rows,
                      "general_polynomial_closure": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""Explicit shared binary-multiplication SSA plans with supplied initial a.

This exporter witnesses the formal instruction convention. Input construction
and scalar compilation of each monoid multiplication are separate costs.
"""
import argparse
import json
from pathlib import Path


def instructions(k):
    if k < 0:
        raise ValueError("natural exponent required")
    if k <= 1:
        return []
    return instructions(k // 2) + (["square"] if k % 2 == 0 else ["square", "multiplyBase"])


def shared_dag(k):
    nodes = [{"op": "identity_leaf", "value": "one"},
             {"op": "input_leaf", "value": "explicit initial a"}]
    current = 0 if k == 0 else 1
    ops = instructions(k)
    for op in ops:
        previous = current
        current = len(nodes)
        nodes.append({"op": "mul", "left": previous,
                      "right": previous if op == "square" else 1})
    logarithm = max(0, k.bit_length() - 1)
    assert len(ops) <= 2 * logarithm
    assert sum(node["op"] == "mul" for node in nodes) == len(ops)
    return {"exponent": k, "instructions": ops, "output": current, "nodes": nodes,
            "multiplications": len(ops), "log2": logarithm,
            "initialization": "a is explicitly supplied; its cost is not included",
            "scope": "Shared monoid multiplication graph, not a circuit for the research target"}


def dense_scalar_cost(r, k, initial_gates=0, u_gates=0, v_gates=0, coordinate_output=False):
    if r < 1:
        raise ValueError("positive matrix dimension required for this dense convention")
    L = len(instructions(k))
    product_cost = r ** 3 + r ** 2 * (r - 1)
    contraction = 0 if coordinate_output else 2 * r ** 2 + r - 1
    return {"dimension": r, "input_gates": initial_gates,
            "u_gates": u_gates, "v_gates": v_gates,
            "monoid_multiplications": L, "dense_product_scalar_gates": product_cost,
            "final_contraction_gates": contraction,
            "total": initial_gates + u_gates + v_gates + L * product_cost + contraction,
            "logarithmic_upper_bound": initial_gates + u_gates + v_gates
                + 2 * max(0, k.bit_length() - 1) * product_cost + contraction,
            "conditional_data": "Requires explicit r-by-r matrix, initial u,v circuits and appropriate scalar algebra; no cheap representation is asserted"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("power-dag-examples.json"))
    args = parser.parse_args()
    report = {"artifact_version": "n40-shared-binary-power-v1",
              "examples": [shared_dag(k) for k in (0, 1, 2, 3, 26, 255, 3124)],
              "scalar_bound": "s_init+s_u+s_v+2*log2(k)*(2*r^3-r^2)+(2*r^2+r-1)",
              "coordinate_output_adjustment": "A fixed matrix entry costs no contraction gates",
              "unknown_root_data": "No polynomial dimension/initial-data construction for the root target has been established here"}
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"examples": len(report["examples"]), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()

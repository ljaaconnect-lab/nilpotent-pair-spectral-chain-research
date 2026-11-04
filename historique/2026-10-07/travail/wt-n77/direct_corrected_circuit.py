"""Complete scalar subset reference for the DIRECT corrected polynomial.

Leaves are the prescribed p_ij=1+a_ij**2, formal z, and the short literal
1. Every internal node is a binary add or mul with earlier operands.
There is no sign-corrector, coefficient, derivative, determinant, division,
or auxiliary-ring operation in this DAG. The circuit is exponential.

The Python lowering is not a new Lean compiler theorem. Its mathematical
recurrence is the independently verified n73 subset/marked-target reference.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


class ScalarDAG:
    def __init__(self):
        self.nodes: list[dict] = []

    def literal_one(self) -> int:
        node = len(self.nodes)
        self.nodes.append({"op": "constant", "value": "1"})
        return node

    def variable(self, name: str) -> int:
        node = len(self.nodes)
        self.nodes.append({"op": "variable", "name": name})
        return node

    def binary(self, op: str, left: int, right: int, stage: str) -> int:
        if op not in ("add", "mul"):
            raise ValueError("Only scalar addition/multiplication is allowed")
        node = len(self.nodes)
        if not (0 <= left < node and 0 <= right < node):
            raise ValueError("Every operand must be an earlier DAG node")
        self.nodes.append({"op": op, "left": left, "right": right,
                           "stage": stage})
        return node


def count_stages(nodes: list[dict]) -> dict:
    result = {stage: {"add": 0, "mul": 0, "total": 0}
              for stage in ("marker_powers", "entry_weights", "subset")}
    for node in nodes:
        if node["op"] in ("add", "mul"):
            record = result[node["stage"]]
            record[node["op"]] += 1
            record["total"] += 1
    return result


def build_corrected(n: int) -> dict:
    """Uniform executable recipe for all n>=1, output full PA(z)=Cn DA(z)."""
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")
    graph = ScalarDAG()
    one = graph.literal_one()
    z = graph.variable("z")
    p = [[graph.variable(f"p_{i}_{j}") for j in range(n)] for i in range(n)]

    # Shared marker construction uses precisely n^2-1 scalar squarings.
    marker = [z]
    for _ in range(1, n*n):
        marker.append(graph.binary("mul", marker[-1], marker[-1],
                                   "marker_powers"))
    marked = [[graph.binary("mul", p[i][j], marker[i*n+j], "entry_weights")
               for j in range(n)] for i in range(n)]

    outputs = [one]
    states = [{"mask": 0, "cardinality": 0, "row": None,
               "output": one, "terms": [], "sums": []}]
    # Removing a nonzero bit decreases a mask, so every child is shared.
    for mask in range(1, 1 << n):
        cardinality = mask.bit_count()
        row = cardinality-1
        terms = []
        sums = []
        term_records = []
        for j in range(n):
            if mask & (1 << j):
                child = mask ^ (1 << j)
                term = graph.binary("mul", marked[row][j], outputs[child],
                                    "subset")
                terms.append(term)
                term_records.append({"column": j, "child": child,
                                     "node": term})
        output = terms[0]
        for term in terms[1:]:
            output = graph.binary("add", output, term, "subset")
            sums.append(output)
        outputs.append(output)
        states.append({"mask": mask, "cardinality": cardinality, "row": row,
                       "output": output, "terms": term_records, "sums": sums})

    return {"model": "Q[z], prescribed p_ij input leaves, binary add/mul",
            "target": "complete PA(z)=Cn(DA(z)); direct subset reference",
            "n": n, "nodes": graph.nodes, "output": outputs[-1],
            "inputs": {"z": z, "p": p}, "markers": marker,
            "marked_entries": marked, "states": states,
            "counts": {"nodes": len(graph.nodes), "states": len(states),
                       "edges": sum(len(s["terms"]) for s in states),
                       "stages": count_stages(graph.nodes),
                       "arithmetic": sum(node["op"] in ("add", "mul")
                                         for node in graph.nodes)}}


def prescribed_bindings(A, z) -> dict[str, Fraction]:
    n = len(A)
    if n < 1 or any(len(row) != n for row in A):
        raise ValueError("A must be a nonempty square rational matrix")
    result = {"z": Fraction(z)}
    for i in range(n):
        for j in range(n):
            a = Fraction(A[i][j])
            result[f"p_{i}_{j}"] = Fraction(1)+a*a
    return result


def fraction_bits(value: Fraction) -> int:
    return abs(value.numerator).bit_length()+value.denominator.bit_length()


def evaluate_at(circuit: dict, A, z) -> tuple[Fraction, dict]:
    """Evaluate EVERY real scalar node; no target or state oracle is called."""
    if len(A) != circuit["n"]:
        raise ValueError("Input matrix dimension does not match the circuit")
    bindings = prescribed_bindings(A, z)
    values: list[Fraction] = []
    arithmetic = 0
    max_bits = 0
    for index, node in enumerate(circuit["nodes"]):
        op = node["op"]
        if op == "constant":
            value = Fraction(node["value"])
        elif op == "variable":
            value = bindings[node["name"]]
        elif op in ("add", "mul"):
            left, right = node["left"], node["right"]
            if not (0 <= left < index and 0 <= right < index):
                raise ValueError("Invalid scalar DAG topology")
            value = (values[left]+values[right] if op == "add"
                     else values[left]*values[right])
            arithmetic += 1
        else:
            raise ValueError(f"Forbidden node kind {op}")
        values.append(value)
        max_bits = max(max_bits, fraction_bits(value))
    return values[circuit["output"]], {
        "arithmetic_nodes_evaluated": arithmetic,
        "max_intermediate_fraction_bits": max_bits,
        "max_prescribed_p_bits": max(fraction_bits(value)
                                      for key, value in bindings.items()
                                      if key.startswith("p_")),
        "max_input_A_bits": max(fraction_bits(Fraction(a))
                                for row in A for a in row)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    circuit = build_corrected(args.n)
    args.output.write_text(json.dumps(circuit, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"n": args.n, "output": str(args.output),
                      "counts": circuit["counts"]}))


if __name__ == "__main__":
    main()

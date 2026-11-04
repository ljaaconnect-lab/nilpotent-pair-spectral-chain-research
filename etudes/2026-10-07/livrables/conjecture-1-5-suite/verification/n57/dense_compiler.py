"""Scalar SSA compiler for supplied u^T M^k v; no target-dependent inputs."""
import json
from pathlib import Path

from power_plan import instructions


class Builder:
    def __init__(self):
        self.nodes = []

    def input(self, name):
        idx = len(self.nodes)
        self.nodes.append({"op": "input", "name": name})
        return idx

    def const(self, value):
        idx = len(self.nodes)
        self.nodes.append({"op": "constant", "value": value})
        return idx

    def gate(self, op, left, right):
        idx = len(self.nodes)
        if not (0 <= left < idx and 0 <= right < idx):
            raise ValueError("Every gate operand must reference an existing wire")
        self.nodes.append({"op": op, "left": left, "right": right})
        return idx

    def dot(self, left, right):
        if not left:
            return self.const(0)
        products = [self.gate("mul", a, b) for a, b in zip(left, right, strict=True)]
        acc = products[0]
        for term in products[1:]:
            acc = self.gate("add", acc, term)
        return acc

    def matrix_product(self, left, right):
        r = len(left)
        return [[self.dot(left[i], [right[j][k] for j in range(r)])
                 for k in range(r)] for i in range(r)]


def compile_scalar(r, k):
    if r < 1 or k < 0:
        raise ValueError("This export convention requires r>=1 and k>=0")
    build = Builder()
    base = [[build.input(f"M[{i},{j}]") for j in range(r)] for i in range(r)]
    u = [build.input(f"u[{i}]") for i in range(r)]
    v = [build.input(f"v[{i}]") for i in range(r)]
    current = base
    stages = []
    if k == 0:
        zero, one = build.const(0), build.const(1)
        current = [[one if i == j else zero for j in range(r)] for i in range(r)]
    else:
        for op in instructions(k):
            start = len(build.nodes)
            current = build.matrix_product(current, current if op == "square" else base)
            stages.append({"instruction": op, "node_start": start,
                           "node_end_exclusive": len(build.nodes), "outputs": current})
    contraction_start = len(build.nodes)
    matrix_v = [build.dot(row, v) for row in current]
    output = build.dot(u, matrix_v)
    add = sum(node["op"] == "add" for node in build.nodes)
    mul = sum(node["op"] == "mul" for node in build.nodes)
    return {"artifact_version": "n57-dense-scalar-compiler-v1", "dimension": r,
            "exponent": k, "input_construction_cost": "Explicit hypothesis S",
            "input_count": r*r+2*r, "instructions": instructions(k),
            "stages": stages, "contraction_start": contraction_start,
            "nodes": build.nodes, "output": output, "additions": add,
            "multiplications": mul, "scalar_gates": add+mul,
            "unknown_target_initialization": False}


def evaluate_dag(dag, inputs):
    values = []
    for idx, node in enumerate(dag["nodes"]):
        op = node["op"]
        if op == "input":
            values.append(inputs[node["name"]])
        elif op == "constant":
            values.append(node["value"])
        else:
            if not (0 <= node["left"] < idx and 0 <= node["right"] < idx):
                raise ValueError("Forward reference in serialized DAG")
            left, right = values[node["left"]], values[node["right"]]
            values.append(left+right if op == "add" else left*right)
    return values[dag["output"]]


def write_dag(path, dag):
    Path(path).write_text(json.dumps(dag, indent=2), encoding="utf-8")

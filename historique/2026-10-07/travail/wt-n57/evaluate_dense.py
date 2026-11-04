"""Frozen positive n57 protocol; independent iterative vector oracle."""
import hashlib
import json
import time
from pathlib import Path

from dense_compiler import compile_scalar, evaluate_dag, write_dag


ROOT = Path(__file__).resolve().parent


def oracle(matrix, u, v, k):
    vector = v[:]
    for _ in range(k):
        vector = [sum(a*b for a, b in zip(row, vector, strict=True)) for row in matrix]
    return sum(a*b for a, b in zip(u, vector, strict=True))


def matrix_case(r, name):
    if name == "identity":
        return [[int(i == j) for j in range(r)] for i in range(r)]
    if name == "cyclic_permutation":
        return [[int(j == (i+1) % r) for j in range(r)] for i in range(r)]
    if name == "dense_integer":
        return [[i+j+1 for j in range(r)] for i in range(r)]
    raise ValueError(name)


def main():
    protocol_bytes = (ROOT / "n57-protocol.json").read_bytes()
    protocol = json.loads(protocol_bytes)
    runs = []
    measured = []
    exports = ROOT / "scalar-dags"
    exports.mkdir(exist_ok=True)
    for n in protocol["python_protocol"]["n_values"]:
        r, k = n, n**n-1
        started = time.perf_counter()
        dag = compile_scalar(r, k)
        write_dag(exports / f"n{n}-r{r}.json", dag)
        J = len(dag["instructions"])
        expected_mul = J*r**3+r*r+r
        expected_add = J*r*r*(r-1)+r*(r-1)+(r-1)
        topology = all(node["op"] in ("input", "constant") or
                       (0 <= node["left"] < idx and 0 <= node["right"] < idx)
                       for idx, node in enumerate(dag["nodes"]))
        graph_ok = topology and dag["multiplications"] == expected_mul and dag["additions"] == expected_add
        runs.append({"n": n, "case": "graph_topology_and_full_count", "passed": graph_ok})
        measured.append({"n": n, "r": r, "K": k, "J": J,
                         "additions": dag["additions"], "multiplications": dag["multiplications"],
                         "scalar_gates": dag["scalar_gates"], "S": "Explicit input construction hypothesis",
                         "conditional_upper_bound_excluding_S": 4*r**3*n**2+3*r**2,
                         "graph_generation_seconds": time.perf_counter()-started})
        u = [i+1 for i in range(r)]
        v = [2*i+1 for i in range(r)]
        for name in protocol["python_protocol"]["cases"]:
            matrix = matrix_case(r, name)
            inputs = {f"M[{i},{j}]": matrix[i][j] for i in range(r) for j in range(r)}
            inputs.update({f"u[{i}]": u[i] for i in range(r)})
            inputs.update({f"v[{i}]": v[i] for i in range(r)})
            started = time.perf_counter()
            result, expected = evaluate_dag(dag, inputs), oracle(matrix, u, v, k)
            # Exact comparison is performed before any digest; large results are
            # represented by bit length and a digest rather than decimal output.
            runs.append({"n": n, "case": name, "passed": result == expected,
                         "result_bit_length": result.bit_length(),
                         "result_sha256_hex_encoding": hashlib.sha256(hex(result).encode()).hexdigest(),
                         "elapsed_seconds": time.perf_counter()-started})
    passed = sum(run["passed"] for run in runs)
    report = {"node": "n57", "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
              "boundary": protocol["boundary"], "python_score": passed/16,
              "passed": passed, "denominator": 16, "runs": runs, "measured_counts": measured,
              "formal_proof_score": "Reported separately by verify_dense.py",
              "root_representation_established": False, "held_out_access": False}
    (ROOT / "n57-python-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"python_score": passed/16, "passed": passed, "measured_counts": measured}, indent=2))
    if passed != 16:
        raise SystemExit("Frozen positive development protocol failed")


if __name__ == "__main__":
    main()

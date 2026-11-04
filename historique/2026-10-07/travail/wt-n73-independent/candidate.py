"""An explicit scalar Hhat DAG and an exponential subset-state P_A DAG.

No determinant/permanent black box is used.  Q[t,z] values are represented by
dicts (t exponent, z exponent) -> Fraction.  Rational constants, z, and t are
leaves; the only counted gate kinds are binary `add` and `mul`.  The prescribed
p_ij = 1 + a_ij**2 are allowed constant leaves, as in the paper's circuit model.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from time import perf_counter

Poly = dict[tuple[int, int], Fraction]


def add_poly(left: Poly, right: Poly) -> Poly:
    result = left.copy()
    for key, value in right.items():
        new = result.get(key, Fraction(0)) + value
        if new:
            result[key] = new
        else:
            result.pop(key, None)
    return result


def mul_poly(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for (lt, lz), lv in left.items():
        for (rt, rz), rv in right.items():
            key = (lt + rt, lz + rz)
            new = result.get(key, Fraction(0)) + lv * rv
            if new:
                result[key] = new
            else:
                result.pop(key, None)
    return result


class DAG:
    """Topologically ordered fan-in-two circuit, with no algebraic shortcuts."""

    def __init__(self):
        self.nodes: list[dict] = []
        self.constants: dict[Fraction, int] = {}
        self.gates = 0

    def constant(self, value) -> int:
        value = Fraction(value)
        if value in self.constants:
            return self.constants[value]
        node = len(self.nodes)
        self.nodes.append({"op": "constant", "value": str(value)})
        self.constants[value] = node
        return node

    def variable(self, name: str) -> int:
        node = len(self.nodes)
        self.nodes.append({"op": "variable", "name": name})
        return node

    def operation(self, op: str, left: int, right: int) -> int:
        assert op in ("add", "mul")
        assert 0 <= left < len(self.nodes) and 0 <= right < len(self.nodes)
        node = len(self.nodes)
        self.nodes.append({"op": op, "left": left, "right": right})
        self.gates += 1
        return node

    def add(self, left, right):
        return self.operation("add", left, right)

    def mul(self, left, right):
        return self.operation("mul", left, right)

    def sub(self, left, right):
        # This explicit +/* implementation counts two gates, conservatively.
        return self.add(left, self.mul(self.constant(-1), right))

    def power(self, base: int, exponent: int) -> int:
        assert exponent >= 0
        if exponent == 0:
            return self.constant(1)
        current = base
        for bit in bin(exponent)[3:]:
            current = self.mul(current, current)
            if bit == "1":
                current = self.mul(current, base)
        return current

    def sum(self, terms) -> int:
        terms = iter(terms)
        current = next(terms)
        for term in terms:
            current = self.add(current, term)
        return current

    def product(self, terms) -> int:
        terms = iter(terms)
        try:
            current = next(terms)
        except StopIteration:
            return self.constant(1)
        for term in terms:
            current = self.mul(current, term)
        return current

    def evaluate(self, output: int) -> tuple[Poly, dict]:
        """Evaluate every actual DAG gate exactly, releasing dead values.

        Liveness is a storage optimization, not a circuit transformation. All
        gate values are formed by the two sparse arithmetic routines above.
        """
        uses = [0] * len(self.nodes)
        for node in self.nodes:
            if node["op"] in ("add", "mul"):
                uses[node["left"]] += 1
                uses[node["right"]] += 1
        uses[output] += 1
        values: dict[int, Poly] = {}
        stats = {"scalar_gate_evaluations": 0, "max_node_terms": 0,
                 "max_live_terms": 0, "nodes": len(self.nodes)}
        live_terms = 0
        for index, node in enumerate(self.nodes):
            op = node["op"]
            if op == "constant":
                value = Fraction(node["value"])
                poly = {(0, 0): value} if value else {}
            elif op == "variable":
                poly = {(1, 0) if node["name"] == "t" else (0, 1): Fraction(1)}
            else:
                left, right = node["left"], node["right"]
                poly = (add_poly if op == "add" else mul_poly)(values[left], values[right])
                stats["scalar_gate_evaluations"] += 1
                for source in (left, right):
                    uses[source] -= 1
                    if uses[source] == 0:
                        live_terms -= len(values[source])
                        del values[source]
            values[index] = poly
            live_terms += len(poly)
            stats["max_node_terms"] = max(stats["max_node_terms"], len(poly))
            stats["max_live_terms"] = max(stats["max_live_terms"], live_terms)
            if uses[index] == 0:
                live_terms -= len(poly)
                del values[index]
        assert stats["scalar_gate_evaluations"] == self.gates
        return values[output], stats

    def serialize(self, output: int) -> dict:
        return {"model": "Q with z,t leaves and fan-in-two add/mul gates",
                "gates": self.gates, "output": output, "nodes": self.nodes}


def matrix_product(dag: DAG, left, right):
    n = len(left)
    return [[dag.sum(dag.mul(left[i][r], right[r][j]) for r in range(n))
             for j in range(n)] for i in range(n)]


def determinant(dag: DAG, matrix):
    """Paper section 7 recurrence, including multiplication by 0/1 gates."""
    n = len(matrix)
    h = [[dag.constant(int(i == j)) for j in range(n)] for i in range(n)]
    for k in range(1, n + 1):
        tk = matrix_product(dag, matrix, h)
        trace = dag.sum(tk[i][i] for i in range(n))
        if k == n:
            return dag.mul(trace, dag.constant(Fraction((-1) ** (n + 1), n)))
        ck = dag.mul(trace, dag.constant(Fraction(-1, k)))
        h = [[dag.add(tk[i][j], ck) if i == j else tk[i][j]
              for j in range(n)] for i in range(n)]
    raise AssertionError("matrix is nonempty")


def check_matrix(A):
    n = len(A)
    if n < 2 or any(len(row) != n for row in A):
        raise ValueError("a square matrix with n>=2 is required")
    return [[Fraction(a) for a in row] for row in A]


def marked_entries(dag: DAG, A):
    n = len(A)
    z = dag.variable("z")
    markers = [z]
    for _ in range(1, n * n):
        markers.append(dag.mul(markers[-1], markers[-1]))
    entries = [[dag.mul(dag.constant(1 + A[i][j] ** 2), markers[i * n + j])
                for j in range(n)] for i in range(n)]
    return entries


def build_hhat(A) -> tuple[DAG, int, int]:
    A = check_matrix(A)
    n = len(A)
    dag = DAG()
    entries = marked_entries(dag, A)
    t = dag.variable("t")
    u = [t]
    for _ in range(1, n):
        u.append(dag.power(u[-1], n))
    powers = [[dag.constant(1), ui] for ui in u]
    for i in range(n):
        for _ in range(2, n):
            powers[i].append(dag.mul(powers[i][-1], u[i]))
    matrix = [[entries[i][j] if j == 0 else dag.mul(entries[i][j], powers[i][j])
               for j in range(n)] for i in range(n)]
    det = determinant(dag, matrix)
    vandermonde = dag.product(dag.sub(u[i], u[l]) for i in range(n)
                              for l in range(i + 1, n))
    ha = dag.mul(det, vandermonde)
    K = n ** n - 1
    centered = dag.add(dag.constant(1), dag.power(t, 2 * K))
    output = dag.add(centered, ha)
    return dag, output, K


def simulate(A):
    dag, output, K = build_hhat(A)
    hhat, _ = dag.evaluate(output)
    central = {ze: value for (te, ze), value in hhat.items() if te == K}
    return {"central": central, "hhat": hhat, "K": K, "gates": dag.gates}


def build_subset_dp(A) -> tuple[DAG, int, dict]:
    """P[S] assigns the first |S| rows bijectively onto column set S."""
    A = check_matrix(A)
    n = len(A)
    dag = DAG()
    entries = marked_entries(dag, A)
    states = {0: dag.constant(1)}
    transitions = 0
    for mask in range(1, 1 << n):
        row = mask.bit_count() - 1
        terms = []
        for column in range(n):
            bit = 1 << column
            if mask & bit:
                terms.append(dag.mul(states[mask ^ bit], entries[row][column]))
                transitions += 1
        states[mask] = dag.sum(terms)
    expected_dp_gates = n * 2 ** n - (2 ** n - 1)
    assert transitions == n * 2 ** (n - 1)
    assert dag.gates == (2 * n * n - 1) + expected_dp_gates
    return dag, states[(1 << n) - 1], {
        "states": len(states), "transitions": transitions,
        "dp_gates": expected_dp_gates, "marker_and_entry_gates": 2 * n * n - 1,
        "formula": "total gates = 2*n^2-1 + n*2^n - (2^n-1)",
    }


def family_matrix(n, name):
    if name == "identity":
        return [[int(i == j) for j in range(n)] for i in range(n)]
    if name == "cyclic":
        return [[int(j == (i + 1) % n) for j in range(n)] for i in range(n)]
    if name == "vandermonde":
        return [[(i + 1) ** j for j in range(n)] for i in range(n)]
    raise ValueError(name)


def inspect_case(A, name):
    dag, output, K = build_hhat(A)
    started = perf_counter()
    hhat, stats = dag.evaluate(output)
    elapsed_hhat = perf_counter() - started
    central = {ze: value for (te, ze), value in hhat.items() if te == K}
    dp, dp_output, dp_stats = build_subset_dp(A)
    started = perf_counter()
    permanent, eval_stats = dp.evaluate(dp_output)
    elapsed_dp = perf_counter() - started
    permanent = {ze: value for (te, ze), value in permanent.items() if te == 0}
    assert central == permanent
    return {
        "case": name, "n": len(A), "K": K,
        "hhat": {"gates": dag.gates, "terms": len(hhat), "seconds": elapsed_hhat, **stats},
        "subset_dp": {"gates": dp.gates, "terms": len(permanent), "seconds": elapsed_dp,
                      **dp_stats, **eval_stats},
        "dp_matches_extracted_central": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=2)
    parser.add_argument("--family", choices=("identity", "cyclic", "vandermonde"), default="identity")
    parser.add_argument("--all-dev", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dag", type=Path)
    args = parser.parse_args()
    if args.all_dev:
        rows = [inspect_case(family_matrix(n, family), f"n{n}-{family}")
                for n in (2, 3, 4) for family in ("identity", "cyclic", "vandermonde")]
    else:
        rows = [inspect_case(family_matrix(args.n, args.family), f"n{args.n}-{args.family}")]
    report = {"protocol": "n1-explicit-dags-v1", "split": "dev", "cases": rows,
              "scope": "Finite exact scalar-DAG evaluation. DP formula describes this algorithm, not a lower bound."}
    if args.output:
        args.output.write_text(json.dumps(report, indent=2))
    if args.dag:
        dag, output, K = build_hhat(family_matrix(args.n, args.family))
        args.dag.write_text(json.dumps({"n": args.n, "family": args.family, "K": K,
                                        **dag.serialize(output)}, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

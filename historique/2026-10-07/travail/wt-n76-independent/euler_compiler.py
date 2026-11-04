"""Three explicit Euler-phase scalar constructions, never free derivatives.

The selected candidate is the shared complementary-cofactor construction.
Generic input leaves x_e may be replaced by prescribed marked entries later.
All determinant instances use the unchanged, counted candidate.py recurrence.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction
from itertools import permutations
from math import comb, factorial
from pathlib import Path
from time import perf_counter

from candidate import DAG, determinant, check_matrix, add_poly, mul_poly
from euler_identity import edge_pairs, row_pairs, inversion_sign


class ConstructionLimit(RuntimeError):
    pass


class ScalarGraph(DAG):
    """Scalar DAG with structural sharing and constant-only simplification.

    Support masks are conservative syntactic variable supports. They do not
    depend on a polynomial expansion or on the unknown corrected coefficient.
    """

    def __init__(self, shared=True, node_cap=None, seconds_cap=None):
        super().__init__()
        self.shared = shared
        self.operation_cache = {}
        self.variables = {}
        self.supports = []
        self.specialization_cache = {}
        self.node_cap = node_cap
        self.deadline = perf_counter() + seconds_cap if seconds_cap else None

    def limit_check(self):
        if self.node_cap is not None and len(self.nodes) >= self.node_cap:
            raise ConstructionLimit(f"node cap {self.node_cap}")
        if self.deadline is not None and perf_counter() >= self.deadline:
            raise ConstructionLimit("construction time cap")

    def constant(self, value):
        self.limit_check()
        before = len(self.nodes)
        result = super().constant(value)
        if len(self.nodes) != before:
            self.supports.append(0)
        return result

    def variable(self, name):
        if name in self.variables:
            return self.variables[name]
        self.limit_check()
        result = super().variable(name)
        self.variables[name] = result
        self.supports.append(1 << int(name[1:]) if name.startswith("x") else 0)
        return result

    def constant_value(self, node):
        return Fraction(self.nodes[node]["value"]) if self.nodes[node]["op"] == "constant" else None

    def operation(self, op, left, right):
        self.limit_check()
        if self.shared:
            lv, rv = self.constant_value(left), self.constant_value(right)
            if op == "add":
                if lv == 0:
                    return right
                if rv == 0:
                    return left
            else:
                if lv == 0 or rv == 0:
                    return self.constant(0)
                if lv == 1:
                    return right
                if rv == 1:
                    return left
            if left > right:
                left, right = right, left
            key = (op, left, right)
            if key in self.operation_cache:
                return self.operation_cache[key]
        result = super().operation(op, left, right)
        self.supports.append(self.supports[left] | self.supports[right])
        if self.shared:
            self.operation_cache[(op, left, right)] = result
        return result

    def specialize(self, source, zero_mask):
        zero_mask &= self.supports[source]
        if not zero_mask:
            return source
        key = (source, zero_mask)
        if key in self.specialization_cache:
            return self.specialization_cache[key]
        node = self.nodes[source]
        if node["op"] == "variable":
            result = self.constant(0)
        elif node["op"] == "constant":
            result = source
        else:
            left = self.specialize(node["left"], zero_mask)
            right = self.specialize(node["right"], zero_mask)
            result = self.operation(node["op"], left, right)
        self.specialization_cache[key] = result
        return result

    def counts(self):
        return dict(Counter(node["op"] for node in self.nodes))

    def reachable(self, output):
        found, pending = set(), [output]
        while pending:
            index = pending.pop()
            if index in found:
                continue
            found.add(index)
            node = self.nodes[index]
            if node["op"] in ("add", "mul"):
                pending.extend((node["left"], node["right"]))
        return found

    def compact(self, output):
        """Remove unreachable gates; retain every live binary operation exactly."""
        live = self.reachable(output)
        result = ScalarGraph(shared=False)
        translated = {}
        for index, node in enumerate(self.nodes):
            if index not in live:
                continue
            op = node["op"]
            if op == "constant":
                translated[index] = result.constant(node["value"])
            elif op == "variable":
                translated[index] = result.variable(node["name"])
            else:
                translated[index] = result.operation(op, translated[node["left"]], translated[node["right"]])
        return result, translated[output]

    def serialize(self, output):
        return {"model": "Q[x] or Q[z], fan-in-two scalar add/mul only",
                "gates": self.gates, "counts": self.counts(), "output": output,
                "nodes": self.nodes}


def seed_matrix(graph, n):
    return [[graph.variable(f"x{i*n+j}") for j in range(n)] for i in range(n)]


def seed_gate_count(n):
    return 2*n**4 - n**3 + 2*n*n - n


def naive_formula(n):
    pairs = len(edge_pairs(n))
    seed = seed_gate_count(n)
    return {"n": n, "seed_gates": seed, "inversion_pairs": pairs,
            "gates": 4**pairs*seed + 7*(4**pairs-1)//3,
            "recurrence": "G_0=2n^4-n^3+2n^2-n; G_(h+1)=4G_h+7",
            "scope": "exact count of this unsimplified construction, not a lower bound"}


def naive_graph_n2():
    graph = ScalarGraph(shared=False)
    matrix = seed_matrix(graph, 2)
    first = determinant(graph, matrix)
    e, f = edge_pairs(2)[0]
    snapshot = list(graph.nodes)

    def copy_with_zero(mask):
        translated = {}
        for i, node in enumerate(snapshot):
            op = node["op"]
            if op == "constant":
                translated[i] = graph.constant(node["value"])
            elif op == "variable":
                cell = int(node["name"][1:])
                translated[i] = graph.constant(0) if mask & (1 << cell) else matrix[cell//2][cell%2]
            else:
                translated[i] = graph.operation(op, translated[node["left"]], translated[node["right"]])
        return translated[first]

    terms = [graph.mul(graph.constant(-1), first),
             graph.mul(graph.constant(2), copy_with_zero(1 << e)),
             graph.mul(graph.constant(2), copy_with_zero(1 << f)),
             graph.mul(graph.constant(-2), copy_with_zero((1 << e) | (1 << f)))]
    output = graph.sum(terms)
    assert graph.gates == naive_formula(2)["gates"]
    return graph, output


def shared_specializations(n):
    graph = ScalarGraph(node_cap=200000, seconds_cap=45)
    started = perf_counter()
    stages = []
    try:
        current = determinant(graph, seed_matrix(graph, n))
        for i, l in row_pairs(n):
            old, corrections = current, []
            for j in range(n):
                for m in range(j):
                    e, f = i*n+j, l*n+m
                    fe = graph.specialize(old, 1 << e)
                    ff = graph.specialize(old, 1 << f)
                    fef = graph.specialize(old, (1 << e) | (1 << f))
                    projected = graph.add(graph.sub(graph.sub(old, fe), ff), fef)
                    corrections.append(graph.mul(graph.constant(-2), projected))
            current = graph.add(old, graph.sum(corrections))
            stages.append({"row_pair": [i,l], "allocated_gates": graph.gates,
                           "nodes": len(graph.nodes),
                           "specialization_cache_entries": len(graph.specialization_cache)})
        allocated = graph.gates
        compact, output = graph.compact(current)
        return compact, output, {"status": "complete", "allocated_gates": allocated,
             "reachable_gates": compact.gates, "stages": stages,
             "elapsed_seconds": perf_counter()-started,
             "specialization_cache_entries": len(graph.specialization_cache)}
    except ConstructionLimit as error:
        return None, None, {"status": "capped", "constraint": str(error),
             "allocated_gates": graph.gates, "nodes": len(graph.nodes), "stages": stages,
             "elapsed_seconds": perf_counter()-started,
             "specialization_cache_entries": len(graph.specialization_cache)}


def matching_union(n, matching, e, f):
    merged = matching | frozenset((e, f))
    rows = [cell//n for cell in merged]
    columns = [cell%n for cell in merged]
    return merged if len(set(rows)) == len(merged) == len(set(columns)) else None


def matching_coefficients(n):
    """Universal integer projector coefficients; no B entries used here."""
    alpha = {frozenset(): 1}
    preprocessing_adds = preprocessing_muls = 0
    attempts = compatible = 0
    stages = []
    for i,l in row_pairs(n):
        updated = dict(alpha)
        for matching, coefficient in alpha.items():
            scaled = -2*coefficient
            preprocessing_muls += 1
            for j in range(n):
                for m in range(j):
                    attempts += 1
                    union = matching_union(n, matching, i*n+j, l*n+m)
                    if union is None:
                        continue
                    compatible += 1
                    updated[union] = updated.get(union, 0) + scaled
                    preprocessing_adds += 1
        alpha = {key: value for key, value in updated.items() if value}
        stages.append({"row_pair": [i,l], "nonzero_matching_states": len(alpha)})
    bound = sum(comb(n,k)**2 * factorial(k) for k in range(n+1))
    return alpha, {"states": len(alpha), "all_partial_matching_state_bound": bound,
        "attempts": attempts, "compatible_transitions": compatible,
        "preprocessing_integer_adds": preprocessing_adds,
        "preprocessing_integer_muls": preprocessing_muls,
        "maximum_integer_coefficient_bit_length": max(abs(v).bit_length() for v in alpha.values()),
        "coefficient_l1_bound": (1+n*(n-1))**len(row_pairs(n)), "stages": stages}


def cofactor_sign(n, matching):
    pairs = sorted((cell//n, cell%n) for cell in matching)
    sign = (-1)**sum(i+j for i,j in pairs)
    sign *= (-1)**sum(pairs[a][1] > pairs[b][1] for a in range(len(pairs)) for b in range(a+1,len(pairs)))
    return sign


def cofactor_graph(n):
    started = perf_counter()
    alpha, metadata = matching_coefficients(n)
    graph = ScalarGraph()
    matrix = seed_matrix(graph, n)
    minor_cache = {}
    edge_cache = {frozenset(): graph.constant(1)}

    def edge_product(matching):
        if matching in edge_cache:
            return edge_cache[matching]
        last = max(matching)
        edge_cache[matching] = graph.mul(edge_product(matching-frozenset((last,))), matrix[last//n][last%n])
        return edge_cache[matching]

    def complementary_minor(matching):
        row_mask = sum(1 << (cell//n) for cell in matching)
        col_mask = sum(1 << (cell%n) for cell in matching)
        key = (row_mask, col_mask)
        if key not in minor_cache:
            rows = [i for i in range(n) if not row_mask & (1 << i)]
            columns = [j for j in range(n) if not col_mask & (1 << j)]
            minor_cache[key] = determinant(graph, [[matrix[i][j] for j in columns] for i in rows]) if rows else graph.constant(1)
        return minor_cache[key]

    terms = []
    for matching, coefficient in sorted(alpha.items(), key=lambda item:(len(item[0]), sorted(item[0]))):
        projected = graph.mul(edge_product(matching), complementary_minor(matching))
        terms.append(graph.mul(graph.constant(coefficient*cofactor_sign(n,matching)), projected))
    output = graph.sum(terms)
    allocated = graph.gates
    graph, output = graph.compact(output)
    metadata.update({"distinct_complementary_minors": len(minor_cache),
        "minor_cache_bound": comb(2*n,n), "edge_product_cache_entries": len(edge_cache),
        "allocated_gates_before_liveness": allocated, "reachable_gates": graph.gates,
        "gate_counts": graph.counts(), "construction_seconds": perf_counter()-started,
        "cost_scope": "Each determinant and edge product uses scalar gates; universal integer preprocessing is separately counted."})
    return graph, output, metadata, alpha


def mark_graph(generic, output, A):
    """Compile original p=1+a^2, shared binary z markers, then live generic DAG.

    Prescribed p leaves are rational constants, as allowed by source §1. The
    preprocessing of their bit representations is explicit Python Fraction
    arithmetic, separate from scalar gate accounting.
    """
    A = check_matrix(A)
    n = len(A)
    result = ScalarGraph(shared=False)
    z = result.variable("z")
    markers = [z]
    for _ in range(1,n*n):
        markers.append(result.mul(markers[-1], markers[-1]))
    replacements = [result.mul(result.constant(1+A[i][j]**2), markers[i*n+j])
                    for i in range(n) for j in range(n)]
    translated = {}
    for index,node in enumerate(generic.nodes):
        op = node["op"]
        if op == "constant":
            translated[index] = result.constant(node["value"])
        elif op == "variable":
            translated[index] = replacements[int(node["name"][1:])]
        else:
            translated[index] = result.operation(op, translated[node["left"]], translated[node["right"]])
    assert result.gates == generic.gates + 2*n*n-1
    return result, translated[output]


def evaluate_generic(graph, output, n):
    """Actual scalar graph interpreted in SymPy Q[x], with dead value release."""
    import sympy as sp
    x = sp.symbols(f"x0:{n*n}")
    uses = [0]*len(graph.nodes)
    for node in graph.nodes:
        if node["op"] in ("add", "mul"):
            uses[node["left"]] += 1
            uses[node["right"]] += 1
    uses[output] += 1
    values, evaluated, maximum = {}, 0, 0
    for i,node in enumerate(graph.nodes):
        op = node["op"]
        if op == "constant":
            q = Fraction(node["value"])
            value = sp.Poly(sp.Rational(q.numerator,q.denominator), *x)
        elif op == "variable":
            value = sp.Poly(x[int(node["name"][1:])], *x)
        else:
            left,right = node["left"],node["right"]
            value = values[left]+values[right] if op == "add" else values[left]*values[right]
            evaluated += 1
            for source in (left,right):
                uses[source] -= 1
                if uses[source] == 0:
                    del values[source]
        maximum = max(maximum,len(value.terms()))
        values[i] = value
        if uses[i] == 0:
            del values[i]
    assert evaluated == graph.gates
    return values[output], {"actual_scalar_gate_evaluations": evaluated, "maximum_node_terms": maximum}


def marked_oracle(A):
    A = check_matrix(A)
    n = len(A)
    result = {}
    for sigma in permutations(range(n)):
        exponent = sum(1 << (i*n+sigma[i]) for i in range(n))
        coefficient = Fraction(1)
        for i in range(n):
            coefficient *= 1+A[i][sigma[i]]**2
        result[exponent] = coefficient
    return result


def build_marked(A):
    """Public frozen candidate API: returns actual scalar DAG, output, metadata."""
    generic,output,metadata,_ = cofactor_graph(len(A))
    marked,marked_output = mark_graph(generic,output,A)
    metadata = {**metadata, "generic_gates": generic.gates,
                "marked_gates": marked.gates, "marker_gates": 2*len(A)**2-1}
    return marked,marked_output,metadata


def build_cofactor(n):
    """Generic public API: actual DAG and output with input leaves x0..x(n²-1)."""
    graph,output,_,_ = cofactor_graph(n)
    return graph,output


def simulate(A):
    """Final candidate value P_A(z); does not construct Hhat or extract blindly."""
    graph,output,metadata = build_marked(A)
    value,stats = graph.evaluate(output)
    return {"central": {z:c for (t,z),c in value.items() if t == 0},
            "gates": graph.gates, "metadata": metadata, "evaluation": stats}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=2)
    parser.add_argument("--dag", type=Path)
    args = parser.parse_args()
    A = [[Fraction(i+1,j+2) for j in range(args.n)] for i in range(args.n)]
    graph,output,metadata = build_marked(A)
    value,stats = graph.evaluate(output)
    assert {z:c for (t,z),c in value.items()} == marked_oracle(A)
    if args.dag:
        args.dag.write_text(json.dumps({"n": args.n, **graph.serialize(output)},indent=2))
    print(json.dumps({"n": args.n, "metadata": metadata, "evaluation": stats,
                      "output_terms": len(value)}, indent=2))


if __name__ == "__main__":
    main()

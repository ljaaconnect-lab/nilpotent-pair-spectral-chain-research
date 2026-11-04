"""Restricted scalar compilation of the oriented chain from B = U V^T.

This is NOT a compiler from the original addressed matrix to a bounded-rank
factorisation.  Its variable leaves are U and V.  All computed nodes are binary
scalar additions or multiplications.  Composition tables have r coordinates;
they are not tables of column subsets.  The only permutation enumeration is
the independent test oracle below.

The output uses the established fusion of the corrected oriented product and
the INTT: the final scalar is routed to sum(d_j) modulo N.  It is the coefficient
of Omega_tilde after both universal signs cancel.  No terminal amplitude is an
input.  The construction is polynomial for a FIXED factorisation rank r.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import permutations
from math import comb, factorial, prod
from pathlib import Path
from random import Random
import json


@dataclass(frozen=True)
class Node:
    kind: str
    payload: object


class ScalarDAG:
    """A genuine binary arithmetic DAG; leaves and output references are free."""

    def __init__(self) -> None:
        self.nodes: list[Node] = []
        self.leaves: dict[tuple, int] = {}
        self.additions = 0
        self.multiplications = 0

    def leaf(self, key: tuple, kind: str, payload: object) -> int:
        if key not in self.leaves:
            self.leaves[key] = len(self.nodes)
            self.nodes.append(Node(kind, payload))
        return self.leaves[key]

    def constant(self, value: int) -> int:
        return self.leaf(("constant", value), "constant", value)

    def variable(self, name: str, row: int, col: int) -> int:
        return self.leaf(("input", name, row, col), "input", (name, row, col))

    def binary(self, kind: str, left: int, right: int) -> int:
        assert kind in ("add", "mul")
        assert 0 <= left < len(self.nodes) and 0 <= right < len(self.nodes)
        result = len(self.nodes)
        self.nodes.append(Node(kind, (left, right)))
        if kind == "add":
            self.additions += 1
        else:
            self.multiplications += 1
        return result

    @property
    def gates(self) -> int:
        return self.additions + self.multiplications

    def evaluate(self, inputs: dict[str, list[list[int]]], modulus: int) -> list[int]:
        values: list[int] = []
        for node in self.nodes:
            if node.kind == "constant":
                value = int(node.payload)
            elif node.kind == "input":
                name, row, col = node.payload
                value = inputs[name][row][col]
            else:
                left, right = node.payload
                value = (values[left] + values[right] if node.kind == "add"
                         else values[left] * values[right])
            values.append(value % modulus)
        return values


def composition_table(dag: ScalarDAG, factors: list[list[int]]) -> dict[tuple[int, ...], int]:
    """Coefficients of a product of linear forms in r auxiliary variables."""
    rank = len(factors[0])
    table = {(0,) * rank: dag.constant(1)}
    for factor in factors:
        next_table: dict[tuple[int, ...], int] = {}
        for key, coefficient in table.items():
            for alpha, variable in enumerate(factor):
                target = list(key)
                target[alpha] += 1
                target = tuple(target)
                term = dag.binary("mul", coefficient, variable)
                next_table[target] = (dag.binary("add", next_table[target], term)
                                      if target in next_table else term)
        table = next_table
    return table


@dataclass
class CompiledChain:
    dag: ScalarDAG
    amplitude: int
    outputs: tuple[int, ...]
    slot: int
    table_gates: tuple[int, int]
    contraction_gates: int


def compile_chain(n: int, rank: int, length: int, labels: list[int]) -> CompiledChain:
    """Compile from U,V; labels and the spectral length are fixed parameters."""
    assert n >= 1 and rank >= 1 and length >= n and length & (length - 1) == 0
    assert len(labels) == n
    dag = ScalarDAG()
    u = [[dag.variable("U", i, a) for a in range(rank)] for i in range(n)]
    v = [[dag.variable("V", j, a) for a in range(rank)] for j in range(n)]
    before = dag.gates
    h = composition_table(dag, u)
    first_cost = dag.gates - before
    before = dag.gates
    g = composition_table(dag, v)
    second_cost = dag.gates - before
    before = dag.gates
    amplitude: int | None = None
    for key, coefficient in h.items():
        term = dag.binary("mul", coefficient, g[key])
        weight = prod(factorial(k) for k in key)
        term = dag.binary("mul", term, dag.constant(weight))
        amplitude = term if amplitude is None else dag.binary("add", amplitude, term)
    assert amplitude is not None
    contraction_cost = dag.gates - before
    slot = sum(labels) % length
    zero = dag.constant(0)
    outputs = tuple(amplitude if k == slot else zero for k in range(length))
    return CompiledChain(dag, amplitude, outputs, slot,
                         (first_cost, second_cost), contraction_cost)


def expected_table_gates(n: int, rank: int) -> int:
    return 2 * rank * comb(n + rank - 1, rank) - comb(n + rank, rank) + 1


def expected_total_gates(n: int, rank: int) -> int:
    return 2 * expected_table_gates(n, rank) + 3 * comb(n + rank - 1, rank - 1) - 1


def reference_transversal_sum(matrix: list[list[int]], modulus: int) -> int:
    """Independent exhaustive oracle, used ONLY in validation, never compilation."""
    n = len(matrix)
    return sum(prod(matrix[i][j] for i, j in enumerate(order))
               for order in permutations(range(n))) % modulus


def power_two_root(length: int, modulus: int) -> int:
    assert length & (length - 1) == 0 and (modulus - 1) % length == 0
    if length == 1:
        return 1
    for candidate in range(2, modulus):
        root = pow(candidate, (modulus - 1) // length, modulus)
        if pow(root, length, modulus) == 1 and pow(root, length // 2, modulus) != 1:
            return root
    raise ValueError("No root of the required order")


def validate() -> dict:
    modulus = 1009
    rng = Random(20261102)
    instances = []
    frequency_checks = 0
    output_checks = 0
    for n in range(1, 7):
        length = 1 << (n - 1).bit_length()
        root = power_two_root(length, modulus)
        for rank in range(1, 5):
            for trial in range(4):
                u = [[rng.randrange(modulus) for _ in range(rank)] for _ in range(n)]
                v = [[rng.randrange(modulus) for _ in range(rank)] for _ in range(n)]
                labels = [rng.randrange(length) for _ in range(n)]
                compiled = compile_chain(n, rank, length, labels)
                values = compiled.dag.evaluate({"U": u, "V": v}, modulus)
                amplitude = values[compiled.amplitude]
                b = [[sum(u[i][a] * v[j][a] for a in range(rank)) % modulus
                      for j in range(n)] for i in range(n)]
                expected_amplitude = reference_transversal_sum(b, modulus)
                assert amplitude == expected_amplitude
                e = expected_table_gates(n, rank)
                m = comb(n + rank - 1, rank - 1)
                assert compiled.table_gates == (e, e)
                assert compiled.contraction_gates == 3 * m - 1
                assert compiled.dag.gates == expected_total_gates(n, rank)
                assert all(node.kind in ("input", "constant", "add", "mul")
                           for node in compiled.dag.nodes)
                assert set(key[1] for key in compiled.dag.leaves if key[0] == "input") == {"U", "V"}
                # W is expressed in the corrected terminal Omega_tilde coordinate.
                # gamma_n from correction and gamma_n from orientation cancel.
                frequencies = []
                for f in range(length):
                    phased_b = [[b[i][j] * pow(root, f * labels[j], modulus) % modulus
                                 for j in range(n)] for i in range(n)]
                    actual_frequency = reference_transversal_sum(phased_b, modulus)
                    assert actual_frequency == amplitude * pow(root, f * sum(labels), modulus) % modulus
                    frequencies.append(actual_frequency)
                    frequency_checks += 1
                inverse_length = pow(length, -1, modulus)
                intt = [inverse_length * sum(frequencies[f] * pow(root, (-f * k) % length, modulus)
                                              for f in range(length)) % modulus
                        for k in range(length)]
                routed = [values[node_id] for node_id in compiled.outputs]
                assert routed == intt
                output_checks += length
                instances.append({"n": n, "rank": rank, "trial": trial,
                                  "N": length, "root": root, "slot": compiled.slot,
                                  "composition_coordinates": m,
                                  "table_gates_each": e,
                                  "contraction_gates": compiled.contraction_gates,
                                  "scalar_additions": compiled.dag.additions,
                                  "scalar_multiplications": compiled.dag.multiplications,
                                  "scalar_gates": compiled.dag.gates,
                                  "gate_bound": expected_total_gates(n, rank),
                                  "amplitude": amplitude, "pass": True})
    return {
        "status": "PASS",
        "date": "2026-11-02",
        "scope": "Exact scalar compiler from supplied factors U,V with B=UV^T; polynomial for fixed rank only",
        "general_original_input_compiler": False,
        "factorisation_required": True,
        "factorisation_construction_cost_included": False,
        "factorisation_cost_must_be_added": True,
        "rank_bound_independent_of_n_required_for_polynomial_claim": True,
        "rank_of_formally_addressed_generic_input_is_bounded": False,
        "scalar_variable_leaves": ["U", "V"],
        "arithmetic_gate_types": ["binary_addition", "binary_multiplication"],
        "terminal_amplitude_is_input": False,
        "column_subset_table_used_in_compiler": False,
        "permutation_enumeration_used_only_in_test_oracle": True,
        "sign_convention": "Output is the Omega_tilde coefficient after gamma_n correction; gamma_n squared equals 1",
        "spectral_compilation": "Established frequency fusion followed by zero-cost final output routing",
        "fixed_constants_and_output_references_are_free": True,
        "formula_table": "E(n,r)=2r*binom(n+r-1,r)-binom(n+r,r)+1",
        "formula_total": "2E(n,r)+3*binom(n+r-1,r-1)-1",
        "modulus": modulus,
        "seed": 20261102,
        "instances_checked": len(instances),
        "frequency_checks": frequency_checks,
        "intt_output_checks": output_checks,
        "n_values": list(range(1, 7)),
        "rank_values": list(range(1, 5)),
        "spectral_lengths": sorted({case["N"] for case in instances}),
        "source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "cases": instances,
    }


if __name__ == "__main__":
    report = validate()
    path = Path(__file__).with_name("rank-validation.json")
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "status", "instances_checked", "frequency_checks", "intt_output_checks",
        "general_original_input_compiler", "factorisation_required", "source_sha256")},
        ensure_ascii=False))

"""Explicit joint-convolution attempt on the existing native scalar DAG.

This emits ordinary scalar +/* gates. The mathematical lowering operator
motivates the recurrence but is never a primitive gate. Row-factor groups
are compilation metadata: their coefficient vectors are pooled by sorted
source-row IDs, so associative and commutative convolution is truly shared.
No column-occupancy table is used. No polynomial bound
is asserted for the number of distinct states or the complete graph.
"""
from __future__ import annotations

from math import factorial
from pathlib import Path
import sys


PROJECT = Path(__file__).resolve().parents[2]
NATIVE = PROJECT/'documents/composition-native-2026-11-03'
sys.path.insert(0, str(NATIVE))
from compose_native_representatives import compile_native_representatives  # noqa: E402


class JointConvolution:
    def __init__(self, dag, N, initial_vectors, initial_rows, fused_with_preparation=False):
        self.dag, self.N = dag, N
        self.fused_with_preparation = fused_with_preparation
        self.states = {}
        self.convolutions = {}
        self.weights = {}
        self.state_counts_by_length = {}
        self.vector_pool = {(i,): tuple(vector) for i, vector in enumerate(initial_vectors)}
        self.row_pool = {(i,): tuple(row) for i, row in enumerate(initial_rows)}
        self.group_weights = {}

    def convolution(self, left, right):
        left, right = tuple(left), tuple(right)
        key = tuple(sorted((left, right)))
        if key not in self.convolutions:
            dag, N = self.dag, self.N
            self.convolutions[key] = tuple(
                dag.sum(dag.mul(left[s], right[(r-s) % N]) for s in range(N))
                for r in range(N))
        return self.convolutions[key]

    def weight(self, vector):
        vector = tuple(vector)
        if vector not in self.weights:
            self.weights[vector] = self.dag.mul(self.dag.constant(self.N), vector[0])
        return self.weights[vector]

    def vector(self, group):
        group = tuple(sorted(group))
        assert group and len(group) == len(set(group))
        if group not in self.vector_pool:
            # Every occurrence of this row-factor product uses exactly this
            # parenthesization. No distinct columns are stored or selected.
            self.vector_pool[group] = self.convolution(
                self.vector(group[:-1]), self.vector(group[-1:]))
        return self.vector_pool[group]

    def row_product(self, group):
        group = tuple(sorted(group))
        assert group and len(group) == len(set(group))
        if group not in self.row_pool:
            left, right = self.row_product(group[:-1]), self.row_product(group[-1:])
            self.row_pool[group] = tuple(self.dag.mul(a, b) for a, b in zip(left, right))
        return self.row_pool[group]

    def group_weight(self, group):
        if group not in self.group_weights:
            if self.fused_with_preparation:
                # Fourier identity: N*c_I[0] = sum_j product_(i in I) B_ij.
                # Only these scalars are read by the recurrence. Reusing B
                # eliminates every unnecessary intermediate transform.
                self.group_weights[group] = self.dag.sum(self.row_product(group))
            else:
                self.group_weights[group] = self.weight(self.vector(group))
        return self.group_weights[group]

    def contract(self, groups):
        state = tuple(sorted(tuple(sorted(group)) for group in groups))
        flattened = [i for group in state for i in group]
        assert len(flattened) == len(set(flattened))
        if state in self.states:
            return self.states[state]
        dag, k = self.dag, len(state)
        if k == 0:
            value = dag.one
        else:
            first = dag.sum(dag.mul(self.group_weight(state[i]),
                                   self.contract(state[:i]+state[i+1:]))
                            for i in range(k))
            pairs = []
            for i in range(k):
                for j in range(i+1, k):
                    merged = tuple(sorted(state[i]+state[j]))
                    if self.fused_with_preparation:
                        self.row_product(merged)
                    else:
                        self.vector(merged)
                    rest = tuple(state[a] for a in range(k) if a not in (i, j))
                    pairs.append(self.contract(rest+(merged,)))
            value = dag.add(first, dag.mul(dag.constant(-2), dag.sum(pairs)))
        self.states[state] = value
        self.state_counts_by_length[k] = self.state_counts_by_length.get(k, 0)+1
        return value


def compile_joint_convolution(n, Q, N, omega, labels, budget=1_000_000,
                              fused_with_preparation=False):
    compiled = compile_native_representatives(n, Q, N, omega, labels, budget=budget)
    dag = compiled['dag']
    preparation_roots = [value for row in compiled['C'] for value in row]
    preparation = {i for i in dag.reachable(preparation_roots) if dag.nodes[i][0] in ('+', '*')}
    allocated_before = len(dag.nodes)
    contraction = JointConvolution(dag, N, compiled['C'], compiled['B'], fused_with_preparation)
    raw = contraction.contract(tuple((i,) for i in range(n)))
    # N|(Q-1) and N>n imply Q>n, so this is a structural constant.
    assert Q > n
    scalar = dag.mul(dag.constant(pow(factorial(n), -1, Q)), raw)
    # gamma*q_top=Omega: the corrected scalar coefficient is R/n!.
    # The terminal value is computed internally; it is never an input leaf.
    phase = dag.constant(pow(omega, sum(labels) % N, Q))
    spectra = [scalar]
    for _ in range(1, N):
        spectra.append(dag.mul(phase, spectra[-1]))
    outputs = dag.intt(spectra, omega)
    live = {i for i in dag.reachable(outputs) if dag.nodes[i][0] in ('+', '*')}
    inputs = sorted(dag.nodes[i][1] for i in dag.reachable(outputs) if dag.nodes[i][0] == 'v')
    assert not any(name.startswith('x_') for name in inputs)
    assert all(name == 'z' or name.startswith('a_') for name in inputs)
    assert dag.derivative_calls == dag.collision_operator_calls == 0
    assert all(node[0] in ('c', 'v', '+', '*') for node in dag.nodes)
    metadata = {
        'n': n, 'Q': Q, 'N': N, 'omega': omega, 'labels': list(labels),
        'variant': 'fused_with_preparation' if fused_with_preparation else 'direct_convolution',
        'states': len(contraction.states),
        'state_counts_by_length': contraction.state_counts_by_length,
        'convolutions': len(contraction.convolutions),
        'distinct_weight_vectors': len(contraction.group_weights),
        'pooled_row_factor_collections': len(contraction.row_pool if fused_with_preparation else contraction.vector_pool),
        'allocated_native_nodes_before_contraction': allocated_before,
        'allocated_nodes': len(dag.nodes),
        'coefficient_preparation_gates': len(preparation),
        'raw_contraction_gates': dag.count([raw]),
        'normalized_scalar_gates': dag.count([scalar]),
        'complete_true_INTT_scalar_gates': len(live),
        'useful_preparation_gates': len(live & preparation),
        'remaining_useful_gates_J': len(live-preparation),
        'output_inputs': inputs,
        'complete_scalar_a_z_only': True,
        'general_polynomial_gate_bound_established': False,
        'column_occupancy_tables_used': False,
        'primitive_derivative_or_quotient_reading_gate': False,
        'circuit_ops': ['+', '*'],
        'convolution_method': ('Fourier identity fused with input preparation; scalar rowwise products and sums'
                               if fused_with_preparation else 'literal cyclic convolution, canonical associative row-factor pool'),
        'state_key': 'sorted tuple of disjoint source-row factor collections',
        'row_factor_collections_are_compile_time_metadata': True,
        'associative_and_commutative_fusion_shared': True,
        'normalization': 'R(C_0,...,C_(n-1))/n!',
        'scope': 'Exact recurrence candidate with explicit scalar compilation; state-count growth is measured, not assumed polynomial.',
    }
    assert metadata['complete_true_INTT_scalar_gates'] == metadata['useful_preparation_gates']+metadata['remaining_useful_gates_J']
    return {'dag': dag, 'native': compiled, 'contraction': contraction,
            'raw': raw, 'scalar': scalar, 'spectra': spectra,
            'outputs': outputs, 'metadata': metadata}

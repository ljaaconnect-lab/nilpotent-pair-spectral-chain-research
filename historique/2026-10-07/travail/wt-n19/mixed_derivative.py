"""Positive rank-one reciprocal updates with reified scalar mixed-jet compilers.

No coefficient, nilpotent multiplication, or residue is a costless scalar gate.
Both eager and demand compilers emit actual +/* DAGs in generic formal B.
"""
from __future__ import annotations
from fractions import Fraction
from itertools import permutations
from math import prod
import sympy as sp
from rational_recurrence import RationalDAG, permanent_on_subset


class ScalarDAG:
    def __init__(self, n):
        self.n = n
        self.nodes = []
        self.gates = 0
        self.constants = {}
        self.weights = {}
        self.symbols = sp.symbols(f'b0:{n*n}')

    def constant(self, value):
        value = Fraction(value)
        if value not in self.constants:
            self.constants[value] = len(self.nodes)
            self.nodes.append(('constant', str(value)))
        return self.constants[value]

    def weight(self, index):
        if index not in self.weights:
            self.weights[index] = len(self.nodes)
            self.nodes.append(('weight', index))
        return self.weights[index]

    def operation(self, op, left, right):
        assert 0 <= left < len(self.nodes) and 0 <= right < len(self.nodes)
        result = len(self.nodes)
        self.nodes.append((op, left, right))
        self.gates += 1
        return result

    def add(self, left, right):
        return self.operation('add', left, right)

    def mul(self, left, right):
        return self.operation('mul', left, right)

    def sum(self, terms):
        terms = iter(terms)
        result = next(terms)
        for term in terms:
            result = self.add(result, term)
        return result

    def evaluate(self):
        values = []
        for node in self.nodes:
            tag = node[0]
            if tag == 'constant':
                value = sp.Rational(node[1])
            elif tag == 'weight':
                value = self.symbols[node[1]]
            elif tag == 'add':
                value = sp.expand(values[node[1]]+values[node[2]])
            elif tag == 'mul':
                value = sp.expand(values[node[1]]*values[node[2]])
            else:
                raise ValueError(tag)
            values.append(value)
        return values

    def serialize(self, output):
        return {'n': self.n, 'model': 'generic-B leaves; rational constants; binary add/mul',
                'gates': self.gates, 'output': output, 'nodes': self.nodes}


def build_rank_one_chain(n):
    """Explicitly initialized reciprocal row updates, retaining only future G entries."""
    source = RationalDAG(n)
    G = {(j, k): source.weight(j, k) for j in range(n) for k in range(n)}
    F = source.constant(1)
    x = [source.occupancy(i) for i in range(n)]
    snapshots = [{'processed': 0, 'F': F, 'G': G.copy()}]
    for i in range(n):
        old = G
        product = source.mul(F, old[i, i])
        F = source.add(F, source.mul(x[i], product))
        G = {}
        for j in range(i+1, n):
            for k in range(i+1, n):
                outer = source.mul(old[j, i], old[i, k])
                G[j, k] = source.add(old[j, k], source.mul(x[i], outer))
        snapshots.append({'processed': i+1, 'F': F, 'G': G.copy()})
    expected = 3*n+n*(n-1)*(2*n-1)//2
    assert source.gates == expected
    return source, F, snapshots, {'native_gates': expected,
                                  'formula': '3*n+n*(n-1)*(2*n-1)/2',
                                  'initial_data': 'F=1, G=B',
                                  'marker_substitution_gates': 2*n*n-1}


def compile_eager(source):
    scalar = ScalarDAG(source.n)
    coordinates = []
    stats = {'coefficient_multiplications': 0, 'coefficient_additions': 0}
    for node in source.nodes:
        tag = node[0]
        if tag == 'constant':
            current = {0: scalar.constant(node[1])} if node[1] else {}
        elif tag == 'weight':
            current = {0: scalar.weight(node[1])}
        elif tag == 'occupancy':
            current = {1 << node[1]: scalar.constant(1)}
        elif tag == 'add':
            current = coordinates[node[1]].copy()
            for mask, value in coordinates[node[2]].items():
                if mask in current:
                    current[mask] = scalar.add(current[mask], value)
                    stats['coefficient_additions'] += 1
                else:
                    current[mask] = value
        elif tag == 'mul':
            current = {}
            for left_mask, left in coordinates[node[1]].items():
                for right_mask, right in coordinates[node[2]].items():
                    if left_mask & right_mask:
                        continue
                    mask = left_mask | right_mask
                    term = scalar.mul(left, right)
                    stats['coefficient_multiplications'] += 1
                    if mask in current:
                        term = scalar.add(current[mask], term)
                        stats['coefficient_additions'] += 1
                    current[mask] = term
        else:
            raise ValueError(tag)
        coordinates.append(current)
    assert scalar.gates == sum(stats.values())
    stats['compiled_gates'] = scalar.gates
    stats['total_materialized_jet_entries'] = sum(map(len, coordinates))
    stats['max_jet_entries_per_source_node'] = max(map(len, coordinates))
    return scalar, coordinates, stats


def positive_supports(source):
    """Exact structural support for this positive circuit, no symbolic zero oracle."""
    supports = []
    for node in source.nodes:
        tag = node[0]
        if tag == 'constant':
            support = {0} if node[1] else set()
        elif tag == 'weight':
            support = {0}
        elif tag == 'occupancy':
            support = {1 << node[1]}
        elif tag == 'add':
            support = supports[node[1]] | supports[node[2]]
        elif tag == 'mul':
            support = {a | b for a in supports[node[1]] for b in supports[node[2]]
                       if not a & b}
        else:
            raise ValueError(tag)
        supports.append(support)
    return supports


def compile_demand(source, output, target_mask):
    """Backward mixed-jet propagation; memoize exactly requested source/mask pairs."""
    scalar = ScalarDAG(source.n)
    supports = positive_supports(source)
    memo = {}

    def coefficient(index, mask):
        if mask not in supports[index]:
            return None
        key = index, mask
        if key in memo:
            return memo[key]
        node = source.nodes[index]
        tag = node[0]
        if tag == 'constant':
            value = scalar.constant(node[1])
        elif tag == 'weight':
            value = scalar.weight(node[1])
        elif tag == 'occupancy':
            value = scalar.constant(1)
        elif tag == 'add':
            a, b = coefficient(node[1], mask), coefficient(node[2], mask)
            value = b if a is None else a if b is None else scalar.add(a, b)
        elif tag == 'mul':
            terms = []
            subset = mask
            while True:
                other = mask ^ subset
                if subset in supports[node[1]] and other in supports[node[2]]:
                    a, b = coefficient(node[1], subset), coefficient(node[2], other)
                    terms.append(scalar.mul(a, b))
                if subset == 0:
                    break
                subset = (subset-1) & mask
            value = scalar.sum(terms)
        else:
            raise ValueError(tag)
        memo[key] = value
        return value

    result = coefficient(output, target_mask)
    histogram = {}
    for _, mask in memo:
        size = mask.bit_count()
        histogram[size] = histogram.get(size, 0)+1
    return scalar, result, {'compiled_gates': scalar.gates,
                           'requested_source_mask_pairs': len(memo),
                           'requested_by_derivative_order': histogram,
                           'support_entries_charged_as_search_work': sum(map(len, supports)),
                           'no_free_projection': True}


def build_cycle_bell(n):
    """Directed-cycle factors followed by Bell partition recurrence, all scalar."""
    dag = ScalarDAG(n)
    B = [[dag.weight(i*n+j) for j in range(n)] for i in range(n)]
    cycles = {}
    path_states = 0
    for anchor in range(n):
        cycles[1 << anchor] = B[anchor][anchor]
        paths = {}
        higher = sum(1 << i for i in range(anchor+1, n))
        subsets = [mask for mask in range(1, 1 << n) if mask & higher == mask]
        for mask in subsets:
            ends = [j for j in range(n) if mask & (1 << j)]
            for j in ends:
                previous = mask ^ (1 << j)
                if previous == 0:
                    paths[mask, j] = B[anchor][j]
                else:
                    paths[mask, j] = dag.sum(dag.mul(paths[previous, k], B[k][j])
                                             for k in range(n) if previous & (1 << k))
                path_states += 1
            cycles[mask | (1 << anchor)] = dag.sum(dag.mul(paths[mask, j], B[j][anchor])
                                                 for j in ends)
    cycle_gates = dag.gates
    partitions = {0: dag.constant(1)}
    transitions = 0
    for mask in range(1, 1 << n):
        anchor_bit = mask & -mask
        terms = []
        subset = mask
        while subset:
            if subset & anchor_bit:
                terms.append(dag.mul(cycles[subset], partitions[mask ^ subset]))
                transitions += 1
            subset = (subset-1) & mask
        partitions[mask] = dag.sum(terms)
    assert transitions == (3**n-1)//2
    assert dag.gates-cycle_gates == 3**n-2**n
    return dag, partitions[(1 << n)-1], {
        'cycle_factor_gates': cycle_gates,
        'bell_recurrence_gates': dag.gates-cycle_gates,
        'bell_recurrence_formula': '3^n-2^n',
        'cycle_states': len(cycles), 'path_states': path_states,
        'partition_states': len(partitions),
        'partition_transitions': transitions,
        'initial_data': 'Q(empty)=1, C(singleton i)=B_ii',
        'marker_substitution_gates': 2*n*n-1}


def path_coefficient(symbols, n, j, k, subset):
    if not subset:
        return symbols[j*n+k]
    terms = []
    for order in permutations(subset):
        route = (j,)+order+(k,)
        terms.append(prod(symbols[a*n+b] for a, b in zip(route, route[1:])))
    return sp.expand(sum(terms))


def verify_layers(source, snapshots, coordinates, scalar_values):
    F_checks, G_checks, rows = [], [], []
    for snapshot in snapshots:
        processed = snapshot['processed']
        scalar_entries = len(coordinates[snapshot['F']])
        for mask in range(1 << processed):
            subset = tuple(i for i in range(processed) if mask & (1 << i))
            actual_F = scalar_values[coordinates[snapshot['F']][mask]]
            expected_F = permanent_on_subset(source.symbols, source.n, subset)
            F_checks.append(actual_F == expected_F)
        for (j, k), node in snapshot['G'].items():
            scalar_entries += len(coordinates[node])
            for mask in range(1 << processed):
                subset = tuple(i for i in range(processed) if mask & (1 << i))
                actual_G = scalar_values[coordinates[node][mask]]
                expected_G = path_coefficient(source.symbols, source.n, j, k, subset)
                G_checks.append(actual_G == expected_G)
        rows.append({'processed': processed, 'retained_G_components': len(snapshot['G']),
                     'F_jet_entries': len(coordinates[snapshot['F']]),
                     'total_retained_scalar_jet_entries': scalar_entries,
                     'maximum_derivative_order': processed})
    return {'all_F_prefix_coefficients_exact': all(F_checks),
            'all_G_prefix_path_coefficients_exact': all(G_checks),
            'F_checks': len(F_checks), 'G_checks': len(G_checks),
            'layers': rows,
            'peak_retained_scalar_states': max(row['total_retained_scalar_jet_entries'] for row in rows)}


def build_marked_circuit(A, variant='demand'):
    """Instantiate emitted generic-weight circuits as actual Q[z] scalar DAGs.

    p_ij are allowed rational leaves; binary squaring constructs every original
    marked z exponent. This helper performs no coefficient extraction at runtime.
    """
    import candidate
    A = candidate.check_matrix(A)
    n = len(A)
    if variant == 'bell':
        scalar, output, stats = build_cycle_bell(n)
    elif variant in ('demand', 'eager'):
        source, F, _, _ = build_rank_one_chain(n)
        if variant == 'demand':
            scalar, output, stats = compile_demand(source, F, (1 << n)-1)
        else:
            scalar, coordinates, stats = compile_eager(source)
            output = coordinates[F][(1 << n)-1]
    else:
        raise ValueError('Expected demand, eager, or bell')
    marked = candidate.DAG()
    entries = candidate.marked_entries(marked, A)
    compiled = []
    for node in scalar.nodes:
        tag = node[0]
        if tag == 'constant':
            value = marked.constant(Fraction(node[1]))
        elif tag == 'weight':
            value = entries[node[1]//n][node[1] % n]
        elif tag == 'add':
            value = marked.add(compiled[node[1]], compiled[node[2]])
        elif tag == 'mul':
            value = marked.mul(compiled[node[1]], compiled[node[2]])
        else:
            raise ValueError(tag)
        compiled.append(value)
    assert marked.gates == scalar.gates+2*n*n-1
    return marked, compiled[output], {
        'variant': variant, 'scalar_weight_gates': scalar.gates,
        'marker_and_entry_gates': 2*n*n-1,
        'total_gates': marked.gates, 'construction': stats}

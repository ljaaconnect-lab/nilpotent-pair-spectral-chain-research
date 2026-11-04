"""Compile the existing projector on a shared scalar DAG using reverse AD.

This is a measured candidate, not a claim of uniform polynomial size.
Only + and * gates are emitted. 0/1, constant folding and hash-consing are
explicit. The original a,z preparation is included.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent


class LimitReached(RuntimeError):
    pass


class DAG:
    def __init__(self, q, limit=600000):
        self.q, self.limit = q, limit
        self.nodes, self.mask, self.memo = [], [], {}
        self.inputs = {}
        self.gates = 0
        self.zero = self.const(0)
        self.one = self.const(1)

    def intern(self, node, mask=0):
        if node in self.memo:
            return self.memo[node]
        if len(self.nodes) >= self.limit:
            raise LimitReached(f'node limit {self.limit}')
        idx = len(self.nodes)
        self.nodes.append(node)
        self.mask.append(mask)
        self.memo[node] = idx
        if node[0] in ('add', 'mul'):
            self.gates += 1
        return idx

    def const(self, value):
        return self.intern(('const', value % self.q))

    def var(self, name, mask=0):
        idx = self.intern(('input', name), mask)
        self.inputs[name] = idx
        return idx

    def add(self, a, b):
        if a == self.zero:
            return b
        if b == self.zero:
            return a
        na, nb = self.nodes[a], self.nodes[b]
        if na[0] == nb[0] == 'const':
            return self.const(na[1] + nb[1])
        if a == b:
            return self.mul(self.const(2), a)
        a, b = sorted((a, b))
        return self.intern(('add', a, b), self.mask[a] | self.mask[b])

    def mul(self, a, b):
        if a == self.zero or b == self.zero:
            return self.zero
        if a == self.one:
            return b
        if b == self.one:
            return a
        na, nb = self.nodes[a], self.nodes[b]
        if na[0] == nb[0] == 'const':
            return self.const(na[1] * nb[1])
        a, b = sorted((a, b))
        return self.intern(('mul', a, b), self.mask[a] | self.mask[b])

    def sum(self, terms):
        acc = self.zero
        for term in terms:
            acc = self.add(acc, term)
        return acc

    def product(self, terms):
        acc = self.one
        for term in terms:
            acc = self.mul(acc, term)
        return acc

    def ancestors(self, out):
        found, todo = set(), [out]
        while todo:
            node = todo.pop()
            if node in found:
                continue
            found.add(node)
            typ, *args = self.nodes[node]
            if typ in ('add', 'mul'):
                todo.extend(args)
        return sorted(found)

    def live_gates(self, out):
        return sum(self.nodes[idx][0] in ('add', 'mul') for idx in self.ancestors(out))

    def gradient(self, out, variables):
        wanted = 0
        for variable in variables:
            wanted |= self.mask[variable]
        ancestors = self.ancestors(out)
        adjoint = {out: self.one}
        for idx in reversed(ancestors):
            if not self.mask[idx] & wanted or idx not in adjoint:
                continue
            typ, *args = self.nodes[idx]
            if typ not in ('add', 'mul'):
                continue
            a, b = args
            for child, other in ((a, b), (b, a)):
                if not self.mask[child] & wanted:
                    continue
                contribution = adjoint[idx] if typ == 'add' else self.mul(adjoint[idx], other)
                adjoint[child] = self.add(adjoint.get(child, self.zero), contribution)
        return [adjoint.get(variable, self.zero) for variable in variables]

    def evaluate(self, out, values):
        table = {}
        for idx in self.ancestors(out):
            typ, *args = self.nodes[idx]
            if typ == 'const':
                value = args[0]
            elif typ == 'input':
                value = values[args[0]]
            elif typ == 'add':
                value = table[args[0]] + table[args[1]]
            else:
                value = table[args[0]] * table[args[1]]
            table[idx] = value % self.q
        return table[out]


def compile_projector(n, q=97, limit=600000):
    dag = DAG(q, limit)
    z = dag.var('z')
    powers = [z]
    for _ in range(n * n - 1):
        powers.append(dag.mul(powers[-1], powers[-1]))
    b = []
    for i in range(n):
        row = []
        for j in range(n):
            a = dag.var(f'a_{i}_{j}')
            row.append(dag.mul(dag.add(dag.one, dag.mul(a, a)), powers[i * n + j]))
        b.append(row)
    s = [dag.var(f's_{j}', 1 << j) for j in range(n)]
    out = dag.product(dag.sum(dag.mul(b[i][j], s[j]) for j in range(n)) for i in range(n))
    stats = [{'step': 0, 'allocated_gates': dag.gates, 'live_gates': dag.live_gates(out)}]
    try:
        for r in range(1, n * (n - 1) // 2 + 1):
            before = dag.gates
            first = dag.gradient(out, s)
            first_added = dag.gates - before
            diagonal, second_added = [], []
            for j in range(n):
                before_second = dag.gates
                diagonal.append(dag.gradient(first[j], [s[j]])[0])
                second_added.append(dag.gates - before_second)
            correction = dag.sum(dag.mul(dag.mul(s[j], s[j]), diagonal[j]) for j in range(n))
            correction = dag.mul(dag.const(-pow(2 * r, -1, q)), correction)
            out = dag.add(out, correction)
            stats.append({'step': r, 'reverse_first_gates_added': first_added,
                          'reverse_second_gates_added': second_added,
                          'allocated_gates': dag.gates, 'live_gates': dag.live_gates(out)})
        return dag, out, stats, True
    except LimitReached:
        stats.append({'stopped_during_step': r, 'allocated_gates': dag.gates,
                      'node_limit': limit})
        return dag, out, stats, False


def specialize_into(source, out, target, substitutions):
    wires = {}
    for idx in source.ancestors(out):
        typ, *args = source.nodes[idx]
        if typ == 'const':
            wire = target.const(args[0])
        elif typ == 'input':
            wire = target.const(substitutions[args[0]]) if args[0] in substitutions else target.var(args[0])
        elif typ == 'add':
            wire = target.add(wires[args[0]], wires[args[1]])
        else:
            wire = target.mul(wires[args[0]], wires[args[1]])
        wires[idx] = wire
    return wires[out]


def compile_full_table(source, out, n, labels, size, omega):
    target = DAG(source.q, max(2000000, source.limit))
    spectrum = [specialize_into(source, out, target,
                {f's_{j}': pow(omega, f * labels[j], source.q) for j in range(n)})
                for f in range(size)]
    spectrum_gates = target.gates
    width = size.bit_length() - 1
    state = [spectrum[int(f'{k:0{width}b}'[::-1], 2)] for k in range(size)]
    length = 2
    while length <= size:
        new = list(state)
        for start in range(0, size, length):
            for j in range(length // 2):
                u = state[start + j]
                v = target.mul(state[start + j + length // 2],
                               target.const(pow(omega, (-j * size // length) % size, source.q)))
                new[start + j] = target.add(u, v)
                new[start + j + length // 2] = target.add(u, target.mul(target.const(-1), v))
        state = new
        length *= 2
    state = [target.mul(v, target.const(pow(size, -1, source.q))) for v in state]
    live = set()
    for wire in state:
        live.update(target.ancestors(wire))
    live_gates = sum(target.nodes[idx][0] in ('add', 'mul') for idx in live)
    return target, state, {'spectrum_allocated_gates': spectrum_gates,
                           'complete_table_allocated_gates': target.gates,
                           'complete_table_live_gates': live_gates}

def collision(u):
    return sum(x * (x - 1) // 2 for x in u)


def direct_reference(n, q, values):
    total = 0
    for labels in product(range(n), repeat=n):
        occupancy = [0] * n
        weight = 1
        for i, j in enumerate(labels):
            occupancy[j] += 1
            b = (1 + values[f'a_{i}_{j}'] ** 2) * pow(values['z'], 1 << (i * n + j), q)
            weight = weight * b * values[f's_{j}'] % q
        if collision(occupancy) == 0:
            total = (total + weight) % q
    return total


def verify(max_n, limit):
    rng = random.Random(20261101)
    cases = []
    for n in range(1, max_n + 1):
        dag, out, stats, complete = compile_projector(n, limit=limit)
        item = {'n': n, 'q': 97, 'complete': complete, 'steps': stats}
        if complete:
            for _ in range(3):
                values = {name: rng.randrange(97) for name in dag.inputs}
                assert dag.evaluate(out, values) == direct_reference(n, 97, values)
            size = 1
            while size <= n:
                size *= 2
            assert (97 - 1) % size == 0
            omega = pow(5, (97 - 1) // size, 97)
            assert pow(omega, size, 97) == 1 and pow(omega, size // 2, 97) != 1
            labels = [rng.randrange(size) for _ in range(n)]
            values = {name: rng.randrange(97) for name in dag.inputs}
            spectrum = []
            for f in range(size):
                values.update({f's_{j}': pow(omega, f * labels[j], 97) for j in range(n)})
                actual = dag.evaluate(out, values)
                assert actual == direct_reference(n, 97, values)
                spectrum.append(actual)
            table = [pow(size, -1, 97) * sum(spectrum[f] * pow(omega, (-f * k) % size, 97)
                     for f in range(size)) % 97 for k in range(size)]
            assert all(v == 0 for k, v in enumerate(table) if k != sum(labels) % size)
            assert table[sum(labels) % size] == spectrum[0]
            compiled, slots, full_cost = compile_full_table(dag, out, n, labels, size, omega)
            original_values = {name: value for name, value in values.items() if not name.startswith('s_')}
            assert set(compiled.inputs) == set(original_values)
            assert [compiled.evaluate(slot, original_values) for slot in slots] == table
            one_point = DAG(97, max(2000000, limit))
            one_out = specialize_into(dag, out, one_point, {f's_{j}': 1 for j in range(n)})
            item.update({'generic_evaluation_checks': 3, 'spectral_frequencies': size,
                         'terminal_live_scalar_gates': dag.live_gates(out), 'table': table,
                         'all_one_point_live_gates': one_point.live_gates(one_out),
                         'full_table_cost': full_cost})
        cases.append(item)
        print(json.dumps({'n': n, 'complete': complete, 'last': stats[-1]}), flush=True)
        if not complete:
            break
    return {'status': 'passed', 'general_polynomial_closure': False,
            'scope': 'direct AD compilation of the existing projector on a shared scalar DAG; measured candidate only',
            'count_includes': 'kernel counts include a,z preparation and symbolic s; full_table_cost additionally specializes and shares all frequencies and emits the INTT from a,z only',
            'sharing': 'hash-consed binary commutative gates; constant folding; eliminate zero and one; add(x,x)=2*x',
            'cases': cases}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-n', type=int, default=5)
    parser.add_argument('--limit', type=int, default=600000)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    source = Path(__file__)
    before = sha256(source.read_bytes()).hexdigest()
    report = verify(args.max_n, args.limit)
    assert before == sha256(source.read_bytes()).hexdigest()
    report['source_sha256'] = {source.name: before}
    if args.write_report:
        (HERE / 'ad-validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

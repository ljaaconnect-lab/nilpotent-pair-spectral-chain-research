"""Inspect existing block-coefficient roots in the immediate-projection DAG.

Every witness query must allocate zero nodes. Semantic separators use only
the original a,z inputs. This audits one compiler, not all scalar circuits.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent))
from direct_projection import compile_projected, DAG_FOLDER  # noqa: E402


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def row_support(dag, root):
    return sorted({int(dag.nodes[i][1].split('_')[1])
                   for i in dag.reachable([root])
                   if dag.nodes[i][0] == 'v' and dag.nodes[i][1].startswith('a_')})


def addition_descendants(dag, root):
    seen, work = set(), [root]
    while work:
        node = work.pop()
        if node in seen:
            continue
        seen.add(node)
        if dag.nodes[node][0] == '+':
            work.extend(dag.nodes[node][1:])
    return seen


def verify_case(n):
    assert n >= 4 and n & (n - 1) == 0
    Q, m, N = 97, n // 2, 1 << n.bit_length()
    assert Q > n * (n - 1) // 2 and (Q - 1) % N == 0
    labels = [(j*j + 2*j + 1) % N for j in range(n)]
    dag, outputs, stages = compile_projected(n, Q, N, labels)
    y = outputs[sum(labels) % N]
    initial = stages[0]['root']
    assert dag.nodes[initial][0] == '*'
    U, V = dag.nodes[initial][1:]
    rows_u, rows_v = row_support(dag, U), row_support(dag, V)
    assert len(rows_u) == len(rows_v) == m
    assert not set(rows_u) & set(rows_v)
    assert sorted(rows_u + rows_v) == list(range(n))

    columns = list(itertools.combinations(range(n), m))
    expected = math.comb(n, m)
    assert len(columns) == expected
    s = [dag.intern[('v', f's_{j}')] for j in range(n)]
    reachable_before_queries = dag.reachable([y])
    additive_paths = addition_descendants(dag, y)
    allocated_before = len(dag.nodes)
    left, right, products = [], [], []
    query_records = []

    def query_block(root, selected):
        selected = set(selected)
        allocated = len(dag.nodes)
        for j in range(n):
            if j in selected:
                root = dag.derivative(root, j)
                assert len(dag.nodes) == allocated, 'Derivative query created evidence'
            root = dag.substitute([root], {s[j]: dag.zero})[0]
            assert len(dag.nodes) == allocated, 'Substitution query created evidence'
        assert root in reachable_before_queries
        assert dag.nodes[root][0] in ('+', '*')
        assert dag.degrees[root] == (0,) * n
        assert not any(dag.nodes[i][0] == 'v' and dag.nodes[i][1].startswith('s_')
                       for i in dag.reachable([root]))
        return root

    for chosen in columns:
        allocated = len(dag.nodes)
        complement = sorted(set(range(n)) - set(chosen))
        u = query_block(U, chosen)
        v = query_block(V, complement)
        product = dag.mul(u, v)
        assert len(dag.nodes) == allocated, 'Product query created evidence'
        assert product in reachable_before_queries
        assert product in additive_paths
        assert dag.nodes[product][0] == '*'
        assert set(dag.nodes[product][1:]) == {u, v}
        left.append(u)
        right.append(v)
        products.append(product)
        query_records.append({'columns': list(chosen), 'left_root': u,
                              'right_root': v, 'product_root': product,
                              'allocated_nodes': len(dag.nodes) - allocated})

    assert len(set(left)) == len(set(right)) == len(set(products)) == expected
    assert not set(left) & set(right)
    assert not set(products) & (set(left) | set(right))
    assert len(dag.nodes) == allocated_before

    # Separate every root using actual initial a,z inputs. Both row blocks
    # are assigned bijectively to complementary sets of columns.
    roots = left + right + products + [y]
    for target, chosen in enumerate(columns):
        complement = sorted(set(range(n)) - set(chosen))
        inputs = {f'a_{i}_{j}': 22 for i in range(n) for j in range(n)}
        inputs['z'] = 1
        for i, j in zip(rows_u, chosen):
            inputs[f'a_{i}_{j}'] = 0
        for i, j in zip(rows_v, complement):
            inputs[f'a_{i}_{j}'] = 0
        values = dag.evaluate(roots, inputs)
        indicator = [int(index == target) for index in range(expected)]
        assert values == indicator * 3 + [1], (n, target, values)
    assert len(dag.nodes) == allocated_before
    return {
        'n': n, 'm': m, 'Q': Q, 'N': N, 'labels': labels,
        'status': 'passed', 'final_scalar_gates': dag.count([y]),
        'allocated_compiler_nodes': allocated_before,
        'row_blocks': [rows_u, rows_v],
        'roots_per_family': expected,
        'left_roots_reachable': len(left),
        'right_roots_reachable': len(right),
        'marked_products_reachable_through_additions': len(products),
        'witness_query_allocations': len(dag.nodes) - allocated_before,
        'separator_entries_per_family': expected * expected,
        'separator_checks_all_three_families': 3 * expected * expected,
        'final_output_separator_checks': expected,
        'original_input_separator': 'z=1; a_ij=0 on the chosen bijection, 22 elsewhere',
        'queries': query_records,
    }


def main():
    sources = [HERE.parent / 'direct_projection.py',
               DAG_FOLDER / 'shared_operator_dag.py',
               HERE / 'CROISSANCE_PROJECTION.md', Path(__file__)]
    hashes = {p.relative_to(PROJECT).as_posix(): digest(p) for p in sources}
    cases = [verify_case(n) for n in (4, 8)]
    assert hashes == {p.relative_to(PROJECT).as_posix(): digest(p) for p in sources}
    report = {
        'status': 'passed', 'source_sha256': hashes,
        'scope': 'The exact immediate-projection compiler only; not a lower bound for all scalar circuits.',
        'general_claim': 'For n=2^k>=4, C_Y(n)>=binomial(n,n/2)>=2^(n/2).',
        'compiler_uses_jet_tables': False,
        'witnesses_are_external_checks_only': True,
        'general_reachability_proof_formalized_in_lean': False,
        'cases': cases,
    }
    destination = HERE / 'block-roots-validation.json'
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'passed', 'cases': [
        {key: case[key] for key in ('n', 'final_scalar_gates', 'roots_per_family',
                                   'witness_query_allocations', 'separator_entries_per_family')}
        for case in cases]}, ensure_ascii=False))


if __name__ == '__main__':
    main()

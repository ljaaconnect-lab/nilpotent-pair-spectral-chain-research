"""Marked scalar Glynn/half-character contraction, shared along a Gray path.

This is a new factorization relative to the subset-transfer baseline, not a
polynomial-size solution. The exact gate formula is 5*n*(n-1)+n*2**n.
"""
from fractions import Fraction
import candidate


def gray_signs(n):
    for step in range(1 << (n - 1)):
        mask = step ^ (step >> 1)
        yield mask, [1] + [-1 if mask & (1 << (j - 1)) else 1 for j in range(1, n)]


def build_marked_gray(A):
    A = candidate.check_matrix(A)
    n = len(A)
    r = 1 << (n - 1)
    dag = candidate.DAG()
    entries = candidate.marked_entries(dag, A)
    preparation = dag.gates
    # Every column except the highest Gray bit flips in both directions; the
    # highest Gray bit flips once, from +1 to -1. Precompute only needed signs.
    positive_update = {(i, j): dag.mul(dag.constant(2), entries[i][j])
                       for i in range(n) for j in range(1, n - 1)}
    negative_update = {(i, j): dag.mul(dag.constant(-2), entries[i][j])
                       for i in range(n) for j in range(1, n)}
    update_preparation = dag.gates - preparation
    rows = [dag.sum(entries[i]) for i in range(n)]
    initial_row_sum_gates = dag.gates - preparation - update_preparation
    positive, negative = [], []
    prior = 0
    path = []
    for step, (mask, signs) in enumerate(gray_signs(n)):
        if step:
            flip = mask ^ prior
            assert flip and flip & (flip - 1) == 0
            column = flip.bit_length()
            updates = negative_update if mask & flip else positive_update
            rows = [dag.add(rows[i], updates[i, column]) for i in range(n)]
        term = dag.product(rows)
        parity = (-1) ** mask.bit_count()
        (positive if parity == 1 else negative).append(term)
        path.append({"step": step, "mask": mask, "signs": signs, "parity": parity})
        prior = mask
    output = dag.mul(dag.sub(dag.sum(positive), dag.sum(negative)),
                     dag.constant(Fraction(1, r)))
    expected = 5 * n * (n - 1) + n * 2 ** n
    assert dag.gates == expected
    return dag, output, {
        "n": n, "dimension": r, "gates": dag.gates,
        "formula": "5*n*(n-1)+n*2^n",
        "marker_and_entry_gates": preparation,
        "signed_update_preparation_gates": update_preparation,
        "initial_row_sum_gates": initial_row_sum_gates,
        "gray_update_gates": n * (r - 1),
        "row_product_gates": (n - 1) * r,
        "bucket_sum_gates": r - 2,
        "signed_bucket_combination_and_normalization_gates": 3,
        "scalar_leaf_data": "z; p_ij=1+a_ij^2; 1,-1,2,-2,2^(1-n)",
        "path": path,
    }

"""Cheap explicit Gram/occupation coefficient encoding of the marked permanent.

The full polynomial circuit is small; no coefficient-extraction circuit or
free determinant/contraction is provided. General proof obligations are
conditional until separately kernel verified.
"""
import sympy as sp
import candidate


def gram_factors(b, y):
    """X is column incidence; W has edge weights b_ij*y_i on its diagonal."""
    n = len(b)
    if len(y) != n or any(len(row) != n for row in b):
        raise ValueError("square weights and one auxiliary per row required")
    X = sp.SparseMatrix(n, n * n, {(j, i * n + j): 1 for i in range(n) for j in range(n)})
    W = sp.SparseMatrix(n * n, n * n,
                        {(i * n + j, i * n + j): b[i][j] * y[i]
                         for i in range(n) for j in range(n)})
    return X, W


def symbolic_encoding(b, auxiliary):
    n = len(b)
    q = n + 1
    return sp.Mul(*(sp.Add(*(b[i][j] * auxiliary ** (q ** i) for i in range(n)))
                    for j in range(n)))


def build_marked_encoding(A):
    """Actually compile the diagonal determinant as n-1 scalar multiplies.

    The existing exact evaluator names the auxiliary axis t; in mathematical
    descriptions this new independent auxiliary is called s.
    """
    A = candidate.check_matrix(A)
    n = len(A)
    q = n + 1
    dag = candidate.DAG()
    b = candidate.marked_entries(dag, A)
    prep = dag.gates
    s = dag.variable("t")
    row_markers = [s]
    for _ in range(1, n):
        row_markers.append(dag.power(row_markers[-1], q))
    aux = dag.gates - prep
    weighted = [[dag.mul(b[i][j], row_markers[i]) for j in range(n)] for i in range(n)]
    weight_cost = dag.gates - prep - aux
    columns = [dag.sum(weighted[i][j] for i in range(n)) for j in range(n)]
    sum_cost = dag.gates - prep - aux - weight_cost
    output = dag.product(columns)
    product_cost = dag.gates - prep - aux - weight_cost - sum_cost
    power_cost = q.bit_length() - 1 + q.bit_count() - 1
    assert dag.gates == 4 * n * n - 2 + (n - 1) * power_cost
    return dag, output, {
        "n": n, "q": q, "T": sum(q ** i for i in range(n)),
        "auxiliary_degree": n * q ** (n - 1),
        "auxiliary_min_degree": n,
        "original_marker_and_entry_gates": prep,
        "auxiliary_marker_gates": aux,
        "weighted_entry_gates": weight_cost,
        "column_sum_gates": sum_cost,
        "diagonal_product_gates": product_cost,
        "gates": dag.gates,
        "formula": "4*n^2-2+(n-1)*(floor(log2(n+1))+popcount(n+1)-1)",
        "input_data": "Original p_ij=1+a_ij^2 constants and z; independent auxiliary s",
        "matrix_factors": "X is n by n^2 column incidence; W is n^2 by n^2 edge-weight diagonal",
        "coefficient_extraction_gates": None,
        "extraction_status": "No cheap scalar extractor supplied; dictionary extraction in the evaluator is expanded verification",
    }

"""Constructive J0,J1 only; not an initialization for the full jet recurrence.

Every operation below is an actual scalar add/mul gate. The second-order
Euler operator is never used as a gate, and no root-target oracle is called.
This source is retained as an untested partial constructor under n65's
strict protocol; no full polynomial state family has been supplied.
"""
from fractions import Fraction

from candidate import determinant,marked_entries,check_matrix
from euler_compiler import ScalarGraph,seed_gate_count


def initial_gate_formula(n,marked=False):
    if n < 2:
        raise ValueError("n>=2 required")
    D = n*(n-1)//2
    minor_cost = seed_gate_count(n-2) if n>2 else 0
    result = seed_gate_count(n)+D*D*minor_cost+4*D*D-1
    return result+(2*n*n-1 if marked else 0)


def build_initial_jets(n,A=None):
    """Return a real two-output DAG for det(X) and N_inv det(X).

    A=None leaves formal x0..x(n²-1). Otherwise the exact prescribed
    p=1+a² constants and all formal binary z markers are built explicitly.
    Full jets J2..JD and a cheap scalar transition on them are NOT provided.
    """
    if n < 2:
        raise ValueError("n>=2 required")
    graph = ScalarGraph(shared=False)
    if A is None:
        X = [[graph.variable(f"x{i*n+j}") for j in range(n)] for i in range(n)]
    else:
        A = check_matrix(A)
        if len(A) != n:
            raise ValueError("matrix size must equal n")
        X = marked_entries(graph,A)
    j0 = determinant(graph,X)
    terms = []
    for i in range(n):
        for l in range(i+1,n):
            rows = [r for r in range(n) if r not in (i,l)]
            for j in range(n):
                for m in range(j):
                    cols = [c for c in range(n) if c not in (m,j)]
                    minor = determinant(graph,[[X[r][c] for c in cols] for r in rows]) if rows else graph.constant(1)
                    edge_product = graph.mul(X[i][j],X[l][m])
                    projected = graph.mul(edge_product,minor)
                    coefficient = -(-1)**(i+l+j+m)
                    terms.append(graph.mul(graph.constant(coefficient),projected))
    j1 = graph.sum(terms)
    assert graph.gates == initial_gate_formula(n,A is not None)
    return graph,(j0,j1),{"n":n,"provided_jets":[0,1],
        "required_jet_range":[0,n*(n-1)//2],"gates":graph.gates,
        "formula_scope":"actual unoptimized partial constructor, no full polynomial recurrence",
        "formal_generic_semantics":"not kernel verified in n65",
        "numerical_validation":"not executed: no complete polynomial candidate isolated"}

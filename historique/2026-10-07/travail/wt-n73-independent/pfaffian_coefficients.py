"""Fixed paired edge ports and an actual scalar trace-Pfaffian compiler.

No root-target contraction is computed here. Universally claimed identities
remain informal until their complete kernel dependency chain is accepted.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations
from math import comb, factorial

import sympy as sp

from candidate import DAG, matrix_product
from euler_identity import inversion_sign


def sign(value):
    return (value > 0)-(value < 0)


def matchings(n):
    for k in range(n+1):
        for rows in combinations(range(n),k):
            for cols in combinations(range(n),k):
                for order in permutations(cols):
                    yield tuple(i*n+j for i,j in zip(rows,order))


def mobius_coefficient(n,matching):
    k = len(matching)
    result = 0
    for mask in range(1 << k):
        selected = [matching[a]%n for a in range(k) if mask & (1 << a)]
        inversions = sum(selected[a] > selected[b] for a in range(len(selected)) for b in range(a+1,len(selected)))
        result += (-1)**(k-len(selected)+inversions)
    return result


def column_pattern(n,matching):
    cols = [edge%n for edge in matching]
    ordered = sorted(cols)
    ranks = {column:i for i,column in enumerate(ordered)}
    return tuple(ranks[column] for column in cols)


def local_matrix(columns):
    k = len(columns)
    d = k+1 if k%2 else k+2
    augmented = [[0]*d for _ in range(d)]
    for a in range(k):
        for b in range(a+1,k):
            augmented[a][b] = sign(columns[b]-columns[a])
            augmented[b][a] = -augmented[a][b]
        augmented[a][k] = -1
        augmented[k][a] = 1
    matrix = [[0]*d for _ in range(d)]
    for a in range(d):
        for b in range(a+1,d):
            matrix[a][b] = 1-(-1)**(a+b)*augmented[a][b]
            matrix[b][a] = -matrix[a][b]
    return matrix


def fixed_port_matrix(n):
    N = n*n
    d = 2*N+2
    result = [[0]*d for _ in range(d)]

    def put(i,j,value):
        result[i][j] = value
        result[j][i] = -value

    for e in range(N+1):
        put(2*e,2*e+1,1 if e == N else -1)
        for f in range(e+1,N+1):
            put(2*e,2*f,1)
            column_sign = 1 if f == N else sign(f%n-e%n)
            put(2*e+1,2*f+1,-column_sign)
    return result


def principal_ports(n,matching):
    return [port for e in matching for port in (2*e,2*e+1)]+[2*n*n,2*n*n+1]


def principal(matrix,indices):
    return [[matrix[i][j] for j in indices] for i in indices]


def pfaffian_oracle(matrix):
    """Independent exact SymPy matching expansion, validation only."""
    A = sp.Matrix(matrix)
    states = 0

    @lru_cache(None)
    def recur(indices):
        nonlocal states
        states += 1
        if not indices:
            return sp.Integer(1)
        first = indices[0]
        result = sp.Integer(0)
        for position in range(1,len(indices)):
            second = indices[position]
            entry = A[first,second]
            if entry:
                rest = indices[1:position]+indices[position+1:]
                result += (-1)**(position+1)*entry*recur(rest)
        return result

    return int(recur(tuple(range(A.rows)))), {"oracle_subset_states":states,
            "scope":"SymPy exact expansion is only a validation oracle"}


def trace_gate_formula(d):
    if d < 2 or d%2:
        raise ValueError("even positive order required")
    m = d//2
    return d*(d-1)//2+d*d//2+(m-1)*(2*d**3-d*d)+m*(d-1)+m//2+m*(m+1)


def trace_circuit(d):
    """Actual shared fan-in-two circuit with skew upper-entry input leaves."""
    if d < 2 or d%2:
        raise ValueError("even positive order required")
    m = d//2
    graph = DAG()
    A = [[graph.constant(0) for _ in range(d)] for _ in range(d)]
    for i in range(d):
        for j in range(i+1,d):
            A[i][j] = graph.variable(f"a_{i}_{j}")
            A[j][i] = graph.mul(graph.constant(-1),A[i][j])
    # Standard J, J²=-I. Pointer row permutations are free wiring; every
    # row negation remains an explicit multiplication by -1, including zeros.
    B = [[graph.mul(graph.constant(-1),A[i+1][j]) if i%2 == 0 else A[i-1][j]
          for j in range(d)] for i in range(d)]
    powers = [None,B]
    for _ in range(2,m+1):
        powers.append(matrix_product(graph,powers[-1],B))
    signed_traces = [None]
    for i in range(1,m+1):
        trace = graph.sum(powers[i][j][j] for j in range(d))
        signed_traces.append(trace if i%2 else graph.mul(graph.constant(-1),trace))
    q = [graph.constant(1)]
    for k in range(1,m+1):
        weighted = graph.sum(graph.mul(signed_traces[i],q[k-i]) for i in range(1,k+1))
        q.append(graph.mul(graph.constant(Fraction(1,2*k)),weighted))
    assert graph.gates == trace_gate_formula(d)
    return graph,q[m]


def evaluate_trace(graph,output,matrix):
    """Interpret every actual gate in Q; no shortcut to a determinant/Pfaffian."""
    values = []
    evaluated = 0
    for node in graph.nodes:
        op = node["op"]
        if op == "constant":
            value = Fraction(node["value"])
        elif op == "variable":
            _,i,j = node["name"].split("_")
            value = Fraction(matrix[int(i)][int(j)])
        else:
            left,right = values[node["left"]],values[node["right"]]
            value = left+right if op == "add" else left*right
            evaluated += 1
        values.append(value)
    assert evaluated == graph.gates
    return values[output], {"actual_scalar_gate_evaluations":evaluated}


def matching_count(n):
    return sum(comb(n,k)**2*factorial(k) for k in range(n+1))

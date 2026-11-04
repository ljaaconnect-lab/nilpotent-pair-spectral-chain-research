"""Positive local constructions for n66; no root contraction is implemented.

All transitions below are actual fan-in-two scalar DAGs.  A four-port basis
transform does not provide a cheap transform of an entire 2*n*n-port family.
"""
from fractions import Fraction
from itertools import product

import sympy as sp

from candidate import DAG


def walsh_transition(graph, values, inverse=False):
    """H^{tensor r} on an explicit vector of length 2^r, charged butterfly."""
    values = list(values)
    length = len(values)
    if length < 1 or length & (length-1):
        raise ValueError("power-of-two vector length required")
    width = 1
    while width < length:
        updated = values.copy()
        for start in range(0, length, 2*width):
            for offset in range(width):
                a, b = values[start+offset], values[start+offset+width]
                updated[start+offset] = graph.add(a,b)
                updated[start+offset+width] = graph.sub(a,b)
        values = updated
        width *= 2
    if inverse:
        values = [graph.mul(graph.constant(Fraction(1,length)),v) for v in values]
    return values


def local_basis_circuit(roundtrip=False):
    graph = DAG()
    leaves = [graph.variable(f"f{i}") for i in range(16)]
    transformed = walsh_transition(graph,leaves)
    restored = walsh_transition(graph,transformed,inverse=True) if roundtrip else None
    return graph, transformed, restored


def scalar_interpret(graph, assignments):
    """Independent direct scalar interpretation, including every live gate."""
    values = []
    for node in graph.nodes:
        if node["op"] == "constant":
            q = Fraction(node["value"])
            value = sp.Rational(q.numerator,q.denominator)
        elif node["op"] == "variable":
            value = assignments[node["name"]]
        else:
            a,b = values[node["left"]],values[node["right"]]
            value = a+b if node["op"] == "add" else a*b
            value = sp.expand(value)
        values.append(value)
    return values


def local_pfaffian_minor(mask):
    """Literal principal Pfaffian of fixed J4, not a root Pfaffian gate."""
    indices = [i for i in range(4) if mask & (1 << i)]
    if len(indices)%2:
        return 0
    if not indices:
        return 1
    if len(indices) == 2:
        return 1
    # Pf J4 = J01*J23 - J02*J13 + J03*J12.
    return 1*1-1*1+1*1


def residual_circuit():
    """h*(1+(a-U)*(b-V))-(h-b*U)*(h-a*V)=U*V, without division."""
    graph = DAG()
    a,b,U,V = [graph.variable(name) for name in ("a","b","U","V")]
    h = graph.add(graph.constant(1),graph.mul(a,b))
    F = graph.add(graph.constant(1),graph.mul(graph.sub(a,U),graph.sub(b,V)))
    gaussian = graph.mul(graph.sub(h,graph.mul(b,U)),graph.sub(h,graph.mul(a,V)))
    residual = graph.sub(graph.mul(h,F),gaussian)
    return graph,residual


def layout(n):
    """Explicit polynomial-size LOCAL block layout, not the entire extractor."""
    if n < 1:
        raise ValueError("positive n required")
    return {"n":n,"edges":n*n,"local_tensor_legs":4,
            "local_gaussian_block_order":4,"total_local_positions":4*n*n,
            "local_forward_scalar_gates":96*n*n,
            "local_roundtrip_scalar_gates":208*n*n,
            "whole_family_legs":2*n*n,
            "whole_family_explicit_values":2**(2*n*n),
            "whole_family_unshared_walsh_gates":3*(2*n*n)*2**(2*n*n-1),
            "whole_family_transform_scope":"cost of the direct explicit-vector route; no lower bound",
            "root_target_compiled":False}

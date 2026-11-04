"""Separate n66 carry supplement: exact bit kernels, not a root extractor.

The bit variables below label tensor components.  They are not the B entries,
and evaluating one component is not contracting the complete tensor family.
All arithmetic circuits use only the inherited binary add/mul DAG.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import product

from candidate import DAG


def words(n):
    return tuple(product((0, 1), repeat=n))


def parity(xs):
    return sum(xs) % 2


def sgn(exponent):
    return -1 if exponent % 2 else 1


def local_T(p, x, y, q):
    return (1 if (p+x+y+q) % 2 == 0 else 0) * sgn(x*y+p*y)


def native_kernel(x, y, q):
    """Boundary order [x0,y0,...,xN-1,yN-1,q], p0=0."""
    assert len(x) == len(y)
    if q != (parity(x)+parity(y)) % 2:
        return 0
    phase = sum(x[j]*y[i] for i in range(len(x)) for j in range(i+1))
    phase += sum(y)*(sum(y)-1)//2
    return sgn(phase)


def grouped_kernel(x, y, q):
    """Same Gaussian tensor after actual port permutation to [all x,all y,q]."""
    if q != (parity(x)+parity(y)) % 2:
        return 0
    return sgn(sum(x)*sum(y)+sum(y)*(sum(y)-1)//2)


def grouped_shuffle(x, y):
    return sum(y[i]*x[j] for i in range(len(x)) for j in range(i+1,len(x))) % 2


def native_order(N):
    return [label for i in range(N) for label in (("x",i),("y",i))]+[("q",0)]


def grouped_order(N):
    return [("x",i) for i in range(N)]+[("y",i) for i in range(N)]+[("q",0)]


def selected_shuffle(source, target, occupied):
    positions = {name:i for i,name in enumerate(target)}
    selected = [positions[name] for name in source if name in occupied]
    return sum(selected[i] > selected[j] for i in range(len(selected))
               for j in range(i+1,len(selected))) % 2


def grouped_matrix(N):
    """A single explicit skew matrix for the grouped coherent Gaussian family."""
    d = 2*N+1
    result = [[0]*d for _ in range(d)]
    for i in range(d):
        for j in range(i+1,d):
            if j == 2*N:
                value = 1
            elif i < N <= j:
                value = -1
            elif i >= N:
                value = -1
            else:
                value = 1
            result[i][j], result[j][i] = value, -value
    return result


def native_matrix(N):
    grouped = grouped_matrix(N)
    positions = {name:i for i,name in enumerate(grouped_order(N))}
    perm = [positions[name] for name in native_order(N)]
    return [[grouped[i][j] for j in perm] for i in perm]


def pfaffian_evaluator(matrix):
    """Independent exact principal-Pfaffian expansion used only for validation."""
    @lru_cache(None)
    def pf(indices):
        if len(indices) % 2:
            return 0
        if not indices:
            return 1
        a = indices[0]
        return sum(sgn(j+1)*matrix[a][indices[j]]*
                   pf(indices[1:j]+indices[j+1:]) for j in range(1,len(indices)))
    return pf


def principal_value(pf, word):
    return pf(tuple(i for i,bit in enumerate(word) if bit))


def xor_gate(graph, a, b):
    return graph.add(graph.add(a,b),
                     graph.mul(graph.constant(-2),graph.mul(a,b)))


def sign_product_gate(graph, a, b):
    return graph.sub(graph.constant(1),graph.mul(graph.constant(2),graph.mul(a,b)))


def compile_local_T():
    graph = DAG()
    p,x,y,q = [graph.variable(label) for label in ("p","x","y","q")]
    signs = [graph.add(graph.constant(1),graph.mul(graph.constant(-2),bit))
             for bit in (p,x,y,q)]
    delta = graph.mul(graph.constant(Fraction(1,2)),
                      graph.add(graph.constant(1),graph.product(signs)))
    value = graph.mul(graph.mul(delta,sign_product_gate(graph,x,y)),
                      sign_product_gate(graph,p,y))
    return graph,value


def compile_native_kernel(N):
    """O(N) scalar gates to evaluate ONE Boolean component, not a contraction."""
    graph = DAG()
    x = [graph.variable(f"x{i}") for i in range(N)]
    y = [graph.variable(f"y{i}") for i in range(N)]
    q = graph.variable("q")
    p = graph.constant(0)
    value = graph.constant(1)
    for i in range(N):
        value = graph.mul(value,graph.mul(sign_product_gate(graph,x[i],y[i]),
                                          sign_product_gate(graph,p,y[i])))
        p = xor_gate(graph,xor_gate(graph,p,x[i]),y[i])
    delta = graph.sub(graph.constant(1),xor_gate(graph,p,q))
    value = graph.mul(value,delta)
    return graph,value


def scalar_evaluate(graph, output, assignments):
    values = []
    for node in graph.nodes:
        if node["op"] == "constant":
            value = Fraction(node["value"])
        elif node["op"] == "variable":
            value = Fraction(assignments[node["name"]])
        else:
            a,b = values[node["left"]],values[node["right"]]
            value = a+b if node["op"] == "add" else a*b
        values.append(value)
    return values[output]


def paired_word(r):
    return tuple(bit for bit in r for _ in range(2))


def pair_cap(xF, xG):
    """Abstract C⊗C transform of paired copy, with final carries implicit."""
    assert len(xF) == len(xG) and len(xF) % 2 == 0
    m = len(xF)//2
    return (1 << m) if xF[1::2] == xG[1::2] else 0


def cap_order_O(m):
    return [name for e in range(m) for name in (("aF",e),("bF",e))]+[("qF",0)]+[
        name for e in range(m) for name in (("aG",e),("bG",e))]+[("qG",0)]


def cap_order_P(m):
    return [("aF",e) for e in range(m)]+[("qF",0)]+[
        ("aG",e) for e in range(m)]+[("qG",0)]+[
        name for e in range(m) for name in (("bF",e),("bG",e))]


def cap_shuffle_formula(u, v, s):
    k = sum(s)
    return (sum(s[e]*sum(u[f]+v[f] for f in range(e+1)) for e in range(len(s)))
            +k*(k+1)//2) % 2


def parity_cap(bits, q, t):
    return int((sum(bits)+q) % 2 == t)


def synchronized_cap(u, v, sF, sG, qF, qG):
    return int(sF == sG and qF == (sum(u)+sum(sF)) % 2 and
               qG == (sum(v)+sum(sG)) % 2)


def factor_cap(u, v, sF, sG, qF, qG):
    """Four Gaussian component FACTORS in order P, without an unproved shuffle."""
    equal = int(sF == sG)
    k = sum(sF)
    return sum(Fraction(1,2)*parity_cap(u,qF,t)*parity_cap(v,qG,t)*equal*
               (1+sgn(t+k)) for t in (0,1))


def measurements(n):
    N = 2*n*n
    graph,output = compile_native_kernel(N)
    return {"n":n,"ports_N":N,"coherent_skew_matrix_order":2*N+1,
            "skew_upper_entries":(2*N+1)*(2*N)//2,
            "local_chain_nodes":N,"internal_carry_edges":max(0,N-1),
            "scalar_component_nodes":len(graph.nodes),
            "scalar_component_binary_gates":graph.gates,"scalar_output":output,
            "constant_literals":sorted(str(q) for q in graph.constants),
            "scope":"one Boolean tensor component; no B-dependent target contraction",
            "root_target_compiled":False}

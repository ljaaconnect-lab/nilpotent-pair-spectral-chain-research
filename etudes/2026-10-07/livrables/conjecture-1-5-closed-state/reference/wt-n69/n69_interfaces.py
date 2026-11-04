"""Explicit n69 interfaces; no eligible polynomial root construction.

The joint-phase circuit has Boolean tensor-label inputs. The row-jet
reference is a complete exponential state. H-Pfaffian circuits only charge
normalization data, not the unconstructed Wick contraction.
"""
from __future__ import annotations

from candidate import DAG
from pfaffian_coefficients import trace_circuit


def H_matrix(n):
    if n < 1:
        raise ValueError("positive n")
    d = 2*n+2
    H = [[0]*d for _ in range(d)]

    def put(i,j,a):
        H[i][j],H[j][i] = a,-a

    for i in range(n):
        for j in range(i+1,n):
            put(i,j,1)
            put(n+i,n+j,-1)
        put(i,2*n,-1)
        put(n+i,2*n+1,-1)
    put(2*n,2*n+1,1)
    return H


def conditioned_matrix(n):
    A = [[0]*(2*n) for _ in range(2*n)]
    for i in range(2*n):
        for j in range(i+1,2*n):
            value = 1 if j < n else -1
            A[i][j],A[j][i] = value,-value
    return A


def xor_gate(g,a,b):
    return g.add(g.add(a,b),g.mul(g.constant(-2),g.mul(a,b)))


def sign_gate(g,a,b):
    return g.sub(g.constant(1),g.mul(g.constant(2),g.mul(a,b)))


def compile_joint_phase(m):
    """73m gates for the precise missing scalar BIT phase, no Gaussian lift."""
    if m < 1:
        raise ValueError("positive m")
    g = DAG()
    values = {label:[g.variable(f"{label}_{e}") for e in range(m)]
              for label in ("u","v","s","aF","bF","aG","bG")}
    zero,one = g.constant(0),g.constant(1)
    suffix = [zero]*m
    t = zero
    for e in reversed(range(m)):
        t = xor_gate(g,values["s"][e],t)
        suffix[e] = t
    pF,pG,pS = zero,zero,zero
    result = one
    for e in range(m):
        u,v,s,aF,bF,aG,bG = [values[label][e]
                              for label in ("u","v","s","aF","bF","aG","bG")]
        factors = [sign_gate(g,u,pF),sign_gate(g,u,suffix[e]),
                   sign_gate(g,v,pG),sign_gate(g,v,suffix[e]),
                   sign_gate(g,s,aF),sign_gate(g,s,aG),
                   sign_gate(g,s,pF),sign_gate(g,s,pG),sign_gate(g,s,pS),
                   g.sub(one,g.mul(g.constant(2),s))]
        result = g.mul(result,g.product(factors))
        pF = xor_gate(g,xor_gate(g,pF,aF),bF)
        pG = xor_gate(g,xor_gate(g,pG,aG),bG)
        pS = xor_gate(g,pS,s)
    return g,result


def compile_H_pf(n):
    """Lower the one fixed normalization Pfaffian through actual trace gates."""
    H = H_matrix(n)
    g,out = trace_circuit(len(H))
    for k,node in enumerate(g.nodes):
        if node["op"] == "variable":
            _,i,j = node["name"].split("_")
            g.nodes[k] = {"op":"constant","value":str(H[int(i)][int(j)])}
    return g,out


def compile_rowjet_reference(n, marked=False):
    """Complete 2^n-dimensional reference, not a polynomial closure claim.

Every node is a scalar + or * gate; no Pfaffian, exterior multiplication,
derivative, coefficient, or Wick functional is a gate in this circuit.
For marked=True, p_i_j are prescribed numeric marked leaves after A is
supplied; they are not arbitrary short rational constants.
"""
    if n < 1:
        raise ValueError("positive n")
    g = DAG()
    if marked:
        z = g.variable("z")
        markers = [z]
        for _ in range(1,n*n):
            markers.append(g.mul(markers[-1],markers[-1]))
        B = [[g.mul(g.variable(f"p_{i}_{j}"),markers[i*n+j])
              for j in range(n)] for i in range(n)]
    else:
        B = [[g.variable(f"b_{i}_{j}") for j in range(n)] for i in range(n)]
    zero,one,minus = g.constant(0),g.constant(1),g.constant(-1)
    jets = [one]+[zero]*((1 << n)-1)
    for i in range(n):
        advanced = []
        for S in range(1 << n):
            terms = []
            for j in range(n):
                bit = 1 << j
                if S & bit:
                    term = g.mul(minus,g.mul(B[i][j],g.add(jets[S^bit],jets[S])))
                else:
                    term = g.mul(B[i][j],g.add(jets[S],jets[S|bit]))
                terms.append(term)
            advanced.append(g.sum(terms))
        jets = advanced
    return g,jets[0]


def reference_gate_formula(n,marked=False):
    return n*(7*n-2)*(1 << (n-1))+((2*n*n-1) if marked else 0)

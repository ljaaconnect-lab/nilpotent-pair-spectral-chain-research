"""Symbolic, occupation-by-occupation proof checks of the loopless degree-six rule.

Here a_ij is b_ij*b_ji, d_ijk is the sum of the two oriented triangle
weights, and e is the sum of the six oriented four-cycle weights.
Only this symbolic verifier requires SymPy; the candidate uses stdlib only.
"""
from itertools import combinations
import json
import sympy as sp


def multiply(p,q,bound):
    result={}
    for u,a in p.items():
        for v,b in q.items():
            w=tuple(x+y for x,y in zip(u,v))
            if all(x<=y for x,y in zip(w,bound)):
                result[w]=result.get(w,0)+a*b
    return {u:sp.expand(v) for u,v in result.items() if v!=0}


def power(p,r,bound):
    zero=(0,)*len(bound); result={zero:sp.Integer(1)}
    for _ in range(r): result=multiply(result,p,bound)
    return result


def inverse(p,bound):
    zero=(0,)*len(bound)
    assert p[zero]==1
    remainder={u:-v for u,v in p.items() if u!=zero}
    result={zero:sp.Integer(1)}; term=result
    for _ in range(sum(bound)//2):
        term=multiply(term,remainder,bound)
        for u,v in term.items(): result[u]=result.get(u,0)+v
    return result


def determinant_polynomial(n,omit=None):
    zero=(0,)*n; result={zero:sp.Integer(1)}
    vertices=[i for i in range(n) if i!=omit]
    def monomial(indices): return tuple(int(i in indices) for i in range(n))
    for i,j in combinations(vertices,2): result[monomial((i,j))]=-sp.Symbol(f'a{i}{j}')
    for i,j,k in combinations(vertices,3): result[monomial((i,j,k))]=-sp.Symbol(f'd{i}{j}{k}')
    if len(vertices)==4:
        a=lambda i,j:sp.Symbol(f'a{i}{j}')
        result[(1,1,1,1)]=a(0,1)*a(2,3)+a(0,2)*a(1,3)+a(0,3)*a(1,2)-sp.Symbol('e')
    return result


def residue(occupation):
    n=len(occupation)
    result=power(determinant_polynomial(n),sum(occupation)-n-1,occupation)
    for i,m in enumerate(occupation):
        if m>1:
            result=multiply(result,power(inverse(determinant_polynomial(n,i),occupation),m-1,occupation),occupation)
    return sp.expand(result.get(tuple(occupation),0))


def main():
    a01,a02,a12,a03,a13=sp.symbols('a01 a02 a12 a03 a13')
    d012=sp.Symbol('d012')
    cases=[((3,3),-a01**3),((4,2),0),
           ((3,2,1),a01**2*a02),
           ((2,2,2),d012**2+a01*a02*a12),
           ((2,2,1,1),-a01*(a02*a13+a03*a12))]
    results=[]
    for m,expected in cases:
        observed=residue(m)
        assert sp.expand(observed-expected)==0,(m,observed,expected)
        results.append({'occupation':m,'coefficient':str(observed)})
    print(json.dumps({'symbolic_degree_six_cases':results,'all_exact':True},indent=2))


if __name__=='__main__': main()

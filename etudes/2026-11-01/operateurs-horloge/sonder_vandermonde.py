"""Noncommutative root interpolation, one formal perturbation parameter."""
from collections import defaultdict
from math import comb,factorial
from itertools import product
from itertools import permutations
import json

Q=241
def primitive():
    return next(g for g in range(2,Q) if all(pow(g,(Q-1)//p,Q)!=1 for p in [2,3,5]))
def add(*ps):
    out=defaultdict(int)
    for p in ps:
        for w,c in p.items():out[w]=(out[w]+c)%Q
    return {w:c for w,c in out.items() if c}
def scale(p,a):return {w:c*a%Q for w,c in p.items() if c*a%Q}
def rightpower(p,j,s):return {w+(j,)*s:c for w,c in p.items()}

def interpolate(n,permutation=None):
    if (Q-1)%n:raise ValueError(n)
    w=pow(primitive(),(Q-1)//n,Q)
    roots=[pow(w,j,Q) for j in (range(n) if permutation is None else permutation)]
    # C[k][r]: coefficient epsilon^r of the kth coefficient of the monic
    # degree-n matrix polynomial with right roots lambda_j I+epsilon X_j.
    c=[[{} for _ in range(n+1)] for _ in range(n)]
    for r in range(n+1):
        rhs=[]
        for j,lam in enumerate(roots):
            h={(j,)*r:-comb(n,r)*pow(lam,n-r,Q)%Q}
            for k in range(n):
                for s in range(1,min(k,r)+1):
                    h=add(h,scale(rightpower(c[k][r-s],j,s),-comb(k,s)*pow(lam,k-s,Q)))
            rhs.append(h)
        for k in range(n):
            c[k][r]=scale(add(*(scale(rhs[j],pow(roots[j],(-k)%n,Q)) for j in range(n))),pow(n,-1,Q))
    return c[0][n]

def cyclic_reduce(p):
    out=defaultdict(int)
    for w,c in p.items():
        key=min(w[i:]+w[:i] for i in range(len(w)))
        out[key]=(out[key]+c)%Q
    return {w:c for w,c in out.items() if c}

def average_roots(n):
    total={}
    for tail in permutations(range(1,n)):
        total=add(total,interpolate(n,(0,)+tail))
    return scale(total,pow(factorial(n-1),-1,Q))

if __name__=='__main__':
    for n in range(1,7):
        p=interpolate(n)
        expected=(-1)**n*pow(factorial(n),-1,Q)%Q
        wrong=[(w,c) for w,c in p.items() if len(set(w))<n or c!=expected]
        allgood=sum(p.get(w,0)==expected for w in product(range(n),repeat=n) if len(set(w))==n)
        print(json.dumps({'n':n,'terms':len(p),'target_coefficient':expected,'correct_permutations':allgood,'wrong_terms':len(wrong),'examples':wrong[:4]}),flush=True)
    for n in [3,4,5]:
        p=average_roots(n)
        c=(-1)**n*pow(factorial(n),-1,Q)%Q
        target={w:c for w in product(range(n),repeat=n) if len(set(w))==n}
        defect=add(p,scale(target,-1))
        print(json.dumps({'root_average_n':n,'wrong_words':len(defect),
                          'wrong_cyclic_classes':len(cyclic_reduce(defect))}),flush=True)

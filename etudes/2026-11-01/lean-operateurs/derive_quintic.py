"""Derive the fifth-order counterterm in a column-independent partition basis.

Each partition denotes an unrestricted matrix contraction: repeated blocks
share one column, singleton blocks are replaced by P=sum A_j. At degree
five at most two blocks repeat, so evaluation uses at most double sums.
"""
from collections import defaultdict,Counter
from fractions import Fraction as F
from math import factorial,comb,prod,lcm
from pathlib import Path
import json

def canonical(word):
    seen={}
    return tuple(seen.setdefault(x,len(seen)) for x in word)

def add(*polys):
    out=defaultdict(F)
    for p in polys:
        for w,c in p.items():out[w]+=c
    return {w:c for w,c in out.items() if c}

def scale(p,c):return {w:v*c for w,v in p.items() if v*c}

def multiply(p,q):
    out=defaultdict(F)
    for u,a in p.items():
        offset=max(u,default=-1)+1
        for v,b in q.items():out[canonical(u+tuple(x+offset for x in v))]+=a*b
    return {w:c for w,c in out.items() if c}

def moment(k,p):
    """Sum_j (left A_j + right A_j)^k, without factors 1/2."""
    out=defaultdict(F)
    for w,c in p.items():
        fresh=max(w,default=-1)+1
        for left in range(k+1):
            key=canonical((fresh,)*left+w+(fresh,)*(k-left))
            out[key]+=comb(k,left)*c
    return {w:c for w,c in out.items() if c}

def partitions(r):
    def visit(w):
        if len(w)==r:yield w;return
        for j in range(max(w,default=-1)+2):yield from visit(w+(j,))
    return list(visit(()))

def exact_numerator(r):
    return {w:F((2**r)*prod((-1)**(s-1)*factorial(s-1) for s in Counter(w).values()))
            for w in partitions(r)}

def derive(max_order=5):
    h=[{():F(1)}]
    counterterms={}
    for r in range(1,max_order+1):
        rhs=add(*(scale(moment(k,h[r-k]),(-1)**(k-1)*factorial(r-1)//factorial(r-k))
                  for k in range(1,r+1)))
        for order,c in counterterms.items():
            factor=F(2**(order-1)*factorial(r-1),factorial(r-order))
            # c is the actual ODE counterterm R_order in partition coordinates.
            rhs=add(rhs,scale(add(multiply(c,h[r-order]),multiply(h[r-order],c)),factor))
        target=exact_numerator(r)
        delta=add(target,scale(rhs,-1))
        if delta:
            denom=2**r*factorial(r-1)
            counterterms[r]=scale(delta,F(1,denom))
        h.append(target)
    return h,counterterms

def main():
    _,c=derive(5)
    result={'date':'2026-11-01','basis':'unrestricted equality-partition contractions',
            'orders':{}}
    for r,p in c.items():
        denominator=lcm(*(v.denominator for v in p.values()))
        ints=scale(p,denominator)
        assert all(v.denominator==1 for v in ints.values())
        max_repeats=max(sum(v>=2 for v in Counter(w).values()) for w in ints)
        result['orders'][r]={'denominator':denominator,'terms':[
            {'pattern':list(w),'coefficient':int(v)} for w,v in sorted(ints.items())],
            'nonzero_patterns':len(ints),'max_repeated_blocks':max_repeats}
    here=Path(__file__).resolve().parent
    (here/'correcteurs.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({r:{k:v for k,v in d.items() if k!='terms'} for r,d in result['orders'].items()},indent=2))

if __name__=='__main__':main()

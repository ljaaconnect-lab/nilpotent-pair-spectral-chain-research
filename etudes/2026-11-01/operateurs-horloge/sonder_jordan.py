from collections import defaultdict
from fractions import Fraction as F
from itertools import product
import json

def add(*ps):
    out=defaultdict(F)
    for p in ps:
        for w,c in p.items():out[w]+=c
    return {w:c for w,c in out.items() if c}
def scale(p,c):return {w:v*c for w,v in p.items() if v*c}
def mul(p,q):
    out=defaultdict(F)
    for u,a in p.items():
        for v,b in q.items():out[u+v]+=a*b
    return {w:c for w,c in out.items() if c}
def jordan(j,p):return add(scale(mul({(j,):F(1)},p),F(1,2)),scale(mul(p,{(j,):F(1)}),F(1,2)))
def comm(p,q):return add(mul(p,q),scale(mul(q,p),-1))
def correction4(q):
    xs=[{(j,):F(1)} for j in range(q)]
    p=add(*xs)
    p2=add(*(mul(x,x) for x in xs))
    t1=add(*(comm(x,comm(x,add(mul(p,p),scale(add(mul(x,p),mul(p,x),p2),-1)))) for x in xs))
    t2=add(add(*(mul(comm(x,p),comm(x,p)) for x in xs)),scale(add(*(mul(comm(x,y),comm(x,y)) for x in xs for y in xs)),-1))
    t3=add(*(add(mul(mul(x,mul(add(p,scale(x,-1)),add(p,scale(x,-1)))),x),scale(mul(mul(add(p,scale(x,-1)),mul(x,x)),add(p,scale(x,-1))),-1)) for x in xs))
    return scale(add(t1,scale(t2,-2),scale(t3,2)),F(1,24))
def expected(q,r):
    from math import factorial
    return {w:F(1,factorial(r)) for w in product(range(q),repeat=r) if len(set(w))==r}
def recurrence(q,order):
    u=[{():F(1)}]
    w=[{():F(1)} for _ in range(q)]
    for r in range(1,order+1):
        v=scale(add(*(jordan(j,w[j]) for j in range(q))),F(1,r))
        u.append(v)
        w=[add(v,scale(jordan(j,w[j]),-1)) for j in range(q)]
    return u
if __name__=='__main__':
    u=recurrence(4,5)
    for r,p in enumerate(u):
        defect=add(p,scale(expected(4,r),-1))
        groups=defaultdict(list)
        for w,c in defect.items():
            key=tuple(sorted((w.count(j) for j in set(w)),reverse=True))
            groups[key].append((''.join(map(str,w)),str(c)))
        print(json.dumps({'degree':r,'nonzero_words':len(defect),'patterns':{str(k):v[:8] for k,v in groups.items()}}))

"""Exact checks of the constructive regular-completion identities."""
from fractions import Fraction as F
from itertools import combinations,permutations,product
from math import factorial
import json
import random
from gaussian_experiments import pf
from gaussian_polarization import build,gate_bound
from dag import DAG


def repeated_kernel(a,b,c,k):
    n=len(a)
    r=[F(x,y) for x,y in zip(b,a)]
    s=[F(x,y) for x,y in zip(c,a)]
    out=[[F(0)]*(2*n) for _ in range(2*n)]
    for j in range(n):
        for l in range(j+1,n):
            xx=a[j]*a[l]*(r[l]-r[j])
            yy=F(factorial(k-2),k)*(s[l]-s[j])
            out[2*j][2*l],out[2*l][2*j]=xx,-xx
            out[2*j+1][2*l+1],out[2*l+1][2*j+1]=yy,-yy
        for l in range(n):
            xy=a[j]*(F(j==l)-F(1,k)+factorial(k-1)*r[j]*s[l])
            out[2*j][2*l+1],out[2*l+1][2*j]=xy,-xy
    return out


def main():
    rng=random.Random(2026102443)
    checks=0
    for k,n in [(3,5),(4,7),(5,6),(6,6)]:
        a=[rng.randrange(1,6) for _ in range(n)]
        b,c=[[rng.randrange(-3,4) for _ in range(n)] for _ in range(2)]
        matrix=repeated_kernel(a,b,c,k)
        rows=[a]*(k-2)+[b,c]
        for subset in combinations(range(n),k):
            inds=[mode for j in subset for mode in (2*j,2*j+1)]
            actual=pf([[matrix[i][j] for j in inds] for i in inds])
            target=sum(__import__('math').prod(rows[i][j] for i,j in enumerate(p))
                       for p in permutations(subset))
            assert actual==target
            checks+=1
    weights=[]
    for m in range(1,8):
        base_values=[sum(sign*(1<<i) for i,sign in enumerate(signs+(1,)))
                     for signs in product((-1,1),repeat=m-1)]
        assert len(base_values)==1<<(m-1)
        assert min(base_values)==1 and max(base_values)==(1<<m)-1
        assert all(v%2==1 for v in base_values)
        weights.append({'m':m,'components':1<<(m-1),'minimum_base':min(base_values),
                        'maximum_base':max(base_values)})
    counts={}
    for n in range(1,11):
        dag=DAG()
        outputs=build(n,list(range(n)),dag)
        assert dag.gates==gate_bound(n)
        counts[n]=dag.gates
    alpha=F(24,73)
    c=F(23,4)
    third_prediction=6*alpha-(2+5*c)*alpha**3
    assert 1-third_prediction==F(46729,389017)
    print(json.dumps({'paired_pfaffian_identity_checks':checks,
                      'polarization_base_values':weights,'exact_gate_counts':counts,
                      'chosen_two_jet_third_order_contrast':str(1-third_prediction),
                      'contrast_refutes_only_this_chosen_jet':True},indent=2))


if __name__=='__main__':
    main()

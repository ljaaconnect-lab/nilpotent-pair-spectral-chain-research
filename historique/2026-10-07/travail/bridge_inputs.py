"""Development consistency checks for Hilbert decomposition; not a formal proof."""
import itertools, json
import sympy as sp
from pathlib import Path
alpha,beta,t=sp.symbols('alpha beta t')
h=sp.expand((alpha*t**2-beta*t)*(t-t**2))
checks={'n2_central_pairing':sp.expand(h).coeff(t,3)==alpha+beta}
labels=[]
for n in (2,3,4):
    assignments=list(itertools.product(range(n),repeat=n))
    rho=[sum(s[i]*n**i for i in range(n)) for s in assignments]
    checks[f'base_{n}_injective_finite']=len(set(rho))==n**n
    perms=list(itertools.permutations(range(n)))
    K=n**n-1
    bad=sum((K+sum(s[i]*n**i for i in range(n))-sum(v[i]*n**i for i in range(n))==K)!=(s==v) for s in perms for v in perms)
    checks[f'n{n}_diagonal_pair_filter']=bad==0
    labels.append({'n':n,'K':K,'assignment_count':len(assignments),'permutation_pairs':len(perms)**2,'bad_pairs':bad})
assert all(checks.values())
report={'scope':'Finite exact development checks only; all general statements remain unverified by Lean.',
        'checks':checks,'passed':sum(checks.values()),'total':len(checks),'labels':labels,'n2_H':str(h)}
Path(__file__).with_name('bridge-inputs.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

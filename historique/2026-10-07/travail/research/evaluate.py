"""Frozen independent exact-arithmetic evaluator v1. Never modify during search."""
import argparse
import hashlib
import importlib.util
import itertools
import json
from fractions import Fraction
from pathlib import Path

def sign(s):
    return (-1) ** sum(s[i] > s[j] for i in range(len(s)) for j in range(i+1,len(s)))

def reference(A):
    n=len(A); K=n**n-1
    perms=list(itertools.permutations(range(n)))
    labels={s:sum(s[i]*n**i for i in range(n)) for s in perms}
    full={(0,0):Fraction(1),(2*K,0):Fraction(1)}
    central={}
    for s in perms:
        amp=Fraction(1)
        for i in range(n): amp *= 1+Fraction(A[i][s[i]])**2
        addr=sum(2**(i*n+s[i]) for i in range(n))
        central[addr]=amp
        for v in perms:
            key=(K+labels[s]-labels[v],addr)
            full[key]=full.get(key,Fraction(0))+sign(s)*sign(v)*amp
    full={k:v for k,v in full.items() if v}
    return central,full

def dev_cases():
    cases=[]
    for n in (2,3,4):
        cases += [(f'n{n}-identity',[[int(i==j) for j in range(n)] for i in range(n)]),
                  (f'n{n}-cyclic',[[int(j==(i+1)%n) for j in range(n)] for i in range(n)]),
                  (f'n{n}-vandermonde',[[(i+1)**j for j in range(n)] for i in range(n)])]
    return cases

def main():
    p=argparse.ArgumentParser(); p.add_argument('--split',choices=['dev','test'],required=True)
    p.add_argument('--cases'); p.add_argument('--output'); args=p.parse_args()
    if args.split=='test':
        if not args.cases: p.error('test requires coordinator case file')
        raw=json.loads(Path(args.cases).read_text()); cases=[(x['name'],[[Fraction(v) for v in row] for row in x['A']]) for x in raw]
    else: cases=dev_cases()
    import candidate
    results=[]; passed=0; total=0
    for name,A in cases:
        n=len(A); central,full=reference(A)
        try:
            got=candidate.simulate(A)
            checks={'central_exact':got['central']==central,'full_exact':got['hhat']==full,
                    'index_exact':got['K']==n**n-1,'gate_bound':0<got['gates']<=4*n**4}
            row={'case':name,'n':n,'checks':checks,'gates':got['gates'],'K':got['K'],'hhat_terms':len(got['hhat'])}
        except Exception as e:
            checks={k:False for k in ['central_exact','full_exact','index_exact','gate_bound']}
            row={'case':name,'n':n,'checks':checks,'error':str(e)}
        passed += sum(checks.values()); total += len(checks); results.append(row)
    report={'protocol':'simulation-v1','split':args.split,'score':passed/total,'passed':passed,'total':total,
            'evaluator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':results,
            'scope':'Finite exact checks; no proof of asymptotic circuit complexity.'}
    if args.output: Path(args.output).write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()

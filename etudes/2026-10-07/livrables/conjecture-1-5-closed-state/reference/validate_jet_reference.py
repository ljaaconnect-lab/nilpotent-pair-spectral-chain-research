"""Frozen positive development validation of an explicitly exponential reference."""
import hashlib
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parent
WT=ROOT/'wt-n69'
FREEZE=ROOT/'n69-reference-validation-freeze.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

if sys.argv[1:] == ['--freeze']:
    record={'mode':'Positive reference-only B_dev; original node metric unchanged',
            'ns':[2,3,4,5],'matrices':['identity','vandermonde','cyclic'],
            'z_values':[-1,0,1],'root_credit':False,'B_test_opened':False,
            'code_sha256':sha(Path(__file__)),
            'dags':{name:sha(WT/name) for n in [2,3,4,5] for name in [
                    f'n69-rowjet_generic_reference-n{n}.json',f'n69-rowjet_marked_reference-n{n}.json']}}
    FREEZE.write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps({'frozen':True,'sha256':sha(FREEZE)}));raise SystemExit(0)

frozen=json.loads(FREEZE.read_text(encoding='utf-8'))
assert sha(Path(__file__))==frozen['code_sha256']
for name,digest in frozen['dags'].items(): assert sha(WT/name)==digest

def evaluate(dag,inputs):
    values=[];gates=0
    for k,node in enumerate(dag['nodes']):
        op=node['op']
        if op=='constant': value=Fraction(node['value'])
        elif op=='variable': value=Fraction(inputs[node['name']])
        else:
            assert op in ['add','mul']
            assert 0<=node['left']<k and 0<=node['right']<k
            a,b=values[node['left']],values[node['right']]
            value=a+b if op=='add' else a*b;gates+=1
        values.append(value)
    assert gates==dag['gates']
    return values[dag['output']]

results=[]
for n in frozen['ns']:
    generic=json.loads((WT/f'n69-rowjet_generic_reference-n{n}.json').read_text(encoding='utf-8'))
    marked=json.loads((WT/f'n69-rowjet_marked_reference-n{n}.json').read_text(encoding='utf-8'))
    assert generic['gates']==n*(7*n-2)*2**(n-1)
    assert marked['gates']==generic['gates']+2*n*n-1
    for family in frozen['matrices']:
        A=[[int(i==j) if family=='identity' else
            (i+1)**j if family=='vandermonde' else int(j==(i+1)%n)
            for j in range(n)] for i in range(n)]
        p=[[1+x*x for x in row] for row in A]
        for z in frozen['z_values']:
            B=[[p[i][j]*z**(2**(i*n+j)) for j in range(n)] for i in range(n)]
            expected=sum(__import__('math').prod(B[i][s[i]] for i in range(n))
                         for s in itertools.permutations(range(n)))
            g=evaluate(generic,{f'b_{i}_{j}':B[i][j] for i in range(n) for j in range(n)})
            m=evaluate(marked,{'z':z,**{f'p_{i}_{j}':p[i][j] for i in range(n) for j in range(n)}})
            results.append({'n':n,'family':family,'z':z,'generic_ok':g==expected,
                            'marked_ok':m==expected,'outputs_agree':g==m,
                            'generic_gates':generic['gates'],'marked_gates':marked['gates']})
report={'scope':'Exponentially sized row-jet scalar reference; development only',
        'freeze_sha256':sha(FREEZE),'cases':len(results),
        'positive_checks_passed':sum(r[k] for r in results for k in ['generic_ok','marked_ok','outputs_agree']),
        'positive_checks_total':3*len(results),'results':results,
        'all_gate_counts_checked':True,'root_conjecture_verified':False,'B_test_opened':False}
(ROOT/'n69-reference-validation-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['cases','positive_checks_passed','positive_checks_total','all_gate_counts_checked','root_conjecture_verified']}))
raise SystemExit(0 if report['positive_checks_passed']==report['positive_checks_total'] else 1)

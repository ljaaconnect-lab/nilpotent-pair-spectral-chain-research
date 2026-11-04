"""Verify the new operator ansatz, including its explicit failure at size 5."""
from itertools import permutations
from math import factorial,prod
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,json,random,sys

from circuit import build
from sonder_jordan import F,add,scale,mul,jordan,expected,correction4,recurrence


def repaired(q,order):
    u=[{():F(1)}]
    w=[{():F(1)} for _ in range(q)]
    r4=correction4(q)
    for r in range(1,order+1):
        rhs=add(*(jordan(j,w[j]) for j in range(q)))
        if r>=4:rhs=add(rhs,scale(add(mul(r4,u[r-4]),mul(u[r-4],r4)),F(1,2)))
        ur=scale(rhs,F(1,r))
        u.append(ur)
        w=[add(ur,scale(jordan(j,wj),-1)) for j,wj in enumerate(w)]
    return u


def formal_target(p,labels,q):
    n=len(p);N=1<<n.bit_length()
    result=[{} for _ in range(N)]
    target=result[sum(labels)%N]
    for s in permutations(range(n)):
        e=sum(1<<(i*n+j) for i,j in enumerate(s))
        c=prod(p[i][j] for i,j in enumerate(s))%q
        target[e]=(target.get(e,0)+c)%q
    return [{e:c for e,c in out.items() if c} for out in result]


def run(write_report):
    word_checks=0
    for colors in range(1,5):
        uncorrected=recurrence(colors,4)
        r4=correction4(colors)
        assert r4==scale(add(expected(colors,4),scale(uncorrected[4],-1)),4)
        u=repaired(colors,4)
        for r in range(5):
            assert u[r]==expected(colors,r)
            word_checks+=colors**r
    two=recurrence(2,10)
    assert not any(two[r] for r in range(3,11))
    five=repaired(5,5)
    # A repeated column whose label sum agrees exactly with the valid sum.
    bad=[]
    for w,c in five[5].items():
        if len(set(w))<5 and sum(w)==10 and c:
            bad.append((w,c))
    assert bad
    bad_word,bad_coefficient=bad[0]

    rng=random.Random(2026110102)
    q=998244353
    scalar_tables=formal_tables=0
    costs=[]
    for n in range(1,5):
        labels=list(range(n))
        dag,outs,meta=build(n,labels,q,3,True,True)
        costs.append(meta)
        for case in range(10):
            raw=[[rng.randrange(-4,5) for _ in range(n)] for _ in range(n)]
            p=[[1+x*x for x in row] for row in raw]
            data={('a',i,j):raw[i][j] for i in range(n) for j in range(n)}
            data['z']=rng.randrange(0,12)
            target=formal_target(p,labels,q)
            numeric=[sum(c*pow(data['z'],e,q) for e,c in t.items())%q for t in target]
            assert dag.evaluate_all(outs,data,q)==numeric
            scalar_tables+=1
            if case==0:
                assert dag.evaluate_polynomials(outs,data,q)==target
                formal_tables+=1
        assert all(arg=='z' or (isinstance(arg,tuple) and arg[0]=='a')
                   for op,*args in dag.nodes if op=='input' for arg in args)

    # Frozen legal input exhibiting wrong amplitude as well as slot leakage.
    p=[[17,2,10,10,10],[2,17,2,17,2],[10,10,5,2,2],[5,10,2,5,2],[17,10,17,10,5]]
    labels=list(range(5))
    dag,outs,meta=build(5,labels,q,3,True,False)
    data={('p',i,j):p[i][j] for i in range(5) for j in range(5)};data['z']=2
    got=dag.evaluate_all(outs,data,q)
    expected_table=[sum(c*pow(2,e,q) for e,c in t.items())%q for t in formal_target(p,labels,q)]
    assert got!=expected_table and got[2]!=expected_table[2]
    report={'date':'2026-11-01','status':'general_candidate_rejected',
            'construction':'clock + Jordan resolvents + quartic commutator correction',
            'ordinary_scalar_gate_bound':'O(N n^2 (n+1)^3), N<2n+1',
            'general_polynomial_solution':False,
            'free_word_coefficients_checked':word_checks,
            'exact_through_order':4,'numeric_tables_correct':scalar_tables,'formal_tables_correct':formal_tables,
            'scalar_costs':costs,
            'formal_counterexample':{'word':bad_word,'candidate_coefficient_after_factorial':str(factorial(5)*bad_coefficient),
                                     'required_coefficient':0,'label_sum':sum(bad_word),'correct_label_sum':10},
            'numeric_counterexample':{'n':5,'Q':q,'z':2,'p':p,'labels':labels,'got':got,'expected':expected_table,**meta}}
    here=Path(__file__).resolve().parent
    report['code_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [here/'circuit.py',here/'verifier.py',here/'sonder_jordan.py']}
    if write_report:(here/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report',action='store_true')
    run(parser.parse_args().write_report)

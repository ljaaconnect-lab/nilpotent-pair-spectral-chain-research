"""Exact full-polynomial validation of a frozen direct scalar DAG; no extraction."""
import argparse, hashlib, importlib.util, itertools, json
from fractions import Fraction
from pathlib import Path

def add(a,b):
    result=dict(a)
    for degree,coefficient in b.items():result[degree]=result.get(degree,Fraction(0))+coefficient
    return {k:v for k,v in result.items() if v}
def mul(a,b):
    result={}
    for i,x in a.items():
        for j,y in b.items():result[i+j]=result.get(i+j,Fraction(0))+x*y
    return {k:v for k,v in result.items() if v}
def evaluate(circuit,A):
    values=[]
    for index,node in enumerate(circuit['nodes']):
        op=node['op']
        if op=='constant':
            value=Fraction(node['value']);poly={0:value} if value else {}
        elif op=='variable':
            if node['name']=='z':poly={1:Fraction(1)}
            else:
                i,j=map(int,node['name'].removeprefix('p_').split('_'))
                poly={0:1+A[i][j]**2}
        else:
            assert op in ('add','mul')
            left,right=node['left'],node['right']
            assert 0<=left<index and 0<=right<index
            poly=(add if op=='add' else mul)(values[left],values[right])
        values.append(poly)
    return values[circuit['output']]
def reference(A):
    n=len(A);result={}
    for permutation in itertools.permutations(range(n)):
        degree=sum(2**(i*n+permutation[i]) for i in range(n))
        coefficient=Fraction(1)
        for i,j in enumerate(permutation):coefficient*=1+A[i][j]**2
        result[degree]=result.get(degree,Fraction(0))+coefficient
    return result
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--out-dir',type=Path,required=True)
    args=parser.parse_args();source=args.source.resolve();args.out_dir.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    freeze={'source':source.name,'source_sha256':digest,'n':[2,3,4,5],
            'A':'A_ij=(i+2)/(j+3)','validation':'Complete exact polynomial in formal z',
            'new_lean_invocations':0,'root_heldout_boundary_opened':False}
    (args.out_dir/'direct-polynomial-validation-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
    spec=importlib.util.spec_from_file_location('frozen_direct_circuit',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    cases=[]
    for n in freeze['n']:
        A=[[Fraction(i+2,j+3) for j in range(n)] for i in range(n)]
        circuit=module.build_corrected(n)
        actual=evaluate(circuit,A);expected=reference(A)
        gates=sum(node['op'] in ('add','mul') for node in circuit['nodes'])
        passed=actual==expected and gates==(n-1)*2**n+2*n*n
        cases.append({'n':n,'passed':passed,'gates':gates,'complete_output_monomials':len(actual)})
    report={'source_sha256':digest,'cases':cases,'passed':sum(c['passed'] for c in cases),
            'checks':len(cases),'root_conjecture_verified':False,
            'scope':'Full symbolic target validation for four explicit matrices; no all-n polynomial-size conclusion'}
    (args.out_dir/'direct-polynomial-validation-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2));assert report['passed']==report['checks']
if __name__=='__main__':main()

"""Explicit +/* DAG for one first- or second-prefix response, not all prefixes."""
from fractions import Fraction
import hashlib, json
from pathlib import Path

class DAG:
    def __init__(self): self.nodes=[]; self.literals={}; self.inputs={}
    def emit(self,node): self.nodes.append(node); return len(self.nodes)-1
    def const(self,value):
        key=str(value)
        if key not in self.literals: self.literals[key]=self.emit({'op':'constant','value':key})
        return self.literals[key]
    def variable(self,name):
        if name not in self.inputs: self.inputs[name]=self.emit({'op':'variable','name':name})
        return self.inputs[name]
    def add(self,a,b): return self.emit({'op':'add','left':a,'right':b})
    def mul(self,a,b): return self.emit({'op':'mul','left':a,'right':b})
    def sub(self,a,b): return self.add(a,self.mul(self.const(-1),b))
    def sum(self,terms):
        terms=list(terms)
        if not terms:return self.const(0)
        out=terms[0]
        for term in terms[1:]:out=self.add(out,term)
        return out
    @property
    def gates(self):return sum(node['op'] in ('add','mul') for node in self.nodes)
    def evaluate(self,values,output):
        table=[]
        for i,node in enumerate(self.nodes):
            op=node['op']
            if op=='constant':value=Fraction(node['value'])
            elif op=='variable':value=Fraction(values[node['name']])
            else:
                assert 0<=node['left']<i and 0<=node['right']<i
                a,b=table[node['left']],table[node['right']]
                value=a+b if op=='add' else a*b
            table.append(value)
        return table[output]

def compile_response(n,J,depth=2,marked=False):
    assert n>=2 and depth in (1,2)
    J=sorted(set(J));assert all(0<=j<n for j in J)
    d=DAG();rows=[]
    if marked:
        powers=[d.variable('z')]
        for _ in range(depth*n-1):powers.append(d.mul(powers[-1],powers[-1]))
        for i in range(depth):
            rows.append([d.mul(d.variable(f'p_{i}_{j}'),powers[i*n+j]) for j in range(n)])
    else:
        for i in range(depth):rows.append([d.variable(f'b_{i}_{j}') for j in range(n)])
    if depth==1:
        b=rows[0];hb=d.sum(b);initialization=d.gates
        out=hb if not J else d.sub(hb,d.sum(b[j] for j in J))
    else:
        b,c=rows;bc=[d.mul(x,y) for x,y in zip(b,c)]
        totals=[d.sum(v) for v in (b,c,bc)];initialization=d.gates
        complements=totals if not J else [d.sub(h,d.sum(v[j] for j in J))
                                         for h,v in zip(totals,(b,c,bc))]
        out=d.sub(d.mul(complements[0],complements[1]),complements[2])
    if len(J)%2:out=d.mul(d.const(-1),out)
    expected_init=(n-1 if depth==1 else 4*n-3)+(2*depth*n-1 if marked else 0)
    expected_query=(0 if not J else len(J)+1)+(len(J)%2) if depth==1 else \
                   (3 if not J else 3*len(J)+6+(len(J)%2))
    assert initialization==expected_init
    assert d.gates-initialization==expected_query
    return {'n':n,'J':J,'depth':depth,'marked':marked,'nodes':d.nodes,'output':out,
            'initialization_gates':initialization,'query_gates':expected_query,'gates':d.gates,
            'scope':'One explicit subset query at fixed prefix depth; not a full extractor',
            'root_conjecture_verified':False}

def direct_response(rows,J):
    n=len(rows[0]);H=[j for j in range(n) if j not in J]
    if len(rows)==1:mass=sum(rows[0][j] for j in H)
    else:mass=sum(rows[0][j]*rows[1][k] for j in H for k in H if j!=k)
    return (-1)**len(J)*mass

def run():
    root=Path(__file__).resolve().parent
    source=root/'atomic_prefix_circuit.py';freeze=root/'atomic-prefix-circuit-freeze.json'
    freeze.write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'n':[2,3,4,5],'A':['identity','Vandermonde','cycle'],'z':[-1,0,1],
        'J':'All subsets, explicit finite queries','depth':[1,2],
        'purpose':'Positive development validation of initialized local constructions',
        'heldout_root_boundary_opened':False},indent=2),encoding='utf-8')
    failures=[];checks=0;counts=[]
    for n in range(2,6):
        for depth in (1,2):
            for kind in ('identity','Vandermonde','cycle'):
                A=[[int(i==j) if kind=='identity' else (i+1)**j if kind=='Vandermonde'
                    else int(j==(i+1)%n) for j in range(n)] for i in range(n)]
                for z in (-1,0,1):
                    rows=[[(1+A[i][j]**2)*Fraction(z)**(2**(i*n+j)) for j in range(n)]
                          for i in range(depth)]
                    for mask in range(2**n):
                        J=[j for j in range(n) if mask&(1<<j)]
                        for marked in (False,True):
                            artifact=compile_response(n,J,depth,marked)
                            dag=DAG();dag.nodes=artifact['nodes']
                            inputs={'z':z} if marked else {}
                            inputs.update({(f'p_{i}_{j}' if marked else f'b_{i}_{j}'):
                                           (1+A[i][j]**2 if marked else rows[i][j])
                                           for i in range(depth) for j in range(n)})
                            observed=dag.evaluate(inputs,artifact['output'])
                            expected=direct_response(rows,J);checks+=1
                            if observed!=expected:failures.append({'n':n,'depth':depth,'kind':kind,
                                 'z':z,'J':J,'marked':marked,'observed':str(observed),'expected':str(expected)})
            for marked in (False,True):
                for J in ([],list(range(n))):
                    artifact=compile_response(n,J,depth,marked)
                    name=f'prefix{depth}-n{n}-'+('marked' if marked else 'generic')+'-'+('empty' if not J else 'full')+'.json'
                    (root/name).write_text(json.dumps(artifact,indent=2),encoding='utf-8')
                    counts.append({k:artifact[k] for k in ('n','depth','marked','J','initialization_gates','query_gates','gates')})
    report={'checks':checks,'passed':checks-len(failures),'failures':failures,'gate_counts':counts,
            'root_conjecture_verified':False,'uniform_constructor_scope':'Fixed depth1 or2, one explicit J',
            'all_J_cost':'Separate queries over all 2^n subsets is not a polynomial-size root construction'}
    (root/'atomic-prefix-circuit-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'checks':checks,'passed':report['passed'],'root_conjecture_verified':False}))
    assert not failures

if __name__=='__main__':run()

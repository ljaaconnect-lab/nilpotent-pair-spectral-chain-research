"""Frozen development evaluator. Passing finite tests does NOT prove a theorem."""
import json,random,hashlib
from pathlib import Path
from dag import DAG
import candidate

def reference(n,values,prime):
    z=values['z']; states={0:1}
    for mask in range(1,1<<n):
        i=mask.bit_count()-1
        states[mask]=sum(values[('p',i,j)]*pow(z,1<<(i*n+j),prime)*states[mask^(1<<j)]
                         for j in range(n) if mask>>j&1)%prime
    return states[(1<<n)-1]

def evaluate(seed=202610241,sizes=range(1,8),cases=8,prime=1000003):
    rng=random.Random(seed); checks=0; counts={}
    for n in sizes:
        dag=DAG(); output=candidate.build(n,dag); counts[n]=dag.gates
        assert isinstance(output,int) and 0<=output<len(dag.nodes)
        for case in range(cases):
            vals={('p',i,j):1+rng.randrange(-20,21)**2 for i in range(n) for j in range(n)}
            vals['z']=[0,1,prime-1,rng.randrange(prime)][case%4]
            observed=dag.evaluate(output,vals,prime)
            expected=reference(n,vals,prime)
            assert observed==expected,(n,case,observed,expected)
            checks+=1
    d=DAG(); candidate.build(8,d)
    return {'correct_on_finite_cases':checks,'gate_counts':counts,'score':d.gates,
            'score_direction':'min','global_polynomial_proof':False,
            'candidate_sha256':hashlib.sha256(Path(candidate.__file__).read_bytes()).hexdigest()}

if __name__=='__main__': print(json.dumps(evaluate(),indent=2))

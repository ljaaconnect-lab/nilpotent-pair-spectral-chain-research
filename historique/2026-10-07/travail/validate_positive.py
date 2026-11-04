"""Coordinator-only exact validation; no search or counterexample generation."""
import hashlib, json, random, sys
from fractions import Fraction
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'gate-n4'))
import candidate, recurrence, evaluate
raw=json.loads((root/'test-boundary'/'simulation.json').read_text())
rng=random.Random(105031245)
for rep in range(2):
    raw.append({'name':f'n5-positive-validation-{rep}',
                'A':[[f'{rng.randint(-3,3)}/{rng.randint(1,4)}' for j in range(5)] for i in range(5)]})
fixture=root/'test-boundary'/'positive-simulation.json'
if not fixture.exists(): fixture.write_text(json.dumps(raw,indent=2))
else:
    assert json.loads(fixture.read_text())==raw, 'Frozen boundary mismatch'
report={'protocol':'positive-transfer-heldout-v1','split':'test','passed':0,'total':0,'cases':[],
        'boundary_sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),
        'scope':'Independent exact formal-z checks. No formal proof or polynomial complexity claim.'}
for entry in raw:
    A=[[Fraction(x) for x in row] for row in entry['A']]; n=len(A)
    expected,_=evaluate.reference(A)
    row={'case':entry['name'],'n':n,'checks':{},'gates':{}}
    for name,builder in [('matrix_K',recurrence.build_matrix_power),
                         ('matrix_n',lambda A:recurrence.build_matrix_power(A,len(A))),
                         ('row_chain',recurrence.build_row_chain),
                         ('subset_dp',candidate.build_subset_dp)]:
        dag,output,stats=builder(A)
        got,_=recurrence.exact_output(dag,output)
        row['checks'][name]=got==expected; row['gates'][name]=dag.gates
    got,_=recurrence.tensor_product_polynomial(A)
    row['checks']['tensor']=got==expected
    report['passed']+=sum(row['checks'].values()); report['total']+=len(row['checks'])
    report['cases'].append(row)
report['score']=report['passed']/report['total']
(root/'positive-test-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
if report['passed']!=report['total']: sys.exit(1)

import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT/'research'
TREE=Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
COMMIT='ff868e702c83e8f23f81a626d9d9a3713fdc92d9'
report=json.loads((ROOT/'wt-n77/n77-dev-report.json').read_text(encoding='utf-8'))
symbolic=json.loads((ROOT/'direct-polynomial-validation/direct-polynomial-validation-report.json').read_text(encoding='utf-8'))
assert report['dev_score']==1 and report['root_score']==0
assert symbolic['passed']==4 and symbolic['checks']==4
assert hashlib.sha256((ROOT/'wt-n77/direct_corrected_circuit.py').read_bytes()).hexdigest()==symbolic['source_sha256']
insight='All marks, initialized subset updates, and the whole PA polynomial are directly wired in an explicit scalar DAG. Counts12,34,80,178 and symbolic full outputs pass; the reference has 2^n states, so polynomial compilation remains open.'
for args in [
    ['set-evidence','--node','n77','--dev-score','1','--result','Direct whole-polynomial scalar DAG, local4/4,36/36 development cases and coordinator4/4 complete symbolic outputs; root0',
     '--insight',insight,'--branch-ref',COMMIT],
    ['propagate','--node','n77','--insight',insight,'--to-root']]:
    p=subprocess.run([sys.executable,str(TREE),'--run-dir',str(REPO),*args],capture_output=True,text=True,check=True)
    print(p.stdout.strip())
file=ROOT/'leap-global-search.json';graph=json.loads(file.read_text(encoding='utf-8'))
graph['goals']['G_direct_raccord'].update({'status':'verified_supporting',
    'commit':COMMIT,'whole_polynomial_cases':'4/4 symbolic','state_dimension':'2^n',
    'new_lean_theorems':0,'root_dependency':False})
for i,statement in enumerate([
    'Radix base2^n and binary digits2^sigma(i) are in range',
    'Rewrite true binary address E as radix assignmentLabel',
    'Prove injectivity of E from radix labels and powers',
    'Define chi_n and prove its values on and off the address image',
    'Define literal diagonal Cn linear map and prove its coefficient action',
    'Expand actual marked determinant DA',
    'Correct one monomial using permutation_sign_square',
    'Extend by map_sum to CnDA=markedPermanent']):
    graph['goals'][f'G_direct_semantic_S{i+1}']={'status':'planned_uncompiled','statement':statement}
file.write_text(json.dumps(graph,indent=2),encoding='utf-8')
print(json.dumps({'direct_root_conjecture_verified':False,'new_formal_invocations':0}))

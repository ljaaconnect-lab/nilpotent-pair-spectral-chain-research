import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT/'research'
TREE=Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
jobs=[
 ('n69',None,'Three joint contractions examined; exact contextual sectors and first-prefix fusion; exponential reference has separate 108/108 coordinator development checks.',
  'Sector closure and first-prefix fusion preserve every future q polynomial, but subsequent polynomial sector fusion and charged normalization remain unconstructed.',
  'efb174084fdd2bcac85a9be3bb8f39b9054a1565'),
 ('n70',None,'Explicit row-frame data transport and bordered Gaussian row components; initialization of DR and global component aggregation remain open.',
  'Changing frames closes chart data without computing the diagonal contextual response; transport cost alone does not initialize the extractor.',
  '738dbe2df096fb2176b6fff4e755628c1fe605b6'),
 ('n73',1.0,'Actual all-n initialized subset recurrence and exact marked central output verified in 18 theorems; independent committed replay exit 0. Baseline 4/4; root score 0.',
  'A genuinely closed state family now has a complete Lean proof with explicit initialization and target identity. Its dimension is exactly 2^n, so polynomial compression remains a separate unproved obligation.',
  '97513bc5e9cca5e0b33d0844980d29da1121a234')]
for node,score,result,insight,commit in jobs:
    args=['set-evidence','--node',node,'--result',result,'--insight',insight,'--branch-ref',commit]
    if score is not None: args += ['--dev-score',str(score)]
    p=subprocess.run([sys.executable,str(TREE),'--run-dir',str(REPO),*args],capture_output=True,text=True,check=True)
    print(p.stdout.splitlines()[0])
    p=subprocess.run([sys.executable,str(TREE),'--run-dir',str(REPO),'propagate',
                      '--node',node,'--insight',insight,'--to-root'],capture_output=True,text=True,check=True)
    print(p.stdout.strip())
runfile=REPO/'.arbor/run.json'
run=json.loads(runfile.read_text(encoding='utf-8'))
run['current_formal_window'].update({
    'actual_complete_candidate_compilations':6,
    'actual_independent_commit_replays':1,
    'actual_delivered_source_replays':0,
    'actual_total_compiler_invocations':7,
    'evidence':['n71 compiler rounds 2: timeout124 then actual0; interface only',
                'n73 compiler rounds 4: 1,0,0,0; 18 actual subset theorems',
                'Coordinator n73 exact committed replay:0, 18 audits accepted'],
})
run['root_conjecture_verified']=False
run['actual_closed_baseline_node']='n73'
run['root_polynomial_state_family_verified']=False
runfile.write_text(json.dumps(run,indent=2),encoding='utf-8')
ledgerfile=REPO/'.arbor/verified-bases.json'
ledger=json.loads(ledgerfile.read_text(encoding='utf-8'))
report=json.loads((ROOT/'wt-n73/n73-strict-report.json').read_text(encoding='utf-8'))
replay=json.loads((ROOT/'n73-independent-replay.json').read_text(encoding='utf-8'))
assert replay['baseline_verified'] and replay['exit_code']==0
names={e['theorem'] for e in ledger['entries']}
for theorem in report['declarations']:
    if theorem not in names:
        ledger['entries'].append({'theorem':theorem,'source':report['source'],
            'source_sha256':report['source_sha256'],'axioms':replay['audits'][theorem],
            'dev_score':1.0,'test_score':1.0,'branch_ref':replay['commit'],
            'verification':'Actual all-n subset baseline theorem; independently replayed. State count exponential; original polynomial root unproved.',
            'root_score':0,'node_id':'n73'})
ledger['root_conjecture_verified']=False
ledgerfile.write_text(json.dumps(ledger,indent=2),encoding='utf-8')
graphfile=ROOT/'leap-global-search.json'
graph=json.loads(graphfile.read_text(encoding='utf-8'))
graph['goals']['G_actual_baseline'].update({'status':'proved_supporting',
    'declarations':report['declarations'],'evidence':'n73 independent committed replay exit0',
    'state_dimension':'2^n','root_dependency':False})
graph['goals']['G_lean_root']['note']='Exact finite circuit proposition elaborated in n71; no proof. Full original goal also requires operational uniformity.'
graph['root_status']='open';graph['new_verified_root_obligations']=0
graphfile.write_text(json.dumps(graph,indent=2),encoding='utf-8')
print(json.dumps({'audited_ledger_entries':len(ledger['entries']),
                  'new_theorems':18,'formal_invocations_this_window':7,
                  'root_conjecture_verified':False}))

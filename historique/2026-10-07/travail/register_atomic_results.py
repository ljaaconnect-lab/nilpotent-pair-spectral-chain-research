"""Register the real supporting proofs and preserve the open direct root."""
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT/'research'
TREE=Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
graphfile=ROOT/'leap-global-search.json';graph=json.loads(graphfile.read_text(encoding='utf-8'))
ledgerfile=REPO/'.arbor/verified-bases.json';ledger=json.loads(ledgerfile.read_text(encoding='utf-8'))
seen={item['theorem'] for item in ledger['entries']}
def state(*args):
    p=subprocess.run([sys.executable,str(TREE),'--run-dir',str(REPO),*args],capture_output=True,text=True,check=True)
    print(p.stdout.strip())
for node in ('n75','n76'):
    replay=json.loads((ROOT/(node+'-independent-replay.json')).read_text(encoding='utf-8'))
    assert replay['exit_code']==0 and replay['atomic_lemmas_verified']
    strict=json.loads((ROOT/('wt-'+node)/(node+'-strict-report.json')).read_text(encoding='utf-8'))
    leaves=strict['goal_statuses'] if node=='n75' else [dict(id=k,**v) for k,v in strict['leaves'].items()]
    for leaf in leaves:
        identifier=('A75_' if node=='n75' else 'A76_')+leaf['id']
        graph['goals'][identifier].update({'status':'proved_supporting',
            'declaration':leaf['declaration'],'evidence':'independent commit replay exit0',
            'root_dependency':False})
    target='G_atomic_first_prefix' if node=='n75' else 'G_atomic_second_prefix'
    graph['goals'][target]['status']='proved_supporting'
    for name,axioms in replay['audits'].items():
        if name not in seen:
            ledger['entries'].append({'theorem':name,'source':Path(strict['source']).name,
                'source_sha256':replay['source_sha256'],'axioms':axioms,
                'dev_score':1,'test_score':1,'branch_ref':replay['commit'],
                'verification':'Supporting elementary prefix identity, independently replayed; no full-depth polynomial compilation claim',
                'root_score':0,'node_id':node})
            seen.add(name)
    insight='Six exact first-prefix obligations now verified; local normalization and semantic finite linearity do not supply a free global scalar contraction.' if node=='n75' else \
            'The signed response after two actual row insertions has initialized data and an O(n) single-subset query. General-depth polynomial closure remains open.'
    state('set-evidence','--node',node,'--dev-score','1','--result',
          str(len(leaves))+'/'+str(len(leaves))+' elementary obligations; independent committed replay exit0; root0',
          '--insight',insight,'--branch-ref',replay['commit'])
    state('propagate','--node',node,'--insight',insight,'--to-root')
state('set-evidence','--node','n74','--result','Five explicit AND obligations frozen; no numerical experiment or Lean invocation; direct root unclosed.',
      '--insight','The actual-suffix quotient still lacks initialized suffix response data; initial projective covariance alone is constructible.',
      '--branch-ref','cbb17c6744cee4e9e5c4b423895f55f76ff82858')
state('propagate','--node','n74','--insight','Actual-suffix reading needs explicit construction; an unknown contraction cannot be initialized as a free scalar.','--to-root')
graph['active_target']='Complete corrected polynomial PA=CnDA, scalar Q circuit; all stages polynomially charged'
graph['coefficient_extraction_strategy']='Equivalent historical formulation, not an additional requirement of the direct route'
graph['root_status']='open'
graph['unresolved_constructive_bottleneck']='Initialized polynomial-size scalar updates for arbitrary prefix depth i<=n, connected to the whole corrected polynomial PA; admissible constants and uniform compilation required.'
graphfile.write_text(json.dumps(graph,indent=2),encoding='utf-8')
ledger['root_conjecture_verified']=False
ledgerfile.write_text(json.dumps(ledger,indent=2),encoding='utf-8')
print(json.dumps({'new_atomic_obligations_verified':10,'new_audited_theorems':22,
                  'ledger_audited_entries':len(ledger['entries']),'root_conjecture_verified':False}))

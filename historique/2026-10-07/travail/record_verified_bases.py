"""Coordinator compiler replay and serial Arbor verified-lemma records."""
import hashlib, json, re, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parent
repo=root/'research'; gate=root/'gate-n3'
ledger_path=repo/'.arbor'/'verified-bases.json'
if ledger_path.exists():
    print('Verified-base replay already recorded; no redundant compilation.')
    sys.exit(0)
lean=Path('C:/Users/REGIS/Documents/Codex/runtimes/elan/toolchains/leanprover--lean4---v4.34.1/bin/lean.exe')
tree=Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
ref='a9fb85d1a2d83db55cf85457de978b2f2de3ba57'
allowed={'propext','Classical.choice','Quot.sound'}
report={'status':'helpers_verified','root_conjecture_verified':False,'commit':ref,
        'coordinator_compiler_rounds':2,'total_compiler_rounds':18,'sources':[]}
entries=[]
for filename in ['CoreBridge.lean','GeneratedCoreN2.lean']:
    path=gate/filename
    p=subprocess.run([str(lean),str(path)],cwd=gate,text=True,capture_output=True,encoding='utf-8')
    row={'source':filename,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
         'command':[str(lean),str(path)],'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    report['sources'].append(row)
    if p.returncode!=0:
        report['status']='replay_failed'; (root/'proof-replay.json').write_text(json.dumps(report,indent=2)); sys.exit(1)
    for name,axiom_text in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",p.stdout):
        axioms={x.strip() for x in axiom_text.split(',') if x.strip()}
        if not axioms<=allowed: raise RuntimeError(f'Unaccepted axioms: {name}: {axioms}')
        entries.append({'theorem':name,'source':filename,'source_sha256':row['sha256'],
                        'axioms':sorted(axioms),'dev_score':1.0,'test_score':1.0,
                        'branch_ref':ref,'verification':'kernel-accepted helper; original root unproved'})
assert len(entries)==9
report['accepted_declarations']=9; report['distinct_results']=7
(root/'proof-replay.json').write_text(json.dumps(report,indent=2))

def command(*args):
    p=subprocess.run([sys.executable,str(tree),*args],cwd=repo,text=True,capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr+p.stdout)
    return p.stdout
command('set-evidence','--node','n3','--dev-score','1','--result',
        '9 accepted declarations, 7 distinct helpers, exit0 and no sorryAx; Mathlib draft separately unverified; root unproved',
        '--insight','The exact source preserves fixed-length labels, central equality and stabilization hypotheses; polynomial compilation remains open',
        '--branch-ref',ref)
for entry in entries:
    txt=command('add-node','--parent','n3','--hypothesis',
                'Verified Base Axiom (proved helper): '+entry['theorem'])
    match=re.search(r'node (n\d+)',txt); assert match,txt
    node=match.group(1); entry['node_id']=node
    command('set-evidence','--node',node,'--dev-score','1','--result',
            'Compiler exit0 in executor and fresh coordinator replay; no sorryAx; helper statement only',
            '--insight','Reuse this exact compiled helper with all of its hypotheses; it adds no axiom asserting the conjecture',
            '--branch-ref',ref)
    command('merge','--node',node,'--test-score','1','--branch-ref',ref)
ledger={'label':'Verified Base Axiom is a user-facing node label for a proved lemma, not an added Lean axiom',
        'root_conjecture_verified':False,'distinct_results':7,'entries':entries}
ledger_path.write_text(json.dumps(ledger,indent=2))
print(json.dumps({'compiler_exit_codes':[r['exit_code'] for r in report['sources']],
                  'accepted_declarations':9,'nodes':[e['node_id'] for e in entries],
                  'total_compiler_rounds':18,'root_conjecture_verified':False},indent=2))

import hashlib, json, os, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
REPO = ROOT / 'research'
GATE = ROOT / 'gate-n38'
REF = '59113789e66c150fcab8b293720d01ea7bbcc0fa'
GIT = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
LEAN = Path('C:/Users/REGIS/Documents/Codex/runtimes/elan/toolchains/leanprover--lean4---v4.34.1/bin/lean.exe')
TREE = Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')

def run(args, env=None, cwd=REPO):
    result = subprocess.run(list(map(str,args)), cwd=cwd, env=env,
                            capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(result.stdout+result.stderr)
    return result

def tree(*args):
    return run([sys.executable,TREE,'--run-dir',REPO,*args]).stdout

if not GATE.exists():
    run([GIT,'-c','safe.directory='+REPO.as_posix(),'-C',REPO,'worktree','add','--detach',GATE,REF])
env = os.environ.copy()
env['LEAN_PATH'] = str(GATE)
report = {'node':'n38','commit':REF,'root_conjecture_verified':False,
          'coordinator_compiler_invocations':3,'sources':[]}
for filename in ['CoreBridge.lean','GeneralPairingRing.lean','LabelBridge.lean']:
    path = GATE/filename
    cmd = [LEAN,'-o',path.with_suffix('.olean'),path] if filename!='LabelBridge.lean' else [LEAN,path]
    result = run(cmd,env,GATE)
    report['sources'].append({'file':filename,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'command':list(map(str,cmd)),'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    assert 'sorryAx' not in result.stdout
entries=[]
final=report['sources'][-1]
for name,text in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",final['stdout']):
    axioms={x.strip() for x in text.split(',') if x.strip()}
    assert axioms<={'propext','Classical.choice','Quot.sound'},(name,axioms)
    entries.append({'theorem':name,'source':'LabelBridge.lean','source_sha256':final['sha256'],
                    'axioms':sorted(axioms),'branch_ref':REF,'dev_score':1.0,'test_score':1.0,
                    'verification':'kernel-accepted supporting lemma; root polynomial extraction unproved'})
assert len(entries)==13
report['accepted_new_declarations']=len(entries)
(ROOT/'label-bridge-replay.json').write_text(json.dumps(report,indent=2))
tree('set-evidence','--node','n38','--dev-score','1','--branch-ref',REF,'--result',
     '13 new declarations; indexed finite assignment labels, occupation selector and ring pairing accepted, independent replay exit0; root unproved',
     '--insight','Actual indexed power-sum labels now have proved injectivity and bounds; occupation selection and central pairing preserve their precise original hypotheses')
tree('merge','--node','n38','--test-score','1','--branch-ref',REF)
tree('propagate','--node','n38','--insight',
     'The indexed-label interface is formally proved over arbitrary finite assignments; actual Polynomial interpretation and uniform scalar extraction remain separate obligations')
ledger_path=REPO/'.arbor/verified-bases.json'
ledger=json.loads(ledger_path.read_text())
for entry in entries:
    old=[e for e in ledger['entries'] if e['theorem']==entry['theorem']]
    if old:
        assert old[0]['source_sha256']==entry['source_sha256']
        continue
    output=tree('add-node','--parent','n38','--hypothesis','Verified Base Axiom (proved helper): '+entry['theorem'])
    match=re.search(r'node (n\d+)',output)
    assert match,output
    entry['node_id']=match.group(1)
    tree('set-evidence','--node',entry['node_id'],'--dev-score','1','--branch-ref',REF,'--result',
         'Committed supporting lemma accepted in executor and fresh independent replay; no sorryAx',
         '--insight','Exact indexed-label helper, with every length, bound, distinctness and sign hypothesis retained')
    tree('merge','--node',entry['node_id'],'--test-score','1','--branch-ref',REF)
    ledger['entries'].append(entry)
ledger['accepted_declarations']=len(ledger['entries'])
ledger_path.write_text(json.dumps(ledger,indent=2))
print(json.dumps({'exit_codes':[s['exit_code'] for s in report['sources']],
    'accepted_new_declarations':13,'ledger_total':len(ledger['entries'])}),flush=True)

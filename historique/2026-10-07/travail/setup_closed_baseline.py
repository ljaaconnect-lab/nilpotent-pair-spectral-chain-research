import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT/'research'
TREE=Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
GIT=Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
def state(*args):
    p=subprocess.run([sys.executable,str(TREE),'--run-dir',str(REPO),*args],capture_output=True,text=True,check=True)
    print(p.stdout.strip())
state('cycle')
state('add-node','--parent','n4','--hypothesis',
      'The actual initialized all-n column-subset scalar transfer is a closed finite state family, and its terminal scalar equals the original central target; its explicit exponential dimension is a baseline, with no polynomial-root credit.')
WT=ROOT/'wt-n73'
subprocess.run([str(GIT),'-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),
                'worktree','add','-b','arbor/n73',str(WT),
                '1c3ee90c7cd972413db18112a8578ea96a34b2bb'],check=True)
protocol={
    'node':'n73','artifact_goal':'ActualClosedSubsetTransfer.lean',
    'target':'F0(U)=delta(U=empty), F(k+1)(U)=sum_(j in U) b(k,j) Fk(U.erase j); terminal full subset at k=n equals sum over permutations, then marked central target',
    'root_statement_unchanged':True,'root_credit':False,
    'state_dimension':'2^n, explicitly exponential; not the polynomial family required by Conjecture 1.5',
    'formal_invocation_cap':8,
    'counting':'Every candidate, diagnostic probe and new dependency compilation counts within both n73 cap 8 and shared continuation window 20',
    'required_complete_claims':['Actual finite scalar initialization','All-n closed subset update',
        'Exact injection-prefix invariant or equivalent actual polynomial coefficient invariant',
        'Terminal equality to the true permutation sum and marked target'],
    'development':'Actual compiler and #print axioms; no replacement numerical identity credited as all-n proof',
    'test_boundary':'Fresh coordinator replay only if complete all-n baseline theorem compiled',
    'forbidden':['No sorry/custom axioms/native_decide','No assumptions asserting closure or target identity',
        'No arbitrary M,u,v substituted for the actual subset transfer','No root success for an exponential state family',
        'No repeated generic matrix-compiler helper','No counterexample generation'],
    'root_conjecture_verified':False,
}
(WT/'n73-protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
state('set-status','--node','n73','--status','running')
graphfile=ROOT/'leap-global-search.json'
graph=json.loads(graphfile.read_text(encoding='utf-8'))
graph['goals']['G_actual_baseline']={'status':'open','node':'n73','root_dependency':False,
    'note':'Prove an actual closed state family; exponential dimension does not close the polynomial-state obligation.'}
graphfile.write_text(json.dumps(graph,indent=2),encoding='utf-8')

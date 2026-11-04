"""Apply the user steering: directly wire the complete corrected polynomial."""
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT/'research'
TREE=Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
GIT=Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
def state(*args):
    p=subprocess.run([sys.executable,str(TREE),'--run-dir',str(REPO),*args],capture_output=True,text=True,check=True)
    print(p.stdout.strip())
state('cycle')
state('add-node','--parent','n4','--hypothesis',
      'The initialized subset transfer is compiled into one explicit scalar DAG for the entire corrected polynomial PA, with input marks and all row updates charged, without central coefficient extraction. This is a fully wired reference; its exponential state count remains a compression obligation.')
WT=ROOT/'wt-n77'
subprocess.run([str(GIT),'-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),
               'worktree','add','-b','arbor/n77',str(WT),'97513bc5e9cca5e0b33d0844980d29da1121a234'],check=True)
protocol={'node':'n77','artifact_goal':'direct_corrected_circuit.py',
 'new_lean_invocations_allowed':0,'semantics':'Existing independently verified n73 state recurrence and marked_target theorem',
 'target':'Complete PA(z)=Cn(DA(z)), as defined in Conjecture1.5',
 'circuit_scope':'All n>=1, p_ij and z leaves, +/* only, explicit initialized states',
 'recipe':'F(empty)=1; for nonempty U of size k use row k-1 and sum j in U b_(k-1,j)*F(U.erase j); output full-set state',
 'gates_recipe':'Shared marks2*n*n-1 plus generic recurrence(n-1)*2^n+1, total(n-1)*2^n+2*n*n',
 'forbidden':['No central t coefficient extraction','No free Cn gate','No unknown coefficient as input',
 'No divisions or auxiliary-ring gates','No counterexample/lower-bound generation','No root polynomial claim from this reference',
 'No Lean invocations','No writes to .arbor/outputs'],
 'development_positive_checks':{'n':[2,3,4,5],'A':['identity','Vandermonde','cycle'],'z':[-1,0,1]},
 'test_boundary':'Coordinator reruns source-frozen DAG evaluation separately; no new root extractor heldout boundary',
 'root_score':0,'root_conjecture_verified':False}
(WT/'n77-protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
state('set-status','--node','n77','--status','running')
graphfile=ROOT/'leap-global-search.json';graph=json.loads(graphfile.read_text(encoding='utf-8'))
graph['active_target']='Direct scalar circuit for PA=Cn(DA), with all stages charged polynomially'
graph['coefficient_extraction_strategy']='Archived equivalent reformulation; not required by the direct target and not an active additional obligation'
graph['goals']['G_direct_raccord']={'status':'open','node':'n77','root_dependency':False,
    'note':'Compile actual all-n baseline as a direct scalar reference; polynomial compression still required'}
graph['goals']['G_lean_root']['direct_Cn_semantic_bridge']='Paper identifies PA=CnDA; current Lean target is explicit markedPermanent. Literal Cn definition and equality must be formalized before claiming every original statement is Lean verified.'
graphfile.write_text(json.dumps(graph,indent=2),encoding='utf-8')

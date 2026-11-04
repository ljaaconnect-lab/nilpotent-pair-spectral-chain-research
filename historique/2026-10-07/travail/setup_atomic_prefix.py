"""Apply the user's new steering without resetting the shared formal budget."""
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT/'research'
TREE=Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
GIT=Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
runfile=REPO/'.arbor/run.json'
run=json.loads(runfile.read_text(encoding='utf-8'))
run['budget_cycles']=24
run['atomic_decomposition_authorization']='User explicitly redirects the active search to elementary constructive subproblems solved one by one; four further coordinator cycles allocated locally, no formal budget reset.'
run['current_formal_window']['actual_total_compiler_invocations']=7
runfile.write_text(json.dumps(run,indent=2),encoding='utf-8')
def state(*args):
    p=subprocess.run([sys.executable,str(TREE),'--run-dir',str(REPO),*args],capture_output=True,text=True,check=True)
    print(p.stdout.strip())
state('cycle')
state('add-node','--parent','n15','--hypothesis',
      'The exact first-prefix q-context response and its rank-one determinantal fusion are constructively proved through six elementary finite-sum and matrix identities, with explicit data initialization and no claim of full-prefix fusion.')
WT=ROOT/'wt-n75'
subprocess.run([str(GIT),'-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),
                'worktree','add','-b','arbor/n75',str(WT),
                'efb174084fdd2bcac85a9be3bb8f39b9054a1565'],check=True)
leaves=[
 {'id':'A1','statement':'h=sum_j b_j; sum_(j not in J)b_j=h-sum_(j in J)b_j',
  'proof_plan':'Partition the finite sum into J and its complement'},
 {'id':'A2','statement':'One-column response on q_J is (-1)^card(J) if j not in J, zero otherwise',
  'proof_plan':'The commuting square-zero basis rule, stated as an explicit disjoint-set coefficient'},
 {'id':'A3','statement':'The weighted first-prefix response is (-1)^card(J)*(h-sum_J b_j)',
  'proof_plan':'Linear finite sum of A2 followed by A1'},
 {'id':'A4','statement':'det((-I+u*1^T)[J,J])=(-1)^card(J)*(1-sum_J u_j)',
  'proof_plan':'Use actual pinned Mathlib rank-one determinant lemma and determinant of a negated matrix; include empty J'},
 {'id':'A5','statement':'If h*u_j=b_j for every j, h times A4 equals A3 for every J',
  'proof_plan':'Distribute h across the finite sum and ring; local normalization hypothesis is explicit, not a root assumption'},
 {'id':'A6','statement':'Equality on all basis q_J extends to every finite coefficient vector f(q)',
  'proof_plan':'Finite linearity; this semantic extension is not a free scalar contraction gate'},
]
protocol={
 'node':'n75','hypothesis_fixed':True,'artifact_goal':'AtomicFirstPrefix.lean',
 'leaves':leaves,'resolution_mode':'Sequential elementary sublemmas, hardest matrix identity retrieved before inventing helpers',
 'formal_invocation_cap':8,'shared_formal_window_cap':20,'already_used_shared_invocations':7,
 'counting':'Every candidate/probe/retry/dependency build counts; preserve global counts without reset',
 'required':'Six actual exact statements, compiler exit0, standard-axiom audit, no placeholder',
 'local_assumptions':'Rank-one normalization h*u=b is a local algebraic hypothesis only; existence and scalar compilation for arbitrary inputs must be discharged separately before a root claim',
 'resource_boundary':'Data (h,b) and single-query response have explicit +/* construction; all-f functional extension is semantic and has no claimed free evaluation',
 'root_score':0,'root_conjecture_verified':False,
 'forbidden':['No assertion that second-prefix/global fusion is obvious','No axiom asserting Delta construction',
              'No sorry/custom axiom/native_decide','No unknown target as initialized data',
              'No variable division leaf','No counterexample/lower-bound generation','No B_test/.arbor/outputs access'],
 'test_boundary':'Coordinator-only fresh exact-source replay after full local proof is frozen',
}
(WT/'n75-protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
state('set-status','--node','n75','--status','running')
graphfile=ROOT/'leap-global-search.json'
graph=json.loads(graphfile.read_text(encoding='utf-8'))
graph['goals']['G_atomic_first_prefix']={'status':'open','node':'n75',
    'required_leaves':[leaf['id'] for leaf in leaves],
    'root_dependency':False,'note':'First-prefix fusion only. Global compact fusion remains open.'}
for leaf in leaves:
    graph['goals']['A75_'+leaf['id']]={'status':'open','statement':leaf['statement'],
                                   'proof_plan':leaf['proof_plan']}
graph['atomic_sequence']=['A75_'+leaf['id'] for leaf in leaves]
graph['unresolved_constructive_bottleneck']='Construct explicit initialized scalar updates for every later prefix, not merely prove a conditional response identity.'
graphfile.write_text(json.dumps(graph,indent=2),encoding='utf-8')

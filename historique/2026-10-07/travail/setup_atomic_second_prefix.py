"""Freeze the next elementary stage, without asserting a global compact closure."""
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT/'research'
TREE=Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
GIT=Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
def state(*args):
    p=subprocess.run([sys.executable,str(TREE),'--run-dir',str(REPO),*args],capture_output=True,text=True,check=True)
    print(p.stdout.strip())
state('cycle')
state('add-node','--parent','n15','--hypothesis',
      'An exact initialized second-prefix response is built from three finite sums and the Hadamard product of two explicit rows, via sequential product-expansion and diagonal-removal lemmas, without variable division.')
WT=ROOT/'wt-n76'
subprocess.run([str(GIT),'-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),
    'worktree','add','-b','arbor/n76',str(WT),'efb174084fdd2bcac85a9be3bb8f39b9054a1565'],check=True)
leaves=[
 {'id':'B1','statement':'(sum_H b)*(sum_H c)=sum_j_in_H sum_k_in_H b_j*c_k','method':'Finite distributivity'},
 {'id':'B2','statement':'sum_j_in_H sum_k_in_H_erase_j b_j*c_k=(sum_H b)*(sum_H c)-sum_H b_j*c_j','method':'Separate k=j with sum_erase_add, then distribute'},
 {'id':'B3','statement':'Signed response from the actual two-column square-zero insertion array equals (-1)^cardJ times B2 on H=univ\\J','method':'Finite disjoint-set coefficient rule, sign of two insertions'},
 {'id':'B4','statement':'The initialized data b,c,d_j=b_j*c_j,h_b,h_c,h_d recover B3 from three complement sums','method':'Finite partition three times and ring'},
]
protocol={'node':'n76','artifact_goal':'AtomicSecondPrefix.lean','leaves':leaves,
 'formal_invocation_cap':3,'formal_invocations_before_authorization':0,
 'compile_start':'Coordinator authorization after the n75 dependency build finishes; shared window cap20 unchanged',
 'initialization_cost':'n multiplications + 3*max(n-1,0) additions; row leaves already explicit',
 'query_cost':'O(n) arithmetic gates for one explicit subset J; using literal -1 for subtractions',
 'root_score':0,'root_conjecture_verified':False,
 'forbidden':['No free contraction with arbitrary future f','No unknown prefix partition function as input',
 'No variable division','No global closure assertion','No counterexample/lower-bound campaign',
 'No sorry/custom axioms/native_decide','No writes to .arbor or outputs'],
 'test_boundary':'Fresh coordinator exact-commit replay if all accepted declarations are compiler verified'}
(WT/'n76-protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
state('set-status','--node','n76','--status','running')
graphfile=ROOT/'leap-global-search.json'; graph=json.loads(graphfile.read_text(encoding='utf-8'))
for leaf in leaves: graph['goals']['A76_'+leaf['id']]={'status':'open',**leaf,'root_dependency':False}
graph['atomic_sequence'] += ['A76_'+leaf['id'] for leaf in leaves]
graph['goals']['G_atomic_second_prefix']={'status':'open','node':'n76','required_leaves':[l['id'] for l in leaves],
    'root_dependency':False,'note':'Exact fixed-prefix2 response, not global closure or a free future contraction'}
graphfile.write_text(json.dumps(graph,indent=2),encoding='utf-8')

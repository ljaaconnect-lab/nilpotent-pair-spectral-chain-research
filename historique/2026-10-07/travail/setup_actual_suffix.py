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
state('add-node','--parent','n19','--hypothesis',
      'Restricting a contextual Gaussian or adjugate transfer to the actual known suffix row products admits an initialized polynomial scalar state for the single true target, without constructing all q-polynomial responses or using the unknown suffix target as input.')
WT=ROOT/'wt-n74'
subprocess.run([str(GIT),'-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),
                'worktree','add','-b','arbor/n74',str(WT),
                '738dbe2df096fb2176b6fff4e755628c1fe605b6'],check=True)
protocol={
    'node':'n74','hypothesis_fixed':True,'candidate_limit':2,
    'candidates':['Context-specific projective Schur/covariance update',
                  'Charged adjugate response restricted to actual suffix row products'],
    'parent_material':'n70 variable-frame transport and explicit DR response; n69 contextual prefix sectors read-only',
    'exact_target':'L(P_n)=per(B); marked substitution and original central coefficient stay unchanged',
    'root_obligations':['Explicit uniform scalar initialization from allowed p entries, z and short constants',
                        'Exact updates preserving the actual suffix contraction for every n and rational A',
                        'Exact terminal scalar and polynomial gate/literal-bit/bit-time bounds; full Lean root'],
    'metric':'Three complete root obligations closed / three; conditions, formal definitions and small-size fits do not close root',
    'formal_invocations_allocated':0,
    'development':'No evaluation until an initialized explicit complete candidate exists; then freeze executable before positive n=2..5 checks',
    'test_boundary':'Coordinator-only root boundary remains untouched',
    'forbidden':['No unknown prefix/suffix partition function used as input','No counterexample or lower-bound campaigns',
                 'No free Wick, Pfaffian, derivative, Hadamard, coefficient or variable-division gates',
                 'No assumption of global Gaussian closure','No full-context preservation advertised if only actual suffix is preserved',
                 'No weakened root quantifiers or altered input marking'],
    'note':'Preserving every arbitrary polynomial f(q) was a sufficient helper requirement, not a requirement of Conjecture 1.5. Its relaxation does not resolve initialization.',
    'root_conjecture_verified':False,
}
(WT/'n74-protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
state('set-status','--node','n74','--status','running')
graphfile=ROOT/'leap-global-search.json'
graph=json.loads(graphfile.read_text(encoding='utf-8'))
graph['goals']['G_actual_suffix']={'status':'open','node':'n74'}
graph['goals']['G0']['strategies'].append('S_actual_suffix')
graph['strategies']['S_actual_suffix']={'parent':'G0','required':[
    'G_target_identity','G_actual_suffix','G_initialization','G_scalar_cost',
    'G_literal_bits','G_uniform_program','G_lean_root']}
graphfile.write_text(json.dumps(graph,indent=2),encoding='utf-8')

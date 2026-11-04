import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT/'research'
WT = ROOT/'wt-n72'
TREE = Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
GIT = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
report = json.loads((WT/'n72-dev-report.json').read_text(encoding='utf-8'))
assert len(report['results']) == 12 and report['supporting_fit_count'] == 6
text = '''# n72 — finite positive pole-functional synthesis

The three frozen root grids have distinct rational poles and denominator degree n².
For every permutation σ, qσ is the polynomial whose factors are all unselected
edge poles; its degree is n²−n. A linear functional ℓ satisfying ℓ(qσ)=sgn(σ)
would give ℓ(D det(Bij/(t−θij)))=per(B), by determinant expansion.

Positive exact SymPy synthesis evaluated every permutation for n=2,3,4,5.
The functional exists on each n=2,3 development grid (six fits in total).
None of the three frozen grids produced a functional at n=4 or n=5.
These are constraints on the chosen grids only, not a disproof or a lower bound
for the conjecture. No numerical matrix counterexamples were generated.

Even a development fit needs an all-n analytic construction with polynomial
preprocessing; factorial enumeration and rational row reduction are not that
constructor. The determinant rational expression also needs a division-free
scalar compilation. Coefficient-array gates and literal bits must be charged.
No full root circuit was isolated, no held-out boundary was opened, and no Lean
compiler was invoked in this node. Root score is 0/4 obligations closed.
'''
(WT/'N72_INSIGHTS.md').write_text(text, encoding='utf-8')
(WT/'n72-leaf-result.json').write_text(json.dumps({
    'node': 'n72', 'artifact_version': 'pole-functional-v1', 'dev_score': 0.0,
    'result': 'Six exact development fits for n=2,3; no functional supplied by the three frozen pole grids for n=4,5. No root constructor.',
    'insight': 'Polynomial degree of the rational determinant alone does not supply the sign-correcting coefficient functional; its exact permutation identities and uniform initialization need separate construction.',
    'branch_ref': 'arbor/n72', 'root_conjecture_verified': False,
    'formal_compiler_invocations': 0, 'heldout_runs': 0,
}, indent=2), encoding='utf-8')
cmd = [str(GIT), '-c', 'safe.directory='+WT.as_posix(), '-C', str(WT)]
subprocess.run(cmd+['add','n72-protocol.json','pole_functional_candidate.py','n72-source-freeze.json',
                    'n72-dev-report.json','N72_INSIGHTS.md','n72-leaf-result.json'], check=True)
subprocess.run(cmd+['-c','user.name=Codex Research','-c','user.email=codex@local.invalid',
                    'commit','-m','Evaluate three frozen low-degree positive pole encodings'], check=True)
commit = subprocess.run(cmd+['rev-parse','HEAD'], capture_output=True, text=True, check=True).stdout.strip()
for args in [
    ['set-evidence','--node','n72','--dev-score','0','--result',
     'Six exact small-size positive functional fits; no all-n root extractor or charged initialization constructed.',
     '--insight','Low denominator degree does not establish a sign-correcting functional or its polynomial uniform initialization.',
     '--branch-ref',commit],
    ['propagate','--node','n72','--insight',
     'A small rational denominator must be accompanied by an exact sign functional on every permutation and its charged uniform construction; finite fitting is only development evidence.','--to-root']
]:
    p = subprocess.run([sys.executable, str(TREE),'--run-dir',str(REPO),*args],
                       capture_output=True,text=True,check=True)
    print(p.stdout.strip())
runfile=REPO/'.arbor/run.json'
run=json.loads(runfile.read_text(encoding='utf-8'))
run['current_formal_window']['actual_total_compiler_invocations']=2
run['current_formal_window']['evidence']=['n71 round 1 timeout 180s, round 2 actual exit 0; no new theorem']
runfile.write_text(json.dumps(run,indent=2),encoding='utf-8')
print(json.dumps({'node':'n72','commit':commit,'root_conjecture_verified':False}))

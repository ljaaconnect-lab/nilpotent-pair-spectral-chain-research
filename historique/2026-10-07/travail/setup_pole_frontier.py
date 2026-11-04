"""Freeze one positive rational-function candidate family before exact fitting."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT / 'research'
TREE = Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
GIT = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')

def state(*args):
    p = subprocess.run([sys.executable, str(TREE), '--run-dir', str(REPO), *args],
                       capture_output=True, text=True, check=True)
    print(p.stdout.strip())

state('cycle')
state('add-node', '--parent', 'n16', '--hypothesis',
      'A fixed polynomial-degree univariate rational pole encoding admits an explicitly constructible linear coefficient functional correcting every permutation sign, with polynomial scalar compilation and initialization costs.')
WT = ROOT / 'wt-n72'
subprocess.run([str(GIT), '-c', 'safe.directory=' + REPO.as_posix(), '-C', str(REPO),
                'worktree', 'add', '-b', 'arbor/n72', str(WT),
                '1c3ee90c7cd972413db18112a8578ea96a34b2bb'], check=True)
protocol = {
    'node': 'n72', 'hypothesis_fixed': True,
    'source_identity': 'q_sigma(t)=D_n(t)/product_i(t-theta_i,sigma(i)); a valid functional must satisfy ell(q_sigma)=sign(sigma) for every sigma',
    'candidate_variants': ['additive', 'squared_additive', 'radix'],
    'theta': {'additive': '(n+1)*(i+1)+(j+1)',
              'squared_additive': '((n+1)*(i+1)+(j+1))**2',
              'radix': '(n+1)**(i+1)+(j+1)'},
    'development': 'Exactly all permutations at n=2,3,4,5; linear functional synthesis only, no matrix counterexample generation',
    'root_obligations': ['An all-n analytic formula or polynomial-time uniform constructor for ell',
                         'Exact functional identity on every permutation',
                         'Division-free scalar compilation of D*det(B_ij/(t-theta_ij))',
                         'Polynomial total gate and literal-bit bounds, complete Lean verification'],
    'root_metric': 'Complete root obligations discharged / four; finite fits alone get no root credit',
    'test_boundary': 'Untouched coordinator-only root boundary; not run until an eligible all-n scalar constructor is frozen',
    'forbidden': ['No counterexample or lower-bound campaigns', 'No free coefficient extraction or variable division gates',
                  'No factorial-time functional fitting advertised as a uniform constructor', 'No finite n observations advertised as an all-n proof'],
    'formal_invocations_allocated': 0, 'root_conjecture_verified': False,
}
(WT / 'n72-protocol.json').write_text(json.dumps(protocol, indent=2), encoding='utf-8')
state('set-status', '--node', 'n72', '--status', 'running')
graph_file = ROOT / 'leap-global-search.json'
graph = json.loads(graph_file.read_text(encoding='utf-8'))
graph['goals']['G_target_identity']['declaration'] = 'CollisionEncodingBridge.marked_A_central_identity'
graph['goals']['G_target_identity']['evidence'] = 'Exact namespace reconfirmed in unchanged delivered EncodingBridge.lean'
graph['goals']['G0']['strategies'].append('S_rational_poles')
graph['goals']['G_pole_functional'] = {'status': 'open', 'node': 'n72'}
graph['strategies']['S_rational_poles'] = {'parent': 'G0', 'required': [
    'G_target_identity', 'G_pole_functional', 'G_initialization', 'G_scalar_cost',
    'G_literal_bits', 'G_uniform_program', 'G_lean_root']}
graph_file.write_text(json.dumps(graph, indent=2), encoding='utf-8')
print(json.dumps({'node': 'n72', 'protocol_sha256': hashlib.sha256((WT/'n72-protocol.json').read_bytes()).hexdigest()}))

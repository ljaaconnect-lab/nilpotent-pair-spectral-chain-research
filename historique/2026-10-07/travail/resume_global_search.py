import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
repo = root / 'research'
tree = Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
git = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')

def state(*args):
    result = subprocess.run([sys.executable, str(tree), '--run-dir', str(repo), *args],
                            capture_output=True, text=True, check=True)
    print(result.stdout.strip())

state('cycle')
jobs = [
    ('n69', 'A simultaneous graded contraction of both basis kernels and the paired cap admits a polynomial-size Gaussian representation after the contextual row-incidence reduction, with every input and cap shuffle retained.', 0),
    ('n70', 'Synchronizing whole row blocks in the reduced two-family kernel admits a polynomial-dimensional closed scalar transfer initialized from generic entries, without a degree-four Wick closure assumption.', 0),
    ('n71', 'An explicit finite scalar DAG model with only marked p entries, z and bit-bounded rational literals captures the unconditional algebraic circuit goal and its separate uniform-construction obligation; complete root closure still requires an actual constructor.', 8)
]
for node, hypothesis, formal_cap in jobs:
    state('add-node', '--parent', 'n68', '--hypothesis', hypothesis)
    worktree = root / ('wt-' + node)
    subprocess.run([str(git), '-c', 'safe.directory=' + repo.as_posix(), '-C', str(repo),
                    'worktree', 'add', '-b', 'arbor/' + node, str(worktree),
                    '1c3ee90c7cd972413db18112a8578ea96a34b2bb'], check=True)
    protocol = {
        'node': node, 'hypothesis': hypothesis, 'root_statement_unchanged': True,
        'root_obligations': ['Explicit scalar construction and target identity for every n and rational A',
                             'Polynomial total gate and rational-literal bit costs',
                             'Uniform circuit construction in polynomial time in n and L, plus full Lean dependency chain'],
        'root_metric': 'Complete root obligations discharged / three; no partial helper or elaborated definition counted as root proof',
        'candidate_limit': 3 if node != 'n71' else 8,
        'formal_compiler_allocation': formal_cap,
        'dev_boundary': 'Frozen positive construction checks n=2,3,4,5 only after an explicit executable candidate is isolated',
        'test_boundary': 'Coordinator-only unused projection-frontier boundary; not accessible to executors',
        'forbidden': ['Counterexample campaigns', 'Lower-bound experiments', 'Free projection or coefficient gates',
                      'Dropping graded shuffles', 'Unknown target coefficients as input leaves',
                      'Assuming Gaussian closure or derivative-context stability', 'Changing the fixed hypothesis',
                      'Calling an elaborated proposition a proved theorem', 'Omitting uniform construction from the full root'],
        'root_conjecture_verified': False,
        'authorization': 'User objects to stopping before a closed state family exists; resume substantive global construction search.'
    }
    (worktree / (node + '-protocol.json')).write_text(json.dumps(protocol, indent=2), encoding='utf-8')
    state('set-status', '--node', node, '--status', 'running')

run_path = repo / '.arbor/run.json'
run = json.loads(run_path.read_text(encoding='utf-8'))
history = run.setdefault('formal_window_history', [])
history.append({'label': 'through n68', **run['current_formal_window']})
run['current_formal_window'] = {'max_decomposition_layers': 3, 'complete_candidate_rounds': 20,
    'actual_total_compiler_invocations': 0, 'counting': 'Shared new continuation window; all candidates, dependencies and replays count together. Prior 19 invocations remain in history.',
    'authorization': 'User explicitly requests continuing the unclosed construction search.'}
run['continuation_authorization'] = 'User asks why search stopped without a closed family; resume global proof search, not merely local reporting.'
run_path.write_text(json.dumps(run, indent=2), encoding='utf-8')

graph = {
    'method': 'Local adapted LEAP AND-OR search graph; not a proof certificate',
    'root': 'G0', 'root_status': 'open',
    'root_statement': 'Conjecture 1.5, original all-n/all-rational-A polynomial scalar circuit, admissible literals and uniform polynomial-time construction in n,L',
    'exact_source': 'annihilation.pdf p5, Conjecture 1.5; local extracted text lines 234ff',
    'lean_environment': 'Lean and Mathlib 4.34.1 pinned; all three environment variables required',
    'goals': {
        'G0': {'status': 'open', 'strategies': ['S_gaussian', 'S_row_transfer']},
        'G_target_identity': {'status': 'proved_supporting', 'declaration': 'CollisionEncoding.marked_A_central_identity',
                              'evidence': 'Previously accepted EncodingBridge.lean; exact name reconfirm before reuse'},
        'G_joint_shuffle': {'status': 'open', 'node': 'n69'},
        'G_row_state': {'status': 'open', 'node': 'n70'},
        'G_initialization': {'status': 'open'},
        'G_scalar_cost': {'status': 'open'},
        'G_literal_bits': {'status': 'open'},
        'G_uniform_program': {'status': 'open', 'note': 'Existence of an abstract circuit family is insufficient'},
        'G_lean_root': {'status': 'open', 'node': 'n71', 'note': 'Exact statement elaboration is not proof'}
    },
    'strategies': {
        'S_gaussian': {'parent': 'G0', 'required': ['G_target_identity', 'G_joint_shuffle', 'G_initialization', 'G_scalar_cost', 'G_literal_bits', 'G_uniform_program', 'G_lean_root']},
        'S_row_transfer': {'parent': 'G0', 'required': ['G_target_identity', 'G_row_state', 'G_initialization', 'G_scalar_cost', 'G_literal_bits', 'G_uniform_program', 'G_lean_root']}
    },
    'acyclic': True, 'new_verified_root_obligations': 0
}
(root / 'leap-global-search.json').write_text(json.dumps(graph, indent=2), encoding='utf-8')
print(json.dumps({'nodes': ['n69','n70','n71'], 'new_formal_rounds_allocated': 20,
                  'prior_formal_rounds_preserved': 19, 'root_conjecture_verified': False}))

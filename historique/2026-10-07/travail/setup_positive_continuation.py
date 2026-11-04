import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
repo = root / 'research'
git = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
tree = Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
run_path = repo / '.arbor/run.json'
state = json.loads(run_path.read_text(encoding='utf-8'))
state['budget_cycles'] = 16
state['continuation_authorization'] = 'User: Maintenant ferme positivement la conjecture. New positive-only continuation window; original root statement and metric unchanged.'
state['current_formal_window'] = {'max_decomposition_layers': 3, 'complete_candidate_rounds': 20,
    'counting': 'All current-window formal child candidates and retries count jointly; prior rounds are preserved separately.'}
run_path.write_text(json.dumps(state, indent=2), encoding='utf-8')

contracts = {
    'n63': {'parent': 'n61', 'base_ref': '2a3a6830f57eb8df200f920ec5058214bec5c32e',
        'hypothesis': 'Uniform Mobius correction coefficient and integer literal bound',
        'dev_boundary': 'Generic Lean theorems with all finite-set binders preserved; compiler and axiom audit',
        'test_boundary': 'Coordinator fresh checkout replay of exact committed source and printed axioms',
        'metric': 'fraction of four fixed helper obligations verified; root conjecture score is independent and remains zero',
        'obligations': ['Explicit Mobius coefficient definition over S.powerset',
            'Zeta reconstruction equals original function, without assuming reconstruction',
            'abs coefficient <= 2^S.card when every function value has abs <= 1',
            'natAbs coefficient < 2^(n+1) if S.card <= n'],
        'candidate_limit': 12, 'forbidden': ['sorryAx', 'new axioms', 'native_decide', 'assuming a polynomial representation'],
        'root_conjecture_verified': False},
    'n64': {'parent': 'n61', 'base_ref': '2a3a6830f57eb8df200f920ec5058214bec5c32e',
        'hypothesis': 'A single local Pfaffian computes c(S); fixed global aggregation is a separate obligation',
        'dev_boundary': 'All partial matchings for n=2,3,4,5; compare n61 recurrence, explicit Mobius sum, local Pfaffian, and charged trace recurrence',
        'test_boundary': 'Coordinator-only fixed fresh permutations and partial matchings at n=6,7,8; independent exact evaluator, committed source before boundary read',
        'metric': 'fraction of four local coefficient identities checked; no local score proves a global polynomial extractor',
        'gate_count': 'Count all add/mul of symbolic-entry trace Pfaffian recurrence; fixed rational divisions lower to rational-literal multiplication. Construction operations reported separately from scalar output gates.',
        'formal_status': 'Local Pfaffian formula remains informal until a complete generic Lean dependency chain exists',
        'forbidden': ['counterexample generation', 'lower-bound experiments', 'free contraction', 'claiming S-dependent matrices form one global representation'],
        'root_conjecture_verified': False}
}
for node, contract in contracts.items():
    worktree = root / ('wt-' + node)
    subprocess.run([str(git), '-c', 'safe.directory=' + repo.as_posix(), '-C', str(repo),
        'worktree', 'add', '-b', 'arbor/' + node, str(worktree), contract['base_ref']], check=True)
    (worktree / (node + '-protocol.json')).write_text(json.dumps(contract, indent=2), encoding='utf-8')
    subprocess.run([sys.executable, str(tree), '--run-dir', str(repo), 'set-status', '--node', node,
        '--status', 'running'], check=True)
subprocess.run([sys.executable, str(tree), '--run-dir', str(repo), 'cycle'], check=True)
print(json.dumps({'worktrees': [str(root / ('wt-' + n)) for n in contracts], 'contracts': list(contracts)}))

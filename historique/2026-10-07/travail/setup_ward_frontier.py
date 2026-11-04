import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
repo = root / 'research'
git = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
tree = Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')

def state(*args):
    return subprocess.run([sys.executable, str(tree), '--run-dir', str(repo), *args],
                          check=True, capture_output=True, text=True).stdout

print(state('cycle'))
print(state('add-node', '--parent', 'n61', '--hypothesis',
    'The two structured Pfaffian families admit a polynomial-size module of mixed contraction moments stable under every remaining synchronization factor, with explicit scalar initialization and updates.'))
node = 'n68'
worktree = root / ('wt-' + node)
subprocess.run([str(git), '-c', 'safe.directory=' + repo.as_posix(), '-C', str(repo),
    'worktree', 'add', '-b', 'arbor/' + node, str(worktree),
    'c785376a2d255cc76db771d239c86c89cc7b888f'], check=True)
contract = {
    'node': node, 'artifact_version': 'n68-contextual-closure-search-v1',
    'hypothesis': 'Polynomial-size mixed Ward moment module for actual synchronized two-family Pfaffian contraction',
    'obligations': [
        'Explicit polynomial-dimensional state map, scalar initialization from generic B, and boundary with no unknown coefficient input',
        'Actual closed scalar update and polynomial gates and allowed-literal bit costs for every synchronization in the full remaining context',
        'Exact identity with the original central coefficient for all n>=2 and rational A; formal root closure only with complete Lean dependency chain'],
    'metric': 'Number of complete original root obligations discharged divided by three; supporting identities are separate',
    'dev_boundary': 'At most two concrete positive closure candidates; freeze source and identity protocol before executing supportive SymPy checks for n=2,3,4,5',
    'test_boundary': 'No held-out access; any full candidate is committed for coordinator-only fresh gate',
    'formal_budget': 'Zero compiler invocations allocated; return an exact constructive blueprint before any new formal window',
    'forbidden': ['Counterexample generation', 'Lower-bound experiments', 'Free differentiation or projection gates',
        'Replacing every future synchronization factor by a bare Gaussian tail',
        'Assuming Gaussian or Ward module closure as an axiom', 'Changing the fixed hypothesis',
        'Representing the target or unknown initial jets as inputs'],
    'root_conjecture_verified': False
}
(worktree / 'n68-protocol.json').write_text(json.dumps(contract, indent=2), encoding='utf-8')
print(state('set-status', '--node', node, '--status', 'running'))
print(json.dumps({'node': node, 'worktree': str(worktree), 'cycles_used': 16, 'budget_cycles': 20}))

import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
repo = root / 'research'
git = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
tree = Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
worktree = root / 'wt-n67'
subprocess.run([str(git), '-c', 'safe.directory=' + repo.as_posix(), '-C', str(repo),
    'worktree', 'add', '-b', 'arbor/n67', str(worktree),
    'c785376a2d255cc76db771d239c86c89cc7b888f'], check=True)
contract = {'node': 'n67', 'parent': 'n64', 'origin': 'n66 candidate',
    'domain': 'four Boolean legs, rational scalar amplitudes, explicit Pfaffian four-mode boundary polynomial',
    'obligations': ['H tensor power 4 applied to COPY4 equals 2 times EVEN4 for every four-bit output',
        'Explicit Pfaffian boundary at all six skew upper entries equal to 1 equals EVEN4 on every subset',
        'H inverse = H/2 as an actual rational two-by-two matrix or equivalent typed finite scalar contraction'],
    'dev_boundary': 'Complete Lean file with all three exact fixed statements, compiler exit zero and printed axioms',
    'test_boundary': 'Coordinator fresh checkout of exact committed source, Lean compilation and independent axiom audit',
    'metric': 'fraction of three fixed helper obligations accepted; root score remains zero',
    'candidate_limit': 5,
    'global_formal_budget_note': '13 full compiler invocations in current window already used, including exact root and delivered replays; reserve five candidates and two fresh/delivered replays, total at most twenty.',
    'forbidden': ['native_decide', 'new axioms', 'sorryAx', 'defining Pfaffian signature as EVEN4 without its explicit matching polynomials', 'assuming global Gaussian closure'],
    'root_conjecture_verified': False}
(worktree / 'n67-protocol.json').write_text(json.dumps(contract, indent=2), encoding='utf-8')
subprocess.run([sys.executable, str(tree), '--run-dir', str(repo), 'set-status', '--node', 'n67',
    '--status', 'running'], check=True)
print(json.dumps({'node': 'n67', 'worktree': str(worktree), 'root_conjecture_verified': False}))

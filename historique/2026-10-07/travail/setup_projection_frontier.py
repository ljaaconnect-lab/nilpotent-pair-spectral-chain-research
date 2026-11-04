import json
import random
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

root = Path(__file__).resolve().parent
repo = root / 'research'
git = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
tree = Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
path = repo / '.arbor/run.json'
state = json.loads(path.read_text(encoding='utf-8'))
state['budget_cycles'] = 20
state['continuation_authorization'] = 'User: continue de chercher une construction positive. Extend the positive projection frontier; preserve original root, metrics and existing evidence.'
path.write_text(json.dumps(state, indent=2), encoding='utf-8')
for node, hypothesis in (
    ('n65', 'Bounded-spectrum inversion-operator jet recurrence with charged scalar states'),
    ('n66', 'Structured auxiliary Pfaffian gadget for synchronized paired-port projection')):
    worktree = root / ('wt-' + node)
    subprocess.run([str(git), '-c', 'safe.directory=' + repo.as_posix(), '-C', str(repo),
        'worktree', 'add', '-b', 'arbor/' + node, str(worktree),
        'c785376a2d255cc76db771d239c86c89cc7b888f'], check=True)
    contract = {'node': node, 'hypothesis': hypothesis,
        'dev_boundary': 'Scalar graph or fixed structured matrix candidate on formal input entries n=2,3,4,5, only positive identity checks; full fan-in-two gate accounting',
        'test_boundary': 'Coordinator fresh checkout of committed candidate; new fixed rational matrices with independent exact scalar interpreter and direct finite target oracle',
        'score_definition': 'Three obligations: correct explicit scalar data and transition; polynomial gate/literal/initialization certificate; exact root-target identity. Report each as proved, finite-only or unclosed. Local numeric score does not close root.',
        'positive_only': True,
        'forbidden': ['counterexample campaigns', 'lower-bound experiments', 'free differential operators', 'free paired projection', 'unknown target in initialization', 'assuming existence of polynomial representation'],
        'root_conjecture_verified': False}
    (worktree / (node + '-protocol.json')).write_text(json.dumps(contract, indent=2), encoding='utf-8')
    subprocess.run([sys.executable, str(tree), '--run-dir', str(repo), 'set-status', '--node', node,
        '--status', 'running'], check=True)

boundary = root / 'test-boundary/projection-frontier-heldout.json'
if boundary.exists():
    raise SystemExit('Refusing to replace boundary')
rng = random.Random(105066027)
cases = []
for n in range(2, 6):
    for case in range(4):
        A = [[str(Fraction(rng.randint(-7, 7), rng.randint(1, 7))) for _ in range(n)] for _ in range(n)]
        cases.append({'n': n, 'A': A})
boundary.write_text(json.dumps({'id': 'projection-frontier-positive-v1', 'seed': 105066027,
    'cases': cases, 'scope': 'Final scalar target only; root controlled; fresh candidate frozen before boundary read'}, indent=2), encoding='utf-8')
subprocess.run([sys.executable, str(tree), '--run-dir', str(repo), 'cycle'], check=True)
print(json.dumps({'nodes': ['n65', 'n66'], 'heldout_cases': len(cases), 'root_conjecture_verified': False}))

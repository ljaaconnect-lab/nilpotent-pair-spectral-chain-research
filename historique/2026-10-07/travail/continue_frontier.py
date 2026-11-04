import json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
REPO = ROOT / 'research'
TREE = Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
GIT = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')

def tree(*args):
    result = subprocess.run([sys.executable, str(TREE), '--run-dir', str(REPO), *args],
                            text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    print(result.stdout.strip(), flush=True)
    return result.stdout

tree('set-evidence', '--node', 'n15', '--dev-score', '1', '--branch-ref',
     'a3a6f044243d4006ba2c3a8a9d9577d13d9d806c', '--result',
     '28/28 frozen constructive half-character tests n=2..5; actual gates 18,54,124,260; root unproved',
     '--insight', 'Half-character polarization supplies cheap initial data and diagonal factors; its explicit scalar contraction is still exponential')
tree('propagate', '--node', 'n15', '--insight',
     'A positive half-character formula has cheap explicit initial data; compression of its scalar contraction remains an independent obligation')
tree('set-evidence', '--node', 'n16', '--dev-score', '1', '--branch-ref',
     'ba86cbd596588993b2061db0f033ec8e5b58fac4', '--result',
     '20/20 generic symbolic tests n=2..5; initialized order-n reciprocal recurrence, native gates 30,129,404,1005; projection compilation unproved',
     '--insight', 'The reciprocal determinant gives a cheap small companion recurrence over auxiliary variables; the squarefree contraction requires its own scalar compilation theorem')
tree('propagate', '--node', 'n16', '--insight',
     'A small initialized recurrence over auxiliary variables does not yet compile the required diagonal functional; charge that projection separately')

nodes = [
    ('n15', 'Constructive Cauchy-Binet and Hadamard determinant pair factorization with scalar gate counts and no uncharged contraction', 'a3a6f044243d4006ba2c3a8a9d9577d13d9d806c'),
    ('n16', 'Constructive mixed-derivative propagation for the reciprocal determinant: search a compact chain with explicit initial data and charged scalar states', 'ba86cbd596588993b2061db0f033ec8e5b58fac4'),
]
created = []
for parent, hypothesis, ref in nodes:
    state = json.loads((REPO / '.arbor' / 'tree.json').read_text())
    existing = [n['id'] for n in state['nodes'].values()
                if n.get('parent') == parent and n.get('hypothesis') == hypothesis]
    if existing:
        node = existing[0]
    else:
        output = tree('add-node', '--parent', parent, '--hypothesis', hypothesis)
        match = re.search(r'node (n\d+)', output)
        if not match:
            raise RuntimeError(output)
        node = match.group(1)
    wt = ROOT / ('wt-' + node)
    result = subprocess.run([str(GIT), '-c', 'safe.directory=' + REPO.as_posix(),
                             '-C', str(REPO), 'worktree', 'add', '-b',
                             'arbor/' + node, str(wt), ref], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    tree('set-status', '--node', node, '--status', 'running')
    created.append({'node': node, 'parent': parent, 'worktree': str(wt), 'base': ref})
tree('cycle')
(ROOT / 'cycle6-dispatch.json').write_text(json.dumps(created, indent=2))
print(json.dumps(created, indent=2), flush=True)

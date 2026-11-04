"""Independent checkout, kernel replay, and serial hypothesis ledger update."""
import hashlib, json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
REPO = ROOT / 'research'
GATE = ROOT / 'gate-n17'
GIT = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
LEAN = Path('C:/Users/REGIS/Documents/Codex/runtimes/elan/toolchains/leanprover--lean4---v4.34.1/bin/lean.exe')
TREE = Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
REF = 'b12329e5416a4bfc253ac948a3994d86382e64e7'

def run(args, cwd=REPO):
    result = subprocess.run(list(map(str, args)), cwd=cwd, capture_output=True,
                            text=True, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result

def tree(*args):
    return run([sys.executable, TREE, '--run-dir', REPO, *args]).stdout

if not GATE.exists():
    run([GIT, '-c', 'safe.directory=' + REPO.as_posix(), '-C', REPO,
         'worktree', 'add', '--detach', GATE, REF])
report = {'node': 'n17', 'commit': REF, 'root_conjecture_verified': False,
          'global_compiler_rounds_after_replay': 38, 'sources': []}
entries = []
for filename in ['GeneralPairing.lean', 'GeneralPairingRing.lean']:
    path = GATE / filename
    result = run([LEAN, path], GATE)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    report['sources'].append({'file': filename, 'sha256': sha, 'exit_code': result.returncode,
                             'stdout': result.stdout, 'stderr': result.stderr})
    assert 'sorryAx' not in result.stdout
    for name, text in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", result.stdout):
        axioms = {s.strip() for s in text.split(',') if s.strip()}
        assert axioms <= {'propext', 'Classical.choice', 'Quot.sound'}, (name, axioms)
        entries.append({'theorem': name, 'source': filename, 'source_sha256': sha,
                        'axioms': sorted(axioms), 'branch_ref': REF,
                        'verification': 'kernel-accepted supporting theorem; root unproved',
                        'dev_score': 1.0, 'test_score': 1.0})
assert len(entries) == 18
report['accepted_declarations'] = len(entries)
(ROOT / 'general-pairing-replay.json').write_text(json.dumps(report, indent=2))
tree('set-evidence', '--node', 'n17', '--dev-score', '1', '--branch-ref', REF,
     '--result', '18 accepted declarations in Rat and arbitrary commutative ring; executor and independent replay exit0, no sorryAx; polynomial extraction unproved',
     '--insight', 'Central sign pairing is proved for actual sparse products, arbitrary distinct bounded labels and arbitrary ring weights; retain every hypothesis in determinant specialization')
tree('merge', '--node', 'n17', '--test-score', '1', '--branch-ref', REF)
tree('propagate', '--node', 'n17', '--insight',
     'A kernel-verified general coefficient identity now supports arbitrary coefficient rings; remaining work is determinant specialization and scalar extraction compilation')
ledger_path = REPO / '.arbor' / 'verified-bases.json'
ledger = json.loads(ledger_path.read_text())
for entry in entries:
    existing = [e for e in ledger['entries'] if e['theorem'] == entry['theorem']]
    if existing:
        assert existing[0]['source_sha256'] == entry['source_sha256']
        continue
    output = tree('add-node', '--parent', 'n17', '--hypothesis',
                  'Verified Base Axiom (proved helper): ' + entry['theorem'])
    match = re.search(r'node (n\d+)', output)
    assert match, output
    entry['node_id'] = match.group(1)
    tree('set-evidence', '--node', entry['node_id'], '--dev-score', '1', '--branch-ref', REF,
         '--result', 'Exact committed source accepted by executor and independent compiler replay, no sorryAx',
         '--insight', 'Reuse this compiled statement with all original assumptions; no new axiom asserting polynomial extraction')
    tree('merge', '--node', entry['node_id'], '--test-score', '1', '--branch-ref', REF)
    ledger['entries'].append(entry)
ledger['accepted_declarations'] = len(ledger['entries'])
ledger_path.write_text(json.dumps(ledger, indent=2))
print(json.dumps({'exit_codes': [s['exit_code'] for s in report['sources']],
                  'accepted_declarations': len(entries), 'global_rounds': 38,
                  'verified_ledger_total': len(ledger['entries'])}), flush=True)

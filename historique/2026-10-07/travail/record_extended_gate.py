from pathlib import Path
import json, subprocess, sys
ROOT = Path(__file__).resolve().parent
TREE = Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
REPO = ROOT / 'research'
report = json.loads((ROOT / 'extended-positive-test-report.json').read_text())
assert report['passed'] == report['total'] == 48
for node in ['n15', 'n16', 'n18', 'n19']:
    ref = report['artifact_refs'][node]
    result = subprocess.run([sys.executable, str(TREE), '--run-dir', str(REPO),
                             'merge', '--node', node, '--test-score', '1', '--branch-ref', ref],
                            text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    print(result.stdout.strip(), flush=True)
for node, lesson in [('n18', 'The Gram determinant supplies a cheaper exact scalar coefficient encoding; no final contraction is counted as a free gate'),
                     ('n19', 'Initialized nilpotent row updates yield cheaper auxiliary circuits and actual emitted derivative DAGs; uniform polynomial scalar extraction remains the target')]:
    result = subprocess.run([sys.executable, str(TREE), '--run-dir', str(REPO),
                             'propagate', '--node', node, '--insight', lesson],
                            text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    print(result.stdout.strip(), flush=True)

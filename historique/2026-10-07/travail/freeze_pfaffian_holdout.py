import hashlib
import json
import random
from pathlib import Path

root = Path(__file__).resolve().parent
path = root / 'test-boundary/pfaffian-local-heldout.json'
if path.exists():
    raise SystemExit('Refusing to replace an existing held-out boundary')
rng = random.Random(105064027)
cases = []
for n in (6, 7, 8):
    for k in range(8):
        size = min(k, n)
        rows = sorted(rng.sample(range(n), size))
        columns = rng.sample(range(n), size)
        cases.append({'n': n, 'edges': list(map(list, zip(rows, columns)))})
boundary = {'id': 'n64-positive-local-v1', 'seed': 105064027,
    'scope': 'Local coefficient identities only; not a global extractor or asymptotic proof',
    'cases': cases, 'root_conjecture_verified': False}
path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps(boundary, indent=2), encoding='utf-8')
digest = hashlib.sha256(path.read_bytes()).hexdigest()
(root / 'n64-heldout-freeze.json').write_text(json.dumps({'path': str(path),
    'sha256': digest, 'case_count': len(cases), 'frozen_before_candidate_tests': True}, indent=2), encoding='utf-8')
print(json.dumps({'boundary_sha256': digest, 'cases': len(cases)}))

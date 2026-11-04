"""Replay delivered sources using the pinned local Lean/Mathlib environment."""
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--lean', type=Path, default=Path('C:/Users/REGIS/Documents/Codex/runtimes/elan/toolchains/leanprover--lean4---v4.34.1/bin/lean.exe'))
parser.add_argument('--cache', type=Path, default=PACKAGE.parent.parent/'work/delivered-proof-cache')
args = parser.parse_args()
assert args.lean.is_file(), args.lean
manifest = json.loads((PACKAGE/'manifest-sha256.json').read_text(encoding='utf-8'))
ledger = json.loads((PACKAGE/'arbor/verified-bases.json').read_text(encoding='utf-8'))
env = os.environ.copy()
env.update(json.loads((PACKAGE/'verification/mathlib-environment-local.json').read_text(encoding='utf-8')))
args.cache.mkdir(parents=True, exist_ok=True)
env['LEAN_PATH'] = str(args.cache.resolve())+os.pathsep+env['LEAN_PATH']
proofs = PACKAGE/'proofs'
files = {p.name:p for p in proofs.glob('*.lean')}
dependencies = {}
for name,p in files.items():
    modules = [m for line in re.findall(r'^import\s+([^\r\n]+)', p.read_text(encoding='utf-8'), re.MULTILINE)
               for m in line.split('--')[0].split()]
    dependencies[name] = {m+'.lean' for m in modules if m+'.lean' in files}
order = []
while len(order) < len(files):
    ready = sorted(name for name in files if name not in order and dependencies[name] <= set(order))
    assert ready, 'A cycle exists among the delivered proof imports'
    order.extend(ready)
report = {'root_conjecture_verified':False, 'sources':[]}
for filename in order:
    p = proofs/filename
    if not p.exists():
        continue
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest == manifest['proofs/'+filename]
    text = p.read_text(encoding='utf-8')
    assert not re.search(r'\b(sorry|admit|native_decide)\b|(?m:^\s*(axiom|unsafe)\s)', text)
    result = subprocess.run([str(args.lean), '-o', str(args.cache/p.with_suffix('.olean').name), str(p)],
                            cwd=proofs, env=env, capture_output=True, text=True, encoding='utf-8', timeout=180)
    audit = {}
    for name, values in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", result.stdout):
        audit[name] = sorted({v.strip() for v in values.split(',') if v.strip()})
    for name in re.findall(r"'([^']+)' does not depend on any axioms", result.stdout):
        audit[name] = []
    record = {'source':filename, 'source_sha256':digest, 'exit_code':result.returncode,
              'stdout':result.stdout, 'stderr':result.stderr, 'axiom_audit':audit}
    report['sources'].append(record)
    (args.cache/'replay-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    assert result.returncode == 0, result.stdout+result.stderr
    assert all(set(values) <= {'propext','Classical.choice','Quot.sound'} for values in audit.values())
    expected = {e['theorem'] for e in ledger['entries'] if e['source'] == filename}
    assert expected <= set(audit), (filename, expected-set(audit))
    print(json.dumps({'source':filename, 'exit_code':0, 'audited_declarations':len(audit)}),flush=True)
print(json.dumps({'all_sources_verified':True, 'root_conjecture_verified':False}),flush=True)

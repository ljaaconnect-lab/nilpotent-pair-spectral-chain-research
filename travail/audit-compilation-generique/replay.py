"""Replay three unchanged historical Lean sources with isolated build products."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES = ROOT / 'etudes/2026-10-07/livrables/conjecture-1-5-suite/proofs'
HELPER = ROOT / 'etudes/2026-11-01/lean-operateurs/lean_check.py'
spec = importlib.util.spec_from_file_location('historical_lean_environment', HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
env = helper.environment()
env['LEAN_PATH'] = str(HERE / 'build') + os.pathsep + str(HERE / 'sources') + os.pathsep + env['LEAN_PATH']
(HERE / 'build').mkdir(exist_ok=True)
(HERE / 'sources').mkdir(exist_ok=True)
version = subprocess.run([str(helper.LEAN), '--version'], capture_output=True, text=True, encoding='utf-8', env=env, cwd=HERE)
report = {'status': 'running', 'compiler': str(helper.LEAN), 'version_stdout': version.stdout,
          'version_stderr': version.stderr, 'version_exit_code': version.returncode,
          'environment_helper': str(HELPER),
          'environment': {k: env[k] for k in ['LEAN_PATH', 'LEAN_SRC_PATH', 'LEAN_SYSROOT']},
          'proof_changes': False, 'historical_report_changes': False, 'runs': []}
target = HERE / 'replay.json'
target.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
assert version.returncode == 0 and '4.34.1' in version.stdout, version.stdout + version.stderr
for name in ['PowerCompiler.lean', 'MatrixScalarCompiler.lean', 'ConditionalCriterion.lean']:
    original = SOURCES / name
    data = original.read_bytes()
    snapshot = HERE / 'sources' / name
    snapshot.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    command = [str(helper.LEAN), '-j1', '-o', str(HERE / 'build' / (snapshot.stem+'.olean')), str(snapshot)]
    started = time.monotonic()
    run = subprocess.run(command, cwd=HERE / 'sources', env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
    output = run.stdout + run.stderr
    audit = {n: [a.strip() for a in ax.split(',') if a.strip()] for n, ax in
             re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", output)}
    audit.update({n: [] for n in re.findall(r"'([^']+)'\s+does not depend on any axioms", output)})
    changed = original.read_bytes() != data or snapshot.read_bytes() != data
    good = run.returncode == 0 and not changed and 'sorryAx' not in output and 'warning:' not in output
    good = good and all(set(axioms) <= {'propext', 'Quot.sound', 'Classical.choice'} for axioms in audit.values())
    result = {'source': str(original), 'snapshot': str(snapshot), 'sha256': digest,
              'lf_normalized_sha256': hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest(),
              'command': command, 'cwd': str(HERE / 'sources'),
              'elapsed_seconds': round(time.monotonic()-started, 3),
              'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr,
              'axiom_audit': audit, 'source_changed': changed, 'status': 'passed' if good else 'failed'}
    report['runs'].append(result)
    report['status'] = 'running' if good else 'failed'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['source', 'status', 'exit_code', 'elapsed_seconds', 'sha256']}, ensure_ascii=False), flush=True)
    if not good:
        print(output, flush=True)
        raise SystemExit(1)
report['status'] = 'passed'
target.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('All three unchanged sources passed.', flush=True)

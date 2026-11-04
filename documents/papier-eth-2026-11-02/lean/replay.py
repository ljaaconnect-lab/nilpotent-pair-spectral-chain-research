"""Replay the local finite difference readout, with build products on D:."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import shutil
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HELPER = ROOT / 'etudes/2026-11-01/lean-operateurs/lean_check.py'
spec = importlib.util.spec_from_file_location('existing_lean_environment', HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
SOURCE = HERE / 'FiniteDifferenceReadout.lean'
BUILD = ROOT / 'travail/papier-eth-finite-difference'
DEPENDENCY = HERE / 'deps/ForwardDiffLocal.lean'
DEPENDENCY_ORIGIN = 'Mathlib/Algebra/Group/ForwardDiff.lean from the project mathlib environment (Lean 4.34.1); MIT license and authors retained verbatim.'

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    BUILD.mkdir(parents=True, exist_ok=True)
    dep_digest = hashlib.sha256(DEPENDENCY.read_bytes()).hexdigest()
    dep_source = BUILD / 'ForwardDiffLocal.lean'
    dep_object = BUILD / 'ForwardDiffLocal.olean'
    dep_report = BUILD / 'dependency-validation.json'
    env = helper.environment()
    env['LEAN_PATH'] = str(BUILD) + ';' + env['LEAN_PATH']
    cached = json.loads(dep_report.read_text(encoding='utf-8')) if dep_report.exists() else {}
    if not dep_object.exists() or cached.get('source_sha256') != dep_digest or cached.get('exit_code') != 0:
        shutil.copyfile(DEPENDENCY, dep_source)
        dep_cmd = [str(helper.LEAN), '-j1', '-o', str(dep_object), str(dep_source)]
        dep_result = subprocess.run(dep_cmd, cwd=BUILD, env=env, capture_output=True,
                                    text=True, encoding='utf-8', errors='replace')
        cached = {'original_source': DEPENDENCY_ORIGIN, 'source_sha256': dep_digest,
                  'source_copy_identical': dep_source.read_bytes() == DEPENDENCY.read_bytes(),
                  'exit_code': dep_result.returncode, 'command': dep_cmd,
                  'stdout': dep_result.stdout, 'stderr': dep_result.stderr}
        dep_report.write_text(json.dumps(cached, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        if dep_result.returncode:
            print(dep_result.stdout, end='')
            print(dep_result.stderr, end='', file=sys.stderr)
            return dep_result.returncode
    cached['original_source'] = DEPENDENCY_ORIGIN
    cached['bundled_source'] = str(DEPENDENCY)
    cached['bundled_source_sha256'] = dep_digest
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    cmd = [str(helper.LEAN), '-j1', '-o', str(BUILD / 'FiniteDifferenceReadout.olean'), str(SOURCE)]
    start = time.monotonic()
    result = subprocess.run(cmd, cwd=HERE, env=env, capture_output=True,
                            text=True, encoding='utf-8', errors='replace')
    report = {
        'scope': 'Local division-free polynomial readout identity only. No bound for constructing the sampled polynomial values is assumed or proved.',
        'source': str(SOURCE), 'source_sha256': digest,
        'source_changed_during_check': hashlib.sha256(SOURCE.read_bytes()).hexdigest() != digest,
        'replay_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'command': cmd, 'exit_code': result.returncode,
        'dependency': cached,
        'seconds': round(time.monotonic() - start, 3),
        'stdout': result.stdout, 'stderr': result.stderr,
    }
    (HERE / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(result.stdout, end='')
    print(result.stderr, end='', file=sys.stderr)
    print(json.dumps({k: v for k, v in report.items() if k not in ('stdout', 'stderr')}, ensure_ascii=False))
    return result.returncode

if __name__ == '__main__':
    raise SystemExit(main())

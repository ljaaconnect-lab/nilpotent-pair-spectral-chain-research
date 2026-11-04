"""Replay local polynomial degree-transfer lemmas; store build products on D:."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HELPER = ROOT / 'etudes/2026-11-01/lean-operateurs/lean_check.py'
spec = importlib.util.spec_from_file_location('existing_lean_environment', HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
SOURCE = HERE / 'DegreeBarrier.lean'
BUILD = ROOT / 'travail/deformations-existence-degree-barrier'

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    BUILD.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    cmd = [str(helper.LEAN), '-j1', '-o', str(BUILD / 'DegreeBarrier.olean'), str(SOURCE)]
    start = time.monotonic()
    result = subprocess.run(cmd, cwd=HERE, env=helper.environment(), capture_output=True,
                            text=True, encoding='utf-8', errors='replace')
    report = {
        'scope': 'Degree transfer from a supplied polynomial identity and numerical interpolation obstruction only. Invariant existence, semistability, Kempf theory, determinant rank-drop multiplicities, and scalar-circuit bounds are not formalized.',
        'source': str(SOURCE), 'source_sha256': digest,
        'source_changed_during_check': hashlib.sha256(SOURCE.read_bytes()).hexdigest() != digest,
        'replay_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'command': cmd, 'exit_code': result.returncode,
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

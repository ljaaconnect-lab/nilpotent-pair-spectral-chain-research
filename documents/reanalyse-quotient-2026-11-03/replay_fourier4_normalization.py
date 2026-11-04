"""Replay the n=2,N=4 reduction directly from convolution and padding."""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
SOURCE = HERE / 'Fourier4Normalization.lean'
HELPER = PROJECT / 'etudes/2026-11-01/lean-operateurs/lean_check.py'
BUILD = PROJECT / 'travail/audit-compilation-generique/build'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('fourier4_environment', HELPER)
    assert spec and spec.loader
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    env = helper.environment()
    env['LEAN_PATH'] = str(BUILD) + os.pathsep + env.get('LEAN_PATH', '')
    raw = SOURCE.read_bytes()
    source_text = raw.decode('utf-8')
    names = re.findall(r'^theorem\s+(\w+)', source_text, re.MULTILINE)
    before = sha256(raw).hexdigest()
    command = [str(helper.LEAN), '-j1', str(SOURCE)]
    started = time.monotonic()
    run = subprocess.run(command, cwd=HERE, env=env,
                         capture_output=True, encoding='utf-8', errors='replace')
    output = run.stdout + run.stderr
    unchanged = sha256(SOURCE.read_bytes()).hexdigest() == before
    complete_audit = all(f'Fourier4Normalization.{name}' in output for name in names)
    placeholders_absent = re.search(r'\b(?:sorry|admit|axiom)\b', source_text) is None
    clean = (run.returncode == 0 and unchanged and complete_audit and placeholders_absent
             and 'warning:' not in output and 'sorryAx' not in output)
    report = {
        'status': 'passed' if clean else 'failed', 'date': '2026-11-03',
        'command': command, 'source': SOURCE.name, 'source_sha256': before,
        'replay_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'environment_helper': str(HELPER),
        'environment_helper_sha256': sha256(HELPER.read_bytes()).hexdigest(),
        'imported_circuit_olean_sha256': sha256((BUILD / 'MatrixScalarCompiler.olean').read_bytes()).hexdigest(),
        'source_changed_during_check': not unchanged, 'exit_code': run.returncode,
        'seconds': round(time.monotonic() - started, 3),
        'stdout': run.stdout, 'stderr': run.stderr, 'theorems': names,
        'all_theorem_axioms_printed': complete_audit,
        'source_has_no_placeholders_or_added_axioms': placeholders_absent,
        'scope': 'Exact n=2,N=4 normalization in an arbitrary commutative algebra, directly from the four convolution relations and two padding relations.',
        'coefficient_circuit': 'B00*B11+B01*B10',
        'scalar_gates_from_B': 3,
        'auxiliary_coordinates_inverted': False,
        'ambient_ring_may_contain_nilpotents': True,
        'general_polynomial_bound_proved': False,
    }
    if args.write_report:
        version = subprocess.run([str(helper.LEAN), '--version'], capture_output=True,
                                 encoding='utf-8', errors='replace', check=True)
        report['lean_version'] = version.stdout.strip()
        (HERE / 'fourier4-lean-validation.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({'status': report['status'], 'theorems_checked': len(names),
                      'scope': report['scope']}, ensure_ascii=False))
    return 0 if clean else 1


if __name__ == '__main__':
    raise SystemExit(main())

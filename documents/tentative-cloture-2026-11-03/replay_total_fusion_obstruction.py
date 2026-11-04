"""Replay the native two-row counterexample to a reader of the fused sum alone."""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
SOURCE = HERE / 'TotalFusionObstruction.lean'
HELPER = PROJECT / 'etudes/2026-11-01/lean-operateurs/lean_check.py'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('total_fusion_environment', HELPER)
    assert spec and spec.loader
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    raw = SOURCE.read_bytes()
    source_text = raw.decode('utf-8')
    names = re.findall(r'^theorem\s+(\w+)', source_text, re.MULTILINE)
    before = sha256(raw).hexdigest()
    command = [str(helper.LEAN), '-j1', str(SOURCE)]
    started = time.monotonic()
    run = subprocess.run(command, cwd=HERE, env=helper.environment(),
                         capture_output=True, encoding='utf-8', errors='replace')
    output = run.stdout + run.stderr
    unchanged = sha256(SOURCE.read_bytes()).hexdigest() == before
    complete_audit = all(f'TotalFusionObstruction.{name}' in output for name in names)
    placeholders_absent = re.search(r'\b(?:sorry|admit|axiom)\b', source_text) is None
    clean = (run.returncode == 0 and unchanged and complete_audit and placeholders_absent
             and 'warning:' not in output and 'sorryAx' not in output)
    report = {
        'status': 'passed' if clean else 'failed', 'date': '2026-11-03',
        'command': command, 'source': SOURCE.name, 'source_sha256': before,
        'replay_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'environment_helper': str(HELPER),
        'environment_helper_sha256': sha256(HELPER.read_bytes()).hexdigest(),
        'source_changed_during_check': not unchanged, 'exit_code': run.returncode,
        'seconds': round(time.monotonic() - started, 3),
        'stdout': run.stdout, 'stderr': run.stderr, 'theorems': names,
        'all_theorem_axioms_printed': complete_audit,
        'source_has_no_placeholders_or_added_axioms': placeholders_absent,
        'scope': 'Concrete obstruction to a reader depending only on u+v, including native rows at z=1; no claim against other circuits.',
        'field': 'ZMod 97',
        'D': 'D(x,y)=x*y',
        'delta': 'D(u+v)-D(u)-D(v)+D(0)=u0*v1+u1*v0',
        'examples': {
            'left_rows': [[1, 5], [5, 1]],
            'right_rows': [[3, 3], [3, 3]],
            'native_left_a': [0, 2, 2, 0],
            'native_right_a': [14, 14, 14, 14],
            'z': 1, 'same_sum': [6, 6], 'different_delta': [26, 18],
        },
        'general_polynomial_circuit_impossibility_claimed': False,
        'other_state_representations_excluded': False,
        'native_polynomial_bound_proved': False,
    }
    if args.write_report:
        version = subprocess.run([str(helper.LEAN), '--version'], capture_output=True,
                                 encoding='utf-8', errors='replace', check=True)
        report['lean_version'] = version.stdout.strip()
        (HERE / 'total-fusion-lean-validation.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({'status': report['status'], 'theorems_checked': len(names),
                      'scope': report['scope']}, ensure_ascii=False))
    return 0 if clean else 1


if __name__ == '__main__':
    raise SystemExit(main())

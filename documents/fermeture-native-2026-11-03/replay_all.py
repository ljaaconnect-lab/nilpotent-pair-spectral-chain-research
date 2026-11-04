"""Rebuild the closure modules in dependency order and check the joint theorem.

Requires the project's Lean/Mathlib environment and MatrixScalarCompiler cache.
The report proves the stated conditional closure, not native normalization.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
BUILD = PROJECT / 'travail/fermeture-native/build'
HELPER = PROJECT / 'etudes/2026-11-01/lean-operateurs/lean_check.py'
COST = PROJECT / 'documents/induction-native-2026-11-03/SharedCostInduction.lean'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    spec = importlib.util.spec_from_file_location('closure_environment', HELPER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    BUILD.mkdir(parents=True, exist_ok=True)
    sources = sorted(HERE.glob('*.lean')) + sorted(HERE.glob('*.py')) + [COST, HELPER]

    def hashes():
        return {p.relative_to(PROJECT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sources}

    before = hashes()
    script_args = [
        ('replay_auxiliary_erasure.py', ['--write-report']),
        ('replay_shared_state.py', ['--write-report']),
        ('replay_terminal_label.py', ['--write-report']),
        ('replay_tagged_closure.py', []),
    ]
    commands = [[sys.executable, '-B', str(HERE / script), *args]
                for script, args in script_args]
    commands += [
        [str(helper.LEAN), '-j1', '-o', str(BUILD / 'SharedCostInduction.olean'), str(COST)],
        [sys.executable, '-B', str(HERE / 'replay_certified_closure.py')],
    ]
    runs = []
    start = time.monotonic()
    for command in commands:
        result = subprocess.run(command, cwd=PROJECT, env=helper.environment(),
                                capture_output=True, encoding='utf-8', errors='replace')
        output = result.stdout + result.stderr
        clean = result.returncode == 0 and 'warning:' not in output and 'sorryAx' not in output
        runs.append({'command': command, 'exit_code': result.returncode,
                     'passed': clean, 'stdout': result.stdout, 'stderr': result.stderr})
        print(output, end='', flush=True)
        if not clean:
            break
    passed = len(runs) == len(commands) and all(r['passed'] for r in runs) and before == hashes()
    theorem_count = sum(len(re.findall(r'^theorem\s+', p.read_text(encoding='utf-8'), re.M))
                        for p in HERE.glob('*.lean'))
    report = {
        'status': 'passed' if passed else 'failed', 'date': '2026-11-03',
        'elapsed_seconds': round(time.monotonic() - start, 3),
        'new_closure_theorems': theorem_count,
        'reused_cost_induction_theorems': 6,
        'source_sha256': before, 'sources_unchanged': before == hashes(),
        'runs': runs,
        'normalization_is_a_hypothesis_of_scalar_readout': True,
        'general_native_normalization_constructed': False,
        'unconditional_native_scalar_polynomiality_proved': False,
    }
    (HERE / 'all-closure-lean-validation.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'closure_theorems': theorem_count}), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())

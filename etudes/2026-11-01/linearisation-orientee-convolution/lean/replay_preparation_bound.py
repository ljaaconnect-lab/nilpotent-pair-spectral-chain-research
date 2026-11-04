"""Replay only the arithmetic bound for the single-frequency preparation."""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
HELPER = HERE.parents[1] / 'lean-operateurs' / 'lean_check.py'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('linearised_bound_lean_environment', HELPER)
    assert spec and spec.loader
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source = HERE / 'LinearisedPreparationBound.lean'
    before = sha256(source.read_bytes()).hexdigest()
    run = subprocess.run([str(helper.LEAN), '-j1', str(source)], cwd=HERE,
                         env=helper.environment(), capture_output=True,
                         encoding='utf-8', errors='replace')
    output = run.stdout + run.stderr
    assert run.returncode == 0, output
    assert before == sha256(source.read_bytes()).hexdigest(), 'source changed during replay'
    assert 'warning:' not in output and 'sorryAx' not in output, output
    assert 'LinearisedPreparationBound.cubic_preparation_bound' in output, output
    report = {
        'status': 'passed',
        'compiler': str(helper.LEAN),
        'compiler_arguments': ['-j1'],
        'source': source.name,
        'sha256': before,
        'replay_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'exit_code': run.returncode,
        'stdout': run.stdout,
        'stderr': run.stderr,
        'scope': 'Arithmetic consequence of n>=1, N<=2*n and ell<=n',
        'formula': '4*n^2-1 + 2*n*N*ell + 3*n*N-1 <= 18*n^3',
        'single_frequency_preparation_only': True,
        'gate_count_derivation_formalized': False,
        'quotient_reader_cost_formalized': False,
        'complete_scalar_chain_polynomial_bound': False,
    }
    if args.write_report:
        (HERE / 'preparation-bound-lean-validation.json').write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({key: report[key] for key in
                      ('status', 'sha256', 'quotient_reader_cost_formalized')}))


if __name__ == '__main__':
    main()

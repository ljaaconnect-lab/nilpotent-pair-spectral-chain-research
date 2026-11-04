"""Replay the algebraic double-log identities with the local Lean kernel."""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
HELPER = HERE.parents[1] / 'lean-operateurs' / 'lean_check.py'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('double_log_lean_environment', HELPER)
    assert spec and spec.loader
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source = HERE / 'DoubleLogConjugation.lean'
    before = sha256(source.read_bytes()).hexdigest()
    run = subprocess.run([str(helper.LEAN), str(source)], cwd=HERE,
                         env=helper.environment(), capture_output=True,
                         encoding='utf-8', errors='replace')
    after = sha256(source.read_bytes()).hexdigest()
    output = run.stdout + run.stderr
    assert run.returncode == 0, output
    assert before == after, 'source changed during replay'
    assert 'warning:' not in output and 'sorryAx' not in output, output
    report = {
        'status': 'passed',
        'compiler': str(helper.LEAN),
        'source': source.name,
        'sha256': before,
        'exit_code': run.returncode,
        'stdout': run.stdout,
        'stderr': run.stderr,
        'scope': 'algebraic double-log conjugation for additive derivations',
        'analytic_logarithm_assumed': False,
        'full_chain_formalization': False,
        'general_polynomial_closure': False,
        'general_quasipolynomial_closure': False,
    }
    if args.write_report:
        (HERE / 'double-log-lean-validation.json').write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({k: report[k] for k in ('status', 'sha256',
                                          'general_polynomial_closure')}))


if __name__ == '__main__':
    main()

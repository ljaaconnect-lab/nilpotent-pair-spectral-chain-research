"""Replay the conditional arithmetic growth argument with the local Lean kernel."""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
HELPER = HERE.parents[2] / 'lean-operateurs' / 'lean_check.py'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('projection_growth_lean_environment', HELPER)
    assert spec and spec.loader
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source = HERE / 'ProjectionGrowth.lean'
    before = sha256(source.read_bytes()).hexdigest()
    run = subprocess.run([str(helper.LEAN), str(source)], cwd=HERE,
                         env=helper.environment(), capture_output=True,
                         encoding='utf-8', errors='replace')
    after = sha256(source.read_bytes()).hexdigest()
    output = run.stdout + run.stderr
    assert run.returncode == 0, output
    assert before == after, 'source changed during replay'
    assert 'warning:' not in output and 'sorryAx' not in output, output
    names = ('exponent_gap', 'exponential_beats_polynomial',
             'no_uniform_polynomial_bound')
    assert all('ProjectionGrowth.' + name in output for name in names), output
    report = {
        'status': 'passed',
        'compiler': str(helper.LEAN),
        'source': source.name,
        'sha256': before,
        'replay_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'exit_code': run.returncode,
        'stdout': run.stdout,
        'stderr': run.stderr,
        'scope': 'Natural-number growth and conditional exclusion of a uniform polynomial bound',
        'conditional_premise': 'For every k>=2, 2^(2^(k-1)) <= C(2^k)',
        'arithmetic_growth_formalized': True,
        'compiler_reachability_formalized': False,
        'general_scalar_circuit_impossibility': False,
        'theorems': list(names),
    }
    if args.write_report:
        (HERE / 'growth-lean-validation.json').write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({key: report[key] for key in
                      ('status', 'sha256', 'compiler_reachability_formalized')}))


if __name__ == '__main__':
    main()

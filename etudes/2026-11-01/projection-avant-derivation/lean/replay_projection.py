"""Replay the genuine derivative/evaluation identity for one projection.

An unchanged Mathlib source is compiled locally when its cached module is
unavailable. No dependency is downloaded or installed.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
HELPER = HERE.parents[1] / 'lean-operateurs' / 'lean_check.py'
DERIVATIVE_SHA256 = 'ab04d4335576e18032f8ed2c15f5bea04a9e0f44bcf15e5ac398a78a3056a5bb'


def checked_run(helper, command, cwd):
    run = subprocess.run(command, cwd=cwd, env=helper.environment(),
                         capture_output=True, encoding='utf-8', errors='replace')
    output = run.stdout + run.stderr
    assert run.returncode == 0, output
    assert 'warning:' not in output and 'sorryAx' not in output, output
    return run


def prepare_derivative(helper):
    original = helper.SOURCE_ENV.parent / 'mathlib/Mathlib/Algebra/Polynomial/Derivative.lean'
    original_bytes = original.read_bytes()
    original_hash = sha256(original_bytes).hexdigest()
    assert original_hash == DERIVATIVE_SHA256, 'Mathlib source differs from the validated version'
    local = helper.BUILD / 'LocalPolynomialDerivative.lean'
    compiled = helper.BUILD / 'local-cache/LocalPolynomialDerivative.olean'
    helper.BUILD.mkdir(parents=True, exist_ok=True)
    compiled.parent.mkdir(parents=True, exist_ok=True)
    source_matches = local.is_file() and local.read_bytes() == original_bytes
    rebuilt = not source_matches or not compiled.is_file()
    if source_matches and compiled.is_file():
        rebuilt = compiled.stat().st_mtime_ns < local.stat().st_mtime_ns
    if not source_matches:
        local.write_bytes(original_bytes)
    if rebuilt:
        checked_run(helper, [str(helper.LEAN), '-o', str(compiled), str(local)], helper.BUILD)
    assert local.read_bytes() == original_bytes
    artifacts = {p.name: sha256(p.read_bytes()).hexdigest()
                 for p in sorted(compiled.parent.glob('LocalPolynomialDerivative.*'))
                 if p.is_file()}
    return {
        'original_source': str(original), 'original_source_sha256': original_hash,
        'local_module': 'LocalPolynomialDerivative', 'source_copied_unchanged': True,
        'rebuilt_during_replay': rebuilt, 'compiled_artifact_sha256': artifacts,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('direct_projection_lean_environment', HELPER)
    assert spec and spec.loader
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    dependency = prepare_derivative(helper)
    source = HERE / 'Projection.lean'
    before = sha256(source.read_bytes()).hexdigest()
    run = checked_run(helper, [str(helper.LEAN), str(source)], HERE)
    assert before == sha256(source.read_bytes()).hexdigest(), 'source changed during replay'
    expected = ('DirectProjection.derivative_at_zero_eq_coeff_one',
                'DirectProjection.derivative_monomial_at_zero')
    assert all(name in run.stdout for name in expected), run.stdout
    report = {
        'status': 'passed', 'compiler': str(helper.LEAN),
        'source': source.name, 'sha256': before,
        'replay_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'dependency': dependency,
        'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr,
        'scope': 'Actual Mathlib formal derivative followed by evaluation at zero extracts coefficient one; general monomial filter over any coefficient semiring',
        'multivariate_compiler_formalized': False,
        'spectral_routing_formalized': False,
        'general_polynomial_closure': False,
        'general_scalar_circuit_lower_bound': False,
        'full_chain_formalization': False,
    }
    if args.write_report:
        (HERE / 'projection-lean-validation.json').write_text(
            json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(run.stdout, end='')
    print(json.dumps({k: report[k] for k in ('status', 'sha256', 'general_polynomial_closure')}))


if __name__ == '__main__':
    main()

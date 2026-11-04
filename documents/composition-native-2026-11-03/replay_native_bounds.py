"""Check natural-number bounds, not compilation or oriented scalarization."""
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
SOURCE = HERE / 'NativeCompositionBounds.lean'
HELPER = PROJECT / 'etudes/2026-11-01/lean-operateurs/lean_check.py'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('native_bounds_lean_environment', HELPER)
    assert spec and spec.loader
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source_bytes = SOURCE.read_bytes()
    source_text = source_bytes.decode('utf-8')
    names = re.findall(r'^theorem\s+(\w+)', source_text, re.MULTILINE)
    before = sha256(source_bytes).hexdigest()
    command = [str(helper.LEAN), '-j1', str(SOURCE)]
    started = time.monotonic()
    run = subprocess.run(command, cwd=HERE, env=helper.environment(),
                         capture_output=True, encoding='utf-8', errors='replace')
    output = run.stdout + run.stderr
    unchanged = sha256(SOURCE.read_bytes()).hexdigest() == before
    complete_audit = all(f'NativeCompositionBounds.{name}' in output for name in names)
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
        'scope': 'Natural-number inequalities conditional on externally justified gate counts.',
        'numeric_hypotheses': ['n >= 1', 'N <= 2*n', 'ell <= n', 'eps <= 1'],
        'bounds': {
            'typed_with_spectral': '6*n^2+n-2+eps+(2*N*ell+3*N-3) <= 17*n^2',
            'typed_routed': '6*n^2+n-2+eps <= 7*n^2',
            'representative_preparation': 'P = 4*n^2-2+2*n*N*ell+3*n*N <= 18*n^3',
            'representative_routed': 'P+eps <= 18*n^3+1',
            'representative_with_spectral': 'P+eps+(2*N*ell+3*N-3) <= 29*n^3',
        },
        'gate_count_hypotheses_are_external': True,
        'compiler_formalized': False,
        'gate_count_derivation_from_program_formalized': False,
        'typed_algebra_gates_identified_with_scalar_gates': False,
        'oriented_product_scalarization_proved': False,
        'auxiliary_variables_eliminated': False,
        'complete_scalar_chain_polynomial_bound_proved': False,
    }
    if args.write_report:
        (HERE / 'native-bounds-lean-validation.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({'status': report['status'], 'theorems_checked': len(names),
                      'scope': report['scope']}, ensure_ascii=False))
    return 0 if clean else 1


if __name__ == '__main__':
    raise SystemExit(main())

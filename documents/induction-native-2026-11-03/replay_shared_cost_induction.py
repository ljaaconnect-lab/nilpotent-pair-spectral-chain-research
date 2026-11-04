"""Replay conditional induction for shared scalar gate counts."""
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
SOURCE = HERE / 'SharedCostInduction.lean'
HELPER = PROJECT / 'etudes/2026-11-01/lean-operateurs/lean_check.py'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('shared_induction_environment', HELPER)
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
    complete_audit = all(f'SharedCostInduction.{name}' in output for name in names)
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
        'scope': 'Finite induction and polynomial consequences of supplied shared scalar increment bounds.',
        'state_semantics': 'S(i) counts the same accumulated circuit; increments count only newly added scalar gates.',
        'bounds': {
            'finite_accumulation': 'S(m) <= S(0) + sum_{i<m} increment(i)',
            'uniform_increment': 'S(m) <= S(0) + m*K*n^c',
            'two_term_polynomial': 'S(m) <= K0*n^a + A*K*n^(b+c)',
            'single_monomial': 'S(m) <= (K0+A*K)*n^max(a,b+c)',
            'family_constants': 'K0,A,K,a,b,c are quantified before n and are independent of n',
        },
        'hypotheses': [
            'For each i<m: S(i+1) <= S(i) + increment(i)',
            'Uniform variant: increment(i) <= K*n^c',
            'S(0) <= K0*n^a and m <= A*n^b',
            'n >= 1 for the single-monomial and family bounds',
            'Every increment concerns new scalar gates on compatible interfaces of the same shared circuit',
        ],
        'scalar_interface_compatibility_is_external': True,
        'native_increment_bound_proved': False,
        'native_compiler_formalized': False,
        'oriented_product_scalarization_proved': False,
        'complete_native_scalar_chain_polynomial_bound_proved': False,
    }
    if args.write_report:
        (HERE / 'shared-cost-induction-validation.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({'status': report['status'], 'theorems_checked': len(names),
                      'scope': report['scope']}, ensure_ascii=False))
    return 0 if clean else 1


if __name__ == '__main__':
    raise SystemExit(main())

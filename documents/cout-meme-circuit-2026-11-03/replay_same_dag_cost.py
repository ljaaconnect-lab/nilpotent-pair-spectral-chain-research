"""Replay exact gate-set accounting and its explicitly conditional polynomial bound."""
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
SOURCE = HERE / 'SameDAGCost.lean'
HELPER = PROJECT / 'etudes/2026-11-01/lean-operateurs/lean_check.py'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('same_dag_cost_environment', HELPER)
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
    complete_audit = all(f'SameDAGCost.{name}' in output for name in names)
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
        'scope': 'Exact set accounting for gates of the same supplied scalar DAG; polynomial consequence of one global joint remainder bound.',
        'gate_set_semantics': {
            'G': 'Final reachable ordinary +/* gates of the fixed graph.',
            'P': 'Actually constructed scalar coefficient prefix B -> C, in the same graph.',
            'J': 'card(G \\ P): all joint fusion/normalization/sign/spectral gates remaining in that graph.',
        },
        'bounds': {
            'exact_partition': 'card(G) = card(G intersect P) + card(G \\ P)',
            'coefficient_prefix': '4*n^2 - 1 + 2*n*N*ell + n*N <= 10*n^3',
            'conditional_total': 'J <= K*n^d implies card(G) <= (10+K)*n^max(3,d)',
            'family_constants': 'K and d are fixed outside the quantifier over n.',
        },
        'hypotheses': ['n >= 1', 'N <= 2*n', 'ell <= n',
                       'card(P) <= coefficientBound(n,N,ell)',
                       'jointCost(G,P) <= K*n^d'],
        'same_graph_interpretation_and_gate_set_extraction_external': True,
        'new_compiler_constructed': False,
        'separate_reader_or_intermediate_amplitude_required': False,
        'native_joint_gate_bound_proved': False,
        'complete_native_polynomial_bound_proved': False,
    }
    if args.write_report:
        version = subprocess.run([str(helper.LEAN), '--version'], capture_output=True,
                                 encoding='utf-8', errors='replace', check=True)
        report['lean_version'] = version.stdout.strip()
        (HERE / 'same-dag-cost-lean-validation.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({'status': report['status'], 'theorems_checked': len(names),
                      'scope': report['scope']}, ensure_ascii=False))
    return 0 if clean else 1


if __name__ == '__main__':
    raise SystemExit(main())

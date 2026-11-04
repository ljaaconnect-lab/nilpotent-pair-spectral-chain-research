"""Replay the augmentation obstruction to erasing a terminal basis label."""
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
SOURCE = HERE/'TerminalLabelNecessity.lean'
HELPER = PROJECT/'etudes/2026-11-01/lean-operateurs/lean_check.py'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('terminal_label_lean_environment', HELPER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source_text = SOURCE.read_text(encoding='utf-8')
    names = re.findall(r'^theorem\s+(\w+)', source_text, re.MULTILINE)
    sources = [SOURCE, Path(__file__), HELPER]

    def hashes():
        return {path.relative_to(PROJECT).as_posix(): sha256(path.read_bytes()).hexdigest()
                for path in sources}

    before = hashes()
    command = [str(helper.LEAN), '-j1', str(SOURCE)]
    started = time.monotonic()
    run = subprocess.run(command, cwd=HERE, env=helper.environment(), capture_output=True,
                         encoding='utf-8', errors='replace')
    output = run.stdout+run.stderr
    unchanged = before == hashes()
    no_placeholders = re.search(r'\b(?:sorry|admit|axiom)\b', source_text) is None
    all_printed = bool(names) and all(f'TerminalLabelNecessity.{name}' in output for name in names)
    clean = (run.returncode == 0 and unchanged and no_placeholders and all_printed
             and 'warning:' not in output and 'sorryAx' not in output)
    report = {
        'status': 'passed' if clean else 'incomplete_or_failed', 'date': '2026-11-03',
        'command': command, 'source_sha256': before, 'source_changed_during_check': not unchanged,
        'exit_code': run.returncode, 'seconds': round(time.monotonic()-started, 3),
        'stdout': run.stdout, 'stderr': run.stderr, 'theorems': names,
        'all_theorem_axioms_printed': all_printed,
        'source_has_no_placeholders_or_added_axioms': no_placeholders,
        'scope': 'An augmentation-kernel value has a scalar-embedded representative only when both are zero. A nonzero such value cannot be represented by an embedded scalar with its terminal label erased.',
        'augmentation_and_section_are_explicit_hypotheses': True,
        'application_to_specific_oriented_quotient_formalized': False,
        'terminal_coefficient_extraction_constructed': False,
        'auxiliary_erasure_of_oriented_value_asserted': False,
        'complete_scalar_chain_polynomial_bound_proved': False,
    }
    if args.write_report:
        if not clean:
            print(output, end='')
            return 1
        (HERE/'terminal-label-lean-validation.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({'status': report['status'], 'theorems': len(names),
                      'seconds': report['seconds']}, ensure_ascii=False))
    return int(not clean)


if __name__ == '__main__':
    raise SystemExit(main())

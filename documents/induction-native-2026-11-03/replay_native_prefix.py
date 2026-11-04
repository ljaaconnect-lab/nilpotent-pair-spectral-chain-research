"""Replay the actual prefix-program semantics, gate count and quotient transport."""
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
SOURCE = HERE/'NativePrefixInduction.lean'
HELPER = PROJECT/'etudes/2026-11-01/lean-operateurs/lean_check.py'
CACHE = PROJECT/'travail/audit-compilation-generique/build'
BUILD = PROJECT/'travail/induction-native/build'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('native_prefix_lean_environment', HELPER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    env = helper.environment()
    env['LEAN_PATH'] = str(CACHE)+';'+env['LEAN_PATH']
    source_text = SOURCE.read_text(encoding='utf-8')
    names = re.findall(r'^theorem\s+(\w+)', source_text, re.MULTILINE)
    sources = [SOURCE, Path(__file__), HELPER,
               CACHE/'MatrixScalarCompiler.olean', CACHE/'PowerCompiler.olean',
               PROJECT/'travail/audit-compilation-generique/sources/MatrixScalarCompiler.lean',
               PROJECT/'travail/audit-compilation-generique/sources/PowerCompiler.lean']
    def hashes():
        return {path.relative_to(PROJECT).as_posix(): sha256(path.read_bytes()).hexdigest()
                for path in sources}
    before = hashes()
    command = [str(helper.LEAN), '-j1']
    olean = BUILD/'NativePrefixInduction.olean'
    if args.write_report:
        BUILD.mkdir(parents=True, exist_ok=True)
        command += ['-o', str(olean)]
    command.append(str(SOURCE))
    started = time.monotonic()
    run = subprocess.run(command, cwd=HERE, env=env, capture_output=True,
                         encoding='utf-8', errors='replace')
    output = run.stdout + run.stderr
    unchanged = before == hashes()
    no_placeholders = re.search(r'\b(?:sorry|admit|axiom)\b', source_text) is None
    all_printed = all(f'NativePrefixInduction.{name}' in output for name in names)
    clean = (run.returncode == 0 and unchanged and no_placeholders and all_printed
             and 'warning:' not in output and 'sorryAx' not in output)
    report = {
        'status': 'passed' if clean else 'incomplete_or_failed', 'date': '2026-11-03',
        'command': command, 'source_sha256': before, 'source_changed_during_check': not unchanged,
        'exit_code': run.returncode, 'seconds': round(time.monotonic()-started, 3),
        'stdout': run.stdout, 'stderr': run.stderr, 'theorems': names,
        'all_theorem_axioms_printed': all_printed,
        'source_has_no_placeholders_or_added_axioms': no_placeholders,
        'scope': 'Shared prefix multiplication program, its evaluation and actual gate count, and semantic transport through a ring homomorphism.',
        'prefix_compiler_formalized': True,
        'prefix_gate_count_derived_from_program': True,
        'preparation_circuit_is_external_parameter': True,
        'quotient_homomorphism_is_semantic_not_a_gate': True,
        'auxiliary_variables_eliminated': False,
        'complete_scalar_a_z_only_compiler_formalized': False,
        'complete_scalar_chain_polynomial_bound_proved': False,
        'exact_prefix_gate_count': 'n-1',
        'exact_composed_gate_count': 'prepare.gates+(n-1)',
        'same_preparation_output_bundle_reused_by_every_prefix_gate': True,
        'import_cache': str(CACHE),
    }
    if args.write_report:
        if not clean:
            print(output, end='')
            return 1
        assert olean.is_file()
        report['olean'] = str(olean)
        report['olean_sha256'] = sha256(olean.read_bytes()).hexdigest()
        (HERE/'native-prefix-lean-validation.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({'status': report['status'], 'theorems': len(names),
                      'seconds': report['seconds']}, ensure_ascii=False))
    return run.returncode if not args.write_report else int(not clean)


if __name__ == '__main__':
    raise SystemExit(main())

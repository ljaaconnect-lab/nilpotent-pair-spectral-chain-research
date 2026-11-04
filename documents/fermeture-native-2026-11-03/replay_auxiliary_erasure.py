"""Replay explicit auxiliary erasure, conditional on fixed-semiring independence."""
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
SOURCE = HERE / 'AuxiliaryErasure.lean'
HELPER = PROJECT / 'etudes/2026-11-01/lean-operateurs/lean_check.py'
CACHE = PROJECT / 'travail/audit-compilation-generique/build'
BUILD = PROJECT / 'travail/fermeture-native/build'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('auxiliary_erasure_environment', HELPER)
    assert spec and spec.loader
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    env = helper.environment()
    env['LEAN_PATH'] = ';'.join([str(BUILD), str(CACHE), str(HERE), env['LEAN_PATH']])
    source_text = SOURCE.read_text(encoding='utf-8')
    names = re.findall(r'^theorem\s+(\w+)', source_text, re.MULTILINE)
    sources = [SOURCE, Path(__file__), HELPER,
               CACHE / 'MatrixScalarCompiler.olean', CACHE / 'PowerCompiler.olean',
               PROJECT / 'travail/audit-compilation-generique/sources/MatrixScalarCompiler.lean',
               PROJECT / 'travail/audit-compilation-generique/sources/PowerCompiler.lean']

    def hashes():
        return {p.relative_to(PROJECT).as_posix(): sha256(p.read_bytes()).hexdigest()
                for p in sources}

    before = hashes()
    command = [str(helper.LEAN), '-j1']
    olean = BUILD / 'AuxiliaryErasure.olean'
    if args.write_report:
        BUILD.mkdir(parents=True, exist_ok=True)
        command += ['-o', str(olean)]
    command.append(str(SOURCE))
    started = time.monotonic()
    run = subprocess.run(command, cwd=HERE, env=env, capture_output=True,
                         encoding='utf-8', errors='replace')
    output = run.stdout + run.stderr
    unchanged = before == hashes()
    placeholders_absent = re.search(r'\b(?:sorry|admit|axiom)\b', source_text) is None
    audited = all(f'AuxiliaryErasure.{name}' in output for name in names)
    clean = (run.returncode == 0 and unchanged and placeholders_absent and audited
             and 'warning:' not in output and 'sorryAx' not in output)
    report = {
        'status': 'passed' if clean else 'failed', 'date': '2026-11-03',
        'command': command, 'source_sha256': before,
        'source_changed_during_check': not unchanged, 'exit_code': run.returncode,
        'seconds': round(time.monotonic() - started, 3),
        'stdout': run.stdout, 'stderr': run.stderr, 'theorems': names,
        'all_theorem_axioms_printed': audited,
        'source_has_no_placeholders_or_added_axioms': placeholders_absent,
        'scope': 'An explicit same-size scalar circuit replacing all auxiliary inputs by zero; correctness when outputs are independent of them over the fixed semiring.',
        'exact_gate_count': 'eraseAux(c).gates = c.gates',
        'exact_semantics': 'eraseAux(c).eval(a) = c.eval(Sum.elim(a, zero))',
        'scalarization_witness': 'eraseAux(c), using only original input wires and zero constants',
        'tagged_terminal_application': 'Independence must hold for an explicit scalar coefficient b, not merely for an oriented homogeneous representative H supported on a fixed terminal label.',
        'formal_identity_policy': 'Choose the coefficient semiring R appropriate to the formal markers; finite-field pointwise equality is not promoted to a formal polynomial identity.',
        'erasure_circuit_formalized': True,
        'erasure_gate_count_derived_from_program': True,
        'auxiliary_independence_is_explicit_hypothesis': True,
        'independence_semiring_is_fixed': True,
        'auxiliary_index_nonempty_required': False,
        'native_output_independence_proved': False,
        'coefficient_reader_introduced': False,
        'native_a_z_only_scalarization_proved': False,
        'complete_native_scalar_chain_polynomial_bound_proved': False,
    }
    if args.write_report and clean:
        assert olean.is_file()
        report['olean'] = str(olean)
        report['olean_sha256'] = sha256(olean.read_bytes()).hexdigest()
        (HERE / 'auxiliary-erasure-validation.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({'status': report['status'], 'theorems': len(names),
                      'seconds': report['seconds']}, ensure_ascii=False))
    return 0 if clean else 1


if __name__ == '__main__':
    raise SystemExit(main())

"""Check terminal tag laws and explicit scalar closure from a normalization certificate."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
BUILD = PROJECT/'travail/fermeture-native/build'
HELPER = PROJECT/'etudes/2026-11-01/lean-operateurs/lean_check.py'
SOURCE = HERE/'TerminalTaggedClosure.lean'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    spec = importlib.util.spec_from_file_location('tagged_closure_environment', HELPER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    env = helper.environment()
    env['LEAN_PATH'] = ';'.join([str(BUILD), str(HERE),
        str(PROJECT/'travail/audit-compilation-generique/build'), env['LEAN_PATH']])
    BUILD.mkdir(parents=True, exist_ok=True)
    sources = [SOURCE, Path(__file__), HERE/'AuxiliaryErasure.lean',
               BUILD/'AuxiliaryErasure.olean', HELPER]
    def hashes():
        return {p.relative_to(PROJECT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sources}
    before = hashes()
    source_text = SOURCE.read_text(encoding='utf-8')
    names = re.findall(r'^theorem\s+(\w+)', source_text, re.M)
    command = [str(helper.LEAN), '-j1', '-o', str(BUILD/'TerminalTaggedClosure.olean'), str(SOURCE)]
    start = time.monotonic()
    result = subprocess.run(command, cwd=HERE, env=env, capture_output=True,
                            encoding='utf-8', errors='replace')
    output = result.stdout+result.stderr
    clean = re.search(r'\b(?:sorry|admit)\b|^\s*axiom\s', source_text, re.M) is None
    audited = all(f'TerminalTaggedClosure.{name}' in output for name in names)
    passed = (result.returncode == 0 and before == hashes() and clean and audited
              and 'sorryAx' not in output and 'warning:' not in output)
    report = {
        'status': 'passed' if passed else 'failed', 'date': '2026-11-03',
        'source_sha256': before, 'command': command, 'exit_code': result.returncode,
        'elapsed_seconds': round(time.monotonic()-start, 3),
        'stdout': result.stdout, 'stderr': result.stderr, 'theorems': names,
        'no_placeholders_or_added_axioms': clean, 'all_axioms_printed': audited,
        'sources_and_dependencies_unchanged': before == hashes(),
        'scope': 'Terminal label closure under sums, scalar multiplication and finite linear readout; '
                 'an explicit scalar circuit follows from a bounded coefficient circuit with a faithful tagged normalization certificate.',
        'normalization_certificate_is_an_explicit_hypothesis': True,
        'coefficient_circuit_is_explicitly_supplied': True,
        'reader_witness': 'AuxiliaryErasure.eraseAux c',
        'coordinate_extraction_from_native_representative_constructed': False,
        'complete_native_scalar_closure_proved': False,
    }
    (HERE/'tagged-closure-lean-validation.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({'status':report['status'],'theorems':len(names)}))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())

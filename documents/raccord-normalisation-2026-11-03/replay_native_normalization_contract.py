"""Check the normalized contract for the retained representative outputs."""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
SOURCE = HERE / 'NativeNormalizationContract.lean'
HELPER = PROJECT / 'etudes/2026-11-01/lean-operateurs/lean_check.py'
BUILDS = [PROJECT / 'travail/fermeture-native/build',
          PROJECT / 'travail/induction-native/build',
          PROJECT / 'travail/audit-compilation-generique/build']

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('native_contract_env', HELPER)
    assert spec and spec.loader
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    env = helper.environment()
    env['LEAN_PATH'] = os.pathsep.join(map(str, BUILDS)) + os.pathsep + env['LEAN_PATH']
    raw = SOURCE.read_bytes()
    txt = raw.decode('utf-8')
    names = re.findall(r'^theorem\s+(\w+)', txt, re.MULTILINE)
    digest = sha256(raw).hexdigest()
    command = [str(helper.LEAN), '-j1', str(SOURCE)]
    started = time.monotonic()
    result = subprocess.run(command, cwd=HERE, env=env, capture_output=True,
                            encoding='utf-8', errors='replace')
    output = result.stdout + result.stderr
    unchanged = sha256(SOURCE.read_bytes()).hexdigest() == digest
    audited = all('NativeNormalizationContract.' + name in output for name in names)
    no_placeholders = re.search(r'\b(?:sorry|admit|axiom)\b', txt) is None
    clean = result.returncode == 0 and unchanged and audited and no_placeholders \
        and 'warning:' not in output and 'sorryAx' not in output
    report = {
        'status': 'passed' if clean else 'failed',
        'date': '2026-11-03', 'command': command,
        'source': SOURCE.name, 'source_sha256': digest,
        'replay_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'environment_helper_sha256': sha256(HELPER.read_bytes()).hexdigest(),
        'local_imports': {
            str(path.relative_to(PROJECT)): sha256(path.read_bytes()).hexdigest()
            for path in [
                BUILDS[0] / 'TerminalTaggedClosure.olean',
                BUILDS[0] / 'AuxiliaryErasure.olean',
                BUILDS[2] / 'MatrixScalarCompiler.olean',
            ]
        },
        'source_changed_during_check': not unchanged,
        'exit_code': result.returncode,
        'seconds': round(time.monotonic() - started, 3),
        'stdout': result.stdout, 'stderr': result.stderr, 'theorems': names,
        'all_theorem_axioms_printed': audited,
        'source_has_no_placeholders_or_added_axioms': no_placeholders,
        'scope': 'The retained homogeneous representatives vanish at x=0. The existing normalized contract on those output wires therefore forces zero native outputs. A nonzero native output contradicts that contract. Q=5,N=4,a=0,z=1 witness arithmetic is checked, and tag(2) is nonzero whenever its target label is nonzero.',
        'nonzero_terminal_label_assumed_in_lean': True,
        'quotient_basis_construction_formalized_here': False,
        'general_polynomial_closure_proved': False,
        'impossibility_of_other_scalar_compilers_claimed': False,
    }
    if args.write_report:
        report['lean_version'] = subprocess.run([str(helper.LEAN), '--version'],
            capture_output=True, encoding='utf-8', check=True).stdout.strip()
        (HERE / 'native-normalization-contract-validation.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({'status': report['status'], 'theorems_checked': len(names)}))
    return 0 if clean else 1

if __name__ == '__main__':
    raise SystemExit(main())

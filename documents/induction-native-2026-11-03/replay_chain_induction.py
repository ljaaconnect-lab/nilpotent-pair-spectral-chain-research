"""Replay the spectral compatibility and combined native-chain certificates."""
from __future__ import annotations

import argparse
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
HELPER = PROJECT / 'etudes/2026-11-01/lean-operateurs/lean_check.py'
BUILD = PROJECT / 'travail/induction-native/build'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--spectral-only', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('native_induction_environment', HELPER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    env = helper.environment()
    env['LEAN_PATH'] = ';'.join([
        str(BUILD), str(HERE),
        str(PROJECT / 'travail/audit-compilation-generique/build'),
        env['LEAN_PATH'],
    ])
    BUILD.mkdir(parents=True, exist_ok=True)
    entries = [('SpectralReadoutCompatibility.lean', 'NativeSpectralInduction',
                'spectral-readout-lean-validation.json',
                'Ring-homomorphism compatibility with spectral linear readout; '
                'kernel orthogonality is an explicit hypothesis.')]
    if not args.spectral_only:
        entries.append(('NativeChainInduction.lean', 'NativeChainInduction',
                        'native-chain-lean-validation.json',
                        'Shared native prefix and suffix circuit semantics and gate bounds; '
                        'preparation and suffix bounds are explicit hypotheses.'))
    summaries = []
    for filename, namespace, report_name, scope in entries:
        source = HERE / filename
        raw = source.read_bytes()
        before = hashlib.sha256(raw).hexdigest()
        source_text = raw.decode('utf-8')
        names = re.findall(r'^theorem\s+(\w+)', source_text, re.M)
        dependencies = ([HERE/'NativePrefixInduction.lean', BUILD/'NativePrefixInduction.olean']
                        if filename.startswith('NativeChain') else [])
        dependency_hashes = {p.relative_to(PROJECT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in dependencies}
        command = [str(helper.LEAN), '-j1', '-o', str(BUILD / (source.stem+'.olean')), str(source)]
        start = time.monotonic()
        result = subprocess.run(command, cwd=HERE, env=env,
                                capture_output=True, encoding='utf-8', errors='replace')
        output = result.stdout + result.stderr
        unchanged = hashlib.sha256(source.read_bytes()).hexdigest() == before
        dependencies_unchanged = all(hashlib.sha256((PROJECT/p).read_bytes()).hexdigest() == h
                                     for p, h in dependency_hashes.items())
        no_placeholders = re.search(r'\b(?:sorry|admit)\b|^\s*axiom\s', source_text, re.M) is None
        audited = all(f'{namespace}.{name}' in output for name in names)
        passed = (result.returncode == 0 and unchanged and dependencies_unchanged and no_placeholders and audited
                  and 'sorryAx' not in output and 'warning:' not in output)
        report = {
            'status': 'passed' if passed else 'failed', 'date': '2026-11-03',
            'source': filename, 'source_sha256': before,
            'source_changed_during_check': not unchanged,
            'replay_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'command': command, 'exit_code': result.returncode,
            'elapsed_seconds': round(time.monotonic()-start, 3),
            'stdout': result.stdout, 'stderr': result.stderr,
            'theorems': names, 'all_axioms_printed': audited,
            'no_placeholders_or_added_axioms': no_placeholders,
            'dependency_sha256': dependency_hashes,
            'dependencies_unchanged': dependencies_unchanged,
            'scope': scope,
            'python_compiler_formalized': False,
            'auxiliary_variables_eliminated': False,
            'complete_scalar_a_z_only_chain_proved': False,
        }
        (HERE/report_name).write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(output, end='')
        summaries.append({'source':filename, 'status':report['status'], 'theorems':len(names)})
        if not passed:
            print(json.dumps(summaries))
            return 1
    print(json.dumps(summaries))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

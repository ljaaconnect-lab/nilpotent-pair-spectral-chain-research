"""Rebuild the verified dependency and the terminal-readout lemmas.

This checks the declared algebraic identities, not the missing general
polynomial closure or the Python compiler's full correctness in Lean.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent/'lean-operateurs'))
from lean_check import LEAN, environment, BUILD


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    cache = BUILD/'readout-cache'
    cache.mkdir(parents=True, exist_ok=True)
    env = environment()
    env['LEAN_PATH'] = str(cache)+';'+env['LEAN_PATH']
    files = [HERE.parent/'fusion-ntt/TerminalDifference.lean', HERE/'TerminalReadout.lean']
    records = []
    for index, source in enumerate(files):
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        command = [str(LEAN)]
        if index == 0:
            command += ['-o', str(cache/'TerminalDifference.olean')]
        command += [str(source)]
        started = time.monotonic()
        result = subprocess.run(command, cwd=source.parent, env=env,
                                capture_output=True, text=True, encoding='utf-8')
        record = {'source': source.relative_to(PROJECT).as_posix(), 'sha256': before,
            'source_changed_during_check': before != hashlib.sha256(source.read_bytes()).hexdigest(),
            'exit_code': result.returncode, 'seconds': round(time.monotonic()-started, 3),
            'stdout': result.stdout, 'stderr': result.stderr}
        records.append(record)
        print(json.dumps({k: v for k, v in record.items() if k not in ('stdout', 'stderr')}), flush=True)
        if result.returncode:
            break
    passed = len(records) == 2 and all(
        r['exit_code'] == 0 and not r['source_changed_during_check'] and
        'sorryAx' not in r['stdout']+r['stderr'] and
        'warning:' not in r['stdout']+r['stderr'] for r in records)
    report = {'status': 'passed' if passed else 'failed', 'compiler': str(LEAN),
        'version': subprocess.run([str(LEAN), '--version'], capture_output=True,
                                  text=True).stdout.strip(),
        'independent_dependency_rebuild': True,
        'full_circuit_formalization': False, 'general_polynomial_solution': False,
        'files': records}
    if args.write_report:
        (HERE/'lean-validation.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())

"""Independent CLI replay; no reliance on the editor/LSP diagnostic cache."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import time
from lean_check import BUILD, LEAN, SOURCE_ENV, environment

HERE = Path(__file__).resolve().parent


def check(name, output=None):
    file = HERE/name
    before = hashlib.sha256(file.read_bytes()).hexdigest()
    cmd = [str(LEAN)]
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        cmd += ['-o', str(output)]
    cmd += [str(file)]
    start = time.monotonic()
    result = subprocess.run(cmd, cwd=HERE, env=environment(), capture_output=True,
                            text=True, encoding='utf-8', errors='replace')
    after = hashlib.sha256(file.read_bytes()).hexdigest()
    record = {'source': name, 'sha256': before, 'source_changed_during_check': before != after,
              'exit_code': result.returncode, 'seconds': round(time.monotonic()-start, 3),
              'stdout': result.stdout, 'stderr': result.stderr}
    print(json.dumps({k: v for k, v in record.items() if k not in ('stdout', 'stderr')}), flush=True)
    return record


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    BUILD.mkdir(parents=True, exist_ok=True)
    version = subprocess.run([str(LEAN), '--version'], capture_output=True, text=True).stdout.strip()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resume', action='store_true', help='Reuse successful CLI records for unchanged sources')
    parser.add_argument('--write-report', action='store_true', help='Replace the archived validation report')
    args = parser.parse_args()
    prior = {}
    report_path = HERE/'lean-validation.json'
    if args.resume and report_path.exists():
        old = json.loads(report_path.read_text(encoding='utf-8'))
        if old.get('version') == version:
            prior = {x['source']: x for x in old['files']}
    records = []
    jobs = [('LocalNoncommRing.lean', BUILD/'local-cache/LocalNoncommRing.olean'),
            ('CollisionFilter.lean', None), ('WeylOperators.lean', None),
            ('PartitionCertificate.lean', BUILD/'local-cache/PartitionCertificate.olean'),
            ('WordFilter.lean', None)]
    for name, output in jobs:
        record = prior.get(name)
        if not (record and record['exit_code'] == 0 and not record['source_changed_during_check']
                and record['sha256'] == hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                and (not output or output.exists())):
            record = check(name, output)
        else:
            print(json.dumps({'source': name, 'reused_successful_cli_record': True}), flush=True)
        records.append(record)
        if record['exit_code'] or record['source_changed_during_check']:
            break
    passed = len(records) == len(jobs) and all(
        x['exit_code'] == 0 and not x['source_changed_during_check'] and
        'sorryAx' not in x['stdout']+x['stderr'] and
        'warning:' not in x['stdout']+x['stderr'] for x in records)
    report = {'date': '2026-11-01', 'status': 'passed' if passed else 'failed',
              'compiler': str(LEAN), 'version': version, 'environment_source': str(SOURCE_ENV),
              'independent_cli_replay': True, 'general_polynomial_solution': False,
              'files': records}
    if args.write_report:
        (HERE/'lean-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'files': len(records)}), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())

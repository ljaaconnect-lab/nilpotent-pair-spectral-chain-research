"""Replay the algebraic lemmas used in the NTT / transport bridge.

These are kernel checks of the stated lemmas, not a scalar complexity proof
or a formal verification of the entire Python experiment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'lean-operateurs'))
from lean_check import LEAN, environment


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    records = []
    for name in ('FusionFourier.lean','TerminalDifference.lean'):
        source = HERE/name
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        start = time.monotonic()
        result = subprocess.run([str(LEAN),str(source)],cwd=HERE,env=environment(),
                                capture_output=True,text=True,encoding='utf-8')
        changed = before != hashlib.sha256(source.read_bytes()).hexdigest()
        record = {'source':name, 'sha256':before, 'source_changed_during_check':changed,
                  'exit_code':result.returncode,'seconds':round(time.monotonic()-start,3),
                  'stdout':result.stdout,'stderr':result.stderr}
        records.append(record)
        print(json.dumps({k:v for k,v in record.items() if k not in ('stdout','stderr')}),flush=True)
    passed = all(r['exit_code'] == 0 and not r['source_changed_during_check'] and
                 'sorryAx' not in r['stdout']+r['stderr'] and
                 'warning:' not in r['stdout']+r['stderr'] for r in records)
    report = {'status':'passed' if passed else 'failed', 'compiler':str(LEAN),
              'version':subprocess.run([str(LEAN),'--version'],capture_output=True,
                                      text=True).stdout.strip(),
              'full_chain_formalization':False, 'general_polynomial_solution':False,
              'files':records}
    if args.write_report:
        (HERE/'lean-validation.json').write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())

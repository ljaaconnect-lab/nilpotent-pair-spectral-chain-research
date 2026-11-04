"""Independently replay the general resolvent-fusion lemmas."""
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
    source = HERE/'ResolventFusion.lean'
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    start = time.monotonic()
    result = subprocess.run([str(LEAN),str(source)], cwd=HERE, env=environment(),
                            capture_output=True, text=True, encoding='utf-8')
    changed = before != hashlib.sha256(source.read_bytes()).hexdigest()
    output = result.stdout+result.stderr
    passed = result.returncode == 0 and not changed and 'sorryAx' not in output and 'warning:' not in output
    report = {'status':'passed' if passed else 'failed', 'source':source.name,
              'sha256':before, 'source_changed_during_check':changed,
              'compiler':str(LEAN),
              'version':subprocess.run([str(LEAN),'--version'], capture_output=True,
                                      text=True).stdout.strip(),
              'exit_code':result.returncode, 'seconds':round(time.monotonic()-start,3),
              'stdout':result.stdout, 'stderr':result.stderr,
              'general_polynomial_solution':False}
    if args.write_report:
        (HERE/'resolvent-lean-validation.json').write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())

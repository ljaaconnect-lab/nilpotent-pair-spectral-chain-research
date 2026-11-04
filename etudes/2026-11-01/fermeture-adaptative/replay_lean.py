"""Independently check the direct Schur/jet algebraic identities."""
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
    source = HERE/'SchurJet.lean'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    started = time.monotonic()
    result = subprocess.run([str(LEAN), str(source)], cwd=HERE, env=environment(),
                            capture_output=True, text=True, encoding='utf-8')
    unchanged = digest == hashlib.sha256(source.read_bytes()).hexdigest()
    passed = result.returncode == 0 and unchanged and all(
        marker not in result.stdout+result.stderr for marker in ('sorryAx', 'warning:'))
    report = {'status': 'passed' if passed else 'failed', 'source': source.name,
        'sha256': digest, 'source_changed_during_check': not unchanged,
        'exit_code': result.returncode, 'seconds': round(time.monotonic()-started, 3),
        'compiler': str(LEAN), 'version': subprocess.run([str(LEAN), '--version'],
            capture_output=True, text=True).stdout.strip(),
        'stdout': result.stdout, 'stderr': result.stderr,
        'theorems': ['jet_eval', 'jet_scale', 'block_eliminate'],
        'scope': 'Algebraic jet identities in any commutative ring. The block theorem takes q^2=0 and r*P=0 as explicit hypotheses; the square-zero degree argument and the full-chain induction are written proofs, not formalized here.',
        'full_chain_formalization': False, 'general_polynomial_closure': False}
    if args.write_report:
        (HERE/'lean-validation.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())

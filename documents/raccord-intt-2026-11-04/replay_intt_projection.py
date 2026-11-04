"""Check the exact scope of coefficient projection through a shared linear DAG."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    helper_path = PROJECT / 'etudes/2026-11-01/lean-operateurs/lean_check.py'
    spec = importlib.util.spec_from_file_location('intt_lean_environment', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source = HERE / 'INTTProjection.lean'
    raw = source.read_bytes()
    names = re.findall(r'^theorem\s+(\w+)', raw.decode('utf-8'), re.M)
    command = [str(helper.LEAN), '-j1', str(source)]
    start = time.monotonic()
    result = subprocess.run(command, cwd=HERE, env=helper.environment(),
                            capture_output=True, encoding='utf-8', errors='replace')
    output = result.stdout + result.stderr
    unchanged = source.read_bytes() == raw
    clean = re.search(r'\b(?:sorry|admit)\b|^\s*axiom\s', raw.decode('utf-8'), re.M) is None
    audited = all((f"'INTTProjection.{name}' depends on axioms:" in output or
                   f"'INTTProjection.{name}' does not depend on any axioms" in output)
                  for name in names)
    passed = (result.returncode == 0 and unchanged and clean and audited
              and 'sorryAx' not in output and 'warning:' not in output)
    report = {
        'status': 'passed' if passed else 'failed',
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'source': source.name, 'source_sha256': hashlib.sha256(raw).hexdigest(),
        'replay_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'command': command, 'exit_code': result.returncode,
        'elapsed_seconds': round(time.monotonic() - start, 3),
        'source_unchanged': unchanged, 'no_placeholders_or_added_axioms': clean,
        'all_theorem_axioms_audited': audited, 'theorems': names,
        'stdout': result.stdout, 'stderr': result.stderr,
        'scope': 'Linear projection through a shared spectral program; projected input values must already be computed. Kernel identity remains explicit.',
        'native_nonlinear_prefix_scalarized': False,
        'complete_scalar_a_z_only_chain_proved': False,
        'radix2_fft_implementation_formalized': False,
    }
    (HERE / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({'status': report['status'], 'theorems': len(names),
                      'seconds': report['elapsed_seconds']}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())

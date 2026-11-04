"""Check unit-insertion lemmas without asserting a complete scalar compiler."""
from __future__ import annotations

from datetime import datetime, timezone
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


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    spec = importlib.util.spec_from_file_location('unit_lean_environment', PROJECT / 'etudes/2026-11-01/lean-operateurs/lean_check.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source = HERE / 'UnitLift.lean'
    raw = source.read_bytes()
    names = re.findall(r'^theorem\s+(\w+)', raw.decode('utf-8'), re.M)
    command = [str(helper.LEAN), '-j1', str(source)]
    start = time.monotonic()
    result = subprocess.run(command, cwd=HERE, env=helper.environment(),
                            capture_output=True, encoding='utf-8', errors='replace')
    output = result.stdout + result.stderr
    clean = re.search(r'\b(?:sorry|admit)\b|^\s*axiom\s', raw.decode('utf-8'), re.M) is None
    audited = all((f"'UnitLift.{name}' depends on axioms:" in output or
                   f"'UnitLift.{name}' does not depend on any axioms" in output) for name in names)
    passed = (result.returncode == 0 and source.read_bytes() == raw and clean and audited
              and 'sorryAx' not in output and 'warning:' not in output)
    report = {
        'status': 'passed' if passed else 'failed',
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'source': source.name, 'source_sha256': hashlib.sha256(raw).hexdigest(),
        'replay_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'command': command, 'exit_code': result.returncode,
        'elapsed_seconds': round(time.monotonic() - start, 3),
        'source_unchanged': source.read_bytes() == raw,
        'no_placeholders_or_added_axioms': clean,
        'all_theorem_axioms_audited': audited, 'theorems': names,
        'stdout': result.stdout, 'stderr': result.stderr,
        'scope': 'Unit insertion, augmentation under quotient equality, and preservation and routing of an arbitrary linear coefficient reader through the spectral readout. Native reader construction and Fourier substitution are justified in the written notes.',
        'spectral_kernel_identity_is_explicit_hypothesis': True,
        'full_native_Fourier_substitution_formalized': False,
        'python_compiler_formalized': False,
        'complete_scalar_a_z_only_chain_proved': False,
    }
    (HERE / 'lean-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({'status': report['status'], 'theorems': len(names), 'seconds': report['elapsed_seconds']}))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())

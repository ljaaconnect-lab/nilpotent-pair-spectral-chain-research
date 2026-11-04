"""Check arithmetic consequences only; no compiler formalisation is claimed."""
from __future__ import annotations

from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    helper_path = PROJECT / 'etudes/2026-11-01/lean-operateurs/lean_check.py'
    spec = importlib.util.spec_from_file_location('shared_chain_lean_environment', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source = HERE / 'SharedChainBounds.lean'
    before = sha256(source.read_bytes()).hexdigest()
    start = time.monotonic()
    command = [str(helper.LEAN), '-j1', str(source)]
    run = subprocess.run(command, cwd=HERE, env=helper.environment(),
                         capture_output=True, encoding='utf-8', errors='replace')
    output = run.stdout + run.stderr
    assert run.returncode == 0, output
    assert sha256(source.read_bytes()).hexdigest() == before
    assert 'warning:' not in output and 'sorryAx' not in output, output
    names = ['coefficient_preparation_bound', 'closed_state_compositions',
             'fused_reader_total', 'explicit_spectral_overhead',
             'linearised_source_budget']
    assert all(f'SharedChainBounds.{name}' in output for name in names), output
    report = {
        'status': 'passed', 'date': '2026-11-03', 'command': command,
        'source': source.name, 'source_sha256': before,
        'replay_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'source_changed_during_check': False, 'exit_code': run.returncode,
        'seconds': round(time.monotonic() - start, 3),
        'stdout': run.stdout, 'stderr': run.stderr, 'theorems': names,
        'scope': 'Arithmetic consequences of independently justified gate-count hypotheses.',
        'compiler_formalised': False, 'provenance_lemma_formalised': False,
        'polynomial_observation_initialisation_proved': False,
        'complete_chain_polynomial_bound_proved': False,
    }
    (HERE / 'lean-validation.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output, end='')
    print(json.dumps({'status': report['status'], 'theorems_checked': len(names),
                      'scope': report['scope']}, ensure_ascii=False))


if __name__ == '__main__':
    main()

"""Inspect the actual unchanged native program at its selected INTT output."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
NATIVE = PROJECT / 'documents/composition-native-2026-11-03'
sys.path.insert(0, str(NATIVE))
from compose_native_representatives import compile_native_representatives


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    compiled = compile_native_representatives(2, 5, 4, 2, [0, 1])
    dag = compiled['dag']
    base = {f'a_{i}_{j}': 0 for i in range(2) for j in range(2)} | {'z': 1}
    snapshots = []
    for auxiliary in ([0, 0, 0, 0], [1, 1, 1, 1]):
        inputs = base | {f'x_{r}': auxiliary[r] for r in range(4)}
        values = dag.evaluate(compiled['outputs'] + [compiled['F0']], inputs)
        outputs, core = values[:4], values[4]
        assert outputs == [0, (-core) % 5, 0, 0]
        assert dag.evaluate([node for row in compiled['B'] for node in row], inputs) == [1] * 4
        snapshots.append({'x': auxiliary, 'F0': core, 'INTT_outputs': outputs})
    # (q0+q1)^2 = 2*q0*q1; gamma_2=-1 and q0*q1=-Omega.
    expected_coefficient = (1 * 1 + 1 * 1) % 5
    assert expected_coefficient == 2
    assert snapshots[0]['INTT_outputs'][1] == 0 != expected_coefficient
    source_paths = [Path(__file__), NATIVE / 'compose_native_representatives.py',
                    PROJECT / 'etudes/2026-11-01/linearisation-orientee-convolution/linearised_inputs.py']
    report = {
        'status': 'passed', 'n': 2, 'Q': 5, 'N': 4, 'omega': 2,
        'target': 1, 'gamma_mod_Q': 4,
        'snapshots': snapshots, 'native_Omega_coefficient': expected_coefficient,
        'actual_INTT_calls': dag.intt_calls,
        'native_program_unchanged': True,
        'scope': 'The selected actual INTT wire equals gamma*F0 as a representative. Substituting auxiliary coordinates does not extract its quotient coefficient.',
        'no_general_circuit_lower_bound': True,
        'source_sha256': {p.relative_to(PROJECT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in source_paths},
    }
    (HERE / 'final-case-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

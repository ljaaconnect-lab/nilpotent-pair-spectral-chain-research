"""Verify only the unit insertion, its shared gate budget, and its scope."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
import sys

from compile_with_unit import compile_with_unit, PROJECT

HERE = Path(__file__).resolve().parent


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    rng = random.Random(20261104)
    cases = []
    for n, Q in [(1, 3), (2, 5), (3, 5), (4, 17), (8, 17), (16, 97)]:
        N = 1 << n.bit_length()
        omega = next(w for w in range(1, Q) if pow(w, N, Q) == 1 and pow(w, N//2, Q) != 1)
        built = compile_with_unit(n, Q, N, omega, list(range(n)))
        dag, original = built['dag'], built['original']
        target = built['metadata']['target']
        snapshots = []
        for trial in range(3):
            inputs = {f'a_{i}_{j}': rng.randrange(Q) if trial else 0
                      for i in range(n) for j in range(n)}
            inputs['z'] = rng.randrange(Q) if trial else 1
            inputs.update({f'x_{r}': rng.randrange(Q) if trial == 2 else 0 for r in range(N)})
            old = dag.evaluate(original['outputs'], inputs)
            new = dag.evaluate(built['outputs'], inputs)
            assert new == [(value + int(k == target)) % Q for k, value in enumerate(old)]
            if trial < 2:
                assert old == [0] * N
                assert new == [int(k == target) for k in range(N)]
            snapshots.append({'trial': trial, 'zero_auxiliary': trial < 2,
                              'old_target': old[target], 'lifted_target': new[target]})
        cases.append(built['metadata'] | {'snapshots': snapshots})
    two = next(case for case in cases if case['n'] == 2)
    # For B_ij=1, the corrected quotient output is 2*Omega in characteristic 5.
    assert two['snapshots'][0]['lifted_target'] == 1 != 2
    sources = [Path(__file__), HERE / 'compile_with_unit.py',
               PROJECT / 'documents/composition-native-2026-11-03/compose_native_representatives.py',
               PROJECT / 'etudes/2026-11-01/raccord-initialisation/spectral/reprise-globale/shared_operator_dag.py']
    report = {
        'status': 'passed', 'cases': cases,
        'counterexample_to_scalar_reading': {'n': 2, 'Q': 5, 'a': 'all zero', 'z': 1,
                                            'top_coefficient': 2, 'lifted_value_at_zero_aux': 1},
        'general_theorem_is_separate_from_finite_checks': True,
        'complete_scalar_closure_proved': False,
        'source_sha256': {p.relative_to(PROJECT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sources},
    }
    (HERE / 'unit-lift-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'passed', 'cases': len(cases),
                      'counts': [(c['n'], c['original_useful_gates'], c['lifted_useful_gates']) for c in cases],
                      'scalar_closure': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()

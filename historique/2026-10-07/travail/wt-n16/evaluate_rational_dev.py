"""Frozen positive reciprocal/Laurent evaluator; written before first execution.

Boundary: generic formal B for n=2,3,4,5. Five exact identity assertions per n.
Metric: exact assertion pass fraction, never a proof-confidence estimate.
"""
from pathlib import Path
from time import perf_counter
import hashlib
import json
import rational_recurrence


def main():
    passed, total, rows = 0, 0, []
    for n in (2, 3, 4, 5):
        started = perf_counter()
        reciprocal = rational_recurrence.check_reciprocal(n)
        laurent = rational_recurrence.label_normalization(n)
        checks = {
            'newton_determinant_coefficients': reciprocal['determinant_coefficients_exact'],
            'reciprocal_coordinates': reciprocal['reciprocal_coordinates_exact'],
            'reciprocal_generic_permanent': reciprocal['generic_permanent_exact'],
            'laurent_full_pair_identity': laurent['all_generic_weight_coefficients_exact'],
            'laurent_central_identity': laurent['central_generic_permanent_exact']}
        passed += sum(checks.values())
        total += len(checks)
        rows.append({'n': n, 'checks': checks, 'reciprocal': reciprocal,
                     'laurent': laurent, 'seconds': perf_counter()-started})
    report = {'protocol': 'positive-rational-dev-v1', 'split': 'dev',
              'score': passed/total, 'passed': passed, 'total': total,
              'evaluator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'artifact_sha256': hashlib.sha256(Path(rational_recurrence.__file__).read_bytes()).hexdigest(),
              'cases': rows,
              'scope': 'Generic formal-weight finite identities; quotient compilation charged; no Lean proof.'}
    Path('dev-rational.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'score': report['score'], 'passed': passed, 'total': total,
                      'evaluator_sha256': report['evaluator_sha256'],
                      'cases': [{'n': row['n'], 'checks': row['checks'],
                                 'native_gates': row['reciprocal']['construction']['native_scalar_gates'],
                                 'compiled_gates': row['reciprocal']['evaluation']['compiled_scalar_gates'],
                                 'normalized_center': row['laurent']['normalized_center'],
                                 'seconds': row['seconds']} for row in rows]}, indent=2))


if __name__ == '__main__':
    main()

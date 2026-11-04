"""Frozen positive-dev recurrence evaluator v1, written before first run.

Metric: exact formal-z identity pass fraction on 12 fixed positive examples,
four independent constructions per example. No held-out data is present.
"""
import argparse
import hashlib
import json
from pathlib import Path
from time import perf_counter
import candidate
import recurrence


def dev_cases():
    for n in (2, 3, 4, 5):
        for family in ('identity', 'cyclic', 'vandermonde'):
            yield f'n{n}-{family}', candidate.family_matrix(n, family)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='dev-recurrence.json')
    args = parser.parse_args()
    passed, total, results = 0, 0, []
    for name, A in dev_cases():
        n = len(A)
        reference = recurrence.reference_marked_permanent(A)
        variants = {}
        for label, builder in [('matrix_power', recurrence.build_matrix_power),
                               ('row_chain', recurrence.build_row_chain),
                               ('subset_dp', candidate.build_subset_dp)]:
            started = perf_counter()
            dag, output, construction = builder(A)
            actual, evaluation = recurrence.exact_output(dag, output)
            exact = actual == reference
            passed += int(exact)
            total += 1
            variants[label] = {'formal_z_exact': exact, 'gates': dag.gates,
                               'terms': len(actual),
                               'seconds': perf_counter()-started,
                               'construction': construction,
                               'evaluation': evaluation}
        started = perf_counter()
        actual, construction = recurrence.tensor_product_polynomial(A)
        exact = actual == reference
        passed += int(exact)
        total += 1
        variants['tensor_factorization'] = {
            'formal_z_exact': exact, 'terms': len(actual),
            'seconds': perf_counter()-started, 'construction': construction}
        results.append({'case': name, 'n': n, 'K': n**n-1,
                        'reference_terms': len(reference), 'variants': variants})
    report = {'protocol': 'positive-recurrence-dev-v1', 'split': 'dev',
              'score': passed/total, 'passed': passed, 'total': total,
              'evaluator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'candidate_sha256': hashlib.sha256(Path(candidate.__file__).read_bytes()).hexdigest(),
              'artifact_sha256': hashlib.sha256(Path(recurrence.__file__).read_bytes()).hexdigest(),
              'cases': results,
              'scope': 'Exact formal-z finite identities. No asymptotic polynomial bound or Lean proof.'}
    Path(args.output).write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'score': report['score'], 'passed': passed, 'total': total,
                      'evaluator_sha256': report['evaluator_sha256'],
                      'cases': [{'case': row['case'],
                                 'gates': {key: variant.get('gates')
                                           for key, variant in row['variants'].items()}}
                                for row in results]}, indent=2))


if __name__ == '__main__':
    main()

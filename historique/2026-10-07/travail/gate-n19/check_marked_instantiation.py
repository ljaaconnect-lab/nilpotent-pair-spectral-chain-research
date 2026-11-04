"""Development diagnostic for the new production Q[z] instantiation helper.

This is outside the frozen generic-weight score and contains no held-out data.
"""
import json
from pathlib import Path
import candidate
import recurrence
import mixed_derivative

rows = []
for n in (2, 3, 4, 5):
    A = candidate.family_matrix(n, 'vandermonde')
    expected = recurrence.reference_marked_permanent(A)
    for variant in ('demand', 'eager', 'bell'):
        dag, output, construction = mixed_derivative.build_marked_circuit(A, variant)
        actual, evaluation = recurrence.exact_output(dag, output)
        rows.append({'n': n, 'family': 'vandermonde', 'variant': variant,
                     'formal_z_exact': actual == expected,
                     'gates': dag.gates, 'construction': construction,
                     'evaluation': evaluation})
report = {'scope': 'Additional development diagnostic; frozen generic score unchanged',
          'passed': sum(row['formal_z_exact'] for row in rows),
          'total': len(rows), 'cases': rows}
Path('marked-mixed-diagnostic.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'passed': report['passed'], 'total': report['total'],
                  'gates': [{'n': row['n'], 'variant': row['variant'],
                             'gates': row['gates']} for row in rows]}, indent=2))

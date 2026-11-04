import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'test-boundary/positive-simulation.json'
TARGET = ROOT / 'test-boundary/matrix-power-heldout.json'
assert not TARGET.exists(), 'Do not change a frozen boundary'
cases = []
for case in json.loads(SOURCE.read_text(encoding='utf-8')):
    A = [[Fraction(x) for x in row] for row in case['A']]
    n = len(A)
    M = A if n < 5 else [[Fraction(1 if i == j else 0) if i >= j else A[i][j]
                         for j in range(n)] for i in range(n)]
    cases.append({'name': case['name'], 'n': n, 'r': n, 'K': n**n-1,
                  'M': [[str(x) for x in row] for row in M],
                  'u': [str(A[i][0]+1) for i in range(n)],
                  'v': [str(A[0][j]-1) for j in range(n)],
                  'matrix_family': 'dense rational' if n < 5 else 'unitriangular rational'})
assert len(cases) == 8
protocol = {'version': 'matrix-power-heldout-v1', 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'frozen_checks': ['scalar DAG exact rational output versus independent K-step matrix-vector oracle',
                              'topological graph and exact scalar +/* count'],
            'denominator': 16, 'cases': cases,
            'root_conjecture_verified': False,
            'scope': 'Correctness of conditional power compiler, not existence of a target representation'}
TARGET.write_text(json.dumps(protocol, indent=2), encoding='utf-8')
print(json.dumps({'cases':len(cases), 'checks':16, 'sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest()}))

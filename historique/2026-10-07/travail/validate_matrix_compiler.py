"""Coordinator-only exact held-out check of the conditional scalar compiler."""
import hashlib
import importlib.util
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT / 'research'
GATE = ROOT / 'gate-n57'
REF = sys.argv[1]
GIT = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
def git(*args):
    r = subprocess.run([str(GIT), '-c', 'safe.directory='+REPO.as_posix(), '-C', str(REPO), *map(str,args)],
                       capture_output=True, text=True, encoding='utf-8', check=True)
    return r.stdout
if not GATE.exists():
    git('worktree', 'add', '--detach', GATE, REF)
actual = subprocess.run([str(GIT), '-c', 'safe.directory='+GATE.as_posix(), '-C', str(GATE),
                         'rev-parse','HEAD'], capture_output=True, text=True, check=True).stdout.strip()
assert actual == REF
sys.path.insert(0, str(GATE))
spec = importlib.util.spec_from_file_location('frozen_dense', GATE/'dense_compiler.py')
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)
boundary = ROOT/'test-boundary/matrix-power-heldout.json'
protocol = json.loads(boundary.read_text(encoding='utf-8'))
report = {'protocol': protocol['version'], 'boundary_sha256': hashlib.sha256(boundary.read_bytes()).hexdigest(),
          'commit':REF, 'root_conjecture_verified':False, 'scope':protocol['scope'],
          'checks':[], 'passed':0, 'total':protocol['denominator']}
for case in protocol['cases']:
    r, k = case['r'], case['K']
    M = [[Fraction(v) for v in row] for row in case['M']]
    u, v = [[Fraction(t) for t in case[name]] for name in ['u','v']]
    dag = candidate.compile_scalar(r,k)
    inputs = {f'M[{i},{j}]':M[i][j] for i in range(r) for j in range(r)}
    inputs.update({f'u[{i}]':u[i] for i in range(r)})
    inputs.update({f'v[{i}]':v[i] for i in range(r)})
    got = candidate.evaluate_dag(dag, inputs)
    # Independent oracle: K matrix-vector steps, without binary squaring.
    current = v[:]
    for _ in range(k):
        current = [sum((M[i][j]*current[j] for j in range(r)), Fraction(0)) for i in range(r)]
    expected = sum((u[i]*current[i] for i in range(r)), Fraction(0))
    okay = got == expected
    assert okay, case['name']
    length = k.bit_length()-1 + k.bit_count()-1
    expected_gates = length*(2*r**3-r**2) + 2*r**2+r-1
    operations = [n for n in dag['nodes'] if n['op'] in ['add','mul']]
    topological = all(0 <= n['left'] < i and 0 <= n['right'] < i
                      for i,n in enumerate(dag['nodes']) if n['op'] in ['add','mul'])
    gate_ok = len(operations) == expected_gates == dag['scalar_gates'] and topological
    assert gate_ok, case['name']
    report['passed'] += int(okay)+int(gate_ok)
    report['checks'].append({'case':case['name'], 'r':r, 'K':k, 'family':case['matrix_family'],
        'exact_rational_agreement':okay, 'topological_and_gate_count':gate_ok,
        'scalar_gates':expected_gates, 'matrix_multiplications':length,
        'output_bit_length':max(got.numerator.bit_length(),got.denominator.bit_length()),
        'output_sha256':hashlib.sha256(str(got).encode()).hexdigest()})
    (ROOT/'matrix-compiler-test-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'case':case['name'], 'passed':2, 'scalar_gates':expected_gates}),flush=True)
assert report['passed'] == report['total']
print(json.dumps({'passed':report['passed'],'total':report['total'],'root_conjecture_verified':False}),flush=True)

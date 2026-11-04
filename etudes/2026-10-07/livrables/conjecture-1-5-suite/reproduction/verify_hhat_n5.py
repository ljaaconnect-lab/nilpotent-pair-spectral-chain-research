"""Complete the requested n=5 scalar-DAG evaluation on frozen positive cases."""
import hashlib
import importlib.util
import json
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASE_FILE = ROOT / 'test-boundary/positive-simulation.json'
GATE = ROOT / 'gate-n1'
REPORT = ROOT/'n5-full-hhat-test-report.json'
if (ROOT.parent/'circuits').is_dir():
    package = ROOT.parent
    CASE_FILE = package/'validation-boundaries/positive-simulation.json'
    GATE = package/'circuits/encoding-and-subset'
    REPORT = package.parent.parent/'work/delivered-validation/n5-full-hhat-test-report.json'
REPORT.parent.mkdir(parents=True,exist_ok=True)


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, GATE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


candidate = load('positive_hhat_candidate', 'candidate.py')
oracle = load('frozen_hhat_oracle', 'evaluate.py')
cases = [c for c in json.loads(CASE_FILE.read_text(encoding='utf-8')) if len(c['A']) == 5]
assert len(cases) == 2
report = {
    'scope': 'Full n=5 scalar-DAG evaluation, positive cases already frozen and previously published; no asymptotic extraction claim.',
    'root_conjecture_verified': False,
    'case_file_sha256': hashlib.sha256(CASE_FILE.read_bytes()).hexdigest(),
    'candidate_sha256': hashlib.sha256((GATE/'candidate.py').read_bytes()).hexdigest(),
    'evaluator_sha256': hashlib.sha256((GATE/'evaluate.py').read_bytes()).hexdigest(),
    'cases': [],
}
for case in cases:
    A = [[Fraction(v) for v in row] for row in case['A']]
    expected, expected_full = oracle.reference(A)
    dag, output, K = candidate.build_hhat(A)
    started = time.perf_counter()
    full, stats = dag.evaluate(output)
    elapsed = time.perf_counter() - started
    central = {z:value for (t,z),value in full.items() if t == K}
    checks = {'full_exact': full == expected_full, 'central_exact': central == expected,
              'canonical_index': K == 3124, 'binary_scalar_gates': dag.gates == 1314,
              'every_gate_evaluated': stats['scalar_gate_evaluations'] == dag.gates}
    row = {'case':case['name'], 'checks':checks, 'seconds':elapsed,
           'central_terms':len(central), 'hhat_terms':len(full), 'K':K,
           'gates':dag.gates, 'evaluation_stats':stats}
    report['cases'].append(row)
    report['passed'] = sum(sum(c['checks'].values()) for c in report['cases'])
    report['total'] = sum(len(c['checks']) for c in report['cases'])
    REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(row),flush=True)
    assert all(checks.values())
print(json.dumps({'passed':report['passed'],'total':report['total'],
                  'root_conjecture_verified':False}),flush=True)

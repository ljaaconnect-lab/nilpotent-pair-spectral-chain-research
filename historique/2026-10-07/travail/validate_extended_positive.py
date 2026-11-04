"""Coordinator-only frozen holdout replay from immutable Git checkouts."""
import hashlib, importlib.util, json, subprocess, sys, time
from fractions import Fraction
from pathlib import Path
ROOT = Path(__file__).resolve().parent
REPO = ROOT / 'research'
GIT = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
REFS = {'n15': 'a3a6f044243d4006ba2c3a8a9d9577d13d9d806c',
        'n16': 'ba86cbd596588993b2061db0f033ec8e5b58fac4',
        'n18': '1c9875ad83b903e5769bacc78df80ae7126a71cb',
        'n19': 'eb1a8e4648a1e883b125661038ffe95f4a424b55'}
for node, ref in REFS.items():
    gate = ROOT / ('gate-' + node)
    if not gate.exists():
        subprocess.run([str(GIT), '-c', 'safe.directory=' + REPO.as_posix(), '-C', str(REPO),
                        'worktree', 'add', '--detach', str(gate), ref], check=True,
                       capture_output=True)

sys.path.insert(0, str(ROOT / 'gate-n4'))
import candidate, evaluate, recurrence

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

half = load('test_half_character', ROOT / 'gate-n15/half_character.py')
rational = load('rational_recurrence', ROOT / 'gate-n16/rational_recurrence.py')
gram = load('test_occupation_gram', ROOT / 'gate-n18/occupation_gram.py')
mixed = load('test_mixed_derivative', ROOT / 'gate-n19/mixed_derivative.py')

def add(left, right):
    result = dict(left)
    for mask, p in right.items():
        result[mask] = candidate.add_poly(result.get(mask, {}), p)
    return {mask: p for mask, p in result.items() if p}

def mul(left, right):
    result = {}
    for lm, lp in left.items():
        for rm, rp in right.items():
            if lm & rm:
                continue
            mask = lm | rm
            result[mask] = candidate.add_poly(result.get(mask, {}), candidate.mul_poly(lp, rp))
    return {mask: p for mask, p in result.items() if p}

def reciprocal_marked(A):
    n = len(A)
    dag, _, h, _, _ = rational.build_reciprocal_recurrence(n)
    values = []
    for node in dag.nodes:
        tag = node[0]
        if tag == 'constant':
            value = {0: {(0, 0): node[1]}} if node[1] else {}
        elif tag == 'weight':
            i, j = divmod(node[1], n)
            value = {0: {(0, 1 << (i*n+j)): 1 + A[i][j]**2}}
        elif tag == 'occupancy':
            value = {1 << node[1]: {(0, 0): Fraction(1)}}
        elif tag == 'add':
            value = add(values[node[1]], values[node[2]])
        elif tag == 'mul':
            value = mul(values[node[1]], values[node[2]])
        else:
            raise ValueError(tag)
        values.append(value)
    p = values[h[n]].get((1 << n)-1, {})
    return {z: a for (t, z), a in p.items() if t == 0}, dag.gates

fixture = ROOT / 'test-boundary/positive-simulation.json'
cases = json.loads(fixture.read_text())
report = {'protocol': 'extended-positive-heldout-v1', 'boundary_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest(),
          'artifact_refs': REFS, 'passed': 0, 'total': 0, 'cases': [],
          'root_conjecture_verified': False,
          'scope': 'Exact formal-z correctness of emitted scalar DAGs or charged quotient evaluation; finite checks do not establish polynomial extraction'}
for case in cases:
    start = time.monotonic()
    A = [[Fraction(a) for a in row] for row in case['A']]
    expected, _ = evaluate.reference(A)
    checks, gates = {}, {}
    dag, output, _ = half.build_marked_gray(A)
    actual, _ = recurrence.exact_output(dag, output)
    checks['n15_gray'] = actual == expected
    gates['n15_gray'] = dag.gates
    actual, cost = reciprocal_marked(A)
    checks['n16_reciprocal_projected'] = actual == expected
    gates['n16_native_before_charged_projection'] = cost
    dag, output, stats = gram.build_marked_encoding(A)
    full, _ = dag.evaluate(output)
    actual = {z: value for (s, z), value in full.items() if s == stats['T']}
    checks['n18_gram_coefficient'] = actual == expected
    gates['n18_encoding_before_extraction'] = dag.gates
    for variant in ['eager', 'demand', 'bell']:
        dag, output, _ = mixed.build_marked_circuit(A, variant)
        actual, _ = recurrence.exact_output(dag, output)
        checks['n19_' + variant] = actual == expected
        gates['n19_' + variant] = dag.gates
    report['passed'] += sum(checks.values())
    report['total'] += len(checks)
    report['cases'].append({'case': case['name'], 'n': len(A), 'checks': checks,
                            'gates': gates, 'elapsed_seconds': time.monotonic()-start})
    print(case['name'], sum(checks.values()), '/', len(checks), flush=True)
report['score'] = report['passed']/report['total']
(ROOT / 'extended-positive-test-report.json').write_text(json.dumps(report, indent=2))
print(json.dumps({'passed': report['passed'], 'total': report['total'], 'score': report['score']}), flush=True)
raise SystemExit(0 if report['passed'] == report['total'] else 1)

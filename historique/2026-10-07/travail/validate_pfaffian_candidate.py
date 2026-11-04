"""Coordinator-only fresh-checkout local identity replay; never a root proof."""
import hashlib
import importlib.util
import json
import subprocess
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

root = Path(__file__).resolve().parent
repo = root / 'research'
git = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
ref, expected_source_sha, expected_protocol_sha = sys.argv[1:]
gate = root / 'gate-n64'

def command(args, directory=repo):
    result = subprocess.run([str(git), '-c', 'safe.directory=' + directory.as_posix(),
        '-C', str(directory), *map(str, args)], capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()

if not gate.exists():
    command(['worktree', 'add', '--detach', gate, ref])
assert command(['rev-parse', 'HEAD'], gate) == ref
assert command(['status', '--porcelain'], gate) == ''

def digest(path):
    raw = path.read_bytes()
    return {'raw_sha256': hashlib.sha256(raw).hexdigest(),
        'canonical_lf_sha256': hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest()}

source_hash = digest(gate / 'pfaffian_coefficients.py')
protocol_hash = digest(gate / 'n64-protocol.json')
assert source_hash['canonical_lf_sha256'] == expected_source_sha
assert protocol_hash['canonical_lf_sha256'] == expected_protocol_sha
# Check every imported local module against the committed Git blob as well.
dependencies = {}
for name in ('pfaffian_coefficients.py', 'candidate.py', 'euler_identity.py'):
    result = subprocess.run([str(git), '-c', 'safe.directory=' + gate.as_posix(),
        '-C', str(gate), 'show', ref + ':' + name], capture_output=True, check=True)
    content = (gate / name).read_bytes().replace(b'\r\n', b'\n')
    assert content == result.stdout.replace(b'\r\n', b'\n')
    dependencies[name] = hashlib.sha256(content).hexdigest()

boundary = root / 'test-boundary/pfaffian-local-heldout.json'
freeze = json.loads((root / 'n64-heldout-freeze.json').read_text(encoding='utf-8'))
assert hashlib.sha256(boundary.read_bytes()).hexdigest() == freeze['sha256']
cases = json.loads(boundary.read_text(encoding='utf-8'))['cases']
sys.path.insert(0, str(gate))
spec = importlib.util.spec_from_file_location('pfaffian_local_candidate', gate / 'pfaffian_coefficients.py')
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)

def own_mobius(edges):
    total = 0
    for mask in range(1 << len(edges)):
        columns = [edge[1] for j, edge in enumerate(edges) if mask & (1 << j)]
        parity = (len(edges) - len(columns)) % 2
        for i, col in enumerate(columns):
            for later in columns[i+1:]:
                if col > later:
                    parity ^= 1
        total += -1 if parity else 1
    return total

def own_pfaffian(matrix):
    values = tuple(tuple(Fraction(v) for v in row) for row in matrix)
    assert len(values) % 2 == 0
    assert all(values[i][j] == -values[j][i] for i in range(len(values)) for j in range(len(values)))
    @lru_cache(None)
    def recur(indices):
        if not indices:
            return Fraction(1)
        first = indices[0]
        return sum(((-1 if j % 2 == 0 else 1) * values[first][indices[j]] *
            recur(indices[1:j] + indices[j+1:]) for j in range(1, len(indices))), Fraction(0))
    return recur(tuple(range(len(values))))

def own_interpreter(graph, output, matrix):
    values = []
    charged = 0
    for node in graph.nodes:
        operation = node['op']
        if operation == 'constant':
            value = Fraction(node['value'])
        elif operation == 'variable':
            _, i, j = node['name'].split('_')
            value = Fraction(matrix[int(i)][int(j)])
        else:
            assert operation in ('add', 'mul')
            assert node['left'] < len(values) and node['right'] < len(values)
            left, right = values[node['left']], values[node['right']]
            value = left + right if operation == 'add' else left * right
            charged += 1
        values.append(value)
    assert charged == graph.gates
    return values[output], charged

details, passed, total = [], 0, 0
circuits = {}
for case in cases:
    n, edges = case['n'], case['edges']
    assert edges == sorted(edges)
    assert len({r for r, _ in edges}) == len(edges) == len({c for _, c in edges})
    matching = tuple(i*n+j for i,j in edges)
    expected = own_mobius(edges)
    local = candidate.local_matrix([j for _,j in edges])
    fixed = candidate.fixed_port_matrix(n)
    indices = candidate.principal_ports(n, matching)
    submatrix = [[fixed[i][j] for j in indices] for i in indices]
    # Four exact local comparisons; no projection of the complete target here.
    tests = [candidate.mobius_coefficient(n, matching) == expected,
        (-1)**len(edges) * own_pfaffian(local) == expected,
        own_pfaffian(submatrix) == expected]
    if len(local) not in circuits:
        circuits[len(local)] = candidate.trace_circuit(len(local))
    graph, output = circuits[len(local)]
    trace_value, gates = own_interpreter(graph, output, local)
    tests.append((-1)**len(edges) * trace_value == expected)
    passed += sum(tests)
    total += len(tests)
    details.append({'n': n, 'matching_size': len(edges), 'tests': tests,
        'expected_coefficient': expected, 'trace_scalar_gates': gates})

report = {'node': 'n64', 'commit': ref, 'source_integrity': source_hash,
    'protocol_integrity': protocol_hash, 'imported_source_integrity': dependencies,
    'boundary_sha256': freeze['sha256'], 'cases': len(cases), 'passed': passed,
    'total': total, 'test_score': passed/total, 'details': details,
    'formal_pfaffian_status': 'unverified generic Lean theorem; finite local identity evidence only',
    'root_conjecture_verified': False}
(root / 'n64-positive-test-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({key: report[key] for key in ('node', 'commit', 'cases', 'passed', 'total', 'test_score', 'root_conjecture_verified')}))
raise SystemExit(0 if passed == total else 1)

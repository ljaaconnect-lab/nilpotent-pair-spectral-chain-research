"""Coordinator-only fresh-checkout scalar-DAG oracle for n61."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT.parent if (ROOT.parent/'circuits').is_dir() else None
if PACKAGE is not None:
    ROOT = PACKAGE.parent.parent/'work'
REPO = ROOT/'research'
GIT = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
TREE = Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
CASE_FILE = ROOT/'test-boundary/projector-positive-holdout.json'
if PACKAGE is not None:
    CASE_FILE = PACKAGE/'validation-boundaries/projector-positive-holdout.json'
FROZEN_CASE_HASH = '98537e66108c753efc6e6197a8cfac126da42e21e2c903875a3e8216c5216172'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('ref')
parser.add_argument('source_sha256')
args = parser.parse_args()


def run(cmd, cwd=None):
    result = subprocess.run(list(map(str,cmd)),cwd=cwd,capture_output=True,text=True,encoding='utf-8',timeout=180)
    assert result.returncode == 0, result.stdout+result.stderr
    return result.stdout


gate = ROOT/'gate-n61'
if PACKAGE is not None:
    gate = PACKAGE/'circuits/direct-projector'
    provenance = json.loads((PACKAGE/'verification/projector-candidate-test-report.json').read_text(encoding='utf-8'))
    assert args.ref == provenance['commit']
    manifest = json.loads((PACKAGE/'manifest-sha256.json').read_text(encoding='utf-8'))
    assert hashlib.sha256((gate/'euler_compiler.py').read_bytes()).hexdigest() == manifest['circuits/direct-projector/euler_compiler.py']
elif not gate.exists():
    run([GIT,'-c','safe.directory='+REPO.as_posix(),'-C',REPO,'worktree','add','--detach',gate,args.ref])
if PACKAGE is None:
    assert run([GIT,'-c','safe.directory='+gate.as_posix(),'-C',gate,'rev-parse','HEAD']).strip() == args.ref
source = gate/'euler_compiler.py'
source_raw = source.read_bytes()
raw_hash = hashlib.sha256(source_raw).hexdigest()
canonical_hash = hashlib.sha256(source_raw.replace(b'\r\n',b'\n')).hexdigest()
assert canonical_hash == args.source_sha256
if raw_hash != canonical_hash and PACKAGE is None and not (ROOT/'n61-checkout-incident.json').exists():
    (ROOT/'n61-checkout-incident.json').write_text(json.dumps({
        'original_check':'Raw bytes hash rejected before reading test cases',
        'resolution':'Git checkout changes LF to CRLF only; canonical full source matches frozen development source',
        'commit':args.ref,'raw_sha256':raw_hash,'canonical_lf_sha256':canonical_hash,
        'normalization':'CRLF -> LF; no other content transformation',
        'test_cases_evaluated_before_resolution':0},indent=2),encoding='utf-8')
assert hashlib.sha256(CASE_FILE.read_bytes()).hexdigest() == FROZEN_CASE_HASH
sys.path.insert(0,str(gate))
spec = importlib.util.spec_from_file_location('frozen_projector_candidate',source)
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)


def oracle(A):
    n = len(A)
    result = {}
    for sigma in itertools.permutations(range(n)):
        exponent = sum(2**(i*n+sigma[i]) for i in range(n))
        coefficient = Fraction(1)
        for i in range(n):
            coefficient *= 1+A[i][sigma[i]]**2
        result[exponent] = result.get(exponent,Fraction(0))+coefficient
    return result


def scalar_evaluate(nodes,output):
    values = []
    gate_count = 0
    bits = []
    for index,node in enumerate(nodes):
        op = node['op']
        if op == 'constant':
            q = Fraction(node['value'])
            bits.append(abs(q.numerator).bit_length()+q.denominator.bit_length()+1)
            value = {0:q} if q else {}
        elif op == 'variable':
            assert node['name'] == 'z', 'Auxiliary variables are not scalar leaves of the target'
            value = {1:Fraction(1)}
        else:
            assert op in ('add','mul')
            left,right = node['left'],node['right']
            assert 0 <= left < index and 0 <= right < index
            gate_count += 1
            if op == 'add':
                value = values[left].copy()
                for exponent,c in values[right].items():
                    value[exponent] = value.get(exponent,Fraction(0))+c
            else:
                value = {}
                for l,c in values[left].items():
                    for r,d in values[right].items():
                        value[l+r] = value.get(l+r,Fraction(0))+c*d
            value = {e:c for e,c in value.items() if c}
        values.append(value)
    assert 0 <= output < len(values)
    return values[output],gate_count,max(bits,default=0)


report = {'node':'n61','boundary':'root-only frozen positive rational cases',
          'commit':args.ref,'source_sha256':raw_hash,'frozen_lf_source_sha256':canonical_hash,
          'case_file_sha256':FROZEN_CASE_HASH,'root_conjecture_verified':False,
          'scope':'Independent evaluation of every scalar DAG node with z formal; no polynomial asymptotic bound.',
          'cases':[]}
for raw in json.loads(CASE_FILE.read_text(encoding='utf-8'))['cases']:
    A = [[Fraction(v) for v in row] for row in raw['A']]
    started = time.perf_counter()
    graph,output,metadata = candidate.build_marked(A)
    value,gates,bits = scalar_evaluate(graph.nodes,output)
    checks = {'canonical_polynomial':value == oracle(A),
              'exact_gate_count':gates == graph.gates,
              'output_nonempty':bool(value),
              'binary_scalar_topology':all(node['op'] in ('constant','variable','add','mul') for node in graph.nodes)}
    row = {'case':raw['name'],'n':len(A),'checks':checks,
           'gates':gates,'output_terms':len(value),'literal_bits_max':bits,
           'seconds':time.perf_counter()-started,'metadata':metadata}
    report['cases'].append(row)
    report['passed'] = sum(sum(c['checks'].values()) for c in report['cases'])
    report['total'] = sum(len(c['checks']) for c in report['cases'])
    report['score'] = report['passed']/report['total']
    destination = ROOT/('delivered-validation/projector-candidate-test-report.json' if PACKAGE is not None else 'projector-candidate-test-report.json')
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:row[k] for k in ('case','checks','gates','output_terms','seconds')}),flush=True)
    assert all(checks.values())
if PACKAGE is None:
    run([sys.executable,TREE,'--run-dir',REPO,'set-evidence','--node','n61','--dev-score','1',
         '--branch-ref',args.ref,'--result','Constructive projector identity and actual scalar DAG; root-only evaluation passes all frozen cases; general polynomial bound unproved',
         '--insight','Direct sign correction via shared cofactor matching projectors; explicit scalar costs include markers and universal preprocessing is measured'])
    run([sys.executable,TREE,'--run-dir',REPO,'merge','--node','n61','--test-score',str(report['score']),'--branch-ref',args.ref])
    run([sys.executable,TREE,'--run-dir',REPO,'propagate','--node','n61',
         '--insight','Independent scalar DAG correctness verified; no polynomial-sized representation or uniform polynomial compilation established'])
print(json.dumps({'passed':report['passed'],'total':report['total'],'root_conjecture_verified':False}),flush=True)

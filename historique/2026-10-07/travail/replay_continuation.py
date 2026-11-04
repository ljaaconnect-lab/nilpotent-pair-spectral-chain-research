"""Independent replay of committed supporting lemmas; never a root proof score."""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT / 'research'
GIT = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
LEAN = Path('C:/Users/REGIS/Documents/Codex/runtimes/elan/toolchains/leanprover--lean4---v4.34.1/bin/lean.exe')
TREE = Path('C:/Users/REGIS/.codex/skills/arbor/scripts/tree.py')
JOBS = [
    ('n67', '3dcfa83ae05f9ed9876ed8b67d35425e40649cf6', ['HadamardPfaffian.lean'], 4,
     'Exact local Hadamard COPY transform, explicit Pf4 boundary, and rational matrix inverse; no global Gaussian closure'),
    ('n63', '98a8c08b6e341202e3d6bf2e8d73bcc498380906', ['MobiusBridge.lean'], 6,
     'Exact Mobius reconstruction and unconditional sign-coefficient literal bounds'),
    ('n39', '1fc355d882554ce93fc619fd496cd32b9e7b70b6', ['RankOneSquareZero.lean'], 6,
     'Square-zero two-sided products and explicit outer-product propagation'),
    ('n40', '3804886e1fd9576c403444fcd2c5a8c5872e0e78', ['PowerCompiler.lean'], 7,
     'Shared binary-power compiler and logarithmic multiplication budget'),
    ('n54', '7e62fc4aa4d31a5d4261ce0072ba3f1d9b069392',
     ['CoreBridge.lean', 'GeneralPairingRing.lean', 'LabelBridge.lean', 'PolynomialBridge.lean'], 6,
     'Actual Polynomial interpretation of central labelled sign pairing'),
    ('n56', 'b8a9c6afb75f43c8a7143407ab82de46bf8e8dce', ['DoubleOrientation.lean'], 7,
     'Noncommutative double orientation, pair nilpotence and exact triangular sign'),
    ('n57', 'b75a6a382ff0ce07ce521f6d219ccaeb48188d17', ['PowerCompiler.lean', 'MatrixScalarCompiler.lean'], 24,
     'Actual shared scalar circuit semantics and conditional matrix-power budget'),
    ('n55', 'a6f3dd13872c5a7932b19ebc875434bc005030fe',
     ['CoreBridge.lean', 'GeneralPairingRing.lean', 'LabelBridge.lean', 'DeterminantBridge.lean'], 13,
     'Actual determinant pairing with proved base-n injectivity and exact canonical central index'),
    ('n59', '367e825e5546ae4cb96e659673c1fc4cea484842',
     ['PowerCompiler.lean', 'MatrixScalarCompiler.lean', 'ConditionalCriterion.lean'], 4,
     'Charged initial input circuit, actual Polynomial Nat budget and explicit representation criterion'),
    ('n58', '96fdd0ca11ad17b0824d213539cc6166df569de0', ['ReverseVandermonde.lean'], 9,
     'Exact projective Vandermonde orientation and original complementary monomial matrix'),
    ('n60', '8174ac17dd1060e1a34ebff8f134fd8a799bcced',
     ['CoreBridge.lean', 'GeneralPairingRing.lean', 'LabelBridge.lean', 'DeterminantBridge.lean',
      'ReverseVandermonde.lean', 'EncodingBridge.lean'], 7,
     'Actual padded Hhat central coefficient and exact original rational marked-A identity'),
    ('n62', '60a68a93817b6f68af2458d5b69324cae0ba7cd2',
     ['CoreBridge.lean', 'GeneralPairingRing.lean', 'LabelBridge.lean', 'DeterminantBridge.lean',
      'DirectProjector.lean'], 7,
     'Local multiaffine scalar cofactors, commuting involutive phases and actual permutation-sign correction'),
]
if sys.argv[1:]:
    selected = set(sys.argv[1:])
    assert selected <= {j[0] for j in JOBS}
    JOBS = [j for j in JOBS if j[0] in selected]
REPORT = ROOT / ('further-proof-replay.json' if sys.argv[1:] else 'continuation-proof-replay.json')

def run(args, cwd=REPO, env=None, timeout=180):
    r = subprocess.run(list(map(str, args)), cwd=cwd, env=env, capture_output=True,
                       text=True, encoding='utf-8', timeout=timeout)
    if r.returncode:
        raise RuntimeError(r.stdout + r.stderr)
    return r

def tree(*args):
    return run([sys.executable, TREE, '--run-dir', REPO, *args]).stdout

report = (json.loads(REPORT.read_text(encoding='utf-8')) if REPORT.exists() else
          {'root_conjecture_verified': False, 'boundary': 'fresh committed proof replay', 'leaves': []})
report['leaves'] = [leaf for leaf in report['leaves'] if leaf['node'] not in {j[0] for j in JOBS}]
ledger_path = REPO / '.arbor/verified-bases.json'
ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
for node, ref, filenames, expected, description in JOBS:
    gate = ROOT / ('gate-' + node)
    if not gate.exists():
        run([GIT, '-c', 'safe.directory=' + REPO.as_posix(), '-C', REPO,
             'worktree', 'add', '--detach', gate, ref])
    actual = run([GIT, '-c', 'safe.directory=' + gate.as_posix(), '-C', gate, 'rev-parse', 'HEAD']).stdout.strip()
    assert actual == ref
    env = os.environ.copy()
    env.update(json.loads((ROOT / 'mathlib-environment.json').read_text(encoding='utf-8')))
    env['LEAN_PATH'] = str(gate) + os.pathsep + env['LEAN_PATH']
    leaf = {'node': node, 'commit': ref, 'description': description, 'sources': [],
            'root_conjecture_verified': False}
    for filename in filenames:
        p = gate / filename
        src = p.read_text(encoding='utf-8')
        assert not re.search(r'\b(sorry|admit|native_decide)\b|(?m:^\s*(axiom|unsafe)\s)', src)
        cmd = [LEAN, '-o', p.with_suffix('.olean'), p] if filename != filenames[-1] else [LEAN, p]
        result = run(cmd, gate, env)
        assert 'sorryAx' not in result.stdout
        audit = {}
        for name, values in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", result.stdout):
            axioms = {v.strip() for v in values.split(',') if v.strip()}
            assert axioms <= {'propext', 'Classical.choice', 'Quot.sound'}, (name, axioms)
            audit[name] = sorted(axioms)
        for name in re.findall(r"'([^']+)' does not depend on any axioms", result.stdout):
            audit[name] = []
        leaf['sources'].append({'file': filename, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
            'command': list(map(str, cmd)), 'exit_code': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr, 'axiom_audit': audit})
        print(json.dumps({'node': node, 'file': filename, 'exit_code': result.returncode}), flush=True)
    final = leaf['sources'][-1]
    assert len(final['axiom_audit']) == expected
    leaf['accepted_new_declarations'] = expected
    report['leaves'].append(leaf)
    REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    tree('set-evidence', '--node', node, '--dev-score', '1', '--branch-ref', ref,
         '--result', f'{expected} audited supporting declarations; independent replay exit 0; root unproved',
         '--insight', description + '; scalar extractor remains an explicit separate obligation')
    tree('merge', '--node', node, '--test-score', '1', '--branch-ref', ref)
    tree('propagate', '--node', node, '--insight',
         description + ' formally verified; this supplies no polynomial-dimensional representation of the target')
    for index, (name, axioms) in enumerate(final['axiom_audit'].items(), 1):
        if any(e['theorem'] == name for e in ledger['entries']):
            continue
        ledger['entries'].append({'theorem': name, 'source': final['file'],
            'source_sha256': final['sha256'], 'axioms': axioms, 'branch_ref': ref,
            'node_id': node, 'subgoal_id': f'{node}:L{index:02}', 'dev_score': 1.0,
            'test_score': 1.0, 'verification': 'kernel-accepted supporting lemma, independent replay',
            'depth_note': 'Supporting theorem frozen inside this committed experiment artifact; no separate worktree claimed'})
    ledger['accepted_declarations'] = len(ledger['entries'])
    ledger.pop('distinct_results', None)
    ledger['count_note'] = 'Declaration count includes specialized and reused formulations; it is not a count of independent mathematical discoveries.'
    ledger_path.write_text(json.dumps(ledger, indent=2), encoding='utf-8')
print(json.dumps({'replayed_leaves': len(report['leaves']), 'new_declarations': sum(x['accepted_new_declarations'] for x in report['leaves']),
                  'ledger_total': len(ledger['entries']), 'root_conjecture_verified': False}), flush=True)

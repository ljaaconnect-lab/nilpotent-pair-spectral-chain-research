"""Distill the actual reverse-Vandermonde compiler acceptance and frozen hashes."""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
protocol = json.loads((root/'reverse-obligations.json').read_text(encoding='utf-8'))
state = json.loads((root/'reverse-progress.json').read_text(encoding='utf-8'))
last = state['rounds'][-1]
source_hash = hashlib.sha256((root/'ReverseVandermonde.lean').read_bytes()).hexdigest()
protocol_hash = hashlib.sha256((root/'reverse-obligations.json').read_bytes()).hexdigest()
extra = ['ReverseVandermonde.unit_monomial_pow',
         'ReverseVandermonde.paper_monomial_matrix_eq',
         'ReverseVandermonde.paper_monomial_det']
assert last['exit_code'] == 0 and not last['banned_tokens']
assert not last['unapproved_axioms']
assert source_hash == last['source_sha256']
assert protocol_hash == state['protocol_sha256']
assert len(last['accepted']) == protocol['obligation_count']
assert all(name in last['axiom_audit'] for name in extra)
version = subprocess.run([last['command'][0], '--version'], capture_output=True,
                         check=True, timeout=20).stdout.decode('utf-8').strip()
report = {
    'node': 'n58', 'dev_score': state['dev_score'],
    'metric': 'accepted_frozen_obligations / 6',
    'compiler_exit_code': last['exit_code'], 'lean_version': version,
    'complete_rounds': state['complete_rounds'],
    'complete_round_budget': protocol['complete_candidate_budget'],
    'import_name_probes': 1, 'tactic_probes': 0,
    'domain': protocol['domain'],
    'accepted': last['accepted'], 'additional_verified': extra,
    'axiom_audit': last['axiom_audit'],
    'unapproved_axioms': last['unapproved_axioms'],
    'source_sha256': source_hash, 'protocol_sha256': protocol_hash,
    'includes_n_zero_and_one': True,
    'orientation': 'product over i<l of v_i-v_l',
    'proof_route': 'Matrix.det_projVandermonde specialized at const1,v',
    'n55_interface': 'The verified raw monomial matrix is the definitional '
        'unfolding of reverseMatrix(baseLabels n)(baseCaps n). The named '
        'n55 module is not imported by this self-contained artifact.',
    'root_conjecture_verified': False, 'held_out_accessed': False,
    'counterexample_generation': False,
    'result': 'Exact reverse Vandermonde, complementary subtraction, and '
              'the paper-entry monomial determinant formula verified.',
    'remaining_constructive_obligation':
        'Construct a polynomial-size scalar circuit for the required central '
        'coefficient, without treating projection or extraction as free.'
}
(root/'reverse-report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'dev_score': report['dev_score'],
                  'complete_rounds': report['complete_rounds'],
                  'additional_verified': extra}, indent=2))

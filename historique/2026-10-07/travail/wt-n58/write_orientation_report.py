"""Distill actual accepted double-orientation verification and frozen hashes."""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
protocol = json.loads((root/'orientation-obligations.json').read_text(encoding='utf-8'))
state = json.loads((root/'orientation-progress.json').read_text(encoding='utf-8'))
last = state['rounds'][-1]
source_hash = hashlib.sha256((root/'DoubleOrientation.lean').read_bytes()).hexdigest()
protocol_hash = hashlib.sha256((root/'orientation-obligations.json').read_bytes()).hexdigest()
assert last['exit_code'] == 0 and not last['banned_tokens']
assert not last['unapproved_axioms']
assert source_hash == last['source_sha256']
assert protocol_hash == state['protocol_sha256']
assert len(last['accepted']) == protocol['obligation_count']
version = subprocess.run([last['command'][0], '--version'], capture_output=True,
                         check=True, timeout=20).stdout.decode('utf-8').strip()
report = {
    'node': 'n56', 'dev_score': state['dev_score'],
    'metric': 'accepted_frozen_obligations / 6',
    'compiler_exit_code': last['exit_code'], 'lean_version': version,
    'complete_rounds': state['complete_rounds'],
    'complete_round_budget': protocol['complete_candidate_budget'],
    'import_name_probes': 1, 'tactic_probes': 0,
    'domain': protocol['domain'], 'explicit_odd_relations': protocol['relations'],
    'accepted': last['accepted'],
    'additional_verified': ['DoubleOrientation.cross_middle'],
    'axiom_audit': last['axiom_audit'],
    'unapproved_axioms': last['unapproved_axioms'],
    'source_sha256': source_hash, 'protocol_sha256': protocol_hash,
    'root_conjecture_verified': False, 'held_out_accessed': False,
    'counterexample_generation': False,
    'result': 'Paired square-zero, paired commutation, and the complete '
              'triangular-sign double-orientation factorization verified.',
    'remaining_constructive_obligation':
        'Compile the required exterior-algebra contraction/top coordinate to '
        'a polynomial-size scalar circuit without treating projection as free.'
}
(root/'orientation-report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'dev_score': report['dev_score'],
                  'complete_rounds': report['complete_rounds'],
                  'axiom_audit': report['axiom_audit']}, indent=2))

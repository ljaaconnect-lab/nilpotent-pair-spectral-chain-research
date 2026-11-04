"""Distill a completed compiler run without rerunning or modifying Lean."""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
protocol = json.loads((root/'rank-one-obligations.json').read_text(encoding='utf-8'))
state = json.loads((root/'rank-one-progress.json').read_text(encoding='utf-8'))
last = state['rounds'][-1]
source_hash = hashlib.sha256((root/'RankOneSquareZero.lean').read_bytes()).hexdigest()
protocol_hash = hashlib.sha256((root/'rank-one-obligations.json').read_bytes()).hexdigest()
assert last['exit_code'] == 0 and not last['banned_tokens']
assert not last['unapproved_axioms']
assert source_hash == last['source_sha256']
assert protocol_hash == state['protocol_sha256']
assert len(last['accepted']) == protocol['obligation_count']
version = subprocess.run([last['command'][0], '--version'], capture_output=True,
                         check=True, timeout=20).stdout.decode('utf-8').strip()
report = {
    'node': 'n39', 'dev_score': state['dev_score'],
    'metric': 'accepted_frozen_obligations / 5',
    'compiler_exit_code': last['exit_code'], 'lean_version': version,
    'complete_rounds': state['complete_rounds'],
    'complete_round_budget': protocol['complete_candidate_budget'],
    'accepted': last['accepted'],
    'additional_verified': ['SquareZeroRankOne.propagate_rank_one'],
    'axiom_audit': last['axiom_audit'],
    'unapproved_axioms': last['unapproved_axioms'],
    'source_sha256': source_hash, 'protocol_sha256': protocol_hash,
    'root_conjecture_verified': False, 'held_out_accessed': False,
    'result': 'Explicit scalar and matrix square-zero update products verified.',
    'remaining_constructive_obligation':
        'Instantiate the quotient-ring updates and compile coefficient contraction '
        'to a polynomial-size scalar circuit with cheap initialized data.'
}
(root/'rank-one-report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'dev_score': report['dev_score'],
                  'complete_rounds': report['complete_rounds'],
                  'additional_verified': report['additional_verified']}, indent=2))

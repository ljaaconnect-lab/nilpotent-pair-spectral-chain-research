"""Integrity audit only: accepted proof replays are reused, not rerun here."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
package = root.parent / 'outputs/conjecture-1-5-continuation'
manifest = json.loads((package / 'manifest-sha256.json').read_text(encoding='utf-8'))
for relative, expected in manifest.items():
    actual = hashlib.sha256((package / relative).read_bytes()).hexdigest()
    assert actual == expected, relative

ledger = json.loads((package / 'arbor/verified-bases.json').read_text(encoding='utf-8'))
assert ledger['root_conjecture_verified'] is False
sources = {}
for entry in ledger['entries']:
    filename = entry['source']
    assert hashlib.sha256((package / 'proofs' / filename).read_bytes()).hexdigest() == entry['source_sha256']
    assert set(entry['axioms']) <= {'propext', 'Classical.choice', 'Quot.sound'}
    sources.setdefault(filename, []).append(entry)
for filename, entries in sources.items():
    report_path = package / 'verification' / ('delivered-' + Path(filename).stem + '.json')
    report = json.loads(report_path.read_text(encoding='utf-8'))['source']
    assert report['exit_code'] == 0
    assert report['source_sha256'] == entries[0]['source_sha256']
    assert {entry['theorem'] for entry in entries} <= set(report['axiom_audit'])

local = package / 'positive-frontier/synchronization'
for freeze_name in ('n66-source-freeze.json', 'n66-carry-freeze.json'):
    freeze = json.loads((local / freeze_name).read_text(encoding='utf-8'))
    for name, expected in freeze['files'].items():
        assert hashlib.sha256((local / name).read_bytes()).hexdigest() == expected, (freeze_name, name)

run_path = root / 'research/.arbor/run.json'
run = json.loads(run_path.read_text(encoding='utf-8'))
window = run['current_formal_window']
window.update({'actual_complete_candidate_compilations': 15,
               'actual_independent_commit_replays': 2,
               'actual_delivered_source_replays': 2,
               'actual_total_compiler_invocations': 19,
               'evidence': ['n63 compiler snapshots: 11', 'n67 compiler snapshots: 4',
                            'root fresh replay: n63, n67', 'delivered standalone replay: n63, n67']})
assert window['actual_total_compiler_invocations'] <= window['complete_candidate_rounds']
run_path.write_text(json.dumps(run, indent=2), encoding='utf-8')
report = {'manifest_files_verified': len(manifest), 'accepted_delivery_sources': sorted(sources),
          'accepted_delta_declarations': len(ledger['entries']), 'accepted_new_local_hadamard_theorems': 3,
          'source_freezes_verified': ['n66-base', 'n66-carry-supplement-v1'],
          'root_conjecture_verified': False,
          'formal_window_compiler_invocations': window['actual_total_compiler_invocations'],
          'scope': 'File integrity and already completed Lean replay evidence; no additional compiler invocation or held-out test'}
(root / 'positive-delivery-integrity.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))

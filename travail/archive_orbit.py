from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import subprocess
import zipfile

root = Path(__file__).resolve().parents[1]
study = root/'etudes/2026-11-01/orbite-scalaire'
lean = json.loads((study/'lean-validation.json').read_text(encoding='utf-8'))
assert lean['status'] == 'passed' and lean['exit_code'] == 0
assert not lean['source_changed_during_check']
assert lean['sha256'] == hashlib.sha256((study/lean['source']).read_bytes()).hexdigest()
assert not lean['full_chain_formalization'] and not lean['general_polynomial_closure']
tests = json.loads((study/'validation.json').read_text(encoding='utf-8'))
assert tests['status'] == 'pass'
assert tests['synthetic_monomial_tables_checked'] == 44
assert tests['phase_frequencies_checked'] == 300
assert tests['stage_coordinates_checked'] == 90252
assert not tests['general_polynomial_closure_proved']
assert tests['conditional_fusion_and_readout_polynomial']
for name, digest in tests['source_sha256'].items():
    assert digest == hashlib.sha256((study/name).read_bytes()).hexdigest()
bridge = json.loads((study/'orbit-bridge-validation.json').read_text(encoding='utf-8'))
assert bridge['status'] == 'pass' and bridge['total_complete_tables'] == 36
assert bridge['formal_z_tables'] == 16
assert bridge['source_sha256'] == hashlib.sha256((study/'verify_orbit_bridge.py').read_bytes()).hexdigest()
assert bridge['collision_observer_sha256'] == hashlib.sha256((study/'collision_observer.py').read_bytes()).hexdigest()
assert bridge['scope']['no_full_scalar_polynomial_compiler_claimed']
assert bridge['scope']['no_initialization_polynomial_bound_claimed']
assert bridge['case_data_sha256'] == hashlib.sha256(json.dumps(
    bridge['cases'], sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
ntt = json.loads((study/'spectral-projector-validation.json').read_text(encoding='utf-8'))
assert ntt['status'] == 'pass'
assert ntt['coefficient_vectors_checked'] == 22 and ntt['synthetic_cases_checked'] == 44
assert ntt['frequencies_checked'] == 300 and ntt['full_inverse_ntt_tables_checked'] == 44
assert not ntt['general_polynomial_closure_proved'] and not ntt['observation_initialization_included']
assert ntt['coefficient_wires_shared_across_all_N_frequencies']
for name, digest in ntt['source_sha256'].items():
    assert digest == hashlib.sha256((study/name).read_bytes()).hexdigest()
assert ntt['synthetic_cases_source_sha256'] == hashlib.sha256(
    (study/ntt['synthetic_cases_source']).read_bytes()).hexdigest()
raw = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                     cwd=root, capture_output=True, check=True).stdout
files = sorted(set(x.decode('utf-8') for x in raw.split(b'\0') if x))
files.remove('manifeste.json')
manifest = {'date': '2026-11-01', 'sha256': {
    name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in files}}
(root/'manifeste.json').write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
archive = root/'exports/projet-annihilation-orbite-scalaire-2026-11-01.zip'
prefix = 'projet-annihilation-collision-orientee/'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as output:
    for name in files+['manifeste.json']:
        output.write(root/name, prefix+name)
with zipfile.ZipFile(archive) as incoming:
    assert set(incoming.namelist()) == {prefix+name for name in files+['manifeste.json']}
    for name, digest in manifest['sha256'].items():
        assert hashlib.sha256(incoming.read(prefix+name)).hexdigest() == digest, name
    assert incoming.read(prefix+'manifeste.json') == (root/'manifeste.json').read_bytes()

class Index(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.details = [], 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'details' and attrs.get('class') == 'essai':
            self.details += 1
        if tag == 'a':
            link = attrs.get('href', '')
            if link and not link.startswith(('#', 'http:', 'https:')):
                self.links.append(link.split('#')[0])

index = Index()
index.feed((root/'index.html').read_text(encoding='utf-8'))
assert index.details == len(json.loads((root/'catalogue.json').read_text(encoding='utf-8'))) == 99
assert not [name for name in index.links if not (root/name).exists()]
print(json.dumps({'files': len(files), 'study_count': index.details,
                  'archive': str(archive), 'archive_bytes': archive.stat().st_size,
                  'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}, indent=2))

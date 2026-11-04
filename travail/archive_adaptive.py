from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import subprocess
import zipfile

root = Path(__file__).resolve().parents[1]
study = root/'etudes/2026-11-01/fermeture-adaptative'
lean = json.loads((study/'lean-validation.json').read_text(encoding='utf-8'))
assert lean['status'] == 'passed' and lean['exit_code'] == 0
assert not lean['source_changed_during_check']
assert lean['sha256'] == hashlib.sha256((study/lean['source']).read_bytes()).hexdigest()
assert not lean['full_chain_formalization'] and not lean['general_polynomial_closure']
tests = json.loads((study/'validation.json').read_text(encoding='utf-8'))
assert tests['status'] == 'all independent finite-order checks passed'
assert tests['numeric_spectral_tables_checked'] == 14
assert tests['formal_z_spectral_tables_checked'] == 5
assert not tests['general_polynomial_closure_proved']
for name, digest in tests['source_sha256'].items():
    assert digest == hashlib.sha256((study/name).read_bytes()).hexdigest()
shared = json.loads((study/'shared-resolvent-validation.json').read_text(encoding='utf-8'))
assert shared['status'] == 'pass' and shared['test_cases'] == 30
assert shared['source_sha256'] == hashlib.sha256((study/shared['verifier']).read_bytes()).hexdigest()
assert shared['scope']['not_a_scalar_polynomial_compiler']
assert shared['case_data_sha256'] == hashlib.sha256(json.dumps(
    shared['cases'], sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
raw = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                     cwd=root, capture_output=True, check=True).stdout
files = sorted(set(x.decode('utf-8') for x in raw.split(b'\0') if x))
files.remove('manifeste.json')
manifest = {'date': '2026-11-01', 'sha256': {
    name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in files}}
(root/'manifeste.json').write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
archive = root/'exports/projet-annihilation-schur-jet-2026-11-01.zip'
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
assert index.details == len(json.loads((root/'catalogue.json').read_text(encoding='utf-8'))) == 98
assert not [name for name in index.links if not (root/name).exists()]
print(json.dumps({'files': len(files), 'study_count': index.details,
                  'archive': str(archive), 'archive_bytes': archive.stat().st_size,
                  'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}, indent=2))

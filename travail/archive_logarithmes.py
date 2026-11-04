from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import subprocess
import zipfile

root = Path(__file__).resolve().parents[1]
study = root/'etudes/2026-11-01/logarithmes-chaine'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

report = json.loads((study/'log-circuit-validation.json').read_text(encoding='utf-8'))
assert report['status'] == 'passed'
assert not report['general_polynomial_closure'] and not report['general_quasipolynomial_closure']
for name, digest in report['source_sha256'].items():
    assert sha(study.parent/name) == digest, name
assert sum(c['tables'] for c in report['cases']) == 40
assert sum(c['intermediate_epsilon_jets'] for c in report['cases']) == 200
assert sum(c['formal_z_tables'] for c in report['cases']) == 3
assert [c['complete_chain_scalar_gates'] for c in report['cases']] == [10, 145, 1215, 18114, 184673]
lean = json.loads((study/'lean/log-lean-validation.json').read_text(encoding='utf-8'))
assert lean['status'] == 'passed' and lean['exit_code'] == 0
assert lean['sha256'] == sha(study/'lean'/lean['source'])
assert not any(word in lean['stdout']+lean['stderr'] for word in ('sorryAx', 'warning:', 'error:'))

raw = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                     cwd=root, capture_output=True, check=True).stdout
files = sorted(set(x.decode('utf-8') for x in raw.split(b'\0') if x))
files.remove('manifeste.json')
manifest = {'date': '2026-11-01', 'sha256': {name: sha(root/name) for name in files}}
(root/'manifeste.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
archive = root/'exports/projet-annihilation-logarithmes-2026-11-01.zip'
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
assert index.details == len(json.loads((root/'catalogue.json').read_text(encoding='utf-8'))) == 101
assert not [name for name in index.links if not (root/name).exists()]
print(json.dumps({'files': len(files), 'study_count': index.details,
                  'archive': str(archive), 'archive_bytes': archive.stat().st_size,
                  'archive_sha256': sha(archive)}, indent=2))

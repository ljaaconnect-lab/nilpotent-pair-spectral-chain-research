"""Package exact committed research artifacts, without transient worktree files."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

BASE = Path(__file__).resolve().parents[1]
WORK = BASE/'work'
REPO = WORK/'chain-search'


def git(*args):
    return subprocess.check_output(['git','-C',str(REPO),*args])


def package(refs):
    target = BASE/'outputs'/'chaine_orientee_spectrale_2026-10-24.zip'
    manifest = {'general_polynomial_resolution_obtained':False,
                'paper_sha256':'ed1f05cd132305ec98ec4f195ae395123cc4ae68e1a137ac4a78898f4d5199f4',
                'snapshots':{},'files_sha256':{}}
    contents = {'LIRE.txt':(WORK/'LIRE_CHAINE.txt').read_bytes(),
                'construction_exacte_chaine.txt':(BASE/'outputs'/'construction_exacte_chaine.txt').read_bytes()}
    for folder,ref in refs.items():
        commit = git('rev-parse',ref).decode().strip()
        manifest['snapshots'][folder] = commit
        with zipfile.ZipFile(io.BytesIO(git('archive','--format=zip',commit))) as z:
            for name in z.namelist():
                if not name.endswith('/'):
                    contents[f'{folder}/{name}'] = z.read(name)
    for name in ['CHAIN_CONTRACT_20261024.md','chain-baseline-heldout.json',
                 'chain-normalization-heldout.json','gaussian-independent.json',
                 'review_gaussian.py','gaussian-polarization-independent.json',
                 'review_polarization.py']:
        path = WORK/name
        if path.exists():
            contents['coordinator/'+name] = path.read_bytes()
    for name in ['tree.json','run.json']:
        contents['arbor/'+name] = (REPO/'.arbor'/name).read_bytes()
    contents['coordinator/package_chain.py'] = Path(__file__).read_bytes()
    contents['history.bundle'] = (WORK/'chain-history.bundle').read_bytes()
    for name,data in sorted(contents.items()):
        manifest['files_sha256'][name] = hashlib.sha256(data).hexdigest()
    contents['manifest.json'] = json.dumps(manifest,ensure_ascii=False,indent=2).encode()
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(contents.items()):
            z.writestr(name,data)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for name,sha in manifest['files_sha256'].items():
            assert hashlib.sha256(z.read(name)).hexdigest()==sha
    print(json.dumps({'path':str(target),'files':len(contents),'bytes':target.stat().st_size,
                      'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                      'snapshots':manifest['snapshots']},indent=2))


if __name__=='__main__':
    refs=json.loads((WORK/'package_refs.json').read_text())
    package(refs)

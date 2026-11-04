"""Fetch pinned Mathlib sources and a workspace-only Git HTTPS runtime."""
from pathlib import Path
import hashlib, json, tarfile, urllib.request, zipfile

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / 'mathlib'
DOWNLOAD = ROOT / 'dependency-downloads'
DOWNLOAD.mkdir(exist_ok=True)

def get(url, dest):
    if dest.exists():
        print('reusing', dest.name, flush=True)
        return
    request = urllib.request.Request(url, headers={'User-Agent': 'Codex-Mathlib-Bootstrap'})
    with urllib.request.urlopen(request, timeout=120) as src, dest.open('wb') as out:
        while chunk := src.read(1024 * 1024):
            out.write(chunk)
    print('downloaded', dest.name, dest.stat().st_size, flush=True)

archive = DOWNLOAD / 'mathlib-v4.34.1.tar.gz'
get('https://codeload.github.com/leanprover-community/mathlib4/tar.gz/refs/tags/v4.34.1', archive)
if not TARGET.exists():
    with tarfile.open(archive) as src:
        src.extractall(DOWNLOAD, filter='data')
    (DOWNLOAD / 'mathlib4-4.34.1').rename(TARGET)
print('toolchain', (TARGET / 'lean-toolchain').read_text().strip(), flush=True)

api = urllib.request.Request('https://api.github.com/repos/git-for-windows/git/releases/latest',
    headers={'User-Agent': 'Codex-Mathlib-Bootstrap'})
with urllib.request.urlopen(api, timeout=60) as src:
    release = json.load(src)
assets = [a for a in release['assets'] if a['name'].startswith('MinGit-')
          and a['name'].endswith('-64-bit.zip') and 'busybox' not in a['name']]
if len(assets) != 1:
    raise RuntimeError('Expected one MinGit x64 release asset')
asset = assets[0]
git_zip = DOWNLOAD / asset['name']
get(asset['browser_download_url'], git_zip)
if asset.get('digest'):
    expected = asset['digest'].removeprefix('sha256:')
    actual = hashlib.sha256(git_zip.read_bytes()).hexdigest()
    if expected != actual:
        raise RuntimeError('Git release digest mismatch')
git_dir = ROOT / 'git-runtime'
git_dir.mkdir(exist_ok=True)
with zipfile.ZipFile(git_zip) as src:
    for info in src.infolist():
        target = (git_dir / info.filename).resolve()
        if not target.is_relative_to(git_dir.resolve()):
            raise RuntimeError('Unsafe archive path')
    src.extractall(git_dir)
report = {'mathlib_tag': 'v4.34.1', 'mathlib_archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
          'git_tag': release['tag_name'], 'git_asset': asset['name'],
          'git_asset_sha256': hashlib.sha256(git_zip.read_bytes()).hexdigest(),
          'git_release_digest': asset.get('digest')}
(ROOT / 'dependency-bootstrap.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report), flush=True)

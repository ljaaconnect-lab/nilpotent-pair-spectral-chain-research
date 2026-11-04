from pathlib import Path
import os, subprocess
ROOT = Path(__file__).resolve().parent
env = os.environ.copy()
env['LC_ALL'] = 'C'
env['LANG'] = 'C'
env['GIT_SSL_CAINFO'] = str(ROOT / 'git-runtime/ucrt64/etc/ssl/certs/ca-bundle.crt')
git = ROOT / 'git-runtime/cmd/git.exe'
cmd = [str(git), '-c', 'http.sslBackend=openssl',
       'ls-remote', 'https://github.com/leanprover-community/plausible', 'HEAD']
result = subprocess.run(cmd, env=env, capture_output=True, timeout=90)
print('exit', result.returncode, flush=True)
for stream in [result.stdout, result.stderr]:
    try:
        print(stream.decode('utf-8'), flush=True)
    except UnicodeDecodeError:
        print(stream.decode('cp1252', errors='replace'), flush=True)

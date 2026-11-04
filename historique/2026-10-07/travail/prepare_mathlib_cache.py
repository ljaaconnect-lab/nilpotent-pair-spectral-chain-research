from pathlib import Path
import json, os, subprocess, time
ROOT = Path(__file__).resolve().parent
MATHLIB = ROOT / 'mathlib'
BIN = Path('C:/Users/REGIS/Documents/Codex/runtimes/elan/toolchains/leanprover--lean4---v4.34.1/bin')
GITBIN = ROOT / 'git-runtime' / 'cmd'
env = os.environ.copy()
env['PATH'] = str(GITBIN) + os.pathsep + str(BIN) + os.pathsep + 'C:/msys64/mingw64/bin' + os.pathsep + env['PATH']
env['ELAN_HOME'] = 'C:/Users/REGIS/Documents/Codex/runtimes/elan'
env['MATHLIB_CACHE_DIR'] = str(ROOT / 'mathlib-cache')
env['GIT_SSL_CAINFO'] = str(ROOT / 'git-runtime/ucrt64/etc/ssl/certs/ca-bundle.crt')
env['CURL_CA_BUNDLE'] = env['GIT_SSL_CAINFO']
env['LC_ALL'] = 'C'
env['LANG'] = 'C'
count = int(env.get('GIT_CONFIG_COUNT', '0'))
for key, value in [('http.sslBackend', 'openssl')]:
    env[f'GIT_CONFIG_KEY_{count}'] = key
    env[f'GIT_CONFIG_VALUE_{count}'] = value
    count += 1
env['GIT_CONFIG_COUNT'] = str(count)
# All sources and precompiled artifacts stay inside the authorized workspace.
modules = ['Mathlib.LinearAlgebra.Matrix.Determinant.Basic',
           'Mathlib.LinearAlgebra.Vandermonde', 'Mathlib.Algebra.Polynomial.Basic',
           'Mathlib.Algebra.Polynomial.Coeff', 'Mathlib.Tactic.Ring']
command = [str(BIN / 'lake.exe'), 'exe', 'cache', 'get',
           '--repo=leanprover-community/mathlib4', *modules]
log_path = ROOT / 'mathlib-preparation.log'
start = time.monotonic()
with log_path.open('w', encoding='utf-8') as log:
    # Fetch only pinned commits for missing dependencies, avoiding full history.
    manifest = json.loads((MATHLIB / 'lake-manifest.json').read_text())
    for package in manifest['packages']:
        directory = MATHLIB / manifest['packagesDir'] / package['name']
        git_cmd = [str(GITBIN / 'git.exe'), '-c', 'safe.directory=' + directory.as_posix(), '-C', str(directory)]
        head = subprocess.run([*git_cmd, 'rev-parse', 'HEAD'], env=env,
                              capture_output=True, encoding='utf-8', errors='replace')
        if head.returncode == 0 and head.stdout.strip() == package['rev']:
            continue
        directory.mkdir(parents=True, exist_ok=True)
        subprocess.run([*git_cmd, 'init'], env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        remote = subprocess.run([*git_cmd, 'remote', 'get-url', 'origin'], env=env,
                                capture_output=True, encoding='utf-8', errors='replace')
        if remote.returncode != 0:
            subprocess.run([*git_cmd, 'remote', 'add', 'origin', package['url']], env=env,
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        print('fetching pinned', package['name'], package['rev'], flush=True)
        subprocess.run([*git_cmd, 'fetch', '--depth', '1', 'origin', package['rev']], env=env,
                       stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
        subprocess.run([*git_cmd, 'checkout', '--detach', package['rev']], env=env,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    result = subprocess.run(command, cwd=MATHLIB, env=env, stdout=log,
                            stderr=subprocess.STDOUT, encoding='utf-8')
report = {'command': command, 'cwd': str(MATHLIB), 'exit_code': result.returncode,
          'elapsed_seconds': time.monotonic() - start, 'log': str(log_path),
          'version': 'v4.34.1', 'requested_modules': modules}
(ROOT / 'mathlib-preparation.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report), flush=True)
print(log_path.read_text(encoding='utf-8')[-3500:], flush=True)
raise SystemExit(result.returncode)

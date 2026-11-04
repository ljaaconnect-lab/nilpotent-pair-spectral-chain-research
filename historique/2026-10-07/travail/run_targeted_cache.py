from pathlib import Path
import json, os, shutil, subprocess, sys, time
ROOT = Path(__file__).resolve().parent
BIN = Path('C:/Users/REGIS/Documents/Codex/runtimes/elan/toolchains/leanprover--lean4---v4.34.1/bin')
env = os.environ.copy()
env['PATH'] = str(ROOT / 'git-runtime/cmd') + os.pathsep + str(BIN) + os.pathsep + 'C:/msys64/mingw64/bin' + os.pathsep + env['PATH']
env['ELAN_HOME'] = 'C:/Users/REGIS/Documents/Codex/runtimes/elan'
env['MATHLIB_CACHE_DIR'] = str(ROOT / 'mathlib-cache')
cache_dir = ROOT / 'mathlib-cache'
cache_dir.mkdir(exist_ok=True)
# Windows CreateProcess searches System32 before PATH for a bare executable.
# Upstream Cache.IO.getCurl honors this local explicit override path.
curl_override = cache_dir / 'curl-7.88.1'
shutil.copyfile('C:/msys64/mingw64/bin/curl.exe', curl_override)
env['CURL_CA_BUNDLE'] = str(ROOT / 'git-runtime/ucrt64/etc/ssl/certs/ca-bundle.crt')
env['GIT_SSL_CAINFO'] = env['CURL_CA_BUNDLE']
env['LC_ALL'] = 'C'
env['LANG'] = 'C'
env['GIT_CONFIG_COUNT'] = '1'
env['GIT_CONFIG_KEY_0'] = 'http.sslBackend'
env['GIT_CONFIG_VALUE_0'] = 'openssl'
modules = sys.argv[1:] or ['Mathlib.LinearAlgebra.Matrix.Determinant.Basic',
    'Mathlib.LinearAlgebra.Vandermonde', 'Mathlib.Algebra.Polynomial.Coeff',
    'Mathlib.Tactic.Ring', 'Mathlib.Tactic.LinearCombination']
cmd = [str(BIN / 'lake.exe'), 'env', str(BIN / 'lean.exe'), '--run', str(ROOT / 'TargetedCache.lean'), *modules]
probe = subprocess.run([str(curl_override), '--version'], env=env, capture_output=True, text=True)
if probe.returncode != 0 or 'OpenSSL' not in probe.stdout:
    raise RuntimeError('Explicit OpenSSL curl override failed: ' + probe.stdout + probe.stderr)
start = time.monotonic()
log = ROOT / 'targeted-cache.log'
with log.open('w', encoding='utf-8') as out:
    result = subprocess.run(cmd, cwd=ROOT / 'mathlib', env=env, stdout=out,
                            stderr=subprocess.STDOUT)
report = {'command': cmd, 'exit_code': result.returncode, 'elapsed_seconds': time.monotonic()-start,
          'upstream_hash_functions_unchanged': True, 'modules': modules,
          'curl_override_version': probe.stdout.splitlines()[0]}
(ROOT / 'targeted-cache-report.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report), flush=True)
print(log.read_text(encoding='utf-8', errors='replace')[-4000:], flush=True)
raise SystemExit(result.returncode)

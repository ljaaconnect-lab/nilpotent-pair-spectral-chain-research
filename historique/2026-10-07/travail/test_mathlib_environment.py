from pathlib import Path
import json, os, subprocess, sys
ROOT = Path(__file__).resolve().parent
BIN = Path('C:/Users/REGIS/Documents/Codex/runtimes/elan/toolchains/leanprover--lean4---v4.34.1/bin')
env = os.environ.copy()
env['PATH'] = str(ROOT / 'git-runtime/cmd') + os.pathsep + str(BIN) + os.pathsep + env['PATH']
env['ELAN_HOME'] = 'C:/Users/REGIS/Documents/Codex/runtimes/elan'
cmd = [str(BIN / 'lake.exe'), 'env', str(BIN / 'lean.exe'), str(ROOT / 'MathlibSmoke.lean')]
result = subprocess.run(cmd, cwd=ROOT / 'mathlib', env=env, capture_output=True, text=True, encoding='utf-8')
report = {'command': cmd, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
(ROOT / 'mathlib-smoke-report.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report), flush=True)
if result.returncode == 0:
    exported = subprocess.run([str(BIN / 'lake.exe'), 'env', sys.executable,
        str(ROOT / 'export_lean_environment.py')], cwd=ROOT / 'mathlib', env=env, capture_output=True,
        text=True, encoding='utf-8')
    print(exported.stdout, flush=True)
    if exported.returncode:
        raise RuntimeError(exported.stderr)
raise SystemExit(result.returncode)

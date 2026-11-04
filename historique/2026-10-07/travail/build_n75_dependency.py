"""One counted, local Lean invocation for the pinned SchurComplement module."""
import hashlib, json, os, subprocess, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent
WT = ROOT / 'wt-n75'
MATHLIB = ROOT / 'mathlib'
LEAN = Path('C:/Users/REGIS/Documents/Codex/runtimes/elan/toolchains/leanprover--lean4---v4.34.1/bin/lean.exe')
SOURCE = MATHLIB / 'Mathlib/LinearAlgebra/Matrix/SchurComplement.lean'
TARGET = MATHLIB / '.lake/build/lib/lean/Mathlib/LinearAlgebra/Matrix/SchurComplement.olean'
REPORT = WT / 'n75-dependency-build.json'
if REPORT.exists():
    raise SystemExit('This dependency invocation has already been attempted')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
prepared = json.loads((ROOT/'mathlib-environment.json').read_text(encoding='utf-8-sig'))
env = os.environ.copy(); env.update(prepared)
command = [str(LEAN), '-o', str(TARGET), str(SOURCE)]
started = time.monotonic()
try:
    p = subprocess.run(command, cwd=MATHLIB, env=env, capture_output=True, timeout=600)
    code, out, err = p.returncode, p.stdout, p.stderr
except subprocess.TimeoutExpired as e:
    code, out, err = 124, e.stdout or b'', e.stderr or b''
report = {'node':'n75','kind':'dependency_build','actual_compiler_invocations':1,
          'command':command,'source_sha256':sha(SOURCE),'exit_code':code,
          'elapsed_seconds':time.monotonic()-started,
          'stdout':out.decode('utf-8',errors='replace'),'stderr':err.decode('utf-8',errors='replace'),
          'environment':prepared,'compiled_sha256':sha(TARGET) if code==0 else None}
REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ('kind','exit_code','elapsed_seconds','stdout','stderr')},indent=2))
raise SystemExit(code)

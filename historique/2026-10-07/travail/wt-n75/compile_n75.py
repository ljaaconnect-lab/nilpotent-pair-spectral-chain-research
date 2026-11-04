"""One sequential n75 compiler invocation, capped at eight of every kind."""
import atexit
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
LEAN = Path(r"C:\Users\REGIS\Documents\Codex\runtimes\elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe")
SOURCE = ROOT / "AtomicFirstPrefix.lean"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

lock = ROOT / ".n75-compile-lock"
with lock.open("x", encoding="ascii") as handle:
    handle.write(str(os.getpid()))
atexit.register(lambda: lock.unlink(missing_ok=True))
logs = ROOT / "n75-compiler-rounds"
logs.mkdir(exist_ok=True)
previous = list(logs.glob("round-*.json"))
if len(previous) >= 7:
    raise SystemExit("n75 budget exhausted: one coordinator dependency build + seven candidates")
environment_file = WORK / "mathlib-environment.json"
prepared = json.loads(environment_file.read_text(encoding="utf-8-sig"))
imports = {}
for name in ["Mathlib.LinearAlgebra.Matrix.SchurComplement", "Mathlib.Algebra.BigOperators.Group.Finset.Powerset", "Mathlib.Tactic.Ring"]:
    relative = Path(*name.split("."))
    src = WORK / "mathlib" / relative.with_suffix(".lean")
    obj = WORK / "mathlib/.lake/build/lib/lean" / relative.with_suffix(".olean")
    if not src.is_file() or not obj.is_file():
        raise SystemExit(f"Missing import, no Lean invocation made: {name}")
    imports[name] = {"source_sha256": sha(src), "compiled_sha256": sha(obj)}
provenance = {"compiler_path": str(LEAN), "compiler_sha256": sha(LEAN),
              "environment_sha256": sha(environment_file), "imports": imports,
              "cache_mutated": False, "outputs_accessed": False,
              "inherited_cache_used": False}
prov_file = ROOT / "n75-dependency-provenance.json"
if prov_file.exists():
    if json.loads(prov_file.read_text(encoding="utf-8")) != provenance:
        raise SystemExit("Frozen import provenance changed")
else:
    prov_file.write_text(json.dumps(provenance, indent=2), encoding="utf-8")
number = len(previous) + 1
snapshot = logs / f"round-{number:02d}-source.lean"
snapshot.write_bytes(SOURCE.read_bytes())
env = os.environ.copy()
env.update(prepared)
env["LEAN_PATH"] = str(ROOT) + os.pathsep + prepared["LEAN_PATH"]
command = [str(LEAN), "-o", str(SOURCE.with_suffix(".olean")), str(SOURCE)]
started = time.monotonic()
try:
    p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=600)
    code, stdout, stderr = p.returncode, p.stdout, p.stderr
except subprocess.TimeoutExpired as e:
    code, stdout, stderr = 124, e.stdout or b"", e.stderr or b""
report = {"node": "n75", "round": number, "kind": "candidate", "source_sha256": sha(snapshot),
          "external_dependency_invocations": 1, "n75_total_invocations_so_far": number + 1,
          "snapshot": str(snapshot.relative_to(ROOT)), "command": command, "cwd": str(ROOT),
          "environment": {k: env[k] for k in ["LEAN_PATH", "LEAN_SRC_PATH", "LEAN_SYSROOT"]},
          "frozen_protocol_sha256": sha(ROOT / "n75-protocol.json"),
          "formal_contract_sha256": sha(ROOT / "n75-formal-contract.json"),
          "dependency_provenance_sha256": sha(prov_file),
          "elapsed_seconds": time.monotonic() - started, "timeout_seconds": 600,
          "exit_code": code, "stdout": stdout.decode("utf-8", errors="replace"),
          "stderr": stderr.decode("utf-8", errors="replace"), "root_conjecture_verified": False}
(logs / f"round-{number:02d}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({k: report[k] for k in ["node", "round", "exit_code", "stdout", "stderr"]}, indent=2))
raise SystemExit(code)

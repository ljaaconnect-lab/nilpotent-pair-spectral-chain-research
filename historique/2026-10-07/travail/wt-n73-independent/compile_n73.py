"""Compile n73 sources sequentially; eight total Lean invocations of any kind."""
import argparse
import atexit
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENVIRONMENT = ROOT.parent / "mathlib-environment.json"
CACHE = ROOT.parent / "delivered-proof-cache"
DELIVERED = ROOT.parent.parent / "outputs/conjecture-1-5-suite/proofs"
LEAN = Path(r"C:\Users\REGIS\Documents\Codex\runtimes\elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument("--source", default="ActualClosedSubsetTransfer.lean")
args = parser.parse_args()
source = ROOT / args.source
if source.parent != ROOT or source.suffix != ".lean":
    raise SystemExit("Only local n73 Lean source may be compiled")
lock = ROOT / ".n73-compile-lock"
try:
    with lock.open("x", encoding="ascii") as handle:
        handle.write(str(os.getpid()))
except FileExistsError:
    raise SystemExit("A compiler runner is still active; wait for its final exit")
atexit.register(lambda: lock.unlink(missing_ok=True))
logs = ROOT / "n73-compiler-rounds"
logs.mkdir(exist_ok=True)
previous = [json.loads(p.read_text(encoding="utf-8")) for p in logs.glob("round-*.json")]
if len(previous) >= 8:
    raise SystemExit("n73 total invocation budget exhausted")
replay_file = CACHE / "replay-report.json"
replay = json.loads(replay_file.read_text(encoding="utf-8"))
dependencies = {}
for record in replay["sources"]:
    delivered = DELIVERED / record["source"]
    compiled = CACHE / Path(record["source"]).with_suffix(".olean")
    if record["exit_code"] != 0 or not delivered.is_file() or sha(delivered) != record["source_sha256"] or not compiled.is_file():
        raise SystemExit(f"Inherited cache provenance rejected: {record['source']}")
    dependencies[record["source"]] = {
        "source_path": str(delivered), "source_sha256": sha(delivered),
        "compiled_path": str(compiled), "compiled_sha256": sha(compiled),
        "prior_replay_exit_code": record["exit_code"],
    }
provenance_path = ROOT / "n73-dependency-provenance.json"
provenance = {
    "replay_report": str(replay_file), "replay_report_sha256": sha(replay_file),
    "dependencies": dependencies, "cache_mutated": False,
    "compiler_path": str(LEAN), "compiler_sha256": sha(LEAN),
    "environment_source": str(ENVIRONMENT), "environment_sha256": sha(ENVIRONMENT),
    "note": "Prior coordinator replay certifies each delivered source hash with exit zero; existing compiled cache bytes are frozen here before n73 import",
}
if provenance_path.exists():
    if json.loads(provenance_path.read_text(encoding="utf-8")) != provenance:
        raise SystemExit("Frozen inherited dependency provenance changed")
else:
    provenance_path.write_text(json.dumps(provenance, indent=2), encoding="utf-8")
number = len(previous) + 1
snapshot = logs / f"round-{number:02d}-source.lean"
source_bytes = source.read_bytes()
snapshot.write_bytes(source_bytes)
command = [str(LEAN), "-o", str(source.with_suffix(".olean")), str(source)]
prepared = json.loads(ENVIRONMENT.read_text(encoding="utf-8-sig"))
env = os.environ.copy()
env.update(prepared)
env["LEAN_PATH"] = str(ROOT) + os.pathsep + str(CACHE) + os.pathsep + prepared["LEAN_PATH"]
started = time.monotonic()
try:
    proc = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=600)
    exit_code, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
except subprocess.TimeoutExpired as exc:
    exit_code, stdout, stderr = 124, exc.stdout or b"", exc.stderr or b""
report = {
    "node": "n73", "round": number, "kind": "candidate",
    "source": source.name, "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
    "snapshot": str(snapshot.relative_to(ROOT)), "command": command, "cwd": str(ROOT),
    "LEAN_PATH": env["LEAN_PATH"], "LEAN_SRC_PATH": env["LEAN_SRC_PATH"],
    "LEAN_SYSROOT": env["LEAN_SYSROOT"],
    "frozen_protocol_sha256": sha(ROOT / "n73-protocol.json"),
    "formal_contract_sha256": sha(ROOT / "n73-formal-contract.json"),
    "dependency_provenance_sha256": sha(provenance_path),
    "elapsed_seconds": time.monotonic() - started, "timeout_seconds": 600,
    "exit_code": exit_code, "stdout": stdout.decode("utf-8", errors="replace"),
    "stderr": stderr.decode("utf-8", errors="replace"),
    "root_conjecture_verified": False,
}
(logs / f"round-{number:02d}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({key: report[key] for key in
                 ["node", "round", "kind", "exit_code", "stdout", "stderr"]}, indent=2))
raise SystemExit(exit_code)

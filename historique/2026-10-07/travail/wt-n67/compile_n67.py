"""Compile only n67-owned sources using the prepared, read-only Mathlib cache."""
import argparse
import atexit
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENVIRONMENT = ROOT.parent / "mathlib-environment.json"
LEAN = Path(r"C:\Users\REGIS\Documents\Codex\runtimes\elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe")
parser = argparse.ArgumentParser()
parser.add_argument("--source", default="HadamardPfaffian.lean")
parser.add_argument("--dependency", action="store_true")
parser.add_argument("--replay", action="store_true", help="Replay only the exact already-audited frozen source")
args = parser.parse_args()
source = ROOT / args.source
if source.parent != ROOT or source.suffix != ".lean":
    raise SystemExit("Source must be a .lean file directly in the n67 worktree")
lock = ROOT / ".n67-compile-lock"
try:
    with lock.open("x", encoding="ascii") as handle:
        handle.write(str(os.getpid()))
except FileExistsError:
    raise SystemExit("A n67 compiler runner is still active; wait for its final exit code")
atexit.register(lambda: lock.unlink(missing_ok=True))
logs = ROOT / "n67-compiler-rounds"
logs.mkdir(exist_ok=True)
previous = [json.loads(p.read_text(encoding="utf-8")) for p in logs.glob("round-*.json")]
candidate_count = sum(r["kind"] == "candidate" for r in previous)
if args.replay:
    if args.dependency or source.name != "HadamardPfaffian.lean":
        raise SystemExit("A frozen replay must target only HadamardPfaffian.lean")
    frozen = json.loads((ROOT / "n67-strict-report.json").read_text(encoding="utf-8"))
    if (frozen["status"] != "local_gadget_verified" or
        frozen["source_sha256"] != hashlib.sha256(source.read_bytes()).hexdigest() or
        frozen["frozen_contract_sha256"] != hashlib.sha256((ROOT / "n67-protocol.json").read_bytes()).hexdigest() or
        frozen["formal_contract_sha256"] != hashlib.sha256((ROOT / "n67-formal-obligations.json").read_bytes()).hexdigest()):
        raise SystemExit("Frozen replay rejected: source must match the exact accepted artifact")
    bonus_contract = ROOT / "n67-bonus-contract.json"
    if bonus_contract.exists() and frozen.get("bonus_contract_sha256") != hashlib.sha256(bonus_contract.read_bytes()).hexdigest():
        raise SystemExit("Frozen replay rejected: the bonus contract must match the accepted artifact")
if not args.dependency and not args.replay and candidate_count >= 5:
    raise SystemExit("n67 candidate budget exhausted")
number = len(previous) + 1
snapshot = logs / f"round-{number:02d}-source.lean"
source_bytes = source.read_bytes()
snapshot.write_bytes(source_bytes)
command = [str(LEAN)]
if args.dependency:
    command.extend(["-o", str(source.with_suffix(".olean"))])
command.append(str(source))
env = os.environ.copy()
prepared = json.loads(ENVIRONMENT.read_text(encoding="utf-8-sig"))
env.update(prepared)
env["LEAN_PATH"] = str(ROOT) + os.pathsep + prepared["LEAN_PATH"]
try:
    proc = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=180)
    exit_code, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
except subprocess.TimeoutExpired as exc:
    exit_code, stdout, stderr = 124, exc.stdout or b"", exc.stderr or b""
report = {
    "node": "n67", "round": number,
    "candidate_round": candidate_count + (not args.dependency and not args.replay),
    "kind": "dependency_build" if args.dependency else "frozen_replay" if args.replay else "candidate",
    "source": args.source, "snapshot": str(snapshot.relative_to(ROOT)),
    "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
    "command": command, "cwd": str(ROOT), "LEAN_PATH": env["LEAN_PATH"],
    "LEAN_SRC_PATH": env["LEAN_SRC_PATH"], "LEAN_SYSROOT": env["LEAN_SYSROOT"],
    "frozen_contract_sha256": hashlib.sha256((ROOT / "n67-protocol.json").read_bytes()).hexdigest(),
    "formal_contract_sha256": hashlib.sha256((ROOT / "n67-formal-obligations.json").read_bytes()).hexdigest(),
    "bonus_contract_sha256": hashlib.sha256((ROOT / "n67-bonus-contract.json").read_bytes()).hexdigest()
        if (ROOT / "n67-bonus-contract.json").exists() else None,
    "environment_source": str(ENVIRONMENT), "exit_code": exit_code,
    "stdout": stdout.decode("utf-8", errors="replace"),
    "stderr": stderr.decode("utf-8", errors="replace"),
    "root_conjecture_verified": False,
}
(logs / f"round-{number:02d}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({key: report[key] for key in
                 ["node", "round", "candidate_round", "kind", "source", "exit_code", "stdout", "stderr"]}, indent=2))
raise SystemExit(exit_code)

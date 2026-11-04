"""Compile only n54-owned sources using the prepared, read-only Mathlib cache."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENVIRONMENT = ROOT.parent / "mathlib-environment.json"
LEAN = Path(r"C:\Users\REGIS\Documents\Codex\runtimes\elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe")
parser = argparse.ArgumentParser()
parser.add_argument("--source", default="PolynomialBridge.lean")
parser.add_argument("--dependency", action="store_true")
args = parser.parse_args()
source = ROOT / args.source
if source.parent != ROOT or source.suffix != ".lean":
    raise SystemExit("Source must be a .lean file directly in the n54 worktree")
logs = ROOT / "n54-compiler-rounds"
logs.mkdir(exist_ok=True)
previous = [json.loads(p.read_text(encoding="utf-8")) for p in logs.glob("round-*.json")]
candidate_count = sum(r["kind"] == "candidate" for r in previous)
if not args.dependency and candidate_count >= 16:
    raise SystemExit("n54 candidate budget exhausted")
number = len(previous) + 1
snapshot = logs / f"round-{number:02d}-source.lean"
snapshot.write_bytes(source.read_bytes())
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
    "node": "n54", "round": number,
    "candidate_round": candidate_count + (not args.dependency),
    "kind": "dependency_build" if args.dependency else "candidate",
    "source": args.source, "snapshot": str(snapshot.relative_to(ROOT)),
    "source_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
    "command": command, "cwd": str(ROOT), "LEAN_PATH": env["LEAN_PATH"],
    "environment_source": str(ENVIRONMENT), "exit_code": exit_code,
    "stdout": stdout.decode("utf-8", errors="replace"),
    "stderr": stderr.decode("utf-8", errors="replace"),
    "root_conjecture_verified": False,
}
(logs / f"round-{number:02d}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({key: report[key] for key in
                 ["node", "round", "candidate_round", "kind", "source", "exit_code", "stdout", "stderr"]}, indent=2))
raise SystemExit(exit_code)

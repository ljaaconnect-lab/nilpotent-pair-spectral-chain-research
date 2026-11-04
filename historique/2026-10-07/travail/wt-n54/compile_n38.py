"""Record all n38 compiler invocations, including explicit local dependency builds."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEAN = Path(r"C:\Users\REGIS\Documents\Codex\runtimes\elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe")
parser = argparse.ArgumentParser()
parser.add_argument("--source", default="LabelBridge.lean")
parser.add_argument("--dependency", action="store_true")
args = parser.parse_args()
source = ROOT / args.source
if source.parent != ROOT or source.suffix != ".lean":
    raise SystemExit("Source must be a .lean file in the n38 worktree")
LOGS = ROOT / "n38-compiler-rounds"
LOGS.mkdir(exist_ok=True)
number = len(list(LOGS.glob("round-*.json"))) + 1
if number > 24:
    raise SystemExit("n38 compiler-round budget exhausted")
command = [str(LEAN)]
if args.dependency:
    command.extend(["-o", str(source.with_suffix(".olean"))])
command.append(str(source))
env = os.environ.copy()
env["LEAN_PATH"] = str(ROOT) + (os.pathsep + env["LEAN_PATH"] if env.get("LEAN_PATH") else "")
proc = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=60)
report = {"node": "n38", "round": number, "kind": "dependency_build" if args.dependency else "candidate",
          "source": args.source, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
          "command": command, "LEAN_PATH": env["LEAN_PATH"], "exit_code": proc.returncode,
          "stdout": proc.stdout.decode("utf-8", errors="replace"), "stderr": proc.stderr.decode("utf-8", errors="replace"),
          "root_conjecture_verified": False}
(LOGS / f"round-{number:02d}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
raise SystemExit(proc.returncode)

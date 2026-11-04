"""Record every actual n17 compiler round. No installation or dependency setup."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--source", default="GeneralPairing.lean", choices=["GeneralPairing.lean", "GeneralPairingRing.lean"])
args = parser.parse_args()
source = ROOT / args.source
LEAN = Path(r"C:\Users\REGIS\Documents\Codex\runtimes\elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe")
LOGS = ROOT / "n17-compiler-rounds"
LOGS.mkdir(exist_ok=True)
round_number = len(list(LOGS.glob("round-*.json"))) + 1
if round_number > 20:
    raise SystemExit("n17 complete-compiler-round budget exhausted")
command = [str(LEAN), str(source)]
result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=60)
out = result.stdout.decode("utf-8", errors="replace")
err = result.stderr.decode("utf-8", errors="replace")
report = {"node": "n17", "round": round_number, "command": command, "source": args.source,
          "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
          "exit_code": result.returncode, "stdout": out, "stderr": err,
          "sorryAx_present": "sorryAx" in out + err,
          "root_conjecture_verified": False}
(LOGS / f"round-{round_number:02d}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
raise SystemExit(result.returncode)

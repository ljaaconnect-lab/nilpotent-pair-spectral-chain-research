"""File-backed incremental Lean probes and strict final power-plan audit."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from time import time

ROOT = Path(__file__).resolve().parent
DEFAULT_LEAN = Path(r"C:\Users\REGIS\Documents\Codex\runtimes\elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe")
STANDARD = {"propext", "Quot.sound", "Classical.choice"}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--kind", choices=("probe", "candidate"), default="probe")
    parser.add_argument("--lean", type=Path, default=DEFAULT_LEAN)
    args = parser.parse_args()
    state_path = ROOT / "power-verification-history.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {"probes": 0, "candidate_rounds": 0, "runs": []}
    key = "probes" if args.kind == "probe" else "candidate_rounds"
    if args.kind == "candidate" and state[key] >= 16:
        raise SystemExit("Frozen complete-candidate budget exhausted")
    state[key] += 1
    tag = f"{args.kind}-{state[key]:02}"
    source = args.source.resolve()
    text = source.read_text(encoding="utf-8")
    archive = ROOT / "power-logs" / tag
    archive.mkdir(parents=True, exist_ok=True)
    (archive / source.name).write_text(text, encoding="utf-8")
    command = [str(args.lean), str(source)]
    started = time()
    try:
        proc = subprocess.run(command, capture_output=True, timeout=60)
        out, err = proc.stdout.decode("utf-8", errors="replace"), proc.stderr.decode("utf-8", errors="replace")
        code = proc.returncode
    except (OSError, subprocess.TimeoutExpired) as error:
        out, err, code = "", repr(error), None
    (archive / "stdout.log").write_text(out, encoding="utf-8")
    (archive / "stderr.log").write_text(err, encoding="utf-8")
    audit = {}
    for name, raw in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", out):
        audit[name] = [s.strip() for s in raw.split(",") if s.strip()]
    for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", out):
        audit[name] = []
    good = code == 0 and "sorryAx" not in out and "declaration uses 'sorry'" not in out
    clean = not re.search(r"\b(?:sorry|admit|axiom|unsafe)\b", re.sub(r"/-.*?-/|--[^\n]*", "", text, flags=re.S))
    main_names = ["SharedBinaryPower.binary_plan_correct", "SharedBinaryPower.binary_plan_logarithmic",
                  "SharedBinaryPower.central_exponent_log_bound"]
    passed = sum(name in audit and not (set(audit[name]) - STANDARD) for name in main_names) if good and clean else 0
    result = {"tag": tag, "command": command, "kind": args.kind, "exit_code": code,
              "source_sha256": hashlib.sha256(text.encode()).hexdigest(), "elapsed_seconds": time() - started,
              "error_count": len(re.findall(r"error(?:\([^)]*\))?:", out)), "axiom_audit": audit, "source_clean": clean,
              "main_obligations_passed": passed, "score": passed / 3 if args.kind == "candidate" else None,
              "root_conjecture_verified": False, "log_directory": str(archive)}
    state["runs"].append(result)
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    (archive / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(out)
    print(err)


if __name__ == "__main__":
    main()

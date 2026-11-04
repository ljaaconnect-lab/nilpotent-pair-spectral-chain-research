"""Frozen n59 Lean compiler, with local dependency builds and exact logs."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEAN = Path(r"C:\Users\REGIS\Documents\Codex\runtimes\elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe")
STANDARD = {"propext", "Quot.sound", "Classical.choice"}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--kind", choices=("probe", "candidate", "dependency"), default="probe")
    args = parser.parse_args()
    protocol = json.loads((ROOT / "n59-protocol.json").read_text(encoding="utf-8"))
    histfile = ROOT / "n59-verification-history.json"
    hist = json.loads(histfile.read_text(encoding="utf-8")) if histfile.exists() else {"probes": 0, "candidates": 0, "dependencies": 0, "runs": []}
    key = {"probe": "probes", "candidate": "candidates", "dependency": "dependencies"}[args.kind]
    if args.kind == "candidate" and hist[key] >= protocol["complete_candidate_budget"]:
        raise SystemExit("Frozen complete-candidate budget exhausted")
    hist[key] += 1
    tag = f"{args.kind}-{hist[key]:02}"
    source = args.source.resolve()
    source_text = source.read_text(encoding="utf-8")
    logs = ROOT / "n59-logs" / tag
    logs.mkdir(parents=True, exist_ok=True)
    (logs / source.name).write_text(source_text, encoding="utf-8")
    supplied = json.loads((ROOT.parent / "mathlib-environment.json").read_text(encoding="utf-8"))
    env = os.environ.copy()
    env.update(supplied)
    build = ROOT / "proof-build"
    build.mkdir(exist_ok=True)
    env["LEAN_PATH"] = os.pathsep.join((str(build), str(ROOT), supplied["LEAN_PATH"]))
    command = [str(LEAN), str(source)]
    if args.kind == "dependency":
        command += ["-o", str(build / (source.stem + ".olean"))]
    started = time.perf_counter()
    try:
        run = subprocess.run(command, capture_output=True, timeout=60, env=env, cwd=ROOT)
        out, err, code = run.stdout.decode("utf-8", errors="replace"), run.stderr.decode("utf-8", errors="replace"), run.returncode
    except (OSError, subprocess.TimeoutExpired) as error:
        out, err, code = "", repr(error), None
    (logs / "stdout.log").write_text(out, encoding="utf-8")
    (logs / "stderr.log").write_text(err, encoding="utf-8")
    audit = {name: [a.strip() for a in ax.split(",") if a.strip()] for name, ax in
             re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", out)}
    audit.update({name: [] for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", out)})
    clean = not re.search(r"\b(?:sorry|admit|axiom|unsafe)\b", re.sub(r"/-.*?-/|--[^\n]*", "", source_text, flags=re.S))
    good = code == 0 and clean and "sorryAx" not in out and all(not (set(a)-STANDARD) for a in audit.values())
    names = [item["name"] for item in protocol["principal_obligations"]]
    passed = sum(name in audit for name in names) if good else 0
    result = {"tag": tag, "kind": args.kind, "command": command,
              "environment_keys": sorted(supplied), "exit_code": code,
              "elapsed_seconds": time.perf_counter()-started,
              "source_sha256": hashlib.sha256(source_text.encode()).hexdigest(),
              "error_count": len(re.findall(r"error(?:\([^)]*\))?:", out)),
              "source_clean": clean, "axiom_audit": audit, "passed": passed,
              "denominator": len(names), "dev_score": passed/len(names) if args.kind == "candidate" else None,
              "root_conjecture_verified": False}
    hist["runs"].append(result)
    histfile.write_text(json.dumps(hist, indent=2), encoding="utf-8")
    (logs / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(out)
    print(err)


if __name__ == "__main__":
    main()

"""Pinned Mathlib compiler harness, preserving every candidate/probe log."""
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
ENVIRONMENT = ROOT.parent / "mathlib-environment.json"
STANDARD = {"propext", "Quot.sound", "Classical.choice"}
OBLIGATIONS = ["DenseScalar.matrix_power_correct", "DenseScalar.scalar_compiler_correct",
               "DenseScalar.dense_product_gate_count", "DenseScalar.conditional_scalar_budget"]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--kind", choices=("probe", "candidate", "dependency"), default="probe")
    args = parser.parse_args()
    hist_path = ROOT / "n57-verification-history.json"
    hist = json.loads(hist_path.read_text(encoding="utf-8")) if hist_path.exists() else {"probes": 0, "candidates": 0, "dependencies": 0, "runs": []}
    key = {"probe": "probes", "candidate": "candidates", "dependency": "dependencies"}[args.kind]
    if args.kind == "candidate" and hist[key] >= 20:
        raise SystemExit("Fixed complete candidate budget exhausted")
    hist[key] += 1
    tag = f"{args.kind}-{hist[key]:02}"
    source = args.source.resolve()
    code_text = source.read_text(encoding="utf-8")
    logs = ROOT / "n57-logs" / tag
    logs.mkdir(parents=True, exist_ok=True)
    (logs / source.name).write_text(code_text, encoding="utf-8")
    env_data = json.loads(ENVIRONMENT.read_text(encoding="utf-8"))
    env = os.environ.copy()
    env.update(env_data)  # Preserve all three supplied Mathlib environment entries.
    build = ROOT / "proof-build"
    build.mkdir(exist_ok=True)
    env["LEAN_PATH"] = os.pathsep.join((str(build), str(ROOT), env_data["LEAN_PATH"]))
    command = [str(LEAN), str(source)]
    if args.kind == "dependency":
        command += ["-o", str(build / (source.stem + ".olean"))]
    started = time.perf_counter()
    try:
        run = subprocess.run(command, capture_output=True, timeout=60, env=env, cwd=ROOT)
        out, err, exit_code = run.stdout.decode("utf-8", errors="replace"), run.stderr.decode("utf-8", errors="replace"), run.returncode
    except (OSError, subprocess.TimeoutExpired) as error:
        out, err, exit_code = "", repr(error), None
    (logs / "stdout.log").write_text(out, encoding="utf-8")
    (logs / "stderr.log").write_text(err, encoding="utf-8")
    audit = {name: [a.strip() for a in ax.split(",") if a.strip()]
             for name, ax in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", out)}
    audit.update({name: [] for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", out)})
    clean = not re.search(r"\b(?:sorry|admit|axiom|unsafe)\b", re.sub(r"/-.*?-/|--[^\n]*", "", code_text, flags=re.S))
    verified = exit_code == 0 and clean and "sorryAx" not in out and all(not (set(ax)-STANDARD) for ax in audit.values())
    passed = sum(name in audit for name in OBLIGATIONS) if verified else 0
    result = {"tag": tag, "kind": args.kind, "command": command,
              "environment_keys": sorted(env_data), "environment_file": str(ENVIRONMENT),
              "source_sha256": hashlib.sha256(code_text.encode()).hexdigest(),
              "exit_code": exit_code, "elapsed_seconds": time.perf_counter()-started,
              "error_count": len(re.findall(r"error(?:\([^)]*\))?:", out)),
              "source_clean": clean, "axiom_audit": audit,
              "passed": passed, "denominator": 4,
              "dev_score": passed/4 if args.kind == "candidate" else None,
              "root_representation_established": False}
    hist["runs"].append(result)
    hist_path.write_text(json.dumps(hist, indent=2), encoding="utf-8")
    (logs / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(out)
    print(err)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Portable, scoped checks of the current representative-chain artifacts.

Only the Python standard library is required for smoke/unit. Historical
validation reports are never rewritten. Lean checks require a separately
prepared Lake environment in repro/lean, pinned to Mathlib v4.34.1.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
LEAN_DIR = ROOT / "repro/lean"
CORE_FILES = (
    "documents/composition-native-2026-11-03/NativeCompositionBounds.lean",
    "documents/induction-native-2026-11-03/SharedCostInduction.lean",
    "documents/cout-meme-circuit-2026-11-03/SameDAGCost.lean",
    "documents/induction-native-2026-11-03/SpectralReadoutCompatibility.lean",
    "documents/raccord-intt-2026-11-04/INTTProjection.lean",
    "documents/unite-temoin-2026-11-04/UnitLift.lean",
    "documents/unite-temoin-2026-11-04/SquarefreeReadout.lean",
)
PYTHON_FILES = (
    "documents/composition-native-2026-11-03/compose_native_representatives.py",
    "documents/unite-temoin-2026-11-04/compile_with_unit.py",
    "etudes/2026-11-01/linearisation-orientee-convolution/linearised_inputs.py",
    "etudes/2026-11-01/raccord-initialisation/spectral/reprise-globale/shared_operator_dag.py",
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def hashes(paths):
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in paths}


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    require(spec is not None and spec.loader is not None, f"Cannot load {relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def exact_root(Q, N):
    return next(w for w in range(1, Q)
                if pow(w, N, Q) == 1 and pow(w, N // 2, Q) != 1)


def input_values(n, N, Q, rng, zero_auxiliary=False):
    values = {f"a_{i}_{j}": rng.randrange(Q)
              for i in range(n) for j in range(n)}
    values["z"] = rng.randrange(Q)
    values.update({f"x_{r}": 0 if zero_auxiliary else rng.randrange(Q)
                   for r in range(N)})
    return values


def smoke():
    before = hashes(PYTHON_FILES)
    module = load_module("compose_native_representatives", PYTHON_FILES[0])
    rng = random.Random(20261104)
    cases = []
    for n, Q, expected in ((1, 3, 12), (2, 5, 73), (4, 17, 330)):
        N = 1 << n.bit_length()
        built = module.compile_native_representatives(
            n, Q, N, exact_root(Q, N), list(range(n)))
        dag, info = built["dag"], built["metadata"]
        require(info["true_INTT_representative_gates"] == expected,
                f"Changed representative gate count for n={n}")
        require(info["true_INTT_representative_gates"] <= 29 * n ** 3,
                f"Representative budget exceeded for n={n}")
        require(info["true_INTT_calls"] == 1, "Expected one native INTT")
        require(not info["complete_scalar_a_z_only"], "Unexpected scope flag")
        for _ in range(4):
            values = input_values(n, N, Q, rng)
            require(dag.evaluate(built["outputs"], values)
                    == dag.evaluate(built["routed"], values),
                    f"INTT/routing mismatch for n={n}")
        cases.append({"n": n, "Q": Q, "N": N,
                      "gates": info["true_INTT_representative_gates"],
                      "explicit_budget": info["true_INTT_bound"],
                      "numeric_trials": 4})
    require(hashes(PYTHON_FILES) == before, "A Python source changed during smoke")
    return {"cases": cases, "source_sha256": before,
            "scope": "Finite checks of representative counts and ordinary-polynomial INTT/routing; auxiliary x inputs are retained.",
            "complete_scalar_a_z_only_chain_proved": False}


def unit():
    before = hashes(PYTHON_FILES)
    load_module("compose_native_representatives", PYTHON_FILES[0])
    module = load_module("portable_compile_with_unit", PYTHON_FILES[1])
    rng = random.Random(20261104)
    cases = []
    for n, Q in ((1, 3), (2, 5), (3, 5), (4, 17), (8, 17), (16, 97)):
        N = 1 << n.bit_length()
        built = module.compile_with_unit(n, Q, N, exact_root(Q, N), list(range(n)))
        dag, original, info = built["dag"], built["original"], built["metadata"]
        target = info["target"]
        for trial in range(3):
            values = input_values(n, N, Q, rng, zero_auxiliary=trial < 2)
            if trial == 0:
                values.update({f"a_{i}_{j}": 0 for i in range(n) for j in range(n)})
                values["z"] = 1
            old = dag.evaluate(original["outputs"], values)
            new = dag.evaluate(built["outputs"], values)
            require(new == [(value + int(k == target)) % Q
                            for k, value in enumerate(old)],
                    f"Unit transport mismatch for n={n}, trial={trial}")
            if trial < 2:
                require(old == [0] * N, "Original homogeneous output must vanish at x=0")
                require(new == [int(k == target) for k in range(N)],
                        "Unit output at x=0 must be the routed unit")
        require(info["shared_prefix_preserved"], "Lost shared prefix")
        require(info["lifted_useful_gates"] <= 29 * n ** 3 + 1,
                "Unit representative budget exceeded")
        cases.append({"n": n, "Q": Q, "N": N,
                      "original_gates": info["original_useful_gates"],
                      "unit_gates": info["lifted_useful_gates"],
                      "numeric_trials": 3})
    require(hashes(PYTHON_FILES) == before, "A Python source changed during unit checks")
    return {"cases": cases, "source_sha256": before,
            "scope": "Finite checks of shared unit insertion and its scalar representative budget. Coefficient preservation is the separately stated mathematical/Lean result.",
            "zero_auxiliary_evaluation_is_coefficient_readout": False,
            "complete_scalar_a_z_only_chain_proved": False}


def lean(timeout):
    lake = shutil.which("lake")
    require(lake is not None, "Lake is missing from PATH. See REPRODUCIBILITY.md for setup.")
    require((LEAN_DIR / "lake-manifest.json").is_file(),
            "Prepare repro/lean first: lake update, then lake exe cache get.")
    before = hashes(CORE_FILES)
    version = subprocess.run([lake, "env", "lean", "--version"], cwd=LEAN_DIR,
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=timeout)
    require(version.returncode == 0, version.stdout + version.stderr)
    require("version 4.34.1" in version.stdout, "Expected Lean version 4.34.1")
    checks = []
    for relative in CORE_FILES:
        source = ROOT / relative
        text = source.read_text(encoding="utf-8")
        imports = re.findall(r"^import\s+([^\n]+)", text, re.MULTILINE)
        require(all(name.startswith("Mathlib.") for line in imports for name in line.split()),
                f"Unexpected non-Mathlib dependency in {relative}")
        require(not re.search(r"\b(?:sorry|admit)\b|^\s*axiom\s", text, re.MULTILINE),
                f"Placeholder or added axiom detected in {relative}")
        command = [lake, "env", "lean", "-j1", str(source)]
        start = time.monotonic()
        run = subprocess.run(command, cwd=LEAN_DIR, capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=timeout)
        output = run.stdout + run.stderr
        passed = (run.returncode == 0 and "warning:" not in output
                  and "sorryAx" not in output)
        checks.append({"source": relative, "imports": imports,
                       "source_sha256": before[relative], "command": command,
                       "exit_code": run.returncode, "passed": passed,
                       "seconds": round(time.monotonic() - start, 3),
                       "stdout": run.stdout, "stderr": run.stderr})
    require(hashes(CORE_FILES) == before, "A Lean source changed during checking")
    return {"lean_version": version.stdout.strip(), "mathlib_tag": "v4.34.1",
            "checks": checks, "all_passed": all(item["passed"] for item in checks),
            "scope": "Seven selected Mathlib-only kernels, with their original explicit hypotheses. This is not a verification of every archived attempt, the Python compiler, or the general scalar closure.",
            "complete_scalar_a_z_only_chain_proved": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("smoke", "unit", "lean"),
                        nargs="?", default="smoke")
    parser.add_argument("--report", type=Path,
                        help="JSON report path; default: reproducibility-results/<command>.json")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Timeout in seconds for each Lean process (default: 600)")
    args = parser.parse_args()
    report_path = args.report or ROOT / "reproducibility-results" / f"{args.command}.json"
    require(args.timeout > 0, "--timeout must be positive")
    start = time.monotonic()
    report = {"command": args.command,
              "checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "python_version": sys.version.split()[0]}
    try:
        details = lean(args.timeout) if args.command == "lean" else {"smoke": smoke, "unit": unit}[args.command]()
        report.update(details)
        passed = details.get("all_passed", True)
        report["status"] = "passed" if passed else "failed"
    except Exception as error:
        report.update(status="failed", error=f"{type(error).__name__}: {error}",
                      traceback=traceback.format_exc())
    report["elapsed_seconds"] = round(time.monotonic() - start, 3)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"status": report["status"], "command": args.command,
                      "report": str(report_path),
                      "elapsed_seconds": report["elapsed_seconds"],
                      **({"error": report["error"]} if "error" in report else {})},
                     ensure_ascii=False))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

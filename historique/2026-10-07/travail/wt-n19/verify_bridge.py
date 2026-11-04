"""Strict verification gate. Exit 0 only after Lean and axiom checks pass.

An absent executable is an infrastructure failure, not a rejected theorem.
Even success verifies only the small generated bridge, never Conjecture 1.5.
No downloads, installation, services, or held-out tests are performed.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STANDARD_AXIOMS = {"propext", "Quot.sound", "Classical.choice"}


def invoke(command, cwd=None):
    try:
        proc = subprocess.run(command, cwd=cwd, capture_output=True, timeout=60)
        def decode(raw):
            if raw.count(b"\x00") > len(raw) // 5:
                return raw.decode("utf-16-le", errors="replace").lstrip("\ufeff")
            return raw.decode("utf-8", errors="replace")
        return {"command": command, "exit_code": proc.returncode,
                "stdout": decode(proc.stdout), "stderr": decode(proc.stderr)}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"command": command, "exit_code": None,
                "invocation_error": f"{type(error).__name__}: {error}"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", help="Existing Mathlib project root, no setup is performed")
    parser.add_argument("--lean", help="Existing Lean executable")
    parser.add_argument("--lake", help="Existing Lake executable")
    parser.add_argument("--source", default="CoreBridge.lean", choices=["CoreBridge.lean", "GeneratedBridge.lean", "GeneratedCoreN2.lean"])
    parser.add_argument("--output", default="verification-report.json")
    args = parser.parse_args()
    if args.lean and args.lake:
        parser.error("choose one compiler backend")
    source_path = ROOT / args.source
    source = source_path.read_text(encoding="utf-8")
    generation = json.loads((ROOT / "generation-report.json").read_text())
    source_manifest = generation["sources"][args.source]
    report = {"status": "unverified", "dev_score": None,
              "root_conjecture_verified": False, "lean_verified": False,
              "verified_scope": source_manifest["scope"], "source": args.source,
              "report_output": args.output,
              "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
              "attempts": [], "error_stack": []}
    # Generated comments do not contribute proof terms. Strip comments before
    # detecting unresolved proof tokens or custom trust-base declarations.
    code_source = re.sub(r"/-.*?-/|--[^\n]*", "", source, flags=re.DOTALL)
    banned = re.findall(r"\b(?:sorry|admit|axiom|unsafe)\b", code_source)
    if banned:
        report["status"] = "rejected_placeholders_or_untrusted_declarations"
        report["error_stack"].append({"banned_tokens": banned})
        finish(report, 3)
    if report["source_sha256"] != source_manifest["sha256"]:
        report["status"] = "rejected_source_changed_since_generation"
        finish(report, 3)
    lake = args.lake or shutil.which("lake")
    lean = args.lean or shutil.which("lean")
    if not lake and not lean:
        # Keep actual invocation diagnostics. No fictional Lean exit code.
        report["attempts"].extend([invoke(["lean", str(source_path)]),
                                   invoke(["lake", "env", "lean", str(source_path)])])
        wsl = shutil.which("wsl")
        if wsl:
            report["attempts"].append(invoke([wsl, "--list", "--quiet"]))
        report["status"] = "infrastructure_failure_no_lean_verifier"
        report["error_stack"].append("No usable Lean/Lake executable; tactic goals were not elaborated.")
        finish(report, 2)
    command = [lake, "env", "lean", str(source_path)] if lake else [lean, str(source_path)]
    report["compiler_version"] = invoke([lake or lean, "--version"], cwd=args.project or ROOT)
    result = invoke(command, cwd=args.project or ROOT)
    report["attempts"].append(result)
    if result["exit_code"] is None:
        report["status"] = "infrastructure_failure_compiler_not_invoked"
        finish(report, 2)
    output = result.get("stdout", "") + result.get("stderr", "")
    if result["exit_code"] != 0:
        missing_dependency = "unknown module prefix" in output
        report["status"] = "infrastructure_failure_missing_dependency" if missing_dependency else "compiler_rejected_candidate"
        report["error_stack"].append(output)
        report["dev_score"] = None if missing_dependency else 0.0
        finish(report, 2 if missing_dependency else 1)
    if re.search(r"\bsorryAx\b|declaration uses ['\"]?sorry|\berror:", output):
        report["status"] = "rejected_compiler_output"
        report["error_stack"].append(output)
        finish(report, 3)
    found = {}
    for name, raw in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", output):
        found[name] = {item.strip() for item in raw.split(",") if item.strip()}
    for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", output):
        found[name] = set()
    report["axiom_audit"] = {name: sorted(found.get(name, set())) for name in source_manifest["theorems"]}
    for name in source_manifest["theorems"]:
        if name not in found:
            report["error_stack"].append(f"Missing explicit #print axioms evidence for {name}")
        elif found[name] - STANDARD_AXIOMS:
            report["error_stack"].append(f"Unexpected axioms for {name}: {sorted(found[name] - STANDARD_AXIOMS)}")
    if report["error_stack"]:
        report["status"] = "rejected_axiom_audit"
        finish(report, 3)
    report.update(status="helper_bridge_verified", lean_verified=True, dev_score=1.0)
    report["accepted_trust_base"] = sorted(STANDARD_AXIOMS)
    finish(report, 0)


def finish(report, code):
    (ROOT / report.get("report_output", "verification-report.json")).write_text(json.dumps(report, indent=2), encoding="utf-8")
    # The full command diagnostics remain file-backed for review.
    print(json.dumps({key: report[key] for key in ["status", "dev_score", "lean_verified", "root_conjecture_verified", "error_stack"]}, indent=2))
    sys.exit(code)


if __name__ == "__main__":
    main()

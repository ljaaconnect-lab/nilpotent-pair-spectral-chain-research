"""Audit a recorded exit-zero compilation of the current exact n54 source.

This does not run held-out tests or count an additional compiler invocation.
Reproducers first run compile_n54.py, which records their own compiler evidence.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
SOURCE = ROOT / "PolynomialBridge.lean"
logs = sorted((ROOT / "n54-compiler-rounds").glob("round-*.json"))
rounds = [json.loads(p.read_text(encoding="utf-8")) for p in logs]
current_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
source = SOURCE.read_text(encoding="utf-8")
expected = ["GeneralCollisionPolynomialBridge." + name for name in
            re.findall(r"^theorem\s+(\w+)", source, flags=re.MULTILINE)]
code = re.sub(r"/-.*?-/|--[^\n]*", "", source, flags=re.DOTALL)
errors = []
if re.search(r"\b(?:sorry|admit|axiom|unsafe)\b", code):
    errors.append("Unresolved placeholder or untrusted declaration in current source")
matching = [r for r in rounds if r["source"] == SOURCE.name and
            r["source_sha256"] == current_hash]
final = matching[-1] if matching else None
if final is None or final["exit_code"] != 0:
    errors.append("No exit-zero compiler evidence for the exact current source")
found = {}
if final:
    output = final["stdout"] + final["stderr"]
    if re.search(r"\bsorryAx\b|declaration uses ['\"]?sorry|\berror:", output):
        errors.append("Rejected compiler diagnostics")
    for name, raw in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", output):
        found[name] = {part.strip() for part in raw.split(",") if part.strip()}
    for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", output):
        found[name] = set()
    for name in expected:
        if name not in found:
            errors.append(f"Missing explicit axiom audit for {name}")
        elif found[name] - STANDARD_AXIOMS:
            errors.append(f"Unexpected axioms for {name}: {sorted(found[name] - STANDARD_AXIOMS)}")
    snapshot = ROOT / final["snapshot"]
    if not snapshot.exists() or hashlib.sha256(snapshot.read_bytes()).hexdigest() != current_hash:
        errors.append("Missing or changed compiler source snapshot")
dependency_audits = {}
for dependency in ["GeneralPairingRing.lean", "CoreBridge.lean", "LabelBridge.lean"]:
    path = ROOT / dependency
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    expected_dependency = re.findall(r"^#print axioms ([\w.]+)",
                                     path.read_text(encoding="utf-8"), flags=re.MULTILINE)
    matches = [r for r in rounds if r["kind"] == "dependency_build" and
               r["source"] == dependency and r["source_sha256"] == digest]
    evidence = matches[-1] if matches else None
    audited = {}
    if evidence is None or evidence["exit_code"] != 0:
        errors.append(f"Missing exact exit-zero local dependency build for {dependency}")
    else:
        output = evidence["stdout"] + evidence["stderr"]
        if re.search(r"\bsorryAx\b|declaration uses ['\"]?sorry|\berror:", output):
            errors.append(f"Rejected dependency diagnostics for {dependency}")
        for name, raw in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", output):
            audited[name] = {part.strip() for part in raw.split(",") if part.strip()}
        for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", output):
            audited[name] = set()
        for name in expected_dependency:
            if name not in audited or audited[name] - STANDARD_AXIOMS:
                errors.append(f"Missing or unexpected dependency axiom audit for {name}")
        snapshot = ROOT / evidence["snapshot"]
        if not snapshot.exists() or hashlib.sha256(snapshot.read_bytes()).hexdigest() != digest:
            errors.append(f"Missing or changed dependency snapshot for {dependency}")
    dependency_audits[dependency] = {
        "source_sha256": digest, "round": evidence["round"] if evidence else None,
        "compiler_exit_code": evidence["exit_code"] if evidence else None,
        "axioms": {name: sorted(audited.get(name, set())) for name in expected_dependency},
    }
report = {
    "node_id": "n54", "artifact_version": "n54-polynomial-interpretation-v1",
    "status": "rejected" if errors else "polynomial_interpretation_verified",
    "dev_score": 0.0 if errors else 1.0,
    "source": SOURCE.name, "source_sha256": current_hash,
    "compiler_invocations": len(rounds),
    "candidate_rounds": sum(r["kind"] == "candidate" for r in rounds),
    "dependency_builds": sum(r["kind"] == "dependency_build" for r in rounds),
    "expected_declarations": len(expected),
    "accepted_declarations": 0 if errors else len(expected),
    "declarations": expected,
    "axiom_audit": {name: sorted(found.get(name, set())) for name in expected},
    "dependency_audits": dependency_audits,
    "accepted_trust_base": sorted(STANDARD_AXIOMS),
    "final_compiler_round": final["round"] if final else None,
    "compiler_exit_code": final["exit_code"] if final else None,
    "command": final["command"] if final else None,
    "LEAN_PATH": final["LEAN_PATH"] if final else None,
    "errors": errors, "root_conjecture_verified": False, "heldout_tests_run": False,
    "scope": "Actual Polynomial interpretation of sparse terms, multiplication and central pairing; no scalar extraction complexity theorem",
}
(ROOT / "n54-strict-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({key: report[key] for key in
                 ["status", "dev_score", "candidate_rounds", "dependency_builds", "accepted_declarations", "errors"]}, indent=2))
raise SystemExit(bool(errors))

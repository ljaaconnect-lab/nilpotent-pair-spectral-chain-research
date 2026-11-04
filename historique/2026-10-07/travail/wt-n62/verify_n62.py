"""Audit a recorded exit-zero compilation of the current exact n62 source.

This does not run held-out tests or count an additional compiler invocation.
Reproducers first run compile_n62.py, which records their own compiler evidence.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
SOURCE = ROOT / "DirectProjector.lean"
logs = sorted((ROOT / "n62-compiler-rounds").glob("round-*.json"))
rounds = [json.loads(p.read_text(encoding="utf-8")) for p in logs]
current_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
source = SOURCE.read_text(encoding="utf-8")
expected = ["CollisionDirectProjector." + name for name in
            re.findall(r"^theorem\s+(\w+)", source, flags=re.MULTILINE)]
code = re.sub(r"/-.*?-/|--[^\n]*", "", source, flags=re.DOTALL)
errors = []
contract = ROOT / "n62-frozen-obligations.json"
required = ["CollisionDirectProjector." + name for name in
            json.loads((ROOT / "n62-formal-obligations.json").read_text(encoding="utf-8"))["obligations"]]
if set(expected) != set(required) or len(required) != 7:
    errors.append("The accepted source must contain exactly the seven frozen development obligations")
if re.search(r"\b(?:sorry|admit|axiom|unsafe|native_decide)\b", code):
    errors.append("Unresolved placeholder or untrusted declaration in current source")
matching = [r for r in rounds if r["source"] == SOURCE.name and
            r["source_sha256"] == current_hash]
final = matching[-1] if matching else None
if final is None or final["exit_code"] != 0:
    errors.append("No exit-zero compiler evidence for the exact current source")
found = {}
if final:
    if final.get("frozen_contract_sha256") != hashlib.sha256(contract.read_bytes()).hexdigest():
        errors.append("The current frozen contract differs from the compiled contract")
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
for dependency in ["GeneralPairingRing.lean", "CoreBridge.lean", "LabelBridge.lean", "DeterminantBridge.lean"]:
    path = ROOT / dependency
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    dependency_code = re.sub(r"/-.*?-/|--[^\n]*", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)
    if re.search(r"\b(?:sorry|admit|axiom|unsafe|native_decide)\b", dependency_code):
        errors.append(f"Rejected placeholder or declaration in dependency {dependency}")
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
formal_contract = ROOT / "n62-formal-obligations.json"
formal_digest = hashlib.sha256(formal_contract.read_bytes()).hexdigest()
if final and final.get("formal_contract_sha256") != formal_digest:
    errors.append("The formal contract differs from the compiled contract")
incident_path = ROOT / "n62-journal-incident.json"
incident = json.loads(incident_path.read_text(encoding="utf-8"))
for key in ["original_metadata_preserved", "snapshot_preserved"]:
    if not (ROOT / incident[key]).is_file():
        errors.append("Missing original journal-collision evidence")
if [r["round"] for r in rounds] != list(range(1, len(rounds) + 1)):
    errors.append("Noncontiguous or repeated invocation identifiers")
if sum(r["kind"] == "candidate" for r in rounds) > 12:
    errors.append("Candidate budget exceeded")
mathlib_provenance_path = ROOT / "n62-mathlib-signature-provenance.json"
mathlib_provenance = json.loads(mathlib_provenance_path.read_text(encoding="utf-8"))
for key, hash_key in [("source_path", "source_sha256"),
                      ("compiled_module_path", "compiled_module_sha256")]:
    path = Path(mathlib_provenance[key])
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != mathlib_provenance[hash_key]:
        errors.append(f"The Mathlib signature dependency differs from its provenance: {key}")
sympy_path = ROOT / "n62-local-sympy-report.json"
sympy_support = json.loads(sympy_path.read_text(encoding="utf-8"))
statements = {
    name: statement.strip()
    for name, statement in re.findall(r"^theorem\s+(\w+)(.*?)\s*:=\s*by", source,
                                      flags=re.MULTILINE | re.DOTALL)
}
report = {
    "node_id": "n62", "artifact_version": "n62-direct-projector-v1",
    "status": "rejected" if errors else "direct_projector_verified",
    "dev_score": 0.0 if errors else 1.0,
    "source": SOURCE.name, "source_sha256": current_hash,
    "compiler_invocations": len(rounds),
    "candidate_rounds": sum(r["kind"] == "candidate" for r in rounds),
    "dependency_builds": sum(r["kind"] == "dependency_build" for r in rounds),
    "frozen_replays": sum(r["kind"] == "frozen_replay" for r in rounds),
    "probe_compilations": sum(r["kind"] == "probe" for r in rounds),
    "candidate_compilation_budget": 12,
    "expected_declarations": len(expected),
    "accepted_declarations": 0 if errors else len(expected),
    "declarations": expected,
    "exact_declaration_statements": statements,
    "axiom_audit": {name: sorted(found.get(name, set())) for name in expected},
    "dependency_audits": dependency_audits,
    "journal_incident": incident,
    "journal_incident_sha256": hashlib.sha256(incident_path.read_bytes()).hexdigest(),
    "mathlib_signature_provenance": mathlib_provenance,
    "mathlib_signature_provenance_sha256": hashlib.sha256(mathlib_provenance_path.read_bytes()).hexdigest(),
    "local_sympy_support_sha256": hashlib.sha256(sympy_path.read_bytes()).hexdigest(),
    "local_sympy_checks": sympy_support["checks"],
    "sympy_counts_as_kernel_proof": False,
    "accepted_trust_base": sorted(STANDARD_AXIOMS),
    "final_compiler_round": final["round"] if final else None,
    "compiler_exit_code": final["exit_code"] if final else None,
    "command": final["command"] if final else None,
    "LEAN_PATH": final["LEAN_PATH"] if final else None,
    "LEAN_SRC_PATH": final.get("LEAN_SRC_PATH") if final else None,
    "LEAN_SYSROOT": final.get("LEAN_SYSROOT") if final else None,
    "frozen_contract_sha256": hashlib.sha256(contract.read_bytes()).hexdigest(),
    "formal_contract_sha256": formal_digest,
    "fixed_development_obligations": required,
    "invocation_history": [{**{key: r[key] for key in
                              ["round", "kind", "source", "source_sha256", "exit_code"]},
                            "journal_recovery": r.get("journal_recovery")}
                            for r in rounds],
    "errors": errors, "root_conjecture_verified": False, "heldout_tests_run": False,
    "scope": "Seven local projector and genuine permutation inversion-phase identities over arbitrary CommRing; no scalar compilation complexity theorem",
}
(ROOT / "n62-strict-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({key: report[key] for key in
                 ["status", "dev_score", "candidate_rounds", "dependency_builds", "accepted_declarations", "errors"]}, indent=2))
raise SystemExit(bool(errors))

"""Audit exact-source kernel evidence and score the four frozen n63 helper goals."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "MobiusBridge.lean"
TRUST = {"propext", "Classical.choice", "Quot.sound"}
protocol = ROOT / "n63-protocol.json"
formal = ROOT / "n63-formal-obligations.json"
required = ["CollisionMobiusBridge." + name for name in
            json.loads(formal.read_text(encoding="utf-8"))["obligations"]]
source_bytes = SOURCE.read_bytes()
digest = hashlib.sha256(source_bytes).hexdigest()
source = source_bytes.decode("utf-8")
declarations = ["CollisionMobiusBridge." + name for name in
                re.findall(r"^theorem\s+(\w+)", source, flags=re.MULTILINE)]
code = re.sub(r"/-.*?-/|--[^\n]*", "", source, flags=re.DOTALL)
rounds = [json.loads(path.read_text(encoding="utf-8")) for path in
          sorted((ROOT / "n63-compiler-rounds").glob("round-*.json"))]
matches = [r for r in rounds if r["source"] == SOURCE.name and r["source_sha256"] == digest]
final = matches[-1] if matches else None
errors = []
if re.search(r"\b(?:sorry|admit|axiom|unsafe|native_decide)\b", code):
    errors.append("Rejected placeholder or untrusted declaration")
if final is None or final["exit_code"] != 0:
    errors.append("No exit-zero compiler evidence for the exact current source")
if [r["round"] for r in rounds] != list(range(1, len(rounds) + 1)):
    errors.append("Noncontiguous or repeated invocation identifiers")
candidate_count = sum(r["kind"] == "candidate" for r in rounds)
if candidate_count > 12:
    errors.append("Candidate budget exceeded")
provenance_path = ROOT / "n63-mathlib-provenance.json"
provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
for module, data in provenance["modules"].items():
    for key, hash_key in [("source_path", "source_sha256"), ("compiled_path", "compiled_sha256")]:
        path = Path(data[key])
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != data[hash_key]:
            errors.append(f"Changed Mathlib dependency: {module}, {key}")
audited = {}
if final:
    if final["frozen_contract_sha256"] != hashlib.sha256(protocol.read_bytes()).hexdigest():
        errors.append("The clarified root protocol differs from the compiled contract")
    if final["formal_contract_sha256"] != hashlib.sha256(formal.read_bytes()).hexdigest():
        errors.append("The formal statements differ from the compiled contract")
    bonus_contract = ROOT / "n63-bonus-contract.json"
    if bonus_contract.exists() and final.get("bonus_contract_sha256") != hashlib.sha256(bonus_contract.read_bytes()).hexdigest():
        errors.append("The bonus contract differs from the compiled contract")
    output = final["stdout"] + final["stderr"]
    if re.search(r"\bsorryAx\b|declaration uses ['\"]?sorry|\berror:", output):
        errors.append("Rejected compiler diagnostics")
    for name, raw in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", output):
        audited[name] = {x.strip() for x in raw.split(",") if x.strip()}
    for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", output):
        audited[name] = set()
    for name in declarations:
        if name not in audited or audited[name] - TRUST:
            errors.append(f"Missing or unexpected axiom audit for {name}")
    snapshot = ROOT / final["snapshot"]
    if not snapshot.is_file() or hashlib.sha256(snapshot.read_bytes()).hexdigest() != digest:
        errors.append("Missing or changed exact compiler source snapshot")
accepted = [] if errors else declarations
closed = [name for name in required if name in accepted]
unclosed = [name for name in required if name not in closed]
status = "rejected" if errors else "mobius_helpers_partial" if unclosed else "mobius_helpers_verified"
report = {
    "node_id": "n63", "artifact_version": "n63-mobius-helpers-v1", "status": status,
    "source": SOURCE.name, "source_sha256": digest,
    "dev_score": len(closed) / 4,
    "score_definition": "Verified frozen helper obligations / four; independent of root conjecture score",
    "root_conjecture_score": 0, "root_conjecture_verified": False,
    "fixed_development_obligations": required, "closed_obligations": closed,
    "unclosed_obligations": unclosed, "accepted_declarations": len(accepted),
    "declarations": accepted,
    "exact_declaration_statements": {
        name: statement.strip() for name, statement in
        re.findall(r"^theorem\s+(\w+)(.*?)\s*:=\s*by", source, flags=re.MULTILINE | re.DOTALL)
    },
    "axiom_audit": {name: sorted(audited.get(name, set())) for name in declarations},
    "accepted_trust_base": sorted(TRUST), "compiler_invocations": len(rounds),
    "candidate_rounds": candidate_count, "candidate_compilation_budget": 12,
    "dependency_builds": sum(r["kind"] == "dependency_build" for r in rounds),
    "probe_compilations": sum(r["kind"] == "probe" for r in rounds),
    "frozen_replays": sum(r["kind"] == "frozen_replay" for r in rounds),
    "final_compiler_round": final["round"] if final else None,
    "compiler_exit_code": final["exit_code"] if final else None,
    "command": final["command"] if final else None,
    "LEAN_PATH": final["LEAN_PATH"] if final else None,
    "LEAN_SRC_PATH": final["LEAN_SRC_PATH"] if final else None,
    "LEAN_SYSROOT": final["LEAN_SYSROOT"] if final else None,
    "frozen_contract_sha256": hashlib.sha256(protocol.read_bytes()).hexdigest(),
    "formal_contract_sha256": hashlib.sha256(formal.read_bytes()).hexdigest(),
    "bonus_contract_sha256": hashlib.sha256((ROOT / "n63-bonus-contract.json").read_bytes()).hexdigest()
        if (ROOT / "n63-bonus-contract.json").exists() else None,
    "bonus_declarations": [name for name in accepted
                           if name == "CollisionMobiusBridge.sign_coefficient_natAbs_bound"],
    "original_protocol_sha256": hashlib.sha256((ROOT / "n63-original-protocol.json").read_bytes()).hexdigest(),
    "invocation_history": [{key: r[key] for key in
                            ["round", "kind", "source", "source_sha256", "exit_code"]}
                           for r in rounds],
    "errors": errors, "heldout_tests_run": False,
    "scope": "Finite-set Mobius reconstruction and integer coefficient bounds; no assumed polynomial representation or scalar circuit theorem",
    "mathlib_dependency_provenance": provenance,
    "mathlib_dependency_provenance_sha256": hashlib.sha256(provenance_path.read_bytes()).hexdigest(),
    "compiler_warnings": [] if not final else re.findall(r"[^\n]*warning:[^\n]*", final["stdout"]),
}
(ROOT / "n63-strict-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({key: report[key] for key in
                 ["status", "dev_score", "closed_obligations", "unclosed_obligations", "candidate_rounds", "errors"]}, indent=2))
raise SystemExit(bool(errors))

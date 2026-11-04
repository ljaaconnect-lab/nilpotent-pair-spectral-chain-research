"""Audit the scalar DAG interface; elaboration never discharges its open proposition."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "ScalarDAG.lean"
TRUST = {"propext", "Classical.choice", "Quot.sound"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


source = SOURCE.read_text(encoding="utf-8")
digest = sha(SOURCE)
protocol_path = ROOT / "n71-protocol.json"
formal_path = ROOT / "n71-formal-contract.json"
formal = json.loads(formal_path.read_text(encoding="utf-8"))
graph_path = ROOT / "n71-and-or-graph.json"
graph = json.loads(graph_path.read_text(encoding="utf-8"))
provenance_path = ROOT / "n71-dependency-provenance.json"
provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
rounds = [json.loads(path.read_text(encoding="utf-8")) for path in
          sorted((ROOT / "n71-compiler-rounds").glob("round-*.json"))]
matches = [r for r in rounds if r["source"] == SOURCE.name and r["source_sha256"] == digest]
final = matches[-1] if matches else None
errors = []
code = re.sub(r"/-.*?-/|--[^\n]*", "", source, flags=re.DOTALL)
if re.search(r"\b(?:sorry|admit|axiom|unsafe|native_decide)\b|\+native\b", code):
    errors.append("Forbidden placeholder or untrusted code")
if len(rounds) > 8:
    errors.append("Total compiler-invocation budget exceeded")
if [r["round"] for r in rounds] != list(range(1, len(rounds) + 1)):
    errors.append("Invocation IDs are not unique and contiguous")
for r in rounds:
    if sha(ROOT / r["snapshot"]) != r["source_sha256"]:
        errors.append(f"Source snapshot changed at invocation {r['round']}")
for module, data in provenance["dependencies"].items():
    for path_key, hash_key in [("source_path", "source_sha256"), ("compiled_path", "compiled_sha256")]:
        if sha(Path(data[path_key])) != data[hash_key]:
            errors.append(f"Inherited dependency changed: {module}, {path_key}")
if sha(Path(provenance["compiler_path"])) != provenance["compiler_sha256"]:
    errors.append("Compiler executable changed")
if sha(Path(provenance["replay_report"])) != provenance["replay_report_sha256"]:
    errors.append("Coordinator inherited replay report changed")
if formal["uniformity"]["status"] != "REQUIRED_OPEN":
    errors.append("Operational uniformity must remain explicitly REQUIRED")
if "operational_uniformity" not in graph["nodes"][0]["children"]:
    errors.append("The full root graph omitted operational uniformity")
expected = ["CollisionScalarDAG." + name for name in
            ["rationalBits", "Leaf.eval", "Node.eval", "Program.eval", "Program.gates",
             "Program.literalBound", "Realizes", "AlgebraicCircuitComponent"]]
audited = {}
if not final or final["exit_code"] != 0:
    errors.append("No exit-zero evidence for the exact current source")
else:
    if final["frozen_protocol_sha256"] != sha(protocol_path) or final["formal_contract_sha256"] != sha(formal_path):
        errors.append("Compiled frozen contracts changed")
    if final["dependency_provenance_sha256"] != sha(provenance_path):
        errors.append("Compiled dependency provenance changed")
    output = final["stdout"] + final["stderr"]
    if re.search(r"\bsorryAx\b|declaration uses ['\"]?sorry|\berror:", output):
        errors.append("Rejected final compiler diagnostic")
    for name, raw in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", output):
        audited[name] = {x.strip() for x in raw.split(",") if x.strip()}
    for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", output):
        audited[name] = set()
    for name in expected:
        if name not in audited or audited[name] - TRUST:
            errors.append(f"Missing or unexpected axiom audit: {name}")
theorems = re.findall(r"^theorem\s+(\w+)", source, flags=re.MULTILINE)
report = {
    "node": "n71", "artifact_version": "n71-finite-scalar-DAG-v1",
    "status": "rejected" if errors else "scalar_interface_elaborated_root_open",
    "source": SOURCE.name, "source_sha256": digest,
    "compiled_artifact_sha256": sha(SOURCE.with_suffix(".olean")) if final and final["exit_code"] == 0 and SOURCE.with_suffix(".olean").is_file() else None,
    "interface_elaborated": not errors,
    "elaborated_definitions": [] if errors else expected,
    "open_Lean_goal": "CollisionScalarDAG.AlgebraicCircuitComponent",
    "exact_open_goal": formal["exact_goal"],
    "algebraic_circuit_component_proved": False,
    "uniformity_status": "REQUIRED_OPEN",
    "root_conjecture_verified": False, "root_score": 0, "dev_score": 0,
    "root_metric": "Complete original root obligations / three; syntax elaboration receives no proof credit",
    "root_obligations_closed": [],
    "root_obligations_open": ["Unconditional finite scalar constructor with target identity for every n,A",
                              "Polynomial gate and rational literal bounds for that constructor",
                              "Executable finite constructor and polynomial bit-time proof in n,L"],
    "accepted_root_theorems": [], "other_source_theorems": theorems,
    "axiom_audit": {name: sorted(audited.get(name, set())) for name in expected},
    "accepted_trust_base": sorted(TRUST),
    "compiler_invocations": len(rounds), "all_kind_invocation_budget": 8,
    "candidate_invocations": sum(r["kind"] == "candidate" for r in rounds),
    "dependency_builds": sum(r["kind"] == "dependency_build" for r in rounds),
    "probe_compilations": sum(r["kind"] == "probe" for r in rounds),
    "compiler_exit_code": final["exit_code"] if final else None,
    "final_compiler_round": final["round"] if final else None,
    "invocation_history": [{key: r[key] for key in
                            ["round", "kind", "source_sha256", "exit_code", "elapsed_seconds"]}
                           for r in rounds],
    "infrastructure_incidents": ["Invocation 1 exceeded its 180-second runner deadline with no Lean output; timeout is synthetic exit 124, not a mathematical diagnostic"],
    "frozen_protocol_sha256": sha(protocol_path),
    "formal_contract_sha256": sha(formal_path),
    "AND_OR_graph_sha256": sha(graph_path),
    "blueprint_sha256": sha(ROOT / "n71-blueprint-informel.md"),
    "dependency_provenance_sha256": sha(provenance_path),
    "cache_mutated": False, "heldout_tests_run": False,
    "errors": errors,
}
(ROOT / "n71-strict-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({key: report[key] for key in
                 ["status", "interface_elaborated", "open_Lean_goal", "root_score", "compiler_invocations", "errors"]}, indent=2))
raise SystemExit(bool(errors))

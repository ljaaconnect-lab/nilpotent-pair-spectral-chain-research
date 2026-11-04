"""Strict exact-source audit of the final n38 compiler evidence; no new compiler calls."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TRUST = {"propext", "Classical.choice", "Quot.sound"}
NAMES = ["digit_step_bound", "encodeDigits_lt_pow", "indexedLabelFrom_eq",
         "indexedLabel_eq", "indexedLabel_injective", "indexedLabel_le_max",
         "assignmentLabel_le_max", "assignmentLabel_injective",
         "occupation_all_ones_selector", "assignmentLabel_sum_eq",
         "occupation_sum_selector", "assignmentLabels_nodup", "indexed_assignment_pairing"]
rows = [json.loads(path.read_text()) for path in sorted((ROOT / "n38-compiler-rounds").glob("round-*.json"))]
report = {"node_id": "n38", "artifact_version": "n38-indexed-label-bridge-v1",
          "root_conjecture_verified": False, "heldout_tests_run": False,
          "compiler_invocations": len(rows), "candidate_rounds": sum(row["kind"] == "candidate" for row in rows),
          "dependency_builds": sum(row["kind"] == "dependency_build" for row in rows),
          "prior_global_compiler_rounds": 38, "global_compiler_rounds": 38 + len(rows),
          "expected_declarations": len(NAMES), "accepted_declarations": 0,
          "dependency_audits": {}, "axiom_audit": {}, "errors": []}


def audit_output(row, required_names):
    output = row.get("stdout", "") + row.get("stderr", "")
    if row["exit_code"] != 0 or re.search(r"\bsorryAx\b|\berror:", output):
        report["errors"].append(f"{row['source']}: compiler rejection or untrusted dependency")
    axioms = {}
    for name, raw in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", output):
        axioms[name] = {item.strip() for item in raw.split(",") if item.strip()}
    for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", output):
        axioms[name] = set()
    for name in required_names:
        if name not in axioms:
            report["errors"].append(f"Missing explicit #print axioms evidence: {name}")
        elif axioms[name] - TRUST:
            report["errors"].append(f"Unexpected axioms for {name}: {sorted(axioms[name] - TRUST)}")
    for name, deps in axioms.items():
        if deps - TRUST:
            report["errors"].append(f"Unexpected dependency axioms for {name}")
    return {name: sorted(deps) for name, deps in axioms.items()}


for dependency in ["CoreBridge.lean", "GeneralPairingRing.lean"]:
    sha = hashlib.sha256((ROOT / dependency).read_bytes()).hexdigest()
    matching = [row for row in rows if row["source"] == dependency and row["kind"] == "dependency_build"
                and row["source_sha256"] == sha]
    if not matching:
        report["errors"].append(f"Missing exact-source dependency build: {dependency}")
        continue
    row = matching[-1]
    report["dependency_audits"][dependency] = {"round": row["round"], "source_sha256": sha,
                                               "compiler_exit_code": row["exit_code"],
                                               "axioms": audit_output(row, [])}

source = ROOT / "LabelBridge.lean"
sha = hashlib.sha256(source.read_bytes()).hexdigest()
code = re.sub(r"/-.*?-/|--[^\n]*", "", source.read_text(encoding="utf-8"), flags=re.DOTALL)
if re.search(r"\b(?:sorry|admit|axiom|unsafe)\b", code):
    report["errors"].append("Current LabelBridge contains a placeholder or untrusted declaration")
matching = [row for row in rows if row["source"] == source.name and row["source_sha256"] == sha]
if not matching:
    report["errors"].append("No exact-source final LabelBridge compiler log")
else:
    row = matching[-1]
    report.update(source=source.name, source_sha256=sha, final_compiler_round=row["round"],
                  compiler_exit_code=row["exit_code"], command=row["command"], LEAN_PATH=row["LEAN_PATH"])
    wanted = ["CollisionLabelBridge." + name for name in NAMES]
    found = audit_output(row, wanted)
    report["axiom_audit"] = {name: found.get(name) for name in wanted}
    if row["exit_code"] == 0:
        report["accepted_declarations"] = sum(name in found and set(found[name]) <= TRUST for name in wanted)
report["dev_score"] = report["accepted_declarations"] / len(NAMES) if not report["errors"] else 0.0
report["status"] = "indexed_label_bridge_verified" if not report["errors"] else "rejected"
report["accepted_trust_base"] = sorted(TRUST)
report["scope"] = "Indexed labels, occupancy selector and actual sparse product coefficient; no determinant/Vandermonde or Polynomial-library interpretation, no scalar extraction complexity claim"
(ROOT / "n38-strict-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({key: report[key] for key in ["node_id", "status", "compiler_invocations", "candidate_rounds",
      "dependency_builds", "global_compiler_rounds", "accepted_declarations", "dev_score", "errors"]}, indent=2))
raise SystemExit(0 if not report["errors"] else 1)

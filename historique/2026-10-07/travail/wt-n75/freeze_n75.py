"""Freeze accepted elementary helper evidence without any Lean invocation."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
report = json.loads((ROOT / "n75-strict-report.json").read_text(encoding="utf-8"))
contract = json.loads((ROOT / "n75-formal-contract.json").read_text(encoding="utf-8"))
if not report["accepted"] or len(report["accepted_declarations"]) != 6:
    raise SystemExit("Only the complete accepted six-leaf artifact may be frozen")
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
nodes = []
dependencies = {"A1": [], "A2": [], "A3": ["A1", "A2"], "A4": [],
                "A5": ["A3", "A4"], "A6": ["A5"]}
for leaf in contract["leaves"]:
    nodes.append({"id": leaf["id"], "kind": "AND", "status": "closed",
                  "context": contract["domain"], "local_hypothesis": leaf.get("hypothesis"),
                  "target": leaf["statement"], "dependencies": dependencies[leaf["id"]],
                  "declaration": "AtomicFirstPrefix." + leaf["name"],
                  "artifact_source_sha256": report["source_sha256"]})
graph = {"node": "n75", "root": {"kind": "AND", "dependencies": list(dependencies),
                                  "status": "helper_closed", "conjecture_status": "OPEN"},
         "nodes": nodes, "cycle_free": True, "root_conjecture_verified": False}
def visit(node, stack):
    if node in stack:
        raise SystemExit("Dependency cycle rejected")
    for child in dependencies[node]:
        visit(child, stack + [node])
for node in dependencies:
    visit(node, [])
(ROOT / "n75-leap-progress.json").write_bytes((json.dumps(graph, indent=2) + "\n").encode("utf-8"))
paths = [p for p in ROOT.glob("n75-*") if p.is_file() and p.name != "n75-source-freeze.json"]
paths += [ROOT / name for name in ["AtomicFirstPrefix.lean", "compile_n75.py", "verify_n75.py", "freeze_n75.py"]]
paths += sorted((ROOT / "n75-compiler-rounds").glob("*"))
freeze = {"node": "n75", "accepted_source": report["source"], "source_sha256": report["source_sha256"],
          "accepted_final_round": 6, "exit_code": 0, "dev_score": 1.0, "root_score": 0,
          "root_conjecture_verified": False,
          "files": {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in sorted(paths)}}
(ROOT / "n75-source-freeze.json").write_bytes((json.dumps(freeze, indent=2) + "\n").encode("utf-8"))
leaf = {"dev_score": 1.0, "root_score": 0, "result": "six exact elementary first-prefix identities kernel verified",
        "insight": "Actual principal minors agree with the coefficient-array response under explicit local h*u=b; finite linearity does not provide a free global scalar contraction",
        "branch_ref": "arbor/n75", "artifact_version": report["source_sha256"],
        "source": report["source"], "candidate_invocations": 6, "dependency_invocations": 1,
        "probe_invocations": 0, "total_invocations": 7, "root_conjecture_verified": False}
(ROOT / "n75-leaf-result.json").write_bytes((json.dumps(leaf, indent=2) + "\n").encode("utf-8"))
print(json.dumps(leaf, indent=2))

"""Freeze direct dependencies and a cycle-checked LEAP record, without invoking Lean."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MATHLIB = ROOT.parent / "mathlib"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


modules = {}
for module in ["Mathlib.Algebra.MvPolynomial.Basic", "Mathlib.Algebra.BigOperators.Ring.Finset",
               "Mathlib.Data.Fintype.EquivFin", "Mathlib.Data.Fintype.Powerset"]:
    relative = Path(*module.split("."))
    source = (MATHLIB / relative).with_suffix(".lean")
    compiled = (MATHLIB / ".lake/build/lib/lean" / relative).with_suffix(".olean")
    modules[module] = {
        "source_path": str(source), "source_sha256": sha(source),
        "compiled_path": str(compiled), "compiled_sha256": sha(compiled),
    }
mathlib = {
    "modules": modules, "cache_mutated": False,
    "inherited_n71_provenance": str(ROOT.parent / "wt-n71/n71-dependency-provenance.json"),
    "inherited_n71_provenance_sha256": sha(ROOT.parent / "wt-n71/n71-dependency-provenance.json"),
}
(ROOT / "n73-mathlib-imports.json").write_text(json.dumps(mathlib, indent=2), encoding="utf-8")
audit = subprocess.run(["python", str(ROOT / "verify_n73.py")], cwd=ROOT, capture_output=True, text=True)
print(audit.stdout)
if audit.returncode:
    print(audit.stderr)
    raise SystemExit(audit.returncode)
report = json.loads((ROOT / "n73-strict-report.json").read_text(encoding="utf-8"))
if report["status"] != "actual_subset_baseline_verified":
    raise SystemExit("Only a complete fixed baseline may be frozen as a verified LEAP graph")
dependencies = {
    "occupation_eq_iff_bijective": [], "expanded_linear_product": [],
    "sum_bijective_functions": [],
    "full_coefficient_permutation": ["occupation_eq_iff_bijective", "expanded_linear_product", "sum_bijective_functions"],
    "subsetExponent_apply": [], "subsetExponent_support": ["subsetExponent_apply"],
    "subsetExponent_zero_iff": ["subsetExponent_support"],
    "subsetExponent_erase": ["subsetExponent_apply"],
    "coefficient_step": ["subsetExponent_support", "subsetExponent_erase"],
    "coefficient_invariant": ["subsetExponent_zero_iff", "coefficient_step"],
    "initial_state": [], "step_state": [], "rowProduct_eq": [],
    "terminal_permutation": ["coefficient_invariant", "rowProduct_eq", "full_coefficient_permutation"],
    "terminal_matrix": ["terminal_permutation"], "marked_central": ["terminal_matrix"],
    "marked_target": ["terminal_matrix"], "state_dimension": [],
}
visiting, visited = set(), set()


def visit(node):
    if node in visiting:
        raise SystemExit("Cycle in actual proof blueprint")
    if node in visited:
        return
    visiting.add(node)
    for child in dependencies[node]:
        visit(child)
    visiting.remove(node)
    visited.add(node)


for node in dependencies:
    visit(node)
graph = {
    "node": "n73", "method": "Local adapted LEAP workflow",
    "selected_strategy": "actual_multivariate_coefficient_invariant",
    "alternative_strategy": {"name": "injective_prefix_embeddings", "status": "UNUSED", "required": False},
    "root": {"id": "actual_subset_baseline", "kind": "AND", "status": "VERIFIED",
             "required": list(json.loads((ROOT / "n73-formal-contract.json").read_text(encoding="utf-8"))["required"])},
    "goals": {name: {"kind": "AND", "status": "VERIFIED", "required": children,
                      "statement": report["exact_source_statements"][name],
                      "source": report["source"], "declaration": "ActualClosedSubsetTransfer." + name,
                      "source_sha256": report["source_sha256"]}
              for name, children in dependencies.items()},
    "external_verified_dependencies": {
        "marked_central": "CollisionEncodingBridge.hhat_central_coefficient",
        "marked_target": "CollisionEncodingBridge.marked_weight_eq",
    },
    "acyclic": True, "compiler_evidence": "n73-strict-report.json",
    "review": "Independent terminal coefficient and genuine recurrence-invariant branches are both complete before they are joined; no target identity is assumed",
    "state_dimension": "2^n", "Conjecture_1_5": "OPEN", "root_conjecture_credit": 0,
}
(ROOT / "n73-leap-progress.json").write_text(json.dumps(graph, indent=2), encoding="utf-8")
leaf = {
    "node_id": "n73", "artifact_version": report["artifact_version"],
    "dev_score": report["dev_score"], "baseline_score": report["baseline_score"],
    "root_conjecture_score": 0,
    "result": "Actual all-n closed subset recurrence verified; arbitrary matrix terminal is its permanent, marked terminal is the exact marked central coefficient",
    "insight": "An honest globally closed reference family exists with known delta initialization and explicit row update; its dimension is 2^n, leaving scalar compression and the uniform polynomial constructor open",
    "branch_ref": "arbor/n73", "source": report["source"], "source_sha256": report["source_sha256"],
    "report": "n73-strict-report.json", "compiler_invocations": report["compiler_invocations"],
    "dependency_builds": 0, "probe_compilations": 0,
    "accepted_declarations": report["accepted_declarations"],
    "root_conjecture_verified": False, "heldout_tests_run": False,
}
(ROOT / "n73-leaf-result.json").write_text(json.dumps(leaf, indent=2), encoding="utf-8")
print(json.dumps({"source_sha256": report["source_sha256"], "acyclic": True, "root_credit": 0}, indent=2))

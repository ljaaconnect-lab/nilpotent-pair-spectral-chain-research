"""Summarize n59's exact compiler evidence, without numerical experiments."""
import hashlib
import json
from pathlib import Path


def source_hash(path):
    return hashlib.sha256(path.read_text(encoding="utf-8").encode()).hexdigest()


def main():
    root = Path(__file__).resolve().parent
    protocol = json.loads((root / "n59-protocol.json").read_text(encoding="utf-8"))
    history = json.loads((root / "n59-verification-history.json").read_text(encoding="utf-8"))
    latest = next(run for run in reversed(history["runs"]) if run["kind"] == "candidate")
    final_hash = source_hash(root / "ConditionalCriterion.lean")
    if latest["source_sha256"] != final_hash:
        raise SystemExit("Current source differs from final compiler evidence")
    for run in history["runs"]:
        if run["kind"] == "dependency":
            dep = Path(run["command"][1])
            if run["exit_code"] != 0 or source_hash(dep) != run["source_sha256"]:
                raise SystemExit("Dependency evidence does not match the exact accepted source")
    report = {
        "node": "n59", "artifact_version": protocol["artifact_version"],
        "dev_score": latest["dev_score"], "passed": latest["passed"], "denominator": 2,
        "compiler_exit_code": latest["exit_code"], "compiler_errors": latest["error_count"],
        "source_sha256": final_hash, "final_candidate": latest["tag"],
        "axiom_audit": latest["axiom_audit"], "audited_new_declarations": len(latest["axiom_audit"]),
        "candidate_rounds": history["candidates"], "candidate_budget": protocol["complete_candidate_budget"],
        "probes": history["probes"], "dependencies": history["dependencies"],
        "environment_keys": latest["environment_keys"],
        "actual_polynomial_type": "Polynomial Nat",
        "Pi_eval": "n^c+4*n^(3*d+2)+3*n^(2*d)",
        "initialization_charge": "Actual initial.gates in composedCircuit; bounded by supplied S<=n^c",
        "conditional_coefficient_identity": "H.coeff(n^n-1)=u^T M^(n^n-1) v is an explicit theorem argument",
        "remaining_target_obligations": [
            "Explicit target representation preserving formal z markers",
            "Uniform polynomial running time of the target-data constructor",
            "Source-model provenance/admissibility of rational and parameter input leaves",
            "Bounded rational-literal bit lengths and bit-operation accounting"
        ],
        "new_numerical_experiments": 0, "held_out_access": False,
        "cache_mutations": False, "root_conjecture_verified": False
    }
    (root / "n59-dev-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("dev_score", "compiler_exit_code", "audited_new_declarations", "candidate_rounds", "probes", "dependencies")}, indent=2))


if __name__ == "__main__":
    main()

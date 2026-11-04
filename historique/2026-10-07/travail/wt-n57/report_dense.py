"""Consolidate actual n57 proof/evaluator evidence without rerunning it."""
import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    root = Path(__file__).resolve().parent
    history = json.loads((root / "n57-verification-history.json").read_text(encoding="utf-8"))
    latest = next(run for run in reversed(history["runs"]) if run["kind"] == "candidate")
    # Match the compiler's newline-normalized text hashing convention.
    source_sha = hashlib.sha256((root / "MatrixScalarCompiler.lean").read_text(encoding="utf-8").encode()).hexdigest()
    if latest["source_sha256"] != source_sha:
        raise SystemExit("Final source does not match preserved compiler evidence")
    finite = json.loads((root / "n57-python-report.json").read_text(encoding="utf-8"))
    protocol_sha = digest(root / "n57-protocol.json")
    if finite["protocol_sha256"] != protocol_sha:
        raise SystemExit("Protocol differs from positive evaluation protocol")
    report = {
        "node": "n57", "artifact_version": "n57-dense-scalar-compiler-v1",
        "dev_score": latest["dev_score"], "formal_passed": latest["passed"], "formal_denominator": 4,
        "python_score": finite["python_score"], "python_passed": finite["passed"], "python_denominator": 16,
        "compiler_exit_code": latest["exit_code"], "compiler_errors": latest["error_count"],
        "final_candidate": latest["tag"], "source_sha256": source_sha,
        "protocol_sha256": protocol_sha, "axiom_audit": latest["axiom_audit"],
        "audited_new_declarations": len(latest["axiom_audit"]),
        "candidate_rounds": history["candidates"], "candidate_budget": 20,
        "probes": history["probes"], "dependency_compiles": history["dependencies"],
        "mathlib_environment_keys_used": latest["environment_keys"],
        "measured_python_scalar_counts": finite["measured_counts"],
        "formally_derived_counts": {
            "dense_product": "2*r^3-r^2, for r>=1",
            "contraction": "2*r^2+r-1, for r>=1",
            "total": "length(binaryPlan(k))*(2*r^3-r^2)+(2*r^2+r-1), for r>=1",
            "conditional_budget": "S+4*r^3*n^2+3*r^2, for r>=1,n>=2,k=n^n-1"
        },
        "scalar_dag_files": [{"file": str(path.relative_to(root)), "sha256": digest(path)}
                             for path in sorted((root / "scalar-dags").glob("*.json"))],
        "semantic_scope": "Universal Lean theorem for the constructed compositional scalar DAG; exact positive agreement of Python serialized SSA implementation against an independent oracle is finite evidence.",
        "ssa_lowering_formally_verified": False,
        "explicit_initial_data": "Every M,u,v scalar is supplied as a leaf; their construction cost S is a separate explicit hypothesis.",
        "root_representation_established": False,
        "held_out_access": False, "cache_mutations": False
    }
    (root / "n57-dev-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("dev_score", "python_score", "compiler_exit_code", "audited_new_declarations", "candidate_rounds", "probes")}, indent=2))


if __name__ == "__main__":
    main()

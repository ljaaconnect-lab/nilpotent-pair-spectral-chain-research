"""Summarize preserved Lean compiler evidence without rerunning a proof."""
import hashlib
import json
from pathlib import Path

from power_plan import instructions


def main():
    root = Path(__file__).resolve().parent
    history = json.loads((root / "power-verification-history.json").read_text(encoding="utf-8"))
    latest = next(run for run in reversed(history["runs"]) if run["kind"] == "candidate")
    source_hash = hashlib.sha256((root / "PowerCompiler.lean").read_text(encoding="utf-8").encode()).hexdigest()
    if source_hash != latest["source_sha256"]:
        raise SystemExit("Current final source differs from latest compiler evidence")
    frozen = json.loads((root / "n40-obligations.json").read_text(encoding="utf-8"))
    report = {
        "node": "n40",
        "artifact_version": frozen["artifact_version"],
        "boundary": frozen["boundary"],
        "frozen_denominator": 3,
        "verified_obligations": latest["main_obligations_passed"],
        "dev_score": latest["score"],
        "final_candidate": latest["tag"],
        "compiler_exit_code": latest["exit_code"],
        "compiler_errors": latest["error_count"],
        "final_source_sha256": source_hash,
        "axiom_audit": latest["axiom_audit"],
        "complete_candidate_rounds": history["candidate_rounds"],
        "complete_candidate_budget": frozen["complete_candidate_round_budget"],
        "incremental_probes": history["probes"],
        "central_dag_counts": [
            {"n": n, "K": n ** n - 1,
             "shared_multiplications": len(instructions(n ** n - 1)),
             "verified_upper_bound": 2 * n ** 2}
            for n in range(2, 6)
        ],
        "extra_helper_outside_metric": "SharedBinaryPower.central_plan_gate_bound",
        "conditional_dense_scalar_budget": "S+4*r^3*n^2+3*r^2 for n>=2,r>=1 and explicitly constructed M,u,v",
        "remaining_constructive_obligation": "Explicit polynomial-dimensional M,u,v and polynomial-cost initial data representing the target; no such representation is asserted",
        "root_conjecture_verified": False,
        "held_out_boundary_accessed": False,
        "evidence_limitations": [
            "The original frozen manifest was written before the first probe; this summary is retrospective.",
            "Probe 01 suffered a UTF-8 logging harness failure, so its compiler exit is unknown and its score is null.",
            "Probe 02's old error regex did not count error(lean.unknownIdentifier); its nonzero compiler exit and original stdout remain preserved.",
            "Archived probe skeletons may contain sorry and are excluded from accepted proof artifacts."
        ]
    }
    (root / "n40-dev-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in
          ("dev_score", "compiler_exit_code", "final_candidate", "complete_candidate_rounds", "incremental_probes", "central_dag_counts")}, indent=2))


if __name__ == "__main__":
    main()

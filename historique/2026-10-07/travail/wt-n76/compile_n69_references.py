"""Compile and count analytical n69 interfaces; never evaluate B inputs.

This command is not an identity evaluator, and cannot produce a dev score.
The frozen root protocol permits testing only an eligible polynomial root
candidate. None of these three partial interfaces meets that criterion.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from n69_interfaces import (compile_joint_phase,compile_H_pf,
                            compile_rowjet_reference,reference_gate_formula)


def main():
    p = Path(__file__).resolve().parent
    frozen = json.loads((p/"n69-source-freeze.json").read_text(encoding="utf-8"))
    for name,digest in frozen["files"].items():
        if hashlib.sha256((p/name).read_bytes()).hexdigest() != digest:
            raise RuntimeError(f"changed frozen file: {name}")
    costs = []
    for n in (2,3,4,5):
        row = {"n":n,"source":"actual DAG construction, without numerical interpretation"}
        for label,builder in (("joint_phase",lambda:compile_joint_phase(n*n)),
                              ("fixed_H_pf",lambda:compile_H_pf(n)),
                              ("rowjet_generic_reference",lambda:compile_rowjet_reference(n)),
                              ("rowjet_marked_reference",lambda:compile_rowjet_reference(n,True))):
            graph,out = builder()
            name = f"n69-{label}-n{n}.json"
            serialized = graph.serialize(out)
            serialized["scope"] = label
            serialized["root_polynomial_candidate"] = False
            if label == "rowjet_marked_reference":
                serialized["leaf_semantics"] = "p_i_j=1+a_i_j^2; z is the sole polynomial variable"
            (p/name).write_text(json.dumps(serialized,separators=(",",":"))+"\n",encoding="utf-8")
            row[label] = {"gates":graph.gates,"nodes":len(graph.nodes),"output":out,
                          "artifact":name,"state_dimension":(1 << n) if "rowjet" in label else None}
            if label == "joint_phase" and graph.gates != 73*n*n:
                raise RuntimeError("joint-phase cost construction mismatch")
            if label.startswith("rowjet") and graph.gates != reference_gate_formula(n,label.endswith("marked_reference")):
                raise RuntimeError("row-jet cost construction mismatch")
        costs.append(row)
    result = {"node":"n69","artifact_version":"n69-joint-interfaces-v1",
              "dev_score":None,"eligible_complete_polynomial_candidates":0,
              "root_obligations_discharged":0,"root_obligations_total":3,
              "construction_measurements":costs,"mathematical_identity_checks":0,
              "B_input_evaluations":0,"heldout_access":False,"Lean_compiles":0,
              "warning":"Counts charge explicit partial or exponential circuits only; none is a polynomial root extractor"}
    (p/"n69-construction-costs.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()

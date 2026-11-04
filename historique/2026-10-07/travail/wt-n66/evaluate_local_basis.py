"""Frozen n66 positive SUPPORTING evaluator; root obligations stay separate."""
import hashlib
import json
from pathlib import Path

import sympy as sp

from local_basis import (layout, local_basis_circuit, local_pfaffian_minor,
                         residual_circuit, scalar_interpret)

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    cases = []
    graph,forward,restored = local_basis_circuit(roundtrip=True)
    formal = {f"f{i}":sp.Symbol(f"f{i}") for i in range(16)}
    values = scalar_interpret(graph,formal)
    for mask,node in enumerate(forward):
        expected = sum((-1)**((mask & source).bit_count())*formal[f"f{source}"]
                       for source in range(16))
        cases.append({"obligation":"formal_local_H4","index":mask,
                      "pass":sp.expand(values[node]-expected) == 0})
    for mask,node in enumerate(restored):
        cases.append({"obligation":"formal_local_inverse_H4","index":mask,
                      "pass":sp.expand(values[node]-formal[f"f{mask}"]) == 0})
    copy = {f"f{i}":sp.Integer(i in (0,15)) for i in range(16)}
    copy_values = scalar_interpret(graph,copy)
    for mask,node in enumerate(forward):
        cases.append({"obligation":"COPY4_to_fixed_J4_minor","index":mask,
                      "pass":copy_values[node] == 2*local_pfaffian_minor(mask)})
    residual_graph,residual = residual_circuit()
    variables = {name:sp.Symbol(name) for name in ("a","b","U","V")}
    residual_values = scalar_interpret(residual_graph,variables)
    cases.append({"obligation":"formal_chiral_residual",
                  "pass":sp.expand(residual_values[residual]-variables["U"]*variables["V"]) == 0})
    layouts = []
    for n in (2,3,4,5):
        item = layout(n)
        generic_B = sp.symbols(f"b0:{n*n}")
        item["generic_formal_entry_count"] = len(generic_B)
        item["generic_entries_used_by_local_copy"] = 0
        item["entire_transformed_families_compiled"] = False
        layouts.append(item)
        cases.append({"obligation":"counted_local_layout","n":n,
                      "pass":item["total_local_positions"] == 4*n*n and graph.gates == 208
                      and residual_graph.gates == 18})
    passed = sum(case["pass"] for case in cases)
    report = {"node":"n66","protocol_sha256":sha(HERE/"n66-protocol.json"),
              "evaluator_sha256":sha(Path(__file__)),
              "supporting_passes":passed,"supporting_count":len(cases),
              "supporting_pass_fraction":passed/len(cases),"cases":cases,
              "local_forward_gates":96,"local_inverse_additional_gates":112,
              "local_roundtrip_gates":graph.gates,"residual_gates":residual_graph.gates,
              "layouts":layouts,"root_obligations":[
                  {"id":"explicit_root_scalar_data_and_transition","status":"unclosed"},
                  {"id":"polynomial_root_gate_literal_initialization_certificate","status":"unclosed"},
                  {"id":"exact_root_target_identity","status":"unclosed"}],
              "root_closed_obligation_count":0,"root_obligation_count":3,
              "dev_score":0.0,"root_conjecture_verified":False,
              "verification_scope":"finite exact symbolic supporting checks only; no root target evaluator exists"}
    (HERE/"n66-support-report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({key:report[key] for key in ("supporting_passes","supporting_count",
          "supporting_pass_fraction","dev_score","root_conjecture_verified")},indent=2))


if __name__ == "__main__":
    run()

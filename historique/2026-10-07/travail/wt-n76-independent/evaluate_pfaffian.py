"""Frozen all-matching development evaluator for n64; never reads B_test."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from time import perf_counter

from euler_compiler import matching_coefficients
from pfaffian_coefficients import (matchings,mobius_coefficient,column_pattern,
    local_matrix,fixed_port_matrix,principal,principal_ports,pfaffian_oracle,
    trace_circuit,evaluate_trace,matching_count,trace_gate_formula)


ROOT = Path(__file__).resolve().parent
SOURCES = ["pfaffian_coefficients.py","evaluate_pfaffian.py","euler_compiler.py",
           "candidate.py","n64-protocol.json"]


def hashes():
    return {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCES}


def template_audit(graph,output,d):
    inputs,counts = set(),Counter()
    for i,node in enumerate(graph.nodes):
        op = node["op"]
        counts[op] += 1
        if op in ("add","mul"):
            assert 0 <= node["left"] < i and 0 <= node["right"] < i
        elif op == "variable":
            inputs.add(node["name"])
        else:
            assert op == "constant"
    assert inputs == {f"a_{i}_{j}" for i in range(d) for j in range(i+1,d)}
    assert counts["add"]+counts["mul"] == graph.gates == trace_gate_formula(d)
    assert 0 <= output < len(graph.nodes)
    return {"d":d,"gates":graph.gates,"counts":dict(counts),"input_upper_entries":len(inputs),
        "topological_binary_scalar_graph":True,
        "formal_semantics_status":"Finite exact checks only; generic Lean trace compiler theorem remains separate"}


def validate(n):
    started = perf_counter()
    alpha,old_stats = matching_coefficients(n)
    fixed = fixed_port_matrix(n)
    patterns,templates = {},{}
    labels = ("n61_equals_mobius","local_pf_equals_mobius","fixed_ports_pf_equals_mobius","charged_trace_matches_both_pf")
    scores = Counter({label:0 for label in labels})
    records = []
    scalar_evaluations = 0
    template_stats = {}
    for matching in matchings(n):
        pattern = column_pattern(n,matching)
        local = local_matrix(pattern)
        paired = principal(fixed,principal_ports(n,matching))
        if pattern not in patterns:
            local_pf,local_stats = pfaffian_oracle(local)
            paired_pf,paired_stats = pfaffian_oracle(paired)
            trace_values = []
            for matrix in (local,paired):
                d = len(matrix)
                if d not in templates:
                    graph,output = trace_circuit(d)
                    template_stats[str(d)] = template_audit(graph,output,d)
                    templates[d] = (graph,output)
                    path = ROOT/f"n64-trace-dag-d{d}-n{n}.json"
                    path.write_text(json.dumps({"d":d,**graph.serialize(output)},separators=(",",":")))
                    template_stats[str(d)]["serialized_path"] = path.name
                    template_stats[str(d)]["serialized_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                value,stats = evaluate_trace(*templates[d],matrix)
                trace_values.append(value)
                scalar_evaluations += stats["actual_scalar_gate_evaluations"]
            patterns[pattern] = (local_pf,paired_pf,trace_values,local,paired,local_stats,paired_stats)
        local_pf,paired_pf,traces,stored_local,stored_paired,_,_ = patterns[pattern]
        mobius = mobius_coefficient(n,matching)
        current = alpha.get(frozenset(matching),0)
        checks = {labels[0]:current == mobius,
                  labels[1]:(-1)**len(matching)*local_pf == mobius,
                  labels[2]:paired_pf == mobius,
                  labels[3]:traces[0] == local_pf and traces[1] == paired_pf and local == stored_local and paired == stored_paired}
        scores.update({label:int(value) for label,value in checks.items()})
        records.append({"matching":list(matching),"pattern":list(pattern),"coefficient":mobius,
            "n61":current,"local_pf_corrected":(-1)**len(matching)*local_pf,"fixed_pf":paired_pf,
            "checks":checks})
    assert len(records) == matching_count(n)
    passed = sum(scores.values())
    return {"node":"n64","n":n,"matching_count":len(records),"passed":passed,"total":4*len(records),
        "scores":dict(scores),"fixed_matrix_order":len(fixed),"unique_column_patterns":len(patterns),
        "actual_scalar_gate_evaluations_across_cached_checks":scalar_evaluations,
        "templates":template_stats,"maximum_coefficient_bits":max(abs(record["coefficient"]).bit_length() for record in records),
        "bit_bound_n_plus_1":all(abs(record["coefficient"]).bit_length() <= n+1 for record in records),
        "old_preprocessing":old_stats,"records":records,"source_hashes":hashes(),
        "elapsed_seconds":perf_counter()-started,"held_out_access":False,
        "root_conjecture_verified":False,"global_synchronized_contraction_verified":False,
        "scope":"Finite exact local/fixed-principal identities and actual scalar compiler evaluations; no global sum algorithm"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n",type=int)
    parser.add_argument("--child",action="store_true")
    parser.add_argument("--aggregate",action="store_true")
    args = parser.parse_args()
    if args.child:
        report = validate(args.n)
        (ROOT/f"n64-dev-n{args.n}.json").write_text(json.dumps(report,indent=2))
        print(json.dumps({key:report[key] for key in ("n","passed","total","unique_column_patterns","elapsed_seconds")},indent=2),flush=True)
        return
    if args.aggregate:
        reports = [json.loads((ROOT/f"n64-dev-n{n}.json").read_text()) for n in (2,3,4,5)]
        passed = sum(report["passed"] for report in reports)
        total = sum(report["total"] for report in reports)
        assert total == 7184
        final = {"node":"n64","artifact_version":"n64-fixed-ports-v1","passed":passed,"total":total,"dev_score":passed/total,
                 "n_reports":[{key:r[key] for key in r if key != "records"} for r in reports],"source_hashes":hashes(),
                 "global_synchronized_contraction_verified":False,"root_conjecture_verified":False,"held_out_access":False}
        (ROOT/"n64-dev-report.json").write_text(json.dumps(final,indent=2))
        print(json.dumps({key:final[key] for key in ("node","passed","total","dev_score","source_hashes")},indent=2))
        return
    command = [sys.executable,str(Path(__file__).resolve()),"--child","--n",str(args.n)]
    try:
        completed = subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=120)
        log = {"command":command,"exit_code":completed.returncode,"stdout":completed.stdout,"stderr":completed.stderr}
    except subprocess.TimeoutExpired as error:
        log = {"command":command,"exit_code":None,"status":"timeout","stdout":str(error.stdout),"stderr":str(error.stderr)}
    (ROOT/f"n64-dev-log-n{args.n}.json").write_text(json.dumps(log,indent=2))
    print(json.dumps(log,indent=2),flush=True)
    if log["exit_code"] != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

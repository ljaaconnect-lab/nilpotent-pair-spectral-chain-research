"""Frozen positive local evaluator for n66 carry supplement v1.

Forty aggregate finite identities.  No held-out input, permanent target,
counterexample campaign, or coefficient projection is evaluated.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import carry_basis as c


def check_local():
    graph,out = c.compile_local_T()
    matrix = [[0,1,-1,1],[-1,0,-1,1],[1,1,0,1],[-1,-1,-1,0]]
    pf = c.pfaffian_evaluator(matrix)
    return all(c.local_T(*w) == c.principal_value(pf,w) ==
               c.scalar_evaluate(graph,out,dict(zip(("p","x","y","q"),w)))
               for w in c.words(4))


def check_native(N):
    graph,out = c.compile_native_kernel(N)
    pf = c.pfaffian_evaluator(c.native_matrix(N))
    for x in c.words(N):
        for y in c.words(N):
            for q in (0,1):
                word = tuple(bit for pair in zip(x,y) for bit in pair)+(q,)
                assignments = {**{f"x{i}":x[i] for i in range(N)},
                               **{f"y{i}":y[i] for i in range(N)},"q":q}
                if not (c.native_kernel(x,y,q) == c.principal_value(pf,word) ==
                        c.scalar_evaluate(graph,out,assignments)):
                    return False
    return True


def check_shuffle(N):
    for x in c.words(N):
        for y in c.words(N):
            occupied = {("x",i) for i in range(N) if x[i]}|{
                ("y",i) for i in range(N) if y[i]}
            actual = c.selected_shuffle(c.native_order(N),c.grouped_order(N),occupied)
            if actual != c.grouped_shuffle(x,y):
                return False
            for q in (0,1):
                if c.native_kernel(x,y,q)*c.sgn(actual) != c.grouped_kernel(x,y,q):
                    return False
    return True


def check_grouped(N):
    pf = c.pfaffian_evaluator(c.grouped_matrix(N))
    return all(c.grouped_kernel(x,y,q) == c.principal_value(pf,x+y+(q,))
               for x in c.words(N) for y in c.words(N) for q in (0,1))


def check_orthogonality(N):
    words = c.words(N)
    rows = [[c.native_kernel(x,y,(c.parity(x)+c.parity(y))%2)
             for y in words] for x in words]
    return all(sum(a*b for a,b in zip(rows[i],rows[j])) ==
               ((1 << N) if i == j else 0)
               for i in range(len(words)) for j in range(len(words)))


def check_pair_cap(m):
    words = c.words(2*m)
    paired = [c.paired_word(r) for r in c.words(m)]
    rows = {x:[c.native_kernel(x,y,c.parity(x)) for y in paired] for x in words}
    return all(sum(a*b for a,b in zip(rows[xF],rows[xG])) == c.pair_cap(xF,xG)
               for xF in words for xG in words)


def check_cap_shuffle(m):
    for u in c.words(m):
        for v in c.words(m):
            for s in c.words(m):
                qF,qG = (sum(u)+sum(s))%2,(sum(v)+sum(s))%2
                occupied = {(label,e) for label,bits in (("aF",u),("aG",v),
                            ("bF",s),("bG",s)) for e,bit in enumerate(bits) if bit}
                if qF: occupied.add(("qF",0))
                if qG: occupied.add(("qG",0))
                actual = c.selected_shuffle(c.cap_order_O(m),c.cap_order_P(m),occupied)
                if actual != c.cap_shuffle_formula(u,v,s):
                    return False
    return True


def check_factor_cap(m):
    # Equality on synchronized s; both expressions are identically zero off it.
    return all(c.synchronized_cap(u,v,s,s,qF,qG) == c.factor_cap(u,v,s,s,qF,qG)
               for u in c.words(m) for v in c.words(m) for s in c.words(m)
               for qF in (0,1) for qG in (0,1))


def main():
    root = Path(__file__).resolve().parent
    protocol = json.loads((root/"n66-carry-protocol.json").read_text(encoding="utf-8"))
    freeze = json.loads((root/"n66-carry-freeze.json").read_text(encoding="utf-8"))
    for name,digest in freeze["files"].items():
        actual = hashlib.sha256((root/name).read_bytes()).hexdigest()
        if actual != digest:
            raise RuntimeError(f"frozen source changed: {name}")
    base = json.loads((root/"n66-source-freeze.json").read_text(encoding="utf-8"))
    for name,digest in base["files"].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest() != digest:
            raise RuntimeError(f"base n66 source changed: {name}")
    results = [{"identity":"local_T_gaussian_and_scalar","pass":check_local()}]
    for name,fn in (("native_coherent_gaussian_and_scalar",check_native),
                    ("actual_grouped_shuffle",check_shuffle),
                    ("grouped_coherent_gaussian",check_grouped),
                    ("abstract_Walsh_orthogonality",check_orthogonality)):
        for N in protocol["kernel_sizes"]:
            results.append({"identity":name,"N":N,"pass":fn(N)})
    for name,fn in (("abstract_paired_copy_transform",check_pair_cap),
                    ("actual_cap_shuffle",check_cap_shuffle),
                    ("four_factor_parity_cap_identity",check_factor_cap)):
        for m in protocol["pair_sizes"]:
            results.append({"identity":name,"m":m,"pass":fn(m)})
    assert len(results) == protocol["support_denominator"]
    passed = sum(row["pass"] for row in results)
    local_graph,local_out = c.compile_local_T()
    report = {"node":"n66","artifact_version":"carry-supplement-v1",
              "root_dev_score":0.0,"root_obligation_denominator":3,
              "root_obligations_closed":0,"root_conjecture_proved":False,
              "support_passes":passed,"support_denominator":len(results),
              "support_score":passed/len(results),"support_results":results,
              "local_scalar_gates":local_graph.gates,"local_scalar_output":local_out,
              "measurements":[c.measurements(n) for n in (2,3,4,5)],
              "lean_candidate_compiles":0,"lean_verified_supplement_theorems":[],
              "base_freeze_unchanged":True,"heldout_access":False,
              "global_status":"unclosed: coherent graded routing does not equal the abstract ordinary basis transform"}
    (root/"n66-carry-report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"support_passes":passed,"support_denominator":len(results),
                      "root_dev_score":0.0,"measurements":report["measurements"]},indent=2))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Authorized n76 Lean runner, strict total cap3; no dependency compilation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

DECLARATIONS = ["B1_distribution","erase_diagonal","B2_remove_diagonal",
                "seed_is_empty","insertion_is_erase","pair_exponent_iff",
                "table_two_pair_expansion","table_two_zero_of_card_ne","signed_response_eq_mass",
                "powerset_pair_indicator","table_two_mass",
                "B3_actual_response","complement_sum","initialized_diagonal",
                "initialized_totals","B4_initialized_query"]
LEAVES = {"B1":"B1_distribution","B2":"B2_remove_diagonal",
          "B3":"B3_actual_response","B4":"B4_initialized_query"}
ALLOWED = {"propext","Classical.choice","Quot.sound"}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    arg = argparse.ArgumentParser()
    arg.add_argument("--authorized",action="store_true")
    args = arg.parse_args()
    if not args.authorized:
        raise SystemExit("Coordinator authorization required; no compiler was invoked")
    here = Path(__file__).resolve().parent
    root = here.parent.parent
    reports = sorted(here.glob("n76-round-*-report.json"))
    if len(reports) >= 3:
        raise SystemExit("Total compiler invocation ceiling3 reached")
    freeze = json.loads((here/"n76-source-freeze.json").read_text(encoding="utf-8"))
    for name,digest in freeze["files"].items():
        if sha(here/name) != digest:
            raise SystemExit(f"Frozen preparation changed: {name}")
    dependency = json.loads((here/"n76-dependency-provenance.json").read_text(encoding="utf-8"))
    for key in ("baseline_source","baseline_olean"):
        if sha(Path(dependency[key])) != dependency[key+"_sha256"]:
            raise SystemExit(f"Dependency changed: {key}")
    source = here/"AtomicSecondPrefix.lean"
    source_text = source.read_text(encoding="utf-8")
    if re.search(r"\b(sorry|axiom|native_decide)\b",source_text):
        raise SystemExit("Forbidden proof token; no compiler invoked")
    for name in DECLARATIONS:
        if f"#print axioms AtomicSecondPrefix.{name}" not in source_text:
            raise SystemExit(f"Missing axiom audit directive: {name}")
    index = len(reports)+1
    archive = here/f"AtomicSecondPrefix.round{index}.lean"
    archive.write_bytes(source.read_bytes())
    env = os.environ.copy()
    exported = json.loads((root/"work/mathlib-environment.json").read_text(encoding="utf-8"))
    for key in ("LEAN_PATH","LEAN_SRC_PATH","LEAN_SYSROOT"):
        if exported.get(key):
            env[key] = exported[key]
    env["LEAN_PATH"] = os.pathsep.join([str(here),str(Path(dependency["baseline_olean"]).parent),
                                       dependency["proof_cache"],env["LEAN_PATH"]])
    compiler = Path(r"C:\Users\REGIS\Documents\Codex\runtimes\elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe")
    command = [str(compiler),"-DmaxHeartbeats=20000","-o",str(here/"AtomicSecondPrefix.olean"),str(source)]
    report_path = here/f"n76-round-{index}-report.json"
    report = {"node":"n76","round":index,"invocation_counted":True,"command":command,
              "source":str(source),"source_archive":str(archive),"source_sha256":sha(source),
              "dependency_provenance":"n76-dependency-provenance.json","exit_code":None,
              "environment":{k:env[k] for k in ("LEAN_PATH","LEAN_SRC_PATH","LEAN_SYSROOT")}}
    report_path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    started = time.monotonic()
    try:
        result = subprocess.run(command,cwd=here,env=env,capture_output=True,text=True,
                                encoding="utf-8",errors="replace",timeout=600)
        stdout,stderr,code = result.stdout,result.stderr,result.returncode
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout.decode("utf-8",errors="replace") if isinstance(e.stdout,bytes) else (e.stdout or "")
        stderr = "Compiler timeout600s; invocation remains counted"
        code = None
    (here/f"n76-round-{index}-stdout.txt").write_text(stdout,encoding="utf-8")
    (here/f"n76-round-{index}-stderr.txt").write_text(stderr,encoding="utf-8")
    audits = {}
    for name,axioms in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",stdout):
        audits[name] = [s.strip() for s in axioms.split(",") if s.strip()]
    for name in re.findall(r"'([^']+)' does not depend on any axioms",stdout):
        audits[name] = []
    expected = ["AtomicSecondPrefix."+name for name in DECLARATIONS]
    success = code == 0 and all(name in audits and set(audits[name]) <= ALLOWED for name in expected)
    report.update({"exit_code":code,"elapsed_seconds":time.monotonic()-started,
                   "audits":audits,"accepted_complete_file":success})
    if success:
        report["compiled_sha256"] = sha(here/"AtomicSecondPrefix.olean")
    report_path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    strict = {"node":"n76","source":str(source),"source_sha256":sha(source),
              "declarations":expected,"accepted_declarations":len(expected) if success else 0,
              "actual_total_compiler_invocations":index,"compiler_invocation_cap":3,
              "dev_score":1.0 if success else 0.0,"leaf_passes":4 if success else 0,
              "leaf_denominator":4,"root_score":0,"root_conjecture_verified":False,
              "leaves":{leaf:{"declaration":"AtomicSecondPrefix."+name,
                               "status":"verified" if success else "unverified"}
                        for leaf,name in LEAVES.items()},
              "axiom_audits":audits,"dependency_provenance":dependency,
              "last_round_report":report_path.name,"stdout_path":f"n76-round-{index}-stdout.txt",
              "stderr_path":f"n76-round-{index}-stderr.txt","exit_code":code,
              "scope":"Four atomic second-prefix leaves only; no arbitrary-future contraction or global closure"}
    if success:
        strict["compiled_sha256"] = report["compiled_sha256"]
    (here/"n76-strict-report.json").write_text(json.dumps(strict,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"round":index,"exit_code":code,"elapsed_seconds":report["elapsed_seconds"],
                      "success":success,"accepted_declarations":strict["accepted_declarations"],
                      "source_sha256":sha(source),"report":"n76-strict-report.json"},indent=2))
    if not success:
        print(stdout)
        print(stderr)
    raise SystemExit(0 if success else 1)


if __name__ == "__main__":
    main()

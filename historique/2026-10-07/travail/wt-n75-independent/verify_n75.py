"""Audit the accepted n75 leaf without invoking Lean or accessing held-out data."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
source = ROOT / "AtomicFirstPrefix.lean"
contract = json.loads((ROOT / "n75-formal-contract.json").read_text(encoding="utf-8"))
rounds = sorted((ROOT / "n75-compiler-rounds").glob("round-*.json"))
records = [json.loads(p.read_text(encoding="utf-8")) for p in rounds]
sha = hashlib.sha256(source.read_bytes()).hexdigest()
text = source.read_text(encoding="utf-8")
blocked = bool(re.search(r"\b(sorry|axiom|native_decide|admit)\b|\+native", text))
last = records[-1] if records else {}
audits = re.findall(r"'AtomicFirstPrefix\.([^']+)' depends on axioms: \[([^\]]*)\]", last.get("stdout", ""))
audit_map = {name: [a.strip() for a in value.split(",") if a.strip()] for name, value in audits}
allowed = {"propext", "Classical.choice", "Quot.sound"}
accepted = last.get("exit_code") == 0 and last.get("source_sha256") == sha and not blocked
accepted = accepted and all(set(a).issubset(allowed) for a in audit_map.values())
names = [leaf["name"] for leaf in contract["leaves"]]
closed = [name for name in names if accepted and name in audit_map]
dependency = json.loads((ROOT / "n75-dependency-build.json").read_text(encoding="utf-8"))
history_integrity = all(hashlib.sha256((ROOT / r["snapshot"]).read_bytes()).hexdigest() == r["source_sha256"]
                        for r in records)
dependency_accepted = dependency["exit_code"] == 0 and dependency["actual_compiler_invocations"] == 1
goal_statuses = [{"id": leaf["id"], "declaration": "AtomicFirstPrefix." + leaf["name"],
                  "status": "closed" if leaf["name"] in closed else "open",
                  "axioms": audit_map.get(leaf["name"])} for leaf in contract["leaves"]]
report = {"node": "n75", "accepted": accepted and len(closed) == 6,
          "source": source.name, "source_sha256": sha,
          "protocol_sha256": hashlib.sha256((ROOT / "n75-protocol.json").read_bytes()).hexdigest(),
          "formal_contract_sha256": hashlib.sha256((ROOT / "n75-formal-contract.json").read_bytes()).hexdigest(),
          "candidate_invocations": len(records), "dependency_invocations": 1, "probe_invocations": 0,
          "total_n75_invocations": len(records) + 1, "prior_shared_invocations": 7,
          "shared_invocations_through_n75": len(records) + 8,
          "history": [{"round": r["round"], "exit_code": r["exit_code"],
                       "source_sha256": r["source_sha256"]} for r in records],
          "accepted_declarations": closed, "axiom_audit": audit_map,
          "declarations": [g["declaration"] for g in goal_statuses if g["status"] == "closed"],
          "goal_statuses": goal_statuses, "history_integrity": history_integrity,
          "dependency_build_accepted": dependency_accepted,
          "dependency_build_report_sha256": hashlib.sha256((ROOT / "n75-dependency-build.json").read_bytes()).hexdigest(),
          "source_encoding": "UTF-8", "source_newlines": "LF" if b'\r' not in source.read_bytes() else "CRLF_PRESENT",
          "dev_score": len(closed) / 6, "root_score": 0, "root_conjecture_verified": False,
          "constraints": ["local h*u=b is explicit", "h=0/existence/compilation REQUIRED_OPEN",
                          "all-f contraction has no free scalar gate", "second-prefix/global closure REQUIRED_OPEN"]}
report["accepted"] = report["accepted"] and history_integrity and dependency_accepted and report["source_newlines"] == "LF"
(ROOT / "n75-strict-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["accepted"] else 1)

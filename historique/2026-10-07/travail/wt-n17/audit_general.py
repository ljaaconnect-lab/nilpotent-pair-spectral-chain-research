"""Freeze n17 only from actual successful compiler logs matching source bytes."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = {"propext", "Classical.choice", "Quot.sound"}
NAMES = ["sign_square", "selectSum_nodup", "central_label_iff", "central_row_select",
         "central_row", "central_pairing", "coefficient_append", "coefficient_multiply",
         "central_product_coefficient"]
LOGS = sorted((ROOT / "n17-compiler-rounds").glob("round-*.json"))
all_rounds = [json.loads(path.read_text()) for path in LOGS]
report = {"node_id": "n17", "artifact_version": "n17-general-pairing-v1",
          "local_compiler_rounds": len(all_rounds), "prior_global_rounds": 18,
          "global_rounds_after_node": 18 + len(all_rounds),
          "root_conjecture_verified": False, "heldout_tests_run": False,
          "boundary": "Nine named declarations in each of Rat and generic-ring files, compiler exit 0, exact source hash, no proof placeholders, explicit axiom audit limited to standard Lean trust base",
          "files": {}, "errors": []}


def strip_comments(source):
    out, i, depth = [], 0, 0
    while i < len(source):
        if source.startswith("/-", i):
            depth += 1
            i += 2
        elif depth and source.startswith("-/", i):
            depth -= 1
            i += 2
        elif depth:
            i += 1
        elif source.startswith("--", i):
            i = source.find("\n", i)
            if i < 0:
                break
        else:
            out.append(source[i])
            i += 1
    if depth:
        raise ValueError("Unclosed Lean block comment")
    return "".join(out)


accepted = 0
for file, namespace in [("GeneralPairing.lean", "GeneralCollisionPairing"),
                        ("GeneralPairingRing.lean", "GeneralCollisionPairingRing")]:
    raw = (ROOT / file).read_bytes()
    source = raw.decode("utf-8")
    source_hash = hashlib.sha256(raw).hexdigest()
    matches = [row for row in all_rounds if row.get("source") == file and
               row.get("source_sha256") == source_hash]
    row = matches[-1] if matches else None
    evidence = {"source_sha256": source_hash, "status": "unverified", "axioms": {}}
    if re.search(r"\b(?:sorry|admit|axiom|unsafe)\b", strip_comments(source)):
        report["errors"].append(f"{file}: unresolved placeholder or untrusted declaration")
    if row is None:
        report["errors"].append(f"{file}: no matching exact-source compiler log")
        report["files"][file] = evidence
        continue
    evidence.update(compiler_round=row["round"], compiler_exit_code=row["exit_code"],
                    command=row["command"], log=f"n17-compiler-rounds/round-{row['round']:02d}.json")
    output = row.get("stdout", "") + row.get("stderr", "")
    if row["exit_code"] != 0 or re.search(r"\bsorryAx\b|\berror:", output):
        report["errors"].append(f"{file}: compiler rejection or untrusted proof dependency")
    found = {}
    for name, raw_axioms in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", output):
        found[name] = {a.strip() for a in raw_axioms.split(",") if a.strip()}
    for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", output):
        found[name] = set()
    for suffix in NAMES:
        name = namespace + "." + suffix
        if name not in found:
            report["errors"].append(f"{file}: missing #print axioms evidence for {name}")
            continue
        evidence["axioms"][name] = sorted(found[name])
        if found[name] - BASE:
            report["errors"].append(f"{file}: unexpected axioms {sorted(found[name] - BASE)}")
            continue
        if row["exit_code"] == 0:
            accepted += 1
    evidence["status"] = "kernel_verified" if row["exit_code"] == 0 else "unverified"
    report["files"][file] = evidence

report["accepted_declarations"] = accepted
report["expected_declarations"] = 18
report["dev_score"] = accepted / 18 if not report["errors"] else 0.0
report["status"] = "general_pairing_verified" if not report["errors"] else "rejected"
report["accepted_trust_base"] = sorted(BASE)
(ROOT / "n17-strict-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({key: report[key] for key in ["node_id", "status", "local_compiler_rounds",
      "global_rounds_after_node", "accepted_declarations", "dev_score", "root_conjecture_verified", "errors"]}, indent=2))
raise SystemExit(0 if not report["errors"] else 1)

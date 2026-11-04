"""Score the fixed all-n subset baseline, independently of Conjecture 1.5."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "ActualClosedSubsetTransfer.lean"
TRUST = {"propext", "Classical.choice", "Quot.sound"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


source = SOURCE.read_text(encoding="utf-8")
digest = sha(SOURCE)
formal_path = ROOT / "n73-formal-contract.json"
formal = json.loads(formal_path.read_text(encoding="utf-8"))
protocol_path = ROOT / "n73-protocol.json"
provenance_path = ROOT / "n73-dependency-provenance.json"
provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
mathlib_path = ROOT / "n73-mathlib-imports.json"
mathlib = json.loads(mathlib_path.read_text(encoding="utf-8"))
rounds = [json.loads(path.read_text(encoding="utf-8")) for path in
          sorted((ROOT / "n73-compiler-rounds").glob("round-*.json"))]
matches = [r for r in rounds if r["source"] == SOURCE.name and r["source_sha256"] == digest]
final = matches[-1] if matches else None
errors = []
code = re.sub(r"/-.*?-/|--[^\n]*", "", source, flags=re.DOTALL)
if re.search(r"\b(?:sorry|admit|axiom|unsafe|native_decide)\b|\+native\b", code):
    errors.append("Forbidden placeholder or untrusted code")
if re.search(r"\b(?:hclosure|hrepresentation|hfix)\b", code):
    errors.append("Actual subset baseline cannot assume closure, representation or stabilization")
state_body = re.search(r"^def state\b(.*?)(?=^theorem)", source, flags=re.MULTILINE | re.DOTALL)
if not state_body or re.search(r"\b(?:coeff|permanent|markedPermanent|inverse)\b", state_body.group(1)):
    errors.append("The effective state definition contains an unknown target or extraction")
if len(rounds) > 8:
    errors.append("Eight-invocation total budget exceeded")
if [r["round"] for r in rounds] != list(range(1, len(rounds) + 1)):
    errors.append("Invocation IDs are not unique and contiguous")
for r in rounds:
    if sha(ROOT / r["snapshot"]) != r["source_sha256"]:
        errors.append(f"Snapshot changed at invocation {r['round']}")
for module, data in provenance["dependencies"].items():
    for path_key, hash_key in [("source_path", "source_sha256"), ("compiled_path", "compiled_sha256")]:
        if sha(Path(data[path_key])) != data[hash_key]:
            errors.append(f"Inherited dependency changed: {module}, {path_key}")
for module, data in mathlib["modules"].items():
    for path_key, hash_key in [("source_path", "source_sha256"), ("compiled_path", "compiled_sha256")]:
        if sha(Path(data[path_key])) != data[hash_key]:
            errors.append(f"Direct Mathlib dependency changed: {module}, {path_key}")
if sha(Path(provenance["compiler_path"])) != provenance["compiler_sha256"]:
    errors.append("Compiler executable changed")
if sha(Path(provenance["replay_report"])) != provenance["replay_report_sha256"]:
    errors.append("Inherited coordinator replay report changed")
names = re.findall(r"^theorem\s+(\w+)", source, flags=re.MULTILINE)
declarations = ["ActualClosedSubsetTransfer." + name for name in names]
audited = {}
if not final or final["exit_code"] != 0:
    errors.append("No exit-zero evidence for exact current source")
else:
    if final["frozen_protocol_sha256"] != sha(protocol_path) or final["formal_contract_sha256"] != sha(formal_path):
        errors.append("Compiled contracts changed")
    if final["dependency_provenance_sha256"] != sha(provenance_path):
        errors.append("Compiled dependency provenance changed")
    output = final["stdout"] + final["stderr"]
    if re.search(r"\bsorryAx\b|declaration uses ['\"]?sorry|\berror:", output):
        errors.append("Rejected final compiler diagnostics")
    for name, raw in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", output):
        audited[name] = {x.strip() for x in raw.split(",") if x.strip()}
    for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", output):
        audited[name] = set()
    for name in declarations:
        if name not in audited or audited[name] - TRUST:
            errors.append(f"Missing or unexpected axiom audit: {name}")
accepted = [] if errors else names
closed_groups = [group for group in formal["score_groups"] if all(name in accepted for name in group)]
required_open = [name for name in formal["required"] if name not in accepted]
status = "rejected" if errors else "actual_subset_baseline_partial" if required_open else "actual_subset_baseline_verified"
report = {
    "node": "n73", "artifact_version": "n73-actual-subset-baseline-v1", "status": status,
    "source": SOURCE.name, "source_sha256": digest,
    "compiled_artifact_sha256": sha(SOURCE.with_suffix(".olean")) if not errors and SOURCE.with_suffix(".olean").is_file() else None,
    "dev_score": len(closed_groups) / 4, "baseline_score": f"{len(closed_groups)}/4",
    "root_conjecture_score": 0, "root_conjecture_verified": False,
    "root_polynomial_gate_bound_proved": False, "uniform_polynomial_constructor_proved": False,
    "state_dimension": "2^n; explicitly exponential",
    "required_obligations": formal["required"], "unclosed_obligations": required_open,
    "accepted_declarations": len(accepted), "declarations": [] if errors else declarations,
    "exact_source_statements": {
        name: statement.strip() for name, statement in
        re.findall(r"^theorem\s+(\w+)(.*?)\s*:=\s*by", source, flags=re.MULTILINE | re.DOTALL)
    },
    "source_context": "namespace ActualClosedSubsetTransfer; variable {R:Type} [CommRing R] {n:Nat}; noncomputable section; each declaration captures its actual free variables",
    "axiom_audit": {name: sorted(audited.get(name, set())) for name in declarations},
    "accepted_trust_base": sorted(TRUST),
    "compiler_invocations": len(rounds), "all_kind_invocation_cap": 8,
    "candidate_invocations": sum(r["kind"] == "candidate" for r in rounds),
    "dependency_builds": sum(r["kind"] == "dependency_build" for r in rounds),
    "probe_compilations": sum(r["kind"] == "probe" for r in rounds),
    "compiler_exit_code": final["exit_code"] if final else None,
    "final_compiler_round": final["round"] if final else None,
    "command": final["command"] if final else None,
    "LEAN_PATH": final["LEAN_PATH"] if final else None,
    "LEAN_SRC_PATH": final["LEAN_SRC_PATH"] if final else None,
    "LEAN_SYSROOT": final["LEAN_SYSROOT"] if final else None,
    "invocation_history": [{key: r[key] for key in
                            ["round", "kind", "source_sha256", "exit_code", "elapsed_seconds"]}
                           for r in rounds],
    "frozen_protocol_sha256": sha(protocol_path), "formal_contract_sha256": sha(formal_path),
    "blueprint_sha256": sha(ROOT / "n73-leap-blueprint.md"),
    "dependency_provenance_sha256": sha(provenance_path),
    "direct_mathlib_import_provenance_sha256": sha(mathlib_path),
    "compiler_warnings": [] if not final else re.findall(r"[^\n]*warning:[^\n]*", final["stdout"]),
    "cache_mutated": False, "heldout_tests_run": False,
    "constraint_history": "Round1 explicit permutation membership was required after simp unfolded bijectivity into a multiset goal; round2 uses the genuine sigma.bijective proof",
    "scope": "Effective closed subset recurrence for arbitrary explicit B, its all-size coefficient invariant, exact permanent and marked central output; no polynomial compression claim",
    "errors": errors,
}
(ROOT / "n73-strict-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({key: report[key] for key in
                 ["status", "baseline_score", "accepted_declarations", "root_conjecture_score", "compiler_invocations", "unclosed_obligations", "errors"]}, indent=2))
raise SystemExit(bool(errors))

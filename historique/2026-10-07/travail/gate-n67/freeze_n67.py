"""Record read-only dependency provenance and distilled n67 results, without compiling."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MATHLIB = ROOT.parent / "mathlib"
ENVIRONMENT = ROOT.parent / "mathlib-environment.json"
LEAN = Path(r"C:\Users\REGIS\Documents\Codex\runtimes\elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


modules = {}
for module in ["Mathlib.Data.Matrix.Basic", "Mathlib.Algebra.Ring.Rat"]:
    relative = Path(*module.split("."))
    source = (MATHLIB / relative).with_suffix(".lean")
    compiled = (MATHLIB / ".lake/build/lib/lean" / relative).with_suffix(".olean")
    modules[module] = {
        "source_path": str(source), "source_sha256": sha(source),
        "compiled_path": str(compiled), "compiled_sha256": sha(compiled),
    }
kernel_tactic = LEAN.parent.parent / "src/lean/Lean/Elab/Tactic/Decide.lean"
provenance = {
    "modules": modules,
    "compiler": {"path": str(LEAN), "sha256": sha(LEAN), "version": "Lean 4.34.1"},
    "environment_source": str(ENVIRONMENT), "environment_sha256": sha(ENVIRONMENT),
    "decide_kernel_implementation": {
        "source_path": str(kernel_tactic), "source_sha256": sha(kernel_tactic),
        "method": "decide +kernel uses doKernel/mkAuxLemma; no native reduction or additional axiom",
    },
    "mathlib_cache_mutated": False,
    "mathlib_git_revision": None,
    "revision_note": "Read-only acquired Mathlib sources and compiled files identified by hashes; no separate Mathlib Git HEAD asserted",
}
(ROOT / "n67-mathlib-provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
audit = subprocess.run(["python", str(ROOT / "verify_n67.py")], cwd=ROOT, capture_output=True, text=True)
print(audit.stdout)
if audit.returncode:
    print(audit.stderr)
    raise SystemExit(audit.returncode)
report = json.loads((ROOT / "n67-strict-report.json").read_text(encoding="utf-8"))
leaf = {
    "node_id": "n67", "artifact_version": report["artifact_version"],
    "dev_score": report["dev_score"], "helper_score": report["helper_score"],
    "root_conjecture_score": 0,
    "result": "Exact four-leg Hadamard COPY transform, explicit six-parameter Pf4 all-one signature, and both rational matrix inverse products kernel verified",
    "insight": "The local boundary signature is representable and the basis change is invertible; contraction closure, crossing compatibility and polynomial scalar compilation remain additional global obligations",
    "branch_ref": "arbor/n67",
    "source": report["source"], "source_sha256": report["source_sha256"],
    "report": "n67-strict-report.json",
    "candidate_rounds": report["candidate_rounds"],
    "dependency_builds": 0, "probe_compilations": 0,
    "root_conjecture_verified": False, "heldout_tests_run": False,
    "constraint": "Ordinary decide was replaced by kernel reduction after its real round-1 transparency diagnostic, preserving all three frozen statements",
}
(ROOT / "n67-leaf-result.json").write_text(json.dumps(leaf, indent=2), encoding="utf-8")
print(json.dumps({"node": "n67", "source_sha256": report["source_sha256"], "helper_score": report["helper_score"]}, indent=2))

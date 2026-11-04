# Reproduce n54

Use the prepared Mathlib environment `work/mathlib-environment.json` in the parent workspace and the existing Lean 4.34.1 compiler. No installation or cache writes are required. Run each command to completion from this worktree, in this order:

```powershell
python .\compile_n54.py --source GeneralPairingRing.lean --dependency
python .\compile_n54.py --source CoreBridge.lean --dependency
python .\compile_n54.py --source LabelBridge.lean --dependency
python .\compile_n54.py
python .\verify_n54.py
```

The runner prepends this worktree to the exact prepared `LEAN_PATH` using `os.pathsep`. It invokes the absolute compiler with this worktree as cwd, retains the exact source snapshot, digest, command, exit code and complete stdout/stderr, and counts dependency builds separately from the maximum of 16 candidate rounds. This frozen run used eight candidate rounds and three dependency builds.

The verifier audits recorded compiler evidence, including an exit-zero invocation for the exact current source and explicit `#print axioms` output for every theorem. It rejects unresolved source placeholders, `sorryAx`, missing audit evidence and axioms beyond `propext`, `Classical.choice`, `Quot.sound`. Its helper score does not assert Conjecture 1.5 or any complexity bound for coefficient extraction.

The accepted source is `PolynomialBridge.lean`. The exact report is `n54-strict-report.json`; the leaf record and acyclic proof obligations are `n54-leaf-result.json` and `n54-blueprint-informel.md`. Historical failed snapshots in `n54-compiler-rounds` are diagnostics, not accepted proofs. Local `.olean` files are reproducible build products and remain uncommitted.

# Reproduce the frozen n55 proof

The existing Lean 4.34.1 compiler and parent workspace's prepared `work/mathlib-environment.json` suffice. The runner copies all three environment entries (`LEAN_PATH`, `LEAN_SRC_PATH`, `LEAN_SYSROOT`), prepends this worktree with `os.pathsep`, invokes the absolute compiler and keeps the cache read-only. Run each command to completion from this worktree:

```powershell
python .\compile_n55.py --source GeneralPairingRing.lean --dependency
python .\compile_n55.py --source CoreBridge.lean --dependency
python .\compile_n55.py --source LabelBridge.lean --dependency
python .\compile_n55.py --replay
python .\verify_n55.py
```

The frozen search used exactly 24 candidate compilations and three local dependency builds. It ends at round 27 with exit 0 for all thirteen declared theorems. The `--replay` path permits only the exact current source matching the accepted strict report; it cannot admit an additional candidate or a changed proof after the search budget. Replays are recorded separately as actual compiler invocations. No replay was used during this frozen search.

The new source and compiler snapshots retain exact Git bytes through `.gitattributes`, so the recorded digests survive Windows checkout. The verifier audits source snapshots, exit codes and every explicit `#print axioms` output, including all three local dependencies. Only `propext`, `Classical.choice`, and `Quot.sound` are admitted; placeholders or `sorryAx` reject acceptance.

The report, leaf record, contract and source are `n55-strict-report.json`, `n55-leaf-result.json`, `n55-frozen-obligations.json`, and `DeterminantBridge.lean`. Historical failed snapshots and full diagnostics remain under `n55-compiler-rounds`. The report's helper score does not prove Conjecture 1.5 or any polynomial scalar extraction complexity bound.

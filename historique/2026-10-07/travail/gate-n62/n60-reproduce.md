# Reproduce the frozen n60 algebraic leaf

Use a fresh checkout of the committed n60 branch directly under the existing `work` directory. The compiler runner reads the prepared, read-only `work/mathlib-environment.json`, retains all three Lean environment entries, and prefixes the current checkout to `LEAN_PATH`. It calls the absolute Lean 4.34.1 compiler and captures real exit codes and exact source snapshots.

From that checkout, run these commands sequentially:

```powershell
python compile_n60.py --source GeneralPairingRing.lean --dependency
python compile_n60.py --source CoreBridge.lean --dependency
python compile_n60.py --source LabelBridge.lean --dependency
python compile_n60.py --source DeterminantBridge.lean --dependency
python compile_n60.py --source ReverseVandermonde.lean --dependency
python compile_n60.py --replay
python verify_n60.py
```

Each command must finish before the next command starts. The replay mode permits only the exact accepted `EncodingBridge.lean` and frozen contract. It is separately counted from the 16-candidate development budget. `.olean` files are local ignored build artifacts. The source bytes are preserved by `.gitattributes`, including the exact copied n58 source.

Expected result: `encoding_identity_verified`, compiler exit 0, seven accepted new declarations, all axioms contained in `{propext, Classical.choice, Quot.sound}`, and no `sorryAx`. The preserved original run used ten candidate compilations and five dependency builds, with zero probe compilations and zero replays. A reproduction appends its own invocation evidence and counts.

The two fixed results are `CollisionEncodingBridge.hhat_central_coefficient` for an arbitrary commutative coefficient ring and `CollisionEncodingBridge.marked_A_central_identity` for rational A with the exact binary cell-address marking. The result is an identity in actual Mathlib polynomial types. No polynomial-size scalar coefficient extractor is declared or assumed. No held-out tests are invoked.

# Reproduce the frozen n62 direct-projector leaf

Use a fresh checkout of this committed branch directly under the existing `work` directory. The runner reads the prepared `work/mathlib-environment.json` without modifying it. All three Lean environment entries are applied, with the current checkout prefixed to `LEAN_PATH`. The direct Lean 4.34.1 compiler path is recorded in every invocation report.

Run these commands sequentially, waiting for each final exit code before starting the next:

```powershell
python compile_n62.py --source GeneralPairingRing.lean --dependency
python compile_n62.py --source CoreBridge.lean --dependency
python compile_n62.py --source LabelBridge.lean --dependency
python compile_n62.py --source DeterminantBridge.lean --dependency
python compile_n62.py --replay
python verify_n62.py
```

The exclusive runner lock rejects a concurrent invocation. Replay mode permits only the exact accepted `DirectProjector.lean` and both frozen contracts. Replay is counted separately from the 12-candidate development budget. Local `.olean` files and the transient lock are ignored; source and evidence bytes are preserved by `.gitattributes`.

Expected result: `direct_projector_verified`, exit code 0, exactly seven accepted declarations, no placeholders or `sorryAx`, and no axioms beyond `{propext, Classical.choice, Quot.sound}`. The original run used nine candidates and four dependency builds; its initial premature-import candidate is explicitly retained and counted, with the journal recovery disclosed. A fresh reproduction appends its own build and replay evidence.

The two local equations are scalar algebra for an explicitly defined bilinear expression. The two phase identities concern actual functions with explicit decidable predicates. The global phase is the product over `Finset.Ioi`, transported from Mathlib's actual permutation sign, and its correction of signed matrix weights uses the inherited sign-square theorem. The pointwise function action is an identity model, with no claimed polynomial scalar implementation. No held-out tests or root-conjecture success assertion are included.

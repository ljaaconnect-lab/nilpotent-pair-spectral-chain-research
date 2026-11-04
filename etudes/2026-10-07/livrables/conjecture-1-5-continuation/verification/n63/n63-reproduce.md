# Reproduce the frozen n63 Mobius helpers

Use a fresh checkout of the committed branch directly under the existing `work` directory. The standalone source imports four already prepared Mathlib modules and no local Lean modules. The runner reads the read-only `work/mathlib-environment.json`, sets all three Lean environment entries and prefixes the checkout to `LEAN_PATH`. The absolute direct Lean 4.34.1 compiler path and exact environments are captured in the journal.

Run sequentially:

```powershell
python compile_n63.py --replay
python verify_n63.py
```

Wait for the final process exit code. A session identifier means that compilation is still running. An exclusive process lock prevents overlapping invocations. Replay requires the exact accepted source, clarified protocol, formal contract and bonus contract; it is separately counted from the 12-candidate budget. No local dependency builds are required. Source bytes and evidence are preserved by `.gitattributes`.

Expected result: `mobius_helpers_verified`, compiler exit 0, four of four frozen helper obligations verified, six accepted theorem declarations, no unresolved goals or `sorryAx`, and only the agreed `{propext, Classical.choice, Quot.sound}` trust base. The original run used eleven candidates, zero dependency builds, zero probes and zero replays. The source has two retained style warnings about an unused section variable, with no compilation errors.

The reconstruction has no bound hypothesis on f. Both primary coefficient bounds retain the explicit `h_f` on every subset of S. The separate bonus specializes to `f(T)=(-1)^q(T)` for arbitrary q and proves that value bound automatically. All results apply to arbitrary finite S, in particular to finite ambient types. No polynomial representation, scalar circuit compression, held-out test, or root-conjecture success is assumed or invoked. The root score remains zero.

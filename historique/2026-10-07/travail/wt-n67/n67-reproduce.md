# n67 exact local algebraic gadgets

The frozen obligations are in `n67-protocol.json` and `n67-formal-obligations.json`. The accepted source is `HadamardPfaffian.lean`. Its exact bytes, three accepted theorem names, definition audit, dependency hashes and all four compiler invocations are bound by `n67-strict-report.json`.

The explicit Gaussian boundary has six independent rational parameters. It is defined by its empty, two-element, four-element and odd-subset values, without reference to the parity indicator. The third theorem uses actual Mathlib multiplication and identity for `Matrix Bool Bool Rat` in both orders.

From the local worktree, run `python verify_n67.py` to audit the frozen evidence without invoking Lean. For an independently budgeted replay of the exact accepted source, run `python compile_n67.py --replay`, then `python verify_n67.py`. The runner requires the prepared read-only `../mathlib-environment.json`, applies its three environment entries and prefixes this checkout to `LEAN_PATH`. It uses the absolute Lean 4.34.1 executable, records a unique exact source snapshot, and waits for final process completion. The replay option verifies accepted source and contract hashes before invoking Lean.

Development used four complete candidates, zero dependency builds and zero hidden probes. The first rejected attempt used ordinary `decide`; its recorded finite rational reduction diagnostic motivated `decide +kernel`. The latter is kernel reduction, without native compilation. The accepted audit contains only `propext`, `Classical.choice`, and `Quot.sound`. No final declaration contains a placeholder or additional axiom.

The local score is 3/3. The Conjecture 1.5 score is zero. These local equalities supply boundary and basis-change components; they establish no global Gaussian contraction theorem, fermionic crossing convention, full permutation-sign cancellation or uniform polynomial scalar compiler. No held-out test boundary was accessed.

# N75 invocation journal

All hypotheses were frozen in `n75-protocol.json` and the exact Lean interface
in `n75-formal-contract.json` before any candidate compilation.

1. Coordinator dependency build: pinned Mathlib `SchurComplement.lean`, exit 0,
   124.547 seconds. Original report is `n75-dependency-build.json`.
2. Candidate 1, A4: exit 1. An unannotated row constant inferred Nat; the subtype
   sum simplified to a sum over `J.attach`. Its generated `sorryAx` was rejected.
3. Candidate 2, A4: exit 0, standard three axioms only. Corrected the constant
   type and used `Finset.sum_attach`; one unused simp argument was removed next.
4. Candidate 3, A1/A2/A3: exit 1. A1 and A2 had standard audits; A3 required
   the reverse direction of `Finset.sum_mul`. The file was not accepted as a leaf.
5. Candidate 4: exit 0, A1–A4 all audited, no warnings.
6. Candidate 5: exit 0, A5 closes under exactly `∀j, total b * u j = b j`.
7. Candidate 6: exit 0, A6 closes by finite linearity. Source bytes were explicitly
   normalized to UTF-8/LF before this invocation. All six audits are standard,
   without warnings. This is the accepted immutable source.

Total: six candidates, one dependency, zero probes, seven actual Lean invocations.
No compiler was killed early or counted successful while still running. Failed
logs/snapshots remain rejected provenance; they are not accepted proofs.

The six elementary identities are proved for arbitrary n and coefficient
CommRing R, including empty J. The root conjecture is not proved. The local
normalization's existence/division-free compilation at arbitrary inputs, its
h=0 handling, and any global all-f contraction remain separate obligations.
No B_test, .arbor, or outputs access occurred in n75.
